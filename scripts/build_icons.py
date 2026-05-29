#!/usr/bin/env python3
# Build dYKcrpytor.icns (macOS) and dYKcrpytor.ico (Windows) from assets/icons/access-keys.png

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "icons" / "access-keys.png"
OUT = ROOT / "assets" / "icons"
ICNS_SET = OUT / "dYKcrpytor.iconset"
ICNS = OUT / "dYKcrpytor.icns"
ICO = OUT / "dYKcrpytor.ico"


def build_ico() -> None:
    from PIL import Image

    img = Image.open(SRC).convert("RGBA")
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ICO, format="ICO", sizes=sizes)
    print(f"Wrote {ICO}")


def build_icns() -> None:
    if sys.platform != "darwin":
        print("Skipping .icns (requires macOS sips + iconutil)")
        return
    if ICNS_SET.exists():
        shutil.rmtree(ICNS_SET)
    ICNS_SET.mkdir(parents=True)
    spec = [
        ("icon_16x16.png", 16),
        ("icon_16x16@2x.png", 32),
        ("icon_32x32.png", 32),
        ("icon_32x32@2x.png", 64),
        ("icon_128x128.png", 128),
        ("icon_128x128@2x.png", 256),
        ("icon_256x256.png", 256),
        ("icon_256x256@2x.png", 512),
        ("icon_512x512.png", 512),
        ("icon_512x512@2x.png", 1024),
    ]
    for name, size in spec:
        dest = ICNS_SET / name
        subprocess.run(
            ["sips", "-z", str(size), str(size), str(SRC), "--out", str(dest)],
            check=True,
            capture_output=True,
        )
    subprocess.run(["iconutil", "-c", "icns", str(ICNS_SET), "-o", str(ICNS)], check=True)
    shutil.rmtree(ICNS_SET)
    print(f"Wrote {ICNS}")


def main() -> int:
    if not SRC.is_file():
        print(f"Missing {SRC}", file=sys.stderr)
        return 1
    build_ico()
    build_icns()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
