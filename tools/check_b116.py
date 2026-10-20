"""B116 real-file repair proof and exact-render review; not a table-size refresh."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from PIL import Image, ImageDraw
import pymupdf as fitz

from pdf_minify.core.cancel import CancelToken
from pdf_minify.core.canvas import flatten_rgb
from pdf_minify.core.display import DisplayPage
from tools import bench_lossy_quality as lossy


BEFORE = Path(".tmp/lossy-quality/q75-fixed-20261019/metrics.json")
BEFORE_SHA256 = "d0d015cc4dffd677f4c85e97a171b8bb7f651e45bb6dec208df1589065219efc"
REGIONS = (("emblem", (772, 42, 794, 74)),
           ("left-photo", (55, 800, 180, 865)),
           ("right-photo", (660, 995, 795, 1120)))


def render(page, dpi):
    pix = DisplayPage(page).render(fitz.Matrix(dpi / 72, dpi / 72))
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def review(folder, document, previous, records):
    source = fitz.open(document.source)
    old = fitz.open(previous["color"]["pdf"])
    jpeg, jpx = (fitz.open(r["pdf"]) for r in records)
    try:
        documents = (source, old, jpeg, jpx)
        labels = ("Original", "Before repair: JPEG q75", "Fixed: JPEG q75", "Fixed: JPEG2000 q75")
        views = [render(d[0], 72) for d in documents]
        width, height = views[0].size
        sheet = Image.new("RGB", (4 * (width + 12) + 12, height + 40), "#cccccc")
        draw = ImageDraw.Draw(sheet)
        for index, (label, view) in enumerate(zip(labels, views, strict=True)):
            x = 12 + index * (width + 12)
            draw.text((x, 5), label, fill="black")
            sheet.paste(view, (x, 28))
        sheet.save(folder / "screen.png")

        views = [render(d[0], 300) for d in documents]
        source_rgb = flatten_rgb(source[0], 300, CancelToken(), lossy.pipeline.force_to_dpi,
                                 directory=str(folder))
        expected = np.asarray(source_rgb)
        checks = []
        crops = Image.new("RGB", (4 * 268 + 12, 3 * 290 + 12), "#cccccc")
        draw = ImageDraw.Draw(crops)
        for row, (name, box) in enumerate(REGIONS):
            rect = (fitz.Rect(box) * fitz.Matrix(300 / 72, 300 / 72)).irect
            reference = expected[rect.y0:rect.y1, rect.x0:rect.x1].astype(float)
            source_variation = reference.mean(axis=2).std()
            values = []
            for record in records:
                mode = record["mode"]
                with fitz.open(previous[mode]["pdf"]) as before, fitz.open(record["pdf"]) as after:
                    a = np.asarray(render(before[0], 300))[rect.y0:rect.y1, rect.x0:rect.x1].astype(float)
                    b = np.asarray(render(after[0], 300))[rect.y0:rect.y1, rect.x0:rect.x1].astype(float)
                bad_error, fixed_error = np.abs(a - reference).mean(), np.abs(b - reference).mean()
                variation = b.mean(axis=2).std()
                if not (fixed_error < bad_error / 2 and variation > source_variation / 2):
                    raise AssertionError(f"B116 artwork not restored: {mode}/{name}")
                values.append(dict(mode=mode, before_mean_absolute_error=bad_error,
                                   fixed_mean_absolute_error=fixed_error,
                                   source_spatial_std=source_variation, fixed_spatial_std=variation))
            checks.append(dict(region=name, points=box, checks=values))
            center = fitz.Rect(box).tl + (fitz.Rect(box).br - fitz.Rect(box).tl) / 2
            x, y = round(center.x * 300 / 72) - 128, round(center.y * 300 / 72) - 128
            for index, (label, view) in enumerate(zip(labels, views, strict=True)):
                left, top = 12 + index * 268, 12 + row * 290
                draw.text((left, top), f"{name}: {label}", fill="black")
                crops.paste(view.crop((x, y, x + 256, y + 256)), (left, top + 24))
        crops.save(folder / "crops-300dpi.png")
        return checks
    finally:
        for doc in (source, old, jpeg, jpx):
            doc.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(".tmp/b116-local-backgrounds-20261019"))
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    folder = args.output
    folder.mkdir(parents=True, exist_ok=args.resume)
    if lossy.file_digest(BEFORE) != BEFORE_SHA256:
        raise ValueError("Changed immutable pre-B116 baseline")
    document = next(d for d in lossy.DOCUMENTS if d.key == "photos")
    original = json.loads(BEFORE.read_text())
    previous = {r["mode"]: r for r in original["records"]
                if r["document"] == document.key and not r["force_raster"]}
    for record in previous.values():
        lossy.verify_record(record, rerender=False)
    current = dict(purpose="B116-local-backgrounds-v1", baseline_sha256=BEFORE_SHA256,
                   measurement=lossy.identity((document,)))
    identity_path = folder / "identity.json"
    if identity_path.exists() and json.loads(identity_path.read_text()) != current:
        raise ValueError("Changed B116 producer/input; cannot resume")
    identity_path.write_text(json.dumps(current, indent=2) + "\n")
    records = [lossy.measure(document, False, mode, folder / mode, current["measurement"],
                             resume=args.resume) for mode in lossy.MODES]
    lossy.verify_pair(*records)
    checks = review(folder, document, previous, records)
    if lossy.file_digest(BEFORE) != BEFORE_SHA256:
        raise ValueError("Historical evidence changed")
    (folder / "proof.json").write_text(json.dumps(dict(
        complete=True, identity=current, records=records, artwork=checks,
        scope="B116 repair validation, not perceptual-quality calibration or benchmark table publication"),
        indent=2) + "\n")
    print("B116 GREEN: two complete eight-page PDFs, exact native/geometry checks, "
          "all-page 72/300-DPI readback, restored emblem/photos and review captures", flush=True)


if __name__ == "__main__":
    main()
