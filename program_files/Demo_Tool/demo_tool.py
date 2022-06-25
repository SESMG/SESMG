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
from program_files.preprocessing.Spreadsheet_Energy_System_Model_Generator \
    import sesmg_main
from program_files.GUI_files import MethodsGUI


class demo_frame_class(MethodsGUI):

    def execute_sesmg_DEMO(self, demo_file, demo_results):
        """ Excecutes the optimization algorithm """
        print(demo_file)
        print(demo_results)

        sesmg_main(
            scenario_file=demo_file,
            result_path=demo_results,
            num_threads=2,
            timeseries_prep=['none', 'none', 'none', 'none', 0],
            graph=False,
            criterion_switch=False,
            xlsx_results=False,
            console_results=False,
            solver="cbc",
            cluster_dh=False,
            district_heating_path="")

    def demo_scenario(self, mode):
        '''modifies financial demo scenario'''
        mode_dict = {
            "monetary": ["demo_scenario_monetaer.xlsx",
                         r"/results/demo/financial",
                         'Total System Costs',
                         'Total Constraint Costs'],
            "emissions": ["demo_scenario_emissionen.xlsx",
                          r"/results/demo/emissions",
                          'Total Constraint Costs',
                          'Total System Costs']}
        
        xfile = openpyxl.load_workbook(os.path.dirname(__file__)
                                       + '/v0.0.6_demo_scenario/'
                                       + mode_dict.get(mode)[0],
                                       data_only=True)

        # PHOTOVOLTAICS
        sheet = xfile["sources"]
        sheet['I3'] = (int(self.entry_values['photovoltaics'].get()))
        sheet['J3'] = (int(self.entry_values['photovoltaics'].get()))
        # SOLAR THERMAL
        sheet = xfile["sources"]
        sheet['I5'] = (int(self.entry_values['solarthermal'].get()))
        sheet['J5'] = (int(self.entry_values['solarthermal'].get()))
        # BATTERY
        sheet = xfile["storages"]
        sheet['N3'] = (int(self.entry_values['battery'].get()))
        sheet['O3'] = (int(self.entry_values['battery'].get()))
        # CHP
        sheet = xfile["transformers"]
        sheet['C4'] = (int(self.entry_values["district heating"].get()))
        sheet['L4'] = (int(self.entry_values['chp'].get()))
        sheet['M4'] = (int(self.entry_values['chp'].get()))
        # ASHP
        sheet = xfile["transformers"]
        sheet['L6'] = (int(self.entry_values['ASHP'].get()))
        sheet['M6'] = (int(self.entry_values['ASHP'].get()))
        # GCHP
        sheet = xfile["transformers"]
        sheet['L5'] = (int(self.entry_values['GCHP'].get()))
        sheet['M5'] = (int(self.entry_values['GCHP'].get()))
        # THERMAL STORAGE
        sheet = xfile["storages"]
        sheet['C4'] = (int(self.entry_values["district heating"].get()))
        sheet['N4'] = (int(self.entry_values['thermal storage'].get()))
        sheet['O4'] = (int(self.entry_values['thermal storage'].get()))
        # THERMAL STORAGE
        sheet = xfile["storages"]
        sheet['N5'] = (int(self.entry_values['thermal storage (decentralized)'].get()))
        sheet['O5'] = (int(self.entry_values['thermal storage (decentralized)'].get()))
        # District Heating
        sheet = xfile["links"]
        sheet['C3'] = (int(self.entry_values['district heating'].get()))

        xfile.save(self.mainpath + mode_dict.get(mode)[1] + '/scenario.xlsx')
        self.execute_sesmg_DEMO(
            demo_file=self.mainpath + mode_dict.get(mode)[1]
                      + r"/scenario.xlsx",
            demo_results=self.mainpath + mode_dict.get(mode)[1])

        df_summary = pd.read_csv(self.mainpath
                                 + mode_dict.get(mode)[1] + r"/summary.csv")
        # monetary_costs = float(df_summary['Total System Costs'])
        self.monetary_costs.set(
            str(round(float(df_summary[mode_dict.get(mode)[2]]/1000000), 2)))
        self.emission_costs.set(
            str(round(float(df_summary[mode_dict.get(mode)[3]])/1000000, 2)))
        self.window.update_idletasks()

    def simulate_scenario(self):
        for i in range(len(self.entry_values)):
            print(self.demo_names[i] + ': '
                  + self.entry_values[self.demo_names[i]].get()
                  + ' ' + self.demo_unit[self.demo_names[i]])
        if self.executionmode.get() == "emissions":
            self.demo_scenario("emissions")
        elif self.executionmode.get() == "monetary":
            self.demo_scenario("monetary")

    def include_optimized_scenarios(self):
        self.results_dict['Status Quo'] = \
            [10.837808, 17222.180444, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.results_dict['Financial Minimum'] = \
            [8.043211, 9221.384569, 10000, 0, 0, 0, 2070.6, 5000, 10000, 0, 0]
        self.results_dict['Emission Minimum'] = \
            [12.96770, 7653.872254, 10000, 6800, 10000, 0, 17523.36,
             5000, 10000, 0, 0]

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
        
    def create_entries(self, demo_components, row, demo_frame, demo_unit,
                       column):
        demo_values = list(demo_components.values())
        demo_names = list(demo_components.keys())
        entry_values = {}
        # Erstellt Eingabefelder für alle variierbaren componenten.
        for i in range(len(demo_components)):
            # Defines Label
            self.create_heading(demo_frame, demo_names[i], column, row, "W")
            # Defines Entry Field
            entry_values[demo_names[i]] = StringVar(demo_values[i])
    
            self.create_entry(demo_frame, row, entry_values[demo_names[i]])
            # Defines Unit
            self.create_heading(demo_frame, demo_unit[demo_names[i]],
                                column + 2, row, "W")
            row += 1
        return entry_values, row
    
    def __init__(self, demo_frame, window):
        # Definition of the DEMO-Frames
        # main_frame = ttk.Frame(tab_control)
        self.mainpath = \
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        self.window = window
        self.monetary_costs = StringVar()
        self.monetary_costs.set('--')

        self.emission_costs = StringVar()
        self.emission_costs.set('--')

        self.results_dict = {}
        # DEMO explanation

        row = 0
        explanation = ('DEMO-Energy System: In this DEMO the financial costs '
                       'and carbon dioxide emissions of a residential area '
                       'are simulated. For improvement, the technologies '
                       'listed below are \n available with the parameters '
                       'below. The simulated scenarios can be compared with '
                       'the status quo, the financial minimum and the '
                       'emission minimum.')

        self.create_heading(demo_frame, explanation, 0, row, "W", True, 7)

        row += 1
        self.create_heading(demo_frame, 'Simulation Input', 1, row, "W", True)
        self.create_heading(demo_frame, 'Manual Result Input', 5, row, "W",
                            True)

        demo_components = {"name": 'name',
                           "photovoltaics": '0',
                           "solarthermal": '0',
                           "battery": '0',
                           "chp": '0',
                           "ASHP": '0',
                           "GCHP": '0',
                           'thermal storage (decentralized)': "0",
                           "thermal storage": '0',
                           "district heating": '0'}
        self.demo_components = demo_components
        self.demo_unit = {"name": '',
                          "photovoltaics": 'kW',
                          "solarthermal": 'kW',
                          "battery": 'kWh',
                          "chp": 'kW (el.)',
                          "ASHP": 'kW',
                          "GCHP": 'kW',
                          'thermal storage (decentralized)': "kWh",
                          "thermal storage": 'kWh',
                          "district heating": 'True (1) / False (0)'}

        row = row + 1
        self.demo_names = list(demo_components.keys())
        self.entry_values, row = \
            self.create_entries(self.demo_components, row,
                                demo_frame, self.demo_unit, 0)
        self.create_heading(demo_frame, "Monetarily driven, emission driven",
                            0, row, "W")
        
        self.executionmode = StringVar(demo_frame, "monetary")
        self.create_option_menu(demo_frame, self.executionmode,
                                ["emissions", "monetary"], 1, row)

        row += 1
        Button(demo_frame, text='SIMULATE', command=self.simulate_scenario)\
            .grid(column=1, row=row, pady=4)

        # RESULTS
        row += 2
        self.create_heading(demo_frame, 'RESULTS', 0, row, "W")
        row += 1
        self.create_heading(demo_frame, "Monetary Costs: ", 0, row, "W")
        label_monetary_costs_value = Label(demo_frame,
                                           textvariable=self.monetary_costs,
                                           font='Helvetica 10')
        label_monetary_costs_value.grid(column=1, row=row, sticky="W")
        self.create_heading(demo_frame, ' Mio. EUR/a', 2, row, "W")
        row += 1
        self.create_heading(demo_frame, 'CO2 Emissions: ', 0, row, "W")
        label_monetary_costs_value = Label(demo_frame,
                                           textvariable=self.emission_costs,
                                           font='Helvetica 10')
        label_monetary_costs_value.grid(column=1, row=row, sticky="W")
        self.create_heading(demo_frame, ' t/a', 2, row, "W")

        # EXECUTION BUTTONS
        row += 1
        Button(demo_frame, text='SAVE', command=self.save_results)\
            .grid(column=1, row=row, sticky=W, pady=4)

        for i in range(15):
            Label(demo_frame, text=' || ', font='Helvetica 10').grid(
                    column=3, row=i + 1)

        row = 2
        self.entry_values2, row = \
            self.create_entries(self.demo_components, row,
                                demo_frame, self.demo_unit, 4)

        # RESULTS

        row = row + 3
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
        row = 18
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
            'Heat Demand': '52 203 000 kWh/a, EFH Load Profile',
            #'Windturbines': '2 000 000 €/MW, 8 g/kWh, 20 a, max. 29.7 MW',
            'Photovoltaics': '1 070 000 €/MW, 27 g/kWh, 20 a, max. 10 MW',
            'Solar Thermal': '  846 000 €/MW, 12 g/kWh, 20 a, max. 6.8 MW',
            'Battery': '1 000 000 €/MWh, 3.96 kg/(kWh * a) (Invest!), 20 a',
            'Gas Heating': '1 005 000 €/MW, 232g/kWh, 18 a, 0.92',
            'CHP': '760 000 €/MW (el.), 308 g/kWh (el), 265 g/kWh (th.), 20 a',
            'Thermal Storage': '35 000 €/MWh, 743 g/(kWh * a), 20 a, 3 % loss /d',
            'Thermal Storage (decentral)': '49 000 €/MWh,  604g/(kWh * a), 20 a, 3 % loss /d',
            'district heating': '86 000 000 €, 15 % loss, 40 a',
            'Gas Import': '6.29 ct/kWh (gas)',
            'Electricity Import': '31.22 ct/kWh, 366 g/kWh, '
                                  'HEATPUMP: 22 ct/kWh, 366 g/kWh',
            'Electricity Export': '- 6.8 ct/kWh, - 27 g/kWh',
            'Air Source Heat Pump': '1 318 000 €/MW, 12g/kWh, 18 a',
            'Ground-coupled Heatpump': '1 444 000 €/MW, 8 g/kWh, 20 a'
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
