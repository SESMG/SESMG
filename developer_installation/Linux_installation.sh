#!/bin/bash

echo --------------------------------
echo Installation started
echo File path: ~/program_files
echo --------------------------------

echo --------------------------------
echo Install the python pip installer
echo --------------------------------
chmod a+rwx "$(pwd)"
pip3 install virtualenv

echo "Enter your Python Version here: "
read PYVERSION

cd "$(pwd)"
cd ..
virtualenv -p /usr/bin/python$PYVERSION venv
. venv/bin/activate

echo ---------------------------------------------
echo download and install required python packages
echo ---------------------------------------------


venv/bin/pip3 install -r ./requirements.txt

echo ----------------------
echo Installation completed
echo ----------------------
venv/bin/python3 -m streamlit run "program_files/GUI_st/1_Main_Application.py"

exit

