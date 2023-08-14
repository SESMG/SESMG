from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('oemof.solph')

datas = collect_data_files('oemof.solph', include_py_files=True)
datas += collect_data_files('pyomo', include_py_files=True)
datas += collect_data_files('pyutilib', include_py_files=True)
datas += collect_data_files('ply', include_py_files=True)
