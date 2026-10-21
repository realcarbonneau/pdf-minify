"""Desktop action icons with portable stock Breeze SVG fallbacks (§197).

Qt owns SVG/HiDPI rendering and generated disabled/active states. This
module never draws glyphs, overrides the desktop theme, or changes actions.
"""
from pathlib import Path

from PySide6.QtCore import QEvent, QObject
from PySide6.QtGui import QAction, QIcon, QPalette
from PySide6.QtWidgets import QApplication, QAbstractButton, QWidget


ICON_NAMES = frozenset({
    "document-revert", "edit-rename", "edit-copy", "document-save",
    "process-stop", "zoom-in", "zoom-out",
})
ASSET_ROOT = Path(__file__).resolve().parent / "assets" / "breeze"
APP_ICON_ROOT = Path(__file__).resolve().parent / "assets" / "app_icon"
APP_ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)


def app_icon() -> QIcon:
    """The product's own application icon (§294), every bundled size."""
    icon = QIcon()
    for size in APP_ICON_SIZES:
        source = APP_ICON_ROOT / f"pdf-minify-{size}.png"
        if not source.is_file():
            raise FileNotFoundError(
                f"Missing application icon: {source}. Include ui_qt/assets in the package.")
        icon.addFile(str(source))
    return icon


def standard_icon(name: str, palette: QPalette | None = None, *, size: int = 16) -> QIcon:
    """Use the desktop's named icon, or the matching light/dark Breeze SVG."""
    if name not in ICON_NAMES:
        raise ValueError(f"No bundled action icon: {name}")
    if palette is None:
        palette = QApplication.palette()
    variant = "dark" if palette.color(QPalette.Window).lightnessF() < .5 else "light"
    # QSvgIconEngine keeps one SVG per mode/state, not per addFile size.
    # Pick the stock optical grid for the logical control size first; Qt
    # then renders that vector at the requested device scale without blur.
    grid = 16 if size <= 16 else 22
    source = ASSET_ROOT / variant / str(grid) / f"{name}.svg"
    if not source.is_file():
        raise FileNotFoundError(
            f"Missing bundled icon: {source}. Include ui_qt/assets in the package.")
    return QIcon.fromTheme(name, QIcon(str(source)))


class ActionIcons(QObject):
    """Refresh icons on palette/theme changes without invoking actions."""

    def __init__(self, window: QWidget):
        super().__init__(window)
        self._window = window
        self._targets: list[tuple[QAction | QAbstractButton, str, QWidget]] = []
        window.installEventFilter(self)

    def bind(self, target: QAction | QAbstractButton, name: str,
             *, context: QWidget | None = None) -> None:
        if context is None:
            context = target if isinstance(target, QAbstractButton) else self._window
        self._set_icon(target, name, context)
        self._targets.append((target, name, context))
        context.installEventFilter(self)

    def _set_icon(self, target, name, context):
        size = target.iconSize().width() if isinstance(target, QAbstractButton) else 16
        palette = QPalette(context.palette())
        # Stylesheets/native styles can retain a control palette distinct
        # from its window. Match the surface that actually holds the glyph.
        palette.setColor(QPalette.Window, palette.color(context.backgroundRole()))
        target.setIcon(standard_icon(name, palette, size=size))

    def refresh(self) -> None:
        for target, name, context in self._targets:
            self._set_icon(target, name, context)

    def eventFilter(self, watched, event):  # noqa: N802
        # Ignore lifecycle events before touching Python state: Qt may still
        # send teardown events while the parent's wrapper is being cleared.
        if event.type() in (
                QEvent.ThemeChange, QEvent.PaletteChange, QEvent.ApplicationPaletteChange):
            self.refresh()
        return False
