# -*- coding: utf-8 -*-
"""Creates HTML results for the Spreadsheet Energy System Model Generator.

Uses the results of the Spreadsheet Energy System Model Generator to create
and launche a interactive HTML page. The HTML Page can be accessed with any
internet browser by entering http://127.0.0.1:8050/.

The HTML-Page consists the following elements:
    - table (1) summarizing the modelling results
    - table (2) summarizing every component of the model
    - drop down menu, where the user can select which timeseries should be 
      displayed in the following graph.
    - graph, where the timeseries' of all components can be displayed
    
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import subprocess
import os
import base64
from dash_canvas import DashCanvas
import io
from PIL import Image
import sys

def return_component_value(ID, df_table):
    """Returns data for the graph.
    
    Function which returns date to be displayed within the graph, depending 
    from which components have been selected within the drop-down menu.
    
    """
        
    values = df_table[ID].tolist()
    dates = df_table["date"].tolist()
    name = df_table[ID].name
    #print(str(name)+' selected.')
    return{
            'x':dates,
            'y':values,
            'mode':'lines',
            'name':str(name)
            }

#Imports Data created by the Spreadsheet Energy System Model Generator
df_table = pd.read_csv(r"results/results.csv")
df_components = pd.read_csv(r"results/components.csv")
#df_model_properties = pd.read_csv(r"results/model_properties.csv")

# Prepares Data for table 1
df_summary = pd.read_csv(r"results/summary.csv")

total_system_costs = float(df_summary['Total System Costs'])
total_variable_costs = float(df_summary['Total Variable Costs'])
total_periodical_costs = float(df_summary['Total Periodical Costs'])
total_energy_demand = float(df_summary['Total Energy Demand'])
total_energy_usage = float(df_summary['Total Energy Usage'])
start_date = str(df_summary['Start Date'][0])
end_date = str(df_summary['End Date'][0])
temoral_resolution = str(df_summary['Resolution'][0])

# Prepares Date for table 2
dates = df_table["date"].tolist()

list_of_components = df_table.columns.values
list_of_components = list_of_components[1:len(list_of_components)]

#Import Image
graph_png = 'results/graph.gv.png'
test_base64 = base64.b64encode(open(graph_png, 'rb').read()).decode('ascii')

# Sets Canvas width in dependency from the image height
imgdata = base64.b64decode(test_base64)
im = Image.open(io.BytesIO(imgdata))
width, height = im.size
canvas_width = (800/height)*width
if canvas_width > 2300:
    canvas_width = 2300
print(height)
print(width)

# loading external resources (stylesheets)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
options = dict(
)

# Creating the application, which is running the interactive page
demo_app = dash.Dash(__name__, **options)




demo_app.layout = html.Div(

    children=[
        # Creates the Headline
        html.H1(children='Spreadsheet Energy System Model Generator - Interactive Results'),

        # Creates the Sub-Headline
        html.Div(children='''Summary of the modelling:'''),
        #Creates Table 1
        dash_table.DataTable(
             id='table2',
             # Defines, that all collumns from df_summary shall be shown
             columns=[{"name": i, "id": i} for i in df_summary.columns],
             data=df_summary.to_dict('records'),
             # Defines the Style of the Table
             style_table={
                        'margin':{
                            'b':10000
                            }
                         }
        ),

        # Includes Image
        DashCanvas(id='graph',
                   tool='line',
                   lineWidth=5,
                   #hide_buttons=['line', 'zoom', 'pan'],
                   lineColor='red',
                   image_content='data:image/png;base64,{}'.format(test_base64),
                   width=canvas_width),

        # Creates the Sub-Headline
        html.Div(
                children=[html.Div("-"),
                          html.Div("-"),
                          html.Div("-"),
                          html.Div("Summary of the components:"),

                          ]),  
         # Creates Table 2
         dash_table.DataTable(
             id='table',
             # Defines, that all columns of df_components shall be shown
             columns=[{"name": i, "id": i} for i in df_components.columns],
             data=df_components.to_dict('records'),
             # Defines the Style of the Table
             style_table={
                 'maxHeight': '300px',
                 'overflowY': 'scroll'
             },
              filter_action="native",
              sort_action="native",
              fixed_rows={'headers': True, 'data': 0},
             style_cell={
                     #'width':'10px'
                     'minWidth':'40px',
                     'maxWidth':'50px',
                     'textOverflow': 'ellipsis',
                     }
         ),
        # Creates the Sub-Headline
        html.Div(
                children=[html.Div("-"),
                          html.Div("-"),
                          html.Div("-"),

                          ]),
         # Defines a fiels, where all selected elements of the following drop-
         # down menue are listed
         html.Div("Selection", id="example-div"),
         # Defines the Drop-Down menu
         dcc.Dropdown(
                 id="component-select",
                 # Defines, that all elements of the list list_of_components 
                 # can be selected
                 options=[
                         {'label': i, 'value': i} for i in list_of_components
                         ],
                 # Defines, that more than one element can be selected
                 multi=True
                 ),
        # Defines the Graph 
        dcc.Graph(
            id='example-graph',
            # Defines the default plot shown in the graph
            figure={
                'data': [
                    {'x': dates,
                     'y': [0,0],
                     'mode':'lines'}                      
                ],
                # Defines the layout of the graph
                'layout': {
                    'title': 'Component Time Series',
                    'xaxis':{
                        'title':'date'
                        },
                    'yaxis':{
                        'title':'performance [kW] / storage capacity [kWh]'
                        }
                }
            }
        ),

    ]
)

# Opens the HTML-Page by utilizing an .cmd command.(WINDOWS)
#if sys.platform.startswith("win"):
#    subprocess.call("start http://127.0.0.1:8050/", shell=True)
# Opens the HTML-Page by utilizing an .command command.(MACOS)
#elif sys.platform.startswith("darwin"):
#    subprocess.call("open http://127.0.0.1:8050/", shell=True)

# app for updating the drop-down menue         
@demo_app.callback(
        Output(component_id="example-div", component_property="children"),
        [Input(component_id="component-select", component_property="value")]
        )
def update_component(ID):         
     return str(ID) 

# app for updating the graph
@demo_app.callback(
        Output(component_id="example-graph", component_property="figure"),
        [Input(component_id="component-select", component_property="value")]
       # [State(component_id="example-graph", component_property="figure")]
        )
def update_graph(component_IDS):
    if component_IDS is  None:
        raise PreventUpdate
    else:
        fig={
        'data': [
            return_component_value(ID=ID, df_table=df_table)
            for ID in component_IDS
        ],
        'layout': {
            'title': 'Component Time Series',
            'xaxis':{
                    'title':'date'
                    },
            'yaxis':{
                    'title':'performance [kW] / storage capacity [kWh]'
                    }
        }
        }
        return(fig)

if __name__ == '__main__':
    demo_app.run_server(debug=True)
