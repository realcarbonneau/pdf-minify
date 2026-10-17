# JBIG2 — developer guide and optimization exploration

Designer §§233/234; [TODO §240](TODO.md#240--open-designer-234-explore-jbig2-optimization-features).
Capability review: 2026-10-16. **The current encoder path is implemented;
additional optimizations below are research, not implemented choices.**

Primary final-size results: [INTEGRATED_COMPRESSION.md](INTEGRATED_COMPRESSION.md).
Preparation/native-artwork policy: [COMPRESSION.md](COMPRESSION.md).
Colored masks: [LAYERED_COLOR_JBIG2.md](LAYERED_COLOR_JBIG2.md).
Reader/combination policy: [COMPRESSION_COMBINATIONS.md](COMPRESSION_COMBINATIONS.md).

## Representation and current flow

JBIG2 encodes **one-bit images**, not native PDF characters, vectors, RGB
photographs or palette indices directly. In a scan, characters are pixels;
encoding their shapes does not create searchable text. Original native text,
including OCR, stays separate when FFPR is off.

The established flow composes the original image layer in full color (the
whole page with FFPR), resizes once to target DPI, then thresholds or maps
the palette. BW produces one binary canvas. JBIG2 Color produces disjoint
one-bit stencils, one per used non-white palette color, painted in that color.
They use the same exact palette map as Indexed, not a color JBIG2 extension.

`core/pipeline.py:encode_binary_jbig2` supplies a precomputed one-bit PNG to:

```text
jbig2 -p <one-bit-input.png>
```

PNG is input transport only. Returned bytes become actual `/JBIG2Decode`
streams, never Flate/PNG bytes mislabeled as JBIG2. Each page/mask is encoded
independently as a self-contained generic region, without shared symbols or
`/JBIG2Globals`. Test-decoding must reproduce its requested samples exactly;
new warnings/error placeholders fail validation. An explicitly selected
JBIG2 failure is an error, not silent Flate fallback. The older automatic
helper's fallback contract is not the explicit GUI codec.

The current wrapper also has a 120-second subprocess timeout per encode.
An explicit codec reports failure rather than substituting an easier encoder;
do not turn such a guard into a size/effort ranking or silently discard valid
optimization candidates because of encoding cost. Research must distinguish
actual encoder failure, cancellation/resource policy and measured size.

Installed encoder: **jbig2enc 0.30**. The GUI selects JBIG2 BW/JBIG2 Color,
but exposes none of the advanced switches below. Otsu/manual threshold
controls prepare pixels; they do **not** adjust lowercase `-t` symbol matching.
Actual code: [pipeline.py](../pdf_minify/core/pipeline.py),
[stencils.py](../pdf_minify/core/stencils.py).

## Feature inventory: capability versus current use

| Feature | Used now? | Fidelity/dependencies | Exploration required |
|---|---|---|---|
| `-p` PDF-ready output | Yes | PDF stream framing, not an effort setting | Retain valid framing and exact decoding. |
| `-d` duplicate-line / typical prediction | No | Lossless generic-region prediction; does not delete image rows | Compare on/off, complete bytes and readers; a size win is not assumed. |
| `-s` symbol mode | No | Dictionary of raster shapes; approximate matching can change characters/pixels | Keep lossy research separate; never silently enable under a lossless label. |
| `-t 0.92` classification similarity | Inactive without `-s` | Installed default; symbol matching, not BW binarization | Evaluate jointly with matching/refinement and explicit exactness criteria. |
| `-w 0.50` classification weighting | Inactive without `-s` | Installed default; affects symbol classification | Not an independent generic-mode optimization. |
| `-r` refinement | No; unavailable in reviewed CLI | Can represent symbol differences in principle; implementation rejects the option as broken | Find a maintained working zero-error implementation before claiming lossless support. |
| Cross-page/shared symbol dictionary | No | Sharing is not inherently lossy; classification/refinement determines fidelity | Compare shared/grouped/per-page scopes, including globals/reference overhead and readers. |

Installed `jbig2 --help` reports those defaults. `jbig2 -r` exits 1 before
reading input. Reviewed upstream also rejects refinement and defaults to
generic coding without duplicate-line prediction. Sources:
[upstream CLI](https://github.com/agl/jbig2enc/blob/master/src/jbig2.cc),
[README](https://github.com/agl/jbig2enc#readme).

### Generic coding and `-d`

Typical prediction lets the decoder reconstruct repeated rows; it is not
despeckling, line deletion, interpolation or a threshold change. Current
production does not try it. The upstream API's older comments warn of output
growth and Ghostscript problems. These are reasons to verify current readers,
not evidence that all current Ghostscript versions fail or that `-d` always
grows files. See [the generic API](https://github.com/agl/jbig2enc/blob/master/src/jbig2enc.h).

Proposed experiment: encode identical prepared samples with prediction off/on,
validate each sample, then compare complete PDFs through the shared saver.
If both satisfy the required reader tier, a best-size encoder could choose
the smaller automatically. This is not implemented, and is not a proposed
speed/effort GUI knob. Encoding time is not a selection criterion (§213).

### Symbols and refinement

Visually similar glyphs need not be identical. Merging them can substitute
digits, letters, punctuation or mathematical marks. A higher matching
threshold or different weighting does not establish losslessness. Symbol
coding also does not retain/create the original PDF's font/text objects.

Do not simply remove upstream's refinement rejection. Its API describes an
allowed pixel-error tolerance per symbol, and currently unreachable CLI
refinement code passes a nonzero value. A future working path must require
**zero sample differences**, not assume a flag named refinement guarantees
exactness. Sources: [refinement API](https://github.com/agl/jbig2enc/blob/master/src/jbig2enc.h),
[CLI configuration](https://github.com/agl/jbig2enc/blob/master/src/jbig2.cc).

If symbol research proceeds, `-a`/`--auto-thresh` and `--no-hash` are additional
classification candidates, not lossless generic switches. They must not
silently replace the app's ruled Otsu/manual image preparation. The API
describes automatic classification as grouping symbols under representatives:
[symbol API](https://github.com/agl/jbig2enc/blob/master/src/jbig2enc.h).

### Multi-page dictionaries and PDF embedding

Upstream exposes a context that collects pages before producing a symbol
table and page streams. Our independent per-page invocation does not use
that workflow. Existing whole-image PDF deduplication is a different mechanism.
See [the multi-page API](https://github.com/agl/jbig2enc/blob/master/src/jbig2enc.h).

A shared-dictionary PDF must embed its global segments and supply their
`/JBIG2Globals` decode-parameter reference for each dependent image. Count
global bytes, page streams, references and container overhead in final sizes.
Small/heterogeneous documents may not repay dictionary overhead. Compare
document-wide, grouped and per-page scopes only at equal decoded samples and
reader requirements. Embedding references:
[upstream's globals-aware PDF example](https://github.com/agl/jbig2enc/blob/master/jbig2topdf.py),
[ISO 32000-1, §7.4.7](https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf).

Test page extraction/subsetting with required globals, ordering, repeated
saves and missing/corrupted dependencies. A globals-dependent page stream
is not standalone. Per-page MuPDF equality and syntax-only QPDF success do
not certify all readers or a complete multi-page implementation.

## End-to-end regression: B114 repaired, awaiting designer confirmation

Whole `examples/scan-jfk-poor-copies.pdf` (eight pages) already uses JBIG2.
At unchanged 300 DPI with lossless JBIG2 and no intended appearance change,
the complete save must retain original bitmap samples/page geometry and not
grow relative to the input and an equivalent preserve-images control (§233).
Cover native and FFPR. Encoder equality against an already altered prepared
image is insufficient for this source-to-output contract.

The former defect rounded about 300.000014 DPI to 301 and resized back to
300 before Otsu, changing 141,203 samples. The shared compositor now retains
the actual fractional density rather than quantizing it to whole DPI (§235).
This keeps the original device grid without special-casing a document or
rounding genuinely fractional resolutions. No JBIG2 encoder settings changed.
[B114](../issues.md#b114--open--same-dpi-jbig2-flow-resamples-and-increases-an-already-compressed-scan)
records the diagnosis and historical sizes.

Fresh real production saves, 2026-10-16, all eight original pages:

| Same source / unchanged 300 DPI | Complete PDF bytes | Original bitmap samples and page pixels at 72/300 DPI |
|---|---:|---|
| Untouched input | 349,667 | Reference |
| Preserve images + Zopfli-Flate streams | 341,728 | Exact |
| BW + Otsu + JBIG2 + Zopfli-Flate streams | 340,909 | Exact |
| BW FFPR + Otsu + JBIG2 + Zopfli-Flate streams | 337,010 | Exact |

These are no-op regression results, not a codec ranking or evidence that FFPR
is equivalent to native preservation for other documents. Each saved output's
encoded image payload totals 332,974 bytes, equal to the original count. The regular
production ID framing is used here; historical controlled-ID benchmark numbers
must not be mixed with these file sizes. Actual files, hashes and implementation
identity are in `.tmp/b114-fixed-verification/metrics.json`.

[test_jbig2_non_regression.py](../tests/test_jbig2_non_regression.py) now has
six normally passing cases, including both actual full-file save paths and
all-page 72/300-DPI pixel equality. The five former expected-failure markers
are removed, not relaxed. Three additional real-PDF density cases cover
299.5, 300.25 and 301.75 DPI. Worker verification does not close the issue:
B114 stays OPEN pending explicit designer confirmation.
QPDF syntax/stream checks also pass all three fresh outputs; this is not an
all-reader certification.

Retaining smaller equivalent existing JBIG2 is allowed. A size guard must
not ignore intentional resolution/threshold/appearance changes or substitute
another codec under an explicit selection. Fidelity changes stay explicit.

For the main conversion/compression comparison use whole eleven-page
**CCITT** `scan-naca-tm972.pdf`, not an already-JBIG2 scan. The published
overview and focused scan comparison now use fresh post-repair saves; all
34 retained scan cells are actual verified outputs (TODO §§239/241).
Historical files keep their original source/version, not repaired labels.
Keep the JFK source unchanged for regression.
Audit actual stored image `/Filter` values, not the PNG/TIFF export format
returned by extraction (B115).

## Size-only exploration protocol — TODO §240

1. Repair/pass B114 before promoting new optimization claims. Separate
   preparation defects from encoder and PDF-container costs.
2. Freeze originals, prepared binary samples/stencils, geometry, native
   content and reader tier. Use 300 DPI; do not mix DPI/threshold/palette,
   native/FFPR or lossless/lossy differences in one fidelity ranking.
3. Begin with `-d` off/on. Then investigate zero-error symbol/dictionary
   options and maintained encoders or audited library-only features. Do not
   invent CLI knobs, install dependencies or change shipped defaults under
   this documentation/research request.
4. Use full TM972/formulas scans, JFK as regression only, FFPR text, noisy/
   dithered BW photos and palette stencils. Add identical/alternating rows,
   sparse marks, random noise, blank/solid images, tiny masks, repeated and
   varied glyphs, and heterogeneous multi-page cases. Stress `O/0`, `I/l/1`,
   `S/5`, `B/8` and mathematical marks; OCR is not a pixel-exactness oracle.
5. Decode every image/mask exactly; check dimensions, polarity, diagnostics,
   native text/vectors/metadata and all-page renders. Test actual target
   readers, including Ghostscript/Poppler where relevant, and dictionary
   subsetting. Record failed/unsupported readers without blanket assurances.
6. Save every candidate through the shared production assembler/native/font/
   container saver. Publish **complete-PDF bytes**, percentages relative to
   named same-fidelity controls and bold tied minima. Invalid output receives
   a failure, never a size ranking. Keep lossy experiments separate.
7. Freeze encoder version/binary or source identity, full arguments and source/
   preparation/output hashes with actual files. Publish Markdown results and
   reproducible evidence, no wall-time rankings. Previews/export must continue
   to use that same completed PDF, not a separate visual approximation.

Promotion requires exactness, meaningful complete-size results and verified
reader support. This does not approve lossy defaults, new advanced GUI
controls or saved-recipe migrations. [TODO §240](TODO.md#240--open-designer-234-explore-jbig2-optimization-features)
remains OPEN: this guide documents the exploration, not its completion.
