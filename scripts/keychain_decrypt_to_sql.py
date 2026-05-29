#!/usr/bin/env python3
# CLI: decrypt keychain .db or backup_keychain_v2.plist → SQLite.

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dykcrpytor.keychain.service import decrypt_keychain_file, export_keychain_to_sqlite, validate_keychain_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Decrypt iOS keychain to SQLite")
    parser.add_argument("keychain", nargs="?", default="keychain-2.db")
    parser.add_argument("-o", "--output", default="decrypted_keychain.db")
    args = parser.parse_args()

    err = validate_keychain_file(args.keychain)
    if err:
        print(err, file=sys.stderr)
        return 1
    print(f"Reading: {args.keychain}")
    data = decrypt_keychain_file(args.keychain)
    export_keychain_to_sqlite(args.keychain, args.output, data)
    print(f"Saved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
