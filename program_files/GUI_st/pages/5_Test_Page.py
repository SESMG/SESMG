# imports
import streamlit as st
import os

from GUI_st_global_functions import st_settings_global

####################################
# settings the initial streamlit page settings
st_settings_global()

def test_page():
    from GUI_streamlit import (import_GUI_input_values_json, \
                               safe_GUI_input_values, \
                               clear_GUI_input_values)

    settings_cache_dict_reload = import_GUI_input_values_json(
        os.path.dirname(__file__) + "/GUI_test_setting_cache.json")

    st.write(settings_cache_dict_reload)

    st.title("Hier werden erweitere Ergebnisaufbereitungen dargestellt.")

    # test - verschieben von einer Seite zu einer anderen Seite
    if "energiemodell" not in st.session_state:
        st.session_state["energiemodell"] = ""

    check = st.checkbox("Datei die auf eine andere Seite geschickt wird:")

    if check:
        energiemodell = st.file_uploader("Import your model definition:", st.session_state["energiemodell"])
        # energiemodell = st.text_input("Input:", st.session_state["energiemodell"])
        submit_em = st.button("Submit")
        if submit_em:
            st.session_state["energiemodell"] = energiemodell
            st.write(energiemodell)



    if st.sidebar.button("Clear Cache"):
        settings_cache_dict_reload_2 = clear_GUI_input_values(settings_cache_dict_reload, "main_page", os.path.dirname(
            __file__) + "/GUI_test_setting_cache.json")

        # rerun whole script to update GUI settings
        st.experimental_rerun()

    with st.sidebar.form("Input Parameters"):

        # Submit button to start optimization.
        submitted_optimization = st.form_submit_button("Start Inputs")
        input1 = st.text_input("Test Input 1", value=settings_cache_dict_reload["input1"])
        input2 = st.text_input("Test Input 2", value=settings_cache_dict_reload["input2"])

        if submitted_optimization:
            settings_cache_dict = {"input1": input1, "input2": input2}

            # sfe GUI settings dict
            safe_GUI_input_values(settings_cache_dict, os.path.dirname(__file__) + "/GUI_test_setting_cache.json")

            # rerun whole script to update GUI settings
            st.experimental_rerun()




test_page()
