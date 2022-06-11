from feedinlib import powerplants, WindPowerPlant
from oemof.solph import Source, Flow, Investment, Bus, Transformer
import logging
import pandas as pd


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
        # output default
        if output is None:
            output = self.busd[so['output']]
        # set variables minimum, maximum and existing
        minimum = so['min. investment capacity']
        maximum = (so['max. investment capacity']
                   if so['max. investment capacity'] != "inf"
                   else float("+inf"))
        existing = so['existing capacity']
        ep_costs = so['periodical costs']
        ep_constr_costs = so['periodical constraint costs']
        non_convex = True if so['non-convex investment'] == 1 else False
        # Creates a oemof source and appends it to the nodes_sources
        # (variable of the create_sources-class) list
        self.nodes_sources.append(
            Source(
                label=so['label'],
                outputs={output: Flow(
                        investment=Investment(
                            ep_costs=ep_costs,
                            periodical_constraint_costs=ep_constr_costs,
                            minimum=minimum,
                            maximum=maximum,
                            existing=existing,
                            nonconvex=non_convex,
                            offset=so['fix investment costs'],
                            fix_constraint_costs=so["fix investment constraint"
                                                    " costs"]),
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
        self.create_source(so, {'min': 0, 'max': 1}, self.busd[so['output']])
        
        # Returns logging info
        logging.info('\t Commodity Source created: ' + so['label'])
    
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
        logging.info('\t Timeseries Source created: ' + so['label'])
        
    def create_feedin_source(self, feedin: pd.Series, so: dict):
        """
        
        """
        if so["fixed"] == 1:
            # sets the attribute for a fixed pv_source
            args = {'fix': feedin}
        elif so["fixed"] == 0:
            # sets the attributes for an unfixed pv_source
            args = {'min': 0, 'max': feedin}
        else:
            raise SystemError(so["label"] + " Error in fixed attribute")
    
        # starts the create_source method with the parameters set before
        self.create_source(so, args, self.busd[so['output']])
    
        # returns logging info
        logging.info('\t Source created: ' + so["label"])
        
    def pv_source(self, so: dict, weather_dataframe: pd.DataFrame):
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
            :param weather_dataframe: Dataframe containing:

                            - 'dirhi'
                            - 'dhi'
                            - 'dni'
                            - 'temperature'
                            - 'windspeed'
            :type weather_dataframe: pd.DataFrame

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
        weather_dataframe['ghi'] = (weather_dataframe.dirhi
                                    + weather_dataframe.dhi)
        
        # changes names of data columns,
        # so it fits the needs of the feedinlib
        name_dc = {'temperature': 'temp_air', 'windspeed': 'v_wind'}
        weather_dataframe.rename(columns=name_dc)
        
        # calculates time series normed on 1 kW pv peak performance
        feedin = pv_module.feedin(weather=weather_dataframe,
                                  location=(so['Latitude'], so['Longitude']),
                                  scaling='peak_power')

        # Replace 'nan' value with 0
        feedin = feedin.fillna(0)
        # Set negative values to zero (requirement for solving the model)
        feedin[feedin < 0] = 0
        # Set values greater 1 to 1 (requirement for solving the model)
        feedin[feedin > 1] = 1

        self.create_feedin_source(feedin, so)
    
    def windpower_source(self, so: dict, weather_df: pd.DataFrame):
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
            :param weather_df: Dataframe containing:

                            - 'windspeed'
                            - 'temperature'
                            - 'z0'
                            - 'pressure'
            :type weather_df: pd.DataFrame

            Christian Klemm - christian.klemm@fh-muenster.de
        """
        
        # set up wind turbine using the wind turbine library.
        # The turbine name must correspond to an entry in the turbine
        # data-base of the feedinlib. Unit of the hub height is m.
        turbine_data = {'turbine_type': so['Turbine Model'],
                        'hub_height': so['Hub Height']}
        # create windturbine
        wind_turbine = WindPowerPlant(**turbine_data)
        
        weather_df = weather_df[['windspeed', 'temperature', 'z0', 'pressure']]
        # second row is height of data acquisition in m
        weather_df.columns = [['wind_speed', 'temperature', 'roughness_length',
                               'pressure'], [0, 2, 10, 0]]
        
        # calculate scaled feed-in
        feedin = wind_turbine.feedin(weather=weather_df,
                                     scaling='nominal_power')

        self.create_feedin_source(feedin, so)
    
    def solar_heat_source(self, so, data, energysystem):
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
        data.index.name = 'Datum'
        data = data.asfreq(energysystem["temporal resolution"])
        
        # calculates global horizontal irradiance from diffuse (dhi)
        # and direct irradiance (dirhi) and adds it to the weather data frame
        data['ghi'] = (data["dirhi"] + data["dhi"])

        collectors_heat = None
        
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
        if so['fixed'] == 1 and collectors_heat is not None:
            # sets the attribute for a fixed solar heat source
            args = {'fix': collectors_heat}
        elif so['fixed'] == 0 and collectors_heat is not None:
            # sets the attributes for an unfixed solar heat source
            args = {'min': 0, 'max': collectors_heat}
        else:
            raise SystemError(so['label'] + " Error in fixed attribute")
        
        # starts the create_source method with the parameters set before
        self.create_source(so, args, output)
        
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
        energysystem = next(nodes_data['energysystem'].iterrows())[1]
        
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
                    self.solar_heat_source(so, weather_data, energysystem)
        
        # appends created sources and other objects to the list of nodes
        for i in range(len(self.nodes_sources)):
            nodes.append(self.nodes_sources[i])