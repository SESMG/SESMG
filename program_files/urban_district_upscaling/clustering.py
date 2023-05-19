import pandas
from program_files.urban_district_upscaling.components import (
    Link,
    Sink,
    Transformer,
    Storage,
    Bus,
    Source,
)

true_bools = ["yes", "Yes", 1, "1"]


def clustering_transformers(
    sheets: dict,
    sink_parameters: list,
    transformer_parameters: dict,
    cluster: str,
    standard_parameters: pandas.ExcelFile,
) -> dict:
    """
        In this method the buses and links for the connection of the
        clustered transformers as well as the clustered transformers
        themselves are created and attached to the return data
        structure "sheets".
        
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param sink_parameters: list containing the cluster's sinks \
            parameter (4) res_heat_demand, (5)com_heat_demand, \
            (6) ind_heat_demand
        :type sink_parameters: list
        :param transformer_parameters: dict containing the cluster's \
            transformer parameters (index) technology each entry is a \
            list where index 0 is a counter
        :type transformer_parameters: list
        :param cluster: str containing the cluster's ID
        :type cluster: str
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    # check rather the cluster's heat demand is > 0
    if (sink_parameters[4] + sink_parameters[5] + sink_parameters[6]) != 0:
        for technology in ["gasheating", "electricheating", "ashp", "gchp"]:
            # create res or com gasheating
            if transformer_parameters[technology][0] > 0:
                # create cluster gas bus with building type weighted
                # shortage costs
                if technology == "gasheating":
                    sheets = Bus.create_cluster_averaged_bus(
                        sink_parameters=sink_parameters,
                        cluster=cluster,
                        fuel_type="gas",
                        sheets=sheets,
                        standard_parameters=standard_parameters,
                    )
                # create cluster hp electricity bus with building type \
                # weighted shortage costs
                elif technology in ["ashp", "gchp"] and str(
                    cluster
                ) + "_gchp_building_link" not in list(sheets["links"]["label"]):
                    # create hp building type averaged price
                    sheets = Bus.create_cluster_averaged_bus(
                        sink_parameters=sink_parameters,
                        cluster=cluster,
                        fuel_type="hp_elec",
                        sheets=sheets,
                        standard_parameters=standard_parameters,
                    )
                    # electricity link from building electricity bus to hp
                    # electricity bus
                    sheets = Link.create_link(
                        label=str(cluster) + "_gchp_building_link",
                        bus_1=str(cluster) + "_electricity_bus",
                        bus_2=str(cluster) + "_hp_elec_bus",
                        link_type="building_hp_elec_link",
                        sheets=sheets,
                        standard_parameters=standard_parameters,
                    )
                # create cluster's gasheating system
                sheets = Transformer.create_cluster_transformer(
                    technology=technology,
                    cluster_parameters=transformer_parameters,
                    cluster=cluster,
                    sheets=sheets,
                    standard_parameters=standard_parameters,
                )
    return sheets


def create_cluster_heat_bus(
    transformer_parameters: dict,
    clustering_dh: bool,
    sink_parameters: list,
    cluster: str,
    sheets: dict,
    standard_parameters: pandas.ExcelFile,
) -> dict:
    """
        In this method the heat bus of the cluster is created, this can
        be created with averaged district heating network values if
        desired by the user or is simply connected to the still
        existing buses of the buildings. The updated model definition
        is then returned as "sheets".
        
        :param transformer_parameters: dict containing the cluster's \
            transformer parameters (index) technology each entry is a \
            list where index 0 is a counter
        :type transformer_parameters: list
        :param clustering_dh: bool which defines rather the district \
            heating coordinates have to be clustered or not
        :type clustering_dh: bool
        :param sink_parameters: list containing the cluster's sinks \
            parameter (4) res_heat_demand, (5) com_heat_demand, \
            (6) ind_heat_demand
        :type sink_parameters: list
        :param cluster: str containing the cluster's ID
        :type cluster: str
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
    # create cluster heat bus if it consists rather the
    # opportunity for an investment in electricheating,
    # gasheating, ashp or gchp
    if sum([float(i[0]) for i in transformer_parameters.values()]) > 0:
        # cluster the district heating building buses
        lats = []
        lons = []
        # averaging the heat buses latitude and longitude entries if the
        # dh system has to be clustered
        if clustering_dh and len(sink_parameters[3]) > 0:
            for num, bus in sheets["buses"].iterrows():
                for sink_bus in sink_parameters[3]:
                    if bus["label"] == sink_bus[1]:
                        lats.append(sheets["buses"].loc[num, "lat"])
                        lons.append(sheets["buses"].loc[num, "lon"])
                        sheets["buses"].loc[num, "district heating conn."] = 0
        # create the cluster's heat bus if it is not in sheets["buses"]
        if str(cluster) + "_heat_bus" not in sheets["buses"]["label"]:
            sheets = Bus.create_standard_parameter_bus(
                label=str(cluster) + "_heat_bus",
                bus_type="building_heat_bus",
                sheets=sheets,
                coords=[
                    (sum(lats) / len(lats)) if len(lats) > 0 else 0,
                    (sum(lons) / len(lons)) if len(lons) > 0 else 0,
                    "1" if len(lats) > 0 else "0",
                ],
                standard_parameters=standard_parameters,
            )
            sheets["buses"].set_index("label", inplace=True, drop=False)
    return sheets


def clustering_information(
    building: list,
    sheets: dict,
    source_param: dict,
    storage_parameters: dict,
    transformer_parameters: dict,
    sheets_clustering: dict,
) -> (dict, dict, dict, dict):
    """
        After the data of the assets that are within a cluster have
        been collected previously, they are clustered in this method.
        
        :param building: list containing the building information from \
            the US-Input sheet
        :type building: list
        :param sheets: dictionary containing the pandas.Dataframes \
            that will represent the model definition's Spreadsheets
        :type sheets: dict
        :param source_param: dictionary containing the cluster summed \
            source information
        :type source_param: dict
        :param storage_parameters: dictionary containing the collected \
            storage information
        :type storage_parameters: dict
        :param transformer_parameters: dictionary containing the \
            collected transformer information
        :type transformer_parameters: dict
        :param sheets_clustering: copy of the model definition created \
            within the pre_processing.py
        :type sheets_clustering: dict
        
        :returns: - **source_param** (dict) - dictionary containing \
                        the cluster summed source information
                  - **transformer_parameters** (dict) - dictionary \
                        containing the collected transformer information
                  - **storage_parameters** (dict) - dictionary \
                        containing the collected storage information
                  - **sheets** (dict) - dictionary containing the \
                        pandas.Dataframes that will represent the \
                        model definition's Spreadsheets which was \
                        modified in this method
    """

    # collect cluster intern source information
    source_param, sheets = Source.sources_clustering(
        source_param=source_param,
        building=building,
        sheets=sheets,
        sheets_clustering=sheets_clustering,
    )

    # collect cluster intern transformer information
    transformer_parameters, sheets = Transformer.transformer_clustering(
        building=building,
        sheets_clustering=sheets_clustering,
        cluster_parameters=transformer_parameters,
        sheets=sheets,
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
        transformer_parameters,
        storage_parameters,
        sheets,
    )


def remove_buses(sheets: dict, sheets_clustering: dict) -> dict:
    """
        remove not longer used buses
        
            1. building specific gas bus
            2. building specific electricity bus
            3. building specific heat pump electricity bus
            4. building specific pv bus
            
        :param sheets: dictionary containing the pandas DataFrames \
            containing the energy system's data
        :type sheets: dict
        :param sheets_clustering:
        :type sheets_clustering: dict
        
        :return: - **sheets** (dict) - updated dictionary without the \
            not used buses
    """
    sheets["buses"].set_index("label", inplace=True, drop=False)
    for num, bus in sheets_clustering["buses"].iterrows():
        type_dict = {
            0: ["gas", "central"],
            1: ["electricity", "central"],
            2: ["hp_elec", "swhp_elec"],
            3: ["pv_bus", "~"],
        }
        for bus_type in type_dict:
            if (
                type_dict[bus_type][0] in bus["label"]
                and type_dict[bus_type][1] not in bus["label"]
            ):
                sheets["buses"] = sheets["buses"].drop(index=bus["label"])
    return sheets


def get_dict_building_cluster(tool: pandas.DataFrame) -> dict:
    """
        Method which creates a dictionary holding the Cluster ID and \
        it's buildings and returns it to the main method
        
        :param tool: DataFrame containing the Energysystem specific \
            parameters which result from the Upscaling Tool's input file
        :type tool: pandas.Dataframe
        
        :returns: **cluster_ids** (dict) - dict holding the Cluster \
            ID buildings combination
    """
    # create a dictionary holding the combination of cluster ID the included
    # building labels and its parcels
    cluster_ids = {}
    for num, building in tool[tool["active"].isin(true_bools)].iterrows():
        # collected building information
        building_info = [
            building["label"],
            building["parcel ID"],
            str(building["building type"])[0:3],
        ]
        # if cluster id already in dict
        if str(building["cluster ID"]) in cluster_ids:
            cluster_ids[str(building["cluster ID"])].append(building_info)
        # if cluster id not in dict
        else:
            cluster_ids.update({str(building["cluster ID"]): [building_info]})
    # return dictionary to main method
    return cluster_ids


def collect_building_information(
    cluster_ids: dict,
    cluster: str,
    sheets: dict,
    standard_parameters: pandas.ExcelFile,
    sheets_clustering: dict,
) -> (dict, list, dict, dict, dict):
    """
        In this method, the building specific assets are collected
        cluster wise. This includes sinks, PV systems, home storages
        (electric and thermal) and heat supply systems.
        
        :param cluster_ids: dictionary holding the clusters' buildings \
            information which are represented by lists containing the \
            building label [0], the building's parcel ID [1] and the \
            building type [2]
        :type cluster_ids: dict
        :param cluster: Cluster ID
        :type cluster: str
        :param sheets: dictionary containing the pandas.Dataframes \
            that will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        :param sheets_clustering: copy of the model definition created \
            within the pre_processing.py
        :type sheets_clustering: dict
        
        :returns: - **sheets** (dict) - dictionary containing the \
                        pandas.Dataframes that will represent the \
                        model definition's Spreadsheets which was \
                        modified in this method
                  - **sink_parameters** (list) - list containing \
                        clusters' sinks information
                  - **source_param** (dict) - dictionary containing \
                        the cluster summed source information
                  - **storage_parameters** (dict) - dictionary \
                        containing the collected storage information
                  - **transformer_parameters** (dict) - dictionary \
                        containing the collected transformer information
    """
    # cluster sinks parameter
    # [res_electricity_demand, com_electricity_demand,
    #  ind_electricity_demand, heat_buses, res_heat_demand,
    #  com_heat_demand, ind_heat_demand, heat_sinks,
    #  electricity_res_sink, electricity_com_sink, electricity_ind_sink]
    sink_parameters = [0, 0, 0, [], 0, 0, 0, [], [], [], []]
    # transformer_parameter technology:
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
    storage_parameters = {"battery": [0] * 5, "thermal": [0] * 5}

    # storage param technology: [counter, maxinvest, periodical costs,
    # periodical constraint costs, variable costs, Albedo,
    # Altitude, Azimuth, Surface Tilt, Latitude, Longitude]
    source_param = {
        "pv_north": [0] * 12,
        "pv_north_east": [0] * 12,
        "pv_east": [0] * 12,
        "pv_south_east": [0] * 12,
        "pv_south": [0] * 12,
        "pv_south_west": [0] * 12,
        "pv_west": [0] * 12,
        "pv_north_west": [0] * 12,
        "st_north": [0] * 12,
        "st_north_east": [0] * 12,
        "st_east": [0] * 12,
        "st_south_east": [0] * 12,
        "st_south": [0] * 12,
        "st_south_west": [0] * 12,
        "st_west": [0] * 12,
        "st_north_west": [0] * 12,
    }

    # remove the not longer used links
    sheets = Link.delete_non_used_links(
        sheets_clustering=sheets_clustering, cluster_ids=cluster_ids, sheets=sheets
    )

    for building in cluster_ids:
        for index, sink in sheets_clustering["sinks"].iterrows():
            # collecting information for sinks
            sink_parameters = Sink.sink_clustering(
                building=building, sink=sink, sink_parameters=sink_parameters
            )

        # create cluster elec buses
        sheets = Bus.create_cluster_electricity_buses(
            building=building,
            cluster=cluster,
            sheets=sheets,
            standard_parameters=standard_parameters,
        )

        (
            source_param,
            transformer_parameters,
            storage_parameters,
            sheets,
        ) = clustering_information(
            building=building,
            sheets=sheets,
            source_param=source_param,
            storage_parameters=storage_parameters,
            transformer_parameters=transformer_parameters,
            sheets_clustering=sheets_clustering,
        )

        sheets = Link.create_cluster_pv_links(
            cluster=cluster,
            sheets=sheets,
            standard_parameters=standard_parameters,
            sink_parameters=sink_parameters,
        )

        if transformer_parameters["gasheating"][0] > 0:
            sheets = Link.add_cluster_naturalgas_bus_links(
                sheets=sheets, cluster=cluster, standard_parameters=standard_parameters
            )

        # update the sources in and output
        sheets = Source.update_sources_in_output(
            building=building,
            sheets_clustering=sheets_clustering,
            cluster=cluster,
            sheets=sheets,
        )

    return (
        sheets,
        sink_parameters,
        source_param,
        storage_parameters,
        transformer_parameters,
    )


def create_cluster_components(
    standard_parameters: pandas.ExcelFile,
    sink_parameters: list,
    cluster: str,
    central_electricity_network: bool,
    sheets: dict,
    transformer_parameters: dict,
    source_param: dict,
    storage_parameters: dict,
    clustering_dh: bool,
) -> dict:
    """
        After previously collecting and or averaging the information of
        the components belonging to a cluster and deleting the
        components that are no longer needed, the cluster components
        are created in this method. The adapted model definition
        structure "sheets" is returned after the creation process.
        
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        :parameter sink_parameters: list containing clusters' sinks \
            information
        :type sink_parameters: list
        :param cluster: cluster ID
        :type cluster: str
        :param central_electricity_network: bool which decides rather \
            a central electricity exchange is possible or not
        :type central_electricity_network: bool
        :param sheets: dictionary containing the pandas.Dataframes that\
                will represent the model definition's Spreadsheets
        :type sheets: dict
        :param transformer_parameters: dictionary containing the \
            collected transformer information
        :type transformer_parameters: dict
        :param source_param: dictionary containing the cluster summed \
            source information
        :type source_param: dict
        :param storage_parameters: dictionary containing the collected \
            storage information
        :type storage_parameters: dict
        :param clustering_dh: bool which decides rather the cluster's \
            district heating connections are clustered or not
        :type clustering_dh: bool
    
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    # TRANSFORMER
    # create cluster electricity sinks
    sheets = Sink.create_cluster_electricity_sinks(
        standard_parameters=standard_parameters,
        sink_parameters=sink_parameters,
        cluster=cluster,
        central_electricity_network=central_electricity_network,
        sheets=sheets,
    )

    sheets = clustering_transformers(
        sheets=sheets,
        sink_parameters=sink_parameters,
        transformer_parameters=transformer_parameters,
        cluster=cluster,
        standard_parameters=standard_parameters,
    )
    # SOURCES
    # create cluster's sources and competition constraints
    sheets = Source.create_cluster_sources(
        source_param=source_param,
        cluster=cluster,
        sheets=sheets,
        standard_parameters=standard_parameters,
    )
    for i in ["battery", "thermal"]:
        # STORAGES
        if storage_parameters[i][0] > 0:
            # create cluster's battery
            sheets = Storage.create_cluster_storage(
                storage_type=i,
                cluster=cluster,
                storage_parameter=storage_parameters,
                sheets=sheets,
                standard_parameters=standard_parameters,
            )

    sheets = create_cluster_heat_bus(
        transformer_parameters=transformer_parameters,
        cluster=cluster,
        clustering_dh=clustering_dh,
        sink_parameters=sink_parameters,
        sheets=sheets,
        standard_parameters=standard_parameters,
    )

    return sheets


def clustering_method(
    tool: pandas.DataFrame,
    sheets: dict,
    standard_parameters: pandas.ExcelFile,
    central_electricity_network: bool,
    clustering_dh: bool,
) -> dict:
    """
        This method represents the main algorithm of clustering within
        the US tool. For this purpose, based on the model definition
        resulting from the preprocessing, the data of the plants in a
        cluster are first collected and/or averaged, then deleted, and
        finally the resulting plant for the cluster is created.
        
        :param tool: DataFrame containing the Energysystem specific \
            parameters which result from the Upscaling Tool's input file
        :type tool: pandas.Dataframe
        :param sheets: dictionary containing the pandas.Dataframes that\
                will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        :param central_electricity_network: bool which decides rather \
            a central electricity exchange is possible or not
        :type central_electricity_network: bool
        :param clustering_dh: bool which decides rather the cluster's \
            district heating connections are clustered or not
        :type clustering_dh: bool
        
        :returns: - **sheets** (dict) - dictionary holding the \
            clustered model definition's data
    """
    # create a dictionary holding the combination of cluster ID and it's
    # buildings
    cluster_ids = get_dict_building_cluster(tool=tool)
    sheets_clustering = {}
    # local copy of status of model definition's components
    for sheet in list(sheets.keys()):
        sheet_edited = sheets[sheet].copy()
        sheet_edited.reset_index(drop=True, inplace=True)
        sheet_edited = sheet_edited.drop(index=0)
        sheets_clustering.update({sheet: sheet_edited})
    sheets = remove_buses(sheets=sheets, sheets_clustering=sheets_clustering)

    for cluster in cluster_ids:
        # reset all indices to delete the right rows in pandas dataframe
        for sheet in ["transformers", "storages", "links", "sinks", "sources", "buses"]:
            if not sheets[sheet].empty:
                sheets[sheet].set_index("label", inplace=True, drop=False)

        if cluster_ids[cluster]:
            (
                sheets,
                sink_parameters,
                source_param,
                storage_parameters,
                transformer_parameters,
            ) = collect_building_information(
                cluster_ids=cluster_ids[cluster],
                cluster=cluster,
                sheets=sheets,
                standard_parameters=standard_parameters,
                sheets_clustering=sheets_clustering,
            )

            sheets = create_cluster_components(
                standard_parameters=standard_parameters,
                sink_parameters=sink_parameters,
                cluster=cluster,
                central_electricity_network=central_electricity_network,
                sheets=sheets,
                transformer_parameters=transformer_parameters,
                source_param=source_param,
                storage_parameters=storage_parameters,
                clustering_dh=clustering_dh,
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
                    standard_parameters=standard_parameters,
                )

    return sheets
