"""Measured PNG sizes versus a matching plain baseline, one factor at a time."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import re

import pytest

from tools import bench_compression_overview as overview


def records_for(documents, rows, baseline_bytes=1000, png_bytes=900):
    records = []
    for document in documents:
        for row in rows:
            case = dict(source=document.source, input_sha256="source-hash", mode=row.family, dpi=300,
                        recipe=dict(mode=row.family, colors=5, dpi=300),
                        prepared=[dict(packed_sha256="same-pixels", palette_sha256="same-palette")])
            records.append(dict(document=document.key, family=row.family, case=case,
                result=dict(image_variant=row.variant, native_policy=row.native,
                    complete_pdf_bytes=png_bytes if row.variant.endswith("-png") else baseline_bytes,
                    pdf=f"/synthetic/{document.key}/{row.family}/{row.variant}/{row.native}.pdf",
                    exact_native=True, exact_images=True, exact_all_page_pixels=True)))
    return records


def selected_rows():
    return tuple(r for r in overview.ROWS if r.family == "indexed" and r.native == "brotli"
                 and r.variant.startswith("brotli-"))


def test_split_preserves_the_full_measured_scope_and_has_no_specialized_codec_predictors():
    pairs = overview.png_pairs(overview.ROWS)
    primary = overview.primary_rows(overview.ROWS)
    assert len(primary) == 26 and len(pairs) == 8
    assert len(overview.DOCUMENTS) * (len(primary) + len(pairs)) == 204
    assert set(primary) | {png for _, png in pairs} == set(overview.ROWS)
    assert {(p.family, p.native) for _, p in pairs} == {
        (family, policy) for family in overview.BITMAP_FAMILIES for policy in ("zopfli", "brotli")}
    for baseline, png in pairs:
        assert baseline.family == png.family and baseline.native == png.native
        assert baseline.variant == png.variant.removesuffix("-png") + "-plain"
        assert baseline in primary


@pytest.mark.parametrize("baseline,png,expected", [
    (1000, 900, "**900** (-10.0%)"),
    (1000, 1025, "1,025 (+2.5%)"),
    (2000, 1800, "**1,800** (-10.0%)"),
    (1000, 1000, "**1,000** (+0.0%)"),
    (100000, 99999, "**99,999** (+0.0%)"),
])
def test_effect_uses_baseline_denominator_signed_change_and_measured_pair_emphasis(baseline, png, expected):
    assert overview.png_effect_cell(baseline, png) == expected


@pytest.mark.parametrize("baseline,png,expected", [
    (1000, 900, "**-10.0%**"),
    (1000, 1025, "+2.5%"),
    (2000, 1800, "**-10.0%**"),
    (1000, 1000, "**+0.0%**"),
    (100000, 99999, "**+0.0%**"),
    (100000, 100001, "+0.0%"),
])
def test_percentage_only_cells_keep_measured_pair_emphasis_even_when_rounded(baseline, png, expected):
    assert overview.png_effect_cell(baseline, png, show_size=False) == expected


@pytest.mark.parametrize("baseline,png", [(0, 1), (1, 0), (1.0, 1), (1, None), (1, True)])
def test_missing_or_estimated_sizes_cannot_be_formatted_as_measurements(baseline, png):
    for show_size in (True, False):
        with pytest.raises(ValueError, match="measured integer"):
            overview.png_effect_cell(baseline, png, show_size=show_size)


def test_table_names_plain_baselines_and_keeps_all_six_pdf_columns():
    rows = selected_rows()
    records = records_for(overview.DOCUMENTS, rows)
    table = overview.png_prediction_markdown(overview.DOCUMENTS, rows, records)
    assert len(table.splitlines()) == 3
    assert all(len(line.split("|")[1:-1]) == 7 for line in table.splitlines())
    assert table.count("**-10.0%**") == 6
    assert "900" not in table
    assert "| Indexed 5 colors + Brotli |" in table
    assert " + PNG prediction |" not in table
    assert all(document.label in table.splitlines()[0] for document in overview.DOCUMENTS)


@pytest.mark.parametrize("field", ["source", "input_sha256", "mode", "dpi", "recipe", "prepared"])
def test_a_pair_cannot_change_another_factor(field):
    rows, documents = selected_rows(), overview.DOCUMENTS[:1]
    records = records_for(documents, rows)
    records[1]["case"][field] = "changed"
    with pytest.raises(ValueError, match="changes source, recipe or prepared pixels"):
        overview.png_prediction_markdown(documents, rows, records)


@pytest.mark.parametrize("missing", [0, 1])
def test_missing_pair_member_is_not_a_blank_estimate_or_copied_control(missing):
    rows, documents = selected_rows(), overview.DOCUMENTS[:1]
    records = records_for(documents, rows)
    records.pop(missing)
    with pytest.raises(ValueError, match="Missing measured PNG/plain pair"):
        overview.png_prediction_markdown(documents, rows, records)


@pytest.mark.parametrize("field", ["exact_native", "exact_images", "exact_all_page_pixels"])
def test_both_outputs_require_exact_verification(field):
    rows, documents = selected_rows(), overview.DOCUMENTS[:1]
    records = records_for(documents, rows)
    records[1]["result"][field] = False
    with pytest.raises(ValueError, match="Missing exact-output verification"):
        overview.png_prediction_markdown(documents, rows, records)


def test_no_image_controls_still_use_two_independently_saved_measured_pdfs():
    rows, documents = selected_rows(), overview.DOCUMENTS[:1]
    records = records_for(documents, rows, png_bytes=1000)
    for record in records:
        record["case"]["prepared"] = [None]
    assert "**+0.0%**" in overview.png_prediction_markdown(documents, rows, records)
    records[1]["result"]["pdf"] = records[0]["result"]["pdf"]
    with pytest.raises(ValueError, match="independently saved"):
        overview.png_prediction_markdown(documents, rows, records)


def test_duplicate_measured_cells_are_rejected_instead_of_silently_overwritten():
    rows, documents = selected_rows(), overview.DOCUMENTS[:1]
    records = records_for(documents, rows)
    records.append(deepcopy(records[0]))
    with pytest.raises(ValueError, match="Duplicate measured cell"):
        overview.png_prediction_markdown(documents, rows, records)


@pytest.mark.parametrize("stage,expected", [("encoder", "FAILED"), ("shared-preparation", "PREP FAILED")])
def test_rejected_candidates_have_no_size_percentage_or_false_win(stage, expected):
    rows, documents = selected_rows(), overview.DOCUMENTS[:1]
    records = records_for(documents, rows)
    records[1]["result"].update(validation_error="bad pixels", validation_stage=stage)
    table = overview.png_prediction_markdown(documents, rows, records)
    assert table.endswith(f"| {expected} |\n")
    assert "%" not in table and "900" not in table


def test_pairs_require_provenance_and_a_plain_combination():
    rows, documents = selected_rows(), overview.DOCUMENTS[:1]
    records = records_for(documents, rows)
    records[0].pop("case")
    with pytest.raises(ValueError, match="pair provenance"):
        overview.png_prediction_markdown(documents, rows, records)
    with pytest.raises(ValueError, match="Missing plain baseline"):
        overview.png_pairs(rows[1:])


def test_no_prediction_rows_produce_no_empty_effect_table():
    assert overview.png_prediction_markdown(overview.DOCUMENTS, overview.ROWS[:3], []) == ""


def test_published_effect_table_is_percentage_only_and_retains_audited_measured_changes():
    from tools import bench_png_extension as extension
    report = Path("docs/INTEGRATED_COMPRESSION.md").read_text()
    primary, effects = report.split(overview.PNG_SECTION, 1)
    effects = effects.split("## Focused scenarios", 1)[0]
    parse = lambda line: [cell.strip() for cell in line.split("|")[1:-1]]
    baselines = {cells[0]: cells[1:] for line in primary.split("## Overview — final complete-file bytes", 1)[1].splitlines()
                 if line.startswith("| ") for cells in [parse(line)]}
    rows = [parse(line) for line in effects.splitlines() if line.startswith("| ")]
    assert len(rows) == 17 and len(rows[0]) == 7  # one header and sixteen pairs
    assert {row[0] for row in rows[1:]} == {b.label for b, _ in overview.png_pairs(extension.publication_rows())}
    audited = 0
    for row in rows[1:]:
        assert len(row) == 7
        for cell, baseline in zip(row[1:], baselines[row[0]]):
            match = re.fullmatch(r"(\*\*)?([+-]\d+\.\d%)(\*\*)?", cell)
            assert match, cell
            assert int(baseline.replace("*", "").replace(",", "")) > 0
            assert bool(match[1]) == bool(match[3])
            audited += 1
    assert audited == 96
    # Frozen projection of the verified 2026-10-17 complete-file measurements.
    # Arithmetic is exercised above; changing this digest needs a fresh raw-
    # measurement audit, not inference of candidate sizes from rounded deltas.
    table = "\n".join(line for line in effects.splitlines() if line.startswith("|")) + "\n"
    assert sha256(table.encode()).hexdigest() == "1fbeca0bcd483d05be176a5dc13d11bdf9e182973ae675e0aace211eb6d499d5"
