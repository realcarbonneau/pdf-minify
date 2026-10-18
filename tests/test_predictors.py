"""§260: joint predictor/encoder choice on real, exactly decoded PDF streams."""

from collections import Counter
import hashlib
import zlib

import pymupdf as fitz
import pytest

from pdf_minify.core import best_streams as best, pipeline, predictors, stream_compression as streams
from pdf_minify.core.cancel import CancelToken
from pdf_minify.core.pdf_io import CancelledError
from pdf_minify.core.recipes import preset_spec, spec_key


def image_doc(data, width, height, bpc=8, colors=1):
    doc = fitz.open()
    page = doc.new_page(width=width, height=height)
    xref = doc.get_new_xref()
    space = {1: "/DeviceGray", 3: "/DeviceRGB", 4: "/DeviceCMYK"}[colors]
    doc.update_object(xref, f"<< /Type /XObject /Subtype /Image /Width {width} /Height {height} "
                            f"/ColorSpace {space} /BitsPerComponent {bpc} >>")
    doc.update_stream(xref, data, compress=False)
    page.insert_image(page.rect, xref=xref)
    return doc, xref


@pytest.mark.parametrize("bpc", [1, 2, 4, 8, 16])
@pytest.mark.parametrize("colors", [1, 3, 4])
def test_packed_and_multicomponent_prediction_decodes_exactly_in_pdf(bpc, colors):
    width, height = 13, 9
    data = bytes((i*37+i//7) % 256 for i in range(height*((width*bpc*colors+7)//8)))
    predicted = predictors.predict_rows(data, width, height, bpc, colors)
    with image_doc(data, width, height, bpc, colors)[0] as doc:
        xref = doc[0].get_images()[0][0]
        assert predictors.image_layout(doc, xref, len(data)) == (width, height, bpc, colors)
        doc.update_stream(xref, zlib.compress(predicted), compress=False)
        doc.xref_set_key(xref, "Filter", "/FlateDecode")
        doc.xref_set_key(xref, "DecodeParms",
                         f"<< /Predictor 15 /Columns {width} /Colors {colors} /BitsPerComponent {bpc} >>")
        assert doc.xref_stream(xref) == data


@pytest.mark.parametrize("bpc,digest", [
    (1, "c0f067cfb26130adf73d5e91c44e7099db7af1b89549ef8ea6e2a053b49fedb1"),
    (2, "5d730c4325c46d7514f0c38399faaca7a2d1b97a93e65b713b132fe4f10d8f2f"),
    (4, "cdb5c9d38f3a8bacf9ba043313377a0c19ce916360c44a3d7657c4b95041649e"),
    (8, "3cabc9ad9d469f8f1616d5db1774140fafd1cebb6ed973448c05afb731530f69"),
])
def test_production_selector_matches_the_frozen_single_component_experiment(bpc, digest):
    # Independently checked against the pre-§260 benchmark implementation.
    data = bytes((i*37+i//7) % 256 for i in range(9*((13*bpc+7)//8)))
    assert hashlib.sha256(predictors.predict_rows(data, 13, 9, bpc)).hexdigest() == digest


@pytest.mark.parametrize("args", [(b"", 0, 1, 8), (b"", 1, 0, 8), (b"", 1, 1, 3),
                                  (b"bad-size", 13, 9, 1)])
def test_prediction_rejects_incorrect_rows_and_cancels(args):
    with pytest.raises(ValueError):
        predictors.predict_rows(*args)
    token = CancelToken()
    token.cancel()
    with pytest.raises(CancelledError):
        predictors.predict_rows(b"\0", 1, 1, 8, token=token)


def save(doc, target, **kwargs):
    return best.save_best_streams(doc, target, writer=pipeline._write_optimized_pdf,
                                  directory=str(target.parent), no_new_id=True, **kwargs)


def test_explicit_zopfli_best_selects_a_measured_complete_off_or_on_file(tmp_path, monkeypatch):
    data = bytes((x+y*3) % 256 for y in range(97) for x in range(127))
    calls = Counter()
    encode = streams.encode_stream

    def record(raw, policy, **kwargs):
        calls[policy] += 1
        return encode(raw, policy, **kwargs)

    monkeypatch.setattr(streams, "encode_stream", record)
    sizes = {}
    with image_doc(data, 127, 97)[0] as doc:
        for prediction in ("off", "on", "best"):
            path = tmp_path / f"{prediction}.pdf"
            stats = save(doc, path, policy="zopfli", image_prediction=prediction)
            sizes[prediction] = path.stat().st_size
            assert stats["brotli_streams"] == 0 and stats["predictable_images"] == 1
            assert stats["file_bytes"] == min(stats["candidate_bytes"].values())
            if prediction != "best":
                assert stats["png_prediction_on_streams"] == (prediction == "on")
            with fitz.open(path) as stored:
                image = stored[0].get_images()[0][0]
                assert stored.xref_stream(image) == data
                assert stored.xref_get_key(image, "Filter")[1] == "/FlateDecode"
    assert sizes["best"] == min(sizes["off"], sizes["on"])
    assert calls["zopfli"] > 0 and calls["brotli"] == 0


def test_best_evaluates_both_image_predictors_with_both_encoders(tmp_path, monkeypatch):
    data = bytes((x+y) % 256 for y in range(29) for x in range(31))
    predicted = predictors.predict_rows(data, 31, 29, 8)
    calls = Counter()
    encode = streams.encode_stream

    def record(raw, policy, **kwargs):
        calls[raw, policy] += 1
        return encode(raw, policy, **kwargs)

    monkeypatch.setattr(streams, "encode_stream", record)
    with image_doc(data, 31, 29)[0] as doc:
        stats = save(doc, tmp_path / "best.pdf")
    assert stats["file_bytes"] == min(stats["candidate_bytes"].values())
    assert any(name.startswith("zopfli") for name in stats["candidate_bytes"])
    assert any(name.startswith("brotli") for name in stats["candidate_bytes"])
    for raw in (data, predicted):
        for policy in ("zopfli", "brotli"):
            assert calls[raw, policy] == 1


def test_no_image_rows_skip_the_predictor_but_still_compress_native_streams(tmp_path, monkeypatch):
    monkeypatch.setattr(best, "predict_rows", lambda *a: pytest.fail("no image rows"))
    with fitz.open() as doc:
        doc.new_page().insert_text((50, 50), "Native text is not a PNG image.")
        stats = save(doc, tmp_path / "native.pdf")
    assert stats["streams"] > 0
    assert stats["image_streams"] == stats["predictable_images"] == 0


def test_unknown_layout_is_preserved_automatically_but_explicit_on_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(best, "image_layout", lambda *a: None)
    monkeypatch.setattr(best, "predict_rows", lambda *a: pytest.fail("unknown layout"))
    with image_doc(b"\x10\x20\x30\x40", 2, 2)[0] as doc:
        stats = save(doc, tmp_path / "best.pdf")
        assert stats["predictable_images"] == 0
        target = tmp_path / "previous.pdf"
        target.write_bytes(b"Keep the completed result")
        with pytest.raises(RuntimeError, match="predictor layout"):
            save(doc, target, policy="zopfli", image_prediction="on")
        assert target.read_bytes() == b"Keep the completed result"


def test_predictor_state_is_effective_only_for_explicit_zopfli_packed_images():
    spec = preset_spec(dict(mode="indexed", params=dict(stream_compression="zopfli")))
    assert spec["png_prediction"] == "off"
    assert len({spec_key(dict(spec, png_prediction=p)) for p in ("off", "on", "best")}) == 3
    for mode, policy in (("indexed", "best"), ("indexed", "brotli"),
                         ("bw", "zopfli"), ("jpx", "best"), ("color", "zopfli")):
        inactive = dict(spec, mode=mode, stream_compression=policy)
        assert len({spec_key(dict(inactive, png_prediction=p)) for p in ("off", "on", "best")}) == 1
    assert predictors.effective_prediction(dict(spec, stream_compression="best")) == "best"


@pytest.mark.parametrize("prediction", ["off", "on", "best"])
def test_real_saver_obeys_explicit_zopfli_prediction_and_restores_context(tmp_path, prediction, monkeypatch):
    monkeypatch.setattr(pipeline, "zopfli_binary", lambda: pytest.fail("repeated opportunistic image encoding"))
    source, target = tmp_path / "source.pdf", tmp_path / "target.pdf"
    with image_doc(bytes((x+y) % 256 for y in range(29) for x in range(31)), 31, 29)[0] as doc:
        doc.save(source)
    spec = dict(mode="indexed", dpi_cap=72, colors=16, stream_compression="zopfli",
                png_prediction=prediction)
    pipeline.save_with_spec(str(source), str(target), spec, workdir=str(tmp_path))
    assert pipeline._PNG_PREDICTION.get() is None
    with fitz.open(target) as doc:
        images = doc[0].get_images()
        assert images
        for row in images:
            xref = row[0]
            assert doc.xref_get_key(xref, "Filter")[1] == "/FlateDecode"
            assert doc.xref_stream(xref)
            if prediction != "best":
                assert (doc.xref_get_key(xref, "DecodeParms/Predictor")[1] == "15") == (prediction == "on")
