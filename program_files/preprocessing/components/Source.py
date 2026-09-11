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
import pvlib


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

    def infer_cec_params(self, source: pandas.Series) -> pandas.Series:
        """
            Calculates CEC 6-parameter set from datasheet specifications.

            Uses pvlib.ivtools.sdm.fit_cec_sam() (Dobos 2012) to estimate
            parameters for the single diode model. Requires NREL-PySAM
            to be installed.

            Note on Units:
                - alpha_sc: Must be [A/°C]. If datasheet gives [%/°C],
                  convert via: alpha_sc_% / 100 * i_sc
                - beta_voc: Must be [V/°C]. If datasheet gives [%/°C],
                  convert via: beta_voc_% / 100 * v_oc
                - gamma_pmp: Remains [%/°C] (e.g. -0.35), no conversion needed.

            :param source: Series containing datasheet values:
                - celltype: e.g., 'monoSi'
                - v_mp: Voltage at maximum power point [V]
                - i_mp: Current at maximum power point [A]
                - v_oc: Open circuit voltage [V]
                - i_sc: Short circuit current [A]
                - alpha_sc: Temp. coefficient of i_sc [A/°C]
                - beta_voc: Temp. coefficient of v_oc [V/°C]
                - gamma_pmp: Temp. coefficient of p_mp [%/°C]
                - cells_in_series: Number of cells in series
                - STC: Nominal power at STC [W]

            :type source: pandas.Series

            :return: Series with parameters for PVSystem/ModelChain
            :rtype: pandas.Series
        """

        # Read parameters from source series
        celltype = str(source["celltype"])
        v_mp = float(source["v mp"])
        i_mp = float(source["i mp"])
        v_oc = float(source["v oc"])
        i_sc = float(source["i sc"])
        # Ensure correct units for temperature coefficients
        # alpha_sc: [A/°C], beta_voc: [V/°C], gamma_pmp: [%/°C]
        alpha_sc = float(source["alpha sc"])
        beta_voc = float(source["beta voc"])
        gamma_pmp = float(source["gamma pmp"])
        n_cells = int(source["cells in series"])

        # Estimate the CEC parameters using the SAM fitting tool
        (I_L_ref, I_o_ref, R_s,
         R_sh_ref, a_ref, Adjust) = pvlib.ivtools.sdm.fit_cec_sam(
            celltype=celltype,
            v_mp=v_mp,
            i_mp=i_mp,
            v_oc=v_oc,
            i_sc=i_sc,
            alpha_sc=alpha_sc,
            beta_voc=beta_voc,
            gamma_pmp=gamma_pmp,
            cells_in_series=n_cells,
        )

        p_stc = float(source["power stc"])

        results = {
            "celltype": celltype,
            "alpha_sc": alpha_sc,
            "beta_voc": beta_voc,
            "a_ref": a_ref,
            "I_L_ref": I_L_ref,
            "I_o_ref": I_o_ref,
            "R_s": R_s,
            "R_sh_ref": R_sh_ref,
            "Adjust": Adjust,
            "STC": p_stc,
            "gamma_pdc": gamma_pmp / 100,
            "gamma_r": gamma_pmp,
        }

        return pandas.Series(results)

    def change_inverter_limits(self, inv_params: pandas.Series, p_stc: float, dc_ac_ratio: float):
        """
            Changes inverter simulation limits to focus solely on conversion efficiency.

            Scales the inverter's capacity based on the DC system size and DC/AC ratio,
            and removes lower operational thresholds to prevent artificial clipping or shutdowns.

            This normalization is critical to allow arbitrary inverter models to be paired
            with any DC system size (e.g., simulating a single 400W module). Without removing
            thresholds like Pso, large commercial inverters would never start operating in a
            small-scale or single-module simulation because their physical startup thresholds
            often require several kilowatts.

            :param inv_params: Series containing inverter parameters.
            :param p_stc: DC power at STC (Standard Test Conditions) in Watts.
            :param dc_ac_ratio: Scaling factor for AC/DC power ratio.
            :type inv_params: pandas.Series
            :type p_stc: float
            :type dc_ac_ratio: float
            :return: Modified inverter parameters.
            :rtype: pandas.Series
        """

        # Define AC power limit based on DC size and desired ratio
        p_limit = p_stc / dc_ac_ratio

        # Set all lower operational and startup thresholds to 0 to ensure continuous operation.
        # Without this, a large commercial inverter would never start up in a small-scale
        # simulation (e.g., a single 400W module could never cross a multi-kW 'Pso' threshold).
        zero_keys = ['Mppt_low', 'MPPTLow', 'Vmin', 'Pso']
        inv_params.loc[inv_params.index.intersection(zero_keys)] = 0

        # Scale rated capacity parameters to p_limit to prevent artificial clipping
        limit_keys = ['Paco', 'Pdco', 'Pacmax', 'Pnom', 'pdc0']
        inv_params.loc[inv_params.index.intersection(limit_keys)] = p_limit

        return inv_params


    def pv_source(self, source: pandas.Series) -> None:
        """
            Creates an oemof photovoltaic source object.

            Simulates the yield of a photovoltaic system using pvlib
            and creates a source object with the yield as time series
            and the use of the create_source method. Supports both
            database-lookup and datasheet-inference for module parameters.

            :param source: Series containing all information for \
                the creation of an oemof source. At least the \
                following key-value-pairs have to be included:

                    - label
                    - fixed
                    - technology: 'photovoltaic' or 'photovoltaic_datasheet'
                    - azimuth
                    - surface tilt
                    - modul model
                    - albedo
                    - latitude
                    - longitude
                    - altitude
                    - inverter_power
                    - inverter_eta
                    
            :type source: pandas.Series
        """
        from pvlib.location import Location
        from pvlib.pvsystem import PVSystem
        from pvlib.modelchain import ModelChain

        # Adjust weather data column names to fit pvlib requirements
        name_dc = {"temperature": "temp_air", "windspeed": "v_wind"}
        self.weather_data.rename(columns=name_dc)

        # Handle different ways of defining module parameters
        pv_module_name = source["modul model"]
        dc_ac_ratio = max(source["dc ac ratio"], 1.0)

        # Map module database names to their corresponding DC model types
        module_dbs = {
            'CECMod': 'cec',
            'SandiaMod': 'sapm'
        }

        module_parameters = None
        dc_model = None

        # Search for the module model across available SAM databases
        for db_name, model_type in module_dbs.items():
            pv_db = pvlib.pvsystem.retrieve_sam(db_name)
            if pv_module_name in pv_db.columns:
                module_parameters = pv_db[pv_module_name]
                dc_model = model_type
                break

        # Extract or calculate STC power based on the selected database/model
        if dc_model == 'cec':
            p_stc = module_parameters["STC"]
        elif dc_model == 'sapm':
            p_stc = module_parameters['Impo'] * module_parameters['Vmpo']
        else:
            # Fallback: Infer CEC parameters from custom datasheet values
            module_parameters = self.infer_cec_params(source)
            p_stc = module_parameters["STC"]
            dc_model = 'cec'

        # Define site location based on geographical coordinates
        location = Location(
            latitude=source["latitude"],
            longitude=source["longitude"],
            altitude=source["altitude"],
        )

        # Handle inverter parameter definition
        inverter_model_name = source["inverter model"]

        # Map database names to their corresponding AC model types
        inverter_dbs = {
            'CECInverter': 'sandia',
            'SandiaInverter': 'sandia',
            'ADRInverter': 'adr'
        }

        inverter_parameters = None
        ac_model = None

        # Search for the inverter model across available databases
        for db_name, model_type in inverter_dbs.items():
            inv_db = pvlib.pvsystem.retrieve_sam(db_name)
            if inverter_model_name in inv_db.columns:
                inverter_parameters = inv_db[inverter_model_name]
                ac_model = model_type
                break

        # Fallback: Create simplified inverter parameters if not found in any database
        if inverter_parameters is None:
            inverter_parameters = pandas.Series({
                "pdc0": p_stc,
                "eta_inv_nom": source["inverter eta"],
            })
            ac_model = 'pvwatts'

        # change capacity and operational limits to prevent unintended simulation clipping
        inverter_parameters = self.change_inverter_limits(inverter_parameters, p_stc, dc_ac_ratio)

        # Set up PVSystem with module and inverter configuration
        system = PVSystem(
            surface_tilt                    = source["surface tilt"],
            surface_azimuth                 = source["azimuth"],
            albedo                          = source["albedo"],
            module_parameters               = module_parameters,
            inverter_parameters             = inverter_parameters,
            temperature_model_parameters    = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_polymer']
        )

        # Configure the ModelChain for simulation
        mc = ModelChain(
            system                  = system,
            location                = location,
            aoi_model               = 'physical',
            spectral_model          = "no_loss",
            ac_model                = ac_model,
            dc_model                = dc_model,
            clearsky_model          = 'ineichen',
            transposition_model     = 'haydavies',
            solar_position_method   = 'nrel_numpy',
            airmass_model           = 'kastenyoung1989',
            temperature_model       = None,
            dc_ohmic_model          = 'no_loss',
            losses_model            = 'no_loss'
        )

        # Run the simulation based on provided weather data
        mc.run_model(self.weather_data)

        # Extract AC and DC power results and handle potential dataframe structures
        ac_power = mc.results.ac
        dc_power = mc.results.dc

        if isinstance(ac_power, pandas.DataFrame):
            ac_power = ac_power.get('p_mp', ac_power.iloc[:, 0])
        if isinstance(dc_power, pandas.DataFrame):
            dc_power = dc_power.get('p_mp', dc_power.iloc[:, 0])

        # Calculate relative feed-in (normalized to STC power)
        feedin = (ac_power.clip(upper=dc_power) / p_stc).fillna(0).clip(lower=0)
        # Finalize the oemof source creation
        self.create_feedin_source(feedin=feedin, source=source)

    def windpower_source(self, source: pandas.Series) -> None:
        """
            Creates an oemof windpower source object.

            Simulates the yield of a windturbine using windpowerlib and
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
        from windpowerlib import WindTurbine, ModelChain

        # Get turbine specifications from the source data
        turbine_data = {
            "turbine_type": source["turbine model"],
            "hub_height": float(source["hub height"])
        }
        turbine_name = turbine_data["turbine_type"]

        wind_turbine = WindTurbine(**turbine_data)

        # Get nominal power automatically from the database (returned in Watts)
        nominal_power = wind_turbine.nominal_power

        # check if the turbine exists in the database by verifying nominal_power
        if nominal_power is None:
            raise ValueError(
                f"The turbine '{turbine_name}' was not found in the windpowerlib database!"
            )

        # Prepare weather data and set up MultiIndex columns for windpowerlib requirements
        weather_df = self.weather_data[["windspeed", "temperature",
                                        "z0", "pressure"]]
        # second row is height of data acquisition in m
        weather_df.columns = [
            ["wind_speed", "temperature", "roughness_length", "pressure"],
            [10, 2, 0, 0]]

        # Calculate power output using the windpowerlib ModelChain approach
        mc = ModelChain(wind_turbine, power_output_model="power_curve")
        mc.run_model(weather_df)

        power_output = mc.power_output

        # Scale feed-in time series to a normalized value between 0 and 1
        if nominal_power and nominal_power > 0:
            feedin = power_output / nominal_power
        else:
            raise ValueError(
                f"Nominal power for '{turbine_name}' is unknown or 0. Scaling failed."
            )

        # Create the oemof source component with the scaled time series
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

        # set collectors_heat from W/sqm to kW/sqm
        collectors_heat = precalc_res.collectors_heat / 1000
        # multiply collectors_heat with conversion factor so that it has no dimension
        # and can be used to create oemof source
        collectors_heat = collectors_heat * source["conversion factor"]

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
                },
                outputs={self.busd[source["output"]]: Flow(
                    variable_costs=source["variable costs"],
                    custom_attributes={"emission_factor":
                                       source["variable constraint costs"]})},
                conversion_factors={
                    self.busd[label + "_bus"]: 1,
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
            "photovoltaic_datasheet": self.pv_source,
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
