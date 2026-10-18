"""Measured PNG sizes versus a matching plain baseline, one factor at a time."""

from copy import deepcopy
from decimal import Decimal
import json
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
    (1000, 900, "**900** (-10.00%)"),
    (1000, 1025, "1,025 (+2.50%)"),
    (2000, 1800, "**1,800** (-10.00%)"),
    (1000, 1000, "**1,000** (+0.00%)"),
    (100000, 99999, "**99,999** (+0.00%)"),
])
def test_effect_uses_baseline_denominator_signed_change_and_measured_pair_emphasis(baseline, png, expected):
    assert overview.measured_effect_cell(baseline, png) == expected


@pytest.mark.parametrize("baseline,png,expected", [
    (1000, 900, "**-10.00%**"),
    (1000, 1025, "+2.50%"),
    (2000, 1800, "**-10.00%**"),
    (1000, 1000, "+0.00%"),
    (100000, 99999, "+0.00%"),
    (100000, 100001, "+0.00%"),
    (100000, 99996, "+0.00%"),
    (100000, 99994, "**-0.01%**"),
    (100000, 100004, "+0.00%"),
    (100000, 100006, "+0.01%"),
])
def test_percentage_only_cells_use_two_decimals_and_never_bold_rounded_zero(baseline, png, expected):
    assert overview.measured_effect_cell(baseline, png, show_size=False) == expected


@pytest.mark.parametrize("baseline,png", [(0, 1), (1, 0), (1.0, 1), (1, None), (1, True)])
def test_missing_or_estimated_sizes_cannot_be_formatted_as_measurements(baseline, png):
    for show_size in (True, False):
        with pytest.raises(ValueError, match="measured integer"):
            overview.measured_effect_cell(baseline, png, show_size=show_size)


def test_table_names_plain_baselines_and_keeps_all_six_pdf_columns():
    rows = selected_rows()
    records = records_for(overview.DOCUMENTS, rows)
    table = overview.png_prediction_markdown(overview.DOCUMENTS, rows, records)
    assert len(table.splitlines()) == 3
    assert all(len(line.split("|")[1:-1]) == 7 for line in table.splitlines())
    assert table.count("**-10.00%**") == 6
    assert "900" not in table
    assert "| Indexed 5 colors + <ins>Brotli</ins> |" in table
    assert table.count("<ins>Brotli</ins>") == 1
    assert all("<ins>" not in row.label for row in rows)  # identity/overview labels stay plain
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
    table = overview.png_prediction_markdown(documents, rows, records)
    assert table.endswith("| +0.00% |\n")
    assert "**" not in table
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
    effects = effects.split("\n## ", 1)[0]
    # Original measured bytes, not reconstructed from previously rounded deltas.
    fixture = json.loads(Path("tests/fixtures/png_prediction_sizes.json").read_text())
    assert fixture["original_publication_sha256"] == "9864f717f7ea0f1f879f8a3d7537229ffe9e62d6817228dc510945d6adc9e7e9"
    assert fixture["publication_sha256"] == "9279a171feff32151a44e7d2f41d3042abdc611bdd2ecf72c3b4bb724eeed22d"
    assert fixture["brotli_declaration"] is False
    assert fixture["documents"] == [d.key for d in overview.DOCUMENTS]
    parse = lambda line: [cell.strip() for cell in line.split("|")[1:-1]]
    # §258 moves fixed-encoder baselines out of the Best-only overview. The
    # actual PNG denominator must remain its own encoder's visible control.
    controls = report.split("### Fixed-encoder controls — measured final PDF bytes", 1)[1].split("## Focused scenarios", 1)[0]
    baselines = {cells[0]: cells[1:] for line in controls.splitlines()
                 if line.startswith("| ") for cells in [parse(line)]}
    rows = [parse(line) for line in effects.splitlines() if line.startswith("| ")]
    assert len(rows) == 17 and len(rows[0]) == 7  # one header and sixteen pairs
    assert sum("<ins>Brotli</ins>" in row[0] for row in rows[1:]) == 8
    for row in rows[1:]:
        if "Brotli" in row[0]:
            assert "<ins>Brotli</ins>" in row[0]
        else:
            assert "<ins>" not in row[0]
        row[0] = row[0].replace("<ins>", "").replace("</ins>", "")
    assert {row[0] for row in rows[1:]} == {overview.display_label(b.label) for b, _ in overview.png_pairs(extension.publication_rows())}
    audited = 0
    for row, expected in zip(rows[1:], fixture["rows"], strict=True):
        assert len(row) == 7
        assert row[0] == expected["label"]
        for cell, baseline, a, b in zip(row[1:], baselines[row[0]], expected["baseline"], expected["png"], strict=True):
            match = re.fullmatch(r"(\*\*)?([+-]\d+\.\d{2}%)(\*\*)?", cell)
            assert match, cell
            assert int(baseline.replace("*", "").replace(",", "")) == a > 0
            change = (Decimal(b - a) * 100 / Decimal(a)).quantize(Decimal("0.01"))
            if change == 0:
                change = Decimal(0)
            assert match[2] == f"{change:+.2f}%"
            assert bool(match[1]) == bool(match[3]) == (change < 0)
            audited += 1
    assert audited == 96


def test_published_decision_tree_leads_the_section_and_matches_measured_results():
    from tools import publish_best_overview as publisher
    report = Path("docs/INTEGRATED_COMPRESSION.md").read_text()
    effects = report.split(overview.PNG_SECTION, 1)[1].split("\n## ", 1)[0]
    assert effects.startswith("\n\n" + publisher.PNG_GUIDANCE + "\n\nOnly **image-row PNG prediction**")
    fixture = json.loads(Path("tests/fixtures/png_prediction_sizes.json").read_text())
    for encoder, reductions in (("Brotli", 0), ("Zopfli", 18)):
        rows = [row for row in fixture["rows"] if encoder in row["label"]]
        pairs = [(a, b) for row in rows for a, b in zip(row["baseline"], row["png"], strict=True)]
        assert len(pairs) == 48
        assert sum(b < a for a, b in pairs) == reductions
        assert f"**{reductions} of 48 {encoder}**" in publisher.PNG_GUIDANCE
    indexed = [row for row in fixture["rows"] if "indexed" in row["label"].lower()]
    assert len(indexed) == 12
    for row in indexed:
        for document in ("photos", "art"):
            i = fixture["documents"].index(document)
            assert row["png"][i] > row["baseline"][i]
    mixed = fixture["documents"].index("mixed")
    mixed_ffpr = [row for row in indexed if "FFPR" in row["label"] and "Zopfli" in row["label"]]
    assert len(mixed_ffpr) == 3
    assert all(row["png"][mixed] < row["baseline"][mixed] for row in mixed_ffpr)
    assert "**Counterexample:**" in publisher.PNG_GUIDANCE
    assert "Best (Zopfli/Brotli) → automatically test OFF/ON with both encoders." in publisher.PNG_GUIDANCE
    assert "96 fixed-encoder pairs do **not** measure §260's new" in publisher.PNG_GUIDANCE
