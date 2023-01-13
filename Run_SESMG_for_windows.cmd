@echo ################################
@echo Starting the Virtual Enviroment
@echo File path: %~dp0
@echo ################################

cd Scripts
start /b activate.bat
cd ..
Scripts\python.exe start_script.py
