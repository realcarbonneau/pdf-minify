"""q75 is quality, not a renamed JPX ratio; preserve real codec semantics."""

import io

import numpy as np
from PIL import Image, JpegImagePlugin
import pymupdf as fitz
import pytest

from pdf_minify.core import pipeline, presets
from pdf_minify.core.algorithms import with_algorithm
from pdf_minify.core.quality import DEFAULT_LOSSY_QUALITY, checked_quality, jpx_quality_psnr
from pdf_minify.core.recipes import preset_spec, spec_key


def artwork():
    rng = np.random.default_rng(263)
    y, x = np.indices((192, 256))
    base = np.stack((x, y, (x+y) // 2), axis=-1)
    return np.uint8(np.clip(base + rng.integers(-24, 25, base.shape), 0, 255))


def pillow_jpx(arr, db):
    """The calibrated profile, written out independently of the app helper."""
    img, buf = Image.fromarray(arr), io.BytesIO()
    img.save(buf, "JPEG2000", quality_mode="dB", quality_layers=[db], irreversible=True, mct=1,
             num_resolutions=min(6, min(img.size).bit_length()), codeblock_size=(64, 64),
             progression="LRCP", tile_size=(512, 512))
    return buf.getvalue()


@pytest.mark.parametrize("q,db", [(0,34.5),(50,39.5),(60,40.5),(70,42.83),(75,44.0),(90,50.5),(100,54.83)])
def test_jpx_quality_uses_the_calibrated_anchors_for_every_input(q, db):
    assert jpx_quality_psnr(q) == db


@pytest.mark.parametrize("q", [-1,101,True,False,10.5,'10',None,float('nan')])
def test_jpx_mapping_rejects_invalid_quality(q):
    with pytest.raises(ValueError, match="integer from 0 to 100"):
        jpx_quality_psnr(q)


def test_mapping_is_monotonic_and_does_not_accept_image_statistics():
    targets = [jpx_quality_psnr(q) for q in range(101)]
    assert all(a < b for a, b in zip(targets, targets[1:]))
    with pytest.raises(TypeError):
        jpx_quality_psnr(75, 10000)


@pytest.mark.parametrize("quality", [-1, 101, 90.5, "90", None, True])
def test_invalid_quality_is_not_silently_clamped_or_ignored(quality):
    with pytest.raises(ValueError, match="integer from 0 to 100"):
        checked_quality(quality)


@pytest.mark.parametrize("mode,field", [("color", "jpeg_q"), ("jpx", "jpx_q")])
def test_preset_quality_is_not_truncated_and_invalid_headless_input_fails_before_io(mode, field):
    with pytest.raises(ValueError, match="integer from 0 to 100"):
        preset_spec(dict(mode=mode, params={field: 90.5}))
    with pytest.raises(ValueError, match="integer from 0 to 100"):
        pipeline.save_with_spec("unopened-input.pdf", "unused-output.pdf", {"mode": mode, field: 90.5})


def test_q75_defaults_and_codec_switches():
    assert DEFAULT_LOSSY_QUALITY == 75
    for mode, field in (("color", "jpeg_q"), ("jpx", "jpx_q")):
        assert preset_spec(dict(mode=mode, params={}))[field] == 75
        assert with_algorithm(dict(mode="bw", dpi=300), mode)[field] == 75
        for preset in presets.PRESETS:
            if preset["mode"] == mode:
                assert preset_spec(preset)[field] == 75
                assert "rate" not in preset["params"]
    original = dict(mode="color", dpi_cap=300, jpeg_q=83)
    wavelet = with_algorithm(original, "jpx")
    wavelet["jpx_q"] = 88
    assert with_algorithm(wavelet, "color")["jpeg_q"] == 83
    assert with_algorithm(with_algorithm(wavelet, "color"), "jpx")["jpx_q"] == 88


def test_quality_and_rate_keys_are_distinct_and_lossless_ignores_both():
    base = dict(mode="jpx", dpi_cap=300)
    quality = dict(base, jpx_q=75)
    assert spec_key(base) == spec_key(quality)
    assert spec_key(quality) != spec_key(dict(base, jpx_q=74))
    assert spec_key(quality) != spec_key(dict(base, rate=75))
    assert spec_key(quality) != spec_key(dict(base, rate=26))
    exact = dict(base, lossless=True)
    assert spec_key(exact) == spec_key(dict(exact, jpx_q=0, rate=192))
    legacy = preset_spec(dict(mode="jpx", params=dict(rate=192)))
    assert legacy["rate"] == 192 and "jpx_q" not in legacy
    with pytest.raises(ValueError, match="not both"):
        preset_spec(dict(mode="jpx", params=dict(jpx_q=90, rate=192)))


def test_real_jpx_quality_has_the_same_fixed_target_on_every_input():
    arr = artwork()
    normal = pipeline.jpx_encode(arr, None, presized=True)
    q75 = pipeline.jpx_encode(arr, None, presized=True, jpx_q=75)
    low = pipeline.jpx_encode(arr, None, presized=True, jpx_q=30)
    assert normal == q75 == pillow_jpx(arr, 44.0)
    assert q75 != pipeline.jpx_encode(arr, None, rate=26, presized=True)  # legacy ratio stays distinct
    q90 = pipeline.jpx_encode(arr, None, presized=True, jpx_q=90)
    assert q90 == pillow_jpx(arr, 50.5)
    decoded = np.asarray(Image.open(io.BytesIO(q75)).convert("RGB"))
    coarse = np.asarray(Image.open(io.BytesIO(low)).convert("RGB"))
    mse = lambda value: np.mean((value.astype(float)-arr.astype(float))**2)
    assert decoded.shape == arr.shape and mse(decoded) < mse(coarse)


def test_jpx_never_encodes_a_reference_jpeg_or_uses_its_bytes(monkeypatch):
    arr = artwork()
    monkeypatch.setattr(pipeline, "jpeg_encode", lambda *a,**k: pytest.fail('JPX encoded a reference JPEG'))
    for source in (arr, np.full_like(arr,255), np.zeros_like(arr)):
        assert pipeline.jpx_encode(source,None,presized=True,jpx_q=75) == pillow_jpx(source, 44.0)
    pipeline.jpx_encode(arr, None, lossless=True, presized=True)


def test_fixed_quality_retains_the_only_resize(monkeypatch):
    arr = artwork()
    monkeypatch.setattr(pipeline,'jpeg_encode',lambda *a,**k: pytest.fail('Reference encode'))
    payload = pipeline.jpx_encode(arr, 12, jpx_q=75)
    assert Image.open(io.BytesIO(payload)).size == (132, 99)


def test_jpx_lossless_retains_exact_samples_and_ignores_inactive_quality():
    arr = artwork()
    payload = pipeline.jpx_encode(arr, None, lossless=True, presized=True, jpx_q=-1, rate=192)
    assert np.array_equal(np.asarray(Image.open(io.BytesIO(payload))), arr)


def test_jpeg_q75_uses_deliberate_full_resolution_chroma_sampling():
    img = Image.fromarray(artwork())
    payload = pipeline.color_canvas_payload(img, allow_substitution=False)
    assert payload["filter"] == "/DCTDecode"
    actual = Image.open(io.BytesIO(payload["stream"]))
    expected = io.BytesIO()
    img.save(expected, "JPEG", quality=75, optimize=True, subsampling=0)
    assert payload["stream"] == expected.getvalue()
    assert JpegImagePlugin.get_sampling(actual) == 0  # 4:4:4, not library-default 4:2:0


@pytest.mark.parametrize("lossless", [False, True])
def test_jpx_uses_the_deliberate_lossy_profile_but_preserves_lossless(lossless):
    payload = pipeline.jpx_encode(artwork(), None, presized=True, lossless=lossless)
    siz = payload.index(b"\xff\x51")
    assert int.from_bytes(payload[siz+38:siz+40], "big") == 3
    for component in range(3):
        offset = siz + 40 + component * 3
        assert payload[offset:offset+3] == bytes((7, 1, 1))  # 8-bit, full-resolution
    cod = payload.index(b"\xff\x52")
    assert payload[cod+5] == 0  # LRCP progression
    assert int.from_bytes(payload[cod+6:cod+8], "big") == 1  # one quality layer
    assert payload[cod+8] == (0 if lossless else 1)
    assert payload[cod+13] == (1 if lossless else 0)  # 5/3 lossless, 9/7 lossy


@pytest.mark.parametrize("shape", [(1, 1), (7, 19), (16, 16), (31, 32)])
@pytest.mark.parametrize("lossless", [False, True])
@pytest.mark.parametrize("quality", [0, 75, 100])
def test_jpx_tiny_inputs_have_valid_wavelet_depth_and_decode(shape, lossless, quality):
    arr = np.random.default_rng(265).integers(0, 256, (*shape, 3), dtype=np.uint8)
    payload = pipeline.jpx_encode(arr, None, presized=True, lossless=lossless, jpx_q=quality)
    actual = np.asarray(Image.open(io.BytesIO(payload)))
    assert actual.shape == arr.shape
    if lossless:
        assert np.array_equal(arr, actual)


@pytest.mark.parametrize("mode,constant", [("color", "JPEG_ENCODING_PROFILE"), ("jpx", "JPX_ENCODING_PROFILE")])
def test_encoder_profile_is_part_of_effective_identity(monkeypatch, mode, constant):
    from pdf_minify.core import recipes
    recipe = dict(mode=mode, dpi_cap=300)
    before = recipes.spec_key(recipe)
    monkeypatch.setattr(recipes, constant, "different-test-profile")
    assert recipes.spec_key(recipe) != before


def test_jpx_quality_identity_drops_reference_profile_and_versions_the_fixed_mapping(monkeypatch):
    from pdf_minify.core import recipes
    selected = dict(mode="jpx", jpx_q=75)
    legacy, exact = dict(mode="jpx", rate=26), dict(mode="jpx", lossless=True)
    keys = [spec_key(s) for s in (selected, legacy, exact)]
    monkeypatch.setattr(recipes, "JPEG_ENCODING_PROFILE", "other-reference")
    assert spec_key(selected) == keys[0]
    assert spec_key(legacy) == keys[1] and spec_key(exact) == keys[2]
    reference_key = spec_key(selected)
    monkeypatch.setattr(recipes, "JPX_QUALITY_MAPPING", "other-mapping")
    assert spec_key(selected) != reference_key


def test_current_preset_benchmark_forwards_the_actual_quality_recipe(monkeypatch):
    from tools import bench_filters as bench
    calls = []
    monkeypatch.setattr(bench, "save_with_spec", lambda *a, **kw: calls.append((a, kw)))
    for pid in ("color-max", "color-j2k"):
        bench.run_one("input.pdf", pid, "output.pdf")
        assert calls[-1][0] == ("input.pdf", "output.pdf", preset_spec(presets.get(pid)))
        assert "rate" not in calls[-1][0][2]


def test_benchmark_provenance_covers_the_quality_mapping():
    from tools import bench_integrated_compression as bench
    assert "pdf_minify/core/quality.py" in bench.environment()["implementation"]


@pytest.mark.parametrize("mode,field", [("color", "jpeg_q"), ("jpx", "jpx_q")])
@pytest.mark.parametrize("force", [False, True])
@pytest.mark.parametrize("quality", [75, 90])
def test_quality_reaches_real_native_and_ffpr_saves(tmp_path, monkeypatch, mode, field, force, quality):
    source, output = tmp_path / "source.pdf", tmp_path / "output.pdf"
    with fitz.open() as doc:
        page = doc.new_page(width=256, height=240)
        png = io.BytesIO()
        Image.fromarray(artwork()).save(png, "PNG")
        page.insert_image(fitz.Rect(0, 0, 256, 192), stream=png.getvalue())
        page.insert_text((8, 220), "Native quality test")
        doc.save(source)
    calls = []
    encode = pipeline.color_canvas_payload

    def observed(img, *args, **kwargs):
        result = encode(img, *args, **kwargs)
        calls.append((img.copy(), result))
        return result

    monkeypatch.setattr(pipeline, "color_canvas_payload", observed)
    pipeline.save_with_spec(str(source), str(output),
                            dict(mode=mode, dpi_cap=72, force_raster=force, **{field: quality}))
    assert len(calls) == 1
    canvas, payload = calls[0]
    if mode == "color":
        encoded = io.BytesIO()
        canvas.save(encoded, "JPEG", quality=quality, optimize=True, subsampling=0)
        expected = encoded.getvalue()
    else:
        expected = pillow_jpx(np.asarray(canvas), jpx_quality_psnr(quality))
    assert payload["stream"] == expected
    with fitz.open(output) as doc:
        page = doc[0]
        assert bool(page.get_text().strip()) != force
        images = page.get_images(full=True)
        assert len(images) == 1
        assert images[0][2:4] == (256, 240)
        assert doc.xref_stream_raw(images[0][0]) == expected
        assert page.get_pixmap().width == 256  # the actual complete file decodes
