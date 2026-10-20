# Controlled compression experiments

Designer §§238–271. The primary measured-size tables are in
[INTEGRATED_COMPRESSION.md](INTEGRATED_COMPRESSION.md); this document owns
the experiment plans, not a second scattered results analysis.

## LOSSY-05 — fixed q75 baseline throughout (§271; COMPLETE)

Restore the stable `101 − q` JPX mapping; hold JPEG q75/JPEG2000 q75 and
300 DPI constant across all six complete PDFs and native/FFPR modes. Keep
all other codec/profile/native/Best settings fixed. This is the approved
working baseline, not a proven equal-quality match. Per-image LOSSY-04 fits
do not supply experimental q values.

The primary inventory remains 24 complete PDFs: reuse the twelve unchanged
JPEG outputs with pinned source/producer/output provenance, and freshly
save twelve JPX outputs through the production saver. Verify identical
prepared RGB geometry/samples, actual JPEG payloads and native content per
pair; no reference JPEG drives JPX rate control. Reuse is rejected on any
source, payload, native or all-page readback mismatch.

The fixed-stream inventory remains 60 complete PDFs: reuse the thirty
unchanged JPEG controls, save thirty JPX controls from the completed JPX
preparations, and verify encoded images byte-for-byte, native decoded bytes,
metadata, geometry and 72/300-DPI page pixels. No control path composes,
resizes or re-encodes images. Update all main, binary, focused-photo and
residual-reference table cells, percentages, bold minima, labels and
conclusions from this one dataset. Preserve every historical manifest and
unaffected measurement; no estimated sizes, timing ranking or CSV.

Completed 2026-10-19: all **24 primary PDFs and 60 controls** are published
with actual sizes and hashes. Twelve primary JPEG files and thirty JPEG
controls were revalidated and reused; twelve primary JPX files and thirty
JPX controls were freshly saved. All 78 paired canvas samples and JPEG
payload fingerprints match; every output passes native/image/geometry and
all-page 72/300-DPI readback checks. All 36 ordinary-format controls also
pass QPDF checks; Brotli controls use the recorded supporting MuPDF decoder.
The four primary rows and all 22 affected supporting rows use the fixed
baseline. Provenance, measured results and caveats are centralized in the
integrated report. Visual review identified the pre-existing native-photo
overlay problem [B116](../issues.md#b116--open--native-overlay-brochure-output-obscures-some-source-artwork);
it is not fixed or claimed as original-appearance equivalence here.
The focused selection passes 193 tests; the full suite passes all 1008,
with no expected failures. See `TEST_PLAN.md` for scope and GUI review.
This completed measurement precedes the subsequent B116 compositor repair.
The integrated tables explicitly retain that producing scope, not repaired
native-photo sizes. `tools/check_b116.py` supplies separate real-file repair
validation without relabeling the old measurements.

## LOSSY-04 — conventional-q visual-quality matching (§§269/270; partial scope measured)

**Historical calibration diagnostics, not benchmark settings:** §271 rejects
per-image q selection and adopts one fixed q75/q75 pair for LOSSY-05. Retain
this experiment's actual observations without promoting its fitted values
to active size comparisons or app controls.

§270's consolidated sources and actual candidate derivation are in
[JPEG_JPEG2000_RESEARCH.md](JPEG_JPEG2000_RESEARCH.md). Execute the matching
experiment, not another ratio-only size study. Preserve JPEG q75 as the
reference and the familiar fixed q scale; independent quality observations
choose the JPEG2000 setting, not a desired percentage saving.

Keep the familiar 0–100 quality scales stable across GUI, recipes and
documentation. Use JPEG q75 as the reference and determine the JPEG2000
actual q that gives the closest practical visual match, not a renamed
JPEG-reference input or a predetermined file-size advantage. Published
visual-matching evidence supplies starting candidates, not a universal
q56 conversion. Use the same original prepared 300-DPI/full-resolution
colour pixels and fixed lossy profiles, with native and FFPR controlled
separately. Compare actual decoded outputs; the optional calibration
protocol in `LOSSY_IMAGE_QUALITY.md` describes metric-assisted and visual
checks. Do not make perfect universal calibration a blocker for a documented
practical matching baseline.

Record the real tested q values, backend mapping, matching evidence and
known content variation. If one fixed candidate is not an adequate corpus
baseline, report that evidence rather than silently normalize individual
images while labeling them all q75. Measure final complete PDFs at the
selected actual settings and propagate changes to all affected comparisons.
Preserve LOSSY-02/03 artifacts and unaffected BW/indexed/PNG/lossless data.
Completed research scope, 2026-10-19: all 78 original RGB canvases and
reference JPEG payloads were verified against LOSSY-02. The first encoded
canvas from each of eleven image-bearing native/FFPR cases was actually
matched by SSIMULACRA2, with PSNR diagnostics and decoded-pixel crop review.
The old fixed-ratio scale reaches the one-point tolerance on 5/11 cases;
the documented PSNR-control alternative reaches 9/11. Both scan cases fail
the integer-step tolerance and show visible white-area noise at the nearest
alternative setting; do not call them matched. The research document owns
actual q tables, named scale definitions, sources and proof hashes.

This research alone is not an all-page quality certificate, product-scale
correction or final-PDF size refresh. §271 subsequently selects the fixed
working baseline implemented and measured in LOSSY-05 above; the research
control does not redefine saved filters or supply per-image benchmark q.

## LOSSY-03 — historical normalized-q75 stream controls (§268)

Superseded by LOSSY-05 (§271). The following records the completed earlier
experiment, not the current fixed-q standard; its JPEG outputs are unchanged
and reused only after exact provenance/preparation/output verification.

The current quality standard is q75 for both codecs with JPEG 4:4:4 and
JPX's study-based JPEG-reference mapping, at 300 DPI. LOSSY-02 already saved
and verified all 24 native/FFPR main-table PDFs. Reuse those exact encoded
image preparations, including native opacity resources; no image encoder,
composition, resize or filter-preview path runs again.

Measure the remaining **60 actual complete PDFs**: Zopfli/Brotli controls
for each of the four lossy recipes and six inputs (48), and standard-Flate
FFPR references for the two lossy codecs across six inputs (12). Fixed pairs
vary general native/residual-stream compression only. Keep image streams
byte-identical, native decoded content/geometry/metadata identical and Brotli
declaration OFF; use the shared real saver and verify all pages at 72/300 DPI.
Source/baseline/output/implementation hashes guard imports and resume.
Never alias a control to a main-table file, even for a no-image/tie case.

One measured control supplies every table that needs that same case: fixed
Zopfli/Brotli effect and sizes, FFPR byte accounting, focused photography,
and Flate-reference residual effects. Preserve the unaffected BW/indexed/
lossless measurements and the already completed main matrix. Refresh active
lossy labels, percentages, minima, conclusions and tests; old q50/r192 and
fixed-ratio q75 files remain immutable historical evidence. No timing ranking,
CSV export, app/GUI change or universal visual-quality claim.

Completed 2026-10-19: **all 60 controls** were actually saved and verified,
reusing the 24 completed LOSSY-02 preparations. Each fixed pair preserves
encoded/decoded images, native content/geometry/metadata and every page's
72/300-DPI pixels. No image encoding runs. Twelve new FFPR byte partitions
close exactly; those streams make Brotli 2–14 bytes larger than Zopfli,
while standard Flate and Zopfli tie on all twelve current lossy FFPR files.
The same measurements update all 22 affected rows in the integrated report,
not duplicated experiments. `tools/bench_lossy_controls.py` owns measurement;
`tools/publish_lossy_controls.py` audits coverage/provenance and emits the
current table/fixture patch. The manifest/hash and actual sizes are centralized
in the integrated report; regression verification is in `TEST_PLAN.md`.

## LOSSY-02 — historical reference-normalized q75 comparison (§267)

Superseded by LOSSY-05 (§271). Its normalized JPX measurements are historical,
not fixed-q75 measurements or calibrated visual equivalence.

Replace only JPX's quality-to-ratio mapping: anchor each actual reference JPEG
at selected q75 to the 2007 visual study's approximate 40→45 / 60→73 ratios.
The exact interpolation and bounded outside-range heuristic are in
[LOSSY_IMAGE_QUALITY.md](LOSSY_IMAGE_QUALITY.md). Keep 300 DPI, prepared RGB,
JPEG 4:4:4, JPX 9/7/ICT, native/FFPR, stream policy and writer unchanged.
Observe the real internal JPEG reference without replacing any encoding.
Record its actual bytes/hash, raw sample count and chosen JPX ratio. In each
pair that reference must match the actual JPEG payload byte-for-byte.
Save/verify all 24 whole PDFs, publish the four current rows only and inspect
real output. This is a source-informed working quality baseline, not a
completed perceptual calibration. No timing ranking or new lossless study.
The old LOSSY-01 manifest stays immutable; current identities reject it.

Completed 2026-10-19: all 24 whole PDFs and 78 reference-JPEG/prepared-canvas
pairs per codec passed verification. JPEG2000 is smaller in the 11 image-
bearing pairs; the no-image case ties. Reference JPEG hashes and byte counts
match the paired actual JPEG payloads. The integrated report owns the final
sizes and percentage range; 16 canvases fall inside the studied anchor
interval, 62 use the explicit outside-range heuristic. These are measured
sizes under the approved working quality assumption, not a new perceptual
quality experiment. Output and proof hashes are pinned separately from the
unchanged LOSSY-01 and original fixed-encoder controls. §268 subsequently
refreshes active lossy fixed controls in LOSSY-03 above.

## LOSSY-01 — previous fixed-ratio q75 baseline (§§265/266)

Use equal q75 slider values as the working comparable-visual-quality baseline,
at 300 DPI and with identical full-resolution colour sampling. JPEG uses
4:4:4 and optimized Huffman coding; JPEG2000 uses one layer/tile, the lossy
9/7 wavelet and RGB colour decorrelation. Technical settings stay internal.
That study's JPEG2000 quality mapping was fixed (q75 → ratio 26).
Do not require an unrun perceptual calibration before producing measurements.

Measure all six representative whole PDFs with native text/vectors retained,
then FFPR, saving a separate real complete PDF for each codec: **24 outputs**.
No-image native cases remain independently saved sanity checks. Observe the
production encoder without changing its result and record identical prepared
RGB dimensions/sample hashes per pair. Validate actual embedded codec/payload,
retained native drawing/text/geometry, source/output hashes and all-page
decoding. Inspect screen-scale output and native 300-DPI pixel crops.
Record versions and current producing code; resume rejects changed identities
or altered outputs. Publish measured complete-file bytes in the integrated
analysis, with per-mode minima and no compute-time comparison or CSV.
Keep q50/r192 fixed-policy studies immutable and explicitly historical.
No new lossless competitor is needed. Report any observed visual differences
and codec regressions; the baseline assumption is not a measured universal
quality equivalence or a guarantee of JPEG2000 winning every file.

Completed 2026-10-19: all 24 outputs and their source/prepared-sample/codec/
native/all-page-render proofs were verified. `tools/bench_lossy_quality.py`
owns production-saver measurement; `tools/publish_lossy_quality.py` audits
completed files without re-encoding and pins the separate q75 fixture.
It reuses the B112 source-image validator and verifies unchanged native
opacity-resource images across both codecs. The current results replace only
the four lossy rows in the continuous integrated overview; no frozen PNG or
native/residual denominator changes. See the integrated report for sizes,
wins/losses and measurement provenance, and `TEST_PLAN.md` for verification.

## Shared protocol

One experiment changes one named factor. Hold the complete source PDF,
prepared raster samples/palette, 300-DPI transform, threshold/quality,
native drawing, save/ID policy and all other compressor choices constant.
Report actual complete saved PDF bytes and
`100 × (candidate bytes − baseline bytes) / baseline bytes`; negative is smaller.
Display signed percentage differences with exactly two decimal places, computed
from the original measured bytes. Normalize rounded zero to `+0.00%`; never bold
a percentage that rounds to zero. Percentage-only cells bold displayed negative
changes only. Exact byte-count emphasis remains based on the measured bytes.
Keep raw sizes/differences in the evidence when small changes round to zero.
In the results report, place NATIVE-02 immediately after PNG-02, before focused
scenarios, with its explanation intact (§§247–249).
Each side is a real, separately saved file. Freeze input/preparation/output
hashes, recipe, tool/package versions and the actual producing implementation.
Verify decoded images/native streams and every page at 72 and 300 DPI.
At publication, also compare actual encoded native-stream signatures across
each PNG pair and encoded image-stream signatures across each native A/B
pair. This proves the supposedly fixed side stayed fixed, not merely that
both saved files passed their individual preparation checks.
Keep failure diagnostics, no-image controls and reader-support limits visible.
No compute-time rankings, payload estimates, new GUI settings or default changes.

§251 subsequently changes the shared save default: omit the Brotli extension
declaration unless compatibility metadata is explicitly requested. Record this
setting in new benchmark identities and reject incompatible resume artifacts.
The original PNG/NATIVE-01/NATIVE-02 datasets used declaration ON and remain
immutable historical evidence. §254 requires the current tables to use
actually re-encoded, measured declaration-OFF Brotli outputs across all three
studies and their supporting component studies. Metadata-only ON controls stay
separate diagnostics, not current default-size entries. This ruling supersedes
the old instruction to retain automatic declaration in new saves.

Implementation: `tools/bench_png_extension.py` and
`tools/bench_residual_streams.py` call the existing shared bitmap preparation,
integrated saver and validators. `tools/publish_compression_experiments.py`
accepts completed manifests only and prepares Markdown plus frozen publication
evidence; it does not encode files or directly edit development documents.
`tools/bench_ffpr_compressors.py` reuses frozen specialized FFPR images,
measures the missing Brotli native saves and emits NATIVE-02 accounting,
metadata-only controls and the five-row effect table.

Reuse existing complete results only when their exact scope, files and
encoding implementation are compatible. Keep the original implementation
identity and proof; the current reporting/selection code is not retroactively
the encoder. Refuse arbitrary changed-code resume. Encoding a missing cell
does not require re-encoding compatible completed cells.

## Declaration-OFF Brotli refresh (§254)

§254 authorizes refreshing all integrated results for declaration OFF, not
just retaining historical ON tables in the primary analysis. Save new actual
complete files through the shared saver, rerunning every published Brotli
image/native encoding while holding prepared samples and other codecs fixed.
This includes supporting image/native studies, plain/PNG and measured levels
9/11. Record source/prepared/producer/output identities. Verify
unchanged rendered object graphs and raw stream signatures before reusing
the earlier all-page rendering evidence. Restore a forced catalog version
marker only with explicit old-producer/source proof; retain legitimate source
versions. No rasterization/filter preparation or assumed byte subtraction is
needed. A run-local cache may reuse freshly encoded identical stream inputs
at the same policy; no historical compressed payload substitutes for a current
Brotli encoding. Report only size, not compute-time comparisons.
Refresh overview/focused minima and both percentage tables from these measured
files; preserve old artifacts and publication manifests separately.

Implementation: `tools/refresh_brotli_tables.py` enumerates the 229 distinct
published Brotli files (177 integrated, 44 bitmap-component and eight
native-component), reruns their actual Brotli encodings and freezes per-output
proof. `tools/publish_brotli_refresh.py` validates the completed inventory,
normalizes only the old producer's proven absent-version marker, saves and
measures through the shared optimizer, and emits a patch for all tables and
regression fixtures. That metadata-only final save reuses this rerun's fresh
encoded streams. Never serialize an absent version as `/Version null`: remove
the dictionary key. Preserve actual source versions. `update_stream` also clears
image decoding parameters: restore existing PNG parameters, but do not add a
null `DecodeParms` entry to plain images. Tests cover both paths. A bounded,
hash-pinned import can reuse successful current-encoder checkpoints from an
interrupted attempt only after repeating graph/image/hash checks; rejected or
partial outputs are never imported or ranked.

## PNG-02 — palette and page-mode coverage

§258 separates the main Best-only matrix from all fixed-encoder controls.
PNG-02 retains its original fixed Zopfli/Brotli baseline recipes and measured
bytes; they are not new Best controls. See the protocol below.

§259 puts the [measured results and decision tree](INTEGRATED_COMPRESSION.md#results-and-decision-tree)
first in the PNG section. Branch on prepared output representation, then
encoder and actual BW/indexed content; keep corpus observations distinct from
universal rules. These versioned measurements preserve the chosen predictor.
§260 subsequently adds joint encoder/predictor selection to the app; these
fixed measurements are not relabeled as results of that search. Fixed
baseline sizes are always visible, not in a drawer. The §258 runner explicitly
requests predictor preservation when reproducing its frozen experiment.

Changed factor within every pair: reversible PNG image-row prediction OFF/ON.
General image and native policies remain paired Zopfli-Flate or Brotli.
The ON path is the existing predictor-15 implementation: adaptively choose
None/Sub/Up/Average/Paeth per packed row by minimum absolute signed-byte sum.
Keep that selector fixed; this study is not an exhaustive compressor-aware
search over every legal sequence of row filters.

Retain the existing BW/Otsu and five-color cases. Add up-to-16 and up-to-64
colors, both native-preserving and FFPR, over the same six complete PDFs:
W-9, CCITT NACA TM972, Crater Lake newspaper, artwork, mixed research paper,
and NASA Kepler. The extension adds eight rows / 48 pairs / 96 measured
PDF dispositions. Four native artwork/mixed palette cases already have
compatible focused-study pairs; reuse those verified files with provenance
instead of encoding them again. Remaining cells require new actual saves.

Publish measured plain baselines in the specialized fixed-encoder controls
(§258), not the Best-only overview. Under §243, the PNG
table shows only signed percentage changes computed from measured complete
files, with the shared precision/emphasis rules above; retain exact byte counts in frozen
measurement evidence. Focused and native/residual size tables remain separate;
§254 refreshes their Brotli cells too.
Keep palette targets as separate fidelity groups; actual palettes may contain
fewer colors. Never apply PNG row prediction to an already
JPEG/JPEG2000/JBIG2-encoded image payload.

The expanded table's 48 Brotli pairs have zero reductions, four no-image
ties and 44 increases. Under §244, underline its Brotli labels as a corpus
annotation, not a decoder limitation or universal obsolescence claim.
The earlier [noisy-BW control](IMAGE_STREAM_COMPRESSION.md#what-these-sizes-show)
is a real counterexample: the refreshed default-OFF Brotli files change from
83,266 to 80,852 bytes with prediction (-2.90%), but JBIG2 is still smaller
at 63,075 bytes.

Across all measured same-fidelity algorithms in the current representative
study, none of the 96 PNG candidates is a unique minimum: 92 are larger than
the minimum and four are image-free W-9 ties. Focused cases and the earlier
22-case image-stream study also have no PNG winner; the historical study's
66 PNG candidates are all larger than their same-case minima. Keep these
scopes separate rather than pooling overlapping or mixed-DPI studies.

This comparison includes limited-reader Brotli. Excluding Brotli leaves eight
strict PNG minima among the current measured alternatives: native-preserving
16/64-color TM972 and FFPR 16/64-color W-9, TM972 and mixed paper. All use
Zopfli-Flate. These 16/64-color groups do not include exhaustive layered-JBIG2
coverage, so they are measured-subset wins, not proof of global optimality.
Retain the distinction between best measured size with modern-reader support
and best available size for broader readers. No codec/optimization removal
or product-default change follows automatically from either observation.

## NATIVE-01 — native/residual-stream recompression

The next binary/A-B factor is the **native/residual-stream encoder**:
standard level-9 Flate (reference) versus the named optimized encoder.
Both sides use the same integrated saver, fixed-width ID policy, prepared
PDF, encoded image payloads, decoded native streams and container settings.
This is not an uncompressed-versus-compressed test or a product-menu proposal.
Classic Flate is only the controlled reference, not a restored product choice.

Use seven rows across all six whole PDFs (42 pairs):

| Fixed image treatment | Candidate native/residual encoder | Baseline |
|---|---|---|
| Preserve original encoded images; native-content control | Zopfli | Standard Flate |
| Preserve original encoded images; native-content control | Brotli | Standard Flate |
| BW/Otsu FFPR + JBIG2 | Zopfli | Standard Flate |
| Five-color FFPR + layered colored JBIG2 | Zopfli | Standard Flate |
| Full-color FFPR + JPEG q75 | Zopfli | Standard Flate |
| Full-color FFPR + JPEG2000 q75 | Zopfli | Standard Flate |
| Full-color FFPR + JPEG2000 lossless | Zopfli | Standard Flate |

The five FFPR rows isolate the residual optimization previously described
only in their labels. The native-preserving controls show the contrast when
fonts/text/vector programs remain. This intentionally scoped first experiment
does not repeat every image palette or PNG variant: those are separate factors.
All seven rows apply to every source, including image-free PDFs. §268
refreshes both lossy rows with fixed-q75 profiles via LOSSY-05 (§271); the original
q50/r192 files stay archived. The other five rows retain their measurements.

Reuse verified candidate outputs and the already measured preserve-images
Flate controls, with their original producing identities. Save the 30 missing
FFPR Flate-reference PDFs from exactly the candidates' prepared bases. Keep
the encoded image-stream snapshot byte-identical within each pair. Verify
native decoding and all-page 72/300-DPI pixels with the shared validator.

Publish candidate **complete-file bytes and signed change versus its measured
Flate reference**, with every reference size visible in an adjacent baseline
table. Negative is smaller. Count ties/regressions, not just wins. The Brotli
native control retains its reader-support warning; this test does not establish
interoperability. Results join the existing integrated report, not this plan.

## NATIVE-02 — FFPR Zopfli treatment versus Brotli baseline

Designer §§245/246. Scope is FFPR with specialized JBIG2 BW, five-color
layered JBIG2, JPEG q75, JPEG2000 q75 and JPEG2000 lossless—not
retained native text/vectors or packed-image compressor alternatives.
Change only native/residual-stream compression: Brotli baseline versus
Zopfli treatment. Encoded image payloads, source, recipe, 300-DPI samples,
native drawing, fixed-width ID framing and final save policy stay fixed.
§271 supplies the twelve current fixed-q75 pairs through LOSSY-05; the
other eighteen retain their verified evidence. LOSSY-03's normalized-q
pairs and the original q50/r192 pairs remain historical.

Use five rows over all six whole PDFs (30 pairs). Reuse the verified Zopfli
candidates from NATIVE-01. Save the 30 missing actual Brotli baselines from
the very same frozen preparations through the existing integrated saver.
Do not threshold, resize or re-encode any image. Keep all original producing
identities; check unchanged encoding sources, packages/binaries and actual
source/preparation/output hashes rather than relaxing normal resume checks.

The table reports
`100 × (Zopfli bytes − Brotli bytes) / Brotli bytes`;
negative favors Zopfli, positive favors Brotli. Bold displayed negative
percentages only. A rounded +0.00% is not necessarily an exact tie; leave it
unbolded and retain raw sizes and paired evidence (§§248/249).

Use the shared two-decimal precision, including for tiny complete-file changes
in large image-dominated PDFs. Preserve raw baseline/treatment byte counts in
frozen evidence. Verify exact decoded native/image data, encoded image
signatures and all-page 72/300-DPI pixels with the existing shared validator.
Completed Zopfli renders remain reusable; new Brotli saves pass their own
full verification. Report actual failures, never a fake size or minimum.

For each pair, account actual encoded image, native, object/xref-container
and other stream bytes plus the remaining PDF syntax. Their deltas must sum
exactly to the measured complete-file difference. Inspect the writer's
Brotli extension declaration and use metadata-only controls (Zopfli streams
with that declaration) to separate declaration/container overhead from
native-payload differences. Never substitute payload estimates for final
size; diagnostics explain the measured whole-file outcome. The extension's
§4 recommends the declaration (SHOULD), not an unconditional SHALL; distinguish
current writer overhead from a format-imposed minimum. Retain the existing
declaration policy in the original frozen experiment. New saves follow §251's
opt-in default. §254 supplies newly encoded/measured default-OFF replacements
for current tables; it does not relabel old files. In the refreshed 30 pairs,
the declaration is absent on both sides, with exact accounting still required.

The corpus contains one one-page input and five multipage inputs. Their
content differs: this is not a controlled test of page count. Compression operates on
individual PDF streams, not one whole-document dictionary automatically
shared across all pages. Never derive an encoder-selection threshold from
page count alone.

Table labels use **Zopfli**. In this PDF context it always produces standard
FlateDecode data; there is no second Zopfli format to distinguish in these
tables. Explain the encoder/decoder distinction in prose, not every row.
See [the Zopfli project](https://github.com/google/zopfli#readme).
This reporting change does not rename stored policies, UI controls or frozen
measurement labels. Reader eligibility remains separate from the size result.

## Best-only overview and expanded binary reference (§258)

The main matrix measures Best through the existing production saver for
19 image/reference recipes across six whole PDFs: 114 actual saved outputs.
Its row labels name only the image recipe/fidelity; section prose owns the
Best explanation and link to the controlled fixed-encoder comparison.
Reuse hash-verified frozen prepared PDFs, not a guessed minimum of previous
Zopfli/Brotli file sizes. Preserve image samples/palettes/predictors, native
geometry, protected J* bytes and source/catalog semantics. Best makes no
reader-compatibility guarantee beyond its existing Brotli-capable boundary.

The specialized binary section expands to the same 19 recipes: Brotli is
the baseline and Zopfli the treatment, with the existing two-decimal signed
full-file percentages. For packed BW/indexed rows, the single general-encoder
factor covers both sample-image and native streams; for J* and original-image
references it changes native/residual streams only. Do not describe the former
as an image-byte-fixed experiment. The existing NATIVE-02 five FFPR/J* rows
and their exact accounting remain separately identified within that section.
PNG-02 still compares each fixed encoder's own OFF/ON files; it must not use
the new Best matrix as its denominator. Keep the Classic-Flate control and
all historical fixed-encoder sizes as reference evidence outside the main
Best-only table. No new image processing, GUI policy or default migration is
authorized or needed for this reporting change.

## Proposed next — JBIG2-01: repeated-row prediction OFF/ON

**Proposed, not executed or approved for product integration.** NATIVE-01
above is already complete; do not repeat it as the next experiment. This is
the first bounded step in existing [JBIG2 optimization TODO §240](TODO.md#240--open-designer-234-explore-jbig2-optimization-features).

Change only generic-region typical prediction: baseline `jbig2 -p` versus
candidate `jbig2 -p -d`. The upstream CLI calls this duplicate-line removal;
it predicts repeated rows losslessly, rather than deleting pixels or changing
thresholding. See [the upstream CLI](https://github.com/agl/jbig2enc/blob/master/src/jbig2.cc)
and [generic API](https://github.com/agl/jbig2enc/blob/master/src/jbig2enc.h).

Use four rows over the same six whole representative PDFs (24 pairs):
BW/Otsu native-preserving and FFPR, and five-color layered JBIG2
native-preserving and FFPR. Hold 300 DPI, prepared samples/palette, native
Zopfli-Flate compression, geometry, PDF assembly and ID policy fixed.
Keep image-free native cases as independently saved no-op controls. Reuse
compatible verified OFF files only with original provenance; do not silently
weaken changed-code resume checks or label an old file newly encoded.

Compare measured complete-file percentage changes against each OFF baseline,
with visible baseline bytes, negative meaning smaller. Decode every image/
stencil exactly and compare all-page pixels/native content. The upstream
API retains historical growth/Ghostscript warnings: check actual MuPDF,
Poppler and Ghostscript decoding, record unsupported/failing readers, and
never count an invalid file as a size win. See [JBIG2.md](JBIG2.md#generic-coding-and--d).
No timing rankings, lossy symbol coding, new UI option or default change.
Add focused synthetic repeated-row/noisy cases only as a separate follow-up
if the representative results need explanation.

## Implementation status — 2026-10-17

PNG-02, NATIVE-01 and NATIVE-02 are implemented and worker-verified. The
JBIG2-01 study remains a proposal. Results remain centralized:
[PNG paired effects](INTEGRATED_COMPRESSION.md#png-prediction--measured-effect-versus-baseline)
[native/residual paired effects](INTEGRATED_COMPRESSION.md#nativeresidual-streams--measured-effect-versus-flate-reference)
and [FFPR Zopfli versus Brotli](INTEGRATED_COMPRESSION.md#ffpr-residual-compression--zopfli-versus-brotli-baseline).
Reproduction evidence, full-suite results and independent publication checks
are recorded in [TEST_PLAN.md](TEST_PLAN.md#current-regression-verification--2026-10-17).
This does not imply designer acceptance, new product defaults or additional
reader/platform certification.
