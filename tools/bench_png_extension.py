"""Extend the six-PDF PNG A/B study without re-encoding compatible results.

Only PNG row prediction changes within a pair. All sizes are actual complete
PDFs made by the existing preparation and integrated-save implementations.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from importlib.metadata import version
import json
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import bench_compression_overview as overview

study = overview.study
VARIANTS = ("zopfli-plain", "zopfli-png", "brotli-plain", "brotli-png")

# The previous encoder differs only in an unused reporting field. This exact,
# bounded bridge is an explicit import, NOT permission to resume changed code.
OLD_METADATA = '''    baseline = row["results"][0]["complete_pdf_bytes"]
    for result in row["results"]:
        result["vs_current_flate_percent"] = round((result["complete_pdf_bytes"]/baseline-1)*100, 3)
'''
NEW_METADATA = '''    # A selected subset need not contain Classic Flate. Report actual complete
    # bytes; named paired comparisons belong to the publication, not an
    # implicit first-variant baseline mislabeled as Classic Flate.
'''


@dataclass(frozen=True)
class Job:
    document: str
    source: str
    mode: str
    colors: int

    @property
    def family(self):
        return f"{self.mode}-{self.colors}"

    @property
    def key(self):
        return f"{self.document}-{self.family}"


JOBS = tuple(Job(d.key, d.source, mode, count) for d in overview.DOCUMENTS
             for count in (16, 64) for mode in ("indexed", "indexed-ffpr"))


def extension_rows():
    rows = []
    for count in (16, 64):
        for mode in ("indexed", "indexed-ffpr"):
            label = f"Indexed {count} colors" if mode == "indexed" else f"Color FFPR; indexed {count} colors"
            for policy, name in (("zopfli", "Zopfli-Flate"), ("brotli", "Brotli")):
                for prediction in ("plain", "png"):
                    rows.append(overview.Combination(f"{mode}-{count}", f"{policy}-{prediction}", policy,
                        f"{label} + {name}" + (" + PNG prediction" if prediction == "png" else "")))
    return tuple(rows)


def publication_rows():
    families = ("preserve-images", "bw-images", "bw-ffpr", "indexed", "indexed-ffpr",
                "indexed-16", "indexed-ffpr-16", "indexed-64", "indexed-ffpr-64",
                "jpeg-q50", "jpx-r192", "jpx-lossless", "jpeg-q50-ffpr", "jpx-r192-ffpr", "jpx-lossless-ffpr")
    rows = overview.ROWS + extension_rows()
    return tuple(row for family in families for row in rows if row.family == family)


def toolchain():
    return dict(environment=study.environment(),
                implementation=overview.file_digest(__file__),
                overview_implementation=overview.file_digest(overview.__file__),
                packages={name: version(name) for name in ("PyMuPDF", "Pillow", "numpy")},
                binaries={name: dict(path=shutil.which(name), sha256=overview.file_digest(shutil.which(name)))
                          for name in ("zopfli", "jbig2", "qpdf")})


def compatible_implementation(previous, current, frozen_image_source):
    """Prove byte equality, except the exact removed, unused metadata block."""
    if set(previous) != set(current):
        raise ValueError("Changed implementation file scope")
    differences = [name for name in previous if previous[name] != current[name]]
    if not differences:
        return []
    name = "tools/bench_image_streams.py"
    if differences != [name] or study.digest(frozen_image_source.encode()) != previous[name]:
        raise ValueError("Changed historical encoding implementation")
    if frozen_image_source.count(OLD_METADATA) != 1:
        raise ValueError("Unknown historical metadata change")
    bridged = frozen_image_source.replace(OLD_METADATA, NEW_METADATA)
    if study.digest(bridged.encode()) != current[name]:
        raise ValueError("Historical change is not solely unused reporting metadata")
    return [dict(file=name, old_sha256=previous[name], current_sha256=current[name],
                 change="Remove unused first-variant vs_current_flate_percent field only")]


def import_history(path, current):
    """Import this explicit manifest, retaining the actual producing identity."""
    stored = json.loads(path.read_text())
    previous = stored["identity"]["measurement_identity"]
    frozen = path.parent.parent / "image-streams.py"
    bridge = compatible_implementation(previous["environment"]["implementation"],
                                      current["environment"]["implementation"], frozen.read_text())
    for field in ("packages", "binaries"):
        if previous[field] != current[field]:
            raise ValueError(f"Changed historical {field}")
    for field in ("python", "pymupdf", "zopfli"):
        if previous["environment"][field] != current["environment"][field]:
            raise ValueError(f"Changed historical environment: {field}")
    for source, expected in previous["source_hashes"].items():
        if overview.file_digest(source) != expected:
            raise ValueError(f"Changed historical source: {source}")
    for record in stored["records"] + stored["extras"]:
        overview.validate_record(record["case"], record["result"])
        origin = json.loads(Path(record["origin"]).read_text())
        if (origin["identity"]["environment"] != previous["environment"] or
                origin["identity"]["case"] != record["case"] or record["result"] not in origin["results"]):
            raise ValueError("Imported record has lost its producing provenance")
    proof = dict(manifest=str(path), manifest_sha256=overview.file_digest(path),
                 producing_identity=previous, metadata_bridge=bridge)
    return stored, proof


def matches_job(record, job):
    case = record["case"]
    return (case.get("source") == job.source and case.get("mode") == job.mode and
            case.get("dpi") == 300 and case.get("colors") == job.colors and
            case.get("recipe") == dict(mode=job.mode, dpi=300, colors=job.colors,
                                       threshold_method=None, threshold=None))


def imported_job(stored, job):
    selected = [r for r in stored["extras"] if matches_job(r, job) and
                r["result"]["image_variant"] in VARIANTS and
                r["result"]["native_policy"] == r["result"]["image_variant"].split("-")[0]]
    if not selected:
        return []
    if len(selected) != 4 or {r["result"]["image_variant"] for r in selected} != set(VARIANTS):
        raise ValueError("Incomplete historical PNG job")
    return [dict(document=job.document, family=job.family, case=r["case"], result=r["result"],
                 origin=r["origin"], imported_record=r) for r in selected]


def validate_job(job, records):
    if len(records) != 4 or {r["result"]["image_variant"] for r in records} != set(VARIANTS):
        raise ValueError("Incomplete four-output PNG job")
    for record in records:
        result = record["result"]
        if (record["document"] != job.document or record["family"] != job.family or
                not matches_job(record, job) or
                result["native_policy"] != result["image_variant"].split("-")[0]):
            raise ValueError("PNG job changes a fixed recipe or compressor")
        overview.validate_record(record["case"], result)
    rows = tuple(r for r in extension_rows() if r.family == job.family)
    document = overview.Document(job.document, job.document, job.source)
    overview.png_prediction_markdown((document,), rows, records)


def measure_job(job, folder, identity, imported=(), resume=False):
    folder = Path(folder)
    checkpoint = folder / "metrics.json"
    expected = dict(run=identity, job=asdict(job))
    if resume and checkpoint.exists():
        report = json.loads(checkpoint.read_text())
        if report["identity"] != expected:
            raise ValueError("Changed PNG job identity; use a new label")
        validate_job(job, report["records"])
        return report["records"]
    folder.mkdir(parents=True, exist_ok=resume)
    if imported:
        records = list(imported)
    else:
        preparation = folder / "prepared"
        raw = study.images.run_case(Path(job.source), preparation, mode=job.mode, dpi=300,
                                    colors=job.colors, variants=VARIANTS,
                                    resume=resume and preparation.exists())
        case = overview.bitmap_case(raw, job.key)
        records = []
        for variant in VARIANTS:
            policy = variant.split("-")[0]
            selected = dict(case, bases={variant: case["bases"][variant]})
            destination = folder / "outputs" / variant
            report = study.run_case(selected, destination, policies=(policy,),
                                    resume=resume and destination.exists())
            records.append(dict(document=job.document, family=job.family, case=selected,
                                result=report["results"][0], origin=str(destination / "metrics.json")))
    validate_job(job, records)
    checkpoint.write_text(json.dumps(dict(identity=expected, records=records), indent=2) + "\n")
    print(json.dumps(dict(completed=job.key, imported=bool(imported), outputs=len(records))), flush=True)
    return records


def run(folder, *, existing=None, resume=False, workers=3):
    if not 1 <= workers <= 3:
        raise ValueError("Use one to three isolated benchmark processes")
    current = toolchain()
    stored, proof = import_history(existing, current) if existing else ({"extras": []}, None)
    identity = dict(toolchain=current, documents=[asdict(d) for d in overview.DOCUMENTS],
                    jobs=[asdict(j) for j in JOBS], variants=list(VARIANTS), dpi=300,
                    sources={j.source: overview.file_digest(j.source) for j in JOBS}, imported=proof)
    folder.mkdir(parents=True, exist_ok=resume)
    frozen = folder / "identity.json"
    if frozen.exists():
        if not resume or json.loads(frozen.read_text()) != identity:
            raise ValueError("Changed PNG study identity; use a new label")
    else:
        frozen.write_text(json.dumps(identity, indent=2) + "\n")
        (folder / "implementation.py").write_bytes(Path(__file__).read_bytes())
    checkpoint = folder / "metrics.json"
    if resume and checkpoint.exists():
        previous = json.loads(checkpoint.read_text())
        if previous["identity"] != identity:
            raise ValueError("Changed PNG checkpoint identity")
        if previous["complete"]:
            for job in JOBS:
                validate_job(job, [r for r in previous["records"] if
                                  (r["document"], r["family"]) == (job.document, job.family)])
            if len(previous["records"]) != 4 * len(JOBS):
                raise ValueError("Unexpected records in completed PNG study")
            return previous["records"]
    by_job = {}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(measure_job, job, folder / "jobs" / job.key, identity,
                               imported_job(stored, job), resume): job for job in JOBS}
        for future in as_completed(futures):
            job = futures[future]
            by_job[job.key] = future.result()
            records = [r for j in JOBS for r in by_job.get(j.key, ())]
            checkpoint.write_text(json.dumps(dict(identity=identity, complete=len(by_job) == len(JOBS),
                                                  records=records), indent=2) + "\n")
    records = [r for job in JOBS for r in by_job[job.key]]
    (folder / "baseline.md").write_text(overview.matrix_markdown(
        overview.DOCUMENTS, overview.primary_rows(extension_rows()), records))
    (folder / "png-prediction.md").write_text(overview.png_prediction_markdown(
        overview.DOCUMENTS, extension_rows(), records))
    print(f"PNG EXTENSION COMPLETE: {len(records)} verified complete PDFs", flush=True)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True)
    parser.add_argument("--existing", type=Path, help="Explicit compatible frozen selected-study manifest")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    if Path(args.label).name != args.label or args.label in (".", ".."):
        parser.error("label must be one directory name")
    run(Path(".tmp/compression-experiments") / args.label, existing=args.existing,
        resume=args.resume, workers=args.workers)


if __name__ == "__main__":
    main()
