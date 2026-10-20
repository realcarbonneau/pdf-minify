"""Keep current q75 measurements separate from immutable historical controls."""

from dataclasses import asdict
import io
import json
from pathlib import Path

from PIL import Image
import pytest
import pymupdf as fitz

from tools import publish_lossy_quality as publication


def example_proof():
    return dict(quality=75, dpi=300, documents=[asdict(d) for d in publication.bench.DOCUMENTS],
                jpx_quality_mapping="darktable-rate-v2",
                visual_quality_basis="designer-fixed-q75-working-baseline",
                rows=[dict(label=label, mode=mode, force_raster=force,
                           sizes=[1000 + offset] * 6)
                      for offset, (force, mode, label, _) in enumerate(publication.LABELS)])


def example_table():
    return "| Algorithm | Six columns |\n| **Full color** | |\n" + "".join(
        f"| {old} | old measured cells |\n" for _, _, _, old in publication.LABELS
    ) + "| JPEG2000 lossless | separate unchanged reference |\n"


def test_overlay_updates_only_four_lossy_rows_and_is_idempotent():
    proof = example_proof()
    result = publication.overlay(example_table(), proof)
    assert "JPEG q50" not in result and "r192" not in result
    assert "| JPEG2000 lossless | separate unchanged reference |" in result
    assert "| JPEG q75 | **1,000** |" in result
    assert "| JPEG2000 q75 | 1,001 |" in result
    assert publication.overlay(result, proof) == result
    summary=publication.current_summary(proof)
    assert 'smaller in 0, larger in 12, and tied in 0' in summary
    assert 'equal visual quality' in summary


@pytest.mark.parametrize("kind", ["missing", "duplicate", "wrong-quality", "wrong-columns", "non-measured", "old-mapping"])
def test_lossy_overlay_rejects_incomplete_or_wrong_measurements(kind):
    proof, table = example_proof(), example_table()
    if kind == "missing":
        table = table.replace("| JPEG q50 | old measured cells |\n", "")
    elif kind == "duplicate":
        table += "| JPEG q50 | duplicate |\n"
    elif kind == "wrong-quality":
        proof["quality"] = 90
    elif kind == "wrong-columns":
        proof["rows"][0]["sizes"] = [1000]
    elif kind == "old-mapping":
        proof["jpx_quality_mapping"] = "darktable-rate-v1"
    else:
        proof["rows"][0]["sizes"][0] = 999.5
    with pytest.raises(ValueError):
        publication.overlay(table, proof)


def test_incomplete_or_changed_producer_cannot_publish(tmp_path):
    manifest = tmp_path / "metrics.json"
    manifest.write_text(json.dumps(dict(complete=False)))
    with pytest.raises(ValueError, match="Incomplete"):
        publication.audit(manifest)


def test_source_bound_nonpainted_native_images_are_preserved_but_unknown_pixels_fail(tmp_path):
    source, output = tmp_path / "native-resource.pdf", tmp_path / "saved.pdf"
    with fitz.open() as doc:
        doc.new_page(width=36, height=48).insert_text((2, 12), "Native", fontsize=5)
        xref = doc.get_new_xref()
        doc.update_object(xref, "<< /Type /XObject /Subtype /Image /Width 2 /Height 2 "
                                "/BitsPerComponent 8 /ColorSpace /DeviceGray >>")
        doc.update_stream(xref, bytes((0, 64, 128, 255)), compress=False)
        # A non-page resource: the selected artwork codec does not authorize
        # removing or rewriting it. Real corpus examples are native soft masks.
        doc.xref_set_key(doc.pdf_catalog(), "NativeResourceProbe", f"{xref} 0 R")
        doc.save(source)
    publication.bench.pipeline.save_with_spec(str(source), str(output), dict(mode="jpx", dpi_cap=300))
    row = dict(pdf=str(output), mode="jpx", force_raster=False, canvases=[])
    protected = publication.native_resource_images(row, source)
    assert len(protected) == 1
    bad = tmp_path / "bad.pdf"
    with fitz.open(output) as doc:
        xref = int(doc.xref_get_key(doc.pdf_catalog(), "NativeResourceProbe")[1].split()[0])
        doc.update_stream(xref, b"bad!", compress=False)
        doc.save(bad)
    with pytest.raises(ValueError, match="Unverified non-artwork"):
        publication.native_resource_images(dict(row, pdf=str(bad)), source)


def test_actual_published_q75_rows_are_pinned_separately_from_historical_controls():
    proof = json.loads(publication.FIXTURE.read_text())
    assert proof["designer_rulings"] == [265, 266, 271]
    assert proof["quality"] == 75 and proof["dpi"] == 300
    assert proof["visual_quality_basis"] == "designer-fixed-q75-working-baseline"
    assert proof["jpx_quality_mapping"] == "darktable-rate-v2"
    assert proof["jpeg_profile"] == "jpeg444-huffman-v1"
    assert proof["jpx_profile"] == "jpx97-ict-v1"
    assert len(proof["measured_manifest_sha256"]) == 64
    assert len(proof["source_sha256"]) == 6
    expected = {line for label, line in publication.row_lines(proof).items() if "q75" in label}
    report = Path("docs/INTEGRATED_COMPRESSION.md").read_text()
    primary = report.split("## Overview — final complete-file bytes", 1)[1].split("## PNG prediction", 1)[0]
    assert expected <= set(primary.splitlines())
    assert "working comparable-quality baseline" in report
    for row in proof["rows"]:
        for field in ("pdf_sha256", "canvas_proof_sha256", "readback_proof_sha256"):
            assert len(row[field]) == 6 and all(len(value) == 64 for value in row[field])
    assert proof["rows"][0]["native_resource_image_count"] == [0, 0, 67, 0, 0, 0]
    assert proof["rows"][0]["native_resource_proof_sha256"] == proof["rows"][1]["native_resource_proof_sha256"]
    controls = report.split("### Fixed-encoder controls — measured final PDF bytes", 1)[1]
    assert "JPEG q75" in controls and "JPEG2000 q75" in controls
    assert not any("q50" in line or "r192" in line for line in report.splitlines() if line.startswith("|"))
    frozen = json.loads(Path("tests/fixtures/best_overview_sizes.json").read_text())
    assert any(row["label"] == "JPEG q50" for row in frozen["rows"])


def test_reference_byte_count_is_checked_against_actual_saved_jpeg(tmp_path):
    source, output = tmp_path / "input.pdf", tmp_path / "jpeg.pdf"
    png = io.BytesIO()
    Image.new("RGB", (16, 16), (32, 128, 240)).save(png, "PNG")
    with fitz.open() as doc:
        page = doc.new_page(width=36, height=48)
        page.insert_image(fitz.Rect(0, 0, 36, 48), stream=png.getvalue())
        doc.save(source)
    publication.bench.pipeline.save_with_spec(str(source), str(output), dict(mode="color", dpi_cap=72))
    with fitz.open(output) as doc:
        payload = doc.xref_stream_raw(doc[0].get_images(full=True)[0][0])
    row = dict(pdf=str(output), mode="color", force_raster=False,
               canvases=[dict(payload_sha256=publication.bench.digest(payload),
                              quality_reference=dict(jpeg_bytes=len(payload)+1))])
    with pytest.raises(ValueError, match="actual saved payload"):
        publication.native_resource_images(row, source)
