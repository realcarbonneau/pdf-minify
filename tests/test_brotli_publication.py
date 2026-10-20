"""Complete measured replacements, table scope and immutable control records."""

from copy import deepcopy
from pathlib import Path
import pytest
import pymupdf as fitz

from tools import publish_brotli_refresh as publication


def record(policy="brotli", variant="jbig2"):
    return dict(document="native", family="bw-images", origin="historical",
                case=dict(prepared=["unchanged"], recipe={"dpi": 300}),
                result=dict(pdf="before.pdf", pdf_sha256="old hash", complete_pdf_bytes=1234,
                            native_policy=policy, image_variant=variant, exact_native=True))


@pytest.mark.parametrize("policy,variant", [("brotli", "jbig2"), ("flate", "brotli-plain"),
                                           ("brotli-9", "preserve-images")])
def test_every_brotli_policy_requires_an_actual_measured_replacement(policy, variant):
    original = record(policy, variant)
    with pytest.raises(KeyError):
        publication.replace_record(original, {})
    unchanged = deepcopy(original)
    evidence = dict(job=dict(result=deepcopy(original["result"])), validation="graph proof",
        result=dict(original["result"], pdf="new/output.pdf", pdf_sha256="new hash",
                    complete_pdf_bytes=1100, brotli_declaration=False))
    result = publication.replace_record(original, {"before.pdf": evidence})
    assert result["case"] == original["case"]
    assert result["result"]["complete_pdf_bytes"] == 1100
    assert result["previous_measurement"]["result"] == original["result"]
    assert original == unchanged
    evidence["job"]["result"]["pdf_sha256"] = "changed"
    with pytest.raises(ValueError, match="historical"):
        publication.replace_record(original, {"before.pdf": evidence})


def test_non_brotli_controls_keep_their_actual_measurement_and_provenance():
    original = record("zopfli")
    result = publication.replace_record(original, {})
    assert result == original and result is not original
    assert "previous_measurement" not in result


def test_table_replacement_is_structural_and_rejects_missing_or_added_tables():
    before = "Heading\n\n| title |\n|---|\n| 1 |\n\nKeep 1 in prose.\n"
    table = "| title |\n|---|\n| 2 |\n"
    assert publication.replace_tables(before, [table]) == before.replace("| 1 |", "| 2 |")
    for tables in ([], [table, table]):
        with pytest.raises(ValueError, match="table"):
            publication.replace_tables(before, tables)


@pytest.mark.parametrize("version", [None, "/2.0"])
def test_final_metadata_save_has_no_artificial_version_or_new_brotli_encoding(tmp_path, monkeypatch, version):
    r = publication.refresh
    source, declared = tmp_path / "source.pdf", tmp_path / "declared.pdf"
    with fitz.open() as doc:
        doc.new_page().insert_text((20, 30), "Native stream")
        if version:
            doc.xref_set_key(doc.pdf_catalog(), "Version", version)
        doc.save(source)
    r.study.pipeline.save_with_spec(str(source), str(declared), dict(
        mode="passthrough", stream_compression="brotli", brotli_declaration=True))
    job = dict(key="test", case=dict(source=str(source), input_sha256=r.file_hash(source),
        mode="passthrough", recipe={}), result=dict(pdf=str(declared), pdf_sha256=r.file_hash(declared),
        complete_pdf_bytes=declared.stat().st_size, image_variant="preserve-images", native_policy="brotli"))
    evidence = r.measure(job, tmp_path / "rerun", {"producer": "test"})
    def no_new_encoding(*args, **kwargs):
        pytest.fail("Metadata finalization must reuse this run's fresh encoded streams")
    monkeypatch.setattr(r, "_ENCODER", no_new_encoding)
    result = publication.finalize_metadata(evidence, tmp_path / "finalized")
    with fitz.open(result["result"]["pdf"]) as doc:
        assert not r.study.streams.brotli_declaration_present(doc)
        if version:
            assert doc.xref_get_key(doc.pdf_catalog(), "Version")[1] == version
            assert result is evidence
        else:
            assert "Version" not in doc.xref_get_keys(doc.pdf_catalog())
            assert result["result"]["complete_pdf_bytes"] == Path(result["result"]["pdf"]).stat().st_size
            assert result["result"]["complete_pdf_bytes"] < evidence["result"]["complete_pdf_bytes"]
            assert publication.finalize_metadata(evidence, tmp_path / "finalized") == result


def test_focused_palette_columns_use_their_own_measured_scenario_family():
    row = publication.overview.Combination("indexed", "brotli-plain", "brotli", "Indexed + Brotli")
    overview_record = dict(document="art", family="indexed", result=dict(
        image_variant="brotli-plain", native_policy="brotli", complete_pdf_bytes=800))
    focused = dict(scenario=dict(key="art-16", family="indexed"), result=dict(
        image_variant="brotli-plain", native_policy="brotli", complete_pdf_bytes=1200))
    result = publication.focused_table(dict(records=[overview_record], extras=[focused]),
        [("a5", "5 colors", "art"), ("a16", "16 colors", "art-16")], [row])
    assert "| Indexed + Brotli | **800** | **1,200** |" in result


def test_native_component_changes_both_brotli_levels_but_never_historical_timings():
    policies = ["none", "flate-fast", "flate", "zopfli", "brotli-9", "brotli", "lzw", "runlength"]
    original = [dict(source="examples.pdf", results=[dict(policy=p, complete_pdf_bytes=1000 + i)
                                                   for i, p in enumerate(policies)])]
    measurements = {str(publication.refresh.NATIVE.parent / f"examples.{p}.pdf"):
                    dict(result=dict(complete_pdf_bytes=n)) for p, n in (("brotli-9", 800), ("brotli", 700))}
    text = "### Complete final PDF sizes (bytes)\n\n| Policy | Source |\n|---|---:|\n" + "".join(
        f"| {p} | {1000+i:,} |\n" for i, p in enumerate(policies)) + "\n### Median native\n\n| Brotli | 0.123 |\n"
    result = publication.component_tables(text, original, measurements, native=True)
    assert "| brotli-9 | 800 |" in result and "| brotli | 700 |" in result
    assert "| zopfli | 1,003 |" in result
    assert result.split("### Median native", 1)[1] == text.split("### Median native", 1)[1]


def test_png_winner_audit_compares_whole_files_and_preserves_reader_tier_counterexamples():
    values = [dict(image_variant=v, native_policy=p, complete_pdf_bytes=n) for v, p, n in (
        ("brotli-plain", "brotli", 700), ("brotli-png", "brotli", 800),
        ("zopfli-plain", "zopfli", 1000), ("zopfli-png", "zopfli", 900))]
    assert publication.prediction_winners([values]) == dict(unique_wins=0, tied_minima=0, larger=2)
    assert publication.prediction_winners([values], exclude_brotli=True) == dict(
        unique_wins=1, tied_minima=0, larger=0)


def test_focused_and_ffpr_cells_are_filled_by_curated_page_row_ids():
    from tools import benchmark_tables as tables
    page = tables.PAGE.read_text()
    specs = publication.focused_specs()
    assert len(specs) == 6
    for table_id, columns, rows in specs:
        table = tables.read_table(page, table_id)
        ids = [publication.focused_row_id(r) for r in rows]
        assert len(set(ids)) == len(ids) and set(ids) == set(table.rows), table_id
        assert len(table.header) == len(columns) + 1, table_id
    binary = tables.read_table(page, "zopfli-vs-brotli").rows
    keys = {publication.recipe_key(r.family, r.variant, r.native) for r in publication.ffpr.ROWS}
    assert keys == {"bw-ffpr-jbig2", "indexed-ffpr-jbig2", "jpeg-ffpr", "jpx-lossy-ffpr", "jpx-lossless-ffpr"}
    assert keys <= set(binary)


def test_focused_row_ids_drop_the_column_varied_palette_or_threshold():
    row = publication.overview.Combination
    assert publication.focused_row_id(row("indexed", "brotli-png", "brotli", "x")) == "indexed.brotli.png"
    assert publication.focused_row_id(row("bw-images", "zopfli-plain", "zopfli", "x")) == "bw.zopfli"
    assert publication.focused_row_id(row("indexed", "jbig2", "brotli", "x")) == "indexed-jbig2.brotli"
    assert publication.focused_row_id(row("preserve-images", "preserve-images", "flate", "x")) == "reference.classic"
    with pytest.raises(ValueError):
        publication.focused_row_id(row("indexed", "zopfli-other", "zopfli", "x"))
