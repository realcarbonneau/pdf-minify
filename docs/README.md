# Developer documentation

For working on PDF Minify: running it from source, testing, and what each
document here covers. To install PDF Minify, see the [README](../README.md).

## Rulings (verbatim)

Exact designer text from `DESIGNER_VERBATIM.md`. Text outside the fenced
quotes is not the designer's.

**§296** (2026-10-20)

```text
And the readme has irrelevant technical details, like debounce, local run, etc.  I want something like taskcoach, we will have the install packages/platforms, and a ref to the docs index, which should be a readme in the docs dir, right?
```

## Running from source

On Debian 13, the certified platform ([PLATFORMS.md](PLATFORMS.md)):

```bash
sudo apt install python3-venv jbig2 zopfli mupdf-tools poppler-utils
./setup_local.sh                  # creates .venv and installs requirements.txt
./run.sh [file.pdf] [--debug]     # starts the app; without a file it reopens the last one
./test.sh                         # the full suite, after code changes (§241)
```

`python -m pdf_minify [input.pdf] [--debug]` also works inside the activated
`.venv`. Python packages stay in `.venv`; the local-versus-system split is in
[DEPENDENCIES.md](DEPENDENCIES.md).

Checks and review tools (outputs go to the gitignored `.tmp/`):

```bash
xvfb-run -a ./.venv/bin/python tools/drag_smoke.py                   # native drag-and-drop (needs xdotool)
QT_QPA_PLATFORM=offscreen ./.venv/bin/python tools/filter_smoke.py   # filter edit and save flow
./.venv/bin/python tools/shot.py [file.pdf]                          # offscreen screenshots
./.venv/bin/python tools/make_demo.py                                # demo PDF
./.venv/bin/python tools/bench_filters.py                            # every filter across the corpus
```

The app log is `${TMPDIR:-/tmp}/pdf-minify/pdf-minify.log`. Filtered PDFs and
encoder scratch live under `${TMPDIR:-/tmp}/pdf-minify/saves/<GUI-PID>/…`,
locked per process and removed on normal exit
([PERSISTENCE_AND_TEMP.md](PERSISTENCE_AND_TEMP.md)).

Building and testing the packages ([PACKAGING.md](PACKAGING.md)):

```bash
scripts/build-deb.sh deps && scripts/build-deb.sh build   # .deb for this Debian or Ubuntu release
scripts/test-deb.sh debian:trixie                          # install it in a clean container, run the suite
```

The Windows installer and the macOS apps are built and tested by
`.github/workflows/build-windows.yml` and `build-macos.yml`.

## Repository layout

```
<checkout>/
  pdf_minify/         # importable Python package; all app source
    core/             # headless pipeline (no Qt imports)
    ui_qt/            # Qt GUI only
  tests/              # pytest suite (./test.sh)
  tools/              # environment check, screenshots, benchmarks, corpus fetcher, release notes, app icon
  examples/           # committed PDF test corpus (examples/README.md)
  docs/               # this documentation
  icons/              # icon artwork sources
  debian/             # Debian and Ubuntu packaging; debian/bundled/ per release
  packaging/          # launchers, desktop entry, icons and installer scripts
  scripts/            # package build and test scripts
  .github/workflows/  # package builds and release notes (Task Coach's pattern)
  CHANGELOG.md        # release notes, one section per version
  requirements*.txt   # pip requirements (installed into .venv)
```

The layout is flat: `pdf_minify/` is the import package, not another checkout
([ARCHITECTURE.md](ARCHITECTURE.md)).

## How the app works

PDF Minify makes PDFs smaller. Open a PDF, compare filters side by side and
save the one you want. Every filter produces a real saved PDF in the
background; the preview, the strip minis and Export all read that file, and
the size shown is its exact byte count. Selecting a filter or changing the
view never reprocesses. Filter edits debounce, show `*`, and offer Save,
Save As…, Discard or Cancel when you leave the filter (§149).

The top-level design principles, word for word, open [DESIGN.md](DESIGN.md).

### Key facts

- **Image compression** is chosen per filter: JBIG2 BW, colored JBIG2, Packed
  BW, Indexed color, JPEG2000 or JPEG. The selected codec is never replaced
  by another one (§203).
- **Page model**: FFPR off keeps native text and vectors over one composed
  image canvas; FFPR on flattens the whole page into one image (§§127/171).
  Images are composed in full colour, resized once to the target DPI
  (default 300) and then transformed (§§180/225).
- **PDF streams**: every app filter uses Best (Zopfli/Brotli) (§257). Brotli
  output needs a reader that supports it.
- **Quality**: one 0–100 control, default 75, for JPEG and JPEG2000
  (§§272/284). The app never chooses between the two (§287).
- **Display**: the actual saved PDFs are drawn at device and zoom resolution,
  without anti-aliasing or interpolation (§§172–175).
- **Icons** follow the desktop theme with a bundled Breeze fallback (§197);
  View → Icon Lab… compares icon sets (§200).

## Documents

| Topic | Page |
|---|---|
| Design principles, behaviour, presets | [DESIGN.md](DESIGN.md) |
| Window layout, strip and controls | [UI_LAYOUT.md](UI_LAYOUT.md) |
| Processing flow and background jobs | [ARCHITECTURE.md](ARCHITECTURE.md), [FILTER_LIFECYCLE.md](FILTER_LIFECYCLE.md) |
| Compression design | [COMPRESSION.md](COMPRESSION.md) |
| Measured complete-PDF sizes | [COMPRESSION_BENCHMARKS.md](COMPRESSION_BENCHMARKS.md) |
| JPEG and JPEG2000 quality | [LOSSY_IMAGE_QUALITY.md](LOSSY_IMAGE_QUALITY.md) |
| PDF stream compression and reader limits | [NATIVE_STREAM_COMPRESSION.md](NATIVE_STREAM_COMPRESSION.md) |
| JBIG2 BW and Color | [JBIG2.md](JBIG2.md) |
| Proposal, not implemented | [MIXED_MODE_OPTION.md](MIXED_MODE_OPTION.md) |
| Icons and tooltips | [ICONS.md](ICONS.md), [ICON_LAB.md](ICON_LAB.md), [TOOLTIPS.md](TOOLTIPS.md) |
| Settings and temporary files | [PERSISTENCE_AND_TEMP.md](PERSISTENCE_AND_TEMP.md) |
| Certified platform, packaging, dependencies | [PLATFORMS.md](PLATFORMS.md), [PACKAGING.md](PACKAGING.md), [DEPENDENCIES.md](DEPENDENCIES.md) |
| What changed in each release | [CHANGELOG.md](../CHANGELOG.md) |
| Developer rules and tests | [DEVELOPER_GUIDELINES.md](DEVELOPER_GUIDELINES.md), [TEST_PLAN.md](TEST_PLAN.md) |
| Designer rulings, word for word | [DESIGNER_VERBATIM.md](DESIGNER_VERBATIM.md) |
| Requirements, defects, dropped ideas | [TODO.md](TODO.md), [issues.md](../issues.md), [DROPPED.md](DROPPED.md) |
