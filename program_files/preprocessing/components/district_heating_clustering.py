def connect_clustered_dh_to_system(oemof_opti_model, busd):
    """
        Method which creates links to connect the scenario based
        created sinks to the thermal network components created before.

        :param oemof_opti_model: Oemof model holing thermal network
        :type oemof_opti_model:
        :param busd: dictionary containing scenario buses
        :type busd: dict
    """
    oemof_opti_model = remove_redundant_sinks(oemof_opti_model)
    # create link to connect consumers heat bus to the dh-system
    for num, consumer in thermal_network.components["consumers"].iterrows():
        bus = solph.Bus(label="clustered_consumers_{}".format(consumer["id"]))
        oemof_opti_model.nodes.append(bus)
        busd["clustered_consumers_{}".format(consumer["id"])] = bus
        oemof_opti_model.nodes.append(solph.Transformer(
            label=("pipe-clustered{}-".format(consumer["id"])
                   + str(consumer["length"])),
            inputs={oemof_opti_model.buses[
                dhnx.optimization_oemof_heatpipe.Label(
                    'consumers', 'heat', 'bus',
                    'consumers-{}'.format(consumer["id"]))]:
                    solph.Flow(investment=solph.Investment(
                        ep_costs=float(component_param.loc[
                                           "clustered_consumer_link"]
                                       ["costs"] * consumer["length"]),
                        # TODO calculation of the periodic cost of the
                        #  clustered line is based on the linearization of
                        #  the line due to the iterative approach see
                        #  parameters sheet
                        periodical_constraint_costs=float(
                            component_param.loc[
                                "clustered_consumer_link"]
                            ["constraint costs"]
                            * consumer["length"]),
                        maximum=200 * len(consumer["input"]),
                        minimum=0, existing=0, nonconvex=False))},
            outputs={
                busd["clustered_consumers_{}".format(consumer["id"])]:
                    solph.Flow()
            },
            # TODO Verlust der Hausübergabe Station
            #  15.8689kWh/(m*a) bei 1500 Vollaststunden/a
            conversion_factors={
                busd["clustered_consumers_{}".format(consumer["id"])]:
                    1 - (((15.8689 / 1500) * consumer["length"]) / 24.42)
            }))
        counter = 1
        for consumer_input in consumer["input"]:
            oemof_opti_model.nodes.append(solph.Transformer(
                label="dh_heat_house_station_{}".format(consumer["id"])
                      + "-" + str(consumer_input),
                inputs={
                    busd["clustered_consumers_{}".format(consumer["id"])]:
                        solph.Flow()},
                outputs={busd[consumer_input]: solph.Flow(
                    investment=solph.Investment(
                            ep_costs=float(component_param.loc[
                                               "dh_heatstation"]
                                           ["costs"]),
                            minimum=0,
                            maximum=999 * len(consumer["input"]),
                            existing=0,
                            nonconvex=False))},
                conversion_factors={busd[consumer_input]:
                                    float(component_param.loc[
                                                  "dh_heatstation"]
                                          ["efficiency"])}))
            counter += 1
    return oemof_opti_model


def clustering_dh_network(nodes_data):
    """

    """
    forks = thermal_network.components["forks"].copy()
    pipes = thermal_network.components["pipes"].copy()
    consumers = thermal_network.components["consumers"].copy()
    forks_street = {}
    # put all forks of a given street part to forks_street dict
    for index, street in nodes_data["district heating"].iterrows():
        if street["active"]:
            street_forks = []
            for num, fork in forks.iterrows():
                if fork["street"] == street["street section name"]:
                    street_forks.append(fork["id"])
            forks_street.update({street["street section name"]: street_forks})
    streets_pipe_length = {}
    # get the length of all pipes connecting street part to consumer of
    # a given street part and put them to streets_pipe_length
    for street in forks_street:
        if forks_street[street]:
            num = 0
            for fork in forks_street[street]:
                forks_street[street][num] = "forks-{}".format(fork)
                num += 1
            for num, pipe in pipes.iterrows():
                if pipe["from_node"] in forks_street[street]:
                    if "consumers" in pipe["to_node"]:
                        if street not in streets_pipe_length:
                            streets_pipe_length.update(
                                {street: [[pipe["id"], pipe["from_node"],
                                           pipe["to_node"],
                                           pipe["length"]]]})
                        else:
                            streets_pipe_length[street].append(
                                [pipe["id"], pipe["from_node"],
                                 pipe["to_node"], pipe["length"]])
                        thermal_network.components["pipes"] = \
                            thermal_network.components["pipes"].drop(
                                index=pipe["id"])
    streets_consumer = {}

    # get consumer information of a given street part
    for street in streets_pipe_length:
        counter = 0
        lat = 0
        lon = 0
        inputs = []
        for street_consumer in streets_pipe_length[street]:
            for num, consumer in consumers.iterrows():
                if street_consumer[2] == \
                        "consumers-{}".format(consumer["id"]):
                    counter += 1
                    lat += consumer["lat"]
                    lon += consumer["lon"]
                    inputs.append(consumer["input"])
                    thermal_network.components["consumers"] = \
                        thermal_network.components["consumers"].drop(
                            index=consumer["id"])
        streets_consumer.update({street: [counter, lat, lon, inputs]})
    counter = 0
    # clear pipes Dataframe
    for num, pipe in thermal_network.components["pipes"].iterrows():
        thermal_network.components["pipes"] = \
            thermal_network.components["pipes"].drop(index=num)
    # clear forks Dataframe
    for num, fork in thermal_network.components["forks"].iterrows():
        thermal_network.components["forks"] = \
            thermal_network.components["forks"].drop(index=num)
    thermal_network.components["forks"] = \
        thermal_network.components["forks"].reset_index(drop=True)
    # calc the summed length of consumer pipes of a given street path
    for street in streets_pipe_length:
        length = 0
        for i in streets_pipe_length[street]:
            length += i[3]
        streets_pipe_length.update({street: length})
    street_sections = \
        convert_dh_street_sections_list(
                nodes_data['district heating'].copy())
    # create the clustered consumer and its fork and pipe
    for street in streets_consumer:
        # add consumer to thermal network components (dummy
        # because cut from system after creating dhnx components
        thermal_network.components["consumers"] = \
            pd.concat([thermal_network.components["consumers"],
                       pd.DataFrame([pd.Series(data={
                            "id": "consumers-{}".format(counter),
                            "lat": float(streets_consumer[street][1]
                                         / streets_consumer[street][0]),
                            "lon": float(streets_consumer[street][2]
                                         / streets_consumer[street][0]),
                            "component_type": "Consumer",
                            "P_heat_max": 1,
                            "input": streets_consumer[street][3],
                            "label": "",
                            "street": street,
                            "length": streets_pipe_length[street]})])])
        # calculate the foot point of the new clustered consumer
        foot_point = \
            get_nearest_perp_foot_point(
                {"lat": float(streets_consumer[street][1]
                              / streets_consumer[street][0]),
                 "lon": float(streets_consumer[street][2]
                              / streets_consumer[street][0])},
                street_sections, counter, "consumers")
        # add the pipe to the clustered consumer to the list of pipes
        thermal_network.components["pipes"] = \
            pd.concat([thermal_network.components["pipes"],
                       pd.DataFrame([pd.Series(data={
                           "id": "pipe-{}".format(len(
                            thermal_network.components["pipes"])),
                           "from_node": "forks-{}".format(foot_point[0][10:-5]),
                           "to_node": "consumers-{}".format(counter),
                           "length": foot_point[3], "component_type": "Pipe"})]
                       )])
        # create fork of the new calculated foot point
        create_fork(foot_point, foot_point[0][10:-5])
        counter += 1

    street_sections = \
        convert_dh_street_sections_list(
            nodes_data['district heating'].copy())
    create_intersection_forks(nodes_data['district heating'])
    create_producer_connection_point(nodes_data, street_sections)
    create_supply_line(nodes_data['district heating'])
    adapt_dhnx_style()
