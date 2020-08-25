"""Functions for returning optimization results in several forms.
 
----
@ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
"""

import logging
import pandas as pd
from oemof import outputlib
from matplotlib import pyplot as plt
import os


def xlsx(nodes_data, optimization_model, energy_system, filepath):
    """Returns model results as xlsx-files.
    
    Saves the in- and outgoing flows of every bus of a given, optimized energy 
    system as .xlsx file
    
    ----    
        
    Keyword arguments:
        
        nodes_data : obj:'dict'
           -- dictionary containing data from excel scenario file
        
        optimization_model
            -- optimized energy system
            
        energy_system : obj:
            -- original (unoptimized) energy system
            
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

    # renames input variables
    nd = nodes_data
    esys = energy_system 
    om = optimization_model
    results = outputlib.processing.results(om)

    # Writes a spreadsheet containing the input and output flows into every
    # bus of the energy system for every timestep of the timesystem
    for i, b in nd['buses'].iterrows():
            if b['active']:
                bus = outputlib.views.node(results, b['label'])                
                file_path = os.path.join(filepath, 'results_'+b['label'] +'.xlsx')
                node_results = outputlib.views.node(results, b['label'])
                df = node_results['sequences']
                df.head(2)          
                
                with pd.ExcelWriter(file_path) as writer:  # doctest: +SKIP
                     df.to_excel(writer, sheet_name=b['label'])

                # returns logging info
                logging.info('   '+'Results saved as xlsx for '+b['label'])


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

    nd = nodes_data
    esys = energy_system 
    om = optimization_model
    results = outputlib.processing.results(om)

    for i, b in nd['buses'].iterrows():
            if b['active']:
                logging.info('   '+"******************************************"
                             +"***************")            
                logging.info('   '+'RESULTS: ' + b['label'])
                
                bus = outputlib.views.node(results, b['label'])
                logging.info('   '+bus['sequences'].sum())
                fig, ax = plt.subplots(figsize=(10,5))
                bus['sequences'].plot(ax=ax)
                ax.legend(loc='upper center', prop={'size': 8}, 
                          bbox_to_anchor=(0.5, 1.4), ncol=2)
                fig.subplots_adjust(top=0.7)
                plt.show()
                                            
    esys.results['main'] = outputlib.processing.results(om)
    esys.results['meta'] = outputlib.processing.meta_results(om)
    string_results = outputlib.views.convert_keys_to_strings(
                                esys.results['main'])
    esys.dump(dpath=None, filename=None)


def statistics(nodes_data, optimization_model, energy_system):
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
        
           
    ----
    @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
    """

    # renames input variables
    nd = nodes_data
    esys = energy_system 
    om = optimization_model
    results = outputlib.processing.results(om)
    
    #######################
    ### Analyze Results ###
    #######################
    total_usage = 0
    total_demand = 0
    total_costs = 0
    total_periodical_costs = 0
    investments_to_be_made = {}
    list_of_components = {}

    # returns logging infos
    logging.info('   '+"******************************************************"
                             +"***") 
    logging.info('   '+"***SINKS**********************************************"
                             +"***") 
    logging.info('   '+"******************************************************"
                             +"***")
    logging.info('   '+'------------------------------------------------------'
                             +'---')

    # creates and returns results for sinks defined in the sinks-sheet of the
    # input spreadsheet
    for i, de in nd['demand'].iterrows():    
        if de['active']:
            # returns logging info
            logging.info('   '+de['label'])
            # reads the sinks optimized time series
            demand = outputlib.views.node(results, de['label'])
            # continues, if the sink has a non-zero timeseries
            if demand:
                # calculates the total demand of the sink
                flowsum = demand['sequences'].sum()
                # returns logging info containing the total demand of the sink
                logging.info('   '+'Total Energy Demand: ' 
                             + str(round(flowsum[[0][0]], 2)) 
                             + ' kWh')
                # adds the sinks energy demand to the total_demand variable
                total_demand = total_demand + flowsum[[0][0]]

            # returns logging info
            logging.info('   '+'----------------------------------------------'
                             +'---')

    # creates and returns results for sinks defined in the buses-sheet of the
    # input spreadsheet (excess sinks)
    for i, b in nd['buses'].iterrows():    
        if b['active']:
            if b['excess']:
                # returns logging info
                logging.info('   '+b['label']+'_excess')
                # reads the sinks optimized time series
                excess = outputlib.views.node(results, b['label']+'_excess')
                # calculates the total demand of the sink
                flowsum = excess['sequences'].sum()
                # returns logging info
                logging.info('   '+'Total Energy Input: ' 
                             + str(round(flowsum[[0][0]], 2)) + ' kWh')
                # adds the sinks energy demand to the total_usage variable
                total_usage = total_usage + flowsum[[0][0]] 
                # calculates the maximum capacity of the excess sink
                flowmax = excess['sequences'].max()
                # returns logging info
                logging.info('   '+'Max. Capacity: ' 
                             + str(round(flowmax[[0][0]], 2)) + ' kW')             
                # calculates the total variable costs of the sink
                variable_costs = b['excess costs /(CU/kWh)'] * flowsum[[0][0]]
                # adds the variable costs to the total_costs variable
                total_costs = total_costs + variable_costs
                # returns logging info
                logging.info('   '+'Variable Costs: ' 
                             + str(round(variable_costs, 2)) + ' cost units')
                logging.info('   '+'------------------------------------------'
                             +'--------------')        

    # returns logging infos
    logging.info('   '+"******************************************************"
                             +"***") 
    logging.info('   '+"***SOURCES********************************************"
                             +"***") 
    logging.info('   '+"******************************************************"
                             +"***")
    logging.info('   '+'------------------------------------------------------'
                             +'---')

    # creates and returns results for sources defined in the sources-sheet of the
    # input spreadsheet
    for i, so in nd['sources'].iterrows():    
        if so['active']:
            # returns logging info
            logging.info('   '+so['label'])
            # reads the time series of the sink
            source = outputlib.views.node(results, so['label'])
            # calculates the sum of all energy flows
            flowsum = source['sequences'].sum()
            # returns logging info
            logging.info('   ' + 'Total Energy Input: '
                         + str(round(flowsum[[0][0]], 2)) + ' kWh')
            # adds the flowsum to the total_usage variable
            total_usage = total_usage + flowsum[[0][0]]                 
            # calculates the maximum capacity of the source
            flowmax = source['sequences'].max()
            # returns logging info
            logging.info('   '+'Max. Capacity: ' 
                         + str(round(flowmax[[0][0]], 2)) + ' kW')
            # continues, if the model decided to take a investment decision
            # for this source
            if so['max. investment capacity /(kW)'] > 0:        
                # Reads the Investment Capacity
                source_node = esys.groups[so['label']]
                bus_node = esys.groups[so['output']]
                source_investment = (results[source_node, bus_node]['scalars']
                                    ['invest'])
                # returns logging info
                logging.info('   '+'Investment Capacity: ' 
                             + str(source_investment) + ' kW')

                # adds the investment to the investments_to_be_made list
                investments_to_be_made[so['label']] = (str(round(
                                                   source_investment, 2))+' kW')
            # return 0, if no investment decision for this source has been taken
            else:
                source_investment = 0
    
            # Calculates Variable Costs, adds it to the total_cost variable and
            # returns logging info
            variable_costs = so['variable costs /(CU/kWh)'] * flowsum[[0][0]]
            total_costs = total_costs + variable_costs
            logging.info('   '+'Variable costs: ' 
                         + str(round(variable_costs, 2)) 
                         + ' cost units')

            # Continues, if this is an investment object
            if source_investment > 0:
                # calculates the periodical costs
                periodical_costs = (so['periodical costs /(CU/(kW a))']*
                                    source_investment)
                # adds the periodical costs to the total_periodical_costs variable
                total_periodical_costs = (total_periodical_costs 
                                         + periodical_costs)
                investments_to_be_made[so['label']] = (str(results[source_node, 
                                                bus_node]['scalars']['invest'])
                                                +' kW; '
                                                +str(round(periodical_costs, 2))
                                                +' cost units (p.a.)')
            else:
                periodical_costs = 0
    
            logging.info('   '+'Periodical costs: ' 
                         + str(round(periodical_costs, 2)) 
                         + ' cost units p.a.')
            logging.info('   '+'----------------------------------------------'
                             +'---')
            
    for i, b in nd['buses'].iterrows():    
        if b['active']:
            if b['shortage']:
                logging.info('   '+b['label']+'_shortage')
                        
                shortage = outputlib.views.node(results, b['label']
                                                +'_shortage')
                # Flows
                flowsum = shortage['sequences'].sum()
                logging.info('   '+'Total Energy Input: ' 
                             + str(round(flowsum[[0][0]], 2)) + ' kWh')
                total_usage = total_usage + flowsum[[0][0]] 
                # Capacity
                flowmax = shortage['sequences'].max()
                logging.info('   '+'Max. Capacity: ' 
                             + str(round(flowmax[[0][0]], 2)) + ' kW')             
                # Variable Costs
                variable_costs = b['shortage costs /(CU/kWh)'] * flowsum[[0][0]]
                total_costs = total_costs + variable_costs
                logging.info('   '+'Variable Costs: ' 
                             + str(round(variable_costs, 2)) + ' cost units')    
                logging.info('   '+'------------------------------------------'
                             +'--------------')        

    logging.info('   '+"******************************************************"
                             +"***") 
    logging.info('   '+"***TRANSFORMERS***************************************"
                             +"***") 
    logging.info('   '+"******************************************************"
                             +"***")
    logging.info('   '+'------------------------------------------------------'
                             +'---')  
    for i, t in nd['transformers'].iterrows():    
        if t['active']:
            logging.info('   '+t['label'])   
                        
            transformer = outputlib.views.node(results, t['label'])
            flowsum = transformer['sequences'].sum()
            flowmax = transformer['sequences'].max()
            
            if t['transformer type'] == 'GenericTransformer':            
                if t['output2'] == 'None':
                    logging.info('   '+'Total Energy Output to ' 
                                 +  t['output'] + ': ' 
                                 + str(round(flowsum[[1][0]], 2)) 
                                 + ' kWh')
                    max_transformer_flow = flowmax[1]                
                else:    
                    logging.info('   '+'Total Energy Output to ' 
                                 +  t['output'] + ': ' 
                                 + str(round(flowsum[[0][0]], 2)) 
                                 + ' kWh')
                    logging.info('   '+'Total Energy Output to ' 
                                 +  t['output2'] + ': ' 
                                 + str(round(flowsum[[1][0]], 2)) 
                                 + ' kWh')
                    max_transformer_flow = flowmax[1]
            
            elif t['transformer type'] == 'ExtractionTurbineCHP':
                logging.info('   '+'WARNING: ExtractionTurbineCHP are'
                             +' currently not a part of this model generator,'
                             +' but will be added later.')                
            
            elif t['transformer type'] == 'GenericCHP':
                logging.info('   '+'Total Energy Output to ' 
                             +  t['output'] + ': ' 
                             + str(round(flowsum[[6][0]], 2)) 
                             + ' kWh')
                logging.info('   '+'Total Energy Output to ' 
                             +  t['output2'] + ': ' 
                             + str(round(flowsum[[7][0]], 2)) 
                             + ' kWh')
                max_transformer_flow = flowmax[2]
            
            elif t['transformer type'] == 'OffsetTransformer':
                logging.info('   '+'WARNING: OffsetTransformer are currently'
                             +' not a part of this model generator, but will'
                             +' be added later.')
            
    
            logging.info('   '+'Max. Capacity: ' 
                         + str(round(max_transformer_flow, 2)) 
                         + ' kW') ### Wert auf beide Busse anwenden!
            if t['output2'] != 'None': 
                logging.info('   '+'WARNING: Capacity to bus2 will be added'
                             +' later')
                

            variable_costs = (t['variable input costs /(CU/kWh)'] 
                              * flowsum[[0][0]] 
                              + t['variable output costs /(CU/kWh)']
                              * flowsum[[1][0]])
            total_costs = total_costs + variable_costs
            logging.info('   '+'Variable Costs: ' 
                         + str(round(variable_costs, 2)) 
                         + ' cost units')

            
            # Investment Capacity
            if t['max. investment capacity /(kW)'] > 0:
                transformer_node = esys.groups[t['label']]
                bus_node = esys.groups[t['output']]
                transformer_investment = (results[transformer_node, bus_node]
                                          ['scalars']['invest'])
                logging.info('   '+'Investment Capacity: ' 
                             + str(round(transformer_investment, 2)) 
                             + ' kW')
    
            else:
                transformer_investment = 0
                    
            # Periodical Costs        
            if transformer_investment > 0:     ### Wert auf beide Busse anwenden! (Es muss die Summe der Busse, inklusive des Wirkungsgrades einbezogen werden!!!)
                periodical_costs = (t['periodical costs /(CU/(kW a))']
                                    *transformer_investment)
                total_periodical_costs = (total_periodical_costs 
                                          + periodical_costs)
                investments_to_be_made[t['label']] = (str(round(
                                                    transformer_investment, 2))
                                                +' kW; '
                                                +str(round(periodical_costs,2))
                                                +' cost units (p.a.)')
            else:
                periodical_costs = 0
            logging.info('   '+'Periodical costs (p.a.): ' 
                         + str(round(periodical_costs, 2)) 
                         + ' cost units p.a.')
            
            logging.info('   '+'----------------------------------------------'
                             +'---') 
            
            
    logging.info('   '+"******************************************************"
                             +"***") 
    logging.info('   '+"***STORAGES*******************************************"
                             +"***") 
    logging.info('   '+"******************************************************"
                             +"***")
    logging.info('   '+'------------------------------------------------------'
                             +'---')          
    for i, s in nd['storages'].iterrows():    
        if s['active']:
            logging.info('   '+s['label'])                     
            storages = outputlib.views.node(results, s['label'])
            flowsum = storages['sequences'].sum()
            #logging.info('   '+flowsum)
            logging.info('   '+'Energy Output from ' 
                         + s['label'] + ': ' 
                         + str(round(flowsum[[1][0]], 2)) 
                         + ' kWh')
            logging.info('   '+'Energy Input to ' 
                         +  s['label'] + ': ' 
                         + str(round(flowsum[[2][0]], 2)) 
                         + ' kWh')
            
            storage = outputlib.views.node(results, s['label'])
            flowmax = storage['sequences'].max()
            #variable_costs = s['variable input costs'] * flowsum[[0][0]]
            logging.info('   '+'Max. Capacity: ' 
                         + str(round(flowmax[[0][0]], 2)) 
                         + ' kW')
            
            storage = outputlib.views.node(results, s['label'])
            flowsum = storage['sequences'].sum()
            variable_costs = s['variable input costs'] * flowsum[[0][0]]
            logging.info('   '+'Total variable costs for: ' 
                         + str(round(variable_costs, 2)) 
                         + ' cost units')
            total_costs = total_costs + variable_costs 
    
            # Investment Capacity
            if s['max. investment capacity /(kWh)'] > 0:
                storage_node = esys.groups[s['label']]
                bus_node = esys.groups[s['bus']]
                storage_investment = results[storage_node, None]['scalars']['invest']
                logging.info('   '+'Investment Capacity: ' 
                             + str(round(storage_investment, 2)) 
                             + ' kW')
    
            else:
                storage_investment = 0
                
            # Periodical Costs
            if storage_investment > float(s['existing capacity /(kWh)']):
                periodical_costs = (s['periodical costs /(CU/(kWh a))']
                                    *storage_investment)
                total_periodical_costs = (total_periodical_costs 
                                        + periodical_costs)
                investments_to_be_made[s['label']] = (str(round(
                                                        storage_investment, 2))
                                                +' kWh; '
                                                +str(round(periodical_costs,2))
                                                +' cost units (p.a.)')
            else:
                periodical_costs = 0
            logging.info('   '+'Periodical costs (p.a.): ' 
                         + str(round(periodical_costs, 2)) 
                         + ' cost units p.a.')
            
            logging.info('   '+'----------------------------------------------'
                             +'---')        
    
    logging.info('   '+"******************************************************"
                             +"***") 
    logging.info('   '+"***LINKS********************************************") 
    logging.info('   '+"******************************************************"
                             +"***")
    logging.info('   '+'------------------------------------------------------'
                             +'---')  
    for i, p in nd['links'].iterrows():    
        if p['active']:
            logging.info('   '+p['label'])   
                        
            link = outputlib.views.node(results, p['label'])
            
            if link:
                
                flowsum = link['sequences'].sum()
                #transformer_test = flowsum
                #transformer = outputlib.views.node(results, t['label'])
                flowmax = link['sequences'].max()
                        
                
                if p['(un)directed'] == 'directed':
                    logging.info('   '+'Total Energy Output to ' 
                                 +  p['bus_2'] + ': ' 
                                 + str(round(flowsum[[1][0]], 2)) 
                                 + ' kWh')
                    max_link_flow = flowmax[1]                
                else:
                    link2 = outputlib.views.node(results, p['label']
                                                 +'_direction_2')
                    flowsum2 = link2['sequences'].sum()
                    flowmax2 = link2['sequences'].max()
                    
                    logging.info('   '+'Total Energy Output to ' +  p['bus_2'] 
                                 + ': ' 
                                 + str(round(flowsum[[1][0]], 2)) 
                                 + ' kWh')
                    logging.info('   '+'Total Energy Output to ' 
                                 +  p['bus_1'] + ': ' 
                                 + str(round(flowsum2[[1][0]], 2)) 
                                 + ' kWh')
                    
                if p['(un)directed'] == 'directed':
                    max_link_flow = flowmax[1]
                    logging.info('   '+'Max. Capacity to '+  p['bus_2'] 
                                 + ': ' 
                                 + str(round(max_link_flow, 2)) 
                                 + ' kW') ### Wert auf beide Busse anwenden!
                else:
                    max_link_flow = flowmax[1]
                    logging.info('   '+'Max. Capacity to '
                                 +  p['bus_2'] + ': ' 
                                 + str(round(max_link_flow, 2)) 
                                 + ' kW')
                    max_link_flow = flowmax2[1]
                    logging.info('   '+'Max. Capacity to '
                                 +  p['bus_1'] + ': ' 
                                 + str(round(max_link_flow, 2)) 
                                 + ' kW')
                    
                #transformer = outputlib.views.node(results, t['label'])
                #flowsum = transformer['sequences'].sum()
                variable_costs = p['variable costs /(CU/kWh)'] * flowsum[[0][0]]
                total_costs = total_costs + variable_costs
                logging.info('   '+'Variable Costs: ' 
                             + str(round(variable_costs, 2)) 
                             + ' cost units')
                total_costs = total_costs + variable_costs
                
                # Investment Capacity
                if p['max. investment capacity /(kW)'] > 0:
                    link_node = esys.groups[p['label']]
                    bus_node = esys.groups[p['bus_2']]
                    link_investment = (results[link_node, bus_node]
                                       ['scalars']['invest'])
                    logging.info('   '+'Investment Capacity: ' 
                                 + str(round(link_investment, 2)) 
                                 + ' kW')
        
                else:
                    link_investment = 0
                        
                # Periodical Costs        
                if link_investment > 0:     ### Wert auf beide Busse anwenden! 
                    periodical_costs = p['periodical costs /(CU/(kW a))']
                    total_periodical_costs = (total_periodical_costs 
                                             + periodical_costs)
                    investments_to_be_made[p['label']] = (str(round(
                                                        link_investment, 2))
                                                +' kW; '
                                                +str(round(periodical_costs,2))
                                                +' cost units (p.a.)')
                else:
                    periodical_costs = 0
                logging.info('   '+'Periodical costs (p.a.): ' 
                             + str(round(periodical_costs, 2)) 
                             + ' cost units p.a.')
            else:
                logging.info('   '+'Total Energy Output to ' 
                             +  p['bus_2'] 
                             + ': 0 kWh')
            logging.info('   '+'----------------------------------------------'
                             +'---') 
    
 
    logging.info('   '+"******************************************************"
                             +"***") 
    logging.info('   '+"***SUMMARY********************************************"
                             +"***") 
    logging.info('   '+"******************************************************"
                             +"***")
    logging.info('   '+'------------------------------------------------------'
                             +'---')
    meta_results = outputlib.processing.meta_results(om)
    meta_results_objective = meta_results['objective']
    logging.info('   '+'Total System Costs:             ' 
                 + str(round(meta_results_objective, 1)) 
                 + ' cost units')
    logging.info('   '+'Total Variable Costs:           ' 
                 + str(round(total_costs)) + ' cost units')
    logging.info('   '+'Total Periodical Costs (p.a.):  ' 
                 + str(round(total_periodical_costs)) 
                 + ' cost units p.a.')
    logging.info('   '+'Total Energy Demand:            ' 
                 + str(round(total_demand)) + ' kWh')
    logging.info('   '+'Total Energy Usage:             ' 
                 + str(round(total_usage)) + ' kWh')
    logging.info('   '+'------------------------------------------------------'
                             +'---') 
    logging.info('   '+'Investments to be made:')
    
    investment_objects = list(investments_to_be_made.keys())
    
    for i in range(len(investment_objects)):
        logging.info('   '+investment_objects[i]+': '
                     + investments_to_be_made[investment_objects[i]])

    logging.info('   '+'------------------------------------------------------'
                             +'---')             
    logging.info('   '+"******************************************************"
                             +"***\n") 



def prepare_plotly_results(nodes_data, 
                           optimization_model, 
                           energy_system, 
                           result_path):
    
    """Function which prepares the results for the creation of a HTML page.
    
    Creates three pandas data frames and saves them, which are required for 
    creating an interactive HTML result page:
       - df_list_of_components: Consists all components with several properties
       - df_result_table: Consists timeseries of al components
       - df_summary: Consists summarizing results of the modelling
       
    ----    
        
    Keyword arguments:
        
        nodes_data : obj:'dict'
           -- dictionary containing data from excel scenario file
        
        optimization_model
            -- optimized energy system
            
        energy_system : obj:
            -- original (unoptimized) energy system
            
        result_path : obj:'str'
            -- path, where the data frames shall be saved as csv-file
        
           
    ----
    @ Christian Klemm - christian.klemm@fh-muenster.de, 13.03.2020
        
    """
    
    logging.info('   '+'--------------------------------------------------------') 
    logging.info('   '+'Preparing the results for interactive results...')
    nd = nodes_data
    esys = energy_system 
    om = optimization_model
    results = outputlib.processing.results(om)
    
    #######################
    ### Analyze Results ###
    #######################
    total_usage = 0
    total_demand = 0
    total_costs = 0
    total_periodical_costs = 0
    investments_to_be_made = {}
    
    df_list_of_components = pd.DataFrame(columns=['ID', 
                                      'type', 
                                      'input 1/kWh', 
                                      'input 2/kWh', 
                                      'output 1/kWh', 
                                      'output 2/kWh', 
                                      'capacity/kW', 
                                      'variable costs/CU', 
                                      'periodical costs/CU',
                                      'investment/kW'])
    #Add dummy component
#    df_demand = pd.DataFrame([['---------------', 
#           '---------------', 
#           '---------------', 
#           '---------------', 
#           '---------------', 
#           '---------------',
#           '---------------',
#           '--------------------',
#           '--------------------',
#           '---------------'
#           ]], 
#           columns=['ID', 
#                      'type', 
#                      'input 1 [kWh]', 
#                      'input 2 [kWh]', 
#                      'output 1 [kWh]', 
#                      'output 2 [kWh]', 
#                      'capacity [kW]', 
#                      'variable costs [CU]', 
#                      'periodical costs [CU]',
#                      'investment [kW]']) 
#    df_list_of_components = df_list_of_components.append(df_demand) 
    
    df_component_flows = pd.DataFrame(columns=['component',
                                               'date',
                                               'performance',
                                               'ID'])
    
    #Add dummy component (required for starting the plotly app)
    
    df_result_table = pd.DataFrame()
 #   print(type(results))
 #   print(results)





######################
##### SOURCES ##########
######################  

    
    for i, de in nd['demand'].iterrows():
        

        variable_costs = 0
        periodical_costs = 0      
        
        if de['active']:
                     
            demand = outputlib.views.node(results, de['label'])
            
#            for i in range len(demand):
            

            
            if demand:
                flowsum = demand['sequences'].sum()
                flowmax = demand['sequences'].max()

                total_demand = total_demand + flowsum[[0][0]]
                
                # Adds the components time series to the df_component_flows
                # data frame for further usage
                i=0
                number_of_periods = len(demand['sequences'].values)
                

             
                component_performance = demand['sequences'].columns.values
                df_demand = demand['sequences'][component_performance[0]]
                df_result_table[de['label']] = df_demand
                    


            
        df_demand = pd.DataFrame([[de['label'], 
                           'sink', 
                           round(demand['sequences'][component_performance[0]].sum(), 2), 
                           '---', 
                           '---', 
                           '---',
                           round(demand['sequences'][component_performance[0]].max(), 2),
                           '---',
                           '---',
                           '---'
                           ]], 
                           columns=['ID', 
                                      'type', 
                                      'input 1/kWh', 
                                      'input 2/kWh', 
                                      'output 1/kWh', 
                                      'output 2/kWh', 
                                      'capacity/kW', 
                                      'variable costs/CU', 
                                      'periodical costs/CU',
                                      'investment/kW'])   
        df_list_of_components = df_list_of_components.append(df_demand)              
                
#            logging.info('   '+'----------------------------------------------'
 #                            +'---')
    
        
    for i, b in nd['buses'].iterrows():
        
        # if flowsum[[0][0]]:
        #     flowsum[[0][0]] = 0
        # if flowmax[[0][0]]:
        #     flowmax[[0][0]] = 0
        variable_costs = 0
        periodical_costs = 0
        
        
        if b['active']:
            if b['excess']:
                        
                excess = outputlib.views.node(results, b['label']+'_excess')
                # Flows
                flowsum = excess['sequences'].sum()

                total_usage = total_usage + flowsum[[0][0]] 
                # Capacity
          
                # Variable Costs
                variable_costs = b['excess costs /(CU/kWh)'] * flowsum[[0][0]]
                total_costs = total_costs + variable_costs
              

                component_performance = excess['sequences'].columns.values
                df_excess = excess['sequences'][component_performance[0]]
                if len(df_result_table) != 0:
                    df_result_table[b['label']+'_excess'] = df_excess
                elif len(df_result_table) == 0:
                    df_result_table[b['label']+'_excess'] = df_excess

        


                df_demand = pd.DataFrame([[b['label'] + '_excess', 
                                   'sink', 
                                   round(excess['sequences'][component_performance[0]].sum(), 2), 
                                   '---', 
                                   '---', 
                                   '---',
                                   round(excess['sequences'][component_performance[0]].max(), 2),
                                   round(variable_costs, 2),
                                   '---',
                                   '---'
                                   ]], 
                                   columns=['ID', 
                                      'type', 
                                      'input 1/kWh', 
                                      'input 2/kWh', 
                                      'output 1/kWh', 
                                      'output 2/kWh', 
                                      'capacity/kW', 
                                      'variable costs/CU', 
                                      'periodical costs/CU',
                                      'investment/kW'])   
                df_list_of_components = df_list_of_components.append(df_demand)
                



######################
##### SOURCES ##########
######################    
    
    for i, so in nd['sources'].iterrows():
        
        # if flowsum[[0][0]]:
        #     flowsum[[0][0]] = 0
        # if flowmax[[0][0]]:
        #     flowmax[[0][0]] = 0
        variable_costs = 0
        periodical_costs = 0
        source_investment = 0
        
        if so['active']:
            #Flows                  
            source = outputlib.views.node(results, so['label'])
            flowsum = source['sequences'].sum()

            total_usage = total_usage + flowsum[[0][0]]                 
            # Capacity
            flowmax = source['sequences'].max()

            if so['max. investment capacity /(kW)'] > 0:        
            # Investment Capacity
                source_node = esys.groups[so['label']]
                bus_node = esys.groups[so['output']]
                source_investment = (results[source_node, bus_node]['scalars']
                                    ['invest'])

                investments_to_be_made[so['label']] = (str(round(
                                                   source_investment,2))+' kW')
            else:
                source_investment = 0
    
            # Variable Costs
            variable_costs = so['variable costs /(CU/kWh)'] * flowsum[[0][0]]
            total_costs = total_costs + variable_costs

            # Periodical Costs
            if source_investment > 0:
                periodical_costs = (so['periodical costs /(CU/(kW a))']*
                                    source_investment)
                total_periodical_costs = (total_periodical_costs 
                                         + periodical_costs)
                investments_to_be_made[so['label']] = (str(results[source_node, 
                                                bus_node]['scalars']['invest'])
                                                +' kW; '
                                                +str(round(periodical_costs,2))
                                                +' cost units (p.a.)')
            else:
                periodical_costs = 0
    

            # Adds the components time series to the df_component_flows
            # data frame for further usage
            component_performance = source['sequences'].columns.values
            df_source = source['sequences'][component_performance[0]]
            df_result_table[so['label']] = df_source      
            
            
            
            df_demand = pd.DataFrame([[so['label'], 
                               'source', 
                               '---', 
                               '---', 
                               round(source['sequences'][component_performance[0]].sum(), 2), 
                               '---',
                               round(source['sequences'][component_performance[0]].max(), 2),
                               round(variable_costs, 2),
                               round(periodical_costs, 2),
                               round(source_investment, 2)
                               ]], 
                               columns=['ID', 
                                          'type', 
                                          'input 1/kWh', 
                                          'input 2/kWh', 
                                          'output 1/kWh', 
                                          'output 2/kWh', 
                                          'capacity/kW', 
                                          'variable costs/CU', 
                                          'periodical costs/CU',
                                          'investment/kW'])   
            df_list_of_components = df_list_of_components.append(df_demand) 



   
         
    for i, b in nd['buses'].iterrows():
        
        # if flowsum[[0][0]]:
        #     flowsum[[0][0]] = 0
        # if flowmax[[0][0]]:
        #     flowmax[[0][0]] = 0
        variable_costs = 0
        periodical_costs = 0
        
        if b['active']:
            if b['shortage']:

                shortage = outputlib.views.node(results, b['label']
                                                +'_shortage')
                # Flows
                flowsum = shortage['sequences'].sum()
    
                total_usage = total_usage + flowsum[[0][0]] 
                # Capacity
                flowmax = shortage['sequences'].max()
           
                # Variable Costs
                variable_costs = b['shortage costs /(CU/kWh)'] * flowsum[[0][0]]
                total_costs = total_costs + variable_costs
       
                    
                df_demand = pd.DataFrame([[b['label']+'_shortage', 
                                   'source', 
                                   '---', 
                                   '---', 
                                   round(flowsum[[0][0]], 2), 
                                   '---',
                                   round(flowmax[[0][0]], 2),
                                   round(variable_costs, 2),
                                   round(periodical_costs, 2),
                                   '---'
                                   ]], 
                                   columns=['ID', 
                                      'type', 
                                      'input 1/kWh', 
                                      'input 2/kWh', 
                                      'output 1/kWh', 
                                      'output 2/kWh', 
                                      'capacity/kW', 
                                      'variable costs/CU', 
                                      'periodical costs/CU',
                                      'investment/kW'])   
                df_list_of_components = df_list_of_components.append(df_demand) 
                
                component_performance = shortage['sequences'].columns.values
                df_shortage = shortage['sequences'][component_performance[0]]
                df_result_table[b['label']+'_shortage'] = df_shortage
            
        

######################
##### TRANSFORMERS ##########
######################  

    for i, t in nd['transformers'].iterrows(): 
        
        # if flowsum[[0][0]]:
        #     flowsum[[0][0]] = 0
        # if flowmax[[0][0]]:
        #     flowmax[[0][0]] = 0
        variable_costs = 0
        periodical_costs = 0
        transformer_investment = 0
        
        if t['active']:

                        
            transformer = outputlib.views.node(results, t['label'])
            flowsum = transformer['sequences'].sum()
            flowmax = transformer['sequences'].max()

              

            variable_costs = (t['variable input costs /(CU/kWh)'] 
                              * flowsum[[0][0]] 
                              + t['variable output costs /(CU/kWh)']
                              * flowsum[[1][0]])
            total_costs = total_costs + variable_costs

            
            # Investment Capacity
            if t['max. investment capacity /(kW)'] > 0:
                transformer_node = esys.groups[t['label']]
                bus_node = esys.groups[t['output']]
                transformer_investment = (results[transformer_node, bus_node]
                                          ['scalars']['invest'])
    
            else:
                transformer_investment = 0
                    
            # Periodical Costs        
            if transformer_investment > 0:     ### Wert auf beide Busse anwenden! (Es muss die Summe der Busse, inklusive des Wirkungsgrades einbezogen werden!!!)
                periodical_costs = (t['periodical costs /(CU/(kW a))']
                                    *transformer_investment)
                total_periodical_costs = (total_periodical_costs 
                                          + periodical_costs)
                investments_to_be_made[t['label']] = (str(round(
                                                    transformer_investment, 2))
                                                +' kW; '
                                                +str(round(periodical_costs,2))
                                                +' cost units (p.a.)')
            else:
                periodical_costs = 0
            
            if t['transformer type'] == 'GenericTransformer':            
                if t['output2'] == 'None':

                    max_transformer_flow = flowmax[1]
                    
                    component_performance = transformer['sequences'].columns.values
                    df_transformer = transformer['sequences'][component_performance[0]]
                    df_result_table[t['label']+'_input1'] = df_transformer
                    df_transformer = transformer['sequences'][component_performance[1]]
                    df_result_table[t['label']+'_output1'] = df_transformer
                    
                    df_demand = pd.DataFrame([[t['label'], 
                       'transformer', 
                       round(transformer['sequences'][component_performance[0]].sum(),2), 
                       '---', 
                       round(transformer['sequences'][component_performance[1]].sum(), 2), 
                       '---',
                       round(transformer['sequences'][component_performance[0]].max(),2),
                       round(variable_costs,2),
                       round(periodical_costs,2),
                       round(transformer_investment, 2)
                       ]], 
                       columns=['ID', 
                                      'type', 
                                      'input 1/kWh', 
                                      'input 2/kWh', 
                                      'output 1/kWh', 
                                      'output 2/kWh', 
                                      'capacity/kW', 
                                      'variable costs/CU', 
                                      'periodical costs/CU',
                                      'investment/kW'])   
                    df_list_of_components = df_list_of_components.append(df_demand) 
                    
                else:    

                    max_transformer_flow = flowmax[1]
                    

                    component_performance = transformer['sequences'].columns.values
                    df_transformer = transformer['sequences'][component_performance[0]]
                    df_result_table[t['label']+'_input1'] = df_transformer
                    df_transformer = transformer['sequences'][component_performance[1]]
                    df_result_table[t['label']+'_output1'] = df_transformer
                    df_transformer = transformer['sequences'][component_performance[2]]
                    df_result_table[t['label']+'_output2'] = df_transformer

                    
                    
                    df_demand = pd.DataFrame([[t['label'], 
                       'transformer', 
                       round(transformer['sequences'][component_performance[0]].sum(),2), 
                       '---', 
                       round(transformer['sequences'][component_performance[1]].sum(), 2), 
                       round(transformer['sequences'][component_performance[2]].sum(), 2),
                       round(transformer['sequences'][component_performance[0]].max(),2),
                       round(variable_costs,2),
                       round(periodical_costs,2),
                       round(transformer_investment, 2)
                       ]], 
                       columns=['ID', 
                                      'type', 
                                      'input 1/kWh', 
                                      'input 2/kWh', 
                                      'output 1/kWh', 
                                      'output 2/kWh', 
                                      'capacity/kW', 
                                      'variable costs/CU', 
                                      'periodical costs/CU',
                                      'investment/kW'])   
                    df_list_of_components = df_list_of_components.append(df_demand) 
                           
            
            elif t['transformer type'] == 'GenericCHP':

                max_transformer_flow = flowmax[2]
                      
                
                df_demand = pd.DataFrame([[t['label'], 
                   'transformer', 
                   'nn', 
                   'nn', 
                   round(flowsum[[6][0]], 2), 
                   round(flowsum[[7][0]], 2),
                   'nn',
                   round(variable_costs, 2),
                   round(periodical_costs, 2),
                   round(transformer_investment, 2)
                   ]], 
                   columns=['ID', 
                                      'type', 
                                      'input 1/kWh', 
                                      'input 2/kWh', 
                                      'output 1/kWh', 
                                      'output 2/kWh', 
                                      'capacity/kW', 
                                      'variable costs/CU', 
                                      'periodical costs/CU',
                                      'investment/kW'])   
                df_list_of_components = df_list_of_components.append(df_demand)    

            
            

######################
##### STORAGES ##########
######################           

    for i, s in nd['storages'].iterrows():
        
        # if flowsum[[0][0]]:
        #     flowsum[[0][0]] = 0
        # if flowsum[[1][0]]:
        #     flowsum[[1][0]] = 0
        # if flowmax[[0][0]]:
        #     flowmax[[0][0]] = 0
        variable_costs = 0
        periodical_costs = 0   
        storage_investment = 0
        
        if s['active']:
                               
            storages = outputlib.views.node(results, s['label'])
            flowsum = storages['sequences'].sum()
            #logging.info('   '+flowsum)
                        
            storage = outputlib.views.node(results, s['label'])
            flowmax = storage['sequences'].max()
            #variable_costs = s['variable input costs'] * flowsum[[0][0]]
            
            
            storage = outputlib.views.node(results, s['label'])
            flowsum = storage['sequences'].sum()
            variable_costs = s['variable input costs'] * flowsum[[0][0]]
            
            total_costs = total_costs + variable_costs 
    
            # Investment Capacity
            if s['max. investment capacity /(kWh)'] > 0:
                storage_node = esys.groups[s['label']]
                bus_node = esys.groups[s['bus']]
                storage_investment = results[storage_node, None]['scalars']['invest']
                
            else:
                storage_investment = 0
                
            # Periodical Costs
            if storage_investment > float(s['existing capacity /(kWh)']):
                periodical_costs = (s['periodical costs /(CU/(kWh a))']
                                    *storage_investment)
                total_periodical_costs = (total_periodical_costs 
                                        + periodical_costs)
                investments_to_be_made[s['label']] = (str(round(
                                                        storage_investment, 2))
                                                +' kWh; '
                                                +str(round(periodical_costs,2))
                                                +' cost units (p.a.)')
            else:
                periodical_costs = 0
            
            df_demand = pd.DataFrame([[s['label'], 
               'storage', 
               round(flowsum[[2][0]], 2), 
               '---', 
               round(flowsum[[1][0]], 2), 
               '---',
               round(flowmax[[0][0]], 2),
               round(variable_costs, 2),
               round(periodical_costs, 2),
               round(storage_investment, 2)
               ]], 
               columns=['ID', 
                                      'type', 
                                      'input 1/kWh', 
                                      'input 2/kWh', 
                                      'output 1/kWh', 
                                      'output 2/kWh', 
                                      'capacity/kW', 
                                      'variable costs/CU', 
                                      'periodical costs/CU',
                                      'investment/kW'])   
            df_list_of_components = df_list_of_components.append(df_demand)
          
            component_performance = storage['sequences'].columns.values
          
            
            df_storage = storage['sequences'][component_performance[0]]
            df_result_table[s['label']+'_capacity'] = df_storage
            df_storage = storage['sequences'][component_performance[2]]
            df_result_table[s['label']+'_input'] = df_storage
            df_storage = storage['sequences'][component_performance[1]]
            df_result_table[s['label']+'_output'] = df_storage
            
            

######################
##### LINKS ##########
######################            


    for i, p in nd['links'].iterrows():
    
        if flowsum[[0][0]]:
            flowsum[[0][0]] = 0
        if flowsum[[1][0]]:
            flowsum[[1][0]] = 0
        if flowmax[[0][0]]:
            flowmax[[0][0]] = 0
        variable_costs = 0
        periodical_costs = 0
        
        if p['active']:
                        
            link = outputlib.views.node(results, p['label'])
            #print(link)
            
            if link:
                
                flowsum = link['sequences'].sum()
                #transformer_test = flowsum
                #transformer = outputlib.views.node(results, t['label'])
                flowmax = link['sequences'].max()
                        
                
                if p['(un)directed'] == 'directed':

                    max_link_flow = flowmax[1] 
                    # define flowsum2[[1][0]] as 0 to avoid later errors
                    flowsum2 = link['sequences'].sum()
                    flowsum2[[1][0]] = 0
                    
                else:
                    link2 = outputlib.views.node(results, p['label']
                                                 +'_direction_2')
                    flowsum2 = link2['sequences'].sum()
                    flowmax2 = link2['sequences'].max()
                                         
                    
                if p['(un)directed'] == 'directed':
                    max_link_flow = flowmax[1]
                    

                    

                else:
                    max_link_flow = flowmax[1]

                    max_link_flow = flowmax2[1]
                    


                    
                variable_costs = p['variable costs /(CU/kWh)'] * flowsum[[0][0]]
                total_costs = total_costs + variable_costs
                total_costs = total_costs + variable_costs
                
                # Investment Capacity
                if p['max. investment capacity /(kW)'] > 0:
                    link_node = esys.groups[p['label']]
                    bus_node = esys.groups[p['bus_2']]
                    link_investment = (results[link_node, bus_node]
                                       ['scalars']['invest'])

        
                else:
                    link_investment = 0
                        
                # Periodical Costs        
                if link_investment > 0:     ### Wert auf beide Busse anwenden! 
                    periodical_costs = p['periodical costs /(CU/(kW a))']
                    total_periodical_costs = (total_periodical_costs 
                                             + periodical_costs)
                    investments_to_be_made[p['label']] = (str(round(
                                                        link_investment, 2))
                                                +' kW; '
                                                +str(round(periodical_costs,2))
                                                +' cost units (p.a.)')
                else:
                    periodical_costs = 0

            if p['(un)directed'] == 'directed':
                component_performance = link['sequences'].columns.values
                df_link = link['sequences'][component_performance[0]]
                df_result_table[p['label']+'_input1'] = df_link
                df_link = link['sequences'][component_performance[1]]
                df_result_table[p['label']+'_output1'] = df_link
              
    
                df_demand = pd.DataFrame([[p['label'], 
                   'link', 
                   round(link['sequences'][component_performance[0]].sum(), 2), 
                   '--',#round(link2['sequences'][component_performance2[0]].sum(), 2), 
                   round(link['sequences'][component_performance[1]].sum(), 2),
                   '--',#round(link2['sequences'][component_performance2[1]].sum(), 2),
                   round(link['sequences'][component_performance[1]].max(), 2),
                   round(variable_costs, 2),
                   round(periodical_costs, 2),
                   round(link_investment, 2)
                   ]], 
                   columns=['ID', 
                                      'type', 
                                      'input 1/kWh', 
                                      'input 2/kWh', 
                                      'output 1/kWh', 
                                      'output 2/kWh', 
                                      'capacity/kW', 
                                      'variable costs/CU', 
                                      'periodical costs/CU',
                                      'investment/kW'])    
                df_list_of_components = df_list_of_components.append(df_demand)                
            else:
                component_performance = link['sequences'].columns.values
                df_link = link['sequences'][component_performance[0]]
                df_result_table[p['label']+'_input1'] = df_link
                df_link = link['sequences'][component_performance[1]]
                df_result_table[p['label']+'_output1'] = df_link
                
                
                component_performance2 = link2['sequences'].columns.values
                df_link2 = link2['sequences'][component_performance2[0]]
                df_result_table[p['label']+'_input2'] = df_link2
                df_link2 = link2['sequences'][component_performance2[1]]
                df_result_table[p['label']+'_output2'] = df_link2
    
    
    
                df_demand = pd.DataFrame([[p['label'], 
                   'link', 
                   round(link['sequences'][component_performance[0]].sum(), 2), 
                   round(link2['sequences'][component_performance2[0]].sum(), 2), 
                   round(link['sequences'][component_performance[1]].sum(), 2),
                   round(link2['sequences'][component_performance2[1]].sum(), 2),
                   round(max(link['sequences'][component_performance[1]].max(), link2['sequences'][component_performance2[1]].max()), 2),
                   round(variable_costs, 2),
                   round(periodical_costs, 2),
                   round(link_investment, 2)
                   ]], 
                   columns=['ID', 
                                      'type', 
                                      'input 1/kWh', 
                                      'input 2/kWh', 
                                      'output 1/kWh', 
                                      'output 2/kWh', 
                                      'capacity/kW', 
                                      'variable costs/CU', 
                                      'periodical costs/CU',
                                      'investment/kW'])    
                df_list_of_components = df_list_of_components.append(df_demand)
            

            
    
################
### SUMMARY ####
################
            
            
    meta_results = outputlib.processing.meta_results(om)
    meta_results_objective = meta_results['objective']
    
    investment_objects = list(investments_to_be_made.keys())


    for j, ts in nd['timesystem'].iterrows():
        start_date = ts['start date']
        end_date = ts['end date']
        temp_resolution = ts['temporal resolution']


    df_summary = pd.DataFrame([[start_date,
                                end_date,
                                temp_resolution,
                                round(meta_results_objective, 2),
                                round(total_costs,2),
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
                'Total Energy Usage'

              ])    


    for j, ts in nd['timesystem'].iterrows():
        start_date = ts['start date']
        end_date = ts['end date']
        temp_resolution = ts['temporal resolution']

   

    
    
    # Dataframes werden als csv zur weiterverarbeitung abgelegt

    df_list_of_components.to_csv(result_path+'/components.csv', index=False) 
    
    df_result_table = df_result_table.rename_axis('date')
    df_result_table.to_csv(result_path+'/results.csv') 
    
    df_summary.to_csv(result_path+'/summary.csv', index=False)
    
    logging.info('   '+'Successfully prepared results...')