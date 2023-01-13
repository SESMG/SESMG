# -*- coding: utf-8 -*-




import streamlit as st
import pandas as pd
from PIL import Image
import os
from datetime import datetime 

from program_files.urban_district_upscaling.pre_processing import urban_district_upscaling_pre_processing

####################################
##### Ubran District Upscaling #####
####################################



def us_application():
    
    
    with st.sidebar.form("Input Parameters"):
        
        # Submit button to start optimization.
        submitted_us_run = st.form_submit_button("Start US Tool")
    
        # Functions to implement text inputs in the form.
        # Text Input prescenario path
        input_prescenario_path = st.text_input("Type in path to your prescenario input sheet.")
        # Text Input standart parameter path
        input_standardparam_path = st.text_input("Type in path to your standard parameter sheet.")
        # Text Input result folder path
        input_result_path = st.text_input("Type in path to the result folder.")

        # Functions to implement checkboxes in the form.
        # Checkbox to active clustering
        input_clustering = st.checkbox("Clustering")   
        # Checkbox to active district heating clustering
        input_clustering_dh = st.checkbox("Clustering District Heating")  
        
        ### Run prgram main function if start button is clicked
        if submitted_us_run: 
            
            if input_prescenario_path != "" and input_standardparam_path != "" and input_result_path != "":
                
                us_path_list = [
                    input_prescenario_path,
                    input_standardparam_path,
                    input_result_path,
                    os.path.join(os.path.dirname(__file__)+"/program_files/urban_district_upscaling/plain_scenario.xlsx")
                    ]
                
                urban_district_upscaling_pre_processing(paths=us_path_list, clustering=False, clustering_dh=False)
            
    
    
    
    udu_page = st.container()
    
    with udu_page:
        st.title("Hier wird das Urban District Upscaling US Tool platziert.")
        
        
        