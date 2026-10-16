"""Full-color PDF composition before DPI resize/filtering (§§180/182).

Source samples, soft masks, clips and blending are composed by MuPDF first.
Bounded native tiles fill one disk-backed composite, then ONE global resize
avoids tile-dependent resampling coefficients or seams.
"""

import math
import mmap
import tempfile

import fitz
import numpy as np
from PIL import Image

from .pdf_io import CancelledError
from .display import DisplayPage


def _source_dpi(page):
    """Actual maximum sampling density; native matrices accept fractional DPI.

    Ceil-to-integer DPI promotes PDF float round-off near 300 to 301,
    creating a real upscale/downscale even when the source grid is unchanged.
    Keep precision here; MuPDF resolves the final device-pixel bounds.
    """
    masks = {e[0]: e[1] for e in page.get_images(full=True) if e[1]}
    dpi = 72.0
    for info in page.get_image_info(xrefs=True):
        a, b, c, d, _, _ = info["transform"]
        width, height = info["width"], info["height"]
        mask = masks.get(info["xref"])
        if mask:
            width = max(width, int(page.parent.xref_get_key(mask, "Width")[1]))
            height = max(height, int(page.parent.xref_get_key(mask, "Height")[1]))
        for pixels, points in ((width, math.hypot(a, b)), (height, math.hypot(c, d))):
            if points > 0:
                dpi = max(dpi, pixels * 72 / points)
    return dpi


def flatten_rgb(page, dpi, token, resample, *, directory=None, tile_pixels=8_000_000,
                minimum_dpi=72):
    """Composite the original full-color layer, then resize to final DPI.

    No palette/threshold/codec runs until this function has completed; no
    individual image is rewritten. RGBX is opaque RGB with a padding byte,
    allowing Pillow to map the complete scratch image without copying it.
    """
    if dpi <= 0:
        raise ValueError("DPI must be positive")
    source_scale = max(_source_dpi(page), minimum_dpi) / 72
    source_matrix = fitz.Matrix(source_scale, source_scale)
    renderer = DisplayPage(page)
    source = (page.rect * source_matrix).irect
    target = (page.rect * fitz.Matrix(dpi / 72, dpi / 72)).irect
    width, height = target.width, target.height
    edge = max(1, min(2048, int(math.sqrt(tile_pixels))))
    inverse = ~source_matrix
    with tempfile.TemporaryFile(prefix="image-composite-", dir=directory) as scratch:
        size = source.width * source.height * 4
        scratch.truncate(size)
        mapped = mmap.mmap(scratch.fileno(), size)
        data, image = None, None
        try:
            data = np.ndarray((source.height, source.width, 4), dtype=np.uint8, buffer=mapped)
            for y in range(0, source.height, edge):
                for x in range(0, source.width, edge):
                    if token.cancelled:
                        raise CancelledError()
                    x2, y2 = min(source.width, x + edge), min(source.height, y + edge)
                    left, top = x + source.x0, y + source.y0
                    clip = fitz.Rect(left, top, x2 + source.x0, y2 + source.y0) * inverse
                    pix = renderer.render(source_matrix, clip)
                    pixels = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                        pix.height, pix.width, 3)
                    ox, oy = left - pix.x, top - pix.y
                    data[y:y2, x:x2, :3] = pixels[oy:oy+y2-y, ox:ox+x2-x]
                    data[y:y2, x:x2, 3] = 255
            if token.cancelled:
                raise CancelledError()
            image = Image.frombuffer("RGBX", (source.width, source.height),
                                     mapped, "raw", "RGBX", 0, 1)
            return resample(image, width, height).convert("RGB")
        finally:
            if image is not None:
                image.close()
            data = None
            mapped.close()
