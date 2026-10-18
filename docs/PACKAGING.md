# Packaging and multi-platform deployment

Designer ruling §176, 2026-10-14. [PLATFORMS.md](PLATFORMS.md) is the authority
for what is certified; this document is a **packaging plan**, not evidence of
existing installers. No packaging tools were installed or releases published.

## Reference: Task Coach, adapted to this app

Reviewed the sibling `/home/user/Downloads/taskcoach`, origin
`git@github.com:taskcoach/taskcoach.git`, local HEAD
`aeb88910cc42d1a25e47413cccc8707db58c13e3`, especially
`docs/PACKAGING.md`, `scripts/build-deb.sh`, `scripts/build-appimage.sh` and the
Windows/macOS build workflows. Its [upstream packaging guide](https://github.com/taskcoach/taskcoach/blob/master/docs/PACKAGING.md)
provides the useful pattern: target-specific dependency tables, native build
jobs, Linux distro packages/AppImage, Windows embedded Python + Inno Setup,
and separate Intel/ARM macOS application bundles/DMGs. These are references,
not a promise to support Task Coach's entire platform matrix.

Do **not** copy wxPython/GTK dependencies, tree-widget patches, Python/version
pins, macOS minima or signing exceptions: PDF Minify uses Qt/PyMuPDF and
must validate its own native libraries and minimum OS. Qt's
[pyside6-deploy](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html)
is an additional Qt-specific candidate, wrapping Nuitka. Choose and test one
bundling route per target; do not combine several freezers by default.

## Dependencies: runtime versus build versus validation

| Component | Running the app | Packaging / validation notes |
|---|---|---|
| CPython | Required; bundle a private interpreter or declare a supported OS Python | Match OS/architecture and binary wheels; only 3.13.5 is currently certified |
| PySide6-Essentials + Shiboken6 | Qt Widgets/Core/Gui/Svg, native Qt libraries and platform plugins | Match binding/runtime versions; include xcb, Windows or Cocoa plugin for the target, plus required image/font support and the SVG icon engine |
| Bundled KDE Breeze action SVGs | Portable action-icon fallback when a desktop theme/name is absent | Include all `ui_qt/assets/breeze/` data (16/22px light/dark SVGs, manifest, notices and LGPL/GPL texts); no KDE package is required at runtime |
| Icon Lab stock PNG resources | Coded Nuvola/Oxygen/GNOME Classic comparison; not a production theme change | Include `ui_qt/assets/icon_lab/` JSON data, provenance, all copyright/license notices and Nuvola's original artwork addendum, plus the reused Breeze assets; decode original PNG bytes in memory, no runtime theme install/download |
| PyMuPDF >=1.28.2 | Required, including its matching native MuPDF binding/library | The native PDF filtering/display APIs are used directly; an older distro binding is not a substitute |
| NumPy, Pillow | Required, including their native extensions/codecs | Use target-specific tested wheels and record exact resolved dependencies |
| `jbig2` / `jbig2.exe` | Required when selecting JBIG2 BW or JBIG2 Color | Native executable and dependencies, not supplied by pip. Explicit choices fail clearly when unavailable; the user can choose Flate instead, never a hidden fallback |
| `zopfli` | Required for the default Best policy (§257) and explicit Zopfli | Best runs the complete encoder, with no missing-encoder fallback. §213 targets one best-encoded Flate format; remaining legacy fixed-path choices require alignment (TODO §217). No new package is claimed here |
| Bundled MuPDF Brotli support | Required for the default Best policy and explicit Brotli; output may need a supporting PDF reader | Verified in the existing 1.28.2 binding, no extra Python package. Verify native/packed-image encoding/decoding, exact predictors/masks, empty-stream guard and optional declaration on each target. Legacy headless Flate remains available |
| `mutool`, `pdfimages`, `jbig2dec` | Not core GUI runtime dependencies | Inspection/independent validation tools; `pdfimages` is used by the saved-image benchmark |
| pytest, Xvfb, xdotool | Not app runtime dependencies | Automated/offscreen and real X11 drag validation tools, respectively |
| Package builders, compiler/SDK, installer tooling | Build only | Keep out of runtime requirements and the certified development environment unless a build is explicitly requested |

Linux source development keeps Python dependencies in `.venv` and native
tools in the OS, per `DEPENDENCIES.md`. A distributable must **declare or
bundle** its dependencies; it cannot assume this workstation's apt packages,
PATH, `.venv`, fonts or developer tools exist on another machine. Do not run
pip or apt, or fetch runtime binaries, on an end user's first launch.

Use a separate build environment and target-specific, hash-locked dependency
resolution. Keep `requirements.txt` as source requirements, not a claim of a
reproducible release lock. Inventory transitive native libraries/plugins and
licenses/notices before distribution; check the actual selected components,
not only their top-level Python package names.

## Target matrix and additional build tools

All formats below are **proposed / unbuilt / uncertified**.

| Target | Initial packaging route | Additional build-time tools / checks |
|---|---|---|
| Debian 13 x86-64 | `.deb`; declared compatible distro dependencies or private app runtime when distro versions are insufficient | `debhelper`, `dh-python`, Python build tooling, `dpkg-buildpackage`, `lintian`; desktop entry/icon/MIME metadata; never install pip into OS-managed Python |
| Broader Linux x86-64 | AppImage with private Python/Qt/native libraries, following Task Coach's AppDir pattern | `python-appimage`/AppImage tooling; audit shared objects and Qt plugin dependencies; build against an intentionally selected oldest compatible glibc baseline, then test each claimed distribution |
| Windows x64 | Private embeddable Python + matching wheels/native encoder; portable directory ZIP, then Inno Setup installer | Build on Windows; controlled `._pth`/import layout, native runtime DLL audit, installer/uninstaller, executable launch without a console or developer Python |
| macOS arm64 / x86_64 | Separate `.app` bundles then `.dmg`; evaluate Qt deployment or Task Coach's py2app pattern against this app | Native per-architecture runner, Xcode command-line tools, bundle/library inspection, `hdiutil`, signing/notarization release tooling; determine minimum macOS from actual wheels/SDK and test it |

For a Qt/Nuitka route, [Qt documents](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html)
build-only Nuitka/ordered-set/zstandard, Linux patchelf, and platform binary
inspection tools (Windows dumpbin, Linux readelf, macOS dyld_info). This is
an alternative toolchain, not an additional universal runtime dependency.
Flatpak/RPM/Arch packages and other architectures can be added when requested
and verified; Task Coach having them does not certify or require them here.

## App-specific integration gates before any packaged build

1. Add package metadata, versioned entry point, icons/desktop metadata and a
   release dependency lock. None of the proposed build scripts/specs or
   installers exists here yet. Preserve `python -m pdf_minify` for source.
2. Preserve multiprocessing **spawn**, process-pool limits, cancellation and
   one GUI per launch. A frozen launcher must dispatch worker/resource-tracker
   startup before importing/creating the GUI or parsing normal app arguments.
   Current `__main__.py` imports the GUI before `cli()` and does not call
   `freeze_support()`; a frozen executable is therefore not ready merely
   because a freezer command completes. Follow the selected tool's spawn
   integration; [PyInstaller explicitly requires early freeze_support](https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html#multi-processing).
3. Resolve bundled external tools at controlled application-relative paths,
   and use the resolved path for both detection and subprocess execution.
   `pipeline.py` detects `jbig2` with `shutil.which` and now invokes that
   resolved path; a bundle still needs an intentional launcher/PATH or resolver. Verify
   the actual `jbig2 -p` output with the installed native MuPDF decoder.
4. Keep helper DLL/shared-library lookup compatible with the helper's origin.
   [PyInstaller's subprocess guidance](https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html#launching-external-programs-from-the-frozen-application)
   distinguishes bundled from host-system programs. Do not strip or replace
   the main GUI's library environment globally to fix an external command.
5. Keep settings in Qt's native settings location and all generated PDF/encoder
   files in `QStandardPaths.TempLocation/pdf-minify/saves/<GUI-PID>/…`.
   Never write into an install directory, app bundle or freezer extraction
   root. Preserve UUID ownership, two simultaneous apps, locks, draft cleanup
   and mmap/document-handle closure before deletion (especially on Windows).
6. Installed launchers must work without `run.sh`, a shell, repository cwd or
   developer environment. No `/usr/bin/jbig2` assumption on Windows/macOS.
   Test native file opening/DnD, spaces/Unicode, long paths, file association,
   fonts and ordinary UI startup. A packaged app must not depend on the
   repository's `examples/images.pdf` for a usable first launch.
7. Keep the exact-display policy: both panes render actual files with all
   PDF-content AA/interpolation/decoder averaging disabled, native geometry
   at device scale, and no filter jobs on zoom. Do not replace it with the
   packager's default smoothed widget/image path.
8. Keep the stock icon assets at their application-relative paths, with
   provenance/notices/licenses, and retain QtSvg plus Qt's SVG icon-engine
   plugin (`iconengines/libqsvgicon.so` on this Linux build; target-specific
   DLL/dylib names elsewhere). An import-only freezer scan may miss this
   plugin and non-Python package data. Test native-theme precedence, no
   theme, an individually missing name, light/dark palettes, disabled states
   and 1×/2× SVG rendering from the installed artifact without `/usr/share/icons`.
   See [ICONS.md](ICONS.md); do not install theme packages on first launch.
   The separate [Icon Lab](ICON_LAB.md) must render its named families directly,
   without inherited theme substitution. Retain both resource directories,
   original PNG-byte hashes and all LGPL/GPL texts in installed artifacts.
   Test choice codes/copy, real/disabled/HiDPI previews and native scrolling.

## Release and certification checklist

- Build on each target OS/architecture in a clean, isolated environment;
  pin inputs, retain source revision, dependency/native-tool versions and
  artifact SHA-256. A Linux build is not a Windows/macOS build.
- Run the full suite, real-file compression benchmark/independent decoder,
  then **test the installed artifact**, not just imports or the source tree.
- On a clean target without development Python/PATH, exercise real native
  GUI launch/exit, filter processing, saved/live/Cancel/Revert flow, export,
  exact display at normal/fractional/HiDPI scales and native DnD. Offscreen
  screenshots alone cannot certify native desktop integration.
- Check multi-page FFPR ownership, native text/vectors, fallback behavior
  without optional tools, two live instances, canceled jobs, normal exit and
  crashed-process cleanup. View whole windows and 1:1 pane/strip captures.
- Test install, upgrade and uninstall without deleting settings, input PDFs
  or another process's temporary files. Verify signing/notarization policy;
  do not tell users to bypass OS security as the standard release workflow.
- Only after the gates pass, add a dated platform/artifact certificate to
  `PLATFORMS.md`. Designer acceptance of individual issues is recorded
  separately. Creating/pushing releases requires explicit authorization.

Primary references checked 2026-10-14: Task Coach's linked guide/workflows,
[Python embeddable distribution](https://docs.python.org/3/using/windows.html#windows-embeddable),
and the Qt/PyInstaller documentation linked above. Revalidate tool versions
when implementing a package; do not copy another project's old pins blindly.
