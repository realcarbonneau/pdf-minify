#!/bin/bash
# Test a built PDF Minify .deb on a clean system: install it in a fresh
# container of its release, check the installed app, then run the full test
# suite against the installed copy in /usr/lib/pdf-minify.
#
# Usage: scripts/test-deb.sh IMAGE [--quick]
#   IMAGE    container image of the release, e.g. debian:trixie
#   --quick  install checks only, without the full test suite
# Uses docker (as in GitHub Actions), or podman.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="${PROJECT_DIR}/build-deb"
IMAGE="$1"
MODE="${2:-full}"

[ -n "$IMAGE" ] || { echo "Usage: $0 IMAGE [--quick]"; exit 1; }
ls "$BUILD_DIR"/*.deb > /dev/null 2>&1 || { echo "No .deb in $BUILD_DIR; run scripts/build-deb.sh first"; exit 1; }
ENGINE=$(command -v docker || command -v podman) || { echo "Needs docker or podman"; exit 1; }
case "$IMAGE" in */*) ;; *) IMAGE="docker.io/library/$IMAGE" ;; esac

# The tests run from a copy of the checkout. Some read the app's source files
# (benchmark provenance), but every import comes from the installed package:
# python3 -P with /usr/lib/pdf-minify first on PYTHONPATH.
WORK=$(mktemp -d -t pdf-minify-test.XXXXXX)
# Files the container wrote as root may resist removal; the result stands.
trap 'rm -rf "$WORK" 2> /dev/null || true' EXIT
mkdir -p "$WORK/src" "$WORK/out"
(cd "$PROJECT_DIR" && git ls-files -z --cached --others --exclude-standard) | \
    (cd "$PROJECT_DIR" && xargs -0 cp --parents -t "$WORK/src")

"$ENGINE" run --rm \
    -e DEBIAN_FRONTEND=noninteractive -e TZ=UTC -e MODE="$MODE" \
    -v "$BUILD_DIR:/packages:ro" -v "$WORK/src:/src" -v "$WORK/out:/out" \
    "$IMAGE" bash -c '
set -e
check() { "$@" || { echo "FAILED: $*"; exit 1; }; }
apt-get update -qq
apt-get install -y -qq /packages/*.deb > /tmp/apt.log 2>&1 || { tail -20 /tmp/apt.log; exit 1; }
echo "Installed: $(dpkg-query -W -f="\${Package} \${Version} \${Architecture}" pdf-minify)"

check test -x /usr/bin/pdf-minify
check test -f /usr/share/applications/io.github.realcarbonneau.PdfMinify.desktop
check test -f /usr/share/icons/hicolor/256x256/apps/io.github.realcarbonneau.PdfMinify.png
# In the package (minimal container images do not install man pages).
dpkg-deb -c /packages/*.deb | grep -q "usr/share/man/man1/pdf-minify.1.gz" || { echo "FAILED: no man page"; exit 1; }
check test -f /usr/lib/pdf-minify/pdf_minify/ui_qt/assets/breeze/LICENSE.LGPL-3
check test -f /usr/lib/pdf-minify/pdf_minify/ui_qt/assets/icon_lab/NOTICE.md
check command -v jbig2 zopfli > /dev/null
check pdf-minify --help > /dev/null

QT_QPA_PLATFORM=offscreen python3 - <<"PY"
import sys
sys.path.insert(0, "/usr/lib/pdf-minify")
import numpy, PIL, PySide6, pymupdf
from PySide6.QtGui import QImageReader
from pdf_minify import __version__
from pdf_minify.core.stream_compression import brotli_available
print("pdf_minify", __version__, "| PyMuPDF", pymupdf.__version__, "| PySide6", PySide6.__version__,
      "| NumPy", numpy.__version__, "| Pillow", PIL.__version__)
assert pymupdf.__file__.startswith("/usr/lib/pdf-minify/"), pymupdf.__file__
assert brotli_available(), "MuPDF without Brotli"
assert b"svg" in [bytes(f) for f in QImageReader.supportedImageFormats()], "no Qt SVG plugin"
PY

# Start the app as the menu entry does, on a file whose name has a space.
python3 -c "import sys; sys.path.insert(0, \"/usr/lib/pdf-minify\"); import pymupdf
d = pymupdf.open(); d.new_page().insert_text((72, 72), \"PDF Minify\"); d.save(\"/tmp/a file.pdf\")"
(cd /tmp && QT_QPA_PLATFORM=offscreen timeout 30 pdf-minify --debug "/tmp/a file.pdf" > /tmp/app.log 2>&1) || true
check grep -q "opened /tmp/a file.pdf" /tmp/app.log
check grep -q "window shown" /tmp/app.log
! grep -q "Traceback" /tmp/app.log || { cat /tmp/app.log; exit 1; }
echo "Install checks passed"

[ "$MODE" = "--quick" ] && exit 0
TEST_PKGS="python3-pytest poppler-utils"
# Where Qt comes from the release, its QtTest module is a separate package.
dpkg -s python3-pyside6.qtcore > /dev/null 2>&1 && TEST_PKGS="$TEST_PKGS python3-pyside6.qttest"
apt-get install -y -qq $TEST_PKGS > /tmp/apt-test.log 2>&1 || { tail -20 /tmp/apt-test.log; exit 1; }
cd /src
export PYTHONPATH=/usr/lib/pdf-minify:/src QT_QPA_PLATFORM=offscreen
check python3 -P -c "import pdf_minify, pymupdf, sys
assert pdf_minify.__file__.startswith(\"/usr/lib/pdf-minify/\"), pdf_minify.__file__
assert pymupdf.__file__.startswith(\"/usr/lib/pdf-minify/\"), pymupdf.__file__"
status=0
for f in tests/test_*.py; do
    n=$(basename "$f" .py)
    if timeout 900 python3 -P -u -m pytest "$f" -q -p no:cacheprovider -rfE \
        -o faulthandler_timeout=300 > "/out/$n.log" 2>&1; then
        echo "ok    $n: $(tail -n 1 "/out/$n.log")"
    else
        status=1
        echo "FAIL  $n: $(tail -n 1 "/out/$n.log")"
        grep -E "^(FAILED|ERROR) " "/out/$n.log" | head -20
    fi
done
[ $status -eq 0 ] && echo "Full test suite passed on the installed package"
exit $status
'
