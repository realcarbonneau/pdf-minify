# Bitmap PDF compression — size-only paired benchmarks

Supporting component study: native compression is fixed in this document.
The primary final-file comparison uses realistic combination rows over six
representative PDFs, followed by focused scenarios (§223):
[INTEGRATED_COMPRESSION.md](INTEGRATED_COMPRESSION.md).

The component preparations below predate the uniform 300-DPI ruling
and shared assembly repairs (§§224–226, B108–B112). They retain the original
explicit recipes and are not current default-filter sizes. Use the primary
integrated overview and focused tables for repaired, uniformly 300-DPI
comparisons; do not relabel these older mixed-DPI artifacts.

§254 refreshes **all 44 Brotli outputs** (plain/PNG) with actual new encodings
and measured complete files, **declaration OFF**, on 2026-10-17. The other 132
component files retain their original measurements and checked hashes.
No pixels, palettes, DPI or thresholds were reprocessed; unchanged rendered
graphs/stream signatures preserve the original pixel-validation evidence.
This controlled metadata-policy refresh does not turn the old preparations
into measurements of the later compositor or new default recipes.

The current single-factor PNG-prediction experiment and its 16/64-color,
native/FFPR extension use the protocol in
[COMPRESSION_EXPERIMENTS.md](COMPRESSION_EXPERIMENTS.md#png-02--palette-and-page-mode-coverage).
Measured PNG-PDF bytes and signed changes from visible, measured plain
baselines are centralized in the integrated report, not duplicated here.

§233 moves the already-JBIG2 JFK scan out of the primary codec-comparison
table and retains it as B114's full-flow regression. The old component rows
below compare transformed pixels; they are not evidence of an improvement
over untouched source JBIG2. The current main BW source is CCITT TM972.
[JBIG2.md](JBIG2.md) documents the implemented encoder scope, safety limits
and TODO §240's optimization exploration; extra settings are not implemented.

Designer §§208/209/220, 2026-10-15 (America/New_York); TODO §§212/223.
Related: [COMPRESSION.md](COMPRESSION.md),
[COMPRESSION_COMBINATIONS.md](COMPRESSION_COMBINATIONS.md),
[LAYERED_COLOR_JBIG2.md](LAYERED_COLOR_JBIG2.md),
[NATIVE_STREAM_COMPRESSION.md](NATIVE_STREAM_COMPRESSION.md),
[TEST_PLAN.md](TEST_PLAN.md).

Size tables: [indexed color](#indexed-color-versus-colored-jbig2) and
[BW / FFPR](#bw-image-layer-and-full-page-rasterization).

## Scope and ruling

> you have color index filters that use flate, so you should make equivalent bechmarks for better compression on color index and bw please, compare with JBIG2 and color JPBIG2 also.  Do the work please.  We are only comparing size a this time.  Compute time is not measure because the cpu load on this workstation is fluctuating alot and unpredictably.

This headless study does not add product codecs or change presets/defaults.
No encode/decode times are collected or compared in this study. Process
timeouts are safety limits, not performance data. Work runs sequentially
with numerical thread limits.

The native-stream benchmark deliberately preserves image bytes. Its NASA
native-stream saving cannot be used as an image-compression result.
Here the native compression remains ordinary Flate for EVERY candidate;
only bitmap encodings/representation vary. Palette reduction and BW
thresholding happen once per case, never separately for each encoder.

## Paired representations

- Indexed color: same production RGB composition/one final-DPI resize and
  nearest-palette map. Minimal actual 1/2/4/8-bit packed palette indices.
  Compare current production Flate policy, explicit zlib-9, full Zopfli and
  Brotli-11; the latter three have plain and PNG-style adaptive row-predicted
  variants. Compare with one disjoint exact colored JBIG2 mask per nonwhite
  entry, retaining the same palette bytes/native overlay.
- BW: same production composed image layer on white (native artwork retained)
  or explicitly flattened full page, then one Otsu/manual threshold. Compare
  current production 1-bit Flate, the same three byte compressors/plain and
  row-predicted variants, and validated lossless JBIG2. No lossy symbol coding.

Row prediction is a reversible byte transform, not display smoothing or a
second image filter. Use predictor 15, Colors 1, actual BitsPerComponent and
Columns; packed-row padding remains exact. Declare all decode parameters.
Brotli is the image's actual filter, never a wrapper around encoded JBIG2.
The existing core native Brotli encoder and optional extension policy are reused;
the existing fixed native policies still exclude image XObjects. §§255/256
later add Best for packed-image/native streams; this fixed-encoder component
study and its frozen measurements do not become Best measurements.

## Correctness, size accounting and limits

Store actual optimized PDFs, every codec's encoded bitmap bytes, full-file
bytes, input/output/sample/palette hashes, dimensions, image counts and diagnostics.
Validate final filter dictionaries and decoded samples, reconstruct colored
mask coverage, and compare actual no-AA page pixels against the paired
current-Flate baseline. Native text/geometry, page boxes/rotation, links and
annotations must stay intact (except deliberately flattened BW). Verify both
small/odd-width fixtures and real multipage outputs. No silent substitutions.
Failed decode/timeout is NOT a valid small-file result.

Full-PDF comparisons include palette/mask/white-base/content/container overhead
with the Brotli declaration **OFF** in current tables. Within packed-stream alternatives, retain
the identical native assembly. Colored JBIG2 necessarily uses different image
paint operators, so compare retained native artwork and complete output, not
require identical canvas-paint bytes across different representations.

Control PDF identifier framing too: MuPDF can serialize a random new 16-byte
ID as a literal or hex string, making otherwise identical files differ by a
few bytes. The standalone study assigns deterministic, distinct, fixed-width
ASCII IDs from source/sample/variant hashes and uses the shared saver with
`no_new_id=True`; production keeps its unchanged default ID behavior. No
codec bytes or content are changed by that control. Pre-control generated
PDFs are preserved as `.original-id.pdf` when resumed, not counted as final
candidates. Existing PDFs are revalidated against fresh preparation and input/
environment hashes; only missing candidates are encoded again.
These are exact sizes of the supplied controlled benchmark PDFs. Normal app
saves keep their usual ID generation and may differ by a few framing bytes;
the table is not an estimate of, or override for, a live app artifact's size.
For already saved xref-stream PDFs, a plain in-memory container roundtrip
precedes setting the trailer IDs: the installed binding otherwise changed
an xref object without changing the writer's observed trailer. Encoded image
streams are preserved; final output still uses the shared optimized container.

Source native-path warnings are recorded separately from image-decoder
diagnostics. A known malformed GAN closepath is reproduced on the original;
matching native warnings are retained in JSON, never called warning-free.
The process-private sequential verifier archives drained diagnostics per stage;
any image decode warning or new output-only page message still fails. Core
production warning handling is unchanged.

Installed Poppler 25.03.0/QPDF 12.2.0 do not decode Brotli; do not call those
compatibility successes. Existing colored-mask versus Indexed Poppler page
sampling differences remain documented in the earlier study. This size study
does not confer an all-reader/platform certificate or designer acceptance.

Normative applicability: [PDF Association EXTN-BROTLI-1 v1.3, §§5.1/5.2](https://pdfa.org/download-area/publications/pdf-extension-brotli.pdf)
permits Brotli wherever Flate is allowed, except inline images, and includes
the existing optional prediction parameters. Image XObjects are applicable.

## Results

Original preparation/validation **2026-10-15**, all 44 Brotli files re-encoded
and remeasured **2026-10-17**: **22 paired cases, 176 final PDFs, 600 candidate
pages** (75 case-pages × eight encodings). The original identifier-control
pass checked every final candidate without re-encoding its image data. All
stored samples/mask reconstructions and actual no-AA page pixels match at
72dpi AND recipe DPI. Input/output hashes, encoded image byte counts, exact
dimensions and diagnostics accompany the actual PDFs in the combined JSON.
There are **zero timing fields**. No result below comes from the native-only
study, a size estimator, a page subset or an invalid decoder placeholder.

All figures below are **complete final PDF bytes**, not bitmap payload sums.
`Flate` means explicit zlib-9/plain; it equals the current product-Flate
reference's size in EVERY case in this corpus. Both entries remain in JSON;
the duplicate table column is omitted. Classic Flate results remain reference
comparisons, not an additional product choice (§214). `+PNG` means reversible
adaptive row prediction BEFORE the same compressor, not a PNG file embedded
in the PDF or a second compression pass. Compare each predicted result with
its matching plain column. Zopfli uses the entire workload; Brotli is level
11. Native streams remain Flate in every row. All columns are retained
together under §220, superseding the earlier documentation split.

**Bold** marks the smallest complete-PDF size in each row, including ties (§221).
Reader-support limitations above still apply to highlighted results.

### Indexed color versus colored JBIG2

The color number is the requested maximum total palette entries, including
white when present. Compare encodings WITHIN a row: different color counts/
DPIs are different prepared images, not an equal-quality contest.

| Source / DPI / colors | Flate | Flate+PNG | Zopfli | Zopfli+PNG | Brotli | Brotli+PNG | Colored JBIG2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| images / 150 / 5 | 19,598 | 20,912 | 18,284 | 19,118 | 14,934 | 17,385 | **13,320** |
| images / 150 / 16 | 29,039 | 31,815 | 26,986 | 28,696 | **22,322** | 26,708 | 24,814 |
| images / 150 / 64 | 34,550 | 46,550 | 31,108 | 40,785 | **27,093** | 38,443 | 46,557 |
| GAN / 150 / 5 | 344,069 | 347,428 | 339,419 | 341,833 | **330,146** | 337,894 | 338,703 |
| GAN / 150 / 16 | 378,991 | 388,336 | 373,255 | 378,806 | **361,053** | 373,417 | 389,741 |
| GAN / 150 / 64 | 429,411 | 459,529 | 419,203 | 441,977 | **405,110** | 433,282 | 478,968 |
| images / 300 / 5 | 32,293 | 40,180 | 29,509 | 35,127 | 23,575 | 30,520 | **18,543** |
| images / 300 / 16 | 50,951 | 60,783 | 45,315 | 51,758 | 36,860 | 47,398 | **35,412** |
| Synthetic flat / 150 / 5 | 3,103 | 3,776 | 2,788 | 3,578 | **2,181** | 2,708 | 3,415 |
| Synthetic flat / 150 / 16 | 3,103 | 3,776 | 2,788 | 3,578 | **2,181** | 2,708 | 3,415 |
| Synthetic noise / 150 / 5 | 115,567 | 152,625 | 108,454 | 151,581 | **107,632** | 149,396 | 145,977 |
| Synthetic noise / 150 / 16 | 115,567 | 152,625 | 108,454 | 151,581 | **107,632** | 149,396 | 145,977 |

Both controls have FIVE actual colors even when 16 are requested, so their
5/16 rows intentionally have identical pixels/bytes; they are not independent
examples. All use 4bpc; real 64-color cases use 8bpc. Per-page actual palette
counts are in JSON. The earlier Oct-14 study has different native optimization/
ID settings; do not mix its byte counts with these paired candidates.

### BW image layer and full-page rasterization

All BW rows use 300dpi, 1-bit samples. `images`/`GAN`/scans without FFPR
retain native artwork; FFPR deliberately flattens native text/vectors too.
Compare encodings within each row, not retained-native versus rasterized
content as though those were the same rendered image.

| Source / mode / threshold | Flate | Flate+PNG | Zopfli | Zopfli+PNG | Brotli | Brotli+PNG | BW JBIG2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| images / image layer / Otsu | 22,605 | 24,096 | 21,051 | 21,637 | 14,992 | 18,176 | **10,133** |
| images / image layer / T=180 | 23,451 | 24,888 | 21,853 | 22,344 | 15,686 | 19,064 | **10,410** |
| images / image layer / T=210 | 26,843 | 28,550 | 24,670 | 25,452 | 18,123 | 22,478 | **11,244** |
| GAN / image layer / Otsu | 337,441 | 338,931 | 334,900 | 335,319 | 323,880 | 327,933 | **319,797** |
| JFK poor copies / image layer / Otsu | 709,790 | 818,583 | 634,911 | 740,164 | 580,974 | 706,597 | **350,007** |
| NACA formulas / image layer / Otsu | 440,623 | 443,514 | 402,184 | 390,412 | 299,260 | 366,668 | **198,920** |
| images / FFPR / Otsu | 17,976 | 19,777 | 16,136 | 16,930 | 9,837 | 13,737 | **4,095** |
| GAN / FFPR / Otsu | 786,664 | 776,860 | 732,409 | 693,876 | 563,060 | 624,574 | **321,295** |
| Synthetic flat / image layer / Otsu | 3,479 | 4,489 | 3,256 | 4,269 | 2,389 | 3,233 | **2,094** |
| Synthetic noise / image layer / Otsu | 102,092 | 98,119 | 91,217 | 86,029 | 83,266 | 80,852 | **63,075** |

### What these sizes show

- **Indexed color has no universal winner.** Plain Brotli wins nine of the
  twelve cases (five of eight real-artwork cases). Colored JBIG2 wins the
  images.pdf five-color cases at both DPIs and the 16-color case at 300dpi.
  The same 16-color artwork switches winner between 150 and 300dpi.
- **BW JBIG2 wins all ten tested BW cases**, including both real scans, both
  FFPR cases and both controls. Brotli improves on the current Flate sizes,
  but does not beat the specialized BW codec in this corpus. This is not a
  proof for all possible BW input/threshold combinations.
- **Payload size alone gives wrong rankings.** At images/150/16, colored
  JBIG2's image payload is 13,241 B versus Brotli's 14,128 B, yet its COMPLETE
  file is 24,814 B versus 22,322 B. Fifteen masks plus paint/resources cost
  more than the payload saving. At 64 colors there are 63 masks, not one.
- **Prediction is not automatically an improvement.** Against the same
  encoder WITHOUT prediction, 60 of 66 predicted PDFs are larger, including
  all indexed-color pairs. Six BW pairs shrink by 1.25%–5.69%: NACA/Zopfli,
  GAN-FFPR/Flate or Zopfli, and the noisy control with all three compressors.
  Each percentage is `100 × (plain bytes - predicted bytes) / plain bytes`;
  none changes the winning algorithm. The best Brotli BW-noise result is the
  predicted 80,852 B, still above JBIG2's 63,075 B. All variants remain visible.
- Native text/fonts/vectors dominate some retained-native files, especially
  GAN, so whole-file gains can be much smaller than bitmap-payload gains.
  Conversely, a processed 300dpi scan need not be smaller than its original
  already-compressed source. The comparison is equal FINAL prepared pixels,
  not a claim that upsampling/thresholding is lossless to the source.

This supports testing Brotli as an optional indexed-image candidate, not
replacing every color or BW encoding with it. No product codecs, presets,
default policy, saved filter identity or UI controls were changed by this
study. The shared saver only gained an optional identifier-preservation
argument; ordinary product saves keep the previous default behavior.

Original dataset: `.tmp/image-stream-compression/size-20261015/metrics.json`.
Each original case's sibling `metrics.json` and PDFs retain the old declared
figures, not the refreshed Brotli table values. Initial source-warning interruption and pre-control ID files are
retained as diagnostic history; only final validated paths listed in JSON
are the 176 candidates. The final normalization pass reused EVERY encoded
candidate and returned `IMAGE STREAM SIZE BENCHMARK GREEN`. The full-suite
handoff evidence is in [TEST_PLAN.md](TEST_PLAN.md). Current Brotli replacements,
actual final hashes/sizes and the unchanged-control audit are frozen in
`.tmp/compression-experiments/brotli-default-off-publication-20261017/`
(`measurements.json`, `analysis.json`, `component-controls.json`). Original
declaration-ON files remain unchanged; no table value is an estimated deduction.

Original component-stage complete suite: **460 passed**, `./test.sh`, exit 0. The 31 new
benchmark tests pass, including source diagnostics, controlled read-back
trailer IDs and strict actual-pixel comparisons. Current §254 regression and
full-suite evidence is in [TEST_PLAN.md](TEST_PLAN.md); verification is not
designer acceptance.

## Reproduction and corpus

```sh
nice -n 10 ./.venv/bin/python tools/bench_image_streams.py --label <new-component-label>
./.venv/bin/python -m pytest tests/test_image_stream_bench.py -q
```

The label names a NEW output directory (existing directories are refused
unless `--resume` is explicit). Resume revalidates all reused PDFs and refuses
changed input/preparation/environment hashes; it does not blindly trust JSON.
All final PDFs, per-case JSON and the combined `metrics.json` are retained in
`.tmp/image-stream-compression/<label>/`. The 36dpi `--smoke` run is a separate
tool check, never substituted for these real-size outputs. One encoding per
candidate: controlled identifier framing, no timing repetitions or timing
fields. External encoder failure/timeout stops the run, not a mislabeled win.

Full plan: **22 paired cases, eight encodings each**. Indexed cases use
images.pdf and the nine-page GAN paper at 150dpi / 5, 16 and 64 colors;
images.pdf also at 300dpi / 5 and 16 colors. Flat/noise controls use 150dpi /
5 and 16 colors. BW image-layer cases use images.pdf at 300dpi with Otsu,
Simple T=180 and Simple T=210; GAN, eight-page JFK poor copies and seven-page
NACA formulas at 300dpi/Otsu; flat/noise controls at 300dpi/Otsu. Additional
images.pdf and GAN cases use BW FFPR at 300dpi/Otsu. Entire documents, not
unreported page subsets. Colors mean requested total palette entries, with
actual counts/bit depths saved per page. The seeded controls are explicitly
synthetic, not scans or estimates. Every eligible source page is prepared
once and shared across all eight encodings within that case.

Runtime: Python 3.13.5, PyMuPDF/MuPDF 1.28.2, NumPy 2.5.3, Pillow 12.3.0,
`/usr/bin/jbig2` reporting jbig2enc 0.30 and `/usr/bin/zopfli` from Debian
package 1.0.3-3. No dependencies were installed. Per-case JSON retains actual
binding/library versions and executable paths; input/output hashes identify
the exact artifacts. The JBIG2 trials use the current lossless generic-region
`jbig2 -p` path, not lossy symbol substitution or shared-page dictionaries.

`current-flate` uses the real product policy: packed BW zlib-9; Indexed
`deflate_best` (Zopfli for at most 100,000 raw bytes when available, otherwise
zlib-9). The explicit Zopfli trials encode the full workload without that
cutoff. Plain and adaptive-PNG trials use the same packed-row source for
each byte codec. The prediction choice per row minimizes the usual sum of
absolute signed residual bytes; it is a deterministic common heuristic,
not an exhaustive codec-specific prediction search or a global optimum claim.
