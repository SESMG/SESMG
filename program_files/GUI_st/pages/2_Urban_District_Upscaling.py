"""
    Janik Budde - janik.budde@fh-muenster.de
    Jan N. Tockloth - jan.tockloth@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
"""

import os
import streamlit as st
import pandas as pd

from program_files.urban_district_upscaling.pre_processing \
    import urban_district_upscaling_pre_processing
from program_files.GUI_st.GUI_st_global_functions \
    import st_settings_global, import_GUI_input_values_json, \
    read_markdown_document

# settings the initial streamlit page settings
st_settings_global()

# opening the input value dict, which will be saved as a json
GUI_udu_dict = {}

# Import GUI help comments from the comment json and safe as an dict
GUI_helper = import_GUI_input_values_json(
    os.path.dirname(os.path.dirname(__file__))
    + "/GUI_st_help_comments.json")


def us_application() -> None:
    """
        Definition of the sidebar elements for the urban district
        upscaling page and starting a udu tool run.

        :returns: - **input_us_sheet** \
                    (streamlit.runtime.uploaded_file_manager.UploadedFile) - \
                    Streamlit varibale including the uploaded upscaling_sheet \
                    (was a xlsx before)
                - **input_standard_parameter** \
                    (streamlit.runtime.uploaded_file_manager.UploadedFile) - \
                    Streamlit varibale including the uploaded \
                    standard_parameter_sheet (was a xlsx before)
    """

    # create form-submit element for multiple inputs
    with st.sidebar.form("Input Parameters"):

        if "state_submitted_us_run" not in st.session_state:
            st.session_state["state_submitted_us_run"] = False

        # input us sheet
        input_us_sheet = st.file_uploader(
            label="Import your upscaling sheet:",
            help=GUI_helper["udu_fu_us_sheet"])

        # input standard parameter sheet
        input_standard_parameter = st.file_uploader(
            label="Import your standard parameter sheet:",
            help=GUI_helper["udu_fu_sp_sheet"])

        # text input to define the file name
        GUI_udu_dict["result_file_name"] = \
            st.text_input(label="Type in your model definition file name.",
                          help=GUI_helper["udu_ti_model_def_name"])

#TODO: add GUI help comments
        # expander for weather data settings
        with st.expander(label="Open Fred Weather Data"):

            # input if open fres weather data should be added
            GUI_udu_dict["input_open_fred"] = st.checkbox(
                label="Download Open Fred Weather Data",
                help=GUI_helper["udu_cb_weather_data"])

            # coordinate input for weather data download
            # longitude coordinates
            GUI_udu_dict["input_cords_lon"] = st.text_input(
                label="Longitude Coordinates",
                help=GUI_helper["udu_ti_coords_lon"])
            # latitude coordinates
            GUI_udu_dict["input_cords_lat"] = st.text_input(
                label="Latitude Coordinates",
                help=GUI_helper["udu_ti_coords_lat"])

        # Submit button to start optimization.
        st.session_state["state_submitted_us_run"] = st.form_submit_button(
                label="Start US Tool",
                help=GUI_helper["udu_fs_start_US_tool"])

    return input_us_sheet, input_standard_parameter


def create_model_definition(input_us_sheet, input_standard_parameter) -> bytes:
    """
    Creates the model definition, after the process was started in the GUI.

    :param input_us_sheet: uploaded upscaling sheet
    :type input_us_sheet: streamlit.runtime.uploaded_file_manager.UploadedFile
    :param input_standard_parameter: uploaded standard parameter sheet
    :type input_standard_parameter: 
        streamlit.runtime.uploaded_file_manager.UploadedFile

    :return: - **model_definition_df** (bytes) - Bytes object which \
        represents the downloadable model definition .

    """

    # prepare the us_path_list as an input for the 
    # urban_district_upscaling_pre_processing function
    us_path_list = [
        input_us_sheet,
        input_standard_parameter,
        GUI_udu_dict["result_file_name"],
        os.path.join(
            os.path.dirname(__file__),
            r"../../urban_district_upscaling/plain_scenario.xlsx")
    ]
    
    open_fred_list = [
        GUI_udu_dict["input_open_fred"],
        GUI_udu_dict["input_cords_lon"],
        GUI_udu_dict["input_cords_lat"]
    ]

    # running the main function
    model_definition_df = \
        urban_district_upscaling_pre_processing(
            paths=us_path_list,
            open_fred_list=open_fred_list,
            clustering=False,
            clustering_dh=False)

    # returning the created model_definition
    return model_definition_df


def us_application_downloader(model_definition) -> None:
    """
        Creating download button for the created model definition.

        :param model_definition: model_definition which was created before
            based on the user input (uploaded files us_sheet and
            standard_parameter_sheet)
        :type model_definition: bytes
    """

    # create download button
    st.sidebar.download_button(label="Download your model definition",
                               data=model_definition,
                               file_name=GUI_udu_dict["result_file_name"]
                               + ".xlsx",
                               help=GUI_helper["udu_b_download_model_def"])


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


# second column
def udu_preprocessing_page(model_definition) -> None:
    """
        Definition of the page elements after the urban district
        upscaling tool ran.

        :param model_definition: model_definition which was created before
            based on the user input (uploaded files us_sheet and
            standard_parameter_sheet)
        :type model_definition: bytes
    """

    # define header
    st.header("Model defintion")

    # create model defnition table
    xls = pd.ExcelFile(model_definition)
    tabs = xls.sheet_names
    # without info column
    tabs.pop(0)
    tab_bar = st.tabs(tabs)
    for i in range(len(tabs)):
        with tab_bar[i]:
            df_input = xls.parse(tabs[i])
            df_input = df_input.astype(str)
            st.dataframe(df_input)


# running sidebar elements
us_sheet, sp_sheet = us_application()
# running the start / main page if tool did not run yet
if st.session_state["state_submitted_us_run"] is not True:
    standard_page()

# raise warning if an necessary input is missing
elif us_sheet == "" \
    or sp_sheet == "" \
        or GUI_udu_dict["result_file_name"] == "":

    st.warning("One of the necessary input fields is missing.\
               Make sure to upload both files and insert a file name.")

# run udu tool and create model definition
else:
    # run tool
    model_definition = \
        create_model_definition(input_us_sheet=us_sheet,
                                input_standard_parameter=sp_sheet)

    # running preprocessing page if tool ran
    udu_preprocessing_page(model_definition=model_definition)
    us_application_downloader(model_definition=model_definition)
