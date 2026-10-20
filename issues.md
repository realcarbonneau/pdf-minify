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
Symptom: the app vanished after launch.
Fix: launches are detached (`setsid` + `disown`), so a launcher timeout no
longer takes the app with it; the standing relaunch rule is §62.

## B2 — OPEN — Original stuck in the filter strip (§140)
Symptom: the baseline preset rendered as a filter mini.
Fix: the strip shows only real filters.

## B3 — OPEN — UI froze during previews (§37)
Symptom: the whole app locked while thumbnails rendered.
Fix: heavy work runs in background processes (half-core cap); pan and zoom
are pure view changes.

## B4 — OPEN — click restarted all processing (§44)
Symptom: clicking a filter preview reprocessed everything.
Fix: each filter is processed once per file and recipe; unchanged clicks
switch instantly.

## B5 — OPEN — truncated half-page minis (§45)
Symptom: strip previews showed only the top slice.
Fix: superseded by the exact-view minis of B7 (§48).

## B6 — OPEN — reprocessing on scroll (§47)
Symptom: scrolling re-ran background jobs.
Fix: scroll, pan, zoom and page turns only reframe minis; jobs run on file
or recipe change alone.

## B7 — OPEN — wrong thumbnail content (§48)
Symptom: minis were baseline crops, not the filter's own view.
Fix: each mini shows exactly the synced main-view framing through its own
filter.

## B8 — OPEN — right preview updated last (§51)
Symptom: on open, the main preview finished after everything else.
Fix: the active filter renders first, ahead of the other minis and sizes.

## B9 — OPEN — nothing was keyboard-zoomable (§52)
Symptom: no keypress zoomed.
Fix: Ctrl+Plus / Ctrl+Minus / Ctrl+0 with synced panes, plus toolbar zoom
controls (§§76/78/86).

## B10 — OPEN — BW saved as PNG, not JBIG2 (§55)
Symptom: the ruled JBIG2 path was never wired.
Fix: BW embeds real JBIG2; each stream is decoded and checked before
embedding.

## B11 — OPEN — JPEG2000 mini crashed silently (§56 wiring)
Symptom: processing looked stalled at 100% with dead JPEG2000 minis.
Fix: the JPEG2000 mini path uses its own preview, and worker failures are
logged.

## B12 — OPEN — Prev/Next did nothing (§58)
Symptom: the Prev/Next buttons did nothing.
Fix: the buttons were replaced by scrollbars and PgUp/PgDn (§71).

## B13 — OPEN — threshold slider changed nothing (§65)
Symptom: dragging T under Otsu re-rendered identical pixels.
Fix: T is enabled only for the Simple method.

## B14 — OPEN — codec missing on the right (§72)
Symptom: the JPEG2000/JPEG details never named the codec.
Fix: a `Codec:` first line in every mode (§82).

## B15 — OPEN — Encode vs Codec incoherence (§79)
Symptom: BW said Encode while colour said Codec.
Fix: one `Codec:` label, first line, every mode.

## B16 — OPEN — Flate streams shifted a byte (§80)
Symptom: Flate payloads carried PNG filter bytes with no predictor declared.
Fix: Flate payloads store raw rows unless a predictor is declared.

## B17 — OPEN — two different DPI values (§83)
Symptom: the preset DPI was decoration while the combo did the work.
Fix: one DPI control rules preview, sizes and save.

## B18 — OPEN — theme-roulette buttons (§84)
Symptom: magnifier icons depended on the desktop theme.
Fix: superseded by the §197 icon provider (B102).

## B19 — OPEN — Cancel looked like Undo (§85)
Symptom: the X button read as undo without a target.
Fix: Cancel is enabled only while a save runs.

## B20 — OPEN — bars parked at 50% (§89)
Symptom: fast minis finished before slow sizes started, parking bars at 50%.
Fix: each bar advances on its own work (B27).

## B21 — OPEN — right-filter click reprocessed left filters (§90)
Symptom: choosing a far-right filter restarted the left filters' in-flight
work.
Fix: selection never restarts filter jobs; every filter runs once per input
and recipe (§149).
See: `docs/FILTER_LIFECYCLE.md`.

## B22 — OPEN — terrible default demo PDF (§§27/31)
Symptom: a synthetic demo file was the default document.
Fix: `examples/images.pdf` is the default, with last-file reopen (§91).

## B23 — OPEN — last-file reopen opened test garbage (§§91/93)
Symptom: a bare launch opened `/tmp/pytest-*/m.pdf` instead of the last real
file.
Fix: the test conftest always overrides `XDG_CONFIG_HOME`, so tests never
touch the user's settings. A `setdefault` guard is not enough: the shell may
already export `XDG_CONFIG_HOME`.

## B24 — OPEN — right-pane zoom never reframed minis (§92)
Symptom: minis stuck on an old view after zooming or scrolling the right pane.
Fix: synced peer zooms notify the trailing reframe debounce.

## B25 — OPEN — palette bytes overflow past 85 entries (found in live log)
Symptom: palettes with 86+ entries embedded wrong colours
(`RuntimeWarning: overflow`).
Fix: palette indices are converted with `int()` before slicing, instead of
wrapping in uint8 arithmetic.

## B26 — OPEN — closing mid-processing must never crash (§94)
Symptom: closing the window during processing risked thread-teardown crashes.
Fix: `closeEvent` cancels all jobs, joins workers and closes the document.

## B28 — OPEN — strip must be one full row, no vscroll (§96)
Fix: one row with no vertical scroll range; horizontal scroll on overflow.
See: `docs/UI_LAYOUT.md`.

## B29 — OPEN — kill the selection bar, all of it (§§96/97)
Symptom: the selection bar and the focus frame stayed visible.
Fix: the strip takes no keyboard focus, so no focus frame is drawn.

## B32 — OPEN — ring instead of bar (§98)
Fix: superseded by the full-cell theme highlight (§134, B64).

## B30 — OPEN — progress overlaid mid-thumbnail (§96)
Fix: a native progress control centred on the mini (§§185/187/190/191,
B95/B103).
See: `docs/UI_LAYOUT.md`.

## B31 — OPEN — one compact action row (§96)
Fix: zoom out / zoom % / zoom in, Save and Stop share one toolbar; Stop is
enabled only while saving.

## B27 — OPEN — bars start at 50% again (§95)
Symptom: per-filter bars jumped to 50% with the first mini.
Fix: progress is weighted by actual work cost (`filter_progress`), so bars
start at 0.

## B33 — OPEN — preview grid out of sync (§101)
Symptom: zoomed out, the preview did not follow the original's page grid.
Fix: the preview mirrors the baseline grid exactly (`layout_from`).

## B34 — OPEN — zoom resets + processing on filter switch (§101)
Symptom: changing filters reset the zoom and showed processing.
Fix: switching filters never moves the view and never reprocesses.

## B35 — OPEN — palette enum crashed opens, popup buried it (§102)
Symptom: opening any file failed with a popup and no logged cause.
Fix: `QPalette.Mid` is read from the class, and `open_file` logs the full
traceback before showing the message box.

## B38 — OPEN — panes drifted unequal, divider invisible (§104)
Symptom: no visible divider; dragging left unequal panes.
Fix: superseded by the fixed equal panes (B43).

## B39 — OPEN — raster toggle churned all minis (§105)
Symptom: flipping force-raster visibly reprocessed every BW thumbnail.
Fix: minis, previews and sizes follow each filter's own recipe; the checkbox
edits only the selected filter's draft (§149).

## B41 — OPEN — BW minis showed color photos (§105 follow-up)
Symptom: BW thumbnails rendered the original colour page.
Fix: BW minis always show the filter's BW output.

## B40 — OPEN — sizes blank on toggle (§106)
Symptom: every size blanked on toggle, even when unchanged.
Fix: displayed minis and sizes stay visible while recomputing; only opening
a new file clears them.

## B43 — OPEN — splitter had to go (§107)
Symptom: a draggable divider between the panes never stayed put.
Fix: removed; the two panes are fixed equal.

## B44 — OPEN — clicks looked like recompute (§108)
Symptom: clicking a mini visibly reflashed the preview.
Fix: a pane skips the rebuild when it already shows that result.

## B45 — OPEN — right preview sits empty (§111)
Symptom: the right preview sat empty after open.
Fix: the right pane shows the baseline until the filter's result lands.

## B46 — OPEN — BW mini, original-looking preview (§113)
Symptom: clicking a BW mini showed the original in the big preview.
Fix: the right pane always shows the filter's saved result.

## B36 — OPEN — raster was global, on by default (§103)
Symptom: force-raster flattened text everywhere unless unticked.
Fix: FFPR is per filter and off by default.

## B37 — OPEN — raster toggle recalculated nothing (§103)
Symptom: flipping force-raster left previews and sizes stale.
Fix: superseded by B47 and the per-filter draft (§149).

## B39 — OPEN — raster toggle churned all minis (§105)
Symptom: flipping force-raster visibly reprocessed every BW thumbnail.
Fix: minis, previews and sizes follow each filter's own recipe; the checkbox
edits only the selected filter's draft (§149).

## B47 — OPEN — raster toggle resized all BW minis (§116)
Symptom: flipping force-raster recomputed every BW size.
Fix: the checkbox changes only the selected filter's draft; other filters
start no jobs.

## B48 — OPEN — panel-width slider instead of divider (§117)
Symptom: the right-panel width was set by a slider.
Fix: a draggable, non-collapsible splitter between the previews and the
panel; the two panes stay equal.

## B50 — DONE — raster-vs-text sizes questioned (§119)
The designer asked why forced raster can be smaller and ruled that no
benchmark is needed: the user chooses with the checkbox. No behaviour change.

## B49 — OPEN — squeezed right panel clipped content (§118)
Symptom: a narrow right panel clipped its content.
Fix: the panel scrolls horizontally when its content overflows.

## B51 — OPEN — rename icon + icon-only filter buttons (§120)
Symptom: the rename glyph was questioned, and Rename/Copy/Save carried words.
Fix: icon-only buttons with tooltips, using the §197 theme icons (B102).

## B52 — OPEN — mixed sizes questioned + zoomed preview text wrong (§121)
Symptom: on `images.pdf`, forced raster was far smaller than text-keeping,
and zoomed mixed-preview text did not look like the original.
Fix: superseded by §§126/127/149: the mixed path is gone and every preview
reads the saved file.

## B53 — OPEN — single path: save temp, everything reads it back (§122)
Ruling: one path only; the saver writes a file, preview, minis and sizes read
it back, and Save copies it.
Fix: one real saver, saved-file pixels, whole-file sizes and byte-copy export
(§149).
See: `docs/ARCHITECTURE.md`, `docs/FILTER_LIFECYCLE.md`.

## B54 — OPEN — OS temp dir via Qt + persistence/temp docs (§123)
Symptom: app scratch files defaulted to the repo `./.tmp/` on every OS.
Fix: runtime files live in the OS temp directory under the GUI PID and filter
UUID, with a held lock and cleanup on normal exit (§§152/153/155).
See: `docs/PERSISTENCE_AND_TEMP.md`.

## B56 — OPEN — rulings into relevant docs + UI layout doc (§125)
Symptom: layout rulings were scattered across logs.
Fix: layout canon lives in `docs/UI_LAYOUT.md`, background jobs in
`docs/ARCHITECTURE.md`.

## B55 — OPEN — elided pane titles with hover text (§124)
Symptom: long pane titles overflowed their half.
Fix: single-line headers elide with "…" and show the full text on hover.

## B57 — OPEN — mixed path was never specified: removed, option parked (§126)
Symptom: a never-specified "mixed" text-pass-through save hid behind the
raster checkbox.
Fix: removed; the idea is parked as a proposal in `docs/MIXED_MODE_OPTION.md`.

## B58 — OPEN — FFPR is optimize-images vs full-page-image (§127)
Symptom: B57's fix wrongly removed the FFPR checkbox.
Fix: FFPR restored: on flattens the page; off keeps native text and vectors
over one image canvas, never colour JPEGs in BW output.

## B59 — OPEN — DnD strip order + inline control rows (§128)
Symptom: the filter order was fixed, and Strategy/DPI/page size sat above
their controls.
Fix: strip rows drag-reorder, the dropdown and processing follow with the
selected filter first, and each control sits inline with its label.

## B60 — OPEN — DPI applies to every image transform (§129)
Symptom: images were transformed at native resolution or downscale-only,
ignoring the DPI setting.
Fix: images are composed and resized once to the exact DPI with Lanczos, up
or down, with no per-image exceptions (§§180/182).
See: `docs/COMPRESSION.md`.

## B61 — OPEN — dropdowns fit largest item + issues on topic pages (§130)
Symptom: right-pane dropdowns were not sized to their content.
Fix: dropdowns fit their widest entry, with the full text in the tooltip.
Issues are also listed on their topic pages.

## B62 — OPEN — clicking a mini moved other filters' sizes (§131)
Symptom: switching to an FFPR filter changed every other BW size.
Fix: each filter's size comes from its own recipe; selecting a filter
recomputes nothing.

## B63 — OPEN — filter sequence numbers in minis + dropdown (§133)
Symptom: no visible filter ordering.
Fix: mini captions and the dropdown show `N. label` from the live strip order.

## B64 — OPEN — full theme highlight + standard drop line (§134)
Symptom: the selected mini was marked by a ring, and DnD showed a hollow band.
Fix: a full-cell theme highlight and a solid insertion bar (B66).

## B65 — OPEN — screenshot canon, never program blind (§137)
Symptom: GUI work shipped without being looked at.
Fix: the screenshot canon, `docs/DEVELOPER_GUIDELINES.md` §5b.

## B66 — OPEN — drop indicator vertical bar (§139)
Symptom: no visible insertion line during strip drags.
Fix: a solid theme-highlight bar at the nearest divider.
See: `docs/UI_LAYOUT.md`.

## B67 — OPEN — drop Original from the filter dropdown (§140)
Symptom: Original sat in the dropdown as if it were a choice.
Fix: the dropdown lists only real filters, in strip order.

## B68 — FIXED — DESIGNER CONFIRMED — 2026-10-13 — ~~drag ghost was not uniformly translucent~~ (§§141/147)
Symptom: the live drag ghost rendered opaque, then alternated fully
transparent and fully opaque pixels.
Fix: the complete selected mini is blended once at uniform 75% opacity (§146).
Explicit designer confirmation: §147, 2026-10-13.

## B69 — FIXED — DESIGNER CONFIRMED — 2026-10-13 — ~~drag ghost lost the selected blue treatment~~ (§§142/147)
Symptom: the translucent ghost lost the selected blue treatment.
Fix: the ghost renders the complete selected cell through the strip's own
delegate (§145) at uniform 75% opacity (§146).
Explicit designer confirmation of the ghost: §147, 2026-10-13.

## B70 — FIXED — DESIGNER CONFIRMED — 2026-10-13 — ~~real drag showed only selection rectangle~~ (§§143/144/147)
Symptom: a real drag showed only the stationary selection and the insertion
bar.
Fix: synchronous paint and a press-anchored hotspot; the moving ghost shows
thumbnail and caption.
Designer confirmed in §144: "The DnD is good". Explicit ghost acceptance
reaffirmed in §147 on 2026-10-13.

## B71 — OPEN — ghost too light and drag confined to strip (§144)
Symptom: the designer asked for a stronger ghost and drops independent of the
pointer's height.
Fix: a window-level ghost at 75% (§146); filter drags anywhere in the window
snap to the nearest horizontal gap.
Ghost appearance/opacity: FIXED — DESIGNER CONFIRMED — 2026-10-13 (§147).
Drop behavior remains OPEN: §147 explicitly excludes other DnD issues from
the ghost confirmation.
See: `docs/UI_LAYOUT.md`, `tools/drag_smoke.py`.

## B72 — FIXED — DESIGNER CONFIRMED — 2026-10-13 — ~~white bottom strip in drag ghost~~ (§§145/147)
Symptom: a white band along the bottom of the drag ghost.
Fix: the view's full-row geometry comes from Qt measurements, and one delegate
renders complete cells for display and drag.
Explicit designer confirmation of the ghost: §147, 2026-10-13.
See: `docs/UI_LAYOUT.md`.

## B73 — FIXED — DESIGNER CONFIRMED — 2026-10-13 — ~~mini numbers stay stale after drop~~ (§§148/149)
Symptom: dropped minis kept old sequence numbers until another refresh.
Fix: the shared delegate paints `N. label` from the live model row; cached
icons hold only stable per-filter content.
Explicit designer confirmation in §149 on 2026-10-13.
See: `docs/UI_LAYOUT.md`, `docs/TODO.md` §148.

## B74 — OPEN — first filter selection starts another preview job (§149)
Symptom: a mini already showed a processed filter, but first selection
started "Rendering preview…" again.
Fix: all filters are real-file jobs queued on open; selection, view changes
and reorder start no filtering.
See: `docs/FILTER_LIFECYCLE.md`, `docs/TODO.md` §150.

## B75 — OPEN — displayed amounts are not final filtered PDF sizes (§149)
Symptom: displayed sizes were sums of estimated payloads, not final PDF sizes.
Fix: each size is the byte count of the complete saved PDF, which preview,
minis and export also read.
See: `docs/ARCHITECTURE.md`, `docs/FILTER_LIFECYCLE.md`, `docs/TODO.md` §150.

## B76 — OPEN — no saved/live draft separation or dirty marker (§149)
Symptom: no saved/live draft separation and no dirty marker.
Fix: live controls edit one debounced draft marked `*`; selection never
changes recipes.
See: `docs/FILTER_LIFECYCLE.md`, `docs/UI_LAYOUT.md`, `docs/TODO.md` §151.

## B77 — OPEN — unsaved filter switching loses edits and artifact ownership (§149)
Symptom: leaving an unsaved filter lost its edits and file ownership.
Fix: Save / Save As… / Discard / Cancel before leaving a dirty filter, with
safe ownership of saved, draft and in-flight files.
See: `docs/FILTER_LIFECYCLE.md`, `docs/PERSISTENCE_AND_TEMP.md`, `docs/TODO.md` §152.

## B78 — OPEN — temp sweeper removes live worker directories (§§123/149/150)
Symptom: the temp sweeper removed live worker directories.
Fix: one held process lock per PID directory; sweeping skips live processes
and fresh directories.
See: `docs/PERSISTENCE_AND_TEMP.md`, TODO §§155/157/158.

## B79 — OPEN — real saved image streams fail decoding (§§122/149/150)
Symptom: saved JPEG/JPX streams carried an extra Flate wrapper and failed
decoding.
Fix: encoded streams are inserted with `compress=False`, and Zopfli writes
validated zlib output.
See: `docs/COMPRESSION.md`, `docs/FILTER_LIFECYCLE.md`, TODO §156.

## B80 — OPEN — filters need unique persistent UUIDs and UUID-named directories (§155)
Symptom: filters lacked unique persistent UUIDs and UUID-named directories.
Fix: persistent UUIDv4 identities with duplicate repair on load; generated
files live under the filter UUID inside the PID directory, and copies get new
UUIDs.
See: `docs/PERSISTENCE_AND_TEMP.md`, `docs/FILTER_LIFECYCLE.md`, TODO §160.

## B81 — FIXED — DESIGNER CONFIRMED — 2026-10-14 — ~~reordered mini clicks flicker wrong identities/captions~~ (§§156/157/159)
Symptom: after reorders, mini clicks flickered wrong names from about mini 5.
Fix: one Qt `startDrag` hook with UUID-only drag data and a single `moveRow`;
the order lives only in the model.
Explicit designer acceptance in §159 on 2026-10-14 (America/New_York).
See: `docs/UI_LAYOUT.md`, TODO §161.

## B82 — OPEN — excessive bottom whitespace in minis strip (§159)
Symptom: excessive whitespace below the minis.
Fix: the cell height is derived from its content, with equal 4px padding
above and below.
See: `docs/UI_LAYOUT.md`, TODO §164.

## B83 — OPEN — white mini pages blend into strip background (§159)
Symptom: white mini pages blended into the strip background.
Fix: the strip ground is the theme's Window colour slightly darkened
(`darker(105)`), shared by the ghost.
See: `docs/UI_LAYOUT.md`, TODO §165.

## B84 — OPEN — unsaved-filter discard has close-oriented wording (§160)
Symptom: the unsaved-filter dialog's Discard could read "Close without saving".
Fix: the button says "Discard Changes" and keeps the standard Discard role.
See: `docs/FILTER_LIFECYCLE.md`, TODO §166.

## B85 — OPEN — Escape after a mini click leaves the wrong selection (§161)
Symptom: Escape after a mini click left the attempted target highlighted.
Fix: Qt's native input handlers finish with view signals blocked, then one
completed selection notification reaches the switch controller. Smoke tests
under Xvfb must return focus explicitly after a modal closes (no window
manager).
See: `docs/FILTER_LIFECYCLE.md`, TODO §167.

## B86 — OPEN — explicit revert changes affordance missing (§162)
Symptom: no explicit Revert Changes control.
Fix: a standard document-revert button beside the dropdown, enabled only for
the active draft, discards it and reuses the saved result.
See: `docs/UI_LAYOUT.md`, `docs/FILTER_LIFECYCLE.md`, TODO §168.

## B87 — OPEN — zoom-out centers phantom columns; original/preview disagree (§§164/165)
Symptom: zoomed out, pages centred on phantom columns, and the original and
preview layouts disagreed.
Fix: one occupied-column grid calculation against Qt's maximum viewport owns
both panes and the minis; peer zoom reflows geometry.
See: `docs/UI_LAYOUT.md`, `docs/DESIGN.md`, TODO §§170/171.

## B88 — FIXED — DESIGNER CONFIRMED — 2026-10-14 — slow resize/divider feedback (§§166/167)
Symptom: resizing to half screen triggered 5–10 seconds of pane and divider
movement.
Fix: headers elide at paint time without changing their size hints, and
window resizes no longer change header text.
Designer explicitly confirmed in §167: "Ok, this is confirmed fixed, thank you."
Acceptance scope is the resize/divider feedback issue, not unrelated issues.
See: `docs/UI_LAYOUT.md`, TODO §172.

## B89 — OPEN — BW text-preserving outputs much larger than FFPR (§168)
Symptom: on `images.pdf`, BW with text kept was much larger than FFPR.
Fix: FFPR off composes all image content into one canvas under native text
and vectors (§§169–171).
See: `docs/COMPRESSION.md`, `docs/DESIGN.md`, TODO §§174/178.

## B90 — OPEN — FFPR overwrites earlier pages with the final image (§168 audit)
Symptom: FFPR pages all showed the last page's image (a shared placeholder
xref was overwritten).
Fix: each encoded page image gets its own xref before placement, and every
saved page is checked against its expected pixels.
See: `docs/COMPRESSION.md`, TODO §175.

## B91 — OPEN — display smooths real bitmap content, including FFPR (§§172/173)
Symptom: the display smoothed real bitmap content, including FFPR.
Fix: exact readback with no anti-aliasing, interpolation or decoder
averaging; native shapes redraw at device resolution (§§174/175).
See: `docs/UI_LAYOUT.md`, `docs/COMPRESSION.md`, TODO §179.

## B92 — OPEN — color processing creates dark image-edge halos (§177)
Symptom: colour processing created dark halos at image edges: hidden black
under transparent pixels was mixed in during resizing.
Fix: compose in full colour first, then resize once, then transform
(§§180–182).
See: `docs/COMPRESSION.md`.

## B93 — FIXED — DESIGNER CONFIRMED — 2026-10-14 — low-color nearest mapping (§183)
Symptom: low-colour palettes mapped some colours to white instead of the
nearest palette colour.
Fix: palette fitting is separate from exact nearest-colour assignment at full
resolution. A median-cut palette passed the nearest-colour tests but wasted
slots on near-white variants, so it was not shipped.

Explicit designer confirmation, §184, 2026-10-14 (America/New_York):
> yes, much better, what was the problem?

Confirmation scope: the reported low-color appearance/mapping improvement.
It does not close the independently tracked debounce policy or all other
color/native-overlay fidelity issues.

## B94 — OPEN — unify and verify filter-edit debounce across controls (§183)
Symptom: filter edits needed one consistent debounce across controls.
Fix: one shared 300ms trailing timer for every filter edit.
See: `docs/FILTER_LIFECYCLE.md`.

## B95 — FIXED — DESIGNER CONFIRMED — 2026-10-14 — ~~mini progress appearance~~ (§§185/187/190/191/192)
Symptom: the mini progress bar was hand-painted, narrower than the cell and
without a white backing.
Fix: a native progress control drawn by the strip delegate after the
selection wash.

Designer confirmation (§192): "Ok, this is good." Exact full message is in
`docs/DESIGNER_VERBATIM.md`. Scope: native progress styling, 4px highlight
inset, 50% larger bar/percentage, no extra white padding and whole-mini-frame
centering. Local date America/New_York. This does not confirm B96/B97 or other
DnD/layout/filter issues. B103 later changes the enlargement to 25%.

## B96 — OPEN — staggered main-region edges and redundant minis title (§188)
Symptom: staggered main-region edges and a redundant minis title.
Fix: one shared 4px region spacing and a zero-margin PreviewPair; the title
row is removed.
See: `docs/UI_LAYOUT.md`, TODO §191.

## B97 — OPEN — Save As from a dirty-filter switch fails to select its new copy (§189)
Symptom: Save As from a dirty-filter switch selected the original target
instead of the new copy.
Fix: the dirty-filter resolution carries the new copy's ID, and one
activation commit selects and reveals it.
See: `docs/FILTER_LIFECYCLE.md`, TODO §192.

## B98 — OPEN — configuration block lacks a matching header (§192)
Symptom: the configuration block lacked a header matching the previews.
Fix: one shared header/content composition for all three regions, with
"Configuration" outside the scroll area.
See: `docs/UI_LAYOUT.md`, TODO §196.

## B99 — OPEN — PBM leading binary whitespace can break production JBIG2 input (worker study finding)
Symptom: a PBM input starting with a newline byte broke the JBIG2 encoder, so
lossless JBIG2 was silently lost.
Fix: one shared encoder feeds 1-bit PNG to `jbig2 -p` for BW and colored
stencils; a failure is an error, never a Flate fallback.
See: `docs/JBIG2.md`, TODO §206.

## B100 — OPEN — all-black error placeholder can pass the production JBIG2 pixel gate (worker study finding)
Symptom: an all-black error placeholder could pass the JBIG2 pixel check.
Fix: the shared gate also rejects new MuPDF decode diagnostics.
See: `docs/JBIG2.md`, TODO §206.

## B101 — OPEN — redundant mini working placeholders (§195)
Symptom: minis showed redundant "working…" placeholders.
Fix: unavailable slots stay blank and progress bars show the work; cached
images and sizes stay visible during edits.

## B102 — OPEN — custom action glyphs mixed with desktop-theme icons (§§196/197)

Designer §200 explicitly REJECTS the delivered icon appearance (2026-10-14).
The technical provider repair is not acceptance. A coded stock-icon comparison
lab is requested in B104; do not auto-choose another production icon set.

Symptom: custom glyphs were mixed with theme icons, and some actions had no
icon.
Fix: one theme-first icon provider with a licensed Breeze SVG fallback.
See: `docs/ICONS.md`, TODO §201.

## B104 — OPEN — designer cannot compare and identify preferred stock icons (§200)
Symptom: the designer cannot compare and choose stock icons.
Fix: View → Icon Lab… with genuine stock families, permanent codes and a
copyable per-action selection; it never changes production icons.
Remaining: the designer's icon choices.
See: `docs/ICON_LAB.md`, TODO §203.

## B103 — OPEN — refine mini progress enlargement to 25% (§§198/199)
Symptom: the mini progress enlargement must be 25% (1.25×), not 1.5×.
Fix: one shared 1.25× height and font factor. B95's confirmation covers the
earlier version, not this refinement.
See: TODO §202.

## B105 — OPEN — compression locked to seed filter; ambiguous Strategy (§203)
Symptom: compression was locked to the seed filter, and "Strategy" was
ambiguous.
Fix: a six-choice Image compression selector, an authoritative saved/draft
mode and the "Threshold method" label; no hidden codec substitution.
See: `docs/COMPRESSION.md`, TODO §206.

## B106 — OPEN — native compression not selectable or benchmarked (§§204/205)
Symptom: native stream compression was not selectable or benchmarked.
Fix: a separate PDF streams selector (Best by default since §257); empty
native streams stay uncompressed because MuPDF 1.28.2 mishandles empty
Brotli streams.
See: `docs/NATIVE_STREAM_COMPRESSION.md`, TODO §208.

## B107 — OPEN — native callback cancellation becomes an unpickleable worker error (worker audit finding)
Symptom: cancelling during close raises `CancelledError` inside a native
MuPDF callback; the wrapped error cannot be pickled across the process pool,
so a cancelled draft is logged as an artifact failure.
Remaining: handle cancellation on the correct side of the native callback
boundary and return only serializable worker failures, preserving genuine
decode errors, saved/draft ownership and partial-file cleanup. A repair needs
a real native-callback plus process-pool cancellation regression, not a
mocked Python-only exception. Not implemented.

## B108 — OPEN — colored-stencil page-edge repair implemented; designer confirmation pending
Symptom: colored stencils lost the rightmost pixel column on fractional-size
pages when embedded as nested page Forms.
Fix: stencils are painted directly in the page with the same placement as
Indexed images (§224).
See: `docs/COMPRESSION.md`, TODO §226.

## B109 — OPEN — orphaned ActualText repair implemented; designer confirmation pending
Symptom: removing an image left whitespace ActualText with no positioned
content, adding MuPDF warnings.
Fix: `core/marked_content.py` removes only that disconnected whitespace
replacement text, keeping MCIDs, tags and drawing operators.
See: `docs/COMPRESSION.md`, TODO §226.

## B110 — OPEN — native-filter write-back repair implemented; designer confirmation pending
Symptom: BW preparations intermittently kept original colour photos above the
new canvas.
Fix: the compositor sets every MuPDF filter option explicitly, including
`no_update = 0`, which the wrapper sometimes left uninitialized.
See: `docs/COMPRESSION.md`, TODO §§226/227.

## B111 — OPEN — native cleanup loses inherited text rendering state at Form calls
Symptom: native cleanup dropped `0 Tr` before a Form call, so map labels
inherited invisible text mode.
Fix: `core/native_layer.py` edits native content with MuPDF's lexer and
parser, removing only replaced image paint and backdrops, with no final
sanitizing pass.
See: `docs/COMPRESSION.md`, TODO §230.

## B112 — OPEN — stale accessibility references retain replaced original images
Symptom: structure-tree references kept replaced original images in the
output.
Fix: native content stays in its original page/Form owners with pruned
resources, and complete-file validation rejects replaced images reachable
through non-page references.
See: `docs/COMPRESSION.md`, TODO §231.

## B113 — OPEN: no-image benchmark preparations fail when assigning IDs to an xref-stream PDF
Symptom: no-image benchmark preparations failed when assigning IDs to an
xref-stream PDF (§229).
Fix: the no-image entry uses the existing container normalizer
(`open_for_id_change`).
See: `docs/COMPRESSION_BENCHMARKS.md`.

## B114 — OPEN — same-DPI JBIG2 flow resamples and increases an already compressed scan
Symptom (§233): the same-DPI JBIG2 flow resampled and grew the already
compressed `examples/scan-jfk-poor-copies.pdf`.
Fix: `_source_dpi` keeps fractional image and mask density instead of rounding
up, so a same-DPI no-op preserves every source sample (§235).
See: `docs/JBIG2.md`, `docs/COMPRESSION_BENCHMARKS.md`, TODO §238.

## B115 — OPEN — corpus inventory mistakes extracted PNG/TIFF for the PDF image codec
Symptom: the corpus inventory read extracted PNG/TIFF file types as the PDF
image codec.
Fix: the classifier reads stored `/Filter` values, and the Poppler fallback
uses its encoding column.
See: `examples/README.md`, TODO §239.

## B116 — OPEN — native-overlay brochure output obscures some source artwork
Symptom (worker observation): on the brochure's first page,
native-overlay output hid two inset photos and the header emblem.
Fix: one source-order backdrop plan (`core/backdrops.py`) keeps flat panels
that enclose a later image below the canvas instead of replaying them above it.
See: `docs/COMPRESSION.md`, `tools/check_b116.py`, TODO §265.

## B117 — OPEN — JPEG2000 q75 is not equivalent to JPEG q75 (§272)
Symptom (§272): no JPEG2000 quality setting was equivalent to JPEG q75, which
the benchmarks and users need. A fixed `101 − q` ratio cannot follow JPEG,
whose size follows content.
Fix: JPEG2000 Quality maps to one PSNR target per 512-pixel tile, calibrated
so its median quality equals JPEG's at the same number (q75 → 44.0 dB), with
standard packages only (§§278/284). Single documents still differ; the
benchmarks list the gaps. There is no automatic choice between the two (§287).
See: `docs/LOSSY_IMAGE_QUALITY.md`, TODO §266.

## B118 — OPEN — verbatim record inexact and documentation corpus disorganized (§273)
Symptom (§273): the developer guidelines are poorly done; the designer's
verbatim words must be exact, and the verbatim recordings are not well
organized.
Fix: entries from §272 on hold one message each in fenced `text` blocks with
a source line; §§139–141 are exact; the missed strip-caption complaint is
§288. Under §290 the log header marks earlier entries as unclear source,
unclear entries superseded or reconfirmed by clear rulings are deleted, and
the rest stay until new rulings replace them. §§199/226 are labelled as
selected options. The guidelines' product rules are a short topic list.
See: `docs/DESIGNER_VERBATIM.md`, `docs/DEVELOPER_GUIDELINES.md`.
