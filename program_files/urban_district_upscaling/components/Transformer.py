"""
    Christian Klemm - christian.klemm@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
    Janik Budde - janik.budde@fh-muenster.de
"""
import pandas


def get_technology_dict(fuel_type: str, label: str, output: str,
                        de_centralized: str, transformer_type: str,
                        category: str):
    """
    
    """
    # update the global data structure which contains the components
    # label, output buses and input bus
    fuel_type_wo_gaps = fuel_type.replace(" ", "_")
    
    return {
        "combined heat and power " + fuel_type + "central":
            [label + "_chp", label + "_" + fuel_type_wo_gaps,
             label + "_electricity", output],
        category + " heating " + fuel_type + de_centralized:
            [label + "_" + fuel_type_wo_gaps + "heating_plant",
             label + "_" + fuel_type_wo_gaps, output, "None"],
        category + " heating " + de_centralized:
            [label + "_" + transformer_type.split(" ")[0] + "_heating_plant",
             label + "_" + fuel_type, output, "None"],
        "heat pump " + fuel_type + de_centralized:
            [label + "_" + fuel_type_wo_gaps + "heatpump",
             label + "_heatpump_electricity_", output, "None"],
        "central_biomass_transformer":
            ["biomass", "biomass", output, "None"],
        "electrolysis central":
            [label + "_electrolysis", de_centralized + "_electricity_",
             de_centralized + "_hydrogen", "None"],
        "methanization central":
            [label + "_methanization", de_centralized + "_hydrogen_",
             de_centralized + "_natural_gas", "None"],
        "fuel cell central":
            [label + "_fuelcell", de_centralized + "_hydrogen_",
             de_centralized + "_electricity", output],
        "woodstove decentral":
            [label + "_woodstove", label + "_wood_", output, "None"]
    }


def create_transformer(label: str, transformer_type: str, sheets: dict,
                       standard_parameters: pandas.ExcelFile,
                       de_centralized: str, flow_temp: str, category="",
                       building_type=None, area="0",
                       fuel_type="None", output="None", min_invest="0",
                       length_geoth_probe="0", heat_extraction="0") -> dict:
    """
        Sets the specific parameters for a transformer component,
        creates them and appends them to the return data structure
        "sheets" afterwards.
        
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
        :param label: since this method is used to create decentral as \
            well as central transformer components the label specifies \
            the first part of the components label.
        :type label: str
        :param fuel_type: with the help of the fuel_type attribute the \
            transformer's fuel type is chosen
        :type fuel_type: str
        :param output: within the output attribute a transformer \
            individual output bus label can be set. This attribute \
            does not have to be filled for each transformer type which \
            is the reason for the standard value.
        :type output: str
        :param min_invest: if the user's input contains an already \
            existing transformer it's capacity is the min investment \
            value of the transformer to be created
        :type min_invest: str
        :param len_geoth_probe: length of the vertical heat exchanger \
            relevant for GCHPs
        :type len_geoth_probe: str
        :param heat_extraction: heat extraction for the heat exchanger \
            referring to the location
        :type heat_extraction: str
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    from program_files import create_standard_parameter_comp
    from program_files import Bus
    
    transformer_type = transformer_type + de_centralized
    
    technology_dict = get_technology_dict(fuel_type=fuel_type,
                                          label=label,
                                          output=output,
                                          de_centralized=de_centralized,
                                          transformer_type=transformer_type,
                                          category=category)
    input_bus = technology_dict.get(transformer_type)[1] + "bus"
    
    # differentiate the building type due to different shortage costs
    if building_type is not None:
        if building_type in ["single family building",
                             "multi family building", "0"]:
            electricity_bus = "electricity bus residential decentral"
            gas_bus = "gas bus residential decentral"
            oil_bus = "oil bus residential decentral"
        elif building_type == "IND":
            electricity_bus = "electricity bus industrial decentral"
            gas_bus = "gas bus industrial decentral"
            oil_bus = "oil bus industrial decentral"
        else:
            electricity_bus = "electricity bus commercial decentral"
            gas_bus = "gas bus commercial decentral"
            oil_bus = "oil bus commercial decentral"
            
        switch_dict = {
            "electric heating decentral": ["_electricity_bus", electricity_bus],
            "gas heating natural gas decentral": ["_natural_gas_bus", gas_bus],
            "oil heating decentral": ["_oil_bus", oil_bus],
            "woodstove decentral": ["_wood_bus", "wood bus decentral"],
            "biomass heating pellet decentral": ["_pellet_bus", "pellet bus decentral"]
        }
        try:
            # get the transformer type specific input bus label and
            # type
            input_bus_list = switch_dict.get(transformer_type)
            # create the transformer specific input bus
            if (len(sheets["buses"]) == 0
                    or str(label) + input_bus_list[0] not in
                    list(sheets["buses"]["label"])):
                sheets = Bus.create_standard_parameter_bus(
                    label=str(label) + input_bus_list[0],
                    bus_type=input_bus_list[1],
                    sheets=sheets,
                    standard_parameters=standard_parameters
                )
            input_bus = str(label) + input_bus_list[0]
        except ValueError:
            pass
        
    if not technology_dict.get(transformer_type)[2] == output:
        output1 = technology_dict.get(transformer_type)[2] + "_bus"
    else:
        output1 = output

    return create_standard_parameter_comp(
        specific_param={
            "label": technology_dict.get(transformer_type)[0]
            + "_transformer",
            "input": input_bus,
            "output": output1,
            "output2": technology_dict.get(transformer_type)[3],
            "area": float(area),
            "temperature high": flow_temp,
            "min. investment capacity": float(min_invest),
            "length of the geoth. probe": float(length_geoth_probe),
            "heat extraction": float(heat_extraction)
        },
        standard_parameter_info=[transformer_type, "4_transformers",
                                 "transformer type"],
        sheets=sheets,
        standard_parameters=standard_parameters
    )


def building_transformer(building: dict, p2g_link: bool, sheets: dict,
                         standard_parameters: pandas.ExcelFile) -> dict:
    """
        In this method, the transformer investment options that can be
        applied to a considered building by the user are created. This
        includes ASHP, Gas heating system, Electric heating system, oil
        heating system and woodstove. In the creation process, these
        are attached to the return data structure "sheets", which in
        the end will represent the model definition spreadsheet.
        
        :param building: dictionary holding the building specific data
        :type building: dict
        :param p2g_link: boolean defining rather a p2g system which \
            creates a central naturalgas bus exists or not
        :type p2g_link: bool
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    from program_files.urban_district_upscaling.components import Link
    from program_files.urban_district_upscaling.pre_processing \
        import represents_int
    
    build_transformer_dict = {
        # 0: building type, 1: transformer type, 2: fuel type, 3: category
        "ashp":
            [None, "heat pump", "air source ", ""],
        "aahp":
            [None, "heat pump", "air to air ", ""],
        "gas heating":
            [building["building type"], "gas heating", "natural gas ", "gas"],
        "electric heating":
            [building["building type"], "electric heating", "", "electric"],
        "oil heating":
            [building["building type"], "oil heating", "", "oil"],
        "wood stove":
            [building["building type"], "woodstove", "", ""],
        "pellet heating":
            [building["building type"], "biomass heating", "pellet ", "biomass"],
    }
    
    for transformer in build_transformer_dict:
        
        # change output bus if the heat share of the wood stove is
        # defined
        if (transformer == "wood stove"
                and building["wood stove share"] != "standard"):
            output = building["label"] + "_wood_stove_heat_bus"
        else:
            output = building["label"] + "_heat_bus"
            
        # check if the current transformer is activated
        if building[transformer] not in ["no", "No", "0"]:
            # Check if the user has inserted a min investment value
            # or a boolean yes
            if represents_int(building[transformer]):
                min_invest = building[transformer]
            else:
                min_invest = "0"
            
            # get the transformer type specific list of attributes
            transformer_list = build_transformer_dict[transformer]
                
            sheets = create_transformer(
                label=building["label"],
                building_type=transformer_list[0],
                transformer_type=transformer_list[1] + " " + transformer_list[2],
                sheets=sheets,
                standard_parameters=standard_parameters,
                flow_temp=building["flow temperature"],
                min_invest=min_invest,
                de_centralized="decentral",
                fuel_type=transformer_list[2],
                category=transformer_list[3],
                output=output
            )
            
            if transformer == "gas heating" and p2g_link:
                if (building["label"] + "_central_natural_gas_link"
                        not in list(sheets["links"]["label"])):
                    sheets = Link.create_link(
                        label=building["label"] + "_central_natural_gas_link",
                        bus_1="central_natural_gas_bus",
                        bus_2=building["label"] + "_natural_gas_bus",
                        link_type="natural gas central link decentral",
                        sheets=sheets,
                        standard_parameters=standard_parameters
                    )
    return sheets


def create_gchp(tool: pandas.DataFrame, parcels: pandas.DataFrame,
                sheets: dict, standard_parameters: pandas.ExcelFile
                ) -> (dict, dict):
    """
        Method that creates a GCHP and its buses for the parcel and \
        appends them to the sheets return structure.

        :param tool: DataFrame containing the building data from the \
            upscaling tool's input file
        :type tool: pandas.DataFrame
        :param parcels: DataFrame containing the energy system's \
            parcels as well as their size
        :type parcels: pandas.DataFrame
        :param sheets: dictionary containing the pandas.Dataframes that\
                will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        
        :returns:   - **gchps** (dict) - dictionary holding the gchp \
                        label area combination
                    - **sheets** (dict) - dictionary containing the \
                        pandas.Dataframes that will represent the \
                        model definition's Spreadsheets which was \
                        modified in this method
    """
    from program_files.urban_district_upscaling.components import Bus
    # TODO parcel ID and ID parcel have to be unified
    # TODO how to solve the "true bools" data structure
    # create GCHPs parcel wise
    gchps = {}
    for num, parcel in parcels.iterrows():
        build_parcel = tool[
            (tool["active"].isin(["Yes", "yes", 1]))
            & (tool["gchp"].isin(["Yes", "yes", 1]))
            & (tool["parcel ID"] == parcel["ID parcel"])
            ]
        if not build_parcel.empty:
            gchps.update({parcel["ID parcel"][-9:]: [
                parcel["gchp area (m²)"],
                parcel["length of the geoth. probe (m)"],
                parcel["heat extraction"]]})
    # create gchp relevant components
    for gchp in gchps:
        # TODO What supply temperature do we use here, do we have to
        #  average that of the buildings?
        sheets = create_transformer(
            area=gchps[gchp][0],
            transformer_type="heat pump ground-coupled ",
            sheets=sheets,
            standard_parameters=standard_parameters,
            flow_temp="60",
            length_geoth_probe=gchps[gchp][1],
            heat_extraction=gchps[gchp][2],
            de_centralized="decentral",
            fuel_type="ground-coupled ",
            output=gchp + "_heat_bus",
            label=gchp
        )
        
        # create the electricity bus for the electric consumption of the
        # heat pump
        sheets = Bus.create_standard_parameter_bus(
            label=gchp + "_heatpump_electricity_bus",
            bus_type="electricity bus heat pump decentral",
            sheets=sheets,
            standard_parameters=standard_parameters
        )
        
        # create the heat bus for the thermal output of the heat pump
        sheets = Bus.create_standard_parameter_bus(
            label=gchp + "_heat_bus",
            bus_type="heat bus heat pump decentral",
            sheets=sheets,
            standard_parameters=standard_parameters
        )
    return gchps, sheets


def cluster_transformer_information(transformer: pandas.DataFrame,
                                    cluster_parameters: dict, technology: str,
                                    sheets: dict) -> (dict, dict):
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

        :returns: - **cluster_parameters** (dict) - dictionary holding \
                        the clustered information of the deleted \
                        transformers
                  - **sheets** (dict) - dictionary containing the \
                        pandas.Dataframes that will represent the \
                        model definition's Spreadsheets which was \
                        modified in this method
    """
    param_dict = {
        0: 1,
        1: transformer["efficiency"],
        2: transformer["periodical costs"],
        3: transformer["variable output constraint costs"],
        4: transformer["area"],
        5: transformer["length of the geoth. probe"],
        6: transformer["heat extraction"],
        7: transformer["temperature high"]
    }
    for num in param_dict:
        # counter
        cluster_parameters[technology][num] += float(param_dict[num])

    # remove the considered transformer from transformer sheet
    sheets["transformers"] = \
        sheets["transformers"].drop(index=transformer["label"])
    # return the modified transformer parameter dict to the transformer
    # clustering method
    return cluster_parameters, sheets


def transformer_clustering(building: list, sheets: dict,
                           sheets_clustering: dict, cluster_parameters: dict
                           ) -> (dict, dict):
    """
        Main method to collect the information about the transformer
        (gasheating, ashp, gchp, electric heating, air-to-air
        heatpumps), which are located in the considered cluster.

        :param building: list containing the building information from \
            the US-Input sheet
        :type building: list
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param sheets_clustering: copy of the model definition created \
            within the pre_processing.py
        :type sheets_clustering: dict
        :param cluster_parameters: dictionary containing the collected \
            transformer information
        :type cluster_parameters: dict

        :returns: - **cluster_parameters** (dict) - dictionary \
                        containing the collected transformer information
                  - **sheets** (dict) - dictionary containing the \
                        pandas.Dataframes that will represent the \
                        model definition's Spreadsheets which was \
                        modified in this method
    """
    for index, transformer in sheets_clustering["transformers"].iterrows():
        label = transformer["label"]
        technologies = cluster_parameters.keys()
        
        # collect gasheating transformer information
        if str(building[0]) in label and label in sheets["transformers"].index:
            for technology in technologies:
                if technology in label:
                    cluster_parameters, sheets = (
                        cluster_transformer_information(
                            transformer=transformer,
                            cluster_parameters=cluster_parameters,
                            technology=technology,
                            sheets=sheets))
                
        # if parcel label != 0
        if str(building[1]) not in ["0", 0, "None"]:
            # collect gchp data
            if (str(building[1]) in transformer["label"]
                and "ground-coupled_heatpump" in transformer["label"]
                and transformer["label"] in sheets["transformers"].index
            ):
                cluster_parameters, sheets = cluster_transformer_information(
                    transformer=transformer,
                    cluster_parameters=cluster_parameters,
                    technology="ground-coupled_heatpump",
                    sheets=sheets)
                sheets["buses"].set_index("label", inplace=True, drop=False)
                
                if transformer["output"] in sheets["buses"].index:
                    sheets["buses"] = \
                        sheets["buses"].drop(index=transformer["output"])
                if transformer["label"] in sheets["transformers"]:
                    sheets["transformers"] = \
                        sheets["transformers"].drop(index=transformer["label"])
    # return the collected data to the main clustering method
    return cluster_parameters, sheets


def create_cluster_transformer(technology: str, cluster_parameters: dict,
                               cluster: str, sheets: dict,
                               standard_parameters: pandas.ExcelFile) -> dict:
    """
        After collecting the attributes of the building specific
        transformers and deleting them, this method creates the
        clustered transformer components and appends them to the return
        data structure "sheets".
        
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

        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    from program_files import read_standard_parameters, append_component
    
    # dictionary holding the technology transformer type combination for
    # importing the standard_parameters
    type_dict = {
        "natural_gas_heating":
            ["gas heating natural gas decentral", "natural gas ", "gas"],
         "electric_heating":
             ["electric heating decentral", "electricity_", "electric"],
         "air_source_heatpump":
             ["heat pump air source decentral", "air source ", ""],
         "ground-coupled_heatpump":
             ["heat pump ground-coupled decentral", "ground-coupled ", ""],
         "air_to_air_heatpump":
             ["heat pump air to air decentral", "air to air ", ""],
         "oil_heating":
             ["oil heating decentral", "oil_", "oil"],
         "pellet_heating":
             ["biomass heating pellet decentral", "pellet ", "biomass"]}
    
    technology_dict = get_technology_dict(
        fuel_type=type_dict.get(technology)[1],
        label=cluster,
        output=cluster + "_heat_bus",
        de_centralized="decentral",
        transformer_type=type_dict.get(technology)[0],
        category=type_dict.get(technology)[2])

    # since the first entry of each technology list is the occurrence
    # a variable is defined
    counter = cluster_parameters[technology][0]
    
    standard_param, keys = read_standard_parameters(
        name=type_dict.get(technology)[0],
        parameter_type="4_transformers",
        index="transformer type",
        standard_parameters=standard_parameters
    )
    
    technology_list = technology_dict.get(type_dict.get(technology)[0])
    specific_dict = {
        "label": technology_list[0],
        "input": technology_list[1] + "bus",
        "output": technology_list[2],
        "output2": "None",
        "min. investment capacity": 0
    }
    # insert standard parameters in the components dataset (dict)
    for i in range(len(keys)):
        specific_dict[keys[i]] = standard_param[keys[i]].iloc[0]
    
    # averaging the transformer parameter
    entries_dict = {"efficiency": 1,
                    "periodical costs": 2,
                    "variable output constraint costs": 3,
                    "area": 4,
                    "length of the geoth. probe": 5,
                    "heat extraction": 6,
                    "temperature high": 7}
    
    for i in entries_dict:
        specific_dict.update({
            i: cluster_parameters[technology][entries_dict.get(i)] / counter})
        
    specific_dict.update({
        "max. investment capacity":
            standard_param["max. investment capacity"].iloc[0] * counter,
        })
    
    specific_dict["transformer type"] = specific_dict["transformer type.1"]
    del (specific_dict["transformer type.1"])
    # produce a pandas series out of the dict above due to
    # easier appending
    return append_component(sheets, "transformers", specific_dict)
