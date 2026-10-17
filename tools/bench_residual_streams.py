"""NATIVE-01: fixed encoded images, Flate reference versus native optimization."""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import bench_png_extension as shared

overview = shared.overview
study = shared.study
SECTION = "## Native/residual streams — measured effect versus Flate reference"
FAMILIES = ("preserve-images", "bw-ffpr", "indexed-ffpr",
            "jpeg-q50-ffpr", "jpx-r192-ffpr", "jpx-lossless-ffpr")
ROWS = tuple(row for family in FAMILIES for row in overview.ROWS if row.family == family and
             ((family == "preserve-images" and row.native != "flate") or
              (family in ("bw-ffpr", "indexed-ffpr") and row.variant == "jbig2") or
              family in ("jpeg-q50-ffpr", "jpx-r192-ffpr", "jpx-lossless-ffpr")))


def validate_pair(document, row, pair, *, reference_policy="flate"):
    reference, candidate = pair["reference"], pair["candidate"]
    signature = ("source", "input_sha256", "mode", "dpi", "recipe", "prepared", "bases")
    if (pair["document"] != document.key or pair["combination"] != asdict(row) or
            candidate["case"]["source"] != document.source or
            any(reference["case"].get(field) != candidate["case"].get(field) for field in signature)):
        raise ValueError("Native A/B comparison changes source, prepared images or recipe")
    for record, policy in ((reference, reference_policy), (candidate, row.native)):
        result = record["result"]
        if result["native_policy"] != policy or result["image_variant"] != row.variant:
            raise ValueError("Native A/B comparison has wrong image variant or native policy")
        overview.validate_record(record["case"], result)
    if reference["result"]["pdf"] == candidate["result"]["pdf"]:
        raise ValueError("Native A/B pair requires independently saved PDFs")


def tables(documents, rows, pairs):
    indexed = {}
    for pair in pairs:
        key = (pair["document"], pair["combination"]["family"], pair["combination"]["variant"],
               pair["combination"]["native"])
        if key in indexed:
            raise ValueError("Duplicate native A/B pair")
        indexed[key] = pair
    header = ["| Candidate combination | " + " | ".join(d.label for d in documents) + " |",
              "|---|" + "---:|" * len(documents)]
    references, effects = list(header), list(header)
    for row in rows:
        baseline_cells, effect_cells = [], []
        for document in documents:
            key = (document.key, row.family, row.variant, row.native)
            if key not in indexed:
                raise ValueError(f"Missing native A/B pair: {key}")
            pair = indexed[key]
            validate_pair(document, row, pair)
            baseline, candidate = (pair[name]["result"]["complete_pdf_bytes"] for name in ("reference", "candidate"))
            baseline_cells.append(f"{baseline:,}")
            effect_cells.append(overview.measured_effect_cell(baseline, candidate))
        references.append("| " + overview.display_label(row.label) + " | " + " | ".join(baseline_cells) + " |")
        effects.append("| " + overview.display_label(row.label) + " | " + " | ".join(effect_cells) + " |")
    return "\n".join(references) + "\n", "\n".join(effects) + "\n"


def measure_pair(document, row, candidate, reference, folder, identity, resume=False, *, reference_policy="flate"):
    folder = Path(folder)
    checkpoint = folder / "metrics.json"
    expected = dict(run=identity, document=asdict(document), combination=asdict(row),
                    candidate=candidate, imported_reference=reference)
    if reference_policy != "flate":
        expected["reference_policy"] = reference_policy
    if resume and checkpoint.exists():
        previous = json.loads(checkpoint.read_text())
        if previous["identity"] != expected:
            raise ValueError("Changed native A/B job identity")
        validate_pair(document, row, previous["pair"], reference_policy=reference_policy)
        return previous["pair"]
    folder.mkdir(parents=True, exist_ok=resume)
    if reference is None:
        case = deepcopy(candidate["case"])
        destination = folder / "reference"
        report = study.run_case(case, destination, policies=(reference_policy,),
                                resume=resume and destination.exists())
        reference = dict(document=document.key, family=row.family, case=case,
                         result=report["results"][0], origin=str(destination / "metrics.json"))
    pair = dict(document=document.key, combination=asdict(row), reference=reference, candidate=candidate)
    validate_pair(document, row, pair, reference_policy=reference_policy)
    checkpoint.write_text(json.dumps(dict(identity=expected, pair=pair), indent=2) + "\n")
    print(json.dumps(dict(completed=document.key, combination=row.label,
                          baseline_bytes=reference["result"]["complete_pdf_bytes"],
                          candidate_bytes=candidate["result"]["complete_pdf_bytes"])), flush=True)
    return pair


def run(folder, existing, *, resume=False, workers=1):
    if not 1 <= workers <= 3:
        raise ValueError("Use one to three isolated benchmark processes")
    current = shared.toolchain()
    stored, proof = shared.import_history(existing, current)
    identity = dict(toolchain=current, implementation=overview.file_digest(__file__),
                    documents=[asdict(d) for d in overview.DOCUMENTS], rows=[asdict(r) for r in ROWS],
                    factor="native stream encoder: standard Flate versus named optimized policy",
                    imported=proof, dpi=300)
    folder.mkdir(parents=True, exist_ok=resume)
    frozen = folder / "identity.json"
    if frozen.exists():
        if not resume or json.loads(frozen.read_text()) != identity:
            raise ValueError("Changed native A/B study identity")
    else:
        frozen.write_text(json.dumps(identity, indent=2) + "\n")
        (folder / "implementation.py").write_bytes(Path(__file__).read_bytes())
    index = {(r["document"], r["family"], r["result"]["image_variant"], r["result"]["native_policy"]): r
             for r in stored["records"]}
    checkpoint = folder / "metrics.json"
    completed = {}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {}
        for document in overview.DOCUMENTS:
            for row in ROWS:
                key = (document.key, row.family, row.variant, row.native)
                candidate = index[key]
                reference = index.get((document.key, row.family, row.variant, "flate"))
                destination = folder / "jobs" / document.key / row.family / row.native
                future = pool.submit(measure_pair, document, row, candidate, reference,
                                     destination, identity, resume)
                futures[future] = key
        for future in as_completed(futures):
            completed[futures[future]] = future.result()
            checkpoint.write_text(json.dumps(dict(identity=identity,
                complete=len(completed) == len(ROWS) * len(overview.DOCUMENTS),
                pairs=list(completed.values())), indent=2) + "\n")
    pairs = [completed[(d.key, r.family, r.variant, r.native)] for d in overview.DOCUMENTS for r in ROWS]
    reference, effect = tables(overview.DOCUMENTS, ROWS, pairs)
    (folder / "reference.md").write_text(reference)
    (folder / "effect.md").write_text(effect)
    print(f"NATIVE A/B COMPLETE: {len(pairs)} verified pairs", flush=True)
    return pairs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True)
    parser.add_argument("--existing", type=Path, required=True, help="Verified selected-study manifest")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    if Path(args.label).name != args.label or args.label in (".", ".."):
        parser.error("label must be one directory name")
    run(Path(".tmp/compression-experiments") / args.label, args.existing,
        resume=args.resume, workers=args.workers)


if __name__ == "__main__":
    main()
