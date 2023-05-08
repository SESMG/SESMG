from sympy import Symbol, solve
from pyproj import Transformer
import numpy
import math
import pandas
from operator import itemgetter
import dhnx.optimization.optimization_models as optimization


transf_WGS84_GK = Transformer.from_crs("EPSG:4326", "EPSG:31466")
transf_GK_WGS84 = Transformer.from_crs("EPSG:31466", "EPSG:4326")


def convert_dh_street_sections_list(street_sec: pandas.DataFrame
                                    ) -> pandas.DataFrame:
    """
        Convert street sections Dataframe to Gaussian Kruger (GK)
        to reduce redundancy.

        :param street_sec: Dataframe holding start and end points
                                of the streets under investigation
        :type street_sec: pandas.DataFrame
        :return: **street_sec** (pandas.DataFrame) - holding \
            converted points
    """
    # iterating threw the given street points and converting each active
    # one to EPSG31466
    for num, street in street_sec[street_sec["active"] == 1].iterrows():
        (
            street_sec.at[num, "lat. 1st intersection"],
            street_sec.at[num, "lon. 1st intersection"],
        ) = transf_WGS84_GK.transform(
            street["lat. 1st intersection"], street["lon. 1st intersection"]
        )
        (
            street_sec.at[num, "lat. 2nd intersection"],
            street_sec.at[num, "lon. 2nd intersection"],
        ) = transf_WGS84_GK.transform(
            street["lat. 2nd intersection"], street["lon. 2nd intersection"]
        )
    return street_sec


def calc_perpendicular_distance_line_point(p1: numpy.array, p2: numpy.array,
                                           p3: numpy.array, converted=False
                                           ) -> list:
    """
        Determination of the perpendicular foot point as well as the
        distance between point and straight line.
        The points consist an array e.g [51.5553878, 7.21026385] which
        northern latitude and eastern longitude.

        .. math::
            &
            distance = \sqrt{dx * dx + dy * dy}

        where :math:`dx` and :math:`dy` are defined as:

        .. math::
            dx = 111.3 * cos(lat) * (lon1 - lon2)\\

            lat = (lat1 + lat2) / 2 * 0.01745\\

            dy = 111.3 * (lat1 - lat2)

        lat1, lat2, lon1, lon2: northern latitude, eastern longitude in
        degree

        :param p1: Starting point of the road section
        :type p1: numpy.array
        :param p2: Ending point of the road section
        :type p2: numpy.array
        :param p3:  point of the building under consideration
        :type p3: numpy.array
        :param converted: defines rather the points are given in \
            EPSG 31466 or not
        :type converted: bool
        
        :return: - **-** (list) - list containing the perpendicular \
            foot point longitude [0] and longitude [1] the distance to \
            the distance to the investigated point as well as it's \
            t value which is the relative position on the street section
    """
    # check rather the third point is already converted or not
    if not converted:
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:31466")
        (p3[0], p3[1]) = transformer.transform(p3[0], p3[1])
    house = numpy.array(p3)
    road_part_limit1 = numpy.array(p1)
    road_part_limit2 = numpy.array(p2)
    # Determining the distance via the orthogonality condition
    # Direction vector of the straight line
    vec_direction = road_part_limit2 - road_part_limit1
    t = Symbol("t")
    vec_l = road_part_limit1 + vec_direction * t
    # Determining the distance via the orthogonality condition;
    # Solve with SymPy
    t = solve(numpy.dot(vec_l - house, vec_direction), t)
    if 0 <= t[0] <= 1:
        # pnt 4 is the closest point on the street to the house
        pnt4 = road_part_limit1 + vec_direction * t
        perp_foot = numpy.array([float(pnt4[0]), float(pnt4[1])])
        perp_foot[0], perp_foot[1] = transf_GK_WGS84.transform(
            perp_foot[0], perp_foot[1]
        )
        house[0], house[1] = transf_GK_WGS84.transform(house[0], house[1])
        # arithmetic mean of latitudes
        lat = (perp_foot[0] + house[0]) / 2
        # distance calculation
        dx = 111.3 * (perp_foot[1] - house[1]) * numpy.cos(numpy.deg2rad(lat))
        dy = 111.3 * (perp_foot[0] - house[0])
        distance = math.sqrt(dx**2 + dy**2) * 1000
        return [perp_foot[0], perp_foot[1], distance, t[0]]
    else:
        return []


def get_nearest_perp_foot_point(building: dict, streets: pandas.DataFrame,
                                index: int, building_type: str) -> list:
    """
        Uses the calc_perpendicular_distance_line_point method and
        finds the shortest distance to a road from its results.

        :param building: coordinates of the building under investigation
        :type building: dict
        :param streets: Dataframe holding all street section of the
                        territory under investigation
        :type streets: pandas.Dataframe
        :param index: integer used for unique indexing of the foot points.
        :type index: int
        :param building_type: specifies building type
        :type building_type: str
        :return: - **foot_point** (list) - list containing information \
                    of the perpendicular foot point
    """
    foot_points = []
    (lat, lon) = transf_WGS84_GK.transform(
        float(building["lat"]), float(building["lon"])
    )
    for num, street in streets[streets["active"] == 1].iterrows():
        # calculation of perpendicular foot point if it is within the
        # limits of the route
        perp_foot_point = calc_perpendicular_distance_line_point(
            [street["lat. 1st intersection"], street["lon. 1st intersection"]],
            [street["lat. 2nd intersection"], street["lon. 2nd intersection"]],
            [lat, lon],
            True,
        )
        if perp_foot_point:
            foot_points.append(perp_foot_point + [street["label"]])
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


def calc_street_lengths(connection_points: list) -> list:
    """
        Calculates the distances between the points of a given street
        given as connection_points.

        :param connection_points: list of connection_points on the \
            given street
        :type connection_points: list
        
        :return: **ordered_road_section_points** (list) - list \
            containing all points of a certain street in an ordered \
            sequence
    """
    # sorts the points created on a road piece according to their
    # position on the same
    connection_points.sort(key=itemgetter(4))
    ordered_road_section_points = []
    for point in range(0, len(connection_points) - 1):
        current_point = connection_points[point]
        next_point = connection_points[point + 1]
        # Calculation of the mean latitude
        lat = (current_point[1] + next_point[1]) / 2
        # Calculation of the x distance according to:
        # (lon1 - lon2) * 111.3km * cos(lat)
        dx = (111.3
              * (current_point[2] - next_point[2])
              * numpy.cos(numpy.deg2rad(lat)))
        # Calculation of the y distance according to: (lat1 - lat2) * 111.3km
        dy = 111.3 * (current_point[1] - next_point[1])
        # Calculation of the actual distance and conversion to meters
        distance = math.sqrt(dx**2 + dy**2) * 1000
        # append the calculated distance and the information of the two
        # forks to the list of the ordered_road_section_points
        # Structure of the list
        # 1. Fork_at_the_beginning - Fork at the end
        # 2. calculated distance
        # 3. (lat1, lon1)
        # 4. (lat2, lon2)
        ordered_road_section_points.append(
            ["{} - {}".format(current_point[0], next_point[0]),
             distance,
             (current_point[1], current_point[2]),
             (next_point[1], next_point[2])]
        )

    return ordered_road_section_points


def calc_heat_pipe_attributes(
        oemof_opti_model: optimization.OemofInvestOptimizationModel,
        pipe_types: pandas.DataFrame
) -> optimization.OemofInvestOptimizationModel:
    """
        In this method, the DHNx components, which were created for a
        purely monetary consideration of the heat network, are extended
        by the emissions approach common in the SESMG. For this
        purpose, the length of the component is determined based on the
        component already created, and the emissions caused are then
        calculated based on this length. These are then assigned to the
        investment attribute of the respective pipe section as an
        emission value. Finally, the extended model is returned.
        
        :param oemof_opti_model: DHNx Model containing the thermal \
            network components
        :type oemof_opti_model: \
            optimization.OemofInvestOptimizationModel
        :param pipe_types: DataFrame containing the model definition's \
            pipe types sheet
        :type pipe_types: pandas.DataFrame
        
        :return: - **oemof_opti_model** \
            (optimization.OemofInvestOptimizationModel) - DHNx Model \
            which was extended by the SESMG common emission approach
    """
    # iterate threw all thermal network components
    for a in oemof_opti_model.nodes:
        # check rather the component is not a bus
        if str(type(a)) != "<class 'oemof.solph.network.bus.Bus'>":
            # get the component's pipe type data frame row
            pipe_row = pipe_types.loc[pipe_types["label_3"] == a.label.tag3]
            # if the pipe type is a linear one
            if int(pipe_row["nonconvex"]) == 0:
                # get the components periodical costs
                ep_costs = getattr(
                    a.outputs[list(a.outputs.keys())[0]].investment, "ep_costs"
                )
                # calculate the length by dividing the pipes periodical
                # costs by the specific periodical costs per meter
                length = ep_costs / float(pipe_row["capex_pipes"])

            # if the pipe type is non convex
            else:
                # get the components fix investment costs
                fix_costs = getattr(
                    a.outputs[list(a.outputs.keys())[0]].investment, "offset"
                )
                # calculate the length by dividing the pipes fix
                # investment costs by the specific fix investment costs
                # per meter
                length = fix_costs / float(pipe_row["fix_costs"])
                
            # set the periodical constraint costs which are
            # calculated by the multiplication of length and
            # specific periodical emissions per meter
            setattr(
                a.outputs[list(a.outputs.keys())[0]].investment,
                "periodical_constraint_costs",
                length * float(pipe_row["periodical_constraint_costs"])
            )
            # set the fix investment constraint costs which are
            # calculated by the multiplication of length and
            # specific fix investment emissions per meter
            setattr(
                    a.outputs[list(a.outputs.keys())[0]].investment,
                    "fix_constraint_costs",
                    length * float(pipe_row["fix_constraint_costs"]),
            )
            # since no variable emissions apply it is set to 0 for each
            # direction
            setattr(a.inputs[list(a.inputs.keys())[0]], "emission_factor", 0)
            setattr(a.outputs[list(a.outputs.keys())[0]], "emission_factor", 0)
    
    return oemof_opti_model
