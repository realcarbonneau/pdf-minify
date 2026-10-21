"""py2app build of "PDF Minify.app", as Task Coach builds its macOS app.

Run from the checkout by .github/workflows/build-macos.yml:
    APP_VERSION=x.y.z python packaging/macos/setup_app.py py2app
The icon, build/pdf-minify.icns, is made from the app icon PNGs first.
"""
import os

from setuptools import setup

VERSION = os.environ["APP_VERSION"]
DESKTOP_ID = "io.github.realcarbonneau.PdfMinify"

OPTIONS = {
    "argv_emulation": False,
    "iconfile": "build/pdf-minify.icns",
    # Whole packages, as folders: the app reads its icons and notices from
    # pdf_minify/, and finds jbig2 and zopfli in the bin folder beside it.
    "packages": ["pdf_minify", "PySide6", "shiboken6", "pymupdf", "numpy", "PIL"],
    "excludes": ["tkinter"],
    "plist": {
        "CFBundleName": "PDF Minify",
        "CFBundleDisplayName": "PDF Minify",
        "CFBundleIdentifier": DESKTOP_ID,
        "CFBundleVersion": VERSION,
        "CFBundleShortVersionString": VERSION,
        "NSHumanReadableCopyright": "Copyright (C) 2026 Real Carbonneau. GNU AGPL v3 or later.",
        "NSHighResolutionCapable": True,
        # PySide6 6.12's wheels need macOS 14.
        "LSMinimumSystemVersion": "14.0",
        # "Open With" for PDFs, without becoming the default PDF viewer.
        "CFBundleDocumentTypes": [{
            "CFBundleTypeName": "PDF Document",
            "CFBundleTypeRole": "Viewer",
            "LSItemContentTypes": ["com.adobe.pdf"],
            "LSHandlerRank": "Alternate",
        }],
    },
}

setup(
    name="PDF Minify",
    app=["packaging/macos/pdf-minify.py"],
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
