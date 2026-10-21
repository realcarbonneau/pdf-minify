"""Find the external encoders (jbig2, zopfli): the app's own copy first.

The Windows and macOS builds carry them in a `bin` folder next to the
`pdf_minify` package. Linux packages and source checkouts use the system's,
found on PATH. Callers run the returned path, so detection and execution
always use the same program.
"""
import shutil
from pathlib import Path

BUNDLED_BIN = Path(__file__).resolve().parents[2] / "bin"


def find_tool(name: str) -> str | None:
    """Full path of `name` (bundled, else on PATH), or None if neither has it."""
    if BUNDLED_BIN.is_dir():
        bundled = shutil.which(name, path=str(BUNDLED_BIN))
        if bundled:
            return bundled
    return shutil.which(name)
