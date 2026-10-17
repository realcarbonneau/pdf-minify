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

## 2. Stack & layout (locked unless the designer says otherwise)
- Product identity (§230): display **PDF Minify**, package `pdf_minify`,
  machine/settings/temp slug `pdf-minify`. Keep the flat import-package layout;
  do not add installation/layout work to a branding rename. All settings
  access uses `ui_qt/settings.py` and its one-time non-overwriting legacy
  migration. Tests/review runs isolate both namespaces before migration.
  Preserve exact quotes, licensed resources and frozen benchmark provenance;
  keep the actual GitHub remote unchanged until the designer renames it.
- Python + PySide6 (Qt6) GUI + PyMuPDF pipeline. `core/` = headless, NO Qt imports.
  `ui_qt/` = widgets only. Pure-numpy thresholds (no hard OpenCV dep).
- REPOSITORY-OWNED: `pdf_minify/`, `tests/`, `tools/`, `docs/`,
  `requirements*.txt`, `.venv/` (git-ignored, via `setup_local.sh`).
- SYSTEM (apt, never vendored): `python3`, `jbig2`, `mutool`, `pdfimages`,
  Qt6 C++ libs. Never `sudo pip install`; pip targets `./.venv` only.

## 3. Opinionated product rules (from the brief)
- Designer §213 supersedes the old Max/Balanced/Fast encoding-effort brief:
  this is an opinionated best-compression suite. Encoder speed/cost and
  dependency convenience are not reasons to retain superseded encoding
  choices. Preserve the chosen image representation/fidelity; minimize actual
  complete PDF bytes within the intended reader-support requirements.
  Distinguish decoder FORMAT from encoder implementation: Zopfli produces
  ordinary FlateDecode data, with no new reader requirement. Target one
  optimized Flate choice using the best validated encoder, not separate
  fast-zlib versus Zopfli products. Retain alternate formats for meaningful
  size outcomes or reader-support requirements, never merely as a faster or
  easier-to-install option. Current runtime has not yet been aligned; see
  TODO §217 and `COMPRESSION_COMBINATIONS.md`. No arbitrary performance cutoff
  or silent weaker-encoder fallback under a best-compression label.
- BW: Otsu auto default, Simple (= GIMP Threshold) + Adaptive + Sauvola available,
  global T slider + per-page override. Encode JBIG2 lossless (each page's
  stream is test-decoded before embedding). §203 adds explicit Flate BW and
  forbids silent codec substitution: a failed selected JBIG2 leaves a clear
  error and the saved file intact. Only legacy automatic headless helpers
  retain the earlier 1-bit PNG fallback contract.
  Lossy JBIG2 OFF by default (glyph-substitution risk).
- BW OFF (§§168–171): text AND vector diagrams remain native, preserving
  original fonts, geometry, colors and opacity. §171 chooses ONE combined BW
  image canvas and a native overlay; plain white page backdrops stay below it.
  Exact original native/image interleaving is not required; use FFPR for the
  flattened appearance. Do not rasterize native artwork or invent
  glyph-shaped masks. Lossless content/font/container compression is distinct
  from image thresholding. See `COMPRESSION.md`, issues B89/B90.
- Color: 300dpi + JPEG q~50 default; JPEG2000 opt-in only (§225).
- §§224/225 supersede mixed-resolution defaults: all built-in raster filters
  and missing-DPI fallbacks use 300 DPI. §226 also requires a one-time migration
  of ALL existing saved raster recipes, including explicit custom DPI values,
  to 300 DPI. Preserve stable UUIDs and other settings; keep DPI editable and
  respect deliberate post-migration values on subsequent launches. Current integrated overview AND
  focused scenarios use 300 DPI, without lower-DPI variation tables.
  Preserve-images controls are explicitly unresampled. §224 also authorizes
  color FFPR: flatten whole-page full color, resize once, then transform/encode
  with the selected existing codec. Extend the existing saver/capability/key
  path, not an independent preview or benchmark-only product implementation.
  Repair B108–B112 rather than suppress diagnostics or relax exact checks.
  Native foreground must preserve original operators/Form text-state
  inheritance. Use token-aware bitmap/backdrop removal and pruned native
  resources, not a final sanitizing cleanup that rewrites retained content.
  Keep native page/Form ownership consistent with the source structure tree;
  prepend the replacement raster as an Artifact, not a grafted native page.
  Use an immutable original for every canvas and one explicit per-document
  native context across shared Forms. Never strip accessibility metadata to
  hide retained images. Check all live image streams, not just page resources.
  Parse inline-image boundaries with the decoder, never regex.
- §203: compression is editable recipe state, never locked by the seed
  preset. Expose the six explicit choices documented in `COMPRESSION.md`;
  persist actual saved mode through Save/Save As/load. Explicit codecs cannot
  silently substitute another codec. Threshold method (not an unqualified
  Strategy or universally automatic strategy) covers manual AND automatic BW
  thresholding. Both palette codecs share the existing exact palette helper;
  production and benchmark tooling share core stencil code. Existing defaults,
  UUIDs, native artwork and real-file/edit lifecycle remain unchanged.
- §§204/205 distinguish image codecs from lossless native-stream compression.
  A separate PDF stream policy (Flate default, Zopfli-Flate, limited-support
  Brotli) is effective recipe state. Share the core adapter with benchmark
  tooling; verify decoded bytes, image-byte preservation, whole-PDF sizes and
  installed readers. Keep empty streams plain; MuPDF 1.28.2's zero-byte Brotli
  result is invalid and its decoder can hang. Do not silently fall back or
  advertise the new extension as universally supported. See
  `NATIVE_STREAM_COMPRESSION.md`.
- §§210/211 request a compression-combination table and UI recommendation,
  not implementation. `COMPRESSION_COMBINATIONS.md` marks current versus
  proposed capabilities explicitly. Shared image/native general compression,
  FFPR fixed general-compression states are not approved replacements for the
  existing selectors. §224 subsequently authorizes color FFPR through the
  existing checkbox/saver. Never treat a worker recommendation as a designer
  ruling or silently migrate saved mixed-codec recipes.
- §220 supersedes §219's documentation split; §§238–240 now move the primary
  integrated overview's PNG rows into a separate measured-effect table.
  Retain the plain and PNG measurements. Explain that prediction
  precedes the same compressor; any percentage compares with that encoder's
  plain counterpart using complete PDF bytes. Preserve both wins and losses;
  do not assert universal growth. No benchmark variant or product behavior
  changes merely to simplify presentation.
- §221: highlight the smallest complete-PDF size in each same-input bitmap
  comparison row using Markdown bold, including ties. Do not compare unrelated
  inputs or mix timing/quality fields into the minimum; reader-support caveats
  remain independent of the size highlighting.
- §222: the primary compression comparison is an integrated matrix of actual
  complete saved PDFs across image/predictor and native-stream policies, not
  separate image/native savings estimates. Report final file bytes only as
  the optimization metric; no timing rankings or payload-size substitutes.
  Keep exact recipe/fidelity and reader requirements explicit. Separate
  component studies are supporting diagnostics, not evidence for unmeasured
  combined outputs.
- §§223/231: present realistic combinations as rows over six representative
  complete-PDF cases (the original five plus NASA Kepler technical illustrations),
  with descriptive labels and focused scenario tables.
  Packed-image/native policies share their general compressor; omit mixed
  general-codec pairings from the published analysis. Keep specialized image
  codecs' meaningful native alternatives, a classic-Flate reference and
  plain/predicted comparisons. Bold minima within the SAME input and fidelity
  group, not across unrelated PDF columns after transposing. Existing raw
  cross-product artifacts remain evidence, not product recommendations.
  This is benchmark scope/presentation, not authority to migrate saved mixed
  recipes, implement new controls or change product defaults.
  Reject new source-to-preparation diagnostics before accepting a frozen
  production baseline. Report a bad candidate as FAILED and a rejected
  shared preparation as PREP FAILED, with no size/minimum; the latter does
  not imply every dependent codec independently failed. Preserve valid
  independent results and expose any processing defects. §224 requests repair
  of B108–B111; worker verification is distinct from designer acceptance.
- §§227/228: group the primary integrated overview as BW, indexed color / low
  palettes, then full color, retaining every representative PDF column and all
  measured combinations in one continuous Markdown table with one header.
  Use unnumbered divider rows with the title only in the far-left cell and
  otherwise blank measurement cells; no separate tables, numbered headings
  or HTML colspan.
  Put unresampled preserve-images references above the groups in the same
  table, and native-retaining rows before FFPR within each group.
  Indexed FFPR stays indexed. Preserve every size and existing per-fidelity
  bold minimum; expected codec strengths do not establish universal winners
  or authorize codec/default changes. Focused tables remain unchanged.
- §232: label the overview BW divider **Black and white (BW + Otsu)**.
  Omit redundant `; keep native` from published combination labels and their
  generator; absence of FFPR implies native text/vector preservation. Keep
  FFPR and native-stream compressor names explicit. No threshold, recipe,
  measured size or bold-minimum change is implied; focused Simple threshold
  columns remain explicitly labeled.
- §229: benchmark every row against every input, including redundant no-image
  cases. With §§231/236 the 34 × 6 study requires 204 measured cells, not
  image-free N/A cells. NASA Kepler is a whole 12-page input, not an extract.
  Save/verify an actual complete output per row; do not copy another row's
  size or alias a control file. An unused image codec is a valid no-op while
  native/font/container compression still runs. Annotate it, never invent a
  bitmap to exercise the encoder. Prior exact-row measurements may be reused
  only with strict compatible-code/source/preparation/output provenance.
- §233: the main BW scan must not already use JBIG2. Use the complete
  11-page CCITT `scan-naca-tm972.pdf`, keeping six columns and every retained row.
  Keep `scan-jfk-poor-copies.pdf` separately as B114's full-flow regression:
  unchanged-resolution lossless JBIG2 must preserve original samples/geometry
  and not increase complete-file bytes. Cover native/FFPR, compare a compatible
  preserve-images control, and keep intentional transformations distinct.
  Check source image `/Filter` values, not extraction/export extensions (B115).
  Never relabel an old input's size as a replacement measurement or mark a
  documented known failure fixed. Historical artifacts stay immutable.
- §234: maintain `JBIG2.md` as the dedicated encoder/embedding/safety reference
  and TODO §240 as the detailed optimization exploration plan. Current `-p`
  generic-region measurements do not prove optimal JBIG2 settings. Research
  `-d`, symbol settings/refinement and shared dictionaries with exact pixels,
  whole-file size and reader gates; no lossy/default/UI changes are approved
  merely by asking for documentation. B114's worker-verified repair is not
  designer acceptance; its issue remains open until explicitly confirmed.
- §235: preserve actual fractional image/mask sampling density in composition,
  never ceil it to whole DPI and create an unintended resize. Keep the one
  final target-DPI resize and existing layer/encoder policy. Same-density
  JBIG2 must pass original-sample, all-page-pixel and complete-file no-growth
  checks normally, not as expected failures. Cover genuinely fractional DPI;
  refresh affected measurements without rewriting historical provenance.
- §§236/237 narrow benchmark reference coverage: remove the eight Classic-Flate
  BW/indexed native/FFPR overview rows and equivalent bitmap rows throughout
  ALL focused tables, not just Logos/artwork. The measurement inventory is
  34 × 6 = 204 actual cells, split for display under §§238–240 below.
  Keep the unresampled Classic-Flate control,
  Zopfli/Brotli predictor pairs, and full coverage of every retained row.
  Share combination selection; do not reintroduce removed rows as supplemental
  references. Preserve frozen supersets; document verified selections separately.
- §§238–240: the first review isolated PNG prediction only, keeping
  residual-stream comparisons unchanged until §242 authorized the next study.
  That initial overview displays 26
  baseline rows / 156 sizes; the PNG table displays eight baseline-labeled
  rows × six PDFs / 48 measured sizes plus signed percentage change from
  each matching measured baseline. Negative is smaller. Paired sources,
  recipes, prepared pixels and native policies must match. No estimates or
  fabricated/no-op replacements; retain independently measured no-image
  controls and all 204 measured dispositions. Preserve focused-scenario data
  and historical artifacts; change presentation, not encoding or strict reuse.
- §242 expands PNG coverage to 16/64-color native/FFPR baselines with both
  general compressors over all six PDFs. Add visible measured plain baselines,
  retain signed full-file deltas and exact paired verification, and encode only
  missing cases. Historical reuse needs explicit bounded compatibility proof
  without relaxing normal resume gates. A no-win Brotli sample is not a
  universal theorem. Plan each next controlled experiment with one named
  changed factor. NATIVE-01 compares standard-Flate reference against named
  optimized native/residual encoders, keeping image payloads byte-identical:
  five specialized FFPR rows plus two native-content controls, all six sources.
  Reference-only Classic Flate does not restore it as a product choice.
  See `COMPRESSION_EXPERIMENTS.md` and TODO §§243/244.
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
- Icon Lab (§200): current icon appearance is rejected, not accepted. Expose
  a direct View menu comparison with genuine stock-family assets and permanent
  choice codes; retain their provenance/licenses. Per-action radio selection,
  background review and Copy choices never mutate production icons/settings
  or filter/selection/processing state. See `ICON_LAB.md`.

## 5. Workflow
- Designer §241 clarifies §59: run `./test.sh` (full
  `./.venv/bin/python -m pytest tests/ -q`) after code-affecting changes,
  including tests, dependencies, build or configuration changes that can
  affect execution. Documentation-only edits, including comment-only changes,
  need relevant documentation checks, not the full suite. Reuse a passing
  result for unchanged code; committing/pushing is not a new test trigger.
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
  Respect an explicit designer closure/leave-closed instruction: do
  not automatically reopen the app to complete or repeat this workflow.
  Never choose Save/Discard for the designer merely to automate a restart;
  leave their unsaved-data decision to them.
  Use retained tool/session state for immediate run status, not permanent
  launch-history TODOs. Keep actual startup/exit failures and their regression
  evidence in the relevant issue/test records. The size-only bitmap protocol
  (§209) collects no compute-time comparisons; temporary workstation scheduling
  does not belong in the design log.
  Confirm `window shown` + preview applied in
  `${TMPDIR:-/tmp}/pdf-minify/pdf-minify.log`. Never leave the
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
- `--debug` (`python -m pdf_minify --debug`) raises logging to DEBUG and dumps
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
