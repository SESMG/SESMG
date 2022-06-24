import oemof.solph as solph
from oemof.network.network import Bus, Sink, Source, Transformer
from oemof.solph.custom import Link
from oemof.solph.components import GenericStorage


def check_for_link_storage(nd, nodes_data):
    undirected_link = \
        True if isinstance(nd, Link) and str(nodes_data["links"].loc[
            nodes_data["links"]["label"] == nd.label]
            ["(un)directed"]) == "undirected" else False
    storage = True if isinstance(nd, GenericStorage) else False
    if undirected_link:
        return "link"
    elif storage:
        return "storage"
    else:
        return ""


def get_sequence(flow, component, nd, output_flow, esys):
    return_list = []
    flow = list(flow) if len(list(flow)) != 0 else None
    if flow:
        attr1 = (str(flow[0].label), str(nd.label))
        attr2 = (str(flow[1].label), str(nd.label)) if len(flow) == 2 else ()
        if output_flow:
            attr1 = attr1[::-1]
            attr2 = attr2[::-1]
        for i in [attr1, attr2]:
            if i != ():
                return_list.append([component['sequences'][(i, "flow")]])
            else:
                return_list.append([len(esys.timeindex) * [0]])
    else:
        return_list.append([len(esys.timeindex) * [0]])
        return_list.append([len(esys.timeindex) * [0]])
    return return_list
    
    
def get_flows(nd, results, esys):
    result_list = []
    component = solph.views.node(results, str(nd.label))
    for flow in [nd.inputs, nd.outputs]:
        result_list += get_sequence(flow, component, nd,
                                    True if flow == nd.outputs else False,
                                    esys)
    return result_list[0][0], result_list[1][0], result_list[2][0], \
        result_list[3][0]


def get_investment(nd, esys, results, comp_type):
    """

    """
    component_node = esys.groups[str(nd.label)]
    if comp_type != "storage":
        bus_node = esys.groups[str(list(nd.outputs)[0].label)]
    else:
        bus_node = None
    if "invest" in results[component_node, bus_node]['scalars']:
        return results[component_node, bus_node]['scalars']['invest']
    else:
        return 0


def calc_periodical_costs(nd, investment, comp_type, cost_type):
    """

    """
    ep_costs = 0
    offset = 0
    attributes = {
        "costs": ["ep_costs", "offset"],
        "emissions": ["periodical_constraint_costs", "fix_constraint_costs"]}
    if comp_type == "storage":
        invest_object = nd.investment
    else:
        invest_object = nd.outputs[list(nd.outputs.keys())[0]].investment
    if investment > 0:
        ep_costs = getattr(invest_object, attributes.get(cost_type)[0])
        offset = getattr(invest_object, attributes.get(cost_type)[1])
    
    if comp_type == "link":
        return (investment * 2 * ep_costs) + 2 * offset
    else:
        return investment * ep_costs + offset


def calc_variable_costs(nd, comp_dict, attr):
    costs = 0
    type_dict = {
        "inputs": [nd.inputs, comp_dict[0], comp_dict[1]],
        "outputs": [nd.outputs, comp_dict[2], comp_dict[3]]}
    for flow_type in type_dict:
        for i in range(0, 1):
            if sum(type_dict[flow_type][i + 1]) > 0:
                costs += \
                    sum(type_dict[flow_type][i + 1]
                        * getattr(type_dict[flow_type][0]
                                  [list(type_dict[flow_type][0].keys())[i]],
                                  attr))
    
    return costs


def get_comp_type(nd, comp_dict):
    type_dict = {
        "<class 'dhnx.optimization_oemof_heatpipe.HeatPipeline'>": "dh",
        "<class 'oemof.solph.network.sink.Sink'>": "sink",
        "<class 'oemof.solph.network.source.Source'>": "source",
        "<class 'oemof.solph.components.generic_storage.GenericStorage'>":
            "storage",
        "<class 'oemof.solph.custom.link.Link'>": "link",
        "<class 'oemof.solph.network.transformer.Transformer'>": "transformer"}

    comp_dict[str(nd.label)].append(type_dict.get(str(type(nd))))


def collect_data(nodes_data, results, esys):
    total_demand = 0
    # dictionary containing energy system components data
    # label: [flow input1, flow input2, flow output1, flow output2,
    # investment, periodical costs, variable costs, constraint costs]
    comp_dict = {}
    for nd in esys.nodes:
        investment = None
        label = str(nd.label)
        comp_type = check_for_link_storage(nd, nodes_data)
        # get component flows from each component except buses
        if not isinstance(nd, Bus):
            comp_dict.update({label: []})
            comp_input1, comp_input2, comp_output1, comp_output2 = get_flows(
                    nd,
                    results,
                    esys)
            comp_dict[label] += [comp_input1,
                                 comp_input2,
                                 comp_output1,
                                 comp_output2]
        if not (isinstance(nd, Source) and "shortage" in nd.label) \
                and not isinstance(nd, Sink) and not isinstance(nd, Bus):
            # get investment
            investment = get_investment(nd, esys, results, comp_type)
            comp_dict[label].append(investment)
            # get periodical costs
            periodical_costs = calc_periodical_costs(
                    nd, investment, comp_type, "costs")
            comp_dict[label].append(periodical_costs)
        elif not isinstance(nd, Bus):
            comp_dict[label] += [0, 0]
        if not (isinstance(nd, Sink)
                and nd.label in list(nodes_data["sinks"]["label"])) \
                and not isinstance(nd, Bus):
            variable_costs = calc_variable_costs(nd, comp_dict[label],
                                                 "variable_costs")
            comp_dict[label].append(variable_costs)
            
            constraint_costs = \
                calc_variable_costs(nd, comp_dict[label], "emission_factor")
            if investment:
                constraint_costs += calc_periodical_costs(
                        nd, investment, comp_type, "emissions")
            comp_dict[label].append(constraint_costs)
        elif not isinstance(nd, Bus):
            comp_dict[label] += [0, 0]
            total_demand += sum(comp_input1)
        if not isinstance(nd, Bus):
            get_comp_type(nd, comp_dict)
    return comp_dict, total_demand