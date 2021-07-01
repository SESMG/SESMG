# -*- coding: utf-8 -*-
from oemof import solph


def constraint_optimization_against_two_values(om: solph.Model,
                                               limit: int) -> solph.Model:
    """
        Function for optimization against two parameters
        (e.g. monetary, emissions)

        :param om: oemof solph model to which the constraints will be \
                   added
        :type om: oemof.solph.Model
        :param limit: maximum value for the second parameter for the \
                      whole energysystem
        :type limit: int
        :return: - **om** (oemof.solph.Model) - oemof solph Model within \
                                                the constraints
    """
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

def competition_constraint(om, nd, energy_system):
    """
        The outflow_competition method is used to optimise the sum of
        the outflows of two given components multiplied by two different
        factors (e.g. the space required for a kW) against a given limit.
        
        :param om: oemof solph model to which the constraints will be \
                   added
        :type om: oemof.solph.Model
        :param nd:  dictionary containing all excel sheets of the spread
                    sheet
        :type nd: dict
        :param energy_system: the oemof created energy_system containing
                              all created components
        :type energy_system: oemof.solph.energy_system
        :return: - **om** (oemof.solph.Model) - oemof solph Model within \
                                                the constraints
    """
    import pyomo.environ as po
    for k, j in nd['competition constraints'].iterrows():
        flows = {}
        # Create a list in which the limit value for each time step of
        # the energy_system is defined, since the constraints are applied
        # to the flow, and here the system is to be dimensioned for the
        # time step with the maximum added space/energy requirement
        # get the two outflows which are competitive
        for i, o in om.flows:
            if i == energy_system.groups[j['component 1']]:
                # first output flow of the component is used to set up
                # the competition
                if o == (list(energy_system.groups[j['component 1']].outputs)
                         [0]):
                    setattr(om.flows[i, o], "competition_factor", j['factor 1'])
                    flows[(i, o)] = om.flows[i, o]
            elif i == energy_system.groups[j['component 2']]:
                setattr(om.flows[i, o], "competition_factor", j['factor 2'])
                flows[(i, o)] = om.flows[i, o]
                
        # rule which is used for the constraint
        # rule : (outflow(comp1) * factor1 + outflow(comp2) * factor2) <= limit
        
        def competition_rule(om):
            competition_flow = \
                sum(om.InvestmentFlow.invest[i, o] * om.flows[i, o].competition_factor
                    for (i, o) in flows)
            limit = j['limit']
            limit = limit - (sum(om.flows[i, o].investment.existing for (i, o) in flows))
            return (limit >= competition_flow)

        setattr(om, j['component 1'] + '_' + j['component 2']
                + "competition_constraint",
                po.Constraint(om.TIMESTEPS, expr=competition_rule))
    
    return om

def least_cost_model(energy_system: solph.EnergySystem, num_threads: int,
                     nodes_data: dict, busd: dict, solver: str) -> solph.Model:
    """
        Solves a given energy system model.
        Solves a given energy system for least costs and returns the
        optimized energy system.

        :param energy_system: energy system consisting a number of \
            components
        :type energy_system: oemof.solph.Energysystem
        :param num_threads: number of threads the solver is allowed to use
        :type num_threads: int
        :param nodes_data: dictionary containing all components \
                           information out of the excel spreadsheet
        :type nodes_data: dict
        :param busd: dictionary containing the buses of the energysystem
        :type busd: dict

        :return: - **om** (oemof.solph.Model) - solved oemof model

        Christian Klemm - christian.klemm@fh-muenster.de
    """

    import logging
    import math
    import pyomo.environ as po

    # add nodes and flows to energy system
    logging.info(
        '   ' + "******************************************************"
        + "***")
    logging.info('   ' + 'Create Energy System...')

    # creation of a least cost model from the energy system
    om = solph.Model(energy_system)
    if (str(next(nodes_data["energysystem"].iterrows())[1]["constraint cost limit"]) != 'none' and
          str(next(nodes_data["energysystem"].iterrows())[1]["constraint cost limit"]) != 'None'):
        limit = float(next(nodes_data["energysystem"].iterrows())[1]["constraint cost limit"])
        om = constraint_optimization_against_two_values(om, limit)
   
    # limit for two given outflows e.g area_competition
    if "competition constraints" in nodes_data:
        om = competition_constraint(om, nodes_data, energy_system)

    for j, z in nodes_data['links'].iterrows():
        for i, b in om.flows.keys():
            # searching for the output-flows of the link labeled
            # z['label']
            if isinstance(i, solph.custom.Link) and str(i) == z['label']:
                # check if the link is undirected and ensure that the
                # solver has to invest the same amount on both
                # directions
                if z['(un)directed'] == 'undirected':
                    p = energy_system.groups[z['label']]
                    solph.constraints.equate_variables(
                        om,
                        om.InvestmentFlow.invest[p, busd[z['bus1']]],
                        om.InvestmentFlow.invest[p, busd[z['bus2']]]
                    )
                # check if the link is directed and ensure that the
                # solver does not invest on the second direction
                elif z['(un)directed'] == 'directed':
                    p = energy_system.groups[z['label']]

                    def input_rule(om, t):
                        inflow = (om.flow[busd[z['bus2']], p, t])
                        return inflow == 0

                    om.InvestmentFlow.invest[p, busd[z['bus1']]] = 0
                    setattr(om, z['label'] + "input_constraint",
                            po.Constraint(om.TIMESTEPS, expr=input_rule))

    logging.info(
        '   ' + "******************************************************"
        + "***")
    logging.info('   '+"Starting Optimization with "+solver+"-Solver")


    # solving the linear problem using the given solver
    om.solve(solver=solver, cmdline_options={"threads": num_threads})

    return om
