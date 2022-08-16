#!/bin/bash
echo --------------------------------
echo Building the Virtual Enviroment
echo File path: $(dirname "$0")
echo --------------------------------
cd $(dirname "$0")
python3.7 -m venv $(dirname "$0")
source bin/activate

echo ---------------------------------------------
echo download and install required python packages
echo ---------------------------------------------

brew install cbc
pip3 install -r requirements.txt
brew install graphviz
mv feedinlib lib/python3.7/site-packages
mv windpowerlib lib/python3.7/site-packages
echo ----------------------
echo Installation completed
echo Starting SESMG
echo ----------------------

bin/python3.7 program_files/GUI.py
osascript -e 'tell application "Terminal" to quit'
