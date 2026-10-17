# Reasonable compression combinations and control design

This is the capability/UI design table, not a measured file-size matrix.
Use [INTEGRATED_COMPRESSION.md](INTEGRATED_COMPRESSION.md) for the primary
comparison of actual complete saved PDFs: realistic combinations as rows
over six representative PDF classes, followed by focused scenarios (§§223/231).

Design review requested by designer §§210–212, followed by the opinionated
encoding ruling §213, 2026-10-15 (America/New_York). The best-encoding/reader-
support policy is now a designer ruling. §§224/225 separately authorize color
FFPR and uniform 300-DPI defaults. §§255/256 authorize Best for native/packed
streams; fixed policies retain their prior semantics. Current code versus
remaining proposals is explicitly identified.

## Combination table

Optimized Flate / Brotli below means two alternative reader formats, not
nested compression. Zopfli is an INTERNAL Flate encoder, not a third reader
format or speed-based product option (§213). FFPR means force full-page
rasterization. This is the target policy; current integration gaps are noted.

| Page handling | Image encoding | Reasonable general-compression choice | What the general compressor affects | Availability today |
|---|---|---|---|---|
| Keep native text/vectors | Packed 1-bit BW | Best (Zopfli/Brotli), shared by bitmap and native streams | Packed BW pixels plus native drawing/font streams | Best implemented; fixed-policy recipes retain the existing Flate image encoding. |
| Keep native text/vectors | Packed indexed color | Best (Zopfli/Brotli), shared by bitmap and native streams | Packed palette indices plus native drawing/font streams | Best implemented; fixed-policy recipes retain the existing Flate image encoding. |
| Keep native text/vectors | JBIG2 BW | Optimized Flate / Brotli for native streams only | Native drawing/font streams; JBIG2 already compresses the BW pixels | Implemented with independent native selection; redundant encoder choice still needs removal. |
| Keep native text/vectors | JBIG2 Color | Optimized Flate / Brotli for native streams only | Native drawing/font streams and stencil painting; each colored mask uses JBIG2 | Implemented with independent native selection; redundant encoder choice still needs removal. |
| Keep native text/vectors | JPEG | Optimized Flate / Brotli for native streams only | Native drawing/font streams; JPEG compresses the composed color image | Implemented; JPEG encoding is lossy. |
| Keep native text/vectors | JPEG2000 | Optimized Flate / Brotli for native streams only | Native drawing/font streams; JPEG2000 compresses the composed color image | Implemented; lossy or lossless encoding. |
| FFPR: flatten whole page | Packed 1-bit BW | Best (Zopfli/Brotli); control remains active | The full-page BW raster, plus its small painting stream | Best implemented; fixed-policy recipes retain the existing Flate image encoding. |
| FFPR: flatten whole page | Packed indexed color | Best (Zopfli/Brotli); control remains active | The full-page palette raster, plus its small painting stream | Best implemented; fixed-policy recipes retain the existing Flate image encoding. |
| FFPR: flatten whole page | JBIG2 BW | Best for residual streams; control remains active | Only tiny placement/drawing instructions; no original native text/fonts/vectors remain | Best implemented alongside the unchanged explicit native policies. |
| FFPR: flatten whole page | JBIG2 Color | Best for residual streams; control remains active | Colored-stencil painting instructions, not the JBIG2 masks | Best implemented; colored masks stay JBIG2. |
| FFPR: flatten whole page | JPEG | Best for residual streams; control remains active | Only placement/drawing instructions; JPEG compresses the full page | Best implemented; text is already part of the selected lossy raster. |
| FFPR: flatten whole page | JPEG2000 | Best for residual streams; control remains active | Only placement/drawing instructions; JPEG2000 compresses the full page | Best implemented; lossless does not restore native text/vector precision. |

"Keep native" follows the established composed-image canvas + native overlay
policy, not exact original image/native interleaving. FFPR deliberately removes
native text selectability and vector/font geometry. Lossless encoding only
preserves the prepared raster: DPI changes, thresholding and palette reduction
can already have discarded information.

§§255/256 approve adding **Best (Zopfli/Brotli)** to the PDF streams selector,
covering native streams AND packed-image streams, while excluding specialized
JPEG/JPEG2000/JBIG2 payloads. All source imagery still passes through the
selected composition/resize/transform pipeline; there is no source-CCITT
preservation exception. Keep the six image choices and existing explicit
native-only policies/recipes. Best changes lossless storage only, not samples,
palettes/predictors, DPI, opacity, FFPR or image quality. This approval does
not implement the earlier proposed inactive FFPR general-compressor control.
See `NATIVE_STREAM_COMPRESSION.md` and TODO §253 for implementation status.

The implementation retains six Image compression choices plus an independent
PDF streams choice (§§203–205). The three FIXED native policies never change
image bytes; Best now covers packed images too. Indexed's legacy explicit-policy
automatic small-stream Zopfli path still stores FlateDecode; it is not a
user-selectable, full-workload Zopfli image policy. Best bypasses that preparation
shortcut, encoding both complete workloads at final selection. Its two packed
image labels are now **Packed BW** / **Indexed color**, not promises of Flate;
internal mode IDs and existing explicit recipes remain unchanged.
FFPR is enabled for all six image codecs (§224), including on native-only
pages. All built-in raster defaults are 300 DPI (§225). §226 migrates all
saved/custom raster recipes once to 300 DPI; later deliberate DPI edits remain
intact. The main/focused comparison uses 300 DPI throughout,
with preserve-images controls explicitly unresampled.

## Decoder support, not encoder cost (§213)

| User-visible format | Decoder requirement | Encoder policy |
|---|---|---|
| Flate (optimized) | Existing FlateDecode support; Zopfli adds NO new requirement | Best validated same-format implementation; currently Zopfli wins the native Flate benchmarks. No separate weaker speed choice. |
| Brotli | A reader verified to support the PDF Brotli extension | Best validated Brotli encoding, retaining the support warning. Do not infer support from "modern" or PDF 2.0 alone. |

Zopfli produces standard zlib/DEFLATE bytes. Any conforming reader that can
decode FlateDecode can decode correctly embedded Zopfli zlib output; it does
not need to know which encoder produced it. This is not a certification of
every reader implementation or the rest of a PDF's features. Use zlib-framed
output, not Zopfli's alternative gzip framing under a FlateDecode label.

The designer's §213 removes encoder cost/speed from product selection.
Retire superseded encoding choices; dependency convenience is not grounds
to ship inferior compression. Compare actual full-file bytes at the chosen
representation/fidelity and reader constraints. If a same-format candidate
really produces smaller valid output on some input, it is not dominated on
that input; selecting it internally does not create another reader format.
Do not assume either Zopfli or Brotli always wins every possible input.

Broad-support versus modern-reader targeting describes allowed DECODERS,
not a fast versus slow encoder. Allowing Brotli does not require it on every
stream when extension/filter overhead loses size. A future automatic
cross-format profile needs explicit design; existing exact-codec labels may
not silently substitute codecs. Benchmarks retain superseded controls for
evidence, not normal UI choices. Current runtime alignment is TODO §217.

The preceding §212 review suggested retaining Flate BW partly to avoid an
external JBIG2 encoder. That justification is WITHDRAWN under §213. Keep an
image alternative only for demonstrated size outcomes or genuine intended-
reader support, not encoder availability/speed. The measured palette winners
remain mixed; the present BW corpus alone does not establish universal
dominance across all readers/inputs. Proposed preserve-images and full-color
lossless additions from that review remain suggestions, not approved features.

## Valid combinations versus useful UI choices

- Mixed general codecs on packed pixels versus native streams are excluded
  from the published algorithm analysis (§223): use one shared optimized
  Flate or Brotli policy for both. Such mixed-stream PDFs are technically
  valid, but format validity is not the agreed test-menu scope. Historical
  cross-product outputs remain raw diagnostic evidence, not recommendations.
  Do not silently reinterpret an existing saved mixed recipe; selector and
  migration work remains separate from this documentation/benchmark ruling.
- Brotli-native + JBIG2, JPEG or JPEG2000 is meaningful when native content is
  retained. Each specialized image codec has its own job; general compression
  does not wrap its already encoded image payload. The same holds for native
   optimized Flate with those codecs.
- BW JBIG2 is a 1-bit codec. Colored JBIG2 means separate disjoint binary
  stencils painted in their palette colors, not a single multichannel JBIG2
  stream. JPEG is not a true 1-bit BW output option. Lossy JBIG2 remains
  excluded from the proposed menu; no new glyph-substitution mode is implied.
- FFPR is a page-construction policy, not a compressor. "Brotli + JBIG2" and
  "FFPR + JPEG2000" name different axes; a flat menu makes that easy to miss.
- Small object/xref container streams remain automatically optimized,
  conventionally using Flate. A Brotli document can legitimately contain
  those Flate streams. The proposed general control is not a command to
  replace every PDF filter, metadata stream or attachment.
- Any effective Brotli use requires a reader supporting the PDF Brotli
  extension. The extension declaration is optional compatibility metadata,
  **OFF by default** under §§251/252; it cannot supply decoder support.
  Choosing JPEG/JBIG2 for the images does not remove the reader requirement.
  Installed Poppler/QPDF failures remain documented in
  [NATIVE_STREAM_COMPRESSION.md](NATIVE_STREAM_COMPRESSION.md).

## What remains after FFPR + a specialized image codec?

Historical read-only inventory of the original size-study PDFs, 2026-10-15,
before §224's shared full-color FFPR preparation. These are retained artifacts,
not the current 300-DPI matrix's output sizes:

| Existing FFPR + JBIG2 output | Pages | Complete PDF B | JBIG2 image B | Unique native streams | Native decoded B | Native Flate B |
|---|---:|---:|---:|---:|---:|---:|
| images.pdf | 1 | 4,095 | 3,218 | 1 | 35 | 37 |
| GAN paper | 9 | 321,295 | 317,682 | 1 | 35 | 37 |

These files live under
`.tmp/image-stream-compression/size-20261015/images.bw-ffpr.300dpi.otsu-180/jbig2.pdf`
and the corresponding `paper-arxiv-1406.2661.bw-ffpr.300dpi.otsu-180/jbig2.pdf`.
The shared unique native stream paints an image at page size:

```text
q
612 0 0 792 0 0 cm
/fzImg0 Do
Q
```

There are 35 decoded bytes including whitespace; the nine-page file reuses
that stream. The remainder of the complete file includes image dictionaries,
page/resource objects, metadata and container structures. It is not all
eligible native-stream data. This inventory introduces no timing comparison
or new encode run.

There is essentially nothing for a user-selected native compressor to win
in these two examples. An opt-in Brotli declaration can exceed a small stream
saving; the current default-OFF experiment excludes that metadata cost.
This supports automatically handling the residual streams in FFPR + a
specialized codec, rather than offering nearly identical general-compression choices.
It does NOT mean all FFPR files have exactly 35 bytes of painting commands:
colored stencils need more operators/resources. The current integrated matrix
measures color FFPR's actual complete-file overhead too. General compression still
matters greatly for FFPR + packed pixels because it compresses the raster
itself, not just those instructions.

## One combined dropdown or separate controls?

| Design | Benefit | Cost / risk | Recommendation |
|---|---|---|---|
| One dropdown listing every combination | Each entry names a complete choice; invalid tuples can be omitted | Repeats codecs for each native compressor and FFPR state; changing one axis can reset another; long labels obscure quality/flattening effects | Do not use as the primary editor. |
| Separate page, image and general-compression controls | Makes each choice's purpose clear; preserves independent preferences; shows which settings apply | Needs one shared capability resolver, explicit scope text and correct disabled states | Recommended, pending designer approval. |
| Existing named filter presets + separate editable controls | One-click combinations without a second competing preset catalog | Preset name alone must not hide the effective recipe | Keep this existing pattern; do not lock codecs to presets. |

Implemented control structure after §§255/256:

1. **Force full-page rasterization**: retain the existing per-filter checkbox;
   this controls whether text/vectors survive. §224 authorizes and implements
   it for every existing image codec, not just BW.
2. **Image encoding**: JBIG2 BW, JBIG2 Color, Packed BW, Indexed color,
   JPEG2000, JPEG. Existing mode IDs persist; only representation labels avoid
   promising Flate when Best chooses Brotli.
3. **PDF streams**: existing Flate, Zopfli and Brotli choices plus
   **Best (Zopfli/Brotli)**. Fixed choices retain native-only semantics; Best
   also encodes packed image samples. J* payloads never enter this competition.
   Contextual native help/accessibility states the scope and reader limitation;
   no inline working/help label is added (§253).

The earlier disabled-Automatic FFPR proposal is superseded by the explicitly
selected Best policy: keep the PDF streams control active, including FFPR +
specialized images, and preserve the chosen recipe. No implicit mode change,
default migration or remembered hidden alternative is introduced. Best tries
only its two named encoders; empty streams stay plain under the safety rule.
For other inapplicable controls, retain visible/disabled effective values under
§100. The default-OFF Compatibility checkbox is the explicit visibility
exception: show it only for Brotli-capable policies (Brotli and Best).

Threshold method applies only to BW; manual T only to Simple; palette count
only to the two palette modes; JPEG quality only to JPEG; JPEG2000 rate only
to lossy JPEG2000. The lossless checkbox remains visible in its correct fixed
state when not editable (§100). Keep one DPI and the one shared 300ms edit
timer. Do not enable/disable controls from whichever codec happened to win
the last benchmark or make their applicability jump from page to page.

A read-only summary gives the convenient combined name without a huge menu,
for example: "Images: JBIG2 BW · Native streams: Brotli · Text/vectors kept"
or "FFPR · JPEG2000 lossless · PDF streams: Best (Zopfli/Brotli)". The recipe
readout reflects the selected policy, not a claim that every stream uses the
same decoder. Best's opt-in declaration readout is conditional on actual use.

## Compatibility, evidence and implementation boundary

The recommendation above is design judgment, not a claim that Qt or the PDF
standard mandates this exact arrangement. Qt supports normal enabled/disabled
widgets; use native states rather than simulated grey paint. §225 changes
built-in raster defaults to 300 DPI; §226 also migrates all saved/custom raster
recipes once. Neither changes encoding defaults. Later deliberate DPI edits
remain effective. Missing explicitly selected encoders must still fail clearly;
never silently replace JPEG/JBIG2/Brotli with a different image codec.

Any approved integration must resolve capabilities/effective parameters ONCE
in core, reused by widgets, keys, saving and summaries. Retain the previous
inactive preferences but omit ineffective inputs from processing identity.
Do not silently migrate a saved native-Brotli + image-Flate recipe to Brotli
images; preserve/reveal its explicit pairing until a deliberate edit, or obtain
a separate migration decision. Real-PDF previews, exact whole-file amounts,
Save/Save As/Discard/Cancel and single-filter debouncing remain canon.

Evidence and primary sources:

- [IMAGE_STREAM_COMPRESSION.md](IMAGE_STREAM_COMPRESSION.md): 22 equal-pixel,
  size-only cases. BW JBIG2 wins all ten BW cases; colored JBIG2 wins three
  of twelve palette cases, plain Brotli nine. These are corpus results, not
  universal guarantees or permission for automatic cross-codec substitution.
- [NATIVE_STREAM_COMPRESSION.md](NATIVE_STREAM_COMPRESSION.md): independent
  native-only study, actual reader limitations and current selector behavior.
- [COMPRESSION.md](COMPRESSION.md): current flows, explicit codec semantics
  and real-file lifecycle. [DESIGNER_VERBATIM.md](DESIGNER_VERBATIM.md)
  §§100/203–205/210–213 preserve the designer's exact words.
- [PDF Association EXTN-BROTLI-1 v1.3, §§5.1/5.2](https://pdfa.org/download-area/publications/pdf-extension-brotli.pdf):
  per-stream Brotli use, including image XObjects and optional prediction;
  inline images are excluded. No blanket prohibition on mixing stream codecs.
- [Zopfli upstream](https://github.com/google/zopfli): encoder of the existing
  deflate/zlib format, not a new PDF decoder requirement.
- [RFC 1951 §1.4](https://www.rfc-editor.org/rfc/rfc1951.html#section-1.4)
  and [RFC 1950](https://www.rfc-editor.org/rfc/rfc1950.html): compliant
  DEFLATE decoding and correct zlib framing; encoder identity is not a
  separate reader capability.
- [Qt QWidget enabled property](https://doc.qt.io/qt-6/qwidget.html#enabled-prop):
  native disabled input/state behavior, not a prescription for this layout.
