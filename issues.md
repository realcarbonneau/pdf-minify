# ISSUES — designer complaint log (confirmation-gated)

Rule (designer §90): every past malfunction complaint is listed here, numbered.
An item is crossed out ONLY after the designer confirms the fix. Fixed in code
but unconfirmed stays OPEN. Verbatim rulings live in
`docs/DESIGNER_VERBATIM.md` (§ numbers below); implementation notes in
`TODO.md`.

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
