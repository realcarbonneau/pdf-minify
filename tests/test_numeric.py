"""§178: native coarse/precise input, one bounded value/edit path."""

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import Qt, QSignalBlocker
from PySide6.QtTest import QTest, QSignalSpy
from PySide6.QtWidgets import QApplication, QStyle, QStyleOptionSpinBox

from pdf_minimalist.ui_qt.numeric import NumericSlider

_app = QApplication.instance() or QApplication([])


@pytest.mark.parametrize("minimum,maximum,initial,value", [(0, 255, 180, 203), (2, 256, 64, 128)])
def test_slider_and_number_share_one_value_notification(minimum, maximum, initial, value):
    control = NumericSlider(minimum, maximum, initial, "Test value")
    spy = QSignalSpy(control.valueChanged)
    control.slider.setValue(value)
    assert control.number.value() == control.value() == value
    assert spy.count() == 1
    control.number.setValue(value - 1)
    assert control.slider.value() == control.value() == value - 1
    assert spy.count() == 2
    control.setValue(value - 1)
    assert spy.count() == 2
    with QSignalBlocker(control):
        control.setValue(initial)
    assert control.number.value() == control.slider.value() == initial
    assert spy.count() == 2


@pytest.mark.parametrize("minimum,maximum,initial,value", [(0, 255, 180, 203), (2, 256, 64, 128)])
def test_typing_is_live_and_native_spinner_steps(minimum, maximum, initial, value):
    control = NumericSlider(minimum, maximum, initial, "Test value")
    control.show()
    try:
        _app.processEvents()
        spy = QSignalSpy(control.valueChanged)
        control.number.setFocus()
        control.number.selectAll()
        QTest.keyClicks(control.number, str(value))
        assert control.value() == value and spy.count() >= 1
        count = spy.count()
        QTest.keyClick(control.number, Qt.Key_Return)
        assert control.value() == value and spy.count() == count
        option = QStyleOptionSpinBox()
        control.number.initStyleOption(option)
        up = control.number.style().subControlRect(
            QStyle.CC_SpinBox, option, QStyle.SC_SpinBoxUp, control.number)
        assert not up.isEmpty()
        QTest.mouseClick(control.number, Qt.LeftButton, Qt.NoModifier, up.center())
        assert control.value() == value + 1 and spy.count() == count + 1
        QTest.keyClick(control.number, Qt.Key_Down)
        assert control.value() == value and spy.count() == count + 2
    finally:
        control.close()


def test_bounds_disabled_state_and_stable_native_width():
    control = NumericSlider(2, 256, 64, "Palette colors")
    width = control.number.sizeHint().width()
    for value, expected in ((0, 2), (16, 16), (128, 128), (999, 256)):
        control.setValue(value)
        assert control.number.value() == control.slider.value() == expected
        assert control.number.sizeHint().width() == width
    control.number.stepUp()
    assert control.value() == 256  # no wrapping
    control.setEnabled(False)
    assert not control.slider.isEnabled() and not control.number.isEnabled()
    assert control.number.accessibleName() == "Palette colors value"
