"""Stock theme/fallback rendering; never depends on a system icon install."""
import hashlib
import json
import os
import xml.etree.ElementTree as ET

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, QSize  # noqa: E402
from PySide6.QtGui import QAction, QColor, QIcon, QImage, QPalette  # noqa: E402
from PySide6.QtWidgets import QApplication, QPushButton, QToolBar, QWidget  # noqa: E402

from pdf_minify.ui_qt import icons  # noqa: E402

_app = QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def no_desktop_theme(tmp_path):
    """Restore all process-global Qt theme settings after each test."""
    old = (QIcon.themeName(), QIcon.fallbackThemeName(), QIcon.themeSearchPaths(),
           QIcon.fallbackSearchPaths())
    QIcon.setThemeSearchPaths([str(tmp_path / "themes")])
    QIcon.setFallbackSearchPaths([])
    QIcon.setFallbackThemeName("pdfmin-absent-fallback")
    QIcon.setThemeName("pdfmin-absent-theme")
    yield
    QIcon.setThemeSearchPaths(old[2])
    QIcon.setFallbackSearchPaths(old[3])
    QIcon.setFallbackThemeName(old[1])
    QIcon.setThemeName(old[0])


def _palette(dark=False):
    palette = QPalette(_app.palette())
    palette.setColor(QPalette.Window, QColor("#232629" if dark else "#eff0f1"))
    palette.setColor(QPalette.WindowText, QColor("#eff0f1" if dark else "#232629"))
    palette.setColor(QPalette.Button, QColor("#31363b" if dark else "#eff0f1"))
    palette.setColor(QPalette.ButtonText, QColor("#eff0f1" if dark else "#232629"))
    return palette


def _pixels(icon, size=16, dpr=1., mode=QIcon.Normal):
    pixmap = icon.pixmap(QSize(size, size), dpr, mode)
    assert not pixmap.isNull()
    assert pixmap.width() == pixmap.height() == round(size * dpr)
    assert pixmap.devicePixelRatio() == dpr
    image = pixmap.toImage().convertToFormat(QImage.Format_RGBA8888)
    return np.frombuffer(image.constBits(), np.uint8).reshape(image.height(), image.width(), 4).copy()


def _theme(tmp_path):
    root = tmp_path / "themes" / "test-native"
    directory = root / "16x16" / "actions"
    directory.mkdir(parents=True)
    (root / "index.theme").write_text(
        "[Icon Theme]\nName=Test native\nDirectories=16x16/actions\n"
        "[16x16/actions]\nSize=16\nContext=Actions\nType=Fixed\n")
    # Deliberately unlike Breeze, to prove precedence rather than presence.
    (directory / "document-save.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16">'
        '<rect x="2" y="2" width="12" height="12" fill="#ff00ff"/></svg>')
    QIcon.setThemeName("test-native")


def test_native_theme_wins_and_missing_name_falls_back(tmp_path):
    _theme(tmp_path)
    assert QIcon.hasThemeIcon("document-save")
    actual = _pixels(icons.standard_icon("document-save", _palette()))
    expected = _pixels(QIcon.fromTheme("document-save"))
    assert np.array_equal(actual, expected)
    assert actual[8, 8].tolist() == [255, 0, 255, 255]
    assert not QIcon.hasThemeIcon("edit-rename")
    missing = _pixels(icons.standard_icon("edit-rename", _palette()))
    QIcon.setThemeName("pdfmin-absent-theme")
    assert np.array_equal(missing, _pixels(icons.standard_icon("edit-rename", _palette())))


@pytest.mark.parametrize("name", sorted(icons.ICON_NAMES))
@pytest.mark.parametrize("size", (16, 20))
def test_fallback_svg_states_contrast_and_hidpi(name, size):
    assert not QIcon.hasThemeIcon(name)
    for dark in (False, True):
        icon = icons.standard_icon(name, _palette(dark), size=size)
        variant, grid = ("dark" if dark else "light"), (16 if size == 16 else 22)
        stock = QIcon(str(icons.ASSET_ROOT / variant / str(grid) / f"{name}.svg"))
        for dpr in (1., 2.):
            normal = _pixels(icon, size, dpr)
            assert np.array_equal(normal, _pixels(stock, size, dpr))
            assert normal[:, :, 3].min() == 0  # no opaque rectangle
            ink = normal[:, :, 3] > 200
            assert ink.any()
            brightness = normal[:, :, :3][ink].mean()
            if name == "process-stop":
                # Stock Breeze uses its negative-action red, not text ink.
                assert np.allclose(normal[:, :, :3][ink].mean(axis=0), (218, 68, 83), atol=2)
            else:
                assert brightness > 200 if dark else brightness < 100
            disabled = _pixels(icon, size, dpr, QIcon.Disabled)
            assert disabled[:, :, 3].any()
            assert not np.array_equal(disabled, normal)
            assert _pixels(icon, size, dpr, QIcon.Active)[:, :, 3].any()


def test_bundled_stock_svg_manifest_and_licenses():
    manifest = json.loads((icons.ASSET_ROOT / "manifest.json").read_text())
    assert manifest["source_version"] == "4:5.116.0-1"
    assert manifest["license"] == "LGPL-3.0-or-later"
    actual = {p.relative_to(icons.ASSET_ROOT).as_posix() for p in icons.ASSET_ROOT.rglob("*.svg")}
    assert actual == {f["path"] for f in manifest["files"]}
    assert len(actual) == len(icons.ICON_NAMES) * 2 * 2
    for entry in manifest["files"]:
        source = (icons.ASSET_ROOT / entry["path"]).read_bytes()
        assert hashlib.sha256(source).hexdigest() == entry["sha256"]
        svg = ET.fromstring(source)
        size = entry["path"].split("/")[1]
        assert svg.attrib["viewBox"] == f"0 0 {size} {size}"
    assert "GNU LESSER GENERAL PUBLIC LICENSE" in (icons.ASSET_ROOT / "LICENSE.LGPL-3").read_text()
    assert "GNU GENERAL PUBLIC LICENSE" in (icons.ASSET_ROOT / "LICENSE.GPL-3").read_text()
    assert "Uri Herrera" in (icons.ASSET_ROOT / "COPYRIGHT").read_text()


def test_missing_asset_and_unknown_name_fail_loudly(tmp_path, monkeypatch):
    monkeypatch.setattr(icons, "ASSET_ROOT", tmp_path)
    with pytest.raises(FileNotFoundError, match="Missing bundled icon"):
        icons.standard_icon("edit-rename")
    with pytest.raises(ValueError, match="No bundled action icon"):
        icons.standard_icon("custom-glyph")


def test_registered_icons_follow_window_palette_and_theme_without_actions(tmp_path):
    window = QWidget()
    window.setPalette(_palette())
    binder = icons.ActionIcons(window)
    button = QPushButton(window)
    button.setIconSize(QSize(20, 20))
    button.setEnabled(False)
    action = QAction("Save", window)
    binder.bind(button, "edit-rename")
    binder.bind(action, "document-save")
    triggered = []
    button.clicked.connect(lambda: triggered.append("button"))
    action.triggered.connect(lambda: triggered.append("action"))
    initial = _pixels(button.icon(), 20)
    window.setPalette(_palette(True))
    assert not np.array_equal(initial, _pixels(button.icon(), 20))
    assert not button.isEnabled() and button.iconSize() == QSize(20, 20)
    # A control may deliberately retain a light/native surface in a dark
    # window. Its fallback must use that actual surface, not the window's.
    button.setPalette(_palette(False))
    assert np.array_equal(initial, _pixels(button.icon(), 20))
    _theme(tmp_path)
    QApplication.sendEvent(window, QEvent(QEvent.ThemeChange))
    assert np.array_equal(_pixels(action.icon()), _pixels(QIcon.fromTheme("document-save")))
    assert not triggered
    window.deleteLater()
    _app.sendPostedEvents(None, QEvent.DeferredDelete)


def test_toolbar_context_controls_action_fallback_and_live_refresh():
    window = QWidget()
    window.setPalette(_palette(True))
    toolbar = QToolBar(window)
    toolbar.setPalette(_palette(False))
    action = toolbar.addAction("Save")
    binder = icons.ActionIcons(window)
    binder.bind(action, "document-save", context=toolbar)
    assert np.array_equal(_pixels(action.icon()),
                          _pixels(icons.standard_icon("document-save", _palette(False))))
    toolbar.setPalette(_palette(True))
    assert np.array_equal(_pixels(action.icon()),
                          _pixels(icons.standard_icon("document-save", _palette(True))))
    window.deleteLater()
    _app.sendPostedEvents(None, QEvent.DeferredDelete)
