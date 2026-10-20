"""Publish the complete default-OFF Brotli rerun, without invoking encoders.

Frozen input manifests and non-Brotli controls remain immutable. This tool
checks actual file hashes/sizes, fills the measured value cells of every
affected benchmark table by table/row ID and emits an apply_patch patch; it
never edits tracked documentation or fixtures directly, and never writes
prose, labels or headers of the hand-curated benchmark page.
"""

import argparse
from copy import deepcopy
import difflib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import refresh_brotli_tables as refresh
from tools import publish_compression_experiments as old_publication
from tools import bench_compression_scenarios as scenarios
from tools import bench_ffpr_compressors as ffpr
from tools import benchmark_tables as tables
from tools.publish_best_overview import fixed_row_id, recipe_key

overview, residual = old_publication.overview, old_publication.residual
# Focused palette/threshold tables vary the count/threshold by column, so
# their row IDs name the transform without it (`indexed.brotli.png`).
FOCUSED_BASES = {"indexed": "indexed", "bw-images": "bw"}


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


def focused_row_id(row):
    """Row ID of a focused-table combination; see FOCUSED_BASES."""
    base = FOCUSED_BASES.get(row.family)
    if base is None:
        return fixed_row_id(row.family, row.variant, row.native)
    if row.variant == "jbig2":
        return f"{base}-jbig2.{row.native}"
    predictor = row.variant.removeprefix(f"{row.native}-")
    if predictor not in ("plain", "png"):
        raise ValueError(f"Unexpected focused combination: {row.family}/{row.variant}")
    return f"{base}.{row.native}" + (".png" if predictor == "png" else "")


def focused_specs():
    """(table ID, measured columns, combinations) of the six focused tables."""
    photo_rows = tuple(r for r in overview.ROWS if r.family in (
        "preserve-images", "jpeg-q50", "jpx-r192", "jpx-lossless", "jpeg-q50-ffpr", "jpx-r192-ffpr", "jpx-lossless-ffpr"))
    indexed_rows = tuple(r for r in overview.ROWS if r.family == "indexed")
    bw_rows = tuple(r for r in overview.ROWS if r.family == "bw-images")
    native_rows = tuple(r for r in overview.ROWS if r.family == "preserve-images")
    return (
        ("focused-photos", [("photos", "Color photos", "photos")], photo_rows),
        ("focused-artwork", [("art", "5 colors", "art"), ("a16", "16 colors", "art-16"),
                             ("a64", "64 colors", "art-64")], indexed_rows),
        ("focused-mixed", [("mixed", "5 colors", "mixed"), ("m16", "16 colors", "mixed-16"),
                           ("m64", "64 colors", "mixed-64")], indexed_rows),
        ("focused-scan", [("scan", "NACA TM972", "scan"), ("naca", "NACA formulas", "naca")], bw_rows),
        ("focused-thresholds", [("art", "Otsu", "art"), ("t180", "Simple T180", "art-t180"),
                                ("t210", "Simple T210", "art-t210")], bw_rows),
        ("focused-native", [("native", "Form W-9", "native"), ("941", "Form 941", "form941"),
                            ("kepler", "NASA Kepler", "extra:kepler")], native_rows))


def table_values(publication):
    """Measured cells of every table this publication supplies, by table/row ID."""
    rows = tuple(overview.Combination(**r) for r in publication["rows"])
    values = old_publication.table_values(rows, publication["records"], publication["native_pairs"])
    values["zopfli-vs-brotli"] = tables.keyed_rows(
        ffpr.effect_table(overview.DOCUMENTS, ffpr.ROWS, publication["ffpr_pairs"]),
        [recipe_key(r.family, r.variant, r.native) for r in ffpr.ROWS])
    for table_id, specs, combinations in focused_specs():
        values[table_id] = tables.keyed_rows(focused_table(publication, specs, combinations),
                                             [focused_row_id(r) for r in combinations])
    return values


def integrated_tables(text, publication):
    """Fill measured cells only; labels, headers and prose stay curated."""
    for table_id, cells in table_values(publication).items():
        text = tables.fill(text, table_id, cells)
    # The later LOSSY-05 controls supersede this study's q50/r192 cells.
    from tools.publish_lossy_controls import apply_current
    return apply_current(text)


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
    outputs = {tables.PAGE.as_posix(): integrated_tables(tables.PAGE.read_text(), publication)}
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
