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

# setting initial session state for mdoel run
if "state_submitted_demo_run" not in st.session_state:
    st.session_state["state_submitted_demo_run"] = "not done"


def dt_input_sidebar():
    """
        Creating the demotool input values in the sidebar.

        :return: **input_values_dict** (dict) - Dict of input values from the \
            GUI sidebar
    """

    input_values_dict = {}

    with st.sidebar.form("Simulation input"):

        # input value for model run name
        st.text_input(label="Name")

        # input value for photovoltaiks
        input_values_dict["input_pv"] = st.number_input(
            label="Photovoltaik in kW",
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
        input_values_dict["iput_gchp"] = st.number_input(
            label="Heat pump in kW",
            min_value=0,
            max_value=5000,
            step=1000)

        # input value for central thermal storage
        input_values_dict["input_cts"] = st.number_input(
            label="Thermal storage in kWh",
            min_value=0,
            max_value=10000,
            step=1000)

        # bool if DH network should be active
        input_dh = st.checkbox(
            label="Distric Heating Network")
        # 1 if True, 0 is False to fit with the model defintion sheet
        if input_dh:
            input_values_dict["input_dh"] = "1"
        else:
            input_values_dict["input_dh"] = "0"

        input_values_dict["input_criterion"] = st.select_slider(
            label="Optimization criterion",
            options=("monetary", "emissions"))

        st.form_submit_button(label="Start Simulation",
                              on_click=change_state_submitted_demo_run)

        if st.form_submit_button:
            return input_values_dict


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
        num_threads=2,
        timeseries_prep=["none", "none", "none", "none", 0],
        graph=False,
        criterion_switch=False,
        xlsx_results=False,
        console_results=False,
        solver="cbc",
        cluster_dh=False,
        district_heating_path=""
    )


def create_demo_scenario(mode, mode_dict, input_values_dict):
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

    st.write(xfile)
    st.write(mainpath_pf)
    st.write(mainpath_mf)

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
    sheet["L5"] = input_values_dict["iput_gchp"]
    sheet["M5"] = input_values_dict["iput_gchp"]
    # THERMAL STORAGE
    sheet = xfile["storages"]
    sheet["C4"] = input_values_dict["input_dh"]
    sheet["N4"] = input_values_dict["input_cts"]
    sheet["O4"] = input_values_dict["input_cts"]
    # THERMAL STORAGE
    # sheet = xfile["storages"]
    # sheet["N5"] = input_values_dict["thermal storage (decentralized)"]
    # sheet["O5"] = input_values_dict["thermal storage (decentralized)"]
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


def show_demo_run_results(mode, mode_dict):
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

    st.write(df_summary)

    summary_headers = list(df_summary)
    # format thousends seperator
    # df_summary = df_summary.iloc[1,:].style.format(thousands=" ",precision=0)
    # TODO: add delta functions based on the latest results
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

    # Display and import simulated energy values from summary dataframe
    # adding two blank rows
    ener1, ener2, ener3, ener4 = st.columns(4)
    ener1.metric(label=summary_headers[7], value=round(
        df_summary[summary_headers[7]], 1))
    ener2.metric(label=summary_headers[8], value=round(
        df_summary[summary_headers[8]], 1))




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

# show results after submit button was clicked
if st.session_state["state_submitted_demo_run"] == "done":
    # create demo model definition and start model run
    create_demo_scenario(mode=input_values_dict["input_criterion"],
                         mode_dict=mode_dict,
                         input_values_dict=input_values_dict)
    # show generated results
    show_demo_run_results(mode=input_values_dict["input_criterion"],
                          mode_dict=mode_dict)
