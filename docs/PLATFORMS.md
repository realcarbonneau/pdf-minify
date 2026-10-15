# Certified platform

Designer ruling: `DESIGNER_VERBATIM.md` §176. Recorded **2026-10-14**
(America/New_York). Packaging plan: [PACKAGING.md](PACKAGING.md).
Latest verification update: **2026-10-15** (America/New_York).

## Current certificate: Debian 13 x86-64, source/workspace build

| Component | Verified configuration |
|---|---|
| OS | Debian GNU/Linux 13 (trixie); `/etc/os-release` reports 13.7 |
| Architecture / kernel | x86_64; Linux 6.12.107+deb13-amd64 |
| Desktop | LXDE, X11 |
| C runtime | glibc 2.41 |
| Python | CPython 3.13.5, project-local `.venv` |
| GUI binding / actual Qt runtime | PySide6-Essentials 6.12.0 / Qt 6.12.0 |
| PDF binding / actual rendering engine | PyMuPDF 1.28.2 / bundled MuPDF 1.28.2 |
| Numeric / image libraries | NumPy 2.5.3 / Pillow 12.3.0 |
| External BW encoder | `/usr/bin/jbig2`, jbig2enc 0.30 |
| Optional stream optimizer | `/usr/bin/zopfli` present; explicit native Zopfli selection requires it, with no hidden fallback |
| Independent PDF validation tools | Poppler 25.03.0; QPDF 12.2.0; `mutool` 1.25.1 |

This certifies the tested **development/source runtime**, not an installer,
binary release, every Debian desktop, or unimplemented features. The current
workspace includes uncommitted work; a release certificate must identify its
immutable release commit, dependency lock and package SHA-256. Broad `>=`
requirements are not a certification of every permitted dependency version.
The OS's separate Qt packages are not the Qt runtime used by these pip wheels.

## Evidence and limits

- Current full suite: **460 passed**, `./test.sh`, 2026-10-15, exit 0.
  The separate size-only bitmap study (§209) adds 31 headless cases and
  22 paired real/control cases / 176 actual PDFs / 600 candidate pages.
  Flate/Zopfli/Brotli plain/predicted Indexed/BW data and BW/colored JBIG2
  decode exactly; all app-engine page pixels match at 72dpi and recipe DPI.
  Final output hashes and all size cells are verified; no codec time figures
  are collected. Native compression stays Flate across each comparison.
  Source closepath warnings and experimental-reader limitations are retained,
  not called an all-reader certificate. The ghost oracle now waits for the
  existing view-reframe timer after resize/show; its exact pixels/opacity
  remain unchanged. Initial 459/one-race failure and deterministic diagnosis
  are recorded in `TEST_PLAN.md`, not omitted from the evidence.
  No new product codec/UI/default policy or dependency; ordinary ID generation
  stays unchanged, while the benchmark explicitly controls ID framing through
  an optional shared-saver flag. No desktop app was relaunched; a fresh
  process check found it closed as requested (§206). New study results:
  `IMAGE_STREAM_COMPRESSION.md`. No new GUI/platform certification is inferred
  from this headless scope, and no designer acceptance is inferred.
- Previous integration suite: **429 passed in 174.96s**, `./test.sh`, 2026-10-15.
  Six editable image codecs and three independent native-stream choices
  preserve actual saved/draft state, UUIDs, native artwork and one edit timer.
  Forty new core/actual-PDF cases and seven lifecycle cases cover actual
  codec filters, exact palette/native pixels, persistence, strict failures,
  shared debounce and inactive/restored FFPR state. The full suite includes
  all seven lifecycle cases; six initial cases additionally passed at 2×.
  Actual full-window/1:1 control and pane captures were viewed at both scales,
  including all choices, limited-support warning and BW-to-color/Revert state.
  Final resize smokes settle in 0.121s/0.315s, then remain stable for ten
  seconds with equal panes, aligned headers, native overflow and no filtering.
  Actual filter-lifecycle smoke passes, with modal Escape/Discard/Save As
  captures viewed. The native-stream benchmark covers 32 cases / 64 outputs;
  all candidate native bytes and MuPDF pages match, image bytes are unchanged.
  Installed Poppler/QPDF pass ordinary codecs but FAIL Brotli; this is not
  an all-reader certificate. See `NATIVE_STREAM_COMPRESSION.md` and
  `TEST_PLAN.md` for scope, CPU-timing caveats and interrupted checks.
  No dependencies were installed; existing certified runtime versions remain
  unchanged. This verification predates the designer's CPU-overload note;
  no new heavy runs were launched during the final documentation pass.
- Previous stage: **382 passed in 78.93s**, `./test.sh`, 2026-10-14.
  The separate Icon Lab (§200) has 37 permanent choices across Nuvola,
  Oxygen, GNOME Classic and Breeze, with bundled source/license provenance.
  Forty-three focused checks pass at normal/2× (3.72s/4.37s), including
  direct family loading, stock hashes, choices/copy/clear, small-window
  scrolling and no production-icon/settings/filter/job mutation. Actual
  light/dark, unselected/selected, lower-row and narrow-window screenshots
  plus 1:1 candidate cards were viewed at both scales. The main layout and
  production icon choices are unchanged. See `ICON_LAB.md` and `TEST_PLAN.md`.
- Previous stage: **339 passed in 68.67s**, `./test.sh`, 2026-10-14;
  includes standard native-theme/Breeze fallback icons (§197) and the final
  1.25× mini progress height/font (§§198/199). Forty progress checks pass at
  normal/2× (2.13s/2.49s), with exact native-widget pixels and unchanged
  reserved width, insets, full-frame centering, status bar and 75% ghost.
  Queued/live/complete full windows and 1:1 strips/default bars/ghosts were
  actually viewed at both scales. Icon-only stage: 339 passed in 71.05s;
  33 icon/lab/app checks additionally pass at 2× (4.04s), with native/fallback
  light/dark and enabled/disabled screenshots viewed. No new dependency;
  bundled Breeze provenance/licenses and QtSvg/package-data requirements are
  recorded in `ICONS.md` and `PACKAGING.md`. Extra icon-stage 100% resize
  passed (0.210s settling, then stable for ten seconds); its additional 2×
  run was interrupted, not certified. The stale diagnostic-only PID-2 lock
  recovery and interrupted initial suite are recorded in `TEST_PLAN.md`.
- Previous stage: **319 passed in 75.40s**, `./test.sh`, 2026-10-14;
  compose-first color/BW, exact nearest palette mapping, shared 300ms control
  debounce, native mini progress, unified main-region spacing and Save As
  destination/lifecycle, matching Configuration heading, no working labels
  and the separate tool-only layered-JBIG2 study. Earlier stage: 294/77.90s.
  The final 32 progress cases pass at 100%/2× (1.38s/2.29s), with exact
  native-widget pixels, actual full-frame centering, larger percentage fonts
  and no extra white padding. Both-scale screenshots were actually viewed.
  The final combined mini-progress/missing-label/layout subset passes at
  both scales: 46 cases (2.14s/2.53s). Header/resize checks also pass at both
  scales: final settling 0.099s/0.182s, then stable for ten seconds, with
  matched header/frame tops, native overflow and no processing.
  Current native DnD passes at 100%; the additional 2× caption-oracle limit
  is recorded in `TEST_PLAN.md`, not called an all-green native 2× certificate.
  Numeric/palette tests also passed at 2× (16 cases). Earlier palette/debounce,
  compose-first and exact-display stages had 244/229/203 tests. Runtime versions
  above are unchanged. Qt's available Windows style is not OS certification.
- Exact display: 16 pixel/geometry/cache cases also pass with
  `QT_SCALE_FACTOR=2`. They cover actual FFPR viewport pixels at five zooms,
  native text/vector refinement, parent-window versus viewport painting,
  genuine color/opacity, settings restoration and bounded source caches.
- Real-file GUI smoke checks no extra filtering jobs or changed PDF bytes on
  zoom; FFPR samples are only 0/255 at 10%, 75%, 200%, 400% and normal/2×
  display scale. Full windows and 1:1 panes/strips are captured for review.
- Standard screenshots cover one/two/seven occupied pages and stacked panes;
  filter-lifecycle smoke covers first visits, exact full sizes, dirty state,
  modal Escape, Revert and explicit Discard ownership. See `TEST_PLAN.md`.
- Compression corpus evidence includes native text/vector retention, distinct
  per-page FFPR payloads and independent image decoding; `COMPRESSION.md`
  records actual bytes, timings and the intentional native-overlay policy.
- Historical layered-color JBIG2 study (§§192–194): Eighteen cases /
  34 page pairs / 107
  masks pass exact stored readback and MuPDF display; Poppler decodes each
  mask exactly but its full-page sampling differs. Thirteen tool tests
  pass. Measured wins, regressions and source diagnostics are documented in
  `LAYERED_COLOR_JBIG2.md`; production modes were unchanged DURING that study.
  §203 subsequently requested the optional production codec now covered by
  the current suite/captures above. The historical study's output sizes are
  not relabeled as current-saver measurements or universal-viewer proof.
- Latest desktop launch, **now closed at the designer's request**: retained
  session **25396**, GUI PID **2955881**; its PGID/SID were not captured and
  are not inferred. Started 2026-10-15 10:40:03, window shown 10:40:07;
  reopened the 12-page NASA source and queued all 12 saved filters with
  default native Flate. Fast Draft's actual 211,181-byte result was ready
  at 10:40:33. The designer closed the app during filtering; retained session
  reported **APP_EXIT status=0**, and desktop PID checks found the GUI gone.
  No worker close/Save/Discard input was sent to this launch. §206 explicitly
  confirms "Yes—leave it closed"; §207 defers designer testing. No later
  launch is made. No preview-applied/all-artifacts-ready claim is made for
  this interrupted startup. A native callback cancellation produced a worker
  error during shutdown (B107 OPEN), despite the normal GUI exit.
  Before this launch, old GUI2448022 was normally closed via Ctrl+Q to its
  verified X11 window56623111; the whole PGID2448018 was independently
  verified gone. Supervisor65772's earlier 143 was NOT taken as GUI exit;
  no APP_EXIT code is invented for that older closure. No worker Save/Discard
  choice was made.
- Previous desktop build: retained session **65772**, GUI PID **2448022**,
  PPID/PGID/SID **2448018**, independently verified in desktop `ps`.
  Window shown 2026-10-14 23:27:40 (America/New_York), exact-file preview
  applied 23:27:49, all 12 artifacts ready by 23:27:59, including the
  designer-created copy. This build adds the separate Icon Lab without
  changing the production icons or the final 1.25× mini progress scale.
  On resume at 2026-10-15 09:12, the retained session remained running and
  desktop `ps` independently confirmed this same GUI/process group alive.
  Previous session18645 / GUI2415604 / PGID2415600 exited normally
  (`APP_EXIT status=0`); its whole process group was independently verified
  gone before relaunch. No worker Quit/Save/Discard input was sent for that
  closure. These IDs are dated observations; future status claims require
  a fresh retained-session/desktop check.
- Previous desktop build: retained session **18645**, GUI PID **2415604**,
  PPID/PGID/SID **2415600**, independently verified in desktop `ps`.
  Window shown 22:56:30, exact-file preview applied 22:56:44, all 12 artifacts
  ready by 22:56:58, including the designer-created copy. The retained session
  was polled again at 22:57:23 and remained running. This build includes the
  standard theme/Breeze action icons and the final 1.25× mini progress scale.
  Previous icon-only session9907 / GUI2409896 / PGID2409892 exited normally
  (`APP_EXIT status=0`, 22:54:41) before a worker Quit was sent; its whole
  process group was independently verified gone before relaunch. No worker
  Save/Discard input was sent. As always, these IDs are dated observations;
  future status claims require a fresh retained-session/desktop check.
- Previous desktop build: retained session 44023, GUI PID 2386118,
  PGID/SID 2386114 (verified in desktop `ps`); window shown 22:01:00,
  actual preview applied 22:01:09, all 12 saved artifacts ready by 22:01:21,
  including the designer-created copy. This is the final Configuration/
  no-working-label build. Previous GUI2376487 was normally closed via its
  verified window for this restart: stdout includes APP_EXIT status=0
  (though its supervisor later reported 143); the whole PGID2376483 was
  independently verified gone. No automated Save/Discard action was sent.
  Earlier desktop build launched in session 2111, GUI PID 2363689,
  PGID/SID 2363685; window shown 21:25:51, preview applied 21:26:01,
  all 12 saved artifacts ready by 21:26:14,
  including the designer-created copy. Session 2111 later ended with status
  143 WITHOUT APP_EXIT. Independent desktop checks at 21:30 proved the GUI
  and its whole working process group remained alive. Do not infer an app
  exit or a crash from that supervisor interruption; fresh desktop checks
  are required because its retained execution session is no longer active.
  That earlier build followed normal Ctrl+Q closure of GUI2346374/session29707:
  APP_EXIT status=0 and whole PGID2346286 independently verified gone.
  Its unsaved-choice dialog was left to the designer; no worker Save/Discard
  action was sent. Earlier GUI2305839/session81018 likewise closed normally
  with APP_EXIT status=0 and whole PGID2305835 verified gone, resolving the
  designer's §189 question about that closure. The worker requested the
  canon-required restart; there is no crash evidence for that close.
  Previous session 40219 ended with status 143 without APP_EXIT, but desktop
  checks proved its GUI 2230109/PGID2230105 remained alive. A normal Ctrl+Q
  was sent to its verified window; no automated Save/Discard action was sent.
  The whole old process group was independently verified gone before relaunch;
  supervisor termination alone was not mistaken for app exit. Earlier launch
  evidence: 19:02:36 (palette), 18:25:37 (compose-first). These IDs are dated
  evidence, not permanent configuration or a promise that a subsequently
  closed app remains alive; poll the retained execution session again.

Certification is worker verification, **not designer acceptance of issues**.
B89/B90/B91/B92/B94/B96/B97/B98/B101/B102/B103/B104/B105/B106 remain OPEN
until explicit designer confirmation. B99/B100 were audit findings only in
the historical study; their production repairs are now worker-verified under
§203 but remain OPEN pending confirmation. B107 is a new unimplemented
shutdown audit finding. §207 explicitly defers acceptance testing, not work.
B95's final progress appearance is designer-confirmed in §192; B93's palette
improvement is designer-confirmed in §184, both 2026-10-14. Previous dated
designer confirmations keep their exact recorded scope in `issues.md`.

## Other targets

Windows, macOS (Intel/Apple Silicon), other Linux distributions/architectures,
Wayland, and all packaged formats are **NOT CERTIFIED**. Cross-platform Qt,
Python or Task Coach support is not evidence that this app has passed there.
Promote a target only after its actual installed artifact passes the packaging
release gates on a clean native machine/VM, with dated versions, results,
screenshots, startup/exit evidence and an artifact checksum. No new platform
was built or published as part of this documentation request.
