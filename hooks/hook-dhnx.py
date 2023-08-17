from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('dhnx')

datas = collect_data_files('dhnx', include_py_files=True)
datas += collect_data_files('addict', include_py_files=True)
datas += collect_data_files('matplotlib', include_py_files=True)
datas += collect_data_files('importlib_resources', include_py_files=True)
datas += collect_data_files('mpl_toolkits', include_py_files=True)
datas += collect_data_files('folium', include_py_files=True)
datas += collect_data_files('branca', include_py_files=True)
