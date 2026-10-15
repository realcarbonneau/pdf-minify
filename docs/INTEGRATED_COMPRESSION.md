# Integrated compression — representative complete-PDF sizes

Designer §§210–214/220–223, 2026-10-15 (America/New_York); TODO §226.

## Scope and five representative classes

This is the primary size comparison: **realistic algorithm combinations as
rows, five complete repository PDFs as columns**. Every numeric result is
the actual complete saved PDF size in bytes, including fonts, native streams,
images, palettes/masks, declarations and container overhead. No timing scores,
payload estimates or arithmetic combinations of separate studies are used.

Five classes are a practical baseline, not an exhaustive PDF taxonomy. The
load-bearing distinction is what dominates the file: native instructions and
fonts, scanned text pixels, photographic pixels, graphic/palette pixels, or
a substantial mixture. Noise, resolution, existing encoding, OCR, masks,
overlap and embedded resources cut across these classes; focused tables and
the supporting studies cover those axes without widening the overview.

| Representative class | Complete PDF | Pages | Original bytes |
|---|---|---:|---:|
| Native text/vectors | [form-fw9.pdf](../examples/form-fw9.pdf) | 6 | 140,815 |
| BW scan | [scan-jfk-poor-copies.pdf](../examples/scan-jfk-poor-copies.pdf) | 8 | 349,667 |
| Color photos | [news-crater-lake-2026.pdf](../examples/news-crater-lake-2026.pdf) | 8 | 5,550,048 |
| Flat-color artwork | [images.pdf](../examples/images.pdf) | 1 | 1,494,439 |
| Mixed text/images | [paper-arxiv-1406.2661.pdf](../examples/paper-arxiv-1406.2661.pdf) | 9 | 530,482 |

The photo column is an actual photo-rich newspaper, not `images.pdf`. The
latter contains raster logos/artwork (including gradients) and very little
text. The W-9 contains no image objects: image-only recipes there are marked
**— (not applicable)**, not fabricated repeats of its native-only result.
FFPR is applicable to W-9 because it deliberately rasterizes that native text.
`FAILED` means a candidate failed exact-output validation. `PREP FAILED`
means its shared source-to-preparation stage was rejected; dependent codecs
cannot be compared, not that each independently failed to encode. Neither
gets a size or a ranking, and neither is silently treated as zero.

## Reading the results

- **Zopfli-Flate** is optimized standard FlateDecode; **classic Flate** is a
  labeled reference, not another recommended encoder-speed choice.
- **Brotli** needs a verified supporting reader. It is not enabled merely by
  choosing JPEG/JBIG2 for the images; reader limitations remain separate from
  size results. See [reader support](#reader-support).
- Packed BW/indexed rows use the **same general compressor for images and
  native streams**. Mixed general-codec pairs are excluded. Specialized
  JPEG/JPEG2000/JBIG2 rows retain their meaningful native Zopfli/Brotli choices.
- **PNG prediction** is reversible row prediction before that same image
  compressor, not another PNG image or a nested second compressor. Both plain
  and predicted variants remain visible.
- **Bold** marks the minimum within the **same PDF column and recipe group**,
  including ties. Groups are preserve-images, each explicit full-color codec
  setting, indexed palette, BW with native artwork, and BW FFPR. Comparing
  unrelated PDFs across a row, or BW against color, would not identify a
  useful winner. Highlighting never overrides reader-support requirements.

### Fixed overview recipes

All non-FFPR rows preserve native text/vectors. Preserve-images keeps original
encoded image bytes. Color and indexed canvases target **150dpi**; indexed
uses **five total colors**, including white when present. JPEG uses quality
50; JPEG2000 uses rate 192 (lossy) or explicit lossless encoding. JPEG2000
lossless preserves the prepared 150dpi canvas, not the unresampled source.
BW uses **300dpi / Otsu**; FFPR converts the whole page, losing native text
selectability and vector precision. Threshold/palette reduction and DPI
changes are fidelity decisions, not lossless compression algorithms.
Palette/BW transforms affect the bitmap canvas, not retained native colors.

Preserve-images rows are **native-only baseline controls**: original image
formats/bytes are deliberately untouched. They are diagnostic references,
not new packed-image/general-compressor pairings.

The FFPR + JBIG2 row uses measured Zopfli-Flate residual painting streams
once; redundant native-codec permutations are not separate rows. This does
**not** claim an implemented automatic plain/Flate selector. Color FFPR is
still unsupported and is not presented as a measured option. Some packed
Brotli/Zopfli image rows remain benchmark prototypes; this documentation does
not add GUI choices, change defaults or migrate saved recipes.

## Overview — final complete-file bytes

| Algorithm combination | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images |
|---|---:|---:|---:|---:|---:|
| Preserve images + Classic Flate (reference) native | 188,447 | 341,697 | 4,641,959 | 1,493,125 | 502,235 |
| Preserve images + Zopfli-Flate native | 187,455 | **341,696** | 4,574,656 | **1,492,980** | 491,510 |
| Preserve images + Brotli native | **182,638** | 341,881 | **4,472,657** | 1,493,126 | **483,963** |
| JPEG q50 + Zopfli-Flate native | — | **1,413,540** | PREP FAILED | **47,272** | 389,732 |
| JPEG q50 + Brotli native | — | 1,413,721 | PREP FAILED | 47,434 | **382,174** |
| JPEG2000 lossy r192 + Zopfli-Flate native | — | **268,346** | PREP FAILED | **40,804** | 366,335 |
| JPEG2000 lossy r192 + Brotli native | — | 268,527 | PREP FAILED | 40,966 | **358,777** |
| JPEG2000 lossless + Zopfli-Flate native | — | **10,813,283** | PREP FAILED | **227,479** | 919,213 |
| JPEG2000 lossless + Brotli native | — | 10,813,464 | PREP FAILED | 227,641 | **911,655** |
| Indexed 5 colors + Classic Flate (reference) | — | 569,637 | PREP FAILED | 19,598 | 344,069 |
| Indexed 5 colors + Classic Flate (reference) + PNG prediction | — | 843,496 | PREP FAILED | 20,912 | 347,428 |
| Indexed 5 colors + Zopfli-Flate | — | **500,222** | PREP FAILED | 18,126 | 328,678 |
| Indexed 5 colors + Zopfli-Flate + PNG prediction | — | 766,135 | PREP FAILED | 18,960 | 331,092 |
| Indexed 5 colors + Brotli | — | 514,767 | PREP FAILED | 14,936 | **311,847** |
| Indexed 5 colors + Brotli + PNG prediction | — | 730,101 | PREP FAILED | 17,387 | 319,595 |
| Indexed 5 colors + colored JBIG2 + Zopfli-Flate native | — | FAILED | PREP FAILED | **13,163** | 327,961 |
| Indexed 5 colors + colored JBIG2 + Brotli native | — | FAILED | PREP FAILED | 13,319 | 320,388 |
| BW; keep native + Classic Flate (reference) | — | 709,790 | PREP FAILED | 22,605 | 337,441 |
| BW; keep native + Classic Flate (reference) + PNG prediction | — | 818,583 | PREP FAILED | 24,096 | 338,931 |
| BW; keep native + Zopfli-Flate | — | 634,911 | PREP FAILED | 20,894 | 324,159 |
| BW; keep native + Zopfli-Flate + PNG prediction | — | 740,164 | PREP FAILED | 21,480 | 324,578 |
| BW; keep native + Brotli | — | 581,155 | PREP FAILED | 14,997 | 305,581 |
| BW; keep native + Brotli + PNG prediction | — | 706,778 | PREP FAILED | 18,181 | 309,634 |
| BW; keep native + JBIG2 + Zopfli-Flate native | — | **350,007** | PREP FAILED | **9,976** | 309,056 |
| BW; keep native + JBIG2 + Brotli native | — | 350,188 | PREP FAILED | 10,138 | **301,498** |
| BW FFPR + Classic Flate (reference) | 779,634 | 690,447 | 2,568,470 | 17,976 | 786,664 |
| BW FFPR + Classic Flate (reference) + PNG prediction | 772,373 | 803,152 | 2,562,141 | 19,777 | 776,860 |
| BW FFPR + Zopfli-Flate | 731,120 | 617,248 | 2,370,682 | 16,136 | 732,409 |
| BW FFPR + Zopfli-Flate + PNG prediction | 685,820 | 726,364 | 2,276,148 | 16,930 | 693,876 |
| BW FFPR + Brotli | 564,200 | 565,269 | 1,830,845 | 10,006 | 563,229 |
| BW FFPR + Brotli + PNG prediction | 624,245 | 693,435 | 2,154,464 | 13,906 | 624,743 |
| BW FFPR + JBIG2; optimized residual streams | **320,500** | **336,978** | **1,117,948** | **4,095** | **321,295** |

Native-only results can exceed the untouched original; the original sizes
above remain the baseline. An encoding result is not automatically an
improvement merely because it is the smallest tested encoding in its group.

## Focused scenarios

These tables keep the same realistic combination policy. They change only
the settings named in each column; every numeric entry is a complete PDF, not
an extracted image or a component payload. Synthetic flat/noise controls
remain in the supporting [bitmap study](IMAGE_STREAM_COMPRESSION.md#results).

### Rejected output — colored JBIG2 on the fractional-page scan

The scan's two colored-JBIG2 cells are marked `FAILED`, not omitted or ranked.
On page 2 the decoded mask/palette samples are exact, but embedding the canvas
as nested page Forms loses non-white pixels in the rightmost column (140 at
72dpi; 165 at 150dpi). This is a whole-page boundary/clipping discrepancy,
not a lossless JBIG2 mask-decoding failure. Evidence and the open defect are
in [B108](../issues.md#b108--open--colored-stencil-embedding-clips-fractional-page-edge-pixels-worker-benchmark-finding).
The checks were not weakened, the input was not replaced, and no product
fix or acceptance is claimed. Other outputs are validated independently.

### Rejected preparation — tagged-content warnings in the photo newspaper

Crater Lake's native-preserving reconstructed-image rows are marked
`PREP FAILED`. Their baseline introduces `ActualText with no position`
warnings absent in the original; later saves preserving that frozen baseline
do not make it valid. On page 1, the original and a rejected preparation both
extract 1,224 visible words, so the observed problem is new tagged-content
diagnostics, not proven visible-word loss. The shared assembly must be repaired
before its full-color and palette codec comparisons can be ranked.
This is [open B109](../issues.md#b109--open--image-layer-reconstruction-introduces-unpositioned-actualtext-worker-benchmark-finding),
not a general-compressor or image-decoder failure. Preserve-images and FFPR
are measured independently; the representative input has not been changed
to conceal the failure. No product fix is implemented in this documentation task.

The BW-image preparation fails a separate invariant: original color photos
are still painted above the new 1-bit canvas. Its eight dependent rows are
also `PREP FAILED`, not equivalent BW encodes. See
[open B110](../issues.md#b110--open--native-overlay-retains-original-color-photos-over-the-bw-canvas-worker-benchmark-finding).
This is an assembly failure, not merely an unused-resource counting artifact;
whether it shares B109's root cause is not established. FFPR does not use
that native-overlay construction and is checked independently.

### Color photography — preserve full color versus encode a target canvas

Crater Lake is eight complete photo-rich newspaper pages. Native content is
retained. Preserve-images keeps source samples; the other rows use the stated
150dpi target. JPEG q50 and JPEG2000 rate 192 are **not quality-matched**.
There is no claim that reducing photos to five colors preserves full color.

| Algorithm combination | Color photos |
|---|---:|
| Preserve images + Classic Flate (reference) native | 4,641,959 |
| Preserve images + Zopfli-Flate native | 4,574,656 |
| Preserve images + Brotli native | **4,472,657** |
| JPEG q50 + Zopfli-Flate native | PREP FAILED |
| JPEG q50 + Brotli native | PREP FAILED |
| JPEG2000 lossy r192 + Zopfli-Flate native | PREP FAILED |
| JPEG2000 lossy r192 + Brotli native | PREP FAILED |
| JPEG2000 lossless + Zopfli-Flate native | PREP FAILED |
| JPEG2000 lossless + Brotli native | PREP FAILED |

### Logos/artwork — palette count and target DPI

All columns use the same complete `images.pdf`. Each column fixes its prepared
pixels; encoder comparisons within that column are exact-pixel comparisons.
Changing its palette or DPI is not an equal-fidelity contest.

| Algorithm combination | 5 colors / 150dpi | 16 colors / 150dpi | 64 colors / 150dpi | 5 colors / 300dpi | 16 colors / 300dpi |
|---|---:|---:|---:|---:|---:|
| Indexed + Classic Flate (reference) | 19,598 | 29,039 | 34,550 | 32,293 | 50,951 |
| Indexed + Classic Flate (reference) + PNG prediction | 20,912 | 31,815 | 46,550 | 40,180 | 60,783 |
| Indexed + Zopfli-Flate | 18,126 | 26,828 | 30,950 | 29,352 | 45,158 |
| Indexed + Zopfli-Flate + PNG prediction | 18,960 | 28,538 | 40,627 | 34,970 | 51,601 |
| Indexed + Brotli | 14,936 | **22,324** | **27,095** | 23,580 | 36,865 |
| Indexed + Brotli + PNG prediction | 17,387 | 26,710 | 38,445 | 30,525 | 47,403 |
| Indexed + colored JBIG2 + Zopfli-Flate native | **13,163** | 24,652 | 46,352 | **18,387** | **35,251** |
| Indexed + colored JBIG2 + Brotli native | 13,319 | 24,783 | 46,430 | 18,545 | 35,384 |

### Mixed text/images — palette size while preserving native artwork

All columns use the complete nine-page GAN paper at 150dpi. Text, vectors
and fonts remain native; only the composed bitmap layer is palette-reduced.

| Algorithm combination | 5 colors | 16 colors | 64 colors |
|---|---:|---:|---:|
| Indexed + Classic Flate (reference) | 344,069 | 378,991 | 429,411 |
| Indexed + Classic Flate (reference) + PNG prediction | 347,428 | 388,336 | 459,529 |
| Indexed + Zopfli-Flate | 328,678 | 362,514 | 408,462 |
| Indexed + Zopfli-Flate + PNG prediction | 331,092 | 368,065 | 431,236 |
| Indexed + Brotli | **311,847** | **342,754** | **386,811** |
| Indexed + Brotli + PNG prediction | 319,595 | 355,118 | 414,983 |
| Indexed + colored JBIG2 + Zopfli-Flate native | 327,961 | 378,989 | 468,130 |
| Indexed + colored JBIG2 + Brotli native | 320,388 | 371,366 | 460,401 |

### Scanned BW text — different source material

JFK poor copies (eight pages) and NACA formulas (seven pages) use 300dpi/Otsu
with native artwork retained if any. A degraded scan and mathematical print
are distinct stress cases; one scan cannot establish a universal codec winner.

| Algorithm combination | JFK poor copies | NACA formulas |
|---|---:|---:|
| BW; keep native + Classic Flate (reference) | 709,790 | 440,623 |
| BW; keep native + Classic Flate (reference) + PNG prediction | 818,583 | 443,514 |
| BW; keep native + Zopfli-Flate | 634,911 | 401,558 |
| BW; keep native + Zopfli-Flate + PNG prediction | 740,164 | 389,786 |
| BW; keep native + Brotli | 581,155 | 297,209 |
| BW; keep native + Brotli + PNG prediction | 706,778 | 364,617 |
| BW; keep native + JBIG2 + Zopfli-Flate native | **350,007** | 198,294 |
| BW; keep native + JBIG2 + Brotli native | 350,188 | **196,869** |

### Threshold sensitivity — one source, three explicit BW transforms

All columns use `images.pdf` at 300dpi, native artwork retained. Otsu and
Simple thresholds 180/210 produce different pixels; compare codecs within
each column, not thresholds as though their visual output were identical.

| Algorithm combination | Otsu | Simple T180 | Simple T210 |
|---|---:|---:|---:|
| BW; keep native + Classic Flate (reference) | 22,605 | 23,451 | 26,843 |
| BW; keep native + Classic Flate (reference) + PNG prediction | 24,096 | 24,888 | 28,550 |
| BW; keep native + Zopfli-Flate | 20,894 | 21,696 | 24,513 |
| BW; keep native + Zopfli-Flate + PNG prediction | 21,480 | 22,187 | 25,295 |
| BW; keep native + Brotli | 14,997 | 15,691 | 18,128 |
| BW; keep native + Brotli + PNG prediction | 18,181 | 19,069 | 22,483 |
| BW; keep native + JBIG2 + Zopfli-Flate native | **9,976** | **10,252** | **11,087** |
| BW; keep native + JBIG2 + Brotli native | 10,138 | 10,415 | 11,249 |

### Native-heavy files — fonts, drawings and container overhead

Preserve all original encoded images. These columns isolate different native
content burdens rather than calling all native-heavy files equivalent. The
last column is the earlier four-page native text/vector/font fixture, not
one of the five representative repository inputs.

| Algorithm combination | W-9 / 6 pages | Form 941 / 3 pages | Kepler / 12 pages | Native font fixture / 4 pages |
|---|---:|---:|---:|---:|
| Preserve images + Classic Flate (reference) native | 188,447 | 872,512 | 2,188,983 | 56,039 |
| Preserve images + Zopfli-Flate native | 187,455 | 854,321 | 2,016,866 | 54,114 |
| Preserve images + Brotli native | **182,638** | **776,197** | **1,766,110** | **53,258** |

## What these results establish

- The five-color artwork output is 13,163 B with colored JBIG2 +
  Zopfli-native, versus 14,936 B with shared Brotli. The mixed
  paper reverses that choice: 311,847 B for shared Brotli versus
  320,388 B for colored JBIG2 + Brotli-native. Representation matters.
- On the eight-page BW scan, JBIG2 + Zopfli-native is 350,007 B,
  versus 581,155 B for shared Brotli at the same prepared
  BW pixels. The preserve-images result is a separate fidelity/baseline choice.
- The photo table separates retaining original image bytes from encoding a
  full-color target canvas. Palette/BW reductions remain explicitly different
  representations; their smaller files are not lossless photo-codec wins.
  On Crater Lake, preserve-images + Brotli is 4,472,657 B.
  Its native-preserving reconstructed-image recipes fail the source-to-preparation
  diagnostic/assembly gates (B109/B110); those native-preserving JPEG/palette/
  BW-image comparisons remain unrankable until the shared preparation is repaired.
  Independent BW FFPR yields 1,117,948 B with JBIG2, versus
  1,830,845 B with shared Brotli, at the same BW pixels.
- A native-heavy file, a scan and a photographic page exercise different
  compression burdens. No single source, generic codec ranking or minimum
  across unlike fidelity groups is an adequate project-wide conclusion.

## Measurement and provenance

The earlier exhaustive study measured 549 complete outputs over 51 recipes.
Those PDFs and their source/preparation/output hashes remain archived in
`.tmp/integrated-compression/size-20261015-v2/`. It was a diagnostic cross-product,
not the agreed product-combination table. Mixed general-codec pairs are not
republished as useful options. Component studies retain their methods as
supporting evidence, not arithmetic substitutes for combined measurements.

The representative overview covers **138 applicable cells**: **114 verified complete outputs** (**30 newly measured**, **84 reused** from the verified prior study) and **24 explicitly rejected cells** with no published size. The focused tables also select verified prior outputs; altogether the published tables reference **195 distinct actual PDFs**. New artifacts and per-cell origins/hashes are in `.tmp/integrated-compression/representative-20261015-v3/`. The overview has 32 realistic combination rows over exactly five complete source files, with 22 explicitly inapplicable image-free cells.

All newly measured valid cells use the existing real page composer, image encoders
and shared final saver. Their frozen preparations retain exact encoded and
decoded image bytes and decoded native streams. Every new final output is
checked for page geometry, native content, metadata/attachments and all-page
no-AA pixel equality at 72dpi and recipe DPI. New output-only diagnostics
fail validation; known source-native warnings remain visible separately.
Prepared fonts are not re-subset: re-subsetting already-subset TrueType can
rewrite checksum bytes and disturb a supposedly frozen comparison.

Prior output reuse requires matching current recorded implementation hashes,
source/preparation hashes, exact-output verification flags, actual full-file
bytes and output hashes. Source-to-preparation diagnostics are checked too,
including reused production JPEG/JPX preparations; a frozen invalid baseline
is not valid evidence. No estimate fills a missing cell. New measurements
run sequentially, headlessly and with numerical thread limits, without a
desktop application launch. The analysis records no compute-time metric.

Reproduce from the repository root with the prior preparations retained:

```sh
nice -n 10 ./.venv/bin/python tools/bench_compression_overview.py --label <new-label>
./.venv/bin/python -m pytest tests/test_compression_overview.py tests/test_integrated_compression_bench.py -q
```

Use `--resume` only for an unchanged interrupted run. The reusable runner
records its own implementation hash and reuses the strict integrated verifier;
it emits Markdown and JSON evidence.

## Reader support

Classic Flate and Zopfli-Flate use the same FlateDecode reader format. Brotli
requires a supporting reader and its extension declaration whether it is in
the image or native layer. Existing installed-reader evidence and failures
remain in [NATIVE_STREAM_COMPRESSION.md](NATIVE_STREAM_COMPRESSION.md#correctness-and-compatibility).
Size minima are not all-reader or cross-platform certificates. The design/
capability boundary remains in [COMPRESSION_COMBINATIONS.md](COMPRESSION_COMBINATIONS.md).

Verification: 20 representative selection/hash/format/failure tests plus 14 strict integrated-encoder tests. All published values, tied bold minima and referenced output hashes were independently checked. Fresh full suite: **494 passed**. This is measured headless analysis, not designer issue acceptance or a new GUI compression option.
