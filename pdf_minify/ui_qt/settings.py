"""PDF Minify settings, with a one-time non-destructive name migration (§230)."""

from PySide6.QtCore import QSettings

from .. import APP_ID, APP_NAME

LEGACY_APP_ID = "pdf-minimalist"
IDENTITY_MIGRATION_KEY = "identityMigrationRevision"
IDENTITY_MIGRATION_REVISION = 1


def configure_application(app):
    """Use a stable machine identity separately from the human-facing name."""
    from .icons import app_icon
    app.setOrganizationName(APP_ID)
    app.setApplicationName(APP_ID)
    app.setApplicationDisplayName(APP_NAME)
    app.setWindowIcon(app_icon())


def _user_settings(app_id):
    store = QSettings(QSettings.NativeFormat, QSettings.UserScope, app_id, app_id)
    # Import only this application's user values, not organization/system
    # fallbacks. Explicit namespaces also work before QApplication exists.
    store.setFallbacksEnabled(False)
    store.sync()
    _check_status(store)
    return store


def _check_status(store):
    if store.status() != QSettings.NoError:
        raise OSError(f"Cannot synchronize {APP_NAME} settings: {store.fileName()}")


def sync_settings(store):
    """Persist a settings transaction without hiding a failed migration write."""
    store.sync()
    _check_status(store)


def _migrated(store):
    try:
        return int(store.value(IDENTITY_MIGRATION_KEY, 0) or 0) >= IDENTITY_MIGRATION_REVISION
    except (TypeError, ValueError):
        return False


def settings_snapshot():
    """Read effective preferences without migrating or writing either store.

    Screenshot/review tools copy this snapshot into an isolated namespace
    before constructing a window. They must not migrate the real user store.
    """
    current = _user_settings(APP_ID)
    values = {} if _migrated(current) else {
        key: value for key, value in _items(_user_settings(LEGACY_APP_ID))
        if key != IDENTITY_MIGRATION_KEY
    }
    values.update(_items(current))
    return values


def _items(store):
    return ((key, store.value(key)) for key in store.allKeys())


def app_settings():
    """Open the shared store; import missing legacy values only on first use.

    Preserve QVariant types, newer values and the untouched legacy source.
    The persisted marker prevents deleted new values from being resurrected.
    Sync failures propagate rather than claiming a successful migration.
    """
    current = _user_settings(APP_ID)
    if not _migrated(current):
        legacy = _user_settings(LEGACY_APP_ID)
        for key, value in _items(legacy):
            if key != IDENTITY_MIGRATION_KEY and not current.contains(key):
                current.setValue(key, value)
        current.setValue(IDENTITY_MIGRATION_KEY, IDENTITY_MIGRATION_REVISION)
        current.sync()
        _check_status(current)
    return current
