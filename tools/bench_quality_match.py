"""LOSSY-04: actual stable-q JPEG2000 matching to JPEG q75, not size targeting.

Research-only SSIMULACRA2 executable is explicit, pinned by hash and never a
runtime dependency. Prepare RGB once; search fixed integer q on those pixels.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from PIL import Image, __version__ as pillow_version, features

from pdf_minify.core import pipeline
from tools import bench_compression_overview as overview

DOCUMENTS = overview.DOCUMENTS
DPI = 300
JPEG_QUALITY = 75
SCALE = "darktable-rate-v1"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def conventional_rate(q):
    if type(q) is not int or not 0 <= q <= 100:
        raise ValueError("Expected actual integer JPEG2000 q in 0..100")
    return 101 - q


def metric_score(executable, source, decoded):
    result = subprocess.run([str(executable), "image", str(source), str(decoded)],
                            check=True, capture_output=True, text=True,
                            env=dict(os.environ, RAYON_NUM_THREADS="1"), timeout=600)
    match = re.fullmatch(r"Score: (-?\d+(?:\.\d+)?)\s*", result.stdout)
    if not match or not math.isfinite(float(match[1])):
        raise ValueError("Missing/invalid SSIMULACRA2 result; no metric fallback")
    return float(match[1])


def psnr(source, decoded):
    error = np.asarray(source, dtype=np.float32) - np.asarray(decoded, dtype=np.float32)
    mse = float(np.mean(error * error, dtype=np.float64))
    return None if mse == 0 else 10 * math.log10(255**2 / mse)


def identity(metric, documents):
    return dict(study="LOSSY-04-stable-q-visual-match-v1", dpi=DPI, jpeg_q=JPEG_QUALITY,
                jpx_quality_scale=SCALE, ssimulacra2_binary=str(metric),
                ssimulacra2_sha256=file_digest(metric),
                documents=[dict(asdict(d), sha256=file_digest(d.source)) for d in documents],
                producing_pipeline=overview.study.environment(),
                driver_sha256=file_digest(__file__), pillow=pillow_version,
                libjpeg_turbo=features.version_feature("libjpeg_turbo"),
                openjpeg=features.version_codec("jpg_2000"),
                matching="nearest measured SSIMULACRA2 on the fixed integer q scale",
                diagnostic="RGB PSNR; null means exact equality", colour_assumption="prepared RGB is sRGB")


def verify_files(records):
    for row in records:
        for field in ("source_png", "jpeg", "jpeg_decoded_png"):
            if file_digest(row[field]) != row[field + "_sha256"]:
                raise ValueError(f"Changed measured source/reference: {row[field]}")


def prepare_case(document, force, folder, current, resume):
    folder.mkdir(parents=True, exist_ok=resume)
    manifest = folder / "prepared.json"
    job = dict(identity=current, document=asdict(document), force_raster=force)
    if manifest.exists():
        previous = json.loads(manifest.read_text())
        if not resume or previous["job"] != job:
            raise ValueError("Changed preparation identity")
        verify_files(previous["canvases"])
        if file_digest(previous["reference_pdf"]) != previous["reference_pdf_sha256"]:
            raise ValueError("Changed actual JPEG reference PDF")
        return previous
    observed = []
    encoder = pipeline.color_canvas_payload

    def observe(img, *args, **kwargs):
        if img.mode != "RGB":
            raise ValueError("Expected the fixed full-colour RGB preparation")
        payload = encoder(img, *args, **kwargs)
        if payload["filter"] != "/DCTDecode":
            raise ValueError("Preparation must use the real JPEG q75 reference")
        page_folder = folder / f"canvas-{len(observed):02d}"
        page_folder.mkdir()
        source, jpeg, decoded = (page_folder / name for name in ("original.png", "reference.jpg", "reference-decoded.png"))
        img.save(source)
        jpeg.write_bytes(payload["stream"])
        Image.open(io.BytesIO(payload["stream"])).convert("RGB").save(decoded)
        row = dict(document=document.key, force_raster=force, canvas=len(observed),
                   width=img.width, height=img.height, samples_sha256=digest(img.tobytes()),
                   source_png=str(source), jpeg=str(jpeg), jpeg_decoded_png=str(decoded),
                   jpeg_bytes=len(payload["stream"]), jpeg_q=JPEG_QUALITY)
        for field in ("source_png", "jpeg", "jpeg_decoded_png"):
            row[field + "_sha256"] = file_digest(row[field])
        observed.append(row)
        return payload

    output = folder / "jpeg-reference.pdf"
    spec = dict(mode="color", jpeg_q=JPEG_QUALITY, dpi_cap=DPI, force_raster=force,
                stream_compression="best", brotli_declaration=False)
    with patch.object(pipeline, "color_canvas_payload", observe):
        pipeline.save_with_spec(document.source, str(output), spec, workdir=str(folder))
    # Exact producing native/geometry and every-page display readback, not an
    # assertion that the two lossy codecs reconstruct identical pixels.
    with overview.study.fitz.open(output) as saved:
        pages = [overview.study.images.page_signature(p, DPI) for p in saved]
    result = dict(job=job, reference_pdf=str(output), reference_pdf_sha256=file_digest(output),
                  reference_pdf_bytes=output.stat().st_size, pages=pages, canvases=observed)
    write_json(manifest, result)
    print(f"PREPARED {document.key} {'FFPR' if force else 'native'}: {len(observed)} original RGB canvases", flush=True)
    return result


def search_integer_quality(evaluate, reference):
    """Bracket/refine measured quality, evaluating adjacent integer endpoints.

    Each evaluated point is retained; mild non-monotonicity cannot discard a
    better observed candidate. Endpoint failures are explicit, never clamped
    into a claimed match. This is a practical search, not exhaustive q0..100.
    """
    seen = {}

    def sample(q):
        if q not in seen:
            seen[q] = evaluate(q)
        return seen[q]

    low, high = 0, 100
    sample(75)
    if sample(75)["ssimulacra2"] >= reference:
        high = 75
    else:
        low = 75
    sample(low)
    sample(high)
    bracketed = sample(low)["ssimulacra2"] <= reference <= sample(high)["ssimulacra2"]
    if bracketed:
        while high - low > 1:
            middle = (low + high) // 2
            if sample(middle)["ssimulacra2"] < reference:
                low = middle
            else:
                high = middle
    best_q = min(seen, key=lambda q: (abs(seen[q]["ssimulacra2"] - reference), seen[q]["bytes"], q))
    # Check local neighbours even if measured scores are mildly non-monotone.
    for q in (best_q - 1, best_q + 1):
        if 0 <= q <= 100:
            sample(q)
    best_q = min(seen, key=lambda q: (abs(seen[q]["ssimulacra2"] - reference), seen[q]["bytes"], q))
    return dict(selected_q=best_q, selected=seen[best_q], bracketed=bracketed,
                within_one_point=abs(seen[best_q]["ssimulacra2"] - reference) <= 1,
                measured_qs=sorted(seen))


def match_canvas(row, metric, current):
    verify_files([row])
    source_path = Path(row["source_png"])
    folder = source_path.parent
    checkpoint = folder / "quality-match.json"
    job = dict(identity=current, canvas=row)
    if checkpoint.exists():
        result = json.loads(checkpoint.read_text())
        if result["job"] != job:
            raise ValueError("Changed quality matching identity/source")
    else:
        result = dict(job=job, complete=False, candidates={})
    with Image.open(source_path) as original:
        source = original.convert("RGB")
    if digest(source.tobytes()) != row["samples_sha256"]:
        raise ValueError("Changed original RGB samples")
    if "reference_score" not in result:
        result["reference_score"] = metric_score(metric, source_path, row["jpeg_decoded_png"])
        with Image.open(row["jpeg_decoded_png"]) as decoded:
            result["reference_psnr"] = psnr(source, decoded)
        write_json(checkpoint, result)

    def evaluate(q):
        old = result["candidates"].get(str(q))
        if old:
            for field in ("jp2", "decoded_png"):
                if file_digest(old[field]) != old[field + "_sha256"]:
                    raise ValueError("Changed measured JPEG2000 candidate")
            return old
        jp2, decoded_path = folder / f"q{q:03d}.jp2", folder / f"q{q:03d}-decoded.png"
        data = pipeline.jpx_encode(np.asarray(source), None, rate=conventional_rate(q), presized=True)
        jp2.write_bytes(data)
        with Image.open(io.BytesIO(data)) as decoded:
            rgb = decoded.convert("RGB")
        if rgb.size != source.size:
            raise ValueError("JPEG2000 changed prepared image dimensions")
        rgb.save(decoded_path)
        measured = dict(q=q, rate=conventional_rate(q), bytes=len(data), jp2=str(jp2),
                        jp2_sha256=digest(data), decoded_png=str(decoded_path),
                        decoded_png_sha256=file_digest(decoded_path), psnr=psnr(source, rgb),
                        ssimulacra2=metric_score(metric, source_path, decoded_path))
        result["candidates"][str(q)] = measured
        write_json(checkpoint, result)
        return measured

    match = search_integer_quality(evaluate, result["reference_score"])
    result.update(match, complete=True)
    write_json(checkpoint, result)
    gap = match["selected"]["ssimulacra2"] - result["reference_score"]
    print(f"MATCH {row['document']} {'FFPR' if row['force_raster'] else 'native'} canvas {row['canvas']}: "
          f"JPEG q75 {result['reference_score']:.3f}; JPX q{match['selected_q']} "
          f"{match['selected']['ssimulacra2']:.3f}; gap {gap:+.3f}", flush=True)
    return result


def run(folder, metric, *, workers=2, resume=False, phase="all", first=False, documents=DOCUMENTS):
    if not 1 <= workers <= 2:
        raise ValueError("Use one or two bounded research workers")
    current = identity(metric, documents)
    folder.mkdir(parents=True, exist_ok=resume)
    manifest = folder / "identity.json"
    if manifest.exists() and json.loads(manifest.read_text()) != current:
        raise ValueError("Changed research identity; use a fresh output directory")
    write_json(manifest, current)
    preparations = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(prepare_case, d, force, folder / d.key / ("ffpr" if force else "native"), current, resume)
                   for d in documents for force in (False, True)]
        for future in as_completed(futures):
            preparations.append(future.result())
    preparations.sort(key=lambda r: (r["job"]["document"]["key"], r["job"]["force_raster"]))
    write_json(folder / "preparations.json", dict(identity=current, complete=True, cases=preparations))
    if phase == "prepare":
        return
    canvases = [c for case in preparations for c in (case["canvases"][:1] if first else case["canvases"])]
    results = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for future in as_completed([pool.submit(match_canvas, r, metric, current) for r in canvases]):
            results.append(future.result())
            write_json(folder / "matches.json", dict(identity=current, complete=False, first_canvas_only=first, records=results))
    results.sort(key=lambda r: (r["job"]["canvas"]["document"], r["job"]["canvas"]["force_raster"], r["job"]["canvas"]["canvas"]))
    write_json(folder / "matches.json", dict(identity=current, complete=True, first_canvas_only=first, records=results))
    print(f"LOSSY-04 COMPLETE: {len(results)} measured canvas matches; "
          f"{sum(r['within_one_point'] for r in results)} within one SSIMULACRA2 point", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--metric", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--phase", choices=("all", "prepare"), default="all")
    parser.add_argument("--first-canvas-only", action="store_true")
    args = parser.parse_args()
    run(args.output, args.metric, workers=args.workers, resume=args.resume,
        phase=args.phase, first=args.first_canvas_only)


if __name__ == "__main__":
    main()
