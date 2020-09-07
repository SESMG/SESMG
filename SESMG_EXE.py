# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import subprocess
import os
from program_files.Spreadsheet_Energy_System_Model_Generator import SESMG


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
    """ opens a file dialog and sets the selected path for the variable "scenario_path" """

    path = filedialog.askopenfilename(filetypes=(("Spreadsheet Files", "*.xlsx"), ("all files", "*.*")))
    print(path)

    scenario_path.set(path)
    print(scenario_path.get())

    file_paths[0].configure(text=scenario_path.get())


def show_graph():
    """ creates and shows a graph of the energy system given by a Spreadsheet"""
    import os
    from program_files import (create_energy_system,
                               create_graph)

    # DEFINES PATH OF INPUT DATA
    scenario_file = scenario_path.get()

    # DEFINES PATH OF OUTPUT DATA
    if sys.platform.startswith("win"):
        result_path = os.path.join(os.path.dirname(__file__) + '/results')
    elif sys.platform.startswith('darwin'):
        result_path = os.path.dirname(os.path.abspath(__file__))
        result_path = result_path + '/results'
    elif sys.platform.startswith("linux"):
        result_path = os.path.dirname(os.path.abspath(__file__))
        result_path = result_path + '/results'
        subprocess.call("chmod +x " + result_path, shell=True)

    # IMPORTS DATA FROM THE EXCEL FILE AND RETURNS IT AS DICTIONARY
    nodes_data = create_energy_system.import_scenario(filepath=scenario_file)

    # PRINTS A GRAPH OF THE ENERGY SYSTEM
    create_graph.create_graph(filepath=result_path,
                              nodes_data=nodes_data,
                              legend=False)


def execute_sesmg():
    """ Excecutes the optimization algorithm """
    if scenario_path.get() != "No scenario selected.":
        scenario_file = scenario_path.get()
        if sys.platform.startswith("win"):
            result_path = os.path.join(os.path.dirname(__file__) + '/results')
        elif sys.platform.startswith('darwin'):
            result_path = os.path.dirname(os.path.abspath(__file__))
            result_path = result_path + '/results'
        elif sys.platform.startswith("linux"):
            result_path = os.path.dirname(os.path.abspath(__file__))
            result_path = result_path + '/results'
            subprocess.call("chmod +x " + result_path, shell=True)
        SESMG(scenario_file=scenario_file, result_path=result_path)
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
        print(pidslist)
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
        IR_PATH = os.path.join(os.path.dirname(__file__) + '/program_files')
        subprocess.call(IR_PATH + "/Interactive_Results.py", timeout=10, shell=True)
    # Starts the new Plotly Dash Server for MACOS
    elif sys.platform.startswith("darwin"):
        IR_PATH = os.path.dirname(os.path.abspath(__file__))
        IR_PATH = IR_PATH + '/program_files'
        subprocess.call("python3 " + IR_PATH + "/Interactive_Results.py", timeout=10, shell=True)
    elif sys.platform.startswith("linux"):
        IR_PATH = os.path.dirname(os.path.abspath(__file__))
        IR_PATH = IR_PATH + '/program_files'
        subprocess.call("python3 " + IR_PATH + "/Interactive_Results.py", timeout=10, shell=True)


# def end_program():
#     ''' kills the entire application'''
#     app_pid = os.getpid()
#     os.kill(app_pid, 0)


# Definition of the user interface
window = Tk()
window.title("SESMG - Spreadsheet Energy System Model Generator")
window.geometry('1000x250')
tab_control = ttk.Notebook(window)
tab_control.pack(expand=1, fill='both')
tab_control.pressed_index = None
scenario_path = StringVar(window, str(os.path.join(os.path.dirname(__file__), 'scenario.xlsx')))

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
main_head2 = Label(main_frame, text='Execution Options', font='Helvetica 10 bold')
main_head2.grid(column=0, row=3 + len(selection_elements), sticky="w")

# ERstellung des zweiten Element-Blocks
# [Label, function to be executed, name of the button, comment]
test = StringVar(window)
execution_elements = {'row2': ['Show Graph', show_graph, 'Execute', ''],
                      'row3': ['Optimize Model', execute_sesmg, 'Execute', test.get()],
                      'row4': ['Show Latest Results', show_results, 'Execute', ''],
                      # 'row7':['End Program',end_program,'End',' '],
                      }
comments = []
create_main_frame_elements(elements=execution_elements, sheet=main_frame, first_row=3 + len(selection_elements),
                           file_paths=comments, frame=main_frame)


############
# DEMO FRAME
############


def monetary_demo_scenario():
    '''modifies financial demo scenario'''
    #windpower_capacity = entry_windpower.get()
    #print(windpower_capacity)
    print("Windpower: " + entry_windpower.get())
    print("Phtovoltaics: " + entry_photovoltaics.get())
    print("Battery: " + entry_battery.get())
    print("CHP: " + entry_chp.get())
    print("Thermal Storage: " + entry_thermalstorage.get())
    print("District Heating: " + entry_districtheating.get())

    import openpyxl
    xfile = openpyxl.load_workbook('demo_scenario_monetaer.xlsx')

    # WINDPOWER
    sheet = xfile["sources"]
    sheet['H2'] = (entry_windpower.get())
    sheet['I2'] = (entry_windpower.get())
    # PHOTOVOLTAICS
    sheet = xfile["sources"]
    sheet['H3'] = (int(entry_photovoltaics.get()))
    sheet['I3'] = (int(entry_photovoltaics.get()))
    # BATTERY
    sheet = xfile["storages"]
    sheet['F2'] = (int(entry_battery.get()))
    sheet['G2'] = (int(entry_battery.get()))
    # CHP
    sheet = xfile["transformers"]
    sheet['N3'] = (int(entry_chp.get()))
    sheet['O3'] = (int(entry_chp.get()))
    # THERMAL STORAGE
    sheet = xfile["storages"]
    sheet['F3'] = (int(entry_thermalstorage.get()))
    sheet['G3'] = (int(entry_thermalstorage.get()))
    # District Heating
    sheet = xfile["links"]
    sheet['C2'] = (int(entry_districtheating.get()))

    xfile.save('scenario.xlsx')
    execute_sesmg()

def emission_demo_scenario():
    '''modifies financial demo scenario'''
    #windpower_capacity = entry_windpower.get()
    #print(windpower_capacity)
    print("Windpower: " + entry_windpower.get())
    print("Phtovoltaics: " + entry_photovoltaics.get())
    print("Battery: " + entry_battery.get())
    print("CHP: " + entry_chp.get())
    print("Thermal Storage: " + entry_thermalstorage.get())
    print("District Heating: " + entry_districtheating.get())

    import openpyxl
    xfile = openpyxl.load_workbook('demo_scenario_emissionen.xlsx')

    # WINDPOWER
    sheet = xfile["sources"]
    sheet['H2'] = (entry_windpower.get())
    sheet['I2'] = (entry_windpower.get())
    # PHOTOVOLTAICS
    sheet = xfile["sources"]
    sheet['H3'] = (int(entry_photovoltaics.get()))
    sheet['I3'] = (int(entry_photovoltaics.get()))
    # BATTERY
    sheet = xfile["storages"]
    sheet['F2'] = (int(entry_battery.get()))
    sheet['G2'] = (int(entry_battery.get()))
    # CHP
    sheet = xfile["transformers"]
    sheet['N3'] = (int(entry_chp.get()))
    sheet['O3'] = (int(entry_chp.get()))
    # THERMAL STORAGE
    sheet = xfile["storages"]
    sheet['F3'] = (int(entry_thermalstorage.get()))
    sheet['G3'] = (int(entry_thermalstorage.get()))
    # District Heating
    sheet = xfile["links"]
    sheet['C2'] = (int(entry_districtheating.get()))

    xfile.save('scenario.xlsx')
    execute_sesmg()



# Definition of the DEMO-Frames
# main_frame = ttk.Frame(tab_control)
demo_frame = ttk.Frame(window)
tab_control.add(demo_frame, text='DEMO')

# WINDPOWER
row = 0
label_windpower = Label(demo_frame, text='Windpower', font=('Helvetica 10'))
label_windpower.grid(column=0, row=row, sticky="W")

entry_windpower = Entry(demo_frame)
entry_windpower.grid(column=1, row=row)

# PHOTOVOLTAICS
row = row+1
label_photovoltaics = Label(demo_frame, text='Photovoltaics', font=('Helvetica 10'))
label_photovoltaics.grid(column=0, row=row, sticky="W")

entry_photovoltaics = Entry(demo_frame)
entry_photovoltaics.grid(column=1, row=row)

# BATTERY
row = row+1
label_battery = Label(demo_frame, text='Battery', font=('Helvetica 10'))
label_battery.grid(column=0, row=row, sticky="W")

entry_battery = Entry(demo_frame)
entry_battery.grid(column=1, row=row)

# CHP
row = row+1
label_chp = Label(demo_frame, text='CHP', font=('Helvetica 10'))
label_chp.grid(column=0, row=row, sticky="W")

entry_chp = Entry(demo_frame)
entry_chp.grid(column=1, row=row)

# THERMAL STORAGE
row = row+1
label_thermalstorage = Label(demo_frame, text='Thermal Storage', font=('Helvetica 10'))
label_thermalstorage.grid(column=0, row=row, sticky="W")

entry_thermalstorage = Entry(demo_frame)
entry_thermalstorage.grid(column=1, row=row)

# District Heating
row = row+1
label_districtheating = Label(demo_frame, text='District Heating', font=('Helvetica 10'))
label_districtheating.grid(column=0, row=row, sticky="W")

entry_districtheating = Entry(demo_frame)
entry_districtheating.grid(column=1, row=row)


# EXECUTION BUTTONS
row = row + 1
Button(demo_frame, text='modify monetary scenario and execute', command=monetary_demo_scenario).grid(column=1, row=row, sticky=W, pady=4)
Button(demo_frame, text='modify emission scenario and execute', command=emission_demo_scenario).grid(column=1, row=row+1, sticky=W, pady=4)

window.mainloop()
