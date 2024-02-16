from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('oemof.network')

datas = collect_data_files('oemof.network', include_py_files=True)
datas += collect_data_files('dill', include_py_files=True)
datas += collect_data_files('networkx', include_py_files=True)
