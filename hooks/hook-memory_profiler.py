from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
datas = collect_data_files('psutil', include_py_files=True)
