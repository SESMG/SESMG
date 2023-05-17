"""
    Christian Klemm - christian.klemm@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
"""
import logging
from oemof.solph import Investment
from oemof.solph.components import Source, Sink
from oemof.solph.flows import Flow
from datetime import datetime
import pandas
from demandlib import bdew


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

    slps = {
        "heat_slps":
            ["efh",   # single family building
             "mfh"],  # multi family building
        "heat_slps_commercial":
            ["gmf",   # household-like business enterprises
             "gpd",   # paper and printing
             "ghd",   # Total load profile Business/Commerce/Services
             "gwa",   # laundries, dry cleaning
             "ggb",   # horticulture
             "gko",   # Local authorities and credit institutions
             "gbd",   # other operational services
             "gba",   # bakery
             "gmk",   # metal and automotive
             "gbh",   # accommodation
             "gga",   # restaurants
             "gha"],  # retail and wholesale
        "electricity_slps":
            ["h0",   # households
             "g0",   # commercial general
             "g1",   # commercial on weeks 8-18 h
             "g2",   # commercial with strong consumption (evening)
             "g3",   # commercial continuous
             "g4",   # shop/hairdresser
             "g5",   # bakery
             "g6",   # weekend operation
             "l0",   # agriculture general
             "l1",   # agriculture with dairy industry/animal breeding
             "l2"]   # other agriculture
    }

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

    def create_sink(self, sink: pandas.Series, nominal_value=None,
                    load_profile=None, args=None) -> None:
        """
            Creates an oemof sink with fixed or unfixed timeseries.

            :param sink: dictionary containing all information for the \
                creation of an oemof sink. At least the following \
                key-value-pairs have to be included:
                
                     - label
                     - input
    
            :type sink: pandas.Series
            :param nominal_value: Float containing the nominal demand \
                of the sink to be created. Only used if the args \
                parameter remains empty.
            :type nominal_value: float
            :param load_profile: load Profile contains the time series \
                of the sink to be created, this is used for the fixed \
                (fix) or the maximum (unfix) time series depending on \
                the sink type. Only used if the args parameter remains \
                empty.
            :param args: dictionary rather containing the \
                'fix-attribute' or the 'min-' and 'max-attribute' of a \
                sink
            :type args: dict
        """

        if args is None:
            args = {"nominal_value": nominal_value}
            if sink["fixed"] == 1:
                # sets attributes for a fixed richardson sink
                args.update({"fix": load_profile})
            elif sink["fixed"] == 0:
                # sets attributes for an unfixed richardson sink
                args.update({"max": load_profile})
                
        # creates an oemof Sink and appends it to the class intern list
        # of created sinks
        self.nodes_sinks.append(
            Sink(label=sink["label"],
                 inputs={self.busd[sink["input"]]: Flow(**args)})
        )
        
        # create insulation sources to the energy system components
        insulations = self.insulation[self.insulation["active"] == 1]
        for num, ins in insulations.iterrows():
            # if insulation sink == sink under investigation (above)
            if ins["sink"] == sink["label"]:
                ep_costs, ep_constr_costs, temp = \
                    self.calc_insulation_parameter(ins=ins)
                if "existing" in self.insulation and ins["existing"]:
                    # add capacity specific costs to self.insulation
                    self.insulation.loc[num, "ep_costs_kW"] = 0
                    # add capacity specific emissions to self.insulation
                    self.insulation.loc[num, "ep_constr_costs_kW"] = 0
                    maximum = 0
                    existing = max(temp)
                else:
                    # add capacity specific costs to self.insulation
                    self.insulation.loc[num, "ep_costs_kW"] = ep_costs
                    # add capacity specific emissions to self.insulation
                    self.insulation.loc[num, "ep_constr_costs_kW"] = \
                        ep_constr_costs
                    maximum = max(temp)
                    existing = 0
                    
                self.nodes_sinks.append(
                    Source(
                        label="{}-insulation".format(ins["label"]),
                        outputs={
                            self.busd[sink["input"]]: Flow(
                                investment=Investment(
                                    ep_costs=ep_costs,
                                    custom_attributes={
                                        "periodical_constraint_costs":
                                        ep_constr_costs,
                                        "constraint2": 1,
                                        "fix_constraint_costs": 0},
                                    minimum=0,
                                    maximum=maximum,
                                    existing=existing
                                ),
                                custom_attributes={"emission_factor": 0},
                                fix=(args["fix"] / args["fix"].max()),
                            )}))

    def unfixed_sink(self, sink: pandas.Series) -> None:
        """
            Creates a sink object with an unfixed energy input and the
            use of the create_sink method.
    
            :param sink: dictionary containing all information for the \
                creation of an oemof sink. For this function the \
                following key-value-pairs have to be included:
                    
                    - label
                    - nominal value

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
                creation of an oemof sink. At least the following \
                key-value-pairs have to be included:
    
                    - label
                    - nominal value
                    - fixed

            :type sink: pandas.Series
        """
        # sets the nominal value
        args = {"nominal_value": sink["nominal value"]}
        # handling unfixed time series sinks
        if sink["fixed"] == 0:
            # sets the attributes for an unfixed time_series sink
            args.update(
                {
                    "min": self.timeseries[sink["label"] + ".min"].tolist(),
                    "max": self.timeseries[sink["label"] + ".max"].tolist(),
                }
            )
        # handling fixed time series sinks
        elif sink["fixed"] == 1:
            # sets the attributes for a fixed time_series sink
            args.update({"fix": self.timeseries[sink["label"] + ".fix"]})
            
        # starts the create_sink method with the parameters set before
        self.create_sink(sink, args=args)

        # returns logging info
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
            index=pandas.date_range(
                datetime(
                    year=start_date.year,
                    month=start_date.month,
                    day=start_date.day,
                    hour=start_date.hour
                ),
                periods=self.energysystem["periods"],
                freq=temp_resolution,
            )
        )
        
        heat_slps = self.slps["heat_slps_commercial"] + self.slps["heat_slps"]
        # creates time series for heat sinks
        if sink["load profile"] in heat_slps:
            # sets the parameters of the heat slps
            args = {
                "temperature": self.weather_data["temperature"],
                "shlp_type": sink["load profile"],
                "wind_class": sink["wind class"],
                "annual_heat_demand": 1,
                "name": sink["load profile"],
            }
            # handling non commercial buildings
            if sink["load profile"] in self.slps["heat_slps"]:
                # adds the building class which is only necessary for
                # the non commercial slps
                args.update({"building_class": sink["building class"]})
                
            # create the demandlib's data set
            demand[sink["load profile"]] = bdew.HeatBuilding(
                demand.index, **args
            ).get_bdew_profile()
            
        # create time series for electricity sinks
        elif sink["load profile"] in self.slps["electricity_slps"]:
            # Imports standard load profiles
            e_slp = bdew.ElecSlp(year=start_date.year)
            demand = e_slp.get_profile({sink["load profile"]: 1})
            # creates time series based on standard load profiles
            demand = demand.resample(temp_resolution).mean()
            
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
                creation of an oemof sink. At least the following \
                key-value-pairs have to be included:
    
                    - label
                    - fixed
                    - annual demand
                    - occupants

            :type sink: pandas.Series
            
            :raise ValueError: Invalid temporal resolution chosen
        """

        import richardsonpy.classes.occupancy as occ
        import richardsonpy.classes.electric_load as eload

        # Import Weather Data
        # Since dirhi is not longer part of the SESMGs weather data it
        # is calculated based on
        # https://power.larc.nasa.gov/docs/methodology/energy-fluxes/
        # correction/
        # by subtracting dhi from ghi
        ghi = self.weather_data["ghi"].values.flatten()
        dhi = self.weather_data["dhi"].values.flatten()
        dirhi = ghi - dhi

        # Conversion of irradiation from W/m^2 to kW/m^2
        dhi /= 1000
        dirhi /= 1000

        # sets the occupancy rates
        # Workaround, because richardson.py only allows a maximum
        # of 5 occupants
        nb_occ = sink["occupants"] if sink["occupants"] < 5 else 5

        # sets the temporal resolution of the richardson.py time series,
        # depending on the temporal resolution of the entire model (as
        # defined in the input spreadsheet)
        temp_res = {"H": 3600, "h": 3600, "min": 60, "s": 1}
        time_step = temp_res.get(self.energysystem["temporal resolution"])

        #  Generate occupancy object
        #  (necessary as input for electric load gen)
        occ_obj = occ.Occupancy(number_occupants=nb_occ)

        #  Generate stochastic electric power object
        el_load_obj = eload.ElectricLoad(
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
        
        sinks = nodes_data["sinks"].loc[nodes_data["sinks"]["active"] == 1]
        # Create sink objects
        for num, sink in sinks.iterrows():
            
            # switch the load profile to slp if load profile in slps
            if sink["load profile"] in self.slps.values():
                load_profile = "slp"
            else:
                load_profile = sink["load profile"]
            # get the sink types creation method from the switch dict
            switch_dict.get(load_profile, "Invalid load profile")(sink)

        # appends created sinks on the list of nodes
        for index in range(len(self.nodes_sinks)):
            nodes.append(self.nodes_sinks[index])
        nodes_data["insulation"] = self.insulation.copy()
