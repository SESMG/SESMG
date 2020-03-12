# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go


df_table = pd.read_csv(r"results/results.csv")
#print(df_table.columns.values)
##df = pd.read_csv(r"results/results.csv").set_index("ID")
##print(df)

df_test = pd.read_csv(r"results/results.csv").set_index("date")
#print(df_test)

df_components = pd.read_csv(r"results/components.csv")
df_model_properties = pd.read_csv(r"results/model_properties.csv")

##print(df_table)
##print(type(df_table))
##print(df_table.head(0))
dates = df_table["date"].tolist()
##print(dates)
##values = df_table["ID"].tolist()
##print(values)
##print(df_table['ID'])

list_of_components = df_table.columns.values
list_of_components = list_of_components[1:len(list_of_components)]
#print(list_of_components)


df_summary = pd.read_csv(r"results/summary.csv")



total_system_costs = float(df_summary['Total System Costs'])
total_variable_costs = float(df_summary['Total Variable Costs'])
total_periodical_costs = float(df_summary['Total Periodical Costs'])
total_energy_demand = float(df_summary['Total Energy Demand'])
total_energy_usage = float(df_summary['Total Energy Usage'])
start_date = str(df_summary['Start Date'][0])
end_date = str(df_summary['End Date'][0])
temoral_resolution = str(df_summary['Resolution'][0])

def return_component_value(ID, df_table):
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

def extract_component(ID):
    return{
            'x': df.loc[ID].date,
            'y': df.loc[ID].performance,
            'mode':'lines+markers',
            'name':df.loc[ID].component.unique()[0]
            }
##    return{
##              'x': df_table['date'],
##              'y': [1,2,3], #df_table[ID],
##              'mode':'lines',
##              #'name':df.loc[ID].component.unique()[0]
##              }






# loading external resources
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
options = dict(
    # external_stylesheets=external_stylesheets
)

demo_app = dash.Dash(__name__, **options)

demo_app.layout = html.Div(
    children=[
        html.H1(children='Spreadsheet Energy System Model Generator'),

        html.Div(children='''Modelling Results'''),
        #html.Div("Selection", id="example-div"),
        dash_table.DataTable(
             id='table2',
             columns=[{"name": i, "id": i} for i in df_summary.columns],
             data=df_summary.to_dict('records'),
             style_table={
                        'margin':{
                            'b':10000
                            }
                         }
        ),
        html.Div(
                children=[html.Div("-"),
                          html.Div("-"),
                          html.Div("-"),

                          ]),  
        
         dash_table.DataTable(
             id='table',
             columns=[{"name": i, "id": i} for i in df_components.columns],
             data=df_components.to_dict('records'),
             style_table={
                 'maxHeight': '300px',
                 'overflowY': 'scroll'
             },
              filter_action="native",
              sort_action="native",
              fixed_rows={'headers': True, 'data': 0}
         ),
        html.Div(
                children=[html.Div("-"),
                          html.Div("-"),
                          html.Div("-"),

                          ]),        
         html.Div("Selection", id="example-div"),
         dcc.Dropdown(
                 id="component-select",
                 options=[
##                         {'label': 'label1', 'value':'value1'},
##                         {'label': 'label2', 'value':'value2'},
##                         {'label': 'label3', 'value':'value3'},

                         {'label': i, 'value': i} for i in list_of_components#.dropna().unique

                         #{'label':list_of_components[i], 'value':i}
                         #{'label':df_components.ID.unique()[0], 'value':i}
                         #{'label':df.loc[i].component.unique()[0], 'value':i}
                         #for i in list_of_components
                         #for i in df_components.ID.dropna().unique()
                         ],
                 multi=True
                 ),
         
        dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    #return_component_value(ID="none", df_table=df_table)
                    {'x': dates,#['2012-01-01 00:00:00', '2012-01-01 01:00:00', '2012-01-01 02:00:00'],
                     'y': [1,1,1,1],#df_table['ID'],
                     'mode':'lines+markers'}
                     
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
        )
    ]
)

import subprocess
subprocess.call("start http://127.0.0.1:8050/", shell=True)
         
@demo_app.callback(
        Output(component_id="example-div", component_property="children"),
        [Input(component_id="component-select", component_property="value")]
        )
def update_component(ID):         
     return str(ID) 


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
##            return_component_value(ID="electricity_demand_001", df_table=df_table)
            return_component_value(ID=ID, df_table=df_table)
            for ID in component_IDS
            #{'x': dates,#['2012-01-01 00:00:00', '2012-01-01 01:00:00', '2012-01-01 02:00:00'],
            #'y': [1,2,3,4],#df_table['ID'],
            #'mode':'lines+markers'}
            #extract_component(ID)
            #for ID in component
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
