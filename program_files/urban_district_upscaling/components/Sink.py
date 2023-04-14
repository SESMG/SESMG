import pandas


def create_standard_parameter_sink(sink_type: str, label: str, sink_input: str,
                                   annual_demand: float, sheets: dict,
                                   standard_parameters: pandas.ExcelFile
                                   ) -> dict:
    """
        Creates a sink with standard_parameters, based on the standard
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
        :param annual_demand: Annual demand previously calculated by \
            the method provided for the considered sink type, \
            representing the energy demand of the sink.
        :type annual_demand: float
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
                            standard_parameters: pandas.ExcelFile) -> dict:
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
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
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
                     standard_parameters: pandas.ExcelFile) -> dict:
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
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
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
            units = str(int(building["units"])) if building["units"] < 12 \
                else "> 12"
            # specific demand per area
            specific_heat_demand = standard_param.loc[yoc][units + " unit(s)"]
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
                   standard_parameters: pandas.ExcelFile) -> dict:
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
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
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
                 standard_parameters: pandas.ExcelFile) -> dict:
    """
        In this method, the sinks necessary to represent the demand of
        a building are created one after the other. These are an
        electricity sink, a heat sink and, if provided by the user
        (distance of Electric vehicle > 0), an EV_sink. Finally they
        are appended to the return structure "sheets".
        
        :param building: building specific data which were imported \
            from the US-Input sheet
        :type building: pandas.Series
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


def sink_clustering(building: list, sink: pandas.Series,
                    sink_parameters: list) -> list:
    """
        In this method, the current sinks of the respective cluster are
        stored in dict and the current sinks are deleted. Furthermore,
        the heat buses and heat requirements of each cluster are
        collected in order to summarize them afterwards.

        :param building: list containing the building label [0], the \
            building's parcel ID [1] and the building type [2]
        :type building: list
        :param sink: One column of the sinks sheet
        :type sink: pandas.Series
        :parameter sink_parameters: list containing clusters' sinks \
            information
        :type sink_parameters: list
        
        :return: - **sink_parameters** (list) - list containing \
            clusters' sinks information which were modified within \
            this method
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


def create_cluster_electricity_sinks(standard_parameters: pandas.ExcelFile,
                                     sink_parameters: list, cluster: str,
                                     central_electricity_network: bool,
                                     sheets: dict) -> dict:
    """
        In this method, the electricity purchase price for the
        respective sink is calculated based on the electricity demand
        of the unclustered sinks. For example, if residential buildings
        account for 30% of the cluster electricity demand, 30% of the
        central electricity purchase price is formed from the
        residential tariff. In addition, the inputs of the cluster
        sinks, if there is an electricity demand, are changed to the
        cluster internal buses, so that the energy flows in the cluster
        can be correctly determined again.
        
        :param standard_parameters: pandas imported ExcelFile \
                containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        :parameter sink_parameters: list containing clusters' sinks \
            information
        :type sink_parameters: list
        :param cluster: Cluster ID
        :type cluster: str
        :param central_electricity_network: boolean which decides \
            whether a central electricity exchange is possible or not
        :param sheets: dictionary containing the pandas.Dataframes that\
                will represent the model definition's Spreadsheets
        :type sheets: dict
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    from program_files import (Link, Bus)

    bus_parameters = standard_parameters.parse("1_buses", index_col="bus_type")
    total_annual_demand = sum(sink_parameters[0:3])
    # if the clusters total annual electricity demand is greater 0
    if total_annual_demand > 0:
        # if there is no cluster electricity bus
        if cluster + "_electricity_bus" not in sheets["buses"].index:
            # create the clusters electricity bus
            sheets = Bus.create_standard_parameter_bus(
                label=str(cluster) + "_electricity_bus",
                bus_type="building_res_electricity_bus",
                sheets=sheets,
                standard_parameters=standard_parameters)
            sheets["buses"].set_index("label", inplace=True, drop=False)
            cost_type = "shortage costs"
            label = "_electricity_bus"
            # calculate the averaged shortage costs based on the
            # percentage of the considered demand on the total demand
            sheets["buses"].loc[(str(cluster) + label), cost_type] = (
                (sink_parameters[0] / total_annual_demand)
                * bus_parameters.loc["building_res" + label][cost_type]
                + (sink_parameters[1] / total_annual_demand)
                * bus_parameters.loc["building_com" + label][cost_type]
                + (sink_parameters[2] / total_annual_demand)
                * bus_parameters.loc["building_ind" + label][cost_type]
            )
        # if there is an opportunity for central electric exchange the
        # new created bus has to be connected to the central electricity
        # bus
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
