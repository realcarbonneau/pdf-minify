import os
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QImage  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402
from PySide6.QtCore import Qt  # noqa: E402

from pdf_minify.ui_qt.viewer import ContinuousDocView  # noqa: E402
from pdf_minify.ui_qt.overview import OverviewMap  # noqa: E402

_app = QApplication.instance() or QApplication([])


def _shown(*views):
    for v in views:
        v.show()
    _app.processEvents()


def _pages(n=5, w=400, h=500):
    out = []
    for i in range(n):
        img = QImage(w, h, QImage.Format_Grayscale8)
        img.fill(100 + i * 10)
        out.append(img)
    return out


def test_autowrap_cols():
    a, b = ContinuousDocView(), ContinuousDocView()
    a.link(b)
    b.link(a)
    a.resize(900, 600)
    a.set_pages(_pages())
    _shown(a)
    assert a.page_count == 5
    assert a.cols() == 1  # fit-width default => single column
    a.set_zoom(0.4)  # zoom out => autowrap grid
    assert a.cols() >= 2
    a.set_zoom(4.0)  # zoom in => single column
    assert a.cols() == 1


def test_continuous_zoom_scroll_synced():
    a, b = ContinuousDocView(), ContinuousDocView()
    a.resize(400, 600)
    b.resize(400, 600)
    a.link(b)
    b.link(a)
    a.set_pages(_pages())
    b.set_pages(_pages())
    _shown(a, b)
    a.set_zoom(2.0)
    assert b._zoom == a._zoom
    a.goto_page(4)
    assert a.current_page == 4
    assert b.verticalScrollBar().value() == a.verticalScrollBar().value()
    a.goto_page(99)
    assert a.current_page == 4  # clamped


def test_goto_page_steps_through_grid():
    a = ContinuousDocView()
    a.resize(900, 600)
    a.set_pages(_pages(n=9))
    _shown(a)
    a.set_zoom(0.4)  # autowrap grid, several columns
    assert a.cols() >= 2
    seen = []
    a.pageChanged = seen.append
    for i in range(9):
        a.goto_page(i)
        assert a.current_page == i, i
    assert seen == list(range(1, 9)) or seen[-1] == 8
    a.goto_page(99)
    assert a.current_page == 8  # clamped, same as scroll path


def test_overview_mirrors_view():
    from PySide6.QtCore import QPointF, QRectF
    nav = OverviewMap()
    nav.resize(200, 200)
    nav.show()
    _app.processEvents()
    img = _pages(n=1)[0]
    nav.set_page(img)
    nav.set_view(QRectF(50, 60, 100, 120), QPointF(0, 0))
    assert not nav._rect.isNull()
    hits = []
    nav.navigate = lambda pt: hits.append((pt.x(), pt.y()))
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtCore import QEvent, QPointF as PF
    ev = QMouseEvent(QEvent.Type.MouseButtonPress, PF(100, 100), PF(100, 100),
                     Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
                     Qt.KeyboardModifier.NoModifier)
    nav.mousePressEvent(ev)
    assert len(hits) == 1
    assert not nav.grab().isNull()


@pytest.mark.parametrize("count", (1, 2, 5, 9))
@pytest.mark.parametrize("zoom", (0.05, 0.25))
def test_zoom_out_centers_only_the_pages_that_exist(count, zoom):
    """§164: a fitting page group centers, never a scene of phantom columns."""
    a = ContinuousDocView()
    a.resize(700, 600)
    a.set_pages(_pages(n=count))
    _shown(a)
    try:
        a.set_zoom(zoom)
        _app.processEvents()
        bounds = a.scene().itemsBoundingRect()
        assert a.sceneRect() == bounds, (count, zoom, a.cols(), a.sceneRect(), bounds)
        assert a.cols() <= count
        assert a._gcols() == a.cols()
        center = a.mapFromScene(bounds.center())
        viewport_center = a.viewport().rect().center()
        assert abs(center.x() - viewport_center.x()) <= 2, (count, zoom, center, viewport_center)
        if bounds.height() * zoom <= a.viewport().height():
            assert abs(center.y() - viewport_center.y()) <= 2, (count, zoom, center, viewport_center)
    finally:
        a.close()


@pytest.mark.parametrize("count", (1, 2, 7))
def test_peer_zoom_and_resize_keep_one_occupied_grid(count):
    """§165: either pane's zoom updates positions/bounds, not only its camera."""
    a, b = ContinuousDocView(), ContinuousDocView()
    a.resize(700, 600)
    b.resize(699, 600)
    b.layout_from = a
    a.link(b)
    b.link(a)
    a.set_pages(_pages(n=count))
    b.set_pages(_pages(n=count))
    _shown(a, b)
    try:
        for view, zoom, width in ((a, 0.05, 700), (b, 0.25, 450),
                                  (a, 1.5, 900), (b, 0.4, 500), (a, 0.1, 800)):
            a.resize(width, 600)
            b.resize(width - 1, 600)
            _app.processEvents()
            view.set_zoom(zoom)
            for _ in range(3):
                _app.processEvents()
            assert a._zoom == b._zoom == zoom
            assert a.cols() == b.cols() == a._gcols() == b._gcols()
            assert a.sceneRect() == b.sceneRect()
            assert [a.page_pos(i) for i in range(count)] == [b.page_pos(i) for i in range(count)]
            for pane in (a, b):
                for i in range(count):
                    row, column = divmod(i, pane.cols())
                    assert pane.page_pos(i).x() == column * (400 + pane.GAP)
                    assert pane.page_pos(i).y() == row * (500 + pane.GAP)
                bounds = pane.scene().itemsBoundingRect()
                # Qt AlignCenter uses maximumViewportSize on a fitting axis;
                # a scrollbar on the other axis does not move that center.
                # Keep the native behavior, rather than a per-bar pixel offset.
                native_center = pane.maximumViewportSize().toSizeF() / 2
                if bounds.width() * zoom <= pane.viewport().width():
                    assert abs(pane.mapFromScene(bounds.center()).x() - native_center.width()) <= 2
                if bounds.height() * zoom <= pane.viewport().height():
                    assert abs(pane.mapFromScene(bounds.center()).y() - native_center.height()) <= 2
    finally:
        a.close()
        b.close()


@pytest.mark.parametrize("zoom", (0.25, 0.5, 0.75))
def test_column_capacity_uses_the_transformed_gap_without_a_trailing_gap(zoom):
    a = ContinuousDocView()
    group_width = 2 * 400 + a.GAP
    a.resize(int(group_width * zoom) + 2 * a.frameWidth(), 1000)
    a.set_pages(_pages(n=3))
    _shown(a)
    try:
        a.set_zoom(zoom)
        _app.processEvents()
        assert a.cols() == 2
        assert a.sceneRect().width() * zoom == a.viewport().width()
        assert not a.horizontalScrollBar().isVisible()
    finally:
        a.close()


@pytest.mark.parametrize("preview_first", (False, True))
def test_resize_alone_reflows_the_linked_grid(preview_first):
    a, b = ContinuousDocView(), ContinuousDocView()
    b.layout_from = a
    a.link(b)
    b.link(a)
    for pane in (a, b):
        pane.resize(700, 600)
        pane.set_pages(_pages(n=8))
    _shown(a, b)
    a.set_zoom(0.5)
    try:
        for width in (450, 1000, 700, 300):
            for pane in ((b, a) if preview_first else (a, b)):
                pane.resize(width, 600)
            for _ in range(3):
                _app.processEvents()
            assert a._zoom == b._zoom == 0.5
            assert a.cols() == b.cols()
            assert a.sceneRect() == b.sceneRect()
            assert [a.page_pos(i) for i in range(8)] == [b.page_pos(i) for i in range(8)]
            assert a.page_pos(a.cols()).y() == 500 + a.GAP
    finally:
        a.close()
        b.close()
