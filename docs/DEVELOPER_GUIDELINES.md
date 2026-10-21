# Developer guidelines — PDF Minify

## Rulings (verbatim)

Exact designer text from `DESIGNER_VERBATIM.md`. Text outside the fenced
quotes is not the designer's.

### Authority and documentation

**§9** (2026-10-09)

```text
Put all my comments verbatim in a design md doc, make a docs dir.  make a dev md doc with guidance, including to keep all my comments verbatim.  I want to see a list of preset optimization options, like photo filters on a camera with a smaller version of previews, and when I click on one, the main doc has original and preview (optmized side by side, vertically or horizontally, same for the filter thumbnails, all would be choosable as menu view options.
```

**§11** (2026-10-09)

```text
design.md, designer rulings section, verbatim.  In the docs, always call the operator/user the designer.
```

**§19** (2026-10-09)

```text
yes, correct docs, don't ask, docs should be all updated first, then dev work.  Docs lead the decisions, rulings, design intent.  Everything else follows.
```

**§16** (2026-10-09)

```text
no checkbox for doto list, put item in full detail, when completed, stub, cross ref with final docs that implement it and strikethrough.  If dropped, we can have a doc with dropped ideas and log them for historical reference with reasons.  Once we do work, we don't want to redo the work and knowledge.
```

**§216** (2026-10-15)

```text
Move the TODO.md to the docs dir please also
```

**§218** (2026-10-15)

```text
commit/push is not a todo/issue neither, you can scrub/drop those, if any, from the docs.  Do you see anything else that is not design related?  Like requesting to run the app or whatever else that has no added value to the docs.
```

**§220** (2026-10-15)

```text
ok, then leave in the tables as it was.  Also, clean this up, we should NOT have typo correction discussions in the docs.
```

**§273** (2026-10-19)

```text
the developper guidelines were not well done neither.  My verbatim words should be exact, but the corpus is a mess and the verbatim recordings might not be well organized.
```

**§279** (2026-10-20)

```text
collect the most important top level design rulings and design intents, varbatim, to the top section of the design document.  Each dev doc should have a first sections with contains the relevant rulings, etc.  Each page should also have a section with historical change logs ONLY for mistakes/changes that have a chance of recurring, eg design traps, of failed attempts and the reason, we onle keep current present tense documentation, UNLESS it's a past mistake that can inform current and future work to avoid past mistakes.  If the mistake was trivial and because the worker did NOT follow canon or rulings, or drifted, we do not document, the git historical keeps a record naturally.
```

**§280** (2026-10-20)

```text
I would rather you don't use a tool, you should be reviewing and think of each one, but you can use a tool for copying precisely, once you have read and analyzed and made decisions.  I don't want a full refactor now, we will work iteratively and opportunistically, start with the most important current design principles please.  Also, after the top level precinciples, work on the compression docs, since we are working on that now.  These are also a mess.
```

**§289** (2026-10-20)

```text
squash, commit and push.  Then review the docs for additional useless chatter that the previous worker kept, list me the top 10 useless chatter that we can scrub from the docs.  Also, when I use the word scrub, that means completely remove, and remove reference, and not log that is was cleaned.  The only history that would remain is in the git history.
```

**§290** (2026-10-20)

```text
ok, for Item 9, Item 10.  For option 1, clean up if you have superceding rulings that override old ones that are not clear about the source, same for one that have been reconfirmed by clear more recent rulings, you can delete the old duplicate unclear source ones.  The rest, you can leave as unclear source and clear when new rulings come in.  Ok for option 2 JBIG2 as you suggest.  Then do the analysis of the next document carefully, one at a time.  You can also squash, commit and push
```

### Issues and acceptance

**§90** (2026-10-10)

```text
Also, when I choose a to be processed filter to the far right, when other fitlers are processed to the left, reprocessing starts onthe left filters, this is also incorrect.  Add each of my notes to a BUGS.md doc, in a numbered list and cross only once I have comfirmed that they are fixed.  Look back at my past complaints and add them to the bugs list please.
```

**§147** (2026-10-13)

```text
Ok, this is good, you can mark these issues fixed, confirmed by me.  I don't know if the worker was self-marking issues fixed without my confirmation, but try to have a marking that indicates that I explicitly confirmed it fixed and the date.  There are still other DnD issues, so mark this ghost as fixed.   Is transparency at 75% now also?
```

### Testing, running and logging

**§59** (2026-10-10)

```text
please complete your work, don't stop half compelted.  Also make a full test suite please and run each time please.
```

**§241** (2026-10-16)

```text
This “full suite before every ship” is incorrect.  Full suite of test after code changed, not documentation changes, right?
```

**§62** (2026-10-10)

```text
run, always run after a new build, kill the existing one
```

**§137** (2026-10-13)

```text
Add canon instructions that you have to take screenshots (in a virtual frambuffer, same for the tests) and view the formats, layouts and other work you do to see if they make visual sense and follow modern best practices, or else you are just programming blind for GUI work!
```

**§14** (2026-10-09)

```text
The app should log everything important to the stdout so that you can run and review what happened from the log.  Also, have a --debug mode that dumps more so you can rune and evaluate issues and problems as required.  This goes in development guidelines, as it is not a ui nor feature design issue.
```

**§102** (2026-10-10)

```text
'PySide6.QtGui.QPalette' object has no attribute 'Mid', BUT you should see this in the log automatically, no?  This was in a popup.
```

### Commits and attribution

**§291** (2026-10-20)

```text
Why forced push, I want to keep some history, when I say squash and push, that means to squash the commits since the last commit that was pushed to origin, to avoid noisy commit history.  The commits should be squashed and pushed by theme/fix/batch.
```

**§292** (2026-10-20)

```text
Also, put an important memory, like in taskcoach, that we never put the workers as co-authors, or is that in the dev guidelines?  Look in sister taskcoach repo.
```

### License

**§297** (2026-10-20)

```text
ok, as you reccommend "I recommend AGPL-3.0-or-later."
```

Read this before touching code. The designer's rulings are in
`DESIGNER_VERBATIM.md`, [00_OVERVIEW.md](00_OVERVIEW.md) maps every page, and
requirements are in [TODO.md](TODO.md).

## 0. General guidelines (designer rulings — always in force)
- The designer is the sole authority. In all docs, call them "the designer".
- Designer words are preserved verbatim (see §1). Technical explanations live
  outside the quotes; omit editorial correction commentary (§220).
- `TODO.md` tracks substantive project requirements, defects and design work,
  not every conversational instruction (§218). IDs are NEVER renumbered,
  reordered or reused. No checkboxes. Open items carry full detail; completed
  items are stubbed — request struck through, stub summary, cross-refs to the implementing
  docs/code. Dropped ideas move to `DROPPED.md` with reasons + revisit
  conditions. Knowledge is referenced, never redone.
- §§216/218 place the log in `docs/TODO.md` and limit documentation to durable
  project value. Do not log one-off execution/publication commands, bare
  run/resume/status prompts, temporary scheduling or per-session handoffs as
  TODOs, issues or design rulings. Preserve real requirements, defect reports,
  acceptance and lasting developer rules; excerpt mixed requests verbatim
  without the routine chatter. Explicit removal overrides preservation:
  delete rather than re-archive/requote, with no renumbering or ID reuse.
  Keep reproducible benchmark/test evidence and source-version identifiers,
  not a diary of process IDs, startup timestamps or routine delivery events.
- **Scrub** (§289): remove the material completely, remove every reference
  to it, and record nothing about the cleanup in any doc, log, TODO or issue.
  Git history is the only record.
- Implementation completion is not designer acceptance (§147). In `issues.md`,
  use `FIXED — DESIGNER CONFIRMED — YYYY-MM-DD` only for an explicit designer
  confirmation, with its verbatim ruling and exact scope. Use the designer's
  local date (America/New_York). Tests or worker assertions never substitute
  for that confirmation. Mixed-scope issues remain OPEN for unconfirmed parts;
  `DONE` in TODO means implementation complete unless confirmation is stated.
- Each page opens with the rulings that govern it, quoted exactly from
  `DESIGNER_VERBATIM.md`, then present-tense documentation, then only design
  traps likely to recur (§279). This file holds the general rules; topic
  rules live on their pages.
- Docs lead: `docs/` is updated FIRST and carries decisions, rulings, and
  design intent; code and everything else follow. When docs and code disagree,
  fix the code to match the docs — or get a new designer ruling. Don't ask
  for direction the docs already give.

## 1. Keep designer comments verbatim — always
- Preserve retained designer quotations exactly in `DESIGNER_VERBATIM.md`;
  do not rewrite their wording or add editorial annotations.
- New substantive designer ruling? Before acting, append it as the next
  numbered entry: one message in a fenced `text` block, with its date and a
  `Source:` line. §218 excludes routine operational chat; do not turn every command
  or housekeeping exchange into a documentation entry.
- §220: do not document typo/spelling corrections, correction logs or mnemonic
  asides. Use correct technical names directly in explanatory prose. Keep
  substantive codec decisions, compatibility evidence and actual defect
  diagnoses; these are not spelling discussions. Explicit cleanup requests
  remove editorial material without re-archiving it or changing retained
  designer quotations.
- Unclear-source entries (§290): entries before §272, except §§139–141,
  cannot be checked against the original messages. When a clear-source
  ruling supersedes or reconfirms one, delete the old entry and point its
  references to the clear ruling; leave the others until new rulings come in.

## 2. Stack & layout (locked unless the designer says otherwise)
- Product identity (§230): display **PDF Minify**, package `pdf_minify`,
  machine/settings/temp slug `pdf-minify`. Keep the flat import-package
  layout. All settings
  access uses `ui_qt/settings.py` and its one-time non-overwriting legacy
  migration. Tests/review runs isolate both namespaces before migration.
  Preserve exact quotes, licensed resources and frozen benchmark provenance;
  keep the actual GitHub remote unchanged until the designer renames it.
- License (§297): PDF Minify is AGPL-3.0-or-later (`LICENSE`), which matches
  PyMuPDF's AGPL-3.0. New dependencies and bundled assets must be compatible
  with it, and bundled assets keep their own notices.
- Python + PySide6 (Qt6) GUI + PyMuPDF pipeline. `core/` = headless, NO Qt imports.
  `ui_qt/` = widgets only. Pure-numpy thresholds.
- REPOSITORY-OWNED: `pdf_minify/`, `tests/`, `tools/`, `docs/`,
  `requirements*.txt`, `.venv/` (git-ignored, via `setup_local.sh`).
- SYSTEM (apt, never vendored): `python3`, `jbig2` and `zopfli`, plus the
  inspection tools `mutool` and `pdfimages`; the Qt runtime comes from the pip
  wheels. Never `sudo pip install`; pip targets `./.venv` only.

## 3. Product rules

Standing rules. Rulings, details and measurements live in the page named on
each line.

**Encoding**
- Use the strongest validated encoder for each representation. Reader
  support is the only trade-off, never encoding speed or dependency
  convenience (§213). A missing or failing selected encoder is a clear error
  that leaves the saved file intact, never a silent fallback or substitution
  (§203). `COMPRESSION.md` (Encoder policy).
- Compression is editable recipe state, never locked by the seed preset: six
  explicit image choices and an independent PDF streams policy, with the
  actual mode persisted through Save/Save As/load (§§203–205). `COMPRESSION.md`.
- BW: Threshold method covers manual Simple (= GIMP Threshold) and automatic
  Otsu (default), Adaptive and Sauvola. JBIG2 is lossless, and each stream is
  decoded and checked before embedding; lossy JBIG2 stays off (§§203/234).
  `COMPRESSION.md`, `JBIG2.md`.
- Every app filter uses **Best (Zopfli/Brotli)** for PDF streams (§257). Best
  covers native and packed BW/indexed image streams, tests PNG prediction off
  and on for eligible image rows, and never recompresses JPEG, JPEG2000 or
  JBIG2 payloads (§§255/256/260). The opt-in Brotli declaration is added only
  when the chosen output uses Brotli (§251). Empty streams stay plain.
  `COMPRESSION.md`, `NATIVE_STREAM_COMPRESSION.md`.
- No JPEG XL inside PDFs: it is not in the PDF specification and viewers
  cannot open it (`DROPPED.md` D1).

**Page preparation**
- FFPR off keeps native text and vector diagrams, with their fonts, geometry,
  colours and opacity, over one combined image canvas; FFPR on flattens the
  whole page (§§127/168–171). Never rasterize native artwork or invent
  glyph-shaped masks. `COMPRESSION.md`.
- Compose original imagery and masks in full colour, resize once to the
  target DPI (default 300; §§180/182/225), then threshold, reduce the palette
  or encode. No second resize and no per-image rewrite. Keep fractional
  source density; never round it up to a whole DPI (§235). `COMPRESSION.md`.
- Native-layer edits go through MuPDF's content filter and lexer, never regex;
  they keep structure-tree ownership and accessibility metadata, and every
  canvas is read from the immutable original (B108–B112, B116).
  `COMPRESSION.md` (Composition rules).

**Lossy quality**
- One Quality control, 0–100 and default 75, drives JPEG and lossy JPEG2000.
  The same number means comparable visual quality through one fixed rule for
  every page (§§272/284), with standard packages only (§278). If the
  encoders or the benchmark pages change, recalibrate and version the
  JPEG2000 mapping. The app never chooses between JPEG and JPEG2000 (§287).
  `LOSSY_IMAGE_QUALITY.md`.

**Benchmarks**
- Report only complete saved PDFs: never estimates, component sums or sizes
  copied from another row (§§222/229/239). Each binary experiment changes one
  named factor against a measured baseline (§238). `COMPRESSION_BENCHMARKS.md`.
- When a setting used by the benchmarks changes, re-measure every affected
  table (§268). Scripts fill only the tagged numbers; tables and text are
  curated by hand (§§282/283). `COMPRESSION_BENCHMARKS.md`.
- A benchmark input must not already use the codec under test (§233). Check
  source `/Filter` values, not extracted file types (B115). `JBIG2.md`.

**Files and flow**
- Every filter runs the real saver once per input and effective recipe;
  preview, minis, size and export all read that saved PDF (§§122/149).
  Selection, zoom, pan, page changes and drag-and-drop never reprocess.
  `FILTER_LIFECYCLE.md`.
- Live edits share one trailing debounce (§183) and mark the filter `*`.
  Leaving a dirty filter offers Save / Save As… / Discard / Cancel; a
  successful Save As creates and selects its copy (§189). `FILTER_LIFECYCLE.md`.
- Never overwrite the input; the default output name is `<name>.reduced.pdf`.

## 4. UX rules (the designer's picky-UI standard)
- Both panes show the actual saved PDFs with no PDF-content anti-aliasing,
  image interpolation or extra smoothing; zoom redraws native geometry at
  device resolution (§§172–175). Render only visible regions; saved files
  stay immutable.
- Viewer input: wheel scrolls, Ctrl+wheel zooms to the cursor, drag pans,
  PgUp/PgDn move by page, and a new file fits on load. No jank on old LXDE
  hardware.
- Escape cancels an active drag, dialog or PDF export; otherwise it does
  nothing and is never Undo (§85). The UI stays responsive, and closing the
  window cancels filtering asynchronously.
- PDF drag-and-drop from the file manager (`text/uri-list`) with an Open
  fallback; the window works at 1024×600.
- Layout, spacing and mini progress follow `UI_LAYOUT.md`; action icons and
  the Icon Lab follow `ICONS.md` and `ICON_LAB.md`.

## 5. Workflow
- Run `./test.sh` (the full suite) after code-affecting changes, including
  tests, dependencies, build or configuration that affect execution;
  documentation-only edits need the relevant documentation checks (§241,
  `TEST_PLAN.md`).
- After every new build, stop the running app, confirm its desktop GUI PID and
  process group have exited, and relaunch it in a separate session with
  `setsid --wait ./run.sh …` (§62). Supervisor exit status alone does not
  prove the app exited. Confirm `window shown` and an applied preview in
  `${TMPDIR:-/tmp}/pdf-minify/pdf-minify.log`. Never leave the designer on a
  stale build, but respect an instruction to leave the app closed, and never
  choose Save or Discard for the designer to automate a restart.
- Commits (§291): "squash and push" squashes only the local commits made since
  the last commit pushed to origin, one commit per theme, fix or batch, then
  pushes normally. Never amend, rebase or force-push commits already on origin.
- No AI attribution (§292): never name AI tools or agents, or credit them, in
  commit messages (no `Co-Authored-By` or session trailers), code comments,
  docstrings, documentation, issues, pull requests or any other project-facing
  text. The git author is the designer; let the work speak for itself.
- `python3 tools/check_env.py` then `./.venv/bin/python tools/check_env.py`.
- Qt smoke: `QT_QPA_PLATFORM=offscreen ./.venv/bin/python -c "...MainWindow..."`.

## 5b. Screenshot canon (designer ruling §137 — GUI work is never blind)

- After EVERY UI-visible change: capture offscreen screenshots (virtual
  framebuffer — `QT_QPA_PLATFORM=offscreen`, the same environment the
  tests run in) via `tools/shot.py` into `./.tmp/`, and actually VIEW the
  PNGs — formats, layouts, spacing, alignment, readability, theme
  behavior. Never ship GUI work without looking at it.
- Review checklist on every shot: does the layout match `UI_LAYOUT.md`?
  Text readable at real sizes (no clipping, no pale-on-pale)? Spacing and
  alignment even? Selection/focus/hover states theme-clean (no baked
  chrome fighting the style)? Drop/drag affordances visible? Compare
  against the previous shot for regressions, not just the new feature.
- Inspect changed regions at 1:1 pixels, never only the downscaled whole
  window — downscaling blends away exactly the defects being hunted
  (unreadable captions, stray accent lines).
- Tests assert what screenshots cannot pin cheaply, and shots cover what
  tests cannot: icons render non-blank, geometries hold, transparency and
  elision behave. Both, every time.
- Viewer layout changes additionally check one/two/many occupied pages,
  both zoom initiators, exact-fit column boundaries, resize and stacked panes
  (§§164/165). `tools/shot.py` captures real-file examples and 1:1 original/
  preview panes plus their minis; its settings are isolated from the designer's.
- Window/header sizing changes also run `tools/resize_smoke.py` offscreen at
  100% and `QT_SCALE_FACTOR=2`: time the wide-to-640px transition over ten
  seconds, keep both panes equal, verify no delayed divider drift and actual
  horizontal overflow after squeezing the panel. Capture/view full windows
  and 1:1 headers/panels. Test helpers must use isolated settings; separate
  sandbox namespaces can both report PID 2, so tools owning the canonical PID
  artifact root run sequentially rather than adding test-only production IDs.
- Drag changes additionally require a real native X11 gesture via
  `xvfb-run -a ./.venv/bin/python tools/drag_smoke.py` (requires xdotool).
  It checks the rendered 75% ghost, drop position, selection, and immediate
  visible caption numbering (actual X11 window pixels) over the
  strip, previews, controls, and below the strip, plus Escape cancellation.
  It also covers an 11-filter layout, sub-threshold movement, repeated tail
  moves and clicks after reordering (row count, UUID set, no filtering,
  caption pixels), and any Qt slot exception fails it. A dirty-mini native
  click, modal Escape and the Revert button must keep both filters edited on
  Cancel, keep files and dirty state intact, and reuse the saved file on
  Revert without work.
  View the captured `.tmp/drag-*.png` images. Settings are isolated.
- Filter-lifecycle changes additionally run
  `QT_QPA_PLATFORM=offscreen ./.venv/bin/python tools/filter_smoke.py`; view
  `.tmp/filter-*.png`, including the real unsaved-dialog capture. It verifies
  prepared-file reuse, exact sizes, dirty state, and Discard file ownership.
  Include the real mini-click Escape capture, explicit Discard Changes label,
  and enabled/disabled standard Revert icon (§197) and retained selection.

## 6. Run-and-review logging (§14)
- The app logs everything important to stdout: startup, open (path + page count),
  preset selection, preview renders (page/strategy/T/size), save params,
  job progress/completion, cancel requests, view-mode changes, warnings.
- `--debug` (`python -m pdf_minify --debug`) raises logging to DEBUG and dumps
  diagnostics: Python/PySide/Qt/fitz versions, cwd, argv, per-stage preview
  timings (render/threshold ms), per-page job progress.
- Default (no flag) stays INFO: quiet enough to run, complete enough to review
  what happened from the log alone.
- Errors and tracebacks reach the log as well as any popup (§102).

## 7. Certified platform and packaging (§176)

- `PLATFORMS.md` records the actual tested OS/architecture/desktop, interpreter,
  Qt/PDF/native-tool versions, certificate date and limits. Certify the measured scope,
  not every version admitted by broad source requirements or another project's
  supported platforms. Platform verification is not designer issue acceptance.
- `PACKAGING.md` adapts the reviewed sibling/upstream Task Coach packaging
  patterns to Qt/PyMuPDF. Keep runtime, build and validation dependencies
  separate. Existing source-runtime certification does not certify installers.
- Proposed distributions must pass clean native installed-artifact gates
  (including multiprocessing, native tools, temp ownership and exact display)
  before promotion. A documentation request does not authorize installing
  packaging tools, changing other projects, publishing or pushing releases.

## Design traps and failed attempts

- **Self-marking issues fixed.** Worker checks were recorded as fixes the
  designer had not confirmed (§147). Only a dated explicit confirmation closes
  an issue.
- **Paraphrased verbatim entries.** Collapsed spaces, merged messages and
  shortened text made the log unreliable (§273). Copy each message exactly,
  one per entry, with its source.
- **Docs turned into run logs.** Dated test counts, "captures viewed" notes and
  changelogs buried the rules (§§279/289). Git history keeps that record.
- **Inventing beyond the request.** A question or a narrow request became a
  broader feature: custom rename artwork from a question about a standard
  icon (§120), and a session-history store nobody asked for (§153).
- **Rewriting pushed history.** Amending and force-pushing commits already on
  origin replaced their history (§291). Squash only unpushed commits.
