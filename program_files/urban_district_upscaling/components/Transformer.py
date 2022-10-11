transf_dict = {
    "building_gchp_transformer": ["gchp", "hp_elec", "heat", "None"],
    "building_ashp_transformer": ["ashp", "hp_elec", "heat", "None"],
    "building_gasheating_transformer": ["gasheating", "gas", "heat", "None"],
    "building_oilheating_transformer": ["oilheating", "oil", "heat", "None"],
    "building_electricheating_transformer": [
        "electricheating",
        "electricity",
        "heat",
        "None",
    ],
}


def create_transformer(
    building_id: str,
    transf_type,
    sheets,
    standard_parameters,
    building_type=None,
    area="0",
    label="None",
    specific="None",
    output="None",
):
    from program_files import create_standard_parameter_comp
    from program_files import Bus

    transf_dict.update(
        {
            "central_"
            + specific
            + "_chp": [label + "_chp", label, label + "_elec", output],
            "central_"
            + specific
            + "_heating_plant_transformer": [
                label + "_heating_plant",
                label,
                output,
                "None",
            ],
            "central_"
            + specific
            + "_transformer": [label + "_heatpump", "heatpump_elec", output, "None"],
            # TODO
            "central_biomass_transformer": ["biomass", "biomass", output, "None"],
            "central_electrolysis_transformer": [
                label + "_electrolysis",
                "electricity",
                "h2",
                "None",
            ],
            "central_methanization_transformer": [
                label + "_methanization",
                "h2",
                "naturalgas",
                "None",
            ],
            "central_fuelcell_transformer": [
                label + "_fuelcell",
                "h2",
                "electricity",
                output,
            ],
        }
    )

    if building_type is not None:
        if building_type == "RES":
            bus = "building_res_gas_bus"
            oil_bus = "building_res_oil_bus"
        elif building_type == "IND":
            bus = "building_ind_gas_bus"
            oil_bus = "building_ind_oil_bus"
        else:
            bus = "building_com_gas_bus"
            oil_bus = "building_com_oil_bus"
            # building gas bus
        sheets = Bus.create_standard_parameter_bus(
            label=str(building_id) + "_gas_bus", bus_type=bus, sheets=sheets,
            standard_parameters=standard_parameters
        )
        sheets = Bus.create_standard_parameter_bus(
                label=str(building_id) + "_oil_bus", bus_type=oil_bus,
                sheets=sheets,
                standard_parameters=standard_parameters
        )

    if not transf_dict.get(transf_type)[2] == output:
        output1 = str(building_id) + "_" + transf_dict.get(transf_type)[2] + "_bus"
    else:
        output1 = output

    return create_standard_parameter_comp(
        specific_param={
            "label": building_id
            + "_"
            + transf_dict.get(transf_type)[0]
            + "_transformer",
            "comment": "automatically_created",
            "input": building_id + "_" + transf_dict.get(transf_type)[1] + "_bus",
            "output": output1,
            "output2": transf_dict.get(transf_type)[3],
            "area": float(area),
        },
        standard_parameter_info=[transf_type, "4_transformers", "comment"],
        sheets=sheets,
        standard_parameters=standard_parameters
    )


def building_transformer(building, p2g_link, true_bools, sheets,
                         standard_parameters):
    """
    TODO
    :param building:
    :type building:
    :param p2g_link:
    :type p2g_link:
    :param true_bools:
    :type true_bools: list
    :param sheets:
    :type sheets:
    """
    from program_files import Link

    build_transf_dict = {
        "ashp": [None, "building_ashp_transformer"],
        "gas heating": [building["building type"], "building_gasheating_transformer"],
        "electric heating": [None, "building_electricheating_transformer"],
        "oil heating": [building["building type"], "building_oilheating_transformer"]
    }
    for transf in build_transf_dict:
        # creates air source heat-pumps
        if building[transf] in true_bools:
            sheets = create_transformer(
                building_id=building["label"],
                building_type=build_transf_dict[transf][0],
                transf_type=build_transf_dict[transf][1],
                sheets=sheets,
                standard_parameters=standard_parameters
            )
            if transf == "gas heating" and p2g_link:
                sheets = Link.create_link(
                    label="central_naturalgas_" + building["label"] + "link",
                    bus_1="central_naturalgas_bus",
                    bus_2=building["label"] + "_gas_bus",
                    link_type="central_naturalgas_building_link",
                    sheets=sheets,
                    standard_parameters=standard_parameters
                )
    return sheets


def cluster_transf_information(transformer, transf_param, transf_type, sheets):
    """
        Collects the transformer information of the selected type, and
        inserts it into the dict containing the cluster specific
        transformer data.

        :param transformer: Dataframe containing the transformer under \
            investigation
        :type transformer: pd.DataFrame
        :param transf_param: dictionary containing the cluster summed \
            transformer information
        :type transf_param: dict
        :param transf_type: transformer type needed to define the dict entry \
            to be modified
        :type transf_type: str

        :return:
    """
    param_dict = {
        0: 1,
        1: transformer["efficiency"],
        3: transformer["periodical costs"],
        4: transformer["variable output constraint costs"],
    }
    for num in param_dict:
        # counter
        transf_param[transf_type][num] += param_dict[num]

    if transf_type in ["ashp", "gchp"]:
        transf_param[transf_type][2] += transformer["efficiency2"]

    if transf_type == "gchp":
        transf_param[transf_type][5] += transformer["area"]
    # remove the considered tranformer from transformer sheet
    sheets["transformers"] = sheets["transformers"].drop(index=transformer["label"])
    # return the modified transf_param dict to the transformer clustering
    # method
    return transf_param, sheets


def transformer_clustering(
    building, sheets_clustering, transf_param, heat_buses_gchps, sheets
):
    """
        Main method to collect the information about the transformer
        (gasheating, ashp, gchp, electric heating), which are located
        in the considered cluster.

        :param building: DataFrame containing the building row from the\
            pre scenario sheet
        :type building: pd.Dataframe
        :param sheets_clustering:
        :type sheets_clustering: pd.DataFrame
        :param transf_param: dictionary containing the collected \
            transformer information
        :type transf_param: dict
        :param heat_buses_gchps: list, used to collect the gchps heat \
            output buses
        :type heat_buses_gchps: list

        :return:
    """
    for index, transformer in sheets_clustering["transformers"].iterrows():
        label = transformer["label"]
        technologies = ["gasheating", "electricheating", "ashp"]
        # collect gasheating transformer information
        if str(building[0]) in label and label in sheets["transformers"].index:
            if label.split("_")[1] in technologies:
                transf_param, sheets = cluster_transf_information(
                    transformer, transf_param, label.split("_")[1], sheets
                )

        # if parcel label != 0
        if str(building[1]) != "0":
            # collect gchp data
            if (
                str(building[1])[-9:] in transformer["label"]
                and "gchp" in transformer["label"]
                and transformer["label"] in sheets["transformers"].index
            ):
                transf_param, sheets = cluster_transf_information(
                    transformer, transf_param, "gchp", sheets
                )
                sheets["buses"].set_index("label", inplace=True, drop=False)
                if transformer["output"] in sheets["buses"].index:
                    sheets["buses"] = sheets["buses"].drop(index=transformer["output"])
                if transformer["label"] in sheets["transformers"]:
                    sheets["transformers"] = sheets["transformers"].drop(
                        index=transformer["label"]
                    )
    # return the collected data to the main clustering method
    return heat_buses_gchps, transf_param, sheets


def create_cluster_transformer(type, transf_param, cluster, sheets):
    """

    :param type:
    :param transf_param:
    :param cluster:
    :param sheets:
    :return:
    """
    from program_files import read_standard_parameters, append_component

    type_dict = {
        "gasheating": "building_gasheating_transformer",
        "electricheating": "building_electricheating_transformer",
        "ashp": "building_ashp_transformer",
        "gchp": "building_gchp_transformer",
    }
    standard_param, keys = read_standard_parameters(
        type_dict.get(type), "transformers", "comment"
    )
    specific_dict = {
        "label": str(cluster) + transf_dict.get(type_dict.get(type))[0],
        "comment": "automatically created",
        "input": str(cluster) + transf_dict.get(type_dict.get(type))[1],
        "output": str(cluster) + transf_dict.get(type_dict.get(type))[2],
        "output2": "None",
    }
    # insert standard parameters in the components dataset (dict)
    for i in range(len(keys)):
        specific_dict[keys[i]] = standard_param[keys[i]]
    specific_dict.update(
        {
            "efficiency": transf_param[type][1] / transf_param[type][0],
            "periodical costs": transf_param[type][3] / transf_param[type][0],
            "variable output constraint costs": transf_param[type][4]
            / transf_param[type][0],
            "max. investment capacity": standard_param["max. investment capacity"]
            * transf_param[type][0],
            "area": transf_param["gchp"][5] if type == "gchp" else "None",
        }
    )

    if type == "ashp" or type == "gchp":
        specific_dict["efficiency2"] = transf_param[type][2] / transf_param[type][0]

    # produce a pandas series out of the dict above due to
    # easier appending
    return append_component(sheets, "transformers", specific_dict)
