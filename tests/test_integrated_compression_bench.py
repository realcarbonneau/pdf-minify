"""Integrated final-PDF matrix: genuine codecs, no estimated combination cells."""

import io
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image
import pymupdf as fitz
import pytest

from tools import bench_integrated_compression as study


def source_pdf(path):
    with fitz.open() as doc:
        for number in range(2):
            page = doc.new_page(width=72, height=96)
            array = np.random.default_rng(number).integers(0, 255, (17, 19, 3), dtype=np.uint8)
            stream = io.BytesIO()
            Image.fromarray(array).save(stream, "PNG")
            page.insert_image(fitz.Rect(5, 5, 65, 55), stream=stream.getvalue())
            page.insert_text((5, 76), f"Native {number}", fontsize=8)
            page.draw_line((5, 82), (65, 82), color=(0, .7, 0))
            page.insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(5, 68, 65, 78),
                              "uri": "https://example.com"})
            page.add_text_annot((55, 65), "Native annotation")
            page.set_rotation(90)
        doc.set_metadata({"title": "Integrated metadata preserved", "author": "Fixture"})
        doc.embfile_add("control.bin", b"Unchanged attachment 0123456789")
        doc.save(path)


@pytest.mark.skipif(not shutil.which("jbig2"), reason="Genuine JBIG2 matrix")
@pytest.mark.parametrize("mode", ["indexed", "bw-images", "bw-ffpr"])
def test_all_21_real_combinations_preserve_prepared_image_and_native_data(tmp_path, mode):
    source = tmp_path / "source.pdf"
    source_pdf(source)
    original = source.read_bytes()
    prepared = study.images.run_case(source, tmp_path / "prepared", mode=mode, dpi=36)
    manifest = tmp_path / "images.json"
    manifest.write_text(json.dumps([prepared]))
    case = next(study.bitmap_cases(manifest))
    context = study.pipeline._STREAM_POLICY.set("brotli")
    try:
        report = study.run_case(case, tmp_path / "integrated")
        assert study.pipeline._STREAM_POLICY.get() == "brotli"
    finally:
        study.pipeline._STREAM_POLICY.reset(context)
    assert len(report["results"]) == 21
    assert {(r["image_variant"], r["native_policy"]) for r in report["results"]} == {
        (v, p) for v in study.VARIANTS for p in study.POLICIES}
    assert source.read_bytes() == original
    for result in report["results"]:
        assert result["complete_pdf_bytes"] == Path(result["pdf"]).stat().st_size
        assert result["exact_images"] and result["exact_native"] and result["exact_all_page_pixels"]
        with fitz.open(result["pdf"]) as doc:
            if result["native_policy"] == "brotli" or result["image_variant"].startswith("brotli"):
                assert doc.xref_get_key(doc.pdf_catalog(), "Extensions/PDFa/ExtensionRevision")[1] == "2026"
    assert "seconds" not in json.dumps(report)
    study.export([report], tmp_path)
    assert "complete_pdf_bytes" in (tmp_path / "matrix.csv").read_text()
    assert "F+/Z" in (tmp_path / "matrix.md").read_text()


def production_case(tmp_path):
    source = tmp_path / "source.pdf"
    source_pdf(source)
    return next(study.production_cases([source], tmp_path / "preparation", native_sources=[]))


def test_resume_verifies_outputs_without_encoding_and_rejects_tampering(tmp_path, monkeypatch):
    case = production_case(tmp_path)
    folder = tmp_path / "run"
    first = study.run_case(case, folder)
    def forbidden(*args):
        pytest.fail("Validated existing combined PDF must not be re-encoded")
    monkeypatch.setattr(study, "save_combination", forbidden)
    resumed = study.run_case(case, folder, resume=True)
    assert all(item["reused"] for item in resumed["results"])
    assert [r["complete_pdf_bytes"] for r in first["results"]] == [r["complete_pdf_bytes"] for r in resumed["results"]]
    output = Path(first["results"][0]["pdf"])
    output.write_bytes(output.read_bytes()+b"\nchanged")
    with pytest.raises(ValueError, match="Changed saved integrated"):
        study.run_case(case, folder, resume=True)


@pytest.mark.parametrize("change", ["source", "prepared", "environment"])
def test_resume_rejects_changed_provenance(tmp_path, monkeypatch, change):
    case = production_case(tmp_path)
    folder = tmp_path / "run"
    study.run_case(case, folder, policies=("flate",))
    if change == "environment":
        monkeypatch.setattr(study, "environment", lambda: {"changed": True})
    else:
        target = Path(case["source"] if change == "source" else next(iter(case["bases"].values()))["pdf"])
        target.write_bytes(target.read_bytes()+b"\nchanged")
    with pytest.raises(ValueError, match="changed|Changed"):
        study.run_case(case, folder, policies=("flate",), resume=True)


def test_production_recipes_use_real_saver_and_no_silent_codec_substitution(tmp_path):
    source = tmp_path / "source.pdf"
    source_pdf(source)
    cases = list(study.production_cases([source], tmp_path / "preparation", native_sources=[]))
    assert [next(iter(c["bases"])) for c in cases] == ["jpeg-q50", "jpx-r192", "jpx-lossless", "preserve-images"]
    for case in cases:
        variant, base = next(iter(case["bases"].items()))
        with fitz.open(base["pdf"]) as doc:
            if variant != "preserve-images":
                wanted = "/DCTDecode" if variant == "jpeg-q50" else "/JPXDecode"
                assert all(doc.xref_get_key(i[0], "Filter")[1] == wanted for p in doc for i in p.get_images())
        report = study.run_case(case, tmp_path / case["id"], policies=("flate", "brotli"))
        assert len(report["results"]) == 2


def test_changed_native_content_is_not_accepted_as_a_smaller_output(tmp_path):
    case = production_case(tmp_path)
    base = Path(next(iter(case["bases"].values()))["pdf"])
    expected = study.snapshot(base, 150)
    broken = tmp_path / "broken.pdf"
    with fitz.open(base) as doc:
        doc[0].insert_text((5, 30), "WRONG", fontsize=8)
        doc.save(broken)
    with pytest.raises(RuntimeError, match="changed native|changed pages"):
        study.verify(broken, expected, 150, "flate")


def test_markdown_bolds_all_tied_complete_file_minima_only():
    case = dict(family="production", source="images.pdf", bases={"jpeg-q50": {}}, recipe={})
    report = dict(identity=dict(case=case), results=[
        dict(image_variant="jpeg-q50", native_policy=p, complete_pdf_bytes=n)
        for p, n in zip(study.POLICIES, (1000, 900, 900))])
    table = study.matrix_markdown([report])
    assert "| 1,000 | **900** | **900** |" in table
    assert "seconds" not in table


def test_explicit_import_preserves_frozen_preparation_provenance_and_checks_hashes(tmp_path):
    source = tmp_path / "source.pdf"
    source_pdf(source)
    folder = tmp_path / "preparation"
    list(study.production_cases([source], folder, native_sources=[]))
    imported = list(study.import_production(folder / "prepared"))
    assert len(imported) == 4
    assert all("preparation_environment" in case for case in imported)
    case = imported[0]
    base = Path(next(iter(case["bases"].values()))["pdf"])
    base.write_bytes(base.read_bytes()+b"changed")
    with pytest.raises(ValueError, match="Changed imported"):
        list(study.import_production(folder / "prepared"))


@pytest.mark.parametrize("subset", [True, False])
def test_shared_saver_only_subsets_fonts_when_requested(tmp_path, monkeypatch, subset):
    calls = []
    class Document:
        def subset_fonts(self):
            calls.append("subset")
        def save(self, path, **kwargs):
            calls.append(("save", kwargs))
    monkeypatch.setattr(study.pipeline, "recompress_native_streams", lambda *a, **k:
                        dict(streams=0, raw_bytes=0, encoded_bytes=0, encode_seconds=0))
    study.pipeline._save_optimized_pdf(Document(), str(tmp_path / "out.pdf"), subset_fonts=subset)
    assert ("subset" in calls) is subset
    assert calls[-1][1]["deflate_fonts"] is False


def test_real_embedded_font_bytes_stay_frozen_across_native_policies(tmp_path):
    source = study.ROOT / "examples/images.pdf"
    base = tmp_path / "prepared.pdf"
    study.pipeline.gc_copy(str(source), str(base))
    case = dict(id="real-font", family="production", source=str(source),
                input_sha256=study.digest(source.read_bytes()), mode="passthrough", dpi=72,
                recipe=dict(mode="passthrough"),
                bases={"preserve-images": dict(pdf=str(base), sha256=study.digest(base.read_bytes()))})
    report = study.run_case(case, tmp_path / "matrix")
    assert len(report["results"]) == 3
    assert all(row["exact_native"] for row in report["results"])
