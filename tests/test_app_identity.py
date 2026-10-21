"""§230: product rename without lost or resurrected user preferences."""

import copy
import os
import subprocess
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QByteArray, QSettings
from PySide6.QtWidgets import QApplication

from pdf_minify import APP_ID, APP_NAME
from pdf_minify.core import presets
from pdf_minify.ui_qt import app as ui, settings

app = QApplication.instance() or QApplication([])


@pytest.fixture
def stores(tmp_path, monkeypatch):
    """Exercise real Qt serialization without touching either user namespace."""
    def open_store(app_id):
        store = QSettings(str(tmp_path / f"{app_id}.ini"), QSettings.IniFormat)
        store.setFallbacksEnabled(False)
        store.sync()
        settings._check_status(store)
        return store

    monkeypatch.setattr(settings, "_user_settings", open_store)
    return open_store(APP_ID), open_store(settings.LEGACY_APP_ID)


def values(store):
    store.sync()
    return {key: store.value(key) for key in store.allKeys()}


def seed_legacy(store):
    saved = dict(id="saved-copy", uuid="b5aa2865-283f-4e40-989b-67de073af423",
                 label="My saved filter", blurb="My saved palette recipe", mode="indexed",
                 params=dict(dpi_cap=150, colors=4, force_raster=False,
                             stream_compression="zopfli"))
    data = dict(customPresets=[saved], customRenames={"bw-t180": "My BW"},
                stripOrder=["saved-copy", "color-j2k", "bw-t180"],
                rasterDefaultsRevision=1, lastFile="/documents/étude.pdf",
                geometry=QByteArray(b"\x00\x01window\xff"), empty="", enabled=False)
    for key, value in data.items():
        store.setValue(key, value)
    store.sync()
    return saved, values(store)


def test_migration_preserves_all_keys_types_and_the_legacy_file(stores):
    current, legacy = stores
    _, expected = seed_legacy(legacy)
    from pathlib import Path
    before = Path(legacy.fileName()).read_bytes()
    migrated = settings.app_settings()
    assert values(migrated) == dict(expected, identityMigrationRevision=1)
    for key, value in expected.items():
        assert type(migrated.value(key)) is type(value), key
    assert values(legacy) == expected
    assert Path(legacy.fileName()).read_bytes() == before
    assert values(current) == values(migrated)


def test_new_values_win_and_deletions_are_not_resurrected(stores):
    current, legacy = stores
    seed_legacy(legacy)
    current.setValue("lastFile", "/new/file.pdf")
    current.setValue("customPresets", [])  # deliberately empty is still a value
    current.sync()
    migrated = settings.app_settings()
    assert migrated.value("lastFile") == "/new/file.pdf"
    assert migrated.value("customPresets") == []
    migrated.remove("customRenames")
    migrated.remove("stripOrder")
    migrated.sync()
    legacy.setValue("lastFile", "/changed/legacy.pdf")
    legacy.sync()
    reopened = settings.app_settings()
    assert not reopened.contains("customRenames") and not reopened.contains("stripOrder")
    assert reopened.value("lastFile") == "/new/file.pdf"
    assert reopened.value("customPresets") == []


def test_empty_legacy_store_is_migrated_only_once(stores):
    current, legacy = stores
    assert settings.app_settings().value(settings.IDENTITY_MIGRATION_KEY, type=int) == 1
    legacy.setValue("lastFile", "/added/later.pdf")
    legacy.sync()
    assert not settings.app_settings().contains("lastFile")
    assert not current.contains("lastFile")


@pytest.mark.parametrize("revision", [None, "invalid", 0])
def test_missing_or_malformed_revision_imports_missing_values(stores, revision):
    current, legacy = stores
    legacy.setValue("lastFile", "/old/file.pdf")
    legacy.sync()
    if revision is not None:
        current.setValue(settings.IDENTITY_MIGRATION_KEY, revision)
        current.sync()
    assert settings.app_settings().value("lastFile") == "/old/file.pdf"
    assert current.value(settings.IDENTITY_MIGRATION_KEY, type=int) == 1


def test_review_snapshot_is_read_only_and_obeys_the_migration_marker(stores):
    current, legacy = stores
    _, expected = seed_legacy(legacy)
    current.setValue("lastFile", "/new/file.pdf")
    current.sync()
    before = values(current), values(legacy)
    assert settings.settings_snapshot() == dict(expected, lastFile="/new/file.pdf")
    assert (values(current), values(legacy)) == before
    settings.app_settings()
    current.remove("customPresets")
    current.sync()
    assert "customPresets" not in settings.settings_snapshot()


def test_unreadable_settings_are_reported_not_marked_migrated(stores, monkeypatch):
    class BrokenStore:
        def status(self):
            return QSettings.FormatError

        def fileName(self):
            return "/isolated/broken.ini"

    with pytest.raises(OSError, match="PDF Minify settings"):
        settings._check_status(BrokenStore())
    current, legacy = stores
    legacy.setValue("lastFile", "/old/file.pdf")
    legacy.sync()
    real_check = settings._check_status

    def fail_commit(store):
        if store.contains(settings.IDENTITY_MIGRATION_KEY):
            raise OSError("Cannot synchronize PDF Minify settings")
        real_check(store)

    monkeypatch.setattr(settings, "_check_status", fail_commit)
    with pytest.raises(OSError, match="Cannot synchronize"):
        settings.app_settings()


def test_migrated_filters_keep_uuid_name_order_and_deliberate_dpi(stores, monkeypatch):
    _, legacy = stores
    saved, _ = seed_legacy(legacy)
    monkeypatch.setattr(presets, "PRESETS", copy.deepcopy(presets.PRESETS))
    window = ui.MainWindow(None)
    try:
        assert window.windowTitle() == "PDF Minify[*]"
        assert window._custom_store().value("lastFile") == "/documents/étude.pdf"
        assert presets.get("saved-copy")["uuid"] == saved["uuid"]
        assert window._preset_label("saved-copy") == saved["label"]
        assert window._preset_label("bw-t180") == "My BW"
        assert window._strip_ids[:3] == ["saved-copy", "color-j2k", "bw-t180"]
        assert window._saved_specs["saved-copy"]["dpi_cap"] == 150
        assert window._saved_specs["saved-copy"]["colors"] == 4
        assert not window._draft_specs and not window.isWindowModified()
    finally:
        window.close()


def test_application_identity_and_cli_are_renamed():
    old = app.organizationName(), app.applicationName(), app.applicationDisplayName()
    try:
        settings.configure_application(app)
        assert (app.organizationName(), app.applicationName(), app.applicationDisplayName()) == (
            APP_ID, APP_ID, APP_NAME)
    finally:
        app.setOrganizationName(old[0])
        app.setApplicationName(old[1])
        app.setApplicationDisplayName(old[2])
    result = subprocess.run([sys.executable, "-m", "pdf_minify", "--help"],
                            capture_output=True, text=True, check=True, timeout=20)
    assert "usage: pdf-minify" in result.stdout
    assert "pdf_minimalist" not in result.stdout


def test_application_icon_is_the_bundled_product_icon():
    """§294: the window/taskbar icon comes from the bundled sizes, never a theme."""
    from PySide6.QtCore import QSize
    from pdf_minify.ui_qt.icons import APP_ICON_SIZES, app_icon
    icon = app_icon()
    assert not icon.isNull()
    assert {s.width() for s in icon.availableSizes()} == set(APP_ICON_SIZES)
    for size, corner_alpha in ((16, 255), (256, 1)):
        image = icon.pixmap(QSize(size, size)).toImage()
        assert image.width() == size and image.hasAlphaChannel()
        # Rounded corners are see-through (only partly at 16 px, where the radius is ~1 px).
        assert image.pixelColor(0, 0).alpha() < corner_alpha
        assert image.pixelColor(size // 2, size // 2).alpha() == 255
    settings.configure_application(app)
    assert {s.width() for s in app.windowIcon().availableSizes()} == set(APP_ICON_SIZES)


def test_application_identity_matches_the_installed_desktop_entry():
    """Packages install the desktop entry under DESKTOP_ID; the version is the package version."""
    from pathlib import Path
    from pdf_minify import DESKTOP_ID, __version__
    settings.configure_application(app)
    assert app.desktopFileName() == DESKTOP_ID
    entry = Path(__file__).parents[1] / "packaging" / "linux" / f"{DESKTOP_ID}.desktop"
    assert f"Icon={DESKTOP_ID}\n" in entry.read_text()
    assert app.applicationVersion() == __version__


def test_startup_last_file_uses_the_same_migrating_store(stores, monkeypatch, tmp_path):
    _, legacy = stores
    source = tmp_path / "remembered.pdf"
    source.touch()
    legacy.setValue("lastFile", str(source))
    legacy.sync()
    observed = []

    class FakeApplication:
        def __init__(self, _argv):
            pass

        def exec(self):
            return 0

        def installEventFilter(self, _handler):
            pass

    class FakeWindow:
        def __init__(self, pdf):
            observed.append(pdf)

        def show(self):
            pass

    monkeypatch.setattr(ui, "QApplication", FakeApplication)
    monkeypatch.setattr(ui, "MainWindow", FakeWindow)
    monkeypatch.setattr(ui, "FileOpenHandler", lambda window: None)
    monkeypatch.setattr(ui, "configure_application", lambda app: None)
    with pytest.raises(SystemExit) as result:
        ui.main()
    assert result.value.code == 0 and observed == [str(source)]
    assert settings.app_settings().value("lastFile") == str(source)


def test_version_is_major_minor_patch_and_the_same_everywhere():
    """§305: #.#.#, one source; the packaging copies must follow it."""
    import re
    from pathlib import Path
    from pdf_minify import DESKTOP_ID, __version__
    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__)
    root = Path(__file__).parents[1]
    changelog = (root / "debian" / "changelog").read_text(encoding="utf-8").splitlines()[0]
    assert changelog.startswith(f"pdf-minify ({__version__}-"), changelog
    metainfo = (root / "packaging" / "linux" / f"{DESKTOP_ID}.metainfo.xml").read_text(encoding="utf-8")
    assert f'<release version="{__version__}"' in metainfo
    manual = (root / "packaging" / "linux" / "pdf-minify.1").read_text(encoding="utf-8")
    assert f'"PDF Minify {__version__}"' in manual


def test_the_version_has_release_notes():
    """CHANGELOG.md's section for the version is its release page's text."""
    from pdf_minify import __version__
    result = subprocess.run([sys.executable, "tools/release_notes.py", f"v{__version__}"],
                            capture_output=True, text=True, encoding="utf-8",
                            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() and not result.stdout.startswith("## ")
    missing = subprocess.run([sys.executable, "tools/release_notes.py", "v99.99.99"],
                             capture_output=True, text=True, encoding="utf-8",
                             cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    assert missing.returncode != 0 and "no section for 99.99.99" in missing.stderr
