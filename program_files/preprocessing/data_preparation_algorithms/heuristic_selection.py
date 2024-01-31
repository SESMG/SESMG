"""
    Christian Klemm - christian.klemm@fh-muenster.de
"""
import datetime
import pandas
import os

from program_files.preprocessing.data_preparation \
    import variable_costs_date_adaption, append_timeseries_to_weatherdata_sheet


def hierarchical_selection(nodes_data: dict, scheme: str, period: str,
                           seasons: int):
    """
        Algorithm for the hierarchical selection of representative time
        periods of a weather data set. In this embodiment, the following
        representative periods are selected for every season
        (winter, spring, summer, fall) are selected:

        - Week containing the coldest temperature of the season
        - Week with the lowest average sun duration
        - Week containing the warmest temperature of the season
        - Week with the highest average sun duration


        :param nodes_data: SESMG-nodes data, containing weather data, \
            energy system parameters and timeseries
        :type nodes_data: dict
        :param scheme: ID of heuristic selection scheme to be applied
        :type scheme: str
        :param period: specifies whether 'days' or 'weeks' are applied \
            as heuristic selection reference periods
        :type period: str
        :param seasons: number of seasons for hierarchical selections, \
            e.g. 12 for months or 4 for annual seasons
        :type seasons: int
        :return: - **nodes_data** (dict): modified SESMG-nodes data, \
                    containing weather data, energy system parameters \
                    and timeseries
                 - **variable_cost_factor** (str) - factor that considers the data_preparation_algorithms,
                    can be used to scale the results up for a year

    """
    
    def extract_data_slices(data_set: pandas.DataFrame, timesteps: int
                            ) -> list:
        """
            extracts slices of a defined length of a dataset. E.g.
            slices of weeks
            (168 timesteps) of a weather data set may be extracted.

            :param data_set: Data set from which the slices are extracted
            :type data_set: pandas.DataFrame
            :param timesteps: length of the to extracted slices
            :type timesteps: int
            
            :return: - **list_of_data_slices** (list) - extracted \
                slices of the given data set
        """
        list_of_data_slices = []
        for i in range(len(data_set) // timesteps):
            period_data_set = data_set[i * timesteps:(i + 1) * timesteps]
            list_of_data_slices.append(period_data_set)
        return list_of_data_slices
    
    def identify_timeseries_minimum(data_set: pandas.DataFrame,
                                    column_name: str) -> float:
        """
            returns the minimum value of a certain column of a given
            data_set

            :param data_set: Data set from which the slices are extracted
            :type data_set: pandas.DataFrame
            :param column_name: column under investigation
            :type column_name: str
            
            :return: - **-** (float) - minimum value of a column
        """
        return min(data_set[column_name])
    
    def identify_minimum_week(data_set: pandas.DataFrame, criterion: str,
                              value: str) -> pandas.DataFrame:
        """
            Returns the week with a minimum value of a certain column.
            Either the week with the absolute minimum value, or the
            week with the average minimum value can be selected.

            :param data_set: Data set from which the slices are \
                extracted
            :type data_set: pandas.DataFrame
            :param criterion: column, which is the criterion of the \
                selection
            :type criterion: str
            :param value: 'extreme' for absolute minimum value, \
                'average' for average minimum value selection
            :type value: str
            
            :return: - **minimum_week** (pandas.Dataframe) - Dataset \
                of the selected minimum week
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
    
    def identify_timeseries_maximum(data_set: pandas.DataFrame,
                                    column_name: str) -> float:
        """
            returns the maximum value of a certain column of a given
            data_set

            :param data_set: Data set from which the slices are \
                extracted
            :type data_set: pandas.DataFrame
            :param column_name: column under investigation
            :type column_name: str
            
            :return: - **-** (float) - maximum value of a column
        """
        return max(data_set[column_name])
    
    def identify_timeseries_average(data_set: pandas.DataFrame,
                                    column_name: str) -> float:
        """
            returns the average value of a certain column of a given
            data_set.

            :param data_set: Data set from which the slices are \
                extracted
            :type data_set: pandas.DataFrame
            :param column_name: column under investigation
            :type column_name: str
            :return: - **-** (float) - average of a column
        """
        list = data_set[column_name]
        return 0 if len(list) == 0 else sum(list) / len(list)
    
    def identify_maximum_week(data_set: pandas.DataFrame, criterion: str,
                              value: str) -> pandas.DataFrame:
        """
            Returns the week with a maximum value of a certain column.
            Either the week with the absolute maximum value, or the
            week with the average maximum value can be selected.

            :param data_set: Data set from which the slices are \
                extracted
            :type data_set: pandas.DataFrame
            :param criterion: column, which is the criterion of the
                              selection
            :type criterion: str
            :param value: 'extreme' for absolute maximum value,
                          'average' for average maximum value selection
            :type value: str
            :return: - **maximum_week** (pandas.Dataframe) - Dataset \
                of the selected maximum week
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
    
    def identify_average_week(data_set: pandas.DataFrame,
                              criterion: str) -> pandas.DataFrame:
        """
            Returns the week with the most average series of a certain
            column.

            :param data_set: Data set from which the slices are \
                extracted
            :type data_set: pandas.DataFrame
            :param criterion: column, which is the criterion of the
                              selection
            :type criterion: str
            :return: - **average_data** (pandas.Dataframe) - Dataset \
                of the selected average week
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
    
    def reorder_weather_data() -> None:
        """
            Reorder weather data set due to the meteorological beginning
            of winter on the 01.12.
        """
        old_start_date = nodes_data['energysystem']['start date'][1]
        old_end_date = nodes_data['energysystem']['end date'][1]
        if int(old_end_date.day) == 30:
            nodes_data['energysystem'][
                'start date'] = datetime.datetime.strptime(
                    str(int(old_start_date.year) - 1) + "-12-02 00:00:00",
                    '%Y-%m-%d %H:%M:%S')
        else:
            nodes_data['energysystem'][
                'start date'] = datetime.datetime.strptime(
                    str(int(old_start_date.year) - 1) + "-12-01 00:00:00",
                    '%Y-%m-%d %H:%M:%S')
        nodes_data['energysystem']['end date'] = datetime.datetime.strptime(
                str(old_end_date.year) + "-11-30 23:00:00",
                '%Y-%m-%d %H:%M:%S')
        nodes_data["timeseries"] = append_timeseries_to_weatherdata_sheet(
                nodes_data)
        old_timeseries = nodes_data["timeseries"].copy()
        
        nodes_data["timeseries"] = old_timeseries[-30 * 24:]
        nodes_data["timeseries"] = nodes_data["timeseries"].append(
                old_timeseries[:-30 * 24])
        
        for i in range(8040, 8759):
            nodes_data['timeseries'].loc[i, 'timestamp'] = \
                nodes_data['timeseries']['timestamp'][i].replace(
                        year=int(old_start_date.year - 1))
        nodes_data["timeseries"].reset_index(inplace=True, drop=False)
        nodes_data["weather data"] = nodes_data["timeseries"].copy()
    
    def create_period_weather_data(period: str) -> list:
        """
             Splits the weather data_set in nodes_data into weekly od
             daily weather data sets

             :param period: defines rather dayly or weekly weather \
                data set is created
             :type period: str
             :return: **-** (list) - shortened weather \
                data data set
        """
        # Splits the given weather data_set in nodes_data into weekly
        # weather data sets
        if period == 'weeks':
            period_length = 24 * 7
        elif period == 'days':
            period_length = 24
        else:
            raise ValueError("Non supported period")
        
        return extract_data_slices(data_set=nodes_data['weather data'],
                                   timesteps=period_length)
    
    def create_period_season_weather_data(period_data_slices: list,
                                          seasons: int) -> list:
        """
            Splits a given weather data (one year) set into weekly
            weather data slices and sorts them into lists of every
            season of the year (each season is defined by a length of
            13 weeks) and returns a list, containing a list of weather
            data weeks for every season.


            :param period_data_slices: weather data already shortend \
                to daily or weakly resolution
            :type period_data_slices: list
            :param seasons: number of seasons
            :type seasons: int
            
            :return: - **season_data** (list) - list, containing list \
                of weekly weather data slices of every season.
        """
        
        season_length = len(period_data_slices) // seasons
        
        # Sorts the weekly weather data sets into seasons. One season is
        # defined by 13 consecutive weeks here
        season_data = []
        for i in range(seasons):
            periods_data = period_data_slices[season_length
                                              * i:season_length * (i + 1)]
            season_data.append(periods_data)
        
        return season_data
    
    def select_heuristic_periods(heuristic_periods: list,
                                 period_data_slices: list,
                                 season_data: list,
                                 seasons: int):
        """
            Selects and returns representative values of time series
            according to a given heuristic scheme.

            :param heuristic_periods: defined heuristic periods to be \
                selected
            :type heuristic_periods: list
            :param period_data_slices: list containing the periods \
                data slices
            :type period_data_slices: list
            :param season_data: containing list of weekly weather data \
                slices of every season.
            :type season_data: list
            :param seasons: number of seasons for hierarchical \
                selections, e.g. 12 for months or 4 for annual seasons
            :type seasons: int
            :return - **prep_weather_data** (pandas.DataFrame) - \
                dataframe containing the sampled weather data data frame
                    - **variable_cost_factor** (str) - factor that considers the data_preparation_algorithms,
                can be used to scale the results up for a year
        """
        prep_weather_data = pandas.DataFrame()
        
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
                    data_set = season_data[int(representative[0]) - 1]
                
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

    # get scheme path for heuristic selection from technical data folder
    scheme_path = \
        os.path.join(os.path.dirname(os.path.dirname(__file__)),
                     '..',
                     'technical_data/hierarchical_selection_schemes.xlsx')
    
    reorder_weather_data()
    period_data_slices = create_period_weather_data(period=period)
    season_data = create_period_season_weather_data(
        period_data_slices=period_data_slices, seasons=seasons)
    prep_weather_data = pandas.DataFrame()
    scheme_df = pandas.read_excel(scheme_path, sheet_name=str(scheme))
    heuristic_periods = scheme_df.values.tolist()
    prep_weather_data = select_heuristic_periods(
        heuristic_periods=heuristic_periods,
        period_data_slices=period_data_slices,
        season_data=season_data,
        seasons=seasons)
    
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
    
    variable_cost_factor = variable_costs_date_adaption(nodes_data=nodes_data,
                                 clusters=int(len(nodes_data['weather data'])
                                              / period_length),
                                 period=period)

    return variable_cost_factor
