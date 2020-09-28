# -*- coding: utf-8 -*-
"""Creates oemof energy system components.

Functions for the creation of oemof energy system objects from a given set 
of object parameters.

---
@ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
"""

from oemof import solph
import logging
import os
import pandas as pd
from feedinlib import *
import demandlib.bdew as bdew
import datetime


def buses(nodes_data, nodes):
    """Creates bus objects.
    
    Creates bus objects with the parameters given in 'nodes_data' and adds 
    them to the list of components 'nodes'.

    ----    
        
    Keyword arguments:
        
        nodes_data : obj:'dict'
           -- dictionary containing parameters of the buses to be created. The 
           following parameters have to be provided: label, active, excess, 
           shortage, shortage costs /(CU/kWh), excess costs /(CU/kWh)
        
        nodes : obj:'list'
            -- list of components created before (can be empty)
            
    ----
    
    Returns:
       busd : obj:'dict'
           -- dictionary containing all buses created   
           
    ----    
    @ Christian Klemm - christian.klemm@fh-muenster.de, 13.02.2020
    """
    # creates a list of buses
    busd = {}
    # renames nodes_data
    nd = nodes_data

    # Creates components, which are defined within the "buses"-sheet of
    # the original excel-file
    for i, b in nd['buses'].iterrows():

        # Create a bus object for every bus, which is marked as "active"
        if b['active']:
            # creates an oemof-bus object
            bus = solph.Bus(label=b['label'])
            # adds the bus object to the list of components "nodes"
            nodes.append(bus)
            busd[b['label']] = bus
            # returns logging info
            logging.info('   ' + 'Bus created: ' + b['label'])

            # Create an sink for every bus, which is marked with "excess"
            if b['excess']:
                # creates the oemof-sink object and directly adds it to the list
                # of components "nodes"
                nodes.append(
                    solph.Sink(label=b['label'] + '_excess',
                               inputs={busd[b['label']]: solph.Flow(
                                   variable_costs=b['excess costs /(CU/kWh)'],
                               )}))

            # Create a source for every bus, which is marked with "shortage"
            if b['shortage']:
                # creates the oemof-source object and directly adds it to the list
                # of components "nodes"re
                nodes.append(
                    solph.Source(label=b['label'] + '_shortage',
                                 outputs={busd[b['label']]: solph.Flow(
                                     variable_costs=b['shortage costs /(CU/kWh)'])}))

    # Returns the list of buses as result of the function
    return busd


class Sources:
    """Creates source objects.
    
    Creates source objects with the parameters given in 'nodes_data' and adds 
    them to the list of components 'nodes'. If the parameter 'technology' in 
    nodes_data is labeled as 'commodity source', a source with defined 
    timeseries will be created. If technology is labeled as 'photovoltaic' a 
    photovoltaic system component will be created.

    ----    
        
    Keyword arguments:
        
        nodes_data : obj:'dict'
           -- dictionary containing parameters of sources to be created. The 
           following data have to be provided: label, active, output, 
           technology, variable costs /(CU/kWh), existing capacity /(kW), 
           min. investment capacity /(kW), max. investment capacity /(kW), 
           periodical costs /(CU/(kW a)), technology database (PV ONLY), 
           inverter database (PV ONLY), Modul Model (PV ONLY), 
           Inverter Model (PV ONLY), Azimuth (PV ONLY), 
           Surface Tilt (PV ONLY), Albedo (PV ONLY), Altitude (PV ONLY), 
           Latitude (PV ONLY), Longitude (PV ONLY)
           
        busd : obj:'dict'
           -- dictionary containing the buses of the energy system

        nodes : obj:'list'
            -- list of components created before (can be empty)
            
        filepath : obj:'str'
            -- path to .xlsx scenario-file containing a "weather data" sheet 
            with timeseries for
               - "dhi" (diffuse horizontal irradiation) W/m^2
               - "dirhi" (direct horizontal irradiance) W/m^2
               - "pressure" in Pa
               - "temperature" in °C
               - "windspeed" in m/s
               - "z0" (roughness length) in m
               
    ---- 
    @ Christian Klemm - christian.klemm@fh-muenster.de, 13.02.2020
    """
    # intern variables
    nodes_sources = []
    nodes = []
    busd = None

    def commodity_source(self, so):
        """Creates a source object with unfixed time-series."""

        # Creates a oemof-source object with unfixed time-series
        self.nodes_sources.append(
            solph.Source(label=so['label'],
                         outputs={self.busd[so['output']]: solph.Flow(
                             investment=solph.Investment(
                                 ep_costs=so['periodical costs /(CU/(kW a))'],
                                 minimum=so['min. investment capacity /(kW)'],
                                 maximum=so['max. investment capacity /(kW)'],
                                 existing=so['existing capacity /(kW)'],
                                 nonconvex=True if so['Non-Convex Investment'] == 1 else False,
                                 offset=so['Fix Investment Capacity']),
                             variable_costs=so['variable costs /(CU/kWh)'])}))

        # Returns logging info
        logging.info('   ' + 'Commodity Source created: ' + so['label'])

    def timeseries_source(self, so, filepath):
        """Creates a source object from a pre-defined timeseries time-series."""

        time_series = pd.read_excel(filepath, sheet_name='time_series')
        if so['fixed'] == 1:
            self.nodes_sources.append(
                solph.Source(label=so['label'],
                             outputs={self.busd[so['output']]: solph.Flow(
                                 investment=solph.Investment(
                                                             ep_costs=so['periodical costs /(CU/(kW a))'],
                                                             minimum=so['min. investment capacity /(kW)'],
                                                             maximum=so['max. investment capacity /(kW)'],
                                                             existing=so['existing capacity /(kW)'],
                                                             nonconvex=True if so['Non-Convex Investment'] == 1 else False,
                                                             offset=so['Fix Investment Capacity']),
                                 fix=time_series[so['label']+'.fix'].tolist(),
                                 variable_costs=so['variable costs /(CU/kWh)'])}))
        elif so['fixed'] == 0:
            self.nodes_sources.append(
                solph.Source(label=so['label'],
                             outputs={self.busd[so['output']]: solph.Flow(
                                 investment=solph.Investment(
                                     ep_costs=so['periodical costs /(CU/(kW a))'],
                                     minimum=so['min. investment capacity /(kW)'],
                                     maximum=so['max. investment capacity /(kW)'],
                                     existing=so['existing capacity /(kW)'],
                                     nonconvex=True if so['Non-Convex Investment'] == 1 else False,
                                     offset=so['Fix Investment Capacity']),
                                 min=time_series[so['label']+'.min'].tolist(),
                                 max=time_series[so['label']+'.max'].tolist(),
                                 variable_costs=so['variable costs /(CU/kWh)'])}))

        # Returns logging info
        logging.info('   ' + 'Timeseries Source created: ' + so['label'])

    def pv_source(self, so):
        """Creates photovoltaic source object.

        Simulates the yield of a photovoltaic system using feedinlib and
        creates a source object with the yield as time series.
        """

        # reads pv system parameters from parameter dictionary nodes_data
        parameter_set = {
            'azimuth': so['Azimuth (PV ONLY)'],
            'tilt': so['Surface Tilt (PV ONLY)'],
            'module_name': so['Modul Model (PV ONLY)'],
            'inverter_name': so['Inverter Model (PV ONLY)'],
            'albedo': so['Albedo (PV ONLY)']}

        # sets pv system parameters for pv_module
        pv_module = powerplants.Photovoltaic(**parameter_set)

        # reads weather data from interim-.csv data set
        my_weather_pandas_DataFrame = pd.read_csv(os.path.join(
            os.path.dirname(__file__)) + '/interim_data/weather_data.csv',
                                                  index_col=0,
                                                  date_parser=lambda idx: pd.to_datetime(idx, utc=True))

        # calculates global horizontal irradiance from diffuse (dhi) and direct
        # irradiance and adds it to the weather data frame
        my_weather_pandas_DataFrame['ghi'] = (my_weather_pandas_DataFrame.dirhi
                                              + my_weather_pandas_DataFrame.dhi)

        # changes names of data columns, so it fits the needs of the feedinlib
        name_dc = {'temperature': 'temp_air',
                   'windspeed': 'v_wind'}
        my_weather_pandas_DataFrame.rename(columns=name_dc)

        # calculates time series normed on 1 kW pv peak performance
        feedin = pv_module.feedin(
            weather=my_weather_pandas_DataFrame,
            location=(so['Latitude (PV ONLY)'],
                      so['Longitude (PV ONLY)']),
            scaling='peak_power')

        # Prepare data set for compatibility with oemof      
        for i in range(len(feedin)):
            # Set negative values to zero (requirement for solving the model)
            if feedin[i] < 0:
                feedin[i] = 0
            # Set values greater 1 to 1 (requirement for solving the model)
            if feedin[i] > 1:
                feedin[i] = 1
        # Replace 'nan' value with 0
        feedin = feedin.fillna(0)
        if so['fixed'] == 1:
        # creates oemof-source object and adds it to the list of components
            self.nodes_sources.append(
                solph.Source(label=so['label'],
                             outputs={self.busd[so['output']]: solph.Flow(
                                 investment=solph.Investment(
                                     ep_costs=so['periodical costs /(CU/(kW a))'],
                                     minimum=so['min. investment capacity /(kW)'],
                                     maximum=so['max. investment capacity /(kW)'],
                                     existing=so['existing capacity /(kW)'],
                                     nonconvex=True if so['Non-Convex Investment'] == 1 else False,
                                     offset=so['Fix Investment Capacity']),
                                 fix=feedin,
                                 variable_costs=so['variable costs /(CU/kWh)'])}))
        elif so['fixed'] == 0:
            self.nodes_sources.append(
                solph.Source(label=so['label'],
                             outputs={self.busd[so['output']]: solph.Flow(
                                 investment=solph.Investment(
                                     ep_costs=so['periodical costs /(CU/(kW a))'],
                                     minimum=so['min. investment capacity /(kW)'],
                                     maximum=so['max. investment capacity /(kW)'],
                                     existing=so['existing capacity /(kW)'],
                                     nonconvex=True if so['Non-Convex Investment'] == 1 else False,
                                     offset=so['Fix Investment Capacity']),
                                 max=feedin,
                                 variable_costs=so['variable costs /(CU/kWh)'])}))
        # returns logging info
        logging.info('   ' + 'Source created: ' + so['label'])

    def windpower_source(self, so):
        """Creates windpower source object.

        Simulates the yield of a windturbine using feedinlib and
        creates a source object with the yield as time series.
        """

        # set up wind turbine using the wind turbine library. The turbine name must
        # correspond to an entry in the turbine data-base of the feedinlib. Unit of
        # the hub height is m.
        turbine_data = {
            'turbine_type': so['Turbine Model (Windpower ONLY)'],
            'hub_height': so['Hub Height (Windpower ONLY)']
        }
        wind_turbine = WindPowerPlant(**turbine_data)

        # set up weather dataframe for windpowerlib
        weather_df_wind = pd.read_csv(os.path.join(
            os.path.dirname(__file__)) + '/interim_data/weather_data.csv',
                                      index_col=0,
                                      date_parser=lambda idx: pd.to_datetime(idx, utc=True))

        # change type of index to datetime and set time zone
        weather_df_wind.index = pd.to_datetime(weather_df_wind.index).tz_convert(
            'Europe/Berlin')
        data_height = {
            'pressure': 0,
            'temperature': 2,
            'wind_speed': 10,
            'roughness_length': 0}
        weather_df_wind = weather_df_wind[['windspeed', 'temperature', 'z0', 'pressure']]
        weather_df_wind.columns = [['wind_speed', 'temperature', 'roughness_length',
                                    'pressure'],
                                   [data_height['wind_speed'],
                                    data_height['temperature'],
                                    data_height['roughness_length'],
                                    data_height['pressure']]]

        # calculate scaled feed-in
        feedin_wind_scaled = wind_turbine.feedin(
            weather=weather_df_wind,
            scaling='nominal_power')

        if so['fixed'] == 1:
            # creates oemof source object and adds it to the list of components
            self.nodes_sources.append(
                solph.Source(label=so['label'],
                             outputs={self.busd[so['output']]: solph.Flow(
                                 investment=solph.Investment(
                                     ep_costs=so['periodical costs /(CU/(kW a))'],
                                     minimum=so['min. investment capacity /(kW)'],
                                     maximum=so['max. investment capacity /(kW)'],
                                     existing=so['existing capacity /(kW)'],
                                     nonconvex=True if so['Non-Convex Investment'] == 1 else False,
                                     offset=so['Fix Investment Capacity']),
                                 fix=feedin_wind_scaled,
                                 variable_costs=so['variable costs /(CU/kWh)'])}))
        elif so['fixed'] == 0:
            self.nodes_sources.append(
                solph.Source(label=so['label'],
                             outputs={self.busd[so['output']]: solph.Flow(
                                 investment=solph.Investment(
                                     ep_costs=so['periodical costs /(CU/(kW a))'],
                                     minimum=so['min. investment capacity /(kW)'],
                                     maximum=so['max. investment capacity /(kW)'],
                                     existing=so['existing capacity /(kW)'],
                                     nonconvex=True if so['Non-Convex Investment'] == 1 else False,
                                     offset=so['Fix Investment Capacity']
                                     ),
                                 max=feedin_wind_scaled,
                                 variable_costs=so['variable costs /(CU/kWh)'])}))
        # returns logging info
        logging.info('   ' + 'Source created: ' + so['label'])

    def __init__(self, nodes_data, nodes, busd, filepath):

        # rename variables
        self.nodes = []
        self.nodes_sources = []
        self.busd = busd.copy()
        self.nodes_data = nodes_data
        for i in range(len(nodes)):
            self.nodes.append(nodes[i])

        # Create Source from "Sources" Table
        for i, so in nodes_data['sources'].iterrows():

            # Create a source object for every source, which is marked as "active"
            if so['active']:

                # Create Commodity Sources
                if so['technology'] == 'other':
                    self.commodity_source(so)

                # Create Photovoltaic Sources
                elif so['technology'] == 'photovoltaic':
                    self.pv_source(so)

                # Create Windpower Sources
                elif so['technology'] == 'windpower':
                    self.windpower_source(so)

                # Create Time-series Sources
                elif so['technology'] == 'timeseries':
                    self.timeseries_source(so, filepath)

        # The feedinlib can only read .csv data sets, so the weather data from
        # the .xlsx scenario file have to be converted into a .csv data set and
        # saved
        read_file = pd.read_excel(filepath, sheet_name='weather data')
        read_file.to_csv(
            os.path.join(os.path.dirname(__file__)) + '/interim_data/weather_data.csv',
            index=None,
            header=True)

        # appends created sources to the list of nodes
        for i in range(len(self.nodes_sources)):
            nodes.append(self.nodes_sources[i])


class Sinks:
    """Creates sink objects.

    Creates sinks objects with the parameters given in 'nodes_data' and adds
    them to the list of components 'nodes'.

    ----

    Keyword arguments:

        nodes_data : obj:'dict'
           -- dictionary containing parameters of sinks to be created. The
           following data have to be provided: label, active, input, input2,
           load profile, nominal value /(kW), annual demand /(kWh/a),
           occupants [RICHARDSON], building class [HEAT SLP ONLY],
           wind class [HEAT SLP ONLY], fixed

        busd : obj:'dict'
           -- dictionary containing the busses of the energy system

        filepath : obj:'str'
            -- path to .xlsx scenario-file containing a "weather data" sheet
            with timeseries for
               - "dhi" (diffuse horizontal irradiation) W/m^2
               - "dirhi" (direct horizontal irradiance) W/m^2
               - "pressure" in Pa
               - "temperature" in °C
               - "windspeed" in m/s
               - "z0" (roughness length) in m

        nodes : obj:'list'
            -- list of components created before (can be empty)

    ----
    @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
    """
    # intern variables
    busd = None
    nodes = []
    nodes_sinks = []
    nd = None

    def unfixed_sink(self, de):
        """Creates a sink object with an unfixed energy input."""

        # set static inflow values
        inflow_args = {'nominal_value': de['nominal value /(kW)']}

        # creates the sink object and adds it to the list of components
        self.nodes_sinks.append(
            solph.Sink(label=de['label'],
                       inputs={
                           self.busd[de['input']]: solph.Flow(**inflow_args)}))

        # returns logging info
        logging.info('   ' + 'Sink created: ' + de['label'])

    def timeseries_sink(self, de,filepath):
        """Creates a sink with fixed input.

        Creates a sink object with a fixed input. The input must be given
        as a time series in 'nodes_data'.

        ----
        @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
        """
        time_series = pd.read_excel(filepath, sheet_name='time_series')

        if de['fixed'] == 0:
            min = time_series[de['label']+'.min'].tolist()
            max = time_series[de['label']+'.max'].tolist()
            inflow_args = {'min': min, 'max': max, 'nominal_value': de['nominal value /(kW)']}
        elif de['fixed'] == 1:
            fix = time_series[de['label']+'.fix'].tolist()
            inflow_args = {'fix': fix, 'nominal_value': de['nominal value /(kW)']}

        # creates sink object and adds it to the list of components
        self.nodes_sinks.append(
            solph.Sink(label=de['label'],
                       inputs={
                           self.busd[de['input']]: solph.Flow(**inflow_args)}))

        # returns logging info
        logging.info('   ' + 'Sink created: ' + de['label'])

    def slp_sink(self, de):
        """Creates a sink with a residential SLP time series.

        Creates a sink with inputs according to VDEW standard load profiles,
        using oemofs demandlib and adds it to the list of components 'nodes'.
        Used for the modelling of residential ectricity demands.

        ----
        @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
        """
        heat_slps = ['efh', 'mfh']
        heat_slps_commercial = ['gmf', 'gpd', 'ghd', 'gwa', 'ggb', 'gko', 'gbd',
                                'gba', 'gmk', 'gbh', 'gga', 'gha']
        electricity_slps = ['h0', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6',
                            'l0', 'l1', 'l2']
        # Import weather Data
        data = pd.read_csv(os.path.join(
            os.path.dirname(__file__)) + '/interim_data/weather_data.csv')

        # Importing timesystem parameters from the scenario file
        for j, ts in self.nd['timesystem'].iterrows():
            temp_resolution = ts['temporal resolution']
            periods = ts["periods"]
            start_date = str(ts['start date'])
            year = datetime.datetime.strptime(str(ts['start date']),
                                              '%Y-%m-%d %H:%M:%S').year

        # Converting start date into datetime format
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')

        # Create DataFrame
        demand = pd.DataFrame(
            index=pd.date_range(pd.datetime(start_date.year,
                                            start_date.month,
                                            start_date.day,
                                            start_date.hour),
                                periods=periods, freq=temp_resolution))

        # creates time series
        if de['load profile'] in heat_slps:
            demand[de['load profile']] = bdew.HeatBuilding(
                demand.index,
                temperature=data['temperature'],
                shlp_type=de['load profile'],
                building_class=de['building class [HEAT SLP ONLY]'],
                wind_class=de['wind class [HEAT SLP ONLY]'],
                annual_heat_demand=1,
                name=de['load profile']).get_bdew_profile()
        elif de['load profile'] in heat_slps_commercial:
            demand[de['load profile']] = bdew.HeatBuilding(
                demand.index,
                temperature=data['temperature'],
                shlp_type=de['load profile'],
                wind_class=de['wind class [HEAT SLP ONLY]'],
                annual_heat_demand=1,
                name=de['load profile']).get_bdew_profile()
        elif de['load profile'] in electricity_slps:
            # Imports standard load profiles
            e_slp = bdew.ElecSlp(year)
            demand = e_slp.get_profile({de['load profile']: 1})

            # creates time series based on standard load profiles
            demand = demand.resample(temp_resolution).mean()

        if de['fixed'] == 1:
            # create Sink and adds it to the list of components
            self.nodes_sinks.append(
                solph.Sink(label=de['label'],
                           inputs={
                               self.busd[de['input']]: solph.Flow(
                                   nominal_value=de['annual demand /(kWh/a)'],
                                   fix=demand[de['load profile']],
                               )}))
        elif de['fixed'] == 0:
            # create Sink and adds it to the list of components
            self.nodes_sinks.append(
                solph.Sink(label=de['label'],
                           inputs={
                               self.busd[de['input']]: solph.Flow(
                                   nominal_value=de['annual demand /(kWh/a)'],
                                   max=demand[de['load profile']],
                               )}))

        # returns logging info
        logging.info('   ' + 'Sink created: ' + de['label'])

    def richardson_sink(self, de):
        """Creates a sink with stochastical timeseries.

        Creates a sink with stochastical input, using richardson.py and adds it
        to the list of components 'nodes'. Used for the modelling of
        residential electricity demands.

        ----
        @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
        """

        import copy
        import richardsonpy.classes.occupancy as occ
        import richardsonpy.functions.load_radiation as loadrad
        import richardsonpy.classes.electric_load as eload

        # Import Weather Data
        dirhi_csv = pd.read_csv(
            os.path.join(os.path.dirname(__file__))
            + '/interim_data/weather_data.csv',
            usecols=['dirhi'],
            dtype=float)
        dirhi = dirhi_csv.values.flatten()
        dhi_csv = pd.read_csv(
            os.path.join(os.path.dirname(__file__))
            + '/interim_data/weather_data.csv',
            usecols=['dhi'],
            dtype=float)
        dhi = dhi_csv.values.flatten()

        # Conversion of irradiation from W/m^2 to kW/m^2
        dhi = dhi / 1000
        dirhi = dirhi / 1000

        # Reads the temporal resolution from the scenario file
        for i, ts in self.nd['timesystem'].iterrows():
            temp_resolution = ts['temporal resolution']

        # sets the occupancy rates
        nb_occ = de['occupants [RICHARDSON]']

        # Workaround, because richardsonpy only allows a maximum of 5 occupants
        if nb_occ > 5:
            occ_ratio = nb_occ / 5
            nb_occ = 5
        else:
            occ_ratio = 1

        # sets the temporal resolution of the richardsonpy time series,
        # depending on the temporal resolution of the entire model (as
        # defined in the input spreadsheet)
        if temp_resolution == 'H':
            timestep = 3600  # in seconds
        elif temp_resolution == 'h':
            timestep = 3600  # in seconds
        elif temp_resolution == 'min':
            timestep = 60  # in seconds
        elif temp_resolution == 's':
            timestep = 1  # in seconds
        else:
            logging.info('   ' + 'Invalid Temporal Resolution!')

        #  Generate occupancy object (necessary as input for electric load gen)
        occ_obj = occ.Occupancy(number_occupants=nb_occ)

        #  Get radiation (necessary for lighting usage calculation)
        (q_direct, q_diffuse) = loadrad.get_rad_from_try_path()

        # renames radiation variables
        q_direct = dirhi
        q_diffuse = dhi

        #  Generate stochastic electric power object
        el_load_obj = eload.ElectricLoad(occ_profile=occ_obj.occupancy,
                                         total_nb_occ=nb_occ,
                                         q_direct=q_direct,
                                         q_diffuse=q_diffuse,
                                         timestep=timestep)

        #  Copy occupancy object, before changing its resolution
        #  (occ_obj.occupancy is the pointer to the occupancy profile array)
        occ_profile_copy = copy.copy(occ_obj.occupancy)

        # creates richardsonpy time series
        load_profile = el_load_obj.loadcurve
        richardson_demand = (sum(el_load_obj.loadcurve)
                             * timestep / (3600 * 1000))
        annual_demand = de['annual demand /(kWh/a)']

        # Disables the stochastic simulation of the total yearly demand by
        # scaling the generated time series using the total energy demand
        # of the sink generated in the spreadsheet
        demand_ratio = annual_demand / richardson_demand

        if de['fixed'] == 1:
            # create sink and adds it to the list of components
            self.nodes_sinks.append(
                solph.Sink(label=de['label'],
                           inputs={self.busd[de['input']]: solph.Flow(
                               nominal_value=0.001 * demand_ratio,
                               fix=load_profile,
                               )}))
        elif de['fixed'] == 0:
            self.nodes_sinks.append(
                solph.Sink(label=de['label'],
                           inputs={self.busd[de['input']]: solph.Flow(
                               nominal_value=0.001 * demand_ratio,
                               max=load_profile,
                           )}))
        # returns logging info
        logging.info('   ' + 'Sink created: ' + de['label'])

    def __init__(self, nodes_data, busd, nodes, filepath):

        # renames variables
        self.nd = nodes_data
        self.busd = busd
        self.nodes = []
        self.nodes_sinks = []
        for i in range(len(nodes)):
            self.nodes.append(nodes[i])

        # richardson.py and demandlib can only read .csv data sets, so the weather
        # data from the .xlsx scenario file have to be converted into a .csv data
        # set and saved
        read_file = pd.read_excel(filepath, sheet_name='weather data')
        read_file.to_csv(
            os.path.join(os.path.dirname(__file__))
            + '/interim_data/weather_data.csv',
            index=None,
            header=True)

        # Create sink objects
        for i, de in self.nd['demand'].iterrows():
            slps = ['efh', 'mfh','gmf', 'gpd', 'ghd', 'gwa', 'ggb', 'gko', 'gbd',
                                    'gba', 'gmk', 'gbh', 'gga', 'gha','h0', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6',
                                'l0', 'l1', 'l2']
            richardson = ['richardson']

            if de['active']:

                # Create Sinks un-fixed time-series
                if de['load profile'] == 'x':
                    self.unfixed_sink(de)

                # Create Sinks with Time-series
                elif de['load profile'] == 'timeseries':
                    self.timeseries_sink(de, filepath)

                # Create Sinks with SLP's
                elif de['load profile'] in slps:
                    self.slp_sink(de)

                # Richardson
                elif de['load profile'] in richardson:
                    self.richardson_sink(de)

        # appends created sinks on the list of nodes
        for i in range(len(self.nodes_sinks)):
            nodes.append(self.nodes_sinks[i])


class Transformers:
    """Creates a transformer object.

    Creates transformers objects as defined in 'nodes_data' and adds them to
    the list of components 'nodes'.

    ----

    Keyword arguments:

        nodes_data : obj:'dict'
           -- dictionary containing data from excel scenario file. The
           following data have to be provided: label, active, transformer type,
           input, output, output2, efficiency, efficency2,
           variable input costs /(CU/kWh), variable output costs /(CU/kWh),
           existing capacity /(kW), max. investment capacity /(kW),
           min. investment capacity /(kW), periodical costs /(CU/(kW a))

        busd : obj:'dict'
           -- dictionary containing the buses of the energy system

        nodes : obj:'list'
            -- list of components

    ----

    @ Christian Klemm - christian.klemm@fh-muenster.de, 13.02.2020
    """
    # intern variables
    nodes_transformer = []
    nodes = []
    busd = None

    def generic_transformer(self, t):
        """Creates a Generic Transformer object.

                Creates a generic transformer with the parameters given in
                'nodes_data' and adds it to the list of components 'nodes'.

                ----
                @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
                """

        # creates a transformer with only one output, if the field "output2"
        # is marked with 'None', 'none' or 'x'.
        if t['output2'] in ['None', 'none', 'x']:
            # creates transformer object and adds it to the list of components
            self.nodes_transformer.append(
                solph.Transformer(
                    label=t['label'],
                    inputs={self.busd[t['input']]: solph.Flow(
                        variable_costs=t['variable input costs /(CU/kWh)'])},
                    outputs={self.busd[t['output']]: solph.Flow(
                        variable_costs=t['variable output costs /(CU/kWh)'],
                        investment=solph.Investment(
                            ep_costs=t['periodical costs /(CU/(kW a))'],
                            minimum=t['min. investment capacity /(kW)'],
                            maximum=t['max. investment capacity /(kW)'],
                            existing=t['existing capacity /(kW)'],
                            nonconvex=True if t['Non-Convex Investment'] == 1 else False,
                            offset=t['Fix Investment Capacity']
                        ))},
                    conversion_factors={self.busd[t['output']]:
                                        t['efficiency']}))

            # returns logging info
            logging.info('   ' + 'Transformer created: ' + t['label'])

        # creates transformer objects with two outputs, if the field "output2"
        # is NOT marked with "none" or "x"
        else:
            # Defines Capacity values for the second transformer output
            existing_capacity2 = ((t['existing capacity /(kW)'] /
                                   t['efficiency']) * t['efficiency'])
            minimum_capacity2 = ((t['min. investment capacity /(kW)'] /
                                  t['efficiency']) * t['efficiency'])
            maximum_capacity2 = ((t['max. investment capacity /(kW)'] /
                                  t['efficiency']) * t['efficiency'])

            # Creates transformer object and adds it to the list of components
            self.nodes_transformer.append(
                solph.Transformer(
                    label=t['label'],
                    inputs={self.busd[t['input']]: solph.Flow(
                        variable_costs=t['variable input costs /(CU/kWh)'])},
                    outputs={self.busd[t['output']]: solph.Flow(
                        variable_costs=t['variable output costs /(CU/kWh)'],
                        investment=solph.Investment(
                            ep_costs=t['periodical costs /(CU/(kW a))'],
                            minimum=t['min. investment capacity /(kW)'],
                            maximum=t['max. investment capacity /(kW)'],
                            existing=t['existing capacity /(kW)'],
                            nonconvex=True if t['Non-Convex Investment'] == 1 else False,
                            offset=t['Fix Investment Capacity']
                        )),
                        self.busd[t['output2']]: solph.Flow(
                            variable_costs=t['variable output costs 2 /(CU/kWh)'],
                            investment=solph.Investment(
                                ep_costs=0,#t['periodical costs /(CU/(kW a))'],
                                existing=existing_capacity2,
                                minimum=minimum_capacity2,
                                maximum=maximum_capacity2,
                                nonconvex = True if t['Non-Convex Investment'] == 1 else False,
                                offset = t['Fix Investment Capacity']
                            ))},
                    conversion_factors={self.busd[t['output']]:
                                        t['efficiency'],
                                        self.busd[t['output2']]:
                                            t['efficiency2']}))

            # returns logging info
            logging.info('   ' + 'Transformer created: ' + t['label'])

    def genericchp_transformer(self, t):
        """Creates a Generic CHP transformer object.

        Creates a generic chp transformer with the parameters given in
        'nodes_data' and adds it to the list of components 'nodes'.

        ----
        @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
        """
        from pandas.tests.arrays.test_datetimelike import datetime_index
        # counts the number of periods within the given datetime index and saves it as variable
        # (number of periods is required for creating generic chp transformers)
        periods = len(datetime_index)

        # creates genericCHP transformer object and adds it to the list of components
        self.nodes_transformer.append(
            solph.components.GenericCHP(
                label=t['label'],
                fuel_input={self.busd[t['input']]: solph.Flow(
                    H_L_FG_share_max=[t['share of flue gas loss at max heat extraction [GenericCHP]']
                                      for p in range(0, periods)])},
                electrical_output={self.busd[t['output']]: solph.Flow(
                    P_max_woDH=[t['max. electric power without district heating [GenericCHP]'] for p in
                                range(0, periods)],
                    P_min_woDH=[t['min. electric power without district heating [GenericCHP]'] for p in
                                range(0, periods)],
                    Eta_el_max_woDH=[t['el. eff. at max. fuel flow w/o distr. heating [GenericCHP]'] for p in
                                     range(0, periods)],
                    Eta_el_min_woDH=[t['el. eff. at min. fuel flow w/o distr. heating [GenericCHP]'] for p in
                                     range(0, periods)])},
                heat_output={self.busd[t['output2']]: solph.Flow(
                    Q_CW_min=[t['minimal therm. condenser load to cooling water [GenericCHP]'] for p in
                              range(0, periods)])},
                Beta=[t['power loss index [GenericCHP]'] for p in range(0, periods)],
                back_pressure=False))

        # returns logging info
        logging.info('   ' + 'Transformer created: ' + t['label'])

    def __init__(self, nodes_data, nodes, busd):

        # renames variables
        self.busd = busd
        self.nodes = []
        self.nodes_transformer = []
        for i in range(len(nodes)):
            self.nodes.append(nodes[i])

        # creates a transformer object for every transformer item within nd
        for i, t in nodes_data['transformers'].iterrows():
            if t['active']:

                # Create Generic Transformers
                if t['transformer type'] == 'GenericTransformer':
                    self.generic_transformer(t)

                # Create Extraction Turbine CHPs
                elif t['transformer type'] == 'ExtractionTurbineCHP':
                    logging.info('   ' + 'WARNING: ExtractionTurbineCHP are'
                                 + ' currently not a part of this model generator,'
                                 + ' but will be added later.')

                # Create Generic CHPs
                elif t['transformer type'] == 'GenericCHP':
                    self.genericchp_transformer(t)
                    logging.info('   ' + 'WARNING: GenericCHP currently does not support'
                                 + ' investments and variable costs! Will be added'
                                 + ' with upcoming updates')

                # Create Offset Transformers
                elif t['transformer type'] == 'OffsetTransformer':
                    logging.info('   ' + 'WARNING: OffsetTransformer are currently'
                                 + ' not a part of this model generator, but will'
                                 + ' be added later.')

                # Error Message for invalid Transformers
                else:
                    logging.info('   ' + 'WARNING: \''
                                 + t['label']
                                 + '\' was not created, because \''
                                 + t['transformer type']
                                 + '\' is no valid transformer type.')

        # appends created transformers to the list of nodes
        for i in range(len(self.nodes_transformer)):
            nodes.append(self.nodes_transformer[i])


class Storages:
    """Creates storage objects.
    
    Creates storage objects as defined in 'nodes_data' and adds them to the 
    list of components 'nodes'.

    ----    
        
    Keyword arguments:
        
        nodes_data : obj:'dict'
           -- dictionary containing data from excel scenario file. The 
           following data have to be provided: label, active, bus, 
           existing capacity /(kW), min. investment capacity /(kW), 
           max. investment capacity /(kW), periodical costs /(CU/(kW a)), 
           capacity inflow, capacity outflow, capacity loss, efficiency inflow, 
           efficiency outflow, initial capacity, capacity min, capacity max,
           variable input costs, variable output costs
           
        busd : obj:'dict'
           -- dictionary containing the busses of the energy system

        nodes : obj:'list'
            -- list of components

    ----   
    @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
    """
    # intern variables
    nodes = []
    nodes_storages = []

    def __init__(self, nodes_data, nodes, busd):

        # rename variables
        self.nodes = []
        self.nodes_storages = []
        for i in range(len(nodes)):
            self.nodes.append(nodes[i])

        # creates storage object for every storage element in nd
        for i, s in nodes_data['storages'].iterrows():
            if s['active']:
                # creates storage object and adds it to the list of components
                self.nodes_storages.append(
                    solph.components.GenericStorage(
                        label=s['label'],
                        inputs={busd[s['bus']]: solph.Flow(
                            # nominal_value=s['capacity inflow'],
                            variable_costs=s['variable input costs'])},
                        outputs={busd[s['bus']]: solph.Flow(
                            # nominal_value=s['capacity outflow'],
                            variable_costs=s['variable output costs'])},
                        loss_rate=s['capacity loss'],
                        inflow_conversion_factor=s['efficiency inflow'],
                        outflow_conversion_factor=s['efficiency outflow'],
                        invest_relation_input_capacity=s['input/capacity ratio (invest)'],
                        invest_relation_output_capacity=s['output/capacity ratio (invest)'],
                        investment=solph.Investment(
                            ep_costs=s['periodical costs /(CU/(kWh a))'],
                            existing=s['existing capacity /(kWh)'],
                            minimum=s['min. investment capacity /(kWh)'],
                            maximum=s['max. investment capacity /(kWh)'],
                            nonconvex = True if s['Non-Convex Investment'] == 1 else False,
                            offset = s['Fix Investment Capacity']
                        )))

                # returns logging info
                logging.info('   ' + 'Storage created: ' + s['label'])

        # appends the created storages to the list of nodes
        for i in range(len(self.nodes_storages)):
            nodes.append(self.nodes_storages[i])


class Links:
    """Creates link objects.
    
    Creates links objects as defined in 'nodes_data' and adds them to the 
    list of components 'nodes'.

    ----    
        
    Keyword arguments:
        
        nodes_data : obj:'dict'
           -- dictionary containing data from excel scenario file. The 
           following data have to be provided: label, active, bus_1, bus_2, 
           (un)directed, efficiency, existing capacity /(kW), 
           min. investment capacity /(kW), max. investment capacity /(kW), 
           variable costs /(CU/kWh), periodical costs /(CU/(kW a))
        
        bus : obj:'dict'
           -- dictionary containing the buses of the energy system
        
        nodes : obj:'list'
            -- list of components

    ----
    @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
    """
    # intern variables
    nodes_links = []
    nodes = []
    busd = None

    def undirected_link(self, p):
        """Creates an undirected link object.
        
        Creates an undirected link between two buses and adds it to the list of 
        components 'nodes'.
                
        ----    
        @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
        """

        # creates transformer representing the first link direction and adds it to the
        # list of components
        self.nodes_links.append(
            solph.Transformer(
                label=p['label'],
                inputs={self.busd[p['bus_1']]: solph.Flow(
                    variable_costs=p['variable costs /(CU/kWh)'])},
                outputs={self.busd[p['bus_2']]: solph.Flow(
                    investment=solph.Investment(
                        ep_costs=p['periodical costs /(CU/(kW a))'],
                        minimum=p['min. investment capacity /(kW)'],
                        maximum=p['max. investment capacity /(kW)'],
                        existing=p['existing capacity /(kW)'],
                        nonconvex = True if p['Non-Convex Investment'] == 1 else False,
                        offset = p['Fix Investment Capacity']
                    ))},
                conversion_factors={self.busd[p['bus_2']]: p['efficiency']}))

        # creates transformer representing the second link direction and adds it to the
        # list of components
        label2 = str(p['label'] + '_direction_2')
        self.nodes_links.append(
            solph.Transformer(
                label=label2,
                inputs={self.busd[p['bus_2']]: solph.Flow(
                    variable_costs=p['variable costs /(CU/kWh)'])},
                outputs={self.busd[p['bus_1']]: solph.Flow(
                    investment=solph.Investment(
                        ep_costs=p['periodical costs /(CU/(kW a))'],
                        minimum=p['min. investment capacity /(kW)'],
                        maximum=p['max. investment capacity /(kW)'],
                        existing=p['existing capacity /(kW)'],
                        nonconvex = True if p['Non-Convex Investment'] == 1 else False,
                        offset = p['Fix Investment Capacity']
                    ))},
                conversion_factors={self.busd[p['bus_2']]: p['efficiency']}))

        # returns logging info
        logging.info('   ' + 'Link created: ' + p['label'])

    def directed_link(self, p):
        """Creates a directed link object.
        
        Creates a directed link between two buses and adds it to the list of 
        components 'nodes'.
                
        ----   
        @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
        """

        # creates transformer object representing the link and adds it to
        # the list of components
        self.nodes_links.append(
            solph.Transformer(
                label=p['label'],
                inputs={self.busd[p['bus_1']]: solph.Flow(
                    variable_costs=p['variable costs /(CU/kWh)'])},
                outputs={self.busd[p['bus_2']]: solph.Flow(
                    investment=solph.Investment(
                        ep_costs=p['periodical costs /(CU/(kW a))'],
                        minimum=p['min. investment capacity /(kW)'],
                        maximum=p['max. investment capacity /(kW)'],
                        existing=p['existing capacity /(kW)'],
                        nonconvex = True if p['Non-Convex Investment'] == 1 else False,
                        offset=p['Fix Investment Capacity']
                    ))},
                conversion_factors={self.busd[p['bus_2']]: p['efficiency']}))

        # returns logging info
        logging.info('   ' + 'Link created: ' + p['label'])

    def __init__(self, nodes_data, nodes, bus):

        # renames variables
        self.busd = bus
        self.nodes = []
        self.nodes_links = []
        for i in range(len(nodes)):
            self.nodes.append(nodes[i])

        # creates link objects for every link object in nd
        for i, p in nodes_data['links'].iterrows():
            if p['active']:

                if p['(un)directed'] == 'undirected':
                    self.undirected_link(p)

                elif p['(un)directed'] == 'directed':
                    self.directed_link(p)
        # appends created links to the list of nodes
        for i in range(len(self.nodes_links)):
            nodes.append(self.nodes_links[i])
