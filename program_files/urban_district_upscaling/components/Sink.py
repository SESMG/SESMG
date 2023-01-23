import pandas


def create_standard_parameter_sink(sink_type: str, label: str, sink_input: str,
                                   annual_demand: int, sheets: dict,
                                   standard_parameters: pandas.ExcelFile):
    """
        creates a sink with standard_parameters, based on the standard
        parameters given in the "standard_parameters" dataset and adds
        it to the "sheets"-output dataset.
    
        :param sink_type: needed to get the standard parameters of the
                          link to be created
        :type sink_type: str
        :param label: label, the created sink will be given
        :type label: str
        :param sink_input: label of the bus which will be the input of \
            the sink to be created
        :type sink_input: str
        :param annual_demand: #todo formula
        :type annual_demand: int
        :param sheets: dictionary containing the pandas.Dataframes that\
                will represent the model definition's Spreadsheets
            :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
                containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
    """
    from program_files import create_standard_parameter_comp

    return create_standard_parameter_comp(
        specific_param={
            "label": label,
            "input": sink_input,
            "annual demand": annual_demand,
        },
        standard_parameter_info=[sink_type, "2_sinks", "sink_type"],
        sheets=sheets,
        standard_parameters=standard_parameters
    )


def create_electricity_sink(building: pandas.Series, area: float, sheets: dict,
                            sinks_standard_param: pandas.DataFrame,
                            standard_parameters: pandas.ExcelFile):
    """
        In this method, the electricity demand is calculated either on
        the basis of energy certificates (area-specific demand values)
        or on the basis of inhabitants. Using this calculated demand
        the load profile electricity sink is created.
        
        :param building: building specific data which were imported \
            from the US-Input sheet
        :type building: pandas.Series
        :param area: building gross area
        :type area: float
        :param sheets: dictionary containing the pandas.Dataframes that\
                will represent the model definition's Spreadsheets
        :type sheets: dict
        :param sinks_standard_param: sinks sheet from standard \
            parameter sheet
        :type sinks_standard_param: pandas.DataFrame
        :param standard_parameters: pandas imported ExcelFile \
                containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
    """
    sink_param = standard_parameters.parse("2_2_electricity")
    specific_demands = {}
    # If an area-specific electricity requirement is given, e.g. from an
    # energy certificate, use the else clause.
    if not building["electricity demand"]:
        # if the investigated building is a residential building
        if building["building type"] in ["SFB", "MFB"]:
            # get all columns from electricity sink parameters sheets
            # that begin with the building type
            for column in sink_param.columns:
                if building["building type"] in column:
                    specific_demands[column[4:]] = [sink_param.loc[1, column]]
            # specific electricity demand for less/equal 5 occupants in
            # one unit
            # calculation: specific demand from standard parameter * units
            if building["occupants per unit"] <= 5:
                # specific demand column from standard parameter sheet
                column = str(int(building["occupants per unit"])) + " person"
                # demand calculation
                demand_el = specific_demands[column][0] * building["units"]
            # specific electricity demand for more than 5 occupants in
            # one unit
            # calculation:
            # specific demand =
            # (specific demand for 5 occupants per unit
            #   from standard parameter) / 5
            # occupants = total occupants of the investigated building
            # demand = specific demand * occupants
            else:
                # specific demand per occupant
                demand_el_specific = (specific_demands["5 person"][0]) / 5
                # total occupants of the investigated building
                occupants = building["occupants per unit"] * building["units"]
                # demand calculation
                demand_el = demand_el_specific * occupants
        # TODO was machen wir mit IND
        else:
            # specific demand per area
            demand_el_specific = sink_param.loc[1, building["building type"]]
            NFA_GFA = \
                sinks_standard_param.loc[
                    building["building type"] + "_electricity_sink"][
                    "net_floor_area / area"]
            demand_el = demand_el_specific * area * NFA_GFA
    else:
        demand_el = building["electricity demand"] * area
    
    return create_standard_parameter_sink(
        sink_type=building["building type"] + "_electricity_sink",
        label=str(building["label"]) + "_electricity_demand",
        sink_input=str(building["label"]) + "_electricity_bus",
        annual_demand=demand_el,
        sheets=sheets,
        standard_parameters=standard_parameters
    )


def create_heat_sink(building: pandas.Series, area: float, sheets: dict,
                     sinks_standard_param: pandas.DataFrame,
                     standard_parameters: pandas.ExcelFile):
    """
        In this method, the heat demand is calculated either on
        the basis of energy certificates (area-specific demand values)
        or on the basis of inhabitants. Using this calculated demand
        the load profile heat sink is created.

        :param building: building specific data which were imported \
            from the US-Input sheet
        :type building: pandas.Series
        :param area: building gross area
        :type area: float
        :param sheets: dictionary containing the pandas.Dataframes that\
                will represent the model definition's Spreadsheets
        :type sheets: dict
        :param sinks_standard_param: sinks sheet from standard \
            parameter sheet
        :type sinks_standard_param: pandas.DataFrame
        :param standard_parameters: pandas imported ExcelFile \
                containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
    """
    standard_param = standard_parameters.parse("2_1_heat")
    standard_param.set_index("year of construction", inplace=True)
    
    # year of construction: buildings older than 1918 are clustered in
    # <1918
    yoc = int(building["year of construction"])
    yoc = (yoc if yoc > 1918 else "<1918")
    
    # define a variable for building type
    building_type = building["building type"]
    
    # If an area-specific electricity requirement is given, e.g. from an
    # energy certificate, use the else clause.
    if not building["heat demand"]:
        # if the investigated building is a residential building
        if building_type in ["SFB", "MFB"]:
            # units: buildings bigger than 12 units are clustered in > 12
            units = str(building["units"]) if building["units"] < 12 \
                else "> 12"
            # specific demand per area
            specific_heat_demand = standard_param.loc[yoc][units + " unit(s)"]
        # TODO was machen wir mit IND
        else:
            # specific demand per area
            specific_heat_demand = standard_param.loc[yoc][building_type]
        NFA_GFA = \
            sinks_standard_param.loc[
                building["building type"] + "_heat_sink"][
                "net_floor_area / area"]
        demand_heat = specific_heat_demand * area * NFA_GFA
    else:
        demand_heat = building["heat demand"] * area
    
    return create_standard_parameter_sink(
        sink_type=building_type + "_heat_sink",
        label=str(building["label"]) + "_heat_demand",
        sink_input=str(building["label"]) + "_heat_bus",
        annual_demand=demand_heat,
        sheets=sheets,
        standard_parameters=standard_parameters
    )


def create_sink_ev(building: pandas.Series, sheets: dict,
                   standard_parameters: pandas.ExcelFile):
    """
        For the modeling of electric vehicles, within this method the
        sink for electric vehicles is created.
    
        :param building: building specific data which were imported \
            from the US-Input sheet
        :type building: pandas.Series
        :param sheets: dictionary containing the pandas.Dataframes that\
                will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
                containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
    """
    from program_files import create_standard_parameter_comp
    
    # multiply the electric vehicle time series with the driven
    # kilometers
    sheets["time series"].loc[:, building['label'] + "_electric_vehicle.fix"] \
        = sheets["time series"].loc[:, "electric_vehicle.fix"] \
        * building["distance of electric vehicles"]
    
    return create_standard_parameter_comp(
        specific_param={
            "label": building["label"] + "_electric_vehicle",
            "input": str(building["label"]) + "_electricity_bus",
            "nominal value": building["distance of electric vehicles"],
        },
        standard_parameter_info=[
            "EV_electricity_sink", "2_sinks", "sink_type"],
        sheets=sheets,
        standard_parameters=standard_parameters)


def create_sinks(building: pandas.Series, sheets: dict,
                 standard_parameters: pandas.ExcelFile):
    """
    TODO DOCSTRING
        
        :param building: building specific data which were imported \
            from the US-Input sheet
        :type building: pandas.Series
        :param sheets: dictionary containing the pandas.Dataframes that\
                will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
                containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
    """
    if building["building type"]:
        area = building["gross building area"]
        # get sinks standard parameters
        sinks_standard_param = standard_parameters.parse("2_sinks")
        sinks_standard_param.set_index("sink_type", inplace=True)
        
        # create electricity sink
        sheets = create_electricity_sink(
            building=building,
            area=area,
            sheets=sheets,
            sinks_standard_param=sinks_standard_param,
            standard_parameters=standard_parameters)

        # heat demand
        sheets = create_heat_sink(
            building=building,
            area=area,
            sheets=sheets,
            sinks_standard_param=sinks_standard_param,
            standard_parameters=standard_parameters)
        
        if building["distance of electric vehicles"] > 0:
            sheets = create_sink_ev(
                building=building,
                sheets=sheets,
                standard_parameters=standard_parameters)
    return sheets


def sink_clustering(building, sink, sink_parameters):
    """
        In this method, the current sinks of the respective cluster are
        stored in dict and the current sinks are deleted. Furthermore,
        the heat buses and heat requirements of each cluster are
        collected in order to summarize them afterwards.

        :param building: DataFrame containing the building row from the\
            pre scenario sheet
        :type building: pd.Dataframe
        :param sink: sink dataframe
        :type sink: pd.Dataframe
        :parameter sink_parameters: list containing clusters' sinks \
            information
        :type sink_parameters: list
    """
    # get cluster electricity sinks
    if str(building[0]) in sink["label"] and "electricity" in sink["label"]:
        # get res elec demand
        if "RES" in building[2]:
            sink_parameters[0] += sink["annual demand"]
            sink_parameters[8].append(sink["label"])
        # get com elec demand
        elif "COM" in building[2]:
            sink_parameters[1] += sink["annual demand"]
            sink_parameters[9].append(sink["label"])
        # get ind elec demand
        elif "IND" in building[2]:
            sink_parameters[2] += sink["annual demand"]
            sink_parameters[10].append(sink["label"])
    # get cluster heat sinks
    elif str(building[0]) in sink["label"] and "heat" in sink["label"]:
        # append heat bus to cluster heat buses
        sink_parameters[3].append((building[2], sink["input"]))
        # get res heat demand
        if "RES" in building[2]:
            sink_parameters[4] += sink["annual demand"]
        # get com heat demand
        elif "COM" in building[2]:
            sink_parameters[5] += sink["annual demand"]
        # get ind heat demand
        elif "IND" in building[2]:
            sink_parameters[6] += sink["annual demand"]
        sink_parameters[7].append((building[2], sink["label"]))
    return sink_parameters


def create_cluster_elec_sinks(
    standard_parameters, sink_parameters, cluster, central_electricity_network, sheets
):
    """

    :return:
    """
    from program_files.urban_district_upscaling.components import Link
    from program_files.urban_district_upscaling.components import Bus

    bus_parameters = standard_parameters.parse("1_buses", index_col="bus_type")
    total_annual_demand = sink_parameters[0] + sink_parameters[1] + sink_parameters[2]
    if total_annual_demand > 0:
        if cluster + "_electricity_bus" not in sheets["buses"].index:
            sheets = Bus.create_standard_parameter_bus(
                label=str(cluster) + "_electricity_bus",
                bus_type="building_res_electricity_bus",
                sheets=sheets,
                standard_parameters=standard_parameters)
            sheets["buses"].set_index("label", inplace=True, drop=False)
            cost_type = "shortage costs"
            label = "_electricity_bus"
            sheets["buses"].loc[(str(cluster) + label), cost_type] = (
                (sink_parameters[0] / total_annual_demand)
                * bus_parameters.loc["building_res" + label][cost_type]
                + (sink_parameters[1] / total_annual_demand)
                * bus_parameters.loc["building_com" + label][cost_type]
                + (sink_parameters[2] / total_annual_demand)
                * bus_parameters.loc["building_ind" + label][cost_type]
            )
        if central_electricity_network:
            sheets = Link.create_central_electricity_bus_connection(
                cluster=cluster,
                sheets=sheets,
                standard_parameters=standard_parameters)

    # create clustered electricity sinks
    if sink_parameters[0] > 0:
        for i in sink_parameters[8]:
            sheets["sinks"].loc[sheets["sinks"]["label"] == i, "input"] = (
                str(cluster) + "_res_electricity_bus"
            )
    if sink_parameters[1] > 0:
        for i in sink_parameters[9]:
            sheets["sinks"].loc[sheets["sinks"]["label"] == i, "input"] = (
                str(cluster) + "_com_electricity_bus"
            )
    if sink_parameters[2] > 0:
        for i in sink_parameters[10]:
            sheets["sinks"].loc[sheets["sinks"]["label"] == i, "input"] = (
                str(cluster) + "_ind_electricity_bus"
            )

    return sheets
