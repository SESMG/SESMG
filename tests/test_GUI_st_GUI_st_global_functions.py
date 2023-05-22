"""
    jtock - jan.tockloth@fh-muenster.de
"""

import pytest
import os


@pytest.fixture
def test_GUI_main_dict():
    """
        Redefining the GUI_main_dict which is inputvariable for all
        global GUI functions
    """

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
        Testing if the function creates the in the parameter list in
        the order as required for the run_sesmg function which is
        [algorithm, cluster_index, cluster_criterion, cluster_period,
        cluster_season]. If valid it is also valid for the
        premodel_parameter_list.
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
        input_timeseries_season="input_timeseries_season")

    # define target list
    target_parameter_list = ["slicing A", 83, "None", "days", 4]

    assert parameter_list == target_parameter_list


def test_import_GUI_input_values_json(test_GUI_main_dict):
    """
        Testing the json upload and the definition of the dict is
        working as required.
    """
    from program_files.GUI_st.GUI_st_global_functions \
        import import_GUI_input_values_json

    path_to_test_json = os.path.join(
        os.path.dirname(__file__),
        "test_GUI_st_cache.json")

    imported_dict = import_GUI_input_values_json(
        json_file_path=path_to_test_json)

    assert imported_dict == test_GUI_main_dict


def test_create_simplification_index(test_GUI_main_dict):
    """
        Testing if the function is creating the indexes in the
        GUI_main_dict as required and is uding the correct values.
    """
    from program_files.GUI_st.GUI_st_global_functions \
        import create_simplification_index

    # dict for timeseries algorithm input as key and streamlitindex as value
    timeseries_algorithm_dict = {"None": 0,
                                 "k_means": 1,
                                 "k_medoids": 2,
                                 "averaging": 3,
                                 "slicing A": 4,
                                 "slicing B": 5,
                                 "downsampling A": 6,
                                 "downsampling B": 7,
                                 "heuristic selection": 8,
                                 "random sampling": 9}

    # dict for timeseries clustering crtieria input as key and streamlit \
    # index as value
    timeseries_cluster_criteria_dict = {"None": 0,
                                        "temperature": 1,
                                        "dhi": 2,
                                        "el_demand_sum": 3,
                                        "heat_demand_sum": 4}

    # dict for timeseries periods input as key and streamlit index as value
    input_timeseries_period_dict = {"None": 0,
                                    "hours": 1,
                                    "days": 2,
                                    "weeks": 3}

    # dict for timeseries clustering crtieria input as key and streamlit \
    # index as value
    input_timeseries_season_dict = {"None": 0,
                                    4: 1,
                                    12: 2}

    # input values list of sublists with parameters
    simpification_index_list = [
        ["input_timeseries_algorithm_index",
         timeseries_algorithm_dict,
         "input_timeseries_algorithm"],
        ["input_timeseries_criterion_index",
         timeseries_cluster_criteria_dict,
         "input_timeseries_criterion"],
        ["input_timeseries_period_index",
         input_timeseries_period_dict,
         "input_timeseries_period"],
        ["input_timeseries_season_index",
         input_timeseries_season_dict,
         "input_timeseries_season"]]

    # change targeted values of the test_GUI_main_dict to cleared values
    reduced_test_dict = test_GUI_main_dict
    reduced_test_dict["input_timeseries_algorithm_index"] = 0
    reduced_test_dict["input_timeseries_criterion_index"] = 0
    reduced_test_dict["input_timeseries_period_index"] = 0
    reduced_test_dict["input_timeseries_season_index"] = 0

    # start function to create the keys and indexes in the GUI_main_dict
    create_simplification_index(
        input_list=simpification_index_list,
        input_output_dict=reduced_test_dict)

    assert reduced_test_dict == test_GUI_main_dict


def test_create_cluster_simplification_index_value(test_GUI_main_dict):
    """
        Testing if the function is changing the globally defined
        GUI_main_dict as required if the input value a an int.
    """
    from program_files.GUI_st.GUI_st_global_functions \
        import create_cluster_simplification_index

    # change the targeted value to a wrong values
    changed_test_dict = test_GUI_main_dict
    changed_test_dict["input_timeseries_cluster_index_index"] = 0

    # run function with reduced dict
    create_cluster_simplification_index(
        input_value="input_timeseries_cluster_index",
        input_output_dict=changed_test_dict,
        input_value_index="input_timeseries_cluster_index_index")

    assert changed_test_dict == test_GUI_main_dict
    
    
def test_create_cluster_simplification_index_none(test_GUI_main_dict):
    """
        Testing if the function is changing the globally defined
        GUI_main_dict as required if the input value a an "None".
    """
    from program_files.GUI_st.GUI_st_global_functions \
        import create_cluster_simplification_index

    # change the targeted value to a wrong values
    changed_test_dict = test_GUI_main_dict
    changed_test_dict["input_timeseries_cluster_index"] = "None"

    # run function with reduced dict
    create_cluster_simplification_index(
        input_value="input_timeseries_cluster_index",
        input_output_dict=changed_test_dict,
        input_value_index="input_timeseries_cluster_index_index")
    
    test_GUI_main_dict["input_timeseries_cluster_index_index"] = 0

    assert changed_test_dict == test_GUI_main_dict


def test_positive_read_markdown_document():
    """
        Testing if function is loading the README.md as required and if
        it is only dropping the required part
    """
    from program_files.GUI_st.GUI_st_global_functions \
        import read_markdown_document
    
    test_target_1, test_target_2 = False, False

    # creating the reduced README file as a str in a list
    reduced_readme = read_markdown_document(
        document_path=os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "README.md"),
        folder_path="empty")

    # iterate through the list and check if unique text part bevor and \
    # behind the reduced part are printed as required
    # testing part before drop
    for item in reduced_readme:
        if item.find("(oemof)") != -1:
            test_target_1 = True

    # testing part behind drop
    for item in reduced_readme:
        if item.find("Code of Conduct") != -1:
            test_target_2 = True

    assert test_target_1 and test_target_2


@pytest.mark.xfail
def test_negative_read_markdown_document():
    """
        Testing if the function is still removing the installation part
        of the README.md correctly to show the rest in the GUI. Test is
        supposed to fail if it contains a str which is used to describe
        the installation process.
    """
    from program_files.GUI_st.GUI_st_global_functions \
        import read_markdown_document

    # creating the reduced README file as a str in a list
    reduced_readme = read_markdown_document(
        document_path=os.path.join(
            os.path.dirname(__file__), "README.md"),
        folder_path="empty")

    # iterate through the list and check if part which is suppost to be \
    # dropped is not in the list of str
    for item in reduced_readme:
        if item.find("install coinor-cbc") != -1:
            test_target = True

    assert test_target
