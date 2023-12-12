from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('feedinlib')

datas = collect_data_files('feedinlib', include_py_files=True)
datas += collect_data_files('xarray', include_py_files=True)
datas += collect_data_files('cdsapi', include_py_files=True)
datas += collect_data_files('tqdm', include_py_files=True)
datas += collect_data_files('oedialect', include_py_files=True)
datas += collect_data_files('sqlalchemy', include_py_files=True)
