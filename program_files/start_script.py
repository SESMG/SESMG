import traceback
os.chdir(os.path.dirname(__file__))
import sys
import os
import multiprocessing
multiprocessing.freeze_support()
    
# setting new system path to be able to refer to parent directories
parent = os.path.abspath('..')
sys.path.insert(1, parent)

import subprocess as sp
#import matplotlib.pyplot as plt
#import streamlit
#import atexit
#import matplotlib
#import sys
#import streamlit.web.bootstrap
from pathlib import Path
#from threading import Thread

from PySide2 import QtCore, QtWebEngineWidgets, QtWidgets
from program_files.GUI_st import GUI_st_global_functions


def kill_server(p):
    """
    Terminate a subprocess depending on the operating system.

    This function is responsible for terminating a subprocess based on the
    operating system. It uses different methods for Windows and POSIX systems.

    :param p: process which will be killed
    :type p: subprocess.Popen
    """
    if os.name == 'nt':
        # Terminate the subprocess using taskkill for Windows
        sp.call(['taskkill', '/F', '/T', '/PID', str(p.pid)])
    elif os.name == 'posix':
        # Terminate the subprocess using the kill method for POSIX systems
        p.kill()
    else:
        # For other operating systems, do nothing
        pass


def create_pyside_gui():

    hostname = 'localhost'
    port = 8501
            
    # Initialize a Qt application and WebEngineView
    app = QtWidgets.QApplication()
    view = QtWebEngineWidgets.QWebEngineView()
                

    # Load and show the Streamlit app in the WebEngineView
    view.load(QtCore.QUrl(f'http://localhost:8501'))
    view.show()
    app.exec_()
    

def start_streamlit():
    from streamlit import config as _config
    try:
        print("TEST")
        print(sys._MEIPASS)
        os.chdir(os.path.dirname(__file__))
        _config.set_option("server.headless", True)
        _config.set_option("global.developmentMode", False)
        _config.set_option("server.enableXsrfProtection", False)
        _config.show_config()
        import streamlit.web.bootstrap
        streamlit.web.bootstrap.run(str(sys._MEIPASS) + "/program_files/GUI_st/1_Main_Application.py", '', [], {})
    except:
        open("/Users/Shared/error1.log", "w").write(traceback.format_exc())

if __name__ == '__main__':
    try:
        #os.chdir(os.path.dirname(__file__))
        
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            multiprocessing.set_start_method("fork")
            process2 = multiprocessing.Process(target=start_streamlit, args=[])
            process2.start()
            create_pyside_gui()
             
            #sys.argv = ["streamlit", "run", "--server.headless=True", "--global.developmentMode=False", "--server.enableXsrfProtection=false",  "./program_files/GUI_st/1_Main_Application.py"]
            #sys.exit(stcli.main())
           # if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS') and sys.platform == "darwin":
           #     cmd = "python3.9 -m streamlit run {} --server.headless=True --global.developmentMode=False --server.enableXsrfProtection=false".format(
           #         "./program_files/GUI_st/1_Main_Application.py")
           # elif getattr(sys, 'frozen', False) and sys.platform == "win32":
           #     cmd = "python -m streamlit run {} --server.headless=True --global.developmentMode=False --server.enableXsrfProtection=false".format(
           #         "program_files\\GUI_st\\1_Main_Application.py")
           # else:
           #     cmd = "streamlit run {} --server.headless=True".format(
           #             "./GUI_st/1_Main_Application.py")
            
            #p = sp.Popen(streamlit.web.bootstrap.run("./program_files/GUI_st/1_Main_Application.py", '', [], flag_options={"server.headless": "true", "global.developmentMode": "false", "server.enableXsrfProtection": "false", "server.port": "8501"}), stdout=sp.DEVNULL)
            

            
        else:
            from streamlit.web import cli as stcli

            sys.argv = ["streamlit", "run", "--server.headless=True", "--global.developmentMode=False", "--server.enableXsrfProtection=false",  "../program_files/GUI_st/1_Main_Application.py"]
            sys.exit(stcli.main())
        
    except:
         open("/Users/Shared/error.log", "w").write(traceback.format_exc())
