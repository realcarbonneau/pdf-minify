"""Pane metadata labels: elision is presentation, never layout state."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPalette
from PySide6.QtWidgets import QLabel, QSizePolicy
from .layout import UI_PADDING


class PaneHeader(QLabel):
    """Single-line, theme-painted text that cannot set a pane's minimum width.

    Keep the full text for accessibility/tooltips and compute its visible
    fragment at paint time. Neither resize nor painting calls setText, so an
    elided fragment cannot feed a changing size hint back into the splitter.
    """

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setTextFormat(Qt.PlainText)
        self.setWordWrap(False)
        self.setContentsMargins(UI_PADDING, UI_PADDING//2, UI_PADDING, UI_PADDING//2)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.setText(text)

    def setText(self, text):  # noqa: N802
        super().setText(text)
        self.setProperty("fullText", text)
        self.setToolTip(text)

    def elided_text(self):
        return self.fontMetrics().elidedText(
            self.text(), Qt.ElideRight, max(0, self.contentsRect().width()))

    def paintEvent(self, event):  # noqa: N802
        painter = QPainter(self)
        rect = self.contentsRect()
        painter.setClipRect(rect)
        self.style().drawItemText(painter, rect, self.alignment(), self.palette(),
                                  self.isEnabled(), self.elided_text(), QPalette.WindowText)
