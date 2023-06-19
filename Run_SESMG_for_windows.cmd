@echo ################################
@echo Starting the Virtual Enviroment
@echo File path: "%~dp0"
@echo ################################

cd "%~dp0"/Scripts
start /b activate.bat
cd ..
Scripts\python.exe start_script.py
