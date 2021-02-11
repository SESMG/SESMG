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


def least_cost_model(energy_system: solph.EnergySystem, num_threads: int,
                     nodes_data: dict, busd: dict) -> solph.Model:
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

        Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
    """

    import logging

    # add nodes and flows to energy system
    logging.info(
        '   ' + "******************************************************"
        + "***")
    logging.info('   ' + 'Create Energy System...')

    # creation of a least cost model from the energy system
    om = solph.Model(energy_system)
    if (str(nodes_data['energysystem']['constraint costs /(CU)'][0]) != 'x' and
            str(nodes_data['energysystem']['constraint costs /(CU)'][
                    0]) != 'None'):
        om = \
            constraint_optimization_against_two_values(
                om, int(nodes_data['energysystem']['constraint costs /(CU)']))

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
                        om.InvestmentFlow.invest[p, busd[z['bus_1']]],
                        om.InvestmentFlow.invest[p, busd[z['bus_2']]]
                    )
                # check if the link is directed and ensure that the
                # solver does not invest on the second direction
                elif z['(un)directed'] == 'directed':
                    p = energy_system.groups[z['label']]
                    om.InvestmentFlow.invest[p, busd[z['bus_2']]] = 0

    logging.info(
        '   ' + "******************************************************"
        + "***")
    logging.info('   ' + "Starting Optimization with CBC-Solver")

    # solving the linear problem using the given solver
    om.solve(solver='cbc', cmdline_options={"threads": num_threads})

    return om
