"""Exact palette-stencil study; shared production primitives since §203."""
import io
import shutil

import numpy as np
import pymupdf as fitz
from PIL import Image
import pytest

from tools import layered_color_jbig2 as study
from pdf_minimalist.core.cancel import CancelToken
from pdf_minimalist.core.display import DisplayPage
from pdf_minimalist.core.pdf_io import CancelledError

requires_encoder = pytest.mark.skipif(study.pipeline.jbig2_binary() is None,
                                      reason="JBIG2 prototype needs the external encoder")


@requires_encoder
@pytest.mark.parametrize("colors", [
    [(255, 255, 255)],
    [(0, 0, 0), (255, 255, 255)],
    [(255, 255, 255), (255, 76, 35), (135, 63, 214), (254, 195, 58), (241, 32, 91)],
    [(254, 254, 254), (1, 2, 3), (12, 102, 231)],
])
def test_stencil_odd_width_coverage_and_exact_palette_colors(colors):
    palette = np.asarray(colors, dtype=np.uint8)
    y, x = np.indices((13, 19))
    rgb = palette[(x+y*3) % len(palette)]
    canvas = study.PaletteCanvas.from_rgb(Image.fromarray(rgb), max(2, len(colors)))
    with study.stencil_pdf(canvas) as doc:
        actual = study.rgb_pixels(DisplayPage(doc[0]).render())
        assert np.array_equal(actual, rgb)
        images = doc[0].get_images(full=True)
        assert len(images) == sum(color != (255, 255, 255) for color in colors)
        assert len({image[0] for image in images}) == len(images)
        for image in images:
            assert image[2:4] == (19, 13)
            assert doc.xref_get_key(image[0], "ImageMask")[1] == "true"
            assert doc.xref_get_key(image[0], "ColorSpace")[0] == "null"
            assert doc.xref_get_key(image[0], "Filter")[1] == "/JBIG2Decode"


@pytest.mark.parametrize("failure", ["missing", "bad_stream", "failed_stream", "cancel"])
def test_prototype_does_not_silently_label_failed_or_unavailable_encodes_as_jbig2(monkeypatch, failure):
    rgb = np.zeros((13, 19, 3), dtype=np.uint8)
    canvas = study.PaletteCanvas.from_rgb(Image.fromarray(rgb), 2)
    token = CancelToken()
    if failure == "cancel":
        token.cancel()
    elif failure == "missing":
        monkeypatch.setattr(study.pipeline, "jbig2_binary", lambda: None)
    else:
        monkeypatch.setattr(study, "encode_mask",
                            lambda *a: b"invalid" if failure == "bad_stream" else None)
    with pytest.raises(CancelledError if failure == "cancel" else RuntimeError):
        study.stencil_pdf(canvas, token)


def test_all_white_needs_no_encoder_or_stencil(monkeypatch):
    monkeypatch.setattr(study.pipeline, "jbig2_binary", lambda: None)
    canvas = study.PaletteCanvas.from_rgb(Image.new("RGB", (19, 13), "white"), 5)
    with study.stencil_pdf(canvas) as doc:
        assert not doc[0].get_images()
        assert np.all(study.rgb_pixels(DisplayPage(doc[0]).render()) == 255)


@requires_encoder
def test_dense_binary_mask_with_leading_packed_newline_uses_unambiguous_transport(monkeypatch):
    random = np.random.default_rng(192)
    black = random.integers(0, 2, (13, 19), dtype=np.uint8).astype(bool)
    black[0, :8] = [0, 0, 0, 0, 1, 0, 1, 0]
    assert np.packbits(black[0])[0] == 0x0a
    rgb = np.where(black[:, :, None], np.array([255, 76, 35], dtype=np.uint8), 255).astype(np.uint8)
    canvas = study.PaletteCanvas.from_rgb(Image.fromarray(rgb), 2)
    def forbidden(*args):
        pytest.fail("The prototype must not use the ambiguous PBM transport")
    monkeypatch.setattr(study.pipeline, "bw_page_jbig2", forbidden)
    with study.stencil_pdf(canvas) as doc:
        assert np.array_equal(study.rgb_pixels(DisplayPage(doc[0]).render()), rgb)


def _source(path, rotation):
    with fitz.open() as doc:
        for index in range(2):
            page = doc.new_page(width=72, height=96)
            rgb = np.full((17, 31, 3), (255, 76, 35) if index == 0 else (12, 102, 231), dtype=np.uint8)
            rgb[3:12, 7:24] = (255, 255, 255)
            buf = io.BytesIO()
            Image.fromarray(rgb).save(buf, "PNG")
            page.draw_rect(page.rect, color=None, fill=(.15, .6, .25))
            page.insert_image(fitz.Rect(10, 10, 62, 42), stream=buf.getvalue())
            page.insert_text((10, 71), f"Native {index}", fontsize=8)
            page.draw_line((10, 75), (60, 75), color=(0, 0, 1))
            page.insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(10, 60, 60, 72),
                              "uri": "https://example.com/"})
            page.add_text_annot((55, 60), "Retain native note")
            page.set_cropbox(fitz.Rect(3, 4, 69, 90))
            page.set_rotation(rotation)
        page = doc.new_page(width=72, height=96)
        page.insert_text((10, 40), "Native only", fontsize=8)
        doc.save(path)


@requires_encoder
@pytest.mark.skipif(not shutil.which("pdfimages") or not shutil.which("pdftoppm"),
                    reason="Independent prototype verification needs Poppler tools")
@pytest.mark.parametrize("rotation", [0, 90])
def test_actual_multipage_files_share_one_palette_map_and_independent_decoding(tmp_path, monkeypatch, rotation):
    source, indexed, layered = (tmp_path / name for name in ("source.pdf", "indexed.pdf", "layered.pdf"))
    _source(source, rotation)
    quantize, flatten = study.pipeline._quantize_palette, study.flatten_rgb
    calls = []
    def fit(*args):
        calls.append("fit")
        return quantize(*args)
    def sample(*args, **kwargs):
        calls.append("sample")
        return flatten(*args, **kwargs)
    monkeypatch.setattr(study.pipeline, "_quantize_palette", fit)
    monkeypatch.setattr(study, "flatten_rgb", sample)
    canvases = study.prepare_canvases(str(source), 5, 144, CancelToken(), str(tmp_path))
    assert calls == ["sample", "fit", "sample", "fit"]
    assert canvases[-1] is None
    for kind, output in (("indexed", indexed), ("jbig2", layered)):
        study.save_variant(str(source), output, canvases, kind)
    # Encoding either representation must NOT refit or recompose the source.
    assert calls == ["sample", "fit", "sample", "fit"]
    report = study.compare_outputs(str(source), indexed, layered, canvases, 144, tmp_path)
    assert report["mupdf_pixel_exact"] and report["poppler_decoded_masks_exact"]
    assert report["nonwhite_mask_counts"][-1] == 0
    assert source.read_bytes() != indexed.read_bytes() != layered.read_bytes()


def test_existing_production_recipes_remain_unchanged():
    from pdf_minimalist.core.presets import PRESETS
    assert not any(preset["mode"] == "layered-jbig2" for preset in PRESETS)
    with pytest.raises(ValueError, match="Unknown filter mode"):
        study.pipeline._save_recipe("unused", "unused", {"mode": "not-an-algorithm"}, None, None)
