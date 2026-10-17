# PDF Minify — shrink PDFs with a camera-filter workbench

PDF optimizer and compressor: open a scan, research paper, manual, or
photo-heavy report, click through black-and-white threshold (Otsu, Simple,
Sauvola, adaptive), JPEG, JPEG2000, and palette-indexed filters, and watch
every filter's **real measured output size** update under its thumbnail.
What you see is what saving writes.

- **BW pipeline**: threshold → selected lossless JBIG2 or 1-bit Flate,
  300dpi default, original page size kept unless you pick Letter/A4.
  FFPR off combines images into one BW canvas with native text/vector
  overlays; FFPR on flattens the entire page, preserving its stacked appearance.
- **Image processing**: compose original imagery/opacity in full color, resize
  once to final DPI, then threshold or reduce colors/compress. No post-filter
  resizing; native text/vectors survive unless FFPR is on. Full-page raster
  works with every image codec, including color. All built-in raster defaults
  are 300 DPI. Existing saved/custom raster filters migrate once to 300 DPI;
  later deliberate DPI choices are retained.
- **Image compression**: each filter can select JBIG2 BW, colored JBIG2 stencils,
  Flate BW, palette Flate Color, JPEG2000 or JPEG; no preset codec lock or
  silent codec substitution. Color uses one composed canvas with native artwork.
- **PDF stream compression**: independently choose Flate (default), compatible
  but slower Zopfli-Flate, or Brotli (requires a supporting PDF 2.0 reader).
  Native text/vector/font data stays lossless; image bytes are unaffected by
  this choice. [Integrated final-file size matrix](docs/INTEGRATED_COMPRESSION.md)
  and [reader limits](docs/NATIVE_STREAM_COMPRESSION.md#correctness-and-compatibility).
- **Honest UI**: original and preview panes stay synced (zoom, pan, scroll);
  view changes never reprocess filters; ESC cancels an active operation/dialog;
  both PDF panes display without added AA/smoothing, and native shapes gain
  precision on zoom. Every size shown is
  the exact full filtered PDF size, including fonts/masks/overhead, never a guess.
- **Saved/live filters**: edits debounce with a `*` marker; switching an
  unsaved filter offers Save, Save As…, Discard, or Cancel. Completed files
  supply preview, minis, sizes, and PDF export without reprocessing on selection.
- **Local-first**: Qt6/PySide6 + PyMuPDF, everything Python-side in `./.venv`.

Latest product ruling: encoding cost is not a selection criterion; use the
best validated encoding and retain alternatives for reader support or real
size outcomes. Zopfli adds no decoder requirement beyond Flate. The current
three-way native selector described above is awaiting alignment; see the
[updated compression policy](docs/COMPRESSION_COMBINATIONS.md#decoder-support-not-encoder-cost-213).

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
This project retains its flat layout. On first normal launch, existing saved
filters/settings migrate from the former app name without overwriting new
values; see [settings migration](docs/PERSISTENCE_AND_TEMP.md#application-name-migration-230).

## System (apt, NOT in this dir)

See `docs/DEPENDENCIES.md` for the full local-vs-system table.
Source runtime: Python/venv plus `requirements.txt`; `jbig2` supplies the
JBIG2 BW/Color modes. Optional `zopfli` is required only when explicitly
selecting native Zopfli-Flate; ordinary Flate needs no external encoder.
`mutool`/`pdfimages` are inspection/validation
tools, not GUI runtime requirements. PySide6 brings its own Qt libraries but
still needs compatible OS display/font libraries.

Certified current platform: **Debian 13 x86-64, LXDE/X11**, source/workspace
runtime (initial certificate 2026-10-14, updated verification 2026-10-16).
See [platform/version evidence](docs/PLATFORMS.md) and the
[multi-platform packaging guide](docs/PACKAGING.md). Windows/macOS/other
platforms and installers are not yet certified or built.

## Docs

- `docs/DESIGNER_VERBATIM.md` — substantive project rulings and confirmations, word for word.
- [docs/TODO.md](docs/TODO.md) — numbered project requirements and pending engineering work.
- `docs/DESIGN.md` — behavior and preset catalog.
- `docs/FILTER_LIFECYCLE.md` — single real-file flow, saved/live edits, and canon audit.
- [Integrated compression matrix](docs/INTEGRATED_COMPRESSION.md) — six complete PDFs, focused scenarios and isolated PNG/native-stream A/B tables; actual complete-file bytes only.
- [Controlled compression experiments](docs/COMPRESSION_EXPERIMENTS.md) — single-factor plans, fixed recipes, provenance and validation protocol.
- [Compression combinations and control-design review](docs/COMPRESSION_COMBINATIONS.md) — table first; current versus proposed capabilities, FFPR scope and separate-control recommendation.
- [Bitmap component controls](docs/IMAGE_STREAM_COMPRESSION.md#results) — supporting equal-pixel indexed/BW study with native compression fixed.
- `docs/NATIVE_STREAM_COMPRESSION.md` — supporting native-stream controls with image bytes fixed, plus reader limits.
- `docs/ICONS.md` — native-theme action icons, stock Breeze fallback and provenance.
- `docs/ICON_LAB.md` — View → Icon Lab…; compare stock libraries and copy permanent choice codes.
- `docs/DEVELOPER_GUIDELINES.md` — workflow (docs lead, full suite green).
- `docs/PLATFORMS.md` — dated certified runtime, evidence and explicit limits.
- `docs/PACKAGING.md` — Task Coach-inspired per-platform build/dependency plan.
- `docs/GITHUB.md` — copy-paste repo description, topics, keywords.
- `issues.md` — complaint log; items cross only on designer confirmation.
