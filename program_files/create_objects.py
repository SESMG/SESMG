# -*- coding: utf-8 -*-
"""Creates oemof energy system components.

Functions for the creation of oemof energy system objects from a
given set of object parameters.

---
Contributors:
    - Christian Klemm - christian.klemm@fh-muenster.de
    - Gregor Becker - gb611137@fh-muenster.de
"""

from oemof import solph
import logging
import os
import pandas as pd
from feedinlib import *
import demandlib.bdew as bdew
import datetime


def buses(nodes_data, nodes):
	"""
    Creates bus objects.

    Creates bus objects with the parameters given in 'nodes_data' and
    adds them to the list of components 'nodes'.

    ----

    Keyword arguments:

        nodes_data : obj:'dict'
           -- dictionary containing parameters of the buses to be
           created. The following parameters have to be provided:

                - label,
                - active,
                - excess,
                - shortage,
                - shortage costs /(CU/kWh),
                - excess costs /(CU/kWh)

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

	# Creates components, which are defined within the "buses"-sheet of
	# the original excel-file
	for i, b in nodes_data['buses'].iterrows():
		# Create a bus object for every bus, which is marked as "active"
		if b['active']:
			# creates an oemof-bus object
			bus = solph.Bus(label=b['label'])
			# adds the bus object to the list of components "nodes"
			nodes.append(bus)
			busd[b['label']] = bus
			# returns logging info
			logging.info('   ' + 'Bus created: ' + b['label'])

			# Create an sink for every bus, which is marked with
			# "excess"
			if b['excess']:
				# creates the oemof-sink object and
				# directly adds it to the list of components "nodes"
				nodes.append(
					solph.Sink(label=b['label'] + '_excess',
							   inputs={
								   busd[b['label']]:
									   solph.Flow(
										   variable_costs=
										   b['excess costs /(CU/kWh)'],
									   )}))

			# Create a source for every bus, which is marked with
			# "shortage"
			if b['shortage']:
				# creates the oemof-source object and
				# directly adds it to the list of components "nodes"
				nodes.append(
					solph.Source(label=b['label'] + '_shortage',
								 outputs={
									 busd[b['label']]:
										 solph.Flow(
											 variable_costs=
											 b['shortage costs /(CU/kWh)'])}))

			# Returns the list of buses as result of the function
			return busd


class Sources:
	"""Creates source objects.

    There are four options for labeling source objects to be created:
        - 'commodity' : a source with flexible time series
        - 'timeseries' : a source with predefined time series
        - 'photovoltaic' : a photovoltaic component
        - 'wind power' : a wind power component
    """

	def create_source(self, so, timeseries_args):
		"""Creates an oemof source with fixed or unfixed timeseries

        ----
        Keyword arguments:

            so : obj:'dict'
                -- dictionary containing all information for the
                   creation of an oemof source. At least the following
                   key-value-pairs have to be included:
                       'label'
                       'output'
                       'periodical costs /(CU/(kW a))'
                       'min. investment capacity /(kW)'
                       'max. investment capacity /(kW)'
                       'existing capacity /(kW)'
                       'Non-Convex Investment'
                       'Fix Investment Costs /(CU/a)'
                       'variable costs /(CU/kWh)'

            timeseries_args: dict
                --  dictionary rather containing the 'fix-attribute' or
                    the 'min-' and 'max-attribute' of a source

        ---
        Contributors:
            - Christian Klemm - christian.klemm@fh-muenster.de

        """

		# Creates a oemof source and appends it to the nodes_sources
		# (variable of the create_sources-class) list
		self.nodes_sources.append(
			solph.Source(label=so['label'],
						 outputs={self.busd[so['output']]: solph.Flow(
							 investment=solph.Investment(
								 ep_costs=so['periodical costs /(CU/(kW a))'],
								 minimum=so['min. investment capacity /(kW)'],
								 maximum=so['max. investment capacity /(kW)'],
								 existing=so['existing capacity /(kW)'],
								 nonconvex=True if
								 so['Non-Convex Investment'] == 1 else False,
								 offset=so['Fix Investment Costs /(CU/a)']),
							 **timeseries_args,
							 variable_costs=so['variable costs /(CU/kWh)'])}))

	def commodity_source(self, so):
		""" Creates an oemof source object with flexible time series
            (no maximum or minimum) with the use of the
            create_source method.

            ----
            Keyword arguments:

                so : obj:'dict'
                    -- dictionary containing all information for the
                        creation of an oemof source. At least the
                        following key-value-pairs have to be included:
                            'label'
        """
		# starts the create_source method with the parameters
		# min = 0 and max = 1
		self.create_source(so, {'min': 0, 'max': 1})

		# Returns logging info
		logging.info('   ' + 'Commodity Source created: ' + so['label'])

	def timeseries_source(self, so, filepath):
		"""Creates an oemof source object from a pre-defined
        timeseries with the use of the create_source
        method.

        ---
        Keyword arguments:

            so : obj:'dict'
                --  dictionary containing all information for the
                    creation of an oemof source. At least the following
                    key-value-pairs have to be included:
                       'label'
                       'output'
                       'periodical costs /(CU/(kW a))'
                       'min. investment capacity /(kW)'
                       'max. investment capacity /(kW)'
                       'existing capacity /(kW)'
                       'Non-Convex Investment'
                       'Fix Investment Costs /(CU/a)'
                       'variable costs /(CU/kWh)'

            filepath: String
                --  path to .xlsx scenario-file containing a
                    "time_series" sheet
        """
		# reads the timeseries sheet of the scenario file
		time_series = pd.read_excel(filepath, sheet_name='time_series')

		if so['fixed'] == 1:
			# sets the timeseries attribute for a fixed source
			args = {'fix': time_series[so['label'] + '.fix'].tolist()}
		elif so['fixed'] == 0:
			# sets the timeseries attributes for an unfixed source
			args = {'min': time_series[so['label'] + '.min'].tolist(),
					'max': time_series[so['label'] + '.max'].tolist()}
		else:
			raise SystemError(so['label'] + " Error in fixed attribute")

		# starts the create_source method with the parameters set before
		self.create_source(so, args)

		# Returns logging info
		logging.info('   ' + 'Timeseries Source created: ' + so['label'])

	def pv_source(self, so):
		"""Creates an oemof photovoltaic source object.

        Simulates the yield of a photovoltaic system using feedinlib and
        creates a source object with the yield as time series and the
        use of the create_source method.

        ---

        Keyword arguments:

            so : obj:'dict'
                --  dictionary containing all information for the
                    creation of an oemof source. At least the following
                    key-value-pairs have to be included:
                        - 'label'
                        - 'fixed'
                        - 'Azimuth (PV ONLY)'
                        - 'Surface Tilt (PV ONLY)'
                        - 'Modul Model (PV ONLY)'
                        - 'Inverter Model (PV ONLY)'
                        - 'Albedo (PV ONLY)'
                        - 'Latitude (PV ONLY)'
                        - 'Longitude (PV ONLY)'
        """

		# reads pv system parameters from parameter dictionary
		# nodes_data
		parameter_set = {
			'azimuth': so['Azimuth (PV ONLY)'],
			'tilt': so['Surface Tilt (PV ONLY)'],
			'module_name': so['Modul Model (PV ONLY)'],
			'inverter_name': so['Inverter Model (PV ONLY)'],
			'albedo': so['Albedo (PV ONLY)']}

		# sets pv system parameters for pv_module
		pv_module = powerplants.Photovoltaic(**parameter_set)

		# reads weather data from interim-.csv data set
		my_weather_pandas_DataFrame = \
			pd.read_csv(
				os.path.join(os.path.dirname(__file__))
				+ '/interim_data/weather_data.csv',
				index_col=0,
				date_parser=lambda idx: pd.to_datetime(idx, utc=True))

		# calculates global horizontal irradiance from diffuse (dhi)
		# and direct irradiance and adds it to the weather data frame
		my_weather_pandas_DataFrame['ghi'] = \
			(my_weather_pandas_DataFrame.dirhi
			 + my_weather_pandas_DataFrame.dhi)

		# changes names of data columns,
		# so it fits the needs of the feedinlib
		name_dc = {'temperature': 'temp_air', 'windspeed': 'v_wind'}
		my_weather_pandas_DataFrame.rename(columns=name_dc)

		# calculates time series normed on 1 kW pv peak performance
		feedin = pv_module.feedin(
			weather=my_weather_pandas_DataFrame,
			location=(so['Latitude (PV ONLY)'],
					  so['Longitude (PV ONLY)']),
			scaling='peak_power')

		# Prepare data set for compatibility with oemof
		for i in range(len(feedin)):
			# Set negative values to zero
			# (requirement for solving the model)
			if feedin[i] < 0:
				feedin[i] = 0
			# Set values greater 1 to 1
			# (requirement for solving the model)
			if feedin[i] > 1:
				feedin[i] = 1
		# Replace 'nan' value with 0
		feedin = feedin.fillna(0)

		if so['fixed'] == 1:
			# sets the attribute for a fixed pv_source
			args = {'fix': feedin}
		elif so['fixed'] == 0:
			# sets the attributes for an unfixed pv_source
			args = {'min': 0, 'max': feedin}
		else:
			raise SystemError(so['label'] + " Error in fixed attribute")

		# starts the create_source method with the parameters set before
		self.create_source(so, args)

		# returns logging info
		logging.info('   ' + 'Source created: ' + so['label'])

	def windpower_source(self, so):
		"""Creates an oemof windpower source object.

        Simulates the yield of a windturbine using feedinlib and
        creates a source object with the yield as time series and the
        use of the create_source method.

        ---
        Keyword arguments:

            so : obj:'dict'
                -- dictionary containing all information for the
                   creation of an oemof source. At least the following
                   key-value-pairs have to be included:
                        - 'label'
                        - 'fixed'
                        - 'Turbine Model (Windpower ONLY)'
                        - 'Hub Height (Windpower ONLY)'
        """

		# set up wind turbine using the wind turbine library.
		# The turbine name must correspond to an entry in the turbine
		# data-base of the feedinlib. Unit of the hub height is m.
		turbine_data = {
			'turbine_type': so['Turbine Model (Windpower ONLY)'],
			'hub_height': so['Hub Height (Windpower ONLY)']
		}
		wind_turbine = WindPowerPlant(**turbine_data)

		# set up weather dataframe for windpowerlib
		weather_df_wind = pd.read_csv(
			os.path.join(os.path.dirname(__file__))
			+ '/interim_data/weather_data.csv',
			index_col=0,
			date_parser=lambda idx: pd.to_datetime(idx, utc=True))

		# change type of index to datetime and set time zone
		weather_df_wind.index = \
			pd.to_datetime(weather_df_wind.index).tz_convert('Europe/Berlin')
		data_height = {
			'pressure': 0,
			'temperature': 2,
			'wind_speed': 10,
			'roughness_length': 0}
		weather_df_wind = \
			weather_df_wind[['windspeed', 'temperature', 'z0', 'pressure']]
		weather_df_wind.columns = \
			[['wind_speed', 'temperature', 'roughness_length', 'pressure'],
			 [data_height['wind_speed'], data_height['temperature'],
			  data_height['roughness_length'], data_height['pressure']]]

		# calculate scaled feed-in
		feedin_wind_scaled = wind_turbine.feedin(
			weather=weather_df_wind,
			scaling='nominal_power')

		if so['fixed'] == 1:
			# sets the attribute for a fixed windpower_source
			args = {'fix': feedin_wind_scaled}

		elif so['fixed'] == 0:
			# sets the attribute for an unfixed windpower_source
			args = {'min': 0, 'max': feedin_wind_scaled}
		else:
			raise SystemError(so['label'] + " Error in fixed attribute")

		# starts the create_source method with the parameters set before
		self.create_source(so, args)

		# returns logging info
		logging.info('   ' + 'Source created: ' + so['label'])

	def __init__(self, nodes_data, nodes, busd, filepath):
		"""
        Inits the source class
        ---
        Keyword arguments:
            
            nodes_data: obj:'dict'
                --  dictionary containing parameters of sources to be
                    created.The following data have to be provided:
                        - 'label'
                        - 'active'
                        - 'fixed'
                        - 'output'
                        - 'technology'
                        - 'variable costs / (CU / kWh)'
                        - 'existing capacity / (kW)'
                        - 'min.investment capacity / (kW)'
                        - 'max.investment capacity / (kW)'
                        - 'periodical costs / (CU / (kW a))'
                        - 'Non-Convex Investment'
                        - 'Fix Investment Cost / (CU/a)'
                        - 'Turbine Model (Windpower ONLY)'
                        - 'Hub Height (Windpower ONLY)'
                        - 'technology database(PV ONLY)'
                        - 'inverter database(PV ONLY)'
                        - 'Modul Model(PV ONLY)'
                        - 'Inverter Model(PV ONLY)'
                        - 'Azimuth(PV ONLY)'
                        - 'Surface Tilt(PV ONLY)'
                        - 'Albedo(PV ONLY)'
                        - 'Altitude(PV ONLY)'
                        - 'Latitude(PV ONLY)'
                        - 'Longitude(PV ONLY)'

            busd: obj:'dict'
                --  dictionary containing the buses of the energy system

            nodes: obj:'list'
                --  list of components created before(can be empty)

            filepath: obj:'str'
                 -- path to .xlsx scenario-file containing a
                    "weather data" sheet with timeseries for
                        -   "dhi"(diffuse horizontal irradiation) 
                            W / m ^ 2
                        -   "dirhi"(direct horizontal irradiance) 
                            W / m ^ 2
                        -   "pressure" in Pa
                        -   "temperature" in °C
                        -   "windspeed" in m / s
                        -   "z0"(roughness length) in m

        ---
        Other variables:

            nodes_sources: obj:'list'
                -- class intern list of sources that are already created

        ---
        Contributors:
            - Christian Klemm - christian.klemm@fh-muenster.de
            - Gregor Becker - gregor.becker@fh-muenster.de
        """
		# Delete possible residues of a previous run from the class
		# internal list nodes_sources
		self.nodes_sources = []
		# Initialise a class intern copy of the bus dictionary
		self.busd = busd.copy()

		# Create Source from "Sources" Table
		for i, so in nodes_data['sources'].iterrows():

			# Create a source object for every source,
			# which is marked as "active"
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

		# appends created sources to the list of nodes
		for i in range(len(self.nodes_sources)):
			nodes.append(self.nodes_sources[i])


class Sinks:
	"""Creates sink objects.

        There are four options for labeling source objects to be
        created:
            - 'unfixed' : a source with flexible time series
            - 'timeseries' : a source with predefined time series
            -  SLP : a VDEW standard load profile component
            - 'richardson' : a component with stochatical generated
                timeseries
    """
	# intern variables
	busd = None
	nodes_sinks = []

	def create_sink(self, de, timeseries_args):
		"""Creates an oemof sink with fixed or unfixed timeseries.

            ----
            Keyword arguments:
                de : obj:'dict'
                    --  dictionary containing all information for the
                        creation of an oemof sink. At least the
                        following key-value-pairs have to be included:
                            - 'label'
                            - 'input'

                timeseries_args : obj:'dict'
                    --  dictionary rather containing the 'fix-attribute'
                        or the 'min-' and 'max-attribute' of a sink

            ---
            Contributors:
                - Christian Klemm - christian.klemm@fh-muenster.de
            """
		# creates an omeof Sink and appends it to the class intern list
		# of created sinks
		self.nodes_sinks.append(
			solph.Sink(label=de['label'],
					   inputs={
						   self.busd[de['input']]:
							   solph.Flow(**timeseries_args)}))

	def unfixed_sink(self, de):
		""" Creates a sink object with an unfixed energy input and the
            use of the create_sink method.
            ----
                Keyword arguments:
                    de : obj:'dict'
                        --  dictionary containing all information for
                        the creation of an oemof sink. For this function
                        the following key-value-pairs have to
                        be included:
                            - 'label'
                            - 'nominal value /(kW)'

                ---
                Contributors:
                    - Christian Klemm - christian.klemm@fh-muenster.de
            """

		# set static inflow values
		inflow_args = {'nominal_value': de['nominal value /(kW)']}
		# starts the create_sink method with the parameters set before
		self.create_sink(de, inflow_args)

		# returns logging info
		logging.info('   ' + 'Sink created: ' + de['label'])

	def timeseries_sink(self, de, filepath):
		""" Creates a sink object with a fixed input. The input must be
            given as a time series in the scenario file.
            In this context the method uses the create_sink method.
        ----
            Keyword arguments:
                de : obj:'dict'
                        --  dictionary containing all information for
                        the creation of an oemof sink. At least the
                        following key-value-pairs have to be included:
                            - 'label'
                            - 'nominal value /(kW)'

                filepath: String
                        -- path to .xlsx scenario-file containing a
                        "time_series" sheet
        ----
        @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
        """
		# imports the time_series sheet of the scenario file
		time_series = pd.read_excel(filepath, sheet_name='time_series')
		# sets the nominal value
		args = {'nominal_value': de['nominal value /(kW)']}
		if de['fixed'] == 0:
			# sets the attributes for an unfixed time_series sink
			args.update({'min': time_series[de['label'] + '.min'].tolist()})
			args.update({'max': time_series[de['label'] + '.max'].tolist()})
		elif de['fixed'] == 1:
			# sets the attributes for a fixed time_series sink
			args.update({'fix': time_series[de['label'] + '.fix'].tolist()})
		# starts the create_sink method with the parameters set before
		self.create_sink(de, args)

		# returns logging info
		logging.info('   ' + 'Sink created: ' + de['label'])

	def slp_sink(self, de, filepath):
		""" Creates a sink with a residential or commercial
            SLP time series.

            Creates a sink with inputs according to VDEW standard
            load profiles, using oemofs demandlib.
            Used for the modelling of residential or commercial
            electricity demand.
            In this context the method uses the create_sink method.
        ----
            Keyword arguments:
                de : obj:'dict'
                        --  dictionary containing all information for
                        the creation of an oemof sink. At least the
                        following key-value-pairs have to be included:
                            - 'label'
                            - 'load profile'
                            - 'annual demand /(kWh/a)'
                            - 'building class [HEAT SLP ONLY]'
                            - 'wind class [HEAT SLP ONLY]'


                filepath : String
                        -- -- path to .xlsx scenario-file containing a
                        "timesystem" sheet

        ----
        @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
        """
		heat_slps = ['efh', 'mfh']
		heat_slps_commercial = \
			['gmf', 'gpd', 'ghd', 'gwa', 'ggb', 'gko', 'gbd', 'gba',
			 'gmk', 'gbh', 'gga', 'gha']
		electricity_slps = \
			['h0', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'l0', 'l1',
			 'l2']
		# Import weather Data
		data = pd.read_csv(os.path.join(
			os.path.dirname(__file__)) + '/interim_data/weather_data.csv')
		# Importing timesystem parameters from the scenario
		nd = pd.read_excel(filepath, sheet_name='timesystem')
		ts = next(nd.iterrows())[1]
		temp_resolution = ts['temporal resolution']
		periods = ts["periods"]
		start_date = str(ts['start date'])

		# Converting start date into datetime format
		start_date = \
			datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')

		# Create DataFrame
		demand = pd.DataFrame(
			index=pd.date_range(pd.datetime(start_date.year,
											start_date.month,
											start_date.day,
											start_date.hour),
								periods=periods, freq=temp_resolution))
		# creates time series
		if de['load profile'] in heat_slps_commercial \
				or de['load profile'] in heat_slps:
			# sets the parameters of the heat slps
			args = {'temperature': data['temperature'],
					'shlp_type': de['load profile'],
					'wind_class': de['wind class [HEAT SLP ONLY]'],
					'annual_heat_demand': 1,
					'name': de['load profile']}
			if de['load profile'] in heat_slps:
				# adds the building class which is only necessary for
				# the non commercial slps
				args.update(
					{'building_class': de['building class [HEAT SLP ONLY]']})
			demand[de['load profile']] = bdew.HeatBuilding(
				demand.index, **args).get_bdew_profile()
		elif de['load profile'] in electricity_slps:
			year = datetime.datetime.strptime(str(ts['start date']),
											  '%Y-%m-%d %H:%M:%S').year
			# Imports standard load profiles
			e_slp = bdew.ElecSlp(year)
			demand = e_slp.get_profile({de['load profile']: 1})
			# creates time series based on standard load profiles
			demand = demand.resample(temp_resolution).mean()
		# sets the nominal value
		args = {'nominal_value': de['annual demand /(kWh/a)']}
		if de['fixed'] == 1:
			# sets the parameters for a fixed sink
			args.update({'fix': demand[de['load profile']]})
		elif de['fixed'] == 0:
			# sets the parameters for an unfixed sink
			args.update({'max': demand[de['load profile']]})
		# starts the create_sink method with the parameters set before
		self.create_sink(de, args)
		# returns logging info
		logging.info('   ' + 'Sink created: ' + de['label'])

	def richardson_sink(self, de, filepath):
		"""Creates a sink with stochastical timeseries.

        Creates a sink with stochastical input, using richardson.py.
        Used for the modelling of residential electricity demands.
        In this context the method uses the create_sink method.
        ----
        Keyword arguments:
            de : obj:'dict'
                        --  dictionary containing all information for
                        the creation of an oemof sink. At least the
                        following key-value-pairs have to be included:
                            - 'label'
                            - 'fixed'
                            - 'annual demand /(kWh/a)'
                            - 'occupants [RICHARDSON]'

                filepath : String
                        -- path to .xlsx scenario-file containing a
                        "timesystem" sheet
        ----
        @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
        """

		import richardsonpy.classes.occupancy as occ
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
		nd = pd.read_excel(filepath, sheet_name='timesystem')
		ts = next(nd.iterrows())[1]
		temp_resolution = ts['temporal resolution']

		# sets the occupancy rates
		nb_occ = de['occupants [RICHARDSON]']

		# Workaround, because richardsonpy only allows a maximum
		# of 5 occupants
		if nb_occ > 5:
			nb_occ = 5

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
			raise SystemError('Invalid Temporal Resolution')

		#  Generate occupancy object
		#  (necessary as input for electric load gen)
		occ_obj = occ.Occupancy(number_occupants=nb_occ)

		#  Generate stochastic electric power object
		el_load_obj = eload.ElectricLoad(occ_profile=occ_obj.occupancy,
										 total_nb_occ=nb_occ,
										 q_direct=dirhi,
										 q_diffuse=dhi,
										 timestep=timestep)

		# creates richardsonpy time series
		load_profile = el_load_obj.loadcurve
		richardson_demand = (sum(el_load_obj.loadcurve)
							 * timestep / (3600 * 1000))
		annual_demand = de['annual demand /(kWh/a)']

		# Disables the stochastic simulation of the total yearly demand
		# by scaling the generated time series using the total energy
		# demand of the sink generated in the spreadsheet
		demand_ratio = annual_demand / richardson_demand
		# sets nominal value
		args = {'nominal_value': 0.001 * demand_ratio}
		if de['fixed'] == 1:
			# sets attributes for a fixed richardson sink
			args.update({'fix': load_profile})
		elif de['fixed'] == 0:
			# sets attributes for an unfixed richardson sink
			args.update({'max': load_profile})
		# starts the create_sink method with the parameters set before
		self.create_sink(de, args)
		# returns logging info
		logging.info('   ' + 'Sink created: ' + de['label'])

	def __init__(self, nodes_data, busd, nodes, filepath):
		""" Inits the sink class.
        ----
        Keyword arguments:

            nodes_data: obj:'dict'
                --  dictionary containing parameters of sinks to be
                    created.The following data have to be provided:
                        - 'label'
                        - 'active'
                        - 'fixed'
                        - 'input'
                        - 'load profile'
                        - 'nominal value /(kW)'
                        - 'annual demand /(kWh/a)'
                        - 'occupants [Richardson]'
                        - 'building class [HEAT SLP ONLY]'
                        - 'wind class [HEAT SLP ONLY]'


            busd: obj:'dict'
                --  dictionary containing the buses of the energy system

            nodes: obj:'list'
                --  list of components created before(can be empty)

            filepath: obj:'str'
                 -- path to .xlsx scenario-file containing a
                    "weather data" sheet with timeseries for
                        -   "dhi"(diffuse horizontal irradiation)
                            W / m ^ 2
                        -   "dirhi"(direct horizontal irradiance)
                            W / m ^ 2
                        -   "pressure" in Pa
                        -   "temperature" in °C
                        -   "windspeed" in m / s
                        -   "z0"(roughness length) in m

        ---
        Other variables:

            nodes_sinks: obj:'list'
                -- class intern list of sinks that are already created

        ---
        Contributors:
            - Christian Klemm - christian.klemm@fh-muenster.de
            - Gregor Becker - gregor.becker@fh-muenster.de
        """

		# Delete possible residues of a previous run from the class
		# internal list nodes_sinks
		self.nodes_sinks = []
		# Initialise a class intern copy of the bus dictionary
		self.busd = busd.copy()

		# richardson.py and demandlib can only read .csv data sets,
		# so the weather data from the .xlsx scenario file have to be
		# converted into a .csv data set and saved
		read_file = pd.read_excel(filepath, sheet_name='weather data')
		read_file.to_csv(
			os.path.join(os.path.dirname(__file__))
			+ '/interim_data/weather_data.csv',
			index=None,
			header=True)

		# Create sink objects
		for i, de in nodes_data['demand'].iterrows():
			slps = \
				['efh', 'mfh', 'gmf', 'gpd', 'ghd', 'gwa', 'ggb', 'gko', 'gbd',
				 'gba', 'gmk', 'gbh', 'gga', 'gha', 'h0', 'g0', 'g1', 'g2',
				 'g3', 'g4', 'g5', 'g6', 'l0', 'l1', 'l2']

			if de['active']:

				# Create Sinks un-fixed time-series
				if de['load profile'] == 'x':
					self.unfixed_sink(de)

				# Create Sinks with Time-series
				elif de['load profile'] == 'timeseries':
					self.timeseries_sink(de, filepath)

				# Create Sinks with SLP's
				elif de['load profile'] in slps:
					self.slp_sink(de, filepath)

				# Richardson
				elif de['load profile'] == 'richardson':
					self.richardson_sink(de, filepath)

		# appends created sinks on the list of nodes
		for i in range(len(self.nodes_sinks)):
			nodes.append(self.nodes_sinks[i])


# TODO Is there a potential for optimization?
# TODO Discussion with Janik
class Transformers:
	"""
	Creates a transformer object.
	Creates transformers objects as defined in 'nodes_data' and adds them to
	the list of components 'nodes'.

	----

	Keyword arguments:

		nodes_data : obj:'dict'
		-- dictionary containing data from excel scenario file. The
			following data have to be provided: label, active, transformer type,
			input, output, output2, efficiency, efficiency2,
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
	nodes_sources = []
	busd = None

	# TODO Revision

	def generic_transformer(self, tf):
		"""
		Creates a Generic Transformer object.
		Creates a generic transformer with the parameters given in
		'nodes_data' and adds it to the list of components 'nodes'.
		----
		Keyword arguments:
			tf : obj:'dict'
			-- dictionary containing all information for thecreation of
			an oemof transformer.
			At least the following key-value-pairs have to be included:
				- 'label'
				- 'input'
				- 'output'
				- 'output2'
				- 'efficiency'
				- 'efficiency2'
				- 'variable input costs / (CU/kWh)'
				- 'variable output costs / (CU/kWh)'
				- 'variable output costs 2 / (CU/kWh)'
				- 'periodical costs / (CU/kWh)'
				- 'min. investment capacity / (kW)'
				- 'max. investment capacacity / (kW)'
				- 'existing capacity / (kW)'
				- 'Non-Convex Investment'
				- 'Fix Investment Costs / (CU/a)'

		----
		@ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
		"""
		outputs = {self.busd[tf['output']]:
			solph.Flow(
				variable_costs=tf['variable output costs /(CU/kWh)'],
				investment=solph.Investment(
					ep_costs=tf['periodical costs /(CU/(kW a))'],
					minimum=tf['min. investment capacity /(kW)'],
					maximum=tf['max. investment capacity /(kW)'],
					existing=tf['existing capacity /(kW)'],
					nonconvex=
					True if tf['Non-Convex Investment'] == 1 else False,
					offset=tf['Fix Investment Costs /(CU/a)']
				))}
		conversion_factors = {self.busd[tf['output']]: tf['efficiency']}
		# Defines Capacity values for the second transformer output
		if tf['output2'] not in ['None', 'none', 'x']:
			existing_capacity2 = ((tf['existing capacity /(kW)'] /
								   tf['efficiency']) * tf['efficiency'])
			minimum_capacity2 = ((tf['min. investment capacity /(kW)'] /
								  tf['efficiency']) * tf['efficiency'])
			maximum_capacity2 = ((tf['max. investment capacity /(kW)'] /
								  tf['efficiency']) * tf['efficiency'])

			# Creates transformer object and adds it to the list of
			# components
			outputs.update({self.busd[tf['output2']]:
				solph.Flow(
					variable_costs=tf['variable output costs 2 /(CU/kWh)'],
					investment=solph.Investment(
						ep_costs=0,
						# t['periodical costs /(CU/(kW a))'],
						existing=existing_capacity2,
						minimum=minimum_capacity2,
						maximum=maximum_capacity2,
						nonconvex=
						True if tf['Non-Convex Investment'] == 1 else False,
						offset=tf['Fix Investment Costs /(CU/a)']))})
			conversion_factors.update({self.busd[tf['output2']]:
										   tf['efficiency2']})
		outputs = {"outputs": outputs}
		conversion_factors = {"conversion_factors": conversion_factors}
		self.nodes_transformer.append(
			solph.Transformer(
				label=tf['label'],
				inputs={self.busd[tf['input']]:
					solph.Flow(
						variable_costs=tf['variable input costs /(CU/kWh)'])},
				**outputs,
				**conversion_factors))

	def heat_pump_transformer(self, t):
		"""
			Creates a Heat Pump object by using oemof.thermal.
			Creates a heat pump with the parameters given in
			'nodes_data' and adds it to the list of components 'nodes'.
			----
			@ Janik Budde - Janik.Budde@fh-muenster.de, 30.07.2020
			"""

		# import oemof.thermal in order to calculate the cop
		global cops_hp, heatsource_capacity, heatpump_label
		import \
			oemof.thermal.compression_heatpumps_and_chillers as cmpr_hp_chiller
		import numpy

		# Import weather Data
		data = pd.read_csv(os.path.join(
			os.path.dirname(__file__)) + '/interim_data/weather_data.csv')

		# creates an oemof-bus object, all heat pumps use the same low temp bus
		bus = solph.Bus(label=t['label'] + '_low_temp_bus')

		# adds the bus object to the list of components "nodes"
		self.nodes.append(bus)
		self.busd[t['label'] + '_low_temp_bus'] = bus

		# returns logging info
		logging.info('   ' + 'Bus created: ' + t['label'] + '_low_temp_bus')

		# differentiation between heat sources
		# ground as a heat source referring to vertical-borehole
		# ground-coupled heat pumps
		if t['heat source'] == "Ground":

			# borehole that acts as heat source for the heat pump
			heatpump_label = t['label'] + '_low_temp_ground_source'

			# the capacity of a borehole is limited by the area
			heatsource_capacity = t['area /(sq m)'] * (
					t['length of the geoth. probe (m)'] *
					t['heat extraction (kW/(m*a))'] /
					t['min. borehole area (sq m)'])

		# ground water as a heat source
		elif t['heat source'] == "GroundWater":

			# ground water that acts as heat source for the heat pump
			heatpump_label = t['label'] + '_low_temp_groundwater_source'

			# the capacity of ambient air is not limited
			heatsource_capacity = 999999

		# ambient air as a heat source
		elif t['heat source'] == "Air":

			# ambient air that acts as heat source for the heat pump
			heatpump_label = t['label'] + '_low_temp_air_source'

			# the capacity of ambient air is not limited
			heatsource_capacity = 999999

		# surface water as a heat source
		elif t['heat source'] == "Water":

			# ambient air that acts as heat source for the heat pump
			heatpump_label = t['label'] + '_low_temp_water_source'

			# the capacity of ambient air is not limited
			heatsource_capacity = 999999

		# the heat source costs are considered by the transformer
		self.nodes_sources.append(
			solph.Source(label=heatpump_label,
						 outputs={self.busd[
							 t['label'] + '_low_temp_bus']: solph.Flow(
							 investment=solph.Investment(
								 ep_costs=0,
								 minimum=0,
								 maximum=heatsource_capacity,
								 existing=0),
							 variable_costs=0)}))

		# Returns logging info
		logging.info(
			'   ' + 'Heat Source created: ' + t['label'] + '_low_temp_source')

		# precalculation of COPs, referring to different low temp sources
		if t['heat source'] == "Ground":
			cops_hp = cmpr_hp_chiller.calc_cops(
				temp_high=[t['temperature high /(deg C)']],
				temp_low=data['ground_temp'],
				quality_grade=t['quality grade'],
				temp_threshold_icing=t['temp threshold icing'],
				factor_icing=t['factor icing'],
				mode='heat_pump')
			logging.info('   ' + t[
				'label'] + ", Average Coefficient of Performance (COP): {:2.2f}".format(
				numpy.mean(cops_hp)))

		elif t['heat source'] == "GroundWater":
			cops_hp = cmpr_hp_chiller.calc_cops(
				temp_high=[t['temperature high /(deg C)']],
				temp_low=data['groundwater_temp'],
				quality_grade=t['quality grade'],
				temp_threshold_icing=t['temp threshold icing'],
				factor_icing=t['factor icing'],
				mode='heat_pump')
			logging.info('   ' + t[
				'label'] + ", Average Coefficient of Performance (COP): {:2.2f}".format(
				numpy.mean(cops_hp)))

		elif t['heat source'] == "Air":
			cops_hp = cmpr_hp_chiller.calc_cops(
				temp_high=[t['temperature high /(deg C)']],
				temp_low=data['temperature'],
				quality_grade=t['quality grade'],
				temp_threshold_icing=t['temp threshold icing'],
				factor_icing=t['factor icing'],
				mode='heat_pump')
			logging.info('   ' + t[
				'label'] + ", Average Coefficient of Performance (COP): {:2.2f}".format(
				numpy.mean(cops_hp)))

		elif t['heat source'] == "Water":
			cops_hp = cmpr_hp_chiller.calc_cops(
				temp_high=[t['temperature high /(deg C)']],
				temp_low=data['water_temp'],
				quality_grade=t['quality grade'],
				temp_threshold_icing=t['temp threshold icing'],
				factor_icing=t['factor icing'],
				mode='heat_pump')
			logging.info('   ' + t[
				'label'] + ", Average Coefficient of Performance (COP): {:2.2f}".format(
				numpy.mean(cops_hp)))

		# Creates transformer object and adds it to the list of components
		self.nodes_transformer.append(
			solph.Transformer(
				label=t['label'],
				inputs={self.busd[t['input']]: solph.Flow(
					variable_costs=t['variable input costs /(CU/kWh)']),
					self.busd[t['label'] + '_low_temp_bus']: solph.Flow(
						variable_costs=0)},
				outputs={self.busd[t['output']]: solph.Flow(
					variable_costs=t['variable output costs /(CU/kWh)'],
					investment=solph.Investment(
						ep_costs=t['periodical costs /(CU/(kW a))'],
						minimum=t['min. investment capacity /(kW)'],
						maximum=t['max. investment capacity /(kW)'],
						existing=t['existing capacity /(kW)']
					))},
				conversion_factors={self.busd[t['label'] + '_low_temp_bus']:
										[(cop - 1) / cop for cop in cops_hp],
									self.busd[t['input']]:
										[1 / cop for cop in cops_hp]}))
		# returns logging info
		logging.info('   ' + 'Transformer created: ' + t['label'])

	def genericchp_transformer(self, tf):
		"""
		Creates a Generic CHP transformer object.
		Creates a generic chp transformer with the parameters given in
		'nodes_data' and adds it to the list of components 'nodes'.

		----
		Keyword arguments:
			tf : obj:'dict'
			-- dictionary containing all information for thecreation of
			an oemof transformer.
			At least the following key-value-pairs have to be included:
				- 'label'
				- 'input'
				- 'output'
				- 'output2'
				- 'efficiency'
				- 'efficiency2'
				- 'variable input costs / (CU/kWh)'
				- 'variable output costs / (CU/kWh)'
				- 'variable output costs 2 / (CU/kWh)'
				- 'periodical costs / (CU/kWh)'
				- 'min. investment capacity / (kW)'
				- 'max. investment capacacity / (kW)'
				- 'existing capacity / (kW)'
				- 'Non-Convex Investment'
				- 'Fix Investment Costs / (CU/a)'
		@ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
		"""
		from pandas.tests.arrays.test_datetimelike import datetime_index
		# counts the number of periods within the given datetime index
		# and saves it as variable
		# (number of periods is required for creating generic chp transformers)
		periods = len(datetime_index)

		# creates genericCHP transformer object and adds it to the
		# list of components
		self.nodes_transformer.append(
			solph.components.GenericCHP(
				label=tf['label'],
				fuel_input={
					self.busd[tf['input']]:
						solph.Flow(
							H_L_FG_share_max=
							[tf[
								 'share of flue gas loss at max heat extraction '
								 '[GenericCHP]']
							 for p in range(0, periods)])},
				electrical_output={self.busd[tf['output']]: solph.Flow(
					P_max_woDH=
					[tf['max. electric power without district heating '
						'[GenericCHP]']
					 for p in range(0, periods)],
					P_min_woDH=
					[tf['min. electric power without district heating '
						'[GenericCHP]']
					 for p in range(0, periods)],
					Eta_el_max_woDH=
					[tf['el. eff. at max. fuel flow w/o distr. heating '
						'[GenericCHP]']
					 for p in range(0, periods)],
					Eta_el_min_woDH=
					[tf['el. eff. at min. fuel flow w/o distr. heating '
						'[GenericCHP]']
					 for p in range(0, periods)])},
				heat_output={self.busd[tf['output2']]: solph.Flow(
					Q_CW_min=
					[tf['minimal therm. condenser load to cooling water '
						'[GenericCHP]']
					 for p in range(0, periods)])},
				Beta=[tf['power loss index [GenericCHP]']
					  for p in range(0, periods)],
				back_pressure=False))

		# returns logging info
		logging.info('   ' + 'Transformer created: ' + tf['label'])

	def __init__(self, nodes_data, nodes, busd):

		# renames variables
		self.busd = busd
		self.nodes = []
		self.nodes_transformer = []
		# for i in range(len(nodes)):
		#     self.nodes.append(nodes[i])

		# creates a transformer object for every transformer item within nd
		for i, t in nodes_data['transformers'].iterrows():
			if t['active']:

				# Create Generic Transformers
				if t['transformer type'] == 'GenericTransformer':
					self.generic_transformer(t)

				# Create Heat Pump
				elif t['transformer type'] == 'HeatPump':
					self.heat_pump_transformer(t)

				# Create Extraction Turbine CHPs
				elif t['transformer type'] == 'ExtractionTurbineCHP':
					logging.info('   ' + 'WARNING: ExtractionTurbineCHP are'
								 + ' currently not a part of this model generator,'
								 + ' but will be added later.')

				# Create Generic CHPs
				elif t['transformer type'] == 'GenericCHP':
					self.genericchp_transformer(t)
					logging.info(
						'   ' + 'WARNING: GenericCHP currently does not support'
						+ ' investments and variable costs! Will be added'
						+ ' with upcoming updates')

				# Create Offset Transformers
				elif t['transformer type'] == 'OffsetTransformer':
					logging.info(
						'   ' + 'WARNING: OffsetTransformer are currently'
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

		for i in range(len(self.nodes_sources)):
			nodes.append(self.nodes_sources[i])

		for i in range(len(self.nodes)):
			nodes.append(self.nodes[i])


class Storages:
	"""
	Creates oemof storage objects as defined in 'nodes_data' and adds them to
	the list of components 'nodes'.
	"""

	def __init__(self, nodes_data, nodes, busd):
		"""
		Inits the storage class.
		----

		Keyword arguments:

			nodes_data : obj:'dict'
				--  dictionary containing parameters of storages to be
					created.The following data have to be provided:
						- 'label'
						- 'active'
						- 'bus'
						- 'existing capacity / (kWh)'
						- 'min.investment capacity / (kWh)'
						- 'max.investment capacity / (kWh)'
						- 'Non-Convex Investments'
						- 'Fix Investment Costs /(CU/a)'
						- 'input/capacity ratio (invest)'
						- 'output/capacity ratio (invest)'
						- 'capacity loss'
						- 'efficiency inflow'
						- 'efficiency outflow'
						- 'initial capacity'
						- 'capacity min'
						- 'capacity max'
						- 'variable input costs'
						- 'variable output costs'

			busd : obj:'dict'
				-- dictionary containing the busses of the energy system

			nodes : obj:'list'
				-- list of components created before (can be empty)

		----
		@ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
		"""

		# creates storage object for every storage element in nodes_data
		for i, s in nodes_data['storages'].iterrows():
			if s['active']:
				# creates storage object and adds it to the
				# list of components
				nodes.append(
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
						invest_relation_input_capacity=s[
							'input/capacity ratio (invest)'],
						invest_relation_output_capacity=s[
							'output/capacity ratio (invest)'],
						investment=solph.Investment(
							ep_costs=s['periodical costs /(CU/(kWh a))'],
							existing=s['existing capacity /(kWh)'],
							minimum=s['min. investment capacity /(kWh)'],
							maximum=s['max. investment capacity /(kWh)'],
							nonconvex=
							True if s['Non-Convex Investment'] == 1 else False,
							offset=s['Fix Investment Costs /(CU/a)']
						)))

				# returns logging info
				logging.info('   ' + 'Storage created: ' + s['label'])


class Links:
	"""
	Creates links objects as defined in 'nodes_data' and adds them to
	the list of components 'nodes'.
	----
	@ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
	"""
	# intern variables
	busd = None

	def create_link(self, link, label, outnum):
		"""
		Creates an oemof link object with the given parameters and
		returns it.
		----

		Keyword arguments:

			link: obj:'dict'
			-- dictionary containing parameters of link to be
			created.The following data have to be provided:
				- 'bus_1'
				- 'bus_2'
				- 'efficiency'
				- 'variable costs /(CU/kWh)'
				- 'existing capacity /(kW)'
				- 'min. investment capacity /(kW)'
				- 'max. investment capacity /(kW)'
				- 'periodical costs /(CU/(kW a))'
				- 'Non-Convex Investment'
				- 'Fix Investment Costs /(CU/a)'

			label: String
			-- separate transmission of the label, because there are two
			labels for an undirected link

			outnum: int
			-- Defines in which direction the link is directed.
		"""
		if outnum == 1:
			busin = 'bus_1'
			busout = 'bus_2'
		else:
			busin = 'bus_2'
			busout = 'bus_1'
		inputs = {self.busd[link[busin]]: solph.Flow(
			variable_costs=link['variable costs /(CU/kWh)'])}
		output = {self.busd[link[busout]]: solph.Flow(
			investment=solph.Investment(
				ep_costs=link['periodical costs /(CU/(kW a))'],
				minimum=link['min. investment capacity /(kW)'],
				maximum=link['max. investment capacity /(kW)'],
				existing=link['existing capacity /(kW)'],
				nonconvex=
				True if link['Non-Convex Investment'] == 1 else False,
				offset=link['Fix Investment Costs /(CU/a)']))}
		# returns logging info
		logging.info('   ' + 'Link created: ' + link['label'])
		return (
			solph.Transformer(
				label=label,
				inputs=inputs,
				outputs=output,
				conversion_factors={
					# TODO Discuss if it is wrong implemented
					self.busd[link['bus_2']]: link['efficiency']}))

	def __init__(self, nodes_data, nodes, bus):
		"""
		Inits the Links class.
		----

		Keyword arguments:
			nodes_data: obj:'dict'
			-- dictionary containing data from excel scenario file. The
			following data have to be provided:
				- 'active'
				- 'label'
				- '(un)directed'

			bus : obj:'dict'
			-- dictionary containing the buses of the energy system

			nodes : obj:'list'
			-- list of components created before (can be empty)
			"""
		# renames variables
		self.busd = bus

		# creates link objects for every link object in nd
		for i, link in nodes_data['links'].iterrows():
			if link['active']:
				# creates transformer representing the first link direction
				# and adds it to the list of components
				nodes.append(self.create_link(link, link['label'], 1))
				if link['(un)directed'] == 'undirected':
					# creates transformer representing the second link
					# direction and adds it to the list of components
					label2 = str(link['label'] + '_direction_2')
					nodes.append(self.create_link(link, label2, 2))
