import pandas as pd
import streamlit as st
import plotly.express as px

from program_files.urban_district_upscaling.urban_district_upscaling_post_processing import *
from program_files.postprocessing.pareto_curve_plotting import *


def advanced_result_page():
    udu_page = st.container()

    with st.sidebar.form("Input Parameters"):
        tab_ov, tab_pd = st.tabs(["Overview", "Pareto"])

        with tab_ov:
            overview_comp = st.file_uploader("Upload your components.csv")
            creating_overview = st.form_submit_button("Create overview!")
            if creating_overview:
                urban_district_upscaling_post_processing(overview_comp)

        with tab_pd:
            pareto_comp = st.file_uploader("Choose your component files", accept_multiple_files=True)
            creating_pareto = st.form_submit_button("Create Pareto-Diagram!")
            pareto_comp_df = [pd.read_csv(pareto_comp[i]) for i in range(len(pareto_comp))]
            pareto_keys = [i for i in range(len(pareto_comp))]
            pareto_dict = {pareto_keys[i]: pareto_comp_df[i] for i in range(len(pareto_comp))}
            if creating_pareto:
                create_pareto_plot(pareto_dict, str(os.path.dirname(__file__) + "/final"))

    with udu_page:
        st.title("Result processing")
        with st.expander("Creating overview of the components."):
            if "overview" not in st.session_state:
                st.session_state["overview"] = "not done"
            building_specific_data = st.file_uploader("Choose your building_specific_data.csv", on_change=change_overview_state)
            if st.session_state["overview"] == "done":
                #overview = pd.ExcelFile(overview_upload)
                df_building_specific_data = pd.read_csv(building_specific_data)

                tab1, tab2 = st.tabs(["🗃 Data", "📈 Chart"])
                with tab1:
                    # show the dataframe
                    st.write(df_building_specific_data)

                with tab2:
                    # get the y values for the chart
                    column_headers = list(df_building_specific_data.columns.values)
                    # delete building column
                    #column_headers.pop(0)
                    # building specific figure
                    # todo filter due to label in order to reduce the number of buildings
                    fig = px.bar(df_building_specific_data, x="Building", y=column_headers)
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        with st.expander("Creating Pareto-Diagram"):
            if "pareto" not in st.session_state:
                st.session_state["pareto"] = "not done"
            pareto_file = st.file_uploader("Choose your pareto.csv", on_change=change_pareto_state)
            if st.session_state["pareto"] == "done":
                pareto_df = pd.read_csv(pareto_file)
                tab1, tab2 = st.tabs(["🗃 Pareto data", "📈 Pareto chart"])

                with tab1:
                    st.dataframe(pareto_df)

                with tab2:
                    fig = px.line(pareto_df, x="costs", y="emissions")
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        with st.expander("Interactive Results"):
            if "results" not in st.session_state:
                st.session_state["results"] = "not done"
            result_file = st.file_uploader("Choose your results.csv", on_change=change_interactive_results)
            if st.session_state["results"] == "done":
                # loading result.csv as a dataframe
                result_df = pd.read_csv(result_file)
                # creating column headers to select
                column_headers_result = list(result_df.columns.values)
                # column headers without date
                list_headers = column_headers_result[1:]
                # selecting headers
                select_headers = st.multiselect("Select a bus:", list_headers)
                # filtered dataframe
                filtered_df = result_df[select_headers]
                # plotting
                fig = px.line(filtered_df)
                st.plotly_chart(fig, theme="streamlit", use_container_width=True)


def change_overview_state():
    st.session_state["overview"] = "done"


def change_pareto_state():
    st.session_state["pareto"] = "done"


def change_interactive_results():
    st.session_state["results"] = "done"


advanced_result_page()
