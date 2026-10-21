# Certified platform

## Rulings (verbatim)

Exact designer text from `DESIGNER_VERBATIM.md`. Text outside the fenced
quotes is not the designer's.

**§176** (2026-10-14)

```text
Also, document the current platform as the certerfied and create a document for packaging, meaning if any packages are required to make this work on multiple platforms, you can follow the taskcoach project which is also on github and in a sister dir here.
```

Certificate date: **2026-10-14** (America/New_York). The first target, LXDE
on Debian, comes from the original brief (§3, quoted in `DESIGN.md`).
Packaging plan: [PACKAGING.md](PACKAGING.md).

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

## Packages tested

Each `.deb` was built in a clean container of its release from the pinned
inputs in `debian/bundled/`, then installed in a fresh container of the same
release by `scripts/test-deb.sh`: install checks, the app started on a file
whose name has a space, and the full test suite run against the installed
copy. Offscreen only: no desktop session, drag-and-drop or HiDPI check yet,
so these are test results, not certificates (see the checklist in
[PACKAGING.md](PACKAGING.md)).

<!-- table: package-tests -->
| Package (x86-64) | Libraries in use | Size | Result (2026-10-20) |
|---|---|---|---|
| Debian 13 `.deb` | Debian's PySide6 6.8.2, NumPy 2.2.4, Pillow 11.1.0; bundled PyMuPDF 1.28.2 | 19 MB (57 MB installed) | all 1,036 tests pass; built before the encoder-path fix, rerun by `build-deb.yml` |
| Ubuntu 24.04 `.deb` | Ubuntu's NumPy 1.26.4, Pillow 10.2.0; bundled PySide6 6.12.0, PyMuPDF 1.28.2 | 70 MB (245 MB installed) | installs and starts; full suite: first run by `build-deb.yml` |
| Ubuntu 26.04 `.deb` | Ubuntu's PySide6 6.10.2, NumPy 2.3.5, Pillow 12.1.1; bundled PyMuPDF 1.28.2 | 21 MB (54 MB installed) | installs and starts; full suite: first run by `build-deb.yml` |
| Windows x64 installer | everything bundled | | first run by `build-windows.yml` |

## Other targets

Windows, macOS, other Linux distributions and architectures, and Wayland
are **NOT CERTIFIED**. Cross-platform Qt, Python or Task Coach support is not
evidence that this app has passed there. Promote a target only after its
installed artifact passes the release checklist on a clean native machine or
VM, with dated versions, results, screenshots, startup and exit evidence and
an artifact checksum.
