# UI layout — main window regions and rules (designer §125)

The main window has exactly four regions. Ruling quotes live in
`DESIGNER_VERBATIM.md` (§ numbers below); work history in `TODO.md`;
defect history in `issues.md` (B numbers below).

```
+---------------------------------------------------------------+
| File  View                                                    |  menu bar
+---------------------------------------------------------------+
| Original metadata  | Filter metadata    | Configuration    |
| +----------------+ +-----------------+ | +----------------+ |  main row:
| |                | |                 | | | File: path…    | |  three blocks
| | BEFORE         | | AFTER           | | | Filter: [combo]| |  | draggable
| | (baseline)     | | (filter)        | | | [ren][cp][save]| |  | divider
| |                | |                 | | | Details/inputs| |  right panel
| |                | |                 | | | Zoom/export   | |  (scrolls)
| +----------------+ +-----------------+ | +----------------+ |
+---------------------------------------------------------------+
| [mini][mini][mini][mini][mini][mini]… → (horizontal scroll) |  full-width strip
+---------------------------------------------------------------+
| filename — N pages (job G) | Page 1 of N | progress | 100% |  |  status bar
+---------------------------------------------------------------+
```

## Main row: panes block + divider + right panel

§188 main-region spacing: one shared UI_PADDING = 4 logical pixels owns the
central layout's outer left/right/top/bottom insets and inter-region gutters.
The main splitter row and strip share the exact outer left/right edges.
No visible minis title or reserved title row remains. The original/preview
frames and right-panel scroll frame end on the same bottom line in side-by-
side mode; one 4px gutter separates that whole line from the mini-strip frame.
In stacked mode, the lower preview frame shares that bottom line with the
panel. The panes' gutter and the draggable panel splitter handle are also
4px wide. This supersedes the old unrelated 6px/8px gaps.

Only the root layout owns outer padding. §192 gives ALL THREE blocks the same
PaneBlock composition: one PaneHeader above one content widget, zero margins
and shared 4px header/content spacing. The right heading is "Configuration",
outside the panel's scroll frame, never scrolling away with its form. In
side-by-side mode all header tops/heights and all scroll-frame tops align;
bottoms retain §188's alignment. PreviewPair owns the equal/stacked preview
blocks, without introducing another set of margins. The panel form owns one explicit
4px internal inset and row spacing. Preserve native frame/scrollbar/control
interiors and the deliberately joined zero-gap zoom control; do not compensate
with per-widget moves, negative margins, fixed overall heights or changing
minimum widths. STRIP_PADDING aliases this same token, including §187's
progress overlay inset. This is a layout policy, not PDF-image padding.

- Two panes, locked equal, no splitter between them (§107, B43): baseline
  left, filter preview right, shared 4px gap (§188), synced zoom/pan/scroll either way
  (§22). Zoom is Ctrl+Plus/Minus/0 (§52) plus −/%/+ toolbar buttons with
  standard theme/fallback magnifiers (§197 supersedes the §84 custom-drawing
  workaround); zoom never reprocesses filters.
  §§174/175 supersede the old prepared-raster-only display: native PDF
  shapes redraw at device resolution without AA. Switching filters never moves the view (§101: the
  preview mirrors the baseline grid exactly).
- Zoom-out page-group centering (§§164/165): use only occupied columns,
  capped by the document's actual page count. One page centers on both axes
  when it fits; two pages center together; larger groups tile left-to-right,
  row-by-row and center their occupied grid on each non-scrolling axis.
  Compute capacity from the same transformed page-plus-gap stride used for
  placement, with no trailing gap. Start from Qt's maximum available viewport
  and reserve a native scrollbar only if the proposed grid needs it; an old
  one-column scrollbar must not prevent a fitting two-column reflow. No
  phantom empty columns, forced pan reset, or per-page centering
  offsets. Qt's AlignCenter works on the accurate scene bounds
  ([QGraphicsView alignment](https://doc.qt.io/qt-6/qgraphicsview.html#alignment-prop)).
  Original and preview share baseline grid dimensions/column calculation;
  peer zoom must reflow geometry as well as copy the camera transform. Minis
  frame that same occupied grid. These remain pure view changes, no filtering.
- Headers ride above each pane (§60): left = `Original · size · 100% ·
  N pages`, right = `filter label · recipe · amount (%)` — the same amount
  string as its strip caption. Overflowing titles elide with "…" and show
  the full text on hover (§124, B55).
- The divider between the panes block and the right panel is a real
  draggable splitter: non-collapsible, visible shared 4px handle (§§117/188,
  B48/B96). It
  replaced the panel-width slider, which was ruled wrong (§117).
- Right panel scrolls internally; squeezing it below content width shows a
  horizontal scrollbar instead of clipping (§118, B49).
- Resize settling (§166): shrinking a maximized window must not trigger
  seconds of timer-driven divider drift. Content display updates (elided
  headers, mini reframing, progress/amounts) must not feed changing minimum
  widths back into the outer splitter. Qt owns layout at the new size; main
  panes remain equal, controls overflow within their scroll area, and the
  designer's chosen splitter position is not repeatedly forced or animated.
  Pane headers retain their full text/tooltip and elide only while painting
  their allocated content rectangle. Their horizontal size policy ignores
  text width; a view resize or splitter drag never rewrites label text or
  publishes a progressively shorter minimum size. Filter/file metadata owns
  header content; the mini-view debounce does not refresh that content.
  See [Qt size policies](https://doc.qt.io/qt-6/qsizepolicy.html#Policy-enum).
  Resize/divider feedback is FIXED — DESIGNER CONFIRMED — 2026-10-14 (§167,
  B88); that confirmation does not close other open layout issues.

## Exact PDF rendering (§§172/173)

Both original and filtered panes display their real source PDFs. Native text
and vector drawing may use AA; bitmap content must not be interpolated or
smoothed. FFPR's rasterized text is bitmap content, not native text eligible
for AA. Saved-file decoding, prepared buffers, zoom painting and minis must
follow the same distinction. Do not repair smoothing by thresholding the view
or by rerunning filtering. Preserve the bitmap's original sample detail when
zooming; changes to display resolution are PDF observation only, never filter
processing. B91 / TODO §179 tracks implementation and actual viewport tests.

§§174/175 choose the simpler display policy: disable ALL PDF-content AA and
bitmap smoothing in both panes. Redraw the actual PDF at the displayed zoom
and device pixel scale so native text/vector geometry gains precision rather
than enlarging a low-resolution prepared raster. Raster samples use nearest
placement. Bound rendering to exposed page/viewport regions; retain the
saved-file source and cached prepared views. This is read-only PDF display,
not filtering, saved-file mutation or an additional threshold. Source colors/
alpha genuinely encoded in a PDF remain visible; disabling AA does not delete
real transparency or convert original color photos into BW.

## Right panel (top to bottom)

Numeric sliders (§178): Threshold (T, 0–255) and Colors (2–256) each use a
standard horizontal QSlider paired with a right-aligned editable QSpinBox
and its native up/down arrows. Both represent one bounded integer with step
1, no wrapping, clear label/buddy and accessible names. The spin box uses
style-derived sizing for the whole range, not a changing width per value.
Dragging, stepping and valid typed values update live through the existing
shared 300ms trailing filter-edit debounce and show `*` immediately
(§§149/183). Keep native keyboard
tracking: no hidden uncommitted numeric value at Save/switch/revert boundaries.
Rapid typing submits only the final debounced recipe; each new bounded value
has one edit path, not duplicated slider/editor processing. Loading, filter
switching, Cancel and Revert synchronize both controls
without creating edits. Disabled/inapplicable settings disable the pair.
Use native theme/layout/HiDPI handling and retain narrow-panel scrolling.

Qt references: [QSpinBox](https://doc.qt.io/qt-6/qspinbox.html),
[keyboard tracking](https://doc.qt.io/qt-6/qabstractspinbox.html#keyboardTracking-prop).

File box (full path, pages, page size, original size — constant for every
filter, §§68/69/73; absurd scan sizes get a Letter/A4 suggestion, never
auto-applied, §74) → Filter row (dropdown fills the row; Revert Changes,
Rename, Copy, Save are icon-only buttons with tooltips, §§109/112/114/120/162,
B51/B86) → Filter
details (`Codec:` first, fixed order every mode, §§72/79/82, B14/B15) →
per-filter controls, each feeding ONLY its filter and grey-but-visible
otherwise: T slider (Simple only, §65, B13), Colors slider (Indexed only,
§67), Lossless checkbox (JPEG2000 only, §100). Strategy, DPI and page size
sit inline with their labels (§128, B59): single shared DPI combo seeded
per preset (rules preview, totals and save, §§83/85, B17), page-size combo
(Original default, §74), Force full-page raster checkbox (§127: ON = page
into one image, OFF = one combined BW image canvas with native text/vectors
above it (§171), flat page-background rectangles below; active filter
follows it, the rest their recipes — toggle re-renders exactly one filter).
§197: all action icons come from one native-theme-first provider, with the
same stock KDE Breeze SVG fallback family when a name/theme is missing.
No hand-drawn rename/revert/zoom or unrelated fallback glyphs; theme/palette
changes refresh icons without touching filtering or selection. Existing
logical icon sizes stay 20px for filter actions and 16px for zoom controls;
Qt renders vectors at the device scale and supplies disabled states.
See `ICONS.md` for exact action names and bundled asset provenance.
The standard document-revert icon (§197, replacing the §162 custom arrow) is enabled only for the
active draft; it restores the saved filter without changing selection or
re-filtering. See `FILTER_LIFECYCLE.md`.

## Filter strip (full window width, below the main row, §§77/96/128)

Rows drag-reorder (§128) with a solid theme insertion bar at the nearest
divider (§139; Qt draws no nearest-gap line in IconMode — researched);
the dropdown holds real filters only, never Original (§140);
the dropdown is rebuilt to the same order and the order persists; dispatch
submits strip order with the selected filter first regardless of position.
Both read `N. label` from the live order (§§133/148); reorder renumbers on
the first post-drop paint, without processing, selection changes, or worker
arrivals. Filter identity and cached thumbnail/recipe/amount/progress belong
to the filter, not its position. The model retains the unnumbered name;
the shared item delegate draws the numbered caption from `QModelIndex.row()`
at paint time. Never bake positional numbers into cached mini pixels. The
dropdown uses the same label formatter and synchronizes on `rowsMoved`;
reordering does not invalidate processing caches or start new work.
This follows Qt's model/view separation: model data stays independent of
its presentation, with custom rendering in the item delegate
([Qt model/view programming](https://doc.qt.io/qtforpython-6.8/overviews/qtwidgets-model-view-programming.html)).
Selected mini: full-rect theme wash, theme caption ink (§§134/139).

Drag ghost (§§144/145/146): render the complete selected mini using the same
item delegate as the strip, including its theme wash, thumbnail, and
caption, then apply a uniform 75% opacity to the whole bitmap. The common
renderer makes it match the selected item without capturing a clipped
viewport or scrollbar pixels. It follows the original grab point throughout
the app window,
including above and below the strip. During an internal filter drag the
whole window accepts the move; pointer X alone selects the nearest vertical
insertion divider in the strip. Pointer Y never changes that target. The
insertion bar stays fully opaque; dropping keeps the moved filter selected
and updates the dropdown/order as usual. Escape or release outside the app
cancels with no reorder. PDF file drops keep their normal open behavior.
Framework guidance recommends a recognizable translucent drag image and
clear destination feedback, without prescribing a universal opacity:
[Apple drag-and-drop HIG](https://developer.apple.com/design/human-interface-guidelines/drag-and-drop).

Ghost appearance, uniform 75% opacity (25% background visible), and removal
of the bottom white band are FIXED — DESIGNER CONFIRMED — 2026-10-13 (§147).
That acceptance is scoped to the ghost, not other DnD/drop behavior (§148).

One row only, with the full item visible and no vertical scroll range
(§§96/145, B28/B72). The view owns one cell size and a non-wrapping horizontal
grid. Its height is the cell height plus Qt's frame and the horizontal
scrollbar's measured height when needed; it updates on resize and style
changes. Never hardcode the entire widget height, shift captions to hide
clipping, or pad a partial screenshot with neutral pixels. Horizontal
scroll is available on overflow. No Original entry — the left pane IS the baseline
(§30, B2). Each mini is an exact composite of what the synced main view
shows through that filter (§48, B7). Minis belong to the FILE: built once,
never cancelled or re-run by clicks (§90, B21). No selection bar or focus
frame — the active filter shows the full theme highlight over the whole
area, caption included (§§96/97/98/134, B29/B32/B64: palette colors, ring
retired).
Progress overlays centered on the mini (§96, B30); per-filter bars are
cost-weighted and start at 0 (§§89/95, B20/B27). Captions: recipe line (§53)
plus measured full-document amount with % (§§55/59/61, B27) — facts from
the saver, never estimates (§122).

§§185/187/190/191 clarify the progress overlay: draw the SAME native Qt progress control
as the default status-bar QProgressBar, not hand-painted groove/chunk/text
rectangles or a custom stylesheet. §187 refines the earlier edge-to-edge
interpretation: both the bar AND its white backing leave STRIP_PADDING
(4 logical pixels) at each cell side so the mini highlight stays visible.
Span the remaining 142px of the reserved 150px cell, not the 120px preview box
or narrower page image. This reuses the existing mini top/bottom padding,
not a new per-control spacing constant; Qt scales logical pixels for HiDPI.
§190 superseded the earlier native-height/2px-white-padding interpretation.
§§198/199 now refine ONLY its enlargement: mini bars use 1.25 times the
default bar's native size-hint height (rounded to logical pixels), and 1.25
times its percentage font size — 25% larger than original, not quarter-size.
The global status
bar remains unchanged. Preserve point-based or pixel-based font sizing and
observe live font changes. Bound oversized heights to the cell's inner height.
Opaque white backing occupies EXACTLY the bar rectangle, including native
rounded corners/groove; no extra white padding on any edge. §191 centers this
rectangle vertically in the ENTIRE mini cell/frame (including captions),
not the preview-image rectangle. Use the delegate's actual cell origin/height
so scroll position, viewport painting and complete drag snapshots agree.
Paint this overlay AFTER the selected-cell wash; the backing stays white on
selected items too. It is a scoped exception to the otherwise transparent
content canvas, not a return to full-cell white backgrounds or selection bars.
At completion both bar and backing disappear without changing cell geometry.
§195 removes redundant "working…" text from pending mini-image and amount
slots, without replacing it by another generic busy label. A native percentage
bar communicates activity; leave unavailable image/amount slots blank until a
real result exists. Retain completed mini/amount pixels while a changed filter
runs; errors and actionable status messages remain explicit. The main preview
header omits unavailable size metadata rather than showing a busy placeholder.

The model carries per-filter progress separately from cached image/caption
pixels. The common item delegate renders the progress control for both the
viewport and the complete selected drag snapshot; the latter still receives
uniform 75% opacity. Use QStyleOptionProgressBar/CE_ProgressBar with the actual
default bar's style, palette, scaled font, direction and formatting. One hidden
formatting template is shared by the delegate, not one QWidget per model row;
it never changes the real status-bar value or consumes input. Theme changes
are observed at paint time. Percentages remain real work progress, never a
cosmetic animation. No filtering, artifact identity, saved-file or debounce
behavior changes.

Qt references: [QStyleOptionProgressBar](https://doc.qt.io/qt-6/qstyleoptionprogressbar.html),
[QProgressBar initStyleOption](https://doc.qt.io/qt-6/qprogressbar.html#initStyleOption).

Saved/live filter states (§149): one prepared filtered PDF supplies the
preview, mini, exact final file size, and exported bytes. First or repeated
selection only displays existing results (or waits for already queued work).
Controls load with signals blocked. All live recipe changes share ONE 300ms
trailing debounce (§183, proposed default), process only
that filter, and append `*` to its mini/dropdown/header until saved or reverted.
Before leaving an unsaved filter, show a Qt modal Save / Save As… / Discard /
Cancel decision; Escape or canceling the name dialog keeps the current filter.
Save As… means a new named filter recipe; PDF Save exports the current real
artifact. File retention/deletion and pending jobs follow `FILTER_LIFECYCLE.md`.
§160 names the discard button **Discard Changes**, regardless of the native
theme's default text. §161 requires canceled mini-click switches to restore
both current item and visible highlight after the full native gesture, not
only the internal active ID. The edited draft and both prepared files stay.
Qt supports this with standard Save/Discard/Cancel roles and an additional
Save As… action ([QMessageBox](https://doc.qt.io/qt-6/qmessagebox.html)).

Reorder identity ownership (§§156/157, B81): the Qt item model is the sole
source of strip order. Never maintain an independently mutable row/ID array
or address cached content by that array's remembered row. Items carry stable
internal UUIDs; content updates find the item by UUID, while the delegate
formats its current row number. The dropdown is a derived view of model order.

One drag controller only: override Qt's `startDrag` hook and let the framework
own press/threshold/gesture-state reset. Do not run a second independent
mouseMove drag beside Qt's default `InternalMove` copy/remove machinery.
Internal payload is the UUID only, not serialized text/icons/old row numbers;
accept it only for this strip's active drag. Drop resolves that UUID's live
row and performs one `moveRow`, with no insertion, duplicate row, source
deletion, filter processing, or content rebuild. Native checks must include
sub-threshold movement, higher-index repeated moves, preserved row count/UUID
set, plain hover after release, and every visible caption after clicking.
See [Qt item-view drag hooks](https://doc.qt.io/qt-6/qabstractitemview.html#startDrag).

Mini geometry/background (§159, B82/B83): top and bottom content padding
share one 4px value. The cell height is the last caption rectangle's end plus
that padding (162px with the current caption layout), not the old 178px with
20px trailing space. Qt size hints still reserve the actual native scrollbar
and frame outside that full viewport row; never crop or hide a vertical range.
The strip's own Base uses the theme's Window ground with a slight darker(105)
shade (for example #efefef → #e4e4e4). Native themes can have nearly-white
Window colors, so using Window unchanged is too subtle. No border is
added. Original/preview panes keep their existing palettes. The shared
delegate and complete 75%-opacity ghost use the same strip ground.

## Status bar and jobs

`filename — N pages (job G)` status, `Page N of M`, global progress bar.
All real filter files are prepared once on open, selected first (§§51/149).
Only actual filter edits authorize new processing; selection and view changes
reuse results (§§47/108/149). Dirty edits are resolved before file-open/close.
Closing mid-processing cancels work and waits asynchronously, never
crashes (§94, B26). Stale "Rendering…" lines settle once idle (§116
follow-up). Temp + persistence split in `PERSISTENCE_AND_TEMP.md` (§123).

## Ruling index (layout-relevant § → topic)

30 strip excludes Original · 43 per-filter bars · 44 process-once ·
47 scroll never dispatches · 48 exact-view minis · 50 navigator dropped ·
51 preview-first · 52 zoom keys · 53 recipe lines · 54 details panel ·
60 pane headers · 61 percents · 65 T feeds Simple · 67 Colors feeds Indexed ·
68/69/73 file box · 71 Prev/Next dropped · 72/79/82 Codec-first details ·
74 page-size default · 76/78/84/86 zoom controls · 77 full-width strip ·
83/85 single DPI · 89/95 progress weights · 90 no selection restarts · 94 safe close ·
96/97/98 strip row, no selection bar, ring · 100 lossless states ·
128 DnD order + inline rows ·
130 combos fit largest item ·
101 grid mirror · 103/127 FFPR ON flattens, OFF keeps text + 1-bit images ·
105 minis never color photos · 106 sizes never blank ·
107 equal panes, no splitter · 108 click isn't recompute · 109/112/114/120
rename/copy/save buttons · 111 preview never empty · 113 preview shows
filter · 115 preview-only status · 116/127 toggle re-renders active filter
only · 117 draggable divider · 118 panel h-scroll · 124 elided headers ·
149 real-file views and dirty Save/Save As/Discard/Cancel · 152 PID temp ownership.

## Issues on this page

B2, B5, B7, B9, B12, B13, B14, B15, B17, B18, B19, B20, B27, B28, B29, B30,
B31, B32, B38, B41, B43, B44, B48, B49, B51, B55, B56, B59, B61 — see
`issues.md` (gated log); substance lives in the sections above. B72 tracks
the unified strip geometry and ghost rendering correction (§145), explicitly
confirmed in §147 on 2026-10-13. B73 tracks immediate post-drop numbering
(§148), explicitly confirmed in §149 on 2026-10-13. B74–B77 track the
single-file result and unsaved-edit lifecycle (§149); see `FILTER_LIFECYCLE.md`.
B81 tracks wrong names after reorder (§§156/157): one Qt drag hook, UUID-only
payload, model-authoritative order, and UUID-addressed item updates above.
FIXED — DESIGNER CONFIRMED — 2026-10-14 (§159). B82/B83 track the equal
top/bottom padding and darker strip ground in §159; these new issues remain
OPEN until their own explicit confirmation.
