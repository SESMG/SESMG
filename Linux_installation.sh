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

echo "Enter yout Python Version here: "
read PYVERSION

virtualenv -p /usr/bin/python$PYVERSION "$(pwd)"
. bin/activate

echo ---------------------------------------------
echo download and install required python packages
echo ---------------------------------------------


pip3 install -r ./requirements.txt

sudo mkdir files_deviant_operating_system
sudo mv MacOS_installation.command files_deviant_operating_system
sudo mv Run_SESMG_for_macos.command files_deviant_operating_system
sudo mv Windows_installation.cmd files_deviant_operating_system
sudo mv Run_SESMG_for_windows.cmd files_deviant_operating_system

echo ----------------------
echo Installation completed
echo ----------------------

exit

