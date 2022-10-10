#!/bin/bash
echo --------------------------------
echo Starting the Virtual Enviroment
echo File path: $(dirname "$0")
echo --------------------------------
cd $(dirname "$0")
source bin/activate
bin/python3 start_script.py -s
