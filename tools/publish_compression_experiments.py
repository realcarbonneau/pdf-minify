"""Publish verified PNG/NATIVE-01 measurements into the benchmark tables.

Does not encode PDFs or edit documentation directly. Fills only the measured
value cells of the `png-effect`, `residual-reference` and `residual-effect`
tables by table/row ID; prose, labels and row selection are curated by hand.
Emits an apply_patch patch on request, and freezes its input manifests,
output and validation proof.
"""

import argparse
from collections import Counter
from dataclasses import asdict
import difflib
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import bench_residual_streams as residual
from tools import benchmark_tables as tables
from tools.publish_best_overview import fixed_row_id

shared, overview = residual.shared, residual.overview


def cells(line):
    return [cell.strip() for cell in line.split("|")[1:-1]]


def pair_summary(pairs):
    changes = [candidate - baseline for baseline, candidate in pairs]
    return dict(smaller=sum(n < 0 for n in changes), tied=sum(n == 0 for n in changes),
                larger=sum(n > 0 for n in changes), min_byte_change=min(changes), max_byte_change=max(changes))


def png_summary(rows, records):
    indexed = {(r["document"], r["family"], r["result"]["image_variant"], r["result"]["native_policy"]):
               r["result"]["complete_pdf_bytes"] for r in records}
    return {policy: pair_summary([
        (indexed[(d.key, a.family, a.variant, a.native)], indexed[(d.key, b.family, b.variant, b.native)])
        for a, b in overview.png_pairs(rows) if a.native == policy for d in overview.DOCUMENTS])
        for policy in ("zopfli", "brotli")}


def fixed_stream_signature(path, kind):
    """Direct pair proof, without re-rendering already verified page pixels."""
    streams = Counter()
    with shared.study.fitz.open(path) as doc:
        xrefs = (shared.study.streams.native_stream_xrefs(doc) if kind == "native" else
                 (x for x in range(1, doc.xref_length()) if doc.xref_is_stream(x) and
                  doc.xref_get_key(x, "Subtype")[1] == "/Image"))
        for xref in xrefs:
            properties = tuple(shared.study.canonical_value(doc, doc.xref_get_key(xref, key)[1])
                               for key in ("Filter", "DecodeParms", "Width", "Height", "BitsPerComponent",
                                           "ColorSpace", "ImageMask", "Interpolate", "Decode"))
            streams[(shared.study.digest(doc.xref_stream_raw(xref)), properties)] += 1
    return sorted((repr(key), count) for key, count in streams.items())


def verify_fixed_pair_streams(rows, records, native_pairs):
    indexed = {(r["document"], r["family"], r["result"]["image_variant"], r["result"]["native_policy"]): r
               for r in records}
    signatures = {}
    def signature(record, kind):
        path = record["result"]["pdf"]
        key = (path, kind)
        if key not in signatures:
            signatures[key] = fixed_stream_signature(path, kind)
        return signatures[key]
    png_count = 0
    for a, b in overview.png_pairs(rows):
        for document in overview.DOCUMENTS:
            pair = [indexed[(document.key, r.family, r.variant, r.native)] for r in (a, b)]
            if signature(pair[0], "native") != signature(pair[1], "native"):
                raise ValueError("PNG pair changed encoded native streams")
            png_count += 1
    for pair in native_pairs:
        if signature(pair["reference"], "images") != signature(pair["candidate"], "images"):
            raise ValueError("Native A/B pair changed encoded image streams")
    return dict(png_native_streams_equal=png_count, native_encoded_images_equal=len(native_pairs))


def qpdf_checks(records, old_evidence, folder):
    """Reuse pinned syntax evidence; check only newly measured ordinary PDFs."""
    prior = {r["pdf"]: r for r in json.loads(old_evidence.read_text())["results"]}
    cache_path = folder / "qpdf.json"
    cached = json.loads(cache_path.read_text())["results"] if cache_path.exists() else []
    cached = {r["pdf"]: r for r in cached}
    outputs, unsupported = [], []
    for record in records:
        result, path = record["result"], record["result"]["pdf"]
        if result["native_policy"] == "brotli":
            unsupported.append(path)
            continue
        known = cached.get(path)
        if known and known["sha256"] != result["pdf_sha256"]:
            raise ValueError("Changed qpdf evidence artifact")
        if known:
            outputs.append(known)
        elif path in prior:
            outputs.append(dict(pdf=path, sha256=result["pdf_sha256"], reused=str(old_evidence),
                                output=prior[path]["output"]))
        else:
            run = subprocess.run(["qpdf", "--check", path], capture_output=True, text=True)
            if run.returncode:
                raise RuntimeError(f"qpdf rejected {path}: {run.stdout}{run.stderr}")
            outputs.append(dict(pdf=path, sha256=result["pdf_sha256"], reused=False,
                                output=run.stdout + run.stderr))
    report = dict(checked=len(outputs), unsupported=len(unsupported), results=outputs,
                  unsupported_pdfs=unsupported, old_evidence=str(old_evidence),
                  old_evidence_sha256=overview.file_digest(old_evidence))
    cache_path.write_text(json.dumps(report, indent=2) + "\n")
    return report


def table_values(rows, records, native_pairs):
    """Measured cells of the PNG-effect and NATIVE-01 tables by table/row ID."""
    png = overview.png_prediction_markdown(overview.DOCUMENTS, rows, records)
    png_ids = [fixed_row_id(plain.family, plain.variant, plain.native) for plain, _ in overview.png_pairs(rows)]
    reference, effects = residual.tables(overview.DOCUMENTS, residual.ROWS, native_pairs)
    residual_ids = [fixed_row_id(r.family, r.variant, r.native) for r in residual.ROWS]
    return {"png-effect": tables.keyed_rows(png, png_ids),
            "residual-reference": tables.keyed_rows(reference, residual_ids),
            "residual-effect": tables.keyed_rows(effects, residual_ids)}


def publish(before, old_path, png_path, native_path, folder):
    current = shared.toolchain()
    old, proof = shared.import_history(old_path, current)
    png, native = (json.loads(path.read_text()) for path in (png_path, native_path))
    for study in (png, native):
        if not study["complete"] or study["identity"]["toolchain"] != current:
            raise ValueError("Incomplete or changed experiment implementation")
    if native["identity"]["implementation"] != overview.file_digest(residual.__file__):
        raise ValueError("Changed native experiment implementation")
    if png["identity"]["imported"] != proof or native["identity"]["imported"] != proof:
        raise ValueError("Changed imported study provenance")
    for job in shared.JOBS:
        shared.validate_job(job, [r for r in png["records"] if
                                 (r["document"], r["family"]) == (job.document, job.family)])
    if len(png["records"]) != len(shared.JOBS) * 4:
        raise ValueError("Unexpected PNG measurement inventory")
    rows, records = shared.publication_rows(), old["records"] + png["records"]
    # Every plain baseline cell must be an actual measurement (raises otherwise).
    overview.matrix_markdown(overview.DOCUMENTS, overview.primary_rows(rows), records)
    if len(native["pairs"]) != len(residual.ROWS) * len(overview.DOCUMENTS):
        raise ValueError("Unexpected native A/B measurement inventory")
    values = table_values(rows, records, native["pairs"])
    by_path = {}
    for record in records + old["extras"] + [p[k] for p in native["pairs"] for k in ("reference", "candidate")]:
        overview.validate_record(record["case"], record["result"])
        path = record["result"]["pdf"]
        if path in by_path and by_path[path]["result"] != record["result"]:
            raise ValueError("Conflicting output measurements")
        by_path[path] = record
    pair_validation = verify_fixed_pair_streams(rows, records, native["pairs"])
    folder.mkdir(parents=True, exist_ok=True)
    publication_identity = dict(inputs={str(p): overview.file_digest(p) for p in (old_path, png_path, native_path)},
                                before_sha256=shared.study.digest(before.encode()),
                                implementation=overview.file_digest(__file__))
    frozen = folder / "identity.json"
    if frozen.exists() and json.loads(frozen.read_text()) != publication_identity:
        raise ValueError("Refusing to overwrite another experiment publication")
    if not frozen.exists():
        frozen.write_text(json.dumps(publication_identity, indent=2) + "\n")
    checks = qpdf_checks(list(by_path.values()), old_path.parent.parent / "qpdf.json", folder)
    summary = png_summary(rows, records)
    ffpr_summary = pair_summary([(p["reference"]["result"]["complete_pdf_bytes"],
                                 p["candidate"]["result"]["complete_pdf_bytes"])
                                for p in native["pairs"] if p["combination"]["family"] != "preserve-images"])
    control_summary = pair_summary([(p["reference"]["result"]["complete_pdf_bytes"],
                                    p["candidate"]["result"]["complete_pdf_bytes"])
                                   for p in native["pairs"] if p["combination"]["family"] == "preserve-images"])
    text = before
    for table_id, cells in values.items():
        text = tables.fill(text, table_id, cells)
    # Never restore superseded lossy cells over the current LOSSY-05 controls.
    from tools.publish_lossy_controls import apply_current
    text = apply_current(text)
    (folder / "before.md").write_text(before)
    (folder / "after.md").write_text(text)
    (folder / "implementation.py").write_bytes(Path(__file__).read_bytes())
    manifest = dict(inputs={str(p): overview.file_digest(p) for p in (old_path, png_path, native_path)},
                    implementation=overview.file_digest(__file__), rows=[asdict(r) for r in rows],
                    records=records, extras=old["extras"], native_pairs=native["pairs"], png_summary=summary,
                    native_summary=dict(ffpr=ffpr_summary, controls=control_summary),
                    pair_validation=pair_validation,
                    before_sha256=shared.study.digest(before.encode()), after_sha256=shared.study.digest(text.encode()),
                    counts=dict(distinct_pdfs=len(by_path), displayed_sizes=375, baseline_sizes=204,
                                png_percentages=96, result_cells=471,
                                png_pairs=96, native_pairs=42, qpdf_passed=checks["checked"],
                                qpdf_unsupported=checks["unsupported"]))
    (folder / "publication.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--existing", type=Path, required=True)
    parser.add_argument("--png", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--emit-patch", action="store_true")
    args = parser.parse_args()
    text = publish(args.before.read_text(), args.existing, args.png, args.native, args.output)
    if args.emit_patch:
        target = tables.PAGE
        if target.read_text() not in (args.before.read_text(), text):
            raise ValueError("Report changed outside this publication; refusing to overwrite edits")
        difference = list(difflib.unified_diff(target.read_text().splitlines(), text.splitlines(), n=3))[2:]
        print("*** Begin Patch\n*** Update File: " + str(target))
        print("\n".join("@@" if line.startswith("@@") else line for line in difference))
        print("*** End Patch")
    else:
        print("EXPERIMENT PUBLICATION PREPARED: " + str(args.output / "after.md"))


if __name__ == "__main__":
    main()
