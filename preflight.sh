#!/usr/bin/env bash
set -e

echo "========================================"
echo "Better Subtitles - Preflight Check"
echo "========================================"
echo

# Prefer venv if present
if [ -f "whisperx-env/bin/activate" ]; then
  # shellcheck disable=SC1091
  source whisperx-env/bin/activate
fi

python setup_whisperx.py --check


