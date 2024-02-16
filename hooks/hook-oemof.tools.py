from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('oemof.tools')

datas = collect_data_files('oemof.tools', include_py_files=True)

