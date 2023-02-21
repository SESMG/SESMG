"""
@author: Janik257
@author: jtock - jan.tockloth@fh-muenster.de
@author: GregorBecker - gregor.becker@fh-muenster.de
"""

import os
import streamlit as st
import pandas as pd

from program_files.urban_district_upscaling.pre_processing \
    import urban_district_upscaling_pre_processing
from program_files.GUI_st.GUI_st_global_functions \
    import st_settings_global, import_GUI_input_values_json

# settings the initial streamlit page settings
st_settings_global()


def us_application():

    # Import GUI help comments from the comment json and safe as an dict
    GUI_helper = import_GUI_input_values_json(
        os.path.dirname(os.path.dirname(__file__))
        + "/GUI_st_help_comments.json")

    model_definition_df = ""
    with st.sidebar.form("Input Parameters"):
        # message that the file is being created
        if "state_created" not in st.session_state:
            st.session_state["state_created"] = "note done"
        # Submit button to start optimization.
        submitted_us_run = st.form_submit_button(
            label="Start US Tool",
            on_click=creating_xlsx,
            help=GUI_helper["udu_fs_start_US_tool"])

        if st.session_state["state_created"] == "done":
            st.success("The model definition ist ready after running process.")

        # input us sheet
        input_us_sheet_path = st.file_uploader(
            label="Import your upscaling sheet:",
            help=GUI_helper["udu_fu_us_sheet"])

        # input standard parameter sheet
        input_standard_parameter_path = st.file_uploader(
            label="Import your standard parameter sheet:",
            help=GUI_helper["udu_fu_sp_sheet"])

        result_file_name = \
            st.text_input(label="Type in your model definition file name.",
                          help=GUI_helper["udu_ti_model_def_name"])

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

                model_definition_df = \
                    urban_district_upscaling_pre_processing(
                        paths=us_path_list,
                        clustering=False,
                        clustering_dh=False,
                        streamlit=True)

    st.sidebar.download_button(label="Download your model definition",
                               data=model_definition_df,
                               file_name=result_file_name + ".xlsx",
                               help=GUI_helper["udu_b_download_model_def"])

    st.session_state["state_model_definition"] = model_definition_df


def standard_page():
    # Open the README.md file and read all lines
    with open("us_tool.md", 'r', encoding="utf8") as f:
        readme_line = f.readlines()
        # Create an empty buffer list to temporarily store the lines of the README.md file
        readme_buffer = []
        # Use the glob library to search for all files in the Resources directory and extract the file names
        resource_files = [os.path.basename(x) for x
                          in glob.glob(f'{"docs/images/manual/UpscalingTool/*"}')]

    # Iterate over each line of the README.md file
    for line in readme_line:
        # Append the current line to the buffer list
        readme_buffer.append(line)
        # Check if any images are present in the current line
        for image in resource_files:
            # If an image is found, display the buffer list up to the last line
            if image in line:
                st.markdown(''.join(readme_buffer[:-1]))
                # Display the image from the Resources folder using the image name from the resource_files list
                st.image(f'docs/images/manual/UpscalingTool/{image}')
                # Clear the buffer list
                readme_buffer.clear()
    # Display any remaining lines in the buffer list using the st.markdown() \
    # function
    st.markdown(''.join(readme_buffer), unsafe_allow_html=True)


# second column
def after_processing_page():
    st.header("Model defintion")

    if "state_xlsx" not in st.session_state:
        st.session_state["state_xlsx"] = "not done"
    input_model_definition = st.file_uploader(
        label="Model definition",
        on_change=change_xlsx_state)
    if st.session_state["state_xlsx"] == "done":
        tabs = pd.ExcelFile(input_model_definition).sheet_names
        # without info column
        tabs.pop(0)
        tab_bar = st.tabs(tabs)
        for i in range(len(tabs)):
            with tab_bar[i]:
                df_input = pd.read_excel(input_model_definition, tabs[i])
                st.dataframe(df_input)


def change_xlsx_state():
    st.session_state["state_xlsx"] = "done"


def creating_xlsx():
    st.session_state["state_created"] = "done"


us_application()
if st.session_state["state_model_definition"] == "":
    standard_page()
else:
    after_processing_page()
