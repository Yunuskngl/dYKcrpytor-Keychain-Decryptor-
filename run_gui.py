#!/usr/bin/env python3
# GUI entry point — use: .venv/bin/python run_gui.py

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dykcrpytor.qt_bootstrap import configure_qt_plugin_paths

configure_qt_plugin_paths()

from dykcrpytor.gui.main_window import main

if __name__ == "__main__":
    main()
