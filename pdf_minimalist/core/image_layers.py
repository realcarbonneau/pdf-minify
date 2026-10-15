"""One transformed image canvas plus native PDF artwork (§§171/180/182).

MuPDF filters original operators, including nested forms: no reconstructed
glyphs, invented text masks, per-image mask-heavy fallback or Qt dependency.
"""
import logging

import fitz
import numpy as np

from .pdf_io import CancelledError
from .canvas import flatten_rgb

m = fitz.mupdf
log = logging.getLogger("pdf_minimalist")
_PATH_PAINT = {m.FZ_CULL_PATH_FILL, m.FZ_CULL_PATH_STROKE,
               m.FZ_CULL_PATH_FILL_STROKE}
_CLIP_PAINT = {m.FZ_CULL_CLIP_PATH_FILL, m.FZ_CULL_CLIP_PATH_STROKE,
               m.FZ_CULL_CLIP_PATH_FILL_STROKE}
_PAINT = _PATH_PAINT | {m.FZ_CULL_GLYPH, m.FZ_CULL_IMAGE, m.FZ_CULL_SHADING}


def _check_cancel(token):
    if token.cancelled:
        raise CancelledError()


def _page_backdrops(page):
    """Actual flat opaque page-covering rectangles, never glyph bboxes."""
    backdrops = []
    for drawing in page.get_drawings():
        items = drawing["items"]
        if (drawing["fill"] is not None and drawing["fill_opacity"] == 1
                and len(items) == 1 and items[0][0] == "re"
                and drawing["rect"].contains(page.rect)):
            backdrops.append(drawing["rect"])
    return backdrops


class _Selector(m.PdfSanitizeFilterOptions2):
    def __init__(self, page, token, layer, backdrops):
        super().__init__()
        self.token, self.layer = token, layer
        self.page_matrix = page.transformation_matrix
        self.backdrops = backdrops
        self.clip_only_text = False
        self.kept = 0
        self.use_virtual_culler()
        self.use_virtual_text_filter()

    def text_filter(self, ctx, ucs, length, trm, ctm, bbox, render, ca, CA):
        self.clip_only_text = render == 7
        return 0

    def culler(self, ctx, bbox, kind):
        _check_cancel(self.token)
        if kind not in _PAINT and kind not in _CLIP_PAINT:
            return 0  # native clipping/graphics-state operators, not painting
        if self.layer == "all":
            return 0
        if kind == m.FZ_CULL_GLYPH and self.layer in ("images", "canvas") and self.clip_only_text:
            return 0  # actual PDF clip-only text: no text paint or invented mask
        if kind == m.FZ_CULL_IMAGE:
            layer = "images"
        else:
            rect = fitz.Rect(bbox.x0, bbox.y0, bbox.x1, bbox.y1) * self.page_matrix
            background = (kind in _PATH_PAINT and any(
                max(abs(a - b) for a, b in zip(rect, backdrop)) < .01
                for backdrop in self.backdrops))
            layer = "background" if background else "foreground"
        keep = layer == self.layer or (self.layer == "canvas" and layer in ("images", "background"))
        if keep:
            self.kept += 1
        return int(not keep)

class _Factory(m.PdfFilterFactory2):
    def __init__(self, selector):
        super().__init__()
        self.selector = selector  # strong ownership throughout nested callbacks
        self.use_virtual_filter()

    def filter(self, ctx, doc, chain, struct_parents, transform, options):
        return m.ll_pdf_new_sanitize_filter(doc, chain, struct_parents, transform,
                                           options, self.selector.internal())


def _filter(page, token, layer, *, backdrops=()):
    selector = _Selector(page, token, layer, backdrops)
    factory = _Factory(selector)
    options = m.PdfFilterOptions()
    options.instance_forms = 1
    options.add_factory(factory.internal())
    native_doc = m.pdf_document_from_fz_document(page.parent.this)
    native_page = (page.this if isinstance(page.this, m.PdfPage)
                   else m.pdf_page_from_fz_page(page.this))
    m.pdf_filter_page_contents(native_doc, native_page, options)
    return selector.kept


def _copy_page(source, pno):
    doc = fitz.open()
    doc.insert_pdf(source, from_page=pno, to_page=pno, links=False, annots=False)
    doc[0].set_rotation(0)
    return doc


def compose_page_images(doc, pno, strategy, threshold, dpi, token, encode, place,
                        resample, *, directory=None):
    """Replace bitmap artwork with ONE BW canvas; preserve native overlays.

    The caller owns the one real saver; encode/place/resample are its shared
    implementations, not alternative preview or compression pipelines.
    """
    def paint(out, page, rgb):
        gray = np.asarray(rgb.convert("L"))
        payload, codec = encode(gray, strategy, threshold)
        _check_cancel(token)
        place(out, page, page.rect, payload, codec, rgb.width, rgb.height)
    result = _compose_page(doc, pno, dpi, token, paint, resample,
                           "images", directory)
    if result:
        log.info("page %d: one BW image canvas, original text/vectors overlaid", pno + 1)
    return result


def _assemble_layers(doc, pno, prepared, token, canvas_layer, paint_canvas):
    """One shared original-native + composite-canvas PDF assembly path."""
    backdrops = _page_backdrops(prepared[0])
    page = doc[pno]
    rotation = page.rotation
    page.set_rotation(0)
    empty = doc.get_new_xref()
    doc.update_object(empty, "<<>>")
    doc.update_stream(empty, b"")
    page.set_contents(empty)
    try:
        for layer in ("background", canvas_layer, "foreground"):
            _check_cancel(token)
            with _copy_page(prepared, 0) as fragment:
                kept = _filter(fragment[0], token, layer, backdrops=backdrops)
                if not kept and layer != canvas_layer:
                    continue
                if layer == canvas_layer:
                    paint_canvas(doc, page, fragment[0])
                else:
                    page.show_pdf_page(page.rect, fragment, 0, keep_proportion=False)
        page.clean_contents()  # prune original image/mask resources
    finally:
        page.set_rotation(rotation)


def compose_color_page(doc, pno, dpi, token, encode, place, resample, *, directory=None):
    """Flatten full color first, resize once, then codec/palette transform.

    Native text/vector overlays follow §170/171. Original flat page backdrops
    participate in color composition, so opacity sees the actual page color.
    """
    def paint(out, page, rgb):
        payload = encode(rgb)
        _check_cancel(token)
        place(out, page, page.rect, payload)
    result = _compose_page(doc, pno, dpi, token, paint, resample,
                           "canvas", directory)
    if result:
        log.info("page %d: one color canvas, native text/vectors overlaid", pno + 1)
    return result


def _compose_page(doc, pno, dpi, token, paint, resample, canvas_layer, directory):
    """Shared compose-first RGB preparation; codec adapters run only afterward."""
    _check_cancel(token)
    with _copy_page(doc, pno) as prepared:
        if not prepared[0].get_image_info():
            return 0
        def canvas(out, page, fragment):
            rgb = flatten_rgb(fragment, dpi, token, resample, directory=directory)
            _check_cancel(token)
            paint(out, page, rgb)
        _assemble_layers(doc, pno, prepared, token, canvas_layer, canvas)
        return 1
