# Parse keychain DER/ASN.1 into display fields (backup plist).

from __future__ import annotations

import base64
import re
import xml.etree.ElementTree as ET
from typing import Any

from pyasn1.codec.der.decoder import decode as der_decode

NOT_FOUND = "Not Found"
SEQUENCE_SUFFIX = "Sequence:"
SEQUENCE_OF_SUFFIX = "SequenceOf:"

FIELD_MAP = {
    "cdat": "Create_Date",
    "mdat": "Modified_Date",
    "svce": "Service",
    "agrp": "accessGroup",
    "acct": "Account",
    "persistref": "Persistref",
    "SecAccessControl": "SecAccessControl",
    "gena": "generic_attribute",
    "sync": "Sync",
    "sha1": "Sha1",
    "UUID": "UUID",
}


def decode_b64(data: Any) -> bytes:
    if not data:
        return b""
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return base64.b64decode("".join(data.split()))
    return b""


def asn1_pretty(der_data: bytes) -> str:
    if not der_data:
        return ""
    obj, _ = der_decode(der_data)
    if hasattr(obj, "prettyPrint"):
        return obj.prettyPrint()
    return str(obj)


def parse_secret_fields(der_data: bytes) -> dict[str, Any]:
    asn1_str = asn1_pretty(der_data)
    field1_match = re.search(r"field-1\s*=\s*([^\n]+)", asn1_str, re.IGNORECASE)
    raw_field1 = field1_match.group(1).strip() if field1_match else NOT_FOUND
    key, data = NOT_FOUND, None
    if raw_field1.startswith("0x62706c6973743030"):
        data = raw_field1
    elif raw_field1.startswith(
        "0x3c3f786d6c2076657273696f6e3d22312e302220656e636f64696e673d225554462d38223f3e"
    ):
        key = _parse_xml_key_hex(raw_field1[2:])
        data = raw_field1
    elif raw_field1.startswith("0x3083038cd1020108316a30120c094f5356657273696f6e0c"):
        key = NOT_FOUND
    else:
        key = raw_field1
    tamper_match = re.search(r"TamperCheck\s+([^\n]+)", asn1_str, re.IGNORECASE)
    tampercheck = tamper_match.group(1).strip() if tamper_match else NOT_FOUND
    return {"tampercheck": tampercheck, "key": key, "data": data}


def parse_metadata_fields(der_data: bytes) -> dict[str, Any]:
    asn1_str = asn1_pretty(der_data)
    metadata: dict[str, Any] = {}
    for abbr, full_name in FIELD_MAP.items():
        val = _find_field_value(abbr, asn1_str)
        if val != NOT_FOUND and val.endswith(SEQUENCE_SUFFIX):
            val = val[: -len(SEQUENCE_SUFFIX)].strip()
        metadata[full_name] = val
    return metadata


def _parse_xml_key_hex(hex_str: str) -> str:
    try:
        xml_str = bytes.fromhex(hex_str).decode("utf-8")
        data_element = ET.fromstring(xml_str).find(".//data")
        if data_element is not None and data_element.text:
            return data_element.text.strip()
    except Exception:
        pass
    return NOT_FOUND


def _find_field_value(abbr: str, asn1_str: str) -> str:
    pattern = r"field-0\s*=?\s*" + re.escape(abbr) + r"\s*(?:\r?\n\s*)+field-1\s*=?\s*(.+)"
    m = re.search(pattern, asn1_str, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    pattern_line = r"\b" + re.escape(abbr) + r"\b\s+(.*)"
    for line in asn1_str.splitlines():
        m_line = re.search(pattern_line, line, re.IGNORECASE)
        if m_line:
            return m_line.group(1).strip()
    return NOT_FOUND


def clean_display_value(val: Any) -> Any:
    if not isinstance(val, str):
        return val
    if val.startswith("0x"):
        val = val[2:]
    if val.endswith(SEQUENCE_OF_SUFFIX):
        val = val[: -len(SEQUENCE_OF_SUFFIX)].strip()
    elif val.endswith(SEQUENCE_SUFFIX):
        val = val[: -len(SEQUENCE_SUFFIX)].strip()
    return val


def format_keychain_timestamp(ts: str) -> str:
    import datetime

    try:
        ts = ts.rstrip("Z")
        if "." in ts:
            main_part, frac_part = ts.split(".", 1)
            ts = f"{main_part}.{frac_part[:6].ljust(6, '0')}"
            dt = datetime.datetime.strptime(ts, "%Y%m%d%H%M%S.%f")
        else:
            dt = datetime.datetime.strptime(ts, "%Y%m%d%H%M%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S (UTC)")
    except Exception:
        return ts
