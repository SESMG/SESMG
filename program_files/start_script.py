import sys
import os

# setting new system path to be able to refer to parent directories
parent = os.path.abspath('..')
sys.path.insert(1, parent)

import subprocess as sp
from multiprocessing import Process
import matplotlib.pyplot as plt
import streamlit
import atexit
import matplotlib
import streamlit.web.bootstrap
from pathlib import Path


# Set environment variables for frozen macOS applications using Qt WebEngine
if getattr(sys, 'frozen', False) and sys.platform == 'darwin':
    # Set the path for Qt WebEngine resources
    #os.environ["QTWEBENGINE_RESOURCES_PATH"] = str(Path(sys._MEIPASS))
    # Set the path for Qt WebEngine locales
    #os.environ["QTWEBENGINE_LOCALES_PATH"] = \
    #    str(Path(sys._MEIPASS)) + "/qtwebengine_locales"
    sys.path.append(str(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))))
os.chdir(os.path.dirname(__file__))
from PySide2 import QtCore, QtWebEngineWidgets, QtWidgets

if getattr(sys, 'frozen', False) and sys.platform == 'darwin':
    os.environ["QTWEBENGINEPROCESS_PATH"] = os.path.normpath(os.path.join(
        sys._MEIPASS, 'PySide2', 'QT', 'lib',
        'QtWebEngineCore.framework', 'Helpers', 'QtWebEngineProcess.app',
        'Contents', 'MacOS', 'QtWebEngineProcess'
        ))

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


if __name__ == '__main__':
    #os.chdir(os.path.dirname(__file__))
    # Set environment variable to enable Qt WebEngine debugging
    #os.environ["QT_LOGGING_TO_CONSOLE"] = "1"

    # Configure Matplotlib to use Qt backend for rendering
    #matplotlib.use("QtAgg")
    #plt.rcParams['figure.hooks'].append('mplcvd:setup')

    # Determine the bundle directory based on frozen or non-frozen state
    #if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    #    bundle_dir = Path(sys._MEIPASS)
    #else:
    #    bundle_dir = Path(__file__).parent.parent

    # Define the command to run the Streamlit application
    #cmd = [
    #    "streamlit",
    #    "run",
    #    str(bundle_dir) + "/program_files/GUI_st/1_Main_Application.py",
    #    "--server.headless=True",
    #    "--global.developmentMode=False"
    #]

    # Start the Streamlit subprocess and register termination function
    #p = sp.Popen(cmd, stdout=sp.DEVNULL)
    #atexit.register(kill_server, p)

    # Set the hostname and port for the Qt WebEngineView
    #hostname = 'localhost'
    #port = 8501

    # Initialize a Qt application and WebEngineView
    #app = QtWidgets.QApplication()
    #view = QtWebEngineWidgets.QWebEngineView()

    # Load and show the Streamlit app in the WebEngineView
    #view.load(QtCore.QUrl(f'http://{hostname}:{port}'))
    #view.show()

    # Start the Qt application event loop
    #app.exec()
    os.chdir(os.path.dirname(__file__))

    
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS') and sys.platform == "darwin":
        cmd = "python3.9 -m streamlit run {} --server.headless=True".format(
            "./program_files/GUI_st/1_Main_Application.py")
    elif getattr(sys, 'frozen', False) and sys.platform == "win32":
        cmd = "python -m streamlit run {} --server.headless=True --server.enableXsrfProtection=false".format(
            ".\\program_files\\GUI_st\\1_Main_Application.py")
    else:
        cmd = "streamlit run {} --server.headless=True".format(
                "./GUI_st/1_Main_Application.py")
        
    p = sp.Popen(cmd.split(), stdout=sp.DEVNULL)
    atexit.register(kill_server, p)

    hostname = 'localhost'
    port = 8501
    
    
    # Initialize a Qt application and WebEngineView
    app = QtWidgets.QApplication()
    view = QtWebEngineWidgets.QWebEngineView()

    # Load and show the Streamlit app in the WebEngineView
    view.load(QtCore.QUrl(f'http://localhost:8501'))
    view.show()

    app.exec_()
