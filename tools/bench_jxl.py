"""JPEG XL binary experiment (TODO §§270/271, designer §§309–314). Analysis only.

No app filter or saved user PDF uses JPEG XL (docs/DROPPED.md D1). Steps:

calibrate  JPEG XL lossy settings on the 67 calibration page images, each
           scored with SSIMULACRA2 against JPEG q75 of the same original
           (the §284 method used for JPEG2000). Resumable JSON lines.
match      The JPEG rows' setting (§314): JPEG XL distances on the JPEG row's
           own photograph pages (Color photos, native), scored against JPEG
           q75 of the same originals. The chosen distance is the measured
           one with the smallest mean gap. Resumable JSON lines.
swap       Copies of measured baseline PDFs in which only the images the
           pipeline prepared are replaced by JPEG XL. Every other object
           stays byte for byte; a no-op resave of each baseline must
           reproduce it exactly, so the size change is the image change.

Treatments: BW and Indexed rows get JPEG XL lossless of the identical decoded
pixels. JPEG rows get JPEG XL encoded from the same original page image
(re-composed by the production composer and checked against the recorded
sample hashes), never from JPEG's output (§311). The filter name
`/JXLDecode` is a placeholder: no PDF reader opens these files.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import math
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from PIL import Image
import pymupdf as fitz

from pdf_minify.core import pipeline

Image.MAX_IMAGE_PIXELS = None

FILTER = "/JXLDecode"          # placeholder; ISO 32000 defines no JPEG XL filter yet
LOSSLESS_EFFORT = 10           # strongest standard lossless effort (§213)
# Whole-image lossy encoding (§315). Above 2048 pixels, cjxl's default at
# effort 7 below distance 3.0 encodes in chunks to save memory, "at the cost
# of compression density", and skips patches. cjxl has no flag for the
# whole-image path; forcing patches turns chunking off and is otherwise
# identical (byte-identical at distance 3.0, where whole-image is the
# default). Effort 10 lossless never uses chunks.
WHOLE_IMAGE = ("--patches=1",)
RESEARCH = Path(".tmp/jpeg-jpx-research")
CANVAS_ROOT = RESEARCH / "match-20261019"
REFERENCE = RESEARCH / "stock-vs-qfactor-20261020/results.jsonl"
REFERENCE_SHA256 = "9294f0f4a2150bc77140f4c1177e13ed561e2578215348606e74f1e72b32f1ef"
METRIC = RESEARCH / "metric/bin/ssimulacra2_rs"
OVERVIEW = Path(".tmp/compression-experiments/best-overview-300dpi-20261017/metrics.json")
OVERVIEW_SHA256 = "ab689814fe55f1d89e2020dee1028819a0d0b9047bd5e84c582441376168f153"
LOSSY = Path(".tmp/lossy-quality/q75-matched-20261020/metrics.json")
LOSSY_SHA256 = "69c190040942c681f3b3a466cd4dbdf038264eb1145fcbab7ea83be359b63b74"
DOCUMENTS = ("native", "scan", "photos", "art", "mixed", "kepler")

# (row ID in the page's table, baseline source, baseline recipe, FFPR, treatment)
ROWS = (
    ("bw-jbig2", "overview", "bw-jbig2", False, "lossless"),
    ("bw-ffpr-jbig2", "overview", "bw-ffpr-jbig2", True, "lossless"),
    ("indexed-5", "overview", "indexed-5", False, "lossless"),
    ("indexed-16", "overview", "indexed-16", False, "lossless"),
    ("indexed-64", "overview", "indexed-64", False, "lossless"),
    ("indexed-ffpr-5", "overview", "indexed-ffpr-5", True, "lossless"),
    ("indexed-ffpr-16", "overview", "indexed-ffpr-16", True, "lossless"),
    ("indexed-ffpr-64", "overview", "indexed-ffpr-64", True, "lossless"),
    ("jpeg", "lossy", "color", False, "lossy"),
    ("jpeg-ffpr", "lossy", "color", True, "lossy"),
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(cmd):
    subprocess.run([str(c) for c in cmd], check=True, capture_output=True)


def tool_versions():
    cjxl = subprocess.run(["cjxl", "--version"], capture_output=True, text=True).stdout.split("\n")[0]
    return dict(cjxl=cjxl.strip(), cjxl_path=shutil.which("cjxl"), djxl_path=shutil.which("djxl"),
                metric=str(METRIC), metric_sha256=file_digest(METRIC))


def encode_jxl(png, out, *, distance, effort, whole_image=False):
    """cjxl on a PNG; distance 0 is mathematically lossless."""
    run(["cjxl", png, out, "-d", repr(float(distance)), "-e", str(int(effort)), "--quiet",
         *(WHOLE_IMAGE if whole_image else ())])
    return Path(out).read_bytes()


def decode_jxl(jxl, png):
    run(["djxl", jxl, png, "--quiet"])
    with Image.open(png) as image:
        if image.mode not in ("L", "RGB"):
            image = image.convert("L" if image.mode in ("1", "I;16", "I") else "RGB")
        return np.asarray(image).copy()


def ssimulacra2(reference_png, decoded_png):
    out = subprocess.run([str(METRIC), "image", str(reference_png), str(decoded_png)],
                         check=True, capture_output=True, text=True).stdout
    return float(out.strip().split()[-1])


def psnr(a, b):
    mse = float(np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2))
    return math.inf if mse == 0 else 10 * math.log10(255 ** 2 / mse)


# ---------------------------------------------------------------- calibration

def calibration_canvases():
    """The 67 unique page images with a JPEG q75 reference (scan FFPR duplicates scan native)."""
    if file_digest(REFERENCE) != REFERENCE_SHA256:
        raise ValueError("Changed JPEG/JPEG2000 calibration results")
    rows = [json.loads(line) for line in REFERENCE.read_text().splitlines()]
    reference = {r["id"]: r for r in rows if r["family"] == "jpeg" and r["param"] == 75}
    canvases = [dict(id=i, doc=r["doc"], mode=r["mode"], path=str(CANVAS_ROOT / i / "original.png"),
                     jpeg_bytes=r["bytes"], jpeg_sha256=r["sha256"], jpeg_ssimulacra2=r["ssimulacra2"])
                for i, r in sorted(reference.items()) if not i.startswith("scan/ffpr/")]
    if len(canvases) != 67:
        raise ValueError(f"Expected 67 calibration page images, found {len(canvases)}")
    return canvases


def calibration_task(canvas, distance, effort, scratch):
    with tempfile.TemporaryDirectory(dir=scratch) as tmp:
        tmp = Path(tmp)
        with Image.open(canvas["path"]) as image:
            original = np.asarray(image.convert("RGB")).copy()
        if distance is None:
            # Reference check: the app's JPEG q75 encoder reproduces the recorded JPEG.
            data = pipeline.jpeg_encode(Image.fromarray(original), 75)
            if digest(data) != canvas["jpeg_sha256"] or len(data) != canvas["jpeg_bytes"]:
                raise ValueError(f"JPEG q75 reference differs for {canvas['id']}")
            return dict(id=canvas["id"], family="jpeg-check", ok=True)
        data = encode_jxl(canvas["path"], tmp / "c.jxl", distance=distance, effort=effort)
        decoded = decode_jxl(tmp / "c.jxl", tmp / "d.png")
        return dict(id=canvas["id"], doc=canvas["doc"], mode=canvas["mode"], family="jxl",
                    distance=float(distance), effort=int(effort), bytes=len(data), sha256=digest(data),
                    jpeg_bytes=canvas["jpeg_bytes"], jpeg_ssimulacra2=canvas["jpeg_ssimulacra2"],
                    ssimulacra2=ssimulacra2(canvas["path"], tmp / "d.png"), psnr=psnr(original, decoded))


def calibrate(args):
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    results = out / "results.jsonl"
    done = set()
    if results.exists():
        for line in results.read_text().splitlines():
            r = json.loads(line)
            done.add((r["id"], r["family"], r.get("distance"), r.get("effort")))
    identity = dict(study="JXL-CAL-01", reference=str(REFERENCE), reference_sha256=REFERENCE_SHA256,
                    tools=tool_versions())
    meta = out / "identity.json"
    if meta.exists() and json.loads(meta.read_text()) != identity:
        raise ValueError("Changed calibration identity; use a new output folder")
    meta.write_text(json.dumps(identity, indent=2) + "\n")
    canvases = calibration_canvases()
    tasks = [(c, None, None) for c in canvases if (c["id"], "jpeg-check", None, None) not in done]
    tasks += [(c, d, e) for e in args.effort for d in args.distance for c in canvases
              if (c["id"], "jxl", float(d), int(e)) not in done]
    scratch = out / "scratch"
    scratch.mkdir(exist_ok=True)
    with ProcessPoolExecutor(args.workers) as pool, results.open("a") as log:
        futures = [pool.submit(calibration_task, c, d, e, scratch) for c, d, e in tasks]
        for n, future in enumerate(as_completed(futures), 1):
            row = future.result()
            row.setdefault("distance", None)
            row.setdefault("effort", None)
            log.write(json.dumps(row) + "\n")
            log.flush()
            print(f"[{n}/{len(tasks)}] {json.dumps(row)}", flush=True)


def calibration_report(path):
    """Per effort and distance: gap statistics against JPEG q75 over the 67 images."""
    rows = [json.loads(line) for line in Path(path).read_text().splitlines()]
    checked = {r["id"] for r in rows if r["family"] == "jpeg-check" and r["ok"]}
    ids = {c["id"] for c in calibration_canvases()}
    if checked != ids:
        raise ValueError("Not every JPEG q75 reference was reproduced")
    groups = {}
    for r in rows:
        if r["family"] == "jxl":
            groups.setdefault((r["effort"], r["distance"]), {})[r["id"]] = r
    report = []
    for (effort, distance), by_id in sorted(groups.items()):
        if set(by_id) != ids:
            continue
        gaps = sorted(r["ssimulacra2"] - r["jpeg_ssimulacra2"] for r in by_id.values())
        deciles = statistics.quantiles(gaps, n=10, method="inclusive")
        report.append(dict(effort=effort, distance=distance, median_gap=statistics.median(gaps),
                           p10=deciles[0], p90=deciles[-1], worst=gaps[0],
                           within_5=sum(abs(g) <= 5 for g in gaps) / len(gaps),
                           bytes_vs_jpeg=sum(r["bytes"] for r in by_id.values())
                           / sum(r["jpeg_bytes"] for r in by_id.values()),
                           median_psnr=statistics.median(r["psnr"] for r in by_id.values())))
    return report


# ------------------------------------------------------- photo match (§314)

MATCH = ("jpeg", "photos")      # the brochure's photograph pages, native: the JPEG row's own images
MATCH_TOLERANCE = 0.5           # largest accepted mean SSIMULACRA2 gap at the chosen distance


def match_targets(out):
    """Write the target cell's originals and JPEG q75 images once, exactly as the swap scores them."""
    described = out / "images.json"
    if described.exists():
        return json.loads(described.read_text())
    entry = baseline_records({MATCH})[MATCH]
    folder, scratch = out / "images", out / "compose"
    folder.mkdir(parents=True, exist_ok=True)
    scratch.mkdir(exist_ok=True)
    targets = []
    with fitz.open(entry["pdf"]) as doc:
        canvases = original_canvases(entry, scratch)
        for xref in prepared_images(doc, MATCH[0], entry["record"]):
            raw = doc.xref_stream_raw(xref)
            original, jpeg = canvases[digest(raw)], pixels(doc, xref)
            png, jpeg_png = folder / f"{xref}.png", folder / f"{xref}-jpeg.png"
            Image.fromarray(original).save(png)
            Image.fromarray(jpeg).save(jpeg_png)
            targets.append(dict(xref=xref, original=str(png), samples_sha256=digest(original.tobytes()),
                                jpeg_bytes=len(raw), jpeg_sha256=digest(raw),
                                jpeg_ssimulacra2=ssimulacra2(png, jpeg_png), jpeg_psnr=psnr(original, jpeg)))
    shutil.rmtree(scratch)
    described.write_text(json.dumps(targets, indent=2) + "\n")
    return targets


def match_task(target, distance, effort, scratch):
    with tempfile.TemporaryDirectory(dir=scratch) as tmp:
        tmp = Path(tmp)
        data = encode_jxl(target["original"], tmp / "i.jxl", distance=distance, effort=effort, whole_image=True)
        decoded = decode_jxl(tmp / "i.jxl", tmp / "d.png")
        with Image.open(target["original"]) as image:
            original = np.asarray(image.convert("RGB")).copy()
        return dict(xref=target["xref"], distance=float(distance), effort=int(effort), bytes=len(data),
                    jxl_sha256=digest(data), ssimulacra2=ssimulacra2(target["original"], tmp / "d.png"),
                    psnr=psnr(original, decoded), jpeg_bytes=target["jpeg_bytes"],
                    jpeg_ssimulacra2=target["jpeg_ssimulacra2"], jpeg_psnr=target["jpeg_psnr"])


def match(args):
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    identity = dict(study="JXL-PHOTO-MATCH-01", row=MATCH[0], document=MATCH[1], lossy=str(LOSSY),
                    lossy_sha256=LOSSY_SHA256, whole_image=list(WHOLE_IMAGE), tools=tool_versions())
    meta = out / "identity.json"
    if meta.exists() and json.loads(meta.read_text()) != identity:
        raise ValueError("Changed photo-match identity; use a new output folder")
    meta.write_text(json.dumps(identity, indent=2) + "\n")
    targets = match_targets(out)
    results = out / "results.jsonl"
    done = set()
    if results.exists():
        done = {(r["xref"], r["distance"], r["effort"])
                for r in map(json.loads, results.read_text().splitlines())}
    tasks = [(t, d, e) for e in args.effort for d in args.distance for t in targets
             if (t["xref"], float(d), int(e)) not in done]
    scratch = out / "scratch"
    scratch.mkdir(exist_ok=True)
    with ProcessPoolExecutor(args.workers) as pool, results.open("a") as log:
        futures = [pool.submit(match_task, t, d, e, scratch) for t, d, e in tasks]
        for n, future in enumerate(as_completed(futures), 1):
            row = future.result()
            log.write(json.dumps(row) + "\n")
            log.flush()
            print(f"[{n}/{len(tasks)}] {json.dumps(row)}", flush=True)


def match_report(path):
    """Per effort and distance measured on every photograph page: the gap against JPEG q75."""
    path = Path(path)
    xrefs = {t["xref"] for t in json.loads((path.parent / "images.json").read_text())}
    groups = {}
    for r in map(json.loads, path.read_text().splitlines()):
        groups.setdefault((r["effort"], r["distance"]), {})[r["xref"]] = r
    report = []
    for (effort, distance), by_xref in sorted(groups.items()):
        if set(by_xref) != xrefs:
            continue
        gaps = [r["ssimulacra2"] - r["jpeg_ssimulacra2"] for r in by_xref.values()]
        report.append(dict(effort=effort, distance=distance, images=len(gaps),
                           mean_gap=statistics.fmean(gaps), median_gap=statistics.median(gaps),
                           worst=min(gaps), best=max(gaps),
                           bytes_vs_jpeg=sum(r["bytes"] for r in by_xref.values())
                           / sum(r["jpeg_bytes"] for r in by_xref.values()),
                           psnr_gap=statistics.fmean(r["psnr"] - r["jpeg_psnr"] for r in by_xref.values()),
                           jxl_sha256={str(x): r["jxl_sha256"] for x, r in sorted(by_xref.items())}))
    return report


def matched_setting(path):
    """The measured setting whose mean gap is closest to zero, within the tolerance."""
    report = match_report(path)
    if not report:
        raise ValueError("No distance was measured on every photograph page")
    chosen = min(report, key=lambda r: (abs(r["mean_gap"]), r["distance"]))
    if abs(chosen["mean_gap"]) > MATCH_TOLERANCE:
        raise ValueError(f"Closest mean gap {chosen['mean_gap']:+.2f}; measure finer distances")
    return chosen


# ----------------------------------------------------------------- the swap

def baseline_records(only=None):
    """(row, document) -> verified baseline record from the pinned measured manifests.

    `only`, a set of (row, document) keys, limits the lookup and the file checks.
    """
    if file_digest(OVERVIEW) != OVERVIEW_SHA256 or file_digest(LOSSY) != LOSSY_SHA256:
        raise ValueError("A pinned baseline manifest changed")
    overview = json.loads(OVERVIEW.read_text())["records"]
    lossy = json.loads(LOSSY.read_text())["records"]
    found = {}
    for row_id, source, recipe, force, treatment in ROWS:
        for document in DOCUMENTS:
            if only is not None and (row_id, document) not in only:
                continue
            if source == "overview":
                match = [r for r in overview if r["recipe"] == recipe and r["document"] == document]
                pdf = match[0]["result"]["pdf"] if len(match) == 1 else None
                sha = match[0]["result"]["pdf_sha256"] if len(match) == 1 else None
                size = match[0]["result"]["complete_pdf_bytes"] if len(match) == 1 else None
            else:
                match = [r for r in lossy if r["mode"] == recipe and r["document"] == document
                         and r["force_raster"] is force]
                pdf, sha = (match[0]["pdf"], match[0]["pdf_sha256"]) if len(match) == 1 else (None, None)
                size = match[0]["complete_pdf_bytes"] if len(match) == 1 else None
            if len(match) != 1:
                raise ValueError(f"Missing or duplicate baseline: {row_id} / {document}")
            if file_digest(pdf) != sha or Path(pdf).stat().st_size != size:
                raise ValueError(f"Changed baseline PDF: {pdf}")
            found[row_id, document] = dict(row=row_id, document=document, treatment=treatment,
                                           force_raster=force, pdf=pdf, pdf_sha256=sha,
                                           complete_pdf_bytes=size, record=match[0])
    return found


def prepared_images(doc, row_id, record):
    """Xrefs of the images the pipeline prepared; residual source resources stay."""
    xrefs = sorted({image[0] for page in doc for image in page.get_images(full=True)})
    if row_id.startswith("bw-"):
        return [x for x in xrefs if doc.xref_get_key(x, "Filter")[1] == "/JBIG2Decode"]
    if row_id.startswith("indexed-"):
        return [x for x in xrefs if doc.xref_get_key(x, "ColorSpace")[1].startswith("[/Indexed")]
    payloads = {c["payload_sha256"] for c in record["canvases"]}
    chosen = [x for x in xrefs if digest(doc.xref_stream_raw(x)) in payloads]
    if {digest(doc.xref_stream_raw(x)) for x in chosen} != payloads:
        raise ValueError("A recorded JPEG canvas is missing from the baseline")
    return chosen


def pixels(doc, xref):
    """Decoded samples exactly as a reader receives them (palette expanded)."""
    pix = fitz.Pixmap(doc, xref)
    if pix.alpha or pix.n not in (1, 3):
        raise ValueError("Unexpected prepared image layout")
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n).squeeze()


def original_canvases(entry, scratch):
    """Re-compose the JPEG baseline's original page images with the production composer.

    The final save is skipped; every canvas must match the recorded sample
    hash and re-encode to the recorded JPEG payload, so it is the very
    original JPEG was made from.
    """
    record = entry["record"]
    captured = []
    encoder = pipeline.color_canvas_payload

    def observe(img, *args, **kwargs):
        payload = encoder(img, *args, **kwargs)
        captured.append((np.asarray(img).copy(), digest(img.tobytes()), digest(payload["stream"])))
        return payload

    source = next(d["source"] for d in json.loads(LOSSY.read_text())["identity"]["documents"]
                  if d["key"] == entry["document"])
    with patch.object(pipeline, "color_canvas_payload", observe), \
            patch.object(pipeline, "_save_optimized_pdf", lambda *a, **k: None):
        pipeline.save_with_spec(source, str(scratch / "unused.pdf"),
                                {k: v for k, v in record["recipe"].items()}, workdir=str(scratch))
    expected = [(c["samples_sha256"], c["payload_sha256"]) for c in record["canvases"]]
    if [(s, p) for _, s, p in captured] != expected:
        raise ValueError(f"Re-composed canvases differ from the baseline: {entry['row']} / {entry['document']}")
    return {payload: array for array, _, payload in captured}


def swap(entry, folder, *, distance, effort):
    folder.mkdir(parents=True, exist_ok=True)
    checkpoint = folder / "metrics.json"
    job = dict(row=entry["row"], document=entry["document"], baseline=entry["pdf"],
               baseline_sha256=entry["pdf_sha256"], treatment=entry["treatment"],
               lossless_effort=LOSSLESS_EFFORT, lossy_distance=distance, lossy_effort=effort,
               lossy_whole_image=list(WHOLE_IMAGE), filter=FILTER)
    if checkpoint.exists():
        previous = json.loads(checkpoint.read_text())
        if previous["job"] == job and file_digest(previous["result"]["pdf"]) == previous["result"]["pdf_sha256"]:
            return previous["result"]
        raise ValueError(f"Changed or unverified existing result: {folder}")
    scratch = folder / "scratch"
    scratch.mkdir(exist_ok=True)
    output = folder / "jxl.pdf"
    baseline_bytes = Path(entry["pdf"]).read_bytes()
    with fitz.open(entry["pdf"]) as doc:
        pipeline._write_optimized_pdf(doc, str(scratch / "noop.pdf"), no_new_id=True)
    if (scratch / "noop.pdf").read_bytes() != baseline_bytes:
        raise ValueError("A no-op resave does not reproduce the baseline; the pair would not be clean")
    doc = fitz.open(entry["pdf"])
    try:
        xrefs = prepared_images(doc, entry["row"], entry["record"])
        canvases = original_canvases(entry, scratch) if entry["treatment"] == "lossy" else None
        images = []
        for xref in xrefs:
            baseline_raw = doc.xref_stream_raw(xref)
            png, jxl, back = scratch / f"{xref}.png", scratch / f"{xref}.jxl", scratch / f"{xref}-d.png"
            if entry["treatment"] == "lossless":
                samples = pixels(doc, xref)
                bilevel = samples.ndim == 2 and set(np.unique(samples).tolist()) <= {0, 255}
                image = Image.fromarray(samples)
                (image.convert("1") if bilevel else image).save(png)
                data = encode_jxl(png, jxl, distance=0, effort=LOSSLESS_EFFORT)
                if not np.array_equal(decode_jxl(jxl, back).squeeze(), samples):
                    raise ValueError("JPEG XL lossless did not decode to the identical pixels")
                quality = None
            else:
                original = canvases[digest(baseline_raw)]
                Image.fromarray(original).save(png)
                data = encode_jxl(png, jxl, distance=distance, effort=effort, whole_image=True)
                decoded = decode_jxl(jxl, back)
                jpeg_png = scratch / f"{xref}-jpeg.png"
                jpeg = pixels(doc, xref)
                Image.fromarray(jpeg).save(jpeg_png)
                quality = dict(jxl_ssimulacra2=ssimulacra2(png, back),
                               jpeg_ssimulacra2=ssimulacra2(png, jpeg_png),
                               jxl_psnr=psnr(original, decoded), jpeg_psnr=psnr(original, jpeg))
            images.append(dict(xref=xref, width=doc.xref_get_key(xref, "Width")[1],
                               height=doc.xref_get_key(xref, "Height")[1],
                               baseline_filter=doc.xref_get_key(xref, "Filter")[1],
                               baseline_bytes=len(baseline_raw), baseline_sha256=digest(baseline_raw),
                               jxl_bytes=len(data), jxl_sha256=digest(data), quality=quality))
            replace_image(doc, xref, data, rgb=entry["row"].startswith("indexed-"))
        pipeline._write_optimized_pdf(doc, str(output), no_new_id=True)
    finally:
        doc.close()
    check_only_images_changed(entry["pdf"], output, {i["xref"]: i["jxl_sha256"] for i in images})
    shutil.rmtree(scratch)
    size = output.stat().st_size
    result = dict(row=entry["row"], document=entry["document"], treatment=entry["treatment"],
                  baseline_pdf=entry["pdf"], baseline_sha256=entry["pdf_sha256"],
                  baseline_bytes=entry["complete_pdf_bytes"], pdf=str(output),
                  pdf_sha256=file_digest(output), complete_pdf_bytes=size,
                  change_percent=100 * (size - entry["complete_pdf_bytes"]) / entry["complete_pdf_bytes"],
                  images=images)
    checkpoint.write_text(json.dumps(dict(job=job, result=result), indent=2) + "\n")
    return result


def replace_image(doc, xref, data, *, rgb):
    """Same image dictionary with the JPEG XL payload and filter.

    /DecodeParms belongs to the old filter and is dropped. An Indexed image
    becomes /DeviceRGB 8-bit: its palette now lives in the JPEG XL stream.
    """
    values = {k: doc.xref_get_key(xref, k)[1] for k in doc.xref_get_keys(xref)
              if k not in ("Length", "Filter", "DecodeParms")}
    if rgb:
        values.update(ColorSpace="/DeviceRGB", BitsPerComponent="8")
    doc.update_object(xref, "<<" + "".join(f"/{k} {v}" for k, v in values.items()) + ">>")
    doc.update_stream(xref, data, compress=False)
    doc.xref_set_key(xref, "Filter", FILTER)


def check_only_images_changed(baseline, treatment, swapped):
    """Every object except the swapped image XObjects is byte-identical."""
    with fitz.open(baseline) as a, fitz.open(treatment) as b:
        if a.xref_length() != b.xref_length() or a.page_count != b.page_count:
            raise ValueError("The swap changed the object or page structure")
        for xref in range(1, a.xref_length()):
            if xref in swapped:
                if (digest(b.xref_stream_raw(xref)) != swapped[xref]
                        or b.xref_get_key(xref, "Filter")[1] != FILTER):
                    raise ValueError("Swapped image object is not the JPEG XL payload")
                continue
            if a.xref_object(xref, compressed=True) != b.xref_object(xref, compressed=True):
                raise ValueError(f"Object {xref} changed outside the images")
            if a.xref_get_key(xref, "Type")[1] == "/XRef":
                continue  # its dictionary matched; its data is the byte offsets
            if a.xref_is_stream(xref) and a.xref_stream_raw(xref) != b.xref_stream_raw(xref):
                raise ValueError(f"Stream {xref} changed outside the images")


def run_swaps(args):
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    rows = sorted(args.rows or [r[0] for r in ROWS])
    identity = dict(study="JXL-SWAP-01", rows=rows, overview=str(OVERVIEW), overview_sha256=OVERVIEW_SHA256,
                    lossy=str(LOSSY), lossy_sha256=LOSSY_SHA256, filter=FILTER,
                    lossless_effort=LOSSLESS_EFFORT, lossy_distance=args.distance,
                    lossy_effort=args.effort, lossy_whole_image=list(WHOLE_IMAGE), tools=tool_versions(),
                    benchmark_sha256=file_digest(__file__))
    meta = out / "identity.json"
    if meta.exists() and json.loads(meta.read_text()) != identity:
        raise ValueError("Changed swap identity; use a new output folder")
    meta.write_text(json.dumps(identity, indent=2) + "\n")
    entries = baseline_records()
    wanted = [k for k in entries if k[0] in rows]
    if any(entries[k]["treatment"] == "lossy" for k in wanted) and args.distance is None:
        raise ValueError("The JPEG rows need the calibrated --distance and --effort")
    results = []
    with ProcessPoolExecutor(args.workers) as pool:
        futures = {pool.submit(swap, entries[k], out / k[1] / k[0],
                               distance=args.distance, effort=args.effort): k for k in wanted}
        for future in as_completed(futures):
            r = future.result()
            results.append(r)
            print(json.dumps({k: r[k] for k in ("row", "document", "baseline_bytes",
                                               "complete_pdf_bytes", "change_percent")}), flush=True)
    manifest = dict(identity=identity, complete=len(results) == len(wanted),
                    records=sorted(results, key=lambda r: (r["row"], r["document"])))
    (out / "metrics.json").write_text(json.dumps(manifest, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    cal = sub.add_parser("calibrate")
    cal.add_argument("--output", required=True)
    cal.add_argument("--distance", type=float, nargs="+", required=True)
    cal.add_argument("--effort", type=int, nargs="+", required=True)
    cal.add_argument("--workers", type=int, default=3)
    rep = sub.add_parser("report")
    rep.add_argument("results")
    mat = sub.add_parser("match")
    mat.add_argument("--output", required=True)
    mat.add_argument("--distance", type=float, nargs="+", required=True)
    mat.add_argument("--effort", type=int, nargs="+", default=[7])
    mat.add_argument("--workers", type=int, default=2)
    mrep = sub.add_parser("match-report")
    mrep.add_argument("results")
    sw = sub.add_parser("swap")
    sw.add_argument("--output", required=True)
    sw.add_argument("--rows", nargs="*")
    sw.add_argument("--distance", type=float)
    sw.add_argument("--effort", type=int)
    sw.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    if args.command == "calibrate":
        calibrate(args)
    elif args.command == "report":
        for row in calibration_report(args.results):
            print(json.dumps(row))
    elif args.command == "match":
        match(args)
    elif args.command == "match-report":
        for row in match_report(args.results):
            print(json.dumps({k: v for k, v in row.items() if k != "jxl_sha256"}))
    else:
        run_swaps(args)


if __name__ == "__main__":
    main()
