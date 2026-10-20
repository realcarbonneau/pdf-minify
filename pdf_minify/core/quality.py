"""Stable user-facing quality controls (§§262/271/272/284).

One Quality index, 0–100, drives JPEG and lossy JPEG2000. JPEG passes it to
libjpeg. JPEG2000 maps it to one fixed OpenJPEG target, calibrated so the
same number looks like JPEG at that number on the benchmark pages (§284),
using standard packages only (§278). See docs/LOSSY_IMAGE_QUALITY.md.
"""

import math
from numbers import Integral

DEFAULT_LOSSY_QUALITY = 75
JPX_QUALITY_MAPPING = "jpeg-matched-tile-psnr-v1"
JPEG_ENCODING_PROFILE = "jpeg444-huffman-v1"
JPX_ENCODING_PROFILE = "jpx97-ict-tile512-v1"   # lossy JPEG2000 at a Quality
JPX_RATE_PROFILE = "jpx97-ict-v1"               # explicit legacy ratios, unchanged
JPX_TILE = 512

# (Quality, JPEG2000 PSNR target per 512-pixel tile in dB). At each anchor the
# median SSIMULACRA2 of JPEG2000 equals JPEG at the same Quality over the 67
# benchmark page images (measured 2026-10-20). Straight lines join the anchors
# and continue beyond q50 and q90, within JPX_PSNR_LIMITS.
JPX_PSNR_ANCHORS = ((50, 39.5), (60, 40.5), (75, 44.0), (90, 50.5))
JPX_PSNR_LIMITS = (20.0, 70.0)


def checked_quality(value):
    """Quality is an integer index, not a ratio, PSNR or percentage."""
    if isinstance(value, bool) or not isinstance(value, Integral) or not 0 <= value <= 100:
        raise ValueError("Image quality must be an integer from 0 to 100")
    return int(value)


def jpx_quality_psnr(quality):
    """Per-tile PSNR target (dB) for a JPEG2000 Quality; same for every image.

    Never derived from a reference JPEG, the image content or its size.
    Explicit historical ratios and Lossless bypass this quality control.
    """
    q = checked_quality(quality)
    points = JPX_PSNR_ANCHORS
    if q <= points[1][0]:
        (q0, d0), (q1, d1) = points[0], points[1]
    elif q >= points[-2][0]:
        (q0, d0), (q1, d1) = points[-2], points[-1]
    else:
        (q0, d0), (q1, d1) = next((a, b) for a, b in zip(points, points[1:]) if a[0] <= q <= b[0])
    target = d0 + (q - q0) * (d1 - d0) / (q1 - q0)
    low, high = JPX_PSNR_LIMITS
    return round(min(max(target, low), high), 2)


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
