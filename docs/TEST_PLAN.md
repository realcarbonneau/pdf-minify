# Test Plan

## Validation triggers (§241)

Run the full suite after code-affecting changes, including test, dependency,
build or configuration changes that affect execution. Documentation-only and
comment-only edits need relevant checks (formatting, links or table/data
consistency), not a full test run. Reuse a passing result when the tested code
is unchanged; committing or pushing does not require repeating verification.

## Current regression verification — 2026-10-17

§§255/256 Best: **767 passed**, `./test.sh`, exit 0 / FULL SUITE GREEN, no
expected failures, 2026-10-17. Focused core checks pass **100 tests**, and
selected Best/Brotli GUI lifecycle checks pass **11 tests**. `test_best_streams.py` covers actual
mixed/homogeneous file-size selection and metadata-overhead reversals, stable
binary PDF IDs (including xref-stream sources), disk-backed reuse, empty input,
missing/corrupt encoders, cancellation/atomic publication and saved-file
readback rejection. Exact page renders, native geometry, samples/predictors,
soft masks and protected J* bytes are compared across native/FFPR modes and
lossy/lossless JPEG2000. A genuine decoded CCITT input must convert in every
image mode, not survive as an invented exception. GUI tests cover the single
debounce, exact completed-file reuse, persistence and existing unsaved-filter
transactions. `tools/shot.py --best-streams-only` captures actual packed results,
the menu, Compatibility states and native tooltip. The successful captures
and 1:1 panels/tooltip were viewed; Packed BW/Indexed color avoid promising
Flate while Best may select Brotli. Both environment checks pass in their
documented system/venv roles. Implementation verification is not designer acceptance.
The fixed-encoder binary experiment below remains complete, not a new corpus
benchmark of Best. Completion-document edits reuse this tested code result;
there is no additional full-suite trigger for documentation-only changes.

### Previous tooltip and complete Brotli refresh stage (§§253/254)

§§253/254: **718 passed**, `./test.sh`, exit 0 / FULL SUITE GREEN, no expected
failures. The completed all-Brotli rerun covers **229 distinct actual outputs**:
177 integrated, 44 bitmap-component and eight native-component (levels 9/11).
Image samples/palettes/thresholds were reused, every Brotli encoding reran,
and all final default-OFF files were actually saved/measured. No encoding
timings, guessed metadata deductions or newly rasterized corpus were used.
The current publication pins SHA-256
`9279a171feff32151a44e7d2f41d3042abdc611bdd2ecf72c3b4bb724eeed22d`;
both percentage fixtures explicitly assert declaration OFF. All 215 integrated
ordinary controls retain checked hashes; 156 supporting controls have checked
sizes and recorded hashes, without inventing hashes absent from the old native
manifest. Fixed-side signatures pass 96 PNG native-stream pairs and 72 native
A/B image pairs. Graph/stream proof preserves earlier all-page pixels; it is
not a claim that pixels or unsupported readers were freshly rerun.

The focused reporting/rerun checks pass **75 tests**. New regressions cover
fresh real encodings, binary-string graph fidelity, PNG decoding parameters,
no artificial null metadata, strict pinned imports/output hashes, immutable
controls, complete replacement scope, actual table arithmetic and reader-tier
winner counts. FFPR byte accounting closes in all thirty default-OFF pairs:
Brotli is 2–105 B larger in 29, 66 B smaller in one, with no exact ties.
Original declaration-ON evidence is preserved, not relabeled.

Tooltip help is native Qt, concise, context-specific and exposed through
accessibility and keyboard What's This. Tests verify no dirty/selection/
artifact/processing change from help, and unchanged platform font/palette/
duration. `tools/shot.py --brotli-compatibility-only` passes; the real native
tooltip `.tmp/shot-brotli-reader-tooltip.png` and all four policy/control panels
were viewed. The inline warning and its layout space are absent. The exact
**(Compatibility)** label and hidden non-Brotli behavior remain unchanged.
Implementation verification is not designer acceptance. Subsequent completion
notes are documentation-only and reuse this passing full-suite result (§241).

### Previous opt-in declaration stage — 2026-10-17 (§§251/252)

Brotli declaration (§§251/252): defaults are OFF in legacy/new filter recipes,
the core saver and benchmark generators. The compatibility checkbox is hidden
for non-Brotli compressors. Tests cover effective identity, exact output/image/
native data, direct/indirect extension dictionaries and mixed arrays, preservation
of unrelated entries/source versions, repeated opt-in, restored save contexts,
benchmark declaration identities/resume rejection, the single edit debounce,
real-file preview, Save/load and Cancel/Discard/Save As/Revert transactions.
Targeted Brotli checks: **47 passed**. The final full suite after the exact
**(Compatibility)** label update (`./test.sh`, offscreen) passes **701 tests**,
exit 0 / FULL SUITE GREEN, with no expected failures. Environment checks pass
in both interpreters; required application packages are in the project venv.
Later completion notes are documentation-only and reuse this result (§241).

`tools/shot.py --brotli-compatibility-only` passes with real completed files.
Viewed captures `.tmp/shot-compatibility-{flate-hidden,brotli-default-off,
brotli-opt-in,zopfli-hidden}.png` and their 1:1 panels show the native unchecked/
checked control only for Brotli, with no non-Brotli placeholder and no label
clipping, including the exact **(Compatibility)** label. Settings are isolated;
no desktop app was launched.
Frozen declaration-ON benchmark tables retain their actual sizes/provenance;
this feature change does not pretend those are new declaration-OFF results.

### Previous percentage-presentation stage — 2026-10-17 (§§247–249)

Percentage presentation (§§247–249): signed changes use two decimals computed
from original measured bytes; exact ties and changes rounded to zero are never
bold. The full FFPR Brotli-baseline/Zopfli-treatment section immediately follows
PNG prediction. Tests cover tiny gains/losses on both sides of the rounding
boundary, unchanged exact byte-count emphasis, all 96 PNG pairs against a frozen
original-size fixture, all 30 FFPR pairs against their existing fixture, and
42 native/residual changes against visible reference/candidate byte counts.
No corpus encoding/rendering or application behavior changes are needed.
Targeted reporting checks: **117 passed**. The full suite (`./test.sh`, offscreen)
passes **679 tests**, exit 0 / FULL SUITE GREEN, with no expected failures.
All ten byte-count tables retain their original counts/emphasis; all 168
percentage differences use two decimals, with rounded zeros unbolded.
Later completion notes are documentation-only; reuse this passing result (§241).

The PNG fixture records its original publication manifest hash
(`9864f717f7ea0f1f879f8a3d7537229ffe9e62d6817228dc510945d6adc9e7e9`);
historical measurement files/identities remain unchanged. Section-order and
published-table checks prevent bold zeros or mixed precision from returning.

### Previous FFPR Brotli–Zopfli stage — 2026-10-17 (§§245/246)

NATIVE-02 (§§245/246) verifies five FFPR/specialized-codec rows over six
whole PDFs: thirty newly saved Brotli baselines versus thirty verified reused
Zopfli files, with encoded images byte-identical and all-page 72/300-DPI
pixels/native content exact. The corpus run performs no new image preparation
or image encoding; unit tests create their own tiny real FFPR fixtures.
Source, preparation, output and encoding-implementation hashes plus package/
binary identities are checked; frozen producer identities remain unchanged.

Measured stream accounting closes exactly in all thirty pairs: Brotli is
100–271 bytes larger. Each difference equals native-payload change + 166
declaration bytes + actual filter-name and Length-digit costs; image,
container-stream and other-stream deltas are zero. Two metadata-only controls
(one/six pages) isolate 166 declaration bytes with native/image payloads
unchanged, and both pass QPDF. The specification recommends the declaration
(SHOULD), not SHALL: this is current writer policy, not an unavoidable
format minimum. New Brotli streams are MuPDF-verified, not QPDF-certified.

Fourteen new tests cover the bounded FFPR scope, real two-page paired saves,
exact accounting, metadata-only controls, reuse without encoding, rejected
pairs, five-decimal precision, short display labels without identity changes,
and all thirty published cells against a frozen actual-size fixture.
The targeted reporting run passes **106 tests**. The fresh full suite
(`./test.sh`, offscreen) passes **674 tests**, exit 0 / FULL SUITE GREEN,
with no expected failures. Later completion notes/docstring clarification
are documentation-only; this tested code result is reused under §241.
The only later benchmark-source change is a docstring clarification of
SHOULD versus SHALL; it does not alter encoding or rewrite the frozen runner.

Evidence: `.tmp/compression-experiments/ffpr-brotli-zopfli-300dpi-20261017/`,
the paired publication/audit in `ffpr-brotli-zopfli-publication-20261017/`,
and `tests/fixtures/ffpr_compressor_sizes.json`. Existing table numbers are
unchanged; labels shorten to Zopfli. The new table adds thirty percentage
cells without new GUI behavior/defaults. JBIG2 `-d` remains proposed, not run.

### Previous Brotli-annotation stage — 2026-10-17 (§244)

The §244 update underlines all eight Brotli labels only in the PNG table.
Generator/published-table tests retain plain baseline identities and the
original audited percentage digest after removing presentation markup.
The targeted PNG/publication run passes **41 tests**. The fresh full suite
(`./test.sh`, offscreen) passes **660 tests**, exit 0 / FULL SUITE GREEN,
with no expected failures. Final completion notes are documentation-only;
the passing code result is reused under §241.

A data-only overall-winner audit checks all 96 representative PNG candidates
against measured same-fidelity minima: zero unique wins, four no-image ties,
92 larger. Fourteen focused PNG records and 66 historical PNG records also
have no minimum. These scopes overlap and are not pooled. Excluding Brotli
leaves eight strict measured-subset minima; incomplete 16/64-color JBIG2
coverage remains explicit. The noisy-BW counterexample's three actual file
sizes/hashes confirm that prediction improves Brotli without winning overall.
Evidence: `.tmp/compression-experiments/png-winner-review-20261017/audit.json`.
No corpus encoding/rendering was repeated. The next JBIG2 `-d` study is a
documented proposal only, not an executed benchmark or product/default change.

### Previous percentage-only PNG stage — 2026-10-17 (§243)

The §243 PNG presentation update removes byte counts only from that effect
table. Its formatter and published snapshot keep 96 signed percentages,
paired win/tie emphasis and six visible-baseline columns. Six added cases
cover percentage-only formatting, exact ties and tiny gains/losses that round
to zero; byte-plus-percentage formatting remains covered for NATIVE-01.
The targeted PNG/publication run passes **41 tests**. The fresh full suite
(`./test.sh`, offscreen) passes **660 tests**, exit 0 / FULL SUITE GREEN,
with no expected failures. Subsequent completion notes are documentation-only;
this passing code result is reused under §241. The desktop app stays closed.

The data-only projection independently checks all 96 pairs against the
original measured bytes and 192 actual output sizes/hashes. Overview,
focused and native/residual tables are unchanged. The report now displays
375 byte counts plus 96 percentage-only cells; all 362 measured PDFs and
their original provenance remain intact. No corpus encoding or rendering
was repeated. Projection proof is frozen in
`.tmp/compression-experiments/png-percentages-20261017/projection.json`;
the portable publication test pins its audited percentage-table digest.

### Previous controlled-experiment stage — 2026-10-17

Full suite after the controlled-experiment code changes (`./test.sh`,
offscreen): **654 passed**, exit 0 / FULL SUITE GREEN, no expected failures.
The 19 new cases cover experiment scope, real saved-file pairs, compatible
reuse, fixed-stream proofs, publication gates and measured table arithmetic.
Production rendering, GUI behavior and defaults are unchanged. The independent
publication audit passes all 362 saved files and 138 signed percentages.
The later completion notes below are documentation-only; the tested code is
unchanged and this passing suite is reused under §241.

### Previous PNG-only stage — 2026-10-16

Fresh full-suite run (`./test.sh`, offscreen): **635 passed**, exit 0 /
FULL SUITE GREEN, with no expected failures. B114's five formerly failing
contracts now pass normally after the shared density repair; their markers
were removed. This includes the all-row coverage, B113 repair, PDF Minify
rename, non-JBIG2 scan selection, fractional-density and corpus-codec
inventory coverage, plus consistent overview/focused row pruning, actual
subset preparation, published-source guards and the 30 PNG-effect cases
described below. The latest focused 110-test run passes; the earlier 80-test
run and six-case / 30-PDF subset smoke also pass. This is regression
verification, not a new compression-time benchmark. Classic-Flate option
removal is still pending in [TODO.md](TODO.md) §217; this suite does not
certify that unimplemented change.

## Controlled experiment verification — 2026-10-17 (§242)

New code is limited to benchmark scope, strict compatible reuse, paired
report generation and tests; production rendering/UI/defaults are unchanged.
`test_png_extension.py` covers the eight new PNG row pairs, separate 16/64
palette and FFPR identities, exact metadata-only historical compatibility,
full-recipe reuse matching, real four-variant 300-DPI saves and unchanged
completed-job resume without re-encoding. Changed output hashes and partial
or changed-identity checkpoints are rejected.

`test_residual_stream_bench.py` checks the planned seven-row/42-pair scope,
actual shared-saver Flate/Zopfli files, identical encoded image bytes/native
decoding/300-DPI pixels, fixed-recipe gates, complete/missing/duplicate pairs
and unchanged-job reuse. Native-stream tests hold image encoding fixed;
they are not another image-codec comparison.

`test_experiment_publication.py` verifies measured signed-byte statistics,
reuse of pinned previous QPDF evidence, checking only missing supported
outputs, incomplete-study rejection and all 42 published paired percentages.
Direct actual-stream signatures distinguish a native-content change from
fixed image payloads. Publication checks encoded native-stream equality in
every PNG pair and encoded image-stream equality in every native A/B pair,
without re-rendering already verified page pixels.
The existing PNG publication test expands its byte/percentage/bold-emphasis
audit from 48 to 96 cells, with visible plain baselines for every row.

Corpus measurements are complete: 96 PNG pairs plus 42 native/residual pairs.
The PNG extension saves 80 missing PDFs and reuses 16 compatible focused
outputs; NATIVE-01 adds 30 actual Flate-reference PDFs. The independent audit
checks all **362 complete files / 471 displayed sizes / 138 signed changes**,
source/preparation/output hashes, same-fidelity bold minima and unchanged
focused data. Direct signatures prove encoded native equality in all 96 PNG
pairs and encoded-image equality in all 42 native pairs. QPDF checks pass 215
supported outputs, reusing pinned earlier results; 147 Brotli outputs are
excluded from that unsupported-reader check, not certified by it.

Evidence: `.tmp/compression-experiments/publication-20261017/`, including
`publication.json`, `final-publication.json`, `audit.json` and `qpdf.json`.
The final publication retains the later committed prose corrections without
changing any measured table or original producing identity. Full suite:
**654 passed**. This is worker verification, **not designer acceptance** or
all-reader certification. The desktop application was not launched.

### Earlier prototype verification (historical)

The earlier **552-test** verification aligned the final legacy-prototype
stencil caller with direct placement.
Two new 72/300-DPI fractional-page cases reproduced its clipping failure and
pass after the change; its full 15-test module passes, followed by the fresh
complete **552-test** run at that stage. The current matrix's frozen saver hashes are
unchanged by that separate prototype-tool correction.

An additional full rerun was interrupted by SIGTERM before a test summary;
it is not counted as a pass. The subsequent complete run at that stage passed.

## Already-JBIG2 no-op flow versus non-JBIG2 comparison scan (§233 / B114–B115)

`tests/test_jbig2_non_regression.py` pins the whole eight-page
`scan-jfk-poor-copies.pdf` by SHA-256, verifies its actual 1-bit JBIG2 streams
and proves that direct 300-DPI rendering equals every original bitmap sample.
The complete input is 349,667 bytes; the historical controlled-ID Zopfli
preserve-images control is 341,696, versus 354,089 for the faulty native BW
flow and 350,190 for FFPR. Those pre-repair preparations are not source-pixel-
exact no-ops even though their subsequent encoder checks pass.

The executable repair contract checks source-density rounding and real full
`save_with_spec` outputs, with native preservation and FFPR: unchanged page
geometry and original samples, valid 1-bit JBIG2, no input overwrite, and
complete file bytes no larger than source or the matching preserve-images
control. The repair retains actual fractional sampling density instead of
rounding up to integer DPI. All six cases pass normally, including all-page
pixel equality at 72 and 300 DPI; no expected-failure markers remain. Three
additional density cases preserve the real 299.5/300.25/301.75-DPI grids.
The combined flow/canvas modules pass 29 tests.

Fresh actual production saves have a 341,728-byte preserve-images control,
340,909-byte native output and 337,010-byte FFPR output. All eight original
image arrays, page geometry and complete page pixels at 72/300 DPI agree
exactly; encoded image bytes total the original 332,974 in every output.
The input hash is unchanged. These use normal production IDs; do not compare
them as a paired benchmark against historical controlled-ID saves. Evidence:
`.tmp/b114-fixed-verification/metrics.json`. B114 is worker-verified repaired,
but remains **OPEN** pending explicit designer confirmation. QPDF syntax/stream
checks pass all three fresh outputs, without claiming all-reader certification.

Normal and 2× isolated offscreen `tools/shot.py
examples/scan-jfk-poor-copies.pdf --progress-only` runs exit 0. Full windows
and 1:1 original/filtered pane and strip captures are actually viewed. The
selected preview comes from the completed real filtered file, not a separate
render/filter approximation. The desktop application remains closed.

The main BW comparison instead uses all eleven pages of
`scan-naca-tm972.pdf`: actual `/CCITTFaxDecode`, one-bit grayscale, about
300 DPI, scanned typewriting/annotations/diagrams with existing OCR text.
Selection tests require this complete non-JBIG2 source and independently
inspect stored filters. TODO §239's complete post-repair refresh measures all
42 replacement scan combinations before §§236/237 select the retained 34.
Every affected preparation is newly generated using the repaired compositor;
historical files/hashes stay untouched. All 291 retained displayed size cells
and tied bold minima are independently audited against 252 distinct actual
complete PDFs, including the new eleven-page source descriptor.

`tests/test_corpus_codecs.py` covers real JBIG2, CCITT, Flate, JPEG and native-
only sources while forbidding `extract_image()` for codec identification;
it also tests one-bit Flate and Poppler's actual encoding column. The corpus
README is audited against stored filters, not export extensions (B115).

## PDF Minify identity and settings migration (§230)

`tests/test_app_identity.py` adds 11 cases covering typed Qt values, saved
filters/UUIDs/order/names/parameters, last-file startup, existing destination
values, empty settings, malformed markers, repeated launches, deletion without
resurrection, read-only review snapshots and reported synchronization errors.
The real migrated MainWindow preserves deliberate post-DPI-migration values
without dirty state. CLI help and Qt machine/display identity use the new name.
An initial missing-`blurb` test fixture was corrected; the focused 11 cases and
fresh **572-test** full suite then pass. No product fallback or weakened oracle
was introduced to satisfy that fixture.

Normal and 2× offscreen `tools/shot.py examples/images.pdf --progress-only`
runs exit 0. Full-window and 1:1 strip/pane/junction images were actually
viewed. Both tools read a non-mutating settings snapshot before using isolated
review stores; the designer's actual name migration waits for a normal launch.
The package/asset audit verifies all 75 moved files exist, all 42 licensed
resources/notices are byte-identical, and all 18 headless modules change only
the logger namespace where applicable. Quotes, stable IDs and 96 local links
pass their audit. The desktop app remains closed; no designer acceptance is
claimed. NASA Kepler's sixth-column extension (§231) is verified below.

## Uniform 300 DPI, color FFPR and native-layer repairs (§§224–226)

`test_composition_repairs.py` and `test_native_layer.py` cover fractional
page edges at 72/150/300 DPI with higher-resolution readback; poisoned native
filter flags; repeated photo saves with no original photo-stream hashes or
new output diagnostics; orphaned whitespace ActualText with retained MCIDs,
Unicode metadata and real replacements; and all four color FFPR codecs,
including rotation and native-only pages. FFPR uses the same full-color,
one-resize preparation as production, not a separate benchmark renderer.

B111 coverage reproduces hidden-to-visible Form text-state inheritance and
asserts exact complete native-page pixels. Native foreground retains original
operators rather than sanitizing them; tests also check binary inline samples
containing false PDF keywords. The actual newspaper map and other pages retain
glyphs, paint, positions and subset-renumbered vector outlines. A validator
regression rejects invisible text even when extracted words are unchanged;
another rejects deleting a real space glyph despite unchanged letter positions.
Source extraction diagnostics are archived separately, cannot leak into the
next image-decode stage, and cannot excuse a new output-only diagnostic.

`test_filter_defaults.py` checks all six codecs, previous 72/150/200/600 DPI,
active and retained DPI fields, saved built-in overrides and custom copies,
stable UUID/name/non-DPI settings, one-time QSettings persistence, malformed
migration markers and deliberate post-migration values surviving another load.
All built-in/missing-DPI defaults are 300. No view-only sampling is treated as
filtering. Explicit Zopfli has no elapsed cutoff; a controlled subprocess test
verifies continuation beyond 120 seconds and cancellation/owned-process reaping.

Color FFPR lifecycle tests verify real saved files, effective keys, one shared
edit debounce, controls, dirty state and Revert. Offscreen
`tools/shot.py examples/images.pdf --compression-state-only` passes at 100%
and 2×. Full-window and 1:1 controls, panes, strip and junction captures were
actually viewed. They include all four color FFPR choices, 300-DPI saved
settings, native-mode restoration and saved BW FFPR Revert. Settings are
isolated; the desktop application stays closed.
Both offscreen state reviews were repeated after B112 at normal/2× scale,
exited normally, and the full window, 1:1 controls/strip/junction and actual
new tagged-map render were viewed.

The complete-source 300-DPI assembly preflight passes Indexed and colored
JBIG2 on all four image-bearing representatives, plus Flate/JBIG2 BW on the
eight-page photo document. Decoded samples and all-page renders remain exact;
source-native diagnostics stay separately attributed. Worker verification is
not designer acceptance; B108–B111 remain OPEN pending explicit confirmation.

Further 2026-10-16 audit: B112 exposed a gap in that first preflight. A valid
painted-page comparison does not establish removal of images retained through
the catalog structure tree. Its affected color measurements are not current
compression evidence. `test_tagged_composition.py` now covers page and Form
MCID scope, MCR `/Stm` ownership in the actual overlay, ParentTree, Alt text,
metadata/bookmarks/attachments, semantic image-only containers, shared Forms
across pages and incompatible tagged derivatives. A stale-tag fixture passes
the one-page-image count but is rejected by the new whole-file image gate.
Two targeted groups pass (62 tests each), followed by the fresh full
**552-test** suite. The renewed complete-source 300-DPI preflight passes
Indexed/colored JBIG2 for all four image-bearing representatives plus
Flate/JBIG2 BW on all eight photo pages. No new PDF/UA certification or
designer acceptance is implied.

## Representative integrated overview (§§223–240)

`tests/test_compression_overview.py`: 33 cases verify six distinct complete
repository inputs and their actual native/scan/photo/artwork/mixed/technical
structure, including Kepler's 12 text-bearing, ten vector-bearing and nine
image-bearing pages (15 image placements). The formatter requires all
34 realistic combination rows × six inputs = **204 measured cells**, including
redundant no-image recipes (§229 / TODO §234). Missing native-only measurements
are errors, not N/A; the runner saves 34 distinct outputs for an image-free
input even when every size is identical. Packed pixels/native policies use the same general
compressor; specialized-codec FFPR has one residual-stream row per recipe,
including color JPEG/JPX/indexed/stencil cases. Classic Flate remains only as
the unresampled reference under §§236/237. Descriptive transposed tables bold
ties only within the same document and fidelity group; missing measurements
are errors, not zero sizes.

Four real no-image cases in `tests/test_image_stream_bench.py` cover both BW
and indexed preparation, with plain and xref-stream source containers. Every
variant saves a separate PDF without thresholding, palette quantization,
image encoding or synthetic bitmap paint. Native artwork/pixels and actual
saved-ID readback are checked. B113 uses the existing container-only ID
normalizer exclusively for this formerly untested no-image path.

Source/preparation/output hashes, actual bytes and exact-verification flags
gate reuse without re-encoding. Explicit interrupted-study imports validate
the frozen implementation; changing source/provenance rejects reuse. A
pixel-invalid candidate is reported FAILED without a size/minimum and
does not hide independent valid variants. A rejected shared preparation is
reported PREP FAILED, not as independently failed downstream codecs. New
source-to-preparation diagnostics reject invalid production JPEG/JPX baselines
even when later saves/imports perfectly preserve them. These are reporting
and validation checks; the shared production repairs are covered above.

The runner reuses the original 14 strict integrated-encoder regressions
below. Full suite after the coverage and B113 changes:
**561 passed**, exit 0. `test_compression_scenarios.py`
adds four scope/provenance cases for nine focused scenarios / 62 additional
complete PDFs, all transformed cases at 300 DPI. No desktop launch performed.
Current published evidence and its exact counts
are in [INTEGRATED_COMPRESSION.md](INTEGRATED_COMPRESSION.md).

§§238–240 change only the PNG presentation: 26 baseline rows / 156 sizes and
a separate eight-row × six-document effect table / 48 measured sizes, with
signed percentage change against the matching measured baseline. The
measurement inventory and all output files remain unchanged. Thirty new
`tests/test_png_prediction_table.py` cases pin exact baseline denominators,
positive/negative/zero signs, rounding, paired wins/ties, all six columns,
same source/recipe/prepared pixels/native policy, independent files, missing
or invalid sizes/provenance, rejected outputs and the published 48 cells.
The 110-test focused run passes. An independent actual-file audit checks
all 156 baseline cells and 48 PNG effects against the original 252 saved-PDF
paths/sizes/hashes, confirms all signed changes, and requires focused data
and residual-stream rows to remain unchanged. No encoding, new codec or
residual-stream comparison was introduced before PNG-only designer review.
§242 subsequently authorizes expanded PNG coverage and the next controlled
experiment, documented separately above and in `COMPRESSION_EXPERIMENTS.md`.
The full post-split suite passes **635 tests**, with no expected failures.

§§236/237 narrow the current scope consistently: 34 overview rows / 204 cells,
and nine focused scenarios / 48 additional complete PDFs. The 33 overview
and ten focused regression cases pin the eight removed overview combinations,
absence of equivalent bitmap rows in every focused table, retention of the
unresampled Classic-Flate control, and preparation of only the five remaining
bitmap variants. The published whole-source descriptor must match the actual
runner input filename, page count and on-disk bytes, preventing another stale
JFK source row after a runner-only change. Prediction pairs and tied bold
minima remain; all retained no-image rows still require independent outputs.
A six-case actual subset-preparation smoke covers overview BW/indexed with
native/FFPR and focused BW/indexed, saving 30 exact-verified PDFs without the
removed variants. Preparation JSON no longer reports a first-variant
percentage mislabeled as Classic Flate when that variant was not selected.
No encoding, pixel, saver or standard import/resume verification is relaxed.

Historical six-case baseline before the §233 scan replacement: **252 verified overview PDFs**,
**62 focused PDFs**, **314 distinct actual final outputs**, zero rejected
or excluded cells. Kepler adds 42 separately saved/verified 12-page outputs;
all 210 previous overview cells/files and every focused table remained intact
at that stage. §233 replaces the scan, not the other five PDF inputs.
The 22 formerly missing no-image cells are also independently saved, never
filled by copying a control's size/file. Every transformed case is 300 DPI;
preserve-images controls are unresampled. At that stage all source/preparation/
output hashes, actual bytes and tied bold minima pass the publication audit.
The Markdown is one rendered table/header, four unnumbered title-only divider
rows and 42 measurement rows with seven cells (algorithm + six PDF cases).
All 252 sizes match their actual files; the first 210 cell strings are unchanged.

The frozen extension replays B113's bounded proof from pinned Git revision
`aa3cb847a75ca0f6acf65de5159ace85cc155847`, not mutable HEAD, and proves only
literal namespace substitutions in saver/verifier modules plus the added
document/docstring in the overview driver. Original measurements keep their
own source versions; new results retain the renamed implementation. The
combined manifest explicitly marks mixed provenance, without relaxing the
strict automatic cross-version import gate. A fresh full **572-test** suite
passes after the six-case code change. QPDF 12.2.0 syntax checks pass all
**207 ordinary-format final PDFs**; **107 Brotli outputs** are excluded from
that unsupported reader check, not certified by it. Across those historical tables,
93 plain/prediction pairs yield 12 wins, six no-image ties and 75 losses.
No timing rankings, CSV delivery, desktop launch or designer issue acceptance.

Historical mixed-DPI run, superseded by §§224/225/229: 138 applicable dispositions, **114 valid final
PDFs / 24 rejected or preparation-blocked cells**, plus 22 then-excluded
image-free cells. Thirty new valid outputs and 84 verified prior outputs;
focused tables bring the publication to 195 distinct actual PDFs. All
published values/minima and saved hashes are independently audited. B108
accounts for two rejected scan candidates; B109/B110 block 22 dependent
photo recipes. Those failures remain explicit, not measured codec losses.

## Original integrated cross-product verification (§222; historical scope)

`tests/test_integrated_compression_bench.py`: 14 focused tests cover all 21
bitmap/native combinations on actual multi-page color/BW/FFPR documents,
rotation, native text/vectors, metadata, annotations, links and attachments.
Checks include exact encoded/decoded images and decoded native bytes, actual
all-page pixels, final native filters and Brotli declarations, real JPEG/JPX
dispatch, complete-file sizes/hashes, no timing fields, changed-input/output
rejection, verified resume, explicit frozen-preparation provenance and tied
Markdown minima. A real embedded-font regression freezes native bytes across
policies: repeated TrueType subsetting rewrote eight checksum bytes. The
shared saver can skip re-subsetting an already-prepared artifact; ordinary
product calls retain the unchanged default of subsetting once.

The full integrated corpus passes: **51 recipes, 549 actual PDFs, 11 whole
inputs, 1,980 candidate pages**, all-page no-AA checks at 72dpi/recipe DPI.
Every final byte count/hash, source/prepared artifact hash, page count,
then-published matrix cell and tied bold minimum was independently checked.
The first rejected font-variant output is excluded, not counted as a success.
§223 replaces that publication layout with realistic combination rows over
five representative PDFs and focused scenario tables in
[INTEGRATED_COMPRESSION.md](INTEGRATED_COMPRESSION.md). The original 549
artifacts remain archived diagnostic evidence, not a recommended menu.
Fresh complete suite: **474 passed**, exit 0 / FULL SUITE GREEN. No desktop
launch or product codec/default change; no designer issue acceptance implied.

Current canon coverage (§§149/150/155): `test_filter_lifecycle.py` verifies every
real output file and exact final size, zero jobs on first/repeated selection
or view/DnD changes, one debounced edit, dirty markers, full effective keys,
every unsaved-dialog decision, canceled naming, late pending completions,
copy/source references, byte-identical PDF export, and canceled open/close.
It also checks selected-first submission, live-process-safe temp sweeping,
real JPEG/JPX/Indexed/BW saved-image readback, corrupt-output rejection, and
zlib-wrapped Zopfli output with validated fallback, UUID directory ownership,
identity stability, independent copies, and normal-exit PID cleanup.
`test_filter_identity.py` checks random non-MAC UUIDv4 generation, injected
collisions, pasted duplicate UUIDs/aliases, invalid/missing IDs, migration
persistence, and stable reloads. The pre-B81 flow/identity suite had 124 tests.
`test_minis.py` covers view/geometry/selection and actual caption pixels.
`test_strip_reorder_identity.py` reproduces the pre-fix armed Qt drag state;
verifies one drag controller, model-only order, repeated high-index moves/all
clicks and caption pixels with content refresh forbidden, UUID-addressed
updates, rejection of foreign model data, and duplicate persisted-order repair.
`test_minis.py` additionally checks §159: shared 4px top/bottom padding,
full amount captions, no hidden vertical range, and theme-derived strip-only
background across light/dark/live palette changes. Rendered color comparisons
use 8-bit RGBA, matching screenshot precision rather than QPalette's 16-bit color.
§§160–162 add 16 cases: every decision via dropdown and real mini click;
real Escape/Cancel/dialog-close after mouse, keyboard and reordered input;
saved/draft file and visible/current selection invariants; and Revert while
ready, debouncing or processing. Qt's two-step key selection must prompt once.
The standard Discard identity/destructive role retains the explicit label
"Discard Changes". The pre-centering full suite had 150 tests. Native smoke exercises the
11-filter layout, eight drag scenarios, 33 subsequent clicks, and actual dirty
mini Escape + Revert gestures at 100%/200%.
`QT_QPA_PLATFORM=offscreen ./.venv/bin/python tools/filter_smoke.py` captures
real completed files, dirty captions, the actual Qt prompt, canceled mini
selection, the standard Revert icon (§197), and Revert/Discard cleanup.
§§164/165 (B87) add 16 viewer cases: actual occupied bounds and horizontal/
vertical centering for one/two/five/nine pages, either-pane zoom with shared
grid positions, exact-fit transformed gaps without a trailing gap, and
resize-only reflow in either resize order. The real-file lifecycle test also
checks baseline/preview/mini grid agreement and centering with processing
submission forbidden. This stage's suite had 166 passing tests.
`tools/shot.py` captures the default one-page input, real two/seven-page
fixtures and stacked layout, including each full window and 1:1 pane/strip
images. Captures were viewed. It mirrors the designer's settings into an
isolated review store, never replaces their remembered input with fixtures.
§166 (B88) adds four cases: 640px/960px shrink across real debounce intervals,
splitter drags with metadata updates/processing forbidden, and full-content
paint-only elision with unchanged size hints/layout and readable theme ink.
Resize-stage full suite: **170 passed in 47.65s** (2026-10-14).
`tools/resize_smoke.py` measures ten seconds of actual 12-page geometry and
then squeezes the panel itself. Before repair: 23 reframes, last geometry
change at 3.955s. After: stable at 0.023s (100%) / 0.049s (200%), one normal
reframe, equal panes, unchanged prepared files/generation, native overflow.
Whole windows plus 1:1 headers/panels were viewed, as were standard shots.
The designer explicitly confirmed B88 in §167, independent of test results.
Run the full `./test.sh`; native DnD and viewed screenshots follow
`DEVELOPER_GUIDELINES.md`. Old speculative fixture/manual lists below are
historical planning, not evidence that their features are implemented.

## BW composition audit (§§168–171)

Actual saved-file regressions cover one combined image canvas, native text
and vector instructions/positions/colors/opacity, overlap, removed masks,
native overlays across formerly interleaved images, crop boxes/rotation/reused
forms, compose-first/full-color DPI-before-threshold, eligible original
font subsetting and high-zoom glyph rendering, real images.pdf, and PNG fallback.
Native-only pages stay native; annotations and links remain on copied pages.
Clip-only native text is kept as an actual PDF clip, never an invented mask.
FFPR checks every distinct page against its own thresholded source, pinning B90
for both JBIG2 and PNG; the saved-file benchmark repeats this on the corpus.

`tools/bench_bw_layers.py` records whole-file sizes, timing, encoded image/mask/
font bytes, retained words/positions, pixel-exact FFPR pages and independent
Poppler (`pdfimages`) decode of every saved 1-bit image. All algorithms and
outputs use the real saver; no preview estimates. Current evidence goes into
`COMPRESSION.md`, issues B89/B90 and TODO §§174–178 after final verification.

## Exact display and current certificate (§§172–176)

Display-stage full suite: **203 passed in 46.82s** (2026-10-14). Compression-stage
suite had 186; `test_exact_display.py` adds 16 real pixel/geometry/cache cases
and filter lifecycle adds one displayed-draft native-file ownership case.
The 16 display cases also pass with `QT_SCALE_FACTOR=2`: strict FFPR at
30/75/150/175/300/600dpi and five actual-view zooms; native text/vector detail
versus stretched prepared pixels; encoded color/gray/opacity; restoration of
filter settings on success/failure; bounded caches/closed PDF sources; and
pixel agreement between individual view and parent-window painting. The last
test reproduced a whole-window device-origin defect before its repair.

`QT_QPA_PLATFORM=offscreen .venv/bin/python tools/display_smoke.py` (also
`QT_SCALE_FACTOR=2`) captures real images.pdf at zoom 0.1/0.75/2/4. Actual
filtered viewport samples are 0/255 and artifact SHA-256/generation unchanged.
Metrics live in `.tmp/display-{1,2}x-metrics.json`; PNGs include whole windows
and 1:1 original/filtered panes/strips. Captures are actually viewed. Standard
`tools/shot.py` and `tools/filter_smoke.py` are also rerun/viewed after the
display change. These are worker verification, not designer issue acceptance.
Current platform/runtime scope is in `PLATFORMS.md`; proposed installed-artifact
release gates and build-only packages are in `PACKAGING.md`.

## Compose-first color/BW and precise controls (§§177–182)

Compose-first stage suite: **229 passed in 45.67s** (2026-10-14), `./test.sh`.
Twenty `test_color_canvas.py` cases cover hidden black RGB behind a separate
soft mask, overlapping alpha on a real colored backdrop, one full-color resize
before either color encoding or BW gray/threshold at 72/144/720dpi, all color
codecs, forced palette bounds, original path clips, four rotations and native
content, exact-DPI dimensions, tiled-native/global-resize seam detection,
native-only pages and owned scratch cleanup after render/resize failure/cancel.
Per-image extraction is forbidden during the order regressions. BW's earlier
per-image/stencil tests now assert the superseding canvas-first order, not the
discarded architecture. FFPR retains its independent complete-page reference.

Five `test_numeric.py` cases verify slider↔native spin-box synchronization,
single edit signals, blocked recipe loading, live keyboard typing, actual
spin-arrow clicks, bounds/no wrapping, accessible names and stable native
three-digit size hints. They also pass at `QT_SCALE_FACTOR=2`.
The lifecycle case types T=203, observes the immediate dirty marker, waits for
one debounced real recipe, reverts without work, then verifies disabled and
enabled pairs on filter selection. Existing dirty/Cancel/Save/copy cases pass.

Viewed captures: `tools/shot.py` numeric Threshold/Colors windows, 1:1 editors,
panes/strip, one/two/seven pages and stacked layout; `tools/filter_smoke.py`
dirty dialog, modal Escape with retained selection and Revert icon/result.
`tools/resize_smoke.py` passes at 100%/200% with equal panes and last geometry
changes at 0.136s/0.101s, no delayed divider drift, unchanged artifacts and
native overflow; full/1:1 panel captures were viewed. Exact-display smoke
passes at both scales with only 0/255 FFPR viewport samples at four zooms,
unchanged PDF SHA-256/generation and viewed captures.

Saved-file benchmark/independent decoder evidence and limitations are in
`COMPRESSION.md`, including 50 color and eight BW image-page decodes. Platform
and supervised desktop restart evidence is in `PLATFORMS.md`. This is worker
verification, not designer acceptance of B92 or older unconfirmed issues.

## Nearest palette and global debounce (§§183/184)

Palette/debounce-stage full suite: **244 passed in 64.42s** (2026-10-14), `./test.sh`.
`test_palette_nearest.py` adds eleven cases: independently brute-forced nearest
RGB assignment at 2/3/4/8/16/64/256 colors, true white backdrop retention,
non-wasted colored slots in white-heavy artwork, the discarded octree/white
fallback reproducer, exact adjacent few colors, agreement between packed
Indexed parts/RGB helper and actual saved images.pdf pixels at full 150dpi.
Five numeric plus eleven palette cases also pass at 2× (16 tests, 9.38s).

Four lifecycle regressions verify the ONE precise, single-shot 300ms trailing
timer. Interleaved native spin steps, slider, DPI, FFPR and page-size edits
restart it without early submission; final immutable recipe/file/preview agree.
Separate cases cover palette stepping/typing, strategy and lossless controls.
Existing cached-recipe/selection/view zero-processing tests still pass.

Fresh `tools/shot.py` captures 3/4/8/16-color real-file results as well as
normal controls/layout. Whole windows and 1:1 previews were viewed. Fresh
`tools/filter_smoke.py` additionally mixes three native spinner steps, a slider
change and typing to 3 colors: no submission at 220ms, exactly one final job,
matching current preview/size and cached Revert with no extra work. The actual
3-color dirty result and reverted 16-color captures were viewed. The five
default color PDFs were independently decoded again; `COMPRESSION.md` records
current sizes and distinguishes earlier-stage benchmarks from the final repair.
The designer confirms the palette improvement in §184; debounce tests alone
do not count as explicit designer confirmation of B94.

## Native mini progress overlays (initial §185 stage)

Initial stage full suite: **272 passed in 64.35s** (2026-10-14), `./test.sh`.
The width/height/backing/centering refinements below supersede this stage's
appearance, not its progress/lifecycle contract.
Twenty-eight new `test_minis.py` cases also pass at `QT_SCALE_FACTOR=2`
(2.02s). Compare delegate pixels to actual QProgressBar widget paint events,
not another hand-drawn implementation: Fusion/Windows styles, light/dark
palettes, selected/unselected states and 0/37/99% progress. Assert the full
150px reserved cell width, native height, centered position and genuinely
opaque white backing above the selection wash. Check the native label's
foreground pen as well as style, palette, font and locale/RTL updates.

Other cases forbid filtering/icon rebuilding for a model-role progress
update, verify completion removes bar AND backing without geometry changes,
and compare the selected-cell/drag-source/native-bar pixels plus uniform
75% exported ghost opacity. The default status bar's value/range stay intact;
the one hidden formatting widget remains hidden and consumes no input.

`tools/shot.py` passes at 100%/200%; actual viewed whole-window and 1:1 captures
include queued processing, a real debounced edit over the retained thumbnail,
and completion. A one-page edit may remain 0% until the next worker poll;
clearly named `progress-paint-fixture` captures additionally pin 0/37/99/65/12%
and completed states side by side. They are paint fixtures, not fabricated
worker progress. Default-bar and selected-source/ghost crops were also viewed.

Native X11 smoke passes at both scales: eight drag scenarios, correct visible
renumbering, 33 post-reorder clicks, Escape, dirty-mini Cancel and Revert, with
no filtering on selection/reorder. The extra 2× run initially missed a tail
drag start when independent scenarios pressed the same cell inside Qt's
double-click interval. The helper now spaces those independent gestures by
the platform interval and asserts a native press arrived; its full rerun
passes. Production drag handling is unchanged. Native window/strip/ghost
captures were viewed. That stage awaited acceptance; §192 later confirms
the final refined B95 appearance on 2026-10-14.
The available Qt style named Windows is not Windows OS certification.

## Shared spacing, Save As destination and enlarged mini bars (§§187–191)

Historical 1.5× stage below; §§198/199 supersede ONLY its mini bar/font
scale with 1.25×. Width, padding, centering, native rendering and lifecycle
requirements remain current. New verification is recorded below.

Final full suite, including §§192/195 and the prototype below:
**319 passed in 75.40s**, `./test.sh`, 2026-10-14.

2026-10-14 worker verification, not designer acceptance:

- Native progress overlays now leave the shared 4px highlight inset on both
  sides (142px within the 150px mini), use 1.5 times the status bar's native
  height and percentage font, and center in the FULL 162px frame, not the
  104px image area. The opaque backing is exactly the bar bounds; no added
  white padding. Thirty-two progress cases pass at normal scale (1.38s) and
  2× (2.29s), including both styles/themes, point/pixel font changes, actual
  frame heights/translated origins, untouched neighboring pixels, native
  locale/RTL, completion, no filtering and uniform 75% ghost opacity.
- The native-widget oracle paints at the SAME cell position and device
  scale as the delegate before cropping. Origin-zero versus translated
  painting otherwise exposes Qt's subpixel clip/gradient rounding rather
  than a product difference. No pixel tolerance was added: equality remains
  exact. The delegate uses native local coordinates for text/chunk clipping.
- Both-scale `tools/shot.py` runs pass. Actually viewed whole windows and
  1:1 strip/junction, explicit 0/37/99/65/12% paint fixtures, actual live
  edits, completion and selected ghost captures show the final appearance.
  Fixture percentages remain explicitly labelled, never fake worker work.
- Six real-frame geometry cases cover equal/stacked panes and wide/small
  windows, with no visible strip title, aligned sides/bottoms and shared 4px
  gutters. `tools/resize_smoke.py` passes at 100%/2×: last resize adjustment
  0.126s/0.115s, then stable for ten seconds; equal panes, squeezed panel
  overflow, no processing or metadata changes. Whole windows and 1:1
  header/panel/junction captures were viewed. Earlier combined 2× subset:
  59 passed in 16.13s (before the four newest progress cases were added).
- The full-suite resize regression now distinguishes an initial native
  horizontal scrollbar's one-metric height adjustment within 500ms from
  divider drift. Horizontal allocations must be stable immediately and the
  entire geometry stable thereafter; no production scrollbar workaround.
- Save As regressions cover Save/Discard/Cancel/Save As across dropdown,
  native mini mouse and keyboard entry; canceled AND blank names; direct
  Save As; pre-debounce drafts; pending/ready copies; and open/close
  resolution. New copy UUID, current/selected mini, dropdown, controls and
  exact-file preview agree; prepared work is reused and both files remain.
  `tools/filter_smoke.py` passes the actual dirty mini-click → modal Save As
  → real naming dialog → new-copy selection, with no extra real filtering.
  Both dialogs and selected-copy full window/strip captures were viewed.
- Final native X11 100% drag smoke passes (21:27:48–21:28:18): eight gestures,
  33 post-reorder clicks, correct visible numbers/UUIDs, 75% outside-strip
  ghost, Escape, dirty mini Cancel and Revert, no extra filtering. Captures
  were viewed. An additional earlier 2× native-caption pixel experiment
  remains inconclusive: after tail-last, one glyph in the correctly named
  T=180 label differs from the fresh-render oracle. No wrong name or UUID
  was found; no tolerance/forced repaint was added to hide it. This is not
  claimed as a product fix or a current all-green 2× native-drag certificate.

B95 is FIXED — DESIGNER CONFIRMED — 2026-10-14 (§192), scoped to progress.
B96/B97 remain OPEN pending their own explicit designer confirmation. Supervised
restart and current full-suite evidence are recorded in `PLATFORMS.md`.

## Proposed layered-color JBIG2 (§§192–194)

Design, benchmark protocol, measured full-PDF comparisons and remaining
integration decisions live in [LAYERED_COLOR_JBIG2.md](LAYERED_COLOR_JBIG2.md).
The prototype must prove disjoint-mask coverage, exact identical-palette RGB
reconstruction, actual PDF stencil filters/bit polarity, native-artwork
retention, multi-page independence and independent Poppler rendering.
No production codec/recipe/default change is authorized by this study.
Thirteen prototype tests pass (1.49s); 18 two-repeat benchmark cases cover 34
final-page pairs and 107 exact masks. App rendering and independent mask
decoding pass exactly; Poppler full-page differences and original-source
warnings remain explicit limitations, not a clean cross-viewer certificate.

## Matching Configuration header and no working placeholders (§§192/195)

All three regions use PaneHeader/PaneBlock. Existing six actual-frame cases
now assert equal header top/height, equal scroll-frame tops and shared
zero-margin composition, in equal/stacked modes at three window sizes.
Nine header/layout/resize regressions pass at both display scales.
Final `tools/resize_smoke.py` captures all three headers: last geometry change
0.099s at 100%, 0.182s at 2×, no further drift over ten seconds, native panel
overflow, no extra filtering. Actual full/small/squeezed windows and 1:1
Configuration headers were viewed, including queued/live/complete strips.

Eight new pending-label cases pin missing/cached images and amounts at
0/37/99/100%, no working/sizing/queued placeholders, transparent empty slots,
retained real byte metadata and no processing. Combined progress/layout/
pending subset: **46 passed** at 100% (2.14s) and 2× (2.53s). Final whole-
window and 1:1 `tools/shot.py` captures pass and were actually viewed at both
scales; a queued strip shows just its genuine native 0% bars, not fake work.
Full suite 319 passed; final app normally stopped/group verified/restarted.
B98/B101 remain OPEN for designer acceptance. B95 alone is confirmed (§192).

## Standard action icons (§§196/197)

One provider replaces the independent custom drawings and missing-icon paths.
Nineteen isolated icon tests cover native-theme precedence and individually
missing names, absent themes, stock SVG hashes/licenses, both source grids,
transparent backgrounds, light/dark contrast, normal/disabled/active modes,
1×/2× device pixels, control versus window/toolbar palette differences and
live refresh without actions. Main-window coverage verifies all eight action
bindings, enabled flags, selection, recipes/prepared files and zero new jobs.
The button lab uses the same provider.

Full suite: **339 passed in 71.05s**. The final icon/lab/main-window subset
passes at 2×: **33 passed in 4.04s**. Full `tools/shot.py` runs passed at both
scales; actual native Breeze and forced-fallback light/dark windows and 1:1
enabled/disabled action/toolbar crops were viewed. An initial dark-palette
diagnostic exposed stylesheet-polished children retaining light surfaces;
the provider now matches the actual control/toolbar background, and fresh
palette-specific windows make the visual fixtures consistent.

Extra normal-scale resize smoke passed: last adjustment 0.210s, stable for
ten seconds, aligned gutters/frames and native panel overflow, no processing;
full/squeezed captures viewed. The additional 2× run was interrupted with
exit 143 before completion, not called green. No production layout workaround
was added. An earlier full-suite run was likewise interrupted (143); the
complete rerun above is the regression evidence.

B102 remains OPEN pending designer acceptance; see `ICONS.md`.

## 25% mini progress enlargement (§§198/199)

The designer clarified 1.25× ORIGINAL height, not quarter-size. Native bar
height and percentage font share that factor; the independent actual-widget
oracle uses literal 1.25 rather than importing the implementation constant.
Reserved width, shared 4px insets, exact backing, full-frame centering,
aggregate status bar, selection, progress and no-filtering requirements stay
unchanged. Forty progress regressions pass at 100% (2.13s) and 2× (2.49s).
`tools/shot.py --progress-only` captures real queued/live/completed work,
explicitly named paint percentages, selected source/75% ghost and the
unchanged default bar without rerunning unrelated icon/grid review variants.
Both focused screenshot runs pass; actual full windows and 1:1 strips,
unchanged native status bars, selected sources and uniform 75% ghosts were
viewed at normal/2×. Final full suite: **339 passed in 68.67s**. The earlier
interrupted 2× resize left a stale PID-2 diagnostic lock; no matching live
diagnostic/test process remained in independent desktop checks. Only that
lock was moved to `/tmp/pdf-minimalist/diagnostic-pid2-lock-interrupted-20261014-2245`
for recovery; no PDFs, user drafts or live GUI files were removed, and the
canonical screenshot runs then completed normally. No production PID/session
design change was made to accommodate the harness's shared PID-2 namespaces.
B103 remains OPEN pending designer acceptance.

## Coded stock Icon Lab (§200)

`test_icon_lab.py` plus the actual-main-window menu regression cover 37 stable
code meanings, all seven action/four-family combinations, 121 original PNG
hashes/dimensions and notices/licenses, explicit-family loading without theme
fallback, light/dark normal/disabled/HiDPI rendering, initial no-selection,
cross-family row exclusivity, real radio mouse/keyboard events, preview clicks,
copy text, Clear, small-window scrolling and reusable modeless menu access.
The app-level test pins production icons, QSettings, recipes, prepared results,
selection and no new filtering. Focused **43 passed** at 100% (3.72s) and 2×
(4.37s). Full suite **382 passed in 78.93s**, `./test.sh`.

`QT_QPA_PLATFORM=offscreen .venv/bin/python tools/shot.py --icon-lab-only`
and its `QT_SCALE_FACTOR=2` run pass. Actual menu-opened full dialogs and 1:1
tables/cards were viewed: unselected state, selected light/dark fixtures,
lower Save/Stop/Zoom rows, and 640×520 scrolling in both directions. Enabled,
disabled, app-size and 32px previews all load real bundled stock artwork.
Stock shadows can contain nearly transparent (alpha=1) edge pixels: tests
require transparency/nonblank rendering and exact original hashes, not an
invented hard alpha cutoff. Mouse tests click the native radio indicator,
not blank stretched space outside Qt's normal radio hit region.

No production icon replacement has been inferred from the designer's rejection;
the new window is a review aid only. B102/B104 remain OPEN; see `ICON_LAB.md`.

## Editable image/native compression (§§203–205)

`tests/test_compression.py`: forty actual-PDF/core cases cover six distinct
image modes, final Filter/BitsPerComponent/stencil dictionaries, native text/
links, FFPR codec selection, multipage independence, identical layered/Indexed
page pixels at multiple zooms, missing encoders with no silent fallback,
leading-packed-whitespace transport, corrupt all-black decode recovery,
native/image key independence, eight native benchmark codecs, exact decoded
native bytes and unchanged images/metadata/attachments. Independent QPDF
decodes ordinary native filters; Brotli is explicitly not supported by the
installed older checker. Empty streams have NO filter: never embed MuPDF's
invalid zero-byte Brotli result. Encoder cancellation/unavailability is tested.

Seven main-window lifecycle cases prove all modes are editable without changing
UUID/name/order, precise threshold label/readout, proper enabled/fixed states,
one trailing timer for image/native/numeric edits, exact actual-file preview,
Save and fresh-default reload of a built-in override, Save As's actual mode
and native policy, retained source, Cancel/Discard transaction behavior and
correct inactive/restored BW-only FFPR state on color transitions. Six initial
focused cases passed at 2× (11.00s); the extra FFPR/updated inline-label subset
passed at normal scale. The final full suite includes all seven.

`tools/shot.py --compression-only` captures the real six image choices and
three native choices after genuine debounce/save/readback, with full windows,
1:1 panels/panes/minis and actual popup choices. Final normal shots were
viewed, including colored JBIG2, manual/automatic disabled controls and Brotli
warning, at normal/2×. Extra `--compression-state-only` full/1:1 captures at
both scales prove color keeps native artwork with the BW-only toggle off,
and Revert restores the saved FFPR state. Both-scale resize smokes pass on
real images.pdf: last geometry change 0.121s/0.315s, stable for ten seconds,
equal panes/aligned headers/4px gutters/native panel overflow and no filtering.
The actual filter lifecycle smoke passes; dirty, real modal Escape/Discard,
Save As new selection and icon/control captures were viewed. An initial
resize run was interrupted (143), not certified. Only a stale diagnostic
PID-2 `.process.lock` was moved to a recoverable dated name after verifying
its owner was gone; no production GUI lock/settings/data was touched. The first full suite
had 427 passes and one obsolete Strategy-label assertion; it was updated to
pin all five new qualified inline rows. The final full rerun is **429 passed
in 174.96s (2:54)**, `./test.sh`, 2026-10-15, exit 0. No production code
changed after that run; the final pass is documentation-only.
The inherited native/layered study limits remain documented; this integration
does not claim universal-viewer exactness or designer acceptance.

Native benchmark: `tools/bench_native_streams.py --repeat 2 --label main`,
32 source/policy cases, 64 outputs, 26 original pages (208 candidate page
comparisons per repeat). Exact bytes/word geometry/all-page MuPDF pixels and
unchanged image signatures pass; original-to-subset baseline is separately
pixel/word checked. Poppler passes ordinary codecs but fails Brotli content,
even when it returns zero; QPDF's ordinary checks/readback pass but Brotli
checks exit 2. Complete figures, CPU-time caveat, source diagnostics and
reproduction commands: `NATIVE_STREAM_COMPRESSION.md`.

A cancellation inside the native culler exposed the separate B107 worker-
error path; it remains OPEN, not treated as fixed by the green compression
suite or by the GUI's normal exit status.

### Designer acceptance checklist

B99/B100/B105/B106 remain OPEN; worker verification is not designer acceptance.
The acceptance review covers:

- All six Image compression choices, enabled parameters, precise Threshold
  method/readout and genuine JBIG2 Color output, without losing filter names
  or UUIDs. Color displays BW-only FFPR off; Revert restores its saved state.
- The independent PDF streams choices, one debounced real-file update,
  exact preview/size, Save/Save As persistence and Cancel retaining the
  edited filter. First/repeat selection and zoom must not reprocess.
- The explicit Brotli reader warning. Use a supporting reader for Brotli;
  the installed older Poppler/QPDF failures are expected, not hidden.
- Zopfli's encoding cost versus unchanged Flate compatibility; do not infer
  responsiveness from the noisy desktop timing samples.

This is a future review checklist, not a request to run heavy checks now or
permission to automatically launch the app. B107 needs a separate targeted
native-callback/process-pool cancellation regression before any repair claim.

The lightweight documentation audit also found inherited duplicate TODO
headings and B39. `git show HEAD` confirms both predate this work; numbering
was preserved and explanatory notes added, not rewritten to hide the history.
New request/issue IDs are unique. `git diff --check` passes; no new full-suite
claim is inferred from documentation-only checks.

## Size-only bitmap study (§209)

`tests/test_image_stream_bench.py`: 31 cases cover independent
PNG-predictor reversal and actual native PDF readback at 1/2/4/8bpc, odd row
padding, eight real saved variants on color/BW/native-overlay/FFPR pages,
rotation/annotations/links, one palette/threshold preparation, fixed native
Flate despite an inherited Brotli context, actual byte counts and absence of
timing fields. The current-Flate reference matches real production saver size
in all six fixture mode/rotation cases. Explicit missing encoders fail; existing
output directories and mismatched prepared-page counts are rejected. Resume
revalidates unchanged outputs without encoding again and rejects changed
preparation. A genuinely malformed native path regression preserves original/
output diagnostics without confusing them with image decoder errors.
Identifier framing is explicitly controlled: the initial byte-parity oracle
exposed random PDF IDs switching between literal/hex serialization (4 B in
one fixture), not different image/native stream bytes. Fixed-width distinct
IDs remove that noise without a size tolerance or changed product default.
The additional read-back/xref-stream test verifies that identifier control
changes the actual writer trailer, not only a copied xref dictionary. That
focused regression passes and is included in the complete final suite below.

`tools/bench_image_streams.py --smoke --label smoke-20261015` passes: two small
36dpi control cases / sixteen actual PDFs, exact image samples and all actual
page renders. This is a tool smoke, not the requested full-resolution corpus.
The full corpus then passes: **22 cases / 176 actual PDFs / 600 candidate
pages**, exact decoded samples/mask reconstruction and all-page MuPDF pixels
at 72dpi and recipe DPI. Final normalization/readback reuses all encoded
outputs, records output hashes and returns IMAGE STREAM SIZE BENCHMARK GREEN.
The JSON has zero timing fields; all current-Flate/plain-Flate reference
sizes agree. Both main tables retain all 154 case/variant size cells,
including the paired plain/PNG-predicted columns (§220). All cells were
mechanically checked against the unchanged JSON and actual PDF sizes/hashes.
The predictor recount is 60 larger / six smaller / zero equal; the six
exceptions save 1.25%–5.69% against their own plain counterparts and do not
change any case's winning algorithm. See
[IMAGE_STREAM_COMPRESSION.md](IMAGE_STREAM_COMPRESSION.md) for algorithm
results/limits. No UI/default-codec change or timing comparison; the shared
saver only has an optional preserved-ID flag with product default unchanged.

§221's Markdown emphasis is checked independently: each of the 22 main
comparison rows bolds exactly its minimum complete-PDF size (all tied minima
if present). All 154 numeric values, row labels and headers remain unchanged;
the saved dataset/PDF sizes and hashes are unaffected by this formatting.

Initial final-suite run: 459 passed / one pre-existing ghost pixel test failed.
Diagnosis reproduced it with a queued-event boundary: all filter jobs finished,
but resize/show had left the existing 150ms mini REFRAMING timer active;
the thumbnail changed between captures WITHOUT scrolling. The oracle compared
different view states, not a changed opacity/selection renderer. The test now
waits for that actual timer to settle BEFORE taking its first reference and
still crosses a full timer interval between strict pixel comparisons. No
production ghost/view behavior or pixel/opacity tolerance is changed. The
focused strict regression passes, and the final full rerun is **460 passed**,
`./test.sh`, 2026-10-15, exit 0 / FULL SUITE GREEN. This failed attempt is
retained as history, not reported as all green. No code changes follow the
successful full rerun; the remaining pass is documentation-only. A fresh
process check finds no desktop `python -m pdf_minimalist`; no app relaunch
was performed. Verification remains distinct from designer acceptance.

## Original v0.1 automated-test sketch (historical, not current coverage)
1. `test_threshold_simple`: 3×3 gray array, T=127 → exact 1-bit output.
2. `test_threshold_otsu`: synthetic bimodal image (half 50, half 200) → Otsu T in 100–150, output has both classes.
3. `test_threshold_adaptive`: gradient + dark corner → corner stays readable (no all-black).
4. `test_sauvola_stained`: yellowed-paper fixture → Sauvola keeps text, Simple@127 loses it (compare pixel counts).
5. `test_jpeg_smaller`: sample photo PDF image → q50 JPEG bytes < original PNG bytes.
6. `test_g4_roundtrip`: 1-bit image → G4 encode → decode → identical pixels.
7. `test_jbig2_if_present`: skip if no `jbig2` binary; else JBIG2 bytes < G4 bytes on text fixture.
8. `test_cancel`: 50-page fake job, set cancel after page 2 → pipeline aborts ≤5 pages, no output file left.
9. `test_esc_binding` (GUI smoke): root has `<Escape>` binding, Cancel button calls `token.cancel()`.
10. `test_no_overwrite`: save refuses to overwrite input path.

Fixtures to create in `tests/data/`:
- `scan_text_300dpi.png` (1 page, generated via PyMuPDF from text PDF)
- `yellowed_note.jpg` (photo of stained paper, or synthetic stains)
- `mixed_4pages.pdf` (text scan + photo + vector + blank)
- `born_digital_text.pdf` (selectable text, for warning test)

## Manual (LXDE Debian 13)
- [ ] DnD PDF from PCManFM onto app → opens. Button open works without tkdnd.
- [ ] Move threshold slider 0→255 → preview updates, extremes all-white/all-black.
- [ ] Per-page override page 3 to T=200, others global 170 → page 3 differs, rest same.
- [ ] Otsu on 10-page scan → readable, no hollow letters.
- [ ] Save BW: check size −60% or better on scans; open in Evince + MuPDF + Chromium.
- [ ] Save Color: JPEG q50 photo PDF −30% or better, no visible blocks at 100%.
- [ ] ESC during 20-page Max job → stops <1s, UI alive, partial file deleted.
- [ ] Simulate an unavailable `jbig2` using an isolated test PATH, without
  renaming system binaries: explicit JBIG2 must show a clear error and retain
  the saved file; deliberate Flate BW remains available. No silent G4 fallback.
- [ ] 1GB RAM limit (`systemd-run --scope -p MemoryMax=1G`) → 50-page PDF still completes (streaming, no OOM).
- [ ] No-network run (unplug) → everything works.

## General regression metrics (not the §209 size-only study)
Input bytes, output bytes, % saved, time sec, effort preset, strategy, T, DPI,
encoder (G4/JBIG2/JPEG/JP2), viewer check (Evince OK?), readability 1–5.

## Definition of done (v0.1)
- BW scan book: −70% size, readable at 100%, ESC works, no overwrite, opens in 3 viewers.
