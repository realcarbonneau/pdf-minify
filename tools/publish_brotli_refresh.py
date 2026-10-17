"""Publish the complete default-OFF Brotli rerun, without invoking encoders.

Frozen input manifests and non-Brotli controls remain immutable. This tool
checks actual file hashes/sizes, updates every affected table and emits an
apply_patch patch; it never edits tracked documentation or fixtures directly.
"""

import argparse
from copy import deepcopy
from dataclasses import asdict, replace
import difflib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import refresh_brotli_tables as refresh
from tools import publish_compression_experiments as old_publication
from tools import bench_compression_scenarios as scenarios
from tools import bench_ffpr_compressors as ffpr

overview, residual = old_publication.overview, old_publication.residual


def has_brotli(result):
    return (result["native_policy"].startswith("brotli") or
            result["image_variant"].startswith("brotli"))


def replace_record(record, measurements):
    """Keep preparation/old producer provenance; substitute only a measured save."""
    result = deepcopy(record)
    before = record["result"]
    if not has_brotli(before):
        return result
    evidence = measurements[before["pdf"]]
    if (evidence["job"]["result"]["pdf_sha256"] != before["pdf_sha256"] or
            evidence["job"]["result"]["complete_pdf_bytes"] != before["complete_pdf_bytes"]):
        raise ValueError("Changed historical measured result")
    result["previous_measurement"] = dict(origin=record.get("origin"), result=deepcopy(before))
    result["result"].update(evidence["result"])
    result["origin"] = str(Path(evidence["result"]["pdf"]).parent / "metrics.json")
    result["validation"] = evidence["validation"]
    return result


def verify_refresh(path):
    data = json.loads(path.read_text())
    if (not data["complete"] or data.get("errors") or
            len(data["results"]) != data["identity"]["job_count"]):
        raise ValueError("Incomplete all-Brotli rerun")
    for source, expected in data["identity"]["inputs"].items():
        if refresh.file_hash(source) != expected:
            raise ValueError("Changed frozen input manifest")
    if refresh.file_hash(path.parent / "implementation.py") != data["identity"]["implementation"]:
        raise ValueError("Changed frozen rerun implementation")
    for original, evidence in data["results"].items():
        if evidence["identity"] != data["identity"] or evidence["job"]["result"]["pdf"] != original:
            raise ValueError("Changed rerun proof/identity")
        result = evidence["result"]
        if (result["brotli_declaration"] is not False or
                Path(result["pdf"]).stat().st_size != result["complete_pdf_bytes"] or
                refresh.file_hash(result["pdf"]) != result["pdf_sha256"]):
            raise ValueError("Changed declaration-OFF measured PDF")
    return data


def finalize_metadata(evidence, directory):
    """Remove the proven benchmark-owned null version marker, then measure.

    The first-pass xref setter serialized absent Version as /Version null.
    Delete that key structurally only when original-source/producer evidence
    proves its absence. Reuse this rerun's freshly encoded bytes, not old
    declaration-ON payloads. The shared saver remains the only final writer.
    """
    directory = Path(directory)
    checkpoint = directory / "metrics.json"
    proof_hash = refresh.digest(json.dumps(evidence, sort_keys=True).encode())
    if checkpoint.exists():
        saved = json.loads(checkpoint.read_text())
        result = saved["result"]
        if (saved["finalization"]["input_proof_sha256"] != proof_hash or
                saved["finalization"]["implementation"] != refresh.file_hash(__file__) or
                refresh.file_hash(result["pdf"]) != result["pdf_sha256"] or
                Path(result["pdf"]).stat().st_size != result["complete_pdf_bytes"]):
            raise ValueError("Changed frozen metadata finalization")
        return saved
    result, metadata = evidence["result"], evidence["metadata"]
    if not (metadata["declared_before"] and metadata["catalog_before"] == "/2.0" and
            metadata["original_catalog_version"] == "null"):
        return evidence
    with refresh.fitz.open(result["pdf"]) as doc:
        if doc.xref_get_key(doc.pdf_catalog(), "Version")[0] != "null":
            raise ValueError("Unexpected finalization version marker")
        m = refresh.fitz.mupdf
        native = m.pdf_document_from_fz_document(doc.this)
        m.pdf_dict_dels(m.pdf_dict_gets(m.pdf_trailer(native), "Root"), "Version")
        graph, images = refresh.rendered_graph(doc), refresh.image_signature(doc)
        policy = result["native_policy"]
        # This file already passed fresh encoding and exact-graph verification.
        # Seed a cache only from its own native payloads, at its actual level.
        cache = {}
        if policy.startswith("brotli"):
            for xref in refresh.study.streams.native_stream_xrefs(doc):
                data = doc.xref_stream(xref)
                if data:
                    if doc.xref_get_key(xref, "Filter")[1] != "/BrotliDecode":
                        raise ValueError("Unexpected freshly encoded native filter")
                    cache[(9 if policy == "brotli-9" else 11, refresh.digest(data))] = doc.xref_stream_raw(xref)
        def fresh_cache_only(data, level):
            return cache[(level, refresh.digest(data))]  # Never fall back to a historical encoding.
        directory.mkdir(parents=True)
        target = directory / "declaration-off.pdf"
        previous_encoder = refresh.study.streams._brotli
        refresh.study.streams._brotli = fresh_cache_only
        work = refresh.study.pipeline._ENCODE_WORKDIR.set(str(directory))
        stream = refresh.study.pipeline._STREAM_POLICY.set(policy)
        declaration = refresh.study.pipeline._BROTLI_DECLARATION.set(False)
        try:
            refresh.study.pipeline._save_optimized_pdf(doc, str(target), no_new_id=True, subset_fonts=False)
        finally:
            refresh.study.streams._brotli = previous_encoder
            refresh.study.pipeline._ENCODE_WORKDIR.reset(work)
            refresh.study.pipeline._STREAM_POLICY.reset(stream)
            refresh.study.pipeline._BROTLI_DECLARATION.reset(declaration)
    with refresh.fitz.open(target) as doc:
        if (refresh.rendered_graph(doc) != graph or refresh.image_signature(doc) != images or
                "Version" in doc.xref_get_keys(doc.pdf_catalog()) or
                refresh.study.streams.brotli_declaration_present(doc)):
            raise ValueError("Metadata-only finalization changed document content")
    saved = dict(evidence, result=dict(result, pdf=str(target), pdf_sha256=refresh.file_hash(target),
                                      complete_pdf_bytes=target.stat().st_size),
        finalization=dict(input_proof_sha256=proof_hash, input_result=deepcopy(result),
                          implementation=refresh.file_hash(__file__),
                          rendered_graph_sha256=graph, freshly_encoded_native_payloads_reused=len(cache),
                          factor="remove benchmark-owned absent-version null entry; no new encoding"))
    checkpoint.write_text(json.dumps(saved, indent=2) + "\n")
    return saved


def refreshed_publication(data):
    original = json.loads(refresh.PUBLICATION.read_text())
    result = dict(rows=deepcopy(original["rows"]), implementation=refresh.file_hash(__file__),
                  previous_publication=dict(path=str(refresh.PUBLICATION), sha256=refresh.file_hash(refresh.PUBLICATION),
                                            inputs=original["inputs"], counts=original["counts"]))
    for key in ("records", "extras"):
        result[key] = [replace_record(r, data["results"]) for r in original[key]]
    result["native_pairs"] = [dict(p, **{role: replace_record(p[role], data["results"])
                                       for role in ("reference", "candidate")})
                              for p in original["native_pairs"]]
    old_ffpr = json.loads(refresh.FFPR.read_text())
    result["ffpr_pairs"] = [dict(p, **{role: replace_record(p[role], data["results"])
                                     for role in ("reference", "candidate")})
                            for p in old_ffpr["pairs"]]
    for pair in result["ffpr_pairs"]:
        pair["accounting"] = ffpr.account_pair(pair)
    unique = {}
    for record in (result["records"] + result["extras"] +
                   [p[k] for p in result["native_pairs"] + result["ffpr_pairs"]
                    for k in ("reference", "candidate")]):
        overview.validate_record(record["case"], record["result"])
        unique[record["result"]["pdf"]] = record
    if len(unique) != 392 or sum(has_brotli(r["result"]) for r in unique.values()) != 177:
        raise ValueError("Changed integrated publication inventory")
    rows = tuple(overview.Combination(**r) for r in result["rows"])
    result["png_summary"] = old_publication.png_summary(rows, result["records"])
    result["pair_validation"] = old_publication.verify_fixed_pair_streams(
        rows, result["records"], result["native_pairs"] + result["ffpr_pairs"])
    result["ffpr_summary"] = old_publication.pair_summary([
        (p["reference"]["result"]["complete_pdf_bytes"], p["candidate"]["result"]["complete_pdf_bytes"])
        for p in result["ffpr_pairs"]])
    result["native_summary"] = {kind: old_publication.pair_summary([
        (p["reference"]["result"]["complete_pdf_bytes"], p["candidate"]["result"]["complete_pdf_bytes"])
        for p in result["native_pairs"] if (p["combination"]["family"] == "preserve-images") == native])
        for kind, native in (("controls", True), ("ffpr", False))}
    result["counts"] = dict(actual_pdfs=len(unique), brotli_remeasured=177, unchanged_controls=215)
    return result


def replace_tables(scope, tables):
    """Replace entire tables in order, never number-substitute unrelated cells."""
    output, index, active = [], 0, False
    for line in scope.splitlines(keepends=True):
        if line.startswith("|"):
            if not active:
                if index >= len(tables):
                    raise ValueError("Unexpected existing table")
                output.append(tables[index])
                index += 1
                active = True
        else:
            active = False
            output.append(line)
    if index != len(tables):
        raise ValueError("Missing existing table")
    return "".join(output)


def section(text, heading, tables):
    before, scope = text.split(heading, 1)
    stop = scope.find("\n## ")
    body, after = (scope[:stop], scope[stop:]) if stop >= 0 else (scope, "")
    return before + heading + replace_tables(body, tables) + after


def focused_table(publication, specs, rows):
    """Columns select actual overview or focused records, sharing fidelity groups."""
    documents, records = [], []
    for key, label, source in specs:
        documents.append(overview.Document(key, label, "unused"))
        collection, field, value = ((publication["records"], "document", source) if
                                    source in {d.key for d in overview.DOCUMENTS} else
                                    (publication["extras"], "scenario", source.removeprefix("extra:")))
        for record in collection:
            matches = record[field] == value if field == "document" else record[field]["key"] == value
            if matches:
                records.append(dict(record, document=key, family=(record["family"] if field == "document"
                                                                 else record["scenario"]["family"])))
    return overview.matrix_markdown(documents, rows, records)


def integrated_tables(text, publication):
    rows = tuple(overview.Combination(**r) for r in publication["rows"])
    baseline = overview.matrix_markdown(overview.DOCUMENTS, overview.primary_rows(rows), publication["records"])
    rendered = {old_publication.cells(line)[0]: line for line in baseline.splitlines()[2:]}
    before, scope = text.split("## Overview — final complete-file bytes", 1)
    body, after = scope.split(overview.PNG_SECTION, 1)
    found = set()
    lines = []
    for line in body.splitlines():
        label = old_publication.cells(line)[0] if line.startswith("| ") else None
        if label in rendered:
            found.add(label)
        lines.append(rendered.get(label, line))
    if found != set(rendered):
        raise ValueError("Overview row selection/order changed")
    text = before + "## Overview — final complete-file bytes" + "\n".join(lines) + "\n\n" + overview.PNG_SECTION + after
    text = section(text, overview.PNG_SECTION, [overview.png_prediction_markdown(
        overview.DOCUMENTS, rows, publication["records"])])
    text = section(text, ffpr.SECTION, [ffpr.effect_table(overview.DOCUMENTS, ffpr.ROWS, publication["ffpr_pairs"])])
    photo_rows = tuple(r for r in overview.ROWS if r.family in (
        "preserve-images", "jpeg-q50", "jpx-r192", "jpx-lossless", "jpeg-q50-ffpr", "jpx-r192-ffpr", "jpx-lossless-ffpr"))
    indexed_rows = tuple(replace(r, label=r.label.replace(" 5 colors", ""))
                         for r in overview.ROWS if r.family == "indexed")
    bw_rows = tuple(r for r in overview.ROWS if r.family == "bw-images")
    native_rows = tuple(r for r in overview.ROWS if r.family == "preserve-images")
    tables = [
        focused_table(publication, [("photos", "Color photos", "photos")], photo_rows),
        focused_table(publication, [("art", "5 colors", "art"), ("a16", "16 colors", "art-16"),
                                    ("a64", "64 colors", "art-64")], indexed_rows),
        focused_table(publication, [("mixed", "5 colors", "mixed"), ("m16", "16 colors", "mixed-16"),
                                    ("m64", "64 colors", "mixed-64")], indexed_rows),
        focused_table(publication, [("scan", "NACA TM972", "scan"), ("naca", "NACA formulas", "naca")], bw_rows),
        focused_table(publication, [("art", "Otsu", "art"), ("t180", "Simple T180", "art-t180"),
                                    ("t210", "Simple T210", "art-t210")], bw_rows),
        focused_table(publication, [("native", "Form W-9", "native"), ("941", "Form 941", "form941"),
                                    ("kepler", "NASA Kepler", "extra:kepler")], native_rows)]
    # Preserve the existing descriptive column headings; only measured cells change.
    scope = text.split("## Focused scenarios", 1)[1].split(residual.SECTION, 1)[0]
    headers = [line for line in scope.splitlines() if line.startswith("| ") and
               ("Algorithm combination" in line or "Combination |" in line)]
    if len(headers) != 6:
        raise ValueError("Changed focused table headers")
    tables = [header + "\n" + table.split("\n", 1)[1] for header, table in zip(headers, tables)]
    text = section(text, "## Focused scenarios", tables)
    text = section(text, residual.SECTION, list(residual.tables(
        overview.DOCUMENTS, residual.ROWS, publication["native_pairs"])))
    return text


def component_tables(text, original, measurements, native=False):
    if native:
        policies = ("none", "flate-fast", "flate", "zopfli", "brotli-9", "brotli", "lzw", "runlength")
        scope = text.split("### Complete final PDF sizes (bytes)", 1)[1].split("### Median native", 1)[0]
        lines = [line for line in scope.splitlines() if line.startswith("| ")]
        if len(lines) != 9:
            raise ValueError("Changed native component table")
        table = [lines[0], "|---|---:|---:|---:|---:|"]
        for line, policy in zip(lines[1:], policies):
            values = []
            for row in original:
                item = next(r for r in row["results"] if r["policy"] == policy)
                path = str(refresh.NATIVE.parent / f"{Path(row['source']).stem}.{policy}.pdf")
                values.append(measurements[path]["result"]["complete_pdf_bytes"] if policy.startswith("brotli")
                              else item["complete_pdf_bytes"])
            table.append("| " + old_publication.cells(line)[0] + " | " + " | ".join(f"{v:,}" for v in values) + " |")
        before, after = text.split(scope, 1)
        return before + replace_tables(scope, ["\n".join(table) + "\n"]) + after
    sections = [("### Indexed color versus colored JBIG2", "indexed"),
                ("### BW image layer and full-page rasterization", "bw")]
    for heading, kind in sections:
        start = text.index(heading)
        stop = text.find("\n### ", start + len(heading))
        scope = text[start:stop] if stop >= 0 else text[start:]
        lines = [line for line in scope.splitlines() if line.startswith("| ")]
        selected = [row for row in original if row["mode"].startswith(kind)]
        if len(lines) != len(selected) + 1:
            raise ValueError("Changed bitmap component table")
        table = [lines[0], "|---|" + "---:|" * 7]
        for line, row in zip(lines[1:], selected):
            values = []
            for variant in refresh.study.images.VARIANTS[1:]:
                item = next(r for r in row["results"] if r["variant"] == variant)
                values.append(measurements[item["pdf"]]["result"]["complete_pdf_bytes"] if variant.startswith("brotli")
                              else item["complete_pdf_bytes"])
            cells = [f"**{v:,}**" if v == min(values) else f"{v:,}" for v in values]
            table.append("| " + old_publication.cells(line)[0] + " | " + " | ".join(cells) + " |")
        text = text[:start] + replace_tables(scope, ["\n".join(table) + "\n"]) + (text[stop:] if stop >= 0 else "")
    return text


def fixtures(publication, manifest_hash):
    records = {(r["document"], r["family"], r["result"]["image_variant"], r["result"]["native_policy"]): r
               for r in publication["records"]}
    rows = tuple(overview.Combination(**r) for r in publication["rows"])
    png = dict(publication_sha256=manifest_hash, original_publication_sha256=refresh.file_hash(refresh.PUBLICATION),
               brotli_declaration=False,
               documents=[d.key for d in overview.DOCUMENTS], rows=[])
    for plain, predicted in overview.png_pairs(rows):
        png["rows"].append(dict(label=overview.display_label(plain.label), **{
            key: [records[(d.key, r.family, r.variant, r.native)]["result"]["complete_pdf_bytes"]
                  for d in overview.DOCUMENTS] for key, r in (("baseline", plain), ("png", predicted))}))
    ffpr_fixture = dict(publication_sha256=manifest_hash, brotli_declaration=False, documents=png["documents"], rows=[])
    for row, label in zip(ffpr.ROWS, ffpr.LABELS):
        pairs = {p["document"]: p for p in publication["ffpr_pairs"] if p["combination"]["family"] == row.family}
        ffpr_fixture["rows"].append(dict(label=label, **{key: [pairs[d.key][role]["result"]["complete_pdf_bytes"]
            for d in overview.DOCUMENTS] for key, role in (("brotli", "reference"), ("zopfli", "candidate"))}))
    return {"tests/fixtures/png_prediction_sizes.json": png,
            "tests/fixtures/ffpr_compressor_sizes.json": ffpr_fixture}


def prediction_winners(groups, *, exclude_brotli=False):
    """Whole-file winners within a single source and fidelity, not payload ranks."""
    counts = dict(unique_wins=0, tied_minima=0, larger=0)
    for records in groups:
        eligible = [r for r in records if not (exclude_brotli and has_brotli(r))]
        minimum = min(r["complete_pdf_bytes"] for r in eligible)
        tied = sum(r["complete_pdf_bytes"] == minimum for r in eligible)
        for result in eligible:
            if not result["image_variant"].endswith("-png"):
                continue
            key = ("larger" if result["complete_pdf_bytes"] > minimum else
                   "unique_wins" if tied == 1 else "tied_minima")
            counts[key] += 1
    return counts


def measured_analysis(publication, data):
    records, extras = publication["records"], publication["extras"]
    main = [[r["result"] for r in records if (r["document"], r["family"]) == key]
            for key in sorted({(r["document"], r["family"]) for r in records})]
    focused = [[r["result"] for r in extras if r["scenario"]["key"] == key]
               for key in sorted({r["scenario"]["key"] for r in extras})]
    components = []
    for row in json.loads(refresh.IMAGE.read_text()):
        results = []
        for item in row["results"]:
            if item["variant"] == "current-flate":
                continue  # Identical reference, not a second independent algorithm.
            result = dict(item, image_variant=item["variant"], native_policy="flate")
            if has_brotli(result):
                result.update(data["results"][item["pdf"]]["result"])
            results.append(result)
        components.append(dict(source=row["source"], mode=row["mode"], dpi=row["dpi"],
                               colors=row["colors"], threshold=row["threshold"], results=results))
    return dict(png=dict(representative=prediction_winners(main),
                         focused=prediction_winners(focused),
                         supporting=prediction_winners([r["results"] for r in components]),
                         representative_without_brotli=prediction_winners(main, exclude_brotli=True)),
                supporting_image=components,
                ffpr_accounting=[dict(document=p["document"], family=p["combination"]["family"],
                                      accounting=p["accounting"]) for p in publication["ffpr_pairs"]])


def patch(files):
    result = ["*** Begin Patch\n"]
    for path, after in files.items():
        before = Path(path).read_text()
        if before == after:
            continue
        result.append(f"*** Update File: {path}\n")
        result.extend(list(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True)))[2:])
    result.append("*** End Patch\n")
    return "".join(result)


def run(path, folder):
    data = verify_refresh(path)
    data["results"] = {original: finalize_metadata(evidence, folder / "finalized" / evidence["job"]["key"])
                       for original, evidence in data["results"].items()}
    folder.mkdir(parents=True, exist_ok=True)
    finalized = folder / "measurements.json"
    finalized.write_text(json.dumps(data, indent=2) + "\n")
    (folder / "implementation.py").write_bytes(Path(__file__).read_bytes())
    publication = refreshed_publication(data)
    analysis = measured_analysis(publication, data)
    (folder / "analysis.json").write_text(json.dumps(analysis, indent=2) + "\n")
    publication["brotli_refresh"] = dict(manifest=str(path), sha256=refresh.file_hash(path), identity=data["identity"])
    publication["brotli_refresh"]["finalization_implementation"] = refresh.file_hash(__file__)
    publication["brotli_refresh"].update(finalized_manifest=str(finalized), finalized_sha256=refresh.file_hash(finalized))
    target = folder / "publication.json"
    content = json.dumps(publication, indent=2) + "\n"
    if target.exists() and target.read_text() != content:
        raise ValueError("Changed frozen refreshed publication")
    target.write_text(content)
    outputs = {"docs/INTEGRATED_COMPRESSION.md": integrated_tables(
        Path("docs/INTEGRATED_COMPRESSION.md").read_text(), publication)}
    for name, source, native in (("IMAGE_STREAM_COMPRESSION", refresh.IMAGE, False),
                                 ("NATIVE_STREAM_COMPRESSION", refresh.NATIVE, True)):
        doc = f"docs/{name}.md"
        outputs[doc] = component_tables(Path(doc).read_text(), json.loads(source.read_text()), data["results"], native)
    outputs.update({p: json.dumps(f, indent=2) + "\n" for p, f in fixtures(publication, refresh.file_hash(target)).items()})
    (folder / "tables.patch").write_text(patch(outputs))
    print(json.dumps(dict(publication=str(target), sha256=refresh.file_hash(target),
        counts=publication["counts"], png=publication["png_summary"], ffpr=publication["ffpr_summary"],
        native=publication["native_summary"], patch=str(folder / "tables.patch")), indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measurements", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.measurements, args.output)
