#!/bin/bash
cd "$(pwd)"
cd ..
. venv/bin/activate
python3 -m streamlit run "program_files/GUI_st/1_Main_Application.py"

