import logging


def get_first_node_flow(flow) -> str:
    """
        returns begin of the flow, used to log where the flow comes
        from

        :param flow:
        :type flow:

        :return: - **flow_name[0]** (str) - label of beginning \
            node of the considered flow
    """
    flow_name = str(flow.name)
    flow_name = flow_name[2:-10]
    flow_name = flow_name.split(",")
    return flow_name[0]


def get_last_node_flow(flow):
    """
        returns end of the flow, used to log where the flow goes to

        :param flow:
        :type flow:

        :return: - **flow_name[1]** (str) - label of the end node \
            of the considered flow
    """
    flow_name = str(flow.name)
    flow_name = flow_name[2:-10]
    flow_name = flow_name.split(",")
    return flow_name[1]


def console_logging(
        comp_dict,
        transformer_type=None,
):
    """
        consists of the different console logging entries and logs
        the one for the given component


        :param transformer_type:
        :type transformer_type:
    """

    # dictionary containing energy system components data
    # label: [flow input1, flow input2, flow output1, flow output2, capacity,
    # investment, periodical costs, max. investment, variable costs,
    # constraint costs, component type]
    
    for comp in comp_dict:
        inflow1 = comp_dict[comp][0]
        inflow1_label = comp_dict[comp][11]
        print(inflow1_label)
        inflow2 = comp_dict[comp][1]
        outflow1 = comp_dict[comp][2]
        outflow2 = comp_dict[comp][3]
    
        if comp_dict[comp][10] == "sink":
            logging.info(
                "\t" + "Total Energy Demand: " + str(inflow1.sum()) + " kWh")
        else:
            logging.info(
                    "   "
                    + "Total Energy Input from"
                    + get_last_node_flow(inflow1_label)
                    + ": "
                    + str(round(outflow1.sum(), 2))
                    + " kWh"
            )
            logging.info(
                    "   "
                    + "Total Energy Input from"
                    + get_last_node_flow(inflow2)
                    + ": "
                    + str(round(outflow1.sum(), 2))
                    + " kWh"
            )
            logging.info(
                    "   "
                    + "Total Energy Output to"
                    + get_last_node_flow(outflow1)
                    + ": "
                    + str(round(outflow1.sum(), 2))
                    + " kWh"
            )
            logging.info(
                    "   "
                    + "Total Energy Output to"
                    + get_last_node_flow(outflow2)
                    + ": "
                    + str(round(outflow1.sum(), 2))
                    + " kWh"
            )
            logging.info("\t" + "Max. Capacity: " + str(comp_dict[comp][4])
                         + " kW")
            
            #if comp_dict[comp][4] is not None:
            logging.info("\t" + "Investment Capacity: "
                         + str(round(comp_dict[comp][5], 2)) + " kW")
            #if periodical_costs is not None:
            logging.info("\t" + "Periodical costs: "
                         + str(round(comp_dict[comp][6], 2))
                         + " cost units p.a.")
            logging.info("\t" + "Variable Costs: "
                         + str(round(comp_dict[comp][8], 2)) + " cost units")
        
def insert_line_end_of_component():
    logging.info("\t" + 56 * "-")
    
    
def logging_model_summary(meta_results_objective, total_constraint_costs,
                          total_variable_costs, total_periodical_costs,
                          total_demand, total_usage):
    logging.info("\t " + 56 * "#")
    logging.info("\t " + "SUMMARY")
    logging.info("\t " + "Total System Costs:             "
                 + str(round(meta_results_objective, 1))
                 + " cost units")
    logging.info("\t " + "Total Constraint Costs:         "
                 + str(round(total_constraint_costs))
                 + " cost units")
    logging.info("\t " + "Total Variable Costs:           "
                 + str(round(total_variable_costs))
                 + " cost units")
    logging.info("\t " + "Total Periodical Costs (p.a.):  "
                 + str(round(total_periodical_costs))
                 + " cost units p.a.")
    logging.info("\t " + "Total Energy Demand:            "
                 + str(round(total_demand)) + " kWh")
    logging.info("\t " + "Total Energy Usage:             "
                 + str(round(total_usage)) + " kWh")
    # creating the list of investments to be made
    logging.info("\t " + 56 * "-")


def logging_investments(investments_to_be_made: dict):
    logging.info("\t " + "Investments to be made:")
    investment_objects = list(investments_to_be_made.keys())
    for num in range(len(investment_objects)):
        logging.info(
                "   - "
                + investment_objects[num]
                + ": "
                + investments_to_be_made[investment_objects[num]]
        )
    logging.info("\t " + 56 * "*" + "\n")
