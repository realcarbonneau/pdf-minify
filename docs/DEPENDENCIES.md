# Dependencies: LOCAL (this dir) vs SYSTEM (apt / OS)

## Rulings (verbatim)

Exact designer text from `DESIGNER_VERBATIM.md`. Text outside the fenced
quotes is not the designer's.

**§8** (undated)

```text
ok, start with that, I already stated alot of my objectives.  Can you put everything local in this directory?  Tell me what is local and what needs to be system packages?
```

The certified runtime and its exact versions are in [PLATFORMS.md](PLATFORMS.md).
The app uses the Qt bundled with the pip PySide6 wheels (6.12.0), not the
separately installed apt Qt. [PACKAGING.md](PACKAGING.md) separates runtime,
build and validation dependencies and plans cross-platform distribution; no
installers exist yet.

## SYSTEM — installed via apt, shared by the OS, NOT in this repo
| Package | Status here | Why system |
|---|---|---|
| `python3, python3-venv` | present 3.13.5 | interpreter itself can't live in repo |
| `libqt6core/gui/widgets 6.8.2` | already installed | Qt C++ runtime; pip PySide6 bundles its own copy, but apt copy helps other apps |
| `jbig2` (`/usr/bin/jbig2`, libjbig2enc) | present 0.30 | best BW encoder, no pure-Python equivalent; called as subprocess |
| `zopfli` (`/usr/bin/zopfli`) | present; required by the default Best policy (§257) | full Flate encoder called as subprocess; MuPDF supplies Best's Brotli encoder/decoder |
| `jbig2dec` | present | debug/verify JBIG2 output |
| `mutool` (mupdf-tools), `libmupdf` | present | inspect/clean PDFs, fallback renderer |
| `pdfimages` (poppler-utils) | present | debug: list/extract embedded images |
| `python3-pil (pillow 11.1)`, `python3-numpy 2.2.4` | present as system dist-packages | usable without venv, but we still pin pip copies in `.venv` for reproducibility |
| fonts, libgl/egl, PCManFM (for DnD) | OS-provided | can't/shouldn't vendor |

Install missing system bits with:
```bash
sudo apt install python3-venv jbig2 zopfli mupdf-tools poppler-utils
# optional, only if you want apt-Qt bindings instead of pip:
sudo apt install python3-pyside6.qtcore python3-pyside6.qtgui python3-pyside6.qtwidgets python3-pymupdf
```

## REPOSITORY-OWNED — this checkout
| Path | What |
|---|---|
| `pdf_minify/` | all app source (`core/` headless + `ui_qt/` GUI) |
| `pdf_minify/ui_qt/assets/breeze/` | stock LGPL-3-or-later Breeze icon subset, provenance, notices and license texts; portable fallback, not a system-theme dependency |
| `pdf_minify/ui_qt/assets/icon_lab/` | curated Nuvola/Oxygen/GNOME PNG resources, original hashes and notices/licenses for §200's comparison lab; not a system package or Task Coach dependency |
| `tests/` | pytest suite and its fixtures |
| `tools/check_env.py` | prints system-vs-local diagnostic |
| `requirements.txt` | `pymupdf, PySide6-Essentials, Pillow, numpy` → installed into `.venv`, NOT system-wide |
| `.venv/` | local virtualenv (created by `setup_local.sh`, git-ignored) |
| `docs/` | design and developer documentation |

Rule: `pip install` always goes to `./.venv` (via `setup_local.sh`).
`apt install` goes to the OS. Never `sudo pip install`.

## Notes

- **PyMuPDF ≥ 1.28.2** is required for MuPDF's native PDF-filter binding; it
  is installed in `.venv`, not taken from the older apt build. Font subsetting
  uses MuPDF's own API, with no extra Python dependency.
- **Encoders.** `jbig2` serves both JBIG2 BW and JBIG2 Color. Best needs
  `/usr/bin/zopfli` and the Brotli encoder/decoder bundled in MuPDF 1.28.2;
  there is no Python Brotli package. A missing selected encoder is a clear
  error, never a silent fallback (§§203/213). Packaging must ship the
  encoders the app selects (TODO §217).
- **Icons.** PySide6-Essentials supplies QtSvg and the SVG icon plugin. The
  bundled Breeze subset (from Debian `breeze-icon-theme` 4:5.116.0-1) and the
  Icon Lab resources (Nuvola 15.08.3-2, Oxygen 5:6.1.0+dfsg-2, GNOME
  3.12.0-6) live in the repository, so no icon theme needs to be installed.
  Their notices and licenses stay with them; see `ICONS.md` and `ICON_LAB.md`.
- **Validation tools.** QPDF 12.2.0, Poppler 25.03.0 and `pdfimages` check
  benchmark output; they are not runtime dependencies, and the installed QPDF
  and Poppler cannot decode Brotli streams.
