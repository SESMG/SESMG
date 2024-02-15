"""
    Christian Klemm - christian.klemm@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
"""
import logging
import pandas
from datetime import datetime
from demandlib import bdew
from oemof import solph
from richardsonpy.classes import occupancy, electric_load


class Sinks:
    """
        Within this class the 'nodes_data' given sinks are created.
        Therefore there is a differentiation between four types
        of sink objects to be created:
    
            - unfixed: a sink with flexible time series
            - timeseries: a sink with predefined time series
            - SLP: a VDEW standard load profile component
            - richardson: a component with stochastically generated \
                time series
    
        :param nodes_data: dictionary containing parameters of sinks \
            to be created. The following data have to be provided:
                
                - label
                - sector
                - active
                - fixed
                - input
                - load profile
                - nominal value
                - annual demand
                - occupants (only needed for the Richardson sinks)
                - building class
                - wind class
                
        :type nodes_data: dict
        :param busd: dictionary containing the buses of the energy \
            system
        :type busd: dict
        :param nodes: list of components created before (can be empty)
        :type nodes: list
    """
    # HEAT SLPS
    # efh,  single family building
    # mfh,  multi family building
    # HEAT SLPS COMMERCIAL
    # gmf,  household-like business enterprises
    # gpd,  paper and printing
    # ghd,  Total load profile Business/Commerce/Services
    # gwa,  laundries, dry cleaning
    # ggb,  horticulture
    # gko,  Local authorities and credit institutions
    # gbd,  other operational services
    # gba,  bakery
    # gmk,  metal and automotive
    # gbh,  accommodation
    # gga,  restaurants
    # gha,  retail and wholesale
    # ELECTRICITY SLPS
    # h0,  households
    # g0,  commercial general
    # g1,  commercial on weeks 8-18 h
    # g2,  commercial with strong consumption (evening)
    # g3,  commercial continuous
    # g4,  shop/hairdresser
    # g5,  bakery
    # g6,  weekend operation
    # l0,  agriculture general
    # l1,  agriculture with dairy industry/animal breeding
    # l2   other agriculture

    slps = {
        "heat_slps": ["efh", "mfh"],
        "heat_slps_commercial": ["gmf", "gpd", "ghd", "gwa", "ggb", "gko",
                                 "gbd", "gba", "gmk", "gbh", "gga", "gha"],
        "electricity_slps": ["h0", "g0", "g1", "g2",  "g3", "g4", "g5", "g6",
                             "l0", "l1", "l2"]
    }

    def __init__(self, nodes_data: dict, busd: dict, nodes: list) -> None:
        """
            Inits the sink class.
        """
        # Delete possible residues of a previous run from the class
        # internal list nodes_sinks
        self.nodes_sinks = []
        # Initialise a class intern copy of the bus dictionary
        self.busd = busd.copy()
        self.insulation = nodes_data["insulation"].copy()
        self.weather_data = nodes_data["weather data"].copy()
        self.timeseries = nodes_data["timeseries"].copy()
        self.energysystem = next(nodes_data["energysystem"].iterrows())[1]
        switch_dict = {
            "x": self.unfixed_sink,
            "timeseries": self.timeseries_sink,
            "slp": self.slp_sink,
            "richardson": self.richardson_sink,
        }
    
        # Create sink objects
        for _, sink in nodes_data["sinks"].query("active == 1").iterrows():
        
            # switch the load profile to slp if load profile in slps
            if sink["load profile"] in self.slps.values():
                load_profile = "slp"
            else:
                load_profile = sink["load profile"]
            # get the sink types creation method from the switch dict
            switch_dict.get(load_profile, self.invalid_load_profile)(sink)
    
        # appends created sinks on the list of nodes
        for index in range(len(self.nodes_sinks)):
            nodes.append(self.nodes_sinks[index])

    def invalid_load_profile(self, sink: pandas.Series) -> None:
        raise ValueError(
                f"{sink['load profile']} is an unsupported sink type!")

    def calc_insulation_parameter(self,
                                  ins: pandas.Series) -> (float, float, list):
        """
            Calculation of insulation measures for the considered sink
            
            Temperature difference is calculated according to:
            
            .. math::
            
                \Delta T = T_{\mathrm{indoor}} - T_{\mathrm{outdoor}}

            is only calculated for the time steps in which the \
            temperature falls below the heating limit temperature.
    
            U-value difference is calculated according to:
            
            .. math::
            
                \Delta U = U_{\mathrm{old}} - U_{\mathrm{new}}
            
            Calculation of the capacity that can be saved according to:
            
            .. math::
            
                P = (\Delta U \cdot \Delta T \cdot A) / (1000\mathrm{(W / kW)})
    
            :params: - **ins** (pandas.Series) - considered insulation \
                row
            
            :returns: - **ep_costs** (float) - periodical costs of the \
                            considered insulation
                      - **ep_constr_costs** (float) - periodical \
                            constraint costs of the considered \
                            insulation
                      - **temp** (list) - list containing the capacity \
                            to be saved for each time step
        """
        temp = []
        # Extract the days that have an outdoor temperature below the
        # heating limit temperature.
        heating_degree_steps = self.weather_data[
            self.weather_data["temperature"] <= ins["heat limit temperature"]]
        
        # calculate insulation capacity per time step
        for time_step in heating_degree_steps["temperature"]:
            # calculate the difference between the outdoor and indoor
            # temperature
            temp_diff = ins["temperature indoor"] - float(time_step)
            # calculate the u-value potential
            u_value_diff = ins["U-value old"] - ins["U-value new"]
            # Calculation of the capacity that can be saved.
            temp.append(temp_diff * u_value_diff * ins["area"] / 1000)

        # check if there is an insulation potential
        if len(temp) != 0:
            # calculate capacity specific costs
            ep_costs = ins["periodical costs"] * ins["area"] / max(temp)
            # calculate capacity specific emissions
            ep_constr_costs = (
                ins["periodical constraint costs"] * ins["area"] / max(temp)
            )
            return ep_costs, ep_constr_costs, temp
        else:
            return 0, 0, [0]

    def create_insulation_source(self, label: str, bus: str, args: dict
                                 ) -> None:
        """
            Create insulation sources for the considered sink "label".
    
            :param label: Label of the considered sink.
            :type label: str
            :param bus: Bus associated with the sink (input).
            :type bus: str
            :param args: Dictionary containing additional arguments.
            :type args: dict
        """
    
        # Filter active insulation for the given label
        active_ins = self.insulation.query("active == 1")
        filtered_active_ins = active_ins.query("sink == '{}'".format(label))
    
        # Iterate over the filtered active insulation
        for num, ins in filtered_active_ins.iterrows():
            # Calculate parameters for the insulation
            ep_costs, ep_constr_costs, temp = self.calc_insulation_parameter(
                ins=ins)
        
            # Check if insulation is existing
            if "existing" in self.insulation and ins["existing"]:
                ep_costs = 0
                ep_constr_costs = 0
                maximum = 0
                existing = max(temp)
            else:
                maximum = max(temp)
                existing = 0
        
            # Update insulation data with capacity-specific values
            self.insulation.loc[num, "ep_costs_kW"] = ep_costs
            self.insulation.loc[num, "ep_constr_costs_kW"] = ep_constr_costs
        
            # Create investment object for the insulation
            investment = solph.Investment(
                ep_costs=ep_costs,
                custom_attributes={
                    "periodical_constraint_costs": ep_constr_costs,
                    "constraint2": 1,
                    "fix_constraint_costs": 0
                },
                minimum=0,
                maximum=maximum,
                existing=existing
            )
        
            # Add a Source node to the list of energy consumers
            self.nodes_sinks.append(
                solph.components.Source(
                    label="{}-insulation".format(ins["label"]),
                    outputs={
                        self.busd[bus]: solph.flows.Flow(
                            investment=investment,
                            custom_attributes={"emission_factor": 0},
                            fix=(args["fix"] / args["fix"].max()),
                        )}))

    def create_sink(self, sink: pandas.Series, nominal_value=None,
                    load_profile=None, args=None) -> None:
        """
            Creates an oemof sink with fixed or unfixed timeseries.

            :param sink: pandas.Series containing information for the \
                creation of an oemof sink.
            :type sink: pandas.Series
            :param nominal_value: Float containing the nominal demand \
                of the sink to be created. Only used if the args \
                parameter remains empty.
            :type nominal_value: float
            :param load_profile: load Profile contains the time series \
                of the sink to be created. This is used for the fixed \
                (fix) or the maximum (unfix) time series depending on \
                the sink type. Only used if the args parameter remains \
                empty.
            :type load_profile: pandas.Series
            :param args: dictionary rather containing the \
                'fix-attribute' or the 'min-' and 'max-attribute' of a \
                sink
            :type args: dict
        """

        args = args or {"nominal_value": nominal_value}
        
        key = "fix" if sink["fixed"] == 1 else "max"
        args.update(**({key: load_profile} if key not in args else {}))

        # Create an oemof Sink and append it to the class internal list
        # of created sinks
        self.nodes_sinks.append(
            solph.components.Sink(
                label=sink["label"],
                inputs={self.busd[sink["input"]]: solph.flows.Flow(**args)})
        )
        
        # Create the corresponding insulation measures for the sink
        self.create_insulation_source(label=sink["label"],
                                      bus=sink["input"],
                                      args=args)
        
    def unfixed_sink(self, sink: pandas.Series) -> None:
        """
            Creates a sink object with an unfixed energy input and the
            use of the create_sink method.
    
            :param sink: dictionary containing all information for the \
                creation of an oemof sink.
            :type sink: pandas.Series
        """
        # starts the create_sink method with the parameters set before
        self.create_sink(sink, args={"nominal_value": sink["nominal value"]})
        # returns logging info
        logging.info("\t Sink created: " + sink["label"])

    def timeseries_sink(self, sink: pandas.Series) -> None:
        """
            Creates a sink object with a fixed input. The input must be
            given as a time series in the model definition file.
            In this context the method uses the create_sink method.
            
            When creating a time series sink, a distinction is made
            between unfixed and fixed operation in the case of unfixed
            operation, the design range must be limited by a lower and
            upper limiting time series (.min and .max) in the case of a
            fixed time series sink, only one load profile (.fix) is
            required.
    
            :param sink: dictionary containing all information for the \
                creation of an oemof sink
            :type sink: pandas.Series
        """
        # Set the nominal value and make the distinction between unfixed
        # sink (sink["fixed"] == 0) and fixed sink (sink["fixed"] == 1)
        args = {
            "nominal_value": sink["nominal value"],
            **(
                {
                    "min": self.timeseries[sink["label"] + ".min"].tolist(),
                    "max": self.timeseries[sink["label"] + ".max"].tolist(),
                }
                if sink["fixed"] == 0 else
                {
                    "fix": self.timeseries[sink["label"] + ".fix"]
                })}

        # Create the sink using the create_sink method
        self.create_sink(sink, args=args)

        # Log the creation of the sink
        logging.info("\t Sink created: " + sink["label"])

    def slp_sink(self, sink: pandas.Series) -> None:
        """
            Creates a sink with a residential or commercial
            SLP time series.
    
            Creates a sink with inputs according to VDEW standard
            load profiles, using oemof's demandlib.
            Used for the modelling of residential or commercial
            electricity demand.
            In this context the method uses the create_sink method.
    
            :param sink: dictionary containing all information for the \
                creation of an oemof sink. At least the following \
                key-value-pairs have to be included:
    
                    - label
                    - load profile
                    - annual demand
                    - building class
                    - wind class

            :type sink: pandas.Series
        """
        
        # Importing timesystem parameters from the model definition
        temp_resolution = self.energysystem["temporal resolution"]

        # Converting start date into datetime format
        start_date = datetime.strptime(
            str(self.energysystem["start date"]), "%Y-%m-%d %H:%M:%S"
        )

        # Create DataFrame
        demand = pandas.DataFrame(
            index=pandas.date_range(start=start_date,
                                    periods=self.energysystem["periods"],
                                    freq=temp_resolution)
        )
        
        heat_slps = self.slps["heat_slps_commercial"] + self.slps["heat_slps"]
        # creates time series for heat sinks
        if sink["load profile"] in heat_slps:
    
            # create the demandlib's data set
            # using the parameters of the heat slps
            # **() and the building class which is only necessary for
            # the non commercial slps
            demand[sink["load profile"]] = bdew.HeatBuilding(
                df_index=demand.index,
                **{
                    "temperature": self.weather_data["temperature"],
                    "shlp_type": sink["load profile"],
                    "wind_class": sink["wind class"],
                    "annual_heat_demand": 1,
                    "name": sink["load profile"],
                    **({"building_class": sink["building class"]}
                        if sink["load profile"] in self.slps["heat_slps"]
                       else {})
                }).get_bdew_profile()
            
        # create time series for electricity sinks
        elif sink["load profile"] in self.slps["electricity_slps"]:
            
            # Imports standard load profiles
            e_slp = bdew.ElecSlp(year=start_date.year)
            
            # get the electricity demand timeseries and resample it on
            # the user chosen temporal resolution
            demand = e_slp.get_profile(
                ann_el_demand_per_sector={sink["load profile"]: 1}
            ).resample(temp_resolution).mean()
            
        else:
            self.invalid_load_profile(sink)
            
        # starts the create_sink method with the parameters set before
        self.create_sink(
            sink,
            nominal_value=sink["annual demand"],
            load_profile=demand[sink["load profile"]],
        )
        
        # returns logging info
        logging.info("\t Sink created: " + sink["label"])

    def richardson_sink(self, sink: pandas.Series) -> None:
        """
            Creates a sink with stochastically generated input, using
            richardson.py. Used for the modelling of residential
            electricity demands. In this context the method uses the
            create_sink method.
    
            :param sink: dictionary containing all information for the \
                creation of an oemof sink.
            :type sink: pandas.Series
        """

        # Import Weather Data
        # Since dirhi is not longer part of the SESMGs weather data it
        # is calculated based on
        # https://power.larc.nasa.gov/docs/methodology/energy-fluxes/
        # correction by subtracting dhi from ghi
        # additionally all iradiations are conversed from W/sqm to
        # kW/sqm
        ghi = (self.weather_data["ghi"].values.flatten()) / 1000
        dhi = (self.weather_data["dhi"].values.flatten()) / 1000
        dirhi = ghi - dhi

        # sets the occupancy rates
        # Workaround, because richardson.py only allows a maximum
        # of 5 occupants
        nb_occ = min(sink["occupants"], 5)

        # sets the temporal resolution of the richardson.py time series,
        # depending on the temporal resolution of the entire model (as
        # defined in the input spreadsheet)
        temp_res = {"H": 3600, "h": 3600, "min": 60, "s": 1}
        time_step = temp_res.get(self.energysystem["temporal resolution"])

        #  Generate occupancy object
        #  (necessary as input for electric load gen)
        occ_obj = occupancy.Occupancy(number_occupants=nb_occ)

        #  Generate stochastic electric power object
        el_load_obj = electric_load.ElectricLoad(
            occ_profile=occ_obj.occupancy,
            total_nb_occ=nb_occ,
            q_direct=dirhi,
            q_diffuse=dhi,
            timestep=time_step,
        )

        # creates richardson.py time series
        load_profile = el_load_obj.loadcurve
        richardson_demand = sum(load_profile) * time_step / (3600 * 1000)

        # Disables the stochastic simulation of the total yearly demand
        # by scaling the generated time series using the total energy
        # demand of the sink generated in the spreadsheet
        demand_ratio = sink["annual demand"] / richardson_demand

        # starts the create_sink method with the parameters set before
        self.create_sink(
            sink, load_profile=load_profile, nominal_value=0.001 * demand_ratio
        )
        
        # returns logging info
        logging.info("\t Sink created: " + sink["label"])
