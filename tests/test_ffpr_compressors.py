"""FFPR residual comparison: measured files, exact accounting, no image changes."""

from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
import re

import pytest

from tools import bench_ffpr_compressors as ffpr

overview, study = ffpr.overview, ffpr.study


def test_scope_is_only_five_specialized_ffpr_rows_over_six_inputs():
    assert len(ffpr.ROWS) * len(overview.DOCUMENTS) == 30
    assert len(ffpr.ROWS) == len(ffpr.LABELS) == 5
    assert all(r.family.endswith("-ffpr") and r.native == "zopfli" for r in ffpr.ROWS)
    assert not any(r.variant.endswith(("-plain", "-png")) for r in ffpr.ROWS)


@pytest.fixture(scope="module")
def actual_pair(tmp_path_factory):
    folder = tmp_path_factory.mktemp("ffpr-compressor")
    source = folder / "source.pdf"
    with study.fitz.open() as doc:
        for _ in range(2):
            page = doc.new_page(width=36, height=48)
            page.insert_text((2, 8), "Raster", fontsize=4)
            page.draw_rect(study.fitz.Rect(2, 12, 30, 40), fill=(0.2, 0.4, 0.8))
        doc.save(source)
    case = next(c for c in study.production_cases([source], folder / "prepared",
        native_sources=[], include_ffpr=True) if "jpeg-q50-ffpr" in c["bases"])
    row = next(r for r in ffpr.ROWS if r.family == "jpeg-q50-ffpr")
    document = overview.Document("tiny", "Two-page FFPR", str(source))
    saved = study.run_case(case, folder / "zopfli", policies=("zopfli",))
    candidate = dict(case=case, result=saved["results"][0], origin="test")
    pair = ffpr.measure(document, row, candidate, folder / "pair", {"fixed": True}, False)
    return folder, document, row, pair, candidate


def test_real_pair_keeps_images_exact_and_accounting_closes(actual_pair):
    _, document, row, pair, _ = actual_pair
    ffpr.residual.validate_pair(document, row, pair, reference_policy="brotli")
    account = pair["accounting"]
    assert account["brotli"]["pages"] == account["zopfli"]["pages"] == 2
    assert account["brotli"]["images_signature"] == account["zopfli"]["images_signature"]
    assert account["zopfli_minus_brotli"]["images"] == 0
    assert sum(account["zopfli_minus_brotli"].values()) == account["complete_byte_change"]
    assert account["brotli"]["brotli_declaration"] == "2026"
    assert account["zopfli"]["brotli_declaration"] == "null"


def test_metadata_only_control_holds_encoded_native_and_images_fixed(actual_pair):
    folder, _, _, pair, _ = actual_pair
    control = ffpr.metadata_control(pair, folder / "metadata-control")
    zopfli = pair["accounting"]["zopfli"]
    assert control["added_declaration_bytes"] > 0
    assert control["accounting"]["images_signature"] == zopfli["images_signature"]
    assert control["accounting"]["native_signature"] == zopfli["native_signature"]
    assert control["accounting"]["brotli_declaration"] == "2026"


def test_table_names_brotli_baseline_and_completed_pairs_do_not_encode_again(actual_pair, monkeypatch):
    folder, document, row, pair, candidate = actual_pair
    table = ffpr.effect_table((document,), (row,), [pair])
    assert "JPEG q50" in table and "Two-page FFPR" in table
    assert re.search(r"[+-]\d+\.\d{2}%", table)
    monkeypatch.setattr(study, "run_case", lambda *a, **k: pytest.fail("re-encoded completed pair"))
    assert ffpr.measure(document, row, candidate, folder / "pair", {"fixed": True}, True) == pair


def test_missing_duplicate_aliased_and_wrong_policy_pairs_cannot_publish(actual_pair):
    _, document, row, pair, _ = actual_pair
    with pytest.raises(ValueError, match="Missing FFPR"):
        ffpr.effect_table((document,), (row,), [])
    with pytest.raises(ValueError, match="Duplicate FFPR"):
        ffpr.effect_table((document,), (row,), [pair, pair])
    changed = deepcopy(pair)
    changed["reference"]["result"]["native_policy"] = "flate"
    with pytest.raises(ValueError, match="wrong image variant or native policy"):
        ffpr.effect_table((document,), (row,), [changed])
    changed = deepcopy(pair)
    changed["reference"]["result"]["pdf"] = changed["candidate"]["result"]["pdf"]
    with pytest.raises(ValueError, match="Changed complete output|independently saved"):
        ffpr.effect_table((document,), (row,), [changed])


@pytest.mark.parametrize("baseline,candidate,expected", [
    (1000, 900, "**-10.00%**"),
    (127518301, 127518137, "+0.00%"),
    (1000, 1001, "+0.10%"),
])
def test_ffpr_percentages_use_the_shared_precision_and_do_not_bold_rounded_zero(baseline, candidate, expected):
    assert overview.measured_effect_cell(baseline, candidate, show_size=False) == expected


@pytest.mark.parametrize("places", [True, -1, 10])
def test_invalid_percentage_precision_is_rejected(places):
    with pytest.raises(ValueError, match="precision"):
        overview.measured_effect_cell(1000, 900, places=places)


def test_short_labels_do_not_rewrite_identity_or_surrounding_prose():
    row = overview.Combination("sample", "jbig2", "zopfli", "JBIG2 + Zopfli-Flate native")
    before = "Zopfli-Flate produces FlateDecode.\n| JBIG2 + Zopfli-Flate native | 123 |\n"
    after = overview.short_table_labels(before)
    assert after == "Zopfli-Flate produces FlateDecode.\n| JBIG2 + Zopfli native | 123 |\n"
    assert asdict(row)["label"] == "JBIG2 + Zopfli-Flate native"


def test_published_ffpr_effects_match_the_measured_sizes_fixture():
    # Frozen measured Brotli baselines are populated only after the real study.
    import json
    from decimal import Decimal

    fixture = json.loads(Path("tests/fixtures/ffpr_compressor_sizes.json").read_text())
    report = Path("docs/INTEGRATED_COMPRESSION.md").read_text()
    section = report.split(ffpr.SECTION, 1)[1].split("\n## ", 1)[0]
    parsed = [[cell.strip() for cell in line.split("|")[1:-1]]
              for line in section.splitlines() if line.startswith("| ")][1:]
    assert len(parsed) == 5
    for row, expected in zip(parsed, fixture["rows"], strict=True):
        assert row[0] == expected["label"]
        for cell, baseline, candidate in zip(row[1:], expected["brotli"], expected["zopfli"], strict=True):
            change = (100 * Decimal(candidate-baseline)/Decimal(baseline)).quantize(Decimal("0.01"))
            if change == 0:
                change = Decimal(0)
            percent = f"{change:+.2f}%"
            assert cell == (f"**{percent}**" if change < 0 else percent)


def test_brotli_comparison_immediately_follows_png_with_all_zero_percentages_unbolded():
    report = Path("docs/INTEGRATED_COMPRESSION.md").read_text()
    headings = [line for line in report.splitlines() if line.startswith("## ")]
    png = headings.index(overview.PNG_SECTION)
    assert headings[png + 1] == ffpr.SECTION
    assert headings[png + 2] == "## Focused scenarios"
    assert not re.search(r"\*\*[+-]0\.00%\*\*", report)
    for line in report.splitlines():
        if line.startswith("|"):
            for percent in re.findall(r"[+-]\d+\.\d+%", line):
                assert re.fullmatch(r"[+-]\d+\.\d{2}%", percent), percent
                assert percent != "-0.00%"


def test_development_document_tables_use_short_zopfli_labels():
    for path in Path("docs").glob("*.md"):
        assert not any("Zopfli-Flate" in line for line in path.read_text().splitlines()
                       if line.startswith("|")), path
