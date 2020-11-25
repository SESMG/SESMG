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
    
    def getflow(self, componentlabel, type):
        """
            Calculates the flow and performance of the given component,
            then logs it in the output and returns it to the statistics
            method.
            ----
            Keyword arguments:
                
                componentlabel: obj:'str'
                    -- label of component to be calculated
                type: obj:'str'
                    -- type of component to be calculated
            ----
            Returns:
                flowsum: -- sum of the of the calculated flow
                flowmax: -- maximum of the calculated flow
                df_component: -- component_performance(input or output)
        """
        logging.info('   ' + componentlabel)
        # creates component by componentlabel
        component = solph.views.node(self.results, componentlabel)
        # reads the flows of the given component
        flowsum = component['sequences'].sum()
        flowmax = component['sequences'].max()
        # sets the performance of the given component
        component_performance = component['sequences'].columns.values
        df_component1 = component['sequences'][component_performance[0]]
        # Dictionary for the information of components to be logged
        component_log = {'demand': [0, 0, 'Total Energy Demand: '],
                         'busexcess': [0, 0, 'Total Energy Input: '],
                         'storage': [1, 0, 'Energy Output from: ']}
        if type == 'demand' or type == 'busexcess' or type == 'storage':
            logging.info('   ' + component_log[type][2]
                         + str(round(
                                    flowsum[[component_log[type][0]]
                                            [component_log[type][1]]], 2))
                         + 'kWh')
        if type == 'busexcess' or type == 'storage':
            if type == 'storage':
                logging.info('   ' + 'Energy Input to ' + componentlabel + ': '
                             + str(round(flowsum[[2][0]], 2)) + ' kWh')
            logging.info('   ' + 'Max. Capacity: '
                         + str(round(flowmax[[0][0]], 2)) + ' kW')
        # returns the parameters to the statistics method
        if type == 'demand' or type == 'busexcess':
            return flowsum[[0][0]], df_component1
        elif type == 'storage':
            return flowsum[[0][0]]
        elif type == 'transformer':
            df_transformer2 = component['sequences'][component_performance[1]]
            df_transformer3 = component['sequences'][component_performance[2]]
            return (flowsum, flowmax, df_component1, df_transformer2,
                    df_transformer3)
        elif type == 'shortage':
            return flowsum[[0][0]], flowmax[[0][0]], df_component1
        elif type == 'link':
            df_link2 = component['sequences'][component_performance[1]]
            return flowsum, flowmax, df_component1, df_link2

    def get_Investment(self, component, type):
        """
        Calculates the investment to be made and the resulting periodical
        costs.
        ----
        Keyword arguments:
            component: obj
                -- one component of the energy system with
                'max. investment' > 0
            type: obj: 'str'
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
        if type == 'source':
            bus_node = self.esys.groups[component['output']]
        elif type == 'storage':
            bus_node = None
        elif type == 'link':
            bus_node = self.esys.groups[component['bus_2']]
        else:
            raise SystemError('Wrong type chosen!')
        # sets component investment
        component_investment = \
            (self.results[component_node, bus_node]['scalars']['invest'])
        # returns logging info
        logging.info('   ' + 'Investment Capacity: '
                     + str(component_investment) + ' kW')
        if type == 'storage':
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
        if type == 'link':
            return component_investment
        else:
            return component_investment, periodical_costs

    def log(self, component):
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
            '   ' + "***"+component+"****************************************")
        logging.info(
            '   ' + "********************************************************")
        logging.info(
            '   ' + '--------------------------------------------------------')

    def statistics(self, nodes_data, optimization_model, energy_system,
                   result_path):
        """
        Returns a list of all defined components with the following information:
        
        component   |   information
        ---------------------------------------------------------------------------
        sinks       |   Total Energy Demand
        sources     |   Total Energy Input, Max. Capacity, Variable Costs,
                        Periodical Costs
        transformers|   Total Energy Output, Max. Capacity, Variable Costs,
                        Investment Capacity, Periodical Costs
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
        columns = ['ID',
                   'type',
                   'input 1/kWh',
                   'input 2/kWh',
                   'output 1/kWh',
                   'output 2/kWh',
                   'capacity/kW',
                   'variable costs/CU',
                   'periodical costs/CU',
                   'investment/kW']

        df_list_of_components = pd.DataFrame(columns=columns)
        df_result_table = pd.DataFrame()

        ###################
        # Analyze Results #
        ###################
        total_usage = 0
        total_demand = 0
        total_costs = 0
        total_periodical_costs = 0
        investments_to_be_made = {}
        # logs the next type of components(sinks)
        self.log("SINKS       ")
        # creates and returns results for sinks defined in the
        # sinks-sheet of the input spreadsheet
        for i, de in nd['demand'].iterrows():
            if de['active']:
                # gets the flow for the given sink
                (flowsum, df_demand) = self.getflow(de['label'], 'demand')
                total_demand = total_demand + flowsum
                df_result_table[de['label']] = df_demand
                # adds the sink to the list of components
                df_list_of_components = \
                    df_list_of_components.append(
                        pd.DataFrame([[de['label'], 'sink',
                                       round(df_demand.sum(), 2),
                                       '---', '---', '---',
                                       round(df_demand.max(), 2),
                                       '---', '---', '---']],
                                     columns=columns))
                # returns logging info
                logging.info(
                    '   ' + '------------------------------------------------')
        # creates and returns results for sinks defined in the
        # buses-sheet of the input spreadsheet (excess sinks)
        for i, b in nd['buses'].iterrows():
            if b['active']:
                if b['excess']:
                    (flowsum, df_excess) = \
                        self.getflow(b['label'] + '_excess', 'demand')
                    total_usage = total_usage + flowsum
                    # calculates the total variable costs of the sink
                    variable_costs = b['excess costs /(CU/kWh)'] * flowsum
                    # adds the variable costs to the total_costs variable
                    total_costs = total_costs + variable_costs
                    df_result_table[b['label'] + '_excess'] = df_excess
                    # adds the bus to the list of components
                    df_list_of_components = \
                        df_list_of_components.append(
                                pd.DataFrame([[b['label'] + '_excess', 'sink',
                                               round(df_excess.sum(), 2),
                                               '---', '---', '---',
                                               round(df_excess.max(), 2),
                                               round(variable_costs, 2),
                                               '---', '---']],
                                             columns=columns))
                    # returns logging info
                    logging.info('   ' + 'Variable Costs: '
                                 + str(round(variable_costs, 2))
                                 + ' cost units')
                    logging.info(
                            '   ' + '-----------------------------------------'
                            + '---------------')
        # logs the next type of components(sources)
        self.log("SOURCES     ")
        # creates and returns results for sources defined in the
        # sources-sheet of the input spreadsheet
        for i, so in nd['sources'].iterrows():
            if so['active']:
                (flowsum, df_source) = self.getflow(so['label'], 'busexcess')
                # adds the flowsum to the total_usage variable
                total_usage = total_usage + flowsum
                # continues, if the model decided to take a investment
                # decision for this source
                if so['max. investment capacity /(kW)'] > 0:
                    # gets the investment for the given source
                    (component_investment, periodical_costs) = \
                        self.get_Investment(so, 'source')
                    # adds the investment to the investments_to_be_made
                    # list
                    investments_to_be_made[so['label']] = \
                        (str(round(component_investment, 2)) + ' kW')
                    if component_investment > 0:
                        total_periodical_costs = (total_periodical_costs
                                                  + periodical_costs)
                        investments_to_be_made[so['label']] = \
                            (str(component_investment)
                             + ' kW; ' + str(round(periodical_costs, 2))
                             + ' cost units (p.a.)')
                else:
                    periodical_costs = 0
                    component_investment = 0

                # Calculates Variable Costs, adds it to the total_cost
                # variable and returns logging info
                variable_costs = so['variable costs /(CU/kWh)'] * flowsum
                total_costs = total_costs + variable_costs
                logging.info('   ' + 'Variable costs: '
                             + str(round(variable_costs, 2)) + ' cost units')
                # Adds the components time series to the
                # df_component_flows data frame for further usage
                df_result_table[so['label']] = df_source
                # adds the source to the list of components
                df_list_of_components = \
                    df_list_of_components.append(
                            pd.DataFrame([[so['label'], 'source',
                                           '---', '---',
                                           round(df_source.sum(), 2), '---',
                                           round(df_source.max(), 2),
                                           round(variable_costs, 2),
                                           round(periodical_costs, 2),
                                           round(component_investment, 2)]],
                                         columns=columns))
                logging.info(
                        '   ' + '---------------------------------------------'
                        + '----')
        for i, b in nd['buses'].iterrows():
            if b['active']:
                if b['shortage']:
                    (flowsum, flowmax, df_shortage) = \
                        self.getflow(b['label'] + '_shortage', 'shortage')
                    total_usage = total_usage + flowsum
                    # Variable Costs
                    variable_costs = b['shortage costs /(CU/kWh)'] * flowsum
                    total_costs = total_costs + variable_costs
                    logging.info('   ' + 'Variable Costs: '
                                 + str(round(variable_costs, 2))
                                 + ' cost units')
                    # adds the bus to the list of components
                    df_list_of_components = \
                        df_list_of_components.append(
                                pd.DataFrame([[b['label'] + '_shortage',
                                               'source', '---', '---',
                                               round(flowsum, 2), '---',
                                               round(flowmax, 2),
                                               round(variable_costs, 2),
                                               '---', '---']],
                                             columns=columns))
                    
                    df_result_table[b['label'] + '_shortage'] = df_shortage
                    logging.info(
                            '   ' + '-----------------------------------------'
                            + '---------------')
        # logs the next type of components
        self.log("TRANSFORMERS")
        for i, t in nd['transformers'].iterrows():
            variable_costs = 0
            if t['active']:
                if t['output2'] != 'None':
                    (flowsum, flowmax, df_transformer1, df_transformer2,
                     df_transformer3) = \
                        self.getflow(t['label'], 'transformer')
                else:
                    (flowsum, flowmax, df_transformer1, df_transformer2) = \
                        self.getflow(t['label'], 'link')
                if t['transformer type'] == 'GenericTransformer' or \
                        t['transformer type'] == 'GenericCHP':
                    transformer_log = {'GenericTransformer': [0, 1, 1],
                                       'GenericCHP': [6, 7, 2]}
                    if t['output2'] != 'None':
                        # TODO potential for Optimization within the use of get
                        # TODO Flow
                        logging.info('   ' + 'Total Energy Output to '
                                     + t['output'] + ': '
                                     + str(round(
                                        flowsum[
                                            [transformer_log[t['transformer type']]
                                                        [0]][0]], 2))
                                     + ' kWh')
                        output = t['output2']
                    else:
                        output = t['output']
                    logging.info('   ' + 'Total Energy Output to ' + output
                                 + ': ' + str(round(
                                                 flowsum[
                                                     [transformer_log
                                                      [t['transformer type']]
                                                        [1]][0]], 2))
                                 + ' kWh')
                    max_transformer_flow = \
                        flowmax[transformer_log[t['transformer type']][2]]

                elif t['transformer type'] == 'ExtractionTurbineCHP':
                    logging.info('   ' + 'WARNING: ExtractionTurbineCHP are'
                                 + ' currently not a part of this model '
                                 + 'generator, but will be added later.')
                # TODO Implemented correctly ? s.o.
                # elif t['transformer type'] == 'GenericCHP':
                #    logging.info('   ' + 'Total Energy Output to '
                # + t['output'] + ': '
                # + str(round(flowsum[[6][0]], 2))
                # + ' kWh')
                #    logging.info('   ' + 'Total Energy Output to '
                # + t['output2'] + ': '
                # + str(round(flowsum[[7][0]], 2))
                # + ' kWh')
                #   max_transformer_flow = flowmax[2]
                    
                elif t['transformer type'] == 'HeatPump':
                    logging.info('   ' + 'Electricity Energy Input to '
                                 + t['label'] + ': '
                                 + str(round(flowsum[[2][0]], 2))
                                 + ' kWh')
                    logging.info('   ' + 'Ambient Energy Input to '
                                 + t['label'] + ': '
                                 + str(round(flowsum[[1][0]], 2))
                                 + ' kWh')
                    logging.info('   ' + 'Total Energy Output to '
                                 + t['output'] + ': '
                                 + str(round(flowsum[[0][0]], 2))
                                 + ' kWh')
                elif t['transformer type'] == 'OffsetTransformer':
                    logging.info('   ' + 'WARNING: OffsetTransformer are '
                                 + 'currently not a part of this model '
                                 + 'generator, but will be added later.')
                
                logging.info('   ' + 'Max. Capacity: '
                             + str(round(max_transformer_flow, 2))
                             + ' kW')
                if t['output2'] != 'None':
                    variable_costs = (t['variable output costs 2 /(CU/kWh)']
                                      * df_transformer1.sum())
                    total_costs = total_costs + variable_costs
                variable_costs+=(t['variable input costs /(CU/kWh)'] * df_transformer3.sum() if t['output2'] != 'None' else df_transformer1.sum())
                variable_costs+=(t['variable output costs /(CU/kWh)'] * df_transformer2.sum())
                total_costs += variable_costs
                logging.info('   ' + 'Variable Costs: '
                             + str(round(variable_costs, 2))
                             + ' cost units')

                # Investment Capacity
                if t['max. investment capacity /(kW)'] > 0:
                    # gets investment for given transformer
                    (transformer_investment, periodical_costs) = \
                        self.get_Investment(t, 'source')
                    logging.info('   ' + 'Investment Capacity: '
                                 + str(round(transformer_investment, 2))
                                 + ' kW')
                else:
                    transformer_investment = 0

                # Periodical Costs
                if transformer_investment > 0:
                    # max investment capacity * periodical costs
                    periodical_costs = (t['periodical costs /(CU/(kW a))']
                                        * transformer_investment)
                    total_periodical_costs = (total_periodical_costs
                                              + periodical_costs)
                    investments_to_be_made[t['label']] = \
                        (str(round(transformer_investment, 2)) + ' kW; '
                         + str(round(periodical_costs, 2))
                         + ' cost units (p.a.)')
                else:
                    periodical_costs = 0
                logging.info('   ' + 'Periodical costs (p.a.): '
                             + str(round(periodical_costs, 2))
                             + ' cost units p.a.')
                if t['transformer type'] == 'GenericTransformer':
                    df_result_table[t['label'] + '_input1'] = df_transformer3 \
                        if t['output2'] != 'None' else df_transformer1
                    df_result_table[t['label'] + '_output1'] = df_transformer2
                    if t['output2'] == 'None':
                        # adds Generic transformer with one given
                        # outputs to the list of components
                        df_list_of_components = \
                            df_list_of_components.append(
                                    pd.DataFrame([[t['label'], 'transformer',
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
                        df_result_table[t['label'] + '_output2'] = \
                            df_transformer1
                        df_list_of_components = \
                            df_list_of_components.append(
                                    pd.DataFrame([[t['label'], 'transformer',
                                                   round(df_transformer3.sum(),2),
                                                    '---',
                                                   round(df_transformer2.sum(),2),
                                                   
                                                   round(df_transformer1.sum(),2),
                                                   round(df_transformer1.max(),
                                                         2),
                                                   round(variable_costs, 2),
                                                   round(periodical_costs, 2),
                                                   round(transformer_investment, 2)
                                                   ]], columns=columns))
                elif t['transformer type'] == 'HeatPump':
                    df_result_table[t['label'] + '_input2'] = df_transformer3
                    # adds heatpump transformer to the list of
                    # components
                    df_list_of_components = \
                        df_list_of_components.append(
                                pd.DataFrame([[t['label'], 'transformer',
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
                       
                elif t['transformer type'] == 'GenericCHP':
                    # adds genericchp transformer to the list of
                    # components
                    df_list_of_components = \
                        df_list_of_components.append(
                                pd.DataFrame([[t['label'], 'transformer', 'nn',
                                               'nn',
                                               round(flowsum[[6][0]], 2),
                                               round(flowsum[[7][0]], 2), 'nn',
                                               round(variable_costs, 2),
                                               round(periodical_costs, 2),
                                               round(transformer_investment, 2)
                                               ]], columns=columns))
                logging.info(
                        '   ' + '---------------------------------------------'
                        + '----')
        # logs the next type of components
        self.log("STORAGES")
        for i, s in nd['storages'].iterrows():
            if s['active']:
                # gets component flow and performance for given storages
                (flowsum, flowmax, df_storage1, df_storage2, df_storage3) = \
                    self.getflow(s['label'], 'transformer')
                variable_costs = s['variable input costs'] * flowsum[[0][0]]
                logging.info('   ' + 'Total variable costs for: '
                             + str(round(variable_costs, 2))
                             + ' cost units')
                total_costs = total_costs + variable_costs
                # Investment Capacity
                if s['max. investment capacity /(kWh)'] > 0:
                    # gets investment and periodical cost for given
                    # storage
                    (storage_investment, periodical_costs) = \
                        self.get_Investment(s, 'storage')
                else:
                    # if no investment decision has been taken
                    storage_investment = 0
                    periodical_costs = 0

                # Periodical Costs
                if storage_investment > float(s['existing capacity /(kWh)']):
                    total_periodical_costs = (total_periodical_costs
                                              + periodical_costs)
                    investments_to_be_made[s['label']] = \
                        (str(round(storage_investment, 2)) + ' kWh; '
                         + str(round(periodical_costs, 2)) +
                         ' cost units (p.a.)')
                df_list_of_components = \
                    df_list_of_components.append(
                            pd.DataFrame([[s['label'], 'storage',
                                           round(flowsum[[2][0]], 2), '---',
                                           round(flowsum[[1][0]], 2), '---',
                                           round(flowmax[[0][0]], 2),
                                           round(variable_costs, 2),
                                           round(periodical_costs, 2),
                                           round(storage_investment, 2)]],
                                         columns=columns))
                df_result_table[s['label'] + '_capacity'] = df_storage1
                df_result_table[s['label'] + '_input'] = df_storage3
                df_result_table[s['label'] + '_output'] = df_storage2
                logging.info(
                        '   ' + '---------------------------------------------'
                        + '----')
        # logs the next type of components (links
        self.log("LINKS")
        for i, p in nd['links'].iterrows():
            variable_costs = 0
            if p['active']:
                (flowsum, flowmax, df_link1, df_link2) = \
                    self.getflow(p['label'], 'link')
                if p['(un)directed'] == 'directed':
                    logging.info('   ' + 'Total Energy Output to '
                                 + p['bus_2'] + ': '
                                 + str(round(flowsum[[1][0]], 2)) + ' kWh')
                    max_link_flow = flowmax[1]
                    logging.info('   ' + 'Max. Capacity to ' + p['bus_2']
                                 + ': ' + str(round(max_link_flow, 2)) + ' kW')
                    # TODO Implemented correctly ? variable costs for
                    # TODO second output
                else:
                    (flowsum2, flowmax2, df_link1_2, df_link2_2) = \
                        self.getflow(p['label'] + '_direction_2', 'link')
                    logging.info('   ' + 'Total Energy Output to ' + p['bus_2']
                                 + ': ' + str(round(flowsum[[1][0]], 2))
                                 + ' kWh')
                    logging.info('   ' + 'Total Energy Output to ' + p['bus_1']
                                 + ': ' + str(round(flowsum2[[1][0]], 2))
                                 + ' kWh')
                    max_link_flow = flowmax[1]
                    logging.info('   ' + 'Max. Capacity to ' + p['bus_2']
                                 + ': ' + str(round(max_link_flow, 2)) + ' kW')
                    max_link_flow = flowmax2[1]
                    logging.info('   ' + 'Max. Capacity to ' + p['bus_1']
                                 + ': ' + str(round(max_link_flow, 2)) + ' kW')
                    variable_costs += p['variable costs /(CU/kWh)'] * \
                                      flowsum2[[0][0]]
                variable_costs += p['variable costs /(CU/kWh)'] * \
                                 flowsum[[0][0]]
                
                total_costs = total_costs + variable_costs
                logging.info('   ' + 'Variable Costs: '
                             + str(round(variable_costs, 2))
                             + ' cost units')

                # Investment Capacity
                if p['max. investment capacity /(kW)'] > 0:
                    # get investment for the given link
                    link_investment = self.get_Investment(p, 'link')
                    logging.info('   ' + 'Investment Capacity: '
                                 + str(round(link_investment, 2))
                                 + ' kW')
                else:
                    # if no investment decision has been taken
                    link_investment = 0

                # Periodical Costs
                if link_investment > 0:
                    # TODO Issue #37
                    periodical_costs = p['periodical costs /(CU/(kW a))']
                    total_periodical_costs = \
                        (total_periodical_costs + periodical_costs)
                    investments_to_be_made[p['label']] = \
                        (str(round(link_investment, 2)) + ' kW; '
                         + str(round(periodical_costs, 2))
                         + ' cost units (p.a.)')
                else:
                    periodical_costs = 0
                logging.info('   ' + 'Periodical costs (p.a.): '
                             + str(round(periodical_costs, 2))
                             + ' cost units p.a.')
                #else:
                #    logging.info('   ' + 'Total Energy Output to ' + p['bus_2']
                #                 + ': 0 kWh')
                df_result_table[p['label'] + '_input1'] = df_link2
                df_result_table[p['label'] + '_output1'] = df_link1
                if p['(un)directed'] == 'directed':
                    df_list_of_components = \
                        df_list_of_components.append(
                                pd.DataFrame([[p['label'], 'link',
                                               round(df_link2.sum(), 2),
                                               '--',
                                               round(df_link1.sum(), 2),
                                               '--',
                                               round(df_link2.max(), 2),
                                               round(variable_costs, 2),
                                               round(periodical_costs, 2),
                                               round(link_investment, 2)]],
                                             columns=columns))
                else:
                    df_result_table[p['label'] + '_input2'] = df_link1_2
                    df_result_table[p['label'] + '_output2'] = df_link2_2
                    df_list_of_components = \
                        df_list_of_components.append(
                                pd.DataFrame([[p['label'], 'link',
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
            logging.info(
                    '   ' + '------------------------------------------------')
        self.log("SUMMARY")
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
