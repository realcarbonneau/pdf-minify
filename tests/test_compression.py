"""§§203–205: explicit codecs, independent native streams, exact real PDFs."""

import hashlib
import io
import shutil
import subprocess
import zlib

import numpy as np
import pymupdf as fitz
from PIL import Image
import pytest

from pdf_minify.core import pipeline, stream_compression as streams
from pdf_minify.core.algorithms import ALGORITHMS, BW_MODES, with_algorithm
from pdf_minify.core.cancel import CancelToken
from pdf_minify.core.display import DisplayPage
from pdf_minify.core.pdf_io import CancelledError
from pdf_minify.core.recipes import preset_spec, spec_key


def source_pdf(path, pages=1):
    palette = np.array([(255, 255, 255), (255, 76, 35), (135, 63, 214),
                        (254, 195, 58), (241, 32, 91)], dtype=np.uint8)
    y, x = np.indices((69, 73))
    with fitz.open() as doc:
        for index in range(pages):
            page = doc.new_page(width=73, height=96)
            data = io.BytesIO()
            Image.fromarray(palette[(x//14+y//17+index) % 5]).save(data, "PNG")
            page.insert_image(fitz.Rect(0, 0, 73, 69), stream=data.getvalue())
            page.insert_font(fontname="Original", fontbuffer=fitz.Font("helv").buffer)
            page.insert_text((3, 82), f"Native {index}", fontname="Original", fontsize=8, color=(0, 0, 1))
            page.draw_line((3, 88), (65, 88), color=(0, .7, .2), width=.5)
            page.insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(3, 73, 65, 84),
                              "uri": "https://example.com/"})
        doc.embfile_add("kept.txt", b"Unchanged attachment bytes.")
        doc.set_xml_metadata("<original-metadata>Keep this stream</original-metadata>")
        doc.save(path)


def pixels(page, matrix=None):
    pix = DisplayPage(page).render(matrix)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)


def recipe(mode, **params):
    spec = preset_spec(dict(mode=mode, params=dict(dpi=72, dpi_cap=72, colors=5,
                                                  force_raster=False) | params))
    return spec


def test_six_algorithms_have_distinct_effective_identities_and_legacy_defaults():
    assert [label for _, label in ALGORITHMS] == [
        "JBIG2 BW", "JBIG2 Color", "Packed BW", "Indexed color", "JPEG2000", "JPEG"]
    assert len({spec_key(recipe(mode)) for mode, _ in ALGORITHMS}) == 6
    for mode, _ in ALGORITHMS:
        spec = recipe(mode)
        assert spec_key(spec) == spec_key(dict(spec, stream_compression="flate", label="not identity"))
        assert spec_key(spec) != spec_key(dict(spec, stream_compression="brotli"))
        assert spec_key(spec) != spec_key(dict(spec, stream_compression="zopfli"))


def test_algorithm_conversion_preserves_active_dpi_and_seeds_real_choices_not_fixed_checkbox_state():
    original = recipe("bw", strategy="simple", t=193)
    layered = with_algorithm(original, "layered-jbig2")
    assert layered["dpi_cap"] == 72 and layered["colors"] == 5
    # The disabled BW lossless checkbox must not select lossless JPX by accident.
    assert not with_algorithm(original, "jpx")["lossless"]
    color = dict(with_algorithm(original, "color"), dpi_cap=200)
    # Old inactive `dpi=72` must not override current color DPI.
    assert with_algorithm(color, "bw-flate")["dpi"] == 200
    assert spec_key(with_algorithm(layered, "bw")) == spec_key(original)


@pytest.mark.parametrize("mode", [mode for mode, _ in ALGORITHMS])
def test_actual_saver_obeys_explicit_image_codec_and_keeps_native_artwork(tmp_path, mode):
    source, output = tmp_path / "source.pdf", tmp_path / "output.pdf"
    source_pdf(source, pages=2)
    before_digest = hashlib.sha256(source.read_bytes()).digest()
    pipeline.save_with_spec(str(source), str(output), recipe(mode), workdir=str(tmp_path))
    with fitz.open(source) as original, fitz.open(output) as doc:
        assert len(doc) == 2
        for index, page in enumerate(doc):
            assert page.get_text("words") == original[index].get_text("words")
            assert page.get_links()[0]["uri"] == "https://example.com/"
            images = page.get_images(full=True)
            expected = {"bw": "/JBIG2Decode", "bw-flate": "/FlateDecode",
                        "layered-jbig2": "/JBIG2Decode", "indexed": "/FlateDecode",
                        "jpx": "/JPXDecode", "color": "/DCTDecode"}[mode]
            assert images
            for image in images:
                assert doc.xref_get_key(image[0], "Filter")[1] == expected
                assert image[2:4] == (73, 96)
                if mode == "layered-jbig2":
                    assert doc.xref_get_key(image[0], "ImageMask")[1] == "true"
                elif mode in BW_MODES:
                    assert image[4] == 1
        if mode not in BW_MODES:
            assert doc.embfile_get("kept.txt") == b"Unchanged attachment bytes."
    assert hashlib.sha256(source.read_bytes()).digest() == before_digest


@pytest.mark.parametrize("mode", ["bw", "bw-flate"])
def test_ffpr_uses_selected_bw_codec_and_has_no_native_text(tmp_path, mode):
    source, output = tmp_path / "source.pdf", tmp_path / "output.pdf"
    source_pdf(source, pages=2)
    pipeline.save_with_spec(str(source), str(output), recipe(mode, force_raster=True))
    with fitz.open(output) as doc:
        assert all(not page.get_text().strip() for page in doc)
        assert len({page.get_images()[0][0] for page in doc}) == 2
        for page in doc:
            image = page.get_images()[0]
            assert image[4] == 1
            assert doc.xref_get_key(image[0], "Filter")[1] == (
                "/JBIG2Decode" if mode == "bw" else "/FlateDecode")


def test_production_layered_and_flate_palette_actual_pages_are_identical(tmp_path):
    source = tmp_path / "source.pdf"
    source_pdf(source, pages=2)
    outputs = []
    for mode in ("indexed", "layered-jbig2"):
        output = tmp_path / f"{mode}.pdf"
        pipeline.save_with_spec(str(source), str(output), recipe(mode))
        outputs.append(fitz.open(output))
    try:
        for index in range(2):
            for scale in (1, 2, 4):
                assert np.array_equal(pixels(outputs[0][index], fitz.Matrix(scale, scale)),
                                      pixels(outputs[1][index], fitz.Matrix(scale, scale)))
    finally:
        for doc in outputs:
            doc.close()


def test_binary_encoder_keeps_leading_packed_whitespace_and_cleans_transport(tmp_path):
    bw = np.random.default_rng(192).choice(np.array([0, 255], dtype=np.uint8), size=(13, 19))
    bw[0, :8] = np.where(np.array([0, 0, 0, 0, 1, 0, 1, 0]), 0, 255)
    assert np.packbits(bw[0] == 0)[0] == 0x0a
    context = pipeline._ENCODE_WORKDIR.set(str(tmp_path))
    try:
        payload, codec = pipeline.bw_page_payload(bw, "simple", 128, codec="jbig2")
        assert codec == "jbig2" and pipeline.jbig2_renders(payload, 19, 13, bw)
    finally:
        pipeline._ENCODE_WORKDIR.reset(context)
    assert not list(tmp_path.iterdir())


def test_invalid_black_placeholder_is_rejected_repeatedly_without_consuming_warnings():
    before = fitz.TOOLS.mupdf_warnings(reset=False)
    for _ in range(2):
        assert not pipeline.jbig2_renders(b"invalid", 19, 13, np.zeros((13, 19), dtype=np.uint8))
    after = fitz.TOOLS.mupdf_warnings(reset=False)
    assert after.startswith(before) and len(after) > len(before)


@pytest.mark.parametrize("mode", ["bw", "layered-jbig2"])
def test_explicit_jbig2_failure_is_not_silently_flate(tmp_path, monkeypatch, mode):
    source, output = tmp_path / "source.pdf", tmp_path / "output.pdf"
    source_pdf(source)
    monkeypatch.setattr(pipeline, "jbig2_binary", lambda: None)
    with pytest.raises(RuntimeError, match="JBIG2"):
        pipeline.save_with_spec(str(source), str(output), recipe(mode))
    assert not output.exists()


@pytest.mark.parametrize("policy", ["none", "flate-fast", "flate", "zopfli",
                                    "brotli-9", "brotli", "lzw", "runlength"])
def test_native_stream_codecs_roundtrip_real_pdf_and_independent_qpdf(tmp_path, policy):
    data = np.random.default_rng(203).bytes(25000)+b"native drawing operators BT /F1 12 Tf ET\n"*1000
    encoded, filtr = streams.encode_stream(data, policy, directory=str(tmp_path))
    with fitz.open() as doc:
        doc.new_page()
        xref = doc.get_new_xref()
        doc.update_object(xref, "<<>>")
        doc.update_stream(xref, encoded, compress=False)
        doc.xref_set_key(xref, "Filter", filtr or "null")
        assert doc.xref_stream(xref) == data
        # Keep this arbitrary non-content stream reachable without rendering it.
        doc.xref_set_key(doc.pdf_catalog(), "CompressionTest", f"{xref} 0 R")
        output = tmp_path / "codec.pdf"
        doc.save(output)
    if shutil.which("qpdf") and not policy.startswith("brotli"):
        result = subprocess.run(["qpdf", f"--show-object={xref}", "--filtered-stream-data", str(output)],
                                capture_output=True, timeout=10)
        assert result.returncode == 0 and not result.stderr and result.stdout == data


@pytest.mark.parametrize("size", [0, 1, 253, 254, 767, 1791, 50000])
def test_lzw_width_boundaries_and_dictionary_reset(size):
    data = np.random.default_rng(size).bytes(size)
    encoded, filtr = streams.encode_stream(data, "lzw")
    with fitz.open() as doc:
        doc.new_page()
        xref = doc.get_new_xref()
        doc.update_object(xref, "<<>>")
        doc.update_stream(xref, encoded, compress=False)
        doc.xref_set_key(xref, "Filter", filtr or "null")
        assert doc.xref_stream(xref) == data


@pytest.mark.parametrize("policy", ["flate", "zopfli", "brotli"])
@pytest.mark.parametrize("declaration", [False, True])
def test_native_policy_never_changes_images_metadata_attachments_or_rendering(tmp_path, policy, declaration):
    from tools.bench_native_streams import image_signature, native_signature
    source, baseline, output = (tmp_path / name for name in ("source.pdf", "baseline.pdf", "out.pdf"))
    source_pdf(source)
    pipeline.save_with_spec(str(source), str(baseline), recipe("indexed"))
    pipeline.save_with_spec(str(source), str(output), dict(recipe("indexed"), stream_compression=policy,
                                                         brotli_declaration=declaration))
    with fitz.open(baseline) as before, fitz.open(output) as after:
        assert image_signature(after) == image_signature(before)
        assert native_signature(after) == native_signature(before)
        assert np.array_equal(pixels(after[0]), pixels(before[0]))
        assert after.get_xml_metadata() == before.get_xml_metadata()
        assert after.embfile_get("kept.txt") == before.embfile_get("kept.txt")
        for xref in streams.native_stream_xrefs(after):
            if not after.xref_stream(xref):
                assert after.xref_get_key(xref, "Filter")[0] == "null"
                continue
            assert after.xref_get_key(xref, "Filter")[1] == (
                "/BrotliDecode" if policy == "brotli" else "/FlateDecode")
        assert streams.brotli_declaration_present(after) is (policy == "brotli" and declaration)
        catalog = after.pdf_catalog()
        if policy == "brotli" and declaration:
            assert after.xref_get_key(catalog, "Version")[1] == "/2.0"
            assert after.xref_get_key(catalog, "Extensions/PDFa/ExtensionLevel")[1] == "1"
        else:
            assert after.xref_get_key(catalog, "Version")[0] == "null"


def test_brotli_declaration_preserves_unrelated_extensions():
    with fitz.open() as doc:
        doc.new_page().insert_text((10, 30), "Keep extensions")
        doc.xref_set_key(doc.pdf_catalog(), "Extensions/ADBE", "<< /BaseVersion /1.7 /ExtensionLevel 3 >>")
        streams.recompress_native_streams(doc, "brotli", brotli_declaration=True)
        assert doc.xref_get_key(doc.pdf_catalog(), "Extensions/ADBE/ExtensionLevel")[1] == "3"
        streams.recompress_native_streams(doc, "brotli", brotli_declaration=True)
        assert doc.xref_get_key(doc.pdf_catalog(), "Extensions/PDFa")[1].count("extension-brotli") == 1


@pytest.mark.parametrize("policy", ["flate", "zopfli", "brotli"])
def test_declaration_recipe_defaults_and_only_brotli_effective_identity(policy):
    legacy = preset_spec(dict(mode="indexed", params=dict(stream_compression=policy)))
    assert legacy["brotli_declaration"] is False
    assert spec_key(legacy) == spec_key({k: v for k, v in legacy.items() if k != "brotli_declaration"})
    enabled = dict(legacy, brotli_declaration=True)
    assert (spec_key(legacy) != spec_key(enabled)) is (policy == "brotli")


@pytest.mark.parametrize("form", ["direct", "indirect", "array", "indirect-array", "indirect-extensions"])
def test_default_removes_inherited_brotli_declaration_structurally_and_keeps_other_extensions(form):
    with fitz.open() as doc:
        doc.new_page().insert_text((10, 30), "Keep other extensions")
        catalog = doc.pdf_catalog()
        streams.set_brotli_declaration(doc, True)
        entry = doc.xref_get_key(catalog, "Extensions/PDFa")[1]
        if "array" in form:
            entry = f"[{entry} << /URL (https://example.com/other-extension) /ExtensionLevel 7 >>]"
        if form in ("indirect", "indirect-array"):
            xref = doc.get_new_xref()
            doc.update_object(xref, entry)
            entry = f"{xref} 0 R"
        doc.xref_set_key(catalog, "Extensions/PDFa", entry)
        doc.xref_set_key(catalog, "Extensions/ADBE", "<< /BaseVersion /1.7 /ExtensionLevel 3 >>")
        if form == "indirect-extensions":
            xref = doc.get_new_xref()
            doc.update_object(xref, doc.xref_get_key(catalog, "Extensions")[1])
            doc.xref_set_key(catalog, "Extensions", f"{xref} 0 R")
        assert streams.brotli_declaration_present(doc)
        streams.recompress_native_streams(doc, "brotli")
        assert not streams.brotli_declaration_present(doc)
        assert doc.xref_get_key(catalog, "Extensions/ADBE/ExtensionLevel")[1] == "3"
        assert doc.xref_get_key(catalog, "Version")[1] == "/2.0"  # never downgrade legitimate source versions
        def extension_text():
            kind, value = doc.xref_get_key(catalog, "Extensions/PDFa")
            return doc.xref_object(int(value.split()[0])) if kind == "xref" else value
        if "array" in form:
            assert "https://example.com/other-extension" in extension_text()
        else:
            assert doc.xref_get_key(catalog, "Extensions/PDFa")[0] == "null"
        streams.set_brotli_declaration(doc, True)
        streams.set_brotli_declaration(doc, True)
        assert streams.brotli_declaration_present(doc)
        assert extension_text().count("extension-brotli") == 1


def test_default_removes_empty_brotli_extension_container_without_downgrading_pdf():
    with fitz.open() as doc:
        doc.new_page()
        streams.set_brotli_declaration(doc, True)
        streams.set_brotli_declaration(doc)
        assert doc.xref_get_key(doc.pdf_catalog(), "Extensions")[0] == "null"
        assert doc.xref_get_key(doc.pdf_catalog(), "Version")[1] == "/2.0"


@pytest.mark.parametrize("failure", [False, True])
@pytest.mark.parametrize("policy", ["brotli", "best"])
def test_saver_owns_declaration_context_and_restores_it_on_success_or_failure(tmp_path, failure, policy):
    source, output = tmp_path / "source.pdf", tmp_path / "output.pdf"
    source_pdf(source)
    previous = pipeline._BROTLI_DECLARATION.set(True)
    try:
        spec = dict(mode="invalid" if failure else "passthrough", stream_compression=policy)
        if failure:
            with pytest.raises(ValueError, match="Unknown filter mode"):
                pipeline.save_with_spec(str(source), str(output), spec)
        else:
            pipeline.save_with_spec(str(source), str(output), spec)
            with fitz.open(output) as doc:
                assert not streams.brotli_declaration_present(doc)
        assert pipeline._BROTLI_DECLARATION.get() is True
    finally:
        pipeline._BROTLI_DECLARATION.reset(previous)


@pytest.mark.parametrize("policy", ["zopfli", "brotli"])
def test_native_selected_encoder_failure_does_not_fallback(tmp_path, monkeypatch, policy):
    if policy == "zopfli":
        monkeypatch.setattr(streams, "find_tool", lambda *a: None)
    else:
        monkeypatch.setattr(streams, "brotli_available", lambda: False)
    with pytest.raises(RuntimeError):
        streams.encode_stream(b"Native data", policy, directory=str(tmp_path))


def test_cancelled_selected_codecs_produce_no_output(tmp_path):
    token = CancelToken()
    token.cancel()
    for mode, _ in ALGORITHMS:
        with pytest.raises(CancelledError):
            pipeline.save_with_spec("unused", str(tmp_path / "out.pdf"), recipe(mode), token)
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("cancel", [False, True])
def test_zopfli_has_no_elapsed_cutoff_but_reaps_on_cancellation(tmp_path, monkeypatch, cancel):
    data = b"Exact native stream" * 10
    token = CancelToken()
    elapsed = [0]

    class Encoder:
        returncode = 0
        terminated = False
        calls = 0

        def communicate(self, timeout):
            self.calls += 1
            if self.calls == 1:
                elapsed[0] += 121
                if cancel:
                    token.cancel()
                raise subprocess.TimeoutExpired("zopfli", timeout)
            return zlib.compress(data, 9), b""

        def terminate(self):
            self.terminated = True

    encoder = Encoder()
    monkeypatch.setattr(streams, "find_tool", lambda *a: "/usr/bin/zopfli")
    monkeypatch.setattr(streams.subprocess, "Popen", lambda *a, **kw: encoder)
    monkeypatch.setattr(streams.time, "monotonic", lambda: elapsed[0])
    if cancel:
        with pytest.raises(CancelledError):
            streams._zopfli(data, str(tmp_path), token)
        assert encoder.terminated
    else:
        assert zlib.decompress(streams._zopfli(data, str(tmp_path), token)) == data
        assert not encoder.terminated
    assert encoder.calls == 2 and elapsed[0] > 120
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("policy", [name for name, _ in streams.STREAM_POLICIES if name != "best"])
def test_empty_native_stream_needs_no_filter_and_cannot_create_invalid_brotli(policy):
    assert streams.encode_stream(b"", policy) == (b"", None)
    with fitz.open() as doc:
        page = doc.new_page()
        xref = doc.get_new_xref()
        doc.update_object(xref, "<<>>")
        doc.update_stream(xref, b"")
        page.set_contents(xref)
        streams.recompress_native_streams(doc, policy)
        assert doc.xref_stream(xref) == b""
        assert doc.xref_get_key(xref, "Filter")[0] == "null"
