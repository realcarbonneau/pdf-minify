import os
import time

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import fitz  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from pdf_minify.ui_qt.app import (  # noqa: E402
    MainWindow, STRIP_ICON, STRIP_PADDING, STRIP_PREVIEW_RECT, STRIP_AMOUNT_RECT,
)
from pdf_minify.ui_qt.jobs import cpu_cap  # noqa: E402

_app = QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def _close_test_windows(monkeypatch):
    """Each GUI test owns its windows, workers, and disposable artifacts."""
    existing = set(_app.topLevelWidgets())
    yield
    windows = [w for w in _app.topLevelWidgets()
               if isinstance(w, MainWindow) and w not in existing]
    for w in windows:
        monkeypatch.setattr(w, "_ask_unsaved_filter", lambda pid: "discard")
        w.close()
    deadline = time.monotonic() + 60
    while any(w._jobs for w in windows):
        assert time.monotonic() < deadline, "filter workers did not close safely"
        _app.processEvents()
        time.sleep(0.02)
    _app.processEvents()


def _three_pages(tmpdir):
    src = os.path.join(tmpdir, "m.pdf")
    d = fitz.open()
    for i in range(3):
        p = d.new_page(width=400, height=400)
        p.insert_text((50, 200), f"Mini test {i}")
    d.save(src)
    d.close()
    return src


def _wait_job(w, timeout=90):
    # Queued cross-thread results can land after isFinished flips, so settle
    # on the STORES (minis + amounts for every filter), not thread state.
    t0 = time.perf_counter()
    while w._artifacts.pending or len(w._mini_view) < len(w._strip_ids) or len(w._mini_amount) < len(w._strip_ids):
        assert time.perf_counter() - t0 < timeout, "filter results hung"
        _app.processEvents()
        time.sleep(0.05)
    _app.processEvents()


def test_background_job_fills_minis_and_preview(tmp_path):
    w = MainWindow(str(_three_pages(str(tmp_path))))
    assert w.before.page_count == 3
    _wait_job(w)
    assert w.after.page_count == 3  # preview applied without freezing
    assert w.filters.count() == 10  # passthrough/Original has no mini (§30)
    for i in range(10):
        assert not w.filters.item(i).icon().isNull(), i
    assert len(w._mini_amount) == 10
    # every filter must hold a real reframed composite, not a placeholder:
    # placeholders pass icon checks and hid the JPX mini crash (§56 wiring).
    assert set(w._mini_view) == set(w._strip_ids)
    for pid, arr in w._mini_view.items():
        assert arr.ndim == 3 and arr.shape[2] == 3, pid
    # §§55/59/61: all captions are real post-save amounts with % — no "est.".
    for pid, v in w._mini_amount.items():
        assert any(u in v for u in ("B", "KB", "MB")), (pid, v)
        assert not v.startswith("est."), (pid, v)
        assert "%" in v, (pid, v)


def test_pure_job_helpers():
    import numpy as np
    from pdf_minify.ui_qt.jobs import frame_view
    assert cpu_cap() >= 1
    page = np.full((60, 60, 3), 123, dtype=np.uint8)
    frame = frame_view([page], 100, 100, 24, 1, (0, 0, 100, 100))
    assert frame.shape == (150, 150, 3)
    assert (frame == 123).all()


def test_threshold_slider_only_for_simple(tmp_path):
    """Designer §65: T feeds Simple only — disabled (not lying) elsewhere."""
    w = MainWindow(str(_three_pages(str(tmp_path))))
    from pdf_minify.core import presets
    w.preset.setCurrentIndex(w.preset.findData("bw-otsu"))
    assert not w.slider.isEnabled()  # otsu computes its own threshold
    w.strategy.setCurrentText("simple")
    assert w.slider.isEnabled()
    w.strategy.setCurrentText("sauvola")
    assert not w.slider.isEnabled()


def test_lossless_checkbox_states(tmp_path, monkeypatch):
    """Designer §100: choice only for JPX; grey + fixed everywhere else."""
    from pdf_minify.core import presets
    w = MainWindow(str(_three_pages(str(tmp_path))))
    monkeypatch.setattr(w, "_ask_unsaved_filter", lambda pid: "discard")
    ids = [p["id"] for p in presets.PRESETS]
    w.preset.setCurrentIndex(w.preset.findData("bw-otsu"))
    assert w.lossless_box.isChecked() and not w.lossless_box.isEnabled()
    w.preset.setCurrentIndex(w.preset.findData("color-j2k"))
    assert w.lossless_box.isEnabled() and not w.lossless_box.isChecked()
    w.lossless_box.setChecked(True)
    assert w.lossless_box.isChecked()
    w.preset.setCurrentIndex(w.preset.findData("color-max"))
    assert not w.lossless_box.isChecked() and not w.lossless_box.isEnabled()
    w.preset.setCurrentIndex(w.preset.findData("color-i64"))
    assert w.lossless_box.isChecked() and not w.lossless_box.isEnabled()


def test_recompute_never_blanks_amounts(tmp_path):
    """Designer §106: stale-while-revalidate — a recompute keeps known
    amounts on screen (bars signal the work); only a new file clears."""
    w = MainWindow(str(_three_pages(str(tmp_path))))
    held = {pid: f"{i}KB ({i}%)" for i, pid in enumerate(w._strip_ids)}
    w._mini_amount.update(held)
    w._reframe_minis()
    assert w._mini_amount == held


def test_filter_set_covers_every_preset(tmp_path):
    """Every filter observes its real saved file, including PDF overhead."""
    from pdf_minify.core import presets
    from pdf_minify.core.recipes import preset_spec
    from pdf_minify.ui_qt.artifacts import build_artifact
    src = str(_three_pages(str(tmp_path)))
    for p in presets.PRESETS:
        if p["mode"] == "passthrough":
            continue
        directory = tmp_path / p["id"]
        directory.mkdir()
        result = build_artifact(src, preset_spec(p), str(directory))
        assert result.nbytes == os.path.getsize(result.pdf_path) > 0, p["id"]
        assert len(result.pages) == 3
        for page in result.pages:
            assert page.ndim == 3 and page.shape[2] == 3, p["id"]
        with fitz.open(result.pdf_path) as filtered:
            assert filtered.page_count == 3
            assert bool(filtered[0].get_text()) != bool(
                p["mode"] == "bw" and p["params"].get("force_raster"))
        result.close_pages()


def test_colors_slider_only_for_indexed(tmp_path):
    """Designer §67: Colors feeds Indexed only — disabled elsewhere."""
    from pdf_minify.core import presets
    w = MainWindow(str(_three_pages(str(tmp_path))))
    w.preset.setCurrentIndex(w.preset.findData("color-i64"))
    assert w.colors.isEnabled()
    assert w.colors.value() == 64
    w.preset.setCurrentIndex(w.preset.findData("bw-otsu"))
    assert not w.colors.isEnabled()
    w.colors.setValue(16)
    w.preset.setCurrentIndex(w.preset.findData("color-p16"))
    assert w.colors.value() == 16  # preset default lands on switch


def test_zoom_actions_have_real_icons():
    """Designer §197: standard zoom icons remain available without a theme."""
    from pdf_minify.ui_qt.app import MainWindow as _MW
    w = _MW(None)
    for act in (w.zoom_in_act, w.zoom_out_act):
        assert not act.icon().isNull()
        assert not act.icon().pixmap(16, 16).isNull()


def test_action_icon_refresh_preserves_filter_and_processing(tmp_path, monkeypatch):
    """§197: theme/palette changes are chrome-only, never filter edits/jobs."""
    from PySide6.QtCore import QEvent, QSize
    from PySide6.QtGui import QColor, QPalette
    w = MainWindow(str(_three_pages(str(tmp_path))))
    _wait_job(w)
    targets = (w.revert_btn, w.rename_btn, w.copy_btn, w.keep_btn,
               w.save_act, w.cancel_act, w.zoom_out_act, w.zoom_in_act)
    assert len(w._action_icons._targets) == len(targets)
    assert {name for _, name, _ in w._action_icons._targets} == {
        "document-revert", "edit-rename", "edit-copy", "document-save",
        "process-stop", "zoom-out", "zoom-in"}
    before = (w.preset.currentData(), w.filters.currentRow(), w._active_pid,
              dict(w._saved_specs), dict(w._draft_specs), w._gen,
              dict(w._artifacts.results), w._shown_preview_key,
              [target.isEnabled() for target in targets])
    started = []
    monkeypatch.setattr(w._artifacts, "start", lambda *a, **kw: started.append(a))
    palette = QPalette(w.palette())
    palette.setColor(QPalette.Window, QColor("#232629"))
    palette.setColor(QPalette.WindowText, QColor("#fcfcfc"))
    w.setPalette(palette)
    QApplication.sendEvent(w, QEvent(QEvent.ThemeChange))
    _app.processEvents()
    after = (w.preset.currentData(), w.filters.currentRow(), w._active_pid,
             dict(w._saved_specs), dict(w._draft_specs), w._gen,
             dict(w._artifacts.results), w._shown_preview_key,
             [target.isEnabled() for target in targets])
    assert after == before and not started
    assert not w._preview_timer.isActive() and not w._artifacts.pending
    for target in targets:
        assert not target.icon().isNull()
    for button in (w.revert_btn, w.rename_btn, w.copy_btn, w.keep_btn):
        assert button.iconSize() == QSize(20, 20)


def test_icon_lab_menu_reuses_window_without_filter_or_settings_changes(tmp_path, monkeypatch):
    from PySide6.QtCore import QSettings
    w = MainWindow(str(_three_pages(str(tmp_path))))
    _wait_job(w)
    settings = QSettings("pdf-minify", "pdf-minify")
    settings_before = {key: settings.value(key) for key in settings.allKeys()}
    before = (w._gen, w._active_pid, w.filters.currentRow(), w.preset.currentData(),
              dict(w._saved_specs), dict(w._draft_specs), dict(w._artifacts.results),
              [target.icon().cacheKey() for target, _, _ in w._action_icons._targets])
    started = []
    monkeypatch.setattr(w._artifacts, "start", lambda *a, **kw: started.append(a))
    assert w._icon_lab is None
    view = next(action.menu() for action in w.menuBar().actions() if action.text() == "&View")
    assert w.icon_lab_act in view.actions()  # direct, not hidden in Widget lab
    w.icon_lab_act.trigger()
    lab = w._icon_lab
    assert lab.isVisible() and lab.parent() is w
    lab.choices["N-REV-02"].setChecked(True)
    lab.choices["O-REN-01"].setChecked(True)
    lab.background.setCurrentIndex(2)
    lab.close()
    w.icon_lab_act.trigger()
    assert w._icon_lab is lab and lab.isVisible()
    assert lab.choice_text() == "Revert Changes: N-REV-02\nRename Filter: O-REN-01"
    after = (w._gen, w._active_pid, w.filters.currentRow(), w.preset.currentData(),
             dict(w._saved_specs), dict(w._draft_specs), dict(w._artifacts.results),
             [target.icon().cacheKey() for target, _, _ in w._action_icons._targets])
    assert after == before and not started
    assert {key: settings.value(key) for key in settings.allKeys()} == settings_before
    assert not w._preview_timer.isActive() and not w._artifacts.pending
    lab.close()


def test_details_codec_first_for_all_modes():
    """Designer §82: Codec opens the details in every mode, same sequence."""
    from pdf_minify.core import presets
    w = MainWindow(None)
    for p in presets.PRESETS:
        w.preset.setCurrentIndex(w.preset.findData(p["id"]))
        first = w.details.text().splitlines()[0]
        assert first.startswith("Codec:"), (p["id"], first)


def test_preset_owns_its_dpi(tmp_path):
    """Designer §§83/85: one DPI — presets seed the shared combo, which rules."""
    from pdf_minify.core import presets
    w = MainWindow(str(_three_pages(str(tmp_path))))
    ids = [p["id"] for p in presets.PRESETS]
    w.preset.setCurrentIndex(w.preset.findData("bw-fast"))
    assert w.dpi.currentData() == 300 and w.dpi.isEnabled()
    w.preset.setCurrentIndex(w.preset.findData("color-j2k"))
    assert w.dpi.isEnabled()  # the single DPI feeds every mode
    assert w.dpi.currentData() == 300  # all built-in output defaults are uniform (§225)
    w.preset.setCurrentIndex(w.preset.findData("bw-otsu"))
    assert w.dpi.currentData() == 300 and w.dpi.isEnabled()


def test_zoom_combo_two_way(tmp_path):
    """Designer §86: preset pick, typed number, and live sync all work."""
    from pdf_minify.core import presets
    w = MainWindow(str(_three_pages(str(tmp_path))))
    w.zoom_combo.setCurrentIndex(5)  # 150%
    w._zoom_combo_chosen(5)
    assert abs(w.before._zoom - 1.5) < 1e-9
    assert w.after._zoom == w.before._zoom
    w.zoom_combo.setCurrentText("42")
    w._zoom_combo_chosen()
    assert abs(w.before._zoom - 0.42) < 1e-9
    w.before.set_zoom(2.0)
    w._update_zoom_control()
    assert w.zoom_combo.currentText() == "200%"


def test_right_pane_zoom_reframes_minis(tmp_path):
    """Designer §92: zooming the RIGHT pane notifies, and the trailing
    debounce reframes minis to the last view (no stuck frames)."""
    import time
    w = MainWindow(str(_three_pages(str(tmp_path))))
    _wait_job(w)
    pid = w._strip_ids[0]
    before = w._mini_view[pid].tobytes()
    w.after.set_zoom(w.after._zoom * 2.0)
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < 5:
        _app.processEvents()
        time.sleep(0.05)
        if w._mini_view[pid].tobytes() != before:
            break
    assert w._mini_view[pid].tobytes() != before


def test_close_mid_processing_is_safe(tmp_path):
    """Designer §94: closing while workers run must never crash."""
    import time
    w = MainWindow(str(_three_pages(str(tmp_path))))
    _app.processEvents()
    assert w._artifacts.pending
    w.close()  # must not raise, hang, or abort
    t0 = time.perf_counter()
    while any(not j.isFinished() for j in list(w._jobs)):
        assert time.perf_counter() - t0 < 60, "worker did not stop"
        _app.processEvents()
        time.sleep(0.05)
    _app.processEvents()


def test_filter_progress_weights_cost(tmp_path):
    """Designer §§89/95: bars start at 0, minis weigh ~15%, amounts ~85%."""
    from pdf_minify.ui_qt.app import filter_progress
    assert filter_progress(0, 7, 0, 7) == 0.0
    first_mini = filter_progress(1, 7, 0, 7)
    assert 0.0 < first_mini < 0.2, first_mini  # never near half
    assert filter_progress(7, 7, 0, 7) < 0.5
    assert filter_progress(7, 7, 7, 7) == 1.0
    assert filter_progress(0, 0, 0, 0) == 1.0
    assert filter_progress(0, 0, 3, 7) == 3 / 7


def _render_progress_cell(w, row=0, selected=False):
    from PySide6.QtCore import QRect
    from PySide6.QtGui import QImage, QPainter, QPixmap
    from PySide6.QtWidgets import QStyle, QStyleOptionViewItem
    v = w.filters
    scale = v.devicePixelRatioF()
    pix = QPixmap(*(round(n*scale) for n in STRIP_ICON))
    pix.setDevicePixelRatio(scale)
    option = QStyleOptionViewItem()
    option.initFrom(v)
    option.rect = QRect(0, 0, *STRIP_ICON)
    if selected:
        option.state |= QStyle.State_Selected
    else:
        option.state &= ~QStyle.State_Selected
    painter = QPainter(pix)
    v.itemDelegate().paint(painter, option, v.model().index(row, 0))
    painter.end()
    return pix.toImage().convertToFormat(QImage.Format_ARGB32), scale


def _device_rect(rect, scale):
    from PySide6.QtCore import QRect
    return QRect(round(rect.x()*scale), round(rect.y()*scale),
                 round(rect.width()*scale), round(rect.height()*scale))


def _native_progress_pixels(w, fraction, size, scale):
    """Actual QProgressBar paintEvent, not a second custom progress drawing."""
    from PySide6.QtCore import QRect, Qt
    from PySide6.QtGui import QFont, QImage, QPainter, QPixmap, QRegion
    from PySide6.QtWidgets import QProgressBar, QWidget
    native = QProgressBar(w)
    reference = w.progress
    native.setStyle(reference.style())
    native.setPalette(reference.palette())
    font = QFont(reference.font())
    if font.pixelSize() > 0:
        font.setPixelSize(round(font.pixelSize()*1.25))
    else:
        font.setPointSizeF(font.pointSizeF()*1.25)
    native.setFont(font)
    native.setLocale(reference.locale())
    native.setLayoutDirection(reference.layoutDirection())
    native.setEnabled(reference.isEnabled())
    native.setFormat(reference.format())
    native.setAlignment(reference.alignment())
    native.setTextVisible(reference.isTextVisible())
    native.setInvertedAppearance(reference.invertedAppearance())
    native.setRange(0, 10_000)
    native.setValue(max(0, min(9999, int(fraction*10_000))))
    native.resize(size)
    bar, _ = w.filters.itemDelegate().progress_rects(QRect(0, 0, *STRIP_ICON))
    pix = QPixmap(*(round(n*scale) for n in STRIP_ICON))
    pix.setDevicePixelRatio(scale)
    pix.fill(Qt.white)
    painter = QPainter(pix)
    # Keep the explicitly requested white backing under native rounded corners.
    native.render(painter, bar.topLeft(), QRegion(), QWidget.DrawChildren)
    painter.end()
    native.deleteLater()
    return pix.toImage().convertToFormat(QImage.Format_ARGB32).copy(_device_rect(bar, scale))


@pytest.mark.parametrize("style_name", ["Fusion", "Windows"])
@pytest.mark.parametrize("dark", [False, True])
@pytest.mark.parametrize("selected", [False, True])
@pytest.mark.parametrize("fraction", [0.0, .375, .9999])
def test_mini_progress_matches_native_reserved_width_with_highlight_padding(style_name, dark, selected, fraction):
    """§§198/199: 1.25× native bar, full-frame center, no plate padding."""
    import numpy as np
    from PySide6.QtCore import QRect, Qt
    from PySide6.QtGui import QColor, QPalette
    from PySide6.QtWidgets import QStyleFactory
    from pdf_minify.ui_qt.app import FILTER_PROGRESS_ROLE, STRIP_WIDTH, STRIP_PADDING
    w = MainWindow()
    style = QStyleFactory.create(style_name)
    assert style is not None
    style.setParent(w.progress)
    w.progress.setStyle(style)
    palette = w.progress.palette()
    if dark:
        for role, color in ((QPalette.Window, "#303030"), (QPalette.Base, "#181818"),
                            (QPalette.Button, "#303030"), (QPalette.Text, "#ffffff"),
                            (QPalette.WindowText, "#ffffff"), (QPalette.ButtonText, "#ffffff")):
            palette.setColor(role, QColor(color))
    w.progress.setPalette(palette)
    pid = w._strip_ids[0]
    y, x = np.indices((104, 120))
    w._mini_view[pid] = np.stack((x*2, y*2, (x+y) % 256), 2).astype(np.uint8)
    w._mini_amount[pid] = "64KB (20%)"
    w._filter_prog[pid] = fraction
    w._paint_strip_item(pid)
    assert w.filters.item(0).data(FILTER_PROGRESS_ROLE) == fraction
    value, limits = w.progress.value(), (w.progress.minimum(), w.progress.maximum())
    original_font = w.progress.font()
    actual, scale = _render_progress_cell(w, selected=selected)
    bar, backing = w.filters.itemDelegate().progress_rects(QRect(0, 0, *STRIP_ICON))
    assert bar.left() == backing.left() == STRIP_PADDING
    assert bar.right() == backing.right() == STRIP_WIDTH-STRIP_PADDING-1
    assert bar.width() == backing.width() == STRIP_WIDTH-2*STRIP_PADDING > STRIP_PREVIEW_RECT.width()
    assert bar.height() == round(w.progress.sizeHint().height()*1.25)
    assert bar.top() == (STRIP_ICON[1]-bar.height())//2
    assert bar.center().y() == QRect(0, 0, *STRIP_ICON).center().y()
    assert bar.center().y() != STRIP_PREVIEW_RECT.center().y()
    assert backing == bar
    # Both side margins must preserve the whole ordinary item treatment,
    # including its selected highlight. No white padding above/below the bar.
    item = w.filters.item(0)
    item.setData(FILTER_PROGRESS_ROLE, 1.)
    unobstructed, _ = _render_progress_cell(w, selected=selected)
    item.setData(FILTER_PROGRESS_ROLE, fraction)
    for left in (0, STRIP_WIDTH-STRIP_PADDING):
        margin = _device_rect(QRect(left, backing.top(), STRIP_PADDING, backing.height()), scale)
        assert actual.copy(margin) == unobstructed.copy(margin)
        assert actual.pixelColor(margin.left(), round(bar.top()*scale)) != Qt.white
    for top in (bar.top()-1, bar.bottom()+1):
        adjacent = _device_rect(QRect(0, top, STRIP_WIDTH, 1), scale)
        assert actual.copy(adjacent) == unobstructed.copy(adjacent)
    # Layout/scroll origins must not alter either side's logical inset.
    for dx, dy in ((150, 9), (-37, 0)):
        shifted = w.filters.itemDelegate().progress_rects(QRect(dx, dy, *STRIP_ICON))
        assert shifted == (bar.translated(dx, dy), backing.translated(dx, dy))
    expected = _native_progress_pixels(w, fraction, bar.size(), scale)
    painted = actual.copy(_device_rect(bar, scale))
    differences = [(x, y, painted.pixelColor(x, y).name(), expected.pixelColor(x, y).name())
                   for y in range(expected.height()) for x in range(expected.width())
                   if painted.pixelColor(x, y) != expected.pixelColor(x, y)]
    assert painted == expected, differences[:12]
    assert w.progress.value() == value and limits == (w.progress.minimum(), w.progress.maximum())
    assert w.progress.font() == original_font
    assert not w.filters.itemDelegate()._progress_template.isVisible()


def test_mini_progress_model_update_needs_no_icon_rebuild_or_filtering(monkeypatch):
    import numpy as np
    from pdf_minify.ui_qt.app import FILTER_PROGRESS_ROLE
    w = MainWindow()
    pid = w._strip_ids[0]
    w._mini_view[pid] = np.zeros((104, 120, 3), dtype=np.uint8)
    w._mini_amount[pid] = "64KB (20%)"
    w._filter_prog[pid] = 0.0
    w._paint_strip_item(pid)
    item = w.filters.item(0)
    key = item.icon().cacheKey()
    before, _ = _render_progress_cell(w)
    def forbidden(*args):
        pytest.fail("Progress paint must not reprocess or rebuild cached image content")
    monkeypatch.setattr(w, "_paint_strip_item", forbidden)
    monkeypatch.setattr(w, "_dispatch_filters", forbidden)
    item.setData(FILTER_PROGRESS_ROLE, .55)
    after, _ = _render_progress_cell(w)
    assert before != after and item.icon().cacheKey() == key
    assert not w._jobs and not w._artifacts.pending


@pytest.mark.parametrize("progress", [0., .375, .9999, 1.])
@pytest.mark.parametrize("cached", [False, True])
def test_pending_mini_uses_progress_not_working_labels(monkeypatch, progress, cached):
    """§195: only real metadata, no placeholder text or missing-image paint."""
    import numpy as np
    from PySide6.QtCore import QRect
    from PySide6.QtGui import QPainter
    from pdf_minify.ui_qt.app import FILTER_PROGRESS_ROLE
    w = MainWindow()
    pid = w._strip_ids[0]
    if cached:
        w._mini_view[pid] = np.zeros((104, 120, 3), dtype=np.uint8)
        w._mini_amount[pid] = "64KB (20%)"
    w._filter_prog[pid] = progress
    texts = []
    draw = QPainter.drawText
    def observe(painter, *args):
        texts.extend(arg for arg in args if isinstance(arg, str))
        return draw(painter, *args)
    monkeypatch.setattr(QPainter, "drawText", observe)
    w._paint_strip_item(pid)
    assert not any(word in text.lower() for text in texts
                   for word in ("working", "sizing", "queued"))
    assert ("64KB (20%)" in texts) == cached
    assert w.filters.item(0).data(FILTER_PROGRESS_ROLE) == progress
    if not cached:
        image = w.filters.item(0).icon().pixmap(*STRIP_ICON).toImage()
        for rect in (STRIP_PREVIEW_RECT, STRIP_AMOUNT_RECT):
            assert all(image.pixelColor(x, y).alpha() == 0
                       for y in range(rect.top(), rect.bottom()+1)
                       for x in range(rect.left(), rect.right()+1))
    before, _ = _render_progress_cell(w)
    bar, _ = w.filters.itemDelegate().progress_rects(QRect(0, 0, *STRIP_ICON))
    assert bar.center().y() == QRect(0, 0, *STRIP_ICON).center().y()
    assert not before.isNull() and not w._jobs and not w._artifacts.pending


def test_completed_mini_hides_bar_and_backing_without_changing_geometry():
    import numpy as np
    from PySide6.QtCore import QRect, Qt
    from pdf_minify.ui_qt.app import FILTER_PROGRESS_ROLE
    w = MainWindow()
    pid = w._strip_ids[0]
    w._mini_view[pid] = np.zeros((104, 120, 3), dtype=np.uint8)
    w._filter_prog[pid] = .5
    w._paint_strip_item(pid)
    before, scale = _render_progress_cell(w)
    _, backing = w.filters.itemDelegate().progress_rects(QRect(0, 0, *STRIP_ICON))
    w.filters.item(0).setData(FILTER_PROGRESS_ROLE, 1.0)
    after, _ = _render_progress_cell(w)
    x, y = round(STRIP_PREVIEW_RECT.center().x()*scale), round(backing.top()*scale)
    assert before.pixelColor(x, y) != after.pixelColor(x, y)
    assert after.pixelColor(x, y) == Qt.black
    for top in (backing.top()-1, backing.bottom()+1):
        adjacent = _device_rect(QRect(0, top, STRIP_ICON[0], 1), scale)
        assert before.copy(adjacent) == after.copy(adjacent)
    assert before.size() == after.size()
    assert w.filters.itemDelegate().sizeHint(None, None).toTuple() == STRIP_ICON


@pytest.mark.parametrize("font_units", ["points", "pixels"])
def test_mini_progress_observes_live_font_locale_direction_and_palette(font_units):
    import numpy as np
    from PySide6.QtCore import QLocale, QRect, Qt
    from PySide6.QtGui import QColor, QFont, QPalette
    w = MainWindow()
    pid = w._strip_ids[0]
    w._mini_view[pid] = np.zeros((104, 120, 3), dtype=np.uint8)
    w._filter_prog[pid] = .375
    w._paint_strip_item(pid)
    first, scale = _render_progress_cell(w, selected=True)
    small, _ = w.filters.itemDelegate().progress_rects(QRect(0, 0, *STRIP_ICON))
    font = QFont(w.progress.font())
    if font_units == "pixels":
        font.setPixelSize(23)
    else:
        font.setPointSizeF(font.pointSizeF()+5)
    w.progress.setFont(font)
    w.progress.setLocale(QLocale("ar_EG"))
    w.progress.setLayoutDirection(Qt.RightToLeft)
    palette = w.progress.palette()
    palette.setColor(QPalette.Highlight, QColor("#7b2cbf"))
    w.progress.setPalette(palette)
    actual, _ = _render_progress_cell(w, selected=True)
    bar, _ = w.filters.itemDelegate().progress_rects(QRect(0, 0, *STRIP_ICON))
    assert bar.height() > small.height() and actual != first
    rendered_font = w.filters.itemDelegate()._progress_template.font()
    if font_units == "pixels":
        assert rendered_font.pixelSize() == round(font.pixelSize()*1.25)
    else:
        assert rendered_font.pointSizeF() == font.pointSizeF()*1.25
    painted = actual.copy(_device_rect(bar, scale))
    expected = _native_progress_pixels(w, .375, bar.size(), scale)
    if painted != expected:
        os.makedirs(".tmp", exist_ok=True)
        painted.save(f".tmp/mini-progress-font-{font_units}-{scale:g}x-actual.png")
        expected.save(f".tmp/mini-progress-font-{font_units}-{scale:g}x-expected.png")
    differences = [(x, y, painted.pixelColor(x, y).name(), expected.pixelColor(x, y).name())
                   for y in range(expected.height()) for x in range(expected.width())
                   if painted.pixelColor(x, y) != expected.pixelColor(x, y)]
    assert painted == expected, differences[:12]


@pytest.mark.parametrize("cell_height", [66, 162, 180])
def test_mini_progress_uses_actual_full_frame_height(cell_height):
    from PySide6.QtCore import QRect
    from PySide6.QtGui import QFont
    w = MainWindow()
    font = QFont(w.progress.font())
    font.setPixelSize(48)
    w.progress.setFont(font)
    cell = QRect(-37, 19, STRIP_ICON[0], cell_height)
    bar, backing = w.filters.itemDelegate().progress_rects(cell)
    height = min(round(w.progress.sizeHint().height()*1.25), cell_height-2*STRIP_PADDING)
    assert bar == backing == QRect(cell.left()+STRIP_PADDING,
                                   cell.top()+(cell.height()-height)//2,
                                   cell.width()-2*STRIP_PADDING, height)
    assert abs(bar.center().y()-cell.center().y()) <= 1
    assert cell.adjusted(STRIP_PADDING, STRIP_PADDING, -STRIP_PADDING, -STRIP_PADDING).contains(bar)


def test_mini_progress_ghost_keeps_native_pixels_and_uniform_opacity():
    import numpy as np
    from PySide6.QtCore import QRect
    from PySide6.QtGui import QImage
    w = MainWindow()
    pid = w._strip_ids[0]
    w._mini_view[pid] = np.zeros((104, 120, 3), dtype=np.uint8)
    w._filter_prog[pid] = .375
    w._paint_strip_item(pid)
    selected, scale = _render_progress_cell(w, selected=True)
    source = w.filters._drag_base_pixmap(0).toImage().convertToFormat(QImage.Format_ARGB32)
    assert source == selected
    bar, _ = w.filters.itemDelegate().progress_rects(QRect(0, 0, *STRIP_ICON))
    assert source.copy(_device_rect(bar, scale)) == _native_progress_pixels(w, .375, bar.size(), scale)
    ghost = w.filters._drag_pixmap(0).toImage()
    expected_alpha = round(255*w.filters.GHOST_OPACITY)
    assert all(abs(ghost.pixelColor(x, y).alpha()-expected_alpha) <= 1
               for y in range(0, ghost.height(), 7) for x in range(0, ghost.width(), 7))
    assert not w._jobs and not w._artifacts.pending


@pytest.mark.parametrize("mode", ["side-h", "stack-v"])
@pytest.mark.parametrize("size", [(1100, 650), (640, 600), (1600, 900)])
def test_main_regions_share_one_padding_policy_and_no_strip_title(mode, size, monkeypatch):
    """§§188/192: actual frame/header edges and one shared composition."""
    from PySide6.QtCore import QPoint, QRect
    from PySide6.QtWidgets import QLabel
    from pdf_minify.ui_qt.layout import UI_PADDING, PaneBlock, PreviewPair
    w = MainWindow()
    def forbidden(*args):
        pytest.fail("Layout/view changes must not dispatch PDF processing")
    monkeypatch.setattr(w, "_dispatch_filters", forbidden)
    w.set_main_mode(mode)
    w.resize(*size)
    w.show()
    _app.processEvents()
    root = w.centralWidget()
    def rect(widget):
        return QRect(widget.mapTo(root, QPoint()), widget.size())
    split, strip = rect(w.panel_split), rect(w.filters)
    before, after, panel = rect(w.before), rect(w.after), rect(w.panelScroll)
    assert isinstance(w.preview_block, PreviewPair)
    assert root.layout().count() == 2
    assert root.layout().itemAt(0).widget() is w.panel_split
    assert root.layout().itemAt(1).widget() is w.filters
    assert not any(label.text().startswith("Filters (left stays baseline") for label in root.findChildren(QLabel))
    assert w.filters.accessibleName() == "Filters"
    assert split.left() == strip.left() == UI_PADDING
    assert root.rect().right()-split.right() == root.rect().right()-strip.right() == UI_PADDING
    assert split.top() == UI_PADDING
    assert strip.top()-split.bottom()-1 == UI_PADDING
    assert root.rect().bottom()-strip.bottom() == UI_PADDING
    assert before.left() == split.left() and panel.right() == split.right()
    assert after.bottom() == panel.bottom() == split.bottom()
    headings = [rect(header) for header in (w.beforeHeader, w.afterHeader, w.configurationHeader)]
    assert w.configurationHeader.text() == w.configurationHeader.toolTip() == "Configuration"
    assert rect(w.configurationHeader).top() == rect(w.beforeHeader).top() == split.top()
    assert all(heading.height() == headings[0].height() for heading in headings)
    assert panel.top()-rect(w.configurationHeader).bottom()-1 == UI_PADDING
    assert w.panel_split.widget(1) is w.configuration_block
    assert w.panel_split.handle(1).width() == UI_PADDING
    pane0, pane1 = (rect(w.panes.itemAt(i).widget()) for i in range(2))
    if mode == "side-h":
        assert before.bottom() == after.bottom()
        assert before.top() == after.top() == panel.top()
        assert all(heading.top() == split.top() for heading in headings)
        assert after.left()-before.right()-1 == panel.left()-after.right()-1 == UI_PADDING
        assert abs(before.width()-after.width()) <= 1
    else:
        assert before.left() == after.left() and before.right() == after.right()
        assert pane1.top()-pane0.bottom()-1 == UI_PADDING
        assert panel.left()-after.right()-1 == UI_PADDING
        assert abs(pane0.height()-pane1.height()) <= 1
    for content in (w.before, w.after, w.panelScroll):
        assert isinstance(content.parentWidget(), PaneBlock)
        assert content.parentWidget().layout().itemAt(1).widget() is content
    for layout in (w.panes, w.before.parentWidget().layout(), w.after.parentWidget().layout(),
                   w.configuration_block.layout()):
        assert layout.getContentsMargins() == (0, 0, 0, 0)
        assert layout.spacing() == UI_PADDING
    form = w.panelScroll.widget().layout()
    assert form.getContentsMargins() == (UI_PADDING,)*4 and form.spacing() == UI_PADDING
    assert not w._jobs and not w._artifacts.pending


def test_panes_equal_no_splitter(tmp_path):
    """Designer §107: no splitter — fixed equal layout, widths always match."""
    w = MainWindow(str(_three_pages(str(tmp_path))))
    w.resize(1100, 650)
    w.show()
    _app.processEvents()
    assert hasattr(w, "panes") and not hasattr(w, "split")
    assert abs(w.before.width() - w.after.width()) <= 2, \
        (w.before.width(), w.after.width())


def test_preset_strip_sync_by_id():
    import tempfile
    src = os.path.join(tempfile.mkdtemp(), "m.pdf")
    d = fitz.open()
    p = d.new_page(width=400, height=400)
    p.insert_text((50, 200), "Sync test")
    d.save(src)
    d.close()
    w = MainWindow(src)
    assert all(w.preset.itemData(i) != "orig" for i in range(w.preset.count()))
    assert w.preset.itemText(0).startswith("1. ")  # first strip filter
    w._filterstrip_chosen(0)  # first mini -> its preset
    from pdf_minify.core import presets
    assert w.preset.itemData(w.preset.currentIndex()) == w._strip_ids[0]
    assert presets.get(w._strip_ids[0])["mode"] != "passthrough"


def test_file_menu_and_single_panel(tmp_path):
    w = MainWindow(str(_three_pages(str(tmp_path))))
    names = [a.text() for a in w.menuBar().actions()]
    assert "&File" in names and "&View" in names
    assert w.before.page_count == 3  # baseline renders synchronously
    _wait_job(w)
    assert w.after.page_count == 3  # preview arrives via background job


def test_force_raster_per_filter(tmp_path):
    """Designer §§103/127: only bw-fast forces; preset switch syncs the box.
    ON = whole page into one image; OFF = text kept, images 1-bit in place."""
    from pdf_minify.core import presets
    w = MainWindow(str(_three_pages(str(tmp_path))))
    ids = [p["id"] for p in presets.PRESETS]
    forced = [p["id"] for p in presets.PRESETS
              if p["mode"] == "bw" and p["params"].get("force_raster")]
    assert forced == ["bw-fast"]
    w.preset.setCurrentIndex(w.preset.findData("bw-otsu"))
    assert not w.force_raster.isChecked()
    w.preset.setCurrentIndex(w.preset.findData("bw-fast"))
    assert w.force_raster.isChecked()


def test_zz_rename_and_copy_filter(tmp_path, monkeypatch):
    """Designer §109: rename + copy via naming popup, persisted. Last."""
    from PySide6.QtWidgets import QInputDialog
    from pdf_minify.core import presets
    w = MainWindow(str(_three_pages(str(tmp_path))))
    ids = [p["id"] for p in presets.PRESETS]
    n_combo, n_strip = w.preset.count(), w.filters.count()
    monkeypatch.setattr(QInputDialog, "getText",
                        staticmethod(lambda *a, **k: ("My Otsu", True)))
    w.preset.setCurrentIndex(w.preset.findData("bw-otsu"))
    w.rename_filter()
    assert presets.get("bw-otsu")["label"] == "My Otsu"
    assert w.preset.itemText(w.preset.currentIndex()).endswith("My Otsu")
    monkeypatch.setattr(QInputDialog, "getText",
                        staticmethod(lambda *a, **k: ("J2K copy", True)))
    w.preset.setCurrentIndex(w.preset.findData("color-j2k"))
    w.copy_filter()
    assert w.preset.count() == n_combo + 1
    assert w.filters.count() == n_strip + 1
    assert w._strip_ids[-1] not in ids
    assert presets.get(w._strip_ids[-1])["mode"] == "jpx"


def test_preview_reuse_and_panel_divider(tmp_path):
    """Designer §§107/115/117/149: selection consumes a prepared result; divider
    between the previews and the right panel drags (slider gone), and the
    two panes stay locked equal."""
    w = MainWindow(str(_three_pages(str(tmp_path))))
    _wait_job(w)
    artifact = w._artifacts.results[w._result_key(w._active_pid)]
    generation = w._gen
    w._dispatch_filters()
    assert w._gen == generation  # no preview-only filtering path anymore
    assert w._artifacts.results[w._result_key(w._active_pid)] is artifact
    assert not w.status.text().startswith("Rendering preview"), w.status.text()
    assert not hasattr(w, "pw_slider")  # slider removed, divider rules
    assert hasattr(w, "panel_split") and not hasattr(w, "split")
    from PySide6.QtCore import Qt as _Qt  # §118: squeezed panel scrolls
    assert w.panelScroll.horizontalScrollBarPolicy() == _Qt.ScrollBarAsNeeded
    w.resize(1100, 650)
    w.show()
    _app.processEvents()
    before = w.panel_split.sizes()
    assert len(before) == 2
    w.panel_split.setSizes([before[0] + 120, max(200, before[1] - 120)])
    _app.processEvents()
    assert w.panel_split.sizes() != before  # divider really moved
    assert abs(w.before.width() - w.after.width()) <= 2  # panes still equal
    assert not w.rename_btn.icon().isNull() and not w.copy_btn.icon().isNull()


def test_bw_details_state_follows_force(tmp_path):
    """Designer §§127/171: full-page raster vs native artwork + image canvas."""
    from pdf_minify.core import presets
    w = MainWindow(str(_three_pages(str(tmp_path))))
    ids = [p["id"] for p in presets.PRESETS]
    w.preset.setCurrentIndex(w.preset.findData("bw-otsu"))
    assert "text/vectors kept" in w.details.text()
    assert "BW image canvas" in w.details.text()
    assert "original stacking" in w.force_raster.toolTip()
    w.force_raster.setChecked(True)
    assert "full-page raster" in w.details.text()


def test_force_toggle_updates_only_active_filter(tmp_path):
    """Designer §127: toggling FFPR re-renders exactly one filter — the
    active one. Every other mini and amount stays byte-identical."""
    import time
    w = MainWindow(str(_three_pages(str(tmp_path))))
    _wait_job(w)
    before_est = dict(w._mini_amount)
    before_view = {pid: arr.tobytes() for pid, arr in w._mini_view.items()}
    active = w.preset.itemData(w.preset.currentIndex())
    assert not w.force_raster.isChecked()  # bw-otsu recipe: OFF
    w.force_raster.setChecked(True)
    t0 = time.perf_counter()
    while True:
        _app.processEvents()
        jobs_done = not w._artifacts.pending and not w._preview_timer.isActive()
        current_cached = w._result_key(w._active_pid) in w._artifacts.results
        if jobs_done and current_cached:
            break
        assert time.perf_counter() - t0 < 120, "jobs never went idle"
        time.sleep(0.05)
    _app.processEvents()
    for pid, txt in w._mini_amount.items():
        if pid != active:
            assert txt == before_est[pid], pid
    for pid, arr in w._mini_view.items():
        if pid != active:
            assert arr.tobytes() == before_view[pid], pid
    assert not w.status.text().startswith("Rendering"), w.status.text()


def test_unforced_preview_keeps_crisp_text(tmp_path):
    """§§127/149: rendered saved output preserves text when FFPR is OFF."""
    import numpy as np
    from pdf_minify.ui_qt.artifacts import build_artifact
    from pdf_minify.core.display import render_display_page
    src = str(_three_pages(str(tmp_path)))
    spec = {"mode": "bw", "dpi": 300, "strategy": "otsu", "t": 180,
            "force_raster": False}
    kept, flat = tmp_path / "kept", tmp_path / "flat"
    kept.mkdir()
    flat.mkdir()
    result = build_artifact(src, spec, str(kept))
    forced = build_artifact(src, dict(spec, force_raster=True), str(flat))
    with fitz.open(src) as doc:
        pix = render_display_page(doc[0], dpi=150)
        original = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, 3)
        assert np.array_equal(result.pages[0], original)
    with fitz.open(result.pdf_path) as doc:
        assert "Mini test" in doc[0].get_text()
    with fitz.open(forced.pdf_path) as doc:
        assert not doc[0].get_text() and doc[0].get_images()
    assert not np.array_equal(result.pages[0], forced.pages[0])
    result.close_pages()
    forced.close_pages()


def test_pane_headers_elide_with_tooltip(tmp_path):
    """Designer §124: overflowing pane titles elide; hover shows it all."""
    from pdf_minify.ui_qt.headers import PaneHeader
    w = MainWindow(str(_three_pages(str(tmp_path))))
    _wait_job(w)
    full = w.afterHeader.property("fullText")
    assert full and w.afterHeader.toolTip() == full
    lab = PaneHeader(full * 3)
    lab.resize(100, 20)
    assert lab.toolTip() == full * 3
    assert lab.text() == full * 3  # metadata/accessibility retain the full text
    assert lab.elided_text() != full * 3 and lab.elided_text().endswith("…")


@pytest.mark.parametrize("width", (640, 960))
def test_window_shrink_has_no_delayed_divider_drift(tmp_path, monkeypatch, width):
    """§166: text presentation cannot negotiate new minima on every reframe."""
    from PySide6.QtTest import QTest
    w = MainWindow(str(_three_pages(str(tmp_path))))
    w.resize(1920, 1000)
    w.show()
    _wait_job(w)
    QTest.qWait(300)
    prepared, generation = dict(w._artifacts.results), w._gen

    def forbidden(*args, **kwargs):
        pytest.fail("window resize must not start filter processing")

    monkeypatch.setattr(w._artifacts, "start", forbidden)
    started = time.monotonic()
    w.resize(width, 600)
    QTest.qWait(50)
    assert w.width() == width
    assert abs(w.before.width() - w.after.width()) <= 1
    allocated = (w.panel_split.sizes(), w.before.size(), w.after.size())
    horizontal = (w.panel_split.sizes(), w.before.width(), w.after.width())
    for _ in range(8):
        QTest.qWait(150)  # cross the real mini-reframe interval repeatedly
        assert (w.panel_split.sizes(), w.before.width(), w.after.width()) == horizontal
        current = (w.panel_split.sizes(), w.before.size(), w.after.size())
        if current != allocated:
            # Qt may publish the strip's newly needed native scrollbar after
            # 50ms. This is one bounded vertical settle, not divider feedback.
            # Match the <500ms contract measured by tools/resize_smoke.py.
            from PySide6.QtWidgets import QStyle
            assert time.monotonic()-started < .5
            extent = w.filters.style().pixelMetric(QStyle.PM_ScrollBarExtent)
            assert abs(current[1].height()-allocated[1].height()) == extent
            assert abs(current[2].height()-allocated[2].height()) == extent
            allocated = current
        assert abs(w.before.width() - w.after.width()) <= 1
    assert w._gen == generation and w._artifacts.results == prepared
    assert not w._artifacts.pending and not w._preview_timer.isActive()


def test_splitter_drag_elides_without_header_or_filter_updates(tmp_path, monkeypatch):
    """The header owns width-dependent presentation, not the view timer."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    w = MainWindow(str(_three_pages(str(tmp_path))))
    w.resize(1100, 650)
    w.show()
    _wait_job(w)
    QTest.qWait(300)
    full = w.afterHeader.text()
    prepared, generation = dict(w._artifacts.results), w._gen

    def forbidden(*args, **kwargs):
        pytest.fail("splitter drag may only change view/presentation")

    monkeypatch.setattr(w, "_update_pane_headers", forbidden)
    monkeypatch.setattr(w._artifacts, "start", forbidden)
    widths = []
    for position in (800, 450, 700):
        w.panel_split.moveSplitter(position, 1)
        QTest.qWait(250)
        widths.append(w.afterHeader.width())
        assert abs(w.before.width() - w.after.width()) <= 1
        assert w.afterHeader.text() == w.afterHeader.toolTip() == full
        assert w.afterHeader.elided_text() == w.afterHeader.fontMetrics().elidedText(
            full, Qt.ElideRight, w.afterHeader.contentsRect().width())
        assert not w.afterHeader.grab().isNull()
    assert len(set(widths)) == 3
    assert w._gen == generation and w._artifacts.results == prepared
    assert not w._artifacts.pending and not w._preview_timer.isActive()


def test_strip_reorder_syncs_combo_and_processing(tmp_path):
    """Designer §128: minis DnD-reorder; dropdown and processing follow;
    the selected filter always goes first."""
    from PySide6.QtCore import Qt as _Qt, QModelIndex as _MI
    w = MainWindow(str(_three_pages(str(tmp_path))))
    try:
        first = [w.filters.item(i).data(_Qt.UserRole) for i in range(w.filters.count())]
        assert first == w._strip_ids
        # Real model move (fires rowsMoved, like a framework drop does).
        assert w.filters.model().moveRow(_MI(), 0, _MI(), 3)
        _app.processEvents()
        expect = [w.filters.item(i).data(_Qt.UserRole)
                  for i in range(w.filters.count())]
        assert expect != first  # the row really moved
        assert w._strip_ids == expect
        combo = [w.preset.itemData(i) for i in range(w.preset.count())]
        assert combo == expect
        active = w.preset.itemData(w.preset.currentIndex())
        assert w._ordered_pids()[0] == active
        assert sorted(w._ordered_pids()) == sorted(expect)
        # Click through the reordered strip: row↔combo must agree, never
        # ping-pong (PRESETS-index mapping desyncs after reorder — crash).
        for row in (0, 2, 5):
            w._filterstrip_chosen(row)
            assert w.preset.itemData(w.preset.currentIndex()) == w._strip_ids[row]
            w.preset.setCurrentIndex(w.preset.findData(w._strip_ids[row]))
            assert w.filters.currentRow() == row
    finally:
        # Persisted order must not leak into other tests' combo indices.
        try:
            w._custom_store().remove("stripOrder")
        except Exception:  # noqa: BLE001
            pass


def test_strip_uses_standard_dnd(tmp_path):
    """Native MIME drag reorders data while the cells keep a static grid."""
    from PySide6.QtWidgets import QAbstractItemView as _AIV
    from PySide6.QtWidgets import QListView as _LV
    w = MainWindow(str(_three_pages(str(tmp_path))))
    v = w.filters
    assert v.dragDropMode() == _AIV.DragDrop
    assert "startDrag" in type(v).__dict__  # no parallel default copy/remove path
    assert not bool(v.property("showDropIndicator"))
    assert v.movement() == _LV.Static
    assert v.viewport().acceptDrops()


def test_strip_gap_bar_and_drop(tmp_path):
    """Designer §§128/139: hovering anywhere snaps to the nearest divider,
    a solid theme bar marks it, and the drop lands there with sync."""
    from PySide6.QtCore import Qt as _Qt, QPointF as _QP, QMimeData as _MD
    from PySide6.QtGui import (QDragMoveEvent as _DME, QDropEvent as _DE,
                               QDragEnterEvent as _DEE)
    from PySide6.QtWidgets import QApplication as _QA
    from PySide6.QtCore import QItemSelectionModel as _SM
    w = MainWindow(str(_three_pages(str(tmp_path))))
    w.resize(1100, 650)
    w.show()
    _app.processEvents()
    v, m = w.filters, w.filters.model()
    n = v.count()
    r2 = v.visualRect(m.index(2, 0))
    assert v._gap_at(r2.right() + 2) == 3  # nearest divider, not the item
    assert v._gap_at(-50) == 0 and v._gap_at(100000) == n  # both ends
    v._begin_drag(0, v.visualRect(m.index(0, 0)).center())
    mime = v._drag_mime
    en = _DEE(_QP(r2.right() + 2, 50), _Qt.MoveAction, mime,
              _Qt.LeftButton, _Qt.NoModifier)
    _QA.sendEvent(v.viewport(), en)
    assert en.isAccepted()
    mv = _DME(_QP(r2.right() + 2, 50), _Qt.MoveAction, mime,
              _Qt.LeftButton, _Qt.NoModifier)
    _QA.sendEvent(v.viewport(), mv)
    assert mv.isAccepted()
    assert v._drop_gap == 3
    assert v._drop_line is not None and v._drop_line.isVisible()
    from PySide6.QtGui import QPalette as _QPAL
    assert v._drop_line.palette().color(v._drop_line.backgroundRole()) == \
        v.palette().color(_QPAL.Highlight)  # solid theme bar, not hollow
    before = [v.item(i).data(_Qt.UserRole) for i in range(n)]
    try:
        v.setCurrentRow(0)
        v.selectionModel().select(m.index(0, 0), _SM.Select)
        dr = _DE(_QP(r2.right() + 2, 50), _Qt.MoveAction, mime,
                 _Qt.LeftButton, _Qt.NoModifier)
        _QA.sendEvent(v.viewport(), dr)
        _app.processEvents()
        assert dr.isAccepted()
        after = [v.item(i).data(_Qt.UserRole) for i in range(v.count())]
        assert after != before and w._strip_ids == after  # landed + synced
        assert v._drop_line.isHidden()  # bar gone after drop
    finally:
        v._end_drag()
        # Persisted order must not leak into other tests' combo indices.
        try:
            w._custom_store().remove("stripOrder")
        except Exception:  # noqa: BLE001
            pass


def test_control_rows_inline(tmp_path):
    """Designer §§128/203/205: compression/method/DPI/page-size share a line with
    labels instead of stacking above their controls."""
    from PySide6.QtWidgets import QLabel
    w = MainWindow(str(_three_pages(str(tmp_path))))
    w.resize(1100, 650)
    w.show()
    _app.processEvents()
    labels = {l.text().replace("&", ""): l for l in w.panelScroll.findChildren(QLabel)}
    for ctl, text in ((w.compression, "Image compression:"),
                      (w.stream_compression, "PDF streams:"),
                      (w.strategy, "Threshold method:"),
                      (w.dpi, "Raster DPI:"),
                      (w.page_size, "Page size:")):
        lab = labels[text]
        assert abs(lab.y() - ctl.y()) < lab.height(), (text, lab.y(), ctl.y())


def test_combos_fit_largest_item_with_tip(tmp_path):
    """Designer §130: dropdowns size to the largest item; hover shows it all
    (Qt clips narrow closed displays without ellipsis, so the minimum width
    carries the fit and the tooltip carries the text)."""
    w = MainWindow(str(_three_pages(str(tmp_path))))
    for combo in (w.preset, w.strategy, w.dpi, w.page_size):
        fm = combo.fontMetrics()
        widest = max(fm.horizontalAdvance(combo.itemText(i))
                     for i in range(combo.count()))
        assert combo.minimumWidth() >= widest, combo
        assert combo.toolTip() == combo.itemText(combo.currentIndex())


def test_clicking_preset_keeps_other_amounts(tmp_path):
    """Designer §131: clicking a mini (preset switch re-seeds the shared
    DPI combo) must not move any other filter's amount — estimates follow
    each filter's own recipe DPI, only the active filter follows the UI."""
    import time
    from pdf_minify.core import presets
    w = MainWindow(str(_three_pages(str(tmp_path))))
    _wait_job(w)
    before_est = dict(w._mini_amount)
    ids = [p["id"] for p in presets.PRESETS]
    w.preset.setCurrentIndex(w.preset.findData("bw-fast"))  # uniform 300dpi seed (§225)
    assert w.dpi.currentData() == 300
    t0 = time.perf_counter()
    while True:
        _app.processEvents()
        jobs_done = not w._artifacts.pending and not w._preview_timer.isActive()
        current_cached = w._result_key(w._active_pid) in w._artifacts.results
        if jobs_done and current_cached:
            break
        assert time.perf_counter() - t0 < 120, "jobs never went idle"
        time.sleep(0.05)
    _app.processEvents()
    for pid, txt in w._mini_amount.items():
        assert txt == before_est[pid], (pid, txt, before_est[pid])
    assert not w.status.text().startswith("Rendering"), w.status.text()


def test_filter_sequence_numbers_follow_order(tmp_path):
    """Designer §133: minis and dropdown both read `N. label` from the live
    strip order — renumbering follows reorder."""
    w = MainWindow(str(_three_pages(str(tmp_path))))
    for i, pid in enumerate(w._strip_ids):
        assert w._strip_label(pid).startswith(f"{i + 1}. "), pid
    combo = [w.preset.itemText(i) for i in range(w.preset.count())]
    assert combo == [w._strip_label(p) for p in w._strip_ids]
    try:
        from PySide6.QtCore import QModelIndex as _MI
        assert w.filters.model().moveRow(_MI(), 0, _MI(), 3)
        _app.processEvents()
        moved = w._strip_ids[2]
        assert w._strip_label(moved).startswith("3. ")
        combo2 = [w.preset.itemText(i) for i in range(w.preset.count())]
        assert combo2 == [w._strip_label(p) for p in w._strip_ids]
    finally:
        try:
            w._custom_store().remove("stripOrder")
        except Exception:  # noqa: BLE001
            pass


@pytest.mark.parametrize("state", ("ready", "pending", "queued"))
def test_drop_renumbers_visible_captions_without_content_refresh(state, monkeypatch):
    """§148: real caption pixels follow model moves, never processing arrivals.

    Freeze content updates after seeding per-filter results. Inspect the first
    viewport paint after forward/backward/no-op drops, without pumping events
    that could refresh an icon or trigger a job.
    """
    import numpy as np
    from PySide6.QtCore import QRect, Qt
    from PySide6.QtGui import QFont, QPainter, QPalette, QPixmap
    from pdf_minify.core import presets

    w = MainWindow()
    v = w.filters
    w.resize(1100, 650)
    w.show()
    _app.processEvents()
    v.setCurrentRow(1)
    for i, pid in enumerate(w._strip_ids):
        if state != "queued":
            w._mini_view[pid] = np.full((60, 70, 3), i * 20, dtype=np.uint8)
        w._filter_prog[pid] = 1.0 if state == "ready" else 0.35
        if state == "ready":
            w._mini_amount[pid] = f"{i + 1}KB ({i + 1}%)"
        w._paint_strip_item(pid)
    _app.processEvents()
    w._preview_timer.stop()
    w._reframe_timer.stop()
    content = dict(w._mini_view)
    amounts, progress = dict(w._mini_amount), dict(w._filter_prog)
    icons = {v.item(i).data(Qt.UserRole): v.item(i).icon().cacheKey()
             for i in range(v.count())}
    active = w.preset.currentData()

    def forbidden(*args):
        pytest.fail("A reorder must not refresh cached content or process the PDF")

    for method in ("_paint_strip_item", "_repaint_all_strip", "_reframe_minis",
                   "_dispatch_filters"):
        monkeypatch.setattr(w, method, forbidden)

    def check_caption_pixels():
        v.doItemsLayout()
        for row in range(5):  # these full cells are visible without scrolling
            rect = v.visualRect(v.model().index(row, 0))
            assert v.viewport().rect().contains(rect)
            actual = v.viewport().grab(rect).toImage()
            expected = QPixmap(*STRIP_ICON)
            expected.fill(v.palette().color(QPalette.Base))
            pt = QPainter(expected)
            font = QFont(v.font())
            font.setPointSize(max(7, font.pointSize() - 2))
            pt.setFont(font)
            pt.setPen(v.palette().color(QPalette.WindowText))
            pid = v.item(row).data(Qt.UserRole)
            pt.drawText(QRect(0, 116, 150, 13), Qt.AlignHCenter,
                        f"{row + 1}. {presets.get(pid)['label']}")
            if v.item(row).isSelected():
                wash = v.palette().color(QPalette.Highlight)
                wash.setAlphaF(0.35)
                pt.fillRect(expected.rect(), wash)
            pt.end()
            caption = QRect(0, 116, 150, 13)
            assert actual.copy(caption) == expected.toImage().copy(caption), (
                state, row, pid, "visible caption still contains the old number")
        assert [w.preset.itemText(i) for i in range(w.preset.count())] == [
            f"{i + 1}. {presets.get(pid)['label']}"
            for i, pid in enumerate(w._strip_ids)]
        assert w.preset.currentData() == active
        assert not w._preview_timer.isActive()
        assert not w._jobs and not w._artifacts.pending
        assert all(w._mini_view[pid] is arr for pid, arr in content.items())
        assert w._mini_amount == amounts and w._filter_prog == progress
        assert {v.item(i).data(Qt.UserRole): v.item(i).icon().cacheKey()
                for i in range(v.count())} == icons

    try:
        assert v._move_to_gap(4)  # row 1 -> row 3
        check_caption_pixels()
        assert v._move_to_gap(1)  # row 3 -> row 1
        check_caption_pixels()
        assert v._move_to_gap(2)  # adjacent gap: no reorder
        check_caption_pixels()
    finally:
        w._custom_store().remove("stripOrder")
        w.close()


def test_selected_mini_uses_theme_highlight(tmp_path):
    """Designer §134: mini icons carry transparent ground (theme selection
    shows through the whole area, caption included) — never baked white."""
    from PySide6.QtGui import QImage
    w = MainWindow(str(_three_pages(str(tmp_path))))
    _wait_job(w)
    active = w.preset.itemData(w.preset.currentIndex())
    other = next(p for p in w._strip_ids if p != active)
    w._paint_strip_item(active)
    w._paint_strip_item(other)
    for pid in (active, other):
        img = w.filters.item(w._strip_ids.index(pid)).icon().pixmap(
            *STRIP_ICON).toImage().convertToFormat(QImage.Format_ARGB32)
        trans = sum(1 for y in range(STRIP_ICON[1]) for x in range(STRIP_ICON[0])
                    if (img.pixel(x, y) >> 24) == 0)
        assert trans > 1000, (pid, trans)


def test_strip_never_scrolls_vertically(tmp_path):
    """Designer §96: no vertical scroll ever (bar hidden AND content
    locked) — wheel drives the horizontal bar; one exact-height row."""
    from PySide6.QtGui import QWheelEvent
    from PySide6.QtCore import QPoint, QPointF as _QPF, Qt as _Qt
    from PySide6.QtWidgets import QApplication as _QA
    w = MainWindow(str(_three_pages(str(tmp_path))))
    w.resize(1100, 650)
    w.show()
    _app.processEvents()
    v = w.filters
    m = v.model()
    r0 = v.visualRect(m.index(0, 0))
    assert r0.top() <= 1  # no white gap above
    assert r0.height() == STRIP_ICON[1]
    assert v.viewport().rect().contains(r0)
    assert v.verticalScrollBar().maximum() == 0
    hb = v.horizontalScrollBar()
    before = hb.value()
    ev = QWheelEvent(_QPF(100, 50), _QPF(100, 50), QPoint(0, 0), QPoint(0, -120),
                     _Qt.NoButton, _Qt.NoModifier, _Qt.ScrollPhase.NoScrollPhase, False)
    v.wheelEvent(ev)  # direct call: event routing is the framework's job
    _app.processEvents()
    assert hb.value() != before or hb.maximum() == 0  # wheel went horizontal
    assert v.verticalScrollBar().value() == 0


def test_selected_wash_covers_full_item(tmp_path):
    """Designer §134: the highlight wash covers the whole item rect —
    photo through caption — with zero baked chrome left in the icon."""
    from PySide6.QtGui import QImage, QPixmap, QPainter
    from PySide6.QtWidgets import QStyleOptionViewItem, QStyle
    w = MainWindow(str(_three_pages(str(tmp_path))))
    _wait_job(w)
    v = w.filters
    w._paint_strip_item(w._strip_ids[0])
    opt = QStyleOptionViewItem()
    opt.initFrom(v)
    opt.rect = v.visualRect(v.model().index(0, 0))
    opt.state |= QStyle.State_Selected
    from PySide6.QtCore import Qt as _Qt2
    pm = QPixmap(opt.rect.size())
    pm.fill(_Qt2.white)
    pt = QPainter(pm)
    v.itemDelegate().paint(pt, opt, v.model().index(0, 0))
    pt.end()
    img = pm.toImage().convertToFormat(QImage.Format_ARGB32)
    W, H = img.width(), img.height()

    def _blueish(px):
        r, g, b = (px >> 16) & 0xff, (px >> 8) & 0xff, px & 0xff
        return b > r + 20

    tinted = sum(1 for y in range(0, H, 4) for x in range(0, W, 8)
                 if _blueish(img.pixel(x, y)))
    assert tinted > (W // 8) * (H // 4) * 0.5, tinted  # wash spans everything
    # caption ink is theme window text (dark), never pale-on-pale
    from PySide6.QtGui import QPalette as _QPAL
    assert w.palette().color(_QPAL.WindowText).lightness() < 128


def test_drag_ghost_is_translucent(tmp_path):
    """Designer §§145/146: complete selected mini uses uniform 75% opacity.

    The live drag is painted into the window so this remains true on X11
    without a compositor; there must be no transparent/opaque dithering.
    """
    from PySide6.QtCore import QPoint
    from PySide6.QtGui import QImage
    from PySide6.QtTest import QTest
    w = MainWindow(str(_three_pages(str(tmp_path))))
    _wait_job(w)
    v = w.filters
    w.resize(1100, 650)
    w.show()
    v.setCurrentRow(0)
    # Artifact readiness predates resize/show. The current view's minis are
    # reframed by a separate timer; compare the same settled view, not an old
    # thumbnail with the new thumbnail arriving between two ghost captures.
    deadline = time.monotonic() + 90
    while True:
        _app.processEvents()
        if not w._reframe_timer.isActive():
            break
        assert time.monotonic() < deadline, "view reframing did not settle"
        QTest.qWait(10)
    item_rect = v.visualRect(v.model().index(0, 0))
    press = item_rect.topLeft() + QPoint(37, 61)
    assert v._drag_hotspot_for(0, press) == QPoint(37, 61)
    visible = item_rect.intersected(v.viewport().rect())
    selected_on_screen = v.viewport().grab(visible).toImage().convertToFormat(
        QImage.Format_ARGB32)
    base = v._drag_base_pixmap(0)
    base_img = base.toImage().convertToFormat(QImage.Format_ARGB32)
    W, H = base_img.width(), base_img.height()

    # The common delegate makes the complete ghost match the displayed
    # selection, including the bottom edge next to the scrollbar.
    offset = visible.topLeft() - item_rect.topLeft()
    for y in range(0, visible.height(), 7):
        for x in range(0, visible.width(), 7):
            assert base_img.pixelColor(x + offset.x(), y + offset.y()) == \
                selected_on_screen.pixelColor(x, y)
    assert base_img.pixelColor(5, H - 1) == base_img.pixelColor(5, 5)
    assert base_img.pixelColor(W - 6, H - 1) == base_img.pixelColor(W - 6, 5)

    # A partially scrolled source still produces the same complete mini;
    # there are no viewport-capture gaps to pad with white.
    # Cross the old race window deliberately. No pixel equality or alpha
    # checks are weakened, even if callbacks run between the captures.
    QTest.qWait(w._reframe_timer.interval() + 20)
    hb = v.horizontalScrollBar()
    hb.setValue(37)
    _app.processEvents()
    assert v.visualRect(v.model().index(0, 0)).left() < 0
    assert v._drag_base_pixmap(0).toImage().convertToFormat(QImage.Format_ARGB32) == base_img
    hb.setValue(0)
    _app.processEvents()

    # The ghost source is the exact selected-item treatment: the theme's
    # blue wash spans the whole rectangle, not merely the thumbnail.
    def _blueish(color):
        return color.blue() > color.red() + 20

    tinted = sum(1 for y in range(0, H, 4) for x in range(0, W, 8)
                 if _blueish(base_img.pixelColor(x, y)))
    assert tinted > (W // 8) * (H // 4) * 0.5, tinted

    ghost = v._drag_pixmap(0).toImage().convertToFormat(QImage.Format_ARGB32)
    alphas = [ghost.pixel(x, y) >> 24 for y in range(0, STRIP_ICON[1], 7)
              for x in range(0, STRIP_ICON[0], 7)]
    assert alphas, "ghost is empty"
    expected = round(255 * v.GHOST_OPACITY)
    assert all(abs(a - expected) <= 1 for a in alphas), set(alphas)

    # Exercise the exact live path with the selected item itself and verify
    # QPainter's channel result, not merely the intermediate pixmap alpha.
    before = w.grab().toImage().convertToFormat(QImage.Format_ARGB32)
    v._drag_base = base
    v._drag_hotspot = QPoint(0, 0)
    v._move_drag_overlay(QPoint(300, -200))  # ghost above the strip
    _app.processEvents()
    after = w.grab().toImage().convertToFormat(QImage.Format_ARGB32)
    destination = v.viewport().mapTo(w, QPoint(305, -195))
    source = base_img.pixelColor(5, 5)
    old = before.pixelColor(destination)
    blended = after.pixelColor(destination)
    assert blended != old  # the ghost is actually visible over the preview
    for channel in ("red", "green", "blue"):
        expected_channel = round(
            getattr(source, channel)() * 0.75 + getattr(old, channel)() * 0.25)
        assert abs(getattr(blended, channel)() - expected_channel) <= 2, (
            channel, getattr(source, channel)(), getattr(old, channel)(),
            getattr(blended, channel)(), expected_channel)
    v._end_drag()


def test_strip_fits_row_across_scrollbar_styles():
    """§145: actual Qt scrollbars never clip cells or create vertical range."""
    from PySide6.QtWidgets import QListWidgetItem, QProxyStyle, QStyle, QStyleFactory
    from pdf_minify.ui_qt.app import _StripList

    for style_name, extent in (("Fusion", 14), ("Fusion", 30), ("Windows", 16)):
        class ScrollbarStyle(QProxyStyle):
            def pixelMetric(self, metric, option=None, widget=None):
                if metric == QStyle.PM_ScrollBarExtent:
                    return extent
                return super().pixelMetric(metric, option, widget)

        v = _StripList()
        style = ScrollbarStyle(QStyleFactory.create(style_name))
        style.setParent(v)
        v.setStyle(style)
        v.horizontalScrollBar().setStyle(style)
        for i in range(8):
            v.addItem(QListWidgetItem(f"Filter {i}"))
        v.resize(450, v.height())
        v.show()
        try:
            for width in (450, 1800, 450):
                v.resize(width, v.height())
                for _ in range(3):
                    _app.processEvents()
                rect = v.visualRect(v.model().index(0, 0))
                assert v.viewport().height() == rect.height() == STRIP_ICON[1], (
                    style_name, extent, width, v.height(), v.viewport().height())
                assert v.viewport().rect().contains(rect)
                assert v.verticalScrollBar().maximum() == 0
                assert not v.verticalScrollBar().isVisible()
                assert v.horizontalScrollBar().isVisible() == (width == 450)
                if width == 450:
                    assert v.horizontalScrollBar().height() == extent
        finally:
            v.close()


def test_strip_content_has_equal_top_and_bottom_padding():
    """§159: trim oversized cell geometry, not captions or the native scrollbar."""
    import numpy as np
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPalette

    w = MainWindow()
    w.resize(1100, 650)
    w.show()
    v = w.filters
    pid = w._strip_ids[0]
    v.setCurrentRow(1)
    w._mini_view[pid] = np.full((104, 120, 3), 255, dtype=np.uint8)
    w._mini_amount[pid] = "64KB (20%)"
    w._filter_prog[pid] = 1.0
    w._paint_strip_item(pid)
    _app.processEvents()

    rect = v.visualRect(v.model().index(0, 0))
    assert STRIP_PREVIEW_RECT.top() == STRIP_PADDING == 4
    assert rect.height() - STRIP_AMOUNT_RECT.bottom() - 1 == STRIP_PADDING
    assert rect.height() == v.viewport().height() == 162
    assert v.verticalScrollBar().maximum() == 0
    actual = v.viewport().grab(rect).toImage()
    ground = v.palette().color(QPalette.Base)
    for y in (*range(STRIP_PADDING), *range(rect.height() - STRIP_PADDING, rect.height())):
        assert all(actual.pixelColor(x, y).rgba() == ground.rgba() for x in range(rect.width()))
    assert actual.pixelColor(STRIP_PREVIEW_RECT.center()) == Qt.white
    # The final amount is still visible, not moved underneath the scrollbar.
    assert any(actual.pixelColor(x, y) != ground
               for y in range(STRIP_AMOUNT_RECT.top(), STRIP_AMOUNT_RECT.bottom() + 1)
               for x in range(rect.width()))


@pytest.mark.parametrize("ground,base,ink", (
    ("#efefef", "#ffffff", "#000000"),
    ("#303030", "#181818", "#ffffff"),
))
def test_strip_background_tracks_theme_without_changing_other_panes(ground, base, ink):
    """§159: local Window ground, including live light/dark palette changes."""
    from PySide6.QtGui import QColor, QPalette

    w = MainWindow()
    w.show()
    pane_bases = [pane.palette().color(QPalette.Base) for pane in (w.before, w.after)]
    w.filters.clearSelection()
    for neutral in (QColor(ground), QColor(ground).lighter(110)):
        pal = QPalette(w.palette())
        pal.setColor(QPalette.Window, neutral)
        pal.setColor(QPalette.Base, QColor(base))
        pal.setColor(QPalette.WindowText, QColor(ink))
        w.setPalette(pal)
        _app.processEvents()
        v = w.filters
        shaded = neutral.darker(105)
        for group in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
            assert v.palette().color(group, QPalette.Base) == shaded
            assert v.viewport().palette().color(group, QPalette.Base) == shaded
        assert w.palette().color(QPalette.Base) == QColor(base)
        assert [pane.palette().color(QPalette.Base) for pane in (w.before, w.after)] == pane_bases
        assert v.palette().color(QPalette.WindowText) == QColor(ink)
        # Unselected cell margins must match the viewport's ground too.
        assert v.viewport().grab().toImage().pixelColor(5, 0).rgba() == shaded.rgba()
    assert w.filters.GHOST_OPACITY == 0.75


def test_filter_drop_from_any_window_height(tmp_path):
    """§144: real Qt events above, in, and below strip share the same gap."""
    from PySide6.QtCore import QPoint, QPointF, Qt
    from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent
    w = MainWindow(None)
    w.resize(1100, 650)
    w.show()
    _app.processEvents()
    v = w.filters
    original = list(w._strip_ids)
    source = v.visualRect(v.model().index(0, 0)).center()
    x = v.visualRect(v.model().index(3, 0)).right() + 1
    # The leftmost divider must win for a point near the start of item 0.
    assert v._gap_at(v.visualRect(v.model().index(0, 0)).left() + 2) == 0
    v._begin_drag(0, source)
    mime = v._drag_mime
    try:
        for y in (-200, 50, v.viewport().height() + 25):
            pos = v.viewport().mapTo(w, QPoint(x, y))
            entered = QDragEnterEvent(QPointF(pos), Qt.MoveAction, mime,
                                      Qt.LeftButton, Qt.NoModifier)
            QApplication.sendEvent(w, entered)
            assert entered.isAccepted()
            moved = QDragMoveEvent(QPointF(pos), Qt.MoveAction, mime,
                                  Qt.LeftButton, Qt.NoModifier)
            QApplication.sendEvent(w, moved)
            assert moved.isAccepted()
            assert v._drop_gap == 4
            assert v._drag_ghost.isVisible()
            assert v._drag_ghost.opacity == 0.75
            assert v._drop_line.isVisible()
        # Release in the preview, with the same pointer X as the strip gap.
        pos = v.viewport().mapTo(w, QPoint(x, -200))
        dropped = QDropEvent(QPointF(pos), Qt.MoveAction, mime,
                            Qt.LeftButton, Qt.NoModifier)
        QApplication.sendEvent(w, dropped)
        assert dropped.isAccepted()
        expected = original[1:4] + original[:1] + original[4:]
        assert w._strip_ids == expected
        assert [w.preset.itemData(i) for i in range(w.preset.count())] == expected
        assert v.currentRow() == 3
        assert w.preset.currentData() == original[0]
        assert w._ordered_pids()[0] == original[0]
        assert v._drop_line.isHidden() and v._drag_ghost.isHidden()
    finally:
        v._end_drag()
        w._custom_store().remove("stripOrder")
        w.close()


def test_zz_save_filter_persists_without_invalidating(tmp_path):
    """Designer §§112/149: Save keeps the processed live recipe/result."""
    from pdf_minify.core import presets
    w = MainWindow(str(_three_pages(str(tmp_path))))
    ids = [p["id"] for p in presets.PRESETS]
    w.preset.setCurrentIndex(w.preset.findData("bw-t180"))
    w.slider.setValue(210)
    w.save_filter()
    assert presets.get("bw-t180")["params"]["t"] == 210
    store = w._custom_store().value("customPresets", [])
    assert any(c.get("id") == "bw-t180" for c in store)
    assert "bw-t180" not in w._draft_specs
    assert w._saved_specs["bw-t180"]["t"] == 210
    assert w._result_key("bw-t180") in (
        w._artifacts.results.keys() | w._artifacts.pending.keys())
