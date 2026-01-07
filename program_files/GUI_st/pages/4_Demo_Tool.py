"""
    Jan N. Tockloth - jan.tockloth@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
    Christian Klemm - christian.klemm@fh-muenster.de
    Benjamin Blankenstein - benjamin.blankenstein@fh-muenster.de
    Oscar Quiroga - oscar.quiroga@fh-muenster.de
"""

import os
import openpyxl
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from datetime import datetime
from PIL import Image
from program_files.preprocessing.Spreadsheet_Energy_System_Model_Generator \
    import sesmg_main
from program_files.GUI_st.GUI_st_global_functions import \
    st_settings_global, read_markdown_document, import_GUI_input_values_json, \
    get_bundle_dir, create_result_directory, set_result_path

# Import GUI help comments from the comment json and save as a dict
GUI_helper = import_GUI_input_values_json(
    os.path.dirname(os.path.dirname(__file__)) + "/GUI_st_help_comments.json")

# creating global model run mode dict
mode_dict = {
    "monetary": ["Total System Costs", "Total Constraint Costs"],
    "emissions": ["Total Constraint Costs", "Total System Costs"],
}

# creating global input values dict
input_values_dict = {}

# define main path to SESMG program files folder
mainpath_pf = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)))
# define main path to SESMG results/demo folder
mainpath_rdf = os.path.join(set_result_path(), "demo")
# define path to SESMG results/demo/demo_pareto_results.csv file for advanced and simplified mode
path_pareto_results_simplified = os.path.join(mainpath_rdf, "demo_pareto_results_simplified.csv")
path_pareto_results_advanced = os.path.join(mainpath_rdf, "demo_pareto_results_advanced.csv")

# setting initial session state for mdoel run
if "state_submitted_demo_run" not in st.session_state:
    st.session_state["state_submitted_demo_run"] = "not done"

# Mapping of input keys to JSON help keys
help_map = {
    "input_name": "input_name",
    "input_pv": "input_pv",
    "input_st": "input_st",
    "input_ashp": "input_ashp",
    "input_gchp": "input_gchp",
    "input_battery": "input_battery",
    "input_dcts": "input_dcts",
    "input_chp": "input_chp",
    "solver_select": "solver_select",
    "input_optimization": "input_optimization"
    # Add more mappings here as needed
}

# Safe way to retrieve help text
def get_help(key):
    help_key = help_map.get(key)
    return GUI_helper.get(help_key, None)


def dt_input_sidebar() -> dict:

    """
        Creating the demo tool input values in the sidebar.

        :return: **input_values_dict** (dict) - Dict of input values \
            from the GUI sidebar
    """

    #Select the mode to use in the Demo Tool
    st.sidebar.write("Select Mode:")
    if "mode" not in st.session_state:
        st.session_state["mode"] = "simplified"
    if st.sidebar.button("Advanced Mode"):
        st.session_state["mode"] = "advanced"
    if st.sidebar.button("Simplified Mode"):
        st.session_state["mode"] = "simplified"

    input_values_dict = {}

    with st.sidebar.form("Simulation input"):

        if st.session_state["mode"] == "advanced":
            
            # input value for model run name
            input_values_dict["input_name"] = st.text_input(
                label="Name",
                value="")
            
            # input value for photovoltaics
            input_values_dict["input_pv"] = st.number_input(
                label="Photovoltaic in kW",
                min_value=0,
                max_value=10000,
                step=1,
                help=get_help("input_pv"))
            
            # input value for solar thermal
            input_values_dict["input_st"] = st.number_input(
                label="Solar Thermal in kW",
                min_value=0,
                max_value=27700,
                step=1,
                help=get_help("input_st"))
            
            # input value for air source heat pump
            input_values_dict["input_ashp"] = st.number_input(
                label="Air source heat pump in kW",
                min_value=0,
                max_value=5000,
                step=1,
                help=get_help("input_ashp"))
            
            # input value for ground coupled heat pump
            input_values_dict["input_gchp"] = st.number_input(
                label="Ground coupled heat pump in kW",
                min_value=0,
                max_value=5000,
                step=1,
                help=get_help("input_gchp"))
            
            # input value for central thermal storage
            input_values_dict["input_battery"] = st.number_input(
                label="Battery in kWh",
                min_value=0,
                max_value=10000,
                step=1,
                help=get_help("input_battery"))
            
            # input value for decentral thermal storage
            input_values_dict["input_dcts"] = st.number_input(
                label="Thermal Storage (decentral) in kWh",
                min_value=0,
                max_value=10000,
                step=1,
                help=get_help("input_dcts"))
            
            # selectbox for the scize of the District Heating Network
            input_dh = st.selectbox(
                label="District Heating Network",
                options=["No District Heating Network", "urban", "sub-urban",
                         "rural"],
                help=GUI_helper["demo_sb_heat_network_chp"])
            
            input_values_dict["input_chp"] = st.number_input(
                label="Design of a CHP",
                min_value=0,
                max_value=20000,
                step=1,
                help=get_help("input_chp"))
            
            if input_values_dict["input_chp"] < 5000:
                st.write("The CHP has a small capacity.")
            elif input_values_dict["input_chp"] < 15000:
                st.write("The CHP has a medium capacity.")
            else:
                st.write("The CHP has a high capacity.")
                
            if input_dh == "No District Heating Network":
                # If there is no district heating network, set all values 
                # to 0
                input_values_dict["input_chp_urban"] = 0
                input_values_dict["input_dh_urban"] = 0
                input_values_dict["input_chp_sub_urban"] = 0
                input_values_dict["input_dh_sub_urban"] = 0
                input_values_dict["input_chp_rural"] = 0
                input_values_dict["input_dh_rural"] = 0
                input_values_dict["input_chp_a"] = 1
                
            elif input_dh == "urban":
                # If the district heating type is urban, set the 
                # corresponding values to 1
                input_values_dict["input_chp_urban"] = 0
                input_values_dict["input_dh_urban"] = 1
                input_values_dict["input_chp_sub_urban"] = 0
                input_values_dict["input_dh_sub_urban"] = 0
                input_values_dict["input_chp_rural"] = 0
                input_values_dict["input_dh_rural"] = 0
                input_values_dict["input_chp_a"] = 1
                
            elif input_dh == "sub-urban":
                # If the district heating type is sub-urban, set the 
                # corresponding values to 1
                input_values_dict["input_chp_urban"] = 0
                input_values_dict["input_dh_urban"] = 1
                input_values_dict["input_chp_sub_urban"] = 0
                input_values_dict["input_dh_sub_urban"] = 1
                input_values_dict["input_chp_rural"] = 0
                input_values_dict["input_dh_rural"] = 0
                input_values_dict["input_chp_a"] = 1
                
            elif input_dh == "rural":
                # If the district heating type is rural, set all values to 1
                input_values_dict["input_chp_urban"] = 0
                input_values_dict["input_dh_urban"] = 1
                input_values_dict["input_chp_sub_urban"] = 0
                input_values_dict["input_dh_sub_urban"] = 1
                input_values_dict["input_chp_rural"] = 0
                input_values_dict["input_dh_rural"] = 1
                input_values_dict["input_chp_a"] = 1
                
            # selectbox to choose solver
            input_values_dict["solver_select"] = st.selectbox(
                label="Optimization Solver",
                options=("cbc", "gurobi"),
                help=get_help("solver_select"))
            
            # create slider to choose the optimization criterion
            input_values_dict["input_criterion"] = st.select_slider(
                label="Optimization Criterion",
                options=("monetary", "emissions"),
                help=get_help("input_optimization"))
            
        else:

            # input value for model run name
            input_values_dict["input_name"] = st.text_input(
                label="Name",
                value="")
            
            # Value for photovoltaics
            pv_options = {"0%": 0, "25%": 0.25, "50%": 0.5, "75%": 0.75, "100%": 1.0}
            selected_pv = st.select_slider("Photovoltaic in kW", options=list(pv_options.keys()),help=get_help("input_pv"))
            input_values_dict["input_pv"] = int(pv_options[selected_pv] * 10000)

            # Value for solar thermal
            sth_options = {"0%": 0, "25%": 0.25, "50%": 0.5, "75%": 0.75, "100%": 1.0}
            selected_sth = st.select_slider("Solar Thermal in kW", options=list(sth_options.keys()),help=get_help("input_st"))
            input_values_dict["input_st"] = int(sth_options[selected_sth] * 27700)

            # Value for air source heat pump
            ashp_options = {"0%": 0, "25%": 0.25, "50%": 0.5, "75%": 0.75, "100%": 1.0}
            selected_ashp = st.select_slider("Air source heat pump in kW", options=list(ashp_options.keys()),help=get_help("input_ashp"))
            input_values_dict["input_ashp"] = int(ashp_options[selected_ashp] * 5000)

            # Value for ground coupled heat pump
            gchp_options = {"0%": 0, "25%": 0.25, "50%": 0.5, "75%": 0.75, "100%": 1.0}
            selected_gchp = st.select_slider("Ground coupled heat pump in kW", options=list(gchp_options.keys()),help=get_help("input_gchp"))
            input_values_dict["input_gchp"] = int(gchp_options[selected_gchp] * 5000)

            # Value for central thermal storage
            battery_options = {"0%": 0, "25%": 0.25, "50%": 0.5, "75%": 0.75, "100%": 1.0}
            selected_battery = st.select_slider("Battery in kWh", options=list(battery_options.keys()),help=get_help("input_battery"))
            input_values_dict["input_battery"] = int(battery_options[selected_battery] * 10000)

            # Value for decentral thermal storage
            dcts_options = {"0%": 0, "25%": 0.25, "50%": 0.5, "75%": 0.75, "100%": 1.0}
            selected_dcts = st.select_slider("Thermal Storage (decentral) in kWh", options=list(dcts_options.keys()),help=get_help("input_dcts"))
            input_values_dict["input_dcts"] = int(dcts_options[selected_dcts] * 10000)

            # Selectbox for the size of the District Heating Network
            input_dh = st.selectbox(
                label="District Heating Network",
                options=["No District Heating Network", "urban", "sub-urban",
                         "rural"],
                help=GUI_helper["demo_sb_heat_network_chp"])
            
            input_values_dict["input_chp"]=0
                
            if input_dh == "No District Heating Network":
                # If there is no district heating network, set all values 
                # to 0
                input_values_dict["input_chp_urban"] = 0
                input_values_dict["input_dh_urban"] = 0
                input_values_dict["input_chp_sub_urban"] = 0
                input_values_dict["input_dh_sub_urban"] = 0
                input_values_dict["input_chp_rural"] = 0
                input_values_dict["input_dh_rural"] = 0
                input_values_dict["input_chp_a"] = 0
                
            elif input_dh == "urban":
                # If the district heating type is urban, set the 
                # corresponding values to 1
                input_values_dict["input_chp_urban"] = 1
                input_values_dict["input_dh_urban"] = 1
                input_values_dict["input_chp_sub_urban"] = 0
                input_values_dict["input_dh_sub_urban"] = 0
                input_values_dict["input_chp_rural"] = 0
                input_values_dict["input_dh_rural"] = 0
                input_values_dict["input_chp_a"] = 0
                
            elif input_dh == "sub-urban":
                # If the district heating type is sub-urban, set the 
                # corresponding values to 1
                input_values_dict["input_chp_urban"] = 1
                input_values_dict["input_dh_urban"] = 1
                input_values_dict["input_chp_sub_urban"] = 1
                input_values_dict["input_dh_sub_urban"] = 1
                input_values_dict["input_chp_rural"] = 0
                input_values_dict["input_dh_rural"] = 0
                input_values_dict["input_chp_a"] = 0
                
            elif input_dh == "rural":
                # If the district heating type is rural, set all values to 1
                input_values_dict["input_chp_urban"] = 1
                input_values_dict["input_dh_urban"] = 1
                input_values_dict["input_chp_sub_urban"] = 1
                input_values_dict["input_dh_sub_urban"] = 1
                input_values_dict["input_chp_rural"] = 1
                input_values_dict["input_dh_rural"] = 1
                input_values_dict["input_chp_a"] = 0
                
            # selectbox to choose solver
            input_values_dict["solver_select"] = st.selectbox(
                label="Optimization Solver",
                options=("cbc", "gurobi"),
                help=get_help("solver_select"))
            
            # create slider to choose the optimization criterion
            input_values_dict["input_criterion"] = st.select_slider(
                label="Optimization Criterion",
                options=("monetary", "emissions"),
                help=get_help("input_optimization"))
        
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
    # "slicing A", "80", "None", "days"
    # run sesmg main function with reduced / fixed input options
    sesmg_main(
        model_definition_file=demo_file,
        result_path=demo_results,
        num_threads=1,
        timeseries_prep=["slicing A", "4", "None", "days", 0],
        # timeseries_prep=["None", "None", "None", "None", 0],
        graph=False,
        criterion_switch=criterion_switch,
        xlsx_results=False,
        console_results=False,
        solver=input_values_dict["solver_select"],
        cluster_dh=False,
        district_heating_path=""
    )

    # reset st.session_state["state_submitted_demo_run"] to stop rerun
    # when switching to Demo Tool multipage again
    st.session_state["state_submitted_demo_run"] = "not done"

def set_named_cell(wb, name, value):
    """Assigns a value to a cell with a defined name in Excel"""
    if name in wb.defined_names:
        dest = wb.defined_names[name].destinations
        for title, cell_ref in dest:
            ws = wb[title]  # Get the sheet where the cell is located
            ws[cell_ref] = value  # Assign the value to the cell
    else:
        print(f"Error: '{name}' is not defined in the Excel file.")


def create_demo_model_definition() -> None:
    """
        Modifies the demo model definition.
    """

    xfile = openpyxl.load_workbook(
        os.path.join(mainpath_pf,
                     "demo_tool",
                     "v1.1.0_demo_model_definition",
                     "demo_model_definition.xlsx"),
        data_only=True)

    # PHOTOVOLTAICS
    set_named_cell(xfile, "Photo1", input_values_dict["input_pv"])
    set_named_cell(xfile, "Photo2", input_values_dict["input_pv"])

    # SOLAR THERMAL
    set_named_cell(xfile, "Solart1", input_values_dict["input_st"])
    set_named_cell(xfile, "Solart2", input_values_dict["input_st"])

    # BATTERY
    set_named_cell(xfile, "Battery1", input_values_dict["input_battery"])
    set_named_cell(xfile, "Battery2", input_values_dict["input_battery"])

    # THERMAL STORAGE
    set_named_cell(xfile, "DCTS1", input_values_dict["input_dcts"])
    set_named_cell(xfile, "DCTS2", input_values_dict["input_dcts"])

    # GCHP
    set_named_cell(xfile, "GCHP1", input_values_dict["input_gchp"])
    set_named_cell(xfile, "GCHP2", input_values_dict["input_gchp"])
    
    # ASHP
    set_named_cell(xfile, "ASHP1", input_values_dict["input_ashp"])
    set_named_cell(xfile, "ASHP2", input_values_dict["input_ashp"])

    # CHP
    set_named_cell(xfile, "CHPtr1", input_values_dict["input_chp"])
    set_named_cell(xfile, "CHPtr2", input_values_dict["input_chp"])

    # DISTRICT HEATING AND CHP
    set_named_cell(xfile, "dhurban", input_values_dict["input_dh_urban"])
    set_named_cell(xfile, "dhsuburban", input_values_dict["input_dh_sub_urban"])
    set_named_cell(xfile, "dhrural", input_values_dict["input_dh_rural"])

    set_named_cell(xfile, "chpurban", input_values_dict["input_chp_urban"])
    set_named_cell(xfile, "chpsuburban", input_values_dict["input_chp_sub_urban"])
    set_named_cell(xfile, "chprural", input_values_dict["input_chp_rural"])
    set_named_cell(xfile, "chpa", input_values_dict["input_chp_a"])

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

    # change dimension of the values to Mio.Euro/a and t/a
    annual_costs = float(df_summary[mode_dict.get(mode)[0]] / 1000000)

    annual_emissions = float(df_summary[mode_dict.get(mode)[1]] / 1000000)

    # calculate relative change refered to the status quo
    # costs in Mio.Euro/a
    stat_quo_costs = 13.61684450
    # emissions in t/a
    stat_quo_emissions = 17177.84374780
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
        label="Annual Costs in Mil. Euro",
        value=round(annual_costs, 2),
        delta=rel_result_costs,
        delta_color="inverse")
    cost2.metric(
        label="Annual Costs in t",
        value=round(annual_emissions, 2),
        delta=rel_result_emissions,
        delta_color="inverse")

    # define new row with new values
    new_row = pd.DataFrame(
        {
            'Costs in million Euro/a': [annual_costs],
            'CO2-emissions in t/a': [annual_emissions],
            'Name': [input_values_dict["input_name"]]
        }
    )

    additional_points = pd.DataFrame()

    # Append a new row to the additional_points DataFrame
    #additional_points = additional_points.concat(new_row, ignore_index=True)
    additional_points = pd.concat(
        [additional_points,new_row],
        ignore_index=True)

    return additional_points


def save_additional_points(additional_points):
    
    if additional_points.empty:
        additional_points = pd.DataFrame()

    # Select the file according to the mode
    if st.session_state["mode"] == "simplified":
        path_pareto_results = path_pareto_results_simplified
    else:
        path_pareto_results = path_pareto_results_advanced

    # Check if the file already exists
    if os.path.exists(path_pareto_results):
        # Append new data to the existing CSV file
        additional_points.to_csv(path_pareto_results,
                                 mode='a',
                                 header=False,
                                 index=False)
    else:
        # Save the Pandas DataFrame to a new CSV file
        additional_points.to_csv(path_pareto_results,
                                 index=False)

# Define the main path
mainpath_pf = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Function to apply style to the table
def style_table(df):
    # Convert DataFrame to HTML
    html = df.to_html(index=False)
    # Apply styling to the first row and column, and center text in all cells
    html = html.replace('<th>', '<th style="font-weight: bold; text-align: center;">')
    html = html.replace('<td>', '<td style="text-align: center;">')
    
    # Apply style to the first row
    rows = html.split('<tr>')
    rows[1] = rows[1].replace('<td', '<td style="font-weight: bold; text-align: center;"')
    
    # Apply style to the first column
    for i in range(2, len(rows)):
        cols = rows[i].split('<td')
        if len(cols) > 1:
            cols[1] = cols[1].replace('style="text-align: center;"', 'style="font-weight: bold; text-align: center;"')
            rows[i] = '<td'.join(cols)
    html = '<tr>'.join(rows)
    
    return html

def get_named_pareto_points():
    df = load_pareto_table_by_mode()

    point_map = {
        "Minimum cost": "MC",
        "Minimum emission": "ME",
        "1. Pareto point": "P1",
        "3. Pareto point": "P3",
        "5. Pareto point": "P5",
        "7. Pareto point": "P7",
        "9. Pareto point": "P9"
    }

    named_points = []

    for label, short in point_map.items():
        row = df[df.iloc[:, 0].astype(str).str.strip().str.lower() == label.lower()]
        if not row.empty:
            try:
                # Cost is second to last column, Emissions is last
                cost_raw = row.iloc[0, -2]
                emissions_raw = row.iloc[0, -1]

                cost = float(str(cost_raw).replace(",", ".")) / 1_000_000
                emissions = float(str(emissions_raw).replace(",", "."))

                named_points.append({
                    "Costs in million Euro/a": cost,
                    "CO2-emissions in t/a": emissions,
                    "Name": short
                })
            except Exception as e:
                st.warning(f"Error parsing row '{label}': {e}")

    return pd.DataFrame(named_points)

# Show Graph
def show_demo_run_results_on_graph():
    
    # Seleccionar el archivo de resultados según el modo
    if st.session_state["mode"] == "simplified":
        path_pareto_results = path_pareto_results_simplified
    else:
        path_pareto_results = path_pareto_results_advanced

    # Cargar solo si el archivo existe
    if os.path.exists(path_pareto_results):
        additional_points = pd.read_csv(path)
    else:
        additional_points = pd.DataFrame(columns=["Costs in million Euro/a", "CO2-emissions in t/a", "Name"])

    # Define datasets for each mode
    if st.session_state["mode"] == "simplified":
        pareto_points = pd.DataFrame({
            "Costs in million Euro/a": [
                13.83457067,
                11.23034118,
                10.38012202,
                9.70299708,
                9.30243609,
                9.05718707,
                8.81421314,
                8.57128538,
                8.35829138,
                8.22717083,
                8.16954368

            ],
            'CO2-emissions in t/a': [
                8228.280691,
                8513.397873,
                8797.61296,
                9081.828048,
                9366.043135,
                9650.258222,
                9934.473309,
                10218.6884,
                10502.90348,
                10787.11857,
                11071.33366
            ]
        })
    elif st.session_state["mode"] == "advanced":
        pareto_points = pd.DataFrame({
            "Costs in million Euro/a": [
                13.83457067,
                11.20222739,
                10.35390994,
                9.67091701,
                9.26286046,
                9.01489089,
                8.76768741,
                8.52168984,
                8.32918132,
                8.21501444,
                8.15942628
            ],
            'CO2-emissions in t/a':[
                8228.280691,
                8518.345322,
                8807.507858,
                9096.670393,
                9385.832929,
                9674.995465,
                9964.158001,
                10253.32054,
                10542.48307,
                10831.64561,
                11120.80814
            ]
        })
    else:
        return  # Do not display anything if no mode is selected

    # DataFrame for the status quo
    status_quo_points = pd.DataFrame(
        {
            'Costs in million Euro/a': [13.61684450],
            'CO2-emissions in t/a': [17177.84374780],
            'Name': ['Status Quo']
        }
    )

    # Get predefined points (MC, ME, P1, ..., P9)
    fixed_points = get_named_pareto_points()

    # chart layer for fixed named points
    fixed_points_chart = alt.Chart(fixed_points).mark_point(
    filled=True, size=100, color="black").encode(
    x='Costs in million Euro/a',
    y='CO2-emissions in t/a',
    tooltip=['Name', 'Costs in million Euro/a', 'CO2-emissions in t/a']) + alt.Chart(fixed_points).mark_text(
    align='left', dx=10, dy=-5, fontSize=12).encode(
    x='Costs in million Euro/a',
    y='CO2-emissions in t/a',
    text='Name')

    # add a new result line to the result data frame
    combined_df = pd.concat(
        [additional_points, status_quo_points, fixed_points],
        ignore_index=True)

    # create pareto point chart layer
    pareto_points_chart = alt.Chart(pareto_points).mark_line().encode(
        x=alt.X('Costs in million Euro/a',
                scale=alt.Scale(
                    domain=(8.2,
                            max(combined_df['Costs in million Euro/a']) * 1.05))),
        y=alt.Y('CO2-emissions in t/a',
                scale=alt.Scale(
                    domain=(8000,
                            max(combined_df['CO2-emissions in t/a']) * 1.05)))
    ).properties(
        width=1000,
        height=800
    ).interactive()

    # create status qou point chart layer
    status_quo_points_chart = alt.Chart(status_quo_points).mark_text(
        size=15,
        text="🔵 Status Quo",
        dx=40, dy=0,
        align="center",
        color="blue").encode(
        x=alt.X('Costs in million Euro/a',
                scale=alt.Scale(
                    domain=(8.2,
                            max(combined_df['Costs in million Euro/a']) * 1.05))),
        y=alt.Y('CO2-emissions in t/a',
                scale=alt.Scale(
                    domain=(8000,
                            max(combined_df['CO2-emissions in t/a']) * 1.05))),
        tooltip=['Costs in million Euro/a', 'CO2-emissions in t/a', 'Name']
    ).properties(
        width=1000,
        height=800
    )

    # create additional point chart layer
    additional_points_chart = alt.Chart(additional_points).mark_circle().encode(
        x=alt.X('Costs in million Euro/a',
                scale=alt.Scale(
                    domain=(8.2,
                            max(combined_df['Costs in million Euro/a']) * 1.05))),
        y=alt.Y('CO2-emissions in t/a',
                scale=alt.Scale(
                    domain=(8000,
                            max(combined_df['CO2-emissions in t/a']) * 1.05))),
        color='Name'
    ).properties(
        width=1000,
        height=800
    ).interactive()

    # write subheader, combine all chart layer and show the combinded chart
    st.subheader("Your solution on pareto graph:")
    
    if additional_points.empty:
        st.altair_chart(pareto_points_chart 
        + status_quo_points_chart 
        + fixed_points_chart,
        theme="streamlit", 
        use_container_width=True)
        
    else:
        st.altair_chart(
            additional_points_chart 
            + pareto_points_chart 
            + status_quo_points_chart
            + fixed_points_chart,
            theme="streamlit", 
            use_container_width=True)

    # Text input for file name
    pareto_result_file_name = st.sidebar.text_input(label='Name for the result file')
    
    # Button to safe a seperate result file
    if st.sidebar.button("Save a seperate file for the pareto results"):
        # create timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # safe the file with the given name and a timestamp as csv 
        combined_df.to_csv(
            os.path.join(mainpath_rdf, pareto_result_file_name 
                         + timestamp 
                         + '.csv'), 
                         index=False)
        # raise success message
        st.success("The result file was safed at {}!".format(mainpath_rdf))

def demo_start_page() -> None:
    """
        Start page text, images and tables for the demo tool.
    """

    # import markdown text from GUI files
    imported_markdown = read_markdown_document(
        document_path="docs/GUI_texts/demo_tool_text.md",
        folder_path=f'{"docs/images/manual/DemoTool/*"}',
        fixed_image_width=500)
    # show markdown text
    st.markdown(''.join(imported_markdown), unsafe_allow_html=True)
    # upload dh image
    image_path_system = str(get_bundle_dir()) \
        + "/docs/images/manual/DemoTool/demo_system_graph.png"
    # open image
    image_system = Image.open(image_path_system)
    # convert image to numpy array
    st.image(image_system, width=500)

    # import markdown tables from GUI files
    imported_markdown_dttab = read_markdown_document(
        document_path="docs/GUI_texts/demo_tool_tables.md",
        folder_path=f'{"docs/images/manual/DemoTool/*"}')
    # show markdown text
    st.markdown(''.join(imported_markdown_dttab), unsafe_allow_html=True)
    # upload dh image
    image_path_dh = str(get_bundle_dir()) \
                    + "/docs/images/manual/DemoTool/district_heating_network" \
                      ".png"
    # open image
    image_dh = Image.open(image_path_dh)
    # convert image to numpy array
    st.image(image_dh, width=500)


def reset_pareto_diagram_results():
    # Select the correct file according to the mode
    if st.session_state["mode"] == "simplified":
        path_pareto_results = path_pareto_results_simplified
    else:
        path_pareto_results = path_pareto_results_advanced
    # read csv
    additional_points = pd.read_csv(path_pareto_results)

    # Verify if the file exists before attempting to modify it
    if os.path.exists(path):
        # Delete data without deleting the file
        empty_df = pd.DataFrame(columns=["Costs in million Euro/a", "CO2-emissions in t/a", "Name"])
        empty_df.to_csv(path_pareto_results, index=False)

    # Reload page to reflect the changes
    st.experimental_rerun()

def load_pareto_table_by_mode():
    sheet_name = "Simplified" if st.session_state.get("mode") == "simplified" else "Advanced"
    
    excel_path = os.path.join(mainpath_pf, 
                              "demo_tool", 
                              "v1.1.0_demo_model_definition", 
                              "Ergebnistabelle_Demo-tool.xlsx")

    try:
        xl = pd.ExcelFile(excel_path, engine='openpyxl')
        if sheet_name in xl.sheet_names:
            df = xl.parse(sheet_name)
            df = df.replace(r'^\s*$', pd.NA, regex=True).dropna(how="all")
            return df
        else:
            st.error(f"La hoja '{sheet_name}' no existe en el archivo Excel.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"No se pudo leer el archivo Excel: {e}")
        return pd.DataFrame()

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

if st.session_state["mode"] == "simplified":
    path = path_pareto_results_simplified
else:
    path = path_pareto_results_advanced

# show results after submit button was clicked
if st.session_state["state_submitted_demo_run"] == "done":
    # Check if the results folder path exists
    if os.path.exists(mainpath_rdf) is False:
        # If not, create the result directory using a separate function
        create_result_directory()
        # Create the demo folder directory
        os.makedirs(mainpath_rdf)

    # check if pareto result csv exists
        if os.path.exists(path) is False:
            # Create path_pareto_results file with header
            with open(path, 'w') as fp:
                fp.write("Costs in million Euro/a,CO2-emissions in t/a,Name\n")  
    # create demo model definition and start model run
    create_demo_model_definition()
    # show generated results
    additional_points = show_demo_run_results(
        mode=input_values_dict["input_criterion"])
    # save additional pareto point from recent run
    save_additional_points(additional_points)

if os.path.exists(path):
    # show demo result file
    show_demo_run_results_on_graph()
    # create button to reset pareto diagram
    button = st.sidebar.button(label="Delete all values from pareto diagram")
    if button:
        reset_pareto_diagram_results()
        st.experimental_rerun()

# Initial table visibility status
if "show_pareto_table" not in st.session_state:
    st.session_state["show_pareto_table"] = False

# Function to toggle table visibility
def toggle_pareto_table():
    st.session_state["show_pareto_table"] = not st.session_state["show_pareto_table"]

# Button to show/hide the ideal data table
st.sidebar.button("Ideal data for pareto graph", on_click=toggle_pareto_table)

# Display the table if the button was pressed
if st.session_state["show_pareto_table"]:
    st.subheader("Table with ideal data for the pareto graph")
    st.warning("Note: Pareto Points P1 to P9 can not be fully reached on the pareto graph due to calculation settings, "
               "which is causing another solution for the operation optimization although the investment is the same. "
               "The energy systems in general can e.g. be operated more cost or emission efficient.")
    df = load_pareto_table_by_mode()
    styled_html = style_table(df)
    st.write(styled_html, unsafe_allow_html=True)
