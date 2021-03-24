import os
from tkinter import *
from tkinter import filedialog
from program_files.urban_district_upscaling import urban_district_upscaling

class upscaling_frame_class:
    def getFolderPath(self):
        """ opens a file dialog and sets the selected path for the variable "scenario_path" """

        path = filedialog.askopenfilename(
            filetypes=(("Spreadsheet Files", "*.xlsx"), ("all files", "*.*")))
        print(path)

        pre_scenario_path.set(path)
        print(pre_scenario_path.get())

        file_paths[0].configure(text=pre_scenario_path.get())

    def testcommand(self):
        print('No action executed. Will be added later.')



    def scenario_upscaling(self,pre_scenario,standard_param,scenario_name):
        # urban_district_upscaling
        urban_district_upscaling.urban_district_upscaling_tool(pre_scenario=pre_scenario,
                                                               standard_parameters=standard_param,
                                                               output_scenario=scenario_name,
                                                               plain_sheet=os.path.join(os.path.dirname(__file__), r'plain_scenario.xlsx'))


    def __init__(self, window, tab_control, upscaling_frame):
        def get_path(value):
            global path
            path = filedialog.askopenfilename(filetypes=(
            ("Spreadsheet Files", "*.xlsx"), ("all files", "*.*")))
            paths[value] = path
            print(path)
            print(paths)

            # standard_param_label.config(text=path)

            standard_param_text.set(path)



        # Definition of the Frame
        self.mainpath = \
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.window = window
        tab_control.add(upscaling_frame, text='Urban District Upscaling')


        # Paths
        paths = {'pre_scenario':os.path.join(os.path.dirname(__file__), r'pre_scenario.xlsx'),
                 'standard_param':os.path.join(os.path.dirname(__file__), r'standard_parameters.xlsx'),
                 'scenario_name':os.path.join(os.path.dirname(__file__), r'upscaled_scenario.xlsx')}

        # Headline
        row = 0
        Label(upscaling_frame,
              text='Urban District Upscaling',
              font='Helvetica 10 bold').grid(column=0,
                                             columnspan=7,
                                             row=row,
                                             sticky="W")

        # Description
        row = row + 1
        Label(upscaling_frame,
              text='Standardized implementation of urban energy systems',
              font='Helvetica 10').grid(column=0,
                                        columnspan=7,
                                        row=row,
                                        sticky="W")

        # Selection of the Pre-Scenario-File
        row = row + 1
        Label(upscaling_frame,
              text='Pre-Scenario',
              font='Helvetica 10').grid(column=0,
                                        row=row,
                                        sticky="W")
        Button(upscaling_frame,
               text="Placeholder",
               command=self.testcommand).grid(column=1,
                                        row=row,
                                        sticky="W")
        Label(upscaling_frame,
              text=paths['pre_scenario'],
              font='Helvetica 10').grid(column=2,
                                        row=row,
                                        sticky="W")

        # Selection of Standard-Parameter-File
        row = row + 1
        Label(upscaling_frame,
              text='Standard Parameters',
              font='Helvetica 10').grid(column=0,
                                        row=row,
                                        sticky="W")
        Button(upscaling_frame,
               text="Placeholder",
               command=self.testcommand).grid(column=1,
                                              row=row,
                                              sticky="W")
        Label(upscaling_frame,
              text=paths['standard_param'],
              font='Helvetica 10').grid(column=2,
                                        row=row,
                                        sticky="W")

        # Name zu erstellendes Scenario
        row = row + 1
        Label(upscaling_frame,
              text='Output File',
              font='Helvetica 10').grid(column=0,
                                        row=row,
                                        sticky="W")
        Button(upscaling_frame,
               text="Placeholder",
               command=self.testcommand).grid(column=1,
                                              row=row,
                                              sticky="W")
        Label(upscaling_frame,
              text=paths['scenario_name'],
              font='Helvetica 10').grid(column=2,
                                        row=row,
                                        sticky="W")

        # Create Scenario
        row = row + 1
        Label(upscaling_frame,
              text='Create Scenario',
              font='Helvetica 10').grid(column=0,
                                        row=row,
                                        sticky="W")
        Button(upscaling_frame,
               text="Execute",
               command=lambda: self.scenario_upscaling(pre_scenario=paths['pre_scenario'],
                                                       standard_param=paths['standard_param'],
                                                       scenario_name=paths['scenario_name'])
                                                       ).grid(column=1,
                                                              row=row)
