# -*- mode: python ; coding: utf-8 -*-

def get_version():
    version_file = os.path.join(os.getcwd(), 'version.txt')
    with open(version_file, 'r') as f:
        return f.read().strip()

block_cipher = None

files = [
    ('img/github_icon.png', 'img'),
    ('version.txt', '.')
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=files,
    hiddenimports=[],
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
    name=f'VCTheme_{get_version()}',
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
)
