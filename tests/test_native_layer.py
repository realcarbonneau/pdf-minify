"""Native-state preservation, not sanitizer-normalized text approximations."""

import io
from pathlib import Path

import pymupdf as fitz
from PIL import Image
import pytest

from pdf_minify.core import image_layers, pipeline
from pdf_minify.core.cancel import CancelToken
from pdf_minify.core.display import DisplayPage
from pdf_minify.core.pdf_io import CancelledError
from tools import bench_image_streams as images


def pixels(page, dpi=72):
    return DisplayPage(page).render(fitz.Matrix(dpi / 72, dpi / 72)).samples


@pytest.mark.parametrize("mode", ["bw-flate", "indexed"])
def test_form_inherits_explicit_visible_text_state_after_hidden_text(tmp_path, mode):
    source, target = tmp_path / "source.pdf", tmp_path / "saved.pdf"
    image = io.BytesIO()
    # A uniform white bitmap triggers composition without introducing image
    # resampling differences into this native-text pixel identity regression.
    Image.new("RGB", (40, 40), "white").save(image, "PNG")
    with fitz.open() as stamp, fitz.open() as doc:
        child = stamp.new_page(width=60, height=60)
        child.insert_text((4, 20), "Visible", fontsize=10)
        child.insert_image(fitz.Rect(5, 30, 45, 58), stream=image.getvalue())
        page = doc.new_page(width=120, height=120)
        page.insert_font(fontname="helv")
        page.show_pdf_page(fitz.Rect(25, 25, 85, 85), stamp)
        content = page.read_contents()
        xref = doc.get_new_xref()
        doc.update_object(xref, "<<>>")
        doc.update_stream(xref, b"BT /helv 10 Tf 3 Tr 1 0 0 1 5 10 Tm (Hidden) Tj ET\nq 0 Tr\n" + content + b"\nQ")
        page.set_contents(xref)
        doc.save(source)
    pipeline.save_with_spec(str(source), str(target), dict(mode=mode, dpi=72, dpi_cap=72, colors=5))
    with fitz.open(source) as before, fitz.open(target) as after:
        images.assert_native_text(before[0], after[0])
        for dpi in (72, 144):
            assert pixels(before[0], dpi) == pixels(after[0], dpi)
        assert len(after[0].get_images(full=True)) == 1


def test_inline_samples_containing_pdf_keywords_are_not_lexed_as_operators(tmp_path):
    with fitz.open() as doc:
        page = doc.new_page(width=120, height=120)
        page.insert_font(fontname="helv")
        xref = doc.get_new_xref()
        doc.update_object(xref, "<<>>")
        samples = b" EI /Do BI BDC () "  # exactly 6 RGB pixels; false EI inside
        assert len(samples) == 18
        native = b"BT /helv 12 Tf 1 0 0 1 5 40 Tm (Kept EI BI BDC) Tj ET"
        doc.update_stream(xref, b"q 60 0 0 10 5 5 cm BI /W 6 /H 1 /BPC 8 /CS /RGB ID " + samples + b" EI Q\n" + native)
        page.set_contents(xref)
        original = page.get_text("words")
        image_layers._filter(page, CancelToken(), "foreground")
        assert page.get_text("words") == original
        assert not page.get_image_info()
        assert native in page.read_contents()


def test_repository_map_keeps_visible_glyphs_and_font_outlines(tmp_path):
    source = Path("examples/news-crater-lake-2026.pdf")
    with fitz.open(source) as original:
        for pno in (1, 3, 4, 5, 6):
            with image_layers._copy_page(original, pno) as native:
                image_layers._filter(native[0], CancelToken(), "foreground",
                                     backdrops=image_layers._page_backdrops(native[0]))
                images.assert_native_text(original[pno], native[0])
                target = tmp_path / f"native-{pno}.pdf"
                pipeline._save_optimized_pdf(native, str(target))
            with fitz.open(target) as saved:
                images.assert_native_text(original[pno], saved[0])


def test_native_foreground_checks_cancellation_outside_native_callbacks():
    token = CancelToken()
    token.cancel()
    with fitz.open() as doc:
        page = doc.new_page()
        with pytest.raises(CancelledError):
            image_layers._filter(page, token, "foreground")


def test_validation_rejects_invisible_glyphs_even_when_extraction_is_identical():
    with fitz.open() as original:
        page = original.new_page(width=120, height=120)
        page.insert_text((10, 30), "Keep visible")
        with image_layers._copy_page(original, 0) as modified:
            xref = modified[0].get_contents()[0]
            modified.update_stream(xref, b"3 Tr\n" + modified.xref_stream(xref))
            assert page.get_text("words") == modified[0].get_text("words")
            with pytest.raises(AssertionError, match="native glyph identity/style/count"):
                images.assert_native_text(page, modified[0])


def test_validation_still_checks_real_space_glyphs_not_only_semantic_letters():
    with fitz.open() as original:
        page = original.new_page(width=120, height=120)
        page.insert_font(fontname="helv")
        xref = original.get_new_xref()
        original.update_object(xref, "<<>>")
        content = b"BT /helv 10 Tf 1 0 0 1 10 30 Tm (A B) Tj ET"
        original.update_stream(xref, content)
        page.set_contents(xref)
        with image_layers._copy_page(original, 0) as modified:
            # Keep the letter positions, but replace the real space glyph by
            # a positioning adjustment. That is NOT equivalent native text.
            modified.update_stream(modified[0].get_contents()[0],
                                   content.replace(b"(A B) Tj", b"[(A) -278 (B)] TJ"))
            with pytest.raises(AssertionError, match="native glyph count"):
                images.assert_native_text(page, modified[0])


def test_validation_archives_source_warnings_without_leaking_them_into_next_codec():
    with fitz.open("examples/news-crater-lake-2026.pdf") as original:
        with image_layers._copy_page(original, 1) as native:
            image_layers._filter(native[0], CancelToken(), "foreground")
            diagnostics = images.assert_native_text(original[1], native[0])
            assert "ActualText with no position" in "\n".join(diagnostics["original"])
            assert not any(diagnostics["output"])
            assert not fitz.TOOLS.mupdf_warnings()
