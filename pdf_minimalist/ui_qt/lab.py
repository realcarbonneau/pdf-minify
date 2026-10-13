"""Widget lab (designer §99): live variant galleries for picking controls.

Two modeless windows, opened from View → Widget lab. Every row is a real Qt
widget running the same code paths as the app — pick a winner here, and the
same construction drops into the main window.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton,
    QToolBar, QStyleFactory,
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QAction, QIcon


def _bar(minimum=0, maximum=100, text_visible=True, centered=False,
         height=None, style=None):
    b = QProgressBar()
    b.setRange(minimum, maximum)
    b.setTextVisible(text_visible)
    if centered:
        b.setAlignment(Qt.AlignCenter)
        b.setFormat("%p%")
    if height is not None:
        b.setFixedHeight(height)
    if style is not None:
        st = QStyleFactory.create(style)
        if st is not None:
            b.setStyle(st)
    return b


class ProgressLab(QDialog):
    """QProgressBar variants, all animated together (designer §99)."""

    ROWS = (
        ("Native standard", "system style, default % placement", {}),
        ("Centered %", "best practice for overlaid/compact bars", {"centered": True}),
        ("Slim, no text", "8px status-strip style; needs a % elsewhere",
         {"centered": True, "height": 8, "text_visible": False}),
        ("Fusion centered", "same widget, Fusion style (compare native)",
         {"centered": True, "style": "Fusion"}),
        ("Chunky 22px", "touch-sized, centered %", {"centered": True, "height": 22}),
        ("Busy / indeterminate", "unknown length; never a fake %",
         {"minimum": 0, "maximum": 0}),
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Widget lab — progress bars")
        self.resize(460, 320)
        box = QVBoxLayout(self)
        box.addWidget(QLabel("Live variants — pick one for the strip overlay:"))
        self._bars = []
        for title, note, kw in self.ROWS:
            box.addWidget(QLabel(f"<b>{title}</b> — {note}"))
            bar = _bar(**{k: v for k, v in kw.items()})
            box.addWidget(bar)
            self._bars.append(bar)
        self._t = QTimer(self)
        self._t.setInterval(120)
        self._t.timeout.connect(self._tick)
        self._v = 0
        self._t.start()

    def _tick(self):
        self._v = (self._v + 2) % 101
        for b in self._bars:
            if b.maximum() > 0:
                b.setValue(self._v)


class ButtonsLab(QDialog):
    """Zoom/Save/Cancel variants with best-practice notes (designer §99)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Widget lab — buttons")
        self.resize(460, 380)
        box = QVBoxLayout(self)
        box.addWidget(QLabel("Live variants — pick the row style:"))
        box.addWidget(QLabel("<b>A · Text buttons.</b> Clearest, widest. "
                             "Good for rare, consequential actions."))
        row = QHBoxLayout()
        row.addWidget(QPushButton("Zoom +"))
        row.addWidget(QPushButton("Zoom −"))
        box.addLayout(row)
        box.addWidget(QLabel("<b>B · Segmented toolbar, words.</b> Compact "
                             "group for frequent zooming; zero-gap reads as one control."))
        bar = QToolBar()
        bar.setIconSize(QSize(16, 16))
        bar.layout().setSpacing(0)
        bar.layout().setContentsMargins(0, 0, 0, 0)
        for name, word, tip in (("zoom-out", "Out", "Zoom out"),
                                ("zoom-in", "In", "Zoom in")):
            a = QAction(QIcon.fromTheme(name), word, self)
            a.setToolTip(tip)
            bar.addAction(a)
        box.addWidget(bar)
        box.addWidget(QLabel("<b>C · Icon-only autoRaise.</b> Smallest "
                             "footprint; needs tooltips + discoverable context. "
                             "Hover raises the button."))
        bar2 = QToolBar()
        bar2.setIconSize(QSize(16, 16))
        for name, tip in (("zoom-out", "Zoom out"), ("zoom-in", "Zoom in")):
            b = bar2.addAction(QIcon.fromTheme(name), "")
            b.setToolTip(tip)
            btn = bar2.widgetForAction(b)
            if btn is not None:
                btn.setAutoRaise(True)
        box.addWidget(bar2)
        box.addWidget(QLabel("<b>D · Emphasized primary.</b> Best practice: "
                             "exactly one suggested action (Save) highlighted, "
                             "Cancel plain. Never two competing emphases."))
        row2 = QHBoxLayout()
        save = QPushButton("Save")
        save.setStyleSheet("QPushButton { background-color: palette(highlight); "
                           "color: palette(highlighted-text); "
                           "border-radius: 4px; padding: 4px 16px; }")
        cancel = QPushButton("Cancel")
        cancel.setFlat(True)
        row2.addWidget(save)
        row2.addWidget(cancel)
        row2.addStretch(1)
        box.addLayout(row2)
        box.addStretch(1)


def open_progress_lab(parent):
    dlg = ProgressLab(parent)
    dlg.show()
    return dlg


def open_buttons_lab(parent):
    dlg = ButtonsLab(parent)
    dlg.show()
    return dlg
