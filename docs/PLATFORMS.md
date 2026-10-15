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
binary release, every Debian desktop, or unimplemented features. A release
certificate must identify its
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
  an optional shared-saver flag. New study results:
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
  Existing certified runtime versions remain unchanged.
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

Certification is worker verification, **not designer acceptance of issues**.
B89/B90/B91/B92/B94/B96/B97/B98/B101/B102/B103/B104/B105/B106 remain OPEN
until explicit designer confirmation. B99/B100 were audit findings only in
the historical study; their production repairs are now worker-verified under
§203 but remain OPEN pending confirmation. B107 is a new unimplemented
shutdown audit finding.
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
