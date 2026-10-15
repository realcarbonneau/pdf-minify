"""Editable compression choices, independent of a filter's name/UUID (§203)."""

ALGORITHMS = (
    ("bw", "JBIG2 BW"),
    ("layered-jbig2", "JBIG2 Color"),
    ("bw-flate", "Flate BW"),
    ("indexed", "Flate Color (palette)"),
    ("jpx", "JPEG2000"),
    ("color", "JPEG"),
)
ALGORITHM_LABELS = dict(ALGORITHMS)
BW_MODES = frozenset(("bw", "bw-flate"))
PALETTE_MODES = frozenset(("indexed", "layered-jbig2"))
COLOR_MODES = frozenset(("color", "jpx", *PALETTE_MODES))


def with_algorithm(spec: dict, mode: str) -> dict:
    """Change codec without changing DPI or forgetting inactive parameters.

    Irrelevant retained values do not enter effective cache identity. Switching
    back can therefore restore the saved recipe without work or false dirtiness.
    Existing mode IDs remain compatible with previously saved filters.
    """
    if mode not in ALGORITHM_LABELS:
        raise ValueError(f"Unknown compression algorithm: {mode}")
    result = dict(spec, mode=mode)
    dpi_field = "dpi" if spec.get("mode") in BW_MODES else "dpi_cap"
    dpi = int(spec.get(dpi_field, 300 if mode in BW_MODES else 150))
    if mode in BW_MODES:
        result.update(dpi=dpi)
        result.setdefault("strategy", "otsu")
        result.setdefault("t", 180)
        result.setdefault("force_raster", False)
        result.setdefault("page_size", "original")
    else:
        result["dpi_cap"] = dpi
        if mode in PALETTE_MODES:
            result.setdefault("colors", 5 if mode == "layered-jbig2" else 64)
        elif mode == "jpx":
            result.setdefault("rate", 192)
            result.setdefault("lossless", False)
        elif mode == "color":
            result.setdefault("jpeg_q", 50)
    return result
