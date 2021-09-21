# TODO umbennen mancher Methoden
# TODO Docstrings schreiben
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
from oemof import solph
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
        return perp_foot[0], perp_foot[1], distance, t[0]
    else:
        return None, None, None, None


def calc_street_lengths(connection_points: list):
    connection_points.sort(key=itemgetter(4))
    results = []
    for point in range(0, len(connection_points)-1):
        lat = (connection_points[point][1]
               + connection_points[point + 1][1]) / 2
        dx = 111.3 * (connection_points[point][2]
                      - connection_points[point + 1][2]) \
            * numpy.cos(numpy.deg2rad(lat))
        dy = 111.3 * (connection_points[point][1]
                      - connection_points[point + 1][1])
        dist = math.sqrt(dx ** 2 + dy ** 2) * 1000
        results.append(["{} - {}".format(connection_points[point][0],
                                         connection_points[point + 1][0]),
                        dist,
                        (connection_points[point][1],
                         connection_points[point][2]),
                        (connection_points[point + 1][1],
                         connection_points[point + 1][2])])
                        
    return results


def create_dict_intersections(streets, pipe_num: int):
    """
    
    :param streets: pandas Dataframe containing the street sections
                    beginning and ending points
    :param pipe_num:
    :type pipe_num: int
    
    """
    road_section_points = {}
    pipe_num += 1
    for j, p in streets.iterrows():
        if not road_section_points:
            road_section_points = {
                "forks-{}".format(pipe_num): [p["lat. 1st intersection"],
                                              p["lon. 1st intersection"]]}
            pipe_num += 1
        if not ([p["lat. 1st intersection"], p["lon. 1st intersection"]]
                in road_section_points.values()):
            road_section_points.update(
                    {"forks-{}".format(pipe_num): [p["lat. 1st intersection"],
                                                   p["lon. 1st intersection"]]
                     })
            pipe_num += 1
        if not ([p["lat. 2nd intersection"], p["lon. 2nd intersection"]]
                in road_section_points.values()):
            road_section_points.update(
                    {"forks-{}".format(pipe_num): [p["lat. 2nd intersection"],
                                                   p["lon. 2nd intersection"]]
                     })
            pipe_num += 1

    for point in road_section_points:
        thermal_network.components["forks"] = \
            thermal_network.components["forks"].append(
                    pd.Series({"id": point[6:],
                               "lat": road_section_points[point][0],
                               "lon": road_section_points[point][1],
                               "component_type": "Fork"
                               }), ignore_index=True)
    return road_section_points, pipe_num
    

def create_connection_points(consumers, streets_dict, results):
    """
        create the entries for the connection points
        :param consumers:
        :type consumers:
        :param streets_dict:
        :type streets_dict:
        :param results:
        :type results:
    """
    consumers = {}
    id = 0
    for num, consumer in consumers.iterrows():
        if consumer['active']:
            if consumer['district heating']:
                # dictionary holding the combination of consumer label
                # and id
                consumers.update({consumer['label']: [id, consumer['input']]})
                label = consumer['label'].split("_")[0]
                logging.info("   Connected {} to district heating network"
                             .format(label))
                results.update({id: []})
                for street in streets_dict:
                    result = ["consumers-{}".format(str(id) + "-fork")]
                    pt_lat, pt_lon, dist, t = \
                        calc_distance([streets_dict[street]["lat-1"],
                                       streets_dict[street]["lon-1"]],
                                      [streets_dict[street]["lat-2"],
                                       streets_dict[street]["lon-2"]],
                                      [float(consumer["lat"]),
                                       float(consumer["lon"])])
                    result.append(pt_lat)
                    result.append(pt_lon)
                    result.append(dist)
                    result.append(t)
                    if result[1] is not None:
                        result.append(street)
                        results[id].append(result)
                if len(results[id]) > 1:
                    # iterate threw the results to find the nearest
                    # point of the calculated points
                    h = 0
                    while h < len(results[id])-1:
                        if results[id][h][3] \
                                > results[id][h+1][3]:
                            results[id].pop(h)
                        else:
                            results[id].pop(h+1)
                        h = 0
                        continue
                # add consumer to thermal network components (dummy
                # because cut from system after creating dhnx components
                thermal_network.components["consumers"] = \
                    thermal_network.components["consumers"].append(
                            pd.Series(data={
                                "id": "consumers-{}".format(id),
                                "lat": float(consumer['lat']),
                                "lon": float(consumer['lon']),
                                "component_type": "Consumer",
                                "P_heat_max": 1}),
                            ignore_index=True)
                id += 1
    if results:
        # create consumers forks pandas Dataframe for thermal network
        for pipe_num in results:
            thermal_network.components["forks"] =\
                thermal_network.components["forks"].append(
                    pd.Series(data={"id": results[pipe_num][0][0][10:-5],
                                    "lat": results[pipe_num][0][1],
                                    "lon": results[pipe_num][0][2],
                                    "component_type": "Fork"}),
                ignore_index=True)
            thermal_network.components["pipes"] = \
                thermal_network.components["pipes"].append(
                        pd.Series(data={"id":
                                        "pipe-{}".format(pipe_num),
                                        "from_node":
                                            "forks-{}".format(
                                                    results[pipe_num]
                                                    [0][0][10:-5]),
                                        "to_node":
                                            results[pipe_num][0][0][:-5],
                                        "length": results[pipe_num][0][3],
                                        "component_type": "Pipe"}),
                        ignore_index=True)
    else:
        pipe_num = 0
    return pipe_num, results, test


def create_supply_line(streets, road_section_points, results):
    pipes = {}
    for j, p in streets.iterrows():
        for point in road_section_points:
            if road_section_points[point] == [p["lat. 1st intersection"],
                                              p["lon. 1st intersection"]]:
                # check if begin of road section is begin or end of another
                road_section = [[point,
                                 p["lat. 1st intersection"],
                                 p["lon. 1st intersection"],
                                 0, 0.0, p['street section name']]]
        # Order Connection points on the currently considered road section
        for result in results:
            if results[result][0][5] == p['street section name']:
                road_section.append(results[result][0])
        for point in road_section_points:
            if road_section_points[point] == [p["lat. 2nd intersection"],
                                              p["lon. 2nd intersection"]]:
                # check if begin of road section is begin or end of another
                road_section.append([point,
                                     p["lat. 2nd intersection"],
                                     p["lon. 2nd intersection"],
                                     0, 1.0, p['street section name']])
        pipes.update(
                {p['street section name']: calc_street_lengths(road_section)})
    
    pipe_num = len(thermal_network.components["pipes"]) + 1
    
    for street in pipes:
        for pipe in pipes[street]:
            ends = pipe[0].split(" - ")
            if "fork" in ends[0] and "consumers" in ends[0]:
                ends[0] = "forks-{}".format(ends[0][10:-5])
            if "fork" in ends[1] and "consumers" in ends[1]:
                ends[1] = "forks-{}".format(ends[1][10:-5])
            thermal_network.components["pipes"] = \
                thermal_network.components["pipes"].append(
                        pd.Series(data={"id": "pipe-{}".format(pipe_num),
                                        "from_node": ends[0],
                                        "to_node": ends[1],
                                        "length": pipe[1],
                                        "component_type": "Pipe"}),
                        ignore_index=True)
            pipe_num += 1


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


def create_components(nodes_data):
    frequence = nodes_data['energysystem']['temporal resolution'].values
    start_date = str(nodes_data['energysystem']['start date'].values[0])
    thermal_network.components["producers"] = \
        thermal_network.components["producers"].append(
                pd.Series({"id": "0", "lat": 51.555, "lon": 7.210,
                           "component_type": "Producer", "active": 1}),
                ignore_index=True)
    pipe_num = len(thermal_network.components['pipes']) + 1
    thermal_network.components['pipes'] = \
        thermal_network.components['pipes'].append(pd.Series(
                {"id": "pipe-{}".format(pipe_num + 1),
                 "from_node": "producers-0", "to_node": "forks-1",
                 "length": 1, "component_type": "Pipe"}),
                ignore_index=True)
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
                                                      "pipes.csv"))}
    }
    oemof_opti_model = \
        optimization.setup_optimise_investment(
                thermal_network=thermal_network,
                invest_options=invest_opt,
                num_ts=nodes_data['energysystem']['periods'],
                start_date=(str(start_date[9:10]) + "/" + str(start_date[6:7])
                            + "/" + str(start_date[0:4])),
                frequence=(str(frequence[0])).upper()
        )
    return oemof_opti_model


def connect_dh_to_system(oemof_opti_model, test, busd):
    sinks = []
    for i in range(len(oemof_opti_model.nodes)):
        if "demand" in str(oemof_opti_model.nodes[i]):
            sinks.append(i)
    already_deleted = 0
    for sink in sinks:
        oemof_opti_model.nodes.pop(sink - already_deleted)
        already_deleted += 1
    # TODO create Link to connect consumers heat bus to dh-system
    for i in test:
        oemof_opti_model.nodes.append(
                solph.custom.Link(
                        label=("link-dhnx-c{}-".format(test[i][0]) + i[:-12]),
                        inputs={
                            oemof_opti_model.buses[
                                dhnx.optimization_oemof_heatpipe.Label(
                                        'consumers', 'heat', 'bus',
                                        'consumers-{}'.format(test[i][0]))]:
                            solph.Flow(),
                            busd[test[i][1]]: solph.Flow()},
                        outputs={
                            busd[test[i][1]]: solph.Flow(),
                            oemof_opti_model.buses[
                                dhnx.optimization_oemof_heatpipe.Label(
                                        'consumers', 'heat', 'bus',
                                        'consumers-{}'.format(test[i][0]))]:
                            solph.Flow()},
                        conversion_factors={
                            (oemof_opti_model.buses[
                                 dhnx.optimization_oemof_heatpipe.Label(
                                         'consumers', 'heat', 'bus',
                                         'consumers-{}'.format(test[i][0]))],
                             busd[test[i][1]]): 1,
                            (busd[test[i][1]],
                             oemof_opti_model.buses[
                                 dhnx.optimization_oemof_heatpipe.Label(
                                         'consumers', 'heat', 'bus',
                                         'consumers-{}'.format(test[i][0]))]
                             ): 0}))
    return oemof_opti_model
    
    
def add_excess_shortage_to_dh(oemof_opti_model, nodes_data, intersections,
                              busd):
    busses = []
    for i, bus in nodes_data['buses'].iterrows():
        if bus["district heating conn."] != 0 and bus["active"] == 1:
            busses.append(bus)
    for bus in busses:
        conn_point = bus['district heating conn.'].split("-")
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
        for key, value in intersections.items():
            if value == [lat, lon]:
                key_parts = key.split("-")
                oemof_opti_model.nodes.append(
                        solph.custom.Link(
                                label=("link-dhnx-" + bus['label']
                                       + "-f{}".format(key_parts[-1])),
                                inputs={
                                    oemof_opti_model.buses[
                                        dhnx.optimization_oemof_heatpipe
                                            .Label('infrastructure',
                                                   'heat', 'bus',
                                                   str(key))]:
                                        solph.Flow(),
                                    busd[bus['label']]: solph.Flow()},
                                outputs={
                                    busd[bus['label']]: solph.Flow(),
                                    oemof_opti_model.buses[
                                        dhnx.optimization_oemof_heatpipe
                                            .Label('infrastructure',
                                                   'heat', 'bus',
                                                   str(key))]:
                                        solph.Flow()},
                                conversion_factors={
                                    (oemof_opti_model.buses[
                                        dhnx.optimization_oemof_heatpipe
                                     .Label('infrastructure', 'heat',
                                            'bus', str(key))],
                                     busd[bus['label']]): 1,
                                    (busd[bus['label']],
                                     oemof_opti_model.buses[
                                         dhnx.optimization_oemof_heatpipe
                                     .Label('infrastructure', 'heat',
                                            'bus', str(key))]): 1}))
                
    return oemof_opti_model


def create_producer_connection_point(streets_dict, nodes_data, pipe_num,
                                     results):
    busses = []
    for i, bus in nodes_data['buses'].iterrows():
        if bus["district heating conn."] == "dh-system" and bus['active'] == 1:
            busses.append(bus)
    ids = {}
    for bus in busses:
        results.update({bus['label']: []})
        for street in streets_dict:
            pt_lat, pt_lon, dist, t = \
                calc_distance([streets_dict[street]["lat-1"],
                               streets_dict[street]["lon-1"]],
                              [streets_dict[street]["lat-2"],
                               streets_dict[street]["lon-2"]],
                              [float(bus["lat"]),
                               float(bus["lon"])])
            result = ["consumers-{}".format(str(pipe_num) + "-fork")]
            result.append(pt_lat)
            result.append(pt_lon)
            result.append(dist)
            result.append(t)
            if result[1] is not None:
                result.append(street)
                results[bus['label']].append(result)
            if len(results[bus['label']]) > 1:
                # iterate threw the results to find the nearest
                # point of the calculated points
                h = 0
                while h < len(results[bus['label']]) - 1:
                    if results[bus['label']][h][3] \
                            > results[bus['label']][h + 1][3]:
                        results[bus['label']].pop(h)
                    else:
                        results[bus['label']].pop(h + 1)
                    h = 0
                    continue
        thermal_network.components["forks"] = \
            thermal_network.components["forks"].append(
                    pd.Series(data={"id": pipe_num,
                                    "lat": results[bus['label']][0][1],
                                    "lon": results[bus['label']][0][2],
                                    "component_type": "Fork"}),
                    ignore_index=True)
        ids.update({bus['label']: "forks-{}".format(pipe_num)})
        pipe_num += 1
    return pipe_num, ids, results

    
def create_producer_connection(oemof_opti_model, ids, busd):
    for key, fork in ids.items():
        oemof_opti_model.nodes.append(
                solph.custom.Link(
                        label=(str(key) + "-dhnx-source-link"),
                        inputs={
                            oemof_opti_model.buses[
                                dhnx.optimization_oemof_heatpipe
                                    .Label('infrastructure',
                                           'heat', 'bus',
                                           str(fork))]:
                                solph.Flow(),
                            busd[key]: solph.Flow()},
                        outputs={
                            busd[key]: solph.Flow(),
                            oemof_opti_model.buses[
                                dhnx.optimization_oemof_heatpipe
                                    .Label('infrastructure',
                                           'heat', 'bus',
                                           str(fork))]:
                                solph.Flow()},
                        conversion_factors={
                            (oemof_opti_model.buses[
                                 dhnx.optimization_oemof_heatpipe
                             .Label('infrastructure', 'heat',
                                    'bus', str(fork))],
                             busd[key]): 1,
                            (busd[key],
                             oemof_opti_model.buses[
                                 dhnx.optimization_oemof_heatpipe
                             .Label('infrastructure', 'heat',
                                    'bus', str(fork))]): 1}))
        
    return oemof_opti_model


def district_heating(nodes_data, nodes, busd):
    global thermal_network
    thermal_network = dhnx.network.ThermalNetwork()
    
    streets_dict = {}
    for j, f in nodes_data['road sections'].iterrows():
        streets_dict.update(
                {f['street section name']: {
                    "lat-1": f["lat. 1st intersection"],
                    "lat-2": f["lat. 2nd intersection"],
                    "lon-1": f["lon. 1st intersection"],
                    "lon-2": f["lon. 2nd intersection"]}})
    if streets_dict != {}:
        # create pipes and connection point for building streets connection
        pipe_num, results, test = create_connection_points(nodes_data['sinks'],
                                                           streets_dict, {})
        
        # creates a dictionary containing the intersection points
        road_section_points, pipe_num = \
            create_dict_intersections(nodes_data['road sections'], pipe_num)

        pipe_num, ids, results = create_producer_connection_point(streets_dict,
                                                                  nodes_data,
                                                                  pipe_num,
                                                                  results)
        
        # create supply line laid on the road
        create_supply_line(nodes_data['road sections'], road_section_points,
                           results)
        
        if thermal_network.components['consumers'].values.any():
            adapt_dhnx_style()
            thermal_network.is_consistent()
            thermal_network.set_timeindex()
            
            # plot network
            # static_map = dhnx.plotting.StaticMap(thermal_network)
            # static_map.draw(background_map=False)
            # plt.title('Given network')
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
            
            # create components of district heating system
            oemof_opti_model = create_components(nodes_data)
            # connect non dh and dh system using links to represent losses
            connect_dh_to_system(oemof_opti_model, test, busd)
            # remove dhnx flows that are not used due to deletion of sinks
            for i in range(len(oemof_opti_model.nodes)):
                outputs = oemof_opti_model.nodes[i].outputs.copy()
                for j in outputs.keys():
                    if ('consumers' in str(j) and 'heat' in str(j)
                            and 'demand' in str(j)):
                        oemof_opti_model.nodes[i].outputs.pop(j)
                        
            oemof_opti_model = \
                add_excess_shortage_to_dh(oemof_opti_model, nodes_data,
                                          road_section_points, busd)
            oemof_opti_model = create_producer_connection(oemof_opti_model,
                                                          ids, busd)
            
            for i in oemof_opti_model.nodes:
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
