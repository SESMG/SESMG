# -*- coding: utf-8 -*-
def least_cost_model(nodes_data, energy_system):
    """
    Solves a given energy system for least costs and returns the 
    optimized energy system.

    ----    
        
    Keyword arguments:
        
        nodes_data : obj:'dict'
           -- dictionary containing data from excel scenario file

        energy_system : obj:
            -- energy system consisting a number of components
            
    ----
    
    Returns:
       nodes_data : obj:'dict'
           -- dictionary containing data from excel scenario file    
           
    ----
    
    @ Christian Klemm - christian.klemm@fh-muenster.de, 14.01.2020

    """
    
    from oemof import solph
    import logging
    
    esys = energy_system
    
    # add nodes and flows to energy system
    print("*********************************************************")
    logging.info('Starting Optimization...')

   # esys.add(nodes)
    
    # creation of a least cost model from the energy system
    om = solph.Model(esys)
    om.receive_duals()
    #del solph.Model.dual(esys)
    # solving the linear problem using the given solver
    om.solve(solver='cbc')
    
    return om