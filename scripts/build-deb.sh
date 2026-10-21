#!/bin/bash
# Build the PDF Minify .deb for the Debian or Ubuntu release this runs on.
# Runs locally or in CI (.github/workflows/build-deb.yml). The build works on
# a clean copy of the tracked files in build-deb/src, so the checkout stays
# clean and the packages land in build-deb/.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="${PROJECT_DIR}/build-deb"
SRC_DIR="${BUILD_DIR}/src"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

sudo_cmd() {
    if [ "$(id -u)" -eq 0 ]; then "$@"; else sudo "$@"; fi
}

check_system() {
    [ -f /etc/os-release ] || error "This script must be run on Debian or Ubuntu"
    . /etc/os-release
    CODENAME="${VERSION_CODENAME}"
    [ -f "${PROJECT_DIR}/debian/bundled/${CODENAME}.txt" ] || \
        error "No package for ${PRETTY_NAME} (${CODENAME}): debian/bundled/${CODENAME}.txt is missing"
    [ "$(dpkg --print-architecture)" = "amd64" ] || error "Packages are built for x86-64 (amd64) only"
    info "Building on: ${PRETTY_NAME} (${CODENAME})"
}

install_deps() {
    info "Installing build dependencies..."
    sudo_cmd apt-get update
    sudo_cmd apt-get install -y --no-install-recommends \
        build-essential debhelper dh-python python3 python3-pip lintian fakeroot git
    # Libraries a bundled wheel links against, so dh_shlibdeps can declare them.
    EXTRA="${PROJECT_DIR}/debian/bundled/${CODENAME}.build-depends"
    if [ -f "$EXTRA" ]; then
        sudo_cmd apt-get install -y --no-install-recommends $(grep -v -E '^\s*(#|$)' "$EXTRA")
    fi
}

get_version() {
    (cd "$PROJECT_DIR" && python3 -c "from pdf_minify import __version__; print(__version__)")
}

clean_build() {
    info "Cleaning previous build artifacts..."
    rm -rf "$BUILD_DIR"
}

build_package() {
    check_system
    VERSION=$(get_version)
    CHANGELOG_VERSION=$(cd "$PROJECT_DIR" && dpkg-parsechangelog -S Version)
    [ "${CHANGELOG_VERSION%-*}" = "$VERSION" ] || \
        error "debian/changelog has ${CHANGELOG_VERSION}, but pdf_minify/__init__.py has ${VERSION}"
    info "Package version: ${CHANGELOG_VERSION}"

    clean_build
    mkdir -p "$SRC_DIR"
    # Tracked files plus new, not-ignored ones, so a build before a commit works.
    (cd "$PROJECT_DIR" && git ls-files -z --cached --others --exclude-standard) | \
        (cd "$PROJECT_DIR" && xargs -0 cp --parents -t "$SRC_DIR" 2>/dev/null || true)

    info "Building binary package..."
    (cd "$SRC_DIR" && dpkg-buildpackage -us -uc -b)

    info "Build complete. Packages are in ${BUILD_DIR}:"
    ls -la "$BUILD_DIR"/*.deb
}

run_lintian() {
    DEB_FILE=$(ls "$BUILD_DIR"/*.deb 2>/dev/null | head -1)
    [ -n "$DEB_FILE" ] || error "No .deb file found; build first"
    info "Checking $DEB_FILE"
    lintian --info --display-info "$DEB_FILE" || true
}

test_install() {
    check_system
    DEB_FILE=$(ls "$BUILD_DIR"/*.deb 2>/dev/null | head -1)
    [ -n "$DEB_FILE" ] || error "No .deb file found to test"
    info "Installing $DEB_FILE..."
    sudo_cmd apt-get install -y "$DEB_FILE"
    dpkg -s pdf-minify | grep -q "Status: install ok installed" || error "Package not installed"
    QT_QPA_PLATFORM=offscreen python3 -c "
import sys
sys.path.insert(0, '/usr/lib/pdf-minify')
import pymupdf
from pdf_minify import __version__
from pdf_minify.core.stream_compression import brotli_available
assert pymupdf.__file__.startswith('/usr/lib/pdf-minify/'), pymupdf.__file__
assert brotli_available()
print('pdf_minify', __version__, '| PyMuPDF', pymupdf.__version__, 'from', pymupdf.__file__)
" || error "The installed package does not load its bundled PyMuPDF"
    info "Installation test passed!"
}

usage() {
    cat << EOF
Usage: $0 [COMMAND]

Build the PDF Minify .deb for this Debian or Ubuntu release (x86-64).

Commands:
    build       Build the .deb package (default)
    clean       Remove build-deb/
    deps        Install build dependencies (sudo)
    lintian     Run lintian on the built package
    test        Install the built package (sudo) and check it loads
    all         clean, deps, build, lintian
EOF
}

case "${1:-build}" in
    build)   build_package ;;
    clean)   clean_build ;;
    deps)    check_system; install_deps ;;
    lintian) run_lintian ;;
    test)    test_install ;;
    all)     check_system; install_deps; build_package; run_lintian ;;
    -h|--help) usage ;;
    *) usage; error "Unknown command: $1" ;;
esac
