from tkinter import *
import tkinter as ttk
import pandas as pd
import openpyxl
import matplotlib as mlp
import matplotlib.pyplot as plt
import numpy as np
from threading import *
import os
import subprocess
from program_files.Spreadsheet_Energy_System_Model_Generator import sesmg_main


class demo_frame_class:

    def execute_sesmg_DEMO(self, demo_file, demo_results):
        """ Excecutes the optimization algorithm """
        print(demo_file)
        print(demo_results)

        # if scenario_path.get() != "No scenario selected.":
        #    scenario_file = scenario_path.get()
        #if sys.platform.startswith("win"):
        #    result_path = os.path.join(os.path.dirname(__file__) + demo_results)
        #elif sys.platform.startswith('darwin'):
        #    result_path = os.path.dirname(os.path.abspath(__file__))
        #    result_path = result_path + demo_results
        #    demo_path = os.path.join(os.path.dirname(__file__) + demo_file)
        #elif sys.platform.startswith("linux"):
        #    result_path = os.path.dirname(os.path.abspath(__file__))
        #    result_path = result_path + demo_results
        #    subprocess.call("chmod +x " + result_path, shell=True)
        # scenario_file = 'scenario.xlsx'
        # SESMG_DEMO(scenario_file=scenario_file, result_path=result_path)
        sesmg_main(scenario_file=demo_file,
                   result_path=demo_results,
                   num_threads=2,
                   graph=False,
                   results=False,
                   plotly=True)
        # show_results()
        # else:
        #     print('Please select scenario first!')
        #     comments[2].configure(text='Please select scenario first!')

    def monetary_demo_scenario(self):
        '''modifies financial demo scenario'''

        xfile = openpyxl.load_workbook(os.path.dirname(__file__)
                        + '/v0.0.6_demo_scenario/demo_scenario_monetaer.xlsx',
                                       data_only=True)

        # WINDPOWER
        sheet = xfile["sources"]
        sheet['K2'] = (int(self.entry_values['windpower'].get()))
        sheet['L2'] = (int(self.entry_values['windpower'].get()))
        # PHOTOVOLTAICS
        sheet = xfile["sources"]
        sheet['K3'] = (int(self.entry_values['photovoltaics'].get()))
        sheet['L3'] = (int(self.entry_values['photovoltaics'].get()))
        # BATTERY
        sheet = xfile["storages"]
        sheet['G2'] = (int(self.entry_values['battery'].get()))
        sheet['H2'] = (int(self.entry_values['battery'].get()))
        # CHP
        sheet = xfile["transformers"]
        sheet['Q3'] = (int(self.entry_values['chp'].get()))
        sheet['R3'] = (int(self.entry_values['chp'].get()))
        # THERMAL STORAGE
        sheet = xfile["storages"]
        sheet['G3'] = (int(self.entry_values['thermal storage'].get()))
        sheet['H3'] = (int(self.entry_values['thermal storage'].get()))
        # District Heating
        sheet = xfile["links"]
        sheet['C2'] = (int(self.entry_values['district heating'].get()))

        xfile.save(self.mainpath + '/results/demo/financial/scenario.xlsx')
        self.execute_sesmg_DEMO(
            demo_file=self.mainpath + r"/results/demo/financial/scenario.xlsx",
            demo_results=self.mainpath + r"/results/demo/financial")

        df_summary = pd.read_csv(self.mainpath
                                 + r"/results/demo/financial/summary.csv")
        # monetary_costs = float(df_summary['Total System Costs'])
        self.monetary_costs.set(
            str(round(float(df_summary['Total System Costs']/1000000), 2)))
        self.emission_costs.set(
            str(round(float(df_summary['Total Constraint Costs'])/1000000, 0)))
        self.window.update_idletasks()

    def emission_demo_scenario(self):
        '''modifies financial demo scenario'''

        xfile = openpyxl.load_workbook(os.path.dirname(__file__) +
            '/v0.0.6_demo_scenario/demo_scenario_emissionen.xlsx')

        # WINDPOWER
        sheet = xfile["sources"]
        sheet['K2'] = (int(self.entry_values['windpower'].get()))
        sheet['L2'] = (int(self.entry_values['windpower'].get()))
        # PHOTOVOLTAICS
        sheet = xfile["sources"]
        sheet['K3'] = (int(self.entry_values['photovoltaics'].get()))
        sheet['L3'] = (int(self.entry_values['photovoltaics'].get()))
        # BATTERY
        sheet = xfile["storages"]
        sheet['G2'] = (int(self.entry_values['battery'].get()))
        sheet['H2'] = (int(self.entry_values['battery'].get()))
        # CHP
        sheet = xfile["transformers"]
        sheet['Q3'] = (int(self.entry_values['chp'].get()))
        sheet['R3'] = (int(self.entry_values['chp'].get()))
        # THERMAL STORAGE
        sheet = xfile["storages"]
        sheet['G3'] = (int(self.entry_values['thermal storage'].get()))
        sheet['H3'] = (int(self.entry_values['thermal storage'].get()))
        # District Heating
        sheet = xfile["links"]
        sheet['C2'] = (int(self.entry_values['district heating'].get()))

        xfile.save(self.mainpath + '/results/demo/emissions/scenario.xlsx')
        self.execute_sesmg_DEMO(
            demo_file=self.mainpath + '/results/demo/emissions/scenario.xlsx',
            demo_results=self.mainpath + '/results/demo/emissions')

        df_summary = pd.read_csv(self.mainpath
                                 + r"/results/demo/emissions/summary.csv")

        self.emission_costs.set(
            str(round(float(df_summary['Total System Costs'])/1000000, 0)))
        self.monetary_costs.set(
            str(round(float(df_summary['Total Constraint Costs'])/1000000, 0)))
        self.window.update_idletasks()

    def simulate_scenario(self):
        for i in range(len(self.entry_values)):
            print(self.demo_names[i] + ': '
                  + self.entry_values[self.demo_names[i]].get()
                  + ' ' + self.demo_unit[self.demo_names[i]])
        if self.executionmode.get() == "emissionen":
            self.emission_demo_scenario()
        elif self.executionmode.get() == "monetaer":
            self.monetary_demo_scenario()

    def include_optimized_scenarios(self):
        self.results_dict['Status Quo'] = \
            [8.2594606, 18521.2, 0, 0, 0, 0, 0, 0]
        self.results_dict['Financial Minimum'] = \
            [1.310668, 14400.430112, 29700, 10000, 0, 0, 0, 0]
        self.results_dict['Emission Minimum'] = \
            [9.825963, 12574.7, 5526, 644, 29680, 2769, 0, 10000]

    def save_results(self):

        interim_results = [float(self.monetary_costs.get()),
                           float(self.emission_costs.get()),]

        for i in range(1, len(self.entry_values)):
            interim_results.append(
                int(self.entry_values[self.demo_names[i]].get()))

        self.results_dict[self.entry_values[self.demo_names[0]].get()] \
            = interim_results
        print(self.results_dict)

    def save_manual_results(self):
        interim_results2 = [float(self.entry_monetary_costs_value.get()),
                            float(self.entry_emission_costs_value.get()),]

        for i in range(1, len(self.entry_values)):
            interim_results2.append(
                int(self.entry_values2[self.demo_names2[i]].get()))

        self.results_dict[self.entry_values2[self.demo_names2[0]].get()] \
            = interim_results2
        print(self.results_dict)

    def plot_results_scatter(self):

        plt.xlabel('Mio. EUR/a')
        plt.ylabel('t/a')

        keys = list(self.results_dict.keys())
        print(keys)
        values = list(self.results_dict.values())
        print(values)

        for i in range(len(self.results_dict)):
            plt.scatter(values[i][0],values[i][1],label=keys[i])

        plt.legend()
        # fig2.tight_layout()
        plt.show()

    def plot_results_bar(self):
        import matplotlib
        import matplotlib.pyplot as plt
        import numpy as np

        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                                       NavigationToolbar2Tk)

        # the figure that will contain the plot
        fig = Figure(figsize=(5, 5), dpi=100)

        labels = list(self.demo_components.keys())
        labels.pop(0)

        scenario_names = list(self.results_dict.keys())
        print(scenario_names)

        scenarios = []
        scenario_data = list(self.results_dict.values())
        print(scenario_data)

        for i in range(len(scenario_data)):
            test_list = scenario_data[i][:]
            test_list.pop(0)
            test_list.pop(0)
            scenarios.append(test_list)

        print(scenarios)

        x = np.arange(len(labels))  # the label locations
        width = 0.5/len(scenarios)  # the width of the bars

        fig, ax = plt.subplots()

        bars = []
        for i in range(len(scenarios)):
            bars.append(ax.bar(x + width*i, scenarios[i], width,
                               label=scenario_names[i]))

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Capacity')
        ax.set_title('Scenarios')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()

        fig.tight_layout()

        plt.show()

    def __init__(self, window, tab_control, demo_frame):
        # Definition of the DEMO-Frames
        # main_frame = ttk.Frame(tab_control)
        self.mainpath = \
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        self.window = window
        tab_control.add(demo_frame, text='DEMO')
        self.monetary_costs = StringVar()
        self.monetary_costs.set('--')

        self.emission_costs = StringVar()
        self.emission_costs.set('--')

        self.results_dict = {}
        # DEMO explanation

        row = 0
        explanation = ('DEMO-Energy System: In this DEMO the financial costs '
                       'and carbon dioxide emissions of a residential area are '
                       'simulated. For improvement, the technologies listed '
                       'below are \n available with the parameters below. The '
                       'simulated scenarios can be compared with the status '
                       'quo, the financial minimum and the emission minimum.')

        label_explanation = Label(demo_frame, text=explanation,
                                  font='Helvetica 10 bold')
        label_explanation.grid(column=0, columnspan=7, row=row)

        row = row + 1
        label_monetary_costs = Label(demo_frame, text='Simulation Input',
                                     font='Helvetica 10 bold')
        label_monetary_costs.grid(column=1, row=row)
        label_monetary_costs = Label(demo_frame, text='Manual Result Input',
                                     font='Helvetica 10 bold')
        label_monetary_costs.grid(column=5, row=row)

        demo_components = {"name": 'name',
                           "windpower": '0',
                           "photovoltaics": '0',
                           "battery": '0',
                           "chp": '0',
                           "thermal storage": '0',
                           "district heating": '0'}
        self.demo_components = demo_components
        self.demo_unit = {"name": '',
                     "windpower": 'kW',
                     "photovoltaics": 'kW',
                     "battery": 'kWh',
                     "chp": 'kW (el.)',
                     "thermal storage": 'kWh',
                     "district heating": 'True (1) / False (0)'}

        row = row + 1
        self.demo_names = list(demo_components.keys())
        demo_values = list(demo_components.values())
        self.entry_values = {}

        # Erstellt Eingabefelder für alle variierbaren componenten.
        for i in range(len(demo_components)):
            column = 0

            # Defines Label
            label_name = Label(demo_frame, text=self.demo_names[i],
                               font='Helvetica 10')
            label_name.grid(column=column, row=row, sticky="W")
            column = column + 1

            # Defines Entry Field
            self.entry_values[self.demo_names[i]] = StringVar()
            self.entry_values[self.demo_names[i]].set(demo_values[i])
            self.entry_values[self.demo_names[i]] = Entry(demo_frame, text=str(
                self.entry_values[self.demo_names[i]]))
            self.entry_values[self.demo_names[i]].grid(column=column, row=row)
            column = column + 1

            # Defines Unit
            label_name = Label(demo_frame,
                               text=self.demo_unit[self.demo_names[i]],
                               font='Helvetica 10')
            label_name.grid(column=column, row=row, sticky="W")

            row = row + 1

        # EXECUTION BUTTONS
        # row = row + 1
        self.executionmode = StringVar()
        OptionMenu(demo_frame, self.executionmode, "emissionen", "monetaer")\
            .grid(column=1, row=row, pady=4)
        row = row + 1
        Button(demo_frame, text='SIMULATE', command=self.simulate_scenario)\
            .grid(column=1, row=row, pady=4)

        # RESULTS
        row = row + 2
        label_monetary_costs = Label(demo_frame, text='RESULTS',
                                     font='Helvetica 10')
        label_monetary_costs.grid(column=0, row=row, sticky="W")

        row = row + 1
        label_monetary_costs = Label(demo_frame, text='Monetary Costs: ',
                                     font='Helvetica 10')
        label_monetary_costs.grid(column=0, row=row, sticky="W")

        label_monetary_costs_value = Label(demo_frame,
                                           textvariable=self.monetary_costs,
                                           font='Helvetica 10')
        label_monetary_costs_value.grid(column=1, row=row, sticky="W")

        label_monetary_unit = Label(demo_frame, text=' Mio. EUR/a',
                                    font='Helvetica 10')
        label_monetary_unit.grid(column=2, row=row, sticky="W")

        row = row + 1
        label_emission_costs = Label(demo_frame, text='CO2 Emissions: ',
                                     font='Helvetica 10')
        label_emission_costs.grid(column=0, row=row, sticky="W")
        label_emission_costs_value = Label(demo_frame,
                                           textvariable=self.emission_costs,
                                           font='Helvetica 10')
        label_emission_costs_value.grid(column=1, row=row, sticky="W")
        label_emission_unit = Label(demo_frame, text=' t/a',
                                    font='Helvetica 10')
        label_emission_unit.grid(column=2, row=row, sticky="W")

        # EXECUTION BUTTONS
        row = row + 1
        Button(demo_frame, text='SAVE', command=self.save_results)\
            .grid(column=1, row=row, sticky=W, pady=4)

        for i in range(15):
            label_placeholder = Label(demo_frame, text=' || ',
                                      font='Helvetica 10')
            label_placeholder.grid(column=3, row=i + 1)

        row = 2
        self.demo_names2 = list(demo_components.keys())
        demo_values2 = list(demo_components.values())
        self.entry_values2 = {}

        # Erstellt Eingabefelder für alle variierbaren componenten.
        for i in range(len(demo_components)):
            column = 4

            # Defines Label
            label_name = Label(demo_frame, text=self.demo_names2[i],
                               font='Helvetica 10')
            label_name.grid(column=column, row=row, sticky="W")
            column = column + 1

            # Defines Entry Field
            self.entry_values2[self.demo_names2[i]] = StringVar()
            self.entry_values2[self.demo_names2[i]].set(demo_values2[i])
            self.entry_values2[self.demo_names2[i]] = \
                Entry(demo_frame,
                      text=str(self.entry_values2[self.demo_names2[i]]))
            self.entry_values2[self.demo_names2[i]]\
                .grid(column=column, row=row)
            column = column + 1

            # Defines Unit
            label_name = Label(demo_frame,
                               text=self.demo_unit[self.demo_names2[i]],
                               font='Helvetica 10')
            label_name.grid(column=column, row=row, sticky="W")

            row = row + 1

        # RESULTS

        row = row + 2
        label_monetary_costs = Label(demo_frame, text='RESULTS',
                                     font='Helvetica 10')
        label_monetary_costs.grid(column=4, row=row, sticky="W")

        row = row + 1
        label_monetary_costs_2 = Label(demo_frame, text='Monetary Costs',
                                       font='Helvetica 10')
        label_monetary_costs_2.grid(column=0 + 4, row=row, sticky="W")

        entry_monetary_costs_value = IntVar()
        entry_monetary_costs_value.set(0)
        entry_monetary_costs_value = Entry(demo_frame, text=str(
            entry_monetary_costs_value))
        entry_monetary_costs_value.grid(column=1 + 4, row=row)

        label_monetary_unit_2 = Label(demo_frame, text=' Mio. EUR/a',
                                      font='Helvetica 10')
        label_monetary_unit_2.grid(column=2 + 4, row=row, sticky="W")

        row = row + 1

        label_emission_costs_2 = Label(demo_frame, text='CO2 Emissions',
                                       font='Helvetica 10')
        label_emission_costs_2.grid(column=0 + 4, row=row, sticky="W")

        entry_emission_costs_value = IntVar()
        entry_emission_costs_value.set(0)
        entry_emission_costs_value = Entry(demo_frame, text=str(
            entry_emission_costs_value))
        entry_emission_costs_value.grid(column=1 + 4, row=row)

        label_emission_unit_2 = Label(demo_frame, text=' t/a',
                                      font='Helvetica 10')
        label_emission_unit_2.grid(column=2 + 4, row=row, sticky="W")
        self.entry_monetary_costs_value = entry_monetary_costs_value
        self.entry_emission_costs_value = entry_emission_costs_value
        #
        #
        # EXECUTION BUTTONS
        row = 15
        Button(demo_frame, text='SAVE', command=self.save_manual_results)\
            .grid(column=1 + 4, row=row, pady=4)
        row = row + 1
        label_line = Label(demo_frame, text=14 * '===========',
                           font='Helvetica 10')
        label_line.grid(column=0, row=row, columnspan=7)
        row = row + 1
        Button(demo_frame, text='SCATTER PLOT',
               command=self.plot_results_scatter)\
            .grid(column=2, row=row, pady=4)
        Button(demo_frame, text='BAR PLOT', command=self.plot_results_bar)\
            .grid(column=4, row=row, pady=4)
        Button(demo_frame, text='Include Optimized Scenarios',
               command=self.include_optimized_scenarios)\
            .grid(column=3, row=row, pady=4)
        row = row + 1
        label_line = Label(demo_frame, text=14 * '===========',
                           font='Helvetica 10')
        label_line.grid(column=0, row=row, columnspan=7)
        
        demo_assumptions = {
            'Electricity Demand': '14 000 000 kWh/a, h0 Load Profile',
            'Heaty Demand': '52 203 000 kWh/a, EFH Load Profile',
            'Windturbines': '2 000 000 €/MW, 8 g/kWh, 20 a, max. 29.7 MW',
            'Photovoltaics': '1 140 000 €/MW, 56 g/kWh, 20 a, max. 10 MW',
            'Battery': '1 000 000 €/MWh, 155 t/MWh (Invest!), 20 a',
            'CHP': '190 000 €/MWh (el.), 375 g/kWh (el), 165 g/kWh (th.), '
                   '20 a',
            'Thermal Storage': '35 000 €/MWh, 46 g/kWh, 20 a, 3 % loss /d',
            'district heating': '86 000 000 €, 15 % loss, 40 a',
            'Gas Import/Heating': '6.4 ct/kWh (gas), 85 % efficiency, '
                                  '45.62 g/kWh',
            'Electricity Import': '30.5 ct/kWh, 474 g/kWh'
            }

        assumption_keys = list(demo_assumptions.keys())
        assumption_values = list(demo_assumptions.values())

        row = row + 1
        rowcount = 0
        column = 4

        for i in range(len(demo_assumptions)):
            label = Label(demo_frame, text=assumption_keys[i],
                          font='Helvetica 10 bold')
            label.grid(column=column, row=row, sticky="W")

            label = Label(demo_frame, text=assumption_values[i],
                          font='Helvetica 10')
            label.grid(column=column + 1, columnspan=2, row=row, sticky="W")

            row = row + 1
