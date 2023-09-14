#!/bin/bash
echo --------------------------------
echo Starting the Virtual Enviroment
echo File path: "$(dirname "$0")"
echo --------------------------------
cd "$(dirname "$0")"
cd ..
source venv/bin/activate
venv/bin/python3 -m streamlit run "program_files/GUI_st/1_Main_Application.py"
