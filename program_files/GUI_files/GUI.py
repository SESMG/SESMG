# -*- coding: utf-8 -*-
from datetime import datetime
from tkinter import *
from tkinter import ttk
import subprocess
import os
import csv
from program_files.Spreadsheet_Energy_System_Model_Generator import sesmg_main
from program_files.GUI_files.urban_district_upscaling_GUI \
    import UpscalingFrameClass
from program_files.GUI_files.MethodsGUI import MethodsGUI


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
        else:
            raise ValueError("closeprocess failure")
    s.close()
    if closeprocess:
        if sys.platform.startswith("win"):
            command = "netstat -aon| findstr :8050"
        elif sys.platform.startswith("darwin"):
            command = "lsof -i tcp:8050"
        elif sys.platform.startswith("linux"):
            command = "fuser -n tcp 8050"
        else:
            raise ValueError("unknown platform")
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
        else:
            raise ValueError("unknown platform")
        return pid
    else:
        return ''


def save_settings(gui_variables):
    dict_to_save = {}
    for key, value in gui_variables.items():
        dict_to_save.update({key: value.get()})
    with open('program_files/technical_data/gui_settings.csv', 'w',
              newline='') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in dict_to_save.items():
            writer.writerow([key, value])


def reload_settings(gui_variables):
    with open(os.path.dirname(os.path.dirname(os.path.join(__file__)))
              + "/technical_data/" + 'gui_settings.csv') \
            as csv_file:
        reader = csv.reader(csv_file)
        dict_to_reload = dict(reader)
    for key, value in dict_to_reload.items():
        gui_variables[key].set(value)
    return gui_variables


def get_checkbox_state(checkbox):
    if checkbox.get() == 1:
        return True
    else:
        return False


class GUI(MethodsGUI):
    frames = []
    gui_variables = {}

    def show_graph(self):
        """ creates and shows a graph of the energy system given by a
        Spreadsheet
            - the created graphs are saved in /results/graphs"""
        import os
        from program_files import (create_energy_system,
                                   create_graph)
    
        # DEFINES PATH OF INPUT DATA
        scenario_file = self.gui_variables["scenario_path"].get()
    
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
        nodes_data = create_energy_system.import_scenario(
            filepath=scenario_file)
    
        # PRINTS A GRAPH OF THE ENERGY SYSTEM
        create_graph.create_graph(filepath=result_path,
                                  nodes_data=nodes_data,
                                  show=self.gui_variables["graph_state"],
                                  legend=False)

    def execute_sesmg(self):
        """ 1. Creates the folder where the results will be saved
            2. Excecutes the optimization algorithm """
        if self.gui_variables["scenario_path"].get():
            # save the choices made in the GUI
            save_settings(self.gui_variables)
        
            scenario_name = \
                os.path.basename(self.gui_variables["scenario_path"].get())
            self.gui_variables["save_path"].set(
                str(os.path.join(self.gui_variables[
                                     "save_path_directory"].get())
                    + '/' + scenario_name[:-5]
                    + str(datetime.now().strftime('_%Y-%m-%d--%H-%M-%S'))))
            os.mkdir(self.gui_variables["save_path"].get())
        
            timeseries_season = self.gui_variables["timeseries_season"].get()
            timeseries_prep_param = \
                [self.gui_variables["timeseries_algorithm"].get(),
                 self.gui_variables["timeseries_cluster"].get(),
                 self.gui_variables["timeseries_criterion"].get(),
                 self.gui_variables["timeseries_period"].get(),
                 0 if timeseries_season == 'none' else timeseries_season]
            sesmg_main(
                scenario_file=self.gui_variables["scenario_path"].get(),
                result_path=self.gui_variables["save_path"].get(),
                num_threads=self.gui_variables["num_threads"].get(),
                timeseries_prep=timeseries_prep_param,
                graph=get_checkbox_state(self.gui_variables["graph_state"]),
                criterion_switch=get_checkbox_state(
                    self.gui_variables["criterion_state"]),
                xlsx_results=get_checkbox_state(
                    self.gui_variables["xlsx_select_state"]),
                console_results=get_checkbox_state(
                    self.gui_variables["console_select_state"]),
                solver=self.gui_variables["solver_select"].get(),
                district_heating_path=self.gui_variables["dh_path"].get(),
                save_dh_calculations=self.gui_variables["save_dh_state"].get(),
                cluster_dh=self.gui_variables["cluster_dh"].get())
            if self.gui_variables["plotly_select_state"].get() == 1:
                self.show_results()
        else:
            print('Please select scenario first!')
            self.gui_variables["scenario_path"].set(
                    'Please select scenario first!')
            self.update_idletasks()
    
    def show_results(self):
        """
            executes the external program, which executes a plotl.
            dash app for displaying interactive results.
        """
        if self.gui_variables["save_path"].get() == '':
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
            else:
                raise ValueError("unknown platform")
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
            subprocess.call(r"Scripts\python.exe"
                            + " program_files/Interactive_Results.py "
                            + 'r"' + self.gui_variables["save_path"].get()
                            + '"',
                            timeout=10, shell=True)
        # Starts the new Plotly Dash Server for MACOS
        elif sys.platform.startswith("darwin"):
            ir_path = os.path.dirname(os.path.abspath(__file__))
            subprocess.call("python3 " + ir_path + "/Interactive_Results.py "
                            + str(self.gui_variables["save_path"].get()),
                            timeout=10, shell=True)
        elif sys.platform.startswith("linux"):
            ir_path = os.path.dirname(os.path.abspath(__file__))
            subprocess.call("python3 " + ir_path + "/Interactive_Results.py "
                            + str(self.gui_variables["save_path"].get()),
                            timeout=10, shell=True)
    
    def __init__(self):
        super().__init__(
                "SESMG - Spreadsheet Energy System Model Generator",
                "0.x",
                "1200x1050")
        tab_control = ttk.Notebook(self)
        tab_control.pack(expand=1, fill='both')
        tab_control.pressed_index = None
        # Home frame
        self.frames.append(ttk.Frame(self))
        tab_control.add(self.frames[-1], text="Home")
        # Upscaling frame
        self.frames.append(ttk.Frame(self))
        tab_control.add(self.frames[-1], text="Upscaling Tool")
        # variables
        self.gui_variables = {
            "scenario_path": StringVar(self.frames[0], 'scenario_v0.2.0.xlsx'),
            "save_path_directory":
                StringVar(self.frames[0],
                          str(os.path.join(
                                  os.path.dirname(os.path.dirname(__file__)),
                                  'results'))),
            "save_path": StringVar(self.frames[0], ''),
            "num_threads": IntVar(self.frames[0], 2),
            "timeseries_algorithm": StringVar(self.frames[0], 'none'),
            "timeseries_cluster": StringVar(self.frames[0], 'none'),
            "timeseries_criterion": StringVar(self.frames[0], 'none'),
            "timeseries_period": StringVar(self.frames[0], 'none'),
            "timeseries_season": StringVar(self.frames[0], 'none'),
            "graph_state": IntVar(),
            "criterion_state": IntVar(),
            "solver_select": StringVar(self.frames[0], 'gurobi'),
            "xlsx_select_state": IntVar(),
            "console_select_state": IntVar(),
            "plotly_select_state": IntVar(),
            "dh_path": StringVar(self.frames[0], ''),
            "save_dh_state": IntVar(),
            "cluster_dh": IntVar(),
            "pre_scenario_path":
                StringVar(self.frames[1],
                          os.path.join(os.path.dirname(__file__)
                                       + "/urban_district_upscaling/",
                                       r'pre_scenario.xlsx')),
            "standard_parameter_path":
                StringVar(self.frames[1],
                          os.path.join(os.path.dirname(__file__)
                                       + "/urban_district_upscaling/",
                                       r'standard_parameters.xlsx')),
            "scenario_name":
                StringVar(self.frames[1],
                          os.path.join(os.path.dirname(__file__)
                                       + "/urban_district_upscaling/",
                                       r'auto_generated_scenario.xlsx')),
            "clustering": BooleanVar(False),
            "components_path": StringVar()
        }
        
        self.gui_variables = reload_settings(self.gui_variables)
        
        # Headline
        self.create_heading(self.frames[0], 'Modeling', 0, 0, "w", True)
        
        self.create_heading(self.frames[0], 'Select scenario file', 0, 1, "w")
        self.create_button(frame=self.frames[0], text='Change',
                           command=lambda: self.get_path(
                               "xlsx", self.gui_variables["scenario_path"]),
                           column=1, row=1)
        self.create_heading(self.frames[0],
                            self.gui_variables["scenario_path"], 2, 1, "w",
                            columnspan=6)

        # TimeSeries Prep Menu
        timeseries_algorithm_list = \
            ["none", "k_means", "averaging", "slicing A", "slicing B",
             "downsampling A", "downsampling B", "heuristic selection",
             "random sampling"]
        
        timeseries_cluster_criteria = \
            ["temperature", "dhi", "el_demand_sum", "heat_demand_sum"]
        
        timeseries_parameters = {
            "Algortihm": ('timeseries_algorithm', timeseries_algorithm_list),
            "Index": ("timeseries_cluster", list(range(1, 365))),
            "Criterion": ("timeseries_criterion", timeseries_cluster_criteria),
            "Period": ("timeseries_period", ["hours", "days", "weeks"]),
            "Season": ("timeseries_season", [4, 12])}
        
        row = 4
        self.create_heading(self.frames[0], 'Timeseries Preparation', 0,
                            row, "w", rowspan=2)
        column = 3
        for param in timeseries_parameters:
            self.create_heading(self.frames[0], param, column, row, "n")
            self.create_option_menu(
                    self.frames[0],
                    self.gui_variables[timeseries_parameters[param][0]],
                    timeseries_parameters[param][1],
                    column, row + 1)
            column += 1
        
        checkboxes_parameters = {
            'Show Graph': "graph_state",
            'Switch Criteria': "criterion_state",
            'Save DH calculations': "save_dh_state"}
        row += 1
        for param in checkboxes_parameters:
            row += 1
            self.create_heading(self.frames[0], param, 0, row, "w")
            self.create_checkbox(
                    self.frames[0],
                    self.gui_variables[checkboxes_parameters[param]], 1, row)
        
        # Solver Selection
        row += 1
        self.create_heading(self.frames[0], 'Optimization Solver', 0, row, "w")
        self.create_option_menu(self.frames[0],
                                self.gui_variables["solver_select"],
                                ["cbc", "gurobi"], 1, row)
        
        row += 1
        # result checkboxes
        self.create_heading(self.frames[0], 'Result processing parameters',
                            0, row, "w", True)
        checkboxes_parameters = {
            'Create xlsx-files': "xlsx_select_state",
            'Create console-log': "console_select_state",
            'Create plotly-dash': "plotly_select_state",
            'Clustering DH': "cluster_dh"}
        for param in checkboxes_parameters:
            row += 1
            self.create_heading(self.frames[0], param, 0, row, "w")
            self.create_checkbox(
                    self.frames[0],
                    self.gui_variables[checkboxes_parameters[param]], 1, row)

        # Headline 2
        row += 1
        self.create_heading(self.frames[0], 'Execution', 0, row, "w", True)
        # execution buttons
        row += 1
        
        # [Label, function to be executed, name of the button, comment]
        execution_elements = {
            'Show Graph': [self.show_graph, 'Execute', ''],
            'Select DH calculations folder':
                [lambda: self.get_path("folder",
                                       self.gui_variables["dh_path"]),
                 'Change', "dh_path"],
            'Optimize Model': [self.execute_sesmg, 'Execute', ''],
            'Show Latest Results': [self.show_results, 'Execute', '']}
        row = self.create_button_lines(self.frames[0], execution_elements, row,
                                       self.gui_variables)
        row += 1
        self.create_heading(self.frames[0], 'Results', 0, row, "w", True)
        row += 1
        analyzing_elements = {
            'Select scenario result folder':
                [lambda: self.get_path("folder",
                                       self.gui_variables["save_path"]),
                 'Change', "save_path"],
            'Start Plotly': [self.show_results, 'Execute', '']}
        self.create_button_lines(self.frames[0], analyzing_elements, row,
                                 self.gui_variables)
        
        UpscalingFrameClass(self.frames[1], self.gui_variables, self)
        
        # ##############
        # # DEMO Frame #
        # ##############
        # demo_frame = ttk.Frame(window)
        # demo_frame1 = demo_tool.demo_frame_class(window, tab_control,
        # demo_frame)
        # # add picture
        # if sys.platform.startswith("win"):
        #     img = PhotoImage(
        #         file='program_files/Demo_Tool/v0.0.6_demo_scenario
        #         /DEMO_System.png')
        # else:
        #     img = PhotoImage(file=os.path.dirname(os.path.abspath(__file__))
        #                      + '/Demo_Tool/v0.0.6_demo_scenario
        #                      /DEMO_System.png')
        # img = img.subsample(2, 2)
        # lab = Label(master=demo_frame, image=img)\
        #         .grid(column=0, columnspan=4, row=19, rowspan=40)
        
        self.mainloop()
