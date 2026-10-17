"""Offscreen UI screenshots for designer review. All artifacts stay in ./.tmp/.

Usage: ./.venv/bin/python tools/shot.py [examples/images.pdf]
Captures: main window (side-h), stacked view, real one/two/seven-page grids,
and 1:1 panes/minis. Review settings are isolated from the designer's.
Filter jobs run in background; we wait for the latest generation to finish.
"""
import argparse
import os
import sys
import time
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fitz  # noqa: E402
from PySide6.QtCore import QPoint, QRect, QSettings  # noqa: E402
from PySide6.QtGui import QColor, QIcon, QPalette  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import QApplication, QToolBar  # noqa: E402
from pdf_minify.ui_qt.app import MainWindow, setup_logging, FILTER_PROGRESS_ROLE  # noqa: E402
from pdf_minify.ui_qt.icons import ICON_NAMES  # noqa: E402
from pdf_minify import APP_ID  # noqa: E402
from pdf_minify.ui_qt.settings import configure_application, settings_snapshot  # noqa: E402


def wait_job(w, timeout=120):
    t0 = time.perf_counter()
    while w._artifacts.pending or w._preview_timer.isActive():
        if time.perf_counter() - t0 > timeout:
            raise AssertionError("screenshot filter jobs timed out")
        app.processEvents()
        time.sleep(0.05)
    app.processEvents()


def close_review_window(w):
    w.close()
    deadline = time.monotonic() + 60
    while w._jobs:
        assert time.monotonic() < deadline, "screenshot workers did not close"
        app.processEvents()
        time.sleep(.02)
    app.processEvents()


def capture(w, name):
    window = w.grab()
    window.save(f".tmp/shot-{name}.png")
    # §188: inspect the entire preview/panel-to-strip junction at 1:1,
    # including outer side insets, not only crops inside each viewport.
    scale = window.devicePixelRatioF()
    strip_top = w.filters.mapTo(w, QPoint()).y()
    window.copy(QRect(0, round((strip_top-12)*scale), window.width(),
                      round(28*scale))).save(f".tmp/shot-{name}-junction.png")
    w.filters.viewport().grab().save(f".tmp/shot-{name}-strip.png")
    w.before.viewport().grab().save(f".tmp/shot-{name}-original.png")
    w.after.viewport().grab().save(f".tmp/shot-{name}-preview.png")
    print(f"shot: .tmp/shot-{name}.png + 1:1 strip/panes")


def icon_lab_samples(w):
    """Actual View menu dialog; sample choices never apply to the app."""
    generation, active = w._gen, w._active_pid
    originals = [target.icon().cacheKey() for target, _, _ in w._action_icons._targets]
    w.icon_lab_act.trigger()
    lab = w._icon_lab
    tag = "" if lab.devicePixelRatioF() == 1 else f"-{lab.devicePixelRatioF():g}x"

    def take(name):
        app.processEvents()
        lab.grab().save(f".tmp/shot-icon-lab-{name}{tag}.png")
        lab.table.grab().save(f".tmp/shot-icon-lab-{name}{tag}-table.png")
        for code in ("N-REV-02", "O-REN-01", "O-REN-02", "G-REN-01"):
            lab.choices[code].parentWidget().grab().save(f".tmp/shot-icon-lab-{name}{tag}-{code}.png")
        print(f"shot: .tmp/shot-icon-lab-{name}{tag}.png + 1:1 table/cards")

    assert not lab.choice_text()
    take("unselected")
    for code in ("N-REV-02", "O-REN-01", "N-COP-01", "O-SAV-01",
                 "N-STP-02", "G-ZIN-01", "G-ZOU-01"):
        lab.choices[code].setChecked(True)
    expected = lab.choice_text()
    for index, name in ((1, "light-selected-fixture"), (2, "dark-selected-fixture")):
        lab.background.setCurrentIndex(index)
        take(name)
        lab.table.verticalScrollBar().setValue(lab.table.verticalScrollBar().maximum())
        take(name + "-bottom")
        lab.table.verticalScrollBar().setValue(0)
    lab.background.setCurrentIndex(1)
    lab.resize(640, 520)
    take("narrow-top")
    assert lab.table.horizontalScrollBar().maximum() > 0
    assert lab.table.verticalScrollBar().maximum() > 0
    lab.table.horizontalScrollBar().setValue(lab.table.horizontalScrollBar().maximum())
    lab.table.verticalScrollBar().setValue(lab.table.verticalScrollBar().maximum())
    take("narrow-bottom-right")
    lab.close()
    w.icon_lab_act.trigger()
    assert w._icon_lab is lab and lab.choice_text() == expected
    assert w._gen == generation and w._active_pid == active
    assert originals == [target.icon().cacheKey() for target, _, _ in w._action_icons._targets]
    assert not w._artifacts.pending and not w._preview_timer.isActive()
    lab.close()


def icon_samples(pdf):
    """Actual controls, native/portable icons, light/dark and disabled states.

    Enabled-fixture shots only change button enabled flags, never edit filters
    or invoke actions. The native-theme sample is conditional on its install;
    production uses only the portable provider, not these diagnostic paths.
    """
    original_palette = QPalette(app.palette())
    theme = (QIcon.themeName(), QIcon.fallbackThemeName(), QIcon.themeSearchPaths(),
             QIcon.fallbackSearchPaths())
    w = None
    try:
        for native in (True, False):
            QIcon.setThemeSearchPaths(["/usr/share/icons"] if native else [])
            QIcon.setFallbackSearchPaths([])
            QIcon.setFallbackThemeName("pdfmin-absent-fallback")
            for dark in (False, True):
                QIcon.setThemeName(("breeze-dark" if dark else "breeze")
                                   if native else "pdfmin-absent-theme")
                if native and not all(QIcon.hasThemeIcon(name) for name in ICON_NAMES):
                    print("icon native-theme sample skipped: Breeze subset not installed")
                    continue
                palette = QPalette(original_palette)
                if dark:
                    for role, color in ((QPalette.Window, "#232629"),
                                        (QPalette.Button, "#31363b"),
                                        (QPalette.Base, "#1b1e20"),
                                        (QPalette.AlternateBase, "#232629"),
                                        (QPalette.Text, "#fcfcfc"),
                                        (QPalette.WindowText, "#fcfcfc"),
                                        (QPalette.ButtonText, "#fcfcfc")):
                        palette.setColor(role, QColor(color))
                    for role in (QPalette.Text, QPalette.WindowText, QPalette.ButtonText):
                        palette.setColor(QPalette.Disabled, role, QColor("#80858a"))
                app.setPalette(palette)
                # Construct after the theme/palette is selected: existing
                # stylesheet-polished controls can retain their old palette.
                # Only one MainWindow owns the canonical PID artifact root.
                w = MainWindow(pdf)
                w.resize(1100, 650)
                w.show()
                wait_job(w)
                controls = (w.revert_btn, w.rename_btn, w.copy_btn, w.keep_btn, w.cancel_act)
                enabled = [control.isEnabled() for control in controls]
                before = (w._gen, dict(w._artifacts.results), w._active_pid,
                          dict(w._saved_specs), dict(w._draft_specs))
                toolbar = next(bar for bar in w.findChildren(QToolBar)
                               if w.zoom_in_act in bar.actions())
                tag = "" if w.devicePixelRatioF() == 1 else f"-{w.devicePixelRatioF():g}x"
                for fixture in (False, True):
                    for control, previous in zip(controls, enabled):
                        control.setEnabled(True if fixture else previous)
                    app.processEvents()
                    name = f"icons-{'native-breeze' if native else 'fallback'}-{'dark' if dark else 'light'}-{'enabled-fixture' if fixture else 'normal'}{tag}"
                    window = w.grab()
                    window.save(f".tmp/shot-{name}.png")
                    rect = QRect()
                    for button in controls[:4]:
                        rect = rect.united(QRect(button.mapTo(w, QPoint()), button.size()))
                    scale = window.devicePixelRatioF()
                    rect = rect.adjusted(-4, -4, 4, 4)
                    window.copy(QRect(round(rect.x()*scale), round(rect.y()*scale),
                                      round(rect.width()*scale), round(rect.height()*scale))).save(
                                          f".tmp/shot-{name}-filter-actions.png")
                    toolbar.grab().save(f".tmp/shot-{name}-toolbar.png")
                    print(f"shot: .tmp/shot-{name}.png + 1:1 action controls")
                assert before == (w._gen, dict(w._artifacts.results), w._active_pid,
                                  dict(w._saved_specs), dict(w._draft_specs))
                assert not w._artifacts.pending and not w._preview_timer.isActive()
                close_review_window(w)
                w = None
    finally:
        if w is not None:
            close_review_window(w)
        QIcon.setThemeSearchPaths(theme[2])
        QIcon.setFallbackSearchPaths(theme[3])
        QIcon.setFallbackThemeName(theme[1])
        QIcon.setThemeName(theme[0])
        app.setPalette(original_palette)
        app.processEvents()


def compression_samples(w):
    """Real debounced codec changes; preview comes from each completed PDF."""
    from pdf_minify.core.algorithms import ALGORITHMS, PALETTE_MODES
    from pdf_minify.core.stream_compression import STREAM_POLICIES
    w.preset.setCurrentIndex(w.preset.findData("color-p16"))
    tag = "" if w.devicePixelRatioF() == 1 else f"-{w.devicePixelRatioF():g}x"
    pid = w._active_pid
    for mode, _ in ALGORITHMS:
        w.compression.setCurrentIndex(w.compression.findData(mode))
        if mode in PALETTE_MODES:
            w.colors_value.setValue(5)
        wait_job(w)
        assert w._active_pid == pid
        assert w._shown_preview_key == w._result_key(pid)
        assert w.after._pdf_source.path == w._artifacts.results[w._result_key(pid)].pdf_path
        settle_view(w)
        name = f"compression-{mode}{tag}"
        capture(w, name)
        w.panelScroll.widget().grab().save(f".tmp/shot-{name}-panel.png")
    w.revert_filter()
    for policy, _ in STREAM_POLICIES:
        w.stream_compression.setCurrentIndex(w.stream_compression.findData(policy))
        wait_job(w)
        settle_view(w)
        name = f"compression-stream-{policy}{tag}"
        capture(w, name)
        w.panelScroll.widget().grab().save(f".tmp/shot-{name}-panel.png")
    w.revert_filter()
    w.compression.showPopup()
    app.processEvents()
    w.compression.view().window().grab().save(f".tmp/shot-compression-options{tag}.png")
    w.compression.hidePopup()
    w.stream_compression.showPopup()
    app.processEvents()
    w.stream_compression.view().window().grab().save(f".tmp/shot-compression-stream-options{tag}.png")
    w.stream_compression.hidePopup()
    assert not w._draft_specs and not w._artifacts.pending


def brotli_compatibility_samples(w):
    """Real saved outputs; the compatibility checkbox is absent outside Brotli."""
    from pdf_minify.core.stream_compression import brotli_declaration_present
    for policy, enabled, name in (("flate", False, "flate-hidden"),
                                  ("brotli", False, "brotli-default-off"),
                                  ("brotli", True, "brotli-opt-in"),
                                  ("zopfli", True, "zopfli-hidden")):
        w.stream_compression.setCurrentIndex(w.stream_compression.findData(policy))
        if policy == "brotli":
            w.brotli_declaration.setChecked(enabled)
        wait_job(w)
        settle_view(w)
        assert w.brotli_declaration.isVisible() is (policy == "brotli")
        result = w._artifacts.results[w._result_key(w._active_pid)]
        with fitz.open(result.pdf_path) as doc:
            assert brotli_declaration_present(doc) is (policy == "brotli" and enabled)
        assert w.after._pdf_source.path == result.pdf_path
        capture(w, f"compatibility-{name}")
        w.panelScroll.widget().grab().save(f".tmp/shot-compatibility-{name}-panel.png")
    w.revert_filter()
    assert not w._draft_specs


def compression_state_samples(w):
    """All color FFPR codecs are effective edits with actual saved readback."""
    tag = "" if w.devicePixelRatioF() == 1 else f"-{w.devicePixelRatioF():g}x"
    w.preset.setCurrentIndex(w.preset.findData("bw-fast"))
    assert w.force_raster.isChecked()
    w.dpi.setCurrentIndex(w.dpi.findData(300))
    for mode in ("color", "jpx", "indexed", "layered-jbig2"):
        w.compression.setCurrentIndex(w.compression.findData(mode))
        if mode in ("indexed", "layered-jbig2"):
            w.colors_value.setValue(5)
        wait_job(w)
        assert w.force_raster.isEnabled() and w.force_raster.isChecked()
        assert w._shown_preview_key == w._result_key(w._active_pid)
        result = w._artifacts.results[w._result_key(w._active_pid)]
        with fitz.open(result.pdf_path) as doc:
            assert all(not page.get_text("words") and not page.get_fonts(full=True) for page in doc)
        w.panelScroll.ensureWidgetVisible(w.force_raster)
        settle_view(w)
        name = f"compression-{mode}-ffpr{tag}"
        capture(w, name)
        w.panelScroll.widget().grab().save(f".tmp/shot-{name}-panel.png")
    w.force_raster.setChecked(False)
    wait_job(w)
    assert "Text/vectors kept" in w.details.text()
    capture(w, f"compression-color-native-state{tag}")
    w.panelScroll.widget().grab().save(f".tmp/shot-compression-color-native-state{tag}-panel.png")
    w.revert_filter()
    assert w.force_raster.isEnabled() and w.force_raster.isChecked()
    capture(w, f"compression-bw-ffpr-restored{tag}")
    w.panelScroll.widget().grab().save(f".tmp/shot-compression-bw-ffpr-restored{tag}-panel.png")
    assert not w._draft_specs


def progress_samples(w):
    """Explicit paint fixtures, then a real debounced edit and completion."""
    v = w.filters
    scale = w.devicePixelRatioF()
    tag = "" if scale == 1 else f"-{scale:g}x"
    rows = [(v.item(i), v.item(i).data(FILTER_PROGRESS_ROLE)) for i in range(v.count())]
    value, low, high = w.progress.value(), w.progress.minimum(), w.progress.maximum()
    for (item, _), fraction in zip(rows, (0., .375, .99, 1., .65, .125)):
        item.setData(FILTER_PROGRESS_ROLE, fraction)
    w.progress.setRange(0, 10_000)
    w.progress.setValue(3750)
    app.processEvents()
    capture(w, f"progress-paint-fixture{tag}")
    w.progress.grab().save(f".tmp/shot-progress-default{tag}.png")
    v._drag_base_pixmap(v.currentRow()).save(f".tmp/shot-progress-selected-source{tag}.png")
    v._drag_pixmap(v.currentRow()).save(f".tmp/shot-progress-ghost{tag}.png")
    for item, fraction in rows:
        item.setData(FILTER_PROGRESS_ROLE, fraction)
    w.progress.setRange(low, high)
    w.progress.setValue(value)

    # These shots use actual worker progress, not the paint fixture above.
    previous = w.preset.currentData()
    w.preset.setCurrentIndex(w.preset.findData("bw-t180"))
    initial = w.threshold_value.value()
    w.threshold_value.setValue(initial+1 if initial < 255 else initial-1)
    deadline = time.monotonic()+120
    while True:
        app.processEvents()
        assert time.monotonic() < deadline, "no live edit progress appeared"
        fraction = w._filter_prog["bw-t180"]
        # A one-page job may finish between progress polls. Capture its real
        # pending state (including 0%); deterministic percentages live only in
        # the explicitly named paint fixture above.
        if w._artifacts.pending and 0 <= fraction < 1:
            capture(w, f"progress-live{tag}")
            print(f"real edit progress captured: {fraction:.4f}")
            break
        assert w._preview_timer.isActive() or w._artifacts.pending, "worker completed without a progress capture"
        time.sleep(.01)
    wait_job(w)
    assert w._filter_prog["bw-t180"] == 1
    capture(w, f"progress-complete{tag}")
    w.revert_filter()
    assert not w._draft_specs
    w.preset.setCurrentIndex(w.preset.findData(previous))


def layout_document(count):
    """Real multi-page PDF fixture; previews still come from actual savers."""
    path = Path(f".tmp/shot-layout-{count}.pdf")
    with fitz.open() as doc:
        for i in range(count):
            page = doc.new_page(width=240, height=320)
            page.insert_text((24, 40), f"Page {i + 1} of {count}", fontsize=20)
            page.insert_text((24, 75), "Occupied grid centering", fontsize=12)
            page.draw_rect(fitz.Rect(24, 110, 216, 280), color=(0.2, 0.4, 0.8),
                           fill=(0.85, 0.9, 0.98), width=2)
        doc.save(path)
    return str(path)


def settle_view(w):
    # Let Qt's delayed item layout and the normal mini-reframe debounce settle
    # before the whole-window grab, not only before a later child grab.
    QTest.qWait(200)
    w._reframe_minis()
    QTest.qWait(30)


def verify_grid(w):
    assert w.before.cols() == w.after.cols() <= w.before.page_count
    assert w.before.sceneRect() == w.after.sceneRect()
    assert [w.before.page_pos(i) for i in range(w.before.page_count)] == [
        w.after.page_pos(i) for i in range(w.after.page_count)]
    for pane in (w.before, w.after):
        bounds = pane.sceneRect()
        if bounds.width() * pane._zoom <= pane.viewport().width():
            assert abs(pane.mapFromScene(bounds.center()).x() - pane.maximumViewportSize().width() / 2) <= 2
        if bounds.height() * pane._zoom <= pane.viewport().height():
            assert abs(pane.mapFromScene(bounds.center()).y() - pane.maximumViewportSize().height() / 2) <= 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", nargs="?", default="examples/images.pdf")
    parser.add_argument("--progress-only", action="store_true",
                        help="capture the actual queued/live/complete mini progress states only")
    parser.add_argument("--icon-lab-only", action="store_true",
                        help="capture the real coded stock-icon lab without processing a PDF")
    parser.add_argument("--compression-only", action="store_true",
                        help="capture real image/native compression choices and completed files")
    parser.add_argument("--compression-state-only", action="store_true",
                        help="capture actual BW/color FFPR and native-preserving state/revert")
    parser.add_argument("--brotli-compatibility-only", action="store_true",
                        help="capture default-off/opt-in Brotli metadata and hidden non-Brotli controls")
    args = parser.parse_args()
    setup_logging(True)
    global app
    app = QApplication([])
    configure_application(app)
    Path(".tmp").mkdir(exist_ok=True)
    # Review the designer's layout/order without writing their preferences or
    # replacing the remembered input with one of these throwaway fixtures.
    kept = settings_snapshot()
    QSettings.setPath(QSettings.NativeFormat, QSettings.UserScope,
                      str(Path(".tmp/shot-settings").resolve()))
    review_settings = QSettings(APP_ID, APP_ID)
    review_settings.clear()
    for key, value in kept.items():
        review_settings.setValue(key, value)
    review_settings.sync()
    pdf = args.pdf
    if args.brotli_compatibility_only and pdf == "examples/images.pdf":
        pdf = layout_document(1)
    w = MainWindow(None if args.icon_lab_only else pdf)
    w.resize(1100, 650)
    w.show()
    app.processEvents()

    if args.icon_lab_only:
        icon_lab_samples(w)
        close_review_window(w)
        print("ICON LAB SHOTS GREEN")
        return

    if args.brotli_compatibility_only:
        wait_job(w)
        brotli_compatibility_samples(w)
        close_review_window(w)
        print("BROTLI COMPATIBILITY SHOTS GREEN")
        return

    if args.compression_only or args.compression_state_only:
        wait_job(w)
        if args.compression_state_only:
            compression_state_samples(w)
        else:
            compression_samples(w)
        close_review_window(w)
        print("COMPRESSION SHOTS GREEN")
        return

    capture(w, "progress-queued")
    wait_job(w)
    capture(w, "main")
    progress_samples(w)
    if args.progress_only:
        close_review_window(w)
        print("PROGRESS SHOTS GREEN")
        return

    original_filter = w.preset.currentData()
    for pid, name in (("bw-t180", "numeric-threshold"), ("color-i64", "numeric-colors")):
        w.preset.setCurrentIndex(w.preset.findData(pid))
        settle_view(w)
        editor = w.threshold_value if pid == "bw-t180" else w.colors_value
        w.panelScroll.ensureWidgetVisible(editor)
        capture(w, name)
        editor.grab().save(f".tmp/shot-{name}-editor.png")
    w.preset.setCurrentIndex(w.preset.findData(original_filter))

    # §183: review the actual low-color files after native numeric edits and
    # the shared trailing debounce, not an independent quantized screenshot.
    w.preset.setCurrentIndex(w.preset.findData("color-p16"))
    for count in (3, 4, 8, 16):
        w.colors_value.setValue(count)
        wait_job(w)
        assert w._shown_preview_key == w._result_key("color-p16")
        settle_view(w)
        capture(w, f"palette-{count}")
    assert not w._draft_specs
    w.preset.setCurrentIndex(w.preset.findData(original_filter))

    w.set_main_mode("stack-v")
    app.processEvents()
    capture(w, "stacked")

    w.set_main_mode("side-h")
    w.preset.setCurrentIndex(3)  # BW Strong T=210
    wait_job(w)
    w.before.set_zoom(0.35)  # zoomed out => autowrap grid
    settle_view(w)
    capture(w, "preset")

    w.before.set_zoom(0.1)
    settle_view(w)
    verify_grid(w)
    capture(w, "center-input")

    for count, zoom in ((2, 0.25), (7, 0.2)):
        w.open_file(layout_document(count))
        wait_job(w)
        generation = w._gen
        prepared = dict(w._artifacts.results)
        w.after.set_zoom(zoom)  # initiate from the preview, not only original
        settle_view(w)
        verify_grid(w)
        assert w._gen == generation and w._artifacts.results == prepared
        assert not w._artifacts.pending and not w._preview_timer.isActive()
        capture(w, f"center-{count}")
    w.set_main_mode("stack-v")
    w.before.set_zoom(0.1)
    settle_view(w)
    verify_grid(w)
    capture(w, "center-stacked")
    close_review_window(w)
    icon_samples(pdf)
    print("OK")


if __name__ == "__main__":
    main()
