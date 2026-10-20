"""Controlled-report statistics and reuse of completed syntax evidence."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools import publish_compression_experiments as publication


def test_pair_statistics_are_actual_signed_byte_changes_not_relative_rankings():
    assert publication.pair_summary([(100, 90), (100, 100), (100, 110)]) == dict(
        smaller=1, tied=1, larger=1, min_byte_change=-10, max_byte_change=10)


def test_qpdf_reuses_existing_evidence_and_only_checks_missing_supported_outputs(tmp_path, monkeypatch):
    old = tmp_path / "previous.json"
    old.write_text(json.dumps(dict(results=[dict(pdf="old.pdf", output="earlier check passed")])) )
    records = [dict(result=dict(pdf=path, pdf_sha256="same", native_policy=policy))
               for path, policy in (("old.pdf", "zopfli"), ("new.pdf", "flate"), ("brotli.pdf", "brotli"))]
    calls = []
    def check(argv, **kwargs):
        calls.append(argv)
        return SimpleNamespace(returncode=0, stdout="syntax passed", stderr="")
    monkeypatch.setattr(publication.subprocess, "run", check)
    result = publication.qpdf_checks(records, old, tmp_path)
    assert result["checked"] == 2 and result["unsupported"] == 1
    assert calls == [["qpdf", "--check", "new.pdf"]]
    assert publication.qpdf_checks(records, old, tmp_path) == result
    assert len(calls) == 1  # unchanged publication is not another decoder run
    records[1]["result"]["pdf_sha256"] = "changed"
    with pytest.raises(ValueError, match="qpdf evidence"):
        publication.qpdf_checks(records, old, tmp_path)


def test_incomplete_measurements_cannot_publish_or_trigger_encoders(tmp_path, monkeypatch):
    monkeypatch.setattr(publication.shared, "toolchain", lambda: {"fixed": True})
    monkeypatch.setattr(publication.shared, "import_history", lambda *a: ({}, {}))
    png, native = tmp_path / "png.json", tmp_path / "native.json"
    png.write_text(json.dumps(dict(complete=False)))
    native.write_text(json.dumps(dict(complete=True)))
    with pytest.raises(ValueError, match="Incomplete or changed"):
        publication.publish("original report", Path("old"), png, native, tmp_path / "output")
    assert not (tmp_path / "output").exists()


def test_direct_stream_signature_distinguishes_native_changes_from_fixed_images(tmp_path):
    import pymupdf as fitz

    paths = [tmp_path / "before.pdf", tmp_path / "after.pdf"]
    for path, word in zip(paths, ("Before", "After")):
        with fitz.open() as doc:
            page = doc.new_page(width=36, height=48)
            page.insert_text((2, 8), word, fontsize=4)
            pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 4, 4), False)
            pix.clear_with(80)
            page.insert_image(fitz.Rect(2, 10, 34, 46), pixmap=pix)
            doc.save(path)
    assert publication.fixed_stream_signature(paths[0], "images") == publication.fixed_stream_signature(paths[1], "images")
    assert publication.fixed_stream_signature(paths[0], "native") != publication.fixed_stream_signature(paths[1], "native")


def test_published_native_pair_percentages_use_the_visible_reference():
    from decimal import Decimal
    import re
    from tools import benchmark_tables as tables
    from tools.publish_best_overview import fixed_row_id

    page = tables.PAGE.read_text()
    reference = tables.read_table(page, "residual-reference").rows
    candidates = tables.read_table(page, "residual-effect").rows
    expected = {fixed_row_id(r.family, r.variant, r.native) for r in publication.residual.ROWS}
    assert len(expected) == 7 and set(reference) == set(candidates) == expected
    audited = 0
    for row_id, cells in candidates.items():
        assert len(cells) == len(reference[row_id]) == 6
        for baseline, cell in zip(reference[row_id], cells, strict=True):
            match = re.fullmatch(r"(\*\*)?([\d,]+)(\*\*)? \(([+-]\d+\.\d{2})%\)", cell)
            assert match, cell
            a, b = int(baseline.replace(",", "")), int(match[2].replace(",", ""))
            change = (Decimal(b - a) * 100 / Decimal(a)).quantize(Decimal("0.01"))
            if change == 0:
                change = Decimal(0)
            assert match[4] == f"{change:+.2f}"
            assert bool(match[1]) == bool(match[3]) == (b <= a)
            audited += 1
    assert audited == 42


def test_publication_fills_measured_cells_by_page_row_id():
    from tools import benchmark_tables as tables
    from tools.publish_best_overview import fixed_row_id

    page = tables.PAGE.read_text()
    rows = publication.shared.publication_rows()
    png = {fixed_row_id(a.family, a.variant, a.native) for a, _ in publication.overview.png_pairs(rows)}
    assert len(png) == 16 and set(tables.read_table(page, "png-effect").rows) == png
