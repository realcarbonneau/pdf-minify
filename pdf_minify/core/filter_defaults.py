"""Versioned saved-recipe default migration (designer §226), without Qt."""

from .algorithms import BW_MODES, COLOR_MODES
from .defaults import DEFAULT_DPI

RASTER_DEFAULTS_REVISION = 1


def migrate_raster_dpi(filters):
    """Apply the authorized 300-DPI migration, preserving every other field.

    The settings owner gates this ONCE by revision. Later explicit choices
    remain user choices; this function is not a permanent DPI clamp.
    """
    changed = []
    for preset in filters:
        mode = preset.get("mode")
        if mode not in BW_MODES | COLOR_MODES:
            continue
        before = preset.get("params", {})
        params = dict(before)
        field = "dpi" if mode in BW_MODES else "dpi_cap"
        keys = {field} | (params.keys() & {"dpi", "dpi_cap"})
        for key in keys:
            params[key] = DEFAULT_DPI
        if params != before:
            preset["params"] = params
            changed.append(preset["id"])
    return changed
