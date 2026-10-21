"""PDF Minify launcher for Windows: Start menu, desktop icon and "Open with".

Runs under pythonw.exe (no console window), so the log goes to
%TEMP%\\pdf-minify\\pdf-minify.log, the folder run.sh uses on Linux.
"""
import os
import sys
import tempfile

APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

if sys.stdout is None or sys.stderr is None:
    if __name__ == "__main__":
        log_dir = os.path.join(tempfile.gettempdir(), "pdf-minify")
        os.makedirs(log_dir, exist_ok=True)
        log = open(os.path.join(log_dir, "pdf-minify.log"), "w", encoding="utf-8", buffering=1)
    else:
        # A multiprocessing worker, which starts this file too: no log of its own.
        log = open(os.devnull, "w", encoding="utf-8")
    sys.stdout = sys.stdout or log
    sys.stderr = sys.stderr or log

from pdf_minify.__main__ import cli  # noqa: E402

if __name__ == "__main__":
    cli()
