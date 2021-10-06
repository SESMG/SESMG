# -*- coding: utf-8 -*-
from datetime import datetime
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import subprocess
import os
import csv
from program_files.Spreadsheet_Energy_System_Model_Generator import sesmg_main
from program_files.Demo_Tool import demo_tool
from program_files.urban_district_upscaling import urban_district_upscaling_GUI


def create_elements(sheet, elements, texts, values, first_row):
    """
        Creates a block of tk-inter elements. The elements are created
        from an input dictionary. The tk-inter output
        has the following structure:
    
        TEXT 1 | TEXT 2 | TEXT 3 | INPUT FIELD   | TEXT 4
        ...    | ...    | ...    | ...           | ...
               |        |        | UPDATE BUTTON |
    
        The block will have the number of lines that the input
        dictionary elements have. By pressing the "UPDATE BUTTON"
        the value "TEXT 2" will be replaced with the input given with
        the input field.
    
        ---
    
        Input variables:
    
        sheet: sheet within the window, where the element block will be
        placed
    
        elements: dictionary containing elements wich will be shown
        within this tk-inter block. Structure of the dictionary
            has to be as follows: elements =
            {'rowname':['text 1', 'text 2', 'text 3', 'text 4']}
    
        texts: list, where the elements of column 3 (TEXT 4) will be
        saved. Required for data updates.
    
        values: list, where the elements of column 1 (TEXT 2) will be
        saved. Required for data updates.
    
        first_row: top line of the window sheet where the block should
        be positioned.

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
    """
        opens a file dialog and sets the selected path for the variable
        "scenario_path"
    """

    path = filedialog.askopenfilename(
            filetypes=(("Spreadsheet Files", "*.xlsx"), ("all files", "*.*")))

    gui_variables["scenario_path"].set(path)
    print(gui_variables["scenario_path"].get())

    file_paths[0].configure(text=gui_variables["scenario_path"].get())


def getSavePath():
    """
        opens a file dialog and sets the selected path for the variable
        "save_path"
    """

    path = filedialog.askdirectory()
    gui_variables["save_path"].set(path)

    save_paths[0].configure(text=gui_variables["save_path"].get())


def getDHPath():
    """
            opens a file dialog and sets the selected path for the variable
            "dh_path"
        """
    
    path = filedialog.askdirectory()
    gui_variables["dh_path"].set(path)
    
    comments[1].configure(text=gui_variables["dh_path"].get())


def show_graph():
    """ creates and shows a graph of the energy system given by a Spreadsheet
        - the created graphs are saved in /results/graphs"""
    import os
    from program_files import (create_energy_system,
                               create_graph)

    # DEFINES PATH OF INPUT DATA
    scenario_file = gui_variables["scenario_path"].get()

    # DEFINES PATH OF OUTPUT DATA
    if sys.platform.startswith("win"):
        result_path = os.path.join(os.path.dirname(__file__)
                                   + '/results/graphs')
    elif sys.platform.startswith('darwin'):
        result_path = os.path.dirname(os.path.abspath(__file__))
        result_path = result_path + '/results/graphs'
    elif sys.platform.startswith("linux"):
        result_path = os.path.dirname(os.path.abspath(__file__))
        result_path = result_path + '/results/graphs'
        subprocess.call("chmod +x " + result_path, shell=True)
    else:
        raise ValueError("unsupported operating system")

    # IMPORTS DATA FROM THE EXCEL FILE AND RETURNS IT AS DICTIONARY
    nodes_data = create_energy_system.import_scenario(filepath=scenario_file)

    # PRINTS A GRAPH OF THE ENERGY SYSTEM
    create_graph.create_graph(filepath=result_path,
                              nodes_data=nodes_data,
                              show=gui_variables["graph_state"],
                              legend=False)


def save_settings():
    dict_to_save = {}
    for key, value in gui_variables.items():
        dict_to_save.update({key: value.get()})
    with open('program_files/technical_data/gui_settings.csv', 'w',
              newline='') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in dict_to_save.items():
            writer.writerow([key, value])

            
def reload_settings():
    with open(os.path.dirname(os.path.join(__file__)) + "/technical_data/"
              + 'gui_settings.csv') \
            as csv_file:
        reader = csv.reader(csv_file)
        dict_to_reload = dict(reader)
    for key, value in dict_to_reload.items():
        gui_variables[key].set(value)


def execute_sesmg():
    """ 1. Creates the folder where the results will be saved
        2. Excecutes the optimization algorithm """
    if gui_variables["scenario_path"].get():
        # save the choices made in the GUI
        save_settings()
                
        scenario_name = os.path.basename(gui_variables["scenario_path"].get())
        gui_variables["save_path"].set(
                str(os.path.join(gui_variables["save_path_directory"].get())
                    + '/' + scenario_name[:-5]
                    + str(datetime.now().strftime('_%Y-%m-%d--%H-%M-%S'))))
        os.mkdir(gui_variables["save_path"].get())

        timeseries_season = gui_variables["timeseries_season"].get()
        timeseries_prep_param = [gui_variables["timeseries_algorithm"].get(),
                                 gui_variables["timeseries_cluster"].get(),
                                 gui_variables["timeseries_criterion"].get(),
                                 gui_variables["timeseries_period"].get(),
                                 0 if timeseries_season == 'none'
                                 else timeseries_season]

        sesmg_main(scenario_file=gui_variables["scenario_path"].get(),
                   result_path=gui_variables["save_path"].get(),
                   num_threads=gui_variables["num_threads"].get(),
                   timeseries_prep=timeseries_prep_param,
                   # time_prep.get(),
                   # timeseries_value = 1
                   # if timeseries_entry.get() == 'aggregation quote'
                   # else timeseries_entry.get(),
                   graph=True if gui_variables["graph_state"].get() == 1
                   else False,
                   criterion_switch=True if
                   gui_variables["criterion_state"].get() == 1 else False,
                   xlsx_results=True if
                   gui_variables["xlsx_select_state"].get() == 1 else False,
                   console_results=True if
                   gui_variables["console_select_state"].get() == 1 else False,
                   solver=gui_variables["solver_select"].get(),
                   district_heating_path=gui_variables["dh_path"].get(),
                   save_dh_calculations=gui_variables["save_dh_state"].get())
        if gui_variables["plotly_select_state"].get() == 1:
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
    """
        executes the external program, which executes a plotl.
        dash app for displaying interactive results.
    """
    if gui_variables["save_path"].get() == '':
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
        subprocess.call("Scripts\python.exe"
                        + " program_files/Interactive_Results.py "
                        + 'r"' + gui_variables["save_path"].get() + '"',
                        timeout=10, shell=True)
    # Starts the new Plotly Dash Server for MACOS
    elif sys.platform.startswith("darwin"):
        IR_PATH = os.path.dirname(os.path.abspath(__file__))
        subprocess.call("python3 " + IR_PATH + "/Interactive_Results.py "
                        + str(gui_variables["save_path"].get()),
                        timeout=10, shell=True)
    elif sys.platform.startswith("linux"):
        IR_PATH = os.path.dirname(os.path.abspath(__file__))
        subprocess.call("python3 " + IR_PATH + "/Interactive_Results.py "
                        + str(gui_variables["save_path"].get()),
                        timeout=10, shell=True)


def create_heading(frame, text, column, row, sticky, bold=False):
    if bold:
        font = 'Helvetica 10 bold'
    else:
        font = 'Helvetica 10'
    Label(frame, text=text, font=font)\
        .grid(column=column, row=row, sticky=sticky)


def create_option_menu(frame, variable, options, column, row):
    DMenu = OptionMenu(frame, variable, *options)
    DMenu.grid(column=column, row=row)
    
    
def create_checkbox(frame, variable, column, row):
    checkbox = Checkbutton(frame, variable=variable)
    checkbox.grid(column=column, row=row)


############
# MAIN FRAME
############
window = Tk()
window.title("SESMG - Spreadsheet Energy System Model Generator")
window.geometry('1200x1050')
tab_control = ttk.Notebook(window)
tab_control.pack(expand=1, fill='both')
tab_control.pressed_index = None

gui_variables = {
    "scenario_path": StringVar(window, 'scenario_v0.2.0.xlsx'),
    "save_path_directory": StringVar(window,
                                     str(os.path.join(
                                             os.path.dirname(
                                                     os.path.dirname(__file__)
                                             ), 'results'))),
    "save_path": StringVar(window, ''),
    "num_threads": IntVar(window, 2),
    "timeseries_algorithm": StringVar(window, 'none'),
    "timeseries_cluster": StringVar(window, 'none'),
    "timeseries_criterion": StringVar(window, 'none'),
    "timeseries_period": StringVar(window, 'none'),
    "timeseries_season": StringVar(window, 'none'),
    "graph_state": IntVar(),
    "criterion_state": IntVar(),
    "solver_select": StringVar(window, 'gurobi'),
    "xlsx_select_state": IntVar(),
    "console_select_state": IntVar(),
    "plotly_select_state": IntVar(),
    "dh_path": StringVar(window, ''),
    "save_dh_state": IntVar()
}

reload_settings()

main_frame = ttk.Frame(window)
tab_control.add(main_frame, text='Home')

# Headline
create_heading(main_frame, 'Modeling', 0, 0, "w", True)

# Erstellung des ersten Element-Blocks
# [label, function to be executed, button label, comment]
selection_elements = {'row1': ['Select scenario file', getFolderPath, 'Change',
                               gui_variables['scenario_path'].get()]}
file_paths = []
create_main_frame_elements(elements=selection_elements,
                           sheet=main_frame,
                           first_row=1,
                           file_paths=file_paths,
                           frame=main_frame)

# TimeSeries Prep Menu
row = 3
timeseries_algorithm_list = ["none", "k_means", "averaging", "slicing A",
                             "slicing B", "downsampling A", "downsampling B",
                             "heuristic selection", "random sampling"]

timeseries_cluster_criteria = ["temperature", "dhi", "el_demand_sum",
                               "heat_demand_sum"]


create_heading(main_frame, 'Timeseries Preparation', 0, row + 1, "w")
column = 3
create_heading(main_frame, 'Algorithm', column, row, "n")
create_option_menu(main_frame, gui_variables['timeseries_algorithm'],
                   timeseries_algorithm_list, column, row + 1)
column += 1

create_heading(main_frame, 'Index', column, row, "n")
create_option_menu(main_frame, gui_variables["timeseries_cluster"],
                   list(range(1, 365)), column, row + 1)
column += 1

create_heading(main_frame, 'Criterion', column, row, "n")
create_option_menu(main_frame, gui_variables["timeseries_criterion"],
                   timeseries_cluster_criteria, column, row + 1)

column += 1

create_heading(main_frame, 'Period', column, row, "n")
create_option_menu(main_frame, gui_variables["timeseries_period"],
                   ["hours", "days", "weeks"], column, row + 1)
column += 1

create_heading(main_frame, 'Season', column, row, "n")
create_option_menu(main_frame, gui_variables["timeseries_season"],
                   [4, 12], column, row + 1)


############################

# Graph Checkbox
row += 2
create_heading(main_frame, 'Show Graph', 0, row, "w")
create_checkbox(main_frame, gui_variables["graph_state"], 3, row)

# Criterion Switch Checkbox
row += 1
create_heading(main_frame, 'Switch Criteria', 0, row, "w")
create_checkbox(main_frame, gui_variables["criterion_state"], 3, row)

# Save Calculations of dh system for decreasing runtime
row += 1
create_heading(main_frame, 'Save DH calculations', 0, row, "w")
create_checkbox(main_frame, gui_variables["save_dh_state"], 3, row)

# Solver Selection
row += 1
create_heading(main_frame, 'Optimization Solver', 0, row, "w")
create_option_menu(main_frame, gui_variables["solver_select"],
                   ["cbc", "gurobi"], 3, row)

row += 1

# result checkboxes
create_heading(main_frame, 'Result processing parameters', 0, row, "w", True)

# xlsx_checkbox
row += 1
create_heading(main_frame, 'Create xlsx-files', 0, row, "w")
create_checkbox(main_frame, gui_variables["xlsx_select_state"], 3, row)

# console_checkbox
row += 1
create_heading(main_frame, 'Create console-log', 0, row, "w")
create_checkbox(main_frame, gui_variables["console_select_state"], 3, row)

# plotly_checkbox
row += 1
create_heading(main_frame, 'Create plotly-dash', 0, row, "w")
create_checkbox(main_frame, gui_variables["plotly_select_state"], 3, row)


# Headline 2
row += 1
create_heading(main_frame, 'Execution', 0, row, "w", True)

# execution buttons
row += 1

# [Label, function to be executed, name of the button, comment]
test = StringVar(window)

execution_elements = {
    'row2': ['Show Graph', show_graph, 'Execute', ''],
    'row3': ['Select DH calculations folder', getDHPath, 'Change',
             gui_variables["dh_path"].get()],
    'row4': ['Optimize Model', execute_sesmg, 'Execute', test.get()],
    'row5': ['Show Latest Results', show_results, 'Execute', '']
}
comments = []

create_main_frame_elements(elements=execution_elements, 
                           sheet=main_frame, 
                           first_row=row,
                           file_paths=comments, 
                           frame=main_frame)

row += (len(execution_elements) + 1)
create_heading(main_frame, 'Results', 0, row, "w", True)

analyzing_elements = {
    'row6': ['Select scenario result folder', getSavePath, 'Change',
             gui_variables["save_path"].get()],
    'row7': ['Start Plotly', show_results, 'Execute', '']}
save_paths = []
create_main_frame_elements(elements=analyzing_elements, sheet=main_frame,
                           first_row=row,
                           file_paths=save_paths, frame=main_frame)

###################
# Upscaling Frame #
###################
upscaling_frame = ttk.Frame(window)
upscaling_frame1 = \
    urban_district_upscaling_GUI.upscaling_frame_class(window,
                                                       tab_control,
                                                       upscaling_frame)

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
lab = Label(master=demo_frame, image=img)\
        .grid(column=0, columnspan=4, row=19, rowspan=40)

window.mainloop()
