# UI layout — main window regions and rules

## Rulings (verbatim)

Exact designer text from `DESIGNER_VERBATIM.md`. Text outside the fenced
quotes is not the designer's.

### This page

**§125** (2026-10-13)

```text
You can move the relevant design rulings to their relevant docs. You can create a main ui layout doc also, rename the file as you feel is best.
```

### Panes and main row

**§22** (2026-10-09)

```text
page zoom, pan, etc is always synced on both panes
```

**§26** (2026-10-09)

```text
the page viewer should be continuous by default, with a gap between paged.  No page list to the left.  Zoom out should aso autowrap to multiple pages per side if it fits in the window width.  Do you follow?
```

**§107** (2026-10-10)

```text
Remove the vertical sizer between the two main previews, not just make it not draggable, that is just wrong.
```

**§117** (2026-10-13)

```text
and the panel width slider is completely wrong, the divider should be adjustable, like the previous preview divider.
```

**§118** (2026-10-13)

```text
If the right panel becomes too small for it's content, it must have a horizontal scroll bar
```

**§124** (2026-10-13)

```text
When the top title above each preview goes beyond the available width, put elipses and hover over full text. Add this as a design ruling.
```

**§188** (2026-10-14)

```text
Also, remove the title for the minis and remove the extra space between the previews and the minis same for the right panel.  Have the same padding for the whole line.  Also, have the same side padding.  Everything is different now and staggered and looks like a mess, poor design and poor modularization.
```

**§60** (2026-10-10)

```text
Above the original and the applied preview, show the relevant information for each, in particular, the filter, dpi, file size, etc.  For the left side, it should show similar to the thumbnails at the bottom for the right side, it should say Original with a new key information, including the file size.
```

**§164** (2026-10-14)

```text
When I zoom in, what happens incorrectly is that sorry, when I zoom out, what happens incorrectly is that since the pages get smaller and smaller and they're supposed to be tiled one beside each other, going from left to right row by row, the page gets left aligned when it should be centered.When I zoom in, what happens incorrectly is that sorry, when I zoom out, what happens incorrectly is that since the pages get smaller and smaller and they're supposed to be tiled one beside each other, going from left to right row by row, the page gets left aligned when it should be centered. However, it does stay vertically centered, which is odd. It should stay both vertically centered and horizontally centered when there's no other pages, when there's one page. If there's two pages, then the layout of two pages should be horizontally centered, etcetera. It should not just go off to the left as if it had other pages when it doesn't.
```

### Exact display

**§173** (2026-10-14)

```text
Previews of original and filters must be exact! No additional filtering, smoothing, etc.    AA can be used on text and vector images of course, but never on anything converted to bitmaps.
```

**§174** (2026-10-14)

```text
you can leave fonts and vectors without AA, just show their higher precision shapes when I zoom in so I can see the diff between what is bitmap and vector.
```

**§175** (2026-10-14)

```text
In otherwises, if it's simpler to drop all AA and smoothing for display, that is ok, I rather precise exat rendering regardless.  So this might be the best solutions overall and addresses the root cuase of the problem.
```

### Right panel

**§100** (2026-10-10)

```text
Also, add a checkbox for lossless.  If the algorithm doesn't have the choice, keep it, but make it grey with the correct otpion, it should always be show for each filter type on the right side.
```

**§178** (2026-10-14)

```text
Also, make the sliders with a number that can be edited and a spinner or something similar, what is modern best practices for designs of such inputs?
```

**§183** (2026-10-14)

```text
In the low color versions, colors are getting incorrectly converted to white instead of their closest colors. Also, when using the spinner, after a debounce, a rerender should be triggered, same for the sliders or any other change.  We should have one global debouce for this.  What do you suggest as a debounce time?
```

### Filter strip and minis

**§77** (2026-10-10)

```text
also make the tumbnail stip go full width, right side panel stopping above with it's own scroll bar if overflow.
```

**§96** (2026-10-10)

```text
The preview thumnail section below should always be full heigh, no vertical scroll bar. There is a blue bar under the selected filter which you should remove.  The progress bar should be layed over the middle of the thumbnail and remove the progress bar reserved space below the thumbnail.  Also, put the save and X button on the same line as zoom and put them less wide.  I still don't know what the X button does, please explain once you are done your work.  Create each of these as issues and I will confirm once they can be marked as completed.
```

**§48** (2026-10-10)

```text
Still wrong! Thumbnails should be a mini version of exactly the current view of the larger window.  Why is this not clear?  If the original and preview windows (always synced view) show three pages wide and 4 pages high with the last page have cut, each preview shows exactly that from it's own filter view (internal, no shown, file preprocessed in bg at the start or from the latest change).  This seems simple and exacly derived from my previous rulings.
```

**§145** (2026-10-13)

```text
There is a weird transparent white bar across the bottom of the ghost, it comes from behind the bottom scrollbar I think.  The previous worker had alot of trouble with a similar blue selection bar below it before and a vertical scrollbar that was incorrect.  I think the previous worker did alot of hacks and did not follow modern best practices for QT and GUI, please review to solve the root causes, and not just patch onto of bad code and bad design.  You can review the docs, my rulings, issues, etc for more context.
```

**§159** (2026-10-14)

```text
Ok, seems good, you can mark this as fixed.  Next issue.  Your previous fix to the mini hightlight and vertical scroll added back the white space gap at the bottom of the minis strip.  I want the same gap as at the top of the minis.  Also, the background of the minis should be a bit darker so that I can see the difference between the white mini page outline and the background.
```

**§288** (2026-10-13)

```text
Now, the last row of the text is trucated by the view, don't you see this?  This is terribly bad!  Are you even looking at the GUI results?  
```

### Order and drag-and-drop

**§128** (2026-10-13)

```text
Again, how is it possible that FFPR is 10x smaller than without. Explain to me. I made an identical filter with both variations. Also, add a design rulings: I want the filters to be DnD orderable in the bottom list of minis and the dropdown follows the same order and the processing follows the same order, except for the one currently selected which is always first priority regardless of ordering. Also, put Strategy, dpi and page size on the same row/line as the lables please.
```

**§133** (2026-10-13)

```text
Put the sequence number in front of the filter, eg "1. ", "2. ", both in the minis and in the dropdown.
```

**§134** (2026-10-13)

```text
Minis should be fully highlighted with light blue with the dark blue (both per theme deifnition, not hardcoded), for the whole area, including the text below them. Also, why is the DnD bar and hollow rectangle?? That certainly doesn't follow modern UI best practices, I have never seen that. How does the default behavior end up looking like that?
```

**§139** (2026-10-13)

```text
Ok, this highlight is good.  you can document and harden the test cases for this.  Also make a full suite of test cases that run automatically, so you don't have to run each one at a time.  Also, next issue, the DnD does NOT show the drop indicator vertical bar, this is wrong, I already defined this many times.
```

**§140** (2026-10-13)

```text
Remove the "Original" option from the filter dropdown, that is NOT an option, it is the default for the left side preview, always.
```

**§141** (2026-10-13)

```text
Also, typical DnD should have some transparency, what is modern GUI best ptractices?
```

```text
NO! That is not correct, the whole ghost should have the same transparency percentage.  What you did is incorrect, with some parts being fully transparent, and other full opaque and I don't know what oyu did with letters, but that is definately incorrect and not modern best practices.  Did you even look at the transparency render during a DnD ghost operation???
```

```text
tell me what you did for transparency, because it just doesn't work
```

**§143** (2026-10-13)

```text
No, not good, the ghost is just a light blue rectangle, not the highlighted blue mini, this is a fail, reread my requests and design rulings, this is simple and obvious, think of what a GUI user expects!
```

**§144** (2026-10-13)

```text
The DnD is good, but a little light, try 65%? Or what is modern best practices for transparency in modern GUI?  Also, let the DnD go outside of the mini strip, same transparency, but snap the drop to the nearest vertical drop point regardless of where it is vertically.
```

**§146** (2026-10-13)

```text
Also, change the transparency to 75% for the DnD ghost please.
```

**§148** (2026-10-13)

```text
When I DnD a mini, the dropped numbers don't renumber immediately, only if there is some reprocessing or miss processing that gets triggered, this is wrong and bad design, please review for the root cause and fix the design properly.
```

### Progress overlay and pending labels

**§185** (2026-10-14)

```text
I want the minis progress bars to follow the same style as the default progress bar and to span the full width of the minis reserved width (larger than the mini image) and also to have an opaque white background behind to make the progress bars visible.  Follow modern GUI best practices.
```

**§187** (2026-10-14)

```text
Obviously you need to have some padding between the progress bar and the edge of the minis to permit some highlight to show.  What is the common padding we are using?  I see a bit of padding above and below.
```

**§191** (2026-10-14)

```text
And center it within the whole box of the mini, not just the image part.  Centered within the frame height of the mini.
```

**§198** (2026-10-14)

```text
I previously asked to increase the progress bar by 50%, I want to change that to only 25% of it's original size.
```

**§199** (2026-10-14, selected option)

```text
25% larger — 1.25× original
```

**§195** (2026-10-14)

```text
Also, drop the "working..." label, it's obvious it's working by the progress bar...
```

## Window regions

The main window has exactly four regions.

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
4px wide.

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
  standard theme/fallback magnifiers (§197); zoom never reprocesses filters.
  Native PDF shapes redraw at device resolution without AA (§§174/175). Switching filters never moves the view (§101: the
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
  B48/B96).
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

## Exact PDF rendering (§§173–175)

Both original and filtered panes display their real saved PDFs with ALL
PDF-content AA and bitmap smoothing disabled; FFPR's rasterized text is
bitmap content. Saved-file decoding, prepared buffers, zoom painting and minis
follow the same rule. Do not repair smoothing by thresholding the view or by
rerunning filtering; changes to display resolution are PDF observation only.
Redraw the actual PDF at the displayed zoom
and device pixel scale so native text/vector geometry gains precision rather
than enlarging a low-resolution prepared raster. Raster samples use nearest
placement. Bound rendering to exposed page/viewport regions; retain the
saved-file source and cached prepared views. This is read-only PDF display,
not filtering, saved-file mutation or an additional threshold. Source colors/
alpha genuinely encoded in a PDF remain visible; disabling AA does not delete
real transparency or convert original color photos into BW.

## Right panel (top to bottom)

The **Image compression** dropdown sits immediately after the filter
name/actions, before the recipe readout (§§203/204). Six choices: JBIG2 BW,
JBIG2 Color, Packed BW, Indexed color, JPEG2000, JPEG. Packed BW and Indexed
color are representation labels because Best can store Brotli (§§255/256);
their internal mode IDs and saved recipes stay compatible. Every filter can
select any choice; its seed preset does not lock controls. Label the threshold dropdown
**Threshold method:** (not Strategy): it includes automatic and manual methods.
Existing 4px spacing, native overflow, header/frame alignment and dirty-edit
transactions apply. Readouts and control enabled/fixed states derive from the
actual saved/draft recipe.
**PDF stream compression:** is a separate dropdown (§205). **Best
(Zopfli/Brotli)**, the default for every app filter (§257), covers native AND
packed-image streams, excluding J* payloads and leaving sample/quality
settings unchanged (§§255/256); the fixed Flate, Zopfli and Brotli choices
compress native streams only. The Brotli reader explanation is native
tooltip/accessibility/keyboard help, with no inline label (§253); the visible
choice reads "Brotli (limited support)". Use the shared
[tooltip convention](TOOLTIPS.md), not a modal on every edit. The declaration checkbox is visible for Brotli and
Best only, off by
default, labeled **Include Brotli extension declaration (Compatibility)**
(§§251/252).

The three fixed stream choices remain beside Best; aligning them with the
encoder policy (§213, `COMPRESSION.md`) is TODO §217.

Controls that do not apply to the current choice stay visible but greyed
(§100).

Force full-page raster is enabled for every image codec (§224), and Page
size is enabled when FFPR is ON. The flag remains effective across BW/color
codec changes, appears in mini/readout descriptions, and participates in the
same dirty/debounce/Save/Revert lifecycle. All built-in raster defaults are
300 DPI, and DPI stays editable (§§225/226). FFPR color readouts must not
claim text/vectors are kept.

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
B51/B86) → Image compression / PDF streams (§§203–205) → Filter
details (`Codec:` first, fixed order every mode, §§72/79/82, B14/B15) →
per-filter controls, each feeding ONLY its filter and grey-but-visible
otherwise: T slider (Simple only, both BW encoders, §65, B13), Colors slider
(Flate palette and colored JBIG2, §§67/203), Lossless checkbox (JPEG2000 only,
§100). Threshold method, DPI and page size
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
The standard document-revert icon (§§162/197) is enabled only for the
active draft; it restores the saved filter without changing selection or
re-filtering. See `FILTER_LIFECYCLE.md`.

## Icon Lab (separate review window, §200)

View → Icon Lab… opens one reusable modeless dialog; it does not change the
main-region layout or app icons. Columns compare Nuvola, Oxygen, GNOME Classic
and Breeze, with permanent family/action/variant codes on every radio option.
Each row is one action with an exclusive cross-family choice. Show actual
16px/20px app-size enabled/disabled controls plus a 32px inspection preview.
The table stretches its four columns at normal width and scrolls natively
when narrow/short; action/family headers and the always-visible choice summary
make the mapping readable. Background selection affects the lab only.
Copy choices produces a per-action text reply; no Apply button or automatic
settings/filter/selection/job change. Source names are visible and codes never
depend on row order. See `ICON_LAB.md` for assets, licenses and acceptance.

## Filter strip (full window width, below the main row, §§77/96/128)

Rows drag-reorder (§128) with a solid theme insertion bar at the nearest
divider (§139; Qt draws no nearest-gap line in IconMode);
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

One row only, with the full item visible and no vertical scroll range
(§§96/145/288, B28/B72). The view owns one cell size and a non-wrapping horizontal
grid. Its height is the cell height plus Qt's frame and the horizontal
scrollbar's measured height when needed; it updates on resize and style
changes. Never hardcode the entire widget height, shift captions to hide
clipping, or pad a partial screenshot with neutral pixels. Horizontal
scroll is available on overflow. No Original entry — the left pane IS the baseline
(§140, B2). Each mini is an exact composite of what the synced main view
shows through that filter (§48, B7). Minis belong to the FILE: built once,
never cancelled or re-run by clicks (§90, B21). No selection bar or focus
frame — the active filter shows the full theme highlight over the whole
area, caption included (§§96/97/98/134, B29/B32/B64: palette colors, ring
retired).
Progress overlays centered on the mini (§96, B30); per-filter bars are
cost-weighted and start at 0 (§§89/95, B20/B27). Captions: recipe line (§53)
plus measured full-document amount with % (§§55/59/61, B27) — facts from
the saver, never estimates (§122).

The progress overlay (§§185/187/190/191) draws the SAME native Qt progress
control as the default status-bar QProgressBar, not hand-painted groove/chunk/text
rectangles or a custom stylesheet. Both the bar AND its white backing leave
STRIP_PADDING (4 logical pixels) at each cell side so the mini highlight stays
visible (§187).
Span the remaining 142px of the reserved 150px cell, not the 120px preview box
or narrower page image. This reuses the existing mini top/bottom padding,
not a new per-control spacing constant; Qt scales logical pixels for HiDPI.
Mini bars use 1.25 times the default bar's native size-hint height (rounded
to logical pixels) and 1.25 times its percentage font size (§§198/199).
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
that padding (162px with the current caption layout). Qt size hints still reserve the actual native scrollbar
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
crashes (§94, B26). Stale "Rendering…" status lines clear once idle (§116). Temp + persistence split in `PERSISTENCE_AND_TEMP.md` (§123).

## Design traps and failed attempts

- **Hiding clipped captions.** Hardcoding the strip height or moving captions
  up to dodge the scrollbar cut the size line in half (§288). The cell height
  comes from the caption rectangles; Qt reserves the scrollbar outside it.
- **Row numbers baked into cached mini pixels.** After a reorder, minis flashed
  old names (B81). The delegate draws `N. label` from the live row at paint time.
- **A second drag controller.** A custom mouse-move drag beside Qt's
  `InternalMove` duplicated or lost rows (B81). Use one `startDrag` override
  and one `moveRow`.
- **A ghost captured from the viewport.** It picked up scrollbar pixels as a
  white band (§145). Render the ghost with the item delegate.
- **Hand-painted progress bars.** Custom groove and chunk drawing never matched
  the theme (§185). Draw the native control through `QStyleOptionProgressBar`.
- **Display updates feeding the splitter.** Elided headers that published
  shrinking minimum widths made the divider drift for seconds after a resize
  (§166, B88).
- **Thresholding the view to hide smoothing.** The grey edges came from display
  interpolation (§172); the fix is disabling AA and smoothing, never filtering
  the view.
