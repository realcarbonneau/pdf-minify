"""Native A/B tests: no image-codec/recipe changes may enter the pair."""

from copy import deepcopy
from dataclasses import asdict
from pathlib import Path

import pymupdf as fitz
import pytest

from tools import bench_residual_streams as residual

overview, study = residual.overview, residual.study


def test_planned_scope_is_five_specialized_ffpr_rows_and_two_native_controls():
    assert len(residual.ROWS) == 7
    assert len(residual.ROWS) * len(overview.DOCUMENTS) == 42
    assert [r.native for r in residual.ROWS[:2]] == ["zopfli", "brotli"]
    assert all(r.family.endswith("-ffpr") and r.native == "zopfli" for r in residual.ROWS[2:])
    assert not any(r.variant.endswith(("-plain", "-png")) for r in residual.ROWS)


@pytest.fixture
def measured_pair(tmp_path):
    source = tmp_path / "source.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=36, height=48)
        page.insert_text((2, 8), "Native", fontsize=5)
        pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 4, 4), False)
        pix.clear_with(80)
        page.insert_image(fitz.Rect(2, 10, 34, 46), pixmap=pix)
        doc.save(source)
    case = next(study.production_cases([source], tmp_path / "prepared", native_sources=[]))
    row = overview.Combination("jpeg-q50", "jpeg-q50", "zopfli", "JPEG q50 + Zopfli-Flate native")
    document = overview.Document("tiny", "Tiny PDF", str(source))
    report = study.run_case(case, tmp_path / "candidate", policies=("zopfli",))
    candidate = dict(case=case, result=report["results"][0], origin="test")
    pair = residual.measure_pair(document, row, candidate, None, tmp_path / "pair", {"fixed": True})
    return document, row, pair, candidate


def test_real_save_holds_encoded_images_and_native_pixels_fixed(measured_pair, tmp_path, monkeypatch):
    document, row, pair, candidate = measured_pair
    residual.validate_pair(document, row, pair)
    a, b = (study.snapshot(Path(pair[k]["result"]["pdf"]), 300) for k in ("reference", "candidate"))
    assert a["images"] == b["images"] and a["native"] == b["native"] and a["pages"] == b["pages"]
    reference, effect = residual.tables((document,), (row,), [pair])
    assert str(pair["reference"]["result"]["complete_pdf_bytes"]) in reference.replace(",", "")
    assert "%" in effect
    monkeypatch.setattr(study, "run_case", lambda *a, **k: pytest.fail("re-encoded completed pair"))
    assert residual.measure_pair(document, row, candidate, None, tmp_path / "pair",
                                 {"fixed": True}, resume=True) == pair
    with pytest.raises(ValueError, match="identity"):
        residual.measure_pair(document, row, candidate, None, tmp_path / "pair", {}, resume=True)


@pytest.mark.parametrize("field", ["source", "dpi", "recipe", "prepared", "bases"])
def test_a_native_pair_cannot_change_other_factors(measured_pair, field):
    document, row, pair, _ = measured_pair
    changed = deepcopy(pair)
    changed["reference"]["case"][field] = "different"
    with pytest.raises(ValueError, match="prepared images or recipe"):
        residual.validate_pair(document, row, changed)


def test_missing_duplicate_mislabeled_or_aliased_pairs_cannot_publish(measured_pair):
    document, row, pair, _ = measured_pair
    with pytest.raises(ValueError, match="Missing native"):
        residual.tables((document,), (row,), [])
    with pytest.raises(ValueError, match="Duplicate native"):
        residual.tables((document,), (row,), [pair, pair])
    changed = deepcopy(pair)
    changed["reference"]["result"]["native_policy"] = "brotli"
    with pytest.raises(ValueError, match="wrong image variant or native policy"):
        residual.validate_pair(document, row, changed)
    changed = deepcopy(pair)
    changed["combination"] = {**asdict(row), "native": "brotli"}
    with pytest.raises(ValueError, match="changes source"):
        residual.validate_pair(document, row, changed)
