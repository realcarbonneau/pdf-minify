# Packaging and multi-platform deployment

## Rulings (verbatim)

Exact designer text from `DESIGNER_VERBATIM.md`. Text outside the fenced
quotes is not the designer's.

**§176** (2026-10-14)

```text
Also, document the current platform as the certerfied and create a document for packaging, meaning if any packages are required to make this work on multiple platforms, you can follow the taskcoach project which is also on github and in a sister dir here.
```

**§298** (2026-10-20)

```text
can you make a build for the two debian version that are stable?  Follow taskcoach
```

**§299** (2026-10-20)

```text
can it work with the packages in debian 13, please test carefully before proposing options!
```

**§301** (2026-10-20)

```text
For the packages, so we need to package everything?  but doesn't debian oblige everything be installed in a venv, if not system?  Follow taskcoach examples please.
```

**§302** (2026-10-20)

```text
debian 13 only for now, that is fine. but why do you need a separate version per arch? just get pip to download the correct one??
```

**§303** (2026-10-20)

```text
ok, proceed for arch specific, but only do x86 for now, arm is not common for desktops I think and it just adds to user confusion, they are already confused with multiple plateforms.  Also, follow the taskcoach windows and macos because those are very common and ubuntu also.
```

**§304** (2026-10-21)

```text
Both options for mac please, and yes, push to github please.
```

[PLATFORMS.md](PLATFORMS.md) records what each package has passed. The
packages follow Task Coach (`/home/user/Downloads/taskcoach`, its
`docs/PACKAGING.md`, `debian/`, `scripts/build-deb.sh` and build workflows),
adapted where PDF Minify differs: compiled dependencies and two external
encoders.

## Targets

The Linux and Windows packages are x86-64 (§303); macOS has both (§304).

| Target | Format | Dependencies | Build | Test |
|---|---|---|---|---|
| Debian 13 (trixie) | `.deb` | Debian's PySide6, NumPy, Pillow, `jbig2`, `zopfli`; bundled PyMuPDF | `scripts/build-deb.sh`, `build-deb.yml` | `scripts/test-deb.sh` |
| Ubuntu 26.04 (resolute) | `.deb` | as Debian 13 | same | same |
| Ubuntu 24.04 (noble) | `.deb` | Ubuntu's NumPy, Pillow, `jbig2`, `zopfli`; bundled PySide6 and PyMuPDF | same | same |
| Windows 10/11 | Inno Setup installer and portable ZIP | everything bundled: Python 3.13 embeddable, pinned wheels, `jbig2.exe`, `zopfli.exe` | `build-windows.yml` | same workflow |
| macOS 14+, Intel and Apple Silicon (§304) | DMG, one per processor | everything bundled: py2app with Python 3.13 and pinned wheels, `jbig2` and `zopfli` built from source | `build-macos.yml` | same workflow |

Not packaged:

- **Debian 12 and Ubuntu 22.04.** They have no PySide6 and no `jbig2`, and
  their PyMuPDF, NumPy and Pillow are too old: a package would carry nearly
  everything, about 110 MB, and compile `jbig2` (§302: Debian 13 only).
- **ARM Linux and Windows** (§303). macOS gets both processors (§304).
- **Debian's own PyMuPDF**, on every release so far. Debian 13 has 1.25,
  Ubuntu 24.04 1.23 and Ubuntu 26.04 1.26; the app needs 1.28.2. On
  Debian 13, measured (§299): the app cannot open a file (no
  `fz_tune_image_rendering`), MuPDF has no Brotli encoder or decoder (Best,
  the default, cannot save), inline images crash MuPDF 1.25, and line art
  renders visibly heavier. Debian 14 (forky) ships MuPDF 1.28.2 with
  Brotli; its package can depend on `python3-pymupdf` and bundle nothing.

## Linux packages: Task Coach's rule

Each release's own packages first. A library the release lacks, or ships
too old, is pip-installed **at build time** into the package, never on the
user's machine, as Task Coach's Arch and Fedora packages do for squaremap.

- The app and the bundled libraries are private modules in
  `/usr/lib/pdf-minify` (Debian Python Policy §5.3: `/usr/lib/<package>`
  for architecture-dependent modules). `/usr/bin/pdf-minify` puts that
  folder first on the module path; nothing goes into the system's
  `dist-packages`, so Debian's own `python3-pymupdf` can coexist.
- PEP 668 ("externally managed") stops `pip install` into the system Python.
  It does not apply to files a `.deb` installs: `dpkg` tracks and removes
  them. No venv is involved.
- Debian Policy §4.13 asks archive packages to use the library Debian ships;
  carrying PyMuPDF means these packages could not enter the Debian archive as
  they are. They are published on GitHub, like Task Coach's.
- The bundled wheels contain compiled code, so the package is
  `Architecture: amd64` (Task Coach's is `all`: its bundled code is pure
  Python). One `.deb` per release and processor, built at build time; no
  install-time download (§302).

Per-release files in `debian/bundled/`, named by the release's codename:

| File | Purpose |
|---|---|
| `<codename>.txt` | pip lock, pinned by SHA-256, installed with `--require-hashes --only-binary` |
| `<codename>.depends` | that release's own packages the app uses (`${release:Depends}`) |
| `<codename>.build-depends` | optional: libraries a bundled wheel links against, installed by `build-deb.sh deps` so `dh_shlibdeps` can declare them |
| `<codename>.lintian-overrides` | optional: overrides for files only that release's package carries |

`debian/rules` trims what the app never loads: PyMuPDF's build files and,
where PySide6 is bundled, Qt's tools, QML, and the database, printing,
Designer, embedded-display and virtual-keyboard plugins (some need libraries
no release has). Lintian is clean; each override in
`debian/pdf-minify.lintian-overrides` says why.

To add a release: write its `debian/bundled/` files, build and test it
locally (below), then add it to both matrices in `build-deb.yml`.

### Building and testing locally

```bash
scripts/build-deb.sh deps      # build dependencies (sudo)
scripts/build-deb.sh build     # packages land in build-deb/
scripts/build-deb.sh lintian
scripts/test-deb.sh debian:trixie          # podman or docker
scripts/test-deb.sh ubuntu:24.04 --quick   # install checks only
```

`build-deb.sh` builds from a clean copy of the checkout in `build-deb/src`.
`test-deb.sh` installs the package in a fresh container of its release,
checks the installed files, starts the app on a file whose name has a space,
then runs the full test suite against `/usr/lib/pdf-minify` (`python3 -P`,
so every import comes from the package). Build another release's package in
its own container, as `build-deb.yml` does.

## Windows

`build-windows.yml` follows Task Coach's Windows build:

- Python's embeddable package (3.13.16, SHA-256 checked) in `python\`, its
  `python313._pth` adding the app folder and `Lib\site-packages`.
- `packaging/windows/requirements.txt`: the wheels, pinned by SHA-256,
  installed by the build machine's pip with `--target`; no pip in the app.
- `jbig2.exe` from conda-forge (jbig2enc 0.32 with Leptonica and its image
  libraries) and `zopfli.exe` built from zopfli 1.0.3's source with the
  static C runtime, in `bin\`, with every licence in `bin\licenses\`.
- `pdf-minify.pyw` runs under `pythonw.exe` (no console); it writes the log
  to `%TEMP%\pdf-minify\pdf-minify.log`, the folder `run.sh` uses.
- The code is compiled at build time (`compileall`, unchecked hashes), so
  the app never writes into its install folder.
- Inno Setup (`packaging/windows/pdf-minify.iss`): per-user install by
  default, Start-menu entry, optional desktop icon, "Open with" for PDFs
  without taking over the default viewer. Uninstalling keeps settings and
  temporary files, which are never in the install folder.
- The portable ZIP starts from `PDF Minify.cmd`. Task Coach also ships a
  VBScript launcher; Windows is removing VBScript.

The workflow smoke-tests the built app (`packaging/smoke_test.py`), runs the
full test suite against it, then installs the installer silently,
smoke-tests the installed copy and uninstalls it.

## macOS

`build-macos.yml` follows Task Coach's macOS build: py2app (0.28.10, with
setuptools below 71.0.2 as Task Coach pins it) on GitHub's Intel
(`macos-15-intel`) and Apple Silicon (`macos-latest`) runners, then a DMG.

- `packaging/macos/setup_app.py` lists whole packages, which py2app copies
  as folders into `Contents/Resources/lib/python3.13/`; the app's icons and
  notices stay readable, and `bin/` beside `pdf_minify` holds the encoders.
- `scripts/build-macos-tools.sh` builds `zopfli` 1.0.3 and `jbig2`
  (jbig2enc 0.32, as on Windows) from sources pinned by SHA-256, with a
  static Leptonica 1.87.0 reading PNG only (the one format the app gives
  it) and libpng 1.6.59. They need only the system's zlib and C/C++
  runtime. It runs on Linux too, to test it.
- macOS 14 or later: PySide6 6.12's wheels need it, and the encoders are
  built for it (`MACOSX_DEPLOYMENT_TARGET`).
- py2app's multiprocessing recipe starts the worker processes with the
  bundled Python, as an ordinary Python would.
- Finder's "Open With" and a PDF dropped on the Dock icon arrive as a
  `QFileOpenEvent`; `FileOpenHandler` opens them. The app is registered for
  PDFs as an alternative, never the default viewer.
- The code is compiled at build time, so the app never writes into its
  bundle; the bundle is ad-hoc signed, not notarized (Signing, below).
- Licences of the bundled packages and Python are in
  `Contents/Resources/licenses/`; PySide6 names LGPL-3.0 without its text,
  so the LGPL-3 and GPL-3 texts are copied beside it.

The workflow smoke-tests the built app through its own executable and runs
the full test suite against it.

## Bundled encoders

`pdf_minify/core/external_tools.find_tool` returns the app's own copy (a
`bin` folder next to `pdf_minify`) first, else the one on PATH. Callers run
the returned path, so detection and execution use the same program. Linux
packages carry no `bin` and use the release's `jbig2` and `zopfli`.

## Signing

As Task Coach's, the Windows installer is not code-signed and the macOS app
would not be notarized: both cost a yearly fee. Windows SmartScreen and macOS
Gatekeeper warn on first start; Task Coach's install guides show users how
to proceed. Linux packages need neither.

## App-specific gates

1. Package metadata: version (`pdf_minify.__version__`), desktop entry,
   icon and AppStream ID (`pdf_minify.DESKTOP_ID`,
   `packaging/linux/`), per-target locks. Keep `python -m pdf_minify` for
   source.
2. Preserve multiprocessing **spawn**, process-pool limits, cancellation and
   one GUI per launch. The Linux and Windows packages run an ordinary
   Python; on macOS, py2app's multiprocessing recipe starts workers with the
   bundled Python. Another freezer (PyInstaller) would need
   `multiprocessing.freeze_support()` before the GUI is imported.
3. Run bundled tools by the path `find_tool` returns, never by name.
4. Keep a helper's DLL/shared-library lookup with the helper: Windows loads
   `jbig2.exe`'s DLLs from its own `bin` folder. Do not change the GUI's
   library environment to fix an external command.
5. Settings stay in Qt's native location and generated files in
   `QStandardPaths.TempLocation/pdf-minify/saves/<GUI-PID>/…`; never in an
   install directory or app bundle.
6. Installed launchers work without `run.sh`, a shell, the repository's
   folder or `examples/images.pdf`.
7. Keep the exact-display policy: both panes render actual files with all
   PDF-content AA/interpolation/decoder averaging disabled.
8. Keep the stock icon assets with their notices and licences, and Qt's SVG
   icon-engine plugin (`qt6-svg-plugins` where Qt comes from the release).

## Release and certification checklist

- Build each target in a clean, isolated environment from pinned inputs.
- Run the full suite against the **installed** artifact, not the source tree.
- On a real desktop, exercise GUI launch and exit, filter processing,
  save/Cancel/Revert, exact display at normal and HiDPI scales, and native
  drag-and-drop. Offscreen runs cannot certify desktop integration.
- Test install, upgrade and uninstall without losing settings, input PDFs or
  another process's temporary files.
- Only then add a dated certificate to `PLATFORMS.md`. Creating or pushing
  releases requires explicit authorization.

## Design traps

- **Running a found tool by name.** `deflate_best` once checked for zopfli,
  then ran `"zopfli"`; with a bundled copy off PATH it fell back to zlib
  without a word. Always run the returned path (`test_external_tools.py`).
- **dh_python3 renames extensions** to the build's Python version
  (`_mupdf.cpython-313-…so`), tying the package to one Python; PyMuPDF and
  PySide6 are built for every Python from 3.10 on, so `debian/rules` passes
  `--no-ext-rename`.
- **Minimal Ubuntu container images skip man pages** (`path-exclude`), so
  `test-deb.sh` checks the man page inside the `.deb`.
- **Debian's PySide6 6.8 is stricter than 6.12**: drag events take a
  `QPoint` there and a `QPointF` (the `QPoint` form deprecated) on newer Qt;
  tests build them with the `drag_event` fixture.
