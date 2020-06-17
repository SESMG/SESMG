#!/bin/bash

echo Spreadsheet Energy System Model Generator is beeing started...
cd $(dirname "$0")
pwd
python3 Spreadsheet_Energy_System_Model_Generator.py
python3 Interactive_Results.py
osascript -e 'tell application "Terminal" to quit'