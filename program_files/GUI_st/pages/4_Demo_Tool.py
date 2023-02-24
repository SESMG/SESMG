"""
    @author: jtock - jan.tockloth@fh-muenster.de
    @author: GregorBecker - gregor.becker@fh-muenster.de
    @authos: chrklemm - christian.klemm@fh-muenster.de
"""

import os
import openpyxl
import streamlit as st
import pandas as pd
from program_files.preprocessing.Spreadsheet_Energy_System_Model_Generator \
    import sesmg_main
from program_files.GUI_st.GUI_st_global_functions import \
    st_settings_global


# creating global model run mode dict
mode_dict = {
    "monetary": [
        "demo_scenario_monetaer.xlsx",
        r"/results/demo/financial",
        "Total System Costs",
        "Total Constraint Costs",
    ],
    "emissions": [
        "demo_scenario_emissionen.xlsx",
        r"/results/demo/emissions",
        "Total Constraint Costs",
        "Total System Costs",
    ],
}

# creating global input values dict
input_values_dict = {}

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
        st.text_input(label="Name")

        # input value for photovoltaiks
        input_values_dict["input_pv"] = st.number_input(
            label="Photovoltaic in kW",
            min_value=0,
            max_value=10000,
            step=1000)

        # input value for solar thermal
        input_values_dict["input_st"] = st.number_input(
            label="Solar thermal in kW",
            min_value=0,
            max_value=27700,
            step=1000)

        # input value for central thermal storage
        input_values_dict["input_battery"] = st.number_input(
            label="Battery in kWh",
            min_value=0,
            max_value=10000,
            step=1000)

        # input value for combined heat and power plant in kW(electric)
        input_values_dict["input_chp"] = st.number_input(
            label="Combined heat and power plant in kW(el)",
            min_value=0,
            max_value=1000000,
            step=1000)

        # input value for ground coupled heat pump
        input_values_dict["input_gchp"] = st.number_input(
            label="Heat pump in kW",
            min_value=0,
            max_value=5000,
            step=1000)

        # # input value for central thermal storage
        # input_values_dict["input_cts"] = st.number_input(
        #     label="Thermal storage (central) in kWh",
        #     min_value=0,
        #     max_value=10000,
        #     step=1000)

        # input value for decentral thermal storage
        input_values_dict["input_dcts"] = st.number_input(
            label="Thermal storage (decentral) in kWh",
            min_value=0,
            max_value=10000,
            step=1000)

        # bool if DH network should be active
        input_dh = st.checkbox(
            label="District Heating Network")
        # 1 if True, 0 is False to fit with the model defintion sheet
        if input_dh:
            input_values_dict["input_dh"] = 1
        else:
            input_values_dict["input_dh"] = 0

        input_values_dict["input_criterion"] = st.select_slider(
            label="Optimization criterion",
            options=("monetary", "emissions"))

        st.form_submit_button(label="Start Simulation",
                              on_click=change_state_submitted_demo_run)

        if st.form_submit_button:
            return input_values_dict
    return None


def execute_sesmg_demo(demo_file, demo_results):
    """
        Excecutes the optimization algorithm.

        :param demo_file:
        :type demo_file:
        :param demo_results:
        :type demo_results:
    """

    # run sesmg main function with reduced / fixed input options
    sesmg_main(
        scenario_file=demo_file,
        result_path=demo_results,
        num_threads=1,
        timeseries_prep=["None", "None", "None", "None", 0],
        graph=False,
        criterion_switch=False,
        xlsx_results=False,
        console_results=False,
        solver="cbc",
        cluster_dh=False,
        district_heating_path=""
    )

    # reset st.session_state["state_submitted_demo_run"] to stop rerun when
    # switching to Demo Tool multipage again
    st.session_state["state_submitted_demo_run"] = "not done"


def create_demo_scenario(mode):
    """
        Modifies financial demo scenario.

        :param mode: ????????????
        :type mode: str
        :param mode: ????????????
        :type mode: dict
    """

    # define main path to SESMG program files folder
    mainpath_pf = os.path.dirname(os.path.dirname(
        os.path.dirname(__file__)))
    # define main path to SESMG main folder
    mainpath_mf = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))))

    xfile = openpyxl.load_workbook(
        mainpath_pf
        + "/Demo_Tool/v0.4.0_demo_scenario/"
        + mode_dict.get(mode)[0],
        data_only=True)

    # PHOTOVOLTAICS
    sheet = xfile["sources"]
    sheet["I3"] = input_values_dict["input_pv"]
    sheet["J3"] = input_values_dict["input_pv"]
    # SOLAR THERMAL
    sheet = xfile["sources"]
    sheet["I5"] = input_values_dict["input_st"]
    sheet["J5"] = input_values_dict["input_st"]
    # BATTERY
    sheet = xfile["storages"]
    sheet["N3"] = input_values_dict["input_battery"]
    sheet["O3"] = input_values_dict["input_battery"]
    # CHP
    sheet = xfile["transformers"]
    sheet["C4"] = input_values_dict["input_dh"]
    sheet["L4"] = input_values_dict["input_chp"]
    sheet["M4"] = input_values_dict["input_chp"]
    # ASHP
    # sheet = xfile["transformers"]
    # sheet["L6"] = input_values_dict["ASHP"]
    # sheet["M6"] = input_values_dict["ASHP"]
    # GCHP
    sheet = xfile["transformers"]
    sheet["L5"] = input_values_dict["input_gchp"]
    sheet["M5"] = input_values_dict["input_gchp"]
    # THERMAL STORAGE
    # sheet = xfile["storages"]
    # sheet["C4"] = input_values_dict["input_dh"]
    # sheet["N4"] = input_values_dict["input_cts"]
    # sheet["O4"] = input_values_dict["input_cts"]
    # THERMAL STORAGE
    sheet = xfile["storages"]
    sheet["N5"] = input_values_dict["input_dcts"]
    sheet["O5"] = input_values_dict["input_dcts"]
    # District Heating
    sheet = xfile["links"]
    sheet["C3"] = input_values_dict["input_dh"]

    # safe motified xlsx file in the results/demo folder
    xfile.save(
        mainpath_mf
        + mode_dict.get(mode)[1]
        + "/scenario.xlsx")

    # run sesmg DEMO version
    execute_sesmg_demo(
        demo_file=mainpath_mf + mode_dict.get(mode)[1] + r"/scenario.xlsx",
        demo_results=mainpath_mf + mode_dict.get(mode)[1])


def show_demo_run_results(mode):
    """
        Loading and displaying demo run results.
    """

    # define main path to SESMG main folder
    mainpath_mf = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))))

    # load summary.csv from results/demo /emissions or /monetary folder
    # which was replaced with the model run above
    df_summary = pd.read_csv(
        mainpath_mf
        + mode_dict.get(mode)[1]
        + r"/summary.csv")

    summary_headers = list(df_summary)
    # Display and import simulated cost values from summary dataframe
    cost1, cost2, cost3, cost4 = st.columns(4)
    cost1.metric(label=summary_headers[3], value=round(
        df_summary[summary_headers[3]], 1))
    cost2.metric(label=summary_headers[4], value=round(
        df_summary[summary_headers[4]], 1))
    cost3.metric(label=summary_headers[5], value=round(
        df_summary[summary_headers[5]], 1))
    cost4.metric(label=summary_headers[6], value=round(
        df_summary[summary_headers[6]], 1))


def demo_start_page():
    """
        Start page text for the demo tool.
    """

    st.header("Spreadsheet Energy System Model Generator (SESMG)")
    st.subheader("Welcome using the Demo Tool!")
    st.write("DEMO-Energy System:")
    st.write("In this DEMO the financial costs and carbon dioxide emissions \
             of a residential area are simulated. For improvement, the \
             technologies listed below are \n available with the parameters \
             below. The simulated scenarios can be compared with the status \
             quo, the financial minimum and the emission minimum.")


def demo_parameters_page():
    """
        Overview of the technical and energy system parameters.
    """

# TODO: Update to actual values and drop not used elements & unify wording!

    model_demands = [
        ["Electricity", "14 000 000 kWh/a", "h0 Load Profile"],
        ["Heat", "52 203 000 kWh/a", "EFH Load Profile"]
        ]

    model_prices = [
        ["Gas Import", "6.29 ct/kWh", "?"],
        ["Electricity Import", "31.22 ct/kWh", "366 g/kWh"],
        ["Electricity Export", "- 6.8 ct/kWh", "- 27 g/kWh"]
        ]

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
         "308 g/kWh(el), 265 g/kWh(th.)", "20 a", "endless", ""],
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

    stdf1, stdf2 = st.columns(2)
    # display dataframe for model demands
    stdf1.dataframe(data=pd.DataFrame(
        data=model_demands,
        columns=["Energy Form", "Demand", "Usage Pattern"]))

    # display dataframe for specific import & export cots
    stdf2.dataframe(data=pd.DataFrame(
        data=model_prices,
        columns=["Energy Form", "Specific Costs", "Specific Emissions"]))

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

# creating main demo tool page
# loading start page
demo_start_page()
# loading parameter overview
demo_parameters_page()

# show results after submit button was clicked
if st.session_state["state_submitted_demo_run"] == "done":
    # create demo model definition and start model run
    create_demo_scenario(mode=input_values_dict["input_criterion"])
    # show generated results
    show_demo_run_results(mode=input_values_dict["input_criterion"])
