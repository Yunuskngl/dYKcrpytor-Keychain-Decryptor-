# dmgbuild settings — styled drag-to-Applications DMG layout.
# `defines["ROOT"]` is injected by scripts/build_dmg.py.

from __future__ import annotations

import os

ROOT = defines["ROOT"]
APP_NAME = "dYKcrpytor.app"
APP_PATH = os.path.join(ROOT, "dist", APP_NAME)
ICON_PATH = os.path.join(ROOT, "assets", "icons", "dYKcrpytor.icns")
BACKGROUND_PATH = os.path.join(ROOT, "assets", "dmg", "background.png")

volume_name = "Install dYKcrpytor"

format = "UDZO"
compression_level = 9

files = [APP_PATH]
symlinks = {"Applications": "/Applications"}

icon = ICON_PATH

window_rect = ((200, 120), (660, 400))
default_view = "icon-view"
show_status_bar = False
show_tab_view = False
show_toolbar = False
show_pathbar = False
show_sidebar = False
show_icon_preview = False

icon_size = 128
text_size = 13

icon_locations = {
    APP_NAME: (155, 145),
    "Applications": (485, 145),
}

background = BACKGROUND_PATH

hide_extensions = [APP_NAME]
