# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import subprocess
import os
from Spreadsheet_Energy_System_Model_Generator import SESMG


# import Shapefiles
# import ast


def create_elements(sheet, elements, texts, values, first_row):
    ''' Creates a block of tk-inter elements. The elements are created from an input dictionary. The tk-inter output
    has the following structure:

    TEXT 1 | TEXT 2 | TEXT 3 | INPUT FIELD   | TEXT 4
    ...    | ...    | ...    | ...           | ...
           |        |        | UPDATE BUTTON |

    The block will have the number of lines that the input dictionary elements have. By pressing the "UPDATE BUTTON"
    the value "TEXT 2" will be replaced with the input given with the input field.

    ---

    Input variables:

    sheet: sheet within the window, where the element block will be placed

    elements: dictionary containing elements wich will be shown within this tk-inter block. Structure of the dictionary
                has to be as follows: elements = {'rowname':['text 1', 'text 2', 'text 3', 'text 4']}

    texts: list, where the elements of column 3 (TEXT 4) will be saved. Required for data updates.

    values: list, where the elements of column 1 (TEXT 2) will be saved. Required for data updates.

    first_row: top line of the window sheet where the block should be positioned.

    '''

    element_keys = [i for i in elements.keys()]

    # Creates the row elements of the time-series-sheet
    for i in range(len(elements)):
        row = i + first_row + 1

        variable_name = Label(sheet, text=elements[element_keys[i]][0], font=('Helvetica 10'))
        variable_name.grid(column=0, row=row, sticky="W")

        variable_value = Label(sheet, text=str(elements[element_keys[i]][1]), font=('Helvetica 10'))
        values.append(variable_value)
        values[i].grid(column=1, row=row)

        variable_unit = Label(sheet, text=str(elements[element_keys[i]][2]), font=('Helvetica 10'))
        variable_unit.grid(column=2, row=row, sticky="W")

        variable_text = Entry(sheet, width=20, font=('Helvetica 10'))
        texts.append(variable_text)
        texts[i].grid(column=3, row=row)

        variable_format = Label(sheet, text=elements[element_keys[i]][3], font=('Helvetica 10'))
        variable_format.grid(column=4, row=row, sticky="W")


def create_main_frame_elements(elements, sheet, first_row, file_paths, frame):
    ''' Creates a block of tk-inter elements. The elements are created from an input dictionary. The tk-inter output
       has the following structure:

       TEXT 1 | BUTTON | TEXT 2 |
       ...    | ...    | ...    |

       The block will have the number of lines that the input dictionary elements have. By pressing the "BUTTONS"
       stored functions will be executed.

       ---

       Input variables:

       sheet: sheet within the window, where the element block will be placed

       elements: dictionary containing elements wich will be shown within this tk-inter block. Structure of the dictionary
                   has to be as follows: elements = {'rowname':['text 1', function to be executed, 'text 2'}

       frame: sheet within the window, where the element block will be placed

       file_paths: dictionary where the values of TEXT 2 can be saved. Required for later changes.

       first_row: top line of the window sheet where the block should be positioned.

       '''
    element_keys = [i for i in elements.keys()]

    for i in range(len(elements)):
        row = i + first_row + 1

        label_name = Label(sheet, text=elements[element_keys[i]][0], font=('Helvetica 10'))
        label_name.grid(column=0, row=row, sticky="W")

        button = Button(frame, text=elements[element_keys[i]][2], command=elements[element_keys[i]][1])
        button.grid(column=3, row=row)

        label_comment = Label(sheet, text=elements[element_keys[i]][3], font=('Helvetica 10'))
        file_paths.append(label_comment)
        file_paths[i].grid(column=4, row=row, sticky="W")


def update_values(texts_input, rows, input_elements, input_values):
    input_element_keys = [i for i in input_elements.keys()]

    for j in range(rows):
        input_text = texts_input[j]
        if len(input_text.get()) > 0:
            input_elements[input_element_keys[j]][1] = input_text.get()
            input_values[j].configure(text=input_text.get())


def data_path():
    print('placeholder')


def getFolderPath():
    ''' opens a file dialog and sets the selected path for the variable "scenario_path"
    '''

    path = filedialog.askopenfilename(filetypes=(("Spreadsheet Files", "*.xlsx"), ("all files", "*.*")))
    print(path)

    scenario_path.set(path)
    print(scenario_path.get())

    file_paths[0].configure(text=scenario_path.get())


def getFolderPath2():
    ''' opens a file dialog and sets the selected path for the variable "sf_residential"
    '''
    path = filedialog.askopenfilename(filetypes=(("Spreadsheet Files", "*.shp"), ("all files", "*.*")))
    print(path)

    sf_residential.set(path)
    print(sf_residential.get())

    file_paths3[1].configure(text=sf_residential.get())


def getFolderPath3():
    ''' opens a file dialog and sets the selected path for the variable "sf_non_residential"
    '''
    path = filedialog.askopenfilename(filetypes=(("Spreadsheet Files", "*.shp"), ("all files", "*.*")))
    print(path)

    sf_non_residential.set(path)
    print(sf_non_residential.get())

    file_paths3[2].configure(text=sf_non_residential.get())


def getFolderPath4():
    ''' opens a file dilaog and sets the selected path for the variable "weather_path"
    '''
    path = filedialog.askopenfilename(filetypes=(("Spreadsheet Files", "*.xlsx"), ("all files", "*.*")))
    print(path)

    weather_path.set(path)
    print(weather_path.get())

    file_paths3[0].configure(text=weather_path.get())


def show_graph():
    ''' creates and shows a graph of the energy system given by a Spreadsheet'''
    import os
    from program_files import (create_energy_system,
                               create_graph)

    # DEFINES PATH OF INPUT DATA
    scenario_file = scenario_path.get()

    # DEFINES PATH OF OUTPUT DATA
    result_path = os.path.join(os.path.dirname(__file__) + '/results')

    # IMPORTS DATA FROM THE EXCEL FILE AND RETURNS IT AS DICTIONARY
    nodes_data = create_energy_system.import_scenario(filepath=scenario_file)

    # PRINTS A GRAPH OF THE ENERGY SYSTEM
    create_graph.create_graph(filepath=result_path,
                              nodes_data=nodes_data,
                              legend=False)


def execute_sesmg():
    ''' Excecutes the optimization algorithm '''
    if scenario_path.get() != "No scenario selected.":
        scenario_file = scenario_path.get()
        result_path = os.path.join(os.path.dirname(__file__) + '/results')
        SESMG(scenario_file=scenario_file, result_path=result_path)
        show_results()
    else:
        print('Please select scenario first!')
        comments[2].configure(text='Please select scenario first!')


def get_pid():
    ''' Returns the ID of the running process on Port 8050 '''
    import socket
    import errno
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Checks if port 8050 can be reached
        s.bind(("127.0.0.1", 8050))
        # If Yes, the program continues in line 225
        closeprocess = False
    # If not, the ID of the running process is returned
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            closeprocess = True
    s.close()
    if closeprocess:
        if sys.platform.startswith("win"):
            command = "netstat -aon| findstr 8050"
        elif sys.platform.startswith("darwin"):
            command = "lsof -i tcp:8050"
        pids = subprocess.check_output(command, shell=True)
        pids = str(pids)
        pidslist = pids.split()
        if sys.platform.startswith("win"):
            pid = pidslist[4]
        elif sys.platform.startswith("darwin"):
            pid = pidslist[9]
        return pid
    else:
        return ''


def show_results():
    ''' executes the external program, which executes a plotl.dash app for displaying interactive results.
    '''
    # Determines the ID of a still running process on port 8050.
    pid = get_pid()
    # Checks if the ID is not an empty return (no process available)
    if pid != '':
        if sys.platform.startswith("win"):
            command = 'taskkill /PID ' + pid
        elif sys.platform.startswith("darwin"):
            command = 'kill ' + pid
        # Kills the still running process on port 8050
        subprocess.call(command, shell=True)

    # Starts the new Plotly Dash Server for Windows
    if sys.platform.startswith("win"):
        subprocess.call("Interactive_Results.py", timeout=10, shell=True)
        subprocess.call("start http://127.0.0.1:8050/", shell=True)

    # Starts the new Plotly Dash Server for MACOS
    elif sys.platform.startswith("darwin"):
        subprocess.call("python3 Interactive_Results.py", timeout=10, shell=True)
        subprocess.call("open http://127.0.0.1:8050/", shell=True)


# def end_program():
#     ''' kills the entire application'''
#     app_pid = os.getpid()
#     os.kill(app_pid, 0)


# def create_scenario_graph():
#     ''' creates a xlsx scenario from a shapefile and shows its graph'''
#     create_scenario()
#     scenario_path.set("shape_scenario.xlsx")
#     file_paths[0].configure(text=scenario_path.get())
#     show_graph()
#
# def create_scenario_optimize():
#     ''' creates a xlsx scenario from a shapefile and optimizes it'''
#     create_scenario()
#     scenario_path.set("shape_scenario.xlsx")
#     file_paths[0].configure(text=scenario_path.get())
#     execute_sesmg()
#
# def create_scenario():
#     ''' creates a xlsx scenario from a shapefile'''
#
#     # Defines timesystem parameters
#     timesystem_parameters = {
#         'start_date': values[0].cget("text"),
#         'end_date': values[1].cget("text"),
#         'temporal_resolution': values[2].cget("text"),
#         'periods': values[3].cget("text")}
#
#     bus_parameters = {
#         'electricity_excess_costs': bus_values[0].cget("text"),
#         'electricity_shortage_costs': bus_values[1].cget("text"),
#         'heat_excess_costs': bus_values[2].cget("text"),
#         'naturalgas_shortage_costs': bus_values[3].cget("text"),
#         'pv_excess_costs': bus_values[4].cget("text")
#     }
#
#     pv_parameters = {
#         'pv_variable_costs': pv_values[0].cget("text"),
#         'pv_periodical_costs': pv_values[1].cget("text"),
#         'pv_technology_database': pv_values[2].cget("text"),
#         'pv_inverter_database': pv_values[3].cget("text"),
#         'pv_modul_model': pv_values[4].cget("text"),
#         'pv_inverter_model': pv_values[5].cget("text"),
#         'pv_albedo': pv_values[6].cget("text"),
#         'pv_altitude': pv_values[7].cget("text"),
#         'pv_latitude': pv_values[8].cget("text"),
#         'pv_longitude': pv_values[9].cget("text")
#     }
#
#     electricity_demand_parameters={
#                 'residential_load_profile' : el_demand_values[0].cget("text"),
#                 'building_class' : el_demand_values[1].cget("text"),
#                 'wind_class' : el_demand_values[2].cget("text"),
#                 'demand_single_family_building' : ast.literal_eval(el_demand_values[3].cget("text")),
#                 'demand_multi_family_building' : ast.literal_eval(el_demand_values[4].cget("text"))
#     }
#
#     heat_demand_parameters={
#         'NFA_coefficient' : float(he_demand_values[0].cget("text")),
#         'demand_residential_building' : {1000:{1:247,2:238,3:212,7:182,13:169},
#                                           1919:{1:254,2:236,3:211,7:178,13:153},
#                                           1949:{1:236,2:219,3:192,7:166,13:140},
#                                           1979:{1:175,2:168,3:155,7:152,13:118},
#                                           1991:{1:131,2:127,3:127,7:114,13:101},
#                                           2001:{1:83,2:88,3:80,7:76,13:69},
#                                           2009:{1:48,2:46,3:46,7:53,13:54}
#                                           },
#         'residential_load_profile' : he_demand_values[1].cget("text"),
#         'building_class': int(he_demand_values[2].cget("text")),
#         'wind_class': int(he_demand_values[3].cget("text")),
#     }
#
#     gasheating_parameters={
#         'efficiency' : gh_values[0].cget("text"),
#         'variable_input_costs':gh_values[1].cget("text"),
#         'variable_output_costs':gh_values[2].cget("text"),
#         'variable_output_costs_2':gh_values[3].cget("text"),
#         'periodical_costs':gh_values[4].cget("text")
#     }
#
#     exchange_of_electricity_parameters={
#         'net_costs': eoe_values[0].cget("text")
#     }
#
#     pv_active = chk_state.get()
#     gh_active = gh_chk_state.get()
#     eoe_active = eoe_chk_state.get()
#
#     print(timesystem_parameters)
#     print(bus_parameters)
#     print(pv_parameters)
#     print(pv_active)
#     print(heat_demand_parameters)
#
#
#     weather_data_path = 'weather_data.xlsx'
#
#     Shapefiles.shapefile_converter(shapefile_residential=sf_residential.get(),
#                                    shapfile_non_residential=sf_non_residential.get(),
#                                    weather_data_path=weather_path.get(),
#                                    timesystem_parameters=timesystem_parameters,
#                                    bus_parameters=bus_parameters,
#                                    pv_active=pv_active,
#                                    pv_parameters=pv_parameters,
#                                    electricity_demand_parameters=electricity_demand_parameters,
#                                    heat_demand_parameters=heat_demand_parameters,
#                                    gasheating_parameters=gasheating_parameters,
#                                    gh_active=gh_active,
#                                    exchange_of_electricity_parameters=exchange_of_electricity_parameters,
#                                    eoe_active=eoe_active)


# Definition of the user interface
window = Tk()
window.title("SESMG - Spreadsheet Energy System Model Generator")
window.geometry('1000x250')
tab_control = ttk.Notebook(window)
tab_control.pack(expand=1, fill='both')
tab_control.pressed_index = None
scenario_path = StringVar(window, str(os.path.join(os.path.dirname(__file__), 'scenario.xlsx')))

    # Code relevant for Shapefileconverter
    # sf_residential = StringVar(window, str(os.path.join(os.path.dirname(__file__), 'shapefiles/Wohngebaeude.shp')))
    # sf_non_residential = StringVar(window,
    #                               str(os.path.join(os.path.dirname(__file__), 'shapefiles/Nicht_Wohngebaeude.shp')))
    # weather_path = StringVar(window, str(os.path.join(os.path.dirname(__file__), 'weather_data.xlsx')))
    # shape_path = ''

############
# MAIN FRAME
############
# Definition of the Main-Frames
    # main_frame = ttk.Frame(tab_control)
main_frame = ttk.Frame(window)
tab_control.add(main_frame, text='Home')

# Headline
main_head1 = Label(main_frame, text='Selection Options', font='Helvetica 10 bold')
main_head1.grid(column=0, row=0, sticky="w")

# Erstellung des ersten Element-Blocks
# [label, function to be executed, button label, comment]
selection_elements = {'row1': ['Select scenario file', getFolderPath, 'Change', scenario_path.get()]}
file_paths = []
create_main_frame_elements(elements=selection_elements, sheet=main_frame, first_row=1, file_paths=file_paths,
                           frame=main_frame)

# Headline 2
main_head2 = Label(main_frame, text='Execution Options', font=('Helvetica 10 bold'))
main_head2.grid(column=0, row=3 + len(selection_elements), sticky="w")

# ERstellung des zweiten Element-Blocks
# [Label, function to be executed, name of the button, comment]
test = StringVar(window)
execution_elements = {'row2': ['Show Graph', show_graph, 'Execute', ''],
                      'row3': ['Optimize Model', execute_sesmg, 'Execute', test.get()],
                      'row4': ['Show Results', show_results, 'Execute', ''],
                      # 'row1':['Shapeconverter',create_scenario,'Execute','Developing Version'],
                      # 'row5':['Shapeconverter + Show Graph',create_scenario_graph,'Execute','Developing Version'],
                      # 'row6':['Shapeconverter + Optimize Model',create_scenario_optimize,'Execute','Developing Version'],
                      # 'row7':['End Program',end_program,'End',' '],
                      }
comments = []
create_main_frame_elements(elements=execution_elements, sheet=main_frame, first_row=3 + len(selection_elements),
                           file_paths=comments, frame=main_frame)

# #######################
# # SHAPE-CONVERTER FRAME
# #######################
#
# # Creates a canvas within, which enables a scrollbar for this frame
# ContainerOne = Frame(tab_control)
# ContainerOne.pack(fill=BOTH, expand=True)
#
# tab_control.add(ContainerOne,text='Shape Converter')
# canvas1 = Canvas(ContainerOne, width=800, height=1000)
# scroll = Scrollbar(ContainerOne, command=canvas1.yview)
# canvas1.config(yscrollcommand=scroll.set, scrollregion=(0,0,100,2000))
# canvas1.pack(side=LEFT, fill=BOTH, expand=True)
# scroll.pack(side=RIGHT, fill=Y)
#
# shape_frame = Frame(canvas1, width=800, height=1000)
# canvas1.create_window(10, 10, window=shape_frame, anchor='nw')
#
# # TIMESYSTEM PARAMETERS
# ts_header = Label(shape_frame, text= 'Files',font=('Helvetica 10 bold'))
# ts_header.grid(column=0, row=0, sticky="W")
#
# # Erstellung des ersten Element-Blocks
# # [label, function to be executed, button label, comment]
# shape_selection_elements = {'row2':['Select weather data file',getFolderPath4,'Change',weather_path.get()],
#                             'row3':['Shape File (Residential)',getFolderPath2,'Change',sf_residential.get()],
#                             'row4':['Shape File (Non-Residential',getFolderPath3,'Change',sf_non_residential.get()]
#                             }
#
# file_paths3 = []
# create_main_frame_elements(elements=shape_selection_elements, sheet=shape_frame, first_row=1, file_paths=file_paths3, frame=shape_frame)
#
# # TIMESYSTEM PARAMETERS
# ts_header = Label(shape_frame, text= 'Time System Parameters',font=('Helvetica 10 bold'))
# ts_header.grid(column=0, row=5, sticky="W")
# row = 6
# # Row Elements summarized in a dictionary. The dictionary will be updated with the button functions. The dictionary can
# # be used to pass values to the program.
# ts_elements = {'row1':['Start Date','2012-01-01 00:00:00','','yyyy-mm-dd hh:mm:ss'],
#             'row2':['End Date','2012-12-30 23:00:00','','yyyy-mm-dd hh:mm:ss'],
#             'row3':['Temporal Resolution','h','','e.g. h'],
#             'row4':['Periods',8760,'',' '],}
# texts, values = [], []
# # Creates Elements
# create_elements(sheet=shape_frame, elements=ts_elements, texts=texts, values=values, first_row=row)
# row = row + len(ts_elements) + 1
# # Update button for the time-series-sheet
# variable_btn = Button(shape_frame, text="Update", command= lambda: update_values(texts_input = texts, rows=len(ts_elements), input_elements=ts_elements, input_values=values))
# variable_btn.grid(column=3, row=row)
# row=row+1
#
#
# # BUSES PARAMETERS
# bus_header = Label(shape_frame, text= 'Bus Parameters',font=('Helvetica 10 bold'))
# bus_header.grid(column=0, row=row, sticky="W")
#
# bus_elements = {'row1':['electricity_excess_costs',     -0.10,'CU/kWh','float value'],
#                 'row2':['electricity_shortage_costs',   0.30,'CU/kWh','float value'],
#                 'row3':['heat_excess_costs',            0,'CU/kWh','float value'],
#                 'row4':['naturalgas_shortage_costs',    0.07,'CU/kWh','float value'],
#                 'row5':['pv_excess_costs',              -0.1,'CU/kWh','float value'],}
# bus_texts, bus_values = [], []
# # Creates Elements
# create_elements(sheet=shape_frame, elements=bus_elements, texts=bus_texts, values=bus_values, first_row=row)
# # Update button for the bus-sheet
# row = row + len(bus_elements)
# variable_btn = Button(shape_frame, text="Update", command= lambda: update_values(texts_input = bus_texts, rows=len(bus_elements), input_elements=bus_elements, input_values=bus_values))
# variable_btn.grid(column=3, row=row+len(bus_elements)+1)
# row = row + 10
#
# # Electricity Demand
# el_demand_header = Label(shape_frame, text= 'Residential Electricity Demand',font=('Helvetica 10 bold'))
# el_demand_header.grid(column=0, row=row, sticky="W")
# row + 1
#
# el_demand_elements = {
#     'residential_load_profile': ['load profile','h0','',"richardson, h0, g0, ..."],
#     'building_class': ['building class',11,' ',' '],
#     'wind_class': ['wind class',0,' ',' '],
#     'demand_single_family_building': ['Single Family Building Demand',{1: 2300, 2: 3000, 3: 3600, 4: 4000, 5: 5000},' ','dictionary'],
#     'demand_multi_family_building': ['Apartment in MFB Demand',{1: 1400, 2: 2000, 3: 2600, 4: 3000, 5: 3600},' ','dictionary']
# }
#
# el_demand_texts, el_demand_values = [], []
# # Creates Elements
# create_elements(sheet=shape_frame, elements=el_demand_elements, texts=el_demand_texts, values=el_demand_values, first_row=row)
#
# # Update button
# variable_btn = Button(shape_frame, text="Update", command= lambda: update_values(texts_input = el_demand_texts, rows=len(el_demand_elements), input_elements=el_demand_elements, input_values=el_demand_values))
# variable_btn.grid(column=3, row=row+len(el_demand_elements)+1)
# row = row + 2 + len(el_demand_elements)
#
# #Heat Demand
#
# # Electricity Demand
# he_demand_header = Label(shape_frame, text= 'Heat Demand',font=('Helvetica 10 bold'))
# he_demand_header.grid(column=0, row=row, sticky="W")
# row + 1
#
# he_demand_elements = {
#     'NFA_coefficient': ['NFA_coefficient',0.9,'',''],
#     # 'demand_residential_building1': ['residential heat demand',{1000: {1: 247, 2: 238, 3: 212, 7: 182, 13: 169}},'',''],
#     # 'demand_residential_building2':[' ',{1919: {1: 254, 2: 236, 3: 211, 7: 178, 13: 153}},'',''],
#     # 'demand_residential_building3':[' ',{1949: {1: 236, 2: 219, 3: 192, 7: 166, 13: 140}},'',''],
#     # 'demand_residential_building4':[' ',{1979: {1: 175, 2: 168, 3: 155, 7: 152, 13: 118}},'',''],
#     # 'demand_residential_building5':[' ',{1991: {1: 131, 2: 127, 3: 127, 7: 114, 13: 101}},'',''],
#     # 'demand_residential_building6':[' ',{2001: {1: 83, 2: 88, 3: 80, 7: 76, 13: 69}},'',''],
#     # 'demand_residential_building7':[' ',{2009: {1: 48, 2: 46, 3: 46, 7: 53, 13: 54}},'',''],
#     #                                 },'',''],
#     'residential_load_profile': ['Load Profile','efh','',''],
#     'building_class': ['building class',11,'',''],
#     'wind_class': ['wind_class',0,'',''],
# }
#
# he_demand_texts, he_demand_values = [], []
# # Creates Elements
# create_elements(sheet=shape_frame, elements=he_demand_elements, texts=he_demand_texts, values=he_demand_values, first_row=row)
#
# # Update button
# variable_btn = Button(shape_frame, text="Update", command= lambda: update_values(texts_input = he_demand_texts, rows=len(he_demand_elements), input_elements=he_demand_elements, input_values=he_demand_values))
# variable_btn.grid(column=3, row=row+len(he_demand_elements)+1)
# row = row + 2 + len(he_demand_elements)
#
# # Gas Heating Transformer
# gh_header = Label(shape_frame, text= 'Gas Heating Systems',font=('Helvetica 10 bold'))
# gh_header.grid(column=0, row=row, sticky="W")
# row + 1
#
# # Check Box
# gh_chk_state = BooleanVar()
# gh_chk_state.set(True) #set check state
# gh_chk = Checkbutton(shape_frame, text='Active', var=gh_chk_state)
# gh_chk.grid(column=1, row=row, sticky="w")
#
# gh_elements = {
#     'efficiency': ['Efficiency',0.85,'',''],
#     'variable_input_costs': ['Variable Input Costs',0,'',''],
#     'variable_output_costs': ['Variable Output Costs',0,'',''],
#     'variable_output_costs_2': ['Variable Output Costs 2',0,'',''],
#     'periodical_costs': ['Periodical Costs',0,'','']
# }
#
#
# gh_texts, gh_values = [], []
# # Creates Elements
# create_elements(sheet=shape_frame, elements=gh_elements, texts=gh_texts, values=gh_values, first_row=row)
#
# # Update button
# variable_btn = Button(shape_frame, text="Update", command= lambda: update_values(texts_input = gh_texts, rows=len(gh_elements), input_elements=gh_elements, input_values=gh_values))
# variable_btn.grid(column=3, row=row+len(gh_elements)+1)
# row = row + 2 + len(gh_elements)
#
#
# # PHOTOVOLTAICS FRAME
# pv_header = Label(shape_frame, text= 'Photovoltaik Systems',font=('Helvetica 10 bold'))
# pv_header.grid(column=0, row=row, sticky="W")
# row + 1
#
# # Check Box
# chk_state = BooleanVar()
# chk_state.set(True) #set check state
# chk = Checkbutton(shape_frame, text='Active', var=chk_state)
# chk.grid(column=1, row=row, sticky="w")
#
# pv_elements = {'pv_variable_costs':['pv_variable_costs',            0,'CU/kWh','float value'],
#                 'pv_periodical_costs':['pv_periodical_costs',       90,'CU/kWh','float value'],
#                 'pv_technology_database':['pv_technology_database', 'SandiaMod',' ','string'],
#                 'pv_inverter_database':['pv_inverter_database',     'sandiainverter',' ','string'],
#                 'pv_modul_model':['pv_modul_model',                 'Panasonic_VBHN235SA06B__2013_',' ','string'],
#                 'pv_inverter_model': ['pv_inverter_model',          'ABB__MICRO_0_25_I_OUTD_US_240__240V_', ' ', 'string'],
#                 'pv_albedo': ['pv_albedo',                          0.2, '°', 'float value'],
#                 'pv_altitude': ['pv_altitude',                      50.0, 'm', 'float value'],
#                 'pv_latitude': ['pv_latitude',                      50.0, '°', 'float value'],
#                 'pv_longitude': ['pv_longitude',                    7, '°', 'float value'],
#                 }
#
# pv_texts, pv_values = [], []
# # Creates Elements
# create_elements(sheet=shape_frame, elements=pv_elements, texts=pv_texts, values=pv_values, first_row=row)
#
# # Update button for the bus-sheet
# # row = row + len(pv_elements)
# variable_btn = Button(shape_frame, text="Update", command= lambda: update_values(texts_input = pv_texts, rows=len(pv_elements), input_elements=pv_elements, input_values=pv_values))
# variable_btn.grid(column=3, row=row+len(pv_elements)+1)
# row = row + 2 + len(pv_elements)
#
#
# # EXCHANGE OF ELECTRICITY
# eoe_header = Label(shape_frame, text= 'Exchange of Electricity',font=('Helvetica 10 bold'))
# eoe_header.grid(column=0, row=row, sticky="W")
# row + 1
#
# # Check Box
# eoe_chk_state = BooleanVar()
# eoe_chk_state.set(True) #set check state
# eoe_chk = Checkbutton(shape_frame, text='Active', var=eoe_chk_state)
# eoe_chk.grid(column=1, row=row, sticky="w")
#
# eoe_elements = {
#     'efficiency': ['network charges (electricity)',0.1438,'CU/kWh',''],
# }
#
#
# eoe_texts, eoe_values = [], []
# # Creates Elements
# create_elements(sheet=shape_frame, elements=eoe_elements, texts=eoe_texts, values=eoe_values, first_row=row)
#
# # Update button
# variable_btn = Button(shape_frame, text="Update", command= lambda: update_values(texts_input = eoe_texts, rows=len(eoe_elements), input_elements=eoe_elements, input_values=eoe_values))
# variable_btn.grid(column=3, row=row+len(eoe_elements)+1)
# row = row + 2 + len(eoe_elements)


#
#
#
#
#
#
#
#
# #
# # ###################
# # # TIME SYSTEM FRAME
# # ###################
# #
# # timesystem = ttk.Frame(tab_control)
# # tab_control.add(timesystem, text='Time System')
# #
# # # Headline
# # lbl1 = Label(timesystem, text= 'Time System',font=(20))
# #
# #
# #
# # # Row Elements summarized in a dictionary. The dictionary will be updated with the button functions. The dictionary can
# # # be used to pass values to the program.
# # elements = {'row1':['Start Date','2012-01-01 00:00:00','','yyyy-mm-dd hh:mm:ss'],
# #             'row2':['End Date','2012-12-30 23:00:00','','yyyy-mm-dd hh:mm:ss'],
# #             'row3':['Temporal Resolution','h','','e.g. h'],
# #             'row4':['Periods',8760,'',' '],}
# #
# # texts, values = [], []
# #
# # # Creates Elements
# # create_elements(sheet=timesystem, elements=elements, texts=texts, values=values)
# #
# # # Update button for the time-series-sheet
# # variable_btn = Button(timesystem, text="Update", command= lambda: update_values(texts_input = texts, rows=4, input_elements=elements, input_values=values))
# # variable_btn.grid(column=3, row=len(elements)+2)
#
# #
# # # BUSES FRAME
# # buses = ttk.Frame(tab_control)
# #
# # bus_elements = {'row1':['electricity_excess_costs',     -0.10,'CU/kWh','float value'],
# #                 'row2':['electricity_shortage_costs',   0.30,'CU/kWh','float value'],
# #                 'row3':['heat_excess_costs',            0,'CU/kWh','float value'],
# #                 'row4':['naturalgas_shortage_costs',    0.07,'CU/kWh','float value'],
# #                 'row5':['pv_excess_costs',              -0.1,'CU/kWh','float value'],}
# #
# # bus_texts = []
# # bus_values = []
# #
# # # Creates Elements
# # create_elements(sheet=buses, elements=bus_elements, texts=bus_texts, values=bus_values)
# #
# # # Update button for the time-series-sheet
# # variable_btn = Button(buses, text="Update", command= lambda: update_values(texts_input = bus_texts, rows=4, input_elements=bus_elements, input_values=bus_values))
# # variable_btn.grid(column=3, row=6)
#
# # PHOTOVOLTAICS FRAME
# pv = ttk.Frame(tab_control)
#
#
# pv_elements = {'pv_variable_costs':['pv_variable_costs',            0,'CU/kWh','float value'],
#                 'pv_periodical_costs':['pv_periodical_costs',       90,'CU/kWh','float value'],
#                 'pv_technology_database':['pv_technology_database', 'SandiaMod',' ','string'],
#                 'pv_inverter_database':['pv_inverter_database',     'sandiainverter',' ','string'],
#                 'pv_modul_model':['pv_modul_model',                 'Panasonic_VBHN235SA06B__2013_',' ','string'],
#                 'pv_inverter_model': ['pv_inverter_model',          'ABB__MICRO_0_25_I_OUTD_US_240__240V_', ' ', 'string'],
#                 'pv_albedo': ['pv_albedo',                          0.2, '°', 'float value'],
#                 'pv_altitude': ['pv_altitude',                      50.0, 'm', 'float value'],
#                 'pv_latitude': ['pv_latitude',                      50.0, '°', 'float value'],
#                 'pv_longitude': ['pv_longitude',                    7, '°', 'float value'],
#                 }
#
# # pv_elements = {for i in pv_parameters }
#
# # Headline
# pv_header = Label(pv, text= 'Photovoltaic Systems',font=(20))
# pv_header.grid(column=0, row=0)
#
# # Check Box
# chk_state = BooleanVar()
# chk_state.set(True) #set check state
# chk = Checkbutton(pv, text='Use Photovoltaics for Optimization', var=chk_state)
# chk.grid(column=0, row=1)
#
#
#
# pv_texts, pv_values = [], []
#
#
# # Creates Elements
# create_elements(sheet=pv, elements=pv_elements, texts=pv_texts, values=pv_values)
#
# # Update button for the time-series-sheet
# variable_btn = Button(pv, text="Update", command= lambda: update_values(texts_input = pv_texts, rows=len(pv_elements), input_elements=pv_elements, input_values=pv_values))
# variable_btn.grid(column=3, row=len(pv_elements)+2)


# tab_control.add(shape_frame, text='Shape-Converter')
# tab_control.add(buses, text='Buses')
# tab_control.add(timesystem, text='Time System')
# tab_control.add(pv, text='Photovoltaics')


window.mainloop()
