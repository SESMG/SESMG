from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('xlsxwriter')

datas = collect_data_files('xlsxwriter', include_py_files=True)
