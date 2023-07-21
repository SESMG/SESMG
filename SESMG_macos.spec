# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

datas = [('lib/Python3.9/site-packages/streamlit', 'streamlit'),
         ('program_files', 'program_files'),
         ('lib/Python3.9/site-packages/dhnx/components.csv', 'dhnx'),
         ('lib/python3.9/site-packages/dhnx/component_attrs', 'dhnx/component_attrs'),
         ('lib/python3.9/site-packages/demandlib/bdew/bdew_data', 'demandlib/bdew/bdew_data'),
         ('lib/python3.9/site-packages/pvlib/data', 'pvlib/data'),
         ('lib/python3.9/site-packages/pyomo', 'pyomo'),
         ('lib/python3.9/site-packages/st_aggrid/frontend/build', 'st_aggrid/frontend/build'),
         ('/usr/local/Cellar/graphviz/*/lib/graphviz/config6', 'graphviz'),
         ('results', 'results'),
         ('docs', 'docs'),
         ('README.md', '.'),
         ]
datas += copy_metadata('streamlit')


block_cipher = None


a = Analysis(
    ['program_files/start_script.py'],
    pathex=[],
    binaries=[('/usr/local/bin/dot', '.'),
              ('/usr/local/bin/nop', '.'),
              ('/usr/local/Cellar/graphviz/*/lib/graphviz/libgvplugin_pango.6.dylib', 'graphviz'),
              ('/usr/local/Cellar/graphviz/*/lib/graphviz/libgvplugin_core.6.dylib', 'graphviz'),
              ('/usr/local/Cellar/graphviz/*/lib/graphviz/libgvplugin_dot_layout.6.dylib', 'graphviz'),
              ('/usr/local/Cellar/graphviz/*/lib/graphviz/libgvplugin_core.6.dylib', 'graphviz'),
              ('/usr/local/Cellar/graphviz/*/lib/graphviz/libgvplugin_gd.6.dylib', 'graphviz'),
              ('/usr/local/Cellar/graphviz/*/lib/graphviz/libgvplugin_neato_layout.6.dylib', 'graphviz'),
              ('/usr/local/Cellar/graphviz/*/lib/graphviz/libgvplugin_quartz.6.dylib', 'graphviz'),
              ('/usr/local/Cellar/graphviz/*/lib/graphviz/libgvplugin_visio.6.dylib', 'graphviz'),
              ('/usr/local/Cellar/graphviz/*/lib/graphviz/libgvplugin_webp.6.dylib', 'graphviz'),],
    datas=datas,
    hiddenimports=["program_files",
                   "numbers",
                   "pyomo",
                   "pyomo.environ",
                   "pyomo.age",
                   "pyomo.core",
                   "pyomo.core.plugins",
                   "pyomo.core.kernel.component_set",
                   "pyomo.core.kernel.component_map",
                   "pyomo.core.base.suffix",
                   "pyomo.core.base.var",
                   "pyomo.core.base.PyomoModel",
                   "pyomo.core.base.block",
                   "pyomo.core.kernel.block",
                   "pyomo.core.kernel.suffix",
                   "pyomo.common",
                   "pyomo.common.plugins",
                   "pyomo.opt",
                   'pyomo.opt.plugins',
                   "pyomo.opt.results.results_",
                   "pyomo.opt.results.solution",
                   "pyomo.opt.results.solver",
                   "pyomo.opt.base",
                   'pyomo.opt.base.solvers',
                   "pyomo.opt.base.problem",
                   "pyomo.opt.base.convert",
                   "pyomo.opt.base.formats",
                   "pyomo.opt.base.results",
                   "pyomo.contrib",
                   "pyomo.contrib.plugins",
                   'pyomo.dataportal',
                   'pyomo.dataportal.plugins',
                   'pyomo.duality',
                   'pyomo.duality.plugins',
                   'pyomo.checker',
                   'pyomo.checker.plugins',
                   'pyomo.repn',
                   'pyomo.repn.plugins',
                   'pyomo.repn.util',
                   'pyomo.pysp',
                   'pyomo.pysp.plugins',
                   'pyomo.neos',
                   'pyomo.neos.plugins',
                   "pyomo.gdp",
                   'pyomo.gdp.plugins',
                   'pyomo.mpec',
                   'pyomo.mpec.plugins',
                   'pyomo.dae',
                   'pyomo.dae.plugins',
                   'pyomo.bilevel',
                   'pyomo.bilevel.plugins',
                   'pyomo.scripting',
                   'pyomo.scripting.plugins',
                   'pyomo.network',
                   'pyomo.network.plugins',
                   "pyomo.kernel",
                   "pyomo.kernel.plugins",
                   'gurobipy',
                   'pyomo.solvers.plugins',
                   'pyomo.solvers.plugins.solvers',
                   'pyomo.solvers.plugins.solvers.direct_solver',
                   'pyomo.solvers.plugins.solvers.direct_or_persistent_solver',
                   "pyomo.solvers.plugins.solvers.persistent_solver",
                   "pyomo.solvers.plugins.solvers.CBCplugin",
                   "pyomo.solvers.plugins.solvers.GUROBI_RUN",
                   'pyomo.solvers',
                   'pyomo.util',
                   'pyomo.util.plugins',
                   "pyomo.core.expr.numvalue",
                   'st_aggrid'],
    hookspath=["."],
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
