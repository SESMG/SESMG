import program_files.urban_district_upscaling.pre_processing as pre_processing


def sink_clustering(building, sink, sink_parameters):
    """
        TODO DOCSTRING
    """

    if str(building[0]) in sink["label"] \
            and "electricity" in sink["label"]:
        if sink["load profile"] == "h0" and "RES" in building[2]:
            sink_parameters[0] += sink["annual demand"]
            sheets["sinks"] = sheets["sinks"].drop(index=sink["label"])
        elif "COM" in building[2]:
            sink_parameters[1] += sink["annual demand"]
            sheets["sinks"] = sheets["sinks"].drop(index=sink["label"])
        elif "IND" in building[2]:
            sink_parameters[2] += sink["annual demand"]
            sheets["sinks"] = sheets["sinks"].drop(index=sink["label"])
    elif str(building[0]) in sink["label"] \
            and "heat" in sink["label"]:
        sink_parameters[3].append((building[2], sink["input"]))
        if "RES" in building[2]:
            sink_parameters[4] += sink["annual demand"]
        elif "COM" in building[2]:
            sink_parameters[5] += sink["annual demand"]
        elif "IND" in building[2]:
            sink_parameters[6] += sink["annual demand"]
    return sink_parameters


def sources_clustering(building, sources, source_param, azimuth_type):
    """
        # TODO DOCSTRING

        :param building:
        :type building:
        :param sources:
        :type sources:
        :param source_param:
        :type source_param:
        :param azimuth_type:
        :type azimuth_type:
    """
    if str(building[0]) in sources["label"] \
            and sources["technology"] == "photovoltaic" \
            and sources["label"] in sheets["sources"].index:
        # counter
        source_param["pv_{}".format(azimuth_type)][0] += 1
        # maxinvest
        source_param["pv_{}".format(azimuth_type)][1] \
            += sources["max. investment capacity"]
        # periodical_costs
        source_param["pv_{}".format(azimuth_type)][2] \
            += sources["periodical costs"]
        # periodical constraint costs
        source_param["pv_{}".format(azimuth_type)][3] \
            += sources["periodical constraint costs"]
        # variable costs
        source_param["pv_{}".format(azimuth_type)][4] \
            += sources["variable costs"]
        # albedo
        source_param["pv_{}".format(azimuth_type)][5] += sources["Albedo"]
        # altitude
        source_param["pv_{}".format(azimuth_type)][6] += sources["Altitude"]
        # azimuth
        source_param["pv_{}".format(azimuth_type)][7] += sources["Azimuth"]
        # surface tilt
        source_param["pv_{}".format(azimuth_type)][8] \
            += sources["Surface Tilt"]
        # latitude
        source_param["pv_{}".format(azimuth_type)][9] += sources["Latitude"]
        # longitude
        source_param["pv_{}".format(azimuth_type)][10] += sources["Longitude"]
        sheets["sources"] = sheets["sources"].drop(index=sources["label"])

    if str(building[0]) in sources["label"] \
            and sources["technology"] == "solar_thermal_flat_plate" \
            and sources["label"] in sheets["sources"].index:
        # counter
        source_param["st_{}".format(azimuth_type)][0] += 1
        # maxinvest
        source_param["st_{}".format(azimuth_type)][1] \
            += sources["max. investment capacity"]
        # periodical_costs
        source_param["st_{}".format(azimuth_type)][2] \
            += sources["periodical costs"]
        # periodical constraint costs
        source_param["st_{}".format(azimuth_type)][3] \
            += sources["periodical constraint costs"]
        # variable costs
        source_param["st_{}".format(azimuth_type)][4] \
            += sources["variable costs"]
        # albedo
        source_param["st_{}".format(azimuth_type)][5] += sources["Albedo"]
        # altitude
        source_param["st_{}".format(azimuth_type)][6] += sources["Altitude"]
        # azimuth
        source_param["st_{}".format(azimuth_type)][7] += sources["Azimuth"]
        # surface tilt
        source_param["st_{}".format(azimuth_type)][8] \
            += sources["Surface Tilt"]
        # latitude
        source_param["st_{}".format(azimuth_type)][9] += sources["Latitude"]
        # longitude
        source_param["st_{}".format(azimuth_type)][10] += sources["Longitude"]
        sheets["sources"] = sheets["sources"].drop(index=sources["label"])

    return source_param


def transformer_clustering(building, transformer,
                           transformer_parameters, heat_buses_gchps):
    if str(building[0]) in transformer["label"] \
            and "gasheating" in transformer["label"] \
            and transformer["label"] in sheets["transformers"].index:
        transformer_parameters["gasheating"][0] += 1
        transformer_parameters["gasheating"][1] \
            += transformer["efficiency"]
        transformer_parameters["gasheating"][3] \
            += transformer["periodical costs"]
        transformer_parameters["gasheating"][4] += \
            transformer["variable output constraint costs"]
        sheets["transformers"] = \
            sheets["transformers"].drop(index=transformer["label"])
    if str(building[0]) in transformer["label"] \
            and "electric" in transformer["label"] \
            and transformer["label"] in sheets["transformers"].index:
        transformer_parameters["electric_heating"][0] += 1
        transformer_parameters["electric_heating"][1] \
            += transformer["efficiency"]
        transformer_parameters["electric_heating"][3] += transformer[
            "periodical costs"]
        transformer_parameters["electric_heating"][4] += \
            transformer["variable output constraint costs"]
        sheets["transformers"] = \
            sheets["transformers"].drop(index=transformer["label"])
    if str(building[0]) in transformer["label"] \
            and "ashp" in transformer["label"] \
            and transformer["label"] in sheets["transformers"].index:
        transformer_parameters["ashp"][0] += 1
        transformer_parameters["ashp"][1] \
            += transformer["efficiency"]
        transformer_parameters["ashp"][2] \
            += transformer["efficiency2"]
        transformer_parameters["ashp"][3] += transformer[
            "periodical costs"]
        transformer_parameters["ashp"][4] += \
            transformer["variable output constraint costs"]
        sheets["transformers"] = \
            sheets["transformers"].drop(index=transformer["label"])
    if str(building[1]) != "0":
        if str(building[1])[-9:] in transformer["label"] \
                and "gchp" in transformer["label"] \
                and transformer["label"] in sheets["transformers"].index:
            transformer_parameters["gchp"][0] += 1
            transformer_parameters["gchp"][1] \
                += transformer["efficiency"]
            transformer_parameters["gchp"][2] \
                += transformer["efficiency2"]
            transformer_parameters["gchp"][3] += transformer[
                "periodical costs"]
            transformer_parameters["gchp"][4] += \
                transformer["variable output constraint costs"]
            transformer_parameters["gchp"][5] += \
                transformer["area"]
            sheets["buses"].set_index("label", inplace=True, drop=False)
            if transformer["output"] in sheets["buses"].index:
                sheets["buses"] = \
                    sheets["buses"].drop(index=transformer["output"])
            sheets["transformers"] = \
                sheets["transformers"].drop(index=transformer["label"])
    return heat_buses_gchps, transformer_parameters


def storage_clustering(building, storage, storage_parameter):
    if str(building[0]) in storage["label"] \
            and "battery" in storage["label"] \
            and storage["label"] in sheets["storages"].index:
        storage_parameter["battery"][0] += 1
        storage_parameter["battery"][1] += storage["max. investment capacity"]
        storage_parameter["battery"][2] += storage["periodical costs"]
        storage_parameter["battery"][3] += storage[
            "periodical constraint costs"]
        sheets["storages"] = sheets["storages"].drop(index=storage["label"])
    if str(building[0]) in storage["label"] \
            and "thermal" in storage["label"] \
            and storage["label"] in sheets["storages"].index:
        storage_parameter["thermal"][0] += 1
        storage_parameter["thermal"][1] += storage["max. investment capacity"]
        storage_parameter["thermal"][2] += storage["periodical costs"]
        storage_parameter["thermal"][3] += storage[
            "periodical constraint costs"]
        storage_parameter["thermal"][4] += storage["variable output costs"]
        sheets["storages"] = sheets["storages"].drop(index=storage["label"])
    return storage_parameter


def restructuring_links(sheets_clustering, building, cluster,
                        standard_parameters):
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


def clustering_method(tool, standard_parameters, sheet_names,
                      central_electricity_network, sheets_input):
    """
        TODO DOCSTRING TEXT
        :param tool:
        :type tool: pd.Dataframe
        :param standard_parameters:
        :type standard_parameters:
        :param sheet_names:
        :type sheet_names:
        :param central_electricity_network:
        :type central_electricity_network:
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
            if str(building["cluster_ID"]) in cluster_ids:
                cluster_ids[str(building["cluster_ID"])].append(
                    [building['label'], building['parcel'],
                     str(building["building type"][0:3])])
            else:
                cluster_ids.update({
                    str(building["cluster_ID"]):
                        [[building['label'], building['parcel'],
                          str(building["building type"][0:3])]]})
    # local copy of status of scenario components
    sheets_clustering = {}
    for sheet in sheet_names:
        sheet_edited = sheets[sheet].copy()
        sheet_edited = sheet_edited.drop(index=0)
        sheets_clustering.update({sheet: sheet_edited})
    # start clustering
    # remove not longer used buses
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
        sheets["transformers"].set_index("label", inplace=True, drop=False)
        sheets["storages"].set_index("label", inplace=True, drop=False)
        sheets["links"].set_index("label", inplace=True, drop=False)
        sheets["sinks"].set_index("label", inplace=True, drop=False)
        sheets["sources"].set_index("label", inplace=True, drop=False)
        sheets["buses"].set_index("label", inplace=True, drop=False)
        if cluster_ids[cluster]:
            # cluster sinks parameter [res_elec_demand, com_elec_demand,
            #                          ind_elec_demand, heat_buses,
            #                          res_heat_demand, com_heat_demand,
            #                          ind_heat_demand]
            sink_parameters = [0, 0, 0, [], 0, 0, 0]
            # transformer_param technology: [counter, efficiency, efficiency2,
            # periodical_costs, variable_constraint_costs]
            transformer_parameters = \
                {"gasheating": [0, 0, "x", 0, 0],
                 "electric_heating": [0, 0, "x", 0, 0],
                 "ashp": [0, 0, 0, 0, 0],
                 "gchp": [0, 0, 0, 0, 0, 0]}
            # storage param technology: [counter, maxinvest, periodical costs,
            # periodical constraint costs, variable output costs]
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
                "st_west": [0] * 11, "st_north_west": [0] * 11,}

            for building in cluster_ids[cluster]:
                for index, sink in sheets_clustering["sinks"].iterrows():
                    # collecting information for bundled elec sinks
                    sink_parameters = sink_clustering(building, sink,
                                                      sink_parameters)
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
                if bus_type:
                    # cluster electricity bus if cluster type is res / com
                    pre_processing.create_standard_parameter_bus(
                        label=str(cluster) + bus_type + "electricity_bus",
                        bus_type="building" + bus_type + "electricity_bus",
                        standard_parameters=standard_parameters)
                    sheets["buses"].set_index("label", inplace=True,
                                              drop=False)

                    # Creates a Bus connecting the cluster electricity bus with
                    # the res electricity bus
                    pre_processing.create_standard_parameter_link(
                        label=str(cluster) + bus_type + "electricity_link",
                        bus_1=str(cluster) + "_electricity_bus",
                        bus_2=str(cluster) + bus_type + "electricity_bus",
                        link_type='building_pv_building_link',
                        standard_parameters=standard_parameters)
                    sheets["links"].set_index("label", inplace=True,
                                              drop=False)
                for index, sources in sheets_clustering["sources"].iterrows():
                    # collecting information for bundled photovoltaic systems
                    if sources["technology"] in ["photovoltaic",
                                                 "solar_thermal_flat_plate"]:
                        if -22.5 <= sources["Azimuth"] < 22.5:
                            azimuth_type = "north"
                        elif 22.5 <= sources["Azimuth"] < 67.5:
                            azimuth_type = "north_east"
                        elif 67.5 <= sources["Azimuth"] < 112.5:
                            azimuth_type = "east"
                        elif 112.5 <= sources["Azimuth"] < 157.5:
                            azimuth_type = "south_east"
                        elif sources["Azimuth"] >= 157.5 \
                                or sources["Azimuth"] < -157.5:
                            azimuth_type = "south"
                        elif -157.5 <= sources["Azimuth"] < -112.5:
                            azimuth_type = "south_west"
                        elif -112.5 <= sources["Azimuth"] < -67.5:
                            azimuth_type = "west"
                        elif -67.5 <= sources["Azimuth"] < -22.5:
                            azimuth_type = "north_west"
                        else:
                            azimuth_type = None
                        if azimuth_type:
                            source_param = \
                                sources_clustering(building, sources,
                                                   source_param, azimuth_type)

                for index, transformer in sheets_clustering[
                        "transformers"].iterrows():
                    # collecting information for bundled transformer
                    heat_buses_gchps, transformer_parameters = \
                        transformer_clustering(building, transformer,
                                               transformer_parameters,
                                               heat_buses_gchps)
                for index, storage in sheets_clustering["storages"].iterrows():
                    # collecting information for bundled storages
                    storage_parameters = \
                        storage_clustering(building, storage,
                                           storage_parameters)
                restructuring_links(sheets_clustering, building, cluster,
                                    standard_parameters)
                # change sources output bus
                for i, j in sheets_clustering["sources"].iterrows():
                    if str(building[0]) in str(j["input"]) and \
                            "electricity" in str(j["input"]):
                        sheets["sources"]['input'] = \
                            sheets["sources"]['input'].replace(
                                [str(building[0]) + "_electricity_bus"],
                                str(cluster) + "_electricity_bus")
                    if str(building[0]) in str(j["output"]) and \
                            "heat" in str(j["output"]):
                        sheets["sources"]["output"] = \
                            sheets["sources"]["output"].replace(
                                [str(building[0]) + "_heat_bus"],
                                str(cluster) + "_heat_bus")

            bus_parameters = \
                standard_parameters.parse('buses', index_col='bus_type')
            total_annual_elec_demand = (sink_parameters[0]
                                        + sink_parameters[1]
                                        + sink_parameters[2])
            total_annual_heat_demand = (sink_parameters[4]
                                        + sink_parameters[5]
                                        + sink_parameters[6])
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
                    pre_processing.create_central_elec_bus_connection(cluster,
                                                       standard_parameters)
            if sink_parameters[0] > 0:
                pre_processing.create_standard_parameter_sink(
                    "RES_electricity_sink",
                    str(cluster) + "_res_electricity_demand",
                    str(cluster) + "_res_electricity_bus",
                    sink_parameters[0], standard_parameters, 0)
            if sink_parameters[1] > 0:
                pre_processing.create_standard_parameter_sink(
                    "COM_electricity_sink",
                    str(cluster) + "_com_electricity_demand",
                    str(cluster) + "_com_electricity_bus",
                    sink_parameters[1], standard_parameters, 0)
            if sink_parameters[2] > 0:
                pre_processing.create_standard_parameter_sink(
                    "IND_electricity_sink",
                    str(cluster) + "_ind_electricity_demand",
                    str(cluster) + "_ind_electricity_bus",
                    sink_parameters[2], standard_parameters, 0)
            # create res or com gasheating
            if transformer_parameters["gasheating"][0] > 0:
                pre_processing.create_standard_parameter_bus(
                    label=str(cluster) + "_gas_bus",
                    bus_type='building_res_gas_bus',
                    standard_parameters=standard_parameters)
                sheets["buses"].set_index("label", inplace=True,
                                          drop=False)
                sheets["buses"].loc[(str(cluster) + "_gas_bus"),
                                    "shortage costs"] = \
                    ((sink_parameters[4] / total_annual_heat_demand)
                      * bus_parameters.loc["building_res_gas_bus"][
                         "shortage costs"]
                      + (sink_parameters[5] / total_annual_heat_demand)
                      * bus_parameters.loc["building_com_gas_bus"][
                        "shortage costs"]
                      + (sink_parameters[6] / total_annual_heat_demand)
                      * bus_parameters.loc["building_ind_gas_bus"][
                         "shortage costs"])

                # define individual gas_heating_parameters
                parameter_dict = \
                    {'label': str(cluster) + '_gasheating_transformer',
                     'comment': 'automatically_created',
                     'input': str(cluster) + '_gas_bus',
                     'output': str(cluster) + '_heat_bus',
                     'output2': 'None'}
                standard_param, standard_keys = \
                    pre_processing.read_standard_parameters(
                        standard_parameters, "building_gasheating_transformer",
                        "transformers", "comment")

                for i in range(len(standard_keys)):
                    parameter_dict[standard_keys[i]] = \
                        standard_param[standard_keys[i]]
                parameter_dict["efficiency"] = \
                    transformer_parameters["gasheating"][1] \
                    / transformer_parameters["gasheating"][0]
                parameter_dict["periodical costs"] = \
                    transformer_parameters["gasheating"][3] \
                    / transformer_parameters["gasheating"][0]
                parameter_dict[
                    "variable output constraint costs"] = \
                    transformer_parameters["gasheating"][4] \
                    / transformer_parameters["gasheating"][0]
                parameter_dict[
                    "max. investment capacity"] = \
                    standard_param["max. investment capacity"] \
                    * transformer_parameters["gasheating"][0]
                # produce a pandas series out of the dict above due to
                # easier appending
                pre_processing.append_component("transformers", parameter_dict)

            # Define PV Standard-Parameters
            sources_standard_parameters = standard_parameters.parse(
                'sources')
            sources_standard_parameters.set_index('comment',
                                                  inplace=True)
            pv_standard_parameters = \
                sources_standard_parameters.loc[
                    'fixed photovoltaic source']

            st_stan_param = \
                sources_standard_parameters.loc[
                    'solar_thermal_collector']

            for azimuth in ["north_000", "north_east_045", "east_090",
                            "south_east_135", "south_180",
                            "south_west_225", "west_270", "north_west_315"]:
                if source_param["pv_{}".format(azimuth[:-4])][0] > 0:
                    if (str(cluster) + "_pv_bus") not in sheets["buses"].index:
                        pre_processing.create_standard_parameter_bus(
                            label=str(cluster) + "_pv_bus",
                            bus_type='building_pv_bus',
                            standard_parameters=standard_parameters)
                        sheets["buses"].set_index("label", inplace=True,
                                                  drop=False)
                    pre_processing.create_pv_source(
                        cluster, azimuth[:-4],
                        area=source_param["pv_{}".format(azimuth[:-4])][1]
                             / pv_standard_parameters[
                                 "Capacity per Area (kW/m2)"],
                        tilt=source_param["pv_{}".format(azimuth[:-4])][8]
                             / source_param["pv_{}".format(azimuth[:-4])][0],
                        azimuth=int(azimuth[-3:]),
                        latitude=
                        source_param["pv_{}".format(azimuth[:-4])][9]
                        / source_param["pv_{}".format(azimuth[:-4])][0],
                        longitude=
                        source_param["pv_{}".format(azimuth[:-4])][10]
                        / source_param["pv_{}".format(azimuth[:-4])][0],
                        pv_standard_parameters=pv_standard_parameters)

                # SOLAR THERMAL
                if source_param["st_{}".format(azimuth[:-4])][0] > 0:
                    pre_processing.create_solarthermal_source(
                        building_id=cluster,
                        plant_id=azimuth[:-4],
                        azimuth=int(azimuth[-3:]),
                        tilt=source_param["st_{}".format(azimuth[:-4])][8]
                             / source_param["st_{}".format(azimuth[:-4])][0],
                        area=source_param["st_{}".format(azimuth[:-4])][1]
                             / st_stan_param["Capacity per Area (kW/m2)"],
                        solarthermal_standard_parameters=st_stan_param,
                        latitude=
                        source_param["st_{}".format(azimuth[:-4])][9]
                        / source_param["st_{}".format(azimuth[:-4])][0],
                        longitude=
                        source_param["st_{}".format(azimuth[:-4])][10]
                        / source_param["st_{}".format(azimuth[:-4])][0], )

                    if source_param["pv_{}".format(azimuth[:-4])][0] > 0:
                        area_st = \
                            (source_param["st_{}".format(azimuth[:-4])][1]
                             / st_stan_param['Capacity per Area (kW/m2)'])
                        area_pv = \
                            (source_param["st_{}".format(azimuth[:-4])][1]
                             / st_stan_param['Capacity per Area (kW/m2)'])

                        pre_processing.create_competition_constraint(
                            component1=str(cluster) + "_" + azimuth[:-4]
                                       + "_solarthermal_source",
                            factor1=1 / st_stan_param[
                                'Capacity per Area (kW/m2)'],
                            component2=str(cluster) + "_" + azimuth[:-4]
                                       + "_pv_source",
                            factor2=1 / pv_standard_parameters[
                                "Capacity per Area (kW/m2)"],
                            limit=area_st if area_st >= area_pv else area_pv)

            # TODO do we have to diiferntiate res and com
            if transformer_parameters["electric_heating"][0] > 0:
                # define individual gas_heating_parameters
                parameter_dict = \
                    {'label': str(cluster) + '_electricheating_transformer',
                     'comment': 'automatically_created',
                     'input': str(cluster) + '_electricity_bus',
                     'output': str(cluster) + '_heat_bus',
                     'output2': 'None'}
                standard_param, standard_keys = \
                    pre_processing.read_standard_parameters(
                        standard_parameters,
                        "building_electricheating_transformer", "transformers", "comment")

                for i in range(len(standard_keys)):
                    parameter_dict[standard_keys[i]] \
                        = standard_param[standard_keys[i]]
                parameter_dict["efficiency"] = \
                    transformer_parameters["electric_heating"][1] \
                    / transformer_parameters["electric_heating"][0]
                parameter_dict["periodical costs"] = \
                    transformer_parameters["electric_heating"][3] \
                    / transformer_parameters["electric_heating"][0]
                parameter_dict["variable output constraint costs"] = \
                    transformer_parameters["electric_heating"][4] \
                    / transformer_parameters["electric_heating"][0]
                parameter_dict["max. investment capacity"] = \
                    standard_param["max. investment capacity"] \
                    * transformer_parameters["electric_heating"][0]
                # produce a pandas series out of the dict above due to easier
                # appending
                pre_processing.append_component("transformers", parameter_dict)

            if transformer_parameters["ashp"][0] > 0:
                # building hp electricity bus
                pre_processing.create_standard_parameter_bus(
                    label=str(cluster) + "_hp_elec_bus",
                    bus_type='building_hp_electricity_bus',
                    standard_parameters=standard_parameters)
                sheets["buses"].set_index("label", inplace=True,
                                          drop=False)
                sheets["buses"].loc[(str(cluster) + "_hp_elec_bus"),
                                    "shortage costs"] = \
                    ((sink_parameters[4]
                      / total_annual_heat_demand)
                     * bus_parameters.loc["building_hp_electricity_bus"][
                         "shortage costs"]
                     + (sink_parameters[5] / total_annual_heat_demand)
                     * bus_parameters.loc["building_hp_electricity_bus"][
                         "shortage costs"]
                     + (sink_parameters[2] / total_annual_heat_demand)
                     * bus_parameters.loc["building_ind_electricity_bus"][
                         "shortage costs"])
                # electricity link from building electricity bus to hp elec bus
                pre_processing.create_standard_parameter_link(
                    label=str(cluster) + "_gchp_building_link",
                    bus_1=str(cluster) + "_electricity_bus",
                    bus_2=str(cluster) + "_hp_elec_bus",
                    link_type="building_hp_elec_link",
                    standard_parameters=standard_parameters)
                standard_param, standard_keys = \
                    pre_processing.read_standard_parameters(
                        standard_parameters, "building_ashp_transformer",
                        "transformers", "comment")
                # define individual gas_heating_parameters
                parameter_dict = {
                    'label': str(cluster) + '_ashp_transformer',
                    'comment': 'automatically_created',
                    'input': str(cluster) + '_hp_elec_bus',
                    'output': str(cluster) + '_heat_bus',
                    'output2': 'None',
                    'existing capacity': 0,
                    'min. investment capacity': 0}

                for i in range(len(standard_keys)):
                    parameter_dict[standard_keys[i]] = \
                        standard_param[standard_keys[i]]
                parameter_dict["efficiency"] = \
                    transformer_parameters["ashp"][1] \
                    / transformer_parameters["ashp"][0]
                parameter_dict["efficiency2"] = \
                    transformer_parameters["ashp"][2] \
                    / transformer_parameters["ashp"][0]
                parameter_dict["periodical costs"] = \
                    transformer_parameters["ashp"][3] \
                    / transformer_parameters["ashp"][0]
                parameter_dict["max. investment capacity"] = \
                    transformer_parameters["ashp"][0] \
                    * parameter_dict["max. investment capacity"]
                # produce a pandas series out of the dict above due to easier
                # appending
                pre_processing.append_component("transformers", parameter_dict)
            if transformer_parameters["gchp"][0] > 0:
                standard_param, standard_keys = \
                    pre_processing.read_standard_parameters(
                        standard_parameters, "building_gchp_transformer",
                        "transformers", "comment")
                # define individual gas_heating_parameters
                parameter_dict = {
                    'label': str(cluster) + '_gchp_transformer',
                    'comment': 'automatically_created',
                    'input': str(cluster) + '_hp_elec_bus',
                    'output': str(cluster) + '_heat_bus',
                    'output2': 'None',
                    'existing capacity': 0,
                    'min. investment capacity': 0}

                for i in range(len(standard_keys)):
                    parameter_dict[standard_keys[i]] = \
                        standard_param[standard_keys[i]]
                parameter_dict["efficiency"] = \
                    transformer_parameters["gchp"][1] \
                    / transformer_parameters["gchp"][0]
                parameter_dict["efficiency2"] = \
                    transformer_parameters["gchp"][2] \
                    / transformer_parameters["gchp"][0]
                parameter_dict["periodical costs"] = \
                    transformer_parameters["gchp"][3] \
                    / transformer_parameters["gchp"][0]
                parameter_dict["max. investment capacity"] = \
                    transformer_parameters["gchp"][0] \
                    * parameter_dict["max. investment capacity"]
                parameter_dict["area"] = transformer_parameters["gchp"][5]
                # produce a pandas series out of the dict above due to easier
                # appending
                pre_processing.append_component("transformers", parameter_dict)
            if storage_parameters["battery"][0] > 0:
                # read the standards from standard_param and append
                # them to the dict
                standard_param, standard_keys = \
                    pre_processing.read_standard_parameters(
                        standard_parameters, "building_battery_storage",
                        "storages", "comment")
                parameter_dict = {'label': str(cluster) + '_battery_storage',
                                  'comment': 'automatically_created',
                                  'bus': str(cluster) + '_electricity_bus'}

                for i in range(len(standard_keys)):
                    parameter_dict[standard_keys[i]] = \
                        standard_param[standard_keys[i]]

                parameter_dict["max. investment capacity"] = \
                    storage_parameters["battery"][1]
                parameter_dict["periodical costs"] = \
                    storage_parameters["battery"][2] / \
                    storage_parameters["battery"][0]
                parameter_dict["periodical constraint costs"] = \
                    storage_parameters["battery"][3] / \
                    storage_parameters["battery"][0]
                # produce a pandas series out of the dict above due to easier
                # appending
                pre_processing.append_component("storages", parameter_dict)
            if storage_parameters["thermal"][0] > 0:
                # read the standards from standard_param and append
                # them to the dict
                standard_param, standard_keys = \
                    pre_processing.read_standard_parameters(
                        standard_parameters, "building_thermal_storage",
                        "storages", "comment")
                parameter_dict = {'label': str(cluster) + '_thermal_storage',
                                  'comment': 'automatically_created',
                                  'bus': str(cluster) + '_heat_bus'}

                for i in range(len(standard_keys)):
                    parameter_dict[standard_keys[i]] = \
                        standard_param[standard_keys[i]]
                parameter_dict["max. investment capacity"] = \
                    storage_parameters["thermal"][1]
                parameter_dict["periodical costs"] = \
                    storage_parameters["thermal"][2] / \
                    storage_parameters["thermal"][0]
                parameter_dict["periodical constraint costs"] = \
                    storage_parameters["thermal"][3] / \
                    storage_parameters["thermal"][0]
                parameter_dict["variable output costs"] = \
                    storage_parameters["thermal"][4] / \
                    storage_parameters["thermal"][0]
                # produce a pandas series out of the dict above due to easier
                # appending
                pre_processing.append_component("storages", parameter_dict)
            if transformer_parameters["gasheating"][0] > 0:
                if str(cluster) + "_heat_bus" not in sheets["buses"].index:
                    pre_processing.create_standard_parameter_bus(
                        label=str(cluster) + "_heat_bus",
                        bus_type='building_heat_bus',
                        standard_parameters=standard_parameters)
                    sheets["buses"].set_index("label", inplace=True,
                                              drop=False)
            if transformer_parameters["electric_heating"][0] > 0 \
                    or transformer_parameters["ashp"][0] > 0 \
                    or transformer_parameters["gchp"][0] > 0:
                if str(cluster) + "_heat_bus" not in sheets["buses"].index:
                    # building heat bus
                    pre_processing.create_standard_parameter_bus(
                        label=str(cluster) + "_heat_bus",
                        bus_type='building_heat_bus',
                        standard_parameters=standard_parameters)
                    sheets["buses"].set_index("label", inplace=True,
                                              drop=False)

            for i in sink_parameters[3]:
                pre_processing.create_standard_parameter_link(
                    label=str(i[0]) + "_" + str(i[1])
                          + "_heat_building_link",
                    bus_1=str(cluster) + "_heat_bus",
                    bus_2=str(i[1]),
                    link_type="building_hp_elec_link",
                    standard_parameters=standard_parameters)

    buses = sheets["buses"].copy()
    # buses = buses.drop(index="")
    # buses.set_index("label", inplace=True, drop=False)
    for i, j in buses.iterrows():
        if heat_buses_gchps:
            if str(j["label"][:9]) in heat_buses_gchps:
                sheets["buses"] = sheets["buses"].drop(index=j["label"])

