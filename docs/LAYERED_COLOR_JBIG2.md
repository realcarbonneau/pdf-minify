# Layered-color JBIG2 — design and benchmark study

Designer rulings: `DESIGNER_VERBATIM.md` §§192–194. Recorded 2026-10-14
(America/New_York). Scope: **design and benchmarks first**, not production
integration or a new GUI filter. Work: root `TODO.md` §§197/198.

Related canon: [COMPRESSION.md](COMPRESSION.md) (compose/resize/quantize),
[DESIGN.md](DESIGN.md) (native artwork and exact prepared files),
[ARCHITECTURE.md](ARCHITECTURE.md) (one real saver),
[TEST_PLAN.md](TEST_PLAN.md) (verification),
[PERSISTENCE_AND_TEMP.md](PERSISTENCE_AND_TEMP.md) (artifact ownership).
This is NOT the parked rasterized-text mixed mode in `MIXED_MODE_OPTION.md`.
Text and vector artwork remain native; only the quantized bitmap canvas is
split into colored stencils.

## 1. Proposed representation

The designer's example is four non-white colors PLUS white, meaning FIVE
total palette entries and FOUR independently JBIG2-compressed 1-bit images.
White is an opaque base; each other color paints only its own pixels. These
are ordinary PDF image stencils, not optional-content layers or four opaque
black/white rectangles (which would erase each other).

```
original image artwork + real flat page backdrop
  → compose in full RGB (native text/vector artwork excluded)
  → ONE resize to the final target DPI
  → ONE existing palette fit + exact nearest-color assignment
  → opaque white base + one disjoint binary mask per used non-white color
  → lossless JBIG2 per mask + that mask's RGB paint color
  → native original text/vector overlay
  → optimized real PDF → readback, true bytes, preview/minis/export
```

Re-use `image_layers.compose_color_page` and the existing `_quantize_palette`
helper; do not build a second source-composition or palette algorithm. The
prototype branches only AFTER final-DPI RGB preparation and shares the SAME
palette/index map between Indexed and layered encoders. Palette reduction is
lossy relative to the RGB source; mask compression/reconstruction must be
pixel-exact relative to that quantized map. No dithering or post-quantization
resizing. No re-quantization per color. Native text/vector colors are not
counted as bitmap palette colors or thresholded to fit the palette.

### PDF objects, polarity and placement

Each stencil image uses `/ImageMask true`, `/BitsPerComponent 1`,
`/Interpolate false`, `/Filter /JBIG2Decode`, and NO `/ColorSpace` or `/SMask`.
With `/Decode [0 1]`, zero bits paint and one bits leave previous content
unchanged. The existing encoder's black (0) samples therefore mean "this
palette color", and white (255) samples mean "transparent here". Set the
nonstroking palette color before invoking each image inside saved/restored
graphics state. Every mask has exactly the same pixel dimensions and page
transform; no offsets, resampling or antialiased fringes between colors.
Allocate independent image objects; never mutate a deduplicated placeholder.
Pre-encoded streams use `update_stream(..., compress=False)` before declaring
their filter (B79/B90 lessons).

Prototype finding: decimal `rg` color operators caused one-channel rounding
errors (for example, green 32 decoded as 31) despite pixel-exact binary masks.
Use an Indexed nonstroking color-space resource with the ORIGINAL palette
bytes, then select its integer entry via `cs/scn`. The image itself still has
NO ColorSpace entry. This preserves exact byte colors without numerical
fudges, a tolerance, re-quantization or a corrective display filter.

The white base must be painted explicitly across the bitmap canvas. Merely
omitting a white mask would expose an original colored backdrop below it.
Do not invent a white palette slot when the chosen palette has none: in that
case all used colors get masks and their union covers the entire base.
Skip unused colors and an actual pure-white entry; do not skip near-white.
Masks are one-hot assignments: no holes except real white pixels, and no
pixel belongs to two colors. Sparse colors may compress well, but each extra
mask has stream/object/paint overhead and a full-page binary domain.

Sources: [ISO 32000-1:2008, §8.9.6.2 (stencil masking), §7.4.7 (JBIG2)](https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf),
[PyMuPDF low-level object/stream updates](https://pymupdf.readthedocs.io/en/latest/document.html#Document.update_stream),
[jbig2enc implementation](https://github.com/agl/jbig2enc).
Use the existing `jbig2 -p` lossless generic-region path, with no lossy symbol
substitution or cross-document dictionaries. Each stream is standalone and
test-decoded. A missing/failing encoder is reported as an unavailable/failed
JBIG2 experiment, never silently measured as JBIG2 after using another codec.

The dense-noise stress fixture exposed a P4/PBM input-transport read failure
in the installed encoder/Leptonica combination. The prototype therefore
feeds the SAME lossless `jbig2 -p` operation a 1-bit PNG, not PBM; this is an
input transport change, not a PNG output fallback or production encoder edit.
The prototype also rejects MuPDF decode diagnostics: malformed streams can
otherwise paint an error rectangle matching an all-black expected mask.
Record these as production audit findings, not fixes delivered by this study.

Placement finding: a pixel-sized intermediate PDF followed by an inverse
page-scale transform caused a dense-noise mismatch at 150dpi, despite exact
source masks. Express the stencil canvas in the target PAGE'S physical units
from the start, using the same image transform as the Indexed baseline. Its
outer Form placement is then identity rather than another rounded inverse
scale. This removes the numerical cause, without pixel offsets or resampling.

## 2. Experimental boundary

Prototype code belongs under `tools/`, not in `save_with_spec`, preset lists,
recipe identity or GUI controls. Its actual PDFs/data live in a named
`.tmp/layered-color-jbig2/` benchmark folder. Production runtime temporary files
remain PID/UUID-owned under the OS temp directory; this study does not change
that policy. No dependencies are installed, defaults changed or input PDFs
overwritten. A later production integration requires a separate decision.

The prototype must preserve the existing original-page boxes/rotation,
text/vector operator overlays, links and annotations through the shared
compositor. Native-only pages acquire no bitmap. Prototype-generated stencil
and Indexed variants receive identical native layers and final lossless
container optimization. Measure WHOLE output PDFs, not sums of JBIG2 payloads.
No automatic smallest-candidate policy is introduced during this study.

## 3. Benchmark and correctness protocol

For each page, fit/assign a palette ONCE and give that same result to both
encoders. Report source, requested/actual total colors, non-white mask count,
DPI/dimensions, FULL final PDF bytes, and
wall time split into shared composition/quantization and each encoding path.
Inspect optional raw-stream diagnostics with `pdfimages -list`; payload sums
never stand in for complete file sizes.
Compare 3/4/5/8/16 total colors at 150dpi, with 300dpi sensitivity samples.
Five entries exercises the exact four-colors-plus-white example. Include
flat-color diagrams, random/dense color regions and real images.pdf artwork;
include a second real PDF, native-only pages and a multi-page regression.
Timings are local wall times, not promised performance on other platforms.

Required verification before treating a result as valid:

1. Every lossless JBIG2 stream reconstructs its input binary mask exactly.
2. Rendering each composite canvas at its stored dimensions matches the
   identical-palette Indexed RGB samples pixel-for-pixel, including white,
   near-white, edge columns and every palette entry.
3. Actual final-file full-page rendering agrees with the Indexed version;
   native words/geometry, vector artwork, rotation and links remain intact.
4. Poppler `pdfimages` independently decodes every stencil, checks its binary
   samples, disjoint coverage and reconstructed palette RGB exactly. Also
   compare Poppler FULL-PAGE renders, but record differences separately:
   different image/stencil sampling policies can create intermediate display
   colors despite exact stored data. Do not turn that finding into a false
   all-viewer pixel-exact claim, hide it with a tolerance, or confuse it with
   encoded sample corruption. Inspect mask counts/filter dictionaries.
   Poppler exports stencil coverage as white=paint, black=transparent, the
   inverse of the source grayscale mask used by the encoder. Compare that
   documented/tested coverage convention, not ordinary-image gray polarity.
5. Tests pin all-white, no-white, white-plus-four, odd widths/padding, multiple
   pages, corrupted encoder data, cancellation and unavailable encoders.

## 4. Measured results — 2026-10-14

Environment: the Debian/Python/Qt-independent PDF stack recorded in
[PLATFORMS.md](PLATFORMS.md), PyMuPDF 1.28.2, Pillow 12.3.0, NumPy 2.5.3,
`jbig2enc 0.30`, Poppler 25.03.0. No new dependency or production codec.
The palette count below applies to the BITMAP canvas, not retained native
text/vector colors. These are paired prototype baselines using production
Indexed packing, not the historical octree outputs in `COMPRESSION.md`.

Reproduce from the repository root:

```sh
./.venv/bin/python tools/layered_color_jbig2.py examples/images.pdf --colors 3 4 5 8 16 --dpi 150 --repeat 2 --fixtures --label main
./.venv/bin/python tools/layered_color_jbig2.py examples/paper-arxiv-1406.2661.pdf --colors 5 16 --dpi 150 --repeat 2 --label paper
./.venv/bin/python tools/layered_color_jbig2.py examples/images.pdf --colors 5 --dpi 300 --repeat 2 --label dpi300
./.venv/bin/python -m pytest tests/test_layered_color_jbig2.py -q
```

Actual PDFs, final-file PNGs, diagnostics and `metrics.json` files are under
`.tmp/layered-color-jbig2/{main,paper,dpi300}/`. Earlier `probe`/`dense-probe`
folders are diagnostic stages, NOT the final results below. Two repetitions
per case, alternating encoder order; every row measures the complete PDF,
including native fonts, objects and white base. Negative delta means smaller
than the SAME-palette Indexed PDF, not improvement over an unreduced source.

| Source / DPI | Requested / used colors | Masks | Indexed B | Layered JBIG2 B | Delta |
|---|---:|---:|---:|---:|---:|
| images.pdf / 150 | 3 / 3 | 2 | 15,362 | 9,978 | −35.05% |
| images.pdf / 150 | 4 / 4 | 3 | 17,386 | 11,994 | −31.01% |
| images.pdf / 150 | 5 / 5 | 4 | 19,074 | 12,765 | −33.08% |
| images.pdf / 150 | 8 / 8 | 7 | 24,362 | 17,439 | −28.42% |
| images.pdf / 150 | 16 / 16 | 15 | 28,515 | 24,233 | −15.02% |
| images.pdf / 300 | 5 / 5 | 4 | 31,768 | 17,987 | −43.38% |
| GAN paper, 9 pages / 150 | 5 / 5 on image pages | 8 total | 329,679 | 324,241 | −1.65% |
| GAN paper, 9 pages / 150 | 16 / 16 on image pages | 30 total | 364,600 | 375,219 | +2.91% |
| Synthetic flat / 150 | 3 / 3 | 2 | 2,529 | 2,622 | +3.68% |
| Synthetic flat / 150 | 4 / 4 | 3 | 2,571 | 2,964 | +15.29% |
| Synthetic flat / 150 | 5 / 5 | 4 | 3,026 | 3,307 | +9.29% |
| Synthetic flat / 150 | 8 / 5 | 4 | 3,026 | 3,307 | +9.29% |
| Synthetic flat / 150 | 16 / 5 | 4 | 3,026 | 3,307 | +9.29% |
| Synthetic noise / 150 | 3 / 3 | 2 | 71,448 | 98,821 | +38.31% |
| Synthetic noise / 150 | 4 / 4 | 3 | 88,902 | 122,371 | +37.65% |
| Synthetic noise / 150 | 5 / 5 | 4 | 115,493 | 145,870 | +26.30% |
| Synthetic noise / 150 | 8 / 5 | 4 | 115,493 | 145,870 | +26.30% |
| Synthetic noise / 150 | 16 / 5 | 4 | 115,493 | 145,870 | +26.30% |

images.pdf input: 1,494,439 B; GAN paper: 530,482 B. GAN image-bearing pages
are 6 and 7; the seven native-only pages gain NO bitmap. Real canvases are
1275×1650 at 150dpi and 2550×3300 at 300dpi. Synthetic inputs contain an actual
600×600 bitmap plus native caption/line, producing a 600×675 page canvas.
They are generated examples, not estimates or reduced-resolution stand-ins
for the real PDFs. Dense noise is seeded deterministically (192).

### Timing (median seconds, two repetitions)

Shared time includes native source preparation, full-color composition,
final-DPI resize and ONE palette fit/assignment, paid once for the comparison.
Add it to the selected variant's time for an end-to-end estimate within this
prototype. Variant time includes its encoding, native-layer assembly and
final font/container optimization; JBIG2 also includes per-mask and colored-
canvas validation. Later full-file independent checks are NOT timed here.
Runs overlapped other validation on the live desktop: these are observed wall
times, not controlled codec speed rankings or promised production latency.

| Case | Shared s | Indexed s | Layered s |
|---|---:|---:|---:|
| images, 5 colors, 150dpi | 2.2612 | 0.5823 | 0.5829 |
| images, 16 colors, 150dpi | 2.1090 | 0.4746 | 0.9641 |
| images, 5 colors, 300dpi | 3.7393 | 3.4617 | 2.1606 |
| GAN, 5 colors, 150dpi | 0.8622 | 1.9277 | 1.5577 |
| GAN, 16 colors, 150dpi | 1.0460 | 1.6774 | 2.6962 |
| Flat, 5 colors, 150dpi | 0.0226 | 0.0830 | 0.0733 |
| Noise, 5 colors, 150dpi | 0.0261 | 0.1008 | 0.1340 |

All 18 cases' timing fields are retained in the JSON, not only favorable rows.

### Correctness and compatibility results

**18 cases, 34 final-page pairs, 107 colored masks** pass exact per-stream
readback, colored canvas reconstruction and actual saved-file MuPDF rendering
at 72dpi and recipe DPI. Poppler independently decodes every saved stencil's
coverage exactly; disjoint union plus palette bytes reconstructs every pixel.
Native words/positions, vector counts (allowing the explicit white base),
rotation, crop boxes, links and annotations are checked. No per-color source
reprocessing or approximation. Final saved-file images were visually reviewed.

Full-page Poppler renders are **NOT pixel-identical** to its Indexed renders.
Diagnostics preserve mismatch counts, bounds and example colors. The Indexed
paint contains intermediate colors absent from the chosen bitmap palette,
while stencil colors remain discrete; this is consistent with different
image-versus-stencil sampling paths, not a failed JBIG2 sample decode. That
sampling explanation is an inference from the exact decoded masks and
observed render colors, not a complete Poppler-internals audit. Do not claim
all-viewer exact appearance. This is an explicit integration/release gate.

The GAN paper also produces 16 `No current point in closepath` messages on
page 3 in BOTH variants. Rendering the ORIGINAL source page with the same
Poppler options reproduces the same 16 messages (different byte offsets).
Record this pre-existing corpus diagnostic; do not attribute it to colored
stencils or hide it as a clean compatibility pass. Source and output renders
are retained as `paper/{source,indexed}-page3.png` diagnostic artifacts.

Thirteen tool-only tests cover white/no-white/near-white/arbitrary byte colors,
white-plus-four, odd widths, leading packed-newline PNG transport, missing/
failed/corrupt encoders, cancellation, multipage independence, original page
geometry/native annotations/links, one shared palette fit and unchanged
production modes. Test completion is NOT designer acceptance or integration.

### Production audit findings (not changed by this study)

- B99: current production PBM transport can fail when its first packed byte
  is whitespace (the stress fixture begins `0x0a`). Installed `jbig2` exits 3
  with a Leptonica PNM read error. The reviewed reader uses whitespace-
  consuming `fscanf` for dimensions; PNG transport removes this ambiguity.
  [Leptonica's PNM reader](https://github.com/DanBloomberg/leptonica/blob/master/src/pnmio.c).
  Production presently falls back; the prototype does not edit that path.
- B100: the production `jbig2_renders` pixel comparison can accept an invalid
  stream for an all-black expected image because MuPDF's error placeholder
  happens to be black. Decode warnings expose the failure. Prototype checks
  reject diagnostics as well as pixel mismatches; production remains unchanged.

## 5. Decisions after measurement

If useful, propose an explicitly named additional low-color codec/profile,
with color-count and final-DPI controls reusing the single edit debounce and
real-file artifact lifecycle. Retain existing Indexed behavior. First decide
whether to expose a forced layered representation or a measured exact-
palette smallest-result policy; a payload-size guess is not sufficient to
choose the smaller COMPLETE PDF. Do not assume lossless colored stencils
always beat compact 2/4-bit Indexed+Flate, especially on flat fills or high
palette counts. Do not silently rasterize text/vectors to win a benchmark.

Measured recommendation: the representation is feasible and worth an optional
low-color candidate, especially for the images.pdf-style artwork. Keep Indexed
as an alternative: flat/noisy examples and the 16-color GAN case prove that
forcing layered JBIG2 globally would be a regression. Resolve viewer sampling
policy and the two existing encoder audit findings before proposing production
integration. No GUI option/default was added in this study (§193).
