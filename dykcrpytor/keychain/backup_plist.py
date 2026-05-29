# backup_keychain_v2.plist — pre-unwrapped keys, two-stage AES-GCM metadata.

from __future__ import annotations

import plistlib
from pathlib import Path
from typing import Any, Callable, Optional

from dykcrpytor.keychain.aes_payload import decrypt_sf_encrypted_blob
from dykcrpytor.keychain.asn1_fields import (
    FIELD_MAP,
    NOT_FOUND,
    clean_display_value,
    decode_b64,
    format_keychain_timestamp,
    parse_metadata_fields,
    parse_secret_fields,
)
from dykcrpytor.keychain.sqlite_export import export_decrypted_to_sqlite


ProgressCallback = Optional[Callable[[str, Optional[int]], None]]


class BackupKeychainV2Decryptor:
    def __init__(self, plist_path: str | Path):
        self.plist_path = Path(plist_path)
        self.progress_callback: ProgressCallback = None

    def set_progress_callback(self, callback: ProgressCallback) -> None:
        self.progress_callback = callback

    def _progress(self, message: str, value: Optional[int] = None) -> None:
        if self.progress_callback:
            self.progress_callback(message, value)

    def decrypt(self) -> dict[str, list[dict]]:
        if not self.plist_path.is_file():
            raise IOError(f"Plist bulunamadı: {self.plist_path}")

        self._progress("backup_keychain_v2.plist okunuyor…", 0)
        with open(self.plist_path, "rb") as f:
            backup = plistlib.load(f)

        metadata_mapping = backup.get("classKeyIdxToUnwrappedMetadataClassKey") or {}
        entries = backup.get("keychainEntries") or []
        if not isinstance(entries, list):
            raise ValueError("keychainEntries listesi bekleniyor")

        total = max(len(entries), 1)
        records: list[dict] = []

        for idx, entry in enumerate(entries, start=1):
            if not isinstance(entry, dict):
                continue
            pct = 10 + int(85 * idx / total)
            self._progress(f"Kayıt {idx}/{len(entries)} çözülüyor…", pct)
            row = self._decrypt_entry(idx, entry, metadata_mapping)
            if row:
                records.append(row)

        self._progress("Tamamlandı!", 100)
        return {"genp": records, "inet": [], "source": "backup_keychain_v2"}

    def _decrypt_entry(self, idx: int, entry: dict, metadata_mapping: dict) -> dict | None:
        try:
            class_key_idx = str(entry.get("classKeyIdx", ""))
            mapping_key = decode_b64(metadata_mapping.get(class_key_idx))

            secret_der = self._decrypt_secret(entry.get("data") or {})
            meta_der = self._decrypt_metadata(entry.get("metadata") or {}, mapping_key)

            secret_fields = parse_secret_fields(secret_der) if secret_der else {}
            meta_fields = parse_metadata_fields(meta_der) if meta_der else {}

            combined = {**secret_fields, **meta_fields}
            for k, v in list(combined.items()):
                combined[k] = clean_display_value(v)
            for date_key in ("Create_Date", "Modified_Date"):
                if date_key in combined and combined[date_key] not in (NOT_FOUND, None, ""):
                    combined[date_key] = format_keychain_timestamp(str(combined[date_key]))

            row = _base_row_template(idx)
            row["classKeyIdx"] = class_key_idx
            row["version"] = entry.get("version")
            for key in row:
                if key in combined and key not in ("entry",):
                    row[key] = combined[key]
            return row
        except Exception:
            return _base_row_template(idx)

    def _decrypt_secret(self, data_field: dict) -> bytes:
        aes_key = decode_b64(data_field.get("unwrappedKey"))[:32]
        ciphertext = decode_b64(data_field.get("ciphertext"))
        if not aes_key or not ciphertext:
            return b""
        return decrypt_sf_encrypted_blob(ciphertext, aes_key)

    def _decrypt_metadata(self, metadata_field: dict, mapping_key: bytes) -> bytes:
        wrapped = decode_b64(metadata_field.get("wrappedKey"))
        cipher_blob = decode_b64(metadata_field.get("ciphertext"))
        if not cipher_blob:
            return b""
        metadata_key = b""
        if wrapped and mapping_key:
            try:
                metadata_key = decrypt_sf_encrypted_blob(wrapped, mapping_key[:32])
            except Exception:
                metadata_key = b""
        if not metadata_key:
            return b""
        return decrypt_sf_encrypted_blob(cipher_blob, metadata_key[:32])

    def export_to_sqlite(self, output_path: str | Path, data: dict | None = None) -> None:
        if data is None:
            data = self.decrypt()
        export_decrypted_to_sqlite(output_path, data)


def _base_row_template(idx: int) -> dict[str, Any]:
    row: dict[str, Any] = {
        "entry": idx,
        "tampercheck": NOT_FOUND,
        "key": NOT_FOUND,
        "data": None,
        "classKeyIdx": "",
        "version": None,
    }
    for full_name in FIELD_MAP.values():
        row[full_name] = NOT_FOUND
    return row
