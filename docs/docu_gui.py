import subprocess
import os

subprocess.call("streamlit run {}".format(
                os.path.dirname(__file__) +
                "/program_files/GUI_st/1_Main_Application.py"), shell=True)