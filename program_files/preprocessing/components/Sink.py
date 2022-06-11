import logging
from oemof.solph import Investment, Flow, Source, Sink
from datetime import datetime
import pandas as pd
from demandlib import bdew


class Sinks:
    """
        Creates sink objects.

        There are four options for labeling source objects to be
        created:

            - unfixed: a source with flexible time series
            - timeseries: a source with predefined time series
            - SLP: a VDEW standard load profile component
            - richardson: a component with stochastically generated timeseries

        :param nd: dictionary containing parameters of sinks to
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
        :type nd: dict
        :param busd: dictionary containing the buses of the energy system
        :type busd: dict
        :param nodes: list of components created before(can be empty)
        :type nodes: list

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
            Sink(label=de['label'],
                 inputs={self.busd[de['input']]: Flow(**timeseries_args)}))
        for num, insul_type in self.energetic_renovation.iterrows():
            if insul_type["active"]:
                temp = []
                time = 0
                if insul_type["sink"] == de["label"]:
                    for timestep in self.weather_data["temperature"]:
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
                            insul_type["periodical constraint costs"] \
                            * insul_type["area"] \
                            / max(temp)
                        self.energetic_renovation.loc[
                            num, "ep_costs_kW"] = ep_costs
                        self.energetic_renovation.loc[
                            num, "ep_constr_costs_kW"] = ep_constr_costs
                        self.nodes_sinks.append(
                            Source(
                                label="insulation-{}".format(
                                        insul_type["label"]),
                                outputs={
                                    self.busd[de['input']]:
                                        Flow(
                                            investment=Investment(
                                                ep_costs=ep_costs,
                                                periodical_constraint_costs=ep_constr_costs,
                                                constraint2=1,
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

    def timeseries_sink(self, de):
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
            args.update({'min': self.timeseries[de['label'] + '.min'].tolist(),
                         'max': self.timeseries[de['label'] + '.max'].tolist()}
                        )
        elif de['fixed'] == 1:
            # sets the attributes for a fixed time_series sink
            args.update({'fix': self.timeseries[de['label'] + '.fix']})
        # starts the create_sink method with the parameters set before
        self.create_sink(de, args)

        # returns logging info
        logging.info('   ' + 'Sink created: ' + de['label'])

    def slp_sink(self, de: dict):
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
        temp_resolution = self.energysystem['temporal resolution']
        periods = self.energysystem["periods"]
        start_date = str(self.energysystem['start date'])

        # Converting start date into datetime format
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')

        # Create DataFrame
        demand = pd.DataFrame(index=pd.date_range(datetime(
                start_date.year, start_date.month, start_date.day,
                start_date.hour), periods=periods, freq=temp_resolution))

        # creates time series
        if de['load profile'] in heat_slps_commercial \
                or de['load profile'] in heat_slps:
            # sets the parameters of the heat slps
            args = {'temperature': self.weather_data['temperature'],
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
            year = datetime.strptime(str(self.energysystem['start date']),
                                     '%Y-%m-%d %H:%M:%S').year
            # Imports standard load profiles
            e_slp = bdew.ElecSlp(year)
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

    def __init__(self, nd: dict, busd: dict, nodes: list, energetic_renovation):
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
        self.weather_data = nd["weather data"].copy()
        self.timeseries = nd["timeseries"].copy()
        self.energysystem = next(nd['energysystem'].iterrows())[1]
        switch_dict = {"x": self.unfixed_sink,
                       "timeseries": self.timeseries_sink,
                       "slp": self.slp_sink,
                       "richardson": self.richardson_sink}
        # Create sink objects
        for i, de in nd['sinks'].loc[nd["sinks"]["active"] == 1].iterrows():
            slps = \
                ['efh', 'mfh', 'gmf', 'gpd', 'ghd', 'gwa', 'ggb', 'gko', 'gbd',
                 'gba', 'gmk', 'gbh', 'gga', 'gha', 'h0', 'g0', 'g1', 'g2',
                 'g3', 'g4', 'g5', 'g6', 'l0', 'l1', 'l2']

            load_profile = "slp" if de["load profile"] in slps \
                else de["load profile"]
            switch_dict.get(load_profile, "Invalid load profile")(de)

        # appends created sinks on the list of nodes
        for i in range(len(self.nodes_sinks)):
            nodes.append(self.nodes_sinks[i])
        nd["insulation"] = self.energetic_renovation.copy()
