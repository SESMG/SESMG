"""
    jtock - jan.tockloth@fh-muenster.de
    GregorBecker - gregor.becker@fh-muenster.de
    chrklemm - christian.klemm@fh-muenster.de
"""

import os
import openpyxl
import glob
import streamlit as st
import pandas as pd
from PIL import Image
from program_files.preprocessing.Spreadsheet_Energy_System_Model_Generator \
    import sesmg_main
from program_files.GUI_st.GUI_st_global_functions import \
    st_settings_global, read_markdown_document


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


def dt_input_sidebar():
    """
        Creating the demotool input values in the sidebar.

        :return: **input_values_dict** (dict) - Dict of input values from the \
            GUI sidebar
    """

    with st.sidebar.form("Simulation input"):

        # input value for model run name
        st.text_input(label="Name",
                      value="Name")

        # input value for photovoltaiks
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

        # input value for central thermal storage
        input_values_dict["input_battery"] = st.number_input(
            label="Battery in kWh",
            min_value=0,
            max_value=10000,
            step=1)

        # input value for combined heat and power plant in kW(electric)
        input_values_dict["input_chp"] = st.number_input(
            label="Combined Heat and Power Plant in kW(el)",
            min_value=0,
            max_value=1000000,
            step=1)

        # input value for ground coupled heat pump
        input_values_dict["input_gchp"] = st.number_input(
            label="Heat Pump in kW",
            min_value=0,
            max_value=5000,
            step=1)

        # # input value for central thermal storage
        # input_values_dict["input_cts"] = st.number_input(
        #     label="Thermal storage (central) in kWh",
        #     min_value=0,
        #     max_value=10000,
        #     step=1000)

        # input value for decentral thermal storage
        input_values_dict["input_dcts"] = st.number_input(
            label="Thermal Storage (decentral) in kWh",
            min_value=0,
            max_value=10000,
            step=1)

        # bool if DH network should be active
        input_dh = st.checkbox(
            label="District Heating Network")
        # 1 if True, 0 is False to fit with the model definition sheet
        if input_dh:
            input_values_dict["input_dh"] = 1
        else:
            input_values_dict["input_dh"] = 0

        input_values_dict["input_criterion"] = st.select_slider(
            label="Optimization Criterion",
            options=("monetary", "emissions"))

        st.form_submit_button(label="Start Simulation",
                              on_click=change_state_submitted_demo_run)

        if st.form_submit_button:
            return input_values_dict
    return None


def execute_sesmg_demo(demo_file, demo_results, mode):
    """
        Excecutes the optimization algorithm.

        :param demo_file:
        :type demo_file:
        :param demo_results:
        :type demo_results:
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
        scenario_file=demo_file,
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


def create_demo_model_definition(mode):
    """
        Modifies demo model definition.

        :param mode: optimization criterion which is chosen in the GUI
        :type mode: str
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
    # CHP
    sheet = xfile["transformers"]
    sheet["C4"] = input_values_dict["input_dh"]
    sheet["L4"] = input_values_dict["input_chp"]
    sheet["M4"] = input_values_dict["input_chp"]
    # GCHP
    sheet["L5"] = input_values_dict["input_gchp"]
    sheet["M5"] = input_values_dict["input_gchp"]
    # ASHP
    # sheet = xfile["transformers"]
    # sheet["L6"] = input_values_dict["ASHP"]
    # sheet["M6"] = input_values_dict["ASHP"]
    # THERMAL STORAGE
    # sheet = xfile["storages"]
    # sheet["C4"] = input_values_dict["input_dh"]
    # sheet["N4"] = input_values_dict["input_cts"]
    # sheet["O4"] = input_values_dict["input_cts"]

    # District Heating
    sheet = xfile["links"]
    sheet["C3"] = input_values_dict["input_dh"]

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


def show_demo_run_results(mode):
    """
        Loading and displaying demo run results.
    """

    # load summary.csv from results/demo /emissions or /monetary folder
    # which was replaced with the model run above
    df_summary = pd.read_csv(mainpath_rdf + r"/summary.csv")

    # change dimension of the values to Mio.€/a and t/a
    annual_costs = float(df_summary[mode_dict.get(mode)[0]] / 1000000)

    annual_emissions = float(df_summary[mode_dict.get(mode)[1]] / 1000000)

    # calculate relative change refered to the status quo
# TODO Update values!
    # costs in Mio.€/a
    stat_quo_costs = 10.70828373
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


def demo_start_page():
    """
        Start page text for the demo tool.
    """
    # import markdown text from GUI files
    imported_markdown = read_markdown_document(
        document_path="docs/GUI_texts/demo_tool.md",
        folder_path="")

    # show markdown text
    st.markdown(''.join(imported_markdown), unsafe_allow_html=True)


def demo_start_page_graph():
    """
        Imports graph to be displayed in the start page.
    """
    # import demo tool graph
    image = Image.open(
        os.path.join(mainpath_pf,
                     "demo_tool",
                     "v0.4.0_demo_model_definition",
                     "demo_system_graph.png"))

    # show image
    st.image(image)


def demo_parameters_page():
    """
        Overview of the technical and energy system parameters.
    """

# TODO: Update to actual values and drop not used elements & unify wording!

    # model_demands = [
    #     ["Electricity", "14 000 000 kWh/a", "h0 Load Profile"],
    #     ["Heat", "52 203 000 kWh/a", "EFH Load Profile"]]

    # model_prices = [
    #     ["Gas Import", "6.29 ct/kWh", "?"],
    #     ["Electricity Import", "31.22 ct/kWh", "366 g/kWh"],
    #     ["Electricity Export", "- 6.8 ct/kWh", "- 27 g/kWh"]]

    model_demands_price = [
        ["Electricity", "14 000 000 kWh/a", "h0 Load Profile",
         "Gas Import", "6.29 ct/kWh", "?"],
        ["Heat", "52 203 000 kWh/a", "EFH Load Profile",
         "Electricity Import", "31.22 ct/kWh", "366 g/kWh"],
        ["", "", "",
         "Electricity Export", "- 6.8 ct/kWh", "- 27 g/kWh"]]

    model_parameter = [
        # ['Windturbines': '2 000 000 €/MW, 8 g/kWh, 20 a, max. 29.7 MW'],
        ["Photovoltaics", "1 070 000 €/MW",
         "27 g/kWh", "20 a", "max. 10 MW", ""],
        ["Solar Thermal", "846 000 €/MW",
         "12 g/kWh", "20 a", "max. 27.7 MW", ""],
        ["Battery", "1 000 000 €/MWh",
         "3.96 kg/(kWh * a) (invest)", "20 a", "max. 10 MWh", ""],
        ["Gas Heating", "1 005 000 €/MW",
         "232g/kWh", "18 a", "endless", "0.92 %"],
        ["Combindes Heat and Power Plant", "760 000 €/MW(el.)",
         "308 g/kWh(el), 265 g/kWh(th.)", "20 a", "endless",
         "?? %(el.), ?? %(th.)"],
        ["Ground-coupled Heatpump", "1 444 000 €/MW",
         "8 g/kWh", "20 a", "max. 5 MW", ""],
        # ["Thermal Storage", "35 000 €/MWh",
        #  "743 g/(kWh * a)", "20 a", "3 % loss /d"],
        ["Thermal Storage (decentral)", "49 000 €/MWh",
         "604g/(kWh * a) (invest)", "20 a", "max. 10 MWh", "3 % loss /d"],
        ["District Heating", "86 000 000 €",
         "????", "40 a", "binary", "15 % loss"],
        # ["HEATPUMP", "22 ct/kWh", "366 g/kWh"],
        # ["Air Source Heat Pump", "1 318 000 €/MW", "12g/kWh", "18 a"],
    ]

    # stdf1, stdf2 = st.columns(2)
    # # display dataframe for model demands
    # stdf1.dataframe(data=pd.DataFrame(
    #     data=model_demands,
    #     columns=["Energy Form", "Demand", "Usage Pattern"]))

    # # display dataframe for specific import & export cots
    # stdf2.dataframe(data=pd.DataFrame(
    #     data=model_prices,
    #     columns=["Energy Form", "Specific Costs", "Specific Emissions"]))

    st.dataframe(data=pd.DataFrame(
        data=model_demands_price,
        columns=["Energy Demand", "Demand", "Usage Pattern",
                 "Energy Form", "Specific Costs", "Specific Emissions"]))

    # display dataframe for technology parameter
    st.dataframe(data=pd.DataFrame(
        data=model_parameter,
        columns=["Technology", "Specific Costs", "Specific Emissions",
                 "Design Lifetime", "Investment Capacity",
                 "Additional Information"]))


def change_state_submitted_demo_run():
    """
        Setup session state for the demo run form-submit as an \
            change event as on-click to switch the state.
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
# set columns
democol1, democol2 = st.columns(spec=[3, 1.5])
with democol1:
    # loading parameter overview
    demo_parameters_page()
with democol2:
    # loading system graph
    demo_start_page_graph()

# show results after submit button was clicked
if st.session_state["state_submitted_demo_run"] == "done":
    # create demo model definition and start model run
    create_demo_model_definition(mode=input_values_dict["input_criterion"])
    # show generated results
    show_demo_run_results(mode=input_values_dict["input_criterion"])
