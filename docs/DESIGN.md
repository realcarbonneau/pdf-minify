# DESIGN — PDF Minify product design

The first section collects the designer's most important top-level rulings,
copied exactly from `DESIGNER_VERBATIM.md` (§279). Topic pages open with their
own detailed rulings. Text outside the fenced quotes is not the designer's.

## Top-level design principles (verbatim)

### Purpose: a simple, opinionated PDF size reducer

**§3** (original brief)

```text
I want to make a simple app that works on multiple platforms, but first targetting lxde debian linux.  I want to dnd or open a pdf docs and be able to visualize various optimizations to it.  Highly opinionated, eg conversion to BW with a few strategies and a global or per page threshold, like GIMP threshold option.  Also, another option that compresses images within the pdf to jpg XL or whatever highest compression algorithms exist.  Same for BW, JDIC2 (I think if I remeber correctly.  Always max compression for all by default, but tunable if too slow.  Always fast cancel with esc by user as required.  Start by making some md docs directly in this dir with your notes, ideas and tests.
```

Later rulings narrow two details of the brief: JPEG XL is not used (§5), and
encoding time is not a constraint (§213).

**§275** (2026-10-19)

```text
I already ruled the use case, this is for making pdfs smaller, thuse lossless or super high quality images are not a concern, we want something simple for most users.
```

**§6**

```text
what if I am really picky about smooth clean custom UI highly tailored for a specific job, like pan, zoom in/out mouse scroll, next page, prev page, DnD, etc.
```

### Compression: the best available algorithms; reader support is the only limit

**§81** (2026-10-10)

```text
Everything in this project must be maximum compression, BW lossles, reduced palette, probably lossless, jpeg full color usually lossy
```

**§213** (2026-10-15)

```text
so all pdf readers can decode flate encoded with zopfli?  Encoding is not a constrain, the objective of this project is to be an opinionated pdf compression suite with the best available algorithms for encoding, we drop superceded algorithms, the only concern that affects decisions would be pdf reader support, where for some usage, a more generally supported decoder would be proferred, in others, the user may expect readers to have the most modern and best pdf reader.
```

**§278** (2026-10-20)

```text
Don't change standard packages, if you can't change JPEG2000, adjust the JPG settings to match.
```

### Workbench: the original beside each filter's real result

**§9** (2026-10-09)

```text
Put all my comments verbatim in a design md doc, make a docs dir.  make a dev md doc with guidance, including to keep all my comments verbatim.  I want to see a list of preset optimization options, like photo filters on a camera with a smaller version of previews, and when I click on one, the main doc has original and preview (optmized side by side, vertically or horizontally, same for the filter thumbnails, all would be choosable as menu view options.
```

**§23** (2026-10-09)

```text
left side is baseline, so no preview of basline, right side is per filter.
```

**§22** (2026-10-09)

```text
page zoom, pan, etc is always synced on both panes
```

**§48** (2026-10-10)

```text
Still wrong! Thumbnails should be a mini version of exactly the current view of the larger window.  Why is this not clear?  If the original and preview windows (always synced view) show three pages wide and 4 pages high with the last page have cut, each preview shows exactly that from it's own filter view (internal, no shown, file preprocessed in bg at the start or from the latest change).  This seems simple and exacly derived from my previous rulings.
```

**§173** (2026-10-14)

```text
Previews of original and filters must be exact! No additional filtering, smoothing, etc.    AA can be used on text and vector images of course, but never on anything converted to bitmaps.
```

**§175** (2026-10-14)

```text
In otherwises, if it's simpler to drop all AA and smoothing for display, that is ok, I rather precise exat rendering regardless.  So this might be the best solutions overall and addresses the root cuase of the problem.
```

### One processing path; every size is an actual saved file

**§122** (2026-10-13)

```text
The preview need to show the saved file, DO NOT have multiple paths, this is the root cause of alot of your failures!! One single path, process the file, save temp, display temp file in preview, minis come from save temp files once they are processed. This is an important design ruling, please put this in the design under architecture and flow. Do you follow this flow? Do you understand why this is robust and safe?
```

**§149** (2026-10-13)

```text
Ok, this renumbering issue seems resolved, you can document my explicit confirmation.  Next issue, this also seems like a design implementation issue, please find the root cause.  Canon design is that all filters be run for real and the previews come from the filtered files, and these files have the true final size, not an approximation, please make sure this is clear canon design ruling in the proper dev docs.  When I zoom in/out, the preview and minis update live, this is good.  However, when I click on a mini that has not been clicked yet, I see it doing a "Rendering preview..." processing.  This is obviously wrong flow because this is already fully processed to have the mini previews that work.  So something is fundamentally wrong.  There should be no reprocessing EXCEPT for changes to the filter.  And there are two types of changes to the filter, the first is live changes which should update the processing live with a debounce and mark the filter as changed with a star * (per standard GUI conventions, right?).  However, if the chosen filter is changed without saving, there should be a popup for discard/save/save-as (aka save copy, choose best modern term).  If discard, then the previous file is kept (and the temp new live changes file is deleted), inverse if save, save-as keeps both of course.  These are multiple design runlings, please document in the correct places, also document the issues and work on them.
```

### Image model: optimize the images, or flatten the whole page

**§127** (2026-10-13)

```text
No, FFPR is not a mixed path. The basic decision is to optimize existing images, or the full page into a single image. This is the basic functionality. I don't know what your mixed path was, but you were saying something about colors in a BW and I could see the letters being rasterized even when the FFPR was OFF, this was your fail.
```

**§171** (2026-10-14)

```text
Why is this complicated?  The PDF always must have a clear and explicit flattening sequence to display the document.   Why can't we just keep everything bitmaps as a big image and overlay the text.  If this doesn't look nice, then the user can choose FFPR options, or we can add further filter profile options.  Choose a simple strategy that will help reduce the size of the file.  Ideally keeping text and images clearly separate.
```

**§129** (2026-10-13)

```text
OMG, why are you not respecting the DPI? How is that not clear??? DPI apply to ALL image transformations on the page, even if smaller res, they get upsized DPI on their original color pallette, I think Laconz something like that is considered the best, please review notes, if we don't have notes on this, we need to do some research. The design flow is all images are forced to the setting DPI in their original image space, then the transformations are applied (eg BW, algo, jpg compression, etc). Same recipe for FFPR. Do you follow? Please document that and create an compression algorithm page for these rules, flows and benchmarks, also note failures, issues and TODOs on this document and cross reference
```

**§225** (2026-10-15)

```text
I think we should also convert all the filters to 300dpi default for now.  We know that lower dpi will be smaller in general, it's not useful to have variations of this, it doesn't provide information and causes comparison problems.
```

**§203** (2026-10-15)

```text
I think we need to add an option that is the algorithm, JBIG2 BW, JBIG2 Color, Flate BW, Flate Color JPEG2000, JPEG.  Because we have no way of choosing between the options at the moment, filters seem to be locked into their algo.  Also, why do we have both JPEG and JPEG2000, and Flate BW and Flate Color?  For backward compatibility?  Aso, the terms strategy should be qualified, is that Threshold automatic strategy?
```

### Lossy quality: one familiar control that means the same for both codecs

**§272** (2026-10-19)

```text
I had a less skiled worker program this app and documentation, but I am not sastisfied.  The first problem I have is that it was not able to derive a proper quality setting equivalence for JPEG2000 that matched JPG q75 (I think that is what I choose).  This is important for the benchmarks, because we need to set all settings as similar as possible and also follow what users expect and understand (eg q=75 quality setting, not multiple different complex settings), so that the benchmarks mean something and so that users can know what they are setting?  There is already some research done in the repo, please review and do me research if you feel that is required.
```

**§284** (2026-10-20)

```text
Ok, so a single setting is the correct direction, however, for the purpose of out benchmarking, we have to choose a single quality setting that provides the same visual results as jpg.  The reasoning is simple, if jpg q75 provides a certain compression and quality, then the newer J2K is expected to provide a smaller (or in the absolute worst case, the same size) file for the same visual quality level.  This is very simple and basic, I should not have to explain this.  Or else, benchmarks and a newer compression algorithm has no value.
```

The current quality mapping and its measurements are in
`LOSSY_IMAGE_QUALITY.md`.

## Project identity (§230)

The product name is **PDF Minify**. The importable Python package is
`pdf_minify`; the machine/settings/temp identifier is `pdf-minify`. The
application title uses the product name, including Qt's unsaved `[*]` marker.
The designer will rename the GitHub repository separately; do not change its
remote or pretend that a new repository URL already exists.

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


## Preset list
| # | Preset (label) | Mode | Params | Use when |
|---|---|---|---|---|
| 0 | Original (no-op) | — | gc+deflate only | baseline / born-digital keep |
| 1 | BW · Otsu Auto ★ default | BW | 300dpi, otsu, JBIG2 | most scans |
| 2 | BW · Clean T=180 | BW | 300dpi, simple T=180 | clean laser prints |
| 3 | BW · Strong T=210 | BW | 300dpi, simple T=210 | faint pencil / gray bg |
| 4 | BW · Stained Paper | BW | 300dpi, sauvola w31 k0.25 | yellowed / uneven light |
| 5 | BW · Full-page | BW | 300dpi, otsu, JBIG2, FFPR | flatten all artwork |
| 6 | Color · JPEG2000 | JPX | 300dpi, q75 | wavelet color encoding |
| 7 | Color · Max Squeeze | JPEG | 300dpi, q75 | retained filter identity/name; editable quality |
| 8 | Color · Balanced | JPEG | 300dpi, q75 | retained filter identity/name; editable quality |
| 9 | Color · Poster 16 | indexed | 300dpi, 16 colors | flat graphics, tiny |
| 10 | Color · Indexed 64 | indexed | 300dpi, 64 colors | diagrams and logos |

### Lossy quality (§§272–287)

One **Quality** control, 0–100 and default 75, drives JPEG and lossy
JPEG2000; the same number must mean comparable visual quality for both
codecs, through one fixed rule for every page (§§272/284). Encoders come from
standard packages only, and JPEG keeps 4:4:4 to match JPEG2000's full-resolution
colour (§§276/278). JPEG2000 maps Quality to one PSNR target per 512-pixel
tile, calibrated so its median quality equals JPEG's at the same number on
the benchmark pages (§284). The app never chooses between JPEG and JPEG2000;
there is no Best option for them (§287). Rulings, settings and measurements:
[LOSSY_IMAGE_QUALITY.md](LOSSY_IMAGE_QUALITY.md).

Defined in code: `pdf_minify/core/presets.py` → `PRESETS` (id, label, mode, params).
Rendering/proof rules have moved to their topical docs (designer §125):
main-window regions, dividers, strip, headers and controls in `UI_LAYOUT.md`;
the single-path saver→temp→preview/minis/amounts flow in `ARCHITECTURE.md`;
temp vs persistence in `PERSISTENCE_AND_TEMP.md`. This file keeps the
original concept; where it disagrees with those docs, those docs rule.

## Behavior

- Both panes scroll continuously through all pages, with a 24-scene-unit gap
  between pages (§26). PgUp/PgDn jump to the previous or next page top.
- A per-page threshold override from the original brief (§3) is not built: a
  page would remember its own preset, and an empty choice would mean the
  global one.

The rest of the behaviour is specified in the topic pages:

- Window layout, panes, strip, minis, captions, progress overlays, headers
  and exact display: `UI_LAYOUT.md`.
- Real-file processing, saved/live edits, Save As and process-once keys:
  `FILTER_LIFECYCLE.md`.
- Background jobs, threading and Escape cancellation: `ARCHITECTURE.md`.
- Page model, composition order, DPI and codecs: `COMPRESSION.md`; JBIG2
  BW and Color: `JBIG2.md`; the parked mixed mode: `MIXED_MODE_OPTION.md`.
- Scratch versus kept data: `PERSISTENCE_AND_TEMP.md`.
- Icons and the Icon Lab: `ICONS.md`, `ICON_LAB.md`.
