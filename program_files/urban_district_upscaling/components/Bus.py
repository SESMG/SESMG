import pandas


def create_standard_parameter_bus(label: str, bus_type: str, sheets: dict,
                                  standard_parameters: pandas.ExcelFile,
                                  coords=None) -> dict:
    """
        Creates a bus with standard_parameters, based on the standard
        parameters given in the "standard_parameters" dataset and adds
        it to the "sheets"-output dataset.
    
        :param label: label, the created bus will be given
        :type label: str
        :param bus_type: defines, which set of standard param. will be
                         given to the dict
        :type bus_type: str
        :param sheets: dictionary containing the pandas.Dataframes that\
                will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        :param coords: latitude / longitude / dh column of the given bus\
            used to connect a producer bus to district heating network
        :type coords: list
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    from program_files import read_standard_parameters, append_component

    # define individual values
    bus_dict = {"label": label}
    # extracts the bus specific standard values from the
    # standard_parameters dataset
    standard_param, standard_keys = read_standard_parameters(
        name=bus_type,
        param_type="1_buses",
        index="bus_type",
        standard_parameters=standard_parameters
    )
    # insert standard parameters in the components dataset (dict)
    for i in range(len(standard_keys)):
        bus_dict[standard_keys[i]] = standard_param[standard_keys[i]]
    # defines rather a district heating connection is possible
    if coords is not None:
        bus_dict.update(
            {"district heating conn.": coords[2],
             "lat": coords[0], "lon": coords[1]})
    else:
        bus_dict.update({"district heating conn.": float(0)})
    # appends the new created component to buses sheet
    return append_component(sheets, "buses", bus_dict)


def create_cluster_electricity_buses(building: list, cluster: str,
                                     sheets: dict,
                                     standard_parameters: pandas.ExcelFile
                                     ) -> dict:
    """
        Method creating the building type specific electricity buses and
        connecting them to the main cluster electricity bus

        :param building: List holding the building label, parcel ID \
            and building type
        :type building: list
        :param cluster: Cluster id
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
    from . import Link

    # ELECTRICITY BUSES
    # get building type to specify bus type to be created
    if building[2] in ["SFB", "MFB"] \
            and str(cluster) + "_res_electricity_bus" \
            not in list(sheets["buses"]["label"]):
        bus_type = "_res_"
    elif "COM" in building[2] and str(cluster) + "_com_electricity_bus" \
            not in list(sheets["buses"]["label"]):
        bus_type = "_com_"
    elif "IND" in building[2] and str(cluster) + "_ind_electricity_bus" \
            not in list(sheets["buses"]["label"]):
        bus_type = "_ind_"
    else:
        bus_type = None
    # if the considered building type is in (RES, COM, IND)
    if bus_type:
        # create building type specific bus
        sheets = create_standard_parameter_bus(
            label=str(cluster) + bus_type + "electricity_bus",
            bus_type="building" + bus_type + "electricity_bus",
            sheets=sheets,
            standard_parameters=standard_parameters
        )
        # reset index to label to ensure further attachments
        sheets["buses"].set_index("label", inplace=True, drop=False)

        # Creates a Bus connecting the cluster electricity bus with
        # the res electricity bus
        sheets = Link.create_link(
            label=str(cluster) + bus_type + "electricity_link",
            bus_1=str(cluster) + "_electricity_bus",
            bus_2=str(cluster) + bus_type + "electricity_bus",
            link_type="cluster_electricity_link",
            sheets=sheets,
            standard_parameters=standard_parameters)
        
        # reset index to label to ensure further attachments
        sheets["links"].set_index("label", inplace=True, drop=False)

    return sheets


def create_cluster_averaged_bus(sink_parameters: list, cluster: str,
                                fuel_type: str, sheets: dict,
                                standard_parameters: pandas.ExcelFile) -> dict:
    """
        In this method, an average grid purchase price for natural gas \
        and heat pump electricity is calculated. This is measured \
        based on the share of the heat demand of a building type \
        (RES, COM, IND) in the total heat demand of the cluster.
        
        :param sink_parameters: list containing the cluster's sinks \
            parameter (4) res_heat_demand, (5) com_heat_demand, \
            (6) ind_heat_demand
        :type sink_parameters: list
        :param fuel_type: str defining which type of buses will be \
            clustered
        :type fuel_type: str
        :param cluster: Cluster id
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
    bus_parameters = standard_parameters.parse("1_buses", index_col="bus_type")
    type_dict = {
        "hp_elec": ["hp_elec"] + 2 * ["hp_electricity"] + ["electricity"],
        "gas": ["gas", "res_gas", "com_gas", "gas"]}
    type1, type2, type3, type4 = type_dict.get(fuel_type)

    # calculate cluster's total heat demand
    total_annual_demand = \
        sink_parameters[4] \
        + sink_parameters[5] \
        + sink_parameters[6]
    
    # create standard_parameter gas bus
    sheets = create_standard_parameter_bus(
        label=str(cluster) + "_" + type1 + "_bus",
        bus_type="building_" + type2 + "_bus",
        sheets=sheets,
        standard_parameters=standard_parameters)
    
    # reindex for further attachments
    sheets["buses"].set_index("label", inplace=True, drop=False)
    
    # recalculate gas bus shortage costs building type weighted
    costs_type = "shortage costs"
    sheets["buses"].loc[(str(cluster) + "_" + type1 + "_bus"), costs_type] = (
        (sink_parameters[4] / total_annual_demand)
        * bus_parameters.loc["building_" + type2 + "_bus"][costs_type]
        + (sink_parameters[5] / total_annual_demand)
        * bus_parameters.loc["building_" + type3 + "_bus"][costs_type]
        + (sink_parameters[6] / total_annual_demand)
        * bus_parameters.loc["building_ind_" + type4 + "_bus"][costs_type]
    )
    return sheets
