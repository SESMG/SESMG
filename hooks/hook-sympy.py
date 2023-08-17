from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('sympy')

datas = collect_data_files('sympy', include_py_files=True)
datas += collect_data_files('mpmath', include_py_files=True)
