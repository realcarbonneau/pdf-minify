# TODO — substantive project requirements (stable IDs, NEVER renumber)

Format (designer rulings §§16/218): no checkboxes. Open items carry full detail.
Completed items are stubbed: request struck through, stub summary, cross-refs
to the final docs/code that implement it. Dropped items move to
[DROPPED.md](DROPPED.md) with reasons. Knowledge is referenced, never redone.
Entries reference [DESIGNER_VERBATIM.md](DESIGNER_VERBATIM.md); the two logs have independent
numbering, so use each entry's explicit designer-§ reference. Historical
duplicate request numbers already exist in checkpoint `8d7f095` (18 repeated
headings among §§60–79). They are preserved, not silently renumbered; identify
those entries by title/scope as well as number. New entries continue above
the highest previously allocated number, including removed entries. The next
new TODO ID is 248. Routine execution requests are not TODOs (§218).

Current location is `docs/TODO.md` (designer §216). Paths in historical
backtick references are repository-root paths unless stated otherwise;
old descriptions of the previous root placement are historical, not current
instructions. Explicitly removed unrelated entries leave numbering gaps (§218).

## 3 — DONE
~~Full app-vision brief (scans → BW threshold + image recompression, max compression default, ESC cancel, md docs with notes/ideas/tests).~~
Stub: vision captured; 5 root analysis docs written.
See: `docs/00_OVERVIEW.md`, `docs/ARCHITECTURE.md`, `docs/PDF_OPTIMIZATION_NOTES.md`, `docs/UX_DESIGN.md`, `docs/TEST_PLAN.md`.

## 4 — DONE
~~Yes, JBIG2, summarize your suggestions to me.~~
Stub: JBIG2 compression guidance is recorded in the research notes.
See: `docs/PDF_OPTIMIZATION_NOTES.md`.

## 5 — DONE
~~lok, no jxl. Rank frameworks by dependency size and OS/WM range.~~
Stub: JXL-in-PDF dropped; frameworks ranked smallest→largest with OS/WM coverage.
See: `docs/PDF_OPTIMIZATION_NOTES.md`, `docs/DROPPED.md` (D1).

## 6 — DONE
~~Picky smooth custom UI: pan, zoom in/out mouse scroll, next/prev page, DnD, etc.~~
Stub: ruled PySide6 + QGraphicsView (Tk Canvas too janky for the standard).
See: `docs/ARCHITECTURE.md`, `docs/UX_DESIGN.md`.

## 7 — DONE
~~Seems like Qt is really solid, can you double check?~~
Stub: verified 2026-10-09 — Qt 6.8.2 in trixie, PySide6 LGPL, QPdfView/QGraphicsView fit, LXDE/X11 OK.

## 8 — DONE
~~Start with Qt; everything local in this directory; tell me what is local vs system packages.~~
Stub: local scaffold built; local-vs-system split documented.
See: `pdf_minify/`, `.venv/`, `requirements*.txt`, `setup_local.sh`, `docs/DEPENDENCIES.md`, `README.md`.

## 9 — DONE
~~Verbatim comments in a design doc, docs dir, dev guidance doc, preset list like camera photo filters with small previews, click → main original+preview side by side H/V, same for filter thumbnails, all as menu view options.~~
Stub: docs dir + verbatim file + dev guidance + 8-preset strip + View menu (main H/V/single, filters film/rail/grid) built and smoke-tested.
See: `docs/DESIGNER_VERBATIM.md`, `docs/DEVELOPER_GUIDELINES.md`, `docs/DESIGN.md`, `pdf_minify/core/presets.py`, `pdf_minify/ui_qt/app.py`.
Open follow-up (offered, awaiting designer ruling): live-rendered 96px thumbnail minis in the strip (currently label rows).

## 10 — DONE
~~Generally forcing alll images on the page and page rasterizing to 300dpi, and 8.5x11, but that also would be options on the main screen.~~
Stub: force-raster + 300dpi + Letter defaults, all three as main-screen controls (DPI combo, page-size combo, force checkbox); force-off passes text pages through.
See: `pdf_minify/core/pipeline.py`, `pdf_minify/core/presets.py`, `pdf_minify/ui_qt/app.py`, `tests/test_pipeline.py`.

## 11 — DONE
~~In the docs, always call the operator/user the designer.~~
Stub: docs prose normalized to "the designer"; verbatim quotes untouched.
See: `docs/DESIGN.md` (rulings section), `docs/DEVELOPER_GUIDELINES.md`, `docs/DESIGNER_VERBATIM.md`.

## 12 — DONE
~~Finish prior work + every request in TODO.md, numbered, never renumbered.~~
Stub: this log exists; prior work finished per item.
See: `TODO.md`.

## 13 — DONE
~~Dev guidance carries general-guideline rulings incl. TODO instructions.~~
Stub: general rulings live in dev guidance.
See: `docs/DEVELOPER_GUIDELINES.md` (§0).

## 14 — DONE
~~Log important app activity to stdout and provide --debug diagnostics; document the developer workflow.~~
Stub: INFO stdout logging everywhere, `--debug` adds versions/argv/timings, `./run.sh` launcher + `.tmp/` log, offscreen review shots.
See: `pdf_minify/ui_qt/app.py` (`setup_logging`), `pdf_minify/__main__.py`, `docs/DEVELOPER_GUIDELINES.md` (§6), `run.sh`, `tools/shot.py`.

## 15 — DONE
~~Keep project work local and scratch in gitignored ./.tmp/.~~
Stub: project-local scratch policy is documented and generated artifacts are ignored.
See: `.tmp/`, `.gitignore`, `run.sh`, `tools/make_demo.py`, `tools/shot.py`.

## 16 — DONE
~~TODO format ruling + dropped-ideas doc (verbatim §16).~~
Stub: this file's format + dropped log established.
See: `TODO.md` (this file), `docs/DROPPED.md`, `docs/DEVELOPER_GUIDELINES.md` (§0).

## 17 — DONE
~~call it the full developper guidlines md doc~~
Stub: dev guidance renamed to its full name.
See: `docs/DEVELOPER_GUIDELINES.md`.

## 18 — DONE
~~move most of your docs to the docs dir please~~
Stub: analysis docs moved to `docs/`; `README.md` + `TODO.md` stay at root; all xrefs fixed.
See: `docs/`, `README.md`.

## 19 — DONE
~~docs-lead ruling (verbatim §19).~~
Stub: all doc xrefs corrected first, ruling recorded, then verification.
See: `docs/DEVELOPER_GUIDELINES.md` (§0).

## 22 — DONE
~~page zoom, pan, etc is always synced on both panes~~
Stub: original/preview panes mirror zoom + pan/scroll both ways (peer sync
with reentrancy guard); covered by sync test.
See: `docs/DESIGN.md` (Behavior), `pdf_minify/ui_qt/viewer.py`,
`tests/test_viewer_sync.py`.

## 23 — DONE
~~left side is baseline, so no preview of basline, right side is per filter.~~
Stub: left pane fixed baseline; right pane shows selected filter; strip renders
a live mini per filter of the current page (icon mode, preset params).
See: `docs/DESIGN.md` (Behavior), `pdf_minify/ui_qt/app.py`
(`_render_filter_minis`), `tests/test_minis.py`, `.tmp/shot-main.png`.

## 24 — DONE
~~find a few public pdf docs that are representative test cases, not too big, 1
to 10 pages, 200k to 10 mb, put in examples dir in this repo~~
Stub: 4 pdf.js-corpus PDFs committed (photo/mixed/vector/vector-stress) +
`examples/README.md` with profiles + spot metrics.
See: `examples/`, `examples/README.md`.

## 25 — DONE
~~also ctl mouse scroll is up/down? Or mouse scroll is page scroll and ctl wheel
is zoom, I think that is more common ui, no?~~
Stub: common convention adopted — plain wheel scrolls, Ctrl+wheel zooms,
both panes stay synced. Covered by wheel test.
See: `pdf_minify/ui_qt/viewer.py`, `tests/test_viewer_sync.py`,
`docs/DEVELOPER_GUIDELINES.md`, `docs/ARCHITECTURE.md`.

## 26 — DONE
~~the page viewer should be continuous by default, with a gap between paged.
No page list to the left. Zoom out should aso autowrap to multiple pages per
side if it fits in the window width.~~
Stub: both panes are continuous scrollers (24px gap, autowrap grid by
viewport/zoom, synced zoom+scroll); page list removed, status shows Page N of
M; PgUp/PgDn jump pages; minis follow the top-visible page.
See: `docs/DESIGN.md` (Behavior), `pdf_minify/ui_qt/viewer.py`
(`ContinuousDocView`), `pdf_minify/ui_qt/app.py`, `tests/test_continuous.py`,
`.tmp/shot-main.png`.

## 27 — DONE
~~Did you find example pdfs? Your pdf file is not a good example at all.~~
Stub: yes — 4 real PDFs were already in `examples/` (item 24); the synthetic
`.tmp/demo.pdf` is retired from demos. Live app + screenshots switched to
`examples/images.pdf` (photo-heavy); window confirmed on the designer display.
See: `examples/`, `examples/README.md`.

## 28 — DONE
~~use a 3 page example for the tests please.~~
Stub: `examples/filled-background.pdf` (3 pages, 401KB, pdf.js corpus) —
probed ~30 corpus files, only 3-pager in the 200KB–10MB band; exercises
continuous scroll, page jumps, and multi-page render.
See: `examples/`, `examples/README.md`.

## 29 — OPEN (full detail, partial progress)
Designer: only 5 examples; want real-world types — deeds, research papers,
documentations, appliance manuals, etc. Landed: recorded deed
(`deed-brevard.pdf`, scan-like), appliance quick-start
(`manual-maytag-dryer.pdf`), government form (`form-fw9.pdf`), research paper
(`paper-arxiv-1406.2661.pdf`) — 9 examples total. Still open: software/project
documentation. (Two requested-type files sit under the 200KB floor — noted in
`examples/README.md`.)

## 30 — DONE
~~Also, why is original still in the filters? Or did you not relaunch the
latest version?~~
Stub: it was code, not a stale launch (relaunches verified by pid + log).
Strip now shows only the 7 real filters (passthrough excluded — left pane is
the baseline); preset combo keeps all 8 modes for Save; strip↔preset mapping
is by id. Covered by strip-sync test; live instance relaunched on the build.
See: `pdf_minify/ui_qt/app.py`, `tests/test_minis.py`, `docs/DESIGN.md`.

## 31 — DONE
~~why are you using that terrible pdf as a default?~~
Stub: default demo is now `examples/images.pdf` (photo-heavy); `run.sh` with
no args opens it; `tools/shot.py` default updated too. `filled-background.pdf`
kept only as the 3-page scroll test.
See: `run.sh`, `tools/shot.py`.

## 32 — DONE
~~the app should show the final size of each filter below it. It should also
show the small preview which is mirroring the current view on the original.
Remove the left panel and put the options in the menu or in the right panel,
there will only be one tool panel and a menu.~~
Stub: strip minis carry real encoder-based est. sizes; OverviewMap navigator
(baseline page + viewport rect, click/drag to jump); left panel deleted —
File menu (Open/Save/Quit), single right panel, page/progress/status in the
status bar.
See: `docs/DESIGN.md` (Behavior), `pdf_minify/ui_qt/app.py`,
`pdf_minify/ui_qt/overview.py`, `pdf_minify/ui_qt/viewer.py`,
`tests/test_minis.py`, `tests/test_continuous.py`, `.tmp/shot-main.png`.

## 33 — DONE
~~Don't show the tooltips at the top, waste of space, we will find another
place for that~~
Stub: pane/strip header labels removed; hints live as zero-space hover
tooltips pending final placement.
See: `pdf_minify/ui_qt/app.py`.

## 34 — DONE
~~For now, fit everything you can on the right side panel or in the menu.~~
Stub: done as part of item 32 (File menu + single right panel + status bar).
See: `pdf_minify/ui_qt/app.py`.

## 35 — DONE
~~document, compile and collect these, document in an examples md doc with
descriptions, view them also. [corpus brief]~~
Stub: `tools/corpus/` (27-record manifest.json + fetch_and_validate.py →
corpus_report.csv OK/OUT_OF_RANGE/ERROR); 26/27 fetched (CDC stacks 403s
scripts — noted); committed to `examples/` (~127MB, 35 files); full table +
codecs + spot metrics in `examples/README.md`; contact sheet viewed.
New band recorded: 3–50p / 200KB–50MB supersedes §24 for additions.
See: `tools/corpus/`, `examples/`, `examples/README.md`, `.tmp/contact.png`.

## 36 — DONE
~~[historical scan set brief]~~
Stub: 10 scans fetched (NACA ×4, NARA schedule, JFK ×5); LoC leads logged
manual in README (no direct PDFs). Faint/dark/ruled scans are now mandatory
regression tests — thresholds must never blank or flood a page.
See: `examples/scan-*.pdf`, `tests/test_regression_scans.py`.
Remaining queue (not yet ruled on): JBIG2 wiring, software
documentation example.

## 37 — DONE
~~don't freeze the whole app when doing the previews, do it in background [...]
(full §37 in verbatim)~~
Stub: FilterWorker (QThread manager) runs minis→estimates→preview in separate
spawn-context PROCESSES capped at half the cores (real cap, crash-isolated),
results applied by generation; minis mirror the viewport; pan/zoom is pure
view; progress per filter + status bar. Hardened along the way: never drop the
last ref of a running QThread (Qt fatal — track in-flight workers); preview
application suppresses sync cascades and preserves scroll/zoom; splitter
stretch keeps panes equal. Sort-filters/max-auto deferred.
See: `pdf_minify/ui_qt/jobs.py`, `docs/DESIGN.md`.

## 38 — OPEN (full detail)
Designer audit: consolidate to ~22–23 (reserve: Kepler, Swift, 2 JFK, TM972,
formulas + others), add camera-photo PDFs (DocShadow subset, SmartDoc),
DIBCO quantitative tests, structural classes (PDF/A, JBIG2-done, OCR text),
processing ladder, automatic "B&W not recommended" recommendation.

## 40 — DONE
~~change the various names and stubs that has pdf-reducer, to
pdf-minimalist.~~
Stub: `git mv pdf_reducer/ pdf_minimalist/` + all `from pdf_reducer`
imports → `pdf_minimalist` (8 test files); display strings/docs already
renamed; `run.sh` + `tools/shot.py` now resolve; `python -m pdf_minimalist`
verified; 27/27 tests green. Historical `TODO.md` stubs keep old paths.
See: `pdf_minify/`, `tests/`, `run.sh`, `tools/shot.py`.

## 41 — DONE
~~also, why does it say local? Ref: pdf-reducer (local)~~
Stub: title → `pdf-minimalist`, `LOCAL` → repository-owned; part of the
item-40 rename, verified in `README.md` / `DEPENDENCIES.md` /
`DEVELOPER_GUIDELINES.md`.
See: `README.md`, `docs/DEPENDENCIES.md`, `docs/DEVELOPER_GUIDELINES.md`.

## 43 — DONE
~~the progress bar is supposed to be for EACH filter.~~
Stub: each strip mini now paints its own bar (`working…` 0.0 → mini 0.5 →
`est. X` 1.0, bar hidden when done); status bar keeps only the aggregate.
Verified by offscreen run (all 7 reach 1.0, icons non-null).
See: `docs/DESIGN.md` (Behavior), `pdf_minify/ui_qt/app.py`
(`_paint_strip_item`, `_filter_prog`), `pdf_minify/ui_qt/jobs.py`.

## 44 — DONE
~~when I was clicking on a filter preview, it seemed to be restarting it
processing, but that is incorrect, it should be processed once and only
reprocessed if there is a change of the file or change in the filter
specifications.~~
Stub: process-once cache — file identity (path+mtime+size) + top page +
spec tuple (preset/mode/dpi/strategy/t); strip/preset clicks hit
`_try_apply_cached` with no new job; `FilterWorker` takes
`need_mini/need_est/need_preview` so partial misses only compute what's
missing. Verified: cache-hit dispatch bumps no gen, same-row click no job,
spec change reprocesses + grows cache 1→2; 27/27 tests green.
See: `docs/DESIGN.md` (Behavior), `pdf_minify/ui_qt/app.py`
(`_file_key`, `_dispatch_filters`, `_try_apply_cached`, `_preview_cache`),
`pdf_minify/ui_qt/jobs.py`.

## 45 — DONE (superseded by 48)
~~Previews are truncated half page or something, when they should should the
exact preview seen in the preview window.~~
Stub: interim fix rendered minis full-page (killed the top-slice truncation,
verified offscreen). Designer §48 then clarified the ruling: minis must mirror
the main view's exact framing (multi-page grid included), each from its own
filter's preprocessed file — implemented under item 48.
See: `docs/DESIGN.md` (Behavior), item 48.

## 46 — DONE
~~Also, make the thumbnail preview box clear and the filter and size below it
in smaller characters and aso clearly divided~~
Stub: bordered preview frame + divider line + small caption (name dark, est
gray) painted per mini; verified offscreen (`shot-main.png`).
See: `pdf_minify/ui_qt/app.py` (`_paint_strip_item`).

## 47 — DONE
~~again, why is there reprocessing when I scroll????~~
Stub: scroll/pan/zoom/page turns are pure view now — never a job. Cause was
the single-page mini/est cache wiped on every top-page change; fixed by the
item-48 redesign (per-preset full-document caches + reframe). Verified
offscreen on a 6-page doc: page turn and scrollbar moves bump no generation,
no job object.
See: `pdf_minify/ui_qt/app.py` (`_reframe_minis`, `_on_page_changed`).

## 48 — DONE
~~Still wrong! Thumbnails should be a mini version of exactly the current view
of the larger window. [...] each preview shows exactly that from it's own
filter view (internal, no shown, file preprocessed in bg at the start or from
the latest change).~~
Stub: every preset × every page preprocessed once in background (mini-pages
~200px + est sizes for all pages; 150dpi preview pages for the active spec);
each mini composites exactly the synced main-view framing from its own
preset's pages (`frame_view`); reframe on scroll with zero jobs; new jobs
only on file/spec change; preview cache capped at 2 specs. Verified: 27/27
tests green + offscreen 6-page check (framing aspect == main view, click
dispatches exactly one preview-only job, click-back cached).
See: `docs/DESIGN.md` (Behavior), `pdf_minify/ui_qt/jobs.py`
(`mini_page_task`, `frame_view`, `FilterWorker`),
`pdf_minify/ui_qt/app.py` (stores, `_reframe_minis`, `_dispatch_filters`).

## 60 — DONE
~~Above the original and the applied preview, show the relevant information
for each [...] it should say Original with a new key information, including
the file size.~~
Stub: splitter halves carry headers — left `Original · name · size · 100% ·
N pages`, right `label · recipe · size (%)`, updated with strip data.
Verified offscreen + suite green.
See: `pdf_minify/ui_qt/app.py` (`_update_pane_headers`).

## 61 — DONE
~~Also, in the thumnails and top lines, shows the size percentage, like
original 230kb 100%, filter 1, 23kb 10%.~~
Stub: every amount carries % of original (`_sized`: `23KB (10%)`, left header
`100%`); original bytes cached at open. Verified: suite asserts `%` on all 8
+ offscreen.
See: `pdf_minify/ui_qt/app.py` (`_sized`).

## 68 — DONE
~~File name should be the firlst list of the right side block.  Original and
size stays above the first previous main window~~
Stub: file name (bold) heads the right panel under a `File:` label, set on
every open; left header untouched. Verified: suite green + offscreen.
See: `pdf_minify/ui_qt/app.py` (`file_label`).

## 79 — DONE
~~why do you have encode and codec on different lines, very incoherent, follow
modern best practices please!~~
Stub: one label everywhere — Filter details opens with `Codec:` as its
consistent first line in all modes (`JBIG2`, `JPEG`, `JPEG2000`,
`Flate (palette)`); same label set/order per mode (modern readout practice:
consistent, scannable, units on every value). The stale live build still
showed the old `Encode:` line. Verified: suite green, relaunched.
See: `pdf_minify/ui_qt/app.py` (`_refresh_details`).

## 82 — DONE
~~Still, why is codec sometimes the first line and other times the last
line!!??? This is bad design!  There will be one codec per filter, all common
filter properties must show in the same stable sequence at the start, and
custom codec specific options after.~~
Stub: fixed properly — Codec opens every mode (BW had it last), then common
properties, then codec-specific options; new test asserts the first line for
all 11 presets. Verified: suite green.
See: `pdf_minify/ui_qt/app.py` (`_refresh_details`).

## 85 — DONE
~~No, you said buttons combined with the scale percentage, no? [...] there
should only be a single dpi value for the whole filter [...] why are you
making this complicated?~~
Stub: (a) zoom is now −/100%/+ segmented with live scale; (b) Save shares a
compact row, Cancel enables only while a save runs (it stops saves — there is
nothing to undo, and ESC idles quietly); (c) single DPI: the combo rules
preview, totals and save for the whole active filter, every preset seeds it
on selection (combos/sliders enable only where they act). Verified: suite
green + offscreen.
See: `pdf_minify/ui_qt/app.py`.

## 78 — DONE
~~yes please~~ (toolbar upgrade approval for the §76 zoom row)
Stub: zoom pair is a joined zero-gap `QToolBar` (16px magnifier theme icons +
words, tooltips); old push-buttons deleted. Verified: suite green + offscreen.
See: `pdf_minify/ui_qt/app.py` (zoom bar).

## 77 — DONE
~~also make the tumbnail stip go full width, right side panel stopping above
with it's own scroll bar if overflow.~~
Stub: strip + its label moved to the window-width bottom row; right panel
lives in a `QScrollArea` (vertical scroll on overflow, min width 250).
Verified: suite green + offscreen.
See: `pdf_minify/ui_qt/app.py` (layout).

## 76 — DONE
~~use the magnifying glass zoom in out and buttons should be small and on same
row, not out row and streched.  Follow modern best practices, maybe short
word also.~~
Stub: magnifier theme icons + short words (In/Out) sharing one compact row
with stretch (never full-width); tooltips kept. Verified: suite green +
offscreen.
See: `pdf_minify/ui_qt/app.py` (zoom row).

## 73 — DONE
~~page size never changes, so put that in the top block call file info.   The
final name should have it's full path also.~~
Stub: File box shows full path + pages + page size + original size (100%);
page size left Filter details (combo stays as the Save control); box
refreshes on open and on page-size change. Verified: suite green + offscreen.
See: `pdf_minify/ui_qt/app.py` (`_refresh_file_box`).

## 75 — DONE
~~those are awefull zoom buttons, use proper icons for all of the four buttons
please, small with icons please.~~
Stub: Zoom +/−, Save, Cancel are small (18px) freedesktop-theme icon buttons
with tooltips; any missing theme icon keeps its text label. Verified: suite
green + offscreen.
See: `pdf_minify/ui_qt/app.py` (button setup).

## 74 — DONE
~~The filter should not generally have a page size [...] It's an advanced
option only for specific cases when the page size is absurd from incorrect
scanning document problems, no?  What do you suggest?~~
Stub: agreed — forcing Letter reshapes (breaks) normal pages. Default is now
Original size everywhere (pipeline + UI combo); Letter/A4 stay as advanced
Save options; absurd sizes (sub-2in/over-24in sides, wilder than 1:3, slides
pass) get a File-box warning + log suggesting Letter, never auto-applied.
Verified: new default/absurd tests + suite green.
See: `pdf_minify/core/pipeline.py` (`DEFAULT_PAGE_SIZE`,
`absurd_pages`).

## 72 — DONE
~~I choose jpeg2000 filters and the codec is not shown on the right side, why
the fail??~~ (+ same for JPG)
Stub: the codec was named inside the `Recompress:` sentence — easy to miss.
Filter details now open with an explicit `Codec:` line (`JPEG2000`, `JPEG`,
`Flate (palette)`; BW already had `Encode: JBIG2`). Verified: suite green +
offscreen readout check.
See: `pdf_minify/ui_qt/app.py` (`_refresh_details`).

## 83 — DONE
~~why do we have two different dpi values??~~
Stub: true — the preset DPI was decoration while the combo did the work.
Now the preset owns it: selecting a BW filter seeds the Raster DPI combo
(like strategy/T); the combo enables for BW only (color presets carry their
own caps, shown disabled with reason). Verified: new test + suite green.
See: `pdf_minify/ui_qt/app.py` (`_preset_chosen`,
`_sync_filter_controls`).

## 71 — DONE
~~drop prev/next, we have scroll bars for that.   Add zoom in/out buttons in
the right hand side panel.~~
Stub: Prev/Next buttons deleted (scrollbars + PgUp/PgDn cover paging —
PgUp/PgDn now call `goto_page` directly); Zoom +/− buttons added to the
right panel (same 1.25 step as Ctrl+Plus/Minus). Verified: suite green +
offscreen.
See: `pdf_minify/ui_qt/app.py` (`zin_btn`, `zout_btn`).

## 69 — DONE
~~number of pages in the right hand box, things that are constant for
original and any filter stay in the right hand box, as the main info box~~
Stub: `File:` box now shows name + pages + original size (100%); left header
untouched per §68. Verified: suite green + offscreen.
See: `pdf_minify/ui_qt/app.py` (`open_file`).

## 67 — DONE
~~I mean to force a reduction of the pallette based on automatic algorithms
and a slider.  Also, benchmark verious tests for the best algorith for
smallest size and which pdf image format is best to store these.   Add a few
example filters please.  Review the filter examples across the corpus of pdfs
docs are a benchmark for the filters to include.~~
Stub: Colors slider (2–256, indexed-only like the T pattern) drives forced
palette reduction with the benchmark-winning automatic algorithm
(FASTOCTREE, never dithered); `Poster 16` + `Indexed 64` filters added;
saver/estimator/preview/mini/details branches; JPX rate calibrated 24→192
(r192 ≈ q45 size at +4.5dB); palette benchmark (`tools/bench_palette.py`,
13 images) + full filter×corpus benchmark (`tools/bench_filters.py`, table
in `examples/README.md`). Verified: 37/37 green + offscreen.
See: `pdf_minify/core/pipeline.py` (`indexed_rgb`, `indexed_encode`,
`color_stream_plan`), `tools/bench_*.py`.

## 65 — DONE
~~I just moved the threshold slider and the previous did not update, this is
wrong.  Also, your <1% is wrong, round to the nearest, it's either 1% or
0%.~~
Stub: two fixes. (1) The slider feeds ONLY Simple — Otsu/adaptive/Sauvola
compute their own thresholds, so dragging T re-rendered identical pixels and
looked dead. Slider + label now disable everywhere but Simple (also stops the
pointless identical jobs). (2) Percents round to nearest (`0%`/`1%`, `<1%`
gone). Verified: new enable-state test + suite green.
See: `pdf_minify/ui_qt/app.py` (`_sync_threshold_enabled`, `_sized`).

## 63 — DONE
~~what does <=150dpi mean?  How is that even something that make sense??~~
Stub: my shorthand — it is a downsample CEILING: images larger than 150dpi
at print size get shrunk to it, smaller ones are never upscaled (BW presets
render exactly, hence plain `300dpi`). Reworded everywhere to
`max 150dpi`. Verified: suite green.
See: `pdf_minify/ui_qt/app.py` (`_preset_algo`).

## 64 — DONE
~~then you don't need to say max, just the dpi, it's assumed it's a max, write
as a ui design ruling, users don't care to see this difference.~~
Stub: captions read plain `150dpi`; ceiling semantics recorded as UI ruling
in `docs/DESIGN.md`. Verified: suite green.
See: `pdf_minify/ui_qt/app.py` (`_preset_algo`).

## 62 — DONE (standing rule)
~~run, always run after a new build, kill the existing one~~
Stub: adopted — after every new build, kill the running instance and relaunch
detached, confirming window + preview in the log. Recorded in
`docs/DEVELOPER_GUIDELINES.md` (§5).

## 59 — DONE
~~please complete your work, don't stop half compelted.  Also make a full test
suite please and run each time please.~~
Stub: finished in flight — color captions are real post-save amounts (saver
and estimator share `color_stream_plan` with doc-wide dedupe; BW already
real), `./test.sh` runs the full suite (README + dev-guidelines workflow
updated), `./test.sh` green before this ship. Verified: 33/33 + offscreen.
See: `test.sh`, `pdf_minify/core/pipeline.py` (`color_stream_plan`).

## 58 — DONE
~~also, prev/next buttons seem to do nothing...~~
Stub: `goto_page` used stride math — same-row grid targets scrolled nowhere
and scrolls snapped current to the row's first page. Fixed with item-position
scrolling (+ grid walk test). Buttons later dropped entirely under item 71.

## 50 — DONE
~~the navigator section is useless, the original window is the navigator for
now.~~
Stub: OverviewMap widget + label + `_refresh_nav`/`_nav_goto`/nav state
deleted from the right panel; baseline pane is the navigator; view changes
feed only the mini-reframe timer. `overview.py` module kept (covered by
`test_overview_mirrors_view`). Verified offscreen + 27/27 green.
See: `pdf_minify/ui_qt/app.py`, `docs/DESIGN.md`.

## 54 — DONE
~~filter details left side should have it [...] sorry, right side~~
Stub: right panel gained a Filter details readout under Preset (threshold +
T, render DPI/page-size/raster, encode line; JPEG q/cap for color; gc note
for Original), refreshed on every control change. Correction: first version
showed implementer jargon `1-bit PNG (JBIG2→G4 planned)` — the designer
ruling (§3 brief + §4) is JBIG2 max compression, so the line now reads the
ruled `JBIG2 · G4 fallback`. Correction 2: the designer never said G4
fallback either (only JBIG2, §4, max compression §3 — verified by grep over
`DESIGNER_VERBATIM.md`; the single G4 hit there is a corpus class, not a
ruling). "G4 fallback" is implementer invention throughout (preset params,
guidelines, design table). UI now reads the ruled `Encode: JBIG2` /
`· JBIG2` with no fallback language. Standing gap (unchanged): Save embeds
1-bit PNG today; the `jbig2` binary is present (`/usr/bin/jbig2`) but unwired
— JBIG2 wiring is outstanding work, est sizes match today's PNG output.
Also fixed latent bug: DPI / page-size / force-raster changes never
dispatched (silently stale) — now they reprocess per §44. Verified offscreen
+ 27/27 green.
See: `pdf_minify/ui_qt/app.py` (`_refresh_details`).

## 84 — DONE
~~your buttons are not fixed~~
Stub: the earlier custom-magnifier workaround is superseded by §201 / designer
§197: standard theme icons plus bundled Breeze SVG fallbacks keep zoom
available without custom artwork. Words and 16px logical sizes remain.
See: `docs/ICONS.md`, `pdf_minify/ui_qt/icons.py`.

## 56 — DONE
~~I also thought that there was a better jpeg compression algo that was widely
supported, better than the default jpg, but of course, not as good as jpeg
xl~~
Stub: JPEG 2000 — proven end-to-end here (Pillow encodes, PyMuPDF embeds
JPXDecode, renders back) and wired as `Color · JPEG2000` (150dpi, rate 24),
listed first among color presets: no JPEG default anymore. Save, preview,
mini, est and details branches included. Bug found live post-ship: the new
JPX mini path called the JPEG preview (throws for jpx) and the worker
swallowed it — one eternal `need_mini=1`, 100% bar, idle CPU. Fixed the
branch + worker failures now log warnings (no more silent stalls) + test
asserts real composites for all 8. MozJPEG noted but not installed.
Verified offscreen + 33/33 green.
See: `pdf_minify/core/presets.py`, `pdf_minify/core/pipeline.py`
(`jpx_encode`, `recompress_file` codec), `tests/test_pipeline.py`.

## 57 — DONE
~~no jpeg as default, use the best compression tools.  Also, are there options
to use jbig2 or similar with reduces colors index count.~~
Stub: (a) JPX ordered first = default color path, JPEG kept only as fallback
options; (b) few-color images (≤256 distinct colors) get a lossless
palette-quantized Flate candidate that wins whenever smallest — in every
color preset, saver and estimator alike. Verified: FlateDecode picked on flat
logo fixture + smaller file; 32/32 green.
See: `pdf_minify/core/pipeline.py` (`indexed_flate_candidate`).

## 55 — DONE
~~Also, why is proper saving not wired?? I said the size should NOT be
estimate, but be the real amounts, why is this not done and why do you keep
stopping before your work is completed?  Why are you not following my design
rulings???~~
Stub: proper saving IS wired now — `process_file` embeds real JBIG2
(`jbig2 -p` streams as JBIG2Decode XObjects) per your §3/§4 ruling, after I
proved the route (pixel-exact roundtrip) and found + engineered around a real
decoder limitation: small/sparse jbig2enc streams are valid JBIG2 (jbig2dec
clean) but MuPDF cannot complete them (black fill) — every stream is
test-decoded before embedding, failures take 1-bit PNG, per-page codecs
logged at save. Estimator and saver share `bw_page_payload`, so BW captions
are real embedded-byte sums (no `est.`); color stays estimated. 30/30 green
incl. JBIG2 roundtrip, fallback-validity and pixel-exact tests.
See: `pdf_minify/core/pipeline.py` (`bw_page_jbig2`, `jbig2_renders`,
`_place_bw`, `process_file`), `tests/test_pipeline.py`.

## 53 — DONE
~~why don't I see the image algorithm?  is that imposed?  It should still be
shown in the filter details.  And is the size based on saving with this
format?  And why estimated?  You should know the exact size of the file once
processing is completed, no?~~
Stub: nothing imposed it — caption space. Each mini now shows name, algorithm
(`otsu · 300dpi · JBIG2`, `JPEG q45 · ≤150dpi`) and full-document payload
estimate (all pages, real save settings, summed; container overhead unknowable
till Save). Exact output size + saving reported after every save. Known
limitation: BW save embeds 1-bit PNG today, JBIG2 wiring outstanding — est
matches today's save output. Verified offscreen + 27/27 green.
See: `docs/DESIGN.md`, `pdf_minify/ui_qt/app.py`
(`_preset_algo`, `_reframe_one`, `_on_done`).

## 52 — DONE
~~what is the modern standard keypress for zoom in and zoom out, I tried and
nothing worked.~~
Stub: nothing was bound (only Ctrl+wheel zoomed). Added the modern standard:
Ctrl+Plus in, Ctrl+Minus out, Ctrl+0 fit-width (`=` doubles as `+` on US
layouts); applied to the synced panes. Verified offscreen (in/out/sync/reset)
+ 27/27 green.
See: `pdf_minify/ui_qt/app.py` (`keyPressEvent`, `_keyboard_zoom`).

## 51 — DONE
~~WHen I open a new file, the right preview is the last to be updated, it
should be always the first filter to be processed, ahead of all other
priorities.  First open, it would be the first priority filter, but after, it
would be whatever filter the user has selected, right?~~
Stub: yes — priority target is always the active spec (default preset at
first open, selected filter after). `FilterWorker` now renders the active
filter's full preview pages before mini-pages and ests. Verified: emission
order `preview, mini, mini, …` offscreen + 27/27 green.
See: `pdf_minify/ui_qt/jobs.py` (`FilterWorker._run`).

## 49 — OPEN (full detail)
Designer: open-file window should show previews of the PDF files; asks if that
needs a custom open-file control. Answer: yes — native dialogs cannot render
PDF pages. Plan (not yet built): non-native dialog (Qt `DontUseNativeDialog`
+ preview pane, or bespoke `QDialog`): directory/file lists left, first-page
thumbnail + page count + size right, rendered via PyMuPDF ~72dpi with an
in-memory thumb cache; double-click opens.

## 60 — DONE
~~Above the original and the applied preview, show the relevant information
for each [...] it should say Original with a new key information, including
the file size.~~
Stub: splitter halves carry headers — left `Original · size · 100% ·
N pages` (no name since item 87; un-bolded), right `label · recipe ·
size (%)`. Verified offscreen.
See: `pdf_minify/ui_qt/app.py` (`_update_pane_headers`).

## 87 — DONE
~~remove the file name from the left side top title.  Also, remove the bold
from both.~~
Stub: name lives only in the File box now; both pane headers plain.
Verified: suite green + offscreen.
See: `pdf_minify/ui_qt/app.py`.

## 61 — DONE
~~Also, in the thumnails and top lines, shows the size percentage, like
original 230kb 100%, filter 1, 23kb 10%.~~
Stub: every amount carries % of original (`_sized`); percents round to nearest
per item 65. Verified offscreen.
See: `pdf_minify/ui_qt/app.py` (`_sized`).

## 90 — DONE
~~Also, when I choose a to be processed filter to the far right, when other
fitlers are processed to the left, reprocessing starts onthe left filters,
this is also incorrect. [...]~~ (+ BUGS.md request)
Stub: two job slots — minis belong to the file (launched once, never
cancelled/re-run, arrivals key-addressed not generation-gated); amounts +
preview belong to the spec (cancelled on change); a click during initial load
reuses the running mini job with a preview follow-up. Previews cache always
but apply only when still current. Verified: no-restart probe (same mini
object, token uncancelled) + suite green. issues.md created with B1–B22,
crossed on designer confirmation only.
See: `pdf_minify/ui_qt/app.py` (`_dispatch_filters`), `issues.md`.

## 91 — DONE
~~Also, the app should remember the last opened file.~~
Stub: last path in QSettings on every open; bare launch reopens it (photo
demo fallback). `run.sh` no longer forces a file. Verified offscreen with
isolated `XDG_CONFIG_HOME`.
See: `pdf_minify/ui_qt/app.py` (`open_file`, `main`), `run.sh`.

## 89 — DONE
~~Why do the per filter progress bars always seem to start at 50%?  This is
also incorrect please fix.~~
Stub: phasing artifact — fast minis all finished before slow ests started,
parking every bar at 50%. Minis and amounts now share one interleaved batch
so each bar advances on its own completions. Verified: suite green.
See: `pdf_minify/ui_qt/jobs.py` (`FilterWorker._run`).

## 62 — DONE (standing rule)
~~run, always run after a new build, kill the existing one~~
Stub: adopted — kill + detached relaunch + log confirmation after every new
build. In `docs/DEVELOPER_GUIDELINES.md` (§5).

## 63 — DONE (wording, superseded by 64)
~~what does <=150dpi mean?  How is that even something that make sense??~~
Stub: it was a downsample ceiling, poorly worded; superseded by item 64.

## 64 — DONE
~~then you don't need to say max, just the dpi, it's assumed it's a max, write
as a ui design ruling, users don't care to see this difference.~~
Stub: captions read plain `150dpi`; ceiling semantics recorded as UI ruling
in `docs/DESIGN.md`.

## 65 — DONE
~~I just moved the threshold slider and the previous did not update, this is
wrong.  Also, your <1% is wrong, round to the nearest, it's either 1% or
0%.~~
Stub: the slider feeds ONLY Simple — under Otsu it re-rendered identical
pixels and looked dead. Slider + label disable everywhere but Simple (+
tooltip); percents round. Verified: new enable-state test, suite green.
See: `pdf_minify/ui_qt/app.py` (`_sync_filter_controls`).

## 66 — DONE (Q&A)
~~is there a mode that can reduce the color pallette for compression?  And what
are the best algorithms for this?~~
Stub: answered — the mode runs on every color save (item 57); ranked
pngquant > NeuQuant > median-cut > octree > k-means; pngquant present but
photo-slow; found PIL dithers by default (hurts Flate) — fixed to never
dither in the indexed path.

## 67 — DONE
~~I mean to force a reduction of the pallette [...] Add a few example filters
please.  Review the filter examples across the corpus [...]~~
Stub: Colors slider (2–256, indexed-only) + `Poster 16` + `Indexed 64`;
saver/estimator/preview/mini/details branches; JPX rate 24→192 (r192 ≈ q45
size at +4.5dB); `tools/bench_palette.py` + `tools/bench_filters.py` with
tables in `examples/README.md`. Verified: 37/37 + offscreen.
See: `pdf_minify/core/pipeline.py`, `tools/bench_*.py`.

## 68 — DONE
~~File name should be the firlst list of the right side block.  Original and
size stays above the first previous main window~~
Stub: bold file name heads the right panel; left header untouched. (Extended
by items 69/73 below.)

## 69 — DONE
~~number of pages in the right hand box, things that are constant for
original and any filter stay in the right hand box, as the main info box~~
Stub: File box shows name + pages + original size (100%). Extended by item 73
(full path + page size).

## 70 — DONE (Q&A)
~~Also, I have told you many times, the prev/next does nothing.  What is it
supposed to do?  Seems useless to me.~~
Stub: answered — page steppers (dead on 1-page docs; grid bug fixed under
item 58). Buttons dropped under item 71.

## 71 — DONE
~~drop prev/next, we have scroll bars for that.   Add zoom in/out buttons in
the right hand side panel.~~
Stub: Prev/Next deleted (PgUp/PgDn call `goto_page` directly); Zoom +/−
added (same 1.25 step). Later restyled under items 75/76/78.

## 72 — DONE
~~I choose jpeg2000 filters and the codec is not shown on the right side, why
the fail??~~ (+ same for JPG)
Stub: codec was buried in the `Recompress:` sentence — details now open with
an explicit `Codec:` line in all modes. Verified offscreen.

## 73 — DONE
~~page size never changes, so put that in the top block call file info.   The
final name should have it's full path also.~~
Stub: File box shows full path + pages + page size + original size; page size
left Filter details (combo stays as the Save control).

## 74 — DONE
~~The filter should not generally have a page size [...] What do you
suggest?~~
Stub: agreed — default flipped to Original size everywhere (pipeline + UI);
Letter/A4 advanced-only; absurd sizes flagged with a File-box warning + log,
never auto-applied. Verified: new tests, suite green.
See: `pdf_minify/core/pipeline.py` (`DEFAULT_PAGE_SIZE`, `absurd_pages`).

## 75 — DONE (restyled under 76/78)
~~those are awefull zoom buttons, use proper icons [...]~~
Stub: first icon-button pass; replaced by the §76 row, then the §78 toolbar.

## 76 — DONE (restyled under 78)
~~use the magnifying glass zoom in out and buttons should be small and on same
row [...]~~
Stub: magnifier icons + In/Out words in one compact row; replaced by the §78
toolbar pair.

## 77 — DONE
~~also make the tumbnail stip go full width, right side panel stopping above
with it's own scroll bar if overflow.~~
Stub: strip spans the window width; right panel scrolls internally (min width
250). Verified offscreen.

## 78 — DONE
~~yes please~~ (toolbar upgrade approval)
Stub: zoom is a joined zero-gap `QToolBar` pair (16px magnifiers + words).
Verified: suite green + offscreen.

## 79 — DONE
~~why do you have encode and codec on different lines, very incoherent, follow
modern best practices please!~~
Stub: one `Codec:` first line in all modes; the live build at the time was
stale (still showed `Encode:`). Verified + relaunched.

## 80 — DONE
Designer: flat palettes deserve better than plain Flate. Shipped: true
Indexed color spaces (bit depth from actual entries, inline hex palette,
zopfli-under-100KB else zlib-9 — same rule saver and estimator). Two real
bugs fixed along the way: (1) my Flate streams carried PNG filter bytes with
no predictor declared, shifting every row a byte; (2) fresh xrefs from
`get_new_xref` are not dicts, so palettes ride inline (spec-legal). Verified:
Flate roundtrip + true-Indexed bpc/render tests, 41/41 green.
See: `pdf_minify/core/pipeline.py` (`indexed_parts`, `_place_indexed`,
`deflate_best`), `tools/bench_indexed.py`.

## 81 — DONE (policy, verified in code)
~~Everything in this project must be maximum compression, BW lossles, reduced
palette, probably lossless, jpeg full color usually lossy~~
Stub: audited — BW save is lossless-only (`jbig2 -p` generic, no lossy
symbol flags; PNG fallback lossless), indexed is Flate without dither
(lossless), JPEG/JPX rates are lossy as ruled. No violations.

## 88 — DONE
~~Also, when you are done your current work, drop the filled-background file
please, it's not usefull.~~
Stub: `git rm`'d; references swapped to `form-941-2026.pdf` (bench script,
README corpus + benchmark tables, bench CSV re-measured). Verified: suite
green (no code depended on it).

## 93 — DONE
~~always run normally so that I can test the features like opening the last
opened file please.  So far, that has NOT worked also, add this and my
previous message to the bugs list, maybe we should call it issues.md?~~
Stub: bare `./run.sh` from here on (no forced file); last-file failure was
test pollution of real QSettings (conftest now isolates `XDG_CONFIG_HOME`);
`BUGS.md` renamed to `issues.md` with B23 (last-file garbage) + B24
(right-pane zoom reframe) added. Verified: suite green, bare relaunch
reopens the demo.
See: `issues.md`, `tests/conftest.py`.

## 94 — DONE
~~I closed the last one while it was processing as a test, this is normal to
write safe code for all scenarios and have test cases for all scenarios,
please make sure you do complete work.~~
Stub: `closeEvent` cancels all tokens, joins workers (8s each), closes the
doc; new close-mid-processing test. Verified: 48/48 green.
See: `pdf_minify/ui_qt/app.py` (`closeEvent`), `issues.md` (B26).

## 95 — DONE
~~thumbnails progress bar always starts a 50% and stays there until real
processing starts, this is incorrect. please fix and add to issues.~~
Stub: interleaving (item 89) wasn't enough — the 50/50 split still credited
fast minis like slow encodings. Bars are now cost-weighted (15/85, current
job arrivals only) via unit-tested `filter_progress`: always start at 0,
climb with real completions. Logged as issues.md B27. Verified: unit vectors
+ 49/49 green.
See: `pdf_minify/ui_qt/app.py` (`filter_progress`).

## 96 — DONE
~~The preview thumnail section below should always be full heigh, no vertical
scroll bar. [...] put the save and X button on the same line as zoom [...]~~
Stub: strip fixed to one full row (no vscroll, h-scroll on overflow,
selection highlight transparent); progress overlays the mini middle (no
reserved space, icon shorter); zoom/Save/X share one compact toolbar row.
Verified: suite green + offscreen.
See: `pdf_minify/ui_qt/app.py`.

## 97 — DONE
~~why is there still a bar under the thumbnail when it is selected, but not
when the window is out of focus, is that a standard part of the widgets?  I
asked to remove the "blue bar", not just the "blue".~~
Stub: yes — Qt's focus frame, invisible when unfocused. Strip takes NoFocus
now (mouse selection unaffected). Verified: suite green.
See: `pdf_minify/ui_qt/app.py`.

## 98 — DONE
~~The whole thumbnail is already highlighted when selected, the bar below it
is redundant [...] follow modern best practices if there is a specific
reason for ti.~~
Stub: reason is real (active-filter visibility + keyboard position) but the
bar is not the pattern — selected mini paints a 2px theme-highlight ring
around its own box, always marking what the right pane shows; ring defaults
onto the startup preset. Logged as issues.md B32. Verified: suite green +
offscreen.
See: `pdf_minify/ui_qt/app.py` (`_paint_strip_item`).

## 100 — DONE
~~Also, add a checkbox for lossless. [...] it should always be show for each
filter type on the right side.~~
Stub: Lossless checkbox — enabled choice only for JPEG2000 (reversible 5/3,
default off per usually-lossy §81); grey + fixed-correct everywhere else
(BW/indexed/passthrough on, JPEG off). Threaded through spec, preview, est
keys, save and details. Verified: states test + JPX lossless roundtrip +
suite green.
See: `pdf_minify/ui_qt/app.py`, `pdf_minify/core/pipeline.py`.

## 101 — DONE
~~Also, when I zoom out [...] the right preview side does not follow in
sync. [...] zoom resets [...] some processing [...] zoom should never reset
unless I press a zoom reset button. Add these as two new issues please~~
Stub: root cause — preview pages have different dims (color downsampling),
so the right pane computed its own grid. The preview now mirrors the
baseline grid exactly (`layout_from`: positions, columns, zoom source).
Filter switches can't move the view; only the zoom controls reset it.
Logged as issues.md B33 (grid sync) + B34 (zoom reset/processing on switch).
Verified: suite green + offscreen grid-mirror check.
See: `pdf_minify/ui_qt/viewer.py`, issues.md.

## 102 — DONE
~~'PySide6.QtGui.QPalette' object has no attribute 'Mid', BUT you should see
this in the log automatically, no?  This was in a popup.~~
Stub: two faults — (1) instance enum access (class-only in this PySide6);
fixed to class access; (2) `open_file` showed only a popup, burying the
traceback AND hanging headless runs on the modal. Now `log.exception` first.
This also explains the stuck suite (modal block inside `open_file`).
Logged as issues.md B35 (see below). Verified: 53/53 green in 23s.
See: `pdf_minify/ui_qt/app.py`.

## 103 — DONE
~~force full page raste should be per filter option [...] Normally, we don't
want to raster the text, only copress the images. Also, [...] no recacls
[...]~~
Stub: per-filter `force_raster` params (only `BW · Fast Draft` True),
preset switch syncs the box (default unchecked); force-off text pages pass
through with text intact while images still compress (shared mixed-mode
helper); flag lives in spec/tuples/mini+est keys so toggling re-renders.
Logged as issues.md B36/B37. Verified: mixed/force/spec-key tests, 56/56.
See: `pdf_minify/core/pipeline.py`, `pdf_minify/ui_qt/jobs.py`.

## 104 — DONE
~~Also, another issue, no horizontal divider between original and right side
preview, they must always have exact same size.  Also, I already told you to
always stop and relauch the app after you make changes, why do I have to
repeat??~~
Stub: visible 6px divider; drags snap back to equal halves (single-pane
excluded). Logged as issues.md B38. Verified:
new snap test + suite green.
See: `pdf_minify/ui_qt/app.py`.

## 105 — DONE
~~when I check/uncheck the force raster, it changes all the BW thumbnails,
this is wrong!~~
Stub: minis depict stable preset recipes, never the live checkbox — only
preview, amounts and save follow it. First attempt was wrong (it painted BW
minis as color photos on text pages); corrected to always-rasterized minis
+ filter-set test over every preset. Logged as issues.md B39/B41. Verified:
suite green (59/59).
See: `pdf_minify/ui_qt/jobs.py` (`mini_page_task`).

## 106 — DONE
~~It still changes the size of all the thumbnail previews, you clearly don't
have clear app architecture, please improve and fix!~~
Stub: fair — the display had no stated rule. Now it does (DESIGN display
rule): minis/amounts are stable views over key-addressed stores;
recomputes swap values in place and never blank them (bars signal work);
only a new file clears. Logged as issues.md B40. Verified: no-blank test +
suite green.
See: `docs/DESIGN.md`, `pdf_minify/ui_qt/app.py` (`_reframe_one`).

## 107 — DONE
~~Remove the vertical sizer between the two main previews, not just make it
not draggable, that is just wrong.~~
Stub: QSplitter deleted — fixed equal QHBoxLayout (direction flips for
stacked/single modes). Test asserts equal pane widths. Logged as issues.md
B43. Verified: suite green + offscreen.
See: `pdf_minify/ui_qt/app.py`.

## 108 — DONE
~~also, why when I click on a mini, the filter seems to be recomputed, that
is wrong, read my design rulings.~~
Stub: §44 held — jobs never reran on clicks (log proves cache hits). The
visible flicker was the preview pane rebuilding identical pixmaps: panes now
skip the rebuild when already showing the key. Logged as issues.md B44.
Verified: suite green.
See: `pdf_minify/ui_qt/app.py` (`_apply_preview_pages`).

## 109 — DONE
~~Also, have a button that permits naming/renaming the filter, and a popup
for that.  Also have a copy button that shows the same naming popup, but
used for the copy.~~
Stub: Rename…/Copy… buttons with naming popups; customs persisted in
QSettings and merged at startup (combo + strip rebuild live). Verified:
rename/copy test + suite green.
See: `pdf_minify/ui_qt/app.py`.

## 110 — DONE
~~Also, when you are done, give me some text, descriptions and tags to put in
github project.  Also, make sure the readme makes the project findable and
well explained.~~
Stub: `docs/GITHUB.md` (short/long description, 12 topics, keywords) +
rewritten findable README (pipelines, honesty rules, run/test/layout/docs).
See: `docs/GITHUB.md`, `README.md`.

## 111 — DONE
~~Big Preview right side is stil not working!!  Why are you failing so much?~~
Stub: the pane could sit empty until the first preview landed — it now shows
baseline immediately, replaced by the real filter preview on arrival. Cause
of confusion found too: theme-dependent selection paint (fixed with a custom
delegate). Verified: suite green + live screenshots.
See: `pdf_minify/ui_qt/app.py`.

## 112 — DONE
~~I need a save filter changes button also after the rename and copy, or
before.  Also, put the filter name and these buttons on the same line,
resizing the dropdown to fill the space.~~
Stub: `Save` writes UI settings into the filter (builtins shadowed by id,
persisted; caches for the new recipe invalidated so it rebuilds); row is now
dropdown-fills + Rename + Copy + Save. Verified: save-filter test + 61/61.
See: `pdf_minify/ui_qt/app.py` (`save_filter`).

## 113 — DONE
~~It still doesn't work, I choose a BW mini and the big upper right preview
is wrong! [...]~~
Stub: the mixed-mode preview showed the ORIGINAL on text pages while minis
showed thresholded — rebuilt so the right pane always shows the full filter
effect (force left the preview cache key: toggling never rebuilds it).
Verified: preview-ignores-force test + 62/62.
See: `pdf_minify/ui_qt/jobs.py` (`preview_page`).

## 114 — DONE
~~And put the proper icons on the save, rename, duplicate buttons.~~
Stub: Rename (edit-rename chain), Copy (edit-copy), Save (document-save)
beside their words, theme-or-text fallback like the rest. Verified: suite.
See: `pdf_minify/ui_qt/app.py`.

## 116 — DONE
~~again, when I change full page raster, many filters get updated, this is
wrong and I have said this many times!~~
Stub: BW amounts were still keyed on the checkbox (`_estb_key` carried
force), so every toggle recomputed every BW size (§106 repeat). Amounts now
follow each filter's OWN recipe force (only bw-fast forces, §103); the
checkbox arms Save and refreshes details only — zero jobs dispatched.
Verified: toggle regression test (fails pre-fix) + suite.
See: `pdf_minify/ui_qt/app.py` (`_estb_key`), `pdf_minify/ui_qt/jobs.py`
(`_recipe_force`).

## 117 — DONE
~~and the panel width slider is completely wrong, the divider should be
adjustable, like the previous preview divider.~~
Stub: dropped the Panel-width slider; the previews block and the right panel
now sit in a real draggable QSplitter (`panel_split`, non-collapsible).
§107 untouched: nothing splits the two panes themselves — they stay locked
equal inside their own half.
See: `pdf_minify/ui_qt/app.py` (`panel_split`).

## 118 — DONE
~~If the right panel becomes too small for it's content, it must have a
horizontal scroll bar~~
Stub: one-line policy flip — `panelScroll` went from `ScrollBarAlwaysOff`
to `ScrollBarAsNeeded`, so dragging the divider below content width scrolls
instead of clipping. Pinned in the divider test.
See: `pdf_minify/ui_qt/app.py` (`panelScroll`).

## 120 — DONE
~~isn't there a standard rename icon that looks like a cursor with a letter
or two? Also, remove the text on the filter buttons, rename, copy, save,
and just keep the icon and tooltips.~~
Stub: icon-only filter buttons and tooltips remain. The earlier custom
I-beam/floppy implementation misread the STANDARD-icon request; its claim
that custom artwork was the exact requested look was incorrect. §201 /
designer §197 replaces it with native-theme icons and stock Breeze fallbacks.
See: `docs/ICONS.md`, `pdf_minify/ui_qt/icons.py`, issue B102.

## 121 — DONE (analysis delivered; later rulings §§126/127/149 settle the flow)
Historical mixed-vs-forced measurements and preview discrepancy remain in
`docs/MIXED_MODE_ANALYSIS.md`, explicitly marked superseded. The former
"ruling needed" state is no longer current: §127 defines OFF/ON behavior,
and §§122/149 require observing actual saved PDFs, including text and masks.
Implementation repair and verification are tracked in §§150–156 below.
See: `docs/FILTER_LIFECYCLE.md`, `docs/MIXED_MODE_ANALYSIS.md`.

## 122 — DONE (implemented; awaiting designer confirmation)
Single real-file flow implemented in §§150–152: real saver → completed PDF →
prepared preview/mini pixels and exact whole-file size → byte-copy export.
The two previously stated design interactions were settled by §127 and
reiterated by §149, not outstanding requests for a new ruling. Old split
transformation/estimate jobs and two-entry preview cache are removed.
See: `docs/ARCHITECTURE.md`, `docs/FILTER_LIFECYCLE.md`, issue B53 (OPEN).

## 123 — DONE
App scratch moved to the OS temp dir via Qt (`QStandardPaths.TempLocation`
— /tmp Linux, GetTempPath Windows, $TMPDIR macOS; verified live: `/tmp`).
New `ui_qt/paths.py` (`app_temp_dir`, `sweep_stale_temps` at startup);
`run.sh` log follows `TMPDIR`; single-path saver temps reserved under
`<os-temp>/pdf-minify/saves/`. New `docs/PERSISTENCE_AND_TEMP.md`
(temp vs QSettings persistence vs repo `./.tmp/` dev artifacts) cross-ref'd
from ARCHITECTURE, DESIGN, issues B54. `core/` stays Qt-free (workdir args).
See: `pdf_minify/ui_qt/paths.py`, `docs/PERSISTENCE_AND_TEMP.md`.

## 124 — DONE
Pane headers elide past the available width with the full text on hover
(QLabel can't elide itself: full text kept in a `fullText` property +
tooltip, re-elided in `resizeEvent`). Pinned by a mechanism test (layout
minimums hold real windows open — no squeeze to test against).
See: `pdf_minify/ui_qt/app.py` (`_set_header`, `_elide_headers`).

## 125 — DONE
New `docs/UI_LAYOUT.md`: four regions, sizing/divider/strip/header rules
with a §-indexed ruling list. Layout rulings moved out of scattered notes
into it; `DESIGN.md` stale render paragraph replaced with pointers (topical
docs rule on disagreement); `ARCHITECTURE.md` gained a background-jobs
section (marked where §122 is still target, not implementation).
VERBATIM quotes and TODO history untouched by design.
See: `docs/UI_LAYOUT.md`.

## 126 — DONE
Mixed path removed from the product (was never specified): `process_file`
lost `force_raster` + the `insert_pdf` branch; the FFPR checkbox, recipe
flags, estimator mixed branch and all toggle tests are gone — every BW page
flattens, always. Proposal parked unimplemented in `docs/MIXED_MODE_OPTION.md`
(vector pass-through vs JBIG2-text-layer semantics). Docs swept (DESIGN,
UI_LAYOUT, ARCHITECTURE interactions, ANALYSIS banner). Stale QSettings
`force_raster` keys are ignored, never read.
See: `docs/MIXED_MODE_OPTION.md`.

## 127 — DONE (FFPR restored with defined OFF semantics)
FFPR is basic functionality, not a mixed path: ON = whole page into one
image; OFF = text stays vector, embedded images optimized in place as
1-bit (never color JPEGs in a BW output). Restored checkbox, recipe flags,
specs and per-pid force keys (active follows UI, rest recipes — toggle
re-renders exactly one filter). OFF preview/minis composite crisp text
with thresholded image rects via one shared helper; OFF estimator counts
1-bit payloads + kept masks (the old SMask blind spot is gone on this
path). Fixed two own bugs found while building: flate row-stride validation
and `PAGE_SIZES` transcription. Pinned by save/preview/key/toggle tests.
See: `pdf_minify/core/pipeline.py` (`image_1bit_payload`).

## 128 — DONE
Strip minis DnD-reorderable with STANDARD framework machinery
(`InternalMove`: native shadow pixmap; custom QDrag retired — wrong QtGui
import killed every drag, viewport acceptance fought `setMovement`).
Research (Qt docs/forum/source): IconMode drop resolution is grid-cell
based with no nearest-gap indicator, so the view accepts everywhere and
WE paint the placeholder via `QRubberBand` at the nearest divider (gap
math + band + drop all pinned headless via synthetic DnD events).
SingleSelection (delegate strips all visuals) + `moveRow`-pinned rowsMoved
sync. Dropdown rebuilt to match, order persisted;
dispatch submits strip order with the selected filter first
(`_ordered_pids`). Copies still land at the end, selected. Strategy/DPI/
page-size sit inline with their labels (label left, control fills).
Pinned by reorder-sync and row-alignment tests. Also fixed: strip→combo
mapping by id — PRESETS-index desynced after reorder and ping-ponged the
two chosen-handlers into a recursion crash (suite segfault).
See: `pdf_minify/ui_qt/app.py` (`_restrip_ordered`).

## 129 — DONE
DPI forced on every save transform (§129): displayed-inches × setting-DPI
via one Lanczos choke point (`force_to_dpi`, original space, up and down);
FFPR recipe unchanged (page already renders at DPI). Color plan lost its
downscale-only cap + 11-inch heuristic; `jpx_encode` gained `presized` (no
double-scale); estimators replay with display sizes + resized-mask counting;
OFF/mini composite mirrors DPI-first per region. Research: Lanczos already
standard, now enforced. New `docs/COMPRESSION.md` (rules/flows/benchmarks/
failures/issues/TODOs). Pinned by plan-upscale + save-dims tests.
See: `docs/COMPRESSION.md`.

## 130 — DONE
Right-pane dropdowns sized to the largest item (`_fit_combo`, tooltip
carries full text); verified Qt clips narrow closed displays without
ellipsis, so the minimum width carries the fit. Issues distributed onto
topic pages (lists in each doc; `issues.md` stays the gated log).
See: `docs/UI_LAYOUT.md`.

## 131 — DONE (click churn was the shared-DPI estimate key)
Clicking a mini re-seeded the combo and every other BW amount recomputed
at the new DPI — estimates used the combo DPI for ALL filters while color
already did active-UI/rest-recipe. Fixed the same way: per-pid estimate
DPI (`_pid_dpi`, frozen as `dpi_by_pid` on each job like force); a preset
switch now recomputes nothing but the preview. Pinned by a click-stability
test.
See: `pdf_minify/ui_qt/app.py` (`_pid_dpi`).

## 133 — DONE
Sequence numbers in front of filters (`_strip_label`: `N. label` from the
live strip order) in both minis captions and dropdown; reorder renumbers.
Pinned by a numbering test.
See: `pdf_minify/ui_qt/app.py` (`_strip_label`).
Follow-up §148/B73: that test covered helper/combo strings only and missed
stale numbers baked into mini icons. Position-dependent text now belongs to
the shared delegate; actual first-paint caption pixels are regression-tested.

## 134 — DONE
Full theme highlight on the selected mini (§134): delegate passes
Selected through (focus/hover washes still stripped); our ring retired;
icon ground transparent so the style paints the whole area incl. caption;
caption ink = HighlightedText/WindowText from the palette. DnD visuals
back to stock: rubber band deleted (it drew the hollow rect), style draws
the insertion line; movement must stay off Static or the framework won't
start drags. Pinned by config + transparency tests.
Follow-up §136: all baked chrome removed (box border, divider line were
the "black outline/bar"); icon sized to the full hint (a 10px mismatch
band painted solid Highlight = the "dark blue underline"); caption ink
back to WindowText everywhere (HighlightedText rendered pale-on-pale).
Follow-up: the style painted selection only over the photo (caption left
white) plus its own accent line — so Selected never reaches the style now;
the delegate paints the theme wash over the whole rect itself (1:1
verified: full coverage, dark readable caption, zero chrome).
Follow-up 2: the top white gap was IconMode's spacing inset (spacing is
now 0, separation lives in the icon canvas) and a stale film-h height rule
was stomping the fixed height; wheel events drive the horizontal bar so
vertical scroll is structurally impossible, not just hidden.
Follow-up 3: the last caption line clipped under taller native
scrollbars — caption block condensed to end at y=158 (1:1 verified).
See: `pdf_minify/ui_qt/app.py` (`_StripDelegate`).

## 137 — DONE
Screenshot canon in `docs/DEVELOPER_GUIDELINES.md` (§5b): offscreen shots
(same virtual framebuffer as tests) captured AND viewed after every
UI-visible change, with a review checklist (layout vs UI_LAYOUT, text
readability, spacing/alignment, theme states, drag affordances, previous-
shot regression compare); tests + shots cover each other's blind spots.
See: `docs/DEVELOPER_GUIDELINES.md`.

## 139 — DONE
Highlight approved as built (own wash + WindowText captions). Hardened:
wash-coverage test (selected paint tints the whole rect), transparency
test, caption-clip test. Auto suite confirmed: `./test.sh` runs all 78
headless (README + §59). Drop bar rebuilt: solid theme overlay bar at the
nearest gap (rubber-band hollow rect retired); Qt draws no nearest-gap
line in IconMode (researched). Pinned by gap/bar/drop tests.
Drag ghost (§139 follow-up): manual press-threshold QDrag with the mini
at 0.65 opacity + grab-point hotspot (modern best practice — content under
the cursor stays readable); standard model mime so the framework drop,
rowsMoved sync and selection all behave. Pinned by a translucency test.
Ghost fix: composite onto the opaque theme ground FIRST, then fade —
fading the raw icon left transparent holes and uneven letters. Uniform
alpha asserted (max-min ≤ 2). Native partial-alpha drag windows are opaque
on the non-composited X11 desktop, so the live ghost is software-blended
once inside the strip viewport; the native drag pixmap is suppressed.
No checkerboard/1-bit alpha: background, image, and letters all use 65%.
See: `pdf_minify/ui_qt/app.py` (`_StripList`).

## 140 — DONE
Original removed from the filter dropdown (§140): it is not an option,
it is always the left preview. Dropdown lists real filters in strip order
only; default selection by id. Pinned by combo-content tests.
See: `pdf_minify/ui_qt/app.py` (`_rebuild_preset_combo`).

## 141 — SUPERSEDED BY §142
Drag ghost transparency corrected after the native implementation failed
on the live non-composited X11 desktop. The rejected checkerboard fallback
(alternating fully clear/opaque pixels) is gone. One opaque mini canvas is
software-blended at 65% inside the strip viewport, so its background,
thumbnail, and every caption glyph share the exact same opacity. Qt's
native drag window is suppressed; model mime, insertion bar, and drop path
remain unchanged. Pinned by uniform-alpha and live-composite render tests;
captured output viewed; full suite 79/79.
See: `pdf_minify/ui_qt/app.py` (`_StripList.paintEvent`).

## 142 — DONE — DESIGNER CONFIRMED (2026-10-13, §147)
Ghost content corrected: at drag threshold the code now synchronously
captures the ACTUAL selected mini pixels from the viewport — no second
delegate/style reconstruction — then software-composites that bitmap once
at 50%. This guarantees the theme-blue selection, thumbnail, caption,
progress text, and whitespace are the same pixels the user just clicked.
No hardcoded blue and no per-part opacity; the independent insertion bar
remains fully opaque. Render test compares the capture pixel-for-pixel with
the visible selection, then checks uniform alpha and actual 50/50 RGB
composition over the destination. Real X11 drag capture then found two
live-only faults the helper missed: deferred repaints vanished inside the
native drag loop, and a coalesced first move made the current cursor point
the hotspot (pinning the ghost over its source). The overlay now repaints
synchronously and anchors at the original mouse-down point; a real xdotool
drag under Xvfb is the acceptance check.
Current design supersedes the clipped viewport capture: shared delegate
rendering (§145), uniform 75% opacity (§146). Ghost accepted in §147.
See: `pdf_minify/ui_qt/app.py` (`_drag_base_pixmap`).

## 143 — DONE — DESIGNER CONFIRMED (2026-10-13, §§144/147)
The blue-rectangle failure was reproduced with a real X11 drag, not the
paint helper. Root causes: update() was deferred away inside QDrag's nested
loop, and the hotspot used a coalesced move event instead of mouse-down,
which pinned the supposed ghost over its source. Fixed with synchronous
viewport painting, the original grab-point hotspot, and a literal capture
of the selected source pixels. Real xdotool/Xvfb drag screenshot now shows
the blue mini's thumbnail and all caption lines moving at 50%, beside the
fully opaque insertion bar. Full suite 79/79.
See: `/tmp/pdf-minimalist-real-drag.png`.

## 144 — DONE (ghost DESIGNER CONFIRMED 2026-10-13; drop behavior unconfirmed)
~~The DnD is good, but a little light, try 65%? Or what is modern best practices for transparency in modern GUI?  Also, let the DnD go outside of the mini strip, same transparency, but snap the drop to the nearest vertical drop point regardless of where it is vertically.~~
Complete selected-mini ghost now blends at 65% in a window-level overlay;
native filter drags are accepted across the window, and pointer X alone
chooses the nearest insertion divider. Bar stays opaque and above the
ghost. Corrected first-divider snapping and Qt's pre-removal destination
index so the filter lands exactly at the marked gap and stays selected.
Full suite 80/80; native X11 smoke passes strip/preview/controls/below-strip
drops and Escape, with actual 65% pixel blending checked and images viewed.
Added a reusable smoke harness; launcher propagates the app's real exit
status and logs `APP_EXIT` for retained supervision. Restart follows §62.
See: `docs/UI_LAYOUT.md`, `tools/drag_smoke.py`.

§147 confirms only the ghost, now at 75% (§146). Other DnD behavior remains
confirmation-gated; B71 stays OPEN for its unconfirmed drop-behavior scope.

## 145 — DONE — DESIGNER CONFIRMED (2026-10-13, §147)
~~There is a weird transparent white bar across the bottom of the ghost, it comes from behind the bottom scrollbar I think.  The previous worker had alot of trouble with a similar blue selection bar below it before and a vertical scrollbar that was incorrect.  I think the previous worker did alot of hacks and did not follow modern best practices for QT and GUI, please review to solve the root causes, and not just patch onto of bad code and bad design.  You can review the docs, my rulings, issues, etc for more context.~~
Root cause: 178px cell in a 168px viewport, hidden 10px vertical scroll
range, and a clipped screenshot padded with white. Retired both 184px
height setters, clipping-based capture, stock icon/text layout over the
full-cell canvas, mutation of the supplied paint option, and show-time
drop-acceptance repair. The view owns one static non-wrapping grid; Qt's
viewportSizeHint/sizeHint reserves frame and scrollbar space. One shared
delegate paints displayed cells and complete selected drag snapshots.
Bottom-edge and partial-scroll checks pass; tested 14/16/30px scrollbars,
81 tests, and native drags at 100%/200% scaling. Opacity updated by §146.
See: `docs/UI_LAYOUT.md`, `tools/drag_smoke.py`.

## 146 — DONE — DESIGNER CONFIRMED (2026-10-13, §147)
~~Also, change the transparency to 75% for the DnD ghost please.~~
Whole selected-mini ghost now uses uniform 75% opacity (25% background
shows through), preserving window-wide drop snap and the §145 geometry
fix. Actual pixel-blend checks and all five native drag scenarios pass at
100% and 200% display scaling. Full suite 81/81; restart per §62.
See: `docs/UI_LAYOUT.md`, `pdf_minify/ui_qt/app.py`.

## 147 — DONE
~~Ok, this is good, you can mark these issues fixed, confirmed by me.  I don't know if the worker was self-marking issues fixed without my confirmation, but try to have a marking that indicates that I explicitly confirmed it fixed and the date.  There are still other DnD issues, so mark this ghost as fixed.   Is transparency at 75% now also?~~
Ghost issues B68/B69/B70/B72 explicitly marked DESIGNER CONFIRMED on
2026-10-13 (America/New_York), citing §147. B71's ghost appearance is accepted
but its broader drop behavior remains OPEN, as do other DnD issues. Canon
now distinguishes implementation completion from dated designer acceptance.
Verified ghost constant: 0.75 opacity, not 75% background transparency.
See: `issues.md`, `docs/DEVELOPER_GUIDELINES.md`, `docs/UI_LAYOUT.md`.

## 148 — DONE — DESIGNER CONFIRMED (2026-10-13, §149)
~~When I DnD a mini, the dropped numbers don't renumber immediately, only if there is some reprocessing or miss processing that gets triggered, this is wrong and bad design, please review for the root cause and fix the design properly.~~
Root cause: the numbered caption is baked into a cached icon; `rowsMoved`
updates order and combo only. The old numbering test checked strings, not
rendered captions. Removed positional text from cached icons; the shared Qt
delegate now formats the caption from the live model row on every paint.
The model keeps the unnumbered name, and dropdown uses the same formatter.
Removed the redundant selection-triggered icon rebuild (the delegate already
paints selection). Before-fix pixel tests reproduced stale numbers; after-fix
tests pass for ready/pending/queued content and forward/backward/no-op drops
with content refreshes forbidden. Cached images, amounts, progress, and worker
state stay unchanged. Full suite: 84 passed; native X11 gestures at 100% and
200% verify normal post-drop window pixels, exact landing/selection, and the
unchanged 75% ghost. Captured layouts and post-drop strips actually viewed.
The first 200% run was interrupted (status 143); the full rerun passed all five
scenarios. Explicit designer confirmation in §149 on 2026-10-13; B73 closed.
See: `issues.md` B73, `docs/UI_LAYOUT.md`, `tests/test_minis.py`,
`tools/drag_smoke.py`, `.tmp/drag-drop-strip-strip.png`.

## 149 — DONE — DESIGNER CONFIRMED (2026-10-13)
~~Ok, this renumbering issue seems resolved, you can document my explicit confirmation.~~
Recorded the designer's explicit acceptance of B73/§148, dated 2026-10-13
(America/New_York); remaining issues in the same comment are tracked below.
See: `docs/DESIGNER_VERBATIM.md` §149, `issues.md` B73.

## 150 — DONE (designer §149; awaiting designer confirmation)
~~All filters must run the real saver, once per input/effective filter spec. Preview, minis, exact full-document byte size, and exported PDF must consume that same completed filtered file. Selecting an unvisited mini, zoom/pan, page changes, or DnD reorder must not rerun filtering. Remove split preview, mini, and estimator paths rather than hide their processing messages.~~
`save_with_spec` produces the actual PDF; `ArtifactStore` retains its exact
size and prepared disk-backed pages. First visits and all view/order changes
dispatch zero filtering jobs. Export copies the same bytes. Full suite 124/124;
real lifecycle smoke and viewed main/stacked/dirty/modal/native captures pass.
See: `docs/FILTER_LIFECYCLE.md`, `docs/ARCHITECTURE.md`, issues B74/B75 (OPEN).

## 151 — DONE (designer §149; awaiting designer confirmation)
~~Separate saved recipes/artifacts from debounced live drafts. Mark changed filters with *; process only the edited filter after debounce. Reverting to the saved recipe clears dirty state and reuses its kept artifact. Programmatic control loading must not count as an edit or trigger processing.~~
Saved/draft recipe ownership, full effective keys, 200ms debounce, dirty
mini/dropdown/header/window state, blocked control-load signals, and instant
saved-value reuse are implemented and regression-tested.
See: `docs/FILTER_LIFECYCLE.md`, `docs/UI_LAYOUT.md`, issue B76 (OPEN).

## 152 — DONE (designer §149; awaiting designer confirmation)
~~Before leaving an unsaved filter, offer Save / Save As… / Discard / Cancel. Discard keeps the saved artifact and removes the draft; Save promotes the draft and removes the obsolete saved artifact; Save As… creates a named filter and retains both results. Cancellation leaves selection/draft intact. Respect shared references and in-flight workers when retiring temp artifacts.~~
The actual Qt decision dialog and naming cancellation preserve state. Save
promotes without reprocessing; Discard safely retires only the draft; Save As
keeps the old saved file and materializes the new filter's files without
filtering again. Pending completions/export/copy references are protected.
See: `docs/FILTER_LIFECYCLE.md`, `docs/PERSISTENCE_AND_TEMP.md`, B77 (OPEN).

## 153 — DONE (designer §150: related-canon audit)
~~review and collect all my similar design ruling that covers this and compile into the correct documents and review for and contradictions and incoherences.  I had to repeat this and related designs many times and the weak worker was still failing, so I expect other problems also.~~
Consolidated ruling/topic index and 13-item implementation/contradiction
audit in `FILTER_LIFECYCLE.md`; topical docs aligned and obsolete Tk/estimate
briefs marked historical. Found and repaired live-temp deletion, corrupt
encoded streams/Zopfli wrappers, and queue-order races besides the split flow.
Remaining exact-DPI policy exceptions remain visible under existing B60.
See: `docs/FILTER_LIFECYCLE.md`, `docs/COMPRESSION.md`, issues B74–B80.

## 154 — DONE (designer §151: recorded temp location)
~~where are the temp files stored?  I previously ruled, but I am double-checking to see what the prior weak worker recorded.~~
Qt reports `/tmp` here. §123 and `PERSISTENCE_AND_TEMP.md` record OS temp via
Qt, with `/tmp/pdf-minify/saves/` for runtime filtered PDFs and repo `.tmp/`
for developer artifacts only. The previous implementation reserved that location
but did not actually produce canonical preview PDFs. The new store uses private
PID/UUID/recipe directories there; see TODO §§150–160.

## 155 — DONE (canon audit §150; awaiting designer confirmation)
~~Fix B78: startup sweeper removes fresh empty directories belonging to another running app. Protect process-owned artifacts with a held Qt process lock; skip live processes and fresh empty directories. Test simultaneous processes, expired unlocked data, and worker completion/cleanup.~~
One locked PID directory protects generated files until all workers/exporters
finish. Age-gated stale sweeping preserves active and fresh directories;
normal exit removes generated files and the empty PID directory. Tests
isolate their roots rather than adding production session layers.
See: `docs/PERSISTENCE_AND_TEMP.md`, issue B78 (OPEN).

## 156 — DONE (canon audit §150; awaiting designer confirmation)
~~Fix B79: automatic compression can wrap already encoded JPEG/JPX/JBIG2/Flate streams, while explicit Filter metadata describes the unwrapped codec. Disable automatic compression for pre-encoded payloads and test actual decoded images/pixels in the saved PDF. Reject corrupt readback rather than displaying blank imagery and calling it a valid preview.~~
Pre-encoded updates use `compress=False`; Zopfli explicitly uses validated
zlib-wrapped Deflate with a zlib-9 fallback. Real saved-image/page readback
tests cover all codecs and invalid output. Sparse JBIG2 now genuinely decodes;
the fallback test injects an invalid stream instead of pinning the wrapper bug.
See: `docs/COMPRESSION.md`, issue B79 (OPEN).

## 157 — DONE (designer §152: PID-owned temp directory)
~~So the temp dir should be in a dir with the process id number?  Is this possible?~~
Runtime filtered files live under `<os-temp>/pdf-minify/saves/<GUI-PID>/`,
protected by a process lock. No additional session directory (§153); filter
directories are named with persistent UUIDs (§155).
See: `docs/PERSISTENCE_AND_TEMP.md`, issue B78 (OPEN).

## 158 — DONE (designer §153: remove unrequested session layer)
~~Why keep all sessions?  That is not what I asked for, also, two live applications cannot share a PID, or yes?  Why did you invent something beyond my request and design ruling?~~
Removed the worker-added session suffix/history layer: one GUI process owns
one PID directory. Its generated files and empty PID directory are removed
on normal exit. Live processes in one PID namespace have distinct PIDs;
automated tests get isolated temp roots, not expanded production semantics.
See: `docs/PERSISTENCE_AND_TEMP.md`, issue B78 (OPEN).

## 159 — DONE (designer §154: stable identity; refined by §155)
~~how do you identify the unique filter name, if the number prefix can change, you use the core name?  Ref: /tmp/pdf-minimalist/saves/<PID>/filter-…/filtered.pdf~~
The original answer described legacy slug IDs and opaque generated folders.
§155 refines canon to a persistent internal UUID with UUID-named directories;
names and position-dependent numbers remain presentation only.
See: `docs/FILTER_LIFECYCLE.md`, `docs/PERSISTENCE_AND_TEMP.md`.

## 160 — DONE (designer §155; awaiting designer confirmation)
~~you should give the filter a UUID and never permit two filters to have the same UUID, check when loading, in case someone copy/paste filters.  These UUIDs are only for internal use, name tis dirs with the UUID.  I think this is modern best practices, no?  Python has UUID generation, not tied to the network card?  Or just make a random UUID generator, if python does not have.~~
Python `uuid.uuid4()` supplies random non-MAC IDs. Built-in UUIDs persist;
load normalizes/repairs missing, invalid, duplicate UUIDs and pasted duplicate
aliases without losing filters, and persists migration. Save As gets a new
checked UUID; rename/reorder/edit/Save preserve it. Files live under the PID
and owning UUID, with referenced saved/live recipe children, not history.
Background file materialization reuses prepared output without filtering.
Full suite 124 passed, including identity/collision/load/reload/path/copy cases.
See: `docs/PERSISTENCE_AND_TEMP.md`, `docs/FILTER_LIFECYCLE.md`, B80 (OPEN).

## 161 — DONE — DESIGNER CONFIRMED (2026-10-14, §159)
~~New issue, everytime I click on the minis, after reordering them, the last ones seems to flicker old names, for the current layout, the flicker of other wrong layout names starts as of filter number 5.  Regardless, this is another clear spaghetti code symptom from the weak worker.  Please review carefully and fix the code to address the root cause in the code please!~~
Root: two drag controllers left Qt's pressed/DraggingState armed; its later
default drag could remove a row after the custom move. A separate mutable
order list then updated wrong/missing items. Before-fix event test reproduces
the armed state; one Qt startDrag override, UUID-only MIME, model-derived
order, UUID item lookup, and deduplicated startup ordering repair ownership.
No missing-item guard, forced content refresh, or filter processing workaround.
Full suite 131 passed. Expanded native 11-filter runs at 100%/200% check eight
gestures, row/UUID preservation, normal caption pixels, and 33 later mini clicks
per scale with no filtering/replaced artifacts. Captures actually viewed.
The first expanded smoke hit xdotool --sync's same-position wait; the harness
was corrected and full reruns passed. 75% ghost remains unchanged. B81 explicitly
confirmed in §159 on 2026-10-14 (America/New_York).
See: `issues.md` B81, `docs/UI_LAYOUT.md`, `docs/FILTER_LIFECYCLE.md`.

## 163 — DONE (designer §159: confirm reordered-name fix)
~~Ok, seems good, you can mark this as fixed.~~
B81/§161 marked FIXED — DESIGNER CONFIRMED — 2026-10-14, citing §159;
only this acceptance is closed. The new spacing/background requests follow.
See: `issues.md`, `docs/DESIGNER_VERBATIM.md` §159.

## 164 — DONE (designer §159: equal top and bottom mini gaps)
~~Your previous fix to the mini hightlight and vertical scroll added back the white space gap at the bottom of the minis strip.  I want the same gap as at the top of the minis.~~
Stub: shared 4px padding; last caption end + padding derives a 162px cell,
replacing the old 178px/20px bottom gap. Qt still reserves its native scrollbar
separately. Full captions, complete ghost, zero vertical range, and 14/16/30px
scrollbar-style cases retained. Full suite 134 passed; native 100%/200% drags
and 33 post-reorder clicks each passed, captures viewed. B82 remains OPEN
awaiting explicit designer acceptance.
See: `docs/UI_LAYOUT.md`, issue B82.

## 165 — DONE (designer §159: darker mini background)
~~Also, the background of the minis should be a bit darker so that I can see the difference between the white mini page outline and the background.~~
Stub: strip-only Base = theme Window.darker(105), including palette changes
and all color groups. Native Window was nearly white, so unshaded Window
was visually too subtle. Shared display/ghost ground, unchanged blue wash
and uniform 75% ghost; no border or other-pane palette change. Light/dark
regressions and full suite 134 passed; native 100%/200% passed, captures
viewed. B83 remains OPEN awaiting explicit designer acceptance.
See: `docs/UI_LAYOUT.md`, issue B83.

## 166 — DONE (designer §160: Discard Changes button wording)
~~Change "Close without saving" to "Discard Changes"~~
Stub: explicit text on the standard Qt Discard button, retaining destructive
role and Cancel escape action. Native theme no longer substitutes close-only
wording. Full suite 150 passed; offscreen/native 100%/200% dialogs captured
and actually viewed. B84 remains OPEN pending explicit designer acceptance.
See: `docs/FILTER_LIFECYCLE.md`, issue B84.

## 167 — DONE (designer §161: canceled mini switch stays edited)
~~Also, after clicking another filter in the minis, if I escape the "Unsaved filter changes", the filter selection changed, but nothing was saved, nor discarded, this is wrong.  Cancel should remain on the edited fiter.~~
Stub: reproduced real Escape/Cancel/close leaving the correct current filter
but the wrong highlight. Qt changes current before selection; keyboard can
select twice. Block only view notifications during the whole native input
handler, then notify one shared switch controller once. No timer rollback or
replacement drag controller. Full suite 150 passed, including repeated mouse,
keyboard and post-reorder real modals and every Save/Discard/Save As/Cancel
decision through both inputs. Native 100%/200% dirty mini Escape and retained
selection/files passed; captures viewed. B85 remains OPEN pending acceptance.
See: `docs/FILTER_LIFECYCLE.md`, issue B85.

## 168 — DONE (designer §162: revert changes icon)
~~Also, add a revert changes igon beside the dropdown, the typical counter-clockwise arrow, right?~~
Stub: Revert Changes immediately beside dropdown, with tooltip/accessibility
name, enabled only for the active draft. The original custom arrow is
superseded by §201 / designer §197's standard document-revert icon policy.
Uses existing Discard ownership: restore saved prepared result/controls,
clear `*`, keep selection/other filters, no processing. Ready/debounced/pending
reverts pass in full suite 150; native 100%/200% clicks and captures viewed.
B86 remains OPEN pending explicit designer acceptance.
See: `docs/UI_LAYOUT.md`, `docs/FILTER_LIFECYCLE.md`, issue B86.

## 170 — DONE (designer §164: center actual pages on zoom-out)
~~Center actual one/two/multi-page groups on zoom-out, retaining row-major autowrap.~~
Stub: cap columns by real page count, use the transformed scene-unit stride
without a trailing gap, and reserve scrollbars against the prospective grid
rather than the old layout. Accurate occupied bounds let native Qt centering
work; no padding/translation or forced pan reset. Full suite 166 passed;
real one/two/seven-page and stacked captures viewed, including 1:1 panes/minis.
The full repeated original comment is preserved in §164. B87 remains OPEN
pending explicit designer acceptance.
See: `docs/UI_LAYOUT.md`, `docs/DESIGN.md`, issue B87.

## 171 — DONE (designer §165: preview/original centering discrepancy)
~~Also, oddly, the preview seems to center correctly, but not the original.~~
Stub: original, preview and mini framing use one baseline-owned occupied grid.
Peer zoom reflows page geometry before copying scroll offsets; transaction
guards prevent intermediate propagation. Resize propagates layout too; a
geometry signature skips per-page repositioning during ordinary pan. Full
suite 166 passed, including either-pane zoom, resize, exact-fit boundaries,
centering and real-file selection/view changes with processing forbidden.
B87 remains OPEN until explicit designer confirmation.
See: `docs/UI_LAYOUT.md`, issue B87, TODO §170.

## 172 — DONE — DESIGNER CONFIRMED — 2026-10-14 (designer §§166/167: slow resize/layout feedback)
~~Fix repeated divider adjustments for several seconds after shrinking a wide window.~~
Stub: reproduced 23 delayed header-driven size changes over about four
seconds. Full-content PaneHeader paints elision without changing text or
horizontal layout hints; view timers no longer refresh metadata. Qt keeps
panes equal and respects the draggable control-panel divider/overflow.
Full suite 170 passed; actual 12-page resize/squeeze captures at 100%/200%
were viewed, with geometry stable after 23/49ms and one normal mini refresh.
Explicit acceptance is preserved in §167 and scoped to B88.
See: `docs/UI_LAYOUT.md`, issue B88.

## 173 — DONE — DESIGNER CONFIRMED — 2026-10-14 (designer §167: record resize fix confirmation)
~~Ok, this is confirmed fixed, thank you.~~
Stub: B88 explicitly marked FIXED — DESIGNER CONFIRMED — 2026-10-14 using the
designer's local date. Other unconfirmed issues retain their prior status.
See: `docs/DESIGNER_VERBATIM.md` §167, issue B88, TODO §172.

## 174 — DONE (implementation; designer acceptance pending)
~~BW image-layer composition and actual saved-file benchmarking (§168).~~
Stub: `core/image_layers.py` implements the §171 single-canvas/native-overlay
policy. Actual images.pdf/corpus bytes, stream accounting, timing, text/vector
retention and independent Poppler readback are recorded in `COMPRESSION.md`.
At 300dpi/Otsu OFF fell from 79,750 to 10,397B; FFPR is 4,093B. Native font/
content/container cost explains why retained text is not always smaller.
See: `docs/DESIGNER_VERBATIM.md` §168, issue B89, TODO §178.

## 175 — DONE (implementation; designer acceptance pending)
~~Fix FFPR multi-page image aliasing found during the §168 audit.~~
Stub: `_place_bw` owns each real encoded XObject before placement; no shared
placeholder mutation. Distinct-page regressions cover JBIG2 and PNG fallback;
the actual benchmark verifies all 60 FFPR page results pixel-for-pixel.
See: `docs/COMPRESSION.md`, issue B90, `tests/test_pipeline.py`.

## 176 — DONE (implementation; designer acceptance pending)
~~Keep original native text, without invented glyph masks (§169).~~
Stub: native operators/fonts/geometry/color/opacity retained, including real
clip-only text. §171 supersedes exact cross-image ordering with the native
overlay policy. No rasterized text plus duplicate selectable layer.
See: `docs/COMPRESSION.md`, issue B89, `tests/test_image_layers.py`.

## 177 — DONE (implementation; designer acceptance pending)
~~Retain vector diagrams and document PDF text/vector compression (§170).~~
Stub: native vectors retained; shared optimized saver deflates native content
and font streams, subsets eligible fonts, deduplicates and uses object streams.
Native rendering regressions and stream accounting distinguish lossless native
compression from image thresholding/FFPR. See `docs/COMPRESSION.md`, B89.

## 178 — DONE (implementation; designer acceptance pending)
~~Simplify to one BW image canvas with native overlays (§171).~~
Stub: image operations combine on white; opaque page backdrops stay beneath
the canvas; native text/vector artwork goes above. Original per-image masks
are not kept in the output. The unshipped ordered-run/mask-heavy architecture
was removed; FFPR is the existing flattened-fidelity alternative.
See: `docs/COMPRESSION.md`, issue B89, TODO §§174/176/177.

## 179 — DONE (implementation; designer acceptance pending)
~~Exact original/filter display with no extra bitmap smoothing (§§172/173).~~
Stub: `core/display.py` disables decoder averaging, image interpolation and
AA; prepared pages/minis and Qt display no longer smooth bitmap samples.
Actual FFPR viewport pixels remain 0/255 across low/high/fractional zoom and
normal/2× display scale; real color/opacity remains. No view threshold or
filter jobs. See `docs/UI_LAYOUT.md`, `tests/test_exact_display.py`, B91.

## 180 — DONE (implementation; designer acceptance pending)
~~Disable all PDF-content AA and show native precision on zoom (§§174/175).~~
Stub: both panes redraw the actual PDF on the device pixel grid, clipped to
exposed regions, with bounded display-list/tile caches. Native geometry is
not an enlarged 150dpi raster. Parent-window/individual-pane pixels agree;
shown draft files remain owned until their PDF handles are released.
Full suite 203 passed; 16 exact-display cases also pass at 2× scale.
See: `docs/UI_LAYOUT.md`, `docs/TEST_PLAN.md`, B91, TODO §179.

## 181 — DONE (designer §176: platform certificate and packaging documentation)
~~Document the certified current platform and multi-platform packaging.~~
Stub: `docs/PLATFORMS.md` certifies the verified Debian 13 x86-64 LXDE/X11
source runtime with actual library versions and dated test/launch evidence.
`docs/PACKAGING.md` follows the reviewed sibling/upstream Task Coach patterns,
adapts them for Qt/PyMuPDF, distinguishes runtime/build/validation dependencies
and documents target-specific tools, missing integration and release gates.
Other platforms/installers remain uncertified. No tools installed or releases
built/published. Designer acceptance of issues is separate from certification.

## 182 — DONE (diagnosis requested in designer §177)
~~Explain the added dark border around color images.~~
Stub: live images.pdf color artifacts reproduce a dark image-edge halo. The
color saver resizes/re-encodes RGB independently of the separate PDF soft mask;
transparent source pixels contain black RGB, which bleeds into visible edge
colors during unassociated Lanczos resampling. JPEG can worsen that fringe.
The alleged alpha skip does not detect separate `/SMask` images. B92 remains
OPEN pending designer confirmation; the subsequently authorized processing
repair is implemented under §184, not part of the original diagnosis.
See: issue B92, `docs/COMPRESSION.md`, verbatim §§177/179/180/182.

## 183 — DONE (designer §178: editable numbers/spinners beside sliders)
~~Pair Threshold/Colors sliders with editable numbers and native spin arrows.~~
Stub: `ui_qt/numeric.py` shares one bounded value between QSlider/QSpinBox,
with step-1 arrows, live typing, blocked recipe loads and native size/theme/
accessibility. Existing debounce/dirty/revert behavior stays authoritative.
Five numeric tests (also 2×) and real typed-edit lifecycle case pass. Whole/1:1
shots and normal/2× narrow-panel smoke were viewed; full suite 229 passed.
See: `docs/UI_LAYOUT.md`, `docs/TEST_PLAN.md`; restarted build in `PLATFORMS.md`.

## 184 — DONE (designer §§179/180/182: composite first, then one DPI resize)
~~Fix B92 using full-color composition before one DPI resize and filtering.~~
Stub: shared `core/canvas.py`/`image_layers.py` preparation composes original
imagery/masks, resizes ONCE in full color, then applies BW or color transforms.
Native text/vectors remain; color uses actual flat backdrops, BW its white
canvas. Removed the old per-image color planner and BW RGB/mask resize stage.
Disk-backed source tiles feed one global resize (no tile seams); scratch
cleanup is tested. Real saver/readback/export ownership is unchanged.
Twenty canvas regressions, 229 full-suite tests, real saved-PDF benchmarks,
58 independent image-page decodes and viewed GUI/HiDPI smokes pass.
Updated supervised GUI restarted; B92 remains OPEN for designer acceptance.
See: `docs/COMPRESSION.md`, `docs/TEST_PLAN.md`, `docs/PLATFORMS.md`, issue B92.

## 185 — DONE (designer §§181/182: artwork type and resize/filter order)
~~Explain the Firefox representation and choose the scale/filter order.~~
Stub: Firefox is a bitmap plus opacity mask; native PDF text/vector artwork
is separate. Use full-color composition, one final-DPI resize, then filters
and encoding; no original+upscaled duplicate processing or post-threshold/
post-palette resizing. See `docs/COMPRESSION.md`, TODO §184 for implementation.

## 186 — DONE — DESIGNER CONFIRMED 2026-10-14 (designer §§183/184)
~~Repair low-color artwork mapped to white instead of its closest color.~~
Stub: replace fast-octree default-bin mapping with representative palette
fitting and exact full-resolution nearest-RGB assignment; retain real white
and exact few colors. Shared helper, no dithering or preview-only transform.
Eleven palette regressions, actual saved-PDF decoding and viewed low-color
captures pass. Designer explicitly confirms the improvement in §184.
See: B93, `docs/COMPRESSION.md`, `docs/TEST_PLAN.md`.

## 187 — DONE (designer §183: one global filter-edit debounce)
~~Unify every filter control under one trailing debounce and recommend a time.~~
Stub: existing single edit path now uses the recommended 300ms precise timer.
Every recipe input restarts it; controls/dirty marker stay immediate, completed
identical files remain reusable and view-only framing never runs filters.
Four lifecycle regressions plus a real-file mixed-spinner/slider/typing smoke
verify one final recipe and preview publication. Full suite 244 passed.
Restart recorded in `PLATFORMS.md`; B94 remains unconfirmed by the designer.

## 188 — DONE (designer §184: palette confirmation and root-cause explanation)
~~Record explicit confirmation and explain the palette defect.~~
Stub: B93 records the designer's verbatim acceptance and local date, limited
to the low-color improvement. Explain missing octree lookup buckets/default
white, insufficient nearest-color validation, improved palette fitting and
full-resolution assignment. See `docs/COMPRESSION.md`, B93 and verbatim §184.

## 189 — DONE (designer §185: native full-width mini progress overlays)
~~Match the default progress style, span the full reserved mini width and
provide an opaque white backing.~~
Stub: shared delegate paints the native Qt control over the selection wash,
150px wide with native height and a white backing; model progress is separate
from cached content. Completion removes the overlay, strip geometry and the
uniform 75% ghost stay unchanged. Full suite 272 passed; 28 new pixel/behavior
cases also pass at 2×. Both-scale screenshots actually viewed; native DnD
passes at 100%/200%. App stopped/group verified/restarted under supervision.
See `docs/UI_LAYOUT.md`, `docs/TEST_PLAN.md`, `docs/PLATFORMS.md`, B95.
Initial stage complete; final refined B95 appearance was subsequently
DESIGNER CONFIRMED 2026-10-14 (§192, TODO §§190/193–195).

## 190 — DONE (designer §187: progress overlay inset leaves highlight visible)
~~Inset the progress bar and backing by the shared mini padding.~~
Stub: STRIP_PADDING=UI_PADDING=4 leaves a 142px overlay in the 150px cell and
visible selected highlight. §§190/191 later replace native height, image-area
centering and 2px white padding with enlarged full-frame-centered progress.
Thirty-two final progress cases pass at 100%/2×; captures viewed, native 100%
DnD passes. See `docs/UI_LAYOUT.md`, TODO §§193–195 and B95's confirmation.

## 191 — DONE (designer §188: title-free strip and one main-region spacing policy)
~~Remove the minis title and unify all main-region outer insets/gutters.~~
Stub: shared UI_PADDING=4, zero-margin PreviewPair/PaneBlock, root-owned
insets, aligned frame sides/bottoms and no title/placeholder row. Both-scale
geometry/resize checks and native 100% DnD pass; screenshots viewed, full suite
319 passed, app normally restarted. See `docs/UI_LAYOUT.md`, `docs/TEST_PLAN.md`.
B96 stays OPEN pending designer acceptance; §192 adds the matching panel header.

## 192 — DONE (designer §189: Save As selects the newly created filter)
~~Select the new Save As copy and audit equivalent dirty-resolution paths.~~
Stub: explicit immutable resolution destination and one activation commit for
mini/dropdown/keyboard, direct Save As, open/close and canceled naming. Both
files stay owned; existing/pending work is reused. Matrix and real nested-
dialog smoke pass, actual captures viewed, full suite 319 passed.
See `docs/FILTER_LIFECYCLE.md`,
`docs/PLATFORMS.md` and B97 (still OPEN for designer acceptance).

## 193 — DONE (designer §190: 50% taller mini bars and percentage text, no white padding)
~~Enlarge native mini bars and percentages by 50%; remove extra white padding.~~
Stub: 1.5× native size-hint height and point/pixel font, backing EXACTLY within
the bar, shared 4px side inset unchanged. Native style/true work/completion,
150×162 cell and uniform 75% ghost retained. Final 32 cases pass at both
scales with exact native pixels; real/fixture screenshots viewed.
See `docs/TEST_PLAN.md`, `docs/PLATFORMS.md`.
B95 FIXED — DESIGNER CONFIRMED — 2026-10-14 (§192); no broader acceptance.

## 194 — DONE (designer §191: center progress within the entire mini cell)
~~Center progress vertically in the whole mini frame, not just its page image.~~
Stub: delegate uses the full actual cell height/origin for viewport and drag
source. Geometry cases cover shifted/negative origins and short/normal/tall
frames; both scales pass with unchanged cell height and no new whitespace.
See `docs/UI_LAYOUT.md`, `tests/test_minis.py` and B95's §192 confirmation.

## 195 — DONE (designer §192: explicit acceptance of mini progress appearance)
~~Record the designer's confirmation of the completed mini progress changes.~~
Stub: B95 FIXED — DESIGNER CONFIRMED — 2026-10-14 (America/New_York), scoped
to native styling, highlight inset, enlarged bar/text, no white padding and
full-frame centering. §192's "Ok, this is good." does not confirm B96/B97 or
unrelated DnD issues. Exact full message is preserved in the verbatim log.

## 196 — DONE (designer §192: configuration heading matches the preview blocks)
~~Add a Configuration heading above the right panel, matching the previews.~~
Stub: all three regions reuse PaneHeader and zero-margin PaneBlock, with 4px
spacing and aligned header/frame tops and bottoms. Both-scale geometry/resize
checks pass (last settling 0.099s/0.182s); full/1:1 captures viewed, full suite
319 passed and final app restarted. See `docs/UI_LAYOUT.md`, B98 (unconfirmed).

## 197 — DONE (designer §192: low-color palette as colored JBIG2 stencils)
~~Design and benchmark one colored lossless JBIG2 stencil per non-white color.~~
Stub: `tools/layered_color_jbig2.py` reuses native composition, one palette map,
native artwork and final PDF optimization. Opaque white base, disjoint masks,
exact palette-byte paint colors and matching physical page transforms.
18 cases / 34 page pairs / 107 masks decode exactly; 13 prototype tests pass.
Wins AND regressions, viewer sampling caveats and two existing production
encoder findings documented. No production codec/default changed (§193).
See `docs/LAYERED_COLOR_JBIG2.md` and issues B99/B100 (audit findings only).

## 198 — DONE (designer §§193/194: dedicated layered-JBIG2 design/benchmark document)
~~Create and cross-reference the layered-JBIG2 developer design/benchmark document.~~
Stub: `docs/LAYERED_COLOR_JBIG2.md` records the model, references, prototype
boundary, reproducible commands, all 18 whole-PDF size rows, timed stages,
exact decoder checks, Poppler display/source-warning limits and next decisions.
Linked from overview, design, architecture, compression and test plan. Inputs
and production filters unchanged. Verification is not designer acceptance.

## 199 — DONE (designer §195: remove redundant working labels)
~~Remove the redundant mini working placeholders; progress already shows activity.~~
Stub: no pending image/amount or header sizing phrase; missing metadata stays
blank and completed image/bytes stay visible during edits. Eight new cases
cover cached/missing results at 0/37/99/100%, transparent empty slots and no
processing. Combined 46-case subset passes at 100%/2×; actual queued/live/
complete captures viewed, full suite 319 passed, app restarted. Errors and
actionable status messages retained. See `docs/UI_LAYOUT.md`, B101 (unconfirmed).

## 200 — DONE (designer §196: establish icon provenance)
~~Check whether the odd revert/rename icons are standard KDE/Nuvola assets.~~
Stub: both were custom QPainter drawings, unlike theme-first Copy/Save.
The rename comment misread §120's request for a STANDARD cursor/letters icon
as a request for custom drawing. Reported without changing the app; §197
then approves consistent theme icons with one coherent standard fallback set.

## 201 — DONE (designer §197: consistent native-theme icons with a standard fallback)
~~Use consistent desktop-theme icons and one standard portable fallback set.~~
Stub: one provider/binder serves filter actions, zoom, export/stop and the
button lab. Desktop names win; bundled stock Breeze light/dark 16/22px SVGs
provide the fallback, matched to actual control/toolbar palettes. Provenance,
checksums, licenses and packaging/plugin gates recorded. Full suite 339
passed; 33 focused cases also pass at 2×; real/fallback light/dark full windows
and 1:1 enabled/disabled controls viewed at both scales.
B102 remains OPEN for designer acceptance.
See `docs/ICONS.md`, `pdf_minify/ui_qt/icons.py`.

## 202 — DONE (designer §§198/199: mini progress enlargement is 25%, not 50%)
~~Use 25%-larger mini bars, instead of the previous 50% enlargement.~~
Stub: one shared 1.25× factor scales original native height and percentage
font; reserved width, 4px insets, exact backing and full-frame centering are
unchanged, as is the aggregate status bar. Forty independent native-widget
progress checks pass at 100%/2×; queued/live/complete full windows, 1:1 strips,
default bars and selected/75% ghost sources were viewed at both scales.
Full suite 339 passed in 68.67s. B103 remains OPEN for designer
acceptance. See `docs/UI_LAYOUT.md`, `docs/TEST_PLAN.md`, `docs/PLATFORMS.md`.

## 203 — DONE (designer §200: coded icon lab, including Nuvola and Oxygen)
~~Add an Icon Lab window with stock-library options and shareable choice codes.~~
Stub: direct View → Icon Lab… opens one reusable modeless table with 37 coded
Nuvola/Oxygen/GNOME Classic/Breeze options; app-size, disabled and 32px previews,
original source names, light/dark review, native small-window scrolling,
per-action radio choices, Clear and Copy choices. Nothing applies or changes
app icons/settings/filters/selection/jobs. Original PNG bytes, sizes/hashes,
source versions, copyright/license texts and Nuvola's artwork addendum bundled.
43 focused cases pass at normal/2×; actual full windows and 1:1 cards viewed.
Full suite 382 passed. B102/B104 remain OPEN pending designer choices/acceptance.
See `docs/ICON_LAB.md`, `docs/TEST_PLAN.md`, `docs/PLATFORMS.md`.

## 206 — DONE (designer §203: editable compression and precise threshold label)
~~Expose six editable image codecs and qualify the threshold-method control.~~
Stub: Image compression offers JBIG2 BW/Color, Flate BW/Color (palette),
JPEG2000 and JPEG. Actual saved/draft mode controls dispatch, enabled states,
readouts, effective keys, Save/Save As and built-in override reload. Shared
core stencil code serves production and the study; strict codec selection,
unambiguous encoder transport and diagnostic-aware decode checks replace
hidden substitution. Preserve UUID/name/order/defaults, native artwork,
BW-only FFPR and one 300ms timer. Final full suite 429 passed; both-scale
real-file UI/resize captures and lifecycle smoke pass and were viewed.
See `docs/COMPRESSION.md`, `docs/TEST_PLAN.md`; B99/B100/B105 remain OPEN
for explicit designer confirmation. DONE is not designer acceptance.

## 207 — DONE (designer §204: distinguish native-stream and image compression)
~~Explain native text/vector/font compression independently of image encoding.~~
Stub: Image compression never disables shared native/font/container
optimization. Flate is the default native codec; LZW/RunLength are valid
historical alternatives. The subsequent §205 explicitly requests a native
selector, expanding the initial explanation-only scope: eligible compressed
native streams are now deliberately recompressed, while encoded images,
metadata and attachments remain untouched by that selector. See
`docs/COMPRESSION.md`, `docs/NATIVE_STREAM_COMPRESSION.md`, TODO §208.

## 208 — DONE (designer §205: native-stream selection and benchmark document)
~~Add independent native-stream compression and benchmark sizes/times/support.~~
Stub: PDF streams offers Flate (unchanged default), Flate (Zopfli, slow)
and Brotli (limited reader support), using shared saved/draft state and timer.
`docs/NATIVE_STREAM_COMPRESSION.md` records primary sources, 32 paired
source/policy cases / 64 outputs, complete PDF sizes, both timing repeats,
native-byte/image/pixel checks and actual reader failures. LZW/RunLength
lose in this corpus and remain benchmark controls, not UI clutter. Empty
streams stay plain to avoid the bundled encoder's invalid empty Brotli.
Final full suite 429 passed in 174.96s; both-scale UI/resize and real lifecycle
smokes pass. B106 remains OPEN; no acceptance is inferred.

## 211 — DONE (designer §208: applicability and scope of Brotli image comparison)
~~Explain existing Brotli measurements versus indexed color and BW/JBIG2.~~
Stub: existing Brotli study changes native streams ONLY and preserves bitmap
bytes, so it provides no image-codec ranking. The PDF extension allows Brotli
on image XObjects; a valid comparison encodes identical packed palette/BW
pixels versus the corresponding exact JBIG2 representation. Reported the
actual historical Indexed/JBIG2 color numbers, not invented Brotli results.

## 212 — DONE (designer §209: size-only bitmap compression benchmarks)
~~Benchmark equal-pixel Indexed/BW Flate, full Zopfli and Brotli versus BW/colored JBIG2.~~
Stub: 22 paired cases / 176 actual optimized PDFs / 600 candidate pages;
same prepared pixels, palette/threshold/DPI and native Flate per case. Plain
and reversible PNG-predicted byte streams, current product policy, real
artwork/scans/native-overlay/FFPR and flat/noise controls. Every final image/
mask and actual MuPDF page matches; complete PDF bytes, image bytes, hashes
and source diagnostics retained. Zero timing fields. Controlled identifier
framing removes size noise without changing product ID defaults. Full tables,
wins/regressions and reproduction are in `docs/IMAGE_STREAM_COMPRESSION.md`;
artifacts in `.tmp/image-stream-compression/size-20261015/`. Thirty-one new
benchmark cases pass in the final full suite: **460 passed**, `./test.sh`.
A pre-existing ghost test now waits for actual view-reframe readiness before
strict pixel comparisons; production ghost/opacity/tolerances unchanged.
No new UI codec/defaults are introduced by this study.
This is completed study implementation, not designer issue acceptance.

## 213 — DONE (designer §210: explain useful compression pairings and FFPR scope)
~~Distinguish valid mixed PDF codecs from useful UI combinations and FFPR overhead.~~
Stub: native Brotli + Flate images is technically valid; a shared general
compressor is a proposed product simplification, not a PDF constraint.
Specialized image codecs do not need another wrapper. Read-only inventory
of both existing FFPR/JBIG2 study outputs finds one shared 35-byte native
painting stream (37 B with Flate); packed-raster compression still matters.
See `docs/COMPRESSION_COMBINATIONS.md`.

## 214 — DONE (designer §211: combinations table first, then UI alternatives)
~~Document reasonable combinations and compare a combined menu with separate controls.~~
Stub: `docs/COMPRESSION_COMBINATIONS.md` starts with twelve mode/FFPR rows,
compressor scope and explicit current-versus-proposed availability. Recommends
separate page/image/general controls, visible disabled effective states and
a read-only combined summary. Color FFPR, unified bitmap compression and
saved-recipe migration require separate approval/integration; current code
and defaults are unchanged. Cross-referenced from the main design, compression,
UI and entry docs. This completes the requested documentation, not approval of its
proposed UI and not designer issue acceptance.

## 215 — DONE (designer §212: assess scope and duplication of the combination table)
~~Review the table against repository document types and the available benchmarks.~~
Stub: recommended factoring FFPR out of repeated family rows, retaining
mixed palette winners, and recording preserve-images/native-only cases.
Full-color/grayscale lossless byte encoding remains a research suggestion,
not an approved addition. The worker's encoder-dependency rationale for
retaining Flate BW is subsequently superseded by designer §213. No code
change, new benchmark or assertion of whole-corpus codec dominance.

## 216 — DONE (designer §213: verify Zopfli support and record opinionated best-encoding policy)
~~Confirm unchanged Flate decoder support and supersede speed-based product choices.~~
Stub: upstream Zopfli and RFC 1950/1951 confirm standard zlib/DEFLATE output;
any conforming FlateDecode implementation can decode correctly embedded
Zopfli data without encoder-specific support. Recorded the exact ruling,
corrected the matrix to optimized Flate versus Brotli formats, retired the
old effort/dependency rationale, and distinguished current implementation
from the target throughout design/developer/packaging docs. Strongest measured
does not mean universally smallest; explicit codecs/fidelity remain intact.
Documentation only; runtime alignment is OPEN below. No designer issue
acceptance is claimed.

## 217 — OPEN (designer §213: align runtime with best encoding and decoder-support choices)
The current UI still exposes ordinary Flate and Zopfli separately, native
Flate defaults to zlib, and Indexed has a 100,000-byte Zopfli performance
cutoff. Align the implementation with §213: one optimized Flate output format
using the best validated encoder(s), no weaker speed/dependency choice or
arbitrary performance cap. Retain same-format alternatives internally only
when actual valid output size justifies them; preserve exact filtered pixels,
native data and the selected decoder format. Package required encoders and
report real failures, not silent inferior fallback. Review image/native and
container paths without inventing new reader filters. Preserve UUIDs, saved
recipes, dirty lifecycle, exact readback/amounts and cache correctness; do not
claim zlib-versus-Zopfli needs a different reader or confuse format/encoder.
Keep Brotli's measured-reader warning. Other image families may be retired
only with real size/reader-support evidence at the chosen fidelity, not just
dependency convenience or one small corpus. Exact UI layout, automatic
cross-format policies, color FFPR and extra representations remain separate
design proposals. Full tests and proportional GUI checks are required when
implemented.

## 218 — OPEN (designer §214: remove classic Flate from product options, retain references)
Remove the redundant ordinary-zlib choice, retain optimized Flate with the
same FlateDecode reader support, and keep classic results/encoders in the
comparison tools/tables for reference. Handle saved legacy policy names and
defaults consistently; never relabel classic encoding as optimized. This
focused implementation step within §217 is still pending.

## 220 — DONE (designer §216: move the request log into docs)
~~Move TODO.md to docs/TODO.md and update active references.~~
Stub: request history is preserved at `docs/TODO.md`; developer entry points,
README and root issue references use the new location. Remaining historic
numbers/order are unchanged. Old stubs retain their period-specific layout
descriptions, identified as historical in this file's introduction.

## 222 — DONE (designer §219: separate PNG prediction from the main size analysis)
~~Move the paired +PNG comparison into its own document and explain the expected size overhead.~~
Stub: the documentation split was implemented, then superseded by designer
§220 / TODO §223. All paired results and relevant interpretation are retained
in the main tables of `docs/IMAGE_STREAM_COMPRESSION.md`; no separate
predictor-only document remains. Dataset and product behavior are unchanged.

## 223 — DONE (designer §220: restore paired benchmark columns and remove editorial corrections)
~~Keep the +PNG results in the main tables and remove typo-correction discussions from the docs.~~
Stub: both main bitmap tables again show Flate/Zopfli/Brotli plain and +PNG
alongside JBIG2. All 154 size cells match the unchanged measurements and actual
PDF sizes/hashes. Same-encoder baselines and six BW gains remain explicit.
Removed the editorial codec-correction passage, correction log, mnemonic,
inline correction asides and instructions to maintain those discussions.
Designer quotations, stable IDs, codec requirements and reader-support rules
remain intact. The redundant predictor-only document is removed; its results
and relevant methods are retained in `docs/IMAGE_STREAM_COMPRESSION.md`.
Documentation only; no new encoding or timing run, code change or issue acceptance.

## 224 — DONE (designer §221: bold the smallest size in every benchmark row)
~~Highlight the best result in each main bitmap benchmark row using Markdown bold.~~
Stub: both size tables in `docs/IMAGE_STREAM_COMPRESSION.md` emphasize the
smallest complete-PDF size per same-input row, with ties included by rule.
All 22 rows are checked against the stored measurements; all 154 numeric
values, row labels and codec columns remain unchanged. Highlighting does
not override reader-support limitations. Documentation only.

## 225 — DONE (designer §222: integrated complete-file compression matrix)
~~Measure image/predictor × native policies as actual final PDFs in one primary size matrix.~~
Stub: `tools/bench_integrated_compression.py` measures 549 actual PDFs across
51 recipes / 11 complete inputs / 1,980 candidate pages: all 21 paired bitmap/
native combinations per case, plus explicit JPEG, JPEG2000 lossy/lossless and
preserve-images recipes. Plain/+PNG, classic reference Flate, full Zopfli,
Brotli and BW/colored JBIG2 remain visible; unsupported color FFPR is explicit.
Actual complete-file bytes only; frozen image/font inputs, exact native/image/
page readback, controlled IDs, validated resume and retained provenance/hashes.
The shared saver can skip re-subsetting already-prepared fonts after an
eight-byte checksum rewrite was caught; normal product behavior is unchanged.
The original matrix's 549 cells/files and tied bold minima were independently
verified. Its exhaustive publication layout is superseded by designer §223 /
TODO §226; the actual artifacts remain archived diagnostic evidence. The
primary Markdown analysis remains `docs/INTEGRATED_COMPRESSION.md`.
Fourteen focused tests and fresh full suite **474 passed**. No benchmark
timings, GUI codec/default change, desktop launch or issue acceptance claimed.

## 226 — DONE (designer §223: representative, realistic integrated size tables)
~~Publish realistic combination rows over five representative complete PDFs,
with focused scenarios and actual final-file bytes.~~ `INTEGRATED_COMPRESSION.md`
now has 42 descriptive rows, **210 verified overview PDFs**, no excluded
cells and **62 focused PDFs**: **272 distinct final outputs**, zero rejected
cells, after designer §229 / TODO §234 filled the former 22 gaps.
Same-general-compressor pairs, meaningful specialized codecs, classic
Flate reference, plain/PNG prediction and separate fidelity groups are retained.
All prepared rasters are 300 DPI; controls are explicitly unresampled.
Bytes/hashes and tied bold minima are independently audited. QPDF syntax
passes 179 ordinary-format files; 93 unsupported Brotli files are excluded
from that reader check. Full **561-test** suite passes. Earlier mixed-DPI/
rejected studies remain historical evidence, not current results. See §§227–231.

## 227 — DONE (designer §224: repair preparation failures and support color FFPR)
~~Repair the production preparation roots and extend FFPR to every existing
color codec; measure valid complete outputs at 300 DPI.~~ Direct stencils,
explicit filter flags, conservative tag repair and original-native ownership/
operators address B108–B112. All six codecs share the actual saver, full-color
composition, one resize, effective recipe/dirty lifecycle and real-file readback.
The uniform overview/focused run validates all 250 final files; full **552-test**
suite, complete-source preflight and reviewed normal/2× offscreen captures pass.
See `COMPRESSION.md`, `TEST_PLAN.md` and `INTEGRATED_COMPRESSION.md`.
Issue acceptance remains pending explicit designer confirmation.

## 228 — DONE (designer §225: uniform 300 DPI filter defaults and benchmarks)
~~Set every built-in raster default/missing-DPI fallback and all transformed
benchmark cases to 300 DPI, retaining editable DPI and stable identity.~~
Implemented through shared defaults; §229 covers the authorized one-time
saved/custom migration. Every transformed overview/focused case uses 300 DPI,
without lower-DPI variation tables. Preserve-images controls remain explicitly
unresampled. Historical artifacts are not relabeled as current results.
See `COMPRESSION.md`, `PERSISTENCE_AND_TEMP.md` and the then-250-file integrated report
(expanded under §§234/236).

## 229 — DONE (designer §226: migrate all existing saved raster filters to 300 DPI)
~~Migrate every existing saved/custom raster filter to 300 DPI once, retaining
identity, other parameters and subsequent deliberate edits.~~ Implemented by
`core/filter_defaults.py` before saved specs/artifacts are built; persist
migrated custom records and a revision marker through normal QSettings load.
Six migration cases and full **552-test** suite pass. Offscreen isolated
settings confirm every recipe loads at 300 DPI; no designer desktop launch
or settings mutation was performed. See `PERSISTENCE_AND_TEMP.md` and
`TEST_PLAN.md`. This is implementation completion, not designer acceptance.

## 230 — DONE (B111: preserve inherited native text state through image-layer assembly)
~~Retain visible Form text and original native operators without the
sanitizer's deferred `0 Tr` loss; remove only replaced bitmap/backdrop paint.~~
Implemented `core/native_layer.py`, pruned native resources and native
inline-image boundary parsing. Synthetic exact-pixel/inherited-state,
repository map, glyph-outline, real-space and diagnostic-isolation regressions
pass, as does the full **552-test** suite and complete-source 300-DPI preflight.
The uniform integrated rerun uses this repaired path. See B111,
`COMPRESSION.md` and `TEST_PLAN.md`; issue acceptance remains pending.

## 231 — DONE (B112: retain correct accessibility ownership without original bitmap payloads)
~~Keep structure-tree references attached to actual native page/Form owners
without retaining replaced original bitmap streams.~~ The compositor retains
native identity/MCID/ParentTree/Alt semantics and the original catalog for BW
and color, prepends an Artifact canvas, and reads immutable originals across
shared Forms. Tagged derivative conflicts fail explicitly; no metadata is
silently stripped. Nine tagged/whole-file regressions, the full **552-test**
suite and renewed complete-source 300-DPI preflight pass. The integrated
study at that stage has 250 verified final PDFs with fresh provenance and zero rejected
cells; old affected files remain diagnostic only.
See B112, `COMPRESSION.md`, `ARCHITECTURE.md` and `TEST_PLAN.md`.
Implementation completion is not designer acceptance or PDF/UA certification.

## 232 — DONE (designer §227: group the integrated overview by output type)
~~Group the primary overview as BW, indexed color / low palettes, then full
color, with unresampled references above the groups.~~
Stub: `INTEGRATED_COMPRESSION.md` groups 3 reference rows, then 15 BW,
15 indexed and 9 full-color rows across the same five PDF columns. The initial
regrouping preserved all 210 cells (then 188 measured sizes and 22 gaps),
labels and per-fidelity bold minima. §234 subsequently measures those gaps.
Native-retaining rows precede FFPR within each group;
indexed FFPR stays indexed. Focused tables and benchmark artifacts are intact.
The row/cell/minimum and stable-ID/quotation/link audits pass, as does a fresh
full **552-test** suite. See `DESIGN.md` §227 and `DEVELOPER_GUIDELINES.md`.
Presentation only; no processing, algorithm, default or issue-acceptance change.
The separate-table presentation is superseded by designer §228 / TODO §233.

## 233 — DONE (designer §228: one continuous overview table with divider rows)
~~Use one continuous overview table with unnumbered title-only divider rows.~~
Stub: `INTEGRATED_COMPRESSION.md` now has one header and one uninterrupted
table: reference controls, BW, indexed color, then full color. Divider titles
occupy only the far-left source cell; all five following cells are blank.
Markdown render and data audits confirm one table, all 42 measurement rows,
unchanged values/bold minima and unchanged focused tables. No HTML is needed.
The fresh full **552-test** suite passes. This changes presentation only,
not benchmark coverage or processing. See `DESIGN.md` §§227/228.

## 234 — DONE (designer §229: benchmark every combination, including no-image no-ops)
~~Remove native-only exclusions; measure every row/input, even when redundant.~~
Stub: runner and formatter require all 42 × 5 = **210 measured cells**. The
22 missing cells now have independent complete saved files and original-native/
pixel/zero-image verification; no control size or file was copied. The earlier
188 overview and 62 focused outputs retain actual files and bounded compatible
provenance: **272 distinct outputs**, zero rejected or excluded cells. Coverage
caught B113's xref-stream ID bug; its shared preparation repair preserves all
image-bearing/FFPR paths and keeps the strict cross-version import gate intact.
The continuous table includes tied minima and annotated no-op repeats. New
row-coverage/distinct-save and plain/xref-stream no-image tests pass; full
**561-test** suite passes. See `INTEGRATED_COMPRESSION.md`, `TEST_PLAN.md` and
B113, which remains OPEN pending explicit designer confirmation.

## 235 — DONE (designer §230: rename the project to PDF Minify)

~~Rename the product/package and active project references, preserving saved
settings and the designer's separately managed repository rename.~~
Stub: UI **PDF Minify**, package `pdf_minify`, machine/temp/settings slug
`pdf-minify`. One shared settings factory imports legacy values once without
overwriting new keys, deleting old data or resurrecting later removals. The
flat Python layout, GitHub remote, exact quotes and measured provenance remain
intact. All 42 licensed files are byte-identical. Eleven identity/migration/CLI
cases and the fresh **572-test** full suite pass. Normal/2× isolated GUI captures
exit 0 and were viewed. The real settings migration waits for a normal launch;
worker verification is not designer acceptance.
See `DESIGN.md` §230, `ARCHITECTURE.md` and `PERSISTENCE_AND_TEMP.md`.

## 236 — DONE (designer §231: sixth representative document — NASA Kepler)

~~Add whole-document NASA Kepler as a sixth case, measuring every combination
and retaining the existing five sources and actual results.~~
Stub: **Technical illustrations** adds all 12 pages (text on 12, vectors on ten,
15 image placements across nine). All **42** new complete PDFs are saved and
verified at common 300-DPI transforms, with unresampled controls. The continuous
overview has **252 numeric cells**, zero exclusions/rejections; all 210 earlier
cells/files and focused tables are unchanged. The publication references
**314 distinct complete PDFs**. Pinned B113 and literal namespace proofs keep
old/new source provenance honest without a permissive import bypass. All bytes,
hashes, minima and seven-column Markdown rendering pass independent checks;
QPDF passes 207 ordinary outputs, excluding 107 unsupported Brotli outputs.
The fresh **572-test** suite passes. The residual-stream legend explicitly
means fixed Zopfli-Flate, not automatic best selection. No encoding-time
comparison, new GUI choice/default, dependency or designer acceptance is claimed.
See `INTEGRATED_COMPRESSION.md` and `TEST_PLAN.md`.

## 237 — DONE (designer §232: explicit BW/Otsu heading and concise combination labels)

~~Rename the BW divider to Black and white (BW + Otsu); remove redundant
`; keep native`, since absence of FFPR implies native preservation.~~
Stub: updated the overview and focused labels plus their generator. FFPR,
native-stream compressor names and focused Simple threshold columns stay
explicit. An exact report audit preserves every measurement and bold minimum;
regression coverage keeps generated and published combination labels aligned.
This is presentation only; no filter, benchmark output or GUI behavior changes.
See `DESIGN.md` §232 and `INTEGRATED_COMPRESSION.md`.

## 238 — DONE (designer §§233/235 / B114: JBIG2 same-DPI end-to-end non-regression)

~~Repair the 300→301→300 preparation error; retain the full eight-page JBIG2
input and require source-pixel/page-geometry equality and complete-file
non-growth through real native/FFPR saves.~~
Stub: the shared compositor preserves actual fractional density; all five
expected-failure markers are removed. Six full-flow cases and three genuinely
fractional-density cases pass; the full suite passes **593 tests**. Fresh
native/FFPR saves are 340,909/337,010 bytes versus the 341,728-byte preservation
control, with every original bitmap/page pixel exact. No codec/default change.
See B114, `JBIG2.md` and `TEST_PLAN.md`. DONE means implementation verified,
not designer acceptance; B114 remains OPEN. The historical main-matrix
replacement/recomputation remains separately tracked in §239.

## 239 — DONE (designer §233: replace the overview scan with a non-JBIG2 PDF)

~~Replace the main already-JBIG2 scan with whole non-JBIG2 CCITT TM972;
repair the codec inventory and publish actual post-repair measurements.~~
Stub: the report now uses all 11 pages / 374,461 bytes of
`scan-naca-tm972.pdf`, including original OCR. All 42 scan combinations and
other affected preparations were newly measured with the §235 repair;
§§236/237 select the current 34 rows. Actual stored filters, corpus inventory,
published source descriptors, saved sizes/hashes and tied minima are guarded
and audited. Historical JFK files remain regression evidence, not main-table
rankings. The full suite passes 605 tests. See `INTEGRATED_COMPRESSION.md`,
`DESIGN.md` §233 and `TEST_PLAN.md`. Implementation verified; B114/B115 remain
OPEN pending explicit designer confirmation.

## 240 — OPEN (designer §234: explore JBIG2 optimization features)

The dedicated [JBIG2 developer guide](JBIG2.md) separates implemented behavior
from research. Current production and published measurements invoke only
`jbig2 -p`: independent lossless generic regions, no `-d`, symbols, refinement
or cross-page dictionary. None of these extra encoder switches has a GUI control.
Do not present the existing results as an exhaustive/best-settings JBIG2 search.

Explore and document, in order:

- Compare generic coding with and without `-d` typical prediction. It encodes
  repeated rows losslessly, not by deleting image rows. Test both final size
  and actual readers; upstream's old API comments warn of larger streams and
  Ghostscript trouble, so neither a universal size win nor compatibility is
  assumed. Prefer automatic smallest validated same-fidelity encoding over
  a speed/effort setting, if later approved for integration.
- Assess `-s` symbol dictionaries, `-t` classification similarity (installed
  default 0.92), and `-w` weighting (0.50). Keep approximate-symbol substitution
  separate from lossless results; a more stringent threshold is not proof of
  exactness. The app's Otsu/manual threshold controls are different operations.
- Investigate genuine zero-error symbol refinement and maintained encoder
  alternatives. Installed 0.30 and reviewed upstream CLI reject `-r` as broken.
  Do not just bypass that guard: the API exposes a per-symbol error tolerance
  and inactive CLI code uses a nonzero value. Require exact reconstructed
  samples and reader evidence before claiming any lossless refinement support.
- Assess document-wide/shared and grouped dictionaries versus per-page
  dictionaries, including `/JBIG2Globals` overhead, references, isolated-page
  decoding with required globals, subset extraction and corrupted/missing
  globals. Dictionary sharing is not inherently lossy; matching/refinement
  determines fidelity. Whole-image PDF deduplication is a separate existing
  mechanism, not evidence that cross-page symbol sharing is implemented.
- If symbol research proceeds, assess `-a`/`--auto-thresh` and `--no-hash` as
  symbol-classification candidates, never as no-op lossless switches. Audit
  encoder versions/library-only coding options rather than invent CLI knobs.

Fix and pass B114's full-flow source-pixel/no-growth gates before promoting
new JBIG2 optimization results. Use whole non-JBIG2 TM972/formulas scans,
already-JBIG2 JFK as regression only, FFPR text, noisy/dithered BW imagery,
flat palette stencils and repeated/sparse/random synthetic patterns. Verify
every decoded image/mask, original geometry/native content, diagnostics and
target readers; measure actual complete PDFs at 300 DPI, not payload estimates.
Freeze inputs, prepared samples, exact arguments, tool/source versions and
all output hashes. Publish Markdown complete-size comparisons with same-
fidelity bold minima, failures and unchanged controls; no timing rankings.
Keep BW and layered color, native and FFPR, and lossless and lossy separate.

This is an exploration task, not authorization to enable lossy coding,
install/change dependencies, replace current recipes, add advanced GUI fields,
or silently change existing saved-filter results. See `JBIG2.md`, B114,
`COMPRESSION.md` and `INTEGRATED_COMPRESSION.md`.

## 241 — DONE (designer §§236/237: remove redundant benchmark rows consistently)

~~Remove the eight main Classic-Flate bitmap rows and their equivalents
throughout ALL focused tables; retain the unresampled reference.~~
Stub: one shared selection drives 34 × six actual overview cells and nine
focused scenarios / 48 additional PDFs. All four bitmap-focused sections
drop equivalent redundant rows; future preparations encode only retained
variants. The report audits 291 size cells against 252 distinct actual PDFs,
with unchanged historical artifacts, recalculated predictor statistics and
same-fidelity tied minima. Regression checks cover row absence/control
retention, full no-image coverage and published source descriptors. Targeted
80-test and actual 30-PDF subset checks pass, followed by the full 605-test
suite. No GUI/default changes or designer defect acceptance. See
`INTEGRATED_COMPRESSION.md`, `DESIGN.md` §§236/237 and `TEST_PLAN.md`.

## 242 — DONE (designer §§238–240: isolate the measured PNG-prediction effect)

~~Move PNG overview rows into a separate baseline-labeled six-document table;
show measured PNG-PDF bytes plus signed change from measured plain baselines.~~
Stub: 26 baseline rows / 156 sizes plus eight PNG rows / 48 measured effects,
with unchanged source/recipe/pixels/native policy and negative meaning smaller.
All original 204 measurements, 252 distinct PDFs and 291 displayed sizes stay
accounted for. Reusable generation and 30 new tests cover pairing, byte counts,
signs, denominator, rounding, wins/ties, failures and the published table.
The 110-test focused run and full 635-test suite pass; an independent actual-
file audit verifies sizes/hashes and signed changes. No new encoding or
residual-stream restructuring; focused data is unchanged. Implementation is
verified, **not designer acceptance**; the PNG-only table awaits review.
See `INTEGRATED_COMPRESSION.md`, `DESIGN.md` §§238–240 and `TEST_PLAN.md`.

## 243 — DONE (designer §242: expand PNG prediction combinations)

~~Add 16/64-color native/FFPR PNG pairs with Zopfli-Flate/Brotli across all
six whole PDFs at 300 DPI, with visible measured baselines and signed changes.~~
Stub: expanded to 16 rows / 96 paired cells; 80 missing files saved, 16
compatible focused outputs reused with original provenance. Sources, palettes,
pixels, native streams and complete sizes are verified; no-image controls and
scoped wins/ties/losses remain explicit. New runner and paired publication
tests pass in the full 654-test suite. **Implementation verified 2026-10-17;
not designer acceptance.** See `INTEGRATED_COMPRESSION.md`,
`COMPRESSION_EXPERIMENTS.md`, `TEST_PLAN.md`, `tools/bench_png_extension.py`.

## 244 — DONE (designer §242: next one-factor benchmark experiment)

~~Plan and build the next binary/A-B complete-file table with one named
factor, fixed recipes, measured references and signed baseline changes.~~
Stub: NATIVE-01 compares standard-Flate reference with named optimized
native/residual encoders: five specialized FFPR rows plus two native controls
across all six sources, 42 pairs. Thirty missing reference PDFs are saved;
candidate/control files are reused. Encoded images remain byte-identical;
all-page rendering, native decoding, file hashes and visible paired arithmetic
are verified. All 362 current files / 471 size cells pass the independent
publication audit; the full 654-test suite passes. No UI/default changes.
**Implementation verified 2026-10-17; not designer acceptance.** See
`INTEGRATED_COMPRESSION.md`, `COMPRESSION_EXPERIMENTS.md`, `TEST_PLAN.md`,
`tools/bench_residual_streams.py`, `tools/publish_compression_experiments.py`.

## 245 — DONE (designer §243: percentage-only PNG effect table)

~~Remove byte counts from the PNG effect table, keeping signed percentages
and measured-baseline comparisons.~~
Stub: all 96 cells are percentage-only, with six columns and paired win/tie
emphasis. Overview, focused and native/residual sizes remain unchanged;
reusable generation preserves this presentation. A data-only audit checks
192 saved files against original measurements, without re-encoding. Targeted
41-test and full 660-test runs pass. **Implementation verified 2026-10-17;
not designer acceptance.** See `INTEGRATED_COMPRESSION.md`, `DESIGN.md` §243,
`TEST_PLAN.md`, `tools/bench_compression_overview.py`.

## 246 — DONE (designer §244: Brotli annotation and PNG overall-winner analysis)

~~Underline Brotli in the PNG table; audit overall winners and recommend
the next controlled experiment.~~
Stub: all eight labels are underlined, with shared identities and all measured
numbers unchanged. Audited unrestricted, focused/historical and non-Brotli
comparisons distinguish no-image ties, real compressor gains and incomplete
reader-tier coverage. JBIG2 `-d` OFF/ON is documented as a 24-pair proposal,
not run or promoted to a product setting. Targeted 41-test and full 660-test
runs pass. **Implementation verified 2026-10-17; not designer acceptance.**
See `INTEGRATED_COMPRESSION.md`, `COMPRESSION_EXPERIMENTS.md`, `DESIGN.md`
§244, `TEST_PLAN.md` and existing JBIG2 optimization TODO §240.

## 247 — DONE (designer §§245/246: FFPR Zopfli versus Brotli and short labels)

~~Compare FFPR/J* residuals with Brotli baseline and Zopfli treatment;
explain regressions and shorten table labels.~~
Stub: five rows / thirty pairs use actual newly saved Brotli files and
verified reused Zopfli files, with encoded images and all-page pixels exact.
Brotli is 100–271 B larger in all cases. Accounting closes per pair; two
metadata-only controls isolate 166 B of current writer declaration overhead
(specification SHOULD, not SHALL), alongside actual payload/filter/Length
costs. Labels shorten to Zopfli without changing identities or old numeric
tables. Targeted 106-test and full 674-test runs pass. **Implementation
verified 2026-10-17; not designer acceptance.** See `INTEGRATED_COMPRESSION.md`,
`COMPRESSION_EXPERIMENTS.md`, `TEST_PLAN.md`, `DESIGN.md` §§245/246,
`tools/bench_ffpr_compressors.py`. No GUI/default change.
