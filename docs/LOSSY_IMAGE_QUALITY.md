# Lossy image quality — JPEG and JPEG2000

How the app's one **Quality** control drives JPEG and lossy JPEG2000, what
"the same quality" has to mean for both, and the measured evidence behind
the JPEG2000 mapping. Sizes of complete PDFs are in
[COMPRESSION_BENCHMARKS.md](COMPRESSION_BENCHMARKS.md).

## Rulings (verbatim)

Exact designer text from `DESIGNER_VERBATIM.md`. Text outside the fenced
quotes is not the designer's.

### One familiar control

**§272** (2026-10-19)

```text
I had a less skiled worker program this app and documentation, but I am not sastisfied.  The first problem I have is that it was not able to derive a proper quality setting equivalence for JPEG2000 that matched JPG q75 (I think that is what I choose).  This is important for the benchmarks, because we need to set all settings as similar as possible and also follow what users expect and understand (eg q=75 quality setting, not multiple different complex settings), so that the benchmarks mean something and so that users can know what they are setting?  There is already some research done in the repo, please review and do me research if you feel that is required.
```

**§275** (2026-10-19)

```text
I already ruled the use case, this is for making pdfs smaller, thuse lossless or super high quality images are not a concern, we want something simple for most users.
```

### Same number, same quality, one setting

**§284** (2026-10-20)

```text
Ok, so a single setting is the correct direction, however, for the purpose of out benchmarking, we have to choose a single quality setting that provides the same visual results as jpg.  The reasoning is simple, if jpg q75 provides a certain compression and quality, then the newer J2K is expected to provide a smaller (or in the absolute worst case, the same size) file for the same visual quality level.  This is very simple and basic, I should not have to explain this.  Or else, benchmarks and a newer compression algorithm has no value.
```

### Colour sampling and packages

**§274** (2026-10-19)

```text
So you have equivalence or can you estimate it?  And do you think we should use "4:2:0" also by default and for benchmarks?
```

**§276** (2026-10-19)

```text
Well if if "4:2:0" matches a lower Q for JPEG2000, then that is not good, we should keep it was it was before, matching JPEG200, or reducing JPEG2000 color setting to match jpg  4:2:0, no?
```

**§278** (2026-10-20)

```text
Don't change standard packages, if you can't change JPEG2000, adjust the JPG settings to match.
```

### No automatic choice between the codecs

**§285** (2026-10-20)

```text
what is the big picture?  Is J2K generally better then JPG?  All things equal?   This is the assumption since it is newer, there would be no point in having a newer algorithm that does not provide improvements.
```

**§287** (2026-10-20)

```text
Sounds like we cannot be opinionated on the JPG/J2K for now, so let's just keep them as comparable as possible in the benchmarks and we will not have an automatic Best option for these.
```

### JPEG XL: from the original, compared by measured quality

**§309** (2026-11-03)

```text
Even though the PDFs do not permit storing JPEG XL, I want you to add that to the analysis. because I think that JPEG Excel seems to be quite performant and might eventually be included in some PDF readers. Also, we could do something where we make a reader that reads the PDF Excel version images and converts them to regular JPEG when we're viewing it, or converts them to bitmap as we're reading it, so that we can have compressed images stored, but also view them temporarily with a special reader until most readers support the JPEG Excel. Also, on this Linux, my Gwen view supports JPEG Excel, and I think we could also read the images directly for cases where the whole PDF is just a set of images. I don't know if you follow, but read the whole repository and see if you can add these tests and discuss, or at least discuss before you start doing heavy tests.
```

**§311** (2026-11-03)

```text
The assumption is that with the best wrapper in the PDF, with the best compression, there won't be any gains in compressing the JPEG internal saved binary data, nor the benchmark one. So you don't have to redo the benchmark tests, right? You're just going from the results that we already have, I think. Also for JPEG, I don't think you should be comparing identical pixels, because JPEG is already a compression of the original file, so that's not a proper comparison. So you would take the original file, compress to JPEG, take the original file, compress to Excel, and then you compare the two with quality measurements. Same thing for, so I don't see the difference between full color test A, full color test B. It's not proper to try to get the compression of a secondary compression to match another secondary compression that is a flawed comparison. Do you follow this?
```

**§314** (2026-11-04)

```text
match the quality for the images, for text, the baseline will not be jpeg anyways.  Add a second table that is the quality delta between the cell baseline and JPEGXL for the target quality that matches Photos.  The best baseliness for mostly text or BW/index text might might even be lossless, so this is generally over for actual quality to be higher
```

**§315** (2026-11-04)

```text
Ok, proceed as you suggest, more compute/memory is fine and fits the objectives of the project.
```

## Current settings

- **Quality** is one integer 0–100 per filter, default 75, shared by JPEG and
  lossy JPEG2000 (`core/quality.py`). Higher means better quality and
  usually larger files; it is not a percentage. It is disabled for other
  codecs and when JPEG2000 Lossless is checked; the stored value is kept.
- **JPEG**: Pillow with libjpeg-turbo, `quality=q`, `subsampling=0` (4:4:4),
  `optimize=True` (profile `jpeg444-huffman-v1`).
- **JPEG2000**: Pillow with OpenJPEG 2.5.4, `irreversible=True` (9/7),
  `mct=1` (RGB colour decorrelation), full-resolution components, up to six
  resolutions (fewer for tiny images), 64×64 code blocks, LRCP, one layer and
  512×512-pixel tiles (profile `jpx97-ict-tile512-v1`).
- **JPEG2000 quality mapping** `jpeg-matched-tile-psnr-v1`
  (`quality.jpx_quality_psnr`): Quality becomes one PSNR target per tile,
  the same for every image, calibrated against JPEG (§284; see
  [The JPEG2000 mapping](#the-jpeg2000-mapping-284)). q75 → 44.0 dB.
- **Explicit legacy ratios** in old recipes keep their meaning and the
  single-tile profile `jpx97-ict-v1`.
- **JPEG2000 Lossless** is a separate checkbox (reversible 5/3, no quality).
- **No automatic choice** (§287): a filter uses the codec it names. No Best
  option chooses between JPEG and JPEG2000; the benchmarks compare them at
  the same Quality.

## What "the same quality" requires

JPEG's quality number scales its quantization tables. The coarseness of
detail is fixed and the file size follows the content: on the 67 benchmark
page images, JPEG q75 compresses between 16:1 and 216:1. A JPEG2000 setting
can only match that if it also fixes quality rather than size.

Stock OpenJPEG, through Pillow, offers two controls: a target ratio
(`quality_mode="rates"`) and a target PSNR in dB (`quality_mode="dB"`),
applied to the whole image or to each tile. Neither fixes quantization. The
JPEG committee's **Qfactor** method does: it derives every wavelet band's
quantization step from one Q of 1–100, using the same scaling as libjpeg
(`50/Q` below 50, `2 − Q/50` above), colour-transform gains and visual
weights ([guideline WG1 N101553 v2, 2026](https://ds.jpeg.org/documents/jpeg2000/wg1n101553-112-COM-Controlling_JPEG_2000_quality_using_Qfactor_v2.pdf)).
Its authors designed it so that "the subjective quality of the resulting
imagery is roughly comparable to that of JPEG at the same Qfactor", tested on
8-bit 4:2:0 images up to Q85 ([HTJ2K white paper, p. 16](https://htj2k.com/wp-content/uploads/white-paper.pdf)).
Kakadu, Grok (≥ 20.3.12, AGPL) and OpenJPH (HTJ2K only) implement it;
OpenJPEG and Pillow do not, because they expose no step sizes.

## Measured comparison

### Method

- **Images**: the 67 distinct 300-DPI RGB canvases that the production
  composer prepares for the six benchmark PDFs, native and FFPR (the scan's
  FFPR canvases are identical to its native ones and counted once).
- **Reference**: JPEG q75, 4:4:4, the app's exact encoder settings.
- **Candidates**: one fixed JPEG2000 setting for every page, using the app's
  JPEG2000 profile. Qfactor was encoded with a research build of OpenJPEG
  2.5.4 that accepts explicit step sizes; in ratio and PSNR modes its output
  is byte-identical to Pillow's apart from the encoder's version comment.
  Every coding pass is kept.
- **Score**: SSIMULACRA2 (Rust implementation 0.5.2) of each decoded image
  against its original. The authors' guide: 70 high quality, 80 very high,
  90 visually lossless ([README](https://github.com/cloudinary/ssimulacra2)).
  "Gap" is JPEG2000 score minus JPEG q75 score on the same page; positive
  means JPEG2000 looks better.
- Data, harness and encoder patch:
  `.tmp/jpeg-jpx-research/stock-vs-qfactor-20261020/` (`results.jsonl`,
  SHA-256 `9294f0f4a2150bc77140f4c1177e13ed561e2578215348606e74f1e72b32f1ef`).
  These are image-only results, not complete-PDF sizes.

### Results by control

Every row is an actually encoded setting, applied unchanged to all 67 pages.

| JPEG2000 control and setting | Standard packages? | Median gap | 10th–90th percentile | Worst page | Pages within ±5 | Total bytes vs JPEG |
|---|---|---:|---:|---:|---:|---:|
| Ratio 26:1 (old q75) | yes | +8.1 | −1.2 to +11.8 | −15.1 | 28% | 1.05 |
| Ratio 60:1 | yes | −2.0 | −41.6 to +5.6 | −75.1 | 39% | 0.49 |
| PSNR 40 dB, whole page | yes | −0.1 | −28.6 to +8.1 | −68.3 | 43% | 0.70 |
| PSNR 40 dB per 512-pixel tile | yes | −7.5 | −26.6 to +4.1 | −38.3 | 36% | 0.78 |
| **PSNR 44 dB per 512-pixel tile (new q75)** | yes | **+0.3** | **−16.6 to +9.0** | **−26.0** | **48%** | **1.02** |
| PSNR 46 dB per 512-pixel tile | yes | +3.2 | −10.2 to +10.9 | −17.1 | 40% | 1.15 |
| Qfactor Q75 | no (patched encoder) | +0.8 | −4.0 to +4.0 | −5.7 | 96% | 0.66 |

FFmpeg's built-in JPEG 2000 encoder, which has a constant-quality setting,
needs 3.5 times the bytes of OpenJPEG at the same score on a test page; it
would misrepresent JPEG2000.

### Results by document

Mean gap and mean size ratio (JPEG2000 / JPEG q75) per document and mode.

| Pages | n | Old q75: ratio 26:1 | New q75: 44 dB per tile | Qfactor Q75 |
|---|---:|---:|---:|---:|
| Flat-color artwork, native | 1 | +5.8 / 1.60 | −19.1 / 0.46 | +0.7 / 0.37 |
| Flat-color artwork, FFPR | 1 | +5.9 / 1.63 | −19.0 / 0.47 | +0.7 / 0.40 |
| Technical illustrations, native | 9 | +4.3 / 1.33 | −10.8 / 0.37 | −3.5 / 0.25 |
| Technical illustrations, FFPR | 12 | +10.0 / 1.27 | +2.1 / 0.95 | +0.6 / 0.67 |
| Mixed text/images, native | 2 | +3.3 / 0.99 | −12.5 / 0.30 | −3.8 / 0.24 |
| Mixed text/images, FFPR | 9 | +11.5 / 1.16 | +2.1 / 0.95 | +3.5 / 0.73 |
| Native text/vectors, FFPR | 6 | +5.1 / 0.83 | +9.4 / 0.99 | +3.6 / 0.75 |
| Color photos, native | 8 | +6.3 / 1.95 | −4.8 / 0.89 | −3.9 / 0.45 |
| Color photos, FFPR | 8 | −5.2 / 0.68 | +9.4 / 1.19 | −0.7 / 0.69 |
| BW scan | 11 | +9.6 / 1.34 | −3.6 / 0.81 | +2.9 / 0.69 |

The old 26:1 gave JPEG2000 noticeably *better* quality than JPEG q75 on most
pages, so complete-PDF sizes at that ratio showed it larger.
A PSNR target, even per tile, still follows content type: flat artwork and
mostly blank native pages come out worse, busy full-page renders better.

### Equal quality, page by page

Bytes the standard JPEG2000 encoder needs to look exactly like JPEG q75 on
each page, as a ratio to JPEG's bytes; below 1.00 is smaller. Each page's
JPEG2000 size is interpolated between its two measured per-tile PSNR targets
that bracket JPEG's score.

| Pages | Pages matched | Median | Range |
|---|---:|---:|---:|
| Native text/vectors, FFPR (the W-9 form) | 6 of 6 | 0.72 | 0.57–0.88 |
| BW scan | 10 of 11 | 0.82 | 0.75–0.95 |
| Mixed text/images, FFPR | 9 of 9 | 0.86 | 0.76–1.25 |
| Color photos, FFPR | 8 of 8 | 0.86 | 0.80–1.03 |
| Technical illustrations, FFPR | 12 of 12 | 0.91 | 0.64–1.24 |
| Technical illustrations, native | 5 of 9 | 0.63 | 0.20–1.23 |
| Mixed text/images, native | 1 of 2 | 0.15 | — |
| Color photos, native | 8 of 8 | 1.21 | 0.93–1.31 |
| Flat-color artwork, native and FFPR | 0 of 2 | — | — |

Unmatched pages score below JPEG q75 even at the highest target measured,
52 dB per tile. Pages of letters (forms, scans, full-page renders of text)
need 9–28% fewer bytes; embedded colour photos need 21% more. Which codec is
smaller at equal quality depends on the page and on the encoder. The fixed
q75 target turns the text-page advantage into better quality at about the
same size, as in the W-9 and newspaper full-page rows of the benchmarks.

### Colour sampling (4:2:0)

- JPEG 4:2:0 q75 against JPEG 4:4:4 q75: median −1.0 points and 10% fewer
  bytes in total; up to 35% fewer on colour artwork, and 8% fewer with no
  quality change on grey scans.
- JPEG2000 cannot store 4:2:0 compatibly: subsampled components (sYCC)
  decode correctly in MuPDF, Ghostscript and Pillow but **wrongly in Poppler
  25.03** (PSNR 15 dB), which most Linux viewers use. Dropping the finest
  colour band inside an ordinary full-size codestream is compatible, but it
  needs explicit step sizes (Qfactor).
- With that colour-reduced Qfactor, JPEG 4:2:0 q75 is matched at about Q70
  rather than Q75 (median gap +0.6 at Q70, +2.5 at Q75). §276 rejects a
  lower number for the same quality, and §278 rules out the patched encoder,
  so **JPEG stays 4:4:4**, matching what JPEG2000 does.

### Reader compatibility of the Qfactor files

Qfactor changes only the step sizes in the standard QCD/QCC markers; the
file is an ordinary JPEG 2000 Part 1 codestream. MuPDF, Poppler (decoded
samples via `pdfimages`) and Ghostscript reproduce Pillow's decoded pixels
exactly, and FFmpeg's independent decoder agrees within ±1 level.

## The JPEG2000 mapping (§284)

For the benchmarks and for users, JPEG2000 at Quality *q* has to look like
JPEG at *q*, through one setting used for every page. With standard packages
(§278) the best available control is a PSNR target per 512-pixel tile: it
has the narrowest spread of the stock controls, and smaller 256-pixel tiles
produced some far worse pages (worst −79).

At each anchor the target was chosen so that the median quality difference
from JPEG at the same Quality is zero over the 67 page images, and then
measured directly:

| Quality | JPEG2000 target (dB per tile) | Median gap | 10th–90th percentile | Pages within ±5 | Total bytes vs JPEG |
|---:|---:|---:|---:|---:|---:|
| 50 | 39.5 | +0.2 | −23.6 to +14.5 | 27% | 1.01 |
| 60 | 40.5 | −0.2 | −22.9 to +13.2 | 30% | 0.98 |
| 75 | 44.0 | +0.3 | −16.6 to +9.0 | 48% | 1.02 |
| 90 | 50.5 | +0.3 | −6.6 to +4.0 | 85% | 1.02 |

Between anchors the target follows straight lines, which continue beyond
q50 and q90 (q0 → 34.5 dB, q100 → 54.8 dB). Those ends are not calibrated;
low and very high qualities are not this app's use (§275).

What this means:

- **On a typical page JPEG2000 q75 now looks like JPEG q75**, and the
  complete-PDF benchmarks compare sizes at that quality.
- **Single documents still differ in both directions** (table above): flat
  colour artwork about 19 points worse, native-mode pages 5–13 worse,
  full-page photo and form pages about 9 better. The benchmark page lists
  these gaps beside the lossy rows.
- **Complete PDFs at q75** ([benchmarks](COMPRESSION_BENCHMARKS.md#overview--final-complete-file-bytes)):
  JPEG2000 is smaller in 9 of 12 pairs, larger in 2 and tied in 1. Where it
  is much smaller (flat artwork −52%, native technical and mixed pages
  −35% to −37%) it also looks worse; where it looks better (full-page photo
  and form renders) it is the same size or larger.
- **Summed over all page images, stock JPEG2000 is about the size of JPEG**
  (+2%), dominated by the large full-page photo renders. OpenJPEG's rate
  control has no visual weighting, so it spends bits on detail that does not
  show. The JPEG committee's Qfactor, with the same codestream format, would
  be 34% smaller at matched quality and track JPEG on 96% of pages, but needs
  a patched encoder (excluded by §278).

## JPEG XL (analysis only)

JPEG XL is not an app setting: no PDF reader opens it ([DROPPED.md](DROPPED.md)
D1). The benchmarks measure it as an analysis (§309), and for JPEG it is
encoded from the original page images, never from JPEG's output (§311).
The benchmarks' JPEG rows use one distance matched to JPEG q75 on
photographs ([below](#jpeg-xl-matched-on-photographs-314);
[COMPRESSION_BENCHMARKS.md](COMPRESSION_BENCHMARKS.md#image-codec--jpeg-xl-versus-the-current-codec)).
The 67-page calibration first matched the median page and shows why that
does not work for JPEG XL.

- **Encoder**: libjxl 0.11.2 `cjxl`. Its quality control is the *distance*,
  a target visual error in JND units: lower is better, 1.0 is "visually
  lossless", and the recommended range is 0.5 to 3.0. *Effort* (1–10, default
  7) trades encoding time for size. For images over 2048 pixels, effort 7
  below distance 3.0 encodes in chunks by default, "at the cost of
  compression density" (libjxl); the benchmarks encode whole images
  (`--patches=1`, §315). The 67-page calibration below measured only
  distances of 3.0 and above, which are whole-image by default.
- **Method**: as for JPEG2000 above. The same 67 page images, prepared
  before the B116 repair; JPEG q75 re-encoded with the app's encoder and
  checked byte for byte against the reference results; one fixed setting
  for every page; SSIMULACRA2 0.5.2 of each decoded image against its
  original.
- **Metric caveat**: SSIMULACRA2 comes from Cloudinary, one of JPEG XL's
  developers, so PSNR is listed as well. JPEG q75's median PSNR on these
  pages is 40.2 dB, measured on the benchmark files' re-composed images.
- Data and harness: `.tmp/jxl/calibration-20261103/results.jsonl` (SHA-256
  `e65c6938bd2dc68319c129f6b8c53eddb5aa29be1f7446f98cd7d70717c57baf`),
  `tools/bench_jxl.py`. These are image-only results.

### JPEG XL results by setting

Every row is an encoded setting, applied unchanged to all 67 pages.

| JPEG XL setting | Median gap | 10th–90th percentile | Worst page | Pages within ±5 | Total bytes vs JPEG | Median PSNR |
|---|---:|---:|---:|---:|---:|---:|
| Distance 3.0, effort 7 | +4.6 | −4.4 to +9.5 | −8.6 | 46% | 0.35 | 47.6 dB |
| Distance 4.0, effort 7 | +1.5 | −6.9 to +9.0 | −12.6 | 33% | 0.30 | 46.9 dB |
| **Distance 4.5, effort 7 (median match)** | **+0.5** | **−8.4 to +8.3** | **−16.0** | **25%** | **0.27** | **45.5 dB** |
| Distance 5.0, effort 7 | −1.5 | −10.6 to +7.5 | −19.7 | 31% | 0.26 | 44.9 dB |
| Distance 6.0, effort 7 | −4.0 | −13.5 to +6.7 | −27.2 | 31% | 0.23 | 43.4 dB |
| Distance 3.0, effort 9 | +4.2 | −6.3 to +10.7 | −11.0 | 31% | 0.37 | 46.9 dB |
| Distance 4.0, effort 9 | +1.2 | −9.5 to +9.6 | −15.3 | 28% | 0.31 | 45.2 dB |

Effort 9 gave larger files and lower scores than effort 7 at both distances
measured, so it was stopped there. `cjxl`'s own Quality 75 is distance 2.35
(byte-identical output); it would look better than JPEG q75 on the median
page, since distance 3.0 already does.

### JPEG XL results by document

Mean gap / total bytes ratio (JPEG XL / JPEG q75) per document and mode, at
effort 7.

| Pages | n | Distance 3.0 | Distance 4.5 | Distance 6.0 |
|---|---:|---:|---:|---:|
| Flat-color artwork, native | 1 | +1.5 / 0.29 | +1.1 / 0.24 | −1.8 / 0.19 |
| Flat-color artwork, FFPR | 1 | +1.5 / 0.31 | +1.1 / 0.26 | −1.8 / 0.21 |
| Technical illustrations, native | 9 | −4.5 / 0.26 | −6.5 / 0.19 | −11.4 / 0.15 |
| Technical illustrations, FFPR | 12 | +4.8 / 0.36 | +1.2 / 0.29 | −2.8 / 0.25 |
| Mixed text/images, native | 2 | −3.7 / 0.28 | −3.8 / 0.22 | −7.8 / 0.17 |
| Mixed text/images, FFPR | 9 | +8.7 / 0.11 | +7.4 / 0.09 | +5.3 / 0.08 |
| Native text/vectors, FFPR | 6 | +9.9 / 0.07 | +8.1 / 0.06 | +7.0 / 0.05 |
| Color photos, native | 8 | −4.3 / 0.41 | −9.8 / 0.29 | −15.5 / 0.22 |
| Color photos, FFPR | 8 | +1.5 / 0.44 | −4.9 / 0.34 | −10.8 / 0.29 |
| BW scan | 11 | +7.2 / 0.58 | +7.2 / 0.49 | +4.8 / 0.44 |

### JPEG XL at equal quality, page by page

Bytes JPEG XL needs to look exactly like JPEG q75 on each page, as a ratio to
JPEG's bytes, interpolated between the two measured effort-7 distances that
bracket JPEG's score. Only pages whose scores cross JPEG's between distance
3.0 and 6.0 can be matched.

| Pages | Pages matched | Median | Range | Unmatched |
|---|---:|---:|---:|---|
| Flat-color artwork, native and FFPR | 2 of 2 | 0.24 | 0.22–0.25 | — |
| Technical illustrations, FFPR | 7 of 12 | 0.26 | 0.23–0.39 | 4 better at 6.0, 1 worse at 3.0 |
| Color photos, FFPR | 5 of 8 | 0.21 | 0.18–0.55 | 3 worse at 3.0 |
| Mixed text/images, FFPR | 1 of 9 | 0.16 | — | 8 better at 6.0 |
| Native text/vectors, FFPR | 0 of 6 | — | — | all better at 6.0 |
| BW scan | 0 of 11 | — | — | all better at 6.0 |
| Technical illustrations, native | 0 of 9 | — | — | all worse at 3.0 |
| Mixed text/images, native | 0 of 2 | — | — | both worse at 3.0 |
| Color photos, native | 0 of 8 | — | — | all worse at 3.0 |

- **44 of 67 pages need fewer bytes in JPEG XL at equal quality**: the 15
  matched pages (median 0.25 of JPEG's bytes, 0.16–0.55), and 29 pages that
  still look better at distance 6.0 with at most 0.46 of JPEG's bytes.
- **The other 23 still look worse at distance 3.0** (by up to 8.6 points,
  with 0.11–0.60 of JPEG's bytes): every native-mode photo, illustration and
  newspaper image, three FFPR photo pages and one FFPR illustration page.
  Their equal-quality size was not measured.

What this means:

- **One distance tracks JPEG q75 less closely than JPEG2000's mapping**: 25%
  of pages within ±5 at the matched setting, against 48% for JPEG2000's per-tile
  PSNR target. Typeset full-page renders and the scan come out better than
  JPEG, embedded photographs and native-mode illustrations worse.
- **Matching the median page leaves photographs well below JPEG.** At
  distance 4.5 the native photo pages score 9.8 lower while text renders
  score 7–8 higher. Text pages would not use JPEG anyway, so the benchmarks
  match on photographs instead (§314, below).
- **Where equal quality could be measured here, JPEG XL needs about a
  quarter of JPEG's bytes.** Of the 23 pages still worse at distance 3.0,
  the eight photograph pages were measured at lower distances (below): at
  equal mean quality they need 0.54 of JPEG's bytes.

### JPEG XL matched on photographs (§314)

The benchmarks' JPEG rows use one distance for every page: the measured
distance whose mean SSIMULACRA2 on the brochure's eight photograph pages
(Color photos, native, the JPEG row's own images) is closest to JPEG q75's.
These are the swap's own originals, re-composed by the current composer
(after the B116 repair) and checked against the recorded sample hashes,
scored exactly as the benchmark cell is.

| Distance (effort 7) | Mean gap | Median gap | Range over the 8 pages | Total bytes vs JPEG | Mean PSNR gap |
|---:|---:|---:|---:|---:|---:|
| 1.0 | +4.10 | +4.39 | +1.2 to +7.6 | 0.95 | +3.60 dB |
| 1.25 | +3.40 | +3.49 | +1.5 to +6.2 | 0.82 | +2.50 dB |
| 1.5 | +2.39 | +2.43 | +0.8 to +4.6 | 0.72 | +1.70 dB |
| 1.75 | +1.39 | +1.36 | −0.2 to +3.1 | 0.64 | +0.89 dB |
| 2.0 | +0.66 | +0.51 | −0.6 to +2.2 | 0.57 | +0.12 dB |
| 2.05 | +0.33 | +0.10 | −0.5 to +1.5 | 0.56 | +0.09 dB |
| 2.1 | +0.08 | −0.15 | −1.1 to +1.4 | 0.55 | −0.02 dB |
| **2.15** | **+0.01** | **−0.20** | **−1.0 to +1.2** | **0.54** | **−0.17 dB** |
| 2.2 | −0.19 | −0.40 | −0.9 to +1.1 | 0.53 | −0.27 dB |
| 2.25 | −0.42 | −0.56 | −1.2 to +0.8 | 0.52 | −0.41 dB |
| 2.5 | −1.54 | −1.83 | −2.3 to +0.0 | 0.48 | −1.02 dB |
| 3.0 | −3.95 | −4.01 | −6.1 to −2.3 | 0.41 | −2.13 dB |

Distance 2.15 is chosen: its mean gap is +0.01, every photograph is within
±1.2 of JPEG q75, and PSNR agrees (−0.17 dB). At equal quality the
photographs need 0.54 of JPEG's bytes, almost twice the 0.29 the
median-matched distance 4.5 gave, because 4.5 left them 9.5 points worse.
Every encode is whole-image (§315); `cjxl`'s chunked default chose the
same distance with 0.56. `cjxl`'s own Quality 75 is distance 2.35, between
the measured 2.25 (−0.42) and 2.5 (−1.54): on these photographs it is
close to JPEG q75, slightly below.

Data: `.tmp/jxl/photo-match-whole-20261104/results.jsonl` (SHA-256
`4805de64d91bd5bd2a44d78e887a7c4b07be290ce11bc9b7f35f10127713046a`), `tools/bench_jxl.py match`.

## Evidence from published studies and tools

| Source | What it shows | Limits |
|---|---|---|
| [Skodras et al. 2001](https://www.csd.uoc.gr/~hy371/bibliography/JPEG2000.pdf#page=17) | At visually comparable quality, JPEG2000 files 11–53% smaller than JPEG, more so at low bit rates | Historical encoders; ratios, not quality settings |
| [Steingrímsson and Simon 2003](https://library.imaging.org/admin/apis/public/api/ist/website/downloadArticle/jist/47/6/art00015) | Observers' matches vary strongly with content and often favour JPEG below about 50:1; equal PSNR favours JPEG2000 more than observers do | No mapping of library quality settings |
| [Allen et al. 2007](https://library.imaging.org/admin/apis/public/api/ist/website/downloadArticle/jist/51/3/art00009#page=10) | Average observer match about 40:1 JPEG ≈ 45:1 JPEG2000, 60:1 ≈ 73:1 | Graph readings; 16 photo scenes, other encoders |
| [FADGI 2013](https://www.digitizationguidelines.gov/still-image/documents/JP2LossyCompression.pdf#page=15) | Text pages need local inspection; ratios across one collection spread from 8:1 to 351:1 | Archival masters, no JPEG mapping |
| HTJ2K white paper and Qfactor guideline (above) | Q designed to match JPEG's Q subjectively | 4:2:0, Q ≤ 85; not in OpenJPEG |
| Tool conventions | darktable: ratio `101 − q`; libvips `Q`: PSNR in dB, default 48 chosen to give "about the same filesize as regular jpg Q75"; ImageMagick and GIMP: PSNR in dB; Acrobat: undocumented levels | None is a quality match to JPEG |

## Saved recipes and compatibility

- Recipes store `jpeg_q` for JPEG and `jpx_q` for JPEG2000. A recipe with a
  legacy explicit `rate` keeps that ratio; `rate` and `jpx_q` together are
  rejected. Lossless ignores both.
- The mapping name and both encoder profiles are part of each filter's
  effective identity, so a completed file from another mapping or profile is
  never reused as current output.
- Saved q values never change with the mapping. A new mapping gets a new
  identity, so every JPEG2000 filter re-encodes once.

## Design traps and failed attempts

- **A compression ratio relabelled as quality.** `101 − q` made JPEG2000
  "q75" about 8 points better than JPEG q75 and larger, so the benchmarks
  compared quality, not compression. A size target cannot track a
  quantization-based quality.
- **Fitting JPEG2000 to the JPEG result per image.** Choosing each image's
  JPEG2000 ratio from the JPEG file's ratio (the 2007 study's anchors) made
  the comparison circular and gave every page a different setting; one
  setting for every page is required (§284).
- **Taking literature ratios as settings.** The 2007 observer ratios came
  from other encoders and photo scenes. Turned into a fixed q56, they scored
  21 points below JPEG q75 on our photo page.
- **PSNR targets.** A whole-image PSNR averages over blank paper; on mostly
  blank native pages images then degrade far below JPEG (−68 points on the
  worst page). PSNR also favours JPEG2000's blur over JPEG's blocking.
- **True 4:2:0 JPEG2000.** Subsampled sYCC components break in Poppler.
  Reduce colour detail within full-size components instead.
- **Pillow's JPEG2000 defaults.** Without options Pillow writes the
  reversible 5/3 wavelet without colour decorrelation (`mct=0`); lossy output
  needs `irreversible=True, mct=1`. Pillow ignores `quality=` for JPEG2000:
  `quality_layers=[75]` means 75:1 in rates mode and 75 dB in dB mode.
- **Expecting the codec to win with a non-perceptual encoder.** At equal
  median quality stock OpenJPEG is about JPEG's size, while the same format
  with Qfactor quantization is a third smaller. A size comparison measures
  the encoder's rate control as much as the format.
- **A weaker encoder as the codec's representative.** FFmpeg's JPEG2000
  encoder has no colour decorrelation and small code blocks; at equal
  quality it is 3.5 times larger than OpenJPEG.
