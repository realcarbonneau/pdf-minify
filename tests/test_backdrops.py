"""B116: page/panel background ownership follows source paint occurrences."""

import io

import numpy as np
import pymupdf as fitz
from PIL import Image
import pytest

from pdf_minify.core import pipeline
from pdf_minify.core.backdrops import BackdropPlan
from pdf_minify.core.cancel import CancelToken
from pdf_minify.core.canvas import flatten_rgb
from pdf_minify.core.display import DisplayPage
from tools.bench_image_streams import assert_native_text


PANEL = fitz.Rect(12, 12, 108, 108)
PHOTO = fitz.Rect(28, 28, 92, 92)


def bitmap():
    y, x = np.indices((64, 64))
    rgb = np.repeat((((x // 8 + y // 8) % 2) * 255).astype(np.uint8)[:, :, None], 3, axis=2)
    stream = io.BytesIO()
    Image.fromarray(rgb).save(stream, "PNG")
    return stream.getvalue()


def pixels(page):
    pix = DisplayPage(page).render()
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)


def save(source, target, mode="jpx"):
    pipeline.save_with_spec(str(source), str(target), dict(
        mode=mode, dpi=72, dpi_cap=72, jpeg_q=75, jpx_q=75, lossless=True,
        colors=5, strategy="simple", t=128, force_raster=False))


@pytest.mark.parametrize("mode", ["bw", "bw-flate", "indexed", "layered-jbig2", "color", "jpx"])
def test_local_panel_cannot_hide_its_photo_in_any_image_codec(tmp_path, mode):
    source, target = tmp_path / "source.pdf", tmp_path / "saved.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=144, height=160)
        page.draw_rect(PANEL, color=None, fill=(.8, .4, .6))
        page.insert_image(PHOTO, stream=bitmap())
        page.draw_rect(fitz.Rect(70, 70, 82, 82), color=None, fill=(0, 0, 1))
        page.insert_text((12, 135), "Native caption", color=(0, 0, 1))
        assert [fill.background for fill in BackdropPlan.from_page(page).fills] == [True, False]
        doc.save(source)
    save(source, target, mode)
    with fitz.open(source) as before, fitz.open(target) as after:
        actual = pixels(after[0])
        assert actual[36:60, 36:60].std() > 100  # actual checkerboard, not a flat panel
        assert tuple(actual[75, 75]) == (0, 0, 255)  # vector foreground stays native
        assert_native_text(before[0], after[0])


@pytest.mark.parametrize("opacity", [.25, 1])
def test_equal_rectangles_have_distinct_background_and_foreground_ownership(tmp_path, opacity):
    source, target = tmp_path / "source.pdf", tmp_path / "saved.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=144, height=160)
        page.draw_rect(PANEL, color=None, fill=(.8, .4, .6))
        page.insert_image(PHOTO, stream=bitmap())
        page.draw_rect(PANEL, color=None, fill=(0, 0, 1), fill_opacity=opacity)
        assert [fill.background for fill in BackdropPlan.from_page(page).fills] == [True, False]
        doc.save(source)
    save(source, target)
    with fitz.open(source) as before, fitz.open(target) as after:
        assert np.array_equal(pixels(before[0]), pixels(after[0]))


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_compound_background_keeps_its_translucent_stroke_once(tmp_path, rotation):
    source, target = tmp_path / "source.pdf", tmp_path / "saved.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=144, height=160)
        page.draw_rect(PANEL, color=(0, 0, 0), fill=(.8, .4, .6),
                       width=2, stroke_opacity=.5)
        page.insert_image(PHOTO, stream=bitmap())
        page.insert_text((12, 135), "Native caption")
        page.set_rotation(rotation)
        doc.save(source)
    save(source, target)
    with fitz.open(source) as before, fitz.open(target) as after, fitz.open() as reference:
        # §171 separates backdrop fill from native stroke. PDF's atomic B
        # knockout can differ at their overlap; assert the explicit policy,
        # including ONE translucent stroke, rather than demanding FFPR.
        page = reference.new_page(width=144, height=160)
        page.draw_rect(PANEL, color=None, fill=(.8, .4, .6))
        page.insert_image(PHOTO, stream=bitmap())
        page.draw_rect(PANEL, color=(0, 0, 0), width=2, stroke_opacity=.5)
        page.insert_text((12, 135), "Native caption")
        page.set_rotation(rotation)
        assert np.array_equal(pixels(reference[0]), pixels(after[0]))
        assert_native_text(before[0], after[0])
        strokes = [d for d in after[0].get_drawings() if d["color"] is not None]
        assert len(strokes) == 1 and strokes[0]["stroke_opacity"] == .5


def test_reused_nested_form_can_be_background_then_foreground_at_the_same_position(tmp_path):
    source, target = tmp_path / "source.pdf", tmp_path / "saved.pdf"
    with fitz.open() as stamp, fitz.open() as doc:
        stamp.new_page(width=96, height=96).draw_rect(
            fitz.Rect(0, 0, 96, 96), color=(0, 0, 0), fill=(.8, .4, .6), width=2)
        page = doc.new_page(width=144, height=160)
        page.show_pdf_page(PANEL, stamp)
        page.insert_image(PHOTO, stream=bitmap())
        page.show_pdf_page(PANEL, stamp)
        assert [fill.background for fill in BackdropPlan.from_page(page).fills] == [True, False]
        doc.save(source)
    save(source, target)
    with fitz.open(source) as before, fitz.open(target) as after:
        assert np.array_equal(pixels(before[0]), pixels(after[0]))


def test_repository_brochure_keeps_emblem_and_both_panel_photos(tmp_path):
    source, target = tmp_path / "brochure-page1.pdf", tmp_path / "saved.pdf"
    with fitz.open("examples/news-crater-lake-2026.pdf") as brochure, fitz.open() as doc:
        doc.insert_pdf(brochure, from_page=0, to_page=0)
        doc.save(source)
    save(source, target)
    with fitz.open(source) as before, fitz.open(target) as after:
        # Compare the same one-time source-density-to-target-DPI operation,
        # not 72-DPI nearest-neighbour display against a resampled canvas.
        a = np.asarray(flatten_rgb(before[0], 72, CancelToken(), pipeline.force_to_dpi))
        b = pixels(after[0])
        for x0, y0, x1, y1 in ((772, 42, 794, 74), (55, 800, 180, 865),
                               (660, 995, 795, 1120)):
            # Text/diagrams are outside these image interiors. Allow only
            # tiny native blend rounding, not a flat background replacement.
            expected, actual = a[y0:y1, x0:x1], b[y0:y1, x0:x1]
            assert actual.std() > 15
            assert np.abs(actual.astype(int) - expected.astype(int)).mean() < 1
        assert_native_text(before[0], after[0])


@pytest.mark.parametrize("mode", ["jpx", "bw-flate"])
def test_inline_image_samples_survive_the_scratch_backdrop_pass(tmp_path, mode):
    source, target = tmp_path / "source.pdf", tmp_path / "saved.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=144, height=160)
        page.draw_rect(PANEL, color=None, fill=(.8, .4, .6))
        samples = bytes([0, 0, 0, 255, 255, 255]) * 3
        xref = doc.get_new_xref()
        doc.update_object(xref, "<<>>")
        doc.update_stream(xref, page.read_contents() +
                          b"q 60 0 0 10 28 100 cm BI /W 6 /H 1 /BPC 8 /CS /RGB ID " +
                          samples + b" EI Q\n")
        page.set_contents(xref)
        doc.save(source)
    save(source, target, mode)
    with fitz.open(target) as after:
        actual = pixels(after[0])
        assert tuple(actual[55, 35]) == (0, 0, 0)
        assert tuple(actual[55, 45]) == (255, 255, 255)


def test_negative_rectangle_extents_match_the_same_background_paint(tmp_path):
    source, target = tmp_path / "source.pdf", tmp_path / "saved.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=144, height=160)
        xref = doc.get_new_xref()
        doc.update_object(xref, "<<>>")
        doc.update_stream(xref, b"q .8 .4 .6 rg 108 148 -96 -96 re f Q\n")
        page.set_contents(xref)
        page.insert_image(PHOTO, stream=bitmap())
        doc.save(source)
    save(source, target)
    with fitz.open(source) as before, fitz.open(target) as after:
        assert np.array_equal(pixels(before[0]), pixels(after[0]))
