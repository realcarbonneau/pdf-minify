# Test Plan

Current canon coverage (§§149/150/155): `test_filter_lifecycle.py` verifies every
real output file and exact final size, zero jobs on first/repeated selection
or view/DnD changes, one debounced edit, dirty markers, full effective keys,
every unsaved-dialog decision, canceled naming, late pending completions,
copy/source references, byte-identical PDF export, and canceled open/close.
It also checks selected-first submission, live-process-safe temp sweeping,
real JPEG/JPX/Indexed/BW saved-image readback, corrupt-output rejection, and
zlib-wrapped Zopfli output with validated fallback, UUID directory ownership,
identity stability, independent copies, and normal-exit PID cleanup.
`test_filter_identity.py` checks random non-MAC UUIDv4 generation, injected
collisions, pasted duplicate UUIDs/aliases, invalid/missing IDs, migration
persistence, and stable reloads. The pre-B81 flow/identity suite had 124 tests.
`test_minis.py` covers view/geometry/selection and actual caption pixels.
`test_strip_reorder_identity.py` reproduces the pre-fix armed Qt drag state;
verifies one drag controller, model-only order, repeated high-index moves/all
clicks and caption pixels with content refresh forbidden, UUID-addressed
updates, rejection of foreign model data, and duplicate persisted-order repair.
`test_minis.py` additionally checks §159: shared 4px top/bottom padding,
full amount captions, no hidden vertical range, and theme-derived strip-only
background across light/dark/live palette changes. Rendered color comparisons
use 8-bit RGBA, matching screenshot precision rather than QPalette's 16-bit color.
§§160–162 add 16 cases: every decision via dropdown and real mini click;
real Escape/Cancel/dialog-close after mouse, keyboard and reordered input;
saved/draft file and visible/current selection invariants; and Revert while
ready, debouncing or processing. Qt's two-step key selection must prompt once.
The standard Discard identity/destructive role retains the explicit label
"Discard Changes". The pre-centering full suite had 150 tests. Native smoke exercises the
11-filter layout, eight drag scenarios, 33 subsequent clicks, and actual dirty
mini Escape + Revert gestures at 100%/200%.
`QT_QPA_PLATFORM=offscreen ./.venv/bin/python tools/filter_smoke.py` captures
real completed files, dirty captions, the actual Qt prompt, canceled mini
selection, the standard Revert icon (§197), and Revert/Discard cleanup.
§§164/165 (B87) add 16 viewer cases: actual occupied bounds and horizontal/
vertical centering for one/two/five/nine pages, either-pane zoom with shared
grid positions, exact-fit transformed gaps without a trailing gap, and
resize-only reflow in either resize order. The real-file lifecycle test also
checks baseline/preview/mini grid agreement and centering with processing
submission forbidden. This stage's suite had 166 passing tests.
`tools/shot.py` captures the default one-page input, real two/seven-page
fixtures and stacked layout, including each full window and 1:1 pane/strip
images. Captures were viewed. It mirrors the designer's settings into an
isolated review store, never replaces their remembered input with fixtures.
§166 (B88) adds four cases: 640px/960px shrink across real debounce intervals,
splitter drags with metadata updates/processing forbidden, and full-content
paint-only elision with unchanged size hints/layout and readable theme ink.
Resize-stage full suite: **170 passed in 47.65s** (2026-10-14).
`tools/resize_smoke.py` measures ten seconds of actual 12-page geometry and
then squeezes the panel itself. Before repair: 23 reframes, last geometry
change at 3.955s. After: stable at 0.023s (100%) / 0.049s (200%), one normal
reframe, equal panes, unchanged prepared files/generation, native overflow.
Whole windows plus 1:1 headers/panels were viewed, as were standard shots.
The designer explicitly confirmed B88 in §167, independent of test results.
Run the full `./test.sh`; native DnD and viewed screenshots follow
`DEVELOPER_GUIDELINES.md`. Old speculative fixture/manual lists below are
historical planning, not evidence that their features are implemented.

## BW composition audit (§§168–171)

Actual saved-file regressions cover one combined image canvas, native text
and vector instructions/positions/colors/opacity, overlap, removed masks,
native overlays across formerly interleaved images, crop boxes/rotation/reused
forms, compose-first/full-color DPI-before-threshold, eligible original
font subsetting and high-zoom glyph rendering, real images.pdf, and PNG fallback.
Native-only pages stay native; annotations and links remain on copied pages.
Clip-only native text is kept as an actual PDF clip, never an invented mask.
FFPR checks every distinct page against its own thresholded source, pinning B90
for both JBIG2 and PNG; the saved-file benchmark repeats this on the corpus.

`tools/bench_bw_layers.py` records whole-file sizes, timing, encoded image/mask/
font bytes, retained words/positions, pixel-exact FFPR pages and independent
Poppler (`pdfimages`) decode of every saved 1-bit image. All algorithms and
outputs use the real saver; no preview estimates. Current evidence goes into
`COMPRESSION.md`, issues B89/B90 and TODO §§174–178 after final verification.

## Exact display and current certificate (§§172–176)

Display-stage full suite: **203 passed in 46.82s** (2026-10-14). Compression-stage
suite had 186; `test_exact_display.py` adds 16 real pixel/geometry/cache cases
and filter lifecycle adds one displayed-draft native-file ownership case.
The 16 display cases also pass with `QT_SCALE_FACTOR=2`: strict FFPR at
30/75/150/175/300/600dpi and five actual-view zooms; native text/vector detail
versus stretched prepared pixels; encoded color/gray/opacity; restoration of
filter settings on success/failure; bounded caches/closed PDF sources; and
pixel agreement between individual view and parent-window painting. The last
test reproduced a whole-window device-origin defect before its repair.

`QT_QPA_PLATFORM=offscreen .venv/bin/python tools/display_smoke.py` (also
`QT_SCALE_FACTOR=2`) captures real images.pdf at zoom 0.1/0.75/2/4. Actual
filtered viewport samples are 0/255 and artifact SHA-256/generation unchanged.
Metrics live in `.tmp/display-{1,2}x-metrics.json`; PNGs include whole windows
and 1:1 original/filtered panes/strips. Captures are actually viewed. Standard
`tools/shot.py` and `tools/filter_smoke.py` are also rerun/viewed after the
display change. These are worker verification, not designer issue acceptance.
Current platform/runtime scope is in `PLATFORMS.md`; proposed installed-artifact
release gates and build-only packages are in `PACKAGING.md`.

## Compose-first color/BW and precise controls (§§177–182)

Compose-first stage suite: **229 passed in 45.67s** (2026-10-14), `./test.sh`.
Twenty `test_color_canvas.py` cases cover hidden black RGB behind a separate
soft mask, overlapping alpha on a real colored backdrop, one full-color resize
before either color encoding or BW gray/threshold at 72/144/720dpi, all color
codecs, forced palette bounds, original path clips, four rotations and native
content, exact-DPI dimensions, tiled-native/global-resize seam detection,
native-only pages and owned scratch cleanup after render/resize failure/cancel.
Per-image extraction is forbidden during the order regressions. BW's earlier
per-image/stencil tests now assert the superseding canvas-first order, not the
discarded architecture. FFPR retains its independent complete-page reference.

Five `test_numeric.py` cases verify slider↔native spin-box synchronization,
single edit signals, blocked recipe loading, live keyboard typing, actual
spin-arrow clicks, bounds/no wrapping, accessible names and stable native
three-digit size hints. They also pass at `QT_SCALE_FACTOR=2`.
The lifecycle case types T=203, observes the immediate dirty marker, waits for
one debounced real recipe, reverts without work, then verifies disabled and
enabled pairs on filter selection. Existing dirty/Cancel/Save/copy cases pass.

Viewed captures: `tools/shot.py` numeric Threshold/Colors windows, 1:1 editors,
panes/strip, one/two/seven pages and stacked layout; `tools/filter_smoke.py`
dirty dialog, modal Escape with retained selection and Revert icon/result.
`tools/resize_smoke.py` passes at 100%/200% with equal panes and last geometry
changes at 0.136s/0.101s, no delayed divider drift, unchanged artifacts and
native overflow; full/1:1 panel captures were viewed. Exact-display smoke
passes at both scales with only 0/255 FFPR viewport samples at four zooms,
unchanged PDF SHA-256/generation and viewed captures.

Saved-file benchmark/independent decoder evidence and limitations are in
`COMPRESSION.md`, including 50 color and eight BW image-page decodes. Platform
and supervised desktop restart evidence is in `PLATFORMS.md`. This is worker
verification, not designer acceptance of B92 or older unconfirmed issues.

## Nearest palette and global debounce (§§183/184)

Palette/debounce-stage full suite: **244 passed in 64.42s** (2026-10-14), `./test.sh`.
`test_palette_nearest.py` adds eleven cases: independently brute-forced nearest
RGB assignment at 2/3/4/8/16/64/256 colors, true white backdrop retention,
non-wasted colored slots in white-heavy artwork, the discarded octree/white
fallback reproducer, exact adjacent few colors, agreement between packed
Indexed parts/RGB helper and actual saved images.pdf pixels at full 150dpi.
Five numeric plus eleven palette cases also pass at 2× (16 tests, 9.38s).

Four lifecycle regressions verify the ONE precise, single-shot 300ms trailing
timer. Interleaved native spin steps, slider, DPI, FFPR and page-size edits
restart it without early submission; final immutable recipe/file/preview agree.
Separate cases cover palette stepping/typing, strategy and lossless controls.
Existing cached-recipe/selection/view zero-processing tests still pass.

Fresh `tools/shot.py` captures 3/4/8/16-color real-file results as well as
normal controls/layout. Whole windows and 1:1 previews were viewed. Fresh
`tools/filter_smoke.py` additionally mixes three native spinner steps, a slider
change and typing to 3 colors: no submission at 220ms, exactly one final job,
matching current preview/size and cached Revert with no extra work. The actual
3-color dirty result and reverted 16-color captures were viewed. The five
default color PDFs were independently decoded again; `COMPRESSION.md` records
current sizes and distinguishes earlier-stage benchmarks from the final repair.
The designer confirms the palette improvement in §184; debounce tests alone
do not count as explicit designer confirmation of B94.

## Native mini progress overlays (initial §185 stage)

Initial stage full suite: **272 passed in 64.35s** (2026-10-14), `./test.sh`.
The width/height/backing/centering refinements below supersede this stage's
appearance, not its progress/lifecycle contract.
Twenty-eight new `test_minis.py` cases also pass at `QT_SCALE_FACTOR=2`
(2.02s). Compare delegate pixels to actual QProgressBar widget paint events,
not another hand-drawn implementation: Fusion/Windows styles, light/dark
palettes, selected/unselected states and 0/37/99% progress. Assert the full
150px reserved cell width, native height, centered position and genuinely
opaque white backing above the selection wash. Check the native label's
foreground pen as well as style, palette, font and locale/RTL updates.

Other cases forbid filtering/icon rebuilding for a model-role progress
update, verify completion removes bar AND backing without geometry changes,
and compare the selected-cell/drag-source/native-bar pixels plus uniform
75% exported ghost opacity. The default status bar's value/range stay intact;
the one hidden formatting widget remains hidden and consumes no input.

`tools/shot.py` passes at 100%/200%; actual viewed whole-window and 1:1 captures
include queued processing, a real debounced edit over the retained thumbnail,
and completion. A one-page edit may remain 0% until the next worker poll;
clearly named `progress-paint-fixture` captures additionally pin 0/37/99/65/12%
and completed states side by side. They are paint fixtures, not fabricated
worker progress. Default-bar and selected-source/ghost crops were also viewed.

Native X11 smoke passes at both scales: eight drag scenarios, correct visible
renumbering, 33 post-reorder clicks, Escape, dirty-mini Cancel and Revert, with
no filtering on selection/reorder. The extra 2× run initially missed a tail
drag start when independent scenarios pressed the same cell inside Qt's
double-click interval. The helper now spaces those independent gestures by
the platform interval and asserts a native press arrived; its full rerun
passes. Production drag handling is unchanged. Native window/strip/ghost
captures were viewed. That stage awaited acceptance; §192 later confirms
the final refined B95 appearance on 2026-10-14.
The available Qt style named Windows is not Windows OS certification.

## Shared spacing, Save As destination and enlarged mini bars (§§187–191)

Historical 1.5× stage below; §§198/199 supersede ONLY its mini bar/font
scale with 1.25×. Width, padding, centering, native rendering and lifecycle
requirements remain current. New verification is recorded below.

Final full suite, including §§192/195 and the prototype below:
**319 passed in 75.40s**, `./test.sh`, 2026-10-14.

2026-10-14 worker verification, not designer acceptance:

- Native progress overlays now leave the shared 4px highlight inset on both
  sides (142px within the 150px mini), use 1.5 times the status bar's native
  height and percentage font, and center in the FULL 162px frame, not the
  104px image area. The opaque backing is exactly the bar bounds; no added
  white padding. Thirty-two progress cases pass at normal scale (1.38s) and
  2× (2.29s), including both styles/themes, point/pixel font changes, actual
  frame heights/translated origins, untouched neighboring pixels, native
  locale/RTL, completion, no filtering and uniform 75% ghost opacity.
- The native-widget oracle paints at the SAME cell position and device
  scale as the delegate before cropping. Origin-zero versus translated
  painting otherwise exposes Qt's subpixel clip/gradient rounding rather
  than a product difference. No pixel tolerance was added: equality remains
  exact. The delegate uses native local coordinates for text/chunk clipping.
- Both-scale `tools/shot.py` runs pass. Actually viewed whole windows and
  1:1 strip/junction, explicit 0/37/99/65/12% paint fixtures, actual live
  edits, completion and selected ghost captures show the final appearance.
  Fixture percentages remain explicitly labelled, never fake worker work.
- Six real-frame geometry cases cover equal/stacked panes and wide/small
  windows, with no visible strip title, aligned sides/bottoms and shared 4px
  gutters. `tools/resize_smoke.py` passes at 100%/2×: last resize adjustment
  0.126s/0.115s, then stable for ten seconds; equal panes, squeezed panel
  overflow, no processing or metadata changes. Whole windows and 1:1
  header/panel/junction captures were viewed. Earlier combined 2× subset:
  59 passed in 16.13s (before the four newest progress cases were added).
- The full-suite resize regression now distinguishes an initial native
  horizontal scrollbar's one-metric height adjustment within 500ms from
  divider drift. Horizontal allocations must be stable immediately and the
  entire geometry stable thereafter; no production scrollbar workaround.
- Save As regressions cover Save/Discard/Cancel/Save As across dropdown,
  native mini mouse and keyboard entry; canceled AND blank names; direct
  Save As; pre-debounce drafts; pending/ready copies; and open/close
  resolution. New copy UUID, current/selected mini, dropdown, controls and
  exact-file preview agree; prepared work is reused and both files remain.
  `tools/filter_smoke.py` passes the actual dirty mini-click → modal Save As
  → real naming dialog → new-copy selection, with no extra real filtering.
  Both dialogs and selected-copy full window/strip captures were viewed.
- Final native X11 100% drag smoke passes (21:27:48–21:28:18): eight gestures,
  33 post-reorder clicks, correct visible numbers/UUIDs, 75% outside-strip
  ghost, Escape, dirty mini Cancel and Revert, no extra filtering. Captures
  were viewed. An additional earlier 2× native-caption pixel experiment
  remains inconclusive: after tail-last, one glyph in the correctly named
  T=180 label differs from the fresh-render oracle. No wrong name or UUID
  was found; no tolerance/forced repaint was added to hide it. This is not
  claimed as a product fix or a current all-green 2× native-drag certificate.

B95 is FIXED — DESIGNER CONFIRMED — 2026-10-14 (§192), scoped to progress.
B96/B97 remain OPEN pending their own explicit designer confirmation. Supervised
restart and current full-suite evidence are recorded in `PLATFORMS.md`.

## Proposed layered-color JBIG2 (§§192–194)

Design, benchmark protocol, measured full-PDF comparisons and remaining
integration decisions live in [LAYERED_COLOR_JBIG2.md](LAYERED_COLOR_JBIG2.md).
The prototype must prove disjoint-mask coverage, exact identical-palette RGB
reconstruction, actual PDF stencil filters/bit polarity, native-artwork
retention, multi-page independence and independent Poppler rendering.
No production codec/recipe/default change is authorized by this study.
Thirteen prototype tests pass (1.49s); 18 two-repeat benchmark cases cover 34
final-page pairs and 107 exact masks. App rendering and independent mask
decoding pass exactly; Poppler full-page differences and original-source
warnings remain explicit limitations, not a clean cross-viewer certificate.

## Matching Configuration header and no working placeholders (§§192/195)

All three regions use PaneHeader/PaneBlock. Existing six actual-frame cases
now assert equal header top/height, equal scroll-frame tops and shared
zero-margin composition, in equal/stacked modes at three window sizes.
Nine header/layout/resize regressions pass at both display scales.
Final `tools/resize_smoke.py` captures all three headers: last geometry change
0.099s at 100%, 0.182s at 2×, no further drift over ten seconds, native panel
overflow, no extra filtering. Actual full/small/squeezed windows and 1:1
Configuration headers were viewed, including queued/live/complete strips.

Eight new pending-label cases pin missing/cached images and amounts at
0/37/99/100%, no working/sizing/queued placeholders, transparent empty slots,
retained real byte metadata and no processing. Combined progress/layout/
pending subset: **46 passed** at 100% (2.14s) and 2× (2.53s). Final whole-
window and 1:1 `tools/shot.py` captures pass and were actually viewed at both
scales; a queued strip shows just its genuine native 0% bars, not fake work.
Full suite 319 passed; final app normally stopped/group verified/restarted.
B98/B101 remain OPEN for designer acceptance. B95 alone is confirmed (§192).

## Standard action icons (§§196/197)

One provider replaces the independent custom drawings and missing-icon paths.
Nineteen isolated icon tests cover native-theme precedence and individually
missing names, absent themes, stock SVG hashes/licenses, both source grids,
transparent backgrounds, light/dark contrast, normal/disabled/active modes,
1×/2× device pixels, control versus window/toolbar palette differences and
live refresh without actions. Main-window coverage verifies all eight action
bindings, enabled flags, selection, recipes/prepared files and zero new jobs.
The button lab uses the same provider.

Full suite: **339 passed in 71.05s**. The final icon/lab/main-window subset
passes at 2×: **33 passed in 4.04s**. Full `tools/shot.py` runs passed at both
scales; actual native Breeze and forced-fallback light/dark windows and 1:1
enabled/disabled action/toolbar crops were viewed. An initial dark-palette
diagnostic exposed stylesheet-polished children retaining light surfaces;
the provider now matches the actual control/toolbar background, and fresh
palette-specific windows make the visual fixtures consistent.

Extra normal-scale resize smoke passed: last adjustment 0.210s, stable for
ten seconds, aligned gutters/frames and native panel overflow, no processing;
full/squeezed captures viewed. The additional 2× run was interrupted with
exit 143 before completion, not called green. No production layout workaround
was added. An earlier full-suite run was likewise interrupted (143); the
complete rerun above is the regression evidence.

Old GUI2386118 exited normally (`APP_EXIT status=0`), its whole group2386114
was independently verified gone, and session9907 launched GUI2409896 /
PGID2409892. Preview applied 22:43:52; all 12 artifacts ready 22:44:02.
This icon-only restart precedes the designer's next 1.25× progress refinement.
B102 remains OPEN pending designer acceptance; see `ICONS.md`.

## 25% mini progress enlargement (§§198/199)

The designer clarified 1.25× ORIGINAL height, not quarter-size. Native bar
height and percentage font share that factor; the independent actual-widget
oracle uses literal 1.25 rather than importing the implementation constant.
Reserved width, shared 4px insets, exact backing, full-frame centering,
aggregate status bar, selection, progress and no-filtering requirements stay
unchanged. Forty progress regressions pass at 100% (2.13s) and 2× (2.49s).
`tools/shot.py --progress-only` captures real queued/live/completed work,
explicitly named paint percentages, selected source/75% ghost and the
unchanged default bar without rerunning unrelated icon/grid review variants.
Both focused screenshot runs pass; actual full windows and 1:1 strips,
unchanged native status bars, selected sources and uniform 75% ghosts were
viewed at normal/2×. Final full suite: **339 passed in 68.67s**. The earlier
interrupted 2× resize left a stale PID-2 diagnostic lock; no matching live
diagnostic/test process remained in independent desktop checks. Only that
lock was moved to `/tmp/pdf-minimalist/diagnostic-pid2-lock-interrupted-20261014-2245`
for recovery; no PDFs, user drafts or live GUI files were removed, and the
canonical screenshot runs then completed normally. No production PID/session
design change was made to accommodate the harness's shared PID-2 namespaces.
The previous GUI2409896 independently exited normally (`APP_EXIT status=0`);
its full group2409892 was verified gone before final relaunch. No worker
Save/Discard/Quit action was sent to that GUI for this second restart.
Final retained-session/PID evidence is in `PLATFORMS.md`. B103 remains OPEN.

## Automated (pytest, run with `python3 -m pytest`)
1. `test_threshold_simple`: 3×3 gray array, T=127 → exact 1-bit output.
2. `test_threshold_otsu`: synthetic bimodal image (half 50, half 200) → Otsu T in 100–150, output has both classes.
3. `test_threshold_adaptive`: gradient + dark corner → corner stays readable (no all-black).
4. `test_sauvola_stained`: yellowed-paper fixture → Sauvola keeps text, Simple@127 loses it (compare pixel counts).
5. `test_jpeg_smaller`: sample photo PDF image → q50 JPEG bytes < original PNG bytes.
6. `test_g4_roundtrip`: 1-bit image → G4 encode → decode → identical pixels.
7. `test_jbig2_if_present`: skip if no `jbig2` binary; else JBIG2 bytes < G4 bytes on text fixture.
8. `test_cancel`: 50-page fake job, set cancel after page 2 → pipeline aborts ≤5 pages, no output file left.
9. `test_esc_binding` (GUI smoke): root has `<Escape>` binding, Cancel button calls `token.cancel()`.
10. `test_no_overwrite`: save refuses to overwrite input path.

Fixtures to create in `tests/data/`:
- `scan_text_300dpi.png` (1 page, generated via PyMuPDF from text PDF)
- `yellowed_note.jpg` (photo of stained paper, or synthetic stains)
- `mixed_4pages.pdf` (text scan + photo + vector + blank)
- `born_digital_text.pdf` (selectable text, for warning test)

## Manual (LXDE Debian 13)
- [ ] DnD PDF from PCManFM onto app → opens. Button open works without tkdnd.
- [ ] Move threshold slider 0→255 → preview updates, extremes all-white/all-black.
- [ ] Per-page override page 3 to T=200, others global 170 → page 3 differs, rest same.
- [ ] Otsu on 10-page scan → readable, no hollow letters.
- [ ] Save BW: check size −60% or better on scans; open in Evince + MuPDF + Chromium.
- [ ] Save Color: JPEG q50 photo PDF −30% or better, no visible blocks at 100%.
- [ ] ESC during 20-page Max job → stops <1s, UI alive, partial file deleted.
- [ ] Kill `jbig2enc` path (rename binary) → app falls back to G4 with info bar, no crash.
- [ ] 1GB RAM limit (`systemd-run --scope -p MemoryMax=1G`) → 50-page PDF still completes (streaming, no OOM).
- [ ] No-network run (unplug) → everything works.

## Metrics to record per test
Input bytes, output bytes, % saved, time sec, effort preset, strategy, T, DPI,
encoder (G4/JBIG2/JPEG/JP2), viewer check (Evince OK?), readability 1–5.

## Definition of done (v0.1)
- BW scan book: −70% size, readable at 100%, ESC works, no overwrite, opens in 3 viewers.
