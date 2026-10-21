#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
if ! command -v python3.14 >/dev/null 2>&1; then
    echo "Install Python 3.14 (python3.14 must be on PATH)." >&2
    exit 1
fi
python3.14 -m venv .venv314
.venv314/bin/python -c 'import sys; sys.exit(sys.version_info[:2] != (3, 14))'
.venv314/bin/python -m pip install -r requirements-dev.txt
printf '\nReady. Run: .venv314/bin/python run.py\n'
