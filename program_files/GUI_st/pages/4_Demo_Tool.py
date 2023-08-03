"""
    Jan N. Tockloth - jan.tockloth@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
    Christian Klemm - christian.klemm@fh-muenster.de
    Benjamin Blankenstein - bb917322@fh-muenster.de
"""

import os
import glob
import openpyxl
import streamlit as st
import pandas as pd
from program_files.preprocessing.Spreadsheet_Energy_System_Model_Generator \
    import sesmg_main
from program_files.GUI_st.GUI_st_global_functions import \
    st_settings_global, read_markdown_document, import_GUI_input_values_json, \
    get_bundle_dir

# Import GUI help comments from the comment json and safe as a dict
GUI_helper = import_GUI_input_values_json(
    os.path.dirname(os.path.dirname(__file__)) + "/GUI_st_help_comments.json")

# creating global model run mode dict
mode_dict = {
    "monetary": ["Total System Costs", "Total Constraint Costs"],
    "emissions": ["Total Constraint Costs", "Total System Costs"],
}

# creating global input values dict
input_values_dict = {}

# define main path to SESMG main folder
mainpath_mf = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(__file__))))
# define main path to SESMG program files folder
mainpath_pf = os.path.join(mainpath_mf, "program_files")
# define main path to SESMG results/demo folder
mainpath_rdf = os.path.join(mainpath_mf, "results", "demo")

# setting initial session state for mdoel run
if "state_submitted_demo_run" not in st.session_state:
    st.session_state["state_submitted_demo_run"] = "not done"


def dt_input_sidebar() -> dict:
    """
        Creating the demo tool input values in the sidebar.

        :return: **input_values_dict** (dict) - Dict of input values \
            from the GUI sidebar
    """

    with st.sidebar.form("Simulation input"):

        # input value for model run name
        st.text_input(label="Name",
                      value="")

        # input value for photovoltaics
        input_values_dict["input_pv"] = st.number_input(
            label="Photovoltaic in kW",
            min_value=0,
            max_value=10000,
            step=1)

        # input value for solar thermal
        input_values_dict["input_st"] = st.number_input(
            label="Solar Thermal in kW",
            min_value=0,
            max_value=27700,
            step=1)

        # input value for air source heat pump
        input_values_dict["input_ashp"] = st.number_input(
            label="Air source heat pump in kW",
            min_value=0,
            max_value=5000,
            step=1)

        # input value for ground coupled heat pump
        input_values_dict["input_gchp"] = st.number_input(
            label="Ground coupled heat pump in kW",
            min_value=0,
            max_value=5000,
            step=1)

        # input value for central thermal storage
        input_values_dict["input_battery"] = st.number_input(
            label="Battery in kWh",
            min_value=0,
            max_value=10000,
            step=1,
            help=GUI_helper["demo_ni_kw_kwh"])

        # input value for decentral thermal storage
        input_values_dict["input_dcts"] = st.number_input(
            label="Thermal Storage (decentral) in kWh",
            min_value=0,
            max_value=10000,
            step=1,
            help=GUI_helper["demo_ni_kw_kwh"])

        # selectbox for the scize of the District Heating Network
        input_dh = st.selectbox(
            label="District Heating Network",
            options=["No District Heating Network", "urban", "sub-urban",
                     "rural"],
            help=GUI_helper["demo_sb_heat_network_chp"])

        # If input_dh is equal to the name of the options, then the \
        # values for the input parameters in input_values_dict are taken from \
        # the params dictionary. Otherwise, the values are set binary.
        # Vales are set according to the chosen dh network.

        if input_dh == "No District Heating Network":
            input_values_dict["input_chp_urban"] = 0
            input_values_dict["input_dh_urban"] = 0
            input_values_dict["input_chp_sub_urban"] = 0
            input_values_dict["input_dh_sub_urban"] = 0
            input_values_dict["input_chp_rural"] = 0
            input_values_dict["input_dh_rural"] = 0

        elif input_dh == "urban":
            input_values_dict["input_chp_urban"] = 1
            input_values_dict["input_dh_urban"] = 1
            input_values_dict["input_chp_sub_urban"] = 0
            input_values_dict["input_dh_sub_urban"] = 0
            input_values_dict["input_chp_rural"] = 0
            input_values_dict["input_dh_rural"] = 0

        elif input_dh == "sub-urban":
            input_values_dict["input_chp_urban"] = 1
            input_values_dict["input_dh_urban"] = 1
            input_values_dict["input_chp_sub_urban"] = 1
            input_values_dict["input_dh_sub_urban"] = 1
            input_values_dict["input_chp_rural"] = 0
            input_values_dict["input_dh_rural"] = 0

        elif input_dh == "rural":
            input_values_dict["input_chp_urban"] = 1
            input_values_dict["input_dh_urban"] = 1
            input_values_dict["input_chp_sub_urban"] = 1
            input_values_dict["input_dh_sub_urban"] = 1
            input_values_dict["input_chp_rural"] = 1
            input_values_dict["input_dh_rural"] = 1

        # create slider to choose the optimization criterion
        input_values_dict["input_criterion"] = st.select_slider(
            label="Optimization Criterion",
            options=("monetary", "emissions"))

        # button to run the demotool
        st.form_submit_button(label="Start Simulation",
                              on_click=change_state_submitted_demo_run)

        if st.form_submit_button:
            return input_values_dict

    return None


def execute_sesmg_demo(demo_file: str, demo_results: str, mode: str) -> None:
    """
        Executes the optimization algorithm.

        :param demo_file: path to the model definition file which is \
            creating the demo tool
        :type demo_file: str
        :param demo_results: path to the demo tool result folder
        :type demo_results: str
        :param mode: optimization criterion which is chosen in the GUI
        :type mode: str
    """

    # activate criterion switch if run is optimized to its emissions
    if mode == "emissions":
        criterion_switch = True
    else:
        criterion_switch = False

    # run sesmg main function with reduced / fixed input options
    sesmg_main(
        model_definition_file=demo_file,
        result_path=demo_results,
        num_threads=1,
        timeseries_prep=["None", "None", "None", "None", 0],
        graph=False,
        criterion_switch=criterion_switch,
        xlsx_results=False,
        console_results=False,
        solver="cbc",
        cluster_dh=False,
        district_heating_path=""
    )

    # reset st.session_state["state_submitted_demo_run"] to stop rerun when
    # switching to Demo Tool multipage again
    st.session_state["state_submitted_demo_run"] = "not done"


def create_demo_model_definition() -> None:
    """
        Modifies the demo model definition.
    """

    xfile = openpyxl.load_workbook(
        mainpath_pf
        + "/demo_tool/v0.4.0_demo_model_definition/demo_model_definition.xlsx",
        data_only=True)

    # PHOTOVOLTAICS
    sheet = xfile["sources"]
    sheet["I3"] = input_values_dict["input_pv"]
    sheet["J3"] = input_values_dict["input_pv"]
    # SOLAR THERMAL
    sheet["I5"] = input_values_dict["input_st"]
    sheet["J5"] = input_values_dict["input_st"]
    # BATTERY
    sheet = xfile["storages"]
    sheet["N3"] = input_values_dict["input_battery"]
    sheet["O3"] = input_values_dict["input_battery"]
    # THERMAL STORAGE
    sheet["N5"] = input_values_dict["input_dcts"]
    sheet["O5"] = input_values_dict["input_dcts"]
    # GCHP
    sheet = xfile["transformers"]
    sheet["L7"] = input_values_dict["input_gchp"]
    sheet["M7"] = input_values_dict["input_gchp"]
    # ASHP
    sheet["L8"] = input_values_dict["input_ashp"]
    sheet["M8"] = input_values_dict["input_ashp"]

    # THERMAL STORAGE
    # sheet = xfile["storages"]
    # sheet["C4"] = input_values_dict["input_dh"]
    # sheet["N4"] = input_values_dict["input_cts"]
    # sheet["O4"] = input_values_dict["input_cts"]

    # DISTRICT HEATING AND CHP
    sheet = xfile["links"]
    sheet["C3"] = input_values_dict["input_dh_urban"]
    sheet["C4"] = input_values_dict["input_dh_sub_urban"]
    sheet["C5"] = input_values_dict["input_dh_rural"]
    sheet = xfile["transformers"]
    sheet["C4"] = input_values_dict["input_chp_urban"]
    sheet["C5"] = input_values_dict["input_chp_sub_urban"]
    sheet["C6"] = input_values_dict["input_chp_rural"]

    # check if /demo exists in results direcotry
    if mainpath_rdf \
            not in glob.glob(os.path.join(mainpath_mf, "results", "*")):
        # create /results/demo directory
        os.mkdir(path=os.path.join(mainpath_rdf))

    # safe motified xlsx file in the results/demo folder
    xfile.save(os.path.join(mainpath_rdf, "model_definition.xlsx"))

    # run sesmg DEMO version
    execute_sesmg_demo(
        demo_file=mainpath_rdf + r"/model_definition.xlsx",
        demo_results=mainpath_rdf,
        mode=input_values_dict["input_criterion"])


def show_demo_run_results(mode: str) -> None:
    """
        Loading and displaying demo run results.

        :param mode: optimization criterion which is chosen in the GUI
        :type mode: str
    """

    # load summary.csv from results/demo /emissions or /monetary folder
    # which was replaced with the model run above
    df_summary = pd.read_csv(mainpath_rdf + r"/summary.csv")

    # change dimension of the values to Mio.€/a and t/a
    annual_costs = float(df_summary[mode_dict.get(mode)[0]] / 1000000)

    annual_emissions = float(df_summary[mode_dict.get(mode)[1]] / 1000000)

    # calculate relative change refered to the status quo
    # costs in Mio.€/a
    stat_quo_costs = 13.68616781
    # emissions in t/a
    stat_quo_emissions = 17221.43690357
    # relative values as str
    rel_result_costs = \
        str(round((annual_costs-stat_quo_costs) / stat_quo_costs * 100, 2)) \
        + " %"
    rel_result_emissions = \
        str(round(
            (annual_emissions-stat_quo_emissions) /
            stat_quo_emissions * 100, 2)) \
        + " %"

    # Display and import simulated cost values from summary dataframe
    st.subheader("Your solution:")
    # create metrics
    cost1, cost2 = st.columns(2)
    cost1.metric(
        label="Annual Costs in Mil. €",
        value=round(annual_costs, 2),
        delta=rel_result_costs,
        delta_color="inverse")
    cost2.metric(
        label="Annual Costs in t",
        value=round(annual_emissions, 2),
        delta=rel_result_emissions,
        delta_color="inverse")


def demo_start_page() -> None:
    """
        Start page text, images and tables for the demo tool.
    """
    

    # import markdown text from GUI files
    imported_markdown = read_markdown_document(
        document_path="docs/GUI_texts/demo_tool_text.md",
        folder_path=f'{"docs/images/manual/DemoTool/*"}')

    # show markdown text
    st.markdown(''.join(imported_markdown), unsafe_allow_html=True)

    # upload demo tool graph image
    img = str(get_bundle_dir()) \
          + "/docs/images/manual/DemoTool/demo_system_graph.png"
    st.image(img, caption="", width=500)

    # import markdown tables from GUI files
    imported_markdown = read_markdown_document(
        document_path="docs/GUI_texts/demo_tool_tables.md",
        folder_path=f'{"docs/images/manual/DemoTool/*"}')

    # show markdown text
    st.markdown(''.join(imported_markdown), unsafe_allow_html=True)

    # upload dh image
    img = str(get_bundle_dir()) \
          + "/docs/images/manual/DemoTool/district_heating_network.png"
    st.image(img, caption="", width=500)


def change_state_submitted_demo_run() -> None:
    """
        Setup session state for the demo run form-submit as an change
        event as on-click to switch the state.
    """
    st.session_state["state_submitted_demo_run"] = "done"


# run demo application
# initialize global streamlit settings
st_settings_global()

# run demotool input sidebar
input_values_dict = dt_input_sidebar()

# creating main demo tool
# loading start page
demo_start_page()


# show results after submit button was clicked
if st.session_state["state_submitted_demo_run"] == "done":
    # create demo model definition and start model run
    create_demo_model_definition()
    # show generated results
    show_demo_run_results(mode=input_values_dict["input_criterion"])
