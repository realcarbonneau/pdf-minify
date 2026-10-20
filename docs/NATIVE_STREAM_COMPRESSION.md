# Native PDF stream compression — design and reader compatibility

Measured final-file sizes, over six representative PDFs plus focused
scenarios (§223), are in
[COMPRESSION_BENCHMARKS.md](COMPRESSION_BENCHMARKS.md).

Measured native/residual stream effects are in
[COMPRESSION_BENCHMARKS.md](COMPRESSION_BENCHMARKS.md#nativeresidual-streams--measured-effect-versus-flate-reference).

Designer §§204/205, 2026-10-15 (America/New_York); TODO §§207/208.
Related: [COMPRESSION.md](COMPRESSION.md),
[JBIG2.md](JBIG2.md),
[ARCHITECTURE.md](ARCHITECTURE.md).

Encoder policy: [COMPRESSION.md](COMPRESSION.md#encoder-policy-213) (§213).
Optimized Flate is ONE reader format regardless of zlib or Zopfli encoding.
The three fixed choices remain alongside Best; aligning them is TODO §217.

## Scope and independent choices

PDF text is font/glyph references plus drawing operators, not just prose.
Compress native page/Form/pattern content, font programs, character maps and
other native non-image resource streams losslessly. Never quantize/rasterize
text/vectors or change fonts to win a benchmark. Explicit fixed policies
preserve bitmap payloads; §§255/256 extend the Best policy to eligible
packed-image streams, as specified below.
Preserve embedded files/metadata and leave PDF object/xref
stream generation to the shared container optimizer. Font subsetting, garbage
collection and object-stream packing remain shared for every policy.

§257 now makes Best the built-in APP default and requests a one-time migration
of ALL existing app filters, including explicit saved stream choices. Only
that policy field changes. UUIDs/order/labels, image settings and compatibility
flags survive; later deliberate manual choices survive restart. Original stays
untouched. The headless legacy missing-policy fallback keeps its meaning.

Image compression and **PDF stream compression** are independent recipe inputs.
Existing fixed choices are Flate (legacy headless fallback), Flate (Zopfli, slow) and Brotli
(limited reader support); installed-reader results are under
[Correctness and compatibility](#correctness-and-compatibility).
Changing either uses the one shared 300ms edit timer, dirty star and existing
saved/draft lifecycle. Keys, Save/Save As/load and actual-file readback/export
include this input. Legacy recipes with no policy mean Flate. The image codec
and encoded image bytes must not change when a fixed native policy changes.
Missing/failing selected encoders fail clearly, never silently fall back.

Designer §251 (2026-10-17) makes the Brotli developer-extension declaration
**opt-in, off by default**, including existing filters with no explicit field.
The `brotli_declaration` recipe boolean applies to Brotli-capable policies
(explicit Brotli and Best). Its checkbox,
**Include Brotli extension declaration (Compatibility)** (§252), is completely hidden
for other stream compressors, rather than disabled. It participates in normal
dirty/debounce/save/revert/copy behavior, without an independent processing path.
This is metadata for readers that use the declaration; it cannot give a reader
a Brotli decoder. Under §253, keep the limited-support warning in native
tooltips/accessibility help, not an inline label (`TOOLTIPS.md`).

The PDF streams policy never changes the selected image codec. Best also
encodes packed images (§256); explicit Zopfli does so when its PNG prediction
setting is supplied (§260). Other legacy calls stay unchanged.

## Best (Zopfli/Brotli) — native and packed-image streams (§§255/256/260)

The new selector value compares the two encoders for each native stream AND
eligible general-compressed image stream: packed BW, palette indices, raw or
Flate/Brotli sample images and masks. It excludes the specialized JPEG,
JPEG2000 and JBIG2 payloads, including lossless JPEG2000 and colored JBIG2
stencils. It does not automatically select image codecs or change DPI, palette, JPEG
quality or FFPR. Shared fonts/resources mean this is per stream, not an
independent rewrite of each page. Explicit policies remain available;
§260 adds Off/On/Best prediction to app Zopfli recipes and always searches
both predictor states under Best. Empty streams stay plain; both encoders are
required for nonempty data, with no cheaper/failing-encoder substitution.

Encode unique stream/predictor bytes once per encoder, verify each representation and
choose a local assignment including dictionary overhead. Save and measure
that mixed assignment plus the homogeneous Zopfli and Brotli controls through
the same optimized writer. §260 also measures OFF/ON whole-file controls and
per-image predictor choices. Preparation/font subsetting happens once, decoded
samples/palettes remain fixed, J* encoded payloads stay identical,
and PDF IDs use identical framing in every candidate.
Return the smallest actual complete file, preferring fewer Brotli streams
on exact ties, then fewer predicted streams; do not claim exhaustive global
optimization. Failed/canceled
work does not replace a completed output. Candidate files belong to the
existing encoding work directory and are cleaned up after selection.
Cache encoded alternatives on disk; retain only stream metadata/digests across
inputs, with exact decoded-byte comparisons before accepting every encoding.

Best can produce Brotli and therefore requires a supporting reader when it
does. Native tooltip/accessibility help explains that scope. The existing
default-OFF declaration option is visible for both Brotli-capable policies;
add its metadata only when the chosen candidate uses Brotli. It participates
in normal effective recipe identity and the shared 300ms edit lifecycle.

The completed [binary Zopfli-versus-Brotli experiment](COMPRESSION_BENCHMARKS.md#stream-compression--zopfli-versus-brotli-baseline)
remains a fixed-encoder comparison of 30 measured FFPR pairs, not a claim
that Best has already been benchmarked across that corpus. No old size or
producing identity is overwritten by this feature.

All source images still undergo the selected production composition, one
final-DPI resize and transformation before encoding. Do not preserve a source
CCITT/PNG/JPEG merely because of its source codec. CCITT is not a product
output option. The untouched Original pane and explicitly unresampled
benchmark reference controls are separate from normal filter conversion.

## Algorithms and reader support (reviewed 2026-10-15)

| Choice | Stored PDF filter | Use / limitation |
|---|---|---|
| Flate / zlib | FlateDecode | Legacy headless fallback/reference, not the app default (§257); no reader-compatibility advantage over Zopfli. Separate speed-based product choice is superseded by §213. |
| Flate / Zopfli | FlateDecode | SAME decoder/format. Strongest measured Flate encoder here; target implementation for one optimized Flate choice. Tool is optional only in the current build. |
| Brotli | BrotliDecode | PDF Association's PDF 2.0 extension, published 2026-08-19. Needs supporting readers; not an ordinary PDF 1.7 feature or universal compatibility. |
| LZW | LZWDecode | Standard historical lossless filter; benchmark/control only unless results justify exposing it. |
| RunLength | RunLengthDecode | Standard lossless run-length coding; useful for repeated bytes, not a general promise of good text compression. Benchmark/control only. |
| Uncompressed | none | Diagnostic baseline, not a compression recommendation. |
| Best (Zopfli/Brotli) | FlateDecode and/or BrotliDecode | New native/packed-image measured-choice policy (§§255/256); may need a Brotli-capable reader. Excludes specialized J* payloads. |

The UI's Flate uses zlib level 9; Brotli uses level 11. The benchmark also
measures zlib level 1 and Brotli level 9 as effort comparisons, not extra
product codecs. Each selected policy applies to every eligible nonempty
native stream; it is not silently capped to a cheaper subset.
Under §213's unconstrained encoding-time rule, explicit Zopfli encoding has
no arbitrary elapsed-time deadline. Continue polling for user cancellation
and terminate/reap its owned subprocess on cancellation or failure; never
substitute a weaker encoder. The size-only 300-DPI study uses this same
adapter, not a separate timeout/fallback implementation.

General-purpose compressors such as Zstandard or LZMA/XZ cannot simply be
renamed FlateDecode in a PDF. Do not add unsupported proprietary filters or
infer PDF support from browser HTTP compression support. Brotli is different:
it now has a published PDF extension. Its 2026 status must not be inferred from
the older January 2026 experimental iText notes or old MuPDF documentation's
"proposed" warning. Installed-reader tests still decide our actual support.

Primary sources:

- [ISO 32000-1 Table 6 and §7.4](https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf).
- [Brotli extension publication, 2026-08-19](https://pdfa.org/no-excuses-brotli-compression-advances-pdf/).
- [PDF Association Brotli specification, EXTN-BROTLI-1 v1.3](https://pdfa.org/download-area/publications/pdf-extension-brotli.pdf)
  and [registered extension details](https://pdfa.org/extensions/#brotli-compression).
- [MuPDF write options](https://mupdf.readthedocs.io/en/latest/reference/common/pdf-write-options.html).
- [Zopfli upstream](https://github.com/google/zopfli) and
  [QPDF compression/decoder behavior](https://qpdf.readthedocs.io/en/stable/cli.html).

## Implementation rules

One shared core adapter owns native stream enumeration, lossless encoding and
exact decoded-byte verification. Reuse it in the real saver and benchmark;
production must not import tooling. Recompress eligible already-Flate streams
as well as plain streams so that selecting an encoder has real effect. Skip
image XObjects, embedded-file/metadata streams, object/xref streams. Preserve
stream dictionaries except Filter/DecodeParms/Length. Never double-wrap encoded
image codecs (B79). Do not silently cap Zopfli to a tiny subset under a global
Zopfli label; record measured full-workload cost and optional dependency.

Brotli uses the bundled MuPDF encoder/decoder, if available; no extra Python
package is assumed. Standard standalone streams, no external dictionaries or
shared framing. Under §251, add catalog PDF 2.0 version and the PDFa
developer-extension declaration (level 1/revision 2026) only when explicitly
requested. Default saves remove an inherited Brotli declaration but preserve
unrelated developer extensions and legitimate source version information.
Handle direct/indirect dictionaries and extension arrays structurally, not
with string/regex deletion. Repeated opt-in saves must not duplicate entries.
Keep container/xref streams conventionally compressed so readers can discover
the extension. Provide explicit limited-support tooltip help (§253). This
does not confer PDF/A or all-viewer certification.

Validation exposed MuPDF 1.28.2 returning zero encoded bytes for empty Brotli
input; decoding that purported stream can loop indefinitely. All policies
leave zero-length native streams plain (no data to compress, no filter),
avoiding invalid streams and useless overhead. A regression covers empty
content plus actual image-bearing production pages, whose assembly leaves
empty intermediate streams until final garbage collection.

## Correctness and compatibility

A rewritten native stream must decode byte-for-byte, keep every native word
and its geometry, and leave MuPDF page pixels and image payload/filter/
dimension signatures unchanged. Installed readers on the certified platform:

| Installed reader/check | Flate / Zopfli | LZW / RunLength | Brotli-9/11 |
|---|---|---|---|
| App's MuPDF 1.28.2 | Exact native bytes and all-page pixels | Exact | Exact, with valid nonempty streams |
| Poppler 25.03.0 | Exact extracted text and ALL page pixels | Exact | FAIL: unknown BrotliDecode; missing/wrong text and pixels |
| QPDF 12.2.0 | Syntax check 0 and largest native stream decodes exactly | Same | FAIL: check exit 2; largest stream does not decode correctly |

QPDF checks all syntax and independently decodes each candidate's largest
native stream; do not mislabel that as independent every-stream readback.
Some Poppler unsupported-filter cases return zero despite bad content; the
benchmark checks diagnostics and actual text/pixel equality, not exit status
alone. None is a cross-platform/all-viewer certificate.

## Joint PNG-predictor selection (§260)

Best now requires a joint storage search for eligible prepared image rows:
Zopfli OFF/ON and Brotli OFF/ON. Native text/vector/font resources have no
image-row predictor. JPEG/JPEG2000/JBIG2 payloads remain protected, even
when their accompanying native streams choose Zopfli. Absence of input PNG
files is not a skip condition: prediction operates on prepared pixel rows.
The adaptive row operation follows the [PNG filter definitions](https://www.w3.org/TR/png-3/#9Filters);
the PDF stores the filtered samples and matching decoding parameters, not a
PNG container or source filename.

Source PDFs can also embed inline bitmaps inside page content streams. The
normal composition pass replaces those bitmaps before this storage stage;
it does not apply PNG prediction blindly to a native painting program.
Here, "image stream" means the prepared image samples, while "native stream"
means the retained non-image content/resources. Both can select Zopfli.

Explicit Zopfli exposes Off/On/Best for eligible packed images. The app's
Best policy always uses predictor Best, regardless of the retained inactive
explicit setting. Choices are effective recipe state and share one normal
edit/artifact transaction. Legacy headless explicit calls with no predictor
field retain native-only behavior. Core trial saves account for predictor
dictionaries, filter names and complete container overhead; they never rerun
the visual processing pipeline. Unsupported general-image layouts are kept
unchanged in automatic mode, not guessed; explicit On reports an error.

The §258 integrated measurements predate this joint search and explicitly
preserve their predictor state. Their actual byte evidence remains valid for
that versioned experiment, not a measurement of the new §260 policy.
See `COMPRESSION.md` (final lossless pass) and the PNG decision tree in `COMPRESSION_BENCHMARKS.md`.
