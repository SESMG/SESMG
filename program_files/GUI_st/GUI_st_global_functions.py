"""
    @author: jtock - jan.tockloth@fh-muenster.de
    @author: GregorBecker - gregor.becker@fh-muenster.de
"""

import json
import glob
import os
import streamlit as st

from program_files.preprocessing.Spreadsheet_Energy_System_Model_Generator\
    import sesmg_main, sesmg_main_including_premodel


def st_settings_global():
    """
    Function to define settings for the Streamlit GUI.

    """
    # Global page settings
    st.set_page_config(
        page_title=('SESMG'),
        layout='wide',
        menu_items={'Get Help': 'https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/',
                    'Report a Bug': 'https://github.com/SESMG/SESMG/issues'})


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
        Function so safe a dict as json.

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
        Function to clear the  GUI settings dict, reset it to the initial
        values and safe in json path as variables.

        # :param result_path: internal path where the latest results were safed
        # :type result_path: str
        # :param premodeling_result_path: internal path where the latest \
        #     premodelling results were safed
        # :type premodeling_result_path: str
        :param json_file_path: internal path where json should be safed
        :type json_file_path: str
    """
    # creating the dict of GUI input values to be safed as json

    GUI_main_dict_cleared = {
        "existing_summary_csv": "null",
        "existing_components_csv": "null",
        "existing_results_csv": "null",
        "input_show_graph": False,
        "input_num_threads": 1,
        "input_solver": "cbc",
        "input_solver_index": 0,
        "input_timeseries_algorithm": "None",
        "input_timeseries_cluster_index": "None",
        "input_timeseries_criterion": "None",
        "input_timeseries_period": "None",
        "input_timeseries_season": "None",
        "input_timeseries_algorithm_index": 0,
        "input_timeseries_cluster_index_index": 0,
        "input_timeseries_criterion_index": 0,
        "input_timeseries_period_index": 0,
        "input_timeseries_season_index": 0,
        "input_activate_premodeling": False,
        "input_premodeling_invest_boundaries": False,
        "input_premodeling_tightening_factor": 1,
        "input_premodeling_timeseries_algorithm": "None",
        "input_premodeling_timeseries_cluster_index": "None",
        "input_premodeling_timeseries_criterion": "None",
        "input_premodeling_timeseries_period": "None",
        "input_premodeling_timeseries_season": "None",
        "input_premodeling_timeseries_algorithm_index": 0,
        "input_premodeling_timeseries_cluster_index_index": 0,
        "input_premodeling_timeseries_criterion_index": 0,
        "input_premodeling_timeseries_period_index": 0,
        "input_premodeling_timeseries_season_index": 0,
        "input_cluster_dh": False,
        "input_xlsx_results": False,
        "input_console_results": False,
        "input_criterion_switch": False,
        "input_pareto_points": [],
        "timeseries_prep_param": ["None", "None", "None", "None", 0],
        "pre_model_timeseries_prep_param": ["None", "None", "None", "None", 0]
    }

    # safe cleared dict
    safe_GUI_input_values(input_values_dict=GUI_main_dict_cleared,
                          json_file_path=json_file_path)


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

    if not GUI_main_dict["input_activate_premodeling"]:
        sesmg_main(
            scenario_file=model_definition,
            result_path=save_path,
            num_threads=GUI_main_dict["input_num_threads"],
            timeseries_prep=GUI_main_dict["timeseries_prep_param"],
            criterion_switch=GUI_main_dict["input_criterion_switch"],
            xlsx_results=GUI_main_dict["input_xlsx_results"],
            console_results=GUI_main_dict["input_console_results"],
            solver=GUI_main_dict["input_solver"],
            district_heating_path="",
            cluster_dh=GUI_main_dict["input_cluster_dh"])

    # If pre-modeling is activated a second run will be carried out
    else:
        sesmg_main_including_premodel(
            scenario_file=model_definition,
            result_path=save_path,
            num_threads=GUI_main_dict["input_num_threads"],
            timeseries_prep=GUI_main_dict["timeseries_prep_param"],
            criterion_switch=GUI_main_dict["input_criterion_switch"],
            xlsx_results=GUI_main_dict["input_xlsx_results"],
            console_results=GUI_main_dict["input_console_results"],
            solver=GUI_main_dict["input_solver"],
            district_heating_path="",
            cluster_dh=GUI_main_dict["input_cluster_dh"],
            pre_model_timeseries_prep=GUI_main_dict["pre_model_timeseries_prep_param"],
            investment_boundaries=GUI_main_dict["input_premodeling_invest_boundaries"],
            investment_boundary_factor=GUI_main_dict["input_premodeling_tightening_factor"],
            pre_model_path=GUI_main_dict["premodeling_res_path"]
        )


def read_markdown_document(document_path, folder_path, main_page=True):
    """

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
                    st.markdown(''.join(readme_buffer[:-1]))
                    # Display the image from the Resources folder using
                    # the image name from the resource_files list
                    st.image(folder_path[:-1] + f'/{image}')
                    # Clear the buffer list
                    readme_buffer.clear()
    
    # Display any remaining lines in the buffer list using the st.markdown() \
    # function
    st.markdown(''.join(readme_buffer), unsafe_allow_html=True)
