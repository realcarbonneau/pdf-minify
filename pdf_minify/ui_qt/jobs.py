"""Shared spawn-process pool and pure view framing.

The GUI has no preview/mini transformation helpers or size estimators.
Real file processing and prepared page buffers live in artifacts.py (§149).
"""
import os

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import numpy as np
from PIL import Image as PILImage

PREVIEW_DPI = 150
_pool = None


def cpu_cap() -> int:
    """Max background worker processes: half the cores, at least 1."""
    return max(1, (os.cpu_count() or 2) // 2)


def pool():
    """Persistent spawn-context process pool (warmed on first dispatch).

    MUST be first created on the main thread (dispatch does this): spawning
    the pool's management threads/processes from a worker thread aborts.
    """
    global _pool
    if _pool is None:
        import multiprocessing as mp
        from concurrent.futures import ProcessPoolExecutor
        _pool = ProcessPoolExecutor(max_workers=cpu_cap(),
                                    mp_context=mp.get_context("spawn"))
    return _pool


def shutdown_pool():
    global _pool
    if _pool is not None:
        _pool.shutdown(wait=False, cancel_futures=True)
        _pool = None


import atexit as _atexit
_atexit.register(shutdown_pool)


def frame_view(pages, pw: int, ph: int, gap: int, cols: int,
               visible, out_w: int = 150) -> np.ndarray:
    """Composite exactly the visible scene rect from per-preset mini-pages.

    Pure function (§48): `pages` are prepared saved-file RGB arrays (small
    view derivatives, index-aligned); `pw/ph` are the base page dimensions;
    `visible` is (x, y, w, h) in scene coords. Returns an RGB thumbnail that
    frames precisely what the main windows show — grid, gaps and cut-off last
    page included. Missing pages stay white.
    """
    vx, vy, vw, vh = (float(v) for v in visible)
    if vw <= 0 or vh <= 0:
        return np.full((8, 8, 3), 255, dtype=np.uint8)
    scale = out_w / vw
    cw, ch = max(1, int(round(vw * scale))), max(1, int(round(vh * scale)))
    canvas = np.full((ch, cw, 3), 255, dtype=np.uint8)
    n = len(pages)
    rows = (n + cols - 1) // cols if cols > 0 else 1
    for idx, pg in enumerate(pages):
        if pg is None:
            continue
        r, c = divmod(idx, max(1, cols))
        ix, iy = c * (pw + gap), r * (ph + gap)
        ox = max(ix, vx)
        oy = max(iy, vy)
        ox2 = min(ix + pw, vx + vw)
        oy2 = min(iy + ph, vy + vh)
        if ox2 <= ox or oy2 <= oy:
            continue
        H, W = pg.shape[:2]
        sx, sy = (W / pw) if pw else 1.0, (H / ph) if ph else 1.0
        px, py = int((ox - ix) * sx), int((oy - iy) * sy)
        px2, py2 = int(np.ceil((ox2 - ix) * sx)), int(np.ceil((oy2 - iy) * sy))
        px, py = max(0, px), max(0, py)
        px2, py2 = min(W, max(px + 1, px2)), min(H, max(py + 1, py2))
        if px2 <= px or py2 <= py:
            continue
        piece = pg[py:py2, px:px2]
        dx, dy = int(round((ox - vx) * scale)), int(round((oy - vy) * scale))
        dx2, dy2 = int(round((ox2 - vx) * scale)), int(round((oy2 - vy) * scale))
        dx, dy = max(0, dx), max(0, dy)
        dx2, dy2 = min(cw, max(dx + 1, dx2)), min(ch, max(dy + 1, dy2))
        if dx2 <= dx or dy2 <= dy:
            continue
        thumb = PILImage.fromarray(piece).resize((dx2 - dx, dy2 - dy), PILImage.Resampling.NEAREST)
        canvas[dy:dy2, dx:dx2] = np.asarray(thumb)
    _ = rows  # layout rows implied by page count; kept for clarity
    return canvas
