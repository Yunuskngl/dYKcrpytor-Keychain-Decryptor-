# -*- mode: python ; coding: utf-8 -*-
# macOS app bundle — output: dist/dYKcrpytor.app

import os

block_cipher = None

SPEC_ROOT = os.path.dirname(os.path.abspath(SPEC))
ICON_ICNS = os.path.join(SPEC_ROOT, "assets", "icons", "dYKcrpytor.icns")
ICON_DATAS = [
    (os.path.join(SPEC_ROOT, "assets", "icons", "access-keys.png"), "assets/icons"),
]

HIDDEN = [
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
    "PyQt6",
    "PyQt6.QtCore",
    "PyQt6.QtGui",
    "PyQt6.QtWidgets",
]

a = Analysis(
    ["run_gui.py"],
    pathex=[SPEC_ROOT],
    binaries=[],
    datas=ICON_DATAS,
    hiddenimports=HIDDEN,
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
    [],
    exclude_binaries=True,
    name="dYKcrpytor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="dYKcrpytor",
)

app = BUNDLE(
    coll,
    name="dYKcrpytor.app",
    icon=ICON_ICNS if os.path.isfile(ICON_ICNS) else None,
    bundle_identifier="local.dykcrpytor.gui",
    info_plist={
        "CFBundleName": "dYKcrpytor",
        "CFBundleDisplayName": "dYKcrpytor",
        "NSPrincipalClass": "NSApplication",
        "NSHighResolutionCapable": True,
    },
)
