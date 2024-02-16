from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('pyproj')

datas = collect_data_files('pyproj', include_py_files=True)
