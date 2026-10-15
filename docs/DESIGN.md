# DESIGN — preset filter-strip + comparison views

## Designer rulings (verbatim)
Quoted exactly from `DESIGNER_VERBATIM.md`. Do not edit the quotes.

Ruling §3 — original brief:
> I want to make a simple app that works on multiple platforms, but first targetting lxde debian linux.  I want to dnd or open a pdf docs and be able to visualize various optimizations to it.  Highly opinionated, eg conversion to BW with a few strategies and a global or per page threshold, like GIMP threshold option.  Also, another option that compresses images within the pdf to jpg XL or whatever highest compression algorithms exist.  Same for BW, JDIC2 (I think if I remeber correctly.  Always max compression for all by default, but tunable if too slow.  Always fast cancel with esc by user as required.  Start by making some md docs directly in this dir with your notes, ideas and tests.

Ruling §6 — picky UI:
> what if I am really picky about smooth clean custom UI highly tailored for a specific job, like pan, zoom in/out mouse scroll, next page, prev page, DnD, etc.

Ruling §9 — preset filter-strip + view options:
> I want to see a list of preset optimization options, like photo filters on a camera with a smaller version of previews, and when I click on one, the main doc has original and preview (optmized side by side, vertically or horizontally, same for the filter thumbnails, all would be choosable as menu view options.

Ruling §10 — raster defaults on main screen:
> Generally forcing alll images on the page and page rasterizing to 300dpi, and 8.5x11, but that also would be options on the main screen.

Refined by §74: page size defaults to Original (saving never reshapes pages
unless asked — forcing Letter would break normal pages). Letter/A4 stay as
advanced Save options for absurd scan sizes, which the File box flags with a
warning line (never auto-applied).

## Concept (camera-filter UX for PDFs)
- Left/bottom **filter strip**: every preset renders a small live thumbnail of the
  CURRENT page through its pipeline. Click a thumbnail = select preset → main panes update.
- **Main panes**: original (left/top) + optimized preview (right/bottom) of the same page.
- **View menu** controls orientation of main panes AND of filter thumbnails:
  - `View → Main: Side by side (H) | Stacked (V) | Single (toggle Orig/Preview)`
  - `View → Filters: Filmstrip (H) | Rail (V) | Grid`
  - Shortcuts: `Ctrl+1/2/3` main modes, `Ctrl+Shift+H/V/G` filter layout.
  - Zoom keys (designer ruling §52, modern standard): `Ctrl+Plus` in,
    `Ctrl+Minus` out, `Ctrl+0` fit-width. Panes stay synced either way.
  - Choice persists in QSettings.

```
View=Main:H + Filters:H (default, wide screen)
+---------------------------------------------------------+
| Pages | Original   | Preview (preset: BW Otsu) | Preset |
|  1    |            |                           | [oto]  |
|  2    |  before    |  after                    | [T180] |
+---------------------------------------------------------+
| Filters (filmstrip H): [orig][otsu][T180][T210][sauv][Cmax][Cbal] |
+---------------------------------------------------------+
View=Main:V + Filters:V (square / portrait screens) → panes stacked, rail on right.
```

## Preset list (v0.1 — opinionated, max-compression default)
| # | Preset (label) | Mode | Params | Use when |
|---|---|---|---|---|
| 0 | Original (no-op) | — | gc+deflate only | baseline / born-digital keep |
| 1 | BW · Otsu Auto ★ default | BW | 300dpi, otsu, JBIG2 | most scans |
| 2 | BW · Clean T=180 | BW | 300dpi, simple T=180 | clean laser prints |
| 3 | BW · Strong T=210 | BW | 300dpi, simple T=210 | faint pencil / gray bg |
| 4 | BW · Stained Paper | BW | 300dpi, sauvola w31 k0.25 | yellowed / uneven light |
| 5 | BW · Fast Draft | BW | 200dpi, otsu, JBIG2 | old hardware, quick pass |
| 6 | Color · JPEG2000 ★ default color | JPX | 150dpi, rate 192 | smallest photos, slower |
| 7 | Color · Max Squeeze | JPEG | 150dpi, q45 4:2:0 | smallest slides/photos |
| 8 | Color · Balanced | JPEG | 200dpi, q60 | readable photos, fewer blocks |
| 9 | Color · Poster 16 | indexed | 150dpi, 16 colors | flat graphics, tiny |
| 10 | Color · Indexed 64 | indexed | 150dpi, 64 colors | diagrams and logos |

Few-color images (designer ruling §57: ≤256 distinct colors — logos,
diagrams, flat screenshots) take a lossless true-Indexed version (designer
§80: packed 1/2/4/8-bit samples by actual entry count + inline palette +
best Deflate) whenever it beats the codec re-encode, in every color preset —
~10x smaller than RGB-Flate on flat graphics, benchmarked in
`tools/bench_indexed.py`.

Defined in code: `pdf_minimalist/core/presets.py` → `PRESETS` (id, label, mode, params).
Rendering/proof rules have moved to their topical docs (designer §125):
main-window regions, dividers, strip, headers and controls in `UI_LAYOUT.md`;
the single-path saver→temp→preview/minis/amounts flow in `ARCHITECTURE.md`;
temp vs persistence in `PERSISTENCE_AND_TEMP.md`; mixed-mode evidence in
`MIXED_MODE_ANALYSIS.md`. This file keeps the original concept; where it
disagrees with those docs, those docs rule.

## Behavior
- Left pane is always the unmodified baseline (no baseline variants); right
  pane shows the selected filter. The strip shows one live mini per filter of
  the current page — Original excluded, the left pane is the baseline
  (designer ruling §30).
- Panes always synced (designer ruling §22): zoom, pan, and scroll in either
  main pane mirror to the other instantly.
- Pane titles elide (designer ruling §124): a title longer than its half
  shows "…" — hovering the label shows the full text.
- Continuous viewer, no page list (designer ruling §26): both panes scroll
  through ALL pages vertically with a 24-scene-unit gap; the left page list is gone and
  the status bar shows `Page N of M` from scroll position instead.
- Autowrap grid (§§26/164/165): zooming out reflows pages into as many
  occupied columns as fit, capped by actual page count. Page spacing is in
  scene coordinates, so capacity uses the transformed page-plus-gap stride
  with no trailing gap. Scene bounds cover only the occupied grid; Qt centers
  it horizontally/vertically on axes that fit. One/two pages never reserve
  nonexistent columns. Original/preview use the same baseline grid and peer
  zoom reflows both; minis use that layout. Zoom/layout never re-filter.
- PgUp/PgDn jump to prev/next page top; click a filter mini still switches
  the right pane's filter (radio-behavior); minis render the current
  (top-visible) page.
- Sizes under minis (designer ruling §32, real amounts §§55/59, single path
  §122): each strip mini carries its filter recipe (threshold strategy, DPI,
  encoder — `§53`) and the FULL-document amount, which is the measured size
  of that filter's saved temp file — container, masks and fonts included.
  No estimates anywhere, no estimators at all; every amount carries its % of
  the original (`23KB (10%)`, original header `100%`). Flow details and the
  why in `ARCHITECTURE.md` (single-path flow).
- DPI wording stays plain (`150dpi`, no max/≤). §129 supersedes §64's
  earlier ceiling-only interpretation: transforms force exact displayed-size
  DPI with Lanczos, up or down, before encoding. See `COMPRESSION.md` for
  implementation exceptions; this does not change the one-DPI UI (§85).
- Navigator dropped (designer ruling §50): the separate OverviewMap navigator
  is gone — the original (left) window is the navigator. The right panel keeps
  preset, strategy, threshold, DPI, page-size, force-raster, page buttons,
  Save and Cancel; page/progress/status stay in the status bar.
- One panel + menu (designer ruling §32): no left panel. File actions live in
  the menu; all working controls live in the single right panel; page/progress
  /status live in the status bar.
- Scratch vs kept (designer ruling §123): app scratch lives in the OS temp
  dir (`/tmp` Linux etc. via Qt); saver temp files regenerate from
  input + spec and are swept at startup. User data (last file, custom
  filters) persists via QSettings. Full split in
  `PERSISTENCE_AND_TEMP.md`.
- Background work (§§37/51/90/122/149) uses spawn-context worker processes,
  capped at half the cores, with thin Qt managers. On open, EVERY saved filter
  runs the real saver once; the selected filter is queued first, then strip
  order (§128). Prepared saved-file pages support both views without extra
  filter jobs on first selection or pan/zoom. Disk-backed buffers avoid
  holding every full document in RAM. There is no independent preview/mini
  transform or size-estimator job. See `FILTER_LIFECYCLE.md`.
- Saved/live state (§§109/112/149): control edits make a separate draft,
  display `*`, and debounce processing through ONE shared trailing 300ms timer
  for all recipe controls (§183, proposed default). Programmatic control loading
  never edits recipes. Switching away from a draft prompts Save / Save As… /
  Discard / Cancel; Save keeps the processed live file instead of invalidating
  it. Save As… keeps the original recipe/file and a new named recipe/file.
  Rename changes the name only. PDF export copies the displayed real file.
- Thumbnails = exact mini of the main view (designer ruling §48, intent §32
  + §37 + §45): each strip mini shows EXACTLY what the synced main windows
  show — same pages, same grid, same scroll framing down to the cut-off last
  page — but rendered through that mini's own filter from its internally
  preprocessed file (built in background at start / latest change). Scroll,
  pan and zoom are pure view changes: minis re-frame from cached per-preset
  pages with zero background jobs (§47). A new job runs only on file change
  or filter-spec change (§44).
- Strip style (latest designer rulings §§134/138/145): full-cell theme wash
  on the selected mini, with its thumbnail and caption included. No extra
  border, divider, focus bar, or style accent. The item delegate renders the
  same complete cell for display and drag; Qt size hints reserve scrollbar
  and frame space. The drag ghost has uniform 75% opacity (§146). Detailed
  geometry, selection, and drop rules live in `UI_LAYOUT.md`.
- Per-filter progress (designer ruling §43): EACH strip filter shows its own
  true work progress from 0, never a fake 50% milestone (§§89/95).
  A complete real PDF and its prepared views yield 100% and exact full bytes.
  The status-bar bar keeps only the aggregate job progress; it never replaces
  the per-filter bars.
- Mini progress appearance (§§185/187/190/191): native default-progress style, reserved
  cell width less the shared 4px outer inset at each side (142px in 150px),
  not image width. Inset the opaque white backing too so highlight remains
  visible. §§198/199 replace §190's 50% enlargement: scale native bar height
  and percentage font by 1.25 for minis only (25% larger, not quarter-size);
  no extra white padding, just opaque backing within the bar's bounds.
  Center vertically in the ENTIRE mini frame, including captions, and paint
  above the selection wash. Hide the whole overlay when
  complete; retain actual progress values and existing row/drag geometry.
  Delegate/model and native-metrics details live in `UI_LAYOUT.md`.
- Pending mini labels (§195): no "working…" image/amount placeholder. Progress
  bars convey work; unavailable results stay blank and previously completed
  image/size metadata remain visible during live edits. Keep real errors.
- Action icons (§§196/197): use the native desktop icon theme consistently,
  with a bundled, licensed KDE Breeze SVG subset as the ONE fallback family.
  No custom QPainter glyphs or missing icons. This supersedes earlier claims
  that §120 authorized custom rename artwork and the old theme-independent
  zoom workaround. Revert Changes uses document-revert, not step-history Undo.
  Preserve action meaning, button sizes, tooltips, native disabled styling and
  device-scale rendering. See `ICONS.md` for names, theme changes and packaging.
- Icon Lab (§200): direct View menu entry, modeless reusable comparison of
  genuine Nuvola/Oxygen/similar stock choices with permanent per-choice codes.
  Per-action selections and a copyable reply are a design-review aid only:
  no automatic Apply, settings writes, filter/selection changes or processing.
  The designer rejects the present glyphs; replacement selection is theirs.
  See `ICON_LAB.md` for the comparison and provenance contract.
- Main-region composition (§188): no minis title or placeholder row. One
  shared 4-logical-pixel token owns outer insets and gutters, including the
  panel splitter handle, with no stacked default wrapper margins. Align the
  full-width strip with the main row's side edges and all three side-by-side
  region bottoms. PreviewPair owns the zero-margin equal/stacked preview
  layout; the root owns outer spacing. See `UI_LAYOUT.md`, B96, TODO §191.
- Three-block headers (§192): Original, selected-filter preview, and
  Configuration all use the same single-line PaneHeader plus zero-margin
  header/content component. Configuration is above/outside the right scroll
  area; side-by-side header and frame tops align, bottoms remain aligned.
  Keep shared 4px spacing, native overflow and stable resize behavior.
- Layered low-color JBIG2 (§§192–194): study one lossless binary stencil per
  non-white palette color on an opaque white base; native text/vectors stay
  separate. Shared compose/resize/palette map, exact reconstruction and actual
  COMPLETE-PDF comparison with Indexed. Explicit scope is design/benchmarks
  first, no production filter change. See `LAYERED_COLOR_JBIG2.md`.
- Save As destination (§189): a named copy becomes the active, visibly
  selected filter through the same selection commit path for explicit Save
  As, mini/dropdown/keyboard dirty-switch resolution, and successful open/
  close resolution. A dirty filter switch must not overwrite the copy with
  the initially clicked filter. Preserve Save/Discard/Cancel semantics and
  prepared result ownership; see `FILTER_LIFECYCLE.md`, B97, TODO §192.
- Exact PDF display (§§172–175): both main panes observe their actual files
  at current zoom/device resolution. Disable all PDF-content AA, bitmap
  interpolation and decoder subsampling. Native text/vector geometry gains
  detail as zoom increases; bitmaps remain literal samples. No additional
  display threshold, saved-file mutation, or filter work. Exposed-region
  painting and bounded caches replace prepared-raster-only zoom; prepared
  saved-file pages still supply layout/minis, using nearest-neighbor scaling.
  Genuine encoded colors, gray and opacity are document content, not AA bugs.
- Process-once (§§44/47/48/122/149): a filter result is computed once
  per (input identity + FULL effective saver recipe) and reused.
  Clicking the strip or preset combo with an unchanged key switches panes
  instantly with NO new background job. A new job runs only when the file
  (path + mtime + size) or the effective recipe changes. Filter name/id,
  selection, page, crop, pan, zoom and order never create processing work.
- BW composition clarification (§§168–171): OFF keeps both native text and
  vector diagrams, including original font/geometry/color/opacity. Optimize
  overlapping imagery, not the text or vectors; no invented glyph masks or
  bitmap text plus duplicate selectable layer. One composite canvas is only
  the simple default: images combined on white, native text/vectors above,
  white page backdrops below. Exact native/image stacking is not required
  by §171; FFPR is the flattened-fidelity choice. See `COMPRESSION.md`,
  B89 and TODO §§174/176/177; old per-image-only implementation is superseded
  as the target, not permission to reintroduce color JPEGs in BW.
- BW raster policy (designer ruling §127): Force full-page raster ON
  flattens the page to one image; OFF keeps native text/vectors with one
  combined BW image canvas (§171; never color JPEGs in BW image output). The old mixed-JPEG
  behavior is gone; the JBIG2-layer variant survives only as the
  unimplemented proposal in `MIXED_MODE_OPTION.md`.
- Per-page override (brief §3, not yet built): page remembers its preset; empty = current global.
- Composition/transform order (§§180–182): flatten original bitmap artwork
  and its opacity in full color, then ONE resize to exact final DPI, then
  gray/threshold, palette or codec processing. No original-plus-upscaled
  duplicate filtering or post-filter resize. This replaces the old per-image
  DPI preparation; native text AND vector diagrams still overlay (§170).
  Color includes the real flat page backdrop; BW retains §171's white canvas.
  FFPR continues to flatten the complete page before thresholding.
- ESC cancels thumbnail batch + save job alike (<200ms, partial output deleted).
- Born-digital warning: selecting a BW preset on a text-layer page shows the
  yellow banner (rasterizes text away) with [Continue] [Use Color instead].
- Display rule §106: the strip shows key-addressed store views —
  recomputes never blank displayed minis or amounts (stale-while-revalidate;
  progress bars signal the work). Only opening a new file clears them.
- Effective recipes (§§127/149): preview, mini, final bytes and export share
  ONE result key with the full effective recipe. Toggling FFPR affects exactly
  the selected filter's draft; all other saved recipes/results stay unchanged.
- DPI is a ceiling here only historically (§64): since §129 the save
  transforms force exact DPI (up and down) — see `COMPRESSION.md`, which
  rules on disagreement.

## Issues on this page

B22 — see `issues.md` (gated log). Layout, flow, compression and temp
issues live on `UI_LAYOUT.md`, `ARCHITECTURE.md`, `COMPRESSION.md` and
`PERSISTENCE_AND_TEMP.md`.
