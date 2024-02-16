from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('openpyxl')

datas = collect_data_files('openpyxl', include_py_files=True)
