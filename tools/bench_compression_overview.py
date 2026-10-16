"""Six representative PDF cases, realistic combinations, complete bytes only.

Reuses hash-verified complete outputs, measures missing cells with the existing
strict integrated saver, and publishes Markdown rather than a codec cross-product.
"""

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import bench_integrated_compression as study

BENCHMARK_DPI = 300

@dataclass(frozen=True)
class Document:
    key: str
    label: str
    source: str


DOCUMENTS = (
    Document("native", "Native text/vectors", "examples/form-fw9.pdf"),
    Document("scan", "BW scan", "examples/scan-jfk-poor-copies.pdf"),
    Document("photos", "Color photos", "examples/news-crater-lake-2026.pdf"),
    Document("art", "Flat-color artwork", "examples/images.pdf"),
    Document("mixed", "Mixed text/images", "examples/paper-arxiv-1406.2661.pdf"),
    Document("kepler", "Technical illustrations", "examples/models-nasa-kepler.pdf"),
)


@dataclass(frozen=True)
class Combination:
    family: str
    variant: str
    native: str
    label: str


def combinations():
    names = {"flate": "Classic Flate (reference)", "zopfli": "Zopfli-Flate", "brotli": "Brotli"}
    rows = [Combination("preserve-images", "preserve-images", p,
                        f"Preserve images + {names[p]} native") for p in study.POLICIES]
    for family, label in (("jpeg-q50", "JPEG q50"), ("jpx-r192", "JPEG2000 lossy r192"),
                          ("jpx-lossless", "JPEG2000 lossless")):
        rows += [Combination(family, family, p, f"{label} + {names[p]} native")
                 for p in ("zopfli", "brotli")]
    for family, label in (("indexed", "Indexed 5 colors"), ("bw-images", "BW; keep native"),
                          ("bw-ffpr", "BW FFPR"), ("indexed-ffpr", "Color FFPR; indexed 5 colors")):
        for policy in study.POLICIES:
            rows += [Combination(family, f"{policy}-{prediction}", policy,
                                 f"{label} + {names[policy]}" + (" + PNG prediction" if prediction == "png" else ""))
                     for prediction in ("plain", "png")]
        rows += [Combination(family, "jbig2", p,
                             f"{label} + {'colored JBIG2' if family.startswith('indexed') else 'JBIG2'}"
                             + ("; optimized residual streams" if family.endswith("-ffpr") else f" + {names[p]} native"))
                 for p in (("zopfli",) if family.endswith("-ffpr") else ("zopfli", "brotli"))]
    for family, label in (("jpeg-q50", "JPEG q50"), ("jpx-r192", "JPEG2000 lossy r192"),
                          ("jpx-lossless", "JPEG2000 lossless")):
        ffpr = family + "-ffpr"
        rows.append(Combination(ffpr, ffpr, "zopfli", f"Color FFPR + {label}; optimized residual streams"))
    return tuple(rows)


ROWS = combinations()


def case_id(source, family):
    stem = Path(source).stem
    if family.startswith("indexed"):
        return f"{stem}.{family}.{BENCHMARK_DPI}dpi.5colors"
    if family in ("bw-images", "bw-ffpr"):
        return f"{stem}.{family}.300dpi.otsu-180"
    return f"{stem}.{family}.{BENCHMARK_DPI}dpi"


def file_digest(path):
    return study.digest(Path(path).read_bytes())


def validate_inputs(case):
    if file_digest(case["source"]) != case["input_sha256"]:
        raise ValueError("Changed source PDF")
    for base in case["bases"].values():
        if file_digest(base["pdf"]) != base["sha256"]:
            raise ValueError("Changed prepared PDF")


def validate_record(case, result, implementation=None):
    """Reuse is bound to actual source/preparation/output hashes and tested code."""
    if result.get("validation_error"):
        raise ValueError("A rejected output cannot be reused as a valid size")
    if implementation:
        for name, expected in implementation.items():
            if file_digest(name) != expected:
                raise ValueError(f"Changed prior benchmark implementation: {name}")
    validate_inputs(case)
    target = Path(result["pdf"])
    if target.stat().st_size != result["complete_pdf_bytes"] or file_digest(target) != result["pdf_sha256"]:
        raise ValueError("Changed complete output PDF")
    if not all(result.get(key) for key in ("exact_native", "exact_images", "exact_all_page_pixels")):
        raise ValueError("Missing exact-output verification")


def load_history(path):
    reports = json.loads(path.read_text())
    return {report["identity"]["case"]["id"]: report for report in reports}


def native_diagnostics(path):
    """A frozen preparation is not valid merely because later saves preserve it."""
    study.fitz.TOOLS.mupdf_warnings()
    with study.fitz.open(path) as pdf:
        initial = study.images.diagnostic_messages(study.fitz.TOOLS.mupdf_warnings())
        pages = []
        for page in pdf:
            page.get_text("words")
            study.images.render_signature(page, 72)
            pages.append(initial | study.images.diagnostic_messages(study.fitz.TOOLS.mupdf_warnings()))
    return pages


def preparation_error(case, cache):
    def diagnostics(path):
        key = (path, file_digest(path))
        if key not in cache:
            cache[key] = native_diagnostics(path)
        return cache[key]
    source = diagnostics(case["source"])
    for base in case["bases"].values():
        actual = diagnostics(base["pdf"])
        if len(actual) != len(source):
            return dict(validation_error="Changed preparation page count", validation_stage="shared-preparation",
                        rejected_pdf=base["pdf"])
        for pno, (before, after) in enumerate(zip(source, actual)):
            if after - before:
                return dict(validation_error=f"New native preparation diagnostics on page {pno+1}: {sorted(after-before)}",
                            validation_stage="shared-preparation", rejected_pdf=base["pdf"])
        if not case.get("recipe", {}).get("force_raster"):
            try:
                with study.fitz.open(case["source"]) as original, study.fitz.open(base["pdf"]) as prepared:
                    study.images.assert_no_retained_source_images(original, prepared)
                    for before, after in zip(original, prepared):
                        study.images.assert_native_text(before, after)
            except AssertionError as error:
                return dict(validation_error=f"Changed native preparation text: {error}",
                            validation_stage="shared-preparation", rejected_pdf=base["pdf"])
    return None


def prepare_case(document, family, folder, production, previous=None):
    source = Path(document.source)
    if family in ("indexed", "indexed-ffpr", "bw-images", "bw-ffpr"):
        dpi = BENCHMARK_DPI
        prep = folder / "prepared-bitmaps" / case_id(source, family)
        imported = previous / "prepared-bitmaps" / prep.name if previous else None
        if imported and imported.exists():
            prep = imported
        failures = {}
        try:
            raw = study.images.run_case(source, prep, mode=family, dpi=dpi, colors=5,
                                       variants=study.VARIANTS, resume=prep.exists())
        except (AssertionError, RuntimeError) as error:
            checkpoint = prep / "metrics.json"
            raw = json.loads(checkpoint.read_text()) if checkpoint.exists() else dict(
                source=str(source), input_sha256=file_digest(source), mode=family, dpi=dpi,
                colors=5 if family.startswith("indexed") else None, threshold_method=None if family.startswith("indexed") else "otsu",
                threshold=None, prepared=[], results=[])
            if not raw["results"]:
                failures = {variant: dict(validation_error=repr(error),
                            validation_stage="shared-preparation", rejected_pdf=str(prep / "flate-plain.pdf"))
                            for variant in study.VARIANTS}
            # A rejected variant must not hide valid measurements or become a
            # misleading small-file winner. Verify remaining variants separately
            # against the same first valid preparation, without relaxing pixels.
            else:
                bitmaps = study.images.prepare(source, family, dpi, 5, "otsu", 180, prep)
                first = raw["results"][0]
                _, expected = study.images.verify_variant(source, Path(first["pdf"]), bitmaps,
                                                          family, first["variant"], dpi)
                for variant in study.VARIANTS:
                    if any(r["variant"] == variant for r in raw["results"]):
                        continue
                    target = prep / f"{variant}.pdf"
                    try:
                        if not target.exists():
                            study.images.save_variant(source, target, bitmaps, family, variant, prep)
                        result, _ = study.images.verify_variant(source, target, bitmaps, family, variant, dpi, expected)
                        raw["results"].append(result)
                    except (AssertionError, RuntimeError) as rejected:
                        failures[variant] = dict(validation_error=repr(rejected), rejected_pdf=str(target))
            if not failures:
                raise RuntimeError("Preparation failed without a reproducible rejected variant") from error
        manifest = prep / "manifest.json"
        manifest.write_text(json.dumps(dict(preparation=raw, failures=failures), indent=2)+"\n")
        case = {key: raw[key] for key in ("source", "input_sha256", "mode", "dpi", "colors",
                                         "threshold_method", "threshold", "prepared")}
        case.update(id=prep.name, family="paired-bitmap", failures=failures,
                    recipe={key: case[key] for key in ("mode", "dpi", "colors", "threshold_method", "threshold")},
                    bases={r["variant"]: dict(pdf=r["pdf"], sha256=r["pdf_sha256"]) for r in raw["results"]})
        return case
    if document.source not in production:
        production[document.source] = {next(iter(case["bases"])): case
                                      for case in study.production_cases([source], folder / "production",
                                                                         resume=True, native_sources=[],
                                                                         dpi=BENCHMARK_DPI, include_ffpr=True)}
    return production[document.source][family]


def matrix_markdown(documents, rows, records):
    values = {(r["document"], r["family"], r["result"]["image_variant"], r["result"]["native_policy"]):
              r["result"]["complete_pdf_bytes"] for r in records if not r["result"].get("validation_error")}
    failures = {(r["document"], r["family"], r["result"]["image_variant"], r["result"]["native_policy"]):
                r["result"].get("validation_stage") for r in records if r["result"].get("validation_error")}
    minima = {}
    for document in documents:
        for row in rows:
            key = (document.key, row.family, row.variant, row.native)
            if key in values:
                group = (document.key, row.family)
                minima[group] = min(minima.get(group, values[key]), values[key])
    lines = ["| Algorithm combination | " + " | ".join(d.label for d in documents) + " |",
             "|---|" + "---:|"*len(documents)]
    for row in rows:
        cells = []
        for document in documents:
            key = (document.key, row.family, row.variant, row.native)
            if key in failures:
                cells.append("PREP FAILED" if failures[key] == "shared-preparation" else "FAILED")
                continue
            if key not in values:
                raise ValueError(f"Missing measured cell: {key}")
            value = values[key]
            cells.append(f"**{value:,}**" if value == minima[(document.key, row.family)] else f"{value:,}")
        lines.append("| " + row.label + " | " + " | ".join(cells) + " |")
    return "\n".join(lines)+"\n"


def run(folder, history_path, *, resume=False, reuse_overview=None):
    folder.mkdir(parents=True, exist_ok=resume)
    history = load_history(history_path) if history_path else {}
    production, records, diagnostics = {}, [], {}
    implementation = file_digest(__file__)
    imports = {}
    if reuse_overview:
        imported = json.loads(reuse_overview.read_text())
        if file_digest(reuse_overview.parent / "implementation.py") != imported["implementation"]:
            raise ValueError("Changed imported overview implementation")
        prior_environment = imported.get("environment")
        if prior_environment is None:
            for record in imported["records"]:
                origin = Path(record["origin"])
                if origin.is_file():
                    stored = json.loads(origin.read_text())
                    if isinstance(stored, dict) and "identity" in stored:
                        prior_environment = stored["identity"]["environment"]
                        break
        if prior_environment is None:
            raise ValueError("Missing imported implementation provenance")
        for name, expected in prior_environment["implementation"].items():
            if file_digest(name) != expected:
                raise ValueError(f"Changed imported saver implementation: {name}")
        imports = {(r["document"], r["family"], r["result"]["image_variant"], r["result"]["native_policy"]): r
                   for r in imported["records"]}
    frozen = folder / "implementation.py"
    if frozen.exists() and file_digest(frozen) != implementation:
        raise ValueError("Changed overview implementation; use explicit verified import, not resume")
    frozen.write_bytes(Path(__file__).read_bytes())
    for document in DOCUMENTS:
        prepared = {}
        for row in ROWS:
            prior = history.get(case_id(document.source, row.family))
            prior_result = next((r for r in prior["results"]
                                 if (r["image_variant"], r["native_policy"]) == (row.variant, row.native)), None) if prior else None
            imported = imports.get((document.key, row.family, row.variant, row.native))
            if prior_result:
                case = prior["identity"]["case"]
                validate_record(case, prior_result, prior["identity"]["environment"]["implementation"])
                result, origin = prior_result, str(history_path)
            elif imported:
                case, result = imported["case"], imported["result"]
                if result.get("validation_error"):
                    validate_inputs(case)
                else:
                    validate_record(case, result)
                origin = str(reuse_overview)
            else:
                if row.family not in prepared:
                    prepared[row.family] = (prior["identity"]["case"] if prior else
                                            prepare_case(document, row.family, folder, production,
                                                         reuse_overview.parent if reuse_overview else None))
                case = dict(prepared[row.family])
                if row.variant in case.get("failures", {}):
                    result = dict(image_variant=row.variant, native_policy=row.native, **case["failures"][row.variant])
                    origin = "rejected preparation"
                else:
                    case["bases"] = {row.variant: case["bases"][row.variant]}
                    case["overview_implementation"] = implementation
                    destination = folder / "outputs" / document.key / row.family / row.variant / row.native
                    report = study.run_case(case, destination, policies=(row.native,), resume=resume and destination.exists())
                    result, origin = report["results"][0], str(destination / "metrics.json")
                    validate_record(case, result)
            if row.family in ("jpeg-q50", "jpx-r192", "jpx-lossless") and not result.get("validation_error"):
                rejected = preparation_error(case, diagnostics)
                if rejected:
                    result = dict(image_variant=row.variant, native_policy=row.native, **rejected)
                    origin = "rejected shared preparation"
            records.append(dict(document=document.key, family=row.family, case=case, result=result, origin=origin))
            (folder / "metrics.json").write_text(json.dumps(dict(implementation=implementation,
                   environment=study.environment(),
                   history=str(history_path), imported_overview=str(reuse_overview) if reuse_overview else None,
                   records=records), indent=2)+"\n")
            print(json.dumps(dict(document=document.key, combination=row.label,
                                  complete_pdf_bytes=result.get("complete_pdf_bytes"),
                                  validation_error=result.get("validation_error"), reused=bool(prior_result or imported))), flush=True)
    (folder / "matrix.md").write_text(matrix_markdown(DOCUMENTS, ROWS, records))
    failed = sum(bool(r["result"].get("validation_error")) for r in records)
    print(f"REPRESENTATIVE MATRIX COMPLETE: {len(records)-failed} verified, {failed} rejected cells", flush=True)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", default="representative-300dpi-20261015")
    parser.add_argument("--history", type=Path, help="Optional compatible, hash-verified prior measurements")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--reuse-overview", type=Path, help="Explicitly import verified completed cells/frozen preparations")
    args = parser.parse_args()
    if Path(args.label).name != args.label or args.label in (".", ".."):
        parser.error("label must be one directory name")
    run(Path(".tmp/integrated-compression") / args.label, args.history, resume=args.resume,
        reuse_overview=args.reuse_overview)


if __name__ == "__main__":
    main()
