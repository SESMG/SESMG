import os
from tkinter import *
from tkinter import filedialog
from urban_district_upscaling.urban_district_upscaling \
    import urban_district_upscaling_tool
from urban_district_upscaling.urban_district_upscaling_post_processing \
    import urban_district_upscaling_post_processing


class upscaling_frame_class:

    #def getFolderPath(self):
    #    """ opens a file dialog and sets the selected path for the variable "scenario_path" """#

    #    path = filedialog.askopenfilename(
    #        filetypes=(("Spreadsheet Files", "*.xlsx"), ("all files", "*.*")))
    #    print(path)

    #    self.pre_scenario_path.set(path)
    #    print(pre_scenario_path.get())

    #    file_paths[0].configure(text=pre_scenario_path.get())

    #def testcommand(self):
    #    print('No action executed. Will be added later.')

    def getPreScenario(self):
        """
            opens a file dialog and sets the selected path for the
            variable "pre_scenario_path"
        """

        path = filedialog.askopenfilename(
            filetypes=(("Spreadsheet Files", "*.xlsx"), ("all files", "*.*")))
        self.pre_scenario_path.set(path)
        print(self.pre_scenario_path.get())
        self.paths['pre_scenario'] = (self.pre_scenario_path.get())
        self.pre_scenario_path_label.configure(
            text=self.pre_scenario_path.get())

    def getStandardParameters(self):
        """
            opens a file dialog and sets the selected path for the
            variable "standard_parameters_path"
        """

        path = filedialog.askopenfilename(
            filetypes=(("Spreadsheet Files", "*.xlsx"), ("all files", "*.*")))
        self.standard_parameters_path.set(path)

        self.paths['standard_parameters'] = \
            (self.standard_parameters_path.get())
        self.standard_parameters_path_label.configure(
            text=self.standard_parameters_path.get())

    def getComponentsCSV(self):
        """
            opens a file dialog and sets the selected path for the
            variable "components_path"
        """

        path = filedialog.askopenfilename(
            filetypes=(("Spreadsheet Files", "*.csv"), ("all files", "*.*")))
        self.components_path.set(path)

        self.paths['componentsCSV'] = (self.components_path.get())
        self.components_path_label.configure(text=self.components_path.get())

    def getScenarioName(self):
        """ opens a file dialog and sets the selected path for the variable "prescenario" """

        path = filedialog.askopenfilename(
            filetypes=(
            ("Spreadsheet Files", "*.xlsx"), ("all files", "*.*")))
        self.scenario_name.set(path)

        self.paths['scenario_name'] = (self.scenario_name.get())
        self.scenario_name_label.configure(text=self.scenario_name.get())

    def scenario_upscaling(self,pre_scenario,standard_param,scenario_name):
        # urban_district_upscaling
        urban_district_upscaling_tool(
            pre_scenario=pre_scenario,
            standard_parameter_path=standard_param,
            output_scenario=scenario_name,
            plain_sheet=os.path.join(os.path.dirname(__file__),
                                     r'plain_scenario.xlsx'))

    def create_overview(self, components, pre_scenario):
        urban_district_upscaling_post_processing(components, pre_scenario)


    def __init__(self, window, tab_control, upscaling_frame):

        #def get_path(value):
        #    global path
        #    path = filedialog.askopenfilename(filetypes=(
        #    ("Spreadsheet Files", "*.xlsx"), ("all files", "*.*")))
        #    paths[value] = path
        #    print(path)
        #    print(paths)

            # standard_param_label.config(text=path)

        #    standard_param_text.set(path)

        self.pre_scenario_path = \
            StringVar(window, os.path.join(os.path.dirname(__file__),
                                   r'pre_scenario.xlsx'))
        self.standard_parameters_path = \
            StringVar(window, os.path.join(os.path.dirname(__file__),
                                   r'standard_parameters.xlsx'))
        self.scenario_name = \
            StringVar(window, os.path.join(os.path.dirname(__file__),
                                   r'auto_generated_scenario.xlsx'))
        self.components_path = StringVar()
        # Definition of the Frame
        self.mainpath = \
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.window = window
        tab_control.add(upscaling_frame, text='Urban District Upscaling')

        # Paths
        self.paths = \
            {'pre_scenario': self.pre_scenario_path.get(),
             'standard_parameters': self.standard_parameters_path.get(),
             'scenario_name': self.scenario_name.get(),
             'componentsCSV': self.components_path.get()}
        # Headline
        row = 0
        Label(upscaling_frame,
              text='Urban District Upscaling',
              font='Helvetica 10 bold')\
            .grid(column=0, columnspan=7, row=row, sticky="W")

        # Description
        row = row + 1
        Label(upscaling_frame,
              text='Standardized implementation of urban energy systems',
              font='Helvetica 10')\
            .grid(column=0, columnspan=7, row=row, sticky="W")

        # Selection of the Pre-Scenario-File
        row = row + 1
        Label(upscaling_frame, text='Pre-Scenario', font='Helvetica 10')\
            .grid(column=0, row=row, sticky="W")
        Button(upscaling_frame, text="Change", command=self.getPreScenario)\
            .grid(column=1, row=row, sticky="W")
        self.pre_scenario_path_label = \
            Label(upscaling_frame, text=self.pre_scenario_path.get(),
                  font='Helvetica 10')
        self.pre_scenario_path_label.grid(column=2, row=row, sticky="W")

        # Selection of Standard-Parameter-File
        row = row + 1
        Label(upscaling_frame, text='Standard Parameters',
              font='Helvetica 10').grid(column=0, row=row, sticky="W")
        Button(upscaling_frame, text="Change",
               command=self.getStandardParameters)\
            .grid(column=1, row=row, sticky="W")
        self.standard_parameters_path_label = \
            Label(upscaling_frame, text=self.standard_parameters_path.get(),
                  font='Helvetica 10')
        self.standard_parameters_path_label.grid(column=2, row=row, sticky="W")

        # Name zu erstellendes Scenario
        row = row + 1
        Label(upscaling_frame, text='Scenario Name', font='Helvetica 10')\
            .grid(column=0, row=row, sticky="W")
        Button(upscaling_frame, text="Change", command=self.getScenarioName)\
            .grid(column=1, row=row, sticky="W")
        self.scenario_name_label = Label(upscaling_frame,
                                         text=self.scenario_name.get(),
                                         font='Helvetica 10')
        self.scenario_name_label.grid(column=2, row=row, sticky="W")

        # Create Scenario
        row = row + 1
        Label(upscaling_frame, text='Create Scenario', font='Helvetica 10')\
            .grid(column=0, row=row, sticky="W")
        Button(upscaling_frame, text="Execute",
               command=lambda: self.scenario_upscaling(
                   pre_scenario=self.paths['pre_scenario'],
                   standard_param=self.paths['standard_parameters'],
                   scenario_name=self.paths['scenario_name']))\
            .grid(column=1, row=row)
        # Path to components csv
        row = row + 1
        Label(upscaling_frame, text='Components CSV for post processing',
              font='Helvetica 10').grid(column=0, row=row, sticky="W")
        Button(upscaling_frame, text="Change", command=self.getComponentsCSV)\
            .grid(column=1, row=row, sticky="W")
        self.components_path_label = Label(upscaling_frame,
                                           text=self.components_path.get(),
                                           font='Helvetica 10')
        self.components_path_label.grid(column=2, row=row, sticky="W")

        # Create Post Scenario
        row = row + 1
        Label(upscaling_frame, text='Create Overview', font='Helvetica 10')\
            .grid(column=0, row=row, sticky="W")
        Button(upscaling_frame, text="Execute",
               command=lambda: self.create_overview(
                   components=self.paths['componentsCSV'],
                   pre_scenario=self.paths['pre_scenario']))\
            .grid(column=1, row=row)
