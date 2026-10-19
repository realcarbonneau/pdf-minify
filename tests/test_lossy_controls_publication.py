"""Current-standard table overlay is complete, scoped, idempotent and measured."""

from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path

import pytest

from tools import publish_lossy_controls as publisher


def proof():
    result = dict(designer_ruling=268, quality=75, dpi=300,
                  jpx_quality_mapping="jpeg-reference-study-v1",
                  documents=[asdict(d) for d in publisher.controls.lossy.DOCUMENTS], rows=[])
    for force in (False, True):
        for mode in publisher.controls.lossy.MODES:
            for policy in (("zopfli", "brotli", "flate") if force else ("zopfli", "brotli")):
                result["rows"].append(dict(mode=mode, force_raster=force, policy=policy,
                                           label=publisher.controls.combination(mode, force, policy).label,
                                           sizes=[1000 + len(result["rows"])] * 6))
    return result


def test_all_twenty_two_affected_rows_update_without_touching_main_or_png():
    original = Path("docs/INTEGRATED_COMPRESSION.md").read_text()
    updated = publisher.rewrite_tables(original, proof())
    assert publisher.rewrite_tables(updated, proof()) == updated
    a = original.split("## Overview — final complete-file bytes", 1)[1].split(publisher.ffpr.SECTION, 1)[0]
    b = updated.split("## Overview — final complete-file bytes", 1)[1].split(publisher.ffpr.SECTION, 1)[0]
    assert a == b  # main matrix and all PNG data/denominators are unchanged
    assert not any("q50" in line or "r192" in line for line in updated.splitlines() if line.startswith("|"))
    assert "JPEG q75 + Zopfli native" in updated
    assert "Color FFPR + JPEG2000 q75; optimized residual streams" in updated


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


def test_missing_table_rows_cannot_silently_skip_a_section():
    text = Path("docs/INTEGRATED_COMPRESSION.md").read_text()
    start = text.index("## Focused scenarios")
    stop = text.index("### Logos/artwork", start)
    with pytest.raises(ValueError, match="all 22"):
        publisher.rewrite_tables(text[:start]+text[stop:], proof())


def test_actual_complete_controls_drive_every_active_lossy_table():
    current = json.loads(publisher.FIXTURE.read_text())
    publisher.validate_proof(current)
    assert current["measured_manifest_sha256"] == "72ceaaa600ef6584c10531cabdffbc266444618944cff6074c60a6bf21defb44"
    assert current["unchanged_publication_sha256"] == publisher.best.PUBLICATION_SHA256
    baseline = json.loads(Path("tests/fixtures/lossy_quality_sizes.json").read_text())
    assert current["baseline_sha256"] == baseline["measured_manifest_sha256"]
    assert sum(len(row["sizes"]) for row in current["rows"]) == 60
    for row in current["rows"]:
        for field in ("pdf_sha256", "base_sha256"):
            assert len(row[field]) == 6 and all(len(h) == 64 for h in row[field])
    report = Path("docs/INTEGRATED_COMPRESSION.md").read_text()
    assert publisher.rewrite_tables(report, current) == report
    assert publisher.apply_current(report) == report
    assert "Every active lossy comparison now uses this same standard." in report
    assert current["measured_manifest_sha256"] in report
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
