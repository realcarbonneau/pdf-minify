# Certified platform

Designer ruling: `DESIGNER_VERBATIM.md` §176. Recorded **2026-10-14**
(America/New_York). Packaging plan: [PACKAGING.md](PACKAGING.md).

## Current certificate: Debian 13 x86-64, source/workspace build

| Component | Verified configuration |
|---|---|
| OS | Debian GNU/Linux 13 (trixie); `/etc/os-release` reports 13.7 |
| Architecture / kernel | x86_64; Linux 6.12.107+deb13-amd64 |
| Desktop | LXDE, X11 |
| C runtime | glibc 2.41 |
| Python | CPython 3.13.5, project-local `.venv` |
| GUI binding / actual Qt runtime | PySide6-Essentials 6.12.0 / Qt 6.12.0 |
| PDF binding / actual rendering engine | PyMuPDF 1.28.2 / bundled MuPDF 1.28.2 |
| Numeric / image libraries | NumPy 2.5.3 / Pillow 12.3.0 |
| External BW encoder | `/usr/bin/jbig2`, jbig2enc 0.30 |
| Stream optimizers | `/usr/bin/zopfli` and the existing MuPDF Brotli encoder/decoder present; both are required by the default Best policy (§257), with no hidden fallback |
| Independent PDF validation tools | Poppler 25.03.0; QPDF 12.2.0; `mutool` 1.25.1 |

This certifies the tested **development/source runtime**, not an installer,
binary release, every Debian desktop, or unimplemented features. A release
certificate must identify its
immutable release commit, dependency lock and package SHA-256. Broad `>=`
requirements are not a certification of every permitted dependency version.
The OS's separate Qt packages are not the Qt runtime used by these pip wheels.

## Limits

- Native-binding behavior (tagged page/Form owners, ParentTree, Alt text,
  document metadata, retained Form/text-state operators) is verified on the
  exact MuPDF build above. An engine upgrade needs renewed regression testing,
  not assumed support. This is not a PDF/UA certification.
- The installed Poppler and QPDF read the ordinary codecs but fail Brotli;
  Brotli output needs a supporting reader. This is not an all-reader
  certificate; see `NATIVE_STREAM_COMPRESSION.md`.
- Poppler decodes each colored-JBIG2 mask exactly, but its full-page sampling
  differs from MuPDF's; see `JBIG2.md`.
- Qt's available Windows style is not OS certification.

## Other targets

Windows, macOS (Intel/Apple Silicon), other Linux distributions/architectures,
Wayland, and all packaged formats are **NOT CERTIFIED**. Cross-platform Qt,
Python or Task Coach support is not evidence that this app has passed there.
Promote a target only after its actual installed artifact passes the packaging
release gates on a clean native machine/VM, with dated versions, results,
screenshots, startup/exit evidence and an artifact checksum.
