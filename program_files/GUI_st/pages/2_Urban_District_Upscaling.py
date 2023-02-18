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
from program_files.GUI_st.GUI_st_global_functions import st_settings_global

# settings the initial streamlit page settings
st_settings_global()


def us_application():
    model_definition_df = ""
    with st.sidebar.form("Input Parameters"):
        # message that the file is being created
        if "state_created" not in st.session_state:
            st.session_state["state_created"] = "note done"
        # Submit button to start optimization.
        submitted_us_run = st.form_submit_button("Start US Tool",
                                                 on_click=creating_xlsx)
        print(st.session_state)
        if st.session_state["state_created"] == "done":
            st.success("The model definition ist ready after running process.")

        # input us sheet
        input_us_sheet_path = st.file_uploader(
            "Import your upscaling sheet:")

        # input standard parameter sheet
        input_standard_parameter_path = st.file_uploader(
            "Import your standard parameter sheet:")

        result_file_name = \
            st.text_input("Type in your model definition file name.")

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
                               file_name=result_file_name + ".xlsx")
    st.session_state["state_model_definition"] = model_definition_df


def standard_page():
    st.markdown(" # Urban District Upscaling Tool")
    st.markdown(
        " Lorem ipsum dolor sit amet, consectetur adipiscing elit, \
            sed do eiusmod tempor"
        " incididunt ut labore et dolore magna aliqua. Ut enim ad \
            minim veniam, quis nostrud "
        "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
        "Duis aute irure dolor in reprehenderit in voluptate velit esse \
            cillum dolore eu "
        "fugiat nulla pariatur. "
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui \
            officia "
        "deserunt mollit anim id est laborum."
        "FINAL TEXT MISSING")


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
