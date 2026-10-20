# PDF Minify — overview

PDF Minify makes PDFs smaller. Open a PDF, compare filters side by side and
save the one you want. Every filter produces a real saved PDF in the
background; the preview, the strip minis and Export all read that file, and
the size shown is its exact byte count. Selecting a filter or changing the
view never reprocesses. Filter edits debounce, show `*`, and offer Save,
Save As…, Discard or Cancel when you leave the filter (§149).

The top-level design principles, word for word, open [DESIGN.md](DESIGN.md).

## Key facts

- **Image compression** is chosen per filter: JBIG2 BW, colored JBIG2, Packed
  BW, Indexed color, JPEG2000 or JPEG. The selected codec is never replaced
  by another one (§203).
- **Page model**: FFPR off keeps native text and vectors over one composed
  image canvas; FFPR on flattens the whole page into one image (§§127/171).
  Images are composed in full colour, resized once to the target DPI
  (default 300) and then transformed (§§180/225).
- **PDF streams**: every app filter uses Best (Zopfli/Brotli) (§257). Brotli
  output needs a reader that supports it.
- **Quality**: one 0–100 control, default 75, for JPEG and JPEG2000
  (§§272/284). The app never chooses between the two (§287).
- **Display**: the actual saved PDFs are drawn at device and zoom resolution,
  without anti-aliasing or interpolation (§§172–175).
- **Icons** follow the desktop theme with a bundled Breeze fallback (§197);
  View → Icon Lab… compares icon sets (§200).

## Where things are

| Topic | Page |
|---|---|
| Design principles, behaviour, presets | [DESIGN.md](DESIGN.md) |
| Window layout, strip and controls | [UI_LAYOUT.md](UI_LAYOUT.md) |
| Processing flow and background jobs | [ARCHITECTURE.md](ARCHITECTURE.md), [FILTER_LIFECYCLE.md](FILTER_LIFECYCLE.md) |
| Compression design | [COMPRESSION.md](COMPRESSION.md) |
| Measured complete-PDF sizes | [COMPRESSION_BENCHMARKS.md](COMPRESSION_BENCHMARKS.md) |
| JPEG and JPEG2000 quality | [LOSSY_IMAGE_QUALITY.md](LOSSY_IMAGE_QUALITY.md) |
| PDF stream compression and reader limits | [NATIVE_STREAM_COMPRESSION.md](NATIVE_STREAM_COMPRESSION.md) |
| JBIG2 BW and Color | [JBIG2.md](JBIG2.md) |
| Proposal, not implemented | [MIXED_MODE_OPTION.md](MIXED_MODE_OPTION.md) |
| Icons and tooltips | [ICONS.md](ICONS.md), [ICON_LAB.md](ICON_LAB.md), [TOOLTIPS.md](TOOLTIPS.md) |
| Settings and temporary files | [PERSISTENCE_AND_TEMP.md](PERSISTENCE_AND_TEMP.md) |
| Certified platform, packaging, dependencies | [PLATFORMS.md](PLATFORMS.md), [PACKAGING.md](PACKAGING.md), [DEPENDENCIES.md](DEPENDENCIES.md) |
| Developer rules and tests | [DEVELOPER_GUIDELINES.md](DEVELOPER_GUIDELINES.md), [TEST_PLAN.md](TEST_PLAN.md) |
| Designer rulings, word for word | [DESIGNER_VERBATIM.md](DESIGNER_VERBATIM.md) |
| Requirements, defects, dropped ideas | [TODO.md](TODO.md), [issues.md](../issues.md), [DROPPED.md](DROPPED.md) |
