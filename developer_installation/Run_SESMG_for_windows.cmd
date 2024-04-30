@echo ################################
@echo Starting the Virtual Enviroment
@echo File path: "%~dp0"
@echo ################################

<<<<<<< HEAD
cd "%~dp0"
cd ..
=======
cd "%~dp0"
cd ..
>>>>>>> master
cd venv\Scripts
start /b activate.bat
cd ..
cd ..
<<<<<<< HEAD
cd ..
=======
>>>>>>> master
venv\Scripts\python.exe -m streamlit run "program_files/GUI_st/1_Main_Application.py"
