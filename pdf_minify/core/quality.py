"""Shared quality and study-informed JPX ratios (§267), not quality guarantees."""

import math
from numbers import Integral

DEFAULT_LOSSY_QUALITY = 75
JPX_QUALITY_MAPPING = "jpeg-reference-study-v1"
JPEG_ENCODING_PROFILE = "jpeg444-huffman-v1"
JPX_ENCODING_PROFILE = "jpx97-ict-v1"


def checked_quality(value):
    """Quality is an integer index, not a ratio, PSNR or percentage."""
    if isinstance(value, bool) or not isinstance(value, Integral) or not 0 <= value <= 100:
        raise ValueError("Image quality must be an integer from 0 to 100")
    return int(value)


def jpx_reference_rate(raw_bytes, jpeg_bytes):
    """Map a measured JPEG ratio using §267's approximate 40→45 / 60→73.

    Byte counts describe the SAME prepared raster and reference JPEG, not
    complete PDFs. Interpolate between study anchors; outside, retain the
    nearest relative gain (an explicit heuristic, NOT proven equivalence).
    Small/header-heavy images can have a ratio below 1; OpenJPEG needs >=1.
    """
    for size in (raw_bytes, jpeg_bytes):
        if isinstance(size, bool) or not isinstance(size, Integral) or size <= 0:
            raise ValueError("Reference byte counts must be positive integers")
    ratio = raw_bytes / jpeg_bytes
    if ratio <= 40:
        target = ratio * (45 / 40)
    elif ratio >= 60:
        target = ratio * (73 / 60)
    else:
        target = 45 + (ratio - 40) * (28 / 20)
    return max(1.0, target)


def jpx_lossy_setting(params):
    """Resolve q versus explicit legacy r without reinterpreting old recipes.

    Lossless ignores either inactive lossy field (including invalid values).
    The returned tag is part of effective identity; q75 and r75 differ.
    """
    if params.get("lossless", False):
        return "lossless", None
    quality, rate = params.get("jpx_q"), params.get("rate")
    if quality is not None and rate is not None:
        raise ValueError("Choose JPEG2000 quality or a legacy rate, not both")
    if rate is not None:
        try:
            numeric_rate = float(rate)
        except (TypeError, ValueError):
            raise ValueError("JPEG2000 rate must be a finite ratio of at least 1") from None
        if isinstance(rate, bool) or not math.isfinite(numeric_rate) or numeric_rate < 1:
            raise ValueError("JPEG2000 rate must be a finite ratio of at least 1")
        return "rate", rate if isinstance(rate, Integral) else numeric_rate
    return "quality", checked_quality(DEFAULT_LOSSY_QUALITY if quality is None else quality)
