"""Measure real complete BW PDFs, their masks, text retention and decoder output."""
import argparse
import csv
import json
import os
from pathlib import Path
import statistics
import subprocess
import tempfile
import sys
import time

for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(name, "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fitz
import numpy as np
from PIL import Image
from pdf_minify.core.pipeline import save_with_spec, jbig2_binary, _threshold


def inspect(path):
    with fitz.open(path) as doc:
        images, masks = set(), set()
        for page in doc:
            for image in page.get_images(full=True):
                images.add(image[0])
                if image[1]:
                    masks.add(image[1])
            assert page.get_pixmap(dpi=150, colorspace=fitz.csRGB, alpha=False).samples
        images -= masks
        fonts = set()
        for xref in range(1, doc.xref_length()):
            for key in ("FontFile", "FontFile2", "FontFile3"):
                kind, value = doc.xref_get_key(xref, key)
                if kind == "xref":
                    fonts.add(int(value.split()[0]))
        return {
            "pages": doc.page_count,
            "text": [page.get_text(sort=True) for page in doc],
            "image_xobjects": len(images), "masks": len(masks),
            "image_stream_bytes": sum(len(doc.xref_stream_raw(x)) for x in images),
            "mask_stream_bytes": sum(len(doc.xref_stream_raw(x)) for x in masks),
            "font_stream_bytes": sum(len(doc.xref_stream_raw(x)) for x in fonts),
            "filters": [doc.xref_get_key(x, "Filter")[1] for x in sorted(images)],
            "bits": [doc.xref_get_key(x, "BitsPerComponent")[1] for x in sorted(images)],
        }


def verify(source, target, spec, folder):
    """Every-page FFPR pixels, native words, and independent Poppler image decode."""
    image_pages, exact_pages = 0, 0
    with fitz.open(source) as before, fitz.open(target) as after:
        assert before.page_count == after.page_count
        for i in range(after.page_count):
            page = after[i]
            if spec["force_raster"]:
                original = before[i].get_pixmap(dpi=spec["dpi"], colorspace=fitz.csGRAY)
                saved = page.get_pixmap(dpi=spec["dpi"], colorspace=fitz.csGRAY)
                expected = _threshold(np.frombuffer(original.samples, dtype=np.uint8).reshape(
                    original.height, original.width), spec["strategy"], spec["t"])
                actual = np.frombuffer(saved.samples, dtype=np.uint8).reshape(saved.height, saved.width)
                assert np.array_equal(expected, actual), (str(target), i, "FFPR pixel mismatch")
                exact_pages += 1
            else:
                original_words = before[i].get_text("words", sort=True)
                saved_words = page.get_text("words", sort=True)
                assert len(original_words) == len(saved_words), (str(target), i, "native word count")
                for original_word, saved_word in zip(original_words, saved_words):
                    assert original_word[4] == saved_word[4], (str(target), i, "native text mismatch")
                    # Native PDF float serialization changed three Kepler word
                    # coordinates by <0.00002 pt, not font geometry or placement.
                    assert np.allclose(original_word[:4], saved_word[:4], atol=.001, rtol=0), (
                        str(target), i, "native placement mismatch", original_word, saved_word)
            entries = page.get_images(full=True)
            if not entries:
                continue
            assert len(entries) == 1 and entries[0][1] == 0, (str(target), i, entries)
            native = fitz.Pixmap(after, entries[0][0])
            expected_image = np.frombuffer(native.samples, dtype=np.uint8).reshape(native.height, native.width)
            assert set(np.unique(expected_image)) <= {0, 255}
            with tempfile.TemporaryDirectory(prefix="decode-", dir=folder) as scratch:
                prefix = str(Path(scratch) / "image")
                result = subprocess.run(["pdfimages", "-f", str(i + 1), "-l", str(i + 1),
                                         str(target), prefix], capture_output=True, check=True)
                assert not result.stderr, result.stderr.decode(errors="replace")
                outputs = list(Path(scratch).glob("image-*.pbm"))
                assert len(outputs) == 1, (str(target), i, list(Path(scratch).iterdir()))
                with Image.open(outputs[0]) as decoded:
                    actual_image = np.asarray(decoded.convert("L"))
                assert np.array_equal(actual_image, expected_image), (str(target), i, "Poppler image mismatch")
            image_pages += 1
    return {"pixel_exact_ffpr_pages": exact_pages, "poppler_verified_image_pages": image_pages}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", default=["examples/images.pdf"])
    parser.add_argument("--label", default="current")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--dpis", nargs="+", type=int, default=[150, 300])
    parser.add_argument("--strategies", nargs="+", default=["otsu", "simple"])
    args = parser.parse_args()
    folder = Path(".tmp/bw-layers") / args.label
    folder.mkdir(parents=True, exist_ok=True)
    rows = []
    print("PyMuPDF", fitz.VersionBind, "JBIG2", jbig2_binary(), flush=True)
    for filename in args.files:
        source = Path(filename)
        original = inspect(source)
        for dpi in args.dpis:
            for strategy in args.strategies:
                for forced in (False, True):
                    spec = dict(mode="bw", strategy=strategy, t=210, dpi=dpi,
                                force_raster=forced, page_size="original")
                    target = folder / f"{source.stem}.{dpi}.{strategy}.ffpr-{int(forced)}.pdf"
                    timings = []
                    for _ in range(args.repeat):
                        started = time.perf_counter()
                        save_with_spec(str(source), str(target), spec)
                        timings.append(time.perf_counter() - started)
                    result = inspect(target)
                    assert result["text"] == ([""] * original["pages"] if forced else original["text"])
                    result.pop("text")
                    checks = verify(source, target, spec, folder)
                    row = dict(source=str(source), label=args.label, dpi=dpi,
                               strategy=strategy, threshold=210 if strategy == "simple" else None,
                               force_raster=forced, in_bytes=source.stat().st_size,
                               out_bytes=target.stat().st_size,
                               seconds=round(statistics.median(timings), 4), **result, **checks)
                    rows.append(row)
                    print(json.dumps(row), flush=True)
    (folder / "metrics.json").write_text(json.dumps(rows, indent=2))
    with (folder / "metrics.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
