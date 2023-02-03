# todo implemt the demo tool
# imports
import streamlit as st
import pandas as pd


# function to show the demo tool
def demo_result_page():
    demo_page = st.container()
    test_df = pd.read_excel(st.session_state["energiemodell"])
    st.dataframe(test_df)
    with demo_page:
        st.title("Demo toool following soon")


demo_result_page()
