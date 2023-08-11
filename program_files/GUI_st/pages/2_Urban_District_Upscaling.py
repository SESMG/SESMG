"""
    Janik Budde - janik.budde@fh-muenster.de
    Jan N. Tockloth - jan.tockloth@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
"""

import os
import streamlit as st
import pandas as pd
from datetime import datetime

from program_files.urban_district_upscaling.pre_processing \
    import urban_district_upscaling_pre_processing
from program_files.GUI_st.GUI_st_global_functions \
    import st_settings_global, import_GUI_input_values_json, \
    read_markdown_document, create_result_directory, set_result_path


# settings the initial streamlit page settings
st_settings_global()

# Import GUI help comments from the comment json and save as an dict
GUI_helper = import_GUI_input_values_json(
    os.path.dirname(os.path.dirname(__file__))
    + "/GUI_st_help_comments.json")


# initialize session_states
if "state_model_definition_sheets" not in st.session_state:
    st.session_state["state_model_definition_sheets"] = ""
if "result_file_name" not in st.session_state:
    st.session_state["result_file_name"] = ""
if "state_download" not in st.session_state:
    st.session_state['state_download'] = False


def us_application() -> None:
    """
        Definition of the sidebar elements for the urban district
        upscaling page and starting a udu tool run.
    """
    # create form-submit element for multiple inputs
    with st.sidebar.form("Input Parameters"):

        # input us sheet
        input_us_sheet_path = st.file_uploader(
            label="Import your upscaling sheet:",
            help=GUI_helper["udu_fu_us_sheet"])

        # input standard parameter sheet
        input_standard_parameter_path = st.file_uploader(
            label="Import your standard parameter sheet:",
            help=GUI_helper["udu_fu_sp_sheet"])

        # text input to define the file name
        result_file_name = \
            st.text_input(label="Type in your model definition file name.",
                          help=GUI_helper["udu_ti_model_def_name"])

        # Submit button to start optimization.
        submitted_us_run = st.form_submit_button(
                label="Start US Tool",
                help=GUI_helper["udu_fs_start_US_tool"])

        # Run program main function if start button is clicked
        if submitted_us_run:
            if input_us_sheet_path != "" \
                    and input_standard_parameter_path != "" \
                    and result_file_name != "":
                # strings replace due to variables defined above
                us_path_list = [
                    input_us_sheet_path,
                    input_standard_parameter_path,
                    result_file_name,
                    os.path.join(
                        os.path.dirname(__file__),
                        r"../../urban_district_upscaling/plain_scenario.xlsx")
                ]

            # get the model definition sheet as a dict and model definition
            # worksheets as a list as return of the main urban district
            # upscaling function
            model_definition_sheets, model_definition_worksheets = \
                urban_district_upscaling_pre_processing(
                    paths=us_path_list,
                    clustering=False,
                    clustering_dh=False)

            # define urban district upscaling model definition as session state
            st.session_state["state_model_definition_sheets"] = \
                model_definition_sheets
            # define urban district upscaling model definition as session state

            st.session_state["state_model_definition_worksheets"] = \
                model_definition_worksheets
            # define result path as session state
            st.session_state["result_file_name"] = result_file_name


def us_application_create_folder() -> None:
    """
        Creating download button for the created model definition.
    """

    # set the result path based on the gui_st_settings.json
    res_folder_path = os.path.join(set_result_path(),
                                   'Upscaling_Tool')

    # Check if the results folder path exists
    if os.path.exists(res_folder_path) is False:
        # If not, create the result directory using a separate function
        create_result_directory()
        # Add upscaling folder if necessary
        os.makedirs(res_folder_path)


def us_application_start_download() -> None:
    """
    Initiates the process to start downloading an Excel file.

    This function prepares and creates an Excel file containing data from
    specified components and data sheets. It sets up the necessary paths,
    creates directories if needed, constructs the Excel file path, and saves
    the data to the file.
    """

    # set the result path based on the gui_st_settings.json
    res_folder_path = os.path.join(set_result_path(),
                                   'Upscaling_Tool')

    # Check if the results folder path exists
    if os.path.exists(res_folder_path) is False:
        # If not, create the result directory using a separate function
        create_result_directory()
        # Add upscaling folder if necessary
        os.makedirs(res_folder_path)

    # defining the the path including file name
    st.session_state['state_file_path'] = res_folder_path \
        + '/' \
        + st.session_state["result_file_name"] \
        + datetime.now().strftime('_%Y-%m-%d--%H-%M-%S') \
        + '.xlsx'

    # open the new excel file and add all the created components
    j = 0
    writer = pd.ExcelWriter(path=st.session_state['state_file_path'],
                            engine="xlsxwriter")
    # save the excel file
    for i in st.session_state["state_model_definition_sheets"]:
        st.session_state["state_model_definition_sheets"][i].to_excel(
            excel_writer=writer,
            sheet_name=st.session_state["state_model_definition_worksheets"][j],
            index=False)
        j = j + 1

    writer.close()


def us_application_create_download_button() -> None:
    """
    Creating the download button and change session state as on_click
    to start the downloading process
    """
    
    # Update session_state when button is clicked
    st.session_state['state_download'] = \
        st.sidebar.button(label="Save your model definition",
                          help=GUI_helper["res_b_load_results"])


def standard_page() -> None:
    """
        Load the existing file of the us tool description and include
        graphics.
    """

    # import of text and graphic
    reduced_readme = read_markdown_document(
        document_path="docs/GUI_texts/us_tool.md",
        folder_path=f'{"docs/images/manual/UpscalingTool/*"}')

    # Display any remaining lines in the buffer list using the st.markdown() \
    # function
    st.markdown(''.join(reduced_readme), unsafe_allow_html=True)


def udu_preprocessing_page() -> None:
    """
        Definition of the page elements after the urban district
        upscaling tool ran.
    """

    # define header
    st.header("Model defintion")

    # create model defnition table
    tabs = st.session_state["state_model_definition_worksheets"].copy()
    # without info column
    tabs.pop(0)
    tab_bar = st.tabs(tabs)
    for i in range(len(tabs)):
        with tab_bar[i]:
            df_input = \
                st.session_state["state_model_definition_sheets"][tabs[i]]
            df_input = df_input.astype(str)
            st.dataframe(df_input)


# running sidebar elements
us_application()
us_application_create_download_button()

# running the start / main page if tool did not run yet
if st.session_state["state_model_definition_sheets"] == "" and \
        st.session_state['state_download'] is False:
    # run start page
    standard_page()

# running preprocessing page if tool ran
elif st.session_state["state_model_definition_sheets"] != "" and \
        st.session_state['state_download'] is False:
    # show result page after finished run
    udu_preprocessing_page()

# safe the model definition
elif st.session_state['state_download'] is True:
    # download the file after button was clicked
    us_application_start_download()
    # reset session states
    st.session_state["state_model_definition_sheets"] = ""
    st.session_state["result_file_name"] = ""
    st.session_state['state_download'] = False
    # 
    st.experimental_rerun()
