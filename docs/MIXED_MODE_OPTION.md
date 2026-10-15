# Mixed mode — PROPOSAL, not implemented (designer §§126/127)

> Current §§168–171: FFPR OFF keeps native text/vectors over one combined
> BW image canvas. This is NOT the rasterized-text proposal below. What remains parked here is only the
> never-built variant B (JBIG2 text layer + images) and the record of the
> removed wrong implementation (variant A: vector pass-through + color
> JPEGs — that one contradicted BW output and is gone for good).

Status: separate future option. Documented only — nothing here is built,
and the old mixed implementation was removed from the product (see §4).
Quotes in `DESIGNER_VERBATIM.md` §126; work log `TODO.md` 126; `issues.md`
B57. Evidence for every claim in `MIXED_MODE_ANALYSIS.md`.

## 1. What "mixed" meant (the removed implementation)

For a BW filter with the raster checkbox OFF, save copied each text page
unchanged (`insert_pdf` — vector text, fonts, everything) and only
recompressed its embedded images (JPEG q45 @150dpi). Forced pages were
flattened to one 1-bit JBIG2 image. Measured on `images.pdf`: 178,766 B
mixed vs 4,127 B forced — the gap was 129 KB of kept color JPEGs plus
42 KB of transparency masks.

## 2. The designer's alternative: JBIG2 text layer + images

Instead of passing text through as vectors, rasterize each page, threshold
it, and store the TEXT pixels as one JBIG2 layer while keeping the PICTURE
regions as compressed images — the classic scanned-document sandwich, but
built from a born-digital page. Text stays selectable only if an invisible
text layer is added back on top (extra work, extra failure modes).

## 3. Why it is parked, not built

- It was never specified or offered as an option — the checkbox hid it as
  a side effect, which caused every round of confusion in §§103–119.
- A BW filter that embeds 129 KB of color JPEGs contradicts the filter's
  own preview (black-and-white blobs); either semantic needs its own
  preview/mini/amount contract, not a silent branch.
- The single-path flow (§122) must come first: any future mixed variant
  has to BE a saver whose temp files preview/minis/amounts read back —
  not another parallel implementation.

## Issues on this page

B57 — see `issues.md` (gated log).

## 4. What to rule if it ever returns

- Offered explicitly (named option in the Filter row), never a checkbox
  side effect.
- One semantic only: vector pass-through (variant A, already measured) or
  JBIG2 text layer + images (variant B, unbuilt) — not both.
- Preview/minis/amounts contract written before any code, per §122.
