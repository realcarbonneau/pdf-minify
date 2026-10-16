"""§§124/166: painting an elision must never change layout/content."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QHBoxLayout, QSizePolicy, QWidget

from pdf_minify.ui_qt.headers import PaneHeader

_app = QApplication.instance() or QApplication([])


def test_header_elision_is_paint_only_and_theme_aware():
    full = "A long literal <filter> & recipe · 300dpi · 12 pages · 123KB (41%)"
    parent = QWidget()
    row = QHBoxLayout(parent)
    a, b = PaneHeader("Original"), PaneHeader(full)
    row.addWidget(a, 1)
    row.addWidget(b, 1)
    parent.resize(500, 50)
    parent.show()
    _app.processEvents()

    class Requests(QObject):
        count = 0

        def eventFilter(self, obj, event):
            if event.type() == QEvent.LayoutRequest:
                self.count += 1
            return False

    requests = Requests(parent)
    parent.installEventFilter(requests)
    try:
        assert b.sizePolicy().horizontalPolicy() == QSizePolicy.Ignored
        assert b.textFormat() == Qt.PlainText
        assert abs(a.width() - b.width()) <= 1
        assert b.elided_text().endswith("…")
        hints = b.sizeHint(), b.minimumSizeHint()
        allocated = a.geometry(), b.geometry()
        for _ in range(8):
            assert not b.grab().isNull()
            _app.processEvents()
            assert (b.sizeHint(), b.minimumSizeHint()) == hints
            assert (a.geometry(), b.geometry()) == allocated
            assert b.text() == b.toolTip() == b.property("fullText") == full
        assert requests.count == 0
        for width in (180, 900, 250):
            parent.resize(width, 50)
            _app.processEvents()
            assert abs(a.width() - b.width()) <= 1
            assert b.text() == full
            assert b.elided_text() == b.fontMetrics().elidedText(
                full, Qt.ElideRight, b.contentsRect().width())
        palette = parent.palette()
        palette.setColor(QPalette.Window, "#222222")
        palette.setColor(QPalette.WindowText, "#eeeeee")
        parent.setPalette(palette)
        _app.processEvents()
        shot = b.grab().toImage()
        assert any(shot.pixelColor(x, y).red() > 200
                   for y in range(shot.height()) for x in range(shot.width()))
        assert b.text() == full
    finally:
        parent.close()
