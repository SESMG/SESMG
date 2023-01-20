import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="whitegrid")
sns.set_color_codes("pastel")


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
            overview_upload = st.file_uploader("Choose your overview.xlsx", on_change=change_overview_state)
            if st.session_state["overview"] == "done":
                overview = pd.ExcelFile(overview_upload)
                df_central_comp = pd.read_excel(overview, 'decentral_components')
                # st.dataframe(df_central_comp)

                tab1, tab2 = st.tabs(["🗃 Data", "📈 Chart"])
                with tab1:
                    st.write(df_central_comp)

                with tab2:
                    fig = plt.figure()
                    df_central_comp.set_index('Building').plot(kind='bar', stacked=True)
                    #sns.barplot(data=df_central_comp, hue="Building")
                    st.pyplot(fig)



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
                    fig = plt.figure()
                    sns.lineplot(data=pareto_df, x="costs", y="emissions")
                    st.pyplot(fig)



def change_overview_state():
    st.session_state["overview"] = "done"


def change_pareto_state():
    st.session_state["pareto"] = "done"
