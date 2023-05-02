import pandas

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
    if str(type(comp_dict[4])) not in ["<class 'float'>", "<class 'int'>"]:
        capacity = max(comp_dict[4])
    else:
        capacity = comp_dict[4]
    df_list_of_components = pandas.concat(
        [
            df_list_of_components,
            pandas.DataFrame(
                [
                    [
                        label,
                        comp_dict[10],
                        round(sum(comp_dict[0]), 2),
                        round(sum(comp_dict[1]), 2),
                        round(sum(comp_dict[2]), 2),
                        round(sum(comp_dict[3]), 2),
                        round(capacity, 2),
                        round(comp_dict[8], 2),
                        round(comp_dict[6], 2),
                        round(comp_dict[5], 2),
                        maxinvest,
                        round(comp_dict[9], 2),
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
    flow_type_dict = {
        0: "_input1",
        1: "_input2",
        2: "_output1",
        3: "_output2",
        4: "_capacity",
    }
    dict_of_columns = {}
    for flow in flow_type_dict:
        if str(type(comp_dict[flow])) not in ["<class 'float'>", "<class 'int'>"]:
            if sum(comp_dict[flow]) != 0:
                dict_of_columns[label + flow_type_dict[flow]] = comp_dict[flow]
    df_result_table = pandas.concat([df_result_table,
                                     pandas.DataFrame(dict_of_columns)],
                                    axis=1)
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
            maxinvest=comp_dict[label][7],
        )
        total_periodical_costs += comp_dict[label][6]
        total_variable_costs += comp_dict[label][8]
        total_constraint_costs += comp_dict[label][9]

    return (
        df_list_of_components,
        total_periodical_costs,
        total_variable_costs,
        total_constraint_costs,
        df_result_table,
    )


def prepare_data(comp_dict, total_demand, nd, result_path, df_result_table):
    df_list_of_components = pandas.DataFrame(columns=copt)
    for label in comp_dict.copy():
        if "insulation" in label:
            total_demand -= sum(comp_dict[label][2])
            comp_dict[label][-1] = "insulation"
        elif "high_temp" in label or "low_temp" in label:
            comp_dict.pop(label)
        elif "collector" in label and label[:-10] in list(nd["sources"]["label"]):
            for i in range(0, 3):
                comp_dict[label[:-10]][i] = comp_dict[label][i]
            comp_dict[label[:-10]][8] = comp_dict[label][8]
            comp_dict[label[:-10]][9] += comp_dict[label][9]
            comp_dict.pop(label)
        elif comp_dict[label][8] == "dh": # TODO hier stimmt was nicht
            pipe_data = pandas.read_csv(result_path + "/pipes.csv")
            comp_dict[get_dh_label(label, pipe_data)] = comp_dict.pop(label)
    (
        df_list_of_components,
        total_periodical_costs,
        total_variable_costs,
        total_constraint_costs,
        df_result_table,
    ) = prepare_loc(comp_dict, df_result_table, df_list_of_components)
    return (
        df_list_of_components,
        total_periodical_costs,
        total_variable_costs,
        total_constraint_costs,
        df_result_table,
        total_demand,
    )
