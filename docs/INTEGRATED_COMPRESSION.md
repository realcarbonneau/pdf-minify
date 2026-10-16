# Integrated compression — complete-PDF sizes at 300 DPI

Designer §§210–214/220–231; TODO §§226–236. This is the primary integrated
size analysis, replacing the earlier mixed-DPI overview. Measurements and
verification: 2026-10-16 (America/New_York).

**Historical matrix — before the B114 preparation repair.** The numbers below
are preserved measurements of the recorded older implementation, not fresh
post-fix results. B114's false 301-DPI intermediate altered the already-JBIG2
scan; it must not be used to rank conversion codecs. The repaired full-flow
regression now preserves every source sample and does not grow the file:
see [current regression evidence](JBIG2.md#end-to-end-regression-b114-repaired-awaiting-designer-confirmation).
TODO §239 tracks the overview's replacement with whole CCITT
`scan-naca-tm972.pdf` and recomputation of affected preparations. Its runner and
source guards are updated; the published scan column still identifies its
actual historical JFK source. No old value is relabeled as a new measurement.

## Scope and six representative cases

**Realistic algorithm combinations are rows; six complete repository PDFs
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
| Technical illustrations | [models-nasa-kepler.pdf](../examples/models-nasa-kepler.pdf) | 12 | 2,262,602 |

These cases distinguish native instructions/fonts, scanned text pixels,
photography, graphic/palette pixels, mixed research content and technical
illustrations. They are a practical basis, not an exhaustive taxonomy. Noise, existing encoding, masks, overlap
and embedded resources cut across them; focused tables follow the overview.
The photo example is an eight-page newspaper, not the logos in `images.pdf`.

NASA Kepler (§231) is added rather than substituted for a current case.
All 12 pages contain text, ten contain vector drawings, and nine contain
images (15 image placements); three pages have no bitmap placements. It
adds a multipage illustrated technical document and the designer's regular
regression input. It overlaps the mixed-content class intentionally,
broadening coverage rather than implying six exclusive PDF categories.

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
- **Every row is measured for every input** (§229), including image-free W-9
  recipes with FFPR off. Their image codec is unused; native/font/container
  compression still runs. These separately saved outputs intentionally repeat
  sizes as a sanity check, not as evidence of image-codec performance. There
  are no unmeasured or inapplicable cells in the overview.

### Fixed recipes and fidelity

Rows without FFPR retain native text/vectors; preservation is implicit in
their labels (§232). A compressor followed by `native` identifies the
compression applied to those PDF streams, not the bitmap image codec.

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

In FFPR rows, **residual streams** means the non-image PDF content left
after rasterization, mainly the commands that position/draw page images.
The label **optimized residual streams** specifically means **Zopfli-Flate
for those remaining streams**, not automatic best-algorithm selection or
additional image filtering. JPEG/JPEG2000/JBIG2 encode the image separately;
PDF object/xref packing is handled separately by the shared writer.

Specialized-codec FFPR rows use that one measured Zopfli-Flate
choice; redundant native-policy permutations are omitted. This is not an
implemented automatic residual-compressor selector. Color FFPR and uniform
built-in defaults are implemented under §§224/225. §226 migrates all existing
saved/custom raster recipes once to 300 DPI, preserving UUIDs and other
settings; later deliberate DPI edits remain. Shared general-compressor image
controls and removal of the legacy native Flate menu remain separate work
(TODO §217); experimental bitmap encodings here do not silently migrate recipes.

## Overview — final complete-file bytes

One continuous table uses unnumbered divider rows (§§227/228): unresampled
reference controls first, then BW, indexed color and full color. The controls
preserve original image encodings and vary native-stream compression; original
source sizes are listed above. Native-retaining rows precede FFPR rows within
each algorithm group. Indexed canvases use five colors, including indexed
FFPR; full-color rows use JPEG q50 or JPEG2000 lossy r192/lossless. Bold minima
remain separate for native/FFPR and lossy/lossless fidelity. All classic-Flate
and plain/predicted comparisons are retained; divider rows contain no sizes.

| Algorithm combination | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images | Technical illustrations |
|---|---:|---:|---:|---:|---:|---:|
| **Unresampled reference controls** | | | | | | |
| Preserve images + Classic Flate (reference) native | 188,447 | 341,697 | 4,641,959 | 1,493,125 | 502,235 | 2,188,983 |
| Preserve images + Zopfli-Flate native | 187,455 | **341,696** | 4,574,656 | **1,492,980** | 491,510 | 2,016,866 |
| Preserve images + Brotli native | **182,638** | 341,881 | **4,472,657** | 1,493,126 | **483,963** | **1,766,110** |
| **Black and white (BW + Otsu)** | | | | | | |
| BW + JBIG2 + Zopfli-Flate native | 187,455 | **354,089** | 1,769,572 | **9,826** | 308,200 | 1,357,553 |
| BW + JBIG2 + Brotli native | **182,638** | 354,346 | **1,668,076** | 9,980 | **300,637** | **1,106,479** |
| BW + Classic Flate (reference) | 188,447 | 713,873 | 2,211,586 | 22,466 | 336,563 | 1,606,164 |
| BW + Classic Flate (reference) + PNG prediction | 188,447 | 822,666 | 2,260,390 | 23,957 | 338,053 | 1,615,786 |
| BW + Zopfli-Flate | 187,455 | 638,993 | 2,067,873 | 20,744 | 323,303 | 1,423,956 |
| BW + Zopfli-Flate + PNG prediction | 187,455 | 744,246 | 2,078,249 | 21,330 | 323,722 | 1,427,788 |
| BW + Brotli | **182,638** | 585,313 | 1,824,470 | 14,839 | 304,720 | 1,126,864 |
| BW + Brotli + PNG prediction | **182,638** | 710,936 | 1,945,111 | 18,023 | 308,773 | 1,145,037 |
| BW FFPR + JBIG2; optimized residual streams | **297,872** | **350,190** | **1,254,079** | **3,876** | **316,049** | **299,818** |
| BW FFPR + Classic Flate (reference) | 733,677 | 709,973 | 2,714,039 | 17,679 | 800,867 | 800,754 |
| BW FFPR + Classic Flate (reference) + PNG prediction | 722,777 | 818,766 | 2,689,224 | 19,271 | 777,268 | 805,442 |
| BW FFPR + Zopfli-Flate | 688,732 | 635,094 | 2,511,775 | 15,830 | 743,693 | 724,057 |
| BW FFPR + Zopfli-Flate + PNG prediction | 649,984 | 740,347 | 2,388,759 | 16,489 | 701,446 | 710,872 |
| BW FFPR + Brotli | 531,399 | 581,338 | 1,970,142 | 9,655 | 574,796 | 527,847 |
| BW FFPR + Brotli + PNG prediction | 578,653 | 706,961 | 2,288,813 | 13,482 | 625,834 | 624,793 |
| **Indexed color — low palettes** | | | | | | |
| Indexed 5 colors + colored JBIG2 + Zopfli-Flate native | 187,455 | **1,099,894** | 4,419,818 | **17,669** | 345,678 | 1,613,624 |
| Indexed 5 colors + colored JBIG2 + Brotli native | **182,638** | 1,100,131 | 4,318,364 | 17,816 | 338,105 | 1,362,486 |
| Indexed 5 colors + Classic Flate (reference) | 188,447 | 1,341,839 | 4,469,850 | 31,951 | 378,057 | 1,898,293 |
| Indexed 5 colors + Classic Flate (reference) + PNG prediction | 188,447 | 1,879,772 | 5,065,305 | 39,838 | 390,403 | 1,990,383 |
| Indexed 5 colors + Zopfli-Flate | 187,455 | 1,174,973 | 4,098,298 | 28,999 | 359,021 | 1,680,513 |
| Indexed 5 colors + Zopfli-Flate + PNG prediction | 187,455 | 1,684,784 | 4,518,574 | 34,617 | 367,014 | 1,744,000 |
| Indexed 5 colors + Brotli | **182,638** | 1,192,432 | **3,523,561** | 23,219 | **332,124** | **1,332,266** |
| Indexed 5 colors + Brotli + PNG prediction | **182,638** | 1,625,012 | 4,283,194 | 30,164 | 347,017 | 1,437,334 |
| Color FFPR; indexed 5 colors + colored JBIG2; optimized residual streams | **299,497** | **1,095,765** | 4,488,350 | **12,417** | **337,274** | **394,165** |
| Color FFPR; indexed 5 colors + Classic Flate (reference) | 733,827 | 1,337,939 | 5,778,786 | 32,907 | 876,609 | 1,062,053 |
| Color FFPR; indexed 5 colors + Classic Flate (reference) + PNG prediction | 722,927 | 1,875,872 | 6,763,541 | 41,339 | 860,595 | 1,089,908 |
| Color FFPR; indexed 5 colors + Zopfli-Flate | 688,882 | 1,171,074 | 5,208,697 | 28,079 | 783,305 | 912,904 |
| Color FFPR; indexed 5 colors + Zopfli-Flate + PNG prediction | 650,134 | 1,680,885 | 6,024,506 | 34,163 | 754,689 | 918,004 |
| Color FFPR; indexed 5 colors + Brotli | 531,549 | 1,188,457 | **4,380,676** | 21,438 | 602,501 | 676,529 |
| Color FFPR; indexed 5 colors + Brotli + PNG prediction | 578,803 | 1,621,037 | 5,729,329 | 31,336 | 668,343 | 809,612 |
| **Full color** | | | | | | |
| JPEG q50 + Zopfli-Flate native | 187,455 | **3,944,595** | 6,249,832 | **116,165** | 551,040 | 2,349,594 |
| JPEG q50 + Brotli native | **182,638** | 3,944,852 | **6,148,336** | 116,319 | **543,477** | **2,098,520** |
| JPEG2000 lossy r192 + Zopfli-Flate native | 187,455 | **1,053,173** | 3,626,722 | **139,048** | 538,500 | 2,483,414 |
| JPEG2000 lossy r192 + Brotli native | **182,638** | 1,053,430 | **3,525,226** | 139,202 | **530,937** | **2,232,340** |
| JPEG2000 lossless + Zopfli-Flate native | 187,455 | **26,637,476** | 55,276,886 | **569,743** | 1,816,596 | 8,930,828 |
| JPEG2000 lossless + Brotli native | **182,638** | 26,637,733 | **55,175,390** | 569,897 | **1,809,033** | **8,679,754** |
| Color FFPR + JPEG q50; optimized residual streams | **5,674,560** | **3,940,696** | **16,386,640** | **119,537** | **5,695,628** | **6,225,232** |
| Color FFPR + JPEG2000 lossy r192; optimized residual streams | **790,654** | **1,049,274** | **2,321,850** | **132,375** | **1,186,046** | **1,581,087** |
| Color FFPR + JPEG2000 lossless; optimized residual streams | **26,977,014** | **26,633,577** | **130,483,529** | **631,823** | **27,091,577** | **32,340,923** |

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
| BW + Classic Flate (reference) | 713,873 | 439,941 |
| BW + Classic Flate (reference) + PNG prediction | 822,666 | 442,832 |
| BW + Zopfli-Flate | 638,993 | 400,877 |
| BW + Zopfli-Flate + PNG prediction | 744,246 | 389,105 |
| BW + Brotli | 585,313 | 296,438 |
| BW + Brotli + PNG prediction | 710,936 | 363,846 |
| BW + JBIG2 + Zopfli-Flate native | **354,089** | 197,613 |
| BW + JBIG2 + Brotli native | 354,346 | **196,098** |

### Threshold sensitivity — three explicit BW transforms

The same complete `images.pdf`, 300 DPI, native artwork retained. Otsu and
Simple T180/T210 produce different pixels. Compare encoders within each
column, not the thresholds as though their output were visually identical.

| Algorithm combination | Otsu | Simple T180 | Simple T210 |
|---|---:|---:|---:|
| BW + Classic Flate (reference) | 22,466 | 23,312 | 26,704 |
| BW + Classic Flate (reference) + PNG prediction | 23,957 | 24,749 | 28,411 |
| BW + Zopfli-Flate | 20,744 | 21,546 | 24,363 |
| BW + Zopfli-Flate + PNG prediction | 21,330 | 22,037 | 25,145 |
| BW + Brotli | 14,839 | 15,533 | 17,970 |
| BW + Brotli + PNG prediction | 18,023 | 18,911 | 22,325 |
| BW + JBIG2 + Zopfli-Flate native | **9,826** | **10,102** | **10,937** |
| BW + JBIG2 + Brotli native | 9,980 | 10,256 | 11,091 |

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
- Across **93** same-input/same-compressor prediction pairs, predicted is smaller in **12**, tied in **6**, and larger in **75**. Six ties are the separately measured no-image W-9 pairs, where no prediction runs. The 87 image-bearing pairs have 12 wins, 0 ties and 75 losses. Each compares complete `+ PNG prediction` PDF bytes with that encoder's plain counterpart. Where smaller, prediction saves **0.91%–5.68%** of its own plain counterpart’s complete bytes.
- The unresampled W-9 original is **140,815 B**; even its smallest tested preserve-images rewrite is **182,638 B**. Being the smallest tested rewrite does not mean it beats the untouched source.
- NASA Kepler: preserve-images + Zopfli native is **2,016,866 B**; Brotli native is **1,766,110 B**, versus the **2,262,602 B** original. Native-preserving BW/JBIG2 + Zopfli is **1,357,553 B**, while BW FFPR/JBIG2 is **299,818 B**. The last two have different native/text fidelity, not equivalent codec quality.
- On the identical prepared five-color Kepler pixels, shared Brotli is **1,332,266 B**, versus **1,362,486 B** for colored JBIG2 + Brotli native: Brotli images are **2.22% smaller** than that JBIG2 counterpart. Both retain the same native artwork and require a Brotli-capable reader; this is a content-specific result, not a universal codec ranking.
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

The historical overview has **42 realistic combination rows × 6 whole-PDF cases**, **252 verified final PDFs**, **zero excluded/unmeasured cells**, and **zero rejected cells**. The focused study retains **62 verified final PDFs**, for **314 distinct actual complete outputs** referenced by these tables. The sixth case adds 42 independently saved, verified whole-Kepler outputs, not partial-page or component-size estimates. All 210 earlier overview cells retain their exact sizes, files and measurement-specific provenance. Encoder/output equality against these frozen preparations does not establish source-pixel equality when preparation was defective (B114); this is not post-fix verification.

The combined six-case manifest, frozen overview/extension drivers and exact source-compatibility proof are under `.tmp/integrated-compression/representative-six-300dpi-20261016/`; its `kepler/metrics.json` records the new 42-cell run and its actual renamed source environment. The previous 210-cell overview remains under `.tmp/integrated-compression/representative-complete-300dpi-20261016-v2/`; the original 188-file overview and focused outputs remain under `.tmp/integrated-compression/representative-300dpi-20261016-v3/` and `.tmp/integrated-compression/scenarios-300dpi-20261016-v3/`. No old fingerprint or archived result is rewritten.

The 22 formerly excluded no-image cells are independently saved and verified, not copied control sizes. B113 changes only their native-copy entry to the existing controlled-ID container normalizer. The exact before/after source proof is replayed from pinned Git revision `aa3cb847a75ca0f6acf65de5159ace85cc155847`, not mutable HEAD; the old image-bearing/FFPR preparations do not use that branch. Those no-image outputs preserve zero image objects, original native glyphs and exact original page pixels at 72/300 DPI.

The PDF Minify rename follows the original measurements. Their manifests retain historical `pdf_minimalist/` paths and hashes. For the sixth-case extension, a bounded source audit proves only literal `pdf_minimalist` → `pdf_minify` substitutions in the saver/verifier modules, plus the overview's added document and descriptive docstring. Existing source/preparation/output hashes are rechecked, and each new result retains its own verified implementation. The combined manifest explicitly records mixed implementation provenance; its historical environment is not relabeled as the new one. The strict automatic cross-version import/resume gate remains unchanged and rejects mismatched versions.

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

All snapshot cells are actual complete-file measurements with their recorded
source versions and hashes, preceding the B114 density repair. Earlier mixed-DPI/rejected artifacts and the historical 549-output
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

QPDF 12.2.0 syntax checks pass all **207 ordinary-format outputs**; the **107 Brotli outputs** are excluded from that unsupported reader check, not certified by it.

Classic Flate and Zopfli-Flate require the same FlateDecode reader format.
Brotli requires extension-aware readers whether used on pixels or native
streams. Existing installed-reader evidence and failures remain in
[NATIVE_STREAM_COMPRESSION.md](NATIVE_STREAM_COMPRESSION.md#correctness-and-compatibility).
MuPDF page equality does not certify Poppler sampling of colored stencils,
all readers or other platforms. See the
[combination/capability design](COMPRESSION_COMBINATIONS.md) and
[tested platform](PLATFORMS.md).

The Brotli outputs' exact samples/native streams/page pixels
are validated with the recorded MuPDF build. QPDF syntax success alone is
not a visual, accessibility or all-reader certification.

Historical full suite after all-row coverage, PDF Minify rename and six-case extension: **572 passed**, exit 0 / FULL SUITE GREEN. Regression coverage includes tagged ownership/whole-file image gates, native-state/inline-image and fractional-page repairs, all color FFPR codecs, saved-filter/name migration, strict integrated/representative/scenario verification and exact real-file lifecycle. All published bytes, output hashes and tied bold minima were independently audited. Current B114 repair and **593-test** verification are recorded in [TEST_PLAN.md](TEST_PLAN.md); they do not remeasure this snapshot. No desktop launch or designer issue acceptance is implied.
