@echo ################################
@echo Starting the Virtual Enviroment
@echo File path: "%~dp0"
@echo ################################

cd "%~dp0"/Scripts
start /b activate.bat
cd ..
Scripts\python.exe -m streamlit run "program_files/GUI_st/1_Main_Application.py"
