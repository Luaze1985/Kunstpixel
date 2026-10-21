#!/usr/bin/env bash
set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
if [[ ! -x .venv/bin/python ]]; then
    python3.13 -m venv .venv
fi
.venv/bin/python -c 'import sys; assert sys.version_info[:2] == (3, 13), "Demoen krever Python 3.13 i .venv"'
.venv/bin/python -m pip install --disable-pip-version-check --no-input -r requirements-demo.txt
exec .venv/bin/python -m src.kunstpixel.hr_simulator web
