"""§§177–182: compose full color, target DPI, filter once; no alpha halos."""

import io
import math

import numpy as np
import pymupdf as fitz
from PIL import Image
import pytest

from pdf_minify.core import pipeline
from pdf_minify.core import canvas
from pdf_minify.core.cancel import CancelToken
from pdf_minify.core.canvas import flatten_rgb
from pdf_minify.core.display import DisplayPage
from pdf_minify.core.pdf_io import CancelledError


def png(array):
    out = io.BytesIO()
    Image.fromarray(array).save(out, "PNG")
    return out.getvalue()


def source_pdf(path, background=(1, 1, 1), *, rotation=0, overlap=False):
    y, x = np.indices((600, 600))
    opacity = np.clip((245.3 - np.hypot(x - 299.1, y - 301.7)) * 255, 0, 255).astype(np.uint8)
    rgba = np.zeros((600, 600, 4), dtype=np.uint8)
    rgba[opacity > 0, :3] = (240, 190, 20)
    rgba[:, :, 3] = opacity
    with fitz.open() as doc:
        page = doc.new_page(width=144, height=180)
        page.draw_rect(page.rect, color=None, fill=background)
        page.insert_image(fitz.Rect(12, 12, 132, 132), stream=png(rgba))
        if overlap:
            top = np.full((240, 240, 4), (30, 180, 230, 127), dtype=np.uint8)
            page.insert_image(fitz.Rect(70, 70, 118, 118), stream=png(top))
        page.insert_text((8, 155), "Native caption", fontsize=10, color=(0, 0, 1))
        page.draw_rect(fitz.Rect(10, 163, 100, 173), color=(1, 0, 0), width=0.5)
        page.insert_link({"kind": fitz.LINK_URI,
                          "from": fitz.Rect(8, 140, 100, 157), "uri": "https://example.com/"})
        page.add_text_annot((130, 155), "Keep annotation")
        page.set_rotation(rotation)
        doc.save(path)


def image_rgb(doc, entry):
    pix = fitz.Pixmap(doc, entry[0])
    if pix.colorspace != fitz.csRGB:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]


@pytest.mark.parametrize("mode,options", [
    ("color", dict(jpeg_q=45)), ("jpx", dict(lossless=True)), ("indexed", dict(colors=16))])
def test_hidden_black_never_becomes_a_color_border(tmp_path, monkeypatch, mode, options):
    source, output = tmp_path / "alpha.pdf", tmp_path / "filtered.pdf"
    source_pdf(source)
    inputs = []
    encode = pipeline.color_canvas_payload
    def observe(image, *args, **kwargs):
        inputs.append(image.copy())
        pixels = np.asarray(image)
        assert pixels[:, :, 0].min() >= 238
        assert pixels[:, :, 1].min() >= 180
        return encode(image, *args, **kwargs)
    monkeypatch.setattr(pipeline, "color_canvas_payload", observe)
    pipeline.save_with_spec(str(source), str(output), dict(mode=mode, dpi_cap=150, **options))
    with fitz.open(source) as before, fitz.open(output) as after:
        images = after[0].get_images(full=True)
        assert len(images) == 1 and images[0][1] == 0
        assert images[0][2:4] == (300, 375)
        pixels = image_rgb(after, images[0])
        # The source is bright yellow on white. Hidden black may NOT enter
        # the flattened image. Allow normal codec/Lanczos error, not a halo.
        if mode != "color":
            assert pixels[:, :, 0].min() > 200
            assert pixels[:, :, 1].min() > 140
        else:
            # Lossy JPEG may ring at a high-contrast boundary. Pin the exact
            # independent JPEG result, not an invented "lossless JPEG" limit.
            expected = io.BytesIO()
            inputs[0].save(expected, "JPEG", quality=45, optimize=True)
            assert after.xref_stream_raw(images[0][0]) == expected.getvalue()
        assert before[0].get_text("words") == after[0].get_text("words")
        assert len(before[0].get_drawings()) == len(after[0].get_drawings())
        assert after[0].get_links()[0]["uri"] == "https://example.com/"
        assert next(after[0].annots()).info["content"] == "Keep annotation"
        if mode == "indexed":
            assert len(np.unique(pixels.reshape(-1, 3), axis=0)) <= 16


@pytest.mark.parametrize("dpi", [72, 144, 720])
@pytest.mark.parametrize("mode", ["jpx", "bw"])
def test_native_composition_then_full_color_resize_then_one_transform(tmp_path, monkeypatch, dpi, mode):
    source, output = tmp_path / "alpha.pdf", tmp_path / "filtered.pdf"
    source_pdf(source, background=(1, 1, 1) if mode == "bw" else (.12, .45, .8), overlap=True)
    events = []
    resize = pipeline.force_to_dpi
    encode = pipeline.bw_page_payload if mode == "bw" else pipeline.color_canvas_payload
    encoded_gray = []
    def observe_resize(image, width, height, **kwargs):
        assert image.mode == "RGBX" and image.readonly
        assert not kwargs
        events.append("resize")
        return resize(image, width, height, **kwargs)
    def observe_encode(image, *args, **kwargs):
        if mode == "bw":
            assert image.ndim == 2
            encoded_gray.append(image.copy())
        else:
            assert image.mode == "RGB"
        events.append("encode")
        return encode(image, *args, **kwargs)
    monkeypatch.setattr(pipeline, "force_to_dpi", observe_resize)
    monkeypatch.setattr(pipeline, "bw_page_payload" if mode == "bw" else "color_canvas_payload", observe_encode)
    # Any unassociated per-image extraction would resurrect the old path.
    with monkeypatch.context() as scoped:
        scoped.setattr(fitz.Document, "extract_image", lambda *a: pytest.fail("per-image color transform"))
        pipeline.save_with_spec(str(source), str(output), dict(
            mode=mode, dpi_cap=dpi, dpi=dpi, force_raster=False,
            strategy="simple", t=128, lossless=True))
    assert events == ["resize", "encode"]
    with fitz.open(source) as before, fitz.open(output) as after:
        entries = after[0].get_images()
        assert len(entries) == 1 and entries[0][1] == 0
        assert entries[0][2:4] == (2*dpi, math.ceil(2.5*dpi))
        rgb = image_rgb(after, entries[0])
        # Native blue page backdrop was composed BEFORE opacity/resampling.
        background = (255, 255, 255) if mode == "bw" else (30, 114, 204)
        assert np.max(np.abs(rgb[0, 0].astype(int) - background)) <= 2
        # Independent full-page native rendering at known source density,
        # then one RGB resize. Text/vector paint is outside this image ROI.
        pix = DisplayPage(before[0]).render(fitz.Matrix(5, 5))
        reference = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).resize(
            (entries[0][2], entries[0][3]), Image.Resampling.LANCZOS)
        margin, end = int(8*dpi/72), int(137*dpi/72)
        if mode == "bw":
            assert np.array_equal(rgb[:, :, 0], pipeline._threshold(encoded_gray[0], "simple", 128))
            region = np.asarray(reference.convert("L"))[margin:end, margin:end].astype(int)
            actual = encoded_gray[0][margin:end, margin:end].astype(int)
        else:
            region = np.asarray(reference)[margin:end, margin:end].astype(int)
            actual = rgb[margin:end, margin:end].astype(int)
        delta = np.abs(actual - region)
        assert delta.max() <= 2


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_color_canvas_keeps_rotations_and_native_content(tmp_path, rotation):
    source, output = tmp_path / "rotated.pdf", tmp_path / "filtered.pdf"
    source_pdf(source, rotation=rotation)
    pipeline.save_with_spec(str(source), str(output), dict(mode="indexed", dpi_cap=72, colors=32))
    with fitz.open(source) as before, fitz.open(output) as after:
        assert after[0].rotation == rotation
        assert after[0].cropbox == before[0].cropbox
        assert before[0].get_text("words") == after[0].get_text("words")
        assert len(before[0].get_drawings()) == len(after[0].get_drawings())
        assert len(after[0].get_images()) == 1


def test_tiled_native_composite_has_no_seams_or_whole_source_buffer(tmp_path, monkeypatch):
    source = tmp_path / "gradient.pdf"
    y, x = np.indices((900, 800))
    rgb = np.stack((x % 256, y % 256, (x+y) % 256), axis=2).astype(np.uint8)
    with fitz.open() as doc:
        doc.new_page(width=144, height=180).insert_image(
            fitz.Rect(0, 0, 144, 180), stream=png(rgb), keep_proportion=False)
        doc.save(source)
    with fitz.open(source) as doc:
        page = doc[0]
        whole = DisplayPage(page).render(fitz.Matrix(400/72, 400/72))
        expected = Image.frombytes("RGB", (whole.width, whole.height), whole.samples).resize(
            (300, 375), Image.Resampling.LANCZOS)
        extents = []
        render = DisplayPage.render
        def observe(renderer, *args, **kwargs):
            pix = render(renderer, *args, **kwargs)
            extents.append(pix.width*pix.height)
            return pix
        monkeypatch.setattr(DisplayPage, "render", observe)
        actual = flatten_rgb(page, 150, CancelToken(), pipeline.force_to_dpi, tile_pixels=200_000)
        assert len(extents) > 1 and max(extents) <= 210_000
        assert np.abs(np.asarray(actual).astype(int) - np.asarray(expected).astype(int)).max() <= 1


@pytest.mark.parametrize("density", [299.5, 300.25, 301.75])
def test_source_density_keeps_genuine_fractional_sampling(tmp_path, density):
    source = tmp_path / "fractional-density.pdf"
    width, height = 601, 485
    samples = np.full((height, width, 3), (32, 128, 224), np.uint8)
    with fitz.open() as pdf:
        page = pdf.new_page(width=width * 72 / density, height=height * 72 / density)
        page.insert_image(page.rect, stream=png(samples), keep_proportion=False)
        pdf.save(source)
    with fitz.open(source) as pdf:
        actual = canvas._source_dpi(pdf[0])
        assert actual == pytest.approx(density, abs=0.0001)
        grid = (pdf[0].rect * fitz.Matrix(actual / 72, actual / 72)).irect
        assert (grid.width, grid.height) == (width, height)


def test_native_only_pages_do_not_gain_a_bitmap(tmp_path):
    source, output = tmp_path / "native.pdf", tmp_path / "filtered.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=144, height=180)
        page.insert_text((10, 30), "Native only")
        page.draw_rect(fitz.Rect(10, 50, 100, 120), color=(1, 0, 0))
        doc.save(source)
    pipeline.save_with_spec(str(source), str(output), dict(mode="indexed", dpi_cap=150, colors=16))
    with fitz.open(output) as doc:
        assert "Native only" in doc[0].get_text() and not doc[0].get_images()


@pytest.mark.parametrize("failure", ["render", "resize", "cancel"])
def test_composite_scratch_is_owned_and_closed_on_failure(tmp_path, monkeypatch, failure):
    source = tmp_path / "source.pdf"
    source_pdf(source)
    owned = tmp_path / "artifact-work"
    owned.mkdir()
    handles = []
    temporary = canvas.tempfile.TemporaryFile
    def observe_temp(*args, **kwargs):
        assert kwargs["dir"] == owned
        handle = temporary(*args, **kwargs)
        handles.append(handle)
        return handle
    monkeypatch.setattr(canvas.tempfile, "TemporaryFile", observe_temp)
    token = CancelToken()
    render = DisplayPage.render
    def observe_render(*args, **kwargs):
        if failure == "render":
            raise RuntimeError("injected native-render failure")
        pix = render(*args, **kwargs)
        if failure == "cancel":
            token.cancel()
        return pix
    def resample(*args):
        if failure == "cancel":
            pytest.fail("resize after cancellation")
        raise RuntimeError("injected resize failure")
    monkeypatch.setattr(DisplayPage, "render", observe_render)
    with fitz.open(source) as doc, pytest.raises(CancelledError if failure == "cancel" else RuntimeError):
        flatten_rgb(doc[0], 150, token, resample, directory=owned, tile_pixels=10_000)
    assert len(handles) == 1 and handles[0].closed
    assert not list(owned.iterdir())


@pytest.mark.parametrize("mode", ["jpx", "bw"])
def test_original_image_path_clips_survive_native_layer_selection(tmp_path, mode):
    source, output = tmp_path / "clipped.pdf", tmp_path / "filtered.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=144, height=144)
        page.insert_image(fitz.Rect(32, 32, 96, 96),
                          stream=png(np.full((64, 64, 3), (240, 20, 20), dtype=np.uint8)))
        stream = page.get_contents()[-1]
        doc.update_stream(stream, b"q 48 64 32 32 re W n\n" + doc.xref_stream(stream) + b"\nQ")
        page.insert_text((10, 130), "Native caption", color=(0, 0, 1))
        doc.save(source)
    pipeline.save_with_spec(str(source), str(output), dict(
        mode=mode, dpi=72, dpi_cap=72, force_raster=False,
        strategy="simple", t=128, lossless=True))
    with fitz.open(source) as before, fitz.open(output) as after:
        original = DisplayPage(before[0]).render()
        pixels = Image.frombytes("RGB", (144, 144), original.samples)
        expected = np.asarray(pixels)[:120]
        if mode == "bw":
            expected = pipeline._threshold(np.asarray(pixels.convert("L")), "simple", 128)[:120]
        saved = DisplayPage(after[0]).render()
        rgb = np.frombuffer(saved.samples, dtype=np.uint8).reshape(144, 144, 3)
        assert np.array_equal(rgb[:120, :, 0] if mode == "bw" else rgb[:120], expected)
        assert before[0].get_text("words") == after[0].get_text("words")
