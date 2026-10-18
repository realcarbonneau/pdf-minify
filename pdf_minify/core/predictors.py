"""Lossless image-row prediction, separate from visual image processing (§260)."""

import numpy as np

from .cancel import CancelToken
from .pdf_io import CancelledError

PREDICTION_CHOICES = (("off", "Off"), ("on", "On"), ("best", "Best"))
PACKED_MODES = frozenset(("bw-flate", "indexed"))


def effective_prediction(spec):
    """Inactive controls do not change jobs or erase the retained choice."""
    if spec["mode"] not in PACKED_MODES and spec["mode"] != "passthrough":
        return None
    policy = spec.get("stream_compression", "flate")
    if policy == "best":
        return "best"
    if policy == "zopfli":
        return spec.get("png_prediction")
    return None


def predict_rows(data, width, height, bpc, colors=1, token=None):
    """Adaptive predictor 15; exact packed bytes, including partial last bytes.

    Choose None/Sub/Up/Average/Paeth by minimum absolute signed-byte sum,
    matching the existing measured single-component benchmark selector.
    """
    if (width <= 0 or height <= 0 or colors <= 0 or bpc not in (1, 2, 4, 8, 16)):
        raise ValueError("Invalid image predictor layout")
    stride = (width * colors * bpc + 7) // 8
    if len(data) != height * stride:
        raise ValueError("Image samples do not match predictor row layout")
    token = token or CancelToken()
    rows = np.frombuffer(data, dtype=np.uint8).reshape(height, stride)
    bpp = max(1, (colors * bpc + 7) // 8)
    output = bytearray()
    previous = np.zeros(stride, dtype=np.int16)
    for row in rows:
        if token.cancelled:
            raise CancelledError()
        current = row.astype(np.int16)
        left = np.zeros(stride, dtype=np.int16)
        upper_left = np.zeros(stride, dtype=np.int16)
        left[bpp:] = current[:-bpp]
        upper_left[bpp:] = previous[:-bpp]
        estimate = left + previous - upper_left
        distance = np.stack((abs(estimate-left), abs(estimate-previous), abs(estimate-upper_left)))
        paeth = np.choose(distance.argmin(axis=0), (left, previous, upper_left))
        predictions = np.stack((np.zeros(stride, dtype=np.int16), left, previous,
                                (left+previous)//2, paeth))
        candidates = (current-predictions).astype(np.uint8)
        signed = candidates.astype(np.int16)
        chosen = int(np.minimum(signed, 256-signed).sum(axis=1).argmin())
        output.append(chosen)
        output.extend(candidates[chosen].tobytes())
        previous = current
    return bytes(output)


def image_layout(doc, xref, decoded_size):
    """Validate known packed layouts; never infer channel count from byte size."""
    import pymupdf as fitz
    m = fitz.mupdf
    native = m.pdf_document_from_fz_document(doc.this)
    image = m.pdf_load_object(native, xref)
    get = lambda key: m.pdf_dict_gets(image, key)
    width, height = m.pdf_to_int(get("Width")), m.pdf_to_int(get("Height"))
    mask = m.pdf_to_bool(get("ImageMask"))
    bpc = 1 if mask else m.pdf_to_int(get("BitsPerComponent"))
    space = get("ColorSpace")
    name = m.pdf_to_name(m.pdf_array_get(space, 0) if m.pdf_is_array(space) else space)
    colors = 1 if mask else {"DeviceGray": 1, "G": 1, "DeviceRGB": 3, "RGB": 3,
                             "DeviceCMYK": 4, "CMYK": 4, "Indexed": 1, "I": 1,
                             "CalGray": 1, "CalRGB": 3, "Lab": 3,
                             "Separation": 1}.get(name)
    if name == "ICCBased":
        colors = m.pdf_to_int(m.pdf_dict_gets(m.pdf_array_get(space, 1), "N"))
    elif name == "DeviceN":
        colors = m.pdf_array_len(m.pdf_array_get(space, 1))
    if (width <= 0 or height <= 0 or not colors or bpc not in (1, 2, 4, 8, 16)
            or decoded_size != height * ((width * colors * bpc + 7) // 8)):
        return None
    return width, height, bpc, colors
