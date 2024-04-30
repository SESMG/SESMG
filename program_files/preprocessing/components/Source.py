"""
    Christian Klemm - christian.klemm@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
    Yannick Wittor - yw090223@fh-muenster.de
"""
from feedinlib import powerplants, WindPowerPlant
from oemof.solph.components import Source, Converter
from oemof.solph.buses import Bus
from oemof.solph.flows import Flow
from oemof.solph import Investment
import logging
import pandas


class Sources:
    """
        Creates an oemof source with fixed or unfixed timeseries.

        There are six options for labeling source objects to be created:

            - 'commodity': a source with flexible time series
            - 'timeseries': a source with predefined time series
            - 'photovoltaic': a photovoltaic component
            - 'wind power': a wind power component
            - 'solar thermal components': a solar thermal or \
              concentrated solar power component

        :param nodes_data: dictionary containing parameters of sources \
            to be created. The following data have to be provided:

                - label
                - active
                - fixed
                - output
                - technology
                - input
                - variable costs
                - existing capacity
                - min. investment capacity
                - max. investment capacity
                - periodical costs
                - non-convex investment
                - fix investment cost
                - fix investment constraint costs
                - variable constraint costs
                - periodical constraint costs
                - Turbine Model  (Windpower ONLY)
                - Hub Height  (Windpower ONLY)
                - Modul Model (PV ONLY)
                - Inverter Model (PV ONLY)
                - Azimuth
                - Surface Tilt
                - Albedo
                - Altitude (PV ONLY)
                - Latitude
                - Longitude
                - ETA 0
                - A1
                - A2
                - C1
                - C2
                - Temperature Inlet
                - Temperature Difference
                - Conversion Factor
                - Peripheral Losses
                - Electric Consumption
                - Cleanliness
                
        :type nodes_data: dict
        :param busd: dictionary containing the buses of the energy system
        :type busd: dict
        :param nodes: list of components created before (can be empty)
        :type nodes: list
    """

    def create_source(self, source: pandas.Series, timeseries_args: dict,
                      output=None, variable_costs_list=None) -> None:
        """
            Creates an oemof source with fixed or unfixed timeseries
    
            :param source: Series containing all information for \
                the creation of an oemof source. At least the \
                following key-value-pairs have to be included:
    
                    - label
                    - output
                    - periodical costs
                    - periodical constraint costs
                    - min. investment capacity
                    - max. investment capacity
                    - existing capacity
                    - non-convex investment
                    - fix investment costs
                    - fix investment constraint costs
                    - variable costs
                    - variable constraint costs

            :type source: pandas.Series
            :param timeseries_args: dictionary rather containing the
                                    'fix-attribute' or the 'min-' and
                                    'max-attribute' of a source
            :type timeseries_args: dict
            :param output: defines the oemof output bus
            :type output: Bus
            :param variable_costs_list: list containing components \
                variable costs if they differ from the spreadsheets \
                entries
            :type variable_costs_list: list
        """
        # set non convex bool
        non_convex = True if source["non-convex investment"] == 1 else False
        # set the variable costs / constraint costs
        variable_costs = source["variable costs"] \
            if not variable_costs_list else variable_costs_list[0]
        variable_constraint_costs = source["variable constraint costs"] \
            if not variable_costs_list else variable_costs_list[1]
        # Creates a oemof source and appends it to the nodes_sources
        # (variable of the create_sources-class) list
        self.nodes_sources.append(
            Source(
                label=source["label"],
                outputs={
                    output: Flow(
                        nominal_value=Investment(
                            ep_costs=source["periodical costs"],
                            minimum=source["min. investment capacity"],
                            maximum=source["max. investment capacity"],
                            existing=source["existing capacity"],
                            nonconvex=non_convex,
                            offset=source["fix investment costs"],
                            custom_attributes={
                                "periodical_constraint_costs":
                                source["periodical constraint costs"],
                                "fix_constraint_costs":
                                source["fix investment constraint costs"],
                            }
                        ),
                        **timeseries_args,
                        variable_costs=variable_costs,
                        custom_attributes={"emission_factor":
                                           variable_constraint_costs}
                        
                    )
                },
            )
        )

    def commodity_source(self, source: pandas.Series) -> None:
        """
            Creates an oemof source object with flexible time series
            (no maximum or minimum) with the use of the create_source
            method.
    
            :param source: Series containing all information for the \
                creation of an oemof source. At least the following \
                key-value-pairs have to be included:
                    - 'label'
            :type source: pandas.Series
        """
        # starts the create_source method with the parameters
        # min = 0 and max = 1
        self.create_source(source=source,
                           timeseries_args={"max": 1},
                           output=self.busd[source["output"]])

        # Returns logging info
        logging.info("\t Commodity Source created: " + source["label"])

    def timeseries_source(self, source: pandas.Series) -> None:
        """
            Creates an oemof source object from a pre-defined
            timeseries with the use of the create_source method.
            A distinction is made here between a fixed source, which
            has only one time series for generation, and an unfixed
            source, which is limited by a lower and an upper time
            series.
    
            :param source: Series containing all information for \
                the creation of an oemof source. At least the \
                following key-value-pairs have to be included:
    
                    - label
                    - output
                    - periodical costs
                    - periodical constraint costs
                    - min. investment capacity
                    - max. investment capacity
                    - existing capacity
                    - non-convex investment
                    - fix investment costs
                    - fix investment constraint costs
                    - variable costs
                    - variable constraint costs
                    
            :type source: pandas.Series
        """

        if source["fixed"] == 1:
            # sets the timeseries attribute for a fixed source
            args = {"fix": self.timeseries[source["label"] + ".fix"].tolist()}
        elif source["fixed"] == 0:
            # sets the timeseries attributes for an unfixed source
            args = {
                "min": self.timeseries[source["label"] + ".min"].tolist(),
                "max": self.timeseries[source["label"] + ".max"].tolist(),
            }
        else:
            raise SystemError(source["label"] + " Error in fixed attribute")

        # starts the create_source method with the parameters set before
        self.create_source(source=source,
                           timeseries_args=args,
                           output=self.busd[source["output"]])

        # Returns logging info
        logging.info("\t Timeseries Source created: " + source["label"])

    def create_feedin_source(self, feedin: pandas.Series,
                             source: pandas.Series, output=None,
                             variable_costs=None) -> None:
        """
            In this method, the parameterization of the output flow \
            for sources has been outsourced, since it is not source \
            type dependent.
            
            :param feedin: time series holding the sources relative \
                output capacity
            :type feedin: pandas.Series
            :param source: Series containing all information for \
                the creation of an oemof source. At least the \
                following key-value-pairs have to be included:
                    
                    - fixed
                    - label
                    - output
            :type source: pandas.Series
            :param output: variable that contains the output of the \
                source if it differs from the value entered in the \
                spreadsheet.
            :type output: oemof.solph.Bus
            :param variable_costs: variable which contains the \
                variable output cost of the source if it differs from \
                the value entered in the spreadsheet.
            :type variable_costs: list
        """
        if source["fixed"] == 1:
            # sets the attribute for a fixed pv_source
            args = {"fix": feedin}
        elif source["fixed"] == 0:
            # sets the attributes for an unfixed pv_source
            args = {"max": feedin}
        else:
            raise SystemError(source["label"] + " Error in fixed attribute")
        
        output = self.busd[source["output"]] if output is None else output
        
        # starts the create_source method with the parameters set before
        self.create_source(source=source,
                           timeseries_args=args,
                           output=output,
                           variable_costs_list=variable_costs)
        # returns logging info
        logging.info("\t Source created: " + source["label"])

    def pv_source(self, source: pandas.Series) -> None:
        """
            Creates an oemof photovoltaic source object.
    
            Simulates the yield of a photovoltaic system using feedinlib
            and creates a source object with the yield as time series
            and the use of the create_source method.
    
            :param source: Series containing all information for \
                the creation of an oemof source. At least the \
                following key-value-pairs have to be included:
    
                    - label
                    - fixed
                    - Azimuth
                    - Surface Tilt
                    - Modul Model
                    - Inverter Model
                    - Albedo
                    - Latitude
                    - Longitude
                    
            :type source: pandas.Series
        """
        # reads pv system parameters from parameter dictionary
        # nodes_data
        parameter_set = {
            "azimuth": source["azimuth"],
            "tilt": source["surface tilt"],
            "module_name": source["modul model"],
            "inverter_name": source["inverter model"],
            "albedo": source["albedo"],
            "module_type": "glass_glass",
            "racking_model": "open_rack",
        }

        # sets pv system parameters for pv_module
        pv_module = powerplants.Photovoltaic(**parameter_set)

        # changes names of data columns,
        # so it fits the needs of the feedinlib
        name_dc = {"temperature": "temp_air", "windspeed": "v_wind"}
        self.weather_data.rename(columns=name_dc)

        # calculates time series normed on 1 kW pv peak performance
        feedin = pv_module.feedin(
            weather=self.weather_data,
            location=(source["latitude"], source["longitude"]),
            scaling="peak_power",
        )

        # Replace 'nan' value with 0
        feedin = feedin.fillna(0)
        # Set negative values to zero (requirement for solving the model)
        feedin[feedin < 0] = 0
        # Set values greater 1 to 1 (requirement for solving the model)
        feedin[feedin > 1] = 1

        self.create_feedin_source(feedin=feedin, source=source)

    def windpower_source(self, source: pandas.Series) -> None:
        """
            Creates an oemof windpower source object.
    
            Simulates the yield of a windturbine using feedinlib and
            creates a source object with the yield as time series and
            the use of the create_source method.
    
            :param source: Series containing all information for \
                the creation of an oemof source. At least the \
                following key-value-pairs have to be included:
    
                    - label
                    - fixed
                    - Turbine Model (Windpower ONLY)
                    - Hub Height (Windpower ONLY)
                    
            :type source: pandas.Series
        """

        # set up wind turbine using the wind turbine library.
        # The turbine name must correspond to an entry in the turbine
        # data-base of the feedinlib. Unit of the hub height is m.
        turbine_data = {
            "turbine_type": source["turbine model"],
            "hub_height": float(source["hub height"]),
        }
        # create windturbine
        wind_turbine = WindPowerPlant(**turbine_data)

        weather_df = self.weather_data[["windspeed", "temperature",
                                        "z0", "pressure"]]
        # second row is height of data acquisition in m
        weather_df.columns = [
            ["wind_speed", "temperature", "roughness_length", "pressure"],
            [10, 2, 0, 0]]
        
        # calculate scaled feed-in
        feedin = wind_turbine.feedin(weather=weather_df,
                                     scaling="nominal_power")
        
        self.create_feedin_source(feedin, source)

    def solar_heat_source(self, source: pandas.Series) -> None:
        """
            Creates a solar thermal collector source object.
    
            Calculates the yield of a solar thermal flat plate collector
            or a concentrated solar power collector as time series by
            using oemof.thermal and the create_source method.
    
            The following key-value-pairs have to be included in the
            keyword arguments:
    
            :type source: pandas.Series
            :param source: has to contain the following keyword \
                arguments:
    
                    - input
                    - technology:
                        - solar_thermal_flat_plate or
                        - concentrated_solar_power
                    - Latitude
                    - Longitude
                    - Surface Tilt
                    - Azimuth
                    - Cleanliness
                    - ETA 0
                    - A1
                    - A2
                    - C1
                    - C2
                    - Temperature Inlet
                    - Temperature Difference
                    - Conversion Factor
                    - Peripheral Losses
                    - Electric Consumption

        """

        # import oemof.thermal in order to calculate collector heat output
        from oemof.thermal.solar_thermal_collector import flat_plate_precalc
        from oemof.thermal.concentrating_solar_power import csp_precalc
        import numpy
        
        # get the source label
        label = source["label"]

        # creates an oemof-bus object for solar thermal collector
        col_bus = Bus(label=label + "_bus")
        # adds the bus object to the list of components "nodes"
        self.nodes_sources.append(col_bus)
        self.busd[label + "_bus"] = col_bus

        # import weather data and set datetime index with hourly frequency
        self.weather_data.index.name = "Datum"
        weather_data = self.weather_data.asfreq(
            self.energysystem["temporal resolution"]
        )

        # pre-calculations for flat plate collectors, calculates total
        # irradiance on collector, efficiency and heat output
        if source["technology"] == "solar_thermal_flat_plate":
            precalc_res = flat_plate_precalc(
                lat=source["latitude"],
                long=source["longitude"],
                collector_tilt=source["surface tilt"],
                collector_azimuth=source["azimuth"],
                eta_0=source["ETA 0"],
                a_1=source["A1"],
                a_2=source["A2"],
                temp_collector_inlet=source["temperature inlet"],
                delta_temp_n=source["temperature difference"],
                irradiance_global=(weather_data["ghi"]),
                irradiance_diffuse=(weather_data["dhi"]),
                temp_amb=weather_data["temperature"],
            )
            # set variables collectors_heat and irradiance and conversion
            # from W/sqm to kW/sqm
            irradiance = precalc_res.col_ira / 1000

        # set parameters for precalculations for concentrating solar power
        elif source["technology"] == "concentrated_solar_power":
            # Import Weather Data
            # Since dirhi is not longer part of the SESMGs weather data it
            # is calculated based on
            # https://power.larc.nasa.gov/docs/methodology/energy-fluxes/
            # correction/
            # by subtracting dhi from ghi
            dirhi = weather_data["ghi"] - weather_data["dhi"]
            # precalculation with parameter set, ambient temperature and
            # direct horizontal irradiance. Calculates total irradiance on
            # collector, efficiency and heat output
            precalc_res = csp_precalc(
                lat=source["latitude"],
                long=source["longitude"],
                collector_tilt=source["surface tilt"],
                collector_azimuth=source["azimuth"],
                cleanliness=source["cleanliness"],
                a_1=source["A1"],
                a_2=source["A2"],
                eta_0=source["ETA 0"],
                c_1=source["C1"],
                c_2=source["C2"],
                temp_collector_inlet=source["temperature inlet"],
                temp_collector_outlet=source["temperature inlet"]
                + source["temperature difference"],
                temp_amb=weather_data["temperature"],
                E_dir_hor=dirhi
            )
            # set variables collectors_heat and irradiance and conversion
            # from W/sqm to kW/sqm
            irradiance = precalc_res.collector_irradiance / 1000
        else:
            raise ValueError("Technology chosen not accepted!")
        collectors_heat = precalc_res.eta_c
        
        self.create_feedin_source(feedin=collectors_heat,
                                  source=source,
                                  output=col_bus,
                                  variable_costs=[0, 0])

        self.nodes_sources.append(
            Converter(
                label=label + "_collector",
                inputs={
                    self.busd[label + "_bus"]: Flow(
                        custom_attributes={"emission_factor": 0}),
                    self.busd[source["input"]]: Flow(
                        custom_attributes={"emission_factor": 0}),
                },
                outputs={self.busd[source["output"]]: Flow(
                    variable_costs=source["variable costs"],
                    custom_attributes={"emission_factor":
                                       source["variable constraint costs"]})},
                conversion_factors={
                    self.busd[label + "_bus"]: 1,
                    self.busd[source["input"]]: source["electric consumption"]
                    * (1 - source["peripheral losses"]),
                    self.busd[source["output"]]:
                        1 - source["peripheral losses"],
                },
            )
        )

        # returns logging info
        logging.info(
            "\t Source created: "
            + source["label"]
            + ", Max Heat power output per year and m²: "
            "{:2.2f}".format(numpy.sum(collectors_heat
                                       / source["conversion factor"]))
            + " kWh/(m²a), Irradiance on collector per year and m²: "
            "{:2.2f}".format(numpy.sum(irradiance)) + " kWh/(m²a)"
        )

    def __init__(self, nodes_data: dict, nodes: list, busd: dict) -> None:
        """
            Inits the source class
        """
        # Delete possible residues of a previous run from the class
        # internal list nodes_sources
        self.nodes_sources = []
        # Initialise a class intern copy of the bus dictionary
        self.busd = busd.copy()
        self.energysystem = next(nodes_data["energysystem"].iterrows())[1]
        self.weather_data = nodes_data["weather data"].copy()
        self.timeseries = nodes_data["timeseries"].copy()
        switch_dict = {
            "other": self.commodity_source,
            "photovoltaic": self.pv_source,
            "windpower": self.windpower_source,
            "timeseries": self.timeseries_source,
            "solar_thermal_flat_plate": self.solar_heat_source,
            "concentrated_solar_power": self.solar_heat_source,
        }
        # dataframe of active sources
        sources = nodes_data["sources"].loc[
            nodes_data["sources"]["active"] == 1]
        
        # Create Source from "Sources" Table
        for num, source in sources.iterrows():
            switch_dict.get(source["technology"],
                            "Invalid technology !")(source)

        # appends created sources and other objects to the list of nodes
        for i in range(len(self.nodes_sources)):
            nodes.append(self.nodes_sources[i])
