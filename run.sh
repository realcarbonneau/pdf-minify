#!/bin/bash
# Local UI launcher for the designer. Stays in this dir; scratch goes to ./.tmp/.
# Usage: ./run.sh [file.pdf] [--debug]
# No args: the app reopens the last file (§91), else the photo demo.
set -e
cd "$(dirname "$0")"
mkdir -p .tmp
./.venv/bin/python -m pdf_minimalist "$@" 2>&1 | tee .tmp/pdf-minimalist.log
