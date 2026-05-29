#!/usr/bin/env bash
# Build dist/dYKcrpytor.app and dist/dYKcrpytor.dmg (PyInstaller).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt pyinstaller pillow dmgbuild

.venv/bin/python scripts/build_icons.py

.venv/bin/pyinstaller --noconfirm --clean dYKcrpytor_mac.spec

xattr -cr dist/dYKcrpytor.app 2>/dev/null || true
codesign --force --deep -s - dist/dYKcrpytor.app 2>/dev/null || true

.venv/bin/python scripts/build_dmg.py

echo "Done:"
echo "  $ROOT/dist/dYKcrpytor.app"
echo "  $ROOT/dist/dYKcrpytor.dmg"
