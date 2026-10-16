import fitz
import numpy as np
from PIL import Image
import io
import pytest
from pdf_minimalist.core.pipeline import process_file, recompress_file, gc_copy, PAGE_SIZES
from pdf_minimalist.core.cancel import CancelToken
from pdf_minimalist.core.display import DisplayPage


def _make_mixed(path: str):
    d = fitz.open()
    p = d.new_page(width=400, height=400)
    p.insert_text((50, 200), "Hello born-digital")
    d.save(path)
    d.close()


def test_default_keeps_original_size(tmp_path):
    """Designer §74: saving never reshapes pages unless asked."""
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_mixed(src)
    process_file(src, out, strategy="otsu", token=CancelToken())
    with fitz.open(out) as o:
        r = o[0].rect
        assert (round(r.width), round(r.height)) == (400, 400)


def test_letter_explicit(tmp_path):
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_mixed(src)
    process_file(src, out, strategy="otsu", page_size="letter", token=CancelToken())
    with fitz.open(out) as o:
        r = o[0].rect
        assert (round(r.width), round(r.height)) == (612, 792)


def test_absurd_pages():
    from pdf_minimalist.core.pipeline import absurd_pages
    assert absurd_pages([(612.0, 792.0)]) == []  # letter fine
    assert absurd_pages([(960.0, 540.0)]) == []  # 16:9 slides pass
    assert absurd_pages([(72.0, 1400.0)]) == [0]  # strip scan flagged
    assert absurd_pages([(612.0, 792.0), (50.0, 50.0)]) == [1]  # tiny page


def test_original_size(tmp_path):
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_mixed(src)
    process_file(src, out, strategy="otsu", page_size="original", token=CancelToken())
    with fitz.open(out) as o:
        r = o[0].rect
        assert (round(r.width), round(r.height)) == (400, 400)


def test_unforced_save_keeps_text_and_1bits_images(tmp_path):
    """Designer §127: FFPR OFF keeps vector text and replaces every image
    with a 1-bit version — never a color JPEG in a BW output."""
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_photo(src)  # photo + "caption keeps text layer"
    process_file(src, out, strategy="otsu", force_raster=False,
                 token=CancelToken())
    with fitz.open(out) as o:
        assert "caption" in o[0].get_text()  # text kept vector
        imgs = o[0].get_images(full=True)
        assert len(imgs) >= 1
        for e in imgs:
            assert o.xref_get_key(e[0], "BitsPerComponent") == ("int", "1"), e[0]


def test_force_keys_differ_by_force():
    """Designer §127: forced and unforced are different outputs — preview,
    mini and amount keys all carry the force."""
    from pdf_minimalist.ui_qt.app import MainWindow
    a = {"preset_id": "bw-otsu", "mode": "bw", "dpi": 300,
         "strategy": "otsu", "t": 180, "force_raster": True}
    b = dict(a, force_raster=False)
    assert MainWindow._spec_tuple(a) != MainWindow._spec_tuple(b)
    from pdf_minimalist.ui_qt.artifacts import ArtifactStore
    # Preview, mini, and final bytes all share this one real-file identity.
    uid = "1b81d828-6917-4684-bf1f-ab268ce009a3"
    assert ArtifactStore.key("f", a, uid) != ArtifactStore.key("f", b, uid)


def test_bw_save_flattens_text_pages(tmp_path):
    """Designer §127: FFPR ON flattens even text pages to one image."""
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_mixed(src)
    process_file(src, out, strategy="otsu", token=CancelToken())
    with fitz.open(out) as o:
        assert o[0].get_text().strip() == ""  # rasterized, no text layer
        assert len(o[0].get_images(full=True)) == 1  # one page image


@pytest.mark.parametrize("png_fallback", [False, True])
def test_distinct_forced_pages_keep_their_own_image_payload(tmp_path, monkeypatch, png_fallback):
    """Different JBIG2 pages must never overwrite one shared placeholder xref."""
    from pdf_minimalist.core.pipeline import _threshold
    if png_fallback:
        monkeypatch.setattr("pdf_minimalist.core.pipeline.bw_page_jbig2", lambda *a, **k: None)
    source, output = tmp_path / "distinct.pdf", tmp_path / "distinct-bw.pdf"
    with fitz.open() as doc:
        for i in range(3):
            page = doc.new_page(width=144, height=180)
            page.insert_text((10, 25), f"Page {i + 1}")
            page.draw_rect(fitz.Rect(10 + i * 25, 50, 30 + i * 25, 150),
                           color=(0, 0, 0), fill=(0, 0, 0))
        doc.save(source)
    process_file(str(source), str(output), strategy="simple", t=180,
                 dpi=72, force_raster=True)
    with fitz.open(source) as src, fitz.open(output) as out:
        assert len({page.get_images()[0][0] for page in out}) == 3
        for i in range(3):
            orig = DisplayPage(src[i]).render()
            saved = out[i].get_pixmap(dpi=72, colorspace=fitz.csGRAY, alpha=False)
            rgb = Image.frombytes("RGB", (orig.width, orig.height), orig.samples)
            expect = _threshold(np.asarray(rgb.convert("L")), "simple", 180)
            got = np.frombuffer(saved.samples, dtype=np.uint8).reshape(saved.height, saved.width)
            assert np.array_equal(got, expect), i


def test_bad_page_size_rejected(tmp_path):
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_mixed(src)
    try:
        process_file(src, out, page_size="bogus", token=CancelToken())
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def _make_photo(path: str):
    rng = np.random.default_rng(7)
    arr = (rng.random((900, 1200, 3)) * 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, "PNG")
    d = fitz.open()
    p = d.new_page(width=600, height=800)
    p.insert_image(fitz.Rect(0, 0, 600, 450), stream=buf.getvalue())
    p.insert_text((50, 700), "caption keeps text layer")
    d.save(path)
    d.close()


def test_color_recompress_shrinks_keeps_text(tmp_path):
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_photo(src)
    n_in = len(open(src, "rb").read())
    recompress_file(src, out, dpi_cap=150, jpeg_q=45, token=CancelToken())
    n_out = len(open(out, "rb").read())
    assert n_out < n_in, (n_in, n_out)
    with fitz.open(out) as o:
        assert o.page_count == 1
        assert "caption" in o[0].get_text()


def test_gc_copy_roundtrip(tmp_path):
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_mixed(src)
    gc_copy(src, out)
    with fitz.open(out) as o:
        assert o.page_count == 1
        assert "Hello" in o[0].get_text()


def _make_dense(path: str):
    import numpy as _np
    rng = _np.random.default_rng(11)
    arr = (rng.random((500, 400, 3)) * 255).astype(_np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, "PNG")
    d = fitz.open()
    p = d.new_page(width=400, height=500)
    p.insert_image(fitz.Rect(0, 0, 400, 500), stream=buf.getvalue())
    d.save(path)
    d.close()


def test_jbig2_save_roundtrip(tmp_path):
    """Designer §3/§55: dense BW pages embed real JBIG2 and render with ink."""
    import shutil
    from pdf_minimalist.core.pipeline import bw_page_payload, jbig2_binary
    if shutil.which("jbig2") is None:
        import pytest
        pytest.skip("jbig2 binary missing")
    assert jbig2_binary() is not None
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_dense(src)
    process_file(src, out, strategy="otsu", dpi=100, token=CancelToken())
    with fitz.open(out) as o:
        assert o.page_count == 1
        imgs = o[0].get_images(full=True)
        assert imgs, "no embedded image"
        assert o.xref_get_key(imgs[0][0], "Filter")[1] == "/JBIG2Decode"
        px = o[0].get_pixmap(dpi=100, colorspace=fitz.csGRAY, alpha=False)
        got = np.frombuffer(px.samples, dtype=np.uint8).reshape(px.height, px.width)
        assert 0 in np.unique(got)  # ink survived, not a blank page
    # real payload beats the PNG fallback
    from pdf_minimalist.core.pdf_io import render_gray
    import fitz as _fz
    with _fz.open(src) as _d:
        g = render_gray(_d, 0, dpi=100, token=CancelToken())
    jb2, codec = bw_page_payload(g, "otsu")
    assert codec == "jbig2"
    from pdf_minimalist.core.pipeline import bw_page_png
    assert len(jb2) < len(bw_page_png(g, "otsu"))


def test_jbig2_fallback_stays_valid(tmp_path, monkeypatch):
    """A genuinely failed decode falls back to PNG — still valid ink.

    Sparse text previously failed only because encoded JBIG2 got an extra
    compression wrapper (B79). Inject invalid bytes instead of asserting
    that repaired, valid encoder output must always use a worse fallback.
    """
    from pdf_minimalist.core import pipeline
    monkeypatch.setattr(pipeline, "bw_page_jbig2", lambda *a, **k: b"invalid JBIG2")
    from pdf_minimalist.core.pdf_io import render_gray
    import fitz as _fz
    from pdf_minimalist.core.pipeline import bw_page_payload
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_mixed(src)
    with _fz.open(src) as _d:
        g = render_gray(_d, 0, dpi=300, token=CancelToken())
    _jb2, codec = bw_page_payload(g, "otsu")
    assert codec == "png"  # the injected encoder output really fails decode
    process_file(src, out, strategy="otsu", token=CancelToken())
    with fitz.open(out) as o:
        px = o[0].get_pixmap(dpi=100, colorspace=fitz.csGRAY, alpha=False)
        got = np.frombuffer(px.samples, dtype=np.uint8).reshape(px.height, px.width)
        assert got.min() < 128  # dark ink pixels, never a blank/failed page


def test_jbig2_pixel_exact(tmp_path):
    """Dense JBIG2 embed round-trips bit-exact (lossless proof)."""
    import shutil
    if shutil.which("jbig2") is None:
        import pytest
        pytest.skip("jbig2 binary missing")
    from pdf_minimalist.core.pdf_io import render_gray
    from pdf_minimalist.core.pipeline import bw_page_jbig2, _place_bw, _threshold, jbig2_renders
    src = str(tmp_path / "in.pdf")
    _make_dense(src)
    with fitz.open(src) as _d:
        g = render_gray(_d, 0, dpi=100, token=CancelToken())
    h, w = g.shape
    jb2 = bw_page_jbig2(g, "otsu")
    assert jb2
    assert jbig2_renders(jb2, w, h, _threshold(g))
    out = fitz.open()
    s = 72 / 100
    page = out.new_page(width=w * s, height=h * s)
    _place_bw(out, page, fitz.Rect(0, 0, w * s, h * s), jb2, "jbig2", w, h)
    pdf = str(tmp_path / "t.pdf")
    out.save(pdf, garbage=4, deflate=True)
    out.close()
    with fitz.open(pdf) as o:
        px = o[0].get_pixmap(dpi=100, colorspace=fitz.csGRAY, alpha=False)
        got = np.frombuffer(px.samples, dtype=np.uint8).reshape(px.height, px.width)
    assert got.shape == _threshold(g).shape
    assert np.array_equal(got, _threshold(g))


def _make_flat_logo(path: str):
    """Few-color image (designer §57): flat red/blue/white, 3 colors."""
    import numpy as _np
    arr = _np.full((400, 500, 3), 255, dtype=_np.uint8)
    arr[50:200, 50:450] = (200, 30, 30)
    arr[220:350, 50:450] = (30, 60, 200)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, "PNG")
    d = fitz.open()
    p = d.new_page(width=500, height=400)
    p.insert_image(fitz.Rect(0, 0, 500, 400), stream=buf.getvalue())
    d.save(path)
    d.close()


def test_jpx_lossless_roundtrip_exact(tmp_path):
    """Designer §100: JPX lossless choice round-trips bit-exact."""
    from pdf_minimalist.core.pipeline import jpx_encode
    import numpy as _np
    rng = _np.random.default_rng(8)
    arr = (rng.random((120, 160, 3)) * 255).astype(_np.uint8)
    data = jpx_encode(arr, 150, lossless=True)
    back = _np.asarray(Image.open(io.BytesIO(data)).convert("RGB"))
    assert back.shape == arr.shape
    assert (_np.asarray(back) == arr).all()


def test_jpx_recompress_roundtrip(tmp_path):
    """Designer §56: JPX codec path embeds JPXDecode and renders back."""
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_photo(src)
    before = len(open(src, "rb").read())
    recompress_file(src, out, dpi_cap=150, token=CancelToken(), codec="jpx", rate=24)
    after = len(open(out, "rb").read())
    assert after < before
    with fitz.open(out) as o:
        imgs = [e for p in o for e in p.get_images(full=True)]
        assert imgs, "no images left"
        assert "caption" in o[0].get_text()  # vectors/text preserved


def test_indexed_palette_wins_on_flat(tmp_path):
    """Designer §57: few-color images go lossless Flate, smaller than JPEG."""
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_flat_logo(src)
    recompress_file(src, out, dpi_cap=150, jpeg_q=45, token=CancelToken())
    with fitz.open(out) as o:
        imgs = o[0].get_images(full=True)
        assert imgs, "no embedded image"
        assert o.xref_get_key(imgs[0][0], "Filter")[1] == "/FlateDecode"
    assert len(open(out, "rb").read()) < len(open(src, "rb").read())


def test_indexed_forced_mode(tmp_path):
    """Designer §67: Indexed filters force the palette count on save."""
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_flat_logo(src)
    recompress_file(src, out, dpi_cap=150, token=CancelToken(),
                    codec="indexed", colors=16)
    with fitz.open(out) as o:
        imgs = o[0].get_images(full=True)
        assert imgs, "no embedded image"
        assert o.xref_get_key(imgs[0][0], "Filter")[1] == "/FlateDecode"
        # count colors in the EMBEDDED stream (renders resample edges).
        # True Indexed decodes to exact palette entries — no ICC fanning.
        info = o.extract_image(imgs[0][0])
        emb = np.asarray(Image.open(io.BytesIO(info["image"])).convert("RGB"))
        assert len(np.unique(emb.reshape(-1, 3), axis=0)) <= 16


def test_indexed_helpers():
    from pdf_minimalist.core.pipeline import indexed_rgb, quantize_method
    import numpy as _np
    rng = _np.random.default_rng(4)
    arr = (rng.random((60, 80, 3)) * 255).astype(_np.uint8)
    assert quantize_method() in (Image.MEDIANCUT, Image.FASTOCTREE, Image.MAXCOVERAGE)
    out = indexed_rgb(arr, 16)
    assert out.shape == arr.shape
    assert len(_np.unique(out.reshape(-1, 3), axis=0)) <= 16


def test_indexed_palette_no_overflow():
    """Live-log bug: numpy uint8 index math wrapped past 85 palette entries."""
    from pdf_minimalist.core.pipeline import indexed_parts
    import numpy as _np
    rng = _np.random.default_rng(21)
    arr = (rng.random((40, 50, 3)) * 255).astype(_np.uint8)
    parts = indexed_parts(Image.fromarray(arr), 256)
    n = parts["hival"] + 1
    assert len(parts["palette"]) == 3 * n


def test_flate_stream_decodes_exact():
    """Designer §80 fix: Flate streams carry raw rows, no filter bytes."""
    import zlib
    from pdf_minimalist.core.pipeline import flate_rgb_encode
    import numpy as _np
    arr = _np.arange(24, dtype=_np.uint8).reshape(2, 4, 3)
    assert zlib.decompress(flate_rgb_encode(arr)) == arr.tobytes()


def test_true_indexed_bpc_and_render(tmp_path):
    """Designer §80: bit depth follows actual entries; render is exact."""
    from pdf_minimalist.core.pipeline import indexed_parts, _place_indexed
    import fitz as _fz
    import numpy as _np
    img2 = Image.new("RGB", (32, 32))
    img2.putdata([(255, 0, 0)] * 512 + [(0, 0, 255)] * 512)
    parts = indexed_parts(img2, 256)
    assert parts["bpc"] == 1 and parts["hival"] == 1 and len(parts["palette"]) == 6
    out = _fz.open()
    page = out.new_page(width=32, height=32)
    from pdf_minimalist.core.pipeline import _tiny_png
    page.insert_image(_fz.Rect(0, 0, 32, 32), stream=_tiny_png())
    xref = page.get_images(full=True)[-1][0]
    _place_indexed(out, xref, parts)
    pdf = str(tmp_path / "idx.pdf")
    out.save(pdf, garbage=4, deflate=True)
    out.close()
    with _fz.open(pdf) as o:
        assert o.xref_get_key(o[0].get_images(full=True)[0][0],
                              "BitsPerComponent")[1] == "1"
        px = o[0].get_pixmap(dpi=72, colorspace=_fz.csRGB, alpha=False)
        got = _np.frombuffer(px.samples, dtype=_np.uint8).reshape(32, 32, 3)
        assert set(map(tuple, _np.unique(got.reshape(-1, 3), axis=0))) <= \
            {(255, 0, 0), (0, 0, 255)}


def test_bw_save_photo_page_single_image(tmp_path):
    """Designer §126: photo pages flatten to one image, smaller than input."""
    src = str(tmp_path / "in.pdf")
    out = str(tmp_path / "out.pdf")
    _make_photo(src)
    n_in = len(open(src, "rb").read())
    process_file(src, out, strategy="otsu", token=CancelToken())
    assert len(open(out, "rb").read()) < n_in
    with fitz.open(out) as o:
        assert o.page_count == 1
        assert len(o[0].get_images(full=True)) == 1
