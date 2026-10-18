# Native PDF stream compression — design, benchmarks and compatibility

Supporting component study: image bytes are fixed in this document.
The primary final-file comparison uses realistic combination rows over six
representative PDFs, followed by focused scenarios (§223):
[INTEGRATED_COMPRESSION.md](INTEGRATED_COMPRESSION.md).

The current NATIVE-01 controlled experiment separates native/residual encoder
effects from image compression, including the five specialized-codec FFPR
cases. Its protocol is in [COMPRESSION_EXPERIMENTS.md](COMPRESSION_EXPERIMENTS.md#native-01--nativeresidual-stream-recompression);
measured reference/candidate complete-file tables belong in the integrated
report, not another duplicate analysis here. The earlier component results
below retain their original scope and provenance.

Designer §§204/205, 2026-10-15 (America/New_York); TODO §§207/208.
Related: [COMPRESSION.md](COMPRESSION.md),
[COMPRESSION_COMBINATIONS.md](COMPRESSION_COMBINATIONS.md),
[LAYERED_COLOR_JBIG2.md](LAYERED_COLOR_JBIG2.md),
[ARCHITECTURE.md](ARCHITECTURE.md), [TEST_PLAN.md](TEST_PLAN.md).

Latest product ruling §213 removes encoder speed/cost as a reason to keep
weaker choices. Optimized Flate is ONE reader format regardless of zlib or
Zopfli encoding. The three existing fixed choices remain alongside the new
Best policy; further old encoder/default alignment is pending TODO §217.
Historical timings/bytes are evidence, not a continuing
instruction to offer fast encoding. See the product-decision section below.

## Scope and independent choices

PDF text is font/glyph references plus drawing operators, not just prose.
Compress native page/Form/pattern content, font programs, character maps and
other native non-image resource streams losslessly. Never quantize/rasterize
text/vectors or change fonts to win a benchmark. Explicit fixed policies and
the component measurements below preserve bitmap payloads; §§255/256 extend
the new Best policy to eligible packed-image streams, as specified below.
Preserve embedded files/metadata and leave PDF object/xref
stream generation to the shared container optimizer. Font subsetting, garbage
collection and object-stream packing remain shared for every policy.

§257 now makes Best the built-in APP default and requests a one-time migration
of ALL existing app filters, including explicit saved stream choices. Only
that policy field changes. UUIDs/order/labels, image settings and compatibility
flags survive; later deliberate manual choices survive restart. Original stays
untouched. The fixed-policy component experiments below and the headless
legacy missing-policy fallback retain their explicit historical meanings.

Image compression and **PDF stream compression** are independent recipe inputs.
Existing fixed choices are Flate (legacy headless fallback), Flate (Zopfli, slow) and Brotli
(limited reader support), with installed-runtime results recorded below.
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

§209 subsequently requests a separate SIZE-ONLY bitmap comparison:
[IMAGE_STREAM_COMPRESSION.md](IMAGE_STREAM_COMPRESSION.md). The native-only
figures here do not compare Brotli images with Indexed Flate or BW/colored
JBIG2. The bitmap study holds this native policy fixed; the product's native
selector does not silently change the selected image codec.

§§210/211 request a combination table and UI design review, documented in
[COMPRESSION_COMBINATIONS.md](COMPRESSION_COMBINATIONS.md). It inventories
the tiny native painting stream in actual FFPR/JBIG2 files and proposes
shared general compression for packed images and an inactive general control
for FFPR + specialized codecs. The earlier automatic/disabled FFPR control is
not approved. §256 now approves shared packed-image/native encoding for Best
only; §260 subsequently extends explicit Zopfli to eligible packed images
when its new predictor setting is supplied. Other legacy calls stay unchanged.

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

The completed [binary Zopfli-versus-Brotli experiment](INTEGRATED_COMPRESSION.md#ffpr-residual-compression--zopfli-versus-brotli-baseline)
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
empty intermediate streams until final garbage collection. Interrupted
diagnostic tests were worker-only; no running GUI was killed for this check.

## Benchmark protocol

Optimize/subset each source ONCE, then re-open that identical baseline for
each native-stream encoder. Leave image streams, native operator bytes and
font programs identical between paired candidates. Compare zlib levels 1/9,
Zopfli, Brotli levels 9/11, LZW, RunLength and uncompressed. Measure complete
PDF bytes as well as native raw/encoded bytes, encode/save/decode wall time,
page/stream counts and installed reader diagnostics. Equal container settings;
no per-candidate font subsetting differences or image transformations.

Use real images.pdf, a research paper and the NASA/vector model plus a
deterministic text/vector/font fixture. Validate every rewritten stream byte
for byte, all native text and actual full-page MuPDF pixels. Independently
check QPDF stream syntax/readback and Poppler text/renders; unknown-filter
warnings or wrong output are incompatibility, not a success because a process
returned zero. Explicitly preserve masks/encoded image bytes. Runtime versions
and repeat counts accompany actual results below; no invented numbers.

## Measured results — original controls 2026-10-15, Brotli refresh 2026-10-17

Both Brotli levels, **all eight complete files**, are actually re-encoded and
measured with **declaration OFF** under §254. The other 24 files remain
unchanged controls. Original declared artifacts and reader/timing evidence
remain historical; the size table below uses the new default-OFF files.
No size is inferred by subtracting historical metadata costs. Fresh native
stream readback and unchanged rendered graphs/image payloads preserve the
earlier all-page pixel proof, without repeating image processing or timing.

Original study command from the repository root (collects historical-style
timing too; it was not rerun for §254). The current size-only refresh uses
the commands in [integrated provenance](INTEGRATED_COMPRESSION.md#measurement-and-provenance):

```sh
./.venv/bin/python tools/bench_native_streams.py --repeat 2 --label <new-component-label>
./.venv/bin/python -m pytest tests/test_compression.py -q
```

Original PDFs, all-page Poppler PNGs and full per-run diagnostics/timings are
in `.tmp/native-stream-compression/main/metrics.json` and its sibling files.
Python 3.13.5, PyMuPDF/MuPDF 1.28.2, QPDF 12.2.0, Poppler 25.03.0 and the
installed `/usr/bin/zopfli`; no dependency was installed. The fixture is real
native text/line artwork plus an embedded subset font and an untouched JPEG,
not a plain-text string mislabeled as a PDF. Image payloads are UNCHANGED.
Current Brotli replacements and measured hashes/sizes are in
`.tmp/compression-experiments/brotli-default-off-publication-20261017/measurements.json`;
`component-controls.json` checks the reused controls' actual sizes and freezes
their current hashes (the original native manifest did not record output hashes).

| Source | Pages | Eligible streams | Native decoded B | Original PDF B |
|---|---:|---:|---:|---:|
| images.pdf | 1 | 4 | 6,902 | 1,494,439 |
| GAN paper | 9 | 43 | 453,607 | 530,482 |
| NASA Kepler model | 12 | 90 | 8,397,087 | 2,262,602 |
| Native text/vector/font fixture | 4 | 80 | 112,030 | 837,374 |

### Complete final PDF sizes (bytes)

All variants start from the SAME once-subset/optimized source. The figures
include font programs, original images, objects and the container, not only
the encoded stream sums. "none" disables eligible native-stream compression,
not object packing or image compression.

| Policy | images.pdf | GAN paper | NASA model | Native fixture |
|---|---:|---:|---:|---:|
| Uncompressed baseline | 1,495,674 | 671,288 | 9,154,319 | 143,942 |
| Flate/zlib-1 | 1,493,232 | 511,692 | 2,511,983 | 59,040 |
| Flate/zlib-9 (default) | 1,493,157 | 502,267 | 2,189,015 | 56,071 |
| Flate/Zopfli | 1,493,012 | 491,542 | 2,016,898 | 54,146 |
| Brotli-9 | 1,493,097 | 493,391 | 2,106,228 | 53,583 |
| Brotli-11 | 1,492,992 | 483,829 | 1,765,976 | 53,124 |
| LZW | 1,494,373 | 614,491 | 3,585,912 | 72,830 |
| RunLength | 1,495,332 | 675,044 | 8,908,640 | 120,574 |

Relative to default Flate, Zopfli saves 2.14% on the paper, 7.86% on NASA and
3.43% on the fixture. Brotli-11 now saves 3.67%, 19.33% and 5.26%, respectively.
On image-heavy images.pdf, Zopfli saves 145 B, while Brotli-11 saves 165 B
and is 20 B smaller than Zopfli. The old one-byte growth was declaration
overhead, not evidence that Brotli's native payload was larger.
Do not present a native-payload percentage as the whole-document saving.

### Median native encoding/readback time (seconds, two repeats)

Historical 2026-10-15 observations only; these times were **not rerun** and
do not describe the new declaration-OFF size measurements. No compute-time
comparison was requested for §254.

The encoder time includes per-stream native decode, encoding and exact
immediate readback. Saving/whole-file decoding are separate JSON fields. Runs
alternate encoder order and overlap validation work on the live desktop,
including the subsequently interrupted empty-Brotli diagnostic tests. These
are observed wall times, NOT isolated codec-speed rankings or guaranteed GUI
latency. The size and exact-byte results do not depend on that timing noise.

| Policy | images.pdf | GAN paper | NASA model | Native fixture |
|---|---:|---:|---:|---:|
| Flate/zlib-9 | 0.00383 | 0.03802 | 1.03653 | 0.06264 |
| Flate/Zopfli | 1.36531 | 12.07179 | 178.33298 | 14.40151 |
| Brotli-9 | 0.01606 | 0.10428 | 1.41582 | 0.59625 |
| Brotli-11 | 0.03119 | 1.80183 | 31.85182 | 0.45865 |

Every measured policy's save/decode time, native encoded byte count and BOTH
repetitions are retained in JSON, not only favorable examples. Zopfli is truly
applied to every nonempty eligible native stream; it is not silently limited
to small streams. Its external process is polled for cancellation and cleaned
up on cancellation/failure; no <200ms claim is made for the native Brotli call.

### Correctness and compatibility

32 source/policy cases, 64 output runs: every rewritten native stream decodes
byte-for-byte, all 26 source pages retain their native words/geometry, and
all actual MuPDF page pixels match their baseline (208 page candidates per
repeat). Image payload/filter/dimension signatures remain identical. A
separate full-source check also verifies original-to-optimized-baseline words
and actual pixels for all 26 pages, not only candidates against each other.

| Installed reader/check | Flate / Zopfli | LZW / RunLength | Brotli-9/11 |
|---|---|---|---|
| App's MuPDF 1.28.2 | Exact native bytes and all-page pixels | Exact | Exact, with valid nonempty streams |
| Poppler 25.03.0 | Exact extracted text and ALL page pixels | Exact | FAIL: unknown BrotliDecode; missing/wrong text and pixels |
| QPDF 12.2.0 | Syntax check 0 and largest native stream decodes exactly | Same | FAIL: check exit 2; largest stream does not decode correctly |

QPDF checks all syntax and independently decodes each candidate's largest
native stream; do not mislabel that as independent every-stream readback.
Some Poppler unsupported-filter cases return zero despite bad content; the
benchmark checks diagnostics and actual text/pixel equality, not exit status
alone. The paper's pre-existing closepath warnings occur in its baseline and
all ordinary supported variants; preserve them in the JSON rather than calling
that source warning-free. None is a cross-platform/all-viewer certificate.

## Product ruling §213 — best encoding, not speed-based alternatives

The earlier decision to expose ordinary zlib separately because of low
encoding cost is SUPERSEDED. For the same FlateDecode data, Zopfli adds no
decoder version, extension or special reader requirement. A conforming Flate
decoder can decode correctly packaged Zopfli zlib output just as it decodes
zlib's output. This is format compatibility, not a claim to have tested every
reader or the unrelated features of every possible PDF.

Target one optimized Flate choice using the strongest validated encoder;
Zopfli is the size winner among the Flate encoders in this native corpus.
Do not preserve weaker encoder choices for speed or dependency convenience.
If another implementation produces smaller valid SAME-format bytes for some
input, choosing it internally is not a reader-support compromise. No claim
that Zopfli is mathematically optimal on every input is required.

Brotli is a genuinely different decoder requirement and can improve native-
heavy sizes; retain its visible support warning. The intended distinction is
broad Flate compatibility versus allowing a supporting modern reader, not
"fast versus slow". A modern-reader requirement alone does not mean every
stream/file should be forced to Brotli: the current FFPR study still has
29 small-stream regressions without a declaration, with one layered-color
exception ([measured effect](INTEGRATED_COMPRESSION.md#ffpr-residual-compression--zopfli-versus-brotli-baseline)). Explicit codec labels still
mean those codecs; §§255/256 now authorize the separately named Best policy,
not silent substitutions in explicit recipes. LZW/RunLength remain losing
benchmark controls, not product options.

Best is added alongside the existing three fixed choices/default; it bypasses
the old opportunistic image-encoding path but does not silently change old
explicit recipes. TODO §217 tracks remaining legacy default/encoder alignment
and validation. Previously measured timings remain historical, not selection
criteria; no new timing run is requested or reported here.

Implementation verification is not designer acceptance. Tests additionally
cover independent image/native keys, all six actual image filters, shared
debounce, Save/Save As/load/Cancel and the empty-stream encoder defect.

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
See `DESIGN.md` §260 and the updated PNG decision tree.

§260 verification: **834 full-suite tests**, the real-file lifecycle smoke,
and viewed native-control captures at 1×/2× pass on 2026-10-18.
Implementation verification is not designer acceptance. See
`TEST_PLAN.md` and TODO §257.

## Original integration verification and acceptance (§205)

Final full suite: **429 passed in 174.96s**, 2026-10-15. Actual six-codec and
three-stream-policy GUI captures were viewed at normal/2×, with both-scale
resize and native-widget lifecycle checks passing; details and limits are in
[TEST_PLAN.md](TEST_PLAN.md). B105/B106 remain OPEN pending explicit designer
acceptance. No CPU-isolated benchmark is claimed.

A shutdown exposed a pre-existing callback-cancellation/worker error
serialization problem, recorded separately as B107 OPEN in `issues.md`.
Do not mistake a green compression suite for coverage or repair of that
shutdown path, or the normal GUI exit for proof that every canceled worker
reported cancellation cleanly.
