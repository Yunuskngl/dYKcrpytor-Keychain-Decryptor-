#!/usr/bin/env python3
# Build a styled macOS DMG (drag app → Applications).

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "dYKcrpytor.dmg"
SETTINGS = ROOT / "scripts" / "dmg_settings.py"


def main() -> int:
    app = ROOT / "dist" / "dYKcrpytor.app"
    if not app.is_dir():
        print(f"Missing {app} — run PyInstaller first.", file=sys.stderr)
        return 1

    sys.path.insert(0, str(ROOT / "scripts"))
    from generate_dmg_background import main as gen_bg

    gen_bg()

    try:
        import dmgbuild
    except ImportError:
        print("Install dmgbuild: pip install dmgbuild", file=sys.stderr)
        return 1

    if OUT.exists():
        OUT.unlink()

    dmgbuild.build_dmg(
        str(OUT),
        "Install dYKcrpytor",
        settings_file=str(SETTINGS),
        defines={"ROOT": str(ROOT)},
    )
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
