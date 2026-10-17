"""Main window: continuous before/after panes, filter strip, ESC cancel."""
import logging
import os
import sys
import time
from contextlib import ExitStack
from dataclasses import dataclass
import numpy as np

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QListView, QLabel, QComboBox, QProgressBar,
    QFileDialog, QMessageBox, QCheckBox, QScrollArea, QToolBar, QBoxLayout,
    QAbstractItemView, QAbstractScrollArea, QStyledItemDelegate, QStyle,
    QStyleOptionViewItem, QStyleOptionProgressBar, QSplitter,
)
from PySide6.QtCore import Qt, QThread, Signal, QSize, QTimer, QModelIndex, QEvent, QRect, QSignalBlocker, QMimeData
from PySide6.QtGui import QImage, QIcon, QPixmap, QPainter, QFont, QPen, QAction, QColor, QPalette, QCursor

from .. import APP_ID, APP_NAME
from ..core.cancel import CancelToken
from ..core import pdf_io, threshold as T
from ..core import presets
from ..core.recipes import preset_spec, spec_key, recipe_params
from ..core.algorithms import ALGORITHMS, ALGORITHM_LABELS, BW_MODES, PALETTE_MODES, with_algorithm
from ..core.stream_compression import STREAM_POLICIES, STREAM_LABELS
from ..core.identity import canonical_uuid, new_filter_uuid, repair_filter_uuids
from ..core.pdf_io import CancelledError
from ..core.display import render_display_page
from .viewer import ContinuousDocView
from .headers import PaneHeader
from .layout import UI_PADDING, PaneBlock, PreviewPair, spaced
from .numeric import NumericSlider
from .icons import ActionIcons
from .jobs import cpu_cap, pool as filter_pool, frame_view
from .artifacts import ArtifactStore
from .lab import open_progress_lab, open_buttons_lab
from .icon_lab import IconLab
from .settings import app_settings, configure_application

import fitz

log = logging.getLogger("pdf_minify")

PREVIEW_DPI = 150
FILTER_EDIT_DEBOUNCE_MS = 300


@dataclass(frozen=True)
class _FilterResolution:
    """A leave decision can redirect selection, not merely permit it (§189)."""
    allowed: bool
    created_pid: str | None = None


def setup_logging(debug: bool = False):
    """Stdout logging for run-and-review. INFO default; --debug => DEBUG + diagnostics."""
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s", "%H:%M:%S"))
    root = logging.getLogger("pdf_minify")
    root.handlers.clear()
    root.addHandler(h)
    root.setLevel(logging.DEBUG if debug else logging.INFO)


def gray_to_qimage(gray: np.ndarray) -> QImage:
    h, w = gray.shape
    return QImage(gray.data, w, h, w, QImage.Format_Grayscale8).copy()


def bw_to_qimage(bw: np.ndarray) -> QImage:
    h, w = bw.shape
    return QImage(bw.data, w, h, w, QImage.Format_Grayscale8).copy()


def rgb_to_qimage(rgb: np.ndarray) -> QImage:
    h, w = rgb.shape[:2]
    return QImage(rgb.data, w, h, w * 3, QImage.Format_RGB888).copy()


def fmt_bytes(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}MB"
    if n >= 1_000:
        return f"{n / 1_000:.0f}KB"
    return f"{n}B"


def filter_progress(md: int, mt: int, ed: int, et: int) -> float:
    """Per-filter bar fraction (designer §§89/95).

    Minis are fast small renders, amounts are slow real encodings (measured
    ~15/85 split) — so completions are cost-weighted, and only completions
    inside the CURRENT job count. A bar therefore always starts at 0 and
    climbs with actual arrivals; nothing pending means done.
    """
    num = 0.15 * md + 0.85 * ed
    den = 0.15 * mt + 0.85 * et
    if den <= 0:
        return 1.0
    return max(0.0, min(1.0, num / den))


STRIP_PADDING = UI_PADDING
STRIP_WIDTH = 150
STRIP_PROGRESS_SCALE = 1.25  # §§198/199: 25% larger than the native default
STRIP_PREVIEW_RECT = QRect((STRIP_WIDTH - 120) // 2, STRIP_PADDING, 120, 104)
STRIP_NAME_RECT = QRect(0, STRIP_PREVIEW_RECT.bottom() + 1 + 8, STRIP_WIDTH, 13)
STRIP_ALGO_RECT = STRIP_NAME_RECT.translated(0, STRIP_NAME_RECT.height() + 1)
STRIP_AMOUNT_RECT = QRect(0, STRIP_ALGO_RECT.bottom() + 1 + 1, STRIP_WIDTH, 14)
# Equal top/bottom content padding. Qt reserves its frame and native scrollbar
# separately; neither belongs to the cell canvas or its complete drag ghost.
STRIP_ICON = (STRIP_WIDTH, STRIP_AMOUNT_RECT.bottom() + 1 + STRIP_PADDING)
FILTER_UUID_ROLE = Qt.UserRole + 1
FILTER_PROGRESS_ROLE = Qt.UserRole + 2
FILTER_DRAG_MIME = f"application/x-{APP_ID}-filter-uuid"


def _numbered_filter_label(row: int, name: str) -> str:
    """Position is presentation, never part of a filter's cached content."""
    return f"{row + 1}. {name}"


class _DragGhost(QWidget):
    """Software-composited mini above the whole window, including its panes."""

    def __init__(self, parent, pixmap: QPixmap, opacity: float):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setFocusPolicy(Qt.NoFocus)
        self.pixmap = pixmap
        self.opacity = opacity
        self.resize(pixmap.deviceIndependentSize().toSize())

    def paintEvent(self, e):  # noqa: N802
        pt = QPainter(self)
        pt.setOpacity(self.opacity)
        pt.drawPixmap(0, 0, self.pixmap)
        pt.end()


class _StripList(QListWidget):
    """Native MIME drag with a selected-mini ghost and nearest-gap bar.

    The ghost blends into the window's backing store on non-composited X11.
    Internal drops anywhere in this window use pointer X to choose a strip
    gap; moveRow fires the existing order/persistence synchronization.
    """

    selectionSettled = Signal(int)

    def __init__(self):
        super().__init__()
        self._press = None  # (pos, row) while the left button is held
        self._drag_base = None  # actual selected mini pixels
        self._drag_hotspot = None
        self._drag_overlay_pos = None
        self._drag_ghost = None
        self._drag_row = None
        self._drag_uuid = None
        self._drag_mime = None
        self._drop_gap = None  # insertion index (0..count) while dragging
        self._drop_line = None  # solid overlay bar, built on first drag
        self.setViewMode(QListView.IconMode)
        self.setFlow(QListView.LeftToRight)
        self.setWrapping(False)
        self.setResizeMode(QListView.Adjust)
        self.setGridSize(QSize(*STRIP_ICON))
        self.setIconSize(QSize(*STRIP_ICON))
        self.setUniformItemSizes(True)
        self.setSpacing(0)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setItemDelegate(_StripDelegate(self))
        # Configure layout first: QListView's movement setter also changes
        # drag flags. Enable the native MIME drag only after that setter.
        self.setMovement(QListView.Static)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
        # The style's grid-cell indicator never marks nearest gaps in
        # IconMode, so it stays off and we draw our own solid bar: theme
        # Highlight fill (a hollow rubber-band rect stood here briefly and
        # read as a broken outline — retired).
        self.setDropIndicatorShown(False)
        self.viewport().setAcceptDrops(True)
        self.horizontalScrollBar().rangeChanged.connect(self._sync_row_height)
        self._sync_background()
        self._sync_row_height()

    def viewportSizeHint(self):  # noqa: N802
        """Qt adds the actual style frame and needed scrollbars to this row."""
        return QSize(*STRIP_ICON)

    def _sync_row_height(self, *_):
        if self.flow() == QListView.LeftToRight and not self.isWrapping():
            height = self.sizeHint().height()
            if self.minimumHeight() != height or self.maximumHeight() != height:
                self.setFixedHeight(height)

    def resizeEvent(self, e):  # noqa: N802
        super().resizeEvent(e)
        self._sync_row_height()

    def _sync_background(self):
        """Neutral theme ground distinguishes white pages, only in this strip."""
        palette = self.palette()
        changed = False
        for group in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
            ground = palette.color(group, QPalette.Window).darker(105)
            if palette.color(group, QPalette.Base) != ground:
                palette.setColor(group, QPalette.Base, ground)
                changed = True
        if changed:
            self.setPalette(palette)

    def changeEvent(self, e):  # noqa: N802
        super().changeEvent(e)
        if e.type() in (QEvent.PaletteChange, QEvent.ApplicationPaletteChange, QEvent.StyleChange):
            self._sync_background()
        if e.type() in (QEvent.StyleChange, QEvent.FontChange):
            QTimer.singleShot(0, self._sync_row_height)

    GHOST_OPACITY = 0.75

    def item_for_uuid(self, uid):
        matches = self.model().match(self.model().index(0, 0), FILTER_UUID_ROLE,
                                     uid, 1, Qt.MatchExactly)
        return self.itemFromIndex(matches[0]) if matches else None

    def _is_own_drag(self, e):
        return (self._drag_uuid is not None
                and e.mimeData().hasFormat(FILTER_DRAG_MIME)
                and bytes(e.mimeData().data(FILTER_DRAG_MIME)) == self._drag_uuid.encode("ascii")
                and (e.source() is self or e.mimeData() is self._drag_mime))

    def _drag_base_pixmap(self, row: int) -> QPixmap:
        """Render the complete selected cell with the display's delegate.

        The renderer is shared with the viewport. This neither copies its
        scrollbars nor fills missing parts of a clipped screen capture.
        """
        dpr = self.devicePixelRatioF()
        base = QPixmap(*(round(n * dpr) for n in STRIP_ICON))
        base.setDevicePixelRatio(dpr)
        base.fill(self.palette().color(QPalette.Base))
        idx = self.model().index(row, 0)
        if not idx.isValid():
            return base
        if self.currentRow() != row:
            self.setCurrentRow(row)
        option = QStyleOptionViewItem()
        self.initViewItemOption(option)
        option.rect = QRect(0, 0, *STRIP_ICON)
        option.state |= QStyle.State_Selected
        pt = QPainter(base)
        self.itemDelegate().paint(pt, option, idx)
        pt.end()
        return base

    def _drag_pixmap(self, row: int) -> QPixmap:
        """Return the exported ghost with one alpha across the whole rect.

        This is also the semantic source for the live window overlay: the
        selected theme-blue ground, thumbnail, and every caption glyph are
        first rendered together, then the complete mini is blended once at
        ``GHOST_OPACITY``.
        """
        base = self._drag_base_pixmap(row)
        ghost = QPixmap(base.size())
        ghost.setDevicePixelRatio(base.devicePixelRatio())
        ghost.fill(Qt.transparent)
        pt = QPainter(ghost)
        pt.setOpacity(self.GHOST_OPACITY)
        pt.drawPixmap(0, 0, base)
        pt.end()
        return ghost

    def _move_drag_overlay(self, cursor_pos):
        if self._drag_base is None or self._drag_hotspot is None:
            return
        self._drag_overlay_pos = cursor_pos - self._drag_hotspot
        window = self.window()
        if self._drag_ghost is None:
            self._drag_ghost = _DragGhost(window, self._drag_base, self.GHOST_OPACITY)
        ghost = self._drag_ghost
        old_rect = ghost.geometry() if ghost.isVisible() else None
        ghost.move(self.viewport().mapTo(window, self._drag_overlay_pos))
        ghost.show()
        ghost.raise_()
        if self._drop_line is not None:
            self._drop_line.raise_()  # insertion bar always above the ghost
        # Flush both old and new positions during QDrag's nested event loop.
        dirty = ghost.geometry()
        if old_rect is not None:
            dirty = dirty.united(old_rect)
        window.repaint(dirty)

    def _hide_drag_overlay(self):
        self._drag_overlay_pos = None
        if self._drag_ghost is not None:
            dirty = self._drag_ghost.geometry()
            self._drag_ghost.hide()
            self.window().repaint(dirty)

    def _drag_hotspot_for(self, row: int, press_pos):
        """Offset within the source item where the mouse went down."""
        rect = self.visualRect(self.model().index(row, 0))
        return press_pos - rect.topLeft()

    def _begin_drag(self, row: int, press_pos):
        self._drag_base = self._drag_base_pixmap(row)
        self._drag_hotspot = self._drag_hotspot_for(row, press_pos)
        self._drag_row = row
        self._drag_uuid = self.item(row).data(FILTER_UUID_ROLE)
        self._drag_mime = QMimeData()
        self._drag_mime.setData(FILTER_DRAG_MIME, self._drag_uuid.encode("ascii"))
        QApplication.instance().installEventFilter(self)
        self._move_drag_overlay(press_pos)

    def _end_drag(self):
        QApplication.instance().removeEventFilter(self)
        self._show_gap(None)
        self._hide_drag_overlay()
        if self._drag_ghost is not None:
            self._drag_ghost.deleteLater()
            self._drag_ghost = None
        self._drag_base = None
        self._drag_hotspot = None
        self._drag_row = None
        self._drag_uuid = None
        self._drag_mime = None
        self._press = None

    def eventFilter(self, watched, e):  # noqa: N802
        """Route this strip's active drag across all children of its window."""
        if (self._drag_row is None or not isinstance(watched, QWidget)
                or watched.window() is not self.window()):
            return super().eventFilter(watched, e)
        kind = e.type()
        if kind == QEvent.DragLeave:
            # Leaving the strip for a pane is still a valid reorder target.
            global_pos = QCursor.pos()
            if self.window().rect().contains(self.window().mapFromGlobal(global_pos)):
                self._track_drag_at(self.viewport().mapFromGlobal(global_pos))
            else:
                self._show_gap(None)
                self._hide_drag_overlay()
            return True
        if kind not in (QEvent.DragEnter, QEvent.DragMove, QEvent.Drop):
            return super().eventFilter(watched, e)
        if not self._is_own_drag(e):
            return super().eventFilter(watched, e)
        global_pos = watched.mapToGlobal(e.position().toPoint())
        strip_pos = self.viewport().mapFromGlobal(global_pos)
        self._track_drag_at(strip_pos)
        if kind == QEvent.Drop:
            self._move_to_gap(self._gap_at(strip_pos.x()))
            self._show_gap(None)
            self._hide_drag_overlay()
        e.setDropAction(Qt.MoveAction)
        e.accept()
        return True

    def _track_drag_at(self, strip_pos):
        self._move_drag_overlay(strip_pos)
        # No Y test: a drag above a preview or below the strip snaps identically.
        self._show_gap(self._gap_at(strip_pos.x()))

    def _run_selection_input(self, handler, e):
        """Decide filter switches AFTER Qt completes one native input step.

        Press updates current before selection; keys can select twice. A
        synchronous modal rollback inside either step is overwritten by the
        unfinished framework handler. Blocking this view's intermediate
        notifications leaves Qt's input/selection/drag machinery intact.
        """
        before = self.currentRow(), tuple(self.selectedItems())
        with QSignalBlocker(self):
            handler(e)
        after = self.currentRow(), tuple(self.selectedItems())
        if after != before:
            self.selectionSettled.emit(after[0])

    def mousePressEvent(self, e):  # noqa: N802 (Qt override naming)
        if e.button() == Qt.LeftButton:
            pos = e.position().toPoint()
            item = self.itemFromIndex(self.indexAt(pos))
            self._press = (pos, item.data(FILTER_UUID_ROLE)) if item is not None else None
        self._run_selection_input(super().mousePressEvent, e)
        # A canceled switch must not arm a drag of its rejected target.
        if self._press is not None:
            current = self.currentItem()
            if current is None or current.data(FILTER_UUID_ROLE) != self._press[1]:
                self._press = None

    def keyPressEvent(self, e):  # noqa: N802
        self._run_selection_input(super().keyPressEvent, e)

    def startDrag(self, supported_actions):  # noqa: N802 (Qt hook)
        """One native controller; Qt owns threshold and pressed-state cleanup."""
        if self._press is None or self._drag_row is not None:
            return
        pos0, uid = self._press
        item = self.item_for_uuid(uid)
        if item is None or not item.isSelected():
            return
        row = self.row(item)
        from PySide6.QtGui import QDrag
        drag = QDrag(self)
        self._begin_drag(row, pos0)
        drag.setMimeData(self._drag_mime)
        # The software overlay provides true uniform alpha on the designer's
        # non-composited X11 desktop; suppress Qt's opaque native drag window.
        native_blank = QPixmap(1, 1)
        native_blank.fill(Qt.transparent)
        drag.setPixmap(native_blank)
        log.info("strip drag start row=%d UUID=%s", row, uid)
        try:
            self._track_drag_at(self.viewport().mapFromGlobal(QCursor.pos()))
            result = drag.exec(Qt.MoveAction)
            log.info("strip drag exec returned %s", result)
        finally:
            self._end_drag()
            drag.deleteLater()

    def mouseReleaseEvent(self, e):  # noqa: N802 (Qt override naming)
        self._press = None
        self._run_selection_input(super().mouseReleaseEvent, e)

    def _gap_at(self, x: int):
        """Nearest insertion gap to a viewport x: 0..count, anywhere along
        the row snaps to the closest divider (designer §128/§139)."""
        n = self.count()
        if n == 0:
            return 0
        bounds = []
        for i in range(n):
            r = self.visualRect(self.model().index(i, 0))
            if r.isValid():
                if i == 0:
                    bounds.append((0, r.left()))
                bounds.append((i + 1, r.right() + 1))
        if not bounds:
            return 0
        return min(bounds, key=lambda b: abs(x - b[1]))[0]

    def _gap_x(self, gap: int) -> int | None:
        """Viewport x of a gap index for the overlay bar."""
        n = self.count()
        if gap <= 0 and n:
            r = self.visualRect(self.model().index(0, 0))
            return r.left() - 1 if r.isValid() else None
        if 0 < gap <= n:
            r = self.visualRect(self.model().index(gap - 1, 0))
            return r.right() + 1 if r.isValid() else None
        return None

    def _show_gap(self, gap: int | None):
        """Position (or hide) the solid insertion bar for a gap index."""
        from PySide6.QtWidgets import QWidget as _QW
        self._drop_gap = gap
        if gap is None:
            if self._drop_line is not None:
                self._drop_line.hide()
            return
        x = self._gap_x(gap)
        if x is None:
            if self._drop_line is not None:
                self._drop_line.hide()
            return
        if self._drop_line is None:
            self._drop_line = _QW(self.window())
            self._drop_line.setAttribute(Qt.WA_TransparentForMouseEvents)
            pal = self.palette()
            self._drop_line.setAutoFillBackground(True)
            role = self._drop_line.backgroundRole()
            pal.setColor(role, pal.color(QPalette.Highlight))
            self._drop_line.setPalette(pal)
        top_left = self.viewport().mapTo(self.window(), self.viewport().rect().topLeft())
        self._drop_line.setGeometry(top_left.x() + x - 1, top_left.y() + 4,
                                    3, max(8, self.viewport().height() - 8))
        self._drop_line.show()
        self._drop_line.raise_()

    def dragEnterEvent(self, e):  # noqa: N802 (Qt override naming)
        if self._is_own_drag(e):
            self._move_drag_overlay(e.position().toPoint())
            e.acceptProposedAction()
        else:
            e.ignore()  # never let foreign serialized model data insert filters

    def dragMoveEvent(self, e):  # noqa: N802 (Qt override naming)
        if self._is_own_drag(e):
            self._move_drag_overlay(e.position().toPoint())
            gap = self._gap_at(e.position().toPoint().x())
            if gap != self._drop_gap:
                self._show_gap(gap)
            e.acceptProposedAction()
        else:
            e.ignore()

    def dragLeaveEvent(self, e):  # noqa: N802 (Qt override naming)
        self._show_gap(None)
        self._hide_drag_overlay()
        super().dragLeaveEvent(e)

    def dropEvent(self, e):  # noqa: N802 (Qt override naming)
        gap = self._gap_at(e.position().toPoint().x())
        self._show_gap(None)
        self._hide_drag_overlay()
        if not self._is_own_drag(e):
            e.ignore()
            return
        if self._move_to_gap(gap):
            e.setDropAction(Qt.MoveAction)
            e.accept()
        else:
            e.ignore()

    def _move_to_gap(self, gap: int) -> bool:
        source_item = self.item_for_uuid(self._drag_uuid) if self._drag_uuid is not None else self.currentItem()
        src = self.row(source_item) if source_item is not None else -1
        if not 0 <= src < self.count():
            return False
        gap = max(0, min(gap, self.count()))
        if gap in (src, src + 1):
            return True  # valid drop, already at that divider
        # Qt takes the destination BEFORE removing the source row. Subtract
        # only for the final selected row, never for moveRow's gap argument.
        dst = gap - 1 if gap > src else gap
        log.info("strip drop src=%d gap=%s dst=%d", src, gap, dst)
        moved = bool(self.model().moveRow(QModelIndex(), src, QModelIndex(), gap))
        if moved:
            self.setCurrentRow(dst)
        return moved

    def wheelEvent(self, e):  # noqa: N802 (Qt override naming)
        # §96: NO vertical scroll ever (the bar is hidden, so any vertical
        # drift reads as a bug) — the wheel drives the horizontal bar.
        hb = self.horizontalScrollBar()
        if e.pixelDelta() and not e.pixelDelta().isNull():
            ticks = e.pixelDelta().y() / 40.0
        else:
            ticks = e.angleDelta().y() / 120.0
        step = hb.pageStep() or 120
        hb.setValue(int(hb.value() - ticks * step / 8))
        e.accept()


class _StripDelegate(QStyledItemDelegate):
    """One full-cell renderer for display and drag, with the approved wash.

    Custom item painting is the Qt delegate extension point. Explicit cell
    geometry avoids IconMode's independent icon/text layout and decoration
    accent lines. The content canvas has neither selection chrome nor a
    positional label: the current model row supplies numbering on every paint.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._progress_reference = None
        self._progress_template = None

    def set_progress_reference(self, reference):
        """One hidden formatter, using the actual default progress bar (§185)."""
        self._progress_reference = reference
        self._progress_template = QProgressBar(reference)
        self._progress_template.setRange(0, 10_000)
        self._progress_template.setFocusPolicy(Qt.NoFocus)
        self._progress_template.hide()

    def progress_rects(self, cell):
        """1.25× native bar, centered in the full mini frame (§§191/198/199)."""
        height = min(round(self._progress_reference.sizeHint().height() * STRIP_PROGRESS_SCALE),
                     max(1, cell.height() - 2*STRIP_PADDING))
        top = cell.top() + (cell.height() - height)//2
        bar = QRect(cell.left() + STRIP_PADDING, top,
                    cell.width() - 2*STRIP_PADDING, height)
        return bar, QRect(bar)  # opaque backing, never extra white padding

    def _paint_progress(self, painter, cell, progress):
        reference, template = self._progress_reference, self._progress_template
        if reference is None or progress is None or progress >= 1:
            return
        # Values/format are independent of the real aggregate status bar.
        # Sample its current theme/font/direction on every paint, not into
        # cached icons. No QWidget is installed per model row.
        if template.style() is not reference.style():
            template.setStyle(reference.style())
        template.setPalette(reference.palette())
        font = QFont(reference.font())
        if font.pixelSize() > 0:
            font.setPixelSize(round(font.pixelSize() * STRIP_PROGRESS_SCALE))
        else:
            font.setPointSizeF(font.pointSizeF() * STRIP_PROGRESS_SCALE)
        template.setFont(font)
        template.setLocale(reference.locale())
        template.setLayoutDirection(reference.layoutDirection())
        template.setEnabled(reference.isEnabled())
        template.setFormat(reference.format())
        template.setAlignment(reference.alignment())
        template.setTextVisible(reference.isTextVisible())
        template.setInvertedAppearance(reference.invertedAppearance())
        template.setValue(max(0, min(9_999, int(progress * 10_000))))
        option = QStyleOptionProgressBar()
        template.initStyleOption(option)
        option.styleObject = None  # no shared widget animation state across rows
        option.rect, backing = self.progress_rects(cell)
        painter.save()
        # Like a native widget's paint bounds: styles must not draw border
        # pixels outside the overlay and into the shared highlight inset.
        painter.setClipRect(backing, Qt.IntersectClip)
        painter.fillRect(backing, Qt.white)
        painter.setFont(font)
        # QCommonStyle may draw the label with the painter's current pen
        # (NoRole). Match QProgressBar's widget painter, not the mini caption.
        painter.setPen(reference.palette().color(reference.foregroundRole()))
        painter.setLayoutDirection(reference.layoutDirection())
        # Native widgets paint in local coordinates. Keep fractional text/chunk
        # clipping identical even when the mini is translated or scrolled.
        painter.translate(option.rect.topLeft())
        option.rect.moveTo(0, 0)
        template.resize(option.rect.size())
        reference.style().drawControl(QStyle.CE_ProgressBar, option, painter, template)
        painter.restore()

    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        painter.save()
        painter.setClipRect(opt.rect)
        painter.fillRect(opt.rect, opt.palette.color(QPalette.Base))
        label = _numbered_filter_label(index.row(), opt.text)
        if not opt.icon.isNull():
            painter.drawPixmap(opt.rect.topLeft(), opt.icon.pixmap(QSize(*STRIP_ICON)))
            font = QFont(opt.font)
            font.setPointSize(max(7, font.pointSize() - 2))
            painter.setFont(font)
            painter.setPen(opt.palette.color(QPalette.WindowText))
            caption = STRIP_NAME_RECT.translated(opt.rect.topLeft())
            painter.drawText(caption, Qt.AlignHCenter, label)
        else:
            painter.setFont(opt.font)
            painter.setPen(opt.palette.color(QPalette.WindowText))
            painter.drawText(opt.rect, Qt.AlignCenter | Qt.TextWordWrap, label)
        if opt.state & QStyle.State_Selected:
            wash = opt.palette.color(QPalette.Highlight)
            wash.setAlphaF(0.35)
            painter.fillRect(opt.rect, wash)
        # The backing must stay opaque white, even on the selected cell.
        self._paint_progress(painter, opt.rect, index.data(FILTER_PROGRESS_ROLE))
        painter.restore()

    def sizeHint(self, option, index):
        return QSize(*STRIP_ICON)


def _fit_combo(combo) -> int:
    """Size a dropdown to its largest item (designer §130).

    Minimum width fits the widest entry (text + icon/arrow padding); when
    the panel squeezes narrower, Qt shows end-ellipsis, and the tooltip
    always carries the full current text (same contract as the pane
    headers, §124). Returns the width in px.
    """
    fm = combo.fontMetrics()
    widest = 0
    for i in range(combo.count()):
        widest = max(widest, fm.horizontalAdvance(combo.itemText(i)))
    width = widest + 40
    combo.setMinimumWidth(width)
    combo.setToolTip(combo.itemText(combo.currentIndex()))
    return width


def _preset_algo(pid: str, spec: dict | None = None) -> str:
    """One recipe readout for mini and preview, including live edits."""
    recipe = preset_spec(presets.get(pid)) if spec is None else spec
    mode = recipe["mode"]
    page_handling = "FFPR · " if recipe.get("force_raster") else ""
    if mode in BW_MODES:
        strategy, dpi = recipe["strategy"], recipe["dpi"]
        codec = "JBIG2" if mode == "bw" else "Flate BW"
        return page_handling + (f"simple T{recipe.get('t', 180)}" if strategy == "simple" else strategy) + f" · {dpi}dpi · {codec}"
    if mode == "color":
        return page_handling + f"JPEG q{recipe['jpeg_q']} · {recipe['dpi_cap']}dpi"
    if mode == "jpx":
        codec = "JPEG2000 lossless" if recipe.get("lossless") else f"JPEG2000 r{recipe['rate']}"
        return page_handling + f"{codec} · {recipe['dpi_cap']}dpi"
    if mode == "indexed":
        return page_handling + f"Indexed {recipe['colors']}c · {recipe['dpi_cap']}dpi"
    if mode == "layered-jbig2":
        return page_handling + f"JBIG2 Color {recipe['colors']}c · {recipe['dpi_cap']}dpi"
    return "as-is"


class CopyWorker(QThread):
    done = Signal(str)
    failed = Signal(str)
    progressed = Signal(int, int)

    def __init__(self, in_path, out_path, token):
        super().__init__()
        self.args = (in_path, out_path, token)

    def run(self):
        import tempfile
        in_path, out_path, token = self.args
        partial = None
        try:
            total, done = os.path.getsize(in_path), 0
            with open(in_path, "rb") as source, tempfile.NamedTemporaryFile(
                    prefix=f".{APP_ID}-export-", suffix=".pdf",
                    dir=os.path.dirname(os.path.abspath(out_path)), delete=False) as dest:
                partial = dest.name
                while True:
                    if token.cancelled:
                        raise CancelledError()
                    block = source.read(1024 * 1024)
                    if not block:
                        break
                    dest.write(block)
                    done += len(block)
                    self.progressed.emit(done, total)
            if token.cancelled:
                raise CancelledError()
            os.replace(partial, out_path)
            partial = None
            self.done.emit(out_path)
        except Exception as e:  # noqa: BLE001
            self.failed.emit("Cancelled" if isinstance(e, CancelledError) else str(e))
        finally:
            if partial is not None:
                os.unlink(partial)


class MainWindow(QMainWindow):
    def __init__(self, start_pdf: str | None = None):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1100, 650)
        self.doc = None
        self.path = None
        self._orig_bytes: int | None = None  # input file size for % (designer §61)
        self.token = CancelToken()
        self.worker: CopyWorker | None = None
        self._gen = 0  # background progress generation (cosmetic bar only)
        self._jobs: set = set()  # in-flight workers: dropping the last ref while
        self._saved_specs: dict = {}
        self._draft_specs: dict = {}
        self._active_pid = None
        self._loading_controls = False
        self._switching_filter = False
        self._closing_requested = False
        self._export_keys: set = set()
        self._mini_view: dict = {}  # pid -> exact-view composite for today (§48)
        self._mini_amount: dict = {}    # pid -> formatted EXACT full-PDF bytes (§149)
        self._filter_prog: dict = {}  # pid -> 0.0..1.0 per-filter progress (§43)
        self._shown_preview_key = None  # preview cache key currently shown (§108)
        self._applying = False  # True while a background preview is applied (no sync/cascade)
        from .paths import app_temp_dir, sweep_stale_temps
        self._temp_root = app_temp_dir()  # OS temp, never the repo (§123)
        sweep_stale_temps()  # temps are regenerable; nothing of value lost
        self._artifacts = ArtifactStore(app_temp_dir("saves"))
        log.info("runtime artifacts: %s (GUI PID %d)", self._artifacts.root, os.getpid())
        self.setAcceptDrops(True)

        root = QWidget()
        self.setCentralWidget(root)
        # §188: the root alone owns outer padding; components own no duplicate
        # wrapper margins. One token also governs every inter-region gutter.
        top = spaced(QVBoxLayout(root), inset=UI_PADDING)
        self.before = ContinuousDocView()  # baseline, all pages
        self.after = ContinuousDocView()   # selected filter, all pages
        self.before.link(self.after)  # designer ruling: panes always synced
        self.after.link(self.before)
        self.after.layout_from = self.before  # same grid, always (§101)
        self.before.pageChanged = self._on_page_changed
        self.after.pageChanged = self._on_page_changed
        self.before.setToolTip("Baseline — original, unmodified")
        self.after.setToolTip("Filter preview — scroll=pan, ctrl+wheel=zoom, drag=pan")
        # §60: per-pane headers ride with the splitter halves.
        self.beforeHeader = PaneHeader("Original — no document")
        self.afterHeader = PaneHeader("Preview — no document")
        self.preview_block = PreviewPair(self.before, self.beforeHeader,
                                         self.after, self.afterHeader)
        self.panes = self.preview_block.panes  # §107: equal layout, no splitter
        self._apply_custom_presets()  # renames + copies before widgets (§109)
        self._saved_specs = {p["id"]: preset_spec(p) for p in presets.PRESETS
                             if p["mode"] != "passthrough"}
        self.filters = _StripList()  # filter strip: full-width, below panes+panel
        self.filters.model().rowsMoved.connect(self._restrip_ordered)
        # One selected filter, with the full-cell theme wash; no focus frame.
        self.filters.setSelectionMode(QAbstractItemView.SingleSelection)
        self.filters.setFocusPolicy(Qt.NoFocus)
        self.filters.setAccessibleName("Filters")  # §188: no visible title row
        self.filters.setToolTip("Filters — click to preview (left stays baseline)")
        initial_ids = [p["id"] for p in presets.PRESETS if p["mode"] != "passthrough"]
        for pid in self._apply_strip_order(initial_ids):
            p = presets.get(pid)
            item = QListWidgetItem(p["label"])
            item.setData(Qt.UserRole, pid)
            item.setData(FILTER_UUID_ROLE, p["uuid"])
            item.setToolTip(p["blurb"])
            item.setSizeHint(QSize(*STRIP_ICON))
            self.filters.addItem(item)
        # §98: the ring must mark the default filter from the start, not only
        # after the first click (safe: no document yet, dispatches no-op).
        try:
            self.filters.setCurrentRow(self._strip_ids.index(presets.default_preset_id()))
        except ValueError:
            pass
        right = spaced(QVBoxLayout(), inset=UI_PADDING)
        # §68/§69: the right block opens with the main info box — everything
        # constant for the original and every filter (name, pages, original
        # size). The left header (§60) stays as it is.
        self.file_label = QLabel("No file")
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet("QLabel { background: palette(base); "
                                      "border: 1px solid palette(mid); padding: 4px; }")
        right.addWidget(QLabel("File:"))
        right.addWidget(self.file_label)
        self.preset = QComboBox()
        self._rebuild_preset_combo()  # strip order, Original first (§128)
        _def = self.preset.findData(presets.default_preset_id())
        self.preset.setCurrentIndex(_def if _def >= 0 else 0)
        self.compression = QComboBox()
        self.compression.setAccessibleName("Image compression")
        for mode, label in ALGORITHMS:
            self.compression.addItem(label, mode)
        self.compression.setToolTip("Bitmap encoding only. Native text/vectors and fonts "
                                   "still use lossless PDF stream/container optimization.")
        self.stream_compression = QComboBox()
        self.stream_compression.setAccessibleName("PDF stream compression")
        for policy, label in STREAM_POLICIES:
            self.stream_compression.addItem(label, policy)
        self.stream_compression.setToolTip("Lossless native text/vector/font streams only; "
                                          "image bytes and image compression stay unchanged. "
                                          "Zopfli is slower; Brotli needs compatible readers.")
        self.stream_warning = QLabel("Brotli requires a compatible PDF 2.0 reader; "
                                     "older readers may show missing content.")
        self.stream_warning.setWordWrap(True)
        self.stream_warning.hide()
        self.brotli_declaration = QCheckBox("Include Brotli extension declaration (Compatibility)")
        self.brotli_declaration.setToolTip(
            "Include PDF 2.0 Brotli extension metadata for readers that use it. "
            "Off by default to minimize file size. This does not add Brotli decoding "
            "support to an incompatible reader.")
        self.brotli_declaration.hide()
        self.strategy = QComboBox()
        self.strategy.addItems(["otsu", "simple", "adaptive", "sauvola"])
        self.strategy.setAccessibleName("Threshold method")
        self.threshold_control = NumericSlider(0, 255, 180, "Threshold")
        self.slider = self.threshold_control.slider
        self.threshold_value = self.threshold_control.number
        self.t_label = QLabel("&Threshold (T):")
        self.t_label.setBuddy(self.threshold_value)
        self.colors_control = NumericSlider(2, 256, 64, "Palette colors")
        self.colors = self.colors_control.slider  # §67: forced palette count
        self.colors_value = self.colors_control.number
        self.colors_control.setToolTip("Maximum bitmap palette colors, including white: "
                                      "JBIG2 Color and Flate Color (palette). No dithering.")
        self.c_label = QLabel("&Colors:")
        self.c_label.setBuddy(self.colors_value)
        self.lossless_box = QCheckBox("Lossless")  # §100: JPX reversible
        self.lossless_box.setToolTip("Lossless encoding — only JPEG2000 offers the choice; "
                                     "every other filter shows its fixed state, greyed.")
        self.dpi = QComboBox()
        for d in presets.RASTER_DPIS:
            self.dpi.addItem(f"{d} dpi", d)
        self.dpi.setCurrentIndex(list(presets.RASTER_DPIS).index(presets.DEFAULT_DPI))
        self.page_size = QComboBox()
        for pid in presets.PAGE_SIZE_IDS:
            self.page_size.addItem(presets.PAGE_SIZE_LABELS[pid], pid)
        self.page_size.setCurrentIndex(list(presets.PAGE_SIZE_IDS).index(presets.DEFAULT_PAGE_SIZE))
        for _cb in (self.compression, self.stream_compression, self.strategy, self.dpi, self.page_size):
            _fit_combo(_cb)  # static items: fit once (§130)
        self.force_raster = QCheckBox("Force full-page raster")
        self.force_raster.setChecked(False)
        self.force_raster.setToolTip("ON: flatten the complete page, including text and vectors, then apply the selected image compression. OFF: transform one image canvas and retain native text/vector artwork. Use ON to flatten original stacking; full-page rasterization loses text selectability and vector precision.")
        self.save_act = QAction("Save", self)
        self.save_act.setToolTip("Save reduced PDF (Ctrl+S)")
        self.save_act.triggered.connect(self.save)
        self.cancel_act = QAction("X", self)
        self.cancel_act.setToolTip("X stops the running save — nothing else to undo (ESC)")
        self.cancel_act.setEnabled(False)
        right.addWidget(QLabel("Filter:"))
        # §§109/112/162: name dropdown and icon-only filter actions share a row.
        nameRow = spaced(QHBoxLayout())
        nameRow.addWidget(self.preset, 1)
        # §120: icon-only filter buttons (tooltips carry the words).
        self.rename_btn = QPushButton("")
        self.rename_btn.setToolTip("Rename the current filter")
        self.rename_btn.clicked.connect(self.rename_filter)
        self.rename_btn.setIconSize(QSize(20, 20))
        self.copy_btn = QPushButton("")
        self.copy_btn.setToolTip("Save As… — keep this filter and save a copy under a new name")
        self.copy_btn.clicked.connect(self.copy_filter)
        self.copy_btn.setIconSize(QSize(20, 20))
        self.revert_btn = QPushButton("")
        self.revert_btn.setAccessibleName("Revert Changes")
        self.revert_btn.setToolTip("Revert Changes")
        self.revert_btn.clicked.connect(self.revert_filter)
        self.revert_btn.setIconSize(QSize(20, 20))
        self.revert_btn.setEnabled(False)
        self.keep_btn = QPushButton("")
        self.keep_btn.setToolTip("Save the current settings into this filter")
        self.keep_btn.clicked.connect(self.save_filter)
        self.keep_btn.setIconSize(QSize(20, 20))
        nameRow.addWidget(self.revert_btn)
        nameRow.addWidget(self.rename_btn)
        nameRow.addWidget(self.copy_btn)
        nameRow.addWidget(self.keep_btn)
        right.addLayout(nameRow)
        # §54: filter details readout — the active filter's full recipe.
        self.details = QLabel()
        self.details.setWordWrap(True)
        self.details.setStyleSheet("QLabel { background: palette(base); "
                                   "border: 1px solid palette(mid); padding: 4px; }")
        # §§128/203: algorithm, threshold method, DPI and page size sit beside
        # labels (label left, control fills the rest).
        compressionRow = spaced(QHBoxLayout())
        compressionLabel = QLabel("&Image compression:")
        compressionLabel.setBuddy(self.compression)
        compressionRow.addWidget(compressionLabel)
        compressionRow.addWidget(self.compression, 1)
        right.addLayout(compressionRow)
        streamRow = spaced(QHBoxLayout())
        streamLabel = QLabel("PDF &streams:")
        streamLabel.setBuddy(self.stream_compression)
        streamRow.addWidget(streamLabel)
        streamRow.addWidget(self.stream_compression, 1)
        right.addLayout(streamRow)
        right.addWidget(self.brotli_declaration)
        right.addWidget(self.stream_warning)
        right.addWidget(QLabel("Filter details:"))
        right.addWidget(self.details)
        stratRow = spaced(QHBoxLayout())
        self.strategy_label = QLabel("Threshold &method:")
        self.strategy_label.setBuddy(self.strategy)
        stratRow.addWidget(self.strategy_label)
        stratRow.addWidget(self.strategy, 1)
        right.addLayout(stratRow)
        right.addWidget(self.t_label)
        right.addWidget(self.threshold_control)
        right.addWidget(self.c_label)
        right.addWidget(self.colors_control)
        right.addWidget(self.lossless_box)
        dpiRow = spaced(QHBoxLayout())
        dpiRow.addWidget(QLabel("Raster DPI:"))
        dpiRow.addWidget(self.dpi, 1)
        right.addLayout(dpiRow)
        psRow = spaced(QHBoxLayout())
        psRow.addWidget(QLabel("Page size:"))
        psRow.addWidget(self.page_size, 1)
        right.addLayout(psRow)
        right.addWidget(self.force_raster)
        # §76/§78/§85/§86: zoom is a joined segmented control — out, live
        # editable % (Evince/Okular convention: preset menu + type any
        # number), in — 16px standard icons (§197), zero-gap group look.
        zoomBar = QToolBar("Zoom")
        zoomBar.setIconSize(QSize(16, 16))
        zoomBar.layout().setSpacing(0)
        zoomBar.layout().setContentsMargins(0, 0, 0, 0)
        zoomBar.setStyleSheet("QToolBar { spacing: 0px; }"
                              "QToolButton { border-radius: 0px; }")
        self.zoom_out_act = QAction("Out", self)
        self.zoom_out_act.setToolTip("Zoom out (Ctrl+Minus)")
        self.zoom_out_act.triggered.connect(lambda: self._button_zoom(1 / 1.25))
        self.zoom_combo = QComboBox()
        self.zoom_combo.setEditable(True)
        for pct in (25, 50, 75, 100, 125, 150, 200, 300, 400):
            self.zoom_combo.addItem(f"{pct}%", pct / 100)
        self.zoom_combo.setCurrentIndex(3)
        self.zoom_combo.setMinimumWidth(76)
        self.zoom_combo.setToolTip("Zoom % — pick a preset or type a number")
        self.zoom_combo.activated.connect(self._zoom_combo_chosen)
        self.zoom_combo.lineEdit().returnPressed.connect(self._zoom_combo_chosen)
        self.zoom_in_act = QAction("In", self)
        self.zoom_in_act.setToolTip("Zoom in (Ctrl+Plus)")
        self.zoom_in_act.triggered.connect(lambda: self._button_zoom(1.25))
        zoomBar.addAction(self.zoom_out_act)
        zoomBar.addWidget(self.zoom_combo)
        zoomBar.addAction(self.zoom_in_act)
        zoomBar.addSeparator()
        zoomBar.addAction(self.save_act)
        zoomBar.addAction(self.cancel_act)
        zoomBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self._action_icons = ActionIcons(self)
        for target, name in (
                (self.revert_btn, "document-revert"), (self.rename_btn, "edit-rename"),
                (self.copy_btn, "edit-copy"), (self.keep_btn, "document-save"),
                (self.save_act, "document-save"), (self.cancel_act, "process-stop"),
                (self.zoom_out_act, "zoom-out"), (self.zoom_in_act, "zoom-in")):
            context = target if isinstance(target, QPushButton) else zoomBar
            self._action_icons.bind(target, name, context=context)
        right.addWidget(zoomBar)
        right.addStretch(1)

        panel = QWidget()
        panel.setLayout(right)
        self.panelScroll = QScrollArea()
        self.panelScroll.setWidget(panel)
        self.panelScroll.setWidgetResizable(True)
        # §118: when the divider squeezes the panel below its content, a
        # horizontal scrollbar appears instead of clipping it.
        self.panelScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.panelScroll.setMinimumWidth(250)
        self.configurationHeader = PaneHeader("Configuration")
        self.configuration_block = PaneBlock(self.configurationHeader, self.panelScroll)
        # §117: the divider between the previews and the right panel is a
        # real draggable splitter (like the old preview divider) — the
        # panel-width slider is gone. §107 still holds: nothing splits the
        # two panes themselves, they stay locked equal inside PreviewPair.
        self.panel_split = QSplitter(Qt.Horizontal)
        self.panel_split.setChildrenCollapsible(False)
        self.panel_split.setHandleWidth(UI_PADDING)
        self.panel_split.setStyleSheet(
            "QSplitter::handle:horizontal { background: palette(mid); "
            "border-left: 1px solid palette(dark); "
            "border-right: 1px solid palette(dark); }")
        self.panel_split.addWidget(self.preview_block)
        self.panel_split.addWidget(self.configuration_block)
        self.panel_split.setStretchFactor(0, 1)
        self.panel_split.setStretchFactor(1, 0)
        # §§77/188: no strip title/placeholder row; both full-width regions
        # share one inset and gutter, and the panel ends above the strip.
        top.addWidget(self.panel_split, 1)
        top.addWidget(self.filters)

        self.page_label = QLabel("No document")
        self.status = QLabel("Drop a PDF here or Open… (File > Open)")
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(220)
        self.filters.itemDelegate().set_progress_reference(self.progress)
        sb = self.statusBar()
        sb.addWidget(self.status, 1)
        sb.addPermanentWidget(self.page_label)
        sb.addPermanentWidget(self.progress)

        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        # ONE trailing edit timer for every recipe control (§183). Separate
        # from view-only reframing; slider/spinner input has no private timer.
        self._preview_timer.setTimerType(Qt.PreciseTimer)
        self._preview_timer.setInterval(FILTER_EDIT_DEBOUNCE_MS)
        self._preview_timer.timeout.connect(self._dispatch_filters)
        # §47/§48: view changes (scroll/pan/zoom/resize/page) only REFRAME
        # minis from cache — they never dispatch. Debounced: one reframe max
        # per settle, no matter how many scroll ticks arrived.
        self._reframe_timer = QTimer(self)
        self._reframe_timer.setSingleShot(True)
        self._reframe_timer.setInterval(150)
        self._reframe_timer.timeout.connect(self._reframe_minis)

        self.save_act.triggered.connect(self.save)
        self.cancel_act.triggered.connect(self.cancel)
        self.before.changed = self._on_view_changed
        self.before.relayouted = self._reframe_timer.start
        self.after.relayouted = self._reframe_timer.start
        for control, signal in ((self.threshold_control, "valueChanged"),
                                (self.colors_control, "valueChanged"),
                                (self.lossless_box, "toggled"), (self.strategy, "currentTextChanged"),
                                (self.compression, "currentIndexChanged"),
                                (self.stream_compression, "currentIndexChanged"),
                                (self.brotli_declaration, "toggled"),
                                (self.dpi, "currentIndexChanged"), (self.page_size, "currentIndexChanged"),
                                (self.force_raster, "toggled")):
            getattr(control, signal).connect(self._filter_edited)
        self.preset.currentIndexChanged.connect(self._preset_chosen)
        # Native inputs notify only after Qt's complete handler (§161).
        # Programmatic setCurrentRow still emits its normal final signal.
        self.filters.currentRowChanged.connect(self._filterstrip_chosen)
        self.filters.selectionSettled.connect(self._filterstrip_chosen)

        filem = self.menuBar().addMenu("&File")
        open_act = filem.addAction("Open…")
        open_act.setShortcut("Ctrl+O")
        open_act.triggered.connect(self.open_dialog)
        save_act = filem.addAction("Save reduced…")
        save_act.setShortcut("Ctrl+S")
        save_act.triggered.connect(self.save)
        quit_act = filem.addAction("Quit")
        quit_act.setShortcut("Ctrl+Q")
        quit_act.triggered.connect(self.close)
        view = self.menuBar().addMenu("&View")
        main_menu = view.addMenu("&Main panes")
        self._main_actions = {}
        for label, mode in [("Side by side (H)  Ctrl+1", "side-h"),
                            ("Stacked (V)  Ctrl+2", "stack-v"),
                            ("Single (toggle)  Ctrl+3", "single")]:
            a = main_menu.addAction(label)
            a.setCheckable(True)
            a.triggered.connect(lambda _=False, m=mode: self.set_main_mode(m))
            self._main_actions[mode] = a
        filt_menu = view.addMenu("&Filter thumbnails")
        self._filter_actions = {}
        for label, mode in [("Filmstrip (H)", "film-h"), ("Rail (V)", "rail-v"), ("Grid", "grid")]:
            a = filt_menu.addAction(label)
            a.setCheckable(True)
            a.triggered.connect(lambda _=False, m=mode: self.set_filter_mode(m))
            self._filter_actions[mode] = a
        lab_menu = view.addMenu("&Widget lab")
        lab_menu.addAction("Progress bars…").triggered.connect(
            lambda: self._labs.append(open_progress_lab(self)))
        lab_menu.addAction("Zoom/Save/Cancel buttons…").triggered.connect(
            lambda: self._labs.append(open_buttons_lab(self)))
        self._labs: list = []
        self._icon_lab = None
        self.icon_lab_act = view.addAction("&Icon Lab…", self._open_icon_lab)
        self.set_main_mode("side-h")
        self.set_filter_mode("film-h")

        # ESC anywhere cancels
        self.cancel_shortcut = self.cancel_act  # action doubles as shortcut
        self._refresh_details()
        self._sync_threshold_enabled()
        self._active_pid = self.preset.currentData()
        self._load_filter_controls(self._active_pid)
        self.setWindowTitle(f"{APP_NAME}[*]")
        self._refresh_dirty_labels()
        if start_pdf:
            self.open_file(start_pdf)

    # --- presets + view modes ---
    def _custom_store(self):
        return app_settings()

    def _apply_custom_presets(self):
        """Load recipes, preserving pasted copies and repairing UUIDs (§155)."""
        from ..core.filter_defaults import RASTER_DEFAULTS_REVISION, migrate_raster_dpi
        store = self._custom_store()
        try:
            renames = store.value("customRenames", {}) or {}
            customs = store.value("customPresets", []) or []
        except Exception:  # noqa: BLE001
            renames, customs = {}, []
        try:
            dpi_revision = int(store.value("rasterDefaultsRevision", 0) or 0)
        except (TypeError, ValueError):
            # A malformed migration marker must not hide valid saved filters.
            dpi_revision = 0
        entries = {p["id"]: p for p in presets.PRESETS}
        seen_records, loaded, aliases_changed = set(), [], False
        for c in customs:
            if not isinstance(c, dict) or not isinstance(c.get("id"), str):
                continue
            c = dict(c)
            if c["id"] in seen_records:
                # Copy/pasting the full record also duplicates the legacy alias.
                # Preserve that filter instead of silently overwriting the first.
                candidate = canonical_uuid(c.get("uuid"))
                taken = {p.get("uuid") for p in entries.values()} | entries.keys()
                if candidate is None or candidate in taken:
                    candidate = new_filter_uuid(
                        [*taken, *(p.get("uuid") for p in customs if isinstance(p, dict))])
                c["id"] = c["uuid"] = candidate
                aliases_changed = True
            seen_records.add(c["id"])
            if c["id"] not in entries:
                presets.PRESETS.append(c)
                entries[c["id"]] = c
            else:
                p = entries[c["id"]]
                p["params"] = dict(c.get("params", p["params"]))
                p["mode"] = c.get("mode", p["mode"])
                p["label"] = c.get("label", p["label"])
                if "uuid" in c:
                    p["uuid"] = c["uuid"]
            loaded.append(entries[c["id"]])
        identities_changed = repair_filter_uuids(presets.PRESETS)
        schema_changed = any(isinstance(p, dict) and isinstance(p.get("id"), str)
                             and "uuid" not in p for p in customs)
        migrate_dpi = dpi_revision < RASTER_DEFAULTS_REVISION
        dpi_changed = migrate_raster_dpi(presets.PRESETS) if migrate_dpi else []
        identity_changed = aliases_changed or identities_changed or schema_changed
        if identity_changed or dpi_changed:
            store.setValue("customPresets", [dict(p) for p in loaded])
        if migrate_dpi:
            store.setValue("rasterDefaultsRevision", RASTER_DEFAULTS_REVISION)
        if identity_changed or dpi_changed or migrate_dpi:
            store.sync()
        if identity_changed:
            log.warning("filter identity migration: repaired missing/invalid/duplicate UUIDs or aliases")
        if migrate_dpi:
            log.info("filter resolution migration: %d saved recipes now use %d DPI", len(dpi_changed), presets.DEFAULT_DPI)
        for p in presets.PRESETS:
            if p["id"] in renames:
                p["label"] = renames[p["id"]]

    def _open_icon_lab(self):
        if self._icon_lab is None:
            self._icon_lab = IconLab(self)
        self._icon_lab.show()
        self._icon_lab.raise_()
        self._icon_lab.activateWindow()

    def _preset_label(self, pid: str) -> str:
        return presets.get(pid)["label"]

    def _spec_for(self, pid):
        return dict(self._draft_specs.get(pid, self._saved_specs[pid]))

    def _filter_display_name(self, pid):
        return self._preset_label(pid) + (" *" if pid in self._draft_specs else "")

    def _refresh_dirty_labels(self):
        for i in range(self.filters.count()):
            pid = self.filters.item(i).data(Qt.UserRole)
            self.filters.item(i).setText(self._filter_display_name(pid))
            row = self.preset.findData(pid)
            if row >= 0:
                with QSignalBlocker(self.preset):
                    self.preset.setItemText(row, self._strip_label(pid))
        self.setWindowModified(bool(self._draft_specs))
        self.keep_btn.setEnabled(self._active_pid in self._draft_specs)
        self.revert_btn.setEnabled(self._active_pid in self._draft_specs)
        self._update_pane_headers()

    def _load_filter_controls(self, pid):
        spec = self._spec_for(pid)
        self._loading_controls = True
        try:
            with ExitStack() as stack:
                for widget in (self.compression, self.stream_compression, self.brotli_declaration, self.strategy,
                               self.threshold_control, self.dpi, self.colors_control,
                               self.lossless_box, self.force_raster, self.page_size):
                    stack.enter_context(QSignalBlocker(widget))
                self.compression.setCurrentIndex(self.compression.findData(spec["mode"]))
                self.stream_compression.setCurrentIndex(self.stream_compression.findData(
                    spec.get("stream_compression", "flate")))
                self.brotli_declaration.setChecked(spec.get("brotli_declaration", False))
                self.strategy.setCurrentText(spec.get("strategy", "otsu"))
                self.threshold_control.setValue(spec.get("t", 180))
                dpi_field = "dpi" if spec["mode"] in BW_MODES else "dpi_cap"
                self.dpi.setCurrentIndex(self.dpi.findData(spec.get(dpi_field, 300)))
                self.colors_control.setValue(spec.get("colors", 64))
                self.force_raster.setChecked(spec.get("force_raster", False))
                self.lossless_box.setChecked(spec.get("lossless", False))
                self.page_size.setCurrentIndex(self.page_size.findData(spec.get("page_size", "original")))
                self._sync_filter_controls()
        finally:
            self._loading_controls = False
        self._refresh_details()

    def _controls_spec(self):
        spec = self._spec_for(self._active_pid)
        mode = self.compression.currentData()
        if mode != spec["mode"]:
            spec = with_algorithm(spec, mode)
        spec["stream_compression"] = self.stream_compression.currentData()
        spec["brotli_declaration"] = self.brotli_declaration.isChecked()
        if mode in BW_MODES:
            spec.update(strategy=self.strategy.currentText(), t=self.slider.value(),
                        dpi=self.dpi.currentData(), force_raster=self.force_raster.isChecked(),
                        page_size=self.page_size.currentData())
        else:
            spec["dpi_cap"] = self.dpi.currentData()
            spec.update(force_raster=self.force_raster.isChecked(), page_size=self.page_size.currentData())
            if mode == "jpx":
                spec["lossless"] = self.lossless_box.isChecked()
            elif mode in PALETTE_MODES:
                spec["colors"] = self.colors.value()
        return spec

    def _filter_edited(self, *_):
        if self._loading_controls or self._switching_filter or self._active_pid is None:
            return
        pid = self._active_pid
        before = self._spec_for(pid)
        algorithm_changed = before["mode"] != self.compression.currentData()
        # Fixed/disabled controls show the PREVIOUS codec's state. Do not
        # accidentally seed JPX losslessness or palette count from that chrome.
        spec = (with_algorithm(before, self.compression.currentData())
                if algorithm_changed else self._controls_spec())
        if spec_key(before) == spec_key(spec):
            return  # disabled/irrelevant controls do not create false edits
        if spec_key(spec) == spec_key(self._saved_specs[pid]):
            self._draft_specs.pop(pid, None)
        else:
            self._draft_specs[pid] = spec
        if algorithm_changed:
            self._load_filter_controls(pid)
        else:
            self._sync_filter_controls()
        self._refresh_details()
        self._refresh_dirty_labels()
        self._filter_prog[pid] = 0.0
        self._paint_strip_item(pid)
        if self._try_apply_cached():
            self._reframe_one(pid)
        else:
            self._preview_timer.start()
            self.status.setText("Filter changed — processing after debounce…")
        self._collect_artifacts()

    def _restore_selection(self, pid):
        with QSignalBlocker(self.preset), QSignalBlocker(self.filters):
            self.preset.setCurrentIndex(self.preset.findData(pid))
            for row in range(self.filters.count()):
                if self.filters.item(row).data(Qt.UserRole) == pid:
                    self.filters.setCurrentRow(row)
                    break

    def _make_unsaved_dialog(self, pid):
        box = QMessageBox(QMessageBox.Warning, "Unsaved filter changes",
                          f"Save changes to ‘{self._preset_label(pid)}’?", parent=self)
        box.setInformativeText("Save updates this filter. Save As creates and selects a new named filter. "
                               "Discard Changes restores the saved filter. No input PDF is changed.")
        box.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        box.button(QMessageBox.Discard).setText("Discard Changes")
        save_as = box.addButton("Save As…", QMessageBox.AcceptRole)
        box.setDefaultButton(QMessageBox.Save)
        box.setEscapeButton(QMessageBox.Cancel)
        return box, save_as

    def _ask_unsaved_filter(self, pid):
        box, save_as = self._make_unsaved_dialog(pid)
        box.exec()
        if box.clickedButton() == save_as:
            return "save_as"
        return {QMessageBox.Save: "save", QMessageBox.Discard: "discard"}.get(
            box.standardButton(box.clickedButton()), "cancel")

    def _resolve_unsaved_filter(self, pid):
        if pid not in self._draft_specs:
            return _FilterResolution(True)
        self._restore_selection(pid)
        choice = self._ask_unsaved_filter(pid)
        if choice == "save":
            self._save_filter_pid(pid)
            return _FilterResolution(True)
        if choice == "save_as":
            created = self._save_as_filter(pid)
            return _FilterResolution(created is not None, created)
        if choice == "discard":
            self._discard_filter(pid)
            return _FilterResolution(True)
        return _FilterResolution(False)

    def _persist_filter(self, entry):
        store = self._custom_store()
        customs = [c for c in (store.value("customPresets", []) or [])
                   if isinstance(c, dict) and c.get("id") != entry["id"]]
        customs.append(entry)
        store.setValue("customPresets", customs)
        store.sync()

    def _save_filter_pid(self, pid):
        spec = self._spec_for(pid)
        p = presets.get(pid)
        params = recipe_params(p, spec)
        self._persist_filter(dict(p, mode=spec["mode"], params=params))  # UUID survives Save
        p.update(mode=spec["mode"], params=params)
        self._saved_specs[pid] = spec
        self._draft_specs.pop(pid, None)
        self._preview_timer.stop()
        self._refresh_dirty_labels()
        self._dispatch_filters()  # only a not-yet-submitted debounced edit needs work
        self._collect_artifacts()
        log.info("filter saved without invalidating result: %s", pid)

    def _discard_filter(self, pid):
        self._preview_timer.stop()
        self._draft_specs.pop(pid, None)
        if pid == self._active_pid:
            self._load_filter_controls(pid)
        self._reframe_one(pid)
        self._refresh_dirty_labels()
        self._try_apply_cached()
        self._collect_artifacts()
        log.info("filter draft discarded, saved result kept: %s", pid)

    def revert_filter(self):
        """Explicitly discard only the active draft, reusing its saved result."""
        if self._active_pid in self._draft_specs:
            self._discard_filter(self._active_pid)

    def _save_as_filter(self, pid):
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Save filter as", "Name for the new filter:",
                                       text=f"{self._preset_label(pid)} copy")
        name = name.strip()
        if not ok or not name:
            return None
        uid = new_filter_uuid(p.get("uuid") for p in presets.PRESETS)
        nid = uid  # new filters no longer derive internal aliases from editable names
        source_key = self._result_key(pid) if self.doc is not None else None
        src, spec = presets.get(pid), self._spec_for(pid)
        entry = {"id": nid, "uuid": uid, "label": name, "mode": spec["mode"],
                 "params": recipe_params(src, spec), "blurb": f"copy of {src['label']}"}
        self._persist_filter(entry)
        presets.PRESETS.append(entry)
        self._saved_specs[nid] = spec
        item = QListWidgetItem(name)
        item.setData(Qt.UserRole, nid)
        item.setData(FILTER_UUID_ROLE, uid)
        item.setToolTip(entry["blurb"])
        item.setSizeHint(QSize(*STRIP_ICON))
        self.filters.addItem(item)
        if source_key is not None and (source_key in self._artifacts.results
                or source_key in self._artifacts.pending
                or source_key in self._artifacts.copy_sources):
            self._artifacts.copy_from(source_key, self._result_key(nid))
        self._draft_specs.pop(pid, None)
        self._preview_timer.stop()
        self._rebuild_preset_combo()
        self._refresh_dirty_labels()
        self._dispatch_filters()
        self._reframe_one(pid)
        self._reframe_one(nid)
        self._collect_artifacts()
        log.info("filter saved as: %s -> %s, both saved results kept", pid, nid)
        return nid

    def rename_filter(self):
        """Rename the current filter via naming popup (designer §109)."""
        from PySide6.QtWidgets import QInputDialog as _QD
        pid = self.preset.itemData(self.preset.currentIndex())
        if not pid:
            return
        name, ok = _QD.getText(self, "Rename filter",
                               f"New name for '{self._preset_label(pid)}':",
                               text=self._preset_label(pid))
        name = name.strip()
        if not ok or not name:
            return
        store = self._custom_store()
        renames = store.value("customRenames", {}) or {}
        renames[pid] = name
        store.setValue("customRenames", renames)
        presets.get(pid)["label"] = name
        self.preset.setItemText(self.preset.currentIndex(), self._strip_label(pid))
        _fit_combo(self.preset)
        self._repaint_all_strip()
        self._update_pane_headers()
        log.info("filter renamed: %s -> %s", pid, name)

    def copy_filter(self):
        """Save As… keeps the original saved recipe and current live result."""
        nid = self._save_as_filter(self._active_pid)
        if nid is not None:
            self._activate_filter(nid, reveal=True)

    def save_filter(self):
        """Promote the live recipe/result; never invalidate completed work."""
        if self._active_pid is not None:
            self._save_filter_pid(self._active_pid)

    def _sync_filter_controls(self):
        """§§65/67/85/100/203: T feeds Simple; Colors feeds both palette codecs;
        Lossless is a choice ONLY for JPEG2000. Raster DPI feeds every mode
        (§85: the single DPI) so it stays enabled.

        Controls without a choice stay visible but grey, showing the correct
        fixed state (§100) — and live controls that change nothing stay
        disabled (this also stops pointless identical-output jobs). §251's
        Brotli declaration compatibility checkbox is the explicit exception:
        hide it entirely for other compressors."""
        pid = self._active_pid or self.preset.currentData()
        mode = self._spec_for(pid)["mode"]
        bw = mode in BW_MODES
        t_on = bw and self.strategy.currentText() == "simple"
        self.threshold_control.setEnabled(t_on)
        self.t_label.setEnabled(t_on)
        self.t_label.setToolTip("Fixed threshold — only the Simple strategy uses it."
                                if t_on else "Fixed threshold — only the Simple strategy uses it "
                                "(Otsu/adaptive/Sauvola are automatic).")
        self.threshold_control.setToolTip(self.t_label.toolTip())
        c_on = mode in PALETTE_MODES
        self.colors_control.setEnabled(c_on)
        self.c_label.setEnabled(c_on)
        self.dpi.setEnabled(True)
        self.dpi.setToolTip("The single DPI: every image in the document (§85).")
        if mode == "jpx":
            self.lossless_box.setEnabled(True)
        else:
            # Fixed state per mode (§100): BW/indexed/passthrough are always
            # lossless; baseline JPEG never is.
            fixed = bw or mode in PALETTE_MODES or mode == "passthrough"
            if self.lossless_box.isChecked() != fixed:
                with QSignalBlocker(self.lossless_box):
                    self.lossless_box.setChecked(fixed)
            self.lossless_box.setEnabled(False)
        self.strategy.setEnabled(bw)
        self.strategy_label.setEnabled(bw)
        self.force_raster.setEnabled(mode in ALGORITHM_LABELS)
        self.page_size.setEnabled(mode in ALGORITHM_LABELS and self.force_raster.isChecked())
        brotli = self._spec_for(pid).get("stream_compression") == "brotli"
        self.brotli_declaration.setVisible(brotli)
        self.stream_warning.setVisible(brotli)

    def _sync_threshold_enabled(self):
        self._sync_filter_controls()

    def _refresh_file_box(self):
        """Main File info box: full path, pages, page size, original size.

        Everything constant for the original and every filter (§§69/73).
        Page size here is display-only info: saving reshapes nothing unless
        the designer picks Letter/A4 (§74). Absurd scan sizes get a warning
        line suggesting Letter — never auto-applied.
        """
        if not self.doc or not self.path:
            text = "No file"
        else:
            rects = [(p.rect.width, p.rect.height) for p in self.doc]
            from ..core.pipeline import absurd_pages
            bad = absurd_pages(rects)
            if self._orig_bytes:
                text = (f"{os.path.abspath(self.path)}\n"
                        f"{self.doc.page_count} pages · "
                        f"{presets.PAGE_SIZE_LABELS[self.page_size.currentData()]} · "
                        f"{fmt_bytes(self._orig_bytes)} (100%)")
            else:
                text = os.path.abspath(self.path)
            if bad:
                shown = ", ".join(f"p{i + 1} {rects[i][0]:.0f}×{rects[i][1]:.0f}pt"
                                  for i in bad[:3])
                if len(bad) > 3:
                    shown += f" +{len(bad) - 3} more"
                text += f"\n⚠ odd page size ({shown}) — consider Letter on Save"
                log.warning("absurd page size on %s: %s", self.path, shown)
        if self.file_label.text() != text:
            self.file_label.setText(text)

    def _refresh_details(self):
        """Right-panel readout of the active filter's full recipe (§§54/82).

        Stable sequence in every mode: Codec first (exactly one per filter),
        then the common properties, then codec-specific options last.
        """
        pid = self.preset.itemData(self.preset.currentIndex())
        if not pid:
            return
        spec = self._spec_for(pid)
        mode = spec["mode"]
        if mode in BW_MODES:
            method = self.strategy.currentText()
            threshold = (f"simple · T={self.slider.value()}" if method == "simple"
                         else f"{method} (automatic)")
            lines = [
                f"Codec: {ALGORITHM_LABELS[mode]}",
                f"Threshold method: {threshold}",
                f"Render: {self.dpi.currentData()} dpi · "
                f"{'full-page raster' if self.force_raster.isChecked() else 'text/vectors kept · BW image canvas'}",
            ]
        elif mode == "color":
            lines = [
                "Codec: JPEG",
                f"Quality: q={spec['jpeg_q']} · {self.dpi.currentData()}dpi",
                "Full-page raster" if spec.get("force_raster") else "Text/vectors kept · color image canvas",
            ]
        elif mode == "jpx":
            lines = [
                "Codec: JPEG2000",
                ("Lossless" if self.lossless_box.isChecked() else
                 f"Rate: r={spec.get('rate', 192)}") + f" · {self.dpi.currentData()}dpi",
                "Full-page raster" if spec.get("force_raster") else "Text/vectors kept · color image canvas",
            ]
        elif mode in PALETTE_MODES:
            lines = [
                f"Codec: {ALGORITHM_LABELS[mode]}",
                f"Colors: {self.colors.value()} (auto algorithm, no dither)",
                "Full-page raster" if spec.get("force_raster") else "Text/vectors kept · color image canvas",
            ]
        else:
            lines = [
                "Codec: none (passthrough)",
                "gc + deflate only — pixels unchanged",
            ]
        lines.append("PDF streams: " + STREAM_LABELS[spec.get("stream_compression", "flate")])
        if spec.get("stream_compression") == "brotli":
            lines.append("Brotli extension declaration: " +
                         ("On (Compatibility)" if spec.get("brotli_declaration", False) else "Off"))
        self.details.setText("\n".join(lines))
        for _cb in (self.preset, self.strategy, self.dpi, self.page_size):
            _cur = _cb.itemText(_cb.currentIndex())
            if _cur:
                _cb.setToolTip(_cur)  # hover always shows the full text (§130)

    @property
    def _strip_ids(self):
        """Derived view of model order, never a second mutable position array."""
        return [self.filters.item(i).data(Qt.UserRole) for i in range(self.filters.count())]

    def _apply_strip_order(self, ids):
        """Apply the persisted strip order, if any (§128): known ids in the
        saved sequence first, then anything new in preset order."""
        try:
            saved = self._custom_store().value("stripOrder", []) or []
        except Exception:  # noqa: BLE001
            saved = []
        if not saved:
            return ids
        known = list(dict.fromkeys(i for i in saved if i in ids))
        return known + [i for i in ids if i not in known]

    def _strip_label(self, pid: str) -> str:
        """Filter label with its sequence number (§133): minis and dropdown
        both read `N. label` from the live strip order."""
        try:
            return _numbered_filter_label(self._strip_ids.index(pid),
                                          self._filter_display_name(pid))
        except (ValueError, KeyError):
            return presets.get(pid)["label"]

    def _rebuild_preset_combo(self):
        """Dropdown follows the strip order (§§128/140): real filters only.
        Original is NOT an option — it is always the left preview (§140) —
        so no passthrough entry exists here; selection preserved by id."""
        cur = self.preset.itemData(self.preset.currentIndex())
        self.preset.blockSignals(True)
        try:
            self.preset.clear()
            for pid in self._strip_ids:
                self.preset.addItem(self._strip_label(pid), pid)
            _fit_combo(self.preset)
            idx = self.preset.findData(cur)
            self.preset.setCurrentIndex(idx if idx >= 0 else 0)
        finally:
            self.preset.blockSignals(False)

    def _restrip_ordered(self, *args):
        """Strip rows were drag-reordered (§128): adopt the visual order,
        sync the dropdown, persist. The delegate numbers from the live model
        row (§148); cached content is id-keyed and has no positional text.
        No icon rebuild or processing — order only changes submission sequence.
        """
        order = self._strip_ids
        if not order:
            return
        self._rebuild_preset_combo()
        try:
            self._custom_store().setValue("stripOrder", order)
        except Exception:  # noqa: BLE001
            pass
        log.info("strip reordered: %s", order)

    def _ordered_pids(self) -> list:
        """Processing sequence (§128): strip order, except the selected
        filter always goes first regardless of position."""
        active = self.preset.itemData(self.preset.currentIndex())
        rest = [p for p in self._strip_ids if p != active]
        return ([active] + rest) if active in self._strip_ids else rest

    def _preset_chosen(self, idx: int):
        pid = self.preset.itemData(idx)
        if self._switching_filter:
            return
        if pid is None:
            self._restore_selection(self._active_pid)
            return
        previous = self._active_pid
        self._switching_filter = True
        try:
            resolution = (self._resolve_unsaved_filter(previous)
                          if pid != previous else _FilterResolution(True))
            if not resolution.allowed:
                self._restore_selection(previous)
                return
            self._activate_filter(resolution.created_pid or pid,
                                  reveal=resolution.created_pid is not None)
        finally:
            self._switching_filter = False

    def _activate_filter(self, pid, *, reveal=False):
        """One selection/control/preview commit; never starts filtering."""
        self._active_pid = pid
        self._restore_selection(pid)
        if reveal:
            # A new copy needs revealing. Native mouse/keyboard activation
            # already owns scrolling; do not move its source during a press.
            self.filters.scrollToItem(self.filters.currentItem())
        self._load_filter_controls(pid)
        self._refresh_dirty_labels()
        log.info("preset selected (view only): %s", pid)
        if not self._try_apply_cached():
            self.save_act.setEnabled(False)
            self.status.setText("Waiting for the queued filter result…")

    def _filterstrip_chosen(self, row: int):
        if self._switching_filter or row < 0 or row >= self.filters.count():
            return
        pid = self.filters.item(row).data(Qt.UserRole)
        idx = self.preset.findData(pid)
        if idx >= 0 and self.preset.currentIndex() != idx:
            self.preset.setCurrentIndex(idx)
        else:
            self._try_apply_cached()
            self._update_pane_headers()

    def set_main_mode(self, mode: str):
        log.info("view main mode: %s", mode)
        for m, a in self._main_actions.items():
            a.setChecked(m == mode)
        # §107: fixed equal layout, no splitter — direction only.
        if mode == "side-h":
            self.panes.setDirection(QBoxLayout.LeftToRight)
            self.before.show()
            self.after.show()
        elif mode == "stack-v":
            self.panes.setDirection(QBoxLayout.TopToBottom)
            self.before.show()
            self.after.show()
        else:  # single: preview only, maximized
            self.panes.setDirection(QBoxLayout.LeftToRight)
            self.before.hide()
            self.after.show()
        self._main_mode = mode

    def set_filter_mode(self, mode: str):
        log.info("view filter mode: %s", mode)
        for m, a in self._filter_actions.items():
            a.setChecked(m == mode)
        if mode == "film-h":
            self.filters.setFlow(QListWidget.LeftToRight)
        elif mode == "rail-v":
            self.filters.setFlow(QListWidget.TopToBottom)
            self.filters.setMaximumHeight(16777215)
        else:  # grid
            self.filters.setFlow(QListWidget.LeftToRight)
            self.filters.setMaximumHeight(16777215)
            self.filters.setWrapping(True)
            return
        self.filters.setWrapping(False)
        self.filters._sync_row_height()

    # --- DnD / open ---
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        for u in e.mimeData().urls():
            p = u.toLocalFile()
            if p.lower().endswith(".pdf"):
                log.info("dnd opened: %s", p)
                self.open_file(p)
                return

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.cancel()
        elif e.key() == Qt.Key_PageDown:
            self.before.goto_page(self.before.current_page + 1)
        elif e.key() == Qt.Key_PageUp:
            self.before.goto_page(self.before.current_page - 1)
        elif e.modifiers() & Qt.ControlModifier and e.key() in (
                Qt.Key_Plus, Qt.Key_Equal, Qt.Key_Minus, Qt.Key_0):
            # §52: modern standard keyboard zoom — Ctrl+Plus in, Ctrl+Minus
            # out, Ctrl+0 fit. (Plus and Equal share the = key on US layouts.)
            self._keyboard_zoom(e.key())
        else:
            super().keyPressEvent(e)

    def _button_zoom(self, factor: float):
        """Right-panel zoom buttons (§71): same step as Ctrl+Plus/Minus."""
        if not self.doc:
            return
        self.before.set_zoom(self.before._zoom * factor)
        log.info("zoom button factor=%.2f", factor)

    def _keyboard_zoom(self, key):
        """Apply one keyboard-zoom step to the synced panes (§52)."""
        if not self.doc:
            return
        if key in (Qt.Key_Plus, Qt.Key_Equal):
            self.before.set_zoom(self.before._zoom * 1.25)
            log.info("keyboard zoom in (Ctrl+Plus)")
        elif key == Qt.Key_Minus:
            self.before.set_zoom(self.before._zoom / 1.25)
            log.info("keyboard zoom out (Ctrl+Minus)")
        elif key == Qt.Key_0:
            self.before.fit_width()
            log.info("keyboard zoom reset (Ctrl+0)")

    def open_dialog(self):
        p, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF (*.pdf)")
        if p:
            self.open_file(p)

    def open_file(self, path: str):
        candidate = None
        try:
            candidate = fitz.open(path)
            resolution = self._resolve_unsaved_filter(self._active_pid)
            if not resolution.allowed:
                candidate.close()
                return
            if resolution.created_pid is not None:
                self._activate_filter(resolution.created_pid, reveal=True)
            if self.doc is not None:
                self.doc.close()
            self.before.clear_pdf_source()
            self.after.clear_pdf_source()
            self.doc, candidate = candidate, None
            self.path = path
            self._preview_timer.stop()
            self._draft_specs.clear()
            self._mini_view.clear()
            self._mini_amount.clear()
            self._filter_prog.clear()
            self._shown_preview_key = None
            self._collect_artifacts()
            self._custom_store().setValue("lastFile", os.path.abspath(path))
            self._orig_bytes = os.path.getsize(path)
            self._refresh_file_box()
            self._refresh_dirty_labels()
            for pid in self._strip_ids:
                self._filter_prog[pid] = 0.0
            self._repaint_all_strip()
            self._render_all()
            self.before.goto_page(0)
            self.page_label.setText(f"Page 1 of {self.doc.page_count} (PgUp/PgDn)")
            log.info("opened %s pages=%d", path, self.doc.page_count)
        except Exception as exc:
            if candidate is not None:
                candidate.close()
            log.exception("open failed %s", path)
            QMessageBox.warning(self, "Open failed", str(exc))

    # --- continuous render ---
    def _render_page_rgb(self, i: int, dpi: int = PREVIEW_DPI) -> np.ndarray:
        pix = render_display_page(self.doc[i], dpi=dpi)
        return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3).copy()

    def _render_all(self):
        """Baseline panes (fast sync renders) + background filter job."""
        if not self.doc:
            return
        t0 = time.perf_counter()
        n = self.doc.page_count
        base = [rgb_to_qimage(self._render_page_rgb(i)) for i in range(n)]
        self.before.set_pages(base, pdf_path=self.path)
        log.info("baseline rendered %d pages in %.0fms", n, (time.perf_counter() - t0) * 1000)
        # §111: the right pane never sits empty — baseline now, real preview
        # the moment it lands (tracked by _shown_preview_key).
        self._applying = True
        self.after._syncing = True
        try:
            self.after.set_pages(base, pdf_path=self.path)
            self.after.setTransform(self.before.transform())
            self.after._zoom = self.before._zoom
            self.after.relayout()
        finally:
            self.after._syncing = False
            self._applying = False
        self._shown_preview_key = None
        self._dispatch_filters()

    def _active_spec(self) -> dict:
        spec = self._spec_for(self._active_pid)
        spec["preset_id"] = self._active_pid
        return spec

    def _file_key(self):
        """Identity for process-once results: path + mtime + size."""
        if not self.path:
            return None
        try:
            st = os.stat(self.path)
            return (os.path.abspath(self.path), st.st_mtime_ns, st.st_size)
        except OSError:
            return (os.path.abspath(self.path),)

    @staticmethod
    def _spec_tuple(spec: dict):
        return spec_key(spec)

    def _result_key(self, pid, saved=False):
        spec = self._saved_specs[pid] if saved else self._spec_for(pid)
        return self._artifacts.key(self._file_key(), spec, presets.get(pid)["uuid"])

    def _collect_artifacts(self):
        wanted = set(self._export_keys)
        if self.doc is not None:
            # The previous ready draft can remain visible while its newer
            # edit is preparing. Keep its native source file alive until the
            # view releases it, not merely until the recipe changes.
            if self._shown_preview_key is not None:
                wanted.add(self._shown_preview_key)
            for pid in self._strip_ids:
                wanted.add(self._result_key(pid, saved=True))
                if pid in self._draft_specs:
                    wanted.add(self._result_key(pid))
        self._artifacts.retain(wanted)

    def _repaint_all_strip(self):
        for pid in self._strip_ids:
            self._paint_strip_item(pid)

    def _apply_preview_pages(self, pages, source: str, key=None, pdf_path=None):
        """Show preview pages in the right pane, preserving scroll/zoom.

        Skips the rebuild entirely when these exact pages are already shown
        (§108): re-setting identical pixmaps only produces flicker that reads
        as recomputation.
        """
        if not self.doc:
            return
        if key is not None and key == self._shown_preview_key:
            log.info("preview kept (already showing %s)", source)
            return
        keep_h = self.after.horizontalScrollBar().value()
        keep_v = self.after.verticalScrollBar().value()
        self._applying = True
        self.after._syncing = True
        try:
            self.after.set_pages([rgb_to_qimage(a) for a in pages], pdf_path=pdf_path)
            self.after.setTransform(self.before.transform())
            self.after._zoom = self.before._zoom
            self.after.relayout()
            self.after.horizontalScrollBar().setValue(keep_h)
            self.after.verticalScrollBar().setValue(keep_v)
        finally:
            self.after._syncing = False
            self._applying = False
        if key is not None:
            self._shown_preview_key = key
        self.status.setText(f"{os.path.basename(self.path)} — {self.doc.page_count} pages ({source})")
        log.info("preview applied from %s (%d pages)", source, len(pages))

    def _try_apply_cached(self) -> bool:
        """Selection consumes a prepared real-file result; never dispatches."""
        if self.doc is None or self._active_pid is None:
            return False
        key = self._result_key(self._active_pid)
        artifact = self._artifacts.results.get(key)
        self.save_act.setEnabled(artifact is not None and
                                 (self.worker is None or self.worker.isFinished()))
        if artifact is None:
            return False
        self._preview_timer.stop()
        self._apply_preview_pages(artifact.pages, "filtered file", key,
                                  pdf_path=artifact.pdf_path)
        return True

    def _dispatch_filters(self):
        """Queue each missing saved/draft recipe once, selected filter first."""
        if self.doc is None or self.path is None or self._closing_requested:
            return
        self._preview_timer.stop()
        self._collect_artifacts()
        executor = filter_pool()  # construct the spawn pool in the GUI thread
        started = 0
        for pid in self._ordered_pids():
            recipes = [self._spec_for(pid)]
            if pid in self._draft_specs:
                recipes.append(self._saved_specs[pid])
            for spec in recipes:
                key = self._artifacts.key(self._file_key(), spec, presets.get(pid)["uuid"])
                worker = self._artifacts.start(key, self.path, spec, executor)
                if worker is None:
                    continue
                self._attach_artifact_worker(key, worker, pid)
                started += not worker.is_copy
                log.info("%s queued: %s UUID=%s spec=%s",
                         "prepared file copy" if worker.is_copy else "real filter",
                         pid, presets.get(pid)["uuid"], spec)
        if started:
            self._gen += 1
            self.status.setText("Processing filtered files…")
        self._reframe_minis()
        self._try_apply_cached()
        self._settle_status()

    def _attach_artifact_worker(self, key, worker, pid):
        worker.ready.connect(lambda result, k=key: self._artifact_ready(k, result))
        worker.failed.connect(lambda message, k=key: self._artifact_failed(k, message))
        worker.progressed.connect(lambda value, k=key: self._artifact_progress(k, value))
        worker.finished.connect(lambda k=key, job=worker: self._artifact_finished(k, job))
        self._jobs.add(worker)
        self._filter_prog[pid] = 0.0
        self._paint_strip_item(pid)
        worker.start()

    def _queue_ready_copies(self):
        if self.doc is None or self._closing_requested:
            return
        for key in list(self._artifacts.copy_sources):
            worker = self._artifacts.start_copy(key, filter_pool())
            if worker is not None:
                pid = next(p for p in self._strip_ids if presets.get(p)["uuid"] == key[0])
                self._attach_artifact_worker(key, worker, pid)
                log.info("prepared file copy queued: UUID=%s", key[0])

    def _on_view_changed(self):
        """Any scroll/pan/zoom/layout change: reframe minis, debounced (§47)."""
        self._update_zoom_control()
        self._reframe_timer.start()

    def _zoom_combo_chosen(self, *args):
        """Preset picked or number typed in the zoom combo (§86)."""
        if not self.doc:
            return
        if args and isinstance(args[0], int) and not isinstance(args[0], bool):
            factor = self.zoom_combo.itemData(args[0]) or 1.0
        else:
            text = self.zoom_combo.currentText().strip().rstrip("%").strip()
            try:
                factor = float(text) / 100
            except ValueError:
                self._update_zoom_control()
                return
            factor = min(8.0, max(0.1, factor))
        self.before.set_zoom(factor)
        log.info("zoom combo -> %.0f%%", factor * 100)

    def _update_zoom_control(self):
        """Live zoom % in the combo, following every view change (§§85/86)."""
        text = "—" if not self.doc else f"{self.before._zoom * 100:.0f}%"
        if self.zoom_combo.currentText() != text:
            blocked = self.zoom_combo.blockSignals(True)
            self.zoom_combo.setCurrentText(text)
            self.zoom_combo.blockSignals(blocked)

    def _current_view(self):
        """Framing both panes share: layout dims + visible scene rect."""
        cols = self.before.cols()
        pw = self.before._page_w()
        ph = self.before._page_h()
        vis = self.before.mapToScene(self.before.viewport().rect()).boundingRect()
        return cols, pw, ph, (vis.x(), vis.y(), vis.width(), vis.height())

    def _sized(self, nbytes: int) -> str:
        """Real amount with % of the original file (designer §§61/65: rounded)."""
        text = fmt_bytes(nbytes)
        if self._orig_bytes:
            text += f" ({nbytes / self._orig_bytes * 100:.0f}%)"
        return text

    def _update_pane_headers(self):
        """Key facts above each main pane (designer §60).

        Left mirrors the strip-thumbnail style (name + info, incl. the real
        file size at 100%); right names the active filter with its recipe and
        real total + % — exactly as its strip caption reads.
        """
        if not self.doc or not self.path:
            left, right = "Original — no document", "Preview — no document"
        else:
            fs = fmt_bytes(self._orig_bytes) if self._orig_bytes else "?"
            n = self.doc.page_count
            left = f"Original · {fs} · 100% · {n} pages"
            pid = self._active_pid
            size = self._mini_amount.get(pid)
            right = f"{self._filter_display_name(pid)} · {_preset_algo(pid, self._spec_for(pid))}"
            if size:
                right += f" · {size}"
        self.beforeHeader.setText(left)
        self.afterHeader.setText(right)

    def _reframe_minis(self):
        """§48: repaint every mini as the current view through its own filter.

        Pure view work from cached per-preset pages — never a job, so this
        is what scroll/pan/zoom/page changes call (§47).
        """
        if not self.doc or not self.path:
            return
        for pid in self._strip_ids:
            self._reframe_one(pid)

    def _reframe_one(self, pid: str):
        if self.doc is None or not self.path:
            return
        key = self._result_key(pid)
        artifact = self._artifacts.results.get(key)
        if artifact is not None:
            self._mini_amount[pid] = self._sized(artifact.nbytes)
            cols, pw, ph, vis = self._current_view()
            self._mini_view[pid] = frame_view(
                artifact.mini_pages, pw, ph, ContinuousDocView.GAP, cols, vis)
            self._filter_prog[pid] = 1.0
        self._paint_strip_item(pid)

    def _settle_status(self):
        if self.doc is None or self.path is None:
            return
        failed = self._artifacts.errors.get(self._result_key(self._active_pid))
        if failed is not None:
            self.status.setText(f"Filter processing failed: {failed}")
            return
        wanted = {self._result_key(pid) for pid in self._strip_ids}
        complete = sum(key in self._artifacts.results for key in wanted)
        self.progress.setMaximum(max(1, len(wanted)))
        self.progress.setValue(complete)
        if wanted <= self._artifacts.results.keys():
            self.status.setText(f"{os.path.basename(self.path)} — {self.doc.page_count} pages")

    def _paint_strip_item(self, pid: str):
        if pid not in self._strip_ids:
            return
        prog = float(self._filter_prog.get(pid, 0.0))
        arr = self._mini_view.get(pid)
        # §195: the progress control already signals work. Only real amount
        # metadata belongs here; keep it visible while a new draft is pending.
        amount = self._mini_amount.get(pid, "")
        pal = self.palette()
        icon = QPixmap(*STRIP_ICON)
        # Stable filter content only. The shared delegate owns the ground,
        # selection, and position-dependent caption (§148).
        icon.fill(Qt.transparent)
        pt = QPainter(icon)
        box = STRIP_PREVIEW_RECT  # mini placement, not a drawn frame
        if arr is not None:
            q = gray_to_qimage(arr) if arr.ndim == 2 else rgb_to_qimage(arr)
            mini = QPixmap.fromImage(q).scaled(box.size(), Qt.KeepAspectRatio,
                                               Qt.FastTransformation)
            pt.drawPixmap(box.x() + (box.width() - mini.width()) // 2,
                          box.y() + (box.height() - mini.height()) // 2, mini)
        small = QFont(pt.font())
        small.setPointSize(max(7, small.pointSize() - 2))
        pt.setFont(small)
        # §§134/136: caption ink is always the theme window text (dark on
        # both white and the light-blue selection) — HighlightedText
        # rendered near-unreadable pale-on-pale, retired.
        pt.setPen(QPen(pal.color(QPalette.WindowText), 1))
        # Recipe/amount belong to this filter; numbered name is delegate-drawn.
        pt.drawText(STRIP_ALGO_RECT, Qt.AlignHCenter, _preset_algo(pid, self._spec_for(pid)))
        pt.drawText(STRIP_AMOUNT_RECT, Qt.AlignHCenter, amount)
        pt.end()
        item = self.filters.item_for_uuid(presets.get(pid)["uuid"])
        item.setData(FILTER_PROGRESS_ROLE, prog)
        item.setText(self._filter_display_name(pid))
        item.setIcon(QIcon(icon))

    def _artifact_ready(self, key, artifact):
        if not self._artifacts.complete(key, artifact):
            return
        self._queue_ready_copies()
        for pid in self._strip_ids:
            if self.doc is not None and self._result_key(pid) == key:
                self._reframe_one(pid)
        if self.doc is not None and self._result_key(self._active_pid) == key:
            self._try_apply_cached()
        self._update_pane_headers()
        self._collect_artifacts()
        self._settle_status()
        log.info("real filter ready: %s bytes=%d pages=%d",
                 artifact.pdf_path, artifact.nbytes, len(artifact.page_paths))

    def _artifact_progress(self, key, value):
        if self.doc is None:
            return
        for pid in self._strip_ids:
            if self._result_key(pid) == key and key not in self._artifacts.results:
                self._filter_prog[pid] = value
                self._paint_strip_item(pid)

    def _artifact_failed(self, key, message):
        if key not in self._artifacts.retired and message != "Cancelled":
            self._artifacts.fail(key, message)
            log.warning("real filter failed: %s: %s", key, message)
            self._settle_status()

    def _artifact_finished(self, key, job):
        self._jobs.discard(job)
        self._artifacts.finish(key)
        self._collect_artifacts()
        self._settle_status()
        if self._closing_requested and not self._jobs:
            QTimer.singleShot(0, self.close)

    def _on_page_changed(self, idx: int):
        if not self.doc or getattr(self, "_applying", False):
            return
        self.page_label.setText(f"Page {idx + 1} of {self.doc.page_count} (PgUp/PgDn)")
        log.debug("current page %d", idx + 1)
        # §47: a page turn is a view change — reframe minis from cache only.
        self._reframe_minis()

    # --- run / cancel ---
    def save(self):
        """PDF export copies the completed artifact; it NEVER filters again."""
        if self.doc is None or self.worker is not None and not self.worker.isFinished():
            return
        key = self._result_key(self._active_pid)
        artifact = self._artifacts.results.get(key)
        if artifact is None:
            self.status.setText("Wait for this filter's real file before saving.")
            return
        stem, _ = os.path.splitext(self.path)
        out, _ = QFileDialog.getSaveFileName(
            self, "Save reduced PDF", stem + ".reduced.pdf", "PDF (*.pdf)")
        if not out:
            return
        if os.path.realpath(out) == os.path.realpath(self.path):
            QMessageBox.warning(self, "Refusing", "Won't overwrite input. Pick another name.")
            return
        self.token.reset()
        self._export_keys.add(key)
        job = CopyWorker(artifact.pdf_path, out, self.token)
        self.worker = job
        self._jobs.add(job)
        self.save_act.setEnabled(False)
        job.finished.connect(lambda: self._export_finished(key, job))
        job.done.connect(self._on_done)
        job.failed.connect(self._on_failed)
        job.progressed.connect(self._on_progress)
        job.start()
        self.cancel_act.setEnabled(True)
        self.status.setText("Saving filtered file… ESC to cancel")
        log.info("export copies exact artifact: %s -> %s bytes=%d",
                 artifact.pdf_path, out, artifact.nbytes)

    def _export_finished(self, key, job):
        self._jobs.discard(job)
        self._export_keys.discard(key)
        self._collect_artifacts()
        self._try_apply_cached()
        if self._closing_requested and not self._jobs:
            QTimer.singleShot(0, self.close)

    def _on_done(self, path: str):
        self.cancel_act.setEnabled(False)
        # §53: the exact size is known once saving completes — report it with
        # the saving against the input.
        try:
            out_n = os.path.getsize(path)
            in_n = os.path.getsize(self.path) if self.path else 0
            delta = f" (was {fmt_bytes(in_n)}, −{100 * (1 - out_n / in_n):.0f}%)" \
                if in_n else ""
        except OSError:
            out_n, delta = -1, ""
        if out_n >= 0:
            log.info("saved %s — %s%s", path, fmt_bytes(out_n), delta)
            self.status.setText(f"Saved {os.path.basename(path)} — {fmt_bytes(out_n)}{delta}")
        else:
            log.info("saved %s", path)
            self.status.setText(f"Saved {path}")

    def _on_failed(self, msg: str):
        self.cancel_act.setEnabled(False)
        log.info("job ended: %s", msg)
        self.status.setText(msg)

    def _on_progress(self, a: int, b: int):
        self.progress.setMaximum(b)
        self.progress.setValue(a)
        log.debug("progress page %d/%d", a, b)

    def cancel(self):
        # §85: Cancel stops a RUNNING save only — there is nothing to undo
        # (saves write a new file; the input is never touched). Quiet no-op
        # otherwise, so ESC never pretends to act.
        if self.worker is None or self.worker.isFinished():
            return
        log.info("cancel requested by designer (ESC/button)")
        self.token.cancel()
        self.status.setText("Cancelling…")

    def closeEvent(self, e):
        """Resolve edits, then cancel/join asynchronously; never destroy QThreads."""
        if not self._closing_requested:
            resolution = self._resolve_unsaved_filter(self._active_pid)
            if not resolution.allowed:
                e.ignore()
                return
            if resolution.created_pid is not None:
                self._activate_filter(resolution.created_pid, reveal=True)
            self._closing_requested = True
            self._preview_timer.stop()
            self._reframe_timer.stop()
            self.token.cancel()
            for worker in list(self._artifacts.pending.values()):
                worker.cancel()
        if self._jobs:
            e.ignore()
            self.status.setText("Closing — waiting for filter workers to stop safely…")
            return
        self.before.clear_pdf_source()
        self.after.clear_pdf_source()
        if self.doc is not None:
            self.doc.close()
            self.doc = None
        self._collect_artifacts()
        self._artifacts.close()
        super().closeEvent(e)


def main(start_pdf: str | None = None, debug: bool = False):
    log.info("starting %s debug=%s pdf=%s", APP_NAME, debug, start_pdf)
    if start_pdf is None:
        # §91: reopen the last file; fall back to the photo demo.
        last = app_settings().value("lastFile")
        if last and os.path.exists(last):
            start_pdf = last
            log.info("reopening last file %s", start_pdf)
        elif os.path.exists("examples/images.pdf"):
            start_pdf = "examples/images.pdf"
    if debug:
        try:
            from PySide6 import __version__ as pyside_v
        except Exception:  # noqa: BLE001
            pyside_v = "?"
        from PySide6.QtCore import qVersion
        log.debug("env python=%s pyside=%s qt=%s fitz=%s cwd=%s",
                  sys.version.split()[0], pyside_v, qVersion(),
                  getattr(fitz, "VersionBind", "?"), os.getcwd())
        log.debug("argv=%s", sys.argv)
        log.debug("filter workers<=%d (half cores cap)", cpu_cap())
    app = QApplication(sys.argv)
    configure_application(app)
    w = MainWindow(start_pdf)
    w.show()
    log.info("window shown")
    sys.exit(app.exec())
