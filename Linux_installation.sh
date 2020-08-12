#!/bin/bash

echo ##############################
echo Installation started 
echo File path: %dp0program_files
echo ##############################

echo #########################
echo Install the python pip installer
echo #########################
sudo apt update 
sudo apt install python3-pip

echo #######################################
echo download and install required python packages 
echo #######################################

pip3 install pandas==0.25.3
pip3 install numpy==1.17.4
pip3 install tables==3.5.2
pip3 install openpyxl==3.0.0
pip3 install pyutilib==5.8
sudo apt-get install python3-tk

pip3 install oemof==0.3.2
pip3 install demandlib==0.1.6
pip3 install pvlib==0.7.1
pip3 install feedinlib==0.0.12
pip3 install richardsonpy==0.2.1
pip3 install dash==1.7.0
pip3 install dash_canvas==0.1.0
pip3 install pydot==1.4.1
pip3 install graphviz==0.13.2

echo ###################
echo Installation completed 
echo ###################
exit


