"""pytest bootstrap: single-thread numerical backends before anything loads BLAS.

Background QThread workers abort under BLAS thread-pool load in constrained
environments (designer §37). Same guards live in pdf_minify/__main__.py
(app entry) and tools/shot.py.
"""
import os
import sys
import tempfile
import itertools
import pytest

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

# Isolate QSettings (§91 last-file memory): tests open throwaway PDFs through
# MainWindow, which must never overwrite the designer's real last file.
# NOTE: unconditional override (not setdefault) — this shell pre-exports
# XDG_CONFIG_HOME, which once silently defeated the isolation (issues.md B23).
os.environ["XDG_CONFIG_HOME"] = tempfile.mkdtemp(prefix="pdfmin-test-xdg-")


@pytest.fixture(autouse=True)
def grayscale_text():
    """Draw test text without sub-pixel (LCD) anti-aliasing, on every platform.

    Pixel-exact GUI tests compare text painted by different paths, and Qt
    applies sub-pixel text to some of them only (a widget's own paint, not a
    delegate painting into a test's image). Ubuntu's fontconfig turns it on,
    Debian's does not; Windows has ClearType. Grey anti-aliasing keeps the
    comparisons about the app, not the platform's font settings.
    """
    if "PySide6.QtWidgets" in sys.modules:
        from PySide6.QtGui import QFont
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is not None and not app.font().styleStrategy() & QFont.NoSubpixelAntialias:
            font = app.font()
            font.setStyleStrategy(QFont.StyleStrategy(font.styleStrategy() | QFont.NoSubpixelAntialias))
            app.setFont(font)
    yield


@pytest.fixture(autouse=True)
def warnings_fail_instead_of_waiting(monkeypatch):
    """An app warning dialog ("Open failed") fails the test with its message.

    Without a screen, a modal warning waits forever for a click, so a test
    that hits an error path would hang (seen on Windows) instead of failing.
    No test expects one; tests drive the unsaved-changes dialog explicitly.
    """
    if "PySide6.QtWidgets" in sys.modules:
        from PySide6.QtWidgets import QMessageBox

        def fail(_parent, title, text, *rest):
            raise AssertionError(f"warning dialog: {title}: {text}")
        monkeypatch.setattr(QMessageBox, "warning", fail)
        monkeypatch.setattr(QMessageBox, "critical", fail)
    yield


@pytest.fixture
def drag_event():
    """Make a drag enter or move event on Debian 13's PySide6 6.8 and on newer Qt.

    Qt 6.8 takes the position as a QPoint; newer Qt takes a QPointF and
    deprecates the QPoint form.
    """
    from PySide6.QtCore import QPointF, Qt

    def make(event_type, pos, mime):
        try:
            return event_type(QPointF(pos), Qt.MoveAction, mime, Qt.LeftButton, Qt.NoModifier)
        except TypeError:
            return event_type(QPointF(pos).toPoint(), Qt.MoveAction, mime,
                              Qt.LeftButton, Qt.NoModifier)
    return make


@pytest.fixture(autouse=True)
def isolate_gui_artifact_roots(request, tmp_path, monkeypatch):
    """Test windows may share a PID; production applications do not (§153).

    Give each constructed test window an isolated OS-temp root instead of
    adding test-only session layers to the production filesystem design.
    """
    if not request.module.__name__.endswith(("test_minis", "test_filter_lifecycle",
                                           "test_strip_reorder_identity", "test_filter_defaults",
                                           "test_app_identity")):
        return
    from pdf_minify.ui_qt import app as ui, paths
    store_type = ui.ArtifactStore
    counter = itertools.count()

    def new_store(_root):
        root = tmp_path / f"test-window-{next(counter)}" / "pdf-minify" / "saves"
        return store_type(str(root))

    original_sweep = paths.sweep_stale_temps
    monkeypatch.setattr(ui, "ArtifactStore", new_store)
    monkeypatch.setattr(paths, "sweep_stale_temps",
                        lambda *a, **kw: original_sweep(*a, temp_base=str(tmp_path), **kw))
