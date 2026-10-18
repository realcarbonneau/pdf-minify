"""Audit measured Best outputs and emit a documentation/fixture apply_patch.

No encoding or direct tracked-file writes. Fixed policies remain the separate
binary experiment; PNG controls keep their original denominators.
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

MAIN = "## Overview — final complete-file bytes"
OLD_BINARY = "## FFPR residual compression — Zopfli versus Brotli baseline"
BINARY = "## Stream compression — Zopfli versus Brotli baseline"
PNG_GUIDANCE = """### Results and decision tree

**Fixed-encoder measured result:** prediction reduces **0 of 48 Brotli** files
and **18 of 48 Zopfli** files. With every measured same-fidelity algorithm
eligible, none of the 96 PNG candidates is uniquely smallest. Reader limits
matter: excluding Brotli leaves eight strict wins in the measured 16/64-color
alternatives, not an exhaustive layered-JBIG2 search.

Use the **prepared output image**, not its original file type, to branch:

```text
Prepared output image
├─ No bitmap rows → no-op; no prediction decision.
├─ JPEG / JPEG2000 / JBIG2 → PNG prediction not applicable to that payload.
└─ Packed BW / indexed samples
   ├─ Best (Zopfli/Brotli) → automatically test OFF/ON with both encoders.
   ├─ Zopfli → PNG prediction: Off / On / Best.
   │           Best automatically compares OFF/ON with Zopfli only.
   └─ Fixed Brotli study → OFF favored here (0/48 reductions), not universally.
```

**Counterexample:** the earlier noisy-BW Brotli control improves **-2.90%**
with prediction, although JBIG2 remains smaller. See the
[measured evidence](IMAGE_STREAM_COMPRESSION.md#what-these-sizes-show).
All current indexed-color photo/artwork PNG candidates grow; some
mixed-paper indexed FFPR candidates shrink with Zopfli. Encoder and actual
image content—not palette count or FFPR alone—determine the measured outcome.

**Application policy (§260):** Best performs the joint search rather than
turning these content observations into skip heuristics. Explicit Zopfli's
Off/On choices force their stated predictor; Best measures both. Compare
actual complete saved PDFs, including predictor dictionaries and container
overhead, without repeating image processing. Keep exact sample bytes and
J* payloads. Native text/vector streams do not use image-row prediction.

The source need not contain PNG files: prediction applies to the prepared
pixel rows. No eligible bitmap rows or J* payloads are applicability skips,
not evidence that prediction loses. Unsupported general-image layouts stay
unchanged in automatic mode; explicit On reports an error. The existing
114-file overview and 96 fixed-encoder pairs do **not** measure §260's new
joint search; their measured sizes and denominators remain frozen.

### Method and interpretation"""


def encoded_images(doc):
    return Counter((doc.xref_get_key(xref, "Filter")[1],
                    bench.study.digest(doc.xref_stream_raw(xref)))
                   for xref in range(1, doc.xref_length())
                   if doc.xref_is_stream(xref) and doc.xref_get_key(xref, "Subtype")[1] == "/Image")


def fixed_label(recipe, policy, catalog):
    variant = recipe.variant.replace("zopfli-", f"{policy}-", 1)
    label = catalog.get((recipe.family, variant, policy), recipe.label + f" + {policy.title()} residual streams")
    return bench.overview.display_label(label)


def fixed_controls(publication):
    """Relocate all fixed alternatives, including the old Classic reference."""
    overview = bench.overview
    index = bench.fixed_records(publication)
    catalog = {(r["family"], r["variant"], r["native"]): r["label"] for r in publication["rows"]}
    rows = []
    for recipe in bench.RECIPES:
        for policy in (("flate", "zopfli", "brotli") if recipe.key == "reference" else ("zopfli", "brotli")):
            variant = recipe.variant.replace("zopfli-", f"{policy}-", 1)
            label = fixed_label(recipe, policy, catalog)
            rows.append(overview.Combination(recipe.family, variant, policy, label))
    records = list(index.values())
    raw = overview.matrix_markdown(overview.DOCUMENTS, rows, records)
    return raw.replace("| Algorithm combination |", "| Fixed-policy combination |", 1)


def fixed_controls_section(publication):
    """Keep the measured baseline sizes always visible (§259)."""
    return (
        "### Fixed-encoder controls — measured final PDF bytes\n\n"
        "These are the relocated fixed-policy alternatives, not additional main\n"
        "matrix choices. PNG OFF/ON calculations keep these encoder-specific\n"
        "plain baselines. The Classic-Flate reference remains a control only.\n\n"
        + fixed_controls(publication) + "\n"
    )


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


def replace_once(text, before, after):
    if text.count(before) != 1:
        raise ValueError(f"Expected exactly one report fragment: {before[:90]}")
    return text.replace(before, after, 1)


def rewrite(before, report, publication, path):
    text = before
    text = replace_once(text, "Designer §§210–214/220–254; TODO §§226–252.",
                        "Designer §§210–214/220–260; TODO §§226–257.")
    text = replace_once(text, "All **177 integrated Brotli outputs** were",
                        "The fixed-encoder study's **177 integrated Brotli outputs** were")
    start = "**Current selected results after the B114 preparation repair and §254 refresh.**"
    paragraph = next(p for p in text.split("\n\n") if p.startswith(start))
    text = replace_once(text, paragraph,
        "**Versioned selection (§258).** The overview has **19 recipes × six complete PDFs = 114 measured sizes**. "
        "The separate Zopfli/Brotli binary reference covers the same 19 recipes; PNG prediction retains "
        "its **96 fixed-encoder pairs**, and NATIVE-01 retains **42 pairs**. The new saves reuse verified "
        "post-B114 preparations; the 392-file fixed-encoder publication remains unchanged. "
        "The BW representative is the eleven-page CCITT NACA TM972 scan, not the already-JBIG2 JFK "
        "regression fixture. B114 is worker-verified, not designer-confirmed acceptance.\n\n"
        "**Policy boundary (§260).** The app's joint encoder/predictor search is newer\n"
        "than these measurements. The 114 overview files use §258's predictor-preserving\n"
        "Best; the 96 PNG pairs use fixed encoders. Neither is relabeled as a measured\n"
        "result of the new automatic search. No replacement size is estimated.")
    text = replace_once(text,
        "  compressor, not a second image/codec. The overview shows plain baselines; the separate PNG table isolates its measured effect.",
        "  compressor, not a second image/codec. Its separate table compares each\n"
        "  fixed encoder's own plain baseline, not the main matrix's policy.")
    text = replace_once(text,
        "- Packed BW/indexed images and native streams use the **same general\n"
        "  compressor**. Mixed general-compressor pairings are excluded from the algorithm overview.\n"
        "  The isolated native-stream experiment deliberately holds image bytes fixed. Specialized\n"
        "  JPEG/JPEG2000/JBIG2 retain meaningful native Zopfli/Brotli alternatives.",
        "- Fixed-encoder controls pair packed BW/indexed images and native streams\n"
        "  with the **same general compressor**. Their specialized J* comparisons\n"
        "  change native/residual compression only. Keep these controlled alternatives\n"
        "  separate from the main matrix's stream-selection policy.")
    text = replace_once(text,
        "Rows without FFPR retain native text/vectors; preservation is implicit in\n"
        "their labels (§232). A compressor followed by `native` identifies the\n"
        "compression applied to those PDF streams, not the bitmap image codec.",
        "Rows without FFPR retain native text/vectors; preservation is implicit in\n"
        "their labels (§232). In fixed-encoder reference labels, `native` identifies\n"
        "the stream compressor, not the bitmap image codec.")
    residual_start = text.index("In FFPR rows, **residual streams**")
    main_start = text.index(MAIN)
    text = text[:residual_start] + (
        "In FFPR rows, **residual streams** means the non-image PDF content left\n"
        "after rasterization, mainly commands that position/draw the page images.\n"
        "The historical fixed-control label **optimized residual streams** means\n"
        "Zopfli for those remaining streams. It is confined to the supporting\n"
        "experiment/reference data, not the new overview's policy or row labels.\n"
        "JPEG/JPEG2000/JBIG2 encode images separately; the shared final writer\n"
        "handles PDF object/xref packing independently.\n\n"
    ) + text[main_start:]
    main_start = text.index(MAIN)
    png_start = text.index(bench.overview.PNG_SECTION)
    primary = (
        MAIN + "\n\n"
        "Every row uses **Best (Zopfli/Brotli)** for native and eligible packed\n"
        "BW/indexed streams. It keeps the smallest actual complete all-Zopfli,\n"
        "all-Brotli or per-stream mixed save, without changing image codecs, quality, DPI,\n"
        "prediction or J* payloads. Compatibility metadata is OFF; output can\n"
        "require a Brotli-capable reader. This common policy is omitted from\n"
        "row labels. The\n"
        "[specialized binary experiment](#stream-compression--zopfli-versus-brotli-baseline)\n"
        "owns the fixed-encoder comparison and its reference sizes.\n\n"
        "This is the measured **§258 predictor-preserving** Best policy, not §260's\n"
        "new joint encoder/predictor search. Frozen outputs and producer identities\n"
        "stay unchanged; reproducing this experiment requests predictor preservation\n"
        "explicitly.\n\n"
        "Transformed packed-image rows use PNG prediction OFF; the unresampled\n"
        "reference keeps its existing image decoding parameters.\n\n"
        "The unresampled reference does not compose, resize or recolor images.\n"
        "It preserves their samples and geometry; eligible lossless image streams\n"
        "can be repacked, so it does not promise identical encoded image bytes.\n"
        "It is a benchmark control, not the app's untouched Original view.\n"
        "All other image recipes use 300 DPI. Original file sizes remain above.\n"
        "Classic-Flate controls are retained in the specialized reference, not\n"
        "this matrix.\n\n"
        "One continuous table retains BW, indexed color and full-color dividers,\n"
        "with native-preserving rows before FFPR. Bold minima compare the same\n"
        "input and fidelity group only; palette counts and JPEG/JPX quality\n"
        "targets remain distinct. A smaller encoding need not beat the original.\n\n"
        + bench.table(bench.overview.DOCUMENTS, bench.RECIPES, report["records"]) + "\n"
    )
    text = text[:main_start] + primary + text[png_start:]
    text = replace_once(text,
        "names its plain baseline in the overview above. Each cell shows the",
        "names its own **fixed-encoder plain baseline**, retained in the specialized\n"
        "reference controls below—not a Best result from the new overview.\n"
        "No denominator or PNG measurement changes. Each cell shows the")
    text = replace_once(text,
        "files now included in this expanded overview.", "files retained in the fixed-encoder controls.")
    text = replace_once(text, "**Does prediction ever win overall?** With all measured same-fidelity\nalgorithms eligible,",
        "**Does prediction ever win overall?** In the fixed-encoder study, with all\nmeasured same-fidelity algorithms eligible,")
    text = replace_once(text, bench.overview.PNG_SECTION + "\n\n",
        bench.overview.PNG_SECTION + "\n\n" + PNG_GUIDANCE + "\n\n")
    old_start = text.index(OLD_BINARY)
    old_end = text.index("## Focused scenarios", old_start)
    old = text[old_start:old_end]
    subset = old[old.index("**Result with declaration OFF:"):]
    subset = subset.replace("### Why Brotli can still be larger", "### Why Brotli can still be larger for the FFPR/J* subset")
    binary = (
        '<a id="ffpr-residual-compression--zopfli-versus-brotli-baseline"></a>\n\n'
        + BINARY + "\n\n"
        "**Expanded binary reference (§258).** Brotli is the baseline and Zopfli\n"
        "the treatment for all 19 overview recipes / **114 pairs**. Source,\n"
        "prepared samples/palette, DPI, threshold/quality, native content, ID\n"
        "framing, writer and declaration-OFF setting stay fixed. For packed\n"
        "BW/indexed rows, this single general-encoder factor changes both image\n"
        "and native streams. For J* and original-image references, only native/\n"
        "residual streams change; their encoded image payloads stay identical.\n"
        "Do not confuse either fixed-policy side with the overview's Best output.\n\n"
        "In particular, the original-image fixed control preserves encoded images;\n"
        "the main unresampled Best reference may also repack eligible image\n"
        "streams. These historical controls are not homogeneous Best candidates.\n\n"
        "`Change (%) = 100 × (Zopfli bytes − Brotli bytes) / Brotli bytes`.\n"
        "**Negative favors Zopfli; positive favors Brotli.** Cells show only\n"
        "two-decimal measured full-file changes. Bold marks displayed negatives;\n"
        "rounded +0.00% is never bold. Exact baseline/treatment sizes are retained\n"
        "in the always-visible reference table and measured evidence below.\n\n"
        "### Replace Brotli with Zopfli — final PDF size change (%)\n\n"
        + bench.binary_table(bench.overview.DOCUMENTS, bench.RECIPES, publication) + "\n"
        "### FFPR/J* subset — unchanged NATIVE-02 findings\n\n"
        "The five FFPR/J* recipes above are the original **30-pair NATIVE-02**\n"
        "experiment (§§245/246). Their results and causal accounting remain\n"
        "unchanged; the statements in this subsection refer to those 30 pairs,\n"
        "not every row of the expanded reference.\n\n" + subset
        + fixed_controls_section(publication) + "\n"
    )
    text = text[:old_start] + binary + text[old_end:]
    text = replace_once(text,
        "Every cell below is another complete saved PDF or an explicitly reused cell\n"
        "from the overview.",
        "Every cell below is a fixed-encoder supporting control, not a Best result\n"
        "from the new overview. Cells reuse their original measured files where applicable.")
    marker = "The representative inventory is **50 combinations"
    paragraph = next(p for p in text.split("\n\n") if p.startswith(marker))
    text = replace_once(text, paragraph,
        "§258 adds **114 new verified Best PDFs**, one per overview cell. Its measured manifest is "
        f"`{path}` (SHA-256 `{bench.digest(path)}`). The fixed-encoder 392-file publication stays "
        "immutable: 300 representative plain/PNG measurements, focused controls and the two native "
        "experiments retain their actual producer identities. The expanded binary table reuses "
        "114 existing pairs; it does not run or relabel those encoders again. "
        "The [Best regression fixture](../tests/fixtures/best_overview_sizes.json) pins all 114 "
        "new sizes/hashes plus both fixed-policy sizes per cell. Publication checks actual file "
        "hashes, sources, frozen preparations, selection candidates and unchanged semantic graphs. "
        "Best changes lossless storage, so its image-byte check compares exact decoded eligible "
        "samples and exact protected J* payloads, not an impossible unchanged packed encoding. "
        "The graph proof preserves the preparations' prior all-page render verification without "
        "rerendering or repeating image transforms. No-image controls are independently saved.")
    text = replace_once(text,
        "Every\nfinal candidate is checked against its frozen preparation for encoded and\n"
        "decoded image bytes, decoded native streams, geometry, metadata/attachments\n"
        "and all-page no-AA pixels at 72 and 300 DPI.",
        "Fixed-policy\nfinal candidates retain their checks against frozen preparations for encoded/\n"
        "decoded image bytes, native streams and all-page 72/300-DPI pixels. The\n"
        "new Best outputs use exact semantic-graph/sample/J* verification as above.")
    text = replace_once(text, "Reproduce from the repository root, using fresh labels:",
        "Reproduce the Best-only overview from the repository root, using fresh labels:\n\n"
        "```sh\nnice -n 10 ./.venv/bin/python tools/bench_best_overview.py --label <best-label> --workers 2\n"
        "./.venv/bin/python tools/publish_best_overview.py --measurements .tmp/compression-experiments/<best-label>/metrics.json --output .tmp/compression-experiments/<best-publication-label>\n```\n\n"
        "The publisher audits actual files and emits an `apply_patch` patch. The\n"
        "following older commands reproduce the separate Brotli-refresh study;\n"
        "they are not required when changing only the overview policy:")
    return text


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
    source = Path("docs/INTEGRATED_COMPRESSION.md")
    before = source.read_text()
    after = rewrite(before, report, publication, args.measurements)
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
