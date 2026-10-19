# Compression algorithms — rules, flows, benchmarks (designer §129)

How every pixel is resampled and encoded, and why. Ruling quotes:
`DESIGNER_VERBATIM.md` §§129/168–171. Work log: `TODO.md` §§129/174–178. Issues on this page:
B10, B16, B25, B36, B37 (superseded), B39, B40, B47, B58, B60, B62, B89, B90 (see
`issues.md` — the gated log; this page explains the substance).

Primary size comparison (§222): [INTEGRATED_COMPRESSION.md](INTEGRATED_COMPRESSION.md)
uses realistic combination rows and six representative PDFs, followed by
focused scenario tables (§223), and measures actual complete saved PDFs.
Component studies linked below explain individual stages;
they do not replace the integrated matrix or justify estimated combined sizes.

Encoder-specific reference (§234): [JBIG2.md](JBIG2.md) documents the current
`jbig2 -p` generic path, unused `-d`/symbol settings, unavailable refinement,
shared-dictionary requirements and TODO §240's detailed size-only exploration.
Current measurements are not a best-settings search. B114's same-DPI/no-growth
repair is worker-verified, awaiting designer confirmation. §233 selects a
non-JBIG2 CCITT scan for the next overview, not the already-JBIG2 regression
fixture. The published overview remains explicitly pre-B114 until TODO §239's
replacement/recomputation is verified; current regression sizes are in the guide.

Historical design/benchmark study (§§192–194): [LAYERED_COLOR_JBIG2.md](LAYERED_COLOR_JBIG2.md)
specifies one lossless colored JBIG2 stencil per non-white palette entry.
It shares the current compose-first RGB/nearest-palette path. Its original
scope was design/prototype measurements ONLY, with no production changes.
Designer §203 subsequently requested explicit selection; the studied stencil
path is now promoted into shared core as an optional production codec.
This is not a resurrection of per-original-image/mask processing or
rasterized text.

Size-only follow-up (§209): [IMAGE_STREAM_COMPRESSION.md](IMAGE_STREAM_COMPRESSION.md)
compares identical indexed/BW bitmap samples with Flate, full Zopfli, Brotli
and the corresponding JBIG2 representation. Native compression is held fixed;
no time comparisons or new production choices/defaults are part of that study.

Combination review (§§210/211): [COMPRESSION_COMBINATIONS.md](COMPRESSION_COMBINATIONS.md)
starts with the reasonable-combinations table, distinguishes implemented modes
from proposed bitmap-policy/control extensions, and compares one combined
menu with separate enabled/disabled controls. Its recommended shared general
compressor and FFPR fixed-state behavior are PROPOSALS, not changes to the
current independent selectors below or approval to migrate saved recipes.

## Latest product ruling: best encoding, reader-support alternatives (§213)

Encoder speed, compute cost or ease of installing dependencies are NOT
reasons to keep a superseded encoder/product option. Target the smallest
validated complete PDF at the chosen image representation/fidelity and reader
requirements. Zopfli's zlib output is standard FlateDecode data; the encoder
adds no reader requirement. Expose one optimized Flate format, with the best
validated implementation behind it, rather than a zlib-versus-Zopfli speed
choice. Retain other decoder formats when actual size results or reader
support justify them; newer does not guarantee smaller for every stream/file.
Keep historical controls/results for analysis, not as a menu of superseded
encoders. See [COMPRESSION_COMBINATIONS.md](COMPRESSION_COMBINATIONS.md)
for decoder tiers, exact compatibility wording and pending integration.

This supersedes the historical encoding-effort rationale, not the explicit
codec, real-file or fidelity rules. The implementation described below is
still the current six-image/three-native-policy build; TODO §217 tracks its
alignment. An automatic cross-codec selector remains an unapproved proposal,
not implied by §213. §224 separately authorizes color FFPR; see below.

## Uniform 300 DPI and whole-page color (§§224–226)

All built-in raster recipes and missing-DPI fallbacks now use the shared
`core.defaults.DEFAULT_DPI = 300`. The old lower-DPI BW seed keeps its legacy
`bw-fast` ID/UUID but is labeled **BW · Full-page**: its distinction is FFPR,
not a lower resolution or speed promise. §226 additionally authorizes a
one-time settings migration of all saved/custom raster recipes to 300 DPI,
including explicit previous values. Preserve UUIDs and non-DPI settings;
record the migration revision before constructing saved specs/artifacts.
DPI stays editable: subsequent deliberate values are not reset on later
launches. Display/minis sampling resolution is view-only and is not changed
into an additional filtering pass.

The existing Force full-page raster checkbox applies to all six image codecs.
ON flattens ALL original page painting in full color, then performs one resize
to target DPI, followed by the chosen BW/palette/JPEG/JPX transform. Render
native geometry at at least target DPI during full-page composition, not at
72 DPI followed by enlarging already-pixelated text. Source bitmap density
can require a higher composition density; only the final RGB canvas is resized.
OFF retains the established native-overlay/image-canvas policy. BW FFPR uses
this same full-color preparation sequence before conversion to gray/threshold.
There is no separate benchmark-only color FFPR implementation.

FFPR intentionally removes selectable text, native vector precision and native
font painting; JPEG FFPR also makes text lossy. Lossless JPEG2000 preserves
the prepared raster, not the original vector representation. Page-size
reshaping applies only with FFPR, for color as well as BW. The flag and its
effective page size participate in recipe/save/load/cache identity and the
existing single 300ms debounce; changing view/selection still does not process.
The native-stream selector remains explicit; the proposed automatic residual-
stream UI is not implemented by this extension.

The current integrated analysis uses 300 DPI throughout prepared raster cases,
including all focused scenarios. Original/preserve-images controls keep their
source samples and are labeled unresampled. Historical mixed-DPI artifacts
are not current equal-resolution comparisons. See `INTEGRATED_COMPRESSION.md`.

### Shared assembly repairs (B108–B112)

- B108: paint colored stencils directly in the destination page using the same
  image placement geometry as Indexed. Do not wrap a page-sized raster in
  nested clipped page Forms; their fractional boundary clipped the last column.
  Production, the integrated/bitmap study and the older prototype saver all
  use `stencils.place_stencils`; no remaining caller re-wraps it in a page Form.
- B109: removing an image can leave a whitespace ActualText tag with only
  clipping/state operators and no positioned content. Repair that disconnected
  property in the derived native layer, using MuPDF's lexer/parser. Keep real
  text-bearing replacement tags, non-whitespace ActualText, MCIDs, other tag
  metadata and drawing/clipping operators. No log suppression or invented text.
- B110: explicitly initialize all filter flags, especially `no_update = 0`.
  On the installed MuPDF 1.28.2 wrapper, reused option storage sometimes held
  a nonzero value despite the advertised default. All culling callbacks then
  ran but the source page was not updated, retaining original photos. Native
  vector-opacity soft masks remain valid native artwork; do not misidentify
  those grayscale masks as the removed ICCBased color photographs.
- B111: the sanitizer also drops text-state changes outside BT before Form
  calls. An earlier invisible text mode can then hide visible nested labels.
  Native foreground now uses `core.native_layer`: MuPDF's lexer/parser removes
  only replaced image paint and deliberate page-backdrop fills, retaining all
  other original text/state/clipping operators. Form resources remain native;
  each invocation has its own pruned resource dictionary. The real inline-
  image decoder consumes binary samples before the lexer resumes. Native
  soft masks and Type 3 programs stay untouched. Prune native destination
  resources before adding replacement layers; do not sanitize the page merely
  to remove unused original images. Backdrop-only/raster fragments still use
  the explicitly initialized native filter; they are not the retained text.
- B112: keep the destination's original native page/first Form identities as
  the actual overlay. Its structure tree, MCIDs and ParentTree must continue
  to describe painted native content, not abandoned source copies. Prune
  replaced image resources in those owners; prepend the composite/background
  as an Artifact instead of moving native content into a new page Form.
  Retain semantic containers/Alt text when bitmap paint is replaced. Read
  every canvas from an immutable original, so editing a shared native Form
  cannot remove imagery from a later page's preparation. Cache original Form
  operators/resources and reuse equal native derivatives across invocations;
  if a tagged Form requires incompatible context-specific derivatives, reject
  the operation explicitly rather than silently corrupting its parent mapping.
  BW native mode likewise keeps the original document catalog/structure tree,
  rather than building a new document with only individually inserted pages.
  Complete-file validation must inspect non-page references too, rejecting
  encoded original page images that survive replacement through stale tags.
  This preserves source semantics; it is not a new PDF/UA certification.

The ownership requirement follows the PDF Association's
[logical-structure reference](https://pdfa.org/download-area/cheat-sheets/LogicalStructureObjects.pdf):
content streams and their StructParents/ParentTree entries have paired scope.
Do not erase accessibility metadata as a compression shortcut.

Strict validation checks source-to-preparation diagnostics and native text/
font/glyph geometry, exact decoded bitmap samples, whole-page pixels between
lossless variants, and final encoded/decoded streams. Text-extraction block
IDs and word/run boundaries are bookkeeping affected by image composition,
not content identity. Check every native glyph, including actual spaces,
font, paint and origin/bounds, plus non-whitespace semantic replacement
characters and their geometry. Extraction-inferred gap spaces and the
image-only ActualText whitespace deliberately removed by B109 are not native
glyphs; they cannot exempt a missing real space from the glyph check. Font
subsetting can renumber local glyph IDs; changed numbers require identical
actual vector outlines, not an exemption from glyph checks. The existing
0.001pt serialization tolerance is unchanged;
whole-page bitmap equality is never relaxed. MuPDF's native filter
[write-back condition](https://github.com/ArtifexSoftware/mupdf/blob/1.28.2/source/pdf/pdf-clean.c)
and [marked-content/image processing](https://github.com/ArtifexSoftware/mupdf/blob/1.28.2/source/pdf/pdf-op-filter.c)
are the relevant upstream mechanisms. These are implementation repairs,
not designer-confirmed acceptance.

## Editable compression selection (§203)

Presets seed recipes; they do not restrict the recipe's compression. Offer
one **Image compression** dropdown: **JBIG2 BW**, **JBIG2 Color**, **Flate BW**,
**Flate Color (palette)**, **JPEG2000**, **JPEG**. The parenthetical qualifies
the existing Indexed 2–256-color mode; a new unquantized RGB-Flate mode was
not requested. BW and Color here describe the bitmap representation, not
different Flate codecs. JBIG2 Color means disjoint colored 1-bit stencils,
one per used non-white palette entry, not a multichannel JBIG2 bitstream.
Keep the measured study's wins AND regressions and Poppler sampling caveat
visible; availability in the app is not universal viewer certification.

Internally retain legacy recipe mode IDs for existing filters and add explicit
IDs for BW Flate and colored stencils. The effective recipe's mode is editable
and authoritative everywhere, including saved custom overrides, Save As,
readouts, control enablement and cache keys. Never read the seed preset's old
mode to decide live behavior. Algorithm changes preserve the current DPI;
irrelevant fields do not affect effective identity or start jobs. Filter UUID,
name, position and original input remain unchanged. Existing presets/defaults
are not replaced and no extra preset is inserted automatically.

Explicit codec selection is exact: JPEG means DCT, JPEG2000 means JPX,
Flate means FlateDecode, and JBIG2 means validated JBIG2Decode. No silent
Indexed substitution for JPEG/JPX or Flate fallback under a JBIG2 label.
Missing/failed encoders fail the draft clearly and retain the saved file.
Headless legacy automatic helpers may keep their documented fallback behavior;
the explicit GUI/saver selection must not use it. All paths share composition,
palette fitting, placement and the final lossless PDF optimization, not a
parallel GUI or tool-only saver. Promote stencil primitives into core and make
the study tool reuse them. Use unambiguous 1-bit PNG transport into jbig2enc;
reject native decode diagnostics as well as pixel differences (B99/B100).

Rename the unqualified Strategy label to **Threshold method**. Otsu, Adaptive
and Sauvola are automatic; Simple uses the manually chosen Threshold value.
The word "automatic" must not describe the whole dropdown. Threshold controls
apply to both BW encoders; palette count applies to both color-palette encoders.
Lossless is editable only for JPEG2000; codec losslessness describes encoding
AFTER resizing/thresholding/palette reduction, not losslessness to the original.
§224 extends FFPR/page reshaping to every selected image codec, not just BW.
All algorithm edits use the shared 300ms debounce, dirty
star and Save / Save As / Discard / Cancel transaction. Selection/zoom still
only observe completed actual PDFs; exports copy those exact files.

JPEG and JPEG2000 are different transform codecs, not historical aliases:
JPEG uses DCT and the app's encoding is lossy; JPEG2000 uses wavelets and
supports lossy rate control or lossless encoding. Keep both as explicit choices
without promising either always wins size, speed or quality. Flate is one
lossless general-purpose codec used on packed 1-bit BW samples or packed
palette indices. Both represent meaningful alternatives to the matching JBIG2
representation, not merely backward compatibility. Normative filter definitions:
[ISO 32000-1 Table 6, §§7.4.4/7.4.7–9](https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf);
encoder options: [Pillow JPEG/JPEG2000](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html).

### Current lossy quality baseline (§§262–268)

JPEG and lossy JPEG2000 now start at **q75**, with one familiar 0–100 Quality
control and JPEG2000's existing Lossless choice. §264 supersedes §263's q90
starting point and the earlier q45/q50/q60 and r192 app defaults, not explicit
historical recipes/results.
§§265/266 adopt JPEG 4:4:4 and a deliberately configured lossy JPEG2000
profile (9/7, RGB colour decorrelation, full-resolution components, one
tile/layer). These internal defaults do not add encoder controls to the GUI.
Equal q75 values are the working comparable-quality benchmark baseline;
produce real 300-DPI measurements rather than blocking on future calibration. See
[LOSSY_IMAGE_QUALITY.md](LOSSY_IMAGE_QUALITY.md) for the exact, versioned
JPEG2000 quality-to-encoder mapping, migration and verification
requirements, fixed profiles, primary sources and the actual comparison method.
§267 replaces fixed q75 → 26:1 with a measured JPEG reference at the same
Quality and the study-informed 40→45 / 60→73 ratio anchors. The same prepared
pixels feed both codecs; no JPEG-decoded intermediate or new GUI option.
§268 applies this standard to every active lossy benchmark section. The
24 image preparations and 60 fixed general-stream controls are measured
and verified; their current sizes and provenance are centralized in
[INTEGRATED_COMPRESSION.md](INTEGRATED_COMPRESSION.md). Original q50/r192
and mixed-DPI studies below are historical, not current comparison baselines.

§204 clarification: the selector governs the bitmap canvas ONLY. Every selected
image codec still uses `_save_optimized_pdf`: font subsetting, explicit native
stream compression, garbage=4, use_objstms=True, compression_effort=100.
Lossless native text/vector/font compression and object/container optimization
are independent of image encoding; they do not turn native artwork into
1-bit/color images. PDF also permits lossless LZW and RunLength stream filters.
§205 subsequently adds an independent native-stream option and benchmark:
[NATIVE_STREAM_COMPRESSION.md](NATIVE_STREAM_COMPRESSION.md). That policy now
deliberately recompresses eligible native streams, including already-compressed
ones; image payloads, metadata and embedded files are excluded. Container/xref
streams remain the shared optimizer's responsibility. Empty streams stay plain.
Existing compressed image codecs are not wrapped in accidental
extra Flate data while declaring a different Filter (the B79 regression).

## Current BW ruling (§§168–171, supersedes per-image-only implementation)

FFPR OFF retains original PDF text **and vector diagrams**. Preserve their
fonts, geometry, colors and opacity. §171 chooses a simple overlay policy,
not exact preservation of all original bitmap/native interleaving.
Combine overlapping image artwork before BW threshold/encoding, so covered
pixels and separate original image masks do not
remain as redundant encoded objects. Native text is not rasterized and no
glyph-shaped bitmap mask or duplicate text layer is invented. Ordinary text
does not require a bitmap mask; a PDF can legitimately use text clipping,
soft masks or nontrivial blend groups. Native artwork keeps those native PDF
states; interaction with the image canvas follows §171's overlay policy. A background
color is commonly a separate vector shape, not part of a text object.

Compose all image content into one BW canvas; retain native text/vector
artwork above it. Flat opaque page-background rectangles (especially the common
white page fill) remain below the canvas so they do not conceal it.
Original relative order within the native
overlay remains intact. Bitmap content is composited in its own original draw
order, including overlap, transforms and image clipping/transparency, on white.
Original native/bitmap interleaving, colored backdrops visible through image
alpha and text-as-clipping can differ under this intentionally simple policy.
Use FFPR when the flattened original appearance is required. Do not invent
more profiles/options or silently revert to a per-image mask-heavy path.
FFPR ON still rasterizes everything to one true 1-bit image per page.
The discarded color-JPEG-in-BW path and proposed rasterized-text mixed mode
remain discarded/parked, respectively. This ruling does not resurrect them.

### Lossless text/vector and PDF container compression (§170)

Text and vector graphics are drawing instructions in content streams, not
bitmaps. PDF Flate compression can losslessly compress those streams and
embedded font programs. Object-stream compression, unused-resource removal
and deduplication reduce the PDF container. Font subsetting retains the
original glyphs actually used, not a substitute font or rasterized letters.
These optimizations require no new image-mode switch. The current saver
uses native font subsetting and explicit lossless native-stream compression
(Flate by default; §205 permits Zopfli-Flate or limited-support Brotli),
followed by garbage=4, use_objstms=True and compression_effort=100. The final
writer's automatic stream replacement is disabled because the selected
native streams and image streams are already explicitly encoded. Original
fonts/glyphs are retained, not replaced with smaller substitute fonts.
Native text/fonts are not zero bytes; font and container costs can exceed
the incremental cost of a few rasterized letters in an exceptionally sparse
page. Do not promise FFPR OFF is always smaller or use that as a reason to
rasterize native text/vectors.

Sources: [PyMuPDF save options](https://pymupdf.readthedocs.io/en/latest/document.html#Document.save),
[native font subsetting](https://pymupdf.readthedocs.io/en/latest/document.html#Document.subset_fonts).
Work: B89 / TODO §§174/176/177/178. Implementation/verification evidence is
below; test completion is not designer confirmation.

### Simple image composition design (§171, current)

Use MuPDF's native PDF content filter, not rectangle-based text reconstruction
or regex edits to content streams. It understands nested Form XObjects and
retains native font/graphics/clipping operators. §§180/182 supersede the earlier
per-image DPI preparation: compose original image samples, masks, overlap and
clips in full color first, on white for BW (§171). Then ONE Lanczos resize sets
the final page-canvas DPI; only afterward convert to gray, threshold and encode
once. Do not resize unassociated RGB and its soft mask separately, or
interpolate palette indices/thresholded samples.
No extra image-coverage mask or original per-image mask is saved. Text and
vectors remain original native PDF operators above the canvas, except simple
opaque flat page-covering rectangle fills, which are retained below it. Colored
flat page backdrops are also kept underneath: they must not conceal the image
canvas. The BW image canvas itself has a white background.
This classification uses MuPDF's actual vector drawing records, not text
bounding-box rasterization or approximate glyph silhouettes. Native annotations,
links and page boxes remain on the copied page. Clean unused original image
resources before lossless saving.

§171 explicitly supersedes the unshipped ordered-run prototype and its complex
blend/text-clip fallbacks. Do not keep both architectures. Native text/vector
transparency resources legitimately needed by the original PDF remain native;
no masks are manufactured to approximate text. FFPR is the existing fidelity
choice for pages whose original native/image stacking does not suit the simple
overlay policy. Both modes still use the ONE real saver/readback architecture.

The final lossless PDF pass subsets eligible original fonts, removes unused
objects/deduplicate, compress native content/font/object streams, and use the
documented maximum compression effort. Verify unchanged native glyph rendering
and text extraction; never replace fonts just to beat an FFPR size benchmark.

## 1. The DPI rule (§129, clarified/superseded by §§180/182)

DPI applies to the complete image canvas, in both directions. Compose original
image artwork in full color, ONE Lanczos resize to the exact target DPI, then
gray/threshold, palette reduction or codec encoding. Never filter both an
original and an upscaled copy, or downscale after threshold/palette reduction.
FFPR instead renders the entire native PDF page at the target DPI before
thresholding; it intentionally includes native text/vector artwork.

- Research note: no new library needed. `Pillow-SIMD`/Pillow `LANCZOS` (a
  Lanczos-windowed sinc, 3-lobed) is already the codebase-wide resampler
  (thumbnails, frames, JPEG2000 previews) and is the highest-quality
  general resampler PIL ships — it preserves edge contrast both directions
  without ringing worse than alternatives. §129 standardizes it as the only
  allowed kernel: `pipeline.force_to_dpi` is the single resize choke point.
  Composition resolves original PDF color spaces/masks to full-color RGB,
  never gray or reduced palette before this resize.
- Source composition density uses actual displayed image-axis lengths and
  original image/mask dimensions (including rotated/nested placements), at
  least 72dpi. The target canvas uses actual page bounds × setting DPI.
  Small, transparent and 1-bit originals are not silently exempted.
- §203 selects an explicit codec for the completed canvas; do not silently
  substitute another codec or retain the old per-image source stream. Keeping
  an original would violate final DPI and composition. Native text/vector
  colors stay unchanged. The prior automatic cross-codec candidate policy
  below is superseded for the explicit saver/GUI selection.

## 2. Flows per codec

### Indexed palette assignment (§183)

The previous FASTOCTREE bucket lookup does not guarantee nearest-color mapping.
With fewer palette entries than occupied coarse color buckets, missing lookup
buckets resolve to index zero (often the white page background). On the saved
images.pdf JPX canvas, 3-color FASTOCTREE maps 111,276 pixels to white despite
a closer selected color; 112,097 total assignments are non-nearest. This is a
quantization defect, not transparency or display interpolation.

Palette selection and assignment are separate. Plain median-cut removed the
bad lookup, but viewed 3/4-color results wasted slots on nearly identical
whites. Use Pillow maximum-coverage initialization plus native k-means fitting
on a bounded ≤512×512 nearest-sampled fitting image. This sample ONLY chooses
the palette; it is never the preview, encoded image or final-DPI source. Every
full-resolution output pixel is assigned by exact nearest-RGB distance in
bounded NumPy blocks (no approximate color-bucket cache). If the original has
at most the requested colors, retain those exact colors directly. Preserve an
actual pure-white fitting background as white, not a new tinted page canvas;
do not invent white when it is absent. No dithering, no unassigned-bin white
fallback, no separate preview implementation. Both Indexed embedding and the
headless RGB helper share ONE quantization helper. "Closest" here is squared
Euclidean distance of the final 8-bit RGB values, not a new perceptual-color
option. Keep true-Indexed bit-depth compaction and actual-PDF readback.
Regression tests independently brute-force distances, including low-color
white-heavy artwork, random RGB, adjacent few colors and actual saved PDFs.

Sources: [Pillow quantize](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.quantize),
[native palette fitting](https://github.com/python-pillow/Pillow/blob/main/src/libImaging/Quant.c),
[octree lookup implementation](https://github.com/python-pillow/Pillow/blob/main/src/libImaging/QuantOctree.c).
The earlier octree compression-only benchmark is historical; smaller bytes do
not justify incorrect pixel assignment. New Indexed file sizes must be measured.
Bounded palette fitting also avoids native 32-bit color-sum overflow on very
large full-resolution pages; the exact full-resolution assignment uses signed
32-bit pair distances (maximum three-channel squared error 195,075), not
overflowing uint8 subtraction. No new package or optional algorithm UI.

- **BW forced ON** (`process_file`, force on): page rendered gray at the DPI
  → threshold (simple/otsu/adaptive/sauvola) → selected validated JBIG2 or
  packed 1-bit Flate → one image per page. Explicit JBIG2 failure is an error,
  not a mislabeled Flate result. Legacy automatic headless helpers retain
  their separate documented fallback behavior, not used by the selector.
- **BW FFPR OFF** (`image_layers.compose_page_images`): full-color original
  image composition on white → one final-DPI Lanczos resize → gray/threshold
  → selected validated lossless JBIG2 or explicit 1-bit Flate.
  Native text/vector PDF operators overlay the canvas; flat page backdrops
  stay below. Original bitmap masks/hidden overlapping pixels are not retained
  separately. Native-only pages do not acquire a needless bitmap canvas.
  The old `_rasterize_images_1bit`/individual-mask path has been removed.
- **Color/JPX/Indexed/colored JBIG2** (`image_layers.compose_color_page`): native full-color
  image composition, including real flat page backdrops → one final-DPI
  Lanczos resize → JPEG quality / JPEG2000 quality or lossless / forced palette.
  Explicit JPEG/JPX never substitute Indexed (§203). Flate Color saves the
  quantized index map; JBIG2 Color splits that SAME map into exact colored
  stencils with an opaque white base. Save ONE opaque composite canvas, not
  redundant source imagery or original bitmap soft masks. Native text/vector overlays,
  links, annotations, crop boxes and rotation remain native. Native-only pages
  do not acquire a bitmap. The old `color_stream_plan`/per-image rewrite path
  is removed, not retained as a fallback. B92 awaits designer confirmation.
- **Whole-file observation only** (§§53/55/122/149): `save_with_spec` produces
  the actual PDF; `artifacts.build_artifact` measures its entire byte size and
  prepares pages by reading that PDF. Preview/minis use those pixels; export
  copies that file. Independent preview transformations and payload estimators
  have been removed. Container overhead is included, never a permissible gap.

## 3. Initial §171 benchmarks — before §§180/182 (2026-10-14)

`tools/bench_bw_layers.py --label after --repeat 2` measures the normal
`save_with_spec` at 150/300dpi, Otsu and Simple T=210, FFPR off/on. Input
`examples/images.pdf`: 1,494,439 B. Timings below are two-run medians, not
isolated encoder timings. Before data was captured on this same current
branch before composition, after the B79 stream-wrapper repair.

| DPI / strategy | OFF before B | OFF after B | OFF median s | ON after B | ON median s |
|---|---:|---:|---:|---:|---:|
| 150 / Otsu | 38,496 | 9,258 | 0.5641 | 3,050 | 0.2640 |
| 150 / Simple T=210 | 39,026 | 9,747 | 0.5585 | 3,225 | 0.2201 |
| 300 / Otsu | 79,750 | 10,397 | 1.2141 | 4,093 | 1.3254 |
| 300 / Simple T=210 | 80,939 | 11,826 | 1.2036 | 5,488 | 0.8680 |

Every new OFF file has **one 1-bit image and zero image masks**, native text
and native vector drawings. At 300dpi Otsu, old masks alone consumed 68,969 B
(five images + five masks); the new complete file is 87% smaller than that old
OFF file. Its accounting is 3,007 B JBIG2 + 3,515 B embedded original subset
font + 3,875 B native content/maps/resources/container = **10,397 B**.
ON is 3,218 B JBIG2 + 875 B container = 4,093 B. For these 18 characters,
rasterized glyph pixels add only 211 B relative to the OFF image payload;
retaining the original font and native PDF resources costs 7,390 B. That is
the measured remaining difference, not a codec failure or duplicate bitmap text.
Keep the designer's text/vector-preserving choice; do not force OFF to rasterize
just to win this sparse-font case.

The current corpus run (`--label corpus --dpis 150 --strategies otsu`) adds:

| PDF | pages | input B | OFF B / s | ON B / s |
|---|---:|---:|---:|---:|
| NASA Kepler model | 12 | 2,262,602 | 766,567 / 2.2551 | 159,174 / 1.3541 |
| TraceMonkey research paper | 14 | 1,016,315 | 678,443 / 1.4596 | 352,350 / 1.4721 |
| JFK handwritten index scan | 30 | 1,069,151 | 417,666 / 7.1165 | 408,971 / 5.7481 |

The native/vector documents still carry fonts/vector instructions; no native
artwork was rasterized to manufacture a size win. Native-only pages remain
native (Kepler: nine image-bearing pages; TraceMonkey: three). The scanned
document is close in both modes; OFF uses original-space Lanczos before
composition, while ON uses the normal complete-page renderer at the recipe DPI.
Both follow their real, documented transformation paths, not an estimator.

Verification: all 60 FFPR benchmark page results match the correctly
thresholded source **pixel-exact** (four images.pdf recipes + 56 corpus pages).
All 106 saved image-page occurrences were independently decoded by Poppler
`pdfimages` and match MuPDF's decoded 1-bit samples exactly. Native word text
and positions are retained on every OFF page (serialization tolerance 0.001pt;
the observed Kepler float change was <0.00002pt). Actual files/metrics:
`.tmp/bw-layers/{before,after,corpus}/`, JSON and CSV. All benchmark algorithms
decoded as real `/JBIG2Decode`; injected encoder failure validates 1-bit fallback
in the test suite. Full suite **186 passed in 41.94s**; actual Qt filter-lifecycle
smoke passed and saved/draft/dialog/selection screenshots were viewed, along
with main/stacked/one/two/seven-page and 1:1 strip/pane captures.

### Historical prior-worker table — superseded measurements

Historical measurements from the prior worker, before the B79 stream-wrapper
repair. Preserved as history, not current output-size or decoder-validity proof;
current verification measures and reads the actual resulting files.

| output | bytes | wall time |
|---|---|---|
| BW forced ON @150dpi | 3,085 | 0.6 s |
| BW forced ON @300dpi | 4,127 | 1.5 s |
| BW OFF (text+1-bit imgs) @150dpi | 39,728 | 2.1 s |
| BW OFF (text+1-bit imgs) @300dpi | 72,702 | 3.1 s |
| color-max @cap150 | 120,818 | 1.7 s |
| color-max @cap300 | 162,493 | 1.9 s |

Reads: DPI is the dominant knob in every mode (150→300 roughly doubles
photo bytes). OFF costs text+fonts+masks+separate native images vs one flat
white page — see the §127 accounting the designer ruled on. Repro:
`/tmp/opencode/bench_dpi.py` (kept out of the repo).

### Initial compose-first results — before §183 (2026-10-14)

**Historical stage, not current benchmarks.** These mixed-DPI/old-quality
numbers document the compositor repair only. Current 300-DPI/q75 comparisons
are in [INTEGRATED_COMPRESSION.md](INTEGRATED_COMPRESSION.md).

`tools/bench_color_layers.py --repeat 2 --before .tmp/color-layers/before-live`
measures complete saved PDFs from the shared full-color compositor. The before
files are copies of the previous running build's saved default artifacts,
not an estimated payload or a rerun using the new code. Input images.pdf is
1,494,439 B. Medians are wall time under normal desktop/other-check load,
not isolated codec timings or a controlled before/after speed comparison.

| Default color recipe | Before B | After B | Median s |
|---|---:|---:|---:|
| JPEG2000 rate 192, 150dpi | 99,391 | 40,437 | 2.1164 |
| JPEG q45, 150dpi | 118,815 | 45,140 | 3.1981 |
| JPEG q60, 200dpi | 141,611 | 73,010 | 2.3733 |
| Poster 16, 150dpi | 99,224 | 23,143 | 2.5183 |
| Indexed 64, 150dpi | 113,261 | 39,447 | 1.7320 |

All five have ONE opaque image, zero image masks, original native words and
two original vector drawings. Image dimensions are exactly 1275×1650 at
150dpi or 1700×2200 at 200dpi. Stored-pixel readback and independently decoded
Poppler images pass (exact Indexed/JPX; JPEG decoder chroma-upsample differences
are checked separately). Saved-file screenshots were viewed at native pixels.
Synthetic hidden-black/soft-mask/overlap/blue-background regressions pin the
pre-encoding RGB result, not a false promise that lossy JPEG never rings.

The additional five-recipe corpus run (`--label corpus --repeat 1`) retains
native text/vector words and geometry on the GAN paper and processes all seven
NACA scan pages. Total: **50 independent image-page decodes** across 15 final
PDFs. Results, exact recipes, dimensions, filters and timings are in
`.tmp/color-layers/{current,corpus}/metrics.json`; PNGs observe those saved
files. Scans already encoded efficiently as 1-bit can grow in a color recipe
(e.g. NACA JPEG q45: 257,739 → 543,361 B, lossless Indexed candidate selected).
Do not silently keep the original and violate DPI/composition, or claim every
color recipe always reduces size; the actual measured amount remains visible.

BW uses the same compose-first preparation with §171's white backdrop.
`tools/bench_bw_layers.py --label canvas-first --repeat 2` gives:

| DPI / strategy | OFF B / median s | ON B / median s |
|---|---:|---:|
| 150 / Otsu | 8,746 / 2.3746 | 3,050 / 0.4722 |
| 150 / Simple T=210 | 9,158 / 2.4688 | 3,225 / 0.4483 |
| 300 / Otsu | 9,643 / 2.4144 | 4,093 / 0.7215 |
| 300 / Simple T=210 | 10,754 / 1.8595 | 5,488 / 0.4992 |

All eight saved image pages independently decode exactly as 1-bit JBIG2;
FFPR matches its complete-page threshold reference pixel-exact. OFF retains
native text/vectors and zero image masks. Earlier tables are dated stage
history, not the current BW composition order or byte counts. The native
font/container overhead explanation still applies.

### Historical palette repair (§§183/184, 2026-10-14; before uniform 300 DPI)

The §183 fitter/nearest mapper supersedes the Indexed byte counts above;
those are preserved stage history. `tools/bench_color_layers.py --repeat 1
--label nearest-fit --before .tmp/color-layers/before-live` saves and independently
decodes every default color output again. JPEG/JPX remain 40,437 / 45,140 /
73,010 B at their respective then-default settings. Then-current **Poster 16: 28,516 B
(2.4350s); Indexed 64: 34,026 B (2.3971s)**, versus the earlier live per-image
99,224 / 113,261 B. These are one-run wall times, not medians over repetitions.
Exact artifacts/recipes/dimensions/decoder evidence and final-file PNGs live
under `.tmp/color-layers/nearest-fit/`.

Eleven independent palette regressions check every pixel against all actual
palette entries at 2/3/4/8/16/64/256 colors, exact nearby few-color samples,
the old white-bucket reproducer and an actual images.pdf save. Whole/1:1 GUI
captures at 3/4/8/16 colors were viewed: the palette preserves distinct artwork
colors instead of using several nearly-white slots. The palette-fitting
sample does not lower output DPI: all full-resolution pixels are assigned.
The designer explicitly confirms the improved palette output in §184;
issue B93 records the date/scope. Other issues retain their own acceptance gates.

## 4. Failures, known gaps, TODOs

- **Multi-page FFPR image aliasing (B90, implemented/verified, unconfirmed)**: inserting the same tiny placeholder
  deduplicates its image xref. Replacing that stream per page overwrites every
  previous page. Per-payload validation alone misses this. Embed independently
  owned real encoded image objects (including fallback) before placing them.
  This is implemented; final-page pixel regressions and all 56 corpus FFPR
  pages pass. Designer confirmation is still required to close the issue.

- **Double-compressed encoded streams (B79, §150 audit)**: PyMuPDF
  `update_stream` defaults to automatic compression. Pre-encoded JPEG/JPX/
  JBIG2/Flate payloads must use `compress=False` before assigning the matching
  Filter dictionary; otherwise an unadvertised wrapper corrupts readback.
  Real saved-PDF decode tests, not synthetic filter images, verify this
  ([PyMuPDF update_stream](https://pymupdf.readthedocs.io/en/latest/document.html#Document.update_stream)).
- **Wrong Deflate container (B79)**: Zopfli defaults to gzip; `/FlateDecode`
  requires zlib-wrapped Deflate. Request `--zlib` explicitly and validate each
  returned stream against its original bytes, falling back to zlib-9 on failure.
  The previously unvalidated gzip output explains the remaining Indexed decode
  errors after automatic compression was removed.
- **Previously blamed small/sparse JBIG2 streams**: the old fallback test
  expected PNG for a valid sparse stream because double compression broke
  the test PDF itself. B79 fixes the wrapper and that stream now decodes as
  JBIG2. Do not infer an encoder defect or require another encoder from the
  old diagnostic. The real pixel-exact decode gate remains; an explicitly
  invalid JBIG2 fixture verifies genuine 1-bit fallback.
- **Old 1-bit Flate row-stride bug** (found §127): the old individual-image
  path silently kept some originals. That path is now removed; fallback
  places correctly sized 1-bit packed rows and real-file tests decode them.
- **OFF wall time** now uses one JBIG2 encode per image-bearing page, not
  one per original image. The external timeout remains up to 120s for hostile
  pages; process-once background ownership/cancellation rules remain unchanged.
- **Old mask-count/overhead gap**: retired with the estimator path (§149).
  Whole-PDF file measurement includes masks, fonts and every PDF object.
- **Old <200px/alpha skips and smaller-wins DPI exception (B60)**: the new
  canvas paths remove these per-image exemptions in color and BW. Actual
  source masks/stencils/inline imagery participate in native full-color
  composition before the exact-DPI resize. Verification is not designer
  confirmation of the older issue's remaining scope.
- **Exact display (§§172–175), not a second transformation**: all filter
  transformations run at recipe DPI in the real saver first. Prepared 150dpi
  pages and small nearest-neighbor derivatives support minis and geometry.
  Main panes observe their actual PDFs at current zoom/device resolution,
  clipped to exposed regions, with bounded display caches. This supersedes
  the previous prepared-raster-only zoom policy. Native text/vectors gain
  geometric precision; PDF-content AA, image interpolation and decoder
  subsampling are disabled. Genuine encoded color/alpha remains visible.
  Display never re-thresholds, mutates a saved PDF, or calls the saver.

## 5. Cross-references

### Color flow clarification (§§179/180)

The designer explicitly requires full-color composition BEFORE DPI resize and
transformations, with native text overlaid afterward. This supersedes §129's
older per-image resize ordering, not its exact-DPI-before-filter requirement.
Keep §170's explicit native-vector retention: no later ruling revokes it.
The shared canvas preparation serves BW and color; no per-image alpha patch
or legacy alternative loop. Processing produces the one actual saved PDF;
no display smoothing, alternate preview transform or estimated sizes.

§§181/182 clarification: the first Firefox image in images.pdf is a 1600×1608
bitmap with a separate soft mask; the PDF also contains native text and two
native drawings. Keep the established native-text/vector overlay policy; the
bitmap layer is flattened. Recommended/implementing order: full-color RGB
composition, ONE resize to final target DPI, then palette/gray/threshold or
codec transform and encoding. Do not process original and enlarged copies or
resize already thresholded/palette-reduced results afterward. This would
reintroduce grays or colors outside the chosen palette.

For color source composition, sample the native PDF image layer at its source
image/mask density (at least 72dpi), then resize full-color pixels to the
target. Bounded native-render tiles fill one anonymous disk-backed opaque RGBX
source buffer; Pillow maps it without a whole-source copy and performs ONE
global resize. Do not resize tiles independently: coefficient rounding can
create seams. The scratch lives in the owning artifact work directory and
is closed/unlinked on completion or cancellation. The final canvas/resize
working buffers still require RAM; this is not an unlimited-memory claim.
Opaque page backdrops participate in color composition so transparency is
resolved against the actual page color, not an invented white matte. Text
and other vector artwork remain native overlays. No per-image alpha rewrite.

- `ARCHITECTURE.md` (single-path flow, background jobs), `DESIGN.md`
  (behavior), `UI_LAYOUT.md` (amounts display), `PERSISTENCE_AND_TEMP.md`
  (saver temp location), `MIXED_MODE_ANALYSIS.md` (measured tables),
  `MIXED_MODE_OPTION.md` (parked JBIG2-layer variant), `PDF_OPTIMIZATION_NOTES.md`.
- Code: `core/image_layers.py` (native filtering/shared BW and color assembly),
  `core/canvas.py` (exact full-color composition/one disk-backed resize),
  `core/pipeline.py` (`force_to_dpi`, `_place_bw`, `_place_color`,
  `_save_optimized_pdf`, `color_canvas_payload`, `jpx_encode`, `process_file`),
  `ui_qt/artifacts.py` (real output and prepared page buffers), `ui_qt/jobs.py`
  (spawn pool and pure view framing), `core/recipes.py` (effective identity).
