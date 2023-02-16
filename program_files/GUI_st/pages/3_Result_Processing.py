import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode 
import plotly.express as px
from PIL import Image
import glob
import os


from GUI_st_global_functions import clear_GUI_main_settings, safe_GUI_input_values, import_GUI_input_values_json, st_settings_global, run_SESMG


def result_processing_sidebar():
    """
        Function to create the sidebar.

    """
    #create sidebar
    with st.sidebar:
        
        st.header("Result Overview")
        
        # read subfolders in the result folder directory        
        existing_result_foldernames_list = [os.path.basename(x) for x in glob.glob(f'results/*')]
        existing_result_foldernames_list.sort()
        # create selectbox with the foldernames which are in the results folder 
        existing_result_folder = st.selectbox(label="Choose the result folder", options=existing_result_foldernames_list)
        
        # chebox if user wants to reload existing results
        run_existing_results = st.checkbox(label="Load Existing Results")
        
        # create checkbox if results are pareo results with subfolders
        existing_pareto_results = st.checkbox(label="Pareto Results")
        st.write(existing_pareto_results)
        if run_existing_results == True and existing_pareto_results == False:
            # set session state with full folder path to the result folder 
            st.session_state["state_result_path"] = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) +"/results/" + existing_result_folder
        
        
        
        st.header("Pareto Results")
        
        
        
        
        st.header("Energy Amount Diagramms")
        
        
        st.button(label="Create Diagramms")


def short_result_summary(result_path_summary):
    """
        Function displaying the short result summary overview of the energy system. 
        :param result_path_summary: path to a result summary.csv file
        :type result_path_summary: str
    """
    # Import summary.csv and create dataframe
    df_summary = pd.read_csv(result_path_summary)
    # Create list with headers
    summary_headers = list(df_summary)
    
    # Display and import time series values
    time1, time2 = st.columns(2)
    time1.metric(label="Start Date", value=str(df_summary.iloc[0,0]))
    time2.metric(label="End Date", value=str(df_summary.iloc[0,1]))
#TODO: Problem Darstellung Temporal Resolution     
    #time3.metric(label="Temporal Resolution", value=str(df_summary['Resolution']))            

#TODO: add delta functions based on the latest results    
    # Display and import simulated cost values from summary dataframe
    cost1, cost2, cost3, cost4 = st.columns(4)
    cost1.metric(label=summary_headers[3], value=round(df_summary[summary_headers[3]],1))
    cost2.metric(label=summary_headers[4], value=round(df_summary[summary_headers[4]],1))
    cost3.metric(label=summary_headers[5], value=round(df_summary[summary_headers[5]],1))
    cost4.metric(label=summary_headers[6], value=round(df_summary[summary_headers[6]],1))
    
    # Display and import simulated energy values from summary dataframe
    ener1, ener2 = st.columns(2)
    ener1.metric(label=summary_headers[7], value=round(df_summary[summary_headers[7]],1))
    ener2.metric(label=summary_headers[8], value=round(df_summary[summary_headers[8]],1))   
    

def short_result_table(result_path_components):   
    """
        Function to create tabel of components 
        :param result_path_components: path to a result components.csv file
        :type result_path_components: str
    """   
    # Import components.csv and create dataframe
    df_components = pd.read_csv(result_path_components)
    # CSS to inject contained in a string
    hide_dataframe_row_index = """
                <style>
                .row_heading.level0 {display:none}
                .blank {display:none}
                </style>
                """
    
    # create table 
    # Inject CSS with Markdown
    st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
    # Creating st_aggrid table
    AgGrid(df_components, height = 400, fit_columns_on_grid_load=True, update_mode=GridUpdateMode.SELECTION_CHANGED)
    
    
def short_result_intercative_dia(result_path_results):
    """
        Function to create interactive results.  
        :param result_path_results: path to a result results.csv file
        :type result_path_results: str
    """
    # loading result.csv as a dataframe
    result_df = pd.read_csv(result_path_results)    
    # creating column headers to select
    column_headers_result = list(result_df.columns.values)
    # column headers without date
    list_headers = column_headers_result[1:]
    # selecting headers
    select_headers = st.multiselect("Select a bus:", list_headers)
    # filtered dataframe
    filtered_df = result_df[select_headers]
    # plotting
    fig = px.line(filtered_df)
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    
    
def short_result_graph(result_path_graph):
    """
        Function to display the energy systems structure in a streamlit expander.
        :param result_path_graph: path to a result graph.gv.png file
        :type result_path_graph: str
    """   
    # Header
    st.subheader("The structure of the modeled energy system:")
    # Importing and printing the energy system graph
    with st.expander("Show the structure of the modeled energy system"):
        es_graph = Image.open(result_path_graph, "r")
        st.image(es_graph)





# initialize global page settings
st_settings_global()

# start sidebar functions
result_processing_sidebar()

st.write(st.session_state)

# initialize session state  if no result paths are definied on main page
if "state_result_path" not in st.session_state:    
    st.session_state["state_result_path"] = "not set"
  
# show introduction page if no result paths are not set
if st.session_state["state_result_path"] == "not set":    
    st.write("This ia a dummy. You can choose your resultfolder here as ....")


else:

    # show short result summarys key values
    short_result_summary(result_path_summary=st.session_state["state_result_path"]+"/summary.csv")
    # show components table
    short_result_table(result_path_components=st.session_state["state_result_path"]+"/components.csv")
    # show interacitve result diagram
    short_result_intercative_dia(result_path_results=st.session_state["state_result_path"]+"/results.csv")
    # show energy system graph
    short_result_graph(result_path_graph=st.session_state["state_result_path"]+"/graph.gv.png")
    
    


    

