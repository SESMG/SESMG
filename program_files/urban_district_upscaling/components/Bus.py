def create_standard_parameter_bus(label: str, bus_type: str, sheets,
                                  standard_parameters, coords=None):
    """
    creates a bus with standard_parameters, based on the standard
    parameters given in the "standard_parameters" dataset and adds
    it to the "sheets"-output dataset.

    :param label: label, the created bus will be given
    :type label: str
    :param bus_type: defines, which set of standard param. will be
                     given to the dict
    :type bus_type: str
    :param sheets:
    :type sheets:
    :param standard_parameters:
    :type standard_parameters:
    :param cords: latitude / longitude / dh column of the given bus\
        used to connect a producer bus to district heating network
    :type cords: list
    """
    from program_files import read_standard_parameters, append_component

    # define individual values
    bus_dict = {"label": label}
    # extracts the bus specific standard values from the
    # standard_parameters dataset
    standard_param, standard_keys = read_standard_parameters(
        bus_type, "1_buses", "bus_type", standard_parameters
    )
    # insert standard parameters in the components dataset (dict)
    for i in range(len(standard_keys)):
        bus_dict[standard_keys[i]] = standard_param[standard_keys[i]]
    # defines rather a district heating connection is possible
    if coords is not None:
        bus_dict.update(
            {"district heating conn.": coords[2],
             "lat": coords[0], "lon": coords[1]}
        )
    else:
        bus_dict.update({"district heating conn.": 0})
    # appends the new created component to buses sheet
    return append_component(sheets, "buses", bus_dict)


def create_cluster_elec_buses(building, cluster, sheets):
    """
        Method creating the building type specific electricity buses and
        connecting them to the main cluster electricity bus

        :param building: Dataframe holding the building specific data \
            from prescenario file
        :type building: pd.Dataframe
        :param cluster: Cluster id
        :type cluster: str
    """
    from . import Link

    # ELEC BUSES
    # get building type to specify bus type to be created
    if "RES" in building[2] and str(cluster) + "_res_electricity_bus" not in list(
        sheets["buses"]["label"]
    ):
        bus_type = "_res_"
    elif "COM" in building[2] and str(cluster) + "_com_electricity_bus" not in list(
        sheets["buses"]["label"]
    ):
        bus_type = "_com_"
    elif "IND" in building[2] and str(cluster) + "_ind_electricity_bus" not in list(
        sheets["buses"]["label"]
    ):
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
        )
        # reset index to label to ensure further attachments
        sheets["buses"].set_index("label", inplace=True, drop=False)

        # Creates a Bus connecting the cluster electricity bus with
        # the res electricity bus
        sheets = Link.create_link(
            label=str(cluster) + bus_type + "electricity_link",
            bus_1=str(cluster) + "_electricity_bus",
            bus_2=str(cluster) + bus_type + "electricity_bus",
            link_type="building_pv_building_link",
            sheets=sheets,
        )
        # reset index to label to ensure further attachments
        sheets["links"].set_index("label", inplace=True, drop=False)

    return sheets


def create_cluster_averaged_bus(sink_parameters, cluster, type, sheets, standard_param):
    """

    :param sink_parameters:
    :param cluster:
    :param type:
    :return:
    """
    bus_parameters = standard_param.parse("buses", index_col="bus_type")
    if type != "gas":
        type1, type2, type3, type4 = (
            "hp_elec",
            "hp_electricity",
            "hp_electricity",
            "electricity",
        )
    else:
        type1, type2, type3, type4 = "gas", "res_gas", "com_gas", "gas"

    # calculate cluster's total heat demand
    total_annual_demand = sink_parameters[4] + sink_parameters[5] + sink_parameters[6]
    # create standard_parameter gas bus
    sheets = create_standard_parameter_bus(
        label=str(cluster) + "_" + type1 + "_bus",
        bus_type="building_" + type2 + "_bus",
        sheets=sheets,
    )
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
