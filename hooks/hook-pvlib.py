from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('pvlib')

datas = collect_data_files('pvlib', include_py_files=True)
