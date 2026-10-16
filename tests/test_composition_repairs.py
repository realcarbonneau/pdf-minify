"""B108–B110, uniform defaults and color FFPR through the real saver."""

import io
from pathlib import Path

import numpy as np
import pymupdf as fitz
from PIL import Image
import pytest

from pdf_minimalist.core import pipeline, presets, image_layers
from pdf_minimalist.core.algorithms import ALGORITHMS, BW_MODES, with_algorithm
from pdf_minimalist.core.cancel import CancelToken
from pdf_minimalist.core.display import DisplayPage
from pdf_minimalist.core.recipes import preset_spec, spec_key
from pdf_minimalist.core.stencils import PaletteCanvas
from tools import bench_image_streams as images
from tools import bench_compression_overview as overview


def png(image):
    buf = io.BytesIO()
    image.save(buf, "PNG")
    return buf.getvalue()


def pixels(page, dpi):
    pix = DisplayPage(page).render(fitz.Matrix(dpi / 72, dpi / 72))
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)


def fixture(path, *, rotation=0):
    with fitz.open() as doc:
        page = doc.new_page(width=96, height=120)
        page.insert_text((4, 16), "Native text", fontsize=10, color=(0, 0, 1))
        page.draw_rect(fitz.Rect(4, 21, 91, 28), fill=(1, 0, 0), color=None)
        page.insert_image(fitz.Rect(7, 34, 87, 110),
                          stream=png(Image.new("RGB", (10, 10), (32, 156, 232))))
        page.set_rotation(rotation)
        doc.save(path)


def test_every_builtin_and_missing_recipe_defaults_to_300dpi():
    for preset in presets.PRESETS:
        if preset["mode"] != "passthrough":
            spec = preset_spec(preset)
            assert spec.get("dpi", spec.get("dpi_cap")) == 300
    for mode, _ in ALGORITHMS:
        field = "dpi" if mode in BW_MODES else "dpi_cap"
        assert preset_spec(dict(mode=mode))[field] == 300
        assert with_algorithm(dict(mode=mode), mode)[field] == 300
        # Pure recipe normalization keeps explicit values; settings loading
        # performs the separately authorized, revision-gated migration (§226).
        assert preset_spec(dict(mode=mode, params={field: 150}))[field] == 150


def test_uniform_overview_covers_color_ffpr_and_has_no_low_dpi_recipes():
    assert overview.BENCHMARK_DPI == 300
    families = {row.family for row in overview.ROWS}
    assert {"indexed-ffpr", "jpeg-q50-ffpr", "jpx-r192-ffpr", "jpx-lossless-ffpr"} <= families
    for row in overview.ROWS:
        assert "300dpi" in overview.case_id("example.pdf", row.family)
        if row.family.endswith("-ffpr") and row.variant == "jbig2":
            assert row.native == "zopfli"


def test_filter_options_explicitly_override_poisoned_native_no_update(tmp_path, monkeypatch):
    source = tmp_path / "source.pdf"
    fixture(source)
    constructor = image_layers.m.PdfFilterOptions
    calls = []
    def poisoned():
        options = constructor()
        options.no_update = 123456  # deterministic reproduction of B110
        calls.append(options)
        return options
    monkeypatch.setattr(image_layers.m, "PdfFilterOptions", poisoned)
    with fitz.open(source) as original:
        for _ in range(6):
            with image_layers._copy_page(original, 0) as doc:
                image_layers._filter(doc[0], CancelToken(), "canvas")
                assert len(doc[0].get_images(full=True)) == 1
                assert not doc[0].get_text("words")
    assert len(calls) == 6 and all(options.no_update == 0 for options in calls)


def test_orphan_image_tag_is_repaired_but_positioned_actualtext_is_kept(tmp_path):
    source, output = tmp_path / "tags.pdf", tmp_path / "result.pdf"
    fixture(source)
    with fitz.open(source) as doc:
        page = doc[0]
        ops = page.get_contents()
        # Whitespace ActualText around the image becomes disconnected when
        # its paint is removed; retain its MCID, clipping and other metadata.
        image_ops = doc.xref_stream(ops[-1])
        doc.update_stream(ops[-1], b"/Figure <</ActualText ( ) /MCID 1 /Alt <FEFF00E9>>> BDC q 0 0 96 120 re W n " + image_ops + b" Q EMC")
        text_ops = doc.xref_stream(ops[0])
        doc.update_stream(ops[0], b"/Span <</ActualText (Kept BDC BI ActualText) /MCID 2>> BDC " + text_ops + b" EMC")
        tagged = tmp_path / "tagged.pdf"
        doc.save(tagged)
    fitz.TOOLS.mupdf_warnings()
    pipeline.save_with_spec(str(tagged), str(output), dict(mode="indexed", dpi_cap=72, colors=5))
    fitz.TOOLS.mupdf_warnings()  # separate transient raster-fragment diagnostics
    with fitz.open(tagged) as before, fitz.open(output) as after:
        assert before[0].get_text("words") == after[0].get_text("words")
        pixels(after[0], 72)
        assert not fitz.TOOLS.mupdf_warnings()
        content = b"\n".join(after.xref_stream(i) for i in range(1, after.xref_length())
                             if after.xref_is_stream(i) and after.xref_get_key(i, "Subtype")[1] != "/Image")
        assert b"Kept BDC BI ActualText" in content
        assert b"/MCID 1" in content and b"FEFF00E9" in content.upper()


@pytest.mark.parametrize("mode", ["bw-flate", "indexed"])
def test_photo_page_repeated_saves_never_retain_source_photos_or_new_diagnostics(tmp_path, mode):
    source = tmp_path / "photo.pdf"
    with fitz.open("examples/news-crater-lake-2026.pdf") as original:
        with image_layers._copy_page(original, 0) as doc:
            doc.save(source)
    for repeat in range(3):
        target = tmp_path / f"{mode}-{repeat}.pdf"
        pipeline.save_with_spec(str(source), str(target),
                                dict(mode=mode, dpi=72, dpi_cap=72, colors=5))
        assert overview.native_diagnostics(target) == [set()]
        with fitz.open(source) as before, fitz.open(target) as after:
            images.assert_native_text(before[0], after[0])
            saved = after[0].get_images(full=True)
            assert len(saved) == 1 and saved[0][8] == "FlateDecode"
            source_photos = {images.digest(before.xref_stream_raw(e[0])) for e in before[0].get_images(full=True)}
            saved_streams = {images.digest(after.xref_stream_raw(i)) for i in range(1, after.xref_length())
                             if after.xref_is_stream(i)}
            assert not source_photos & saved_streams
            # Genuine grayscale masks of retained native vector borders are
            # not the removed ICCBased color photos and must keep their opacity.


@pytest.mark.parametrize("dpi", [72, 150, 300])
def test_colored_stencils_match_indexed_on_fractional_page_edges(tmp_path, dpi):
    source = tmp_path / "fractional.pdf"
    width, height = 60.6719970703125, 78.95999755859375
    rgb = np.full((31, 23, 3), 255, np.uint8)
    rgb[:, -2:] = (255, 76, 35)
    rgb[-2:, :] = (12, 102, 231)
    with fitz.open() as doc:
        page = doc.new_page(width=width, height=height)
        page.insert_image(page.rect, stream=png(Image.fromarray(rgb)), keep_proportion=False)
        doc.save(source)
    outputs = []
    for mode in ("indexed", "layered-jbig2"):
        target = tmp_path / f"{mode}.pdf"
        pipeline.save_with_spec(str(source), str(target), dict(mode=mode, dpi_cap=dpi, colors=5))
        outputs.append(fitz.open(target))
    try:
        for scale in (72, dpi, 600):
            assert np.array_equal(pixels(outputs[0][0], scale), pixels(outputs[1][0], scale))
        assert not outputs[1][0].get_xobjects()  # no nested canvas clipping
    finally:
        for doc in outputs:
            doc.close()


@pytest.mark.parametrize("mode", ["color", "jpx", "indexed", "layered-jbig2"])
@pytest.mark.parametrize("rotation", [0, 90])
def test_color_ffpr_uses_selected_codec_and_removes_native_text(tmp_path, mode, rotation):
    source, target = tmp_path / "source.pdf", tmp_path / "ffpr.pdf"
    fixture(source, rotation=rotation)
    recipe = dict(mode=mode, force_raster=True, dpi_cap=144, colors=5, lossless=True, jpeg_q=50)
    assert spec_key(recipe) != spec_key(dict(recipe, force_raster=False))
    assert spec_key(recipe) != spec_key(dict(recipe, page_size="letter"))
    pipeline.save_with_spec(str(source), str(target), recipe)
    with fitz.open(source) as before, fitz.open(target) as after:
        assert len(after) == 1 and not after[0].get_text("words") and not after[0].get_fonts(full=True)
        assert after[0].rect == before[0].rect
        entries = after[0].get_images(full=True)
        expected = (before[0].rect * fitz.Matrix(2, 2)).irect
        assert entries and all(e[2:4] == (expected.width, expected.height) for e in entries)
        filtr = {"color": "DCTDecode", "jpx": "JPXDecode", "indexed": "FlateDecode", "layered-jbig2": "JBIG2Decode"}[mode]
        assert all(e[8] == filtr for e in entries)
        if mode == "jpx":
            assert np.array_equal(pixels(before[0], 144), pixels(after[0], 144))


def test_native_only_pages_are_also_processed_by_color_ffpr(tmp_path):
    source, target = tmp_path / "native.pdf", tmp_path / "ffpr.pdf"
    with fitz.open() as doc:
        doc.new_page(width=96, height=120).insert_text((4, 25), "Native only")
        doc.save(source)
    pipeline.save_with_spec(str(source), str(target), dict(mode="jpx", force_raster=True, lossless=True))
    with fitz.open(target) as doc:
        assert not doc[0].get_text("words")
        assert doc[0].get_images()[0][2:4] == (400, 500)


def test_native_glyph_validation_accepts_regrouping_not_changed_glyphs(tmp_path):
    source, target = tmp_path / "mixed.pdf", tmp_path / "saved.pdf"
    with fitz.open("examples/paper-arxiv-1406.2661.pdf") as original:
        # Page 6's original 48 runs become 68 while its 1,900 glyphs remain.
        with image_layers._copy_page(original, 5) as doc:
            doc.save(source)
    pipeline.save_with_spec(str(source), str(target), dict(mode="indexed", dpi_cap=72, colors=16))
    with fitz.open(source) as before, fitz.open(target) as after:
        after[0].clean_contents()  # deliberate equivalent run regrouping
        assert len(before[0].get_texttrace()) != len(after[0].get_texttrace())
        images.assert_native_text(before[0], after[0])
    with fitz.open(target) as doc:
        doc[0].insert_text((10, 10), "Changed glyphs")
        with fitz.open(source) as original:
            with pytest.raises(AssertionError, match="native character count|native glyph"):
                images.assert_native_text(original[0], doc[0])


def test_tag_repair_checks_cancellation_between_native_tokens():
    from pdf_minimalist.core.marked_content import _repair_stream
    from pdf_minimalist.core.pdf_io import CancelledError
    token = CancelToken()
    token.cancel()
    with pytest.raises(CancelledError):
        _repair_stream(b"q Q", None, None, token)
