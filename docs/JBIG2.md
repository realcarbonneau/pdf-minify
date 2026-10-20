# JBIG2 — BW and Color

JBIG2 encodes one-bit images. Two Image compression choices use it: **JBIG2
BW** and **JBIG2 Color** (§203). Text and vector artwork stay native unless
FFPR is on. Optimization research is TODO §240.

Measured sizes: [COMPRESSION_BENCHMARKS.md](COMPRESSION_BENCHMARKS.md).
Preparation and native artwork: [COMPRESSION.md](COMPRESSION.md).
Encoder and reader policy: [COMPRESSION.md](COMPRESSION.md#encoder-policy-213).
Encoder capabilities below were reviewed on 2026-10-16; the current encoder
path is implemented, and the optimizations listed are research, not choices.

## Rulings (verbatim)

Exact designer text from `DESIGNER_VERBATIM.md`. Text outside the fenced
quotes is not the designer's.

**§192** (2026-10-14)

```text
Ok, this is good.  Next issue, above the right pane, put a text "parameters" or Configuration, or something like this.  This will make all three blocks follow the same pattern.  After, the next issue is to design an low color count pallete compression model with multiple JBIG2 with each a color, so 4 colors +while would be 4 JBIG2 overlaid, do you follow this plan?  Can you do this?
```

**§203** (2026-10-15)

```text
I think we need to add an option that is the algorithm, JBIG2 BW, JBIG2 Color, Flate BW, Flate Color JPEG2000, JPEG.  Because we have no way of choosing between the options at the moment, filters seem to be locked into their algo.  Also, why do we have both JPEG and JPEG2000, and Flate BW and Flate Color?  For backward compatibility?  Aso, the terms strategy should be qualified, is that Threshold automatic strategy?
```

**§233** (2026-10-16)

```text
that is a good test case for the full flow, the flow should never make a JBIG2 worse, document this as an issue and a test case to use to fix and check for regressions.  Also, this is NOT a good test case for this table, find another BW pdf that is NOT already JBIG2, or else the results are meaningless.
```

**§234** (2026-10-16)

```text
Add a JBIG2 dev doc, add documentation relevant to the algo and add a TODO that we need to explore other JBIG2 optimization features and detail them
```

## How JBIG2 is used

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
JBIG2 failure is an error, not silent Flate fallback.

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

## JBIG2 Color: one stencil per palette colour

The designer's example is four non-white colors PLUS white, meaning FIVE
total palette entries and FOUR independently JBIG2-compressed 1-bit images.
White is an opaque base; each other color paints only its own pixels. These
are ordinary PDF image stencils, not optional-content layers or four opaque
black/white rectangles (which would erase each other).

```
original image artwork + real flat page backdrop
  → compose in full RGB (native text/vector artwork excluded)
  → ONE resize to the final target DPI
  → ONE existing palette fit + exact nearest-color assignment
  → opaque white base + one disjoint binary mask per used non-white color
  → lossless JBIG2 per mask + that mask's RGB paint color
  → native original text/vector overlay
  → optimized real PDF → readback, true bytes, preview/minis/export
```

The canvas comes from `image_layers.compose_color_page` and the palette from
`_quantize_palette`, the same composition and palette fit as Indexed color;
the stencils branch only after final-DPI RGB preparation and share the SAME
palette/index map. Palette reduction is lossy relative to the RGB source;
mask compression/reconstruction is pixel-exact relative to that quantized
map. No dithering, post-quantization resizing or per-color re-quantization.
Native text/vector colors are not counted as bitmap palette colors or
thresholded to fit the palette. Native-only pages get no bitmap; page boxes,
rotation, links and annotations pass through the shared compositor.

### PDF objects, polarity and placement

Each stencil image uses `/ImageMask true`, `/BitsPerComponent 1`,
`/Interpolate false`, `/Filter /JBIG2Decode`, and NO `/ColorSpace` or `/SMask`.
With `/Decode [0 1]`, zero bits paint and one bits leave previous content
unchanged. The existing encoder's black (0) samples therefore mean "this
palette color", and white (255) samples mean "transparent here". Set the
nonstroking palette color before invoking each image inside saved/restored
graphics state. Every mask has exactly the same pixel dimensions and page
transform; no offsets, resampling or antialiased fringes between colors.
Allocate independent image objects; never mutate a deduplicated placeholder.
Pre-encoded streams use `update_stream(..., compress=False)` before declaring
their filter (B79/B90 lessons).

Paint colors use an Indexed nonstroking color-space resource holding the
ORIGINAL palette bytes, selected by integer entry via `cs/scn`. The image
itself still has NO ColorSpace entry. This preserves exact byte colors without
numerical fudges, a tolerance, re-quantization or a corrective display filter.

The stencil canvas is expressed in the target page's physical units from the
start, with the same image transform as Indexed color, so its outer Form
placement is identity.

The white base must be painted explicitly across the bitmap canvas. Merely
omitting a white mask would expose an original colored backdrop below it.
Do not invent a white palette slot when the chosen palette has none: in that
case all used colors get masks and their union covers the entire base.
Skip unused colors and an actual pure-white entry; do not skip near-white.
Masks are one-hot assignments: no holes except real white pixels, and no
pixel belongs to two colors. Sparse colors may compress well, but each extra
mask has stream/object/paint overhead and a full-page binary domain.

Sources: [ISO 32000-1:2008, §8.9.6.2 (stencil masking), §7.4.7 (JBIG2)](https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf),
[PyMuPDF low-level object/stream updates](https://pymupdf.readthedocs.io/en/latest/document.html#Document.update_stream),
[jbig2enc implementation](https://github.com/agl/jbig2enc).
Masks use the existing `jbig2 -p` lossless generic-region path, with no lossy
symbol substitution or cross-document dictionaries. Each stream is
standalone and test-decoded; it reaches the encoder as a 1-bit PNG, the same
transport as BW. Explicit JBIG2 never falls back silently to another codec.

### Correctness

1. Every lossless JBIG2 stream reconstructs its input binary mask exactly,
   and decoding must finish without decoder diagnostics.
2. Rendering each composite canvas at its stored dimensions matches the
   identical-palette Indexed RGB samples pixel-for-pixel, including white,
   near-white, edge columns and every palette entry.
3. Actual final-file full-page rendering agrees with the Indexed version;
   native words/geometry, vector artwork, rotation and links remain intact.
4. Poppler `pdfimages` independently decodes every stencil, checks its binary
   samples, disjoint coverage and reconstructed palette RGB exactly. Poppler
   exports stencil coverage as white=paint, black=transparent, the inverse of
   the source grayscale mask used by the encoder; compare that coverage
   convention, not ordinary-image gray polarity.
5. Tests pin all-white, no-white, white-plus-four, odd widths/padding, multiple
   pages, corrupted encoder data, cancellation and unavailable encoders.

### Reader compatibility

Poppler decodes every stencil's coverage exactly, but its full-page renders
are not pixel-identical to its renders of the same Indexed page: its image
and stencil sampling paths differ, so the Indexed paint shows intermediate
colors while stencil colors stay discrete. This is a display difference, not
a decode failure. Do not claim all-viewer exact appearance.

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

## Same-resolution non-regression (§233)

`examples/scan-jfk-poor-copies.pdf` (eight pages) already uses JBIG2. At
unchanged 300 DPI, with lossless JBIG2 and no intended appearance change, a
complete save must keep the original bitmap samples and page geometry and
must not grow relative to the input or an equivalent preserve-images control,
both with native preservation and with FFPR. Encoder equality against an
already altered prepared image does not prove this. The compositor keeps the
actual fractional source density instead of rounding it to a whole DPI
(§235); `tests/test_jbig2_non_regression.py` holds the contract.

Keeping a smaller equivalent existing JBIG2 is allowed. A size guard must not
ignore an intentional resolution, threshold or appearance change, or
substitute another codec under an explicit selection.

BW comparisons use the CCITT scan `scan-naca-tm972.pdf`, never an
already-JBIG2 scan, and check the stored image `/Filter` values rather than
the format extraction returns (B115).

## Size-only exploration protocol — TODO §240

1. Keep the same-resolution non-regression passing before promoting new
   optimization claims. Separate preparation defects from encoder and
   PDF-container costs.
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
controls or saved-recipe migrations. See
[TODO §240](TODO.md#240--open-designer-234-explore-jbig2-optimization-features).

## Design traps and failed attempts

- **Decimal `rg` paint colors.** They caused one-channel rounding errors (green
  32 decoded as 31) despite pixel-exact masks. Use the Indexed color space.
- **PBM transport to `jbig2` (B99).** The installed encoder/Leptonica
  combination fails on a valid P4 file whose first packed byte is whitespace
  (exit 3, `pixReadStreamPnm: read error`): the dimension `fscanf` consumes
  it ([Leptonica's PNM reader](https://github.com/DanBloomberg/leptonica/blob/master/src/pnmio.c)).
  1-bit PNG transport avoids the ambiguity.
- **Pixel checks without decoder diagnostics (B100).** A malformed stream can
  make MuPDF paint a black error placeholder that matches an all-black
  expected mask. Validation rejects new decoder diagnostics as well as wrong
  pixels.
- **A pixel-sized intermediate PDF.** Placing it with an inverse page-scale
  transform caused a dense-noise mismatch despite exact masks. Use page units
  from the start.
