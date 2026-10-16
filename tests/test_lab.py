import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from pdf_minify.ui_qt.lab import ProgressLab, ButtonsLab  # noqa: E402

_app = QApplication.instance() or QApplication([])


def test_progress_lab_variants():
    d = ProgressLab()
    assert len(d._bars) == len(ProgressLab.ROWS) == 6
    assert any(b.maximum() == 0 for b in d._bars)  # busy variant present
    centered = sum(1 for b in d._bars if b.alignment() == Qt.AlignCenter)
    assert centered >= 3  # centered-% rows (incl. Fusion + chunky)
    d.close()


def test_buttons_lab_variants():
    d = ButtonsLab()
    assert d is not None
    d.close()


def test_app_temp_dir_is_os_temp(tmp_path):
    """Designer §123: app scratch lives in the OS temp dir, never the repo."""
    import tempfile
    from pdf_minify.ui_qt.paths import app_temp_dir, sweep_stale_temps
    from PySide6.QtCore import QStandardPaths
    base = QStandardPaths.writableLocation(QStandardPaths.TempLocation) or tempfile.gettempdir()
    p = app_temp_dir("probe")
    assert os.path.isdir(p)
    assert os.path.abspath(p).startswith(os.path.abspath(base) + os.sep)
    assert "pdf-minify" in p
    assert os.path.abspath(os.getcwd()) not in os.path.abspath(p)
    stale = os.path.join(p, "old.pdf")
    with open(stale, "wb") as f:
        f.write(b"x")
    os.utime(stale, (0, 0))
    assert sweep_stale_temps(max_age_hours=1) >= 1
    assert not os.path.exists(stale)
