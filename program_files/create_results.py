"""Functions for returning optimization results in several forms.

----
@ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
"""

import logging
import pandas as pd
from oemof import solph
from matplotlib import pyplot as plt
import os


def xlsx(nodes_data, optimization_model, filepath):
    """Returns model results as xlsx-files.
    Saves the in- and outgoing flows of every bus of a given,
    optimized energy system as .xlsx file
    
    ----
    
    Keyword arguments:
    
        nodes_data : obj:'dict'
            -- dictionary containing data from excel scenario file
        
        optimization_model
            -- optimized energy system
        
        filepath : obj:'str'
            -- path, where the results will be stored
    
    ----
    
    Returns:
        results : obj:'.xlsx'
            -- xlsx files containing in and outgoing flows of the energy
            systems' buses.
    
    ----
    @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
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


def charts(nodes_data, optimization_model, energy_system):
    """Plots model results.
    
    Plots the in- and outgoing flows of every bus of a given, optimized energy
    system
    
    ----
    
    Keyword arguments:
    
        nodes_data : obj:'dict'
            -- dictionary containing data from excel scenario file
        
        optimization_model
            -- optimized energy system
        
        energy_system : obj:
            -- original (unoptimized) energy system
    
    ----
    
    Returns:
        plots
            -- plots displaying in and outgoing flows of the energy
            systems' buses.
    
    ----
    @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
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

    def get_flow(self, comp_label, comp_type):
        """
            Calculates the flow and performance of the given component,
            then logs it in the output and returns it to the statistics
            method.
            ----
            Keyword arguments:
                
                comp_label: obj:'str'
                    -- label of component to be calculated
                comp_type: obj:'str'
                    -- type of component to be calculated
            ----
            Returns:
                flow_sum: -- sum of the of the calculated flow
                flow_max: -- maximum of the calculated flow
                df_component: -- component_performance(input or output)
        """
        logging.info('   ' + comp_label)
        # creates component by component_label
        component = solph.views.node(self.results, comp_label)
        # reads the flows of the given component
        flow_sum = component['sequences'].sum()
        flow_max = component['sequences'].max()
        # sets the performance of the given component
        component_performance = component['sequences'].columns.values
        df_component1 = component['sequences'][component_performance[0]]
        # Dictionary for the information of components to be logged
        comp_log = {'demand': [0, 0, 'Total Energy Demand: '],
                    'source': [0, 0, 'Total Energy Input: '],
                    'storage': [1, 0, 'Energy Output from: ']}
        if comp_type == 'demand' or comp_type == 'source' \
                or comp_type == 'storage':
            logging.info('   ' + comp_log[comp_type][2]
                         + str(round(flow_sum[[comp_log[comp_type][0]]
                                              [comp_log[comp_type][1]]], 2))
                         + 'kWh')
        if comp_type == 'source' or comp_type == 'storage':
            if comp_type == 'storage':
                logging.info('   ' + 'Energy Input to ' + comp_label + ': '
                             + str(round(flow_sum[[2][0]], 2)) + ' kWh')
            logging.info('   ' + 'Max. Capacity: '
                         + str(round(flow_max[[0][0]], 2)) + ' kW')
        # returns the parameters to the statistics method
        if comp_type == 'storage':
            return flow_sum[[0][0]]
        elif comp_type == 'demand' or comp_type == 'source':
            return flow_sum[[0][0]], df_component1
        elif comp_type == 'shortage':
            return flow_sum[[0][0]], flow_max[[0][0]], df_component1
        elif comp_type == 'link':
            df_link2 = component['sequences'][component_performance[1]]
            return flow_sum, flow_max, df_component1, df_link2
        elif comp_type == 'transformer':
            df_transformer2 = component['sequences'][component_performance[1]]
            df_transformer3 = component['sequences'][component_performance[2]]
            return (flow_sum, flow_max, df_component1, df_transformer2,
                    df_transformer3)

    def get_investment(self, component, comp_type):
        """
        Calculates the investment to be made and the resulting periodical
        costs.
        ----
        Keyword arguments:
            component: obj
                -- one component of the energy system with
                'max. investment' > 0
            comp_type: obj: 'str'
                -- type of the component to be calculated
        ----
        Returns:
            component_investment: obj: 'float'
                -- investment to be made
            periodical_costs: obj: 'float'
                -- periodic_costs resulting from the investment decision
        """
        component_node = self.esys.groups[component['label']]
        # defines bus_node for different components
        if comp_type == 'source':
            bus_node = self.esys.groups[component['output']]
        elif comp_type == 'storage':
            bus_node = None
        elif comp_type == 'link':
            bus_node = self.esys.groups[component['bus_2']]
        else:
            raise SystemError('Wrong type chosen!')
        # sets component investment
        component_investment = \
            (self.results[component_node, bus_node]['scalars']['invest'])
        # returns logging info
        logging.info('   ' + 'Investment Capacity: '
                     + str(component_investment) + ' kW')
        if comp_type == 'storage':
            # calculates the periodical costs
            periodical_costs = (component['periodical costs /(CU/(kWh a))'] *
                                component_investment)
        else:
            # calculates the periodical costs
            periodical_costs = (component['periodical costs /(CU/(kW a))'] *
                                component_investment)
        # logs periodical costs in system output
        logging.info('   ' + 'Periodical costs: '
                     + str(round(periodical_costs, 2))
                     + ' cost units p.a.')
        if comp_type == 'link':
            return component_investment
        else:
            return component_investment, periodical_costs

    def statistics(self, nodes_data, optimization_model, energy_system,
                   result_path):
        """
        Returns a list of all defined components with the following
        information:
        
        component   |   information
        ----------------------------------------------------------------
        sinks       |   Total Energy Demand
        sources     |   Total Energy Input, Max. Capacity,
                        Variable Costs, Periodical Costs
        transformers|   Total Energy Output, Max. Capacity,
                        Variable Costs, Investment Capacity,
                        Periodical Costs
        storages    |   Energy Output, Energy Input, Max. Capacity,
                        Total variable costs, Investment Capacity,
                        Periodical Costs
        links       |   Total Energy Output
        
        Furthermore, a list of recommended investments is printed.
        ----
        Keyword arguments:
        
            nodes_data : obj:'dict'
               -- dictionary containing data from excel scenario file
        
            optimization_model
                -- optimized energy system
        
            energy_system : obj:
                -- original (unoptimized) energy system
            
            result_path : obj: 'str'
                -- Path where the results are saved.
        ----
        @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
        """

        # renames input variables
        nd = nodes_data
        self.esys = energy_system
        om = optimization_model
        self.results = solph.processing.results(om)
        # columns of list of components
        columns = ['ID', 'type', 'input 1/kWh', 'input 2/kWh', 'output 1/kWh',
                   'output 2/kWh', 'capacity/kW', 'variable costs/CU',
                   'periodical costs/CU', 'investment/kW']

        df_list_of_components = pd.DataFrame(columns=columns)
        df_result_table = pd.DataFrame()
        log_end = \
            '   ' + '--------------------------------------------------------'

        ###################
        # Analyze Results #
        ###################
        total_usage = 0
        total_demand = 0
        total_costs = 0
        total_periodical_costs = 0
        investments_to_be_made = {}
        # logs the next type of components(sinks)
        log("SINKS********")
        # creates and returns results for sinks defined in the
        # sinks-sheet of the input spreadsheet
        for i, comp in nd['demand'].iterrows():
            if comp['active']:
                # gets the flow for the given sink
                (flow_sum, df_demand) = self.get_flow(comp['label'], 'demand')
                total_demand = total_demand + flow_sum
                df_result_table[comp['label']] = df_demand
                # adds the sink to the list of components
                df_list_of_components = \
                    df_list_of_components.append(
                        pd.DataFrame([[comp['label'], 'sink',
                                       round(df_demand.sum(), 2), '---', '---',
                                       '---', round(df_demand.max(), 2), '---',
                                       '---', '---']], columns=columns))
                # returns logging info
                logging.info(log_end)
        # creates and returns results for excess buses defined in the
        # buses-sheet of the input spreadsheet (excess sinks)
        for i, comp in nd['buses'].iterrows():
            if comp['active']:
                if comp['excess']:
                    (flow_sum, df_excess) = \
                        self.get_flow(comp['label'] + '_excess', 'demand')
                    total_usage = total_usage + flow_sum
                    # calculates the total variable costs of the sink
                    variable_costs = comp['excess costs /(CU/kWh)'] * flow_sum
                    # adds the variable costs to the total_costs variable
                    total_costs = total_costs + variable_costs
                    df_result_table[comp['label'] + '_excess'] = df_excess
                    # adds the bus to the list of components
                    df_list_of_components = \
                        df_list_of_components.append(
                            pd.DataFrame([[comp['label'] + '_excess',
                                           'sink', round(df_excess.sum(),
                                                         2),
                                           '---', '---', '---',
                                           round(df_excess.max(), 2),
                                           round(variable_costs, 2), '---',
                                           '---']], columns=columns))
                    # returns logging info
                    logging.info('   ' + 'Variable Costs: '
                                 + str(round(variable_costs, 2))
                                 + ' cost units')
                    logging.info(log_end)
        # logs the next type of components(sources)
        log("SOURCES******")
        # creates and returns results for sources defined in the
        # sources-sheet of the input spreadsheet
        for i, comp in nd['sources'].iterrows():
            if comp['active']:
                (flow_sum, df_source) = self.get_flow(comp['label'], 'source')
                # adds the flowsum to the total_usage variable
                total_usage = total_usage + flow_sum
                # continues, if the model decided to take a investment
                # decision for this source
                if comp['max. investment capacity /(kW)'] > 0:
                    # gets the investment for the given source
                    (component_investment, periodical_costs) = \
                        self.get_investment(comp, 'source')
                    # adds the investment to the investments_to_be_made
                    # list
                    investments_to_be_made[comp['label']] = \
                        (str(round(component_investment, 2)) + ' kW')
                    if component_investment > 0:
                        total_periodical_costs = (total_periodical_costs
                                                  + periodical_costs)
                        investments_to_be_made[comp['label']] = \
                            (str(component_investment)
                             + ' kW; ' + str(round(periodical_costs, 2))
                             + ' cost units (p.a.)')
                else:
                    periodical_costs = 0
                    component_investment = 0

                # Calculates Variable Costs, adds it to the total_cost
                # variable and returns logging info
                variable_costs = comp['variable costs /(CU/kWh)'] * flow_sum
                total_costs = total_costs + variable_costs
                logging.info('   ' + 'Variable costs: '
                             + str(round(variable_costs, 2)) + ' cost units')
                # Adds the components time series to the
                # df_component_flows data frame for further usage
                df_result_table[comp['label']] = df_source
                # adds the source to the list of components
                df_list_of_components = \
                    df_list_of_components.append(
                        pd.DataFrame([[comp['label'], 'source', '---',
                                       '---', round(df_source.sum(), 2),
                                       '---', round(df_source.max(), 2),
                                       round(variable_costs, 2),
                                       round(periodical_costs, 2),
                                       round(component_investment, 2)]],
                                     columns=columns))
                logging.info(log_end)
        for i, comp in nd['buses'].iterrows():
            if comp['active']:
                if comp['shortage']:
                    (flow_sum, flow_max, df_shortage) = \
                        self.get_flow(comp['label'] + '_shortage', 'shortage')
                    total_usage = total_usage + flow_sum
                    # Variable Costs
                    variable_costs = \
                        comp['shortage costs /(CU/kWh)'] * flow_sum
                    total_costs = total_costs + variable_costs
                    logging.info('   ' + 'Variable Costs: '
                                 + str(round(variable_costs, 2))
                                 + ' cost units')
                    # adds the bus to the list of components
                    df_list_of_components = \
                        df_list_of_components.append(
                            pd.DataFrame([[comp['label'] + '_shortage',
                                           'source', '---', '---',
                                           round(flow_sum, 2), '---',
                                           round(flow_max, 2),
                                           round(variable_costs, 2), '---',
                                           '---']], columns=columns))
                    df_result_table[comp['label'] + '_shortage'] = df_shortage
                    logging.info(log_end)
        # logs the next type of components
        log("TRANSFORMERS*")
        for i, comp in nd['transformers'].iterrows():
            variable_costs = 0
            max_transformer_flow = 0
            df_transformer3 = 0
            if comp['active']:
                if comp['output2'] != 'None' \
                        or comp['transformer type'] == 'HeatPump':
                    (flow_sum, flow_max, df_transformer1, df_transformer2,
                     df_transformer3) = \
                        self.get_flow(comp['label'], 'transformer')
                else:
                    (flow_sum, flow_max, df_transformer1, df_transformer2) = \
                        self.get_flow(comp['label'], 'link')
                if comp['transformer type'] == 'GenericTransformer' or \
                        comp['transformer type'] == 'GenericCHP':
                    transformer_log = {'GenericTransformer': [0, 1, 1],
                                       'GenericCHP': [6, 7, 2]}
                    if comp['output2'] != 'None':
                        pos1 = transformer_log[comp['transformer type']][0]
                        logging.info('   '
                                     + 'Total Energy Output to '
                                     + comp['output'] + ': '
                                     + str(round(flow_sum[[pos1][0]], 2))
                                     + ' kWh')
                        output = comp['output2']
                    else:
                        output = comp['output']
                    pos2 = transformer_log[comp['transformer type']][1]
                    logging.info('   '
                                 + 'Total Energy Output to ' + output + ': '
                                 + str(round(flow_sum[[pos2][0]], 2)) + ' kWh')
                    max_transformer_flow = \
                        flow_max[transformer_log[comp['transformer type']][2]]

                elif comp['transformer type'] == 'ExtractionTurbineCHP':
                    logging.info('   ' + 'WARNING: ExtractionTurbineCHP are'
                                 + ' currently not a part of this model '
                                 + 'generator, but will be added later.')

                elif comp['transformer type'] == 'HeatPump':
                    logging.info('   ' + 'Electricity Energy Input to '
                                 + comp['label'] + ': '
                                 + str(round(flow_sum[[2][0]], 2))
                                 + ' kWh')
                    logging.info('   ' + 'Ambient Energy Input to '
                                 + comp['label'] + ': '
                                 + str(round(flow_sum[[1][0]], 2))
                                 + ' kWh')
                    logging.info('   ' + 'Total Energy Output to '
                                 + comp['output'] + ': '
                                 + str(round(flow_sum[[0][0]], 2))
                                 + ' kWh')
                elif comp['transformer type'] == 'OffsetTransformer':
                    logging.info('   ' + 'WARNING: OffsetTransformer are '
                                 + 'currently not a part of this model '
                                 + 'generator, but will be added later.')

                logging.info('   ' + 'Max. Capacity: '
                             + str(round(max_transformer_flow, 2)) + ' kW')
                if comp['output2'] != 'None':
                    variable_costs = (comp['variable output costs 2 /(CU/kWh)']
                                      * df_transformer1.sum())
                    total_costs = total_costs + variable_costs
                variable_costs += (comp['variable input costs /(CU/kWh)']
                                   * (df_transformer3.sum()
                                      if comp['output2'] != 'None'
                                      else df_transformer1.sum()))
                variable_costs += \
                    (comp['variable output costs /(CU/kWh)']
                     * df_transformer2.sum())
                total_costs += variable_costs
                logging.info('   ' + 'Variable Costs: '
                             + str(round(variable_costs, 2)) + ' cost units')

                # Investment Capacity
                if comp['max. investment capacity /(kW)'] > 0:
                    # gets investment for given transformer
                    (transformer_investment, periodical_costs) = \
                        self.get_investment(comp, 'source')
                    logging.info('   ' + 'Investment Capacity: '
                                 + str(round(transformer_investment, 2))
                                 + ' kW')
                else:
                    transformer_investment = 0

                # Periodical Costs
                if transformer_investment > 0:
                    # max investment capacity * periodical costs
                    periodical_costs = (comp['periodical costs /(CU/(kW a))']
                                        * transformer_investment)
                    total_periodical_costs = (total_periodical_costs
                                              + periodical_costs)
                    investments_to_be_made[comp['label']] = \
                        (str(round(transformer_investment, 2)) + ' kW; '
                         + str(round(periodical_costs, 2))
                         + ' cost units (p.a.)')
                else:
                    periodical_costs = 0
                logging.info('   ' + 'Periodical costs (p.a.): '
                             + str(round(periodical_costs, 2))
                             + ' cost units p.a.')
                if comp['transformer type'] == 'GenericTransformer':
                    df_result_table[comp['label'] + '_input1'] = \
                        df_transformer3 if comp['output2'] != 'None' \
                        else df_transformer1
                    df_result_table[comp['label'] + '_output1'] = \
                        df_transformer2
                    if comp['output2'] == 'None':
                        # adds Generic transformer with one given
                        # outputs to the list of components
                        df_list_of_components = \
                            df_list_of_components.append(
                                pd.DataFrame([[comp['label'], 'transformer',
                                               round(df_transformer1.sum(),
                                                     2), '---',
                                               round(df_transformer2.sum(),
                                                     2), '---',
                                               round(df_transformer1.max(),
                                                     2),
                                               round(variable_costs, 2),
                                               round(periodical_costs, 2),
                                               round(transformer_investment, 2)
                                               ]], columns=columns))
                    else:
                        # adds Generic transformer with two given
                        # outputs to the list of components
                        df_result_table[comp['label'] + '_output2'] = \
                            df_transformer1
                        df_list_of_components = \
                            df_list_of_components.append(
                                pd.DataFrame([[comp['label'], 'transformer',
                                               round(df_transformer3.sum(), 2),
                                               '---',
                                               round(df_transformer2.sum(), 2),

                                               round(df_transformer1.sum(), 2),
                                               round(df_transformer1.max(), 2),
                                               round(variable_costs, 2),
                                               round(periodical_costs, 2),
                                               round(transformer_investment, 2)
                                               ]], columns=columns))
                elif comp['transformer type'] == 'HeatPump':
                    df_result_table[comp['label'] + '_input2'] = \
                        df_transformer3
                    # adds heatpump transformer to the list of
                    # components
                    df_list_of_components = \
                        df_list_of_components.append(
                            pd.DataFrame([[comp['label'], 'transformer',
                                           round(df_transformer2.sum(), 2),
                                           round(df_transformer3.sum(), 2),
                                           round(df_transformer1.sum(), 2),
                                           '---',
                                           round(df_transformer1.max(), 2),
                                           round(variable_costs, 2),
                                           round(periodical_costs, 2),
                                           round(transformer_investment, 2)
                                           ]],
                                         columns=columns))

                elif comp['transformer type'] == 'GenericCHP':
                    # adds genericchp transformer to the list of
                    # components
                    df_list_of_components = \
                        df_list_of_components.append(
                            pd.DataFrame([[comp['label'], 'transformer', '---',
                                           '---', round(flow_sum[[6][0]], 2),
                                           round(flow_sum[[7][0]], 2), '---',
                                           round(variable_costs, 2),
                                           round(periodical_costs, 2),
                                           round(transformer_investment, 2)
                                           ]], columns=columns))
                logging.info(log_end)
        # logs the next type of components
        log("STORAGES*****")
        for i, comp in nd['storages'].iterrows():
            if comp['active']:
                # gets component flow and performance for given storages
                (flow_sum, flow_max, df_storage1, df_storage2, df_storage3) = \
                    self.get_flow(comp['label'], 'transformer')
                variable_costs = \
                    comp['variable input costs'] * flow_sum[[0][0]]
                logging.info('   ' + 'Total variable costs for: '
                             + str(round(variable_costs, 2))
                             + ' cost units')
                total_costs = total_costs + variable_costs
                # Investment Capacity
                if comp['max. investment capacity /(kWh)'] > 0:
                    # gets investment and periodical cost for given
                    # storage
                    (storage_investment, periodical_costs) = \
                        self.get_investment(comp, 'storage')
                else:
                    # if no investment decision has been taken
                    storage_investment = 0
                    periodical_costs = 0

                # Periodical Costs
                if storage_investment \
                        > float(comp['existing capacity /(kWh)']):
                    total_periodical_costs = (total_periodical_costs
                                              + periodical_costs)
                    investments_to_be_made[comp['label']] = \
                        (str(round(storage_investment, 2)) + ' kWh; '
                         + str(round(periodical_costs, 2)) +
                         ' cost units (p.a.)')
                df_list_of_components = \
                    df_list_of_components.append(
                        pd.DataFrame([[comp['label'], 'storage',
                                       round(flow_sum[[2][0]], 2), '---',
                                       round(flow_sum[[1][0]], 2), '---',
                                       round(flow_max[[0][0]], 2),
                                       round(variable_costs, 2),
                                       round(periodical_costs, 2),
                                       round(storage_investment, 2)]],
                                     columns=columns))
                df_result_table[comp['label'] + '_capacity'] = df_storage1
                df_result_table[comp['label'] + '_input'] = df_storage3
                df_result_table[comp['label'] + '_output'] = df_storage2
                logging.info(log_end)
        # logs the next type of components (links
        log("LINKS********")
        for i, comp in nd['links'].iterrows():
            variable_costs = 0
            if comp['active']:
                (flow_sum, flow_max, df_link1, df_link2) = \
                    self.get_flow(comp['label'], 'link')
                if comp['(un)directed'] == 'directed':
                    logging.info('   ' + 'Total Energy Output to '
                                 + comp['bus_2'] + ': '
                                 + str(round(flow_sum[[1][0]], 2)) + ' kWh')
                    max_link_flow = flow_max[1]
                    logging.info('   ' + 'Max. Capacity to ' + comp['bus_2']
                                 + ': ' + str(round(max_link_flow, 2)) + ' kW')
                    # TODO Implemented correctly ? variable costs for
                    # TODO second output
                else:
                    (flow_sum2, flow_max2, df_link1_2, df_link2_2) = \
                        self.get_flow(comp['label'] + '_direction_2', 'link')
                    logging.info('   ' + 'Total Energy Output to '
                                 + comp['bus_2'] + ': '
                                 + str(round(flow_sum[[1][0]], 2)) + ' kWh')
                    logging.info('   ' + 'Total Energy Output to '
                                 + comp['bus_1'] + ': '
                                 + str(round(flow_sum2[[1][0]], 2)) + ' kWh')
                    max_link_flow = flow_max[1]
                    logging.info('   ' + 'Max. Capacity to ' + comp['bus_2']
                                 + ': ' + str(round(max_link_flow, 2)) + ' kW')
                    max_link_flow = flow_max2[1]
                    logging.info('   ' + 'Max. Capacity to ' + comp['bus_1']
                                 + ': ' + str(round(max_link_flow, 2)) + ' kW')
                    variable_costs += \
                        comp['variable costs /(CU/kWh)'] * flow_sum2[[0][0]]
                variable_costs += \
                    comp['variable costs /(CU/kWh)'] * flow_sum[[0][0]]

                total_costs = total_costs + variable_costs
                logging.info('   ' + 'Variable Costs: '
                             + str(round(variable_costs, 2))
                             + ' cost units')

                # Investment Capacity
                if comp['max. investment capacity /(kW)'] > 0:
                    # get investment for the given link
                    link_investment = self.get_investment(comp, 'link')
                    logging.info('   ' + 'Investment Capacity: '
                                 + str(round(link_investment, 2))
                                 + ' kW')
                else:
                    # if no investment decision has been taken
                    link_investment = 0

                # Periodical Costs
                if link_investment > 0:
                    # TODO Issue #37
                    periodical_costs = comp['periodical costs /(CU/(kW a))']
                    total_periodical_costs = \
                        (total_periodical_costs + periodical_costs)
                    investments_to_be_made[comp['label']] = \
                        (str(round(link_investment, 2)) + ' kW; '
                         + str(round(periodical_costs, 2))
                         + ' cost units (p.a.)')
                else:
                    periodical_costs = 0
                logging.info('   ' + 'Periodical costs (p.a.): '
                             + str(round(periodical_costs, 2))
                             + ' cost units p.a.')

                df_result_table[comp['label'] + '_input1'] = df_link2
                df_result_table[comp['label'] + '_output1'] = df_link1
                if comp['(un)directed'] == 'directed':
                    df_list_of_components = \
                        df_list_of_components.append(
                            pd.DataFrame([[comp['label'], 'link',
                                           round(df_link2.sum(), 2), '---',
                                           round(df_link1.sum(), 2), '---',
                                           round(df_link2.max(), 2),
                                           round(variable_costs, 2),
                                           round(periodical_costs, 2),
                                           round(link_investment, 2)]],
                                         columns=columns))
                else:
                    df_result_table[comp['label'] + '_input2'] = df_link1_2
                    df_result_table[comp['label'] + '_output2'] = df_link2_2
                    df_list_of_components = \
                        df_list_of_components.append(
                            pd.DataFrame([[comp['label'], 'link',
                                           round(df_link1.sum(), 2),
                                           round(df_link1_2.sum(), 2),
                                           round(df_link2.sum(), 2),
                                           round(df_link2_2.sum(), 2),
                                           round(max(df_link2.max(),
                                                     df_link2_2.max()), 2),
                                           round(variable_costs, 2),
                                           round(periodical_costs, 2),
                                           round(link_investment, 2)]],
                                         columns=columns))
            logging.info(log_end)
        log("SUMMARY")
        meta_results = solph.processing.meta_results(om)
        meta_results_objective = meta_results['objective']
        logging.info('   ' + 'Total System Costs:             '
                     + str(round(meta_results_objective, 1))
                     + ' cost units')
        logging.info('   ' + 'Total Variable Costs:           '
                     + str(round(total_costs)) + ' cost units')
        logging.info('   ' + 'Total Periodical Costs (p.a.):  '
                     + str(round(total_periodical_costs))
                     + ' cost units p.a.')
        logging.info('   ' + 'Total Energy Demand:            '
                     + str(round(total_demand)) + ' kWh')
        logging.info('   ' + 'Total Energy Usage:             '
                     + str(round(total_usage)) + ' kWh')
        logging.info('   ' + '------------------------------------------------'
                     + '---------')
        logging.info('   ' + 'Investments to be made:')

        investment_objects = list(investments_to_be_made.keys())
        # Importing timesystem parameters from the scenario
        ts = next(nd['timesystem'].iterrows())[1]
        temp_resolution = ts['temporal resolution']
        start_date = ts['start date']
        end_date = ts['end date']

        df_summary = pd.DataFrame([[start_date,
                                    end_date,
                                    temp_resolution,
                                    round(meta_results_objective, 2),
                                    round(total_costs, 2),
                                    round(total_periodical_costs, 2),
                                    round(total_demand, 2),
                                    round(total_usage, 2)
                                    ]],
                                  columns=['Start Date',
                                           'End Date',
                                           'Resolution',
                                           'Total System Costs',
                                           'Total Variable Costs',
                                           'Total Periodical Costs',
                                           'Total Energy Demand',
                                           'Total Energy Usage'])
        for i in range(len(investment_objects)):
            logging.info('   ' + investment_objects[i] + ': '
                         + investments_to_be_made[investment_objects[i]])
        logging.info(
            '   ' + '-----------------------------------------------------'
            + '----')
        logging.info(
            '   ' + "*****************************************************"
            + "****\n")
        # Dataframes are exported as csv for further processing
        df_list_of_components.to_csv(result_path + '/components.csv',
                                     index=False)

        df_result_table = df_result_table.rename_axis('date')
        df_result_table.to_csv(result_path + '/results.csv')

        df_summary.to_csv(result_path + '/summary.csv', index=False)

        logging.info('   ' + 'Successfully prepared results...')

    def __init__(self, nodes_data, optimization_model, energy_system,
                 result_path):
        """
            Inits the Results class for preparing Plotly results and
            logging the results of Cbc-Solver.
            
            ----
            Keyword arguments:
                
                nodes_data: obj:'dict'
                    -- dictionary containing data from excel scenario
                    file.
                optimization_model: -- optimized energy system
                energy_system: obj:
                    -- original (unoptimized) energy system
                result_path:
                    -- Path where the results are saved.
        """
        self.statistics(nodes_data, optimization_model, energy_system,
                        result_path)


def log(component):
    """
    Returns logging info for type of given components.
    ----
    Keyword arguments:
         component: obj: 'str'
         -- component type
    """
    # returns logging infos
    logging.info(
        '   ' + "********************************************************")
    logging.info(
        '   ' + "***" + component + "****************************************")
    logging.info(
        '   ' + "********************************************************")
    logging.info(
        '   ' + '--------------------------------------------------------')
