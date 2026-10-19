"""Versioned saved-recipe migrations (designer §§226/257/263/264), without Qt."""

from .algorithms import BW_MODES, COLOR_MODES
from .defaults import DEFAULT_DPI
from .quality import DEFAULT_LOSSY_QUALITY

RASTER_DEFAULTS_REVISION = 1
STREAM_DEFAULTS_REVISION = 1
QUALITY_DEFAULTS_REVISION = 2
DEFAULT_APP_STREAM_POLICY = "best"


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


def migrate_stream_compression(filters):
    """Set every app filter to Best, changing no other setting or identity.

    Built-in seeds use the same rule. The settings owner gates saved-filter
    migration ONCE, so subsequent explicit choices are not clamped on load.
    Original/passthrough is a reference, not an editable app filter.
    """
    changed = []
    for preset in filters:
        if preset.get("mode") not in BW_MODES | COLOR_MODES:
            continue
        before = preset.get("params", {})
        if before.get("stream_compression") == DEFAULT_APP_STREAM_POLICY:
            continue
        preset["params"] = dict(before, stream_compression=DEFAULT_APP_STREAM_POLICY)
        changed.append(preset["id"])
    return changed


def migrate_lossy_quality(filters):
    """Apply the q75 starting point once; preserve Lossless and other fields.

    JPX's old ratio is replaced, not renamed or numerically reinterpreted.
    Settings gate the migration so later deliberate quality edits survive.
    """
    changed = []
    for preset in filters:
        mode = preset.get("mode")
        if mode not in ("color", "jpx"):
            continue
        before = preset.get("params", {})
        params = dict(before)
        params["jpeg_q" if mode == "color" else "jpx_q"] = DEFAULT_LOSSY_QUALITY
        if mode == "jpx":
            params.pop("rate", None)
        if params != before:
            preset["params"] = params
            changed.append(preset["id"])
    return changed
