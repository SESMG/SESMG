import pandas

technology_dict = {
    "building_gchp_transformer":
        ["gchp", "hp_elec", "heat", "None"],
    "building_ashp_transformer":
        ["ashp", "hp_elec", "heat", "None"],
    "building_gasheating_transformer":
        ["gasheating", "gas", "heat", "None"],
    "building_oilheating_transformer":
        ["oilheating", "oil", "heat", "None"],
    "building_electricheating_transformer":
        ["electricheating", "electricity", "heat", "None"],
}


def create_transformer(building_id: str, transformer_type: str, sheets: dict,
                       standard_parameters: pandas.ExcelFile,
                       flow_temp: str, building_type=None,
                       area="0", label="None", specific="None",
                       output="None"):
    """
    
        :param building_id: building label
        :type building_id: str
        :param transformer_type: string containing the type of \
            transformer which has to be created
        :type transformer_type: str
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        :param flow_temp: flow temperature of the heating system which \
            is necessary for the COP calculation of heat pumps etc.
        :type flow_temp: str
        :param building_type: building type is used to define the \
            shortage costs of heatpump electricity, gas, oil etc.
        :type building_type: str
        :param area: potential area for gchps
        :type area: str
        :param label: TODO
        :type label: str
        :param specific: TODO
        :type specific: str
        :param output:
        :type output: str
    """
    from program_files import create_standard_parameter_comp
    from program_files import Bus

    # update the global data structure which contains the components
    # label, output buses and input bus
    technology_dict.update(
        {
            "central_" + specific + "_chp":
                [label + "_chp", label, label + "_elec", output],
            "central_" + specific + "_heating_plant_transformer":
                [label + "_heating_plant", label, output, "None"],
            "central_" + specific + "_transformer":
                [label + "_heatpump", "heatpump_elec", output, "None"],
            # TODO
            "central_biomass_transformer":
                ["biomass", "biomass", output, "None"],
            "central_electrolysis_transformer":
                [label + "_electrolysis", "electricity", "h2", "None"],
            "central_methanization_transformer":
                [label + "_methanization", "h2", "naturalgas", "None"],
            "central_fuelcell_transformer":
                [label + "_fuelcell", "h2", "electricity", output],
        }
    )
    
    # differentiate the building type due to different shortage costs
    if building_type is not None:
        if building_type in ["SFB", "MFB", "0"]:
            bus = "building_res_gas_bus"
            oil_bus = "building_res_oil_bus"
        elif building_type == "IND":
            bus = "building_ind_gas_bus"
            oil_bus = "building_ind_oil_bus"
        else:
            bus = "building_com_gas_bus"
            oil_bus = "building_com_oil_bus"
            
        if transformer_type == "building_gasheating_transformer":
            sheets = Bus.create_standard_parameter_bus(
                label=str(building_id) + "_gas_bus", bus_type=bus,
                sheets=sheets, standard_parameters=standard_parameters
            )
        if transformer_type == "building_oilheating_transformer":
            sheets = Bus.create_standard_parameter_bus(
                label=str(building_id) + "_oil_bus", bus_type=oil_bus,
                sheets=sheets, standard_parameters=standard_parameters
            )

    if not technology_dict.get(transformer_type)[2] == output:
        output1 = str(building_id) + "_" \
                  + technology_dict.get(transformer_type)[2] + "_bus"
    else:
        output1 = output

    return create_standard_parameter_comp(
        specific_param={
            "label": building_id
            + "_"
            + technology_dict.get(transformer_type)[0]
            + "_transformer",
            "input": building_id
            + "_"
            + technology_dict.get(transformer_type)[1] + "_bus",
            "output": output1,
            "output2": technology_dict.get(transformer_type)[3],
            "area": float(area),
            "temperature high": flow_temp
        },
        standard_parameter_info=[transformer_type, "4_transformers",
                                 "transformer_type"],
        sheets=sheets,
        standard_parameters=standard_parameters
    )


def building_transformer(building: dict, p2g_link: bool, true_bools: list,
                         sheets: dict, standard_parameters: pandas.ExcelFile):
    """
        TODO
        :param building: dictionary holding the building specific data
        :type building: dict
        :param p2g_link: boolean defining rather a p2g system which \
            creates a central naturalgas bus exists or not
        :type p2g_link: bool
        :param true_bools: list containing the entries that are \
            evaluated as true
        :type true_bools: list
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
    """
    from program_files.urban_district_upscaling.components import Link
    
    build_transformer_dict = {
        "ashp":
            [None, "building_ashp_transformer"],
        "gas heating":
            [building["building type"], "building_gasheating_transformer"],
        "electric heating":
            [None, "building_electricheating_transformer"],
        "oil heating":
            [building["building type"], "building_oilheating_transformer"]
    }
    
    for transformer in build_transformer_dict:
        # creates air source heat-pumps
        if building[transformer] in true_bools:
            sheets = create_transformer(
                building_id=building["label"],
                building_type=build_transformer_dict[transformer][0],
                transformer_type=build_transformer_dict[transformer][1],
                sheets=sheets,
                standard_parameters=standard_parameters,
                flow_temp=building["flow temperature"]
            )
            if transformer == "gas heating" and p2g_link:
                sheets = Link.create_link(
                    label="central_naturalgas_" + building["label"] + "link",
                    bus_1="central_naturalgas_bus",
                    bus_2=building["label"] + "_gas_bus",
                    link_type="central_naturalgas_building_link",
                    sheets=sheets,
                    standard_parameters=standard_parameters
                )
    return sheets


def cluster_transformer_information(transformer: pandas.DataFrame,
                                    cluster_parameters: dict, technology: str,
                                    sheets: dict):
    """
        Collects the transformer information of the selected type, and
        inserts it into the dict containing the cluster specific
        transformer data.

        :param transformer: Dataframe containing the transformer under \
            investigation
        :type transformer: pandas.DataFrame
        :param cluster_parameters: dictionary containing the cluster \
            summed transformer information
        :type cluster_parameters: dict
        :param technology: transformer type needed to define the dict \
            entry to be modified
        :type technology: str
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict

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
        cluster_parameters[technology][num] += param_dict[num]

    if technology in ["ashp", "gchp"]:
        cluster_parameters[technology][2] += transformer["efficiency2"]

    if technology == "gchp":
        cluster_parameters[technology][5] += transformer["area"]
    # remove the considered transformer from transformer sheet
    sheets["transformers"] = \
        sheets["transformers"].drop(index=transformer["label"])
    # return the modified transformer parameter dict to the transformer
    # clustering method
    return cluster_parameters, sheets


def transformer_clustering(building: pandas.DataFrame, sheets: dict,
                           sheets_clustering: dict, cluster_parameters: dict,
                           heat_buses_gchps: list):
    """
        Main method to collect the information about the transformer
        (gasheating, ashp, gchp, electric heating), which are located
        in the considered cluster.

        :param building: DataFrame containing the building row from the\
            pre scenario sheet
        :type building: pandas.Dataframe
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param sheets_clustering:
        :type sheets_clustering: dict
        :param cluster_parameters: dictionary containing the collected \
            transformer information
        :type cluster_parameters: dict
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
                cluster_parameters, sheets = cluster_transformer_information(
                    transformer=transformer,
                    cluster_parameters=cluster_parameters,
                    technology=label.split("_")[1],
                    sheets=sheets)
                
        # if parcel label != 0
        if str(building[1]) != "0":
            # collect gchp data
            if (
                str(building[1])[-9:] in transformer["label"]
                and "gchp" in transformer["label"]
                and transformer["label"] in sheets["transformers"].index
            ):
                cluster_parameters, sheets = cluster_transformer_information(
                    transformer=transformer,
                    cluster_parameters=cluster_parameters,
                    technology="gchp",
                    sheets=sheets)
                sheets["buses"].set_index("label", inplace=True, drop=False)
                
                if transformer["output"] in sheets["buses"].index:
                    sheets["buses"] = \
                        sheets["buses"].drop(index=transformer["output"])
                if transformer["label"] in sheets["transformers"]:
                    sheets["transformers"] = \
                        sheets["transformers"].drop(index=transformer["label"])
    # return the collected data to the main clustering method
    return heat_buses_gchps, cluster_parameters, sheets


def create_cluster_transformer(technology: str, cluster_parameters: dict,
                               cluster: str, sheets: dict,
                               standard_parameters: pandas.ExcelFile):
    """
        TODO METHOD DESCRIPTION
        
        :param technology: str containing the transformer type
        :type technology: str
        :param cluster_parameters: dict containing the cluster's \
            transformer parameters (index) technology each entry is a \
            list where index 0 is a counter
        :type cluster_parameters: list
        :param cluster: str containing the cluster's ID
        :type cluster: str
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile

        :return:
    """
    from program_files import read_standard_parameters, append_component
    
    # dictionary holding the technology transformer type combination for
    # importing the standard_parameters
    type_dict = {"gasheating": "building_gasheating_transformer",
                 "electricheating": "building_electricheating_transformer",
                 "ashp": "building_ashp_transformer",
                 "gchp": "building_gchp_transformer"}
    
    # since the first entry of each technology list is the occurrence
    # a variable is defined
    counter = cluster_parameters[technology][0]
    
    standard_param, keys = read_standard_parameters(
        name=type_dict.get(technology),
        param_type="4_transformers",
        index="transformer_type",
        standard_parameters=standard_parameters
    )
    
    specific_dict = {
        "label": cluster + technology_dict.get(type_dict.get(technology))[0],
        "input": cluster + technology_dict.get(type_dict.get(technology))[1],
        "output": cluster + technology_dict.get(type_dict.get(technology))[2],
        "output2": "None",
    }
    # insert standard parameters in the components dataset (dict)
    for i in range(len(keys)):
        specific_dict[keys[i]] = standard_param[keys[i]]
    
    # averaging the transformer parameter
    entries_dict = {"efficiency": 1,
                    "periodical costs": 3,
                    "variable output constraint costs": 4}
    
    for i in entries_dict:
        specific_dict.update({
            i: cluster_parameters[technology][entries_dict.get(i)] / counter})
    
    specific_dict.update({
        "max. investment capacity": standard_param["max. investment capacity"]
        * counter,
        "area": cluster_parameters["gchp"][5]
        if technology == "gchp" else "None"})

    if technology in ["ashp", "gchp"]:
        specific_dict["efficiency2"] = \
            cluster_parameters[technology][2] / counter

    # produce a pandas series out of the dict above due to
    # easier appending
    return append_component(sheets, "transformers", specific_dict)
