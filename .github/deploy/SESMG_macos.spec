# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

import sys
sys.setrecursionlimit(sys.getrecursionlimit()*5)

datas = [('../../program_files','program_files'),
	 ('../../docs', 'docs'),
         ('../../README.md', '.'),
	 ('../../Lib/python3.9/site-packages/typing_extensions.py', '.'),
	 ('../../Lib/python3.9/site-packages/six.py', '.'),
	 ('../../Lib/python3.9/site-packages/memory_profiler.py', '.'),
         ('../../Lib/python3.9/site-packages/decorator.py', '.'),
	 ('../../Lib/python3.9/site-packages/cycler.py', '.'),
	 ('../../Lib/python3.9/site-packages/decouple.py', '.'),
	 ('../../.streamlit','.streamlit')]
datas += copy_metadata('streamlit')


block_cipher = None


a = Analysis(
    ['../../program_files/start_script.py'],
    pathex=['lib/Python3.9/site-packages'],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=["hooks"],
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
    name='SESMG',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,

)
app = BUNDLE(
    exe,
    name='SESMG.app',
    icon='SESMG.ico',
    bundle_identifier=None,
)