"""§§172–175: actual device pixels, no invented gray, native geometry on zoom."""

import io
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pymupdf as fitz
import pytest
from PIL import Image
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QWidget

from pdf_minimalist.core.display import DisplayPage, render_display_page
from pdf_minimalist.ui_qt.artifacts import build_artifact
from pdf_minimalist.ui_qt.jobs import frame_view
from pdf_minimalist.ui_qt.viewer import ContinuousDocView, _PdfSource

_app = QApplication.instance() or QApplication([])


def rgb(pix):
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)


def qimage(array):
    h, w = array.shape[:2]
    return QImage(array.data, w, h, w * 3, QImage.Format_RGB888).copy()


def pixels(image):
    image = image.convertToFormat(QImage.Format_RGBA8888)
    return np.frombuffer(image.constBits(), dtype=np.uint8).reshape(
        image.height(), image.bytesPerLine() // 4, 4)[:, :image.width(), :3].copy()


@pytest.fixture
def files(tmp_path):
    source = tmp_path / "native.pdf"
    pattern = np.full((300, 600), 255, dtype=np.uint8)
    pattern[10:60, 10:590:3] = 0
    pattern[90:280:4, 10:590] = 0
    stream = io.BytesIO()
    Image.fromarray(pattern).convert("1").save(stream, format="PNG")
    with fitz.open() as doc:
        page = doc.new_page(width=144, height=144)
        page.insert_image(fitz.Rect(0, 0, 144, 72), stream=stream.getvalue())
        page.insert_text((8, 90), "Native precision: Ag 123", fontsize=8)
        page.draw_line((5.37, 110.63), (137.17, 137.39), color=(0, 0, 0), width=0.37)
        doc.save(source)
    root = tmp_path / "flat"
    root.mkdir()
    artifact = build_artifact(str(source), dict(mode="bw", dpi=300,
                             strategy="otsu", t=180, force_raster=True), str(root))
    yield source, artifact
    artifact.close_pages()


@pytest.mark.parametrize("dpi", [30, 75, 150, 175, 300, 600])
def test_real_ffpr_readback_never_averages_bitmap_samples(files, dpi):
    _, artifact = files
    with fitz.open(artifact.pdf_path) as doc:
        assert not doc[0].get_text()
        assert doc[0].get_images()[0][4] == 1
        if dpi == 75:
            assert len(np.unique(rgb(doc[0].get_pixmap(dpi=dpi)))) > 2
        display = rgb(render_display_page(doc[0], dpi=dpi))
        assert set(np.unique(display)) == {0, 255}
    assert set(np.unique(artifact.pages[0])) == {0, 255}
    assert set(np.unique(artifact.mini_pages[0])) == {0, 255}
    mini = frame_view(artifact.mini_pages, 300, 300, 24, 1,
                      (17, 33, 250, 240), out_w=127)
    assert set(np.unique(mini)) <= {0, 255}


@pytest.mark.parametrize("zoom", [0.1, 0.35, 1.0, 1.37, 3.5])
def test_actual_ffpr_viewport_pixels_are_binary_at_every_zoom(files, zoom):
    _, artifact = files
    view = ContinuousDocView()
    try:
        view.resize(440, 440)
        view.setBackgroundBrush(QColor(105, 105, 105))
        view.set_pages([qimage(artifact.pages[0])], pdf_path=artifact.pdf_path)
        view.show()
        _app.processEvents()
        view.set_zoom(zoom)
        _app.processEvents()
        image = view.viewport().grab().toImage()
        ratio = image.devicePixelRatio()
        page = view.mapFromScene(view._items[0].sceneBoundingRect()).boundingRect()
        visible = page.intersected(view.viewport().rect()).adjusted(2, 2, -2, -2)
        crop = pixels(image)[int(visible.top() * ratio):int((visible.bottom()+1) * ratio),
                             int(visible.left() * ratio):int((visible.right()+1) * ratio)]
        assert crop.size
        assert set(np.unique(crop)) == {0, 255}
        assert not view.renderHints() & QPainter.SmoothPixmapTransform
    finally:
        view.clear_pdf_source()
        view.close()


def test_native_zoom_refines_shapes_instead_of_stretching_prepared_raster(files):
    source, _ = files
    with fitz.open(source) as doc:
        base = rgb(render_display_page(doc[0], dpi=150)).copy()
    view = ContinuousDocView()
    try:
        view.resize(800, 800)
        view.set_pages([qimage(base)], pdf_path=source)
        view.show()
        _app.processEvents()
        view.set_zoom(2)
        _app.processEvents()
        shot = view.viewport().grab().toImage()
        ratio = shot.devicePixelRatio()
        origin = view.mapFromScene(view._items[0].pos())
        rendered = pixels(shot)[int(origin.y()*ratio):int((origin.y()+600)*ratio),
                                int(origin.x()*ratio):int((origin.x()+600)*ratio)]
        with fitz.open(source) as doc:
            native = rgb(render_display_page(doc[0], dpi=300*ratio))
        assert np.array_equal(rendered, native)
        enlarged = np.repeat(np.repeat(base, int(2*ratio), axis=0), int(2*ratio), axis=1)
        assert not np.array_equal(rendered[rendered.shape[0]//2:],
                                  enlarged[enlarged.shape[0]//2:])
    finally:
        view.clear_pdf_source()
        view.close()


def test_encoded_gray_color_opacity_are_not_thresholded(tmp_path):
    source = tmp_path / "gray-alpha.pdf"
    array = np.full((30, 30, 3), (91, 117, 143), dtype=np.uint8)
    stream = io.BytesIO()
    Image.fromarray(array).save(stream, format="PNG")
    with fitz.open() as doc:
        page = doc.new_page(width=100, height=100)
        page.insert_image(fitz.Rect(0, 0, 50, 100), stream=stream.getvalue(), keep_proportion=False)
        page.draw_rect(fitz.Rect(50, 0, 100, 100), color=None, fill=(0, 0, 0), fill_opacity=0.5)
        doc.save(source)
    with fitz.open(source) as doc:
        result = rgb(render_display_page(doc[0], dpi=144))
        assert tuple(result[50, 25]) == (91, 117, 143)
        assert 120 <= int(result[50, 150, 0]) <= 130
        assert np.all(result[50, 150] == result[50, 150, 0])


def test_native_paint_matches_viewport_during_parent_window_capture(files):
    _, artifact = files
    root = QWidget()
    root.resize(850, 800)
    view = ContinuousDocView(root)
    view.setGeometry(37, 61, 760, 700)
    try:
        view.set_pages([qimage(artifact.pages[0])], pdf_path=artifact.pdf_path)
        root.show()
        _app.processEvents()
        for zoom in (0.1, 0.75, 2, 4):
            view.set_zoom(zoom)
            _app.processEvents()
            whole = root.grab().toImage()
            individual = view.viewport().grab().toImage()
            origin = view.viewport().mapTo(root, QPoint(0, 0))
            ratio = whole.devicePixelRatio()
            x, y = int(origin.x()*ratio), int(origin.y()*ratio)
            crop = pixels(whole)[y:y+individual.height(), x:x+individual.width()]
            assert np.array_equal(crop, pixels(individual))
    finally:
        view.clear_pdf_source()
        root.close()


def test_display_restores_filter_render_settings_even_after_error(files, monkeypatch):
    _, artifact = files
    m = fitz.mupdf
    previous = fitz.TOOLS.show_aa_level()
    try:
        m.fz_set_graphics_aa_level(4)
        m.fz_set_text_aa_level(2)
        with fitz.open(artifact.pdf_path) as doc:
            original = doc[0].get_pixmap(dpi=75).samples
            renderer = DisplayPage(doc[0])
            renderer.render(fitz.Matrix(1, 1))
            assert fitz.TOOLS.show_aa_level()["graphics"] == 4
            assert fitz.TOOLS.show_aa_level()["text"] == 2
            assert doc[0].get_pixmap(dpi=75).samples == original
            def fail(*args):
                raise ValueError("simulated display failure")
            monkeypatch.setattr(m, "fz_run_display_list", fail)
            with pytest.raises(ValueError, match="simulated"):
                renderer.render()
            assert fitz.TOOLS.show_aa_level()["graphics"] == 4
            assert fitz.TOOLS.show_aa_level()["text"] == 2
    finally:
        m.fz_set_graphics_aa_level(previous["graphics"])
        m.fz_set_text_aa_level(previous["text"])


def test_native_display_cache_is_bounded_and_source_is_released(tmp_path):
    path = tmp_path / "many.pdf"
    with fitz.open() as doc:
        for i in range(12):
            doc.new_page(width=100, height=100).insert_text((10, 50), str(i))
        doc.save(path)
    source = _PdfSource(path)
    for i in range(12):
        tile = source.tile(i, fitz.Matrix(10, 10), fitz.Rect(0, 0, 100, 100))
        assert tile[2].width() == 1000
        assert len(source._tiles) <= source.MAX_TILES
        assert source._tile_bytes <= source.MAX_TILE_BYTES
        assert len(source._pages) <= source.MAX_PAGES
        assert source.tile(i, fitz.Matrix(10, 10), fitz.Rect(0, 0, 100, 100)) is tile
    source.close()
    assert source.doc is None and not source._pages and not source._tiles
