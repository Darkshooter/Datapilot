# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['python.py'],
    pathex=[],
    binaries=[],
    datas=[('set_device_time_32bit.py', '.'), ('set_pc_time.py', '.')],
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
splash = Splash(
    'C:\\Program Files (x86)\\IBDS\\DataPilot\\img\\splashscreen.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
    always_on_top=True,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    splash,
    splash.binaries,
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
