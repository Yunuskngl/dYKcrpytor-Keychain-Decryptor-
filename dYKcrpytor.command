#!/bin/bash
# Launch GUI via project .venv (double-click in Finder).
cd "$(dirname "$0")" || exit 1
if [[ ! -x .venv/bin/python ]]; then
  osascript -e 'display dialog "Run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" buttons {"OK"} default button 1' &
  exit 1
fi
exec .venv/bin/python run_gui.py
