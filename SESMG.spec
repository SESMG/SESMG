# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

datas = [('program_files', 'program_files'), ('lib/python3.9/site-packages/dhnx', 'dhnx')]
datas += copy_metadata('streamlit')


block_cipher = None


a = Analysis(
    ['start_script.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['numbers', 'pyutilib', 'pyutilib.component.config', 'pyomo', 'pyomo.environ', 'pyutilib.component.app', 'pyutilib.common', 'pyutilib.component.executables', 'pyutilib.component.loader', 'pyutilib.dev', 'pyutilib.dev', 'pyutilib.enum', 'pyutilib.math', 'pyutilib.misc', 'pyutilib.ply', 'pyutilib.pyro', 'pyutilib.R', 'pyutilib.services', 'pyutilib.subprocess', 'pyutilib.svn', 'pyutilib.th', 'pyutilib.virtualenv', 'pyutilib.workflow', 'pyomo.age', 'pyomo.bilevel', 'pyomo.bilevel.plugins', 'pyomo.core', 'pyomo.core.plugins', 'pyomo.dae', 'pyomo.dae.plugins', 'pyomo.gdp', 'pyomo.gdp.plugins', 'pyomo.neos', 'pyomo.neos.plugins', 'pyomo.opt', 'pyomo.opt.plugins', 'pyomo.pysp', 'pyomo.pysp.plugins', 'pyomo.solvers.plugins', 'pyomo.solvers', 'pyomo.checker', 'pyomo.checker.plugins', 'pyomo.contrib', 'pyomo.contrib.plugins', 'pyomo.dataportal', 'pyomo.dataportal.plugins', 'pyomo.duality', 'pyomo.duality.plugins', 'pyomo.kernel', 'pyomo.kernel.plugins', 'pyomo.mpec', 'pyomo.mpec.plugins', 'pyomo.network', 'pyomo.network.plugins', 'pyomo.repn', 'pyomo.repn.plugins', 'pyomo.scripting', 'pyomo.scripting.plugins', 'pyomo.util', 'pyomo.util.plugins', 'pyomo.common', 'pyomo.common.plugins', 'sys', 'logging', 're', 'sys', 'pyutilib.services', 'pyomo.core.expr.numvalue', 'pyomo.core.expr.numvalue', 'pyomo.solvers.plugins.solvers.direct_solver', 'pyomo.solvers.plugins.solvers.direct_or_persistent_solver', 'pyomo.core.kernel.component_set', 'pyomo.core.kernel.component_map', 'pyomo.opt.results.results_', 'pyomo.opt.results.solution', 'pyomo.opt.results.solver', 'pyomo.opt.base', 'pyomo.core.base.suffix', 'pyomo.core.base.var', 'pyomo.core.base.PyomoModel', 'pyomo.solvers.plugins.solvers.persistent_solver', 'pyomo.opt.base.problem', 'pyomo.opt.base.convert', 'pyomo.opt.base.formats', 'pyomo.opt.base.results', 'pyomo.core.base.block', 'pyomo.core.kernel.block', 'pyomo.core.kernel.suffix', 'pyomo.solvers.plugins.solvers.CBCplugin', 'pyomo.repn.util'],
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
    name='SESMG',
    debug=False,
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
    icon=None,
    bundle_identifier=None,
)
