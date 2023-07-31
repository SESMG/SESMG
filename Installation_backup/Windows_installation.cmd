@echo ################################
@echo Building the Virtual Enviroment
@echo File path: "%~dp0"
@echo ################################

@echo off
set /p PYVERSION="Enter your Python Version here:"

py -%PYVERSION% -m venv "%~dp0 "

cd Scripts/
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

mkdir "%~dp0 "/files_deviant_operating_system
move "%~dp0 "/MacOS_installation.command "%~dp0 "/files_deviant_operating_system\MacOS_installation.command
move "%~dp0 "/Run_SESMG_for_macos.command "%~dp0 "/files_deviant_operating_system\Run_SESMG_for_macos.command
move "%~dp0 "/Linux_installation.sh "%~dp0 "/files_deviant_operating_system\Linux_installation.sh
move "%~dp0 "/Run_SESMG_for_Linux.sh "%~dp0 "/files_deviant_operating_system\Run_SESMG_for_Linux.sh


@echo ######################
@echo Installation completed
@echo Starting SESMG
@echo ######################
cd ..
Scripts\python.exe -m streamlit run "program_files/GUI_st/1_Main_Application.py"

