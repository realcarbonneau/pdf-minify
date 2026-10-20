# Lossy image quality — JPEG and JPEG2000

How the app's one **Quality** control drives JPEG and lossy JPEG2000, what
"the same quality" has to mean for both, and the measured evidence behind
the JPEG2000 mapping. Sizes of complete PDFs are in
[COMPRESSION_BENCHMARKS.md](COMPRESSION_BENCHMARKS.md).

## Rulings (verbatim)

Exact designer text from `DESIGNER_VERBATIM.md`. Text outside the fenced
quotes is not the designer's.

### One familiar control

**§262** (2026-10-18)

```text
We have to use the parameter that users are most used to, that is the most common.
```

**§264** (2026-10-18)

```text
change the quality for both to 75, but also do research on what the best comparable setting would be for the sampling and if there are other settings that we should adjust to make more comparable between the two.
```

**§265** (2026-10-19)

```text
I don't care so much about lossless, it's not core to the app, it might be never used or only for extreme edge cases, highly doubtfull.  What is important is that the lossy compression works and better than jpeg.   So please review modern best practices for setting and fixing all these jpeg2000 options for the objectives I had previously stated (300dpi, screen view, etc.).  User expect these to be set correctly and only have a quality slider AND most importantly that the benchmark be of comparable visual quality betwee the two JP*.
```

**§275** (2026-10-19)

```text
I already ruled the use case, this is for making pdfs smaller, thuse lossless or super high quality images are not a concern, we want something simple for most users.
```

### Same number, same quality, one setting

**§266** (2026-10-19)

```text
If you don't have something better, backed by solid sources, the working assumption is that "equal slider values count as comparable visual quality.".   When you state " equal slider values won’t count as comparable visual quality." without any benchmarking options, that statement has no value nor usefulness, it only leads to ***NO BENCHMARKS*** and thus no information, which worse than a good enough comparison baseline.
```

**§269** (2026-10-19)

```text
I ruled that both JPG and JPEG2000 will have the same 0-100 quality scale that matches common user expectations.  So the benchmark and documentation q must be on the same scale.  You are saying that JPEG2000 is set at q56 will everything else held approximatey equal?  This is my request, to try to find the best possible equivalance between the two to make the size benchmarks comparable, or else benchmarking is useless.  Do you understand this??
```

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

**§270** (2026-10-19)

```text
You previously did the research, make a document with all your research on prior work and public studies comparing JPG and JPEG2000.  You said you had found some that had matched image quality visually and numerically, I thought you had derived the equivalent quality settings from both?  If not, do that work and review the past conversation histories in this harness and sequence before compaction.
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
pages, which is why the earlier complete-PDF benchmarks showed it larger.
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
  JPEG2000 ratio from the JPEG file's ratio (the §267 study anchors) made
  the comparison circular and gave every page a different setting; §271
  rejected it.
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
