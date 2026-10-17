"""Size-only exact bitmap comparisons (§209); never launches the GUI.

Production composition/palette/threshold/JBIG2/native assembly/save are reused.
Only the experimental packed-stream transport/prediction is benchmark-owned.
"""

import argparse
from dataclasses import dataclass
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import zlib

for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pymupdf as fitz
from PIL import Image, __version__ as pillow_version

from pdf_minify.core import image_layers, pipeline, stream_compression as streams
from pdf_minify.core.cancel import CancelToken
from pdf_minify.core.canvas import flatten_rgb
from pdf_minify.core.display import DisplayPage
from pdf_minify.core.pdf_io import render_gray
from pdf_minify.core.stencils import PaletteCanvas, place_stencils
from tools.layered_color_jbig2 import write_fixture


VARIANTS = ("current-flate", "flate-plain", "flate-png", "zopfli-plain",
            "zopfli-png", "brotli-plain", "brotli-png", "jbig2")


def digest(data):
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class Bitmap:
    samples: np.ndarray
    packed: bytes
    bpc: int
    palette: np.ndarray | None = None

    @classmethod
    def color(cls, rgb, colors):
        canvas = PaletteCanvas.from_rgb(rgb, colors)
        bpc = pipeline.bpc_for(len(canvas.palette))
        return cls(canvas.indices, pipeline.pack_indices(canvas.indices, bpc), bpc, canvas.palette)

    @classmethod
    def bw(cls, gray, strategy, threshold):
        samples = pipeline._threshold(gray, strategy, threshold)
        packed = Image.fromarray(samples).convert("1", dither=Image.Dither.NONE).tobytes()
        return cls(samples, packed, 1)

    @property
    def width(self):
        return self.samples.shape[1]

    @property
    def height(self):
        return self.samples.shape[0]

    @property
    def rgb(self):
        return (self.palette[self.samples] if self.palette is not None
                else np.repeat(self.samples[:, :, None], 3, axis=2))

    def description(self):
        return dict(width=self.width, height=self.height, bpc=self.bpc,
                    palette_colors=len(self.palette) if self.palette is not None else 2,
                    raw_bytes=len(self.packed), packed_sha256=digest(self.packed),
                    palette_sha256=digest(self.palette.tobytes()) if self.palette is not None else None)


def predict_rows(data, width, height, bpc):
    """Reversible adaptive PNG byte predictors; one packed component, bpp=1."""
    stride = (width*bpc+7)//8
    rows = np.frombuffer(data, dtype=np.uint8).reshape(height, stride)
    output = bytearray()
    previous = np.zeros(stride, dtype=np.int16)
    for row in rows:
        current = row.astype(np.int16)
        left = np.concatenate((np.zeros(1, dtype=np.int16), current[:-1]))
        upper_left = np.concatenate((np.zeros(1, dtype=np.int16), previous[:-1]))
        estimate = left+previous-upper_left
        distance = np.stack((abs(estimate-left), abs(estimate-previous), abs(estimate-upper_left)))
        paeth = np.choose(distance.argmin(axis=0), (left, previous, upper_left))
        predictions = np.stack((np.zeros(stride, dtype=np.int16), left, previous,
                                (left+previous)//2, paeth))
        candidates = (current-predictions).astype(np.uint8)
        signed = candidates.astype(np.int16)
        scores = np.minimum(signed, 256-signed).sum(axis=1)
        chosen = int(scores.argmin())
        output.append(chosen)
        output.extend(candidates[chosen].tobytes())
        previous = current
    return bytes(output)


def prepare(source, mode, dpi, colors, strategy, threshold, folder):
    """Prepare each source page ONCE, independent of the candidate encoders."""
    token = CancelToken()
    bitmaps = []
    with fitz.open(source) as original:
        for pno, page in enumerate(original):
            if mode == "bw-ffpr":
                rgb = flatten_rgb(page, dpi, token, pipeline.force_to_dpi,
                                  directory=str(folder), minimum_dpi=dpi)
                bitmaps.append(Bitmap.bw(np.asarray(rgb.convert("L")), strategy, threshold))
                continue
            if mode == "indexed-ffpr":
                rgb = flatten_rgb(page, dpi, token, pipeline.force_to_dpi,
                                  directory=str(folder), minimum_dpi=dpi)
                bitmaps.append(Bitmap.color(rgb, colors))
                continue
            with image_layers._copy_page(original, pno) as fragment:
                if not fragment[0].get_image_info():
                    bitmaps.append(None)
                    continue
                layer = "canvas" if mode == "indexed" else "images"
                image_layers._filter(fragment[0], token, layer,
                                     backdrops=image_layers._page_backdrops(fragment[0]))
                rgb = flatten_rgb(fragment[0], dpi, token, pipeline.force_to_dpi, directory=str(folder))
                bitmaps.append(Bitmap.color(rgb, colors) if mode == "indexed" else
                               Bitmap.bw(np.asarray(rgb.convert("L")), strategy, threshold))
    return bitmaps


def encoded_samples(bitmap, variant, folder):
    if variant == "current-flate":
        payload = (pipeline.deflate_best(bitmap.packed) if bitmap.palette is not None
                   else zlib.compress(bitmap.packed, 9))
        return payload, "/FlateDecode", None
    policy, prediction = variant.split("-")
    raw = bitmap.packed
    params = None
    if prediction == "png":
        raw = predict_rows(raw, bitmap.width, bitmap.height, bitmap.bpc)
        params = (f"<< /Predictor 15 /Colors 1 /BitsPerComponent {bitmap.bpc} "
                  f"/Columns {bitmap.width} >>")
    payload, filtr = streams.encode_stream(raw, policy, directory=str(folder))
    return payload, filtr, params


def place_bitmap(out, page, bitmap, variant, folder):
    if variant == "jbig2":
        if bitmap.palette is not None:
            canvas = PaletteCanvas(bitmap.samples, bitmap.palette)
            place_stencils(out, page, page.rect, canvas)
        else:
            payload = pipeline.encode_binary_jbig2(bitmap.samples)
            if payload is None or not pipeline.jbig2_renders(
                    payload, bitmap.width, bitmap.height, bitmap.samples):
                raise RuntimeError("BW JBIG2 failed exact validation; no fallback")
            pipeline._place_bw(out, page, page.rect, payload, "jbig2", bitmap.width, bitmap.height)
        return
    payload, filtr, params = encoded_samples(bitmap, variant, folder)
    color_space = (f"[/Indexed /DeviceRGB {len(bitmap.palette)-1} <{bitmap.palette.tobytes().hex().upper()}>]"
                   if bitmap.palette is not None else "/DeviceGray")
    xref = out.get_new_xref()
    out.update_object(xref, f"<< /Type /XObject /Subtype /Image /Width {bitmap.width} "
                      f"/Height {bitmap.height} /ColorSpace {color_space} "
                      f"/BitsPerComponent {bitmap.bpc} /Interpolate false >>")
    out.update_stream(xref, payload, compress=False)
    out.xref_set_key(xref, "Filter", filtr)
    if params:
        out.xref_set_key(xref, "DecodeParms", params)
    if out.xref_stream(xref) != bitmap.packed:
        raise RuntimeError(f"{variant}: packed samples did not decode byte-exact")
    page.insert_image(page.rect, xref=xref, keep_proportion=False)


def set_pdf_id(doc, input_hash, prepared, variant):
    """Distinct deterministic IDs with identical literal-string framing size."""
    first = input_hash[:16]
    second = digest(json.dumps(prepared, sort_keys=True).encode()+variant.encode())[:16]
    doc.xref_set_key(-1, "ID", f"[<{first.encode().hex()}> <{second.encode().hex()}>]")
    assert first in doc.xref_get_key(-1, "ID")[1]


def open_for_id_change(target):
    """Normalize an xref-stream trailer through a plain in-memory container.

    MuPDF 1.28.2 copy-on-write can update its xref object's ID but leave the
    writer trailer unchanged. A standard container-only roundtrip makes that
    trailer direct; no image codec is decoded/re-encoded by this conversion.
    """
    with fitz.open(target) as doc:
        data = doc.tobytes(garbage=4, deflate=False, deflate_fonts=False,
                           use_objstms=False, no_new_id=True)
    return fitz.open(stream=data, filetype="pdf")


def stabilize_existing_id(source_hash, prepared, variant, target, folder, *, brotli_declaration=False):
    first = source_hash[:16]
    second = digest(json.dumps(prepared, sort_keys=True).encode()+variant.encode())[:16]
    with fitz.open(target) as previous:
        value = previous.xref_get_key(-1, "ID")[1]
        if first in value and second in value:
            return
    with open_for_id_change(target) as doc:
        set_pdf_id(doc, source_hash, prepared, variant)
        stable, original = target.with_suffix(".fixed-id.pdf"), target.with_suffix(".original-id.pdf")
        if stable.exists() or original.exists():
            raise FileExistsError("Refusing to overwrite an ID-normalization archive")
        work_context = pipeline._ENCODE_WORKDIR.set(str(folder))
        stream_context = pipeline._STREAM_POLICY.set("flate")
        declaration_context = pipeline._BROTLI_DECLARATION.set(bool(brotli_declaration))
        try:
            pipeline._save_optimized_pdf(doc, str(stable), no_new_id=True)
        finally:
            pipeline._STREAM_POLICY.reset(stream_context)
            pipeline._BROTLI_DECLARATION.reset(declaration_context)
            pipeline._ENCODE_WORKDIR.reset(work_context)
    target.replace(original)
    stable.replace(target)


def save_variant(source, target, bitmaps, mode, variant, folder, *, brotli_declaration=False):
    """One shared native page assembler and optimizer; no alternative saver."""
    token = CancelToken()
    from pdf_minify.core.native_layer import NativeContext
    work_context = pipeline._ENCODE_WORKDIR.set(str(folder))
    stream_context = pipeline._STREAM_POLICY.set("flate")
    declaration_context = pipeline._BROTLI_DECLARATION.set(
        bool(brotli_declaration and variant.startswith("brotli")))
    try:
        with fitz.open(source) as original:
            # An untouched xref-stream document needs a direct trailer before
            # controlled ID assignment (B113), just like the final saver.
            # Image-bearing and FFPR preparation retain their existing path.
            with (fitz.open() if mode.endswith("-ffpr") else
                  fitz.open(source) if any(bitmap is not None for bitmap in bitmaps)
                  else open_for_id_change(source)) as doc:
                native_context = NativeContext(doc)
                if len(bitmaps) != len(original):
                    raise ValueError("Prepared page count does not match source")
                for pno, bitmap in enumerate(bitmaps):
                    if mode.endswith("-ffpr"):
                        rect = original[pno].rect
                        page = doc.new_page(width=rect.width, height=rect.height)
                        place_bitmap(doc, page, bitmap, variant, folder)
                    else:
                        if bitmap is None:
                            continue
                        def paint(out, page, _fragment):
                            place_bitmap(out, page, bitmap, variant, folder)
                        with image_layers._copy_page(original, pno) as prepared:
                            image_layers._assemble_layers(doc, pno, prepared, token,
                                                         "canvas" if mode == "indexed" else "images", paint,
                                                         native_context=native_context)
                set_pdf_id(doc, digest(source.read_bytes()),
                           [bitmap.description() if bitmap else None for bitmap in bitmaps], variant)
                pipeline._save_optimized_pdf(doc, str(target), no_new_id=True)
    finally:
        pipeline._STREAM_POLICY.reset(stream_context)
        pipeline._BROTLI_DECLARATION.reset(declaration_context)
        pipeline._ENCODE_WORKDIR.reset(work_context)


def render_signature(page, dpi):
    image = DisplayPage(page).render(fitz.Matrix(dpi/72, dpi/72))
    return image.width, image.height, digest(image.samples)


def page_signature(page, dpi):
    return dict(words=page.get_text("words"), rotation=page.rotation,
                cropbox=tuple(page.cropbox), mediabox=tuple(page.mediabox),
                links=[(item.get("kind"), item.get("uri"), item.get("page")) for item in page.get_links()],
                annotations=[annot.info for annot in page.annots()], drawings=len(page.get_drawings()),
                renders=[render_signature(page, scale) for scale in sorted({72, dpi})])


def assert_native_text(original, saved):
    """Check extracted characters AND native glyph/font/paint geometry.

    Extraction block numbers include image/ActualText blocks. Composing many
    images into one legitimately renumbers those bookkeeping IDs, without
    changing any text. Glyph origins/bounds retain the established 0.001pt
    serialization tolerance; characters, font names, paint and counts don't.
    """
    diagnostics = dict(prior=fitz.TOOLS.mupdf_warnings(), original=[], output=[])

    def observe(operation, side):
        result = operation()
        diagnostics[side].append(fitz.TOOLS.mupdf_warnings())
        return result

    # An intervening image/ActualText block can make an extractor return
    # "page)" and "." versus "page)." despite identical positioned characters.
    # Check semantic non-whitespace replacements, not inferred gap-spaces or
    # the image-only ActualText whitespace deliberately removed by B109.
    # EVERY native glyph, including every real space, is checked below.
    def characters(page):
        flags = (fitz.TEXTFLAGS_RAWDICT | fitz.TEXT_INHIBIT_SPACES) & ~fitz.TEXT_PRESERVE_IMAGES
        return [char for block in page.get_text("rawdict", flags=flags)["blocks"] if "lines" in block
                for line in block["lines"] for span in line["spans"] for char in span["chars"]
                if not char["c"].isspace()]
    before = observe(lambda: characters(original), "original")
    after = observe(lambda: characters(saved), "output")
    assert len(before) == len(after), "native character count"
    assert [char["c"] for char in before] == [char["c"] for char in after], "native extracted characters"
    before_positions = np.asarray([(*c["origin"], *c["bbox"]) for c in before], dtype=float)
    after_positions = np.asarray([(*c["origin"], *c["bbox"]) for c in after], dtype=float)
    assert np.allclose(before_positions, after_positions, atol=.001, rtol=0), "native character geometry"
    # Sanitizing equivalent text operators can split/merge trace runs. Check
    # every glyph and its effective style instead of incidental run grouping.
    def glyphs(page):
        identity, geometry = [], []
        fields = ("font", "flags", "type", "wmode", "bidi_lvl", "bidi_dir", "color", "opacity", "layer")
        for run in page.get_texttrace():
            style = tuple(run[field] for field in fields) + (run["linewidth"] is None,)
            for char in run["chars"]:
                identity.append((style, char[0], char[1]))
                geometry.append((*run["dir"], run["size"], run["linewidth"] or 0, *char[2], *char[3]))
        return identity, np.asarray(geometry, dtype=float).reshape(-1, 10)
    before, before_geometry = observe(lambda: glyphs(original), "original")
    after, after_geometry = observe(lambda: glyphs(saved), "output")
    assert len(before) == len(after), "native glyph count"
    outlines = (_FontOutlines(original), _FontOutlines(saved))
    for a, b in zip(before, after):
        assert a[:2] == b[:2], "native glyph identity/style/count"
        if a[2] != b[2]:
            # Legal font subsetting can renumber local glyph indices. Verify
            # the actual vector outline, not an incidental font-local number.
            source_paths = observe(lambda: outlines[0].paths(a[0][0], a[2]), "original")
            saved_paths = observe(lambda: outlines[1].paths(b[0][0], b[2]), "output")
            assert source_paths & saved_paths, "native glyph outline"
    # An unused space glyph's inferred width can change after font subsetting;
    # every ACTUAL space and symbol glyph still has to pass this geometry check.
    assert np.allclose(before_geometry, after_geometry, atol=.001, rtol=0), "native glyph geometry"
    added = diagnostic_messages("\n".join(diagnostics["output"])) - diagnostic_messages("\n".join(diagnostics["original"]))
    assert not added, f"New native text diagnostics: {sorted(added)}"
    return diagnostics


class _Outline(fitz.mupdf.FzPathWalker2):
    def __init__(self):
        super().__init__()
        self.ops = []
        for name in ("moveto", "lineto", "curveto", "closepath"):
            getattr(self, f"use_virtual_{name}")()
        # Explicitly initialize optional function pointers as well; an absent
        # shortcut uses MuPDF's expansion into the four handlers above.
        for name in ("quadto", "curvetov", "curvetoy", "rectto"):
            getattr(self, f"use_virtual_{name}")(False)

    def moveto(self, _ctx, x, y):
        self.ops.append(("m", x, y))

    def lineto(self, _ctx, x, y):
        self.ops.append(("l", x, y))

    def curveto(self, _ctx, *points):
        self.ops.append(("c", *points))

    def closepath(self, _ctx):
        self.ops.append(("h",))


class _FontOutlines:
    """Lazy exact outline proof for legitimately renumbered subset glyphs."""
    def __init__(self, page):
        self.page, self.fonts, self.cache = page, None, {}

    def paths(self, name, gid):
        key = name, gid
        if key in self.cache:
            return self.cache[key]
        if self.fonts is None:
            self.fonts = {}
            for xref in dict.fromkeys(entry[0] for entry in self.page.get_fonts(full=True)):
                font_name, _, _, data = self.page.parent.extract_font(xref)
                if not data:
                    continue
                font = fitz.Font(fontbuffer=data)
                for alias in {re.sub(r"^[A-Z]{6}\+", "", font_name), font.name}:
                    self.fonts.setdefault(alias, []).append(font)
        paths = set()
        for font in self.fonts.get(name, []):
            path = fitz.mupdf.fz_outline_glyph(font.this, gid, fitz.mupdf.FzMatrix())
            if path:
                walker = _Outline()
                # The director's opaque argument is its internal walker,
                # as required by MuPDF's FzPathWalker2 binding contract.
                fitz.mupdf.fz_walk_path(path, walker, walker.m_internal)
                paths.add(tuple(walker.ops))
        assert paths, f"Cannot verify renumbered native glyph outline: {name}/{gid}"
        self.cache[key] = paths
        return paths


def diagnostic_messages(diagnostics):
    return {line for line in diagnostics.splitlines()
            if line and not re.fullmatch(r"\.\.\. repeated \d+ times\.\.\.", line)}


def assert_no_retained_source_images(original, saved, replacement_xrefs=None):
    """Catch source bitmaps kept by non-page owners, e.g. stale MCR /Stm.

    A selected replacement can legitimately have identical encoded bytes to
    the source (an idempotent transform). Its verified/painted xref is allowed,
    not every hidden object with the same hash. Native opacity/Type 3 resources
    are not page-image occurrences and are not authorized for deletion.
    """
    source_images = {digest(original.xref_stream_raw(info["xref"]))
                     for page in original for info in page.get_image_info(xrefs=True)
                     if info["xref"] > 0}
    if replacement_xrefs is None:
        replacement_xrefs = {info["xref"] for page in saved
                             for info in page.get_image_info(xrefs=True) if info["xref"] > 0}
    retained = [xref for xref in range(1, saved.xref_length())
                if xref not in replacement_xrefs and saved.xref_is_stream(xref)
                and saved.xref_get_key(xref, "Subtype")[1] == "/Image"
                and digest(saved.xref_stream_raw(xref)) in source_images]
    assert not retained, f"retained replaced source image streams outside the verified canvas: {retained}"


def verify_variant(source, target, bitmaps, mode, variant, dpi, expected=None):
    """Final PDF samples, native content and exact actual no-AA page renders."""
    # This is a standalone, sequential tool process, not the shared GUI/core
    # gate. Archive every drained diagnostic; distinguish original malformed
    # native paths from NEW image codec errors rather than suppressing either.
    prior_diagnostics = fitz.TOOLS.mupdf_warnings()
    diagnostics = []
    image_xrefs = set()
    signatures = []
    with fitz.open(source) as original, fitz.open(target) as doc:
        assert len(doc) == len(original) == len(bitmaps)
        for pno, (page, bitmap) in enumerate(zip(doc, bitmaps)):
            if expected is None:
                original_signature = page_signature(original[pno], dpi)
                source_diagnostics = fitz.TOOLS.mupdf_warnings()
            else:
                original_signature = expected[pno]["original"]
                source_diagnostics = expected[pno]["source_diagnostics"]
            images = page.get_images(full=True)
            expected_count = (0 if bitmap is None else
                              PaletteCanvas(bitmap.samples, bitmap.palette).nonwhite_colors
                              if variant == "jbig2" and bitmap.palette is not None else 1)
            assert len(images) == expected_count, (pno, variant, "image count")
            reconstructed = np.full_like(bitmap.rgb, 255) if bitmap and variant == "jbig2" and bitmap.palette is not None else None
            coverage = np.zeros(bitmap.samples.shape, dtype=bool) if reconstructed is not None else None
            for image in images:
                xref = image[0]
                image_xrefs.add(xref)
                assert image[2:4] == (bitmap.width, bitmap.height)
                assert doc.xref_get_key(xref, "Interpolate")[1] == "false"
                assert doc.xref_get_key(xref, "Filter")[1] == (
                    "/JBIG2Decode" if variant == "jbig2" else
                    "/BrotliDecode" if variant.startswith("brotli") else "/FlateDecode")
                pix = fitz.Pixmap(doc, xref)
                actual = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
                if reconstructed is not None:
                    index = int(image[7].removeprefix("C"))
                    marked = bitmap.samples == index
                    assert doc.xref_get_key(xref, "ImageMask")[1] == "true"
                    assert np.array_equal(actual[:, :, 0], np.where(marked, 255, 0))
                    assert not np.any(coverage & marked)
                    coverage |= marked
                    reconstructed[marked] = bitmap.palette[index]
                else:
                    wanted = bitmap.rgb if bitmap.palette is not None else bitmap.samples[:, :, None]
                    assert np.array_equal(actual, wanted), (pno, variant, "decoded image samples")
                    if variant != "jbig2":
                        assert doc.xref_stream(xref) == bitmap.packed
                decode_diagnostics = fitz.TOOLS.mupdf_warnings()
                if decode_diagnostics:
                    raise RuntimeError(f"{variant}: image decode diagnostics: {decode_diagnostics}")
            if reconstructed is not None:
                assert np.array_equal(reconstructed, bitmap.rgb)
            signature = page_signature(page, dpi)
            observed_diagnostics = fitz.TOOLS.mupdf_warnings()
            if diagnostic_messages(observed_diagnostics) - diagnostic_messages(source_diagnostics):
                raise RuntimeError(f"{variant}: new page diagnostics: {observed_diagnostics}")
            diagnostics.append(dict(page=pno+1, original=source_diagnostics, output=observed_diagnostics))
            if mode.endswith("-ffpr"):
                assert not signature["words"]
            else:
                diagnostics[-1]["native_text"] = assert_native_text(original[pno], page)
            if expected is not None:
                for field in ("rotation", "cropbox", "mediabox", "links", "annotations", "renders"):
                    assert signature[field] == expected[pno][field], (pno, variant, field)
                assert len(signature["words"]) == len(expected[pno]["words"])
                assert signature["drawings"] == expected[pno]["drawings"] + int(reconstructed is not None)
            signature["original"] = original_signature
            signature["source_diagnostics"] = source_diagnostics
            signatures.append(signature)
        assert_no_retained_source_images(original, doc, image_xrefs)
        image_bytes = sum(len(doc.xref_stream_raw(xref)) for xref in image_xrefs)
    return dict(variant=variant, complete_pdf_bytes=target.stat().st_size,
                pdf_sha256=digest(target.read_bytes()),
                encoded_image_bytes=image_bytes, image_objects=len(image_xrefs),
                decoded_samples_exact=True, actual_pages_exact=True, native_artwork_retained=not mode.endswith("-ffpr"),
                pre_validation_diagnostics=prior_diagnostics, page_diagnostics=diagnostics,
                pdf=str(target)), signatures


def run_case(source, folder, *, mode="indexed", dpi=300, colors=5, strategy="otsu", threshold=180,
             variants=VARIANTS, resume=False, brotli_declaration=False):
    folder.mkdir(parents=True, exist_ok=resume)
    bitmaps = prepare(source, mode, dpi, colors, strategy, threshold, folder)
    row = dict(source=str(source), input_bytes=source.stat().st_size,
               input_sha256=digest(source.read_bytes()), mode=mode, dpi=dpi,
               environment=dict(python=sys.version.split()[0], pymupdf=fitz.VersionBind,
                                numpy=np.__version__, pillow=pillow_version,
                                jbig2=pipeline.jbig2_binary(), zopfli=pipeline.zopfli_binary()),
               colors=colors if mode.startswith("indexed") else None,
               threshold_method=strategy if not mode.startswith("indexed") else None,
               threshold=threshold if not mode.startswith("indexed") and strategy == "simple" else None,
               pages=len(bitmaps), native_stream_policy="flate", repetitions=1, id_policy="fixed-ascii16-v1",
               brotli_declaration=bool(brotli_declaration),
               prepared=[bitmap.description() if bitmap else None for bitmap in bitmaps], results=[])
    if resume and (folder / "metrics.json").exists():
        prior = json.loads((folder / "metrics.json").read_text())
        if prior.get("brotli_declaration") != row["brotli_declaration"]:
            raise ValueError("Cannot reuse changed benchmark input: Brotli declaration setting")
        for field in ("input_sha256", "environment", "mode", "dpi", "colors", "threshold_method", "threshold", "prepared"):
            if prior[field] != row[field]:
                raise ValueError(f"Cannot reuse changed benchmark input: {field}")
    expected = None
    for variant in variants:
        declaration = bool(brotli_declaration and variant.startswith("brotli"))
        target = folder / f"{variant}.pdf"
        reused = resume and target.exists()
        if reused:
            stabilize_existing_id(row["input_sha256"], row["prepared"], variant, target, folder,
                                  brotli_declaration=declaration)
        else:
            save_variant(source, target, bitmaps, mode, variant, folder,
                         brotli_declaration=declaration)
        result, signatures = verify_variant(source, target, bitmaps, mode, variant, dpi, expected)
        with fitz.open(target) as doc:
            if streams.brotli_declaration_present(doc) != declaration:
                raise ValueError("Wrong Brotli extension declaration setting")
        result["brotli_declaration"] = declaration
        result["reused_existing_pdf"] = reused
        if expected is None:
            expected = signatures
        row["results"].append(result)
        (folder / "metrics.json").write_text(json.dumps(row, indent=2)+"\n")
        print(json.dumps(dict(case=folder.name, **{key: result[key] for key in (
            "variant", "complete_pdf_bytes", "encoded_image_bytes", "actual_pages_exact", "reused_existing_pdf")})), flush=True)
    # A selected subset need not contain Classic Flate. Report actual complete
    # bytes; named paired comparisons belong to the publication, not an
    # implicit first-variant baseline mislabeled as Classic Flate.
    row["smallest"] = min(row["results"], key=lambda item: item["complete_pdf_bytes"])["variant"]
    (folder / "metrics.json").write_text(json.dumps(row, indent=2)+"\n")
    return row


def cases(folder, smoke=False):
    fixtures = {}
    for kind in ("flat", "noise"):
        source = folder / f"synthetic-{kind}.pdf"
        if not source.exists():
            write_fixture(source, kind)
        fixtures[kind] = source
    if smoke:
        yield fixtures["flat"], dict(mode="indexed", dpi=36, colors=5)
        yield fixtures["noise"], dict(mode="bw-images", dpi=36)
        return
    for name in ("images.pdf", "paper-arxiv-1406.2661.pdf"):
        for count in (5, 16, 64):
            yield Path("examples") / name, dict(mode="indexed", dpi=300, colors=count)
    for source in fixtures.values():
        for count in (5, 16):
            yield source, dict(mode="indexed", dpi=300, colors=count)
    for method, threshold in (("otsu", 180), ("simple", 180), ("simple", 210)):
        yield Path("examples/images.pdf"), dict(mode="bw-images", dpi=300, strategy=method, threshold=threshold)
    for name in ("paper-arxiv-1406.2661.pdf", "scan-jfk-poor-copies.pdf", "scan-naca-formulas.pdf"):
        yield Path("examples") / name, dict(mode="bw-images", dpi=300)
    for name in ("images.pdf", "paper-arxiv-1406.2661.pdf"):
        yield Path("examples") / name, dict(mode="bw-ffpr", dpi=300)
    for source in fixtures.values():
        yield source, dict(mode="bw-images", dpi=300)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", default="size-main")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--brotli-declaration", action="store_true",
                        help="Opt in to Brotli extension compatibility metadata (default: omitted)")
    parser.add_argument("--resume", action="store_true", help="revalidate unchanged existing PDFs; encode only missing ones")
    args = parser.parse_args()
    if Path(args.label).name != args.label or args.label in (".", ".."):
        parser.error("label must be a single directory name")
    folder = Path(".tmp/image-stream-compression") / args.label
    folder.mkdir(parents=True, exist_ok=args.resume)
    rows = []
    for source, params in cases(folder, args.smoke):
        suffix = (f"{params['colors']}colors" if params["mode"] == "indexed" else
                  f"{params.get('strategy', 'otsu')}-{params.get('threshold', 180)}")
        label = f"{source.stem}.{params['mode']}.{params['dpi']}dpi.{suffix}"
        rows.append(run_case(source, folder / label, resume=args.resume,
                             brotli_declaration=args.brotli_declaration, **params))
        (folder / "metrics.json").write_text(json.dumps(rows, indent=2)+"\n")
    print("IMAGE STREAM SIZE BENCHMARK GREEN", flush=True)


if __name__ == "__main__":
    main()
