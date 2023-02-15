# -*- coding: utf-8 -*-
from oemof import solph
from memory_profiler import memory_usage
from datetime import datetime


def constraint_optimization_against_two_values(
    om: solph.Model, limit: float
) -> solph.Model:
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
    ##########################
    # PERIODICAL CONSTRAINTS #
    ##########################
    # extract all investment flows where periodical constraints apply
    for (i, o) in om.flows:
        if hasattr(om.flows[i, o].investment, "periodical_constraint_costs"):
            invest_flows[(i, o)] = om.flows[i, o].investment
    limit_name = "invest_limit_" + "periodical_constraints"
    # Setting the equation representing the sum of the periodic
    # emissions
    setattr(
        om,
        limit_name,
        po.Expression(
            expr=sum(
                om.InvestmentFlow.invest[inflow, outflow]
                * getattr(invest_flows[inflow, outflow], "periodical_constraint_costs")
                for (inflow, outflow) in invest_flows
            )
        ),
    )
    ##########################
    # NONCONVEX CONSTRAINTS  #
    ##########################
    invest_flows2 = {}
    # extract all investment flows where fix constraints apply
    for (i, o) in om.flows:
        if hasattr(om.flows[i, o].investment, "fix_constraint_costs"):
            invest_flows2[(i, o)] = om.flows[i, o].investment
    limit_name1 = "invest_limit_" + "nonconvex_constraints"
    # Setting the equation representing the sum of the nonconvex
    # emissions
    setattr(
        om,
        limit_name1,
        po.Expression(
            expr=sum(
                getattr(invest_flows2[inflow, outflow], "fix_constraint_costs")
                for (inflow, outflow) in invest_flows2
            )
        ),
    )
    ##########################
    # VARIABLE CONSTRAINTS   #
    ##########################
    flows = {}
    # extract all investment flows where variable constraints apply
    for (i, o) in om.flows:
        if hasattr(om.flows[i, o], "emission_factor"):
            flows[(i, o)] = om.flows[i, o]
    limit_name2 = "integral_limit_" + "variable_constraints"
    # Setting the equation representing the sum of the variable
    # emissions
    setattr(
        om,
        limit_name2,
        po.Expression(
            expr=sum(
                om.flow[inflow, outflow, t]
                * om.timeincrement[t]
                * sequence(getattr(flows[inflow, outflow], "emission_factor"))[t]
                for (inflow, outflow) in flows
                for t in om.TIMESTEPS
            )
        ),
    )
    ##########################
    # STORAGE CONSTRAINTS    #
    ##########################
    comp = {}
    comp_fix = {}
    # extract all investment flows where periodical / fix constraints
    # apply
    for num in om.GenericInvestmentStorageBlock.INVESTSTORAGES.data():
        if hasattr(num.investment, "periodical_constraint_costs"):
            comp[num] = num.investment
        if hasattr(num.investment, "fix_constraint_costs"):
            comp_fix[num] = num.investment
    # Setting the equation representing the sum of the periodic
    # emissions
    limit_name3 = "invest_limit_storage"
    setattr(
        om,
        limit_name3,
        po.Expression(
            expr=sum(
                om.GenericInvestmentStorageBlock.invest[num]
                * getattr(comp[num], "periodical_constraint_costs")
                for num in comp
            )
        ),
    )
    # Setting the equation representing the sum of the nonconvex
    # emissions
    limit_name4 = "invest_limit_fix_storage"
    setattr(
        om,
        limit_name4,
        po.Expression(
            expr=sum(getattr(comp_fix[num], "fix_constraint_costs") for num in comp_fix)
        ),
    )
    # Setting the equation representing the overall limit for the sum of
    # all appearing constraints
    setattr(
        om,
        limit_name + "_constraint",
        po.Constraint(
            expr=(
                (
                    getattr(om, limit_name)
                    #+ getattr(om, limit_name1)
                    + getattr(om, limit_name2)
                    + getattr(om, limit_name4)
                    + getattr(om, limit_name3)
                )
                <= limit
            )
        ),
    )
    # Return of the opimization model extended by the new equations
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

    for k, j in nd["competition constraints"].iterrows():
        if j["active"]:
            flows = {}
            # Create a list in which the limit value for each time step of
            # the energy_system is defined, since the constraints are applied
            # to the flow, and here the system is to be dimensioned for the
            # time step with the maximum added space/energy requirement
            # get the two outflows which are competitive
            for i, o in om.flows:
                if i == energy_system.groups[j["component 1"]]:
                    # first output flow of the component is used to set up
                    # the competition
                    if o == (list(energy_system.groups[j["component 1"]].outputs)[0]):
                        setattr(om.flows[i, o], "competition_factor", j["factor 1"])
                        flows[(i, o)] = om.flows[i, o]
                elif i == energy_system.groups[j["component 2"]]:
                    setattr(om.flows[i, o], "competition_factor", j["factor 2"])
                    flows[(i, o)] = om.flows[i, o]

            # rule which is used for the constraint
            # rule : (outflow(comp1) * factor1 + outflow(comp2) * factor2)
            # <= limit

            def competition_rule(om):
                competition_flow = sum(
                    om.InvestmentFlow.invest[i, o] * om.flows[i, o].competition_factor
                    for (i, o) in flows
                )
                limit = j["limit"]
                limit = limit - (
                    sum(om.flows[i, o].investment.existing for (i, o) in flows)
                )
                return limit >= competition_flow

            setattr(
                om,
                j["component 1"] + "_" + j["component 2"] + "competition_constraint",
                po.Constraint(om.TIMESTEPS, expr=competition_rule),
            )

    return om


def constraint_optimization_of_criterion_adherence_to_a_minval(
    om: solph.Model, limit: float
) -> solph.Model:

    import pyomo.environ as po
    from oemof.solph.plumbing import sequence

    flows = {}
    for (i, o) in om.flows:
        if hasattr(om.flows[i, o].investment, "constraint2"):
            flows[(i, o)] = om.flows[i, o].investment

    limit_name = "invest_limit_" + "space2"

    setattr(
        om,
        limit_name,
        po.Expression(
            expr=sum(
                om.flow[inflow, outflow, t]
                * om.timeincrement[t]
                * sequence(getattr(flows[inflow, outflow], "constraint2"))[t]
                for (inflow, outflow) in flows
                for t in om.TIMESTEPS
            )
        ),
    )

    setattr(
        om,
        limit_name + "_constraint2",
        po.Constraint(expr=((getattr(om, limit_name) >= limit))),
    )

    return om


def least_cost_model(
    energy_system: solph.EnergySystem,
    num_threads: int,
    nodes_data: dict,
    busd: dict,
    solver: str,
) -> solph.Model:
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
    logging.info("\t ********************************************************")
    logging.info("   " + "Create Energy System...")
    # creation of a least cost model from the energy system
    om = solph.Model(energy_system)
    if (
        str(next(nodes_data["energysystem"].iterrows())[1]["constraint cost limit"])
        != "none"
        and str(next(nodes_data["energysystem"].iterrows())[1]["constraint cost limit"])
        != "None"
    ):
        limit = float(
            next(nodes_data["energysystem"].iterrows())[1]["constraint cost limit"]
        )
        om = constraint_optimization_against_two_values(om, limit)
    if (
        str(
            next(nodes_data["energysystem"].iterrows())[1][
                "minimum final energy reduction"
            ]
        )
        != "none"
        and str(
            next(nodes_data["energysystem"].iterrows())[1][
                "minimum final energy reduction"
            ]
        )
        != "None"
    ):
        limit = float(
            next(nodes_data["energysystem"].iterrows())[1][
                "minimum final energy reduction"
            ]
        )
        om = constraint_optimization_of_criterion_adherence_to_a_minval(om, limit)

    # limit for two given outflows e.g area_competition
    if "competition constraints" in nodes_data:
        om = competition_constraint(om, nodes_data, energy_system)

    for j, z in nodes_data["links"].iterrows():
        for i, b in om.flows.keys():
            # searching for the output-flows of the link labeled
            # z['label']
            if isinstance(i, solph.custom.Link) and str(i) == z["label"]:
                # check if the link is undirected and ensure that the
                # solver has to invest the same amount on both
                # directions
                if z["(un)directed"] == "undirected":
                    p = energy_system.groups[z["label"]]
                    solph.constraints.equate_variables(
                        om,
                        om.InvestmentFlow.invest[p, busd[z["bus1"]]],
                        om.InvestmentFlow.invest[p, busd[z["bus2"]]],
                    )
    #            # check if the link is directed and ensure that the
    #            # solver does not invest on the second direction
    #            elif z['(un)directed'] == 'directed':
    #                p = energy_system.groups[z['label']]
    #
    #                def input_rule(om, t):
    #                    inflow = (om.flow[busd[z['bus2']], p, t])
    #                    return inflow == 0
    #
    #                om.InvestmentFlow.invest[p, busd[z['bus1']]] = 0
    #                setattr(om, z['label'] + "input_constraint",
    #                        po.Constraint(om.TIMESTEPS, expr=input_rule))
    logging.info(
        "   " + "******************************************************" + "***"
    )
    logging.info("   " + "Starting Optimization with " + solver + "-Solver")

    # solving the linear problem using the given solver
    if solver== 'gurobi':
        om.solve(solver=solver, cmdline_options={"threads": num_threads})
    else:
        om.solve(solver=solver)
    logging.info("\t Memory Usage during processing:" + str(memory_usage()))
    return om
