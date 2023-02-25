"""
    Christian Klemm - christian.klemm@fh-muenster.de
"""

import random
import pandas

from program_files.preprocessing.data_preparation \
    import k_means_parameter_adaption, extract_single_periods


def random_sampling(nodes_data: dict, period: str, number_of_samples: int):
    """
        TODO Docstring
        
        :param nodes_data: dictionary containing the model \
            definition's data
        :type nodes_data: dict
        :param period: str containing the slicing period type chosen \
            within the GUI
        :type period: str
        :param number_of_samples: TODO ...
        :type number_of_samples: int
        
        :raise: - **ValueError** - Error raised if the chosen period \
            is not supported
    """
    weather_data = nodes_data['weather data']
    data_set = nodes_data['weather data']
    prep_data_set = pandas.DataFrame()
    cluster_vectors = extract_single_periods(data_set=weather_data,
                                             column_name='temperature',
                                             period=period)

    # generate random integers
    random_integers = []
    for i in range(number_of_samples):
        random.seed(i)
        random_int = random.randint(0, len(cluster_vectors)-1)
        random_integers.append(random_int)

    column_names = [data_set.columns[i]
                    for i in range(1, len(data_set.columns))]

    for i in range(len(column_names)):
        # Extract individual weather data set for the current weather
        # data column
        data_set_column = extract_single_periods(data_set=data_set,
                                                 column_name=column_names[i],
                                                 period=period)

        reference_data_set = []
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
                               clusters=int(adaption_clusters),
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
