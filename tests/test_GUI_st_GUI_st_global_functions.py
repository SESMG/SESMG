"""
    jtock - jan.tockloth@fh-muenster.de
"""

import pytest
import os

@pytest.fixture
def test_GUI_main_dict():

    return {"input_timeseries_algorithm": "slicing A",
            "input_timeseries_cluster_index": 83,
            "input_timeseries_criterion": "None",
            "input_timeseries_period": "days",
            "input_timeseries_season": 4,
            "input_timeseries_algorithm_index": 4,
            "input_timeseries_criterion_index": 0,
            "input_timeseries_period_index": 2,
            "input_timeseries_season_index": 1,
            "input_timeseries_cluster_index_index": 83,
            "input_activate_premodeling": False,
            "input_premodeling_invest_boundaries": False,
            "input_premodeling_tightening_factor": 1,
            "input_premodeling_timeseries_algorithm": "averaging",
            "input_premodeling_timeseries_cluster_index": 5,
            "input_premodeling_timeseries_criterion": "temperature",
            "input_premodeling_timeseries_period": "weeks",
            "input_premodeling_timeseries_season": 12,
            "input_premodeling_timeseries_algorithm_index": 3,
            "input_premodeling_timeseries_criterion_index": 1,
            "input_premodeling_timeseries_period_index": 3,
            "input_premodeling_timeseries_season_index": 2,
            "input_premodeling_timeseries_cluster_index_index": 5,
            "input_pareto_points": [],
            "input_cluster_dh": False,
            "input_criterion_switch": False,
            "input_num_threads": 1,
            "input_solver": "cbc",
            "input_solver_index": 0,
            "input_xlsx_results": False,
            "input_console_results": False}


def test_create_timeseries_parameter_list(test_GUI_main_dict):
    """
        TODO
    """

    from program_files.GUI_st.GUI_st_global_functions \
        import create_timeseries_parameter_list

    # prepared timeseries parameter list
    timeseries_prep_parameter_list = \
        ["input_timeseries_algorithm", "input_timeseries_cluster_index",
         "input_timeseries_criterion", "input_timeseries_period"]

    # use function to create parameter list
    parameter_list = create_timeseries_parameter_list(
        GUI_main_dict=test_GUI_main_dict,
        input_value_list=timeseries_prep_parameter_list,
        input_timseries_season="input_timeseries_season")

    # define target list
    target_parameter_list = ["slicing A", 83, "None", "days", 4]

    assert parameter_list == target_parameter_list


def test_import_GUI_input_values_json(test_GUI_main_dict):
    """
        TODO @gregorbecker
    """
    from program_files.GUI_st.GUI_st_global_functions \
        import import_GUI_input_values_json

    path_to_test_json = os.path.join(
        os.path.dirname(__file__),
        "test_GUI_st_cache.json")

    imported_dict = import_GUI_input_values_json(
        json_file_path=path_to_test_json)

    assert imported_dict == test_GUI_main_dict
