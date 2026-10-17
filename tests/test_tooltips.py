"""Native contextual help: concise hover text, accessible and keyboard help."""

from PySide6.QtWidgets import QApplication, QWidget

from pdf_minify.ui_qt.tooltips import set_control_help


def test_control_help_keeps_native_chrome_and_exposes_non_hover_equivalents():
    app = QApplication.instance() or QApplication([])
    widget = QWidget()
    font, palette = widget.font(), widget.palette()
    duration, style = widget.toolTipDuration(), widget.styleSheet()
    set_control_help(widget, "Short explanation.", "More detailed keyboard help.")
    assert widget.toolTip() == widget.accessibleDescription() == "Short explanation."
    assert widget.whatsThis() == "Short explanation.\n\nMore detailed keyboard help."
    assert widget.font() == font and widget.palette() == palette
    assert widget.toolTipDuration() == duration and widget.styleSheet() == style
    set_control_help(widget, "New context.")
    assert widget.toolTip() == widget.whatsThis() == widget.accessibleDescription() == "New context."
    widget.close()
