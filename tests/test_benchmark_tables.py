"""Tagged benchmark tables: scripts change measured cells only (§§282/283)."""

import pytest

from tools import benchmark_tables as tables

PAGE = """# Curated heading

Prose mentions | pipes |, 1,234 bytes and BW + JBIG2.

<!-- table: sizes -->

| Combination | Scan | Photos |
|---|---:|---:|
| <!-- row: group.bw --> **Black and white** | | |
| <!-- row: bw-jbig2 --> BW + JBIG2 | **1,234** | 5,678 |
| <!-- row: bw-packed --> BW | 2,000 | **4,000** |

More prose | 2,000 | 4,000 |

<!-- table: other -->
| Combination | Scan |
|---|---:|
| <!-- row: bw-jbig2 --> BW + JBIG2 | +0.00% |
"""


def test_read_returns_header_ordered_value_cells_and_labels():
    table = tables.read_table(PAGE, "sizes")
    assert table.header == ["Combination", "Scan", "Photos"]
    assert list(table.rows) == ["group.bw", "bw-jbig2", "bw-packed"]
    assert table.rows["bw-jbig2"] == ["**1,234**", "5,678"]
    assert table.rows["group.bw"] == ["", ""]
    assert table.labels == {"group.bw": "**Black and white**", "bw-jbig2": "BW + JBIG2", "bw-packed": "BW"}
    # Same row ID in another table is a different row.
    assert tables.read_table(PAGE, "other").rows == {"bw-jbig2": ["+0.00%"]}
    assert tables.table_ids(PAGE) == ["sizes", "other"]


def test_fill_round_trip_is_byte_identical_and_changes_only_listed_value_cells():
    for table_id in tables.table_ids(PAGE):
        assert tables.fill(PAGE, table_id, tables.read_table(PAGE, table_id).rows) == PAGE
    after = tables.fill(PAGE, "sizes", {"bw-packed": ["**1,999**", "4,001"]})
    changed = [(a, b) for a, b in zip(PAGE.splitlines(), after.splitlines(), strict=True) if a != b]
    assert changed == [("| <!-- row: bw-packed --> BW | 2,000 | **4,000** |",
                        "| <!-- row: bw-packed --> BW | **1,999** | 4,001 |")]
    assert tables.read_table(after, "sizes").labels == tables.read_table(PAGE, "sizes").labels
    assert tables.read_table(after, "other") == tables.read_table(PAGE, "other")


def test_untouched_prose_and_lookalike_lines_are_never_rewritten():
    after = tables.fill(PAGE, "sizes", {"bw-jbig2": ["9", "9"], "bw-packed": ["9", "9"]})
    before_prose = PAGE.split("<!-- table: sizes -->")[0] + PAGE.split("| <!-- row: bw-packed -->")[1].split("\n", 1)[1]
    after_prose = after.split("<!-- table: sizes -->")[0] + after.split("| <!-- row: bw-packed -->")[1].split("\n", 1)[1]
    assert before_prose == after_prose
    assert "More prose | 2,000 | 4,000 |" in after
    assert "Prose mentions | pipes |, 1,234 bytes and BW + JBIG2." in after


def test_unknown_row_is_an_error_not_an_insertion():
    with pytest.raises(ValueError, match="Missing row bw-ffpr"):
        tables.fill(PAGE, "sizes", {"bw-ffpr": ["1", "2"]})


@pytest.mark.parametrize("cells", [["1"], ["1", "2", "3"]])
def test_wrong_cell_count_is_rejected(cells):
    with pytest.raises(ValueError, match="needs 2 value cells"):
        tables.fill(PAGE, "sizes", {"bw-jbig2": cells})


@pytest.mark.parametrize("cell", [12, "1 | 2", "1\n2"])
def test_value_cells_must_be_single_markdown_cells(cell):
    with pytest.raises(ValueError, match="Invalid value cell"):
        tables.fill(PAGE, "sizes", {"bw-jbig2": [cell, "2"]})


def test_missing_or_duplicate_table_tags_are_errors():
    with pytest.raises(ValueError, match="Missing benchmark table tag: absent"):
        tables.read_table(PAGE, "absent")
    duplicated = PAGE + "\n<!-- table: sizes -->\n\n| A | B | C |\n|---|---|---|\n"
    for call in (lambda: tables.read_table(duplicated, "sizes"),
                 lambda: tables.fill(duplicated, "sizes", {})):
        with pytest.raises(ValueError, match="Duplicate benchmark table tag: sizes"):
            call()


@pytest.mark.parametrize("bad,message", [
    ("| BW | 2,000 | **4,000** |", "Row without ID tag"),
    ("| <!-- row: bw-jbig2 --> BW | 2,000 | **4,000** |", "Duplicate row ID bw-jbig2"),
    ("| <!-- row: bw-packed --> BW | 2,000 |", "has 2 cells"),
])
def test_untagged_repeated_or_ragged_rows_are_errors(bad, message):
    page = PAGE.replace("| <!-- row: bw-packed --> BW | 2,000 | **4,000** |", bad)
    with pytest.raises(ValueError, match=message):
        tables.read_table(page, "sizes")


def test_tag_without_a_following_table_is_an_error():
    with pytest.raises(ValueError, match="No Markdown table"):
        tables.read_table("<!-- table: empty -->\n\nJust prose.\n", "empty")


def test_generated_rows_are_keyed_in_order_and_counts_must_match():
    generated = "| Algorithm | Scan |\n|---|---:|\n| BW + JBIG2 | **1** |\n| BW | 2 |\n"
    assert tables.keyed_rows(generated, ["bw-jbig2", "bw-packed"]) == {
        "bw-jbig2": ["**1**"], "bw-packed": ["2"]}
    for ids in (["bw-jbig2"], ["bw-jbig2", "bw-jbig2"]):
        with pytest.raises(ValueError, match="distinct row IDs"):
            tables.keyed_rows(generated, ids)
