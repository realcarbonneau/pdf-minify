#!/usr/bin/env python3
"""Make PDF Minify's application icon from the designer's sheet (§294).

    python3 tools/app_icon.py

Takes column 5, row 4 of icons/test2.png, removes its light tile so the
background is transparent, keeps a soft shadow under the page, crops to the
design and writes pdf_minify/ui_qt/assets/app_icon/pdf-minify-<size>.png and
packaging/windows/pdf-minify.ico. The Linux and macOS packages are made from
those PNGs (debian/rules, build-macos.yml).

The sheet has no transparency, and the page is nearly as light as the tile,
so the tile is found by its connection to the edge of the cell: a pixel is
background when it is reached from there through pale pixels, each within a
few levels of the last (the tile's shading changes slowly; the outlines
change sharply). Pixels within a few pixels of the background are then
unmixed from the tile's colour, so edges stay smooth on any background.
"""
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SHEET = ROOT / "icons" / "test2.png"
CELL = (1001, 738, 1243, 974)          # column 5, row 4
OUT = ROOT / "pdf_minify" / "ui_qt" / "assets" / "app_icon"
ICO = ROOT / "packaging" / "windows" / "pdf-minify.ico"
SIZES = (16, 24, 32, 48, 64, 128, 256)
STEP = 9           # largest colour change between neighbouring background pixels
DEPTH = 4          # edge blends and the shadow strip lie within 4 px of the background
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = tuple((dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy, dx) != (0, 0))


def parts(mask):
    """8-connected groups of True pixels."""
    h, w = mask.shape
    seen = ~mask
    for sy, sx in zip(*np.nonzero(mask)):
        if seen[sy, sx]:
            continue
        part, queue = [], deque([(sy, sx)])
        seen[sy, sx] = True
        while queue:
            y, x = queue.popleft()
            part.append((y, x))
            for dy, dx in N8:
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and not seen[ny, nx]:
                    seen[ny, nx] = True
                    queue.append((ny, nx))
        yield part


def neighbours(mask):
    """How many of each pixel's 8 neighbours are True (outside counts as `False`)."""
    h, w = mask.shape
    pad = np.pad(mask, 1, constant_values=False)
    return sum(pad[1 + dy:1 + dy + h, 1 + dx:1 + dx + w].astype(int) for dy, dx in N8)


def background(tile, lum):
    """The tile: pale pixels reached from the cell's edge in small colour steps."""
    h, w, _ = tile.shape
    chroma = tile.max(axis=2) - tile.min(axis=2)
    pale = (lum >= 150) & (chroma <= 80)
    bg = np.zeros((h, w), bool)
    queue = deque((y, x) for y in range(h) for x in range(w)
                  if (y in (0, h - 1) or x in (0, w - 1)) and pale[y, x])
    for y, x in queue:
        bg[y, x] = True
    while queue:
        y, x = queue.popleft()
        for dy, dx in N4:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not bg[ny, nx] and pale[ny, nx] \
                    and np.abs(tile[ny, nx] - tile[y, x]).max() <= STEP:
                bg[ny, nx] = True
                queue.append((ny, nx))
    # Specks of the sheet at the cell's corners, apart from the design.
    for part in parts(~bg):
        if len(part) < 150:
            for y, x in part:
                bg[y, x] = True
    return bg


def tile_colour(tile, lum, bg):
    """The tile's colour without the design's shadow: a smooth fit to its bright pixels."""
    h, w, _ = tile.shape
    yy, xx = np.mgrid[0:h, 0:w] / max(h, w)
    terms = np.stack([np.ones_like(xx), xx, yy, xx * xx, xx * yy, yy * yy], axis=-1)
    bright = bg & (lum >= 225)
    coef, *_ = np.linalg.lstsq(terms[bright], tile[bright], rcond=None)
    return np.clip(terms @ coef, 0, 255)


def darken_alpha(colour, behind):
    """How opaque a darker colour must be, over `behind`, to show as `colour`."""
    darker = np.where(colour < behind, (behind - colour) / np.maximum(behind, 1), 0)
    return float(np.clip(darker.max(), 0, 1))


def transparent(tile):
    """RGBA of the cell with its tile removed."""
    h, w, _ = tile.shape
    lum = 0.299 * tile[..., 0] + 0.587 * tile[..., 1] + 0.114 * tile[..., 2]
    bg = background(tile, lum)
    behind = tile_colour(tile, lum, bg)

    def near_outline(y, x):
        y0, y1, x0, x1 = max(0, y - 2), min(h, y + 3), max(0, x - 2), min(w, x + 3)
        return bool(((lum[y0:y1, x0:x1] < 140) & ~bg[y0:y1, x0:x1]).any())

    # From the background toward each outline: through the pixels touching it,
    # then inward while pixels get darker, at most DEPTH px. A light pixel
    # touching the background away from any dark outline is the page's own
    # edge: it stays, and the pass does not go through it.
    peeled = np.zeros((h, w), bool)
    page_edge = np.zeros((h, w), bool)
    queue = deque()
    for y, x in zip(*np.nonzero(~bg)):
        if any(0 <= y + dy < h and 0 <= x + dx < w and bg[y + dy, x + dx] for dy, dx in N4):
            if darken_alpha(tile[y, x], behind[y, x]) < 0.05 and not near_outline(y, x):
                page_edge[y, x] = True
            else:
                peeled[y, x] = True
                queue.append((y, x, 1))
    while queue:
        y, x, depth = queue.popleft()
        if depth == DEPTH:
            continue
        for dy, dx in N4:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not (bg[ny, nx] or peeled[ny, nx] or page_edge[ny, nx]) \
                    and lum[ny, nx] <= lum[y, x]:
                peeled[ny, nx] = True
                queue.append((ny, nx, depth + 1))

    alpha = np.where(bg, 0.0, 1.0)
    rgb = tile.copy()
    for y, x in zip(*np.nonzero(peeled | bg)):
        a = darken_alpha(tile[y, x], behind[y, x])
        if peeled[y, x] and a >= 0.85:      # the outline itself
            a = 1.0
        if bg[y, x] and a < 0.12:           # the tile's own shading
            a = 0.0
        alpha[y, x] = a
        if a > 0:
            rgb[y, x] = np.clip((tile[y, x] - behind[y, x]) / a + behind[y, x], 0, 255)

    # Stray light specks: opaque pixels with at least 6 of 8 neighbours see-through.
    clear = 8 - neighbours(alpha >= 0.5)
    alpha[(alpha >= 0.5) & (clear >= 6) & (lum >= 140)] = 0.0
    # Of the tile, only the shadow next to the design stays.
    near = ~bg
    for _ in range(8):
        grown = near.copy()
        grown[1:] |= near[:-1]
        grown[:-1] |= near[1:]
        grown[:, 1:] |= near[:, :-1]
        grown[:, :-1] |= near[:, 1:]
        near = grown
    alpha[bg & ~near] = 0.0
    # Faint pixels with nothing visible around them, then tiny detached groups.
    alpha[(alpha < 0.5) & (neighbours(alpha >= 0.1) == 0)] = 0.0
    for part in parts(alpha * 255 >= 1):
        if len(part) < 10:
            for y, x in part:
                alpha[y, x] = 0.0
    return np.dstack([rgb, alpha * 255]).round().astype(np.uint8)


def main():
    tile = np.asarray(Image.open(SHEET).convert("RGB").crop(CELL)).astype(float)
    rgba = transparent(tile)
    image = Image.fromarray(rgba, "RGBA")
    # Crop to what is clearly visible, then centre it in a square with a small margin.
    design = image.crop(Image.fromarray(rgba[..., 3]).point(lambda a: 255 if a >= 40 else 0).getbbox())
    side = round(max(design.size) * 1.04)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.paste(design, ((side - design.width) // 2, (side - design.height) // 2))
    # Scale in premultiplied alpha, so see-through pixels' colours do not bleed in.
    icons = [square.convert("RGBa").resize((s, s), Image.LANCZOS).convert("RGBA") for s in SIZES]
    for size, icon in zip(SIZES, icons):
        icon.save(OUT / f"pdf-minify-{size}.png", optimize=True)
    icons[-1].save(ICO, format="ICO", sizes=[(s, s) for s in SIZES], append_images=icons[:-1])
    print(f"{side} px design square -> {', '.join(map(str, SIZES))} px and {ICO.name}")


if __name__ == "__main__":
    main()
