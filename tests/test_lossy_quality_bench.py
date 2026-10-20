"""q75/q75 baseline: real separate saves and strict prepared-pixel provenance."""

from copy import deepcopy
import io
from pathlib import Path

import numpy as np
from PIL import Image
import pymupdf as fitz
import pytest

from tools import bench_lossy_quality as bench


@pytest.fixture(scope="module")
def real_study(tmp_path_factory):
    folder = tmp_path_factory.mktemp("lossy-q75")
    source = folder / "source.pdf"
    rgb = np.random.default_rng(266).integers(0, 256, (32, 48, 3), dtype=np.uint8)
    png = io.BytesIO()
    Image.fromarray(rgb).save(png, "PNG")
    with fitz.open() as doc:
        page = doc.new_page(width=72, height=96)
        page.insert_image(fitz.Rect(4, 8, 68, 56), stream=png.getvalue())
        page.insert_text((4, 76), "Native text", fontsize=7)
        page.draw_line((4, 80), (68, 80), color=(.2, .4, .8))
        doc.new_page(width=72, height=96).insert_text((4, 32), "Text only", fontsize=7)
        doc.save(source)
    document = bench.overview.Document("art", "Real two-page fixture", str(source))
    records = bench.run(folder / "study", (document,))
    return folder, document, records


def test_scope_has_six_whole_inputs_and_only_lossy_q75_rows():
    assert len(bench.DOCUMENTS) == 6 and bench.DPI == 300 and bench.QUALITY == 75
    assert bench.MODES == ("color", "jpx")
    for force in (False, True):
        for mode in bench.MODES:
            spec = bench.recipe(mode, force)
            assert spec["jpeg_q" if mode == "color" else "jpx_q"] == 75
            assert spec["stream_compression"] == "best"
            assert spec["force_raster"] == force and not spec["brotli_declaration"]
            assert "rate" not in spec and not spec.get("lossless")
    with pytest.raises(ValueError, match="lossy"):
        bench.recipe("bw", False)


def test_real_outputs_are_independent_and_match_production_canvases(real_study):
    folder, document, records = real_study
    assert len(records) == len({r["pdf"] for r in records}) == 4
    for force in (False, True):
        pair = [r for r in records if r["force_raster"] == force]
        bench.verify_pair(*pair)
        assert all(len(r["canvases"]) == (2 if force else 1) for r in pair)
        for record in pair:
            bench.verify_record(record)
            assert record["complete_pdf_bytes"] == Path(record["pdf"]).stat().st_size
            assert len(record["readback"]["pages"]) == 2
            assert all(len(page["renders"]) == 2 for page in record["readback"]["pages"])
            for canvas in record["canvases"]:
                reference = canvas["quality_reference"]
                assert reference["quality"] == 75 and reference["jpeg_bytes"] > 0
                assert reference["jpx_target_psnr_db"] == 44.0
    markdown = (folder / "study" / "table.md").read_text()
    assert markdown.count(" q75 |") == 4 and "lossless" not in markdown.lower()
    assert "**" in markdown
    assert not any(word in markdown for word in ("seconds", "PSNR", "estimated"))


def test_validated_resume_does_not_reencode(real_study, monkeypatch):
    folder, document, records = real_study
    monkeypatch.setattr(bench.pipeline, "save_with_spec", lambda *a, **k: pytest.fail("re-encoded complete output"))
    assert bench.run(folder / "study", (document,), resume=True) == records


def test_verified_jpeg_reuse_saves_only_jpx_and_checks_actual_paired_payloads(real_study, tmp_path, monkeypatch):
    folder, document, original = real_study
    source = folder/'study'/'metrics.json'
    save = bench.pipeline.save_with_spec
    calls = []
    def only_jpx(*args, **kwargs):
        calls.append(args[2]['mode'])
        assert args[2]['mode'] == 'jpx'
        return save(*args, **kwargs)
    monkeypatch.setattr(bench.pipeline,'save_with_spec',only_jpx)
    current = bench.run(tmp_path/'reuse',(document,),reuse_jpeg=source,
                        reuse_jpeg_sha256=bench.file_digest(source))
    assert calls == ['jpx','jpx']
    for row in current:
        if row['mode']=='color':
            before=next(r for r in original if r['mode']=='color' and r['force_raster']==row['force_raster'])
            assert row['pdf']==before['pdf'] and row['pdf_sha256']==before['pdf_sha256']
            assert row['reused_from']['manifest_sha256']==bench.file_digest(source)
    for force in (False,True):
        bench.verify_pair(*[r for r in current if r['force_raster']==force])


def test_changed_jpeg_reuse_provenance_is_not_accepted(real_study):
    folder,document,_=real_study
    with pytest.raises(ValueError,match='frozen JPEG'):
        bench.load_jpeg_reuse(folder/'study'/'metrics.json','wrong hash',(document,))


def test_tampered_actual_pdf_is_not_a_measurement(real_study, tmp_path):
    _, _, records = real_study
    row = deepcopy(records[0])
    changed = tmp_path / "tampered.pdf"
    changed.write_bytes(Path(row["pdf"]).read_bytes() + b"\nchanged")
    row["pdf"] = str(changed)
    with pytest.raises(ValueError, match="Changed measured"):
        bench.verify_record(row)


@pytest.mark.parametrize("change", ["source-pixels", "native", "geometry", "aliased", "reference"])
def test_pair_rejects_confounded_inputs_or_changed_native_content(real_study, change):
    _, _, records = real_study
    left, right = deepcopy(records[:2])
    if change == "source-pixels":
        right["canvases"][0]["samples_sha256"] = "changed"
    elif change == "native":
        right["readback"]["native"] = []
    elif change == "geometry":
        right["readback"]["pages"][0]["rotation"] = 90
    elif change == "aliased":
        right["pdf"] = left["pdf"]
    else:
        right["canvases"][0]["quality_reference"]["jpeg_sha256"] = "f" * 64
    with pytest.raises(ValueError, match="different prepared|native content|aliased|reference differs"):
        bench.verify_pair(left, right)


def test_invalid_reference_or_old_mapping_is_not_current_measurement(real_study):
    _, document, records = real_study
    row = deepcopy(records[0])
    row["canvases"][0]["quality_reference"]["jpx_target_psnr_db"] = 39.5
    with pytest.raises(ValueError, match="quality reference"):
        bench.verify_record(row, rerender=False)
    current = bench.identity((document,))
    assert current["jpx_quality_mapping"] == "jpeg-matched-tile-psnr-v1"
    assert current["study"] == "LOSSY-06-jpeg-matched-q75-v1"


def test_table_rejects_missing_duplicate_and_estimated_sizes(real_study):
    _, document, records = real_study
    with pytest.raises(ValueError, match="Incomplete"):
        bench.table((document,), records[:-1])
    with pytest.raises(ValueError, match="Duplicate"):
        bench.table((document,), records + records[:1])
    changed = deepcopy(records)
    changed[0]["complete_pdf_bytes"] = 1.5
    with pytest.raises(ValueError, match="positive measured"):
        bench.table((document,), changed)
