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

pip install pandas==0.25.3
pip install numpy==1.17.4
pip install tables==3.5.2
pip install openpyxl==3.0.0

pip install https://github.com/oemof/oemof-solph/archive/master.zip
pip install oemof.thermal==0.0.3
pip install demandlib==0.1.6
pip install pvlib==0.7.1
pip install feedinlib==0.0.12
pip install richardsonpy==0.2.1
pip install dash==1.7.0
pip install dash_canvas==0.1.0
pip install pydot==1.4.1
pip install graphviz==0.13.2
pip install xlrd==1.2.0
pip install Pyomo==5.7.1
pip install xlsxwriter
pip install demandlib --upgrade

@echo ######################
@echo Installation completed
@echo Starting SESMG
@echo ######################
cd ..
Scripts\python.exe program_files/GUI.py
