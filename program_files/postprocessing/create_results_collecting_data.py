"""
    Christian Klemm - christian.klemm@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
"""
import oemof.solph as solph
from oemof.network.network import Bus, Sink, Source
from oemof.solph.components.experimental import Link
from oemof.solph.components import GenericStorage
from dhnx.optimization.oemof_heatpipe import HeatPipeline
import pandas


def check_for_link_storage(node, nodes_data: pandas.DataFrame) -> str:
    """
        since there are component specific decisions (e.g. capacity)
        especially for storages and links the component type of the
        investigated component (node) is collected within this method
        
        :param node: component under investigation
        :type node: different oemof solph components
        :param nodes_data: Dataframe containing all energy system \
            components data from the input Excel File
        :type nodes_data: pandas.DataFrame
        
        :return: - **return_str** (str) - containing the component \
            type e.g. storage or link
    """
    return_str = ""
    # get the component's row from the input file (nodes_data)
    row = nodes_data.loc[nodes_data["label"] == node.label]
    # decide rather the investigated component is an undirected link
    # ("link"), a storage (storage) or another component ("")
    if str(row["(un)directed"]) == "undirected" and isinstance(node, Link):
        return_str = "link"
    if isinstance(node, GenericStorage):
        return_str = "storage"
    if "pipe-clustered" in node.label:
        return_str = "clustered_dh"
    return return_str


def get_sequence(flow, component: dict, node, output_flow: bool,
                 esys: solph.EnergySystem) -> list:
    """
        method to get the in- and outflow's sequences from the oemof
        produced structures
        
        :param flow: oemof in or output data that essentially represent\
            the properties of the edges of the graph.
        :type flow: oemof.network.Inputs or Outputs
        :param component: energy system node's information
        :type component: dict
        :param node: component under investigation
        :type node: different oemof solph components
        :param output_flow: boolean which decides rather the \
            considered flows (flow) are output flows
        :type output_flow: bool
        :param esys: oemof energy system variable holding the energy \
            system status before optimization used to reduce the
            dependency of the correctness of user's input
        :type esys: solph.EnergySystem
        
        :return: - **return_list** (list) - list containing the found \
            flows sequences
    """
    return_list = []
    flow = list(flow) if len(list(flow)) != 0 else None
    if flow:
        # create the index tuple(s) for the flow sequence to be found in
        # the list of flows
        attr1 = (str(flow[0].label), str(node.label))
        attr2 = (str(flow[1].label), str(node.label)) \
            if len(flow) == 2 else ()
        # if the considered flows are output flows revert the tuple
        # structure
        if output_flow:
            attr1 = attr1[::-1]
            attr2 = attr2[::-1]
        # iterate threw the created tuples
        for label in [attr1, attr2]:
            # search the created tuple in the components sequences
            if label != ():
                return_list.append([component["sequences"][(label, "flow")]])
                return_list[-1][0] = return_list[-1][0].dropna()
            # create an empty sequence (timesteps * 0) if the considered
            # tuple is empty
            else:
                return_list.append([len(esys.timeindex) * [0]])
    # create two empty sequences timesteps * 0 if the flow parameter is
    # empty
    else:
        return_list.append([len(esys.timeindex) * [0]])
        return_list.append([len(esys.timeindex) * [0]])
    # return the found sequences
    return return_list


def get_flows(node, results: dict, esys: solph.EnergySystem) -> list:
    """
        method to get component's (nd) in- and outflows
        
        :param node: component under investigation
        :type node: different oemof solph components
        :param results: oemof result object holding the return of the \
            chosen solver
        :type results: dict
        :param esys: oemof energy system variable holding the energy \
            system status before optimization used to reduce the
            dependency of the correctness of user's input
        :type esys: solph.EnergySystem
        
        :return: - **-** (list) - list of flow series of the \
                    considered component: [0] inflow 1, \
                    [1] inflow 2, [2] outflow 1, [3] outflow 2
    """
    result_list = []
    # get component information from the oemof result object based on
    # their label
    component = solph.views.node(results=results, node=str(node.label))
    # iterate threw in and outputs to get the result's flow sequences
    # result list [0]: inflow 1, [1] inflow 2, [2] outflow 1,
    # [3] outflow 2
    for flow in [node.inputs, node.outputs]:
        result_list += get_sequence(
            flow=flow,
            component=component,
            node=node,
            output_flow=True if flow == node.outputs else False,
            esys=esys,
        )
    # return the flow series
    # [input flow 1, input flow 2, output flow 1, output flow 2]
    return [result_list[0][0], result_list[1][0],
            result_list[2][0], result_list[3][0]]


def get_investment(node, esys: solph.EnergySystem, results: dict,
                   comp_type: str) -> float:
    """
        method used to obtain the component's investment, this is
        calculated differently for storages compared to the other
        components
        
        :param node: component under investigation
        :type node: different oemof solph components
        :param esys: oemof energy system variable holding the energy \
            system status before optimization used to reduce the
            dependency of the correctness of user's input
        :type esys: solph.EnergySystem
        :param results: oemof result object holding the return of the \
            chosen solver
        :type results: dict
        :param comp_type: str holding the component's type
        :type comp_type: str
        
        :return: - **-** (float) - float containing the investment \
            value of the considered component (node)
    """
    # get the component from the energy system's variables
    component_node = esys.groups[str(node.label)]
    # get the output bus which is depending on the component type since
    # the investment of storages is taken on storage content
    if comp_type != "storage" and comp_type != "clustered_dh":
        bus_node = esys.groups[str(list(node.outputs)[0].label)]
    elif comp_type == "clustered_dh":
        bus_node = esys.groups[str(list(node.inputs)[0].label)]
    else:
        bus_node = None
    # get the specified flows investment variable
    if not comp_type == "clustered_dh" \
            and "invest" in results[component_node, bus_node]["scalars"]:
        return results[component_node, bus_node]["scalars"]["invest"] \
            if results[component_node, bus_node]["scalars"]["invest"] \
            > 0.000001 else 0
    elif comp_type == "clustered_dh" \
            and "invest" in results[bus_node, component_node]["scalars"]:
        return results[bus_node, component_node]["scalars"]["invest"] \
            if results[bus_node, component_node]["scalars"]["invest"] \
            > 0.000001 else 0
    else:
        return 0


def calc_periodical_costs(node, investment: float, comp_type: str,
                          cost_type: str) -> float:
    """
        method to calculate the component's periodical costs for the
        first optimization criterion (cost_type = costs) or the second
        optimization criterion (cost_type = emissions)
    
        :param node: component under investigation
        :type node: different oemof solph components
        :param investment: float containing the investment value of \
            the considered component (node)
        :type investment: float
        :param comp_type: str holding the component's type
        :type comp_type: str
        :param cost_type: str that makes the distinction between a \
            monetary or emissions calculation
        :type cost_type: str
    
        :return: - **-** (float) - float holding the calculated \
                    periodical costs or emissions
    """
    ep_costs = 0
    offset = 0
    attributes = {
        "costs": ["ep_costs", "offset"],
        "emissions": ["periodical_constraint_costs", "fix_constraint_costs"],
    }
    # get the comp_type dependent investment variable from the component
    # variable (node)
    if comp_type == "storage":
        invest_object = node.investment
    elif comp_type == "clustered_dh":
        invest_object = node.inputs[list(node.inputs.keys())[0]].investment
    else:
        invest_object = node.outputs[list(node.outputs.keys())[0]].investment
    # if an investment was made in the considered component (nd),
    # the costs (periodical and fixed) are calculated
    if investment > 0:
        ep_costs = getattr(invest_object, attributes.get(cost_type)[0])
        offset = getattr(invest_object, attributes.get(cost_type)[1])

    if comp_type == "link":
        return (investment * 2 * ep_costs) + 2 * offset
    else:
        return investment * ep_costs + offset


def calc_variable_costs(node, comp_dict: list, attr: str) -> float:
    """
        method to calculate the component's variable costs for the
        first optimization criterion (attr = variable costs) or the
        second optimization criterion (attr = emission factor)
        
        :param node: component under investigation
        :type node: different oemof solph components
        :param comp_dict: list holding the energy system component's \
            information as specified in the main method collect_data
        :type comp_dict: list
        :param attr: str defining the cost factor's name to get the \
            attribute from the component's data
        :type attr: str
        
        :return: - **costs** (float) - float holding the calculated \
                    variable costs or emissions
    """
    costs = 0
    type_dict = {
        "inputs": [node.inputs, comp_dict[0], comp_dict[1]],
        "outputs": [node.outputs, comp_dict[2], comp_dict[3]],
    }
    for flow_type in type_dict:
        for i in range(0, 2):
            # if the sum of the flow stored in comp_dict 0 to 3 is more
            # than 0 the sum is multiplied with the for this input/output
            # defined costs factor which is searched by the method getattr
            if sum(type_dict[flow_type][i + 1]) > 0:
                costs += sum(
                    type_dict[flow_type][i + 1]
                    * getattr(
                        type_dict[flow_type][0][
                            list(type_dict[flow_type][0].keys())[i]
                        ],
                        attr,
                    )
                )

    return costs


def get_comp_type(node) -> str:
    """
        method to declare the component type's short form for the list
        of components (loc)
    
        :param node: component under investigation
        :type node: different oemof solph components
    
        :return: **-** (str) - str holding the component's type which \
                    will be listed in the list of components (loc)
    """
    type_dict = {
        "<class 'dhnx.optimization_oemof_heatpipe.HeatPipeline'>": "dh",
        "<class 'dhnx.optimization.oemof_heatpipe.HeatPipeline'>": "dh",
        "<class 'oemof.solph.components._sink.Sink'>": "sink",
        "<class 'oemof.solph.components._source.Source'>": "source",
        "<class 'oemof.solph.components._generic_storage.GenericStorage'>":
            "storage",
        "<class 'oemof.solph.components.experimental._link.Link'>": "link",
        "<class 'oemof.solph.components._transformer.Transformer'>":
            "transformer",
    }
    return type_dict.get(str(type(node)))


def get_capacities(comp_type: str, comp_dict: list, results: dict,
                   label: str) -> list:
    """
        method to get the components capacity which is component type
        specific
        
        :param comp_type: str holding the component's type
        :type comp_type: str
        :param comp_dict: list holding the energy system component's \
            information as specified in the main method collect_data
        :type comp_dict: list
        :param results: oemof result object holding the return of the \
            chosen solver
        :type results: dict
        :param label: str holding the label which is necessary to \
            determine the storage capacity
        :type label: str
        
        :return: - **comp_dict** (list) - returns the component's \
                    parameter list after the capacity has been added
    """
    # if component type ist not storage the capacity is rather the
    # maximum of the first output if there ist one or the maximum of the
    # first input
    if comp_type != "storage":
        comp_dict += [max(comp_dict[0] if sum(comp_dict[2]) == 0
                          else comp_dict[2])]
    # if the component type is storage the storage content which is part
    # of the oemof results object is used to determine the capacity
    else:
        component = solph.views.node(results, label)
        capacity = component["sequences"][((label, "None"), "storage_content")]
        comp_dict += [capacity]
    return comp_dict


def get_max_invest(comp_type: str, node) -> float:
    """
        get the maximum investment capacity for the specified component
        (nd)
    
        :param comp_type: str holding the component's type
        :type comp_type: str
        :param node: component under consideration
        :type node: different oemof solph components
    
        :return: - **max_invest** (float) - float holding the maximum \
                    possible investment
    """
    max_invest = None
    # get the comp_type dependent investment variable from the component
    # variable (nd)
    if comp_type == "storage":
        invest_object = node.investment
    else:
        invest_object = node.outputs[list(node.outputs.keys())[0]].investment
    # check rather there is an opportunity to invest in the component (node)
    if hasattr(invest_object, "maximum"):
        # if yes return the maximum investment capacity
        max_invest = round(getattr(invest_object, "maximum"), 2)
    return max_invest


def change_heatpipelines_label(comp_label: str, result_path: str) -> str:
    """
        method used to make the heatpipeline labels easier to read
        
        :param comp_label: energy system intern label for the specific \
            heatpipeline part
        :type comp_label: str
        :param result_path: str holding the algorithms result path used
            for the energy system's pipes data
        :type result_path: str
        
        :return: - **loc_label** (str) - string containig the easy \
            readable label for the list of components (loc)
    """
    if "exergy" in comp_label:
        # get the energy system's pipes
        pipes_esys = pandas.read_csv(result_path
                                     + "/pipes_exergy.csv", index_col="id")
    else:
        # get the energy system's pipes
        pipes_esys = pandas.read_csv(result_path
                                     + "/pipes_anergy.csv", index_col="id")
        
    # cut the "infrastructure_ from the pipes label
    loc_label = str(comp_label)[20:]
    # get the heatpipes nodes
    pipe_nodes = loc_label.split("_")[1].split("-")
    # search for the specified pipe in the list of pipes
    pipe = pipes_esys.loc[
        (
            (pipes_esys["from_node"] == pipe_nodes[0] + "-" + pipe_nodes[1])
            & (pipes_esys["to_node"] == pipe_nodes[2] + "-" + pipe_nodes[3])
        )
        | (
            (pipes_esys["to_node"] == pipe_nodes[0] + "-" + pipe_nodes[1])
            & (pipes_esys["from_node"] == pipe_nodes[2] + "-" + pipe_nodes[3])
        )
    ]
    # build the new label for the heatpipe part
    street = str(pipe["street"].values[0])
    loc_label = street + "_" + loc_label
    # replace forks, producers and consumers by their first letters to
    # shorten the labels.
    loc_label = loc_label.replace("forks-", "f")
    loc_label = loc_label.replace("producers-", "p")
    loc_label = loc_label.replace("consumers-", "c")
    # return the new formed label
    return loc_label


def collect_data(nodes_data: dict, results: dict, esys: solph.EnergySystem,
                 result_path: str) -> (dict, float, float):
    """
        main method of the algorithm used to collect the data which is
        necessary to create the results presentation
        
        :param nodes_data: dictionary containing all energy system \
            components data from the input Excel File
        :type nodes_data: dict
        :param results: oemof result object holding the return of the \
            chosen solver
        :type results: dict
        :param esys: oemof energy system variable holding the energy \
            system status before optimization used to reduce the
            dependency of the correctness of user's input
        :type esys: solph.EnergySystem
        :param result_path: str holding the algorithms result path used
            for the energy system's pipes data
        :type result_path: str
        
        :return: - **comp_dict** (dict) - dictionary containing the \
                    result parameters of all of the energy system's \
                    components
                 - **total_demand** (float) - float holding the energy \
                    system's final energy demand
                 - **total_usage** (float) - float holding the energy \
                    system's secondary energy demand
    """
    total_demand = 0
    total_usage = 0
    # dictionary containing energy system components data
    # label: [flow input1, flow input2, flow output1, flow output2,
    # capacity, investment, periodical costs, max. investment, variable
    # costs, constraint costs, component type, uuid]
    comp_dict = {}
    for node in esys.nodes:
        if not isinstance(node, Bus):
            investment = None
            comp_label = str(node.label)
            if isinstance(node, HeatPipeline):
                # make heat pipeline labels easier to read in the list of
                # components (loc)
                loc_label = change_heatpipelines_label(comp_label=node.label,
                                                       result_path=result_path)
            else:
                loc_label = comp_label
            comp_type = check_for_link_storage(node=node,
                                               nodes_data=nodes_data["links"])
            # get component flows from each component except buses
            comp_dict.update({loc_label: []})
            # get component flows attributes
            flows = get_flows(node=node, results=results, esys=esys)
            # append them to the to returned dict comp_dict
            comp_dict[loc_label] += flows
            # get the nodes capacity
            comp_dict[loc_label] = get_capacities(
                comp_type=comp_type, comp_dict=comp_dict[loc_label],
                results=results, label=comp_label
            )
            # investment and periodical costs
            if not (
                isinstance(node, Source) and "shortage" in node.label
            ) and not isinstance(node, Sink):
                # get investment
                investment = get_investment(
                    node=node, esys=esys, results=results, comp_type=comp_type)
                comp_dict[loc_label].append(investment)
                # get periodical costs
                periodical_costs = calc_periodical_costs(
                    node=node, investment=investment, comp_type=comp_type,
                    cost_type="costs"
                )
                comp_dict[loc_label].append(periodical_costs)
                max_invest = get_max_invest(comp_type=comp_type, node=node)
                comp_dict[loc_label].append(max_invest)

            # for un-investable components set investment and
            # periodical costs to 0 in comp_dict
            else:
                comp_dict[loc_label] += [0, 0, 0]
            if not (
                isinstance(node, Sink)
                and node.label in list(nodes_data["sinks"]["label"])
            ):
                # calculate the variable costs of the first optimization
                # criterion
                variable_costs = calc_variable_costs(
                    node=node, comp_dict=comp_dict[loc_label],
                    attr="variable_costs"
                )
                comp_dict[loc_label].append(variable_costs)
                # calculate the variable costs of the second optimization
                # criterion
                constraint_costs = calc_variable_costs(
                    node=node, comp_dict=comp_dict[loc_label],
                    attr="emission_factor"
                )
                # if there is an investment in the node under investigation
                # calculate the periodical costs of the second optimization
                # criterion
                if investment:
                    constraint_costs += calc_periodical_costs(
                        node=node, investment=investment, comp_type=comp_type,
                        cost_type="emissions"
                    )
                # append the costs of the second optimization criterion to the
                # dict to be returned
                comp_dict[loc_label].append(constraint_costs)
            else:
                comp_dict[loc_label] += [0, 0]
                total_demand += sum(flows[0])
            if isinstance(node, Source):
                total_usage += sum(flows[2])
            # get the component's type for the loc
            comp_dict[loc_label].append(get_comp_type(node=node))
            
    return comp_dict, total_demand, total_usage
