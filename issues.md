# ISSUES — designer complaint log (confirmation-gated)

Rule (designer §90): every past malfunction complaint is listed here, numbered.
An item is crossed out ONLY after the designer confirms the fix. Fixed in code
but unconfirmed stays OPEN. Verbatim rulings live in
`docs/DESIGNER_VERBATIM.md` (§ numbers below); implementation notes in
`docs/TODO.md`.

Status convention (§147): `OPEN` includes implemented-but-unconfirmed fixes.
`FIXED — DESIGNER CONFIRMED — YYYY-MM-DD` records explicit designer acceptance,
its local date (America/New_York), and the confirming verbatim ruling. Tests
and worker completion are not acceptance. A mixed-scope issue stays OPEN for
unconfirmed parts; only its explicitly accepted component is marked fixed.

Older implementation notes below are dated history, not current canon. The
§§149–155 audit and `docs/FILTER_LIFECYCLE.md` supersede split preview/mini/
estimate jobs, two-slot caches, and worker-added session directories. New
repairs remain OPEN awaiting explicit designer confirmation.

Historical numbering note (audit 2026-10-15): B39 has two same-title entries
already present in checkpoint `8d7f095`. Do not silently renumber the log or
interpret this duplication as a second designer confirmation. New issue IDs
continue above the highest existing ID.

## B1 — OPEN — process closed by itself (§45)
Symptom: the app vanished after launch. Cause found: the launcher command
timed out and took the app with it. Since fixed by detached launches
(`setsid` + `disown`); standing relaunch rule is §62.

## B2 — OPEN — Original stuck in the filter strip (§30)
Symptom: baseline preset rendered as a filter mini. Fixed: strip shows only
real filters (preset combo keeps all modes for Save).

## B3 — OPEN — UI froze during previews (§37)
Symptom: whole app locked while thumbnails rendered. Fixed: all heavy work
in spawn-context background processes (half-core cap); pan/zoom is pure view.

## B4 — OPEN — click restarted all processing (§44)
Symptom: clicking a filter preview reprocessed everything. Fixed: process-once
cache keyed on file identity + spec; unchanged clicks switch panes instantly.

## B5 — OPEN — truncated half-page minis (§45)
Symptom: strip previews showed only the top slice. Cause: viewport crop taken
before layout. Superseded by the §48 exact-view redesign below.

## B6 — OPEN — reprocessing on scroll (§47)
Symptom: scrolling re-ran background jobs. Fixed: scroll/pan/zoom/page turns
only reframe minis from cache; jobs run on file/spec change alone.

## B7 — OPEN — wrong thumbnail content (§48)
Symptom: minis were baseline crops, not the filter's own view. Fixed: every
preset × every page preprocessed once; each mini composites exactly the
synced main-view framing from its own filter's pages.

## B8 — OPEN — right preview updated last (§51)
Symptom: on open, the main preview finished after everything else. Fixed: the
active filter's preview pages render first, ahead of minis and amounts.

## B9 — OPEN — nothing was keyboard-zoomable (§52)
Symptom: no keypress zoomed. Fixed: Ctrl+Plus / Ctrl+Minus / Ctrl+0, synced
panes, plus zoom toolbar and editable zoom combo (§§76/78/86).

## B10 — OPEN — BW saved as PNG, not JBIG2 (§55)
Symptom: the ruled JBIG2 path was never wired. Fixed: real JBIG2 embedding
with per-stream test-decode; undecodable pages take 1-bit PNG (logged).

## B11 — OPEN — JPEG2000 mini crashed silently (§56 wiring)
Symptom: processing looked stalled at 100% with idle CPU and dead minis.
Cause: the JPX mini path called the JPEG preview (throws); the worker
swallowed it. Fixed the branch; worker failures now log warnings.

## B12 — OPEN — Prev/Next did nothing (§58)
Symptom: dead buttons (stride math + grid same-row targets). Fixed with
item-position scrolling; buttons later dropped entirely (§71) for scrollbars
+ PgUp/PgDn.

## B13 — OPEN — threshold slider changed nothing (§65)
Symptom: dragging T under Otsu re-rendered identical pixels, looking dead.
Fixed: T enables for Simple only (tooltip says so); percents round (§61/65).

## B14 — OPEN — codec missing on the right (§72)
Symptom: JPEG2000/JPEG details never named the codec outright. Fixed:
explicit `Codec:` first line in all modes (unified order under §82).

## B15 — OPEN — Encode vs Codec incoherence (§79)
Symptom: BW said Encode while color said Codec. Fixed: one `Codec:` label,
first line, every mode.

## B16 — OPEN — Flate streams shifted a byte (§80)
Symptom: Flate payloads carried PNG filter bytes with no predictor declared.
Fixed at the foundation (raw rows) with a decode-roundtrip test.

## B17 — OPEN — two different DPI values (§83)
Symptom: preset DPI was decoration while the combo did the work. Fixed: the
preset seeds the single shared combo, which rules preview, totals and save.

## B18 — OPEN — theme-roulette buttons (§84)
Symptom: magnifier icons depended on the desktop theme. Fixed: drawn in code
(`_zoom_icon`), identical everywhere.

## B19 — OPEN — Cancel looked like Undo (§85)
Symptom: X button read as undo-without-a-target. Fixed: Cancel enables only
while a save runs (it stops saves; ESC idles quietly otherwise).

## B20 — OPEN — bars parked at 50% (§89)
Symptom: fast minis finished before slow amounts started. Fixed: one
interleaved batch so each bar advances on its own completions.

## B21 — OPEN — right-filter click reprocessed left filters (§90)
Symptom: choosing a far-right filter restarted the left filters' in-flight
work (their minis/amounts visibly reset). Fixed: two job slots — content
work is never cancelled by a preview-only follow-up; clicks during initial
load reuse the running job instead of restarting it.

## B22 — OPEN — terrible default demo PDF (§§27/31)
Symptom: synthetic demo file as the default document. Fixed: photo-heavy
`examples/images.pdf` default (plus last-file reopen under §91).

## B23 — OPEN — last-file reopen opened test garbage (§§91/93)
Symptom: bare launch opened `/tmp/pytest-*/m.pdf` instead of the last real
file. First fix attempt (conftest `setdefault`) SILENTLY FAILED: this shell
pre-exports `XDG_CONFIG_HOME`, so the guard never engaged — proven by config
checksum changing across a suite run. Real fix: conftest overrides it
unconditionally (test processes only); checksum now identical across a full
49-test run. Awaiting designer confirmation.

## B24 — OPEN — right-pane zoom never reframed minis (§92)
Symptom: minis stuck on an old view after zooming/scrolling the right pane.
Cause: synced peer zooms never emitted `changed`, so the trailing reframe
debounce never saw the last view change. Fixed: `_pull` notifies; debounce
confirmed trailing-edge (fires after the last change).

## B25 — OPEN — palette bytes overflow past 85 entries (found in live log)
Symptom: `RuntimeWarning: overflow` in the log; palettes with 86+ entries
embedded wrong colors. Cause: numpy uint8 index arithmetic wrapped.
Fixed: `int()` conversion before slicing the palette.

## B26 — OPEN — closing mid-processing must never crash (§94)
Symptom: closing the window while workers run risked `QThread: Destroyed
while thread is still running` and pool-teardown races. Fixed: `closeEvent`
cancels all tokens, joins workers, closes the document; covered by a
close-mid-processing test.

## B28 — OPEN — strip must be one full row, no vscroll (§96)
Shipped: fixed height, vertical scrollbar off, horizontal on overflow.

## B29 — OPEN — kill the selection bar, all of it (§§96/97)
First pass removed only the blue background; the standard focus frame
survived (visible only while focused — exactly as reported). Fixed: the
strip takes no keyboard focus at all (mouse selection unaffected).

## B32 — OPEN — ring instead of bar (§98)
The bar is gone, but dropping ALL selection marking would break the modern
pattern for a reason: the strip must always show which filter the right pane
is displaying (plus keyboard position). The pattern is a ring ON the item,
not a bar below it: the selected mini now paints a 2px theme-highlight frame
around its preview box, drawn by us so no style or focus change can alter it.

## B30 — OPEN — progress overlaid mid-thumbnail (§96)
Shipped: centered overlay plate, reserved space below deleted, icons shorter.
§§185/187/B95 tighten appearance: native default progress control, reserved
mini width less the shared 4px side padding and opaque white backing, above
selection. The old hand-painted
104×12px bar did not actually implement the claimed native style.

## B31 — OPEN — one compact action row (§96)
Shipped: zoom-out / live % / zoom-in + separator + Save + X in a single
toolbar; X stops the running save only (disabled otherwise).

## B27 — OPEN — bars start at 50% again (§95)
Symptom: per-filter bars jump to 50% with the first mini and sit through the
slow amounts. Cause: the 50/50 phase split weighed fast minis like slow
encodings. Fixed: cost-weighted completions (15/85, current-job arrivals
only) via a unit-tested `filter_progress` — bars always start at 0.

## B33 — OPEN — preview grid out of sync (§101)
Symptom: zoomed out, the original wraps to side-by-side pages but the right
preview does not follow. Cause: downsampled color previews have smaller dims,
so the right pane computed its own grid. Fixed: the preview mirrors the
baseline grid exactly (`layout_from` — positions, columns, zoom source).

## B34 — OPEN — zoom resets + processing on filter switch (§101)
Symptom: changing filters reset the zoom and showed processing. Cause: same
grid mismatch reflowed the view on every switch. Fixed by the §101 mirror —
switches can't move the view; only the zoom controls reset it. First-view
preview renders once per spec (process-once); repeats hit cache.

## B35 — OPEN — palette enum crashed opens, popup buried it (§102)
Symptom: opening any file failed with a popup; nothing about the cause in
the log. Cause: `QPalette.Mid` exists on the class, not the instance — and
`open_file` showed only a QMessageBox, swallowing the traceback (which also
hung the headless suite on the modal). Fixed: class enum access; `open_file`
logs the full traceback to stdout first.

## B38 — OPEN — panes drifted unequal, divider invisible (§104)
Symptom: no visible divider; dragging left unequal panes. Fixed: 6px styled
divider handle; any drag snaps back to equal halves (single-pane mode
excluded).

## B39 — OPEN — raster toggle churned all minis (§105)
Symptom: flipping force-raster visibly reprocessed every BW thumbnail.
First fix (minis follow the UI checkbox) was wrong — it also painted BW
minis as full-color photos on text pages. Real fix: minis ALWAYS show the
rasterized filter recipe (achromatic for BW); only preview, amounts and save
follow the checkbox. Pinned by a filter-set test covering every preset.

## B41 — OPEN — BW minis showed color photos (§105 follow-up)
Symptom: BW thumbnails rendered the original color page. Cause: mixed-mode
mini logic returned the RGB original for text pages. Fixed as above; new
`test_filter_set_covers_every_preset` asserts every strip preset renders its
own kind (BW achromatic), previews, and measures.

## B40 — OPEN — sizes blank on toggle (§106)
Symptom: every amount blanked to sizing… on toggle, even when identical.
Cause: reframe popped displayed values for missing keys. Fixed architecture:
displayed minis/amounts are stable store views — recomputes update them in
place, only a new file clears (stale-while-revalidate, bars signal work).

## B43 — OPEN — splitter had to go (§107)
Symptom: a draggable divider between panes that could never stay put.
Fixed: deleted — fixed equal layout, direction flips per view mode.

## B44 — OPEN — clicks looked like recompute (§108)
Symptom: clicking a mini visibly reflashed the preview. Jobs never reran
(§44 held, log-proven); the pane rebuilt identical pixmaps. Fixed: panes
skip the rebuild when already showing the key.

## B45 — OPEN — right preview sits empty (§111)
Symptom: big right pane blank, especially right after open. The baseline
rendered instantly on the left while the right waited for the first
background preview. Fixed: right pane shows baseline immediately; the real
filter preview replaces it the moment it lands.

## B46 — OPEN — BW mini, original-looking preview (§113)
Symptom: clicking a BW mini showed the original in the big preview. Cause:
mixed-mode preview rendered text pages as original while minis showed the
thresholded filter. Fixed: the right pane always shows the full filter
effect; force left the preview identity (toggle never rebuilds it).

## B36 — OPEN — raster was global, on by default (§103)
Symptom: force-raster flattened text everywhere unless unticked. Fixed: per
filter, default off except `BW · Fast Draft`; preset switch syncs the box.

## B37 — OPEN — raster toggle recalculated nothing (§103)
Symptom: flipping force-raster left previews and amounts stale. Cause:
previews/amounts/keys ignored the flag. Fixed: the flag is in the spec,
cache keys, mini keys and estimator; mixed mode (text passes, images
compress) shared by save, preview and estimator alike.
Update (2026-10-13): superseded by B47 below — later rulings (§§105/106/113
+ repeat complaint) killed every strip/preview recalc on toggle; only Save
follows the checkbox now.

## B39 — OPEN — raster toggle churned all minis (§105)
Symptom: flipping force-raster visibly reprocessed every BW thumbnail.
First fix (minis follow the UI checkbox) was wrong — it also painted BW
minis as full-color photos on text pages. Real fix: minis ALWAYS show the
rasterized filter recipe (achromatic for BW); only preview, amounts and save
follow the checkbox. Pinned by a filter-set test covering every preset.
Update (2026-10-13): amounts left the checkbox too (§116/B47) — minis,
previews AND amounts are force-independent; only Save follows it.

## B47 — OPEN — raster toggle resized all BW minis (§116)
Symptom: flipping force-raster recomputed every BW amount (repeat
complaint). Cause: the BW est cache key still carried the checkbox flag,
so each toggle was a mass cache miss. Fixed: amounts follow each filter's
own recipe force (only BW · Fast Draft forces); the checkbox arms Save and
refreshes details only — zero jobs dispatched (pinned by a toggle test that
fails pre-fix). Follow-up in the same fix: a same-key preview arrival or a
mini-only top-up could leave the "Rendering…" status up forever; the line
now settles once nothing is in flight and the current preview is cached.

## B48 — OPEN — panel-width slider instead of divider (§117)
Symptom: right-panel width via a slider. Fixed: slider deleted; the previews
block and the right panel sit in a draggable non-collapsible QSplitter with
a visible 8px handle. The two panes themselves stay locked equal (§107 and
B43 hold — nothing splits them).

## B50 — DONE — raster-vs-text sizes questioned (§119)
Designer asked why forced raster can be smaller; ruled: no benchmark
needed — the user chooses via the checkbox, which Save honors
(ON flattens, OFF passes text through). No behavior change.

## B49 — OPEN — squeezed right panel clipped content (§118)
Symptom: divider dragged below content width clipped the panel (horizontal
scrollbar forced off). Fixed: `ScrollBarAsNeeded` — the bar appears only
when the content overflows.

## B51 — OPEN — rename icon + icon-only filter buttons (§120)
Original symptom: rename glyph questioned; words on Rename/Copy/Save buttons.
The initial custom I-beam/floppy implementation misread a STANDARD-icon
question as a custom-artwork requirement. §197 approves native-theme lookup
with stock Breeze fallbacks; B102 / TODO §201 supersede those drawings.
Buttons remain icon-only with tooltips. Not designer-confirmed fixed.

## B52 — OPEN — mixed sizes questioned + zoomed preview text wrong (§121)
Two questions on `images.pdf`: (1) forced raster far smaller than
text-keeping — measured honest (file is 94% photo pixels: 129 KB kept
JPEGs + 42 KB masks vs 3.2 KB whole-page JBIG2; tables in the doc);
(2) zoomed mixed preview text unlike the original — CONFIRMED bug: the
preview thresholds everything while mixed save keeps vector text (proven:
text extractable from mixed output, preview pixels pure 0/255).
Full analysis with options in `docs/MIXED_MODE_ANALYSIS.md`; also found:
the mixed/color estimators ignore soft-mask bytes (~24% undercount here).
No code changed — awaiting the designer's option ruling.
Update (2026-10-13): that historical wait is superseded by §§126/127/149.
The real-file flow now reads the preserved text and masks directly; independent
preview transforms and mask-blind estimators are removed. Implementation is
verified, but this issue remains OPEN pending designer confirmation.

## B53 — OPEN — single path: save temp, everything reads it back (§122)
Ruling: one path only — saver writes temp files; preview, minis and
amounts all read back from them; Save copies the temp. Documented in
`docs/ARCHITECTURE.md` (+ `DESIGN.md` pointer). Implemented 2026-10-13 under
§149: one real saver, prepared saved-file pixels, exact whole-file measurement,
and byte-copy export. The formerly stated design questions were settled by
§127 and reiterated by §149. Full suite 124 passed; current B74–B77 coverage
checks actual files/call counts. OPEN means awaiting designer confirmation.

## B54 — OPEN — OS temp dir via Qt + persistence/temp docs (§123)
Symptom: app scratch (and the planned single-path saver temps) defaulted
to the repo `./.tmp/` on every OS. Fixed: `ui_qt/paths.py` resolves the OS
standard temp via `QStandardPaths.TempLocation` (verified `/tmp` on Linux;
Windows/macOS per Qt), with a stdlib fallback; stale temps swept at
startup. `run.sh` log follows `TMPDIR`. New `docs/PERSISTENCE_AND_TEMP.md`
(temp vs QSettings persistence vs repo `./.tmp/` dev artifacts, which stay
put deliberately), cross-ref'd from ARCHITECTURE/DESIGN.
Update (2026-10-13, §§152/153/155): actual runtime files now live under the
GUI PID and filter UUID, with a held process lock, ownership-safe cleanup,
and normal-exit deletion. There is no additional session-history layer.

## B56 — OPEN — rulings into relevant docs + UI layout doc (§125)
Symptom: layout rulings scattered across logs. Fixed: new
`docs/UI_LAYOUT.md` (regions, divider, strip, headers, controls, ruling
index); `DESIGN.md` stale render paragraph replaced with topical-doc
pointers; `ARCHITECTURE.md` background-jobs section added. Quote log and
work history untouched.

## B55 — OPEN — elided pane titles with hover text (§124)
Symptom: long pane titles overflowed their half. Fixed: single-line
headers elide with "…" past the available width; hovering shows the full
text (full text kept in a property, re-elided on resize).

## B57 — OPEN — mixed path was never specified: removed, option parked (§126)
Symptom: a "mixed" text-pass-through save hid behind the raster checkbox —
never specified, never offered, the source of the FFPR size confusion.
Fixed: mixed branch, checkbox, recipe flags and toggle machinery all
removed; every BW page flattens, always; stale saved `force_raster` values
are ignored. The idea survives only as the unimplemented proposal in
`docs/MIXED_MODE_OPTION.md` (vector pass-through vs JBIG2-text-layer).

## B58 — OPEN — FFPR is optimize-images vs full-page-image (§127)
Correction of B57's overreach (checkbox wrongly removed): FFPR stays —
ON flattens the page to one image, OFF keeps vector text and 1-bits
embedded images in place (never color JPEGs in BW output; the old
mixed-JPEG behavior is gone for good). Preview/minis composite crisp text
with thresholded images via one shared helper; toggle re-renders exactly
the active filter. Also fixed while here: 1-bit Flate row-stride
validation (3 images silently kept originals).

## B59 — OPEN — DnD strip order + inline control rows (§128)
Symptom: fixed filter order; Strategy/DPI/page-size stacked above their
controls. Fixed: strip rows drag-reorder (dropdown rebuilt to match, order
persisted, copies land last); dispatch submits strip order with the
selected filter first. Each control sits inline with its label. Follow-up
fix: row→combo lookup by id — PRESETS-index mapping desynced post-reorder
and crashed via handler ping-pong (found as a suite segfault). Explicit
`_StripList` press-drag-drop replaced InternalMove (never fired); drag
start/drop now logged for live diagnosis. Process lesson logged in TODO-131:
verify old-gone/new-pid on every relaunch (one round silently missed).
Follow-up (§132): every drag died on `ImportError: QMimeData` — it lives
in QtCore, not QtGui (found in the live log, fixed, suite green).

## B60 — OPEN — DPI applies to every image transform (§129)
Symptom: images transformed at native resolution (OFF path) or capped
downscale-only with a page-size heuristic (color path) — DPI ignored or
partial. Fixed: displayed-inches × setting-DPI via one Lanczos choke point
(`force_to_dpi`, original space, up and down); `jpx_encode` presized flag
ends double-scaling; estimators replay with display sizes. Research:
Lanczos already the codebase standard, now enforced. Rules/flows/benchmarks
in `docs/COMPRESSION.md`.
Audit update (2026-10-13, §150): small-image/alpha skips, preserved 1-bit
sources, and keep-original-if-smaller remain exceptions to §129's broad
exact-DPI rule. Prior documentation is not approval. B60 stays OPEN for
this policy discrepancy; the real-file flow does not silently change codecs.

## B61 — OPEN — dropdowns fit largest item + issues on topic pages (§130)
Symptom: right-pane dropdowns not sized to content. Fixed: `_fit_combo`
minimum-widths to the widest entry; tooltip carries the full text (Qt
clips narrow closed displays without ellipsis — verified). Also per this
ruling: every issue now listed on its topic doc page (`issues.md` stays
the confirmation-gated log).

## B62 — OPEN — clicking a mini moved other filters' sizes (§131)
Symptom: switching to an FFPR filter re-seeded the shared DPI combo and
every other BW amount recomputed at the new DPI. Cause: estimates keyed
the combo DPI for ALL filters (color already did active-UI/rest-recipe).
Fixed the same way — per-pid estimate DPI frozen per job; a preset switch
now recomputes nothing but the preview. Pinned by a click-stability test.

## B63 — OPEN — filter sequence numbers in minis + dropdown (§133)
Symptom: no visible filter ordering. Fixed: `N. label` from the live strip
order in both mini captions and dropdown (reorder renumbers); Original
stays unnumbered. Pinned by a numbering test.

## B64 — OPEN — full theme highlight + standard drop line (§134)
Symptom: selected mini marked by a painted ring only; DnD showed a custom
hollow-rectangle band. Fixed: style paints the whole selected area
(transparent icon ground, palette Highlight/HighlightedText ink, ring
retired); rubber band deleted so the style draws the insertion line;
strip movement off Static (which silently unwires framework drags).

## B65 — OPEN — screenshot canon, never program blind (§137)
Symptom: GUI work shipped without looking at it. Fixed: canon rule (§5b
in `DEVELOPER_GUIDELINES.md`) — offscreen shots in the tests' virtual
framebuffer captured and actually viewed after every UI-visible change,
with a review checklist; tests and shots cover each other's blind spots.

## B66 — OPEN — drop indicator vertical bar (§139)
Symptom: no visible insertion line during strip drags. Fixed: solid
theme-Highlight overlay bar at the nearest divider (anywhere-hover snap);
Qt draws no nearest-gap line in IconMode (researched), and the hollow
rubber-band rect is retired. Pinned by gap/bar/drop tests.

## B67 — OPEN — drop Original from the filter dropdown (§140)
Symptom: Original sat in the dropdown as if it were a choice. Fixed: it
is not an option — always the left preview — so the dropdown lists real
filters in strip order only. Pinned by combo-content tests.

## B68 — FIXED — DESIGNER CONFIRMED — 2026-10-13 — ~~drag ghost was not uniformly translucent~~ (§§141/147)
Symptom: the live X11 drag ghost rendered opaque; the attempted fallback
made alternating pixels fully transparent and fully opaque, directly
violating the uniform-opacity ruling. Fixed: the native drag window is
blank and the complete selected mini is software-blended once in a
window-level overlay. Background, image, and letters share uniform 75%
opacity (§146). Pinned by alpha and actual composite tests; native captures
reviewed. Explicit designer confirmation: §147, 2026-10-13.

## B69 — FIXED — DESIGNER CONFIRMED — 2026-10-13 — ~~drag ghost lost the selected blue treatment~~ (§§142/147)
Symptom: the uniformly translucent ghost was reconstructed on a neutral
white card instead of matching the selected blue mini visible at drag
start. First fix (a second delegate render) failed live confirmation: only
the light-blue rectangle was apparent. Reworked to synchronously capture
the actual selected viewport pixels after mouse-down, then composite that
complete bitmap at 50%. Pinned by pixel-for-pixel source comparison, blue
coverage, uniform alpha, and rendered 50/50 composition checks. A real X11
drag exposed two more helper-hidden failures: deferred paint was lost in
QDrag's loop and the hotspot used a coalesced move position rather than the
original press. Both are corrected; real-drag capture is now required.
Current implementation renders the complete cell through the same delegate
as the visible selection (§145), at uniform 75% opacity (§146). Explicit
designer confirmation of the ghost: §147, 2026-10-13.

## B70 — FIXED — DESIGNER CONFIRMED — 2026-10-13 — ~~real drag showed only selection rectangle~~ (§§143/144/147)
Symptom confirmed under a real X11 QDrag: helper output contained the mini,
but the live capture showed only the stationary selected source plus the
insertion bar. Deferred viewport paint was lost inside the native loop and
the hotspot was derived from a coalesced move. Fixed with synchronous paint
and mouse-down anchoring. Real-drag capture now visibly contains thumbnail
and caption in the moving blue ghost. Designer confirmed in §144: "The DnD
is good".
Explicit ghost acceptance reaffirmed in §147 on 2026-10-13.

## B71 — OPEN — ghost too light and drag confined to strip (§144)
Designer confirmed the recognizable mini drag is good, but requests 65%
opacity and a drop target independent of vertical pointer position. The
previous viewport painter clipped the ghost to the strip and rejected drops
elsewhere. Implemented: window-level software-composited ghost, now at 75%
per §146; internal filter drags across the window use the same horizontal
nearest-gap rule.
Native smoke verifies actual ghost pixels and exact drop/selection above,
inside, and below the strip and over controls, plus Escape cancellation.
Ghost appearance/opacity: FIXED — DESIGNER CONFIRMED — 2026-10-13 (§147).
Drop behavior remains OPEN: §147 explicitly excludes other DnD issues from
the ghost confirmation. See: `docs/UI_LAYOUT.md`,
`tools/drag_smoke.py`.

## B72 — FIXED — DESIGNER CONFIRMED — 2026-10-13 — ~~white bottom strip in drag ghost~~ (§§145/147)
Measured: 178px item, 184px list widget, 168px viewport after a 14px
horizontal scrollbar and 2px frame. The hidden vertical scrollbar still
had a 10px range. Capturing only the visible portion of the item into a
178px white canvas created the trailing neutral band. Earlier caption
condensing masked clipping without correcting that mismatch. Fix the
view's full-row geometry from Qt measurements and render complete items
through the same delegate for display and drag snapshots. Fixed: one
view-owned static grid, Qt size hints including frame/scrollbar, and a
single delegate for complete displayed and dragged cells. The hidden
vertical range is zero; the trailing neutral pixels are gone. Bottom-edge
and partial-scroll comparisons, 14/16/30px scrollbar styles, and native
drags at 100%/200% scaling verify it. Uniform opacity is 75% per §146.
Explicit designer confirmation of the ghost: §147, 2026-10-13.
See: `docs/UI_LAYOUT.md`, `tools/drag_smoke.py`.

## B73 — FIXED — DESIGNER CONFIRMED — 2026-10-13 — ~~mini numbers stay stale after drop~~ (§§148/149)
Symptom: dropped minis retain old sequence numbers until processing or
another content refresh. Root cause: `_paint_strip_item` bakes `N. label`
into cached icons; `_restrip_ordered` updates the order and combo without
refreshing those pixels. Existing tests checked helper/combo strings only,
not what the minis actually rendered. Design: retain stable unnumbered names
in the model; the shared display/ghost delegate paints numbered captions
from the live model row. Reorder must not reprocess documents, clear caches,
or change recipe/amount/progress. Regression coverage must inspect actual
caption pixels immediately with content refreshes disabled, including native
drops. Implemented: the common delegate now draws `N. label` from the current
model row; the icon contains only stable per-filter content, and redundant
selection-triggered icon rebuilding is removed. Regression tests reproduce
the original failure and now pass for ready/pending/queued content without
refreshes. Full suite: 84 passed. Native 100%/200% drop checks inspect the
actual X11 window pixels without forcing a new widget paint; screenshots
viewed. Explicit designer confirmation in §149 on 2026-10-13.
See: `docs/UI_LAYOUT.md`, `docs/TODO.md` §148.

## B74 — OPEN — first filter selection starts another preview job (§149)
Visible symptom: a mini already depicts a processed filter, but first-time
selection starts "Rendering preview…" again. Trace the split processing and
cache lifecycles and replace them with the canon's shared real filtered file.
Implemented 2026-10-13: removed three independent GUI job paths and the
two-entry visited-preview cache. All filters are real-file jobs queued on
open; selection/view/reorder adds zero filtering calls in regression tests.
Real lifecycle smoke passes. Awaiting designer confirmation.
See: `docs/FILTER_LIFECYCLE.md`, `docs/TODO.md` §150.

## B75 — OPEN — displayed amounts are not final filtered PDF sizes (§149)
Canon requires `os.path.getsize` of the actual filtered PDF, including
container/fonts/masks, not sums of estimated image/encoding payload bytes.
Preview/minis/export must consume the same artifact that was measured.
Implemented 2026-10-13: `nbytes` measures the whole completed PDF; actual
readback pixels and exported bytes are checked against that file. Awaiting
designer confirmation, not closed by the 124-test suite.
See: `docs/ARCHITECTURE.md`, `docs/FILTER_LIFECYCLE.md`, `docs/TODO.md` §150.

## B76 — OPEN — no saved/live draft separation or dirty marker (§149)
Live controls must edit one filter draft, debounce processing, and show `*`
until saved or reverted. Selection must not mutate recipes or dirty state.
Implemented 2026-10-13: saved/draft recipe separation, 200ms debounce, full
effective inputs, blocked load signals, `*` labels/window state, and instant
saved-value reuse. Regression tests and viewed GUI captures pass. Unconfirmed.
See: `docs/FILTER_LIFECYCLE.md`, `docs/UI_LAYOUT.md`, `docs/TODO.md` §151.

## B77 — OPEN — unsaved filter switching loses edits and artifact ownership (§149)
Require Save / Save As… / Discard / Cancel before leaving a dirty filter,
with the designer's keep/delete semantics and safe in-flight cleanup.
Implemented 2026-10-13: standard Qt decision roles plus Save As; every
decision and canceled naming is tested. Save As preserves old saved files
and copies prepared new files into its new UUID without re-filtering. Source/
worker/export references prevent premature deletion. Awaiting confirmation.
See: `docs/FILTER_LIFECYCLE.md`, `docs/PERSISTENCE_AND_TEMP.md`, `docs/TODO.md` §152.

## B78 — OPEN — temp sweeper removes live worker directories (§§123/149/150)
Concurrent GUI smoke sessions exposed FileNotFoundError in workers writing
progress/output: the old sweeper removed every empty directory, regardless of
age or ownership. Fresh worker directories may be empty before their first
write. Implemented 2026-10-13: one held Qt process lock per PID directory;
stale sweeping skips live processes and fresh empty directories. Normal-exit
cleanup removes owned files after workers finish. The worker-added session
layer was rejected in §153 and removed; test roots are isolated instead.
Ownership/expiry/exclusivity/normal-exit tests pass; awaiting confirmation.
See `docs/PERSISTENCE_AND_TEMP.md`, TODO §§155/157/158.

## B79 — OPEN — real saved image streams fail decoding (§§122/149/150)
Real-file native smoke logged JPEG "starts with 0x78 0xda", invalid JPX
headers, and Flate header errors. Replacing already-encoded streams with
PyMuPDF's default compression can add a Flate wrapper, then code overwrites
the Filter dictionary with the original codec. Simulated previews concealed
this corruption. Encoded stream insertion must disable automatic compression;
render/readback tests must verify actual decoded output for every codec.
Implemented 2026-10-13: `compress=False` for encoded insertion, plus explicit
validated Zopfli zlib output (its default gzip was a second corruption source).
Actual JPEG/JPX/Indexed/BW readback and invalid-output gate tests pass; the
formerly misdiagnosed sparse JBIG2 sample now decodes. Awaiting confirmation.
See: `COMPRESSION.md`, `FILTER_LIFECYCLE.md`, TODO §156.

## B80 — OPEN — filters need unique persistent UUIDs and UUID-named directories (§155)
Legacy slug IDs and opaque generated artifact directories do not implement
the designer's UUID ruling. Assign persistent random UUIDv4 identities;
check the full loaded list for canonical UUID duplicates, including pasted
records, and repair collisions without dropping filters. Copy/Save As gets
a new UUID; rename/reorder do not. Store generated files under that UUID
inside the owning PID directory, without rerunning filtering for copies.
Implemented 2026-10-13: built-in/persisted UUIDv4, checked generation, load
migration/duplicate repair (including pasted alias duplicates), UUID-named
folders, and immutable saved/live recipe children. Copies materialize prepared
files in background, with safe source references. Identity/path/reload/copy
tests pass in the full 124-test suite. Awaiting designer confirmation.
See: `docs/PERSISTENCE_AND_TEMP.md`, `docs/FILTER_LIFECYCLE.md`, TODO §160.

## B81 — FIXED — DESIGNER CONFIRMED — 2026-10-14 — ~~reordered mini clicks flicker wrong identities/captions~~ (§§156/157/159)
Designer reports wrong old names flickering from roughly mini 5 after reorders.
The retained live app log also shows `_paint_strip_item` receiving a `None`
item: the visible Qt model and separate `_strip_ids` order can diverge. Trace
actual native higher-index moves, model row count/data identity, and first-click
paint; fix ownership/drag mutation at the root. Never restore missing filters
only in an auxiliary list or suppress a missing-item exception. UUIDs and
prepared filtered files must remain stable, with no reprocessing on selection.
Implemented/verified 2026-10-14: a before-fix event test reproduced Qt still
in DraggingState after the separate manual drag ended. The default Qt
controller could then run its own copy/remove cleanup. Consolidated into the
Qt startDrag hook, UUID-only active-drag MIME, one moveRow, model-only order,
UUID-addressed content updates, and deduplicated startup order. No suppressed
exception or extra repaint repair. Full suite 131 passed; native 100%/200%
runs preserve all 11 UUIDs/rows and prepared artifacts through eight gestures
and 33 subsequent clicks at each scale. Captures actually viewed. Explicit
designer acceptance in §159 on 2026-10-14 (America/New_York).
See: `docs/UI_LAYOUT.md`, TODO §161.

## B82 — OPEN — excessive bottom whitespace in minis strip (§159)
The 178px cell's final caption rectangle ends at y=158 (exclusive), leaving 20px below
versus the 4px top padding. This is oversized content geometry, not scrollbar
space to hide or clip. Derive the full cell height from the same 4px padding
above and below content, keeping the native scrollbar reserved separately.
Keep full captions, zero vertical range, and the complete selected drag ghost.
Implemented with shared layout rectangles and a content-derived 162px cell:
4px padding above/below, unchanged thumbnail/caption placement, no cropping.
Qt reserves the actual scrollbar separately; 14/16/30px style cases still
hold. Full suite 134 passed, including painted margins and intact last caption.
Native 100%/200% runs passed eight gestures and 33 clicks each. Offscreen
main/stacked/zoom, 1:1 strip, and native captures actually viewed. Still
OPEN: implementation/test completion is not designer acceptance.
See: `docs/UI_LAYOUT.md`, TODO §164.

## B83 — OPEN — white mini pages blend into strip background (§159)
Delegate/view ground uses the same white Base as rendered PDF pages. Give
the strip a subtly darker palette-derived background so page bounds are
visible, with no added border or selection bar. Display and ghost must share
the same background and unchanged uniform 75% ghost opacity.
Implemented as the strip's local Base = Window.darker(105), for active,
inactive, and disabled groups and on theme palette changes. Native Window
was nearly white (#faf9f8), so using it unchanged was too subtle; a slight
theme-derived shade makes page bounds distinct without adding a border.
Other pane palettes untouched; full suite 134 passed (light/dark/palette
regressions and shared complete 75% ghost). Native 100%/200% passed;
offscreen/native captures viewed. Still OPEN pending designer acceptance.
See: `docs/UI_LAYOUT.md`, TODO §165.

## B84 — OPEN — unsaved-filter discard has close-oriented wording (§160)
Qt's native Discard text can read "Close without saving" in this theme, even
though this dialog resolves a filter edit. Explicitly use "Discard Changes"
while keeping the standard Discard identity/role and Cancel escape button.
Implemented; role/label regression passes, full suite 150 green. Actual
offscreen and native 100%/200% dialogs captured and viewed. Still OPEN
pending explicit designer acceptance, not self-marked confirmed.
See: `docs/FILTER_LIFECYCLE.md`, TODO §166.

## B85 — OPEN — Escape after a mini click leaves the wrong selection (§161)
The existing tests mock a decision on dropdown changes, missing the native
mouse press/release which can finish selecting a new mini after a synchronous
rollback. Keep the edited current/selected mini, dropdown, controls, preview,
dirty marker and both saved/live files on cancellation. Reproduce the real
modal gesture, then repair the selection transaction at its Qt lifecycle.
Reproduced Escape/Cancel/close failures: active/current/dropdown stayed edited,
but the highlight selected the attempted target. Qt changes current before
selection, and can select twice during keyboard navigation. Repair runs Qt's
unmodified native input handlers with scoped view-signal blocking, then emits
one completed selection notification to the existing switch controller. This
avoids rollback inside an unfinished Qt step; no timer/extra repaint repair.
Full suite 150 passed: repeated real modals for mouse/keyboard/post-reorder,
one prompt per gesture, both selection states and file/control/preview/dirty
invariants; all decisions through dropdown and mini. Native 100%/200% dirty
mini Escape and pixel checks passed; captures viewed. Xvfb's missing window
manager requires explicit native focus return after modal close in the smoke,
not a product selection patch. Still OPEN pending designer acceptance.
See: `docs/FILTER_LIFECYCLE.md`, TODO §167.

## B86 — OPEN — explicit revert changes affordance missing (§162)
Provide a counter-clockwise Revert Changes icon beside the dropdown, enabled
only for the active draft; it discards that draft and reuses the saved result
without changing selection, other filters, or dispatching filtering work.
Implemented immediately beside dropdown: tooltip/accessibility name,
active-draft-only enabled state. §197 / B102 replaces the original custom
arrow with the standard document-revert icon; behavior is unchanged. Calls the existing
safe Discard operation. Full suite 150 passed, including ready/debounced/
pending revert with saved result reused and no new filtering. Native 100%/
200% Revert clicks passed; icon/dialog/selection captures viewed. Still OPEN
pending explicit designer acceptance.
See: `docs/UI_LAYOUT.md`, `docs/FILTER_LIFECYCLE.md`, TODO §168.

B84–B86 still await explicit designer acceptance; launching the app or
worker test interaction does not constitute that acceptance.

## B87 — OPEN — zoom-out centers phantom columns; original/preview disagree (§§164/165)
Original computes capacity without capping it by actual page count, then
sets scene width to every possible column. Qt centers that oversized scene,
leaving one/two actual pages towards the left. Gap capacity also differs
from the actual transformed scene stride. Capacity based on the old viewport
can also retain a needless vertical scrollbar and prevent an exact-fit
two-column grid. Calculate the prospective grid against Qt's maximum viewport,
reserving the style's scrollbar extent only if that grid needs it.
Peer zoom copies transform/scroll
but does not reflow items/scene bounds, so preview can retain a different
layout. Use accurate occupied bounds with Qt centering and one shared grid
calculation/reflow for both panes and mini framing. No filter processing,
forced scroll/pan reset or per-page positioning patches. Regressions must
cover one/two/many pages, both zoom directions/panes, row-major layout and
resize. Implementation is not designer acceptance.
Implemented 2026-10-14: one occupied-column calculation owns main/minis;
baseline owns both panes' grid area/dimensions. Peer zoom reflows geometry,
guarded against intermediate scrollbar signals; resize propagates too.
Unchanged geometry is cached for ordinary pan. Nine new cases reproduced
the phantom-column/peer failure before repair; exact-fit testing additionally
reproduced the stale-scrollbar capacity failure. Full suite 166 passed with
16 new viewer cases plus real-file/no-processing integration coverage.
Offscreen one/two/seven-page, row-major and stacked captures actually viewed
at whole-window and 1:1 pane/strip sizes.
Still OPEN pending explicit designer confirmation, not self-marked fixed.
See: `docs/UI_LAYOUT.md`, `docs/DESIGN.md`, TODO §§170/171.

## B88 — FIXED — DESIGNER CONFIRMED — 2026-10-14 — slow resize/divider feedback (§§166/167)
Designer reports maximize-to-half-screen/smaller triggers 5–10 seconds of
repeated original/preview boundary and right-panel splitter movement,
apparently when controls overflow horizontally. Trace and reproduce the
feedback between content-derived size hints, splitter/scroll-area layout,
headers and delayed view/mini updates before selecting a root repair.
Main panes remain equal, the right divider stays draggable, controls scroll
internally, and resize never reprocesses filters. No timed sizing patches.
Implementation/test completion will not imply designer acceptance.
Reproduced with the actual 12-page NASA Kepler example: 1920×1000 → request
640×600 was initially constrained to 806px by the old text-derived minimums.
23 view-reframe timeouts followed; original/preview widths started 202/297px,
and the panel allocation drifted 257 → 383px. Last geometry change was at
3.955s; last reframe at 4.118s. Each shortened header became the next minimum
width. The controls' horizontal scrollbar was a symptom, not the controller.
Root design: full-content, paint-only elision with ignored horizontal size
hints; remove window-resize text mutation and header refresh from view timers.
Implemented in `ui_qt/headers.py`: full text/tooltip/accessibility stay intact;
theme painting computes elision without setText or geometry mutation. Removed
the window-resize text setter and view-timer header refresh. Both initial
640px/960px shrink regressions failed before repair. Full suite 170 passed
in 47.65s, including equal/stable panes, splitter moves with metadata updates
forbidden, no filter jobs, paint-only size hints and theme/text invariants.
Real 12-page resize smoke stayed stable for 10 seconds: final geometry at
0.023s (100%) / 0.049s (200%), one normal mini refresh at each scale. Squeezing
the panel itself preserved the chosen divider and native horizontal overflow.
Whole-window/1:1 header/panel captures and standard shots actually viewed.
Designer explicitly confirmed in §167: "Ok, this is confirmed fixed, thank you."
Acceptance scope is the resize/divider feedback issue, not unrelated issues.
See: `docs/UI_LAYOUT.md`, TODO §172.

## B89 — OPEN — BW text-preserving outputs much larger than FFPR (§168)
Designer reports `examples/images.pdf`: FFPR is much smaller than BW with
retained text. Inspect actual objects/streams/soft masks, source DPI/placement,
overlap, encoder validity and saved readback. New ruling: BW with FFPR off
composites overlapping imagery into an efficiently encoded BW layer without
text; retained text remains separate/on top. FFPR on rasterizes everything.
Benchmark true complete PDF sizes/times, retained text and rendered appearance,
including overlapping/transparent/reused images and image/text ordering.
Preserving text is not a universal mathematical guarantee of smaller PDFs;
account for measured encoder/resolution/font/container costs. Design decision
and implementation must resolve existing per-image-only canon explicitly.
See: `docs/COMPRESSION.md`, `docs/DESIGN.md`, TODO §174.

Clarifications §§169/170: both text and vector diagrams remain native, with
their original geometry, colors and transparency. Never manufacture
glyph-outline masks or rasterize text under a duplicate selectable text layer.
Only image content is eligible for BW composition. §171 subsequently chooses
a simpler ONE-image-canvas/native-overlay policy, explicitly accepting different
unusual native/image stacking instead of the unshipped ordered-run architecture.
Plain opaque white page backgrounds go below the image, not above it; native
text/vector artwork goes above it. FFPR is the existing flattened-fidelity
choice. See TODO §178 and the current compression policy; no ordered-run or
mask-heavy fallback architecture is to be shipped.

Implemented and worker-verified 2026-10-14; **designer confirmation pending**.
The simple policy is now in `core/image_layers.py`; 14 saved-file regressions
cover native content, image DPI, overlap/masks, rotations/forms/inline/stencil
and PNG fallback. images.pdf at 300dpi/Otsu: old OFF 79,750B → new OFF 10,397B
(about 87% smaller), versus ON 4,093B. OFF's native subset font and content/
container cost is explicitly accounted for in `COMPRESSION.md`; smaller FFPR
is not itself evidence of a broken encoder. Saved-file/corpus runs verify
60 FFPR page results and 106 independently decoded image-page occurrences.

## B90 — OPEN — FFPR overwrites earlier pages with the final image (§168 audit)
Real saved NASA Kepler output at 100dpi uses xref 5 on all 12 pages. Page 1
differs from its correctly thresholded source by 245,746 pixels; page 2 by
264,461; page 12 matches exactly. Root cause: PyMuPDF deduplicates identical
tiny PNG placeholders, then `_place_bw` overwrites that shared image stream
with each new JBIG2 page. Validating each payload separately did not validate
its ownership in the final multi-page file. Allocate the real image XObject
with an independent xref before placement; never mutate a shared placeholder.
Regression must compare every saved page to its actual expected thresholded
pixels, not merely assert that get_pixmap succeeds.
See: `docs/COMPRESSION.md`, TODO §175.

Implemented and worker-verified 2026-10-14; **designer confirmation pending**.
Real encoded JBIG2 and PNG image objects own independent xrefs before placing
them. Three-distinct-page regressions check every pixel for both codecs; the
actual corpus benchmark checks every FFPR page, not merely the last page.

## B91 — OPEN — display smooths real bitmap content, including FFPR (§§172/173)
Saved FFPR images are genuinely 1-bit and their decoded pixels passed both
MuPDF and Poppler gates, but build_artifact reads them into 150dpi RGB view
buffers, then mini Lanczos/Qt smooth zoom introduce grey edge samples.
The designer rules that original and filtered previews must be exact: AA only
on native PDF text/vectors, never bitmap content. Remove inappropriate image
interpolation in PDF readback and Qt display; preserve encoded sample detail
on zoom. Never apply an extra display threshold, change the saved file, or
rerun filters as a view operation. Test/view actual rendered viewport pixels,
mixed native/vector+bitmap original pages, strict FFPR and varied zoom/DPR.
See: `docs/UI_LAYOUT.md`, `docs/COMPRESSION.md`, TODO §179.

§§174/175 choose **all PDF-content AA off**, including native text/vectors,
which redraw with their actual native geometry at display/device resolution.
Implemented and worker-verified 2026-10-14; **designer confirmation pending**.
Root causes included MuPDF decoder subsampling, draw-device image interpolation,
PIL Lanczos derivatives and Qt smooth pixmap scaling. The shared exact readback
uses no interpolation, no decoder averaging and no AA; the previous prepared
150dpi page is no longer the zoomed main-pane source. Visible-region native
painting has bounded caches and handles Qt's full device transform (including
parent-window capture offsets and DPR), not a guessed scale-only correction.
The PDF composition/actual encoded color/opacity remains intact. Prepared minis
use nearest-neighbor; no view threshold, saver invocation or file mutation.
Full suite **203 passed in 46.82s**; 16 exact-display cases pass at 100%/200%,
including native-shape refinement and equal parent/pane capture pixels.
Real-file smoke captures show binary FFPR at four zooms with unchanged SHA-256
and no extra filter jobs. Standard/lifecycle whole-window and 1:1 captures
reviewed; actual updated GUI launch is recorded in `docs/PLATFORMS.md`.

## B92 — OPEN — color processing creates dark image-edge halos (§177)

Diagnosed 2026-10-14 on the live images.pdf JPEG/JPX/Indexed artifacts, not
only a GUI derivative. The first source image is 1600×1608 RGB plus a separate
same-size soft mask; 983,445 fully transparent source pixels have RGB=(0,0,0).
At 150dpi the saver writes 356×358 RGB but keeps the original soft mask.
Different mask dimensions are not inherently an illegal PDF; the defect is
resizing unassociated RGB without its opacity, mixing hidden black into edge
colors, then independently masking the already-contaminated result.
`color_stream_plan` only checks PIL RGBA/LA/PA, but `extract_image` reports the
PDF soft mask separately, so the intended alpha guard does not catch it.
An in-memory alpha-aware resampling comparison finds 445 affected edge pixels
with up to 119/255 channel darkening before encoding. Lossy codecs may worsen
the result, but the Indexed output reproduces it without JPEG.

Captured/viewed `.tmp/border-{original,indexed64,jpeg}.png`; the border is
present in the actual saved PDF readback and absent from the original. Do not
re-enable display smoothing, paint over the fringe or flatten images onto an
assumed white background. Correct color+opacity processing must preserve real
PDF compositing. This turn's original request asks why: diagnosis is complete,
application repair is pending explicit direction. No fix/acceptance claimed.

§179 subsequently authorizes the repair; §180 specifies the root design:
flatten the image/content layer in full color first, then resize to the chosen
DPI and apply the transform, with native text overlaid. The remaining per-image
color loop is a flow discrepancy, not merely a missing alpha guard. Do not
ship a local alpha patch in lieu of this requested composition-first design.
§§181/182 retain §170's explicit native-vector rule and select full-color
composition → ONE final-DPI resize → filter/encode. No original-plus-upscaled
duplicate processing or post-palette/threshold resize. This also supersedes
BW's earlier per-image resize preparation; BW keeps §171's white backdrop.

Implemented/worker-verified **2026-10-14**, pending designer acceptance:
removed `color_stream_plan` and the individual RGB/mask rewrite loop. Color
and BW share native image-layer selection, opaque full-color composition,
one global Lanczos resize and original native text/vector assembly. Original
flat page backdrops participate in color composition; source masks are consumed
by MuPDF, not retained as stale independent output masks. Bounded source tiles
fill one anonymous disk-backed RGBX buffer in the artifact work directory;
one global resize avoids tile coefficient seams. Scratch cleanup is tested on
render/resize errors and cancellation. No view smoothing or second filter path.

All five images.pdf color outputs have one final-DPI image, zero masks, native
text/two drawings and 48–77% smaller actual PDFs than the previous live default
artifacts. Normal lossy JPEG ringing remains a codec tradeoff, not hidden-black
alpha contamination. Synthetic tests inspect RGB BEFORE encoding plus actual
saved pixels; overlap, blue backgrounds, clips, rotations, DPI up/down and all
codecs are covered. Full suite **229 passed in 45.67s**; 50 independent color
image-page decodes and eight BW decodes pass. Main/1:1 numeric, lifecycle,
layout/HiDPI and final-file screenshots were viewed. `COMPRESSION.md` records
bytes/timings, corpus size increases and the overlay policy. Updated desktop
build launched and supervised (see `PLATFORMS.md`). B92 remains OPEN until
the designer explicitly confirms the repaired halo-free image-edge scope.

## B93 — FIXED — DESIGNER CONFIRMED — 2026-10-14 — low-color nearest mapping (§183)

Reported 2026-10-14 after the compose-first build. Investigate palette creation
separately from assignment, reproduce the actual saved result and compare each
assigned color to the available palette. No display recoloring/dithering or
special Firefox patch; repair the quantization path shared by actual outputs.

Root cause: FASTOCTREE maps through coarse color buckets, not an exact nearest
search. At low palette counts some buckets resolve to default index zero,
which is commonly white after page composition. On the diagnostic images.pdf
JPX canvas, 3-color output has 111,276 wrongly-white assignments, 112,097 total
non-nearest assignments. The earlier tests only checked count/encoding, not
the nearest-color contract. A median-cut replacement passed nearest tests but
viewed 3/4-color results wasted slots on nearly-white variants; not shipped.

Final repair separates bounded coverage/k-means palette fitting from exact
full-resolution RGB assignment. One shared helper supplies true-Indexed parts
and headless RGB utilities; duplicate helper definitions are removed. No
dithering or approximate white fallback, no output-resolution reduction.
Actual white stays white; genuinely few colors remain exact. Eleven palette
regressions, full suite 244 passed, real saved-file readback/independent decode,
and viewed 3/4/8/16-color whole/1:1 captures verify the repair. Current files
and benchmarks are in `COMPRESSION.md`; supervised restart is in `PLATFORMS.md`.

Explicit designer confirmation, §184, 2026-10-14 (America/New_York):
> yes, much better, what was the problem?

Confirmation scope: the reported low-color appearance/mapping improvement.
It does not close the independently tracked debounce policy or all other
color/native-overlay fidelity issues.

## B94 — OPEN — unify and verify filter-edit debounce across controls (§183)

The existing application uses one 200ms `_preview_timer` for recipe edits;
spinner/slider values already enter `_filter_edited`. The designer requests
consistent debounced preview publication for every input. Recommend one 300ms
trailing edit timer, immediate dirty/control feedback and latest-recipe
publication. Diagnose any missed update rather than adding per-widget timers.
View-only framing stays separate and never processes PDF filters (§149).

Implemented/worker-verified 2026-10-14: retain the existing one edit path,
set its common interval to 300ms with Qt PreciseTimer, and verify every recipe
input. Four new lifecycle cases and a real-file mixed-spinner/slider/typing
smoke pin no early submission, one final recipe and correct file publication.
Immediate controls/dirty feedback and prepared identical-recipe reuse remain.
There was already a shared 200ms timer, not a proven separate per-widget timer
bug. B94 remains OPEN for explicit designer confirmation of the new policy.

## B95 — FIXED — DESIGNER CONFIRMED — 2026-10-14 — ~~mini progress appearance~~ (§§185/187/190/191/192)

Designer confirmation (§192): "Ok, this is good." Exact full message is in
`docs/DESIGNER_VERBATIM.md`. Scope: native progress styling, 4px highlight
inset, 50% larger bar/percentage, no extra white padding and whole-mini-frame
centering. Local date America/New_York. This does not confirm B96/B97 or other
DnD/layout/filter issues. The OPEN statements below are historical stage logs,
superseded by this explicit acceptance, not worker self-certification.

Reported 2026-10-14. `_paint_strip_item` manually paints a
104×12px groove/chunk/text into the cached icon. This is narrower than both the
120px preview box and 150px reserved cell, bypasses Qt's actual progress style
and native font metrics, and lacks an opaque white backing. The selection
wash is applied afterward, so merely adding white inside that icon would tint
it blue instead of satisfying the designer's request.

Required repair: keep progress as model data, draw a native CE_ProgressBar in
the shared strip delegate after the selection wash, using the default bar's
style and metrics. Reserved cell width (less §187's shared outer inset),
opaque white backing, no new strip height,
no selection/scrollbar/drag regression. `UI_LAYOUT.md` carries the design;
TODO §189 tracks implementation/verification. Designer acceptance pending.

Implemented/worker-verified 2026-10-14: separate model progress role and shared
delegate `CE_ProgressBar` rendering replace the cached hand-painted bar. The
actual default widget supplies style, palette, font, direction and native
formatting; one hidden formatter serves all rows without changing the status
bar's value. Full 150px width, native height and an opaque white plate (2px
above/below) are painted after selection. No strip sizing, jobs or output
files change. Completion removes the overlay; the complete ghost retains
uniform 75% opacity. Native painter foreground ink is matched too, including
styles whose label drawing uses the current pen instead of a palette role.

Full suite: 272 passed in 64.35s. Twenty-eight new cases also pass at 2×:
pixel agreement with actual QProgressBar widgets in Fusion/Windows styles,
light/dark palettes and selected/unselected 0/37/99% states; font/locale/RTL,
opaque backing, model-only updates, completion geometry and ghost pixels/
opacity. Both-scale `tools/shot.py` captures were actually viewed, including
explicit percentage paint fixtures, actual pending edits and completion.
See `TEST_PLAN.md` for native drag evidence. B95 remains OPEN until explicit
designer confirmation; test/style names do not certify another OS.

§187 refinement (2026-10-14, not acceptance): the edge-to-edge 150px overlay
obscures all highlight at its sides. Reuse STRIP_PADDING=4 logical pixels to
inset BOTH the native bar and backing, leaving a 142px overlay and selected
highlight visible on both sides. Existing 2px white backing above/below is
separate from this outer padding. Geometry and worker/native style behavior
otherwise stay unchanged. TODO §190 tracks this correction.

§§190/191 refinement (2026-10-14, not acceptance): make the mini bar height
and percentage font 1.5 times the default native control's, remove the
separate 2px white padding, and center in the complete mini frame INCLUDING
captions, not just its page image. The opaque backing is limited to the bar
bounds; retain the 4px outer side inset and unchanged cell/ghost geometry.
These rulings supersede earlier height, backing-padding and centering details,
not native styling or true progress. TODO §§193/194 track this refinement.

Final refinement implemented/worker-verified 2026-10-14: 142px bar and backing,
1.5× native height and percentage font, centered in the full 162px cell, with
no extra white padding. Thirty-two progress cases pass at 100%/2×, including
exact native-widget pixels, whole-cell/translated geometry, point/pixel fonts,
adjacent unchanged pixels, live theme/locale/RTL, completion and 75% ghost.
Both-scale real/fixture captures were viewed. Native X11 100% drag smoke
passes all eight gestures, 33 clicks, dirty Cancel and Revert. The additional
2× caption-oracle experiment's limit is recorded separately in `TEST_PLAN.md`;
it is not hidden by a tolerance or called designer acceptance. B95 stays OPEN.

## B96 — OPEN — staggered main-region edges and redundant minis title (§188)

Reported 2026-10-14. The preview block is inside an unnecessary mid/row layout
chain; attaching its layout to a wrapper gives it default margins in addition
to the root's. The strip and panel frame do not share those margins. A visible
minis title adds a whole extra row; pane spacing is hardcoded 6px while the
panel divider is 8px. These independent owners produce staggered side/bottom
edges and different gaps between previews, panel and minis.

Required repair: remove the title/row and redundant wrapper layouts, introduce
one shared 4-logical-pixel region-spacing policy and a reusable zero-margin
PreviewPair component. Align outer frames and preserve equal/stacked panes,
draggable divider, native panel overflow and the designer-confirmed stable
resize behavior. No positional nudges or compensating spacers. See
`UI_LAYOUT.md`, TODO §191. Designer acceptance pending.

Implemented/worker-verified 2026-10-14: root-owned UI_PADDING=4 and reusable
zero-margin PreviewPair replace the wrapper chain; title/row removed, equal
4px outer edges, pane/panel gutters and row-to-strip gap. Six actual-frame
regressions pass in equal/stacked modes at three widths and both scales.
Both-scale resize smokes settle in 0.126s/0.115s without later drift, retain
native panel overflow and cause no filtering. Full windows and 1:1 junctions
were viewed. No strip-cell, selection, ghost-opacity or PDF behavior changed.
B96 remains OPEN for explicit designer confirmation.

## B97 — OPEN — Save As from a dirty-filter switch fails to select its new copy (§189)

Reported 2026-10-14. Actual desktop log: at 20:44:54 Save As created a new
UUID-owned filter/result, then selection continued to color-j2k instead of
the copy. Root cause: `_resolve_unsaved_filter` reduces the new filter ID to
a boolean; `_preset_chosen` then unconditionally commits the originally
requested destination. Explicit `copy_filter` independently handles the ID,
so the same action has inconsistent selection semantics. Existing tests
checked file ownership but incorrectly expected the original target after
Save As. §189 explicitly corrects that behavior.

Required repair: an explicit dirty-resolution result carrying any new
destination and one shared activation commit. Audit mouse/dropdown/keyboard,
direct Save As, canceled names, ready/debouncing/pending output, and open/
close decisions. Keep both saved recipes/results, show the new copy and
scroll its mini into view; selection must never start another real saver.
See `FILTER_LIFECYCLE.md`, TODO §192. Designer acceptance pending.

Implemented/worker-verified 2026-10-14: immutable _FilterResolution carries
the new-copy ID; one _activate_filter commit updates both selectors, controls
and exact prepared-file preview. Only newly created copies request reveal;
ordinary mouse/keyboard selection retains Qt's own scrolling and drag press
geometry. Save As redirects dirty switches and explicit/open/close resolution;
Save/Discard still honor the original target, Cancel/blank names stay edited.
Native mouse/keyboard/dropdown and direct/pre-debounce/pending/open/close
regressions pass. The real modal mini-click Save As and naming dialogs were
exercised in `filter_smoke.py`; new-copy selected captures were viewed, both
saved files retained and no second real saver started. B97 stays OPEN.

## B98 — OPEN — configuration block lacks a matching header (§192)

Reported 2026-10-14. Both preview blocks have PaneHeaders outside their scroll
frames, but the right-hand block starts with the scrolling File metadata.
Required repair: a "Configuration" PaneHeader and the SAME shared header/
content composition as the previews, with aligned tops/bottoms, no duplicate
margins and unchanged overflow/resize behavior. See `UI_LAYOUT.md`, TODO §196.
Implemented/worker-verified 2026-10-14: one shared PaneBlock composition and
PaneHeader for all three regions; Configuration sits outside the scroll area.
Both-scale actual geometry and ten-second resize smokes pass, last settling
0.099s/0.182s with equal headers/frame tops, no later drift or filtering.
Viewed full/1:1 captures, full suite 319 passed and normal final restart.
Designer acceptance pending.

## B99 — OPEN — PBM leading binary whitespace can break production JBIG2 input (worker study finding)

Found 2026-10-14 during §192's prototype stress benchmark. A valid P4 input
whose first packed raster byte is newline (0x0a) produces encoder exit 3 and
Leptonica `pixReadStreamPnm: read error in 4`; the reader's dimension fscanf
consumes leading binary whitespace. Production `bw_page_jbig2` uses PBM and
falls back to PNG when this happens, so lossless JBIG2 is unnecessarily lost.
The prototype feeds a 1-bit PNG to the SAME `jbig2 -p` coder and passes exact
decode, including a leading-newline regression. Production was deliberately
NOT changed: designer §193 authorizes design/benchmarks, not integration or
unrelated encoder fixes. See `docs/LAYERED_COLOR_JBIG2.md` for the primary
reader source, reproducer and measured scope. No designer confirmation.
Subsequent §203 requests production codec selection; the shared transport
repair is now in scope for TODO §206. Keep this issue OPEN until confirmation.

Implemented/worker-verified 2026-10-15: one shared encoder feeds valid 1-bit
PNG transport to the same resolved `jbig2 -p` executable for BW and colored
stencils. The leading-packed-newline regression now yields genuine lossless
JBIG2 with exact decoder pixels; explicit selections never hide failure with
Flate. Covered by the final 429-test suite. This is a production repair under
§203, not a retroactive change to the study's original scope or acceptance.
B99 remains OPEN pending explicit designer confirmation.

## B100 — OPEN — all-black error placeholder can pass the production JBIG2 pixel gate (worker study finding)

Found 2026-10-14 with an injected malformed stream (`b'invalid'`):
`jbig2_renders(..., expect=all_black)` returns true although MuPDF reports
cannot-complete/read-error/padding diagnostics. Rendering recovery paints
black, coincidentally matching the expected array. Prototype validation also
rejects diagnostics; its regression passes. Production remains unchanged
under §193's study-only scope. A production repair should validate decoder
success as well as pixels without swallowing unrelated concurrent warnings.
See `docs/LAYERED_COLOR_JBIG2.md`. No designer confirmation.
Subsequent §203's production integration must repair this shared validation
gate, not duplicate the prototype workaround. TODO §206; confirmation pending.

Implemented/worker-verified 2026-10-15: the shared gate snapshots MuPDF
diagnostics under FITZ_LOCK and rejects newly appended decode errors even
when an all-black recovery image equals the expected samples. Existing
diagnostics are preserved, not consumed as a workaround. Valid sparse masks
and the deliberately corrupt all-black fixture are covered by the final
429-test suite. B100 remains OPEN pending explicit designer confirmation.

## B101 — OPEN — redundant mini working placeholders (§195)

Reported 2026-10-14. `_paint_strip_item` bakes "working…" into both a missing
image and pending amount, independently of the native progress overlay.
Implemented/worker-verified: no substitute busy phrase, unavailable slots are
transparent/blank, real cached image/bytes retained through edits, preview
header omits unknown size. Eight paint/model regressions pass at both scales;
queued/live/complete captures viewed, full suite 319 passed, final restart.
Errors and actionable status remain. Designer acceptance pending.

## B102 — OPEN — custom action glyphs mixed with desktop-theme icons (§§196/197)

Designer §200 explicitly REJECTS the delivered icon appearance (2026-10-14).
The technical provider repair is not acceptance. A coded stock-icon comparison
lab is requested in B104; do not auto-choose another production icon set.

Reported 2026-10-14. Revert/rename and zoom are hand-painted raster glyphs,
Copy/Save have independent theme/fallback code, and export/stop can lack an
icon. The rename comment misstates §120 as authorizing custom drawing.
Required repair: one desktop-theme-first named-icon provider and a licensed
stock KDE Breeze SVG fallback family, including light/dark and HiDPI states.
Use it consistently for filter actions, export/stop, zoom and the widget lab;
preserve callbacks, logical sizes, enabled state and filter lifecycle. Record
provenance/licenses, package data/QtSvg requirements, tests, viewed captures
and normal restart. Implemented/worker-verified: shared provider and stock
16/22px light/dark SVGs, actual surface-palette refresh, no action/selection/
processing changes. Full suite 339 passed; 33 focused checks pass at 2×;
real/fallback enabled/disabled full windows and 1:1 crops viewed at both
scales. See `docs/ICONS.md`, TODO §201.
Designer acceptance pending.

## B104 — OPEN — designer cannot compare and identify preferred stock icons (§200)

The current glyph appearance is rejected. Add View → Icon Lab… with genuine
Nuvola, Oxygen and similar choices, permanent visible codes, app-size/disabled/
enlarged previews and a copyable per-action selection. This is a review tool,
not an automatic icon-theme/apply operation. Keep source/license provenance
and no-filtering/settings invariants. See TODO §203 and `docs/ICON_LAB.md`.
Implemented/worker-verified: 37 choices / four genuine stock families, explicit
permanent IDs, original source names, app-size/disabled/32px previews, scoped
background review and native scrolling, per-action selection, Clear and Copy.
One reusable modeless window; no production icon/settings/filter/job mutation.
Original PNG hashes, source versions and all notices/licenses bundled.
43 focused cases pass at both scales, actual full/1:1 captures viewed; full
suite 382 passed, previous normal exit/group verification and restart recorded
in `docs/PLATFORMS.md`. Still OPEN pending designer choices/acceptance.

## B103 — OPEN — refine mini progress enlargement to 25% (§§198/199)

Requested/clarified 2026-10-14: 25% LARGER than the original native progress
bar, 1.25× instead of the previous 1.5× height and percentage font. Preserve
the native control appearance, full reserved width less 4px insets, full-frame
centering, backing only within bar bounds and unchanged aggregate status bar.
B95's §192 confirmation remains historical acceptance of the earlier version;
it is not acceptance of this new refinement. Implemented/worker-verified:
shared 1.25× height/font factor; 40 progress checks pass at both scales,
including exact native-widget pixels, unchanged aggregate bar, retained
insets/centering and uniform 75% drag snapshot. Queued/live/complete full
windows and 1:1 controls/strips viewed at 100%/2×. Final full suite 339 passed
in 68.67s; normal prior exit/group verification and final relaunch recorded
in `docs/PLATFORMS.md`. Work: TODO §202. Designer acceptance pending.

## B105 — OPEN — compression locked to seed filter; ambiguous Strategy (§203)

Reported 2026-10-15. There is no compression selector: `_controls_spec` keeps
the existing mode, `_sync_filter_controls` and details consult the preset's
mode, and Save/Save As/load cannot persist a changed mode. Expose six explicit
compression choices, make effective recipe state authoritative throughout,
promote shared validated colored stencils and add deliberate BW Flate.
Qualify Strategy as Threshold method (manual AND automatic). Preserve UUIDs,
existing defaults, native artwork, exact real-file lifecycle and debounce.
No silent codec substitutions. See TODO §206, `docs/COMPRESSION.md` and B99/
B100 for shared encoder requirements.

Implemented/worker-verified 2026-10-15: one six-choice Image compression
selector and qualified Threshold method label, authoritative saved/draft mode
through control state/readout/effective keys/Save/Save As/fresh built-in
override reload. Shared core stencils serve production/tooling; codec labels
match actual PDF filters with no hidden JPEG/JPX-to-Indexed or JBIG2-to-Flate
substitution. UUIDs/names/order/defaults, native artwork, BW-only FFPR and
one 300ms timer remain intact. Forty core/actual-PDF and seven lifecycle
cases are in the final 429-test suite; both-scale actual-file captures and
resize checks plus modal lifecycle smoke pass and were viewed.
B105 remains OPEN, not designer-confirmed.

## B106 — OPEN — native compression not selectable or benchmarked (§§204/205)

Requested 2026-10-15: separate native text/vector/font compression from image
encoding; expose useful encoder choices and document true sizes/times/reader
limits. The shared native adapter and actual benchmark cover Flate, optimized
Flate, the 2026 Brotli extension and legacy controls. Empty native streams
exposed a MuPDF 1.28.2 encoder/decoder defect: leave them uncompressed rather
than embedding invalid zero-byte Brotli. Only two hung worker-owned diagnostic
tests were terminated; the desktop GUI was not touched for that diagnosis.
See TODO §208, `docs/NATIVE_STREAM_COMPRESSION.md`. Acceptance pending.

Implemented/worker-verified 2026-10-15: separate PDF streams selector offers
Flate (unchanged default), compatible Zopfli-Flate and limited-support Brotli
with visible warning, effective keys, shared timer and Save/Save As/load.
The shared adapter preserves decoded native bytes and encoded images,
metadata and attachments; native/container optimization is not tied to the
chosen image codec. Benchmarks cover 32 source/policy pairs / 64 outputs
with exact readback/all-page MuPDF pixels. Poppler 25.03.0 and QPDF 12.2.0
FAIL Brotli and pass ordinary codecs; both success and failure are documented.
LZW/RunLength lose on this corpus and remain controls, not UI choices.
Final 429-test suite and both-scale UI/resize/lifecycle evidence are recorded
in `docs/TEST_PLAN.md`. No claim of isolated CPU timing or universal reader
support. B106 remains OPEN pending designer acceptance.

## B107 — OPEN — native callback cancellation becomes an unpickleable worker error (worker audit finding)

Observed 2026-10-15 during close-while-processing. The GUI exited normally,
but the log records `_Selector.culler` in `core/image_layers.py`
raising Python `CancelledError` inside a native SWIG director callback.
MuPDF wraps it as `FzErrorGeneric`; returning that exception from the process
pool fails serialization: `cannot pickle 'swig_runtime_data5.SwigPyObject'
object`. A BW draft is consequently logged as an artifact failure rather than
clean cancellation. This callback path predates the compression selector work.
It is not evidence that the app crashed or that the selected codecs produced
corrupt completed files. Normal GUI exit does not certify clean worker reports.

Root-cause direction, NOT an implemented fix: keep cancellation handling on
the correct side of the native callback boundary and return only serializable
worker failures; preserve genuine decode errors, saved/draft ownership and
partial-file cleanup. A future repair needs an actual native-callback plus
process-pool cancellation regression, not a mocked Python-only exception.
Keep OPEN; the green compression suite does not establish coverage or repair
of this shutdown path.

## B108 — OPEN — colored-stencil embedding clips fractional-page edge pixels (worker benchmark finding)

Observed 2026-10-15 while extending designer §223's representative size
analysis, not a designer-confirmed UI report. On page 2 of the complete
`examples/scan-jfk-poor-copies.pdf`, the 150dpi/five-color preparation has
pixel-exact decoded palette samples/masks, and the standalone colored canvas
passes its native-resolution test. After embedding that canvas as nested
page Forms, the actual page rendering loses non-white samples on the rightmost
column relative to the identical Indexed-Flate canvas: 140 pixels at 72dpi,
165 at 150dpi, all replaced by white. Page bounds are fractional
606.719970703125 × 789.5999755859375 pt; no rotation is involved.

Reproducer/evidence: the `flate-plain.pdf` and rejected `jbig2.pdf` under
`.tmp/integrated-compression/representative-20261015/prepared-bitmaps/scan-jfk-poor-copies.indexed.150dpi.5colors/`.
Compare both pages through `core.display.DisplayPage` at 72/150dpi; on page 2
the 150dpi difference lies entirely at x=1263 of 1264 pixels. Encoded masks
and reconstructed palette samples pass; the discrepancy appears at the
whole-page Form embedding/clipping boundary, not in JBIG2 lossless decoding.

The representative runner must report rejected cells as FAILED with no size
or minimum ranking and continue verified independent cases. Do not loosen
pixel equality, change the representative scan, remove the edge from the
test or count the rejected file as a compression success. No product/display
fix is implemented here. A repair needs a fractional-page edge regression
and exact whole-page checks for both production and benchmark assemblers;
the standalone stencil test alone is insufficient. Scope: TODO §226 and
`docs/INTEGRATED_COMPRESSION.md`. Keep OPEN.

## B109 — OPEN — image-layer reconstruction introduces unpositioned ActualText (worker benchmark finding)

Observed 2026-10-15 on the complete eight-page photo-rich repository input
`examples/news-crater-lake-2026.pdf` while building designer §223's five-class
comparison. Page 1 extracts 1,224 visible words and renders without diagnostics
in the original. Its reconstructed indexed and production JPEG preparations
extract the same visible word count but introduce MuPDF's `ActualText with no
position. Text may be lost or mispositioned.` warning (six repeats on page 1).
Thus this is not evidence of visible-word loss, but native/tagged-content
diagnostics are no longer preserved. The failure appears before changing the
final native compressor; it is not a Flate/Brotli/JBIG2 decoder failure.

Evidence is the rejected `flate-plain.pdf` in
`.tmp/integrated-compression/representative-20261015-v2/prepared-bitmaps/news-crater-lake-2026.indexed.150dpi.5colors/`
and `production/prepared/news-crater-lake-2026.jpeg-q50/base.pdf` under that
same study root. Compare original and derived `get_text('words')` plus
`DisplayPage` at 72dpi, draining/reporting MuPDF diagnostics separately.

Root-cause direction, not a product fix: review how image removal/reassembly
handles tagged/ActualText spans and their positioning. Do not suppress the
warning merely because a visible-page comparison passes. A final save that
perfectly preserves an already-invalid preparation does not validate that
preparation. The overview now checks new source-to-preparation diagnostics
even for reused production JPEG/JPX outputs; affected recipes are marked
PREP FAILED with no size ranking. Preserve-images and deliberate FFPR are
validated independently. No original input is replaced to hide the case.
See TODO §226 and `docs/INTEGRATED_COMPRESSION.md`. Keep OPEN.

## B110 — OPEN — native overlay retains original color photos over the BW canvas (worker benchmark finding)

Observed 2026-10-15 on `examples/news-crater-lake-2026.pdf` in designer §223's
representative study. The BW-image preparation fails the one-final-canvas
invariant on page 1. This is not just stale unused resource counting:
`get_image_info(xrefs=True)` reports original color photographs actually
painted above the new 3534 × 5250, 1-bit DeviceGray canvas. `get_images(full=True)`
also exposes six retained 8-bit ICCBased DCT image streams, including the
1660 × 568 photograph (112,094 bytes), plus further painted inline images.
Thus the candidate is not an equivalent processed BW document and its size
must not be ranked against the other BW codecs.

Evidence: `flate-plain.pdf` under
`.tmp/integrated-compression/representative-20261015-v3/prepared-bitmaps/news-crater-lake-2026.bw-images.300dpi.otsu-180/`.
Inspect page 1 with both image APIs, distinguishing painted occurrences from
resource entries; the original photos have page positions on top of the
full-page BW canvas. This path uses the shared `_assemble_layers` compositor.
The observation does not establish whether B109 has the same root cause.

Review nested Form/inline-image filtering and native-layer assembly; do not
merely relax image-count assertions or store the duplicate color artwork.
Preserve genuine native text/vectors while removing all replaced bitmap
artwork. No product fix or designer acceptance is claimed. The shared BW
preparation is marked PREP FAILED; its dependent codecs are unmeasured, not
eight independently failed encoders. Scope: TODO §226. Keep OPEN.
