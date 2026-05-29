# AES-GCM decrypt for NSKeyedArchiver SF* wrapped blobs.

from __future__ import annotations

from io import BytesIO

from Crypto.Cipher import AES

from dykcrpytor.vendor import ccl_bplist


def decrypt_sf_encrypted_blob(encrypted_blob: bytes, key: bytes) -> bytes:
    if not encrypted_blob or not key:
        return b""
    plist = ccl_bplist.load(BytesIO(encrypted_blob))
    deserialized = ccl_bplist.deserialise_NsKeyedArchiver(plist, parse_whole_structure=True)
    root = deserialized["root"]
    cipher = AES.new(key[:32], AES.MODE_GCM, root["SFInitializationVector"])
    return cipher.decrypt_and_verify(root["SFCiphertext"], root["SFAuthenticationCode"])
