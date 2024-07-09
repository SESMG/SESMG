@echo ################################
@echo Building the Virtual Environment
@echo File path: "%~dp0"
@echo ################################

@echo off
setlocal enabledelayedexpansion

set "list_of_allowed_versions=3.8,3.9,3.10,3.11"
set /p PYVERSION="Enter your Python Version here:"

set "found=0"
for %%v in (%list_of_allowed_versions%) do (
    if "%%v"=="%PYVERSION%" (
        set "found=1"
        goto :found
    )
)

:found
if "%found%"=="1" (
    echo Version input allowed. Installation will continue.
    
    cd "%~dp0"
    cd ..
    py -%PYVERSION% -m venv venv

    cd venv\Scripts\
    start /b activate.bat

    pip install pipwin
    pipwin install gdal
    pipwin install fiona

    mkdir %userprofile%\.streamlit
    move ..\..\..\.streamlit\credentials.toml %userprofile%\.streamlit\credentials.toml

    @echo #############################################
    @echo Download and install required python packages
    @echo #############################################

    pip install -r ../../requirements.txt

    @echo ######################
    @echo Installation completed
    @echo Starting SESMG
    @echo ######################
    
    cd ..
    cd ..
    venv\Scripts\python.exe -m streamlit run "program_files/GUI_st/1_Main_Application.py"
) else (
    echo Input not in the list of allowed versions. Restart the installation with an allowed version.
    exit /b 1
)