#!/bin/bash
# Build the encoders the macOS app carries: zopfli and jbig2, self-contained,
# from sources pinned by SHA-256. Leptonica is built with PNG input only, the
# one format the app gives jbig2. Each tool needs only the system's zlib and
# C/C++ runtime. Honors MACOSX_DEPLOYMENT_TARGET (the app's minimum macOS).
#
# Usage: scripts/build-macos-tools.sh OUTDIR
#   -> OUTDIR/bin/{jbig2,zopfli} and OUTDIR/bin/licenses/
# Used by .github/workflows/build-macos.yml; also runs on Linux to test it.

set -euo pipefail

OUT="$(mkdir -p "${1:?Usage: $0 OUTDIR}" && cd "$1" && pwd)"
WORK="$(mktemp -d -t pdf-minify-tools.XXXXXX)"
trap 'rm -rf "$WORK"' EXIT
PREFIX="$WORK/prefix"
JOBS="$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2)"

ZOPFLI=(1.0.3 "https://github.com/google/zopfli/archive/refs/tags/zopfli-1.0.3.tar.gz"
        e955a7739f71af37ef3349c4fa141c648e8775bceb2195be07e86f8e638814bd)
LIBPNG=(1.6.59 "https://github.com/pnggroup/libpng/archive/refs/tags/v1.6.59.tar.gz"
        2540302a1844ad2b2b501977abecfa850f265f97b78f065a712ab4074a89f5b5)
LEPTONICA=(1.87.0 "https://github.com/DanBloomberg/leptonica/releases/download/1.87.0/leptonica-1.87.0.tar.gz"
           c73363397f96eb1295602bf44d708a994ad42046c791bf03ea0505d829bdb6a7)
JBIG2ENC=(0.32 "https://github.com/agl/jbig2enc/archive/refs/tags/0.32.tar.gz"
          5b3b1c48617e5b1608f916a78038ea867a2c9eb20c2ff34a78a48a243f655c2a)

# fetch NAME URL SHA256: download, check, unpack into $WORK/NAME.
fetch() {
    curl -sSfL -o "$WORK/$1.tar.gz" "$2"
    echo "$3  $WORK/$1.tar.gz" | shasum -a 256 -c - > /dev/null || { echo "$1: wrong SHA-256"; exit 1; }
    mkdir -p "$WORK/$1"
    tar -xzf "$WORK/$1.tar.gz" -C "$WORK/$1" --strip-components 1
}

fetch zopfli "${ZOPFLI[1]}" "${ZOPFLI[2]}"
fetch libpng "${LIBPNG[1]}" "${LIBPNG[2]}"
fetch leptonica "${LEPTONICA[1]}" "${LEPTONICA[2]}"
fetch jbig2enc "${JBIG2ENC[1]}" "${JBIG2ENC[2]}"

CC="${CC:-cc}"
CXX="${CXX:-c++}"
mkdir -p "$OUT/bin/licenses"

echo "zopfli ${ZOPFLI[0]}"
"$CC" -O2 "$WORK"/zopfli/src/zopfli/*.c -lm -o "$OUT/bin/zopfli"

echo "libpng ${LIBPNG[0]} (static)"
(cd "$WORK/libpng" && ./configure --quiet --prefix="$PREFIX" --disable-shared --enable-static \
    && make -s -j"$JOBS" install) > "$WORK/libpng.log" 2>&1 || { tail -30 "$WORK/libpng.log"; exit 1; }

echo "leptonica ${LEPTONICA[0]} (static, PNG input only)"
(cd "$WORK/leptonica" && PKG_CONFIG_PATH="$PREFIX/lib/pkgconfig" \
    CPPFLAGS="-I$PREFIX/include" LDFLAGS="-L$PREFIX/lib" \
    ./configure --quiet --prefix="$PREFIX" --disable-shared --enable-static --disable-programs \
        --without-jpeg --without-giflib --without-libtiff --without-libwebp \
        --without-libwebpmux --without-libopenjpeg \
    && make -s -j"$JOBS" install) > "$WORK/leptonica.log" 2>&1 || { tail -30 "$WORK/leptonica.log"; exit 1; }

echo "jbig2enc ${JBIG2ENC[0]}"
(cd "$WORK/jbig2enc" && "$CXX" -O2 -DVERSION="\"$(cat VERSION)\"" -I"$PREFIX/include" \
    src/jbig2.cc src/jbig2enc.cc src/jbig2arith.cc src/jbig2sym.cc src/jbig2comparator.cc \
    "$PREFIX/lib/libleptonica.a" "$PREFIX/lib/libpng16.a" -lz -lm -o "$OUT/bin/jbig2")

cp "$WORK/zopfli/COPYING" "$OUT/bin/licenses/zopfli-COPYING.txt"
cp "$WORK/jbig2enc/COPYING" "$OUT/bin/licenses/jbig2enc-COPYING.txt"
cp "$WORK/jbig2enc/doc/PATENTS" "$OUT/bin/licenses/jbig2enc-PATENTS.txt" 2>/dev/null || true
cp "$WORK/leptonica/leptonica-license.txt" "$OUT/bin/licenses/leptonica-license.txt"
cp "$WORK/libpng/LICENSE" "$OUT/bin/licenses/libpng-LICENSE.txt"

"$OUT/bin/jbig2" --version 2>&1 | head -2
ls -la "$OUT/bin"
