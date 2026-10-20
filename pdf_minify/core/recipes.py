"""Effective filter recipes (§149). Identity excludes names and view state."""

from .pipeline import DEFAULT_DPI, DEFAULT_PAGE_SIZE
from .algorithms import BW_MODES, COLOR_MODES, PALETTE_MODES
from .stream_compression import permits_brotli
from .predictors import effective_prediction
from .quality import (DEFAULT_LOSSY_QUALITY, JPEG_ENCODING_PROFILE, JPX_ENCODING_PROFILE,
                      JPX_RATE_PROFILE,
                      JPX_QUALITY_MAPPING, checked_quality, jpx_lossy_setting)


def preset_spec(preset: dict) -> dict:
    prm = preset.get("params", {})
    mode = preset["mode"]
    spec = {"mode": mode, "stream_compression": prm.get("stream_compression", "flate"),
            "png_prediction": prm.get("png_prediction", "off"),
            "brotli_declaration": bool(prm.get("brotli_declaration", False))}
    if mode in BW_MODES:
        spec.update(strategy=prm.get("strategy", "otsu"), t=int(prm.get("t", 180)),
                    dpi=int(prm.get("dpi", DEFAULT_DPI)),
                    force_raster=bool(prm.get("force_raster", False)),
                    page_size=prm.get("page_size", DEFAULT_PAGE_SIZE))
    elif mode in COLOR_MODES:
        spec.update(dpi_cap=int(prm.get("dpi_cap", DEFAULT_DPI)),
                    force_raster=bool(prm.get("force_raster", False)),
                    page_size=prm.get("page_size", DEFAULT_PAGE_SIZE))
        if mode == "color":
            spec["jpeg_q"] = checked_quality(prm.get("jpeg_q", DEFAULT_LOSSY_QUALITY))
        elif mode == "jpx":
            spec["lossless"] = bool(prm.get("lossless", False))
            # A saved q field wins only when rate is absent; explicit old
            # ratio recipes remain reproducible, never silently relabeled.
            if prm.get("jpx_q") is not None or prm.get("rate") is None:
                spec["jpx_q"] = prm.get("jpx_q", DEFAULT_LOSSY_QUALITY)
            if prm.get("rate") is not None:
                spec["rate"] = prm["rate"]
            jpx_lossy_setting(spec)  # fail ambiguous active recipes early
        else:
            spec["colors"] = int(prm.get("colors", 5 if mode == "layered-jbig2" else 64))
    return spec


def spec_key(spec: dict) -> tuple:
    """Every effective saver input, no disabled controls or filter identity.

    An automatic strategy ignores T; unforced BW ignores page reshaping;
    lossless JPEG2000 ignores its lossy quality/rate. Equivalent copies share results.
    """
    policy = spec.get("stream_compression", "flate")
    return (*_image_spec_key(spec), policy,
            bool(spec.get("brotli_declaration", False)) if permits_brotli(policy) else False,
            effective_prediction(spec))


def _image_spec_key(spec):
    mode = spec["mode"]
    force = bool(spec.get("force_raster", False))
    raster = (force, spec.get("page_size", DEFAULT_PAGE_SIZE) if force else None)
    if mode in BW_MODES:
        strategy = spec.get("strategy", "otsu")
        force = bool(spec.get("force_raster", False))
        return (mode, int(spec.get("dpi", DEFAULT_DPI)), strategy,
                int(spec.get("t", 180)) if strategy == "simple" else None,
                force, spec.get("page_size", DEFAULT_PAGE_SIZE) if force else None)
    if mode == "color":
        return (mode, int(spec.get("dpi_cap", DEFAULT_DPI)),
                checked_quality(spec.get("jpeg_q", DEFAULT_LOSSY_QUALITY)),
                JPEG_ENCODING_PROFILE, *raster)
    if mode == "jpx":
        setting, value = jpx_lossy_setting(spec)
        quality_key = ((setting, value, JPX_QUALITY_MAPPING)
                       if setting == "quality" else (setting, value))
        profile = {"lossless": "jpx-rgb53-lossless-v1", "rate": JPX_RATE_PROFILE}.get(
            setting, JPX_ENCODING_PROFILE)
        return (mode, int(spec.get("dpi_cap", DEFAULT_DPI)), quality_key, profile, *raster)
    if mode in PALETTE_MODES:
        return (mode, int(spec.get("dpi_cap", DEFAULT_DPI)),
                int(spec.get("colors", 5 if mode == "layered-jbig2" else 64)), *raster)
    if mode == "passthrough":
        return (mode,)
    raise ValueError(f"Unknown filter mode: {mode}")


def recipe_params(preset: dict, spec: dict) -> dict:
    """Keep non-editable metadata while committing the effective recipe."""
    params = dict(preset.get("params", {}))
    params.update({k: v for k, v in spec.items() if k not in ("mode", "preset_id")})
    return params
