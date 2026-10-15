"""Effective filter recipes (§149). Identity excludes names and view state."""

from .pipeline import DEFAULT_DPI, DEFAULT_PAGE_SIZE
from .algorithms import BW_MODES, COLOR_MODES, PALETTE_MODES


def preset_spec(preset: dict) -> dict:
    prm = preset.get("params", {})
    mode = preset["mode"]
    spec = {"mode": mode, "stream_compression": prm.get("stream_compression", "flate")}
    if mode in BW_MODES:
        spec.update(strategy=prm.get("strategy", "otsu"), t=int(prm.get("t", 180)),
                    dpi=int(prm.get("dpi", DEFAULT_DPI)),
                    force_raster=bool(prm.get("force_raster", False)),
                    page_size=prm.get("page_size", DEFAULT_PAGE_SIZE))
    elif mode in COLOR_MODES:
        spec["dpi_cap"] = int(prm.get("dpi_cap", 150))
        if mode == "color":
            spec["jpeg_q"] = int(prm.get("jpeg_q", 50))
        elif mode == "jpx":
            spec.update(rate=int(prm.get("rate", 192)),
                        lossless=bool(prm.get("lossless", False)))
        else:
            spec["colors"] = int(prm.get("colors", 5 if mode == "layered-jbig2" else 64))
    return spec


def spec_key(spec: dict) -> tuple:
    """Every effective saver input, no disabled controls or filter identity.

    An automatic strategy ignores T; unforced BW ignores page reshaping;
    lossless JPEG2000 ignores its lossy rate. Equivalent copies share results.
    """
    return (*_image_spec_key(spec), spec.get("stream_compression", "flate"))


def _image_spec_key(spec):
    mode = spec["mode"]
    if mode in BW_MODES:
        strategy = spec.get("strategy", "otsu")
        force = bool(spec.get("force_raster", False))
        return (mode, int(spec.get("dpi", DEFAULT_DPI)), strategy,
                int(spec.get("t", 180)) if strategy == "simple" else None,
                force, spec.get("page_size", DEFAULT_PAGE_SIZE) if force else None)
    if mode == "color":
        return (mode, int(spec.get("dpi_cap", 150)), int(spec.get("jpeg_q", 50)))
    if mode == "jpx":
        lossless = bool(spec.get("lossless", False))
        return (mode, int(spec.get("dpi_cap", 150)), lossless,
                None if lossless else int(spec.get("rate", 192)))
    if mode in PALETTE_MODES:
        return (mode, int(spec.get("dpi_cap", 150)),
                int(spec.get("colors", 5 if mode == "layered-jbig2" else 64)))
    if mode == "passthrough":
        return (mode,)
    raise ValueError(f"Unknown filter mode: {mode}")


def recipe_params(preset: dict, spec: dict) -> dict:
    """Keep non-editable metadata while committing the effective recipe."""
    params = dict(preset.get("params", {}))
    params.update({k: v for k, v in spec.items() if k not in ("mode", "preset_id")})
    return params
