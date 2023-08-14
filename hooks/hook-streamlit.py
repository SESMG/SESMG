from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('streamlit')
hiddenimports += collect_submodules('st_aggrid')

datas = collect_data_files('streamlit', include_py_files=True)
datas += collect_data_files('st_aggrid', include_py_files=True)
