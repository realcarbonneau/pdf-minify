"""Exact colored JBIG2 stencils shared by production and benchmark (§203)."""

from dataclasses import dataclass

import numpy as np
import pymupdf as fitz

from . import pipeline
from .cancel import CancelToken
from .display import DisplayPage
from .pdf_io import CancelledError


def check_cancel(token):
    if token.cancelled:
        raise CancelledError()


@dataclass(frozen=True)
class PaletteCanvas:
    indices: np.ndarray
    palette: np.ndarray

    @classmethod
    def from_rgb(cls, image, colors):
        quantized = pipeline._quantize_palette(image, colors)
        used, inverse = np.unique(np.asarray(quantized), return_inverse=True)
        palette = np.asarray(quantized.getpalette(), dtype=np.uint8).reshape(-1, 3)[used]
        indices = inverse.reshape(quantized.height, quantized.width).astype(np.uint8)
        return cls(indices, palette)

    @property
    def width(self):
        return self.indices.shape[1]

    @property
    def height(self):
        return self.indices.shape[0]

    @property
    def rgb(self):
        return self.palette[self.indices]

    @property
    def nonwhite_colors(self):
        return sum(not np.all(color == 255) for color in self.palette)


def encode_mask(mask):
    return pipeline.encode_binary_jbig2(mask)


def stencil_pdf(canvas, token=None, *, page_size=None, mask_encoder=None):
    """One opaque canvas, one validated lossless JBIG2 stencil per color.

    mask_encoder is a diagnostic/test seam; the product and study use the SAME
    shared encoder and renderer. No codec fallback or lossy symbol substitution.
    """
    token = token or CancelToken()
    mask_encoder = mask_encoder or encode_mask
    check_cancel(token)
    if canvas.nonwhite_colors and pipeline.jbig2_binary() is None:
        raise RuntimeError("JBIG2 Color unavailable: install jbig2 or choose Flate Color (palette).")
    doc = fitz.open()
    try:
        width, height = page_size or (canvas.width, canvas.height)
        page = doc.new_page(width=width, height=height)
        resources = []
        commands = [f"q 1 1 1 rg 0 0 {width} {height} re f Q"]
        for index, color in enumerate(canvas.palette):
            check_cancel(token)
            if np.all(color == 255):
                continue
            mask = np.where(canvas.indices == index, 0, 255).astype(np.uint8)
            payload = mask_encoder(mask)
            check_cancel(token)
            if payload is None or not pipeline.jbig2_renders(
                    payload, canvas.width, canvas.height, mask):
                raise RuntimeError("JBIG2 Color failed: mask did not decode pixel-exact.")
            xref = doc.get_new_xref()
            doc.update_object(xref, f"<< /Type /XObject /Subtype /Image "
                              f"/Width {canvas.width} /Height {canvas.height} "
                              "/ImageMask true /BitsPerComponent 1 "
                              "/Interpolate false /Decode [0 1] >>")
            doc.update_stream(xref, payload, compress=False)
            doc.xref_set_key(xref, "Filter", "/JBIG2Decode")
            resources.append(f"/C{index} {xref} 0 R")
            commands.append(f"q /Palette cs {index} scn "
                            f"{width} 0 0 {height} 0 0 cm /C{index} Do Q")
        doc.xref_set_key(page.xref, "Resources", "<< /XObject << " + " ".join(resources) +
                         f" >> /ColorSpace << /Palette [/Indexed /DeviceRGB {len(canvas.palette)-1} "
                         f"<{canvas.palette.tobytes().hex()}>] >> >>")
        content = doc.get_new_xref()
        doc.update_object(content, "<< >>")
        doc.update_stream(content, "\n".join(commands).encode("ascii"))
        page.set_contents(content)
        actual = DisplayPage(page).render(fitz.Matrix(canvas.width/width, canvas.height/height))
        pixels = np.frombuffer(actual.samples, dtype=np.uint8).reshape(actual.height, actual.width, 3)
        if not np.array_equal(pixels, canvas.rgb):
            raise RuntimeError("JBIG2 Color failed: colored canvas did not reconstruct exactly.")
        return doc
    except BaseException:
        doc.close()
        raise
