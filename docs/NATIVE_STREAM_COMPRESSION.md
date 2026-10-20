# Native PDF stream compression — design and reader compatibility

## Rulings (verbatim)

Exact designer text from `DESIGNER_VERBATIM.md`. Text outside the fenced
quotes is not the designer's.

### Stream compression choices

**§205** (2026-10-15)

```text
what are the top text compression algorithms, and we should add an option for this also.  And make a benchmark document for that scope of compression also.  Are there support limitations on some of these algorithms?  Any reason to keep lesser compression algorithms?
```

**§213** (2026-10-15)

```text
so all pdf readers can decode flate encoded with zopfli?  Encoding is not a constrain, the objective of this project is to be an opinionated pdf compression suite with the best available algorithms for encoding, we drop superceded algorithms, the only concern that affects decisions would be pdf reader support, where for some usage, a more generally supported decoder would be proferred, in others, the user may expect readers to have the most modern and best pdf reader.
```

**§214** (2026-10-15)

```text
Compression time is not a concern, so we drop classic Flate from the options?  Keep in the comparison table for reference.
```

### Best

**§255** (2026-10-17)

```text
ok, this is fine the way it is, can we add an algorithm that chooses the best for each page?
```

```text
Not good, because we are not automatically selecting all options, just the pdf outer data (not images), right?
```

```text
Best (Zopli/Brotli) In the "PDF Streams:" dropdown please.
```

**§256** (2026-10-17)

```text
Why limite to non-image streams?  Don't they also compress PNGs?  Please explain.
```

```text
I don't think we will be supporting anything other than the three J*.  Why are you mentionning "CCITT fax images", did we not rule that all images get converted?
```

```text
yes, but those would be compressed with Best, but J* are excluded.
```

**§257** (2026-10-17)

```text
Change all the app filters to "Best" please
```

**§260** (2026-10-17)

```text
Also, can it happen that the images is native stream AND that best chooses zopfli?  Regardless, in the decision tree, when zopfli, we should automatically test PNG Prediction on and off when choosing best?  And also have an option for PNG prediction for when zopfli is chosen, have On/Off/Best.  For Best Zopfli/Brotli, it would also always try PNG Prediction Best.  or are there cases where it's guaranteed useless, eg, no PNGs = no need?
```

### Brotli declaration and help

**§251** (2026-10-17)

```text
Also, we should remove the "extension specification" for all the tests and filters by default, but add it as a compatibility option when Brotli is selected.  Only show that option for Brotli, which is different than our existing pattern to always show the option by grey it out when not applicable.
```

**§252** (2026-10-17)

```text
Mark that option as "(Compatibility)" for clarity.
```

**§253** (2026-10-17)

```text
Remove the text under Brotli, put that in a tooltip please, plan a standard tooltip as per modern GUI best practices
```

Measured complete-PDF sizes and the
[native/residual stream effects](COMPRESSION_BENCHMARKS.md#nativeresidual-streams--measured-effect-versus-flate-reference)
are in [COMPRESSION_BENCHMARKS.md](COMPRESSION_BENCHMARKS.md). Encoder policy:
[COMPRESSION.md](COMPRESSION.md#encoder-policy-213). Related:
[JBIG2.md](JBIG2.md), [ARCHITECTURE.md](ARCHITECTURE.md).

Optimized Flate is ONE reader format regardless of zlib or Zopfli encoding.
The three fixed choices remain alongside Best; aligning them is TODO §217,
and removing classic Flate as a product choice is TODO §218.

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

Every app filter uses Best (§257). Saved filters from before §257 are moved
to Best once, changing only the stream policy; later manual choices survive
restart. The headless legacy missing-policy fallback keeps its meaning.

Image compression and **PDF stream compression** are independent recipe inputs.
The fixed choices are labelled Flate, Flate (Zopfli, slow) and Brotli
(limited support); Flate is also the legacy headless fallback. Installed-reader
results are under
[Correctness and compatibility](#correctness-and-compatibility).
Changing either uses the one shared 300ms edit timer, dirty star and existing
saved/draft lifecycle. Keys, Save/Save As/load and actual-file readback/export
include this input. Legacy recipes with no policy mean Flate. The image codec
and encoded image bytes must not change when a fixed native policy changes.
Missing/failing selected encoders fail clearly, never silently fall back.

The Brotli developer-extension declaration is **opt-in and off by default**
(§251), including for filters with no explicit field.
The `brotli_declaration` recipe boolean applies to Brotli-capable policies
(explicit Brotli and Best). Its checkbox,
**Include Brotli extension declaration (Compatibility)** (§252), is completely hidden
for other stream compressors, rather than disabled. It participates in normal
dirty/debounce/save/revert/copy behavior, without an independent processing path.
This is metadata for readers that use the declaration; it cannot give a reader
a Brotli decoder. The limited-support warning lives in native tooltips and
accessibility help, not an inline label (§253, `TOOLTIPS.md`).

The PDF streams policy never changes the selected image codec. Best also
encodes packed images (§256); explicit Zopfli does so when its PNG prediction
setting is supplied (§260). Other legacy calls stay unchanged.

## Best (Zopfli/Brotli) — native and packed-image streams (§§255/256/260)

Best compares the two encoders for each native stream AND
eligible general-compressed image stream: packed BW, palette indices, raw or
Flate/Brotli sample images and masks. It excludes the specialized JPEG,
JPEG2000 and JBIG2 payloads, including lossless JPEG2000 and colored JBIG2
stencils. It does not automatically select image codecs or change DPI, palette, JPEG
quality or FFPR. Shared fonts/resources mean this is per stream, not an
independent rewrite of each page. Explicit policies remain available;
explicit Zopfli has Off/On/Best prediction, and Best always searches both
predictor states (§260). Empty streams stay plain; both encoders are
required for nonempty data, with no cheaper/failing-encoder substitution.

Encode unique stream/predictor bytes once per encoder, verify each representation and
choose a local assignment including dictionary overhead. Save and measure
that mixed assignment plus the homogeneous Zopfli and Brotli controls through
the same optimized writer. It also measures prediction OFF/ON whole-file controls and
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

All source images still undergo the selected production composition, one
final-DPI resize and transformation before encoding. Do not preserve a source
CCITT/PNG/JPEG merely because of its source codec. CCITT is not a product
output option. The untouched Original pane and explicitly unresampled
benchmark reference controls are separate from normal filter conversion.

## Algorithms and reader support (reviewed 2026-10-15)

| Choice | Stored PDF filter | Use / limitation |
|---|---|---|
| Flate / zlib | FlateDecode | Legacy headless fallback/reference, not the app default (§257); no reader-compatibility advantage over Zopfli. |
| Flate / Zopfli | FlateDecode | SAME decoder/format. Strongest measured Flate encoder here; target implementation for one optimized Flate choice. Required by Best. |
| Brotli | BrotliDecode | PDF Association's PDF 2.0 extension, published 2026-08-19. Needs supporting readers; not an ordinary PDF 1.7 feature or universal compatibility. |
| LZW | LZWDecode | Standard historical lossless filter; benchmark/control only unless results justify exposing it. |
| RunLength | RunLengthDecode | Standard lossless run-length coding; useful for repeated bytes, not a general promise of good text compression. Benchmark/control only. |
| Uncompressed | none | Diagnostic baseline, not a compression recommendation. |
| Best (Zopfli/Brotli) | FlateDecode and/or BrotliDecode | The app default (§257): measured per-stream choice for native and packed-image streams (§§255/256); may need a Brotli-capable reader. Excludes specialized J* payloads. |

The UI's Flate uses zlib level 9; Brotli uses level 11. Each selected policy
applies to every eligible nonempty native stream; it is not silently capped to
a cheaper subset. Encoding time is not a constraint (§213): explicit Zopfli
has no elapsed-time deadline, keeps polling for user cancellation, terminates
and reaps its own subprocess on cancellation or failure, and never substitutes
a weaker encoder.

General-purpose compressors such as Zstandard or LZMA/XZ cannot simply be
renamed FlateDecode in a PDF. Do not add unsupported proprietary filters or
infer PDF support from browser HTTP compression support. Brotli is different:
it has a published PDF extension (2026-08-19); older sources that call it
experimental or proposed predate that. Installed-reader tests still decide our
actual support.

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
image codecs (B79). Do not silently cap Zopfli to a subset of streams under a
global Zopfli label.

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

All policies leave zero-length native streams plain (no data to compress, no
filter). A regression covers empty
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

Best runs a joint storage search for eligible prepared image rows:
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

See `COMPRESSION.md` (final lossless pass) and the PNG decision tree in `COMPRESSION_BENCHMARKS.md`.

## Design traps and failed attempts

- **Empty Brotli streams.** MuPDF 1.28.2 returns zero bytes for empty input,
  and decoding that stream can loop forever. All policies leave zero-length
  streams plain.
- **Double-wrapped image payloads (B79).** Saved JPEG and JPEG2000 streams got
  an extra Flate wrapper and failed to decode. Pre-encoded payloads are written
  with `compress=False` under their own filter.
- **Trusting a reader's exit status.** Some Poppler unsupported-filter cases
  exit 0 with wrong content. Check diagnostics and actual text and pixels.
