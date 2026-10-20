# PDF Minify — shrink PDFs with a camera-filter workbench

PDF optimizer and compressor: open a scan, research paper, manual, or
photo-heavy report, click through black-and-white threshold (Otsu, Simple,
Sauvola, adaptive), JPEG, JPEG2000, and palette-indexed filters, and watch
every filter's **real measured output size** update under its thumbnail.
What you see is what saving writes.

- **BW pipeline**: threshold → selected lossless JBIG2 or packed 1-bit samples,
  300dpi default, original page size kept unless you pick Letter/A4.
  FFPR off combines images into one BW canvas with native text/vector
  overlays; FFPR on flattens the entire page, preserving its stacked appearance.
- **Image processing**: compose original imagery/opacity in full color, resize
  once to final DPI, then threshold or reduce colors/compress. No post-filter
  resizing; native text/vectors survive unless FFPR is on. Full-page raster
  works with every image codec, including color. Raster filters default to
  300 DPI.
- **Image compression**: each filter can select JBIG2 BW, colored JBIG2 stencils,
  Packed BW, Indexed color, JPEG2000 or JPEG; no preset codec lock or
  silent codec substitution. Color uses one composed canvas with native artwork.
- **PDF stream compression**: every app filter uses **Best (Zopfli/Brotli)**,
  which compares actual complete saved candidates for native text/vector/font
  streams AND packed BW/indexed images, keeping exact samples and leaving
  JPEG/JPEG2000/JBIG2 payloads untouched. It may require a Brotli-capable PDF
  reader. Explicit Flate, Zopfli and Brotli choices compress native streams
  only. [Measured sizes](docs/COMPRESSION_BENCHMARKS.md) and
  [reader limits](docs/NATIVE_STREAM_COMPRESSION.md#correctness-and-compatibility).
- **Honest UI**: original and preview panes stay synced (zoom, pan, scroll);
  view changes never reprocess filters; ESC cancels an active operation/dialog;
  both PDF panes display without added AA/smoothing, and native shapes gain
  precision on zoom. Every size shown is
  the exact full filtered PDF size, including fonts/masks/overhead, never a guess.
- **Saved/live filters**: edits debounce with a `*` marker; switching an
  unsaved filter offers Save, Save As…, Discard, or Cancel. Completed files
  supply preview, minis, sizes, and PDF export without reprocessing on selection.
- **Local-first**: Qt6/PySide6 + PyMuPDF, everything Python-side in `./.venv`.

Encoding cost is not a selection criterion: the app uses the best validated
encoder and keeps alternatives only for reader support or real size outcomes.
Zopfli adds no decoder requirement beyond Flate. See the
[encoder policy](docs/COMPRESSION.md#encoder-policy-213).

Keywords: pdf optimizer, pdf compressor, reduce pdf size, threshold
binarization, otsu sauvola, jbig2 encoder, jpeg2000 pdf, downsample images,
lossless palette flate, pyside6 gui, debian lxde.

## Run (all Python deps local in `./.venv`)

```bash
./setup_local.sh
./test.sh              # FULL suite after code-affecting changes, not docs-only edits
./run.sh [file.pdf] [--debug]   # UI + stdout log in the OS temp directory
xvfb-run -a ./.venv/bin/python tools/drag_smoke.py  # native DnD smoke (xdotool)
QT_QPA_PLATFORM=offscreen ./.venv/bin/python tools/filter_smoke.py  # filter flow smoke
# no file: reopens the last one. or:
source .venv/bin/activate
python -m pdf_minify [input.pdf] [--debug]
```

App logs live in `${TMPDIR:-/tmp}/pdf-minify/pdf-minify.log`.
Runtime filtered PDFs and encoder scratch live under
`${TMPDIR:-/tmp}/pdf-minify/saves/<GUI-PID>/<filter-UUID>/<artifact-key>/`;
each process holds a lock so cleanup cannot delete another running app's work.
Its generated files and empty PID directory are removed on normal exit.
Development artifacts (demos and screenshots) live in gitignored `./.tmp/`:
`tools/make_demo.py` builds `.tmp/demo.pdf`, `tools/shot.py` captures
offscreen review shots into `.tmp/shot-*.png`, `tools/drag_smoke.py` captures
native drags into `.tmp/drag-*.png`,
`tools/bench_filters.py` benchmarks every filter across the corpus.

## Layout

```
<checkout>/
  pdf_minify/         # importable Python package; all app source
    core/             # headless pipeline (no Qt imports)
    ui_qt/            # Qt GUI only
  tests/              # pytest suite (./test.sh)
  tools/              # env check, screenshots, benchmarks, corpus fetcher
  examples/           # committed PDF test corpus, see examples/README.md
  docs/               # design + dev guidelines + benchmark notes
  requirements*.txt   # pip pins (installed into .venv)
  .venv/              # virtualenv (created by setup_local.sh, git-ignored)
```

The checkout directory is independent of Python's `pdf_minify` package name.
The package gives imports and `python -m pdf_minify` a specific namespace;
`src/` would be an additional container, not a replacement package name.
This project retains its flat layout. Settings saved under the former app
name are imported once, without overwriting newer values; see
[settings migration](docs/PERSISTENCE_AND_TEMP.md#application-name-migration-230).

## System (apt, NOT in this dir)

See `docs/DEPENDENCIES.md` for the full local-vs-system table.
Source runtime: Python/venv plus `requirements.txt`; `jbig2` supplies the
JBIG2 BW/Color modes. The default **Best** policy requires system `zopfli` and
the bundled MuPDF Brotli encoder/decoder; missing encoders produce an error,
not a silent fallback. Explicit ordinary Flate needs no external encoder.
`mutool`/`pdfimages` are inspection/validation
tools, not GUI runtime requirements. PySide6 brings its own Qt libraries but
still needs compatible OS display/font libraries.

Certified current platform: **Debian 13 x86-64, LXDE/X11**, source/workspace
runtime (certificate 2026-10-14).
See the [certificate and its limits](docs/PLATFORMS.md) and the
[multi-platform packaging guide](docs/PACKAGING.md). Windows/macOS/other
platforms and installers are not yet certified or built.

## Docs

[docs/00_OVERVIEW.md](docs/00_OVERVIEW.md) maps every page. The main ones:

- `docs/DESIGN.md` — top-level design principles, behavior and presets.
- `docs/COMPRESSION.md` — how pages are prepared and encoded.
- [docs/COMPRESSION_BENCHMARKS.md](docs/COMPRESSION_BENCHMARKS.md) — measured complete-PDF sizes and single-factor experiments.
- `docs/LOSSY_IMAGE_QUALITY.md` — the JPEG/JPEG2000 Quality control and its calibration.
- `docs/NATIVE_STREAM_COMPRESSION.md` — Best, Zopfli and Brotli, and reader limits.
- `docs/FILTER_LIFECYCLE.md` — single real-file flow and saved/live edits.
- `docs/DEVELOPER_GUIDELINES.md` — workflow and product rules.
- `docs/PLATFORMS.md` — certified runtime and its limits.
- `docs/DESIGNER_VERBATIM.md` — the designer's rulings, word for word.
- [docs/TODO.md](docs/TODO.md) — numbered project requirements and pending work.
- `issues.md` — complaint log; items cross only on designer confirmation.
