from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('graphviz')

datas = collect_data_files('graphviz', include_py_files=True)
