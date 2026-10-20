# Compression benchmarks — measured complete-PDF sizes

Every size on this page is the byte count of a complete PDF actually saved
by the production pipeline. Section 1 compares whole algorithm combinations;
section 2 holds single-factor (binary) experiments; section 3 records method
and provenance. The design these numbers test is in
[COMPRESSION.md](COMPRESSION.md).

Tables are curated by hand. Scripts only write measured values into rows
matched by their hidden `<!-- table: … -->` and `<!-- row: … -->` tags
(§§282/283); they never edit labels or text.

## Rulings (verbatim)

Exact designer text from `DESIGNER_VERBATIM.md`. Text outside the fenced
quotes is not the designer's.

### What is measured

**§222** (2026-10-15)

```text
where is the matrix comparing all algo combos file sizes on complete files, your analysis seems scattered.  We only care about the final file size, this is integrated compression analysis.
```

**§223** (2026-10-15)

```text
Why does your table have columns like Z/B, etc?  We agreed that those are not realistic?  Same for F/Z.  These are useless.  Have one table with all the algo combos as rows and choose a 5 typical types of pdfs that cover the major styles.   Then we will have other table that goes into more details for specific scenarios, like color photos, scanned BW docs, mix images text, etc.  There are only a few major classes of pdfs that are load bearing to pdf compression algorithm analysis, no?
```

**§229** (2026-10-16)

```text
please drop that rule, every row gets benchmarked, even if redundant, this is also a sanity check on the benchmarks.
```

**§239** (2026-10-16)

```text
There is no "predicted PDF bytes", no predicted.  Only measured.  Why did you say predicted?
```

**§209** (2026-10-15)

```text
you have color index filters that use flate, so you should make equivalent bechmarks for better compression on color index and bw please, compare with JBIG2 and color JPBIG2 also.  Do the work please.  We are only comparing size a this time.  Compute time is not measure because the cpu load on this workstation is fluctuating alot and unpredictably.
```

**§225** (2026-10-15)

```text
I think we should also convert all the filters to 300dpi default for now.  We know that lower dpi will be smaller in general, it's not useful to have variations of this, it doesn't provide information and causes comparison problems.
```

**§231** (2026-10-16)

```text
also, add models-nasa-kepler.pdf as another Representative class, or within an existing class, or suggest another alternative to add a sixth case that covers a broad spectrum.  I have been using that one as a good test case, but maybe you have other suggestions?
```

**§233** (2026-10-16)

```text
that is a good test case for the full flow, the flow should never make a JBIG2 worse, document this as an issue and a test case to use to fix and check for regressions.  Also, this is NOT a good test case for this table, find another BW pdf that is NOT already JBIG2, or else the results are meaningless.
```

### Binary experiments

**§238** (2026-10-16)

```text
Your analysis is not well structured.  When an optimization does not change the final pdf visualization, like PNG prediction and optimized residual streams, split them out into their own tables to make single changes tests, this is the scientific method.  So for all the combination where PNG optimization is relevant, make a new table, with the rows for each of the baseline (eg "Indexed 5 colors + Brotli", etc) and the six columns, but the result size in the table will be for the "PNG prediction" version and beside it put the % improvement over the baseline (eg -1.2%, or +2.5%, etc)  The -% is good.  DO you follow?
```

**§258** (2026-10-17)

```text
Why do we still have rows in the main table that compare Zopfli with Brotli?  Move all those to the specialized binary table and only use the new "Best" algorithm for the main table, document in the section, but not in the table directly, because that would make the table too noisy, the specialize binary experiment table will be the reference for that information.
```

**§245** (2026-10-17)

```text
It looks like Brotli is a bit bigger than Zopfli for single page documents, then Brotli is better for multiple pages.  Is this always true?  Can you make a new section and new table comparing Brotli as basline, with Zopfli as treatment?  Also, replace all Zopfli-flate in table with just Zopfli, is there any reason to keep the long version "Zopfli-flate" in the tables?  Does it permit distinction against anything else with same name?
```

**§246** (2026-10-17)

```text
I mean with FFPR and modern compressions, like J* of course, other than that, the page would have additional information that is expected to be compressible.  I am looking for the scenarios where Brotli is worse, which is not the null hypothesis, since it is supposed to be better.  And when worse is found, why?
```

**§243** (2026-10-17)

```text
also, remove the sizes from the binary test table "PNG prediction — measured effect versus baseline"
```

**§250** (2026-10-17)

```text
You need to put a table title directly before those two table that clearly and concisely states the experimental treatment in the cells of the table.  Show me here first for headers, the I will confirm.
```

```text
ok, proceed
```

### Presentation

**§227** (2026-10-16)

```text
In the table "Overview — final complete-file bytes" Make three sections to clarify the analysis, the first will be all BW algorithms, then indexed colors, then full colors algorithms.  It's generally expected that JPBIG2 will be the best for BW, then maybe Brotli or layered JBIG2 for low pallettes, then JPEG, JPG2000 for full color.
```

**§228** (2026-10-16)

```text
No, put in a same continuous table with a row as the divider, no numbering.  Merged cells if md permits, if not, just blank cell except for the far left one with the title.
```

**§221** (2026-10-15)

```text
Also highlight in bold the best of each row in the tables, can you do that in md?  Or not supported?
```

**§248** (2026-10-17)

```text
Decide on a stanard number of decimals for percentage diff.  Let's use 2 decimals.  And move the brotli table after png.
```

**§249** (2026-10-17)

```text
if it rounds to 0.00%, no bold please
```

**§232** (2026-10-16)

```text
"Black and white (BW)" rename to "Black and white (BW + Otsu)" and remove the "; keep native", this is implied by no FFPR.
```

### Lossy settings

**§271** (2026-10-19)

```text
NO! That is NOT good, there has to be ONE single q setting for all experiments!  You really don't know how to design proper experiments?  With variations of q for JPEG2000, nothing is comparable consistently, it has no value.
```

```text
ok, tat is good
```

**§272** (2026-10-19)

```text
I had a less skiled worker program this app and documentation, but I am not sastisfied.  The first problem I have is that it was not able to derive a proper quality setting equivalence for JPEG2000 that matched JPG q75 (I think that is what I choose).  This is important for the benchmarks, because we need to set all settings as similar as possible and also follow what users expect and understand (eg q=75 quality setting, not multiple different complex settings), so that the benchmarks mean something and so that users can know what they are setting?  There is already some research done in the repo, please review and do me research if you feel that is required.
```

**§284** (2026-10-20)

```text
Ok, so a single setting is the correct direction, however, for the purpose of out benchmarking, we have to choose a single quality setting that provides the same visual results as jpg.  The reasoning is simple, if jpg q75 provides a certain compression and quality, then the newer J2K is expected to provide a smaller (or in the absolute worst case, the same size) file for the same visual quality level.  This is very simple and basic, I should not have to explain this.  Or else, benchmarks and a newer compression algorithm has no value.
```

**§287** (2026-10-20)

```text
Sounds like we cannot be opinionated on the JPG/J2K for now, so let's just keep them as comparable as possible in the benchmarks and we will not have an automatic Best option for these.
```

### Maintaining this page

**§281** (2026-10-20)

```text
I think the compression docs should be organized as the first one being for the compression design, high level, and another with the compression benchmarks.  Compression benchmarks should be mostly focused on the integrated final size, and then binary experiment benchmarks, those that I have guided closely follow better my design intent and follow proper experimental treatment design, the others that predate are somewhat a mess.  do you see any need for any other compression related documents?  Or should we have other splits/docs for this?
```

**§282** (2026-10-20)

```text
ok, as you suggest, but the scripts should only be updating the benchmarks, not various texts in the file, right?  Maybe the benchmark results on the matching line specifically?  Thus you curate the tables manually?
```

**§283** (2026-10-20)

```text
can you put id tags on the lines to ensure full match, even if the row description is short and not necessarily unique across the page, or md doesn't provide this?
```

## Status of the current measurements

- **Lossy rows: LOSSY-06 (2026-10-20).** JPEG q75 against JPEG2000 q75 under
  the calibrated mapping (§284): on a typical page the two look alike. Single
  documents still differ, so each lossy size comparison should be read with
  its [measured quality gap](#measured-image-quality-of-jpeg2000-q75-against-jpeg-q75).
  These 24 files and the lossy rows of every other table were measured fresh
  with the current compositor.
- **Other native-mode rows predate the B116 composition repair.** The known
  visible effect is on the photo brochure's first page, where two framed
  inset photographs and the header emblem are missing; FFPR keeps them.
  These rows are re-measured next.
- The non-lossy overview cells used Best with each image's PNG predictor
  kept as prepared (§258). Since §260, Best also tries prediction on and off;
  those cells are not yet re-measured with that search.
- Brotli outputs carry no compatibility declaration (the default since §251).

## Six representative PDFs

<!-- table: representatives -->

| Representative class | Complete PDF | Pages | Original bytes |
|---|---|---:|---:|
| <!-- row: native --> Native text/vectors | [form-fw9.pdf](../examples/form-fw9.pdf) | 6 | 140,815 |
| <!-- row: scan --> BW scan | [scan-naca-tm972.pdf](../examples/scan-naca-tm972.pdf) | 11 | 374,461 |
| <!-- row: photos --> Color photos | [news-crater-lake-2026.pdf](../examples/news-crater-lake-2026.pdf) | 8 | 5,550,048 |
| <!-- row: art --> Flat-color artwork | [images.pdf](../examples/images.pdf) | 1 | 1,494,439 |
| <!-- row: mixed --> Mixed text/images | [paper-arxiv-1406.2661.pdf](../examples/paper-arxiv-1406.2661.pdf) | 9 | 530,482 |
| <!-- row: kepler --> Technical illustrations | [models-nasa-kepler.pdf](../examples/models-nasa-kepler.pdf) | 12 | 2,262,602 |

The six columns cover native instructions and fonts, scanned text pixels,
photography, flat graphics, mixed research content and multipage technical
illustration. They overlap on purpose and are not an exhaustive taxonomy.

- **BW scan** is the whole `scan-naca-tm972.pdf`: eleven 1-bit CCITT pages at
  about 300 DPI with typewriting, annotations and diagrams. It contains no
  JBIG2, so JBIG2 results are not a re-encode of JBIG2 (§233). The
  already-JBIG2 JFK scan serves only as B114's no-growth regression in
  [JBIG2.md](JBIG2.md).
- **Color photos** is an eight-page newspaper, not the logos in `images.pdf`.
- **Technical illustrations** is NASA Kepler (§231): twelve pages of text, ten
  with vector drawings and nine with images.

## How to read the tables

- Bitmap canvases are prepared at **300 DPI**, in every table. The
  **unresampled reference** keeps the source images' samples and geometry
  (eligible lossless image streams may be repacked); it is a control, not
  the app's Original view.
- Rows without FFPR keep native text and vectors; FFPR rasterizes the whole
  page. They are different fidelity groups and are never ranked against each
  other, nor are BW, palette and full-colour rows.
- **Bold** marks the smallest value within the same PDF column and fidelity
  group, ties included. A group with one row has one bold value; that is not
  proof of a universal winner.
- Indexed rows use up to 5, 16 or 64 colours, each its own fidelity group;
  colored JBIG2 encodes only the non-white colours a page uses. BW uses Otsu
  unless a row names a Simple threshold.
- JPEG is 4:4:4 with optimized Huffman coding. JPEG2000 q75 is lossy 9/7
  with RGB colour decorrelation, full-resolution components, one layer, LRCP,
  64×64 code blocks and a PSNR target of 44 dB per 512-pixel tile, the
  setting calibrated to look like JPEG q75 (§284,
  [LOSSY_IMAGE_QUALITY.md](LOSSY_IMAGE_QUALITY.md)). JPEG2000 lossless rows
  are edge-case references, not competitors of the lossy rows.
- **Zopfli** always means standard FlateDecode data. **Classic Flate** is a
  labelled reference, not a product choice. **Brotli** needs a reader with
  Brotli support, whether it compresses images or native streams.
- Percentage changes are computed from the exact byte counts and shown with
  two decimals. Negative is smaller. A change that rounds to +0.00% is never
  bold; the exact bytes stay authoritative.
- Every row is measured for every PDF (§229), including image-free W-9 cases
  where the image codec has nothing to do. Their repeated sizes are a sanity
  check.

## 1. Integrated final sizes

### Overview — final complete-file bytes

Every row uses **Best (Zopfli/Brotli)** for native streams and eligible
packed BW/indexed image streams; JPEG, JPEG2000 and JBIG2 payloads are left
untouched. Best keeps the smallest of its per-stream mix, all-Zopfli and
all-Brotli saves. The fixed-encoder alternatives are in the
[binary experiment](#stream-compression--zopfli-versus-brotli-baseline).

<!-- table: overview -->

| Algorithm combination | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images | Technical illustrations |
|---|---:|---:|---:|---:|---:|---:|
| <!-- row: group.reference --> **Unresampled reference** | | | | | | |
| <!-- row: reference --> Unresampled reference | **182,485** | **364,347** | **4,455,585** | **913,416** | **450,454** | **1,607,127** |
| <!-- row: group.bw --> **Black and white (BW + Otsu)** | | | | | | |
| <!-- row: bw-jbig2 --> BW + JBIG2 | **182,485** | **267,896** | **1,622,205** | **9,761** | **300,346** | **1,106,489** |
| <!-- row: bw-packed --> BW | **182,485** | 413,126 | 1,747,688 | 14,678 | 304,701 | 1,127,095 |
| <!-- row: bw-ffpr-jbig2 --> BW FFPR + JBIG2 | **297,872** | **229,520** | **1,199,049** | **3,868** | **316,049** | **299,818** |
| <!-- row: bw-ffpr-packed --> BW FFPR | 531,332 | 374,750 | 1,903,288 | 9,417 | 574,780 | 527,882 |
| <!-- row: group.indexed --> **Indexed color — low palettes** | | | | | | |
| <!-- row: indexed-jbig2 --> Indexed 5 colors + colored JBIG2 | **182,485** | **269,681** | 4,003,018 | **15,737** | 338,209 | 1,363,580 |
| <!-- row: indexed-5 --> Indexed 5 colors | **182,485** | 413,401 | **3,277,697** | 21,909 | **331,692** | **1,334,237** |
| <!-- row: indexed-16 --> Indexed 16 colors | **182,485** | **413,401** | **5,456,145** | **36,337** | **416,843** | **1,712,306** |
| <!-- row: indexed-64 --> Indexed 64 colors | **182,485** | **413,401** | **8,276,451** | **52,382** | **513,607** | **2,247,500** |
| <!-- row: indexed-ffpr-jbig2 --> Color FFPR; indexed 5 colors + colored JBIG2 | **299,497** | **231,619** | 3,817,040 | **9,390** | **337,263** | **394,148** |
| <!-- row: indexed-ffpr-5 --> Color FFPR; indexed 5 colors | 531,482 | 375,025 | **3,733,844** | 15,377 | 602,485 | 676,564 |
| <!-- row: indexed-ffpr-16 --> Color FFPR; indexed 16 colors | **531,482** | **375,025** | **6,169,370** | **31,186** | **634,540** | **817,716** |
| <!-- row: indexed-ffpr-64 --> Color FFPR; indexed 64 colors | **531,482** | **375,025** | **9,679,530** | **47,253** | **661,319** | **991,691** |
| <!-- row: group.full-color --> **Full color** | | | | | | |
| <!-- row: jpeg --> JPEG q75 | **182,517** | 6,191,883 | 10,008,205 | 222,989 | 739,504 | 3,112,615 |
| <!-- row: jpx-lossy --> JPEG2000 q75 | **182,517** | **5,156,583** | **9,150,363** | **107,274** | **469,094** | **2,029,694** |
| <!-- row: jpx-lossless --> JPEG2000 lossless | **182,485** | **19,097,985** | **56,241,450** | **569,331** | **1,805,448** | **8,674,834** |
| <!-- row: jpeg-ffpr --> Color FFPR + JPEG q75 | **7,613,891** | 6,153,507 | **25,408,327** | 229,805 | 7,796,434 | 9,166,422 |
| <!-- row: jpx-lossy-ffpr --> Color FFPR + JPEG2000 q75 | 7,657,666 | **5,118,207** | 30,474,962 | **109,422** | **7,494,281** | **8,847,881** |
| <!-- row: jpx-lossless-ffpr --> Color FFPR + JPEG2000 lossless | **26,977,014** | **19,059,609** | **127,518,137** | **631,376** | **27,091,577** | **32,340,923** |

At q75 JPEG2000 is smaller than JPEG in 9 of the 12 complete-PDF pairs,
larger in 2 and tied in 1 (from −52.38% to +19.94%). The tie is the native
W-9, which has no images; the two larger files are the full-page newspaper
(+19.94%) and the full-page W-9 (+0.58%).

#### Measured image quality of JPEG2000 q75 against JPEG q75

Mean SSIMULACRA2 difference of each document's page images, JPEG2000 minus
JPEG, from the calibration study in
[LOSSY_IMAGE_QUALITY.md](LOSSY_IMAGE_QUALITY.md#results-by-document). Positive
means JPEG2000 looks better. A smaller JPEG2000 file with a large negative gap
is a lower-quality file, not a like-for-like win. The page images were
prepared before the B116 repair; the newspaper's native images now also
include the two inset photographs.

<!-- table: lossy-quality-gap -->

| Image mode | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images | Technical illustrations |
|---|---:|---:|---:|---:|---:|---:|
| <!-- row: native --> JPEG q75 / JPEG2000 q75 | no images | -3.6 | -4.8 | -19.1 | -12.5 | -10.8 |
| <!-- row: ffpr --> Color FFPR + JPEG q75 / JPEG2000 q75 | +9.4 | -3.6 | +9.4 | -19.0 | +2.1 | +2.1 |

### Focused scenarios

Each focused table changes only the setting named in its columns. Cells are
fixed-encoder controls, not Best results, and reuse the measured files above
where they coincide.

#### Color photography — native preservation and full-page color

All eight Crater Lake pages, full colour. Preserve-images keeps the original
image bytes; the other rows target 300 DPI.

<!-- table: focused-photos -->

| Algorithm combination | Color photos |
|---|---:|
| <!-- row: reference.classic --> Preserve images + Classic Flate (reference) native | 4,641,959 |
| <!-- row: reference.zopfli --> Preserve images + Zopfli native | 4,574,656 |
| <!-- row: reference.brotli --> Preserve images + Brotli native | **4,472,491** |
| <!-- row: jpeg.zopfli --> JPEG q75 + Zopfli native | 10,125,272 |
| <!-- row: jpeg.brotli --> JPEG q75 + Brotli native | **10,008,389** |
| <!-- row: jpx-lossy.zopfli --> JPEG2000 q75 + Zopfli native | 9,267,429 |
| <!-- row: jpx-lossy.brotli --> JPEG2000 q75 + Brotli native | **9,150,547** |
| <!-- row: jpx-lossless.zopfli --> JPEG2000 lossless + Zopfli native | 56,343,268 |
| <!-- row: jpx-lossless.brotli --> JPEG2000 lossless + Brotli native | **56,241,606** |
| <!-- row: jpeg-ffpr.zopfli --> Color FFPR + JPEG q75; optimized residual streams | **25,408,295** |
| <!-- row: jpx-lossy-ffpr.zopfli --> Color FFPR + JPEG2000 q75; optimized residual streams | **30,474,930** |
| <!-- row: jpx-lossless-ffpr.zopfli --> Color FFPR + JPEG2000 lossless; optimized residual streams | **127,518,137** |

#### Logos/artwork — palette count

The complete `images.pdf` at 300 DPI with native artwork kept. Within a
column the encoders preserve identical pixels; across columns the palette,
and therefore the fidelity, changes.

<!-- table: focused-artwork -->

| Algorithm combination | 5 colors | 16 colors | 64 colors |
|---|---:|---:|---:|
| <!-- row: indexed.zopfli --> Indexed + Zopfli | 28,012 | 44,809 | 63,305 |
| <!-- row: indexed.zopfli.png --> Indexed + Zopfli + PNG prediction | 32,639 | 51,430 | 85,501 |
| <!-- row: indexed.brotli --> Indexed + Brotli | 21,917 | 36,345 | **52,390** |
| <!-- row: indexed.brotli.png --> Indexed + Brotli + PNG prediction | 28,249 | 47,043 | 76,746 |
| <!-- row: indexed-jbig2.zopfli --> Indexed + colored JBIG2 + Zopfli native | 15,776 | 34,468 | 71,263 |
| <!-- row: indexed-jbig2.brotli --> Indexed + colored JBIG2 + Brotli native | **15,757** | **34,428** | 71,146 |

#### Mixed text/images — palette count

All nine pages of the GAN paper; text, vectors and fonts stay native and
only the composed bitmap layer is palette-reduced.

<!-- table: focused-mixed -->

| Algorithm combination | 5 colors | 16 colors | 64 colors |
|---|---:|---:|---:|
| <!-- row: indexed.zopfli --> Indexed + Zopfli | 359,179 | 459,802 | 578,231 |
| <!-- row: indexed.zopfli.png --> Indexed + Zopfli + PNG prediction | 367,102 | 478,813 | 640,060 |
| <!-- row: indexed.brotli --> Indexed + Brotli | **331,663** | **416,814** | **513,578** |
| <!-- row: indexed.brotli.png --> Indexed + Brotli + PNG prediction | 347,095 | 456,196 | 605,762 |
| <!-- row: indexed-jbig2.zopfli --> Indexed + colored JBIG2 + Zopfli native | 345,953 | 467,614 | 643,874 |
| <!-- row: indexed-jbig2.brotli --> Indexed + colored JBIG2 + Brotli native | 338,214 | 459,851 | 635,977 |

#### Scanned BW text — different source material

NACA TM972 (eleven typewritten pages) and NACA formulas (seven pages of
mathematical print), 300 DPI, Otsu.

<!-- table: focused-scan -->

| Algorithm combination | NACA TM972 | NACA formulas |
|---|---:|---:|
| <!-- row: bw.zopfli --> BW + Zopfli | 578,690 | 394,669 |
| <!-- row: bw.zopfli.png --> BW + Zopfli + PNG prediction | 570,171 | 383,806 |
| <!-- row: bw.brotli --> BW + Brotli | 412,939 | 289,811 |
| <!-- row: bw.brotli.png --> BW + Brotli + PNG prediction | 529,852 | 357,693 |
| <!-- row: bw-jbig2.zopfli --> BW + JBIG2 + Zopfli native | 270,228 | 192,438 |
| <!-- row: bw-jbig2.brotli --> BW + JBIG2 + Brotli native | **267,896** | **190,757** |

#### Threshold sensitivity — three explicit BW transforms

The same `images.pdf`; Otsu and Simple T180/T210 produce different pixels,
so compare encoders within a column only.

<!-- table: focused-thresholds -->

| Algorithm combination | Otsu | Simple T180 | Simple T210 |
|---|---:|---:|---:|
| <!-- row: bw.zopfli --> BW + Zopfli | 20,769 | 21,537 | 24,435 |
| <!-- row: bw.zopfli.png --> BW + Zopfli + PNG prediction | 21,477 | 22,005 | 25,299 |
| <!-- row: bw.brotli --> BW + Brotli | 14,686 | 15,418 | 17,982 |
| <!-- row: bw.brotli.png --> BW + Brotli + PNG prediction | 18,284 | 18,712 | 22,249 |
| <!-- row: bw-jbig2.zopfli --> BW + JBIG2 + Zopfli native | 9,798 | 10,077 | 10,945 |
| <!-- row: bw-jbig2.brotli --> BW + JBIG2 + Brotli native | **9,786** | **10,065** | **10,933** |

#### Native-heavy files — fonts, drawings and container overhead

Original encoded images kept without resampling; the W-9, Form 941 and
Kepler expose different native-content burdens.

<!-- table: focused-native -->

| Algorithm combination | W-9 / 6 pages | Form 941 / 3 pages | Kepler / 12 pages |
|---|---:|---:|---:|
| <!-- row: reference.classic --> Preserve images + Classic Flate (reference) native | 188,447 | 872,512 | 2,188,983 |
| <!-- row: reference.zopfli --> Preserve images + Zopfli native | 187,455 | 854,321 | 2,016,866 |
| <!-- row: reference.brotli --> Preserve images + Brotli native | **182,487** | **776,046** | **1,765,944** |

### Findings

- Five-colour artwork: colored JBIG2 + Brotli native is 15,757 B against
  21,917 B for packed indexed + Brotli. On the mixed paper the order flips:
  338,214 B against 331,663 B. Content decides; no codec wins everywhere.
- NACA TM972 scan: BW/JBIG2 + Brotli native is 267,896 B, 28.46% below the
  374,461 B original and well below packed BW + Brotli (412,939 B) at
  identical pixels.
- Crater Lake: native-preserving JPEG q75 + Zopfli native is 10,125,272 B;
  the full-page JPEG counterpart is 25,408,295 B. FFPR rasterizes the text,
  so these are different fidelity.
- W-9: the original is 140,815 B and the smallest rewrite 182,487 B. Being
  the smallest tested rewrite does not mean beating the untouched source.
- Kepler: Brotli native alone takes the original from 2,262,602 B to
  1,765,944 B; BW FFPR/JBIG2 reaches 299,818 B at a different fidelity.
- On identical five-colour Kepler pixels, packed indexed + Brotli
  (1,334,091 B) is 2.16% smaller than colored JBIG2 + Brotli native
  (1,363,587 B).
- JPEG2000 q75 against JPEG q75: the two larger JPEG2000 files (full-page
  newspaper and W-9) look better than their JPEG versions (+9.4). Matched to
  JPEG's quality page by page, those page images need 14% and 28% fewer
  bytes in JPEG2000, while embedded colour photos need 21% more
  ([equal quality, page by page](LOSSY_IMAGE_QUALITY.md#equal-quality-page-by-page)).
  Neither codec wins everywhere, and neither is chosen automatically (§287).

## 2. Binary experiments

Each experiment changes exactly one factor between two actually saved PDFs;
everything else (source, prepared pixels and palette, DPI, threshold,
quality, native content, PDF ID framing, writer settings) is held fixed.
Cells show `100 × (treatment − baseline) / baseline` from exact byte counts.
Negative favours the treatment. Bold marks a displayed reduction; +0.00% is
never bold. Exact byte counts live in the fixtures listed in section 3.

### PNG prediction — measured effect versus baseline

#### Results and decision tree

Fixed encoders, 96 pairs: prediction makes **0 of 48 Brotli** files and
**18 of 48 Zopfli** files smaller. Counting every measured algorithm at the
same fidelity, no PNG-prediction candidate is uniquely the smallest file.
Without Brotli (for readers that lack it), eight 16/64-colour candidates do
win, so prediction is not obsolete.

The policy branches on the **prepared output image**, not the source file
type:

```text
Prepared output image
├─ No bitmap rows → no-op; no prediction decision.
├─ JPEG / JPEG2000 / JBIG2 → PNG prediction not applicable to that payload.
└─ Packed BW / indexed samples → apply the stream policy below.

Best (Zopfli/Brotli)
├─ Zopfli → test prediction OFF and ON.
└─ Brotli → test prediction OFF and ON.

Explicit Zopfli
├─ Off → test prediction OFF only.
├─ On → test prediction ON only.
└─ Best → test prediction OFF and ON.

Compare measured complete-PDF candidates; keep the smallest.
```

Best measures both states instead of skipping on content heuristics (§§260/261).
Native text and vector streams never use image-row prediction. Counterexample
to "Brotli never benefits": an earlier noisy-BW control shrinks with Brotli +
prediction from 83,266 to 80,852 B (−2.90%), though JBIG2 still wins at 63,075 B.

#### Enable PNG prediction — final PDF size change (%) versus prediction OFF

Each row names its fixed-encoder plain baseline (the fixed-encoder controls
below). The predictor is the adaptive predictor-15 row selector, held fixed.
<ins>Brotli</ins> is underlined where prediction never helped (§244).

<!-- table: png-effect -->

| Baseline combination | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images | Technical illustrations |
|---|---:|---:|---:|---:|---:|---:|
| <!-- row: bw-packed.zopfli --> BW + Zopfli | +0.00% | **-1.47%** | +1.41% | +3.41% | +0.13% | +0.29% |
| <!-- row: bw-packed.brotli --> BW + <ins>Brotli</ins> | +0.00% | +28.31% | +6.14% | +24.50% | +1.22% | +1.67% |
| <!-- row: bw-ffpr-packed.zopfli --> BW FFPR + Zopfli | **-5.63%** | **-1.58%** | **-4.54%** | +4.30% | **-5.68%** | **-1.82%** |
| <!-- row: bw-ffpr-packed.brotli --> BW FFPR + <ins>Brotli</ins> | +8.90% | +31.21% | +16.49% | +41.05% | +8.88% | +18.37% |
| <!-- row: indexed-5.zopfli --> Indexed 5 colors + Zopfli | +0.00% | **-1.47%** | +11.84% | +16.52% | +2.21% | +3.84% |
| <!-- row: indexed-5.brotli --> Indexed 5 colors + <ins>Brotli</ins> | +0.00% | +28.29% | +20.84% | +28.89% | +4.65% | +8.01% |
| <!-- row: indexed-ffpr-5.zopfli --> Color FFPR; indexed 5 colors + Zopfli | **-5.62%** | **-1.58%** | +13.94% | +19.09% | **-3.65%** | +0.56% |
| <!-- row: indexed-ffpr-5.brotli --> Color FFPR; indexed 5 colors + <ins>Brotli</ins> | +8.89% | +31.19% | +29.54% | +44.36% | +10.93% | +19.68% |
| <!-- row: indexed-16.zopfli --> Indexed 16 colors + Zopfli | +0.00% | **-1.47%** | +15.83% | +14.78% | +4.13% | +5.45% |
| <!-- row: indexed-16.brotli --> Indexed 16 colors + <ins>Brotli</ins> | +0.00% | +28.29% | +22.67% | +29.43% | +9.45% | +12.13% |
| <!-- row: indexed-ffpr-16.zopfli --> Color FFPR; indexed 16 colors + Zopfli | **-5.62%** | **-1.58%** | +17.19% | +16.46% | **-2.05%** | +5.22% |
| <!-- row: indexed-ffpr-16.brotli --> Color FFPR; indexed 16 colors + <ins>Brotli</ins> | +8.89% | +31.19% | +29.22% | +35.77% | +12.08% | +22.17% |
| <!-- row: indexed-64.zopfli --> Indexed 64 colors + Zopfli | +0.00% | **-1.47%** | +18.68% | +35.06% | +10.69% | +15.39% |
| <!-- row: indexed-64.brotli --> Indexed 64 colors + <ins>Brotli</ins> | +0.00% | +28.29% | +25.84% | +46.49% | +17.95% | +24.17% |
| <!-- row: indexed-ffpr-64.zopfli --> Color FFPR; indexed 64 colors + Zopfli | **-5.62%** | **-1.58%** | +23.62% | +38.51% | **-2.92%** | +1.29% |
| <!-- row: indexed-ffpr-64.brotli --> Color FFPR; indexed 64 colors + <ins>Brotli</ins> | +8.89% | +31.19% | +33.42% | +53.67% | +11.74% | +21.13% |

- Zopfli: 18 smaller, 4 tied, 26 larger of 48 pairs.
- Brotli: 0 smaller, 4 tied, 44 larger of 48 pairs.

The ties are the image-free W-9, a sanity check rather than a predictor result.

<a id="ffpr-residual-compression--zopfli-versus-brotli-baseline"></a>

### Stream compression — Zopfli versus Brotli baseline

Brotli is the baseline and Zopfli the treatment, for all 19 overview recipes
(114 pairs). For packed BW/indexed rows both image and native streams change;
for JPEG, JPEG2000, JBIG2 and original-image rows only the native or residual
streams change, and the image payloads are identical.

#### Replace Brotli with Zopfli — final PDF size change (%)

<!-- table: zopfli-vs-brotli -->

| Image recipe / reference | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images | Technical illustrations |
|---|---:|---:|---:|---:|---:|---:|
| <!-- row: group.reference --> **Unresampled reference** | | | | | | |
| <!-- row: reference --> Unresampled reference | +2.72% | +0.64% | +2.28% | +0.00% | +1.59% | +14.21% |
| <!-- row: group.bw --> **Black and white (BW + Otsu)** | | | | | | |
| <!-- row: bw-jbig2 --> BW + JBIG2 | +2.72% | +0.87% | +6.27% | +0.12% | +2.57% | +22.71% |
| <!-- row: bw-packed --> BW | +2.72% | +40.14% | +12.91% | +41.42% | +6.10% | +26.36% |
| <!-- row: bw-ffpr-jbig2 --> BW FFPR + JBIG2 | +0.00% | **-0.01%** | +0.00% | **-0.08%** | +0.00% | +0.00% |
| <!-- row: bw-ffpr-packed --> BW FFPR | +29.65% | +43.62% | +28.03% | +67.56% | +29.42% | +37.21% |
| <!-- row: group.indexed --> **Indexed color — low palettes** | | | | | | |
| <!-- row: indexed-jbig2 --> Indexed 5 colors + colored JBIG2 | +2.72% | +0.86% | +2.54% | +0.12% | +2.29% | +18.43% |
| <!-- row: indexed-5 --> Indexed 5 colors | +2.72% | +40.11% | +14.99% | +27.81% | +8.30% | +26.16% |
| <!-- row: indexed-16 --> Indexed 16 colors | +2.72% | +40.11% | +12.11% | +23.29% | +10.31% | +23.96% |
| <!-- row: indexed-64 --> Indexed 64 colors | +2.72% | +40.11% | +12.83% | +20.83% | +12.59% | +23.44% |
| <!-- row: indexed-ffpr-jbig2 --> Color FFPR; indexed 5 colors + colored JBIG2 | **-0.04%** | **-0.04%** | +0.00% | **-0.11%** | **-0.01%** | **-0.02%** |
| <!-- row: indexed-ffpr-5 --> Color FFPR; indexed 5 colors | +29.64% | +43.59% | +20.57% | +41.33% | +30.04% | +34.97% |
| <!-- row: indexed-ffpr-16 --> Color FFPR; indexed 16 colors | +29.64% | +43.59% | +16.93% | +27.11% | +29.06% | +31.01% |
| <!-- row: indexed-ffpr-64 --> Color FFPR; indexed 64 colors | +29.64% | +43.59% | +15.02% | +23.52% | +30.41% | +33.85% |
| <!-- row: group.full-color --> **Full color** | | | | | | |
| <!-- row: jpeg --> JPEG q75 | +2.72% | +0.04% | +1.17% | +0.01% | +1.05% | +8.07% |
| <!-- row: jpx-lossy --> JPEG2000 q75 | +2.72% | +0.05% | +1.28% | +0.01% | +1.65% | +12.38% |
| <!-- row: jpx-lossless --> JPEG2000 lossless | +2.72% | +0.01% | +0.18% | +0.00% | +0.43% | +2.90% |
| <!-- row: jpeg-ffpr --> Color FFPR + JPEG q75 | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% |
| <!-- row: jpx-lossy-ffpr --> Color FFPR + JPEG2000 q75 | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% |
| <!-- row: jpx-lossless-ffpr --> Color FFPR + JPEG2000 lossless | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% |

#### FFPR with JPEG, JPEG2000 or JBIG2: why Brotli can be larger

In the five FFPR rows with a specialized image codec (30 pairs), Brotli is
larger in 29 pairs by 2–105 bytes and smaller in one, the newspaper with
five-colour layered JBIG2, by 66 bytes. Most of these round to +0.00%.

The byte accounting closes exactly. Image bytes, container bytes and other
streams are identical; the whole difference is:

- one byte per native stream, because `/BrotliDecode` is one byte longer
  than `/FlateDecode`;
- the native payload difference plus any extra `/Length` digits. After
  rasterization only 35–245 bytes of drawing commands remain per document
  (the six-page W-9 shares one 43-byte program), and Brotli's encoding of
  such tiny streams is 1–7 bytes larger.

For example, artwork + JBIG2 is 3,871 B with Brotli and 3,868 B with Zopfli.
On the newspaper, Brotli saves 74 payload bytes and spends 8 syntax bytes,
ending 66 B smaller. This is small-stream overhead, not worse compression of
the images.

#### Fixed-encoder controls — measured final PDF bytes

The fixed-policy alternatives behind both experiments above. Compare paired
controls with each other only: their PDF ID framing and font handling differ
slightly from the overview's Best saves.

<!-- table: fixed-controls -->

| Fixed-policy combination | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images | Technical illustrations |
|---|---:|---:|---:|---:|---:|---:|
| <!-- row: reference.classic --> Preserve images + Classic Flate (reference) native | 188,447 | 367,630 | 4,641,959 | 1,493,125 | 502,235 | 2,188,983 |
| <!-- row: reference.zopfli --> Preserve images + Zopfli native | 187,455 | 366,695 | 4,574,656 | 1,492,980 | 491,510 | 2,016,866 |
| <!-- row: reference.brotli --> Preserve images + Brotli native | **182,487** | **364,353** | **4,472,491** | **1,492,960** | **483,797** | **1,765,944** |
| <!-- row: bw-jbig2.zopfli --> BW + JBIG2 + Zopfli native | 187,455 | 270,228 | 1,724,023 | 9,798 | 308,080 | 1,357,736 |
| <!-- row: bw-jbig2.brotli --> BW + JBIG2 + Brotli native | **182,487** | **267,896** | **1,622,361** | **9,786** | **300,351** | **1,106,496** |
| <!-- row: bw-packed.zopfli --> BW + Zopfli | 187,455 | 578,690 | 1,973,320 | 20,769 | 323,270 | 1,424,063 |
| <!-- row: bw-packed.brotli --> BW + Brotli | **182,487** | 412,939 | 1,747,708 | 14,686 | 304,672 | 1,126,949 |
| <!-- row: bw-ffpr-jbig2.zopfli --> BW FFPR + JBIG2; optimized residual streams | **297,872** | **229,520** | **1,199,049** | **3,868** | **316,049** | **299,818** |
| <!-- row: bw-ffpr-jbig2.brotli --> BW FFPR + JBIG2 + Brotli residual streams | 297,875 | 229,534 | 1,199,051 | 3,871 | 316,052 | 299,821 |
| <!-- row: bw-ffpr-packed.zopfli --> BW FFPR + Zopfli | 688,732 | 537,982 | 2,436,663 | 15,756 | 743,693 | 724,057 |
| <!-- row: bw-ffpr-packed.brotli --> BW FFPR + Brotli | 531,233 | 374,577 | 1,903,154 | 9,403 | 574,630 | 527,681 |
| <!-- row: indexed-jbig2.zopfli --> Indexed 5 colors + colored JBIG2 + Zopfli native | 187,455 | 272,001 | 4,104,794 | 15,776 | 345,953 | 1,614,891 |
| <!-- row: indexed-jbig2.brotli --> Indexed 5 colors + colored JBIG2 + Brotli native | **182,487** | **269,681** | 4,003,174 | **15,757** | 338,214 | 1,363,587 |
| <!-- row: indexed-5.zopfli --> Indexed 5 colors + Zopfli | 187,455 | 578,965 | 3,769,149 | 28,012 | 359,179 | 1,683,086 |
| <!-- row: indexed-5.brotli --> Indexed 5 colors + Brotli | **182,487** | 413,214 | **3,277,717** | 21,917 | **331,663** | **1,334,091** |
| <!-- row: indexed-16.zopfli --> Indexed 16 colors + Zopfli | 187,455 | 578,965 | 6,116,675 | 44,809 | 459,802 | 2,122,383 |
| <!-- row: indexed-16.brotli --> Indexed 16 colors + Brotli | **182,487** | **413,214** | **5,456,165** | **36,345** | **416,814** | **1,712,160** |
| <!-- row: indexed-64.zopfli --> Indexed 64 colors + Zopfli | 187,455 | 578,965 | 9,338,434 | 63,305 | 578,231 | 2,774,044 |
| <!-- row: indexed-64.brotli --> Indexed 64 colors + Brotli | **182,487** | **413,214** | **8,276,471** | **52,390** | **513,578** | **2,247,354** |
| <!-- row: indexed-ffpr-jbig2.zopfli --> Color FFPR; indexed 5 colors + colored JBIG2; optimized residual streams | **299,497** | **231,619** | 3,817,106 | **9,390** | **337,274** | **394,165** |
| <!-- row: indexed-ffpr-jbig2.brotli --> Color FFPR; indexed 5 colors + colored JBIG2 + Brotli residual streams | 299,602 | 231,716 | 3,817,040 | 9,400 | 337,306 | 394,241 |
| <!-- row: indexed-ffpr-5.zopfli --> Color FFPR; indexed 5 colors + Zopfli | 688,882 | 538,257 | 4,501,917 | 21,713 | 783,305 | 912,904 |
| <!-- row: indexed-ffpr-5.brotli --> Color FFPR; indexed 5 colors + Brotli | 531,383 | 374,852 | **3,733,710** | 15,363 | 602,335 | 676,363 |
| <!-- row: indexed-ffpr-16.zopfli --> Color FFPR; indexed 16 colors + Zopfli | 688,882 | 538,257 | 7,213,825 | 39,624 | 818,742 | 1,071,002 |
| <!-- row: indexed-ffpr-16.brotli --> Color FFPR; indexed 16 colors + Brotli | **531,383** | **374,852** | **6,169,236** | **31,172** | **634,390** | **817,515** |
| <!-- row: indexed-ffpr-64.zopfli --> Color FFPR; indexed 64 colors + Zopfli | 688,882 | 538,257 | 11,133,100 | 58,350 | 862,205 | 1,327,080 |
| <!-- row: indexed-ffpr-64.brotli --> Color FFPR; indexed 64 colors + Brotli | **531,383** | **374,852** | **9,679,396** | **47,239** | **661,169** | **991,490** |
| <!-- row: jpeg.zopfli --> JPEG q75 + Zopfli native | 187,455 | 6,194,183 | 10,125,272 | 222,994 | 747,206 | 3,363,830 |
| <!-- row: jpeg.brotli --> JPEG q75 + Brotli native | **182,487** | **6,191,851** | **10,008,389** | **222,982** | **739,477** | **3,112,590** |
| <!-- row: jpx-lossy.zopfli --> JPEG2000 q75 + Zopfli native | 187,455 | 5,158,883 | 9,267,429 | 107,279 | 476,796 | 2,280,909 |
| <!-- row: jpx-lossy.brotli --> JPEG2000 q75 + Brotli native | **182,487** | **5,156,551** | **9,150,547** | **107,267** | **469,067** | **2,029,669** |
| <!-- row: jpx-lossless.zopfli --> JPEG2000 lossless + Zopfli native | 187,455 | 19,100,317 | 56,343,268 | 569,368 | 1,813,182 | 8,926,081 |
| <!-- row: jpx-lossless.brotli --> JPEG2000 lossless + Brotli native | **182,487** | **19,097,985** | **56,241,606** | **569,356** | **1,805,453** | **8,674,841** |
| <!-- row: jpeg-ffpr.zopfli --> Color FFPR + JPEG q75; optimized residual streams | **7,613,859** | **6,153,475** | **25,408,295** | **229,773** | **7,796,402** | **9,166,390** |
| <!-- row: jpeg-ffpr.brotli --> Color FFPR + JPEG q75 + Brotli residual streams | 7,613,862 | 6,153,489 | 25,408,297 | 229,776 | 7,796,405 | 9,166,393 |
| <!-- row: jpx-lossy-ffpr.zopfli --> Color FFPR + JPEG2000 q75; optimized residual streams | **7,657,634** | **5,118,175** | **30,474,930** | **109,390** | **7,494,249** | **8,847,849** |
| <!-- row: jpx-lossy-ffpr.brotli --> Color FFPR + JPEG2000 q75 + Brotli residual streams | 7,657,637 | 5,118,189 | 30,474,932 | 109,393 | 7,494,252 | 8,847,852 |
| <!-- row: jpx-lossless-ffpr.zopfli --> Color FFPR + JPEG2000 lossless; optimized residual streams | **26,977,014** | **19,059,609** | **127,518,137** | **631,376** | **27,091,577** | **32,340,923** |
| <!-- row: jpx-lossless-ffpr.brotli --> Color FFPR + JPEG2000 lossless + Brotli residual streams | 26,977,017 | 19,059,623 | 127,518,139 | 631,379 | 27,091,580 | 32,340,926 |

### Native/residual streams — measured effect versus Flate reference

One factor changes: standard level-9 Flate versus the named encoder for
native or FFPR residual streams. Encoded images, decoded drawing commands,
preparation and writer settings stay fixed. The two preserve-images rows
share their source's Flate reference.

#### Measured reference bytes — standard Flate native/residual streams

<!-- table: residual-reference -->

| Candidate combination | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images | Technical illustrations |
|---|---:|---:|---:|---:|---:|---:|
| <!-- row: reference.zopfli --> Preserve images + Zopfli native | 188,447 | 367,630 | 4,641,959 | 1,493,125 | 502,235 | 2,188,983 |
| <!-- row: reference.brotli --> Preserve images + Brotli native | 188,447 | 367,630 | 4,641,959 | 1,493,125 | 502,235 | 2,188,983 |
| <!-- row: bw-ffpr-jbig2.zopfli --> BW FFPR + JBIG2; optimized residual streams | 297,872 | 229,520 | 1,199,049 | 3,868 | 316,049 | 299,818 |
| <!-- row: indexed-ffpr-jbig2.zopfli --> Color FFPR; indexed 5 colors + colored JBIG2; optimized residual streams | 299,531 | 231,619 | 3,817,113 | 9,390 | 337,274 | 394,165 |
| <!-- row: jpeg-ffpr.zopfli --> Color FFPR + JPEG q75; optimized residual streams | 7,613,859 | 6,153,475 | 25,408,295 | 229,773 | 7,796,402 | 9,166,390 |
| <!-- row: jpx-lossy-ffpr.zopfli --> Color FFPR + JPEG2000 q75; optimized residual streams | 7,657,634 | 5,118,175 | 30,474,930 | 109,390 | 7,494,249 | 8,847,849 |
| <!-- row: jpx-lossless-ffpr.zopfli --> Color FFPR + JPEG2000 lossless; optimized residual streams | 26,977,014 | 19,059,609 | 127,518,137 | 631,376 | 27,091,577 | 32,340,923 |

#### Measured candidate bytes and change from that reference

Bold bytes are no larger than their own reference, ties included.

<!-- table: residual-effect -->

| Candidate combination | Native text/vectors | BW scan | Color photos | Flat-color artwork | Mixed text/images | Technical illustrations |
|---|---:|---:|---:|---:|---:|---:|
| <!-- row: reference.zopfli --> Preserve images + Zopfli native | **187,455** (-0.53%) | **366,695** (-0.25%) | **4,574,656** (-1.45%) | **1,492,980** (-0.01%) | **491,510** (-2.14%) | **2,016,866** (-7.86%) |
| <!-- row: reference.brotli --> Preserve images + Brotli native | **182,487** (-3.16%) | **364,353** (-0.89%) | **4,472,491** (-3.65%) | **1,492,960** (-0.01%) | **483,797** (-3.67%) | **1,765,944** (-19.33%) |
| <!-- row: bw-ffpr-jbig2.zopfli --> BW FFPR + JBIG2; optimized residual streams | **297,872** (+0.00%) | **229,520** (+0.00%) | **1,199,049** (+0.00%) | **3,868** (+0.00%) | **316,049** (+0.00%) | **299,818** (+0.00%) |
| <!-- row: indexed-ffpr-jbig2.zopfli --> Color FFPR; indexed 5 colors + colored JBIG2; optimized residual streams | **299,497** (-0.01%) | **231,619** (+0.00%) | **3,817,106** (+0.00%) | **9,390** (+0.00%) | **337,274** (+0.00%) | **394,165** (+0.00%) |
| <!-- row: jpeg-ffpr.zopfli --> Color FFPR + JPEG q75; optimized residual streams | **7,613,859** (+0.00%) | **6,153,475** (+0.00%) | **25,408,295** (+0.00%) | **229,773** (+0.00%) | **7,796,402** (+0.00%) | **9,166,390** (+0.00%) |
| <!-- row: jpx-lossy-ffpr.zopfli --> Color FFPR + JPEG2000 q75; optimized residual streams | **7,657,634** (+0.00%) | **5,118,175** (+0.00%) | **30,474,930** (+0.00%) | **109,390** (+0.00%) | **7,494,249** (+0.00%) | **8,847,849** (+0.00%) |
| <!-- row: jpx-lossless-ffpr.zopfli --> Color FFPR + JPEG2000 lossless; optimized residual streams | **26,977,014** (+0.00%) | **19,059,609** (+0.00%) | **127,518,137** (+0.00%) | **631,376** (+0.00%) | **27,091,577** (+0.00%) | **32,340,923** (+0.00%) |

Across the 30 FFPR pairs the change ranges from −34 B to +0 B: 2 smaller,
28 tied. The 12 native-preserving pairs are all smaller, by at least 145 B,
because far more native content remains to compress.

## 3. Method and provenance

### Measurement protocol

- Every cell is a complete PDF saved through the production composer, image
  encoders and final lossless pass. No size is estimated or derived from
  component sizes.
- Preparations (composed and resized canvases) are frozen and reused, so a
  control never repeats image processing; each control is still its own
  saved file.
- Benchmark saves use a fixed-width 16-byte PDF ID and do not re-subset
  already-prepared fonts, so neither adds size noise between paired files.
- Each output is checked against its preparation: every native glyph (font,
  paint, origin and bounds, 0.001 pt tolerance), exact decoded image samples
  and identical encoded J* payloads where they are meant to be identical, and
  all pages rendered at 72 and 300 DPI. Source warnings are kept apart from
  output and decoder warnings.
- Runs are size-only. Encoding time is not recorded (§209).
- Flate and Zopfli outputs pass `qpdf --check` (QPDF 12.2.0). Brotli outputs
  are validated with the recorded Brotli-capable MuPDF build; neither check
  certifies other readers. Reader limits are in
  [NATIVE_STREAM_COMPRESSION.md](NATIVE_STREAM_COMPRESSION.md#correctness-and-compatibility).

### Measurement and provenance

| Data | Manifest (under `.tmp/`) | SHA-256 | Pinned by |
|---|---|---|---|
| Best overview, 114 PDFs (§258) | `compression-experiments/best-overview-300dpi-20261017/metrics.json` | `ab689814fe55f1d89e2020dee1028819a0d0b9047bd5e84c582441376168f153` | `tests/fixtures/best_overview_sizes.json` |
| Brotli declaration-off refresh, 229 outputs (§254) | `compression-experiments/brotli-default-off-publication-20261017/publication.json` | `9279a171feff32151a44e7d2f41d3042abdc611bdd2ecf72c3b4bb724eeed22d` | `png_prediction_sizes.json`, `ffpr_compressor_sizes.json` |
| Lossy primary outputs, 24 PDFs (LOSSY-06) | `lossy-quality/q75-matched-20261020/metrics.json` | `69c190040942c681f3b3a466cd4dbdf038264eb1145fcbab7ea83be359b63b74` | `lossy_quality_sizes.json` |
| Lossy stream controls, 60 PDFs (LOSSY-06) | `lossy-controls/q75-matched-20261020/metrics.json` | `674a9e88d9f5cc7f0ea9a350864fa2155f448589a1d12741723a435991fedb83` | `lossy_controls_sizes.json` |
| JPEG/JPEG2000 quality calibration, image-only | `jpeg-jpx-research/stock-vs-qfactor-20261020/results.jsonl` | `9294f0f4a2150bc77140f4c1177e13ed561e2578215348606e74f1e72b32f1ef` | — |
| Measured superset after B114, 252 + 62 outputs | `integrated-compression/post-b114-300dpi-20261016/` | see its `identity.json` | — |

Older studies remain under `.tmp/` and in git history; they are not current
cells. Runners are `tools/bench_*.py`; publishers (`tools/publish_*.py`)
validate a completed run against its manifest and then fill the tagged rows.

To re-measure the lossy rows (24 complete PDFs, then 60 stream controls):

```sh
nice -n 10 ./.venv/bin/python tools/bench_lossy_quality.py --output .tmp/lossy-quality/<label>
./.venv/bin/python tools/publish_lossy_quality.py .tmp/lossy-quality/<label>/metrics.json
nice -n 10 ./.venv/bin/python tools/bench_lossy_controls.py --baseline .tmp/lossy-quality/<label>/metrics.json --output .tmp/lossy-controls/<label> --workers 3
./.venv/bin/python tools/publish_lossy_controls.py .tmp/lossy-controls/<label>/metrics.json
```

Each publisher audits the completed run and outputs its fixture and the
tagged table cells. The controls runner only accepts a lossy run whose
fixture is already published. `--resume` is only for an unchanged
interrupted run.

## Design traps and failed attempts

- **Benchmark settings that differ from the product's.** The first Brotli
  tables included the compatibility-declaration metadata the product no
  longer writes; 229 outputs had to be re-measured (§254). Benchmarks must
  use the product's actual defaults.
- **Equal quality numbers are not equal quality.** JPEG2000 "q75" as a fixed
  26:1 ratio was about 8 SSIMULACRA2 points better than JPEG q75 on a typical
  page, so the old lossy tables mixed quality with compression and showed
  JPEG2000 larger in 9 of 12 pairs. Calibrate the setting and check measured
  quality before reading a lossy size comparison.
- **Comparing a control with a file from another table.** Container
  differences from re-subset fonts or random PDF IDs can exceed the effect
  under test. Compare only files saved as a pair, with fixed-width IDs and
  without re-subsetting prepared fonts.
- **A benchmark input already in the codec under test.** Using an
  already-JBIG2 scan as the BW input made JBIG2 rankings meaningless (§233).
- **Mixed resolutions across rows.** Rows at different DPI are not
  comparable; everything is measured at 300 DPI (§225).
- **Whole-DPI rounding (B114).** Rounding a near-300 density up to 301 DPI
  created a real resampling step that changed source samples and could grow
  an already-compressed scan. Keep fractional density.
- **A failed preparation is not a compressor result.** "PREP FAILED" cells
  meant the shared preparation was invalid; such cells get no size or rank
  until the preparation is fixed.
- **Scripts that rewrite prose.** Earlier publishers replaced sentences and
  regenerated whole sections, which turned this page into a run log.
  Scripts now fill tagged numbers only (§§282/283).
