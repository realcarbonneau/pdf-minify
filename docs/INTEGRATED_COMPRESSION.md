# Integrated compression — complete-PDF sizes at 300 DPI

Designer §§210–214/220–251; TODO §§226–250. This is the primary integrated
size analysis, replacing the earlier mixed-DPI overview. Measurements and
verification: 2026-10-16–17 (America/New_York).

**Declaration policy:** these frozen tables used the earlier automatic Brotli
extension declaration. Designer §251 changes new filters/tests/benchmarks to
declaration **OFF by default**, with an explicit Brotli-only compatibility
option. The numbers below retain their original declaration-ON provenance;
they are not remeasured default-OFF results or metadata-subtraction estimates.

**Current selected results after the B114 preparation repair.** The representative overview now has **204 baseline sizes** and **96 isolated PNG effects** across six PDFs. The native/residual A/B experiment adds **42 paired comparisons**; the FFPR Brotli-baseline/Zopfli-treatment study adds **30 pairs**. Together with the unchanged focused scenarios, **392 distinct actual saved PDFs** support these tables, including 30 new FFPR Brotli baselines. Two additional metadata-only diagnostic outputs are not ranked. Compatible earlier outputs retain their original provenance; only missing cases were encoded. The BW representative is the eleven-page CCITT NACA TM972 scan, not the already-JBIG2 JFK regression fixture. B114 is worker-verified, not designer-confirmed acceptance.

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
- **Zopfli** means the encoder producing standard FlateDecode data; the
  longer Zopfli-Flate label adds no distinction in these tables. **Classic Flate** is a labeled
  comparison reference, not an encoder-speed recommendation.
- Packed BW/indexed images and native streams use the **same general
  compressor**. Mixed general-compressor pairings are excluded from the algorithm overview.
  The isolated native-stream experiment deliberately holds image bytes fixed. Specialized
  JPEG/JPEG2000/JBIG2 retain meaningful native Zopfli/Brotli alternatives.
- Percentage differences use **two decimal places**, computed from original
  measured bytes. Rounded zero is `+0.00%` and is never bold; it can hide a
  tiny actual change, so raw byte evidence remains authoritative.
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

Indexed uses **up to 5/16/64 total colors**, in separate fidelity groups.
The expanded 16/64-color rows are paired PNG controls, not a complete
specialized-codec search at each palette limit. A source with fewer colors need not use every entry;
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
each algorithm group. Indexed canvases have separate 5/16/64-color groups,
including indexed FFPR; full-color rows use JPEG q50 or JPEG2000 lossy r192/lossless. Bold minima
remain separate for native/FFPR and lossy/lossless fidelity.
The unresampled Classic-Flate reference remains. Designer §§236/237 remove
eight repeated Classic-Flate bitmap rows here and their equivalents
throughout all focused tables. Both Zopfli/Brotli variants remain measured;
PNG variants appear in the isolated-effect table below (§§238–242).
Divider rows contain no sizes.

| Algorithm combination | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images | Technical illustrations |
|---|---:|---:|---:|---:|---:|---:|
| **Unresampled reference controls** | | | | | | |
| Preserve images + Classic Flate (reference) native | 188,447 | 367,630 | 4,641,959 | 1,493,125 | 502,235 | 2,188,983 |
| Preserve images + Zopfli native | 187,455 | 366,695 | 4,574,656 | **1,492,980** | 491,510 | 2,016,866 |
| Preserve images + Brotli native | **182,638** | **364,519** | **4,472,657** | 1,493,126 | **483,963** | **1,766,110** |
| **Black and white (BW + Otsu)** | | | | | | |
| BW + JBIG2 + Zopfli native | 187,455 | 270,228 | 1,724,023 | **9,798** | 308,080 | 1,357,736 |
| BW + JBIG2 + Brotli native | **182,638** | **268,062** | **1,622,527** | 9,952 | **300,517** | **1,106,662** |
| BW + Zopfli | 187,455 | 578,690 | 1,973,320 | 20,769 | 323,270 | 1,424,063 |
| BW + Brotli | **182,638** | 413,105 | 1,747,874 | 14,852 | 304,838 | 1,127,115 |
| BW FFPR + JBIG2; optimized residual streams | **297,872** | **229,520** | **1,199,049** | **3,868** | **316,049** | **299,818** |
| BW FFPR + Zopfli | 688,732 | 537,982 | 2,436,663 | 15,756 | 743,693 | 724,057 |
| BW FFPR + Brotli | 531,399 | 374,743 | 1,903,320 | 9,569 | 574,796 | 527,847 |
| **Indexed color — low palettes** | | | | | | |
| Indexed 5 colors + colored JBIG2 + Zopfli native | 187,455 | 272,001 | 4,104,794 | **15,776** | 345,953 | 1,614,891 |
| Indexed 5 colors + colored JBIG2 + Brotli native | **182,638** | **269,847** | 4,003,340 | 15,923 | 338,380 | 1,363,753 |
| Indexed 5 colors + Zopfli | 187,455 | 578,965 | 3,769,149 | 28,012 | 359,179 | 1,683,086 |
| Indexed 5 colors + Brotli | **182,638** | 413,380 | **3,277,883** | 22,083 | **331,829** | **1,334,257** |
| Indexed 16 colors + Zopfli | 187,455 | 578,965 | 6,116,675 | 44,809 | 459,802 | 2,122,383 |
| Indexed 16 colors + Brotli | **182,638** | **413,380** | **5,456,331** | **36,511** | **416,980** | **1,712,326** |
| Indexed 64 colors + Zopfli | 187,455 | 578,965 | 9,338,434 | 63,305 | 578,231 | 2,774,044 |
| Indexed 64 colors + Brotli | **182,638** | **413,380** | **8,276,637** | **52,556** | **513,744** | **2,247,520** |
| Color FFPR; indexed 5 colors + colored JBIG2; optimized residual streams | **299,497** | **231,619** | 3,817,106 | **9,390** | **337,274** | **394,165** |
| Color FFPR; indexed 5 colors + Zopfli | 688,882 | 538,257 | 4,501,917 | 21,713 | 783,305 | 912,904 |
| Color FFPR; indexed 5 colors + Brotli | 531,549 | 375,018 | **3,733,876** | 15,529 | 602,501 | 676,529 |
| Color FFPR; indexed 16 colors + Zopfli | 688,882 | 538,257 | 7,213,825 | 39,624 | 818,742 | 1,071,002 |
| Color FFPR; indexed 16 colors + Brotli | **531,549** | **375,018** | **6,169,402** | **31,338** | **634,556** | **817,681** |
| Color FFPR; indexed 64 colors + Zopfli | 688,882 | 538,257 | 11,133,100 | 58,350 | 862,205 | 1,327,080 |
| Color FFPR; indexed 64 colors + Brotli | **531,549** | **375,018** | **9,679,562** | **47,405** | **661,335** | **991,656** |
| **Full color** | | | | | | |
| JPEG q50 + Zopfli native | 187,455 | 4,434,870 | 6,269,805 | **116,296** | 550,470 | 2,349,517 |
| JPEG q50 + Brotli native | **182,638** | **4,432,704** | **6,168,309** | 116,450 | **542,907** | **2,098,443** |
| JPEG2000 lossy r192 + Zopfli native | 187,455 | 1,253,676 | 3,626,725 | **139,068** | 538,601 | 2,483,638 |
| JPEG2000 lossy r192 + Brotli native | **182,638** | **1,251,510** | **3,525,229** | 139,222 | **531,038** | **2,232,564** |
| JPEG2000 lossless + Zopfli native | 187,455 | 19,100,317 | 56,343,268 | **569,368** | 1,813,182 | 8,926,081 |
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
**signed percentage change in measured complete saved PDF bytes**
from that baseline. Candidate byte counts are omitted here (§243);
exact counts remain in the frozen measurement manifests.

`Change (%) = 100 × (PNG-prediction bytes − baseline bytes) / baseline bytes`.
**Negative is smaller/better; positive is larger/worse.** Percentages
are rounded to two decimal places. Bold percentages mark displayed
negative reductions only—not a cross-document minimum. Exact ties and
changes that round to +0.00% are not bold.
Underlined Brotli labels flag its zero improvements in these 48 pairs, not
a universal claim that prediction is obsolete.

Source PDF, prepared pixels/palette, DPI, threshold, native-stream
compressor and save policy are unchanged within each pair. The ON path
uses the existing adaptive predictor-15 row selector (minimum absolute
signed-byte sum across None/Sub/Up/Average/Paeth), held fixed throughout;
these results do not test every possible row-filter selection strategy. These are
two actual separately saved PDFs, never an estimated size or a copied
control. The non-FFPR W-9 has no bitmap stage: its eight independently
measured ties are no-op sanity controls, not evidence of predictor savings.

### Enable PNG prediction — final PDF size change (%) versus prediction OFF

| Baseline combination | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images | Technical illustrations |
|---|---:|---:|---:|---:|---:|---:|
| BW + Zopfli | +0.00% | **-1.47%** | +1.41% | +3.41% | +0.13% | +0.29% |
| BW + <ins>Brotli</ins> | +0.00% | +28.30% | +6.14% | +24.23% | +1.22% | +1.67% |
| BW FFPR + Zopfli | **-5.63%** | **-1.58%** | **-4.54%** | +4.30% | **-5.68%** | **-1.82%** |
| BW FFPR + <ins>Brotli</ins> | +8.89% | +31.20% | +16.49% | +40.34% | +8.88% | +18.37% |
| Indexed 5 colors + Zopfli | +0.00% | **-1.47%** | +11.84% | +16.52% | +2.21% | +3.84% |
| Indexed 5 colors + <ins>Brotli</ins> | +0.00% | +28.28% | +20.84% | +28.67% | +4.65% | +8.01% |
| Color FFPR; indexed 5 colors + Zopfli | **-5.62%** | **-1.58%** | +13.94% | +19.09% | **-3.65%** | +0.56% |
| Color FFPR; indexed 5 colors + <ins>Brotli</ins> | +8.89% | +31.18% | +29.54% | +43.89% | +10.93% | +19.67% |
| Indexed 16 colors + Zopfli | +0.00% | **-1.47%** | +15.83% | +14.78% | +4.13% | +5.45% |
| Indexed 16 colors + <ins>Brotli</ins> | +0.00% | +28.28% | +22.67% | +29.30% | +9.44% | +12.13% |
| Color FFPR; indexed 16 colors + Zopfli | **-5.62%** | **-1.58%** | +17.19% | +16.46% | **-2.05%** | +5.22% |
| Color FFPR; indexed 16 colors + <ins>Brotli</ins> | +8.89% | +31.18% | +29.22% | +35.58% | +12.08% | +22.17% |
| Indexed 64 colors + Zopfli | +0.00% | **-1.47%** | +18.68% | +35.06% | +10.69% | +15.39% |
| Indexed 64 colors + <ins>Brotli</ins> | +0.00% | +28.28% | +25.84% | +46.34% | +17.94% | +24.16% |
| Color FFPR; indexed 64 colors + Zopfli | **-5.62%** | **-1.58%** | +23.62% | +38.51% | **-2.92%** | +1.29% |
| Color FFPR; indexed 64 colors + <ins>Brotli</ins> | +8.89% | +31.18% | +33.42% | +53.48% | +11.73% | +21.12% |

The table now covers **96 pairs**: BW/Otsu and 5/16/64-color palettes,
native-preserving and FFPR, with both general compressors. The 16/64-color
rows add coverage, not an exhaustive algorithm search at those palettes.
Source palettes can use fewer entries; the BW scan is intentionally
measured even when different palette limits produce identical samples.

- **Zopfli-Flate**: 18 smaller, 4 tied, 26 larger out of 48 measured pairs.
- **Brotli**: 0 smaller, 4 tied, 44 larger out of 48 measured pairs.

These counts apply only to this corpus/settings. No-image ties are sanity
controls, not image compression wins. The focused measurements below
are unchanged; four native 16/64-color cases reuse the very same measured
files now included in this expanded overview.

**Does prediction ever win overall?** With all measured same-fidelity
algorithms eligible, none of these 96 PNG candidates is uniquely smallest:
92 lose to another result; four merely tie on the image-free W-9. The
focused cases and earlier image-stream study also have no PNG winner.
Nevertheless, that earlier noisy-BW control shrinks with Brotli+prediction
from 83,432 to 81,018 bytes (-2.89%); JBIG2 still wins at 63,075 bytes.
This distinguishes improving one compressor from beating every competitor.
See the [earlier measured evidence](IMAGE_STREAM_COMPRESSION.md#what-these-sizes-show).

Reader eligibility changes the comparison. Excluding Brotli leaves eight
strict PNG wins among the current measured 16/64-color alternatives; those
groups do not exhaust layered-JBIG2 possibilities. Therefore this corpus
does not establish that PNG prediction is universally superseded. Details
and the proposed next **JBIG2 repeated-row prediction OFF/ON** experiment
are in [the experiment plan](COMPRESSION_EXPERIMENTS.md#proposed-next--jbig2-01-repeated-row-prediction-offon).
No algorithm or product option has been removed.

## FFPR residual compression — Zopfli versus Brotli baseline

**NATIVE-02 — designer §§245/246.** Every cell uses FFPR with the named
specialized image codec; columns describe the original input classes, not
retained native text. Encoded images, prepared samples, 300 DPI and save
settings are fixed. Only residual/native-stream compression changes:
**Brotli is the baseline; Zopfli is the treatment**. No image is re-encoded.

`Change (%) = 100 × (Zopfli bytes − Brotli bytes) / Brotli bytes`.
**Negative favors Zopfli; positive favors Brotli.** Cells show percentages
only, rounded to two decimal places. Bold marks displayed negative changes;
changes that round to +0.00% are not bold, even when the actual file is smaller.
Actual complete-file sizes are retained in the measured evidence and
[regression fixture](../tests/fixtures/ffpr_compressor_sizes.json).

### Replace Brotli with Zopfli for FFPR residual streams — final PDF size change (%)

| FFPR image encoding | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images | Technical illustrations |
|---|---:|---:|---:|---:|---:|---:|
| BW + JBIG2 | **-0.06%** | **-0.08%** | **-0.01%** | **-4.19%** | **-0.05%** | **-0.06%** |
| 5 colors + layered JBIG2 | **-0.09%** | **-0.11%** | +0.00% | **-1.84%** | **-0.06%** | **-0.06%** |
| Color + JPEG q50 | +0.00% | +0.00% | +0.00% | **-0.14%** | +0.00% | +0.00% |
| Color + JPEG2000 lossy r192 | **-0.02%** | **-0.01%** | **-0.01%** | **-0.13%** | **-0.01%** | **-0.01%** |
| Color + JPEG2000 lossless | +0.00% | +0.00% | +0.00% | **-0.03%** | +0.00% | +0.00% |

**Result: Brotli is larger in all 30 pairs, by 100–271 complete-file bytes.**
This includes every multipage source: six-page W-9, eleven-page TM972,
eight-page newspaper, nine-page research paper and twelve-page Kepler.
This is evidence for these FFPR recipes, not a theorem that Brotli always
loses on residual streams. The sources differ; this is not a page-count-only
experiment or a basis for an automatic page-count cutoff.

### Why Brotli is worse here

The byte accounting closes exactly in every pair. Encoded image bytes,
object/xref-container stream bytes and other stream bytes are unchanged.
The complete-file growth is the sum of:

- **166 bytes for our writer's Brotli extension declaration.** Metadata-only
  controls keep the Zopfli image AND native stream payloads byte-identical
  and add just that declaration. Both the one-page artwork and six-page W-9
  grow by exactly 166 bytes. The extension specification recommends it
  (**SHOULD**, not SHALL); this was the study's writer declaration policy,
  not an unavoidable 166-byte minimum imposed by the format. That policy
  stays fixed in these frozen results; new saves default OFF under §251.
- **One extra filter-name byte per native stream:** `/BrotliDecode` is one
  byte longer than `/FlateDecode`.
- **The actual native-payload difference and any extra `/Length` digits.**
  In BW/JPEG/JPEG2000 FFPR cases, only 35–245 decoded drawing-command bytes
  remain per document; Brotli's encoded payload is 1–7 bytes larger here.
  Many identical page drawing programs are deduplicated: the six-page W-9
  has ONE shared 43-byte program. More pages need not mean more compressible
  residual data. Five-color layered JBIG2 has more drawing commands and can
  favor either payload encoder, but its savings never repay the overhead.

For example, artwork/JBIG2 is **4,037 B with Brotli versus 3,868 B with
Zopfli**: 166 declaration + 1 filter-name + 2 payload bytes = **169 B**.
The six-page W-9/JBIG2 has that same 169-byte difference, despite six times
as many pages. In eight-page newspaper/layered-JBIG2, Brotli actually saves
**74 native-payload bytes**, but adds **174 syntax bytes**: the complete
PDF is still **100 B larger** (3,817,206 versus 3,817,106 B).

This is a small-stream and whole-PDF overhead effect, not worse compression
of the J* images: their encoded payloads are proven identical. No encoder or
format is guaranteed to win every input. These results favor Zopfli for
these FFPR residuals; no application setting/default changes in this benchmark.

The [shared per-stream saver](../pdf_minify/core/stream_compression.py)
explains the implementation boundary; the
[Brotli PDF extension, §4](https://pdfa.org/download-area/publications/pdf-extension-brotli.pdf) specifies
its declaration. The longer label Zopfli-Flate is unnecessary in tables:
**Zopfli** here always means standard FlateDecode data, not a second format.
See [the Zopfli project](https://github.com/google/zopfli#readme).

Evidence: `.tmp/compression-experiments/ffpr-brotli-zopfli-300dpi-20261017/`.
Thirty Brotli baselines are newly saved and pass the shared exact native,
image and all-page 72/300-DPI checks; thirty verified Zopfli files are reused
with their original provenance. Both metadata-only controls pass QPDF checks;
that does not certify Brotli decoding. No compute-time comparison is made.

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
| Preserve images + Zopfli native | 4,574,656 |
| Preserve images + Brotli native | **4,472,657** |
| JPEG q50 + Zopfli native | 6,269,805 |
| JPEG q50 + Brotli native | **6,168,309** |
| JPEG2000 lossy r192 + Zopfli native | 3,626,725 |
| JPEG2000 lossy r192 + Brotli native | **3,525,229** |
| JPEG2000 lossless + Zopfli native | 56,343,268 |
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
| Indexed + Zopfli | 28,012 | 44,809 | 63,305 |
| Indexed + Zopfli + PNG prediction | 32,639 | 51,430 | 85,501 |
| Indexed + Brotli | 22,083 | 36,511 | **52,556** |
| Indexed + Brotli + PNG prediction | 28,415 | 47,209 | 76,912 |
| Indexed + colored JBIG2 + Zopfli native | **15,776** | **34,468** | 71,263 |
| Indexed + colored JBIG2 + Brotli native | 15,923 | 34,594 | 71,312 |

### Mixed text/images — palette count

All nine GAN-paper pages at 300 DPI. Text, vectors and fonts remain native;
only the composed bitmap layer is palette-reduced.

| Algorithm combination | 5 colors | 16 colors | 64 colors |
|---|---:|---:|---:|
| Indexed + Zopfli | 359,179 | 459,802 | 578,231 |
| Indexed + Zopfli + PNG prediction | 367,102 | 478,813 | 640,060 |
| Indexed + Brotli | **331,829** | **416,980** | **513,744** |
| Indexed + Brotli + PNG prediction | 347,261 | 456,362 | 605,928 |
| Indexed + colored JBIG2 + Zopfli native | 345,953 | 467,614 | 643,874 |
| Indexed + colored JBIG2 + Brotli native | 338,380 | 460,017 | 636,143 |

### Scanned BW text — different source material

NACA TM972 (eleven pages) and NACA formulas (seven pages), 300 DPI/Otsu,
with native artwork retained if present. Typewritten scans and mathematical
print are distinct stress cases, not interchangeable evidence.

| Algorithm combination | NACA TM972 | NACA formulas |
|---|---:|---:|
| BW + Zopfli | 578,690 | 394,669 |
| BW + Zopfli + PNG prediction | 570,171 | 383,806 |
| BW + Brotli | 413,105 | 289,977 |
| BW + Brotli + PNG prediction | 530,018 | 357,859 |
| BW + JBIG2 + Zopfli native | 270,228 | 192,438 |
| BW + JBIG2 + Brotli native | **268,062** | **190,923** |

### Threshold sensitivity — three explicit BW transforms

The same complete `images.pdf`, 300 DPI, native artwork retained. Otsu and
Simple T180/T210 produce different pixels. Compare encoders within each
column, not the thresholds as though their output were visually identical.

| Algorithm combination | Otsu | Simple T180 | Simple T210 |
|---|---:|---:|---:|
| BW + Zopfli | 20,769 | 21,537 | 24,435 |
| BW + Zopfli + PNG prediction | 21,477 | 22,005 | 25,299 |
| BW + Brotli | 14,852 | 15,584 | 18,148 |
| BW + Brotli + PNG prediction | 18,450 | 18,878 | 22,415 |
| BW + JBIG2 + Zopfli native | **9,798** | **10,077** | **10,945** |
| BW + JBIG2 + Brotli native | 9,952 | 10,231 | 11,099 |

### Native-heavy files — fonts, drawings and container overhead

Preserve original encoded images without resampling. The W-9, Form 941 and
NASA Kepler paper expose different native-content burdens. These are whole
repository PDFs, not extracted pages or combined component estimates.

| Algorithm combination | W-9 / 6 pages | Form 941 / 3 pages | Kepler / 12 pages |
|---|---:|---:|---:|
| Preserve images + Classic Flate (reference) native | 188,447 | 872,512 | 2,188,983 |
| Preserve images + Zopfli native | 187,455 | 854,321 | 2,016,866 |
| Preserve images + Brotli native | **182,638** | **776,197** | **1,766,110** |

## Native/residual streams — measured effect versus Flate reference

Plan: **NATIVE-01**, [controlled experiments](COMPRESSION_EXPERIMENTS.md#native-01--nativeresidual-stream-recompression). One factor changes: standard level-9 Flate versus the named optimized
**native/residual-stream encoder**. Encoded image streams, decoded native
drawing, preparation, ID framing and final writer settings stay fixed.
Classic Flate is a controlled reference, not a restored product option.
These seven rows isolate the five specialized FFPR residual cases plus
two native-content controls, not another image-codec cross-product.

### Measured reference bytes — standard Flate native/residual streams

Each row names the candidate; these cells are its **measured Flate-reference
complete-file bytes**. The two preserve-images controls share the same
already measured Flate reference for each source.

| Candidate combination | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images | Technical illustrations |
|---|---:|---:|---:|---:|---:|---:|
| Preserve images + Zopfli native | 188,447 | 367,630 | 4,641,959 | 1,493,125 | 502,235 | 2,188,983 |
| Preserve images + Brotli native | 188,447 | 367,630 | 4,641,959 | 1,493,125 | 502,235 | 2,188,983 |
| BW FFPR + JBIG2; optimized residual streams | 297,872 | 229,520 | 1,199,049 | 3,868 | 316,049 | 299,818 |
| Color FFPR; indexed 5 colors + colored JBIG2; optimized residual streams | 299,531 | 231,619 | 3,817,113 | 9,390 | 337,274 | 394,165 |
| Color FFPR + JPEG q50; optimized residual streams | 5,674,560 | 4,394,162 | 16,652,211 | 119,758 | 5,695,628 | 6,225,232 |
| Color FFPR + JPEG2000 lossy r192; optimized residual streams | 790,654 | 1,212,968 | 2,322,153 | 132,374 | 1,186,046 | 1,581,087 |
| Color FFPR + JPEG2000 lossless; optimized residual streams | 26,977,014 | 19,059,609 | 127,518,137 | 631,376 | 27,091,577 | 32,340,923 |

### Measured candidate bytes and change from that reference

Each cell is **measured candidate complete-file bytes** plus
`100 × (candidate − reference) / reference`. Negative is smaller/better.
Bold bytes mean no larger than its own reference, including ties.
Rounding is to two decimal places; tiny byte differences can round to
+0.00%, so the exact reference and candidate counts remain visible.

| Candidate combination | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images | Technical illustrations |
|---|---:|---:|---:|---:|---:|---:|
| Preserve images + Zopfli native | **187,455** (-0.53%) | **366,695** (-0.25%) | **4,574,656** (-1.45%) | **1,492,980** (-0.01%) | **491,510** (-2.14%) | **2,016,866** (-7.86%) |
| Preserve images + Brotli native | **182,638** (-3.08%) | **364,519** (-0.85%) | **4,472,657** (-3.65%) | 1,493,126 (+0.00%) | **483,963** (-3.64%) | **1,766,110** (-19.32%) |
| BW FFPR + JBIG2; optimized residual streams | **297,872** (+0.00%) | **229,520** (+0.00%) | **1,199,049** (+0.00%) | **3,868** (+0.00%) | **316,049** (+0.00%) | **299,818** (+0.00%) |
| Color FFPR; indexed 5 colors + colored JBIG2; optimized residual streams | **299,497** (-0.01%) | **231,619** (+0.00%) | **3,817,106** (+0.00%) | **9,390** (+0.00%) | **337,274** (+0.00%) | **394,165** (+0.00%) |
| Color FFPR + JPEG q50; optimized residual streams | **5,674,560** (+0.00%) | **4,394,162** (+0.00%) | **16,652,211** (+0.00%) | **119,758** (+0.00%) | **5,695,628** (+0.00%) | **6,225,232** (+0.00%) |
| Color FFPR + JPEG2000 lossy r192; optimized residual streams | **790,654** (+0.00%) | **1,212,968** (+0.00%) | **2,322,153** (+0.00%) | **132,374** (+0.00%) | **1,186,046** (+0.00%) | **1,581,087** (+0.00%) |
| Color FFPR + JPEG2000 lossless; optimized residual streams | **26,977,014** (+0.00%) | **19,059,609** (+0.00%) | **127,518,137** (+0.00%) | **631,376** (+0.00%) | **27,091,577** (+0.00%) | **32,340,923** (+0.00%) |

Across the **30 FFPR pairs**, complete-file byte changes range from **-34 B** to **+0 B**: **2 smaller, 28 tied, 0 larger**. These are actual final-file differences, not residual-payload estimates. The 12 native-preserving controls give **11 smaller, 0 tied, 1 larger**; the largest growth is **+1 B**. They retain much more content to recompress; the table measures that
contrast. Do not generalize these settings to
every PDF. Brotli still requires a supporting reader.

## What the measurements establish

- Five-color artwork: colored JBIG2 + Zopfli-native is **15,776 B**, versus **22,083 B** for shared Brotli without prediction. The complete mixed-paper counterparts are **345,953 B** and **331,829 B**. Representation/content changes the comparison.
- On the eleven-page **CCITT** NACA TM972 scan, BW/JBIG2 + Zopfli-native is **270,228 B**, versus **413,105 B** for shared Brotli at identical prepared BW pixels. The unresampled Zopfli control is **366,695 B** and the original is **374,461 B**. The measured JBIG2 recipe is **27.84% smaller** than that original; this is not a universal ranking.
- Crater Lake's native-preserving JPEG q50 + Zopfli-native is **6,269,805 B**; its full-page JPEG counterpart is **16,652,211 B**. Both target 300 DPI, but FFPR rasterizes text/vectors: their sizes are not equal-fidelity codec scores.
- The [PNG-prediction table](#png-prediction--measured-effect-versus-baseline) shows **96 six-document pairs**. Four focused palette cases now reuse those same outputs; six other focused pairs remain outside this table. The [native/residual A/B experiment](#nativeresidual-streams--measured-effect-versus-flate-reference) holds encoded images fixed and reports **42 separate Flate-reference comparisons**.
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

The representative inventory is **50 combinations × six PDFs = 300 verified measurements**: **34 baseline rows / 204 sizes** plus **16 PNG-effect rows / 96 percentages**. Focused tables still display 87 sizes. NATIVE-01 displays 42 reference and 42 candidate sizes; NATIVE-02 adds 30 FFPR compressor effects from separately measured Brotli baselines. That is **375 displayed byte-count cells plus 126 percentage-only cells = 501 result cells**, supported by **392 distinct actual complete files**, with no rejected or unmeasured cells. The original selected study supplied 252 files; PNG coverage adds 80 newly saved files and reuses 16 focused outputs, while NATIVE-01 adds 30 reference files and reuses its candidates/controls. NATIVE-02 adds 30 Brotli files and reuses 30 Zopfli files; two metadata-only diagnostic outputs are additional, not ranked cases. No-image treatments are independently saved, not filled by copying a control.

The complete fresh post-B114 measurement superset remains immutable under `.tmp/integrated-compression/post-b114-300dpi-20261016/`: 252 overview and 62 focused outputs, all saved using one repaired compositor. Its `identity.json` pins source, tool, environment and saver/verifier/driver hashes; `refresh.py`, `overview.py`, `scenarios.py`, scoped job manifests and `complete.json` preserve the actual full measurement scope.

`image-streams.py` also freezes the measured bitmap driver. Subsequent runner
changes select only retained variants and remove an unused JSON percentage
that incorrectly assumed the first variant was always Classic Flate. This
changes future scope/metadata, not the shared pixel/encoding/save operations;
the current publication retains the actual measured implementation hashes.

Designer §§236/237's reduced publication is a hash-verified **selection from that measured superset**, not a claim that it was re-encoded under the later row-selection code. `selected-237/metrics.json` records the exact selected paths, original per-output provenance, frozen-superset hashes and new selector scope. The redundant bitmap combinations are removed consistently from every table, not kept as supplemental references. Sixty-two superseded files stay archived but are not current analysis cells. No original source, saved PDF, measured byte count or strict import/resume gate is rewritten or relaxed.

The §242 extensions are frozen under `.tmp/compression-experiments/`: `png-palettes-300dpi-20261017/` and `native-residual-300dpi-20261017/`. Their identities retain the producing implementation, source/tool hashes, original imported records and a bounded compatibility proof: the earlier bitmap driver's only core difference is removal of an unused JSON percentage field. No encoder, preparation, saver or validator changed. Normal changed-code resume remains forbidden. Publication inputs, sources, complete output hashes, paired statistics and current Markdown are frozen separately under `.tmp/compression-experiments/publication-20261017/`. See [experiment plans](COMPRESSION_EXPERIMENTS.md).

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
nice -n 10 ./.venv/bin/python tools/bench_png_extension.py --label <png-label>
nice -n 10 ./.venv/bin/python tools/bench_residual_streams.py --label <native-label> --existing <selected-manifest>
```

Use `--resume` only for an unchanged interrupted run. Source, preparation,
output and implementation hashes gate reuse. Runners emit Markdown/JSON
evidence, not CSV. The desktop application is not launched for this study.

NATIVE-02 is frozen under `.tmp/compression-experiments/ffpr-brotli-zopfli-300dpi-20261017/`: source/producer identities, actual paired files/sizes/hashes, exact verification, stream accounting and metadata-only controls. Its data-only publication and per-pair causal byte audit are recorded in `.tmp/compression-experiments/ffpr-brotli-zopfli-publication-20261017/`. Existing encoding-source hashes, packages and binaries match the producing study; changed reporting helpers are not relabeled as historical encoders.

The PNG-only presentation split is recorded under `.tmp/png-prediction-review-20261016/`: the before/after Markdown, frozen formatter/publisher sources, original measurement-manifest hash and exact PNG/plain output paths and hashes. No measurement or original provenance is rewritten; current formatter code is not claimed as the encoding implementation.

## Reader support

QPDF 12.2.0 syntax checks pass all **215 selected ordinary-format outputs**; the original **147 selected Brotli outputs**, plus **30 new NATIVE-02 Brotli baselines**, are excluded from that unsupported reader check, not certified by it.

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
row pruning then passed 605. The PNG-only split stage passed **635 tests**, with no expected failures.
Current controlled-experiment regressions, complete-suite results, actual
save smoke tests and publication audits are recorded in [TEST_PLAN.md](TEST_PLAN.md).
All published bytes, actual output hashes, tied bold minima and source
descriptors are independently audited. This headless study does not launch
the desktop application or imply designer acceptance.
