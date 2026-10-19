"""LOSSY-03: save only missing fixed-stream controls of verified q75 PDFs.

No image preparation/encoding, size estimates, timing rankings or CSV.
The completed LOSSY-02 study is the sole image-preparation input (§268).
"""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import bench_lossy_quality as lossy
from tools import publish_lossy_quality as publication

overview, study = lossy.overview, lossy.overview.study
BASELINE = Path(".tmp/lossy-quality/q75-jpeg-reference-20261019/metrics.json")


def family(mode, force):
    if mode not in lossy.MODES or type(force) is not bool:
        raise ValueError("Expected JPEG/JPEG2000 and boolean FFPR")
    return ("jpeg-q75" if mode == "color" else "jpx-q75") + ("-ffpr" if force else "")


def combination(mode, force, policy):
    if policy not in ("zopfli", "brotli", "flate") or (not force and policy == "flate"):
        raise ValueError("Unsupported current lossy control")
    variant = family(mode, force)
    label = ("Color FFPR + " if force else "") + ("JPEG q75" if mode == "color" else "JPEG2000 q75")
    if force:
        label += ("; optimized residual streams" if policy == "zopfli" else
                  f" + {'Brotli' if policy == 'brotli' else 'Classic Flate (reference)'} residual streams")
    else:
        label += f" + {'Zopfli' if policy == 'zopfli' else 'Brotli'} native"
    return overview.Combination(variant, variant, policy, label)


def load_baseline(path, documents=lossy.DOCUMENTS):
    data = json.loads(path.read_text())
    if not data.get("complete") or data["identity"] != lossy.identity(documents):
        raise ValueError("Incomplete or changed current lossy baseline")
    if tuple(documents) == lossy.DOCUMENTS:
        pinned = json.loads(publication.FIXTURE.read_text())
        if (str(path) != pinned["measured_manifest"] or lossy.file_digest(path) != pinned["measured_manifest_sha256"]):
            raise ValueError("Current lossy baseline differs from its verified publication")
    for row in data["records"]:
        lossy.verify_record(row, rerender=False)
    lossy.table(documents, data["records"])  # exact inventory and prepared/reference pairs
    return data


def prepared_case(document, row, baseline_sha256, source_sha256):
    spec = {k: v for k, v in row["recipe"].items() if k not in ("stream_compression", "brotli_declaration")}
    variant = family(row["mode"], row["force_raster"])
    return dict(id=f"{document.key}.{variant}.300dpi", family="production",
                source=document.source, input_sha256=source_sha256,
                mode=row["mode"], dpi=300, recipe=spec,
                prepared=dict(study="LOSSY-02", baseline_sha256=baseline_sha256,
                              prepared_pdf_sha256=row["pdf_sha256"],
                              jpx_quality_mapping=lossy.quality.JPX_QUALITY_MAPPING),
                bases={variant: dict(pdf=row["pdf"], sha256=row["pdf_sha256"])})


def measure(document, row, folder, identity, resume=False):
    source_hash = next(d["source_sha256"] for d in identity["producing_baseline_identity"]["documents"]
                       if d["key"] == document.key)
    case = prepared_case(document, row, identity["baseline_sha256"], source_hash)
    policies = ("zopfli", "brotli", "flate") if row["force_raster"] else ("zopfli", "brotli")
    # Shared production writer, font subsetting already completed. This path
    # repacks native streams only, holds every image stream byte-for-byte and
    # compares every actual output page with the completed preparation.
    report = study.run_case(case, folder, policies=policies, resume=resume)
    records = []
    for result in report["results"]:
        overview.validate_record(case, result)
        records.append(dict(document=document.key, mode=row["mode"], force_raster=row["force_raster"],
                            family=family(row["mode"], row["force_raster"]), case=case,
                            result=result, origin=str(folder / "metrics.json")))
    return records


def validate_inventory(documents, records):
    expected = {(d.key, family(mode, force), policy) for d in documents for mode in lossy.MODES
                for force in (False, True) for policy in (("zopfli", "brotli", "flate") if force else ("zopfli", "brotli"))}
    keys = [(r["document"], r["family"], r["result"]["native_policy"]) for r in records]
    if len(keys) != len(set(keys)) or set(keys) != expected:
        raise ValueError("Missing, duplicate or unexpected current lossy control")
    if len({r["result"]["pdf"] for r in records}) != len(records):
        raise ValueError("Aliased lossy controls")
    for row in records:
        result = row["result"]
        variant = family(row["mode"], row["force_raster"])
        spec = lossy.recipe(row["mode"], row["force_raster"])
        spec = {k: v for k, v in spec.items() if k not in ("stream_compression", "brotli_declaration")}
        if (row["family"] != variant or result["image_variant"] != variant
                or row["case"]["recipe"] != spec or result["brotli_declaration"]):
            raise ValueError("Mislabeled current-standard lossy control")
        overview.validate_record(row["case"], result)


def run(folder, baseline=BASELINE, *, documents=lossy.DOCUMENTS, workers=2, resume=False):
    if not 1 <= workers <= 3:
        raise ValueError("Use one to three isolated benchmark workers")
    source = load_baseline(baseline, documents)
    identity = dict(study="LOSSY-03-current-stream-controls-v1", baseline=str(baseline),
                    baseline_sha256=lossy.file_digest(baseline),
                    producing_baseline_identity=source["identity"], environment=study.environment(),
                    implementation_sha256=lossy.file_digest(__file__),
                    documents=[asdict(d) for d in documents], dpi=300, quality=75,
                    jpx_quality_mapping=lossy.quality.JPX_QUALITY_MAPPING,
                    brotli_declaration=False, factor="native/residual stream encoder only")
    folder.mkdir(parents=True, exist_ok=resume)
    frozen = folder / "identity.json"
    if frozen.exists() and (not resume or json.loads(frozen.read_text()) != identity):
        raise ValueError("Changed lossy control identity; incompatible resume")
    frozen.write_text(json.dumps(identity, indent=2) + "\n")
    index = {d.key: d for d in documents}
    records = []
    checkpoint = folder / "metrics.json"

    def complete(measured):
        records.extend(measured)
        checkpoint.write_text(json.dumps(dict(identity=identity, complete=False, records=records), indent=2) + "\n")

    jobs = [(index[r["document"]], r, folder / "outputs" / r["document"] / family(r["mode"], r["force_raster"]),
             identity, resume) for r in source["records"]]
    if workers == 1:
        for job in jobs:
            complete(measure(*job))
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for future in as_completed([pool.submit(measure, *job) for job in jobs]):
                complete(future.result())
    validate_inventory(documents, records)
    records.sort(key=lambda r: (r["document"], r["family"], r["result"]["native_policy"]))
    checkpoint.write_text(json.dumps(dict(identity=identity, complete=True, records=records), indent=2) + "\n")
    print(f"LOSSY-03 COMPLETE: {len(records)} verified complete PDFs; no image re-encoding", flush=True)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    run(args.output, args.baseline, workers=args.workers, resume=args.resume)


if __name__ == "__main__":
    main()
