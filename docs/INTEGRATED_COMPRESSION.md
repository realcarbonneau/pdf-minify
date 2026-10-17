# Integrated compression — complete-PDF sizes at 300 DPI

Designer §§210–214/220–240; TODO §§226–242. This is the primary integrated
size analysis, replacing the earlier mixed-DPI overview. Measurements and
verification: 2026-10-16 (America/New_York).

**Current selected results after the B114 preparation repair.** The same **204 measured cells** are now presented as **156 baseline overview cells** and **48 isolated PNG-prediction effect cells**; focused scenarios use **48 additional complete PDFs**. All 252 distinct outputs come from the newly saved, verified post-repair study. Designer §§236/237 remove redundant Classic-Flate bitmap rows consistently from the overview and every focused section; no pre-fix measurements are reused. The BW source is now the eleven-page CCITT NACA TM972 scan, not the already-JBIG2 JFK regression fixture. B114's runtime repair is worker-verified, not designer-confirmed acceptance.

## Scope and six representative cases

**Realistic algorithm combinations are rows; six complete repository PDFs
are columns. All sizes are measured final saved PDF bytes.** PNG-effect
percentages compare those measurements with their named plain baselines. Fonts,
native drawing streams, images, masks, palettes and container overhead are
included. No compute-time rankings, component-size estimates or CSV delivery.

| Representative class | Complete PDF | Pages | Original bytes |
|---|---|---:|---:|
| Native text/vectors | [form-fw9.pdf](../examples/form-fw9.pdf) | 6 | 140,815 |
| BW scan | [scan-naca-tm972.pdf](../examples/scan-naca-tm972.pdf) | 11 | 374,461 |
| Color photos | [news-crater-lake-2026.pdf](../examples/news-crater-lake-2026.pdf) | 8 | 5,550,048 |
| Flat-color artwork | [images.pdf](../examples/images.pdf) | 1 | 1,494,439 |
| Mixed text/images | [paper-arxiv-1406.2661.pdf](../examples/paper-arxiv-1406.2661.pdf) | 9 | 530,482 |
| Technical illustrations | [models-nasa-kepler.pdf](../examples/models-nasa-kepler.pdf) | 12 | 2,262,602 |

These cases distinguish native instructions/fonts, scanned text pixels,
photography, graphic/palette pixels, mixed research content and technical
illustrations. They are a practical basis, not an exhaustive taxonomy. Noise, existing encoding, masks, overlap
and embedded resources cut across them; focused tables follow the overview.
The photo example is an eight-page newspaper, not the logos in `images.pdf`.

The BW case is whole `scan-naca-tm972.pdf`: eleven 1-bit grayscale `/CCITTFaxDecode` images at approximately 300 DPI, with scanned typewriting, annotations, diagrams and original OCR text. It contains no JBIG2 image streams. The already-JBIG2 JFK scan is retained solely as B114's full-flow source-pixel/no-growth regression, not a conversion ranking in these tables. All original PDFs are unchanged.

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
  compressor, not a second image/codec. The overview shows plain baselines; the separate PNG table isolates its measured effect.
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

Indexed uses **up to five total colors** in the overview; focused palette
limits are 5/16/64. A source with fewer colors need not use every entry;
colored JBIG2 encodes only used non-white colors.
BW uses **Otsu**, except the explicitly labeled Simple thresholds. JPEG uses
**quality 50**; JPEG2000 uses **rate 192 (lossy)** or explicit **lossless**.
JPEG q50 and JPEG2000 r192 are **not quality-matched**. Lossless encoding
preserves the prepared 300-DPI raster, not the original unresampled PDF.
Common DPI does not make these different transformations equal fidelity.
Palette/BW processing does not recolor the native artwork retained with FFPR OFF.

Measured BW and colored JBIG2 use independent generic regions via `jbig2 -p`, without `-d`, symbol/refinement mode or shared multi-page dictionaries. This is the current implemented path, not an exhaustive best-settings search. Feature boundaries and the remaining optimization research are in [JBIG2.md](JBIG2.md), TODO §240.

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
source sizes are listed above. Here **Preserve images** means keeping
the original encoded image data, codecs, pixel dimensions, colors and
masks unchanged: no image composition, resampling or re-encoding.
Native text/font streams and the PDF container can still be optimized,
so the entire file need not be byte-identical. Other rows retain the
pictures as content but deliberately change their representation:
compose at full color, resize once to 300 DPI, then threshold, reduce
colors or apply the selected image codec. Without FFPR, text/vectors
remain native; with FFPR, they too become part of the page bitmap.
Native-retaining rows precede FFPR rows within
each algorithm group. Indexed canvases use up to five colors, including indexed
FFPR; full-color rows use JPEG q50 or JPEG2000 lossy r192/lossless. Bold minima
remain separate for native/FFPR and lossy/lossless fidelity.
The unresampled Classic-Flate reference remains. Designer §§236/237 remove
eight repeated Classic-Flate bitmap rows here and their equivalents
throughout all focused tables. Both Zopfli/Brotli variants remain measured;
the eight PNG rows move to the isolated-effect table below (§§238–240).
Divider rows contain no sizes.

| Algorithm combination | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images | Technical illustrations |
|---|---:|---:|---:|---:|---:|---:|
| **Unresampled reference controls** | | | | | | |
| Preserve images + Classic Flate (reference) native | 188,447 | 367,630 | 4,641,959 | 1,493,125 | 502,235 | 2,188,983 |
| Preserve images + Zopfli-Flate native | 187,455 | 366,695 | 4,574,656 | **1,492,980** | 491,510 | 2,016,866 |
| Preserve images + Brotli native | **182,638** | **364,519** | **4,472,657** | 1,493,126 | **483,963** | **1,766,110** |
| **Black and white (BW + Otsu)** | | | | | | |
| BW + JBIG2 + Zopfli-Flate native | 187,455 | 270,228 | 1,724,023 | **9,798** | 308,080 | 1,357,736 |
| BW + JBIG2 + Brotli native | **182,638** | **268,062** | **1,622,527** | 9,952 | **300,517** | **1,106,662** |
| BW + Zopfli-Flate | 187,455 | 578,690 | 1,973,320 | 20,769 | 323,270 | 1,424,063 |
| BW + Brotli | **182,638** | 413,105 | 1,747,874 | 14,852 | 304,838 | 1,127,115 |
| BW FFPR + JBIG2; optimized residual streams | **297,872** | **229,520** | **1,199,049** | **3,868** | **316,049** | **299,818** |
| BW FFPR + Zopfli-Flate | 688,732 | 537,982 | 2,436,663 | 15,756 | 743,693 | 724,057 |
| BW FFPR + Brotli | 531,399 | 374,743 | 1,903,320 | 9,569 | 574,796 | 527,847 |
| **Indexed color — low palettes** | | | | | | |
| Indexed 5 colors + colored JBIG2 + Zopfli-Flate native | 187,455 | 272,001 | 4,104,794 | **15,776** | 345,953 | 1,614,891 |
| Indexed 5 colors + colored JBIG2 + Brotli native | **182,638** | **269,847** | 4,003,340 | 15,923 | 338,380 | 1,363,753 |
| Indexed 5 colors + Zopfli-Flate | 187,455 | 578,965 | 3,769,149 | 28,012 | 359,179 | 1,683,086 |
| Indexed 5 colors + Brotli | **182,638** | 413,380 | **3,277,883** | 22,083 | **331,829** | **1,334,257** |
| Color FFPR; indexed 5 colors + colored JBIG2; optimized residual streams | **299,497** | **231,619** | 3,817,106 | **9,390** | **337,274** | **394,165** |
| Color FFPR; indexed 5 colors + Zopfli-Flate | 688,882 | 538,257 | 4,501,917 | 21,713 | 783,305 | 912,904 |
| Color FFPR; indexed 5 colors + Brotli | 531,549 | 375,018 | **3,733,876** | 15,529 | 602,501 | 676,529 |
| **Full color** | | | | | | |
| JPEG q50 + Zopfli-Flate native | 187,455 | 4,434,870 | 6,269,805 | **116,296** | 550,470 | 2,349,517 |
| JPEG q50 + Brotli native | **182,638** | **4,432,704** | **6,168,309** | 116,450 | **542,907** | **2,098,443** |
| JPEG2000 lossy r192 + Zopfli-Flate native | 187,455 | 1,253,676 | 3,626,725 | **139,068** | 538,601 | 2,483,638 |
| JPEG2000 lossy r192 + Brotli native | **182,638** | **1,251,510** | **3,525,229** | 139,222 | **531,038** | **2,232,564** |
| JPEG2000 lossless + Zopfli-Flate native | 187,455 | 19,100,317 | 56,343,268 | **569,368** | 1,813,182 | 8,926,081 |
| JPEG2000 lossless + Brotli native | **182,638** | **19,098,151** | **56,241,772** | 569,522 | **1,805,619** | **8,675,007** |
| Color FFPR + JPEG q50; optimized residual streams | **5,674,560** | **4,394,162** | **16,652,211** | **119,758** | **5,695,628** | **6,225,232** |
| Color FFPR + JPEG2000 lossy r192; optimized residual streams | **790,654** | **1,212,968** | **2,322,153** | **132,374** | **1,186,046** | **1,581,087** |
| Color FFPR + JPEG2000 lossless; optimized residual streams | **26,977,014** | **19,059,609** | **127,518,137** | **631,376** | **27,091,577** | **32,340,923** |

An encoded output can exceed the untouched original. The original sizes above
remain the baseline; the smallest tested encoding within a group is not
automatically an improvement over that original.

## PNG prediction — measured effect versus baseline

Only **image-row PNG prediction** changes within each pair. The row
names its plain baseline in the overview above. Each cell shows the
**measured complete saved PDF bytes with PNG prediction**, followed by
the signed change from that baseline's measured complete PDF bytes.

`Change (%) = 100 × (PNG-prediction bytes − baseline bytes) / baseline bytes`.
**Negative is smaller/better; positive is larger/worse.** Percentages
are rounded to one decimal place. Bold bytes mean this result is no
larger than its own baseline, including ties—not a cross-document minimum.

Source PDF, prepared pixels/palette, DPI, threshold, native-stream
compressor and save policy are unchanged within each pair. These are
two actual separately saved PDFs, never an estimated size or a copied
control. The non-FFPR W-9 has no bitmap stage: its four independently
measured ties are no-op sanity controls, not evidence of predictor savings.

| Baseline combination | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images | Technical illustrations |
|---|---:|---:|---:|---:|---:|---:|
| BW + Zopfli-Flate | **187,455** (+0.0%) | **570,171** (-1.5%) | 2,001,217 (+1.4%) | 21,477 (+3.4%) | 323,698 (+0.1%) | 1,428,260 (+0.3%) |
| BW + Brotli | **182,638** (+0.0%) | 530,018 (+28.3%) | 1,855,119 (+6.1%) | 18,450 (+24.2%) | 308,565 (+1.2%) | 1,145,936 (+1.7%) |
| BW FFPR + Zopfli-Flate | **649,984** (-5.6%) | **529,463** (-1.6%) | **2,325,936** (-4.5%) | 16,434 (+4.3%) | **701,446** (-5.7%) | **710,872** (-1.8%) |
| BW FFPR + Brotli | 578,653 (+8.9%) | 491,656 (+31.2%) | 2,217,193 (+16.5%) | 13,429 (+40.3%) | 625,834 (+8.9%) | 624,793 (+18.4%) |
| Indexed 5 colors + Zopfli-Flate | **187,455** (+0.0%) | **570,446** (-1.5%) | 4,215,578 (+11.8%) | 32,639 (+16.5%) | 367,102 (+2.2%) | 1,747,647 (+3.8%) |
| Indexed 5 colors + Brotli | **182,638** (+0.0%) | 530,293 (+28.3%) | 3,960,927 (+20.8%) | 28,415 (+28.7%) | 347,261 (+4.7%) | 1,441,081 (+8.0%) |
| Color FFPR; indexed 5 colors + Zopfli-Flate | **650,134** (-5.6%) | **529,738** (-1.6%) | 5,129,371 (+13.9%) | 25,857 (+19.1%) | **754,689** (-3.7%) | 918,004 (+0.6%) |
| Color FFPR; indexed 5 colors + Brotli | 578,803 (+8.9%) | 491,931 (+31.2%) | 4,836,813 (+29.5%) | 22,344 (+43.9%) | 668,343 (+10.9%) | 809,612 (+19.7%) |

This first review covers PNG prediction only. Residual-stream rows and
the existing focused-scenario measurements below are unchanged.

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
| JPEG q50 + Zopfli-Flate native | 6,269,805 |
| JPEG q50 + Brotli native | **6,168,309** |
| JPEG2000 lossy r192 + Zopfli-Flate native | 3,626,725 |
| JPEG2000 lossy r192 + Brotli native | **3,525,229** |
| JPEG2000 lossless + Zopfli-Flate native | 56,343,268 |
| JPEG2000 lossless + Brotli native | **56,241,772** |
| Color FFPR + JPEG q50; optimized residual streams | **16,652,211** |
| Color FFPR + JPEG2000 lossy r192; optimized residual streams | **2,322,153** |
| Color FFPR + JPEG2000 lossless; optimized residual streams | **127,518,137** |

### Logos/artwork — palette count

The same complete `images.pdf` at 300 DPI with native artwork retained.
Within each column the competing lossless encoders preserve identical
prepared pixels. Changing the palette is not an equal-fidelity contest.

| Algorithm combination | 5 colors | 16 colors | 64 colors |
|---|---:|---:|---:|
| Indexed + Zopfli-Flate | 28,012 | 44,809 | 63,305 |
| Indexed + Zopfli-Flate + PNG prediction | 32,639 | 51,430 | 85,501 |
| Indexed + Brotli | 22,083 | 36,511 | **52,556** |
| Indexed + Brotli + PNG prediction | 28,415 | 47,209 | 76,912 |
| Indexed + colored JBIG2 + Zopfli-Flate native | **15,776** | **34,468** | 71,263 |
| Indexed + colored JBIG2 + Brotli native | 15,923 | 34,594 | 71,312 |

### Mixed text/images — palette count

All nine GAN-paper pages at 300 DPI. Text, vectors and fonts remain native;
only the composed bitmap layer is palette-reduced.

| Algorithm combination | 5 colors | 16 colors | 64 colors |
|---|---:|---:|---:|
| Indexed + Zopfli-Flate | 359,179 | 459,802 | 578,231 |
| Indexed + Zopfli-Flate + PNG prediction | 367,102 | 478,813 | 640,060 |
| Indexed + Brotli | **331,829** | **416,980** | **513,744** |
| Indexed + Brotli + PNG prediction | 347,261 | 456,362 | 605,928 |
| Indexed + colored JBIG2 + Zopfli-Flate native | 345,953 | 467,614 | 643,874 |
| Indexed + colored JBIG2 + Brotli native | 338,380 | 460,017 | 636,143 |

### Scanned BW text — different source material

NACA TM972 (eleven pages) and NACA formulas (seven pages), 300 DPI/Otsu,
with native artwork retained if present. Typewritten scans and mathematical
print are distinct stress cases, not interchangeable evidence.

| Algorithm combination | NACA TM972 | NACA formulas |
|---|---:|---:|
| BW + Zopfli-Flate | 578,690 | 394,669 |
| BW + Zopfli-Flate + PNG prediction | 570,171 | 383,806 |
| BW + Brotli | 413,105 | 289,977 |
| BW + Brotli + PNG prediction | 530,018 | 357,859 |
| BW + JBIG2 + Zopfli-Flate native | 270,228 | 192,438 |
| BW + JBIG2 + Brotli native | **268,062** | **190,923** |

### Threshold sensitivity — three explicit BW transforms

The same complete `images.pdf`, 300 DPI, native artwork retained. Otsu and
Simple T180/T210 produce different pixels. Compare encoders within each
column, not the thresholds as though their output were visually identical.

| Algorithm combination | Otsu | Simple T180 | Simple T210 |
|---|---:|---:|---:|
| BW + Zopfli-Flate | 20,769 | 21,537 | 24,435 |
| BW + Zopfli-Flate + PNG prediction | 21,477 | 22,005 | 25,299 |
| BW + Brotli | 14,852 | 15,584 | 18,148 |
| BW + Brotli + PNG prediction | 18,450 | 18,878 | 22,415 |
| BW + JBIG2 + Zopfli-Flate native | **9,798** | **10,077** | **10,945** |
| BW + JBIG2 + Brotli native | 9,952 | 10,231 | 11,099 |

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

- Five-color artwork: colored JBIG2 + Zopfli-native is **15,776 B**, versus **22,083 B** for shared Brotli without prediction. The complete mixed-paper counterparts are **345,953 B** and **331,829 B**. Representation/content changes the comparison.
- On the eleven-page **CCITT** NACA TM972 scan, BW/JBIG2 + Zopfli-native is **270,228 B**, versus **413,105 B** for shared Brotli at identical prepared BW pixels. The unresampled Zopfli control is **366,695 B** and the original is **374,461 B**. The measured JBIG2 recipe is **27.84% smaller** than that original; this is not a universal ranking.
- Crater Lake's native-preserving JPEG q50 + Zopfli-native is **6,269,805 B**; its full-page JPEG counterpart is **16,652,211 B**. Both target 300 DPI, but FFPR rasterizes text/vectors: their sizes are not equal-fidelity codec scores.
- The [isolated PNG-prediction table](#png-prediction--measured-effect-versus-baseline) shows all **48 six-document pairs**, with measured bytes and signed change versus each matching baseline. The focused scenarios retain 14 additional pairs; they are not pooled into that six-document table. No new encoding or residual-stream comparison is introduced.
- The unresampled W-9 original is **140,815 B**; its smallest tested preserve-images rewrite is **182,638 B**. Being the smallest tested rewrite does not mean it beats the untouched source.
- NASA Kepler: preserve-images + Zopfli native is **2,016,866 B**; Brotli native is **1,766,110 B**, versus the **2,262,602 B** original. Native-preserving BW/JBIG2 + Zopfli is **1,357,736 B**, while BW FFPR/JBIG2 is **299,818 B**. The last two have different native/text fidelity, not equivalent codec quality.
- On identical prepared five-color Kepler pixels, shared Brotli is **1,334,257 B**, versus **1,363,753 B** for colored JBIG2 + Brotli native: the complete shared-Brotli PDF is **2.16% smaller** than that complete JBIG2 counterpart. Both retain the same native artwork and require a Brotli-capable reader; this is content-specific, not a universal codec ranking.
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

- **B114:** whole-DPI upward quantization could turn PDF float noise near
  300 DPI into a real 301-DPI intermediate and change source samples. The
  compositor now keeps fractional image/mask density. Every preparation
  in these tables is newly generated after that repair. The separate
  eight-page JFK native/FFPR no-op tests preserve every original sample
  and page pixel and do not grow the complete PDF; see [JBIG2.md](JBIG2.md).

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

The measurement inventory remains **34 combinations × six whole PDFs = 204 verified cells**, displayed as **26 baseline overview rows / 156 sizes** plus **eight PNG-effect rows / 48 sizes**, with zero excluded, unmeasured or rejected cells. Focused tables display another 87 cells, reusing 39 overview outputs and referencing **48 additional PDFs**: **291 displayed size cells / 252 distinct actual complete files** in total. Every no-image row is still independently saved and verified, not filled by copying a control.

The complete fresh post-B114 measurement superset remains immutable under `.tmp/integrated-compression/post-b114-300dpi-20261016/`: 252 overview and 62 focused outputs, all saved using one repaired compositor. Its `identity.json` pins source, tool, environment and saver/verifier/driver hashes; `refresh.py`, `overview.py`, `scenarios.py`, scoped job manifests and `complete.json` preserve the actual full measurement scope.

`image-streams.py` also freezes the measured bitmap driver. Subsequent runner
changes select only retained variants and remove an unused JSON percentage
that incorrectly assumed the first variant was always Classic Flate. This
changes future scope/metadata, not the shared pixel/encoding/save operations;
the current publication retains the actual measured implementation hashes.

Designer §§236/237's reduced publication is a hash-verified **selection from that measured superset**, not a claim that it was re-encoded under the later row-selection code. `selected-237/metrics.json` records the exact selected paths, original per-output provenance, frozen-superset hashes and new selector scope. The redundant bitmap combinations are removed consistently from every table, not kept as supplemental references. Sixty-two superseded files stay archived but are not current analysis cells. No original source, saved PDF, measured byte count or strict import/resume gate is rewritten or relaxed.

Historical studies remain untouched under `.tmp/integrated-compression/representative-six-300dpi-20261016/`, `representative-complete-300dpi-20261016-v2/`, `representative-300dpi-20261016-v3/` and `scenarios-300dpi-20261016-v3/`. Their original files, historical namespace paths and compatibility proofs are not relabeled. The already-JBIG2 JFK measurements remain B114 regression/diagnostic evidence, not current codec-rank cells.

Each final save uses the shared production page composer, image primitives
and native/font/container saver. Packed-stream prediction and prototype
general-image compression are the explicit experimental variables. Every
final candidate is checked against its frozen preparation for encoded and
decoded image bytes, decoded native streams, geometry, metadata/attachments
and all-page no-AA pixels at 72 and 300 DPI. The preparation itself is checked
against its original input for native-text integrity, unintended retained source-image
payloads throughout the file, and new diagnostics.
Prepared fonts are not re-subset: doing so can change checksum bytes even
when glyphs are unchanged. Saved-file hashes and complete bytes are audited.
Benchmark PDF IDs use a controlled 16-byte ASCII framing through the shared
saver's existing option, avoiding random literal-versus-hex size noise.
Normal GUI ID generation is unchanged; these remain actual complete PDFs,
not estimated UI bytes or payload-only sizes.

All current cells are actual complete-file measurements from the repaired compositor. Source/preparation/output hashes are checked; earlier failed or mixed-DPI results remain historical, never current measurements. Ordinary low-priority subprocesses use independent scoped directories, with no preparation races or shared output writers. Only completed verified jobs enter the final matrix. No encoding-time metric/ranking is published, and all original PDFs remain unchanged.

Reproduce from the repository root, using fresh labels:

```sh
nice -n 10 ./.venv/bin/python tools/bench_compression_overview.py --label <overview-label>
nice -n 10 ./.venv/bin/python tools/bench_compression_scenarios.py --label <focused-label>
./test.sh
```

Use `--resume` only for an unchanged interrupted run. Source, preparation,
output and implementation hashes gate reuse. Runners emit Markdown/JSON
evidence, not CSV. The desktop application is not launched for this study.

The PNG-only presentation split is recorded under `.tmp/png-prediction-review-20261016/`: the before/after Markdown, frozen formatter/publisher sources, original measurement-manifest hash and exact PNG/plain output paths and hashes. No measurement or original provenance is rewritten; current formatter code is not claimed as the encoding implementation.

## Reader support

QPDF 12.2.0 syntax checks pass all **145 selected ordinary-format outputs**; the **107 selected Brotli outputs** are excluded from that unsupported reader check, not certified by it.

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

The B114 repair originally passed 593 tests; source publication and consistent
row pruning then passed 605. The fresh full suite after the PNG-only split is
**635 passed**, with no expected failures. The 30 PNG-table cases, latest
110-test focused run, source-choice/publication coverage and earlier 30-PDF
actual subset smoke are recorded in [TEST_PLAN.md](TEST_PLAN.md).
All published bytes, actual output hashes, tied bold minima and source
descriptors are independently audited. This headless study does not launch
the desktop application or imply designer acceptance.
