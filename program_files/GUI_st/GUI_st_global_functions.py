"""
    jtock - jan.tockloth@fh-muenster.de
    GregorBecker - gregor.becker@fh-muenster.de
"""

import json
import glob
import os
import streamlit as st

from program_files.preprocessing.Spreadsheet_Energy_System_Model_Generator \
    import sesmg_main, sesmg_main_including_premodel


def st_settings_global():
    """
        Function to define settings for the Streamlit GUI.
    """
    menu_items = {
        'Get Help': 'https://spreadsheet-energy-system-model-generator.'
                    'readthedocs.io/en/latest/',
        'Report a Bug': 'https://github.com/SESMG/SESMG/issues'}
    # Global page settings
    st.set_page_config(
        page_title=('SESMG'),
        layout='wide',
        menu_items=menu_items)


def import_GUI_input_values_json(json_file_path: str) -> dict:
    """
        Function to import GUI settings from am existing json file and
        save it as a dict.

        :param json_file_path: file name to the underlying json with \
            input values for all GUI pages
        :type json_file_path: str

        :return: **GUI_settings_cache_dict_reload** (dict) - \
            exported dict from json file including a (sub)dict for \
            every GUI page
    """
    # Import json file including several (sub)dicts for every GUI page
    # Each (sub)dict includes input values as a cache from the last session
    with open(json_file_path, "r", encoding="utf-8") as infile:
        GUI_settings_cache_dict_reload = json.load(infile)

    return GUI_settings_cache_dict_reload


def safe_GUI_input_values(input_values_dict: dict, json_file_path: str):
    """
        Function to safe a dict as json.

        :param input_values_dict: name of the dict of input values \
            for specific GUI page
        :type input_values_dict: dict
        :param json_file_path: file name to the underlying json with \
            input values
        :type json_file_path: str
    """
    with open(json_file_path, 'w', encoding="utf-8") as outfile:
        json.dump(input_values_dict, outfile, indent=4)


def clear_GUI_main_settings(json_file_path: str):
    """
        Function to clear the GUI settings dict, reset it to the initial
        values and safe in json path as variables.

        :param json_file_path: internal path where json should be saved
        :type json_file_path: str
    """
    # creating the dict of GUI input values to be safed as json

    GUI_main_dict_cleared = {
        "input_timeseries_algorithm": "None",
        "input_timeseries_cluster_index": 0,
        "input_timeseries_criterion": "None",
        "input_timeseries_period": "None",
        "input_timeseries_season": "None",
        "input_timeseries_algorithm_index": 0,
        "input_timeseries_criterion_index": 0,
        "input_timeseries_period_index": 0,
        "input_timeseries_season_index": 0,
        "input_timeseries_cluster_index_index": 0,
        "input_activate_premodeling": False,
        "input_premodeling_invest_boundaries": False,
        "input_premodeling_tightening_factor": 1,
        "input_premodeling_timeseries_algorithm": "None",
        "input_premodeling_timeseries_cluster_index": "None",
        "input_premodeling_timeseries_criterion": "None",
        "input_premodeling_timeseries_period": "None",
        "input_premodeling_timeseries_season": "None",
        "input_premodeling_timeseries_algorithm_index": 0,
        "input_premodeling_timeseries_criterion_index": 0,
        "input_premodeling_timeseries_period_index": 0,
        "input_premodeling_timeseries_season_index": 0,
        "input_premodeling_timeseries_cluster_index_index": 0,
        "input_pareto_points": [],
        "input_cluster_dh": False,
        "input_criterion_switch": False,
        "input_num_threads": 1,
        "input_solver": "cbc",
        "input_solver_index": 0,
        "input_xlsx_results": False,
        "input_console_results": False}

    # safe cleared dict
    safe_GUI_input_values(input_values_dict=GUI_main_dict_cleared,
                          json_file_path=json_file_path)


def create_timeseries_parameter_list(GUI_main_dict: dict,
                                     input_value_list: list,
                                     input_timseries_season: str) -> list:
    """
        Creates list of input variables as input preparation for run_semsg \
        with appending input_timseries_season value.

        :param GUI_main_dict: global defined dict of GUI input variables
        :type GUI_main_dict: dict
        :param input_values_list: list of input variables which will be \
            writen in a list from the GUI_main_dict
        :type input_values_list: list

        :return: - **parameter_list + input_value_season** (list) - list of
            timeseries simplification parameters
    """

    # set parameter from the GUI main dict and store them in a list
    parameter_list = \
        [GUI_main_dict[input_value] for input_value in input_value_list]

    # set input_timseries_season value
    input_value_season = \
        [0 if GUI_main_dict[input_timseries_season] == "None"
         else GUI_main_dict[input_timseries_season]]

    # append input_timseries_season value and return
    return parameter_list + input_value_season


def run_SESMG(GUI_main_dict: dict, model_definition: str, save_path: str):
    """
        Function to run SESMG main based on the GUI input values dict.

        :param GUI_main_dict: TODO ...
        :type GUI_main_dict: dict
        :param model_definition: file path of the model definition to \
            be optimized
        :type model_definition: str
        :param save_path: file path where the results will be saved
        :type save_path: str
    """

    # prepare timeseries parameter list
    timeseries_prep_parameter_list = \
        ["input_timeseries_algorithm", "input_timeseries_cluster_index",
         "input_timeseries_criterion", "input_timeseries_period"]

    # create timeseries parameter list as an input variable for run_sesmg
    timeseries_prep = create_timeseries_parameter_list(
        GUI_main_dict=GUI_main_dict,
        input_value_list=timeseries_prep_parameter_list,
        input_timseries_season="input_timeseries_season")

    if not GUI_main_dict["input_activate_premodeling"]:

        sesmg_main(
            scenario_file=model_definition,
            result_path=save_path,
            num_threads=GUI_main_dict["input_num_threads"],
            timeseries_prep=timeseries_prep,
            criterion_switch=GUI_main_dict["input_criterion_switch"],
            xlsx_results=GUI_main_dict["input_xlsx_results"],
            console_results=GUI_main_dict["input_console_results"],
            solver=GUI_main_dict["input_solver"],
            district_heating_path="",
            cluster_dh=GUI_main_dict["input_cluster_dh"])

    # If pre-modeling is activated a second run will be carried out
    else:

        # prepare premodell timeseries parameter list
        timeseries_prep_parameter_list = \
            ["input_premodeling_timeseries_algorithm",
             "input_premodeling_timeseries_cluster_index",
             "input_premodeling_timeseries_criterion",
             "input_premodeling_timeseries_period"]

        # create premodell timeseries parameter list as an input variable
        # for run_sesmg
        premodel_timeseries_prep = create_timeseries_parameter_list(
            GUI_main_dict=GUI_main_dict,
            input_value_list=timeseries_prep_parameter_list,
            input_timseries_season="input_premodeling_timeseries_season")

        sesmg_main_including_premodel(
            scenario_file=model_definition,
            result_path=save_path,
            num_threads=GUI_main_dict["input_num_threads"],
            timeseries_prep=timeseries_prep,
            criterion_switch=GUI_main_dict["input_criterion_switch"],
            xlsx_results=GUI_main_dict["input_xlsx_results"],
            console_results=GUI_main_dict["input_console_results"],
            solver=GUI_main_dict["input_solver"],
            district_heating_path="",
            cluster_dh=GUI_main_dict["input_cluster_dh"],
            pre_model_timeseries_prep=premodel_timeseries_prep,
            investment_boundaries=GUI_main_dict["input_premodeling_invest_boundaries"],
            investment_boundary_factor=GUI_main_dict["input_premodeling_tightening_factor"],
            pre_model_path=GUI_main_dict["premodeling_res_path"],
            graph=False)


def read_markdown_document(document_path: str, folder_path: str,
                           main_page=True) -> list:
    """
        Using this method, texts stored in the repository in the form \
        of markdown files can be used as the content of a streamlit \
        page. To do this, the markdown file and the images it contains \
        are loaded and then displayed in streamlit format.

        :param document_path: path where the markdown file which will \
            be displayed is stored
        :type document_path: str
        :param folder_path: path where the images the to be displayed \
            file contains are stored
        :type folder_path: str
        :param main_page: boolean which differentiates rather the \
            method is called from the main method or not since the \
            main page content is the Readme reduced by the \
            installation part
        :type main_page: bool
        
        :return: - **readme_buffer** (list) - list of markdown text which is \
        educed by the parts between ## Quick Start ## SESMG Features \
            & Releases based on the readme.md
    """
    # Open the README.md file and read all lines
    with open(document_path, 'r', encoding="utf8") as file:
        readme_line = file.readlines()
        # Create an empty buffer list to temporarily store the lines of \
        # the README.md file
        readme_buffer = []
        # Use the glob library to search for all files in the Resources \
        # directory and extract the file names
        resource_files = [os.path.basename(x) for x
                          in glob.glob(folder_path)]

    non_print = False
    # Iterate over each line of the README.md file
    for line in readme_line:
        if main_page:
            if "## Quick Start" in str(line):
                non_print = True
            elif "## SESMG Features & Releases" in str(line):
                non_print = False
        if not non_print:
            # Append the current line to the buffer list
            readme_buffer.append(line)
            # Check if any images are present in the current line
            for image in resource_files:
                # If an image is found, display the buffer list up to
                # the last line
                if image in line:
# TODO @gregorbecker: können wir die st. Beffehle in die GUI verschieben?
                    st.markdown(''.join(readme_buffer[:-1]))
                    # Display the image from the Resources folder using
                    # the image name from the resource_files list
                    st.image(folder_path[:-1] + f'/{image}')
                    # Clear the buffer list
                    readme_buffer.clear()

    return readme_buffer


def create_simplification_index(input_list: list, input_output_dict: dict):
    """
        Creates the streamlit index for timeseries simplification params \
            as required to reload GUI elements with initial values

       :param input_list: list with lists for each simplification with three
           columns: name of the index, list in which the index is definied
           reguarding to the input cariable name, input variable name
       :type input_list: list
       :param input_output_dict: global defined dict to which the indexes will
           be written in
       :type input_output_dict: dict
    """

    # iteratale trough the inner lists
    for var in input_list:

        input_output_dict[var[0]] = var[1][input_output_dict[var[2]]]


def create_cluster_simplification_index(input_value: str,
                                        input_output_dict: dict,
                                        input_value_index: str):
    """
        Creates the streamlit index for timeseries simplification param \
            clustering as required to reload GUI elements with initial values \
            since clustering index needs to set differntly

       :param input_value: name of the input variable in the input_output_dict
       :type input_value: str
       :param output_dict: global defined dict to which the indexes will be
           written in
       :type output_dict: dict
       :param input_list: name of the output variable in the input_output_dict
       :type input_list: str
    """

    if input_output_dict[input_value] == "None":
        input_output_dict[input_value_index] = 0
    else:
        input_output_dict[input_value_index] = input_output_dict[input_value]
