"""
    Christian Klemm - christian.klemm@fh-muenster.de
"""

import random
import pandas

from program_files.preprocessing.data_preparation \
    import variable_costs_date_adaption, extract_single_periods


def create_new_random_data_set(random_integers: list,
                               data_set: pandas.DataFrame, period: str,
                               weatherdata_or_timeseries=True):
    """
        In this method, the new DataFrames for the subsequent
        optimization of the energy system are created and returned to
        the main method.
    
        :param random_integers: list of randomly created integers
        :type random_integers: list
        :param data_set: DataFrame to be prepared for upcoming \
            optimization
        :type data_set: pandas.DataFrame
        :param period: user chosen period type
        :type period: str
        :param weatherdata_or_timeseries: boolean which defines rather \
            the considered DataFrame is weather data (True) or \
            timeseries (False)
        :type weatherdata_or_timeseries: bool
    """
    column_names = [data_set.columns[i]
                    for i in range(1, len(data_set.columns))]
    # create an empty DataFrame for upcoming adaption
    prep_data_set = pandas.DataFrame()
    
    for index in range(len(column_names)):
        # Extract individual weather data set for the current weather
        # data column
        data_set_column = extract_single_periods(
            data_set=data_set,
            column_name=column_names[index],
            period=period)

        reference_data_set = []
        for r_index in range(len(random_integers)):
            column = r_index if weatherdata_or_timeseries \
                else random_integers[r_index]
            reference_data_set += data_set_column[column]

        # Appends the calculated reference days for the current weather
        # data column to the final weather data set
        prep_data_set[column_names[index]] = reference_data_set
    
    return prep_data_set


def random_sampling(nodes_data: dict, period: str, number_of_samples: int):
    """
        In the Random Sampling method, the time series and weather data
        Dataframes are truncated to the time horizon selected by the
        user by randomly selecting time steps from the DataFrames.
        
        :param nodes_data: dictionary containing the user's model \
            definition's data
        :type nodes_data: dict
        :param period: str containing the slicing period type chosen \
            within the GUI
        :type period: str
        :param number_of_samples: amount of samples randomly selected \
            within this method
        :type number_of_samples: int
        
        :raise: - **ValueError** - Error raised if the chosen period \
            is not supported
    """
    # create two local copies of the nodes data weather data sheet
    weather_data = nodes_data['weather data']
    data_set = nodes_data['weather data']
    
    # extract the periods based on the temperature
    cluster_vectors = extract_single_periods(data_set=weather_data,
                                             column_name='temperature',
                                             period=period)

    # generate a list of (amount = number of samples) random integers
    random_integers = []
    for sample in range(number_of_samples):
        random.seed(sample)
        random_int = random.randint(0, len(cluster_vectors)-1)
        random_integers.append(random_int)

    prep_weather_data = create_new_random_data_set(
        random_integers=random_integers,
        data_set=data_set,
        period=period)

    # Rename columns of the new weather_dataset
    prep_weather_data['timestamp'] = \
        weather_data['timestamp'][:len(prep_weather_data)]

    # Replaces the weather data set in nodes_data by the new one
    nodes_data['weather data'] = prep_weather_data.copy()

    # Adapts Other Parameters (despite weather data) of the energy system
    period_dict = {"days": 24, "weeks": 168}
    try:
        adaption_clusters = int(len(prep_weather_data)
                                / period_dict.get(period))
    except TypeError:
        raise ValueError("Non supported period")

    # adapt costs and energy system date range
    variable_costs_date_adaption(nodes_data=nodes_data,
                                 clusters=int(adaption_clusters),
                                 period=period)

    data_set = nodes_data['timeseries']
    
    prep_timeseries = create_new_random_data_set(
        random_integers=random_integers,
        data_set=data_set,
        period=period,
        weatherdata_or_timeseries=False)

    prep_timeseries['timestamp'] = \
        nodes_data['timeseries']['timestamp'][:len(prep_weather_data)]
    nodes_data['timeseries'] = prep_timeseries.copy()
