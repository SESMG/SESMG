from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('shapely')

datas = collect_data_files('shapely', include_py_files=True)
