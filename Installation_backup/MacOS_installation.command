#!/bin/bash
echo --------------------------------
echo Building the Virtual Enviroment
echo File path: "$(dirname "$0")"
echo --------------------------------
cd "$(dirname "$0")"
cd ..

echo "Enter your Python Version here:"
read PYVERSION

python$PYVERSION -m venv .
source bin/activate

echo ---------------------------------------------
echo download and install required python packages
echo ---------------------------------------------

brew install cbc
brew install geos
brew install graphviz
brew install postgresql

../bin/pip3 install -r requirements.txt

echo ----------------------
echo Installation completed
echo Starting SESMG
echo ----------------------

../bin/python$PYVERSION -m streamlit run "program_files/GUI_st/1_Main_Application.py"
osascript -e 'tell application "Terminal" to quit'
