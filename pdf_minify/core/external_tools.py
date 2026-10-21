"""Find the external encoders (jbig2, zopfli): the app's own copy first.

The Windows and macOS builds carry them in a `bin` folder next to the
`pdf_minify` package. Linux packages and source checkouts use the system's,
found on PATH. Callers run the returned path, so detection and execution
always use the same program.
"""
import os
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


def tool_path(path) -> str:
    r"""A file path to give an external tool, which it can open on any platform.

    On Windows, a program opens paths longer than 260 characters only in the
    \\?\ form; the app's encoder scratch files sit deep in its temporary
    folder (saves/<PID>/<filter>/<hash>/...), past that limit for a long user
    name or test folder. Python itself has no such limit.
    """
    path = os.path.abspath(path)
    if os.name == "nt" and len(path) >= 240 and not path.startswith("\\\\?\\"):
        return "\\\\?\\" + path
    return path


def short_scratch_dir(directory):
    r"""`directory`, or None (the system temp folder) where its files' paths reach 260 characters.

    For a tool that cannot open the \\?\ form either: jbig2 opens its input
    through Leptonica, which turns every \ into / on Windows. A file named
    with up to 40 characters in the folder returned stays under the limit.
    """
    if os.name == "nt" and directory and len(os.path.abspath(directory)) + 41 >= 260:
        return None
    return directory
