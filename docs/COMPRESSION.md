# Compression — how a page is prepared and encoded

This page is the hub for image preparation, codec choice and the final
lossless PDF pass. Measured sizes live in
[COMPRESSION_BENCHMARKS.md](COMPRESSION_BENCHMARKS.md); specialist pages are
listed under [Related pages](#related-pages).

## Rulings (verbatim)

Exact designer text from `DESIGNER_VERBATIM.md`. Text outside the fenced
quotes is not the designer's.

### Policy: maximum compression, best encoders, standard packages

**§81** (2026-10-10)

```text
Everything in this project must be maximum compression, BW lossles, reduced palette, probably lossless, jpeg full color usually lossy
```

**§213** (2026-10-15)

```text
so all pdf readers can decode flate encoded with zopfli?  Encoding is not a constrain, the objective of this project is to be an opinionated pdf compression suite with the best available algorithms for encoding, we drop superceded algorithms, the only concern that affects decisions would be pdf reader support, where for some usage, a more generally supported decoder would be proferred, in others, the user may expect readers to have the most modern and best pdf reader.
```

**§214** (2026-10-15)

```text
Compression time is not a concern, so we drop classic Flate from the options?  Keep in the comparison table for reference.
```

**§278** (2026-10-20)

```text
Don't change standard packages, if you can't change JPEG2000, adjust the JPG settings to match.
```

### Page model: optimize the images or flatten the page

**§127** (2026-10-13)

```text
No, FFPR is not a mixed path. The basic decision is to optimize existing images, or the full page into a single image. This is the basic functionality. I don't know what your mixed path was, but you were saying something about colors in a BW and I could see the letters being rasterized even when the FFPR was OFF, this was your fail.
```

**§170** (2026-10-14)

```text
Vector diagrams remain, these are rarely taking alot of space.  Most waste is images.  Also, is the test and vector graphics compressed within a pdf?  Are there compression options?
```

**§171** (2026-10-14)

```text
Why is this complicated?  The PDF always must have a clear and explicit flattening sequence to display the document.   Why can't we just keep everything bitmaps as a big image and overlay the text.  If this doesn't look nice, then the user can choose FFPR options, or we can add further filter profile options.  Choose a simple strategy that will help reduce the size of the file.  Ideally keeping text and images clearly separate.
```

### Resolution and order of operations

**§129** (2026-10-13)

```text
OMG, why are you not respecting the DPI? How is that not clear??? DPI apply to ALL image transformations on the page, even if smaller res, they get upsized DPI on their original color pallette, I think Laconz something like that is considered the best, please review notes, if we don't have notes on this, we need to do some research. The design flow is all images are forced to the setting DPI in their original image space, then the transformations are applied (eg BW, algo, jpg compression, etc). Same recipe for FFPR. Do you follow? Please document that and create an compression algorithm page for these rules, flows and benchmarks, also note failures, issues and TODOs on this document and cross reference
```

**§180** (2026-10-14)

```text
It should always render flattened first, why is it not doing this?  this should be simple.  Can your render everything without the text, full color, then upscale, then apply the transforms.  I already ruled that this was the flow, but the prior weak worker probably messed this up.
```

**§225** (2026-10-15)

```text
I think we should also convert all the filters to 300dpi default for now.  We know that lower dpi will be smaller in general, it's not useful to have variations of this, it doesn't provide information and causes comparison problems.
```

### Explicit codec choice and colour reduction

**§203** (2026-10-15)

```text
I think we need to add an option that is the algorithm, JBIG2 BW, JBIG2 Color, Flate BW, Flate Color JPEG2000, JPEG.  Because we have no way of choosing between the options at the moment, filters seem to be locked into their algo.  Also, why do we have both JPEG and JPEG2000, and Flate BW and Flate Color?  For backward compatibility?  Aso, the terms strategy should be qualified, is that Threshold automatic strategy?
```

**§183** (2026-10-14)

```text
In the low color versions, colors are getting incorrectly converted to white instead of their closest colors. Also, when using the spinner, after a debounce, a rerender should be triggered, same for the sliders or any other change.  We should have one global debouce for this.  What do you suggest as a debounce time?
```

**§287** (2026-10-20)

```text
Sounds like we cannot be opinionated on the JPG/J2K for now, so let's just keep them as comparable as possible in the benchmarks and we will not have an automatic Best option for these.
```

### Lossless streams: Best for every filter, excluding J* payloads

**§205** (2026-10-15)

```text
what are the top text compression algorithms, and we should add an option for this also.  And make a benchmark document for that scope of compression also.  Are there support limitations on some of these algorithms?  Any reason to keep lesser compression algorithms?
```

**§256** (2026-10-17)

```text
Why limite to non-image streams?  Don't they also compress PNGs?  Please explain.
```

```text
I don't think we will be supporting anything other than the three J*.  Why are you mentionning "CCITT fax images", did we not rule that all images get converted?
```

```text
yes, but those would be compressed with Best, but J* are excluded.
```

**§257** (2026-10-17)

```text
Change all the app filters to "Best" please
```

## The preparation path

Every filter produces one real saved PDF through `pipeline.save_with_spec`.
Its byte size is the filter's size; the preview, the minis and Export all read
that same file (see `ARCHITECTURE.md`). There is no estimator and no second
preview transformation.

Two page models exist, selected by **Force full-page raster** (FFPR):

- **FFPR off (default).** All image artwork on a page is composed into one
  canvas. Native text and vector drawings stay native PDF operators painted
  above it, with their fonts, geometry, colours and opacity. Flat opaque page
  backgrounds, and local flat panels that enclose an image painted later in
  the source (B116), stay below the canvas so they never hide it. Pages
  without images get no canvas. The original interleaving of native and
  bitmap paint can differ; FFPR is the choice when the exact flattened
  appearance matters.
- **FFPR on.** The whole page, including text and vectors, is rendered into
  one image. Text stops being selectable; with JPEG it becomes lossy. Page
  size reshaping (Letter/A4) applies only in this mode.

Both models, and every codec, follow the same order:

1. Compose in full colour. Source images, masks, overlaps, clips and
   transforms are resolved at the source density (at least 72 DPI, from the
   actual image and mask dimensions). Bounded native-render tiles fill one
   disk-backed RGBX buffer in the artifact's work directory. BW canvases are
   composed on white; colour canvases include the page's real backgrounds.
   FFPR renders native geometry at the target DPI or above.
2. Resize once to the target DPI with Lanczos (`pipeline.force_to_dpi`, the
   only resize point). The default is 300 DPI (`core.defaults.DEFAULT_DPI`);
   DPI is one editable value per filter and also upsizes smaller images.
3. Transform: grey plus threshold for BW, palette reduction for indexed and
   coloured JBIG2, nothing for JPEG and JPEG2000.
4. Encode once with the selected codec.
5. Run the final lossless pass (below) and save.

## Encoder policy (§213)

Each representation uses the strongest validated encoder. Encoding time and
extra encoder dependencies are not reasons to keep a weaker one; reader
support is the only trade-off. Zopfli and zlib write the same Flate format, so
they are not different choices for the reader, while Brotli needs a reader
that supports it. Reader support is tested on actual readers, never inferred
from a PDF version label. Superseded encoders such as Classic Flate remain
only as labelled benchmark references. The explicit Flate stream policy is
still offered; aligning the fixed policies with this rule is TODO §217.

## Editable compression selection (§203)

The **Image compression** choice is part of every recipe and is exact:

| Choice | PDF filter | Representation |
|---|---|---|
| JBIG2 BW | `/JBIG2Decode` | 1-bit, lossless generic region |
| JBIG2 Color | `/JBIG2Decode` | one coloured 1-bit stencil per non-white palette entry over an opaque white base ([JBIG2.md](JBIG2.md#jbig2-color-one-stencil-per-palette-colour)) |
| Flate BW | `/FlateDecode` | packed 1-bit samples |
| Flate Color (palette) | `/FlateDecode` | true Indexed, 2–256 colours |
| JPEG2000 | `/JPXDecode` | lossy at the Quality setting, or Lossless |
| JPEG | `/DCTDecode` | lossy at the Quality setting |

- A selected codec is never replaced by another one. A missing or failing
  encoder fails the draft with a clear error and leaves the saved file
  untouched. Each JBIG2 stream is decoded by MuPDF and must match the
  thresholded bitmap pixel for pixel before it is embedded.
- **Threshold method**: Otsu, Adaptive and Sauvola choose automatically;
  Simple uses the Threshold value. Both BW encoders use it. The palette count
  applies to both palette encoders.
- **Quality** (0–100, default 75) applies to JPEG and lossy JPEG2000. The
  encoder profiles and the quality mapping are in
  [LOSSY_IMAGE_QUALITY.md](LOSSY_IMAGE_QUALITY.md).
- **Lossless** is editable only for JPEG2000. It describes the encoding after
  resizing, thresholding or palette reduction, not fidelity to the source.
- The effective recipe's mode is authoritative everywhere (controls, cache
  keys, Save As). Legacy mode IDs stay readable for saved filters. Changing
  the algorithm keeps the DPI; fields that do not apply to the chosen codec
  never change the recipe identity or start processing. Edits follow the
  shared debounce and save lifecycle in `FILTER_LIFECYCLE.md`.
- JPEG and JPEG2000 are different transform codecs (DCT and wavelet), and
  Flate is a general lossless coder for packed samples. Each is a real
  alternative to the matching JBIG2 representation; none is promised to win.
  No Best option chooses between JPEG and JPEG2000 (§287); Best covers only
  the lossless streams.

## Palette assignment (§183)

Choosing the palette and assigning pixels are separate steps.

- The palette is fitted on a bounded sample (at most 512×512, nearest
  sampled) with Pillow's maximum-coverage initialization and k-means. The
  sample only chooses colours; it never becomes an output or preview.
- Every full-resolution pixel is assigned to the nearest palette entry by
  squared RGB distance, computed in bounded NumPy blocks with 32-bit signed
  arithmetic. There is no colour-bucket cache, no dithering and no fallback to
  white.
- An image with no more colours than requested keeps its exact colours.
  White stays in the palette only if the source has pure white.
- Indexed embedding and the headless RGB helper share one quantization
  helper; true Indexed images use the smallest valid bit depth.

## Final lossless pass

`pipeline._save_optimized_pdf` runs for every codec:

- subset the original fonts (`Document.subset_fonts`); glyphs stay original;
- compress native content, font and residual streams with the filter's PDF
  Streams policy. **Best** (all app filters) encodes each eligible stream
  with both Zopfli-Flate and Brotli, including packed BW and indexed image
  streams with PNG prediction off and on. It saves its per-stream choice
  beside the all-Zopfli and all-Brotli versions and keeps the smallest
  complete file. JPEG, JPEG2000 and JBIG2 payloads are never recompressed.
  Details, reader limits and measurements:
  [NATIVE_STREAM_COMPRESSION.md](NATIVE_STREAM_COMPRESSION.md);
- save with `garbage=4`, `use_objstms=True`, `compression_effort=100` and the
  writer's own stream compression disabled.

Pre-encoded image payloads are written with `update_stream(..., compress=False)`
under the matching `/Filter`. Zopfli runs with `--zlib`; each result must
inflate back to its input, or saving fails.

## Composition rules

The native layer is derived with MuPDF's content filter and lexer
(`core.native_layer`), never by regex edits or text reconstruction.

- It removes only replaced image paint and the backdrop fills moved below the
  canvas. All other text, graphics-state and clipping operators remain.
  Inline image data is consumed by the real decoder before lexing resumes.
  Native soft masks and Type 3 programs are untouched.
- Every MuPDF filter option is set explicitly, including `no_update = 0`.
- Each Form invocation gets its own pruned resource dictionary. Destination
  resources are pruned before replacement layers are added.
- The page and first Form keep their original identities, so the structure
  tree, MCIDs and ParentTree still describe the painted content. The
  composite is prepended as an Artifact. Alt text and semantic containers
  remain when bitmap paint is replaced. A whitespace-only ActualText tag left
  around a removed image is repaired. A tagged Form that would need
  incompatible derivatives in different contexts is rejected explicitly.
- Every canvas is read from the immutable original document, never from a
  page already edited for another canvas.
- Coloured stencils are painted directly in the page with the same placement
  geometry as Indexed images.

### Shared assembly repairs (B108–B112)

These issues fixed the rules above; their traps are listed under
[Design traps](#design-traps-and-failed-attempts).

## Validation

Benchmarks and regression tests accept a saved output only if:

- every native glyph survives with its font, paint, origin and bounds
  (0.001 pt tolerance). Subset fonts may renumber glyph IDs only if the
  outlines are identical. Extraction-inferred gap spaces and the removed
  whitespace ActualText are not glyphs;
- decoded bitmap samples equal the prepared samples exactly, and lossless
  variants of the same preparation render identical page pixels;
- every encoded stream decodes under its declared filter, and non-page
  references (for example stale tags) hold no original image that should
  have been replaced.

Validation follows the PDF Association's
[logical-structure reference](https://pdfa.org/download-area/cheat-sheets/LogicalStructureObjects.pdf)
and MuPDF's [filter write-back](https://github.com/ArtifexSoftware/mupdf/blob/1.28.2/source/pdf/pdf-clean.c)
and [marked-content handling](https://github.com/ArtifexSoftware/mupdf/blob/1.28.2/source/pdf/pdf-op-filter.c).

## Related pages

- [COMPRESSION_BENCHMARKS.md](COMPRESSION_BENCHMARKS.md): measured complete-PDF sizes for every combination.
- [LOSSY_IMAGE_QUALITY.md](LOSSY_IMAGE_QUALITY.md): JPEG/JPEG2000 settings, the quality mapping and its measured evidence.
- [NATIVE_STREAM_COMPRESSION.md](NATIVE_STREAM_COMPRESSION.md): Best, Zopfli and Brotli for native and packed streams.
- [JBIG2.md](JBIG2.md): JBIG2 BW and coloured stencils (JBIG2 Color).
- Code: `core/image_layers.py` (native filtering, BW and colour assembly),
  `core/canvas.py` (composition and the single resize), `core/pipeline.py`
  (`force_to_dpi`, `color_canvas_payload`, `jpx_encode`, `_save_optimized_pdf`),
  `core/native_layer.py`, `core/backdrops.py`, `core/stencils.py`,
  `core/recipes.py` (effective identity), `ui_qt/artifacts.py` (real output).

## Design traps and failed attempts

Only traps with a real chance of recurring are kept here; git holds the rest.

- **Encoding each original image separately.** The first BW path kept
  every source image with its own mask: on `images.pdf` at 300 DPI the masks
  alone took 68,969 bytes, and small or transparent images escaped the DPI
  rule. One composed canvas per page replaced it (the complete file became
  87% smaller). Do not reintroduce per-image paths "to save work".
- **Resizing in the wrong place.** Resizing after threshold or palette
  reduction creates greys and colours outside the palette; resizing RGB and
  its soft mask separately misaligns them; resizing render tiles one by one
  leaves seams; rendering native geometry at 72 DPI and enlarging it
  pixelates text. Resize once, in full colour, before any transform.
- **Double-compressed payloads (B79).** PyMuPDF's `update_stream` compresses
  by default, so an already-encoded JPEG, JPEG2000, JBIG2 or Flate payload got
  an undeclared extra Flate layer and failed to decode. Small JBIG2 streams
  were wrongly blamed on the encoder because of it.
- **Zopfli writes gzip by default (B79).** `/FlateDecode` needs zlib framing;
  without `--zlib` readers fail. Validate every encoded stream.
- **Shared placeholder images (B90).** Inserting the same placeholder image on
  several FFPR pages deduplicates it into one object; replacing its stream
  per page overwrote every earlier page. Each page needs its own image object,
  and per-payload checks do not catch this; check rendered pages.
- **Palette lookup by colour bucket (§183).** Pillow's FASTOCTREE lookup sent
  colours with no occupied bucket to index 0, often white: on `images.pdf`
  111,276 pixels turned white. Smaller files never justify wrong pixels.
- **MuPDF filter defaults (B110).** An option left at its advertised default
  (`no_update`) sometimes held a stale non-zero value, so the page was never
  updated and the original photos stayed. Set every option explicitly.
- **Sanitizing instead of filtering (B111).** The generic sanitizer also drops
  text-state changes outside `BT`; an earlier invisible text mode then hid
  visible labels inside Forms.
- **Rebuilding pages or wrapping them in Forms (B108, B112).** A page-sized
  raster wrapped in nested clipped Forms lost its last column to a fractional
  clip. Moving native content into a new Form or document detached the
  structure tree and left original images reachable through stale tags.
- **"FFPR is smaller than native" is not a defect.** On sparse pages the
  original subset fonts and native resources can outweigh a few rasterized
  letters. On `images.pdf` at 300 DPI, Otsu: native mode is 10,397 bytes
  (3,007 JBIG2 + 3,515 font + 3,875 content and container), FFPR is 4,093
  bytes. Native text is kept by design (§§168–171); never rasterize it to win
  a size comparison.
