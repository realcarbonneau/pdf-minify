# pdf-minimalist — shrink PDFs with a camera-filter workbench

PDF optimizer and compressor: open a scan, research paper, manual, or
photo-heavy report, click through black-and-white threshold (Otsu, Simple,
Sauvola, adaptive), JPEG, JPEG2000, and palette-indexed filters, and watch
every filter's **real measured output size** update under its thumbnail.
What you see is what saving writes.

- **BW pipeline**: threshold → lossless JBIG2 (1-bit PNG where undecodable),
  300dpi default, original page size kept unless you pick Letter/A4.
- **Color pipeline**: best tool wins per image — baseline JPEG, JPEG2000, or
  lossless palette Flate for few-color graphics; vectors and text survive.
- **Honest UI**: original and preview panes stay synced (zoom, pan, scroll);
  scrolling never recomputes; ESC cancels anything; every size shown is
  measured encoder output, never a guess.
- **Local-first**: Qt6/PySide6 + PyMuPDF, everything Python-side in `./.venv`.

Keywords: pdf optimizer, pdf compressor, reduce pdf size, threshold
binarization, otsu sauvola, jbig2 encoder, jpeg2000 pdf, downsample images,
lossless palette flate, pyside6 gui, debian lxde.

## Run (all Python deps local in `./.venv`)

```bash
./setup_local.sh
./test.sh              # FULL suite (green before every ship)
./run.sh [file.pdf] [--debug]   # UI + stdout log, tee'd to .tmp/pdf-minimalist.log
# no file: reopens the last one. or:
source .venv/bin/activate
python -m pdf_minimalist [input.pdf] [--debug]
```

Scratch (demos, logs, screenshots) lives in gitignored `./.tmp/`:
`tools/make_demo.py` builds `.tmp/demo.pdf`, `tools/shot.py` captures
offscreen review shots into `.tmp/shot-*.png`,
`tools/bench_filters.py` benchmarks every filter across the corpus.

## Layout

```
pdf-minimalist/
  pdf_minimalist/     # all app source
    core/             # headless pipeline (no Qt imports)
    ui_qt/            # Qt GUI only
  tests/              # pytest suite (./test.sh)
  tools/              # env check, screenshots, benchmarks, corpus fetcher
  examples/           # committed PDF test corpus, see examples/README.md
  docs/               # design + dev guidelines + benchmark notes
  requirements*.txt   # pip pins (installed into .venv)
  .venv/              # virtualenv (created by setup_local.sh, git-ignored)
```

## System (apt, NOT in this dir)

See `docs/DEPENDENCIES.md` for the full local-vs-system table.
Minimum: `python3, python3-venv, jbig2, mupdf-tools, poppler-utils`.
Qt6 system libs already present on most Debian LXDE boxes; pip PySide6
bundles its own Qt inside `.venv` so it works even without them.

## Docs

- `docs/DESIGNER_VERBATIM.md` — every designer ruling, word for word.
- `docs/DESIGN.md` — behavior and preset catalog.
- `docs/DEVELOPER_GUIDELINES.md` — workflow (docs lead, full suite green).
- `docs/GITHUB.md` — copy-paste repo description, topics, keywords.
- `issues.md` — complaint log; items cross only on designer confirmation.
