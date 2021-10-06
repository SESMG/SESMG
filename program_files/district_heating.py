# TODO Docstrings zu Ende schreiben
# TODO alternativen zu pyproj suchen da sehr langsam
from operator import itemgetter
import numpy
import math
from sympy import Symbol, solve
from pyproj import Transformer
import pandas as pd
import dhnx
import matplotlib.pyplot as plt
import dhnx.optimization as optimization
import oemof.solph as solph
import os
import logging


def calc_perp_distance_line_point(p1, p2, p3):
    """
        Determination of the perpendicular foot point as well as the
        distance between point and straight line
        p1 - Starting point of the road section
        p2 - Ending point of the road section
        p3 - point of the building under consideration
        Are three geographical points where p1 and p2 represent the
        street as the crow flies and p3 represents the house under
        consideration.
        The points consist an array e.g [51.5553878, 7.21026385] which
        nothern latitude and eastern longitude.
        distance = sqrt(dx * dx + dy * dy)

        distance:
        dx = 111.3 * cos(lat) * (lon1 - lon2)
        lat = (lat1 + lat2) / 2 * 0.01745
        dy = 111.3 * (lat1 - lat2)
        lat1, lat2, lon1, lon2: northern latitude, eastern longitude in degree
    """
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:31466")
    (p1[0], p1[1]) = transformer.transform(p1[0], p1[1])
    (p2[0], p2[1]) = transformer.transform(p2[0], p2[1])
    (p3[0], p3[1]) = transformer.transform(p3[0], p3[1])
    house = numpy.array(p3)
    startstreet = numpy.array(p1)
    endstreet = numpy.array(p2)
    # Determining the distance via the orthogonality condition
    # Direction vector of the straight line
    vecvg = endstreet-startstreet
    t = Symbol("t")
    vec_l = startstreet + vecvg * t
    # Determining the distance via the orthogonality condition;
    # Solve with SymPy
    t = solve(numpy.dot(vec_l - house, vecvg), t)
    if 0 <= t[0] <= 1:
        # pnt 4 is the closest point on the street to the house
        pnt4 = startstreet + vecvg * t
        perp_foot = numpy.array([float(pnt4[0]), float(pnt4[1])])
        transformer1 = Transformer.from_crs("EPSG:31466", "EPSG:4326")
        perp_foot[0], perp_foot[1] = \
            transformer1.transform(perp_foot[0], perp_foot[1])
        house[0], house[1] = transformer1.transform(house[0], house[1])
        lat = (perp_foot[0] + house[0]) / 2
        dx = 111.3*(perp_foot[1]-house[1])*numpy.cos(numpy.deg2rad(lat))
        dy = 111.3*(perp_foot[0]-house[0])
        distance = math.sqrt(dx**2+dy**2)*1000
        return [perp_foot[0], perp_foot[1], distance, t[0]]
    else:
        return []


def get_nearest_perp_foot_point(building, streets, index, building_type):
    """

    """
    foot_points = []
    for num, street in streets.iterrows():
        perp_foot_point = calc_perp_distance_line_point(
                [street["lat. 1st intersection"],
                 street["lon. 1st intersection"]],
                [street["lat. 2nd intersection"],
                 street["lon. 2nd intersection"]],
                [float(building["lat"]),
                 float(building["lon"])])
        if perp_foot_point:
            perp_foot_point.append(street["street section name"])
            foot_points.append(perp_foot_point)
    # check if more than one result was found
    if len(foot_points) > 1:
        # iterate threw the results to find the nearest
        # point of the calculated points
        num = 0
        while num < len(foot_points) - 1:
            if foot_points[num][2] > foot_points[num + 1][2]:
                foot_points.pop(num)
            else:
                foot_points.pop(num + 1)
            num = 0
            continue
    foot_point = [building_type + "-{}".format(str(index)) + "-fork"]
    foot_point.extend(foot_points[0])
    return foot_point


def create_connection_points(consumers, road_sections):
    """
        create the entries for the connection points and adds them to
        thermal network forks, consumers and pipes

        :param consumers: holding nodes_data["sinks"]
        :type consumers: pandas.Dataframe
        :param road_sections: holding nodes_data["road sections"]
        :type road_sections: pandas.Dataframe
    """
    consumer_counter = 0
    for num, consumer in consumers.iterrows():
        if consumer['active']:
            if consumer['district heating']:
                # TODO label of sinks has to be id_...
                label = consumer['label'].split("_")[0]
                foot_point = \
                    get_nearest_perp_foot_point(consumer, road_sections,
                                                consumer_counter, "consumers")
                # add consumer to thermal network components (dummy
                # because cut from system after creating dhnx components
                thermal_network.components["consumers"] = \
                    thermal_network.components["consumers"].append(
                            pd.Series(data={
                                "id": "consumers-{}".format(consumer_counter),
                                "lat": float(consumer['lat']),
                                "lon": float(consumer['lon']),
                                "component_type": "Consumer",
                                "P_heat_max": 1,
                                "input": consumer["input"],
                                "label": consumer["label"]}),
                            ignore_index=True)
                # create consumers forks pandas Dataframe for thermal network
                thermal_network.components["forks"] = \
                    thermal_network.components["forks"].append(
                            pd.Series(data={"id": foot_point[0][10:-5],
                                            "lat": foot_point[1],
                                            "lon": foot_point[2],
                                            "component_type": "Fork",
                                            "street": foot_point[5],
                                            "t": foot_point[4]}),
                            ignore_index=True)
                thermal_network.components["pipes"] = \
                    thermal_network.components["pipes"].append(
                            pd.Series(data={
                                "id": "pipe-{}".format(foot_point[0][10:-5]),
                                "from_node":
                                    "forks-{}".format(foot_point[0][10:-5]),
                                "to_node": foot_point[0][:-5],
                                "length": foot_point[3],
                                "component_type": "Pipe"}),
                            ignore_index=True)
                consumer_counter += 1
                logging.info("   Connected {} to district heating network"
                             .format(label))


def create_intersection_forks(road_sections):
    """
    creates the forks of the scenario given street points
    :param road_sections: pandas Dataframe containing the street sections
                    beginning and ending points
    :type road_sections: pandas.Dataframe
    """
    road_section_points = {}
    fork_num = len(thermal_network.components["forks"])
    for num, street in road_sections.iterrows():
        if not road_section_points:
            road_section_points = {
                "forks-{}".format(fork_num): [street["lat. 1st intersection"],
                                              street["lon. 1st intersection"]]}
            fork_num += 1
        if not ([street["lat. 1st intersection"],
                 street["lon. 1st intersection"]]
                in road_section_points.values()):
            road_section_points.update(
                    {"forks-{}".format(fork_num):
                     [street["lat. 1st intersection"],
                      street["lon. 1st intersection"]]})
            fork_num += 1
        if not ([street["lat. 2nd intersection"],
                 street["lon. 2nd intersection"]]
                in road_section_points.values()):
            road_section_points.update(
                    {"forks-{}".format(fork_num):
                     [street["lat. 2nd intersection"],
                      street["lon. 2nd intersection"]]})
            fork_num += 1
    
    for point in road_section_points:
        thermal_network.components["forks"] = \
            thermal_network.components["forks"].append(
                    pd.Series({"id": point[6:],
                               "lat": road_section_points[point][0],
                               "lon": road_section_points[point][1],
                               "component_type": "Fork"
                               }), ignore_index=True)


def create_producer_connection_point(nodes_data):
    """
    create the entries for the producers  connection points and adds
    them to thermal network forks, producers and pipes
    :param nodes_data:
    :type nodes_data: pandas.Dataframe
    """
    number = 0
    for i, bus in nodes_data['buses'].iterrows():
        if bus["district heating conn."] == "dh-system" and bus['active'] == 1:
            # create a producer buses and its connections point and pipe
            # due to the given lat and lon from buses sheet
            thermal_network.components["producers"] = \
                thermal_network.components["producers"].append(
                        pd.Series({"id": number, "lat": bus["lat"],
                                   "lon": bus["lon"],
                                   "component_type": "Producer", "active": 1}),
                        ignore_index=True)
            foot_point = \
                get_nearest_perp_foot_point(bus, nodes_data["road sections"],
                                            number, "producers")
            thermal_network.components["forks"] = \
                thermal_network.components["forks"].append(pd.Series(data={
                    "id": len(thermal_network.components["forks"]) + 1,
                    "lat": foot_point[1],
                    "lon": foot_point[2],
                    "component_type": "Fork",
                    "bus": bus["label"],
                    "street": foot_point[5],
                    "t": foot_point[4]
                }), ignore_index=True)
            thermal_network.components['pipes'] = \
                thermal_network.components['pipes'].append(pd.Series(data={
                    "id": "pipe-{}".format(
                            len(thermal_network.components['pipes']) + 1),
                    "from_node": "producers-{}".format(number),
                    "to_node": "forks-{}".format(
                            len(thermal_network.components["forks"])),
                    "length": foot_point[3],
                    "component_type": "Pipe"}), ignore_index=True)
            number += 1
            logging.info("   Connected {} to district heating network"
                         .format(bus["label"]))
            
            
def calc_street_lengths(connection_points: list) -> list:
    """
        calculates the distances between the points of a given street
        given as connection_points
        :param connection_points: list of connection_points on the
                                  given street
        :type connection_points: list
    """
    # sorts the points created on a road piece according to their
    # position on the same
    connection_points.sort(key=itemgetter(4))
    ordered_road_section_points = []
    for point in range(0, len(connection_points)-1):
        # Calculation of the mean latitude
        lat = (connection_points[point][1]
               + connection_points[point + 1][1]) / 2
        # Calculation of the x distance according to:
        # (lon1 - lon2) * 111.3km * cos(lat)
        dx = 111.3 * (connection_points[point][2]
                      - connection_points[point + 1][2]) \
            * numpy.cos(numpy.deg2rad(lat))
        # Calculation of the y distance according to: (lat1 - lat2) * 111.3km
        dy = 111.3 * (connection_points[point][1]
                      - connection_points[point + 1][1])
        # Calculation of the actual distance and conversion to meters
        dist = math.sqrt(dx ** 2 + dy ** 2) * 1000
        # append the calculated distance and the information of the two
        # forks to the list of the ordered_road_section_points
        # Structure of the list
        # 1. Fork_at_the_beginning - Fork at the end
        # 2. calculated distance
        # 3. (lat1, lon1)
        # 4. (lat2, lon2)
        ordered_road_section_points.append(
                ["{} - {}".format(connection_points[point][0],
                                  connection_points[point + 1][0]),
                 dist,
                 (connection_points[point][1],
                  connection_points[point][2]),
                 (connection_points[point + 1][1],
                  connection_points[point + 1][2])])
                        
    return ordered_road_section_points


def create_supply_line(streets):
    """
    
    :param streets: road sections Dataframe including the scenario sheet
    :type streets: pandas.Dataframe
    """
    pipes = {}
    for num, street in streets.iterrows():
        road_section = []
        for key, point in thermal_network.components["forks"].iterrows():
            if point["lat"] == street["lat. 1st intersection"] \
                    and point["lon"] == street["lon. 1st intersection"]:
                # check if begin of road section is begin or end of another
                road_section.append([point["id"],
                                     street["lat. 1st intersection"],
                                     street["lon. 1st intersection"],
                                     0, 0.0, street['street section name']])
            if point["lat"] == street["lat. 2nd intersection"] \
                    and point["lon"] == street["lon. 2nd intersection"]:
                # check if begin of road section is begin or end of another
                road_section.append([point["id"],
                                     street["lat. 2nd intersection"],
                                     street["lon. 2nd intersection"],
                                     0, 1.0, street['street section name']])
            if point["street"] == street["street section name"]:
                road_section.append([point["id"], point["lat"], point["lon"],
                                     0, point["t"],
                                     street["street section name"]])
                
        # Order Connection points on the currently considered road section
        pipes.update({street['street section name']:
                      calc_street_lengths(road_section)})
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
            thermal_network.components["pipes"] = \
                thermal_network.components["pipes"].append(pd.Series(data={
                    "id": "pipe-{}".format(
                            len(thermal_network.components["pipes"]) + 1),
                    "from_node": ends[0],
                    "to_node": ends[1],
                    "length": pipe[1],
                    "component_type": "Pipe"}), ignore_index=True)


def adapt_dhnx_style():
    """
        Brings the created dicts to the dhnx style
    """
    for i, p in thermal_network.components["consumers"].iterrows():
        thermal_network.components["consumers"].replace(
                to_replace=p['id'], value=p['id'][10:], inplace=True)
    for i, p in thermal_network.components["pipes"].iterrows():
        thermal_network.components["pipes"].replace(
                to_replace=p['id'], value=p['id'][5:], inplace=True)
    thermal_network.components["consumers"].index = \
        thermal_network.components["consumers"]['id']
    thermal_network.components["forks"].index = \
        thermal_network.components["forks"]['id']
    thermal_network.components["pipes"].index = \
        thermal_network.components["pipes"]['id']
    thermal_network.components["prodcuers"].index = \
        thermal_network.components["prodcuers"]['id']


def create_components(nodes_data):
    """
        runs dhnx methods for creating thermal network oemof components
        :param nodes_data: Dataframe holing scenario sheet information
        :type nodes_data: pd.Dataframe
    """
    frequency = nodes_data['energysystem']['temporal resolution'].values
    start_date = str(nodes_data['energysystem']['start date'].values[0])
    invest_opt = {
        'consumers': {'bus': pd.DataFrame({"label_2": "heat",
                                           "active": 1,
                                           "excess": 0,
                                           "shortage": 0}, index=[0]),
                      'demand': pd.DataFrame({"label_2": "heat",
                                              "active": 1,
                                              "nominal_value": 1}, index=[0])},
        'producers': {'bus': pd.DataFrame({"Unnamed: 0": 1,
                                           "label_2": "heat",
                                           "active": 1,
                                           "excess": 0,
                                           "shortage": 0}, index=[0]),
                      'source': pd.DataFrame({"label_2": "heat",
                                              "active": 0},
                                             index=[0])},
        'network': {'pipes': pd.read_csv(os.path.join("invest_data", "network",
                                                      "pipes.csv"))}}
    oemof_opti_model = \
        optimization.setup_optimise_investment(
                thermal_network=thermal_network,
                invest_options=invest_opt,
                num_ts=nodes_data['energysystem']['periods'],
                start_date=(str(start_date[9:10]) + "/" + str(start_date[6:7])
                            + "/" + str(start_date[0:4])),
                frequence=(str(frequency[0])).upper()
        )
    return oemof_opti_model


def connect_dh_to_system(oemof_opti_model, busd):
    """
        method which creates links to connect the scenario based
        created sinks to the thermal network components created before
        :param oemof_opti_model: Oemof model holing thermal network
        :type oemof_opti_model:
        :param busd: dictionary containing scenario buses
        :type busd: dict
    """
    sinks = []
    for i in range(len(oemof_opti_model.nodes)):
        # get demand created bei dhnx and add them to the list "sinks"
        if "demand" in str(oemof_opti_model.nodes[i]):
            sinks.append(i)
    already_deleted = 0
    for sink in sinks:
        oemof_opti_model.nodes.pop(sink - already_deleted)
        already_deleted += 1
    # create link to connect consumers heat bus to the dh-system
    for num, consumer in thermal_network.components["consumers"].iterrows():
        oemof_opti_model.nodes.append(solph.custom.Link(
                label=("link-dhnx-c{}-".format(consumer["id"])
                       + consumer["label"][:-12]),
                inputs={
                    oemof_opti_model.buses[
                        dhnx.optimization_oemof_heatpipe.Label(
                                'consumers', 'heat', 'bus',
                                'consumers-{}'.format(consumer["id"]))]:
                    solph.Flow(),
                    busd[consumer["input"]]: solph.Flow()},
                outputs={
                    busd[consumer["input"]]: solph.Flow(),
                    oemof_opti_model.buses[
                        dhnx.optimization_oemof_heatpipe.Label(
                                'consumers', 'heat', 'bus',
                                'consumers-{}'.format(consumer["id"]))]:
                    solph.Flow()},
                # TODO Verlust der Hausübergabe Station
                conversion_factors={
                    (oemof_opti_model.buses[
                         dhnx.optimization_oemof_heatpipe.Label(
                                 'consumers', 'heat', 'bus',
                                 'consumers-{}'.format(consumer["id"]))],
                     busd[consumer["input"]]): 1,
                    (busd[consumer["input"]],
                     oemof_opti_model.buses[
                         dhnx.optimization_oemof_heatpipe.Label(
                                 'consumers', 'heat', 'bus',
                                 'consumers-{}'.format(consumer["id"]))]
                     ): 0}))
    return oemof_opti_model
    
    
def add_excess_shortage_to_dh(oemof_opti_model, nodes_data, busd):
    """
        TODO TEST
    """
    busses = []
    for i, bus in nodes_data['buses'].iterrows():
        if bus["district heating conn."] != 0 and bus["active"] == 1 \
                and bus["district heating conn."] != "dh-system":
            busses.append(bus)
    for bus in busses:
        conn_point = bus['district heating conn.'].split("-")
        lat = None
        lon = None
        for i, street in nodes_data['road sections'].iterrows():
            if street['street section name'] == conn_point[0]:
                if conn_point[1] == "1":
                    lat = street["lat. 1st intersection"]
                    lon = street["lon. 1st intersection"]
                elif conn_point[1] == "2":
                    lat = street["lat. 2nd intersection"]
                    lon = street["lon. 2nd intersection"]
                else:
                    raise ValueError("invalid district heating conn.")
        if lat is None or lon is None:
            raise ValueError
        for key, fork in thermal_network.components["forks"].iterrows():
            if fork["lat"] == lat and fork["lon"] == lon:
                oemof_opti_model.nodes.append(solph.custom.Link(
                    label=("link-dhnx-" + bus['label']
                           + "-f{}".format(fork["id"])),
                    inputs={oemof_opti_model.buses[
                            dhnx.optimization_oemof_heatpipe
                                .Label('infrastructure',
                                       'heat', 'bus',
                                       str("forks-{}".format(fork["id"])))]:
                            solph.Flow(),
                            busd[bus['label']]: solph.Flow()},
                    outputs={busd[bus['label']]: solph.Flow(),
                             oemof_opti_model.buses[
                             dhnx.optimization_oemof_heatpipe
                                 .Label('infrastructure',
                                        'heat', 'bus',
                                        str("forks-{}".format(fork["id"])))]:
                             solph.Flow()},
                    conversion_factors={
                        (oemof_opti_model.buses[
                         dhnx.optimization_oemof_heatpipe
                            .Label('infrastructure', 'heat',
                                   'bus', str("forks-{}".format(fork["id"])))],
                         busd[bus['label']]): 1,
                        (busd[bus['label']],
                         oemof_opti_model.buses[
                         dhnx.optimization_oemof_heatpipe
                         .Label('infrastructure', 'heat',
                                'bus', str("forks-{}".format(fork["id"])))]): 1
                    }))
    
    return oemof_opti_model
    
    
def create_producer_connection(oemof_opti_model, busd):
    """

    """
    for key, producer in thermal_network.components["forks"].iterrows():
        if str(producer["bus"]) != "nan":
            oemof_opti_model.nodes.append(solph.custom.Link(
                label=(str(key) + "-dhnx-source-link"),
                inputs={oemof_opti_model.buses[
                        dhnx.optimization_oemof_heatpipe
                        .Label('infrastructure',
                               'heat', 'bus',
                               str("forks-{}".format(producer["id"])))]:
                        solph.Flow(),
                        busd[producer["bus"]]: solph.Flow()},
                outputs={busd[producer["bus"]]: solph.Flow(),
                         oemof_opti_model.buses[
                         dhnx.optimization_oemof_heatpipe
                         .Label('infrastructure',
                                'heat', 'bus',
                                str("forks-{}".format(producer["id"])))]:
                         solph.Flow()},
                # TODO Zirkulationspumpenwirjkungsgrad
                conversion_factors={
                    (oemof_opti_model.buses[
                     dhnx.optimization_oemof_heatpipe
                     .Label('infrastructure', 'heat', 'bus',
                            str("forks-{}".format(producer["id"])))],
                     busd[producer["bus"]]): 0,
                    (busd[producer["bus"]],
                     oemof_opti_model.buses[
                     dhnx.optimization_oemof_heatpipe
                     .Label('infrastructure', 'heat',
                            'bus',
                            str("forks-{}".format(producer["id"])))]): 1}
            ))
            
    return oemof_opti_model


def create_connect_dhnx(nodes_data, busd):
    """

    """
    thermal_network.is_consistent()
    thermal_network.set_timeindex()
    # create components of district heating system
    oemof_opti_model = create_components(nodes_data)
    # connect non dh and dh system using links to represent losses
    connect_dh_to_system(oemof_opti_model, busd)
    # remove dhnx flows that are not used due to deletion of sinks
    for i in range(len(oemof_opti_model.nodes)):
        outputs = oemof_opti_model.nodes[i].outputs.copy()
        for j in outputs.keys():
            if ('consumers' in str(j) and 'heat' in str(j)
                    and 'demand' in str(j)):
                oemof_opti_model.nodes[i].outputs.pop(j)

    oemof_opti_model = \
        add_excess_shortage_to_dh(oemof_opti_model, nodes_data,
                                  busd)
    oemof_opti_model = \
        create_producer_connection(oemof_opti_model, busd)
    return oemof_opti_model.nodes


def district_heating(nodes_data, nodes, busd, district_heating_path,
                     save_dh_calculations, result_path):
    """

    """
    # create global variable which will include all thermal network
    # variables
    global thermal_network
    thermal_network = dhnx.network.ThermalNetwork()
    # check rather saved calculation are distributed
    if district_heating_path == "":
        # check if the scenario includes road sections
        if len(nodes_data["road sections"]) != 0:
            # create pipes and connection point for building-streets connection
            create_connection_points(nodes_data['sinks'],
                                     nodes_data['road sections'])
            
            # appends the intersections to the thermal network forks
            create_intersection_forks(nodes_data['road sections'])
            # create pipes and connection point for producer-streets connection
            create_producer_connection_point(nodes_data)
            # create supply line laid on the road
            create_supply_line(nodes_data['road sections'])

            # if any consumers where connected to the thermal network
            if thermal_network.components['consumers'].values.any():
                adapt_dhnx_style()
                if save_dh_calculations:
                    for i in ["consumers", "pipes", "producers", "forks"]:
                        thermal_network.components[i].to_csv(
                                result_path + "/" + i + ".csv")

                        # TODO Diskutieren plot network
                        static_map = dhnx.plotting.StaticMap(thermal_network)
                        static_map.draw(background_map=False)
                        plt.title('Given network')
                        plt.scatter(
                                thermal_network.components.consumers['lon'],
                                thermal_network.components.consumers['lat'],
                                color='tab:green', label='consumers',
                                zorder=2.5, s=50)
                        plt.scatter(
                                thermal_network.components.producers['lon'],
                                thermal_network.components.producers['lat'],
                                color='tab:red', label='producers', zorder=2.5,
                                s=50)
                        plt.scatter(thermal_network.components.forks['lon'],
                                    thermal_network.components.forks['lat'],
                                    color='tab:grey', label='forks',
                                    zorder=2.5, s=50)
                        plt.text(-2, 32, 'P0', fontsize=14)
                        plt.text(82, 0, 'P1', fontsize=14)
                        plt.legend()
                        plt.show()
    else:
        for i in ["consumers", "pipes", "producers", "forks"]:
            thermal_network.components[i] = \
                pd.read_csv(district_heating_path + "/" + i + ".csv")
        thermal_network.components["consumers"].index = \
            thermal_network.components["consumers"]['id']
        thermal_network.components["forks"].index = \
            thermal_network.components["forks"]['id']
        thermal_network.components["pipes"].index = \
            thermal_network.components["pipes"]['id']
        thermal_network.components["prodcuers"].index = \
            thermal_network.components["prodcuers"]['id']
    new_nodes = create_connect_dhnx(nodes_data, busd)

    for i in new_nodes:
        nodes.append(i)
    return nodes

    # get results
    # results_edges = thermal_network.results.optimization['components']
    # ['pipes']
    # print(results_edges[['from_node', 'to_node', 'hp_type', 'capacity',
    #                     'direction', 'costs', 'losses']])  #
    # print("COMPONENTS")
    # print(thermal_network.results.optimization['components'])
    #
    # print(results_edges[['invest_costs[€]']].sum())
    # print('Objective value: ',
    #      thermal_network.results.optimization['oemof_meta']['objective'])
    
    # assign new ThermalNetwork with invested pipes
    # twn_results = thermal_network
    # twn_results.components['pipes'] = results_edges[
    #    results_edges['capacity'] > 0.001]
    
    # plot invested edges
    # static_map_2 = dhnx.plotting.StaticMap(twn_results)
    # static_map_2.draw(background_map=False)
    # plt.title('Result network')
    # plt.scatter(thermal_network.components.consumers['lon'],
    #            thermal_network.components.consumers['lat'],
    #            color='tab:green', label='consumers', zorder=2.5, s=50)
    # plt.scatter(thermal_network.components.producers['lon'],
    #            thermal_network.components.producers['lat'],
    #            color='tab:red', label='producers', zorder=2.5, s=50)
    # plt.scatter(thermal_network.components.forks['lon'],
    #            thermal_network.components.forks['lat'],
    #            color='tab:grey', label='forks', zorder=2.5, s=50)
    # plt.text(-2, 32, 'P0', fontsize=14)
    # plt.text(82, 0, 'P1', fontsize=14)
    # plt.legend()
    # plt.show()
