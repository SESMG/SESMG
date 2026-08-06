"""
    Christian Klemm - christian.klemm@fh-muenster.de
"""
import pandas
from program_files.preprocessing.data_preparation \
    import variable_costs_date_adaption


def update_temporal_resolution(current_res: str, n_timesteps: int) -> str:
    """
        Updates the temporal resolution string (e.g., '1h', '15min') by multiplying
        it with the given downsampling factor (n_timesteps) using pandas timedeltas.

        :param current_res: current temporal resolution as string (e.g., '1h', '15min')
        :type current_res: str
        :param n_timesteps: downsampling factor / step size
        :type n_timesteps: int

        :return: - **str** - updated temporal resolution string in the appropriate unit
    """
    current_res = str(current_res).strip()

    # If the string starts directly with a unit letter instead of a digit (e.g. 'h' instead of '1h'), prepend '1'
    if current_res and not current_res[0].isdigit():
        current_res = f"1{current_res}"

    # Calculate total delta based on timedelta multiplication
    total_delta = pandas.to_timedelta(current_res) * n_timesteps
    seconds = total_delta.total_seconds()

    # Determine the best matching unit for output formatting
    if seconds % 86400 == 0:
        val = seconds / 86400
        return f"{val:g}d"
    elif seconds % 3600 == 0 or seconds >= 3600:
        val = seconds / 3600
        return f"{val:g}h"
    elif seconds % 60 == 0 or seconds >= 60:
        val = seconds / 60
        return f"{val:g}min"
    elif seconds >= 1:
        return f"{seconds:g}s"
    else:
        ms = seconds * 1000
        return f"{ms:g}ms"


def timeseries_downsampling(nodes_data: dict, n_timesteps: int, time_increment: float) -> tuple:
    """
        Performs downsampling on timeseries and weather data by taking
        every n-th timestep based on the specified step size.

        :param nodes_data: dictionary containing system parameters, weather data, and timeseries
        :type nodes_data: dict
        :param n_timesteps: interval or step size for downsampling
        :type n_timesteps: int
        :param time_increment: original temporal resolution in hours
        :type time_increment: float

        :return: - **variable_cost_factor** (float) - factor that considers the data_preparation_algorithms,
                     can be used to scale the results up for a year

    """
    # Backup original end date and calculate adjusted periods count
    end_date = nodes_data['energysystem']['end date'].copy()
    periods = round(int(nodes_data["energysystem"]["periods"].item()) / n_timesteps, 0)
    # shortening timeseries and weather data
    nodes_data['timeseries'] = \
        nodes_data['timeseries'].iloc[::n_timesteps, :]
    nodes_data['weather data'] = \
        nodes_data['weather data'].iloc[::n_timesteps, :]
    # Update the temporal resolution string in the energysystem metadata
    current_res = str(nodes_data['energysystem']['temporal resolution'].item())
    nodes_data['energysystem']['temporal resolution'] = update_temporal_resolution(
                                                            current_res=current_res,
                                                            n_timesteps=n_timesteps)
    # Calculate clusters for cost and date adaptation
    clusters = int(nodes_data['energysystem']['periods'].item() / n_timesteps)

    # Define original and new time increments for resolution scaling
    time_increment_orig = time_increment
    time_increment_new = time_increment_orig * n_timesteps
    
    variable_cost_factor = variable_costs_date_adaption(nodes_data=nodes_data,
                                 clusters=clusters,
                                 period="hours",
                                 time_increment_orig=time_increment_orig,
                                 time_increment_new=time_increment_new)

    # bring periods and end date back to the old value due to
    # manipulating the temporal resolution
    nodes_data['energysystem']['periods'] = periods
    nodes_data['energysystem']['end date'] = end_date

    return variable_cost_factor, time_increment_new


def timeseries_downsampling2(nodes_data: dict, n_timesteps: int) -> float:
    """
        cuts every n-th period of timeseries and weather data

        :param nodes_data: system parameters
        :type nodes_data: dict
        :param n_timesteps: defines which period is cut
        :type n_timesteps: int

        :return: - **variable_cost_factor** (float) - factor that considers the data_preparation_algorithms,
                     can be used to scale the results up for a year
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
    variable_cost_factor = variable_costs_date_adaption(nodes_data=nodes_data,
                                 clusters=int(len(prep_timeseries)),
                                 period="hours")

    return variable_cost_factor
