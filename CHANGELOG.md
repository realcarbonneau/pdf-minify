# Changelog

What changes for users in each release, newest first. A release's
section is the text of its GitHub release page
([PACKAGING.md](docs/PACKAGING.md#release-notes)).

## 0.0.1

The first release. PDF Minify makes PDFs smaller with a variety of
filters, compression algorithms and techniques, and previews that show
each one's visual effect and file size. Every preview and size is the
actual file you would save.

### Packages

- Windows 10 and 11: an installer, or a portable ZIP.
- macOS 14 (Sonoma) or later: one DMG for Apple Silicon, one for Intel.
- Debian 13, Ubuntu 24.04 (and Linux Mint 22) and Ubuntu 26.04: a `.deb`
  for each.

The Windows and Linux packages are for 64-bit PCs (x86-64). The Windows
and macOS packages are not signed: Windows asks before running the
installer (**More info**, then **Run anyway**), and macOS before the
first start (**System Settings → Privacy & Security → Open Anyway**).
See the [README](https://github.com/realcarbonneau/pdf-minify#install).

### Known limits

- Some PDF readers, such as Evince and other Poppler-based viewers,
  cannot yet display files saved with Brotli compression. For a file
  that must open everywhere, choose a Flate option under **PDF streams**
  before saving.
