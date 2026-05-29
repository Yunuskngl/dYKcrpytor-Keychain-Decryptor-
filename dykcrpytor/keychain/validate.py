# SQLite keychain schema validation.

from __future__ import annotations

import sqlite3


def validate_keychain_db(path: str) -> str | None:
    from dykcrpytor.keychain.service import detect_keychain_format, validate_keychain_file

    if str(path).lower().endswith(".plist"):
        return validate_keychain_file(path)

    fmt = detect_keychain_format(path)
    if fmt is not None and fmt.value != "sqlite":
        return validate_keychain_file(path)

    try:
        con = sqlite3.connect(path)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cur.fetchall()}
        con.close()
    except sqlite3.Error as e:
        return f"SQLite read failed: {e}"

    missing = {"genp", "inet", "metadatakeys"} - tables
    if missing:
        return "Missing tables: " + ", ".join(sorted(missing))
    return None
