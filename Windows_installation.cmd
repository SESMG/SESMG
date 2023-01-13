@echo ################################
@echo Building the Virtual Enviroment
@echo File path: %~dp0
@echo ################################

@echo off
set /p PYVERSION="Enter your Python Version here:"

py -%PYVERSION% -m venv .

cd Scripts/
start /b activate.bat

pip install pipwin
pipwin install gdal
pipwin install fiona

@echo #############################################
@echo download and install required python packages
@echo #############################################

pip install -r ..\requirements.txt

mkdir ..\files_deviant_operating_system
move ..\MacOS_installation.command ..\files_deviant_operating_system\MacOS_installation.command
move ..\Run_SESMG_for_macos.command ..\files_deviant_operating_system\Run_SESMG_for_macos.command
move ..\Linux_installation.sh ..\files_deviant_operating_system\Linux_installation.sh
move ..\Run_SESMG_for_Linux.sh ..\files_deviant_operating_system\Run_SESMG_for_Linux.sh


@echo ######################
@echo Installation completed
@echo Starting SESMG
@echo ######################
cd ..
Scripts\python.exe start_script.py
