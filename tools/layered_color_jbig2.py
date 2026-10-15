"""Paired colored-JBIG2 benchmark (§§192–194), reusing shared core (§203).

Run ./.venv/bin/python tools/layered_color_jbig2.py --help.
Both encoders receive the same once-prepared palette/index map. The production
canvas, native-layer assembler, encoder validation and PDF optimizer are reused.
"""
import argparse
import io
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(name, "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pymupdf as fitz
from PIL import Image, ImageDraw

from pdf_minimalist.core import image_layers, pipeline
from pdf_minimalist.core.cancel import CancelToken
from pdf_minimalist.core.canvas import flatten_rgb
from pdf_minimalist.core.display import DisplayPage
from pdf_minimalist.core.pdf_io import CancelledError
from pdf_minimalist.core import stencils
from pdf_minimalist.core.stencils import PaletteCanvas


def check_cancel(token):
    if token.cancelled:
        raise CancelledError()


def indexed_payload(canvas):
    """Production Indexed packing/Deflate, without a second palette fit."""
    bpc = pipeline.bpc_for(len(canvas.palette))
    parts = dict(stream=pipeline.deflate_best(pipeline.pack_indices(canvas.indices, bpc)),
                 palette=canvas.palette.tobytes(), bpc=bpc, hival=len(canvas.palette)-1,
                 w=canvas.width, h=canvas.height)
    return dict(filter="/FlateDecode", stream=parts["stream"], indexed=parts,
                w=canvas.width, h=canvas.height)


def encode_mask(mask):
    """Shared production lossless coder; retained seam for failure injection."""
    return stencils.encode_mask(mask)


def stencil_pdf(canvas, token=None, *, page_size=None):
    return stencils.stencil_pdf(canvas, token, page_size=page_size, mask_encoder=encode_mask)


def rgb_pixels(pix):
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]


def prepare_canvases(source, colors, dpi, token, directory):
    """The production native filter/full-RGB sampler/one resize/palette fit."""
    result = []
    with fitz.open(source) as original:
        for pno in range(len(original)):
            check_cancel(token)
            with image_layers._copy_page(original, pno) as fragment:
                page = fragment[0]
                if not page.get_image_info():
                    result.append(None)
                    continue
                image_layers._filter(page, token, "canvas",
                                     backdrops=image_layers._page_backdrops(page))
                rgb = flatten_rgb(page, dpi, token, pipeline.force_to_dpi, directory=directory)
                result.append(PaletteCanvas.from_rgb(rgb, colors))
    return result


def save_variant(source, target, canvases, kind, token=None):
    """Reuse the production page assembler and final font/container optimizer."""
    if kind not in ("indexed", "jbig2"):
        raise ValueError(kind)
    token = token or CancelToken()
    with fitz.open(source) as doc:
        if len(canvases) != len(doc):
            raise ValueError("Canvas count must match the source page count")
        for pno, canvas in enumerate(canvases):
            check_cancel(token)
            if canvas is None:
                continue
            def paint(out, page, _fragment):
                if kind == "indexed":
                    pipeline._place_color(out, page, page.rect, indexed_payload(canvas))
                else:
                    # Express masks directly in target PAGE units, just like
                    # the Indexed image. Avoid inverse nested scale matrices
                    # whose float rounding shifts dense alternating pixels.
                    with stencil_pdf(canvas, token, page_size=(page.rect.width, page.rect.height)) as tile:
                        page.show_pdf_page(page.rect, tile, 0, keep_proportion=False)
            with image_layers._copy_page(doc, pno) as prepared:
                image_layers._assemble_layers(doc, pno, prepared, token, "canvas", paint)
        check_cancel(token)
        pipeline._save_optimized_pdf(doc, str(target))


def compare_outputs(source, indexed, layered, canvases, dpi, folder, independent=True):
    """Read actual files; verify native ownership and both rendering engines."""
    mask_count = 0
    render_differences = []
    render_diagnostics = []
    with fitz.open(source) as original, fitz.open(indexed) as before, fitz.open(layered) as after:
        assert len(original) == len(before) == len(after) == len(canvases)
        for pno, canvas in enumerate(canvases):
            old, ref, page = original[pno], before[pno], after[pno]
            assert old.rotation == ref.rotation == page.rotation
            assert old.cropbox == ref.cropbox == page.cropbox
            original_words = old.get_text("words")
            for candidate in (ref, page):
                words = candidate.get_text("words")
                assert len(words) == len(original_words)
                for left, right in zip(original_words, words):
                    assert left[4:] == right[4:]
                    assert np.allclose(left[:4], right[:4], atol=.001, rtol=0)
                assert [link.get("uri") for link in old.get_links()] == [
                    link.get("uri") for link in candidate.get_links()]
                assert [annot.info for annot in old.annots()] == [annot.info for annot in candidate.annots()]
            # The deliberate opaque white base is the only extra vector fill.
            assert len(page.get_drawings()) == len(ref.get_drawings()) + int(canvas is not None)
            images = page.get_images(full=True)
            assert len(images) == (canvas.nonwhite_colors if canvas else 0)
            for image in images:
                xref = image[0]
                assert after.xref_get_key(xref, "Filter")[1] == "/JBIG2Decode"
                assert after.xref_get_key(xref, "ImageMask")[1] == "true"
                assert after.xref_get_key(xref, "ColorSpace")[0] == "null"
                assert after.xref_get_key(xref, "Interpolate")[1] == "false"
                assert after.xref_get_key(xref, "SMask")[0] == "null"
                assert after.xref_get_key(xref, "BitsPerComponent")[1] == "1"
                assert image[2:4] == (canvas.width, canvas.height)
            mask_count += len(images)
            for scale in (1, dpi/72):
                a = rgb_pixels(DisplayPage(ref).render(fitz.Matrix(scale, scale)))
                b = rgb_pixels(DisplayPage(page).render(fitz.Matrix(scale, scale)))
                assert np.array_equal(a, b), (pno, scale, "saved MuPDF render mismatch")
            if independent:
                if shutil.which("pdftoppm") is None:
                    raise RuntimeError("Independent Poppler comparison unavailable: pdftoppm missing")
                with tempfile.TemporaryDirectory(prefix="poppler-", dir=folder) as scratch:
                    if canvas is not None:
                        prefix = Path(scratch) / "mask"
                        run = subprocess.run(["pdfimages", "-f", str(pno+1), "-l", str(pno+1),
                                              "-png", str(layered), str(prefix)],
                                             capture_output=True, timeout=120)
                        if run.returncode or run.stderr:
                            raise RuntimeError(f"Poppler mask decode failed: {run.stderr.decode(errors='replace')}")
                        decoded = sorted(Path(scratch).glob("mask-*.png"))
                        entries = [(i, color) for i, color in enumerate(canvas.palette)
                                   if not np.all(color == 255)]
                        assert len(decoded) == len(entries)
                        reconstructed = np.full_like(canvas.rgb, 255)
                        coverage = np.zeros(canvas.indices.shape, dtype=bool)
                        for filename, (index, color) in zip(decoded, entries):
                            with Image.open(filename) as image:
                                mask = np.asarray(image.convert("L"))
                            # pdfimages exports stencil COVERAGE (white=paint),
                            # not ordinary DeviceGray image sample polarity.
                            expected = np.where(canvas.indices == index, 255, 0).astype(np.uint8)
                            assert np.array_equal(mask, expected), (pno, index, "independent mask mismatch")
                            marked = mask == 255
                            assert not np.any(coverage & marked), "color masks overlap"
                            coverage |= marked
                            reconstructed[marked] = color
                        assert np.array_equal(reconstructed, canvas.rgb), "independent color reconstruction mismatch"
                    pngs = []
                    for label, filename in (("indexed", indexed), ("layered", layered)):
                        prefix = Path(scratch) / label
                        run = subprocess.run(["pdftoppm", "-f", str(pno+1), "-l", str(pno+1),
                                              "-singlefile", "-cropbox", "-r", str(dpi),
                                              "-aa", "no", "-aaVector", "no", "-png",
                                              str(filename), str(prefix)], capture_output=True, timeout=120)
                        if run.returncode:
                            raise RuntimeError(f"Poppler verification failed: {run.stderr.decode(errors='replace')}")
                        if run.stderr:
                            render_diagnostics.append(dict(page=pno+1, variant=label,
                                                           diagnostics=run.stderr.decode(errors="replace")))
                        with Image.open(prefix.with_suffix(".png")) as image:
                            pngs.append(np.asarray(image.convert("RGB")))
                    if not np.array_equal(*pngs):
                        prefix = Path(layered).with_suffix("")
                        for name, pixels in zip(("indexed", "layered"), pngs):
                            Image.fromarray(pixels).save(f"{prefix}.poppler-{name}.png")
                        wrong = np.any(pngs[0] != pngs[1], axis=2)
                        y, x = np.where(wrong)
                        pairs = np.unique(np.concatenate((pngs[0][wrong], pngs[1][wrong]), axis=1), axis=0)
                        render_differences.append(dict(page=pno+1, different_pixels=int(wrong.sum()),
                                                       bounds=[int(x.min()), int(y.min()), int(x.max()), int(y.max())],
                                                       indexed_vs_layered_colors=pairs[:12].tolist()))
        DisplayPage(after[0]).render(fitz.Matrix(dpi/72, dpi/72)).save(str(Path(layered).with_suffix(".png")))
    return dict(pages=len(canvases), colored_masks=mask_count,
                actual_palette_counts=[len(c.palette) if c else 0 for c in canvases],
                nonwhite_mask_counts=[c.nonwhite_colors if c else 0 for c in canvases],
                dimensions=[(c.width, c.height) if c else None for c in canvases],
                mupdf_pixel_exact=True, poppler_decoded_masks_exact=independent,
                poppler_page_render_exact=independent and not render_differences,
                poppler_page_render_differences=render_differences,
                poppler_render_clean=independent and not render_diagnostics,
                poppler_render_diagnostics=render_diagnostics)


def write_fixture(path, kind):
    """Explicitly synthetic source PDFs, not compression estimates."""
    colors = [(255, 255, 255), (0, 0, 0), (220, 35, 45), (25, 90, 210), (20, 150, 65)]
    rgb = np.full((600, 600, 3), 255, dtype=np.uint8)
    if kind == "noise":
        random = np.random.default_rng(192)
        rgb = np.asarray(colors, dtype=np.uint8)[random.integers(0, len(colors), (600, 600))]
    else:
        image = Image.fromarray(rgb)
        draw = ImageDraw.Draw(image)
        for index, color in enumerate(colors[1:]):
            left, top = 25+(index % 2)*290, 25+(index//2)*290
            draw.rectangle((left, top, left+220, top+160), fill=color)
            draw.ellipse((left+40, top+175, left+180, top+265), fill=color)
        rgb = np.asarray(image)
    stream = io.BytesIO()
    Image.fromarray(rgb).save(stream, "PNG")
    with fitz.open() as doc:
        page = doc.new_page(width=288, height=324)
        page.insert_image(fitz.Rect(0, 0, 288, 288), stream=stream.getvalue())
        page.insert_text((12, 309), f"Native {kind} caption", fontsize=12)
        page.draw_line((12, 315), (270, 315), color=(0, 0, 1))
        doc.save(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", default=["examples/images.pdf", "examples/paper-arxiv-1406.2661.pdf"])
    parser.add_argument("--colors", nargs="+", type=int, default=[3, 4, 5, 8, 16])
    parser.add_argument("--dpi", nargs="+", type=int, default=[150])
    parser.add_argument("--repeat", type=int, default=2)
    parser.add_argument("--label", default="study")
    parser.add_argument("--fixtures", action="store_true")
    args = parser.parse_args()
    if args.repeat < 1 or any(not 2 <= count <= 256 for count in args.colors) or any(dpi < 1 for dpi in args.dpi):
        parser.error("repeat/dpi must be positive and total palette colors in 2..256")
    if Path(args.label).name != args.label or args.label in (".", ".."):
        parser.error("label must be one directory name")
    folder = Path(".tmp/layered-color-jbig2") / args.label
    folder.mkdir(parents=True, exist_ok=True)
    sources = [Path(file) for file in args.files]
    if args.fixtures:
        for kind in ("flat", "noise"):
            fixture = folder / f"synthetic-{kind}.pdf"
            write_fixture(fixture, kind)
            sources.append(fixture)
    rows = []
    # The existing encoder/Deflate scratch context is reused within this tool.
    context = pipeline._ENCODE_WORKDIR.set(str(folder))
    try:
        for source in sources:
            for dpi in args.dpi:
                for colors in args.colors:
                    stem = f"{source.stem}.{colors}colors.{dpi}dpi"
                    indexed, layered = (folder / f"{stem}.{kind}.pdf" for kind in ("indexed", "jbig2"))
                    if source.resolve() in (indexed.resolve(), layered.resolve()):
                        raise ValueError("Benchmark must not overwrite its source")
                    times = {name: [] for name in ("shared", "indexed", "jbig2")}
                    for repeat in range(args.repeat):
                        token = CancelToken()
                        started = time.perf_counter()
                        canvases = prepare_canvases(str(source), colors, dpi, token, str(folder))
                        times["shared"].append(time.perf_counter()-started)
                        # Alternate ordering to avoid always giving one path warm caches.
                        kinds = ("indexed", "jbig2") if repeat % 2 == 0 else ("jbig2", "indexed")
                        for kind in kinds:
                            started = time.perf_counter()
                            save_variant(str(source), indexed if kind == "indexed" else layered, canvases, kind, token)
                            times[kind].append(time.perf_counter()-started)
                    verification = compare_outputs(str(source), indexed, layered, canvases, dpi, folder)
                    index_bytes, layer_bytes = indexed.stat().st_size, layered.stat().st_size
                    row = dict(source=str(source), input_bytes=source.stat().st_size, total_colors=colors,
                               dpi=dpi, repetitions=args.repeat, indexed_bytes=index_bytes, jbig2_bytes=layer_bytes,
                               layered_vs_indexed_percent=round((layer_bytes/index_bytes-1)*100, 2),
                               median_seconds={key: round(statistics.median(values), 4) for key, values in times.items()},
                               **verification)
                    rows.append(row)
                    summary = {key: row[key] for key in (
                        "source", "total_colors", "dpi", "indexed_bytes", "jbig2_bytes",
                        "layered_vs_indexed_percent", "median_seconds", "colored_masks",
                        "mupdf_pixel_exact", "poppler_decoded_masks_exact", "poppler_page_render_exact")}
                    summary["poppler_diagnostic_pages"] = len(row["poppler_render_diagnostics"])
                    print(json.dumps(summary), flush=True)
                    (folder / "metrics.json").write_text(json.dumps(rows, indent=2))
    finally:
        pipeline._ENCODE_WORKDIR.reset(context)


if __name__ == "__main__":
    main()
