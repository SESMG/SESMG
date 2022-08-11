#!/bin/bash
echo --------------------------------
echo Building the Virtual Enviroment
echo File path: $(dirname "$0")
echo --------------------------------
cd $(dirname "$0")
python3.9 -m venv $(dirname "$0")
source bin/activate

echo ---------------------------------------------
echo download and install required python packages
echo ---------------------------------------------

brew install cbc
brew install geos
brew install graphviz

bin/python3 setup.py

mv dhnx lib/python3.7/site-packages
mkdir files_deviant_operating_system
mv Linux_installation.sh files_deviant_operating_system
mv Run_SESMG_for_Linux.sh files_deviant_operating_system
mv Windows_installation.cmd files_deviant_operating_system
mv Run_SESMG_for_windows.cmd files_deviant_operating_system

echo ----------------------
echo Installation completed
echo Starting SESMG
echo ----------------------

bin/python3.9 start_script.py
osascript -e 'tell application "Terminal" to quit'
