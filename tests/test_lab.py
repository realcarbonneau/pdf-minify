import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from pdf_minimalist.ui_qt.lab import ProgressLab, ButtonsLab  # noqa: E402

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
