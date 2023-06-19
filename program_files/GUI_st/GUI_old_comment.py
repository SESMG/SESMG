# -*- coding: utf-8 -*-
from datetime import datetime
from tkinter import *
from tkinter import ttk
import subprocess
import os
import csv
from program_files.preprocessing.Spreadsheet_Energy_System_Model_Generator \
    import \
    sesmg_main
from program_files.GUI_files.urban_district_upscaling_GUI \
    import UpscalingFrameClass
from program_files.GUI_files.MethodsGUI import MethodsGUI
import \
    program_files.postprocessing.merge_partial_results as merge_partial_results
import program_files.postprocessing.plotting as plotting
from program_files.preprocessing.create_energy_system import import_scenario


def get_pid():
    """ Returns the ID of the running process on Port 8050 """
    # TODO @JAN diese Methode war notwendig, um den alten plotly dash Prozess
    # über seine IP und seinen Port zu clearen, und anschließend einen neuen
    # zu starten. Ich denke die benötigen wir in der neuen Struktur nicht mehr
    import socket
    import errno
    import sys
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Checks if port 8050 can be reached
        s.bind(("127.0.0.1", 8050))
        # If Yes, the program continues in line 53
        closeProcess = False
    # If not, the ID of the running process is returned
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            closeProcess = True
        else:
            raise ValueError("closeProcess failure")
    s.close()
    if closeProcess:
        if sys.platform.startswith("win"):
            command = "netstat -aon| findstr :8050"
        elif sys.platform.startswith("darwin"):
            command = "lsof -i tcp:8050"
        elif sys.platform.startswith("linux"):
            command = "fuser -n tcp 8050"
        else:
            raise ValueError("unknown platform")
        # list of processes running on 8050
        p_ids_list = str(subprocess.check_output(command, shell=True)).split()
        if sys.platform.startswith("win"):
            pid = p_ids_list[5]
            pid = pid[:-4]
        elif sys.platform.startswith("darwin"):
            pid = p_ids_list[9]
        elif sys.platform.startswith("linux"):
            pid = p_ids_list[1]
        else:
            raise ValueError("unknown platform")
        return pid
    else:
        return ''


def save_settings(gui_variables: dict):
    """
        Method that stores the settings entered in the GUI in a csv file
        in program_files/technical_data.

        :param gui_variables: dictionary holding the settings chosen in
            GUI
        :type gui_variables: dict

    """
    # TODO @JAN diese Methode speichert bei einem gestarteten Lauf alle
    # in der GUI getroffenen Einstellungen in einer csv, die in der Ordner-
    # struktur des SESMGs abgelegt wird. Hier haben wir gestern besprochen,
    # dass dies vielleicht erst der zweite Schritt bei der Entwicklung der
    # GUI sein sollte.
    dict_to_save = {}
    # remove variable handling from tkinter
    for key, value in gui_variables.items():
        dict_to_save.update({key: value.get()})
    # store extracted variables to csv file
    with open('program_files/technical_data/gui_settings.csv', 'w',
              newline='') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in dict_to_save.items():
            writer.writerow([key, value])


def reload_settings(gui_variables: dict):
    """
        Method that loads the settings saved in the csv file and then
        embeds them in the GUI.

        :param gui_variables: dictionary holding the GUI settings
        :type gui_variables: dict
        :return: **gui_variables** (dict) - updated dictionary holding \
            GUI settings
    """
    # TODO @ JAN hier genau das Gegenteil, diese Methode lädt die GUI-
    # Einstellungen aus der csv zurück in die GUI
    with open(os.path.dirname(os.path.dirname(os.path.join(__file__)))
              + "/technical_data/" + 'gui_settings.csv') \
            as csv_file:
        reader = csv.reader(csv_file)
        dict_to_reload = dict(reader)
    for key, value in dict_to_reload.items():
        gui_variables[key].set(value)
    return gui_variables


class GUI(MethodsGUI):
    """
        This class is used to create the Graphical User Interface
        (GUI). In this context, it uses the methods of the
        superclass MethodsGUI.
    """
    frames = []
    gui_variables = {}
    
    @staticmethod
    def __get_cb_state(checkbox) -> bool:
        """
            removes tkinter variable handling

            :param checkbox: checkbox whose boolean is to be returned
            :type checkbox: tkinter.Variable
            :rtype: bool

        """
        # TODO @ JAN da wir uns von tkinter verabschieden wahrscheinlich
        # nicht mehr nötig, hab ich auch nur genutzt um den Code zu
        # veschlanken. Überprüft im wesentlichen ob in der Variable die
        # als Parameter übergeben wird 0 oder 1 drin steht und gibt je
        # nach dem dann True oder False zurück
        if checkbox.get() == 1:
            return True
        else:
            return False
    
    def show_graph(self):
        """
            creates and shows a graph of the energy system given by a
            Spreadsheet - the created graphs are saved in
            /results/graphs
        """
        import os
        from program_files.preprocessing import (create_energy_system,
                                                 create_graph)
        import sys
        # TODO @ JAN hier wird es etwas komplizierter, da diese Funktion
        # momentan aus einem mir noch nicht ganz verständlichen Grund nicht
        # läuft. Kannst du das vielleicht ans Ende schieben? Trotzdem will
        # ich kurz das vorgehen erklären.
        
        # DEFINES PATH OF INPUT DATA
        scenario_file = self.gui_variables["scenario_path"].get()
        
        # DEFINES PATH OF OUTPUT DATA
        # TODO @ JAN hier müssen wir aufgrund der unterschiedlichen Path
        # Variablen der Betriebssysteme unterscheiden und diese separat
        # definieren
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
        """
            1. Creates the folder where the results will be saved
            2. Executes the optimization algorithm
        """
        # TODO @ JAN das ist meiner Meinung nach erst einmal die wichtigste
        # Methode für die neue GUI. Hierin werden die in der GUI getroffenen
        # entscheidungen an den Optimierungs algorithmus übermittelt.
        
        # check rather a scenario path is set -> TODO gibt es überhaupt ein Inputfile
        if self.gui_variables["scenario_path"].get():
            # save the choices made in the GUI -> TODO s.o. speichert die GUI Einstellungen
            save_settings(self.gui_variables)
            
            # set the timeseries preparation arguments -> TODO
            #  das ist CKs Reich, hier wird die Wahl der Zeitreihenbeschneidung in die
            # festgelegten Datenstrukturen überführt
            timeseries_season = self.gui_variables["timeseries_season"].get()
            timeseries_prep_param = \
                [self.gui_variables["timeseries_algorithm"].get(),
                 self.gui_variables["timeseries_cluster"].get(),
                 self.gui_variables["timeseries_criterion"].get(),
                 self.gui_variables["timeseries_period"].get(),
                 0 if timeseries_season == 'none' else timeseries_season]
            # TODO die folgenden Zeilen sind für die Pareto Optimierung und
            # daher wahrscheinlich auch erstmal nicht nötig
            limits = self.gui_variables["limits_pareto"].get().split(",")
            print(limits)
            result_folders = {"1": []}
            # TODO hier wird durch eine Liste von Inputdateien iteriert. Das ermöglicht,
            # Quartiere in Teilbereiche zu unterteilen und diese nach und nach zu
            # optimieren. Vielleicht in der ersten Version auch noch nicht nötig?
            for scenario in self.gui_variables["scenario_path"].get().split(
                    "\n"):
                # set the save path
                scenario_name = os.path.basename(scenario)[:-5]
                # TODO Definition des Ordners, in dem die Ergebnisse des folgenden
                # Optimierungslaufes gespeichert werden.
                self.gui_variables["save_path"].set(
                        str(os.path.join(self.gui_variables[
                                             "save_path_directory"].get()) +
                            '/'
                            + scenario_name
                            + str(
                            datetime.now().strftime('_%Y-%m-%d--%H-%M-%S'))))
                # TODO das ist wieder für die automatische Paretooptimierung
                result_folders["1"].append(
                    self.gui_variables["save_path"].get())
                print(result_folders["1"])
                # create new folder in which the results will be stored -> TODO erstellt
                # den eigentlichen Ordner in dem die Ergebnisse abgespeichert werden
                os.mkdir(self.gui_variables["save_path"].get())
                
                # execute SESMG algorithm -> TODO hier haben wir dann den
                # Aufruf des SESMGs. Um hier kurz die Parameter zu erklären:
                # scenario_file -> Pfad zur Inputdatei als String
                # result_path -> Pfad zum Ergebnisordner als String
                # num_threads -> Anzahl der maximal durch den SESMG zu nutzenden Threads.
                #   Das wird zur Parallelisierung des Optimierungsprozesses genutzt.
                # timeseries_prep -> Attribute der Zeitreihenbeschneidung (s.o.)
                # graph -> Bool die festlegt, ob der Graph angezeigt wird oder nicht.
                # criterion_switch -> bool die festlegt, ob die Optimierungsgrößen im Szenario getauscht werden sollen
                # xlsx_results -> bool die festlegt, ob die Exceldateien für die Busse erstellt werden
                # console_results -> VORSICHT beinhaltet fehler, ist aber eine boolean, die festlegt,
                #   ob die Ergebnisaufbereitung in der Konsole ausgegeben wird
                # solver -> String: Name des solvers erklärt sich denke ich von selbst
                # district_heating_path -> bin ich mir unschlüssig ob es langfristig weiter besteht. ist jedoch die
                #   Möglichkeit bereits berechnete Anschlusspunktsuchen wieder zu verwenden.
                #   Gibt den Pfad zu der bereits durchgeführten Suche an (Ordner).
                # cluster -> boolean die festlegt ob das wärmenetz nach straßen geclustert werden soll.
                sesmg_main(
                        scenario_file=scenario,
                        result_path=self.gui_variables["save_path"].get(),
                        num_threads=self.gui_variables["num_threads"].get(),
                        timeseries_prep=timeseries_prep_param,
                        graph=self.__get_cb_state(
                                self.gui_variables["graph_state"]),
                        criterion_switch=self.__get_cb_state(
                                self.gui_variables["criterion_state"]),
                        xlsx_results=self.__get_cb_state(
                                self.gui_variables["xlsx_select_state"]),
                        console_results=self.__get_cb_state(
                                self.gui_variables["console_select_state"]),
                        solver=self.gui_variables["solver_select"].get(),
                        district_heating_path=self.gui_variables[
                            "dh_path"].get(),
                        cluster_dh=self.gui_variables["cluster_dh"].get())
            # TODO auch hier sind wir wieder bei der Paretooptimierung bleibt also erst einmal raus
            if len(limits) > 1 or limits[0] != "":
                print("100% scenarios finished")
                constraints = merge_partial_results.get_constraints(
                    result_folders)
                files, path = \
                    merge_partial_results.create_transformation_scenarios(
                            constraints,
                            self.gui_variables["scenario_path"].get().split(
                                "\n"),
                            result_folders, limits)
                result_folders = \
                    merge_partial_results.run_pareto(
                            limits, files, self.gui_variables,
                            timeseries_prep_param, path, result_folders)
                # TODO merge components or not
                dfs = merge_partial_results.merge_component_csvs(
                        limits, files, path, result_folders)
                plotting.create_pareto_plot(dfs.values(), path)
                plotting.create_energy_amount_plot_elec(
                        dfs, path, import_scenario(scenario), self, tab_control)
            # start algorithm for creation of plotly dash -> TODO hier wurde der plotly aufgerufen,
            #   sofern die bool in der GUI das vorgesehen hat.
            if self.gui_variables["plotly_select_state"].get() == 1:
                self.show_results()
        
        else: # -> wird erreicht, wenn keine Inputdatei vorhanden ist.
            print('Please select scenario first!')
            self.gui_variables["scenario_path"].set(
                    'Please select scenario first!')
            self.update_idletasks()
    
    def show_results(self):
        """
            executes the external program, which executes a plotl.
            dash app for displaying interactive results.
        """
        import sys
        if self.gui_variables["save_path"].get() == '':
            raise SystemError('No optimization since the last restart'
                              ' please select a result folder!')
        # TODO 317 - 338 killen den alten plotly Prozess und öffnen einen neuen, daher nicht nötig.
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
        
        # Starts the new Plotly Dash Server for Windows -> TODO hier wird die Datei
        #   aufgerufen, die die Struktur des plotlys definiert hat.
        #   Wahrscheinlich so dann auch nicht mehr notwendig müssen wir mal überlegen
        if sys.platform.startswith("win"):
            subprocess.call(r"Scripts\python.exe"
                            + " program_files/postprocessing/Interactive_Results.py "
                            + 'r"' + self.gui_variables["save_path"].get()
                            + '"', timeout=10, shell=True)
        # Starts the new Plotly Dash Server for MACOS
        elif sys.platform.startswith("darwin"):
            ir_path = os.path.dirname(os.path.abspath(__file__))
            subprocess.call("python3.9 " + os.path.dirname(
                ir_path) + "/postprocessing/Interactive_Results.py "
                            + str(self.gui_variables["save_path"].get()),
                            timeout=10, shell=True)
        # Starts the new Plotly Dash Server for Linux
        elif sys.platform.startswith("linux"):
            ir_path = os.path.dirname(os.path.abspath(__file__))
            subprocess.call("python3 " + os.path.dirname(
                ir_path) + "/postprocessing/Interactive_Results.py "
                            + str(self.gui_variables["save_path"].get()),
                            timeout=10, shell=True)
    
    def __init__(self):
        # initialize super class to create an empty tk frame
        super().__init__(
                "SESMG - Spreadsheet Energy System Model Generator",
                "0.x",
                "1200x1050")
        global tab_control
        # TODO ganz viel TKinterkram
        tab_control = ttk.Notebook(self)
        tab_control.pack(expand=1, fill='both')
        tab_control.pressed_index = None
        # Home frame
        self.frames.append(ttk.Frame(self))
        tab_control.add(self.frames[-1], text="Home")
        # Upscaling frame
        self.frames.append(ttk.Frame(self))
        tab_control.add(self.frames[-1], text="Upscaling Tool")
        
        # variables -> TODO das sind alle Variablen, die wir bis jetzt in der GUI hatten,
        #   die meisten habe ich oben schon erläutert. Sollten welche nicht verständlich
        #   sein meld dich.
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
            "cluster_dh": IntVar(),
            "limits_pareto": StringVar(self.frames[0], ''),
            # upscaling tool variables
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
            "clustering_dh": BooleanVar(False),
            "components_path": StringVar()
        }
        # TODO hier wieder laden bzw. speichern der Einstellungen
        # reload the stored variables from technical_data/gui_settings
        self.gui_variables = reload_settings(self.gui_variables)
        
        # TODO jetzt beginnt der Aufbau der GUI bei Fragen sag bescheid ich
        #   suche jetzt die wichtigsten Stellen raus.
        # Headline
        self.create_heading(self.frames[0], 'Modeling', 0, 0, "w", True)
        # Scenario selection line
        self.create_button_lines(
                self.frames[0],
                {'Select scenario file':
                     [lambda: self.get_path("xlsx",
                                            self.gui_variables[
                                                "scenario_path"]),
                      'Change', 'scenario_path']}, 1, self.gui_variables)
        
        # TimeSeries Prep Menu
        timeseries_algorithm_list = \
            ["none", "k_means", "k_medoids", "averaging", "slicing A",
             "slicing B", "downsampling A", "downsampling B",
             "heuristic selection", "random sampling"]
        
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
            'Switch Criteria': "criterion_state"}
        row += 1
        row = self.create_cb_lines(self.frames[0], checkboxes_parameters, row,
                                   self.gui_variables) + 1
        
        # Solver Selection
        self.create_heading(self.frames[0], 'Optimization Solver', 0, row, "w")
        self.create_option_menu(self.frames[0],
                                self.gui_variables["solver_select"],
                                ["cbc", "gurobi"], 1, row)
        row += 1
        self.create_heading(self.frames[0], 'Pareto limits', 0, row, "w")
        self.create_entry(self.frames[0], row,
                          self.gui_variables["limits_pareto"])
        
        row += 1
        # result checkboxes
        self.create_heading(self.frames[0], 'Result processing parameters',
                            0, row, "w", True)
        checkboxes_parameters = {
            'Create xlsx-files': "xlsx_select_state",
            'Create console-log': "console_select_state",
            'Create plotly-dash': "plotly_select_state",
            'Clustering DH': "cluster_dh"}
        row = self.create_cb_lines(self.frames[0], checkboxes_parameters, row,
                                   self.gui_variables) + 1
        
        self.create_heading(self.frames[0], 'Execution', 0, row, "w", True)
        # execution buttons
        row += 1
        
        # TODO hier wird den Buttons ihr OnClick event hinterlegt
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
                                       self.gui_variables) + 1
        self.create_heading(self.frames[0], 'Results', 0, row, "w", True)
        row += 1
        # TODO hier haben wir noch das erneute betrachten alter Ergebnisse
        analyzing_elements = \
            {'Select scenario result folder':
                 [lambda: self.get_path("folder",
                                        self.gui_variables["save_path"]),
                  'Change', "save_path"],
             'Start Plotly': [self.show_results, 'Execute', '']}
        self.create_button_lines(self.frames[0], analyzing_elements, row,
                                 self.gui_variables)
        
        # TODO hier laden wir das Upscalingframe dazu.
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
