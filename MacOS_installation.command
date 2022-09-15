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
brew install postgresql
brew install geos

bin/pip3 install numpy==1.17.4
bin/pip3 install tables==3.5.2
bin/pip3 install openpyxl==3.0.0

bin/pip3 install oemof.thermal==0.0.3
bin/pip3 install demandlib==0.1.6
bin/pip3 install pvlib==0.7.1
echo bin/pip3 install feedinlib==0.0.12
bin/pip3 install oedialect==0.0.10
bin/pip3 install sqlalchemy==1.3.16
bin/pip3 install open_fred-cli
bin/pip3 install richardsonpy==0.2.1
bin/pip3 install dash==1.7.0
bin/pip3 install dash_canvas==0.1.0
bin/pip3 install pydot==1.4.1
bin/pip3 install graphviz==0.13.2
bin/pip3 install xlrd==1.2.0
bin/pip3 install Pyomo==5.7.1
bin/pip3 install basemap==1.3.3
bin/pip3 install xlsxwriter
bin/pip3 install dhnx
bin/pip3 install pyproj
bin/pip3 install sympy
bin/pip3 install numpy==1.17.4
bin/pip3 install memory-profiler
bin/pip3 install scikit-learn-extra
bin/pip3 install seaborn
bin/pip3 install matplotlib
bin/pip3 install oemof.solph==0.4.1
bin/pip3 install numpy==1.17.4
bin/pip3 install werkzeug==2.0.3
bin/pip3 install flask==2.1.3
bin/pip3 install pandas==1.0.0
brew install graphviz
mv feedinlib lib/python3.7/site-packages
mv windpowerlib lib/python3.7/site-packages
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

bin/python3.7 start_script.py
osascript -e 'tell application "Terminal" to quit'
