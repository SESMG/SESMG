@echo ################################
@echo Building the Virtual Enviroment
@echo File path: %~dp0
@echo ################################

py -3.9 -m venv .
cd Scripts/
start /b activate.bat

@echo #############################################
@echo download and install required python packages
@echo #############################################

pip install -r requirements.txt

@echo ######################
@echo Installation completed
@echo Starting SESMG
@echo ######################
cd ..
Scripts\python.exe start_script.py
