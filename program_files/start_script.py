"""
    Gregor Becker - gregor.becker@fh-muenster.de
    Jan N. Tockloth - jan.tockloth@fh-muenster.de
"""

import traceback
import sys
import os
import multiprocessing
multiprocessing.freeze_support()
    
# setting new system path to be able to refer to parent directories
parent = os.path.abspath('..')
sys.path.insert(1, parent)

import subprocess as sp
from pathlib import Path

os.chdir(os.path.dirname(__file__))

from PySide6 import QtCore, QtWebEngineWidgets, QtWidgets
from program_files.GUI_st import GUI_st_global_functions
from program_files.start_streamlit import start_streamlit


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


def create_pyside_gui() -> None:
    """
    Create a PySide2 GUI to display a Streamlit app using QtWebEngineView.

    This function initializes a Qt application, creates a QMainWindow,
    and embeds a QWebEngineView widget to display a Streamlit app.
    It sets focus policies and loads the app's URL.
    """

    hostname = 'localhost'
    port = 8501

    # Initialize a Qt application and WebEngineView
    app = QtWidgets.QApplication(sys.argv)
    # Create a PySide2 QMainWindow
    main_window = QtWidgets.QMainWindow()
    # Create a QWebEngineView widget
    view = QtWebEngineWidgets.QWebEngineView()
    # Set the focus policy for the QWebEngineView widget
    view.setFocusPolicy(QtCore.Qt.StrongFocus)
    # Load the Streamlit app URL
    view.load(QtCore.QUrl(f'{"http://localhost:8501"}'))
    # Set the view as the central widget
    main_window.setCentralWidget(view)
    # Set focus to the main_window
    main_window.setFocus()
    # Show the main window
    main_window.show()
    # Load and show the Streamlit app in the WebEngineView
    app.exec_()


if __name__ == '__main__':
    # Check if the script is being executed as the main program

    if getattr(sys, 'frozen', False) \
            and hasattr(sys, '_MEIPASS') \
            and sys.platform == "darwin":
        # Check if the script is frozen (compiled) and running on macOS

        # Set the start method for multiprocessing to "spawn"
        multiprocessing.set_start_method("spawn")
        # Create a new process to run the 'start_streamlit' function
        process2 = multiprocessing.Process(target=start_streamlit, args=[])
        # Start the new process for the Streamlit app
        process2.start()
        # Create and run the PySide2 GUI
        create_pyside_gui()

    elif getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Check if the script is frozen (compiled) and running on Windows
        # or other platforms
        # Set the start method for multiprocessing to "spawn"
        multiprocessing.set_start_method("spawn")
        # Create a new process to run the 'start_streamlit' function
        process2 = multiprocessing.Process(target=start_streamlit, args=[])
        # Start the new process for the Streamlit app
        process2.start()
        # Create and run the PySide2 GUI
        create_pyside_gui()

    else:
        # If not frozen or running on macOS, execute the following code:
        # Import the Streamlit web CLI module
        from streamlit.web import cli as stcli

        # Configure the command-line arguments for running Streamlit
        sys.argv = ["streamlit",
                    "run",
                    "--server.headless=True",
                    "--global.developmentMode=False",
                    "--server.enableXsrfProtection=false",
                    "../program_files/GUI_st/1_Main_Application.py"]

        # Run the Streamlit app using the specified command-line arguments
        sys.exit(stcli.main())
