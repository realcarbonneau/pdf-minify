"""Audit measured Best outputs; emit a table-value/fixture apply_patch.

No encoding or direct tracked-file writes. The page's prose, labels and row
order are curated by hand; this tool fills only the measured value cells of
the `overview`, `zopfli-vs-brotli` and `fixed-controls` tables by table/row
ID. Fixed policies remain the separate binary experiment; PNG controls keep
their original denominators.
"""

import argparse
from collections import Counter
from dataclasses import asdict
import difflib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import bench_best_overview as bench
from tools import benchmark_tables as tables
from tools.publish_lossy_quality import current_overview_values

# Divider rows are curated by hand; their IDs are never filled.
GROUP_IDS = {bench.REFERENCE: "group.reference", bench.BW: "group.bw",
             bench.INDEXED: "group.indexed", bench.COLOR: "group.full-color"}


def recipe_key(family, variant, native="zopfli"):
    """Overview row ID (recipe key) of a measured family/variant combination.

    Packed-sample variants are named per general compressor (`brotli-plain`);
    the recipe catalogue records them under their Zopfli name.
    """
    plain = variant.replace(f"{native}-", "zopfli-", 1)
    matches = [r.key for r in bench.RECIPES if r.family == family and r.variant == plain]
    if len(matches) != 1:
        raise ValueError(f"No benchmark recipe for {family}/{variant}/{native}")
    return matches[0]


def fixed_row_id(family, variant, native):
    """Per-encoder row ID: `<recipe-key>.<zopfli|brotli>` or `reference.classic`."""
    if native == "flate":
        if family != "preserve-images":
            raise ValueError(f"Classic Flate is only the unresampled reference, not {family}")
        return "reference.classic"
    if native not in ("zopfli", "brotli"):
        raise ValueError(f"Unsupported fixed encoder: {native}")
    return f"{recipe_key(family, variant, native)}.{native}"


def recipe_rows(generated):
    """Value cells of a generated recipe table (with dividers) by recipe key."""
    ids, current = [], None
    for recipe in bench.RECIPES:
        if recipe.section != current:
            current = recipe.section
            ids.append(GROUP_IDS[current])
        ids.append(recipe.key)
    rows = tables.keyed_rows(generated, ids)
    return {key: cells for key, cells in rows.items() if key not in GROUP_IDS.values()}


def encoded_images(doc):
    return Counter((doc.xref_get_key(xref, "Filter")[1],
                    bench.study.digest(doc.xref_stream_raw(xref)))
                   for xref in range(1, doc.xref_length())
                   if doc.xref_is_stream(xref) and doc.xref_get_key(xref, "Subtype")[1] == "/Image")


def fixed_label(recipe, policy, catalog):
    variant = recipe.variant.replace("zopfli-", f"{policy}-", 1)
    label = catalog.get((recipe.family, variant, policy), recipe.label + f" + {policy.title()} residual streams")
    return bench.overview.display_label(label)


def fixed_control_values(publication):
    """Measured `fixed-controls` cells, including the Classic Flate reference."""
    overview = bench.overview
    index = bench.fixed_records(publication)
    rows = []
    for recipe in bench.RECIPES:
        for policy in (("flate", "zopfli", "brotli") if recipe.key == "reference" else ("zopfli", "brotli")):
            variant = recipe.variant.replace("zopfli-", f"{policy}-", 1)
            rows.append(overview.Combination(recipe.family, variant, policy, recipe.label))
    generated = overview.matrix_markdown(overview.DOCUMENTS, rows, list(index.values()))
    return tables.keyed_rows(generated, [fixed_row_id(r.family, r.variant, r.native) for r in rows])


def overview_values(report):
    """Best `overview` cells by recipe key; current lossy rows overlay §258's."""
    values = recipe_rows(bench.table(bench.overview.DOCUMENTS, bench.RECIPES, report["records"]))
    values.update(current_overview_values())
    return values


def binary_values(publication):
    """`zopfli-vs-brotli` percentages by recipe key, from the fixed pairs."""
    return recipe_rows(bench.binary_table(bench.overview.DOCUMENTS, bench.RECIPES, publication))


def audit(path):
    report = json.loads(path.read_text())
    expected_identity = bench.identity(bench.PUBLICATION)
    if not report.get("complete") or report["identity"] != expected_identity:
        raise ValueError("Incomplete or incompatible Best study")
    publication = bench.load_publication()
    source_hashes = {r["document"]: r["case"]["input_sha256"] for r in publication["records"]}
    documents = {d.key: d for d in bench.overview.DOCUMENTS}
    recipes = {r.key: r for r in bench.RECIPES}
    fixed = bench.fixed_records(publication)
    actual = {}
    for record in report["records"]:
        key = record["document"], record["recipe"]
        if key in actual or record["identity"] != expected_identity:
            raise ValueError("Duplicate Best output or changed producing identity")
        bench.validate_measured(record)
        job = record["job"]
        document, recipe = documents[record["document"]], recipes[record["recipe"]]
        seed = bench.fixed_pair(document, recipe, fixed)[1]
        if (job["document"] != asdict(document) or job["recipe"] != asdict(recipe)
                or job["preparation"] != seed["case"]["bases"][recipe.variant]
                or job["seed_pdf"] != seed["result"]["pdf"]
                or job["seed_sha256"] != seed["result"]["pdf_sha256"]):
            raise ValueError("Best cell is mislabeled or uses the wrong frozen recipe")
        if (bench.digest(job["preparation"]["pdf"]) != job["preparation"]["sha256"]
                or bench.digest(job["seed_pdf"]) != job["seed_sha256"]
                or bench.digest(job["document"]["source"]) != source_hashes[record["document"]]):
            raise ValueError("Changed source/preparation/render-proof seed")
        case = seed["case"]
        with bench.study.images.open_for_id_change(job["preparation"]["pdf"]) as prepared:
            bench.study.images.set_pdf_id(prepared, case["input_sha256"], case.get("prepared", case["recipe"]),
                                          f"integrated-best:{recipe.key}")
            expected_graph = bench.semantic_graph(prepared)
        with bench.study.fitz.open(record["result"]["pdf"]) as output:
            if (bench.semantic_graph(output) != expected_graph or
                    record["result"]["render_proof"]["semantic_graph_sha256"] != expected_graph):
                raise ValueError("Changed Best document graph")
        actual[key] = record
    expected = {(d.key, r.key) for d in bench.overview.DOCUMENTS for r in bench.RECIPES}
    if set(actual) != expected:
        raise ValueError("Best matrix does not cover all 114 recipe/input cells")
    index = bench.fixed_records(publication)
    for d in bench.overview.DOCUMENTS:
        for r in bench.RECIPES:
            a, b = bench.fixed_pair(d, r, index)
            for record in (a, b):
                bench.overview.validate_record(record["case"], record["result"])
            with bench.study.fitz.open(a["result"]["pdf"]) as left, bench.study.fitz.open(b["result"]["pdf"]) as right:
                if bench.semantic_graph(left, include_ids=False) != bench.semantic_graph(right, include_ids=False):
                    raise ValueError(f"Fixed encoder pair changes content: {d.key}/{r.key}")
                if not r.variant.startswith("zopfli-") and encoded_images(left) != encoded_images(right):
                    raise ValueError(f"Native-only fixed pair changed encoded images: {d.key}/{r.key}")
    return report, publication


def fixture(report, publication, path):
    records = {(r["document"], r["recipe"]): r["result"] for r in report["records"]}
    index = bench.fixed_records(publication)
    catalog = {(r["family"], r["variant"], r["native"]): r["label"] for r in publication["rows"]}
    rows = []
    for recipe in bench.RECIPES:
        row = asdict(recipe)
        row.update(best=[records[d.key, recipe.key]["complete_pdf_bytes"] for d in bench.overview.DOCUMENTS],
                   pdf_sha256=[records[d.key, recipe.key]["pdf_sha256"] for d in bench.overview.DOCUMENTS])
        for i, policy in enumerate(("brotli", "zopfli")):
            row[policy] = [bench.fixed_pair(d, recipe, index)[i]["result"]["complete_pdf_bytes"]
                           for d in bench.overview.DOCUMENTS]
        row["fixed_labels"] = {policy: fixed_label(recipe, policy, catalog) for policy in ("brotli", "zopfli")}
        rows.append(row)
    return dict(designer_ruling=258, stream_policy="best", brotli_declaration=False,
                measured_manifest_sha256=bench.digest(path),
                fixed_publication_sha256=bench.PUBLICATION_SHA256,
                classic_reference=[index[d.key, "preserve-images", "preserve-images", "flate"]["result"]["complete_pdf_bytes"]
                                   for d in bench.overview.DOCUMENTS],
                documents=[asdict(d) for d in bench.overview.DOCUMENTS], rows=rows)


def fill_tables(text, report, publication):
    """Fill measured cells only; prose, labels and row selection stay curated."""
    text = tables.fill(text, "overview", overview_values(report))
    text = tables.fill(text, "zopfli-vs-brotli", binary_values(publication))
    text = tables.fill(text, "fixed-controls", fixed_control_values(publication))
    # The frozen catalogue is historical evidence, not authority to restore
    # obsolete settings in active supporting tables after a newer publication.
    from tools.publish_lossy_controls import apply_current
    return apply_current(text)


def patch(files):
    lines = ["*** Begin Patch\n"]
    for name, before, after in files:
        if before == after:
            continue
        if before is None:
            lines.append(f"*** Add File: {name}\n")
            lines.extend("+" + line for line in after.splitlines(keepends=True))
        else:
            lines.append(f"*** Update File: {name}\n")
            diff = list(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True), n=3))
            lines.extend("@@\n" if line.startswith("@@") else line for line in diff[2:])
    lines.append("*** End Patch\n")
    return "".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measurements", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report, publication = audit(args.measurements)
    source = tables.PAGE
    before = source.read_text()
    after = fill_tables(before, report, publication)
    fixture_path = Path("tests/fixtures/best_overview_sizes.json")
    fixture_text = json.dumps(fixture(report, publication, args.measurements), indent=2) + "\n"
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "report.md").write_text(after)
    (args.output / "audit.json").write_text(json.dumps(dict(
        measured_manifest=dict(path=str(args.measurements), sha256=bench.digest(args.measurements)),
        fixed_publication_sha256=bench.PUBLICATION_SHA256, publisher_sha256=bench.digest(__file__),
        actual_best_outputs=len(report["records"]),
        exact_fixed_pairs=len(bench.RECIPES) * len(bench.overview.DOCUMENTS),
        image_byte_fixed_pairs=sum(not r.variant.startswith("zopfli-") for r in bench.RECIPES) * len(bench.overview.DOCUMENTS),
        packed_sample_pairs=sum(r.variant.startswith("zopfli-") for r in bench.RECIPES) * len(bench.overview.DOCUMENTS),
        declaration=False,
        pixel_proof="unchanged exact semantic graphs preserve frozen preparation renders"), indent=2) + "\n")
    (args.output / "report.patch").write_text(patch([
        (source.as_posix(), before, after),
        (fixture_path.as_posix(), fixture_path.read_text() if fixture_path.exists() else None, fixture_text)]))
    print(f"BEST PUBLICATION VERIFIED: {len(report['records'])} actual outputs; patch {args.output / 'report.patch'}")


if __name__ == "__main__":
    main()
