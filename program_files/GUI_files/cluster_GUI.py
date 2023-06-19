# -*- coding: utf-8 -*-
from datetime import datetime
import os
from program_files.Spreadsheet_Energy_System_Model_Generator import sesmg_main
import pandas as pd


def execute_sesmg():
    """
    1. Creates the folder where the results will be saved
    2. Excecutes the optimization algorithm
    """
    runs = pd.read_csv(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.join(__file__))))
        + "/Geplante_Modelllaeufe_20220303.csv"
    )
    print(runs)
    for num, run in runs.iterrows():
        gui_variables["save_path"] = str(
            os.path.join(gui_variables["save_path_directory"])
            + "/"
            + run["name"]
            + str(datetime.now().strftime("_%Y-%m-%d--%H-%M-%S"))
        )
        print(gui_variables["save_path"])
        os.mkdir(gui_variables["save_path"])

        timeseries_season = run["seasons"]
        timeseries_prep_param = [
            run["algorithm"],
            run["index"],
            run["criterion"],
            run["period"],
            0 if timeseries_season == "none" else timeseries_season,
        ]
        print(timeseries_prep_param)
        sesmg_main(
            scenario_file=gui_variables["scenario_path"],
            result_path=gui_variables["save_path"],
            num_threads=gui_variables["num_threads"],
            timeseries_prep=timeseries_prep_param,
            graph=True if gui_variables["graph_state"] == 1 else False,
            criterion_switch=True if gui_variables["criterion_state"] == 1 else False,
            xlsx_results=True if gui_variables["xlsx_select_state"] == 1 else False,
            console_results=True
            if gui_variables["console_select_state"] == 1
            else False,
            solver=gui_variables["solver_select"],
            cluster_dh=False,
            district_heating_path=gui_variables["dh_path"],
        )


# dh_path has to be a directory e.g. results/last_result_folder
gui_variables = {
    "scenario_path": "scenario_ck_paper.xlsx",
    "save_path_directory": str(
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "results/ck_paper",
        )
    ),
    "save_path": "",
    "num_threads": 30,
    "timeseries_algorithm": "slicing A",
    "timeseries_cluster": "10",
    "timeseries_criterion": "none",
    "timeseries_period": "days",
    "timeseries_season": "none",
    "graph_state": 0,
    "criterion_state": 0,
    "solver_select": "gurobi",
    "xlsx_select_state": 1,
    "console_select_state": 0,
    "plotly_select_state": 0,
    "dh_path": "",
    "save_dh_state": 1,
}
execute_sesmg()
