"""Filter benchmark across corpus PDFs (designer §67).

Saves every preset for each sample file with preset-default settings and
records in/out bytes + seconds. Outputs .tmp/bench_filters.csv + table.
"""
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_minimalist.core import presets
from pdf_minimalist.core.cancel import CancelToken
from pdf_minimalist.core.pipeline import process_file, recompress_file, gc_copy

FILES = [
    "examples/deed-brevard.pdf",
    "examples/form-fw9.pdf",
    "examples/filled-background.pdf",
    "examples/images.pdf",
    "examples/paper-arxiv-1406.2661.pdf",
    "examples/scan-naca-formulas.pdf",
]


def run_one(src, pid, out):
    p = presets.get(pid)
    t0 = time.perf_counter()
    tok = CancelToken()
    if p["mode"] == "bw":
        prm = p["params"]
        process_file(src, out, strategy=prm["strategy"], t=prm["t"],
                     dpi=prm["dpi"], token=tok)
    elif p["mode"] == "color":
        prm = p["params"]
        recompress_file(src, out, dpi_cap=prm["dpi_cap"], jpeg_q=prm["jpeg_q"],
                        token=tok)
    elif p["mode"] == "jpx":
        prm = p["params"]
        recompress_file(src, out, dpi_cap=prm["dpi_cap"], token=tok,
                        codec="jpx", rate=prm.get("rate", 192))
    elif p["mode"] == "indexed":
        prm = p["params"]
        recompress_file(src, out, dpi_cap=prm["dpi_cap"], token=tok,
                        codec="indexed", colors=prm.get("colors", 64))
    else:
        gc_copy(src, out)
    return time.perf_counter() - t0


def main():
    os.makedirs(".tmp/bench", exist_ok=True)
    rows = []
    for src in FILES:
        if not os.path.exists(src):
            print(f"SKIP missing {src}", flush=True)
            continue
        size_in = os.path.getsize(src)
        base = os.path.splitext(os.path.basename(src))[0]
        for p in presets.PRESETS:
            out = f".tmp/bench/{base}.{p['id']}.pdf"
            try:
                secs = run_one(src, p["id"], out)
                size_out = os.path.getsize(out)
                rows.append((base, p["id"], size_in, size_out, secs))
                print(f"{base:28} {p['id']:12} {size_in:>9} -> {size_out:>9} "
                      f"({size_out / size_in * 100:5.1f}%) {secs:6.1f}s", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"{base:28} {p['id']:12} FAILED: {e}", flush=True)
    with open(".tmp/bench_filters.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "preset", "in_bytes", "out_bytes", "seconds"])
        w.writerows(rows)


if __name__ == "__main__":
    main()
