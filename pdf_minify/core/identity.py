"""Persistent random filter identities, independent of names/order (§155)."""

import uuid


def canonical_uuid(value) -> str | None:
    """Normalize a UUIDv4; malformed/non-random IDs need migration."""
    try:
        parsed = uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError):
        return None
    return str(parsed) if parsed.version == 4 else None


def new_filter_uuid(existing=()) -> str:
    """Use the standard OS-random generator, checking loaded IDs as well."""
    used = {canonical_uuid(value) for value in existing}
    while True:
        candidate = str(uuid.uuid4())
        if candidate not in used:
            return candidate


def repair_filter_uuids(filters: list[dict]) -> bool:
    """Keep the first valid identity; preserve every duplicate as a new filter.

    Reserve later valid IDs too, so generating an ID for an earlier missing
    entry cannot take an existing filter's identity. The caller persists repairs.
    """
    reserved = {canonical_uuid(p.get("uuid")) for p in filters}
    seen, changed = set(), False
    for preset in filters:
        candidate = canonical_uuid(preset.get("uuid"))
        if candidate is None or candidate in seen:
            candidate = new_filter_uuid(reserved | seen)
            reserved.add(candidate)
        if preset.get("uuid") != candidate:
            preset["uuid"] = candidate
            changed = True
        seen.add(candidate)
    return changed
