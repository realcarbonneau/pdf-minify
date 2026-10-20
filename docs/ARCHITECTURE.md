# Architecture & Tech Stack

## Rulings (verbatim)

Exact designer text from `DESIGNER_VERBATIM.md`. Text outside the fenced
quotes is not the designer's.

### Stack and layout

**§6** (undated)

```text
what if I am really picky about smooth clean custom UI highly tailored for a specific job, like pan, zoom in/out mouse scroll, next page, prev page, DnD, etc.
```

**§230** (2026-10-16)

```text
Also, rename this project to "PDF Minify", rename anything in the repo and I will rename the repo itself later.  Also, why is there a dir that restates pdf_minimalist, why not app, source, code, or something like that?
```

### Background jobs and the single path

**§37** (2026-10-09)

```text
don't freeze the whole app when doing the previews, do it in background.  the thumnail previews have to show the same viewport.  I want the app to do the full processing of each preset in the background without freezing the system, maybe set a max cores usually at 50% of the system if the processing is one core at a time (is it?) and then when panning, you are just showing a view on the rendered file.  Show a progress bar on each file that is processing.  Later, we will have an option to sort the filters and set a max auto filters, or no max.
```

**§51** (2026-10-10)

```text
WHen I open a new file, the right preview is the last to be updated, it should be always the first filter to be processed, ahead of all other priorities.  First open, it would be the first priority filter, but after, it would be whatever filter the user has selected, right?
```

**§43** (2026-10-10)

```text
the progress bar is supposed to be for EACH filter.
```

**§122** (2026-10-13)

```text
The preview need to show the saved file, DO NOT have multiple paths, this is the root cause of alot of your failures!! One single path, process the file, save temp, display temp file in preview, minis come from save temp files once they are processed. This is an important design ruling, please put this in the design under architecture and flow. Do you follow this flow? Do you understand why this is robust and safe?
```

## Stack (locked, designer rulings §§6–8)

Python with PyMuPDF, Pillow and numpy, and a PySide6 (Qt6) GUI built directly
in `pdf_minify/ui_qt/`; the Tkinter-first alternative is `DROPPED.md` D2.
Pipeline code in `core/` must never import Qt. Installation and the
local-versus-system split are in `DEPENDENCIES.md`.

- `PyMuPDF` (≥ 1.28.2, in `.venv`) — open, render, filter native content and
  save; the native PDF-filter bindings need this version.
- `Pillow` — JPEG and JPEG2000 encoding, image bridges.
- `numpy` — threshold and palette math.
- `jbig2` (system package) — JBIG2 BW and JBIG2 Color encoder; each stream is
  decoded and checked before embedding, and a failure is a clear error.

## Module layout (actual)

The repository root and import package are different concepts. `pdf_minify/`
is the application's Python namespace, not a duplicate checkout. Retain the
current **flat layout** for §230: `python -m pdf_minify` works from the root
without installing the project. A future `src/` layout would still contain
`src/pdf_minify/` and need packaging/editable-install changes; generic `app`
or `code` names offer no required benefit for this rename. See the
[PyPA layout guide](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/).

```
<checkout>/
  pdf_minify/
    core/             # headless, NO Qt imports
      cancel.py       # shared CancelToken (threading.Event + kill list)
      threshold.py    # simple / otsu / adaptive / sauvola, pure numpy
      pdf_io.py       # open, page count, gray render, save with gc
      display.py      # exact read-only native PDF display, no AA/interpolation
      canvas.py       # full-color composition, one final DPI resize
      image_layers.py # native backdrop / transformed canvas / native overlay
      backdrops.py    # source-order page/panel fill ownership (B116)
      native_layer.py # token edits preserving native Form/text state (B111)
      marked_content.py # orphaned whitespace ActualText repair, native parser
      defaults.py     # shared 300-DPI raster default
      filter_defaults.py # versioned saved-DPI/stream-default migrations
      pipeline.py     # the real saver: compose, transform, encode, final lossless pass
      algorithms.py   # editable six-codec image recipe choices, no preset lock
      stencils.py     # exact colored JBIG2 masks, shared by product/benchmark
      stream_compression.py # independent lossless native content/font encoders
      best_streams.py  # measured native/packed Zopfli/Brotli choice, J* untouched
      presets.py      # opinionated starting recipes, view modes, apply helpers
    ui_qt/            # Qt GUI only
      app.py          # DnD, pages, presets, main panes, save worker, ESC
      layout.py       # shared 4px token, PaneBlock headers/content, equal/stacked PreviewPair
      headers.py      # metadata elides on paint, never drives splitter widths
      icons.py        # one named-theme action provider, stock Breeze SVG fallback (§197)
      icon_lab.py     # reusable stock-family comparison, permanent codes, no Apply (§200)
      settings.py     # shared user settings, one-time legacy name migration (§230)
      assets/breeze/  # 16/22px light/dark icons with provenance and licenses
      assets/icon_lab/ # original PNG resource bank, hashes, provenance/notices/licenses
      viewer.py       # QGraphicsView: wheel=scroll, ctrl+wheel=zoom, drag-pan, peer-synced
    __main__.py       # CLI: [pdf] [--debug]
  tests/  (see TEST_PLAN.md)
  tools/              # check_env, make_demo, shot (all scratch → .tmp/)
  docs/               # all analysis + rulings docs
```

Display name **PDF Minify** and machine identifier `pdf-minify` are declared
once in the package root. The Qt entry point uses both; the main window and
startup last-file lookup share the settings factory. Project identity rules
are in `DESIGN.md` (§230).

## Background jobs (designer rulings §§37/43/44/47/48/51/89/90/95)

Heavy work runs in spawn-context worker PROCESSES (half-core cap), managed
by thin QThreads that only forward key-addressed results.
Process-once (§§44/122/149): on file open, queue every saved filter (selected
first, then strip order). Each immutable effective recipe owns one real saved
PDF, exact file size, and prepared page data used by both views. Existing work
is reused even on first selection; scroll, pan, zoom, page turns and strip
clicks only view/reframe that result. Live recipe changes debounce only the
edited filter; saved and live artifacts remain separate until an explicit
Save / Save As… / Discard decision.
See `FILTER_LIFECYCLE.md`, `UI_LAYOUT.md`, issues B74–B77, TODO §§150–152.

## Threading & ESC cancel design

- Artifact manager QThreads wait on process-pool futures; the GUI never waits
  synchronously for filtering or whole-document prepared-file readback.
  Keys address every completion. Native viewport painting (§§174/175) observes
  bounded exposed regions, caching display lists and device-scale tiles.
- All live recipe inputs share one trailing 300ms edit debounce (§183,
  proposed default). Retired results cannot overwrite a newer draft;
  completed/in-flight files are deleted only after all owners release them.
- PDF export is a cancellable chunked copy in a QThread. Escape/Cancel stops
  a running export only (§85); it is not Undo and does not discard filter edits.
- Closing resolves dirty state, writes per-job cancellation markers, cancels
  queued futures, and waits asynchronously for running work before deleting
  process-owned files. Pipeline cancellation is checked between pages/images/stages.
- The UI stays responsive. An external encoder that is already running may
  take a while to exit after cancellation; do not destroy its QThread or files
  meanwhile.

## Data flow — SINGLE PATH (designer rulings §§122/149, locked)

There is exactly ONE way a filter result comes into existence: no parallel
preview renderer, no mini renderer, no estimator. The flow:

```
input PDF + filter spec
  → run the REAL saver → <os-temp>/pdf-minify/saves/<GUI-PID>/<filter-UUID>/<artifact-key>/filtered.pdf
     (background, process-once; OS temp via Qt QStandardPaths — /tmp Linux,
     GetTempPath Windows, $TMPDIR macOS; designer §123, see
     docs/PERSISTENCE_AND_TEMP.md and ui_qt/paths.py)
  → preview  = observe THAT temp file at current device/zoom resolution, no AA
               (prepared 150dpi pages supply stable layout/mini data)
  → minis    = frame prepared pages from THAT temp file exactly (§48)
  → amount   = os.path.getsize(THAT temp file)
  → Save button = copy THAT temp file to the destination
baseline pane = the input file itself, rendered by the same page renderer
```

- View geometry (§§101/164/165): the baseline owns page dimensions, page
  count and available layout area. One column calculation caps capacity by
  real page count and uses the transformed scene-unit stride with no trailing
  gap. Prospective row height determines native scrollbar reservation, not
  the previous grid's scrollbar state. Original, preview and mini framing use
  this same occupied grid. Peer zoom copies the camera AND reflows geometry
  before copying scroll positions; scoped synchronization guards prevent
  intermediate scrollbar signals from propagating half a zoom. A geometry
  signature avoids repositioning all pages on ordinary pan. Qt AlignCenter
  owns centering; no artificial padding, translations or forced pan resets.
- Header sizing (§§124/166): header content is full filter/file metadata,
  not the current elided fragment. The widget ignores horizontal text size
  hints and paints the elision at its allocated width. Painting never mutates
  content/geometry. Filter/file state updates headers; the view-reframe timer
  does not.
- Region composition (§188): the central root owns one shared 4-logical-pixel
  outer inset and gutter; PaneBlock gives all three regions the same header/
  content layout; PreviewPair owns its equal/stacked preview
  layouts with zero nested margins. The panel form owns its single internal
  inset. The main splitter row and title-free full-width strip share edges;
  no default-margin wrapper chain, spacer compensation or metadata-driven
  geometry. STRIP_PADDING aliases the same token for mini/progress margins.
  Native frame/control interiors remain independent; see `UI_LAYOUT.md`.
- One saver: spec dict → PDF file (`pipeline.save_with_spec`, shared by the
  background temp saves and the Save button — same function, same bytes).
- One renderer: PDF pages → bitmaps (baseline, previews and minis differ
  only in source file and display scale, never in filter processing path).
  Filter processing happens once. Disk-backed prepared page buffers supply
  immediate layout/minis; bounded native viewport readback preserves native
  geometry as zoom increases (§§172–175). The renderer disables image
  decoder subsampling as well as interpolation and all PDF-content AA.
  It never thresholds display pixels or changes files. Native font/vector
  precision is not limited by the prepared 150dpi raster. UI chrome is
  unaffected; genuine encoded gray/color/opacity is retained.
- Filter UUIDs are persistent unique internal identities (§155); load repairs
  invalid/duplicate UUIDs, and Save As generates a fresh one. UUID-named
  directories own immutable input/recipe artifacts; copying a prepared result
  into a new filter does not call the real saver. Names/numbers stay out of
  recipe identity, and legacy slug aliases are only for settings compatibility.
- Strip sequence numbers are presentation state (§148), not saver or cached
  image data. Stable filter identities retain their results across reorders;
  the shared Qt item delegate draws the numbered name from the current model
  row. `rowsMoved` synchronizes the dropdown and persistence without processing
  or rebuilding content. See `UI_LAYOUT.md`, issue B73, and `TODO.md` §148.
- Reorder identity repair (§§156/157): model order is authoritative; the
  dropdown and processing sequence derive from it. Caption/content updates
  bind to stable UUID-bearing items, not mutable position arrays. One Qt
  `startDrag` override owns native drags and a UUID-only payload; one `moveRow`
  is the only drop mutation.
- Dirty selection transaction (§161): scoped QSignalBlocker suppresses a
  view's intermediate row notifications while Qt runs normal press/release/
  key handlers. One selectionSettled notification follows the complete input
  if state changed. The shared switch controller then resolves the draft;
  Cancel cannot be overwritten by a still-running native selection step.
  Programmatic row changes retain their normal final signal. Revert (§162)
  calls the same safe Discard operation without changing selection or filtering.
- Temp ownership keys include (filter UUID + file identity + FULL spec inputs): same key =
  same bytes, guaranteed; missing key = run the saver, never invent.
- The input file is never touched; a crashed worker leaves at most an
  orphan temp, never a corrupt document. Stale temps are swept, not trusted.

Why this is robust and safe: preview, minis and amounts are OBSERVATIONS of
the save output, so they cannot disagree with Save by construction — not by
test coverage. Container overhead, soft masks, font subsets: included
automatically, because they are measured, not modeled. There is no second
implementation that could diverge from the saved file.

### Effective BW recipes (§§127/149/168–171)

FFPR ON flattens each page to one 1-bit image; OFF keeps original text/vectors
and optimizes existing images to 1-bit. Overlapping imagery is composed into
ONE image canvas on white, with original native text and vector diagrams above
it and plain white page-backdrop rectangles below it (§§168–171). MuPDF filters original PDF operators,
not approximate glyph silhouettes. Exact native/image interleaving is not
required; FFPR provides the fully flattened appearance. `COMPRESSION.md`
describes this policy and lossless PDF/font compression. Both modes feed the same saved-file observation flow. Toggle affects
only the edited filter's draft, never unrelated results.

### Shared image-canvas preparation (§§180/182)

MuPDF filters original paint operators into native backdrops, one image
canvas and native foreground artwork. `core/canvas.py` composes unmodified
image samples/opacity at actual source image/mask density using the exact
native renderer. Bounded tiles fill an anonymous disk-backed RGBX buffer.
ONE global Lanczos resize sets final DPI before BW gray/threshold or color
palette/codec transforms; the scratch is artifact-owned and auto-unlinked.
No per-image RGB/mask rewrite, independent tiled resize or post-filter resize.
BW retains its white composition backdrop; color includes actual flat page
backdrops. Native text/vectors, page boxes, links and annotations remain;
native-only pages do not gain a canvas. FFPR deliberately renders the entire
page instead, for every codec, BW and colour (§224): compose the full
original page in RGB at least at the target DPI (higher if source bitmap
density requires it), perform one final resize, then the BW/palette/codec
transform. FFPR removes native painting even on image-free pages. Raster
filters default to 300 DPI (§225); `core/filter_defaults.py` moves older saved
recipes to 300 DPI once at settings load (`PERSISTENCE_AND_TEMP.md`). All modes
use `save_with_spec` and actual saved-file readback; there is no second GUI
filter pipeline.

The FFPR flag and page size are effective recipe inputs for colour too; the
single edit/debounce and artifact owner handle them. `core/backdrops.py` builds
one immutable `BackdropPlan` shared by canvas preparation and native-foreground
removal (B116); `core/native_layer.py` edits tokens while keeping original
operators and Form text state (B111); each file owns a `NativeContext` for
immutable Form inputs and equal-derivative reuse, and canvas preparation always
reads a separate immutable original. The composition rules themselves are in
`COMPRESSION.md` (Composition rules).

### Editable compression (§§203–205, 255–257, 260)

Compression is editable recipe state (§§203–205): the saved/draft mode, not
the seed preset, controls UI behaviour and dispatch, and it is persisted on
Save/Save As and for built-in overrides. `core/algorithms.py` lists the six
image choices; `core/stencils.py` builds
[JBIG2 Color](JBIG2.md#jbig2-color-one-stencil-per-palette-colour).
`core/stream_compression.py` encodes non-image native resources after font
subsetting and before the shared container save; its policy is an effective
cache input. Explicit codecs never silently substitute another encoder.

`core/best_streams.py` implements Best (§§255/256/260). After the same
once-only preparation and font subsetting, it encodes native and eligible
packed-image streams with Zopfli and Brotli, with PNG prediction off and on for
image rows, verifies exact readback, and keeps encoded alternatives in scratch
files. It compares the mixed, all-Zopfli and all-Brotli saves through the one
`pipeline._write_optimized_pdf` writer with stable PDF-ID framing, reopens each
candidate to verify decoded streams and protected J* bytes, then publishes the
smallest file atomically. Image samples and source conversion are unchanged.
The optional Brotli declaration is added only when the winning output uses
Brotli. `core/filter_defaults.py` holds the versioned migrations (300 DPI,
Best for app filters) applied before effective recipes are built. See
`COMPRESSION.md` and [NATIVE_STREAM_COMPRESSION.md](NATIVE_STREAM_COMPRESSION.md).

## Packaging

Packaging plans are in `PACKAGING.md`; the certified runtime is in
`PLATFORMS.md`.

## Design traps and failed attempts

- **Compute in threads.** numpy work inside QThreads, with Qt signals in play,
  aborted the process. Heavy work runs in spawn-context worker processes;
  threads only forward results.
- **Two implementations of one result.** Every past "preview wrong / amount
  wrong" failure came from a separate preview, mini or size path drifting from
  the saved file (§122). Everything observes the one saved PDF.
