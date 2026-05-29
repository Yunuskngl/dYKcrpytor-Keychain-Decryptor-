# Export decrypted rows to SQLite (genp / inet tables).

from __future__ import annotations

import binascii
import sqlite3
from pathlib import Path
from typing import Any


def export_decrypted_to_sqlite(output_path: str | Path, data: dict) -> None:
    out_db = sqlite3.connect(str(output_path))
    cursor = out_db.cursor()
    cursor.execute("DROP TABLE IF EXISTS genp")
    cursor.execute("DROP TABLE IF EXISTS inet")
    _create_table_from_data(cursor, "genp", data.get("genp") or [])
    _create_table_from_data(cursor, "inet", data.get("inet") or [])
    out_db.commit()
    out_db.close()


def _create_table_from_data(cursor, table_name: str, data_list: list) -> None:
    if not data_list:
        return
    all_keys: set[str] = set()
    for item in data_list:
        if isinstance(item, dict):
            all_keys.update(str(k) for k in item.keys())
    keys = sorted(all_keys)
    columns = ", ".join(f'"{k}" TEXT' for k in keys)
    cursor.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, {columns})"
    )
    placeholders = ", ".join(["?"] * len(keys))
    columns_str = ", ".join(f'"{k}"' for k in keys)
    insert_stmt = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    for item in data_list:
        if not isinstance(item, dict):
            continue
        row_values = [_decode_value(item.get(key, "")) for key in keys]
        cursor.execute(insert_stmt, row_values)


def _decode_value(val: Any) -> str:
    if isinstance(val, bytes):
        try:
            return val.decode("utf-8")
        except UnicodeDecodeError:
            return "0x" + binascii.hexlify(val).decode("utf-8")
    if val is None:
        return ""
    return str(val)
