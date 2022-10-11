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

from program_files.preprocessing.Spreadsheet_Energy_System_Model_Generator import sesmg_main

from program_files.GUI_st.GUI_st_US import *
from program_files.GUI_st.GUI_st_mainpage import *



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
     "Advanced Model Results",
     "SESMG Demo Tool"])


if app_mode == "Main SESMG Application":
    main_application_sesmg()
elif app_mode == "Urban District Upscaling Tool":
    us_application()
elif app_mode == "Advanced Model Results":
    advanced_result_page()
elif app_mode == "SESMG Demo Tool":
    demo_result_page()
    
    
    








# ####################################
# ###### SESMG Advanced Results ######
# ####################################


# def advanced_result_page():
    
#     udu_page = st.container()
    
#     with udu_page:
#         st.title("Hier werden erweitere Ergebnisaufbereitungen dargestellt.")
        

# ####################################
# ############ DEMO Tool #############
# ####################################


# def demo_result_page():
    
#     demo_page = st.container()
    
#     with demo_page:
#         st.title("Hier wird das Demotool platziert.")













