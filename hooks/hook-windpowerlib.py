from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('windpowerlib')

datas = collect_data_files('windpowerlib', include_py_files=True)
