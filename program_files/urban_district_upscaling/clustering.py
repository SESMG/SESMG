from program_files.urban_district_upscaling.components \
    import Link, Sink, Transformer, Storage, Bus, Source
    
    
def clustering_transformers(sink_parameters, transformer_parameters,
                            cluster, sheets, standard_parameters):
    """
    
    """
    total_heat_demand = \
        sink_parameters[4] + sink_parameters[5] + sink_parameters[6]
    for i in ["gasheating", "electric_heating", "ashp", "gchp"]:
        # create res or com gasheating
        if transformer_parameters[i][0] > 0 and total_heat_demand != 0:
            # create cluster gas bus with building type weighted
            # shortage costs
            if i == "gasheating":
                sheets = Bus.create_cluster_averaged_bus(
                        sink_parameters, cluster, "gas", sheets,
                        standard_parameters)
            elif (i == "ashp" or i == "gchp") \
                    and not str(cluster) + "_gchp_building_link" \
                    in sheets["links"].index:
                # create hp building type averaged price
                sheets = Bus.create_cluster_averaged_bus(
                        sink_parameters, cluster, "hp_elec", sheets,
                        standard_parameters)
                # electricity link from building electricity bus to hp
                # elec bus
                Link.create_link(
                        label=str(cluster) + "_gchp_building_link",
                        bus_1=str(cluster) + "_electricity_bus",
                        bus_2=str(cluster) + "_hp_elec_bus",
                        link_type="building_hp_elec_link")
            # create cluster's gasheating system
            Transformer.create_cluster_transformer(
                    i, transformer_parameters, cluster)
    
    return sheets
    
    
def create_cluster_heat_bus(transformer_parameters, clustering_dh, sheets,
                            sink_parameters, cluster):
    # create cluster heat bus if it consists rather the
    # opportunity for an investment in electricheating,
    # gasheating, ashp or gchp
    if transformer_parameters["electric_heating"][0] > 0 \
            or transformer_parameters["ashp"][0] > 0 \
            or transformer_parameters["gchp"][0] > 0 \
            or transformer_parameters["gasheating"][0] > 0:
        # cluster the district heating building buses
        lats = []
        lons = []
        if clustering_dh and len(sink_parameters[3]) > 0:
            for num, bus in sheets["buses"].iterrows():
                if bus["label"] == (sink_bus[1] for sink_bus
                                    in sink_parameters[3]):
                    lats.append(sheets["buses"].loc[num, "lat"])
                    lons.append(sheets["buses"].loc[num, "lon"])
                    sheets["buses"].loc[num, "district heating conn."] = 0
        if str(cluster) + "_heat_bus" not in sheets["buses"].index:
            # create cluster's heat bus
            Bus.create_standard_parameter_bus(
                label=str(cluster) + "_heat_bus",
                bus_type='building_heat_bus',
                dh="1" if len(lats) > 0 else "0",
                cords=[(sum(lats) / len(lats)) if len(lats) > 0 else 0,
                       (sum(lons) / len(lons)) if len(lons) > 0 else 0])
            sheets["buses"].set_index("label", inplace=True, drop=False)
    return sheets
    
    
def collect_clustering_information(building, sheets_clustering, sheets,
                                   heat_buses_gchps):
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
    # collect cluster intern source information
    source_param, sheets = Source.sources_clustering(
            source_param, building, sheets_clustering, sheets)
    
    # collect cluster intern transformer information
    heat_buses_gchps, transformer_parameters, sheets = \
        Transformer.transformer_clustering(
                building, sheets_clustering, transformer_parameters,
                heat_buses_gchps, sheets)
    
    # collect cluster intern storage information
    storage_parameters, sheets = \
        Storage.storage_clustering(
                building, sheets_clustering, storage_parameters,
                sheets)
    return source_param, heat_buses_gchps, transformer_parameters, \
        storage_parameters, sheets


def get_dict_building_cluster(tool):
    # create a dictionary holding the combination of cluster ID the included
    # building labels and its parcels
    cluster_ids = {}
    for num, building in tool.iterrows():
        if building["active"]:
            print(building["label"])
            building_info = [building['label'], building['parcel'],
                             str(building["building type"])[0:3]]
            # if cluster id already in dict
            if str(building["cluster_ID"]) in cluster_ids:
                cluster_ids[str(building["cluster_ID"])].append(building_info)
            # if cluster id not in dict
            else:
                cluster_ids.update({
                    str(building["cluster_ID"]): [building_info]})
    return cluster_ids

    
def clustering_method(tool, standard_parameters, sheet_names, sheets,
                      central_electricity_network, clustering_dh):
    """
        TODO DOCSTRING TEXT
        :param tool:
        :type tool: pd.Dataframe
        :param standard_parameters:
        :type standard_parameters:
        :param sheet_names:
        :type sheet_names:
        :param sheets:
        :type sheets:
        :param central_electricity_network:
        :type central_electricity_network:
        :param clustering_dh:
        :type clustering_dh:
    """
    cluster_ids = get_dict_building_cluster(tool)
                
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
        type_dict = {0: ["gas", "central"],
                     1: ["electricity", "central"],
                     2: ["hp_elec", "swhp_elec"]}
        for k in type_dict:
            if type_dict[k][0] in j["label"] \
                    and type_dict[k][1] not in j["label"]:
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
            transformer_parameters = None
            storage_parameters = None
            source_param = None
            for building in cluster_ids[cluster]:
                for index, sink in sheets_clustering["sinks"].iterrows():
                    # collecting information for sinks
                    sink_parameters = Sink.sink_clustering(building, sink,
                                                           sink_parameters)
                    
                # create cluster elec buses
                sheets = Bus.create_cluster_elec_buses(
                    building, cluster, sheets)

                source_param, heat_buses_gchps, transformer_parameters, \
                    storage_parameters, sheets = \
                    collect_clustering_information(building, sheets_clustering,
                                                   sheets, heat_buses_gchps)
                # restructre all links
                sheets = Link.restructuring_links(
                    sheets_clustering, building, cluster, sink_parameters,
                    sheets)
                
                # update the sources in and output
                sheets = Source.update_sources_in_output(
                    building, sheets_clustering, cluster, sheets)
                
            # TRANSFORMER
            # create cluster electricity sinks
            sheets = Sink.create_cluster_elec_sinks(
                standard_parameters, sink_parameters,
                cluster, central_electricity_network, sheets)
            
            sheets = clustering_transformers(
                sink_parameters, transformer_parameters, cluster, sheets,
                standard_parameters)

            # SOURCES
            # create cluster's sources and competition constraints
            Source.create_cluster_sources(standard_parameters, source_param,
                                          cluster)
            for i in ["battery", "thermal"]:
                # STORAGES
                if storage_parameters[i][0] > 0:
                    # create cluster's battery
                    Storage.create_cluster_storage(
                        i, cluster, storage_parameters)
                
            sheets = create_cluster_heat_bus(
                transformer_parameters, clustering_dh, sheets, sink_parameters,
                cluster)
            # if building and gchp parcel are in the same cluster create
            # a link between them
            for i in sink_parameters[3]:
                Link.create_link(
                    label=str(i[0]) + "_" + str(i[1]) + "_heat_building_link",
                    bus_1=str(cluster) + "_heat_bus",
                    bus_2=str(i[1]),
                    link_type="building_hp_elec_link")

    buses = sheets["buses"].copy()

    for i, j in buses.iterrows():
        if heat_buses_gchps:
            if str(j["label"][:9]) in heat_buses_gchps:
                sheets["buses"] = sheets["buses"].drop(index=j["label"])
