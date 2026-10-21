"""Per-page + whole-file BW pipeline with per-page cancel checks.

GUI defaults preserve text and original page size (§§74/103/127), with one
explicit full-page BW example. All processing goes through save_with_spec.
"""
import pymupdf as fitz
import numpy as np
from PIL import Image
import io
import logging
import os
import subprocess
import tempfile
import zlib
from functools import wraps
from contextvars import ContextVar

from .cancel import CancelToken
from .external_tools import find_tool
from .pdf_io import CancelledError, render_gray, FITZ_LOCK
from . import threshold as T
from .image_layers import compose_page_images, compose_color_page
from .algorithms import BW_MODES, COLOR_MODES
from .stream_compression import STREAM_LABELS, permits_brotli, recompress_native_streams
from .defaults import DEFAULT_DPI
from .quality import DEFAULT_LOSSY_QUALITY, JPX_TILE, checked_quality, jpx_lossy_setting, jpx_quality_psnr
from .canvas import flatten_rgb

log = logging.getLogger("pdf_minify")
_ENCODE_WORKDIR = ContextVar("encoder_workdir", default=None)
_STREAM_POLICY = ContextVar("stream_compression", default="flate")
_PNG_PREDICTION = ContextVar("png_prediction", default=None)
_BROTLI_DECLARATION = ContextVar("brotli_declaration", default=False)
_SAVE_TOKEN = ContextVar("save_token", default=None)

# points (1/72 in). Letter = 8.5x11in, A4 = 210x297mm.
PAGE_SIZES = {
    "original": None,
    "letter": (612.0, 792.0),
    "a4": (595.28, 841.89),
}
DEFAULT_PAGE_SIZE = "original"  # §74: never reshape by default; Letter/A4 are
# advanced-only fixes for absurd scan sizes (flagged, never auto-applied).


def absurd_pages(rects) -> list:
    """0-based indices of pages whose size looks like a broken scan (§74).

    Flags a side under 2in (144pt) or over 24in (1728pt), or an aspect wilder
    than 1:3 — while ordinary slides (16:9 ≈ 1.78) and photos pass quietly.
    The app suggests Letter/A4 for these; it never reshapes on its own.
    """
    bad = []
    for i, r in enumerate(rects):
        w, h = float(r[0]), float(r[1])
        if w <= 0 or h <= 0:
            continue
        if min(w, h) < 144 or max(w, h) > 1728:
            bad.append(i)
            continue
        a = w / h
        if a < 1 / 3 or a > 3:
            bad.append(i)
    return bad


def _fitz_locked(fn):
    """Serialize MuPDF use within one process; GUI jobs use spawn processes."""
    @wraps(fn)
    def inner(*a, **k):
        with FITZ_LOCK:
            return fn(*a, **k)
    return inner


def _threshold(gray: np.ndarray, strategy: str = "otsu", t: int = 180) -> np.ndarray:
    """Grayscale array -> 0/255 array (designer §3: the BW algorithm)."""
    if strategy == "simple":
        return T.simple(gray, t)
    elif strategy == "otsu":
        return T.otsu(gray)
    elif strategy == "adaptive":
        return T.adaptive_mean(gray)
    elif strategy == "sauvola":
        return T.sauvola(gray)
    else:
        raise ValueError(strategy)


def bw_page_png(gray: np.ndarray, strategy: str = "otsu", t: int = 180) -> bytes:
    """Grayscale array -> 1-bit PNG bytes (fallback payload when no JBIG2)."""
    bw = _threshold(gray, strategy, t)
    img = Image.fromarray(bw).convert("1")
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def jbig2_binary() -> str | None:
    """Path to the JBIG2 encoder (designer §3), or None if not installed."""
    return find_tool("jbig2")


def bw_page_jbig2(gray: np.ndarray, strategy: str = "otsu", t: int = 180,
                  timeout: int = 120) -> bytes | None:
    """Grayscale array -> self-contained JBIG2 page stream (designer §3).

    Lossless generic-region coding via `jbig2 -p` (PDF-ready data, no shared
    globals — every page decodes standalone). Returns None when the encoder
    is missing or fails; the caller falls back to 1-bit PNG.
    """
    return encode_binary_jbig2(_threshold(gray, strategy, t), timeout)


def encode_binary_jbig2(bw: np.ndarray, timeout: int = 120) -> bytes | None:
    """Lossless generic-region encoder shared by BW and colored stencils.

    A 1-bit PNG is input transport, NOT an output codec fallback. P4 dimension
    readers can consume a leading packed whitespace byte as header space.
    """
    binary = jbig2_binary()
    if binary is None:
        return None
    fd, png = tempfile.mkstemp(prefix="encode-jbig2-", suffix=".png",
                              dir=_ENCODE_WORKDIR.get())
    try:
        with os.fdopen(fd, "wb") as f:
            Image.fromarray(bw).convert("1", dither=Image.Dither.NONE).save(f, "PNG")
        try:
            r = subprocess.run([binary, "-p", png], capture_output=True,
                               timeout=timeout)
        except (OSError, subprocess.TimeoutExpired):
            return None
        if r.returncode != 0 or not r.stdout:
            return None
        return bytes(r.stdout)
    finally:
        try:
            os.unlink(png)
        except OSError:
            pass


def bw_page_payload(gray: np.ndarray, strategy: str = "otsu", t: int = 180,
                    *, codec: str | None = None) -> tuple[bytes, str]:
    """Real save payload for one BW page: (bytes, "jbig2" | "png").

    JBIG2 wins only when the bytes test-decode pixel-exact in our renderer;
    otherwise use 1-bit PNG. The former sparse-stream failure was caused by
    a corrupt PDF wrapper (B79), not proof of an encoder defect. GUI captions
    measure the complete saved PDF, never sums of these payloads.
    """
    if codec not in (None, "jbig2", "flate"):
        raise ValueError(f"Unknown BW codec: {codec}")
    if codec == "flate":
        return bw_page_png(gray, strategy, t), "png"
    jb2 = bw_page_jbig2(gray, strategy, t)
    if jb2 is not None:
        bw = _threshold(gray, strategy, t)
        h, w = bw.shape[:2]
        if jbig2_renders(jb2, w, h, bw):
            return jb2, "jbig2"
    if codec == "jbig2":
        raise RuntimeError("JBIG2 encoding unavailable or failed exact validation; "
                           "install jbig2 or choose Flate BW.")
    return bw_page_png(gray, strategy, t), "png"


@_fitz_locked
def jbig2_renders(payload: bytes, w: int, h: int, expect: np.ndarray) -> bool:
    """True iff MuPDF decodes this JBIG2 stream back to `expect` (0/255).

    Same engine renders previews, main panes and minis: a stream that fails
    here must never be embedded.
    """
    # Do not clear/consume another caller's diagnostics. All native validation
    # is serialized; a newly appended error invalidates even an all-black match.
    prior_diagnostics = fitz.TOOLS.mupdf_warnings(reset=False)
    try:
        d = fitz.open()
        try:
            page = d.new_page(width=w, height=h)
            _place_bw(d, page, fitz.Rect(0, 0, w, h), payload, "jbig2", w, h)
            px = page.get_pixmap(dpi=72, colorspace=fitz.csGRAY, alpha=False)
            got = np.frombuffer(px.samples, dtype=np.uint8).reshape(px.height, px.width)
            diagnostics = fitz.TOOLS.mupdf_warnings(reset=False)
            return (diagnostics == prior_diagnostics and got.shape == expect.shape
                    and bool(np.array_equal(got, expect)))
        finally:
            d.close()
    except Exception:
        return False


def _fit_rect(src_w: float, src_h: float, dst_w: float, dst_h: float) -> fitz.Rect:
    """Aspect-fit src dimensions into dst page, centered."""
    scale = min(dst_w / src_w, dst_h / src_h)
    w, h = src_w * scale, src_h * scale
    x0 = (dst_w - w) / 2
    y0 = (dst_h - h) / 2
    return fitz.Rect(x0, y0, x0 + w, y0 + h)


def jpeg_encode(img: Image.Image, quality: int = DEFAULT_LOSSY_QUALITY) -> bytes:
    """Fixed full-chroma JPEG profile; only quality is user-facing (§§272/278)."""
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=checked_quality(quality), optimize=True, subsampling=0)
    return buf.getvalue()


def jpx_encode(arr: np.ndarray, dpi_cap: int | None, rate: float | None = None,
               lossless: bool = False, presized: bool = False, *,
               jpx_q: int | None = None) -> bytes:
    """RGB array -> JPEG2000 bytes at the cap rule (designer §56).

    Used by the real saver; previews read its resulting PDF. Lossless
    (`§100`, reversible 5/3) when asked; otherwise the lossy 9/7 + RGB
    colour-transform profile at user-facing quality or an explicit legacy
    rate. Never reinterpret an old ratio. Technical options stay internal.
    presized=True skips the legacy downscale (designer §129: the caller
    already forced exact DPI — never scale twice).
    """
    setting, value = jpx_lossy_setting(dict(lossless=lossless, rate=rate, jpx_q=jpx_q))
    h, w = arr.shape[:2]
    img = Image.fromarray(arr)
    if not presized:
        if dpi_cap is None:
            raise ValueError("DPI is required unless the canvas is already sized")
        scale = min(1.0, (dpi_cap * 11) / max(w, h))
        if scale < 1.0:
            img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    buf = io.BytesIO()
    # Six resolutions is OpenJPEG's normal profile. Tiny helper inputs need
    # fewer decompositions; neither path introduces spatial subsampling.
    resolutions = min(6, min(img.size).bit_length())
    lossy = dict(irreversible=True, mct=int(img.mode == "RGB"), num_resolutions=resolutions,
                 codeblock_size=(64, 64), progression="LRCP")
    if setting == "lossless":
        img.save(buf, "JPEG2000", quality_mode="lossless", num_resolutions=resolutions)
    elif setting == "quality":
        # §284: one PSNR target per 512-pixel tile, calibrated against JPEG.
        img.save(buf, "JPEG2000", quality_mode="dB", quality_layers=[jpx_quality_psnr(value)],
                 tile_size=(JPX_TILE, JPX_TILE), **lossy)
    else:
        # Explicit legacy ratio: unchanged single-tile profile and meaning.
        img.save(buf, "JPEG2000", quality_mode="rates", quality_layers=[value],
                 tile_size=None, **lossy)
    return buf.getvalue()


def flate_rgb_encode(arr: np.ndarray) -> bytes:
    """RGB array -> raw Flate stream bytes (designer §80 fix).

    Plain concatenated scanlines with Predictor 1 (none): NO PNG filter
    bytes. An earlier version prepended \\x00 per row without declaring a
    predictor, shifting every row one byte in strict decoders.
    """
    return zlib.compress(np.ascontiguousarray(arr).tobytes())


def bpc_for(ncolors: int) -> int:
    """Smallest PDF bit depth holding ncolors entries (designer §80)."""
    if ncolors <= 2:
        return 1
    if ncolors <= 4:
        return 2
    if ncolors <= 16:
        return 4
    return 8


def pack_indices(idx: np.ndarray, bpc: int) -> bytes:
    """Packed index samples, first sample in the high-order bits."""
    h, w = idx.shape[:2]
    if bpc == 8:
        return np.ascontiguousarray(idx, dtype=np.uint8).tobytes()
    per = 8 // bpc
    out = bytearray()
    for y in range(h):
        bits = n = 0
        for x in range(w):
            bits = (bits << bpc) | int(idx[y, x])
            n += 1
            if n == per:
                out.append(bits)
                bits = n = 0
        if n:
            out.append(bits << (8 - n * bpc))
    return bytes(out)


def zopfli_binary() -> str | None:
    return find_tool("zopfli")


def deflate_best(data: bytes) -> bytes:
    """Validated zlib-wrapped Deflate for PDF /FlateDecode (designer §80).

    zopfli wins ~6% over zlib-9 but costs 60x time, so it applies only below
    100KB (fast either way); above that zlib-9. Zopfli's default gzip wrapper
    is NOT a PDF Flate stream. Roundtrip validation rejects wrong containers.
    """
    if (_STREAM_POLICY.get() == "best"
            or (_STREAM_POLICY.get() == "zopfli" and _PNG_PREDICTION.get() is not None)):
        # Preparation transport only. The final selector runs the selected
        # full encoder(s) once per distinct sample/predictor input; do not run
        # the old opportunistic Zopfli path first and then repeat that work.
        return zlib.compress(data, 9)
    binary = zopfli_binary() if len(data) <= 100_000 else None
    if binary is not None:
        fd, tmp = tempfile.mkstemp(prefix="encode-zopfli-", dir=_ENCODE_WORKDIR.get())
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(data)
            try:
                r = subprocess.run([binary, "--zlib", "-c", tmp], capture_output=True,
                                   timeout=120)
            except (OSError, subprocess.TimeoutExpired):
                return zlib.compress(data, 9)
            if r.returncode == 0 and r.stdout:
                try:
                    if zlib.decompress(r.stdout) == data:
                        return bytes(r.stdout)
                except zlib.error:
                    pass
        finally:
            try:
                os.unlink(tmp)
            except OSError:
                pass
    return zlib.compress(data, 9)


def indexed_parts(img: "Image.Image", colors: int) -> dict:
    """Forced palette reduction to PDF-ready parts (designer §80).

    Automatic algorithm, never dithered; bit depth follows the ACTUAL used
    entries (16 requested but 10 used → 4bpc). Returns stream/palette/bpc/
    dims for a true Indexed color space — typically 10x smaller than the
    RGB-Flate equivalent on flat graphics.
    """
    q = _quantize_palette(img, colors)
    idx = np.asarray(q)
    used, inv = np.unique(idx, return_inverse=True)
    n = len(used)
    bpc = bpc_for(n)
    pal = q.getpalette()
    # int() first: `used` holds numpy uint8, whose i*3 overflows past 85
    # and silently writes wrong palette bytes (found in the live log).
    pal_bytes = b"".join(bytes(pal[i * 3:i * 3 + 3]) for i in map(int, used))
    packed = pack_indices(inv.reshape(idx.shape).astype(np.uint8), bpc)
    return {"stream": deflate_best(packed), "palette": pal_bytes,
            "bpc": bpc, "hival": n - 1, "w": idx.shape[1], "h": idx.shape[0]}


def indexed_flate_candidate(img: "Image.Image") -> dict | None:
    """Few-color image (designer §57) -> true Indexed parts, else None.

    Images with at most 256 distinct colors (logos, diagrams, flat UI shots)
    quantize losslessly; the winner is picked by total bytes elsewhere.
    """
    rgb = img.convert("RGB")
    if rgb.getcolors(maxcolors=257) is None:
        return None
    return indexed_parts(rgb, 256)


def quantize_method() -> int:
    """Coverage initialization for the shared palette fitter (§183).

    FASTOCTREE's bucket mapping sends unrepresented buckets to index zero
    instead of the nearest palette color. A smaller wrong image is no win.
    Median-cut alone wastes low-color slots on near-white page background.
    Fit representative colors, then assign ALL pixels by exact RGB distance.
    """
    return Image.MAXCOVERAGE


def _quantize_palette(img, colors):
    """ONE quantization path for embedded Indexed and headless RGB helpers."""
    rgb = img.convert("RGB")
    limit = max(2, min(256, int(colors)))
    exact = rgb.getcolors(maxcolors=limit)
    if exact is not None:
        palette = np.array(sorted(color for _, color in exact), dtype=np.uint8)
    else:
        scale = min(1.0, 512 / max(rgb.size))
        fit = rgb.resize((max(1, round(rgb.width*scale)),
                          max(1, round(rgb.height*scale))), Image.Resampling.NEAREST)
        fitted = fit.quantize(colors=limit, method=quantize_method(), kmeans=1,
                              dither=Image.Dither.NONE)
        used = sorted(index for _, index in fitted.getcolors())
        palette = np.asarray(fitted.getpalette(), dtype=np.uint8).reshape(-1, 3)[used].copy()
        if np.any(np.all(np.asarray(fit) == 255, axis=2)):
            near_white = ((palette.astype(np.int32) - 255)**2).sum(1).argmin()
            palette[near_white] = 255
    source = np.asarray(rgb).reshape(-1, 3)
    indices = np.empty(len(source), dtype=np.uint8)
    p = palette.astype(np.int32)
    norms = (p*p).sum(1, dtype=np.int32)
    # At most 8192×256 int32 pair scores (8MiB), not a whole-page distance
    # tensor. The omitted source norm is constant within each argmin row.
    palette_keys = (p[:, 0] << 16) | (p[:, 1] << 8) | p[:, 2]
    for start in range(0, len(source), 8192):
        block = source[start:start+8192].astype(np.int32)
        if exact is not None:
            keys = (block[:, 0] << 16) | (block[:, 1] << 8) | block[:, 2]
            chosen = np.searchsorted(palette_keys, keys)
        else:
            distances = block @ p.T
            distances *= -2
            distances += norms
            chosen = distances.argmin(1)
        indices[start:start+len(block)] = chosen
    result = Image.frombytes("P", rgb.size, indices.tobytes())
    result.putpalette(palette.tobytes())
    return result


def indexed_rgb(arr: np.ndarray, colors: int) -> np.ndarray:
    """RGB array -> palette-reduced RGB array (designer §67).

    Automatic algorithm (`quantize_method`), never dithered.
    """
    return np.asarray(_quantize_palette(Image.fromarray(np.asarray(arr)), colors).convert("RGB"))


def _place_indexed(doc: "fitz.Document", xref: int, parts: dict):
    """Embed true Indexed parts: Flate index stream + inline hex palette."""
    doc.update_stream(xref, parts["stream"], compress=False)
    doc.xref_set_key(xref, "Filter", "/FlateDecode")
    doc.xref_set_key(xref, "Width", str(parts["w"]))
    doc.xref_set_key(xref, "Height", str(parts["h"]))
    doc.xref_set_key(
        xref, "ColorSpace",
        f"[/Indexed /DeviceRGB {parts['hival']} <{parts['palette'].hex().upper()}>]")
    doc.xref_set_key(xref, "BitsPerComponent", str(parts["bpc"]))
    try:
        cur = doc.xref_get_key(xref, "DecodeParms")
        if cur[0] != "null":
            doc.xref_set_key(xref, "DecodeParms", "null")
    except Exception:
        pass


def color_canvas_payload(img, codec="jpeg", jpeg_q=DEFAULT_LOSSY_QUALITY, rate=None,
                         colors=64, lossless=False, *, allow_substitution=True,
                         token=None, jpx_q=None):
    """Transform an ALREADY flattened, final-DPI RGB canvas (§§180/182).

    No per-image alpha guard, size skip or keep-original branch. The chosen
    filter runs on the actual composite. Lossless Indexed may beat a lossy
    codec for genuinely few-color canvases; forced Indexed always quantizes.
    """
    if img.mode != "RGB":
        raise ValueError("Color transforms require a flattened RGB canvas")
    iw, ih = img.width, img.height
    if codec == "layered-jbig2":
        from .stencils import PaletteCanvas
        return {"stencils": PaletteCanvas.from_rgb(img, colors), "token": token}
    if codec == "indexed":
        parts = indexed_parts(img, colors)
        return {"filter": "/FlateDecode", "stream": parts["stream"],
                "w": iw, "h": ih, "indexed": parts}
    if codec == "jpx":
        cands = [(jpx_encode(np.asarray(img), None, rate, lossless,
                             presized=True, jpx_q=jpx_q), "/JPXDecode", None)]
    elif codec == "jpeg":
        cands = [(jpeg_encode(img, jpeg_q), "/DCTDecode", None)]
    else:
        raise ValueError(f"Unknown color codec: {codec}")
    auto = indexed_flate_candidate(img) if allow_substitution else None
    if auto is not None:
        cands.append((auto["stream"], "/FlateDecode", auto))
    best = None
    for data, filtr, parts in cands:
        total = len(data) + (len(parts["palette"]) if parts else 0)
        if best is None or total < best[0]:
            best = (total, data, filtr, parts)
    _total, data, filtr, parts = best
    return {"filter": filtr, "stream": data, "w": iw, "h": ih, "indexed": parts}


def _place_color(out, page, rect, payload):
    """Fresh opaque composite XObject; never retain source masks/Decode keys."""
    if "stencils" in payload:
        from .stencils import place_stencils
        place_stencils(out, page, rect, payload["stencils"], payload["token"])
        return
    xref = out.get_new_xref()
    out.update_object(xref, f"<< /Type /XObject /Subtype /Image /Width {payload['w']} "
                      f"/Height {payload['h']} /ColorSpace /DeviceRGB /BitsPerComponent 8 "
                      "/Interpolate false >>")
    if payload["indexed"] is not None:
        _place_indexed(out, xref, payload["indexed"])
    else:
        out.update_stream(xref, payload["stream"], compress=False)
        out.xref_set_key(xref, "Filter", payload["filter"])
    page.insert_image(rect, xref=xref, overlay=True, keep_proportion=False)


def _tiny_png() -> bytes:
    """1x1 1-bit placeholder: creates the image xref that a JBIG2 stream
    then replaces (`insert_image` rejects raw JBIG2, so the xref must first
    exist as a decodable image)."""
    img = Image.new("1", (1, 1), 1)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _place_bw(out: "fitz.Document", page: "fitz.Page", rect: fitz.Rect,
              payload: bytes, codec: str, w: int, h: int, *, overlay=True):
    """Place an independently owned encoded image, never a mutable placeholder.

    insert_image deduplicates identical input streams. Mutating a reused tiny
    placeholder therefore changes every earlier page (B90). Allocate the real
    JBIG2 XObject first; deduplication at final save can safely merge only truly
    identical payloads. Return the actual placed xref.
    """
    if codec == "png":
        with Image.open(io.BytesIO(payload)) as image:
            if image.mode != "1" or image.size != (w, h):
                raise ValueError("BW fallback must be a correctly sized 1-bit PNG")
            payload = zlib.compress(image.tobytes(), 9)
        filtr = "/FlateDecode"
    elif codec == "jbig2":
        filtr = "/JBIG2Decode"
    else:
        raise ValueError(f"unsupported BW image codec: {codec}")
    xref = out.get_new_xref()
    out.update_object(xref, f"<< /Type /XObject /Subtype /Image /Width {w} "
                      f"/Height {h} /ColorSpace /DeviceGray "
                      "/BitsPerComponent 1 /Interpolate false >>")
    out.update_stream(xref, payload, compress=False)
    out.xref_set_key(xref, "Filter", filtr)
    return page.insert_image(rect, xref=xref, overlay=overlay,
                             keep_proportion=False)


@_fitz_locked
def force_to_dpi(img, target_w: int, target_h: int):
    """Resample a PIL image to exact dims with Lanczos (designer §129).

    The canvas calls this in full color BEFORE gray/threshold or palette
    reduction (§§180/182); original samples/masks are already composed.
    Same size in → same object back (no-op, not a copy roundtrip).
    """
    if (img.width, img.height) == (target_w, target_h):
        return img
    return img.resize((max(1, target_w), max(1, target_h)), Image.Resampling.LANCZOS)


def process_file(in_path: str, out_path: str, strategy: str = "otsu", t: int = 180,
                 dpi: int = 300, token: CancelToken | None = None,
                 progress=None, per_page: dict | None = None,
                 page_size: str = DEFAULT_PAGE_SIZE, force_raster: bool = True,
                 codec: str | None = None):
    """BW save with two honest modes (designer §127).

    force_raster=True: every page flattened to one 1-bit image.
    force_raster=False: ONE combined image canvas below original native
      text/vector artwork (§171); plain white page backgrounds stay below.
    per_page: {pageno: {"strategy"/"t"/"dpi"/"page_size"}} overrides.
    progress(pageno, total) called per page.
    Raises CancelledError on ESC. Deletes partial output on cancel (caller should unlink).
    """
    if page_size not in PAGE_SIZES:
        raise ValueError(f"page_size must be one of {sorted(PAGE_SIZES)}: {page_size!r}")
    token = token or CancelToken()
    per_page = per_page or {}
    src = fitz.open(in_path)
    out = fitz.open() if force_raster else fitz.open(in_path)
    from .native_layer import NativeContext
    native_context = NativeContext(out)
    n_jbig2 = n_png = n_img = 0
    try:
        for i in range(src.page_count):
            if token.cancelled:
                raise CancelledError()
            ov = per_page.get(i, {})
            strat = ov.get("strategy", strategy)
            tt = ov.get("t", t)
            dd = ov.get("dpi", dpi)
            ps = ov.get("page_size", page_size)
            if not force_raster:
                # §171: ONE image canvas + original native overlay.
                composed = compose_page_images(out, i, strat,
                                               tt, dd, token,
                                               lambda *a: bw_page_payload(*a, codec=codec),
                                               _place_bw, force_to_dpi,
                                               directory=_ENCODE_WORKDIR.get(),
                                               original=src, native_context=native_context)
                n_img += composed
                if progress:
                    progress(i + 1, src.page_count)
                continue
            rgb = flatten_rgb(src[i], dd, token, force_to_dpi,
                              directory=_ENCODE_WORKDIR.get(), minimum_dpi=dd)
            gray = np.asarray(rgb.convert("L"))
            if token.cancelled:
                raise CancelledError()
            payload, actual_codec = bw_page_payload(gray, strat, tt, codec=codec)
            if actual_codec == "jbig2":
                n_jbig2 += 1
            else:
                n_png += 1
                log.info("page %d: 1-bit Flate%s", i + 1,
                         " (legacy automatic fallback)" if codec is None else "")
            if token.cancelled:
                raise CancelledError()
            target = PAGE_SIZES[ps]
            if target is None:
                rect = src[i].rect
                page = out.new_page(width=rect.width, height=rect.height)
                _place_bw(out, page, rect, payload, actual_codec,
                          gray.shape[1], gray.shape[0])
            else:
                tw, th = target
                page = out.new_page(width=tw, height=th)
                srect = src[i].rect
                _place_bw(out, page,
                          _fit_rect(srect.width, srect.height, tw, th),
                          payload, actual_codec, gray.shape[1], gray.shape[0])
            if progress:
                progress(i + 1, src.page_count)
        _save_optimized_pdf(out, out_path)
        log.info("saved %s: BW pages JBIG2=%d PNG-fallback=%d images-1bit=%d",
                 out_path, n_jbig2, n_png, n_img)
    finally:
        out.close()
        src.close()


def _save_optimized_pdf(doc: "fitz.Document", out_path: str, *, no_new_id: bool = False,
                        subset_fonts: bool = True):
    """Shared optimizer; studies can freeze already-subset fonts/controlled IDs."""
    if subset_fonts:
        doc.subset_fonts()
    policy = _STREAM_POLICY.get()
    if policy == "best" or (policy == "zopfli" and _PNG_PREDICTION.get() is not None):
        from .best_streams import save_best_streams
        stats = save_best_streams(doc, out_path, writer=_write_optimized_pdf,
                                  directory=_ENCODE_WORKDIR.get(), token=_SAVE_TOKEN.get(),
                                  brotli_declaration=_BROTLI_DECLARATION.get(), no_new_id=no_new_id,
                                  policy=policy,
                                  image_prediction="best" if policy == "best" else _PNG_PREDICTION.get())
        log.info("Best PDF streams: %s; candidates=%s; Brotli=%d; packed images=%d",
                 stats["winner"], stats["candidate_bytes"], stats["brotli_streams"],
                 stats["image_streams"])
    else:
        stats = recompress_native_streams(doc, policy, directory=_ENCODE_WORKDIR.get(),
                                         token=_SAVE_TOKEN.get(),
                                         brotli_declaration=_BROTLI_DECLARATION.get())
        _write_optimized_pdf(doc, out_path, no_new_id=no_new_id)
    log.info("PDF streams: %s, %d streams, %d -> %d bytes, %.3fs",
             policy, stats["streams"], stats["raw_bytes"], stats["encoded_bytes"],
             stats["encode_seconds"])


def _write_optimized_pdf(doc, out_path, *, no_new_id=False):
    """One final container writer for explicit policies and every Best trial."""
    # All selected streams are explicitly encoded; never replace their codec.
    # Object/xref generation remains the writer's compatible optimization.
    doc.save(out_path, garbage=4, deflate=False, deflate_fonts=False,
             use_objstms=True, compression_effort=100, no_new_id=no_new_id)


@_fitz_locked
def gc_copy(in_path: str, out_path: str):
    """Passthrough: garbage-collect + deflate, no pixel changes (Original preset)."""
    doc = fitz.open(in_path)
    try:
        _save_optimized_pdf(doc, out_path)
    finally:
        doc.close()


@_fitz_locked
def recompress_file(in_path: str, out_path: str, dpi_cap: int = DEFAULT_DPI,
                    jpeg_q: int = DEFAULT_LOSSY_QUALITY,
                    token: CancelToken | None = None, progress=None,
                    codec: str = "jpeg", rate: float | None = None, colors: int = 64,
                    lossless: bool = False, *, allow_substitution: bool = True,
                    force_raster: bool = False, page_size: str = DEFAULT_PAGE_SIZE,
                    jpx_q: int | None = None):
    """Color: native full-color composition → final DPI → transform/encode.

    One opaque canvas per image-bearing page, with native text/vectors above.
    No individual image rewrite or source opacity masks in the output (§180).
    Raises CancelledError on ESC.
    """
    if page_size not in PAGE_SIZES:
        raise ValueError(f"Unknown page size: {page_size}")
    token = token or CancelToken()
    source = fitz.open(in_path)
    doc = fitz.open() if force_raster else fitz.open(in_path)
    from .native_layer import NativeContext
    native_context = NativeContext(doc)
    try:
        total = source.page_count
        for pno in range(total):
            if token.cancelled:
                raise CancelledError()
            def encode(rgb):
                return color_canvas_payload(rgb, codec, jpeg_q, rate, colors, lossless,
                                            allow_substitution=allow_substitution, token=token,
                                            jpx_q=jpx_q)
            if force_raster:
                # Same compose → one resize → transform/encode sequence as the
                # image layer, but include ALL original page painting (§224).
                rgb = flatten_rgb(source[pno], dpi_cap, token, force_to_dpi,
                                  directory=_ENCODE_WORKDIR.get(), minimum_dpi=dpi_cap)
                payload = encode(rgb)
                if token.cancelled:
                    raise CancelledError()
                rect = source[pno].rect
                target = PAGE_SIZES[page_size]
                page = doc.new_page(width=target[0] if target else rect.width,
                                    height=target[1] if target else rect.height)
                placement = _fit_rect(rect.width, rect.height, *target) if target else page.rect
                _place_color(doc, page, placement, payload)
            else:
                compose_color_page(doc, pno, dpi_cap, token, encode,
                                   _place_color, force_to_dpi, directory=_ENCODE_WORKDIR.get(),
                                   original=source, native_context=native_context)
            if progress:
                progress(pno + 1, total)
        _save_optimized_pdf(doc, out_path)
    finally:
        doc.close()
        if source is not doc:
            source.close()


def save_with_spec(in_path: str, out_path: str, spec: dict,
                   token: CancelToken | None = None, progress=None,
                   workdir: str | None = None):
    """The ONLY filter-to-PDF entry point (§§122/149); UI reads this file back.

    The same recipe includes every effective parameter, including palette
    count, JPEG/JPX quality (or explicit legacy JPX rate), lossless and page size.
    """
    policy = spec.get("stream_compression", "flate")
    if policy not in STREAM_LABELS:
        raise ValueError(f"Unknown PDF stream compression: {policy}")
    from .predictors import effective_prediction
    prediction = spec.get("png_prediction")
    if prediction is not None and prediction not in ("off", "on", "best"):
        raise ValueError(f"Unknown PNG prediction: {prediction}")
    context = _ENCODE_WORKDIR.set(workdir)
    stream_context = _STREAM_POLICY.set(policy)
    prediction_context = _PNG_PREDICTION.set(effective_prediction(spec))
    declaration_context = _BROTLI_DECLARATION.set(
        permits_brotli(policy) and bool(spec.get("brotli_declaration", False)))
    token_context = _SAVE_TOKEN.set(token)
    try:
        return _save_recipe(in_path, out_path, spec, token, progress)
    finally:
        _ENCODE_WORKDIR.reset(context)
        _STREAM_POLICY.reset(stream_context)
        _PNG_PREDICTION.reset(prediction_context)
        _BROTLI_DECLARATION.reset(declaration_context)
        _SAVE_TOKEN.reset(token_context)


def _save_recipe(in_path, out_path, spec, token, progress):
    token = token or CancelToken()
    if token.cancelled:
        raise CancelledError()
    mode = spec["mode"]
    if mode in BW_MODES:
        process_file(in_path, out_path, strategy=spec.get("strategy", "otsu"),
                     t=spec.get("t", 180), dpi=spec.get("dpi", DEFAULT_DPI),
                     token=token, progress=progress,
                     page_size=spec.get("page_size", DEFAULT_PAGE_SIZE),
                     force_raster=spec.get("force_raster", False),
                     codec="jbig2" if mode == "bw" else "flate")
    elif mode in COLOR_MODES:
        if mode == "color":
            checked_quality(spec.get("jpeg_q", DEFAULT_LOSSY_QUALITY))
        elif mode == "jpx":
            jpx_lossy_setting(spec)
        recompress_file(in_path, out_path, dpi_cap=spec.get("dpi_cap", DEFAULT_DPI),
                        jpeg_q=spec.get("jpeg_q", DEFAULT_LOSSY_QUALITY), token=token, progress=progress,
                        codec={"color": "jpeg", "jpx": "jpx", "indexed": "indexed",
                               "layered-jbig2": "layered-jbig2"}[mode],
                        rate=spec.get("rate") if mode == "jpx" else None,
                        jpx_q=spec.get("jpx_q") if mode == "jpx" else None,
                        colors=spec.get("colors", 5 if mode == "layered-jbig2" else 64),
                        lossless=spec.get("lossless", False), allow_substitution=False,
                        force_raster=spec.get("force_raster", False),
                        page_size=spec.get("page_size", DEFAULT_PAGE_SIZE))
    elif mode == "passthrough":
        gc_copy(in_path, out_path)
    else:
        raise ValueError(f"Unknown filter mode: {mode}")
    if token.cancelled:
        raise CancelledError()
