"""
    Christian Klemm - christian.klemm@fh-muenster.de
"""
from sklearn.cluster import KMeans
from sklearn_extra.cluster import KMedoids
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import KNeighborsClassifier

from program_files.preprocessing.data_preparation \
    import calculate_cluster_means, append_timeseries_to_weatherdata_sheet,\
    variable_costs_date_adaption, extract_single_periods, \
    timeseries_adaption


def calculate_k_means_clusters(cluster_number: int, weather_data: dict,
                               cluster_criterion: str, period: str):
    """
        Applies the k-means algorithm to a list of day-weather-vectors.
        Caution: weather data set must be available in hourly resolution!

        :param cluster_number: Number of k-mean-clusters
        :type cluster_number: int
        :param weather_data: weather_data, the clusters should be applied to
        :type weather_data: dict
        :param cluster_criterion: weather_parameter/column name which
            should be applied as cluster criterion
        :type cluster_criterion: str
        :param period: defines rather days or weeks were selected
        :type period: str

        :return: - **model.labels_** - Chronological list, which days of the
            weather data set belongs to which cluster

    """
    cluster_vectors = extract_single_periods(data_set=weather_data,
                                             column_name=cluster_criterion,
                                             period=period)
    kmeans = KMeans(n_clusters=cluster_number)
    model = kmeans.fit(cluster_vectors)
    return model.labels_


def calculate_k_medoids_clusters(cluster_number: int, weather_data: dict,
                                 cluster_criterion: str, period: str):
    """
        Applies the k-medoids algorithm to a list of day-weather-vectors.
        Caution: weather data set must be available in hourly resolution!

        :param cluster_number: Number of k-mean-clusters
        :type cluster_number: int
        :param weather_data: weather_data, the clusters should be applied to
        :type weather_data: dict
        :param cluster_criterion: weather_parameter/column name which
            should be applied as cluster criterion
        :type cluster_criterion: str
        :param period: defines rather days or weeks were selected
        :type period: str

        :return: - **model.labels_** - Chronological list, which days of the
            weather data set belongs to which cluster

    """
    cluster_vectors = extract_single_periods(data_set=weather_data,
                                             column_name=cluster_criterion,
                                             period=period)
    kmedoids = KMedoids(n_clusters=cluster_number)
    model = kmedoids.fit(cluster_vectors)
    return model.labels_


def k_medoids_timeseries_adaption(nodes_data: dict, clusters: int,
                                  cluster_labels, period: str):
    """
        TODO missing
        :param nodes_data: system parameters
        :type nodes_data: dict
        :param clusters: Number of clusters
        :type clusters: int
        :param cluster_labels: Chronological list, which days of the weather
                               data set belongs to which cluster

        :type cluster_labels: np.array
        :param period: defines rather hours, days or weeks were selected
        :type period: str

    """
    prep_timeseries = \
        calculate_cluster_means(data_set=nodes_data['timeseries'].copy(),
                                cluster_number=clusters,
                                cluster_labels=cluster_labels,
                                period=period)
    clusters = len(nodes_data["timeseries"]) // len(nodes_data["weather data"])
    # Rename columns of the new timeseries-dataset
    if period == 'hours':
        prep_timeseries['timestamp'] = \
            nodes_data['timeseries']['timestamp'][
            :int(len(nodes_data['timeseries']))]
    elif period == 'days':
        prep_timeseries['timestamp'] = \
            nodes_data['timeseries']['timestamp'][
            :int(len(nodes_data['timeseries']) / clusters)]
    elif period == 'weeks':
        prep_timeseries['timestamp'] = \
            nodes_data['timeseries']['timestamp'][
            :int(len(nodes_data['timeseries']))]  # / (clusters * 7))]
    nodes_data['timeseries'] = prep_timeseries
    nodes_data['weather data'] = prep_timeseries


def k_means_algorithm(cluster_period: int, days_per_cluster: int,
                      criterion: str, nodes_data: dict, period: str):
    """
        TODO missing
        
        :param cluster_period: contains the gui input of the chosen \
            period type (possible entries: days, weeks)
        :type cluster_period: str
        :param days_per_cluster: contains the gui input of the chosen \
            index (possible entries: 1 - 365)
        :type days_per_cluster: int
        :param criterion: criterion chosen for k_mean algorithm
        :type criterion: str
        :param nodes_data: dictionary containing the excel worksheets from
                           the used scenario workbook

        :type nodes_data: dict
        :param period: defines rather days or weeks were selected
        :type period: str
        
        :raise: - **ValueError** - Error raised if the chosen period \
            is not supported
    """
    if cluster_period == 'days':
        clusters = 365 // int(days_per_cluster)
    elif cluster_period == 'weeks':
        clusters = 52 // int(days_per_cluster)
    else:
        raise ValueError("period chosen not possible")
    # Merge the timeseries and weather data sets, sothat that all timeseries'
    # get clustered within one step
    nodes_data['timeseries'] = append_timeseries_to_weatherdata_sheet(
        nodes_data)
    weather_data = nodes_data['timeseries'].copy()
    
    # # depending on the chosen criterion rather the timeseries or the
    # # weather data sheet is selected for the following preparation
    # if criterion == 'el_demand_sum' or criterion == 'heat_demand_sum':
    #     weather_data = nodes_data['timeseries'].copy()
    # else:
    #     weather_data = nodes_data['weather data'].copy()
    
    # Calculate k-mean clusters, based on the cluster_criterion
    cluster_labels = calculate_k_means_clusters(cluster_number=clusters,
                                                weather_data=weather_data,
                                                cluster_criterion=criterion,
                                                period=period)
    
    weather_data = nodes_data['weather data'].copy()
    
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
    variable_costs_date_adaption(nodes_data, clusters, period)
    timeseries_adaption(nodes_data, clusters, cluster_labels, period)
    
    
def k_medoids_algorithm(cluster_period: int, days_per_cluster: int,
                        criterion: str, nodes_data: dict, period: str):
    """
        TODO missing
        
        :param cluster_period: contains the gui input of the chosen \
            period type (possible entries: hours, days, weeks)
        :type cluster_period: str
        :param days_per_cluster: contains the gui input of the chosen \
            index (possible entries: 1 - 365)
        :type days_per_cluster: int
        :param criterion: criterion chosen for k_mean algorithm
        :type criterion: str
        :param nodes_data: dictionary containing the excel worksheets from
                           the used scenario workbook

        :type nodes_data: dict
        :param period: defines rather days or weeks were selected
        :type period: str
        
        :raise: - **ValueError** - Error raised if the chosen period \
            is not supported
    """
    if cluster_period == 'days':
        clusters = 365 // int(days_per_cluster)
        print('days per cluster: ' + str(days_per_cluster))
        print('clusters: ' + str(clusters))
    elif cluster_period == 'weeks':
        clusters = 52 // int(days_per_cluster)
        print('days per cluster: ' + str(days_per_cluster))
        print('clusters: ' + str(clusters))
    else:
        raise ValueError("period chosen not possible")
    # Merge the timeseries and weather data sets, sothat that all timeseries'
    # get clustered within one step
    nodes_data['timeseries'] = append_timeseries_to_weatherdata_sheet(
        nodes_data=nodes_data)

    weather_data = nodes_data['timeseries'].copy()

    # Calculate k-medoids clusters, based on the cluster_criterion
    cluster_labels = calculate_k_medoids_clusters(cluster_number=clusters,
                                                  weather_data=weather_data,
                                                  cluster_criterion=criterion,
                                                  period=period)

    weather_data = nodes_data['timeseries'].copy()
    nodes_data['weather data'] = weather_data
    nodes_data['timeseries'] = weather_data

    # Adapts Other Parameters (despite weather data) of the energy system
    variable_costs_date_adaption(nodes_data, clusters, period)

    k_medoids_timeseries_adaption(nodes_data, clusters,
                                  cluster_labels, period)
