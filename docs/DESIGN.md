# DESIGN — preset filter-strip + comparison views

Documentation scope (§218): keep substantive design, defect reports and dated
acceptance. One-off execution, status and publication commands are not design
requirements. Lasting development/test rules belong in `DEVELOPER_GUIDELINES.md`.

## Project identity (§230)

The product name is **PDF Minify**. The importable Python package is
`pdf_minify`; the machine/settings/temp identifier is `pdf-minify`. The
application title uses the product name, including Qt's unsaved `[*]` marker.
Rename launchers, imports, diagnostics, runtime paths and active documentation
together. The designer will rename the GitHub repository separately; do not
change its remote or pretend that a new repository URL already exists.

Retain the existing flat Python layout: `pdf_minify/` is the import package,
not another repository. A `src/` layout would contain `src/pdf_minify/` and
require installation changes; generic `app`/`source` directories are not a
replacement needed for this naming change. See `ARCHITECTURE.md`.

Preserve all saved filters, UUIDs, order, names, parameters and the remembered
input. One shared settings factory copies legacy user-scope settings once,
without overwriting values already in the new store or modifying the old
store. Persist a migration marker so deleted new settings never reappear
from the legacy copy. This identity migration is not a filter edit or a
reason to reprocess during selection. Tests/review tools must never migrate
or write the designer's real settings. Details: `PERSISTENCE_AND_TEMP.md`.

Original designer quotations, license/provenance notices, historical artifact
paths and benchmark source hashes remain exact. Historical names in these
records and the explicit legacy-settings identifier are not active branding.

## Designer rulings (verbatim)
Quoted exactly from `DESIGNER_VERBATIM.md`. Do not edit the quotes.

Ruling §3 — original brief:
> I want to make a simple app that works on multiple platforms, but first targetting lxde debian linux.  I want to dnd or open a pdf docs and be able to visualize various optimizations to it.  Highly opinionated, eg conversion to BW with a few strategies and a global or per page threshold, like GIMP threshold option.  Also, another option that compresses images within the pdf to jpg XL or whatever highest compression algorithms exist.  Same for BW, JDIC2 (I think if I remeber correctly.  Always max compression for all by default, but tunable if too slow.  Always fast cancel with esc by user as required.  Start by making some md docs directly in this dir with your notes, ideas and tests.

Ruling §6 — picky UI:
> what if I am really picky about smooth clean custom UI highly tailored for a specific job, like pan, zoom in/out mouse scroll, next page, prev page, DnD, etc.

Ruling §9 — preset filter-strip + view options:
> I want to see a list of preset optimization options, like photo filters on a camera with a smaller version of previews, and when I click on one, the main doc has original and preview (optmized side by side, vertically or horizontally, same for the filter thumbnails, all would be choosable as menu view options.

Ruling §10 — raster defaults on main screen:
> Generally forcing alll images on the page and page rasterizing to 300dpi, and 8.5x11, but that also would be options on the main screen.

Refined by §74: page size defaults to Original (saving never reshapes pages
unless asked — forcing Letter would break normal pages). Letter/A4 stay as
advanced Save options for absurd scan sizes, which the File box flags with a
warning line (never auto-applied).

## Concept (camera-filter UX for PDFs)
- Left/bottom **filter strip**: every preset renders a small live thumbnail of the
  CURRENT page through its pipeline. Click a thumbnail = select preset → main panes update.
- **Main panes**: original (left/top) + optimized preview (right/bottom) of the same page.
- **View menu** controls orientation of main panes AND of filter thumbnails:
  - `View → Main: Side by side (H) | Stacked (V) | Single (toggle Orig/Preview)`
  - `View → Filters: Filmstrip (H) | Rail (V) | Grid`
  - Shortcuts: `Ctrl+1/2/3` main modes, `Ctrl+Shift+H/V/G` filter layout.
  - Zoom keys (designer ruling §52, modern standard): `Ctrl+Plus` in,
    `Ctrl+Minus` out, `Ctrl+0` fit-width. Panes stay synced either way.
  - Choice persists in QSettings.

```
View=Main:H + Filters:H (default, wide screen)
+---------------------------------------------------------+
| Pages | Original   | Preview (preset: BW Otsu) | Preset |
|  1    |            |                           | [oto]  |
|  2    |  before    |  after                    | [T180] |
+---------------------------------------------------------+
| Filters (filmstrip H): [orig][otsu][T180][T210][sauv][Cmax][Cbal] |
+---------------------------------------------------------+
View=Main:V + Filters:V (square / portrait screens) → panes stacked, rail on right.
```

## Preset list (v0.1 — opinionated, max-compression default)
| # | Preset (label) | Mode | Params | Use when |
|---|---|---|---|---|
| 0 | Original (no-op) | — | gc+deflate only | baseline / born-digital keep |
| 1 | BW · Otsu Auto ★ default | BW | 300dpi, otsu, JBIG2 | most scans |
| 2 | BW · Clean T=180 | BW | 300dpi, simple T=180 | clean laser prints |
| 3 | BW · Strong T=210 | BW | 300dpi, simple T=210 | faint pencil / gray bg |
| 4 | BW · Stained Paper | BW | 300dpi, sauvola w31 k0.25 | yellowed / uneven light |
| 5 | BW · Full-page | BW | 300dpi, otsu, JBIG2, FFPR | flatten all artwork |
| 6 | Color · JPEG2000 ★ default color | JPX | 300dpi, rate 192 | photo/reader tradeoff |
| 7 | Color · Max Squeeze | JPEG | 300dpi, q45 | smaller lossy photos |
| 8 | Color · Balanced | JPEG | 300dpi, q60 | fewer JPEG blocks |
| 9 | Color · Poster 16 | indexed | 300dpi, 16 colors | flat graphics, tiny |
| 10 | Color · Indexed 64 | indexed | 300dpi, 64 colors | diagrams and logos |

Historical automatic choice (§57), superseded for explicit selections by
§203: few-color images (≤256 distinct colors — logos,
diagrams, flat screenshots) took a lossless true-Indexed version (designer
§80: packed 1/2/4/8-bit samples by actual entry count + inline palette +
best Deflate) whenever it beats the codec re-encode, in every color preset —
~10x smaller than RGB-Flate on flat graphics, benchmarked in
`tools/bench_indexed.py`.

### Editable image and native-stream compression (§§203–205)

Designer §203:
> I think we need to add an option that is the algorithm, JBIG2 BW, JBIG2 Color, Flate BW, Flate Color JPEG2000, JPEG.  Because we have no way of choosing between the options at the moment, filters seem to be locked into their algo.  Also, why do we have both JPEG and JPEG2000, and Flate BW and Flate Color?  For backward compatibility?  Aso, the terms strategy should be qualified, is that Threshold automatic strategy?

Designer §205:
> what are the top text compression algorithms, and we should add an option for this also.  And make a benchmark document for that scope of compression also.  Are there support limitations on some of these algorithms?  Any reason to keep lesser compression algorithms?

A preset is a named starting recipe, never a codec lock. The six-choice Image
compression control edits the actual mode while preserving filter UUID/name/
position. Flate Color qualifies the existing palette representation; colored
JBIG2 uses one exact stencil per non-white palette entry. No hidden codec
substitutions. Threshold method names its scope and contains manual AND
automatic options; manual T is not advertised as active for automatic methods.
An independent PDF stream policy compresses native content/fonts, without
changing image samples or re-rasterizing native artwork. Flate is the current
default; Zopfli produces the same Flate format. §213 supersedes encoding-speed
trade-offs as a product rationale. Brotli requires a supporting
PDF 2.0 reader, with an explicit warning and proper extension metadata.
Sizes/times, legacy comparisons and actual reader failures are documented in
`NATIVE_STREAM_COMPRESSION.md`; image rules are in `COMPRESSION.md`.
Both choices use the existing real-PDF/debounce/saved-draft lifecycle, not a
parallel saver. Existing preset defaults remain, but their recipes are editable.

§209 explicitly requests SIZE-ONLY bitmap comparisons at equivalent filtered
pixels, separate from the native-stream study. No compute-time measurements
or speed rankings under the workstation's fluctuating load. Compare actual
Indexed/BW Flate with full Zopfli, Brotli and colored/BW JBIG2, retaining common
native compression and all PDF overhead. Exact quote, protocol and measured
outputs: `IMAGE_STREAM_COMPRESSION.md`. This authorizes headless benchmarking,
not new GUI options/defaults.

### Retain paired benchmark results; omit editorial corrections (§220)

Designer §220 (verbatim excerpt):
> ok, then leave in the tables as it was.  Also, clean this up, we should NOT have typo correction discussions in the docs.

Retain the plain/`+PNG` pairs alongside BW/colored JBIG2 in the main size
tables. This supersedes §219's split. Compare prediction with the same
encoder's plain output, retaining identical prepared pixels and complete PDF
sizes. Sixty of 66 pairs grow; six BW pairs shrink; no algorithm winner
changes in this corpus. All results remain in `IMAGE_STREAM_COMPRESSION.md`.
§§238–240 subsequently separate the primary integrated overview's PNG
effect table; that does not delete either variant or alter this component study.

Use correct technical names directly in explanatory prose, without typo
discussions, correction lists or mnemonic asides. Retain designer quotations
unchanged and keep substantive codec/reader-support decisions in their
topical documents.

Designer §221:
> Also highlight in bold the best of each row in the tables, can you do that in md?  Or not supported?

In the main bitmap benchmark tables, bold the smallest complete-PDF size
within each same-input row, including every tied minimum. This is a size
comparison, not a claim of universal reader support or different fidelity.

Designer §222:
> where is the matrix comparing all algo combos file sizes on complete files, your analysis seems scattered.  We only care about the final file size, this is integrated compression analysis.

Use [INTEGRATED_COMPRESSION.md](INTEGRATED_COMPRESSION.md) as the primary
algorithm-combination comparison. Each reported cell is an actual complete
saved PDF, including native/image/resource/extension/container overhead.
Cross image encoding and prediction with native compression; never add
separate payload savings to predict an unmeasured cell. Keep fixed-pixel
comparisons distinct from different DPI, palette, threshold or lossy recipes.
The older isolated studies remain supporting methodology/evidence only.

Designer §223:
> Why does your table have columns like Z/B, etc?  We agreed that those are not realistic?  Same for F/Z.  These are useless.  Have one table with all the algo combos as rows and choose a 5 typical types of pdfs that cover the major styles.   Then we will have other table that goes into more details for specific scenarios, like color photos, scanned BW docs, mix images text, etc.  There are only a few major classes of pdfs that are load bearing to pdf compression algorithm analysis, no?

The primary integrated matrix has realistic algorithm combinations as rows
and representative complete PDFs as columns: the original five plus the
NASA Kepler technical document added by §231. Use descriptive names.
For packed pixels, use the same general compressor for images and native
streams, not mixed general-codec pairs. Specialized image codecs retain
their meaningful optimized-Flate/Brotli native alternatives. Classic Flate
remains a labeled reference, not another recommended product choice. Keep
page handling/fidelity explicit, with focused scenario tables for palette,
DPI, threshold, photo, scan and mixed-content detail. These classes are
a useful benchmark basis, not an exhaustive PDF taxonomy or reader certificate.
This supersedes §222's exhaustive cross-product presentation; its actual
complete-file metric and strict output verification remain unchanged. It
does not migrate recipes or implement the proposed compression controls.

### Integrated overview output groups (§§227/228)

Designer §227 (verbatim excerpt):
> In the table "Overview — final complete-file bytes" Make three sections to clarify the analysis, the first will be all BW algorithms, then indexed colors, then full colors algorithms.  It's generally expected that JPBIG2 will be the best for BW, then maybe Brotli or layered JBIG2 for low pallettes, then JPEG, JPG2000 for full color.

Designer §228 (verbatim):
> No, put in a same continuous table with a row as the divider, no numbering.  Merged cells if md permits, if not, just blank cell except for the far left one with the title.

Present the primary overview in this order: **BW**, **indexed color / low
palettes**, then **full color**. Retain every representative PDF column and
add the sixth Kepler case (§231), keeping the combinations selected under
§236, including the unresampled classic-Flate reference and plain/predicted
pairs. Use one continuous Markdown table with one column-header row, not
separate tables or numbered headings. Each group starts with an unnumbered
divider row: a bold title in the far-left cell and otherwise blank measurement
cells. Standard Markdown tables do not merge cells; do not require HTML
colspan. Put unresampled preserve-images controls first under their own
reference divider in the same table, above the three algorithm groups.
Within each group, put native-retaining rows before its FFPR rows; indexed
FFPR belongs to indexed color, not full color. Preserve separate native/FFPR
and lossy/lossless fidelity minima, including tied bold winners. Expected
codec strengths guide interpretation, not changes to measurements, automatic
codec selection or claims of a universal winner. This is a presentation-only
refinement of §223; §§236/237 subsequently remove redundant bitmap-reference
rows throughout the analysis without deleting historical benchmark artifacts.
See [the overview](INTEGRATED_COMPRESSION.md#overview--final-complete-file-bytes)
and TODO §§232/233.

### Integrated benchmark labels (§232)

Designer §232 (verbatim):
> "Black and white (BW)" rename to "Black and white (BW + Otsu)" and remove the "; keep native", this is implied by no FFPR.

Use **Black and white (BW + Otsu)** for the overview's BW divider. Omit the
redundant `; keep native` from combination labels throughout the report and
its generator: absence of FFPR means original text/vectors remain native.
Keep FFPR explicit and retain compressor suffixes such as `Zopfli-Flate
native`, which identify native-stream compression rather than image encoding.
This changes presentation only, not processing, measured bytes, minima or
the explicitly labeled Simple thresholds in the focused sensitivity table.
See [INTEGRATED_COMPRESSION.md](INTEGRATED_COMPRESSION.md).

### JBIG2 flow regression versus codec-comparison input (§233)

Designer §233 (verbatim):
> that is a good test case for the full flow, the flow should never make a JBIG2 worse, document this as an issue and a test case to use to fix and check for regressions.  Also, this is NOT a good test case for this table, find another BW pdf that is NOT already JBIG2, or else the results are meaningless.

Keep the complete eight-page `scan-jfk-poor-copies.pdf` as an end-to-end
non-regression fixture, not as the main BW conversion/compression example.
At unchanged 300 DPI with lossless JBIG2 and no requested visual changes,
the real save flow must retain exact source bitmap samples and page geometry
and must not grow the final complete PDF relative to the input or a compatible
preserve-images control. Include native-preserving and FFPR paths. A
no-op must not accidentally round source DPI upward and resample. A future
size guard must not silently ignore an intentional transform or substitute
another codec; preserving existing valid JBIG2 is not a codec substitution.
Issue B114 records the defect, executable regression contract and §235 repair.
It remains OPEN pending designer acceptance; normally passing worker checks
do not supply that acceptance.

Use whole `scan-naca-tm972.pdf` (11 pages, 374,461 bytes) for the six-case
overview's BW scan column. Its eleven 1-bit images use `/CCITTFaxDecode` at
approximately 300 DPI, not JBIG2; it contains scanned typewriting, annotations,
diagrams and an existing OCR layer. Keep the other five representatives and
all retained combinations (34 under §236). Verify actual stored `/Filter`
values, never infer source compression from the PNG/TIFF returned by extraction (B115).
Keep the JFK file and historical measurements untouched, outside the current
codec-comparison tables. Replace, independently save and verify every retained
scan cell; never reuse the old scan's sizes under the new filename. Source/output
hashes, original reader limitations and common 300-DPI transformations remain
required. This does not declare B114 fixed or authorize pixel changes to a
same-DPI no-op. See `INTEGRATED_COMPRESSION.md` and `TEST_PLAN.md`.

### Same-density composition repair (§235)

Designer §235 (verbatim):
> Please fix that bug

B114 must be repaired, not left as expected test failures. Preserve the
actual fractional image/mask sampling density when constructing the native
composition matrix; the renderer does not require integer DPI. Remove whole-
DPI upward quantization, which turns harmless PDF float noise near 300 into
a real 301-DPI intermediate. Keep genuine fractional densities and mask
resolution, the original composition/layer policy and the one final resize.
The nominal same-density source grid must remain the original pixel grid.
Remove the five expected-failure markers and require original bitmap sample
equality and complete-file non-growth through native and FFPR saves. Add
genuinely fractional-density tests so the fix cannot indiscriminately round
real resolutions. Recheck color/alpha/rotation/tile/cancellation behavior and
regenerate affected benchmark preparations with new provenance. Old files
and hashes stay historical; no unrelated encoder switches/defaults change.

### JBIG2 encoder documentation and exploration (§234)

Designer §234 (verbatim):
> Add a JBIG2 dev doc, add documentation relevant to the algo and add a TODO that we need to explore other JBIG2 optimization features and detail them

[JBIG2.md](JBIG2.md) is the dedicated developer reference for current codec
scope, safe/lossy features, upstream limitations, PDF embedding and a size-only
exploration protocol. TODO §240 tracks duplicate-line typical prediction,
symbol classification settings, zero-error refinement, shared dictionaries,
encoder alternatives and their validation gates. Current `-p` generic coding
and actual GUI capabilities must remain explicit. A research/documentation
request is not approval to enable lossy modes or change encoders/defaults.
The B114 same-DPI source-pixel/no-growth contract remains an independent
prerequisite for promoting future optimization results.

### Complete matrix coverage (§229)

Current row selection is narrowed by §236 below; complete six-input coverage
continues to apply to every retained row.

Designer §229 (verbatim):
> please drop that rule, every row gets benchmarked, even if redundant, this is also a sanity check on the benchmarks.

Benchmark every combination against every representative PDF: all 34 retained
rows (§236) × six inputs (§231), including image-free inputs with FFPR off. An unused image
codec is a valid no-op, not an inapplicable recipe; native/font/container compression
still runs. Save and verify each row's actual complete PDF even when its size
duplicates another row. Never fill a newly measured cell by copying a control
size or aliasing another recipe's output. No-image cases must preserve native
artwork and must not invent a raster just to exercise the selected image codec.
Record that the image stage was unused; it is not codec-compression evidence.
Compatible previously measured cells may retain their actual files with strict
source/implementation/output verification and explicit provenance. Preserve
300-DPI transforms, same-fidelity minima, reader-support limits and the single
continuous table. Failures remain explicit, never blanks or guessed sizes.
See [INTEGRATED_COMPRESSION.md](INTEGRATED_COMPRESSION.md) and TODO §234.

### Remove redundant Classic-Flate benchmark rows (§§236/237)

Designer §236 (verbatim excerpt):
> ok, proceed.

The approved ten-row list is recorded in [DESIGNER_VERBATIM.md](DESIGNER_VERBATIM.md#236--approve-ten-complete-benchmark-row-removals-verbatim-excerpt-2026-10-16).
Remove eight complete Classic-Flate bitmap rows from the main overview
(native/FFPR × BW/indexed × plain/predicted). Designer §237 extends the
initial Logos/artwork-only focused scope consistently to all focused tables:

> Obviously, if a row was considered redundant in the overview, is should also be dropped from the focused view, or else the statement that the row has low added values was incorrect.

The measurement inventory is **34 rows × six complete inputs = 204 measured
cells**. §§238–240 subsequently split its display into 26 baseline rows and
eight isolated PNG-effect rows without dropping measurements.
Remove equivalent Classic-Flate bitmap rows from Logos/artwork, Mixed
text/images, Scanned BW text and Threshold sensitivity. Do not retain them
as supplemental references. Preserve the unresampled Classic-Flate control
in the overview and applicable photo/native-focused sections. This does not
globally remove the encoder from older diagnostic tooling or authorize
GUI/recipe changes.

Keep Zopfli/Brotli predictor pairs, continuous fidelity groups, same-input
bold minima, 300-DPI transforms, and actual complete-file measurements even
for no-image cases. Recompute current coverage, conclusions and predictor
statistics from the selected outputs. Historical full-scope artifacts retain
their original files, hashes and scope; a verified selection is not a new
encoding run. Use one shared combination selection for overview and focused
tables so removed bitmap references cannot leak back into another section.
See TODO §241.

### Isolated PNG-prediction effect (§§238–240)

Designer §238 requests a separate single-change comparison, §239 requires
measured saved-file bytes only, and §240 limits the first implementation to:

> Start with only "PNG prediction" so that I can review an make sure it is correct.

Move the eight PNG-prediction rows out of the primary integrated overview
into their own table. Its rows name the matching plain baseline; retain all
six representative PDF columns. Each cell shows the measured PNG-prediction
complete-PDF bytes and signed percentage change from the measured plain
baseline: `100 × (PNG bytes − baseline bytes) / baseline bytes`. Negative
means smaller, positive means larger. Keep the PDF source, prepared pixels,
recipe, general compressor and native-stream policy identical within each
pair; only reversible image-row prediction changes. No size estimation,
payload-only comparison, guessed baseline or missing-cell substitution.

The measurement scope stays 34 × six: 26 baseline overview rows / 156 size
cells plus eight PNG effect rows / 48 size cells. No PDF is re-encoded for
this presentation change. Preserve measured files, hashes, reader caveats,
no-image sanity controls and the existing focused-scenario data. The new
six-document effect table is the first review surface; do not restructure
residual streams or add other optimization tables before that review.

Overview bold minima are recalculated among its baseline rows within the
same document/fidelity group. In the paired effect table, bold measured bytes
mean the PNG result is no larger than its own baseline (including ties), not
the smallest across unrelated documents/recipes. Explain this distinct paired
emphasis locally; §§247–249 below supersede the original rounding and tie styling.
This supersedes §220's placement of PNG rows in the primary overview, not
the requirement to retain and verify both measured variants. See TODO §242.

### Expanded controlled experiments (§242)

Designer §242 requests more PNG combinations and the next binary experiment.
Extend PNG coverage with up-to-16 and up-to-64-color indexed canvases, each
native-preserving and FFPR, with matching Zopfli-Flate/Brotli policies over
all six whole PDFs at 300 DPI. This adds eight baseline/prediction combinations
and 48 paired cells. Publish the matching plain baseline sizes as well so
every signed change has a visible measured denominator. Expanded coverage is
34 baseline rows / 204 sizes plus 16 PNG rows / 96 effects. Do not invent PNG
variants for already specialized JPEG, JPEG2000 or JBIG2 image payloads.

Reuse compatible complete measurements with their original provenance;
encode only missing cases. Normal strict resume/import checks remain intact.
Record the bounded source-compatibility proof for explicit historical reuse,
and never relabel imported PDFs as newly encoded. Preserve all-page decoded
pixels, native content, image bytes across native-stream recompression, and
whole-file hashes. Keep no-image cases as independent actual saves.

Treat the Brotli observation as scoped to the measured corpus. Count wins,
ties and regressions, retain counterexamples, and do not change product defaults
from an empirical size table. The next experiment needs its own named A/B
factor and plan before encoding. Method and scope are centralized in
`COMPRESSION_EXPERIMENTS.md`; results stay in `INTEGRATED_COMPRESSION.md`.
The next planned A/B factor is native/residual-stream encoder selection:
standard Flate reference versus the named optimized encoder, with image
payloads held byte-identical. Five specialized-codec FFPR rows and two native
controls give 42 six-input pairs. This is a controlled reference experiment,
not a reinstatement of classic Flate in the product menu.
See TODO §§243/244.

### Percentage-only PNG effect table (§243)

> also, remove the sizes from the binary test table "PNG prediction — measured effect versus baseline"

Supersede only the PNG effect table's byte-count presentation above: show
signed percentage changes alone, computed from the same measured complete
files. Keep all 16 rows / 96 pairs, six columns, visible overview baselines
and the rounding/emphasis rules in §§247–249 below. Exact byte counts and
original provenance remain in frozen evidence; no encoding is repeated.
Update reusable generation and tests. Focused and native/residual size
tables are outside this change. See TODO §245.

### Brotli annotation and PNG winner analysis (§244)

Underline every Brotli row label in the PNG effect table only, using GitHub's
`<ins>Brotli</ins>` syntax; retain all measurements and baseline identities.
Explain the annotation with the measured corpus, not a universal obsolescence
claim. Compare PNG candidates against every measured same-source/fidelity
competitor, distinguishing unique wins from no-image ties and reader tiers.
Retain evidence that prediction can improve a compressor without winning
the overall complete-file comparison. No codec/predictor removal or default
change is authorized by a question about the results.

The next A/B recommendation is a proposal, not a benchmark execution request:
JBIG2 generic repeated-row prediction `-d` off/on with identical samples,
fixed save settings and reader gates. See `COMPRESSION_EXPERIMENTS.md`,
`JBIG2.md`, existing optimization TODO §240 and presentation TODO §246.

### Brotli baseline versus Zopfli treatment (§§245/246)

Add a separate controlled comparison to the integrated report: Brotli is
the measured baseline, Zopfli the treatment. Show signed complete-file
percentage changes over the same six PDFs; negative means Zopfli is smaller.
§246 clarifies the scope: FFPR with specialized JBIG2 BW, layered-color
JBIG2, JPEG and JPEG2000 lossy/lossless. Hold source, exact encoded images,
recipe and save policy fixed; change only native/residual-stream compression.
Use five rows over six PDFs / 30 pairs, reusing verified Zopfli files and
saving missing actual Brotli baselines through the shared integrated saver.
Do not broaden this table to retained native artwork or packed-image codecs.
Decompose every regression into measured stream and container/syntax bytes;
use metadata-only controls to distinguish extension overhead from payload
compression. No image re-encoding, guessed sizes or rewritten provenance.

Investigate whether Brotli is worse and why; do not assume it must win or
infer a page-count cutoff from unrelated documents. Cross-document page
counts are descriptive, not a causal page-count experiment.

Use **Zopfli** in development-document tables, not Zopfli-Flate. Explain once
that it produces ordinary FlateDecode data, while Brotli needs a supporting
reader. The longer label distinguishes encoder from format educationally,
not a second Zopfli variant in these tables. Preserve frozen measurement
identities, exact quotes, raw evidence and application settings/controls;
shorten reporting labels only. See `COMPRESSION_EXPERIMENTS.md`, TODO §247.

### Percentage precision and comparison order (§§247–249)

> Don't bold 0% in the "PNG Prediction" table please

> Decide on a stanard number of decimals for percentage diff.  Let's use 2 decimals.  And move the brotli table after png.

> if it rounds to 0.00%, no bold please

Use exactly two decimal places for signed percentage differences in the
integrated comparison tables and their reusable formatters. Compute from the
original measured complete-file byte counts, never by padding or re-rounding
previously displayed percentages. Normalize rounded negative zero to `+0.00%`.
In percentage-only tables, bold only displayed negative reductions; leave exact
ties and any changes that round to zero unbolded. Preserve the Brotli underlines.
Byte-count emphasis in other tables still reflects actual measured bytes;
rounded zero does not prove an exact tie. Retain exact byte differences in
the evidence/explanation rather than adding extra percentage precision.

Place the complete FFPR Zopfli-versus-Brotli section immediately after the PNG
section, before focused scenarios. Keep its explanation with its table and
preserve all measurements, source identities, reader caveats and other section
order. These are presentation changes, not authority to rerun encoding or
change application settings. See TODO §248 and `COMPRESSION_EXPERIMENTS.md`.

### Treatment titles directly above effect tables (§250)

Designer §250 requests concise titles immediately before both percentage-effect
tables and approves these exact titles:

- **Enable PNG prediction — final PDF size change (%) versus prediction OFF**
- **Replace Brotli with Zopfli for FFPR residual streams — final PDF size change (%)**

Use level-three Markdown headings directly above the corresponding tables,
after the explanatory prose. Keep section headings/anchors, cell values,
two-decimal precision and emphasis unchanged. This is documentation-only;
no new benchmark encoding or full-suite run is needed (§241). See TODO §249.

### Brotli declaration is opt-in compatibility metadata (§251)

> Also, we should remove the "extension specification" for all the tests and filters by default, but add it as a compatibility option when Brotli is selected.  Only show that option for Brotli, which is different than our existing pattern to always show the option by grey it out when not applicable.

Default `brotli_declaration` to false for existing/missing-field recipes, new
filters, headless saves and benchmark/test outputs. The shared saver omits the
Brotli developer-extension entry by default, including an inherited entry in a
prepared/source PDF; preserve unrelated extension entries and legitimate source
version information. With the option on, add the existing PDF 2.0/catalog
declaration once, preserving other declarations. This metadata option does not
change compressed samples/operators or supply missing reader decoder support.

Expose **Include Brotli extension declaration (Compatibility)** (§252) as an unchecked
checkbox beside the stream-compression settings. Show it only when Brotli is
selected; hide it entirely otherwise, explicitly excepting this one control
from the always-visible/disabled convention. Retain an inactive choice when
switching codecs, but exclude it from non-Brotli effective cache identity.
For Brotli, include it in identity, dirty state, the single 300ms debounce,
Save/Save As/load, Revert/Discard/Cancel and exact saved-file preview/export.
Never auto-enable it for legacy Brotli filters that omit the new field.

Benchmark generation/verification uses the same opt-in policy; identity/resume
checks must not mistake declaration-ON artifacts for default-OFF measurements.
Explicit declaration compatibility tests and metadata-only controls may opt in.
Preserve frozen old artifacts/numbers with their declaration-ON provenance;
measure new complete files before publishing replacement results. See
`NATIVE_STREAM_COMPRESSION.md`, `COMPRESSION_EXPERIMENTS.md` and TODO §250.

### Contextual help and refreshed default-OFF measurements (§§253/254)

Remove the inline Brotli reader-warning label, including its layout space.
Put the short warning in the Brotli selection's native Qt tooltip and expose
equivalent help for keyboard/accessibility users. Keep the visible "limited
support" choice label and the Brotli-only (Compatibility) checkbox. Use the
shared convention in `TOOLTIPS.md`; do not retheme tooltips or add private
hover timers, and never dispatch filtering for a help interaction.

Remeasure actual complete PDFs under the declaration-OFF policy, updating all
affected overview/focused/reference/effect cells and conclusions together.
Reuse verified prepared image data; do not repeat rasterization, thresholding
or palette transforms. Rerun all Brotli image/native encodings in the published
integrated and supporting studies, including plain/PNG and levels 9/11 where
measured. Non-Brotli controls may be reused with their actual provenance.
Save new complete files with the shared saver, verify exact rendered
object graphs/stream bytes and source/output hashes, and retain original
declaration-ON provenance separately. Restore only catalog version markers
proven to have been forced by the old declaration producer, never legitimate
source version information. Measure sizes; do not subtract assumed overhead.
When the proven original has no catalog version entry, delete the old
producer's entry structurally; do not serialize an artificial `/Version null`.
Preserve two decimals, unbolded rounded zeros, baseline/treatment directions
and the approved adjacent titles. See TODO §§251/252.

### Best stream compression (§§255/256)

Add **Best (Zopfli/Brotli)** to the existing PDF streams selector. It compares
those two lossless encoders for native streams (drawing/text/font resources)
AND packed BW/indexed image streams. Eligible sample-based images and masks
use the same lossless encoding; specialized JPEG, JPEG2000 (including lossless)
and JBIG2 BW/color payloads are excluded. This does not choose image codecs or
visual/quality settings. The normal composition/conversion pipeline still runs
for every source image; CCITT is an input format, not a preservation exception
or an output choice. Choose per stream, since pages
can share resources and one page can contain multiple streams. Empty streams
remain plain under the existing safety rule; this named option does not add
another general compressor or change explicit saved recipes/defaults.

Encode each distinct input with both existing full-workload adapters, verify
readback, and account encoded bytes plus filter/Length dictionary costs.
Keep reusable encoded candidates in the existing scratch work directory,
not all decoded image samples in an unbounded in-memory cache.
Compare actual complete saved all-Zopfli, all-Brotli and mixed candidates with
identical once-prepared image samples/palettes/predictors, fonts, content and
PDF-ID framing; specialized J* payload bytes stay identical. Publish the
smallest measured candidate, preferring fewer Brotli streams on exact ties.
This is best among evaluated assignments, not a mathematical global optimum.
Do not rerender/filter images in this encoding stage or silently skip a
missing/failing encoder. Existing explicit policies remain native-only; the
new Best policy is the approved shared packed-image/native choice. Do not
remove Flate BW/Color or silently migrate their saved recipes.
Use representation labels **Packed BW** and **Indexed color** for those two
existing image choices; they cannot promise Flate when Best may store Brotli.
Keep internal mode IDs `bw-flate`/`indexed`, defaults and saved recipes intact.
Retain existing manual choices/legacy recipes; no automatic migration is
approved. The fixed-encoder binary table remains measured historical evidence
with unchanged encoder policies, not a benchmark of the new Best policy.

Best explicitly permits Brotli and therefore needs reader-support help under
the shared native tooltip convention. Its default-OFF (Compatibility) checkbox
is visible as it is for explicit Brotli, and effective in its recipe identity.
Only add the optional declaration when a saved candidate actually uses Brotli.
Use the existing dirty/debounce/Save/Save As/Revert/Discard/Cancel and real-file
preview/export lifecycle; no separate best-mode GUI processing path.

### Best for every app filter (§257)

All built-in app filter recipes now seed **Best (Zopfli/Brotli)**. Apply one
versioned startup migration to every saved custom filter and built-in override,
including explicit old Flate/Zopfli/Brotli choices. Change only
`params.stream_compression`; preserve UUIDs, aliases, labels, ordering, DPI,
image codec/quality, FFPR, compatibility declaration setting and other metadata.
The untouched Original reference is not a filter and stays unchanged.

Persist the migrated saved records and revision before constructing effective
recipes or scheduling work, using the existing settings owner. Failed settings
synchronization must fail clearly, not report a successful migration. This is
an explicitly authorized one-time change, not a permanent Best clamp: later
deliberate manual compression choices survive restart. Save As/copies inherit
the actual current recipe normally. Explicit benchmark recipes, frozen tables
and the headless legacy missing-policy fallback are not rewritten by an app
default change. §257 supersedes §§255/256's no-default-migration boundary only
for this app migration; the fixed encoder APIs retain their meanings.

### Best-only integrated overview (§258)

The primary complete-file matrix uses the actual Best stream policy for every
image recipe, not separate fixed Zopfli/Brotli rows or a minimum copied from
their old sizes. Explain Best once in the overview section, with a link to
the specialized controlled compressor comparison; omit stream-policy names
and "optimized residual streams" suffixes from its row labels. The unresampled
Best reference preserves samples, not necessarily their original lossless
encoding; label it "Unresampled reference", not "Preserve images". Keep one
continuous table, six complete inputs, native/FFPR fidelity groups, 300 DPI,
plain image prediction and measured complete-file bytes. Packed BW/indexed
images participate in Best; J* payloads remain unchanged.

Move fixed Zopfli/Brotli alternatives to the specialized binary section,
extending its coverage to all overview recipes. Its factor is residual/native
encoding for specialized J* or preserved-image cases, and the shared general
encoder for packed-image cases; state this boundary explicitly. Retain the
original FFPR-only experiment and its accounting as a separately identified
subset. Keep Classic-Flate reference evidence outside the Best-only matrix.
PNG OFF/ON pairs remain a separate fixed-encoder experiment; their baselines
are not renamed to Best or silently compared against new Best results.

Save actual new Best outputs through the shared saver from verified frozen
preparations, without repeating raster/image preparation or J* encoding.
Verify source/preparation/output hashes, exact decoded native/image content,
unchanged visual graph and protected J* payloads. Retain frozen fixed-encoder
provenance and all old measurements. This updates reporting and benchmark
policy, not app settings, core algorithm behavior or reader certification.

### Visible controls and PNG-prediction guidance (§259)

Keep the relocated fixed Zopfli/Brotli sizes and Classic-Flate control always
visible in the specialized binary section, with no collapsible details/summary
wrapper. Preserve every measured cell, label, denominator and emphasis rule.

Lead the PNG-prediction section with results and a decision tree for the
**prepared output image representation**, not the original input codec.
No eligible bitmap is a no-op; PNG row prediction does not apply to J*
payloads or native text/vector streams. For packed BW/indexed samples, the
fixed encoder and actual content matter: the representative Brotli study has
no reductions, while Zopfli improves some scan/text-like and FFPR cases but
not the current color-photo/artwork cases. Retain the earlier noisy-BW Brotli
counterexample and the distinction between a baseline improvement and an
overall size winner, including reader eligibility.

This is measured guidance, not a universal predictor-elimination rule or an
implemented automatic policy. Best preserves the selected predictor; it does
not search prediction OFF/ON. New-input certainty requires measured complete
OFF/ON files with other factors fixed. Update the documentation publisher and
its presentation regressions, without re-encoding the corpus, changing app
behavior or modifying frozen evidence. The results/conclusion must precede
the method and existing percentage table.

### Joint image prediction and stream selection (§260)

Supersede §259's runtime predictor-preservation boundary: **Best
(Zopfli/Brotli) always tests PNG prediction OFF and ON for eligible prepared
image samples**, with both encoders. Do not discard Brotli+prediction because
of a corpus heuristic; the noisy-BW counterexample rules that out. Native
text/vector/font streams still compare the two encoders without image-row
prediction. An image stream is not a native text/vector stream, but either
kind can select Zopfli. "PNG prediction" describes reversible sample-row
filtering; the input need not contain PNG files.

For explicit Zopfli, expose **PNG prediction: Off / On / Best**. This
selection controls eligible packed BW/indexed image storage as well as the
existing Zopfli native-stream policy. Best compares both predictor states;
Off/On force their stated state. Keep the control visible but disabled at
Best for the Best stream policy, and disabled/inapplicable for J* image
choices and other fixed stream policies. Preserve the saved explicit choice
when switching controls. Include only the effective choice in recipe/cache
identity; use the existing debounce/dirty/Save/Save As/Revert lifecycle.

Use one core predictor and selection saver, disk-backed encoded alternatives,
exact sample readback and actual complete-file trial saves. Include predictor
dictionary and PDF/container overhead when selecting; prefer fewer Brotli
streams, then fewer predictions on exact ties. Never repeat composition,
resizing, thresholding, quantization or J* encoding for a storage trial.
No-image/native-only and specialized J* payloads need no predictor work.
For general images, validate sample layout rather than guess from names or
extensions. Preserve unknown layouts in automatic mode; an explicit On must
fail clearly if it cannot be applied. Keep cancellation/atomic publication,
mask/palette/native geometry and the compatibility declaration contract.

Legacy headless explicit-policy calls without a predictor field keep their
native-only semantics; app recipes carry the new choice. Frozen §258
benchmarks explicitly retain predictor-preserving selection and remain
labeled as such, never relabeled as measurements of §260. Update the decision
tree and publisher without inventing replacement sizes. Verify both encoder
and predictor outcomes, packed row padding, masks, exact visuals and the
shared GUI lifecycle; capture/view the new control states.

### Sixth representative: technical illustrations (§231)

Add `examples/models-nasa-kepler.pdf` as a sixth complete-file overview
column, **Technical illustrations**, rather than replacing a current class.
Its 12 pages all contain native text; ten have vector drawings, nine have
bitmap images (15 placements total), and three have no bitmap placements.
It broadens the existing short artwork and research-paper cases with a
multipage illustrated technical document and includes the designer's regular
regression input. This is a practical additional stress case, not a claim
that PDF composition has six exhaustive, mutually exclusive classes.

Measure all retained rows (34 under §236) at the common 300-DPI transform
resolution, with the same unresampled controls, native/FFPR distinction and
reader limitations. Keep
all previous actual files/values; verify pinned implementation changes and
their hashes instead of relabeling old measurements as freshly encoded.
See `INTEGRATED_COMPRESSION.md`, `TEST_PLAN.md` and TODO §236.

### Uniform resolution and color FFPR (§§224/225)

Designer §§224/225 supersede the earlier deferred-color-FFPR scope and the
mixed-resolution defaults below. Full-page rasterization is valid for every
supported image codec: flatten the whole original page in full color, resize
once to the chosen DPI, then apply the selected BW/palette/codec transform.
FFPR intentionally removes native text/vector drawing; OFF preserves native
artwork above one transformed bitmap canvas. Both paths use the same saver,
effective recipe, cache identity and exact saved-file preview lifecycle.

Repair rejected preparations at their assembly/filtering root (B108–B111),
not by suppressing diagnostics or weakening pixel checks. The primary and
focused integrated comparisons use **300 DPI for all prepared rasters**;
preserve-images controls deliberately retain their original samples. Remove
lower-DPI scenario variations from the current analysis, retaining historical
artifacts as evidence rather than mixing them into current rankings. Report
actual complete-file bytes and maintain separate fidelity groups. A common
DPI does not make JPEG/JPX quality settings or palette/BW transforms equivalent.

**Preserve images** names an unresampled control that leaves the original
encoded image data/codecs, dimensions, colors and masks unchanged. It does
not mean other filters delete the pictures. Other rows intentionally compose
and transform their bitmap representation (DPI, BW, palette or image codec)
while retaining native text/vectors unless FFPR is selected. FFPR includes
that native content in the page bitmap. Native/font/container optimization
can change whole-file bytes even in the preserve-images control. Distinguish
retaining pictorial content from preserving its original encoded representation.

All built-in raster filter defaults and missing-DPI fallbacks become 300 DPI.
§226 additionally authorizes migrating ALL existing saved raster filters,
including explicit custom values, to 300 DPI. Do this once at initial settings
load before creating saved recipes/artifacts, then record the migration
revision. DPI remains editable; subsequent deliberate choices must not be
reset on every launch. Preserve names, UUIDs, order, codecs and other recipe
settings. Keep built-in UUIDs stable. Any legacy seed renamed for clarity retains its
identity; do not create a second low-DPI comparison profile. Implementation
and validation are tracked in TODO §§227–229.

### Compression combinations: documentation and UI review (§§210/211)

Designer §211:
> Make a documentation table of reasonable combinations, also, should we have the combination as a single compression dropdown (eg Brotli+JBIG2, FFPR+JPEG2000, etc.)? Or separate controls that are enabled/disabled?  Start with the table please.

The designer asks for a table and recommendation, not an approved replacement
UI. `COMPRESSION_COMBINATIONS.md` separates current capabilities from proposals:
shared general compression for packed BW/palette pixels plus native streams;
native-only compression alongside specialized image codecs; automatic small
painting streams after FFPR + a specialized codec. Color FFPR is authorized
by §224 and its implementation is tracked in TODO §227. Mixed native-Brotli/image-Flate is valid PDF even if
omitted from a future simplified editor. Recommendation: separate controls,
visible disabled effective states and a read-only combined summary, not an
enumerated cross-product menu. This does not supersede §§203–205, change any
saved recipe/default.

### Opinionated best encoding, with reader-support choices (§213)

Designer §213:
> so all pdf readers can decode flate encoded with zopfli?  Encoding is not a constrain, the objective of this project is to be an opinionated pdf compression suite with the best available algorithms for encoding, we drop superceded algorithms, the only concern that affects decisions would be pdf reader support, where for some usage, a more generally supported decoder would be proferred, in others, the user may expect readers to have the most modern and best pdf reader.

Do not preserve a weaker encoder or product mode because it is faster or has
fewer encoding dependencies. Select the strongest validated encoding for the
intended reader support, comparing complete PDFs at the chosen representation
and fidelity. Keep superseded methods as benchmark baselines, not normal
product choices. Zopfli and ordinary zlib target the SAME Flate decoder, so
there is no compatibility reason to present them as different user choices.
The target is optimized Flate (currently Zopfli is the strongest measured
Flate encoder here) versus genuinely different decoder requirements such as
Brotli. Modern-reader support must be feature-tested, not inferred solely
from a new version or PDF 2.0 label; allowing Brotli does not prove it always
makes the smallest full file. Existing exact-codec/fidelity rules remain.

§213 supersedes the old speed-knob brief and worker arguments for keeping
Flate BW merely to avoid the JBIG2 encoder dependency. It does not prove all
BW/palette/photo codecs are universally dominated, approve the proposed UI
layout or authorize cross-codec substitution under explicit labels. §224
separately authorizes color FFPR and §225 updates all default resolutions.
Current three-way native selector and zlib paths remain implementation gaps,
tracked in TODO §217; no runtime change is claimed by this documentation pass.
See `COMPRESSION_COMBINATIONS.md`, `NATIVE_STREAM_COMPRESSION.md` and
`DROPPED.md` D3 for the corrected policy and measured scope.

Defined in code: `pdf_minify/core/presets.py` → `PRESETS` (id, label, mode, params).
Rendering/proof rules have moved to their topical docs (designer §125):
main-window regions, dividers, strip, headers and controls in `UI_LAYOUT.md`;
the single-path saver→temp→preview/minis/amounts flow in `ARCHITECTURE.md`;
temp vs persistence in `PERSISTENCE_AND_TEMP.md`; mixed-mode evidence in
`MIXED_MODE_ANALYSIS.md`. This file keeps the original concept; where it
disagrees with those docs, those docs rule.

## Behavior
- Left pane is always the unmodified baseline (no baseline variants); right
  pane shows the selected filter. The strip shows one live mini per filter of
  the current page — Original excluded, the left pane is the baseline
  (designer ruling §30).
- Panes always synced (designer ruling §22): zoom, pan, and scroll in either
  main pane mirror to the other instantly.
- Pane titles elide (designer ruling §124): a title longer than its half
  shows "…" — hovering the label shows the full text.
- Continuous viewer, no page list (designer ruling §26): both panes scroll
  through ALL pages vertically with a 24-scene-unit gap; the left page list is gone and
  the status bar shows `Page N of M` from scroll position instead.
- Autowrap grid (§§26/164/165): zooming out reflows pages into as many
  occupied columns as fit, capped by actual page count. Page spacing is in
  scene coordinates, so capacity uses the transformed page-plus-gap stride
  with no trailing gap. Scene bounds cover only the occupied grid; Qt centers
  it horizontally/vertically on axes that fit. One/two pages never reserve
  nonexistent columns. Original/preview use the same baseline grid and peer
  zoom reflows both; minis use that layout. Zoom/layout never re-filter.
- PgUp/PgDn jump to prev/next page top; click a filter mini still switches
  the right pane's filter (radio-behavior); minis render the current
  (top-visible) page.
- Sizes under minis (designer ruling §32, real amounts §§55/59, single path
  §122): each strip mini carries its filter recipe (threshold strategy, DPI,
  encoder — `§53`) and the FULL-document amount, which is the measured size
  of that filter's saved temp file — container, masks and fonts included.
  No estimates anywhere, no estimators at all; every amount carries its % of
  the original (`23KB (10%)`, original header `100%`). Flow details and the
  why in `ARCHITECTURE.md` (single-path flow).
- DPI wording stays plain (`150dpi`, no max/≤). §129 supersedes §64's
  earlier ceiling-only interpretation: transforms force exact displayed-size
  DPI with Lanczos, up or down, before encoding. See `COMPRESSION.md` for
  implementation exceptions; this does not change the one-DPI UI (§85).
- Navigator dropped (designer ruling §50): the separate OverviewMap navigator
  is gone — the original (left) window is the navigator. The right panel keeps
  preset, strategy, threshold, DPI, page-size, force-raster, page buttons,
  Save and Cancel; page/progress/status stay in the status bar.
- One panel + menu (designer ruling §32): no left panel. File actions live in
  the menu; all working controls live in the single right panel; page/progress
  /status live in the status bar.
- Scratch vs kept (designer ruling §123): app scratch lives in the OS temp
  dir (`/tmp` Linux etc. via Qt); saver temp files regenerate from
  input + spec and are swept at startup. User data (last file, custom
  filters) persists via QSettings. Full split in
  `PERSISTENCE_AND_TEMP.md`.
- Background work (§§37/51/90/122/149) uses spawn-context worker processes,
  capped at half the cores, with thin Qt managers. On open, EVERY saved filter
  runs the real saver once; the selected filter is queued first, then strip
  order (§128). Prepared saved-file pages support both views without extra
  filter jobs on first selection or pan/zoom. Disk-backed buffers avoid
  holding every full document in RAM. There is no independent preview/mini
  transform or size-estimator job. See `FILTER_LIFECYCLE.md`.
- Saved/live state (§§109/112/149): control edits make a separate draft,
  display `*`, and debounce processing through ONE shared trailing 300ms timer
  for all recipe controls (§183, proposed default). Programmatic control loading
  never edits recipes. Switching away from a draft prompts Save / Save As… /
  Discard / Cancel; Save keeps the processed live file instead of invalidating
  it. Save As… keeps the original recipe/file and a new named recipe/file.
  Rename changes the name only. PDF export copies the displayed real file.
- Thumbnails = exact mini of the main view (designer ruling §48, intent §32
  + §37 + §45): each strip mini shows EXACTLY what the synced main windows
  show — same pages, same grid, same scroll framing down to the cut-off last
  page — but rendered through that mini's own filter from its internally
  preprocessed file (built in background at start / latest change). Scroll,
  pan and zoom are pure view changes: minis re-frame from cached per-preset
  pages with zero background jobs (§47). A new job runs only on file change
  or filter-spec change (§44).
- Strip style (latest designer rulings §§134/138/145): full-cell theme wash
  on the selected mini, with its thumbnail and caption included. No extra
  border, divider, focus bar, or style accent. The item delegate renders the
  same complete cell for display and drag; Qt size hints reserve scrollbar
  and frame space. The drag ghost has uniform 75% opacity (§146). Detailed
  geometry, selection, and drop rules live in `UI_LAYOUT.md`.
- Per-filter progress (designer ruling §43): EACH strip filter shows its own
  true work progress from 0, never a fake 50% milestone (§§89/95).
  A complete real PDF and its prepared views yield 100% and exact full bytes.
  The status-bar bar keeps only the aggregate job progress; it never replaces
  the per-filter bars.
- Mini progress appearance (§§185/187/190/191): native default-progress style, reserved
  cell width less the shared 4px outer inset at each side (142px in 150px),
  not image width. Inset the opaque white backing too so highlight remains
  visible. §§198/199 replace §190's 50% enlargement: scale native bar height
  and percentage font by 1.25 for minis only (25% larger, not quarter-size);
  no extra white padding, just opaque backing within the bar's bounds.
  Center vertically in the ENTIRE mini frame, including captions, and paint
  above the selection wash. Hide the whole overlay when
  complete; retain actual progress values and existing row/drag geometry.
  Delegate/model and native-metrics details live in `UI_LAYOUT.md`.
- Pending mini labels (§195): no "working…" image/amount placeholder. Progress
  bars convey work; unavailable results stay blank and previously completed
  image/size metadata remain visible during live edits. Keep real errors.
- Action icons (§§196/197): use the native desktop icon theme consistently,
  with a bundled, licensed KDE Breeze SVG subset as the ONE fallback family.
  No custom QPainter glyphs or missing icons. This supersedes earlier claims
  that §120 authorized custom rename artwork and the old theme-independent
  zoom workaround. Revert Changes uses document-revert, not step-history Undo.
  Preserve action meaning, button sizes, tooltips, native disabled styling and
  device-scale rendering. See `ICONS.md` for names, theme changes and packaging.
- Icon Lab (§200): direct View menu entry, modeless reusable comparison of
  genuine Nuvola/Oxygen/similar stock choices with permanent per-choice codes.
  Per-action selections and a copyable reply are a design-review aid only:
  no automatic Apply, settings writes, filter/selection changes or processing.
  The designer rejects the present glyphs; replacement selection is theirs.
  See `ICON_LAB.md` for the comparison and provenance contract.
- Main-region composition (§188): no minis title or placeholder row. One
  shared 4-logical-pixel token owns outer insets and gutters, including the
  panel splitter handle, with no stacked default wrapper margins. Align the
  full-width strip with the main row's side edges and all three side-by-side
  region bottoms. PreviewPair owns the zero-margin equal/stacked preview
  layout; the root owns outer spacing. See `UI_LAYOUT.md`, B96, TODO §191.
- Three-block headers (§192): Original, selected-filter preview, and
  Configuration all use the same single-line PaneHeader plus zero-margin
  header/content component. Configuration is above/outside the right scroll
  area; side-by-side header and frame tops align, bottoms remain aligned.
  Keep shared 4px spacing, native overflow and stable resize behavior.
- Layered low-color JBIG2 (§§192–194): study one lossless binary stencil per
  non-white palette color on an opaque white base; native text/vectors stay
  separate. Shared compose/resize/palette map, exact reconstruction and actual
  COMPLETE-PDF comparison with Indexed. Explicit scope is design/benchmarks
  first, no production filter change. See `LAYERED_COLOR_JBIG2.md`.
- Save As destination (§189): a named copy becomes the active, visibly
  selected filter through the same selection commit path for explicit Save
  As, mini/dropdown/keyboard dirty-switch resolution, and successful open/
  close resolution. A dirty filter switch must not overwrite the copy with
  the initially clicked filter. Preserve Save/Discard/Cancel semantics and
  prepared result ownership; see `FILTER_LIFECYCLE.md`, B97, TODO §192.
- Exact PDF display (§§172–175): both main panes observe their actual files
  at current zoom/device resolution. Disable all PDF-content AA, bitmap
  interpolation and decoder subsampling. Native text/vector geometry gains
  detail as zoom increases; bitmaps remain literal samples. No additional
  display threshold, saved-file mutation, or filter work. Exposed-region
  painting and bounded caches replace prepared-raster-only zoom; prepared
  saved-file pages still supply layout/minis, using nearest-neighbor scaling.
  Genuine encoded colors, gray and opacity are document content, not AA bugs.
- Process-once (§§44/47/48/122/149): a filter result is computed once
  per (input identity + FULL effective saver recipe) and reused.
  Clicking the strip or preset combo with an unchanged key switches panes
  instantly with NO new background job. A new job runs only when the file
  (path + mtime + size) or the effective recipe changes. Filter name/id,
  selection, page, crop, pan, zoom and order never create processing work.
- BW composition clarification (§§168–171): OFF keeps both native text and
  vector diagrams, including original font/geometry/color/opacity. Optimize
  overlapping imagery, not the text or vectors; no invented glyph masks or
  bitmap text plus duplicate selectable layer. One composite canvas is only
  the simple default: images combined on white, native text/vectors above,
  white page backdrops below. Exact native/image stacking is not required
  by §171; FFPR is the flattened-fidelity choice. See `COMPRESSION.md`,
  B89 and TODO §§174/176/177; old per-image-only implementation is superseded
  as the target, not permission to reintroduce color JPEGs in BW.
- BW raster policy (designer ruling §127): Force full-page raster ON
  flattens the page to one image; OFF keeps native text/vectors with one
  combined BW image canvas (§171; never color JPEGs in BW image output). The old mixed-JPEG
  behavior is gone; the JBIG2-layer variant survives only as the
  unimplemented proposal in `MIXED_MODE_OPTION.md`.
- Per-page override (brief §3, not yet built): page remembers its preset; empty = current global.
- Composition/transform order (§§180–182): flatten original bitmap artwork
  and its opacity in full color, then ONE resize to exact final DPI, then
  gray/threshold, palette or codec processing. No original-plus-upscaled
  duplicate filtering or post-filter resize. This replaces the old per-image
  DPI preparation; native text AND vector diagrams still overlay (§170).
  Color includes the real flat page backdrop; BW retains §171's white canvas.
  FFPR continues to flatten the complete page before thresholding.
- ESC cancels thumbnail batch + save job alike (<200ms, partial output deleted).
- Born-digital warning: selecting a BW preset on a text-layer page shows the
  yellow banner (rasterizes text away) with [Continue] [Use Color instead].
- Display rule §106: the strip shows key-addressed store views —
  recomputes never blank displayed minis or amounts (stale-while-revalidate;
  progress bars signal the work). Only opening a new file clears them.
- Effective recipes (§§127/149): preview, mini, final bytes and export share
  ONE result key with the full effective recipe. Toggling FFPR affects exactly
  the selected filter's draft; all other saved recipes/results stay unchanged.
- DPI is a ceiling here only historically (§64): since §129 the save
  transforms force exact DPI (up and down) — see `COMPRESSION.md`, which
  rules on disagreement.

## Issues on this page

B22 — see `issues.md` (gated log). Layout, flow, compression and temp
issues live on `UI_LAYOUT.md`, `ARCHITECTURE.md`, `COMPRESSION.md` and
`PERSISTENCE_AND_TEMP.md`.
