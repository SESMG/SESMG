"""
Functions for returning optimization results in several forms.
 
----

@ Christian Klemm - christian.klemm@fh-muenster.de, 14.01.2020

"""

import logging
import pandas as pd
from oemof import outputlib
from matplotlib import pyplot as plt
import os

def xlsx(nodes_data, optimization_model, energy_system, filepath):
    """
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
    
    @ Christian Klemm - christian.klemm@fh-muenster.de, 14.01.2020
    
    """
    
    nd = nodes_data
    esys = energy_system 
    om = optimization_model
    results = outputlib.processing.results(om)
    
    for i, b in nd['buses'].iterrows():
            if b['active']:
                bus = outputlib.views.node(results, b['label'])                
                file_path = os.path.join(filepath, 'results_'+b['label']+'.xlsx')                        
                node_results = outputlib.views.node(results, b['label'])
                df = node_results['sequences']
                df.head(2)          
                
                with pd.ExcelWriter(file_path) as writer:  # doctest: +SKIP
                     df.to_excel(writer, sheet_name=b['label'])
                     
                logging.info('Results saved as xlsx for '+b['label'])









def charts(nodes_data, optimization_model, energy_system):
    """
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
    
    @ Christian Klemm - christian.klemm@fh-muenster.de, 14.01.2020

    """

    nd = nodes_data
    esys = energy_system 
    om = optimization_model
    results = outputlib.processing.results(om)
       
    for i, b in nd['buses'].iterrows():
            if b['active']:
                print("*********************************************************")            
                print('RESULTS: ' + b['label'])
                
                bus = outputlib.views.node(results, b['label'])
                print(bus['sequences'].sum())
                fig, ax = plt.subplots(figsize=(10,5))
                bus['sequences'].plot(ax=ax)
                ax.legend(loc='upper center', prop={'size': 8}, bbox_to_anchor=(0.5, 1.4), ncol=2)
                fig.subplots_adjust(top=0.7)
                plt.show()
                        
#                    node_results = outputlib.views.node(results, b['label'])
#                    df = node_results['sequences']
#                    df.head(2)          
#                    
#                    with pd.ExcelWriter('results_'+b['label']+'.xlsx') as writer:  # doctest: +SKIP
#                         df.to_excel(writer, sheet_name=b['label'])
                     
    esys.results['main'] = outputlib.processing.results(om)
    esys.results['meta'] = outputlib.processing.meta_results(om)
    string_results = outputlib.views.convert_keys_to_strings(esys.results['main'])
    esys.dump(dpath=None, filename=None)









    
def costs(nodes_data, optimization_model, energy_system):
    """
    Returns a list of all defined components with the following information:
        
    component   |   information
    -------------------------------------------------------------------------------
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
    
    @ Christian Klemm - christian.klemm@fh-muenster.de, 14.01.2020

    """
    
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
    
    print("*********************************************************") 
    print("***SINKS*************************************************") 
    print("*********************************************************")
    print('--------------------------------------------------------')
    
    for i, de in nd['demand'].iterrows():    
        if de['active']:
            print(de['label'])                        
            demand = outputlib.views.node(results, de['label'])
            flowsum = demand['sequences'].sum()
            #print(flowsum)
            print('Total Energy Demand: ' + str(round(flowsum[[0][0]], 2)) + ' kWh')
            total_demand = total_demand + flowsum[[0][0]]
            print('--------------------------------------------------------')
            
    for i, b in nd['buses'].iterrows():    
        if b['active']:
            if b['excess']:
                print(b['label']+'_excess')
                        
                excess = outputlib.views.node(results, b['label']+'_excess')
                # Flows
                flowsum = excess['sequences'].sum()
                print('Total Energy Input: ' + str(round(flowsum[[0][0]], 2)) + ' kWh')
                total_usage = total_usage + flowsum[[0][0]] 
                # Capacity
                flowmax = excess['sequences'].max()
                print('Max. Capacity: ' + str(round(flowmax[[0][0]], 2)) + ' kW')             
                # Variable Costs
                variable_costs = b['excess costs [CU/kWh]'] * flowsum[[0][0]]
                total_costs = total_costs + variable_costs
                print('Variable Costs: ' + str(round(variable_costs, 2)) + ' cost units')    
                print('--------------------------------------------------------')        
    
    
    
    
    print("*********************************************************") 
    print("***SOURCES***********************************************") 
    print("*********************************************************")
    print('--------------------------------------------------------CAPACITY ÜBERPRÜFEN, INSB. BEI PV MUSS PEAK POWER BERÜCKSICTIGT WERDEN.')    
    
    for i, so in nd['sources'].iterrows():    
        if so['active']:
            #Flows
            print(so['label'])                     
            source = outputlib.views.node(results, so['label'])
            flowsum = source['sequences'].sum()
            print('Total Energy Input: ' + str(round(flowsum[[0][0]], 2)) + ' kWh')
            total_usage = total_usage + flowsum[[0][0]]                 
            # Capacity
            flowmax = source['sequences'].max()
            print('Max. Capacity: ' + str(round(flowmax[[0][0]], 2)) + ' kW')
            if so['max. investment capacity [kW]'] > 0:        
            # Investment Capacity
                source_node = esys.groups[so['label']]
                bus_node = esys.groups[so['output']]
                source_investment = results[source_node, bus_node]['scalars']['invest']
                print('Investment Capacity: ' + str(source_investment) + ' kW')
                investments_to_be_made[so['label']] = (str(round(source_investment,2))+' kW')
            else:
                source_investment = 0
    
            # Variable Costs
            variable_costs = so['variable costs [CU/kWh]'] * flowsum[[0][0]]
            total_costs = total_costs + variable_costs
            print('Variable costs: ' + str(round(variable_costs, 2)) + ' cost units')
            # Periodical Costs
            if source_investment > 0:
                periodical_costs = so['periodical costs [CU/(kW a)]']*source_investment
                total_periodical_costs = total_periodical_costs + periodical_costs
                investments_to_be_made[so['label']] = (str(results[source_node, bus_node]['scalars']['invest'])
                                                        +' kW; '+str(round(periodical_costs,2))
                                                        +' cost units (p.a.)')
            else:
                periodical_costs = 0
    
            print('Periodical costs: ' + str(round(periodical_costs, 2)) + ' cost units p.a.')
            print('--------------------------------------------------------')
            
    for i, b in nd['buses'].iterrows():    
        if b['active']:
            if b['shortage']:
                print(b['label']+'_shortage')
                        
                shortage = outputlib.views.node(results, b['label']+'_shortage')
                # Flows
                flowsum = shortage['sequences'].sum()
                print('Total Energy Input: ' + str(round(flowsum[[0][0]], 2)) + ' kWh')
                total_usage = total_usage + flowsum[[0][0]] 
                # Capacity
                flowmax = shortage['sequences'].max()
                print('Max. Capacity: ' + str(round(flowmax[[0][0]], 2)) + ' kW')             
                # Variable Costs
                variable_costs = b['shortage costs [CU/kWh]'] * flowsum[0]
                total_costs = total_costs + variable_costs
                print('Variable Costs: ' + str(round(variable_costs, 2)) + ' cost units')    
                print('--------------------------------------------------------')        

    print("*********************************************************") 
    print("***TRANSFORMERS******************************************") 
    print("*********************************************************")
    print('--------------------------------------------------------CAPACITY BEI MEHREREN AUSGÄNGEN PRÜFEN')  
    for i, t in nd['transformers'].iterrows():    
        if t['active']:
            print(t['label'])   
                        
            transformer = outputlib.views.node(results, t['label'])
            flowsum = transformer['sequences'].sum()
            #transformer_test = flowsum
            #transformer = outputlib.views.node(results, t['label'])
            flowmax = transformer['sequences'].max()
                    
            if t['transformer type'] == 'GenericTransformer':            
                if t['output2'] == 'None':
                    print('Total Energy Output to ' +  t['output'] + ': ' + str(round(flowsum[[1][0]], 2)) + ' kWh')
                    max_transformer_flow = flowmax[1]                
                else:    
                    print('Total Energy Output to ' +  t['output'] + ': ' + str(round(flowsum[[0][0]], 2)) + ' kWh')
                    print('Total Energy Output to ' +  t['output2'] + ': ' + str(round(flowsum[[1][0]], 2)) + ' kWh')
                    max_transformer_flow = flowmax[1]
            
            elif t['transformer type'] == 'ExtractionTurbineCHP':
                print('WARNING: ExtractionTurbineCHP are currently not a part of this model generator, but will be added later.')                
            
            elif t['transformer type'] == 'GenericCHP':
                print('Total Energy Output to ' +  t['output'] + ': ' + str(round(flowsum[[6][0]], 2)) + ' kWh')
                print('Total Energy Output to ' +  t['output2'] + ': ' + str(round(flowsum[[7][0]], 2)) + ' kWh')
                max_transformer_flow = flowmax[2]
            
            elif t['transformer type'] == 'OffsetTransformer':
                print('WARNING: OffsetTransformer are currently not a part of this model generator, but will be added later.')
            
    
            print('Max. Capacity: ' + str(round(max_transformer_flow, 2)) + ' kW') ### Wert auf beide Busse anwenden!
            if t['output2'] != 'None': 
                print('WARNING: Capacity to bus2 will be added later')
                
            #transformer = outputlib.views.node(results, t['label'])
            #flowsum = transformer['sequences'].sum()
            variable_costs = (t['variable input costs [CU/kWh]']+t['variable output costs [CU/kWh]']) * flowsum[[0][0]]
            total_costs = total_costs + variable_costs
            print('Variable Costs: ' + str(round(variable_costs, 2)) + ' cost units')
            total_costs = total_costs + variable_costs
            
            # Investment Capacity
            if t['max. investment capacity [kW]'] > 0:
                transformer_node = esys.groups[t['label']]
                bus_node = esys.groups[t['output']]
                transformer_investment = results[transformer_node, bus_node]['scalars']['invest']
                print('Investment Capacity: ' + str(round(transformer_investment, 2)) + ' kW')
    
            else:
                transformer_investment = 0
                    
            # Periodical Costs        
            if transformer_investment > 0:     ### Wert auf beide Busse anwenden! (Es muss die Summe der Busse, inklusive des Wirkungsgrades einbezogen werden!!!)
                periodical_costs = t['periodical costs [CU/(kW a)]']*transformer_investment
                total_periodical_costs = total_periodical_costs + periodical_costs
                investments_to_be_made[t['label']] = (str(round(transformer_investment, 2))+' kW; '+str(round(periodical_costs,2))+' cost units (p.a.)')
            else:
                periodical_costs = 0
            print('Periodical costs (p.a.): ' + str(round(periodical_costs, 2)) + ' cost units p.a.')
            
            print('--------------------------------------------------------') 
            
            
    print("*********************************************************") 
    print("***STORAGES**********************************************") 
    print("*********************************************************")
    print('--------------------------------------------------------')          
    for i, s in nd['storages'].iterrows():    
        if s['active']:
            print(s['label'])                     
            storages = outputlib.views.node(results, s['label'])
            flowsum = storages['sequences'].sum()
            #print(flowsum)
            print('Energy Output from ' +  s['label'] + ': ' + str(round(flowsum[[1][0]], 2)) + ' kWh')
            print('Energy Input to ' +  s['label'] + ': ' + str(round(flowsum[[2][0]], 2)) + ' kWh')
            
            storage = outputlib.views.node(results, s['label'])
            flowmax = storage['sequences'].max()
            #variable_costs = s['variable input costs'] * flowsum[[0][0]]
            print('Max. Capacity: ' + str(round(flowmax[[0][0]], 2)) + ' kW')
            
            storage = outputlib.views.node(results, s['label'])
            flowsum = storage['sequences'].sum()
            variable_costs = s['variable input costs'] * flowsum[[0][0]]
            print('Total variable costs for: ' + str(round(variable_costs, 2)) + ' cost units')
            total_costs = total_costs + variable_costs 
    
            # Investment Capacity
            if s['max. investment capacity [kW]'] > 0:
                storage_node = esys.groups[s['label']]
                bus_node = esys.groups[s['bus']]
                storage_investment = results[storage_node, None]['scalars']['invest']
                print('Investment Capacity: ' + str(round(storage_investment, 2)) + ' kW')
    
            else:
                storage_investment = 0
                
            # Periodical Costs
            if storage_investment > float(s['existing capacity [kW]']):
                periodical_costs = s['periodical costs [CU/(kW a)]']*storage_investment
                total_periodical_costs = total_periodical_costs + periodical_costs
                investments_to_be_made[s['label']] = (str(round(storage_investment, 2))+' kW; '+str(round(periodical_costs,2))+' cost units (p.a.)')
            else:
                periodical_costs = 0
            print('Periodical costs (p.a.): ' + str(round(periodical_costs, 2)) + ' cost units p.a.')
            
            print('--------------------------------------------------------')        
    
    print("*********************************************************") 
    print("***POWERLINES********************************************") 
    print("*********************************************************")
    print('--------------------------------------------------------CAPACITY BEI MEHREREN AUSGÄNGEN PRÜFEN')  
    for i, p in nd['powerlines'].iterrows():    
        if p['active']:
            print(p['label'])   
                        
            powerline = outputlib.views.node(results, p['label'])
            
            if powerline:
                
                flowsum = powerline['sequences'].sum()
                #transformer_test = flowsum
                #transformer = outputlib.views.node(results, t['label'])
                flowmax = powerline['sequences'].max()
                        
                
                if p['(un)directed'] == 'directed':
                    print('Total Energy Output to ' +  p['bus_2'] + ': ' + str(round(flowsum[[1][0]], 2)) + ' kWh')
                    max_powerline_flow = flowmax[1]                
                else:    
                    print('Total Energy Output to ' +  p['bus_2'] + ': ' + str(round(flowsum[[0][0]], 2)) + ' kWh')
                    print('Total Energy Output to ' +  p['bus_1'] + ': ' + str(round(flowsum[[1][0]], 2)) + ' kWh')
                    max_powerline_flow = flowmax[1]
        
                print('Max. Capacity: ' + str(round(max_powerline_flow, 2)) + ' kW') ### Wert auf beide Busse anwenden!
                if p['undirected'] != 'None': 
                    print('WARNING: Capacity to bus2 will be added later')
                    
                #transformer = outputlib.views.node(results, t['label'])
                #flowsum = transformer['sequences'].sum()
                variable_costs = p['variable input costs'] * flowsum[[0][0]]
                total_costs = total_costs + variable_costs
                print('Variable Costs: ' + str(round(variable_costs, 2)) + ' cost units')
                total_costs = total_costs + variable_costs
                
                # Investment Capacity
                if p['max. investment capacity [kW]'] > 0:
                    powerline_node = esys.groups[p['label']]
                    bus_node = esys.groups[p['output']]
                    powerline_investment = results[powerline_node, bus_node]['scalars']['invest']
                    print('Investment Capacity: ' + str(round(powerline_investment, 2)) + ' kW')
        
                else:
                    powerline_investment = 0
                        
                # Periodical Costs        
                if powerline_investment > 0:     ### Wert auf beide Busse anwenden! (Es muss die Summe der Busse, inklusive des Wirkungsgrades einbezogen werden!!!)
                    periodical_costs = p['periodical costs [CU/(kW a)]']#*powerline_investment
                    total_periodical_costs = total_periodical_costs + periodical_costs
                    investments_to_be_made[p['label']] = (str(round(powerline_investment, 2))+' kW; '+str(round(periodical_costs,2))+' cost units (p.a.)')
                else:
                    periodical_costs = 0
                print('Periodical costs (p.a.): ' + str(round(periodical_costs, 2)) + ' cost units p.a.')
            else:
                print('Total Energy Output to ' +  p['bus_2'] + ': 0 kWh')
            print('--------------------------------------------------------') 
    
 
    print("*********************************************************") 
    print("***SUMMARY***********************************************") 
    print("*********************************************************")
    print('--------------------------------------------------------')
    meta_results = outputlib.processing.meta_results(om)
    meta_results_objective = meta_results['objective']
    print('Total System Costs:             ' + str(round(meta_results_objective, 1)) + ' cost units')
    print('Total Variable Costs:           ' + str(round(total_costs)) + ' cost units')
    print('Total Periodical Costs (p.a.):  ' + str(round(total_periodical_costs)) + ' cost units p.a.')
    print('Total Energy Demand:            ' + str(round(total_demand)) + ' kWh')
    print('Total Energy Usage:             ' + str(round(total_usage)) + ' kWh')
    print('--------------------------------------------------------') 
    print('Investments to be made:')
    print(investments_to_be_made)
    print('--------------------------------------------------------')             
    print("*********************************************************\n") 
        
