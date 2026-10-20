# Mixed mode — parked proposal, not implemented

## Rulings (verbatim)

Exact designer text from `DESIGNER_VERBATIM.md`. Text outside the fenced
quotes is not the designer's.

**§126** (2026-10-13)

```text
What is a mixed path? I never specified this and it's not indicated as an option. is that to take all the BW text and make a JBIG2 layer in additional to the images? Put this as a new separate option with it's own doc, for now, this should not be implemented, as you can see, you made a mess of this, and it just causes confusion. I never asked for this.
```

## The proposal

Rasterize each page, threshold it, and store the text pixels as one JBIG2
layer while keeping the picture regions as compressed images: the classic
scanned-document sandwich, built from a born-digital page. Text stays
selectable only if an invisible text layer is added back on top.

This is not FFPR. FFPR off keeps native text and vectors over one combined
image canvas; FFPR on rasterizes the whole page (§§127/168–171).

## If it is ever built

- It is offered as an explicitly named option, never as a side effect of
  another control.
- Like every filter, it is one saver whose saved file the preview, minis and
  size read back (§122). Its preview, mini and size behaviour is written down
  before any code.
