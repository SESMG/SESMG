def create_link(label: str, bus_1: str, bus_2: str,
                link_type: str):
    """
        creates a link with standard_parameters, based on the standard
        parameters given in the "standard_parameters" dataset and adds
        it to the "sheets"-output dataset.

        :param label: label, the created link will be given
        :type label: str
        :param bus_1: label, of the first bus
        :type bus_1: str
        :param bus_2: label, of the second bus
        :type bus_2: str
        :param link_type: needed to get the standard parameters of the
                          link to be created
        :type link_type: str
        :param standard_parameters: pandas Dataframe holding the
               information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
    """
    from program_files.urban_district_upscaling.pre_processing \
        import create_standard_parameter_comp
    create_standard_parameter_comp(
        specific_param={'label': label, 'bus1': bus_1, 'bus2': bus_2},
        type="links",
        index="link_type",
        standard_param_name=link_type)


def restructuring_links(sheets_clustering, building, cluster, sink_parameters,
                        sheets):
    # TODO comments
    for i, j in sheets_clustering["links"][sheets_clustering["label"] in sheets["links"].index].iterrows():
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
                create_link(cluster + "pv_central_electricity_link",
                            bus_1=cluster + "_pv_bus",
                            bus_2="central_electricity_bus",
                            link_type="building_pv_central_link")
                if sink_parameters[0] + sink_parameters[1] + sink_parameters[2]:
                    create_link(cluster + "pv_electricity_link",
                                bus_1=cluster + "_pv_bus",
                                bus_2=cluster + "_electricity_bus",
                                link_type="building_pv_central_link")
                sheets["links"].set_index("label", inplace=True, drop=False)
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
                    Link.create_link(
                        "central_naturalgas" + cluster,
                        bus_1="central_naturalgas_bus",
                        bus_2=cluster + "_gas_bus",
                        link_type="central_naturalgas_building_link")
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