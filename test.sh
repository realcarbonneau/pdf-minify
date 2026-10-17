#!/bin/bash
# Full suite after code-affecting changes; docs-only edits do not require it (§241).
# Usage: ./test.sh
# Runs the whole pytest suite (headless + offscreen Qt) and fails loudly.
set -e
cd "$(dirname "$0")"
./.venv/bin/python -m pytest tests/ -q
echo "FULL SUITE GREEN"
