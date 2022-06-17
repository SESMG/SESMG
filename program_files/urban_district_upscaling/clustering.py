import program_files.urban_district_upscaling.pre_processing as pre_processing
from program_files.urban_district_upscaling.components import Link, Sink


def create_cluster_elec_buses(building, cluster):
    """
        Method creating the building type specific electricity buses and
        connecting them to the main cluster electricity bus
        
        :param building: Dataframe holding the building specific data \
            from prescenario file
        :type building: pd.Dataframe
        :param cluster: Cluster id
        :type cluster: str
    """
    # ELEC BUSES
    # get building type to specify bus type to be created
    if "RES" in building[2] \
            and str(cluster) + "_res_electricity_bus" \
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
        pre_processing.create_standard_parameter_bus(
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


def cluster_storage_information(storage, storage_parameter, type):
    """
        Collects the transformer information of the selected type, and
        inserts it into the dict containing the cluster specific
        transformer data.

        :param storage: Dataframe containing the storage under \
            investigation
        :type storage: pd.DataFrame
        :param storage_parameter: dictionary containing the cluster \
            summed storage information
        :type storage_parameter: dict
        :param type: storage type needed to define the dict entry \
            to be modified
        :type type: str

        :return:
    """
    # counter
    storage_parameter[type][0] += 1
    # max invest
    storage_parameter[type][1] += storage["max. investment capacity"]
    # periodical costs
    storage_parameter[type][2] += storage["periodical costs"]
    # periodical constraint costs
    storage_parameter[type][3] += storage["periodical constraint costs"]
    if type == "thermal":
        # variable output costs
        storage_parameter[type][4] += storage["variable output costs"]
    # remove the considered storage from transformer sheet
    sheets["storages"] = sheets["storages"].drop(index=storage["label"])
    # return the modified transf_param dict to the transformer clustering
    # method
    return storage_parameter


def storage_clustering(building, sheets_clustering, storage_parameter):
    """
        Main method to collect the information about the storage
        (battery, thermal storage), which are located in the considered
        cluster.

        :param building: DataFrame containing the building row from the\
            pre scenario sheet
        :type building: pd.Dataframe
        :param sheets_clustering:
        :type sheets_clustering: pd.DataFrame
        :param storage_parameter: dictionary containing the collected \
            storage information
        :type storage_parameter: dict

        :return:
    """
    for index, storage in sheets_clustering["storages"].iterrows():
        # collect battery information
        if str(building[0]) in storage["label"] \
                and "battery" in storage["label"] \
                and storage["label"] in sheets["storages"].index:
            storage_parameter = cluster_storage_information(storage,
                                                            storage_parameter,
                                                            "battery")
        # collect thermal storage information
        if str(building[0]) in storage["label"] \
                and "thermal" in storage["label"] \
                and storage["label"] in sheets["storages"].index:
            storage_parameter = cluster_storage_information(storage,
                                                            storage_parameter,
                                                            "thermal")
    # return the collected data to the main clustering method
    return storage_parameter


def restructuring_links(sheets_clustering, building, cluster,
                        standard_parameters, sink_parameters):
    # TODO comments
    for i, j in sheets_clustering["links"].iterrows():

        if j["label"] in sheets["links"].index:
            # remove heatpump links
            if str(building[0]) in j["bus2"] and "hp_elec" in j["bus2"]:
                sheets["links"] = sheets["links"].drop(index=j["label"])
            if str(building[1])[-9:] in j["bus2"] and "hp_elec" in j["bus2"] \
                    and j["label"] in sheets["links"].index:
                sheets["links"] = sheets["links"].drop(index=j["label"])
            # delete pvbus -> central elec
            if str(building[0]) in j["bus1"] and \
                    "central_electricity" in j["bus2"] and \
                    "pv_bus" in j["bus1"]:
                sheets["links"] = sheets["links"].drop(index=j["label"])
                if not (str(cluster) + "_pv_bus" in j["bus1"]
                        and "central_electricity" in j["bus2"]) \
                        and cluster + "pv_central_electricity_link" \
                        not in sheets["links"].index:
                    pre_processing.create_standard_parameter_link(
                        cluster + "pv_central_electricity_link",
                        bus_1=cluster + "_pv_bus",
                        bus_2="central_electricity_bus",
                        link_type="building_pv_central_link",
                        standard_parameters=standard_parameters)
                    if sink_parameters[0] + sink_parameters[1] + sink_parameters[2]:
                        pre_processing.create_standard_parameter_link(
                                cluster + "pv_electricity_link",
                                bus_1=cluster + "_pv_bus",
                                bus_2=cluster + "_electricity_bus",
                                link_type="building_pv_central_link",
                                standard_parameters=standard_parameters)
                    sheets["links"].set_index("label", inplace=True,
                                              drop=False)
            # delete pvbus ->  elec bus of building
            if str(building[0]) in j["bus1"] and \
                    str(building[0]) in j["bus2"] and \
                    "pv_bus" in j["bus1"]:
                sheets["links"] = sheets["links"].drop(
                    index=j["label"])

            if str(building[1][-9:]) in j["bus1"] and "heat" in j["bus1"]:
                sheets["links"] = sheets["links"].drop(index=j["label"])

            # connecting the clusters to the central gas bus
            if str(building[0]) in j["label"]:
                if "central_naturalgas" in j["bus1"] and \
                        "_gas_bus" in j["bus2"]:
                    sheets["links"] = sheets["links"].drop(index=j["label"])

                    if "central_naturalgas" + cluster \
                            not in sheets["links"].index:
                        pre_processing.create_standard_parameter_link(
                            "central_naturalgas" + cluster,
                            bus_1="central_naturalgas_bus",
                            bus_2=cluster + "_gas_bus",
                            link_type="central_naturalgas_building_link",
                            standard_parameters=standard_parameters)
                        sheets["links"].set_index("label", inplace=True,
                                                  drop=False)
        if str(building[0]) in j["bus2"] and "electricity" in j["bus2"]:
            sheets["links"]['bus2'] = \
                sheets["links"]['bus2'].replace(
                    [str(building[0]) + "_electricity_bus"],
                    str(cluster) + "_electricity_bus")
        # delete and replace central elec -> building elec
        if str(building[0]) in j["bus2"] and \
                "central_electricity" in j["bus1"] and \
                "electricity_bus" in j["bus2"]:
            sheets["links"] = sheets["links"].drop(index=j["label"])

        if str(building[0]) in j["bus2"] and \
                "gas" in j["bus2"]:
            sheets["links"]['bus2'] = \
                sheets["links"]['bus2'].replace(
                    [str(building[0]) + "_gas_bus"],
                    str(cluster) + "_gas_bus")
            
            
def update_sources_in_output(building, sheets_clustering, cluster):
    """
    
    """
    # change sources output bus
    for i, j in sheets_clustering["sources"].iterrows():
        if str(building[0]) in str(j["input"]) and \
                "electricity" in str(j["input"]):
            sheets["sources"]['input'] = \
                sheets["sources"]['input'].replace(
                        [str(building[0]) + "_electricity_bus"],
                        str(cluster) + "_electricity_bus")
        if str(building[0]) in str(j["output"]) and "heat" in str(j["output"]):
            sheets["sources"]["output"] = \
                sheets["sources"]["output"].replace(
                        [str(building[0]) + "_heat_bus"],
                        str(cluster) + "_heat_bus")
            

def create_cluster_elec_sinks(standard_parameters, sink_parameters, cluster,
                              central_electricity_network):
    """
        
        :return:
    """
    bus_parameters = \
        standard_parameters.parse('buses', index_col='bus_type')
    total_annual_elec_demand = (sink_parameters[0]
                                + sink_parameters[1]
                                + sink_parameters[2])
    if total_annual_elec_demand > 0:
        if cluster + "_electricity_bus" \
                not in sheets["buses"].index:
            pre_processing.create_standard_parameter_bus(
                    label=str(cluster) + "_electricity_bus",
                    bus_type='building_res_electricity_bus',
                    standard_parameters=standard_parameters)
            sheets["buses"].set_index("label", inplace=True,
                                      drop=False)
            sheets["buses"].loc[(str(cluster) + "_electricity_bus"),
                                "shortage costs"] = \
                ((sink_parameters[0]
                  / total_annual_elec_demand)
                 * bus_parameters.loc["building_res_electricity_bus"][
                     "shortage costs"]
                 + (sink_parameters[1] / total_annual_elec_demand)
                 * bus_parameters.loc["building_com_electricity_bus"][
                     "shortage costs"]
                 + (sink_parameters[2] / total_annual_elec_demand)
                 * bus_parameters.loc["building_ind_electricity_bus"][
                     "shortage costs"])
        if central_electricity_network:
            pre_processing.create_central_elec_bus_connection(
                    cluster, standard_parameters)
    
    # create clustered electricity sinks
    if sink_parameters[0] > 0:
        for i in sink_parameters[7]:
            sheets["sinks"].loc[sheets["sinks"]["label"] == i, "input"] \
                = str(cluster) + "_res_electricity_bus"
        # create clustered res electricity sink
        # annual demand sink_parameters[0]
        #pre_processing.create_standard_parameter_sink(
        #        "RES_electricity_sink",
        #        str(cluster) + "_res_electricity_demand",
        #        str(cluster) + "_res_electricity_bus",
        #        sink_parameters[0], standard_parameters)
    if sink_parameters[1] > 0:
        for i in sink_parameters[8]:
            sheets["sinks"].loc[sheets["sinks"]["label"] == i, "input"] \
                = str(cluster) + "_com_electricity_bus"
        # create clustered res electricity sink
        # annual demand sink_parameters[1]
        #pre_processing.create_standard_parameter_sink(
        #        "COM_electricity_sink",
        #        str(cluster) + "_com_electricity_demand",
        #        str(cluster) + "_com_electricity_bus",
        #        sink_parameters[1], standard_parameters)
    if sink_parameters[2] > 0:
        for i in sink_parameters[9]:
            sheets["sinks"].loc[sheets["sinks"]["label"] == i, "input"] \
                = str(cluster) + "_ind_electricity_bus"
        # create clustered res electricity sink
        # annual demand sink_parameters[2]
        #pre_processing.create_standard_parameter_sink(
        #        "IND_electricity_sink",
        #        str(cluster) + "_ind_electricity_demand",
        #        str(cluster) + "_ind_electricity_bus",
        #        sink_parameters[2], standard_parameters)
        

def create_cluster_averaged_bus(sink_parameters, cluster, type,
                                standard_parameters):
    """
    
    :param sink_parameters:
    :param cluster:
    :param type:
    :return:
    """
    bus_parameters = \
        standard_parameters.parse('buses', index_col='bus_type')
    if type != "gas":
        type1 = "hp_elec"
        type2 = "hp_electricity"
        type3 = "hp_electricity"
        type4 = "electricity"
    else:
        type1 = "gas"
        type2 = "res_gas"
        type3 = "com_gas"
        type4 = "gas"
    # calculate cluster's total heat demand
    total_annual_heat_demand = (sink_parameters[4]
                                + sink_parameters[5]
                                + sink_parameters[6])
    # create standard_parameter gas bus
    pre_processing.create_standard_parameter_bus(
            label=str(cluster) + "_" + type1 + "_bus",
            bus_type='building_' + type2 + '_bus',
            standard_parameters=standard_parameters)
    # reindex for further attachments
    sheets["buses"].set_index("label", inplace=True,
                              drop=False)
    # recalculate gas bus shortage costs building type weighted
    sheets["buses"].loc[(str(cluster) + "_" + type1 + "_bus"),
                        "shortage costs"] = \
        ((sink_parameters[4] / total_annual_heat_demand)
         * bus_parameters.loc["building_" + type2 + "_bus"][
             "shortage costs"]
         + (sink_parameters[5] / total_annual_heat_demand)
         * bus_parameters.loc["building_" + type3 + "_bus"][
             "shortage costs"]
         + (sink_parameters[6] / total_annual_heat_demand)
         * bus_parameters.loc["building_ind_" + type4 + "_bus"][
             "shortage costs"])
    




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
                / source_param["st_{}".format(azimuth[:-4])][0], )
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
                    factor1=1 / st_standard_param['Capacity per Area (kW/m2)'],
                    component2=str(cluster) + "_" + azimuth[:-4]
                    + "_pv_source",
                    factor2=1 / pv_standard_param["Capacity per Area (kW/m2)"],
                    limit=area_pv)
   
                
def create_cluster_storage(standard_parameters, type, cluster,
                           storage_parameters):
    """
    
    :param standard_parameters:
    :param type:
    :return:
    """
    if type == "battery":
        standard_param, standard_keys = \
            pre_processing.read_standard_parameters(
                    standard_parameters, "building_battery_storage",
                    "storages", "comment")
        param_dict = {'label': str(cluster) + '_battery_storage',
                      'comment': 'automatically_created',
                      'bus': str(cluster) + '_electricity_bus'}
    elif type == "thermal":
        standard_param, standard_keys = \
            pre_processing.read_standard_parameters(
                    standard_parameters, "building_thermal_storage",
                    "storages", "comment")
        param_dict = {'label': str(cluster) + '_thermal_storage',
                      'comment': 'automatically_created',
                      'bus': str(cluster) + '_heat_bus'}
    else:
        raise ValueError("chosen storage type in create cluster storage "
                         "not allowed")
        
    for i in range(len(standard_keys)):
        param_dict[standard_keys[i]] = \
            standard_param[standard_keys[i]]
    # max invest
    param_dict["max. investment capacity"] = storage_parameters[type][1]
    # periodical costs
    param_dict["periodical costs"] = storage_parameters[type][2] \
        / storage_parameters[type][0]
    # periodical constraint costs
    param_dict["periodical constraint costs"] = storage_parameters[type][3] \
        / storage_parameters[type][0]
    if type == "thermal":
        param_dict["variable output costs"] = storage_parameters[type][4] \
            / storage_parameters[type][0]
    # produce a pandas series out of the dict above due to easier
    # appending
    pre_processing.append_component("storages", param_dict)


def clustering_method(tool, standard_parameters, sheet_names, sheets_input,
                      central_electricity_network, clustering_dh):
    """
        TODO DOCSTRING TEXT
        :param tool:
        :type tool: pd.Dataframe
        :param standard_parameters:
        :type standard_parameters:
        :param sheet_names:
        :type sheet_names:
        :param sheets_input:
        :type sheets_input:
    """
    global sheets
    sheets = sheets_input
    # create a dictionary holding the combination of cluster ID the included
    # building labels and its parcels
    cluster_ids = {}
    for num, building in tool.iterrows():
        if building["active"]:
            print(building["label"])
            # if cluster id already in dict
            if str(building["cluster_ID"]) in cluster_ids:
                cluster_ids[str(building["cluster_ID"])].append(
                    [building['label'], building['parcel'],
                     str(building["building type"])[0:3]])
            # if cluster id not in dict
            else:
                cluster_ids.update({
                    str(building["cluster_ID"]):
                        [[building['label'], building['parcel'],
                          str(building["building type"])[0:3]]]})
                
    # local copy of status of scenario components
    sheets_clustering = {}
    for sheet in sheet_names:
        sheet_edited = sheets[sheet].copy()
        sheet_edited = sheet_edited.drop(index=0)
        sheets_clustering.update({sheet: sheet_edited})
        
    # remove not longer used buses
    # 1. building specific gas bus
    # 2. building specific electricity bus
    # 3. building specific heat pump electricity bus
    # 4. building specific pv bus
    for i, j in sheets_clustering["buses"].iterrows():
        if "gas" in j["label"] and "central" not in j["label"]:
            sheets["buses"] = sheets["buses"].drop(index=i)
        if "electricity" in j["label"] and "central" not in j["label"]:
            sheets["buses"] = sheets["buses"].drop(index=i)
        if "hp_elec" in j["label"] and "swhp_elec" not in j["label"]:
            sheets["buses"] = sheets["buses"].drop(index=i)
        if "pv_bus" in j["label"]:
            sheets["buses"] = sheets["buses"].drop(index=i)
            
    heat_buses_gchps = []
    for cluster in cluster_ids:
        # reset all indizes to delete the right rows in pandas dataframe
        for sheet in ["transformers", "storages", "links", "sinks", "sources",
                      "buses"]:
            sheets[sheet].set_index("label", inplace=True, drop=False)

        if cluster_ids[cluster]:
            # cluster sinks parameter
            # [res_elec_demand, com_elec_demand, ind_elec_demand,
            #  heat_buses, res_heat_demand, com_heat_demand,
            #  ind_heat_demand, heat_sinks, elec_res_sink,
            #  elec_com_sink, elec_ind_sink]
            sink_parameters = [0, 0, 0, [], 0, 0, 0, [], [], [], []]
            
            # transformer_param technology:
            # [counter, efficiency, efficiency2, periodical_costs,
            #  variable_constraint_costs]
            transformer_parameters = \
                {"gasheating": [0, 0, "x", 0, 0],
                 "electric_heating": [0, 0, "x", 0, 0],
                 "ashp": [0, 0, 0, 0, 0],
                 "gchp": [0, 0, 0, 0, 0, 0]}
            
            # storage param technology:
            # [counter, maxinvest, periodical costs,
            #  periodical constraint costs, variable output costs]
            storage_parameters = {"battery": [0, 0, 0, 0, "x"],
                                  "thermal": [0, 0, 0, 0, 0]}

            # storage param technology: [counter, maxinvest, periodical costs,
            # periodical constraint costs, variable costs, Albedo,
            # Altitude, Azimuth, Surface Tilt, Latitude, Longitude]
            source_param = {
                "pv_north": [0] * 11, "pv_north_east": [0] * 11,
                "pv_east": [0] * 11, "pv_south_east": [0] * 11,
                "pv_south": [0] * 11, "pv_south_west": [0] * 11,
                "pv_west": [0] * 11, "pv_north_west": [0] * 11,
                "st_north": [0] * 11, "st_north_east": [0] * 11,
                "st_east": [0] * 11, "st_south_east": [0] * 11,
                "st_south": [0] * 11, "st_south_west": [0] * 11,
                "st_west": [0] * 11, "st_north_west": [0] * 11}

            for building in cluster_ids[cluster]:
                for index, sink in sheets_clustering["sinks"].iterrows():
                    # collecting information for sinks
                    sink_parameters = Sink.sink_clustering(building, sink,
                                                           sink_parameters)
                    
                # create cluster elec buses
                create_cluster_elec_buses(building, cluster,
                                          standard_parameters)
                    
                # collect cluster intern source information
                source_param = sources_clustering(source_param, building,
                                                  sheets_clustering)
                
                # collect cluster intern transformer information
                heat_buses_gchps, transformer_parameters = \
                    transformer_clustering(building, sheets_clustering,
                                           transformer_parameters,
                                           heat_buses_gchps)
                
                # collect cluster intern storage information
                storage_parameters = \
                    storage_clustering(building, sheets_clustering,
                                       storage_parameters)
                # restructre all links
                restructuring_links(sheets_clustering, building, cluster,
                                    standard_parameters, sink_parameters)
                
                # update the sources in and output
                update_sources_in_output(building, sheets_clustering, cluster)
                
            # TRANSFORMER
            # create cluster electricity sinks
            create_cluster_elec_sinks(standard_parameters, sink_parameters,
                                      cluster, central_electricity_network)

            # create res or com gasheating
            if transformer_parameters["gasheating"][0] > 0 \
                    and (sink_parameters[4] + sink_parameters[5]
                         + sink_parameters[6]) != 0:
                # create cluster gas bus with building type weighted shortage
                # costs
                create_cluster_averaged_bus(sink_parameters, cluster, "gas",
                                            standard_parameters)
                # create cluster's gasheating system
                create_cluster_transformer("gasheating",
                                           transformer_parameters, cluster,
                                           standard_parameters)

            # create cluster's electric heating system
            if transformer_parameters["electric_heating"][0] > 0:
                create_cluster_transformer("electric_heating",
                                           transformer_parameters, cluster,
                                           standard_parameters)

            if transformer_parameters["ashp"][0] > 0 \
                    and (sink_parameters[4] + sink_parameters[5]
                         + sink_parameters[6]) != 0:
                # create hp building type averaged price
                create_cluster_averaged_bus(sink_parameters, cluster,
                                            "hp_elec", standard_parameters)
                # electricity link from building electricity bus to hp
                # elec bus
                pre_processing.create_standard_parameter_link(
                        label=str(cluster) + "_gchp_building_link",
                        bus_1=str(cluster) + "_electricity_bus",
                        bus_2=str(cluster) + "_hp_elec_bus",
                        link_type="building_hp_elec_link",
                        standard_parameters=standard_parameters)
                # create cluster's ashp
                create_cluster_transformer("ashp", transformer_parameters,
                                           cluster, standard_parameters)

            if transformer_parameters["gchp"][0] > 0 \
                    and (sink_parameters[4] + sink_parameters[5]
                         + sink_parameters[6]) != 0:
                if not transformer_parameters["ashp"][0] > 0:
                    create_cluster_averaged_bus(sink_parameters, cluster,
                                                "hp_elec", standard_parameters)
                # create cluster's gchp
                create_cluster_transformer("gchp", transformer_parameters,
                                           cluster, standard_parameters)
            # SOURCES
            # create cluster's sources and competition constraints
            create_cluster_sources(standard_parameters, source_param, cluster)
            # STORAGES
            if storage_parameters["battery"][0] > 0:
                # create cluster's battery
                create_cluster_storage(standard_parameters, "battery", cluster,
                                       storage_parameters)
            if storage_parameters["thermal"][0] > 0:
                # create cluster's thermal storage
                create_cluster_storage(standard_parameters, "thermal", cluster,
                                       storage_parameters)
                
            # create cluster heat bus if it consists rather the
            # opportunity for an investment in electricheating,
            # gasheating, ashp or gchp
            if transformer_parameters["electric_heating"][0] > 0 \
                    or transformer_parameters["ashp"][0] > 0 \
                    or transformer_parameters["gchp"][0] > 0\
                    or transformer_parameters["gasheating"][0] > 0:
                # cluster the district heating building buses
                lats = []
                lons = []
                if clustering_dh:
                    for num, bus in sheets["buses"].iterrows():
                        for sink_bus in sink_parameters[3]:
                            if len(sink_parameters[3]) > 0 \
                                  and bus["label"] == sink_bus[1]:
                                lats.append(sheets["buses"].loc[num, "lat"])
                                lons.append(sheets["buses"].loc[num, "lon"])
                                sheets["buses"].loc[
                                    num, "district heating conn."] = 0
                if str(cluster) + "_heat_bus" not in sheets["buses"].index:
                    # create cluster's heat bus
                    pre_processing.create_standard_parameter_bus(
                        label=str(cluster) + "_heat_bus",
                        bus_type='building_heat_bus',
                        dh=1 if len(lats) > 0 else 0,
                        lat=(sum(lats) / len(lats)) if len(lats) > 0 else 0,
                        lon=(sum(lons) / len(lons)) if len(lons) > 0 else 0,
                        standard_parameters=standard_parameters)
                    sheets["buses"].set_index("label", inplace=True,
                                              drop=False)
            # if building and gchp parcel are in the same cluster create
            # a link between them
            for i in sink_parameters[3]:
                pre_processing.create_standard_parameter_link(
                    label=str(i[0]) + "_" + str(i[1]) + "_heat_building_link",
                    bus_1=str(cluster) + "_heat_bus",
                    bus_2=str(i[1]),
                    link_type="building_hp_elec_link",
                    standard_parameters=standard_parameters)

    buses = sheets["buses"].copy()

    for i, j in buses.iterrows():
        if heat_buses_gchps:
            if str(j["label"][:9]) in heat_buses_gchps:
                sheets["buses"] = sheets["buses"].drop(index=j["label"])
