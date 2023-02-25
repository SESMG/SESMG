"""
    Christian Klemm - christian.klemm@fh-muenster.de
"""
import numpy
from program_files.preprocessing.data_preparation \
    import calculate_cluster_means, k_means_parameter_adaption, \
    k_means_timeseries_adaption


def timeseries_averaging(cluster_period: str, days_per_cluster: int,
                         nodes_data: dict, period: str):
    """
        Averages the values of the time series, how many values are
        averaged is defined by the variable clusters.

        :param cluster_period: contains the gui input of the chosen \
            period type (possible entries: hours, days, weeks)
        :type cluster_period: str
        :param days_per_cluster: contains the gui input of the chosen \
            index (possible entries: 1 - 365)
        :type days_per_cluster: int
        :param nodes_data: dictionary containing the excel worksheets
                           from the used scenario workbook
        :type nodes_data: dict
        :param period: defines rather days or weeks were selected
        :type period: str
        
        :raise: - **ValueError** - Error raised if the chosen period \
            is not supported
    """
    if cluster_period == 'hours':
        clusters = 8760 // int(days_per_cluster)
    elif cluster_period == 'days':
        clusters = 365 // int(days_per_cluster)
    elif cluster_period == 'weeks':
        clusters = 52 // int(days_per_cluster)
    else:
        raise ValueError("period chosen not possible")
    
    weather_data = nodes_data['weather data']
    
    if period == 'days':
        periods = int(len(weather_data) / 24)
    elif period == 'weeks':
        periods = int(len(weather_data) / (24 * 7))
    elif period == 'hours':
        periods = int(len(weather_data))
    else:
        raise ValueError("period chosen not possible")
    
    cluster_labels = []
    for i in range(clusters):
        for j in range(periods // clusters):
            cluster_labels.append(i)
    if periods % clusters >= 0:
        for k in range(periods % clusters):
            cluster_labels.append(clusters - 1)
    cluster_labels = numpy.array(cluster_labels)
    
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
    k_means_parameter_adaption(nodes_data, clusters, period)
    
    k_means_timeseries_adaption(nodes_data, clusters, cluster_labels, period)
