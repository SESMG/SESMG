import pandas
import dhnx
from dhnx.plotting import StaticMap
from dhnx.network import ThermalNetwork
import dhnx.optimization.optimization_models as optimization
import logging
from program_files.preprocessing.components.district_heating_calculations \
    import *
from program_files.preprocessing.components.district_heating_clustering \
    import *


def load_thermal_network_data(thermal_net: ThermalNetwork, path: str
                              ) -> ThermalNetwork:
    """
        Method to load already calculated thermal network data.
        
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
        :param path: path where the ThermalNetwork data is stored.
        :type path: str
        
        :return: - **thermal_net** (ThermalNetwork) - DHNX \
            ThermalNetwork instance to which the already existing data \
            was attached.
    """
    for dataframe in ["consumers", "pipes", "producers", "forks"]:
        thermal_net.components[dataframe] = \
            pandas.read_csv(path + "/" + dataframe + ".csv")
    return thermal_net


def save_thermal_network_data(thermal_net: ThermalNetwork, path: str):
    """
        Method to save the calculated thermal network data.

        :param thermal_net: DHNx ThermalNetwork instance which will be \
            stored within the optimization result folder
        :type thermal_net: ThermalNetwork
        :param path: path where the ThermalNetwork data will be stored.
        :type path: str
    """
    for dataframe in ["consumers", "pipes", "producers", "forks"]:
        thermal_net.components[dataframe].to_csv(
                path + "/" + dataframe + ".csv")

    
def concat_on_thermal_net_components(comp_type: str, new_dict: dict,
                                     thermal_net: dhnx.network.ThermalNetwork
                                     ) -> dhnx.network.ThermalNetwork:
    """
        Outsourced the concatenation of a new row (component) to the \
        thermal network component dataframes (consumers, producers, \
        forks etc.) which is part of several algorithm steps.
        
        :param comp_type: defines on which thermal net components \
            DataFrame the new dict will be appended
        :type comp_type: str
        :param new_dict: holds the information of the new component to \
            be appended on an existing DataFrame
        :type new_dict: dict
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: dhnx.network.ThermalNetwork
        
        :return: - **thermal_net** (dhnx.network.ThermalNetwork) - \
            updated instance of the DHNx ThermalNetwork
    """
    # create consumers forks pandas Dataframe for thermal network
    thermal_net.components[comp_type] = pandas.concat(
        [thermal_net.components[comp_type],
         pandas.DataFrame([pandas.Series(data=new_dict)])]
    )
    return thermal_net
    
    
def clear_thermal_net(thermal_net: dhnx.network.ThermalNetwork
                      ) -> dhnx.network.ThermalNetwork:
    """
        Method to clear the pandas dataframes of thermal network
        that might consist of old information.
        
        :param thermal_net: DHNx ThermalNetwork instance possibly \
            holding information of an older optimization run
        :type thermal_net: dhnx.network.ThermalNetwork
        
        :return: - **thermal_net** (dhnx.network.ThermalNetwork) - \
            cleared instance of the DHNx ThermalNetwork
    """
    for dataframe in ["forks", "consumers", "pipes", "producers"]:
        thermal_net.components[dataframe] = pandas.DataFrame()
    return thermal_net


def create_fork(point: list, label: int, thermal_net: ThermalNetwork, bus=None
                ) -> ThermalNetwork:
    """
        Outsourced from creation algorithm to reduce redundancy.
    
        :param point: list containing information of the point to be
                      appended
        :type point: list
        :param label: id of the fork to be created
        :type label: int
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
        :param bus: bus is used for producers forks identification
        :type bus: str
        
        :return: - **None** (ThermalNetwork) - DHNx ThermalNetwork \
            instance on which the new fork was appended.
    """
    # create the fork specific dict based on the parameter data
    fork_dict = {
        "id": label,
        "lat": point[1],
        "lon": point[2],
        "component_type": "Fork",
        "street": point[5],
        "t": point[4],
    }
    # if the bus variable is set append it on the fork dict
    if bus:
        fork_dict.update({"bus": bus})
    # append the fork on the thermal net instance and return it
    return concat_on_thermal_net_components(comp_type="forks",
                                            new_dict=fork_dict,
                                            thermal_net=thermal_net)


def append_pipe(nodes: list, length: float, street: str,
                thermal_net) -> ThermalNetwork:
    """
        Method which is used to append the heatpipeline specified by the
        methods parameter to the list of pipes
        (thermal_net.components["pipes"])
        
        :param nodes: definition of the first and second edge of the \
            heatpipeline to be appended to the list of pipes
        :type nodes: list
        :param length: definition of the length of the heatpipeline to \
            be appended to the list of pipes
        :type length: float
        :param street: defintion of the street in which the \
            heatpipeline will be layed
        :type street: str
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
    """
    pipe_dict = {
        "id": "pipe-{}".format(len(thermal_net.components["pipes"]) + 1),
        "from_node": nodes[0],
        "to_node": nodes[1],
        "length": length,
        "component_type": "Pipe",
        "street": street,
    }
    return concat_on_thermal_net_components("pipes", pipe_dict, thermal_net)


def remove_redundant_sinks(
        oemof_opti_model: optimization.OemofInvestOptimizationModel
) -> optimization.OemofInvestOptimizationModel:
    """
        Within the dhnx algorithm empty sinks are created,
        which are removed in this method.

        :param oemof_opti_model: dh model
        :type oemof_opti_model: optimization.OemofInvestOptimizationModel
        
        :return: **oemof_opti_model** \
            (optimization.OemofInvestOptimizationModel) - dh model \
            without unused sinks
    """
    sinks = []
    # get demand created bei dhnx and add them to the list "sinks"
    for i in range(len(oemof_opti_model.nodes)):
        if "demand" in str(oemof_opti_model.nodes[i]):
            sinks.append(i)
    # delete the created sinks
    already_deleted = 0
    for sink in sinks:
        oemof_opti_model.nodes.pop(sink - already_deleted)
        already_deleted += 1
    # return the oemof model without the unused sinks
    return oemof_opti_model


def create_connection_points(consumers: pandas.DataFrame,
                             road_sections: pandas.DataFrame,
                             thermal_net: ThermalNetwork) -> ThermalNetwork:
    """
        Create the entries for the connection points and adds them to
        thermal network forks, consumers and pipes.
    
        :param consumers: holding nodes_data["sinks"]
        :type consumers: pandas.Dataframe
        :param road_sections: holding nodes_data["district heating"]
        :type road_sections: pandas.Dataframe
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
        
        :return: - **thermal_net** (ThermalNetwork) - DHNx \
            ThermalNetwork instance after attaching of the network's \
            consumers
    """
    consumer_counter = 0
    # locate the DataFrame entries necessary for consumer connections
    dh_consumers = consumers[(consumers["active"] == 1)
                             & (consumers["district heating conn."] == 1)]
    for num, consumer in dh_consumers.iterrows():
        # TODO label of sinks has to be id_...
        label = consumer["label"].split("_")[0] + "1"
        foot_point = get_nearest_perp_foot_point(
            consumer, road_sections, consumer_counter, "consumers"
        )
        # add consumer to thermal network components (dummy
        # because cut from system after creating dhnx components
        thermal_net = concat_on_thermal_net_components(
            comp_type="consumers",
            new_dict={
                "id": "consumers-{}".format(consumer_counter),
                "lat": float(consumer["lat"]),
                "lon": float(consumer["lon"]),
                "component_type": "Consumer",
                "P_heat_max": 1,
                "input": consumer["label"],
                "label": consumer["label"],
                "street": foot_point[5],
            },
            thermal_net=thermal_net
        )
        # add fork of perpendicular foot point to the dataframe
        # of forks
        thermal_net = create_fork(
            point=foot_point,
            label=foot_point[0][10:-5],
            thermal_net=thermal_net)
        # add pipe between the perpendicular foot point and the
        # building to the dataframe of pipes
        thermal_net = append_pipe(
            nodes=["forks-{}".format(foot_point[0][10:-5]),
                   foot_point[0][:-5]],
            length=foot_point[3],
            street=label,
            thermal_net=thermal_net
        )
        consumer_counter += 1
        logging.info("\t Connected {} to district heating "
                     "network".format(label))
    return thermal_net


def create_intersection_forks(street_sec: pandas.DataFrame,
                              thermal_net: ThermalNetwork) -> ThermalNetwork:
    """
        Creates the forks of the scenario given street points.
    
        :param street_sec: pandas Dataframe containing the street
                              sections beginning and ending points
        :type street_sec: pandas.Dataframe
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
        
        :return: - **thermal_net** (ThermalNetwork) - DHNx \
            ThermalNetwork instance after attaching of the network's \
            intersection forks
    """
    road_section_points = {}
    fork_num = len(thermal_net.components["forks"])
    # create a dictionary containing all street points once
    for num, street in street_sec[street_sec["active"] == 1].iterrows():
        for i in ["1st", "2nd"]:
            if [
                street["lat. {} intersection".format(i)],
                street["lon. {} intersection".format(i)],
            ] not in road_section_points.values():
                road_section_points.update(
                    {
                        "forks-{}".format(fork_num): [
                            street["lat. {} intersection".format(i)],
                            street["lon. {} intersection".format(i)],
                        ]
                    }
                )
                fork_num += 1
            
    # append all points on forks dataframe
    for point in road_section_points:
        thermal_net = concat_on_thermal_net_components(
            comp_type="forks",
            new_dict={
                "id": point[6:],
                "lat": road_section_points[point][0],
                "lon": road_section_points[point][1],
                "component_type": "Fork",
            },
            thermal_net=thermal_net
        )
    
    return thermal_net


def create_producer_connection_point(
        buses: pandas.DataFrame, road_sections: pandas.DataFrame,
        thermal_net: ThermalNetwork) -> ThermalNetwork:
    """
        Create the entries for the producers connection points and adds
        them to thermal network forks, producers and pipes
    
        :param buses: pandas DataFrame containing the model definition \
            buses data
        :type buses: pandas.DataFrame ['buses']
        :param road_sections: Dataframe containing the street sections \
            start and end points
        :type road_sections: pandas.Dataframe
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
        
        :return: - **thermal_net** (ThermalNetwork) - DHNx \
            ThermalNetwork instance after attaching of the network's \
            producer connection points
    """
    number = 0
    dh_producers = buses[(buses["district heating conn."] == "dh-system")
                         & (buses["active"] == 1)]
    for i, bus in dh_producers.iterrows():
        # create a producer buses and its connections point and pipe
        # due to the given lat and lon from buses sheet
        thermal_net = concat_on_thermal_net_components(
            comp_type="producers",
            new_dict={
                "id": number,
                "lat": bus["lat"],
                "lon": bus["lon"],
                "component_type": "Producer",
                "active": 1,
            },
            thermal_net=thermal_net
        )
        foot_point = get_nearest_perp_foot_point(
            bus, road_sections, number, "producers"
        )
        thermal_net = create_fork(
            point=foot_point,
            label=len(thermal_net.components["forks"]) + 1,
            thermal_net=thermal_net,
            bus=bus["label"]
        )
        thermal_net = append_pipe(
            nodes=["producers-{}".format(number),
                   "forks-{}".format(len(thermal_net.components["forks"]))],
            length=foot_point[3],
            street=bus["label"],
            thermal_net=thermal_net
        )
        number += 1
        logging.info(
            "\t Connected {} to district heating network".format(bus["label"])
        )
    return thermal_net


def create_supply_line(streets: pandas.DataFrame,
                       thermal_net: ThermalNetwork) -> ThermalNetwork:
    """
        Acquisition of all points of a route (road sections), order
        itself in ascending order and creation of the lines to link the
        forks.
    
        :param streets: district heating Dataframe including the
            scenario sheet
        :type streets: pandas.Dataframe
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
        
        :return: - **thermal_net** (ThermalNetwork) - DHNx \
            ThermalNetwork instance after attaching of the network's \
            supply lines
    """
    pipes = {}
    for num, street in streets[streets["active"] == 1].iterrows():
        road_section = []
        for key, point in thermal_net.components["forks"].iterrows():
            if (
                point["lat"] == street["lat. 1st intersection"]
                and point["lon"] == street["lon. 1st intersection"]
            ):
                # check if begin of road section is begin or end of another
                road_section.append(
                    [
                        point["id"],
                        street["lat. 1st intersection"],
                        street["lon. 1st intersection"],
                        0,
                        0.0,
                        street["label"],
                    ]
                )
            if (
                point["lat"] == street["lat. 2nd intersection"]
                and point["lon"] == street["lon. 2nd intersection"]
            ):
                # check if begin of road section is begin or end of another
                road_section.append(
                    [
                        point["id"],
                        street["lat. 2nd intersection"],
                        street["lon. 2nd intersection"],
                        0,
                        1.0,
                        street["label"],
                    ]
                )
            if "street" in point:
                if point["street"] == street["label"]:
                    road_section.append(
                        [
                            point["id"],
                            point["lat"],
                            point["lon"],
                            0,
                            point["t"],
                            street["label"],
                        ]
                    )

        # Order Connection points on the currently considered road section
        pipes.update({street["label"]: calc_street_lengths(road_section)})

    for street in pipes:
        for pipe in pipes[street]:
            ends = pipe[0].split(" - ")
            if "fork" in ends[0] and "consumers" in ends[0]:
                ends[0] = "forks-{}".format(ends[0][10:-5])
            else:
                ends[0] = "forks-{}".format(ends[0])
            if "fork" in ends[1] and "consumers" in ends[1]:
                ends[1] = "forks-{}".format(ends[1][10:-5])
            else:
                ends[1] = "forks-{}".format(ends[1])
            thermal_net = append_pipe(
                nodes=[ends[0], ends[1]],
                length=pipe[1],
                street=street,
                thermal_net=thermal_net)
    
    return thermal_net


def adapt_dhnx_style(thermal_net: ThermalNetwork) -> ThermalNetwork:
    """
        Brings the created pandas Dataframes to the dhnx style.
        
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
        
        :return: - **thermal_net** (ThermalNetwork) - DHNx \
            ThermalNetwork instance after style adaption
    """
    consumers = thermal_net.components["consumers"]
    consumer_df = consumers.loc[consumers["id"].str.contains("consumers")]
    for num, consumer in consumer_df.iterrows():
        thermal_net.components["consumers"].replace(
            to_replace=consumer["id"], value=consumer["id"][10:], inplace=True
        )
    pipes = thermal_net.components["pipes"]
    for num, pipe in pipes.loc[pipes["id"] != type(int)].iterrows():
        thermal_net.components["pipes"].replace(
            to_replace=pipe["id"], value=pipe["id"][5:], inplace=True
        )
            
    # reset the index on the id column of each DataFrame
    for index in ["consumers", "pipes", "producers", "forks"]:
        thermal_net.components[index].index = \
            thermal_net.components[index]["id"]
    # return the adapted thermal network
    return thermal_net


def create_components(nodes_data: dict, anergy_or_exergy: bool,
                      thermal_net: ThermalNetwork
                      ) -> optimization.OemofInvestOptimizationModel:
    """
        Runs dhnx methods for creating thermal network oemof components.
    
        :param nodes_data: dictionary holing model definition sheet \
            information
        :type nodes_data: dict
        :param anergy_or_exergy: bool which defines rather the \
            considered network is an exergy net (False) or an anergy \
            net (True)
        :type anergy_or_exergy: bool
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
    
        :return: **oemof_opti_model** (dhnx.optimization) - model \
            holding dh components
    """
    frequency = nodes_data["energysystem"]["temporal resolution"].values
    start_date = str(nodes_data["energysystem"]["start date"].values[0])
    # changes names of data columns,
    # so it fits the needs of the feedinlib
    name_dc = {"min. investment capacity": "cap_min",
               "max. investment capacity": "cap_max",
               "periodical costs": "capex_pipes",
               "fix investment costs": "fix_costs",
               "periodical constraint costs": "periodical_constraint_costs",
               "fix investment constraint costs": "fix_constraint_costs"}
    nodes_data["pipe types"] = nodes_data["pipe types"].rename(columns=name_dc)
    
    pipe_types = nodes_data["pipe types"]
    label_5 = "anergy" if anergy_or_exergy else "exergy"
    
    # set standard investment options that do not require user modification
    invest_opt = {
        "consumers": {
            "bus": pandas.DataFrame(
                {"label_2": "heat",
                 "active": 1,
                 "excess": 0,
                 "shortage": 0}, index=[0]
            ),
            "demand": pandas.DataFrame(
                {"label_2": "heat", "active": 1, "nominal_value": 1}, index=[0]
            ),
        },
        "producers": {
            "bus": pandas.DataFrame(
                {
                    "Unnamed: 0": 1,
                    "label_2": "heat",
                    "active": 1,
                    "excess": 0,
                    "shortage": 0,
                },
                index=[0],
            ),
            "source": pandas.DataFrame(
                {"label_2": "heat", "active": 0}, index=[0]),
        },
        "network": {
            "pipes": pipe_types.loc[(pipe_types["anergy_or_exergy"] == label_5)
                                    & (pipe_types["distribution_pipe"] == 1)],
            "pipes_houses": pipe_types.loc[
                (pipe_types["anergy_or_exergy"] == label_5)
                & (pipe_types["building_pipe"] == 1)],
        },
    }
    # start dhnx algorithm to create dh components
    oemof_opti_model = optimization.setup_optimise_investment(
        thermal_network=thermal_net,
        invest_options=invest_opt,
        num_ts=nodes_data["energysystem"]["periods"],
        start_date=(
            str(start_date[9:10])
            + "/"
            + str(start_date[6:7])
            + "/"
            + str(start_date[0:4])
        ),
        frequence=(str(frequency[0])).upper(),
        label_5=label_5
    )
    return oemof_opti_model


def connect_dh_to_system(
        oemof_opti_model: optimization.OemofInvestOptimizationModel,
        busd: dict, pipe_types: pandas.DataFrame, thermal_net: ThermalNetwork
) -> optimization.OemofInvestOptimizationModel:
    """
        Method which creates links to connect the scenario based
        created sinks to the thermal network components created before.

        :param oemof_opti_model: Oemof model holing thermal network
        :type oemof_opti_model:
        :param busd: dictionary containing scenario buses
        :type busd: dict
        :param pipe_types: DataFrame holing the model definition's \
            pipe types sheet information
        :type pipe_types: pandas.DataFrame
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
        
        :return: - **oemof_opti_model** \
            (optimization.OemofInvestOptimizationModel) - oemof dh \
            model within connection to the main model
    """
    oemof_opti_model = remove_redundant_sinks(
        oemof_opti_model=oemof_opti_model)
    oemof_opti_model = calc_heat_pipe_attributes(
        oemof_opti_model=oemof_opti_model,
        pipe_types=pipe_types)
    
    # create link to connect consumers heat bus to the dh-system
    for num, consumer in thermal_net.components["consumers"].iterrows():
        
        label = heatpipe.Label("consumers", "heat", "bus",
                               "consumers-{}".format(consumer["id"]), "exergy")
        
        inputs = {oemof_opti_model.buses[label]: solph.Flow(emission_factor=0)}
        
        heatstation = pipe_types.loc[pipe_types["label_3"] == "dh_heatstation"]
        outputs = {
            busd[consumer["input"]]: solph.Flow(
                investment=solph.Investment(
                    ep_costs=float(heatstation["capex_pipes"]),
                    periodical_constraint_costs=float(
                        heatstation["periodical_constraint_costs"]),
                    minimum=0,
                    maximum=999 * len(consumer["input"]),
                    existing=0,
                    nonconvex=False,
                    fix_constraint_costs=0,
                ),
                emission_factor=0,
            )}
        
        conversion_factors = {
            (label, busd[consumer["input"]]): float(heatstation["efficiency"])
        }
        
        oemof_opti_model.nodes.append(
            solph.Transformer(
                label=("dh_heat_house_station_"
                       + consumer["label"].split("_")[0]),
                inputs=inputs,
                outputs=outputs,
                conversion_factors=conversion_factors
            )
        )
        
    return oemof_opti_model


def connect_anergy_to_system(
        oemof_opti_model: optimization.OemofInvestOptimizationModel,
        busd: dict, pipe_types: pandas.DataFrame, thermal_net: ThermalNetwork
) -> optimization.OemofInvestOptimizationModel:
    """
        Method which creates links to connect the scenario based
        created sinks to the thermal network components created before.

        :param oemof_opti_model: Oemof model holing thermal network
        :type oemof_opti_model:
        :param busd: dictionary containing scenario buses
        :type busd: dict
        :param pipe_types: DataFrame holing the model definition's \
            pipe types sheet information
        :type pipe_types: pandas.DataFrame
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
        
        :return: - **oemof_opti_model** \
            (optimization.OemofInvestOptimizationModel) - oemof dh \
            model within connection to the main model
    """
    import oemof.thermal.compression_heatpumps_and_chillers as cmpr_hp_chiller

    oemof_opti_model = remove_redundant_sinks(
        oemof_opti_model=oemof_opti_model)
    oemof_opti_model = calc_heat_pipe_attributes(
        oemof_opti_model=oemof_opti_model,
        pipe_types=pipe_types)

    # create link to connect consumers heat bus to the dh-system
    for num, consumer in thermal_net.components["consumers"].iterrows():
        # TODO Temperaturen? from pre scenario
        # calculation of COPs with set parameters
        cops_hp = cmpr_hp_chiller.calc_cops(
                temp_high=168 * [60],
                temp_low=168 * [20],
                quality_grade=0.6,
                temp_threshold_icing=2,
                factor_icing=1,
                mode="heat_pump",
        )
        
        label = heatpipe.Label("consumers", "heat", "bus",
                               "consumers-{}".format(consumer["id"]), "anergy")
        # TODO elec bus
        inputs = {busd["ID_electricity_bus"]: solph.Flow(emission_factor=0),
                  oemof_opti_model.buses[label]: solph.Flow(emission_factor=0)}
        
        heat_pump = pipe_types.loc[pipe_types["label_3"] == "dh_heatstation"]
        outputs = {
            busd[consumer["input"]]: solph.Flow(
                investment=solph.Investment(
                    ep_costs=float(heat_pump["costs"]),
                    periodical_constraint_costs=float(
                        heat_pump["constraint costs"]),
                    minimum=0,
                    maximum=999 * len(consumer["input"]),
                    existing=0,
                    nonconvex=False,
                    fix_constraint_costs=0,
                ),
                emission_factor=0,
            )}
    
        conversion_factors = {
            oemof_opti_model.buses[label]: [
                ((cop - 1) / cop) / 1 for cop in cops_hp],
            busd["ID_electricity_bus"]: [1 / cop for cop in cops_hp]
        }
    
        oemof_opti_model.nodes.append(
            solph.Transformer(
                label=("anergy_heat_pump_"
                       + consumer["label"].split("_")[0]),
                inputs=inputs,
                outputs=outputs,
                conversion_factors=conversion_factors
            )
        )

    return oemof_opti_model


def create_link_between_dh_heat_bus_and_excess_shortage_bus(
        busd: dict, bus: pandas.Series,
        oemof_opti_model: optimization.OemofInvestOptimizationModel,
        fork_label: heatpipe.Label):
    """

    """
    # return the oemof solph link which connects the excess/shortage
    # bus with the thermal network fork
    fork_id = fork_label.tag4.split("-")[-1]
    return solph.custom.Link(
        label=("link-dhnx-" + bus["label"] + "-f{}".format(fork_id)),
        inputs={
            oemof_opti_model.buses[fork_label]: solph.Flow(),
            busd[bus["label"]]: solph.Flow(),
        },
        outputs={
            busd[bus["label"]]: solph.Flow(),
            oemof_opti_model.buses[fork_label]: solph.Flow(),
        },
        conversion_factors={
            (oemof_opti_model.buses[fork_label], busd[bus["label"]]): 1,
            (busd[bus["label"]], oemof_opti_model.buses[fork_label]): 1
        },
    )


def add_excess_shortage_to_dh(
        oemof_opti_model: optimization.OemofInvestOptimizationModel,
        nodes_data: dict, busd: dict, thermal_net: ThermalNetwork,
        anergy_or_exergy: bool) -> optimization.OemofInvestOptimizationModel:
    """
        With the help of this method, it is possible to map an external
        heat supply (e.g. from a neighboring heat network) or the export
        to a neighboring heat network.

        :param oemof_opti_model: dh network components
        :type oemof_opti_model: optimization.OemofInvestOptimizationModel
        :param nodes_data: Dataframe containing all components data
        :type nodes_data: pandas. Dataframe
        :param busd: dict containing all buses of the energysystem under
         investigation
        :type busd: dict
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
        :param anergy_or_exergy: bool which defines rather the \
            considered network is an exergy net (False) or an anergy \
            net (True)
        :type anergy_or_exergy: bool
        
        :return: - **oemof_opti_model** \
            (optimization.OemofInvestOptimizationModel) - dh network \
            components + excess and shortage bus
    """
    buses_df = nodes_data["buses"].loc[nodes_data["buses"]["active"] == 1]
    # iterate threw all active buses
    for index, bus in buses_df.iterrows():
        # check for a district heating conn. deviating from 0, 1, and
        # dh-system since the name pattern for excess and/or shortage
        # is <dh-heating-section>-<1/2> second part is for first or
        # second intersection
        if bus["district heating conn."] not in [0, 1, "dh-system"]:
            conn_point = bus["district heating conn."].split("-")
            district_heating_df = nodes_data["district heating"]
            street = district_heating_df.loc[
                (district_heating_df["label"] == conn_point[0])
                & (district_heating_df["active"] == 1)]
            if conn_point[1] == "1":
                lat = float(street["lat. 1st intersection"])
                lon = float(street["lon. 1st intersection"])
            elif conn_point[1] == "2":
                lat = float(street["lat. 2nd intersection"])
                lon = float(street["lon. 2nd intersection"])
            else:
                raise ValueError("invalid district heating conn.")
            
            forks = thermal_net.components["forks"]
            fork_node = forks.loc[(forks["lat"] == lat)
                                  & (forks["lon"] == lon)]
            
            for key, fork in fork_node.iterrows():
                # create dhnx strutured fork label
                label_5 = "anergy" if anergy_or_exergy else "exergy"
                fork_label = heatpipe.Label(
                    "infrastructure",
                    "heat",
                    "bus",
                    str("forks-{}".format(fork["id"])),
                    label_5)
                # run link creation between the fork and the
                # excess/shortage bus
                oemof_opti_model.nodes.append(
                    create_link_between_dh_heat_bus_and_excess_shortage_bus(
                        busd=busd,
                        bus=bus,
                        oemof_opti_model=oemof_opti_model,
                        fork_label=fork_label)
                )

    return oemof_opti_model


def create_producer_connection(
        oemof_opti_model: optimization.OemofInvestOptimizationModel,
        busd: dict, anergy_or_exergy: bool, thermal_net: ThermalNetwork
) -> optimization.OemofInvestOptimizationModel:
    """
        This method creates a link that connects the heat producer to
        the heat network.

        :param oemof_opti_model: dh model created before
        :type oemof_opti_model: optimization.OemofInvestOptimizationModel
        :param busd: dictionary containing the energysystem busses
        :type busd: dict
        :param anergy_or_exergy: bool which defines rather the \
            considered network is an exergy net (False) or an anergy \
            net (True)
        :type anergy_or_exergy: bool
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
        
        :return: - **oemof_opti_model** (dhnx.optimization) - dhnx model \
            within the new Transformers
    """
    counter = 0
    forks = thermal_net.components["forks"]
    for key, producer in forks.loc[forks["bus"].notna()].iterrows():
        label_5 = "anergy" if anergy_or_exergy else "exergy"
        label = heatpipe.Label(
            "producers",
            "heat",
            "bus",
            str("producers-{}".format(str(counter))),
            label_5
        )
        oemof_opti_model.nodes.append(
            solph.Transformer(
                label=(str(producer["bus"]) + "_dh_source_link_" + label_5),
                inputs={busd[producer["bus"]]: solph.Flow(emission_factor=0)},
                outputs={oemof_opti_model.buses[label]: solph.Flow(
                    emission_factor=0)
                },
                conversion_factors={
                    (oemof_opti_model.buses[label], busd[producer["bus"]]): 1
                },
            )
        )
        counter += 1

    return oemof_opti_model


def create_connect_dhnx(nodes_data: dict, busd: dict,
                        thermal_net: ThermalNetwork, clustering=False,
                        anergy_or_exergy=False) -> list:
    """
        At this point, the preparations of the heating network to use
        the dhnx package are completed. For this purpose, it is checked
        whether the given data result in a coherent network, which can
        be optimized in the following.
    
        :param nodes_data: Dataframe containing all components data
        :type nodes_data: pandas.Dataframe
        :param busd: dictionary containing scenario buses
        :type busd: dict
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
        :param clustering: used to define rather the spatial clustering
            algorithm is used or not
        :type clustering
        :param anergy_or_exergy: bool which defines rather the \
            considered network is an exergy net (False) or an anergy \
            net (True)
        :type anergy_or_exergy: bool
        
        :return: - **oemof_opti_model.nodes** (list) - energy system \
            nodes of the created thermal network
    """
    thermal_net.is_consistent()
    thermal_net.set_timeindex()
    # create components of district heating system
    oemof_opti_model = create_components(nodes_data=nodes_data,
                                         anergy_or_exergy=anergy_or_exergy,
                                         thermal_net=thermal_net)
    if clustering:
        oemof_opti_model = connect_clustered_dh_to_system(
            oemof_opti_model=oemof_opti_model,
            busd=busd,
            thermal_network=thermal_net,
            nodes_data=nodes_data)
    else:
        # connect non dh and dh system using links to represent losses
        if anergy_or_exergy:
            oemof_opti_model = connect_anergy_to_system(
                oemof_opti_model=oemof_opti_model,
                busd=busd,
                pipe_types=nodes_data["pipe types"],
                thermal_net=thermal_net)
        else:
            oemof_opti_model = connect_dh_to_system(
                oemof_opti_model=oemof_opti_model,
                busd=busd,
                pipe_types=nodes_data["pipe types"],
                thermal_net=thermal_net)
    # remove dhnx flows that are not used due to deletion of sinks
    for i in range(len(oemof_opti_model.nodes)):
        outputs = oemof_opti_model.nodes[i].outputs.copy()
        for j in outputs.keys():
            if "consumers" in str(j) and "heat" in str(j) \
                    and "demand" in str(j):
                oemof_opti_model.nodes[i].outputs.pop(j)

    oemof_opti_model = add_excess_shortage_to_dh(
        oemof_opti_model=oemof_opti_model,
        nodes_data=nodes_data,
        busd=busd,
        thermal_net=thermal_net,
        anergy_or_exergy=anergy_or_exergy)
    
    oemof_opti_model = create_producer_connection(
        oemof_opti_model=oemof_opti_model,
        busd=busd,
        anergy_or_exergy=anergy_or_exergy,
        thermal_net=thermal_net)
    
    return oemof_opti_model.nodes


def create_dh_map(thermal_net: ThermalNetwork, result_path: str):
    """
        Within this method the calculated thermal network is plotted as
        a matplotlib pyplot which can be used for verification of the
        perpendicular foot print search as well as the imported data.
        
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
        :param result_path: path where the resulting map will be stored
        :type result_path
    """
    import matplotlib.pyplot as plt
    static_map = StaticMap(thermal_net).draw(background_map=False)
    plt.title("Given network")
    components = {
        "forks": [thermal_net.components.forks, "tab:grey"],
        "consumers": [thermal_net.components.consumers, "tab:green"],
        "producers": [thermal_net.components.producers, "tab:red"]
    }
    for index in components:
        plt.scatter(
            components[index][0]["lon"],
            components[index][0]["lat"],
            color=components[index][1],
            label=index,
            zorder=2.5,
            s=50)
    plt.legend()
    plt.savefig(result_path + "/district_heating.jpeg")
    
    
def use_data_of_already_calculated_thermal_network_data(
        thermal_net: ThermalNetwork, district_heating_path: str,
        cluster_dh: bool, nodes_data: dict, result_path: str
) -> ThermalNetwork:
    """
        By this method it is possible to do without a new plumb bob if
        the user has specified a folder in the GUI where already
        calculated thermal network data are stored. Nevertheless, a
        subsequent clustering of the thermal network is possible even
        if the calculation has already been performed.
        
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
        :param district_heating_path: string of the path where the \
            already calculated thermal network data is stored
        :type district_heating_path: str
        :param cluster_dh: boolean which decides rather the thermal \
            network will be clustered or not
        :type cluster_dh: bool
        :param nodes_data: dictionary containing the scenario data
        :type nodes_data: dict
        :param result_path: path where the optimization results as \
            well as the district heating calculations will be stored
        :type result_path: str
    """
    # load the already calculated network data of a previous
    # optimization
    thermal_net = load_thermal_network_data(thermal_net=thermal_net,
                                            path=district_heating_path)
    # adapt the dataframe structures to the dhnx accepted form
    thermal_net = adapt_dhnx_style(thermal_net=thermal_net)
    # if the user has chosen the clustering of the thermal network
    # within the GUI it is triggered here
    if cluster_dh:
        thermal_net = clustering_dh_network(nodes_data=nodes_data,
                                            thermal_network=thermal_net)
    # save the calculated thermal network data within the optimization
    # result path
    save_thermal_network_data(thermal_net=thermal_net, path=result_path)
    return thermal_net


def district_heating(
    nodes_data: dict, nodes: list, busd: dict, district_heating_path: str,
    result_path: str, cluster_dh: bool, anergy_or_exergy: bool
):
    """
        The district_heating method represents the main method of heat
        network creation, it is called by the main algorithm to perform
        the preparation to use the dhnx components and finally add them
        to the already existing energy system. It is up to the users to
        choose whether they want to use spatial clustering or not.
    
        :param nodes_data: dictionary containing the scenario data
        :type nodes_data: dict
        :param nodes: list which contains the already created components
        :type nodes: list
        :param busd: dictionary containing the scenario buses
        :type busd: dict
        :param district_heating_path: Path to a folder in which the
            calculated heat network information was stored after a
            one-time connection point search. Entering this parameter in
            the GUI shortens the calculation time, because the above
            mentioned search can then be skipped.
        :type district_heating_path: str
        :param result_path: path where the result will be saved
        :type result_path: str
        :param cluster_dh: boolean which defines rather the heat network
            is clustered spatially or not
        :type cluster_dh: bool
        :param anergy_or_exergy: bool which defines rather the \
            considered network is an exergy net (False) or an anergy \
            net (True)
        :type anergy_or_exergy: bool
    """
    thermal_net = clear_thermal_net(dhnx.network.ThermalNetwork())
    # check rather saved calculation are distributed
    if district_heating_path == "":
        # check if the scenario includes district heating
        if len(nodes_data["district heating"]) != 0:
            street_sections = convert_dh_street_sections_list(
                nodes_data["district heating"].copy()
            )
            # create pipes and connection point for building-streets connection
            thermal_net = create_connection_points(
                consumers=nodes_data["buses"],
                road_sections=street_sections,
                thermal_net=thermal_net)
            # appends the intersections to the thermal network forks
            thermal_net = create_intersection_forks(
                street_sec=nodes_data["district heating"],
                thermal_net=thermal_net)
            # create pipes and connection point for producer-streets connection
            thermal_net = create_producer_connection_point(
                buses=nodes_data["buses"],
                road_sections=street_sections,
                thermal_net=thermal_net)
            # create supply line laid on the road
            thermal_net = create_supply_line(
                streets=nodes_data["district heating"],
                thermal_net=thermal_net)
            # if any consumers where connected to the thermal network
            if thermal_net.components["consumers"].values.any():
                thermal_net = adapt_dhnx_style(thermal_net=thermal_net)
                # save the created dataframes to improve runtime of a
                # second optimization run
                save_thermal_network_data(thermal_net=thermal_net,
                                          path=result_path)
                # create a map of the created thermal network
                create_dh_map(thermal_net=thermal_net, result_path=result_path)
    else:
        thermal_net = use_data_of_already_calculated_thermal_network_data(
            thermal_net=thermal_net,
            district_heating_path=district_heating_path,
            cluster_dh=cluster_dh,
            nodes_data=nodes_data,
            result_path=result_path)
    if len(thermal_net.components["pipes"]) > 0:
        if cluster_dh == 1:
            new_nodes = create_connect_dhnx(nodes_data=nodes_data,
                                            busd=busd,
                                            clustering=True,
                                            anergy_or_exergy=anergy_or_exergy,
                                            thermal_net=thermal_net)
        else:
            new_nodes = create_connect_dhnx(nodes_data=nodes_data,
                                            busd=busd,
                                            clustering=False,
                                            anergy_or_exergy=anergy_or_exergy,
                                            thermal_net=thermal_net)
        for node in new_nodes:
            nodes.append(node)
    return nodes
