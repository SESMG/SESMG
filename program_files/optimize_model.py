# -*- coding: utf-8 -*-
def least_cost_model(energy_system):
    """
    Solves a given energy system model.
    Solves a given energy system for least costs and returns the
    optimized energy system.

    ----    
        
    Keyword arguments:

        energy_system : obj:
            -- energy system consisting a number of components
            
    ----
    
    Returns:
       om: obj:'Model'
           -- solved oemof model
           
    ----   
    @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
    """
    
    from oemof import solph
    import logging

    # add nodes and flows to energy system
    logging.info('   '+"******************************************************"
                 + "***")
    logging.info('   '+'Create Energy System...')
    
    # creation of a least cost model from the energy system
    om = solph.Model(energy_system)

    logging.info('   '+"******************************************************"
                 + "***")
    logging.info('   '+"Starting Optimization with CBC-Solver")

    # solving the linear problem using the given solver
    om.solve(solver='cbc')

    return om
