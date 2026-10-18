"""Explicitly authorized one-time 300-DPI migration, not an ongoing clamp."""

import copy
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from pdf_minify.core import presets
from pdf_minify.core.algorithms import ALGORITHMS
from pdf_minify.core.filter_defaults import (RASTER_DEFAULTS_REVISION, migrate_raster_dpi,
    STREAM_DEFAULTS_REVISION, DEFAULT_APP_STREAM_POLICY, migrate_stream_compression)
from pdf_minify.core.recipes import preset_spec
from pdf_minify.ui_qt.settings import sync_settings
from pdf_minify.ui_qt.app import MainWindow

app = QApplication.instance() or QApplication([])


@pytest.mark.parametrize("dpi", [72, 150, 200, 600])
def test_migration_changes_only_active_and_retained_dpi_fields(dpi):
    filters = [dict(id=mode, uuid=f"identity-{mode}", label=f"Saved {mode}", mode=mode,
                    params=dict(dpi=dpi, dpi_cap=dpi, force_raster=True, page_size="a4",
                                colors=16, jpeg_q=74, stream_compression="brotli"))
               for mode, _ in ALGORITHMS]
    before = copy.deepcopy(filters)
    assert migrate_raster_dpi(filters) == [p["id"] for p in filters]
    for old, new in zip(before, filters):
        assert {k: v for k, v in old.items() if k != "params"} == {k: v for k, v in new.items() if k != "params"}
        assert new["params"] == dict(old["params"], dpi=300, dpi_cap=300)
    assert not migrate_raster_dpi(filters)


@pytest.mark.parametrize("revision", [None, "not-a-number"])
def test_settings_migrate_custom_and_builtin_overrides_once_then_keep_deliberate_values(tmp_path, monkeypatch, revision):
    previous = copy.deepcopy(presets.PRESETS)
    monkeypatch.setattr(presets, "PRESETS", copy.deepcopy(previous))
    store = QSettings(str(tmp_path / "filters.ini"), QSettings.IniFormat)
    custom = dict(id="saved-copy", uuid="fc5ae502-a5e8-44a6-8ffa-e2d1510a968e", label="Custom copy",
                  blurb="Saved custom recipe", mode="indexed",
                  params=dict(dpi_cap=150, colors=4, force_raster=True))
    builtin = copy.deepcopy(presets.get("color-j2k"))
    builtin["params"]["dpi_cap"] = 200
    store.setValue("customPresets", [builtin, custom])
    store.setValue("customRenames", {"color-j2k": "Renamed JPX"})
    if revision is not None:
        store.setValue("rasterDefaultsRevision", revision)
    monkeypatch.setattr(MainWindow, "_custom_store", lambda self: store)
    w = MainWindow(None)
    assert all(spec.get("dpi", spec.get("dpi_cap")) == 300 for spec in w._saved_specs.values())
    migrated = store.value("customPresets")
    assert all(p["params"].get("dpi", p["params"].get("dpi_cap")) == 300 for p in migrated)
    assert store.value("rasterDefaultsRevision", type=int) == RASTER_DEFAULTS_REVISION
    assert presets.get("saved-copy")["uuid"] == custom["uuid"]
    assert presets.get("saved-copy")["params"]["force_raster"]
    assert w._preset_label("color-j2k") == "Renamed JPX" and not w._draft_specs
    w.close()
    # A later explicit edit is not another request to reapply the default.
    migrated[-1]["params"]["dpi_cap"] = 150
    store.setValue("customPresets", migrated)
    w = MainWindow(None)
    assert w._saved_specs["saved-copy"]["dpi_cap"] == 150
    assert presets.get("saved-copy")["uuid"] == custom["uuid"]
    w.close()


@pytest.mark.parametrize("policy", [None, "flate", "zopfli", "brotli", "best"])
def test_best_migration_changes_only_the_stream_policy_across_all_image_modes(policy):
    filters = [dict(id=mode, uuid=f"identity-{mode}", label=f"Saved {mode}", mode=mode,
                    metadata={"retained": [1, 2, 3]},
                    params=dict(dpi=150, dpi_cap=200, force_raster=True, page_size="a4",
                                colors=16, jpeg_q=74, brotli_declaration=True))
               for mode, _ in ALGORITHMS]
    if policy is not None:
        for preset in filters:
            preset["params"]["stream_compression"] = policy
    original = dict(id="orig", mode="passthrough", params={})
    filters.append(original)
    before = copy.deepcopy(filters)
    changed = migrate_stream_compression(filters)
    assert changed == ([] if policy == "best" else [mode for mode, _ in ALGORITHMS])
    assert filters[-1] == before[-1] and filters[-1] is original
    for old, new in zip(before[:-1], filters[:-1]):
        assert new == dict(old, params=dict(old["params"], stream_compression="best"))
    assert not migrate_stream_compression(filters)


def test_every_builtin_app_filter_seeds_best_but_original_and_headless_legacy_are_unchanged():
    assert DEFAULT_APP_STREAM_POLICY == "best"
    for preset in presets.PRESETS:
        if preset["mode"] == "passthrough":
            assert preset["params"].get("stream_compression") is None
        else:
            assert preset["params"]["stream_compression"] == "best"
            assert preset_spec(preset)["stream_compression"] == "best"
    assert preset_spec(dict(mode="indexed", params={}))["stream_compression"] == "flate"


@pytest.mark.parametrize("revision", [None, 0, "invalid-revision"])
def test_all_saved_filters_migrate_once_without_losing_metadata_or_later_choices(tmp_path, monkeypatch, revision):
    templates = copy.deepcopy(presets.PRESETS)
    monkeypatch.setattr(presets, "PRESETS", copy.deepcopy(templates))
    store = QSettings(str(tmp_path / "best-defaults.ini"), QSettings.IniFormat)
    saved = []
    for index, (mode, _) in enumerate(ALGORITHMS):
        saved.append(dict(id=f"saved-{mode}", uuid=f"00000000-0000-4000-8000-{index:012d}",
                          label=f"Keep {mode}", blurb="Saved migration fixture", mode=mode,
                          customMetadata={"keep": [index]},
                          params=dict(dpi=150, dpi_cap=200, strategy="simple", t=173,
                                      colors=16, rate=96, lossless=True, jpeg_q=74,
                                      force_raster=True, page_size="a4", brotli_declaration=True,
                                      stream_compression=("flate", "zopfli", "brotli")[index % 3])))
    override = copy.deepcopy(presets.get("color-j2k"))
    override["params"].update(stream_compression="zopfli", dpi_cap=150, lossless=True)
    override["customMetadata"] = {"must": "survive built-in override migration"}
    saved.append(override)
    before = copy.deepcopy(saved)
    store.setValue("customPresets", saved)
    order = [p["id"] for p in saved][::-1]
    store.setValue("stripOrder", order)
    renames = {"color-j2k": "Keep my renamed JPEG2000"}
    store.setValue("customRenames", renames)
    # The DPI migration was already completed; this request must not reset it.
    store.setValue("rasterDefaultsRevision", RASTER_DEFAULTS_REVISION)
    if revision is not None:
        store.setValue("streamDefaultsRevision", revision)
    monkeypatch.setattr(MainWindow, "_custom_store", lambda self: store)
    w = MainWindow(None)
    try:
        assert all(spec["stream_compression"] == "best" for spec in w._saved_specs.values())
        assert not w._draft_specs and not w._preview_timer.isActive() and not w._artifacts.pending
        assert w.stream_compression.currentData() == "best"
        assert w._strip_ids[:len(order)] == order
        assert store.value("stripOrder") == order and store.value("customRenames") == renames
        assert store.value("streamDefaultsRevision", type=int) == STREAM_DEFAULTS_REVISION
        migrated = store.value("customPresets")
        assert migrated == [dict(p, params=dict(p["params"], stream_compression="best")) for p in before]
    finally:
        w.close()
    # Fresh-process seeds, and a deliberate subsequent saved choice.
    migrated[0]["params"]["stream_compression"] = "flate"
    migrated[-1]["params"]["stream_compression"] = "brotli"
    store.setValue("customPresets", migrated)
    monkeypatch.setattr(presets, "PRESETS", copy.deepcopy(templates))
    w = MainWindow(None)
    try:
        assert w._saved_specs[migrated[0]["id"]]["stream_compression"] == "flate"
        assert w._saved_specs["color-j2k"]["stream_compression"] == "brotli"
        assert store.value("customPresets") == migrated
        assert presets.get(migrated[0]["id"])["uuid"] == before[0]["uuid"]
    finally:
        w.close()


def test_settings_sync_failure_is_not_reported_as_a_completed_migration(tmp_path):
    class FailingStore:
        called = False

        def sync(self):
            self.called = True

        def status(self):
            return QSettings.AccessError

        def fileName(self):
            return str(tmp_path / "not-writable.ini")

    store = FailingStore()
    with pytest.raises(OSError, match="Cannot synchronize"):
        sync_settings(store)
    assert store.called
