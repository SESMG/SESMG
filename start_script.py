import sys
import subprocess
import os

if __name__ == "__main__":
    if sys.platform.startswith("darwin"):
        #command to allow streamlit run
        subprocess.call("streamlit run {}".format(os.path.dirname(__file__) + "/program_files/GUI_st/1_Main_Application.py"), shell=True)
        
        
    elif sys.platform.startswith("linux"):
        #command to allow streamlit run
        subprocess.call("streamlit run {}".format(os.path.dirname(__file__) + "/program_files/GUI_st/1_Main_Application.py"), shell=True)
    else:
        #command to allow streamlit run
        subprocess.call("streamlit run {}".format(os.path.dirname(__file__) + "/program_files/GUI_st/1_Main_Application.py"), shell=True)
