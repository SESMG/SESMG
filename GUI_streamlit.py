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

# from program_files.preprocessing.Spreadsheet_Energy_System_Model_Generator import sesmg_main
# from program_files.preprocessing.Spreadsheet_Energy_System_Model_Generator import sesmg_main_including_premodel

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
                    'Report a Bug': 'https://github.com/SESMG/SESMG/issues'})



####################################
####### Global GUI functions #######
####################################




def import_GUI_input_values_json(json_file_path):
    """
        :param json_file_path: file name to the underlying json with input values for all GUI pages
        :type json_file_path: str
        :param GUI_settings_cache_dict_reload: exported dict from json file including a (sub)dict for every GUI page
        :type json_file_name: dict
    """
    #Import json file including several (sub)dicts for every GUI page 
    #Each (sub)dict includes input values as a cache from the last session
    with open(json_file_path, "r") as infile:
        GUI_settings_cache_dict_reload = json.load(infile)
        
    return GUI_settings_cache_dict_reload


def safe_GUI_input_values(input_values_dict, json_file_path):
    """
        :param input_values_sub_dict: name of the dict of input values for specific GUI page
        :type input_values_dict: dict
        :param json_file_path: file name to the underlying json with input values
        :type json_file_path: str
    """
    
    with open(json_file_path, 'w') as outfile:
        json.dump(input_values_dict, outfile, indent=4)

                
def clear_GUI_input_values(input_values_dict, name_sub_dict, json_file_path):
    """
        :param input_values_sub_dict: name of the dict of input values for specific GUI page
        :type input_values_dict: dict
        :param name_sub_dict: name of the subdict in the json-file can be "main_page", "udu_page", "result_page", or "test_page"
        :type name_sub_dict: str
        :param json_file_path: file name to the underlying json with input values
        :type json_file_path: str
    """
    #Clearing the GUI input values of the subdict / GUI page
    input_values_dict_cleared = dict.fromkeys(input_values_dict, "")
    
    #Saving the updates GUI dicts
    updated_GUI_dict = safe_GUI_input_values(input_values_dict_cleared, 'GUI_test_setting_cache.json')
                              
    return updated_GUI_dict


if os.path.exists(os.path.dirname(__file__) + "/program_files/GUI_st/GUI_cache.json") == True:

    # create empty GUI values dict
    GUI_input_values_empty = {
        "main_page": {},
        "udu_page": {},
        "result_page": {},
        "test_page": {},
        }
    safe_GUI_input_values(GUI_input_values_empty, os.path.dirname(__file__) + "/program_files/GUI_st/GUI_cache.json")
    

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
     "SESMG Demo Tool",
     "Development Test Page"])


if app_mode == "Main SESMG Application":
    main_application_sesmg()
elif app_mode == "Urban District Upscaling Tool":
    us_application()
elif app_mode == "Advanced Model Results":
    advanced_result_page()
elif app_mode == "SESMG Demo Tool":
    demo_result_page()
elif app_mode == "Development Test Page":
    test_page()
    
    




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













