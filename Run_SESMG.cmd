@echo ################################
@echo Starting the Virtual Enviroment
@echo File path: %~dp0
@echo ################################

python -m venv .
cd Scripts
start /b activate.bat
cd ..
%~dp0Scripts\python.exe program_files/GUI.py