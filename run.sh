#!/bin/bash
# Local UI launcher; logs follow the OS temp directory.
# Usage: ./run.sh [file.pdf] [--debug]
# No args: the app reopens the last file (§91), else the photo demo.
set -e -o pipefail
trap 'app_exit_code=$?; printf "APP_EXIT status=%s\n" "$app_exit_code"' EXIT
cd "$(dirname "$0")"
mkdir -p .tmp
LOGDIR="${TMPDIR:-/tmp}/pdf-minify"
mkdir -p "$LOGDIR" .tmp
./.venv/bin/python -m pdf_minify "$@" 2>&1 | tee "$LOGDIR/pdf-minify.log"
