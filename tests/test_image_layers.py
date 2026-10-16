"""Real-file ordered composition, native artwork, alpha and DPI regressions."""
import io
from pathlib import Path

import fitz
import numpy as np
from PIL import Image
import pytest

from pdf_minimalist.core import pipeline
from pdf_minimalist.core.display import DisplayPage


def _png(array):
    stream = io.BytesIO()
    Image.fromarray(array).save(stream, "PNG")
    return stream.getvalue()


def _pixels(page, dpi=72):
    pix = page.get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False, annots=False)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)


def _save(source, output, *, dpi=72, mode="bw"):
    pipeline.save_with_spec(str(source), str(output), dict(
        mode=mode, force_raster=False, strategy="simple", t=128,
        dpi=dpi, page_size="original"))


def _actual_images(page):
    return page.get_image_info(xrefs=True)


def test_overlapping_images_combine_without_duplicate_mask_or_glyphs(tmp_path):
    source, output = tmp_path / "overlap.pdf", tmp_path / "bw.pdf"
    black = np.zeros((64, 64, 3), dtype=np.uint8)
    overlay = np.full((64, 64, 4), 255, dtype=np.uint8)
    overlay[:32, :, :3] = 0
    overlay[32:, :, 3] = 0
    with fitz.open() as doc:
        page = doc.new_page(width=144, height=180)
        page.draw_rect(page.rect, color=None, fill=(1, 1, 1))
        page.insert_text((10, 25), "Native text", color=(0, 0, 1))
        page.insert_image(fitz.Rect(10, 40, 74, 104), stream=_png(black))
        page.insert_image(fitz.Rect(46, 40, 110, 104), stream=_png(overlay))
        page.draw_rect(fitz.Rect(10, 140, 110, 155), color=(1, 0, 0))
        page.insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(10, 10, 100, 30),
                          "uri": "https://example.com/"})
        page.add_text_annot((125, 15), "Retain annotation")
        doc.save(source)
    _save(source, output)
    with fitz.open(source) as before, fitz.open(output) as after:
        assert np.array_equal(_pixels(before[0]), _pixels(after[0]))
        assert before[0].get_text("words") == after[0].get_text("words")
        assert before[0].get_fonts()[0][3] == after[0].get_fonts(full=True)[0][3]
        assert len(after[0].get_drawings()) == len(before[0].get_drawings())
        assert len(_actual_images(after[0])) == 1
        entries = after[0].get_images(full=True)
        assert len(entries) == 1 and entries[0][1] == 0
        assert after.xref_get_key(entries[0][0], "BitsPerComponent")[1] == "1"
        assert after[0].get_links()[0]["uri"] == "https://example.com/"
        assert next(after[0].annots()).info["content"] == "Retain annotation"


@pytest.mark.parametrize("mode", ["bw", "bw-flate"])
def test_simple_canvas_has_native_overlay_and_no_image_masks(tmp_path, monkeypatch, mode):
    if mode == "bw-flate":
        monkeypatch.setattr(pipeline, "bw_page_jbig2",
                            lambda *a, **k: pytest.fail("Explicit Flate must not call JBIG2"))
    source, output = tmp_path / "ordered.pdf", tmp_path / "bw.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=144, height=180)
        page.draw_rect(page.rect, color=None, fill=(0, .8, .2))
        page.insert_text((10, 55), "Behind", color=(1, 0, 0), fontsize=18)
        for i, alpha in enumerate((128, 204)):
            rgba = np.zeros((48, 48, 4), dtype=np.uint8)
            rgba[:, :, 3] = alpha
            page.insert_image(fitz.Rect(25, 30 + i * 80, 73, 78 + i * 80), stream=_png(rgba))
            if i == 0:
                page.draw_rect(fitz.Rect(15, 125, 100, 135), color=None, fill=(0, 0, 1))
        page.insert_text((5, 165), "Foreground", color=(1, 1, 1), fill_opacity=.5)
        doc.save(source)
    _save(source, output, mode=mode)
    with fitz.open(source) as before, fitz.open(output) as after:
        pixels = _pixels(after[0])
        assert tuple(pixels[70, 30]) == (0, 0, 0)  # image alpha composited onto white, then BW
        assert tuple(pixels[128, 60]) == (0, 0, 255)  # native vector overlays second image
        assert tuple(pixels[10, 10]) == (255, 255, 255)  # canvas backdrop is white
        assert not np.array_equal(_pixels(before[0]), pixels)  # explicit §171 policy, not original interleaving
        assert before[0].get_text("words") == after[0].get_text("words")
        for original, saved in zip(before[0].get_texttrace(), after[0].get_texttrace()):
            for key in ("font", "size", "color", "opacity", "chars", "type"):
                assert original[key] == saved[key], key
        entries = after[0].get_images(full=True)
        assert len(entries) == 1 and entries[0][1] == 0
        assert len(after[0].get_drawings()) == len(before[0].get_drawings())


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_cropbox_rotation_reused_forms_keep_native_geometry(tmp_path, rotation):
    source, output = tmp_path / "forms.pdf", tmp_path / "bw.pdf"
    pixels = np.full((48, 48, 3), 255, dtype=np.uint8)
    pixels[8:40, 8:40] = 0
    with fitz.open() as stamp, fitz.open() as doc:
        stamp.new_page(width=48, height=48).insert_image(
            fitz.Rect(0, 0, 48, 48), stream=_png(pixels))
        page = doc.new_page(width=200, height=220)
        page.set_cropbox(fitz.Rect(20, 20, 180, 200))
        page.show_pdf_page(fitz.Rect(10, 40, 58, 88), stamp)
        page.show_pdf_page(fitz.Rect(40, 40, 88, 88), stamp)
        page.insert_text((10, 125), "Rotated native text", fontsize=10)
        page.set_rotation(rotation)
        doc.save(source)
    _save(source, output)
    with fitz.open(source) as before, fitz.open(output) as after:
        assert after[0].rotation == rotation
        assert after[0].cropbox == before[0].cropbox
        assert after[0].mediabox == before[0].mediabox
        assert before[0].get_text("words") == after[0].get_text("words")
        assert np.array_equal(_pixels(before[0]), _pixels(after[0]))
        assert len(_actual_images(after[0])) == 1


def test_rotated_image_is_composed_in_color_before_one_canvas_resize(tmp_path, monkeypatch):
    source, output = tmp_path / "rotated.pdf", tmp_path / "bw.pdf"
    rgb = np.zeros((8, 8, 3), dtype=np.uint8)
    rgb[::2, :] = (210, 80, 30)
    with fitz.open() as stamp, fitz.open() as doc:
        stamp.new_page(width=40, height=60).insert_image(
            fitz.Rect(0, 0, 40, 60), stream=_png(rgb), keep_proportion=False)
        doc.new_page(width=144, height=180).show_pdf_page(
            fitz.Rect(10, 30, 90, 110), stamp, rotate=45)
        doc.save(source)
    calls = []
    resample = pipeline.force_to_dpi

    def record(image, width, height):
        calls.append((image.mode, image.size, width, height))
        return resample(image, width, height)

    monkeypatch.setattr(pipeline, "force_to_dpi", record)
    _save(source, output, dpi=144)
    # §182 supersedes the per-image resize: compose the page at native source
    # density (72dpi floor here), then resize the full-color canvas ONCE.
    assert calls == [("RGBX", (144, 180), 288, 360)]


def test_text_clipping_has_no_hidden_fallback_or_invented_glyph_masks(tmp_path, caplog):
    source, output = tmp_path / "text-clip.pdf", tmp_path / "bw.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=144, height=144)
        page.insert_font(fontname="helv")
        page.insert_image(page.rect, stream=_png(np.zeros((144, 144, 3), dtype=np.uint8)))
        image_ops = page.read_contents()
        stream = doc.get_new_xref()
        doc.update_object(stream, "<<>>")
        doc.update_stream(stream, b"q BT /helv 45 Tf 7 Tr 1 0 0 1 8 70 Tm (Clip) Tj ET\n" +
                          image_ops + b"\nQ")
        page.set_contents(stream)
        doc.save(source)
    with caplog.at_level("INFO", logger="pdf_minimalist"):
        _save(source, output)
    assert "one BW image canvas" in caplog.text
    with fitz.open(source) as before, fitz.open(output) as after:
        assert "Clip" in after[0].get_text()
        assert len(after[0].get_images(full=True)) == 1
        assert not after[0].get_images(full=True)[0][1]
    forced = tmp_path / "ffpr.pdf"
    pipeline.process_file(str(source), str(forced), force_raster=True, dpi=72,
                          strategy="simple", t=128)
    with fitz.open(source) as before, fitz.open(forced) as after:
        pix = DisplayPage(before[0]).render()
        rgb = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        expected = pipeline._threshold(np.asarray(rgb.convert("L")), "simple", 128)
        assert np.array_equal(_pixels(after[0])[:, :, 0], expected)
    with fitz.open(output) as simple:
        # The image-layer compositor follows the exact no-AA source policy;
        # FFPR above deliberately uses the complete-page filter renderer.
        with fitz.open(source) as original:
            pix = DisplayPage(original[0]).render()
            rgb = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            canvas_expected = pipeline._threshold(np.asarray(rgb.convert("L")), "simple", 128)
        assert np.array_equal(_pixels(simple[0])[:, :, 0], canvas_expected)


def test_non_normal_blend_uses_same_simple_canvas_not_per_image_fallback(tmp_path, caplog):
    source, output = tmp_path / "multiply.pdf", tmp_path / "bw.pdf"
    pixels = np.full((64, 64, 3), 255, dtype=np.uint8)
    pixels[::2] = 0
    with fitz.open() as doc:
        page = doc.new_page(width=144, height=144)
        page.draw_rect(page.rect, color=None, fill=(0, .8, .2))
        page.insert_image(fitz.Rect(20, 40, 84, 104), stream=_png(pixels))
        image_stream = page.get_contents()[-1]
        original_image = doc.xref_stream(image_stream)
        resource = int(doc.xref_get_key(page.xref, "Resources")[1].split()[0])
        doc.xref_set_key(resource, "ExtGState", "<< /Blend << /BM /Multiply >> >>")
        doc.update_stream(image_stream, b"q /Blend gs\n" + original_image + b"Q")
        page.insert_text((5, 125), "Native blend")
        doc.save(source)
    with caplog.at_level("INFO", logger="pdf_minimalist"):
        _save(source, output)
    assert "one BW image canvas" in caplog.text
    with fitz.open(source) as before, fitz.open(output) as after:
        assert before[0].get_text("words") == after[0].get_text("words")
        entries = after[0].get_images(full=True)
        assert len(entries) == 1 and entries[0][1] == 0
        assert after.xref_get_key(entries[0][0], "BitsPerComponent")[1] == "1"


def test_real_images_pdf_one_composite_native_text_and_vectors(tmp_path):
    source = Path("examples/images.pdf")
    output = tmp_path / "real-bw.pdf"
    _save(source, output, dpi=150)
    with fitz.open(source) as before, fitz.open(output) as after:
        assert before[0].get_text("words") == after[0].get_text("words")
        assert len(after[0].get_drawings()) == len(before[0].get_drawings())
        assert len(_actual_images(after[0])) == 1
        entries = after[0].get_images(full=True)
        assert len(entries) == 1 and entries[0][1] == 0
        assert after.xref_get_key(entries[0][0], "BitsPerComponent")[1] == "1"
        assert output.stat().st_size < 12_000  # original mask waste alone was 28,893 B
        clip = fitz.Rect(60, 60, 325, 112)
        orig = before[0].get_pixmap(dpi=600, clip=clip, colorspace=fitz.csRGB)
        saved = after[0].get_pixmap(dpi=600, clip=clip, colorspace=fitz.csRGB)
        # Extra native Form grouping can round antialias color by one level.
        # Font/positions remain native; this is not a rasterized-text tolerance.
        delta = np.abs(np.frombuffer(orig.samples, dtype=np.uint8).astype(np.int16) -
                       np.frombuffer(saved.samples, dtype=np.uint8).astype(np.int16))
        assert delta.max() <= 1


def test_font_subsetting_keeps_original_native_pixels(tmp_path):
    font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    if not font.exists():
        pytest.skip("system test font missing")
    source, output = tmp_path / "font.pdf", tmp_path / "bw.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=300, height=150)
        page.insert_font(fontname="original", fontfile=str(font))
        page.insert_text((20, 70), "Original glyphs", fontname="original", fontsize=30)
        page.draw_rect(fitz.Rect(10, 90, 220, 100), color=(1, 0, 0))
        doc.save(source)
    _save(source, output)
    assert output.stat().st_size < source.stat().st_size / 10
    with fitz.open(source) as before, fitz.open(output) as after:
        assert before[0].get_text("words") == after[0].get_text("words")
        assert np.array_equal(_pixels(before[0], 300), _pixels(after[0], 300))
        assert not after[0].get_images()


def test_inline_bitmap_is_composited_with_native_text(tmp_path):
    source, output = tmp_path / "inline.pdf", tmp_path / "bw.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=144, height=144)
        stream = doc.get_new_xref()
        doc.update_object(stream, "<<>>")
        data = b"\x00" * 3 + b"\xff" * 3 + b"\xff" * 3 + b"\x00" * 3
        doc.update_stream(stream, b"q 32 0 0 32 10 100 cm BI /W 2 /H 2 /CS /RGB /BPC 8 ID " +
                          data + b"\nEI Q\n")
        page.set_contents(stream)
        page.insert_text((10, 120), "Inline native caption")
        doc.save(source)
    _save(source, output)
    with fitz.open(source) as before, fitz.open(output) as after:
        assert not before[0].get_images() and before[0].get_image_info()
        assert len(after[0].get_images()) == 1
        assert before[0].get_text("words") == after[0].get_text("words")
        assert _pixels(after[0]).min() == 0


def test_native_stencil_is_composed_before_full_color_canvas_resize(tmp_path, monkeypatch):
    source, output = tmp_path / "stencil.pdf", tmp_path / "bw.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=100, height=100)
        xref = doc.get_new_xref()
        doc.update_object(xref, "<< /Type /XObject /Subtype /Image /Width 8 /Height 8 "
                          "/ImageMask true /BitsPerComponent 1 >>")
        doc.update_stream(xref, b"\x0f" * 8, compress=False)
        page.insert_image(fitz.Rect(10, 10, 74, 74), xref=xref)
        doc.save(source)
    resample, calls = pipeline.force_to_dpi, []

    def record(image, width, height):
        calls.append((image.mode, image.size, width, height))
        return resample(image, width, height)

    monkeypatch.setattr(pipeline, "force_to_dpi", record)
    _save(source, output, dpi=144)
    assert calls == [("RGBX", (100, 100), 200, 200)]
    with fitz.open(output) as after:
        entries = after[0].get_images()
        assert len(entries) == 1 and entries[0][1] == 0
        assert after.xref_get_key(entries[0][0], "BitsPerComponent")[1] == "1"
        assert _pixels(after[0], 144).min() == 0
