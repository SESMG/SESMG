import pandas


def create_source(source_type: str, roof_num: str, building: dict,
                  sheets: dict, standard_parameters: pandas.ExcelFile,
                  st_output=None, central=False, min_invest="0"):
    """
        TODO DOCSTRINGTEXT
        :param source_type: define rather a photovoltaic or a \
            solarthermal source has to be created
        :type source_type: str
        :param roof_num: roof part number
        :type roof_num: str
        :param building: building specific data (e.g. azimuth, \
            surface tilt etc.)
        :type building: dict
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        :param st_output: str containing the solar thermal output bus \
            which is used for the connection to district heating systems
        :type st_output: str
        :param central: parameter which definies rather the source is a\
            central source (True) or a decentral one (False)
        :type central: bool
    """
    from program_files import append_component, read_standard_parameters

    # convert the building dict into a list
    source_param = [
        str(roof_num),
        building["label"],
        building["azimuth {}".format(roof_num)],
        building["surface tilt {}".format(roof_num)],
        building["latitude"],
        building["longitude"],
        building["roof area {}".format(roof_num)],
    ]
    
    # define the source's label, output bus, input bus
    switch_dict = {
        "fixed photovoltaic source": [
            "_pv_source",
            "_pv_bus",
            0],
        "solar_thermal_collector": [
            "_solarthermal_source",
            "_heat_bus",
            str(source_param[1]) + "_electricity_bus"]
    }
    
    # read the source specific standard parameters
    standard_param = standard_parameters.parse("3_sources")
    if not central:
        standard_param = standard_param.loc[
            standard_param["source_type"] == "solar_thermal_collector"]
    else:
        standard_param = standard_param.loc[
            standard_param["source_type"] == "central_solar_thermal_collector"]
    # calculate the inlet temperature which is necessary for solar
    # thermal flat plates
    temp_inlet = (
        (building["flow temperature"]
         - (2 * float(standard_param["Temperature Difference"])))
        if source_type == "solar_thermal_collector" else 0)

    # technical parameters
    source_dict = {
        "label": str(source_param[1])
        + "_"
        + str(source_param[0])
        + switch_dict.get(source_type)[0],
        "output": str(source_param[1]) + switch_dict.get(source_type)[1]
        if not st_output
        else st_output,
        "Azimuth": source_param[2],
        "Surface Tilt": source_param[3],
        "Latitude": source_param[4],
        "Longitude": source_param[5],
        "input": switch_dict.get(source_type)[2],
        "Temperature Inlet": temp_inlet,
        "min. investment capacity": min_invest
    }
    if central:
        source_type = "central_solar_thermal_collector"

    # extracts the st source specific standard values from the
    # standard_parameters dataset
    param, keys = read_standard_parameters(source_type, "3_sources",
                                           "source_type", standard_parameters)
    for i in range(len(keys)):
        source_dict[keys[i]] = param[keys[i]]

    source_dict["max. investment capacity"] = (
        param["Capacity per Area (kW/m2)"] * source_param[6]
    )

    return append_component(sheets, "sources", source_dict)


def create_timeseries_source(sheets, label, output, standard_parameters):
    """
        TODO DOCSTRINGTEXT
        :param source_type: define rather a photovoltaic or a \
            solarthermal source has to be created
        :type source_type: str
        :param roof_num: roof part number
        :type roof_num:
        :param building:
        :type building:
        :param sheets:
        :type sheets:
        """
    from program_files import append_component, read_standard_parameters

    # technical parameters
    source_dict = {
        "label": label,
        "existing capacity": 0,
        "min. investment capacity": 0,
        "output": output,
        "Azimuth": 0,
        "Surface Tilt": 0,
        "Latitude": 0,
        "Longitude": 0,
        "input": 0,
    }

    # extracts the st source specific standard values from the
    # standard_parameters dataset
    param, keys = read_standard_parameters("timeseries_source", "3_sources",
                                           "source_type", standard_parameters)
    for i in range(len(keys)):
        source_dict[keys[i]] = param[keys[i]]

    return append_component(sheets, "sources", source_dict)


def create_competition_constraint(limit: float, label: str, roof_num: str,
                                  sheets: dict,
                                  standard_parameters: pandas.ExcelFile):
    """
        TODO DOCSTRINGTEXT
        :param limit: max available roof area which can rather be used \
            for photovoltaic or solar thermal sources
        :type limit: float
        :param label: building label
        :type label: str
        :param roof_num: roof part id
        :type roof_num: str
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
    """
    from program_files import append_component, read_standard_parameters

    # import the photovoltaic and solar thermal standard parameters
    pv_param, pv_keys = read_standard_parameters(
        "fixed photovoltaic source", "3_sources", "source_type",
        standard_parameters)
    
    st_param, st_keys = read_standard_parameters(
        "solar_thermal_collector", "3_sources", "source_type",
        standard_parameters)
    
    # define individual values
    constraint_dict = {
        "component 1": label + "_" + str(roof_num) + "_pv_source",
        "factor 1": 1 / pv_param["Capacity per Area (kW/m2)"],
        "component 2": label + "_" + str(roof_num) + "_solarthermal_source",
        "factor 2": 1 / st_param["Capacity per Area (kW/m2)"],
        "limit": limit,
        "active": 1,
    }

    return append_component(sheets, "competition constraints", constraint_dict)


def create_sources(building: dict, clustering: bool, sheets: dict,
                   standard_parameters: pandas.ExcelFile,
                   st_output=None, central=False):
    """
        Algorithm which creates a photovoltaic- and  a solar thermal \
        source as well as the resulting competition constraint for a \
        roof part under consideration
        
        :param building: dictionary containing the building specific \
            parameters
        :type building: dict
        :param clustering: boolean which definies rather the resulting \
            energy system is spatially clustered or not
        :type clustering: bool
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        :param st_output: str containing the solar thermal output bus \
            which is used for the connection to district heating systems
        :type st_output: str
        :param central: parameter which definies rather the source is a\
            central source (True) or a decentral one (False)
        :type central: bool
    """
    from program_files.urban_district_upscaling.pre_processing \
        import column_exists, represents_int
    # create pv-sources and solar thermal-sources including area
    # competition
    roof_num = 1
    while column_exists(building, str("roof area %1d" % roof_num)):
        if building[str("roof area %1d" % roof_num)]:
            pv = building["pv {}".format(roof_num)] not in ["No", "no", "0"]
            st = building["st {}".format(roof_num)] not in ["No", "no", "0"]
            
            if pv:
                pv_column = building["pv {}".format(roof_num)]
                # if the user inserted an entry deviating yes in the pv
                # column it has to be the min invest value
                min_invest = pv_column if represents_int(pv_column) else "0"
                
                sheets = create_source(
                    source_type="fixed photovoltaic source",
                    roof_num=str(roof_num),
                    building=building,
                    sheets=sheets,
                    standard_parameters=standard_parameters,
                    min_invest=min_invest
                )
    
            if building["building type"] not in ["0", 0] and st:
                st_column = building["st {}".format(roof_num)]
                # if the user inserted an entry deviating yes in the pv
                # column it has to be the min invest value
                min_invest = st_column if represents_int(st_column) else "0"
                
                sheets = create_source(
                    source_type="solar_thermal_collector",
                    roof_num=str(roof_num),
                    building=building,
                    sheets=sheets,
                    st_output=st_output,
                    standard_parameters=standard_parameters,
                    central=central,
                    min_invest=min_invest
                )
    
                if not clustering and pv and st:
                    sheets = create_competition_constraint(
                        roof_num=str(roof_num),
                        label=building["label"],
                        sheets=sheets,
                        limit=building["roof area %1d" % roof_num],
                        standard_parameters=standard_parameters
                    )
    
        roof_num += 1
    return sheets


def cluster_sources_information(source: pandas.Series, source_param: dict,
                                azimuth_type: str, sheets: dict):
    """
        Collects the source information of the selected type, and
        inserts it into the dict containing the cluster specific
        sources data.

        :param source: Dataframe containing the source under \
            investigation
        :type source: pandas.Series
        :param source_param: dictionary containing the cluster summed \
            source information
        :type source_param: dict
        :param azimuth_type: defines the celestial direction of the \
            source to be clustered
        :type azimuth_type: str
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict


        :return: - **source_param** (dict) - dict extended by a new \
            entry
    """
    source_type = "pv" if source["technology"] == "photovoltaic" else "st"
    param_dict = {
        0: 1,
        1: source["max. investment capacity"],
        2: source["periodical costs"],
        3: source["periodical constraint costs"],
        4: source["variable costs"],
        5: source["Albedo"],
        6: source["Altitude"],
        7: source["Azimuth"],
        8: source["Surface Tilt"],
        9: source["Latitude"],
        10: source["Longitude"],
        11: source["Temperature Inlet"]
    }
    for num in param_dict:
        source_param[source_type + "_{}".format(azimuth_type)][num] \
            += param_dict[num]
    # remove the considered source from sources sheet
    sheets["sources"] = sheets["sources"].drop(index=source["label"])
    # return the modified source_param dict to the sources clustering
    # method
    return source_param, sheets


def sources_clustering(source_param: dict, building: list,
                       sheets: dict, sheets_clustering: dict):
    """
        In this method, the information of the photovoltaic and solar
        thermal systems to be clustered is collected, and the systems
        whose information has been collected are deleted.
        
        :param source_param: dictionary containing the cluster summed \
            source information
        :type source_param: dict
        :param building: list containing the building label [0], the \
            building's parcel ID [1] and the building type [2]
        :type building: list
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param sheets_clustering: copy of the scenario created within \
            the pre_processing.py
        :type sheets_clustering: dict

        :return: - **source_param** (dict) - containing the cluster \
            summed source information attached within this method
    """
    for index, source in sheets_clustering["sources"].iterrows():
        # collecting information for bundled photovoltaic systems
        if source["technology"] in [
                "photovoltaic", "solar_thermal_flat_plate"]:
            # check the azimuth type for clustering in 8 cardinal
            # directions
            dir_dict = {
                "south_west": [-157.5, -112.5],
                "west": [-112.5, -67.5],
                "north_west": [-67.5, -22.5],
                "north": [-22.5, 22.5],
                "north_east": [22.5, 67.5],
                "east": [67.5, 112.5],
                "south_east": [112.5, 157.5],
            }
            azimuth_type = None
            for dire in dir_dict:
                if dir_dict[dire][0] <= source["Azimuth"] < dir_dict[dire][1]:
                    azimuth_type = dire

            azimuth_type = "south" if azimuth_type is None else azimuth_type
            # Sources clustering - collecting the sources
            # information for each cluster
            if (
                str(building[0]) in source["label"]
                and source["label"] in sheets["sources"].index
            ):
                source_param, sheets = cluster_sources_information(
                    source=source,
                    source_param=source_param,
                    azimuth_type=azimuth_type,
                    sheets=sheets
                )

    # return the collected data to the main clustering method
    return source_param, sheets


def create_cluster_sources(source_param: dict, cluster: str, sheets: dict,
                           standard_parameters: pandas.ExcelFile):
    """
        This method is used to create the clustered sources, which \
        are divided into 8 cardinal directions with averaged parameters.
        
        :param source_param: dictionary containing the cluster summed \
                source information
        :type source_param: dict
        :param cluster: Cluster id
        :type cluster: str
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
    """
    from program_files import read_standard_parameters
    from program_files.urban_district_upscaling.components import Bus

    # Define PV Standard-Parameters
    pv_standard_param, pv_standard_keys = read_standard_parameters(
        name="fixed photovoltaic source",
        param_type="3_sources",
        index="source_type",
        standard_parameters=standard_parameters)
    st_standard_param, st_standard_keys = read_standard_parameters(
        name="solar_thermal_collector",
        param_type="3_sources",
        index="source_type",
        standard_parameters=standard_parameters)
    
    bus_created = False
    for azimuth in [
        "north_000",
        "north_east_045",
        "east_090",
        "south_east_135",
        "south_180",
        "south_west_225",
        "west_270",
        "north_west_315",
    ]:
        for pv_st in ["pv", "st"]:
            # if the counter for the considered cardinal orientation is
            # not 0
            if source_param[pv_st + "_{}".format(azimuth[:-4])][0] > 0:
                # type dependent parameter
                type_param = {
                    "pv": [pv_standard_param, "fixed photovoltaic source"],
                    "st": [st_standard_param, "solar_thermal_collector"],
                }
                param_dict = {
                    "label": cluster,
                    "azimuth {}".format(azimuth[:-4]): int(azimuth[-3:]),
                    "roof area {}".format(azimuth[:-4]):
                        source_param[pv_st + "_{}".format(azimuth[:-4])][1]
                        / type_param.get(pv_st)[0]["Capacity per Area (kW/m2)"]
                }

                if not bus_created and pv_st == "pv":
                    sheets = Bus.create_standard_parameter_bus(
                        label=str(cluster) + "_pv_bus",
                        bus_type="building_pv_bus",
                        sheets=sheets,
                        standard_parameters=standard_parameters
                    )
                    bus_created = True
                if pv_st == "pv" \
                        and source_param["st_{}".format(azimuth[:-4])][0] > 0:
                    sheets = create_competition_constraint(
                        limit=param_dict["roof area {}".format(azimuth[:-4])],
                        label=cluster,
                        roof_num=azimuth[:-4],
                        sheets=sheets,
                        standard_parameters=standard_parameters
                    )
                    
                # dict defining param location in sources information list
                pos_dict = {
                    "surface tilt {}".format(azimuth[:-4]): 8,
                    "latitude": 9,
                    "longitude": 10,
                    "flow temperature": 11
                }
                for i in pos_dict:
                    param = source_param[pv_st + "_{}".format(azimuth[:-4])]
                    param_dict.update({i: param[pos_dict[i]] / param[0]})

                sheets = create_source(
                    source_type=type_param.get(pv_st)[1],
                    roof_num=azimuth[:-4],
                    building=param_dict,
                    sheets=sheets,
                    standard_parameters=standard_parameters)
    return sheets


def update_sources_in_output(building, sheets_clustering, cluster, sheets):
    """ """
    # change sources output bus
    for i, j in sheets_clustering["sources"].iterrows():
        heat_elec = {
            "heat": ["output", "_heat_bus"],
            "elec": ["input", "_electricity_bus"],
        }
        for k in heat_elec:
            if building[0] in str(j[heat_elec[k][0]]) and k in str(j[heat_elec[k][0]]):
                sheets["sources"][heat_elec[k][0]] = sheets["sources"][
                    heat_elec[k][0]
                ].replace(
                    [str(building[0]) + heat_elec[k][1], str(cluster) + heat_elec[k][1]]
                )
    return sheets
