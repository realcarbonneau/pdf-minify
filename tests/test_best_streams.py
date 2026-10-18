"""§§255/256: actual-file choice, exact samples, and the J* boundary."""

from collections import Counter
import errno
import hashlib
import io
from pathlib import Path
import zlib

import numpy as np
import pymupdf as fitz
from PIL import Image
import pytest

from pdf_minify.core import best_streams as best, pipeline, stream_compression as streams
from pdf_minify.core.cancel import CancelToken
from pdf_minify.core.display import DisplayPage
from pdf_minify.core.pdf_io import CancelledError
from pdf_minify.core.recipes import preset_spec, spec_key


TINY = b"\nq\n612 0 0 792 0 0 cm\n/fzImg0 Do\nQ\n"
WORDS = (b"The quick brown fox jumps over the lazy dog. This is a searchable PDF "
         b"document with native text and vector graphics. ") * 20


def resource_doc(*payloads):
    doc = fitz.open()
    doc.new_page(width=73, height=96)
    xrefs = []
    for index, data in enumerate(payloads):
        xref = doc.get_new_xref()
        # Distinct dictionaries keep duplicate payloads distinct at garbage=4.
        doc.update_object(xref, f"<< /Sample {index} >>")
        doc.update_stream(xref, data, compress=False)
        xrefs.append(xref)
    doc.xref_set_key(doc.pdf_catalog(), "BestTest", "[" + " ".join(f"{x} 0 R" for x in xrefs) + "]")
    return doc


def save(doc, target, **kwargs):
    return best.save_best_streams(doc, target, writer=pipeline._write_optimized_pdf,
                                  directory=str(target.parent), **kwargs)


def pdf_ids(doc):
    m = fitz.mupdf
    native = m.pdf_document_from_fz_document(doc.this)
    ids = m.pdf_dict_gets(m.pdf_trailer(native), "ID")
    return tuple(m.pdf_sprint_obj(None, 0, m.pdf_array_get(ids, i), True, True)[0]
                 for i in range(m.pdf_array_len(ids)))


@pytest.mark.parametrize("size", [9, 99, 999])
def test_local_cost_includes_filter_names_and_length_digits(size):
    assert best._stored_cost(size, "/FlateDecode") == size + 12 + len(str(size))
    assert best._stored_cost(size, "/BrotliDecode") == size + 13 + len(str(size))
    # A one-byte Brotli payload reduction can tie after its longer filter name.
    assert best._stored_cost(size-1, "/BrotliDecode") == size + 12 + len(str(size))


def test_length_digit_boundary_counts_towards_a_real_stream_saving():
    assert best._stored_cost(99, "/BrotliDecode") < best._stored_cost(100, "/FlateDecode")


def test_best_measures_both_homogeneous_controls_and_a_mixed_winner(tmp_path):
    with resource_doc(TINY, WORDS) as doc:
        stats = save(doc, tmp_path / "best.pdf")
    assert set(stats["candidate_bytes"]) == {"zopfli", "brotli", "mixed"}
    assert stats["winner"] == "mixed" and stats["brotli_streams"] == 1
    assert stats["file_bytes"] == (tmp_path / "best.pdf").stat().st_size
    assert stats["file_bytes"] == min(stats["candidate_bytes"].values())
    with fitz.open(tmp_path / "best.pdf") as doc:
        observed = {doc.xref_stream(x): doc.xref_get_key(x, "Filter")[1]
                    for x in streams.native_stream_xrefs(doc)}
        assert observed == {TINY: "/FlateDecode", WORDS: "/BrotliDecode"}
    assert {path.name for path in tmp_path.iterdir()} == {"best.pdf"}


def test_file_overhead_can_overrule_the_local_brotli_choice(tmp_path):
    choices = [streams.encode_stream(WORDS, policy) for policy in ("zopfli", "brotli")]
    assert best._stored_cost(len(choices[1][0]), choices[1][1]) < best._stored_cost(len(choices[0][0]), choices[0][1])
    with resource_doc(WORDS) as doc:
        stats = save(doc, tmp_path / "best.pdf", brotli_declaration=True)
    assert stats["winner"] == "zopfli" and not stats["brotli_streams"]
    assert stats["file_bytes"] < stats["candidate_bytes"]["brotli"]
    with fitz.open(tmp_path / "best.pdf") as doc:
        assert not streams.brotli_declaration_present(doc)


def test_identical_inputs_are_encoded_once_per_encoder_not_once_per_candidate(tmp_path, monkeypatch):
    calls = Counter()
    encode = streams.encode_stream

    def record(data, policy, **kwargs):
        calls[data, policy] += 1
        return encode(data, policy, **kwargs)

    monkeypatch.setattr(streams, "encode_stream", record)
    with resource_doc(TINY, TINY, WORDS, WORDS) as doc:
        stats = save(doc, tmp_path / "best.pdf")
    assert stats["streams"] == 4
    assert calls == Counter({(data, policy): 1 for data in (TINY, WORDS)
                             for policy in ("zopfli", "brotli")})


def test_empty_streams_and_an_empty_page_never_need_a_brotli_encoder(tmp_path, monkeypatch):
    monkeypatch.setattr(streams, "_brotli", lambda *args: pytest.fail("empty Brotli encoding"))
    monkeypatch.setattr(streams, "_zopfli", lambda *args: pytest.fail("empty Zopfli encoding"))
    for index, payloads in enumerate(((), (b"",))):
        target = tmp_path / f"empty-{index}.pdf"
        with resource_doc(*payloads) as doc:
            stats = save(doc, target, brotli_declaration=True)
        assert stats["brotli_streams"] == 0 and stats["encoded_bytes"] == 0
        assert len(stats["candidate_bytes"]) == 1
        with fitz.open(target) as doc:
            assert not streams.brotli_declaration_present(doc)
            for xref in streams.native_stream_xrefs(doc):
                assert doc.xref_stream(xref) == b""
                assert doc.xref_get_key(xref, "Filter")[0] == "null"


@pytest.mark.parametrize("no_new_id", [False, True])
@pytest.mark.parametrize("xref_source", [False, True])
def test_all_trials_share_ids_and_preserve_the_permanent_binary_id(tmp_path, no_new_id, xref_source):
    original_ids = "[<000102030405060708090a0b0c0dfeff> <fffefdfcfbfaf9f8f7f6f5f4f3f2f100>]"
    with resource_doc(TINY, WORDS) as source:
        source.xref_set_key(-1, "ID", original_ids)
        expected = pdf_ids(source)
        snapshot = source.tobytes(use_objstms=xref_source, no_new_id=True)
    observed = []

    def writer(doc, path, **kwargs):
        observed.append(pdf_ids(doc))
        pipeline._write_optimized_pdf(doc, path, **kwargs)
        with fitz.open(path) as stored:
            assert pdf_ids(stored) == observed[-1]

    with fitz.open(stream=snapshot, filetype="pdf") as doc:
        best.save_best_streams(doc, tmp_path / "best.pdf", writer=writer,
                               directory=str(tmp_path), no_new_id=no_new_id)
    assert len(observed) == 3 and len(set(observed)) == 1
    assert observed[0][0] == expected[0]
    assert (observed[0][1] == expected[1]) is no_new_id


def test_no_new_id_preserves_an_absent_id_instead_of_generating_one(tmp_path):
    with resource_doc(TINY) as doc:
        assert not pdf_ids(doc)
        save(doc, tmp_path / "best.pdf", no_new_id=True)
    with fitz.open(tmp_path / "best.pdf") as doc:
        assert not pdf_ids(doc)


@pytest.mark.parametrize("failure", ["zopfli", "brotli", "corrupt", "cancel"])
def test_failure_or_cancellation_preserves_existing_output_and_cleans_trials(tmp_path, monkeypatch, failure):
    target = tmp_path / "completed.pdf"
    target.write_bytes(b"previous completed result")
    token = CancelToken()
    encode = streams.encode_stream

    def broken(data, policy, **kwargs):
        if policy == failure:
            raise RuntimeError(f"{policy} unavailable")
        if failure == "corrupt" and policy == "brotli":
            return zlib.compress(b"different decoded content"), "/FlateDecode"
        return encode(data, policy, **kwargs)

    def writer(doc, path, **kwargs):
        pipeline._write_optimized_pdf(doc, path, **kwargs)
        if failure == "cancel":
            token.cancel()

    monkeypatch.setattr(streams, "encode_stream", broken)
    with resource_doc(TINY, WORDS) as doc, pytest.raises(CancelledError if failure == "cancel" else RuntimeError):
        best.save_best_streams(doc, target, writer=writer, directory=str(tmp_path), token=token)
    assert target.read_bytes() == b"previous completed result"
    assert {path.name for path in tmp_path.iterdir()} == {"completed.pdf"}


def test_saved_file_readback_rejects_writer_corruption_before_publication(tmp_path):
    target = tmp_path / "completed.pdf"
    target.write_bytes(b"previous completed result")

    def corrupt_writer(doc, path, **kwargs):
        xref = next(streams.native_stream_xrefs(doc))
        doc.update_stream(xref, b"different content", compress=False)
        doc.xref_set_key(xref, "Filter", "null")
        pipeline._write_optimized_pdf(doc, path, **kwargs)

    with resource_doc(TINY, WORDS) as doc, pytest.raises(RuntimeError, match="saved-file"):
        best.save_best_streams(doc, target, writer=corrupt_writer, directory=str(tmp_path))
    assert target.read_bytes() == b"previous completed result"
    assert {path.name for path in tmp_path.iterdir()} == {"completed.pdf"}


def test_both_encoded_alternatives_are_disk_artifacts_not_cached_decoded_pages(tmp_path):
    with resource_doc(TINY, TINY, WORDS) as doc:
        pairs, _ = best._encode_pairs(doc, str(tmp_path), CancelToken())
        assert len(pairs) == 3
        assert pairs[0].zopfli is pairs[1].zopfli
        assert len(list(tmp_path.glob("stream-*.bin"))) == 4
        for pair in pairs:
            for choice in (pair.zopfli, pair.brotli):
                assert choice.path.stat().st_size == choice.size


@pytest.mark.parametrize("array", [False, True])
def test_jbig2_shared_dictionary_is_not_treated_as_a_native_stream(array):
    # Structurally inspect the boundary without claiming this dummy dictionary
    # is a valid image or a new symbol-mode encoding feature.
    with resource_doc(b"dummy shared JBIG2 dictionary") as doc:
        shared = next(streams.native_stream_xrefs(doc))
        image = doc.get_new_xref()
        params = f"<< /JBIG2Globals {shared} 0 R >>"
        if array:
            params = f"[ {params} ]"
        doc.update_object(image, f"<< /Type /XObject /Subtype /Image /Width 1 /Height 1 "
                                 f"/BitsPerComponent 1 /Filter /JBIG2Decode /DecodeParms {params} >>")
        doc.update_stream(image, b"dummy JBIG2 image", compress=False)
        doc.xref_set_key(image, "Filter", "/JBIG2Decode")
        doc.xref_set_key(image, "DecodeParms", params)
        assert {shared, image} <= best._protected_xrefs(doc)
        assert not list(best._eligible_xrefs(doc))


def test_exact_file_ties_prefer_fewer_brotli_streams(tmp_path):
    def writer(doc, path, **kwargs):
        pipeline._write_optimized_pdf(doc, path, **kwargs)
        # Legal trailing whitespace makes every ACTUALLY saved file the same
        # length; test tie-breaking, not an estimator or mocked stat result.
        with open(path, "ab") as output:
            output.write(b" " * (8000 - Path(path).stat().st_size))

    with resource_doc(TINY, WORDS) as doc:
        stats = best.save_best_streams(doc, tmp_path / "best.pdf", writer=writer, directory=str(tmp_path))
    assert set(stats["candidate_bytes"].values()) == {8000}
    assert stats["winner"] == "zopfli" and stats["brotli_streams"] == 0


def test_cross_filesystem_publication_is_atomic_and_cancellable(tmp_path, monkeypatch):
    candidate, target = tmp_path / "trial.pdf", tmp_path / "finished.pdf"
    candidate.write_bytes(b"new completed result")
    target.write_bytes(b"old completed result")
    replace = best.os.replace
    token = CancelToken()

    def cross_device(source, destination):
        if source == candidate:
            raise OSError(errno.EXDEV, "different devices")
        return replace(source, destination)

    monkeypatch.setattr(best.os, "replace", cross_device)
    copyfile = best.shutil.copyfile

    def cancel_after_copy(source, destination):
        copyfile(source, destination)
        token.cancel()

    monkeypatch.setattr(best.shutil, "copyfile", cancel_after_copy)
    with pytest.raises(CancelledError):
        best._publish(candidate, target, token)
    assert target.read_bytes() == b"old completed result"
    assert {path.name for path in tmp_path.iterdir()} == {"trial.pdf", "finished.pdf"}
    token = CancelToken()
    monkeypatch.setattr(best.shutil, "copyfile", copyfile)
    best._publish(candidate, target, token)
    assert target.read_bytes() == b"new completed result"


def source_pdf(path):
    palette = np.array([(255, 255, 255), (255, 76, 35), (135, 63, 214),
                        (254, 195, 58), (241, 32, 91)], dtype=np.uint8)
    y, x = np.indices((69, 73))
    with fitz.open() as doc:
        for index in range(2):
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


def image_samples(doc):
    return Counter((hashlib.sha256(doc.xref_stream(xref)).digest(),
                    *(doc.xref_get_key(xref, key)[1] for key in
                      ("Width", "Height", "BitsPerComponent", "ImageMask", "ColorSpace", "Decode")))
                   for xref in range(1, doc.xref_length())
                   if doc.xref_is_stream(xref) and doc.xref_get_key(xref, "Subtype")[1] == "/Image")


@pytest.mark.parametrize("mode,lossless", [(mode, True) for mode in
                                         ("bw", "layered-jbig2", "color", "jpx", "bw-flate", "indexed")]
                                        + [("jpx", False)])
@pytest.mark.parametrize("force", [False, True])
def test_real_filter_flow_preserves_exact_pages_and_specialized_payloads(tmp_path, monkeypatch, mode, lossless, force):
    from tools.bench_native_streams import image_signature, native_signature

    source, reference, target = [tmp_path / name for name in ("source.pdf", "reference.pdf", "best.pdf")]
    source_pdf(source)
    original_hash = hashlib.sha256(source.read_bytes()).digest()
    spec = preset_spec(dict(mode=mode, params=dict(dpi=72, dpi_cap=72, colors=5,
                                                  force_raster=force, lossless=lossless)))
    pipeline.save_with_spec(str(source), str(reference), spec, workdir=str(tmp_path))
    observed = []
    saver = best.save_best_streams

    def record(*args, **kwargs):
        stats = saver(*args, **kwargs)
        observed.append(stats)
        return stats

    monkeypatch.setattr(best, "save_best_streams", record)
    pipeline.save_with_spec(str(source), str(target), dict(spec, stream_compression="best"),
                            workdir=str(tmp_path))
    stats, = observed
    packed = mode in ("indexed", "bw-flate")
    assert (stats["image_streams"] > 0) is packed
    assert (stats["predictable_images"] > 0) is packed
    if not packed:
        assert stats["png_prediction_on_streams"] == 0
    assert target.stat().st_size == min(stats["candidate_bytes"].values())
    with fitz.open(reference) as before, fitz.open(target) as after:
        if packed:
            assert image_samples(after) == image_samples(before)
        else:
            assert image_signature(after) == image_signature(before)
        assert native_signature(after) == native_signature(before)
        assert after.get_xml_metadata() == before.get_xml_metadata()
        assert after.embfile_names() == before.embfile_names()
        for name in before.embfile_names():
            assert after.embfile_get(name) == before.embfile_get(name)
        for original, actual in zip(before, after):
            assert actual.rect == original.rect and actual.rotation == original.rotation
            assert actual.get_text("words") == original.get_text("words")
            assert actual.get_drawings() == original.get_drawings()
            assert [link["uri"] for link in actual.get_links()] == [link["uri"] for link in original.get_links()]
            for zoom in (1, 2, 4):
                matrix = fitz.Matrix(zoom, zoom)
                assert DisplayPage(actual).render(matrix).samples == DisplayPage(original).render(matrix).samples
    assert hashlib.sha256(source.read_bytes()).digest() == original_hash
    assert not list(tmp_path.glob("best-streams-*"))


@pytest.mark.parametrize("indirect", [False, True])
@pytest.mark.parametrize("prediction", ["preserve", "best"])
def test_png_mask_pixels_stay_exact_and_frozen_prediction_is_supported(tmp_path, indirect, prediction):
    with fitz.open() as doc:
        page = doc.new_page(width=17, height=13)
        raw = bytes((x * 11 + y * 7) % 256 for y in range(13) for x in range(17))
        predicted = b"".join(b"\0" + raw[y*17:(y+1)*17] for y in range(13))
        parms = "<< /Predictor 15 /Colors 1 /BitsPerComponent 8 /Columns 17 >>"
        if indirect:
            pxref = doc.get_new_xref()
            doc.update_object(pxref, parms)
            parms = f"{pxref} 0 R"
        mask = doc.get_new_xref()
        doc.update_object(mask, "<< /Type /XObject /Subtype /Image /Width 17 /Height 13 "
                               "/ColorSpace /DeviceGray /BitsPerComponent 8 >>")
        doc.update_stream(mask, zlib.compress(predicted), compress=False)
        doc.xref_set_key(mask, "Filter", "/FlateDecode")
        doc.xref_set_key(mask, "DecodeParms", parms)
        assert doc.xref_stream(mask) == raw
        data = io.BytesIO()
        Image.new("RGB", (17, 13), "red").save(data, "PNG")
        image = page.insert_image(page.rect, stream=data.getvalue())
        doc.xref_set_key(image, "SMask", f"{mask} 0 R")
        # Compare saved PDFs. insert_image caches a decoded Pixmap; attaching
        # a soft mask afterward makes its in-memory rendering differ from a
        # fresh reader even with the unchanged writer (one-level alpha rounding).
        # That construction cache is not the Best baseline.
        baseline = tmp_path / "reference.pdf"
        pipeline._write_optimized_pdf(doc, str(baseline), no_new_id=True)
        with fitz.open(baseline) as stored:
            before = DisplayPage(stored[0]).render().samples
        stats = save(doc, tmp_path / "best.pdf", image_prediction=prediction)
        assert stats["image_streams"] == 2
    with fitz.open(tmp_path / "best.pdf") as doc:
        assert DisplayPage(doc[0]).render().samples == before
        image = doc[0].get_images()[0][0]
        mask = int(doc.xref_get_key(image, "SMask")[1].split()[0])
        assert doc.xref_stream(mask) == raw
        if prediction == "preserve":
            assert doc.xref_get_key(mask, "DecodeParms/Predictor")[1] == "15"
            doc.xref_set_key(mask, "DecodeParms", "null")
            assert doc.xref_stream(mask) == predicted
        else:
            assert stats["predictable_images"] == 2


def test_source_ccitt_is_converted_not_preserved_as_an_output_exception(tmp_path):
    # Genuine Group-4 fax data is a supported INPUT, not a product output codec.
    image = Image.new("1", (37, 41), 1)
    for y in range(5, 36):
        for x in range(4, 33):
            image.putpixel((x, y), (x//3+y//4) % 2)
    tiff = io.BytesIO()
    image.save(tiff, "TIFF", compression="group4")
    with Image.open(io.BytesIO(tiff.getvalue())) as encoded:
        offset, = encoded.tag_v2[273]
        length, = encoded.tag_v2[279]
    source, target = tmp_path / "fax.pdf", tmp_path / "converted.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=37, height=41)
        xref = doc.get_new_xref()
        doc.update_object(xref, "<< /Type /XObject /Subtype /Image /Width 37 /Height 41 "
                                "/ColorSpace /DeviceGray /BitsPerComponent 1 "
                                "/Filter /CCITTFaxDecode "
                                "/DecodeParms << /K -1 /Columns 37 /Rows 41 >> >>")
        doc.update_stream(xref, tiff.getvalue()[offset:offset+length], compress=False)
        doc.xref_set_key(xref, "Filter", "/CCITTFaxDecode")
        doc.xref_set_key(xref, "DecodeParms", "<< /K -1 /Columns 37 /Rows 41 /BlackIs1 true >>")
        page.insert_image(page.rect, xref=xref)
        doc.save(source)
    with fitz.open(source) as doc:
        assert doc.xref_get_key(doc[0].get_images()[0][0], "Filter")[1] == "/CCITTFaxDecode"
        assert DisplayPage(doc[0]).render().samples == image.convert("RGB").tobytes()
    for mode in ("bw", "bw-flate", "indexed", "layered-jbig2", "jpx", "color"):
        spec = preset_spec(dict(mode=mode, params=dict(dpi=72, dpi_cap=72, colors=5,
                                                       stream_compression="best")))
        pipeline.save_with_spec(str(source), str(target), spec, workdir=str(tmp_path))
        with fitz.open(target) as doc:
            filters = [doc.xref_get_key(x, "Filter")[1] for x in range(1, doc.xref_length())
                       if doc.xref_is_stream(x) and doc.xref_get_key(x, "Subtype")[1] == "/Image"]
            assert filters and "/CCITTFaxDecode" not in filters


def test_best_recipe_identity_includes_compatibility_without_migrating_existing_defaults():
    original = preset_spec(dict(mode="indexed", params={}))
    chosen = dict(original, stream_compression="best")
    assert original["stream_compression"] == "flate"
    assert spec_key(chosen) != spec_key(original)
    assert spec_key(chosen) != spec_key(dict(chosen, brotli_declaration=True))
    assert streams.STREAM_LABELS["best"] == "Best (Zopfli/Brotli)"


def test_prepare_and_subset_once_without_opportunistic_then_full_reencoding(tmp_path, monkeypatch):
    source, target = tmp_path / "source.pdf", tmp_path / "best.pdf"
    source_pdf(source)
    counts = Counter()
    compose = pipeline.compose_color_page
    subset = fitz.Document.subset_fonts
    encode = streams._zopfli

    def compose_once(*args, **kwargs):
        counts["compose"] += 1
        return compose(*args, **kwargs)

    def subset_once(*args, **kwargs):
        counts["subset"] += 1
        return subset(*args, **kwargs)

    encoded_inputs = Counter()

    def encode_once(data, *args, **kwargs):
        encoded_inputs[hashlib.sha256(data).digest()] += 1
        return encode(data, *args, **kwargs)

    monkeypatch.setattr(pipeline, "compose_color_page", compose_once)
    monkeypatch.setattr(fitz.Document, "subset_fonts", subset_once)
    monkeypatch.setattr(streams, "_zopfli", encode_once)
    monkeypatch.setattr(pipeline, "zopfli_binary", lambda: pytest.fail("old opportunistic image encoder"))
    spec = preset_spec(dict(mode="indexed", params=dict(dpi_cap=72, colors=5, stream_compression="best")))
    pipeline.save_with_spec(str(source), str(target), spec, workdir=str(tmp_path))
    assert counts == {"compose": 2, "subset": 1}
    assert encoded_inputs and set(encoded_inputs.values()) == {1}
