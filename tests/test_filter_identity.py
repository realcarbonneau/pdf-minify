"""Designer §155: persistent, hidden, unique UUIDv4 filter identities."""

import copy
from types import SimpleNamespace
import uuid

import pytest
from PySide6.QtCore import QSettings

from pdf_minify.core import identity, presets
from pdf_minify.ui_qt.app import MainWindow

DEFAULTS = copy.deepcopy(presets.PRESETS)


@pytest.fixture
def registry(monkeypatch):
    settings = QSettings("pdf-minify", "pdf-minify")
    kept = {key: settings.value(key) for key in settings.allKeys()}
    settings.clear()
    monkeypatch.setattr(presets, "PRESETS", copy.deepcopy(DEFAULTS))
    model = SimpleNamespace(_custom_store=lambda: settings)
    yield model, settings
    settings.clear()
    for key, value in kept.items():
        settings.setValue(key, value)


def test_builtin_uuids_are_unique_persistent_random_ids():
    values = [p["uuid"] for p in DEFAULTS]
    assert len(set(values)) == len(values)
    assert all(uuid.UUID(value).version == 4 for value in values)


def test_random_uuid_generator_never_uses_network_identity(monkeypatch):
    def forbidden():
        raise AssertionError("UUIDv4 must not consult a network card")
    monkeypatch.setattr(uuid, "getnode", forbidden)
    values = [identity.new_filter_uuid() for _ in range(100)]
    assert len(set(values)) == 100
    assert all(uuid.UUID(value).version == 4 for value in values)


def test_generation_checks_even_an_injected_collision(monkeypatch):
    taken, fresh = uuid.uuid4(), uuid.uuid4()
    choices = iter((taken, fresh))
    monkeypatch.setattr(uuid, "uuid4", lambda: next(choices))
    assert identity.new_filter_uuid([str(taken).upper()]) == str(fresh)


def test_repairs_missing_invalid_duplicate_and_noncanonical_ids():
    first, last = str(uuid.uuid4()), str(uuid.uuid4())
    filters = [{"uuid": first}, {"uuid": first.upper()}, {}, {"uuid": "bad"},
               {"uuid": last.upper()}, {"uuid": str(uuid.uuid1(node=0))}]
    assert identity.repair_filter_uuids(filters)
    values = [p["uuid"] for p in filters]
    assert len(set(values)) == len(values)
    assert values[0] == first and values[4] == last
    assert all(identity.canonical_uuid(value) == value for value in values)
    assert not identity.repair_filter_uuids(filters)  # stable on the next load


def test_loading_pasted_duplicate_record_preserves_both_filters(registry):
    model, settings = registry
    record = copy.deepcopy(presets.get("bw-t180"))
    settings.setValue("customPresets", [record, copy.deepcopy(record)])
    MainWindow._apply_custom_presets(model)
    loaded = settings.value("customPresets")
    assert len(loaded) == 2
    assert loaded[0]["label"] == loaded[1]["label"]
    assert loaded[0]["params"] == loaded[1]["params"]
    assert loaded[0]["id"] != loaded[1]["id"]
    assert loaded[0]["uuid"] != loaded[1]["uuid"]
    uuids = [p["uuid"] for p in presets.PRESETS]
    assert len(set(uuids)) == len(uuids)
    repaired = copy.deepcopy(loaded)
    presets.PRESETS[:] = copy.deepcopy(DEFAULTS)
    MainWindow._apply_custom_presets(model)
    assert settings.value("customPresets") == repaired
    assert all(presets.get(p["id"])["uuid"] == p["uuid"] for p in repaired)


@pytest.mark.parametrize("value", (None, "not-a-uuid", DEFAULTS[1]["uuid"].upper()))
def test_loaded_custom_identity_is_repaired_and_persisted(registry, value):
    model, settings = registry
    record = copy.deepcopy(presets.get("bw-t180"))
    record["id"] = "legacy-pasted-custom"
    record["uuid"] = value
    settings.setValue("customPresets", [record])
    MainWindow._apply_custom_presets(model)
    loaded = presets.get(record["id"])
    assert identity.canonical_uuid(loaded["uuid"]) == loaded["uuid"]
    assert loaded["uuid"] != DEFAULTS[1]["uuid"]
    assert settings.value("customPresets")[0]["uuid"] == loaded["uuid"]


def test_legacy_saved_builtin_gains_persistent_uuid_on_load(registry):
    model, settings = registry
    record = copy.deepcopy(presets.get("bw-t180"))
    expected = record.pop("uuid")
    settings.setValue("customPresets", [record])
    MainWindow._apply_custom_presets(model)
    assert presets.get("bw-t180")["uuid"] == expected
    assert settings.value("customPresets")[0]["uuid"] == expected


def test_pasted_alias_with_already_unique_uuid_keeps_that_identity(registry):
    model, settings = registry
    first = copy.deepcopy(presets.get("bw-t180"))
    second = copy.deepcopy(first)
    second["uuid"] = str(uuid.uuid4())
    settings.setValue("customPresets", [first, second])
    MainWindow._apply_custom_presets(model)
    loaded = settings.value("customPresets")
    assert [p["uuid"] for p in loaded] == [first["uuid"], second["uuid"]]
    assert len({p["id"] for p in loaded}) == 2
