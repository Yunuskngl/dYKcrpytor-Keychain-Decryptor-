# Resolve application icon path (dev tree or PyInstaller bundle).

from __future__ import annotations

import sys
from pathlib import Path


def project_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[1]


def icon_png_path() -> Path | None:
    path = project_root() / "assets" / "icons" / "access-keys.png"
    return path if path.is_file() else None
