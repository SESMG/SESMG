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

from program_files.GUI_st.GUI_st_global_functions import clear_GUI_main_settings, create_safe_GUI_main_settings_dict, import_GUI_input_values_json
from program_files.preprocessing.Spreadsheet_Energy_System_Model_Generator import sesmg_main, sesmg_main_including_premodel

# from program_files.GUI_st.GUI_st_US import *


####################################
###### Main SESMG Application ######
####################################

def main_output_result_overview(result_path_summary, result_path_components, result_path_results):   
    
    #result_path_summary: path to summary.csv
    #result_path_components: path to components.csv
    #result_path_results: path to results.csv
    
    ####################################
    ############ Result Page ###########
    
    ########## Result Summary ########
    # Functions to display a summary of the modeled energy system.
    
    # Import summary.csv and create dataframe
    #df_summary = pd.read_csv(os.path.dirname(__file__) + "/summary.csv")
    df_summary = pd.read_csv(result_path_summary)
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
    
    # Import components.csv and create dataframe
    #df_components = pd.read_csv(os.path.dirname(__file__) + "/components.csv")
    df_components = pd.read_csv(result_path_components)
    
    # CSS to inject contained in a string
    hide_dataframe_row_index = """
                <style>
                .row_heading.level0 {display:none}
                .blank {display:none}
                </style>
                """

    # Inject CSS with Markdown
    st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

    # Creating st_aggrid table
    AgGrid(df_components, height = 400, fit_columns_on_grid_load=True, update_mode=GridUpdateMode.SELECTION_CHANGED)
    
    
    ####################  
    # hier plotly import
    

    ########## Show Model Graph ########
    #Function to display the energy systems structure.
    
    # Header
    st.subheader("The structure of the modeled energy system:")
    
# Expander einfügen
    # Importing and printing the energy system graph
    es_graph = Image.open(os.path.dirname(__file__) + "/graph.gv.png", "r")
    st.image(es_graph, caption="Beispielgraph.",)




def main_application_sesmg():    

    # Import the saved GUI settings from the last session
    settings_cache_dict_reload = import_GUI_input_values_json(os.path.dirname(__file__) + "/GUI_st_cache.json")
    
    st.write(settings_cache_dict_reload)
    st.write(settings_cache_dict_reload["num_threads"])
        
    ####################################
    ############## Sidebar #############
    
    ########## Scenario Input ##########
    #
                
    
    ###### Run Model Visualization #####
    # Function to create and display the model structure without optimizung the system.
    
    with st.sidebar.form("Visualization"):
        
        submitted_vis_existing_results = st.form_submit_button(label="Visualize existing model results")
        
        with st.expander("File Upload"):
            
            #importing an existing summary file
            existing_summary_csv = st.file_uploader("Existing summary.csv file")
        
            #importing an existing components file
            existing_components_csv= st.file_uploader("Existing components.csv file")
            
            #importing an existing results file
            existing_results_csv= st.file_uploader("Existing results.csv file")
    
    
    ########## Modelrun Parameter Input ##########
    # Creating Frame as st.form_submit_button
    with st.sidebar.form("Input Parameters"):
    
        # Submit button to start optimization.
        submitted_optimization = st.form_submit_button("Start Optimization")
        
        #Functions to upload the scenario sheet file.
           
        # Header
        st.title("Upload Model Definition")
       
        scenario_input_sheet_path = st.file_uploader(label=
           "Upload your model definition sheet.",
           help="muss noch geschrieben werden.")
        
        # Header
        st.title("Input Parameters")
    
        
        ####################################
        # Input processing parameters
        # Functions to input the modelling parameters.
        
        # Header
        st.subheader("Processing Parameters")

        # Checkboxes processing graph
        input_show_graph=st.checkbox("Show Graph")
        # Slider number of threads
        input_num_threads = st.slider("Number of threads",min_value=1,max_value=35, help="Number of threads to use on your machine", value=settings_cache_dict_reload["num_threads"])
        #indexing the chosen solver of the cache session as an inputvalue for st. selectbox
        
        # Dict of choosable solvers the streamlit input index for selectbox's preselections
        input_solver_dict = {"cbc": 0,
                             "gurobi": 1}
        # chosing the solver in an select box
        input_solver = st.selectbox("Optimization Solver", input_solver_dict.keys(), index=settings_cache_dict_reload["input_solver_index"])
        
        #preparing input_timeseries_season for GUI cache as an streamlit input index
        input_solver_index = input_solver_dict[input_solver]       
    
        ####################################
        # Input preprocessing parameters
        # Functions to input the preprocessing parameters.
        
        # Header
        st.subheader("Preprocessing Parameters")

        ### Functions to input the parameters for timeseries preparation.
        # TimeSeries Preparation
        # Dict of choosable algorithms matching the streamlit input index for selectbox's preselections
        timeseries_algorithm_dict = {"None": 0,
                                     "k_means": 1, 
                                     "k_medoids": 2, 
                                     "averaging": 3, 
                                     "slicing A": 4,
                                     "slicing B": 5, 
                                     "downsampling A": 6, 
                                     "downsampling B": 7,
                                     "heuristic selection": 8, 
                                     "random sampling": 9}
        
        # Timeseries Index Range
        timeseries_index_range_start = ["None"]
        timeseries_index_range_values = [i for i in range(1, 366)]
        # None or 1 to 365
        timeseries_index_range_list = timeseries_index_range_start + timeseries_index_range_values
        
        # Dict of choosable clustering crtieria matching the streamlit input index for selectbox's preselections 
        timeseries_cluster_criteria_dict = {"None": 0, 
                                            "temperature": 1, 
                                            "dhi": 2, 
                                            "el_demand_sum": 3, 
                                            "heat_demand_sum": 4}
        
        # Dict of choosable timeseries periods matching the streamlit input index for selectbox's preselections 
        input_timeseries_period_dict = {"None": 0,
                                        "hours": 1, 
                                        "days": 2 , 
                                        "weeks": 3}
        
        # Dict of choosable timeseries periods matching the streamlit input index for selectbox's preselections 
        input_timeseries_season_dict = {"None": 0,
                                        4: 1, 
                                        12: 2}

        # Timeseries preparation input inside an expander. 
        with st.expander("Timeseries Simplification"):
            # Choosing timeseries parameters - algorithm
            input_timeseries_algorithm = st.selectbox(label="Algorithm", options=timeseries_algorithm_dict.keys(), index=settings_cache_dict_reload["input_timeseries_algorithm_index"])
            # Choosing timeseries parameters - index
            input_timeseries_cluster_index = st.selectbox(label="Index", options=timeseries_index_range_list, index=settings_cache_dict_reload["input_timeseries_cluster_index_index"])
            # Choosing timeseries parameters - cluster criterion
            input_timeseries_criterion = st.selectbox(label="Cluster Criterion", options=timeseries_cluster_criteria_dict.keys(), index=settings_cache_dict_reload["input_timeseries_criterion_index"])
            # Choosing timeseries parameters - period
            input_timeseries_period = st.selectbox(label="Period", options=input_timeseries_period_dict.keys(), index=settings_cache_dict_reload["input_timeseries_period_index"])
            # Choosing timeseries parameters - season
            input_timeseries_season = st.selectbox(label="Season", options=input_timeseries_season_dict.keys(), index=settings_cache_dict_reload["input_timeseries_season_index"])
            
        # transform input values of Timeseries Simplification to an index which will be safed in the GUI cache to be able to reload setting. Needs to be an index for st.selectboxes.
        #preparing input_timeseries_algorithm for GUI cache as an streamlit input index
        input_timeseries_algorithm_index = timeseries_algorithm_dict[input_timeseries_algorithm]
        #preparing input_timeseries_cluster_index for GUI cache as an streamlit input index
        if input_timeseries_cluster_index == "None":
            input_timeseries_cluster_index_index = 0
        else: 
            input_timeseries_cluster_index_index = input_timeseries_cluster_index
        #preparing input_timeseries_criterion for GUI cache as an streamlit input index
        input_timeseries_criterion_index = timeseries_cluster_criteria_dict[input_timeseries_criterion]
        #preparing input_timeseries_period for GUI cache as an streamlit input index
        input_timeseries_period_index = input_timeseries_period_dict[input_timeseries_period]
        #preparing input_timeseries_season for GUI cache as an streamlit input index
        input_timeseries_season_index = input_timeseries_season_dict[input_timeseries_season]
        
        
        # Pre-Model setting and pre-model timeseries preparation input inside an expander.
        with st.expander("Pre-Modeling Settings"):
            
            # Checkbox to activate the pre-modeling
            input_activate_premodeling = st.checkbox(label="Activate Pre-Modeling")
            
            # Activate functions to reduce the maximum design capacity
            input_premodeling_invest_boundaries = st.checkbox(label="Investment Boundaries Tightening", value=settings_cache_dict_reload["input_premodeling_invest_boundaries"])
            # Slider to set the tightening factor for maximum design capacity
            input_premodeling_tightening_factor = st.slider(label="Investment Tightening Factor", min_value=1, max_value=100, value=settings_cache_dict_reload["input_premodeling_tightening_factor"])
            
            # Choosing pre-model timeseries parameters - algorithm
            input_premodeling_timeseries_algorithm = st.selectbox(label="Algorithm (Pre-Model)", options=timeseries_algorithm_dict.keys(), index=settings_cache_dict_reload["input_premodeling_timeseries_algorithm_index"])
            # Choosing pre-model timeseries parameters - index
            input_premodeling_timeseries_cluster_index = st.selectbox(label="Index (Pre-Model)", options=timeseries_index_range_list, index=settings_cache_dict_reload["input_premodeling_timeseries_cluster_index_index"])
            # Choosing pre-model timeseries parameters - cluster criterion
            input_premodeling_timeseries_criterion = st.selectbox(label="Cluster Criterion (Pre-Model)", options=timeseries_cluster_criteria_dict.keys(), index=settings_cache_dict_reload["input_premodeling_timeseries_criterion_index"])
            # Choosing pre-model timeseries parameters - period
            input_premodeling_timeseries_period = st.selectbox(label="Period (Pre-Model)", options=input_timeseries_period_dict.keys(), index=settings_cache_dict_reload["input_premodeling_timeseries_period_index"])
            # Choosing pre-model timeseries parameters - season
            input_premodeling_timeseries_season = st.selectbox(label="Season (Pre-Model)", options=input_timeseries_season_dict.keys(), index=settings_cache_dict_reload["input_premodeling_timeseries_season_index"])
 
        # transform input values of Timeseries Simplification to an index which will be safed in the GUI cache to be able to reload setting. Needs to be an index for st.selectboxes.
        #preparing input_timeseries_algorithm for GUI cache as an streamlit input index
        input_premodeling_timeseries_algorithm_index = timeseries_algorithm_dict[input_premodeling_timeseries_algorithm]
        #preparing input_timeseries_cluster_index for GUI cache as an streamlit input index
        if input_premodeling_timeseries_cluster_index == "None":
            input_premodeling_timeseries_cluster_index_index = 0
        else: 
            input_premodeling_timeseries_cluster_index_index = input_premodeling_timeseries_cluster_index
        #preparing input_timeseries_criterion for GUI cache as an streamlit input index
        input_premodeling_timeseries_criterion_index = timeseries_cluster_criteria_dict[input_premodeling_timeseries_criterion]
        #preparing input_timeseries_period for GUI cache as an streamlit input index
        input_premodeling_timeseries_period_index = input_timeseries_period_dict[input_premodeling_timeseries_period]
        #preparing input_timeseries_season for GUI cache as an streamlit input index
        input_premodeling_timeseries_season_index = input_timeseries_season_dict[input_premodeling_timeseries_season]       
 
          
        # Checkboxes modeling while using district heating clustering.
        input_cluster_dh = st.checkbox(label="Clustering District Heating Network", value=settings_cache_dict_reload["cluster_dh"])
        
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
        input_xlsx_results = st.checkbox(label="Create xlsx-files", value=settings_cache_dict_reload["xlsx_results"])
        input_console_results = st.checkbox(label="Create console-log", value=settings_cache_dict_reload["console_results"])


        # Elements to set the pareto points.
        with st.expander("Pareto Point Options"):
            
            input_criterion_switch = st.checkbox(label="Switch Criteria", value=settings_cache_dict_reload["criterion_switch"])
            
            # List of pareto points wich can be chosen.
            pareto_options = [100 - 5*i for i in range(1,20)]
            
            # Multiselect element
            input_pareto_points = st.multiselect(label="Pareto Points", options=pareto_options, default=settings_cache_dict_reload["input_pareto_points"])
            input_pareto_points.sort(reverse=True)
            
            
    ####### Clear the GUI settings cache
    # creating sidebar form submit strucutre
    with st.sidebar.form("Clear Cache"):
        
        submitted_clear_cache = st.form_submit_button(label="Clear all GUI Settings")
        
        #button if latest path should be cleard as well
        clear_path=st.checkbox(label="Clear result paths")
    
    
    #################################### 
    # Clear all GUI settings if clear latest result paths clicked
    if submitted_clear_cache and clear_path == True:
        #create and safe dict, set paths empty
        clear_GUI_main_settings(result_path="",
                                premodeling_result_path="",
                                json_file_path=os.path.dirname(__file__) + "/GUI_st_cache.json")
        #rerun whole script to update GUI settings
        st.experimental_rerun()
        
    elif submitted_clear_cache == True:
        #create and safe dict, set paths as before
        clear_GUI_main_settings(result_path=settings_cache_dict_reload["result_path"],
                                premodeling_result_path=settings_cache_dict_reload["premodeling_result_path"],
                                json_file_path=os.path.dirname(__file__) + "/GUI_st_cache.json")
        #rerun whole script to update GUI settings
        st.experimental_rerun()  
            
    
    
    ####################################
    # Starting process if "Visualize existing model results"-button is clicked    
    
    if submitted_vis_existing_results:
        
        # run main result page with uploaded existiag files  
        main_output_result_overview(result_path_summary=existing_summary_csv, 
                                    result_path_components=existing_components_csv,
                                    result_path_results=existing_results_csv)
    
    
    ####################################
    # Starting process if "Start Optimization"-button is clicked
    
    if submitted_optimization:
        
        if scenario_input_sheet_path != "":
                        
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

             # Setting the path where to safe the modeling results
            res_folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),'results')
            res_path = res_folder_path \
                        + '/' \
                        + scenario_input_sheet_path.name.split("/")[-1][:-5] \
                        + datetime.now().strftime('_%Y-%m-%d--%H-%M-%S')
            st.write(res_path)
            os.mkdir(res_path)             
            
# HIER NOCHMAL ANSEHEN WIE / WO DIE DATEI GESPEICHERT WERDEN SOLL            
            # Setting the path where to safe the pre-modeling results
            premodeling_res_folder_path = os.path.join(os.path.dirname(__file__),'pre_model_results')
            premodeling_res_path = premodeling_res_folder_path \
                        + '/' \
                        + scenario_input_sheet_path.name.split("/")[-1][:-5] \
                        + datetime.now().strftime('_%Y-%m-%d--%H-%M-%S')
            #os.mkdir(premodeling_res_path)
            st.write(premodeling_res_path)

             # Creating a dict with all GUI settings as preparation to save them for the next session
             # settings_cache_dict_reload["main_page"]
             
            create_safe_GUI_main_settings_dict(result_path=res_path,
                                               premodeling_result_path=premodeling_res_path,
                                               num_threads=input_num_threads,
                                               input_timeseries_algorithm_index=input_timeseries_algorithm_index,
                                               input_timeseries_cluster_index_index=input_timeseries_cluster_index_index,
                                               input_timeseries_criterion_index=input_timeseries_criterion_index,
                                               input_timeseries_period_index=input_timeseries_period_index , 
                                               input_timeseries_season_index=input_timeseries_season_index ,
                                               graph=input_show_graph,
                                               criterion_switch=input_criterion_switch,
                                               xlsx_results=input_xlsx_results,
                                               console_results=input_console_results,
                                               input_solver_index=input_solver_index,
                                               cluster_dh=input_cluster_dh,
                                               input_premodeling_invest_boundaries=input_premodeling_invest_boundaries,
                                               input_premodeling_tightening_factor=input_premodeling_tightening_factor,
                                               input_premodeling_timeseries_algorithm_index=input_premodeling_timeseries_algorithm_index,
                                               input_premodeling_timeseries_cluster_index_index=input_premodeling_timeseries_cluster_index_index,
                                               input_premodeling_timeseries_criterion_index=input_premodeling_timeseries_criterion_index,
                                               input_premodeling_timeseries_period_index=input_premodeling_timeseries_period_index,
                                               input_premodeling_timeseries_season_index=input_premodeling_timeseries_season_index,
                                               input_pareto_points=input_pareto_points,
                                               json_file_path=os.path.dirname(__file__) + "/GUI_st_cache.json")
                     
            
            # Starting the waiting / processing screen
            with st.spinner(text="Modelling in Progress."):
            
                # Starting the model run without a pre-model
                if input_activate_premodeling == False:
                    sesmg_main(
                        scenario_file=scenario_input_sheet_path,
                        result_path=res_path,
                        num_threads=input_num_threads,
                        timeseries_prep=timeseries_prep_param,
        #TODO: Implementieren 
                        graph=False,
                        criterion_switch=input_criterion_switch,
                        xlsx_results=input_xlsx_results,
                        console_results=input_console_results,
                        solver=input_solver,
                        district_heating_path=district_heating_precalc_path,
                        cluster_dh=input_cluster_dh
                        )
                    
                    st.write('Modelling completed!')
                    
                    # run main result page with new modelled files 
                    main_output_result_overview(result_path_summary=res_path + "/summary.csv", 
                                                result_path_components=res_path + "/components.csv",
                                                result_path_results=res_path + "/results.csv")
                    
                
        #     # Starting the model run with a pre-model           
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
        #                 pre_model_path=premodeling_res_path)
                    
        #             st.write('Modelling completed!')

           
            
        else:
            
            #main_output_result_overview()
            st.spinner("Modelling in Progress...")
            st.write("Hallo")
             



####################################
############ TEST PAGE #############
####################################
                
             



def test_page():
    
    from GUI_streamlit import (import_GUI_input_values_json, \
        safe_GUI_input_values, \
        clear_GUI_input_values)
        
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

















