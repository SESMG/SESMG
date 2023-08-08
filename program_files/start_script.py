import sys
import os
      
# setting new system path to be able to refer to parent directories
parent = os.path.abspath('..')
sys.path.insert(1, parent)

from program_files.GUI_st import GUI_st_global_functions
import streamlit
from streamlit.web import cli as stcli
from pathlib import Path
import atexit
import subprocess as sp
import matplotlib.pyplot as plt
import matplotlib

if getattr(sys, 'frozen', False) and sys.platform == 'darwin':
    os.environ["QTWEBENGINE_RESOURCES_PATH"] = str(Path(sys._MEIPASS))
    os.environ["QTWEBENGINE_LOCALES_PATH"] = str(Path(sys._MEIPASS)) + "/qtwebengine_locales"

from PySide6 import QtCore, QtWebEngineWidgets, QtWidgets

def kill_server(p):
    if os.name == 'nt':
        # p.kill is not adequate
        sp.call(['taskkill', '/F', '/T', '/PID', str(p.pid)])
    elif os.name == 'posix':
        p.kill()
    else:
        pass


if __name__ == '__main__':
    matplotlib.use("QtAgg")
    plt.rcParams['figure.hooks'].append('mplcvd:setup')

    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_dir = Path(sys._MEIPASS)
    else:
        bundle_dir = Path(__file__).parent.parent
    
    cmd = ["streamlit",
           "run",
           str(bundle_dir)
           + "/program_files/GUI_st/1_Main_Application.py",
             "--server.headless=True",
             "--global.developmentMode=False"
    ]
    p = sp.Popen(cmd, stdout=sp.DEVNULL)
    atexit.register(kill_server, p)
    
    hostname = 'localhost'
    port = 8501
    
    app = QtWidgets.QApplication()
    view = QtWebEngineWidgets.QWebEngineView()
    
    view.load(QtCore.QUrl(f'http://{hostname}:{port}'))
    view.show()
    app.exec()
