from sklearn.cluster import KMeans
from sklearn_extra.cluster import KMedoids
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import numpy as np


def extract_single_periods(data_set, column_name, period):
    """
        Extracts individual periods of a certain column of a weather data
        set as lists. Caution: weather data set must be available in
        hourly resolution!

        :param data_set: weather data set to be extracted
        :param column_name: column name of which the extraction should
                            be applied
        :param period: indicates what kind of periods shall be extracted.
                       Possible arguments: "days", "weeks", "hours".

        :return: - **cluster_vectors** - list, containing a list/vector for
            every single day
            
    """

    if period == "days":
        timesteps = 24
    elif period == "weeks":
        timesteps = 168
    elif period == "hours":
        timesteps = 1
    else:
        raise ValueError("Non supported period")
    # extract data_set of cluster_criterion
    cluster_df = data_set[column_name]
    # extract single periods as lists and add them to a list
    cluster_vectors = []
    for i in range(0, int(len(cluster_df) / timesteps)):
        cluster_vector = []
        for j in range(timesteps):
            cluster_vector.append(cluster_df[i * timesteps + j])
        cluster_vectors.append(cluster_vector)

    # returns the list with extracted day data sets
    return cluster_vectors


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

def calculate_brute_force_clusters(cluster_number: int, weather_data: dict,
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

    neigh = KNeighborsClassifier(n_neigghbors=2)
    


    # nbrs = NearestNeighbors(n_neighbors=cluster_number, algorithm='brute').fit(cluster_vectors)
    # print('ping1')
    # print(nbrs)
    # distances, indices = nbrs.kneighbors(cluster_vectors)
    # print(len(distances))
    # print(distances)

    # kmedoids = KMedoids(n_clusters=cluster_number)
    # model = kmedoids.fit(cluster_vectors)
    return model.labels_

def calculate_cluster_means(data_set, cluster_number: int,
                            cluster_labels, period: str):
    """
        Determines weather averages of the individual clusters for a
        weather dataset, based on predetermined cluster allocation.
        Caution: weather data set must be available in hourly resolution!

        :param data_set: data_set, the clusters should be applied to
        :type data_set: pd.core.frame.DataFrame
        :param cluster_number: Number of clusters
        :type cluster_number: int
        :param cluster_labels: Chronological list, which days of the
            weather data set belongs to which cluster
        :type cluster_labels: np.array
        :param period: defines rather days or weeks were selected
        :type period: str

        :return: - **prep_data_set** (pd.Dataframe) - pandas dataframe 
            containing the prepared weather data set
       
    """
    column_names = [data_set.columns[i] for i in
                    range(1, len(data_set.columns))]
    # Define pandas Dataframe for final data_set
    prep_data_set = pd.DataFrame()
    # Loop for every column of the weather data set
    for i in range(len(column_names) - 1):
        # Extract individual weather data set for the current weather
        # data column
        data_set_column = extract_single_periods(data_set=data_set,
                                                 column_name=column_names[i],
                                                 period=period)
        # Define empty list used later
        reference_data_set = []
        # Loop for every k_means cluster
        for j in range(0, cluster_number):
            # Define empty list used later
            cluster_dataset = []
            # Loop for every day of the weather data set
            for k in range(len(data_set_column)):
                # if the day belongs to the current cluster, it will be
                # appended to 'cluster_dataset'
                if cluster_labels[k] == j:
                    cluster_dataset.append(data_set_column[k])
            # Calculates the mean for ever hour of the current cluster
            cluster_dataset_array = np.array(cluster_dataset)
            # Appends the calculated mean values to the 'reference_data_
            # set' list
            reference_data_set += cluster_dataset_array.mean(axis=0).tolist()
        # Appends the calculated reference days for the current weather
        # data column to the final weather data set
        prep_data_set[column_names[i]] = reference_data_set

    return prep_data_set

def append_timeseries_to_weatherdata_sheet(nodes_data: dict):
    """
    Merges the time series of the weather data set and the time series. This
    allows the weather data and time series to be processed together for
    cluster algorithms, reducing the error-proneness of sepparate processing.
    :param data_set:
    :return:
    """

    # Adding the weather data set to the timeseries data set
    nodes_data['timeseries'] = nodes_data['timeseries'].merge(
        nodes_data['weather data'], how='inner', left_index=True,
        right_index=True)

    # Correction of duplicate names/columns
    for column_name in list(nodes_data['timeseries'].columns.values):
        # if a column was in both of the panda data frames, they are indexed
        # with the ending "_x" and "_y". Those are identified, and renamed,
        # respectively deleted.
        if column_name[-2:] == "_x":
            nodes_data['timeseries'].rename(columns={column_name: column_name[:-2]}, inplace=True)
        elif column_name[-2:] == "_y":
            del nodes_data['timeseries'][column_name]

    print(list(nodes_data['timeseries'].columns.values))
    print(nodes_data['timeseries'])

    return nodes_data['timeseries']

def calculate_cluster_medoids(data_set, cluster_number: int,
                            cluster_labels, period: str):
    """
        Determines weather medoid of the individual clusters for a
        weather dataset, based on predetermined cluster allocation.
        Caution: weather data set must be available in hourly resolution!

        :param data_set: data_set, the clusters should be applied to
        :type data_set: pd.core.frame.DataFrame
        :param cluster_number: Number of clusters
        :type cluster_number: int
        :param cluster_labels: Chronological list, which days of the
            weather data set belongs to which cluster
        :type cluster_labels: np.array
        :param period: defines rather days or weeks were selected
        :type period: str

        :return: - **prep_data_set** (pd.Dataframe) - pandas dataframe
            containing the prepared weather data set

    """


    # column_names = [data_set.columns[i] for i in
    #                 range(1, len(data_set.columns))]
    # # Define pandas Dataframe for final data_set
    # prep_data_set = pd.DataFrame()
    # # Loop for every column of the weather data set
    # for i in range(len(column_names) - 1):
    #     # Extract individual weather data set for the current weather
    #     # data column
    #     data_set_column = extract_single_periods(data_set=data_set,
    #                                              column_name=column_names[i],
    #                                              period=period)
    #     # Define empty list used later
    #     reference_data_set = []
    #     # Loop for every k-cluster
    #     for j in range(0, cluster_number):
    #         # Define empty list used later
    #         cluster_dataset = []
    #         # Loop for every day of the weather data set
    #         for k in range(len(data_set_column)):
    #             # if the day belongs to the current cluster, it will be
    #             # appended to 'cluster_dataset'
    #             if cluster_labels[k] == j:
    #                 cluster_dataset.append(data_set_column[k])
    #         # Calculates the medoid for ever hour of the current cluster
    #         cluster_dataset_array = np.array(cluster_dataset)
    #         # Appends the calculated mean values to the 'reference_data_
    #         # set' list
    #         reference_data_set += cluster_dataset_array.argmin(distMatrix.sum(axis=0)).tolist()
    #     # Appends the calculated reference days for the current weather
    #     # data column to the final weather data set
    #     prep_data_set[column_names[i]] = reference_data_set

    return prep_data_set


def k_means_parameter_adaption(nodes_data: dict, clusters: int, period: str):
    """
        To be able to work with the adapted weather data set some
        parameters from nodes_data must be changed.

        :param nodes_data: system parameters
        :type nodes_data: dict
        :param clusters: Number of clusters
        :type clusters: int
        :param period: defines rather hours, days or weeks were selected
    """
    # Adapting variable costs
    if period == 'days':
        variable_cost_factor = int(nodes_data['energysystem']['periods']) \
                               / int(24*clusters)
        print('VARIABLE COST FACTOR')
        print(variable_cost_factor)
    elif period == 'weeks':
        variable_cost_factor = int(nodes_data['energysystem']['periods']) \
                               / int(7*24 * clusters)
        print('VARIABLE COST FACTOR')
        print(variable_cost_factor)
    elif period == 'hours':
        variable_cost_factor = int(nodes_data['energysystem']['periods']) \
                               / int(clusters)
        print('VARIABLE COST FACTOR')
        print(variable_cost_factor)
    else:
        raise ValueError("unsupported period")

    # Adapting Costs and Constraint Costs
    for sheet in nodes_data:
        for column in nodes_data[sheet].columns:
            if "variable" in column:
                nodes_data[sheet][column] *= variable_cost_factor
            # workaround for excess and shortage costs
            if sheet == "buses":
                if "costs" in column:
                    nodes_data[sheet][column] *= variable_cost_factor

    # Adapting Demands
    nodes_data['sinks']['annual demand'] = \
        nodes_data['sinks']['annual demand'] / variable_cost_factor

    # Adapting timesystem parameters
    if period == 'days':
        nodes_data['energysystem']['end date'] = \
            nodes_data['energysystem']['start date'] \
            + pd.Timedelta(str(clusters*24-1)+' hours')
        nodes_data['energysystem']['periods'] = int(24*clusters)
    elif period == 'weeks':
        nodes_data['energysystem']['end date'] = \
            nodes_data['energysystem']['start date'] \
            + pd.Timedelta(str(clusters*7*24-1)+' hours')
        nodes_data['energysystem']['periods'] = int(7*24*clusters)
    elif period == 'hours':
        nodes_data['energysystem']['end date'] = \
            nodes_data['energysystem']['start date'] \
            + pd.Timedelta(str(clusters-1)+' hours')
        nodes_data['energysystem']['periods'] = int(clusters)


def k_means_timeseries_adaption(nodes_data: dict, clusters: int,
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
    clusters = len(nodes_data["timeseries"]) \
               // len(nodes_data["weather data"])
    print(prep_timeseries)
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
            :int(len(nodes_data['timeseries']) / (clusters*7))]
    # print(prep_timeseries)
    nodes_data['timeseries'] = prep_timeseries


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
    clusters = len(nodes_data["timeseries"]) \
               // len(nodes_data["weather data"])
    print(prep_timeseries)
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
            :int(len(nodes_data['timeseries']) / (clusters * 7))]
    # print(prep_timeseries)
    nodes_data['timeseries'] = prep_timeseries
    nodes_data['weather data'] = prep_timeseries


def k_means_algorithm(clusters: int, criterion: str, nodes_data: dict,
                      period: str):
    """
        TODO missing
        :param clusters: number of clusters chosen in GUI
        :type clusters: int
        :param criterion: criterion chosen for k_mean algorithm
        :type criterion: str
        :param nodes_data: dictionary containing the excel worksheets from
                           the used scenario workbook

        :type nodes_data: dict
        :param period: defines rather days or weeks were selected
        :type period: str
    """
    # depending on the chosen criterion rather the timeseries or the
    # weather data sheet is selected for the following preparation
    if criterion == 'el_demand_sum' or criterion == 'heat_demand_sum':
        weather_data = nodes_data['timeseries'].copy()
    else:
        weather_data = nodes_data['weather data'].copy()

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
    k_means_parameter_adaption(nodes_data, clusters, period)
    k_means_timeseries_adaption(nodes_data, clusters,
                                cluster_labels, period)


def k_medoids_algorithm(clusters: int, criterion: str, nodes_data: dict,
                        period: str):
    """
        TODO missing
        :param clusters: number of clusters chosen in GUI
        :type clusters: int
        :param criterion: criterion chosen for k_mean algorithm
        :type criterion: str
        :param nodes_data: dictionary containing the excel worksheets from
                           the used scenario workbook

        :type nodes_data: dict
        :param period: defines rather days or weeks were selected
        :type period: str
    """
    # Merge the timeseries and weather data sets, sothat that all timeseries'
    # get clustered within one step
    nodes_data['timeseries'] = append_timeseries_to_weatherdata_sheet(nodes_data)

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
    k_means_parameter_adaption(nodes_data, clusters, period)

    k_medoids_timeseries_adaption(nodes_data, clusters,
                                cluster_labels, period)

def brute_force_algorithm(clusters: int, criterion: str, nodes_data: dict,
                        period: str):
    """
        TODO missing
        :param clusters: number of clusters chosen in GUI
        :type clusters: int
        :param criterion: criterion chosen for k_mean algorithm
        :type criterion: str
        :param nodes_data: dictionary containing the excel worksheets from
                           the used scenario workbook

        :type nodes_data: dict
        :param period: defines rather days or weeks were selected
        :type period: str
    """
    # Merge the timeseries and weather data sets, sothat that all timeseries'
    # get clustered within one step
    nodes_data['timeseries'] = append_timeseries_to_weatherdata_sheet(nodes_data)

    weather_data = nodes_data['timeseries'].copy()

    # Calculate k-medoids clusters, based on the cluster_criterion
    cluster_labels = calculate_brute_force_clusters(cluster_number=clusters,
                                                    weather_data=weather_data,
                                                    cluster_criterion=criterion,
                                                    period=period)

    weather_data = nodes_data['timeseries'].copy()
    nodes_data['weather data'] = weather_data
    nodes_data['timeseries'] = weather_data

    # Adapts Other Parameters (despite weather data) of the energy system
    k_means_parameter_adaption(nodes_data, clusters, period)

    k_medoids_timeseries_adaption(nodes_data, clusters,
                                cluster_labels, period)

def timeseries_averaging(clusters: int, nodes_data: dict, period: str):
    """
        Averages the values of the time series, how many values are
        averaged is defined by the variable clusters.
        
        :param clusters: definies how many periods will be averaged
        :type clusters: int
        :param nodes_data: dictionary containing the excel worksheets
                           from the used scenario workbook
        :type nodes_data: dict
        :param period: defines rather days or weeks were selected
        :type period: str
    """
    weather_data = nodes_data['weather data']

    if period == 'days':
        periods = int(len(weather_data) / 24)
    elif period == 'weeks':
        periods = int(len(weather_data) / (24*7))
    elif period == 'hours':
        periods = int(len(weather_data))
    else:
        raise ValueError("period choosen not possible")
        
    cluster_labels = []
    for i in range(clusters):
        for j in range(periods // clusters):
            cluster_labels.append(i)
    if periods % clusters >= 0:
        for k in range(periods % clusters):
            cluster_labels.append(clusters - 1)
    cluster_labels = np.array(cluster_labels)

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


def data_set_slicing(n_days: int, data_set, period: str):
    """
        uses every n-th period of the given data_set and cuts the rest
        out of the data_set
        
        :param n_days: defines which period is chosen
        :type n_days: int
        :param data_set: data to be sliced
        :type data_set: pandas.core.frame.Dataframe
        :param period: defines rather hours, days or weeks were selected
        :type period: str
    """

    column_names = [data_set.columns[i] for i in
                    range(1, len(data_set.columns))]

    prep_data_set = pd.DataFrame()

    # Loop for every column of the weather data set
    for i in range(len(column_names)):
        # Extract individual weather data set for the current weather
        # data column
        data_set_column = extract_single_periods(data_set=data_set,
                                                 column_name=column_names[i],
                                                 period=period)

        # If the data set is not divisible by the corresponding number
        # of periods, the data set is shortened accordingly
        if len(data_set_column) % n_days > 0:
            data_set_column = \
                data_set_column[0:-(len(data_set_column) % n_days)]

        sliced_column = data_set_column[0::n_days]

        reference_data_set = []
        for j in range(len(sliced_column)):
            reference_data_set = reference_data_set + sliced_column[j]

        # Appends the calculated reference days for the current weather
        # data column to the final weather data set
        prep_data_set[column_names[i]] = reference_data_set

    return prep_data_set


def data_set_slicing2(n_days, data_set, period):
    """
        cuts out every nth period from the given data_set and leaves the
        remaining periods for further consideration
        
        :param n_days: defines which period is sliced
        :type n_days: int
        :param data_set: data to be sliced
        :type data_set: pandas.core.frame.Dataframe
        :param period: defines rather hours, days or weeks were selected
        :type period: str
    """

    column_names = [data_set.columns[i] for i in
                    range(1, len(data_set.columns))]

    prep_data_set = pd.DataFrame()

    # Loop for every column of the weather data set
    for i in range(len(column_names)):
        # Extract individual weather data set for the current weather
        # data column
        data_set_column = extract_single_periods(data_set=data_set,
                                                 column_name=column_names[i],
                                                 period=period)

        # If the data set is not divisible by the corresponding number
        # of periods, the data set is shortened accordingly
        if len(data_set_column) % n_days > 0:
            data_set_column = data_set_column[0:-(len(data_set_column)%n_days)]

        sliced_column = data_set_column
        del sliced_column[n_days-1::n_days]

        reference_data_set = []
        for j in range(len(sliced_column)):
            reference_data_set = reference_data_set + sliced_column[j]

        # Appends the calculated reference days for the curent weather
        # data column to the final weather data set
        prep_data_set[column_names[i]] = reference_data_set

    return prep_data_set


def timeseries_slicing(n_days: int, nodes_data: dict, period: str):
    """
        uses every n-th period of the given data_set and cuts the rest
        out of the data_set
        
        :param n_days: defines which period is chosen
        :type n_days: int
        :param nodes_data: data to be sliced
        :type nodes_data: dict
        :param period: defines rather hours, days or weeks were selected
        :type period: str
    """

    weather_data = nodes_data['weather data']
    data_set = nodes_data['weather data']

    prep_weather_data = data_set_slicing(n_days,
                                         data_set=data_set,
                                         period=period)

    # Rename columns of the new weather_dataset
    prep_weather_data['timestamp'] = \
        weather_data['timestamp'][:len(prep_weather_data)]

    # Replaces the weather data set in nodes_data by the new one
    nodes_data['weather data'] = prep_weather_data
    # Adapts Other Parameters (despite weather data) of the energy system

    if period == 'days':
        adaption_clusters = len(prep_weather_data)/24
    elif period == 'weeks':
        adaption_clusters = len(prep_weather_data)/(24*7)
    elif period == 'hours':
        adaption_clusters = len(prep_weather_data)
    else:
        raise ValueError("Non supported period")
    k_means_parameter_adaption(nodes_data=nodes_data,
                               clusters=adaption_clusters, # TODO: relativen wert einfügen!
                               period=period)

    prep_timeseries = data_set_slicing(n_days,
                                       data_set=nodes_data['timeseries'],
                                       period=period)
    prep_timeseries['timestamp'] = \
        nodes_data['timeseries']['timestamp'][:len(prep_weather_data)]
    nodes_data['timeseries'] = prep_timeseries


def timeseries_slicing2(n_days: int, nodes_data: dict, period: str):
    """
        cuts out every nth period from the given data_set and leaves the
        remaining periods for further consideration
        
        :param n_days: defines which period is sliced
        :type n_days: int
        :param nodes_data: data to be sliced
        :type nodes_data: dict
        :param period: defines rather hours, days or weeks were selected
        :type period: str
    """
    weather_data = nodes_data['weather data']
    data_set = nodes_data['weather data']

    prep_weather_data = data_set_slicing2(n_days,
                                          data_set=data_set,
                                          period=period)

    # Rename columns of the new weather_dataset
    prep_weather_data['timestamp'] = \
        weather_data['timestamp'][:len(prep_weather_data)]

    # Replaces the weather data set in nodes_data by the new one
    nodes_data['weather data'] = prep_weather_data

    if period == 'days':
        adaption_clusters = len(prep_weather_data)/24
    elif period == 'weeks':
        adaption_clusters = len(prep_weather_data)/(24*7)
    elif period == 'hours':
        adaption_clusters = len(prep_weather_data)
    else:
        raise ValueError("Non supported period")
    # Adapts Other Parameters (despite weather data) of the energy system
    print('LEN PREP WEATHER DATA')
    print(len(prep_weather_data))
    k_means_parameter_adaption(nodes_data=nodes_data,
                               clusters=adaption_clusters,
                               period=period)

    prep_timeseries = data_set_slicing2(n_days,
                                        data_set=nodes_data['timeseries'],
                                        period=period)
    prep_timeseries['timestamp'] = \
        nodes_data['timeseries']['timestamp'][:len(prep_weather_data)]
    nodes_data['timeseries'] = prep_timeseries


def timeseries_downsampling(nodes_data: dict, n_timesteps: int, period: str):
    """
        uses every n-th period of timeseries and weather data
        
        :param nodes_data: system parameters
        :type nodes_data: dict
        :param n_timesteps: defines which period is chosen
        :type n_timesteps: int
        :param period: defines rather hours, days or weeks were selected
        :type period: str

    """
    end_date = nodes_data['energysystem']['end date'].copy()
    periods = round(nodes_data["energysystem"]["periods"] / n_timesteps,0)
    # shortening timeseries and weather data
    nodes_data['timeseries'] = \
        nodes_data['timeseries'].iloc[::n_timesteps, :]
    nodes_data['weather data'] = \
        nodes_data['weather data'].iloc[::n_timesteps, :]
    # changing the temporal resolution to n-periods
    nodes_data['energysystem']['temporal resolution'] = \
        str(n_timesteps) + nodes_data['energysystem']['temporal resolution']

    k_means_parameter_adaption(nodes_data=nodes_data,
                               clusters=int(nodes_data['energysystem']
                                            ['periods']/n_timesteps),
                               period="hours")
    # bring periods and end date back to the old value due to
    # manipulating the temporal resolution
    nodes_data['energysystem']['periods'] = periods
    nodes_data['energysystem']['end date'] = end_date
    
    
def timeseries_downsampling2(nodes_data: dict, n_timesteps: int, period: str):
    """
        cuts every n-th period of timeseries and weather data
        
        :param nodes_data: system parameters
        :type nodes_data: dict
        :param n_timesteps: defines which period is cut
        :type n_timesteps: int
        :param period: defines rather hours, days or weeks were selected
        :type period: str
    """
    prep_timeseries = nodes_data['timeseries'].copy()
    # cut every n-th period
    prep_timeseries = prep_timeseries.iloc[::n_timesteps]

    weather_data = nodes_data['weather data']
    prep_weather_data = nodes_data['weather data'].copy()
    
    # cut every n-th period
    prep_weather_data = prep_weather_data.iloc[::n_timesteps]

    prep_timeseries.reset_index(drop=True, inplace=True)
    prep_weather_data.reset_index(drop=True, inplace=True)
    
    # change timestamp to the new ones for stringent dates
    prep_timeseries['timestamp'] = \
        weather_data['timestamp'][:len(prep_timeseries)]
    prep_weather_data['timestamp'] = \
        weather_data['timestamp'][:len(prep_weather_data)]
    nodes_data['weather data'] = prep_weather_data
    nodes_data['timeseries'] = prep_timeseries
    # adapt the variable cost parameter
    k_means_parameter_adaption(nodes_data=nodes_data,
                               clusters=int(len(prep_timeseries)),
                               period="hours")


def hierarchical_selection(nodes_data, scheme, period, seasons, scheme_path):
    """
        Algorithm for the hierarchical selection of representative time
        periods of a weather data set. In this embodiment, the following
        representative periods are selected for every season
        (winter, spring, summer, fall) are selected:
    
        - Week containing the coldest temperature of the season
        - Week with the lowest average sun duration
        - Week containing the warmest temperature of the season
        - Week with the highest average sun duration
    
    
        :param nodes_data: SESMG-nodes data, containing weather data,
                           energy system parameters and timeseries
        :return: **nodes_data** (dict): modified SESMG-nodes data,
                                       containing weather data, energy
                                       system parameters and timeseries
    """

    def extract_data_slices(data_set, timesteps: int):
        """
            extracts slices of a defined length of a dataset. E.g.
            slices of weeks
            (168 timesteps) of a weather data set may be extracted.

            :param data_set: Data set from which the slices are extracted
            :type data_set:
            :param timesteps: length of the to extracted slices
            :type timesteps: int
            :return: **list** extracted slices of the given data set
        """
        list_of_data_slices = []
        for i in range(len(data_set) // timesteps):
            period_data_set = data_set[i * timesteps:(i + 1) * timesteps]
            list_of_data_slices.append(period_data_set)
        return list_of_data_slices

    def identify_timeseries_minimum(data_set, column_name: str):
        """
            returns the minimum value of a certain column of a given
            data_set
            
            :param data_set:
            :type data_set:
            :param column_name: column under investigation
            :type column_name: str
            :return: **float** minimum value of a column
        """
        return min(data_set[column_name])

    def identify_minimum_week(data_set, criterion, value):
        """
            Returns the week with a minimum value of a certain column.
            Either the week with the absolute minimum value, or the week
            with the average minimum value can be selected.

            :param data_set: Dataset
            :param criterion: column, which is the criterion of the selection
            :param value: 'extreme' for absolute minimum value, 'average' for
                           average minimum value selection
            :return: minimum_week: Dataset of the selected minimum week
        """

        absolute_minimum = 99999999
        for i in range(len(data_set)):

            if value == "extreme":
                weekly_minimum = identify_timeseries_minimum(
                    data_set=data_set[i],
                    column_name=criterion)
            elif value == "average":
                weekly_minimum = identify_timeseries_average(
                    data_set=data_set[i],
                    column_name=criterion)
            else:
                raise ValueError("value chosen not supported")
            # check if calc. minimum is lower than the one calc. before
            if weekly_minimum < absolute_minimum:
                absolute_minimum = weekly_minimum
                minimum_week = data_set[i]

        return minimum_week

    def identify_timeseries_maximum(data_set, column_name):
        """
            returns the maximum value of a certain column of a given
            data_set
            
            :param data_set:
            :type data_set:
            :param column_name: column under investigation
            :type column_name: str
            :return: **float** maximum value of a column
        """
        return max(data_set[column_name])

    def identify_timeseries_average(data_set, column_name):
        """
            returns the average value of a certain column of a given
            data_set.
            
            :param data_set:
            :type data_set:
            :param column_name: column under investigation
            :type column_name: str
            :return: **float** average of a column
        """
        list = data_set[column_name]
        return 0 if len(list) == 0 else sum(list) / len(list)

    def identify_maximum_week(data_set, criterion: str, value: str):
        """
            Returns the week with a maximum value of a certain column.
            Either the week with the absolute maximum value, or the week
            with the average maximum value can be selected.
            
            :param data_set: Dataset
            :type data_set:
            :param criterion: column, which is the criterion of the
                              selection
            :type criterion: str
            :param value: 'extreme' for absolute maximum value,
                          'average' for average maximum value selection
            :type value: str
            :return: minimum_week: Dataset of the selected maximum week
        """
        absolute_maximum = -99999999
        for i in range(len(data_set)):
            if value == "extreme":
                weekly_maximum = identify_timeseries_maximum(
                    data_set=data_set[i],
                    column_name=criterion)
            elif value == "average":
                weekly_maximum = identify_timeseries_average(
                    data_set=data_set[i],
                    column_name=criterion)
            else:
                raise ValueError("value chosen not supported")

            if weekly_maximum > absolute_maximum:
                absolute_maximum = weekly_maximum
                maximum_week = data_set[i]

        return maximum_week

    def identify_average_week(data_set, criterion: str):
        """
            Returns the week with the most average series of a certain
            column.

            :param data_set: Dataset
            :type data_set:
            :param criterion: column, which is the criterion of the
                              selection
            :type criterion: str
            :return: minimum_week: Dataset of the selected maximum week
        """
        # Creates a list with the average value of every week
        list_of_averages = []
        for i in range(len(data_set)):
            weekly_average = identify_timeseries_average(data_set=data_set[i],
                                                         column_name=criterion)
            list_of_averages.append(weekly_average)

        # Calculates the average of the entire dataset
        absolute_average = 0 if len(list_of_averages) == 0 \
            else sum(list_of_averages) / len(list_of_averages)

        # Checks which average is closest to the absolute average
        deviation = 999999999999
        for i in range(len(data_set)):
            if abs(list_of_averages[i] - absolute_average) <= deviation:
                deviation = abs(list_of_averages[i] - absolute_average)
                average_data = data_set[i]

        return average_data

    def create_period_weather_data(period: str):
        """
             Splits the weather data_set in nodes_data into weekly od
             dayly weather data sets
             :param period: defines rather dayly or weekly weather data
                            data set is created
             :type period: str
             :return: shortend weather data data set
        """
        # Splits the given weather data_set in nodes_data into weekly
        # weather data sets
        if period == 'weeks':
            period_length = 24*7
        elif period == 'days':
            period_length = 24
        else:
            raise ValueError("Non supported period")
                
        return extract_data_slices(data_set=nodes_data['weather data'],
                                   timesteps=period_length)

    def create_period_season_weather_data(period_data_slices, seasons: int):
        """
            Splits a given weather data (one year) set into weekly
            weather data slices and sorts them into lists of every
            season of the year (each season is defined by a length of 13
            weeks) and returns a list, containing a list of weather
            data weeks for every season.
    
    
            :param period_data_slices: weather data already shortend to
                                       dayly or weakly resolution
            :param seasons: number of seasons
            :type seasons: int
            :return: list, containing list of weekly weather data slices
                     of every season.
        """

        season_length = len(period_data_slices) // seasons

        # Sorts the weekly weather data sets into seasons. One season is
        # defined by 13 consecutive weeks here
        season_data = []
        for i in range(seasons):
            periods_data = period_data_slices[season_length
                                              * i:season_length*(i+1)]
            season_data.append(periods_data)

        return season_data

    def select_heuristic_periods(heuristic_periods,
                                 period_data_slices,
                                 season_data,
                                 seasons):
        """
            Selects and returns representative values of time series
            according to a given heuristic scheme.
            
            :param heuristic_periods:
            :param period_data_slices:
            :param season_data:
            :param seasons:
            :return:
        """
        prep_weather_data = pd.DataFrame()

        if seasons == 4:
            for representative in heuristic_periods:
                if representative[0] == 'winter':
                    data_set = season_data[0]
                elif representative[0] == 'spring':
                    data_set = season_data[1]
                elif representative[0] == 'summer':
                    data_set = season_data[2]
                elif representative[0] == 'fall':
                    data_set = season_data[3]
                elif representative[0] == 'year':
                    data_set = period_data_slices
                else:
                    raise ValueError("Error")

                if representative[1] == 'lowest':
                    selected_week = identify_minimum_week(
                            data_set=data_set,
                            criterion=representative[2],
                            value=representative[3])

                elif representative[1] == 'highest':
                    selected_week = identify_maximum_week(
                        data_set=data_set,
                        criterion=representative[2],
                        value=representative[3])

                elif representative[1] == 'average':
                    selected_week = identify_average_week(
                        data_set=data_set,
                        criterion=representative[2])
                else:
                    raise ValueError("Error")

                prep_weather_data = prep_weather_data.append(selected_week)

        elif seasons == 12:
            for representative in heuristic_periods:
                if representative[0] == 'year':
                    data_set = period_data_slices
                else:
                    data_set = season_data[int(representative[0])-1]

                if representative[1] == 'lowest':
                    selected_week = identify_minimum_week(
                            data_set=data_set,
                            criterion=representative[2],
                            value=representative[3])

                elif representative[1] == 'highest':
                    selected_week = identify_maximum_week(
                        data_set=data_set,
                        criterion=representative[2],
                        value=representative[3])

                elif representative[1] == 'average':
                    selected_week = identify_average_week(
                        data_set=data_set,
                        criterion=representative[2])
                else:
                    raise ValueError("Error")

                prep_weather_data = prep_weather_data.append(selected_week)

        return prep_weather_data

    period_data_slices = create_period_weather_data(period)
    season_data = create_period_season_weather_data(period_data_slices,
                                                    seasons=seasons)
    prep_weather_data = pd.DataFrame()
    scheme_df = pd.read_excel(scheme_path, sheet_name=str(scheme))
    heuristic_periods = scheme_df.values.tolist()
    prep_weather_data = select_heuristic_periods(heuristic_periods,
                                                 period_data_slices,
                                                 season_data,
                                                 seasons)

    for col in nodes_data['timeseries']:
        prep_weather_data[col] = nodes_data['timeseries'][col]
    # Rename columns of the new weather_dataset
    weather_data = nodes_data['weather data'].copy()
    prep_weather_data.reset_index(drop=True, inplace=True)
    prep_weather_data['timestamp'] = \
        weather_data['timestamp'][:len(prep_weather_data)]
    prep_weather_data.reset_index(drop=True)

    # Replace original data with hierarchical clustered data
    nodes_data['weather data'] = prep_weather_data.copy()
    nodes_data['timeseries'] = prep_weather_data.copy()
    # Adapts Other Parameters (despite weather data) of the energy system
    if period == 'weeks':
        period_length = 24 * 7
    elif period == 'days':
        period_length = 24
    else:
        raise ValueError("period chosen not possible")

    k_means_parameter_adaption(nodes_data=nodes_data,
                               clusters=int(len(nodes_data['weather data'])
                                            / period_length),
                               period=period)


def random_sampling(nodes_data, period, number_of_samples):
    import random as rd

    weather_data = nodes_data['weather data']
    data_set = nodes_data['weather data']
    prep_data_set = pd.DataFrame()
    cluster_vectors = extract_single_periods(data_set=weather_data,
                                             column_name='temperature',
                                             period=period)

    print('LEN CLUSTER VECTORS')
    print(len(cluster_vectors))

    # generate random integers
    random_integers = []
    for i in range(number_of_samples):
        rd.seed(i)
        random = rd.randint(0, len(cluster_vectors)-1)
        random_integers.append(random)
    print('RANDOM INTEGER LIST')
    print(random_integers)
    print(max(random_integers))

    column_names = [data_set.columns[i]
                    for i in range(1, len(data_set.columns))]
    prep_data_set = pd.DataFrame()

    for i in range(len(column_names)):
        # Extract individual weather data set for the current weather
        # data column
        data_set_column = extract_single_periods(data_set=data_set,
                                                 column_name=column_names[i],
                                                 period=period)

        reference_data_set = []
        print('LEN DATA SET COLUMN')
        print(len(data_set_column))
        for j in random_integers:
            reference_data_set = reference_data_set + data_set_column[j]

        # Appends the calculated reference days for the curent weather
        # data column to the final weather data set
        prep_data_set[column_names[i]] = reference_data_set

    prep_weather_data = prep_data_set

    # Rename columns of the new weather_dataset
    prep_weather_data['timestamp'] = \
        weather_data['timestamp'][:len(prep_weather_data)]

    # Replaces the weather data set in nodes_data by the new one
    nodes_data['weather data'] = prep_weather_data.copy()

    # Adapts Other Parameters (despite weather data) of the energy system

    if period == 'days':
        adaption_clusters = len(prep_weather_data)/24
    elif period == 'weeks':
        adaption_clusters = len(prep_weather_data)/(24*7)
    else:
        raise ValueError("Non supported period")

    k_means_parameter_adaption(nodes_data=nodes_data,
                               clusters=int(adaption_clusters), # TODO: relativen wert einfügen!
                               period=period)

    data_set = nodes_data['timeseries']
    column_names = [data_set.columns[i]
                    for i in range(1, len(data_set.columns))]
    for i in range(len(column_names)):
        # Extract individual weather data set for the current weather
        # data column
        data_set_column = extract_single_periods(data_set=data_set,
                                                 column_name=column_names[i],
                                                 period=period)

        reference_data_set = []
        for j in range(len(random_integers)):
            reference_data_set = reference_data_set \
                                 + data_set_column[random_integers[j]]

        # Appends the calculated reference days for the current weather
        # data column to the final weather data set
        prep_data_set[column_names[i]] = reference_data_set

    prep_timeseries = prep_data_set

    prep_timeseries['timestamp'] = \
        nodes_data['timeseries']['timestamp'][:len(prep_weather_data)]
    nodes_data['timeseries'] = prep_timeseries.copy()


def timeseries_preparation(timeseries_prep_param: list,
                           nodes_data: dict,
                           scheme_path: str,
                           result_path: str):
    """
        Evaluates the passed parameters for timeseries preparation and
        starts the corresponding simplification/clustering algorithm.

        :param timeseries_prep_param: List of timeseries preparation
                                      parameters with the scheme
                                      [algorithm, cluster_index,
                                      cluster_criterion, cluster_period,
                                      cluster_season]
        :type timeseries_prep_param: list
        :param nodes_data: Dictionary containing the energy systems data
        :type nodes_data: dict
        :param scheme_path: Path, where the xlsx-file with possible
                            heuristic selection schemes is stored.
        :type scheme_path: str
        :param result_path:
        :type result_path: str
        :return:
    """
    data_prep = timeseries_prep_param[0]
    days_per_cluster = timeseries_prep_param[1]
    n_timesteps = timeseries_prep_param[1]
    cluster_criterion = timeseries_prep_param[2]
    cluster_period = timeseries_prep_param[3]
    cluster_seasons = int(timeseries_prep_param[4])

    # K-MEANS ALGORITHM
    if data_prep == 'k_means':
        if cluster_period == 'days':
            clusters = 365 // int(days_per_cluster)
        elif cluster_period == 'weeks':
            clusters = 52 // int(days_per_cluster)
        else:
            raise ValueError("period chosen not possible")
        k_means_algorithm(clusters=clusters,
                          criterion=cluster_criterion,
                          nodes_data=nodes_data,
                          period=cluster_period)

    # K-MEDOIDS ALGORITHM
    if data_prep == 'k_medoids':
        if cluster_period == 'days':
            clusters = 365 // int(days_per_cluster)
        elif cluster_period == 'weeks':
            clusters = 52 // int(days_per_cluster)
        else:
            raise ValueError("period chosen not possible")
        k_medoids_algorithm(clusters=clusters,
                            criterion=cluster_criterion,
                            nodes_data=nodes_data,
                            period=cluster_period)

    # BRUTE-FORCE ALGORITHM
    if data_prep == 'brute force':
        if cluster_period == 'days':
            clusters = 365 // int(days_per_cluster)
        elif cluster_period == 'weeks':
            clusters = 52 // int(days_per_cluster)
        else:
            raise ValueError("period chosen not possible")
        brute_force_algorithm(clusters=clusters,
                              criterion=cluster_criterion,
                              nodes_data=nodes_data,
                              period=cluster_period)

    # AVERAGING ALGORITHM
    elif data_prep == 'averaging':
        if cluster_period == 'hours':
            clusters = 8760 // int(days_per_cluster)
        elif cluster_period == 'days':
            clusters = 365 // int(days_per_cluster)
        elif cluster_period == 'weeks':
            clusters = 52 // int(days_per_cluster)
        else:
            raise ValueError("period chosen not possible")
        timeseries_averaging(clusters=clusters,
                             nodes_data=nodes_data,
                             period=cluster_period)

    # SLICING ALGORITHM
    # use every n-th period
    elif data_prep == 'slicing A':
        timeseries_slicing(n_days=int(days_per_cluster),
                           nodes_data=nodes_data,
                           period=cluster_period),
    # delete every n-th period
    elif data_prep == 'slicing B':
        timeseries_slicing2(n_days=int(days_per_cluster),
                            nodes_data=nodes_data,
                            period=cluster_period),

    # DOWNSAMPLING ALGORITHM
    # use every n-th period
    elif data_prep == 'downsampling A':
        timeseries_downsampling(nodes_data, int(n_timesteps), cluster_period)
    # delete every n-th period
    elif data_prep == 'downsampling B':
        timeseries_downsampling2(nodes_data, int(n_timesteps), cluster_period)

    # HEURISTIC SELECTION ALGORITHM
    elif data_prep == 'heuristic selection':
        hierarchical_selection(nodes_data=nodes_data,
                               scheme=int(n_timesteps),
                               period=cluster_period,
                               seasons=cluster_seasons,
                               scheme_path=scheme_path)

    elif data_prep == 'random sampling':
        random_sampling(nodes_data, period=cluster_period,
                        number_of_samples=int(n_timesteps))

    # ADAPTS THE PARAMETERS OF THE ENERGY SYSTEM
    if data_prep != 'none':
        path = result_path + "/modified_scenario.xlsx"
        writer = pd.ExcelWriter(path, engine='xlsxwriter')
        nodes_data['weather data'].to_excel(writer, sheet_name='weather data')
        nodes_data['timeseries'].to_excel(writer, sheet_name='time series')
        nodes_data['energysystem'].to_excel(writer, sheet_name='energysystem')
        writer.save()
        scenario_file = path


def change_optimization_criterion(nodes_data: dict):
    """
    Swaps the primary optimization criterion ("costs") with the
    secondary criterion ("constraint costs") in the entire scenario. The
    constraint limit is adjusted.

    @ Christian Klemm - christian.klemm@fh-muenster.de

    :param nodes_data: dictionary containing the parameters of the scenario
    :type nodes_data: dict
    
    """

    def switch_column_names(nd: dict, scenario_sheet: str):
        """
        For a defined component type (scenario_sheet) the optimization
        criterion ("costs") is swapped by the secondary criterion ("constraint
        costs")

        :param nd: dictionary containing the parameters of the scenario
        :type nd: dict
        :param scenario_sheet: defines the component type, the parameters are
                               to be swapped.
        :type scenario_sheet: str
        """
        column_names = nd[scenario_sheet].columns.values
        column_names_list = column_names.tolist()

        column_names_list = \
            ['variable constraint costs' if x == 'variable costs'
             else 'variable costs' if x == 'variable constraint costs'
             else 'periodical costs' if x == 'periodical constraint costs'
             else 'periodical constraint costs' if x == 'periodical costs'
             else 'variable output costs'
             if x == 'variable output constraint costs'
             else 'variable output constraint costs'
             if x == 'variable output costs'
             else 'variable output costs 2'
             if x == 'variable output constraint costs 2'
             else 'variable output constraint costs 2'
             if x == 'variable output costs 2'
             else 'variable input costs'
             if x == 'variable input constraint costs'
             else 'variable input constraint costs'
             if x == 'variable input costs'
             else 'excess costs' if x == 'excess constraint costs'
             else 'excess constraint costs' if x == 'excess costs'
             else 'shortage costs' if x == 'shortage constraint costs'
             else 'shortage constraint costs' if x == 'shortage costs'
             else x for x in column_names_list]

        if scenario_sheet == 'links':
            column_names_list = ['variable output costs'
                                 if x == 'variable costs'
                                 else 'variable constraint costs'
                                 if x == 'variable output constraint costs'
                                 else x for x in column_names_list]

        nd[scenario_sheet].columns = column_names_list

    for i in [*nodes_data]:
        switch_column_names(nodes_data, i)

    # Sets the constraint Limit to "None"
    nodes_data['energysystem']['constraint costs'] = 'None'

    # Prints information
    print('''Primary and secondary cost criterion successfully swapped.
    ATTENTION, PLEASE NOTE:
    1. The new constraint limit was automatically set to "None"
    2. The swap does currently not support fix investment costs 
    (non-convex-investments).''')
