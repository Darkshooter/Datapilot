# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['python.py'],
    pathex=[],
    binaries=[('C:/Users/user/AppData/Local/Programs/Python/Python38/tcl/tcl8.6', './tcl/tcl8.6'), ('C:/Users/user/AppData/Local/Programs/Python/Python38/tcl/tk8.6', './tcl/tk8.6')],
    datas=[],
    hiddenimports=['numpy.core._dtype_ctypes', 'canmatrix.formats', 'canmatrix.formats.dbc', 'canmatrix.formats.arxml', 'asammdf.blocks.cutils', 'psutil'],
    hookspath=['hooks'],
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
    name='DataPilot',
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
    uac_admin=True,
    icon=['C:\\Program Files\\Airforce_Application\\Airforce\\img\\ico.ico'],
)
