import oemof.solph as solph
from oemof.network.network import Bus, Sink, Source
from oemof.solph.custom import Link
from oemof.solph.components import GenericStorage
from dhnx.optimization_oemof_heatpipe import HeatPipeline
import pandas


def check_for_link_storage(nd, nodes_data: pandas.DataFrame) -> str:
    """
        since there are component specific decisions (e.g. capacity)
        especially for storages and links the component type of the
        investigated component (nd) is collected within this method
        
        :param nd: component under investigation
        :type nd: different oemof solph components
        :param nodes_data: Dataframe containing all energy system \
            components data from the input Excel File
        :type nodes_data: pandas.DataFrame
        
        :return: - **return_str** (str) - containing the component type\
            e.g. storage or link
    """
    return_str = ""
    # get the component's row from the input file (nodes_data)
    row = nodes_data.loc[nodes_data["label"] == nd.label]
    # decide rather the investigated component is an undirected link
    # ("link"), a storage (storage) or another component ("")
    if str(row["(un)directed"]) == "undirected" and isinstance(nd, Link):
        return_str = "link"
    if isinstance(nd, GenericStorage):
        return_str = "storage"
    return return_str


def get_sequence(
    flow, component: dict, nd, output_flow: bool, esys: solph.EnergySystem
) -> list:
    """
        method to get the in- and outflow's sequences from the oemof
        produced structures
        
        :param flow: oemof in or output data that essentially represent\
            the properties of the edges of the graph.
        :type flow: oemof.network.Inputs or Outputs
        :param component: energy system node's information
        :type component: dict
        :param nd: component under investigation
        :type nd: different oemof solph components
        :param output_flow: boolean which decides rather the cosindered\
            flows (flow) are output flows
        :type output_flow: bool
        :param esys: oemof energy system variable holding the energy \
            system status before optimization used to reduce the
            dependency of the correctness of user's input
        :type esys: solph.EnergySystem
        
        :return - **return_list**(list) - list containing the found \
            flows sequences
    """
    return_list = []
    flow = list(flow) if len(list(flow)) != 0 else None
    if flow:
        # create the index tuple(s) for the flow sequence to be found in
        # the list of flows
        attr1 = (str(flow[0].label), str(nd.label))
        attr2 = (str(flow[1].label), str(nd.label)) if len(flow) == 2 else ()
        # if the considered flows are output flows revert the tuple
        # structure
        if output_flow:
            attr1 = attr1[::-1]
            attr2 = attr2[::-1]
        # iterate threw the created tuples
        for i in [attr1, attr2]:
            # search the created tuple in the components sequences
            if i != ():
                return_list.append([component["sequences"][(i, "flow")]])
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


def get_flows(nd, results, esys: solph.EnergySystem):
    """
        method to get component's (nd) in- and outflows
        
        :param nd: component under investigation
        :type nd: different oemof solph components
        :param results: oemof result object holding the return of the \
            chosen solver
        :type results: TODO
        :param esys: oemof energy system variable holding the energy \
            system status before optimization used to reduce the
            dependency of the correctness of user's input
        :type esys: solph.EnergySystem
        
        :return: TODO
    """
    result_list = []
    # get component information from the oemof result object based on
    # their label
    component = solph.views.node(results=results, node=str(nd.label))
    # iterate threw in and outputs to get the result's flow sequences
    # result list [0]: inflow 1, [1] inflow 2, [2] outflow 1,
    # [3] outflow 2
    for flow in [nd.inputs, nd.outputs]:
        result_list += get_sequence(
            flow=flow,
            component=component,
            nd=nd,
            output_flow=True if flow == nd.outputs else False,
            esys=esys,
        )
    # return the flow series
    return result_list[0][0], result_list[1][0], result_list[2][0], result_list[3][0]


def get_investment(nd, esys: solph.EnergySystem, results, comp_type: str) -> float:
    """
        method used to obtain the component investment, this is
        calculated differently for storages compared to the other
        components
        
        :param nd: component under investigation
        :type nd: different oemof solph components
        :param esys: oemof energy system variable holding the energy \
            system status before optimization used to reduce the
            dependency of the correctness of user's input
        :type esys: solph.EnergySystem
        :param results: oemof result object holding the return of the \
            chosen solver
        :type results: TODO
        :param comp_type: str holding the component's type
        :type comp_type: str
        
        :return: - float containing the investment value of the \
            considered component (nd)
    """
    # get the component from the energy system's variables
    component_node = esys.groups[str(nd.label)]
    # get the ouput bus which is depending on the component type since
    # the investment of storages is taken on storage content
    if comp_type != "storage":
        bus_node = esys.groups[str(list(nd.outputs)[0].label)]
    else:
        bus_node = None
    # get the specified flows investment variable
    if "invest" in results[component_node, bus_node]["scalars"]:
        return results[component_node, bus_node]["scalars"]["invest"]
    else:
        return 0


def calc_periodical_costs(nd, investment, comp_type, cost_type):
    """
    method to calculate the component's periodical costs for the
    first optimization criterion (cost_type = costs) or the second
    optimization criterion (cost_type = emissions)

    :param nd: component under investigation
    :type nd: TODO
    :param investment: TODO
    :type investment: float
    :param comp_type: TODO
    :type comp_type: str
    :param cost_type: TODO
    :type cost_type: str

    :return: TODO
    """
    ep_costs = 0
    offset = 0
    attributes = {
        "costs": ["ep_costs", "offset"],
        "emissions": ["periodical_constraint_costs", "fix_constraint_costs"],
    }
    # get the comp_type dependent investment variable from the component
    # variable (nd)
    if comp_type == "storage":
        invest_object = nd.investment
    else:
        invest_object = nd.outputs[list(nd.outputs.keys())[0]].investment
    # if an investment was made in the considered component (nd),
    # the costs (periodical and fixed) are calculated
    if investment > 0:
        ep_costs = getattr(invest_object, attributes.get(cost_type)[0])
        offset = getattr(invest_object, attributes.get(cost_type)[1])

    if comp_type == "link":
        return (investment * 2 * ep_costs) + 2 * offset
    else:
        return investment * ep_costs + offset


def calc_variable_costs(nd, comp_dict, attr):
    """
        method to calculate the component's variable costs for the first
        optimization criterion (attr = variable costs) or the second
        optimization criterion (attr = emission factor)
        
        :param nd: component under investigation
        :type nd: TODO
        :param comp_dict: dict holding the energy system component's \
            information as specified in the main method collect_data
        :type comp_dict: dict
        :param attr: str defining the cost factor's name to get the \
            attribute from the component's data
        :type attr: str
        
        :return: TODO
    """
    costs = 0
    type_dict = {
        "inputs": [nd.inputs, comp_dict[0], comp_dict[1]],
        "outputs": [nd.outputs, comp_dict[2], comp_dict[3]],
    }
    for flow_type in type_dict:
        for i in range(0, 1):
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


def get_comp_type(nd) -> str:
    """
    method to declare the component type's short form for the list
    of components (loc)

    :param nd: component under investigation
    :type nd: TODO

    :return: TODO
    """
    type_dict = {
        "<class 'dhnx.optimization_oemof_heatpipe.HeatPipeline'>": "dh",
        "<class 'oemof.solph.network.sink.Sink'>": "sink",
        "<class 'oemof.solph.network.source.Source'>": "source",
        "<class 'oemof.solph.components.generic_storage.GenericStorage'>": "storage",
        "<class 'oemof.solph.custom.link.Link'>": "link",
        "<class 'oemof.solph.network.transformer.Transformer'>": "transformer",
    }
    return type_dict.get(str(type(nd)))


def get_capacities(comp_type: str, comp_dict: dict, results, label: str):
    """
        method to get the components capacity which is component type
        specific
        
        :param comp_type: str holding the component's type
        :type comp_type: str
        :param comp_dict: dict holding the energy system component's \
            information as specified in the main method collect_data
        :type comp_dict: dict
        :param results: oemof result object holding the return of the \
            chosen solver
        :type results: TODO
        :param label: str holding the label which is necessary to \
            determine the storage capacity
        :type label: str
    """
    # if component type ist not storage the capacity is rather the
    # maximum of the first output if there ist one or the maximum of the
    # first input
    if comp_type != "storage":
        comp_dict += [max(comp_dict[0] if sum(comp_dict[2]) == 0 else comp_dict[2])]
    # if the component type is storage the storage content which is part
    # of the oemof results object is used to determine the capacity
    else:
        component = solph.views.node(results, label)
        capacity = component["sequences"][((label, "None"), "storage_content")]
        comp_dict += [capacity]
    return comp_dict


def get_max_invest(comp_type: str, nd):
    """
    get the maximum investment capacity for the specified component
    (nd)

    :param comp_type: str holding the component's type
    :type comp_type: str
    :param nd: component under consideration
    :type nd: different oemof solph components

    :return: TODO
    """
    max_invest = None
    # get the comp_type dependent investment variable from the component
    # variable (nd)
    if comp_type == "storage":
        invest_object = nd.investment
    else:
        invest_object = nd.outputs[list(nd.outputs.keys())[0]].investment
    # check rather there is an opportunity to invest in the component (nd)
    if hasattr(invest_object, "maximum"):
        # if yes return the maximum investment capacity
        max_invest = getattr(invest_object, "maximum")
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
    # get the energy system's pipes
    pipes_esys = pandas.read_csv(result_path + "/pipes.csv", index_col="id")
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


def collect_data(nodes_data, results, esys, result_path):
    """
        main method of the algorithm used to collect the data which is
        necessary to create the results presentation
        
        :param nodes_data: Dataframe containing all energy system \
            components data from the input Excel File
        :type nodes_data: pd.DataFrame
        :param results: oemof result object holding the return of the \
            chosen solver
        :type results: TODO
        :param esys: oemof energy system variable holding the energy \
            system status before optimization used to reduce the
            dependency of the correctness of user's input
        :type esys: solph.EnergySystem
        :param result_path: str holding the algorithms result path used
            for the energy system's pipes data
        :type result_path: str
        
        :return: TODO
    """
    total_demand = 0
    total_usage = 0
    # dictionary containing energy system components data
    # label: [flow input1, flow input2, flow output1, flow output2, capacity,
    # investment, periodical costs, max. investment, variable costs,
    # constraint costs, component type]
    comp_dict = {}
    for nd in esys.nodes:
        if not isinstance(nd, Bus):
            investment = None
            comp_label = str(nd.label)
            if isinstance(nd, HeatPipeline):
                # make heatpipline labels easier to read in the list of
                # components (loc)
                loc_label = change_heatpipelines_label(nd.label, result_path)
            else:
                loc_label = comp_label
            comp_type = check_for_link_storage(nd, nodes_data["links"])
            # get component flows from each component except buses
            comp_dict.update({loc_label: []})
            # get component flows attributes
            comp_input1, comp_input2, comp_output1, comp_output2 = get_flows(
                nd, results, esys
            )
            # append them to the to returned dict comp_dict
            comp_dict[loc_label] += [
                comp_input1,
                comp_input2,
                comp_output1,
                comp_output2,
            ]
            # get the nodes capacity
            comp_dict[loc_label] = get_capacities(
                comp_type, comp_dict[loc_label], results, comp_label
            )
            # investment and periodical costs
            if not (
                isinstance(nd, Source) and "shortage" in nd.label
            ) and not isinstance(nd, Sink):
                # get investment
                investment = get_investment(nd, esys, results, comp_type)
                comp_dict[loc_label].append(investment)
                # get periodical costs
                periodical_costs = calc_periodical_costs(
                    nd, investment, comp_type, "costs"
                )
                comp_dict[loc_label].append(periodical_costs)
                max_invest = get_max_invest(comp_type, nd)
                comp_dict[loc_label].append(max_invest)

            # for uninvestable components set investment and periodical costs
            # to 0 in comp_dict
            else:
                comp_dict[loc_label] += [0, 0, 0]
            if not (
                isinstance(nd, Sink) and nd.label in list(nodes_data["sinks"]["label"])
            ):
                # calculate the variable costs of the first optimization
                # criterion
                variable_costs = calc_variable_costs(
                    nd, comp_dict[loc_label], "variable_costs"
                )
                comp_dict[loc_label].append(variable_costs)
                # calculate the variable costs of the second optimization
                # criterion
                constraint_costs = calc_variable_costs(
                    nd, comp_dict[loc_label], "emission_factor"
                )
                # if there is an investment in the node under investigation
                # calculate the periodical costs of the second optimization
                # criterion
                if investment:
                    constraint_costs += calc_periodical_costs(
                        nd, investment, comp_type, "emissions"
                    )
                # append the costs of the second optimization criterion to the
                # dict to be returned
                comp_dict[loc_label].append(constraint_costs)
            else:
                comp_dict[loc_label] += [0, 0]
                total_demand += sum(comp_input1)
            if isinstance(nd, Source):
                total_usage += sum(comp_output1)
            # get the component's type for the loc
            comp_dict[loc_label].append(get_comp_type(nd))
    return comp_dict, total_demand, total_usage
