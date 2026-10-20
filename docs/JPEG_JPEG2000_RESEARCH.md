# JPEG versus JPEG2000 — published evidence and matching quality settings

Designer §§262–271; TODO §264; LOSSY-04/05. Research checked 2026-10-19.
This document owns the prior-work review and quality equivalence. Actual
complete-PDF size tables stay in [INTEGRATED_COMPRESSION.md](INTEGRATED_COMPRESSION.md).
Encoder/control details are in [LOSSY_IMAGE_QUALITY.md](LOSSY_IMAGE_QUALITY.md).

**Current experiment ruling (§271):** use one fixed JPEG q75/JPEG2000 q75
baseline at 300 DPI for every input and native/FFPR mode. JPEG2000's stable
`101 − q` convention makes q75 a 26:1 target. Per-image fits below are
diagnostic evidence only, not approved benchmark settings; their PSNR-control
numbers are backend dB targets, not values on the app's quality slider.
LOSSY-05 corrects the product mapping and refreshes every affected size table.
The working baseline does not claim proven equal visual quality.

Selection evidence: the retained photographic FFPR diagnostic scores
JPEG2000 q56 at 54.328 versus JPEG q75 at 75.268, so the literature-derived
q56 is not a suitable universal replacement. Fixed JPX q75 meets or exceeds
the JPEG reference's metric score on all eleven tested first canvases; that
supports a conservative working baseline, not an all-page equivalence claim.
Canvas metrics also do not certify original appearance after native overlay;
the actual-PDF B116 observation is documented in the integrated analysis.

## Finding recovered from the earlier research

The earlier research did find human-observer comparisons and numerical
matching results. It derived conditional JPEG2000 candidates from compression
ratios, **not a verified fixed JPEG2000 q equivalent to JPEG q75**. In
particular, JPEG 40:1 → JPEG2000 approximately 45:1 gives q56 on the existing
`101 − ratio` scale only if the actual JPEG q75 reference achieves 40:1 on
that image. The 2001 and 2003 comparisons below were also cited earlier;
the later implementation relied on the 2007 average-curve estimates instead.

LOSSY-02/03's measured files are real, but their JPEG2000 q75 labels refer
to the subsequent reference-normalized mapping. They do not measure fixed
q56 or establish visual equivalence. Their apparent savings are not an
independent quality test: a smaller target budget was chosen by design.
§§269/270 require actual q settings on the stable user-facing scales.

### Recovered decision sequence

The accessible earlier Codex transcript and local session export were
reviewed for these codec decisions. The export predates this research;
the transcript supplied the study links, conditional derivations and the
previously downloaded full Qfactor v2 guideline. Raw conversation files
are not copied into the repository.

The sequence matters: the initial q50/r192 comparisons were not matched;
q90 and then q75 became explicit working baselines; the darktable ratio
convention supplied a reproducible numeric scale; the 2007 graph supplied
conditional ratio candidates. The subsequent JPEG-reference normalization
used those candidates to set the byte budget, without independently
measuring reconstructed quality. That last step did **not** complete the
missing q75-equivalence experiment. This document separates the recovered
evidence, derived starting points and newly measured settings.

## Public studies: what was actually compared

### 2000 — equal bit budgets and numerical reconstruction error

Ebrahimi, Santa Cruz, Askelöf, Larsson and Christopoulos, *JPEG 2000 still
image coding versus other standards*, SPIE 4115, pp. 446–454. This is the
release-era numerical comparison cited in the earlier discussion, not the
source of a JPEG-q75 ↔ JPEG2000-q conversion. The later authors' overview
also presents comparative rate-distortion results. Keep equal-bit-budget
PSNR distinct from an observer-matched setting. [Authors' overview](https://infoscience.epfl.ch/record/111816/files/26%20The%20JPEG2000%20still%20image%20coding%20system%20-%20An%20overview.pdf).

The original `jpeg.org/public/wg1n1816.pdf` link is not currently retrievable;
do not claim a newly verified original data table from that inaccessible
link. The two directly retrieved visual studies below provide stronger
evidence for the specific quality-matching question.

### 2001 — published visual-comparison savings

Skodras, Christopoulos and Ebrahimi, *The JPEG 2000 Still Image Compression
Standard*, IEEE Signal Processing Magazine, September 2001, p. 52, reports
these average visual-comparison results against optimized-Huffman baseline
JPEG. These are historical image-codec results, not current library q values
or complete-PDF savings. [Paper, PDF page 17](https://www.csd.uoc.gr/~hy371/bibliography/JPEG2000.pdf#page=17).

| JPEG2000 bits/pixel | Reported JPEG2000 file-size reduction versus visually comparable JPEG |
|---:|---:|
| 1.00 | 11% |
| 0.75 | 18% |
| 0.50 | 36% |
| 0.25 | 53% |

The percentages are different operating points, not a constant expected
advantage. Do not infer that every JPEG2000 output should beat JPEG, or
substitute these numbers for measurements of this project's PDFs.

### 2003 — directly matched visual quality and separately matched PSNR

Steingrímsson and Simon, *Perceptive Quality Estimations: JPEG 2000 versus
JPEG*, JIST 47, pp. 572–585. The paper uses interactive visual preference
boundaries; its larger evaluation covers 108 images and 297 examinations.
It separately calculates equivalent-PSNR curves. Those curves favor
JPEG2000 more consistently than observers do: visual results vary strongly
with image content, and frequently favor JPEG below approximately 50:1.
This is direct evidence that matching PSNR alone is not sufficient for this
project's visual-quality baseline. [Paper, especially Figs. 10–14 and conclusions](https://library.imaging.org/admin/apis/public/api/ist/website/downloadArticle/jist/47/6/art00015).

Its ratios and image-specific boundaries are useful search evidence, but
it does not calibrate Pillow/libjpeg-turbo q75 against current OpenJPEG q.
The difference between the studies is a reason to test the actual prepared
images, not a reason to avoid useful benchmarks.

### 2007 — observer curves and PSNR on the same image set

Allen, Triantaphillidou and Jacobson, *Image Quality Comparison Between
JPEG and JPEG2000. I. Psychophysical Investigation*, JIST 51, pp. 248–258.
Sixteen scenes, ten observers and ratios 20/40/60/80:1 were assessed in
paired screen comparisons. JPEG used Advanced JPEG Compressor 4.1; JPEG2000 used
Lurawave SmartCompress 3.0. This is not our current encoder/profile setup.
The displayed test images were 317×476 pixels at 100%, not our complete
300-DPI page canvases.
Fig. 14 averages all scenes except “African tree.” [Paper, methods and Fig. 14](https://library.imaging.org/admin/apis/public/api/ist/website/downloadArticle/jist/51/3/art00009#page=10).

The previously derived matches **40:1 → approximately 45:1** and
**60:1 → approximately 73:1** are interpolated graph readings, not tabulated
q settings. The paper's visual and PSNR results are not interchangeable,
and its scene-specific exceptions remain relevant. Outside 40–60:1,
the old implementation's fixed relative-gain extension was an additional
project heuristic, not a demonstrated result of this paper.

## Deriving useful candidates, rather than renaming quality

Use the familiar JPEG2000 scale already selected from darktable's
implementation: `r = 101 − q`, with integer q in 0–100. Thus q75 means
26:1 and q56 means 45:1, consistently in recipes, GUI and analysis.
This is a documented application convention, not the JPEG committee's
Qfactor algorithm. [darktable 5.2.1 encoder](https://github.com/darktable-org/darktable/blob/release-5.2.1/src/imageio/format/j2k.c#L324-L335).

For a 24-bit RGB source, the algebra for a study point is:

```text
JPEG2000 ratio = 24 / JPEG2000 bits-per-pixel
JPEG ratio at reported visual match = JPEG2000 ratio × (1 − saving)
JPEG2000 q candidate = 101 − JPEG2000 ratio
```

These are **derived starting candidates**, not newly measured quality matches:

| Evidence | JPEG ratio at match | JPEG2000 ratio | JPEG2000 q on the fixed scale |
|---|---:|---:|---:|
| 2001, 1.00 bits/pixel, 11% saving | 21.36:1 | 24:1 | 77 |
| 2001, 0.75 bits/pixel, 18% saving | 26.24:1 | 32:1 | 69 |
| 2001, 0.50 bits/pixel, 36% saving | 30.72:1 | 48:1 | 53 |
| 2001, 0.25 bits/pixel, 53% saving | 45.12:1 | 96:1 | 5 |
| 2007 average-curve estimate | approximately 40:1 | approximately 45:1 | approximately 56 |
| 2007 average-curve estimate | approximately 60:1 | approximately 73:1 | approximately 28 |

The 24-bit calculation is our assumption for our RGB canvases, not an
assertion that every historical test image had that representation. It
must not be applied to raw PDF byte ratios or silently generalized to
grayscale data. The studies do not determine JPEG's q for those ratios:
**encode JPEG q75 on the actual source pixels to supply that missing link**.
Then independently test nearby JPEG2000 q settings; do not enforce the
literature's percentage savings in the measurement.

The differing study candidates make a sweep necessary. The stable q scale
also has endpoints: if a match lies outside q0–100, report that constraint
instead of inventing negative q or changing the scale per image.

### Controlled alternative if the previous scale cannot reach a match

ImageMagick's current JPEG2000 writer interprets an interior quality value
as OpenJPEG's target PSNR (`tcp_distoratio`), not `101 − ratio`. This is a
second documented numeric convention worth testing when the first scale's
q0 remains above the reference quality. [ImageMagick's encoder](https://github.com/ImageMagick/ImageMagick/blob/main/coders/jp2.c#L988-L996).

The alternative experiment changes only the rate-control parameter, keeping
the same original pixels and lossy profile. Its q is a fixed PSNR target,
never a JPEG-derived normalization. Match it by actual SSIMULACRA2, not by
assuming equal PSNR means equal visual quality. Distinguish both scales
explicitly in every research result; a q value on one is not a q value on
the other. For testing, q0 is clamped to a 1 dB target and q100 remains lossy
profile/100 dB; do not import ImageMagick's special lossless endpoints or
silently change production recipes. This is research, not an approved
saved-filter migration or a new GUI control.

## Document guidance and user-facing quality conventions

FADGI's *JPEG 2000 Lossy Compression for Digitized Textual Materials*
describes Harvard's 46 dB PSNR approach and examples with visible local
damage despite the global target. It supports examining text, abrupt edges
and mostly uniform page regions in addition to a global numerical score.
It does not prescribe a JPEG-q75 equivalent. [FADGI report, pp. 15–16](https://www.digitizationguidelines.gov/still-image/documents/JP2LossyCompression.pdf#page=15).

Acrobat exposes named JPEG2000 quality levels and Lossless; darktable
exposes a numeric quality. Those UI conventions motivated the familiar
quality control; they do not prove cross-encoder quality equivalence.
[Adobe settings](https://developer.adobe.com/acrobat-pdfl-sdk/guides/pdfcreation/pdf-create-usingsettings#jpeg2000),
[darktable settings](https://docs.darktable.org/usermanual/development/en/special-topics/program-invocation/darktable-cli/#j2k-jpg2000).

The earlier research also linked an
[IIIF image-access recipe](https://journal.code4lib.org/articles/17596#recipes),
using Kakadu's `Qfactor=90`. That recipe is not OpenJPEG rate 90, PSNR 90
or a validated match to this project's JPEG q90/q75. Its encoder and viewing
purpose remain explicit; it cannot supply a backend-independent conversion.

## The JPEG committee quality controller: Qfactor v2

The complete previously downloaded
[JPEG committee guideline](https://ds.jpeg.org/documents/jpeg2000/wg1n101553-112-COM-Controlling_JPEG_2000_quality_using_Qfactor_v2.pdf)
was recovered and read. Its algorithm derives subband quantization steps from integer
**Q=1–100**, synthesis gains, colour-transform gains and visual weights.
Its modulation uses `50/Q` below 50 and `2 × (1 − Q/100)` at/above 50,
like familiar JPEG quantizer scaling. Q100 is still the guideline's highest
**lossy** setting, not a substitute for explicit Lossless.

This is a genuine quality-based controller, unlike a renamed compression
ratio. It is also **not** a raw PSNR target. The current Pillow/OpenJPEG
interface does not expose the required quantization controls; it cannot
implement the guideline by passing the Q number into `rates` or `dB`.
The guideline describes both classic and HT block coding, so the concept
does not itself require changing the PDF's decoder format. Any backend
adoption still needs its actual implementation, licence and reader checks.

The guideline supplies a reproducible scale, not a claim that its q56
matches libjpeg q75 on every image. The measured rate/PSNR-control studies
below test what the installed backend can do; neither is Qfactor v2.

## LOSSY-04 — execute the missing equivalence measurement

1. Freeze the exact original 300-DPI RGB canvases from the production
   composer, native and FFPR separately; retain hashes and source identity.
   Never use JPEG-decoded pixels as the JPEG2000 input.
2. Encode the actual JPEG q75/4:4:4/optimized-Huffman reference once. Keep
   the lossy OpenJPEG 9/7, RGB ICT, full component resolution and existing
   layout profile fixed. Search **actual integer q**, mapping each directly
   to its fixed ratio; there is no JPEG-reference normalization in that path.
3. Match actual decoded output using SSIMULACRA2, with PSNR as a separate
   numerical diagnostic. A practical starting tolerance is one metric
   point, not a new codec-quality scale or a human-observer equivalence
   guarantee. Search endpoints and bracket/refine actual candidates; report
   unattainable or content-dependent matches instead of hiding them.
4. Inspect representative and worst-gap crops at native pixels and ordinary
   screen viewing sizes. Preserve text, line and photographic cases. Do not
   rank a blurred result as equivalent solely because a global score passes.
5. Record actual q, decoded scores, gaps, bytes/hashes and selected-candidate
   rationale. Use these settings for measured complete-PDF comparisons,
   holding all non-quality choices fixed; keep raw image-codec and full-PDF
   accounting distinct. No compute-time ranking or CSV delivery.

[SSIMULACRA2's authors](https://github.com/cloudinary/ssimulacra2) describe
its perceptually relevant colour space, multiscale blur/ringing treatment
and tuning against subjective datasets including JPEG2000. This makes it
more relevant than PSNR alone, without replacing visual inspection. The
research-only pinned Rust implementation is built under ignored `.tmp/`;
it is not a new runtime dependency or an in-PDF codec.
Prepared RGB is treated as sRGB by the metric, explicitly recorded in the
producing identity; this experiment adds no colour-management transform.

The practical search starts at q75, measures the required scale endpoint,
then brackets/refines to adjacent integers and probes the best observed
point's neighbours. Selection minimizes the absolute perceptual-score gap;
actual bytes break ties only, never determine the intended quality. All
measured points are retained. This assumes broadly monotonic quality and
is not an exhaustive evaluation of all 101 integers; “endpoint limit” means
the measured endpoint did not bracket the reference. Non-monotonic metric
behavior remains a limitation, not a claimed global-optimum proof.

### Decoded-pixel visual review — 2026-10-19

All eleven comparison sheets were inspected at native pixels: three
distinct 256×256 crops per case, showing original RGB, JPEG q75 and both
selected JPEG2000 controls. Crop selection includes the highest JPEG
error, highest alternative-control error and a high-variance source tile.
The review tool copies pixels without resampling, sharpening or smoothing.

Artwork shows the different artifact families clearly: JPEG block/boundary
damage versus JPEG2000 ringing and colour-region texture. The ratio-scale
endpoint artwork is visibly cleaner, consistent with its higher metric
score, rather than evidence of an equal-quality comparison. Kepler's source
screenshots already contain raster noise; neither codec should get credit
for that original damage. Rasterized text and photographs remain recognizable
at the selected settings, but comparable global scores do not make their
local blur, ringing and edge detail identical.

The scan is a concrete rejected match: the alternative's q48 introduces
visible stippled noise in nearly white regions. Adjacent q49 scores
86.987 versus q48's 73.979, with the JPEG reference at 79.318. Do not hide
this integer-control jump or accept q48 as a quality-matched baseline just
because it is the closest measured integer. The fixed-ratio endpoint is
also unmatched, in the opposite direction. Finer backend rate-control or
genuine Qfactor testing is a specific follow-up, not a reason to discard
the nine practical matches on the alternative control.

This is a developer visual audit, not a new human-observer study, designer
acceptance, ordinary-screen/full-document review or all-page certification.
Sheets and crop coordinates are reproducible under
`.tmp/jpeg-jpx-research/review/` using `tools/review_quality_match.py`.

```sh
.venv/bin/python -m tools.review_quality_match --rate .tmp/jpeg-jpx-research/match-20261019/matches.json --psnr .tmp/jpeg-jpx-research/psnr-match-20261019/matches.json --output .tmp/jpeg-jpx-research/review
```

[Historical research verification](TEST_PLAN.md): the §270 research delivery
passed 43 focused checks and 1,003 full-suite tests, without changing the
runtime mapping, saved filters or GUI. §271 subsequently approves the fixed
q75/q75 baseline; LOSSY-05 implements it and refreshes all affected complete-file
tables. Current verification is recorded in `TEST_PLAN.md`, not inferred
from the earlier research-only run.

## Actual measured equivalence results

**Measured scope:** the first encoded RGB canvas in each of the eleven
image-bearing native/FFPR cases, across all six representative PDFs.
The no-image native W-9 has no bitmap-quality setting to match. All 78
prepared RGB canvases and JPEG payloads were recovered and independently
verified against LOSSY-02 hashes; these results do **not** claim that
every page of every complete PDF has been quality-calibrated.

JPEG is q75/4:4:4 in every row. Scores are measured from actual decoded
images against their original prepared RGB; each JPEG2000 candidate
receives those original pixels, never a JPEG-decoded intermediate.
Positive gap means the metric favors JPEG2000. One point is the stated
practical matching tolerance, not a human-observer equivalence claim.
PSNR and source/payload hashes remain in the regression fixture.

### Previous darktable-based scale: 5 of 11 within one point

`q = 101 − target ratio`; the scale is fixed, not JPEG-normalized.
An endpoint-limit row cannot be called a matched-quality size test.
A higher-quality result is not evidence of codec inefficiency; if it
is also smaller it is conservative quality/size dominance, not an
exactly equal-quality measurement.

For example, the artwork/native JPEG q75 reference achieves 117.19:1
against its raw RGB samples, beyond this scale's maximum 101:1 target.
Large uniform page regions make a fixed raw-byte ratio especially
unsuitable as a content-independent visual-quality control.

| Case | JPEG q75 score | JPEG2000 actual q | JPEG2000 score | Score gap | Within 1 point? |
|---|---:|---:|---:|---:|---|
| Flat-color artwork · native | 83.543 | 1 | 88.941 | +5.398 | No — endpoint limit |
| Flat-color artwork · FFPR | 82.996 | 0 | 88.217 | +5.221 | No — endpoint limit |
| Technical illustrations · native | 88.066 | 1 | 90.214 | +2.148 | No — endpoint limit |
| Technical illustrations · FFPR | 77.826 | 60 | 77.356 | -0.470 | Yes |
| Mixed text/images · native | 89.014 | 1 | 91.167 | +2.153 | No — endpoint limit |
| Mixed text/images · FFPR | 78.169 | 52 | 78.073 | -0.096 | Yes |
| Native text/vectors · FFPR | 77.528 | 66 | 78.018 | +0.491 | Yes |
| Color photos · native | 81.392 | 14 | 81.383 | -0.009 | Yes |
| Color photos · FFPR | 75.268 | 75 | 75.272 | +0.005 | Yes |
| BW scan · native | 79.318 | 0 | 88.598 | +9.280 | No — endpoint limit |
| BW scan · FFPR | 79.318 | 0 | 88.598 | +9.280 | No — endpoint limit |

### PSNR-target diagnostic: 9 of 11 within one point

Here each setting is an OpenJPEG target in dB under the documented
ImageMagick interior-value convention, with the explicit research
endpoints described above. This is **not the previous scale or the
current app quality scale**. Scores, not equality of PSNR, select the target.
No saved-filter migration or runtime dependency is implied.

| Case | JPEG q75 score | JPEG2000 target (dB) | JPEG2000 score | Score gap | Within 1 point? |
|---|---:|---:|---:|---:|---|
| Flat-color artwork · native | 83.543 | 48 | 83.816 | +0.273 | Yes |
| Flat-color artwork · FFPR | 82.996 | 47 | 82.483 | -0.514 | Yes |
| Technical illustrations · native | 88.066 | 49 | 88.476 | +0.410 | Yes |
| Technical illustrations · FFPR | 77.826 | 41 | 77.611 | -0.215 | Yes |
| Mixed text/images · native | 89.014 | 51 | 89.127 | +0.113 | Yes |
| Mixed text/images · FFPR | 78.169 | 36 | 77.749 | -0.420 | Yes |
| Native text/vectors · FFPR | 77.528 | 35 | 77.439 | -0.089 | Yes |
| Color photos · native | 81.392 | 46 | 81.889 | +0.498 | Yes |
| Color photos · FFPR | 75.268 | 39 | 75.598 | +0.330 | Yes |
| BW scan · native | 79.318 | 48 | 73.979 | -5.339 | No — integer step |
| BW scan · FFPR | 79.318 | 48 | 73.979 | -5.339 | No — integer step |

Neither study establishes one universal JPEG2000 q56 for JPEG q75.
The fixed-ratio scale has a demonstrated range problem; the second
convention is a tested alternative, not a silent redefinition.
Its measured target settings span 35–51 dB;
that is a content-dependent research diagnostic, not app q values.
Under §271 these per-image fits are NOT experimental settings.
Every current size experiment uses one fixed JPEG q75/JPX q75
pair, with JPX targeting 26:1 on every canvas (LOSSY-05).
Do not relabel the existing normalized-q75 PDF sizes as these results.

### Provenance and reproduction

Metric binary SHA-256: `bbb5bc6e9700a6c039a9daf53d88424fb5c26b05ba2cfc7b2d8195d7ad5143a0`. The research-only Rust CLI is 0.5.2, library 0.5.0, with video/AVIF
features disabled. The identity comparison returns exactly 100;
this is a sanity check, not cross-implementation reader certification.

- `.tmp/jpeg-jpx-research/match-20261019/matches.json` — SHA-256 `ab83c6f0c834c129b8cbf9bf639c416082d02c4626656e713e29f33ed4e15800`.
- `.tmp/jpeg-jpx-research/psnr-match-20261019/matches.json` — SHA-256 `ea6dfadca4a9d35fc63b1e8166f06cc436a5f7c9c740261d2ce1a126a6e381ce`.

`tests/fixtures/jpeg_jpeg2000_quality_match.json` pins the selected
actual settings, both scores/PSNRs, complete source and payload hashes,
scope and measured search points. Publication rechecks actual decoded
JPEG/JP2 samples and the candidate selection without re-encoding or
rerunning the metric. Raw transcripts and downloaded papers remain
outside Git. No complete-PDF size estimate is published here.

```sh
nice -n 10 .venv/bin/python tools/bench_quality_match.py --output .tmp/jpeg-jpx-research/<rate-label> --metric <ssimulacra2_rs> --workers 2 --first-canvas-only
nice -n 10 .venv/bin/python tools/bench_jpx_psnr_match.py --prepared .tmp/jpeg-jpx-research/<rate-label>/preparations.json --output .tmp/jpeg-jpx-research/<psnr-label> --metric <ssimulacra2_rs> --workers 2
.venv/bin/python -m tools.publish_quality_match --rate .tmp/jpeg-jpx-research/<rate-label>/matches.json --psnr .tmp/jpeg-jpx-research/<psnr-label>/matches.json
```

Use `--resume` only with an unchanged producing identity. The first
runner can extend to every prepared canvas without the first-only
flag; the second uses `--all-canvases`. An extended study needs its
actual larger scope published separately, not relabeled as this one.
