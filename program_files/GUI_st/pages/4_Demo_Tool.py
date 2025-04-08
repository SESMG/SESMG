"""
    Jan N. Tockloth - jan.tockloth@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
    Christian Klemm - christian.klemm@fh-muenster.de
    Benjamin Blankenstein - bb917322@fh-muenster.de
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
            
            input_values_dict["input_chp"] = st.number_input(
                label="Design of a CHP",
                min_value=0,
                max_value=20000,
                step=1,
                help=GUI_helper["demo_sb_heat_network_chp"]
            )
            
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
                help=GUI_helper["main_sb_solver"])
            
            # create slider to choose the optimization criterion
            input_values_dict["input_criterion"] = st.select_slider(
                label="Optimization Criterion",
                options=("monetary", "emissions"))
            
        else:

            # input value for model run name
            input_values_dict["input_name"] = st.text_input(
                label="Name",
                value="")
            
            # Value for photovoltaics
            pv_options = {"0%": 0, "25%": 0.25, "50%": 0.5, "75%": 0.75, "100%": 1.0}
            selected_pv = st.select_slider("Photovoltaic in kW", options=list(pv_options.keys()))
            input_values_dict["input_pv"] = int(pv_options[selected_pv] * 10000)

            # Value for solar thermal
            sth_options = {"0%": 0, "25%": 0.25, "50%": 0.5, "75%": 0.75, "100%": 1.0}
            selected_sth = st.select_slider("Solar Thermal in kW", options=list(sth_options.keys()))
            input_values_dict["input_st"] = int(sth_options[selected_sth] * 27700)

            # Value for air source heat pump
            ashp_options = {"0%": 0, "25%": 0.25, "50%": 0.5, "75%": 0.75, "100%": 1.0}
            selected_ashp = st.select_slider("Air source heat pump in kW", options=list(ashp_options.keys()))
            input_values_dict["input_ashp"] = int(ashp_options[selected_ashp] * 5000)

            # Value for ground coupled heat pump
            gchp_options = {"0%": 0, "25%": 0.25, "50%": 0.5, "75%": 0.75, "100%": 1.0}
            selected_gchp = st.select_slider("Ground coupled heat pump in kW", options=list(gchp_options.keys()))
            input_values_dict["input_gchp"] = int(gchp_options[selected_gchp] * 5000)

            # Value for central thermal storage
            battery_options = {"0%": 0, "25%": 0.25, "50%": 0.5, "75%": 0.75, "100%": 1.0}
            selected_battery = st.select_slider("Battery in kWh", options=list(battery_options.keys()),help=GUI_helper["demo_ni_kw_kwh"])
            input_values_dict["input_battery"] = int(battery_options[selected_battery] * 10000)

            # Value for decentral thermal storage
            dcts_options = {"0%": 0, "25%": 0.25, "50%": 0.5, "75%": 0.75, "100%": 1.0}
            selected_dcts = st.select_slider("Thermal Storage (decentral) in kWh", options=list(dcts_options.keys()),help=GUI_helper["demo_ni_kw_kwh"])
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
                help=GUI_helper["main_sb_solver"])
            
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
    # "slicing A", "80", "None", "days"
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

# Load the Excel file from the specified path
excel_path = os.path.join(mainpath_pf, 
                          "demo_tool", 
                          "v1.1.0_demo_model_definition", 
                          "Ergebnistabelle_Demo-tool.xlsx")

if "mode" not in st.session_state:
    st.session_state["mode"] = "simplified"

sheet_name = "Advanced" if st.session_state["mode"] == "advanced" else "Simplified"
df = pd.read_excel(excel_path, sheet_name=sheet_name, engine='openpyxl')

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
                13.89549383, 
                12.56013776, 
                11.91894652, 
                11.3499508, 
                10.87207637,
                10.48015488, 
                10.12417196, 
                9.81144029, 
                9.59650753, 
                9.45681218,
                9.3275912, 
                9.19859782, 
                9.06960445, 
                8.94061108, 
                8.8116177,
                8.68858617, 
                8.58751772, 
                8.50769999, 
                8.44293867, 
                8.3931325,
                8.35503916, 
                8.32996238
            ],
            'CO2-emissions in t/a': [
                8210.772581, 
                8300.155956, 
                8362.449986, 
                8513.338036, 
                8664.226086,
                8815.114135, 
                8966.002185, 
                9116.890234, 
                9267.778284, 
                9418.666334,
                9569.554383, 
                9720.442433, 
                9871.330482, 
                10022.21853, 
                10173.10658,
                10323.99463, 
                10474.88268, 
                10625.77073, 
                10776.65878, 
                10927.54683,
                11078.43488, 
                11229.32293
            ]
        })
    elif st.session_state["mode"] == "advanced":
        pareto_points = pd.DataFrame({
            "Costs in million Euro/a": [
                13.89549383,
                13.21783787,
                11.99551678, 
                10.74532013, 
                10.25169493, 
                9.82225764, 
                9.57504883,
                9.41326585, 
                9.25148414, 
                9.08970045, 
                8.92793397, 
                8.83689952,
                8.79384666
            ],
            'CO2-emissions in t/a':[
                8210.772581,
                8356.12793537,
                8840.34851861,
                9500.36881876, 
                9766.69002624, 
                10055.84923162,
                10245.08943589, 
                10384.32964154, 
                10523.56984699, 
                10712.81005318,
                10902.05026001, 
                11091.29046663, 
                11280.53066925
            ]
        })
    else:
        return  # Do not display anything if no mode is selected

    # DataFrame for the status quo
    status_quo_points = pd.DataFrame(
        {
            'Costs in million Euro/a': [13.68616781],
            'CO2-emissions in t/a': [17221.43690357],
            'Name': ['Status Quo']
        }
    )

    # add a new result line to the result data frame
    combined_df = pd.concat(
        [additional_points, status_quo_points],
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
                        + status_quo_points_chart, 
                        theme="streamlit", 
                        use_container_width=True)
    else:
        st.altair_chart(additional_points_chart 
                        + pareto_points_chart 
                        + status_quo_points_chart, 
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
    # Seleccionar el archivo correcto según el modo
    if st.session_state["mode"] == "simplified":
        path_pareto_results = path_pareto_results_simplified
    else:
        path_pareto_results = path_pareto_results_advanced
    # read csv
    additional_points = pd.read_csv(path_pareto_results)

    # Verificar si el archivo existe antes de intentar modificarlo
    if os.path.exists(path):
        # Borrar los datos sin eliminar el archivo
        empty_df = pd.DataFrame(columns=["Costs in million Euro/a", "CO2-emissions in t/a", "Name"])
        empty_df.to_csv(path_pareto_results, index=False)

    # Recargar la página para reflejar los cambios
    st.experimental_rerun()


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
    styled_html = style_table(df)
    st.write(styled_html, unsafe_allow_html=True)