from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('oemof.db')

datas = collect_data_files('oemof.db', include_py_files=True)
datas += collect_data_files('keyring', include_py_files=True)
