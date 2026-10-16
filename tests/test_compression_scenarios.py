"""Focused comparisons keep meaningful palette/threshold axes, not DPI noise."""

from pathlib import Path

import pytest

from tools import bench_compression_scenarios as scenarios


def test_focused_scope_is_unique_at_uniform_300dpi():
    assert len({s.key for s in scenarios.SCENARIOS}) == len(scenarios.SCENARIOS) == 9
    assert all(Path(s.source).is_file() for s in scenarios.SCENARIOS)
    assert scenarios.identity()["dpi"] == 300
    assert sum(len(scenarios.rows_for(s)) for s in scenarios.SCENARIOS) == 62
    for scenario in scenarios.SCENARIOS:
        for row in scenarios.rows_for(scenario):
            if row.variant.startswith(("flate-", "zopfli-", "brotli-")):
                assert row.variant.split("-")[0] == row.native


@pytest.mark.parametrize("kind", ["art", "mixed"])
def test_additional_palette_cases_do_not_repeat_five_color_overview(kind):
    cases = [s for s in scenarios.SCENARIOS if s.key.startswith(kind) and s.family == "indexed"]
    assert {s.colors for s in cases} == {16, 64}


def test_scenario_resume_rejects_implementation_changes(tmp_path, monkeypatch):
    import json
    folder = tmp_path / "study"
    folder.mkdir()
    (folder / "metrics.json").write_text(json.dumps(dict(identity={"changed": True})))
    monkeypatch.setattr(scenarios, "prepare", lambda *args: pytest.fail("No encoding after provenance mismatch"))
    with pytest.raises(ValueError, match="Changed focused-study"):
        scenarios.run(folder, resume=True)
