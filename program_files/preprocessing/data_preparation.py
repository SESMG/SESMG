import pandas as pd
import numpy as np
import demandlib.bdew as bdew
import datetime


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
    for i in range(len(column_names)):
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

    return nodes_data['timeseries']


#def calculate_cluster_medoids(data_set, cluster_number: int,
#                            cluster_labels, period: str):
#    """
#        Determines weather medoid of the individual clusters for a
#        weather dataset, based on predetermined cluster allocation.
#        Caution: weather data set must be available in hourly resolution!
#
#        :param data_set: data_set, the clusters should be applied to
#        :type data_set: pd.core.frame.DataFrame
#        :param cluster_number: Number of clusters
#        :type cluster_number: int
#        :param cluster_labels: Chronological list, which days of the
#            weather data set belongs to which cluster
#        :type cluster_labels: np.array
#        :param period: defines rather days or weeks were selected
#        :type period: str
#
#        :return: - **prep_data_set** (pd.Dataframe) - pandas dataframe
#            containing the prepared weather data set
#
#    """


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

#    return prep_data_set


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


def slp_sink_adaption(nodes_data: dict):
    """
        calculates the standard load profile timeseries, saves them to
        the timeseries data-sheet and changes the timeseries-reference
        for the respective sinks within the sinks-sheet.
    
        This step is required, so that the slp-timeseries will be
        considered during the timeseries adaptions.
    
        :param nodes_data: dict containing the data from the user's \
            model definition
        :type nodes_data: dict
        :return:
    """

    # Lists of possible standard load profiles
    heat_slp_list = ['efh', 'mfh']
    heat_slp_com = ['gmf', 'gpd', 'ghd', 'gwa', 'ggb', 'gko',
                     'gbd', 'gba', 'gmk', 'gbh', 'gga', 'gha']
    elec_slp_list = ['h0', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'l0',
                     'l1', 'l2']
    slp_list = heat_slp_list + elec_slp_list + heat_slp_com

    slp_profiles = pd.DataFrame()
    weather_data = nodes_data["weather data"].copy()

    # Creating Timesystem and Dataframe (required for the creation of standard
    # load profiles)
    ts = next(nodes_data['energysystem'].iterrows())[1]
    temp_resolution = str(ts['temporal resolution'])
    periods = int(ts["periods"])
    start_date = str(ts['start date'])
    start_date = \
        datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')


    # Creating standard load profile time series for sinks refering to heat or
    # electric standard load profiles
    for i, j in nodes_data["sinks"].iterrows():
        demand = pd.DataFrame(
            index=pd.date_range(datetime.datetime(start_date.year,
                                                  start_date.month,
                                                  start_date.day,
                                                  start_date.hour),
                                periods=periods, freq=temp_resolution))

        if j["load profile"] in heat_slp_list or j["load profile"] in heat_slp_com:
            # sets the parameters of the heat slps
            args = {'temperature': weather_data['temperature'],
                    'shlp_type': j["load profile"],
                    'wind_class': j['wind class'],
                    'annual_heat_demand': j['annual demand'],
                    'name': j['load profile']}
            if j["load profile"] in heat_slp_list:
                args.update({'building_class': j['building class']})
            # Add heat SLP to Timeseries-Dataframe
            slp=bdew.HeatBuilding(demand.index, **args).get_bdew_profile()
            nodes_data['timeseries'].insert(loc=len(nodes_data['timeseries'].columns), column=j["label"]+'.fix',value=slp.tolist())

            # Replacing SLP-index with timeseries index
            nodes_data["sinks"].at[i, 'load profile'] = 'timeseries'
            # Replacing Nominal-Value
            nodes_data["sinks"].at[i, 'nominal value'] = 1

        # creates time series for electricity slps
        elif j["load profile"] in elec_slp_list:
            year = datetime.datetime.strptime(str(ts['start date']),
                                              '%Y-%m-%d %H:%M:%S').year
            # Imports standard load profiles
            e_slp = bdew.ElecSlp(year)
            # TODO Discuss if this is right !!! ( dyn_function_h0 )
            demand = e_slp.get_profile({j['load profile']: 1})
            # creates time series based on standard load profiles
            slp = demand.resample(temp_resolution).mean()
            slp_list = [item for sublist in slp.values.tolist() for item in sublist]
            del slp_list[:-int(ts['periods'])]
            nodes_data['timeseries'].insert(
                loc=len(nodes_data['timeseries'].columns),
                column=j["label"] + '.fix', value=slp_list)
            # nodes_data['timeseries'].append(slp, ignore_index=True)

            # Replacing SLP-index with timeseries index
            nodes_data["sinks"].at[i, 'load profile'] = 'timeseries'
            # Replacing Nominal-Value
            nodes_data["sinks"].at[i, 'nominal value'] = j['annual demand']


        elif j["load profile"] == "timeseries":
            pass
        else:
            raise ValueError('Invalid Load Profile for '+ str(j["label"]))

    # Add newly created slp-timeseries to timeseries dataframe
    # nodes_data['timeseries'] = nodes_data['timeseries'].append(slp_profiles, ignore_index=True, sort=False)


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
            :int(len(nodes_data['timeseries']) / (clusters * 7))]
    nodes_data['timeseries'] = prep_timeseries


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
    from program_files.preprocessing.data_preparation_algorithms \
        import slicing, downsampling, averaging, heuristic_selection, \
        random_sampling, k_means_medoids
    
    data_prep = timeseries_prep_param[0]
    days_per_cluster = timeseries_prep_param[1]
    n_timesteps = timeseries_prep_param[1]
    cluster_criterion = timeseries_prep_param[2]
    cluster_period = timeseries_prep_param[3]
    cluster_seasons = int(timeseries_prep_param[4])

    if data_prep != 'none':
        # Adapting Standard Load Profile-Sinks
        slp_sink_adaption(nodes_data)

    # K-MEANS ALGORITHM
    if data_prep == 'k_means':
        k_means_medoids.k_means_algorithm(cluster_period=cluster_period,
                                          days_per_cluster=days_per_cluster,
                                          criterion=cluster_criterion,
                                          nodes_data=nodes_data,
                                          period=cluster_period)

    # K-MEDOIDS ALGORITHM
    if data_prep == 'k_medoids':
        k_means_medoids.k_medoids_algorithm(cluster_period=cluster_period,
                                            days_per_cluster=days_per_cluster,
                                            criterion=cluster_criterion,
                                            nodes_data=nodes_data,
                                            period=cluster_period)

    # AVERAGING ALGORITHM
    elif data_prep == 'averaging':
        averaging.timeseries_averaging(cluster_period=cluster_period,
                                       days_per_cluster=days_per_cluster,
                                       nodes_data=nodes_data,
                                       period=cluster_period)

    # SLICING ALGORITHM
    # use every n-th period
    elif data_prep == 'slicing A':
        slicing.timeseries_slicing(n_days=int(days_per_cluster),
                                   nodes_data=nodes_data,
                                   period=cluster_period),
    # delete every n-th period
    elif data_prep == 'slicing B':
        slicing.timeseries_slicing2(n_days=int(days_per_cluster),
                                    nodes_data=nodes_data,
                                    period=cluster_period),

    # DOWNSAMPLING ALGORITHM
    # use every n-th period
    elif data_prep == 'downsampling A':
        downsampling.timeseries_downsampling(nodes_data=nodes_data,
                                             n_timesteps=int(n_timesteps))
    # delete every n-th period
    elif data_prep == 'downsampling B':
        downsampling.timeseries_downsampling2(nodes_data=nodes_data,
                                              n_timesteps=int(n_timesteps))

    # HEURISTIC SELECTION ALGORITHM
    elif data_prep == 'heuristic selection':
        heuristic_selection.hierarchical_selection(nodes_data=nodes_data,
                                                   scheme=int(n_timesteps),
                                                   period=cluster_period,
                                                   seasons=cluster_seasons,
                                                   scheme_path=scheme_path)

    elif data_prep == 'random sampling':
        random_sampling.random_sampling(nodes_data=nodes_data,
                                        period=cluster_period,
                                        number_of_samples=int(n_timesteps))

    # ADAPTS THE PARAMETERS OF THE ENERGY SYSTEM
    if data_prep != 'none':
        path = result_path + "/modified_scenario.xlsx"
        writer = pd.ExcelWriter(path, engine='xlsxwriter')
        nodes_data['weather data'].to_excel(writer, sheet_name='weather data')
        nodes_data['timeseries'].to_excel(writer, sheet_name='time series')
        nodes_data['energysystem'].to_excel(writer, sheet_name='energysystem')
        nodes_data['sinks'].to_excel(writer, sheet_name='sinks')
        writer.close()
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
    
    for sheet in [*nodes_data]:
        switch_dict = {
            'constraint cost limit': 'cost limit',
            'cost limit': 'constraint cost limit',
            'variable costs': 'variable constraint costs',
            'variable constraint costs': 'variable costs',
            'periodical constraint costs': 'periodical costs',
            'periodical costs': 'periodical constraint costs',
            'variable output constraint costs': 'variable output costs',
            'variable output costs': 'variable output constraint costs',
            'variable output constraint costs 2': 'variable output costs 2',
            'variable output costs 2': 'variable output constraint costs 2',
            'variable input constraint costs': 'variable input costs',
            'variable input costs': 'variable input constraint costs',
            'excess constraint costs': 'excess costs',
            'excess costs': 'excess constraint costs',
            'shortage constraint costs': 'shortage costs',
            'shortage costs': 'shortage constraint costs',
            'fix investment constraint costs': 'fix investment costs',
            'fix investment costs': 'fix investment constraint costs'}
    
        column_names = nodes_data[sheet].columns.values
        column_names_list = column_names.tolist()
    
        column_names_list = [
            (switch_dict.get(x) if x in switch_dict.keys() else x)
            for x in column_names_list]
    
        nodes_data[sheet].columns = column_names_list
