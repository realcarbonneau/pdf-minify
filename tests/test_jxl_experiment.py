"""JPEG XL binary experiment (TODO §270): clean swaps and tagged-cell publication."""

import json
import shutil

import numpy as np
from PIL import Image
import pymupdf as fitz
import pytest

from pdf_minify.core import pipeline
from tools import bench_jxl as bench
from tools import benchmark_tables as tables
from tools import publish_jxl as publication


def two_image_pdf(path):
    with fitz.open() as doc:
        page = doc.new_page(width=72, height=72)
        page.insert_text((4, 20), "Native", fontsize=8)
        for n, rect in enumerate((fitz.Rect(0, 30, 30, 60), fitz.Rect(36, 30, 66, 60))):
            xref = doc.get_new_xref()
            doc.update_object(xref, "<< /Type /XObject /Subtype /Image /Width 2 /Height 2 "
                                    "/ColorSpace /DeviceGray /BitsPerComponent 8 >>")
            doc.update_stream(xref, bytes((0, 64, 128, 255 - n)), compress=False)
            page.insert_image(rect, xref=xref, keep_proportion=False)
        pipeline._write_optimized_pdf(doc, str(path), no_new_id=True)


def test_swap_changes_only_the_image_object(tmp_path):
    baseline, treatment = tmp_path / "base.pdf", tmp_path / "jxl.pdf"
    two_image_pdf(baseline)
    with fitz.open(baseline) as doc:
        first = sorted({i[0] for i in doc[0].get_images(full=True)})[0]
        bench.replace_image(doc, first, b"payload", rgb=True)
        pipeline._write_optimized_pdf(doc, str(treatment), no_new_id=True)
    bench.check_only_images_changed(baseline, treatment, {first: bench.digest(b"payload")})
    with fitz.open(treatment) as doc:
        assert doc.xref_get_key(first, "Filter")[1] == bench.FILTER
        assert doc.xref_get_key(first, "ColorSpace")[1] == "/DeviceRGB"
        assert doc.xref_get_key(first, "DecodeParms")[0] == "null"


def test_swap_check_rejects_any_other_change(tmp_path):
    baseline, treatment = tmp_path / "base.pdf", tmp_path / "jxl.pdf"
    two_image_pdf(baseline)
    with fitz.open(baseline) as doc:
        first, second = sorted({i[0] for i in doc[0].get_images(full=True)})
        bench.replace_image(doc, first, b"payload", rgb=False)
        doc.update_stream(second, bytes((1, 2, 3, 4)), compress=False)
        pipeline._write_optimized_pdf(doc, str(treatment), no_new_id=True)
    with pytest.raises(ValueError, match="changed outside the images"):
        bench.check_only_images_changed(baseline, treatment, {first: bench.digest(b"payload")})


@pytest.mark.skipif(not (shutil.which("cjxl") and shutil.which("djxl")), reason="needs libjxl tools")
def test_lossless_jpeg_xl_round_trips_bilevel_and_palette_pixels(tmp_path):
    rng = np.random.default_rng(7)
    bilevel = (rng.random((37, 53)) > 0.5).astype(np.uint8) * 255
    palette = np.array([[255, 255, 255], [200, 30, 40], [10, 90, 200]], np.uint8)[rng.integers(0, 3, (31, 29))]
    for name, samples in (("bw", bilevel), ("rgb", palette)):
        png = tmp_path / f"{name}.png"
        image = Image.fromarray(samples)
        (image.convert("1") if name == "bw" else image).save(png)
        bench.encode_jxl(png, tmp_path / f"{name}.jxl", distance=0, effort=7)
        assert np.array_equal(bench.decode_jxl(tmp_path / f"{name}.jxl", tmp_path / f"{name}-d.png"), samples)


def example_proof():
    rows = []
    for n, (row_id, *_rest, treatment) in enumerate(bench.ROWS):
        row = dict(row=row_id, treatment=treatment, baseline_bytes=[1000] * 6,
                   jxl_bytes=[900 + n, 1000, 1001, 999, 1000, 2000], jxl_pdf_sha256=["0" * 64] * 6,
                   images=[1] * 6)
        if treatment == "lossy":
            row["quality_gap"] = [None, 1.25, -3.0, 0.04, 2.0, -0.5]
        rows.append(row)
    return dict(documents=list(bench.DOCUMENTS), rows=rows)


def test_percentages_bold_only_displayed_reductions():
    assert publication.percent(1000, 900) == "**-10.00%**"
    assert publication.percent(1000, 1000) == "+0.00%"
    assert publication.percent(1_000_000, 999_999) == "+0.00%"
    assert publication.percent(1000, 1001) == "+0.10%"


def test_quality_gaps_never_show_negative_zero():
    assert publication.gap(-0.014) == "+0.0"
    assert publication.gap(-0.06) == "-0.1"
    assert publication.gap(0.04) == "+0.0"


def test_publication_fills_only_tagged_cells_and_is_idempotent():
    before = tables.PAGE.read_text()
    after = publication.fill(before, example_proof())
    effect = tables.read_table(after, "jxl-effect")
    assert effect.rows["bw-jbig2"] == ["**-10.00%**", "+0.00%", "+0.10%", "**-0.10%**", "+0.00%", "+100.00%"]
    assert effect.rows["group.bw"] == [""] * 6
    assert tables.read_table(after, "jxl-bytes").rows["jpeg"][0] == "908"
    assert tables.read_table(after, "jxl-quality-gap").rows["jpeg"] == ["no images", "+1.2", "-3.0", "+0.0", "+2.0", "-0.5"]
    assert effect.labels == tables.read_table(before, "jxl-effect").labels
    outside = [line for line in after.splitlines() if "<!-- row:" not in line]
    assert outside == [line for line in before.splitlines() if "<!-- row:" not in line]
    assert publication.fill(after, example_proof()) == after


def test_publication_rejects_wrong_scope_or_non_measured_sizes():
    proof = example_proof()
    proof["rows"] = proof["rows"][:-1]
    with pytest.raises(ValueError, match="scope"):
        publication.values(proof)
    proof = example_proof()
    proof["rows"][0]["jxl_bytes"][0] = 900.5
    with pytest.raises(ValueError, match="measured integer"):
        publication.values(proof)


def test_published_tables_match_the_pinned_measurements():
    if not publication.FIXTURE.exists():
        pytest.skip("JPEG XL experiment not yet published")
    proof = json.loads(publication.FIXTURE.read_text())
    page = tables.PAGE.read_text()
    assert publication.fill(page, proof) == page


def write_match(folder, rows, xrefs=(11, 12)):
    (folder / "images.json").write_text(json.dumps([dict(xref=x) for x in xrefs]))
    lines = [json.dumps(dict(xref=x, distance=d, effort=7, bytes=100, jpeg_bytes=400, ssimulacra2=80 + g,
                             jpeg_ssimulacra2=80, psnr=40, jpeg_psnr=40, jxl_sha256=f"{x}-{d}"))
             for x, d, g in rows]
    (folder / "results.jsonl").write_text("\n".join(lines) + "\n")
    return folder / "results.jsonl"


def test_photo_match_picks_the_measured_distance_closest_to_zero(tmp_path):
    results = write_match(tmp_path, [(11, 2.0, 1.0), (12, 2.0, 0.2), (11, 2.2, -0.1), (12, 2.2, -0.3),
                                     (11, 2.1, 0.0)])  # 2.1 lacks image 12, so it is not a candidate
    chosen = bench.matched_setting(results)
    assert (chosen["distance"], chosen["effort"]) == (2.2, 7)
    assert chosen["mean_gap"] == pytest.approx(-0.2)
    assert chosen["bytes_vs_jpeg"] == 0.25
    assert chosen["jxl_sha256"] == {"11": "11-2.2", "12": "12-2.2"}


def test_photo_match_refuses_a_distance_outside_the_tolerance(tmp_path):
    results = write_match(tmp_path, [(11, 3.0, -2.0), (12, 3.0, -1.0)])
    with pytest.raises(ValueError, match="finer distances"):
        bench.matched_setting(results)
