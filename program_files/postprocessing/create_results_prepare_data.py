import pandas as pd

# columns_of_plotly_table
copt = [
    "ID",
    "type",
    "input 1/kWh",
    "input 2/kWh",
    "output 1/kWh",
    "output 2/kWh",
    "capacity/kW",
    "variable costs/CU",
    "periodical costs/CU",
    "investment/kW",
    "max. invest./kW",
    "constraints/CU",
]


def add_component_to_loc(label, comp_dict, df_list_of_components, maxinvest="---"):
    """
    adds the given component with its parameters to
    list of components (loc)
    """

    df_list_of_components = pd.concat(
        [
            df_list_of_components,
            pd.DataFrame(
                [
                    [
                        label,
                        comp_dict[8],
                        round(sum(comp_dict[0]), 1),
                        round(sum(comp_dict[1]), 1),
                        round(sum(comp_dict[2]), 1),
                        round(sum(comp_dict[3]), 1),
                        round(
                            max(
                                comp_dict[0] if sum(comp_dict[2]) == 0 else comp_dict[2]
                            ),
                            1,
                        ),
                        round(comp_dict[6], 1),
                        round(comp_dict[5], 1),
                        round(comp_dict[4], 1),
                        maxinvest,
                        round(comp_dict[7], 1),
                    ]
                ],
                columns=copt,
            ),
        ]
    )
    return df_list_of_components


def get_dh_label(label, param):
    label_parts = str(label).split("-")
    diameter = str(label).split("_")[2]
    if "consumers" in str(label_parts):
        pipe = param.loc[param["to_node"] == "consumers-" + label_parts[-1]]
        name = (
            str(pipe["street"].values[0])
            + "_"
            + str(diameter)
            + "_f"
            + str(label_parts[-3])
            + "_to_c"
            + str(label_parts[-1])
        )
    elif "producers" in str(label_parts):
        pipe = param.loc[param["from_node"] == "producers-" + label_parts[-3]]
        name = (
            "producer"
            + str(pipe["street"].values[0])
            + "_"
            + str(diameter)
            + "_p"
            + str(label_parts[-3])
            + "_to_f"
            + str(label_parts[-1])
        )
    else:
        name = ""
        pipe_dict = {"_": [-1, -3], "_revers_": [-3, -1]}
        for i in pipe_dict:
            pipe = param.loc[
                (param["to_node"] == "forks-" + label_parts[pipe_dict[i][0]])
                & (param["from_node"] == "forks-" + label_parts[pipe_dict[i][1]])
            ]
            if not pipe.empty:
                name = (
                    str(pipe["street"].values[0])
                    + i
                    + str(diameter)
                    + "_f"
                    + str(label_parts[-3])
                    + "_to_f"
                    + str(label_parts[-1])
                )

    return str(name)


def append_flows(label, comp_dict, df_result_table):
    flow_type_dict = {0: "_input1", 1: "_input2", 2: "_output1", 3: "_output2"}
    for flow in flow_type_dict:
        if sum(comp_dict[flow]) != 0:
            df_result_table.loc[:, label + flow_type_dict[flow]] = comp_dict[flow]
    return df_result_table


def prepare_loc(comp_dict, df_result_table, df_list_of_components):
    total_periodical_costs = 0
    total_variable_costs = 0
    total_constraint_costs = 0
    for label in comp_dict:
        df_result_table = append_flows(str(label), comp_dict[label], df_result_table)
        df_list_of_components = add_component_to_loc(
            label=label,
            comp_dict=comp_dict[label],
            df_list_of_components=df_list_of_components,
            maxinvest="---",
        )
        total_periodical_costs += comp_dict[label][5]
        total_variable_costs += comp_dict[label][6]
        total_constraint_costs += comp_dict[label][7]

    return (
        df_list_of_components,
        total_periodical_costs,
        total_variable_costs,
        total_constraint_costs,
        df_result_table,
    )


def prepare_data(comp_dict, total_demand, nd, result_path, df_result_table):
    df_list_of_components = pd.DataFrame(columns=copt)
    pipe_data = pd.read_csv(result_path + "/pipes.csv")
    for label in comp_dict.copy():
        if "insulation" in label:
            sink = str(
                nd["insulation"]
                .loc[nd["insulation"]["label"] == label[11:]]["sink"]
                .values[0]
            )
            comp_dict[str(sink)][0] -= comp_dict[label][2]
            total_demand -= sum(comp_dict[label][2])
            comp_dict.pop(label)
        elif "high_temp" in label or "low_temp" in label:
            comp_dict.pop(label)
        elif "collector" in label and label[:-10] in list(nd["sources"]["label"]):
            for i in range(0, 3):
                comp_dict[label[:-10]][i] = comp_dict[label][i]
            comp_dict.pop(label)
        elif comp_dict[label][8] == "dh":
            comp_dict[get_dh_label(label, pipe_data)] = comp_dict.pop(label)

    return prepare_loc(comp_dict, df_result_table, df_list_of_components), total_demand
