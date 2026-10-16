"""§§233/235 / B114: full eight-page lossless JBIG2 no-op regression."""

import hashlib
from pathlib import Path

import numpy as np
import pymupdf as fitz
import pytest

from pdf_minify.core import canvas, pipeline
from pdf_minify.core.display import DisplayPage


SOURCE = Path("examples/scan-jfk-poor-copies.pdf")
SOURCE_HASH = "6170e5e125278a540f8f133a9a5f527926e0c213c5aa438f6c7956d80ce3dd36"


def image_samples(doc, page):
    entries = page.get_images(full=True)
    assert len(entries) == 1 and entries[0][4:6] == (1, "DeviceGray")
    assert doc.xref_get_key(entries[0][0], "Filter")[1] == "/JBIG2Decode"
    pix = fitz.Pixmap(doc, entries[0][0])
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width)


def test_jfk_regression_input_is_pinned_jbig2_and_direct_300dpi_is_sample_exact():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_HASH
    with fitz.open(SOURCE) as pdf:
        assert len(pdf) == 8
        for page in pdf:
            assert not page.get_text("words") and not page.get_drawings()
            expected = image_samples(pdf, page)
            rendered = DisplayPage(page).render(fitz.Matrix(300 / 72, 300 / 72))
            rgb = np.frombuffer(rendered.samples, np.uint8).reshape(
                rendered.height, rendered.width, 3)
            for component in range(3):
                np.testing.assert_array_equal(rgb[:, :, component], expected)


def test_nominal_300dpi_jbig2_source_must_not_round_up_to_301dpi():
    with fitz.open(SOURCE) as pdf:
        for page in pdf:
            density = canvas._source_dpi(page)
            grid = (page.rect * fitz.Matrix(density / 72, density / 72)).irect
            expected = image_samples(pdf, page)
            assert (grid.width, grid.height) == (expected.shape[1], expected.shape[0])


@pytest.fixture(scope="module", params=[False, True], ids=["native", "ffpr"])
def saved_noop(request, tmp_path_factory):
    if pipeline.jbig2_binary() is None or pipeline.zopfli_binary() is None:
        pytest.skip("Real JBIG2/Zopfli tools are required for the full-flow contract")
    folder = tmp_path_factory.mktemp(f"jbig2-noop-{request.param}")
    reference, target = folder / "preserve-images.pdf", folder / "filtered.pdf"
    before_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    pipeline.save_with_spec(str(SOURCE), str(reference), dict(
        mode="passthrough", stream_compression="zopfli"), workdir=str(folder))
    pipeline.save_with_spec(str(SOURCE), str(target), dict(
        mode="bw", dpi=300, strategy="otsu", force_raster=request.param,
        stream_compression="zopfli"), workdir=str(folder))
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == before_hash == SOURCE_HASH
    return reference, target


def test_full_flow_jbig2_noop_preserves_every_original_bitmap_sample(saved_noop):
    _, target = saved_noop
    with fitz.open(SOURCE) as original, fitz.open(target) as output:
        assert len(original) == len(output) == 8
        for before, after in zip(original, output):
            assert before.rect == after.rect
            assert before.cropbox == after.cropbox
            assert before.rotation == after.rotation
            np.testing.assert_array_equal(image_samples(output, after),
                                          image_samples(original, before))
            for dpi in (72, 300):
                matrix = fitz.Matrix(dpi / 72, dpi / 72)
                assert (DisplayPage(before).render(matrix).samples ==
                        DisplayPage(after).render(matrix).samples)


def test_full_flow_jbig2_noop_does_not_grow_the_complete_file(saved_noop):
    reference, target = saved_noop
    assert target.stat().st_size <= reference.stat().st_size <= SOURCE.stat().st_size
