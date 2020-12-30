# -*- coding: utf-8 -*-
def constraint(om, limit):
    import pyomo.environ as po
    from oemof.solph.plumbing import sequence

    invest_flows = {}
    for (i, o) in om.flows:
        if hasattr(om.flows[i, o].investment, "periodical_constraint_costs"):
            invest_flows[(i, o)] = om.flows[i, o].investment

    limit_name = "invest_limit_" + "space"

    setattr(om, limit_name, po.Expression(
        expr=sum(om.InvestmentFlow.invest[inflow, outflow] *
                 getattr(invest_flows[inflow, outflow],
                         "periodical_constraint_costs")
                 for (inflow, outflow) in invest_flows
                 )))

    ############
    flows = {}
    for (i, o) in om.flows:
        if hasattr(om.flows[i, o], "emission_factor"):
            flows[(i, o)] = om.flows[i, o]

    limit_name1 = "integral_limit_" + "emission_factor"

    setattr(om, limit_name1, po.Expression(
        expr=sum(om.flow[inflow, outflow, t]
                 * om.timeincrement[t]
                 * sequence(getattr(flows[inflow, outflow],
                                    "emission_factor"))[t]
                 for (inflow, outflow) in flows
                 for t in om.TIMESTEPS)))

    setattr(om, limit_name + "_constraint", po.Constraint(
        expr=((getattr(om, limit_name) + getattr(om, limit_name1)) <= limit)))

    return om

def least_cost_model(energy_system, num_threads, nodes_data, busd):
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
    
    import oemof
    import logging

    # add nodes and flows to energy system
    logging.info('   '+"******************************************************"
                 + "***")
    logging.info('   '+'Create Energy System...')
    
    # creation of a least cost model from the energy system
    om = oemof.solph.Model(energy_system)

    om = constraint(om, int(nodes_data['energysystem']['constraint costs /(CU)']))

    for j, z in nodes_data['links'].iterrows():
        for i, b in om.flows.keys():
            # searching for the output-flows of the link labeled
            # z['label']
            if isinstance(i, oemof.solph.custom.Link) and str(i) == z['label']:
                # check if the link is undirected and ensure that the
                # solver has to invest the same amount on both
                # directions
                if z['(un)directed'] == 'undirected':
                    p = energy_system.groups[z['label']]
                    oemof.solph.constraints.equate_variables(
                            om,
                            om.InvestmentFlow.invest[p, busd[z['bus_1']]],
                            om.InvestmentFlow.invest[p, busd[z['bus_2']]]
                    )
                # check if the link is directed and ensure that the
                # solver does not invest on the second direction
                elif z['(un)directed'] == 'directed':
                    p = energy_system.groups[z['label']]
                    om.InvestmentFlow.invest[p, busd[z['bus_2']]] = 0
    
    logging.info('   '+"******************************************************"
                 + "***")
    logging.info('   '+"Starting Optimization with CBC-Solver")

    # solving the linear problem using the given solver
    om.solve(solver='cbc', cmdline_options={"threads": num_threads})

    return om
