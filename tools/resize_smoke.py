"""Timed real-file shrink/splitter diagnostic; review artifacts stay in .tmp/."""
import json
import os
from pathlib import Path
import sys
import time

for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(name, "1")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import QPoint, QRect, QSettings
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from pdf_minify.ui_qt.app import MainWindow
from pdf_minify.ui_qt.layout import UI_PADDING
from pdf_minify import APP_ID
from pdf_minify.ui_qt.settings import configure_application, settings_snapshot


def geometry(w):
    root = w.centralWidget()
    def rect(widget):
        return QRect(widget.mapTo(root, QPoint()), widget.size())
    split, strip = rect(w.panel_split), rect(w.filters)
    before, after, panel = rect(w.before), rect(w.after), rect(w.panelScroll)
    return {
        "window": [w.width(), w.height()],
        "splitter": w.panel_split.sizes(),
        "original": [w.before.width(), w.before.height()],
        "preview": [w.after.width(), w.after.height()],
        "headers": [[h.width(), h.minimumSizeHint().width(), h.text()]
                    for h in (w.beforeHeader, w.afterHeader, w.configurationHeader)],
        "header_tops": [rect(h).top() for h in
                        (w.beforeHeader, w.afterHeader, w.configurationHeader)],
        "header_heights": [h.height() for h in
                           (w.beforeHeader, w.afterHeader, w.configurationHeader)],
        "frame_tops": [before.top(), after.top(), panel.top()],
        "panel": [w.panelScroll.width(), w.panelScroll.widget().width(),
                  w.panelScroll.horizontalScrollBar().maximum()],
        "region_gutters": [split.left(), root.rect().right()-split.right(),
                           strip.left(), root.rect().right()-strip.right(),
                           strip.top()-split.bottom()-1,
                           after.left()-before.right()-1,
                           panel.left()-after.right()-1],
        "region_bottoms": [before.bottom(), after.bottom(), panel.bottom(), split.bottom()],
    }


def main():
    app = QApplication([])
    configure_application(app)
    suffix = "-2x" if app.devicePixelRatio() >= 2 else ""

    def capture(widget, name):
        widget.grab().save(f".tmp/resize{suffix}-{name}.png")
    Path(".tmp").mkdir(exist_ok=True)
    kept = settings_snapshot()
    QSettings.setPath(QSettings.NativeFormat, QSettings.UserScope,
                      str(Path(".tmp/resize-settings").resolve()))
    isolated = QSettings(APP_ID, APP_ID)
    isolated.clear()
    for key, value in kept.items():
        isolated.setValue(key, value)
    isolated.sync()
    pdf = sys.argv[1] if len(sys.argv) > 1 else "examples/models-nasa-kepler.pdf"
    w = MainWindow(pdf)
    w.resize(1920, 1000)
    w.show()
    try:
        deadline = time.monotonic() + 120
        while w._artifacts.pending:
            assert time.monotonic() < deadline, "filter jobs timed out"
            QTest.qWait(20)
        QTest.qWait(1000)
        capture(w, "wide")
        print("wide:", json.dumps(geometry(w)), flush=True)
        prepared, generation = dict(w._artifacts.results), w._gen
        calls = []
        w._reframe_timer.timeout.connect(lambda: calls.append(round(time.monotonic() - started, 3)))
        trace = []
        started = time.monotonic()
        w.resize(640, 600)
        previous = None
        while time.monotonic() - started < 10:
            QTest.qWait(20)
            state = geometry(w)
            if state != previous:
                entry = {"seconds": round(time.monotonic() - started, 3), **state}
                trace.append(entry)
                print(json.dumps(entry), flush=True)
                previous = state
        capture(w, "small")
        capture(w.panelScroll, "small-panel")
        capture(w.beforeHeader, "small-original-header")
        capture(w.afterHeader, "small-preview-header")
        capture(w.configurationHeader, "small-configuration-header")
        Path(f".tmp/resize{suffix}-trace.json").write_text(json.dumps({"trace": trace, "reframes": calls}, indent=2))
        assert w._gen == generation and w._artifacts.results == prepared
        assert not w._artifacts.pending and not w._preview_timer.isActive()
        print("last geometry change:", trace[-1]["seconds"], "reframes:", calls, flush=True)
        assert trace[-1]["seconds"] < 0.5, "delayed divider drift after shrink"
        assert all(abs(s["original"][0] - s["preview"][0]) <= 1 for s in trace)
        assert all(s["region_gutters"] == [UI_PADDING]*7 for s in trace)
        assert all(len(set(s["region_bottoms"])) == 1 for s in trace)
        assert all(len(set(s[key])) == 1 for s in trace
                   for key in ("header_tops", "header_heights", "frame_tops"))
        assert w.width() == 640
        # Also squeeze the control area itself: overflow stays internal and
        # delayed view refresh cannot move the designer's chosen divider.
        w.panel_split.moveSplitter(w.panel_split.width() - 250, 1)
        QTest.qWait(50)
        allocated = geometry(w)
        QTest.qWait(2000)
        assert geometry(w) == allocated
        assert w.panelScroll.horizontalScrollBar().maximum() > 0
        assert abs(w.before.width() - w.after.width()) <= 1
        capture(w, "squeezed")
        capture(w.panelScroll, "squeezed-panel")
        print("RESIZE SMOKE GREEN", flush=True)
    finally:
        w.close()
        deadline = time.monotonic() + 30
        while w._jobs:
            assert time.monotonic() < deadline, "resize smoke workers did not close"
            QTest.qWait(20)
        app.processEvents()


if __name__ == "__main__":
    main()
