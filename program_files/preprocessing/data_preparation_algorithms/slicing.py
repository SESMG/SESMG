"""
    Christian Klemm - christian.klemm@fh-muenster.de
"""
import pandas

from program_files.preprocessing.data_preparation \
    import extract_single_periods, variable_costs_date_adaption


def adaption_energy_system_parameter(prep_weather_data: pandas.DataFrame,
                                     nodes_data: dict, period: str,
                                     weather_data: pandas.DataFrame):
    """
        Within this method the adaption clusters are calculated and the
        energy system parameters are adapted afterwards.
        
        :param prep_weather_data: dataframe containing the sliced \
            weather data data frame
        :type prep_weather_data: pandas.DataFrame
        :param nodes_data: dictionary containing the model \
            definition's data
        :type nodes_data: dict
        :param period: str containing the slicing period type chosen \
            within the GUI
        :type period: str
        :param weather_data: unsliced weather data DataFrame
        :type weather_data: pandas.DataFrame
    
        :raise: - **ValueError** - Error raised if the chosen period \
            is not supported

        :return: - **variable_cost_factor** (str) - factor that considers the data_preparation_algorithms,
                    can be used to scale the results up for a year
    """
    # Rename columns of the new weather_dataset
    prep_weather_data['timestamp'] = \
        weather_data['timestamp'][:len(prep_weather_data)]

    # Replaces the weather data set in nodes_data by the new one
    nodes_data['weather data'] = prep_weather_data

    if period == 'days':
        adaption_clusters = len(prep_weather_data) / 24
    elif period == 'weeks':
        adaption_clusters = len(prep_weather_data) / (24 * 7)
    elif period == 'hours':
        adaption_clusters = len(prep_weather_data)
    else:
        raise ValueError("Non supported period")
    
    # Adapts Other Parameters (despite weather data) of the energy system
    variable_cost_factor = variable_costs_date_adaption(nodes_data=nodes_data,
                                 clusters=adaption_clusters,
                                 period=period)

    return variable_cost_factor


def data_set_slicing(n_days: int, data_set: pandas.DataFrame, period: str
                     ) -> pandas.DataFrame:
    """
        uses every n-th period of the given data_set and cuts the rest
        out of the data_set

        :param n_days: defines which period is chosen
        :type n_days: int
        :param data_set: data to be sliced
        :type data_set: pandas.core.frame.Dataframe
        :param period: defines rather hours, days or weeks were selected
        :type period: str
        
        :return: - **prep_data_set** (pandas.DataFrame) - return the \
            sliced pandas.DataFrame
    """
    
    column_names = [data_set.columns[i] for i in
                    range(1, len(data_set.columns))]
    
    prep_data_set = pandas.DataFrame()
    
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


def data_set_slicing2(n_days: int, data_set: pandas.DataFrame, period: str
                      ) -> pandas.DataFrame:
    """
        cuts out every nth period from the given data_set and leaves the
        remaining periods for further consideration

        :param n_days: defines which period is sliced
        :type n_days: int
        :param data_set: data to be sliced
        :type data_set: pandas.core.frame.Dataframe
        :param period: defines rather hours, days or weeks were selected
        :type period: str
        
        :return: - **prep_data_set** (pandas.DataFrame) - return the \
            sliced pandas.DataFrame
    """
    
    column_names = [data_set.columns[i] for i in
                    range(1, len(data_set.columns))]
    
    prep_data_set = pandas.DataFrame()
    
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
            data_set_column = data_set_column[
                              0:-(len(data_set_column) % n_days)]
        
        sliced_column = data_set_column
        del sliced_column[n_days - 1::n_days]
        
        reference_data_set = []
        for j in range(len(sliced_column)):
            reference_data_set = reference_data_set + sliced_column[j]
        
        # Appends the calculated reference days for the current weather
        # data column to the final weather data set
        prep_data_set[column_names[i]] = reference_data_set
    
    return prep_data_set


def timeseries_slicing(n_days: int, nodes_data: dict, period: str) -> None:
    """
        uses every n-th period of the given data_set and cuts the rest
        out of the data_set

        :param n_days: defines which period is chosen
        :type n_days: int
        :param nodes_data: data to be sliced
        :type nodes_data: dict
        :param period: defines rather hours, days or weeks were selected
        :type period: str

        :return: - **variable_cost_factor** (str) - factor that considers the data_preparation_algorithms,
                    can be used to scale the results up for a year
    """
    
    weather_data = nodes_data['weather data']
    data_set = nodes_data['weather data']
    
    prep_weather_data = data_set_slicing(n_days,
                                         data_set=data_set,
                                         period=period)

    variable_cost_factor = adaption_energy_system_parameter(prep_weather_data=prep_weather_data,
                                     nodes_data=nodes_data,
                                     period=period,
                                     weather_data=weather_data)
    
    prep_timeseries = data_set_slicing(n_days,
                                       data_set=nodes_data['timeseries'],
                                       period=period)
    prep_timeseries['timestamp'] = \
        nodes_data['timeseries']['timestamp'][:len(prep_weather_data)]
    nodes_data['timeseries'] = prep_timeseries

    return variable_cost_factor


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

        :return: - **variable_cost_factor** (str) - factor that considers the data_preparation_algorithms,
                    can be used to scale the results up for a year
    """
    weather_data = nodes_data['weather data']
    data_set = nodes_data['weather data']
    
    prep_weather_data = data_set_slicing2(n_days,
                                          data_set=data_set,
                                          period=period)

    variable_cost_factor = adaption_energy_system_parameter(prep_weather_data=prep_weather_data,
                                     nodes_data=nodes_data,
                                     period=period,
                                     weather_data=weather_data)
    
    prep_timeseries = data_set_slicing2(n_days,
                                        data_set=nodes_data['timeseries'],
                                        period=period)
    prep_timeseries['timestamp'] = \
        nodes_data['timeseries']['timestamp'][:len(prep_weather_data)]
    nodes_data['timeseries'] = prep_timeseries

    return variable_cost_factor
