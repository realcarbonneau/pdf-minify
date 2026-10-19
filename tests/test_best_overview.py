"""Best-only primary matrix; immutable fixed-encoder binary reference (§258)."""

from copy import deepcopy
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image
import pytest

from tools import bench_best_overview as bench


def record(document, recipe, size):
    return dict(document=document.key, recipe=recipe.key,
                result=dict(stream_policy="best", exact_semantic_graph=True, complete_pdf_bytes=size))


def test_primary_catalog_has_one_policy_free_row_per_recipe_and_no_prediction():
    assert len(bench.RECIPES) == len({r.key for r in bench.RECIPES}) == 19
    assert len(bench.RECIPES) * len(bench.overview.DOCUMENTS) == 114
    assert {r.section for r in bench.RECIPES} == {bench.REFERENCE, bench.BW, bench.INDEXED, bench.COLOR}
    for recipe in bench.RECIPES:
        assert not any(word in recipe.label for word in ("Best", "Brotli", "Zopfli", "Flate", "residual"))
        assert not recipe.variant.endswith("-png")
        assert ("FFPR" in recipe.label) == ("ffpr" in recipe.family)
    indexed = [r for r in bench.RECIPES if r.section == bench.INDEXED]
    assert max(i for i, r in enumerate(indexed) if "ffpr" not in r.family) < min(
        i for i, r in enumerate(indexed) if "ffpr" in r.family)


def test_matrix_requires_all_114_actual_cells_in_one_table_with_six_inputs():
    records = [record(d, r, 123456) for d in bench.overview.DOCUMENTS for r in bench.RECIPES]
    table = bench.table(bench.overview.DOCUMENTS, bench.RECIPES, records)
    assert table.count("**123,456**") == 114
    assert len(table.splitlines()) == 25  # header, separator, four dividers, 19 recipes
    assert all(len(line.split("|")[1:-1]) == 7 for line in table.splitlines())
    for section in (bench.REFERENCE, bench.BW, bench.INDEXED, bench.COLOR):
        assert f"| **{section}** | | | | | | |" in table
    with pytest.raises(ValueError, match="Missing measured Best cell"):
        bench.table(bench.overview.DOCUMENTS, bench.RECIPES, records[:-1])
    with pytest.raises(ValueError, match="Duplicate Best"):
        bench.table(bench.overview.DOCUMENTS, bench.RECIPES, records + records[:1])


@pytest.mark.parametrize("bad", [0, -10, True, 1.5])
def test_matrix_cannot_publish_invalid_sizes(bad):
    d, r = bench.overview.DOCUMENTS[0], bench.RECIPES[0]
    with pytest.raises(ValueError, match="positive measured integer"):
        bench.table([d], [r], [record(d, r, bad)])


def test_matrix_cannot_relabel_fixed_policy_measurements_as_best():
    d, r = bench.overview.DOCUMENTS[0], bench.RECIPES[0]
    row = record(d, r, 1000)
    row["result"]["stream_policy"] = "brotli"
    with pytest.raises(ValueError, match="actual verified Best"):
        bench.table([d], [r], [row])


def test_bold_minima_remain_separate_for_native_ffpr_and_palette_targets():
    d = bench.overview.DOCUMENTS[0]
    recipes = [r for r in bench.RECIPES if r.key in
               ("bw-jbig2", "bw-packed", "bw-ffpr-jbig2", "indexed-5", "indexed-16")]
    table = bench.table([d], recipes, [record(d, r, size) for r, size in
                        zip(recipes, (100, 200, 400, 500, 900), strict=True)])
    assert "| BW + JBIG2 | **100** |" in table
    assert "| BW + packed samples | 200 |" in table
    assert "| BW FFPR + JBIG2 | **400** |" in table
    assert "| Indexed 5 colors | **500** |" in table
    assert "| Indexed 16 colors | **900** |" in table


@pytest.fixture(scope="module")
def real_best(tmp_path_factory):
    folder = tmp_path_factory.mktemp("best-overview")
    source, base = folder / "source.pdf", folder / "base.pdf"
    with bench.study.fitz.open() as doc:
        page = doc.new_page(width=36, height=48)
        page.insert_text((2, 8), "Text", fontsize=4)
        pixels = np.zeros((12, 12, 3), dtype=np.uint8)
        pixels[::2] = (255, 128, 0)
        payload = io.BytesIO()
        Image.fromarray(pixels).save(payload, format="PNG")
        page.insert_image(bench.study.fitz.Rect(2, 12, 30, 40), stream=payload.getvalue())
        doc.save(source)
    spec = dict(mode="indexed", dpi_cap=300, colors=5)
    bench.study.pipeline.save_with_spec(str(source), str(base), spec)
    document = bench.overview.Document("tiny", "Tiny real input", str(source))
    recipe = next(r for r in bench.RECIPES if r.key == "indexed-5")
    case = dict(id="tiny-indexed", source=str(source), input_sha256=bench.digest(source),
                mode="indexed", dpi=300, recipe=spec,
                bases={recipe.variant: dict(pdf=str(base), sha256=bench.digest(base))})
    saved = bench.study.run_case(case, folder / "fixed", policies=("zopfli",))
    seed = dict(case=case, result=saved["results"][0])
    identity = dict(producing_implementation="unit-test")
    target = folder / "best"
    result = bench.measure(document, recipe, seed, target, identity)
    return document, recipe, seed, target, identity, result


def test_real_shared_saver_measures_best_without_preparation_or_jstar_encoding(real_best, monkeypatch):
    document, recipe, seed, target, identity, result = real_best
    bench.validate_measured(result)
    actual = result["result"]
    assert actual["complete_pdf_bytes"] == Path(actual["pdf"]).stat().st_size
    assert actual["selection"]["image_streams"] > 0
    assert actual["complete_pdf_bytes"] == min(actual["selection"]["candidate_bytes"].values())
    assert "encode_seconds" not in actual["selection"]
    with bench.study.fitz.open(actual["pdf"]) as output, bench.study.fitz.open(seed["result"]["pdf"]) as fixed:
        assert bench.semantic_graph(output, include_ids=False) == bench.semantic_graph(fixed, include_ids=False)
        assert not bench.study.streams.brotli_declaration_present(output)
    monkeypatch.setattr(bench.best, "save_best_streams", lambda *a, **k: pytest.fail("re-encoded completed Best"))
    assert bench.measure(document, recipe, seed, target, identity, resume=True) == result


def test_resume_rejects_changed_identity_and_actual_output_tampering(real_best, tmp_path):
    document, recipe, seed, target, identity, result = real_best
    with pytest.raises(ValueError, match="changed Best input"):
        bench.measure(document, recipe, seed, target, dict(identity, changed=True), resume=True)
    copy = deepcopy(result)
    damaged = tmp_path / "changed.pdf"
    damaged.write_bytes(Path(copy["result"]["pdf"]).read_bytes() + b"extra")
    copy["result"]["pdf"] = str(damaged)
    with pytest.raises(ValueError, match="Changed measured Best"):
        bench.validate_measured(copy)
    copy = deepcopy(result)
    copy["result"]["selection"]["candidate_bytes"]["pretend-smaller"] = 1
    with pytest.raises(ValueError, match="actual saved candidate minimum"):
        bench.validate_measured(copy)


def test_changed_fixed_publication_and_mismatched_binary_recipe_are_rejected(tmp_path):
    path = tmp_path / "changed-publication.json"
    path.write_text("{}")
    with pytest.raises(ValueError, match="Changed frozen"):
        bench.load_publication(path)
    d, recipe = bench.overview.DOCUMENTS[0], bench.RECIPES[1]
    index = {}
    for policy in ("brotli", "zopfli"):
        index[d.key, recipe.family, recipe.variant, policy] = dict(
            case=dict(source=d.source, dpi=300, recipe=dict(mode="bw", t=180)),
            result=dict(image_variant=recipe.variant, native_policy=policy))
    bench.fixed_pair(d, recipe, index)
    index[d.key, recipe.family, recipe.variant, "zopfli"]["case"]["recipe"]["t"] = 210
    with pytest.raises(ValueError, match="changes preparation or recipe"):
        bench.fixed_pair(d, recipe, index)


@pytest.mark.parametrize("kind", ["incomplete", "changed-identity", "missing-cells"])
def test_publisher_refuses_partial_or_incompatible_studies_without_running_encoders(tmp_path, monkeypatch, kind):
    from tools import publish_best_overview as publisher
    monkeypatch.setattr(bench, "load_publication", lambda *a: dict(records=[], ffpr_pairs=[]))
    monkeypatch.setattr(bench, "identity", lambda *a: dict(fixed="identity"))
    monkeypatch.setattr(bench.best, "save_best_streams", lambda *a, **k: pytest.fail("publication encoded a PDF"))
    path = tmp_path / "metrics.json"
    path.write_text(json.dumps(dict(complete=kind != "incomplete", records=[],
                                    identity=dict(fixed="changed" if kind == "changed-identity" else "identity"))))
    with pytest.raises(ValueError, match="Incomplete or incompatible|all 114"):
        publisher.audit(path)


def test_semantic_proof_detects_geometry_native_and_decoded_image_changes(real_best):
    _, _, seed, _, _, _ = real_best
    path = seed["result"]["pdf"]
    for kind in ("native", "geometry", "samples", "metadata"):
        with bench.study.fitz.open(path) as doc:
            before = bench.semantic_graph(doc)
            if kind == "native":
                doc[0].insert_text((2, 42), "Changed", fontsize=4)
            elif kind == "geometry":
                doc[0].set_rotation(90)
            elif kind == "metadata":
                doc.set_metadata(dict(doc.metadata, title="Changed"))
            else:
                xref = next(x for x, image in bench.best._eligible_xrefs(doc) if image)
                data = doc.xref_stream(xref)
                doc.update_stream(xref, bytes([data[0] ^ 1]) + data[1:], compress=False)
                doc.xref_set_key(xref, "Filter", "null")
            assert bench.semantic_graph(doc) != before, kind


def test_published_primary_and_binary_tables_match_all_measured_cells():
    from tools import publish_best_overview as publisher
    from tools import publish_lossy_controls as lossy

    frozen = json.loads(Path("tests/fixtures/best_overview_sizes.json").read_text())
    current = json.loads(lossy.FIXTURE.read_text())
    assert frozen["designer_ruling"] == 258 and frozen["stream_policy"] == "best"
    assert frozen["brotli_declaration"] is False
    assert frozen["fixed_publication_sha256"] == bench.PUBLICATION_SHA256
    assert frozen["documents"] == [vars(d) for d in bench.overview.DOCUMENTS]
    assert len(frozen["rows"]) == 19
    report = Path("docs/INTEGRATED_COMPRESSION.md").read_text()
    primary = report.split("## Overview — final complete-file bytes", 1)[1].split(bench.overview.PNG_SECTION, 1)[0]
    assert "Every row uses **Best (Zopfli/Brotli)**" in primary
    assert "#stream-compression--zopfli-versus-brotli-baseline" in primary
    binary = report.split("## Stream compression — Zopfli versus Brotli baseline", 1)[1]
    binary = binary.split("### FFPR/J* subset", 1)[0]
    records = [record(d, recipe, row["best"][i])
               for recipe, row in zip(bench.RECIPES, frozen["rows"], strict=True)
               for i, d in enumerate(bench.overview.DOCUMENTS)]
    expected = publisher.current_primary(publisher.display_table(
        bench.table(bench.overview.DOCUMENTS, bench.RECIPES, records)))
    assert expected.strip() in primary
    for section in (primary, binary):
        assert "| BW |" in section and "| BW FFPR |" in section
        assert "| BW + packed samples |" not in section
        assert "| BW FFPR + packed samples |" not in section
    parsed = {cells[0]: cells[1:] for line in binary.splitlines() if line.startswith("| ")
              if (cells := [c.strip() for c in line.split("|")[1:-1]])}
    audited = 0
    for recipe, row in zip(bench.RECIPES, frozen["rows"], strict=True):
        assert row["key"] == recipe.key and row["label"] == recipe.label
        assert len(row["pdf_sha256"]) == 6 and all(len(h) == 64 for h in row["pdf_sha256"])
        measured = lossy.updated_fixed_row(row, current)
        label = lossy.current_label(recipe.label).removesuffix(" + packed samples")
        assert parsed[label] == [bench.overview.measured_effect_cell(a, b, show_size=False)
                                 for a, b in zip(measured["brotli"], measured["zopfli"], strict=True)]
        audited += len(row["best"])
    assert audited == 114
    controls = report.split("### Fixed-encoder controls — measured final PDF bytes", 1)[1].split("## Focused scenarios", 1)[0]
    control_rows = {cells[0]: cells[1:] for line in controls.splitlines() if line.startswith("| ")
                    if (cells := [c.strip() for c in line.split("|")[1:-1]])}
    decode = lambda value: int(value.replace("*", "").replace(",", ""))
    for row in frozen["rows"]:
        row = lossy.updated_fixed_row(row, current)
        for policy in ("brotli", "zopfli"):
            assert [decode(c) for c in control_rows[row["fixed_labels"][policy]]] == row[policy]
    assert [decode(c) for c in control_rows["Preserve images + Classic Flate (reference) native"]] == frozen["classic_reference"]


def test_fixed_controls_are_relocated_not_removed_and_png_denominators_stay_fixed():
    report = Path("docs/INTEGRATED_COMPRESSION.md").read_text()
    primary = report.split("## Overview — final complete-file bytes", 1)[1].split(bench.overview.PNG_SECTION, 1)[0]
    binary = report.split("## Stream compression — Zopfli versus Brotli baseline", 1)[1].split("## Focused scenarios", 1)[0]
    assert "Classic Flate (reference) native |" not in primary
    assert "Preserve images + Classic Flate (reference) native |" in binary
    assert "<details" not in binary and "<summary" not in binary and "</details>" not in binary
    assert "### Replace Brotli with Zopfli — final PDF size change (%)\n\n|" in binary
    assert "### FFPR/J* subset — current NATIVE-02 findings" in binary
    png = report.split(bench.overview.PNG_SECTION, 1)[1].split("## Stream compression", 1)[0]
    assert "fixed-encoder plain baseline" in png and "No denominator or PNG measurement changes" in png


def test_publisher_fixed_controls_remain_visible_without_a_drawer(monkeypatch):
    from tools import publish_best_overview as publisher
    sentinel = object()
    table = "| Fixed-policy combination | Input |\n|---|---:|\n| Control | 123 |\n"
    seen = []

    def fixed_controls(publication):
        seen.append(publication)
        return table

    monkeypatch.setattr(publisher, "fixed_controls", fixed_controls)
    section = publisher.fixed_controls_section(sentinel)
    assert seen == [sentinel]
    assert "<details" not in section and "<summary" not in section
    assert section.endswith("\n\n" + table + "\n")
    assert section.startswith("### Fixed-encoder controls — measured final PDF bytes\n\n")
