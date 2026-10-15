"""Read-only PDF display (§§172–175), separate from filter rasterization.

Native geometry is drawn at the requested device resolution. Bitmap samples
are never interpolated or decoder-averaged; there is no display threshold.
Actual PDF color management, compositing and encoded opacity still apply.
"""

import pymupdf as fitz

from .pdf_io import FITZ_LOCK


class DisplayPage:
    """An immutable page display list, with the PDF's own color/spot policy."""

    def __init__(self, page):
        with FITZ_LOCK:
            self.rect = fitz.Rect(page.rect)
            self.display_list = page.get_displaylist(annots=True)
            m = fitz.mupdf
            doc = m.FzDocument(page.parent.this)
            intent = m.fz_document_output_intent(doc)
            self.colorspace = fitz.csRGB.this
            if intent.m_internal and m.fz_colorspace_n(intent) == 3:
                self.colorspace = intent
            self.separations = m.fz_page_separations(page.this)
            if self.separations.m_internal:
                for i in range(m.fz_count_separations(self.separations)):
                    m.fz_set_separation_behavior(
                        self.separations, i, m.FZ_SEPARATION_COMPOSITE)
            elif m.fz_page_uses_overprint(page.this) or (
                    intent.m_internal and m.fz_colorspace_n(intent) != 3):
                self.separations = m.fz_new_separations(0)
            # Keep NULL separations for ordinary RGB/BW pages. An unnecessary
            # overprint simulation would color-convert literal black pixels.

    def render(self, matrix=None, clip=None):
        """RGB readback of just `clip`, with its integer device-pixel origin.

        The application owns MuPDF's image-rendering policy (normally BALANCE).
        Its public tuning setter has no getter; restore that normal policy,
        and restore independently captured text/graphics AA, even on failure.
        The full-color canvas compositor also uses this exact source sampler
        in its worker process, then performs its ONE explicit Lanczos resize.
        Scoped policy restoration keeps other filter renderers unchanged.
        """
        matrix = fitz.Matrix(matrix) if matrix is not None else fitz.Matrix(1, 1)
        rect = self.rect if clip is None else self.rect & fitz.Rect(clip)
        if rect.is_empty or rect.is_infinite:
            raise ValueError("Display clip must intersect the page")
        bbox = (rect * matrix).irect
        m = fitz.mupdf
        with FITZ_LOCK:
            aa = fitz.TOOLS.show_aa_level()
            m.fz_tune_image_rendering(m.FZ_IMAGE_RENDERING_QUALITY)
            fitz.TOOLS.set_aa_level(0)
            try:
                pix = m.fz_new_pixmap_with_bbox(
                    self.colorspace, m.FzIrect(*bbox), self.separations, 0)
                m.fz_clear_pixmap_with_value(pix, 255)
                dev = m.fz_new_draw_device(m.FzMatrix(*matrix), pix)
                m.fz_enable_device_hints(dev, m.FZ_DONT_INTERPOLATE_IMAGES)
                m.fz_run_display_list(self.display_list.this, dev, m.FzMatrix(),
                                      m.FzRect(*rect), m.FzCookie())
                m.fz_close_device(dev)
                return fitz.Pixmap("raw", pix)
            finally:
                m.fz_set_graphics_aa_level(aa["graphics"])
                m.fz_set_text_aa_level(aa["text"])
                m.fz_tune_image_rendering(m.FZ_IMAGE_RENDERING_BALANCE)


def render_display_page(page, dpi=150):
    """Prepared view pixels from the same exact renderer used by both panes."""
    return DisplayPage(page).render(fitz.Matrix(dpi / 72, dpi / 72))
