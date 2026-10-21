"""PDF Minify launcher for the macOS app (py2app's main script).

py2app's multiprocessing recipe starts the app's worker processes with the
bundled Python, as an ordinary (not frozen) Python would.
"""
from pdf_minify.__main__ import cli

if __name__ == "__main__":
    cli()
