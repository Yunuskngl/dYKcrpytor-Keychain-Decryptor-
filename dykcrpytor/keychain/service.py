# Routes input to SQLite or backup_keychain_v2.plist decryptor.

from __future__ import annotations

import plistlib
import sqlite3
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional, Union

from dykcrpytor.keychain.backup_plist import BackupKeychainV2Decryptor
from dykcrpytor.keychain.decryptor import KeychainDecryptor
from dykcrpytor.keychain.sqlite_export import export_decrypted_to_sqlite


class KeychainFormat(str, Enum):
    SQLITE = "sqlite"
    BACKUP_V2_PLIST = "backup_keychain_v2"


ProgressCallback = Optional[Callable[[str, Optional[int]], None]]


def detect_keychain_format(path: str | Path) -> KeychainFormat | None:
    path = Path(path)
    if not path.is_file():
        return None
    if path.suffix.lower() == ".plist":
        return KeychainFormat.BACKUP_V2_PLIST if _looks_like_backup_v2_plist(path) else None
    if _looks_like_backup_v2_plist(path):
        return KeychainFormat.BACKUP_V2_PLIST
    if _looks_like_keychain_sqlite(path):
        return KeychainFormat.SQLITE
    return None


def validate_keychain_file(path: str | Path) -> str | None:
    fmt = detect_keychain_format(path)
    if fmt in (KeychainFormat.BACKUP_V2_PLIST, KeychainFormat.SQLITE):
        return None
    return (
        "Unknown file. Expected keychain SQLite (.db) or "
        "backup_keychain_v2.plist (keychainEntries)."
    )


def create_decryptor(path: str | Path) -> Union[KeychainDecryptor, BackupKeychainV2Decryptor]:
    fmt = detect_keychain_format(path)
    if fmt == KeychainFormat.BACKUP_V2_PLIST:
        return BackupKeychainV2Decryptor(path)
    if fmt == KeychainFormat.SQLITE:
        return KeychainDecryptor(str(path))
    raise ValueError(validate_keychain_file(path) or "Invalid keychain file")


def decrypt_keychain_file(
    path: str | Path,
    progress_callback: ProgressCallback = None,
) -> dict[str, Any]:
    decryptor = create_decryptor(path)
    if progress_callback:
        decryptor.set_progress_callback(progress_callback)
    return decryptor.decrypt()


def export_keychain_to_sqlite(
    source_path: str | Path,
    output_path: str | Path,
    data: dict | None = None,
) -> None:
    if data is not None:
        export_decrypted_to_sqlite(output_path, data)
        return
    decryptor = create_decryptor(source_path)
    if hasattr(decryptor, "export_to_sqlite"):
        decryptor.export_to_sqlite(output_path, None)
    else:
        export_decrypted_to_sqlite(output_path, decryptor.decrypt())


def _looks_like_backup_v2_plist(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            pl = plistlib.load(f)
        if not isinstance(pl, dict):
            return False
        return "keychainEntries" in pl or "classKeyIdxToUnwrappedMetadataClassKey" in pl
    except Exception:
        return False


def _looks_like_keychain_sqlite(path: Path) -> bool:
    try:
        con = sqlite3.connect(str(path))
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cur.fetchall()}
        con.close()
        return {"genp", "inet", "metadatakeys"}.issubset(tables)
    except sqlite3.Error:
        return False
