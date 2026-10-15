"""Benchmark actual composite-first color PDFs and independently decode images."""
import argparse
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time

for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(name, "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pymupdf as fitz
import numpy as np
from PIL import Image
from pdf_minimalist.core.pipeline import save_with_spec
from pdf_minimalist.core.presets import PRESETS
from pdf_minimalist.core.recipes import preset_spec
from pdf_minimalist.core.display import DisplayPage


def verify(source, target, spec, folder):
    image_pages, dimensions, filters = 0, [], []
    with fitz.open(source) as before, fitz.open(target) as after:
        assert before.page_count == after.page_count
        for index, page in enumerate(after):
            original = before[index]
            old_words, new_words = original.get_text("words"), page.get_text("words")
            assert len(old_words) == len(new_words)
            for old, new in zip(old_words, new_words):
                assert old[4:] == new[4:]
                assert np.allclose(old[:4], new[:4], atol=.001, rtol=0)
            assert len(original.get_drawings()) == len(page.get_drawings())
            assert page.rotation == original.rotation and page.cropbox == original.cropbox
            entries = page.get_images(full=True)
            if not original.get_image_info():
                assert not entries
                continue
            assert len(entries) == 1 and entries[0][1] == 0
            entry = entries[0]
            rect = fitz.Rect(0, 0, page.cropbox.width, page.cropbox.height)
            expected = (rect * fitz.Matrix(spec["dpi_cap"]/72, spec["dpi_cap"]/72)).irect
            assert entry[2:4] == (expected.width, expected.height)
            native = fitz.Pixmap(after, entry[0])
            if native.colorspace != fitz.csRGB:
                native = fitz.Pixmap(fitz.csRGB, native)
            rgb = np.frombuffer(native.samples, dtype=np.uint8).reshape(native.height, native.width, 3)
            if spec["mode"] == "indexed":
                assert len(np.unique(rgb.reshape(-1, 3), axis=0)) <= spec["colors"]
            with tempfile.TemporaryDirectory(prefix="decode-", dir=folder) as scratch:
                prefix = str(Path(scratch) / "image")
                result = subprocess.run(["pdfimages", "-png", "-f", str(index+1),
                                         "-l", str(index+1), str(target), prefix],
                                        capture_output=True, check=True)
                assert not result.stderr, result.stderr.decode(errors="replace")
                decoded = list(Path(scratch).glob("image-*.png"))
                assert len(decoded) == 1
                with Image.open(decoded[0]) as image:
                    other = np.asarray(image.convert("RGB"))
                # JPEG decoders legitimately differ in chroma upsampling;
                # lossless Indexed and OpenJPEG readback must be exact.
                if after.xref_get_key(entry[0], "Filter")[1] == "/DCTDecode":
                    assert other.shape == rgb.shape and np.abs(other.astype(int)-rgb).mean() < 4
                else:
                    assert np.array_equal(other, rgb)
            dimensions.append(entry[2:4])
            filters.append(after.xref_get_key(entry[0], "Filter")[1])
            image_pages += 1
        # View the actual final-file composition, not encoder input pixels.
        pix = DisplayPage(after[0]).render(fitz.Matrix(2, 2))
        pix.save(str(target.with_suffix(".png")))
    return dict(poppler_verified_image_pages=image_pages, image_dimensions=dimensions,
                image_filters=filters, image_masks=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", default=["examples/images.pdf"])
    parser.add_argument("--repeat", type=int, default=2)
    parser.add_argument("--label", default="current")
    parser.add_argument("--before", type=Path)
    args = parser.parse_args()
    folder = Path(".tmp/color-layers") / args.label
    folder.mkdir(parents=True, exist_ok=True)
    rows = []
    for filename in args.files:
        source = Path(filename)
        for preset in PRESETS:
            if preset["mode"] not in ("color", "jpx", "indexed"):
                continue
            spec = preset_spec(preset)
            target = folder / f"{source.stem}.{preset['id']}.pdf"
            times = []
            for _ in range(args.repeat):
                started = time.perf_counter()
                save_with_spec(str(source), str(target), spec, workdir=str(folder))
                times.append(time.perf_counter() - started)
            row = dict(source=str(source), preset=preset["id"], spec=spec,
                       input_bytes=source.stat().st_size, output_bytes=target.stat().st_size,
                       median_seconds=round(statistics.median(times), 4),
                       **verify(source, target, spec, folder))
            if args.before and (old := args.before / target.name).is_file():
                row["before_bytes"] = old.stat().st_size
            rows.append(row)
            print(json.dumps(row), flush=True)
    (folder / "metrics.json").write_text(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
