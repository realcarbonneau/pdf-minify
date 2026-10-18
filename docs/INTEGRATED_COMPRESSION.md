# Integrated compression — complete-PDF sizes at 300 DPI

Designer §§210–214/220–259; TODO §§226–256. This is the primary integrated
size analysis, replacing the earlier mixed-DPI overview. Measurements and
verification: 2026-10-16–17 (America/New_York).

**Declaration policy: OFF.** The fixed-encoder study's **177 integrated Brotli outputs** were
re-encoded and actually saved/measured under the current default. The broader
§254 rerun also refreshes **44 supporting bitmap and eight native outputs**,
including plain/PNG and levels 9/11. No number is an estimated metadata
subtraction. Original declaration-ON files remain immutable historical evidence;
the optional **(Compatibility)** declaration is not enabled in current tables.

**Current selection (§258).** The overview has **19 recipes × six complete PDFs = 114 measured sizes**. The separate Zopfli/Brotli binary reference covers the same 19 recipes; PNG prediction retains its **96 fixed-encoder pairs**, and NATIVE-01 retains **42 pairs**. The new saves reuse verified post-B114 preparations; the 392-file fixed-encoder publication remains unchanged. The BW representative is the eleven-page CCITT NACA TM972 scan, not the already-JBIG2 JFK regression fixture. B114 is worker-verified, not designer-confirmed acceptance.

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
- Fixed-encoder controls pair packed BW/indexed images and native streams
  with the **same general compressor**. Their specialized J* comparisons
  change native/residual compression only. Keep these controlled alternatives
  separate from the main matrix's stream-selection policy.
- Percentage differences use **two decimal places**, computed from original
  measured bytes. Rounded zero is `+0.00%` and is never bold; it can hide a
  tiny actual change, so raw byte evidence remains authoritative.
- **PNG prediction** is reversible row prediction before the same image
  compressor, not a second image/codec. Its separate table compares each
  fixed encoder's own plain baseline, not the main matrix's policy.
- **Bold** is the minimum among combinations shown in that table within the
  **same PDF column and recipe/fidelity group**, including ties. Controlled
  treatments in separate effect tables can be smaller. Do not rank BW against color or native preservation
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
their labels (§232). In fixed-encoder reference labels, `native` identifies
the stream compressor, not the bitmap image codec.

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
after rasterization, mainly commands that position/draw the page images.
The historical fixed-control label **optimized residual streams** means
Zopfli for those remaining streams. It is confined to the supporting
experiment/reference data, not the new overview's policy or row labels.
JPEG/JPEG2000/JBIG2 encode images separately; the shared final writer
handles PDF object/xref packing independently.

## Overview — final complete-file bytes

Every row uses **Best (Zopfli/Brotli)** for native and eligible packed
BW/indexed streams. It keeps the smallest actual complete all-Zopfli,
all-Brotli or per-stream mixed save, without changing image codecs, quality, DPI,
prediction or J* payloads. Compatibility metadata is OFF; output can
require a Brotli-capable reader. This common policy is omitted from
row labels. The
[specialized binary experiment](#stream-compression--zopfli-versus-brotli-baseline)
owns the fixed-encoder comparison and its reference sizes.

Transformed packed-image rows use PNG prediction OFF; the unresampled
reference keeps its existing image decoding parameters.

The unresampled reference does not compose, resize or recolor images.
It preserves their samples and geometry; eligible lossless image streams
can be repacked, so it does not promise identical encoded image bytes.
It is a benchmark control, not the app's untouched Original view.
All other image recipes use 300 DPI. Original file sizes remain above.
Classic-Flate controls are retained in the specialized reference, not
this matrix.

One continuous table retains BW, indexed color and full-color dividers,
with native-preserving rows before FFPR. Bold minima compare the same
input and fidelity group only; palette counts and JPEG/JPX quality
targets remain distinct. A smaller encoding need not beat the original.

| Algorithm combination | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images | Technical illustrations |
|---|---:|---:|---:|---:|---:|---:|
| **Unresampled reference** | | | | | | |
| Unresampled reference | **182,485** | **364,347** | **4,455,585** | **913,416** | **450,454** | **1,607,127** |
| **Black and white (BW + Otsu)** | | | | | | |
| BW + JBIG2 | **182,485** | **267,896** | **1,622,205** | **9,761** | **300,346** | **1,106,489** |
| BW + packed samples | **182,485** | 413,126 | 1,747,688 | 14,678 | 304,701 | 1,127,095 |
| BW FFPR + JBIG2 | **297,872** | **229,520** | **1,199,049** | **3,868** | **316,049** | **299,818** |
| BW FFPR + packed samples | 531,332 | 374,750 | 1,903,288 | 9,417 | 574,780 | 527,882 |
| **Indexed color — low palettes** | | | | | | |
| Indexed 5 colors + colored JBIG2 | **182,485** | **269,681** | 4,003,018 | **15,737** | 338,209 | 1,363,580 |
| Indexed 5 colors | **182,485** | 413,401 | **3,277,697** | 21,909 | **331,692** | **1,334,237** |
| Indexed 16 colors | **182,485** | **413,401** | **5,456,145** | **36,337** | **416,843** | **1,712,306** |
| Indexed 64 colors | **182,485** | **413,401** | **8,276,451** | **52,382** | **513,607** | **2,247,500** |
| Color FFPR; indexed 5 colors + colored JBIG2 | **299,497** | **231,619** | 3,817,040 | **9,390** | **337,263** | **394,148** |
| Color FFPR; indexed 5 colors | 531,482 | 375,025 | **3,733,844** | 15,377 | 602,485 | 676,564 |
| Color FFPR; indexed 16 colors | **531,482** | **375,025** | **6,169,370** | **31,186** | **634,540** | **817,716** |
| Color FFPR; indexed 64 colors | **531,482** | **375,025** | **9,679,530** | **47,253** | **661,319** | **991,691** |
| **Full color** | | | | | | |
| JPEG q50 | **182,485** | **4,432,538** | **6,167,987** | **116,259** | **542,736** | **2,098,270** |
| JPEG2000 lossy r192 | **182,485** | **1,251,344** | **3,524,907** | **139,031** | **530,867** | **2,232,391** |
| JPEG2000 lossless | **182,485** | **19,097,985** | **56,241,450** | **569,331** | **1,805,448** | **8,674,834** |
| Color FFPR + JPEG q50 | **5,674,560** | **4,394,162** | **16,652,211** | **119,758** | **5,695,628** | **6,225,232** |
| Color FFPR + JPEG2000 lossy r192 | **790,654** | **1,212,968** | **2,322,153** | **132,374** | **1,186,046** | **1,581,087** |
| Color FFPR + JPEG2000 lossless | **26,977,014** | **19,059,609** | **127,518,137** | **631,376** | **27,091,577** | **32,340,923** |

## PNG prediction — measured effect versus baseline

### Results and decision tree

**Current measured result:** prediction reduces **0 of 48 Brotli** files
and **18 of 48 Zopfli** files. With every measured same-fidelity algorithm
eligible, none of the 96 PNG candidates is uniquely smallest. Reader limits
matter: excluding Brotli leaves eight strict wins in the measured 16/64-color
alternatives, not an exhaustive layered-JBIG2 search.

Use the **prepared output image**, not its original file type, to branch:

```text
Prepared output image
├─ No bitmap rows → no-op; no prediction decision.
├─ JPEG / JPEG2000 / JBIG2 → PNG prediction not applicable to that payload.
└─ Packed BW / indexed samples
   ├─ Brotli → prefer OFF in this corpus (0/48 reductions); see counterexample.
   ├─ Zopfli
   │  ├─ BW → test ON, especially scans and FFPR; not a guaranteed win.
   │  └─ Indexed → OFF first for color photos/artwork; test ON for
   │              scan/text-like content and mixed-content FFPR.
   └─ Best → keeps the chosen predictor; no automatic OFF/ON search.
```

**Counterexample:** the earlier noisy-BW Brotli control improves **-2.90%**
with prediction, although JBIG2 remains smaller. See the
[measured evidence](IMAGE_STREAM_COMPRESSION.md#what-these-sizes-show).
All current indexed-color photo/artwork PNG candidates grow; some
mixed-paper indexed FFPR candidates shrink with Zopfli. Encoder and actual
image content—not palette count or FFPR alone—determine the measured outcome.

This is **benchmark guidance, not a new automatic app policy** (§259).
For a new input, a firm choice requires actual complete-PDF OFF/ON
measurements with other factors and reader eligibility fixed. Best currently
preserves the predictor supplied by the recipe; these results do not measure
a joint Best-plus-predictor search. Native text/vector streams do not use
image-row prediction.

### Method and interpretation

Only **image-row PNG prediction** changes within each pair. The row
names its own **fixed-encoder plain baseline**, retained in the specialized
reference controls below—not a Best result from the new overview.
No denominator or PNG measurement changes. Each cell shows the
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
| BW + <ins>Brotli</ins> | +0.00% | +28.31% | +6.14% | +24.50% | +1.22% | +1.67% |
| BW FFPR + Zopfli | **-5.63%** | **-1.58%** | **-4.54%** | +4.30% | **-5.68%** | **-1.82%** |
| BW FFPR + <ins>Brotli</ins> | +8.90% | +31.21% | +16.49% | +41.05% | +8.88% | +18.37% |
| Indexed 5 colors + Zopfli | +0.00% | **-1.47%** | +11.84% | +16.52% | +2.21% | +3.84% |
| Indexed 5 colors + <ins>Brotli</ins> | +0.00% | +28.29% | +20.84% | +28.89% | +4.65% | +8.01% |
| Color FFPR; indexed 5 colors + Zopfli | **-5.62%** | **-1.58%** | +13.94% | +19.09% | **-3.65%** | +0.56% |
| Color FFPR; indexed 5 colors + <ins>Brotli</ins> | +8.89% | +31.19% | +29.54% | +44.36% | +10.93% | +19.68% |
| Indexed 16 colors + Zopfli | +0.00% | **-1.47%** | +15.83% | +14.78% | +4.13% | +5.45% |
| Indexed 16 colors + <ins>Brotli</ins> | +0.00% | +28.29% | +22.67% | +29.43% | +9.45% | +12.13% |
| Color FFPR; indexed 16 colors + Zopfli | **-5.62%** | **-1.58%** | +17.19% | +16.46% | **-2.05%** | +5.22% |
| Color FFPR; indexed 16 colors + <ins>Brotli</ins> | +8.89% | +31.19% | +29.22% | +35.77% | +12.08% | +22.17% |
| Indexed 64 colors + Zopfli | +0.00% | **-1.47%** | +18.68% | +35.06% | +10.69% | +15.39% |
| Indexed 64 colors + <ins>Brotli</ins> | +0.00% | +28.29% | +25.84% | +46.49% | +17.95% | +24.17% |
| Color FFPR; indexed 64 colors + Zopfli | **-5.62%** | **-1.58%** | +23.62% | +38.51% | **-2.92%** | +1.29% |
| Color FFPR; indexed 64 colors + <ins>Brotli</ins> | +8.89% | +31.19% | +33.42% | +53.67% | +11.74% | +21.13% |

The table now covers **96 pairs**: BW/Otsu and 5/16/64-color palettes,
native-preserving and FFPR, with both general compressors. The 16/64-color
rows add coverage, not an exhaustive algorithm search at those palettes.
Source palettes can use fewer entries; the BW scan is intentionally
measured even when different palette limits produce identical samples.

- **Zopfli-Flate**: 18 smaller, 4 tied, 26 larger out of 48 measured pairs.
- **Brotli**: 0 smaller, 4 tied, 44 larger out of 48 measured pairs.

These counts apply only to this corpus/settings. No-image ties are sanity
controls, not image compression wins. The focused recipes below are retained,
with every Brotli cell also refreshed; four native 16/64-color cases reuse the very same measured
files retained in the fixed-encoder controls.

**Does prediction ever win overall?** In the fixed-encoder study, with all
measured same-fidelity algorithms eligible, none of these 96 PNG candidates is uniquely smallest:
92 lose to another result; four merely tie on the image-free W-9. The
focused cases and earlier image-stream study also have no PNG winner.
Nevertheless, that earlier noisy-BW control shrinks with Brotli+prediction
from 83,266 to 80,852 bytes (-2.90%); JBIG2 still wins at 63,075 bytes.
This distinguishes improving one compressor from beating every competitor.
See the [earlier measured evidence](IMAGE_STREAM_COMPRESSION.md#what-these-sizes-show).

Reader eligibility changes the comparison. Excluding Brotli leaves eight
strict PNG wins among the current measured 16/64-color alternatives; those
groups do not exhaust layered-JBIG2 possibilities. Therefore this corpus
does not establish that PNG prediction is universally superseded. Details
and the proposed next **JBIG2 repeated-row prediction OFF/ON** experiment
are in [the experiment plan](COMPRESSION_EXPERIMENTS.md#proposed-next--jbig2-01-repeated-row-prediction-offon).
No algorithm or product option has been removed.

<a id="ffpr-residual-compression--zopfli-versus-brotli-baseline"></a>

## Stream compression — Zopfli versus Brotli baseline

**Expanded binary reference (§258).** Brotli is the baseline and Zopfli
the treatment for all 19 overview recipes / **114 pairs**. Source,
prepared samples/palette, DPI, threshold/quality, native content, ID
framing, writer and declaration-OFF setting stay fixed. For packed
BW/indexed rows, this single general-encoder factor changes both image
and native streams. For J* and original-image references, only native/
residual streams change; their encoded image payloads stay identical.
Do not confuse either fixed-policy side with the overview's Best output.

In particular, the original-image fixed control preserves encoded images;
the main unresampled Best reference may also repack eligible image
streams. These historical controls are not homogeneous Best candidates.

`Change (%) = 100 × (Zopfli bytes − Brotli bytes) / Brotli bytes`.
**Negative favors Zopfli; positive favors Brotli.** Cells show only
two-decimal measured full-file changes. Bold marks displayed negatives;
rounded +0.00% is never bold. Exact baseline/treatment sizes are retained
in the always-visible reference table and measured evidence below.

### Replace Brotli with Zopfli — final PDF size change (%)

| Image recipe / reference | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images | Technical illustrations |
|---|---:|---:|---:|---:|---:|---:|
| **Unresampled reference** | | | | | | |
| Unresampled reference | +2.72% | +0.64% | +2.28% | +0.00% | +1.59% | +14.21% |
| **Black and white (BW + Otsu)** | | | | | | |
| BW + JBIG2 | +2.72% | +0.87% | +6.27% | +0.12% | +2.57% | +22.71% |
| BW + packed samples | +2.72% | +40.14% | +12.91% | +41.42% | +6.10% | +26.36% |
| BW FFPR + JBIG2 | +0.00% | **-0.01%** | +0.00% | **-0.08%** | +0.00% | +0.00% |
| BW FFPR + packed samples | +29.65% | +43.62% | +28.03% | +67.56% | +29.42% | +37.21% |
| **Indexed color — low palettes** | | | | | | |
| Indexed 5 colors + colored JBIG2 | +2.72% | +0.86% | +2.54% | +0.12% | +2.29% | +18.43% |
| Indexed 5 colors | +2.72% | +40.11% | +14.99% | +27.81% | +8.30% | +26.16% |
| Indexed 16 colors | +2.72% | +40.11% | +12.11% | +23.29% | +10.31% | +23.96% |
| Indexed 64 colors | +2.72% | +40.11% | +12.83% | +20.83% | +12.59% | +23.44% |
| Color FFPR; indexed 5 colors + colored JBIG2 | **-0.04%** | **-0.04%** | +0.00% | **-0.11%** | **-0.01%** | **-0.02%** |
| Color FFPR; indexed 5 colors | +29.64% | +43.59% | +20.57% | +41.33% | +30.04% | +34.97% |
| Color FFPR; indexed 16 colors | +29.64% | +43.59% | +16.93% | +27.11% | +29.06% | +31.01% |
| Color FFPR; indexed 64 colors | +29.64% | +43.59% | +15.02% | +23.52% | +30.41% | +33.85% |
| **Full color** | | | | | | |
| JPEG q50 | +2.72% | +0.05% | +1.65% | +0.01% | +1.42% | +11.97% |
| JPEG2000 lossy r192 | +2.72% | +0.19% | +2.88% | +0.01% | +1.46% | +11.25% |
| JPEG2000 lossless | +2.72% | +0.01% | +0.18% | +0.00% | +0.43% | +2.90% |
| Color FFPR + JPEG q50 | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% |
| Color FFPR + JPEG2000 lossy r192 | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% |
| Color FFPR + JPEG2000 lossless | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% |

### FFPR/J* subset — unchanged NATIVE-02 findings

The five FFPR/J* recipes above are the original **30-pair NATIVE-02**
experiment (§§245/246). Their results and causal accounting remain
unchanged; the statements in this subsection refer to those 30 pairs,
not every row of the expanded reference.

**Result with declaration OFF: Brotli is larger in 29 pairs by 2–105 bytes,
and smaller in one pair by 66 bytes; there are no exact ties.** The win is
the eight-page newspaper with five-color layered JBIG2. Most differences
round to +0.00% at the approved two decimals, including that Brotli win;
the actual file counts remain authoritative. These sources differ, so this
is not a page-count-only experiment or a basis for a page-count cutoff.

### Why Brotli can still be larger for the FFPR/J* subset

The byte accounting closes exactly in every pair. Encoded image bytes,
object/xref-container stream bytes and other stream bytes are unchanged.
There is **no Brotli declaration cost in these results**. The complete-file
difference is the sum of:

- **One extra filter-name byte per native stream:** `/BrotliDecode` is one
  byte longer than `/FlateDecode`.
- **The actual native-payload difference and any extra `/Length` digits.**
  In BW/JPEG/JPEG2000 FFPR cases, only 35–245 decoded drawing-command bytes
  remain per document; Brotli's encoded payload is 1–7 bytes larger here.
  Many identical page drawing programs are deduplicated: the six-page W-9
  has ONE shared 43-byte program. More pages need not mean more compressible
  residual data. Five-color layered JBIG2 has more drawing commands and can
  favor either payload encoder; the newspaper's savings now exceed its
  remaining syntax overhead.

For example, artwork/JBIG2 is **3,871 B with Brotli versus 3,868 B with
Zopfli**: 1 filter-name + 2 payload bytes = **3 B**.
The six-page W-9/JBIG2 has that same 3-byte difference, despite six times
as many pages. In eight-page newspaper/layered-JBIG2, Brotli actually saves
**74 native-payload bytes**, but adds **8 syntax bytes**: the complete
PDF is now **66 B smaller** (3,817,040 versus 3,817,106 B).

This is a small-stream and whole-PDF overhead effect, not worse compression
of the J* images: their encoded payloads are proven identical. No encoder or
format is guaranteed to win every input. These results favor Zopfli for
most of these tiny FFPR residuals, with the measured layered-color exception;
no application setting/default changes follow from this benchmark.

The [shared per-stream saver](../pdf_minify/core/stream_compression.py)
explains the implementation boundary; the
[Brotli PDF extension, §4](https://pdfa.org/download-area/publications/pdf-extension-brotli.pdf) specifies
its declaration. The longer label Zopfli-Flate is unnecessary in tables:
**Zopfli** here always means standard FlateDecode data, not a second format.
See [the Zopfli project](https://github.com/google/zopfli#readme).

Current evidence: `.tmp/compression-experiments/brotli-default-off-publication-20261017/`.
Thirty Brotli baselines are actually re-encoded, saved and measured with
declaration OFF; thirty verified Zopfli files retain their original provenance.
Unchanged exact rendered graphs and image payloads preserve the earlier
all-page 72/300-DPI proof without repeating rasterization. The older declared
study and metadata-only controls remain historical diagnostics, not current
table entries. No compute-time comparison or new reader certification is made.

### Fixed-encoder controls — measured final PDF bytes

These are the relocated fixed-policy alternatives, not additional main
matrix choices. PNG OFF/ON calculations keep these encoder-specific
plain baselines. The Classic-Flate reference remains a control only.

| Fixed-policy combination | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images | Technical illustrations |
|---|---:|---:|---:|---:|---:|---:|
| Preserve images + Classic Flate (reference) native | 188,447 | 367,630 | 4,641,959 | 1,493,125 | 502,235 | 2,188,983 |
| Preserve images + Zopfli native | 187,455 | 366,695 | 4,574,656 | 1,492,980 | 491,510 | 2,016,866 |
| Preserve images + Brotli native | **182,487** | **364,353** | **4,472,491** | **1,492,960** | **483,797** | **1,765,944** |
| BW + JBIG2 + Zopfli native | 187,455 | 270,228 | 1,724,023 | 9,798 | 308,080 | 1,357,736 |
| BW + JBIG2 + Brotli native | **182,487** | **267,896** | **1,622,361** | **9,786** | **300,351** | **1,106,496** |
| BW + Zopfli | 187,455 | 578,690 | 1,973,320 | 20,769 | 323,270 | 1,424,063 |
| BW + Brotli | **182,487** | 412,939 | 1,747,708 | 14,686 | 304,672 | 1,126,949 |
| BW FFPR + JBIG2; optimized residual streams | **297,872** | **229,520** | **1,199,049** | **3,868** | **316,049** | **299,818** |
| BW FFPR + JBIG2 + Brotli residual streams | 297,875 | 229,534 | 1,199,051 | 3,871 | 316,052 | 299,821 |
| BW FFPR + Zopfli | 688,732 | 537,982 | 2,436,663 | 15,756 | 743,693 | 724,057 |
| BW FFPR + Brotli | 531,233 | 374,577 | 1,903,154 | 9,403 | 574,630 | 527,681 |
| Indexed 5 colors + colored JBIG2 + Zopfli native | 187,455 | 272,001 | 4,104,794 | 15,776 | 345,953 | 1,614,891 |
| Indexed 5 colors + colored JBIG2 + Brotli native | **182,487** | **269,681** | 4,003,174 | **15,757** | 338,214 | 1,363,587 |
| Indexed 5 colors + Zopfli | 187,455 | 578,965 | 3,769,149 | 28,012 | 359,179 | 1,683,086 |
| Indexed 5 colors + Brotli | **182,487** | 413,214 | **3,277,717** | 21,917 | **331,663** | **1,334,091** |
| Indexed 16 colors + Zopfli | 187,455 | 578,965 | 6,116,675 | 44,809 | 459,802 | 2,122,383 |
| Indexed 16 colors + Brotli | **182,487** | **413,214** | **5,456,165** | **36,345** | **416,814** | **1,712,160** |
| Indexed 64 colors + Zopfli | 187,455 | 578,965 | 9,338,434 | 63,305 | 578,231 | 2,774,044 |
| Indexed 64 colors + Brotli | **182,487** | **413,214** | **8,276,471** | **52,390** | **513,578** | **2,247,354** |
| Color FFPR; indexed 5 colors + colored JBIG2; optimized residual streams | **299,497** | **231,619** | 3,817,106 | **9,390** | **337,274** | **394,165** |
| Color FFPR; indexed 5 colors + colored JBIG2 + Brotli residual streams | 299,602 | 231,716 | 3,817,040 | 9,400 | 337,306 | 394,241 |
| Color FFPR; indexed 5 colors + Zopfli | 688,882 | 538,257 | 4,501,917 | 21,713 | 783,305 | 912,904 |
| Color FFPR; indexed 5 colors + Brotli | 531,383 | 374,852 | **3,733,710** | 15,363 | 602,335 | 676,363 |
| Color FFPR; indexed 16 colors + Zopfli | 688,882 | 538,257 | 7,213,825 | 39,624 | 818,742 | 1,071,002 |
| Color FFPR; indexed 16 colors + Brotli | **531,383** | **374,852** | **6,169,236** | **31,172** | **634,390** | **817,515** |
| Color FFPR; indexed 64 colors + Zopfli | 688,882 | 538,257 | 11,133,100 | 58,350 | 862,205 | 1,327,080 |
| Color FFPR; indexed 64 colors + Brotli | **531,383** | **374,852** | **9,679,396** | **47,239** | **661,169** | **991,490** |
| JPEG q50 + Zopfli native | 187,455 | 4,434,870 | 6,269,805 | 116,296 | 550,470 | 2,349,517 |
| JPEG q50 + Brotli native | **182,487** | **4,432,538** | **6,168,143** | **116,284** | **542,741** | **2,098,277** |
| JPEG2000 lossy r192 + Zopfli native | 187,455 | 1,253,676 | 3,626,725 | 139,068 | 538,601 | 2,483,638 |
| JPEG2000 lossy r192 + Brotli native | **182,487** | **1,251,344** | **3,525,063** | **139,056** | **530,872** | **2,232,398** |
| JPEG2000 lossless + Zopfli native | 187,455 | 19,100,317 | 56,343,268 | 569,368 | 1,813,182 | 8,926,081 |
| JPEG2000 lossless + Brotli native | **182,487** | **19,097,985** | **56,241,606** | **569,356** | **1,805,453** | **8,674,841** |
| Color FFPR + JPEG q50; optimized residual streams | **5,674,560** | **4,394,162** | **16,652,211** | **119,758** | **5,695,628** | **6,225,232** |
| Color FFPR + JPEG q50 + Brotli residual streams | 5,674,563 | 4,394,176 | 16,652,213 | 119,761 | 5,695,631 | 6,225,235 |
| Color FFPR + JPEG2000 lossy r192; optimized residual streams | **790,654** | **1,212,968** | **2,322,153** | **132,374** | **1,186,046** | **1,581,087** |
| Color FFPR + JPEG2000 lossy r192 + Brotli residual streams | 790,657 | 1,212,982 | 2,322,155 | 132,377 | 1,186,049 | 1,581,090 |
| Color FFPR + JPEG2000 lossless; optimized residual streams | **26,977,014** | **19,059,609** | **127,518,137** | **631,376** | **27,091,577** | **32,340,923** |
| Color FFPR + JPEG2000 lossless + Brotli residual streams | 26,977,017 | 19,059,623 | 127,518,139 | 631,379 | 27,091,580 | 32,340,926 |

## Focused scenarios

Every cell below is a fixed-encoder supporting control, not a Best result
from the new overview. Cells reuse their original measured files where applicable. Only the settings named in the columns change. All
transformed cases remain at 300 DPI; lower-DPI variations are not repeated.

### Color photography — native preservation and full-page color

All eight Crater Lake pages. Preserve-images retains original image bytes;
the other rows target 300 DPI. Native and FFPR rows remain separate fidelity
groups. These are full-color cases, not five-color or BW photo approximations.

| Algorithm combination | Color photos |
|---|---:|
| Preserve images + Classic Flate (reference) native | 4,641,959 |
| Preserve images + Zopfli native | 4,574,656 |
| Preserve images + Brotli native | **4,472,491** |
| JPEG q50 + Zopfli native | 6,269,805 |
| JPEG q50 + Brotli native | **6,168,143** |
| JPEG2000 lossy r192 + Zopfli native | 3,626,725 |
| JPEG2000 lossy r192 + Brotli native | **3,525,063** |
| JPEG2000 lossless + Zopfli native | 56,343,268 |
| JPEG2000 lossless + Brotli native | **56,241,606** |
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
| Indexed + Brotli | 21,917 | 36,345 | **52,390** |
| Indexed + Brotli + PNG prediction | 28,249 | 47,043 | 76,746 |
| Indexed + colored JBIG2 + Zopfli native | 15,776 | 34,468 | 71,263 |
| Indexed + colored JBIG2 + Brotli native | **15,757** | **34,428** | 71,146 |

### Mixed text/images — palette count

All nine GAN-paper pages at 300 DPI. Text, vectors and fonts remain native;
only the composed bitmap layer is palette-reduced.

| Algorithm combination | 5 colors | 16 colors | 64 colors |
|---|---:|---:|---:|
| Indexed + Zopfli | 359,179 | 459,802 | 578,231 |
| Indexed + Zopfli + PNG prediction | 367,102 | 478,813 | 640,060 |
| Indexed + Brotli | **331,663** | **416,814** | **513,578** |
| Indexed + Brotli + PNG prediction | 347,095 | 456,196 | 605,762 |
| Indexed + colored JBIG2 + Zopfli native | 345,953 | 467,614 | 643,874 |
| Indexed + colored JBIG2 + Brotli native | 338,214 | 459,851 | 635,977 |

### Scanned BW text — different source material

NACA TM972 (eleven pages) and NACA formulas (seven pages), 300 DPI/Otsu,
with native artwork retained if present. Typewritten scans and mathematical
print are distinct stress cases, not interchangeable evidence.

| Algorithm combination | NACA TM972 | NACA formulas |
|---|---:|---:|
| BW + Zopfli | 578,690 | 394,669 |
| BW + Zopfli + PNG prediction | 570,171 | 383,806 |
| BW + Brotli | 412,939 | 289,811 |
| BW + Brotli + PNG prediction | 529,852 | 357,693 |
| BW + JBIG2 + Zopfli native | 270,228 | 192,438 |
| BW + JBIG2 + Brotli native | **267,896** | **190,757** |

### Threshold sensitivity — three explicit BW transforms

The same complete `images.pdf`, 300 DPI, native artwork retained. Otsu and
Simple T180/T210 produce different pixels. Compare encoders within each
column, not the thresholds as though their output were visually identical.

| Algorithm combination | Otsu | Simple T180 | Simple T210 |
|---|---:|---:|---:|
| BW + Zopfli | 20,769 | 21,537 | 24,435 |
| BW + Zopfli + PNG prediction | 21,477 | 22,005 | 25,299 |
| BW + Brotli | 14,686 | 15,418 | 17,982 |
| BW + Brotli + PNG prediction | 18,284 | 18,712 | 22,249 |
| BW + JBIG2 + Zopfli native | 9,798 | 10,077 | 10,945 |
| BW + JBIG2 + Brotli native | **9,786** | **10,065** | **10,933** |

### Native-heavy files — fonts, drawings and container overhead

Preserve original encoded images without resampling. The W-9, Form 941 and
NASA Kepler paper expose different native-content burdens. These are whole
repository PDFs, not extracted pages or combined component estimates.

| Algorithm combination | W-9 / 6 pages | Form 941 / 3 pages | Kepler / 12 pages |
|---|---:|---:|---:|
| Preserve images + Classic Flate (reference) native | 188,447 | 872,512 | 2,188,983 |
| Preserve images + Zopfli native | 187,455 | 854,321 | 2,016,866 |
| Preserve images + Brotli native | **182,487** | **776,046** | **1,765,944** |

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
| Preserve images + Brotli native | **182,487** (-3.16%) | **364,353** (-0.89%) | **4,472,491** (-3.65%) | **1,492,960** (-0.01%) | **483,797** (-3.67%) | **1,765,944** (-19.33%) |
| BW FFPR + JBIG2; optimized residual streams | **297,872** (+0.00%) | **229,520** (+0.00%) | **1,199,049** (+0.00%) | **3,868** (+0.00%) | **316,049** (+0.00%) | **299,818** (+0.00%) |
| Color FFPR; indexed 5 colors + colored JBIG2; optimized residual streams | **299,497** (-0.01%) | **231,619** (+0.00%) | **3,817,106** (+0.00%) | **9,390** (+0.00%) | **337,274** (+0.00%) | **394,165** (+0.00%) |
| Color FFPR + JPEG q50; optimized residual streams | **5,674,560** (+0.00%) | **4,394,162** (+0.00%) | **16,652,211** (+0.00%) | **119,758** (+0.00%) | **5,695,628** (+0.00%) | **6,225,232** (+0.00%) |
| Color FFPR + JPEG2000 lossy r192; optimized residual streams | **790,654** (+0.00%) | **1,212,968** (+0.00%) | **2,322,153** (+0.00%) | **132,374** (+0.00%) | **1,186,046** (+0.00%) | **1,581,087** (+0.00%) |
| Color FFPR + JPEG2000 lossless; optimized residual streams | **26,977,014** (+0.00%) | **19,059,609** (+0.00%) | **127,518,137** (+0.00%) | **631,376** (+0.00%) | **27,091,577** (+0.00%) | **32,340,923** (+0.00%) |

Across the **30 FFPR pairs**, complete-file byte changes range from **-34 B** to **+0 B**: **2 smaller, 28 tied, 0 larger**. These are actual final-file differences, not residual-payload estimates. The 12 native-preserving controls give **12 smaller, 0 tied, 0 larger**, saving at least **145 B**. They retain much more content to recompress; the table measures that
contrast. Do not generalize these settings to
every PDF. Brotli still requires a supporting reader.

## What the measurements establish

- Five-color artwork: colored JBIG2 + Brotli-native is **15,757 B**, versus **21,917 B** for shared Brotli without prediction. The complete mixed-paper counterparts are **338,214 B** and **331,663 B**. Representation/content changes the comparison. Removing declaration overhead also reverses the artwork's old native-encoder ordering: the **15,776 B** Zopfli-native file is now 19 B larger than its Brotli counterpart.
- On the eleven-page **CCITT** NACA TM972 scan, BW/JBIG2 + Brotli-native is **267,896 B**, versus **412,939 B** for shared Brotli at identical prepared BW pixels. The unresampled Zopfli control is **366,695 B** and the original is **374,461 B**. The measured JBIG2 recipe is **28.46% smaller** than that original; this is not a universal ranking.
- Crater Lake's native-preserving JPEG q50 + Zopfli-native is **6,269,805 B**; its full-page JPEG counterpart is **16,652,211 B**. Both target 300 DPI, but FFPR rasterizes text/vectors: their sizes are not equal-fidelity codec scores.
- The [PNG-prediction table](#png-prediction--measured-effect-versus-baseline) shows **96 six-document pairs**. Four focused palette cases now reuse those same outputs; six other focused pairs remain outside this table. The [native/residual A/B experiment](#nativeresidual-streams--measured-effect-versus-flate-reference) holds encoded images fixed and reports **42 separate Flate-reference comparisons**.
- The unresampled W-9 original is **140,815 B**; its smallest tested preserve-images rewrite is **182,487 B**. Being the smallest tested rewrite does not mean it beats the untouched source.
- NASA Kepler: preserve-images + Zopfli native is **2,016,866 B**; Brotli native is **1,765,944 B**, versus the **2,262,602 B** original. Native-preserving BW/JBIG2 + Zopfli is **1,357,736 B**, while BW FFPR/JBIG2 is **299,818 B**. The last two have different native/text fidelity, not equivalent codec quality.
- On identical prepared five-color Kepler pixels, shared Brotli is **1,334,091 B**, versus **1,363,587 B** for colored JBIG2 + Brotli native: the complete shared-Brotli PDF is **2.16% smaller** than that complete JBIG2 counterpart. Both retain the same native artwork and require a Brotli-capable reader; this is content-specific, not a universal codec ranking.
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

§254's current declaration-OFF publication is frozen under
`.tmp/compression-experiments/brotli-default-off-publication-20261017/`.
Its `publication.json` SHA-256 is
`9279a171feff32151a44e7d2f41d3042abdc611bdd2ecf72c3b4bb724eeed22d`.
`measurements.json` records all **229 refreshed Brotli outputs** and their
actual final sizes/hashes, fresh-encoder proof and metadata-only finalization.
The integrated subset replaces 177 files; its 215 ordinary controls retain
their original hashes. `component-controls.json` verifies the 156 unchanged
supporting controls; the old native component manifest lacked output hashes,
so current hashes freeze those files without inventing historical hashes.
`analysis.json` recomputes winner counts and all thirty FFPR byte partitions.
The fixed-side checks pass **96 PNG native-stream pairs** and **72 native
A/B image pairs**, including both native experiments.

The rerun itself is frozen in `brotli-default-off-20261017-v2/`. Prepared
pixels/palettes were reused; every published Brotli image/native encoding ran
again, with a run-local cache for identical fresh inputs. Successful pinned
first-pass checkpoints retain their own producer proof; rejected partial
files are not ranked. Metadata-only finalization reuses this rerun's fresh
payloads and removes only a proven benchmark-owned absent-version marker.
All bytes are measured after the shared optimizer saves the real file; no
fixed metadata deduction is used (actual old-to-new differences are 151 or
166 B in this integrated corpus). Exact reachable graphs/stream signatures
preserve the earlier all-page pixel proof without rendering/filtering again.
Both effect fixtures pin this new publication and declaration-OFF setting.

§258 adds **114 new verified Best PDFs**, one per overview cell. Its measured manifest is `.tmp/compression-experiments/best-overview-300dpi-20261017/metrics.json` (SHA-256 `ab689814fe55f1d89e2020dee1028819a0d0b9047bd5e84c582441376168f153`). The fixed-encoder 392-file publication stays immutable: 300 representative plain/PNG measurements, focused controls and the two native experiments retain their actual producer identities. The expanded binary table reuses 114 existing pairs; it does not run or relabel those encoders again. The [Best regression fixture](../tests/fixtures/best_overview_sizes.json) pins all 114 new sizes/hashes plus both fixed-policy sizes per cell. Publication checks actual file hashes, sources, frozen preparations, selection candidates and unchanged semantic graphs. Best changes lossless storage, so its image-byte check compares exact decoded eligible samples and exact protected J* payloads, not an impossible unchanged packed encoding. The graph proof preserves the preparations' prior all-page render verification without rerendering or repeating image transforms. No-image controls are independently saved.

The complete fresh post-B114 measurement superset remains immutable under `.tmp/integrated-compression/post-b114-300dpi-20261016/`: 252 overview and 62 focused outputs, all saved using one repaired compositor. Its `identity.json` pins source, tool, environment and saver/verifier/driver hashes; `refresh.py`, `overview.py`, `scenarios.py`, scoped job manifests and `complete.json` preserve the actual full measurement scope.

`image-streams.py` also freezes the measured bitmap driver. Subsequent runner
changes select only retained variants and remove an unused JSON percentage
that incorrectly assumed the first variant was always Classic Flate. This
changes future scope/metadata, not the shared pixel/encoding/save operations;
the current publication retains the actual measured implementation hashes.

Designer §§236/237's reduced publication is a hash-verified **selection from that measured superset**, not a claim that it was re-encoded under the later row-selection code. `selected-237/metrics.json` records the exact selected paths, original per-output provenance, frozen-superset hashes and new selector scope. The redundant bitmap combinations are removed consistently from every table, not kept as supplemental references. Sixty-two superseded files stay archived but are not current analysis cells. No original source, saved PDF, measured byte count or strict import/resume gate is rewritten or relaxed.

The original §242 extensions are frozen under `.tmp/compression-experiments/`: `png-palettes-300dpi-20261017/` and `native-residual-300dpi-20261017/`. Their identities retain the producing implementation, source/tool hashes, original imported records and a bounded compatibility proof: the earlier bitmap driver's only core difference is removal of an unused JSON percentage field. No encoder, preparation, saver or validator changed in that import. Normal changed-code resume remains forbidden. Original publication inputs, sources, complete output hashes, paired statistics and then-current Markdown remain under `.tmp/compression-experiments/publication-20261017/`; §254's replacement is above. See [experiment plans](COMPRESSION_EXPERIMENTS.md).

Historical studies remain untouched under `.tmp/integrated-compression/representative-six-300dpi-20261016/`, `representative-complete-300dpi-20261016-v2/`, `representative-300dpi-20261016-v3/` and `scenarios-300dpi-20261016-v3/`. Their original files, historical namespace paths and compatibility proofs are not relabeled. The already-JBIG2 JFK measurements remain B114 regression/diagnostic evidence, not current codec-rank cells.

Each final save uses the shared production page composer, image primitives
and native/font/container saver. Packed-stream prediction and prototype
general-image compression are the explicit experimental variables. Fixed-policy
final candidates retain their checks against frozen preparations for encoded/
decoded image bytes, native streams and all-page 72/300-DPI pixels. The
new Best outputs use exact semantic-graph/sample/J* verification as above. The preparation itself is checked
against its original input for native-text integrity, unintended retained source-image
payloads throughout the file, and new diagnostics.
Prepared fonts are not re-subset: doing so can change checksum bytes even
when glyphs are unchanged. Saved-file hashes and complete bytes are audited.
Benchmark PDF IDs use a controlled 16-byte ASCII framing through the shared
saver's existing option, avoiding random literal-versus-hex size noise.
Normal GUI ID generation is unchanged; these remain actual complete PDFs,
not estimated UI bytes or payload-only sizes.

All current cells are actual complete-file measurements from the repaired compositor. Source/preparation/output hashes are checked; earlier failed or mixed-DPI results remain historical, never current measurements. Ordinary low-priority subprocesses use independent scoped directories, with no preparation races or shared output writers. Only completed verified jobs enter the final matrix. No encoding-time metric/ranking is published, and all original PDFs remain unchanged.

Reproduce the Best-only overview from the repository root, using fresh labels:

```sh
nice -n 10 ./.venv/bin/python tools/bench_best_overview.py --label <best-label> --workers 2
./.venv/bin/python tools/publish_best_overview.py --measurements .tmp/compression-experiments/<best-label>/metrics.json --output .tmp/compression-experiments/<best-publication-label>
```

The publisher audits actual files and emits an `apply_patch` patch. The
following older commands reproduce the separate Brotli-refresh study;
they are not required when changing only the overview policy:

```sh
nice -n 10 ./.venv/bin/python tools/refresh_brotli_tables.py --label <brotli-label> --workers 2
./.venv/bin/python tools/publish_brotli_refresh.py --measurements .tmp/compression-experiments/<brotli-label>/metrics.json --output .tmp/compression-experiments/<publication-label>
```

Those commands reuse the frozen prepared corpus and emit an `apply_patch`
patch, without editing tracked documents directly. For a genuinely new
corpus/preparation, the original study runners are:

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

QPDF 12.2.0 syntax checks pass the **215 unchanged ordinary-format controls**;
their existing evidence is reused after hash verification. The **177 refreshed
Brotli outputs** are excluded from that unsupported reader check, not certified
by it. Removing a declaration cannot add Brotli decoding to an older reader.

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
