from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('oemof.thermal')

datas = collect_data_files('oemof.thermal', include_py_files=True)
