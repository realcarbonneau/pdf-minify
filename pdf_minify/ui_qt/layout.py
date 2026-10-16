"""Main-region spacing and composition: one owner per inset, no stacked gaps."""
from PySide6.QtWidgets import QBoxLayout, QHBoxLayout, QVBoxLayout, QWidget


UI_PADDING = 4  # Logical pixels; Qt handles device scaling (§§187/188).


def spaced(layout: QBoxLayout, *, inset: int = 0) -> QBoxLayout:
    """Apply the shared gutter; only a region's owner supplies its inset."""
    layout.setContentsMargins(inset, inset, inset, inset)
    layout.setSpacing(UI_PADDING)
    return layout


class PaneBlock(QWidget):
    """One shared header/content column for previews and configuration (§192)."""

    def __init__(self, header, content, parent=None):
        super().__init__(parent)
        column = spaced(QVBoxLayout(self))
        column.addWidget(header)
        column.addWidget(content, 1)


class PreviewPair(QWidget):
    """Equal pane/header columns with no outer or nested wrapper margins.

    The root owns the surrounding gutter. Changing the box direction stacks
    the same two components without another set of sizes or spacing rules.
    """

    def __init__(self, before, before_header, after, after_header, parent=None):
        super().__init__(parent)
        self.panes = spaced(QHBoxLayout(self))
        for header, view in ((before_header, before), (after_header, after)):
            self.panes.addWidget(PaneBlock(header, view, self), 1)
