"""Focused integrated size cases at 300 DPI, using the overview's real pairs.

No timing metric, CSV, mixed general-codec cross-product or alternate saver.
The representative overview supplies the five-color/main-source columns; this
runner measures only additional palette, threshold, scan and native controls.
"""

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import bench_compression_overview as overview

study = overview.study


@dataclass(frozen=True)
class Scenario:
    key: str
    label: str
    source: str
    family: str
    colors: int = 5
    strategy: str = "otsu"
    threshold: int = 180


SCENARIOS = (
    *(Scenario(f"{kind}-{count}", f"{count} colors", source, "indexed", colors=count)
      for kind, source in (("art", "examples/images.pdf"),
                           ("mixed", "examples/paper-arxiv-1406.2661.pdf")) for count in (16, 64)),
    Scenario("naca", "NACA formulas", "examples/scan-naca-formulas.pdf", "bw-images"),
    *(Scenario(f"art-t{threshold}", f"Simple T{threshold}", "examples/images.pdf", "bw-images",
               strategy="simple", threshold=threshold) for threshold in (180, 210)),
    Scenario("form941", "Form 941", "examples/form-941-2026.pdf", "preserve-images"),
    Scenario("kepler", "NASA Kepler", "examples/models-nasa-kepler.pdf", "preserve-images"),
)


def rows_for(scenario):
    return tuple(row for row in overview.ROWS if row.family == scenario.family)


def prepare(scenario, folder, resume):
    source = Path(scenario.source)
    if scenario.family != "preserve-images":
        raw = study.images.run_case(source, folder, mode=scenario.family, dpi=300,
                                    colors=scenario.colors, strategy=scenario.strategy,
                                    threshold=scenario.threshold, variants=study.VARIANTS, resume=resume)
        manifest = folder / "manifest.json"
        manifest.write_text(json.dumps([raw], indent=2) + "\n")
        return next(study.bitmap_cases(manifest))
    folder.mkdir(parents=True, exist_ok=resume)
    base = folder / "base.pdf"
    recipe = dict(mode="passthrough")
    identity = dict(source=scenario.source, input_sha256=overview.file_digest(source), recipe=recipe)
    checkpoint = folder / "identity.json"
    if resume and base.exists():
        previous = json.loads(checkpoint.read_text())
        if previous["identity"] != identity or previous["sha256"] != overview.file_digest(base):
            raise ValueError("Changed native scenario preparation")
    else:
        if base.exists():
            raise FileExistsError(base)
        study.pipeline.save_with_spec(str(source), str(base), recipe, workdir=str(folder))
        checkpoint.write_text(json.dumps(dict(identity=identity, sha256=overview.file_digest(base)), indent=2) + "\n")
    case = dict(id=scenario.key, family="production", source=scenario.source,
                input_sha256=identity["input_sha256"], mode="passthrough", dpi=300,
                recipe=recipe, bases={"preserve-images": dict(pdf=str(base), sha256=overview.file_digest(base))})
    error = overview.preparation_error(case, {})
    if error:
        raise RuntimeError(error["validation_error"])
    return case


def identity():
    return dict(environment=study.environment(), implementation=overview.file_digest(__file__),
                overview_implementation=overview.file_digest(overview.__file__),
                dpi=300, scenarios=[asdict(s) for s in SCENARIOS])


def run(folder, *, resume=False):
    folder.mkdir(parents=True, exist_ok=resume)
    current = identity()
    checkpoint = folder / "metrics.json"
    if resume and checkpoint.exists() and json.loads(checkpoint.read_text())["identity"] != current:
        raise ValueError("Changed focused-study implementation or scope")
    (folder / "implementation.py").write_bytes(Path(__file__).read_bytes())
    records = []
    for scenario in SCENARIOS:
        preparation = folder / "prepared" / scenario.key
        case = prepare(scenario, preparation, resume and preparation.exists())
        for row in rows_for(scenario):
            selected = dict(case, bases={row.variant: case["bases"][row.variant]})
            destination = folder / "outputs" / scenario.key / row.variant / row.native
            report = study.run_case(selected, destination, policies=(row.native,),
                                    resume=resume and destination.exists())
            result = report["results"][0]
            overview.validate_record(selected, result)
            records.append(dict(scenario=asdict(scenario), case=selected, result=result,
                                origin=str(destination / "metrics.json")))
            checkpoint.write_text(json.dumps(dict(identity=current, records=records), indent=2) + "\n")
    print(f"FOCUSED 300 DPI STUDY COMPLETE: {len(records)} verified complete PDFs", flush=True)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", default="scenarios-300dpi-20261015")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if Path(args.label).name != args.label or args.label in (".", ".."):
        parser.error("label must be a single directory name")
    run(Path(".tmp/integrated-compression") / args.label, resume=args.resume)


if __name__ == "__main__":
    main()
