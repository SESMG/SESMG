"""
    Functions for returning optimization results in several forms.

    Contributor:
        Christian Klemm - christian.klemm@fh-muenster.de
"""

import logging
import pandas as pd
from oemof import solph
from matplotlib import pyplot as plt
import os
import dhnx


def xlsx(nodes_data: dict, optimization_model: solph.Model, filepath: str):
    """
        Returns model results as xlsx-files.
        Saves the in- and outgoing flows of every bus of a given,
        optimized energy system as .xlsx file

        :param nodes_data: dictionary containing data from excel
                           scenario file
        :type nodes_data: dict
        :param optimization_model: optimized energy system
        :type optimization_model: oemof.solph.model
        :param filepath: path, where the results will be stored
        :type filepath: str
        :return: - **results** (.xlsx) - xlsx files containing in and \
                   outgoing flows of the energy systems' buses.

        Christian Klemm - christian.klemm@fh-muenster.de
    """
    results = solph.processing.results(optimization_model)

    # Writes a spreadsheet containing the input and output flows into
    # every bus of the energy system for every timestep of the
    # timesystem
    for i, b in nodes_data['buses'].iterrows():
        if b['active']:
            file_path = \
                os.path.join(filepath, 'results_' + b['label'] + '.xlsx')
            node_results = solph.views.node(results, b['label'])
            df = node_results['sequences']
            df.head(2)
            with pd.ExcelWriter(file_path) as writer:  # doctest: +SKIP
                df.to_excel(writer, sheet_name=b['label'])
            # returns logging info
            logging.info('   ' + 'Results saved as xlsx for ' + b['label'])
    # Bus xlsx-files for district heating busses
    results_copy = results.copy()
    components = []
    for i in results.keys():
        if 'tag1=' not in str(i):
            results_copy.pop(i)
    for i in results_copy.keys():
        if i[0] not in components and i[0] is not None:
            if "bus" in str(i[0]):
                components.append(i[0])
        if i[1] not in components and i[1] is not None:
            if "bus" in str(i[1]):
                components.append(i[1])
    for component in components:
        file_path = \
            os.path.join(filepath, 'results_' + str(component) + '.xlsx')
        node_results = solph.views.node(results, str(component))
        df = node_results['sequences']
        df.head(2)
        sheet_name = str(component).replace("infrastructure", "infras.")
        with pd.ExcelWriter(file_path) as writer:  # doctest: +SKIP
            df.to_excel(writer, sheet_name=sheet_name)
        # returns logging info
        logging.info('   ' + 'Results saved as xlsx for ' + str(component))


def charts(nodes_data: dict, optimization_model: solph.Model,
           energy_system: solph.EnergySystem):
    """
        Plots model results.

        Plots the in- and outgoing flows of every bus of a given,
        optimized energy system

        :param nodes_data: dictionary containing data from excel
                            scenario file
        :type nodes_data: dict
        :param optimization_model: optimized energy system
        :type optimization_model: oemof.solph.Model
        :param energy_system: original (unoptimized) energy system
        :type energy_system: oemof.solph.Energysystem
        :return: - **plots** (matplotlib.plot) plots displaying in \
                   and outgoing flows of the energy systems' buses.

        Christian Klemm - christian.klemm@fh-muenster.de
    """
    # rename variables
    esys = energy_system
    results = solph.processing.results(optimization_model)

    for i, b in nodes_data['buses'].iterrows():
        if b['active']:
            logging.info('   ' + "******************************************"
                         + "***************")
            logging.info('   ' + 'RESULTS: ' + b['label'])

            bus = solph.views.node(results, b['label'])
            logging.info('   ' + bus['sequences'].sum())
            fig, ax = plt.subplots(figsize=(10, 5))
            bus['sequences'].plot(ax=ax)
            ax.legend(loc='upper center', prop={'size': 8},
                      bbox_to_anchor=(0.5, 1.4), ncol=2)
            fig.subplots_adjust(top=0.7)
            plt.show()

    esys.results['main'] = solph.processing.results(optimization_model)
    esys.results['meta'] = solph.processing.meta_results(optimization_model)
    esys.dump(dpath=None, filename=None)


class Results:
    """
        Class for preparing Plotly results and logging the results of
        Cbc-Solver
    """
    results = None
    esys = None
    comp_input1 = None
    comp_input2 = None
    comp_output1 = None
    comp_output2 = None
    comp_capacity = None
    df_list_of_components = None
    df_result_table = pd.DataFrame()
    # columns_of_plotly_table
    copt = ['ID', 'type', 'input 1/kWh', 'input 2/kWh', 'output 1/kWh',
            'output 2/kWh', 'capacity/kW', 'variable costs/CU',
            'periodical costs/CU', 'investment/kW', 'max. invest./kW',
            'constraints/CU']

    @staticmethod
    def log_category(component: str):
        """
            Returns logging info for type of given components.
            Which is the first step of the logging/ results producing process.

            :param component: component type
            :type component: str
        """
        # returns logging infos
        logging.info('   ' + 56 * "*")
        logging.info('   ' + "***" + component + (53 - len(component)) * "*")
        logging.info('   ' + 56 * "*")
        logging.info('   ' + 56 * "-")

    def create_flow_dataframes(self, component, comp=None,
                               excess_or_shortage=None,
                               district_heating=None):
        """
            creates up to 5 pandas series consisting the flows of the
            given component
        """
        # clearing all possibly used variables
        self.comp_input1 = None
        self.comp_input2 = None
        self.comp_output1 = None
        self.comp_output2 = None
        self.comp_capacity = None

        if comp is not None:
            label = comp['label']
            # because of not every sheet consisting the same columns these
            # tests are necessary
            bus1 = comp['bus1'] if 'bus1' in comp else None
            bus2 = comp['bus2'] if 'bus2' in comp else None
            if 'input' in comp:
                input1 = comp['input']
            elif 'bus' in comp:
                input1 = comp['bus']
            else:
                input1 = None
            if 'output' in comp:
                output = comp['output']
            elif 'bus' in comp:
                output = comp['bus']
            else:
                output = None
            output2 = comp['output2'] if 'output2' in comp else None
            for index, value in component['sequences'].sum().items():
                # inflow 1
                if index in [((input1, label), 'flow'),
                             ((bus1, label), 'flow'),
                             ((label, label + '_excess'), 'flow')]:
                    self.comp_input1 = component['sequences'][index]
                # inflow2
                elif index in [((label + '_low_temp' + '_bus', label), 'flow'),
                               ((label + '_high_temp' + '_bus', label),
                                'flow'),
                               ((bus2, label), 'flow'),
                               ((label[:-10] + '_bus', label), 'flow')]:
                    self.comp_input2 = component['sequences'][index]
                # outflow 1
                elif index in [((label, output), 'flow'),
                               ((label, bus2), 'flow'),
                               ((label + '_shortage', label), 'flow')]:
                    self.comp_output1 = component['sequences'][index]
                # outflow 2
                elif index in [((label, output2), 'flow'),
                               ((label, bus1), 'flow')]:
                    self.comp_output2 = component['sequences'][index]
                # capacity
                elif index == ((label, 'None'), 'storage_content'):
                    self.comp_capacity = component['sequences'][index]
            if excess_or_shortage == "excess":
                self.comp_output1 = None
            elif excess_or_shortage == "shortage":
                self.comp_input1 = None
        else:
            input_one = False
            output_one = False
            for index, value in component['sequences'].sum().items():
                index_parts = str(index).split(",")
                if district_heating['label'] in index_parts[1] \
                        and not input_one:
                    self.comp_input1 = component['sequences'][index]
                    input_one = True
                elif district_heating['label'] in index_parts[1] \
                        and input_one:
                    self.comp_input2 = component['sequences'][index]
                elif district_heating['label'] in index_parts[0] \
                        and not output_one:
                    self.comp_output1 = component['sequences'][index]
                    output_one = True
                elif district_heating['label'] in index_parts[0] \
                        and output_one:
                    self.comp_output2 = component['sequences'][index]

    def get_comp_investment(self, comp=None, comp_type=None):
        component_investment = 0
        if comp is not None:
            if comp['max. investment capacity'] > 0:
                component_node = self.esys.groups[comp['label']]
            
                # defines bus_node for different components
                if comp_type == 'source':
                    if comp['input'] in [0, 'None', 'none']:
                        bus_node = self.esys.groups[comp['output']]
                    else:
                        component_node = self.esys.groups[comp['label'][:-10]]
                        label = comp['label'][:-10] + '_bus'
                        bus_node = self.esys.groups[label]
                elif comp_type == 'storage':
                    bus_node = None
                elif comp_type == 'link':
                    bus_node = self.esys.groups[comp['bus2']]
                elif comp_type == 'transformer':
                    bus_node = self.esys.groups[comp['output']]
                else:
                    raise ValueError('comp_type not known')
                # sets component investment
                component_investment += (self.results[component_node, bus_node]
                ['scalars']['invest'])
                if comp_type == 'source':
                    if comp['input'] not in [0, 'None', 'none']:
                        # considers area conversion factor on investment for
                        # solar heat sources
                        component_investment = \
                            component_investment / comp['Conversion Factor']
        
        return component_investment

    def get_dh_investment(self, label):
        component_invest = 0
        print(type(label))
        if "bus" not in str(type(label)):
            for i in self.results.keys():
                node_1 = self.esys.groups[str(i[0])]
                if "link-dhnx-" in str(i[0]):
                    if str(label) in str(i[0]):
                        if "clustered_consumers" in str(i[1]):
                            node_2 = self.esys.groups[str(i[1])]
                            component_invest += (self.results[node_1, node_2]
                                                 ["scalars"]["invest"])
                elif "clustered_consumers" in str(i[0]):
                    if str(label) in str(i[0]):
                        if "heat_bus" in str(i[1]):
                            node_2 = self.esys.groups[str(i[1])]
                            component_invest += (self.results[node_1, node_2]
                            ["scalars"]["invest"])
                elif "infrastructure" in str(i[0]) \
                        and "infrastructure" in str(i[1]):
                    if str(label) in str(i[0]):
                        if "forks" in str(i[0]) and "forks" in str(i[1]):
                            node_2 = self.esys.groups[str(i[1])]
                            component_invest += (self.results[node_1, node_2]
                                                 ["scalars"]["invest"])
                            #print(self.results[node_1, node_2])
                        if "forks" in str(i[0]) and "consumers" in str(i[1]):
                            node_2 = self.esys.groups[str(i[1])]
                            component_invest += (self.results[node_1, node_2]
                                                 ["scalars"]["invest"])
                        if "producers" in str(i[0]) and "forks" in str(i[1]):
                            node_2 = self.esys.groups[str(i[1])]
                            component_invest += (self.results[node_1, node_2]
                                                 ["scalars"]["invest"])
            print(component_invest)
        return component_invest
        #else:
        #    if not "source" in district_heating['label'] \
        #            and not "heat_bus" in district_heating['label'] \
        #            and not district_heating['label'][-1] == "-" \
        #            and not "dh-" in district_heating['label']:
        #        print(self.results.keys())
        #        component_node = self.esys.groups[district_heating['label']]
        #        bus_node = self.esys.groups[district_heating['output']]
        #        component_investment += (self.results[component_node, bus_node]
        #        ['scalars']['invest'])

    def calc_constraint_costs(self, comp, investment=None, comp_type=None):
        # get flow values
        inflow1 = 0 if self.comp_input1 is None else self.comp_input1.sum()
        outflow1 = 0 if self.comp_output1 is None else self.comp_output1.sum()
        outflow2 = 0 if self.comp_output2 is None else self.comp_output2.sum()

        constraint_costs = 0
        # calculating constraint costs for different components
        if comp_type == 'source':
            constraint_costs += outflow1 * comp['variable constraint costs']
        elif comp_type == 'link':
            constraint_costs += \
                comp['variable constraint costs'] * (outflow1 + outflow2)
        elif comp_type == 'excess':
            constraint_costs += \
                inflow1 * comp['excess constraint costs']
        elif comp_type == 'shortage':
            constraint_costs += \
                outflow1 * comp['shortage constraint costs']
        else:
            constraint_costs += outflow1 \
                                * comp['variable output constraint costs']
            if comp_type == 'transformer':
                constraint_costs \
                    += outflow2 * comp['variable output constraint costs 2']
                constraint_costs \
                    += inflow1 * comp['variable input constraint costs']
            if comp_type == 'storage':
                constraint_costs \
                    += inflow1 * comp['variable input constraint costs']

        if comp_type != 'excess' and comp_type != 'shortage':
            constraint_costs += investment \
                                * comp['periodical constraint costs']
        return constraint_costs

    def calc_variable_costs(self, comp, comp_type):
        # get flow values
        inflow1 = 0 if self.comp_input1 is None else self.comp_input1.sum()
        outflow1 = 0 if self.comp_output1 is None else self.comp_output1.sum()
        outflow2 = 0 if self.comp_output2 is None else self.comp_output2.sum()

        variable_costs = 0

        if comp_type == 'sources':
            variable_costs += comp['variable costs'] * outflow1
        elif comp_type == 'storages' or comp_type == 'transformers':
            variable_costs += comp['variable input costs'] * inflow1
            variable_costs += comp['variable output costs'] * outflow1
            if comp_type == 'transformers':
                variable_costs += (comp['variable output costs 2'] * outflow2)
        elif comp_type == 'links':
            variable_costs += \
                comp['variable output costs'] * (outflow1 + outflow2)
        elif comp_type == 'excess':
            variable_costs += comp['excess costs'] * inflow1
        elif comp_type == 'shortage':
            variable_costs += comp['shortage costs'] * outflow1

        return variable_costs

    @staticmethod
    def calc_periodical_costs(comp, investment):
        periodical_costs = 0
        fix_invest = comp['fix investment costs'] \
            if 'fix investment costs' in comp else 0
        non_convex = comp['non-convex investment'] \
            if 'non-convex investment' in comp else 0
        periodical_costs += (fix_invest
                             if (non_convex == 1 and investment > 0) else 0)
        periodical_costs += investment * comp['periodical costs']
        return periodical_costs

    def add_component_to_loc(self, label, comp_type,
                             capacity=None, variable_costs=None,
                             periodical_costs=None, investment=None,
                             maxinvest='---',
                             constraints=None):
        """
            adds the given component with its parameters to
            list of components (loc)
        """
        # creating strings for dataframe
        inflow1 = '---' if self.comp_input1 is None \
            else str(round(self.comp_input1.sum(), 2))
        inflow2 = '---' if self.comp_input2 is None \
            else str(round(self.comp_input2.sum(), 2))
        outflow1 = '---' if self.comp_output1 is None \
            else str(round(self.comp_output1.sum(), 2))
        outflow2 = '---' if self.comp_output2 is None \
            else str(round(self.comp_output2.sum(), 2))
        capacity = '---' if capacity is None \
            else str(round(capacity, 2))
        variable_costs = '---' if variable_costs is None \
            else str(round(variable_costs, 2))
        periodical_costs = '---' if periodical_costs is None \
            else str(round(periodical_costs, 2))
        investment = '---' if investment is None \
            else str(round(investment, 2))
        constraints = '---' if constraints is None \
            else str(round(constraints, 2))

        self.df_list_of_components = \
            self.df_list_of_components.append(
                pd.DataFrame(
                    [[label, comp_type, inflow1, inflow2, outflow1, outflow2,
                      capacity, variable_costs, periodical_costs, investment,
                      maxinvest,
                      constraints]], columns=self.copt))

    @staticmethod
    def get_first_node_flow(flow):
        """ returns begin of the flow, used to log where the flow comes from"""
        flow_name = str(flow.name)
        flow_name = flow_name[2:-10]
        flow_name = flow_name.split(',')
        return flow_name[0]

    @staticmethod
    def get_last_node_flow(flow):
        """ returns end of the flow, used to log where the flow goes to"""
        flow_name = str(flow.name)
        flow_name = flow_name[2:-10]
        flow_name = flow_name.split(',')
        return flow_name[1]

    def console_logging(self, comp_type, capacity=None, variable_costs=None,
                        periodical_costs=None, investment=None,
                        transformer_type=None):
        """
            consists of the different console logging entries and logs
            the one for the given component
        """

        inflow1 = self.comp_input1
        inflow2 = self.comp_input2
        outflow1 = self.comp_output1
        outflow2 = self.comp_output2

        if comp_type == 'sink':
            logging.info('   ' + 'Total Energy Demand: ' + str(inflow1.sum())
                         + ' kWh')
        else:
            if comp_type == 'source':
                if inflow1 is None or \
                        'shortage' in self.get_first_node_flow(outflow1):
                    logging.info('   ' + 'Total Energy Input: '
                                 + str(outflow1.sum()) + ' kWh')
                    logging.info('   ' + 'Max. Capacity: ' + str(capacity)
                                 + ' kW')
                else:
                    logging.info('   ' + 'Input from '
                                 + self.get_first_node_flow(inflow1) + ': '
                                 + str(round(inflow1.sum(), 2)) + ' kWh')
                    logging.info('   ' + 'Ambient Energy Input to '
                                 + self.get_first_node_flow(inflow2) + ': '
                                 + str(round(inflow2.sum(), 2)) + ' kWh')
                    logging.info('   ' + 'Energy Output to '
                                 + self.get_last_node_flow(outflow1) + ': '
                                 + str(round(outflow1.sum(), 2)) + ' kWh')

            if comp_type == 'transformer':
                if inflow2 is None:
                    logging.info('   ' + 'Total Energy Output to'
                                 + self.get_last_node_flow(outflow1) + ': '
                                 + str(round(outflow1.sum(), 2)) + ' kWh')
                    if outflow2 is not None:
                        logging.info('   ' + 'Total Energy Output to'
                                     + self.get_last_node_flow(outflow2) + ': '
                                     + str(round(outflow2.sum(), 2)) + ' kWh')
                else:
                    logging.info('   ' + 'Electricity Energy Input to '
                                 + self.get_first_node_flow(inflow1) + ': '
                                 + str(round(inflow1.sum(), 2)) + ' kWh')
                    if transformer_type == 'absorption_heat_transformer':
                        logging.info('   ' + 'Heat Input to'
                                     + self.get_last_node_flow(inflow2) + ': '
                                     + str(round(inflow2.sum(), 2)) + ' kWh')
                    elif transformer_type == 'compression_heat_transformer':
                        logging.info('   ' + 'Ambient Energy Input to'
                                     + self.get_last_node_flow(inflow2) + ': '
                                     + str(round(inflow2.sum(), 2)) + ' kWh')
                    logging.info('   ' + 'Total Energy Output to'
                                 + self.get_last_node_flow(outflow1) + ': '
                                 + str(round(outflow1.sum(), 2)) + ' kWh')
                logging.info('   ' + 'Max. Capacity: ' + str(capacity) + ' kW')

                if comp_type == 'storage':
                    logging.info(
                        '   ' + 'Energy Output from '
                        + self.get_first_node_flow(outflow1) + ': '
                        + str(round(outflow1.sum(), 2)) + 'kWh')
                    logging.info('   ' + 'Energy Input to '
                                 + self.get_last_node_flow(outflow1) + ': '
                                 + str(round(inflow1.sum(), 2)) + ' kWh')

                if comp_type == 'link':
                    if capacity is None:
                        logging.info('   ' + 'Total Energy Output to '
                                     + self.get_last_node_flow(outflow1) + ': '
                                     + str(round(outflow1.sum(), 2)) + ' kWh')
                        logging.info('   ' + 'Total Energy Output to '
                                     + self.get_last_node_flow(outflow2) + ': '
                                     + str(round(outflow2.sum(), 2)) + ' kWh')
                        logging.info('   ' + 'Max. Capacity to '
                                     + self.get_last_node_flow(outflow1) + ': '
                                     + str(round(outflow1.max(), 2)) + ' kW')
                        logging.info('   ' + 'Max. Capacity to '
                                     + self.get_last_node_flow(outflow2) + ': '
                                     + str(round(outflow2.max(), 2)) + ' kW')
                    else:
                        logging.info('   ' + 'Total Energy Output to '
                                     + self.get_last_node_flow(outflow1) + ': '
                                     + str(round(outflow1.sum(), 2)) + ' kWh')
                        logging.info('   ' + 'Max. Capacity to '
                                     + self.get_last_node_flow(outflow1) + ': '
                                     + str(round(capacity, 2)) + ' kW')
            if investment is not None:
                logging.info('   ' + 'Investment Capacity: '
                             + str(round(investment, 2)) + ' kW')
            if periodical_costs is not None:
                logging.info('   ' + 'Periodical costs: '
                             + str(round(periodical_costs, 2))
                             + ' cost units p.a.')
            logging.info('   ' + 'Variable Costs: '
                         + str(round(variable_costs, 2)) + ' cost units')

    @staticmethod
    def insert_line_end_of_component():
        logging.info(
            '   ' + '--------------------------------------------------------')

    def __init__(self, nodes_data: dict, optimization_model: solph.Model,
                 energy_system: solph.EnergySystem, result_path: str,
                 console_log: bool):
        """
            Returns a list of all defined components with the following
            information:

            +------------+----------------------------------------------+
            |component   |   information                                |
            +------------+----------------------------------------------+
            |sinks       |   Total Energy Demand                        |
            +------------+----------------------------------------------+
            |sources     |   Total Energy Input, Max. Capacity,         |
            |            |   Variable Costs, Periodical Costs           |
            +------------+----------------------------------------------+
            |transformers|   Total Energy Output, Max. Capacity,        |
            |            |   Variable Costs, Investment Capacity,       |
            |            |   Periodical Costs                           |
            +------------+----------------------------------------------+
            |storages    |   Energy Output, Energy Input, Max. Capacity,|
            |            |   Total variable costs, Investment Capacity, |
            |            |   Periodical Costs                           |
            +------------+----------------------------------------------+
            |links       |   Total Energy Output                        |
            +------------+----------------------------------------------+

            Furthermore, a list of recommended investments is printed.

            The algorithm uses the following steps:

                1. logging the component type for example "sinks"
                2. creating pandas dataframe out of the results of the
                   optimization consisting of every single flow in/out
                   a component
                3. calculating the investment and the costs regarding
                   the flows
                4. adding the component to the list of components (loc)
                   which is part of the plotly dash and is the content
                   of components.csv
                5. logging the component specific text with its parameters
                   in the console

            :param nodes_data: dictionary containing data from excel \
                               scenario file
            :type nodes_data: dict
            :param optimization_model: optimized energy system
            :type optimization_model: oemof.solph.Model
            :param energy_system: original (unoptimized) energy system
            :type energy_system: oemof.solph.Energysystem
            :param result_path: Path where the results are saved.
            :type result_path: str

            Christian Klemm - christian.klemm@fh-muenster.de
            Gregor Becker - gregor.becker@fh-muenster.de
        """

        components_dict = {
            "sinks": nodes_data['sinks'],
            "buses_e": nodes_data['buses'],
            "sources": nodes_data['sources'],
            "buses_s": nodes_data['buses'],
            "transformers": nodes_data['transformers'],
            "storages": nodes_data['storages'],
            "links": nodes_data['links']
        }
        # create excess and shortage sheet
        components_dict['buses_e'] = components_dict['buses_e'].drop(
            components_dict['buses_e']
            [components_dict['buses_e']['excess'] == 0].index)
        components_dict['buses_s'] = components_dict['buses_s'].drop(
            components_dict['buses_s']
            [components_dict['buses_s']['shortage'] == 0].index)

        investments_to_be_made = {}
        total_periodical_costs = 0
        total_usage = 0
        total_variable_costs = 0
        total_constraint_costs = 0
        total_demand = 0
        # define class variables
        self.esys = energy_system
        self.results = solph.processing.results(optimization_model)
        self.df_list_of_components = pd.DataFrame(columns=self.copt)
        self.df_result_table = pd.DataFrame()
        for i in components_dict:
            investment = None
            variable_costs = None
            periodical_costs = None
            constraint_costs = None
            transformer_type = None
           
            if i != 'buses_e' and i != 'buses_s' and console_log:
                self.log_category(i.upper())
            for j, comp in components_dict[i].iterrows():
                if comp['active']:
                    # needed due to the structure of thermal flat plate
                    if i == 'sources' and comp[
                            'technology'] in ['solar_thermal_flat_plate',
                                              'concentrated_solar_power']:
                        comp['label'] = comp['label'] + '_collector'

                    if i == 'buses_e':
                        if console_log:
                            logging.info('   ' + comp['label'] + '_excess')
                        excess_or_shortage = "excess"
                    elif i == 'buses_s':
                        if console_log:
                            logging.info('   ' + comp['label'] + '_shortage')
                        excess_or_shortage = "shortage"
                    else:
                        if console_log:
                            logging.info('   ' + comp['label'])
                        excess_or_shortage = None
                    component = solph.views.node(self.results, comp['label'])
                    
                    # create class intern dataframes consisting the flows
                    # of given component
                    self.create_flow_dataframes(component, comp,
                                                excess_or_shortage)
                    
                    if i != 'buses_s' and i != 'buses_e' and i != "sinks":
                        # get the investment on component out of results
                        # of the optimization
                        # (excluding sinks, excess sinks and shortage sources)
                        investment = self.get_comp_investment(comp, i[:-1])
                        if investment > 0:
                            investments_to_be_made[comp['label']] = \
                               (str(round(investment, 2)) + ' kW')
                        # calculate periodical costs
                        periodical_costs = \
                            self.calc_periodical_costs(comp, investment)
                        total_periodical_costs += periodical_costs
                        # calculate variable costs
                        variable_costs = self.calc_variable_costs(comp, i)
                        total_variable_costs += variable_costs
                        # calculate constraint costs
                        constraint_costs = self.calc_constraint_costs(
                            comp, comp_type=i[:-1], investment=investment)
                        total_constraint_costs += constraint_costs
                    # sinks
                    if i == "sinks" or i == 'buses_e':
                        # the following values do not apply to sinks 
                        periodical_costs = None
                        investment = None
                        # excess sink
                        if i == 'buses_e':
                            comp_label = comp['label'] + '_excess'
                            # calculation of excess costs
                            variable_costs = \
                                self.calc_variable_costs(comp, 'excess')
                            total_variable_costs += variable_costs
                            # calculation of excess constraint costs
                            constraint_costs = self.calc_constraint_costs(
                                comp, comp_type="excess")
                            total_constraint_costs += constraint_costs
                        # demand sink
                        else:
                            total_demand += self.comp_input1.sum()
                            comp_label = comp['label']
                            variable_costs = None
                            constraint_costs = None
                            input1 = self.comp_input1.copy()
                            self.comp_input1 = None
                            input = comp["input"]
                            for num, insulation in \
                                    nodes_data["energetic_renovation"].iterrows():
                                if insulation["sink"] == comp["label"]:
                                    comp_type = "insulation"
                                    investment = \
                                        self.results[self.esys.groups["egs-" + str(insulation["label"])],
                                                     self.esys.groups[str(input)]]["scalars"]["invest"]
                                    capacity = investment
                                    periodical_costs = investment * insulation["ep_costs_kW"]
                                    #investment = self.get_comp_investment(insulation, "source")
                                    self.add_component_to_loc(
                                            label=str(insulation["label"]),
                                            comp_type=comp_type,
                                            capacity=capacity,
                                            variable_costs=variable_costs,
                                            periodical_costs=periodical_costs,
                                            investment=investment,
                                            maxinvest="---",
                                            constraints=constraint_costs)
                            self.comp_input1 = input1.copy()
                        capacity = round(self.comp_input1.max(), 2)
                        self.df_result_table[comp_label] = self.comp_input1
                    # sources
                    elif i == "sources" or i == 'buses_s':
                        total_usage += self.comp_output1.sum()
                        comp_input = \
                            comp['input'] if 'input' in comp else 'None'
                        # shortage source
                        if i == 'buses_s':
                            # calculation of excess costs
                            variable_costs = \
                                self.calc_variable_costs(comp, 'shortage')
                            total_variable_costs += variable_costs

                            # calculation of excess constraint costs
                            constraint_costs = self.calc_constraint_costs(
                                comp, comp_type="shortage")
                            total_constraint_costs += constraint_costs
                            # the following values do not apply to
                            # shortage-sources 
                            periodical_costs = None
                            investment = None
                        # Non-thermal-sources and shortage sources
                        if comp_input in [0, 'None', 'none']:
                            if i != 'buses_s':
                                comp_label = comp['label']
                            else:
                                comp_label = comp['label'] + '_shortage'
                            self.df_result_table[comp_label] = \
                                self.comp_output1
                            capacity = round(self.comp_output1.max(), 2)
                        # thermal-sources
                        else:
                            self.df_result_table[
                                comp['label'] + '_el_input'] = \
                                self.comp_input1
                            self.df_result_table[
                                comp['label'] + '_solar_input'] = \
                                self.comp_input2
                            self.df_result_table[
                                comp['label'] + '_heat_output'] = \
                                self.comp_output1
                            comp_label = comp['label']
                            capacity = round(self.comp_input2.max(), 2)
                    # transformers
                    elif i == "transformers":
                        comp_label = comp['label']
                        capacity = round(self.comp_output1.max(), 2)
                        if comp['transformer type'] == 'ExtractionTurbineCHP':
                            logging.info(
                                '   ' + 'WARNING: ExtractionTurbineCHP are '
                                + 'currently not a part of this model '
                                + 'generator, but will be added later.')

                        elif comp['transformer type'] == 'OffsetTransformer':
                            logging.info(
                                '   ' + 'WARNING: OffsetTransformer are '
                                + 'currently not a part of this model '
                                + 'generator, but will be added later.')

                        elif comp['transformer type'] == 'GenericTransformer' \
                                or comp['transformer type'] == 'GenericCHP':

                            self.df_result_table[comp['label'] + '_input'] = \
                                self.comp_input1
                            self.df_result_table[comp['label'] + '_output1'] =\
                                self.comp_output1

                            if comp['output2'] not in [0, 'None', 'none']:
                                self.df_result_table[
                                    comp['label'] + '_output2'] = \
                                    self.comp_output2

                        elif comp['transformer type'] == \
                                'CompressionHeatTransformer' or \
                                comp['transformer type'] == \
                                'AbsorptionHeatTransformer':

                            self.df_result_table[
                                comp['label'] + '_el_input'] = self.comp_input1
                            
                            transformer_type = comp['transformer type']
                            
                            if comp['transformer type'] == \
                                    'AbsorptionHeatTransformer':
                                self.df_result_table[
                                    comp['label'] + '_heat_input'] = \
                                    self.comp_input2
                            else:
                                self.df_result_table[
                                    comp['label'] + '_ambient_input'] = \
                                    self.comp_input2

                            if comp['mode'] == 'chiller':
                                self.df_result_table[
                                    comp['label'] + '_cooling_output'] = \
                                    self.comp_output1
                            if comp['mode'] == 'heat_pump':
                                self.df_result_table[
                                    comp['label'] + '_heat_output'] = \
                                    self.comp_output1
                    # storages
                    elif i == "storages":
                        comp_label = comp['label']
                        self.df_result_table[comp['label'] + '_capacity'] = \
                            self.comp_capacity
                        self.df_result_table[comp['label'] + '_input'] = \
                            self.comp_input1
                        self.df_result_table[comp['label'] + '_output'] = \
                            self.comp_output1
                        capacity = round(self.comp_capacity.max(), 2)

                    # links
                    elif i == "links":
                        comp_label = comp['label']
                        self.df_result_table[comp['label'] + '_input1'] = \
                            self.comp_input1
                        self.df_result_table[comp['label'] + '_output1'] = \
                            self.comp_output1
                        if comp['(un)directed'] == 'undirected':
                            self.df_result_table[comp['label'] + '_input2'] = \
                                self.comp_input2
                            self.df_result_table[comp['label'] + '_output2'] =\
                                self.comp_output2

                            capacity = round(max(self.comp_output1.max(),
                                                 self.comp_output2.max()), 2)
                        else:
                            capacity = round(self.comp_output1.max(), 2)
                    else:
                        raise ValueError("Error with technology" + i)
                    if i in ['buses_e', 'buses_s']:
                        if i == 'buses_e':
                            comp_type = 'sink'
                        else:
                            comp_type = 'source'
                    else:
                        comp_type = i[:-1]

                    if 'max. investment capacity' in comp:
                        if comp["max. investment capacity"] != "inf":
                            invest = round(comp['max. investment capacity'], 2)
                        else:
                            invest = "inf"
                    else:
                        invest = "---"
                    self.add_component_to_loc(
                        label=comp_label,
                        comp_type=comp_type,
                        capacity=capacity,
                        variable_costs=variable_costs,
                        periodical_costs=periodical_costs,
                        investment=investment,
                        maxinvest=invest,
                        constraints=constraint_costs)
                    if console_log:
                        self.console_logging(
                            comp_type=comp_type,
                            capacity=capacity,
                            variable_costs=variable_costs,
                            periodical_costs=periodical_costs,
                            investment=investment,
                            transformer_type=transformer_type)

                        self.insert_line_end_of_component()

        # TODO
        self.log_category("DISTRICT HEATING")
        results = self.results.copy()
        components = []
        for i in self.results.keys():
            if 'link-dhnx' not in str(i) and "tag1=" not in str(i) \
                    and "consumers_connection_dh" not in str(i) \
                    and "clustered_consumers" not in str(i):
                results.pop(i)
        for i in results.keys():
            if i[0] not in components:
                if i[0] is not None:
                    if "bus" not in str(i[0]):
                        components.append(i[0])
            if i[1] not in components:
                if i[1] is not None:
                    if "bus" not in str(i[1]) \
                            or str(type(i[1])) == "<class " \
                                                    "'oemof.solph.custom.link.Link'>":
                        components.append(i[1])
        for i in range(len(components)):
            if "clustered_consumer" in str(components[i]) \
                    and "-" not in str(components[i]):
                print("dummy")
            else:
                variable_costs = None
                constraint_costs = None
                transformer_type = None
                if console_log:
                    logging.info('   ' + str(components[i]))
                component = solph.views.node(self.results,
                                             str(components[i]))
                # create class intern dataframes consisting the flows
                # of given component
                self.create_flow_dataframes(component,
                                            district_heating=
                                            {"label": str(components[i])})
                investment = self.get_dh_investment(components[i])
                if investment > 0:
                    investments_to_be_made[str(components[i])] = \
                        (str(round(investment, 2)) + ' kW')
                if investment == 0 and type(investment) == int:
                    investment = None
                # get length of pipes
                length_list = []
                if self.comp_input1 is not None:
                    if "forks" in str(components[i]):
                        list = str(components[i]).split("-")
                        if "consumers" in str(components[i])[-11:]:
                            name = ("heatp.-"
                                    + str(list[1])
                                    + "-f{}".format(list[-3]) + "-to"
                                    + "-c{}".format(list[-1]))
                            length_list = ["forks-{}".format(list[-3]),
                                           "consumers-{}".format(list[-1])]
                        elif "producer" in str(components[i])[-19:-11]:
                            name = ("heatp.-"
                                    + str(list[1])
                                    + "-p{}".format(list[-3]) + "-to"
                                    + "-f{}".format(list[-1]))
                            length_list = ["producers-{}".format(list[-3]),
                                           "forks-{}".format(list[-1])]
                        else:
                            name = ("heatp.-"
                                    + str(list[1])
                                    + "-f{}".format(list[-3]) + "-to"
                                    + "-f{}".format(list[-1]))
                            length_list = ["forks-{}".format(list[-3]),
                                           "forks-{}".format(list[-1])]
                    else:
                        name = str(components[i])
                    self.df_result_table[
                        name + "-input"] = self.comp_input1
                else:
                    name = str(components[i])
                print(result_path)
                if length_list:
                    pipes = pd.read_csv(result_path + "/pipes_clustered.csv")  # TODO
                    for num, pipe in pipes.iterrows():
                        if pipe["from_node"] == length_list[0] \
                                and pipe["to_node"] == length_list[1]:
                            length = pipe["length"]

                # TODO linearisierter Kostenfaktor
                if "infrastructure" in str(components[i]) \
                        or "link-dhnx-c" in str(components[i]):
                    if investment == 0.0 and type(investment) != int:
                        if "link-dhnx-c" in str(components[i]):
                            #length = float(str(components[i]).split("-")[-1])
                            periodical_costs = investment * 2.6618 
                            constraint_costs = investment * 9.9918 
                        else:
                            periodical_costs = investment * 0.3103 * length
                            constraint_costs = investment * 1.8084 * length
                        total_periodical_costs += periodical_costs
                        total_constraint_costs += constraint_costs
                else:
                    periodical_costs = None
                
                if self.comp_output2 is not None:
                    self.df_result_table[
                        name + "-output"] = self.comp_output2
                if self.comp_input2 is not None:
                    self.df_result_table[
                        name + "-input2"] = self.comp_input2
                if "infrastructure" in str(components[i]):
                    self.comp_output1 = self.comp_output2.copy()
                    self.comp_output2 = None
                if self.comp_input1 is not None and self.comp_output1 is not None:
                    if self.comp_input1.sum() + self.comp_output1.sum() == 0.0:
                        capacity = None
                    else:
                        capacity = round(self.comp_input1.max(), 2)
                else:
                    capacity = None
                   
                self.add_component_to_loc(
                        label=name,
                        comp_type="d.-h.",
                        capacity=capacity,
                        variable_costs=variable_costs,
                        periodical_costs=periodical_costs,
                        investment=investment,
                        maxinvest='---',
                        constraints=constraint_costs)
                if console_log:
                    self.console_logging(
                            comp_type="district_heating",
                            capacity=round(self.comp_output1.max(), 2),
                            variable_costs=variable_costs,
                            periodical_costs=periodical_costs,
                            investment=investment,
                            transformer_type=transformer_type)
    
                    self.insert_line_end_of_component()
        # SUMMARY
        meta_results = solph.processing.meta_results(optimization_model)
        meta_results_objective = meta_results['objective']
        if console_log:
            self.log_category("SUMMARY")
            logging.info('   ' + 'Total System Costs:             '
                         + str(round(meta_results_objective, 1))
                         + ' cost units')
            logging.info('   ' + 'Total Constraint Costs:         '
                         + str(round(total_constraint_costs)) + ' cost units')
            logging.info('   ' + 'Total Variable Costs:           '
                         + str(round(total_variable_costs)) + ' cost units')
            logging.info('   ' + 'Total Periodical Costs (p.a.):  '
                         + str(round(total_periodical_costs))
                         + ' cost units p.a.')
            logging.info('   ' + 'Total Energy Demand:            '
                         + str(round(total_demand)) + ' kWh')
            logging.info('   ' + 'Total Energy Usage:             '
                         + str(round(total_usage)) + ' kWh')
            # creating the list of investments to be made
            self.insert_line_end_of_component()
            logging.info('   ' + 'Investments to be made:')
            investment_objects = list(investments_to_be_made.keys())
            for i in range(len(investment_objects)):
                logging.info('   - ' + investment_objects[i] + ': '
                             + investments_to_be_made[investment_objects[i]])
            logging.info('   ' + 56 * "*" + "\n")

        # Importing time system parameters from the scenario
        ts = next(nodes_data['energysystem'].iterrows())[1]
        temp_resolution = ts['temporal resolution']
        start_date = ts['start date']
        end_date = ts['end date']

        df_summary = pd.DataFrame(
            [[start_date, end_date, temp_resolution,
              round(meta_results_objective, 2),
              round(total_constraint_costs, 2),
              round(total_variable_costs, 2),
              round(total_periodical_costs, 2), round(total_demand, 2),
              round(total_usage, 2)]],
            columns=['Start Date', 'End Date', 'Resolution',
                     'Total System Costs', 'Total Constraint Costs',
                     'Total Variable Costs', 'Total Periodical Costs',
                     'Total Energy Demand', 'Total Energy Usage'])

        # Dataframes are exported as csv for further processing
        self.df_list_of_components.to_csv(result_path + '/components.csv',
                                          index=False)

        df_result_table = self.df_result_table.rename_axis('date')
        df_result_table.to_csv(result_path + '/results.csv')

        df_summary.to_csv(result_path + '/summary.csv', index=False)

        logging.info('   ' + 'Successfully prepared results...')
