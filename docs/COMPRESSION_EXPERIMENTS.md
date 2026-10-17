# Controlled compression experiments

Designer §§238–242. The primary measured-size tables are in
[INTEGRATED_COMPRESSION.md](INTEGRATED_COMPRESSION.md); this document owns
the experiment plans, not a second scattered results analysis.

## Shared protocol

One experiment changes one named factor. Hold the complete source PDF,
prepared raster samples/palette, 300-DPI transform, threshold/quality,
native drawing, save/ID policy and all other compressor choices constant.
Report actual complete saved PDF bytes and
`100 × (candidate bytes − baseline bytes) / baseline bytes`; negative is smaller.
Each side is a real, separately saved file. Freeze input/preparation/output
hashes, recipe, tool/package versions and the actual producing implementation.
Verify decoded images/native streams and every page at 72 and 300 DPI.
At publication, also compare actual encoded native-stream signatures across
each PNG pair and encoded image-stream signatures across each native A/B
pair. This proves the supposedly fixed side stayed fixed, not merely that
both saved files passed their individual preparation checks.
Keep failure diagnostics, no-image controls and reader-support limits visible.
No compute-time rankings, payload estimates, new GUI settings or default changes.

Implementation: `tools/bench_png_extension.py` and
`tools/bench_residual_streams.py` call the existing shared bitmap preparation,
integrated saver and validators. `tools/publish_compression_experiments.py`
accepts completed manifests only and prepares Markdown plus frozen publication
evidence; it does not encode files or directly edit development documents.

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

Publish measured plain baseline rows in the overview and PNG version bytes
with signed change in the PNG table. Keep palette targets as separate
fidelity groups; actual palettes may contain fewer colors. Never apply PNG
row prediction to an already JPEG/JPEG2000/JBIG2-encoded image payload.

The initial table's Brotli results show no reduction in this corpus. Expand
coverage before generalizing; record all wins/ties/losses and explain no-image
ties separately. This is not authority to remove a codec or optimization.

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
| Preserve original encoded images; native-content control | Zopfli-Flate | Standard Flate |
| Preserve original encoded images; native-content control | Brotli | Standard Flate |
| BW/Otsu FFPR + JBIG2 | Zopfli-Flate | Standard Flate |
| Five-color FFPR + layered colored JBIG2 | Zopfli-Flate | Standard Flate |
| Full-color FFPR + JPEG q50 | Zopfli-Flate | Standard Flate |
| Full-color FFPR + JPEG2000 lossy r192 | Zopfli-Flate | Standard Flate |
| Full-color FFPR + JPEG2000 lossless | Zopfli-Flate | Standard Flate |

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

## Implementation status — 2026-10-17

Both plans are implemented and worker-verified. Results remain centralized:
[PNG paired effects](INTEGRATED_COMPRESSION.md#png-prediction--measured-effect-versus-baseline)
and [native/residual paired effects](INTEGRATED_COMPRESSION.md#nativeresidual-streams--measured-effect-versus-flate-reference).
Reproduction evidence, full-suite results and independent publication checks
are recorded in [TEST_PLAN.md](TEST_PLAN.md#controlled-experiment-verification--2026-10-17-242).
This does not imply designer acceptance, new product defaults or additional
reader/platform certification.
