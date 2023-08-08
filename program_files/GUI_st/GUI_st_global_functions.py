"""
    Jan N. Tockloth - jan.tockloth@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
"""

import json
import glob
import os
import streamlit as st
import sys
from pathlib import Path

from program_files.preprocessing.Spreadsheet_Energy_System_Model_Generator \
    import sesmg_main, sesmg_main_including_premodel


def get_bundle_dir():

    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_dir = Path(sys._MEIPASS)
    else:
        bundle_dir = Path(__file__).parent.parent.parent

    return bundle_dir


def st_settings_global() -> None:
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


def safe_GUI_input_values(input_values_dict: dict,
                          json_file_path: str) -> None:
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


def clear_GUI_main_settings(json_file_path: str) -> None:
    """
        Function to clear the GUI settings dict, reset it to the
        initial values and safe in json path as variables.

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
        "input_dh_folder_index": 0,
        "input_activate_dh_precalc": False,
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
                                     input_timeseries_season: str) -> list:
    """
        Creates list of input variables as input preparation for
        run_semsg with appending input_timseries_season value.

        :param GUI_main_dict: global defined dict of GUI input variables
        :type GUI_main_dict: dict
        :param input_value_list: list of input variables which will \
            be written in a list from the GUI_main_dict
        :type input_value_list: list
        :param input_timeseries_season: input value of the season drop \
            down menu in the GUI
        :type input_timeseries_season: str

        :return: - **parameter_list + input_value_season** (list) - \
            list of timeseries simplification parameters
    """

    # set parameter from the GUI main dict and store them in a list
    parameter_list = \
        [GUI_main_dict[input_value] for input_value in input_value_list]

    # set input_timseries_season value
    input_value_season = \
        [0 if GUI_main_dict[input_timeseries_season] == "None"
         else GUI_main_dict[input_timeseries_season]]

    # append input_timseries_season value and return
    return parameter_list + input_value_season


def run_SESMG(GUI_main_dict: dict,
              model_definition: str,
              save_path: str) -> None:
    """
        Function to run SESMG main based on the GUI input values dict.

        :param GUI_main_dict: global defined dict of GUI input variables
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
        input_timeseries_season="input_timeseries_season")

    if not GUI_main_dict["input_activate_premodeling"]:

        sesmg_main(
            model_definition_file=model_definition,
            result_path=save_path,
            num_threads=GUI_main_dict["input_num_threads"],
            timeseries_prep=timeseries_prep,
            criterion_switch=GUI_main_dict["input_criterion_switch"],
            xlsx_results=GUI_main_dict["input_xlsx_results"],
            console_results=GUI_main_dict["input_console_results"],
            solver=GUI_main_dict["input_solver"],
            district_heating_path=GUI_main_dict["input_dh_folder"],
            cluster_dh=GUI_main_dict["input_cluster_dh"])

    # If pre-modeling is activated a second run will be carried out
    else:

        # prepare pre-model timeseries parameter list
        timeseries_prep_parameter_list = \
            ["input_premodeling_timeseries_algorithm",
             "input_premodeling_timeseries_cluster_index",
             "input_premodeling_timeseries_criterion",
             "input_premodeling_timeseries_period"]

        # create pre-model timeseries parameter list as an input variable
        # for run_sesmg
        premodel_timeseries_prep = create_timeseries_parameter_list(
            GUI_main_dict=GUI_main_dict,
            input_value_list=timeseries_prep_parameter_list,
            input_timeseries_season="input_premodeling_timeseries_season")

        sesmg_main_including_premodel(
            model_definition_file=model_definition,
            result_path=save_path,
            num_threads=GUI_main_dict["input_num_threads"],
            timeseries_prep=timeseries_prep,
            criterion_switch=GUI_main_dict["input_criterion_switch"],
            xlsx_results=GUI_main_dict["input_xlsx_results"],
            console_results=GUI_main_dict["input_console_results"],
            solver=GUI_main_dict["input_solver"],
            district_heating_path=GUI_main_dict["input_dh_folder"],
            cluster_dh=GUI_main_dict["input_cluster_dh"],
            pre_model_timeseries_prep=premodel_timeseries_prep,
            investment_boundaries=GUI_main_dict["input_premodeling_invest_boundaries"],
            investment_boundary_factor=GUI_main_dict["input_premodeling_tightening_factor"],
            graph=False)


def read_markdown_document(document_path: str, folder_path: str,
                           main_page=True) -> list:
    """
        Using this method, texts stored in the repository in the form
        of markdown files can be used as the content of a streamlit
        page. To do this, the markdown file and the images it contains
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

        :return: - **readme_buffer** (list) - list of markdown text \
            which is educed by the parts between ## Quick Start \
            ## SESMG Features & Releases based on the readme.md
    """
    # Open the README.md file and read all lines
    with open(str(get_bundle_dir()) + "/" + document_path, 'r',
              encoding="utf8") as file:
        readme_line = file.readlines()
        # Create an empty buffer list to temporarily store the lines of \
        # the README.md file
        readme_buffer = []
        # Use the glob library to search for all files in the Resources \
        # directory and extract the file names
        resource_files = [os.path.basename(x) for x
                          in glob.glob(str(get_bundle_dir())
                                       + "/" + folder_path)]

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
                    st.markdown(''.join(readme_buffer[:-1]))
                    # Display the image from the Resources folder using
                    # the image name from the resource_files list
                    st.image(str(get_bundle_dir())
                             + "/" + folder_path[:-1] + f'{image}')
                    # Clear the buffer list
                    readme_buffer.clear()

    return readme_buffer


def create_simplification_index(input_list: list,
                                input_output_dict: dict) -> None:
    """
        Creates the streamlit index for timeseries simplification
        params as required to reload GUI elements with initial values.

       :param input_list: list with lists for each simplification with \
           three columns: name of the index, list in which the index \
           is defined regarding to the input cariable name, input \
           variable name
       :type input_list: list
       :param input_output_dict: global defined dict to which the \
           indexes will be written in
       :type input_output_dict: dict
    """

    # iterate trough the inner lists
    for var in input_list:

        input_output_dict[var[0]] = var[1][input_output_dict[var[2]]]


def create_cluster_simplification_index(input_value: str,
                                        input_output_dict: dict,
                                        input_value_index: str) -> None:
    """
        Creates the streamlit index for timeseries simplification param
        clustering as required to reload GUI elements with initial
        values since clustering index needs to set differently

        :param input_value: name of the input variable in the \
            input_output_dict
        :type input_value: str
        :param input_output_dict: global defined dict to which the \
            indexes will be written in
        :type input_output_dict: dict
        :param input_value_index: name of the output variable in the \
            input_output_dict
        :type input_value_index: str
    """

    if input_output_dict[input_value] == "None":
        input_output_dict[input_value_index] = 0
    else:
        input_output_dict[input_value_index] = input_output_dict[input_value]


def load_result_folder_list() -> list:
    """
        Load the folder names of the existing result folders.

        :return: - **existing_result_foldernames_list** (list) - list \
            of exsting folder names.
    """

    # Define the path to the results folder within SESMG directory
    res_folder_path = os.path.expanduser(
        os.path.join('~', 'documents', 'sesmg', 'results', '*'))

    # read sub folders in the result folder directory
    existing_result_foldernames_list = [
        os.path.basename(x) for x in glob.glob(res_folder_path)]
    # sort list
    existing_result_foldernames_list.sort()

    return existing_result_foldernames_list


def check_for_dependencies():
    """
        Checks rather Graphviz, CBC or gurobi are installed.
    """

    from pathlib import Path
    import glob
    # graphviz paths
    dot_paths = ["C:\\Program Files (x86)\\Graphviz2.38\\bin",
                 "/usr/local/bin",
                 "/opt/anaconda3/bin"]
    dot_bool = False
    for path in dot_paths:
        if Path(path).is_dir():
            list = glob.glob(path + "/*")
            for i in list:
                if "dot" in i:
                    dot_bool = True
                    os.environ["PATH"] += os.pathsep + path
    if not dot_bool:
        raise ImportError("Graphviz is not installed on your device.")

    # cbc solver paths
    cbc_paths = ["/usr/local/bin",
                 "/opt/homebrew/bin"]
    cbc_bool = False
    for path in cbc_paths:
        if Path(path).is_dir():
            if Path(path).is_dir():
                list = glob.glob(path + "/*")
                for i in list:
                    if "cbc" in i:
                        cbc_bool = True
                        os.environ["PATH"] += os.pathsep + path
    if not cbc_bool:
        raise ImportError("CBC Solver is not installed on your device.")


def set_result_path() -> str:
    """
    Set the path for storing results based on settings.

    This function determines and returns the path for storing results
    based on the settings specified in 'GUI_st_settings.json' file.
    The 'result_folder_directory' value in the JSON defines the relative path
    within the user's documents directory.

    Returns:
        str: The path for storing results.
    """
    # defineing path to GUI_st_settings.json
    settings_json_path = os.path.dirname(__file__) \
        + "/GUI_st_settings.json"
    # import json
    gui_settings_json = \
        import_GUI_input_values_json(settings_json_path)
    # get list with directories which is defining the result folder
    result_directory_list = gui_settings_json['result_folder_directory']
    # Define the path to the results folder within SESMG directory
    res_folder_path = os.path.expanduser(
        os.path.join('~', *result_directory_list))

    return res_folder_path


def create_result_directory() -> None:
    """
    Create a result directory and a SESMG folder in the user's documents
    directory for storing JSON files and results.

    This function creates a directory structure to store JSON files and
    results. It imports settings from 'GUI_st_settings.json' to determine the
    path structure. The 'result_folder_directory' value in the JSON defines
    the relative path. The directory structure is constructed based on the
    user's documents directory.
    """

    # Define the path to the result directory
    result_directory_path = set_result_path()

    # Check if the results directory exists inside and create it if necessary
    if os.path.exists(result_directory_path) is False:
        # Create the results directory if it doesn't exist
        os.makedirs(result_directory_path)
