"""
    Christian Klemm - christian.klemm@fh-muenster.de
"""
import numpy
from program_files.preprocessing.data_preparation \
    import calculate_cluster_means, variable_costs_date_adaption, \
    timeseries_adaption


def mean_adapt_timeseries_weatherdata(
        clusters: int, cluster_labels: list, period: str, nodes_data: dict
) -> str:
    """
        Using this method, the mean values of the clusters are formed
        and then cost values as well as time series and weather data
        are adjusted to the new data set length.
        
        :param clusters: number of clustered chosen by the user's input
        :type clusters: int
        :param cluster_labels: list holding the cluster labels \
            represented by integers between 0 and (clusters - 1)
        :type cluster_labels: list
        :param period: str holding the user's period decision
        :type period: str
        :param nodes_data: dictionary holding the user' model \
            model definition spreadsheet
        :return: - **variable_cost_factor** (str) - factor that considers the data_preparation_algorithms,
                         can be used to scale the results up for a year
    """
    weather_data = nodes_data["weather data"]
    # Apply the Clusters to the entire weather_dataset
    prep_weather_data = calculate_cluster_means(data_set=weather_data,
                                                cluster_number=clusters,
                                                cluster_labels=cluster_labels,
                                                period=period)

    # Rename columns of the new weather_dataset
    prep_weather_data['timestamp'] = \
        weather_data['timestamp'][:len(prep_weather_data)]

    # Replaces the weather data set in nodes_data by the new one
    nodes_data['weather data'] = prep_weather_data

    # Adapts Other Parameters (despite weather data) of the energy system
    variable_cost_factor = variable_costs_date_adaption(nodes_data=nodes_data,
                                 clusters=clusters,
                                 period=period)

    timeseries_adaption(nodes_data=nodes_data,
                        clusters=clusters,
                        cluster_labels=cluster_labels,
                        period=period)

    return variable_cost_factor


def timeseries_averaging(cluster_period: str, days_per_cluster: int,
                         nodes_data: dict, period: str) -> str:
    """
        Averages the values of the time series, how many values are
        averaged is defined by the variable clusters.

        :param cluster_period: contains the gui input of the chosen \
            period type (possible entries: hours, days, weeks)
        :type cluster_period: str
        :param days_per_cluster: contains the gui input of the chosen \
            index (possible entries: 1 - 365)
        :type days_per_cluster: int
        :param nodes_data: dictionary containing the excel worksheets \
            from the used model definition workbook
        :type nodes_data: dict
        :param period: defines rather days or weeks were selected
        :type period: str
        
        :raise: - **ValueError** - Error raised if the chosen period \
            is not supported

        :return: - **variable_cost_factor** (str) - factor that considers the data_preparation_algorithms,
                     can be used to scale the results up for a year
    """
    # create a local copy of the weather data sheet
    weather_data = nodes_data['weather data']
    
    # calculate the number of clusters based on the timeseries length of
    # the chosen period type divided by one cluster length
    cluster_dict = {"hours": 8760, "days": 365, "weeks": 52}
    try:
        clusters = cluster_dict.get(cluster_period) // int(days_per_cluster)
    except TypeError:
        raise ValueError("Non supported period")
    
    # calculate the number of periods by dividing the weather data
    # length by the hourly time horizon of one hour/day/week
    period_dict = {"hours": 1, "days": 24, "weeks": 168}
    try:
        periods = int(len(weather_data) / period_dict.get(period))
    except TypeError:
        raise ValueError("Non supported period")

    cluster_labels = []
    # iterate threw the amount of clusters
    for cluster_number in range(clusters):
        # append cluster length times cluster number on cluster labels
        for cluster_length in range(periods // clusters):
            cluster_labels.append(cluster_number)
    
    # If there is a remainder when dividing period by clusters, the last
    # cluster number is added to the list of cluster labels again.
    if periods % clusters >= 0:
        for k in range(periods % clusters):
            cluster_labels.append(clusters - 1)
    cluster_labels = numpy.array(cluster_labels)
    
    variable_cost_factor = mean_adapt_timeseries_weatherdata(clusters=clusters,
                                      cluster_labels=cluster_labels,
                                      period=period,
                                      nodes_data=nodes_data)

    return variable_cost_factor
