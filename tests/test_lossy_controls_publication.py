"""Current-standard table overlay is complete, scoped, idempotent and measured."""

from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path

import pytest

from tools import benchmark_tables as tables
from tools import publish_lossy_controls as publisher


def proof():
    result = dict(designer_ruling=284, quality=75, dpi=300,
                  jpx_quality_mapping="jpeg-matched-tile-psnr-v1",
                  documents=[asdict(d) for d in publisher.controls.lossy.DOCUMENTS], rows=[])
    for force in (False, True):
        for mode in publisher.controls.lossy.MODES:
            for policy in (("zopfli", "brotli", "flate") if force else ("zopfli", "brotli")):
                result["rows"].append(dict(mode=mode, force_raster=force, policy=policy,
                                           label=publisher.controls.combination(mode, force, policy).label,
                                           sizes=[1000 + len(result["rows"])] * 6))
    return result


AFFECTED = {
    "zopfli-vs-brotli": {"jpeg", "jpx-lossy", "jpeg-ffpr", "jpx-lossy-ffpr"},
    "fixed-controls": {f"{key}.{policy}" for key in ("jpeg", "jpx-lossy", "jpeg-ffpr", "jpx-lossy-ffpr")
                       for policy in ("zopfli", "brotli")},
    "focused-photos": {"jpeg.zopfli", "jpeg.brotli", "jpx-lossy.zopfli", "jpx-lossy.brotli",
                       "jpeg-ffpr.zopfli", "jpx-lossy-ffpr.zopfli"},
    "residual-reference": {"jpeg-ffpr.zopfli", "jpx-lossy-ffpr.zopfli"},
    "residual-effect": {"jpeg-ffpr.zopfli", "jpx-lossy-ffpr.zopfli"},
}


def test_all_twenty_two_affected_rows_update_without_touching_other_cells_or_text():
    original = tables.PAGE.read_text()
    updated = publisher.rewrite_tables(original, proof())
    assert publisher.rewrite_tables(updated, proof()) == updated
    assert sum(len(rows) for rows in AFFECTED.values()) == 22
    changed = set()
    for table_id in tables.table_ids(original):
        before, after = (tables.read_table(text, table_id) for text in (original, updated))
        assert (before.header, before.labels, list(before.rows)) == (after.header, after.labels, list(after.rows))
        changed |= {(table_id, key) for key in before.rows if before.rows[key] != after.rows[key]}
    assert changed == {(table_id, key) for table_id, keys in AFFECTED.items() for key in keys}
    # Only those 22 lines differ; prose and every other line stay byte-identical.
    diff = [(a, b) for a, b in zip(original.splitlines(), updated.splitlines(), strict=True) if a != b]
    assert len(diff) == 22


@pytest.mark.parametrize("bad", ["quality", "mapping", "missing", "duplicate", "size", "label", "columns"])
def test_incomplete_old_or_estimated_data_cannot_be_relabelled_current(bad):
    value = proof()
    if bad == "quality":
        value["quality"] = 50
    elif bad == "mapping":
        value["jpx_quality_mapping"] = "darktable-rate-v1"
    elif bad == "missing":
        value["rows"].pop()
    elif bad == "duplicate":
        value["rows"][-1] = deepcopy(value["rows"][0])
    elif bad == "size":
        value["rows"][0]["sizes"][0] = 1000.5
    elif bad == "label":
        value["rows"][0]["label"] = "JPEG q50"
    else:
        value["rows"][0]["sizes"] = [1000]
    with pytest.raises(ValueError):
        publisher.validate_proof(value)


def test_fixed_overlay_does_not_mislabel_old_best_bytes():
    original = dict(family="jpeg-q50", variant="jpeg-q50", label="JPEG q50",
                    best=[500]*6, pdf_sha256=["old"]*6, zopfli=[400]*6, brotli=[300]*6,
                    fixed_labels={"zopfli":"old", "brotli":"old"})
    changed = publisher.updated_fixed_row(original, proof())
    assert changed["label"] == "JPEG q75" and changed["family"] == "jpeg-q75"
    assert "best" not in changed and "pdf_sha256" not in changed
    assert original["label"] == "JPEG q50" and original["best"] == [500]*6


@pytest.mark.parametrize("table_id", sorted(AFFECTED))
def test_missing_table_or_row_cannot_silently_skip_an_affected_table(table_id):
    text = tables.PAGE.read_text()
    with pytest.raises(ValueError, match=f"Missing benchmark table tag: {table_id}"):
        publisher.rewrite_tables(text.replace(f"<!-- table: {table_id} -->", ""), proof())
    row_id = sorted(AFFECTED[table_id])[0]
    table = tables.read_table(text, table_id)
    tagged = f"<!-- row: {row_id} --> {table.labels[row_id]}"
    start = text.index(tagged, text.index(f"<!-- table: {table_id} -->"))
    line_start, line_end = text.rindex("\n", 0, start) + 1, text.index("\n", start) + 1
    with pytest.raises(ValueError, match=f"Missing row {row_id}"):
        publisher.rewrite_tables(text[:line_start] + text[line_end:], proof())


def test_actual_complete_controls_drive_every_active_lossy_table():
    current = json.loads(publisher.FIXTURE.read_text())
    publisher.validate_proof(current)
    assert current["measured_manifest_sha256"] == "674a9e88d9f5cc7f0ea9a350864fa2155f448589a1d12741723a435991fedb83"
    assert current["unchanged_publication_sha256"] == publisher.best.PUBLICATION_SHA256
    baseline = json.loads(Path("tests/fixtures/lossy_quality_sizes.json").read_text())
    assert current["baseline_sha256"] == baseline["measured_manifest_sha256"]
    assert sum(len(row["sizes"]) for row in current["rows"]) == 60
    for row in current["rows"]:
        for field in ("pdf_sha256", "base_sha256"):
            assert len(row[field]) == 6 and all(len(h) == 64 for h in row[field])
    report = tables.PAGE.read_text()
    assert publisher.rewrite_tables(report, current) == report
    assert publisher.apply_current(report) == report
    assert len(current["ffpr_accounting"]) == 12
    expected = {(d.key, mode) for d in publisher.controls.lossy.DOCUMENTS for mode in publisher.controls.lossy.MODES}
    assert {(r["document"], r["mode"]) for r in current["ffpr_accounting"]} == expected
    for record in current["ffpr_accounting"]:
        part = record["accounting"]
        assert part["brotli"]["images_signature"] == part["zopfli"]["images_signature"]
        assert part["brotli"]["native_decoded_bytes"] == part["zopfli"]["native_decoded_bytes"]
        assert part["complete_byte_change"] == sum(part["zopfli_minus_brotli"].values())
        assert part["zopfli_minus_brotli"]["images"] == 0
        assert part["zopfli_minus_brotli"]["container"] == 0
        assert part["zopfli_minus_brotli"]["other_streams"] == 0
