from program_files.postprocessing.plotting import get_pv_st_dir


def create_source(source_type, roof_num, building):
    """
            TODO DOCSTRINGTEXT
            :param building_id: building label
            :type building_id: str
            :param plant_id: roof part number
            :type plant_id: str
            :param azimuth: azimuth of given roof part
            :type azimuth: float
            :param tilt: tilt of given roof part
            :type tilt: float
            :param area: area of the given roof part
            :type area: float
            :param latitude: geographic latitude of the building
            :type latitude: float
            :param longitude: geographic longitude of the building
            :type longitude: float
        """
    from program_files.urban_district_upscaling.pre_processing \
        import append_component, read_standard_parameters
    source_param = [str(roof_num),
                    building["label"],
                    building['azimuth (°) %1d' % roof_num],
                    building['surface tilt (°) %1d' % roof_num],
                    building['latitude'],
                    building['longitude'],
                    building['roof area (m²) %1d' % roof_num]]
    switch_dict = {
        "fixed photovoltaic source":
            ['_pv_source', '_pv_bus', 0],
        "solar_thermal_collector":
            ['_solarthermal_source', '_heat_bus',
             str(source_param[1]) + '_electricity_bus']}

    # technical parameters
    source_dict = \
        {'label': str(source_param[1]) + '_' + str(source_param[0])
            + switch_dict.get(source_type)[0],
         'existing capacity': 0,
         'min. investment capacity': 0,
         'output': str(source_param[1]) + switch_dict.get(source_type)[1],
         'Azimuth': source_param[2],
         'Surface Tilt': source_param[3],
         'Latitude': source_param[4],
         'Longitude': source_param[5],
         'input': switch_dict.get(source_type)[2]}
    
    # extracts the st source specific standard values from the
    # standard_parameters dataset
    param, keys = read_standard_parameters(source_type, "sources", "comment")
    for i in range(len(keys)):
        source_dict[keys[i]] = param[keys[i]]
    
    source_dict['max. investment capacity'] = \
        param['Capacity per Area (kW/m2)'] * source_param[6]
    
    append_component("sources", source_dict)
    
    
def create_competition_constraint(limit, building_id, roof_num):
    """
        TODO DOCSTRINGTEXT
        :param component1: label of the first component in competition
        :type component1: str
        :param component2: label of the second component in competition
        :type component2: str
        :param limit:
        :type limit: float
    """
    from program_files.urban_district_upscaling.pre_processing \
        import append_component, read_standard_parameters
    pv_param, pv_keys = read_standard_parameters(
            'fixed photovoltaic source', "sources", "comment")
    st_param, st_keys = read_standard_parameters(
            'solar_thermal_collector', "sources", "comment")
    # define individual values
    constraint_dict = {
        'component 1': str(building_id) + '_' + str(roof_num) + '_pv_source',
        'factor 1': 1 / pv_param['Capacity per Area (kW/m2)'],
        'component 2': str(building_id) + '_' + str(roof_num)
                       + '_solarthermal_source',
        'factor 2': 1 / st_param['Capacity per Area (kW/m2)'],
        'limit': limit, 'active': 1}
    
    append_component("competition constraints", constraint_dict)


def create_sources(building, clustering):
    """
    
    """
    # create pv-sources and solar thermal-sources including area
    # competition
    roof_num = 0
    while building['roof area (m²) %1d' % roof_num]:
        column = 'st or pv %1d' % roof_num
        if building[column] == "pv&st":
            create_source(source_type="fixed photovoltaic source",
                          roof_num=roof_num, building=building)
            if not clustering and building["building type"] not in ["0", 0]:
                create_competition_constraint(
                    roof_num=roof_num, building_id=building["label"],
                    limit=building['roof area (m²) %1d' % roof_num])
                
        if building["building type"] not in ["0", 0]:
            create_source(source_type="solar_thermal_collector",
                          roof_num=roof_num, building=building)

        roof_num += 1


def cluster_sources_information(source, source_param, azimuth_type, type):
    """
        Collects the source information of the selected type, and
        inserts it into the dict containing the cluster specific
        sources data.

        :param source: Dataframe containing the source under \
            investigation
        :type source: pd.DataFrame
        :param source_param: dictionary containing the cluster summed \
            source information
        :type source_param: dict
        :param azimuth_type: definies the celestial direction of the \
            source to be clustered
        :type azimuth_type: str
        :param type: source type needed to define the dict entry \
            to be modified
        :type type: str

        :return: - **source_param** (dict) - dict extended by a new \
            entry
    """
    # counter
    source_param[type + "_{}".format(azimuth_type)][0] += 1
    # maxinvest
    source_param[type + "_{}".format(azimuth_type)][1] \
        += source["max. investment capacity"]
    # periodical_costs
    source_param[type + "_{}".format(azimuth_type)][2] \
        += source["periodical costs"]
    # periodical constraint costs
    source_param[type + "_{}".format(azimuth_type)][3] \
        += source["periodical constraint costs"]
    # variable costs
    source_param[type + "_{}".format(azimuth_type)][4] \
        += source["variable costs"]
    # albedo
    source_param[type + "_{}".format(azimuth_type)][5] += source["Albedo"]
    # altitude
    source_param[type + "_{}".format(azimuth_type)][6] += source["Altitude"]
    # azimuth
    source_param[type + "_{}".format(azimuth_type)][7] += source["Azimuth"]
    # surface tilt
    source_param[type + "_{}".format(azimuth_type)][8] \
        += source["Surface Tilt"]
    # latitude
    source_param[type + "_{}".format(azimuth_type)][9] += source["Latitude"]
    # longitude
    source_param[type + "_{}".format(azimuth_type)][10] += source["Longitude"]
    # remove the considered source from sources sheet
    sheets["sources"] = sheets["sources"].drop(index=source["label"])
    # return the modified source_param dict to the sources clustering
    # method
    return source_param


def sources_clustering(source_param, building, sheets_clustering):
    """
        In this method, the information of the photovoltaic and solar
        thermal systems to be clustered is collected, and the systems
        whose information has been collected are deleted.
        :param source_param: dictionary containing the cluster summed \
            source information
        :type source_param: dict
        :param building: DataFrame containing the building row from the\
            pre scenario sheet
        :type building: pd.Dataframe
        :param sheets_clustering: copy of the scenario created within \
            the pre_processing.py
        :type sheets_clustering: pd.DataFrame

        :return: - **source_param** (dict) - containing the cluster \
            summed source information attached within this method
    """
    for index, sources in sheets_clustering["sources"].iterrows():
        # collecting information for bundled photovoltaic systems
        if sources["technology"] in ["photovoltaic",
                                     "solar_thermal_flat_plate"]:
            # check the azimuth type for clustering in 8 cardinal
            # directions
            dir_dict = {"south_west": [-157.5, -112.5],
                        "west": [-112.5, -67.5],
                        "north_west": [-67.5, -22.5],
                        "north": [-22.5, 22.5],
                        "north_east": [22.5, 67.5],
                        "east": [67.5, 112.5],
                        "south_east": [112.5, 157.5]}
            azimuth_type = None
            for dire in dir_dict:
                if not dir_dict[dire][0] <= sources["Azimuth"] \
                       < dir_dict[dire][1]:
                    pass
                else:
                    azimuth_type = dire
            azimuth_type = "south" if azimuth_type is None else azimuth_type
            # Photovoltaic clustering - collecting the sources
            # information for each cluster
            if str(building[0]) in sources["label"] \
                    and sources["technology"] == "photovoltaic" \
                    and sources["label"] in sheets["sources"].index:
                source_param = \
                    cluster_sources_information(sources, source_param,
                                                azimuth_type, "pv")
            # Solar thermal clustering - collecting the sources
            # information for each cluster
            if str(building[0]) in sources["label"] \
                    and sources["technology"] == \
                    "solar_thermal_flat_plate" \
                    and sources["label"] in sheets["sources"].index:
                source_param = \
                    cluster_sources_information(sources, source_param,
                                                azimuth_type, "st")
    # return the collected data to the main clustering method
    return source_param


def create_cluster_sources(standard_param, source_param, cluster):
    """

    :param standard_param:
    :param source_param:
    :param cluster:
    :return:
    """
    # Define PV Standard-Parameters
    pv_standard_param, pv_standard_keys = \
        pre_processing.read_standard_parameters(standard_param,
                                                "fixed photovoltaic source",
                                                "sources", "comment")
    st_standard_param, st_standard_keys = \
        pre_processing.read_standard_parameters(standard_param,
                                                "solar_thermal_collector",
                                                "sources", "comment")
    
    for azimuth in ["north_000", "north_east_045", "east_090",
                    "south_east_135", "south_180",
                    "south_west_225", "west_270", "north_west_315"]:
        # Photovoltaic
        if source_param["pv_{}".format(azimuth[:-4])][0] > 0:
            if (str(cluster) + "_pv_bus") not in sheets["buses"].index:
                pre_processing.create_standard_parameter_bus(
                        label=str(cluster) + "_pv_bus",
                        bus_type='building_pv_bus',
                        standard_parameters=standard_param)
                sheets["buses"].set_index("label", inplace=True,
                                          drop=False)
            pre_processing.create_pv_source(
                    building_id=cluster,
                    plant_id=azimuth[:-4],
                    # calculate area from peak power
                    area=source_param["pv_{}".format(azimuth[:-4])][1] \
                         / pv_standard_param["Capacity per Area (kW/m2)"],
                    # calculate mean tilt
                    tilt=source_param["pv_{}".format(azimuth[:-4])][8] \
                         / source_param["pv_{}".format(azimuth[:-4])][0],
                    # extract azimuth from azimuth type
                    azimuth=int(azimuth[-3:]),
                    # calculate mean latitude
                    latitude=source_param["pv_{}".format(azimuth[:-4])][9] \
                             / source_param["pv_{}".format(azimuth[:-4])][0],
                    # calculate mean longitude
                    longitude=source_param["pv_{}".format(azimuth[:-4])][10] \
                              / source_param["pv_{}".format(azimuth[:-4])][0],
                    pv_standard_parameters=pv_standard_param)
        
        # Solar Thermal
        if source_param["st_{}".format(azimuth[:-4])][0] > 0:
            pre_processing.create_solarthermal_source(
                    building_id=cluster,
                    plant_id=azimuth[:-4],
                    # extract azimuth from azimuth type
                    azimuth=int(azimuth[-3:]),
                    # calculate mean tilt
                    tilt=source_param["st_{}".format(azimuth[:-4])][8] \
                         / source_param["st_{}".format(azimuth[:-4])][0],
                    # calculate area from peak power
                    area=source_param["st_{}".format(azimuth[:-4])][1] \
                         / st_standard_param["Capacity per Area (kW/m2)"],
                    solarthermal_standard_parameters=st_standard_param,
                    # calculate mean latitude
                    latitude=source_param["st_{}".format(azimuth[:-4])][9] \
                             / source_param["st_{}".format(azimuth[:-4])][0],
                    # calculate mean longitude
                    longitude=source_param["st_{}".format(azimuth[:-4])][10] \
                              / source_param["st_{}".format(azimuth[:-4])][
                                  0], )
            # Create new competition constraint
            if source_param["pv_{}".format(azimuth[:-4])][0] > 0:
                # calculate area from peak power
                area_st = (source_param["st_{}".format(azimuth[:-4])][1]
                           / st_standard_param['Capacity per Area (kW/m2)'])
                # calculate area from peak power
                area_pv = (source_param["pv_{}".format(azimuth[:-4])][1]
                           / pv_standard_param['Capacity per Area (kW/m2)'])
                
                pre_processing.create_competition_constraint(
                        component1=str(cluster) + "_" + azimuth[:-4]
                                   + "_solarthermal_source",
                        factor1=1 / st_standard_param[
                            'Capacity per Area (kW/m2)'],
                        component2=str(cluster) + "_" + azimuth[:-4]
                                   + "_pv_source",
                        factor2=1 / pv_standard_param[
                            "Capacity per Area (kW/m2)"],
                        limit=area_pv)
