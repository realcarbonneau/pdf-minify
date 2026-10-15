# Dependencies: LOCAL (this dir) vs SYSTEM (apt / OS)

Checked on this machine (Debian 13 trixie, Python 3.13.5) on 2026-10-09.
That table is a historical inventory. The current **certified** runtime and
versions are recorded in [PLATFORMS.md](PLATFORMS.md) (2026-10-14); the actual
pip-provided Qt is 6.12.0, not the separately installed apt Qt 6.8.2.
[PACKAGING.md](PACKAGING.md) separates runtime, build and validation dependencies
and documents planned cross-platform distribution; no installers exist yet.

## SYSTEM — installed via apt, shared by the OS, NOT in this repo
| Package | Status here | Why system |
|---|---|---|
| `python3, python3-venv` | present 3.13.5 | interpreter itself can't live in repo |
| `libqt6core/gui/widgets 6.8.2` | already installed | Qt C++ runtime; pip PySide6 bundles its own copy, but apt copy helps other apps |
| `jbig2` (`/usr/bin/jbig2`, libjbig2enc) | present 0.30 | best BW encoder, no pure-Python equivalent; called as subprocess |
| `jbig2dec` | present | debug/verify JBIG2 output |
| `mutool` (mupdf-tools), `libmupdf` | present | inspect/clean PDFs, fallback renderer |
| `pdfimages` (poppler-utils) | present | debug: list/extract embedded images |
| `python3-pil (pillow 11.1)`, `python3-numpy 2.2.4` | present as system dist-packages | usable without venv, but we still pin pip copies in `.venv` for reproducibility |
| fonts, libgl/egl, PCManFM (for DnD) | OS-provided | can't/shouldn't vendor |

Install missing system bits with:
```bash
sudo apt install python3-venv jbig2 mupdf-tools poppler-utils
# optional, only if you want apt-Qt bindings instead of pip:
sudo apt install python3-pyside6.qtcore python3-pyside6.qtgui python3-pyside6.qtwidgets python3-pymupdf
```

## REPOSITORY-OWNED — in `/home/user/Downloads/pdf-minimalist/`
| Path | What |
|---|---|
| `pdf_minimalist/` | all app source (`core/` headless + `ui_qt/` GUI) |
| `pdf_minimalist/ui_qt/assets/breeze/` | stock LGPL-3-or-later Breeze icon subset, provenance, notices and license texts; portable fallback, not a system-theme dependency |
| `tests/` | pytest suite + future fixtures in `tests/data/` |
| `tools/check_env.py` | prints system-vs-local diagnostic |
| `requirements.txt` | `pymupdf, PySide6-Essentials, Pillow, numpy` → installed into `.venv`, NOT system-wide |
| `.venv/` | local virtualenv (created by `setup_local.sh`, git-ignored) |
| `*.md` | design docs (overview, architecture, UX, test plan, this file) |

Rule: `pip install` always goes to `./.venv` (via `setup_local.sh`).
`apt install` goes to the OS. Never `sudo pip install`.

2026-10-14 BW composition audit: require **PyMuPDF >=1.28.2**, the verified
native MuPDF PDF-filter binding version. It is installed in this project's
`.venv`; the older system apt build is not the implementation dependency.
Font subsetting uses MuPDF's native API; no fontTools/OpenCV/new Python dependency.
`pdfimages` independently verifies saved 1-bit image payloads in the benchmark.

2026-10-14 action icons (§197): existing PySide6-Essentials 6.12.0 supplies
QtSvg and the SVG icon-engine plugin; no new pip/apt dependency was added.
The copied development-source theme was Debian `breeze-icon-theme`
4:5.116.0-1, but the running app never needs it installed. Bundle the
repository-owned subset and Qt SVG support per `ICONS.md` / `PACKAGING.md`.
