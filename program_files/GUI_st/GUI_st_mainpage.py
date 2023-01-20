#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 13:23:07 2022

@author: jantockloth
"""

import streamlit as st
import pandas as pd
from PIL import Image
import os
from datetime import datetime 
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode 
import json

# from program_files.preprocessing.Spreadsheet_Energy_System_Model_Generator import sesmg_main

# from program_files.GUI_st.GUI_st_US import *
from GUI_streamlit import *



####################################
###### Main SESMG Application ######
####################################




def main_output_result_overview():    
    ####################################
    ############ Result Page ###########
    
    ########## Show Model Graph ########
    #Function to display the energy systems structure.
    
    # Header
    st.subheader("The structure of the modeled energy system:")
    
    # Importing and printing the energy system graph
    es_graph = Image.open(os.path.dirname(__file__) + "/graph.gv.png", "r")
    st.image(es_graph, caption="Beispielgraph.",)
    
    
    ########## Result Summary ########
    # Functions to display a summary of the modeled energy system.
    
    # Import summary csv and create dataframe
    df_summary = pd.read_csv(os.path.dirname(__file__) + "/summary.csv")
    # Create list with headers
    summary_headers = list(df_summary)
    
    # Display and import time series values
    time1, time2 = st.columns(2)
    time1.metric(label="Start Date", value=str(df_summary.iloc[0,0]))
    time2.metric(label="End Date", value=str(df_summary.iloc[0,1]))
    #time3.metric(label="Temporal Resolution", value=str(df_summary['Resolution']))            
    '''Hier Problem mit Darstellung des Typs Datetime'''
    
    
    # Display and import simulated cost values from summary dataframe
    cost1, cost2, cost3, cost4 = st.columns(4)
    cost1.metric(label=summary_headers[3], value=round(df_summary[summary_headers[3]],1), delta="1.2 °F")
    cost2.metric(label=summary_headers[4], value=round(df_summary[summary_headers[4]],1), delta="1.2 °F")
    cost3.metric(label=summary_headers[5], value=round(df_summary[summary_headers[5]],1), delta="-1.2 °F")
    cost4.metric(label=summary_headers[6], value=round(df_summary[summary_headers[6]],1), delta="1.2 °F")
    
    # Display and import simulated energy values from summary dataframe
    ener1, ener2 = st.columns(2)
    ener1.metric(label=summary_headers[7], value=round(df_summary[summary_headers[7]],1), delta="1.2 °F")
    ener2.metric(label=summary_headers[8], value=round(df_summary[summary_headers[8]],1), delta="1.2 °F")   
    
    
    ########## Result Summary ########
    # Functions to display a summary of the modeled energy system.
    
    # Import components csv and create dataframe
    df_components = pd.read_csv(os.path.dirname(__file__) + "/components.csv")
    
    
    # CSS to inject contained in a string
    hide_dataframe_row_index = """
                <style>
                .row_heading.level0 {display:none}
                .blank {display:none}
                </style>
                """

    # Inject CSS with Markdown
    st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)


    st.dataframe(df_components)
    
    AgGrid(df_components, height = 400, fit_columns_on_grid_load=True, update_mode=GridUpdateMode.SELECTION_CHANGED)
    
    st.write(df_summary['Start Date'])
    st.write(df_summary.iloc[0,0])
    st.write(summary_headers)
    st.dataframe(df_summary)
    st.write(df_summary)
    

    




def main_application_sesmg():    

    # Import the saved GUI settings from the last session
    settings_cache_dict_reload = import_GUI_input_values_json(os.path.dirname(__file__) + "/GUI_test_setting_cache.json")

        
    ####################################
    ############## Sidebar #############
    
    ########## Scenario Input ##########
    # Functions to upload the scenario sheet file.
        
    # Header
    st.sidebar.title("Upload Model Definition File")
    
    scenario_input_sheet_path = st.sidebar.text_input(
        "Type in path to your model definition sheet.",
        help="Give the full path from your main directory ending with \
                /modeldefinition_name.xlsx . \
                You can choose the filenames and directorties as you want.")
                
    
    # ###### Run Model Visualization #####
    # # Function to create and display the model structure without optimizung the system.
    
    # with st.sidebar.form("Visualization"):
        
    #     submitted_vis_structure = st.form_submit_button(label="Visualize model")
    
    
    ########## Modelrun Parameter Input ##########
    # Creating Frame as st.form_submit_button
    with st.sidebar.form("Input Parameters"):
        
        # Submit button to start optimization.
        submitted_optimization = st.form_submit_button("Start Optimization")
            
        # Header
        st.title("Input Parameters")
    
        
        ####################################
        # Input processing parameters
        # Functions to input the modelling parameters.
        
        # Header
        st.subheader("Processing Parameters")

        # Checkboxes processing graph
        st.checkbox("Show Graph")
        # Slider number of threads
        input_num_threads = st.slider("Number of threads",min_value=1,max_value=35, help="Number of threads to use on your machine")
        # Choosing solver
        input_solver = st.selectbox("Optimization Solver", ("cbc", "gurobi"))


        ####################################
        # Input preprocessing parameters
        # Functions to input the preprocessing parameters.
        
        # Header
        st.subheader("Preprocessing Parameters")

        ### Functions to input the parameters for timeseries preparation.
        # TimeSeries Preparation
        # Choosable Algorithms
        timeseries_algorithm_list = \
            ["None", "k_means", "k_medoids", "averaging", "slicing A",
             "slicing B", "downsampling A", "downsampling B",
             "heuristic selection", "random sampling"]
        # Choosable clustering crtieria
        timeseries_cluster_criteria_list = \
            ["None", "temperature", "dhi", "el_demand_sum", "heat_demand_sum"]
        # Timeseries Index Range
        timeseries_index_range_start = ["None"]
        timeseries_index_range_values = [i for i in range(1, 366)]
        timeseries_index_range_list = timeseries_index_range_start + timeseries_index_range_values
        
        # Timeseries preparation input inside an expander. 
        with st.expander("Timeseries Simplification"):
            # Choosing timeseries parameters - algorithm
            input_timeseries_algorithm = st.selectbox("Algorithm", timeseries_algorithm_list)
            # Choosing timeseries parameters - index
            input_timeseries_cluster_index = st.selectbox("Index", timeseries_index_range_list)
            # Choosing timeseries parameters - cluster criterion
            input_timeseries_criterion = st.selectbox("Cluster Criterion", timeseries_cluster_criteria_list)
            # Choosing timeseries parameters - period
            input_timeseries_period = st.selectbox("Period", ["None","hours", "days", "weeks"])
            # Choosing timeseries parameters - season
            input_timeseries_season = st.selectbox("Season", ["None",4,12])
        
        
        # Pre-Model setting and pre-model timeseries preparation input inside an expander.
        with st.expander("Pre-Modeling Settings"):
            
            # Checkbox to activate the pre-modeling
            input_activate_premodeling = st.checkbox("Activate Pre-Modeling")
            
            # Activate functions to reduce the maximum design capacity
            input_premodeling_invest_boundaries = st.checkbox("Investment Boundaries Tightening")
            # Slider to set the tightening factor for maximum design capacity
            input_premodeling_tightening_factor = st.slider("Investment Tightening Factor", min_value=1, max_value=100)
            
            # Choosing pre-model timeseries parameters - algorithm
            input_premodeling_timeseries_algorithm = st.selectbox("Algorithm (Pre-Model)", timeseries_algorithm_list)
            # Choosing pre-model timeseries parameters - index
            input_premodeling_timeseries_cluster_index = st.selectbox("Index (Pre-Model)", timeseries_index_range_list)
            # Choosing pre-model timeseries parameters - cluster criterion
            input_premodeling_timeseries_criterion = st.selectbox("Cluster Criterion (Pre-Model)", timeseries_cluster_criteria_list)
            # Choosing pre-model timeseries parameters - period
            input_premodeling_timeseries_period = st.selectbox("Period (Pre-Model)", ["None","hours", "days", "weeks"])
            # Choosing pre-model timeseries parameters - season
            input_premodeling_timeseries_season = st.selectbox("Season (Pre-Model)", ["None",4,12])
 
        
               
        # Checkboxes modeling while using district heating clustering.
        input_cluster_dh = st.checkbox("Clustering District Heating Network")
        
        ### Function to upload the distrct heating precalulation inside an expander.
        with st.expander("Advanced District Heating Precalculation"):
            #'''
            #### Fileuploader not able to print file path
            ## Upload DH Precalc File 
            #district_heating_precalc = st.file_uploader("Select District Heating File")
            #'''
            district_heating_precalc_path = st.text_input("Type in path to your District Heating File input file.") 
        
        
        ####################################
        # Input Postprocessing Parameters
        # Functions to input the postprocessing parameters.
        
        # Header
        st.subheader("Postprocessing Parameters")
       
        # Input result processing parameters
        input_xlsx_results = st.checkbox("Create xlsx-files")
        input_console_results = st.checkbox("Create console-log")


        # Elements to set the pareto points.
        with st.expander("Pareto Point Options"):
            
            input_criterion_switch = st.checkbox("Switch Criteria")
            
            # List of pareto points wich can be chosen.
            pareto_options = [100 - 5*i for i in range(1,20)]
            
            # Multiselect element
            input_pareto_points = st.multiselect("Pareto Points", options=pareto_options)
            input_pareto_points.sort(reverse=True)
        
    
    
    ####################################
    # Starting process if "Start Optimization"-button is clicked
    
    if submitted_optimization:
        
        
        
        if scenario_input_sheet_path is not "":
            
            # Creating a dict with all GUI settings as preparation to save them for the next session
            # settings_cache_dict_reload["main_page"]
            
            
            # Creating the timeseries preperation settings list for the main model
            timeseries_prep_param = \
                [input_timeseries_algorithm,
                 input_timeseries_cluster_index,
                 input_timeseries_criterion,
                 input_timeseries_period,
                 0 if input_timeseries_season == "None" else input_timeseries_season]
            
            # Creating the timeseries preperation settings list for the pre-model
            pre_model_timeseries_prep_param = \
                [input_premodeling_timeseries_algorithm,
                 input_premodeling_timeseries_cluster_index,
                 input_premodeling_timeseries_criterion,
                 input_premodeling_timeseries_period,
                 0 if input_premodeling_timeseries_season == "None" else input_premodeling_timeseries_season]
            
            st.write(timeseries_prep_param)
            st.write(scenario_input_sheet_path)
            
#             # Setting the path where to safe the modeling results
#             res_folder_path = os.path.join(os.path.dirname(__file__),'results')
#             res_path = res_folder_path \
#                         + '/' \
#                         + scenario_input_sheet_path.split("/")[-1][:-5] \
#                         + datetime.now().strftime('_%Y-%m-%d--%H-%M-%S')
#             os.mkdir(res_path)

# # HIER NOCHMAL ANSEHEN WIE / WO DIE DATEI GESPEICHERT WERDEN SOLL            
#             # Setting the path where to safe the pre-modeling results
#             premodeling_res_folder_path = os.path.join(os.path.dirname(__file__),'pre_model_results')
#             premodeling_res_path = premodeling_res_folder_path \
#                         + '/' \
#                         + scenario_input_sheet_path.split("/")[-1][:-5] \
#                         + datetime.now().strftime('_%Y-%m-%d--%H-%M-%S')
#             os.mkdir(premodeling_res_path)
            
            
            # Staring the model run without a pre-model
    #         if input_activate_premodeling == False:
    #             sesmg_main(
    #                 scenario_file=scenario_input_sheet_path,
    #                 result_path=res_path,
    #                 num_threads=input_num_threads,
    #                 timeseries_prep=timeseries_prep_param,
    # #TODO: Implementieren 
    #                 graph=False,
    #                 criterion_switch=input_criterion_switch,
    #                 xlsx_results=input_xlsx_results,
    #                 console_results=input_console_results,
    #                 solver=input_solver,
    #                 district_heating_path=district_heating_precalc_path,
    #                 cluster_dh=input_cluster_dh
    #                 )
                
            # Staring the model run with a pre-model           
    #         else: 
    #             sesmg_main_including_premodel(
    #                 scenario_file=scenario_input_sheet_path,
    #                 result_path=res_path,
    #                 num_threads=input_num_threads,
    #                 timeseries_prep=timeseries_prep_param,
    # #TODO: Implementieren 
    #                 graph=False,
    #                 criterion_switch=input_criterion_switch,
    #                 xlsx_results=input_xlsx_results,
    #                 console_results=input_console_results,
    #                 solver=input_solver,
    #                 district_heating_path=district_heating_precalc_path,
    #                 cluster_dh=input_cluster_dh,
    #                 pre_model_timeseries_prep=pre_model_timeseries_prep_param,
    #                 investment_boundaries = input_premodeling_invest_boundaries,
    #                 investment_boundary_factor = input_premodeling_tightening_factor,
    #                 pre_model_path=premodeling_res_path
    #                 )
                
            
        else:
            main_output_result_overview()
            st.write("Hallo")
             



####################################
############ TEST PAGE #############
####################################
                
             



def test_page():
    
    settings_cache_dict_reload = import_GUI_input_values_json(os.path.dirname(__file__) + "/GUI_test_setting_cache.json")

    st.write(settings_cache_dict_reload)
    
    
    st.title("Hier werden erweitere Ergebnisaufbereitungen dargestellt.")
       
    
    if st.sidebar.button("Clear Cache"):

        settings_cache_dict_reload_2 = clear_GUI_input_values(settings_cache_dict_reload, "main_page", os.path.dirname(__file__) + "/GUI_test_setting_cache.json")
        
        #rerun whole script to update GUI settings
        st.experimental_rerun()

        
    with st.sidebar.form("Input Parameters"):
        
        # Submit button to start optimization.
        submitted_optimization = st.form_submit_button("Start Inputs")
        input1 = st.text_input("Test Input 1", value=settings_cache_dict_reload["input1"])
        input2 = st.text_input("Test Input 2", value=settings_cache_dict_reload["input2"])
    
        if  submitted_optimization:
            
            settings_cache_dict = {"input1": input1, "input2": input2}
            
            #sfe GUI settings dict
            safe_GUI_input_values(settings_cache_dict, os.path.dirname(__file__) + "/GUI_test_setting_cache.json")
            
            #rerun whole script to update GUI settings
            st.experimental_rerun()

        

####################################
############ DEMO Tool #############
####################################


def demo_result_page():
    
    demo_page = st.container()
    
    with demo_page:
        st.title("Hier wird das Demotool platziert.")

















