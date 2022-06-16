def create_pv_source(building_id, plant_id, azimuth, tilt, area,
                     standard_parameters, latitude, longitude):
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
    # technical parameters
    pv_dict = \
        {'label': str(building_id) + '_' + str(plant_id) + '_pv_source',
         'existing capacity': 0,
         'min. investment capacity': 0,
         'output': str(building_id) + '_pv_bus',
         'Azimuth': azimuth,
         'Surface Tilt': tilt,
         'Latitude': latitude,
         'Longitude': longitude,
         'input': 0}
    # extracts the pv source specific standard values from the
    # standard_parameters dataset
    pv_param, pv_keys = read_standard_parameters(
            standard_parameters, 'fixed photovoltaic source', "sources",
            "comment")
    for i in range(len(pv_keys)):
        pv_dict[pv_keys[i]] = pv_param[pv_keys[i]]

    pv_dict['max. investment capacity'] = \
        pv_param['Capacity per Area (kW/m2)'] * area

    # produce a pandas series out of the dict above due to easier appending
    append_component("sources", pv_dict)
    
    
def create_solarthermal_source(building_id, plant_id, azimuth, tilt, area,
                               standard_parameters, latitude,
                               longitude):
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
    # technical parameters
    st_dict = \
        {'label': (str(building_id) + '_' + str(plant_id)
                   + '_solarthermal_source'),
         'existing capacity': 0,
         'min. investment capacity': 0,
         'output': str(building_id) + '_heat_bus',
         'Azimuth': azimuth,
         'Surface Tilt': tilt,
         'Latitude': latitude,
         'Longitude': longitude,
         'input': str(building_id) + '_electricity_bus'}
    # extracts the st source specific standard values from the
    # standard_parameters dataset
    st_param, st_keys = read_standard_parameters(
            standard_parameters, 'solar_thermal_collector', "sources",
            "comment")
    for i in range(len(st_keys)):
        st_dict[st_keys[i]] = st_param[st_keys[i]]

    st_dict['max. investment capacity'] = \
        st_param['Capacity per Area (kW/m2)'] * area
    
    append_component("sources", st_dict)
    
    
def create_competition_constraint(component1, component2, limit,
                                  standard_parameters):
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
            standard_parameters, 'fixed photovoltaic source', "sources",
            "comment")
    st_param, st_keys = read_standard_parameters(
            standard_parameters, 'solar_thermal_collector', "sources",
            "comment")
    # define individual values
    constraint_dict = {'component 1': component1,
                       'factor 1': 1 / pv_param['Capacity per Area (kW/m2)'],
                       'component 2': component2,
                       'factor 2': 1 / st_param['Capacity per Area (kW/m2)'],
                       'limit': limit, 'active': 1}
    append_component("competition constraints", constraint_dict)


def create_sources(building, standard_parameters, clustering):
    """
    
    """
    # create pv-sources and solar thermal-sources including area
    # competition
    for roof_num in range(1, 29):
        if building['roof area (m²) %1d' % roof_num]:
            plant_id = str(roof_num)
            if building['st or pv %1d' % roof_num] == "pv&st":
                create_pv_source(
                        building_id=building['label'],
                        plant_id=plant_id,
                        azimuth=building['azimuth (°) %1d' % roof_num],
                        tilt=building['surface tilt (°) %1d' % roof_num],
                        area=building['roof area (m²) %1d' % roof_num],
                        latitude=building['latitude'],
                        longitude=building['longitude'],
                        standard_parameters=standard_parameters)
            if building['st or pv %1d' % roof_num] in ["st", "pv&st"] \
                    and building["building type"] not in ["0", 0]:
                create_solarthermal_source(
                        building_id=building['label'],
                        plant_id=plant_id,
                        azimuth=building['azimuth (°) %1d' % roof_num],
                        tilt=building['surface tilt (°) %1d' % roof_num],
                        area=building['roof area (m²) %1d' % roof_num],
                        latitude=building['latitude'],
                        longitude=building['longitude'],
                        standard_parameters=standard_parameters)
            if building['st or pv %1d' % roof_num] == "pv&st" \
                    and building["building type"] != "0" \
                    and not clustering:
                create_competition_constraint(
                    component1=(building['label'] + '_'
                                + plant_id + '_pv_source'),
                    component2=(building['label'] + '_' + plant_id
                                + '_solarthermal_source'),
                    limit=building['roof area (m²) %1d' % roof_num],
                    standard_parameters=standard_parameters)
