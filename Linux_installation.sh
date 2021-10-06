#!/bin/bash

echo --------------------------------
echo Installation started
echo File path: ~/program_files
echo --------------------------------

echo --------------------------------
echo Install the python pip installer
echo --------------------------------
chmod a+rwx $(pwd)
pip3 install virtualenv
virtualenv -p /usr/bin/python3.7 $(pwd)
. bin/activate

echo ---------------------------------------------
echo download and install required python packages
echo ---------------------------------------------

pip3 install pandas==0.25.3
pip3 install numpy==1.17.4
pip3 install tables==3.5.2
pip3 install openpyxl==3.0.0

pip3 install https://github.com/oemof/oemof-solph/archive/master.zip
pip3 install oemof.thermal==0.0.3
pip3 install demandlib==0.1.6
pip3 install pvlib==0.7.1
echo pip3 install feedinlib==0.0.12
pip3 install richardsonpy==0.2.1
pip3 install dash==1.7.0
pip3 install dash_canvas==0.1.0
pip3 install pydot==1.4.1
pip3 install graphviz==0.13.2
pip3 install xlrd==1.2.0
pip3 install tables
pip3 install Pyomo==5.7.1
pip3 install xlsxwriter
pip3 install dhnx 
pip3 install pyproj 
pip3 install sympy
sudo mv feedinlib lib/python3.7/site-packages
sudo mv windpowerlib lib/python3.7/site-packages
echo ----------------------
echo Installation completed
echo ----------------------

exit

