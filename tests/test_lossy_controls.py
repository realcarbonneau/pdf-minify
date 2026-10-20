"""All affected controls reuse q75 images; stream policies are the only factor."""

from copy import deepcopy
import io
from pathlib import Path

from PIL import Image
import pymupdf as fitz
import pytest

from tools import bench_lossy_controls as controls


@pytest.fixture(scope="module")
def baseline(tmp_path_factory):
    folder = tmp_path_factory.mktemp("current-lossy-controls")
    source = folder / "source.pdf"
    png = io.BytesIO()
    Image.new("RGB", (16, 24), (40, 120, 230)).save(png, "PNG")
    with fitz.open() as doc:
        page = doc.new_page(width=48, height=64)
        page.insert_image(fitz.Rect(4, 4, 44, 40), stream=png.getvalue())
        page.insert_text((4, 55), "Native", fontsize=6)
        doc.save(source)
    document = controls.overview.Document("tiny", "Tiny PDF", str(source))
    controls.lossy.run(folder / "baseline", (document,))
    return folder, document


def test_scope_covers_sixty_actual_current_standard_controls():
    rows = [controls.combination(mode, force, policy) for mode in controls.lossy.MODES
            for force in (False, True) for policy in (("zopfli", "brotli", "flate") if force else ("zopfli", "brotli"))]
    assert len(rows) == 10 and len(rows) * len(controls.lossy.DOCUMENTS) == 60
    assert all("q75" in row.family and "q75" in row.label for row in rows)
    assert not any("q50" in row.label or "r192" in row.label for row in rows)


@pytest.fixture(scope="module")
def measured_controls(baseline):
    folder, document = baseline
    reject = lambda *a, **k: pytest.fail("Repeated image processing/encoding")
    with pytest.MonkeyPatch.context() as patch:
        for name in ("save_with_spec", "jpeg_encode", "jpx_encode"):
            patch.setattr(controls.study.pipeline, name, reject)
        rows = controls.run(folder / "controls", folder / "baseline" / "metrics.json",
                            documents=(document,), workers=1)
    return folder, document, rows


def test_real_controls_never_reencode_images_and_resume_is_strict(measured_controls, monkeypatch):
    folder, document, rows = measured_controls
    assert len(rows) == len({r["result"]["pdf"] for r in rows}) == 10
    for row in rows:
        assert row["result"]["exact_all_page_pixels"] and row["result"]["exact_images"]
        assert Path(row["result"]["pdf"]).stat().st_size == row["result"]["complete_pdf_bytes"]
    reject = lambda *a, **k: pytest.fail("Resume repeated image processing/encoding or saving")
    for name in ("save_with_spec", "jpeg_encode", "jpx_encode"):
        monkeypatch.setattr(controls.study.pipeline, name, reject)
    monkeypatch.setattr(controls.study, "save_combination", reject)
    resumed = controls.run(folder / "controls", folder / "baseline" / "metrics.json",
                           documents=(document,), workers=1, resume=True)
    assert [r["result"]["pdf_sha256"] for r in resumed] == [r["result"]["pdf_sha256"] for r in rows]


def test_jpeg_control_reuse_verifies_existing_files_without_new_jpeg_saves(measured_controls,tmp_path,monkeypatch):
    folder,document,previous=measured_controls
    frozen=folder/'controls'/'metrics.json'
    save=controls.study.save_combination
    def only_jpx(base,target,case,variant,*args,**kwargs):
        assert variant.startswith('jpx-')
        return save(base,target,case,variant,*args,**kwargs)
    monkeypatch.setattr(controls.study,'save_combination',only_jpx)
    rows=controls.run(tmp_path/'reused',folder/'baseline'/'metrics.json',documents=(document,),workers=1,
                      reuse_jpeg=frozen,reuse_jpeg_sha256=controls.lossy.file_digest(frozen))
    assert len(rows)==10
    for row in rows:
        if row['mode']=='color':
            old=next(r for r in previous if (r['mode'],r['force_raster'],r['result']['native_policy'])==
                     ('color',row['force_raster'],row['result']['native_policy']))
            assert row['result']['pdf']==old['result']['pdf']
            assert row['result']['pdf_sha256']==old['result']['pdf_sha256']
            assert row['reused_from']['sha256']==controls.lossy.file_digest(frozen)


def test_jpeg_control_reuse_rejects_changed_frozen_proof(measured_controls):
    folder,document,_=measured_controls
    with pytest.raises(ValueError,match='frozen JPEG control'):
        controls.load_control_reuse(folder/'controls'/'metrics.json','bad hash',{},(document,))


def test_incomplete_and_changed_baseline_cannot_be_imported(baseline, tmp_path):
    import json
    folder, document = baseline
    original = folder / "baseline" / "metrics.json"
    for field in ("complete", "identity"):
        value = json.loads(original.read_text())
        value[field] = False if field == "complete" else {}
        broken = tmp_path / f"{field}.json"
        broken.write_text(json.dumps(value))
        with pytest.raises(ValueError, match="current lossy baseline"):
            controls.load_baseline(broken, (document,))


@pytest.mark.parametrize("change", ["missing", "duplicate", "wrong-quality", "aliased"])
def test_inventory_rejects_missing_duplicate_or_mislabeled_measurements(measured_controls, change):
    _, document, original = measured_controls
    rows = deepcopy(original)
    if change == "missing":
        rows.pop()
    elif change == "duplicate":
        rows.append(rows[0])
    elif change == "wrong-quality":
        rows[0]["case"]["recipe"]["jpeg_q"] = 50
    else:
        rows[0]["result"]["pdf"] = rows[1]["result"]["pdf"]
    with pytest.raises(ValueError):
        controls.validate_inventory((document,), rows)
