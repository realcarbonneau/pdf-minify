# Developer guidelines — pdf-minimalist (full)

Read this before touching code. Source of truth for designer intent:
`DESIGNER_VERBATIM.md`. Request tracker: `../TODO.md` (repo root).
Root docs: `00_OVERVIEW.md`, `ARCHITECTURE.md`.
Entry points at repo root: `../README.md`, `../TODO.md`. All other analysis
docs live in this dir (`DESIGN.md`, `DROPPED.md`, `DESIGNER_VERBATIM.md`, …).

## 0. General guidelines (designer rulings — always in force)
- The designer is the sole authority. In all docs, call them "the designer".
- Designer words are preserved verbatim (see §1). Corrections and interpretations
  live OUTSIDE the quotes, never inside them.
- `TODO.md` tracks EVERY designer request: numbered append-only, NEVER renumbered
  or reordered. No checkboxes. Open items carry full detail; completed items are
  stubbed — request struck through, stub summary, cross-refs to the implementing
  docs/code. Dropped ideas move to `DROPPED.md` with reasons + revisit
  conditions. Knowledge is referenced, never redone.
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
- NEVER fix the designer's spelling/grammar inside `DESIGNER_VERBATIM.md`.
  Typos (`targetting`, `remeber`, `lok`, `optmized`, `alll`, `alot`, double/triple spaces)
  are intentional preservation, not bugs.
- New designer note? Append it verbatim (full text, numbered, dated) before acting.
- Corrections (JDIC2→JBIG2, JXL dropped) go in the "Corrections log" section or in
  code/docs OUTSIDE the quotes — never by editing the quotes.

## 2. Stack & layout (locked unless the designer says otherwise)
- Python + PySide6 (Qt6) GUI + PyMuPDF pipeline. `core/` = headless, NO Qt imports.
  `ui_qt/` = widgets only. Pure-numpy thresholds (no hard OpenCV dep).
- REPOSITORY-OWNED: `pdf_minimalist/`, `tests/`, `tools/`, `docs/`,
  `requirements*.txt`, `.venv/` (git-ignored, via `setup_local.sh`).
- SYSTEM (apt, never vendored): `python3`, `jbig2`, `mutool`, `pdfimages`,
  Qt6 C++ libs. Never `sudo pip install`; pip targets `./.venv` only.

## 3. Opinionated product rules (from the brief)
- Max compression by default; single Effort knob (Max/Balanced/Fast) to trade speed.
- BW: Otsu auto default, Simple (= GIMP Threshold) + Adaptive + Sauvola available,
  global T slider + per-page override. Encode JBIG2 lossless (each page's
  stream is test-decoded before embedding; 1-bit PNG where the decoder
  can't take it).
  Lossy JBIG2 OFF by default (glyph-substitution risk).
- BW OFF (§§168–171): text AND vector diagrams remain native, preserving
  original fonts, geometry, colors and opacity. §171 chooses ONE combined BW
  image canvas and a native overlay; plain white page backdrops stay below it.
  Exact original native/image interleaving is not required; use FFPR for the
  flattened appearance. Do not rasterize native artwork or invent
  glyph-shaped masks. Lossless content/font/container compression is distinct
  from image thresholding. See `COMPRESSION.md`, issues B89/B90.
- Color: downsample 150dpi + JPEG q~50 default; JPEG2000 opt-in only.
- §§180/182: for BW image layers and color, compose original imagery/masks
  in full color first, resize the canvas ONCE to target DPI, then gray/BW,
  palette or codec transforms. No post-threshold/palette resize, per-image
  RGB/mask rewrite or duplicate original/upscaled filtering. Preserve native
  text/vectors (§170); BW uses the §171 white canvas, color the actual flat
  page backdrop. See `COMPRESSION.md` for source-density/scratch policy.
- NO JPEG XL inside PDFs (not in the spec, viewers can't open it).
- Never overwrite input; default `<name>.reduced.pdf`.
- Warn before rasterizing born-digital (selectable-text) PDFs in BW mode.
- Canon §§122/149: every filter runs the real saver once per input/effective
  recipe. Preview and minis read that completed PDF; amount is its exact full
  file size; export copies it. No GUI estimator or independent filter-preview
  transformation. First selection, repeat selection, zoom/pan/page changes,
  and DnD never reprocess. Live edits alone debounce one filter and show `*`.
  Keep saved and draft recipes/artifacts separate; resolve dirty switches with
  Save / Save As… / Discard / Cancel before changing selection. Artifact
  ownership and late-worker cleanup follow `FILTER_LIFECYCLE.md`.
  §189: successful Save As creates AND selects its named copy, including
  resolution of a mini/dropdown/keyboard switch. Carry that destination
  explicitly through the transaction; do not subsequently activate the
  originally clicked filter. Canceled/blank naming cancels the entire switch.
- §183: one shared 300ms trailing edit timer (proposed default) covers every
  recipe control, sliders AND numeric typing/steps AND dropdowns/toggles.
  Immediate value/dirty feedback; latest immutable recipe, exact saved-file
  publication, no per-widget processing timers. Keep view-only framing separate.

## 4. UX rules (the designer's picky-UI standard)
- Exact PDF display (§§172/173): original AND filtered panes observe their
  actual PDFs without extra bitmap smoothing/filtering. AA is allowed for
  native text/vector drawing, never raster content (including rasterized
  text in FFPR). Do not hide grey interpolation with a second threshold or
  rerun filter processing for view changes. Saved bitmap samples stay exact.
  §§174/175 select no PDF-content AA at all, and zoom renders actual native
  PDF geometry at device resolution rather than enlarging a prepared raster.
  Bound display rendering to visible regions; keep saved files immutable.
- Preset filter-strip (camera-filter UX) + main original/preview panes.
  View menu controls orientation of BOTH main panes and filter thumbnails
  (side-by-side H / stacked V). See `DESIGN.md`.
- Smooth `QGraphicsView`: wheel = scroll/pan, Ctrl+wheel = zoom-to-cursor, drag = pan, PgUp/PgDn = pages,
  fit-on-load, neighbor-page prefetch. No jank on old LXDE hardware.
- Escape cancels an active drag/dialog or running PDF export; otherwise it
  is a quiet no-op, not Undo (§85, superseding the brief's "ANYTHING"). The UI
  stays responsive; close cancels filtering asynchronously. Do not claim
  <200ms external-encoder termination without measuring it.
- PCManFM DnD (`text/uri-list`) + Open button fallback; 1024×600-friendly.
- Main-region spacing (§188): use the shared UI_PADDING token (4 logical
  pixels) for outer insets and gutters. The root alone owns outer padding;
  PreviewPair owns zero-margin equal/stacked pane/header layouts. No visible
  minis title, placeholder row or accumulated default wrapper margins. Align
  preview/panel bottoms and the strip's side edges; retain native control
  interiors, panel overflow and stable splitter sizing. See `UI_LAYOUT.md`.
- Mini progress (§§185/187/190/191/198/199): native default-control style, 1.25 times
  its height and percentage font, centered in the FULL mini frame. Keep the
  shared 4px side inset; opaque backing only inside bar bounds, with no extra
  white padding. The status-bar control itself is not enlarged. Use the same
  delegate for the viewport and uniform 75% drag snapshot; true progress and
  completion never change cell geometry or dispatch filtering.
- Action icons (§197): one native-theme-first provider for the main window
  and button lab, with stock Breeze SVG fallback assets and their licenses.
  No custom glyph drawings or unrelated fallback symbols. Match the actual
  control/toolbar palette, preserve action semantics/sizes/state, and refresh
  on theme/palette changes without filtering or changing selection. Revert
  uses `document-revert`, not history Undo. See `ICONS.md`.

## 5. Workflow
- `./test.sh` (full `./.venv/bin/python -m pytest tests/ -q`) must stay green —
  designer ruling §59: run the FULL suite every time, before every ship.
- Designer ruling §62: after every new build, stop the running app by its
  verified desktop PID, confirm it exited, then relaunch in a separate
  session. Use `setsid --wait ./run.sh …` in a retained execution session:
  the app has no controlling terminal, while the supervisor reports its
  actual exit status. Poll that execution session when reporting app status;
  successful startup alone does not establish that it remains running.
  An abruptly terminated supervisor can leave its detached GUI and workers
  alive: session exit/nonzero status alone does NOT prove app exit. Confirm
  the desktop GUI PID and process group independently, especially if no
  `APP_EXIT` line was reported. Record GUI PID/PGID alongside the retained
  execution session. Never report the app closed from supervisor status alone.
  Confirm `window shown` + preview applied in
  `${TMPDIR:-/tmp}/pdf-minimalist/pdf-minimalist.log`. Never leave the
  designer on a stale build. Sandbox process lists may not include desktop
  processes; check the desktop context when resolving a PID.
- `python3 tools/check_env.py` then `./.venv/bin/python tools/check_env.py`.
- Qt smoke: `QT_QPA_PLATFORM=offscreen ./.venv/bin/python -c "...MainWindow..."`.
- Record per-test metrics (bytes in/out, % saved, secs, preset, viewer check).

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
  B81 adds the 11-filter layout, sub-threshold native movement, repeated tail
  moves, and 33 post-reorder clicks; validate row count/UUID set, Qt NoState,
  existing artifacts/no filtering, and first normal caption pixels. Qt slot
  exceptions must FAIL the smoke, never just print and return GREEN.
  B84–B86 additionally require an actual dirty-mini native click, modal Escape,
  and Revert button click: current AND selected filter stay edited on Cancel,
  files/dirty state stay intact, and Revert reuses the saved file without work.
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
- `--debug` (`python -m pdf_minimalist --debug`) raises logging to DEBUG and dumps
  diagnostics: Python/PySide/Qt/fitz versions, cwd, argv, per-stage preview
  timings (render/threshold ms), per-page job progress.
- Default (no flag) stays INFO: quiet enough to run, complete enough to review
  what happened from the log alone.

## 7. Certified platform and packaging (§176)

- `PLATFORMS.md` records the actual tested OS/architecture/desktop, interpreter,
  Qt/PDF/native-tool versions and dated evidence. Certify the measured scope,
  not every version admitted by broad source requirements or another project's
  supported platforms. Platform verification is not designer issue acceptance.
- `PACKAGING.md` adapts the reviewed sibling/upstream Task Coach packaging
  patterns to Qt/PyMuPDF. Keep runtime, build and validation dependencies
  separate. Existing source-runtime certification does not certify installers.
- Proposed distributions must pass clean native installed-artifact gates
  (including multiprocessing, native tools, temp ownership and exact display)
  before promotion. A documentation request does not authorize installing
  packaging tools, changing other projects, publishing or pushing releases.
