"""Runtime filesystem locations (designer §123).

Two buckets, never mixed:

- TEMP (disposable): the OS standard temp dir via Qt —
  `QStandardPaths.TempLocation` (`/tmp` on Linux, `GetTempPath` on Windows,
  `$TMPDIR` on macOS). The app must never write scratch into the repo dir.
  Core (`core/`) stays Qt-free, so it takes workdir paths as arguments or
  uses stdlib `tempfile` (which already targets the OS temp dir).
- PERSISTENCE (kept): Qt `QSettings` platform locations (config dir) —
  last file, custom presets. Documented in `docs/PERSISTENCE_AND_TEMP.md`.

Dev-tool artifacts (screenshots, benches, demo PDFs) deliberately stay in
the repo `./.tmp/` — they are review outputs, not app scratch (gitignored).
"""

import os
import time

APP_TAG = "pdf-minimalist"


def app_temp_dir(*parts: str) -> str:
    """`<os-temp>/pdf-minimalist[/...parts]`, created on demand."""
    try:
        from PySide6.QtCore import QStandardPaths
        base = QStandardPaths.writableLocation(QStandardPaths.TempLocation)
    except Exception:  # noqa: BLE001 — Qt unavailable, stdlib fallback
        base = ""
    if not base:
        import tempfile
        base = tempfile.gettempdir()
    path = os.path.join(base, APP_TAG, *parts)
    os.makedirs(path, exist_ok=True)
    return path


def sweep_stale_temps(max_age_hours: int = 48, *, temp_base: str | None = None) -> int:
    """Retire expired disposable data, never a live or fresh temp session.

    QLockFile protects long-running sessions. Fresh session directories are
    untouched even before their owner has acquired its lock. Empty-directory
    cleanup is age-gated, not an unconditional walk of other processes' work.
    """
    try:
        from PySide6.QtCore import QLockFile, QStandardPaths
        base = temp_base or QStandardPaths.writableLocation(QStandardPaths.TempLocation)
    except ImportError:
        QLockFile = None
        base = temp_base or ""
    if not base:
        import tempfile
        base = tempfile.gettempdir()
    root = os.path.join(base, APP_TAG)
    cutoff = time.time() - max_age_hours * 3600
    if not os.path.isdir(root):
        return 0
    removed, protected, expired_dirs, held = 0, set(), set(), []
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            try:
                expired = os.path.getmtime(dirpath) < cutoff
            except OSError:
                dirnames.clear()
                continue
            is_process = (os.path.basename(os.path.dirname(dirpath)) == "saves"
                          and os.path.basename(dirpath).isdecimal())
            legacy_session = os.path.basename(dirpath).startswith("session-")
            if is_process or legacy_session:
                if not expired or QLockFile is None:
                    protected.add(dirpath)
                    dirnames.clear()
                    continue
                lock_name = ".process.lock" if is_process else ".session.lock"
                lock = QLockFile(os.path.join(dirpath, lock_name))
                lock.setStaleLockTime(0)
                if not lock.tryLock(0):
                    protected.add(dirpath)
                    dirnames.clear()
                    continue
                held.append((dirpath, lock))
            if expired:
                expired_dirs.add(dirpath)
            for name in filenames:
                if name in (".process.lock", ".session.lock"):
                    continue
                full = os.path.join(dirpath, name)
                try:
                    if os.path.getmtime(full) < cutoff:
                        os.unlink(full)
                        removed += 1
                except OSError:
                    continue
        # Release acquired inactive-session locks before removing their empty
        # roots. Live session locks are never acquired, removed, or touched.
        for _path, lock in held:
            lock.unlock()
        held.clear()
        for dirpath, _dirnames, _filenames in os.walk(root, topdown=False):
            if dirpath not in expired_dirs:
                continue
            if any(dirpath == p or dirpath.startswith(p + os.sep) for p in protected):
                continue
            try:
                os.rmdir(dirpath)  # succeeds only if actually empty
            except OSError:
                pass
    finally:
        for _path, lock in held:
            lock.unlock()
    return removed
