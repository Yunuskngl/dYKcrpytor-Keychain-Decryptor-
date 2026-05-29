# -*- mode: python ; coding: utf-8 -*-
# Windows one-file exe — output: dist/dYKcrpytor.exe

import os

from PyInstaller.utils.hooks import collect_all

block_cipher = None

SPEC_ROOT = os.path.dirname(os.path.abspath(SPEC))
ICON_ICO = os.path.join(SPEC_ROOT, "assets", "icons", "dYKcrpytor.ico")
ICON_DATAS = [
    (os.path.join(SPEC_ROOT, "assets", "icons", "access-keys.png"), "assets/icons"),
]

qt_datas, qt_binaries, qt_hidden = collect_all("PyQt6")

a = Analysis(
    ["run_gui.py"],
    pathex=[SPEC_ROOT],
    binaries=qt_binaries,
    datas=qt_datas + ICON_DATAS,
    hiddenimports=qt_hidden
    + [
        "dykcrpytor",
        "dykcrpytor.qt_bootstrap",
        "dykcrpytor.app_icon",
        "dykcrpytor.keychain.decryptor",
        "dykcrpytor.keychain.backup_plist",
        "dykcrpytor.keychain.service",
        "dykcrpytor.keychain.aes_payload",
        "dykcrpytor.keychain.asn1_fields",
        "dykcrpytor.keychain.sqlite_export",
        "dykcrpytor.keychain.validate",
        "dykcrpytor.gui.main_window",
        "dykcrpytor.gui.worker",
        "dykcrpytor.gui.models",
        "dykcrpytor.gui.styles",
        "dykcrpytor.proto.SecDbKeychainSerializedItemV7_pb2",
        "dykcrpytor.proto.SecDbKeychainSerializedSecretData_pb2",
        "dykcrpytor.proto.SecDbKeychainSerializedMetadata_pb2",
        "dykcrpytor.proto.SecDbKeychainSerializedAKSWrappedKey_pb2",
        "dykcrpytor.vendor.ccl_bplist",
        "google.protobuf.internal",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="dYKcrpytor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_ICO if os.path.isfile(ICON_ICO) else None,
)
