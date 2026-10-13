"""Main window: continuous before/after panes, filter strip, ESC cancel."""
import logging
import os
import sys
import time
import numpy as np

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QListView, QLabel, QSlider, QComboBox, QProgressBar,
    QFileDialog, QMessageBox, QCheckBox, QScrollArea, QToolBar, QBoxLayout,
    QAbstractItemView, QStyledItemDelegate, QStyle, QSplitter,
)
from PySide6.QtCore import Qt, QThread, Signal, QSize, QTimer
from PySide6.QtGui import QImage, QIcon, QPixmap, QPainter, QFont, QPen, QAction, QColor, QPalette

from ..core.cancel import CancelToken
from ..core import pdf_io, threshold as T
from ..core import presets
from ..core.pipeline import process_file, recompress_file, gc_copy
from ..core.pdf_io import CancelledError
from .viewer import ContinuousDocView
from .jobs import FilterWorker, cpu_cap, pool as filter_pool, frame_view
from .lab import open_progress_lab, open_buttons_lab

import fitz

log = logging.getLogger("pdf_minimalist")

PREVIEW_DPI = 150


def setup_logging(debug: bool = False):
    """Stdout logging for run-and-review. INFO default; --debug => DEBUG + diagnostics."""
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s", "%H:%M:%S"))
    root = logging.getLogger("pdf_minimalist")
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


class _StripDelegate(QStyledItemDelegate):
    """Paints strip icons with zero Qt selection chrome (§§96-98).

    Some desktop styles paint selection/focus/hover backgrounds no stylesheet
    or focus policy suppresses. Clearing the states before the default paint
    leaves only our icons (plus our own painted ring) on every style.
    """

    def paint(self, painter, option, index):
        option.state &= ~(QStyle.State_Selected | QStyle.State_HasFocus
                           | QStyle.State_MouseOver | QStyle.State_Active)
        super().paint(painter, option, index)


def _zoom_icon(plus: bool) -> QIcon:
    """Crisp magnifier + / − icon drawn in code (designer §84).

    Desktop theme icons proved unreliable (missing or mismatched), so the
    zoom pair no longer depends on them: a 32px symbolic glyph in the
    window-text color, shown at 16px. Identical on every desktop.
    """
    from PySide6.QtWidgets import QApplication as _QA
    color = _QA.palette().windowText().color()
    s = 32
    pm = QPixmap(s, s)
    pm.fill(Qt.transparent)
    pt = QPainter(pm)
    pt.setRenderHint(QPainter.Antialiasing)
    pt.setPen(QPen(color, 3, Qt.SolidLine, Qt.RoundCap))
    pt.drawEllipse(4, 4, 18, 18)
    pt.drawLine(18, 18, 27, 27)
    pt.drawLine(8, 13, 18, 13)
    if plus:
        pt.drawLine(13, 8, 13, 18)
    pt.end()
    return QIcon(pm)


def _rename_icon() -> QIcon:
    """Pencil glyph drawn in code (designer §115).

    `edit-rename` is the freedesktop standard name, but themes ship it
    inconsistently — drawn wins everywhere, theme first where present.
    """
    found = QIcon.fromTheme("edit-rename")
    if not found.isNull():
        return found
    from PySide6.QtWidgets import QApplication as _QA
    color = _QA.palette().windowText().color()
    s = 32
    pm = QPixmap(s, s)
    pm.fill(Qt.transparent)
    pt = QPainter(pm)
    pt.setRenderHint(QPainter.Antialiasing)
    pt.setPen(QPen(color, 3, Qt.SolidLine, Qt.RoundCap))
    pt.drawLine(8, 24, 13, 19)
    pt.drawLine(13, 19, 23, 9)
    pt.drawLine(23, 9, 25, 7)
    pt.drawLine(20, 22, 24, 18)
    pt.end()
    return QIcon(pm)


def _copy_icon() -> QIcon:
    """Overlapping-rects copy glyph, same policy as `_rename_icon`."""
    found = QIcon.fromTheme("edit-copy")
    if not found.isNull():
        return found
    from PySide6.QtWidgets import QApplication as _QA
    color = _QA.palette().windowText().color()
    s = 32
    pm = QPixmap(s, s)
    pm.fill(Qt.transparent)
    pt = QPainter(pm)
    pt.setRenderHint(QPainter.Antialiasing)
    pen = QPen(color, 3)
    pen.setStyle(Qt.SolidLine)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    pt.setPen(pen)
    pt.drawRect(12, 12, 13, 13)
    pt.drawRect(7, 7, 13, 13)
    pt.end()
    return QIcon(pm)


def _preset_algo(pid: str) -> str:
    """One-line filter recipe for the strip caption (§53): the image
    algorithm each mini was rendered with — threshold strategy (+T for the
    fixed-threshold filter), render DPI and encoder for BW; JPEG quality and
    DPI cap for color."""
    p = presets.get(pid)
    prm = p["params"]
    if p["mode"] == "bw":
        base = f"{prm['strategy']} T{prm['t']}" if prm["strategy"] == "simple" \
            else prm["strategy"]
        return f"{base} · {prm['dpi']}dpi · JBIG2"
    if p["mode"] == "color":
        return f"JPEG q{prm['jpeg_q']} · {prm['dpi_cap']}dpi"
    if p["mode"] == "jpx":
        return f"JPEG2000 r{prm.get('rate', 192)} · {prm['dpi_cap']}dpi"
    if p["mode"] == "indexed":
        return f"Indexed {prm.get('colors', 64)}c · {prm['dpi_cap']}dpi"
    return "as-is"


class Worker(QThread):
    done = Signal(str)
    failed = Signal(str)
    progressed = Signal(int, int)

    def __init__(self, in_path, out_path, spec: dict, token):
        super().__init__()
        self.args = (in_path, out_path, spec, token)

    def run(self):
        in_path, out_path, spec, token = self.args
        try:
            cb = lambda a, b: self.progressed.emit(a, b)  # noqa: E731
            if spec["mode"] == "bw":
                process_file(in_path, out_path, spec["strategy"], spec["t"], spec["dpi"], token,
                             page_size=spec["page_size"], force_raster=spec["force_raster"],
                             progress=cb)
            elif spec["mode"] == "color":
                recompress_file(in_path, out_path, spec["dpi_cap"], spec["jpeg_q"], token,
                                progress=cb)
            elif spec["mode"] == "jpx":
                recompress_file(in_path, out_path, spec["dpi_cap"], token=token,
                                progress=cb, codec="jpx", rate=spec["rate"],
                                lossless=spec.get("lossless", False))
            elif spec["mode"] == "indexed":
                recompress_file(in_path, out_path, spec["dpi_cap"], token=token,
                                progress=cb, codec="indexed", colors=spec["colors"])
            else:
                gc_copy(in_path, out_path)
            if token.cancelled:
                try:
                    os.unlink(out_path)
                except OSError:
                    pass
                self.failed.emit("Cancelled")
            else:
                self.done.emit(out_path)
        except CancelledError:
            try:
                os.unlink(out_path)
            except OSError:
                pass
            self.failed.emit("Cancelled")
        except Exception as e:  # noqa: BLE001
            self.failed.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self, start_pdf: str | None = None):
        super().__init__()
        self.setWindowTitle("pdf-minimalist")
        self.resize(1100, 650)
        self.doc = None
        self.path = None
        self._orig_bytes: int | None = None  # input file size for % (designer §61)
        self.token = CancelToken()
        self.worker: Worker | None = None
        self._gen = 0  # background progress generation (cosmetic bar only)
        self._mini_jobs: set = set()  # mini workers: appended, never restarted.
        self._work_job = None  # amounts + preview for one spec (cancelled on change)
        self._jobs: set = set()  # in-flight workers: dropping the last ref while
        self._work_token = CancelToken()  # a QThread still runs aborts (Qt fatal)
        self._mini_pages: dict = {}  # (file_key, pid) -> [mini-page array|None] (§48)
        self._est_bytes: dict = {}  # (file_key, pid, dpi) -> [int|None], BW pages (§55)
        self._est_doc: dict = {}  # (file_key, pid) -> int doc total, color (§59)
        self._mini_view: dict = {}  # pid -> exact-view composite for today (§48)
        self._mini_est: dict = {}    # pid -> "est. X" for the top-visible page
        self._filter_prog: dict = {}  # pid -> 0.0..1.0 per-filter progress (§43)
        self._preview_cache: dict = {}  # (file_key, spec_tuple) -> [arrays] (§44)
        self._expect: dict = {}  # pid -> [mini_done, mini_total, est_done, est_total]
        self._shown_preview_key = None  # preview cache key currently shown (§108)
        self._applying = False  # True while a background preview is applied (no sync/cascade)
        self.setAcceptDrops(True)

        root = QWidget()
        self.setCentralWidget(root)
        top = QVBoxLayout(root)
        row = QHBoxLayout()

        mid = QVBoxLayout()
        # §107: no splitter — the panes share one fixed equal layout.
        self.panes = QHBoxLayout()
        self.panes.setContentsMargins(0, 0, 0, 0)
        self.panes.setSpacing(6)
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
        self.beforeHeader = QLabel("Original — no document")
        self.afterHeader = QLabel("Preview — no document")
        for hdr in (self.beforeHeader, self.afterHeader):
            hdr.setWordWrap(True)
            hdr.setStyleSheet("QLabel { padding: 2px 4px; }")
        leftWrap, rightWrap = QWidget(), QWidget()
        lv, rv = QVBoxLayout(leftWrap), QVBoxLayout(rightWrap)
        lv.setContentsMargins(0, 0, 0, 0)
        rv.setContentsMargins(0, 0, 0, 0)
        lv.addWidget(self.beforeHeader)
        lv.addWidget(self.before, 1)
        rv.addWidget(self.afterHeader)
        rv.addWidget(self.after, 1)
        self.panes.addWidget(leftWrap, 1)
        self.panes.addWidget(rightWrap, 1)
        mid.addLayout(self.panes, 1)
        self._apply_custom_presets()  # renames + copies before widgets (§109)
        self.filters = QListWidget()  # filter strip: full-width, below panes+panel
        self.filters.setViewMode(QListView.IconMode)
        self.filters.setIconSize(QSize(150, 168))
        self.filters.setResizeMode(QListView.Adjust)
        self.filters.setMovement(QListView.Static)
        self.filters.setSpacing(4)
        self.filters.setWordWrap(True)
        # §96: exactly one full row, never a vertical scrollbar; the strip
        # scrolls horizontally when filters overflow the width.
        self.filters.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.filters.setFixedHeight(186)
        self.filters.setItemDelegate(_StripDelegate(self))
        # §§96-98: Qt selection visuals are style-dependent (an invalid
        # declaration voids the whole rule — that's how the blue survived).
        # Bulletproof instead: the view selects NOTHING, ever, and never
        # takes keyboard focus (no focus wash either). currentRow still
        # tracks clicks for us, and our painted ring marks the filter.
        self.filters.setSelectionMode(QAbstractItemView.NoSelection)
        self.filters.setFocusPolicy(Qt.NoFocus)
        self.filters.setToolTip("Filters — click to preview (left stays baseline)")
        self._strip_ids = [p["id"] for p in presets.PRESETS if p["mode"] != "passthrough"]
        for pid in self._strip_ids:
            p = presets.get(pid)
            item = QListWidgetItem(p["label"])
            item.setData(Qt.UserRole, pid)
            item.setToolTip(p["blurb"])
            item.setSizeHint(QSize(150, 178))  # icon canvas: box + 3-line caption
            self.filters.addItem(item)
        # §98: the ring must mark the default filter from the start, not only
        # after the first click (safe: no document yet, dispatches no-op).
        try:
            self.filters.setCurrentRow(self._strip_ids.index(presets.default_preset_id()))
        except ValueError:
            pass
        # §77: strip spans the full window width; the right panel stops above
        # it and scrolls internally on overflow.
        top.addLayout(row, 1)
        top.addWidget(QLabel("Filters (left stays baseline, right shows filter):"))
        top.addWidget(self.filters)

        right = QVBoxLayout()
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
        for p in presets.PRESETS:
            self.preset.addItem(p["label"], p["id"])
        self.preset.setCurrentIndex([p["id"] for p in presets.PRESETS].index(presets.default_preset_id()))
        self.strategy = QComboBox()
        self.strategy.addItems(["otsu", "simple", "adaptive", "sauvola"])
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 255)
        self.slider.setValue(180)
        self.t_label = QLabel("T=180")
        self.colors = QSlider(Qt.Horizontal)  # §67: forced palette count
        self.colors.setRange(2, 256)
        self.colors.setValue(64)
        self.colors.setToolTip("Palette colors — only the Indexed filters use it.")
        self.c_label = QLabel("Colors=64")
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
        self.force_raster = QCheckBox("Force full-page raster")
        self.force_raster.setChecked(False)
        self.force_raster.setToolTip("ON: every page flattened to one image (default). OFF: pages with extractable text pass through untouched.")
        self.save_act = QAction("Save", self)
        _sic = QIcon.fromTheme("document-save")
        if not _sic.isNull():
            self.save_act.setIcon(_sic)
        self.save_act.setToolTip("Save reduced PDF (Ctrl+S)")
        self.save_act.triggered.connect(self.save)
        self.cancel_act = QAction("X", self)
        _xic = QIcon.fromTheme("process-stop")
        if not _xic.isNull():
            self.cancel_act.setIcon(_xic)
        self.cancel_act.setToolTip("X stops the running save — nothing else to undo (ESC)")
        self.cancel_act.setEnabled(False)
        right.addWidget(QLabel("Filter:"))
        # §109/§112: name dropdown fills the row; Rename, Copy and Save
        # share it compactly.
        nameRow = QHBoxLayout()
        nameRow.addWidget(self.preset, 1)
        self.rename_btn = QPushButton("Rename…")
        self.rename_btn.setToolTip("Rename the current filter")
        self.rename_btn.clicked.connect(self.rename_filter)
        self.rename_btn.setIcon(_rename_icon())
        self.copy_btn = QPushButton("Copy…")
        self.copy_btn.setToolTip("Copy the current filter under a new name")
        self.copy_btn.clicked.connect(self.copy_filter)
        self.copy_btn.setIcon(_copy_icon())
        self.keep_btn = QPushButton("Save")
        self.keep_btn.setToolTip("Save the current settings into this filter")
        self.keep_btn.clicked.connect(self.save_filter)
        _sic = QIcon.fromTheme("document-save")
        if not _sic.isNull():
            self.keep_btn.setIcon(_sic)
        nameRow.addWidget(self.rename_btn)
        nameRow.addWidget(self.copy_btn)
        nameRow.addWidget(self.keep_btn)
        right.addLayout(nameRow)
        # §54: filter details readout — the active filter's full recipe.
        self.details = QLabel()
        self.details.setWordWrap(True)
        self.details.setStyleSheet("QLabel { background: palette(base); "
                                   "border: 1px solid palette(mid); padding: 4px; }")
        right.addWidget(QLabel("Filter details:"))
        right.addWidget(self.details)
        right.addWidget(QLabel("Strategy:"))
        right.addWidget(self.strategy)
        right.addWidget(self.t_label)
        right.addWidget(self.slider)
        right.addWidget(self.c_label)
        right.addWidget(self.colors)
        right.addWidget(self.lossless_box)
        right.addWidget(QLabel("Raster DPI:"))
        right.addWidget(self.dpi)
        right.addWidget(QLabel("Page size:"))
        right.addWidget(self.page_size)
        right.addWidget(self.force_raster)
        # §76/§78/§85/§86: zoom is a joined segmented control — out, live
        # editable % (Evince/Okular convention: preset menu + type any
        # number), in — 16px drawn magnifiers, zero-gap group look.
        zoomBar = QToolBar("Zoom")
        zoomBar.setIconSize(QSize(16, 16))
        zoomBar.layout().setSpacing(0)
        zoomBar.layout().setContentsMargins(0, 0, 0, 0)
        zoomBar.setStyleSheet("QToolBar { spacing: 0px; }"
                              "QToolButton { border-radius: 0px; }")
        self.zoom_out_act = QAction(_zoom_icon(False), "Out", self)
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
        self.zoom_in_act = QAction(_zoom_icon(True), "In", self)
        self.zoom_in_act.setToolTip("Zoom in (Ctrl+Plus)")
        self.zoom_in_act.triggered.connect(lambda: self._button_zoom(1.25))
        zoomBar.addAction(self.zoom_out_act)
        zoomBar.addWidget(self.zoom_combo)
        zoomBar.addAction(self.zoom_in_act)
        zoomBar.addSeparator()
        zoomBar.addAction(self.save_act)
        zoomBar.addAction(self.cancel_act)
        zoomBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        right.addWidget(zoomBar)
        right.addStretch(1)

        panel = QWidget()
        panel.setLayout(right)
        self.panelScroll = QScrollArea()
        self.panelScroll.setWidget(panel)
        self.panelScroll.setWidgetResizable(True)
        self.panelScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.panelScroll.setMinimumWidth(250)
        midWrap = QWidget()
        midWrap.setLayout(mid)
        # §117: the divider between the previews and the right panel is a
        # real draggable splitter (like the old preview divider) — the
        # panel-width slider is gone. §107 still holds: nothing splits the
        # two panes themselves, they stay locked equal inside midWrap.
        self.panel_split = QSplitter(Qt.Horizontal)
        self.panel_split.setChildrenCollapsible(False)
        self.panel_split.addWidget(midWrap)
        self.panel_split.addWidget(self.panelScroll)
        self.panel_split.setStretchFactor(0, 1)
        self.panel_split.setStretchFactor(1, 0)
        row.addWidget(self.panel_split, 1)

        self.page_label = QLabel("No document")
        self.status = QLabel("Drop a PDF here or Open… (File > Open)")
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(220)
        sb = self.statusBar()
        sb.addWidget(self.status, 1)
        sb.addPermanentWidget(self.page_label)
        sb.addPermanentWidget(self.progress)

        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(200)
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
        self.slider.valueChanged.connect(lambda v: (self.t_label.setText(f"T={v}"), self._refresh_details(), self._preview_timer.start()))
        self.colors.valueChanged.connect(lambda v: (self.c_label.setText(f"Colors={v}"), self._refresh_details(), self._preview_timer.start()))
        self.lossless_box.toggled.connect(lambda _: (self._refresh_details(), self._preview_timer.start()))
        self.strategy.currentTextChanged.connect(lambda _: (self._refresh_details(), self._sync_filter_controls(), self._preview_timer.start()))
        self.dpi.currentIndexChanged.connect(lambda _: (self._refresh_details(), self._preview_timer.start()))
        self.page_size.currentIndexChanged.connect(lambda _: (self._refresh_details(), self._refresh_file_box(), self._preview_timer.start()))
        self.force_raster.toggled.connect(lambda _: (self._refresh_details(), self._preview_timer.start()))
        self.preset.currentIndexChanged.connect(self._preset_chosen)
        self.filters.currentRowChanged.connect(self._filterstrip_chosen)
        self.filters.currentRowChanged.connect(lambda _: self._repaint_all_strip())

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
        self.set_main_mode("side-h")
        self.set_filter_mode("film-h")

        # ESC anywhere cancels
        self.cancel_shortcut = self.cancel_act  # action doubles as shortcut
        self._refresh_details()
        self._sync_threshold_enabled()
        if start_pdf:
            self.open_file(start_pdf)

    # --- presets + view modes ---
    def _custom_store(self):
        from PySide6.QtCore import QSettings as _QS
        return _QS("pdf-minimalist", "pdf-minimalist")

    def _apply_custom_presets(self):
        """Merge remembered renames + copies into PRESETS (designer §109)."""
        try:
            renames = self._custom_store().value("customRenames", {}) or {}
            customs = self._custom_store().value("customPresets", []) or []
        except Exception:  # noqa: BLE001
            renames, customs = {}, []
        ids = {p["id"] for p in presets.PRESETS}
        for c in customs:
            if not isinstance(c, dict) or "id" not in c:
                continue
            if c["id"] not in ids:
                presets.PRESETS.append(c)
                ids.add(c["id"])
            else:
                # A saved-over builtin (§112): same id replaces params+label.
                for p in presets.PRESETS:
                    if p["id"] == c["id"]:
                        p["params"] = dict(c.get("params", p["params"]))
                        p["label"] = c.get("label", p["label"])
                        break
        for p in presets.PRESETS:
            if p["id"] in renames:
                p["label"] = renames[p["id"]]

    def _preset_label(self, pid: str) -> str:
        return presets.get(pid)["label"]

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
        self.preset.setItemText(self.preset.currentIndex(), name)
        self._repaint_all_strip()
        self._update_pane_headers()
        log.info("filter renamed: %s -> %s", pid, name)

    def copy_filter(self):
        """Copy the current filter under a popup-given name (§109)."""
        import copy as _copy
        from PySide6.QtWidgets import QInputDialog as _QD
        from PySide6.QtWidgets import QListWidgetItem as _QI
        pid = self.preset.itemData(self.preset.currentIndex())
        if not pid:
            return
        src = presets.get(pid)
        name, ok = _QD.getText(self, "Copy filter",
                               f"Name for the copy of '{src['label']}':",
                               text=f"{src['label']} copy")
        name = name.strip()
        if not ok or not name:
            return
        base = "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-") or "custom"
        nid, k = base, 2
        ids = {p["id"] for p in presets.PRESETS}
        while nid in ids:
            nid = f"{base}-{k}"
            k += 1
        new = {"id": nid, "label": name, "mode": src["mode"],
               "params": _copy.deepcopy(src["params"]),
               "blurb": f"copy of {src['label']}"}
        presets.PRESETS.append(new)
        store = self._custom_store()
        customs = store.value("customPresets", []) or []
        customs.append(new)
        store.setValue("customPresets", customs)
        self.preset.addItem(name, nid)
        if new["mode"] != "passthrough":
            item = _QI("")
            item.setData(Qt.UserRole, nid)
            item.setToolTip(new["blurb"])
            item.setSizeHint(QSize(150, 178))
            self.filters.addItem(item)
            self._strip_ids.append(nid)
            self._filter_prog[nid] = 0.0
            self._paint_strip_item(nid)
        self.preset.setCurrentIndex(self.preset.count() - 1)
        log.info("filter copied: %s -> %s (%s)", pid, nid, name)

    def save_filter(self):
        """Persist the current UI settings into the current filter (§112).

        Writes a full custom entry (shadowing builtins by id) to QSettings,
        invalidates that filter's cached minis/amounts so they rebuild from
        the new recipe, and repaints.
        """
        import copy as _copy
        pid = self.preset.itemData(self.preset.currentIndex())
        if not pid:
            return
        p = presets.get(pid)
        prm = _copy.deepcopy(p["params"])
        if p["mode"] == "bw":
            prm["strategy"] = self.strategy.currentText()
            prm["t"] = self.slider.value()
            prm["dpi"] = self.dpi.currentData()
            prm["force_raster"] = self.force_raster.isChecked()
        else:
            prm["dpi_cap"] = self.dpi.currentData()
            if p["mode"] == "indexed":
                prm["colors"] = self.colors.value()
        entry = {"id": pid, "label": p["label"], "mode": p["mode"],
                 "params": prm, "blurb": p.get("blurb", "")}
        store = self._custom_store()
        customs = [c for c in (store.value("customPresets", []) or [])
                   if isinstance(c, dict) and c.get("id") != pid]
        customs.append(entry)
        store.setValue("customPresets", customs)
        p["params"] = _copy.deepcopy(prm)
        fkey = self._file_key()
        if fkey is not None and self.doc is not None:
            self._mini_pages.pop(self._mini_key(fkey, pid), None)
            self._est_bytes.pop(
                (fkey, pid, self.dpi.currentData()), None)
            for key in [k for k in self._est_doc if k[0] == fkey and k[1] == pid]:
                self._est_doc.pop(key, None)
            self._preview_cache.pop((fkey, self._spec_tuple(self._active_spec())), None)
            self._expect.pop(pid, None)
            self._filter_prog[pid] = 0.0
        self._refresh_details()
        self._repaint_all_strip()
        self._dispatch_filters()
        log.info("filter saved: %s params=%s", pid, prm)

    def _sync_filter_controls(self):
        """§§65/67/85/100: T feeds ONLY Simple; Colors feeds ONLY Indexed;
        Lossless is a choice ONLY for JPEG2000. Raster DPI feeds every mode
        (§85: the single DPI) so it stays enabled.

        Controls without a choice stay visible but grey, showing the correct
        fixed state (§100) — and live controls that change nothing stay
        disabled (this also stops pointless identical-output jobs)."""
        mode = presets.get(self.preset.itemData(self.preset.currentIndex()))["mode"]
        t_on = mode == "bw" and self.strategy.currentText() == "simple"
        self.slider.setEnabled(t_on)
        self.t_label.setEnabled(t_on)
        self.t_label.setToolTip("Fixed threshold — only the Simple strategy uses it."
                                if t_on else "Fixed threshold — only the Simple strategy uses it "
                                "(Otsu/adaptive/Sauvola are automatic).")
        c_on = mode == "indexed"
        self.colors.setEnabled(c_on)
        self.c_label.setEnabled(c_on)
        self.dpi.setEnabled(True)
        self.dpi.setToolTip("The single DPI: every image in the document (§85).")
        if mode == "jpx":
            self.lossless_box.setEnabled(True)
        else:
            # Fixed state per mode (§100): BW/indexed/passthrough are always
            # lossless; baseline JPEG never is.
            fixed = mode in ("bw", "indexed", "passthrough")
            if self.lossless_box.isChecked() != fixed:
                self.lossless_box.setChecked(fixed)
            self.lossless_box.setEnabled(False)

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
        p = presets.get(pid)
        if p["mode"] == "bw":
            lines = [
                "Codec: JBIG2",
                f"Threshold: {self.strategy.currentText()} "
                f"T={self.slider.value()}",
                f"Render: {self.dpi.currentData()} dpi · "
                f"{'forced raster' if self.force_raster.isChecked() else 'text pass-through'}",
            ]
        elif p["mode"] == "color":
            prm = p["params"]
            lines = [
                "Codec: JPEG",
                f"Quality: q={prm['jpeg_q']} · {self.dpi.currentData()}dpi",
                "Keeps vectors and text",
            ]
        elif p["mode"] == "jpx":
            prm = p["params"]
            lines = [
                "Codec: JPEG2000",
                ("Lossless" if self.lossless_box.isChecked() else
                 f"Rate: r={prm.get('rate', 192)}") + f" · {self.dpi.currentData()}dpi",
                "Keeps vectors and text",
            ]
        elif p["mode"] == "indexed":
            lines = [
                "Codec: Flate (palette)",
                f"Colors: {self.colors.value()} (auto algorithm, no dither)",
                "Lossless when smallest; keeps vectors and text",
            ]
        else:
            lines = [
                "Codec: none (passthrough)",
                "gc + deflate only — pixels unchanged",
            ]
        self.details.setText("\n".join(lines))

    def _preset_chosen(self, idx: int):
        pid = self.preset.itemData(idx)
        if not pid:
            return
        log.info("preset selected: %s", pid)
        p = presets.get(pid)
        if p["mode"] == "bw":
            self.strategy.setCurrentText(p["params"]["strategy"])
            self.slider.setValue(p["params"]["t"])
            self.force_raster.setChecked(bool(p["params"].get("force_raster", False)))
            self.dpi.setCurrentIndex(list(presets.RASTER_DPIS).index(p["params"]["dpi"]))
        else:
            # §85: one DPI for the whole filter — the preset seeds the shared
            # combo, which then rules preview, totals and save alike.
            cap = p["params"].get("dpi_cap", presets.DEFAULT_DPI)
            if cap in presets.RASTER_DPIS:
                self.dpi.setCurrentIndex(list(presets.RASTER_DPIS).index(cap))
        if p["mode"] == "indexed":
            self.colors.setValue(p["params"]["colors"])
        if p["mode"] == "jpx":
            # Presets carry no lossless default (§81: usually lossy).
            self.lossless_box.setChecked(False)
        if p["mode"] in ("color", "jpx", "indexed"):
            cap = p["params"].get("dpi_cap", presets.DEFAULT_DPI)
            if cap in presets.RASTER_DPIS:
                self.dpi.setCurrentIndex(list(presets.RASTER_DPIS).index(cap))
        if pid in self._strip_ids:  # passthrough has no mini; left pane is the baseline
            row = self._strip_ids.index(pid)
            if self.filters.currentRow() != row:
                self.filters.setCurrentRow(row)
        self._refresh_details()
        self._sync_threshold_enabled()
        self._update_pane_headers()
        if self._try_apply_cached():
            return
        self._preview_timer.start()

    def _filterstrip_chosen(self, row: int):
        if row < 0 or row >= len(self._strip_ids):
            return
        idx = [p["id"] for p in presets.PRESETS].index(self._strip_ids[row])
        if self.preset.currentIndex() != idx:
            self.preset.setCurrentIndex(idx)
        elif self._try_apply_cached():
            self._update_pane_headers()
            return
        else:
            self._update_pane_headers()
            self._preview_timer.start()

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
            self.filters.setMaximumHeight(230)
            self.filters.setMinimumHeight(190)
        elif mode == "rail-v":
            self.filters.setFlow(QListWidget.TopToBottom)
            self.filters.setMaximumHeight(16777215)
        else:  # grid
            self.filters.setFlow(QListWidget.LeftToRight)
            self.filters.setMaximumHeight(16777215)
            self.filters.setWrapping(True)
            return
        self.filters.setWrapping(False)

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
        try:
            if self.doc:
                self.doc.close()
            self.doc = fitz.open(path)
            self.path = path
            for _mj in list(self._mini_jobs):
                _mj.token.cancel()
            self._work_token.cancel()
            self._work_token = CancelToken()
            from PySide6.QtCore import QSettings as _QS
            _QS("pdf-minimalist", "pdf-minimalist").setValue(
                "lastFile", os.path.abspath(path))
            try:
                self._orig_bytes = os.path.getsize(path)
            except OSError:
                self._orig_bytes = None
            self._refresh_file_box()
            self._mini_pages.clear()
            self._est_bytes.clear()
            self._est_doc.clear()
            self._mini_view.clear()
            self._mini_est.clear()
            self._filter_prog.clear()
            self._expect.clear()
            self._preview_cache.clear()
            self._shown_preview_key = None
            for pid in self._strip_ids:
                self._filter_prog[pid] = 0.0
            self._repaint_all_strip()
            self._render_all()
            self.before.goto_page(0)
            self.page_label.setText(f"Page 1 of {self.doc.page_count} (PgUp/PgDn)")
            self.status.setText(f"{os.path.basename(path)} — {self.doc.page_count} pages")
            log.info("opened %s pages=%d", path, self.doc.page_count)
        except Exception as e:  # noqa: BLE001
            # §14 run-and-review: the traceback belongs in stdout first — a
            # popup alone buries it (designer §102).
            log.exception("open failed %s", path)
            QMessageBox.warning(self, "Open failed", str(e))

    # --- continuous render ---
    def _render_page_rgb(self, i: int, dpi: int = PREVIEW_DPI) -> np.ndarray:
        pix = self.doc[i].get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False)
        return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3).copy()

    def _render_page_gray(self, i: int, dpi: int = PREVIEW_DPI) -> np.ndarray:
        pix = self.doc[i].get_pixmap(dpi=dpi, colorspace=fitz.csGRAY, alpha=False)
        return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).copy()

    def _render_all(self):
        """Baseline panes (fast sync renders) + background filter job."""
        if not self.doc:
            return
        t0 = time.perf_counter()
        n = self.doc.page_count
        base = [rgb_to_qimage(self._render_page_rgb(i)) for i in range(n)]
        self.before.set_pages(base)
        log.info("baseline rendered %d pages in %.0fms", n, (time.perf_counter() - t0) * 1000)
        # §111: the right pane never sits empty — baseline now, real preview
        # the moment it lands (tracked by _shown_preview_key).
        self._applying = True
        self.after._syncing = True
        try:
            self.after.set_pages(base)
            self.after.setTransform(self.before.transform())
            self.after._zoom = self.before._zoom
            self.after.relayout()
        finally:
            self.after._syncing = False
            self._applying = False
        self._shown_preview_key = None
        self._dispatch_filters()

    def _active_spec(self) -> dict:
        pid = self.preset.itemData(self.preset.currentIndex())
        p = presets.get(pid)
        spec = {"preset_id": pid, "mode": p["mode"], "dpi": self.dpi.currentData()}
        if p["mode"] == "bw":
            spec.update(strategy=self.strategy.currentText(), t=self.slider.value(),
                        force_raster=self.force_raster.isChecked())
        if p["mode"] in ("color", "jpx", "indexed"):
            # §85: the combo is the single DPI for the whole filter.
            spec.update(dpi_cap=self.dpi.currentData())
        if p["mode"] == "indexed":
            spec.update(colors=self.colors.value())
        if p["mode"] == "jpx":
            spec.update(lossless=self.lossless_box.isChecked())
        return spec

    def _file_key(self):
        """Identity for process-once cache §44: path + mtime + size."""
        if not self.path:
            return None
        try:
            st = os.stat(self.path)
            return (os.path.abspath(self.path), st.st_mtime_ns, st.st_size)
        except OSError:
            return (os.path.abspath(self.path),)

    @staticmethod
    def _spec_tuple(spec: dict):
        # Preview identity (§113): the preview shows the filter effect, which
        # never depends on force-raster — so force is NOT part of this key
        # (toggling it must not rebuild the preview).
        return (spec.get("preset_id"), spec.get("mode"), spec.get("dpi"),
                spec.get("strategy"), spec.get("t"), spec.get("colors"),
                spec.get("dpi_cap"), spec.get("lossless", False))

    @staticmethod
    def _mini_key(fkey, pid: str):
        """Mini cache key (§105: force-independent — minis always depict the
        preset recipe, so the checkbox never churns them)."""
        return (fkey, pid)

    @staticmethod
    def _estb_key(fkey, pid: str, dpi):
        """BW est cache key (§§103/106: force-independent — each filter's
        amount follows its OWN recipe force, so the checkbox never churns
        any size; it arms Save and refreshes details only)."""
        return (fkey, pid, dpi)

    def _repaint_all_strip(self):
        for pid in self._strip_ids:
            self._paint_strip_item(pid)

    def _apply_preview_pages(self, pages, source: str, key=None):
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
            self.after.set_pages([rgb_to_qimage(a) for a in pages])
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
        """§44: if the active spec already has a cached preview, show it now."""
        if not self.doc or not self.path:
            return False
        fkey = self._file_key()
        if fkey is None:
            return False
        spec = self._active_spec()
        pkey = (fkey, self._spec_tuple(spec))
        pages = self._preview_cache.get(pkey)
        if pages is None:
            return False
        try:
            self._preview_timer.stop()
        except Exception:
            pass
        self._apply_preview_pages(pages, "cache", pkey)
        return True

    @staticmethod
    def _est_ck(pid: str, spec: dict):
        """Cache key tail for a color total: (colors, cap, lossless).

        The ACTIVE filter follows the UI (single-DPI ruling §85); inactive
        presets show their own recipe values (matching their minis) until
        selected — at which point the combo syncs and the keys agree.
        """
        if pid == spec.get("preset_id"):
            return (spec.get("colors"), spec.get("dpi_cap"),
                    spec.get("lossless", False))
        prm = presets.get(pid)["params"]
        return (prm.get("colors"), prm.get("dpi_cap"), False)

    @staticmethod
    def _preset_snapshot() -> dict:
        """Picklable mode+params per strip filter for pool workers (§109).

        Workers re-import modules fresh and never see runtime renames,
        copies or saves — without this snapshot those tasks KeyError and the
        strip hangs forever.
        """
        import copy as _copy
        snap = {}
        for p in presets.PRESETS:
            if p["mode"] == "passthrough":
                continue
            snap[p["id"]] = {"mode": p["mode"],
                             "params": _copy.deepcopy(p["params"])}
        return snap

    def _dispatch_filters(self):
        """Background work for cache misses only (§§43/44/47/48).

        Dispatches on FILE change or SPEC change alone. Scroll, pan, zoom,
        page turns and strip clicks never reach here with work to do: minis
        reframe from the per-preset caches (§48) and previews hit
        `_try_apply_cached` first.
        Two slots (§90): minis belong to the FILE — once launched they are
        never cancelled or re-run, so clicking a far-right filter cannot
        restart the left filters. Amounts + preview belong to the SPEC and
        restart on change. Arrival handlers are key-addressed (file/spec
        keys), never generation-gated; the generation drives only the
        cosmetic global bar.
        """
        if not self.doc or not self.path:
            return
        fkey = self._file_key()
        if fkey is None:
            return
        n = self.doc.page_count
        spec = self._active_spec()
        spec_tup = self._spec_tuple(spec)
        dpi = spec.get("dpi")
        preview_key = (fkey, spec_tup)

        need_mini = {}
        for pid in self._strip_ids:
            pages = self._mini_pages.get(self._mini_key(fkey, pid))
            if pages is None:
                need_mini[pid] = list(range(n))
            else:
                missing = [i for i, pg in enumerate(pages) if pg is None]
                if len(pages) != n:
                    missing = list(range(n))
                if missing:
                    need_mini[pid] = missing
        need_est_pages = {}
        need_est_doc = {}
        for pid in self._strip_ids:
            if presets.get(pid)["mode"] == "bw":
                counts = self._est_bytes.get(self._estb_key(fkey, pid, dpi))
                if counts is None:
                    need_est_pages[pid] = list(range(n))
                else:
                    missing = [i for i, t in enumerate(counts) if t is None]
                    if len(counts) != n:
                        missing = list(range(n))
                    if missing:
                        need_est_pages[pid] = missing
            else:
                # Color totals follow the single DPI (§85): active filter uses
                # the UI values, inactive presets their own recipe values.
                ck = self._est_ck(pid, spec)
                if (fkey, pid) + ck not in self._est_doc:
                    need_est_doc[pid] = ck
        need_preview = preview_key not in self._preview_cache

        # Mini jobs are never cancelled for new needs: subtract whatever is
        # already submitted by running jobs, and top up the rest in a new
        # worker (§90 follow-up — added presets must not restart the rest).
        covered: set[tuple] = set()
        for _rj in list(self._mini_jobs):
            if _rj.isFinished() or getattr(_rj, "_fkey", None) != fkey:
                continue
            for _pid, _idxs in _rj.need_mini.items():
                covered.update((_pid, _i) for _i in _idxs)
        top_up = {}
        for pid, idxs in need_mini.items():
            rest = [i for i in idxs if (pid, i) not in covered]
            if rest:
                top_up[pid] = rest
        filter_pool()  # warm on the main thread; workers only ever submit
        if top_up:
            for pid, idxs in top_up.items():
                exp = self._expect.setdefault(pid, [0, 0, 0, 0])
                exp[1] = len(idxs)
            self._reframe_minis()
            self.status.setText("Rendering filters…")
            log.info("mini job pages=%d preset=%s missing=%d",
                     n, spec["preset_id"],
                     sum(len(v) for v in top_up.values()))
            job = FilterWorker(self.path, self._strip_ids, spec,
                               CancelToken(), self._gen, n,
                               need_mini=top_up,
                               preset_snap=self._preset_snapshot())
            job._fkey = fkey
            job.mini_done.connect(self._jm_mini)
            job.progressed.connect(self._jm_progress)
            job.finished.connect(lambda: self._clear_job(job))
            self._mini_jobs.add(job)
            self._jobs.add(job)
            job.start()

        if need_est_pages or need_est_doc or need_preview:
            if self._work_job is not None:
                self._work_token.cancel()
            self._work_token = CancelToken()
            self._gen += 1
            for pid in self._strip_ids:
                exp = self._expect.setdefault(pid, [0, 0, 0, 0])
                if presets.get(pid)["mode"] == "bw":
                    exp[3] = len(need_est_pages.get(pid, ()))
                else:
                    exp[3] = 0 if (fkey, pid) + self._est_ck(pid, spec) in self._est_doc else 1
            self._reframe_minis()
            if need_preview and not need_est_pages and not need_est_doc:
                self.status.setText(f"Rendering preview… (job {self._gen})")
            else:
                self.status.setText(f"Rendering amounts… (job {self._gen})")
            log.info("work job gen=%d pages=%d preset=%s need_est=%d need_preview=%s",
                     self._gen, n, spec["preset_id"],
                     sum(len(v) for v in need_est_pages.values()) + len(need_est_doc),
                     need_preview)
            job = FilterWorker(self.path, self._strip_ids, spec,
                               self._work_token, self._gen, n,
                               need_est_pages=need_est_pages,
                               need_est_doc=need_est_doc,
                               need_preview=need_preview,
                               preset_snap=self._preset_snapshot())
            job._fkey = fkey
            job._est_dpi = dpi
            job._preview_key = preview_key
            job.est_done.connect(self._jm_est)
            job.preview_done.connect(self._jm_preview)
            job.progressed.connect(self._jm_progress)
            job.finished.connect(lambda: self._clear_job(job))
            self._work_job = job
            self._jobs.add(job)
            job.start()
        else:
            self._reframe_minis()
            log.info("filter job skipped (cache hit) preset=%s", spec["preset_id"])

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
            pid = self.preset.itemData(self.preset.currentIndex())
            size = self._mini_est.get(pid, "sizing…")
            right = f"{presets.get(pid)['label']} · {_preset_algo(pid)} · {size}"
        if self.beforeHeader.text() != left:
            self.beforeHeader.setText(left)
        if self.afterHeader.text() != right:
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
        self._update_pane_headers()

    def _reframe_one(self, pid: str):
        if not self.doc or not self.path:
            return
        fkey = self._file_key()
        if fkey is None:
            return
        pages = self._mini_pages.get(self._mini_key(fkey, pid))
        dpi = self.dpi.currentData()
        # §§55/59/61: real post-save amounts with % of the original — no
        # estimates anywhere. BW sums the exact per-page payload bytes; color
        # shows the exact per-image decision total. Container overhead is
        # reported at Save instead.
        if presets.get(pid)["mode"] == "bw":
            counts = self._est_bytes.get(self._estb_key(fkey, pid, dpi))
            if counts is not None and len(counts) == self.doc.page_count and \
                    all(c is not None for c in counts):
                shown = self._sized(sum(counts))
            else:
                shown = None
        else:
            total = self._est_doc.get((fkey, pid) + self._est_ck(pid, self._active_spec()))
            shown = self._sized(total) if total is not None else None
        if shown is not None:
            if self._mini_est.get(pid) != shown:
                self._mini_est[pid] = shown
        # §106: stale-while-revalidate — a recompute never blanks a known
        # amount (the progress bar already signals work); only a new file
        # clears the display (see open_file). First load still shows
        # working…/queued… via the paint fallbacks.
        if pages is not None and all(pg is not None for pg in pages):
            cols, pw, ph, vis = self._current_view()
            try:
                self._mini_view[pid] = frame_view(
                    pages, pw, ph, ContinuousDocView.GAP, cols, vis)
            except Exception:  # noqa: BLE001
                log.debug("reframe failed for %s", pid, exc_info=True)
                return
            exp = self._expect.get(pid)
            if exp is not None and (exp[1] or exp[3]):
                self._filter_prog[pid] = filter_progress(*exp)
            else:
                self._filter_prog[pid] = 1.0
        self._paint_strip_item(pid)

    def _clear_job(self, job):
        self._jobs.discard(job)
        self._mini_jobs.discard(job)
        if self._work_job is job:
            self._work_job = None

    def _paint_strip_item(self, pid: str):
        if pid not in self._strip_ids:
            return
        prog = float(self._filter_prog.get(pid, 0.0))
        arr = self._mini_view.get(pid)
        if pid in self._mini_est:
            est = self._mini_est[pid]
        elif arr is not None:
            est = "sizing…"
        elif prog > 0.0:
            est = "working…"
        else:
            est = "queued…"
        icon = QPixmap(150, 168)
        icon.fill(Qt.white)
        pt = QPainter(icon)
        # §46: clear preview box — bordered frame around the mini, divided
        # from the small caption below it (§53: name, algorithm, size).
        box = (13, 2, 124, 108)
        pt.setPen(QPen(Qt.gray, 1))
        pt.drawRect(*box)
        # §98: the modern selection marker is a ring ON the selected item —
        # not a bar below it. Painted by us in the theme highlight color, so
        # it survives styles and focus changes, and always marks the filter
        # the right pane is showing.
        try:
            _cur = self._strip_ids[self.filters.currentRow()]
        except IndexError:
            _cur = None
        if pid == _cur:
            pt.setPen(QPen(self.palette().highlight().color(), 2))
            pt.drawRect(box[0] - 1, box[1] - 1, box[2] + 2, box[3] + 2)
        if arr is not None:
            q = gray_to_qimage(arr) if arr.ndim == 2 else rgb_to_qimage(arr)
            mini = QPixmap.fromImage(q).scaled(120, 104, Qt.KeepAspectRatio,
                                               Qt.SmoothTransformation)
            pt.drawPixmap(box[0] + (box[2] - mini.width()) // 2,
                          box[1] + (box[3] - mini.height()) // 2, mini)
        else:
            small_ph = QFont(pt.font())
            small_ph.setPointSize(max(7, small_ph.pointSize() - 2))
            pt.setFont(small_ph)
            pt.drawText(box[0], box[1], box[2], box[3],
                        Qt.AlignCenter | Qt.TextWordWrap, "working…")
        # Divider between preview box and caption.
        pt.setPen(QPen(Qt.lightGray, 1))
        pt.drawLine(8, 116, 142, 116)
        small = QFont(pt.font())
        small.setPointSize(max(7, small.pointSize() - 2))
        pt.setFont(small)
        pt.setPen(QPen(Qt.black, 1))
        pt.drawText(0, 118, 150, 15, Qt.AlignHCenter, presets.get(pid)["label"])
        pt.setPen(QPen(Qt.darkGray, 1))
        pt.drawText(0, 133, 150, 14, Qt.AlignHCenter, _preset_algo(pid))
        pt.drawText(0, 147, 150, 14, Qt.AlignHCenter, est)
        if prog < 1.0:
            # §43/§96/§99: the standard progress bar, laid over the middle —
            # style colors (Highlight chunk on Mid groove, never a hardcoded
            # green) with the % centered exactly like QProgressBar.
            bx, by, bw, bh = 23, 51, 104, 12
            pal = self.palette()
            pt.fillRect(bx, by, bw, bh, pal.color(QPalette.Mid))
            fw = int(round(bw * max(0.0, min(1.0, prog))))
            pt.fillRect(bx, by, fw, bh, pal.color(QPalette.Highlight))
            label = f"{prog * 100:.0f}%"
            pt.setPen(QPen(pal.color(QPalette.WindowText)))
            pt.drawText(bx, by, bw, bh, Qt.AlignCenter, label)
            pt.save()
            pt.setClipRect(bx, by, fw, bh)
            pt.setPen(QPen(pal.color(QPalette.HighlightedText)))
            pt.drawText(bx, by, bw, bh, Qt.AlignCenter, label)
            pt.restore()
        pt.end()
        self.filters.item(self._strip_ids.index(pid)).setIcon(QIcon(icon))
        self.filters.item(self._strip_ids.index(pid)).setText("")

    def _jm_mini(self, pid, page, arr, gen):
        job = self.sender()
        if job is None or getattr(job, "_fkey", None) != self._file_key():
            return
        n = self.doc.page_count if self.doc else 0
        key = self._mini_key(job._fkey, pid)
        pages = self._mini_pages.get(key)
        if pages is None or len(pages) != n:
            pages = [None] * n
            self._mini_pages[key] = pages
        if 0 <= page < n:
            pages[page] = arr
        exp = self._expect.get(pid)
        if exp is not None:
            exp[0] += 1
        self._reframe_one(pid)

    def _jm_est(self, pid, page, value, gen):
        job = self.sender()
        if job is None or getattr(job, "_fkey", None) != self._file_key():
            return
        if page < 0:
            # Whole-document color total (§59); key carries the values used.
            ck = job.need_est_doc.get(pid)
            self._est_doc[(job._fkey, pid) + tuple(ck)] = int(value)
        else:
            n = self.doc.page_count if self.doc else 0
            key = self._estb_key(job._fkey, pid, getattr(job, "_est_dpi", None))
            counts = self._est_bytes.get(key)
            if counts is None or len(counts) != n:
                counts = [None] * n
                self._est_bytes[key] = counts
            if 0 <= page < n:
                counts[page] = int(value)
        exp = self._expect.get(pid)
        if exp is not None:
            exp[2] += 1
        log.debug("job gen=%d %s p%s -> %dB", gen, pid, page + 1, value)
        self._reframe_one(pid)

    def _jm_preview(self, pages, gen):
        if not self.doc:
            return
        job = self.sender()
        pkey = getattr(job, "_preview_key", None)
        if pkey is None:
            return
        # Cache every completed preview; show it only if it is still the
        # active spec (a stale arrival must never steal the panes).
        self._preview_cache[pkey] = list(pages)
        while len(self._preview_cache) > 2:  # bound memory: latest specs only
            self._preview_cache.pop(next(iter(self._preview_cache)))
        try:
            current = (self._file_key(), self._spec_tuple(self._active_spec()))
        except Exception:  # noqa: BLE001
            return
        if pkey != current:
            log.info("job gen=%d preview cached, not current (%d pages)", gen, len(pages))
            return
        self._apply_preview_pages(pages, f"job {gen}", pkey)
        log.info("job gen=%d preview applied (%d pages)", gen, len(pages))

    def _jm_progress(self, done, total, gen):
        if gen != self._gen:
            return
        self.progress.setMaximum(total)
        self.progress.setValue(done)
        log.debug("job gen=%d filter progress %d/%d", gen, done, total)

    def _on_page_changed(self, idx: int):
        if not self.doc or getattr(self, "_applying", False):
            return
        self.page_label.setText(f"Page {idx + 1} of {self.doc.page_count} (PgUp/PgDn)")
        log.debug("current page %d", idx + 1)
        # §47: a page turn is a view change — reframe minis from cache only.
        self._reframe_minis()

    # --- run / cancel ---
    def save(self):
        if not self.path:
            return
        out, _ = QFileDialog.getSaveFileName(self, "Save reduced PDF", self.path.replace(".pdf", ".reduced.pdf"), "PDF (*.pdf)")
        if not out:
            return
        if os.path.abspath(out) == os.path.abspath(self.path):
            QMessageBox.warning(self, "Refusing", "Won't overwrite input. Pick another name.")
            return
        self.token.reset()
        pid = self.preset.itemData(self.preset.currentIndex())
        p = presets.get(pid)
        if p["mode"] == "bw":
            spec = {"mode": "bw", "strategy": self.strategy.currentText(), "t": self.slider.value(),
                    "dpi": self.dpi.currentData(), "page_size": self.page_size.currentData(),
                    "force_raster": self.force_raster.isChecked()}
        elif p["mode"] == "color":
            spec = {"mode": "color", "dpi_cap": self.dpi.currentData(), "jpeg_q": p["params"]["jpeg_q"]}
        elif p["mode"] == "jpx":
            spec = {"mode": "jpx", "dpi_cap": self.dpi.currentData(), "rate": p["params"].get("rate", 192),
                    "lossless": self.lossless_box.isChecked()}
        elif p["mode"] == "indexed":
            spec = {"mode": "indexed", "dpi_cap": self.dpi.currentData(), "colors": self.colors.value()}
        else:
            spec = {"mode": "passthrough"}
        log.info("save start preset=%s spec=%s in=%s out=%s", pid, spec, self.path, out)
        self.worker = Worker(self.path, out, spec, self.token)
        self._jobs.add(self.worker)
        self.worker.finished.connect(lambda: self._jobs.discard(self.worker))
        self.worker.done.connect(self._on_done)
        self.worker.failed.connect(self._on_failed)
        self.worker.progressed.connect(self._on_progress)
        self.worker.start()
        self.cancel_act.setEnabled(True)
        self.status.setText("Working… ESC to cancel")

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
        """§94: closing mid-processing must never crash. Cancel everything,
        let worker threads notice between phases and join them, then close."""
        self.token.cancel()
        for _mj in list(self._mini_jobs):
            _mj.token.cancel()
        self._work_token.cancel()
        for job in list(self._jobs):
            try:
                job.wait(8000)
            except Exception:  # noqa: BLE001
                pass
        if self.doc:
            try:
                self.doc.close()
            except Exception:  # noqa: BLE001
                pass
            self.doc = None
        super().closeEvent(e)


def main(start_pdf: str | None = None, debug: bool = False):
    log.info("starting pdf-minimalist debug=%s pdf=%s", debug, start_pdf)
    if start_pdf is None:
        # §91: reopen the last file; fall back to the photo demo.
        from PySide6.QtCore import QSettings as _QS
        last = _QS("pdf-minimalist", "pdf-minimalist").value("lastFile")
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
    w = MainWindow(start_pdf)
    w.show()
    log.info("window shown")
    sys.exit(app.exec())
