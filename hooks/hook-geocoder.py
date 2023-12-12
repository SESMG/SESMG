from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('geocoder')

datas = collect_data_files('geocoder', include_py_files=True)
datas += collect_data_files('ratelim', include_py_files=True)
