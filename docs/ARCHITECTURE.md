# Architecture & Tech Stack

## Decision (locked per designer rulings §6–§8, DROPPED D2): Python + PyMuPDF + Pillow + numpy, GUI = PySide6 (Qt6)

| Option | LXDE fit | Cross-platform | Preview speed | Verdict |
|---|---|---|---|---|
| PySide6 (Qt6) | good via apt or pip wheel | excellent DnD/HiDPI | best | **built — locked** |
| Tkinter (stdlib) + Pillow | excellent, zero extra GUI dep | good | OK but janky zoom | **superseded (D2)** — fails the designer's picky-UI standard |
| PyGObject GTK3 | most native on LXDE | painful on Win/Mac | good | rejected (portability) |
| Electron / Tauri | too heavy for old LXDE boxes | excellent | good | rejected |

Qt is built directly (`pdf_minimalist/ui_qt/`); there is no Tk code and no Tk-first
staging step. Pipeline code in `core/` must never import Qt.

## Dependencies (Debian 13)
```
sudo apt install python3-pymupdf python3-pil python3-numpy \
  python3-opencv  # optional, for Otsu/adaptive/Sauvola speed
  jbig2 poppler-utils  # optional: best BW encoder + pdfimages debug
pip install -r requirements.txt  # into local ./.venv (PySide6, pymupdf, Pillow, numpy)
```
- `PyMuPDF (fitz)` — open/render/replace images, `rewrite_images`, save with
  `garbage/deflate/use_objstms`. The local requirement is >=1.28.2 for the
  verified native filter bindings; Debian's older system build is not used.
- `Pillow` — JPEG encode, 1-bit PNG payloads, numpy↔QImage preview bridge.
- `numpy` — threshold math without OpenCV. OpenCV used only if present.
- `jbig2` (external system package) — the BW encoder: per-page streams via
  `jbig2 -p`, test-decoded before embedding, 1-bit PNG where undecodable.

## Module layout (actual)
```
pdf-minimalist/
  pdf_minimalist/
    core/             # headless, NO Qt imports
      cancel.py       # shared CancelToken (threading.Event + kill list)
      threshold.py    # simple / otsu / adaptive / sauvola, pure numpy
      pdf_io.py       # open, page count, gray render, save with gc
      display.py      # exact read-only native PDF display, no AA/interpolation
      canvas.py       # full-color composition, one final DPI resize
      image_layers.py # native backdrop / transformed canvas / native overlay
      native_layer.py # token edits preserving native Form/text state (B111)
      marked_content.py # orphaned whitespace ActualText repair, native parser
      defaults.py     # shared 300-DPI raster default
      filter_defaults.py # one-time saved-DPI settings migration policy
      pipeline.py     # BW full-page raster + color JPEG recompress + gc copy
      algorithms.py   # editable six-codec image recipe choices, no preset lock
      stencils.py     # exact colored JBIG2 masks, shared by product/benchmark
      stream_compression.py # independent lossless native content/font encoders
      presets.py      # opinionated starting recipes, view modes, apply helpers
    ui_qt/            # Qt GUI only
      app.py          # DnD, pages, presets, main panes, save worker, ESC
      layout.py       # shared 4px token, PaneBlock headers/content, equal/stacked PreviewPair
      headers.py      # metadata elides on paint, never drives splitter widths
      icons.py        # one named-theme action provider, stock Breeze SVG fallback (§197)
      icon_lab.py     # reusable stock-family comparison, permanent codes, no Apply (§200)
      assets/breeze/  # 16/22px light/dark icons with provenance and licenses
      assets/icon_lab/ # original PNG resource bank, hashes, provenance/notices/licenses
      viewer.py       # QGraphicsView: wheel=scroll, ctrl+wheel=zoom, drag-pan, peer-synced
    __main__.py       # CLI: [pdf] [--debug]
  tests/  (see TEST_PLAN.md)
  tools/              # check_env, make_demo, shot (all scratch → .tmp/)
  docs/               # all analysis + rulings docs
```

## Background jobs (designer rulings §§37/43/44/47/48/51/89/90/95)

Heavy work runs in spawn-context worker PROCESSES (half-core cap), managed
by thin QThreads that only forward key-addressed results — threads proved
fatal for compute (bare aborts inside numpy with Qt signals in play).
Process-once (§§44/122/149): on file open, queue every saved filter (selected
first, then strip order). Each immutable effective recipe owns one real saved
PDF, exact file size, and prepared page data used by both views. Existing work
is reused even on first selection; scroll, pan, zoom, page turns and strip
clicks only view/reframe that result. Live recipe changes debounce only the
edited filter; saved and live artifacts remain separate until an explicit
Save / Save As… / Discard decision. The old mini-slot/spec-slot architecture
and two-entry preview cache violated this rule and are superseded, not canon.
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
- Responsiveness remains required. An already running external encoder can
  take until its bounded subprocess timeout to exit; this repair does not claim
  sub-200ms encoder termination. Do not destroy its QThread or files meanwhile.

## Data flow — SINGLE PATH (designer rulings §§122/149, locked)

There is exactly ONE way a filter result comes into existence. No parallel
preview renderer, no mini renderer, no estimator — every past "preview
wrong / amount wrong" failure came from two implementations of the same idea
drifting apart. The flow:

```
input PDF + filter spec
  → run the REAL saver → <os-temp>/pdf-minimalist/saves/<GUI-PID>/<filter-UUID>/<artifact-key>/filtered.pdf
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
  does not. This breaks the former loop: elided setText → changing minimum
  widths → layout/splitter resize → delayed mini reframe → shorter setText.
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
  is the only drop mutation. The old parallel default/manual drag controllers
  could leave Qt's pressed state armed and delete a source row after moving.
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
automatically, because they are measured, not modeled. Any divergence that
used to be possible (thresholded preview vs vector-text save, estimated vs
embedded bytes) becomes structurally impossible: there is no second
implementation left to diverge.

Historical, superseded by §122 and §§171/180/182: the old per-mode sketches
below are retained only as history. Both observation flow AND image-layer
saver internals have changed; do not restore these per-image loops.
```
BW internals: PDF page → fitz.get_pixmap(dpi) → numpy gray (0-255)
  → threshold(strategy, T) → 1-bit PIL image
  → encode JBIG2 (test-decoded; 1-bit PNG where undecodable)
  → replace page with single image xref → save new PDF (garbage=4)
Color internals:
for each image xref: extract pix → downsample if > dpi_cap
  → re-encode (JPEG / JPEG2000 / palette-Flate) → replace only if smaller
→ save with gc + deflate
```

### Effective BW recipes (§§127/149/168–171)

FFPR ON flattens each page to one 1-bit image; OFF keeps original text/vectors
and optimizes existing images to 1-bit. §§168–171 require composition
of overlapping imagery, retaining native text AND vector diagrams, not the old
per-image mask waste. §171 simplifies the unshipped ordered-run prototype:
ONE image canvas on white, original native text/vectors above it, plain white
page-backdrop rectangles below it. MuPDF filters original PDF operators,
not approximate glyph silhouettes. Exact native/image interleaving is not
required; FFPR provides the fully flattened appearance. `COMPRESSION.md`
describes this policy and lossless PDF/font compression.
This is not the discarded mixed-layer
proposal. Both modes feed the same saved-file observation flow. Toggle affects
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
page instead. §224 extends this to every color codec as well as BW. Compose
the full original page in RGB at at least target DPI (and higher if source
bitmap density requires it), perform one final resize, then BW/palette/codec
transforms. FFPR removes native painting even on image-free pages. §225 sets
all built-in raster defaults and missing-DPI fallbacks to 300 DPI. §226 also
migrates every saved/custom raster recipe once at settings load, before saved
specs/artifacts are built. Persist the revision and migrated records; preserve
UUID/name/order/non-DPI settings and later deliberate DPI edits. All modes still use `save_with_spec` and actual
saved-file readback; no second GUI filter pipeline.

The FFPR flag/page size are effective recipe inputs for color too; the single
edit/debounce and artifact owner handle them without another processing path.
Shared composition explicitly initializes native filter flags (B110), repairs
only orphaned whitespace ActualText in derived native fragments (B109), and
places palette stencils directly rather than through nested clipped page
Forms (B108). Native foreground uses token-aware bitmap/backdrop removal,
preserving original operators and Form text-state inheritance (B111).
B112 keeps the original native page/first Form owners and their pruned
resources, so MCIDs, MCR `/Stm` and ParentTree still describe the actual native
overlay. New background/canvas content is prepended as an Artifact; no page-
Form graft strands accessibility references or retains original photographs.
Each file owns an explicit `NativeContext` for immutable Form inputs and
equal-derivative reuse. Canvas preparation always reads a separate immutable
original, including shared Forms on later pages. BW native mode keeps the
original catalog/structure too. Incompatible tagged derivatives fail clearly
instead of silently splitting their parent mapping. No final sanitize pass
rewrites native operators. See `COMPRESSION.md` for validation boundaries.

### Layered-color JBIG2 study (§§192–194)

§§203–205 subsequently make compression editable recipe state. The actual
saved/draft mode, not the seed preset mode, controls UI behavior and dispatch;
mode is persisted on Save/Save As and loaded even for built-in overrides.
`core/algorithms.py` describes six image choices; `core/stencils.py` owns the
promoted colored-mask implementation reused by production and the study.
`core/stream_compression.py` independently encodes non-image native resources
after font subsetting and before the shared container save. Its policy is an
effective cache input and uses the same dirty/edit/lifecycle controller.
Explicit codecs never silently substitute another encoder. See
`COMPRESSION.md` and [NATIVE_STREAM_COMPRESSION.md](NATIVE_STREAM_COMPRESSION.md).
The paragraph below describes the historical study boundary, not a prohibition
on this later separately requested integration.

[LAYERED_COLOR_JBIG2.md](LAYERED_COLOR_JBIG2.md) records the proposed colored
1-bit stencil representation and actual full-PDF benchmark/decoder evidence.
Prototype tooling reuses the existing RGB canvas, nearest-palette map, native
layer assembler and PDF optimizer; the experiment splits only the final
quantized bitmap canvas. No production codec, recipe identity, GUI control,
saved artifact lifecycle or default changes during the study. This is not
the parked rasterized-text mixed-mode design.

## Packaging
- v0.1: `python3 -m pdf_minimalist` from source + `requirements.txt`.
- Later: `.deb`, AppImage, `pipx`, Windows exe via PyInstaller (same `core/`).

## Issues on this page

B1, B3, B4, B6, B8, B11, B21, B24, B26, B33, B34, B35, B45, B46, B53 — see
`issues.md` (gated log); substance lives in the sections above.
