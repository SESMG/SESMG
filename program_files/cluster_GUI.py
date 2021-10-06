# -*- coding: utf-8 -*-
from datetime import datetime
import subprocess
import os
import sys
from program_files.Spreadsheet_Energy_System_Model_Generator import sesmg_main


def execute_sesmg():
    """ 1. Creates the folder where the results will be saved
        2. Excecutes the optimization algorithm """
    if gui_variables["scenario_path"] != "No scenario selected.":
        
        scenario_name = os.path.basename(gui_variables["scenario_path"])
        gui_variables["save_path"] = str(
            os.path.join(gui_variables["save_path_directory"])
            + '/' + scenario_name[:-5]
            + str(datetime.now().strftime('_%Y-%m-%d--%H-%M-%S')))
        os.mkdir(gui_variables["save_path"])
        
        timeseries_season = gui_variables["timeseries_season"]
        timeseries_prep_param = [gui_variables["timeseries_algorithm"],
                                 gui_variables["timeseries_cluster"],
                                 gui_variables["timeseries_criterion"],
                                 gui_variables["timeseries_period"],
                                 0 if timeseries_season == 'none'
                                 else timeseries_season]
        
        sesmg_main(scenario_file=gui_variables["scenario_path"],
                   result_path=gui_variables["save_path"],
                   num_threads=gui_variables["num_threads"],
                   timeseries_prep=timeseries_prep_param,
                   # time_prep.get(),
                   # timeseries_value = 1
                   # if timeseries_entry.get() == 'aggregation quote'
                   # else timeseries_entry.get(),
                   graph=True if gui_variables["graph_state"] == 1
                   else False,
                   criterion_switch=True if
                   gui_variables["criterion_state"] == 1 else False,
                   xlsx_results=True if
                   gui_variables["xlsx_select_state"] == 1 else False,
                   console_results=True if
                   gui_variables["console_select_state"] == 1 else False,
                   solver=gui_variables["solver_select"],
                   save_dh_calculations=gui_variables["save_dh_state"],
                   district_heating_path=gui_variables["dh_path"])
        if gui_variables["plotly_select_state"] == 1:
            show_results()
    else:
        print('Please select scenario first!')


def get_pid():
    """ Returns the ID of the running process on Port 8050 """
    import socket
    import errno
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Checks if port 8050 can be reached
        s.bind(("127.0.0.1", 8050))
        # If Yes, the program continues in line 225
        closeprocess = False
    # If not, the ID of the running process is returned
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            closeprocess = True
    s.close()
    if closeprocess:
        if sys.platform.startswith("win"):
            command = "netstat -aon| findstr :8050"
        elif sys.platform.startswith("darwin"):
            command = "lsof -i tcp:8050"
        elif sys.platform.startswith("linux"):
            command = "fuser -n tcp 8050"
        pids = subprocess.check_output(command, shell=True)
        pids = str(pids)
        pidslist = pids.split()
        if sys.platform.startswith("win"):
            pid = pidslist[5]
            pid = pid[:-4]
        elif sys.platform.startswith("darwin"):
            pid = pidslist[9]
        elif sys.platform.startswith("linux"):
            pid = pidslist[1]
        return pid
    else:
        return ''


def show_results():
    """
        executes the external program, which executes a plotl.
        dash app for displaying interactive results.
    """
    if gui_variables["save_path"].get() == '':
        raise SystemError('No optimization since the last restart'
                          ' please select a result folder!')
    
    # Determines the ID of a still running process on port 8050.
    pid = get_pid()
    # Checks if the ID is not an empty return (no process available)
    if pid != '':
        if sys.platform.startswith("win"):
            command = 'taskkill /F /PID ' + pid
        elif sys.platform.startswith("darwin"):
            command = 'kill ' + pid
        elif sys.platform.startswith("linux"):
            command = 'kill ' + pid
        # Kills the still running process on port 8050
        subprocess.call(command, shell=True)
    else:
        if sys.platform.startswith("win"):
            subprocess.call("start http://127.0.0.1:8050", shell=True)
        elif sys.platform.startswith("darwin"):
            subprocess.call("open http://127.0.0.1:8050", shell=True)
        elif sys.platform.startswith("linux"):
            subprocess.call("xdg-open http://127.0.0.1:8050", shell=True)
    
    # Starts the new Plotly Dash Server for Windows
    if sys.platform.startswith("win"):
        subprocess.call("Scripts\python.exe"
                        + " program_files/Interactive_Results.py "
                        + 'r"' + gui_variables["save_path"].get() + '"',
                        timeout=10, shell=True)
    # Starts the new Plotly Dash Server for MACOS
    elif sys.platform.startswith("darwin"):
        IR_PATH = os.path.dirname(os.path.abspath(__file__))
        subprocess.call("python3 " + IR_PATH + "/Interactive_Results.py "
                        + str(gui_variables["save_path"].get()),
                        timeout=10, shell=True)
    elif sys.platform.startswith("linux"):
        IR_PATH = os.path.dirname(os.path.abspath(__file__))
        subprocess.call("python3 " + IR_PATH + "/Interactive_Results.py "
                        + str(gui_variables["save_path"].get()),
                        timeout=10, shell=True)
# TODO Necessary attributes for the cluster run
# dh_path has to be a directory e.g. results/last_result_folder
gui_variables = {
    "scenario_path": 'scenario.xlsx',
    "save_path_directory":
        str(os.path.join(
                os.path.dirname(
                        os.path.dirname(__file__)
                ), 'results')),
    "save_path": '',
    "num_threads": 30,
    "timeseries_algorithm": 'slicing A',
    "timeseries_cluster": '10',
    "timeseries_criterion": 'none',
    "timeseries_period": 'days',
    "timeseries_season": 'none',
    "graph_state": 0,
    "criterion_state": 0,
    "solver_select": 'gurobi',
    "xlsx_select_state": 1,
    "console_select_state": 1,
    "plotly_select_state": 1,
    "dh_path": "",
    "save_dh_state": 1
}
execute_sesmg()
