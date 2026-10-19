"""q75 is quality, not a renamed JPX ratio; preserve real codec semantics."""

import io

import numpy as np
from PIL import Image, JpegImagePlugin
import pymupdf as fitz
import pytest

from pdf_minify.core import pipeline, presets
from pdf_minify.core.algorithms import with_algorithm
from pdf_minify.core.quality import DEFAULT_LOSSY_QUALITY, checked_quality, jpx_reference_rate
from pdf_minify.core.recipes import preset_spec, spec_key


def artwork():
    rng = np.random.default_rng(263)
    y, x = np.indices((192, 256))
    base = np.stack((x, y, (x+y) // 2), axis=-1)
    return np.uint8(np.clip(base + rng.integers(-24, 25, base.shape), 0, 255))


@pytest.mark.parametrize("jpeg_ratio,target", [(0.5, 1), (1, 1.125), (20, 22.5),
                                             (40, 45), (50, 59), (60, 73),
                                             (120, 146), (1000, 1216.6666666667)])
def test_jpx_reference_uses_study_anchors_and_bounded_endpoint_gains(jpeg_ratio, target):
    assert jpx_reference_rate(int(jpeg_ratio * 100), 100) == pytest.approx(target)


@pytest.mark.parametrize("raw,jpeg", [(0, 10), (10, 0), (-1, 10), (10, -1),
                                      (True, 10), (10, False), (10.5, 10), (10, "10")])
def test_jpx_reference_rejects_unmeasured_or_invalid_byte_counts(raw, jpeg):
    with pytest.raises(ValueError, match="positive integers"):
        jpx_reference_rate(raw, jpeg)


def test_reference_mapping_is_continuous_monotonic_and_not_capped_at_101():
    ratios = [x / 100 for x in range(3900, 6101)]
    targets = [jpx_reference_rate(round(r * 100), 100) for r in ratios]
    assert all(a < b for a, b in zip(targets, targets[1:]))
    assert jpx_reference_rate(400001, 10000) == pytest.approx(45, abs=.001)
    assert jpx_reference_rate(599999, 10000) == pytest.approx(73, abs=.001)
    assert jpx_reference_rate(20000, 100) > 101


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


def test_real_jpx_quality_anchors_to_same_quality_jpeg_without_decoding_it():
    arr = artwork()
    normal = pipeline.jpx_encode(arr, None, presized=True)
    q75 = pipeline.jpx_encode(arr, None, presized=True, jpx_q=75)
    reference_rate = lambda q: jpx_reference_rate(arr.nbytes, len(pipeline.jpeg_encode(Image.fromarray(arr), q)))
    matched = pipeline.jpx_encode(arr, None, rate=reference_rate(75), presized=True)
    low = pipeline.jpx_encode(arr, None, presized=True, jpx_q=30)
    assert normal == q75 == matched
    assert q75 != pipeline.jpx_encode(arr, None, rate=26, presized=True)
    q90 = pipeline.jpx_encode(arr, None, presized=True, jpx_q=90)
    assert q90 == pipeline.jpx_encode(arr, None, rate=reference_rate(90), presized=True)
    decoded = np.asarray(Image.open(io.BytesIO(q75)).convert("RGB"))
    coarse = np.asarray(Image.open(io.BytesIO(low)).convert("RGB"))
    mse = lambda value: np.mean((value.astype(float)-arr.astype(float))**2)
    assert decoded.shape == arr.shape and mse(decoded) < mse(coarse)


def test_quality_reference_sees_only_final_prepared_pixels_and_legacy_bypasses_it(monkeypatch):
    arr = artwork()
    original, calls = pipeline.jpeg_encode, []

    def observe(img, quality):
        calls.append((np.asarray(img).copy(), quality))
        return original(img, quality)

    monkeypatch.setattr(pipeline, "jpeg_encode", observe)
    encoded = pipeline.jpx_encode(arr, None, presized=True, jpx_q=75)
    assert len(calls) == 1 and calls[0][1] == 75
    assert np.array_equal(calls[0][0], arr)
    reference_ratio = jpx_reference_rate(arr.nbytes, len(original(Image.fromarray(arr), 75)))
    # Explicit-ratio encode bypasses JPEG. Equality proves it encoded original
    # samples, not reference-JPEG decoded/blurred/recoloured samples.
    assert encoded == pipeline.jpx_encode(arr, None, rate=reference_ratio, presized=True)
    pipeline.jpx_encode(arr, None, lossless=True, presized=True)
    assert len(calls) == 1


def test_reference_is_encoded_after_the_only_resize(monkeypatch):
    arr, calls = artwork(), []
    original = pipeline.jpeg_encode
    monkeypatch.setattr(pipeline, "jpeg_encode",
                        lambda img, q: (calls.append(img.size), original(img, q))[1])
    payload = pipeline.jpx_encode(arr, 12, jpx_q=75)
    assert Image.open(io.BytesIO(payload)).size == calls[0] == (132, 99)


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


def test_jpx_quality_identity_depends_on_reference_profile_but_legacy_does_not(monkeypatch):
    from pdf_minify.core import recipes
    selected = dict(mode="jpx", jpx_q=75)
    legacy, exact = dict(mode="jpx", rate=26), dict(mode="jpx", lossless=True)
    keys = [spec_key(s) for s in (selected, legacy, exact)]
    monkeypatch.setattr(recipes, "JPEG_ENCODING_PROFILE", "other-reference")
    assert spec_key(selected) != keys[0]
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


def test_q75_publication_keeps_historical_controls_distinct():
    from pathlib import Path
    from tools import publish_best_overview as publication
    report = Path("docs/INTEGRATED_COMPRESSION.md").read_text()
    assert "**Lossy baseline (§§265–267).**" in report
    assert "JPEG q50 / JPX r192" in report
    assert "Lossy baseline (§§265–267)" in Path(publication.__file__).read_text()


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
        reference = pipeline.jpeg_encode(canvas, quality)
        target = jpx_reference_rate(canvas.width * canvas.height * 3, len(reference))
        expected = pipeline.jpx_encode(np.asarray(canvas), None, rate=target, presized=True)
    assert payload["stream"] == expected
    with fitz.open(output) as doc:
        page = doc[0]
        assert bool(page.get_text().strip()) != force
        images = page.get_images(full=True)
        assert len(images) == 1
        assert images[0][2:4] == (256, 240)
        assert doc.xref_stream_raw(images[0][0]) == expected
        assert page.get_pixmap().width == 256  # the actual complete file decodes
