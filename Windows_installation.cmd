@echo ################################
@echo Building the Virtual Enviroment
@echo File path: %~dp0
@echo ################################

py -3.7 -m venv .
cd Scripts/
start /b activate.bat

@echo #############################################
@echo download and install required python packages
@echo #############################################

pip install "oemof.solph>=0.4"
pip install "openpyxl>=3.0.0"
pip install "oemof.thermal>=0.0.5"

echo CHANGE THIS LINE AFTER PR IS MERGED
pip install git+https://github.com/oemof/feedinlib.git@refs/pull/73/head
pip install "open_fred-cli>=0.0.1"
pip install "basemap>=1.3.0"

echo CHANGE THIS LINE AFTER PR IS MERGED
pip install git+https://github.com/oemof/demandlib.git@refs/pull/51/head
pip install "richardsonpy>=0.2.0"

pip install "graphviz>=0.20"

pip install "scikit-learn-extra>=0.2.0"
pip install "memory-profiler>=0.60.0"

pip install "dhnx>=0.0.2"
pip install "sympy>=1.10.0"
pip install "osmnx>=1.2.0"

pip install "xlsxwriter>=3.0.0"

pip install "seaborn>=0.11.0"

pip install "dash>=2.4.0"
pip install "dash_canvas>=0.1.0"

@echo ######################
@echo Installation completed
@echo Starting SESMG
@echo ######################
cd ..
Scripts\python.exe start_script.py
