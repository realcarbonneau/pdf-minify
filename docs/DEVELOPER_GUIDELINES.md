# Developer guidelines — PDF Minify (full)

Read this before touching code. Source of truth for designer intent:
`DESIGNER_VERBATIM.md`. Request tracker: [TODO.md](TODO.md) (this directory).
Root docs: `00_OVERVIEW.md`, `ARCHITECTURE.md`.
Entry point at repo root: `../README.md`. The request log and analysis docs
live in this dir (`TODO.md`, `DESIGN.md`, `DROPPED.md`, `DESIGNER_VERBATIM.md`, …).

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
- This file carries the designer's general rulings; `DESIGN.md` carries the
  design rulings with verbatim quotes. Both stay in sync with
  `DESIGNER_VERBATIM.md`.
- Docs lead: `docs/` is updated FIRST and carries decisions, rulings, and
  design intent; code and everything else follow. When docs and code disagree,
  fix the code to match the docs — or get a new designer ruling. Don't ask
  for direction the docs already give.

## 1. Keep designer comments verbatim — always
- Preserve retained designer quotations exactly in `DESIGNER_VERBATIM.md`;
  do not rewrite their wording or add editorial annotations.
- New substantive designer ruling? Append it verbatim (numbered, dated) before
  acting. §218 excludes routine operational chat; do not turn every command
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
  machine/settings/temp slug `pdf-minify`. Keep the flat import-package layout;
  do not add installation/layout work to a branding rename. All settings
  access uses `ui_qt/settings.py` and its one-time non-overwriting legacy
  migration. Tests/review runs isolate both namespaces before migration.
  Preserve exact quotes, licensed resources and frozen benchmark provenance;
  keep the actual GitHub remote unchanged until the designer renames it.
- Python + PySide6 (Qt6) GUI + PyMuPDF pipeline. `core/` = headless, NO Qt imports.
  `ui_qt/` = widgets only. Pure-numpy thresholds.
- REPOSITORY-OWNED: `pdf_minify/`, `tests/`, `tools/`, `docs/`,
  `requirements*.txt`, `.venv/` (git-ignored, via `setup_local.sh`).
- SYSTEM (apt, never vendored): `python3`, `jbig2`, `mutool`, `pdfimages`,
  Qt6 C++ libs. Never `sudo pip install`; pip targets `./.venv` only.

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

## 6. Run-and-review logging (designer ruling — process, not UI/feature design)
- The app logs everything important to stdout: startup, open (path + page count),
  preset selection, preview renders (page/strategy/T/size), save params,
  job progress/completion, cancel requests, view-mode changes, warnings.
- `--debug` (`python -m pdf_minify --debug`) raises logging to DEBUG and dumps
  diagnostics: Python/PySide/Qt/fitz versions, cwd, argv, per-stage preview
  timings (render/threshold ms), per-page job progress.
- Default (no flag) stays INFO: quiet enough to run, complete enough to review
  what happened from the log alone.

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
