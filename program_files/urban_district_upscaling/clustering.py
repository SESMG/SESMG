from program_files.urban_district_upscaling.components import (
    Link,
    Sink,
    Transformer,
    Storage,
    Bus,
    Source,
)


def clustering_transformers(
    sheets, sink_parameters, transformer_parameters, cluster, standard_parameters
):
    """ """

    if (sink_parameters[4] + sink_parameters[5] + sink_parameters[6]) != 0:
        for i in ["gasheating", "electricheating", "ashp", "gchp"]:
            # create res or com gasheating
            if transformer_parameters[i][0] > 0:
                # create cluster gas bus with building type weighted
                # shortage costs
                if i == "gasheating":
                    sheets = Bus.create_cluster_averaged_bus(
                        sink_parameters, cluster, "gas", sheets, standard_parameters
                    )
                elif (i == "ashp" or i == "gchp") and str(
                    cluster
                ) + "_gchp_building_link" not in list(sheets["links"]["label"]):
                    # create hp building type averaged price
                    sheets = Bus.create_cluster_averaged_bus(
                        sink_parameters, cluster, "hp_elec", sheets, standard_parameters
                    )
                    # electricity link from building electricity bus to hp
                    # elec bus
                    sheets = Link.create_link(
                        label=str(cluster) + "_gchp_building_link",
                        bus_1=str(cluster) + "_electricity_bus",
                        bus_2=str(cluster) + "_hp_elec_bus",
                        link_type="building_hp_elec_link",
                        sheets=sheets,
                    )
                # create cluster's gasheating system
                sheets = Transformer.create_cluster_transformer(
                    i, transformer_parameters, cluster, sheets
                )
    return sheets


def create_cluster_heat_bus(
    transformer_parameters, clustering_dh, sink_parameters, cluster, sheets
):
    # create cluster heat bus if it consists rather the
    # opportunity for an investment in electricheating,
    # gasheating, ashp or gchp
    if (
        transformer_parameters["electricheating"][0] > 0
        or transformer_parameters["ashp"][0] > 0
        or transformer_parameters["gchp"][0] > 0
        or transformer_parameters["gasheating"][0] > 0
    ):
        # cluster the district heating building buses
        lats = []
        lons = []
        if clustering_dh and len(sink_parameters[3]) > 0:
            for num, bus in sheets["buses"].iterrows():
                for sink_bus in sink_parameters[3]:
                    if bus["label"] == sink_bus[1]:
                        lats.append(sheets["buses"].loc[num, "lat"])
                        lons.append(sheets["buses"].loc[num, "lon"])
                        sheets["buses"].loc[num, "district heating conn."] = 0
        if str(cluster) + "_heat_bus" not in sheets["buses"]["label"]:
            # create cluster's heat bus
            sheets = Bus.create_standard_parameter_bus(
                label=str(cluster) + "_heat_bus",
                bus_type="building_heat_bus",
                sheets=sheets,
                cords=[
                    (sum(lats) / len(lats)) if len(lats) > 0 else 0,
                    (sum(lons) / len(lons)) if len(lons) > 0 else 0,
                    "1" if len(lats) > 0 else "0",
                ],
            )
            sheets["buses"].set_index("label", inplace=True, drop=False)
    return sheets


def collect_clustering_information(
    building,
    heat_buses_gchps,
    sheets,
    source_param,
    storage_parameters,
    transformer_parameters,
):

    # collect cluster intern source information
    source_param, sheets = Source.sources_clustering(
        source_param=source_param,
        building=building,
        sheets=sheets,
        sheets_clustering=sheets_clustering,
    )

    # collect cluster intern transformer information
    (
        heat_buses_gchps,
        transformer_parameters,
        sheets,
    ) = Transformer.transformer_clustering(
        building=building,
        sheets_clustering=sheets_clustering,
        transf_param=transformer_parameters,
        sheets=sheets,
        heat_buses_gchps=heat_buses_gchps,
    )

    # collect cluster intern storage information
    storage_parameters, sheets = Storage.storage_clustering(
        building=building,
        sheets_clustering=sheets_clustering,
        storage_parameter=storage_parameters,
        sheets=sheets,
    )

    return (
        source_param,
        heat_buses_gchps,
        transformer_parameters,
        storage_parameters,
        sheets,
    )


def remove_buses(sheets):
    """
        remove not longer used buses
            1. building specific gas bus
            2. building specific electricity bus
            3. building specific heat pump electricity bus
            4. building specific pv bus
        :param sheets: dictionary containing the pandas DataFrames \
            containing the energy system's data
        :type sheets: dict
        :return: - **sheets**(dict) - updated dictionary without the \
            not used buses
    """
    sheets["buses"].set_index("label", inplace=True, drop=False)
    for i, j in sheets_clustering["buses"].iterrows():
        type_dict = {
            0: ["gas", "central"],
            1: ["electricity", "central"],
            2: ["hp_elec", "swhp_elec"],
            3: ["pv_bus", "~"],
        }
        for k in type_dict:
            if type_dict[k][0] in j["label"] and type_dict[k][1] not in j["label"]:
                sheets["buses"] = sheets["buses"].drop(index=j["label"])
    return sheets


def get_dict_building_cluster(tool):
    # create a dictionary holding the combination of cluster ID the included
    # building labels and its parcels
    cluster_ids = {}
    for num, building in tool[tool["active"] == 1].iterrows():
        building_info = [
            building["label"],
            building["parcel"],
            str(building["building type"])[0:3],
        ]
        # if cluster id already in dict
        if str(building["cluster_ID"]) in cluster_ids:
            cluster_ids[str(building["cluster_ID"])].append(building_info)
        # if cluster id not in dict
        else:
            cluster_ids.update({str(building["cluster_ID"]): [building_info]})
    return cluster_ids


def collect_builing_information(cluster_ids, cluster, sheets, heat_buses_gchps):
    # cluster sinks parameter
    # [res_elec_demand, com_elec_demand, ind_elec_demand,
    #  heat_buses, res_heat_demand, com_heat_demand,
    #  ind_heat_demand, heat_sinks, elec_res_sink,
    #  elec_com_sink, elec_ind_sink]
    sink_parameters = [0, 0, 0, [], 0, 0, 0, [], [], [], []]
    # transformer_param technology:
    # [counter, efficiency, efficiency2, periodical_costs,
    #  variable_constraint_costs]
    transformer_parameters = {
        "gasheating": [0, 0, "x", 0, 0],
        "electricheating": [0, 0, "x", 0, 0],
        "ashp": [0, 0, 0, 0, 0],
        "gchp": [0, 0, 0, 0, 0, 0],
    }
    # storage param technology:
    # [counter, maxinvest, periodical costs,
    #  periodical constraint costs, variable output costs]
    storage_parameters = {"battery": [0, 0, 0, 0, "x"], "thermal": [0, 0, 0, 0, 0]}

    # storage param technology: [counter, maxinvest, periodical costs,
    # periodical constraint costs, variable costs, Albedo,
    # Altitude, Azimuth, Surface Tilt, Latitude, Longitude]
    source_param = {
        "pv_north": [0] * 11,
        "pv_north_east": [0] * 11,
        "pv_east": [0] * 11,
        "pv_south_east": [0] * 11,
        "pv_south": [0] * 11,
        "pv_south_west": [0] * 11,
        "pv_west": [0] * 11,
        "pv_north_west": [0] * 11,
        "st_north": [0] * 11,
        "st_north_east": [0] * 11,
        "st_east": [0] * 11,
        "st_south_east": [0] * 11,
        "st_south": [0] * 11,
        "st_south_west": [0] * 11,
        "st_west": [0] * 11,
        "st_north_west": [0] * 11,
    }
    for building in cluster_ids:
        for index, sink in sheets_clustering["sinks"].iterrows():
            # collecting information for sinks
            sink_parameters = Sink.sink_clustering(building, sink, sink_parameters)

        # create cluster elec buses
        sheets = Bus.create_cluster_elec_buses(building, cluster, sheets)

        (
            source_param,
            heat_buses_gchps,
            transformer_parameters,
            storage_parameters,
            sheets,
        ) = collect_clustering_information(
            building,
            heat_buses_gchps,
            sheets,
            source_param,
            storage_parameters,
            transformer_parameters,
        )

        # restructure all links
        sheets = Link.restructuring_links(
            sheets_clustering, building, cluster, sink_parameters, sheets
        )

        # update the sources in and output
        sheets = Source.update_sources_in_output(
            building, sheets_clustering, cluster, sheets
        )

    return (
        sheets,
        sink_parameters,
        heat_buses_gchps,
        source_param,
        storage_parameters,
        transformer_parameters,
    )


def create_cluster_components(
    standard_parameters,
    sink_parameters,
    cluster,
    central_electricity_network,
    sheets,
    transformer_parameters,
    source_param,
    storage_parameters,
    clustering_dh,
):
    # TRANSFORMER
    # create cluster electricity sinks
    sheets = Sink.create_cluster_elec_sinks(
        standard_parameters,
        sink_parameters,
        cluster,
        central_electricity_network,
        sheets,
    )

    sheets = clustering_transformers(
        sheets, sink_parameters, transformer_parameters, cluster, standard_parameters
    )
    # SOURCES
    # create cluster's sources and competition constraints
    sheets = Source.create_cluster_sources(source_param, cluster, sheets)
    for i in ["battery", "thermal"]:
        # STORAGES
        if storage_parameters[i][0] > 0:
            # create cluster's battery
            sheets = Storage.create_cluster_storage(
                i, cluster, storage_parameters, sheets
            )

    sheets = create_cluster_heat_bus(
        transformer_parameters=transformer_parameters,
        cluster=cluster,
        clustering_dh=clustering_dh,
        sink_parameters=sink_parameters,
        sheets=sheets,
    )

    return sheets


def clustering_method(
    tool, standard_parameters, sheets, central_electricity_network, clustering_dh
):
    """
    TODO DOCSTRING TEXT
    :param tool:
    :type tool: pd.Dataframe
    :param standard_parameters:
    :type standard_parameters:
    :param sheets:
    :type sheets:
    :param central_electricity_network:
    :type central_electricity_network:
    :param clustering_dh:
    :type clustering_dh:
    """
    cluster_ids = get_dict_building_cluster(tool)
    global sheets_clustering
    sheets_clustering = {}
    # local copy of status of scenario components
    for sheet in list(sheets.keys()):
        sheet_edited = sheets[sheet].copy()
        sheet_edited.reset_index(drop=True, inplace=True)
        sheet_edited = sheet_edited.drop(index=0)
        sheets_clustering.update({sheet: sheet_edited})
    sheets = remove_buses(sheets)
    heat_buses_gchps = []
    print(sheets.keys())
    for cluster in cluster_ids:
        # reset all indizes to delete the right rows in pandas dataframe
        for sheet in ["transformers", "storages", "links", "sinks", "sources", "buses"]:
            if not sheets[sheet].empty:
                sheets[sheet].set_index("label", inplace=True, drop=False)

        if cluster_ids[cluster]:

            (
                sheets,
                sink_parameters,
                heat_buses_gchps,
                source_param,
                storage_parameters,
                transformer_parameters,
            ) = collect_builing_information(
                cluster_ids[cluster], cluster, sheets, heat_buses_gchps
            )

            sheets = create_cluster_components(
                standard_parameters,
                sink_parameters,
                cluster,
                central_electricity_network,
                sheets,
                transformer_parameters,
                source_param,
                storage_parameters,
                clustering_dh,
            )

            # if building and gchp parcel are in the same cluster create
            # a link between them
            for i in sink_parameters[3]:
                sheets = Link.create_link(
                    label=str(i[0]) + "_" + str(i[1]) + "_heat_building_link",
                    bus_1=str(cluster) + "_heat_bus",
                    bus_2=str(i[1]),
                    link_type="building_hp_elec_link",
                    sheets=sheets,
                )

    buses = sheets["buses"].copy()

    for i, j in buses.iterrows():
        if heat_buses_gchps:
            if str(j["label"][:9]) in heat_buses_gchps:
                sheets["buses"] = sheets["buses"].drop(index=j["label"])

    return sheets
