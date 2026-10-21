"""Benchmark palette-reduction algorithms x PDF storage formats (§67).

Collects embedded images from representative corpus PDFs (+ synthetic flat
and photo images), then measures bytes for:
  algos: mediancut / fastoctree / pngquant  x dither off/on x colors 16/64/256
  formats: Flate-RGB, Flate-Indexed, JPEG q45, JPX r24, PNG-file
Prints a table + writes .tmp/bench_palette.csv.
"""
import io
import os
import shutil
import subprocess
import sys
import tempfile
import zlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymupdf as fitz
import numpy as np
from PIL import Image

SOURCES = [
    "examples/images.pdf",            # photo-heavy
    "examples/news-crater-lake-2026.pdf",  # mixed newspaper
    "examples/form-941-2026.pdf",     # flat form
    "examples/manual-maytag-dryer.pdf",    # diagrams
]
COLORS = (16, 64, 256)
PNGQUANT = shutil.which("pngquant")


def collect():
    imgs = []
    for src in SOURCES:
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
                    if len(imgs) >= 10:
                        break
                if len(imgs) >= 10:
                    break
        finally:
            doc.close()
    rng = np.random.default_rng(9)
    flat = np.full((500, 600, 3), 255, dtype=np.uint8)
    flat[50:250, 50:550] = (200, 30, 30)
    flat[280:450, 50:550] = (30, 60, 200)
    flat[100:200, 100:200] = (40, 180, 80)
    imgs.append(("synthetic-flat", Image.fromarray(flat)))
    photo = (rng.random((500, 600, 3)) * 255).astype(np.uint8)
    imgs.append(("synthetic-noise", Image.fromarray(photo)))
    return imgs


def cap(img, dpi_cap=150):
    w, h = img.size
    s = min(1.0, (dpi_cap * 11) / max(w, h))
    if s < 1.0:
        img = img.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)
    return img


def flate_rgb(arr):
    h = arr.shape[0]
    raw = b"".join(b"\x00" + np.ascontiguousarray(arr[y]).tobytes() for y in range(h))
    return zlib.compress(raw)


def quantize(img, colors, method, dither):
    m = {"mediancut": Image.MEDIANCUT, "fastoctree": Image.FASTOCTREE}[method]
    return img.quantize(colors=colors, method=m, dither=dither).convert("RGB")


def pngquant_bytes(img, colors):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img.save(f.name, "PNG")
        src = f.name
    try:
        r = subprocess.run([PNGQUANT, "--force", "--strip", "--speed", "1",
                            str(colors), "--output", "-", "--", src],
                           capture_output=True, timeout=120)
        if r.returncode != 0 or not r.stdout:
            return None
        return r.stdout
    except Exception:
        return None
    finally:
        os.unlink(src)


def main():
    imgs = collect()
    print(f"{len(imgs)} source images", flush=True)
    rows = []
    algos = [("mediancut", Image.NONE), ("mediancut", Image.FLOYDSTEINBERG),
             ("fastoctree", Image.NONE)]
    for name, im in imgs:
        im = cap(im)
        w, h = im.size
        arr = np.asarray(im)
        base = {}
        b = io.BytesIO()
        im.save(b, "JPEG", quality=45, optimize=True)
        base["jpeg-q45"] = len(b.getvalue())
        b = io.BytesIO()
        im.save(b, "JPEG2000", quality_mode="rates", quality_layers=[24])
        base["jpx-r24"] = len(b.getvalue())
        base["flate-rgb"] = len(flate_rgb(arr))
        for key, val in base.items():
            rows.append((name, f"{w}x{h}", "ref", key, val))
        for colors in COLORS:
            for method, dither in algos:
                q = np.asarray(quantize(im, colors, method, dither))
                rows.append((name, f"{w}x{h}",
                             f"{method}-{'dith' if dither else 'nodith'}-{colors}",
                             "flate-rgb", len(flate_rgb(q))))
                idx = np.asarray(im.quantize(colors=colors, method={
                    "mediancut": Image.MEDIANCUT,
                    "fastoctree": Image.FASTOCTREE}[method],
                    dither=dither))
                # true Indexed: 1 byte/px zlib + palette stream
                rows.append((name, f"{w}x{h}",
                             f"{method}-{'dith' if dither else 'nodith'}-{colors}",
                             "flate-indexed",
                             len(zlib.compress(idx.tobytes())) + 3 * colors))
            if PNGQUANT:
                pq = pngquant_bytes(im, colors)
                if pq is not None:
                    rows.append((name, f"{w}x{h}", f"pngquant-{colors}",
                                 "png-file", len(pq)))
    os.makedirs(".tmp", exist_ok=True)
    with open(".tmp/bench_palette.csv", "w") as f:
        f.write("image,size,algo,format,bytes\n")
        for r in rows:
            f.write(",".join(map(str, r)) + "\n")
    # summary: best algo/format per image at 64 colors + refs
    print(f"{'image':32} {'best-64':28} {'bytes':>8}  jpeg  jpx  flateRGB", flush=True)
    by_img = {}
    for r in rows:
        by_img.setdefault(r[0], []).append(r)
    for name, rr in by_img.items():
        refs = {x[3]: x[4] for x in rr if x[2] == "ref"}
        c64 = [x for x in rr if x[2].endswith("-64")]
        best = min(c64, key=lambda x: x[4]) if c64 else None
        print(f"{name:32} {best[2] + '/' + best[3] if best else '-':28} "
              f"{best[4] if best else 0:>8}  {refs.get('jpeg-q45', 0)} "
              f"{refs.get('jpx-r24', 0)} {refs.get('flate-rgb', 0)}", flush=True)


if __name__ == "__main__":
    main()
