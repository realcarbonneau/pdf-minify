"""§183: independent nearest-color checks, not just palette-count checks."""
import zlib

import numpy as np
from PIL import Image
import pymupdf as fitz
import pytest

from pdf_minimalist.core import pipeline


def artwork():
    rgb = np.full((160, 160, 3), 255, dtype=np.uint8)
    y, x = np.indices((120, 120))
    rgb[20:140, 20:140] = np.stack((x*255//119, y*255//119, 255-x*255//119), 2)
    return rgb


def nonnearest(source, actual, palette):
    src = source.reshape(-1, 3).astype(np.int32)
    out = actual.reshape(-1, 3).astype(np.int32)
    pal = palette.astype(np.int32)
    wrong = 0
    for start in range(0, len(src), 4096):
        block = src[start:start+4096]
        closest = ((block[:, None] - pal[None])**2).sum(2).min(1)
        assigned = ((block - out[start:start+len(block)])**2).sum(1)
        wrong += int((assigned > closest).sum())
    return wrong


def decode_parts(parts):
    bpc, width, height = parts["bpc"], parts["w"], parts["h"]
    raw = np.frombuffer(zlib.decompress(parts["stream"]), dtype=np.uint8).reshape(height, -1)
    bits = np.unpackbits(raw, axis=1)[:, :width*bpc].reshape(height, width, bpc)
    indices = (bits * (1 << np.arange(bpc-1, -1, -1))).sum(2)
    palette = np.frombuffer(parts["palette"], dtype=np.uint8).reshape(-1, 3)
    assert indices.max() <= parts["hival"]
    return palette[indices], palette


@pytest.mark.parametrize("colors", [2, 3, 4, 8, 16, 64, 256])
def test_every_index_maps_to_a_nearest_color_not_a_white_fallback(colors):
    rgb = artwork()
    parts = pipeline.indexed_parts(Image.fromarray(rgb), colors)
    actual, palette = decode_parts(parts)
    assert len(palette) <= colors
    assert nonnearest(rgb, actual, palette) == 0
    assert np.array_equal(actual, pipeline.indexed_rgb(rgb, colors))
    assert np.all(actual[0, 0] == 255), "real white page background must stay white"
    if colors >= 3:
        assert np.count_nonzero(palette.max(1)-palette.min(1) > 80) >= 2, (
            "white-heavy artwork must not waste its low-color slots on near-white duplicates")


def test_fixture_reproduces_the_discarded_octree_white_bucket_defect():
    rgb = artwork()
    old = Image.fromarray(rgb).quantize(colors=3, method=Image.Quantize.FASTOCTREE,
                                       dither=Image.Dither.NONE)
    palette = np.asarray(old.getpalette(), dtype=np.uint8).reshape(-1, 3)[:3]
    actual = np.asarray(old.convert("RGB"))
    assert nonnearest(rgb, actual, palette) > 0
    white = np.all(actual > 240, axis=2)
    assert nonnearest(rgb[white], actual[white], palette) > 0


@pytest.mark.parametrize("colors", [16, 256])
def test_genuinely_few_nearby_colors_remain_exact(colors):
    rgb = np.array([[(100+i, 100, 100) for i in range(16)]], dtype=np.uint8)
    parts = pipeline.indexed_parts(Image.fromarray(rgb), colors)
    actual, _ = decode_parts(parts)
    assert np.array_equal(actual, rgb)
    candidate = pipeline.indexed_flate_candidate(Image.fromarray(rgb))
    assert np.array_equal(decode_parts(candidate)[0], rgb)


def test_actual_images_pdf_low_palette_is_nearest_before_and_after_pdf_embedding(tmp_path, monkeypatch):
    reference = []
    encode = pipeline.color_canvas_payload
    def observe(image, *args, **kwargs):
        reference.append(np.asarray(image).copy())
        return encode(image, *args, **kwargs)
    monkeypatch.setattr(pipeline, "color_canvas_payload", observe)
    target = tmp_path / "four-colors.pdf"
    pipeline.save_with_spec("examples/images.pdf", str(target),
                            dict(mode="indexed", dpi_cap=150, colors=4))
    assert len(reference) == 1
    with fitz.open(target) as doc:
        entry = doc[0].get_images(full=True)[0]
        assert not entry[1] and entry[2:4] == (1275, 1650)
        pix = fitz.Pixmap(doc, entry[0])
        actual = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
        palette = np.unique(actual.reshape(-1, 3), axis=0)
        assert len(palette) <= 4 and nonnearest(reference[0], actual, palette) == 0
        assert np.array_equal(actual, pipeline.indexed_rgb(reference[0], 4))
