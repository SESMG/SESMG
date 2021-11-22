# -*- coding: utf-8 -*-
"""
    Creates oemof energy system components.

    Functions for the creation of oemof energy system objects from a
    given set of object parameters.

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
import numpy


def buses(nodes_data: dict, nodes: list) -> dict:
    """
        Creates bus objects.
        Creates bus objects with the parameters given in 'nodes_data' and
        adds them to the list of components 'nodes'.

        :param nodes_data: dictionary containing parameters of the buses
                           to be created.
                           The following parameters have to be provided:

                                - label,
                                - active,
                                - excess,
                                - shortage,
                                - shortage costs,
                                - excess costs
        :type nodes_data: dict
        :param nodes: list of components created before (can be empty)
        :type nodes: list

        :return busd: dictionary containing all buses created
        :rtype: dict

        Christian Klemm - christian.klemm@fh-muenster.de
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
                inputs = {
                    busd[b['label']]:
                        solph.Flow(variable_costs=b['excess costs'],
                                   emission_factor=b[
                                       'excess constraint costs'])}
                nodes.append(
                    solph.Sink(
                        label=b['label'] + '_excess',
                        inputs=inputs))

            # Create a source for every bus, which is marked with
            # "shortage"
            if b['shortage']:
                # creates the oemof-source object and
                # directly adds it to the list of components "nodes"
                outputs = {
                    busd[b['label']]:
                        solph.Flow(
                            variable_costs=b['shortage costs'],
                            emission_factor=b[
                                'shortage constraint costs'])}
                nodes.append(
                    solph.Source(
                        label=b['label'] + '_shortage',
                        outputs=outputs))
    # Returns the list of buses as result of the function
    return busd


class Sources:
    """
        Creates source objects.


    #def create_source(self, so, timeseries_args, output):
        Creates an oemof source with fixed or unfixed timeseries

        There are four options for labeling source objects to be created:

            - 'commodity': a source with flexible time series
            - 'timeseries': a source with predefined time series
            - 'photovoltaic': a photovoltaic component
            - 'wind power': a wind power component

        :param nodes_data: dictionary containing parameters of sources
                           to be created.The following data have to be
                           provided:

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
                                - 'non-convex investment'
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
        :type nodes_data: dict
        :param busd: dictionary containing the buses of the energy system
        :type busd: dict
        :param nodes: list of components created before(can be empty)
        :type nodes: list
        :param filepath: path to .xlsx scenario-file containing a
                         "weather data" sheet with timeseries for

                            - "dhi"(diffuse horizontal irradiation)
                              W / m ^ 2
                            - "dirhi"(direct horizontal irradiance)
                              W / m ^ 2
                            - "pressure" in Pa
                            - "temperature" in °C
                            - "windspeed" in m / s
                            - "z0"(roughness length) in m
        :type filepath: str

        Contributors:

            - Christian Klemm - christian.klemm@fh-muenster.de
            - Gregor Becker - gregor.becker@fh-muenster.de
    """

    def create_source(self, so: dict, timeseries_args: dict, output=None):
        """
            Creates an oemof source with fixed or unfixed timeseries

            :param so: dictionary containing all information for the
                       creation of an oemof source. At least the
                       following key-value-pairs have to be included:

                           - 'label'
                           - 'output'
                           - 'periodical costs'
                           - 'min. investment capacity'
                           - 'max. investment capacity'
                           - 'existing capacity'
                           - 'non-convex investment'
                           - 'fix investment costs'
                           - 'variable costs'
            :type so: dict
            :param timeseries_args: dictionary rather containing the
                                    'fix-attribute' or the 'min-' and
                                    'max-attribute' of a source
            :type timeseries_args: dict

            Christian Klemm - christian.klemm@fh-muenster.de
        """
        import math
        # output default
        if output is None:
            output = self.busd[so['output']]
        # set variables minimum, maximum and existing
        if str(so['input']) in ['0', 'None', 'none', 'nan']:
            minimum = so['min. investment capacity']
            maximum = (so['max. investment capacity']
                       if so['max. investment capacity'] != "inf"
                       else float("+inf"))
            existing = so['existing capacity']
            ep_costs = so['periodical costs']
            ep_constr_costs = so['periodical constraint costs']
        # set variables minimum, maximum and existing for solar thermal heat
        # sources
        else:
            minimum = so['min. investment capacity']
            maximum = so['max. investment capacity']
            existing = so['existing capacity']
            ep_costs = so['periodical costs']
            ep_constr_costs = so['periodical constraint costs']
            # minimum = so['min. investment capacity']
            # maximum = so['max. investment capacity']
            # existing = so['existing capacity']
        # Creates a oemof source and appends it to the nodes_sources
        # (variable of the create_sources-class) list
        self.nodes_sources.append(
            solph.Source(
                label=so['label'],
                outputs={output: solph.Flow(
                    investment=solph.Investment(
                        ep_costs=ep_costs,
                        periodical_constraint_costs=ep_constr_costs,
                        minimum=minimum,
                        maximum=maximum,
                        existing=existing,
                        nonconvex=True if
                        so['non-convex investment'] == 1
                        else False,
                        offset=so[
                            'fix investment costs']),
                    **timeseries_args,
                    variable_costs=so['variable costs'],
                    emission_factor=so[
                        'variable constraint costs']
                )}
            ))

    def commodity_source(self, so: dict):
        """
            Creates an oemof source object with flexible time series
            (no maximum or minimum) with the use of the create_source
            method.

            :param so: dictionary containing all information for the
                       creation of an oemof source. At least the
                       following key-value-pairs have to be included:

                            - 'label'
            :type so: object

            Christian Klemm - christian.klemm@fh-muenster.de

        """
        # starts the create_source method with the parameters
        # min = 0 and max = 1
        self.create_source(so, {'min': 0, 'max': 1}, self.busd[so['output']])

        # Returns logging info
        logging.info('   ' + 'Commodity Source created: ' + so['label'])

    def timeseries_source(self, so: dict, time_series):
        """
            Creates an oemof source object from a pre-defined
            timeseries with the use of the create_source method.

            :param so: dictionary containing all information for the
                       creation of an oemof source. At least the
                       following key-value-pairs have to be included:

                            - 'label'
                            - 'output'
                            - 'periodical costs'
                            - 'min. investment capacity'
                            - 'max. investment capacity'
                            - 'existing capacity'
                            - 'non-convex investment'
                            - 'fix investment costs'
                            - 'variable costs'
            :type so: dict
            :param filepath: path to .xlsx scenario-file containing a
                             "time_series" sheet
            :type filepath: str

            Christian Klemm - christian.klemm@fh-muenster.de
        """

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
        self.create_source(so, args, self.busd[so['output']])

        # Returns logging info
        logging.info('   ' + 'Timeseries Source created: ' + so['label'])

    def pv_source(self, so: dict, my_weather_pandas_dataframe):
        """
            Creates an oemof photovoltaic source object.

            Simulates the yield of a photovoltaic system using feedinlib
            and creates a source object with the yield as time series
            and the use of the create_source method.

            :param so: dictionary containing all information for the
                       creation of an oemof source. At least the
                       following key-value-pairs have to be included:

                            - 'label'
                            - 'fixed'
                            - 'Azimuth (PV ONLY)'
                            - 'Surface Tilt (PV ONLY)'
                            - 'Modul Model (PV ONLY)'
                            - 'Inverter Model (PV ONLY)'
                            - 'Albedo (PV ONLY)'
                            - 'Latitude (PV ONLY)'
                            - 'Longitude (PV ONLY)'
            :type so: dict
            :param my_weather_pandas_dataframe: Dataframe containing:

                            - 'dirhi'
                            - 'dhi'
                            - 'temperature'
                            - 'windspeed'
            :type my_weather_pandas_dataframe: pandas.core.frame.Dataframe

            Christian Klemm - christian.klemm@fh-muenster.de
        """
        # reads pv system parameters from parameter dictionary
        # nodes_data
        parameter_set = {
            'azimuth': so['Azimuth'],
            'tilt': so['Surface Tilt'],
            'module_name': so['Modul Model'],
            'inverter_name': so['Inverter Model'],
            'albedo': so['Albedo']}

        # sets pv system parameters for pv_module
        pv_module = powerplants.Photovoltaic(**parameter_set)

        # calculates global horizontal irradiance from diffuse (dhi)
        # and direct irradiance and adds it to the weather data frame
        my_weather_pandas_dataframe['ghi'] = \
            (my_weather_pandas_dataframe.dirhi
             + my_weather_pandas_dataframe.dhi)

        # changes names of data columns,
        # so it fits the needs of the feedinlib
        name_dc = {'temperature': 'temp_air', 'windspeed': 'v_wind'}
        my_weather_pandas_dataframe.rename(columns=name_dc)

        # calculates time series normed on 1 kW pv peak performance
        feedin = pv_module.feedin(
            weather=my_weather_pandas_dataframe,
            location=(so['Latitude'], so['Longitude']),
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
        self.create_source(so, args, self.busd[so['output']])

        # returns logging info
        logging.info('   ' + 'Source created: ' + so['label'])

    def windpower_source(self, so: dict, weather_df_wind):
        """
            Creates an oemof windpower source object.

            Simulates the yield of a windturbine using feedinlib and
            creates a source object with the yield as time series and the
            use of the create_source method.

            :param so: dictionary containing all information for the
                       creation of an oemof source. At least the
                       following key-value-pairs have to be included:

                            - 'label'
                            - 'fixed'
                            - 'Turbine Model (Windpower ONLY)'
                            - 'Hub Height (Windpower ONLY)'
            :type so: dict
            :param weather_df_wind: Dataframe containing:

                            - 'windspeed'
                            - 'temperature'
                            - 'z0'
                            - 'pressure'
            :type weather_df_wind: pandas.core.frame.Dataframe

            Christian Klemm - christian.klemm@fh-muenster.de
        """

        # set up wind turbine using the wind turbine library.
        # The turbine name must correspond to an entry in the turbine
        # data-base of the feedinlib. Unit of the hub height is m.
        turbine_data = {
            'turbine_type': so['Turbine Model'],
            'hub_height': so['Hub Height']}
        wind_turbine = WindPowerPlant(**turbine_data)

        data_height = {'pressure': 0, 'temperature': 2, 'wind_speed': 10,
                       'roughness_length': 0}
        weather_df_wind = \
            weather_df_wind[['windspeed', 'temperature', 'z0', 'pressure']]
        weather_df_wind.columns = \
            [['wind_speed', 'temperature', 'roughness_length', 'pressure'],
             [data_height['wind_speed'], data_height['temperature'],
              data_height['roughness_length'], data_height['pressure']]]

        # calculate scaled feed-in
        feedin_wind_scaled = wind_turbine.feedin(
            weather=weather_df_wind, scaling='nominal_power')
        if so['fixed'] == 1:
            # sets the attribute for a fixed windpower_source
            args = {'fix': feedin_wind_scaled}

        elif so['fixed'] == 0:
            # sets the attribute for an unfixed windpower_source
            args = {'min': 0, 'max': feedin_wind_scaled}
        else:
            raise SystemError(so['label'] + " Error in fixed attribute")

        # starts the create_source method with the parameters set before
        self.create_source(so, args, self.busd[so['output']])

        # returns logging info
        logging.info('   ' + 'Source created: ' + so['label'])

    def solar_heat_source(self, so, data):
        """
            Creates a solar thermal collector source object.

            Calculates the yield of a solar thermal flat plate collector
            or a concentrated solar power collector as time series by
            using oemof.thermal and the create_source method.

            The following key-value-pairs have to be included in the
            keyword arguments:

            :type so: dict
            :param so: has to contain the following keyword arguments

                - 'input'
                - 'technology':
                    - 'solar_thermal_flat_plate' or
                    - 'concentrated_solar_power'
                - 'Latitude'
                - 'Longitude'
                - 'Surface Tilt'
                - 'Azimuth'
                - 'Cleanliness'
                - 'ETA 0'
                - 'A1'
                - 'A2'
                - 'C1'
                - 'C2'
                - 'Temperature Inlet'
                - 'Temperature Difference'
                - 'Conversion Factor'
                - 'Peripheral Losses'
                - 'Electric Consumption'
            @ Yannick Wittor - yw090223@fh-muenster.de, 27.11.2020
        """

        # import oemof.thermal in order to calculate collector heat output
        from oemof.thermal.solar_thermal_collector import flat_plate_precalc
        from oemof.thermal.concentrating_solar_power import csp_precalc
        import numpy

        # creates an oemof-bus object for solar thermal collector
        col_bus = solph.Bus(label=so['label'] + '_bus')
        # adds the bus object to the list of components "nodes"
        self.nodes_sources.append(col_bus)
        self.busd[so['label'] + '_bus'] = col_bus
        output = col_bus

        # import weather data and set datetime index with hourly frequency
        data.index.name = 'Datum'
        # TODO get frequency from energysystem sheet
        data = data.asfreq('h')

        # calculates global horizontal irradiance from diffuse (dhi)
        # and direct irradiance (dirhi) and adds it to the weather data frame
        data['ghi'] = (data["dirhi"] + data["dhi"])

        # precalculations for flat plate collectors, calculates total
        # irradiance on collector, efficiency and heat output
        if so['technology'] == 'solar_thermal_flat_plate':
            precalc_results = flat_plate_precalc(
                lat=so['Latitude'],
                long=so['Longitude'],
                collector_tilt=so['Surface Tilt'],
                collector_azimuth=so['Azimuth'],
                eta_0=so['ETA 0'],
                a_1=so['A1'],
                a_2=so['A2'],
                temp_collector_inlet=
                so['Temperature Inlet'],
                delta_temp_n=
                so['Temperature Difference'],
                irradiance_global=(data['ghi']),
                irradiance_diffuse=(data['dhi']),
                temp_amb=data['temperature'])
            # set variables collectors_heat and irradiance and conversion
            # from W/sqm to kW/sqm
            collectors_heat = precalc_results.collectors_heat / 1000
            irradiance = precalc_results.col_ira / 1000
            collectors_heat = collectors_heat * so['Conversion Factor']

        # set parameters for precalculations for concentrating solar power
        elif so['technology'] == 'concentrated_solar_power':
            # precalculation with parameter set, ambient temperature and
            # direct horizontal irradiance. Calculates total irradiance on
            # collector, efficiency and heat output
            precalc_results = csp_precalc(
                lat=so['Latitude'],
                long=so['Longitude'],
                collector_tilt=so['Surface Tilt'],
                collector_azimuth=so['Azimuth'],
                cleanliness=so['Cleanliness'],
                a_1=so['A1'],
                a_2=so['A2'],
                eta_0=so['ETA 0'],
                c_1=so['C1'],
                c_2=so['C2'],
                temp_collector_inlet=so['Temperature Inlet'],
                temp_collector_outlet=so['Temperature Inlet']
                                      + so['Temperature Difference'],
                temp_amb=data['temperature'],
                E_dir_hor=data['dirhi'])

            # set variables collectors_heat and irradiance and conversion
            # from W/sqm to kW/sqm
            collectors_heat = precalc_results.collector_heat / 1000
            irradiance = precalc_results.collector_irradiance / 1000
            collectors_heat = collectors_heat * so['Conversion Factor']

        # set collector heat as timeseries as argument for source
        if so['fixed'] == 1:
            # sets the attribute for a fixed solar heat source
            args = {'fix': collectors_heat}
        elif so['fixed'] == 0:
            # sets the attributes for an unfixed solar heat source
            args = {'min': 0, 'max': collectors_heat}
        else:
            raise SystemError(so['label'] + " Error in fixed attribute")

        # starts the create_source method with the parameters set before
        self.create_source(so, args, output)

        self.nodes_sources.append(solph.Transformer(
            label=so['label'] + '_collector',
            inputs={self.busd[so['label'] + '_bus']:
                        solph.Flow(variable_costs=0),
                    self.busd[so['input']]: solph.Flow(variable_costs=0)},
            outputs={self.busd[so['output']]: solph.Flow(variable_costs=0)},
            conversion_factors={
                self.busd[so['label'] + '_bus']: 1,
                self.busd[so['input']]:
                    so['Electric Consumption'] *
                    (1 - so['Peripheral Losses']),
                self.busd[so['output']]:
                    1 - so['Peripheral Losses']
            }))

        # returns logging info
        logging.info('   ' + 'Source created: ' + so['label']
                     + ", Max Heat power output per year and m²: {:2.2f}".
                     format(numpy.sum(collectors_heat
                                      / so['Conversion Factor']))
                     + ' kWh/(m²a)'
                     + ", Irradiance on collector per year and m²: "
                       "{:2.2f}".format(numpy.sum(irradiance)) + ' kWh/(m²a)')

    def __init__(self, nodes_data: dict, nodes: list, busd: dict,
                 time_series, weather_data):
        """
            Inits the source class
            ---
            Other variables:

            nodes_sources: obj:'list'
            -- class intern list of sources that are already created
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
                    self.pv_source(so, weather_data)

                # Create Windpower Sources
                elif so['technology'] == 'windpower':
                    self.windpower_source(so, weather_data)

                # Create Time-series Sources
                elif so['technology'] == 'timeseries':
                    self.timeseries_source(so, time_series)

                # Create flat plate solar thermal Sources
                elif so['technology'] in ['solar_thermal_flat_plate',
                                          'concentrated_solar_power']:
                    self.solar_heat_source(so, weather_data)

        # appends created sources and other objects to the list of nodes
        for i in range(len(self.nodes_sources)):
            nodes.append(self.nodes_sources[i])


class Sinks:
    """
        Creates sink objects.

        There are four options for labeling source objects to be
        created:

            - unfixed: a source with flexible time series
            - timeseries: a source with predefined time series
            - SLP: a VDEW standard load profile component
            - richardson: a component with stochastically generated timeseries

        :param nodes_data: dictionary containing parameters of sinks to
                           be created.The following data have to be
                           provided:

                                - 'label'
                                - 'active'
                                - 'fixed'
                                - 'input'
                                - 'load profile'
                                - 'nominal value'
                                - 'annual demand'
                                - 'occupants [Richardson]'
                                - 'building class'
                                - 'wind class'
        :type nodes_data: dict
        :param busd: dictionary containing the buses of the energy system
        :type busd: dict
        :param nodes: list of components created before(can be empty)
        :type nodes: list
        :param filepath: path to .xlsx scenario-file containing a
                         "weather data" sheet with timeseries for

                            - "dhi"(diffuse horizontal irradiation)
                              W / m ^ 2
                            - "dirhi"(direct horizontal irradiance)
                              W / m ^ 2
                            - "pressure" in Pa
                            - "temperature" in °C
                            - "windspeed" in m / s
                            - "z0"(roughness length) in m
        :type filepath: str

        Contributors:

            - Christian Klemm - christian.klemm@fh-muenster.de
            - Gregor Becker - gregor.becker@fh-muenster.de
    """
    # intern variables
    busd = None
    nodes_sinks = []
    energetic_renovation = None
    weatherdata = None

    def create_sink(self, de: dict, timeseries_args: dict):
        """
            Creates an oemof sink with fixed or unfixed timeseries.

            :param de: dictionary containing all information for the
                       creation of an oemof sink. At least the
                       following key-value-pairs have to be included:

                            - 'label'
                            - 'input'

            :type de: dict
            :param timeseries_args: dictionary rather containing the
                                    'fix-attribute' or the 'min-' and
                                    'max-attribute' of a sink
            :type timeseries_args: dict

            Christian Klemm - christian.klemm@fh-muenster.de
        """
        # creates an omeof Sink and appends it to the class intern list
        # of created sinks
        self.nodes_sinks.append(
            solph.Sink(label=de['label'],
                       inputs={
                           self.busd[de['input']]:
                               solph.Flow(**timeseries_args)},
                       ))
        for num, insul_type in self.energetic_renovation.iterrows():
            if insul_type["active"]:
                temp = []
                time = 0
                if insul_type["sink"] == de["label"]:
                    for timestep in self.weatherdata["temperature"]:
                        if timestep <= insul_type["heat limit temperature"]:
                            temp.append(
                                ((insul_type["temperature indoor"] - timestep)
                                 * (insul_type["U-value old"]
                                    - insul_type["U-value new"])
                                 * insul_type["area"]) / 1000)
                        else:
                            temp.append(0)
                    if max(temp) != 0:
                        ep_costs = insul_type["periodical costs"] \
                                   * insul_type["area"] \
                                   / max(temp)
                        ep_constr_costs = \
                            insul_type["periodical_constraint_costs"] \
                            * insul_type["area"] \
                            / max(temp)
                        self.energetic_renovation.loc[
                            num, "ep_costs_kW"] = ep_costs
                        self.energetic_renovation.loc[
                            num, "ep_constr_costs_kW"] = ep_constr_costs
                        self.nodes_sinks.append(
                            solph.Source(
                                    label="insulation-{}".format(
                                            insul_type["label"]),
                                    outputs={
                                        self.busd[de['input']]:
                                            solph.Flow(
                                                investment=solph.Investment(
                                                    ep_costs=ep_costs,
                                                    minimum=0,
                                                    maximum=max(temp)),
                                                fix=(timeseries_args["fix"]
                                                     / timeseries_args["fix"].max()))}))

        # self.nodes_sinks.append(
        #    solph.custom.SinkDSM(label=de['label'],
        #                         inputs={
        #                             self.busd[de['input']]:
        #                                 solph.Flow()
        #                         },
        #                         demand=timeseries_args["nominal_value"]
        #                                * timeseries_args["fix"],
        #                         approach="DLR",
        #                         capacity_down=1,
        #                        capacity_up=1,
        #                        delay_time=3,
        #                        flex_share_up=0.3,
        #                         flex_share_down=0.3,
        #                         shift_time=2,
        #                         shed_eligibility=False,
        #                         investment=solph.Investment(ep_costs=3)))

    def unfixed_sink(self, de: dict):
        """
            Creates a sink object with an unfixed energy input and the
            use of the create_sink method.

            :param de: dictionary containing all information for the
                       creation of an oemof sink. For this function the
                       following key-value-pairs have to be included:

                            - 'label'
                            - 'nominal value'
            :type de: dict

            Christian Klemm - christian.klemm@fh-muenster.de
        """

        # set static inflow values
        inflow_args = {'nominal_value': de['nominal value']}
        # starts the create_sink method with the parameters set before
        self.create_sink(de, inflow_args)
        # returns logging info
        logging.info('   ' + 'Sink created: ' + de['label'])

    def timeseries_sink(self, de, nodes_data):
        """
            Creates a sink object with a fixed input. The input must be
            given as a time series in the scenario file.
            In this context the method uses the create_sink method.

            :param de: dictionary containing all information for the
                       creation of an oemof sink. At least the
                       following key-value-pairs have to be included:

                            - 'label'
                            - 'nominal value'
            :type de: dict
            :param filepath: path to .xlsx scenario-file containing a
                             "time_series" sheet
            :type filepath: str

            Christian Klemm - christian.klemm@fh-muenster.de
        """
        # imports the time_series sheet of the scenario file

        # sets the nominal value
        args = {'nominal_value': de['nominal value']}
        if de['fixed'] == 0:
            # sets the attributes for an unfixed time_series sink
            args.update({'min': nodes_data[de['label'] + '.min'].tolist(),
                         'max': nodes_data[de['label'] + '.max'].tolist()})
        elif de['fixed'] == 1:
            # sets the attributes for a fixed time_series sink
            args.update({'fix': nodes_data[de['label'] + '.fix'].tolist()})
        # starts the create_sink method with the parameters set before
        self.create_sink(de, args)

        # returns logging info
        logging.info('   ' + 'Sink created: ' + de['label'])

    def slp_sink(self, de: dict, nodes_data: dict, weather_data):
        """
            Creates a sink with a residential or commercial
            SLP time series.

            Creates a sink with inputs according to VDEW standard
            load profiles, using oemofs demandlib.
            Used for the modelling of residential or commercial
            electricity demand.
            In this context the method uses the create_sink method.

            :param de: dictionary containing all information for the
                       creation of an oemof sink. At least the
                       following key-value-pairs have to be included:

                            - 'label'
                            - 'load profile'
                            - 'annual demand'
                            - 'building class'
                            - 'wind class'
            :type de: dict
            :param filepath: path to .xlsx scenario-file containing a
                             "energysystem" sheet
            :type filepath: str

            Christian Klemm - christian.klemm@fh-muenster.de
        """
        heat_slps = ['efh', 'mfh']
        heat_slps_commercial = \
            ['gmf', 'gpd', 'ghd', 'gwa', 'ggb', 'gko', 'gbd', 'gba',
             'gmk', 'gbh', 'gga', 'gha']
        electricity_slps = \
            ['h0', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'l0', 'l1', 'l2']
        # Import weather Data
        # Importing timesystem parameters from the scenario
        ts = next(nodes_data['energysystem'].iterrows())[1]
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
            args = {'temperature': weather_data['temperature'],
                    'shlp_type': de['load profile'],
                    'wind_class': de['wind class'],
                    'annual_heat_demand': 1,
                    'name': de['load profile']}
            if de['load profile'] in heat_slps:
                # adds the building class which is only necessary for
                # the non commercial slps
                args.update(
                    {'building_class': de['building class']})
            demand[de['load profile']] = bdew.HeatBuilding(
                demand.index, **args).get_bdew_profile()
        elif de['load profile'] in electricity_slps:
            year = datetime.datetime.strptime(str(ts['start date']),
                                              '%Y-%m-%d %H:%M:%S').year
            # Imports standard load profiles
            e_slp = bdew.ElecSlp(year)
            # TODO Discuss if this is right !!! ( dyn_function_h0 )
            demand = e_slp.get_profile({de['load profile']: 1})
            # creates time series based on standard load profiles
            demand = demand.resample(temp_resolution).mean()
        # sets the nominal value
        args = {'nominal_value': de['annual demand']}
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

    def richardson_sink(self, de: dict, nodes_data: dict, weather_data):
        """
            Creates a sink with stochastically timeseries.

            Creates a sink with stochastically generated input, using
            richardson.py. Used for the modelling of residential
            electricity demands. In this context the method uses the
            create_sink method.

            :param de: dictionary containing all information for
                       the creation of an oemof sink. At least the
                       following key-value-pairs have to be included:

                            - 'label'
                            - 'fixed'
                            - 'annual demand'
                            - 'occupants'
            :type de: dict
            :param nodes_data: dictionary containing excel sheets
            :type nodes_data: dict

            Christian Klemm - christian.klemm@fh-muenster.de
        """

        import richardsonpy.classes.occupancy as occ
        import richardsonpy.classes.electric_load as eload
        # Import Weather Data
        dirhi = weather_data["dirhi"].values.flatten()
        dhi = weather_data["dhi"].values.flatten()

        # Conversion of irradiation from W/m^2 to kW/m^2
        dhi = dhi / 1000
        dirhi = dirhi / 1000

        # Reads the temporal resolution from the scenario file
        ts = nodes_data['energysystem']
        temp_resolution = ts['temporal resolution'][1]

        # sets the occupancy rates
        nb_occ = de['occupants']

        # Workaround, because richardson.py only allows a maximum
        # of 5 occupants
        if nb_occ > 5:
            nb_occ = 5

        # sets the temporal resolution of the richardson.py time series,
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
                                         total_nb_occ=nb_occ, q_direct=dirhi,
                                         q_diffuse=dhi, timestep=timestep)

        # creates richardson.py time series
        load_profile = el_load_obj.loadcurve
        richardson_demand = (sum(el_load_obj.loadcurve)
                             * timestep / (3600 * 1000))
        annual_demand = de['annual demand']

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

    def __init__(self, nodes_data: dict, busd: dict, nodes: list, time_series,
                 weather_data, energetic_renovation):
        """ Inits the sink class.
        ---
        Other variables:

            nodes_sinks: obj:'list'
                -- class intern list of sinks that are already created

        """

        # Delete possible residues of a previous run from the class
        # internal list nodes_sinks
        self.nodes_sinks = []
        # Initialise a class intern copy of the bus dictionary
        self.busd = busd.copy()
        self.energetic_renovation = energetic_renovation.copy()
        self.weatherdata = weather_data.copy()

        # Create sink objects
        for i, de in nodes_data['sinks'].iterrows():
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
                    self.timeseries_sink(de, time_series)

                # Create Sinks with SLP's
                elif de['load profile'] in slps:
                    self.slp_sink(de, nodes_data, weather_data)

                # Richardson
                elif de['load profile'] == 'richardson':
                    self.richardson_sink(de, nodes_data, weather_data)

        # appends created sinks on the list of nodes
        for i in range(len(self.nodes_sinks)):
            nodes.append(self.nodes_sinks[i])
        nodes_data["energetic_renovation"] = self.energetic_renovation.copy()


class Transformers:
    """
        Creates a transformer object.
        Creates transformers objects as defined in 'nodes_data' and adds
        them to the list of components 'nodes'.

        :param nodes_data: dictionary containing data from excel scenario
                           file. The following data have to be provided:

                                - label,
                                - active,
                                - transformer type,
                                - input,
                                - output,
                                - output2,
                                - efficiency,
                                - efficiency2,
                                - variable input costs,
                                - variable output costs,
                                - existing capacity,
                                - max. investment capacity,
                                - min. investment capacity,
                                - periodical costs
        :type nodes_data: dict
        :param busd: dictionary containing the buses of the energy system
        :type busd: dict
        :param nodes: list of components created before(can be empty)
        :type nodes: list

        Christian Klemm - christian.klemm@fh-muenster.de
    """
    # intern variables
    nodes_transformer = []
    busd = None

    def create_transformer(self, tf, inputs, outputs, conversion_factors):
        """ TODO Docstring missing """
        self.nodes_transformer.append(solph.Transformer(
            label=tf['label'], **inputs, **outputs, **conversion_factors))
        logging.info('   ' + 'Transformer created: ' + tf['label'])

    def generic_transformer(self, tf: dict):
        """
            Creates a Generic Transformer object.
            Creates a generic transformer with the parameters given in
            'nodes_data' and adds it to the list of components 'nodes'.

            :param tf: dictionary containing all information for the
                       creation of an oemof transformer. At least the
                       following key-value-pairs have to be included:

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
                            - 'max. investment capacity / (kW)'
                            - 'existing capacity / (kW)'
                            - 'non-convex investment'
                            - 'fix investment costs / (CU/a)'
            :type tf: dict

            Christian Klemm - christian.klemm@fh-muenster.de
        """
        outputs = \
            {self.busd[tf['output']]: solph.Flow(
                variable_costs=tf['variable output costs'],
                emission_factor=tf[
                    'variable output constraint costs'],
                investment=solph.Investment(
                    ep_costs=tf['periodical costs'],
                    periodical_constraint_costs=tf[
                        'periodical constraint costs'],
                    minimum=tf['min. investment capacity'],
                    maximum=tf['max. investment capacity']
                    if tf['max. investment capacity'] != "inf"
                    else float("+inf"),
                    existing=tf['existing capacity'],
                    nonconvex=True if
                    tf['non-convex investment'] == 1 else False,
                    offset=tf['fix investment costs']))}
        conversion_factors = {self.busd[tf['output']]: tf['efficiency']}
        # Defines Capacity values for the second transformer output
        if tf['output2'] not in ['None', 'none', 0]:
            existing_capacity2 = \
                ((float(tf['efficiency2']) / float(tf['efficiency']))
                 * float(tf['existing capacity']))
            minimum_capacity2 = ((float(tf['efficiency2'])
                                  / float(tf['efficiency']))
                                 * float(tf['min. investment capacity']))
            maximum_capacity2 = ((float(tf['efficiency2'])
                                  / float(tf['efficiency']))
                                 * float(tf['max. investment capacity']))
            # Creates transformer object and adds it to the list of
            # components
            outputs.update(
                {self.busd[tf['output2']]: solph.Flow(
                    variable_costs=tf['variable output costs 2'],
                    emission_factor=tf[
                        'variable output constraint costs 2'],
                    investment=solph.Investment(
                        ep_costs=0,
                        existing=existing_capacity2,
                        minimum=minimum_capacity2,
                        maximum=maximum_capacity2
                        if tf['max. investment capacity'] != "inf"
                        else float("+inf"),
                        nonconvex=True if
                        tf['non-convex investment'] == 1 else False,
                        offset=tf['fix investment costs']))})
            conversion_factors.update(
                {self.busd[tf['output2']]: tf['efficiency2']})
        outputs = {"outputs": outputs}

        conversion_factors = {"conversion_factors": conversion_factors}
        inputs = {"inputs": {self.busd[tf['input']]: solph.Flow(
            variable_costs=tf['variable input costs'],
            emission_factor=tf['variable input constraint costs'])
        }}
        self.create_transformer(tf, inputs, outputs, conversion_factors)

    def compression_heat_transformer(self, tf: dict, data):
        """
            Creates a Compression Heat Pump or Compression Chiller by using
            oemof.thermal and adds it to the list of components 'nodes'.
            Parameters are given in 'nodes_data' are used .

            :param tf: has to contain the following keyword arguments

                - 'label'
                - 'variable input costs / (CU/kWh)'
                - 'variable output costs / (CU/kWh)'
                - 'min. investment capacity / (kW)'
                - 'max. investment capacity / (kW)'
                - 'existing capacity / (kW)'
                - 'transformer type': 'compression_heat_transformer'
                - 'mode':
                    - 'heat_pump' or
                    - 'chiller'
                - 'heat source'
                - 'temperature high'
                - 'temperature low'
                - 'quality grade'
                - 'area'
                - 'length of the geoth. probe'
                - 'heat extraction'
                - 'min. borehole area'
                - 'temp. threshold icing'
                - 'factor icing'
            :type tf: dict
            :param data: Dataframe containing all temperature information \
                         for the low temperature source. At least the \
                         following key-value-pairs have to be included:

                            - 'ground_temp'
                            - 'groundwater_temp'
                            - 'temperature'
                            - 'water_temp'
            :type data: pandas.core.frame.Dataframe

            :raise SystemError: choosen heat source not defined

            Janik Budde - Janik.Budde@fh-muenster.de
            Yannick Wittor - yw090223@fh-muenster.de
        """

        # import oemof.thermal in order to calculate the cop
        import oemof.thermal.compression_heatpumps_and_chillers \
            as cmpr_hp_chiller
        import math

        # creates one oemof-bus object for compression heat transformers
        # depending on mode of operation
        if tf['mode'] == 'heat_pump':
            temp = '_low_temp'
        elif tf['mode'] == 'chiller':
            temp = '_high_temp'
        else:
            raise ValueError("Mode of " + tf['label']
                             + "contains a typo")
        bus = solph.Bus(label=tf['label'] + temp + '_bus')

        # adds the bus object to the list of components "nodes"
        self.nodes_transformer.append(bus)
        self.busd[tf['label'] + temp + '_bus'] = bus

        # returns logging info
        logging.info('   ' + 'Bus created: ' + tf['label'] + temp + '_bus')

        # differentiation between heat sources under consideration of mode
        # of operation
        # ground as a heat source referring to vertical-borehole
        # ground-coupled compression heat transformers
        if tf['heat source'] == "Ground":

            # borehole that acts as heat source for the transformer
            cmpr_heat_transformer_label = tf['label'] + \
                                          temp + '_ground_source'

            # the capacity of a borehole is limited by the area
            heatsource_capacity = \
                tf['area'] * \
                (tf['length of the geoth. probe']
                 * tf['heat extraction']
                 / tf['min. borehole area'])
        # ground water as a heat source
        elif tf['heat source'] == "GroundWater":

            # ground water that acts as heat source for the transformer
            cmpr_heat_transformer_label = tf['label'] + \
                                          temp + '_groundwater_source'

            # the capacity of ambient ground water is not limited
            heatsource_capacity = math.inf

        # ambient air as a heat source
        elif tf['heat source'] == "Air":

            # ambient air that acts as heat source for the transformer
            cmpr_heat_transformer_label = tf['label'] + temp + '_air_source'

            # the capacity of ambient air is not limited
            heatsource_capacity = math.inf

        # surface water as a heat source
        elif tf['heat source'] == "Water":

            # ambient air that acts as heat source for the transformer
            cmpr_heat_transformer_label = tf['label'] + temp + '_water_source'

            # the capacity of ambient water is not limited
            heatsource_capacity = math.inf
        else:
            raise ValueError(tf['label'] + " Error in heat source attribute")
        maximum = heatsource_capacity
        # Creates heat source for transformer. The heat source costs are
        # considered by the transformer.
        self.nodes_transformer.append(
            solph.Source(label=cmpr_heat_transformer_label,
                         outputs={self.busd[
                             tf['label'] + temp + '_bus']: solph.Flow(
                             investment=solph.Investment(ep_costs=0,
                                                         minimum=0,
                                                         maximum=maximum,
                                                         existing=0),
                             variable_costs=0)}))

        # Returns logging info
        logging.info(
            '   ' + 'Heat Source created: ' + tf['label']
            + temp + '_source')

        # set temp_high and temp_low and icing considering different
        # heat sources and the mode of operation
        if tf['heat source'] == "Ground":
            if tf['mode'] == 'heat_pump':
                temp_low = data['ground_temp']
            elif tf['mode'] == 'chiller':
                temp_high = data['ground_temp']
        elif tf['heat source'] == "GroundWater":
            if tf['mode'] == 'heat_pump':
                temp_low = data['groundwater_temp']
            elif tf['mode'] == 'chiller':
                temp_high = data['groundwater_temp']
        elif tf['heat source'] == "Air":
            if tf['mode'] == 'heat_pump':
                temp_low = data['temperature']
            elif tf['mode'] == 'chiller':
                temp_high = data['temperature'].copy()
                temp_low_value = tf['temperature low']
                # low temperature as formula to avoid division by zero error
                for index, value in enumerate(temp_high):
                    if value == temp_low_value:
                        temp_high[index] = temp_low_value + 0.1
        elif tf['heat source'] == "Water":
            if tf['mode'] == 'heat_pump':
                temp_low = data['water_temp']
            elif tf['mode'] == 'chiller':
                temp_high = data['water_temp']
        else:
            raise SystemError(tf['label'] + " Error in heat source attribute")

        if tf['mode'] == 'heat_pump':
            temp_threshold_icing = tf['temp. threshold icing']
            factor_icing = tf['factor icing']
            temp_high = [tf['temperature high']]
        elif tf['mode'] == 'chiller':
            # variable "icing" is not important in cooling mode
            temp_threshold_icing = None
            factor_icing = None
            temp_low = [tf['temperature low']]
        else:
            raise ValueError("Mode of " + tf['label']
                             + "contains a typo")
        # calculation of COPs with set parameters
        cops_hp = cmpr_hp_chiller.calc_cops(
            temp_high=temp_high,
            temp_low=temp_low,
            quality_grade=tf['quality grade'],
            temp_threshold_icing=temp_threshold_icing,
            factor_icing=factor_icing,
            mode=tf['mode'])
        logging.info('   ' + tf['label']
                     + ", Average Coefficient of Performance (COP): {:2.2f}"
                     .format(numpy.mean(cops_hp)))

        # Creates transformer object and adds it to the list of components
        inputs = {"inputs": {self.busd[tf['input']]: solph.Flow(
            variable_costs=tf['variable input costs'],
            emission_factor=
            tf['variable input constraint costs']),
            self.busd[tf['label'] + temp + '_bus']: solph.Flow(
                variable_costs=0)}}
        outputs = {"outputs": {self.busd[tf['output']]: solph.Flow(
            variable_costs=tf['variable output costs'],
            emission_factor=tf[
                'variable output constraint costs'],
            investment=solph.Investment(
                ep_costs=tf['periodical costs'],
                minimum=tf['min. investment capacity'],
                maximum=tf['max. investment capacity']
                if tf['max. investment capacity'] != "inf"
                else float("+inf"),
                periodical_constraint_costs=tf[
                    'periodical constraint costs'],
                existing=tf['existing capacity']))}}
        conversion_factors = {
            "conversion_factors": {
                self.busd[tf['label'] + temp + '_bus']:
                    [((cop - 1) / cop) / tf['efficiency']
                     for cop in cops_hp],
                self.busd[tf['input']]: [1 / cop for cop in cops_hp]}}
        self.create_transformer(tf, inputs, outputs, conversion_factors)

    def genericchp_transformer(self, tf: dict, nd: dict):
        """
            Creates a Generic CHP transformer object.
            Creates a generic chp transformer with the parameters given
            in 'nodes_data' and adds it to the list of components
            'nodes'.

            :param tf: dictionary containing all information for the
                       creation of an oemof transformer. At least the
                       following key-value-pairs have to be included:

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
                            - 'max. investment capacity / (kW)'
                            - 'existing capacity / (kW)'
                            - 'non-convex investment'
                            - 'fix investment costs / (CU/a)'
            :type tf: dict
            :param nd: dictionary containing parameters of the buses
                       to be created.
            :type nd: dict

            Christian Klemm - christian.klemm@fh-muenster.de
        """
        # counts the number of periods within the given datetime index
        # and saves it as variable
        # (number of periods is required for creating generic chp transformers)
        # Importing timesystem parameters from the scenario
        ts = next(nd['energysystem'].iterrows())[1]
        periods = int(ts['periods'])
        # creates genericCHP transformer object and adds it to the
        # list of components
        self.nodes_transformer.append(solph.components.GenericCHP(
            label=tf['label'],
            fuel_input={
                self.busd[tf['input']]: solph.Flow(
                    H_L_FG_share_max=[
                        tf['share of flue gas loss at max heat '
                           'extraction']
                        for p in range(0, periods)],
                    H_L_FG_share_min=[
                        tf['share of flue gas loss at min heat '
                           'extraction']
                        for p in range(0, periods)],
                    variable_costs=tf[
                        'variable input costs'],
                    emission_factor=
                    tf['variable input constraint costs'])},
            electrical_output={
                self.busd[tf['output']]: solph.Flow(
                    investment=solph.Investment(
                        ep_costs=tf[
                            'periodical costs'],
                        periodical_constraint_costs=tf[
                            'periodical constraint costs'],
                        minimum=tf['min. investment capacity'],
                        maximum=tf['max. investment capacity']
                        if tf['max. investment capacity'] != "inf"
                        else float("+inf")
                        ,
                        existing=tf['existing capacity'],
                        nonconvex=True if
                        tf['non-convex investment'] == 1 else False,
                        offset=tf['fix investment costs']
                    ),
                    P_max_woDH=[
                        tf['max. electric power without district '
                           'heating']
                        for p in range(0, periods)],
                    P_min_woDH=[tf['min. electric power without '
                                   'district heating']
                                for p in range(0, periods)],
                    Eta_el_max_woDH=[
                        tf['el. eff. at max. fuel flow w/o distr. '
                           'heating']
                        for p in range(0, periods)],
                    Eta_el_min_woDH=[
                        tf['el. eff. at min. fuel flow w/o distr. '
                           'heating']
                        for p in range(0, periods)],
                    variable_costs=tf[
                        'variable output costs'],
                    emission_factor=tf[
                        'variable output constraint costs']
                )
            },
            heat_output={self.busd[tf['output2']]: solph.Flow(
                Q_CW_min=[tf['minimal therm. condenser load to '
                             'cooling water']
                          for p in range(0, periods)],
                variable_costs=tf[
                    'variable output costs 2'],
                emission_factor=tf[
                    'variable output constraint costs 2']
            )},
            Beta=[tf['power loss index']
                  for p in range(0, periods)],
            # fixed_costs=0,
            back_pressure=True if tf['back pressure'] == 1 else False,
        ))

        # returns logging info
        logging.info('   ' + 'Transformer created: ' + tf['label'])

    def absorption_heat_transformer(self, tf, data):
        """
            Creates an absorption heat transformer object with the parameters
            given in 'nodes_data' and adds it to the list of components 'nodes'


            :type tf: dict
            :param tf: has to contain the following keyword arguments
                - Standard Input information of transformer class
                - 'transformer type': 'absorption_heat_transformer'
                - 'mode': 'chiller'
                - 'name'
                    - name refers to models of absorption heat transformers
                      with different equation parameters. See documentation
                      for possible inputs.
                - 'high temperature'
                - 'chilling temperature'
                - 'electrical input conversion factor'
                - 'recooling temperature difference'
            :param data: weather data
            :type data: dict

            Yannick Wittor - yw090223@fh-muenster.de
        """
        # import oemof.thermal in order to calculate COP
        import oemof.thermal.absorption_heatpumps_and_chillers \
            as abs_hp_chiller
        from math import inf
        import numpy as np

        # Import characteristic equation parameters
        char_para = pd.read_csv(os.path.join(
            os.path.dirname(__file__)) +
                                '/technical_data/characteristic_parameters.csv')

        # creates one oemof-bus object for compression heat transformers
        # depending on mode of operation
        if tf['mode'] == 'heat_pump':
            temp = '_low_temp'
        elif tf['mode'] == 'chiller':
            temp = '_high_temp'
        else:
            raise ValueError("Mode of " + tf['label']
                             + "contains a typo")

        bus_label = tf['label'] + temp + '_bus'
        source_label = tf['label'] + temp + '_source'
        bus = solph.Bus(label=bus_label)

        # adds the bus object to the list of components "nodes"
        self.nodes_transformer.append(bus)
        self.busd[bus_label] = bus

        # returns logging info
        logging.info('   ' + 'Bus created: ' + bus_label)

        # Calculates cooling temperature in absorber/evaporator depending on
        # ambient air temperature of recooling system
        data_np = np.array(data['temperature'])
        t_cool = data_np + \
                 tf['recooling temperature difference']
        t_cool = list(map(int, t_cool))
        n = len(t_cool)

        # Calculation of characteristic temperature difference
        chiller_name = tf['name']
        ddt = abs_hp_chiller.calc_characteristic_temp(
            t_hot=[tf['high temperature']],
            t_cool=t_cool,
            t_chill=[tf['chilling temperature']],
            coef_a=char_para[(char_para['name'] ==
                              chiller_name)]['a'].values[0],
            coef_e=char_para[(char_para['name'] ==
                              chiller_name)]['e'].values[0],
            method='kuehn_and_ziegler')
        # Calculation of cooling capacity
        q_dots_evap = abs_hp_chiller.calc_heat_flux(
            ddts=ddt,
            coef_s=char_para[(char_para['name'] ==
                              chiller_name)]['s_E'].values[0],
            coef_r=char_para[(char_para['name'] ==
                              chiller_name)]['r_E'].values[0],
            method='kuehn_and_ziegler')
        # Calculation of driving heat
        q_dots_gen = abs_hp_chiller.calc_heat_flux(
            ddts=ddt,
            coef_s=char_para[(char_para['name'] ==
                              chiller_name)]['s_G'].values[0],
            coef_r=char_para[(char_para['name'] ==
                              chiller_name)]['r_G'].values[0],
            method='kuehn_and_ziegler')
        # Calculation of COPs
        cops_abs = \
            [Qevap / Qgen for Qgen, Qevap in zip(q_dots_gen, q_dots_evap)]

        logging.info('   ' + tf['label']
                     + ", Average Coefficient of Performance (COP): {:2.2f}"
                     .format(numpy.mean(cops_abs)))

        # creates a source object as high temperature heat source and sets
        # heat capacity for this source
        maximum = tf['heat capacity of source']
        self.nodes_transformer.append(
            solph.Source(label=source_label,
                         outputs={self.busd[
                             tf['label'] + temp + '_bus']: solph.Flow(
                             investment=solph.Investment(ep_costs=0,
                                                         minimum=0,
                                                         maximum=maximum,
                                                         existing=0),
                             variable_costs=0)}))

        # Returns logging info
        logging.info(
            '   ' + 'Heat Source created:' + source_label)

        # Set in- and outputs with conversion factors and creates transformer
        # object and adds it to  the list of components
        inputs = {"inputs": {self.busd[tf['input']]: solph.Flow(
            variable_costs=tf['variable input costs'],
            emission_factor=
            tf['variable input constraint costs']),
            self.busd[tf['label'] + temp + '_bus']: solph.Flow(
                variable_costs=0)}}
        outputs = {"outputs": {self.busd[tf['output']]: solph.Flow(
            variable_costs=tf['variable output costs'],
            emission_factor=tf['variable output constraint costs'],
            investment=solph.Investment(
                ep_costs=tf['periodical costs'],
                minimum=tf['min. investment capacity'],
                maximum=tf['max. investment capacity']
                if tf['max. investment capacity'] != "inf"
                else float("+inf"),
                existing=tf['existing capacity']))}}
        conversion_factors = {
            "conversion_factors": {
                self.busd[tf['output']]:
                    [cop for cop in cops_abs],
                self.busd[tf['input']]:
                    tf['electrical input conversion factor']
            }}
        self.create_transformer(tf, inputs, outputs, conversion_factors)

    def __init__(self, nodes_data, nodes, busd, weather_data):
        """ TODO Docstring missing """
        # renames variables
        self.busd = busd
        self.nodes_transformer = []

        # creates a transformer object for every transformer item within nd
        for i, t in nodes_data['transformers'].iterrows():
            if t['active']:
                # Create Generic Transformers
                if t['transformer type'] == 'GenericTransformer':
                    self.generic_transformer(t)

                # Create Compression Heat Transformer
                elif t['transformer type'] == 'CompressionHeatTransformer':
                    self.compression_heat_transformer(t, weather_data)

                # Create Extraction Turbine CHPs
                elif t['transformer type'] == 'ExtractionTurbineCHP':
                    logging.info('   ' + 'WARNING: ExtractionTurbineCHP are'
                                         ' currently not a part of this model '
                                         'generator, but will be added later.')

                # Create Generic CHPs
                elif t['transformer type'] == 'GenericCHP':
                    self.genericchp_transformer(t, nodes_data)

                # Create Offset Transformers
                elif t['transformer type'] == 'OffsetTransformer':
                    logging.info(
                        '   ' + 'WARNING: OffsetTransformer are currently'
                        + ' not a part of this model generator, but will'
                        + ' be added later.')

                # Create Absorption Chiller
                elif t['transformer type'] == 'AbsorptionHeatTransformer':
                    self.absorption_heat_transformer(t, weather_data)

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
    """
        Creates oemof storage objects as defined in 'nodes_data' and
        adds them to the list of components 'nodes'.

        :param nodes_data: dictionary containing parameters of storages
                           to be created.The following data have to be
                           provided:

                                - 'label'
                                - 'active'
                                - 'bus'
                                - 'existing capacity / (kWh)'
                                - 'min.investment capacity / (kWh)'
                                - 'max.investment capacity / (kWh)'
                                - 'non-convex investments'
                                - 'fix investment costs'
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
        :type nodes_data: dict
        :param busd: dictionary containing the buses of the energy system
        :type busd: dict
        :param nodes: list of components created before(can be empty)
        :type nodes: list

        Christian Klemm - christian.klemm@fh-muenster.de
    """

    def generic_storage(self, s):
        """
            Creates a generic storage object with the parameters
            given in 'nodes_data' and adds it to the list of components 'nodes'
            ----
            Keyword arguments:
            t : obj:'dict'
                -- dictionary containing all information for
                the creation of an oemof storage.
        """

        # creates storage object and adds it to the
        # list of components
        self.nodes.append(
            solph.components.GenericStorage(
                label=s['label'],
                inputs={self.busd[s['bus']]: solph.Flow(
                    variable_costs=s[
                        'variable input costs'],
                    emission_factor=s[
                        'variable input constraint costs']
                )},
                outputs={self.busd[s['bus']]: solph.Flow(
                    variable_costs=s[
                        'variable output costs'],
                    emission_factor=s[
                        'variable output constraint costs']
                )},
                loss_rate=s['capacity loss'],
                inflow_conversion_factor=s['efficiency inflow'],
                outflow_conversion_factor=s['efficiency outflow'],
                invest_relation_input_capacity=s['input/capacity ratio'],
                invest_relation_output_capacity=s['output/capacity ratio'],
                investment=solph.Investment(
                    ep_costs=s['periodical costs'],
                    periodical_constraint_costs=s[
                        'periodical constraint costs'],
                    existing=s['existing capacity'],
                    minimum=s['min. investment capacity'],
                    maximum=s['max. investment capacity']
                    if s['max. investment capacity'] != "inf"
                    else float("+inf"),
                    nonconvex=True if
                    s['non-convex investment'] == 1 else False,
                    offset=s['fix investment costs'])))

        # returns logging info
        logging.info('   ' + 'Storage created: ' + s['label'])

    def stratified_thermal_storage(self, s, data):
        """
            Creates a stratified thermal storage object with the parameters
            given in 'nodes_data' and adds it to the list of components 'nodes'


            :type s: dict
            :param s: has to contain the following keyword arguments:
                - Standard information on Storages
                - 'storage type': 'Stratified'
                - 'diameter'
                - 'temperature high'
                - 'temperature low'
                - 'U value /(W/(sqm*K))'
            @ Yannick Wittor - yw090223@fh-muenster.de, 26.01.2021
        """
        # import functions for stratified thermal storages from oemof thermal
        from oemof.thermal.stratified_thermal_storage import calculate_losses
        # Import weather Data
        data.index = pd.to_datetime(data["timestamp"].values, utc=True)
        data.index = pd.to_datetime(data.index).tz_convert("Europe/Berlin")
        # calculations for stratified thermal storage
        loss_rate, fixed_losses_relative, fixed_losses_absolute = \
            calculate_losses(
                s['U value'],
                s['diameter'],
                s['temperature high'],
                s['temperature low'],
                data['temperature'])

        # creates storage object and adds it to the
        # list of components
        self.nodes.append(
            solph.components.GenericStorage(
                label=s['label'],
                inputs={self.busd[s['bus']]: solph.Flow(
                    variable_costs=s['variable input costs'],
                    emission_factor=s['variable input constraint costs']
                )},
                outputs={self.busd[s['bus']]: solph.Flow(
                    variable_costs=s['variable output costs'],
                    emission_factor=s['variable output constraint costs']
                )},
                min_storage_level=s['capacity min'],
                max_storage_level=s['capacity max'],
                loss_rate=loss_rate,
                fixed_losses_relative=fixed_losses_relative,
                fixed_losses_absolute=fixed_losses_absolute,
                inflow_conversion_factor=s['efficiency inflow'],
                outflow_conversion_factor=s['efficiency outflow'],
                invest_relation_input_capacity=s['input/capacity ratio'],
                invest_relation_output_capacity=s['output/capacity ratio'],
                investment=solph.Investment(
                    ep_costs=s['periodical costs'],
                    periodical_constraint_costs=s[
                        'periodical constraint costs'],
                    existing=s['existing capacity'],
                    minimum=s['min. investment capacity'],
                    maximum=s['max. investment capacity']
                    if s['max. investment capacity'] != "inf"
                    else float("+inf"),
                    nonconvex=True if
                    s['non-convex investment'] == 1 else False,
                    offset=s['fix investment costs'])))
        # returns logging info
        logging.info('   ' + 'Storage created: ' + s['label'])

    def __init__(self, nodes_data: dict, nodes: list, busd: dict):
        """
            Inits the storage class.

            Christian Klemm - christian.klemm@fh-muenster.de
        """
        # renames variables
        self.busd = busd
        self.nodes = []

        # creates storage object for every storage element in nodes_data
        for i, s in nodes_data['storages'].iterrows():
            if s['active']:

                # Create Generic Storage
                if s['storage type'] == 'Generic':
                    self.generic_storage(s)

                # Create Generic Storage
                if s['storage type'] == 'Stratified':
                    self.stratified_thermal_storage(s,
                                                    nodes_data['weather data'])

        # appends created storages to the list of nodes
        for i in range(len(self.nodes)):
            nodes.append(self.nodes[i])


class Links:
    """
        Creates links objects as defined in 'nodes_data' and adds them
        to the list of components 'nodes'.

        # TODO Excel columns missing

        :param nodes_data: dictionary containing data from excel
                           scenario file. The following data have to be
                           provided:

                                - 'active'
                                - 'label'
                                - '(un)directed'
        :type nodes_data: dict
        :param busd: dictionary containing the buses of the energy system
        :type busd: dict
        :param nodes: list of components created before(can be empty)
        :type nodes: list

        Christian Klemm - christian.klemm@fh-muenster.de
    """
    # intern variables
    busd = None

    def __init__(self, nodes_data, nodes, bus):
        """
            Inits the Links class.

            Christian Klemm - christian.klemm@fh-muenster.de
        """
        # renames variables
        self.busd = bus
        # creates link objects for every link object in nd
        for i, link in nodes_data['links'].iterrows():
            if link['active']:
                if link['(un)directed'] == 'directed':
                    ep_costs = link['periodical costs']
                elif link['(un)directed'] == 'undirected':
                    ep_costs = link['periodical costs'] / 2
                else:
                    raise SystemError('Problem with periodical costs')
                nodes.append(solph.custom.Link(
                    label=link['label'],
                    inputs={self.busd[link['bus1']]: solph.Flow(),
                            self.busd[link['bus2']]: solph.Flow()},
                    outputs={self.busd[link['bus2']]: solph.Flow(
                        variable_costs=
                        link['variable output costs'],
                        emission_factor=
                        link['variable constraint costs'],
                        investment=solph.Investment(
                            ep_costs=ep_costs,
                            periodical_constraint_costs=link[
                                'periodical constraint costs'],
                            minimum=link[
                                'min. investment capacity'],
                            maximum=link['max. investment capacity']
                            if link['max. investment capacity'] != "inf"
                            else float("+inf"),
                            existing=link[
                                'existing capacity'],
                            nonconvex=True if
                            link['non-convex investment'] == 1
                            else False,
                            offset=link[
                                'fix investment costs'])),
                        self.busd[link['bus1']]: solph.Flow(
                            variable_costs=
                            link['variable output costs'],
                            emission_factor=
                            link['variable constraint costs'],
                            investment=solph.Investment(
                                ep_costs=ep_costs,
                                periodical_constraint_costs=link[
                                    'periodical constraint costs'],
                                minimum=link[
                                    'min. investment capacity'],
                                maximum=link['max. investment capacity']
                                if link['max. investment capacity'] != "inf"
                                else float("+inf"),
                                existing=link[
                                    'existing capacity'],
                                nonconvex=True if
                                link['non-convex investment'] == 1
                                else False,
                                offset=link[
                                    'fix investment costs'])), },
                    conversion_factors={
                        (self.busd[link['bus1']],
                         self.busd[link['bus2']]): link['efficiency'],
                        (self.busd[link['bus2']],
                         self.busd[link['bus1']]):
                            (link['efficiency']
                             if link['(un)directed'] == 'undirected' else 0)}
                ))
                # returns logging info
                logging.info('   ' + 'Link created: ' + link['label'])
