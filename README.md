# PDF Minify — make PDFs smaller

<p align="center"><img src="pdf_minify/ui_qt/assets/app_icon/pdf-minify-128.png" alt="PDF Minify icon" width="128"></p>

Make PDFs smaller with a variety of filters, compression algorithms and
techniques, and extensive previews that give a quick overview of each one's
visual effect and file size. Every preview and size is the actual file you
would save.

## Install

Installer packages are not available yet. PDF Minify runs from source on its
certified platform; packages for other systems are planned.

| Platform | Status |
|----------|--------|
| [Debian 13 (Trixie), x86-64](#debian-13) | Run from source |
| Other Linux, Windows, macOS | Planned |

### Debian 13

```bash
sudo apt install git python3-venv jbig2 zopfli
git clone https://github.com/realcarbonneau/pdf-minify.git
cd pdf-minify
./setup_local.sh
./run.sh
```

### Opening the smaller PDFs

To save the most space, PDF Minify may store parts of a file with Brotli
compression, which older PDF readers (for example Evince and other
Poppler-based viewers) cannot display yet. If a file must open everywhere,
choose a Flate option under **PDF streams** before saving.

## Support

Report bugs or request features at GitHub Issues:
https://github.com/realcarbonneau/pdf-minify/issues

## License

PDF Minify is free software, licensed under the
[GNU Affero General Public License v3.0 or later](LICENSE).

Copyright (C) 2026 Real Carbonneau

Bundled third-party icons keep their own licenses; their notices are with
them in `pdf_minify/ui_qt/assets/`.

## Developers

Running from source, tests, the design and the measured benchmarks:
[developer documentation](docs/README.md).
