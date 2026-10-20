# DROPPED — ideas intentionally not pursued (historical reference)

Rule: an idea lands here only by designer ruling, with reason + date + source
request number. Check here before re-proposing anything. Revisit only if the
stated reason expires. Knowledge is referenced, never redone.

## D1 — JPEG XL embedded inside PDFs — DROPPED 2026-10-09 (request §5)
Reason: JXL is not part of ISO 32000, so no PDF viewer renders JXL image
streams — shipping it would produce unopenable files. The PDF Association
(Sep 2025) named JXL the future preferred HDR format with no timeline.
Revisit if: ISO 32000 adopts JXL AND Evince/MuPDF/Chromium render it.
See: `DESIGNER_VERBATIM.md` §5.

## D2 — Tkinter-first GUI staging — SUPERSEDED 2026-10-09 (requests §6–§8)
Reason: the original plan was Tkinter for v0.1, Qt for v0.2. The designer's
§6 picky-UI ruling (smooth custom pan/zoom/DnD) disqualified the Tk Canvas,
so PySide6 was built directly and there is no Tk code.
Revisit if: never expected; kept here so nobody rebuilds the Tk detour.
See: `ARCHITECTURE.md`, `DESIGNER_VERBATIM.md` §6.

## D3 — inferior encoders retained for speed/dependency convenience — SUPERSEDED 2026-10-15 (request §213)
Reason: the designer specifies an opinionated best-compression suite. Encoding
cost is not a constraint; superseded encoders are dropped as product choices.
The old Max/Balanced/Fast brief and worker justification for a separate
ordinary-zlib versus Zopfli speed choice no longer apply. Zopfli uses the SAME
Flate decoder. Avoiding the JBIG2 encoder dependency is likewise not a reason
to keep a dominated image option. Reader support and actual compressed-size
outcomes at the chosen fidelity decide which formats remain useful.
Revisit if: the designer explicitly introduces an encoding-cost constraint,
or an alternative demonstrates a genuine size or reader-support advantage.
See: `COMPRESSION.md` (Encoder policy), TODO §217 (integration pending).

## D4 — corpus audit plan (former TODO 38) — DROPPED 2026-10-20 (request §290)
Reason: TODO 38 came from third-party corpus research pasted on 2026-10-09,
not from a designer requirement: consolidate to about 22 PDFs, add
camera-photographed pages (DocShadow, SmartDoc), DIBCO quantitative tests,
structural classes and an automatic "B&W not recommended" hint. Benchmarks
now use six representative PDFs (§§223/231).
Revisit if: the designer asks for camera-photographed pages or quantitative
binarization tests; open a new, narrow TODO then.
See: `DESIGNER_VERBATIM.md` §290.
