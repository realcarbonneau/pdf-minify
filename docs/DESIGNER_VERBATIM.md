# Designer directives — VERBATIM

Preserve retained designer quotations exactly, without paraphrasing or
editorial annotations. Append substantive new directives with date and
verbatim text. Use correct technical terminology directly in explanatory
prose; do not add correction discussions or correction logs (§220).

Scope: substantive project requirements, defects, acceptance and lasting
development rules. One-off execution/status chatter is not a design record.
Explicit removals are not re-archived or replaced by stubs; remaining IDs
stay unchanged and removed IDs are never reused (§218).

From §272 on, each entry holds exactly one designer message in a fenced
`text` block, so spacing renders exactly as typed; a `Source:` line names
where it came from. Earlier entries keep their original blockquote form,
except §§139/141, restored exactly from their original source.

Entries before §272 were recorded by an earlier worker and cannot be checked
against the original messages, except §§139–141: their source is unclear.
When a clear-source ruling supersedes or reconfirms an unclear-source entry,
the old entry is deleted; the others stay until new rulings replace them
(§290).

## 3 — app vision (original brief)
> I want to make a simple app that works on multiple platforms, but first targetting lxde debian linux.  I want to dnd or open a pdf docs and be able to visualize various optimizations to it.  Highly opinionated, eg conversion to BW with a few strategies and a global or per page threshold, like GIMP threshold option.  Also, another option that compresses images within the pdf to jpg XL or whatever highest compression algorithms exist.  Same for BW, JDIC2 (I think if I remeber correctly.  Always max compression for all by default, but tunable if too slow.  Always fast cancel with esc by user as required.  Start by making some md docs directly in this dir with your notes, ideas and tests.

## 4 — codec name
> Yes, JBIG2, summarize your suggestions to me

## 5 — frameworks
> lok, no jxl.   rank the frameworks by the size of dependencies and range of os/wm support.

## 6 — picky UI
> what if I am really picky about smooth clean custom UI highly tailored for a specific job, like pan, zoom in/out mouse scroll, next page, prev page, DnD, etc.

## 7 — Qt check
> seems like Qt is really solid, can you double check?

## 8 — local vs system
> ok, start with that, I already stated alot of my objectives.  Can you put everything local in this directory?  Tell me what is local and what needs to be system packages?

## 9 — this request (verbatim, 2026-10-09)
> Put all my comments verbatim in a design md doc, make a docs dir.  make a dev md doc with guidance, including to keep all my comments verbatim.  I want to see a list of preset optimization options, like photo filters on a camera with a smaller version of previews, and when I click on one, the main doc has original and preview (optmized side by side, vertically or horizontally, same for the filter thumbnails, all would be choosable as menu view options.

## 10 — raster defaults (verbatim, 2026-10-09)
> Generally forcing alll images on the page and page rasterizing to 300dpi, and 8.5x11, but that also would be options on the main screen.

## 11 — docs terminology (verbatim, 2026-10-09)
> design.md, designer rulings section, verbatim.  In the docs, always call the operator/user the designer.

## 12 — finish work + TODO log (verbatim, 2026-10-09)
> yes, finish prior work, and every request put in a TODO.md doc numbered list, never renumbered, so you don't forget things.

## 13 — dev guidance rulings (verbatim, 2026-10-09)
> developement guidelines has my ruling for general guidelines, including the todo instructions.

## 14 — stdout logging and --debug (verbatim excerpt, 2026-10-09)
> The app should log everything important to the stdout so that you can run and review what happened from the log.  Also, have a --debug mode that dumps more so you can rune and evaluate issues and problems as required.  This goes in development guidelines, as it is not a ui nor feature design issue.

## 15 — stay local (verbatim excerpt, 2026-10-09)
> don't go outside the local dir, make a local ./.tmp/ and gitignore it.

## 16 — todo format + dropped log (verbatim, 2026-10-09)
> no checkbox for doto list, put item in full detail, when completed, stub, cross ref with final docs that implement it and strikethrough.  If dropped, we can have a doc with dropped ideas and log them for historical reference with reasons.  Once we do work, we don't want to redo the work and knowledge.

## 17 — full developer guidelines doc (verbatim, 2026-10-09)
> call it the full developper guidlines md doc

## 18 — docs to docs dir (verbatim, 2026-10-09)
> move most of your docs to the docs dir please

## 19 — docs lead (verbatim, 2026-10-09)
> yes, correct docs, don't ask, docs should be all updated first, then dev work.  Docs lead the decisions, rulings, design intent.  Everything else follows.

## 22 — synced panes (verbatim, 2026-10-09)
> page zoom, pan, etc is always synced on both panes

## 23 — baseline left, filters right (verbatim, 2026-10-09)
> left side is baseline, so no preview of basline, right side is per filter.

## 24 — example PDFs (verbatim, 2026-10-09)
> find a few public pdf docs that are representative test cases, not too big, 1 to 10 pages, 200k to 10 mb, put in examples dir in this repo

## 25 — scroll convention (verbatim, 2026-10-09)
> also ctl mouse scroll is up/down?  Or mouse scroll is page scroll and ctl wheel is zoom, I think that is more common ui, no?

## 26 — continuous viewer (verbatim, 2026-10-09)
> the page viewer should be continuous by default, with a gap between paged.  No page list to the left.  Zoom out should aso autowrap to multiple pages per side if it fits in the window width.  Do you follow?

## 27 — real examples (verbatim, 2026-10-09)
> Did you find example pdfs?  Your pdf file is not a good example at all.

## 28 — 3-page example (verbatim, 2026-10-09)
> use a 3 page example for the tests please.

## 29 — more real-world types (verbatim, 2026-10-09)
> Why are there only 5 examples in the repo?  There are many types of pdf available on the internet, deeds, research papers, documentations, appliance manuals, etc...

## 31 — terrible default pdf (verbatim, 2026-10-09)
> why are you using that terrible pdf as a default?

## 32 — sizes, navigator, one panel (verbatim, 2026-10-09)
> the app should show the final size of each filter below it.  It should also show the small preview which is mirroring the current view on the original.  Remove the left panel and put the options in the menu or in the right panel, there will only be one tool panel and a menu.

## 33 — drop top labels (verbatim, 2026-10-09)
> Don't show the tooltips at the top, waste of space, we will find another place for that

## 34 — fit right or menu (verbatim, 2026-10-09)
> For now, fit everything you can on the right side panel or in the menu.

## 35 — optimization test corpus brief (verbatim excerpt, 2026-10-09)
> document, compile and collect these, document in an examples md doc with descriptions, view them also.

## 37 — background previews (verbatim, 2026-10-09)
> don't freeze the whole app when doing the previews, do it in background.  the thumnail previews have to show the same viewport.  I want the app to do the full processing of each preset in the background without freezing the system, maybe set a max cores usually at 50% of the system if the processing is one core at a time (is it?) and then when panning, you are just showing a view on the rendered file.  Show a progress bar on each file that is processing.  Later, we will have an option to sort the filters and set a max auto filters, or no max.

## 40 — product and stub rename (verbatim, 2026-10-09)
> change the various names and stubs that has pdf-reducer, to pdf-minimalist.

## 41 — stale local label (verbatim, 2026-10-09)
> also, why does it say local? Ref: pdf-reducer (local)

## 43 — per-filter progress (verbatim, 2026-10-10)
> the progress bar is supposed to be for EACH filter.

## 44 — process-once cache (verbatim, 2026-10-10)
> when I was clicking on a filter preview, it seemed to be restarting it processing, but that is incorrect, it should be processed once and only reprocessed if there is a change of the file or change in the filter specifications.

## 45 — full-page minis + process exit (verbatim, 2026-10-10)
> Previews are truncated half page or something, when they should should the exact preview seen in the preview window, this was my previous design intent and ruling and you keep failing this.  Is it recorded?  Aso, why did the process close by itself??

## 46 — strip caption style (verbatim, 2026-10-10)
> Also, make the thumbnail preview box clear and the filter and size below it in smaller characters and aso clearly divided

## 47 — scroll reprocessing (verbatim, 2026-10-10)
> again, why is there reprocessing when I scroll????

## 48 — thumbnail meaning, clarified (verbatim, 2026-10-10)
> Still wrong! Thumbnails should be a mini version of exactly the current view of the larger window.  Why is this not clear?  If the original and preview windows (always synced view) show three pages wide and 4 pages high with the last page have cut, each preview shows exactly that from it's own filter view (internal, no shown, file preprocessed in bg at the start or from the latest change).  This seems simple and exacly derived from my previous rulings.

## 49 — open dialog with previews (verbatim, 2026-10-10)
> can we have an open file window that shows previews of the pdf files?  Does that require a custom open file control?

## 50 — drop the navigator (verbatim, 2026-10-10)
> the navigator section is useless, the original window is the navigator for now.

## 51 — preview-first priority (verbatim, 2026-10-10)
> WHen I open a new file, the right preview is the last to be updated, it should be always the first filter to be processed, ahead of all other priorities.  First open, it would be the first priority filter, but after, it would be whatever filter the user has selected, right?

## 52 — keyboard zoom (verbatim, 2026-10-10)
> what is the modern standard keypress for zoom in and zoom out, I tried and nothing worked.

## 53 — algorithm + size honesty (verbatim, 2026-10-10)
> why don't I see the image algorithm?  is that imposed?  It should still be shown in the filter details.  And is the size based on saving with this format?  And why estimated?  You should know the exact size of the file once processing is completed, no?

## 54 — details on the right (verbatim, 2026-10-10)
> filter details left side should have it, that is what I meant, this is obvious....
> sorry, right side

## 55 — wire the real saving (verbatim, 2026-10-10)
> Also, why is proper saving not wired?? I said the size should NOT be estimate, but be the real amounts, why is this not done and why do you keep stopping before your work is completed?  Why are you not following my design rulings???

## 56 — better JPEG (verbatim, 2026-10-10)
> I also thought that there was a better jpeg compression algo that was widely supported, better than the default jpg, but of course, not as good as jpeg xl

## 57 — JPX default + indexed colors (verbatim, 2026-10-10)
> no jpeg as default, use the best compression tools.  Also, are there options to use jbig2 or similar with reduces colors index count.

## 58 — dead Prev/Next (verbatim, 2026-10-10)
> also, prev/next buttons seem to do nothing...

## 59 — finish completely + full suite (verbatim, 2026-10-10)
> please complete your work, don't stop half compelted.  Also make a full test suite please and run each time please.

## 60 — pane headers (verbatim, 2026-10-10)
> Above the original and the applied preview, show the relevant information for each, in particular, the filter, dpi, file size, etc.  For the left side, it should show similar to the thumbnails at the bottom for the right side, it should say Original with a new key information, including the file size.

## 61 — size percentages (verbatim, 2026-10-10)
> Also, in the thumnails and top lines, shows the size percentage, like original 230kb 100%, filter 1, 230kb 10%.

## 62 — always relaunch (verbatim, 2026-10-10)
> run, always run after a new build, kill the existing one

## 63 — dpi cap wording (verbatim, 2026-10-10)
> what does <=150dpi mean?  How is that even something that make sense??

## 64 — dpi is always a ceiling (verbatim, 2026-10-10)
> then you don't need to say max, just the dpi, it's assumed it's a max, write as a ui design ruling, users don't care to see this difference.

## 65 — dead slider + percent rounding (verbatim, 2026-10-10)
> I just moved the threshold slider and the previous did not update, this is wrong.  Also, your <1% is wrong, round to the nearest, it's either 1% or 0%.

## 66 — palette reduction (verbatim, 2026-10-10)
> is there a mode that can reduce the color pallette for compression?  And what are the best algorithms for this?

## 67 — forced palette mode + benchmark (verbatim, 2026-10-10)
> I mean to force a reduction of the pallette based on automatic algorithms and a slider.  Also, benchmark verious tests for the best algorith for smallest size and which pdf image format is best to store these.   Add a few example filters please.  Review the filter examples across the corpus of pdfs docs are a benchmark for the filters to include.

## 68 — file name heads the right panel (verbatim, 2026-10-10)
> File name should be the firlst list of the right side block.  Original and size stays above the first previous main window

## 69 — right box holds file constants (verbatim, 2026-10-10)
> number of pages in the right hand box, things that are constant for original and any filter stay in the right hand box, as the main info box

## 70 — Prev/Next purpose (verbatim, 2026-10-10)
> Also, I have told you many times, the prev/next does nothing.  What is it supposed to do?  Seems useless to me.

## 71 — drop Prev/Next, add zoom buttons (verbatim, 2026-10-10)
> drop prev/next, we have scroll bars for that.   Add zoom in/out buttons in the right hand side panel.

## 72 — codec must be explicit (verbatim, 2026-10-10)
> I choose jpeg2000 filters and the codec is not shown on the right side, why the fail??

## 73 — path + page size in File box (verbatim, 2026-10-10)
> page size never changes, so put that in the top block call file info.   The final name should have it's full path also.

## 74 — page size is advanced-only (verbatim, 2026-10-10)
> The filter should not generally have a page size, I think this is dangerous, would it not break the page?  It's an advanced option only for specific cases when the page size is absurd from incorrect scanning document problems, no?  What do you suggest?

## 75 — icon buttons (verbatim, 2026-10-10)
> those are awefull zoom buttons, use proper icons for all of the four buttons please, small with icons please.

## 76 — zoom row (verbatim, 2026-10-10)
> use the magnifying glass zoom in out and buttons should be small and on same row, not out row and streched.  Follow modern best practices, maybe short word also.

## 77 — full-width strip (verbatim, 2026-10-10)
> also make the tumbnail stip go full width, right side panel stopping above with it's own scroll bar if overflow.

## 78 — toolbar approval (verbatim, 2026-10-10)
> yes please

## 79 — one codec label (verbatim, 2026-10-10)
> why do you have encode and codec on different lines, very incoherent, follow modern best practices please!

## 80 — best flat-palette compression (verbatim, 2026-10-10)
> and even a flat palette must have a better compression coded than just flate?  Is that the best compression??

## 81 — maximum-compression policy (verbatim, 2026-10-10)
> Everything in this project must be maximum compression, BW lossles, reduced palette, probably lossless, jpeg full color usually lossy

## 82 — stable details order (verbatim, 2026-10-10)
> Still, why is codec sometimes the first line and other times the last line!!??? This is bad design!  There will be one codec per filter, all common filter properties must show in the same stable sequence at the start, and custom codec specific options after.

## 83 — one DPI (verbatim, 2026-10-10)
> why do we have two different dpi values??

## 84 — buttons still not fixed (verbatim, 2026-10-10)
> your buttons are not fixed

## 85 — zoom %, small Save, Cancel meaning, one DPI (verbatim, 2026-10-10)
> No, you said buttons combined with the scale percentage, no?  and save as a small button.  What is the X for?  Cancel?  Isn't that an undo?  ANd undo what?  Also, there should only be a single dpi value for the whole filter.  That is all user's care about, never two different dpi values.  DPI is clear and means for all images in the document, why are you making this complicated?

## 86 — zoom spinner (verbatim, 2026-10-10)
> what is modern best practices for a spinner in qt between 1 and 100% for zooming?  Please research and implement.  The current option is not good.

## 87 — plain headers (verbatim, 2026-10-10)
> remove the file name from the left side top title.  Also, remove the bold from both.

## 88 — drop filled-background (verbatim, 2026-10-10)
> Also, when you are done your current work, drop the filled-background file please, it's not usefull.

## 89 — progress starts at 50% (verbatim, 2026-10-10)
> Why do the per filter progress bars always seem to start at 50%?  This is also incorrect please fix.

## 90 — click restarts left filters (verbatim, 2026-10-10)
> Also, when I choose a to be processed filter to the far right, when other fitlers are processed to the left, reprocessing starts onthe left filters, this is also incorrect.  Add each of my notes to a BUGS.md doc, in a numbered list and cross only once I have comfirmed that they are fixed.  Look back at my past complaints and add them to the bugs list please.

## 91 — remember last file (verbatim, 2026-10-10)
> Also, the app should remember the last opened file.

## 92 — debounce review (verbatim, 2026-10-10)
> when I scroll on the main windows, the previews are not always updated to the last view, there should be a debounce for updating and also update after the last view change after debounce time also.  I think debounce will always be correct for fixing this, but please review.

## 93 — run normally + last file broken (verbatim, 2026-10-10)
> always run normally so that I can test the features like opening the last opened file please.  So far, that has NOT worked also, add this and my previous message to the bugs list, maybe we should call it issues.md?

## 94 — safe close (verbatim, 2026-10-10)
> I closed the last one while it was processing as a test, this should not crash, this is normal to write safe code for all scenarios and have test cases for all scenarios, please make sure you do complete work.

## 95 — bars start at 50% again (verbatim, 2026-10-10)
> thumbnails progress bar always starts a 50% and stays there until real processing starts, this is incorrect. please fix and add to issues.

## 96 — strip height, selection bar, overlay progress, action row (verbatim, 2026-10-10)
> The preview thumnail section below should always be full heigh, no vertical scroll bar. There is a blue bar under the selected filter which you should remove.  The progress bar should be layed over the middle of the thumbnail and remove the progress bar reserved space below the thumbnail.  Also, put the save and X button on the same line as zoom and put them less wide.  I still don't know what the X button does, please explain once you are done your work.  Create each of these as issues and I will confirm once they can be marked as completed.

## 97 — focus bar remainder (verbatim, 2026-10-10)
> why is there still a bar under the thumbnail when it is selected, but not when the window is out of focus, is that a standard part of the widgets?  I asked to remove the "blue bar", not just the "blue".

## 98 — selection ring vs bar (verbatim, 2026-10-10)
> The whole thumbnail is already highlighted when selected, the bar below it is redundant, at least from my perspective, but I want to follow modern best practices if there is a specific reason for ti.

## 99 — standard progress + widget lab (verbatim, 2026-10-10)
> The progress bar layed over the thumbnails should be the standard progress bar.  Why did you put it green which varies from the previous progress bars.  Make me a menu item with widget lab that shows various options for the progress bar, including a percentage in the center of each.  Also variations that follow modern best practices for Qt and the existing framework.  Also, make another menu option with a window with variations of the zoom, save, cancel buttons, also including those that follow modern best practices.

## 100 — lossless checkbox (verbatim, 2026-10-10)
> Also, add a checkbox for lossless.  If the algorithm doesn't have the choice, keep it, but make it grey with the correct otpion, it should always be show for each filter type on the right side.

## 101 — preview grid out of sync (verbatim, 2026-10-10)
> Also, when I zoom out, the original side works correctly by putting pages side-by-side, but the right preview side does not follow in sync.  Add this to the list of issues.

## 102 — popup buried the traceback (verbatim, 2026-10-10)
> 'PySide6.QtGui.QPalette' object has no attribute 'Mid', BUT you should see this in the log automatically, no?  This was in a popup.

## 103 — raster is per-filter + toggle dead (verbatim, 2026-10-10)
> force full page raste should be per filter option and should not be enabled on the default filters except for one BW example filter.  Normally, we don't want to raster the text, only copress the images.  Also, I change the full-page raster option on/off and no recacls, so that is another fail, another issue.

## 104 — locked equal panes + relaunch rule (verbatim, 2026-10-10)
> Also, another issue, no horizontal divider between original and right side preview, they must always have exact same size.  Also, I already told you to always stop and relauch the app after you make changes, why do I have to repeat??

## 105 — toggle churns all minis (verbatim, 2026-10-10)
> when I check/uncheck the force raster, it changes all the BW thumbnails, this is wrong!

## 106 — sizes churn on toggle (verbatim, 2026-10-10)
> It still changes the size of all the thumbnail previews, you clearly don't have clear app architecture, please improve and fix!

## 107 — remove the splitter (verbatim, 2026-10-10)
> Remove the vertical sizer between the two main previews, not just make it not draggable, that is just wrong.

## 108 — click looks like recompute (verbatim, 2026-10-10)
> also, why when I click on a mini, the filter seems to be recomputed, that is wrong, read my design rulings.

## 109 — rename/copy filter (verbatim, 2026-10-10)
> Also, have a button that permits naming/renaming the filter, and a popup for that.  Also have a copy button that shows the same naming popup, but used for the copy.

## 110 — github text + findable readme (verbatim, 2026-10-10)
> Also, when you are done, give me some text, descriptions and tags to put in github project.  Also, make sure the readme makes the project findable and well explained.

## 111 — right preview empty (verbatim, 2026-10-10)
> Big Preview right side is stil not working!!  Why are you failing so much?

## 112 — save filter + one-line row (verbatim, 2026-10-10)
> I need a save filter changes button also after the rename and copy, or before.  Also, put the filter name and these buttons on the same line, resizing the dropdown to fill the space.

## 113 — preview must show the filter + button icons (verbatim, 2026-10-10)
> It still doesn't work, I choose a BW mini and the big upper right preview is wrong!  Why are you so lost??

## 114 — icons on Save/Rename/Copy (verbatim, 2026-10-10)
> And put the proper icons on the save, rename, duplicate buttons.

## 115 — amounts status, panel slider, rename icon (verbatim, 2026-10-10)
> Why when I click on thumbnails is says "rendering amounts"?  And add an adjustable slider for the far right pane with the controls.  Also, find a rename icon, there are some standard.

## 116 — force toggle churns filters (verbatim, 2026-10-13)
> again, when I change full page raster, many filters get updated, this is wrong and I have said this many times!

## 117 — panel slider wrong, want draggable divider (verbatim, 2026-10-13)
> and the panel width slider is completely wrong, the divider should be adjustable, like the previous preview divider.

## 118 — squeezed panel must scroll horizontally (verbatim, 2026-10-13)
> If the right panel becomes too small for it's content, it must have a horizontal scroll bar

## 119 — raster-vs-text sizes + user chooses (verbatim, 2026-10-13)
> Why would ful page rasterization be much smaller than with it off, this is wrong, text charaters take less space than the equivalent in bitmap.
> I don't follow your answer, there must be wrong, text always takes less space as each character will be much smaller than a bitmap of the character. Regardless, follow my prior instructions, the user can choose, I did not ask you to benchmark it.

## 120 — cursor rename icon + icon-only filter buttons (verbatim, 2026-10-13)
> isn't there a standard rename icon that looks like a cursor with a letter or two? Also, remove the text on the filter buttons, rename, copy, save, and just keep the icon and tooltips.

## 121 — mixed sizes + zoomed preview text (verbatim, 2026-10-13)
> Explain why the rasterized BW filter is much smaller than the one that keeps text, this seems incorrect. Also, when I zoom in on the non-full-image-rasterized preview, the text does NOT look like the original, this is also incorrect. Are you keeping the text and rasterizing the whole image also? I tested on the images.pdf. You can do benchmarking for this issue and do in depth analysis, you can create an MD doc specifically for this, since you seem to have alot of trouble getting this to work. Document your notes, benchmarks, failures and successes please. Cross ref with issues and other relevant docs

## 122 — single path: save temp, preview/minis/amounts read it back (verbatim, 2026-10-13)
> The preview need to show the saved file, DO NOT have multiple paths, this is the root cause of alot of your failures!! One single path, process the file, save temp, display temp file in preview, minis come from save temp files once they are processed. This is an important design ruling, please put this in the design under architecture and flow. Do you follow this flow? Do you understand why this is robust and safe?

## 123 — OS temp dir via Qt + persistence/temp docs (verbatim, 2026-10-13)
> The temp dir for the app should be the standard temp dir for the os, for linux it's /tmp/ I think, but the framework (qt?) should be able to provide this information, right? It would be different per OS, and this is what I want. Please review and do your research and correct. This is also a design ruling and an issue, please document accordingly. Also, make a persistence and temp work dir docs and cross reference accordingly.

## 124 — elided pane titles with hover text (verbatim, 2026-10-13)
> When the top title above each preview goes beyond the available width, put elipses and hover over full text. Add this as a design ruling.

## 125 — rulings into relevant docs + UI layout doc (verbatim, 2026-10-13)
> You can move the relevant design rulings to their relevant docs. You can create a main ui layout doc also, rename the file as you feel is best.

## 126 — mixed was never specified: separate option doc, do not implement (verbatim, 2026-10-13)
> What is a mixed path? I never specified this and it's not indicated as an option. is that to take all the BW text and make a JBIG2 layer in additional to the images? Put this as a new separate option with it's own doc, for now, this should not be implemented, as you can see, you made a mess of this, and it just causes confusion. I never asked for this.

## 127 — FFPR is optimize-images vs full-page-image (verbatim, 2026-10-13)
> No, FFPR is not a mixed path. The basic decision is to optimize existing images, or the full page into a single image. This is the basic functionality. I don't know what your mixed path was, but you were saying something about colors in a BW and I could see the letters being rasterized even when the FFPR was OFF, this was your fail.

## 128 — DnD strip order + inline control rows (verbatim, 2026-10-13)
> Again, how is it possible that FFPR is 10x smaller than without. Explain to me. I made an identical filter with both variations. Also, add a design rulings: I want the filters to be DnD orderable in the bottom list of minis and the dropdown follows the same order and the processing follows the same order, except for the one currently selected which is always first priority regardless of ordering. Also, put Strategy, dpi and page size on the same row/line as the lables please.

## 129 — DPI applies to every image transform (verbatim, 2026-10-13)
> OMG, why are you not respecting the DPI? How is that not clear??? DPI apply to ALL image transformations on the page, even if smaller res, they get upsized DPI on their original color pallette, I think Laconz something like that is considered the best, please review notes, if we don't have notes on this, we need to do some research. The design flow is all images are forced to the setting DPI in their original image space, then the transformations are applied (eg BW, algo, jpg compression, etc). Same recipe for FFPR. Do you follow? Please document that and create an compression algorithm page for these rules, flows and benchmarks, also note failures, issues and TODOs on this document and cross reference

## 130 — combos fit largest item + issues onto topic pages (verbatim, 2026-10-13)
> Also, a UI design ruling, the dropdowns in the right pane should be sized to the largest item, if items don't fit, they get elipses at the end. Also add as an issue and fix. I think we have enough issues to now start putting the issues on the relevant topic doc pages, please do this.

## 131 — sizes move on FFPR click + DnD/highlight still broken (verbatim, 2026-10-13)
> DnD does not work, highlight is not fixed. Other issues: When I click on a filter mini that has FFPR, the size of other filters changes, obviously this is completely wrong and you have problems in your architecture. This shows you have spaghetti code.

## 132 — DnD still dead (verbatim, 2026-10-13)
> Again, DnD not working. This should be very basic ui functionality, either you are doing something wrong or we are not understanding each other.

## 133 — filter sequence numbers (verbatim, 2026-10-13)
> Put the sequence number in front of the filter, eg "1. ", "2. ", both in the minis and in the dropdown.

## 134 — full theme highlight + standard drop line (verbatim, 2026-10-13)
> Minis should be fully highlighted with light blue with the dark blue (both per theme deifnition, not hardcoded), for the whole area, including the text below them. Also, why is the DnD bar and hollow rectangle?? That certainly doesn't follow modern UI best practices, I have never seen that. How does the default behavior end up looking like that?

## 135 — closest divider snap (verbatim, ruled 2026-10-13 between §§128/132, logged late)
> No, that really is not working properly. First, I don't see any highlight drop line, second, it only changes the cursor when exactly over the divider, that is also incorrect, as anywhere should automatically choose the closest divider. Why are you not finding this as standard UI patterns within the framework? Do research, search the internet, this doesn't make sense.

## 136 — current version worse, restate the pattern (verbatim, 2026-10-13)
> No, this version is much worse! It lost the closest DnD snap, and lost the visual vertical bar indicator. Also, the highlight is just wrong. Please review all my requested related to this, I have always asked for the same thing, summarize them all and tell me what you think that means as a UI pattern, short, concise, numbered list in flow from the moment before a user clicks on a minis to after the final drop.

## 138 — light-blue overlay, current mess itemized (verbatim, 2026-10-13, ruled before §137, logged late)
> No, the whole mini should have a light blue highlight overlay, this is simple. what i see is a light blue box within a black rectangle outline and a black horizontal divider bar with light blue text color and a dark blue underline, just a total mess, nothing like what I requested.

## 137 — screenshot canon, never program blind (verbatim, 2026-10-13)
> Add canon instructions that you have to take screenshots (in a virtual frambuffer, same for the tests) and view the formats, layouts and other work you do to see if they make visual sense and follow modern best practices, or else you are just programming blind for GUI work!

## 139 — highlight approved + auto suite + drop bar missing (verbatim, 2026-10-13)

Source: designer message in the session `ses_ed9c28122ffe8V7aTCnj1ue5w6` (2026-10-10 to 2026-10-13); copied exactly from its export on 2026-10-20.

```text
Ok, this highlight is good.  you can document and harden the test cases for this.  Also make a full suite of test cases that run automatically, so you don't have to run each one at a time.  Also, next issue, the DnD does NOT show the drop indicator vertical bar, this is wrong, I already defined this many times.
```

## 140 — drop Original from the filter dropdown (verbatim, 2026-10-13)
> Remove the "Original" option from the filter dropdown, that is NOT an option, it is the default for the left side preview, always.

## 141 — drag ghost needs true uniform transparency (verbatim, 2026-10-13)

Source: three designer messages in the session `ses_ed9c28122ffe8V7aTCnj1ue5w6` (2026-10-10 to 2026-10-13); copied exactly from its export on 2026-10-20. The first two came before §140, the third after it.

```text
Also, typical DnD should have some transparency, what is modern GUI best ptractices?
```

```text
NO! That is not correct, the whole ghost should have the same transparency percentage.  What you did is incorrect, with some parts being fully transparent, and other full opaque and I don't know what oyu did with letters, but that is definately incorrect and not modern best practices.  Did you even look at the transparency render during a DnD ghost operation???
```

```text
tell me what you did for transparency, because it just doesn't work
```

## 142 — ghost is the selected blue mini at about 50% (verbatim, 2026-10-13)
> The ghost should be blue exactly as it is when I click on it to start the DnD, but probably 50% when over white, because of transparency, or some similar strategy. Follow modern best practices for GUI, the previous worker was not skilled and did mediocre work, I don't trust it's work.

## 143 — blue rectangle is not a recognizable mini (verbatim, 2026-10-13)
> No, not good, the ghost is just a light blue rectangle, not the highlighted blue mini, this is a fail, reread my requests and design rulings, this is simple and obvious, think of what a GUI user expects!

## 144 — stronger ghost + drop from any height (verbatim, 2026-10-13)
> The DnD is good, but a little light, try 65%? Or what is modern best practices for transparency in modern GUI?  Also, let the DnD go outside of the mini strip, same transparency, but snap the drop to the nearest vertical drop point regardless of where it is vertically.

## 145 — remove ghost bottom bar by fixing strip design (verbatim, 2026-10-13)
> There is a weird transparent white bar across the bottom of the ghost, it comes from behind the bottom scrollbar I think.  The previous worker had alot of trouble with a similar blue selection bar below it before and a vertical scrollbar that was incorrect.  I think the previous worker did alot of hacks and did not follow modern best practices for QT and GUI, please review to solve the root causes, and not just patch onto of bad code and bad design.  You can review the docs, my rulings, issues, etc for more context.

## 146 — ghost at 75% opacity (verbatim, 2026-10-13)
> Also, change the transparency to 75% for the DnD ghost please.

## 147 — ghost explicitly confirmed; dated acceptance (verbatim, 2026-10-13)
> Ok, this is good, you can mark these issues fixed, confirmed by me.  I don't know if the worker was self-marking issues fixed without my confirmation, but try to have a marking that indicates that I explicitly confirmed it fixed and the date.  There are still other DnD issues, so mark this ghost as fixed.   Is transparency at 75% now also?

## 148 — dropped minis must renumber immediately (verbatim, 2026-10-13)
> When I DnD a mini, the dropped numbers don't renumber immediately, only if there is some reprocessing or miss processing that gets triggered, this is wrong and bad design, please review for the root cause and fix the design properly.

## 149 — renumbering confirmed; real artifacts and unsaved filter lifecycle (verbatim, 2026-10-13)
> Ok, this renumbering issue seems resolved, you can document my explicit confirmation.  Next issue, this also seems like a design implementation issue, please find the root cause.  Canon design is that all filters be run for real and the previews come from the filtered files, and these files have the true final size, not an approximation, please make sure this is clear canon design ruling in the proper dev docs.  When I zoom in/out, the preview and minis update live, this is good.  However, when I click on a mini that has not been clicked yet, I see it doing a "Rendering preview..." processing.  This is obviously wrong flow because this is already fully processed to have the mini previews that work.  So something is fundamentally wrong.  There should be no reprocessing EXCEPT for changes to the filter.  And there are two types of changes to the filter, the first is live changes which should update the processing live with a debounce and mark the filter as changed with a star * (per standard GUI conventions, right?).  However, if the chosen filter is changed without saving, there should be a popup for discard/save/save-as (aka save copy, choose best modern term).  If discard, then the previous file is kept (and the temp new live changes file is deleted), inverse if save, save-as keeps both of course.  These are multiple design runlings, please document in the correct places, also document the issues and work on them.

## 150 — collect related rulings and audit contradictions (verbatim, 2026-10-13)
> review and collect all my similar design ruling that covers this and compile into the correct documents and review for and contradictions and incoherences.  I had to repeat this and related designs many times and the weak worker was still failing, so I expect other problems also.

## 151 — check recorded temp-file location (verbatim, 2026-10-13)
> where are the temp files stored?  I previously ruled, but I am double-checking to see what the prior weak worker recorded.

## 152 — identify temp sessions by process ID (verbatim, 2026-10-13)
> So the temp dir should be in a dir with the process id number?  Is this possible?

## 153 — PID ownership without invented session retention (verbatim, 2026-10-13)
> Why keep all sessions?  That is not what I asked for, also, two live applications cannot share a PID, or yes?  Why did you invent something beyond my request and design ruling?

## 154 — stable filter identity versus changing display number (verbatim, 2026-10-13)
> how do you identify the unique filter name, if the number prefix can change, you use the core name?  Ref: /tmp/pdf-minimalist/saves/<PID>/filter-…/filtered.pdf

## 155 — unique internal UUIDs and UUID-named filter directories (verbatim, 2026-10-13)
> you should give the filter a UUID and never permit two filters to have the same UUID, check when loading, in case someone copy/paste filters.  These UUIDs are only for internal use, name tis dirs with the UUID.  I think this is modern best practices, no?  Python has UUID generation, not tied to the network card?  Or just make a random UUID generator, if python does not have.

## 156 — reordered mini clicks flicker wrong names (verbatim, 2026-10-13)
> New issue, everytime I click on the minis, after reordering them, the last ones seems to flicker old names, for the current layout, the flicker of other wrong layout names starts as of filter number 5.  Regardless, this is another clear spaghetti code symptom from the weak worker.  Please review carefully and fix the code to address the root cause in the code please!

## 157 — repeated request for reordered-mini root fix (verbatim, 2026-10-13)
> New issue, everytime I click on the minis, after reordering them, the last ones seems to flicker old names, for the current layout, the flicker of other wrong layout names starts as of filter number 5.  Regardless, this is another clear spaghetti code symptom from the weak worker.  Please review carefully and fix the code to address the root cause in the code please!

## 159 — reordered names confirmed; equal mini padding and darker background (verbatim, 2026-10-14)
> Ok, seems good, you can mark this as fixed.  Next issue.  Your previous fix to the mini hightlight and vertical scroll added back the white space gap at the bottom of the minis strip.  I want the same gap as at the top of the minis.  Also, the background of the minis should be a bit darker so that I can see the difference between the white mini page outline and the background.

## 160 — explicit discard button wording (verbatim, 2026-10-14)
> Change "Close without saving" to "Discard Changes"

## 161 — cancel unsaved mini switch keeps the edited filter (verbatim, 2026-10-14)
> Also, after clicking another filter in the minis, if I escape the "Unsaved filter changes", the filter selection changed, but nothing was saved, nor discarded, this is wrong.  Cancel should remain on the edited fiter.

## 162 — revert changes icon beside dropdown (verbatim, 2026-10-14)
> Also, add a revert changes igon beside the dropdown, the typical counter-clockwise arrow, right?

## 164 — center the actual page group when zooming out (verbatim, 2026-10-14)
> When I zoom in, what happens incorrectly is that sorry, when I zoom out, what happens incorrectly is that since the pages get smaller and smaller and they're supposed to be tiled one beside each other, going from left to right row by row, the page gets left aligned when it should be centered.When I zoom in, what happens incorrectly is that sorry, when I zoom out, what happens incorrectly is that since the pages get smaller and smaller and they're supposed to be tiled one beside each other, going from left to right row by row, the page gets left aligned when it should be centered. However, it does stay vertically centered, which is odd. It should stay both vertically centered and horizontally centered when there's no other pages, when there's one page. If there's two pages, then the layout of two pages should be horizontally centered, etcetera. It should not just go off to the left as if it had other pages when it doesn't.

## 165 — preview/original centering discrepancy (verbatim, 2026-10-14)
> Also, oddly, the preview seems to center correctly, but not the original.

## 166 — slow repeated layout adjustment after shrinking the window (verbatim, 2026-10-14)
> Something very strange happens when I go from maximize, so the screen is wide, lots of place for everything,
>   to a much smaller screen. I think because the right panel is compressed or cannot show the whole panel
>   width, then it slowly, maybe three ticks per second or a tick per second, uh, kind of adjusts to both
>   adjusting the middle divider between the, the preview and the original, and the divider of the um, side
>   panel. So when I go from full screen to, let's say, a half screen to the left side or even smaller, then I
>   see this strange uh, readjustment uh, iteration that lasts uh, 5 to 10 seconds and then stabilizes.

## 167 — explicit confirmation of the resize/layout feedback fix (verbatim, 2026-10-14)
> Ok, this is confirmed fixed, thank you.

## 168 — BW image-layer composition, preserved text, FFPR and benchmarks (verbatim, 2026-10-14)
> The next issue is more complicated to describe and to analyze. It relates to the forceful page rasterization
>   and also optimization of the PDFs. So when I choose black and white and there's some images and some text,
>   obviously if we convert the images to black and white and we keep the text, the file should be smaller than
>   when we rasterize the full file because text is much more compressed when it's actually text versus when
>   it's pixels, right? So this doesn't happen, and the best example is the simple images.pdf, I believe it is.
>   So there's one mode that is FFPR, which is full page rasterization, and it is much smaller than the mode
>   with images. This doesn't make sense. What should be happening is that the images themselves are reduced,
>   uh, compressed based on whatever the algorithm is. So for example, if we're doing black and white and then
>   GBIG2, GBIG2, And the images overlap. Of course, we only want to have one final set of images in the PDF,
>   meaning that I don't know how you suggested, but either we um, make one image that covers it all with some
>   blank spaces, or we cut out corner the, the areas of overlap from the other image and put it white. Um, and
>   then, I, well, I think we can just cover the area with the images. Uh, the full rectangle, even the full
>   rectangle of the page, it doesn't matter because the black and white compression will apply. Uh, this is
>   without the text, of course, and then the text is um, kept separate. So I don't know what's happening now,
>   but obviously that's not working. If it's um, text over images, then PDF should keep this layer uh, keep
>   these layers. So we do the PDF, sorry, we do the images uh, black and white, for example, and then compress
>   and then just put the text back on top. If it's put full page rasterization, then the whole thing is
>   converted to images. So tell me if you follow this, and if it makes sense, then proceed with this fix and do
>   the proper benchmarking to make sure that the compression algorithms are working correctly. It could be
>   that the weak worker did a mess of this, and it has to be redesigned or restructured.

## 169 — preserve native text rather than glyph-shaped masks (verbatim, 2026-10-14)
> You don't need to keep masks that follow the text, can't you just overlay the texts, as they were before?  Or the texts already have complex transparencies?  I think that text should already be describing their background colod and transparency and foreground color and what layer they are on, in front or behind the image.  But not complex transparency outlines, no?

## 170 — retain vector diagrams; text/vector compression options (verbatim, 2026-10-14)
> Vector diagrams remain, these are rarely taking alot of space.  Most waste is images.  Also, is the test and vector graphics compressed within a pdf?  Are there compression options?

## 171 — simple image canvas and native overlays; FFPR for fidelity (verbatim, 2026-10-14)
> Why is this complicated?  The PDF always must have a clear and explicit flattening sequence to display the document.   Why can't we just keep everything bitmaps as a big image and overlay the text.  If this doesn't look nice, then the user can choose FFPR options, or we can add further filter profile options.  Choose a simple strategy that will help reduce the size of the file.  Ideally keeping text and images clearly separate.

## 172 — FFPR preview introduces grey antialiased bitmap edges (verbatim, 2026-10-14)
> Why when I zoom into a supposedly BW filter images with FFPR, do I still see antialiasing? I see shades of grey on the edges of both images and texts.  This is absolutely wrong, obviously.

## 173 — exact original/filter display; AA only for native text/vectors (verbatim, 2026-10-14)
> Previews of original and filters must be exact! No additional filtering, smoothing, etc.    AA can be used on text and vector images of course, but never on anything converted to bitmaps.

## 174 — native geometry refines on zoom; AA can be disabled (verbatim, 2026-10-14)
> you can leave fonts and vectors without AA, just show their higher precision shapes when I zoom in so I can see the diff between what is bitmap and vector.

## 175 — prefer precise display with all AA/smoothing disabled (verbatim, 2026-10-14)
> In otherwises, if it's simpler to drop all AA and smoothing for display, that is ok, I rather precise exat rendering regardless.  So this might be the best solutions overall and addresses the root cuase of the problem.

## 176 — certify current platform and document cross-platform packaging (verbatim, 2026-10-14)
> Also, document the current platform as the certerfied and create a document for packaging, meaning if any packages are required to make this work on multiple platforms, you can follow the taskcoach project which is also on github and in a sister dir here.

## 177 — unexpected dark outside border in color output (verbatim, 2026-10-14)
> Why is the color version showing some sort of black/dark border around the outside, when there is no such pattern on the original?

## 178 — editable numeric values and spinner controls beside sliders (verbatim, 2026-10-14)
> Also, make the sliders with a number that can be edited and a spinner or something similar, what is modern best practices for designs of such inputs?

## 179 — fix both controls and the color defect; clarify original image representation (verbatim, 2026-10-14)
> Fix both, but I don't understand how that can happen, is the image not as I see it in the original?

## 180 — flatten full-color content before resizing and filter transforms (verbatim, 2026-10-14)
> It should always render flattened first, why is it not doing this?  this should be simple.  Can your render everything without the text, full color, then upscale, then apply the transforms.  I already ruled that this was the flow, but the prior weak worker probably messed this up.

## 181 — clarify whether the Firefox artwork is bitmap or vector (verbatim, 2026-10-14)
> I guess you are asking me because there is bitmap mixed with vectors?  Is the firefox logo a vector image or bitmap or a mix?

## 182 — determine resize/filter order for the flattened image layer (verbatim, 2026-10-14)
> Ok, so what is the problem, take the flattened image layer, upscale if required in the full color palette, then apply filters to original scale + upscaled, then downscale, or should we scale first to the target DPI, then apply filters?

## 183 — nearest-color palette mapping and one global edit debounce (verbatim, 2026-10-14)
> In the low color versions, colors are getting incorrectly converted to white instead of their closest colors. Also, when using the spinner, after a debounce, a rerender should be triggered, same for the sliders or any other change.  We should have one global debouce for this.  What do you suggest as a debounce time?

## 184 — explicit confirmation of improved palette output; request for root cause (verbatim, 2026-10-14)
> yes, much better, what was the problem?

## 185 — native full-width mini progress bars with an opaque white backing (verbatim, 2026-10-14)
> I want the minis progress bars to follow the same style as the default progress bar and to span the full width of the minis reserved width (larger than the mini image) and also to have an opaque white background behind to make the progress bars visible.  Follow modern GUI best practices.

## 187 — retain visible mini highlight around progress overlays (verbatim, 2026-10-14)
> Obviously you need to have some padding between the progress bar and the edge of the minis to permit some highlight to show.  What is the common padding we are using?  I see a bit of padding above and below.

## 188 — remove minis title and unify main-region spacing (verbatim, 2026-10-14)
> Also, remove the title for the minis and remove the extra space between the previews and the minis same for the right panel.  Have the same padding for the whole line.  Also, have the same side padding.  Everything is different now and staggered and looks like a mess, poor design and poor modularization.

## 189 — Save As must select its new filter; explain app closure (verbatim, 2026-10-14)
> I just did a change, then click mini elsewhere, then save as, but the selection did not move to the new sav-as filter, this is incorrect.   Modern GUI design would expect this.  Review anywhere this pattern would apply.  Also, I think the all just crashed, or you killed it?

## 190 — taller mini progress bars and larger percentages without white padding (verbatim, 2026-10-14)
> Make the progress bar a bit fatter (more height) by 50% more and remove the white padding, this will help make it more visible, also, increase the percentage character size accordingly.

## 191 — center progress in the complete mini frame (verbatim, 2026-10-14)
> And center it within the whole box of the mini, not just the image part.  Centered within the frame height of the mini.

## 192 — confirm mini progress, title the configuration block, design layered-color JBIG2 (verbatim, 2026-10-14)
> Ok, this is good.  Next issue, above the right pane, put a text "parameters" or Configuration, or something like this.  This will make all three blocks follow the same pattern.  After, the next issue is to design an low color count pallete compression model with multiple JBIG2 with each a color, so 4 colors +while would be 4 JBIG2 overlaid, do you follow this plan?  Can you do this?

## 193 — layered-color JBIG2 scope: design and benchmarks before integration (verbatim, 2026-10-14)
> Design and benchmark first

## 195 — remove redundant working labels (verbatim, 2026-10-14)
> Also, drop the "working..." label, it's obvious it's working by the progress bar...

## 196 — question whether odd revert/rename glyphs are standard icons (verbatim, 2026-10-14)
> Those icons look odd, in particular the undo and rename, are those standard icons? Standard KDE or nuvola?

## 197 — approve desktop-theme icons with one standard fallback set (verbatim, 2026-10-14)
> ok, as you suggest.

## 198 — reduce the previous progress-bar enlargement (verbatim, 2026-10-14)
> I previously asked to increase the progress bar by 50%, I want to change that to only 25% of it's original size.

## 199 — clarify progress-bar scale (selected option, 2026-10-14)
> 25% larger — 1.25× original

## 200 — reject the current icons and request an icon lab with choice codes (verbatim, 2026-10-14)
> I don't like those icons, make an icon lab menu item with a window with various options and codes for each so I can tell you my choices.  use icons from nuvola, oxygen and other similar libraries.

## 203 — editable compression algorithm and qualified threshold terminology (verbatim, 2026-10-15)
> I think we need to add an option that is the algorithm, JBIG2 BW, JBIG2 Color, Flate BW, Flate Color JPEG2000, JPEG.  Because we have no way of choosing between the options at the moment, filters seem to be locked into their algo.  Also, why do we have both JPEG and JPEG2000, and Flate BW and Flate Color?  For backward compatibility?  Aso, the terms strategy should be qualified, is that Threshold automatic strategy?

## 204 — clarify content-stream compression versus image compression (verbatim, 2026-10-15)
> But flate also always compresses the contents (eg characters, vectors) of the pdf? or are there other options?

## 205 — native text/vector compression options, benchmarks and support limits (verbatim, 2026-10-15)
> what are the top text compression algorithms, and we should add an option for this also.  And make a benchmark document for that scope of compression also.  Are there support limitations on some of these algorithms?  Any reason to keep lesser compression algorithms?

## 208 — ask whether Brotli image comparisons exist and are applicable (verbatim, 2026-10-15)
> what do your benchmarks show for brotli on color index versus jbig2, and on BW?  Is that applicable comparison?

## 209 — size-only equivalent bitmap compression benchmarks (verbatim, 2026-10-15)
> you have color index filters that use flate, so you should make equivalent bechmarks for better compression on color index and bw please, compare with JBIG2 and color JPBIG2 also.  Do the work please.  We are only comparing size a this time.  Compute time is not measure because the cpu load on this workstation is fluctuating alot and unpredictably.

## 210 — ask which compression combinations are useful, especially with FFPR (verbatim, 2026-10-15)
> So we need a option for the compression algorithms, however, there are only certain combinations that make sense, right? Brotli content implied Brotli images or Jpeg/jbig2, never Brotli+Flate for example.  Also, when we use FFPR+J* does it still make sense to choose Flate/Zopfli/Brotli?  Or there is litle/nothing to compress?

## 211 — document reasonable combinations first; compare combined versus separate controls (verbatim, 2026-10-15)
> Make a documentation table of reasonable combinations, also, should we have the combination as a single compression dropdown (eg Brotli+JBIG2, FFPR+JPEG2000, etc.)? Or separate controls that are enabled/disabled?  Start with the table please.

## 212 — review whether the combinations cover the full range of documents (verbatim, 2026-10-15)
> of the tabe options, considering the full variety of files and situations, including those in this repo, do you think that tabe of combinations could be reduced?  Or should be increased?

## 213 — opinionated best encoding; retain alternatives for reader support, not encoding cost (verbatim, 2026-10-15)
> so all pdf readers can decode flate encoded with zopfli?  Encoding is not a constrain, the objective of this project is to be an opinionated pdf compression suite with the best available algorithms for encoding, we drop superceded algorithms, the only concern that affects decisions would be pdf reader support, where for some usage, a more generally supported decoder would be proferred, in others, the user may expect readers to have the most modern and best pdf reader.

## 214 — remove classic Flate as a selectable encoder; retain comparison evidence (verbatim, 2026-10-15)
> Compression time is not a concern, so we drop classic Flate from the options?  Keep in the comparison table for reference.

## 216 — move the request log into docs (verbatim, 2026-10-15)
> Move the TODO.md to the docs dir please also

## 218 — document durable design, not routine execution requests (verbatim, 2026-10-15)
> commit/push is not a todo/issue neither, you can scrub/drop those, if any, from the docs.  Do you see anything else that is not design related?  Like requesting to run the app or whatever else that has no added value to the docs.

## 219 — separate PNG-predictor comparisons from the main algorithm-size analysis (verbatim, 2026-10-15)
> are all of your *+PNG benchmarks larger than the non +PNG versions?  It looks like that at first glance.  That seems obvious.  I think you should delegate that comparison specifically to a separate doc and state that this is to be exepected, and removed from the main analysis to avoid noise.

## 220 — retain all benchmark columns; omit typo-correction commentary (verbatim excerpt, 2026-10-15)
> ok, then leave in the tables as it was.  Also, clean this up, we should NOT have typo correction discussions in the docs.

## 221 — bold the smallest size in each benchmark row (verbatim, 2026-10-15)
> Also highlight in bold the best of each row in the tables, can you do that in md?  Or not supported?

## 222 — integrated algorithm-combination matrix of final complete-PDF sizes (verbatim, 2026-10-15)
> where is the matrix comparing all algo combos file sizes on complete files, your analysis seems scattered.  We only care about the final file size, this is integrated compression analysis.

## 223 — realistic combination rows over five representative PDF classes (verbatim, 2026-10-15)
> Why does your table have columns like Z/B, etc?  We agreed that those are not realistic?  Same for F/Z.  These are useless.  Have one table with all the algo combos as rows and choose a 5 typical types of pdfs that cover the major styles.   Then we will have other table that goes into more details for specific scenarios, like color photos, scanned BW docs, mix images text, etc.  There are only a few major classes of pdfs that are load bearing to pdf compression algorithm analysis, no?

## 224 — repair rejected preparations; include color FFPR at a common 300 DPI (verbatim, 2026-10-15)
> what does "PREP FAILED", please fix, or is your flow or design implementation wrong??  Also, why don't you have FFPR for color documents, that is valid also.  I think you should do all at 300 dpi to make everything comparable.   JPEG compression at high levels is not so affected by the resolution.

## 225 — default every filter to 300 DPI; avoid redundant DPI benchmark variants (verbatim, 2026-10-15)
> I think we should also convert all the filters to 300dpi default for now.  We know that lower dpi will be smaller in general, it's not useful to have variations of this, it doesn't provide information and causes comparison problems.

## 226 — migrate every existing saved filter to 300 DPI (selected option, 2026-10-15)
> Change all saved filters to 300 DPI

## 227 — group the integrated overview by BW, indexed color and full color (verbatim excerpt, 2026-10-16)
> In the table "Overview — final complete-file bytes" Make three sections to clarify the analysis, the first will be all BW algorithms, then indexed colors, then full colors algorithms.  It's generally expected that JPBIG2 will be the best for BW, then maybe Brotli or layered JBIG2 for low pallettes, then JPEG, JPG2000 for full color.

## 228 — one continuous overview table with unnumbered divider rows (verbatim, 2026-10-16)
> No, put in a same continuous table with a row as the divider, no numbering.  Merged cells if md permits, if not, just blank cell except for the far left one with the title.

## 229 — benchmark every row, including redundant no-image cases (verbatim, 2026-10-16)
> please drop that rule, every row gets benchmarked, even if redundant, this is also a sanity check on the benchmarks.

## 230 — rename the project to PDF Minify (verbatim, 2026-10-16)
> Also, rename this project to "PDF Minify", rename anything in the repo and I will rename the repo itself later.  Also, why is there a dir that restates pdf_minimalist, why not app, source, code, or something like that?

## 231 — add a sixth representative complete-document benchmark (verbatim, 2026-10-16)
> also, add models-nasa-kepler.pdf as another Representative class, or within an existing class, or suggest another alternative to add a sixth case that covers a broad spectrum.  I have been using that one as a good test case, but maybe you have other suggestions?

## 232 — explicit Otsu group label; native preservation implied without FFPR (verbatim, 2026-10-16)
> "Black and white (BW)" rename to "Black and white (BW + Otsu)" and remove the "; keep native", this is implied by no FFPR.

## 233 — JBIG2 end-to-end non-regression; non-JBIG2 BW benchmark input (verbatim, 2026-10-16)
> that is a good test case for the full flow, the flow should never make a JBIG2 worse, document this as an issue and a test case to use to fix and check for regressions.  Also, this is NOT a good test case for this table, find another BW pdf that is NOT already JBIG2, or else the results are meaningless.

## 234 — dedicated JBIG2 developer guide and optimization exploration TODO (verbatim, 2026-10-16)
> Add a JBIG2 dev doc, add documentation relevant to the algo and add a TODO that we need to explore other JBIG2 optimization features and detail them

## 235 — repair the JBIG2 same-DPI preparation bug (verbatim, 2026-10-16)
> Please fix that bug

## 236 — approve ten complete benchmark-row removals (verbatim excerpt, 2026-10-16)
> ok, proceed.

## 237 — apply redundant-row removal consistently to focused tables (verbatim, 2026-10-16)
> Obviously, if a row was considered redundant in the overview, is should also be dropped from the focused view, or else the statement that the row has low added values was incorrect.

## 238 — isolate lossless optimization effects with measured baseline comparisons (verbatim, 2026-10-16)
> Your analysis is not well structured.  When an optimization does not change the final pdf visualization, like PNG prediction and optimized residual streams, split them out into their own tables to make single changes tests, this is the scientific method.  So for all the combination where PNG optimization is relevant, make a new table, with the rows for each of the baseline (eg "Indexed 5 colors + Brotli", etc) and the six columns, but the result size in the table will be for the "PNG prediction" version and beside it put the % improvement over the baseline (eg -1.2%, or +2.5%, etc)  The -% is good.  DO you follow?

## 239 — only measured complete-PDF sizes (verbatim, 2026-10-16)
> There is no "predicted PDF bytes", no predicted.  Only measured.  Why did you say predicted?

## 240 — review PNG prediction before other optimization tables (verbatim, 2026-10-16)
> Start with only "PNG prediction" so that I can review an make sure it is correct.

## 241 — full-suite trigger is code changes, not documentation or publication (verbatim, 2026-10-16)
> This “full suite before every ship” is incorrect.  Full suite of test after code changed, not documentation changes, right?

## 242 — expand PNG coverage and build the next controlled experiment (verbatim, 2026-10-16)
> Add more combos with PNG Prediction testing, but so far, it looks like it's never beneficial with Brotli.    Then plan and build the next binary benchmark experiment table.

## 243 — percentage-only PNG-prediction effect table (verbatim, 2026-10-17)
> also, remove the sizes from the binary test table "PNG prediction — measured effect versus baseline"

## 244 — annotate Brotli PNG results and assess overall winners (verbatim, 2026-10-17)
> In that table, underline all the word "Brotli", as none were improved by PNG prediction, thus Brotli makes PNG prediction obsolete, right?    Also, what is the next binary experiment we can do?

> Also, are there any cases where the "PNG prediction" version is the smallest of all algorithms?  This would tell use if "PNG Prediction" is completely superceeded.

## 245 — compare Zopfli treatment against Brotli baseline; short table labels (verbatim, 2026-10-17)
> It looks like Brotli is a bit bigger than Zopfli for single page documents, then Brotli is better for multiple pages.  Is this always true?  Can you make a new section and new table comparing Brotli as basline, with Zopfli as treatment?  Also, replace all Zopfli-flate in table with just Zopfli, is there any reason to keep the long version "Zopfli-flate" in the tables?  Does it permit distinction against anything else with same name?

## 246 — restrict the comparison to FFPR with specialized codecs; explain regressions (verbatim, 2026-10-17)
> I mean with FFPR and modern compressions, like J* of course, other than that, the page would have additional information that is expected to be compressible.  I am looking for the scenarios where Brotli is worse, which is not the null hypothesis, since it is supposed to be better.  And when worse is found, why?

## 247 — leave zero PNG-effect percentages unbolded (verbatim, 2026-10-17)
> Don't bold 0% in the "PNG Prediction" table please

## 248 — standardize percentage precision and order the comparison tables (verbatim, 2026-10-17)
> Decide on a stanard number of decimals for percentage diff.  Let's use 2 decimals.  And move the brotli table after png.

## 249 — leave all rounded-zero percentage changes unbolded (verbatim, 2026-10-17)
> if it rounds to 0.00%, no bold please

## 250 — treatment titles directly above effect tables (verbatim, 2026-10-17)
> You need to put a table title directly before those two table that clearly and concisely states the experimental treatment in the cells of the table.  Show me here first for headers, the I will confirm.

> ok, proceed

## 251 — opt-in Brotli declaration and Brotli-only compatibility control (verbatim, 2026-10-17)
> Also, we should remove the "extension specification" for all the tests and filters by default, but add it as a compatibility option when Brotli is selected.  Only show that option for Brotli, which is different than our existing pattern to always show the option by grey it out when not applicable.

## 252 — explicit Compatibility label (verbatim, 2026-10-17)
> Mark that option as "(Compatibility)" for clarity.

## 253 — Brotli help in tooltips; standard tooltip convention (verbatim, 2026-10-17)
> Remove the text under Brotli, put that in a tooltip please, plan a standard tooltip as per modern GUI best practices

## 254 — remeasure the tables after changing the Brotli default (verbatim, 2026-10-17)
> Did you redo the tables?  Why is brotli still larger?

> Yes

> You have to rerun everything brotli...

## 255 — best Zopfli/Brotli choice for non-image PDF streams (verbatim, 2026-10-17)
> ok, this is fine the way it is, can we add an algorithm that chooses the best for each page?

> Not good, because we are not automatically selecting all options, just the pdf outer data (not images), right?

> Best (Zopli/Brotli) In the "PDF Streams:" dropdown please.

## 256 — Best includes packed-image streams, not J* payloads (verbatim, 2026-10-17)

> Why limite to non-image streams?  Don't they also compress PNGs?  Please explain.

> I don't think we will be supporting anything other than the three J*.  Why are you mentionning "CCITT fax images", did we not rule that all images get converted?

> yes, but those would be compressed with Best, but J* are excluded.

## 257 — make Best the setting for all app filters (verbatim, 2026-10-17)

> Change all the app filters to "Best" please

## 258 — Best-only overview and separate compressor experiment (verbatim, 2026-10-17)

> Why do we still have rows in the main table that compare Zopfli with Brotli?  Move all those to the specialized binary table and only use the new "Best" algorithm for the main table, document in the section, but not in the table directly, because that would make the table too noisy, the specialize binary experiment table will be the reference for that information.

## 259 — visible fixed controls and PNG-prediction decision tree (verbatim, 2026-10-17)

> you can leave this always expanded, no drawer to open "Show fixed Zopfli/Brotli sizes and the Classic-Flate reference".  Also, we now have a decision tree for PNG prediction, right, please document, it depends on brotli and image type.  Add it to the top section of "PNG prediction — measured effect versus baseline" conclusion/resuts.  Right?

## 260 — jointly choose image predictor and lossless encoder (verbatim, 2026-10-17)

> Also, can it happen that the images is native stream AND that best chooses zopfli?  Regardless, in the decision tree, when zopfli, we should automatically test PNG Prediction on and off when choosing best?  And also have an option for PNG prediction for when zopfli is chosen, have On/Off/Best.  For Best Zopfli/Brotli, it would also always try PNG Prediction Best.  or are there cases where it's guaranteed useless, eg, no PNGs = no need?

## 261 — show both predictor states for both Best encoder branches (verbatim, 2026-10-18)

> Ok, then leave it always tested for both, fix your tree to show the test for both.

## 268 — refresh every affected benchmark and document (verbatim, 2026-10-19)

> ok, update all benchmarks and docs, and run the updated benchmarks that have not been done yet.

## 272 — JPEG2000 quality equivalence to JPEG q75 (verbatim, 2026-10-19)

Source: designer message in the session of 2026-10-19; exact text.

```text
I had a less skiled worker program this app and documentation, but I am not sastisfied.  The first problem I have is that it was not able to derive a proper quality setting equivalence for JPEG2000 that matched JPG q75 (I think that is what I choose).  This is important for the benchmarks, because we need to set all settings as similar as possible and also follow what users expect and understand (eg q=75 quality setting, not multiple different complex settings), so that the benchmarks mean something and so that users can know what they are setting?  There is already some research done in the repo, please review and do me research if you feel that is required.
```

## 273 — developer guidelines and verbatim record quality (verbatim, 2026-10-19)

Source: designer message in the session of 2026-10-19; exact text.

```text
the developper guidelines were not well done neither.  My verbatim words should be exact, but the corpus is a mess and the verbatim recordings might not be well organized.
```

## 274 — equivalence estimate and 4:2:0 question (verbatim, 2026-10-19)

Source: designer message in the session of 2026-10-19; exact text.

```text
So you have equivalence or can you estimate it?  And do you think we should use "4:2:0" also by default and for benchmarks?
```

## 275 — use case: smaller PDFs for most users (verbatim, 2026-10-19)

Source: designer message in the session of 2026-10-19; exact text.

```text
I already ruled the use case, this is for making pdfs smaller, thuse lossless or super high quality images are not a concern, we want something simple for most users.
```

## 276 — colour sampling must match between the codecs (verbatim, 2026-10-19)

Source: designer message in the session of 2026-10-19; exact text.

```text
Well if if "4:2:0" matches a lower Q for JPEG2000, then that is not good, we should keep it was it was before, matching JPEG200, or reducing JPEG2000 color setting to match jpg  4:2:0, no?
```

## 277 — option 2 approval (verbatim, 2026-10-19)

Source: designer message in the session of 2026-10-19; exact text.

```text
Yes, option 2 please and document properly.
```

## 278 — standard packages only; JPEG settings follow JPEG2000 (verbatim, 2026-10-20)

Source: designer message in the session of 2026-10-20; exact text.

```text
Don't change standard packages, if you can't change JPEG2000, adjust the JPG settings to match.
```

## 279 — documentation structure: rulings first, present tense, recurring traps only (verbatim, 2026-10-20)

Source: designer message in the session of 2026-10-20; exact text.

```text
collect the most important top level design rulings and design intents, varbatim, to the top section of the design document.  Each dev doc should have a first sections with contains the relevant rulings, etc.  Each page should also have a section with historical change logs ONLY for mistakes/changes that have a chance of recurring, eg design traps, of failed attempts and the reason, we onle keep current present tense documentation, UNLESS it's a past mistake that can inform current and future work to avoid past mistakes.  If the mistake was trivial and because the worker did NOT follow canon or rulings, or drifted, we do not document, the git historical keeps a record naturally.
```

## 280 — documentation rework: reviewed by hand, iterative, principles then compression docs (verbatim, 2026-10-20)

Source: designer message in the session of 2026-10-20; exact text.

```text
I would rather you don't use a tool, you should be reviewing and think of each one, but you can use a tool for copying precisely, once you have read and analyzed and made decisions.  I don't want a full refactor now, we will work iteratively and opportunistically, start with the most important current design principles please.  Also, after the top level precinciples, work on the compression docs, since we are working on that now.  These are also a mess.
```

## 281 — compression docs: one design page, one benchmark page (verbatim, 2026-10-20)

Source: designer message in the session of 2026-10-20; exact text.

```text
I think the compression docs should be organized as the first one being for the compression design, high level, and another with the compression benchmarks.  Compression benchmarks should be mostly focused on the integrated final size, and then binary experiment benchmarks, those that I have guided closely follow better my design intent and follow proper experimental treatment design, the others that predate are somewhat a mess.  do you see any need for any other compression related documents?  Or should we have other splits/docs for this?
```

## 282 — publisher scripts update only measured numbers; tables and text curated by hand (verbatim, 2026-10-20)

Source: designer message in the session of 2026-10-20; exact text.

```text
ok, as you suggest, but the scripts should only be updating the benchmarks, not various texts in the file, right?  Maybe the benchmark results on the matching line specifically?  Thus you curate the tables manually?
```

## 283 — ID tags on benchmark table rows for exact matching (verbatim, 2026-10-20)

Source: designer message in the session of 2026-10-20; exact text.

```text
can you put id tags on the lines to ensure full match, even if the row description is short and not necessarily unique across the page, or md doesn't provide this?
```

## 284 — benchmark JPEG2000 at the single setting that looks like JPEG q75 (verbatim, 2026-10-20)

Source: designer message in the session of 2026-10-20; exact text.

```text
Ok, so a single setting is the correct direction, however, for the purpose of out benchmarking, we have to choose a single quality setting that provides the same visual results as jpg.  The reasoning is simple, if jpg q75 provides a certain compression and quality, then the newer J2K is expected to provide a smaller (or in the absolute worst case, the same size) file for the same visual quality level.  This is very simple and basic, I should not have to explain this.  Or else, benchmarks and a newer compression algorithm has no value.
```

## 285 — expectation that JPEG2000 improves on JPEG (verbatim, 2026-10-20)

Source: designer message in the session of 2026-10-20; exact text.

```text
what is the big picture?  Is J2K generally better then JPG?  All things equal?   This is the assumption since it is newer, there would be no point in having a newer algorithm that does not provide improvements.
```

## 286 — question: JPEG2000 on letters (verbatim, 2026-10-20)

Source: designer message in the session of 2026-10-20; exact text.

```text
should J2K have better results on letters?
```

## 287 — no automatic Best between JPEG and JPEG2000; keep them comparable in benchmarks (verbatim, 2026-10-20)

Source: designer message in the session of 2026-10-20; exact text.

```text
Sounds like we cannot be opinionated on the JPG/J2K for now, so let's just keep them as comparable as possible in the benchmarks and we will not have an automatic Best option for these.
```

## 288 — mini caption's last line cut off; look at the GUI results (verbatim, 2026-10-13)

Source: designer message in the session `ses_ed9c28122ffe8V7aTCnj1ue5w6` (2026-10-10 to 2026-10-13), sent just before §139 and not logged at the time; copied exactly from its export on 2026-10-20. Subject (worker text, not designer words): the last caption line under each strip mini, the size, was cut off at the bottom.

```text
Now, the last row of the text is trucated by the view, don't you see this?  This is terribly bad!  Are you even looking at the GUI results?  
```

## 289 — scrub means remove completely, with no reference or cleanup log (verbatim, 2026-10-20)

Source: designer message in the session of 2026-10-20; exact text.

```text
squash, commit and push.  Then review the docs for additional useless chatter that the previous worker kept, list me the top 10 useless chatter that we can scrub from the docs.  Also, when I use the word scrub, that means completely remove, and remove reference, and not log that is was cleaned.  The only history that would remain is in the git history.
```

## 290 — unclear-source entries: delete when superseded or reconfirmed by clear rulings (verbatim, 2026-10-20)

Source: designer message in the session of 2026-10-20; exact text.

```text
ok, for Item 9, Item 10.  For option 1, clean up if you have superceding rulings that override old ones that are not clear about the source, same for one that have been reconfirmed by clear more recent rulings, you can delete the old duplicate unclear source ones.  The rest, you can leave as unclear source and clear when new rulings come in.  Ok for option 2 JBIG2 as you suggest.  Then do the analysis of the next document carefully, one at a time.  You can also squash, commit and push
```

## 291 — squash only unpushed commits, by theme; keep pushed history (verbatim, 2026-10-20)

Source: designer message in the session of 2026-10-20; exact text.

```text
Why forced push, I want to keep some history, when I say squash and push, that means to squash the commits since the last commit that was pushed to origin, to avoid noisy commit history.  The commits should be squashed and pushed by theme/fix/batch.
```

## 292 — never credit AI workers as co-authors or in project text (verbatim, 2026-10-20)

Source: designer message in the session of 2026-10-20; exact text.

```text
Also, put an important memory, like in taskcoach, that we never put the workers as co-authors, or is that in the dev guidelines?  Look in sister taskcoach repo.
```

## 293 — describe the purpose, not the techniques (verbatim, 2026-10-20)

Source: designer message in the session of 2026-10-20; exact text.

```text
start with PDF Minify: Make pdf smaller ... avoid technical references, the techniques are for an objective.  make pdfs smaller using a variety of filters and compression algorithms and techniques with extensive previews giving you a quick overvew of the visual effects of the compression and the size... etc.  This is the idea, it should have already been clear from my rulings, make a good description and update the rulings, because the two are closely linked.
```

## 294 — application icon: column 5, row 4 of icons/test2.png (verbatim, 2026-10-20)

Source: designer message in the session of 2026-10-20; exact text.

```text
Also, I want to use the Icon col 5, row 4 from     pdf-minimalist/icons

/test2.png.
```

## 295 — show the application icon in the README (verbatim, 2026-10-20)

Source: designer message in the session of 2026-10-20; exact text.

```text
Can you put this in the readme?
```

## 296 — README for users, like Task Coach; docs index in docs/README.md (verbatim, 2026-10-20)

Source: designer message in the session of 2026-10-20; exact text.

```text
And the readme has irrelevant technical details, like debounce, local run, etc.  I want something like taskcoach, we will have the install packages/platforms, and a ref to the docs index, which should be a readme in the docs dir, right?
```

## 297 — license: AGPL-3.0-or-later (verbatim, 2026-10-20)

Source: designer message in the session of 2026-10-20; exact text. It approves
the recommendation it quotes.

```text
ok, as you reccommend "I recommend AGPL-3.0-or-later."
```
