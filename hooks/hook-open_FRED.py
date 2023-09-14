from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('open_FRED')

datas = collect_data_files('open_FRED', include_py_files=True)
datas += collect_data_files('alembic', include_py_files=True)
datas += collect_data_files('mako', include_py_files=True)
datas += collect_data_files('geoalchemy2', include_py_files=True)
datas += collect_data_files('markupsafe', include_py_files=True)
