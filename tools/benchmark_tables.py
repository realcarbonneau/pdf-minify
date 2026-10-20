"""Read and fill measured cells of hand-curated benchmark tables by ID tag.

People curate the benchmark page: prose, headings, table placement, row
order, labels and column headers (designer §282). Scripts only read or write
the measured value cells of rows matched by table ID plus row ID (§283)::

    <!-- table: overview -->

    | Algorithm combination | Native text/vectors | BW scan |
    |---|---:|---:|
    | <!-- row: bw-jbig2 --> BW + JBIG2 | **182,485** | **267,896** |

The table tag is its own line; blank lines may separate it from the table.
Every body row starts its label cell with a row tag. Nothing here locates a
table by heading, label text or position, and :func:`fill` never changes a
label, header, untouched row or any text outside the rows it is given.
"""

from dataclasses import dataclass
from pathlib import Path
import re

PAGE = Path("docs/COMPRESSION_BENCHMARKS.md")

_TABLE_TAG = re.compile(r"^<!-- table: ([A-Za-z0-9._-]+) -->[ \t]*$")
_ROW_TAG = re.compile(r"^\s*<!-- row: ([A-Za-z0-9._-]+) -->[ \t]*")
_SEPARATOR = re.compile(r"^\s*:?-+:?\s*$")
_PIPE = re.compile(r"(?<!\\)\|")


@dataclass(frozen=True)
class Table:
    """One tagged table. ``rows`` maps row ID to value cells, in page order.

    Value cells are the stripped cell text after the label, including any
    Markdown such as ``**bold**``. ``labels`` maps row ID to its label text,
    without the tag. ``header`` includes the label column's heading.
    """

    id: str
    header: list
    rows: dict
    labels: dict


def _segments(line):
    """Raw text between unescaped pipes; requires leading and trailing pipes."""
    parts = _PIPE.split(line)
    if len(parts) < 3 or parts[0].strip() or parts[-1].strip():
        raise ValueError(f"Malformed benchmark table row: {line!r}")
    return parts


def table_ids(markdown):
    """All table IDs on the page, in page order."""
    return [m[1] for line in markdown.splitlines() if (m := _TABLE_TAG.match(line))]


def _locate(markdown, table_id):
    """Return the page lines and the parsed table with each row's line index."""
    lines = markdown.splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines)
              if (m := _TABLE_TAG.match(line.rstrip("\r\n"))) and m[1] == table_id]
    if not starts:
        raise ValueError(f"Missing benchmark table tag: {table_id}")
    if len(starts) > 1:
        raise ValueError(f"Duplicate benchmark table tag: {table_id}")
    index = starts[0] + 1
    while index < len(lines) and not lines[index].strip():
        index += 1
    block = []
    while index < len(lines) and lines[index].lstrip().startswith("|"):
        block.append(index)
        index += 1
    if len(block) < 2:
        raise ValueError(f"No Markdown table follows tag: {table_id}")
    header = [cell.strip() for cell in _segments(lines[block[0]].rstrip("\r\n"))[1:-1]]
    separator = _segments(lines[block[1]].rstrip("\r\n"))[1:-1]
    if len(separator) != len(header) or not all(_SEPARATOR.match(cell) for cell in separator):
        raise ValueError(f"Missing header separator in table: {table_id}")
    rows, labels, where = {}, {}, {}
    for number in block[2:]:
        cells = _segments(lines[number].rstrip("\r\n"))[1:-1]
        tag = _ROW_TAG.match(cells[0])
        if not tag:
            raise ValueError(f"Row without ID tag in table {table_id}: {lines[number].strip()}")
        row_id = tag[1]
        if row_id in rows:
            raise ValueError(f"Duplicate row ID {row_id} in table: {table_id}")
        if len(cells) != len(header):
            raise ValueError(f"Row {row_id} has {len(cells)} cells; table {table_id} has {len(header)} columns")
        rows[row_id] = [cell.strip() for cell in cells[1:]]
        labels[row_id] = cells[0][tag.end():].strip()
        where[row_id] = number
    return lines, Table(table_id, header, rows, labels), where


def read_table(markdown, table_id):
    """Parse the table tagged ``table_id``; see :class:`Table`."""
    return _locate(markdown, table_id)[1]


def fill(markdown, table_id, values):
    """Write measured value cells, ``{row_id: [cells]}``, into one table.

    Only the listed rows' value cells change. A cell whose stripped text is
    already the new value keeps its exact original bytes, so filling the
    published values again is byte-identical. Every listed row must exist
    and supply exactly that row's number of value cells.
    """
    lines, table, where = _locate(markdown, table_id)
    for row_id, cells in values.items():
        if row_id not in table.rows:
            raise ValueError(f"Missing row {row_id} in benchmark table: {table_id}")
        cells = list(cells)
        if len(cells) != len(table.rows[row_id]):
            raise ValueError(f"Row {row_id} in table {table_id} needs {len(table.rows[row_id])} "
                             f"value cells, got {len(cells)}")
        if any(type(cell) is not str or "\n" in cell or "\r" in cell or _PIPE.search(cell)
               for cell in cells):
            raise ValueError(f"Invalid value cell for row {row_id} in table: {table_id}")
        line = lines[where[row_id]]
        body = line.rstrip("\r\n")
        parts = _segments(body)
        values_raw = parts[2:-1]
        parts[2:-1] = [old if old.strip() == new.strip() else f" {new.strip()} "
                       for old, new in zip(values_raw, cells)]
        lines[where[row_id]] = "|".join(parts) + line[len(body):]
    return "".join(lines)


def keyed_rows(generated, row_ids):
    """Assign the body rows of an untagged generated table to ``row_ids`` in order.

    Generators emit one header, one separator and then one line per row;
    this returns ``{row_id: [value cells]}`` ready for :func:`fill`.
    """
    lines = [line for line in generated.splitlines() if line.strip()]
    body = [[cell.strip() for cell in _segments(line)[1:-1]][1:] for line in lines[2:]]
    row_ids = list(row_ids)
    if len(body) != len(row_ids) or len(set(row_ids)) != len(row_ids):
        raise ValueError(f"Generated table has {len(body)} rows for {len(row_ids)} distinct row IDs")
    return dict(zip(row_ids, body))
