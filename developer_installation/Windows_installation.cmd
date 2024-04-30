@echo ################################
@echo Building the Virtual Enviroment
@echo File path: "%~dp0"
@echo ################################

@echo off
set /p PYVERSION="Enter your Python Version here:"
<<<<<<< HEAD
cd "%~p0 "
=======
cd "%~dp0 "
>>>>>>> master
cd ..
py -%PYVERSION% -m venv venv

cd venv/Scripts/
start /b activate.bat

pip install pipwin
pipwin install gdal
pipwin install fiona

mkdir %userprofile%\.streamlit
<<<<<<< HEAD
move ..\.streamlit\credentials.toml %userprofile%\.streamlit\credentials.toml
=======
move ..\..\.streamlit\credentials.toml %userprofile%\.streamlit\credentials.toml
>>>>>>> master

@echo #############################################
@echo download and install required python packages
@echo #############################################

pip install -r ../../requirements.txt

@echo ######################
@echo Installation completed
@echo Starting SESMG
@echo ######################
cd ..
cd ..
venv\Scripts\python.exe -m streamlit run "program_files/GUI_st/1_Main_Application.py"

