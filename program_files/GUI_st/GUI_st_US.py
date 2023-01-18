import streamlit as st
import pandas as pd
import os

from program_files.urban_district_upscaling.pre_processing import urban_district_upscaling_pre_processing


def us_application():
    with st.sidebar.form("Input Parameters"):
        # message that the file is beeing created
        if "created" not in st.session_state:
            st.session_state["created"] = "note done"
        # Submit button to start optimization.
        submitted_us_run = st.form_submit_button("Start US hallo Tool", on_click=creating_xlsx)
        if st.session_state["created"] == "done":
            st.success("The model definition ist being created.")

        # tabs to create the model definition
        tab_us, tab_sp, tab_md = st.tabs(["sheet 1", "sheet 2", "sheet 3"])

        with tab_us:
            # input us sheet
            input_us_sheet_path = st.file_uploader("Import your upscaling sheet:")

        with tab_sp:
            # input standard parameter sheet
            input_standardparam_path = st.file_uploader("Import your standard parameter sheet:")

        with tab_md:
            # input model definition sheet
            input_result_path = st.file_uploader("Import your model definition:")

        # Run program main function if start button is clicked
        if submitted_us_run:
            if input_us_sheet_path != "" and input_standardparam_path != "" and input_result_path != "":
                # strings replace due to variables defined above
                us_path_list = [
                    input_us_sheet_path,
                    input_standardparam_path,
                    input_result_path,
                    os.path.join(
                        os.path.dirname(__file__),
                        r"../urban_district_upscaling/plain_scenario.xlsx")
                ]

                urban_district_upscaling_pre_processing(paths=us_path_list, clustering=False, clustering_dh=False)

    udu_page = st.container()

    with udu_page:
        introduction, overview_md = st.columns([2, 1])
        introduction.markdown(" # Urban District Upscaling Tool")
        introduction.markdown(" Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor"
                              " incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
                              "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
                              "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu "
                              "fugiat nulla pariatur. "
                              "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia "
                              "deserunt mollit anim id est laborum. ")
        overview_md.markdown(" # Model definition ")

        if "xlsx" not in st.session_state:
            st.session_state["xlsx"] = "not done"
        test = overview_md.file_uploader("Model definition", on_change=change_xlsx_state)
        if st.session_state["xlsx"] == "done":
            overview_md.success("xlsx file uploaded successfully")

            with st.expander("Show the sinks of the model definition"):
                model_definition = pd.ExcelFile(test)
                df1 = pd.read_excel(model_definition, 'sinks')
                st.dataframe(df1)


def change_xlsx_state():
    st.session_state["xlsx"] = "done"


def creating_xlsx():
    st.session_state["created"] = "done"
