# Qt plugin paths for bundled PyQt6 (avoids stale QT_* env vars).

from __future__ import annotations

import os
import sys
from pathlib import Path


def _clear_external_qt_env() -> None:
    for key in (
        "QT_PLUGIN_PATH",
        "QT_QPA_PLATFORM_PLUGIN_PATH",
        "QT_QPA_PLATFORM",
        "QTDIR",
        "QML2_IMPORT_PATH",
    ):
        os.environ.pop(key, None)


def configure_qt_plugin_paths() -> None:
    _clear_external_qt_env()
    try:
        import PyQt6  # noqa: PLC0415
    except ImportError:
        return

    base = Path(PyQt6.__file__).resolve().parent
    for plugins_root in (base / "Qt6" / "plugins", base / "plugins"):
        platforms = plugins_root / "platforms"
        if not platforms.is_dir():
            continue
        os.environ["QT_PLUGIN_PATH"] = str(plugins_root)
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(platforms)
        if sys.platform == "darwin":
            os.environ["QT_QPA_PLATFORM"] = "cocoa"
        return


def ensure_project_on_path() -> Path:
    root = Path(__file__).resolve().parents[1]
    s = str(root)
    if s not in sys.path:
        sys.path.insert(0, s)
    return root
