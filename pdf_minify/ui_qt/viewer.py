"""Exact PDF pan/zoom viewer: wheel=scroll, ctrl+wheel=zoom, drag=pan.

Designer ruling: all panes stay synced — zoom/pan in either pane mirrors to
its peers (used for the original/preview pair).
"""
from collections import OrderedDict

import pymupdf as fitz
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem, QStyle
from PySide6.QtCore import Qt, QPoint, QPointF, QRectF
from PySide6.QtGui import QPixmap, QImage, QPainter, QTransform

from ..core.display import DisplayPage
from ..core.pdf_io import FITZ_LOCK


class _PdfSource:
    """Read-only native source with bounded page-list/device-tile caches.

    Qt requests only exposed items/regions. No whole-document high-DPI raster,
    filtering, worker submission, file writes or re-thresholding on zoom.
    """

    MAX_PAGES = 8
    MAX_TILES = 8
    MAX_TILE_BYTES = 32 * 1024 * 1024

    def __init__(self, path):
        self.path = str(path)
        with FITZ_LOCK:
            self.doc = fitz.open(path)
            self.rects = [fitz.Rect(page.rect) for page in self.doc]
        self._pages = OrderedDict()
        self._tiles = OrderedDict()
        self._tile_bytes = 0

    def tile(self, index, matrix, clip):
        key = (index, tuple(matrix), tuple(clip))
        cached = self._tiles.get(key)
        if cached is not None:
            self._tiles.move_to_end(key)
            return cached
        page = self._pages.get(index)
        if page is None:
            with FITZ_LOCK:
                page = DisplayPage(self.doc[index])
            self._pages[index] = page
            while len(self._pages) > self.MAX_PAGES:
                self._pages.popitem(last=False)
        self._pages.move_to_end(index)
        pix = page.render(matrix, clip)
        image = QImage(pix.samples, pix.width, pix.height, pix.stride,
                       QImage.Format_RGB888).copy()
        result = (pix.x, pix.y, image)
        self._tiles[key] = result
        self._tile_bytes += image.sizeInBytes()
        while (len(self._tiles) > self.MAX_TILES or
               self._tile_bytes > self.MAX_TILE_BYTES):
            _, (_, _, old) = self._tiles.popitem(last=False)
            self._tile_bytes -= old.sizeInBytes()
        return result

    def close(self):
        self._tiles.clear()
        self._tile_bytes = 0
        self._pages.clear()
        if self.doc is not None:
            with FITZ_LOCK:
                self.doc.close()
            self.doc = None


class _PdfPageItem(QGraphicsPixmapItem):
    """Stable prepared-page bounds; native content at actual device pixels."""

    def __init__(self, pixmap, source, index):
        super().__init__(pixmap)
        self.source, self.index = source, index
        self.setTransformationMode(Qt.FastTransformation)
        self.setFlag(QGraphicsItem.ItemUsesExtendedStyleOption, True)

    def paint(self, painter, option, widget=None):
        if self.source.doc is None:
            return
        bounds = self.boundingRect()
        exposed = option.exposedRect.intersected(bounds)
        if exposed.isEmpty():
            return
        rect = self.source.rects[self.index]
        px, py = bounds.width() / rect.width, bounds.height() / rect.height
        transform = painter.deviceTransform()
        matrix = fitz.Matrix(px * transform.m11(), 0, 0,
                             py * transform.m22(), transform.dx(), transform.dy())
        clip = fitz.Rect(exposed.left() / px, exposed.top() / py,
                         exposed.right() / px, exposed.bottom() / py)
        x, y, image = self.source.tile(self.index, matrix, clip)
        # Already rendered on the actual device grid, including fractional
        # page placement and HiDPI. Do not scale it a second time through the
        # view's world transform (or lose native shape precision on zoom).
        painter.save()
        painter.resetTransform()
        # Resetting the world transform does not remove Qt's system/device
        # translation (e.g. a viewport painted into a parent-window capture).
        # Invert the remaining device mapping, not just its HiDPI scale.
        inverse, valid = painter.deviceTransform().inverted()
        if not valid:
            painter.restore()
            return
        painter.setRenderHint(QPainter.SmoothPixmapTransform, False)
        painter.setRenderHint(QPainter.Antialiasing, False)
        painter.drawImage(inverse.mapRect(QRectF(x, y, image.width(), image.height())), image)
        painter.restore()


class PdfGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._item = QGraphicsPixmapItem()
        self._scene.addItem(self._item)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self._zoom = 1.0
        self._peers: list["PdfGraphicsView"] = []
        self._syncing = False
        self.horizontalScrollBar().valueChanged.connect(lambda _v: self._push())
        self.verticalScrollBar().valueChanged.connect(lambda _v: self._push())

    def link(self, other: "PdfGraphicsView"):
        """Mirror all zoom/pan to `other` (call both ways for a pair)."""
        if other is not self and other not in self._peers:
            self._peers.append(other)

    def set_image(self, qimg: QImage):
        self._scene.clear()
        self._item = QGraphicsPixmapItem(QPixmap.fromImage(qimg))
        self._scene.addItem(self._item)
        self._zoom = 1.0
        self.resetTransform()
        self.fitInView(self._item, Qt.KeepAspectRatio)
        self._push()

    def wheelEvent(self, e):
        if e.modifiers() & Qt.ControlModifier:
            factor = 1.25 if e.angleDelta().y() > 0 else 1 / 1.25
            new = self._zoom * factor
            if 0.1 <= new <= 20:
                self._zoom = new
                self.scale(factor, factor)
            e.accept()
            self._push()
        else:
            super().wheelEvent(e)  # page scroll; scrollbar sync propagates the pan

    def _push(self):
        if self._syncing:
            return
        for p in self._peers:
            p._pull(self)

    def _pull(self, src: "PdfGraphicsView"):
        self._syncing = True
        try:
            self.setTransform(src.transform())
            self._zoom = src._zoom
            self.horizontalScrollBar().setValue(src.horizontalScrollBar().value())
            self.verticalScrollBar().setValue(src.verticalScrollBar().value())
        finally:
            self._syncing = False

    def resizeEvent(self, e):
        super().resizeEvent(e)


class ContinuousDocView(QGraphicsView):
    """All pages, one continuous scroller: vertical flow, gap, autowrap grid.

    Zooming out reflows to as many occupied columns as fit the window width
    (§§26/164). Peers share the baseline grid and zoom/scroll (§§101/165).
    """

    GAP = 24

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.SmoothPixmapTransform, False)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self._base: list[QPixmap] = []
        self._pdf_source = None
        self._items: list[QGraphicsPixmapItem] = []
        self._layout_grid = None
        self._zoom = 1.0
        self._did_fit = False
        self._peers: list["ContinuousDocView"] = []
        self._syncing = False
        self._current = 0
        self.layout_from = None  # sibling view whose grid this one mirrors (§101)
        self.pageChanged = None  # callback(index): status + minis
        self.changed = None  # callback(): any zoom/scroll/layout change (mini reframe)
        self.relayouted = None  # callback(): grid reflowed (mini reframe, §48)
        self.verticalScrollBar().valueChanged.connect(self._on_vscroll)
        self.horizontalScrollBar().valueChanged.connect(lambda _v: self._push())

    def link(self, other: "ContinuousDocView"):
        if other is not self and other not in self._peers:
            self._peers.append(other)

    @property
    def page_count(self) -> int:
        return len(self._items)

    @property
    def current_page(self) -> int:
        return self._current

    def page_pos(self, i: int) -> QPointF:
        """Scene position (top-left) of page i's image, for navigator mapping."""
        if 0 <= i < len(self._items):
            return self._items[i].pos()
        return QPointF(0, 0)

    def clear_pdf_source(self):
        """Release open PDF handles before artifact retirement/window close."""
        if self._pdf_source is not None:
            self._pdf_source.close()
            self._pdf_source = None

    def set_pages(self, images: list[QImage], pdf_path=None):
        source = _PdfSource(pdf_path) if pdf_path is not None else None
        if source is not None and len(source.rects) != len(images):
            source.close()
            raise ValueError("Prepared pages and actual PDF must match")
        self._scene.clear()
        self.clear_pdf_source()
        self._pdf_source = source
        self._base = [QPixmap.fromImage(im) for im in images]
        self._items = []
        self._layout_grid = None
        for i, pm in enumerate(self._base):
            it = (_PdfPageItem(pm, source, i) if source is not None
                  else QGraphicsPixmapItem(pm))
            it.setTransformationMode(Qt.FastTransformation)
            self._scene.addItem(it)
            self._items.append(it)
        self._zoom = 1.0
        self.resetTransform()
        self._current = 0
        self._did_fit = False
        self.relayout()
        self.verticalScrollBar().setValue(0)

    def _page_w(self) -> int:
        return max([pm.width() for pm in self._base], default=0)

    def _page_h(self) -> int:
        return max([pm.height() for pm in self._base], default=0)

    def _gw(self) -> int:
        """Grid page width: the mirrored sibling's when set (§101)."""
        src = self.layout_from
        if src is not None and src._base:
            return src._page_w()
        return self._page_w()

    def _gh(self) -> int:
        src = self.layout_from
        if src is not None and src._base:
            return src._page_h()
        return self._page_h()

    def _gcols(self) -> int:
        src = self.layout_from
        grid = src if src is not None and src._base else self
        available = grid.maximumViewportSize()
        vw, vh = max(1, available.width()), max(1, available.height())
        # Placement uses scene-unit gaps, transformed along with the pages.
        # The last column has no trailing gap. Never reserve nonexistent pages:
        # AlignCenter must center the occupied grid, not empty column capacity.
        slot = (self._gw() + self.GAP) * self._zoom
        count = max(1, grid.page_count)

        def columns(width):
            capacity = max(1, int((width + self.GAP * self._zoom) / slot)) if slot > 0 else 1
            return min(count, capacity)

        cols = columns(vw)
        # Decide against the proposed grid, not the old scrollbar visibility:
        # wrapping can remove the vertical bar and make another column fit.
        extent = grid.style().pixelMetric(QStyle.PM_ScrollBarExtent, None, grid)
        if grid.style().styleHint(QStyle.SH_ScrollView_FrameOnlyAroundContents, None, grid):
            extent += 2 * grid.frameWidth()
        if grid.horizontalScrollBarPolicy() == Qt.ScrollBarAsNeeded and self._gw() * self._zoom > vw:
            vh -= extent
        rows = (count + cols - 1) // cols
        height = (rows * (self._gh() + self.GAP) - self.GAP) * self._zoom
        if grid.verticalScrollBarPolicy() == Qt.ScrollBarAsNeeded and height > vh:
            cols = columns(max(1, vw - extent))
        return cols

    def cols(self) -> int:
        """The same occupied grid used for page placement and mini framing."""
        return self._gcols()

    def relayout(self):
        if not self._items:
            return
        cols = self._gcols()
        pw, ph = self._gw(), self._gh()
        grid = (cols, pw, ph, len(self._items))
        if grid == self._layout_grid:
            return  # Ordinary peer pan needs no page-geometry work.
        self._layout_grid = grid
        for i, it in enumerate(self._items):
            r, c = divmod(i, cols)
            it.setPos(c * (pw + self.GAP), r * (ph + self.GAP))
        rows = (len(self._items) + cols - 1) // cols
        self.setSceneRect(0, 0, cols * (pw + self.GAP) - self.GAP,
                          rows * (ph + self.GAP) - self.GAP)
        self._notify_changed()
        if self.relayouted is not None:
            self.relayouted()

    def fit_width(self):
        src = self.layout_from
        if src is not None and src._base:
            # Mirrored pane: take the sibling's zoom, never compute our own —
            # zoom must never reset from layout differences (§101).
            self._apply_zoom(src._zoom)
            return
        if self._page_w():
            vw = max(1, self.viewport().width())
            self._apply_zoom(max(0.05, vw / (self._page_w() + self.GAP)))

    def set_zoom(self, z: float):
        self._apply_zoom(min(4.0, max(0.05, z)))

    def _apply_zoom(self, z: float):
        syncing = self._syncing
        self._syncing = True
        try:
            self._zoom = z
            self.setTransform(QTransform().scale(z, z))
            self.relayout()
        finally:
            self._syncing = syncing
        # Scrollbar signals during transform/reflow must not mirror half of a
        # zoom transaction (new camera with old page geometry) to the peer.
        self._push()

    def wheelEvent(self, e):
        if e.modifiers() & Qt.ControlModifier:
            dy = e.angleDelta().y()
            self.set_zoom(self._zoom * (1.25 if dy > 0 else 1 / 1.25))
            e.accept()
        else:
            super().wheelEvent(e)  # page scroll; scrollbar sync propagates

    def _push(self):
        if self._syncing:
            return
        self._syncing = True
        try:
            for p in self._peers:
                p._pull(self)
        finally:
            self._syncing = False
        self._notify_changed()

    def _notify_changed(self):
        if self.changed is not None:
            self.changed()

    def _pull(self, src: "ContinuousDocView"):
        syncing = self._syncing
        self._syncing = True
        try:
            self._zoom = src._zoom
            self.setTransform(src.transform())
            self.relayout()
            self.horizontalScrollBar().setValue(src.horizontalScrollBar().value())
            self.verticalScrollBar().setValue(src.verticalScrollBar().value())
        finally:
            self._syncing = syncing
        # §92: a synced zoom (Ctrl+wheel on the peer pane) changes this view
        # without touching its own scrollbars — notify so the trailing
        # reframe debounce still sees the last view change.
        self._notify_changed()

    def _on_vscroll(self, _v):
        self._push()
        self._update_current()

    def _update_current(self):
        if not self._items:
            return
        y = self.mapToScene(QPoint(0, 0)).y()
        stride = self._gh() + self.GAP
        row = max(0, int(y / stride)) if stride else 0
        idx = min(len(self._items) - 1, row * self._gcols())
        if idx != self._current:
            self._current = idx
            if self.pageChanged is not None:
                self.pageChanged(idx)

    def goto_page(self, i: int):
        if not self._items:
            return
        i = max(0, min(len(self._items) - 1, i))
        changed = (i != self._current)
        # Scroll the target item's actual scene position to the top: exact
        # for any grid shape or mixed page sizes. Same-row targets need no
        # scroll (already visible) but still become current.
        self.verticalScrollBar().setValue(int(self._items[i].pos().y() * self._zoom))
        self._current = i
        if changed and self.pageChanged is not None:
            self.pageChanged(i)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self._items and not self._did_fit and self.viewport().width() > 100:
            self._did_fit = True
            self.fit_width()
        else:
            self.relayout()
            self._push()
