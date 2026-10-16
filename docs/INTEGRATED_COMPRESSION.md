# Integrated compression — complete-PDF sizes at 300 DPI

Designer §§210–214/220–227; TODO §§226–232. This is the primary integrated
size analysis, replacing the earlier mixed-DPI overview. Measurements and
verification: 2026-10-16 (America/New_York).

## Scope and five representative classes

**Realistic algorithm combinations are rows; five complete repository PDFs
are columns. Every number is the final saved PDF size in bytes.** Fonts,
native drawing streams, images, masks, palettes and container overhead are
included. No compute-time rankings, component-size estimates or CSV delivery.

| Representative class | Complete PDF | Pages | Original bytes |
|---|---|---:|---:|
| Native text/vectors | [form-fw9.pdf](../examples/form-fw9.pdf) | 6 | 140,815 |
| BW scan | [scan-jfk-poor-copies.pdf](../examples/scan-jfk-poor-copies.pdf) | 8 | 349,667 |
| Color photos | [news-crater-lake-2026.pdf](../examples/news-crater-lake-2026.pdf) | 8 | 5,550,048 |
| Flat-color artwork | [images.pdf](../examples/images.pdf) | 1 | 1,494,439 |
| Mixed text/images | [paper-arxiv-1406.2661.pdf](../examples/paper-arxiv-1406.2661.pdf) | 9 | 530,482 |

These classes distinguish native instructions/fonts, scanned text pixels,
photography, graphic/palette pixels and mixed content. They are a practical
basis, not an exhaustive taxonomy. Noise, existing encoding, masks, overlap
and embedded resources cut across them; focused tables follow the overview.
The photo example is an eight-page newspaper, not the logos in `images.pdf`.

## Reading the results

- All transformed bitmap canvases use **300 DPI**, including color FFPR and
  every focused scenario. Preserve-images controls are **unresampled**.
- **Zopfli-Flate** uses standard FlateDecode. **Classic Flate** is a labeled
  comparison reference, not an encoder-speed recommendation.
- Packed BW/indexed images and native streams use the **same general
  compressor**. Mixed general-compressor pairings are excluded. Specialized
  JPEG/JPEG2000/JBIG2 retain meaningful native Zopfli/Brotli alternatives.
- **PNG prediction** is reversible row prediction before the same image
  compressor, not a second image/codec. Plain and predicted rows stay together.
- **Bold** is the minimum within the **same PDF column and recipe/fidelity
  group**, including ties. Do not rank BW against color or native preservation
  against FFPR as equivalent fidelity. A group with one tested combination
  has one bold value; that is not proof of a universally optimal encoder.
- **Brotli requires a verified supporting reader** regardless of whether it
  compresses native or image streams. A size win is not reader certification.
- **—** means an image-only recipe is inapplicable to the image-free W-9.
  Its native-only control and whole-page FFPR remain applicable.

### Fixed recipes and fidelity

Native-preserving rows compose original bitmap artwork into one canvas and
keep native text/vectors above it under the established layer policy. FFPR
flattens the **entire original page** in full color, resizes once, then applies
the chosen BW/palette/codec transform. FFPR loses text selectability and native
vector precision; JPEG FFPR also makes the text lossy. Native modes preserve
the original document catalog and semantic tags. The current FFPR writer
creates new raster pages, not an accessible/native-preserving equivalent;
its smaller metadata/font burden is another reason to keep it a separate group.

Indexed uses **five total colors** in the overview; focused cases use 5/16/64.
BW uses **Otsu**, except the explicitly labeled Simple thresholds. JPEG uses
**quality 50**; JPEG2000 uses **rate 192 (lossy)** or explicit **lossless**.
JPEG q50 and JPEG2000 r192 are **not quality-matched**. Lossless encoding
preserves the prepared 300-DPI raster, not the original unresampled PDF.
Common DPI does not make these different transformations equal fidelity.
Palette/BW processing does not recolor the native artwork retained with FFPR OFF.

The lossy JPEG2000 adapter uses Pillow's `quality_mode="rates"`: r192
targets an approximate size-reduction ratio, not constant perceptual quality.
Putting text/vectors into FFPR spends that same raster budget on more content;
it is not a quality-matched comparison with keeping them native. See
[Pillow's JPEG2000 settings](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg-2000).
These rows measure the current fixed encoder settings, not an exhaustive
JPEG2000 parameter search or a claim of globally optimal format tuning.

Specialized-codec FFPR rows use one measured Zopfli-Flate residual-stream
choice; redundant native-policy permutations are omitted. This is not an
implemented automatic residual-compressor selector. Color FFPR and uniform
built-in defaults are implemented under §§224/225. §226 migrates all existing
saved/custom raster recipes once to 300 DPI, preserving UUIDs and other
settings; later deliberate DPI edits remain. Shared general-compressor image
controls and removal of the legacy native Flate menu remain separate work
(TODO §217); experimental bitmap encodings here do not silently migrate recipes.

## Unresampled reference controls

These controls preserve original image encodings without resampling and
vary native-stream compression. Original source sizes are listed above;
these are references, not BW, indexed-color or full-color raster transforms.

| Algorithm combination | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images |
|---|---:|---:|---:|---:|---:|
| Preserve images + Classic Flate (reference) native | 188,447 | 341,697 | 4,641,959 | 1,493,125 | 502,235 |
| Preserve images + Zopfli-Flate native | 187,455 | **341,696** | 4,574,656 | **1,492,980** | 491,510 |
| Preserve images + Brotli native | **182,638** | 341,881 | **4,472,657** | 1,493,126 | **483,963** |

## Overview — final complete-file bytes

The same five PDF columns are repeated in three output groups: BW, indexed
color, then full color (§227). Native-retaining rows precede FFPR rows within
each group. Bold minima remain separate for native/FFPR and lossy/lossless
fidelity; grouping does not change any measured bytes or establish a
universal codec winner. All classic-Flate and plain/predicted comparisons
are retained.

### 1. Black and white (BW)

| Algorithm combination | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images |
|---|---:|---:|---:|---:|---:|
| BW; keep native + JBIG2 + Zopfli-Flate native | — | **354,089** | 1,769,572 | **9,826** | 308,200 |
| BW; keep native + JBIG2 + Brotli native | — | 354,346 | **1,668,076** | 9,980 | **300,637** |
| BW; keep native + Classic Flate (reference) | — | 713,873 | 2,211,586 | 22,466 | 336,563 |
| BW; keep native + Classic Flate (reference) + PNG prediction | — | 822,666 | 2,260,390 | 23,957 | 338,053 |
| BW; keep native + Zopfli-Flate | — | 638,993 | 2,067,873 | 20,744 | 323,303 |
| BW; keep native + Zopfli-Flate + PNG prediction | — | 744,246 | 2,078,249 | 21,330 | 323,722 |
| BW; keep native + Brotli | — | 585,313 | 1,824,470 | 14,839 | 304,720 |
| BW; keep native + Brotli + PNG prediction | — | 710,936 | 1,945,111 | 18,023 | 308,773 |
| BW FFPR + JBIG2; optimized residual streams | **297,872** | **350,190** | **1,254,079** | **3,876** | **316,049** |
| BW FFPR + Classic Flate (reference) | 733,677 | 709,973 | 2,714,039 | 17,679 | 800,867 |
| BW FFPR + Classic Flate (reference) + PNG prediction | 722,777 | 818,766 | 2,689,224 | 19,271 | 777,268 |
| BW FFPR + Zopfli-Flate | 688,732 | 635,094 | 2,511,775 | 15,830 | 743,693 |
| BW FFPR + Zopfli-Flate + PNG prediction | 649,984 | 740,347 | 2,388,759 | 16,489 | 701,446 |
| BW FFPR + Brotli | 531,399 | 581,338 | 1,970,142 | 9,655 | 574,796 |
| BW FFPR + Brotli + PNG prediction | 578,653 | 706,961 | 2,288,813 | 13,482 | 625,834 |

### 2. Indexed color — low palettes

Five-color bitmap canvases, with native artwork retained first and indexed
FFPR below. Full-page rasterization does not make indexed output full color.

| Algorithm combination | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images |
|---|---:|---:|---:|---:|---:|
| Indexed 5 colors + colored JBIG2 + Zopfli-Flate native | — | **1,099,894** | 4,419,818 | **17,669** | 345,678 |
| Indexed 5 colors + colored JBIG2 + Brotli native | — | 1,100,131 | 4,318,364 | 17,816 | 338,105 |
| Indexed 5 colors + Classic Flate (reference) | — | 1,341,839 | 4,469,850 | 31,951 | 378,057 |
| Indexed 5 colors + Classic Flate (reference) + PNG prediction | — | 1,879,772 | 5,065,305 | 39,838 | 390,403 |
| Indexed 5 colors + Zopfli-Flate | — | 1,174,973 | 4,098,298 | 28,999 | 359,021 |
| Indexed 5 colors + Zopfli-Flate + PNG prediction | — | 1,684,784 | 4,518,574 | 34,617 | 367,014 |
| Indexed 5 colors + Brotli | — | 1,192,432 | **3,523,561** | 23,219 | **332,124** |
| Indexed 5 colors + Brotli + PNG prediction | — | 1,625,012 | 4,283,194 | 30,164 | 347,017 |
| Color FFPR; indexed 5 colors + colored JBIG2; optimized residual streams | **299,497** | **1,095,765** | 4,488,350 | **12,417** | **337,274** |
| Color FFPR; indexed 5 colors + Classic Flate (reference) | 733,827 | 1,337,939 | 5,778,786 | 32,907 | 876,609 |
| Color FFPR; indexed 5 colors + Classic Flate (reference) + PNG prediction | 722,927 | 1,875,872 | 6,763,541 | 41,339 | 860,595 |
| Color FFPR; indexed 5 colors + Zopfli-Flate | 688,882 | 1,171,074 | 5,208,697 | 28,079 | 783,305 |
| Color FFPR; indexed 5 colors + Zopfli-Flate + PNG prediction | 650,134 | 1,680,885 | 6,024,506 | 34,163 | 754,689 |
| Color FFPR; indexed 5 colors + Brotli | 531,549 | 1,188,457 | **4,380,676** | 21,438 | 602,501 |
| Color FFPR; indexed 5 colors + Brotli + PNG prediction | 578,803 | 1,621,037 | 5,729,329 | 31,336 | 668,343 |

### 3. Full color

JPEG q50, JPEG2000 lossy r192 and JPEG2000 lossless remain distinct fidelity
groups, with native-retaining rows first and full-color FFPR below.

| Algorithm combination | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images |
|---|---:|---:|---:|---:|---:|
| JPEG q50 + Zopfli-Flate native | — | **3,944,595** | 6,249,832 | **116,165** | 551,040 |
| JPEG q50 + Brotli native | — | 3,944,852 | **6,148,336** | 116,319 | **543,477** |
| JPEG2000 lossy r192 + Zopfli-Flate native | — | **1,053,173** | 3,626,722 | **139,048** | 538,500 |
| JPEG2000 lossy r192 + Brotli native | — | 1,053,430 | **3,525,226** | 139,202 | **530,937** |
| JPEG2000 lossless + Zopfli-Flate native | — | **26,637,476** | 55,276,886 | **569,743** | 1,816,596 |
| JPEG2000 lossless + Brotli native | — | 26,637,733 | **55,175,390** | 569,897 | **1,809,033** |
| Color FFPR + JPEG q50; optimized residual streams | **5,674,560** | **3,940,696** | **16,386,640** | **119,537** | **5,695,628** |
| Color FFPR + JPEG2000 lossy r192; optimized residual streams | **790,654** | **1,049,274** | **2,321,850** | **132,375** | **1,186,046** |
| Color FFPR + JPEG2000 lossless; optimized residual streams | **26,977,014** | **26,633,577** | **130,483,529** | **631,823** | **27,091,577** |

An encoded output can exceed the untouched original. The original sizes above
remain the baseline; the smallest tested encoding within a group is not
automatically an improvement over that original.

## Focused scenarios

Every cell below is another complete saved PDF or an explicitly reused cell
from the overview. Only the settings named in the columns change. All
transformed cases remain at 300 DPI; lower-DPI variations are not repeated.

### Color photography — native preservation and full-page color

All eight Crater Lake pages. Preserve-images retains original image bytes;
the other rows target 300 DPI. Native and FFPR rows remain separate fidelity
groups. These are full-color cases, not five-color or BW photo approximations.

| Algorithm combination | Color photos |
|---|---:|
| Preserve images + Classic Flate (reference) native | 4,641,959 |
| Preserve images + Zopfli-Flate native | 4,574,656 |
| Preserve images + Brotli native | **4,472,657** |
| JPEG q50 + Zopfli-Flate native | 6,249,832 |
| JPEG q50 + Brotli native | **6,148,336** |
| JPEG2000 lossy r192 + Zopfli-Flate native | 3,626,722 |
| JPEG2000 lossy r192 + Brotli native | **3,525,226** |
| JPEG2000 lossless + Zopfli-Flate native | 55,276,886 |
| JPEG2000 lossless + Brotli native | **55,175,390** |
| Color FFPR + JPEG q50; optimized residual streams | **16,386,640** |
| Color FFPR + JPEG2000 lossy r192; optimized residual streams | **2,321,850** |
| Color FFPR + JPEG2000 lossless; optimized residual streams | **130,483,529** |

### Logos/artwork — palette count

The same complete `images.pdf` at 300 DPI with native artwork retained.
Within each column the competing lossless encoders preserve identical
prepared pixels. Changing the palette is not an equal-fidelity contest.

| Algorithm combination | 5 colors | 16 colors | 64 colors |
|---|---:|---:|---:|
| Indexed + Classic Flate (reference) | 31,951 | 50,609 | 73,596 |
| Indexed + Classic Flate (reference) + PNG prediction | 39,838 | 60,441 | 104,394 |
| Indexed + Zopfli-Flate | 28,999 | 44,805 | 64,543 |
| Indexed + Zopfli-Flate + PNG prediction | 34,617 | 51,248 | 88,418 |
| Indexed + Brotli | 23,219 | 36,504 | **54,124** |
| Indexed + Brotli + PNG prediction | 30,164 | 47,042 | 79,422 |
| Indexed + colored JBIG2 + Zopfli-Flate native | **17,669** | **34,539** | 73,655 |
| Indexed + colored JBIG2 + Brotli native | 17,816 | 34,665 | 73,704 |

### Mixed text/images — palette count

All nine GAN-paper pages at 300 DPI. Text, vectors and fonts remain native;
only the composed bitmap layer is palette-reduced.

| Algorithm combination | 5 colors | 16 colors | 64 colors |
|---|---:|---:|---:|
| Indexed + Classic Flate (reference) | 378,057 | 483,604 | 617,887 |
| Indexed + Classic Flate (reference) + PNG prediction | 390,403 | 510,466 | 693,096 |
| Indexed + Zopfli-Flate | 359,021 | 458,426 | 580,617 |
| Indexed + Zopfli-Flate + PNG prediction | 367,014 | 477,373 | 640,904 |
| Indexed + Brotli | **332,124** | **416,450** | **514,926** |
| Indexed + Brotli + PNG prediction | 347,017 | 455,462 | 606,819 |
| Indexed + colored JBIG2 + Zopfli-Flate native | 345,678 | 466,140 | 645,262 |
| Indexed + colored JBIG2 + Brotli native | 338,105 | 458,543 | 637,531 |

### Scanned BW text — different source material

JFK poor copies (eight pages) and NACA formulas (seven pages), 300 DPI/Otsu,
with native artwork retained if present. Degraded scans and mathematical
print are distinct stress cases, not interchangeable evidence.

| Algorithm combination | JFK poor copies | NACA formulas |
|---|---:|---:|
| BW; keep native + Classic Flate (reference) | 713,873 | 439,941 |
| BW; keep native + Classic Flate (reference) + PNG prediction | 822,666 | 442,832 |
| BW; keep native + Zopfli-Flate | 638,993 | 400,877 |
| BW; keep native + Zopfli-Flate + PNG prediction | 744,246 | 389,105 |
| BW; keep native + Brotli | 585,313 | 296,438 |
| BW; keep native + Brotli + PNG prediction | 710,936 | 363,846 |
| BW; keep native + JBIG2 + Zopfli-Flate native | **354,089** | 197,613 |
| BW; keep native + JBIG2 + Brotli native | 354,346 | **196,098** |

### Threshold sensitivity — three explicit BW transforms

The same complete `images.pdf`, 300 DPI, native artwork retained. Otsu and
Simple T180/T210 produce different pixels. Compare encoders within each
column, not the thresholds as though their output were visually identical.

| Algorithm combination | Otsu | Simple T180 | Simple T210 |
|---|---:|---:|---:|
| BW; keep native + Classic Flate (reference) | 22,466 | 23,312 | 26,704 |
| BW; keep native + Classic Flate (reference) + PNG prediction | 23,957 | 24,749 | 28,411 |
| BW; keep native + Zopfli-Flate | 20,744 | 21,546 | 24,363 |
| BW; keep native + Zopfli-Flate + PNG prediction | 21,330 | 22,037 | 25,145 |
| BW; keep native + Brotli | 14,839 | 15,533 | 17,970 |
| BW; keep native + Brotli + PNG prediction | 18,023 | 18,911 | 22,325 |
| BW; keep native + JBIG2 + Zopfli-Flate native | **9,826** | **10,102** | **10,937** |
| BW; keep native + JBIG2 + Brotli native | 9,980 | 10,256 | 11,091 |

### Native-heavy files — fonts, drawings and container overhead

Preserve original encoded images without resampling. The W-9, Form 941 and
NASA Kepler paper expose different native-content burdens. These are whole
repository PDFs, not extracted pages or combined component estimates.

| Algorithm combination | W-9 / 6 pages | Form 941 / 3 pages | Kepler / 12 pages |
|---|---:|---:|---:|
| Preserve images + Classic Flate (reference) native | 188,447 | 872,512 | 2,188,983 |
| Preserve images + Zopfli-Flate native | 187,455 | 854,321 | 2,016,866 |
| Preserve images + Brotli native | **182,638** | **776,197** | **1,766,110** |

## What the measurements establish

- Five-color artwork: colored JBIG2 + Zopfli-native is **17,669 B**, versus **23,219 B** for shared Brotli without prediction. The complete mixed-paper counterparts are **345,678 B** and **332,124 B**. Representation/content changes the comparison.
- On the eight-page JFK BW scan, JBIG2 + Zopfli-native is **354,089 B**, versus **585,313 B** for shared Brotli at identical prepared BW pixels. Preserve-images remains a different, unresampled baseline.
- Crater Lake's native-preserving JPEG q50 + Zopfli-native is **6,249,832 B**; its full-page JPEG counterpart is **16,386,640 B**. Both target 300 DPI, but FFPR rasterizes text/vectors: their sizes are not equal-fidelity codec scores.
- Across **75** same-input/same-compressor prediction pairs, predicted is smaller in **11**, tied in **0**, and larger in **64**. Each compares complete `+ PNG prediction` PDF bytes with that encoder's plain counterpart. Where smaller, prediction saves **0.91%–5.68%** of its own plain counterpart’s complete bytes. Neither universal growth nor universal savings is assumed.
- The unresampled W-9 original is **140,815 B**; even its smallest tested preserve-images rewrite is **182,638 B**. Being the smallest tested rewrite does not mean it beats the untouched source.
- No single PDF, generic algorithm ranking or minimum across unlike fidelity/reader groups establishes a project-wide winner. Retain meaningful measured outcomes and reader requirements.

## Preparation defects and verification

The old **PREP FAILED** meant the shared input-to-prepared-PDF stage failed
validation; it did not mean every dependent compressor independently failed.
Invalid candidates never receive a size or minimum ranking. The current
measurements are rebuilt after the shared production repairs, not estimates
inserted into those old failed cells.

- **B108:** nested page Forms clipped colored JBIG2 at fractional page edges.
  Stencils now paint directly with the same placement geometry as Indexed.
- **B109:** removing an image orphaned its whitespace ActualText tag. Repair
  only that disconnected property using MuPDF's parser, retaining native
  text-bearing replacements, MCIDs, other metadata and clipping/state.
- **B110:** an uninitialized native `no_update` flag skipped filter write-back,
  leaving original photos. Initialize the complete filter policy explicitly;
  retain genuine native vector soft masks, not the replaced source photos.
- **B111:** content sanitization deferred `0 Tr` before a Form call, letting
  nested visible labels inherit an earlier invisible mode. Native foreground
  now preserves original operators with token-aware image/backdrop removal;
  pruned native resources eliminate the final destructive sanitize pass.
- **B112:** stale accessibility MCR `/Stm` references kept original Forms and
  replaced images alive outside page resources. The original native owners
  now remain the actual overlay, with the replacement canvas underneath as
  an Artifact. MCIDs, ParentTree and Alt text remain; BW native mode retains
  the catalog too. Immutable originals protect later pages with shared Forms.
  A whole-file gate catches hidden retained source-image streams. Accessibility
  metadata is not discarded to reduce sizes; no new PDF/UA certification is claimed.

Details and acceptance status: [issues B108–B112](../issues.md) and
[shared assembly design](COMPRESSION.md#shared-assembly-repairs-b108b112).
These are worker-verified repairs, **not designer-confirmed acceptance**.

Preparations check every native glyph (including real spaces), font, paint,
geometry and semantic non-whitespace replacement text. Locally renumbered
subset glyphs require identical vector outlines. Extraction-inferred gap
spaces and deliberately removed image-only whitespace tags are not glyphs.
Origin/bounds serialization tolerance stays 0.001pt; actual bitmap samples and
lossless variant page pixels must match exactly. Source warnings are archived
separately from output/decoder warnings, including during native extraction;
they cannot leak into the next image-decoding stage or excuse a new warning.

## Measurement and provenance

The overview and its unresampled reference controls have **42 realistic combination rows × 5 whole-PDF classes**, **188 verified final PDFs**, **22 explicitly inapplicable cells**, and **zero rejected cells**. The focused study adds **62 verified final PDFs**, for **250 distinct actual complete outputs** referenced by these tables. Per-cell source/preparation/output hashes and implementation provenance are in `.tmp/integrated-compression/representative-300dpi-20261016-v3/` and `.tmp/integrated-compression/scenarios-300dpi-20261016-v3/`. Main and focused studies share the same recorded core/verifier implementation. The §227 row regrouping changes presentation only; measured artifacts and focused tables are unchanged.

Each final save uses the shared production page composer, image primitives
and native/font/container saver. Packed-stream prediction and prototype
general-image compression are the explicit experimental variables. Every
final candidate is checked against its frozen preparation for encoded and
decoded image bytes, decoded native streams, geometry, metadata/attachments
and all-page no-AA pixels at 72 and 300 DPI. The preparation itself is checked
against its original input for native-text integrity, retained source-image
payloads throughout the file, and new diagnostics.
Prepared fonts are not re-subset: doing so can change checksum bytes even
when glyphs are unchanged. Saved-file hashes and complete bytes are audited.
Benchmark PDF IDs use a controlled 16-byte ASCII framing through the shared
saver's existing option, avoiding random literal-versus-hex size noise.
Normal GUI ID generation is unchanged; these remain actual complete PDFs,
not estimated UI bytes or payload-only sizes.

All current cells are fresh measurements with the recorded repaired source
hashes. Earlier mixed-DPI/rejected artifacts and the historical 549-output
cross-product remain diagnostic evidence; none is relabeled as a new 300-DPI
result. Original examples are unchanged. No timing metric is collected.
Preparations and per-case outputs can run in parallel. Only completed,
verified directories are published atomically without overwriting directories
already claimed by the main runner. Its normal strict resume path rechecks
source/implementation hashes, exact native/image bytes and all-page pixels;
the main runner alone assembles the final matrix records.

Reproduce from the repository root, using fresh labels:

```sh
nice -n 10 ./.venv/bin/python tools/bench_compression_overview.py --label <overview-label>
nice -n 10 ./.venv/bin/python tools/bench_compression_scenarios.py --label <focused-label>
./test.sh
```

Use `--resume` only for an unchanged interrupted run. Source, preparation,
output and implementation hashes gate reuse. Runners emit Markdown/JSON
evidence, not CSV. The desktop application is not launched for this study.

## Reader support

Classic Flate and Zopfli-Flate require the same FlateDecode reader format.
Brotli requires extension-aware readers whether used on pixels or native
streams. Existing installed-reader evidence and failures remain in
[NATIVE_STREAM_COMPRESSION.md](NATIVE_STREAM_COMPRESSION.md#correctness-and-compatibility).
MuPDF page equality does not certify Poppler sampling of colored stencils,
all readers or other platforms. See the
[combination/capability design](COMPRESSION_COMBINATIONS.md) and
[tested platform](PLATFORMS.md).

Independent QPDF 12.2.0 syntax checks pass for **166 ordinary-format final
PDFs**. The **84 Brotli outputs** are excluded from that installed reader's
check, not certified by it. Their exact samples/native streams/page pixels
are validated with the recorded MuPDF build. QPDF syntax success alone is
not a visual, accessibility or all-reader certification.

Fresh full suite: **552 passed**, exit 0 / FULL SUITE GREEN. Regression coverage includes tagged ownership/whole-file image gates, native-state/inline-image and fractional-page repairs, all color FFPR codecs, saved-filter migration, strict integrated/representative/scenario verification and exact real-file lifecycle. All published bytes, output hashes and tied bold minima were independently audited. Offscreen full-window and 1:1 controls/panes/strip captures were reviewed; no desktop launch or designer issue acceptance is implied.
