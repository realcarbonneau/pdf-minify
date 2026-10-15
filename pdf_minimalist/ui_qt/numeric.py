"""Standard slider + precise integer editor, sharing one value (§178)."""

from PySide6.QtCore import Qt, Signal, QSignalBlocker
from PySide6.QtWidgets import QWidget, QHBoxLayout, QSlider, QSpinBox, QSizePolicy


class NumericSlider(QWidget):
    valueChanged = Signal(int)

    def __init__(self, minimum, maximum, value, name, parent=None):
        super().__init__(parent)
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setRange(minimum, maximum)
        self.slider.setSingleStep(1)
        self.slider.setValue(value)
        self.slider.setAccessibleName(name)
        self.number = QSpinBox(self)
        self.number.setRange(minimum, maximum)
        self.number.setSingleStep(1)
        self.number.setWrapping(False)
        self.number.setValue(self.slider.value())
        self.number.setAlignment(Qt.AlignRight)
        self.number.setKeyboardTracking(True)
        self.number.setAccessibleName(f"{name} value")
        self.number.setAccessibleDescription(
            f"{minimum} to {maximum}. Type a value or use the arrows; updates live.")
        self.number.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(self.slider, 1)
        row.addWidget(self.number)
        self.slider.valueChanged.connect(self._changed)
        self.number.valueChanged.connect(self.slider.setValue)

    def _changed(self, value):
        # Slider is the single bounded value. Block the mirror's signal so
        # typing, dragging and stepping each have exactly one edit path.
        with QSignalBlocker(self.number):
            self.number.setValue(value)
        self.valueChanged.emit(value)

    def value(self):
        return self.slider.value()

    def setValue(self, value):
        # Blocking THIS widget during recipe loads still lets its children
        # synchronize, while suppressing the public editing notification.
        self.slider.setValue(value)
