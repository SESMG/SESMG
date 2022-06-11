from feedinlib import powerplants, WindPowerPlant
from oemof.solph import Source, Flow, Investment, Bus, Transformer
import logging
import pandas as pd


class Sources:
    """

        Creates an oemof source with fixed or unfixed timeseries

        There are four options for labeling source objects to be created:

            - 'commodity': a source with flexible time series
            - 'timeseries': a source with predefined time series
            - 'photovoltaic': a photovoltaic component
            - 'wind power': a wind power component
            - 'solar thermal components': a solar thermal or \
              concentrated solar power component

        :param nd: dictionary containing parameters of sources
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
        :type nd: dict
        :param busd: dictionary containing the buses of the energy system
        :type busd: dict
        :param nodes: list of components created before(can be empty)
        :type nodes: list

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
            :param output: defines the oemof output bus
            :type output: Bus

            Christian Klemm - christian.klemm@fh-muenster.de
        """
        # set non convex bool
        non_convex = True if so['non-convex investment'] == 1 else False
        # Creates a oemof source and appends it to the nodes_sources
        # (variable of the create_sources-class) list
        self.nodes_sources.append(
            Source(
                label=so['label'],
                outputs={output: Flow(
                        investment=Investment(
                            ep_costs=so['periodical costs'],
                            periodical_constraint_costs=so[
                                'periodical constraint costs'],
                            minimum=so['min. investment capacity'],
                            maximum=so['max. investment capacity'],
                            existing=so['existing capacity'],
                            nonconvex=non_convex,
                            offset=so['fix investment costs'],
                            fix_constraint_costs=so[
                                "fix investment constraint costs"]),
                        **timeseries_args,
                        variable_costs=so['variable costs'],
                        emission_factor=so['variable constraint costs'])}))
    
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
        self.create_source(so, {'max': 1}, self.busd[so['output']])
        
        # Returns logging info
        logging.info('\t Commodity Source created: ' + so['label'])
    
    def timeseries_source(self, so: dict):
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

            Christian Klemm - christian.klemm@fh-muenster.de
        """
        
        if so['fixed'] == 1:
            # sets the timeseries attribute for a fixed source
            args = {'fix': self.timeseries[so['label'] + '.fix'].tolist()}
        elif so['fixed'] == 0:
            # sets the timeseries attributes for an unfixed source
            args = {'min': self.timeseries[so['label'] + '.min'].tolist(),
                    'max': self.timeseries[so['label'] + '.max'].tolist()}
        else:
            raise SystemError(so['label'] + " Error in fixed attribute")
        
        # starts the create_source method with the parameters set before
        self.create_source(so, args, self.busd[so['output']])
        
        # Returns logging info
        logging.info('\t Timeseries Source created: ' + so['label'])
        
    def create_feedin_source(self, feedin: pd.Series, so: dict, output=None):
        """
        
        """
        if so["fixed"] == 1:
            # sets the attribute for a fixed pv_source
            args = {'fix': feedin}
        elif so["fixed"] == 0:
            # sets the attributes for an unfixed pv_source
            args = {'max': feedin}
        else:
            raise SystemError(so["label"] + " Error in fixed attribute")
        if output is None:
            # starts the create_source method with the parameters set before
            self.create_source(so, args, self.busd[so['output']])
        else:
            # starts the create_source method with the parameters set before
            self.create_source(so, args, output)
        # returns logging info
        logging.info('\t Source created: ' + so["label"])
        
    def pv_source(self, so: dict):
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

            Christian Klemm - christian.klemm@fh-muenster.de
        """
        # reads pv system parameters from parameter dictionary
        # nodes_data
        parameter_set = {
            'azimuth': so['Azimuth'],
            'tilt': so['Surface Tilt'],
            'module_name': so['Modul Model'],
            'inverter_name': so['Inverter Model'],
            'albedo': so['Albedo'],
            "module_type": "glass_glass",
            "racking_model": "open_rack"}
        
        # sets pv system parameters for pv_module
        pv_module = powerplants.Photovoltaic(**parameter_set)
        
        # calculates global horizontal irradiance from diffuse (dhi)
        # and direct irradiance and adds it to the weather data frame
        self.weather_data['ghi'] = (self.weather_data.dirhi
                                    + self.weather_data.dhi)
        
        # changes names of data columns,
        # so it fits the needs of the feedinlib
        name_dc = {'temperature': 'temp_air', 'windspeed': 'v_wind'}
        self.weather_data.rename(columns=name_dc)
        
        # calculates time series normed on 1 kW pv peak performance
        feedin = pv_module.feedin(weather=self.weather_data,
                                  location=(so['Latitude'], so['Longitude']),
                                  scaling='peak_power')

        # Replace 'nan' value with 0
        feedin = feedin.fillna(0)
        # Set negative values to zero (requirement for solving the model)
        feedin[feedin < 0] = 0
        # Set values greater 1 to 1 (requirement for solving the model)
        feedin[feedin > 1] = 1

        self.create_feedin_source(feedin, so)
    
    def windpower_source(self, so: dict):
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

            Christian Klemm - christian.klemm@fh-muenster.de
        """
        
        # set up wind turbine using the wind turbine library.
        # The turbine name must correspond to an entry in the turbine
        # data-base of the feedinlib. Unit of the hub height is m.
        turbine_data = {'turbine_type': so['Turbine Model'],
                        'hub_height': so['Hub Height']}
        # create windturbine
        wind_turbine = WindPowerPlant(**turbine_data)
        
        weather_df = self.weather_data[['windspeed', 'temperature',
                                        'z0', 'pressure']]
        # second row is height of data acquisition in m
        weather_df.columns = [['wind_speed', 'temperature', 'roughness_length',
                               'pressure'], [0, 2, 10, 0]]
        
        # calculate scaled feed-in
        feedin = wind_turbine.feedin(weather=weather_df,
                                     scaling='nominal_power')

        self.create_feedin_source(feedin, so)
    
    def solar_heat_source(self, so: dict):
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
        col_bus = Bus(label=so['label'] + '_bus')
        # adds the bus object to the list of components "nodes"
        self.nodes_sources.append(col_bus)
        self.busd[so['label'] + '_bus'] = col_bus
        output = col_bus
        
        # import weather data and set datetime index with hourly frequency
        self.weather_data.index.name = 'Datum'
        weather_data = self.weather_data.asfreq(
                self.energysystem["temporal resolution"])
        
        # calculates global horizontal irradiance from diffuse (dhi)
        # and direct irradiance (dirhi) and adds it to the weather data frame
        weather_data['ghi'] = (weather_data["dirhi"] + weather_data["dhi"])

        # precalculations for flat plate collectors, calculates total
        # irradiance on collector, efficiency and heat output
        if so['technology'] == 'solar_thermal_flat_plate':
            precalc_res = flat_plate_precalc(
                    lat=so['Latitude'], long=so['Longitude'],
                    collector_tilt=so['Surface Tilt'],
                    collector_azimuth=so['Azimuth'],
                    eta_0=so['ETA 0'], a_1=so['A1'], a_2=so['A2'],
                    temp_collector_inlet=so['Temperature Inlet'],
                    delta_temp_n=so['Temperature Difference'],
                    irradiance_global=(weather_data['ghi']),
                    irradiance_diffuse=(weather_data['dhi']),
                    temp_amb=weather_data['temperature'])
            # set variables collectors_heat and irradiance and conversion
            # from W/sqm to kW/sqm
            irradiance = precalc_res.col_ira / 1000

        # set parameters for precalculations for concentrating solar power
        elif so['technology'] == 'concentrated_solar_power':
            # precalculation with parameter set, ambient temperature and
            # direct horizontal irradiance. Calculates total irradiance on
            # collector, efficiency and heat output
            precalc_res = csp_precalc(
                    lat=so['Latitude'], long=so['Longitude'],
                    collector_tilt=so['Surface Tilt'],
                    collector_azimuth=so['Azimuth'],
                    cleanliness=so['Cleanliness'],
                    a_1=so['A1'], a_2=so['A2'], eta_0=so['ETA 0'],
                    c_1=so['C1'], c_2=so['C2'],
                    temp_collector_inlet=so['Temperature Inlet'],
                    temp_collector_outlet=so[
                        'Temperature Inlet'] + so['Temperature Difference'],
                    temp_amb=weather_data['temperature'],
                    E_dir_hor=weather_data['dirhi'])
            # set variables collectors_heat and irradiance and conversion
            # from W/sqm to kW/sqm
            irradiance = precalc_res.collector_irradiance / 1000
        else:
            raise ValueError("Technology chosen not accepted!")
        collectors_heat = (precalc_res.collectors_heat / 1000) \
            * so['Conversion Factor']
        self.create_feedin_source(collectors_heat, so, output)
        
        self.nodes_sources.append(Transformer(
            label=so['label'] + '_collector',
            inputs={self.busd[so['label'] + '_bus']: Flow(variable_costs=0),
                    self.busd[so['input']]: Flow(variable_costs=0)},
            outputs={self.busd[so['output']]: Flow(variable_costs=0)},
            conversion_factors={
                self.busd[so['label'] + '_bus']: 1,
                self.busd[so['input']]:
                    so['Electric Consumption'] * (1 - so['Peripheral Losses']),
                self.busd[so['output']]: 1 - so['Peripheral Losses']}))
        
        # returns logging info
        logging.info('\t Source created: ' + so['label']
                     + ", Max Heat power output per year and m²: "
                       "{:2.2f}".format(numpy.sum(collectors_heat
                                        / so['Conversion Factor']))
                     + " kWh/(m²a), Irradiance on collector per year and m²: "
                       "{:2.2f}".format(numpy.sum(irradiance)) + ' kWh/(m²a)')
    
    def __init__(self, nd: dict, nodes: list, busd: dict):
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
        self.energysystem = next(nd['energysystem'].iterrows())[1]
        self.weather_data = nd["weather data"].copy()
        self.timeseries = nd["timeseries"].copy()
        switch_dict = {
            "other": self.commodity_source,
            "photovoltaic": self.pv_source,
            "windpower": self.windpower_source,
            "timeseries": self.timeseries_source,
            "solar_thermal_flat_plate": self.solar_heat_source,
            "concentrated_solar_power": self.solar_heat_source
        }
        # Create Source from "Sources" Table
        for i, s in nd["sources"].loc[nd["sources"]["active"] == 1].iterrows():
            switch_dict.get(s["technology"], "Invalid technology !")(s)
        
        # appends created sources and other objects to the list of nodes
        for i in range(len(self.nodes_sources)):
            nodes.append(self.nodes_sources[i])
