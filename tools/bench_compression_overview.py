"""Six representative PDF cases, realistic combinations, complete bytes only.

Reuses hash-verified complete outputs, measures missing cells with the existing
strict integrated saver, and publishes Markdown rather than a codec cross-product.
"""

import argparse
from dataclasses import dataclass
from decimal import Decimal
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
    Document("scan", "BW scan", "examples/scan-naca-tm972.pdf"),
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
    for family, label in (("indexed", "Indexed 5 colors"), ("bw-images", "BW"),
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


ALL_ROWS = combinations()
BITMAP_FAMILIES = ("indexed", "indexed-ffpr", "bw-images", "bw-ffpr")
# §§236/237: retain the unresampled reference, not redundant bitmap encodings.
# Focused scenarios share this selection, rather than reintroducing those rows.
ROWS = tuple(row for row in ALL_ROWS if not (row.family in BITMAP_FAMILIES and row.native == "flate"))
PNG_SECTION = "## PNG prediction — measured effect versus baseline"


def primary_rows(rows):
    """Prediction remains measured, but its effect is presented separately."""
    return tuple(row for row in rows if not row.variant.endswith("-png"))


def png_pairs(rows):
    rows = tuple(rows)
    by_key = {(r.family, r.variant, r.native): r for r in rows}
    pairs = []
    for row in rows:
        if row.variant.endswith("-png"):
            key = (row.family, row.variant.removesuffix("-png") + "-plain", row.native)
            if key not in by_key:
                raise ValueError(f"Missing plain baseline combination: {key}")
            pairs.append((by_key[key], row))
    return tuple(pairs)


def png_effect_cell(baseline_bytes, png_bytes, *, show_size=True):
    """Signed change from measured bytes, optionally including candidate size."""
    if any(type(size) is not int or size <= 0 for size in (baseline_bytes, png_bytes)):
        raise ValueError("PNG comparison requires positive measured integer byte counts")
    change = (100 * Decimal(png_bytes - baseline_bytes) / Decimal(baseline_bytes)).quantize(Decimal("0.1"))
    if change == 0:
        change = Decimal(0)  # Do not print a misleading negative zero after rounding.
    if not show_size:
        percentage = f"{change:+.1f}%"
        return f"**{percentage}**" if png_bytes <= baseline_bytes else percentage
    size = f"{png_bytes:,}"
    if png_bytes <= baseline_bytes:
        size = f"**{size}**"
    return f"{size} ({change:+.1f}%)"


def png_prediction_markdown(documents, rows, records):
    """One-factor effect table; callers verify source/output files before publishing."""
    pairs = png_pairs(rows)
    if not pairs:
        return ""
    by_key = {}
    for record in records:
        result = record["result"]
        key = (record["document"], record["family"], result["image_variant"], result["native_policy"])
        if key in by_key:
            raise ValueError(f"Duplicate measured cell: {key}")
        by_key[key] = record
    lines = ["| Baseline combination | " + " | ".join(d.label for d in documents) + " |",
             "|---|" + "---:|" * len(documents)]
    signature = ("source", "input_sha256", "mode", "dpi", "recipe", "prepared")
    for plain, png in pairs:
        cells = []
        for document in documents:
            keys = [(document.key, r.family, r.variant, r.native) for r in (plain, png)]
            if any(key not in by_key for key in keys):
                raise ValueError(f"Missing measured PNG/plain pair: {keys}")
            baseline, candidate = (by_key[key] for key in keys)
            results = [r["result"] for r in (baseline, candidate)]
            rejected = [r for r in results if r.get("validation_error")]
            if rejected:
                cells.append("PREP FAILED" if any(r.get("validation_stage") == "shared-preparation"
                                                 for r in rejected) else "FAILED")
                continue
            cases = [r.get("case", {}) for r in (baseline, candidate)]
            if any(any(field not in case for field in signature) for case in cases):
                raise ValueError("Missing PNG/plain pair provenance")
            if ({field: cases[0][field] for field in signature} !=
                    {field: cases[1][field] for field in signature} or
                    cases[0]["source"] != document.source):
                raise ValueError("PNG comparison changes source, recipe or prepared pixels")
            if not all(r.get(field) for r in results for field in
                       ("exact_native", "exact_images", "exact_all_page_pixels")):
                raise ValueError("Missing exact-output verification for PNG/plain pair")
            if not all(r.get("pdf") for r in results) or results[0]["pdf"] == results[1]["pdf"]:
                raise ValueError("PNG/plain pair requires independently saved PDFs")
            cells.append(png_effect_cell(*(r["complete_pdf_bytes"] for r in results), show_size=False))
        lines.append("| " + plain.label + " | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def bitmap_variants(rows):
    wanted = {row.variant for row in rows}
    return tuple(variant for variant in study.VARIANTS if variant in wanted)


def bitmap_case(raw, identifier):
    """One manifest shape for overview/focused preparations of any chosen subset."""
    case = {key: raw[key] for key in ("source", "input_sha256", "mode", "dpi", "colors",
                                    "threshold_method", "threshold", "prepared")}
    case.update(id=identifier, family="paired-bitmap",
                recipe={key: case[key] for key in ("mode", "dpi", "colors", "threshold_method", "threshold")},
                bases={r["variant"]: dict(pdf=r["pdf"], sha256=r["pdf_sha256"]) for r in raw["results"]})
    return case


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
    if family in BITMAP_FAMILIES:
        variants = bitmap_variants(row for row in ROWS if row.family == family)
        if not variants:
            raise ValueError(f"No selected bitmap variants for {family}")
        dpi = BENCHMARK_DPI
        prep = folder / "prepared-bitmaps" / case_id(source, family)
        imported = previous / "prepared-bitmaps" / prep.name if previous else None
        if imported and imported.exists():
            prep = imported
        failures = {}
        try:
            raw = study.images.run_case(source, prep, mode=family, dpi=dpi, colors=5,
                                       variants=variants, resume=prep.exists())
        except (AssertionError, RuntimeError) as error:
            checkpoint = prep / "metrics.json"
            raw = json.loads(checkpoint.read_text()) if checkpoint.exists() else dict(
                source=str(source), input_sha256=file_digest(source), mode=family, dpi=dpi,
                colors=5 if family.startswith("indexed") else None, threshold_method=None if family.startswith("indexed") else "otsu",
                threshold=None, prepared=[], results=[])
            if not raw["results"]:
                failures = {variant: dict(validation_error=repr(error),
                            validation_stage="shared-preparation", rejected_pdf=str(prep / f"{variants[0]}.pdf"))
                            for variant in variants}
            # A rejected variant must not hide valid measurements or become a
            # misleading small-file winner. Verify remaining variants separately
            # against the same first valid preparation, without relaxing pixels.
            else:
                bitmaps = study.images.prepare(source, family, dpi, 5, "otsu", 180, prep)
                first = raw["results"][0]
                _, expected = study.images.verify_variant(source, Path(first["pdf"]), bitmaps,
                                                          family, first["variant"], dpi)
                for variant in variants:
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
        case = bitmap_case(raw, prep.name)
        case["failures"] = failures
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
    (folder / "matrix.md").write_text(matrix_markdown(DOCUMENTS, primary_rows(ROWS), records))
    png_table = png_prediction_markdown(DOCUMENTS, ROWS, records)
    if png_table:
        (folder / "png-prediction.md").write_text(PNG_SECTION + "\n\n" + png_table)
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
