def create_standard_parameter_bus(label: str, bus_type: str, dh=None,
                                  cords=None):
    """
        creates a bus with standard_parameters, based on the standard
        parameters given in the "standard_parameters" dataset and adds
        it to the "sheets"-output dataset.

        :param label: label, the created bus will be given
        :type label: str
        :param bus_type: defines, which set of standard param. will be
                         given to the dict
        :type bus_type: str
        :param cords: latitude / longitude of the given bus used to \
            connect a producer bus to district heating network
        :type cords: list
        :param dh: string which can be "dh-system" (for searching the
                   nearest point on heat network or "street-1/2" if the
                   bus has to be connected to a specific intersection
        :type dh: str
    """
    from program_files.urban_district_upscaling.pre_processing \
        import read_standard_parameters, append_component
    # define individual values
    bus_dict = {'label': label}
    # extracts the bus specific standard values from the
    # standard_parameters dataset
    standard_param, standard_keys = \
        read_standard_parameters(bus_type, "buses", 'bus_type')
    # insert standard parameters in the components dataset (dict)
    for i in range(len(standard_keys)):
        bus_dict[standard_keys[i]] = standard_param[standard_keys[i]]
    # defines rather a district heating connection is possible
    if cords is not None:
        bus_dict.update({"district heating conn.": dh,
                         "lat": cords[0],
                         "lon": cords[1]})
    # appends the new created component to buses sheet
    append_component("buses", bus_dict)


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
    from program_files.urban_district_upscaling.components import Link
    # ELEC BUSES
    # get building type to specify bus type to be created
    if "RES" in building[2] and str(cluster) + "_res_electricity_bus" \
            not in sheets["buses"].index:
        bus_type = "_res_"
    elif "COM" in building[2] \
            and str(cluster) + "_com_electricity_bus" \
            not in sheets["buses"].index:
        bus_type = "_com_"
    elif "IND" in building[2] \
            and str(cluster) + "_ind_electricity_bus" \
            not in sheets["buses"].index:
        bus_type = "_ind_"
    else:
        bus_type = None
    # if the considered building type is in (RES, COM, IND)
    if bus_type:
        # create building type specific bus
        create_standard_parameter_bus(
            label=str(cluster) + bus_type + "electricity_bus",
            bus_type="building" + bus_type + "electricity_bus")
        # reset index to label to ensure further attachments
        sheets["buses"].set_index("label", inplace=True, drop=False)
        
        # Creates a Bus connecting the cluster electricity bus with
        # the res electricity bus
        Link.create_link(label=str(cluster) + bus_type + "electricity_link",
                         bus_1=str(cluster) + "_electricity_bus",
                         bus_2=str(cluster) + bus_type + "electricity_bus",
                         link_type='building_pv_building_link')
        # reset index to label to ensure further attachments
        sheets["links"].set_index("label", inplace=True, drop=False)
        
    return sheets


def create_cluster_averaged_bus(sink_parameters, cluster, type,
                                sheets, standard_param):
    """

    :param sink_parameters:
    :param cluster:
    :param type:
    :return:
    """
    bus_parameters = standard_param.parse('buses', index_col='bus_type')
    if type != "gas":
        type1, type2, type3, type4 = "hp_elec", "hp_electricity", \
                                     "hp_electricity", "electricity"
    else:
        type1, type2, type3, type4 = "gas", "res_gas", "com_gas", "gas"

    # calculate cluster's total heat demand
    total_annual_demand = \
        (sink_parameters[4] + sink_parameters[5] + sink_parameters[6])
    # create standard_parameter gas bus
    create_standard_parameter_bus(label=str(cluster) + "_" + type1 + "_bus",
                                  bus_type='building_' + type2 + '_bus')
    # reindex for further attachments
    sheets["buses"].set_index("label", inplace=True, drop=False)
    # recalculate gas bus shortage costs building type weighted
    costs_type = "shortage costs"
    sheets["buses"].loc[(str(cluster) + "_" + type1 + "_bus"), costs_type] = \
        ((sink_parameters[4] / total_annual_demand)
         * bus_parameters.loc["building_" + type2 + "_bus"][costs_type]
         + (sink_parameters[5] / total_annual_demand)
         * bus_parameters.loc["building_" + type3 + "_bus"][costs_type]
         + (sink_parameters[6] / total_annual_demand)
         * bus_parameters.loc["building_ind_" + type4 + "_bus"][costs_type])
    return sheets