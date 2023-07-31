@echo ################################
@echo Building the Virtual Enviroment
@echo File path: "%~dp0"
@echo ################################

@echo off
set /p PYVERSION="Enter your Python Version here:"
cd "%~dp0 "
cd ..
py -%PYVERSION% -m venv venv

cd venv/Scripts/
start /b activate.bat

mkdir %userprofile%\.streamlit
move ..\.streamlit\credentials.toml %userprofile%\.streamlit\credentials.toml

pip install pipwin
pipwin install gdal
pipwin install fiona

@echo #############################################
@echo download and install required python packages
@echo #############################################

pip install -r ../requirements.txt

@echo ######################
@echo Installation completed
@echo Starting SESMG
@echo ######################
cd ..
cd ..
venv\Scripts\python.exe -m streamlit run "program_files/GUI_st/1_Main_Application.py"

