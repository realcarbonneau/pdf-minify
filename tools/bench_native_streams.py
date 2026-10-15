"""Native text/vector/font compression: real paired PDFs, no image changes."""

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import time

for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(name, "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pymupdf as fitz
from PIL import Image

from pdf_minimalist.core import pipeline
from pdf_minimalist.core.display import DisplayPage
from pdf_minimalist.core.stream_compression import native_stream_xrefs, recompress_native_streams

POLICIES = ("none", "flate-fast", "flate", "zopfli", "brotli-9", "brotli", "lzw", "runlength")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def native_signature(doc):
    return Counter(digest(doc.xref_stream(xref)) for xref in native_stream_xrefs(doc))


def image_signature(doc):
    return Counter((digest(doc.xref_stream_raw(xref)),
                    *(doc.xref_get_key(xref, key)[1]
                      for key in ("Filter", "Width", "Height", "BitsPerComponent", "ImageMask")))
                   for xref in range(1, doc.xref_length())
                   if doc.xref_is_stream(xref) and doc.xref_get_key(xref, "Subtype")[1] == "/Image")


def fixture(path):
    """Actual native font/text/vector work, plus an untouched bitmap control."""
    with fitz.open() as doc:
        for index in range(3):
            page = doc.new_page(width=400, height=560)
            page.insert_text((20, 30), f"Native compression fixture {index+1}", fontsize=16)
            for row in range(35):
                page.insert_text((20, 55+row*12),
                                 f"Row {row:02}: Native text, vectors and exact glyphs 0123456789.",
                                 fontsize=9)
                page.draw_line((20, 59+row*12), (380, 59+row*12),
                               color=(.1, .4, .7), width=.2)
            # Long, dense operators cross all LZW width/reset boundaries.
            shape = page.new_shape()
            for point in range(2000):
                x, y = 20+(point*17 % 360), 490+(point*7 % 40)
                shape.draw_line((x, y), (x+1, y+1))
            shape.finish(color=(.7, .2, .1), width=.1)
            shape.commit()
        page = doc.new_page(width=400, height=560)
        page.insert_text((20, 30), "Embedded font / untouched image control")
        fontfile = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        if fontfile.is_file():
            page.insert_font(fontname="Embedded", fontfile=str(fontfile))
            page.insert_text((20, 70), "Subset original glyphs: Greek αβγ, Latin éèö.",
                             fontname="Embedded", fontsize=13)
        import io
        bitmap = io.BytesIO()
        Image.new("RGB", (91, 73), (240, 190, 20)).save(bitmap, "JPEG", quality=75)
        page.insert_image(fitz.Rect(20, 100, 200, 245), stream=bitmap.getvalue())
        doc.save(path)


def poppler_check(path, prefix):
    text = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, timeout=120)
    render = subprocess.run(["pdftoppm", "-r", "72", "-png", str(path), str(prefix)],
                            capture_output=True, timeout=120)
    pixels = []
    for png in sorted(prefix.parent.glob(prefix.name+"-*.png")):
        with Image.open(png) as image:
            pixels.append(digest(image.convert("RGB").tobytes()))
    return dict(text_sha256=digest(text.stdout), page_pixel_sha256=pixels,
                text_exit=text.returncode, render_exit=render.returncode,
                diagnostics=(text.stderr+render.stderr).decode(errors="replace"))


def qpdf_check(path, doc):
    if shutil.which("qpdf") is None:
        return dict(available=False)
    check = subprocess.run(["qpdf", "--check", str(path)], capture_output=True, timeout=120)
    # Independently decode the largest eligible stream as well as checking all
    # document syntax. This is not mislabeled as independent every-stream proof.
    candidates = list(native_stream_xrefs(doc))
    xref = max(candidates, key=lambda item: len(doc.xref_stream(item)))
    read = subprocess.run(["qpdf", f"--show-object={xref}", "--filtered-stream-data", str(path)],
                          capture_output=True, timeout=120)
    return dict(available=True, check_exit=check.returncode, decode_exit=read.returncode,
                largest_native_stream_exact=read.stdout == doc.xref_stream(xref),
                diagnostics=(check.stderr+read.stderr).decode(errors="replace"))


def run_case(source, folder, policies, repeat):
    baseline = folder / f"{source.stem}.baseline.pdf"
    pipeline.gc_copy(str(source), str(baseline))
    with fitz.open(baseline) as doc:
        expected_native, expected_images = native_signature(doc), image_signature(doc)
        expected_words = [page.get_text("words") for page in doc]
        expected_pixels = [digest(DisplayPage(page).render().samples) for page in doc]
        page_count = len(doc)
    have_poppler = shutil.which("pdftotext") and shutil.which("pdftoppm")
    baseline_poppler = poppler_check(baseline, folder / f"{source.stem}.baseline.poppler") if have_poppler else None
    rows = []
    # Alternate order on repeats; timing is local wall time, not a CPU ranking.
    for number in range(repeat):
        for policy in policies[::1 if number % 2 == 0 else -1]:
            target = folder / f"{source.stem}.{policy}.pdf"
            with fitz.open(baseline) as doc:
                stats = recompress_native_streams(doc, policy, directory=str(folder))
                start = time.perf_counter()
                doc.save(target, garbage=4, deflate=False, use_objstms=True, compression_effort=100)
                save_time = time.perf_counter()-start
            with fitz.open(target) as doc:
                start = time.perf_counter()
                assert native_signature(doc) == expected_native, (source, policy, "native bytes")
                decode_time = time.perf_counter()-start
                assert image_signature(doc) == expected_images, (source, policy, "image bytes")
                assert [page.get_text("words") for page in doc] == expected_words
                assert [digest(DisplayPage(page).render().samples) for page in doc] == expected_pixels
                reader = qpdf_check(target, doc) if number == repeat-1 else None
            item = dict(policy=policy, complete_pdf_bytes=target.stat().st_size,
                        save_seconds=save_time, decode_seconds=decode_time, **stats)
            if number == repeat-1:
                item["qpdf"] = reader
                if baseline_poppler is not None:
                    observed = poppler_check(target, folder / f"{source.stem}.{policy}.poppler")
                    item["poppler"] = dict(
                        exact_text=observed["text_sha256"] == baseline_poppler["text_sha256"],
                        exact_all_page_pixels=observed["page_pixel_sha256"] == baseline_poppler["page_pixel_sha256"],
                        **observed)
            rows.append(item)
            print(source.name, policy, target.stat().st_size, "bytes", flush=True)
    summary = []
    for policy in policies:
        variants = [item for item in rows if item["policy"] == policy]
        last = dict(variants[-1])
        for name in ("encode_seconds", "save_seconds", "decode_seconds"):
            last[name] = statistics.median(item[name] for item in variants)
        summary.append(last)
    return dict(source=str(source), input_bytes=source.stat().st_size, pages=page_count,
                baseline_bytes=baseline.stat().st_size, repetitions=repeat,
                exact_native_bytes=True, exact_image_bytes=True, exact_mupdf_pixels=True,
                baseline_poppler=baseline_poppler, results=summary, repetitions_raw=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", default=["examples/images.pdf",
                        "examples/paper-arxiv-1406.2661.pdf", "examples/models-nasa-kepler.pdf"])
    parser.add_argument("--policies", nargs="+", choices=POLICIES, default=list(POLICIES))
    parser.add_argument("--repeat", type=int, default=2)
    parser.add_argument("--label", default="main")
    args = parser.parse_args()
    if Path(args.label).name != args.label or args.label in (".", ".."):
        parser.error("label must be a single directory name")
    folder = Path(".tmp/native-stream-compression") / args.label
    folder.mkdir(parents=True, exist_ok=True)
    synthetic = folder / "native-text-vector-font.pdf"
    fixture(synthetic)
    reports = []
    for source in [*(Path(file) for file in args.files), synthetic]:
        reports.append(run_case(source, folder, args.policies, args.repeat))
        (folder / "metrics.json").write_text(json.dumps(reports, indent=2)+"\n")
    print("NATIVE STREAM BENCHMARK GREEN", flush=True)


if __name__ == "__main__":
    main()
