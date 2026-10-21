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
new TODO ID is 270. Routine execution requests are not TODOs (§218).

Current location is `docs/TODO.md` (designer §216). Paths in historical
backtick references are repository-root paths unless stated otherwise;
old descriptions of the previous root placement are historical, not current
instructions. Explicitly removed unrelated entries leave numbering gaps (§218).

## 3 — DONE
~~Full app-vision brief (scans → BW threshold + image recompression, max compression default, ESC cancel, md docs with notes/ideas/tests).~~
Stub: the app vision is captured in the overview and architecture pages.
See: `docs/README.md`, `docs/ARCHITECTURE.md`.

## 4 — DONE
~~Yes, JBIG2, summarize your suggestions to me.~~
Stub: JBIG2 guidance is in the JBIG2 page.
See: `docs/JBIG2.md`.

## 5 — DONE
~~lok, no jxl. Rank frameworks by dependency size and OS/WM range.~~
Stub: JPEG XL inside PDFs was dropped, and the GUI frameworks were ranked by size and OS/WM coverage.
See: `docs/DROPPED.md` (D1), `docs/ARCHITECTURE.md`.

## 6 — DONE
~~Picky smooth custom UI: pan, zoom in/out mouse scroll, next/prev page, DnD, etc.~~
Stub: PySide6 with QGraphicsView was chosen for the custom UI.
See: `docs/ARCHITECTURE.md`.

## 7 — DONE
~~Seems like Qt is really solid, can you double check?~~
Stub: Qt was checked on 2026-10-09: Qt 6.8.2 is in Debian trixie, PySide6 is LGPL, and it fits LXDE/X11.
See: `docs/ARCHITECTURE.md`.

## 8 — DONE
~~Start with Qt; everything local in this directory; tell me what is local vs system packages.~~
Stub: the app runs from a project-local setup, with local and system packages documented.
See: `docs/DEPENDENCIES.md`, `README.md`.

## 9 — DONE
~~Verbatim comments in a design doc, docs dir, dev guidance doc, preset list like camera photo filters with small previews, click → main original+preview side by side H/V, same for filter thumbnails, all as menu view options.~~
Stub: the docs folder, verbatim log, developer guidance, filter strip and View menu layouts were built.
See: `docs/DESIGNER_VERBATIM.md`, `docs/DEVELOPER_GUIDELINES.md`, `docs/DESIGN.md`.

## 10 — DONE
~~Generally forcing alll images on the page and page rasterizing to 300dpi, and 8.5x11, but that also would be options on the main screen.~~
Stub: force-raster, DPI and page size are main-screen controls.
See: `pdf_minify/core/pipeline.py`, `pdf_minify/ui_qt/app.py`.

## 11 — DONE
~~In the docs, always call the operator/user the designer.~~
Stub: the docs call the operator "the designer"; verbatim quotes are unchanged.
See: `docs/DEVELOPER_GUIDELINES.md`.

## 12 — DONE
~~Finish prior work + every request in TODO.md, numbered, never renumbered.~~
Stub: this TODO log exists.

## 13 — DONE
~~Dev guidance carries general-guideline rulings incl. TODO instructions.~~
Stub: general rulings live in the developer guidelines.
See: `docs/DEVELOPER_GUIDELINES.md` (§0).

## 14 — DONE
~~Log important app activity to stdout and provide --debug diagnostics; document the developer workflow.~~
Stub: the app logs to stdout at INFO; `--debug` adds versions, arguments and timings.
See: `pdf_minify/__main__.py`, `run.sh`, `docs/DEVELOPER_GUIDELINES.md` (§6).

## 15 — DONE
~~Keep project work local and scratch in gitignored ./.tmp/.~~
Stub: scratch output goes to the ignored project-local `.tmp/` folder.
See: `.gitignore`.

## 16 — DONE
~~TODO format ruling + dropped-ideas doc (verbatim §16).~~
Stub: this file's format and the dropped-ideas log are set.
See: `docs/DROPPED.md`, `docs/DEVELOPER_GUIDELINES.md` (§0).

## 17 — DONE
~~call it the full developper guidlines md doc~~
Stub: the developer guidance page has its full name.
See: `docs/DEVELOPER_GUIDELINES.md`.

## 18 — DONE
~~move most of your docs to the docs dir please~~
Stub: the analysis docs live in `docs/`.

## 19 — DONE
~~docs-lead ruling (verbatim §19).~~
Stub: doc cross-references are fixed before verification.
See: `docs/DEVELOPER_GUIDELINES.md` (§0).

## 22 — DONE
~~page zoom, pan, etc is always synced on both panes~~
Stub: the original and preview panes mirror zoom, pan and scroll both ways.
See: `pdf_minify/ui_qt/viewer.py`, `tests/test_viewer_sync.py`.

## 23 — DONE
~~left side is baseline, so no preview of basline, right side is per filter.~~
Stub: the left pane is the fixed baseline, the right pane shows the selected filter, and the strip shows one live mini per filter.
See: `docs/DESIGN.md`, `tests/test_minis.py`.

## 24 — DONE
~~find a few public pdf docs that are representative test cases, not too big, 1
to 10 pages, 200k to 10 mb, put in examples dir in this repo~~
Stub: four pdf.js-corpus PDFs and their profiles were added to the examples.
See: `examples/README.md`.

## 25 — DONE
~~also ctl mouse scroll is up/down? Or mouse scroll is page scroll and ctl wheel
is zoom, I think that is more common ui, no?~~
Stub: the plain wheel scrolls and Ctrl+wheel zooms, with both panes synced.
See: `pdf_minify/ui_qt/viewer.py`, `tests/test_viewer_sync.py`.

## 26 — DONE
~~the page viewer should be continuous by default, with a gap between paged.
No page list to the left. Zoom out should aso autowrap to multiple pages per
side if it fits in the window width.~~
Stub: both panes are continuous synced scrollers with page jumps, replacing the page list.
See: `pdf_minify/ui_qt/viewer.py`, `tests/test_continuous.py`.

## 27 — DONE
~~Did you find example pdfs? Your pdf file is not a good example at all.~~
Stub: demos and screenshots use real example PDFs, not a synthetic file.
See: `examples/README.md`.

## 28 — DONE
~~use a 3 page example for the tests please.~~
Stub: the three-page `filled-background.pdf` example exercises continuous scrolling.
See: `examples/README.md`.

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
Stub: the strip shows only real filters, since the left pane is the baseline.
See: `pdf_minify/ui_qt/app.py`, `tests/test_minis.py`.

## 31 — DONE
~~why are you using that terrible pdf as a default?~~
Stub: `examples/images.pdf` is the default demo file.
See: `run.sh`, `tools/shot.py`.

## 32 — DONE
~~the app should show the final size of each filter below it. It should also
show the small preview which is mirroring the current view on the original.
Remove the left panel and put the options in the menu or in the right panel,
there will only be one tool panel and a menu.~~
Stub: a File menu, one right panel and the status bar replaced the left panel.
See: `docs/DESIGN.md`.

## 33 — DONE
~~Don't show the tooltips at the top, waste of space, we will find another
place for that~~
Stub: the pane and strip header labels were removed.
See: `pdf_minify/ui_qt/app.py`.

## 34 — DONE
~~For now, fit everything you can on the right side panel or in the menu.~~
Stub: done with item 32.

## 35 — DONE
~~document, compile and collect these, document in an examples md doc with
descriptions, view them also. [corpus brief]~~
Stub: the public test corpus is in `examples/`, with a manifest, a fetch-and-validate tool and documented profiles.
See: `tools/corpus/`, `examples/README.md`.

## 36 — DONE
~~[historical scan set brief]~~
Stub: ten historical scans were added; faint, dark and ruled scans are mandatory regression tests.
See: `examples/README.md`, `tests/test_regression_scans.py`.

## 37 — DONE
~~don't freeze the whole app when doing the previews, do it in background [...]
(full §37 in verbatim)~~
Stub: filters are processed in background processes capped at half the cores, without freezing the UI.
See: `pdf_minify/ui_qt/jobs.py`, `docs/ARCHITECTURE.md`.

## 40 — DONE
~~change the various names and stubs that has pdf-reducer, to
pdf-minimalist.~~
Stub: the package, imports and launchers were renamed together.
See: `pdf_minify/`, `run.sh`.

## 41 — DONE
~~also, why does it say local? Ref: pdf-reducer (local)~~
Stub: the title and ownership wording were renamed in the docs.
See: `README.md`.

## 43 — DONE
~~the progress bar is supposed to be for EACH filter.~~
Stub: each strip mini shows its own progress bar; the status bar shows only the aggregate.
See: `docs/DESIGN.md`, `pdf_minify/ui_qt/app.py`.

## 44 — DONE
~~when I was clicking on a filter preview, it seemed to be restarting it
processing, but that is incorrect, it should be processed once and only
reprocessed if there is a change of the file or change in the filter
specifications.~~
Stub: results are cached by file identity and filter recipe, so clicks never start new jobs.
See: `docs/FILTER_LIFECYCLE.md`.

## 45 — DONE (superseded by 48)
~~Previews are truncated half page or something, when they should should the
exact preview seen in the preview window.~~
Stub: superseded by item 48.

## 46 — DONE
~~Also, make the thumbnail preview box clear and the filter and size below it
in smaller characters and aso clearly divided~~
Stub: each mini has a framed preview and a caption.
See: `pdf_minify/ui_qt/app.py`.

## 47 — DONE
~~again, why is there reprocessing when I scroll????~~
Stub: scrolling, panning, zooming and page turns are view changes that never start a job.
See: `docs/FILTER_LIFECYCLE.md`.

## 48 — DONE
~~Still wrong! Thumbnails should be a mini version of exactly the current view
of the larger window. [...] each preview shows exactly that from it's own
filter view (internal, no shown, file preprocessed in bg at the start or from
the latest change).~~
Stub: each mini shows the synced main-view framing from its own filter's processed pages, with no jobs on scroll.
See: `docs/DESIGN.md`, `pdf_minify/ui_qt/jobs.py`.

## 60 — DONE
~~Above the original and the applied preview, show the relevant information
for each [...] it should say Original with a new key information, including
the file size.~~
Stub: each pane has a header with name, size and percentage.
See: `pdf_minify/ui_qt/app.py`.

## 61 — DONE
~~Also, in the thumnails and top lines, shows the size percentage, like
original 230kb 100%, filter 1, 23kb 10%.~~
Stub: every size shows its percentage of the original.
See: `pdf_minify/ui_qt/app.py`.

## 68 — DONE
~~File name should be the firlst list of the right side block.  Original and
size stays above the first previous main window~~
Stub: the file name heads the right panel.
See: `pdf_minify/ui_qt/app.py`.

## 79 — DONE
~~why do you have encode and codec on different lines, very incoherent, follow
modern best practices please!~~
Stub: Filter details opens with a `Codec:` line in every mode.
See: `pdf_minify/ui_qt/app.py`.

## 82 — DONE
~~Still, why is codec sometimes the first line and other times the last
line!!??? This is bad design!  There will be one codec per filter, all common
filter properties must show in the same stable sequence at the start, and
custom codec specific options after.~~
Stub: the Codec line comes first in every mode, then common and codec-specific properties.
See: `pdf_minify/ui_qt/app.py`.

## 85 — DONE
~~No, you said buttons combined with the scale percentage, no? [...] there
should only be a single dpi value for the whole filter [...] why are you
making this complicated?~~
Stub: zoom is a −/100%/+ control with a live scale, Save and Cancel share a compact row, and one DPI control rules the active filter.
See: `pdf_minify/ui_qt/app.py`.

## 78 — DONE
~~yes please~~ (toolbar upgrade approval for the §76 zoom row)
Stub: zoom is a joined toolbar pair with magnifier icons and words.
See: `pdf_minify/ui_qt/app.py`.

## 77 — DONE
~~also make the tumbnail stip go full width, right side panel stopping above
with it's own scroll bar if overflow.~~
Stub: the strip spans the window width; the right panel scrolls on overflow.
See: `pdf_minify/ui_qt/app.py`.

## 76 — DONE
~~use the magnifying glass zoom in out and buttons should be small and on same
row, not out row and streched.  Follow modern best practices, maybe short
word also.~~
Stub: zoom uses magnifier icons and short words in one compact row.
See: `pdf_minify/ui_qt/app.py`.

## 73 — DONE
~~page size never changes, so put that in the top block call file info.   The
final name should have it's full path also.~~
Stub: the File box shows the full path, pages, page size and original size.
See: `pdf_minify/ui_qt/app.py`.

## 75 — DONE
~~those are awefull zoom buttons, use proper icons for all of the four buttons
please, small with icons please.~~
Stub: Zoom, Save and Cancel are small themed icon buttons with tooltips.
See: `pdf_minify/ui_qt/app.py`.

## 74 — DONE
~~The filter should not generally have a page size [...] It's an advanced
option only for specific cases when the page size is absurd from incorrect
scanning document problems, no?  What do you suggest?~~
Stub: the original page size is the default; Letter and A4 are options, and unusual sizes get a warning, never an automatic change.
See: `pdf_minify/core/pipeline.py`.

## 72 — DONE
~~I choose jpeg2000 filters and the codec is not shown on the right side, why
the fail??~~ (+ same for JPG)
Stub: Filter details opens with an explicit `Codec:` line.
See: `pdf_minify/ui_qt/app.py`.

## 83 — DONE
~~why do we have two different dpi values??~~
Stub: selecting a filter sets the DPI control from its preset.
See: `pdf_minify/ui_qt/app.py`.

## 71 — DONE
~~drop prev/next, we have scroll bars for that.   Add zoom in/out buttons in
the right hand side panel.~~
Stub: the Prev/Next buttons were removed (scrollbars and PgUp/PgDn page) and zoom buttons were added.
See: `pdf_minify/ui_qt/app.py`.

## 69 — DONE
~~number of pages in the right hand box, things that are constant for
original and any filter stay in the right hand box, as the main info box~~
Stub: the File box shows the name, pages and original size.
See: `pdf_minify/ui_qt/app.py`.

## 67 — DONE
~~I mean to force a reduction of the pallette based on automatic algorithms
and a slider.  Also, benchmark verious tests for the best algorith for
smallest size and which pdf image format is best to store these.   Add a few
example filters please.  Review the filter examples across the corpus of pdfs
docs are a benchmark for the filters to include.~~
Stub: a Colors slider drives palette reduction, Poster 16 and Indexed 64 filters were added, and palette and filter benchmarks were built.
See: `pdf_minify/core/pipeline.py`, `tools/bench_palette.py`, `tools/bench_filters.py`.

## 65 — DONE
~~I just moved the threshold slider and the previous did not update, this is
wrong.  Also, your <1% is wrong, round to the nearest, it's either 1% or
0%.~~
Stub: the Threshold slider is active only for Simple, and percentages round to nearest.
See: `pdf_minify/ui_qt/app.py`.

## 63 — DONE
~~what does <=150dpi mean?  How is that even something that make sense??~~
Stub: the DPI caption meant a downsample ceiling; superseded by item 64.

## 64 — DONE
~~then you don't need to say max, just the dpi, it's assumed it's a max, write
as a ui design ruling, users don't care to see this difference.~~
Stub: captions show plain DPI values.
See: `docs/DESIGN.md`.

## 62 — DONE (standing rule)
~~run, always run after a new build, kill the existing one~~
Stub: after every new build the running app is closed and relaunched, a standing rule.
See: `docs/DEVELOPER_GUIDELINES.md` (§5).

## 59 — DONE
~~please complete your work, don't stop half compelted.  Also make a full test
suite please and run each time please.~~
Stub: colour captions show real saved sizes, and `./test.sh` runs the full suite.
See: `test.sh`.

## 58 — DONE
~~also, prev/next buttons seem to do nothing...~~
Stub: page jumps scroll to the exact grid position.

## 50 — DONE
~~the navigator section is useless, the original window is the navigator for
now.~~
Stub: the overview navigator was removed; the original pane is the navigator.
See: `docs/DESIGN.md`.

## 54 — DONE
~~filter details left side should have it [...] sorry, right side~~
Stub: a Filter details readout shows the active settings with the ruled codec names.
See: `pdf_minify/ui_qt/app.py`.

## 84 — DONE
~~your buttons are not fixed~~
Stub: zoom icons come from the desktop theme with the bundled Breeze fallback.
See: `docs/ICONS.md`, `pdf_minify/ui_qt/icons.py`.

## 56 — DONE
~~I also thought that there was a better jpeg compression algo that was widely
supported, better than the default jpg, but of course, not as good as jpeg
xl~~
Stub: JPEG2000 is a working colour codec with its own filter.
See: `pdf_minify/core/presets.py`, `pdf_minify/core/pipeline.py`.

## 57 — DONE
~~no jpeg as default, use the best compression tools.  Also, are there options
to use jbig2 or similar with reduces colors index count.~~
Stub: few-colour images got a lossless palette candidate (explicit codec choice later replaced it, §203).
See: `docs/COMPRESSION.md`.

## 55 — DONE
~~Also, why is proper saving not wired?? I said the size should NOT be
estimate, but be the real amounts, why is this not done and why do you keep
stopping before your work is completed?  Why are you not following my design
rulings???~~
Stub: BW saves embed real JBIG2, and each stream is decoded and checked before embedding.
See: `pdf_minify/core/pipeline.py`, `tests/test_pipeline.py`.

## 53 — DONE
~~why don't I see the image algorithm?  is that imposed?  It should still be
shown in the filter details.  And is the size based on saving with this
format?  And why estimated?  You should know the exact size of the file once
processing is completed, no?~~
Stub: each mini caption shows the filter name, its recipe and the full-document size.
See: `docs/DESIGN.md`.

## 52 — DONE
~~what is the modern standard keypress for zoom in and zoom out, I tried and
nothing worked.~~
Stub: Ctrl+Plus, Ctrl+Minus and Ctrl+0 zoom both panes.
See: `pdf_minify/ui_qt/app.py`.

## 51 — DONE
~~WHen I open a new file, the right preview is the last to be updated, it
should be always the first filter to be processed, ahead of all other
priorities.  First open, it would be the first priority filter, but after, it
would be whatever filter the user has selected, right?~~
Stub: the active filter is always processed first.
See: `pdf_minify/ui_qt/jobs.py`.

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
Stub: the pane headers show size and percentage; the name is in the File box.
See: `pdf_minify/ui_qt/app.py`.

## 87 — DONE
~~remove the file name from the left side top title.  Also, remove the bold
from both.~~
Stub: the file name appears only in the File box.
See: `pdf_minify/ui_qt/app.py`.

## 61 — DONE
~~Also, in the thumnails and top lines, shows the size percentage, like
original 230kb 100%, filter 1, 23kb 10%.~~
Stub: every size shows its percentage of the original, rounded to nearest.
See: `pdf_minify/ui_qt/app.py`.

## 90 — DONE
~~Also, when I choose a to be processed filter to the far right, when other
fitlers are processed to the left, reprocessing starts onthe left filters,
this is also incorrect. [...]~~
Stub: minis belong to the file and never re-run on clicks; `issues.md` lists complaints until the designer confirms each fix.
See: `docs/FILTER_LIFECYCLE.md`, `issues.md`.

## 91 — DONE
~~Also, the app should remember the last opened file.~~
Stub: the last opened file is remembered and reopened on a bare launch.
See: `docs/PERSISTENCE_AND_TEMP.md`.

## 89 — DONE
~~Why do the per filter progress bars always seem to start at 50%?  This is
also incorrect please fix.~~
Stub: each mini's progress bar advances with its own work.
See: `pdf_minify/ui_qt/jobs.py`.

## 62 — DONE (standing rule)
~~run, always run after a new build, kill the existing one~~
Stub: same standing rule as item 62 above.

## 63 — DONE (wording, superseded by 64)
~~what does <=150dpi mean?  How is that even something that make sense??~~
Stub: superseded by item 64.

## 64 — DONE
~~then you don't need to say max, just the dpi, it's assumed it's a max, write
as a ui design ruling, users don't care to see this difference.~~
Stub: captions show plain DPI values.

## 65 — DONE
~~I just moved the threshold slider and the previous did not update, this is
wrong.  Also, your <1% is wrong, round to the nearest, it's either 1% or
0%.~~
Stub: the Threshold slider is active only for Simple.

## 66 — DONE (Q&A)
~~is there a mode that can reduce the color pallette for compression?  And what
are the best algorithms for this?~~
Stub: answered: palette quantizers were ranked, and the indexed path never dithers.

## 67 — DONE
~~I mean to force a reduction of the pallette [...] Add a few example filters
please.  Review the filter examples across the corpus [...]~~
Stub: same as item 67 above.

## 68 — DONE
~~File name should be the firlst list of the right side block.  Original and
size stays above the first previous main window~~
Stub: the file name heads the right panel.

## 69 — DONE
~~number of pages in the right hand box, things that are constant for
original and any filter stay in the right hand box, as the main info box~~
Stub: the File box shows the name, pages and original size.

## 70 — DONE (Q&A)
~~Also, I have told you many times, the prev/next does nothing.  What is it
supposed to do?  Seems useless to me.~~
Stub: answered: they were page steppers, removed under item 71.

## 71 — DONE
~~drop prev/next, we have scroll bars for that.   Add zoom in/out buttons in
the right hand side panel.~~
Stub: the Prev/Next buttons were removed and zoom buttons added.

## 72 — DONE
~~I choose jpeg2000 filters and the codec is not shown on the right side, why
the fail??~~ (+ same for JPG)
Stub: Filter details opens with a `Codec:` line.

## 73 — DONE
~~page size never changes, so put that in the top block call file info.   The
final name should have it's full path also.~~
Stub: the File box shows the full path, pages, page size and original size.

## 74 — DONE
~~The filter should not generally have a page size [...] What do you
suggest?~~
Stub: the original page size is the default; Letter and A4 are options.

## 75 — DONE (restyled under 76/78)
~~those are awefull zoom buttons, use proper icons [...]~~
Stub: a first icon-button pass, replaced by items 76 and 78.

## 76 — DONE (restyled under 78)
~~use the magnifying glass zoom in out and buttons should be small and on same
row [...]~~
Stub: a magnifier row, replaced by the item-78 toolbar.

## 77 — DONE
~~also make the tumbnail stip go full width, right side panel stopping above
with it's own scroll bar if overflow.~~
Stub: the strip spans the window width; the right panel scrolls.

## 78 — DONE
~~yes please~~ (toolbar upgrade approval)
Stub: zoom is a joined toolbar pair.

## 79 — DONE
~~why do you have encode and codec on different lines, very incoherent, follow
modern best practices please!~~
Stub: Filter details opens with one `Codec:` line in all modes.

## 80 — DONE
Stub: flat palettes use true Indexed colour spaces sized to their actual entries.
See: `pdf_minify/core/pipeline.py`, `tools/bench_indexed.py`.

## 81 — DONE (policy, verified in code)
~~Everything in this project must be maximum compression, BW lossles, reduced
palette, probably lossless, jpeg full color usually lossy~~
Stub: audited: BW and indexed saves are lossless; only JPEG and JPEG2000 are lossy, as ruled.

## 88 — DONE
~~Also, when you are done your current work, drop the filled-background file
please, it's not usefull.~~
Stub: the removed example was replaced by `form-941-2026.pdf` in scripts and docs.
See: `examples/README.md`.

## 93 — DONE
~~always run normally so that I can test the features like opening the last
opened file please.  So far, that has NOT worked also, add this and my
previous message to the bugs list, maybe we should call it issues.md?~~
Stub: a bare `./run.sh` opens the last file, tests isolate their settings, and `issues.md` replaced the old bug list.
See: `issues.md`, `tests/conftest.py`.

## 94 — DONE
~~I closed the last one while it was processing as a test, this is normal to
write safe code for all scenarios and have test cases for all scenarios,
please make sure you do complete work.~~
Stub: closing the window cancels and joins all workers before closing the document.
See: `pdf_minify/ui_qt/app.py`, issue B26.

## 95 — DONE
~~thumbnails progress bar always starts a 50% and stays there until real
processing starts, this is incorrect. please fix and add to issues.~~
Stub: progress bars are cost-weighted, start at 0 and rise with real completions.
See: `pdf_minify/ui_qt/app.py`, issue B27.

## 96 — DONE
~~The preview thumnail section below should always be full heigh, no vertical
scroll bar. [...] put the save and X button on the same line as zoom [...]~~
Stub: the strip is one full row with horizontal scrolling, and progress overlays the mini.
See: `docs/UI_LAYOUT.md`.

## 97 — DONE
~~why is there still a bar under the thumbnail when it is selected, but not
when the window is out of focus, is that a standard part of the widgets?  I
asked to remove the "blue bar", not just the "blue".~~
Stub: the strip takes no keyboard focus, so Qt's focus frame is gone.
See: `pdf_minify/ui_qt/app.py`.

## 98 — DONE
~~The whole thumbnail is already highlighted when selected, the bar below it
is redundant [...] follow modern best practices if there is a specific
reason for ti.~~
Stub: the selected mini is visibly marked; item 134 gives the current full wash.
See: `pdf_minify/ui_qt/app.py`.

## 100 — DONE
~~Also, add a checkbox for lossless. [...] it should always be show for each
filter type on the right side.~~
Stub: a Lossless checkbox is editable only for JPEG2000 and shows the fixed state elsewhere.
See: `pdf_minify/ui_qt/app.py`.

## 101 — DONE
~~Also, when I zoom out [...] the right preview side does not follow in
sync. [...] zoom resets [...] some processing [...] zoom should never reset
unless I press a zoom reset button. Add these as two new issues please~~
Stub: the preview mirrors the baseline grid exactly, so switching filters never moves the view.
See: `pdf_minify/ui_qt/viewer.py`, issues B33/B34.

## 102 — DONE
~~'PySide6.QtGui.QPalette' object has no attribute 'Mid', BUT you should see
this in the log automatically, no?  This was in a popup.~~
Stub: file-open errors are logged with their traceback before any popup.
See: `pdf_minify/ui_qt/app.py`, issue B35.

## 103 — DONE
~~force full page raste should be per filter option [...] Normally, we don't
want to raster the text, only copress the images. Also, [...] no recacls
[...]~~
Stub: per-filter force-raster flags were added; items 126/127 define the current FFPR behaviour.

## 104 — DONE
~~Also, another issue, no horizontal divider between original and right side
preview, they must always have exact same size.  Also, I already told you to
always stop and relauch the app after you make changes, why do I have to
repeat??~~
Stub: a visible divider kept the panes equal; replaced by item 107.

## 105 — DONE
~~when I check/uncheck the force raster, it changes all the BW thumbnails,
this is wrong!~~
Stub: minis show each filter's saved recipe, never the live checkbox.
See: issues B39/B41.

## 106 — DONE
~~It still changes the size of all the thumbnail previews, you clearly don't
have clear app architecture, please improve and fix!~~
Stub: minis and amounts never blank during recomputes; only a new file clears them.
See: `docs/DESIGN.md`.

## 107 — DONE
~~Remove the vertical sizer between the two main previews, not just make it
not draggable, that is just wrong.~~
Stub: the panes sit in a fixed equal layout instead of a splitter.
See: `pdf_minify/ui_qt/app.py`, issue B43.

## 108 — DONE
~~also, why when I click on a mini, the filter seems to be recomputed, that
is wrong, read my design rulings.~~
Stub: panes skip rebuilding when they already show the result, removing the flicker.
See: `pdf_minify/ui_qt/app.py`, issue B44.

## 109 — DONE
~~Also, have a button that permits naming/renaming the filter, and a popup
for that.  Also have a copy button that shows the same naming popup, but
used for the copy.~~
Stub: Rename… and Copy… create named custom filters that persist.
See: `pdf_minify/ui_qt/app.py`.

## 110 — DONE
~~Also, when you are done, give me some text, descriptions and tags to put in
github project.  Also, make sure the readme makes the project findable and
well explained.~~
Stub: `docs/GITHUB.md` holds the repository description and topics, and the README was rewritten.
See: `docs/GITHUB.md`, `README.md`.

## 111 — DONE
~~Big Preview right side is stil not working!!  Why are you failing so much?~~
Stub: the right pane shows the baseline until the filter preview arrives.
See: `pdf_minify/ui_qt/app.py`.

## 112 — DONE
~~I need a save filter changes button also after the rename and copy, or
before.  Also, put the filter name and these buttons on the same line,
resizing the dropdown to fill the space.~~
Stub: Save writes the edited settings into the filter.
See: `pdf_minify/ui_qt/app.py`.

## 113 — DONE
~~It still doesn't work, I choose a BW mini and the big upper right preview
is wrong! [...]~~
Stub: the right pane always shows the full filter effect.
See: `pdf_minify/ui_qt/jobs.py`.

## 114 — DONE
~~And put the proper icons on the save, rename, duplicate buttons.~~
Stub: Rename, Copy and Save show standard icons beside their words.
See: `pdf_minify/ui_qt/app.py`.

## 116 — DONE
~~again, when I change full page raster, many filters get updated, this is
wrong and I have said this many times!~~
Stub: each filter's amount follows its own recipe, so toggling the checkbox starts no jobs.
See: `pdf_minify/ui_qt/app.py`.

## 117 — DONE
~~and the panel width slider is completely wrong, the divider should be
adjustable, like the previous preview divider.~~
Stub: a draggable splitter separates the previews from the right panel; the two panes stay equal.
See: `pdf_minify/ui_qt/app.py`.

## 118 — DONE
~~If the right panel becomes too small for it's content, it must have a
horizontal scroll bar~~
Stub: the right panel scrolls instead of clipping when narrowed.
See: `pdf_minify/ui_qt/app.py`.

## 120 — DONE
~~isn't there a standard rename icon that looks like a cursor with a letter
or two? Also, remove the text on the filter buttons, rename, copy, save,
and just keep the icon and tooltips.~~
Stub: filter buttons are icon-only with tooltips, using theme icons and the Breeze fallback.
See: `docs/ICONS.md`, `pdf_minify/ui_qt/icons.py`, issue B102.

## 121 — DONE (analysis delivered; later rulings §§126/127/149 settle the flow)
Stub: the analysis was delivered; §§122/127/149 settle the flow.
See: `docs/FILTER_LIFECYCLE.md`.

## 122 — DONE (implemented; awaiting designer confirmation)
Stub: the single real-file flow is implemented: one saver writes the PDF that the preview, minis, size and export all read.
See: `docs/ARCHITECTURE.md`, `docs/FILTER_LIFECYCLE.md`, issue B53 (OPEN).

## 123 — DONE
Stub: app scratch files live in the OS temp folder.
See: `pdf_minify/ui_qt/paths.py`, `docs/PERSISTENCE_AND_TEMP.md`.

## 124 — DONE
Stub: pane headers elide to the available width, with the full text on hover.
See: `pdf_minify/ui_qt/app.py`.

## 125 — DONE
Stub: `docs/UI_LAYOUT.md` holds the layout rules.
See: `docs/UI_LAYOUT.md`.

## 126 — DONE
Stub: the unspecified mixed path was removed and the proposal parked.
See: `docs/MIXED_MODE_OPTION.md`.

## 127 — DONE (FFPR restored with defined OFF semantics)
Stub: FFPR is restored: on flattens the page; off keeps text native and optimizes the images.
See: `docs/COMPRESSION.md`.

## 128 — DONE
Stub: minis reorder by drag and drop; the dropdown and processing follow the strip order, and controls sit inline with their labels.
See: `docs/UI_LAYOUT.md`.

## 129 — DONE
Stub: every save resizes images to the exact DPI in one Lanczos step.
See: `docs/COMPRESSION.md`.

## 130 — DONE
Stub: dropdowns fit their longest item, and issues are listed on their topic pages.
See: `docs/UI_LAYOUT.md`.

## 131 — DONE (click churn was the shared-DPI estimate key)
Stub: each filter's amount uses its own DPI, so clicking a mini recomputes only the preview.
See: `pdf_minify/ui_qt/app.py`.

## 133 — DONE
Stub: filters are numbered from the live strip order in the minis and the dropdown.
See: `docs/UI_LAYOUT.md`.

## 134 — DONE
Stub: the selected mini gets a full theme wash with readable captions and no extra chrome.
See: `docs/UI_LAYOUT.md`.

## 137 — DONE
Stub: the screenshot rule is in the developer guidelines.
See: `docs/DEVELOPER_GUIDELINES.md` (§5b).

## 139 — DONE
Stub: the highlight was approved, `./test.sh` runs every test automatically, and a solid drop bar marks the nearest gap.
See: `docs/UI_LAYOUT.md`, `test.sh`.

## 140 — DONE
Stub: Original is not in the filter dropdown; the left pane always shows it.
See: `docs/UI_LAYOUT.md`.

## 141 — SUPERSEDED BY §142
Drag ghost transparency corrected after the native implementation failed
on the live non-composited X11 desktop. The rejected checkerboard fallback
(alternating fully clear/opaque pixels) is gone. One opaque mini canvas is
software-blended at 65% inside the strip viewport, so its background,
thumbnail, and every caption glyph share the exact same opacity. Qt's
native drag window is suppressed; model mime, insertion bar, and drop path
remain unchanged. Pinned by uniform-alpha and live-composite render tests.
See: `pdf_minify/ui_qt/app.py` (`_StripList.paintEvent`).

## 142 — DONE — DESIGNER CONFIRMED (2026-10-13, §147)
Stub: the drag ghost is the complete selected mini.
See: `docs/UI_LAYOUT.md`.

## 143 — DONE — DESIGNER CONFIRMED (2026-10-13, §§144/147)
Stub: real drags no longer reduce the ghost to a blue rectangle.
See: `docs/UI_LAYOUT.md`.

## 144 — DONE (ghost DESIGNER CONFIRMED 2026-10-13; drop behavior unconfirmed)
~~The DnD is good, but a little light, try 65%? Or what is modern best practices for transparency in modern GUI?  Also, let the DnD go outside of the mini strip, same transparency, but snap the drop to the nearest vertical drop point regardless of where it is vertically.~~
Stub: the ghost moves across the whole window, and pointer X alone picks the nearest insertion divider.
See: `docs/UI_LAYOUT.md`, `tools/drag_smoke.py`, issue B71.

## 145 — DONE — DESIGNER CONFIRMED (2026-10-13, §147)
~~There is a weird transparent white bar across the bottom of the ghost, it comes from behind the bottom scrollbar I think.  The previous worker had alot of trouble with a similar blue selection bar below it before and a vertical scrollbar that was incorrect.  I think the previous worker did alot of hacks and did not follow modern best practices for QT and GUI, please review to solve the root causes, and not just patch onto of bad code and bad design.  You can review the docs, my rulings, issues, etc for more context.~~
Stub: the strip cell fits its row with no hidden vertical range, and one delegate paints both cells and the ghost.
See: `docs/UI_LAYOUT.md`.

## 146 — DONE — DESIGNER CONFIRMED (2026-10-13, §147)
~~Also, change the transparency to 75% for the DnD ghost please.~~
Stub: the whole ghost has a uniform 75% opacity.
See: `docs/UI_LAYOUT.md`.

## 147 — DONE
~~Ok, this is good, you can mark these issues fixed, confirmed by me.  I don't know if the worker was self-marking issues fixed without my confirmation, but try to have a marking that indicates that I explicitly confirmed it fixed and the date.  There are still other DnD issues, so mark this ghost as fixed.   Is transparency at 75% now also?~~
Stub: ghost issues B68/B69/B70/B72 are marked DESIGNER CONFIRMED on 2026-10-13, and canon separates implementation from designer acceptance.
See: `issues.md`, `docs/DEVELOPER_GUIDELINES.md`.

## 148 — DONE — DESIGNER CONFIRMED (2026-10-13, §149)
~~When I DnD a mini, the dropped numbers don't renumber immediately, only if there is some reprocessing or miss processing that gets triggered, this is wrong and bad design, please review for the root cause and fix the design properly.~~
Stub: caption numbers are drawn from the live row at paint time, never baked into cached icons.
See: `docs/UI_LAYOUT.md`, `tests/test_minis.py`, issue B73.

## 149 — DONE — DESIGNER CONFIRMED (2026-10-13)
~~Ok, this renumbering issue seems resolved, you can document my explicit confirmation.~~
Stub: the designer's acceptance of B73 is recorded with its date.
See: `docs/DESIGNER_VERBATIM.md` §149, issue B73.

## 150 — DONE (designer §149; awaiting designer confirmation)
~~All filters must run the real saver, once per input/effective filter spec. Preview, minis, exact full-document byte size, and exported PDF must consume that same completed filtered file. Selecting an unvisited mini, zoom/pan, page changes, or DnD reorder must not rerun filtering. Remove split preview, mini, and estimator paths rather than hide their processing messages.~~
Stub: one saver produces each filter's real PDF; view and order changes start no jobs, and Export copies the same bytes.
See: `docs/FILTER_LIFECYCLE.md`, issues B74/B75.

## 151 — DONE (designer §149; awaiting designer confirmation)
~~Separate saved recipes/artifacts from debounced live drafts. Mark changed filters with *; process only the edited filter after debounce. Reverting to the saved recipe clears dirty state and reuses its kept artifact. Programmatic control loading must not count as an edit or trigger processing.~~
Stub: saved and draft recipes are separate, with one debounce and a dirty marker.
See: `docs/FILTER_LIFECYCLE.md`, issue B76.

## 152 — DONE (designer §149; awaiting designer confirmation)
~~Before leaving an unsaved filter, offer Save / Save As… / Discard / Cancel. Discard keeps the saved artifact and removes the draft; Save promotes the draft and removes the obsolete saved artifact; Save As… creates a named filter and retains both results. Cancellation leaves selection/draft intact. Respect shared references and in-flight workers when retiring temp artifacts.~~
Stub: leaving a dirty filter offers Save, Save As, Discard or Cancel, each keeping the right files.
See: `docs/FILTER_LIFECYCLE.md`, `docs/PERSISTENCE_AND_TEMP.md`, issue B77.

## 153 — DONE (designer §150: related-canon audit)
~~review and collect all my similar design ruling that covers this and compile into the correct documents and review for and contradictions and incoherences.  I had to repeat this and related designs many times and the weak worker was still failing, so I expect other problems also.~~
Stub: the related rulings are indexed in the lifecycle page, and the topic pages agree with it.
See: `docs/FILTER_LIFECYCLE.md`.

## 154 — DONE (designer §151: recorded temp location)
~~where are the temp files stored?  I previously ruled, but I am double-checking to see what the prior weak worker recorded.~~
Stub: runtime filtered PDFs live in the OS temp folder; the repository `.tmp/` holds developer artifacts only.
See: `docs/PERSISTENCE_AND_TEMP.md`.

## 155 — DONE (canon audit §150; awaiting designer confirmation)
~~Fix B78: startup sweeper removes fresh empty directories belonging to another running app. Protect process-owned artifacts with a held Qt process lock; skip live processes and fresh empty directories. Test simultaneous processes, expired unlocked data, and worker completion/cleanup.~~
Stub: a locked PID folder protects generated files until all work finishes, and normal exit removes it.
See: `docs/PERSISTENCE_AND_TEMP.md`, issue B78.

## 156 — DONE (canon audit §150; awaiting designer confirmation)
~~Fix B79: automatic compression can wrap already encoded JPEG/JPX/JBIG2/Flate streams, while explicit Filter metadata describes the unwrapped codec. Disable automatic compression for pre-encoded payloads and test actual decoded images/pixels in the saved PDF. Reject corrupt readback rather than displaying blank imagery and calling it a valid preview.~~
Stub: pre-encoded images are written as-is under their filter, and Zopfli output is validated zlib data.
See: `docs/COMPRESSION.md`, issue B79.

## 157 — DONE (designer §152: PID-owned temp directory)
~~So the temp dir should be in a dir with the process id number?  Is this possible?~~
Stub: runtime files live under `<os-temp>/pdf-minify/saves/<GUI-PID>/`.
See: `docs/PERSISTENCE_AND_TEMP.md`, issue B78.

## 158 — DONE (designer §153: remove unrequested session layer)
~~Why keep all sessions?  That is not what I asked for, also, two live applications cannot share a PID, or yes?  Why did you invent something beyond my request and design ruling?~~
Stub: one GUI process owns one PID folder, with no extra session layer.
See: `docs/PERSISTENCE_AND_TEMP.md`.

## 159 — DONE (designer §154: stable identity; refined by §155)
~~how do you identify the unique filter name, if the number prefix can change, you use the core name?  Ref: /tmp/pdf-minimalist/saves/<PID>/filter-…/filtered.pdf~~
Stub: filters have a persistent internal UUID; names and numbers are presentation only.
See: `docs/FILTER_LIFECYCLE.md`, `docs/PERSISTENCE_AND_TEMP.md`.

## 160 — DONE (designer §155; awaiting designer confirmation)
~~you should give the filter a UUID and never permit two filters to have the same UUID, check when loading, in case someone copy/paste filters.  These UUIDs are only for internal use, name tis dirs with the UUID.  I think this is modern best practices, no?  Python has UUID generation, not tied to the network card?  Or just make a random UUID generator, if python does not have.~~
Stub: each filter has a unique random UUID that loading repairs and Save As renews; its files live under that UUID.
See: `docs/PERSISTENCE_AND_TEMP.md`, issue B80.

## 161 — DONE — DESIGNER CONFIRMED (2026-10-14, §159)
~~New issue, everytime I click on the minis, after reordering them, the last ones seems to flicker old names, for the current layout, the flicker of other wrong layout names starts as of filter number 5.  Regardless, this is another clear spaghetti code symptom from the weak worker.  Please review carefully and fix the code to address the root cause in the code please!~~
Stub: a reorder moves exactly one row by UUID, so names never mix up after a drag.
See: `docs/UI_LAYOUT.md`, issue B81.

## 163 — DONE (designer §159: confirm reordered-name fix)
~~Ok, seems good, you can mark this as fixed.~~
Stub: B81 is marked FIXED — DESIGNER CONFIRMED — 2026-10-14.
See: `issues.md`.

## 164 — DONE (designer §159: equal top and bottom mini gaps)
~~Your previous fix to the mini hightlight and vertical scroll added back the white space gap at the bottom of the minis strip.  I want the same gap as at the top of the minis.~~
Stub: the mini cell has equal 4px top and bottom padding.
See: `docs/UI_LAYOUT.md`, issue B82.

## 165 — DONE (designer §159: darker mini background)
~~Also, the background of the minis should be a bit darker so that I can see the difference between the white mini page outline and the background.~~
Stub: the strip background is a slightly darker theme Window colour.
See: `docs/UI_LAYOUT.md`, issue B83.

## 166 — DONE (designer §160: Discard Changes button wording)
~~Change "Close without saving" to "Discard Changes"~~
Stub: the Discard button reads "Discard Changes".
See: `docs/FILTER_LIFECYCLE.md`, issue B84.

## 167 — DONE (designer §161: canceled mini switch stays edited)
~~Also, after clicking another filter in the minis, if I escape the "Unsaved filter changes", the filter selection changed, but nothing was saved, nor discarded, this is wrong.  Cancel should remain on the edited fiter.~~
Stub: cancelling a mini switch keeps the current filter selected and edited.
See: `docs/FILTER_LIFECYCLE.md`, issue B85.

## 168 — DONE (designer §162: revert changes icon)
~~Also, add a revert changes igon beside the dropdown, the typical counter-clockwise arrow, right?~~
Stub: a Revert Changes button beside the dropdown restores the saved filter.
See: `docs/UI_LAYOUT.md`, issue B86.

## 170 — DONE (designer §164: center actual pages on zoom-out)
~~Center actual one/two/multi-page groups on zoom-out, retaining row-major autowrap.~~
Stub: zoom-out centres the actual pages.
See: `docs/UI_LAYOUT.md`, issue B87.

## 171 — DONE (designer §165: preview/original centering discrepancy)
~~Also, oddly, the preview seems to center correctly, but not the original.~~
Stub: the original, preview and minis share one grid, so their centring matches.
See: `docs/UI_LAYOUT.md`, issue B87.

## 172 — DONE — DESIGNER CONFIRMED — 2026-10-14 (designer §§166/167: slow resize/layout feedback)
~~Fix repeated divider adjustments for several seconds after shrinking a wide window.~~
Stub: resizing no longer triggers delayed header-driven layout changes.
See: `docs/UI_LAYOUT.md`, issue B88.

## 173 — DONE — DESIGNER CONFIRMED — 2026-10-14 (designer §167: record resize fix confirmation)
~~Ok, this is confirmed fixed, thank you.~~
Stub: B88 is marked FIXED — DESIGNER CONFIRMED — 2026-10-14.
See: issue B88.

## 174 — DONE (implementation; designer acceptance pending)
~~BW image-layer composition and actual saved-file benchmarking (§168).~~
Stub: FFPR off keeps native text and vectors over one combined image canvas.
See: `docs/COMPRESSION.md`, issue B89.

## 175 — DONE (implementation; designer acceptance pending)
~~Fix FFPR multi-page image aliasing found during the §168 audit.~~
Stub: each page places its own encoded image.
See: `docs/COMPRESSION.md`, issue B90.

## 176 — DONE (implementation; designer acceptance pending)
~~Keep original native text, without invented glyph masks (§169).~~
Stub: native text operators, fonts and geometry are kept, including clip-only text.
See: `docs/COMPRESSION.md`, issue B89.

## 177 — DONE (implementation; designer acceptance pending)
~~Retain vector diagrams and document PDF text/vector compression (§170).~~
Stub: native vectors are kept and compressed losslessly by the shared saver.
See: `docs/COMPRESSION.md`, issue B89.

## 178 — DONE (implementation; designer acceptance pending)
~~Simplify to one BW image canvas with native overlays (§171).~~
Stub: images combine on one canvas above the page backdrop and below native artwork.
See: `docs/COMPRESSION.md`, issue B89.

## 179 — DONE (implementation; designer acceptance pending)
~~Exact original/filter display with no extra bitmap smoothing (§§172/173).~~
Stub: display turns off decoder averaging, interpolation and anti-aliasing.
See: `docs/UI_LAYOUT.md`, `tests/test_exact_display.py`, issue B91.

## 180 — DONE (implementation; designer acceptance pending)
~~Disable all PDF-content AA and show native precision on zoom (§§174/175).~~
Stub: both panes redraw the actual PDF on the device pixel grid.
See: `docs/UI_LAYOUT.md`, issue B91.

## 181 — DONE (designer §176: platform certificate and packaging documentation)
~~Document the certified current platform and multi-platform packaging.~~
Stub: `docs/PLATFORMS.md` certifies the Debian 13 source runtime, and `docs/PACKAGING.md` plans the other platforms.
See: `docs/PLATFORMS.md`, `docs/PACKAGING.md`.

## 182 — DONE (diagnosis requested in designer §177)
~~Explain the added dark border around color images.~~
Stub: the dark image-edge halo was diagnosed: black colour under transparent pixels bled in during resizing.
See: `docs/COMPRESSION.md`, issue B92.

## 183 — DONE (designer §178: editable numbers/spinners beside sliders)
~~Pair Threshold/Colors sliders with editable numbers and native spin arrows.~~
Stub: each slider has a linked number box with step arrows.
See: `docs/UI_LAYOUT.md`.

## 184 — DONE (designer §§179/180/182: composite first, then one DPI resize)
~~Fix B92 using full-color composition before one DPI resize and filtering.~~
Stub: images are composed in full colour, resized once, then transformed.
See: `docs/COMPRESSION.md`, issue B92.

## 185 — DONE (designer §§181/182: artwork type and resize/filter order)
~~Explain the Firefox representation and choose the scale/filter order.~~
Stub: answered: Firefox artwork is a bitmap with an opacity mask; processing composes first, resizes once, then filters.
See: `docs/COMPRESSION.md`.

## 186 — DONE — DESIGNER CONFIRMED 2026-10-14 (designer §§183/184)
~~Repair low-color artwork mapped to white instead of its closest color.~~
Stub: palette reduction fits representative colours and gives each pixel its exact nearest colour.
See: `docs/COMPRESSION.md`, issue B93.

## 187 — DONE (designer §183: one global filter-edit debounce)
~~Unify every filter control under one trailing debounce and recommend a time.~~
Stub: one 300 ms debounce governs all filter edits.
See: `docs/FILTER_LIFECYCLE.md`, issue B94.

## 188 — DONE (designer §184: palette confirmation and root-cause explanation)
~~Record explicit confirmation and explain the palette defect.~~
Stub: B93 records the designer's acceptance, with the palette root cause explained.
See: `docs/COMPRESSION.md`, issue B93.

## 189 — DONE (designer §185: native full-width mini progress overlays)
~~Match the default progress style, span the full reserved mini width and
provide an opaque white backing.~~
Stub: a native progress bar overlays each mini during work and disappears on completion.
See: `docs/UI_LAYOUT.md`, issue B95.

## 190 — DONE (designer §187: progress overlay inset leaves highlight visible)
~~Inset the progress bar and backing by the shared mini padding.~~
Stub: the progress overlay leaves the selected highlight visible at the cell sides.
See: `docs/UI_LAYOUT.md`, issue B95.

## 191 — DONE (designer §188: title-free strip and one main-region spacing policy)
~~Remove the minis title and unify all main-region outer insets/gutters.~~
Stub: the strip has no title row, and the main regions share one 4px spacing.
See: `docs/UI_LAYOUT.md`, issue B96.

## 192 — DONE (designer §189: Save As selects the newly created filter)
~~Select the new Save As copy and audit equivalent dirty-resolution paths.~~
Stub: Save As selects the newly created filter.
See: `docs/FILTER_LIFECYCLE.md`, issue B97.

## 193 — DONE (designer §190: 50% taller mini bars and percentage text, no white padding)
~~Enlarge native mini bars and percentages by 50%; remove extra white padding.~~
Stub: the mini progress bars and text were enlarged; item 202 sets the final size.
See: `docs/UI_LAYOUT.md`, issue B95.

## 194 — DONE (designer §191: center progress within the entire mini cell)
~~Center progress vertically in the whole mini frame, not just its page image.~~
Stub: progress is centred in the whole mini cell.
See: `docs/UI_LAYOUT.md`, `tests/test_minis.py`, issue B95.

## 195 — DONE (designer §192: explicit acceptance of mini progress appearance)
~~Record the designer's confirmation of the completed mini progress changes.~~
Stub: B95 is marked FIXED — DESIGNER CONFIRMED — 2026-10-14, scoped to the mini progress appearance.
See: issue B95.

## 196 — DONE (designer §192: configuration heading matches the preview blocks)
~~Add a Configuration heading above the right panel, matching the previews.~~
Stub: the configuration panel header matches the preview headers.
See: `docs/UI_LAYOUT.md`, issue B98.

## 197 — DONE (designer §192: low-color palette as colored JBIG2 stencils)
~~Design and benchmark one colored lossless JBIG2 stencil per non-white color.~~
Stub: a layered colored-JBIG2 prototype was built from the shared composition and palette map.
See: `docs/JBIG2.md`, issues B99/B100.

## 198 — DONE (designer §193: layered-JBIG2 design and benchmarks first)
~~Create and cross-reference the layered-JBIG2 developer design/benchmark document.~~
Stub: the colored-JBIG2 representation is documented with JBIG2 BW.
See: `docs/JBIG2.md`.

## 199 — DONE (designer §195: remove redundant working labels)
~~Remove the redundant mini working placeholders; progress already shows activity.~~
Stub: the "working…" labels are gone; missing results stay blank and completed ones stay visible.
See: `docs/UI_LAYOUT.md`, issue B101.

## 200 — DONE (designer §196: establish icon provenance)
~~Check whether the odd revert/rename icons are standard KDE/Nuvola assets.~~
Stub: reported: both icons were custom drawings; item 201 replaces them.

## 201 — DONE (designer §197: consistent native-theme icons with a standard fallback)
~~Use consistent desktop-theme icons and one standard portable fallback set.~~
Stub: icons come from the desktop theme with a bundled Breeze fallback, with provenance and licences recorded.
See: `docs/ICONS.md`, `pdf_minify/ui_qt/icons.py`, issue B102.

## 202 — DONE (designer §§198/199: mini progress enlargement is 25%, not 50%)
~~Use 25%-larger mini bars, instead of the previous 50% enlargement.~~
Stub: mini progress bars and their percentage text are 25% larger than the default bar.
See: `docs/UI_LAYOUT.md`, issue B103.

## 203 — DONE (designer §200: coded icon lab, including Nuvola and Oxygen)
~~Add an Icon Lab window with stock-library options and shareable choice codes.~~
Stub: View → Icon Lab… compares coded icon sets without changing the app.
See: `docs/ICON_LAB.md`, issues B102/B104.

## 206 — DONE (designer §203: editable compression and precise threshold label)
~~Expose six editable image codecs and qualify the threshold-method control.~~
Stub: Image compression is an editable choice of six codecs, never silently substituted, with a precise Threshold method label.
See: `docs/COMPRESSION.md`, `docs/TEST_PLAN.md`, issues B99/B100/B105.

## 207 — DONE (designer §204: distinguish native-stream and image compression)
~~Explain native text/vector/font compression independently of image encoding.~~
Stub: image compression never disables native-stream optimization; item 208 adds the stream selector.
See: `docs/COMPRESSION.md`, `docs/NATIVE_STREAM_COMPRESSION.md`.

## 208 — DONE (designer §205: native-stream selection and benchmark document)
~~Add independent native-stream compression and benchmark sizes/times/support.~~
Stub: a PDF streams selector was added, with its design and reader limits documented.
See: `docs/NATIVE_STREAM_COMPRESSION.md`, issue B106.

## 211 — DONE (designer §208: applicability and scope of Brotli image comparison)
~~Explain existing Brotli measurements versus indexed color and BW/JBIG2.~~
Stub: answered: the Brotli study compressed native streams only, so it ranks no image codec.

## 212 — DONE (designer §209: size-only bitmap compression benchmarks)
~~Benchmark equal-pixel Indexed/BW Flate, full Zopfli and Brotli versus BW/colored JBIG2.~~
Stub: a size-only equal-pixel bitmap study was run; the integrated benchmarks now cover these comparisons.
See: `docs/COMPRESSION_BENCHMARKS.md`.

## 213 — DONE (designer §210: explain useful compression pairings and FFPR scope)
~~Distinguish valid mixed PDF codecs from useful UI combinations and FFPR overhead.~~
Stub: answered: native Brotli with Flate images is valid PDF; a shared general compressor would be a product simplification.

## 214 — DONE (designer §211: combinations table first, then UI alternatives)
~~Document reasonable combinations and compare a combined menu with separate controls.~~
Stub: the combinations table and a separate-controls recommendation were delivered.

## 215 — DONE (designer §212: assess scope and duplication of the combination table)
~~Review the table against repository document types and the available benchmarks.~~
Stub: answered: the combinations table's scope and duplication were assessed.

## 216 — DONE (designer §213: verify Zopfli support and record opinionated best-encoding policy)
~~Confirm unchanged Flate decoder support and supersede speed-based product choices.~~
Stub: Zopfli output was confirmed readable by any Flate decoder, and the best-encoding policy was recorded.
See: `docs/COMPRESSION.md`, TODO §217.

## 217 — OPEN (designer §213: align runtime with best encoding and decoder-support choices)
§§255–257 add full-encoder Best for native AND eligible packed-image streams,
make it the app default and migrate existing app filters once. That path has
no historical Zopfli performance cutoff. Remaining legacy paths still expose
ordinary Flate and Zopfli separately, retain a headless zlib fallback and have
an Indexed Zopfli performance cutoff. Align those remaining paths with §213:
one optimized Flate output format
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
Stub: the TODO log lives in `docs/TODO.md`.

## 222 — DONE (designer §219: separate PNG prediction from the main size analysis)
~~Move the paired +PNG comparison into its own document and explain the expected size overhead.~~
Stub: superseded by item 223.

## 223 — DONE (designer §220: restore paired benchmark columns and remove editorial corrections)
~~Keep the +PNG results in the main tables and remove typo-correction discussions from the docs.~~
Stub: the paired plain and +PNG columns were restored and the editorial corrections removed.

## 224 — DONE (designer §221: bold the smallest size in every benchmark row)
~~Highlight the best result in each main bitmap benchmark row using Markdown bold.~~
Stub: the smallest size in each benchmark row is bold.
See: `docs/COMPRESSION_BENCHMARKS.md`.

## 225 — DONE (designer §222: integrated complete-file compression matrix)
~~Measure image/predictor × native policies as actual final PDFs in one primary size matrix.~~
Stub: an integrated benchmark measured complete PDFs across all combinations.
See: `docs/COMPRESSION_BENCHMARKS.md`, `tools/bench_integrated_compression.py`.

## 226 — DONE (designer §223: representative, realistic integrated size tables)
~~Publish realistic combination rows over five representative complete PDFs,
with focused scenarios and actual final-file bytes.~~
Stub: the integrated benchmark uses realistic combination rows over representative complete PDFs.
See: `docs/COMPRESSION_BENCHMARKS.md`.

## 227 — DONE (designer §224: repair preparation failures and support color FFPR)
~~Repair the production preparation roots and extend FFPR to every existing
color codec; measure valid complete outputs at 300 DPI.~~
Stub: the preparation failures were repaired (B108–B112), and colour FFPR works with all six codecs.
See: `docs/COMPRESSION.md`, `docs/COMPRESSION_BENCHMARKS.md`.

## 228 — DONE (designer §225: uniform 300 DPI filter defaults and benchmarks)
~~Set every built-in raster default/missing-DPI fallback and all transformed
benchmark cases to 300 DPI, retaining editable DPI and stable identity.~~
Stub: built-in filters and the benchmarks use 300 DPI.
See: `docs/COMPRESSION.md`, `docs/PERSISTENCE_AND_TEMP.md`.

## 229 — DONE (designer §226: migrate all existing saved raster filters to 300 DPI)
~~Migrate every existing saved/custom raster filter to 300 DPI once, retaining
identity, other parameters and subsequent deliberate edits.~~
Stub: saved raster filters were migrated once to 300 DPI.
See: `docs/PERSISTENCE_AND_TEMP.md`.

## 230 — DONE (B111: preserve inherited native text state through image-layer assembly)
~~Retain visible Form text and original native operators without the
sanitizer's deferred `0 Tr` loss; remove only replaced bitmap/backdrop paint.~~
Stub: inherited native text state survives image-layer assembly.
See: `docs/COMPRESSION.md`, issue B111.

## 231 — DONE (B112: retain correct accessibility ownership without original bitmap payloads)
~~Keep structure-tree references attached to actual native page/Form owners
without retaining replaced original bitmap streams.~~
Stub: accessibility structure is kept while replaced image payloads are removed.
See: `docs/COMPRESSION.md`, `docs/ARCHITECTURE.md`, issue B112.

## 232 — DONE (designer §227: group the integrated overview by output type)
~~Group the primary overview as BW, indexed color / low palettes, then full
color, with unresampled references above the groups.~~
Stub: the overview is grouped into reference, BW, indexed and full-colour rows.
See: `docs/COMPRESSION_BENCHMARKS.md`.

## 233 — DONE (designer §228: one continuous overview table with divider rows)
~~Use one continuous overview table with unnumbered title-only divider rows.~~
Stub: the overview is one continuous table with divider rows.
See: `docs/COMPRESSION_BENCHMARKS.md`.

## 234 — DONE (designer §229: benchmark every combination, including no-image no-ops)
~~Remove native-only exclusions; measure every row/input, even when redundant.~~
Stub: every row is measured for every PDF, including image-free no-op cases.
See: `docs/COMPRESSION_BENCHMARKS.md`, issue B113.

## 235 — DONE (designer §230: rename the project to PDF Minify)
~~Rename the product/package and active project references, preserving saved
settings and the designer's separately managed repository rename.~~
Stub: the project is renamed PDF Minify (package `pdf_minify`), and legacy settings are imported once.
See: `docs/DESIGN.md` §230, `docs/PERSISTENCE_AND_TEMP.md`.

## 236 — DONE (designer §231: sixth representative document — NASA Kepler)
~~Add whole-document NASA Kepler as a sixth case, measuring every combination
and retaining the existing five sources and actual results.~~
Stub: NASA Kepler was added as the sixth representative PDF.
See: `docs/COMPRESSION_BENCHMARKS.md`.

## 237 — DONE (designer §232: explicit BW/Otsu heading and concise combination labels)
~~Rename the BW divider to Black and white (BW + Otsu); remove redundant
`; keep native`, since absence of FFPR implies native preservation.~~
Stub: the overview's BW divider reads "BW + Otsu", and redundant label suffixes are gone.
See: `docs/COMPRESSION_BENCHMARKS.md`.

## 238 — DONE (designer §§233/235 / B114: JBIG2 same-DPI end-to-end non-regression)
~~Repair the 300→301→300 preparation error; retain the full eight-page JBIG2
input and require source-pixel/page-geometry equality and complete-file
non-growth through real native/FFPR saves.~~
Stub: the compositor keeps fractional source density, so same-DPI JBIG2 scans keep their exact pixels and do not grow.
See: `docs/JBIG2.md`, issue B114.

## 239 — DONE (designer §233: replace the overview scan with a non-JBIG2 PDF)
~~Replace the main already-JBIG2 scan with whole non-JBIG2 CCITT TM972;
repair the codec inventory and publish actual post-repair measurements.~~
Stub: the overview's BW column uses the non-JBIG2 `scan-naca-tm972.pdf`.
See: `docs/COMPRESSION_BENCHMARKS.md`, issues B114/B115.

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
`COMPRESSION.md` and `COMPRESSION_BENCHMARKS.md`.

## 241 — DONE (designer §§236/237: remove redundant benchmark rows consistently)
~~Remove the eight main Classic-Flate bitmap rows and their equivalents
throughout ALL focused tables; retain the unresampled reference.~~
Stub: the redundant Classic-Flate rows were removed from the overview and every focused table.
See: `docs/COMPRESSION_BENCHMARKS.md`.

## 242 — DONE (designer §§238–240: isolate the measured PNG-prediction effect)
~~Move PNG overview rows into a separate baseline-labeled six-document table;
show measured PNG-PDF bytes plus signed change from measured plain baselines.~~
Stub: PNG prediction has its own effect table against measured baselines.
See: `docs/COMPRESSION_BENCHMARKS.md`.

## 243 — DONE (designer §242: expand PNG prediction combinations)
~~Add 16/64-color native/FFPR PNG pairs with Zopfli-Flate/Brotli across all
six whole PDFs at 300 DPI, with visible measured baselines and signed changes.~~
Stub: PNG prediction coverage was expanded to 16- and 64-colour cases.
See: `docs/COMPRESSION_BENCHMARKS.md`, `tools/bench_png_extension.py`.

## 244 — DONE (designer §242: next one-factor benchmark experiment)
~~Plan and build the next binary/A-B complete-file table with one named
factor, fixed recipes, measured references and signed baseline changes.~~
Stub: a native/residual-stream experiment compared standard Flate with the optimized encoders.
See: `docs/COMPRESSION_BENCHMARKS.md`, `tools/bench_residual_streams.py`.

## 245 — DONE (designer §243: percentage-only PNG effect table)
~~Remove byte counts from the PNG effect table, keeping signed percentages
and measured-baseline comparisons.~~
Stub: the PNG effect table shows percentages only.
See: `docs/COMPRESSION_BENCHMARKS.md`.

## 246 — DONE (designer §244: Brotli annotation and PNG overall-winner analysis)
~~Underline Brotli in the PNG table; audit overall winners and recommend
the next controlled experiment.~~
Stub: Brotli rows are underlined in the PNG table, and the PNG winner analysis was audited.
See: `docs/COMPRESSION_BENCHMARKS.md`, TODO §240.

## 247 — DONE (designer §§245/246: FFPR Zopfli versus Brotli and short labels)
~~Compare FFPR/J* residuals with Brotli baseline and Zopfli treatment;
explain regressions and shorten table labels.~~
Stub: an FFPR experiment compared Zopfli with Brotli, and the tables say Zopfli.
See: `docs/COMPRESSION_BENCHMARKS.md`, `tools/bench_ffpr_compressors.py`.

## 248 — DONE (designer §§247–249: consistent percentage presentation and table order)
~~Use two decimals for percentage differences, leave rounded zeros unbolded,
and place the Brotli comparison immediately after PNG prediction.~~
Stub: percentages use two decimals, rounded zeros are never bold, and the Brotli table follows the PNG table.
See: `docs/COMPRESSION_BENCHMARKS.md`.

## 249 — DONE (designer §250: explicit treatment titles above effect tables)
~~Put concise experimental-treatment titles directly above the PNG and
FFPR Brotli–Zopfli percentage tables, using the approved wording.~~
Stub: both effect tables have the approved titles directly above them.
See: `docs/COMPRESSION_BENCHMARKS.md`.

## 250 — DONE (designer §§251/252: opt-in Brotli compatibility declaration)
~~Default filters and benchmark/tests to no Brotli declaration; add a persisted
**Include Brotli extension declaration (Compatibility)** checkbox visible only
for Brotli.~~
Stub: the Brotli declaration is opt-in metadata, off by default.
See: `docs/COMPRESSION.md`, `docs/NATIVE_STREAM_COMPRESSION.md`.

## 251 — DONE (designer §253: tooltip-only Brotli help and shared convention)
~~Remove inline Brotli help/space and establish a shared native-tooltip convention.~~
Stub: Brotli help is in the tooltip, with keyboard and accessibility equivalents.
See: `docs/TOOLTIPS.md`.

## 252 — DONE (designer §254: refresh measured declaration-OFF tables)
~~Rerun every published Brotli case and replace historical ON table entries with measured default-OFF results.~~
Stub: all Brotli outputs were re-measured without the declaration, and the tables refreshed.
See: `docs/COMPRESSION_BENCHMARKS.md`.

## 253 — DONE (designer §§255/256: Best Zopfli/Brotli stream compression)
~~Add Best (Zopfli/Brotli) for native/packed-image streams, excluding J* payloads,
with actual complete-file selection and the existing filter lifecycle.~~
Stub: Best (Zopfli/Brotli) keeps the smallest complete file per stream, leaving image samples and J* payloads unchanged.
See: `docs/COMPRESSION.md`, `docs/NATIVE_STREAM_COMPRESSION.md`.

## 254 — DONE (designer §257: Best for every app filter)
Stub: every app filter uses Best.
See: `docs/COMPRESSION.md`, `docs/NATIVE_STREAM_COMPRESSION.md`.

## 255 — DONE (designer §258: Best-only integrated overview)
~~Use Best only in the main matrix and move fixed-encoder comparisons to the specialized binary reference.~~
Stub: the main overview uses actual Best saves; the fixed encoders moved to the binary section.
See: `docs/COMPRESSION_BENCHMARKS.md`, `tools/bench_best_overview.py`.

## 256 — DONE (designer §259: visible controls and PNG-prediction decision tree)
~~Show the fixed-size reference without a drawer and lead PNG results with
a measured decision tree by prepared image representation, encoder and content.~~
Stub: the fixed-encoder sizes are always visible, and the PNG section opens with its decision tree.
See: `docs/COMPRESSION_BENCHMARKS.md`.

## 257 — DONE (designer §260: automatic PNG prediction with Best)
~~Jointly select PNG prediction OFF/ON and Zopfli/Brotli; expose explicit
Zopfli Off/On/Best through the existing filter lifecycle.~~
Stub: Best tests PNG prediction off and on, and explicit Zopfli offers Off/On/Best.
See: `docs/COMPRESSION.md`, `pdf_minify/core/predictors.py`, `pdf_minify/core/best_streams.py`.

## 258 — DONE (designer §261: explicit OFF/ON branches in the predictor tree)
~~Show prediction OFF/ON testing in both Best encoder branches.~~
Stub: the decision tree states the off/on prediction test on both Best branches.
See: `docs/COMPRESSION_BENCHMARKS.md`.

## 259 — DONE (familiar q90 JPEG/JPEG2000 starting point)
~~Use the familiar quality parameter and start JPEG/JPEG2000 at q90.~~
Stub: a Quality control for JPEG and JPEG2000 was added, first seeded at q90 (now q75, item 260).
See: `docs/LOSSY_IMAGE_QUALITY.md`.

## 260 — DONE (q75 defaults and comparable lossy settings research)
~~Set both lossy codecs to q75 and research comparable encoder settings.~~
Stub: Quality defaults to 75, and comparable lossy settings were researched.
See: `docs/LOSSY_IMAGE_QUALITY.md`.

## 261 — DONE (configured lossy profiles and q75 comparison)
~~Fix internal lossy profiles and benchmark comparable q75 outputs now.~~
Stub: JPEG uses 4:4:4 and JPEG2000 a fixed lossy profile, both measured at q75.
See: `docs/LOSSY_IMAGE_QUALITY.md`, `docs/COMPRESSION_BENCHMARKS.md`.

## 262 — DONE (study-based JPEG2000 quality matching)
~~Use the approved conditional JPEG/JPEG2000 quality comparison instead of
the fixed 101-q mapping; update actual complete-file measurements.~~
Stub: a study-based JPEG2000 quality mapping was tried; item 266 replaces it.
See: `docs/LOSSY_IMAGE_QUALITY.md`.

## 263 — DONE (designer §268: current standard across all affected benchmarks)
~~Apply the approved current quality standard to every active lossy benchmark
and run the missing comparisons.~~
Stub: every affected lossy benchmark row uses stream controls saved from the same image preparations.
See: `docs/LOSSY_IMAGE_QUALITY.md`, `docs/COMPRESSION_BENCHMARKS.md`.

## 264 — DONE (stable quality scales and one fixed baseline)
Stub: one fixed q75 baseline was set for all experiments; item 266 replaces its JPEG2000 mapping.
See: `docs/LOSSY_IMAGE_QUALITY.md`, `docs/COMPRESSION_BENCHMARKS.md`.

## 265 — DONE (B116: local backgrounds hide native-mode image artwork)
~~Correct background ownership so local panel fills do not hide image artwork.~~
Stub: native-mode backgrounds no longer hide image artwork.
See: `pdf_minify/core/backdrops.py`, `docs/COMPRESSION.md`, issue B116.

## 266 — DONE (designer §§272/276/278/284: JPEG2000 quality that matches JPEG q75)
~~JPEG2000 q75 must look like JPEG q75 through one fixed setting, with
matching colour sampling and standard packages only, so the benchmarks
compare sizes at equal visual quality.~~
Stub: JPEG2000 Quality maps to one PSNR target per 512-pixel tile, calibrated so its median quality matches JPEG at the same number; the app never chooses between the two (§287).
See: `pdf_minify/core/quality.py`, `docs/LOSSY_IMAGE_QUALITY.md`, issue B117.

## 267 — OPEN (designer §§273/279–283: documentation structure)

Each page opens with its relevant rulings (exact text), then present-tense
documentation, then only the design traps and failed attempts likely to
recur. Work iteratively, reviewing each page by hand (§280).

Remaining: give every page its rulings section; finish
`DEVELOPER_GUIDELINES.md` as a short topic-based rulebook.

## 268 — OPEN (designer §268: run the benchmarks that are not yet up to date)

Two groups of benchmark cells predate later changes and must be re-measured
from actual complete PDFs, filling only the tagged numbers (§§282/283): the
non-lossy native-mode rows, which predate the B116 composition repair, and the
non-lossy overview cells, measured before Best began trying PNG prediction on
and off (§260).
See: `docs/COMPRESSION_BENCHMARKS.md`, issue B116.

## 269 — OPEN (designer §§298/301–304: packages for Debian, Ubuntu, Windows and macOS)

x86-64 packages following Task Coach ([PACKAGING.md](PACKAGING.md)). Built and
tested on a clean system of each release: the `.deb` for Debian 13, Ubuntu
24.04 and Ubuntu 26.04 (`scripts/build-deb.sh`, `scripts/test-deb.sh`).
Remaining:

- Windows: first run of `build-windows.yml` (build, full suite, install and
  uninstall), then a check on a real Windows desktop.
- macOS: first run of `build-macos.yml` (Intel and Apple Silicon, §304),
  then a check on a real Mac.
- Real-desktop checks of the Linux packages (X11 and Wayland, drag-and-drop,
  HiDPI) before the first release.
- The first release, `v0.1.0`, needs the designer's authorization.
