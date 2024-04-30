# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

import sys
sys.setrecursionlimit(sys.getrecursionlimit()*5)

datas = [('../../program_files','program_files'),
         ('../../docs', 'docs'),
         ('../../README.md', '.'),
	     ('../../lib/python3.9/site-packages/typing_extensions.py', '.'),
	     ('../../lib/python3.9/site-packages/six.py', '.'),
	     ('../../lib/python3.9/site-packages/memory_profiler.py', '.'),
         ('../../lib/python3.9/site-packages/decorator.py', '.'),
	     ('../../lib/python3.9/site-packages/decouple.py', '.')]

datas += copy_metadata('streamlit')

options = [ ('W ignore', None, 'OPTION') ]

block_cipher = None


a = Analysis(
    ['../../program_files/start_script.py'],
    pathex=[],
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

exe = EXE(pyz,
          a.scripts,
          options,
          exclude_binaries=True,
          name='SESMG',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='SESMG')
