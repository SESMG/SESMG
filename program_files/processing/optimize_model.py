"""
    Gregor Becker - gregor.becker@fh-muenster.de
    Christian Klemm - christian.klemm@fh-muenster.de
"""

# -*- coding: utf-8 -*-
import pandas
from oemof import solph
from memory_profiler import memory_usage


def constraint_optimization_against_two_values(
    om: solph.Model, limit: float, storages=False
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
        :param storages: boolean indicating whether or not the energy \
            system has a storage as an investment alternative.
        :type storages: bool
        
        :return: - **om** (oemof.solph.Model) - oemof solph Model \
            within the added constraints
    """
    import pyomo.environ as po
    from oemof.solph import sequence
    
    periodical_flows = {}
    nonconvex_flows = {}
    variable_flows = {}
   
    for (inflow, outflow) in om.flows:
        # extract all investment flows where periodical constraints apply
        if hasattr(om.flows[inflow, outflow].investment,
                   "periodical_constraint_costs"):
            periodical_flows[(inflow, outflow)] = \
                om.flows[inflow, outflow].investment
            
        # extract all investment flows where fix constraints apply
        if hasattr(om.flows[inflow, outflow].investment,
                   "fix_constraint_costs")\
                and getattr(om.flows[inflow, outflow].investment,
                            "nonconvex"):
            nonconvex_flows[(inflow, outflow)] = \
                om.flows[inflow, outflow].investment

        # extract all investment flows where variable constraints apply
        if hasattr(om.flows[inflow, outflow], "emission_factor"):
            variable_flows[(inflow, outflow)] = om.flows[inflow, outflow]
            
    ##########################
    # PERIODICAL CONSTRAINTS #
    ##########################
    # Setting the equation representing the sum of the periodic
    # emissions calculated by applied investment capacity * periodical
    # constraint costs
    setattr(
        om,
        "invest_limit_periodical_constraints",
        po.Expression(
            expr=sum(
                om.InvestmentFlowBlock.invest[(inflow, outflow, 0)]
                * getattr(periodical_flows[inflow, outflow],
                          "periodical_constraint_costs")
                for (inflow, outflow) in periodical_flows
            )
        ),
    )

    ##########################
    # NONCONVEX CONSTRAINTS  #
    ##########################
    # Setting the equation representing the sum of the nonconvex
    # emissions om.InvestmentFlow.invest_status represents the boolean
    # indicating whether there is an invest done or not which is
    # needed to use only the applying constraints
    setattr(
        om,
        "invest_limit_nonconvex_constraints",
        po.Expression(
            expr=sum(
                (getattr(nonconvex_flows[inflow, outflow],
                         "fix_constraint_costs")
                 * om.InvestmentFlowBlock.invest_status[(inflow, outflow, 0)])
                for (inflow, outflow) in nonconvex_flows)
        ),
    )
    
    ##########################
    # VARIABLE CONSTRAINTS   #
    ##########################
    # Setting the equation representing the sum of the variable
    # emissions calculated by flow value of investigated component in
    # investigated time increment * time increment length * variable
    # constraint costs
    setattr(
        om,
        "integral_limit_variable_constraints",
        po.Expression(
            expr=sum(
                om.flow[(inflow, outflow, 0, t)]
                * om.timeincrement[t]
                * sequence(getattr(variable_flows[inflow, outflow],
                                   "emission_factor"))[t]
                for (inflow, outflow) in variable_flows
                for t in om.TIMESTEPS
            )
        ),
    )
    
    ##########################
    # STORAGE CONSTRAINTS    #
    ##########################
    # Special treatment of the storages is necessary, because here the
    # investment variable is not on one of the flows, but on the
    # storage component itself.
    comp = {}
    comp_fix = {}
    # extract all investment flows where periodical / fix constraints
    # apply
    if storages:
        invest_storages = om.GenericInvestmentStorageBlock.INVESTSTORAGES
        for num in invest_storages.data():
            if hasattr(num.investment, "periodical_constraint_costs"):
                comp[num] = num.investment
            if hasattr(num.investment, "fix_constraint_costs") \
                    and getattr(num.investment, "nonconvex"):
                comp_fix[num] = num.investment
                
        # Setting the equation representing the sum of the periodic
        # emissions
        setattr(
            om,
            "invest_limit_storage",
            po.Expression(
                expr=sum(
                    om.GenericInvestmentStorageBlock.invest[(num, 0)]
                    * getattr(comp[num], "periodical_constraint_costs")
                    for num in comp
                )
            ),
        )
    
        # Setting the equation representing the sum of the nonconvex
        # emissions
        setattr(
            om,
            "invest_limit_fix_storage",
            po.Expression(
                expr=sum((
                    getattr(comp_fix[num], "fix_constraint_costs")
                    * om.GenericInvestmentStorageBlock.invest_status[num])
                    for num in comp_fix)
            ),
        )
    else:
        setattr(om, "invest_limit_storage", 0)
        setattr(om, "invest_limit_fix_storage", 0)
        
    # Setting the equation representing the overall limit for the sum of
    # all appearing constraints
    setattr(
        om,
        "second_criterion_constraint_equation",
        po.Constraint(
            expr=(
                (
                    getattr(om, "invest_limit_periodical_constraints")
                    + getattr(om, "invest_limit_nonconvex_constraints")
                    + getattr(om, "integral_limit_variable_constraints")
                    + getattr(om, "invest_limit_storage")
                    + getattr(om, "invest_limit_fix_storage")
                )
                <= limit
            )
        ),
    )
    # Return of the optimization model extended by the new equations
    return om


def competition_constraint(om: solph.Model,
                           comp_constraints: pandas.DataFrame,
                           energy_system: solph.EnergySystem) -> solph.Model:
    """
        The outflow_competition method is used to optimise the sum of
        the outflows of two given components multiplied by two
        different factors (e.g. the space required for a kW) against a
        given limit.
        
        :param om: oemof solph model to which the constraints will be \
            added
        :type om: oemof.solph.Model
        :param comp_constraints:  pandas dataframe of the \
            competition constraint sheet
        :type comp_constraints: pandas.DataFrame
        :param energy_system: the oemof created energy_system \
            containing all created components
        :type energy_system: oemof.solph.energy_system
        
        :return: - **om** (oemof.solph.Model) - oemof solph Model \
            within the newly added competition constraints
    """
    import pyomo.environ as po
    
    # Filter only the rows in comp_constraints where the "active" column
    # is equal to 1
    active_df = comp_constraints.loc[comp_constraints["active"] == 1]

    # Iterate over active competition constraints
    for num, row in active_df.iterrows():
    
        # Dictionary to store relevant flows
        flows = {}

        # Create a dict of flows and their associated competition
        # factors
        index = 1
        constr_name = ""
        while "component {}".format(index) in row:
            if row["component {}".format(index)] not in ["None", 0, "none"]:
    
                # Get the flow from the energy system
                flow = energy_system.groups[row["component {}".format(index)]]

                # Find the corresponding flow tuple in the solph model
                flow_keys = list(om.flows.keys())
                flow_tuple = next((
                    tpl for tpl in flow_keys if tpl[0] == flow), None)

                # If the flow tuple is found, set the competition factor
                # and add the flow to the dictionary
                if flow_tuple is not None:
                    setattr(om.flows[flow_tuple],
                            "competition_factor",
                            row["factor {}".format(index)])
                    flows[flow_tuple] = om.flows[flow_tuple[0], flow_tuple[1]]
                    
            constr_name += (row["component {}".format(index)] + "_")
            index += 1

        # Define a rule for the competition constraint
        # rule : sum(outflow(x) * factor x) <= (limit - existing)
        def competition_rule(om):
            competition_flow = sum(
                om.InvestmentFlowBlock.invest[(inflow, outflow, 0)]
                * om.flows[inflow, outflow].competition_factor
                for (inflow, outflow) in flows
            )
            return competition_flow

        # Add an expression to the solph model based on the competition
        # rule
        setattr(om, constr_name[:-1], po.Expression(expr=competition_rule))

        # Calculate the constraint limit
        limit = row["limit"] - (
           sum(om.flows[inflow, outflow].investment.existing
               for (inflow, outflow) in flows)
            )

        # Add the competition constraint to the solph model
        setattr(
            om,
            constr_name + "constraint",
            po.Constraint(expr=(getattr(om, constr_name[:-1]) <= limit)))
            
    return om


def constraint_optimization_of_criterion_adherence_to_a_minval(
        om: solph.Model, limit: float) -> solph.Model:
    """
        Using this method, the solver can be forced to reduce the final
        energy demand by insulation measures. In this case, all flows
        from the insulation investments are summed up and the solver is
        forced to at least reach the value limit.
        
        :param om: oemof solph model to which the constraints will be \
            added
        :type om: oemof.solph.Model
        :param limit: Value by which the solver must reduce the final \
            energy demand by investing in insulation measures.
        :type limit: float
        
        :return: - **om** (oemof.solph.Model) - oemof solph Model \
            within the newly added constraints
    """
    import pyomo.environ as po
    from oemof.solph import sequence

    flows = {}
    # Search for all flows that contain the parameter constraint2,
    # since these components can be used to reduce the final energy
    # demand by at least the value limit.
    for (inflow, outflow) in om.flows:
        if hasattr(om.flows[inflow, outflow].investment, "constraint2"):
            flows[(inflow, outflow)] = om.flows[inflow, outflow].investment

    # calculate the sum of the total flow reduction applied by the
    # investment in insulation measures
    setattr(
        om,
        "limit_constraint2",
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
        "reduce_final_energy_demand",
        po.Constraint(expr=(getattr(om, "limit_constraint2") >= limit)),
    )

    return om


def least_cost_model(energy_system: solph.EnergySystem, num_threads: int,
                     nodes_data: dict, busd: dict, solver: str) -> solph.Model:
    """
        Solves a given energy system for least costs and returns the
        optimized energy system.

        :param energy_system: energy system consisting a number of \
            components
        :type energy_system: oemof.solph.Energysystem
        :param num_threads: number of threads the solver is allowed to \
            use
        :type num_threads: int
        :param nodes_data: dictionary containing all components \
                           information out of the excel spreadsheet
        :type nodes_data: dict
        :param busd: dictionary containing the buses of the energysystem
        :type busd: dict
        :param solver: str holding the user chosen solver label
        :type solver: str

        :return: - **om** (oemof.solph.Model) - solved oemof model
    """
    import logging

    # add nodes and flows to energy system
    logging.info("\t " + 56 * "*")
    logging.info("\t Create Energy System...")
    
    # creation of a least cost model from the energy system
    om = solph.Model(energy_system)
    column_label = "constraint cost limit"
    if str(next(nodes_data["energysystem"].iterrows())[1][column_label]) \
            not in ["none", "None"]:
        limit = float(
            next(nodes_data["energysystem"].iterrows())[1][column_label]
        )
        if len(nodes_data["storages"].loc[
                   nodes_data["storages"]["active"] == 1]) > 0:
            om = constraint_optimization_against_two_values(om=om,
                                                            limit=limit,
                                                            storages=True)
        else:
            om = constraint_optimization_against_two_values(om=om,
                                                            limit=limit)
    column_label = "minimum final energy reduction"
    if str(next(nodes_data["energysystem"].iterrows())[1][column_label]) \
            not in ["none", "None"]:
        limit = float(
            next(nodes_data["energysystem"].iterrows())[1][column_label]
        )
        om = constraint_optimization_of_criterion_adherence_to_a_minval(
            om=om, limit=limit)

    # limit for two given outflows e.g area_competition
    if "competition constraints" in nodes_data:
        om = competition_constraint(
            om=om,
            comp_constraints=nodes_data["competition constraints"],
            energy_system=energy_system)

    for num, row in nodes_data["links"].iterrows():
        for comp, outflow in om.flows.keys():
            # searching for the output-flows of the link labeled
            # z['label']
            if isinstance(comp, solph.components.Link) \
                    and str(comp) == row["label"]:
                # check if the link is undirected and ensure that the
                # solver has to invest the same amount on both
                # directions
                if row["(un)directed"] == "undirected":
                    comp = energy_system.groups[row["label"]]
                    solph.constraints.equate_variables(
                        model=om,
                        var1=om.InvestmentFlowBlock.invest[
                            comp, busd[row["bus1"]]],
                        var2=om.InvestmentFlowBlock.invest[
                            comp, busd[row["bus2"]]],
                    )
    logging.info("\t " + 56 * "*")
    logging.info("\t " + "Starting Optimization with " + solver + "-Solver")

    # solving the linear problem using the given solver
    if solver == 'gurobi':
        om.solve(solver=solver, cmdline_options={"threads": num_threads})
    else:
        om.solve(solver=solver)
    logging.info("\t Memory Usage during processing: "
                 + str(memory_usage()[0]))
    return om
