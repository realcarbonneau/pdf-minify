# Integrated compression — complete-file size matrix

Designer §222, 2026-10-15 (America/New_York); TODO §225.

## Metric and measured scope

The objective is the size in bytes of the final complete saved PDF. Native
streams, encoded images, palettes/masks, font subsets, resources, metadata,
extension declarations and container overhead all count. Encoding time and
payload-only savings are not comparison metrics.

The previous studies did **not** measure the full cross-product: the
[bitmap study](IMAGE_STREAM_COMPRESSION.md) fixed native compression to
classic Flate, and the [native study](NATIVE_STREAM_COMPRESSION.md) preserved
original image bytes. Their complete-file numbers are valid for those
specific outputs, but cannot be combined arithmetically into new results.

Measured **2026-10-15**: **549 actual complete PDFs across 51 explicit
recipes and 11 complete inputs; 1,980 candidate pages**. The paired bitmap
matrix is 22 recipes × seven image variants × three native policies = 462
files. The other-production matrix adds 29 recipes × three native policies
= 87 files. There are zero benchmark timing fields. Every published cell
matches the actual saved file size/hash, not a component estimate.

This is the primary analysis entry point. The component studies retain
their methods and prior evidence as supporting docs. The 11 inputs are
eight repository PDFs plus the flat/noise and native-font fixtures; repeated
recipe variants are not independent source documents. Synthetic 5/16-color
rows have five actual colors and intentionally repeat the same prepared pixels.

## How to read the integrated matrix

Every cell is the final complete PDF size in bytes. **Bold** marks the
smallest complete-file result in the same row, including ties. Different
rows can have different retained fidelity; do not treat a BW/low-palette
result as lossless to a full-color source just because its bytes are smaller.

In the paired-bitmap matrix, a column is **image / native**, never nested
compression: `Z+/B`, for example, is a PNG-predicted Zopfli-Flate bitmap
with Brotli native streams.

- `F`: classic zlib-9 Flate, retained as the reference encoder.
- `Z`: full-workload Zopfli-Flate, with the same FlateDecode reader format.
- `B`: Brotli level 11, requiring a supporting reader when used in either layer.
- `J`: lossless JBIG2 BW, or colored JBIG2 stencils for an indexed-color row.
- `+`: reversible PNG row prediction before the image compressor. The native
  policy is still the separate code after `/`.

The other-production-recipes matrix fixes the image recipe in its row label;
its `F`, `Z`, `B` columns name the native policy only. JPEG uses quality 50
at a 150dpi target; JPX uses rate 192 (lossy) or explicit lossless encoding
at that target. The recipe API retains the historical key `dpi_cap`, but
composition uses the final target DPI, not a second post-filter resize.
JPX lossless preserves that prepared canvas, not the unresampled source.
Preserve-images does not resize or alter bitmap samples; its 150dpi value
is only the validation-render scale. All pages of each original input are
included, not page subsets or image-only files.

Coverage is all three currently selectable native policies across the seven
distinct packed-image/predictor variants, plus the explicitly listed JPEG,
JPEG2000 and preserve-images cases. It is not every possible quality/DPI/
threshold value or every example PDF in the repository. Color FFPR and an
automatic plain-storage residual-stream policy remain unimplemented proposals,
not measured product choices. LZW/RunLength and low-effort encoder controls
in the earlier native study are not current selectable combinations.

## Final complete-PDF sizes (bytes)

All 549 outputs below are measured complete-file sizes, not estimates.

### Paired bitmap × native policies

| Complete input / explicit recipe | F/F | F/Z | F/B | F+/F | F+/Z | F+/B | Z/F | Z/Z | Z/B | Z+/F | Z+/Z | Z+/B | B/F | B/Z | B/B | B+/F | B+/Z | B+/B | J/F | J/Z | J/B |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| images / 150dpi / 5 colors | 19,598 | 19,440 | 19,600 | 20,912 | 20,754 | 20,914 | 18,284 | 18,126 | 18,286 | 19,118 | 18,960 | 19,120 | 15,100 | 14,942 | 14,936 | 17,551 | 17,393 | 17,387 | 13,320 | **13,163** | 13,319 |
| images / 150dpi / 16 colors | 29,039 | 28,881 | 29,041 | 31,815 | 31,657 | 31,817 | 26,986 | 26,828 | 26,988 | 28,696 | 28,538 | 28,698 | 22,488 | 22,330 | **22,324** | 26,874 | 26,716 | 26,710 | 24,814 | 24,652 | 24,783 |
| images / 150dpi / 64 colors | 34,550 | 34,392 | 34,552 | 46,550 | 46,392 | 46,552 | 31,108 | 30,950 | 31,110 | 40,785 | 40,627 | 40,787 | 27,259 | 27,101 | **27,095** | 38,609 | 38,451 | 38,445 | 46,557 | 46,352 | 46,430 |
| GAN / 150dpi / 5 colors | 344,069 | 333,328 | 325,770 | 347,428 | 336,687 | 329,129 | 339,419 | 328,678 | 321,120 | 341,833 | 331,092 | 323,534 | 330,312 | 319,571 | **311,847** | 338,060 | 327,319 | 319,595 | 338,703 | 327,961 | 320,388 |
| GAN / 150dpi / 16 colors | 378,991 | 368,250 | 360,692 | 388,336 | 377,595 | 370,037 | 373,255 | 362,514 | 354,956 | 378,806 | 368,065 | 360,507 | 361,219 | 350,478 | **342,754** | 373,583 | 362,842 | 355,118 | 389,741 | 378,989 | 371,366 |
| GAN / 150dpi / 64 colors | 429,411 | 418,670 | 411,112 | 459,529 | 448,788 | 441,230 | 419,203 | 408,462 | 400,904 | 441,977 | 431,236 | 423,678 | 405,276 | 394,535 | **386,811** | 433,448 | 422,707 | 414,983 | 478,968 | 468,130 | 460,401 |
| images / 300dpi / 5 colors | 32,293 | 32,136 | 32,298 | 40,180 | 40,023 | 40,185 | 29,509 | 29,352 | 29,514 | 35,127 | 34,970 | 35,132 | 23,741 | 23,584 | 23,580 | 30,686 | 30,529 | 30,525 | 18,543 | **18,387** | 18,545 |
| images / 300dpi / 16 colors | 50,951 | 50,794 | 50,956 | 60,783 | 60,626 | 60,788 | 45,315 | 45,158 | 45,320 | 51,758 | 51,601 | 51,763 | 37,026 | 36,869 | 36,865 | 47,564 | 47,407 | 47,403 | 35,412 | **35,251** | 35,384 |
| synthetic-flat / 150dpi / 5 colors | 3,103 | 3,103 | 3,265 | 3,776 | 3,776 | 3,938 | 2,788 | 2,788 | 2,950 | 3,578 | 3,578 | 3,740 | 2,347 | 2,347 | **2,343** | 2,874 | 2,874 | 2,870 | 3,415 | 3,413 | 3,567 |
| synthetic-flat / 150dpi / 16 colors | 3,103 | 3,103 | 3,265 | 3,776 | 3,776 | 3,938 | 2,788 | 2,788 | 2,950 | 3,578 | 3,578 | 3,740 | 2,347 | 2,347 | **2,343** | 2,874 | 2,874 | 2,870 | 3,415 | 3,413 | 3,567 |
| synthetic-noise / 150dpi / 5 colors | 115,567 | 115,567 | 115,725 | 152,625 | 152,625 | 152,783 | 108,454 | 108,454 | 108,612 | 151,581 | 151,581 | 151,739 | 107,798 | 107,798 | **107,790** | 149,562 | 149,562 | 149,554 | 145,977 | 145,975 | 146,125 |
| synthetic-noise / 150dpi / 16 colors | 115,567 | 115,567 | 115,725 | 152,625 | 152,625 | 152,783 | 108,454 | 108,454 | 108,612 | 151,581 | 151,581 | 151,739 | 107,798 | 107,798 | **107,790** | 149,562 | 149,562 | 149,554 | 145,977 | 145,975 | 146,125 |
| images / bw-images / 300dpi / otsu | 22,605 | 22,448 | 22,610 | 24,096 | 23,939 | 24,101 | 21,051 | 20,894 | 21,056 | 21,637 | 21,480 | 21,642 | 15,158 | 15,001 | 14,997 | 18,342 | 18,185 | 18,181 | 10,133 | **9,976** | 10,138 |
| images / bw-images / 300dpi / T=180 | 23,451 | 23,294 | 23,456 | 24,888 | 24,731 | 24,893 | 21,853 | 21,696 | 21,858 | 22,344 | 22,187 | 22,349 | 15,852 | 15,695 | 15,691 | 19,230 | 19,073 | 19,069 | 10,410 | **10,252** | 10,415 |
| images / bw-images / 300dpi / T=210 | 26,843 | 26,686 | 26,848 | 28,550 | 28,393 | 28,555 | 24,670 | 24,513 | 24,675 | 25,452 | 25,295 | 25,457 | 18,289 | 18,132 | 18,128 | 22,644 | 22,487 | 22,483 | 11,244 | **11,087** | 11,249 |
| GAN / bw-images / 300dpi / otsu | 337,441 | 326,700 | 319,142 | 338,931 | 328,190 | 320,632 | 334,900 | 324,159 | 316,601 | 335,319 | 324,578 | 317,020 | 324,046 | 313,305 | 305,581 | 328,099 | 317,358 | 309,634 | 319,797 | 309,056 | **301,498** |
| jfk-poor-copies / bw-images / 300dpi / otsu | 709,790 | 709,790 | 709,971 | 818,583 | 818,583 | 818,764 | 634,911 | 634,911 | 635,092 | 740,164 | 740,164 | 740,345 | 581,140 | 581,140 | 581,155 | 706,763 | 706,763 | 706,778 | **350,007** | **350,007** | 350,188 |
| naca-formulas / bw-images / 300dpi / otsu | 440,623 | 439,997 | 438,572 | 443,514 | 442,888 | 441,463 | 402,184 | 401,558 | 400,133 | 390,412 | 389,786 | 388,361 | 299,426 | 298,800 | 297,209 | 366,834 | 366,208 | 364,617 | 198,920 | 198,294 | **196,869** |
| images / bw-ffpr / 300dpi / otsu | 17,976 | 17,976 | 18,145 | 19,777 | 19,777 | 19,946 | 16,136 | 16,136 | 16,305 | 16,930 | 16,930 | 17,099 | 10,003 | 10,003 | 10,006 | 13,903 | 13,903 | 13,906 | **4,095** | **4,095** | 4,264 |
| GAN / bw-ffpr / 300dpi / otsu | 786,664 | 786,664 | 786,833 | 776,860 | 776,860 | 777,029 | 732,409 | 732,409 | 732,578 | 693,876 | 693,876 | 694,045 | 563,226 | 563,226 | 563,229 | 624,740 | 624,740 | 624,743 | **321,295** | **321,295** | 321,464 |
| synthetic-flat / bw-images / 300dpi / otsu | 3,479 | 3,479 | 3,641 | 4,489 | 4,489 | 4,651 | 3,256 | 3,256 | 3,418 | 4,269 | 4,269 | 4,431 | 2,555 | 2,555 | 2,551 | 3,399 | 3,399 | 3,395 | **2,094** | **2,094** | 2,256 |
| synthetic-noise / bw-images / 300dpi / otsu | 102,092 | 102,092 | 102,250 | 98,119 | 98,119 | 98,277 | 91,217 | 91,217 | 91,375 | 86,029 | 86,029 | 86,187 | 83,432 | 83,432 | 83,424 | 81,018 | 81,018 | 81,010 | **63,075** | **63,075** | 63,233 |

### Other production image recipes × native policies

| Complete input / explicit recipe | F | Z | B |
|---|---:|---:|---:|
| deed-brevard / preserve-images | **143,121** | **143,121** | 143,311 |
| form-941-2026 / preserve-images | 872,512 | 854,321 | **776,197** |
| form-fw9 / preserve-images | 188,447 | 187,455 | **182,638** |
| images / jpeg-q50 | 47,429 | **47,272** | 47,434 |
| images / jpx-lossless | 227,636 | **227,479** | 227,641 |
| images / jpx-r192 | 40,961 | **40,804** | 40,966 |
| images / preserve-images | 1,493,125 | **1,492,980** | 1,493,126 |
| models-nasa-kepler / preserve-images | 2,188,983 | 2,016,866 | **1,766,110** |
| native-text-vector-font / preserve-images | 56,039 | 54,114 | **53,258** |
| GAN / jpeg-q50 | 400,473 | 389,732 | **382,174** |
| GAN / jpx-lossless | 929,954 | 919,213 | **911,655** |
| GAN / jpx-r192 | 377,076 | 366,335 | **358,777** |
| GAN / preserve-images | 502,235 | 491,510 | **483,963** |
| jfk-poor-copies / jpeg-q50 | **1,413,540** | **1,413,540** | 1,413,721 |
| jfk-poor-copies / jpx-lossless | **10,813,283** | **10,813,283** | 10,813,464 |
| jfk-poor-copies / jpx-r192 | **268,346** | **268,346** | 268,527 |
| jfk-poor-copies / preserve-images | 341,697 | **341,696** | 341,881 |
| naca-formulas / jpeg-q50 | 939,789 | 939,163 | **937,738** |
| naca-formulas / jpx-lossless | 6,383,501 | 6,382,875 | **6,381,450** |
| naca-formulas / jpx-r192 | 227,851 | 227,225 | **225,800** |
| naca-formulas / preserve-images | 252,142 | 251,548 | **250,059** |
| synthetic-flat / jpeg-q50 | **13,614** | **13,614** | 13,776 |
| synthetic-flat / jpx-lossless | **41,973** | **41,973** | 42,135 |
| synthetic-flat / jpx-r192 | **7,788** | **7,788** | 7,950 |
| synthetic-flat / preserve-images | 1,083,763 | **1,083,640** | 1,083,719 |
| synthetic-noise / jpeg-q50 | **173,421** | **173,421** | 173,579 |
| synthetic-noise / jpx-lossless | **1,242,582** | **1,242,582** | 1,242,740 |
| synthetic-noise / jpx-r192 | **7,656** | **7,656** | 7,814 |
| synthetic-noise / preserve-images | 1,083,763 | **1,083,640** | 1,083,721 |

## Integrated conclusions

- Palette rows have two winning combinations: packed Brotli images + Brotli
  native streams win nine of twelve; colored JBIG2 + Zopfli-native win three.
  Those are whole-file results, not separate image/native payload rankings.
- BW JBIG2 wins all ten BW rows, but the winning native policy varies:
  Brotli on the GAN/NACA image-layer cases, Zopfli on the other eight, with
  classic-Flate ties in five of those eight. There is no one mandatory native
  compressor that gives the smallest file on every input.
- FFPR + JBIG2 leaves little native data: images.pdf is 4,095 B with either
  Flate or Zopfli-native, versus 4,264 B with Brotli-native. The GAN FFPR file
  is 321,295 B versus 321,464 B respectively. Declaration/filter overhead
  counts, so a newer decoder does not automatically produce a smaller file.
- No predicted variant wins a whole paired row here, but the smaller
  same-encoder BW prediction results remain visible. JPEG/JPX rows use their
  declared settings and are not a claim of matched fidelity with each other,
  reduced palettes, BW or the original source.

## Measurement contract

- Cross all seven distinct prepared bitmap variants (plain and PNG-predicted
  classic Flate, full Zopfli and Brotli, plus BW/colored JBIG2) with native
  classic Flate, Zopfli-Flate and Brotli. Reuse each existing validated
  prepared image PDF, then use the shared final saver for **every** native
  policy, including the classic-Flate control.
- Freeze the prepared font programs too. Re-subsetting an already-subset
  TrueType program can rewrite its checksum bytes and alter compressed size
  without changing glyphs. The shared saver has an explicit `subset_fonts`
  flag, defaulting to the unchanged product behavior; this study passes
  `False` only for already-prepared artifacts. Exact native-byte checks stay
  strict. The first rejected run exposed this eight-byte font difference;
  that failed output is not a matrix result. Frozen production preparations
  can be explicitly imported with source/artifact hashes and their original
  implementation provenance, rather than recompressed or silently resumed
  across changed code.
- Also measure explicit production JPEG, JPEG2000 lossy/lossless and
  preserve-images recipes against all three native policies. Declare DPI,
  JPEG quality/JPX rate and fidelity; these are not equal-pixel rivals to BW
  or reduced palettes. The current six product image choices are represented
  by these families and the bitmap matrix.
- Keep FFPR on/off separate. Only BW FFPR is implemented. Unsupported color
  FFPR is unavailable, not a zero-size result or an inferred measurement.
- Measure the entire input document and actual final file size. Preserve
  deterministic fixed-width PDF identifier framing for all paired variants.
  Reopening/resaving an artifact must not alter encoded image bytes, decoded
  native data, text, geometry, annotations/links or any actual page pixels.
- Validate every completed output and retain its actual PDF, hash and exact
  byte count. Unknown filters, failed decodes and new warnings are failures,
  never small-file successes. Keep source-native warnings visible separately.
  Resume only verified unchanged input/environment/artifact combinations.
- Use a sequential, thread-limited, low-priority headless run. Collect no
  benchmark timing fields. Do not change product defaults or launch the GUI.
- Bold the smallest complete-file value per comparable row, including ties.
  Report all measured combinations, not only favorable examples or winners.

## Reader support

Classic Flate and Zopfli-Flate use the same FlateDecode format. Brotli in
either the image or native layer requires a supporting reader and extension
declaration; a different image codec does not remove that requirement.
Installed-reader evidence and limitations remain in
[NATIVE_STREAM_COMPRESSION.md](NATIVE_STREAM_COMPRESSION.md#correctness-and-compatibility).
Size winners are not all-reader or cross-platform certificates.

## Artifacts, reproduction and verification

All 549 PDFs and per-case/combined JSON evidence are retained in
`.tmp/integrated-compression/size-20261015-v2/`. The Markdown tables above
contain all 549 complete-file measurements.

Run from the repository root after preparing the bitmap corpus described in
[IMAGE_STREAM_COMPRESSION.md](IMAGE_STREAM_COMPRESSION.md#reproduction-and-corpus):

```sh
nice -n 10 ./.venv/bin/python tools/bench_integrated_compression.py --label <new-label>
./.venv/bin/python -m pytest tests/test_integrated_compression_bench.py -q
```

The measured run explicitly reused frozen production image preparations
from `.tmp/integrated-compression/size-20261015/prepared/` with
`--prepared-production`; their original implementation/source/artifact hashes
are recorded alongside the current matrix implementation. The extra native
fixture is the existing four-page fixture from the earlier native study and
is included when present. Use the retained preparations for exact byte-count
reproduction; fresh preparations can change font checksum/identifier bytes.
`--resume` requires unchanged inputs/environment/output hashes, revalidates
every existing output and does not re-encode valid completed cells.

Python 3.13.5 and PyMuPDF/MuPDF 1.28.2; no dependencies installed. Every output
preserves its frozen decoded native streams, encoded/decoded image data,
page geometry/content, user metadata and attachments, with all-page no-AA
pixel equality at 72dpi and recipe DPI. Existing source-native warnings are
retained separately; new output-only warnings fail verification. An
independent audit rechecked every saved size/hash and whole-document page
count, every published Markdown value, and all tied bold minima.

Verification: **14 focused tests; 474 passed in the fresh full suite**.
This is measured headless analysis, not designer acceptance or a new GUI
codec/default. Ordinary application font-subsetting behavior remains unchanged.
