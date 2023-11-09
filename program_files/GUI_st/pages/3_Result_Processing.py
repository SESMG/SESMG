"""
    Jan N. Tockloth - jan.tockloth@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
    Janik Budde - janik.budde@fh-muenster.de
"""
import glob
import os
import multiprocessing

import dash
from dash import html, dash_table
import streamlit as st
from streamlit.components.v1 import iframe
import pandas as pd
import plotly.express as px

from program_files.GUI_st.GUI_st_global_functions import \
    import_GUI_input_values_json, st_settings_global, read_markdown_document, \
    load_result_folder_list, show_error_with_link, short_result_graph, \
    create_exception_for_failed_runs


def result_processing_sidebar() -> None:
    """
        Function to create the sidebar.
    """

    # Import GUI help comments from the comment json and safe as an dict
    GUI_helper = import_GUI_input_values_json(
        os.path.dirname(os.path.dirname(__file__))
        + "/GUI_st_help_comments.json")

    # create sidebar
    with st.sidebar:
        st.header("Result Overview")

        # read sub folders in the result folder directory
        existing_result_foldernames_list = load_result_folder_list()

        # create select box with the folder names which are in the
        # results folder
        existing_result_folder = st.selectbox(
            label="Choose the result folder",
            options=existing_result_foldernames_list,
            help=GUI_helper["res_dd_result_folder"])

        # check box if user wants to reload existing results
        run_existing_results = st.button(label="Load Existing Results",
                                         help=GUI_helper["res_b_load_results"])

        if run_existing_results:
            # set session state with full folder path to the result folder
            st.session_state["state_result_path"] = \
                os.path.join(os.path.dirname(os.path.dirname(
                                os.path.dirname(os.path.dirname(
                                    os.path.abspath(__file__))))),
                             "results",
                             existing_result_folder)

            # set session state with full folder path to the pareto result folder (added)
            st.session_state["state_pareto_result_path"] = \
                os.path.join(os.path.dirname(os.path.dirname(
                    os.path.dirname(os.path.dirname(
                        os.path.abspath(__file__))))),
                    "results",
                    existing_result_folder)

        if st.session_state["state_result_path"] != "not set" and \
                os.path.join(st.session_state["state_result_path"],
                             "components.csv") \
                not in glob.glob(st.session_state["state_result_path"] + "/*"):
            # header
            st.header("Pareto Results")

            # read out sub folders of pareto list
            existing_result_foldernames_list = next(
                os.walk(st.session_state["state_result_path"]))[1]
            # split folder names and safe pareto point positions in a list
            pareto_points_list = [directory.split(
                "_")[-2] for directory in existing_result_foldernames_list]

            # create dict with pareto point positions and folder names
            pareto_folder_dict = dict(
                zip(pareto_points_list, existing_result_foldernames_list))
            # sort pareto point list
            pareto_points_list.sort()
            # create select box to choose the pareto point you want to see
            # show results for
            pareto_point_chosen = st.selectbox(
                label="Choose the pareto point",
                options=pareto_points_list,
                help=GUI_helper["res_dd_pareto_point"])

            # create session_state to initialize the pareto result overviews
            st.session_state["state_pareto_point_chosen"] = pareto_point_chosen
            st.session_state["state_pareto_result_path"] = \
                os.path.join(st.session_state["state_result_path"],
                             pareto_folder_dict[pareto_point_chosen])
            # st.session_state["state_pareto_result_path"] = \
            #     st.session_state["state_result_path"] + \
            #     "/" + pareto_folder_dict[pareto_point_chosen]


def short_result_summary_time(result_path_summary) -> None:
    """
        Function displaying the results time series information.

        :param result_path_summary: path to a result summary.csv file
        :type result_path_summary: str
    """
    st.subheader("Result Overview")
    # Import summary.csv and create dataframe
    df_summary = pd.read_csv(result_path_summary)
    # Display and import time series values
    # adding two blank rows
    time1, time2, time3, time4 = st.columns(4)
    time1.metric(label="Start Date", value=str(df_summary.iloc[0, 0]))
    time2.metric(label="End Date", value=str(df_summary.iloc[0, 1]))
    time3.metric(label="Temporal Resolution",
                 value=str(df_summary['Resolution'][0]))


def short_result_summary_system(result_path_summary) -> None:
    """
        Function displaying the short result summary overview of the
        energy system.

        :param result_path_summary: path to a result summary.csv file
        :type result_path_summary: str
    """
    # Import summary.csv and create dataframe
    df_summary = pd.read_csv(result_path_summary)
    # Create list with headers
    summary_headers = list(df_summary)
    # add the energy system costs
    cost1, cost2, cost3, cost4 = st.columns(4)
    cost1.metric(label=summary_headers[3], value="{:,.2f}".format(float(round(
        df_summary[summary_headers[3]], 1))))
    cost2.metric(label=summary_headers[4], value="{:,.2f}".format(float(round(
        df_summary[summary_headers[4]], 1))))
    cost3.metric(label=summary_headers[5], value="{:,.2f}".format(float(round(
        df_summary[summary_headers[5]], 1))))
    cost4.metric(label=summary_headers[6], value="{:,.2f}".format(float(round(
        df_summary[summary_headers[6]], 1))))

    # Display and import simulated energy values from summary dataframe
    # adding two blank rows
    ener1, ener2, ener3, ener4 = st.columns(4)
    ener1.metric(label=summary_headers[7], value="{:,.2f}".format(float(round(
        df_summary[summary_headers[7]], 1))))
    ener2.metric(label=summary_headers[8], value="{:,.2f}".format(float(round(
        df_summary[summary_headers[8]], 1))))


def short_result_simplifications(result_GUI_settings_dict: dict) -> None:
    """
        Function to display model simplification settings in addition
        to the timeseries information.

        :param result_GUI_settings_dict: dict including the last runs \
            GUI settings
        :type result_GUI_settings_dict: dict
    """
    alg1, alg2 = st.columns(2)
    alg1.metric(label="Simplification Algorithm",
                value=result_GUI_settings_dict["input_timeseries_algorithm"])
    # create 5 columns. one for each simplification input field
    simp1, simp2, simp3, simp4 = st.columns(4)
    simp1.metric(
        label="Simplification Index",
        value=result_GUI_settings_dict["input_timeseries_cluster_index"])
    simp2.metric(
        label="Cluster Criterion",
        value=result_GUI_settings_dict["input_timeseries_criterion"])
    simp3.metric(
        label="Simplification Period",
        value=result_GUI_settings_dict["input_timeseries_period"])
    simp4.metric(
        label="Cluster Season",
        value=result_GUI_settings_dict["input_timeseries_season"])


def short_result_premodelling(result_GUI_settings_dict: dict) -> None:
    """
        Function to display premodel settings in addition to the
        timeseries information.

        :param result_GUI_settings_dict: dict including the last
            runs GUI settings
        :type result_GUI_settings_dict: dict
    """
    # check if investment boundaries were active to show tightening factor
    # create columns for pre-modelling information
    # adding one optional for tightening factor and one blank
    pre1, pre2, pre3, pre4 = st.columns(4)
    pre1.metric(
        label="Premodelling Active",
        value=result_GUI_settings_dict["input_activate_premodeling"])
    pre2.metric(
        label="Investment Bounderies",
        value=result_GUI_settings_dict["input_premodeling_invest_boundaries"])
    if result_GUI_settings_dict["input_premodeling_invest_boundaries"]:
        pre3.metric(
            label="Tightening Factor",
            value=result_GUI_settings_dict
            ["input_premodeling_tightening_factor"])


def start_dash_server(df_components) -> None:
    """
        function to start dash application
        :param df_components: df containing all components for the result table
    """

    # create table
    # start Dash-App
    app = dash.Dash(__name__, suppress_callback_exceptions=True)

    # Layout of the Dash-App
    app.layout = html.Div([
        dash_table.DataTable(
            data=df_components.to_dict('records'),
            columns=[{'id': c, 'name': c} for c in df_components.columns],
            filter_action='native',  # activates filter
            page_action='none',  # 'none' deactivates the pagination
            fixed_rows={'headers': True},  # fixed headers also when scrolling down in the table
            style_table={'height': '400'}
        )
    ])
    # set port
    app.run_server(port=8503, debug=True, use_reloader=False)

# TODO ich habe diese Funktionen einmal drin gelassen, mache es aber jetzt über die streamlit tabelle


def dash_result_table(result_path_components: str) -> None:
    """
        Function to create table of components.

        :param result_path_components: path to a result components.csv \
            file
        :type result_path_components: str
    """

    # Header
    st.subheader("Result Table")

    # Import components.csv and create dataframe
    df_components = pd.read_csv(result_path_components)

    # starting parallel dash process
    dash_process = multiprocessing.Process(target=start_dash_server, args=(df_components,))
    dash_process.start()

    # waiting for the end of the dash application to avoid an endless dash process
    dash_process.join()

    # URL for the Dash-Application
    dash_app_url = "http://127.0.0.1:8503/"

    # Using the dash-table in streamlit
    iframe(dash_app_url, width=1000, height=500)


def short_result_table(result_path_components: str) -> None:
    """
        Function to create table of components.

        :param result_path_components: path to a result components.csv \
            file
        :type result_path_components: str
    """

    # Header
    st.subheader("Result Table")

    # Import components.csv and create dataframe
    df_components = pd.read_csv(result_path_components)

    # chosing between small table and table with whole data
    with st.form("my_form"):

        # formular-submit-button
        submit_button = st.form_submit_button("Show complete table")

        if submit_button:
            # Toggle the value of show_complete_table
            st.session_state.show_complete_table = not st.session_state.get("show_complete_table", False)

    # create table
    # set min hight which is the header height
    ag_min_height = 47
    # set right per row
    ag_row_height = 33.5
    # calculate logical height based on the df length
    logical_df_height = ag_min_height + len(df_components) * ag_row_height
    # set maximum height for Table
    ag_max_height = 200

    # set table height based on the button state
    if st.session_state.get("show_complete_table", False):
        # if button was clicked, set height to None
        table_height = None
    else:
        # otherwise, calculate minimum height
        table_height = int(min(logical_df_height, ag_max_height))

    # create streamlit table
    st.data_editor(df_components,
                   height=table_height,
                   use_container_width=True  # desired height in pixels
                   )


def short_result_interactive_dia(result_path_results: str) -> None:
    """
        Function to create interactive results.

        :param result_path_results: path to a result results.csv file
        :type result_path_results: str
    """
    # Header
    st.subheader("Interactive Results")
    # loading result.csv as a dataframe
    result_df = pd.read_csv(result_path_results)
    # creating column headers to select
    column_headers_result = list(result_df.columns.values)
    # column headers without date
    list_headers = column_headers_result[1:]
    # selecting headers
    select_headers = st.multiselect("Select a bus:", list_headers)
    # filtered dataframe
    filtered_df = result_df[select_headers]
    # plotting
    fig = px.line(filtered_df).update_layout(
        xaxis_title="timestep (hour)",
        yaxis_title="performance (kW) / storage capacity (kWh)")
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)


def create_energy_amounts_diagram(result_path_amounts: str) -> None:
    """
        Function to create energy amount diagrams in streamlit.

        :param result_path_amounts: path to a result heat_amounts.csv \
            or elec_amounts.csv file
        :type result_path_amounts: str
    """
    # loading result.csv as a dataframe
    amounts_df = pd.read_csv(result_path_amounts)
    amounts_df = amounts_df.loc[:, (amounts_df != 0).any(axis=0)]

    # creating column headers to select
    column_headers_amount = list(amounts_df.columns.values)
    # column headers without date
    list_headers = column_headers_amount[1:]

    # create plotly chart
    fig = px.area(amounts_df, x="reductionco2", y=list_headers).update_layout(
        xaxis_title="Reduced GHG emissions in percentage of the \
            maximum potential reduction (%)",
        yaxis_title="energy amounts (kWh)")
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)


def show_energy_amounts(result_path_heat_amounts: str,
                        result_path_elec_amounts: str) -> None:
    """
        Function to create heat amounts.

        :param result_path_heat_amounts: path to a result \
            heat_amounts.csv file
        :type result_path_heat_amounts: str
        :param result_path_elec_amounts: path to a result \
            elec_amounts.csv file
        :type result_path_elec_amounts: str
    """
    # Header
    st.subheader("Energy Amount Diagrams")

    with st.subheader("Energy Amounts"):
        tab1, tab2 = st.tabs(["Heat Amounts", "Electricity Amounts"])
        # create heat amount diagram
        with tab1:
            create_energy_amounts_diagram(
                result_path_amounts=result_path_heat_amounts)
        # create elec amount diagram
        with tab2:
            create_energy_amounts_diagram(
                result_path_amounts=result_path_elec_amounts)

    # comment that diagrams are not always valid / can be wrong
    st.write("Info: The energy amount diagrams are only valid if the model \
             definition created with the Urban Upscaling Tool. \
             Otherwise there is no guarantee that there are no components \
             missing in the diagrams. Note that only components considered \
             during the optimization are shown as option for vizualization.")


def show_pareto(result_path_pareto: str) -> None:
    """
        Function to create heat amounts.

        :param result_path_pareto: path to a result \
            pareto.csv file
        :type result_path_pareto: str
    """
    # Header
    st.subheader("Pareto Diagram")

    # load pareto.csv
    pareto_df = pd.read_csv(result_path_pareto)
    # create and show pareto plot incl. point values
    fig = px.line(pareto_df,
                  x="costs",
                  y="emissions",
                  markers=True,
                  hover_data=["costs", "emissions"],
                  labels={"costs": "costs (EUR / a)",
                          "emissions": "emissions (g CO<sub>2</sub> / a)"}
                  )
    fig.update_traces(textposition="top right")
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)


def create_exception_for_failed_runs_result_processing():
    """
    Create a streamlit exception that shows the user the energy graph if it was created before the run stopped.
    """

    # initialize session state  if no result paths are defined on main page
    if "state_result_path" not in st.session_state:
        st.session_state["state_result_path"] = "not set"
    if "state_pareto_result_path" not in st.session_state:
        st.session_state["state_pareto_result_path"] = "not set"

    # create the paths for the different safed energy graphs
    graph_file_path_normal = st.session_state["state_result_path"] + "/graph.gv.png"
    graph_file_path_pareto = st.session_state["state_pareto_result_path"] + "/graph.gv.png"

    # check if there is a pareto graph
    if os.path.isfile(graph_file_path_pareto):
        st.markdown("If the Troubleshooting is not helpful, maybe also the graph shows the mistakes:")
        short_result_graph(result_path_graph=graph_file_path_pareto)

    # check if there is no pareto graph but a graph for a normal run
    if os.path.isfile(graph_file_path_normal) and not os.path.isfile(graph_file_path_pareto):
        st.markdown("If the Troubleshooting is not helpful, maybe also the graph shows the mistakes:")
        short_result_graph(result_path_graph=graph_file_path_normal)

    # check if there is not a energy graph at all
    if not os.path.isfile(graph_file_path_pareto) and not os.path.isfile(graph_file_path_normal):
        st.markdown("No graph could be created, check the model definition again!")


try:
    # starting page functions
    # initialize global page settings
    st_settings_global()

    # initialize session state  if no result paths are defined on main page
    if "state_result_path" not in st.session_state:
        st.session_state["state_result_path"] = "not set"
    if "state_pareto_result_path" not in st.session_state:
        st.session_state["state_pareto_result_path"] = "not set"

    # start sidebar functions
    result_processing_sidebar()

    # show introduction page if no result paths are not set
    if st.session_state["state_result_path"] == "not set":
        read_markdown_document(
            document_path="docs/GUI_texts/results.md",
            folder_path=f'{"docs/images/manual/Results/*"}')

    # check if components.csv is in the result folder. Loading result page \
    # elements for a non-pareto run if so.
    elif os.path.join(st.session_state["state_result_path"], "components.csv") \
            in glob.glob(st.session_state["state_result_path"] + "/*"):

        # show short result summaries time series information
        short_result_summary_time(
            result_path_summary=st.session_state["state_result_path"]
            + "/summary.csv")

        # check if GUI settings dict is in result folder
        if os.path.join(st.session_state["state_result_path"],
                        "GUI_st_run_settings.json") \
                in glob.glob(st.session_state["state_result_path"] + "/*"):
            # import json as in a dict
            GUI_run_settings_dict = import_GUI_input_values_json(
                json_file_path=st.session_state["state_result_path"]
                + "/GUI_st_run_settings.json")
            # display some GUI settings if pre-modelling was active
            if GUI_run_settings_dict["input_timeseries_algorithm"] != "None":
                # show time series simplification settings
                short_result_simplifications(
                    result_GUI_settings_dict=GUI_run_settings_dict)
            if GUI_run_settings_dict["input_activate_premodeling"]:
                # show time series simplification settings
                short_result_premodelling(
                    result_GUI_settings_dict=GUI_run_settings_dict)
        # show short result summaries key values
        short_result_summary_system(
            result_path_summary=st.session_state["state_result_path"]
            + "/summary.csv")

        # show energy system graph
        short_result_graph(
            result_path_graph=st.session_state["state_result_path"]
            + "/graph.gv.png")
        # show components table
        short_result_table(
            result_path_components=st.session_state["state_result_path"]
            + "/components.csv")

        # show interactive result diagram
        short_result_interactive_dia(
            result_path_results=st.session_state["state_result_path"]
            + "/results.csv")

    # check if components.csv is in the result folder. Loading result page \
    # elements for a pareto run if not.
    elif os.path.join(st.session_state["state_result_path"], "components.csv") \
            not in glob.glob(st.session_state["state_result_path"] + "/*"):

        # show building specific results
        show_pareto(
            result_path_pareto=os.path.join(st.session_state["state_result_path"],
                                            "pareto.csv"))
        # show heat amount diagram
        show_energy_amounts(
            result_path_heat_amounts=st.session_state["state_result_path"]
            + "/heat_amounts.csv",
            result_path_elec_amounts=st.session_state["state_result_path"]
            + "/elec_amounts.csv")

        # open short results for the chosen pareto point incl. header
        st.subheader("Short Results for Pareto Point: " +
                     st.session_state["state_pareto_point_chosen"])
        # show short result summaries time series informations
        short_result_summary_time(
            result_path_summary=st.session_state["state_pareto_result_path"]
            + "/summary.csv")
        # check if GUI settings dict is in result folder
        if os.path.join(st.session_state["state_result_path"],
                        "GUI_st_run_settings.json") \
                in glob.glob(st.session_state["state_result_path"] + "/*"):
            # import json as in a dict
            GUI_run_settings_dict = import_GUI_input_values_json(
                json_file_path=os.path.join(
                    st.session_state["state_result_path"],
                    "GUI_st_run_settings.json"))
            # display some GUI settings if pre-modelling was active
            if GUI_run_settings_dict["input_timeseries_algorithm"] != "None":
                # show time series simplification settings
                short_result_simplifications(
                    result_GUI_settings_dict=GUI_run_settings_dict)
            if GUI_run_settings_dict["input_activate_premodeling"]:
                # show time series simplification settings
                short_result_premodelling(
                    result_GUI_settings_dict=GUI_run_settings_dict)
        # show short result summaries key values
        short_result_summary_system(
            result_path_summary=st.session_state["state_pareto_result_path"]
            + "/summary.csv")
        # show components table
        short_result_table(
            result_path_components=st.session_state["state_pareto_result_path"]
            + "/components.csv")
        # show interactive result diagram
        short_result_interactive_dia(
            result_path_results=st.session_state["state_pareto_result_path"]
            + "/results.csv")
        # show energy system graph
        short_result_graph(
            result_path_graph=st.session_state["state_pareto_result_path"]
            + "/graph.gv.png")

# Show an error message with additional information and defining a function that adds the link to the error message
except Exception as e:
    show_error_with_link()
    # display the exception along with the traceback
    st.exception(e)
    # show the graph if it was created or tell the user that no graph was created
    create_exception_for_failed_runs_result_processing()










