# DROPPED — ideas intentionally not pursued (historical reference)

Rule: an idea lands here only by designer ruling, with reason + date + source
request number. Check here before re-proposing anything. Revisit only if the
stated reason expires. Knowledge is referenced, never redone.

## D1 — JPEG XL embedded inside PDFs — DROPPED 2026-10-09 (request §5)
Reason: JXL is not part of ISO 32000, so no PDF viewer renders JXL image
streams — shipping it would produce unopenable files. The PDF Association
(Sep 2025) named JXL the future preferred HDR format with no timeline.
Revisit if: ISO 32000 adopts JXL AND Evince/MuPDF/Chromium render it.
See: `PDF_OPTIMIZATION_NOTES.md`, `DESIGNER_VERBATIM.md` §5.

## D2 — Tkinter-first GUI staging — SUPERSEDED 2026-10-09 (requests §6–§8)
Reason: the original plan was Tkinter for v0.1, Qt for v0.2. The designer's
§6 picky-UI ruling (smooth custom pan/zoom/DnD) disqualified the Tk Canvas,
so PySide6 was built directly and there is no Tk code. Note: `ARCHITECTURE.md`
still describes the old Tk-first staging — treat Qt as locked.
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
Historical benchmark controls/results are retained; this ruling does not
delete working code or establish universal dominance of one image codec.
Revisit if: the designer explicitly introduces an encoding-cost constraint,
or an alternative demonstrates a genuine size or reader-support advantage.
See: `DESIGN.md`, `COMPRESSION_COMBINATIONS.md`, TODO §217 (integration pending).
