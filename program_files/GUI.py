
# -*- coding: utf-8 -*-
from datetime import datetime
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import subprocess
import os
from Spreadsheet_Energy_System_Model_Generator import sesmg_main
from Demo_Tool import demo_tool
from urban_district_upscaling import urban_district_upscaling_GUI



def create_elements(sheet, elements, texts, values, first_row):
    """ Creates a block of tk-inter elements. The elements are created from an input dictionary. The tk-inter output
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

    """

    element_keys = [i for i in elements.keys()]

    # Creates the row elements of the time-series-sheet
    for i in range(len(elements)):
        row = i + first_row + 1

        variable_name = Label(sheet, text=elements[element_keys[i]][0], font='Helvetica 10')
        variable_name.grid(column=0, row=row, sticky="W")

        variable_value = Label(sheet, text=str(elements[element_keys[i]][1]), font='Helvetica 10')
        values.append(variable_value)
        values[i].grid(column=1, row=row)

        variable_unit = Label(sheet, text=str(elements[element_keys[i]][2]), font='Helvetica 10')
        variable_unit.grid(column=2, row=row, sticky="W")

        variable_text = Entry(sheet, width=20, font='Helvetica 10')
        texts.append(variable_text)
        texts[i].grid(column=3, row=row)

        variable_format = Label(sheet, text=elements[element_keys[i]][3], font='Helvetica 10')
        variable_format.grid(column=4, row=row, sticky="W")


def create_main_frame_elements(elements, sheet, first_row, file_paths, frame):
    """ Creates a block of tk-inter elements. The elements are created from an input dictionary. The tk-inter output
       has the following structure:

       TEXT 1 | BUTTON | TEXT 2 |
       ...    | ...    | ...    |

       The block will have the number of lines that the input dictionary elements have. By pressing the "BUTTONS"
       stored functions will be executed.

       ---

       Input variables:

       sheet: sheet within the window, where the element block will be placed

       elements: dictionary containing elements wich will be shown within this tk-inter block.
       Structure of the dictionary has to be as follows:
            elements = {'rowname':['text 1', function to be executed, 'text 2'}

       frame: sheet within the window, where the element block will be placed

       file_paths: dictionary where the values of TEXT 2 can be saved. Required for later changes.

       first_row: top line of the window sheet where the block should be positioned.

       """
    element_keys = [i for i in elements.keys()]

    for i in range(len(elements)):
        row = i + first_row + 1

        label_name = Label(sheet, text=elements[element_keys[i]][0], font='Helvetica 10')
        label_name.grid(column=0, row=row, sticky="W")

        button = Button(frame, text=elements[element_keys[i]][2], command=elements[element_keys[i]][1])
        button.grid(column=3, row=row)

        label_comment = Label(sheet, text=elements[element_keys[i]][3], font='Helvetica 10')
        file_paths.append(label_comment)
        file_paths[i].grid(column=4, row=row, columnspan=7, sticky="W")


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
    """ opens a file dialog and sets the selected path for the variable "scenario_path" """

    path = filedialog.askopenfilename(filetypes=(("Spreadsheet Files", "*.xlsx"), ("all files", "*.*")))

    scenario_path.set(path)
    print(scenario_path.get())

    file_paths[0].configure(text=scenario_path.get())

def getSavePath():
    """ opens a file dialog and sets the selected path for the variable "save_path" """

    path = filedialog.askdirectory()
    save_path.set(path)

    save_paths[0].configure(text=save_path.get())

def show_graph():
    """ creates and shows a graph of the energy system given by a Spreadsheet
        - the created graphs are saved in /results/graphs"""
    import os
    from program_files import (create_energy_system,
                               create_graph)

    # DEFINES PATH OF INPUT DATA
    scenario_file = scenario_path.get()

    # DEFINES PATH OF OUTPUT DATA
    if sys.platform.startswith("win"):
        result_path = os.path.join(os.path.dirname(__file__) + '/results/graphs')
    elif sys.platform.startswith('darwin'):
        result_path = os.path.dirname(os.path.abspath(__file__))
        result_path = result_path + '/results/graphs'
    elif sys.platform.startswith("linux"):
        result_path = os.path.dirname(os.path.abspath(__file__))
        result_path = result_path + '/results/graphs'
        subprocess.call("chmod +x " + result_path, shell=True)

    # IMPORTS DATA FROM THE EXCEL FILE AND RETURNS IT AS DICTIONARY
    nodes_data = create_energy_system.import_scenario(filepath=scenario_file)

    # PRINTS A GRAPH OF THE ENERGY SYSTEM
    create_graph.create_graph(filepath=result_path,
                              nodes_data=nodes_data,
                              show=True, # TODO: to be replaced by variable
                              legend=False)



def execute_sesmg():
    """ 1. Creates the folder where the results will be saved
        2. Excecutes the optimization algorithm """
    if scenario_path.get() != "No scenario selected.":
        scenario_name = os.path.basename(scenario_path.get())
        save_path.set(str(os.path.join(save_path_directory.get())
                          + '/' + scenario_name[:-5]
                          + str(datetime.now().strftime(
                            '_%Y-%m-%d--%H-%M-%S'))))
        os.mkdir(save_path.get())

        timeseries_prep_param = [timeseries_algorithm.get(),
                                 timeseries_cluster.get(),
                                 timeseries_criterion.get(),
                                 timeseries_period.get(),
                                 0 if timeseries_season.get() == 'none' else timeseries_season.get()]

        sesmg_main(scenario_file=scenario_path.get(),
                   result_path=save_path.get(),
                   num_threads=1,
                   timeseries_prep = timeseries_prep_param, #time_prep.get(),
                   # timeseries_value = 1 if timeseries_entry.get() == 'aggregation quote' else timeseries_entry.get(),
                   graph=True if graph_state.get() == 1 else False,
                   results=True,
                   plotly=True,
                   solver=solver_select.get())
        show_results()
    else:
        print('Please select scenario first!')
        comments[2].configure(text='Please select scenario first!')


def get_pid():
    """ Returns the ID of the running process on Port 8050 """
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
            command = "netstat -aon| findstr :8050"
        elif sys.platform.startswith("darwin"):
            command = "lsof -i tcp:8050"
        elif sys.platform.startswith("linux"):
            command = "fuser -n tcp 8050"
        pids = subprocess.check_output(command, shell=True)
        pids = str(pids)
        pidslist = pids.split()
        if sys.platform.startswith("win"):
            pid = pidslist[5]
            pid = pid[:-4]
        elif sys.platform.startswith("darwin"):
            pid = pidslist[9]
        elif sys.platform.startswith("linux"):
            pid = pidslist[1]
        return pid
    else:
        return ''


def show_results():
    """ executes the external program, which executes a plotl.dash app for displaying interactive results."""
    if save_path.get() == '':
        raise SystemError('No optimization since the last restart'
                          ' please select a result folder!')

    # Determines the ID of a still running process on port 8050.
    pid = get_pid()
    # Checks if the ID is not an empty return (no process available)
    if pid != '':
        if sys.platform.startswith("win"):
            command = 'taskkill /F /PID ' + pid
        elif sys.platform.startswith("darwin"):
            command = 'kill ' + pid
        elif sys.platform.startswith("linux"):
            command = 'kill ' + pid
        # Kills the still running process on port 8050
        subprocess.call(command, shell=True)
    else:
        if sys.platform.startswith("win"):
            subprocess.call("start http://127.0.0.1:8050", shell=True)
        elif sys.platform.startswith("darwin"):
            subprocess.call("open http://127.0.0.1:8050", shell=True)
        elif sys.platform.startswith("linux"):
            subprocess.call("xdg-open http://127.0.0.1:8050", shell=True)

    # Starts the new Plotly Dash Server for Windows
    if sys.platform.startswith("win"):
        subprocess.call(
                "Scripts\python.exe" + " program_files/Interactive_Results.py "
                + 'r"' + save_path.get() + '"', timeout=10, shell=True)
    # Starts the new Plotly Dash Server for MACOS
    elif sys.platform.startswith("darwin"):
        IR_PATH = os.path.dirname(os.path.abspath(__file__))
        subprocess.call("python3 " + IR_PATH + "/Interactive_Results.py "
                        + str(save_path.get()), timeout=10, shell=True)
    elif sys.platform.startswith("linux"):
        IR_PATH = os.path.dirname(os.path.abspath(__file__))
        subprocess.call("python3 " + IR_PATH + "/Interactive_Results.py "
                        + str(save_path.get()), timeout=10, shell=True)

# Definition of the user interface
window = Tk()
window.title("SESMG - Spreadsheet Energy System Model Generator")
window.geometry('1200x1050')
tab_control = ttk.Notebook(window)
tab_control.pack(expand=1, fill='both')
tab_control.pressed_index = None
scenario_path = StringVar(window, str(os.path.join(os.path.dirname(__file__), 'scenario_v0.2.0.xlsx')))
save_path_directory = \
        StringVar(window, str(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')))
save_path = StringVar(window, '')
num_threads = 2

############
# MAIN FRAME
############
# Definition of the Main-Frames
# main_frame = ttk.Frame(tab_control)
main_frame = ttk.Frame(window)
tab_control.add(main_frame, text='Home')

# Headline
main_head1 = Label(main_frame, text='Modeling', font='Helvetica 10 bold')
main_head1.grid(column=0, row=0, sticky="w")

# Erstellung des ersten Element-Blocks
# [label, function to be executed, button label, comment]
selection_elements = {'row1': ['Select scenario file', getFolderPath, 'Change', scenario_path.get()]}
file_paths = []
create_main_frame_elements(elements=selection_elements, sheet=main_frame, first_row=1, file_paths=file_paths,
                           frame=main_frame)


## TimeSeries Prep Menu
row = 3

timeseries_algorithm_list = ["none",
                             "k_means",
                             "averaging",
                             "slicing n>=2",
                             "slicing n<2",
                             "downsampling n>=2",
                             "downsampling n<2",
                             "heuristic selection",
                             "random sampling"]

timeseries_cluster_values = list(range(1,365))

timeseries_cluster_criteria = ["temperature",
                               "dhi",
                               "el_demand_sum",
                               "heat_demand_sum",]

timeseries_cluster_periods = ["hours",
                              "days",
                              "weeks"]

timeseries_cluster_seasons = [4, 12]

column = 0
Label(main_frame, text='Timeseries Preparation', font='Helvetica 10').grid(column=column, row=row+1,
                                                   sticky="W")

column = 3
Label(main_frame, text='Algorithm', font='Helvetica 10').grid(column=column, row=row,sticky="n")
timeseries_algorithm = StringVar(main_frame)
timeseries_algorithm.set('none')
DMenu = OptionMenu(main_frame, timeseries_algorithm, *timeseries_algorithm_list)
DMenu.grid(column=column, row=row+1)

column = column + 1
Label(main_frame, text='Index', font='Helvetica 10').grid(column=column, row=row,sticky="n")
timeseries_cluster = StringVar(main_frame)
timeseries_cluster.set('none')
DMenu = OptionMenu(main_frame, timeseries_cluster, *timeseries_cluster_values)
DMenu.grid(column=column, row=row+1)

column = column + 1
Label(main_frame, text='Criterion', font='Helvetica 10').grid(column=column, row=row,sticky="n")
timeseries_criterion = StringVar(main_frame)
timeseries_criterion.set('none')
DMenu = OptionMenu(main_frame, timeseries_criterion, *timeseries_cluster_criteria)
DMenu.grid(column=column, row=row+1)

column = column + 1
Label(main_frame, text='Period', font='Helvetica 10').grid(column=column, row=row,sticky="n")
timeseries_period = StringVar(main_frame)
timeseries_period.set('none')
DMenu = OptionMenu(main_frame, timeseries_period, *timeseries_cluster_periods)
DMenu.grid(column=column, row=row+1)

column = column + 1
Label(main_frame, text='Season', font='Helvetica 10').grid(column=column, row=row,sticky="n")
timeseries_season = StringVar(main_frame)
timeseries_season.set('none')
DMenu = OptionMenu(main_frame, timeseries_season, *timeseries_cluster_seasons)
DMenu.grid(column=column, row=row+1)


############################

# Graph Checkbox
row = row + 2
Label(main_frame, text='Show Graph', font='Helvetica 10').grid(column=0, row=row,
                                                   sticky="W")
graph_state = IntVar()
graph_checkbox = Checkbutton(main_frame, variable=graph_state)
graph_checkbox.grid(column=3, row=row)

# Solver Selection
row = row + 1
solvers = [
    "cbc",
    "gurobi",
]
Label(main_frame, text='Optimization Solver', font='Helvetica 10').grid(column=0, row=row,
                                                   sticky="W")

solver_select = StringVar(main_frame)
solver_select.set('gurobi')
SolverMenu = OptionMenu(main_frame, solver_select, *solvers)
SolverMenu.grid(column=3, row=row)

# Headline 2
row = row + 1
main_head2 = Label(main_frame, text='Execution', font='Helvetica 10 bold')
main_head2.grid(column=0, row=row, sticky="w")

# ERstellung des zweiten Element-Blocks
row = row + 1
# [Label, function to be executed, name of the button, comment]
test = StringVar(window)
execution_elements = {'row2': ['Show Graph', show_graph, 'Execute', ''],
                      'row3': ['Optimize Model', execute_sesmg, 'Execute', test.get()],
                      'row4': ['Show Latest Results', show_results, 'Execute', ''],
                      # 'row7':['End Program',end_program,'End',' '],
                      }
comments = []

create_main_frame_elements(elements=execution_elements, 
                           sheet=main_frame, 
                           first_row=row,
                           file_paths=comments, 
                           frame=main_frame)

row = row + len(execution_elements)
main_head3 = Label(main_frame, text='Results',
                       font='Helvetica 10 bold')
row = row + 1
main_head3.grid(column=0, row=row, sticky="w")
analyzing_elements = {'row5': ['Select scenario result folder',
                               getSavePath, 'Change', save_path.get()],
                      'row6': ['Start Plotly', show_results, 'Execute', '']}
save_paths = []
create_main_frame_elements(elements=analyzing_elements, sheet=main_frame,
                           first_row=row,
                           file_paths=save_paths, frame=main_frame)

###################
# Upscaling Frame #
###################
upscaling_frame = ttk.Frame(window)
upscaling_frame1 = urban_district_upscaling_GUI.upscaling_frame_class(window, tab_control, upscaling_frame)

##############
# DEMO Frame #
##############
demo_frame = ttk.Frame(window)
demo_frame1 = demo_tool.demo_frame_class(window, tab_control, demo_frame)
# add picture
if sys.platform.startswith("win"):
    img = PhotoImage(
        file='program_files/Demo_Tool/v0.0.6_demo_scenario/DEMO_System.png')
else:
    img = PhotoImage(file=os.path.dirname(os.path.abspath(__file__))
                     + '/Demo_Tool/v0.0.6_demo_scenario/DEMO_System.png')
img = img.subsample(2, 2)
lab = Label(master=demo_frame,image=img)\
        .grid(column=0, columnspan=4, row=19, rowspan=40)

window.mainloop()
