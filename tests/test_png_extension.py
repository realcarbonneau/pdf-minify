"""Scope, provenance and real-save contracts for the additional PNG pairs."""

from copy import deepcopy
import json
from pathlib import Path

import pymupdf as fitz
import pytest

from tools import bench_png_extension as extension
from tools import bench_compression_overview as overview


def test_extension_is_exactly_48_new_pairs_with_separate_palette_and_page_mode_groups():
    assert len(extension.JOBS) == 24
    assert len({job.key for job in extension.JOBS}) == 24
    assert {job.colors for job in extension.JOBS} == {16, 64}
    assert {job.mode for job in extension.JOBS} == {"indexed", "indexed-ffpr"}
    rows = extension.extension_rows()
    assert len(rows) == 16 and len(overview.png_pairs(rows)) == 8
    assert len(extension.publication_rows()) == 50
    assert len(overview.primary_rows(extension.publication_rows())) == 34
    assert len(overview.png_pairs(extension.publication_rows())) == 16
    assert all(row.variant in extension.VARIANTS for row in rows)
    assert all(row.native == row.variant.split("-")[0] for row in rows)


def test_compatibility_bridge_only_allows_the_exact_unused_metadata_removal():
    old = "prefix\n" + extension.OLD_METADATA + "suffix\n"
    new = "prefix\n" + extension.NEW_METADATA + "suffix\n"
    name = "tools/bench_image_streams.py"
    previous = {name: extension.study.digest(old.encode()), "pipeline": "same"}
    current = {name: extension.study.digest(new.encode()), "pipeline": "same"}
    assert len(extension.compatible_implementation(previous, current, old)) == 1
    for changed in ({**current, "pipeline": "different"},
                    {**current, name: extension.study.digest((new + "changed encoder").encode())}):
        with pytest.raises(ValueError, match="historical|solely"):
            extension.compatible_implementation(previous, changed, old)
    with pytest.raises(ValueError, match="file scope"):
        extension.compatible_implementation(previous, {name: current[name]}, old)
    assert extension.compatible_implementation(previous, previous, "") == []


def sample_record(job, variant):
    return dict(case=dict(source=job.source, mode=job.mode, colors=job.colors, dpi=300,
                recipe=dict(mode=job.mode, colors=job.colors, dpi=300, threshold_method=None, threshold=None)),
                result=dict(image_variant=variant, native_policy=variant.split("-")[0]), origin="original")


def test_import_scope_uses_full_recipe_not_mutable_name_or_source_alone():
    job = extension.JOBS[0]
    records = [sample_record(job, variant) for variant in extension.VARIANTS]
    selected = extension.imported_job(dict(extras=records), job)
    assert len(selected) == 4 and selected[0]["imported_record"] == records[0]
    for field, value in (("colors", 5), ("dpi", 150), ("mode", "indexed-ffpr"), ("source", "other.pdf")):
        changed = deepcopy(records)
        for record in changed:
            record["case"][field] = value
        assert extension.imported_job(dict(extras=changed), job) == []
    with pytest.raises(ValueError, match="Incomplete historical"):
        extension.imported_job(dict(extras=records[:3]), job)


@pytest.mark.parametrize("mode", ["indexed", "indexed-ffpr"])
def test_real_four_variant_save_exactness_and_completed_job_resume(tmp_path, monkeypatch, mode):
    source = tmp_path / "tiny.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=36, height=48)
        page.insert_text((2, 8), "PNG", fontsize=5)
        pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 4, 4), False)
        pix.clear_with(60)
        page.insert_image(fitz.Rect(2, 10, 34, 46), pixmap=pix)
        doc.save(source)
    job = extension.Job("tiny", str(source), mode, 16)
    # Custom sources are valid measurement jobs, not extra corpus members.
    records = extension.measure_job(job, tmp_path / "run", {"test": "fixed"})
    assert len(records) == 4
    assert len({r["result"]["pdf"] for r in records}) == 4
    for record in records:
        overview.validate_record(record["case"], record["result"])
    monkeypatch.setattr(extension.study.images, "run_case", lambda *a, **k: pytest.fail("re-encoded completed job"))
    assert extension.measure_job(job, tmp_path / "run", {"test": "fixed"}, resume=True) == records
    with pytest.raises(ValueError, match="identity"):
        extension.measure_job(job, tmp_path / "run", {"test": "changed"}, resume=True)
    result = records[0]["result"]
    Path(result["pdf"]).write_bytes(b"changed saved artifact")
    with pytest.raises(ValueError, match="Changed complete output"):
        extension.measure_job(job, tmp_path / "run", {"test": "fixed"}, resume=True)


def test_recipe_and_four_output_gates_cannot_be_bypassed_with_a_partial_checkpoint(tmp_path):
    job = extension.JOBS[0]
    with pytest.raises(ValueError, match="four-output"):
        extension.validate_job(job, [])
    records = [dict(document=job.document, family=job.family, **sample_record(job, v)) for v in extension.VARIANTS]
    records[0]["family"] = "indexed-5"
    with pytest.raises(ValueError, match="fixed recipe"):
        extension.validate_job(job, records)
    folder = tmp_path / "run"
    folder.mkdir()
    (folder / "metrics.json").write_text(json.dumps(dict(identity="wrong", records=[])))
    with pytest.raises(ValueError, match="identity"):
        extension.measure_job(job, folder, "expected", resume=True)
