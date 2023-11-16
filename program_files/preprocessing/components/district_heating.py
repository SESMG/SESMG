"""
    Gregor Becker - gregor.becker@fh-muenster.de
"""
import pandas
import dhnx
from dhnx.plotting import StaticMap
from dhnx.network import ThermalNetwork
import dhnx.optimization.optimization_models as optimization
from program_files.preprocessing.components.district_heating_calculations \
    import *
from program_files.preprocessing.components.district_heating_clustering \
    import *
import program_files.preprocessing.components.district_heating_components \
    as dh_components


def load_thermal_network_data(thermal_net: ThermalNetwork, path: str
                              ) -> ThermalNetwork:
    """
        This function takes a ThermalNetwork instance and a path as
        input. It then reads CSV files for different components
        (consumers, pipes, producers, forks) from the specified path
        and attaches the data to the corresponding components in the
        ThermalNetwork instance. Finally, it returns the modified
        ThermalNetwork.
        
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
    # Loop through comp dataframes (consumers, pipes, producers, forks)
    for dataframe in ["consumers", "pipes", "producers", "forks"]:
        # # Read CSV files for each dataframe and assign them to the
        # respective component in the ThermalNetwork
        thermal_net.components[dataframe] = \
            pandas.read_csv(path + "/" + dataframe + ".csv")
    # Return the modified ThermalNetwork with attached data
    return thermal_net


def save_thermal_network_data(thermal_net: ThermalNetwork, path: str) -> None:
    """
        Method to save the calculated thermal network data.

        :param thermal_net: DHNx ThermalNetwork instance which will be \
            stored within the optimization result folder
        :type thermal_net: ThermalNetwork
        :param path: path where the ThermalNetwork data will be stored.
        :type path: str
    """
    # Loop through comp dataframes (consumers, pipes, producers, forks)
    for dataframe in ["consumers", "pipes", "producers", "forks"]:
        # Save each dataframe to a CSV file in the specified path
        thermal_net.components[dataframe].to_csv(
                path + "/" + dataframe + ".csv")

    
def concat_on_thermal_net_components(comp_type: str, new_dict: dict,
                                     thermal_net: dhnx.network.ThermalNetwork
                                     ) -> dhnx.network.ThermalNetwork:
    """
        Concatenates a new row (component) to the thermal network
        component DataFrames (consumers, producers, forks, etc.) as
        part of several algorithm steps.

        
        :param comp_type: Defines on which thermal net components \
            DataFrame the new dict will be appended.
        :type comp_type: str
        :param new_dict: Holds the information of the new component to \
            be appended on an existing DataFrame.
        :type new_dict: dict
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: dhnx.network.ThermalNetwork
        
        :return: - **thermal_net** (dhnx.network.ThermalNetwork) - \
            updated instance of the DHNx ThermalNetwork
    """
    # Concatenate the new component information to the specified
    # component type DataFrame
    # 1 Existing DataFrame
    # 2 new Component information as DataFrame
    thermal_net.components[comp_type] = pandas.concat(
        [thermal_net.components[comp_type],
         pandas.DataFrame([pandas.Series(data=new_dict)])]
    )
    return thermal_net
    
    
def clear_thermal_net(thermal_net: dhnx.network.ThermalNetwork
                      ) -> dhnx.network.ThermalNetwork:
    """
        Clears the pandas dataframes of the thermal network that might
        consist of old information.
        
        :param thermal_net: DHNx ThermalNetwork instance possibly \
            holding information of an older optimization run
        :type thermal_net: dhnx.network.ThermalNetwork
        
        :return: **thermal_net** (dhnx.network.ThermalNetwork) - \
            cleared instance of the DHNx ThermalNetwork
    """
    # Iterate over the dataframes in thermal_net.components and replace
    # them with empty dataframes
    for dataframe in ["forks", "consumers", "pipes", "producers"]:
        thermal_net.components[dataframe] = pandas.DataFrame()
        
    return thermal_net


def create_dh_map(thermal_net: ThermalNetwork, result_path: str) -> None:
    """
        Within this method the calculated thermal network is plotted as
        a matplotlib pyplot which can be used for verification of the
        perpendicular foot print search as well as the imported data.

        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
        :param result_path: path where the resulting map will be stored
        :type result_path: str
    """
    import matplotlib.pyplot as plt
    static_map = StaticMap(thermal_net).draw(background_map=False)
    plt.title("Given network")
    dh_comps = {
        "forks": [thermal_net.components.forks, "tab:grey"],
        "consumers": [thermal_net.components.consumers, "tab:green"],
        "producers": [thermal_net.components.producers, "tab:red"]
    }
    for index in dh_comps:
        plt.scatter(
            dh_comps[index][0]["lon"],
            dh_comps[index][0]["lat"],
            color=dh_comps[index][1],
            label=index,
            zorder=2.5,
            s=50)
    plt.legend()
    plt.savefig(result_path + "/district_heating.jpeg")
    
    
def remove_sinks_collect_buses(
        oemof_opti_model: optimization.OemofInvestOptimizationModel,
        busd: dict
) -> (optimization.OemofInvestOptimizationModel, dict):
    """
        Within the dhnx algorithm empty sinks are created,
        which are removed in this method.

        :param oemof_opti_model: parameter holding the district \
            heating optimization model
        :type oemof_opti_model: optimization.OemofInvestOptimizationModel
        :param busd: dictionary holding the energy system buses
        :type busd: dict
        
        :return: - **oemof_opti_model** \
            (optimization.OemofInvestOptimizationModel) - dh model \
            without unused sinks
                - **busd** (dict) - As the busd is always handled as \
            a dictionary of all buses within the SESMG, the buses of \
            the heating network are also added.
    """
    sinks = []
    # iterate threw all the energy system nodes
    for i in range(len(oemof_opti_model.nodes)):
        # get demand created bei dhnx and add them to the list "sinks"
        if "demand" in str(oemof_opti_model.nodes[i]):
            sinks.append(i)
        # get buses created bei dhnx and add them to the dict "busd"
        if "bus" in str(oemof_opti_model.nodes[i]):
            busd.update({str(oemof_opti_model.nodes[i].label):
                         oemof_opti_model.nodes[i]})
    # delete the sinks created by the dhnx algorithm and not used
    # within the SESMG generated energy system
    already_deleted = 0
    for sink in sinks:
        oemof_opti_model.nodes.pop(sink - already_deleted)
        already_deleted += 1
    # return the oemof model without the unused sinks as well as the
    # dictionary holding the energy system's buses
    return oemof_opti_model, busd


def adapt_dhnx_style(thermal_net: ThermalNetwork, cluster_dh: bool
                     ) -> ThermalNetwork:
    """
        Brings the created pandas Dataframes to the dhnx style.
        
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
        :param cluster_dh: boolean used to distinguish between a \
            clustered heat network or an un-clustered heat network run
        :type cluster_dh: bool
        
        :return: - **thermal_net** (ThermalNetwork) - DHNx \
            ThermalNetwork instance after style adaption
    """
    if not cluster_dh:
        consumers = thermal_net.components["consumers"]
        consumer_df = consumers.loc[consumers["id"] != type(int)]
        for num, consumer in consumer_df.iterrows():
            thermal_net.components["consumers"].replace(
                to_replace=consumer["id"],
                value=consumer["id"][10:],
                inplace=True
            )
        producers = thermal_net.components["producers"]
        producer_df = producers.loc[producers["id"] != type(int)]
        for num, consumer in producer_df.iterrows():
            thermal_net.components["producers"].replace(
                    to_replace=consumer["id"],
                    value=consumer["id"][10:],
                    inplace=True
            )
        pipes = thermal_net.components["pipes"]
        for num, pipe in pipes.loc[pipes["id"] != type(int)].iterrows():
            thermal_net.components["pipes"].replace(
                to_replace=pipe["id"], value=pipe["id"][5:], inplace=True
            )
        for num, pipe in pipes.iterrows():
            thermal_net.components["pipes"].replace(
                to_replace=pipe["id"], value=str(int(pipe["id"]) - 1),
                inplace=True
            )	
            
    # reset the index on the id column of each DataFrame
    for index in ["consumers", "pipes", "producers", "forks"]:
        thermal_net.components[index].index = \
            thermal_net.components[index]["id"]
    # return the adapted thermal network
    return thermal_net


def filter_pipe_types(pipe_types: pandas.DataFrame, label_5: str,
                      pipe_type: str, active=1) -> pandas.DataFrame:
    """
        Filter pipe types based on given conditions.
    
        :param pipe_types: DataFrame holding pipe types information.
        :type pipe_types: pandas.DataFrame
        :param label_5: Label for filtering based on anergy/exergy.
        :type label_5: str
        :param pipe_type: Pipe type to filter.
        :type pipe_type: str
        :param active: Value for the "active" column, defaults to 1.
        :type active: int, optional
    
        :return: *-* (pandas.DataFrame) - Filtered DataFrame.
    """
    return pipe_types.loc[
        (pipe_types["anergy_or_exergy"] == label_5)
        & (pipe_types[pipe_type] == 1)
        & (pipe_types["active"] == active)
    ]


def create_components(nodes_data: dict, label_5: str,
                      thermal_net: ThermalNetwork
                      ) -> optimization.OemofInvestOptimizationModel:
    """
        Runs dhnx methods for creating thermal network oemof components.
    
        :param nodes_data: dictionary holing model definition sheet \
            information
        :type nodes_data: dict
        :param label_5: str which defines rather the considered \
            network is an exergy net or an anergy net
        :type label_5: bool
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
    
        :return: - **oemof_opti_model** \
            (optimization.OemofInvestOptimizationModel) - model \
            holding dh components
    """
    # Extract relevant data from nodes_data energysystem
    frequency = nodes_data["energysystem"]["temporal resolution"].values
    date = str(nodes_data["energysystem"]["start date"].values[0])
    
    # Rename data columns to fit feedinlib requirements
    name_dc = {"min. investment capacity": "cap_min",
               "max. investment capacity": "cap_max",
               "periodical costs": "capex_pipes",
               "fix investment costs": "fix_costs",
               "periodical constraint costs": "periodical_constraint_costs",
               "fix investment constraint costs": "fix_constraint_costs"}
    nodes_data["pipe types"] = nodes_data["pipe types"].rename(columns=name_dc)

    # Common parameters for consumers and producers
    common_param = {"label_2": "heat", "active": 1, "excess": 0, "shortage": 0}
    
    consumers = {
        "bus": pandas.DataFrame(data=common_param, index=[0]),
        "demand": pandas.DataFrame(
            {"label_2": "heat", "active": 1, "nominal_value": 1}, index=[0]),
    }
    
    producers = {
        "bus": pandas.DataFrame({"Unnamed: 0": 1, **common_param}, index=[0]),
        "source": pandas.DataFrame(
            {"label_2": "heat", "active": 0}, index=[0]),
    }

    pipe_types = nodes_data["pipe types"]
    network = {
        "pipes": filter_pipe_types(pipe_types, label_5, "distribution_pipe"),
        "pipes_houses": filter_pipe_types(pipe_types, label_5, "building_pipe")
    }

    # Extract the day, month, and year for start_date
    start_date = str(date[9:10]) + "/" + str(date[6:7]) + "/" + str(date[0:4])

    # Start dhnx algorithm to create dh components
    oemof_opti_model = optimization.setup_optimise_investment(
        thermal_network=thermal_net,
        invest_options={"consumers": consumers,
                        "producers": producers,
                        "network": network},
        num_ts=nodes_data["energysystem"]["periods"],
        start_date=start_date,
        frequence=(str(frequency[0])).upper(),
        label_5=label_5,
        bidirectional_pipes=True,
    )
    return oemof_opti_model


def add_excess_shortage_to_dh(
        oemof_opti_model: optimization.OemofInvestOptimizationModel,
        nodes_data: dict, busd: dict, thermal_net: ThermalNetwork,
        anergy_or_exergy: bool) -> optimization.OemofInvestOptimizationModel:
    """
        With the help of this method, it is possible to map an external
        heat supply (e.g. from a neighboring heat network) or the
        export to a neighboring heat network.

        :param oemof_opti_model: dh network components
        :type oemof_opti_model: optimization.OemofInvestOptimizationModel
        :param nodes_data: Dataframe containing all components data
        :type nodes_data: pandas.Dataframe
        :param busd: dict containing all buses of the energysystem \
            under investigation
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
                    dh_components.create_link_between_dh_heat_bus_and_excess_shortage_bus(
                        busd=busd,
                        bus=bus,
                        oemof_opti_model=oemof_opti_model,
                        fork_label=fork_label)
                )

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
        :param busd: dictionary containing model definitions' buses
        :type busd: dict
        :param thermal_net: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_net: ThermalNetwork
        :param clustering: used to define rather the spatial \
            clustering algorithm is used or not
        :type clustering: bool
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
    oemof_opti_model = create_components(
        nodes_data=nodes_data,
        label_5="anergy" if anergy_or_exergy else "exergy",
        thermal_net=thermal_net)
    if clustering:
        oemof_opti_model = connect_clustered_dh_to_system(
            oemof_opti_model=oemof_opti_model,
            busd=busd,
            thermal_network=thermal_net,
            nodes_data=nodes_data)
    else:
        oemof_opti_model, busd = dh_components.connect_dh_to_system(
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
    
    oemof_opti_model = dh_components.create_producer_connection(
        oemof_opti_model=oemof_opti_model,
        busd=busd,
        label_5="anergy" if anergy_or_exergy else "exergy",
        thermal_net=thermal_net)
    
    return oemof_opti_model.nodes, busd

    
def use_data_of_already_calculated_thermal_network_data(
        thermal_net: ThermalNetwork, district_heating_path: str,
        cluster_dh: bool, nodes_data: dict, result_path: str
) -> ThermalNetwork:
    """
        By this method it is possible to optimize a thermal network
        without calculating the perpendicular foot points and the
        heat networks's components if the user has specified a folder
        in the GUI where already calculated thermal network data are
        stored. Nevertheless, a subsequent clustering of the thermal
        network is possible even if the calculation has already been
        performed.
        
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
        :param nodes_data: dictionary containing the model \
            definitions' data
        :type nodes_data: dict
        :param result_path: path where the optimization results as \
            well as the district heating calculations will be stored
        :type result_path: str
        
        :return: - **thermal_net** (ThermalNetwork) - Thermal network \
            holding the networks' components which were loaded from \
            the users input path in the GUI
    """
    # load the already calculated network data of a previous
    # optimization
    thermal_net = load_thermal_network_data(thermal_net=thermal_net,
                                            path=district_heating_path)
    # adapt the dataframe structures to the dhnx accepted form
    thermal_net = adapt_dhnx_style(thermal_net=thermal_net,
                                   cluster_dh=True)
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
    result_path: str, cluster_dh: bool, is_anergy: bool
) -> (list, dict):
    """
        The district_heating method represents the main method of heat
        network creation, it is called by the main algorithm to perform
        the preparation to use the dhnx components and finally add them
        to the already existing energy system. It is up to the users to
        choose whether they want to use spatial clustering or not.
    
        :param nodes_data: dictionary containing the model \
            definitions' data
        :type nodes_data: dict
        :param nodes: list which contains the already created components
        :type nodes: list
        :param busd: dictionary containing the model definitions' buses
        :type busd: dict
        :param district_heating_path: Path to a folder in which the \
            calculated heat network information was stored after a \
            one-time connection point search. Entering this parameter \
            in the GUI shortens the calculation time, because the \
            above mentioned search can then be skipped.
        :type district_heating_path: str
        :param result_path: path where the result will be saved
        :type result_path: str
        :param cluster_dh: boolean which defines rather the heat \
            network is clustered spatially or not
        :type cluster_dh: bool
        :param is_anergy: bool which defines rather the \
            considered network is an exergy net (False) or an anergy \
            net (True)
        :type is_anergy: bool
        
        :return: - **nodes** (list) - list containing the energy \
            systems' nodes after the thermal network components were \
            added
    """
    print(is_anergy)
    thermal_net = clear_thermal_net(dhnx.network.ThermalNetwork())

    # Check if saved calculations are distributed ("" no saved data)
    if district_heating_path == "":
        # Check if the model definition includes district heating
        if len(nodes_data["district heating"]) != 0:
            street_sections = convert_dh_street_sections_list(
                nodes_data["district heating"].copy()
            )

            # Create pipes and connection points for building-streets
            # connection
            thermal_net = \
                dh_components.create_connection_consumers_and_producers(
                    data=nodes_data["buses"],
                    road_sections=street_sections,
                    thermal_net=thermal_net,
                    is_consumer=True)
            
            # Append intersections to the thermal network forks
            thermal_net = dh_components.create_intersection_forks(
                street_sec=nodes_data["district heating"],
                thermal_net=thermal_net)

            # Create pipes and connection points for producer-streets
            # connection
            thermal_net = \
                dh_components.create_connection_consumers_and_producers(
                    data=nodes_data["buses"],
                    road_sections=street_sections,
                    thermal_net=thermal_net,
                    is_consumer=False)

            # Create supply line laid on the road
            thermal_net = dh_components.create_supply_line(
                streets=nodes_data["district heating"],
                thermal_net=thermal_net)
            
            # Check if consumers are connected to the thermal network
            if thermal_net.components["consumers"].values.any():
                
                thermal_net = adapt_dhnx_style(thermal_net=thermal_net,
                                               cluster_dh=False)
                
                if cluster_dh:
                    thermal_net = clustering_dh_network(
                        nodes_data=nodes_data,
                        thermal_network=thermal_net)
                    
                # Save calculated thermal network data
                save_thermal_network_data(thermal_net=thermal_net,
                                          path=result_path)
                
                # Create a map of the thermal network
                create_dh_map(thermal_net=thermal_net, result_path=result_path)
    else:
        thermal_net = use_data_of_already_calculated_thermal_network_data(
            thermal_net=thermal_net,
            district_heating_path=district_heating_path,
            cluster_dh=cluster_dh,
            nodes_data=nodes_data,
            result_path=result_path)

    # Check if pipes are present in the thermal network
    if len(thermal_net.components["pipes"]) > 0:
        new_nodes, busd = create_connect_dhnx(
            nodes_data=nodes_data,
            busd=busd,
            clustering=cluster_dh,
            anergy_or_exergy=is_anergy,
            thermal_net=thermal_net)
        for node in new_nodes:
            nodes.append(node)
    return nodes, busd
