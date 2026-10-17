"""Publish verified PNG/NATIVE-01 measurements as one integrated Markdown report.

Does not encode PDFs or edit documentation directly. Emits an apply_patch
patch on request, and freezes its input manifests, output and validation proof.
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
    baseline = overview.matrix_markdown(overview.DOCUMENTS, overview.primary_rows(rows), records)
    effects = overview.png_prediction_markdown(overview.DOCUMENTS, rows, records)
    reference, native_effects = residual.tables(overview.DOCUMENTS, residual.ROWS, native["pairs"])
    if len(native["pairs"]) != len(residual.ROWS) * len(overview.DOCUMENTS):
        raise ValueError("Unexpected native A/B measurement inventory")
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
    text = overview.short_table_labels(before)
    # Preserve all existing overview ordering/dividers; insert only the new
    # palette baselines, with minima computed within distinct fidelity groups.
    primary_scope = text.split("## Overview — final complete-file bytes", 1)[1].split(overview.PNG_SECTION, 1)[0]
    measured = {cells(line)[0]: line for line in baseline.splitlines()[2:]}
    updated = []
    extra_native = {overview.display_label(r.label) for r in overview.primary_rows(shared.extension_rows()) if "ffpr" not in r.family}
    extra_ffpr = {overview.display_label(r.label) for r in overview.primary_rows(shared.extension_rows()) if "ffpr" in r.family}
    # The publication puts JBIG2 first here, unlike the raw catalog.
    indexed_ffpr = {overview.display_label(r.label) for r in overview.ROWS if r.family == "indexed-ffpr"}
    first_actual_ffpr = next(cells(item)[0] for item in primary_scope.splitlines()
                             if item.startswith("| ") and cells(item)[0] in indexed_ffpr)
    for line in primary_scope.splitlines():
        label = cells(line)[0] if line.startswith("| ") else None
        if label == first_actual_ffpr:
            updated.extend(item for item in baseline.splitlines()[2:] if cells(item)[0] in extra_native)
        if label == "**Full color**":
            updated.extend(item for item in baseline.splitlines()[2:] if cells(item)[0] in extra_ffpr)
        updated.append(measured.get(label, line))
    text = text.replace(primary_scope, "\n".join(updated).rstrip() + "\n\n", 1)
    scope = text.split(overview.PNG_SECTION, 1)[1].split("\n## ", 1)[0]
    old_table = "\n".join(line for line in scope.splitlines() if line.startswith("|")) + "\n"
    changed = scope.replace(old_table, effects)
    changed = changed.replace(
        "**measured complete saved PDF bytes with PNG prediction**, followed by\n"
        "the signed change from that baseline's measured complete PDF bytes.",
        "**signed percentage change in measured complete saved PDF bytes**\n"
        "from that baseline. Candidate byte counts are omitted here (§243);\n"
        "exact counts remain in the frozen measurement manifests.")
    changed = changed.replace("Bold bytes mean this result is no", "Bold percentages mean this result is no")
    changed = changed.replace("larger than its own baseline, including ties—not a cross-document minimum.",
        "larger than its own baseline, including ties—not a cross-document minimum.\n"
        "Underlined Brotli labels identify that compressor's measured pairs;\n"
        "the observed win/tie/loss counts below are corpus-specific, not a\n"
        "universal claim that prediction is obsolete.")
    changed = changed.replace(
        "are rounded to one decimal place. Bold percentages mean this result is no\n"
        "larger than its own baseline, including ties—not a cross-document minimum.",
        "are rounded to two decimal places. Bold percentages mark displayed\n"
        "negative reductions only—not a cross-document minimum. Exact ties and\n"
        "changes that round to +0.00% are not bold.")
    changed = changed.replace("compressor and save policy are unchanged within each pair.",
        "compressor and save policy are unchanged within each pair. The ON path\n"
        "uses the existing adaptive predictor-15 row selector (minimum absolute\n"
        "signed-byte sum across None/Sub/Up/Average/Paeth), held fixed throughout;\n"
        "these results do not test every possible row-filter selection strategy.")
    changed = changed.replace("its four independently", "its eight independently")
    changed = changed.replace(
        "This first review covers PNG prediction only. Residual-stream rows and\n"
        "the existing focused-scenario measurements below are unchanged.",
        "The table now covers **96 pairs**: BW/Otsu and 5/16/64-color palettes,\n"
        "native-preserving and FFPR, with both general compressors. The 16/64-color\n"
        "rows add coverage, not an exhaustive algorithm search at those palettes.\n"
        "Source palettes can use fewer entries; the BW scan is intentionally\n"
        "measured even when different palette limits produce identical samples.\n\n"
        + "\n".join(f"- **{name}**: {summary[policy]['smaller']} smaller, {summary[policy]['tied']} tied, "
                     f"{summary[policy]['larger']} larger out of 48 measured pairs."
                     for policy, name in (("zopfli", "Zopfli-Flate"), ("brotli", "Brotli")))
        + "\n\nThese counts apply only to this corpus/settings. No-image ties are sanity\n"
        "controls, not image compression wins. The focused measurements below\n"
        "are unchanged; four native 16/64-color cases reuse the very same measured\n"
        "files now included in this expanded overview.")
    text = text.replace(scope, changed, 1)
    ffpr_changes = [p["candidate"]["result"]["complete_pdf_bytes"] - p["reference"]["result"]["complete_pdf_bytes"]
                    for p in native["pairs"] if p["combination"]["family"] != "preserve-images"]
    ffpr_summary = pair_summary([(p["reference"]["result"]["complete_pdf_bytes"],
                                 p["candidate"]["result"]["complete_pdf_bytes"])
                                for p in native["pairs"] if p["combination"]["family"] != "preserve-images"])
    control_summary = pair_summary([(p["reference"]["result"]["complete_pdf_bytes"],
                                    p["candidate"]["result"]["complete_pdf_bytes"])
                                   for p in native["pairs"] if p["combination"]["family"] == "preserve-images"])
    native_section = (residual.SECTION + "\n\n"
        "Plan: **NATIVE-01**, [controlled experiments](COMPRESSION_EXPERIMENTS.md#native-01--nativeresidual-stream-recompression). "
        "One factor changes: standard level-9 Flate versus the named optimized\n"
        "**native/residual-stream encoder**. Encoded image streams, decoded native\n"
        "drawing, preparation, ID framing and final writer settings stay fixed.\n"
        "Classic Flate is a controlled reference, not a restored product option.\n"
        "These seven rows isolate the five specialized FFPR residual cases plus\n"
        "two native-content controls, not another image-codec cross-product.\n\n"
        "### Measured reference bytes — standard Flate native/residual streams\n\n"
        "Each row names the candidate; these cells are its **measured Flate-reference\n"
        "complete-file bytes**. The two preserve-images controls share the same\n"
        "already measured Flate reference for each source.\n\n" + reference + "\n"
        "### Measured candidate bytes and change from that reference\n\n"
        "Each cell is **measured candidate complete-file bytes** plus\n"
        "`100 × (candidate − reference) / reference`. Negative is smaller/better.\n"
        "Bold bytes mean no larger than its own reference, including ties.\n"
        "Rounding is to two decimal places; tiny byte differences can round to\n"
        "+0.00%, so the exact reference and candidate counts remain visible.\n\n" + native_effects + "\n"
        f"Across the **30 FFPR pairs**, complete-file byte changes range from **{min(ffpr_changes):+,} B** "
        f"to **{max(ffpr_changes):+,} B**: **{ffpr_summary['smaller']} smaller, {ffpr_summary['tied']} tied, "
        f"{ffpr_summary['larger']} larger**. These are actual final-file differences, not residual-payload estimates. "
        f"The 12 native-preserving controls give **{control_summary['smaller']} smaller, {control_summary['tied']} tied, "
        f"{control_summary['larger']} larger**; the largest growth is **{control_summary['max_byte_change']:+,} B**. "
        "They retain much more content to recompress; the table measures that\n"
        "contrast. Do not generalize these settings to\n"
        "every PDF. Brotli still requires a supporting reader.\n\n")
    text = text.replace("## What the measurements establish", native_section + "## What the measurements establish", 1)
    text = text.replace("Designer §§210–214/220–240; TODO §§226–242.", "Designer §§210–214/220–244; TODO §§226–246.")
    text = text.replace("verification: 2026-10-16 (America/New_York).", "verification: 2026-10-16–17 (America/New_York).")
    old_intro = next(line for line in text.splitlines() if line.startswith("**Current selected results"))
    text = text.replace(old_intro,
        "**Current selected results after the B114 preparation repair.** "
        "The representative overview now has **204 baseline sizes** and **96 isolated PNG effects** "
        "across six PDFs. The next native/residual A/B experiment adds **42 paired comparisons**. "
        f"Together with the unchanged focused scenarios, **{len(by_path)} distinct actual saved PDFs** support these tables. "
        "Compatible earlier outputs retain their original provenance; only missing cases were encoded. "
        "The BW representative is the eleven-page CCITT NACA TM972 scan, not the already-JBIG2 JFK regression fixture. "
        "B114 is worker-verified, not designer-confirmed acceptance.")
    text = text.replace("Mixed general-compressor pairings are excluded.",
        "Mixed general-compressor pairings are excluded from the algorithm overview.\n"
        "  The isolated native-stream experiment deliberately holds image bytes fixed.")
    text = text.replace("Indexed uses **up to five total colors** in the overview; focused palette\nlimits are 5/16/64.",
        "Indexed uses **up to 5/16/64 total colors**, in separate fidelity groups.\n"
        "The expanded 16/64-color rows are paired PNG controls, not a complete\n"
        "specialized-codec search at each palette limit.")
    text = text.replace("each algorithm group. Indexed canvases use up to five colors, including indexed\nFFPR; full-color rows",
        "each algorithm group. Indexed canvases have separate 5/16/64-color groups,\nincluding indexed FFPR; full-color rows")
    text = text.replace("the eight PNG rows move to the isolated-effect table below (§§238–240).",
        "PNG variants appear in the isolated-effect table below (§§238–242).")
    old_summary = next(line for line in text.splitlines() if line.startswith("- The [isolated PNG-prediction"))
    text = text.replace(old_summary,
        "- The [PNG-prediction table](#png-prediction--measured-effect-versus-baseline) shows **96 six-document pairs**. "
        "Four focused palette cases now reuse those same outputs; six other focused pairs remain outside this table. "
        "The [native/residual A/B experiment](#nativeresidual-streams--measured-effect-versus-flate-reference) "
        "holds encoded images fixed and reports **42 separate Flate-reference comparisons**.")
    inventory = next(line for line in text.splitlines() if line.startswith("The measurement inventory remains"))
    text = text.replace(inventory,
        "The representative inventory is **50 combinations × six PDFs = 300 verified measurements**: "
        "**34 baseline rows / 204 sizes** plus **16 PNG-effect rows / 96 percentages**. "
        "Focused tables still display 87 sizes. NATIVE-01 displays 42 reference and 42 candidate sizes. "
        "That is **375 displayed byte-count cells plus 96 percentage-only cells = 471 result cells**, "
        f"supported by **{len(by_path)} distinct actual complete files**, with no rejected or unmeasured cells. "
        "The original selected study supplied 252 files; PNG coverage adds 80 newly saved files "
        "and reuses 16 focused outputs, while NATIVE-01 adds 30 reference files and reuses its candidates/controls. "
        "No-image treatments are independently saved, not filled by copying a control.")
    anchor = "Historical studies remain untouched"
    text = text.replace(anchor,
        "The §242 extensions are frozen under `.tmp/compression-experiments/`: "
        "`png-palettes-300dpi-20261017/` and `native-residual-300dpi-20261017/`. "
        "Their identities retain the producing implementation, source/tool hashes, original imported records "
        "and a bounded compatibility proof: the earlier bitmap driver's only core difference is removal of "
        "an unused JSON percentage field. No encoder, preparation, saver or validator changed. "
        "Normal changed-code resume remains forbidden. Publication inputs, sources, complete output hashes, "
        "paired statistics and current Markdown are frozen separately under "
        "`.tmp/compression-experiments/publication-20261017/`. "
        "See [experiment plans](COMPRESSION_EXPERIMENTS.md).\n\n" + anchor, 1)
    text = text.replace("./test.sh\n```", "nice -n 10 ./.venv/bin/python tools/bench_png_extension.py --label <png-label>\n"
        "nice -n 10 ./.venv/bin/python tools/bench_residual_streams.py --label <native-label> --existing <selected-manifest>\n```", 1)
    text = text.replace("QPDF 12.2.0 syntax checks pass all **145 selected ordinary-format outputs**; the **107 selected Brotli outputs**",
        f"QPDF 12.2.0 syntax checks pass all **{checks['checked']} selected ordinary-format outputs**; "
        f"the **{checks['unsupported']} selected Brotli outputs**")
    text = text.replace("The fresh full suite after the PNG-only split is\n"
        "**635 passed**, with no expected failures. The 30 PNG-table cases, latest\n"
        "110-test focused run, source-choice/publication coverage and earlier 30-PDF\n"
        "actual subset smoke are recorded in [TEST_PLAN.md](TEST_PLAN.md).",
        "The PNG-only split stage passed **635 tests**, with no expected failures.\n"
        "Current controlled-experiment regressions, complete-suite results, actual\n"
        "save smoke tests and publication audits are recorded in [TEST_PLAN.md](TEST_PLAN.md).")
    # Focused data must not be silently regenerated by this expansion.
    focused = lambda s: s.split("## Focused scenarios", 1)[1].split("## What the measurements establish", 1)[0].split(residual.SECTION, 1)[0].rstrip()
    if focused(text) != overview.short_table_labels(focused(before)):
        raise ValueError("Unexpected focused-scenario change")
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
        target = Path("docs/INTEGRATED_COMPRESSION.md")
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
