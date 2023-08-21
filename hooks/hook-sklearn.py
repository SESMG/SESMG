from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('sklearn')

datas = collect_data_files('sklearn', include_py_files=True)
datas += collect_data_files('sklearn_extra', include_py_files=True)
datas += collect_data_files('joblib', include_py_files=True)
