"""Explicitly authorized one-time 300-DPI migration, not an ongoing clamp."""

import copy
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from pdf_minimalist.core import presets
from pdf_minimalist.core.algorithms import ALGORITHMS
from pdf_minimalist.core.filter_defaults import RASTER_DEFAULTS_REVISION, migrate_raster_dpi
from pdf_minimalist.ui_qt.app import MainWindow

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
