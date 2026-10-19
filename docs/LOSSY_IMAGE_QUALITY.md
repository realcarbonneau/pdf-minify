# Lossy image quality — q75 baseline and comparable settings

Designer §§262–268; implementation trackers TODO §§259–263. The current
approved starting setting is **q75 for JPEG and lossy JPEG2000**, at the
existing 300 DPI. §264 supersedes §263's initial q90 setting.
§266 explicitly adopts equal q75 values as the **working comparable-quality
baseline**; §267 now anchors JPEG2000's internal mapping to JPEG's measured
ratio using published visual-quality results. Run benchmarks now; do not block them on a proposed
perceptual calibration. This is not a claim of experimentally proven universal
equivalence, or a change to native
text/vectors, FFPR, composition/resizing, PDF-stream compression or losslessness.

## User-facing control

Expose **Quality**, 0–100, as the existing native slider plus editable spinner
pattern. Higher means higher quality, usually larger files; it is a quality
index, not a percentage of preserved information. JPEG2000 keeps a separate
Lossless checkbox. Disable Quality for other image codecs and for Lossless;
retain the inactive value. Use the shared edit timer, effective recipe key,
dirty star and Save / Save As / Discard / Cancel / Revert transaction.

The familiar convention is quality, not a requested compression ratio:
[Adobe](https://developer.adobe.com/acrobat-pdfl-sdk/guides/pdfcreation/pdf-create-usingsettings#jpeg2000)
uses named levels and Lossless;
[darktable](https://docs.darktable.org/usermanual/development/en/special-topics/program-invocation/darktable-cli/#j2k-jpg2000)
uses numeric JPEG2000 quality. Neither establishes a universally calibrated
cross-codec scale or which number users choose most often.

## Current mapping: `jpeg-reference-study-v1` (§267)

Quality still means **the selected common 0–100 value**, default 75. It
does not now mean `101 − ratio`. For every already prepared RGB canvas:

1. Encode a reference JPEG using the selected Quality and the same fixed
   4:4:4/optimized-Huffman helper as actual JPEG output. Measure
   `R = raw sample bytes / reference JPEG bytes`; use raster bytes, not the
   original PDF or final PDF size.
2. Derive JPEG2000's target from the approximate visual-quality anchors:

   | JPEG achieved ratio | JPEG2000 target ratio |
   |---:|---:|
   | 40:1 | 45:1 |
   | 60:1 | 73:1 |

   The source is [Allen, Triantaphillidou and Jacobson (2007), Figure 14,
   p. 257](https://library.imaging.org/admin/apis/public/api/ist/website/downloadArticle/jist/51/3/art00009#page=10).
   These are approximate readings from the average curve excluding
   “African tree”, not exact tabulated results or q75 settings. The study
   used 16 scenes, ten observers and actual compression ratios, not our
   libraries' quality indices. The earlier
   [2000 study](https://www.researchgate.net/publication/37435598_JPEG_2000_still_image_coding_versus_other_standards)
   used PSNR at equal bit budgets; it is not the source of a visual matching
   conversion.
3. Use `45 + (R − 40) × 28/20` within 40–60. Below 40 use
   `R × 45/40`; above 60 use `R × 73/60`; the target is at least 1.
   Outside-range relative gains are a bounded implementation heuristic,
   **not a demonstrated study result**. No arbitrary 101:1 ceiling or
   universal visual-quality guarantee is introduced.
4. Encode JPX from the original prepared pixels at that target with the
   existing 9/7/ICT/full-resolution profile. Never decode the reference JPEG
   and recompress it. No extra composition, resizing, display smoothing or
   extra filter job is involved. The reference JPEG is not exported, not
   embedded and not a silent fallback. Encoding effort is not a constraint.

Thus at selected **q75**, a canvas whose reference JPEG achieves 40:1 gets
JPX target 45:1; a different q75 canvas at 60:1 gets target 73:1. The prior
slider would label those targets q56/q28, but §267 does **not** set all
app quality values to either number. Existing saved q values, filter UUIDs,
Lossless and later deliberate edits remain intact. The effective key carries
`jpeg-reference-study-v1` and the JPEG reference profile. Explicit `rate`
recipes bypass this reference step and remain actual ratios.

The current six-file benchmark remains a **study-informed working
comparable-quality baseline**, not measured universal quality equivalence.
Record reference JPEG bytes/hash, prepared samples and the target ratio per
canvas; prove that each JPX reference matches the paired actual JPEG output.
Rank only actual final complete-PDF bytes. Do not force a JPX win or infer
final PDF sizes from the target ratio. LOSSY-02 supersedes LOSSY-01 in the
four current lossy overview rows. §268 now extends this standard to all
active binary/focused/residual comparisons; old binary files stay immutable
historical evidence, not active lossy baselines. LOSSY-03 reuses the completed
images and has measured all 60 missing general-stream controls, without image encoding.

## Previous mapping: `darktable-rate-v1` (historical §§262–266)

- JPEG: Pillow/libjpeg `quality=q`, `optimize=True`, explicit `subsampling=0`
  (4:4:4), under the fixed `jpeg444-huffman-v1` profile (§265).
- JPEG2000: Pillow/OpenJPEG `quality_mode="rates"`, with rate **101 − q**.
  Thus **q75 → 26:1**, not 75:1 and not 75 dB; explicit q90 still means
  11:1. This is the numeric mapping in
  [darktable 5.2.1's normal JPEG2000 exporter](https://github.com/darktable-org/darktable/blob/release-5.2.1/src/imageio/format/j2k.c#L324-L335),
  extended to q0 (101:1) for our 0–100 control. §265 replaces the old lossy
  reversible/RGB-independent configuration with `jpx97-ict-v1`: 9/7, RGB MCT,
  full-resolution components, one tile/layer and LRCP progression. Keep the
  transform lossy even at q100; explicit Lossless is the separate edge case.
- Explicit Lossless: reversible 5/3, no lossy rate target, unchanged behavior.

This superseded mapping was an implementation choice, **not the JPEG committee's Qfactor
quantization guideline**, and not a claim to duplicate all darktable settings.
The current Pillow adapter has no Qfactor input: passing `quality=75` would be
ignored, `rates=[75]` would mean 75:1, and `dB=[75]` would mean a PSNR target.
Do not silently make any of those substitutions. See
[Pillow's JPEG2000 options](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg-2000).

The two q75 values are the designer's working comparable-quality assumption.
This JPX mapping sets a raster compression budget; JPEG q75 sets quantization
tables. Record both mechanisms in the method, but do not use that distinction
as a reason to postpone the actual comparison. Inspect results and refine
the baseline with evidence if a meaningful discrepancy is found.

## Fixed sampling and encoder settings — research checked 2026-10-19

Local backends checked: Pillow 12.3.0, libjpeg-turbo 3.1.4.1 and OpenJPEG
2.5.4. The recommendations use options available in these installed encoders;
no encoder installation or upgrade is needed for the adopted sampling,
wavelet or colour-transform settings.

**Adopted by §§265/266; implementation and measurement tracked in TODO §261:**
use JPEG **4:4:4** and JPEG2000 **full-resolution components** for the main
comparison. Both then retain colour samples at every pixel before lossy
coding, rather than giving JPEG an additional spatial colour reduction.
This is a clean baseline for this project's mix of photos, coloured text,
logos and diagrams, not a claim that 4:4:4 always produces the smallest file.
4:2:0 remains useful for photo-focused size/quality studies, separately.

| Setting | Previous app at q75 | Adopted comparable baseline |
|---|---|---|
| Prepared raster | Shared 300 DPI pipeline | Identical dimensions, 8-bit RGB pixels, flattening/resizing and colour interpretation for both; record the prepared-pixel hash |
| JPEG sampling | Installed libjpeg default: 4:2:0 | Explicit `subsampling=0` (4:4:4); keep normal RGB-to-YCbCr conversion |
| JPEG entropy coding | `optimize=True`, sequential Huffman | Keep optimized Huffman; progression is a separate lossless packaging experiment |
| JPEG2000 sampling | Every RGB component has grid step (1, 1) | Keep full component resolution; do not manually blur/downsample chroma |
| JPEG2000 wavelet | Pillow default reversible 5/3, rate-limited | For lossy output, `irreversible=True` (9/7); keep 5/3 for Lossless; cap decomposition levels to valid image dimensions |
| JPEG2000 colour transform | Pillow default `mct=0` (independent RGB) | `mct=1` for RGB; with 9/7 this uses irreversible colour decorrelation, without spatial subsampling |
| JPEG2000 layout | One image-sized tile, one quality layer | Keep these; do not equate JPEG's 8×8 DCT blocks with JPEG2000 tiles/code blocks |
| Quality | JPEG q75; JPX q75 → ratio 26 | q75/q75 with §267's JPEG-reference mapping; actual ratios depend on the shared raster |
| PDF assembly | Existing native/FFPR saver and PDF Streams policy | Hold native/FFPR, metadata, masks and outer-stream policy fixed; measure the complete saved PDF |

### Why these adjustments

[libjpeg-turbo's encoder documentation](https://github.com/libjpeg-turbo/libjpeg-turbo/blob/main/doc/usage.txt)
identifies 4:2:0 as its default and provides full-resolution chroma sampling.
It distinguishes chroma quantization from subsampling: avoiding the latter
does not eliminate lossy quantization. Thus 4:4:4 is a sampling match, not
lossless colour or proof of equal perceived quality. The same documentation
states that progressive and sequential JPEG can reconstruct the same image;
do not add progression as another visual-quality knob.

[GIMP's JPEG export manual](https://docs.gimp.org/3.2/en/file-jpeg-export.html)
specifically identifies fine text and nearly flat colours as cases benefiting
from no chroma subsampling. That supports the full-resolution baseline for
this project's mixed documents, rather than using a photo-only assumption.

[Pillow's documented options](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg-2000)
confirm its default 5/3 and disabled MCT. Its writer does not expose subsampled
RGB components, so matching full-resolution channels is the direct supported
route. The installed 12.3.0 adapter sets component `dx=dy=1` in
[Jpeg2KEncode.c](https://github.com/python-pillow/Pillow/blob/12.3.0/src/libImaging/Jpeg2KEncode.c).

The previous rate-limited 5/3 path **could still be lossy**: reversible transform
does not mean the encoder retains every coding pass. However, lossy 9/7 plus
colour decorrelation is the adopted lossy configuration:
[OpenJPEG's own encoder](https://github.com/uclouvain/openjpeg/blob/master/src/bin/jp2/opj_compress.c)
offers 9/7 and enables RGB-to-YCC MCT by default for three-component input;
the separate [pylibjpeg-openjpeg encoder](https://github.com/pydicom/pylibjpeg-openjpeg/blob/main/openjpeg/utils.py)
uses 9/7 with irreversible colour transformation for lossy encoding and no
subsampling. This supports the configuration, **not a measured guarantee**
that changing those settings improves every project document. Do not force
JPEG to encode independent RGB just to imitate the previous JPX default.

The fixed lossy profile explicitly selects LRCP, one quality layer, no
image subdivision, 64×64 code blocks and at most six resolutions (fewer for
small images). These are documented in
[OpenJPEG's own options](https://github.com/uclouvain/openjpeg/blob/master/src/bin/jp2/opj_compress.c).
No cinema profile, HTJ2K extension, ROI weighting, extra quality layers,
chroma downsampling or display smoothing is added. Existing PDF/reader
requirements remain separate from these standard JPEG2000 settings.
`JPEG_ENCODING_PROFILE` and `JPX_ENCODING_PROFILE` are part of effective
recipe identity, so an old completed artifact cannot masquerade as the fixed
encoder's output. Headless JPEG roundtrips share the production JPEG helper.

### Immediate comparison and optional later quality calibration

**LOSSY-02 runs q75/q75 now**, on all six representative whole PDFs, native
and FFPR separately. Measure final complete files and inspect the outputs.
Keep the six-column size analysis in `INTEGRATED_COMPRESSION.md`, not a new
scattered results document. The following stronger matching experiment is
optional later work, not a prerequisite for that baseline comparison:

1. Freeze the same prepared raster for both codecs. Run native-preserving
   and FFPR cases separately; include photos, `images.pdf`, mixed text/images
   and `models-nasa-kepler.pdf`. Do not use screen captures as source pixels.
2. Use JPEG q75/4:4:4/optimized Huffman as the fixed reference. Start JPX at
   q75 with the §267 reference-derived ratio and fixed 9/7/MCT setup. Decode each actual image
   stream at full resolution and compare with the prepared original.
3. Sweep JPX's ratio around that starting point to bracket JPEG's measured
   [SSIMULACRA2](https://github.com/cloudinary/ssimulacra2) score, then narrow
   the bracket. If an endpoint does not bracket it, extend the search; do not
   invent a universal quality conversion or hide differing page results.
   Record the actual ratio, mapping, encoder versions and metric scores.
4. Check matched candidates visually at ordinary screen scale and 1:1,
   especially fine coloured text, chart edges, photo detail and ringing.
   Metrics are a matching aid, not a guarantee of legibility. Any metric
   downsampling is analysis only, never a display/preview smoothing change.
5. Save complete PDFs through the real saver, check decoder compatibility
   and rank **measured final file bytes** only after quality qualification.
   Exclude compute time. Do not put these unrun candidates into existing
   measured tables or infer their sizes from codec ratios.

The [JPEG committee's Qfactor v2 guideline](https://ds.jpeg.org/documents/jpeg2000/wg1n101553-112-COM-Controlling_JPEG_2000_quality_using_Qfactor_v2.pdf)
describes a perceptually weighted JPEG2000 quantization scale for sRGB,
including full-resolution colour. It is a more principled long-term quality
control candidate than an inverted size ratio, but it is **not** our
ratio-based mapping, not directly exposed by Pillow's adapter, and
does not certify q75 equivalence to JPEG. Adopting it needs an explicit
backend/mapping design and compatibility decision, not an undocumented
change to existing recipes. No backend or dependency change is made here.

## Saved recipes and compatibility

§267 changes the effective mapping identity, not the persisted q value or
quality-default migration revision. Keep all current q values and deliberate
edits. The new reference-derived ratio is computed internally per canvas;
do not persist it as the user's Quality, expose it as another knob or
reuse a prior mapping's completed file.

Persist `jpeg_q` for JPEG and `jpx_q` for JPEG2000. Apply q75 once to all
existing app filters using either mode, preserving every other setting and
identity, including a checked Lossless box. Remove the superseded active JPX
`rate` field during that migration. Persist a checked migration revision
before constructing saved effective specs or starting jobs. Subsequent saved
quality edits must survive fresh-process reloads. Quality migration revision
2 must run even when the previous q90 migration revision 1 is recorded.

Explicit legacy/headless `rate` recipes remain ratio-based, distinct from
`jpx_q`, so archived benchmark inputs are reproducible. Do not reinterpret an
old r192 file/recipe as q75 or silently change its bytes. Reject simultaneous
effective `rate` and `jpx_q`; Lossless ignores either lossy parameter. Include
the q-versus-r distinction in effective identity; disabled quality controls
must not create edits or processing work.
The ratio's meaning is preserved, but reproducing an old encoded bitstream
also requires its recorded producing implementation/profile. The new lossy
profile is not retroactively the producer of historical 5/3/RGB-independent
JPEG2000 files or 4:2:0 JPEG files.

## Measurement boundary and verification

[INTEGRATED_COMPRESSION.md](INTEGRATED_COMPRESSION.md) uses the current
standard for **all active lossy rows**: the overview's 24 LOSSY-02 PDFs and
60 additional LOSSY-03 fixed controls. The latter reuse the completed encoded
images and save 48 Zopfli/Brotli controls plus 12 standard-Flate FFPR
references. The same files feed binary effects, fixed sizes, focused photos,
FFPR accounting and residual effects; each pair uses its own actual measured
denominator. No image encoder or compose/resize step runs again.

Source/baseline/output hashes, profile identity, exact image/native content
and all-page 72/300-DPI readback guard reuse. Unaffected BW/indexed, PNG and
lossless measurements remain frozen. Historical q50/r192 and fixed-ratio
q75 artifacts stay immutable, never relabeled or mixed into current lossy
rows. The integrated report owns current sizes, manifest hashes and
conclusions; this document owns the settings and method. The additional
proof is pinned in `tests/fixtures/lossy_controls_sizes.json` without rewriting
the original fixed-encoder fixtures.

The previous LOSSY-01 fixed-ratio q75 manifest is immutable at
`.tmp/lossy-quality/q75-full-chroma-20261019/metrics.json` (SHA-256
`bc651088b5679afe28cc428501918a8f6df117da7d305a811b9c61e9596ee00b`).
Its tests/evidence below describe that historical stage, not the new mapping.

Verification covers endpoint/invalid-quality mapping, actual encoded JP2
roundtrips and JPEG sampling, q-versus-r keys, lossless irrelevance, saver
propagation, native/FFPR output, one-time migration and later explicit edits,
slider/spinner debounce and Save/Save As/Discard/Cancel/Revert, and viewed
offscreen GUI captures. Run the full suite after code changes. Keep the
designer's explicit leave-closed instruction; do not reopen their desktop app
merely to review an offscreen build.

Previous q90 stage verified 2026-10-18: **38 focused quality/migration/lifecycle
checks and 872 full-suite tests passed**, with no expected failures. Actual normal-scale full
window and 1×/2× panel/editor captures were viewed; both quality-only review
runs finish GREEN. These are implementation checks, not designer acceptance.
Published benchmark measurements remain unchanged.

Previous q75-only stage verified 2026-10-18: **46 focused checks and 880 full-suite
tests passed**, with no expected failures. Both isolated 1×/2× quality-only
GUI runs exit 0 / QUALITY SHOTS GREEN; actual full-window, panel and editor
captures were viewed, including Lossless/BW-disabled states. Codestream
checks pin unchanged sampling and JPEG2000 transform settings. All numeric
benchmark columns are unchanged; `git diff --check` passes. These are
implementation checks, not designer acceptance; they are not reused as proof
of the subsequent profile changes.

Fixed-profile/q75-comparison stage verified 2026-10-19: **908 full-suite
tests passed**, with no expected failures; **69 focused codec/publication
checks and 33 overview checks passed**. LOSSY-01 completed all **24 actual
whole-PDF outputs**, with identical prepared samples within each q75 pair,
exact codec payloads, retained native content and all-page 72/300-DPI decoding.
Publication also verifies source-bound native opacity-resource images and
their equality across each pair, instead of deleting them or misclassifying
them as the selected page-artwork codec. The output and proof hashes are
pinned in `tests/fixtures/lossy_quality_sizes.json`.

Both isolated 1×/2× quality-only GUI reviews finish GREEN and were viewed.
Actual artwork/photo PDFs were inspected at screen scale and in 300-DPI
edge/photo/text crops. Only the four lossy rows in the continuous integrated
overview change; fixed q50/r192 controls and all PNG/native experiment
measurements stay unchanged. No new encoder dependency, technical GUI
control, display smoothing or desktop app launch was introduced.
This is implementation verification, not designer acceptance. The desktop
app remains closed.

Study-reference stage verified 2026-10-19: **942 full-suite tests passed**;
the focused quality/benchmark/publication/overview selection passes **186**,
as does the separate overlapping quality/lifecycle selection. Both 1×/2×
quality-only UI reviews exit GREEN and were viewed. LOSSY-02 completes all
24 actual PDFs, with 78 verified prepared-canvas/reference pairs per codec.
JPEG references match the actual selected JPEG payloads byte-for-byte;
native resources/content and all-page decoding pass. Existing diagnostics
are unchanged from LOSSY-01. Reference-byte tampering, old mapping publication
and changed producer/source/output reuse are rejected. Explicit ratios and
Lossless bypass the reference; tiny inputs and q0/q100 remain valid.

Current measured results and the manifest hash are centralized in
`INTEGRATED_COMPRESSION.md`; `tests/fixtures/lossy_quality_sizes.json` pins
their provenance. Real artwork/photo screen views and 300-DPI crops were
inspected using the actual app renderer. No new dependency, technical knob,
display filtering or desktop launch. This verifies implementation, not
designer acceptance or universal perceptual equivalence.

All-section refresh verified 2026-10-19 (§268): **960 full-suite tests passed**,
with no expected failures. LOSSY-03 completes all 60 additional actual PDFs
without repeating image encoding; the main 24 and unaffected studies stay
unchanged. The binary/fixed/focused/residual tables, actual-file accounting,
labels, minima and measured denominators now share the current standard.
All controls preserve exact image/native content and all-page pixels;
36 ordinary-format controls also pass QPDF syntax checks, without claiming
unsupported-reader certification for the 24 Brotli files. The integrated
report and current-controls fixture pin their hashes/provenance. No new UI
review is required for benchmark/report-only changes; the desktop remains
closed. This is implementation verification, not designer acceptance.
