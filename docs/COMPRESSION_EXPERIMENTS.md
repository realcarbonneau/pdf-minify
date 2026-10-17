# Controlled compression experiments

Designer §§238–251. The primary measured-size tables are in
[INTEGRATED_COMPRESSION.md](INTEGRATED_COMPRESSION.md); this document owns
the experiment plans, not a second scattered results analysis.

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
The completed PNG/NATIVE-01/NATIVE-02 datasets below used declaration ON;
their frozen files and measured tables remain historical evidence, not new
default-OFF measurements. Metadata-only controls explicitly opt in. This ruling
supersedes the old instruction to retain automatic declaration in new saves.

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

## PNG-02 — palette and page-mode coverage

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

Publish measured plain baseline rows in the overview. Under §243, the PNG
table shows only signed percentage changes computed from measured complete
files, with the shared precision/emphasis rules above; retain exact byte counts in frozen
measurement evidence. Focused and native/residual sizes are unchanged.
Keep palette targets as separate fidelity groups; actual palettes may contain
fewer colors. Never apply PNG row prediction to an already
JPEG/JPEG2000/JBIG2-encoded image payload.

The expanded table's 48 Brotli pairs have zero reductions, four no-image
ties and 44 increases. Under §244, underline its Brotli labels as a corpus
annotation, not a decoder limitation or universal obsolescence claim.
The earlier [noisy-BW control](IMAGE_STREAM_COMPRESSION.md#what-these-sizes-show)
is a real counterexample: Brotli changes from 83,432 to 81,018 bytes with
prediction (-2.89%), but JBIG2 is still smaller at 63,075 bytes.

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
| Full-color FFPR + JPEG q50 | Zopfli | Standard Flate |
| Full-color FFPR + JPEG2000 lossy r192 | Zopfli | Standard Flate |
| Full-color FFPR + JPEG2000 lossless | Zopfli | Standard Flate |

The five FFPR rows isolate the residual optimization previously described
only in their labels. The native-preserving controls show the contrast when
fonts/text/vector programs remain. This intentionally scoped first experiment
does not repeat every image palette or PNG variant: those are separate factors.
All seven rows apply to every source, including image-free PDFs.

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
layered JBIG2, JPEG q50, JPEG2000 lossy r192 and JPEG2000 lossless—not
retained native text/vectors or packed-image compressor alternatives.
Change only native/residual-stream compression: Brotli baseline versus
Zopfli treatment. Encoded image payloads, source, recipe, 300-DPI samples,
native drawing, fixed-width ID framing and final save policy stay fixed.

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
declaration policy in the frozen experiment. New saves follow §251's opt-in
default; do not relabel the old results as declaration-OFF measurements.

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
