"""
    Christian Klemm - christian.klemm@fh-muenster.de
"""
from program_files.preprocessing.data_preparation \
    import k_means_parameter_adaption


def timeseries_downsampling(nodes_data: dict, n_timesteps: int):
    """
        uses every n-th period of timeseries and weather data

        :param nodes_data: system parameters
        :type nodes_data: dict
        :param n_timesteps: defines which period is chosen
        :type n_timesteps: int

    """
    end_date = nodes_data['energysystem']['end date'].copy()
    periods = round(nodes_data["energysystem"]["periods"] / n_timesteps, 0)
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
                                            ['periods'] / n_timesteps),
                               period="hours")
    # bring periods and end date back to the old value due to
    # manipulating the temporal resolution
    nodes_data['energysystem']['periods'] = periods
    nodes_data['energysystem']['end date'] = end_date


def timeseries_downsampling2(nodes_data: dict, n_timesteps: int):
    """
        cuts every n-th period of timeseries and weather data

        :param nodes_data: system parameters
        :type nodes_data: dict
        :param n_timesteps: defines which period is cut
        :type n_timesteps: int
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
