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

## B27 — OPEN — bars start at 50% again (§95)
Symptom: per-filter bars jump to 50% with the first mini and sit through the
slow amounts. Cause: the 50/50 phase split weighed fast minis like slow
encodings. Fixed: cost-weighted completions (15/85, current-job arrivals
only) via a unit-tested `filter_progress` — bars always start at 0.
