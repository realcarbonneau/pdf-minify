"""§209: size-only, same actual pixels, genuine image codecs/predictors."""

import io
import shutil

import numpy as np
import pymupdf as fitz
from PIL import Image
import pytest

from tools import bench_image_streams as study


def unpredicted(data, stride):
    result = bytearray()
    previous = [0]*stride
    for offset in range(0, len(data), stride+1):
        kind, encoded = data[offset], data[offset+1:offset+stride+1]
        row = []
        for index, byte in enumerate(encoded):
            left, up = row[index-1] if index else 0, previous[index]
            corner = previous[index-1] if index else 0
            estimate = left+up-corner
            choices = (left, up, corner)
            paeth = min(choices, key=lambda value: abs(estimate-value))
            prediction = (0, left, up, (left+up)//2, paeth)[kind]
            row.append((byte+prediction) % 256)
        result.extend(row)
        previous = row
    return bytes(result)


@pytest.mark.parametrize("bpc", [1, 2, 4, 8])
@pytest.mark.parametrize("width", [19, 32])
def test_predictor_roundtrip_preserves_all_packed_row_padding(bpc, width):
    stride, height = (width*bpc+7)//8, 17
    packed = np.random.default_rng(192).integers(0, 256, (height, stride), dtype=np.uint8).tobytes()
    predicted = study.predict_rows(packed, width, height, bpc)
    assert len(predicted) == len(packed)+height
    assert unpredicted(predicted, stride) == packed


@pytest.mark.parametrize("bpc", [1, 2, 4, 8])
@pytest.mark.parametrize("variant", ["flate-png", "zopfli-png", "brotli-png"])
def test_actual_pdf_predictors_decode_identical_odd_width_index_samples(tmp_path, bpc, variant):
    count = min(1 << bpc, 64)
    palette = np.random.default_rng(19).integers(0, 256, (count, 3), dtype=np.uint8)
    y, x = np.indices((17, 19))
    samples = ((x+y*3) % count).astype(np.uint8)
    bitmap = study.Bitmap(samples, study.pipeline.pack_indices(samples, bpc), bpc, palette)
    with fitz.open() as doc:
        page = doc.new_page(width=19, height=17)
        study.place_bitmap(doc, page, bitmap, variant, tmp_path)
        xref = page.get_images()[0][0]
        assert doc.xref_stream(xref) == bitmap.packed
        assert doc.xref_get_key(xref, "DecodeParms/Predictor")[1] == "15"
        got = np.frombuffer(fitz.Pixmap(doc, xref).samples, dtype=np.uint8).reshape(17, 19, 3)
        assert np.array_equal(got, palette[samples])


def source_pdf(path, rotation):
    with fitz.open() as doc:
        palette = np.array([(255, 255, 255), (255, 76, 35), (135, 63, 214),
                            (254, 195, 58), (241, 32, 91)], dtype=np.uint8)
        y, x = np.indices((17, 19))
        for index in range(2):
            page = doc.new_page(width=72, height=96)
            stream = io.BytesIO()
            Image.fromarray(palette[(x+y*3+index) % 5]).save(stream, "PNG")
            page.insert_image(fitz.Rect(5, 5, 65, 55), stream=stream.getvalue())
            page.insert_text((5, 76), f"Native {index}", fontsize=8)
            page.draw_line((5, 82), (65, 82), color=(0, .7, 0))
            page.insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(5, 68, 65, 78),
                              "uri": "https://example.com"})
            page.add_text_annot((55, 65), "Kept native note")
            page.set_rotation(rotation)
        page = doc.new_page(width=72, height=96)
        page.insert_text((5, 40), "Native only", fontsize=8)
        doc.save(path)


@pytest.mark.skipif(not shutil.which("jbig2"), reason="Actual size comparison requires JBIG2")
@pytest.mark.parametrize("mode", ["indexed", "indexed-ffpr", "bw-images", "bw-ffpr"])
@pytest.mark.parametrize("rotation", [0, 90])
def test_all_eight_actual_pdf_variants_share_preparation_pixels_native_policy_and_sizes(tmp_path, monkeypatch, mode, rotation):
    source = tmp_path / "source.pdf"
    source_pdf(source, rotation)
    original = source.read_bytes()
    quantize, threshold = study.pipeline._quantize_palette, study.pipeline._threshold
    calls = []
    def fit(*args):
        calls.append("palette")
        return quantize(*args)
    def bw(*args):
        calls.append("threshold")
        return threshold(*args)
    monkeypatch.setattr(study.pipeline, "_quantize_palette", fit)
    monkeypatch.setattr(study.pipeline, "_threshold", bw)
    context = study.pipeline._STREAM_POLICY.set("brotli")
    try:
        report = study.run_case(source, tmp_path / "case", mode=mode, dpi=72)
        assert study.pipeline._STREAM_POLICY.get() == "brotli"
    finally:
        study.pipeline._STREAM_POLICY.reset(context)
    assert calls == ["palette" if mode.startswith("indexed") else "threshold"] * (3 if mode.endswith("-ffpr") else 2)
    assert [result["variant"] for result in report["results"]] == list(study.VARIANTS)
    assert report["native_stream_policy"] == "flate"
    assert source.read_bytes() == original
    for result in report["results"]:
        output = study.Path(result["pdf"])
        assert result["complete_pdf_bytes"] == output.stat().st_size
        assert result["pdf_sha256"] == study.digest(output.read_bytes())
        assert result["decoded_samples_exact"] and result["actual_pages_exact"]
        with fitz.open(output) as doc:
            assert not study.streams.brotli_declaration_present(doc)
            assert result["brotli_declaration"] is False
            for xref in study.streams.native_stream_xrefs(doc):
                assert doc.xref_get_key(xref, "Filter")[1] in ("/FlateDecode", "null")
    product = tmp_path / "product.pdf"
    shared_save = study.pipeline._save_optimized_pdf
    def controlled_save(doc, path):
        study.set_pdf_id(doc, report["input_sha256"], report["prepared"], "current-flate")
        return shared_save(doc, path, no_new_id=True)
    monkeypatch.setattr(study.pipeline, "_save_optimized_pdf", controlled_save)
    study.pipeline.save_with_spec(str(source), str(product), dict(
        mode="indexed" if mode.startswith("indexed") else "bw-flate", colors=5,
        dpi=72, dpi_cap=72, strategy="otsu", t=180, force_raster=mode.endswith("-ffpr")),
        workdir=str(tmp_path))
    assert product.stat().st_size == report["results"][0]["complete_pdf_bytes"]
    serialized = study.json.dumps(report)
    assert "seconds" not in serialized and "timing" not in serialized
    assert "vs_current_flate_percent" not in serialized
    assert report["smallest"] in study.VARIANTS


def test_explicit_benchmark_codecs_fail_instead_of_silently_falling_back(tmp_path, monkeypatch):
    bitmap = study.Bitmap.bw(np.zeros((13, 19), dtype=np.uint8), "simple", 180)
    monkeypatch.setattr(study.pipeline, "encode_binary_jbig2", lambda *a: None)
    with fitz.open() as doc:
        page = doc.new_page(width=19, height=13)
        with pytest.raises(RuntimeError, match="JBIG2 failed"):
            study.place_bitmap(doc, page, bitmap, "jbig2", tmp_path)
    monkeypatch.setattr(study.streams, "find_tool", lambda *a: None)
    with pytest.raises(RuntimeError, match="Zopfli is not installed"):
        study.encoded_samples(bitmap, "zopfli-plain", tmp_path)


def test_invalid_preparation_count_and_existing_output_directory_are_rejected(tmp_path):
    source = tmp_path / "source.pdf"
    source_pdf(source, 0)
    with pytest.raises(ValueError, match="page count"):
        study.save_variant(source, tmp_path / "bad.pdf", [], "indexed", "current-flate", tmp_path)
    with pytest.raises(FileExistsError):
        study.run_case(source, tmp_path)


@pytest.mark.parametrize("mode", ["indexed", "bw-images"])
@pytest.mark.parametrize("object_streams", [False, True])
def test_no_image_recipes_save_all_variants_without_inventing_a_bitmap(tmp_path, monkeypatch, mode, object_streams):
    source = tmp_path / "native.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=84, height=96)
        page.insert_text((5, 20), "Native only", fontsize=8)
        page.draw_line((5, 30), (70, 30), color=(0, .7, 0))
        doc.save(source, use_objstms=object_streams)
    original = source.read_bytes()
    if object_streams:
        with fitz.open(source) as doc:
            assert doc.xref_get_key(-1, "Type")[1] == "/XRef"

    def forbidden(*args, **kwargs):
        pytest.fail("A no-image recipe must not fabricate or encode a bitmap")

    monkeypatch.setattr(study, "place_bitmap", forbidden)
    monkeypatch.setattr(study, "encoded_samples", forbidden)
    monkeypatch.setattr(study.pipeline, "_quantize_palette", forbidden)
    monkeypatch.setattr(study.pipeline, "_threshold", forbidden)
    report = study.run_case(source, tmp_path / mode, mode=mode, dpi=300)
    assert report["prepared"] == [None]
    assert [result["variant"] for result in report["results"]] == list(study.VARIANTS)
    assert len({result["pdf"] for result in report["results"]}) == len(study.VARIANTS)
    for result in report["results"]:
        assert result["image_objects"] == result["encoded_image_bytes"] == 0
        assert result["actual_pages_exact"] and result["decoded_samples_exact"]
        target = study.Path(result["pdf"])
        assert target.stat().st_size == result["complete_pdf_bytes"]
        with fitz.open(target) as doc:
            assert not doc[0].get_images()
            assert "Native only" in doc[0].get_text()
            assert report["input_sha256"][:16] in doc.pdf_trailer()
    assert source.read_bytes() == original


def test_resume_revalidates_existing_pdfs_and_rejects_changed_preparation(tmp_path, monkeypatch):
    source = tmp_path / "source.pdf"
    source_pdf(source, 0)
    folder = tmp_path / "case"
    variants = ("zopfli-plain", "brotli-png")
    initial = study.run_case(source, folder, dpi=72, variants=variants)
    assert "vs_current_flate_percent" not in study.json.dumps(initial)
    def forbidden(*a, **k):
        pytest.fail("A verified existing PDF must not be encoded again")
    monkeypatch.setattr(study, "save_variant", forbidden)
    resumed = study.run_case(source, folder, dpi=72, variants=variants, resume=True)
    assert all(item["reused_existing_pdf"] for item in resumed["results"])
    assert [item["complete_pdf_bytes"] for item in resumed["results"]] == [
        item["complete_pdf_bytes"] for item in initial["results"]]
    with pytest.raises(ValueError, match="changed benchmark input"):
        study.run_case(source, folder, dpi=72, colors=16, variants=variants, resume=True)


@pytest.mark.parametrize("declaration", [False, True])
def test_image_declaration_is_opt_in_and_cannot_reuse_a_different_setting(tmp_path, declaration):
    source = tmp_path / "source.pdf"
    source_pdf(source, 0)
    folder = tmp_path / "compatibility"
    variants = ("zopfli-plain", "brotli-plain")
    report = study.run_case(source, folder, dpi=72, variants=variants,
                            brotli_declaration=declaration)
    assert report["brotli_declaration"] is declaration
    for result in report["results"]:
        included = declaration and result["variant"].startswith("brotli")
        with fitz.open(result["pdf"]) as doc:
            assert study.streams.brotli_declaration_present(doc) is included
        assert result["brotli_declaration"] is included
    with pytest.raises(ValueError, match="declaration setting"):
        study.run_case(source, folder, dpi=72, variants=variants, resume=True,
                       brotli_declaration=not declaration)


def test_existing_malformed_native_path_is_recorded_not_hidden_or_misclassified(tmp_path):
    original, source = tmp_path / "original.pdf", tmp_path / "source.pdf"
    source_pdf(original, 0)
    with fitz.open(original) as doc:
        contents = doc[-1].get_contents()[0]
        doc.update_stream(contents, doc.xref_stream(contents)+b"\nh\n")
        doc.save(source)
    report = study.run_case(source, tmp_path / "case", dpi=72,
                            variants=("current-flate", "brotli-plain"))
    for item in report["results"]:
        observed = item["page_diagnostics"][-1]
        assert "closepath with no current point" in observed["original"]
        assert "closepath with no current point" in observed["output"]
        assert item["actual_pages_exact"]


def test_identifier_control_updates_actual_readback_xref_stream_trailer(tmp_path):
    source = tmp_path / "source.pdf"
    source_pdf(source, 0)
    report = study.run_case(source, tmp_path / "case", dpi=72, variants=("current-flate",))
    output = study.Path(report["results"][0]["pdf"])
    controlled = tmp_path / "controlled.pdf"
    with study.open_for_id_change(output) as doc:
        study.set_pdf_id(doc, "a"*64, report["prepared"], "different")
        assert "aaaaaaaaaaaaaaaa" in doc.pdf_trailer()
        study.pipeline._save_optimized_pdf(doc, str(controlled), no_new_id=True)
    with fitz.open(controlled) as doc:
        assert "aaaaaaaaaaaaaaaa" in doc.pdf_trailer()
