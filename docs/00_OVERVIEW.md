# pdf-minimalist — Overview & Opinionated Defaults

Current canon is in `DESIGN.md`, `UI_LAYOUT.md`, `ARCHITECTURE.md`,
`FILTER_LIFECYCLE.md`, and `COMPRESSION.md`. All filters produce real saved
PDFs in the background; previews/minis read those files, sizes are their exact
whole-file byte counts, and export copies them. Selection and view changes do
not process again. Live filter edits debounce and show `*`, with explicit
Save / Save As… / Discard / Cancel when leaving an unsaved filter (§149).

Exact display (§§172–175) observes the actual PDFs at device/zoom resolution,
without PDF-content AA, image interpolation or decoder averaging. This is
read-only rendering, not repeated filtering. Native shapes refine on zoom.
The dated certified current runtime is in [PLATFORMS.md](PLATFORMS.md);
Task Coach-inspired cross-platform dependency/build plans are in
[PACKAGING.md](PACKAGING.md) (§176). Unbuilt targets are not certified.

Action icons (§197) use the desktop theme with a bundled stock Breeze SVG
fallback, not custom glyphs. Naming, palette handling, licenses and packaging
requirements are in [ICONS.md](ICONS.md).
§200 rejects the current appearance and adds View → Icon Lab… for genuine
Nuvola/Oxygen/GNOME/Breeze comparisons, permanent choice codes and a copyable
per-action reply. Selections never apply automatically; see [ICON_LAB.md](ICON_LAB.md).

The designer's new low-color experiment is documented separately in
[LAYERED_COLOR_JBIG2.md](LAYERED_COLOR_JBIG2.md) (§§192–194): one colored
lossless JBIG2 stencil per non-white palette entry. §203 subsequently makes
this an optional explicit image codec; existing preset defaults are unchanged.
Every filter can now edit Image compression independently of its name/template.
§205 adds independent PDF stream compression (Flate, Zopfli-Flate or limited-
reader-support Brotli). Design, measured full-PDF results and actual reader
limits: [NATIVE_STREAM_COMPRESSION.md](NATIVE_STREAM_COMPRESSION.md).
§209 separately benchmarks image compression at equal pixels, size-only:
[IMAGE_STREAM_COMPRESSION.md](IMAGE_STREAM_COMPRESSION.md). Native-only
Brotli gains cannot substitute for indexed-color or BW/JBIG2 measurements.

§§222/223 make [INTEGRATED_COMPRESSION.md](INTEGRATED_COMPRESSION.md) the primary
size analysis: realistic combination rows over five representative complete
PDFs, then focused scenario tables, with all overhead included and no timing
comparisons. Mixed general-codec pairs are excluded; the two component
studies above support the analysis, not substitute for it.

§§210/211 request [a reasonable-combinations table and UI review](COMPRESSION_COMBINATIONS.md).
The proposed shared general-compressor/disabled-control design is separate
from current capabilities; no new selector behavior, color FFPR or saved-recipe
migration is approved by the documentation request.

Designer §213 subsequently rules that encoding cost is not a product constraint:
use the best validated encoding and drop superseded encoder choices. Zopfli
needs only the existing Flate decoder, so the target is one optimized Flate
format versus genuinely different reader-support requirements such as Brotli.
The current three-way selector has not yet been aligned (TODO §217). This
supersedes the historical Max/Balanced/Fast effort brief, not fidelity rules.

HISTORICAL BRIEF BELOW — original JPEG defaults, DPI-ceiling wording,
page-list/per-page-control plan, on-click work and size estimates are
superseded or unimplemented. They are not current developer instructions.

Target first: **LXDE on Debian 13 (trixie), Python 3.13**.
Goal later: same codebase runs on Windows / macOS / other Linux.

## What it does
Drag-and-drop (or File > Open) a PDF, visualize per-page and global size wins,
apply one of two opinionated pipelines, save a much smaller PDF.

Two pipelines only (v0.1):
1. **BW Document** — render page → grayscale → threshold → 1-bit → encode
   with JBIG2 lossless. For scans, notes, books.
2. **Color/Gray Recompress** — keep page as-is, extract embedded images,
   downsample + recompress to JPEG (default) or JPEG2000 (opt-in). For slides,
   photos in PDFs.

No magic "auto-optimize" button that silently destroys quality. Every action
shows before/after preview + bytes saved.

## Opinionated defaults (max compression first)
- DPI: render/threshold at 300 dpi, downsample color images to 150 dpi.
- BW threshold: **Otsu auto** global, manual slider 0–255 overrides global,
  per-page override table overrides global (GIMP Threshold equivalent = Simple mode).
- BW encode: **JBIG2 lossless**; pages whose stream fails test-decode embed
  1-bit PNG instead (never a corrupt page).
  Lossy JBIG2 OFF by default (character-substitution risk, NARA forbids lossy for archives).
- Color encode: **JPEG q=50, subsampling 4:2:0, optimize**, fallback to keep-original if larger.
  JPEG2000 OFF by default (20% smaller but 5–10x slower + viewer lag on big pages).
- PDF save: `garbage=4, deflate=1, use_objstms=1` (PyMuPDF), dedup images.
- Speed knob: single `Effort: Max | Balanced | Fast` that maps to the above.
  Max = smallest file, slowest. Fast = JBIG2 + JPEG only, no JP2, no Sauvola.
- JPEG XL: **NOT used inside PDF in v0.1** (see `PDF_OPTIMIZATION_NOTES.md`).
  Optional sidecar export later.

## Non-negotiables
- **ESC cancels anything in <200ms.** Every long loop checks a cancel event
  per page, kills subprocesses (`jbig2enc`, `cjpeg`, etc.), cleans temp files.
- No network. No telemetry. Local files only.
- Never overwrite input. Output defaults to `<name>.reduced.pdf`.
- Born-digital PDFs (selectable text / vector) get a warning before BW rasterize,
  because BW mode in v0.1 destroys the text layer.

## v0.1 scope
- Open 1 PDF (DnD + button), page list with thumbnails, click page → large
  before/after preview, global threshold slider + strategy dropdown, per-page
  threshold override, size estimate label, Save + Cancel.
- No OCR, no MRC sandwich, no multi-file batch (v0.2).
