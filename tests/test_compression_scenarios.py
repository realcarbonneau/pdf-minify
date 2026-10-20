"""Focused comparisons keep meaningful palette/threshold axes, not DPI noise."""

from pathlib import Path

import pytest

from tools import bench_compression_scenarios as scenarios


def test_focused_scope_is_unique_at_uniform_300dpi():
    assert len({s.key for s in scenarios.SCENARIOS}) == len(scenarios.SCENARIOS) == 9
    assert all(Path(s.source).is_file() for s in scenarios.SCENARIOS)
    assert scenarios.identity()["dpi"] == 300
    assert sum(len(scenarios.rows_for(s)) for s in scenarios.SCENARIOS) == 48
    for scenario in scenarios.SCENARIOS:
        for row in scenarios.rows_for(scenario):
            if row.variant.startswith(("flate-", "zopfli-", "brotli-")):
                assert row.variant.split("-")[0] == row.native


@pytest.mark.parametrize("kind", ["art", "mixed"])
def test_additional_palette_cases_do_not_repeat_five_color_overview(kind):
    cases = [s for s in scenarios.SCENARIOS if s.key.startswith(kind) and s.family == "indexed"]
    assert {s.colors for s in cases} == {16, 64}


def test_redundant_classic_flate_bitmap_rows_are_removed_from_every_focused_table():
    from tools import benchmark_tables as tables
    for scenario in scenarios.SCENARIOS:
        rows = scenarios.rows_for(scenario)
        if scenario.family != "preserve-images":
            assert len(rows) == 6 and not any(r.native == "flate" for r in rows)
        else:
            assert any(r.native == "flate" for r in rows), scenario.key
    page = tables.PAGE.read_text()
    for table_id, base in (("focused-artwork", "indexed"), ("focused-mixed", "indexed"),
                           ("focused-scan", "bw"), ("focused-thresholds", "bw")):
        assert set(tables.read_table(page, table_id).rows) == {
            f"{base}.zopfli", f"{base}.zopfli.png", f"{base}.brotli", f"{base}.brotli.png",
            f"{base}-jbig2.zopfli", f"{base}-jbig2.brotli"}, table_id


def test_unresampled_classic_control_stays_in_applicable_focused_sections():
    from tools import benchmark_tables as tables
    page = tables.PAGE.read_text()
    assert set(tables.read_table(page, "focused-native").rows) == {
        "reference.classic", "reference.zopfli", "reference.brotli"}
    photos = tables.read_table(page, "focused-photos").rows
    assert {"reference.classic", "reference.zopfli", "reference.brotli"} <= set(photos)


@pytest.mark.parametrize("key", ["art-16", "mixed-16", "naca", "art-t180"])
def test_preparation_encodes_only_the_selected_focused_variants(tmp_path, monkeypatch, key):
    scenario = next(s for s in scenarios.SCENARIOS if s.key == key)
    expected = {r.variant for r in scenarios.rows_for(scenario)}
    def prepare(source, folder, **settings):
        assert set(settings["variants"]) == expected
        folder.mkdir(parents=True)
        results = []
        for variant in settings["variants"]:
            target = folder / f"{variant}.pdf"
            target.write_bytes(variant.encode())
            results.append(dict(variant=variant, pdf=str(target),
                                pdf_sha256=scenarios.overview.file_digest(target)))
        return dict(source=str(source), input_sha256=scenarios.overview.file_digest(source),
                    mode=scenario.family, dpi=300, colors=scenario.colors,
                    threshold_method=scenario.strategy, threshold=None, prepared=[], results=results)
    monkeypatch.setattr(scenarios.study.images, "run_case", prepare)
    case = scenarios.prepare(scenario, tmp_path / "prepare", False)
    assert set(case["bases"]) == expected


def test_scenario_resume_rejects_implementation_changes(tmp_path, monkeypatch):
    import json
    folder = tmp_path / "study"
    folder.mkdir()
    (folder / "metrics.json").write_text(json.dumps(dict(identity={"changed": True})))
    monkeypatch.setattr(scenarios, "prepare", lambda *args: pytest.fail("No encoding after provenance mismatch"))
    with pytest.raises(ValueError, match="Changed focused-study"):
        scenarios.run(folder, resume=True)
