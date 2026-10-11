"""Benchmark flat-palette storage formats (designer §80).

Compares, per image: RGB-Flate (current), true Indexed 1/2/4/8-bit Flate +
palette cost, zlib levels 6/9, and zopfli (if present). Prints table +
writes .tmp/bench_indexed.csv.
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile
import zlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fitz
import numpy as np
from PIL import Image

from pdf_minimalist.core.pipeline import indexed_rgb, flate_rgb_encode

ZOPFLI = shutil.which("zopfli")


def bpc_for(ncolors):
    if ncolors <= 2:
        return 1
    if ncolors <= 4:
        return 2
    if ncolors <= 16:
        return 4
    return 8


def pack_indices(idx, bpc):
    h, w = idx.shape
    if bpc == 8:
        return idx.astype(np.uint8).tobytes()
    scale = 8 // bpc
    out = bytearray()
    for y in range(h):
        bits = 0
        n = 0
        for x in range(w):
            bits = (bits << bpc) | int(idx[y, x])
            n += 1
            if n == scale:
                out.append(bits)
                bits = 0
                n = 0
        if n:
            out.append(bits << (8 - n * bpc))
    return bytes(out)


def zopfli_bytes(data):
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(data)
        src = f.name
    try:
        r = subprocess.run(["zopfli", "-c", src], capture_output=True, timeout=300)
        return bytes(r.stdout) if r.returncode == 0 and r.stdout else None
    except Exception:
        return None
    finally:
        os.unlink(src)


def collect():
    imgs = []
    for src in ["examples/manual-maytag-dryer.pdf", "examples/form-941-2026.pdf",
                "examples/news-crater-lake-2026.pdf"]:
        if not os.path.exists(src):
            continue
        doc = fitz.open(src)
        try:
            seen = set()
            for pno in range(doc.page_count):
                for e in doc[pno].get_images(full=True):
                    if e[0] in seen:
                        continue
                    seen.add(e[0])
                    try:
                        info = doc.extract_image(e[0])
                    except Exception:
                        continue
                    if info.get("bpc") == 1 or max(info["width"], info["height"]) < 300:
                        continue
                    try:
                        im = Image.open(io.BytesIO(info["image"])).convert("RGB")
                    except Exception:
                        continue
                    imgs.append((f"{os.path.basename(src)}#{e[0]}", im))
                    if len(imgs) >= 6:
                        break
                if len(imgs) >= 6:
                    break
        finally:
            doc.close()
    flat = np.full((500, 600, 3), 255, dtype=np.uint8)
    flat[50:250, 50:550] = (200, 30, 30)
    flat[280:450, 50:550] = (30, 60, 200)
    flat[100:200, 100:200] = (40, 180, 80)
    imgs.append(("synthetic-flat", Image.fromarray(flat)))
    return imgs


def main():
    imgs = collect()
    print(f"{len(imgs)} images, zopfli={'yes' if ZOPFLI else 'no'}", flush=True)
    rows = []
    for name, im in imgs:
        w, h = im.size
        s = min(1.0, 1650 / max(w, h))
        if s < 1.0:
            im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
        arr = np.asarray(im)
        rgbflate = flate_rgb_encode(arr)
        rows.append((name, "rgb-flate/z6", len(rgbflate)))
        print(f"{name}: rgb-flate/z6 {len(rgbflate)}", flush=True)
        for colors in (256, 64, 16):
            q = np.asarray(im.quantize(colors=colors, method=Image.FASTOCTREE,
                                       dither=Image.NONE))
            # count actual used entries
            used = np.unique(q)
            n = len(used)
            bpc = bpc_for(n)
            packed = pack_indices(q, bpc)
            pal = 3 * n
            for label, comp in (("z6", lambda d: zlib.compress(d, 6)),
                                ("z9", lambda d: zlib.compress(d, 9))):
                rows.append((name, f"indexed-{colors}/{bpc}bpc/{label}",
                             len(comp(packed)) + pal))
            if ZOPFLI:
                z = zopfli_bytes(packed)
                if z is not None:
                    rows.append((name, f"indexed-{colors}/{bpc}bpc/zopfli",
                                 len(z) + pal))
        # indexed_rgb agreement (what the app embeds today)
        app = indexed_rgb(arr, 64)
        rows.append((name, "app-indexed64-rgbflate", len(flate_rgb_encode(app))))
    os.makedirs(".tmp", exist_ok=True)
    with open(".tmp/bench_indexed.csv", "w") as f:
        f.write("image,variant,bytes\n")
        for r in rows:
            f.write(",".join(map(str, r)) + "\n")
    by_img = {}
    for r in rows:
        by_img.setdefault(r[0], []).append(r)
    for name, rr in by_img.items():
        best = min(rr, key=lambda x: x[2])
        print(f"{name:36} best={best[1]:28} {best[2]}", flush=True)


if __name__ == "__main__":
    main()
