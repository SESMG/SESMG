# -*- coding: utf-8 -*-
from datetime import datetime
import os
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
