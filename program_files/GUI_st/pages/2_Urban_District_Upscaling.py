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


def us_application():

    # Import GUI help comments from the comment json and safe as an dict
    GUI_helper = import_GUI_input_values_json(
        os.path.dirname(os.path.dirname(__file__))
        + "/GUI_st_help_comments.json")

    model_definition_df = ""
    with st.sidebar.form("Input Parameters"):

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

        # Submit button to start optimization.
        submitted_us_run = st.form_submit_button(
                label="Start US Tool",
                on_click=creating_xlsx,
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

                model_definition_df = \
                    urban_district_upscaling_pre_processing(
                        paths=us_path_list,
                        clustering=False,
                        clustering_dh=False)

    st.sidebar.download_button(label="Download your model definition",
                               data=model_definition_df,
                               file_name=result_file_name + ".xlsx",
                               help=GUI_helper["udu_b_download_model_def"])

    st.session_state["state_model_definition"] = model_definition_df
    st.session_state["state_xlsx"] = "done"


def standard_page():
    """
        Load the existing file of the us tool description and include grafics.
    """
    reduced_readme = read_markdown_document(
        document_path="docs/GUI_texts/us_tool.md",
        folder_path=f'{"docs/images/manual/UpscalingTool/*"}')

    # Display any remaining lines in the buffer list using the st.markdown() \
    # function
    st.markdown(''.join(reduced_readme), unsafe_allow_html=True)


# second column
def after_processing_page():
    st.header("Model defintion")

    if "state_xlsx" not in st.session_state:
        st.session_state["state_xlsx"] = "not done"
    if st.session_state["state_xlsx"] == "done":
        xls = pd.ExcelFile(st.session_state["state_model_definition"])
        tabs = xls.sheet_names
        # without info column
        tabs.pop(0)
        tab_bar = st.tabs(tabs)
        for i in range(len(tabs)):
            with tab_bar[i]:
                df_input = xls.parse(tabs[i])
                df_input = df_input.astype(str)
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
