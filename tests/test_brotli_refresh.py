"""Current encoders, immutable old evidence, exact rendered graph and real sizes."""

from pathlib import Path
import json

import pymupdf as fitz
import pytest

from tools import refresh_brotli_tables as refresh


def measured_source(tmp_path):
    source, before = tmp_path / "source.pdf", tmp_path / "declared.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=72, height=96)
        page.insert_text((3, 30), "Brotli", fontsize=8)
        page.draw_rect(fitz.Rect(4, 40, 60, 85), color=(0, 0, 1))
        doc.xref_set_key(doc.pdf_catalog(), "BinaryControl", "<000178ff>")
        doc.save(source)
    refresh.study.pipeline.save_with_spec(str(source), str(before), dict(
        mode="passthrough", stream_compression="brotli", brotli_declaration=True))
    return dict(key="fixture", scope="test", case=dict(source=str(source),
        input_sha256=refresh.file_hash(source), mode="passthrough", recipe={}),
        result=dict(pdf=str(before), pdf_sha256=refresh.file_hash(before),
                    complete_pdf_bytes=before.stat().st_size,
                    image_variant="preserve-images", native_policy="brotli"))


def test_real_brotli_rerun_is_declaration_off_and_preserves_full_document_graph(tmp_path):
    job = measured_source(tmp_path)
    original = Path(job["result"]["pdf"]).read_bytes()
    measured = refresh.measure(job, tmp_path / "rerun", {"source": "test"})
    result = measured["result"]
    assert result["complete_pdf_bytes"] == Path(result["pdf"]).stat().st_size
    assert result["complete_pdf_bytes"] < len(original)
    assert measured["encoder"]["fresh_encodes"] > 0
    assert Path(job["result"]["pdf"]).read_bytes() == original
    with fitz.open(result["pdf"]) as doc:
        assert not refresh.study.streams.brotli_declaration_present(doc)
        assert doc.xref_get_key(doc.pdf_catalog(), "Version")[0] == "null"
        assert doc.xref_get_key(doc.pdf_catalog(), "BinaryControl")[1] == "\x00\x01xÿ"
    assert refresh.measure(job, tmp_path / "rerun", {"source": "test"}, True) == measured
    with pytest.raises(ValueError, match="identity"):
        refresh.measure(job, tmp_path / "rerun", {"source": "changed"}, True)


def test_graph_detects_binary_string_or_drawing_changes_without_rasterization():
    with fitz.open() as doc:
        doc.new_page().insert_text((10, 30), "Drawn text")
        doc.xref_set_key(doc.pdf_catalog(), "BinaryControl", "<000178ff>")
        before = refresh.rendered_graph(doc)
        doc.xref_set_key(doc.pdf_catalog(), "BinaryControl", "<000178fe>")
        assert refresh.rendered_graph(doc) != before
        doc.xref_set_key(doc.pdf_catalog(), "BinaryControl", "<000178ff>")
        assert refresh.rendered_graph(doc) == before
        doc[0].insert_text((10, 50), "New content")
        assert refresh.rendered_graph(doc) != before


@pytest.mark.parametrize("prediction", [False, True])
def test_brotli_image_rerun_retains_only_existing_decoding_parameters(tmp_path, prediction):
    samples = bytes([0x10, 0x00, 0xA5, 0x80, 0xFF, 0x80])
    predicted = refresh.study.images.predict_rows(samples, 9, 3, 1) if prediction else samples
    payload, filtr = refresh.study.streams.encode_stream(predicted, "brotli")
    params = "<< /Predictor 15 /Colors 1 /BitsPerComponent 1 /Columns 9 >>"
    with fitz.open() as doc:
        doc.new_page(width=9, height=3)
        xref = doc.get_new_xref()
        doc.update_object(xref, "<< /Type /XObject /Subtype /Image /Width 9 /Height 3 "
                               "/BitsPerComponent 1 /ColorSpace /DeviceGray >>")
        doc.update_stream(xref, payload, compress=False)
        doc.xref_set_key(xref, "Filter", filtr)
        if prediction:
            doc.xref_set_key(xref, "DecodeParms", params)
        assert doc.xref_stream(xref) == samples
        before = doc.xref_stream_raw(xref)
        assert refresh.rerun_brotli_images(doc, tmp_path) == 1
        assert doc.xref_stream(xref) == samples
        assert doc.xref_stream_raw(xref) == before
        if prediction:
            assert doc.xref_get_key(xref, "DecodeParms/Predictor")[1] == "15"
        else:
            assert "DecodeParms" not in doc.xref_get_keys(xref)


def test_only_pinned_successful_current_encoder_checkpoints_can_be_imported(tmp_path, monkeypatch):
    job = measured_source(tmp_path)
    previous = tmp_path / "previous"
    previous.mkdir()
    implementation = previous / "implementation.py"
    implementation.write_text("pinned first-pass fixture")
    producer = refresh.file_hash(implementation)
    monkeypatch.setattr(refresh, "REUSABLE_PRODUCER", producer)
    old_identity = dict(implementation=producer, inputs={"old": "hash"},
                        environment={"encoder": "same"}, jobs_sha256="same jobs")
    measured = refresh.measure(job, previous / "jobs" / job["key"], old_identity)
    new_identity = dict(old_identity, implementation="current", verified_import=str(previous))
    imported = refresh.measure(job, tmp_path / "new", new_identity, reuse_verified=previous)
    assert imported["reused_verified"]["sha256"]
    assert imported["encoder"]["fresh_encodes"] == 0
    assert Path(imported["result"]["pdf"]).read_bytes() == Path(measured["result"]["pdf"]).read_bytes()
    with pytest.raises(ValueError, match="Incompatible"):
        refresh.measure(job, tmp_path / "changed", dict(new_identity, environment={}), reuse_verified=previous)
    checkpoint = previous / "jobs" / job["key"] / "metrics.json"
    proof = json.loads(checkpoint.read_text())
    proof["result"]["pdf_sha256"] = "changed"
    checkpoint.write_text(json.dumps(proof))
    with pytest.raises(ValueError, match="Changed verified-import PDF"):
        refresh.measure(job, tmp_path / "changed-output", new_identity, reuse_verified=previous)
