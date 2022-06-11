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
brew install postgresql
brew install geos
brew install Proj
brew install graphviz

bin/pip3 install "oemof.solph>=0.4"
bin/pip3 install "openpyxl>=3.0.0"
bin/pip3 install "oemof.thermal>=0.0.5"

echo CHANGE THIS LINE AFTER PR IS MERGED
bin/pip3 install git+https://github.com/oemof/feedinlib.git@refs/pull/73/head
bin/pip3 install "open_fred-cli>=0.0.1"
bin/pip3 install "basemap>=1.3.0"

echo CHANGE THIS LINE AFTER PR IS MERGED
bin/pip3 install git+https://github.com/oemof/demandlib.git@refs/pull/51/head
bin/pip3 install "richardsonpy>=0.2.0"

bin/pip3 install "graphviz>=0.20"

bin/pip3 install "scikit-learn-extra>=0.2.0"
bin/pip3 install "memory-profiler>=0.60.0"

bin/pip3 install "dhnx>=0.0.2"
bin/pip3 install "sympy>=1.10.0"
bin/pip3 install "osmnx>=1.2.0"

bin/pip3 install "xlsxwriter>=3.0.0"

bin/pip3 install "seaborn>=0.11.0"

bin/pip3 install "dash>=2.4.0"
bin/pip3 install "dash_canvas>=0.1.0"

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
