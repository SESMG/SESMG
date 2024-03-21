"""
    Gregor Becker - gregor.becker@fh-muenster.de
"""
import logging
import pandas
from oemof import solph
from dhnx.network import ThermalNetwork
import dhnx.optimization.optimization_models as optimization
import dhnx.optimization.oemof_heatpipe as heatpipe
import program_files.preprocessing.components.district_heating \
    as district_heating
import program_files.preprocessing.components.district_heating_calculations \
    as dh_calculations


def create_fork(point: list, label: int, thermal_net: ThermalNetwork, bus=None
                ) -> ThermalNetwork:
    """
        Outsourced from creation algorithm to reduce redundancy.

        :param point: list containing information of the point to be \
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

        :return: - **-** (ThermalNetwork) - DHNx ThermalNetwork \
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
    return district_heating.concat_on_thermal_net_components(
        comp_type="forks", new_dict=fork_dict, thermal_net=thermal_net)


def append_pipe(nodes: list, length: float, street: str,
                thermal_net: ThermalNetwork, is_exergy: bool
                ) -> ThermalNetwork:
    """
        Method which is used to append the heatpipeline specified by
        the method's parameter to the list of pipes
        (thermal_net.components["pipes"]).

        :param nodes: definition of the first and second edge of the \
            heatpipeline to be appended to the list of pipes
        :type nodes: list
        :param length: definition of the length of the heatpipeline to \
            be appended to the list of pipes
        :type length: float
        :param street: definition of the street in which the \
            heatpipeline will be laid
        :type street: str
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork

        :return: - **-** (ThermalNetwork) - DHNx ThermalNetwork \
            instance used to create the components of the thermal \
            network for the energy system. Within this method a new \
            pipe was added.
    """
    # Creating a dictionary representing the new pipe
    pipe_dict = {
        "id": "pipe-{}".format(len(thermal_net.components["pipes"]) + 1),
        "from_node": nodes[0],
        "to_node": nodes[1],
        "length": length,
        "component_type": "Pipe",
        "street": street,
        "is_exergy": is_exergy
    }
    
    # Using the concat_on_thermal_net_components function to add the new
    # pipe to the 'pipes' component
    return district_heating.concat_on_thermal_net_components(
        comp_type="pipes", new_dict=pipe_dict, thermal_net=thermal_net)


def create_intersection_forks(street_sec: pandas.DataFrame,
                              thermal_net: ThermalNetwork) -> ThermalNetwork:
    """
        Creates the forks of the model definition given street points.

        :param street_sec: pandas Dataframe containing the street \
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
    # Dictionary to store unique road section forks
    road_section_forks = {}
    
    # Counter for fork numbering
    fork_num = len(thermal_net.components["forks"])
    
    # create a dictionary containing all street points once
    for num, street in street_sec[street_sec["active"] == 1].iterrows():
        for i in ["1st", "2nd"]:
            point = [street["lat. {} intersection".format(i)],
                     street["lon. {} intersection".format(i)]]
            
            # Check if the point is not already in the dictionary
            if point not in road_section_forks.values():
                
                # Add the point to the dictionary with a unique key
                road_section_forks.update({"forks-{}".format(fork_num): point})
                fork_num += 1
    
    # append all points on forks dataframe of the thermal network
    for point in road_section_forks:
        thermal_net = district_heating.concat_on_thermal_net_components(
                comp_type="forks",
                new_dict={
                    "id": point[6:],
                    "lat": road_section_forks[point][0],
                    "lon": road_section_forks[point][1],
                    "component_type": "Fork",
                },
                thermal_net=thermal_net
        )
    
    return thermal_net


def create_supply_line(streets: pandas.DataFrame,
                       thermal_net: ThermalNetwork,
                       is_exergy: bool) -> ThermalNetwork:
    """
        Acquisition of all points of a route (road sections), order
        itself in ascending order and creation of the lines to link the
        forks.

        :param streets: district heating Dataframe including the \
            model definition sheet
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
    # Iterate through active street sections
    for _, street in streets[streets["active"] == 1].iterrows():
        road_section = []
        
        # Iterate through forks and determine their connection to the
        # street
        for _, point in thermal_net.components["forks"].iterrows():
            for i in ["1st intersection", "2nd intersection"]:
                if (point["lat"] == street["lat. {}".format(i)]
                        and point["lon"] == street["lon. {}".format(i)]):
                    
                    # Check if the point is the beginning or end of the
                    # road section
                    road_section.append(
                            [
                                point["id"],
                                street["lat. {}".format(i)],
                                street["lon. {}".format(i)],
                                0,
                                0.0 if i == "1st intersection" else 1.0,
                                street["label"],
                            ]
                    )
            # Check if the point is on the current street
            if "street" in point and point["street"] == street["label"]:
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
        
        # Order Connection points on the currently considered road
        # section
        pipes.update({street["label"]:
                      dh_calculations.calc_street_lengths(road_section)})
        
    # Iterate through calculated pipes and add them to the thermal
    # network
    for street in pipes:
        for pipe in pipes[street]:
            ends = pipe[0].split(" - ")
            
            # Update pipe ends if they involve forks connected to
            # consumers
            for num in [0, 1]:
                if "fork" in ends[num] and "consumers" in ends[num]:
                    ends[num] = "forks-{}".format(ends[num][10:-5])
                else:
                    ends[num] = "forks-{}".format(ends[num])

            # Append the pipe to the thermal network
            thermal_net = append_pipe(
                    nodes=[ends[0], ends[1]],
                    length=pipe[1],
                    street=street,
                    thermal_net=thermal_net,
                    is_exergy=is_exergy)
    
    return thermal_net


def create_connection_consumers_and_producers(
        data: pandas.DataFrame, road_sections: pandas.DataFrame,
        thermal_net: ThermalNetwork, is_consumer: bool,
        is_exergy: bool) -> ThermalNetwork:
    """
        Create the entries for the connection points and adds them to
        thermal network forks, consumers and pipes.

        NOTE:

              bus label structure for consumers has to be <ID>_...

        :param data: holding nodes_data["buses"]
        :type data: pandas.Dataframe
        :param road_sections: holding nodes_data["district heating"]
        :type road_sections: pandas.Dataframe
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
        :param is_consumer: boolean differentiating consumers and \
            producers
        :type is_consumer: bool

        :return: - **thermal_net** (ThermalNetwork) - DHNx \
            ThermalNetwork instance after attaching of the network's \
            consumers/producers

    """
    counter = 0
    
    net_type = "(exergy)" if is_exergy else "(anergy)"
    # Filter relevant components based on their district heating conn.
    # entries
    if is_consumer:
        dh_components = \
            data[(data["active"] == 1)
                 & (data["district heating conn. {}".format(net_type)] == 1)]
    else:
        dh_components = \
            data[(data["district heating conn. {}".format(net_type)]
                  == "dh-system")
                 & (data["active"] == 1)]
    
    for _, comp in dh_components.iterrows():
        
        # calculate the perpendicular foot point
        foot_point = dh_calculations.get_nearest_perp_foot_point(
                building=comp,
                streets=road_sections,
                index=counter,
                building_type="consumers" if is_consumer else "producers"
        )
        
        comp_id = ("consumers-" + str(counter) if is_consumer
                   else "producers-" + str(counter))
        
        # Create dictionary which will be the new component's series
        # appended on the components dataframe
        # Entries within the **() are only appended in case of the
        # usage of this method for consumers creation process
        entry_dict = {
            "id": comp_id,
            "lat": float(comp["lat"]),
            "lon": float(comp["lon"]),
            "component_type": "Consumer" if is_consumer else "Producer",
            "active": 1,
            **({"existing heathouse station": comp["existing heathouse station"],
                "P_heat_max": 1,
                "input": comp["label"],
                "label": comp["label"],
                "street": foot_point[5],
                "electricity_bus": comp["electricity bus"],
                "flow_temperature": comp["flow temperature"],
                }
               if is_consumer else {})
        }
        
        # Add the calculated entry to the thermal network components
        thermal_net = district_heating.concat_on_thermal_net_components(
                comp_type="consumers" if is_consumer else "producers",
                new_dict=entry_dict,
                thermal_net=thermal_net
        )
        
        # Get the current length of the forks dataframe
        forks_len = len(thermal_net.components["forks"])
        
        # Determine the label for the fork based on the is_consumer bool
        fork_label = foot_point[0][10:-5] if is_consumer else forks_len
        
        # Determine the label based on the is_consumer flag
        label = comp["label"].split("_")[0] if is_consumer else comp["label"]
        
        # Determine the pipe label based on the is_consumer flag
        if is_consumer:
            pipe_label = ["forks-{}".format(foot_point[0][10:-5]),
                          foot_point[0][:-5]]
        else:
            pipe_label = ["producers-{}".format(counter),
                          "forks-{}".format(forks_len)]
        
        # Add the calculated point to the forks DataFrame
        thermal_net = create_fork(
                point=foot_point,
                label=fork_label,
                thermal_net=thermal_net,
                bus=None if is_consumer else comp["label"]
        )
        
        # Add the pipe to connect fork and producer/consumer node
        thermal_net = append_pipe(
                nodes=pipe_label,
                length=foot_point[3],
                street=label,
                thermal_net=thermal_net,
                is_exergy=is_exergy
        )
        counter += 1
        logging.info(
                "\t Connected {} to district heating network".format(label)
        )
    
    return thermal_net


def create_producer_connection(
        oemof_opti_model: optimization.OemofInvestOptimizationModel,
        busd: dict, label_5: str, thermal_net: ThermalNetwork
) -> optimization.OemofInvestOptimizationModel:
    """
        This method creates a transformer that connects the heat
        producer to the thermal network.

        :param oemof_opti_model: dh model created before
        :type oemof_opti_model: optimization.OemofInvestOptimizationModel
        :param busd: dictionary containing the energysystem busses
        :type busd: dict
        :param label_5: str containing the differentiation between \
            exergy (label_5=exergy) and anergy (label5=anergy)
        :type label_5: str
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork

        :return: - **oemof_opti_model** (dhnx.optimization) - dhnx model \
            within the new Transformers
    """
    counter = 0
    forks = thermal_net.components["forks"]

    # Iterate through the producers forks in the thermal network
    for _, producer in forks.loc[forks["bus"].notna()].iterrows():
        
        # Reproducer the Heatpipe fork label of the het network producer
        bus = heatpipe.Label(
            "producers",
            "heat",
            "bus",
            str("producers-{}".format(str(counter))),
            label_5
        )
        
        # Create a unique transformer label
        transformer_label = str(producer["bus"]) + "_dh_source_link_" + label_5
        
        # Add a Transformer component to the optimization model
        oemof_opti_model.nodes.append(
            solph.components.Converter(
                label=transformer_label,
                inputs={busd[producer["bus"]]: solph.Flow(
                        custom_attributes={"emission_factor": 0})},
                outputs={oemof_opti_model.buses[bus]: solph.Flow(
                        custom_attributes={"emission_factor": 0})
                },
                conversion_factors={
                    (oemof_opti_model.buses[bus],
                     busd[producer["bus"]]): 1
                },
            )
        )
        counter += 1
    
    return oemof_opti_model


def connect_dh_to_system_exergy(
        oemof_opti_model: optimization.OemofInvestOptimizationModel,
        busd: dict, pipe_types: pandas.DataFrame, thermal_net: ThermalNetwork
) -> (optimization.OemofInvestOptimizationModel, dict):
    """
        Connects the district heating (DH) system to the main energy
        system model.

        Method which creates links to connect the model definition
        based created sinks to the thermal network components created
        before.

        :param oemof_opti_model: Oemof model holing thermal network
        :type oemof_opti_model: optimization.OemofInvestOptimizationModel
        :param busd: dictionary containing model definitions' buses
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
                 - **busd** (dict) - dict containing the energy \
            system's buses
    """
    # Remove dhnx created sinks and collect dhnx buses (busd)
    oemof_opti_model, busd = district_heating.remove_sinks_collect_buses(
            oemof_opti_model=oemof_opti_model, busd=busd)

    # Calculate heat pipe attributes
    oemof_opti_model = dh_calculations.calc_heat_pipe_attributes(
            oemof_opti_model=oemof_opti_model,
            pipe_types=pipe_types)

    # Create links to connect consumers' heat bus to the DH system
    for num, consumer in thermal_net.components["consumers"].iterrows():
        # Create label for the heat bus of consumers
        label = heatpipe.Label("consumers", "heat", "bus",
                               "consumers-{}".format(consumer["id"]), "exergy")

        # Define inputs and outputs for the Transformer
        inputs = {oemof_opti_model.buses[label]: solph.Flow(
                  custom_attributes={"emission_factor": 0})}
        # get heatstation row from pipe types sheet
        heatstation = pipe_types.query("label_3 == 'dh_heatstation'")

        # get heatstation periodical costs if existing heathouse station
        # is not 1
        ep_costs = (float(heatstation["capex_pipes"].iloc[0])
                    if consumer["existing heathouse station"] == 0 else 0)
        
        # get heatstation periodical emission if existing heathouse
        # station is not 1
        ep_emi = (float(heatstation["periodical_constraint_costs"].iloc[0])
                    if consumer["existing heathouse station"] == 0 else 0)

        outputs = {
            busd[consumer["input"]]: solph.Flow(
                    nominal_value=solph.Investment(
                            ep_costs=ep_costs,
                            maximum=999 * len(consumer["input"]),
                            nonconvex=False,
                            custom_attributes={
                                "fix_constraint_costs": 0,
                                "periodical_constraint_costs": ep_emi},
                    ),
                    custom_attributes={"emission_factor": 0},
            )}
        
        conversion_factors = {
            (label, busd[consumer["input"]]):
                float(heatstation["efficiency"].iloc[0])
        }
        
        # Add a Transformer component to the OemofInvestOptimizationModel
        oemof_opti_model.nodes.append(
                solph.components.Converter(
                        label=("dh_heat_house_station_"
                               + consumer["label"].split("_")[0]),
                        inputs=inputs,
                        outputs=outputs,
                        conversion_factors=conversion_factors
                )
        )
    
    return oemof_opti_model, busd


def connect_dh_to_system_anergy(
        oemof_opti_model: optimization.OemofInvestOptimizationModel,
        busd: dict, pipe_types: pandas.DataFrame, thermal_net: ThermalNetwork,
        network_temp: pandas.Series
) -> (optimization.OemofInvestOptimizationModel, dict):
    """
        Connects the district heating (DH) system to the main energy
        system model.

        Method which creates links to connect the model definition
        based created sinks to the thermal network components created
        before.

        :param oemof_opti_model: Oemof model holing thermal network
        :type oemof_opti_model: optimization.OemofInvestOptimizationModel
        :param busd: dictionary containing model definitions' buses
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
                 - **busd** (dict) - dict containing the energy \
            system's buses
    """
    import \
        oemof.thermal.compression_heatpumps_and_chillers as cmpr_hp_chiller
    # Remove dhnx created sinks and collect dhnx buses (busd)
    oemof_opti_model, busd = district_heating.remove_sinks_collect_buses(
            oemof_opti_model=oemof_opti_model, busd=busd)

    # Calculate heat pipe attributes
    oemof_opti_model = dh_calculations.calc_heat_pipe_attributes(
            oemof_opti_model=oemof_opti_model,
            pipe_types=pipe_types)
    
    # Create links to connect consumers' heat bus to the DH system
    for num, consumer in thermal_net.components["consumers"].iterrows():
        # Create label for the heat bus of consumers
        label = heatpipe.Label("consumers", "heat", "bus",
                               "consumers-{}".format(consumer["id"]), "anergy")
        
        # Define inputs and outputs for the Transformer
        inputs = {oemof_opti_model.buses[label]: solph.Flow(
                  custom_attributes={"emission_factor": 0}),
                  busd[consumer["electricity_bus"]]: solph.Flow(
                  custom_attributes={"emission_factor": 0})}
        
        anergy_hp = pipe_types.loc[pipe_types["label_3"] == "anergy_hp"]
        outputs = {
            busd[consumer["input"]]: solph.Flow(
                    investment=solph.Investment(
                            ep_costs=float(anergy_hp["capex_pipes"]),
                            minimum=0,
                            maximum=999 * len(consumer["input"]),
                            existing=0,
                            nonconvex=False,
                            custom_attributes={
                                "fix_constraint_costs": 0,
                                "periodical_constraint_costs":
                                    float(anergy_hp[
                                              "periodical_constraint_costs"])},
                    ),
                    custom_attributes={"emission_factor": 0},
            )}

        temp_high = [consumer["flow_temperature"]] * len(network_temp)
        # calculation of COPs with set parameters
        cops_hp = cmpr_hp_chiller.calc_cops(
                temp_high=temp_high,
                temp_low=network_temp.to_list(),
                quality_grade=0.6, # TODO
                temp_threshold_icing=3,
                factor_icing=0.8,
                mode="heat_pump",
        )
        
        conversion_factors = {
            oemof_opti_model.buses[label]: [((cop - 1) / cop)
                                            / float(anergy_hp["efficiency"])
                                            for cop in cops_hp],
            busd[consumer["electricity_bus"]]: [1 / cop for cop in cops_hp]
        }
        
        # Add a Transformer component to the OemofInvestOptimizationModel
        oemof_opti_model.nodes.append(
                solph.components.Converter(
                        label=("dh_anergy_hp_"
                               + consumer["label"].split("_")[0]),
                        inputs=inputs,
                        outputs=outputs,
                        conversion_factors=conversion_factors
                )
        )
        
    return oemof_opti_model, busd


def create_link_between_dh_heat_bus_and_excess_shortage_bus(
        busd: dict, bus: pandas.Series,
        oemof_opti_model: optimization.OemofInvestOptimizationModel,
        fork_label: heatpipe.Label) -> solph.components.Link:
    """
        Create the link between the bus which enables the heat
        shortage for the district heating network and the fork of the
        district heating network.

        :param busd: dictionary holding the energy systems' buses
        :type busd: dict
        :param bus: Series holding the shortage bus information
        :type bus: pandas.Series
        :param oemof_opti_model: Oemof model holing thermal network
        :type oemof_opti_model: optimization.OemofInvestOptimizationModel
        :param fork_label: heatpipe label of the fork which will be \
            connected to the shortage bus
        :type fork_label: heatpipe.Label

        :return: - **-** (solph.components.Link) - Link \
            component which connects the shortage bus and the heat \
            network's fork
    """
    # Extract the fork ID from the label
    fork_id = fork_label.tag4.split("-")[-1]

    # Create and return the Oemof solph link connecting the
    # excess/shortage bus with the thermal network fork
    return solph.components.Link(
            label=("link-dhnx-" + bus["label"] + "-f{}".format(fork_id)),
            inputs={
                oemof_opti_model.buses[fork_label]: solph.Flow(
                        custom_attributes={"emission_factor": 0}),
                busd[bus["label"]]: solph.Flow(
                        custom_attributes={"emission_factor": 0}),
            },
            outputs={
                busd[bus["label"]]: solph.Flow(
                        custom_attributes={"emission_factor": 0}),
                oemof_opti_model.buses[fork_label]: solph.Flow(
                        custom_attributes={"emission_factor": 0}),
            },
            conversion_factors={
                (oemof_opti_model.buses[fork_label], busd[bus["label"]]): 1,
                (busd[bus["label"]], oemof_opti_model.buses[fork_label]): 1
            },
    )