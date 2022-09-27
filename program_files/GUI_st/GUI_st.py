#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 09:58:07 2022

@author: jtock
"""


import streamlit as st
import pandas as pd
from PIL import Image
import os





    



####################################
###### Main SESMG Application ######
####################################


def main_page():    
    """
    Function to create the result page of the main SESMG application.
    """
    
    mr_page = st.container()
    
    with mr_page: 
        st.title("Spredsheet Energy System Model Generator - Result Overview")   

    main_result_graph()
    
    main_result_summary()


def main_sidebar():
    """
    Function to create the sidebar page of the main SESMG application.
    """
    
    # Scenario Upload
    main_input_sb_scenario()
    
    main_input_create_model_structure()
    
    # Creating Frame as st.form_submit_button
    with st.sidebar.form("Input Parameters"):
        
        # Submit button to start optimization.
        submitted_optimization = st.form_submit_button("Start Optimization")
            
        # Header
        st.title("Input Parameters")
        
        # Input Modelling Parameters
        main_input_sb_modelling()
        
        # Input Result Processing Parameters
        main_input_sb_processing()
        
        # Input Timeseries Parameters
        main_input_sb_timeseries()
        

########### Input Functions ###########


def main_input_sb_scenario():
    """
    Function to upload the scenario sheet file.
    """
    
    # Header
    st.sidebar.title("Upload Scenario File")
    
    # Upload Scenario Sheet File 
    scenario_sheet = st.sidebar.file_uploader("Select Scenario File")
    if scenario_sheet is not None:
         dataframe = pd.read_excel(scenario_sheet)
         st.write(dataframe)
         

def main_input_create_model_structure():
    """
    Function to create and display the model structure without optimizung the system.
    """

    with st.sidebar.form("Visualization"):
        
        submitted_vis_structure = st.form_submit_button("Visualize model")
    


def main_input_sb_modelling():
    """
    Function to input the modelling parameters.
    """
    
    # Header
    st.subheader("Modelling Parameters")

    # Checkboxes Modeling
    st.checkbox("Show Graph")
    st.checkbox("Switch Criteria")
    
    # Choosing Solver
    st.selectbox("Optimization Solver", ("Option A", "Option B"))
    


def main_input_sb_timeseries():
    """
    Function to input the parameters for timeseries preparation.
    """
    
    # Header
    st.subheader("Timeseries Preparation")
    
    # Choosing Timeseries Parameters - Algorithm
    st.selectbox("Algorithm", ("None", "Option A", "Option B"))
    # Choosing Timeseries Parameters - Index
    st.selectbox("Index", ("None", "Option A", "Option B"))
    # Choosing Timeseries Parameters - Criterion
    st.selectbox("Criterion", ("None", "Option A", "Option B"))
    # Choosing Timeseries Parameters - Period
    st.selectbox("Period", ("None", "Option A", "Option B"))
    # Choosing Timeseries Parameters - Season
    st.selectbox("Season", ("None", "Option A", "Option B"))
    
  
  
def main_input_sb_processing():    
    """
    Function to input the result processing parameters.
    """
    
    # Header
    st.subheader("Result Processing Parameters")

    # Checkboxes Modeling
    st.checkbox("Create xlsx-files")
    st.checkbox("Create console-log")
    st.checkbox("Create plotly-dash")   



########### Result Functions ##########


def main_result_graph():
    """
    Function to display the energy systems structure.
    """
    
    # Header
    st.subheader("The structure of the modelled energy system:")
    
    # Importing and printing the Energy System Graph
    es_graph = Image.open(os.path.dirname(__file__) + "/graph.gv.png", "r")
    st.image(es_graph, caption = "Filename oÄ?",)



def main_result_summary():
    """
    Function to display a summary of the modeled energy system.
    """
    
    # Import summary csv and create dataframe
    df_summary = pd.read_csv(os.path.dirname(__file__) + "/summary.csv")
    
    # Display and import time series values
    #time1, time2 = st.columns(2)
    #time1.metric(label="Start Date", value=str(df_summary['Start Date']))
    #time2.metric(label="End Date", value=str(df_summary['End Date']))
    #time3.metric(label="Temporal Resolution", value=str(df_summary['Resolution']))            
    '''Hier Problem mit Darstellung des Typs Datetime'''
    
    # Display and import simulated cost values from summary dataframe
    cost1, cost2, cost3, cost4 = st.columns(4)
    cost1.metric(label="Total System Costs", value=round(df_summary['Total System Costs'],1), delta="1.2 °F")
    cost2.metric(label="Total Constraint Costs", value=round(df_summary['Total Constraint Costs'],1), delta="1.2 °F")
    cost3.metric(label="Total Variable Costs", value=round(df_summary['Total Variable Costs'],1), delta="-1.2 °F")
    cost4.metric(label="Total Periodical Costs", value=round(df_summary['Total Periodical Costs'],1), delta="1.2 °F")
    
    # Display and import simulated energy values from summary dataframe
    ener1, ener2 = st.columns(2)
    ener1.metric(label="Total Energy Demand", value=round(df_summary['Total Energy Demand'],1), delta="1.2 °F")
    ener2.metric(label="Total Energy Usage", value=round(df_summary['Total Energy Usage'],1), delta="1.2 °F")



#def main_result_comp_timeseries():
    
#    st.line_chart






####################################
##### Ubran District Upscaling #####
####################################


def udu_result_page():
    
    udu_page = st.container()
    
    with udu_page:
        st.title("Hier wird das Urban District Upscaling Tool platziert.")







####################################
############ DEMO Tool #############
####################################


def demo_result_page():
    
    demo_page = st.container()
    
    with demo_page:
        st.title("Hier wird das Demotool platziert.")



####################################
######## STREAMLIT SETTINGS ########
####################################


def st_settings_global():
    """
    Function to define settings for the Streamlit GUI.

    """
    
    # Global page settings
    st.set_page_config(
        page_title=('SESMG'),
        layout='wide', 
        menu_items={'Get Help': 'https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/',
                    'Report a Bug': 'https://github.com/chrklemm/SESMG/issues'})



####################################
########### RUN THE APP ############
####################################

# Import settings
st_settings_global()

app_mode = st.sidebar.selectbox(
    "Choose the app mode",
    ["Main SESMG Application", 
     "Urban District Upscaling Tool", 
     "SESMG Demo Tool"])


if app_mode == "Main SESMG Application":
    main_page()
    main_sidebar()
elif app_mode == "Urban District Upscaling Tool":
    udu_result_page()
elif app_mode == "SESMG Demo Tool":
    demo_result_page()
    
    
    
    
    
    
    
    
    
    

# =============================================================================
# def main_result_page():    
#     
#     mr_page = st.container()
#     
#     with mr_page: 
#         st.title("Spredsheet Energy System Model Generator - Result Overview")   
# 
#     # rerun the model
#     if st.sidebar.button("Rerun",):
#         st.experimental_rerun()
#         
#     expaner_main = st.sidebar.expander("Input Main")    
#     expaner_main.checkbox("Show3 Graph")    
# =============================================================================
