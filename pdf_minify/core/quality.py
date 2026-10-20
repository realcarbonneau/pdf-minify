"""Stable user-facing quality controls (§271), not quality guarantees."""

import math
from numbers import Integral

DEFAULT_LOSSY_QUALITY = 75
JPX_QUALITY_MAPPING = "darktable-rate-v2"
JPEG_ENCODING_PROFILE = "jpeg444-huffman-v1"
JPX_ENCODING_PROFILE = "jpx97-ict-v1"


def checked_quality(value):
    """Quality is an integer index, not a ratio, PSNR or percentage."""
    if isinstance(value, bool) or not isinstance(value, Integral) or not 0 <= value <= 100:
        raise ValueError("Image quality must be an integer from 0 to 100")
    return int(value)


def jpx_quality_rate(quality):
    """Fixed conventional scale: q75 always targets 26:1 on every input.

    Never derive this value from JPEG bytes, source complexity or PSNR.
    Explicit historical ratios and Lossless bypass this quality control.
    """
    return 101 - checked_quality(quality)


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
