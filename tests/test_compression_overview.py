"""Representative overview selection/formatting without repeating costly encodes."""

from pathlib import Path

import pytest

from tools import bench_compression_overview as overview


def test_exactly_five_distinct_real_repository_classes():
    assert len(overview.DOCUMENTS) == 5
    assert len({d.source for d in overview.DOCUMENTS}) == 5
    assert all(Path(d.source).is_file() for d in overview.DOCUMENTS)
    assert {d.key for d in overview.DOCUMENTS} == {"native", "scan", "photos", "art", "mixed"}
    assert next(d.source for d in overview.DOCUMENTS if d.key == "photos").endswith("news-crater-lake-2026.pdf")
    assert next(d.source for d in overview.DOCUMENTS if d.key == "art").endswith("images.pdf")


def test_no_mixed_general_codecs_or_specialized_ffpr_policy_explosion():
    assert len(overview.ROWS) == 32
    assert len(set(overview.ROWS)) == 32
    for row in overview.ROWS:
        if row.variant.startswith(("flate-", "zopfli-", "brotli-")):
            assert row.variant.split("-")[0] == row.native
    residual = [r for r in overview.ROWS if r.family == "bw-ffpr" and r.variant == "jbig2"]
    assert len(residual) == 1 and residual[0].native == "zopfli"
    assert all("reference" in r.label for r in overview.ROWS if r.native == "flate")


def test_five_class_matrix_has_138_applicable_whole_file_cells():
    assert sum(overview.applicable(d, row) for d in overview.DOCUMENTS for row in overview.ROWS) == 138
    native = overview.DOCUMENTS[0]
    assert not overview.applicable(native, next(r for r in overview.ROWS if r.family == "indexed"))
    assert overview.applicable(native, next(r for r in overview.ROWS if r.family == "bw-ffpr"))


def test_transposed_table_bolds_ties_within_same_document_and_fidelity():
    documents = overview.DOCUMENTS[:2]
    rows = overview.ROWS[:3]
    records = [dict(document=d.key, family=row.family,
                    result=dict(image_variant=row.variant, native_policy=row.native, complete_pdf_bytes=value))
               for d, values in zip(documents, ((1000, 900, 900), (20, 15, 18)))
               for row, value in zip(rows, values)]
    table = overview.matrix_markdown(documents, rows, records)
    assert "| **900** | **15** |" in table
    assert "| **900** | 18 |" in table
    assert "| 1,000 | 20 |" in table
    assert "Z/B" not in table


def test_missing_applicable_measurement_is_error_not_blank_or_zero():
    with pytest.raises(ValueError, match="Missing measured cell"):
        overview.matrix_markdown(overview.DOCUMENTS[:1], overview.ROWS[:1], [])


def test_unapplicable_image_free_cells_do_not_invent_measurements():
    row = next(r for r in overview.ROWS if r.family == "indexed")
    table = overview.matrix_markdown(overview.DOCUMENTS[:1], [row], [])
    assert table.endswith("| — |\n")


def test_minima_do_not_compare_native_preservation_with_bw_conversion():
    rows = [r for r in overview.ROWS if (r.family == "preserve-images" and r.native != "flate") or
            (r.family == "bw-images" and r.variant == "jbig2")]
    document = overview.DOCUMENTS[-1]
    records = [dict(document=document.key, family=row.family,
                    result=dict(image_variant=row.variant, native_policy=row.native, complete_pdf_bytes=value))
               for row, value in zip(rows, (1000, 900, 50, 55))]
    table = overview.matrix_markdown([document], rows, records)
    assert "| **900** |" in table and "| **50** |" in table
    assert "| 1,000 |" in table and "| 55 |" in table


def test_fixture_structure_matches_its_compression_class():
    import pymupdf as fitz
    statistics = {}
    for document in overview.DOCUMENTS:
        with fitz.open(document.source) as pdf:
            statistics[document.key] = dict(
                images=[len(page.get_image_info()) for page in pdf],
                words=sum(len(page.get_text("words")) for page in pdf))
    assert not any(statistics["native"]["images"]) and statistics["native"]["words"] > 1000
    assert all(statistics["photos"]["images"])
    assert all(statistics["scan"]["images"]) and statistics["scan"]["words"] == 0
    assert sum(statistics["mixed"]["images"]) and statistics["mixed"]["words"] > 1000
    assert sum(statistics["art"]["images"]) and statistics["art"]["words"] < 20


def test_valid_prior_complete_results_are_reused_without_preparation_or_encoding(tmp_path, monkeypatch):
    document, rows = overview.DOCUMENTS[0], overview.ROWS[:3]
    source, base, output = (tmp_path / name for name in ("source", "base", "output"))
    for path in (source, base, output):
        path.write_bytes(path.name.encode())
    document = overview.Document(document.key, document.label, str(source))
    case = dict(id=overview.case_id(source, "preserve-images"), source=str(source),
                input_sha256=overview.file_digest(source), bases={"preserve-images":
                dict(pdf=str(base), sha256=overview.file_digest(base))})
    results = [dict(image_variant="preserve-images", native_policy=row.native,
                    pdf=str(output), pdf_sha256=overview.file_digest(output),
                    complete_pdf_bytes=output.stat().st_size, exact_native=True,
                    exact_images=True, exact_all_page_pixels=True) for row in rows]
    report = dict(identity=dict(case=case, environment=dict(implementation={})), results=results)
    monkeypatch.setattr(overview, "DOCUMENTS", [document])
    monkeypatch.setattr(overview, "ROWS", rows)
    monkeypatch.setattr(overview, "load_history", lambda path: {case["id"]: report})
    def forbidden(*args, **kwargs):
        pytest.fail("A verified prior complete output must not be re-encoded")
    monkeypatch.setattr(overview, "prepare_case", forbidden)
    monkeypatch.setattr(overview.study, "run_case", forbidden)
    folder = tmp_path / "overview"
    records = overview.run(folder, tmp_path / "history.json")
    assert len(records) == 3 and all(r["origin"].endswith("history.json") for r in records)
    assert (folder / "matrix.md").is_file() and (folder / "metrics.json").is_file()
    assert not list(folder.glob("*.csv"))


def test_failed_validation_is_visible_and_cannot_become_a_size_minimum():
    document, rows = overview.DOCUMENTS[-1], overview.ROWS[1:3]
    records = [dict(document=document.key, family=rows[0].family,
                    result=dict(image_variant=rows[0].variant, native_policy=rows[0].native,
                                complete_pdf_bytes=900)),
               dict(document=document.key, family=rows[1].family,
                    result=dict(image_variant=rows[1].variant, native_policy=rows[1].native,
                                validation_error="actual page pixels changed"))]
    table = overview.matrix_markdown([document], rows, records)
    assert "| **900** |" in table and "| FAILED |" in table
    assert "| 0 |" not in table
    with pytest.raises(ValueError, match="rejected output"):
        overview.validate_record({}, records[1]["result"])


def test_changed_imported_overview_source_is_rejected(tmp_path):
    import json
    prior = tmp_path / "previous"
    prior.mkdir()
    (prior / "implementation.py").write_text("original")
    manifest = prior / "metrics.json"
    manifest.write_text(json.dumps(dict(implementation=overview.file_digest(prior / "implementation.py"), records=[])))
    (prior / "implementation.py").write_text("changed")
    history = tmp_path / "history.json"
    history.write_text("[]")
    with pytest.raises(ValueError, match="Changed imported overview"):
        overview.run(tmp_path / "new", history, reuse_overview=manifest)


def test_bad_preparation_does_not_hide_other_variants_or_relax_exact_pixels(tmp_path, monkeypatch):
    import json
    document = overview.Document("scan", "scan", str(tmp_path / "source.pdf"))
    Path(document.source).write_bytes(b"source")
    prep = tmp_path / "prepared-bitmaps" / overview.case_id(document.source, "indexed")
    prep.mkdir(parents=True)
    raw = dict(source=document.source, input_sha256=overview.file_digest(document.source), mode="indexed",
               dpi=150, colors=5, threshold_method=None, threshold=None, prepared=[], results=[])
    def saved_result(variant, path):
        return dict(variant=variant, pdf=str(path), pdf_sha256=overview.file_digest(path), complete_pdf_bytes=path.stat().st_size)
    base = prep / "flate-plain.pdf"
    base.write_bytes(b"verified reference")
    raw["results"] = [saved_result("flate-plain", base)]
    (prep / "metrics.json").write_text(json.dumps(raw))
    def interrupted(*a, **k):
        raise AssertionError("whole-page pixels differ")
    def verify(source, target, bitmaps, family, variant, dpi, expected=None):
        if variant == "jbig2":
            raise AssertionError("rightmost page column clipped")
        return saved_result(variant, target), ["strict reference pixels"]
    def save(source, target, *a):
        target.write_bytes(b"candidate")
    monkeypatch.setattr(overview.study.images, "run_case", interrupted)
    monkeypatch.setattr(overview.study.images, "prepare", lambda *a: [])
    monkeypatch.setattr(overview.study.images, "verify_variant", verify)
    monkeypatch.setattr(overview.study.images, "save_variant", save)
    case = overview.prepare_case(document, "indexed", tmp_path, {})
    assert set(case["bases"]) == set(overview.study.VARIANTS) - {"jbig2"}
    assert "rightmost page column clipped" in case["failures"]["jbig2"]["validation_error"]
    assert "complete_pdf_bytes" not in case["failures"]["jbig2"]


@pytest.mark.parametrize("family", ["indexed", "bw-images"])
def test_rejected_shared_preparation_is_not_reported_as_independent_codec_failures(tmp_path, monkeypatch, family):
    source = tmp_path / "source.pdf"
    source.write_bytes(b"source")
    document = overview.Document("photos", "photos", str(source))
    def failed(*a, **k):
        a[1].mkdir(parents=True, exist_ok=True)
        raise RuntimeError("ActualText with no position")
    monkeypatch.setattr(overview.study.images, "run_case", failed)
    case = overview.prepare_case(document, family, tmp_path, {})
    assert not case["bases"]
    assert set(case["failures"]) == set(overview.study.VARIANTS)
    assert all(r["validation_stage"] == "shared-preparation" for r in case["failures"].values())
    row = next(r for r in overview.ROWS if r.family == family)
    result = dict(image_variant=row.variant, native_policy=row.native, **case["failures"][row.variant])
    table = overview.matrix_markdown([document], [row], [dict(document=document.key, family=family, result=result)])
    assert "PREP FAILED" in table and "complete_pdf_bytes" not in result


def test_frozen_native_preparation_with_new_diagnostics_is_rejected(tmp_path, monkeypatch):
    source, base = tmp_path / "source", tmp_path / "base"
    source.write_bytes(b"source")
    base.write_bytes(b"base")
    case = dict(source=str(source), bases={"jpeg-q50": dict(pdf=str(base))})
    calls = []
    def diagnostics(path):
        calls.append(path)
        return [{"source warning"} if path == str(source) else {"source warning", "ActualText with no position"}]
    monkeypatch.setattr(overview, "native_diagnostics", diagnostics)
    cache = {}
    rejected = overview.preparation_error(case, cache)
    assert rejected["validation_stage"] == "shared-preparation"
    assert "ActualText with no position" in rejected["validation_error"]
    assert "complete_pdf_bytes" not in rejected
    assert overview.preparation_error(case, cache) == rejected
    assert len(calls) == 2


@pytest.mark.parametrize("target", ["source", "base", "output", "implementation", "verification"])
def test_reused_measurements_require_hashes_sizes_and_exact_checks(tmp_path, target):
    source, base, output, implementation = (tmp_path / name for name in ("source", "base", "output", "script"))
    for path in (source, base, output, implementation):
        path.write_bytes(path.name.encode())
    case = dict(source=str(source), input_sha256=overview.file_digest(source),
                bases={"x": dict(pdf=str(base), sha256=overview.file_digest(base))})
    result = dict(pdf=str(output), pdf_sha256=overview.file_digest(output), complete_pdf_bytes=output.stat().st_size,
                  exact_native=True, exact_images=True, exact_all_page_pixels=True)
    code = {str(implementation): overview.file_digest(implementation)}
    overview.validate_record(case, result, code)
    if target == "verification":
        result["exact_images"] = False
    else:
        dict(source=source, base=base, output=output, implementation=implementation)[target].write_bytes(b"changed")
    with pytest.raises(ValueError, match="Changed|Missing"):
        overview.validate_record(case, result, code)
