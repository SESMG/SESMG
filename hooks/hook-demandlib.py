from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('demandlib')

datas = collect_data_files('demandlib', include_py_files=True)
