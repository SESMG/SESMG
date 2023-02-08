# todo implemt the demo tool
# imports
import streamlit as st
import pandas as pd

from GUI_st_global_functions import st_settings_global

####################################
# settings the initial streamlit page settings
st_settings_global()


# function to show the demo tool
def demo_result_page():
    demo_page = st.container()
    test_df = pd.read_excel(st.session_state["energiemodell"])
    st.dataframe(test_df)
    with demo_page:
        st.title("Demo toool following soon")


demo_result_page()
