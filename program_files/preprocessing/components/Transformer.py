from oemof.solph import Flow, Investment, Transformer, Source, Bus
from oemof.solph.components import GenericCHP
import logging
import numpy
import pandas as pd
import os


class Transformers:
    """
    Creates a transformer object.
    Creates transformers objects as defined in 'nodes_data' and adds
    them to the list of components 'nodes'.

    :param nd: dictionary containing data from excel scenario
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
    :type nd: dict
    :param busd: dictionary containing the buses of the energy system
    :type busd: dict
    :param nodes: list of components created before(can be empty)
    :type nodes: list

    Christian Klemm - christian.klemm@fh-muenster.de
    """

    # intern variables
    nodes_transformer = []
    busd = None

    def get_primary_output_data(self, tf):
        """ """
        return {
            "outputs": {
                self.busd[tf["output"]]: Flow(
                    variable_costs=tf["variable output costs"],
                    emission_factor=tf["variable output constraint costs"],
                    investment=Investment(
                        ep_costs=tf["periodical costs"],
                        minimum=tf["min. investment capacity"],
                        maximum=tf["max. investment capacity"],
                        periodical_constraint_costs=tf["periodical constraint costs"],
                        existing=tf["existing capacity"],
                        nonconvex=True if tf["non-convex investment"] == 1 else False,
                        offset=tf["fix investment costs"],
                        fix_constraint_costs=tf["fix investment constraint costs"],
                    ),
                )
            }
        }

    def create_transformer(self, tf, inputs, conversion_factors, outputs):
        """TODO Docstring missing"""
        self.nodes_transformer.append(
            Transformer(label=tf["label"], **inputs, **outputs, **conversion_factors)
        )
        logging.info("\t Transformer created: " + tf["label"])

    def generic_transformer(self, tf: pd.Series):
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
        outputs = self.get_primary_output_data(tf)
        conversion_factors = {self.busd[tf["output"]]: tf["efficiency"]}
        # Defines Capacity values for the second transformer output
        if tf["output2"] not in ["None", "none", 0]:
            existing_capacity2 = (
                float(tf["efficiency2"]) / float(tf["efficiency"])
            ) * float(tf["existing capacity"])
            minimum_capacity2 = (
                float(tf["efficiency2"]) / float(tf["efficiency"])
            ) * float(tf["min. investment capacity"])
            maximum_capacity2 = (
                float(tf["efficiency2"]) / float(tf["efficiency"])
            ) * float(tf["max. investment capacity"])
            # Creates transformer object and adds it to the list of
            # components
            outputs["outputs"].update(
                {
                    self.busd[tf["output2"]]: Flow(
                        variable_costs=tf["variable output costs 2"],
                        emission_factor=tf["variable output constraint costs 2"],
                        investment=Investment(
                            existing=existing_capacity2,
                            minimum=minimum_capacity2,
                            maximum=maximum_capacity2,
                            periodical_constraint_costs=0,
                            fix_constraint_costs=0,
                        ),
                    )
                }
            )
            conversion_factors.update({self.busd[tf["output2"]]: tf["efficiency2"]})
        # outputs = {"outputs": outputs}

        conversion_factors = {"conversion_factors": conversion_factors}
        inputs = {
            "inputs": {
                self.busd[tf["input"]]: Flow(
                    variable_costs=tf["variable input costs"],
                    emission_factor=tf["variable input constraint costs"],
                )
            }
        }
        self.create_transformer(tf, inputs, outputs, conversion_factors)

    def create_abs_comp_bus(self, tf: pd.Series):
        """
        create absorption chiller and compression heat transformer's
        intern bus

        :param tf: transformer specific data
        :type tf: pd.Series
        :return: - **temp**(str) - mode definition
        """
        # creates one oemof-bus object for compression heat transformers
        # depending on mode of operation
        if tf["mode"] == "heat_pump":
            temp = "_low_temp"
        elif tf["mode"] == "chiller":
            temp = "_high_temp"
        else:
            raise ValueError("Mode of " + tf["label"] + "contains a typo")
        bus = Bus(label=tf["label"] + temp + "_bus")

        # adds the bus object to the list of components "nodes"
        self.nodes_transformer.append(bus)
        self.busd[tf["label"] + temp + "_bus"] = bus

        # returns logging info
        logging.info("\t Bus created: " + tf["label"] + temp + "_bus")

        return temp

    def compression_heat_transformer(self, tf: pd.Series):
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
        :type tf: pd.Series

        :raise SystemError: chosen heat source not defined

        Janik Budde - Janik.Budde@fh-muenster.de
        Yannick Wittor - yw090223@fh-muenster.de
        """

        # import oemof.thermal in order to calculate the cop
        import oemof.thermal.compression_heatpumps_and_chillers as cmpr_hp_chiller

        # create transformer intern bus and determine operational mode
        temp = self.create_abs_comp_bus(tf)

        # dictionary containing the
        # 1. heat source specific labels,
        # 2. capacity calculation,
        # 3. heat_source_temperature definition
        switch_dict = {
            "Ground": [
                tf["label"] + temp + "_ground_source",
                # TODO Formel lesbar einfügen?
                tf["area"]
                * (
                    tf["length of the geoth. probe"]
                    * tf["heat extraction"]
                    / (tf["min. borehole area"] if tf["min. borehole area"] != 0 else 1)
                ),
                self.weather_data["ground_temp"],
            ],
            "GroundWater": [
                tf["label"] + temp + "_groundwater_source",
                float("+inf"),
                self.weather_data["groundwater_temp"],
            ],
            "Air": [
                tf["label"] + temp + "_air_source",
                float("+inf"),
                self.weather_data["temperature"],
            ],
            "Water": [
                tf["label"] + temp + "_water_source",
                float("+inf"),
                self.weather_data["water_temp"],
            ],
        }
        # differentiation between heat sources under consideration of mode
        # of operation
        transformer_label = list(
            switch_dict.get(
                tf["heat source"], tf["label"] + " Error in heat source attribute"
            )
        )[0]

        heatsource_cap = list(
            switch_dict.get(
                tf["heat source"], tf["label"] + " Error in heat source attribute"
            )
        )[1]

        # Creates heat source for transformer. The heat source costs are
        # considered by the transformer.
        self.nodes_transformer.append(
            Source(
                label=transformer_label,
                outputs={
                    self.busd[tf["label"] + temp + "_bus"]: Flow(
                        investment=Investment(
                            maximum=heatsource_cap,
                            periodical_constraint_costs=0,
                            fix_constraint_costs=0,
                        ),
                        emission_factor=0,
                    )
                },
            )
        )

        # Returns logging info
        logging.info("\t Heat Source created: " + tf["label"] + temp + "_source")

        # set temp_high and temp_low and icing considering different
        # heat sources and the mode of operation
        temp_low = list(
            switch_dict.get(
                tf["heat source"], tf["label"] + " Error in heat source attribute"
            )
        )[2]
        temp_high = temp_low.copy()
        if tf["heat source"] == "Air":
            temp_low_value = tf["temperature low"]
            # low temperature as formula to avoid division by zero error
            for index, value in enumerate(temp_high):
                if value == temp_low_value:
                    temp_high[index] = temp_low_value + 0.1

        if tf["mode"] == "heat_pump":
            temp_threshold_icing = tf["temp. threshold icing"]
            factor_icing = tf["factor icing"]
            temp_high = [tf["temperature high"]]
        elif tf["mode"] == "chiller":
            # variable "icing" is not important in cooling mode
            temp_threshold_icing = None
            factor_icing = None
            temp_low = [tf["temperature low"]]
        else:
            raise ValueError("Mode of " + tf["label"] + "contains a typo")
        # calculation of COPs with set parameters
        cops_hp = cmpr_hp_chiller.calc_cops(
            temp_high=temp_high,
            temp_low=temp_low,
            quality_grade=tf["quality grade"],
            temp_threshold_icing=temp_threshold_icing,
            factor_icing=factor_icing,
            mode=tf["mode"],
        )
        logging.info(
            "\t "
            + tf["label"]
            + ", Average Coefficient of Performance (COP): {:2.2f}".format(
                numpy.mean(cops_hp)
            )
        )

        # transformer inputs parameter
        inputs = {
            "inputs": {
                self.busd[tf["input"]]: Flow(
                    variable_costs=tf["variable input costs"],
                    emission_factor=tf["variable input constraint costs"],
                ),
                self.busd[tf["label"] + temp + "_bus"]: Flow(emission_factor=0),
            }
        }
        outputs = self.get_primary_output_data(tf)
        # transformer conversion factor parameter
        conversion_factors = {
            "conversion_factors": {
                self.busd[tf["label"] + temp + "_bus"]: [
                    ((cop - 1) / cop) / tf["efficiency"] for cop in cops_hp
                ],
                self.busd[tf["input"]]: [1 / cop for cop in cops_hp],
            }
        }
        self.create_transformer(
            tf, inputs=inputs, outputs=outputs, conversion_factors=conversion_factors
        )

    def genericchp_transformer(self, tf: pd.Series):
        """
        TODO column names - check completition
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

        Christian Klemm - christian.klemm@fh-muenster.de
        """
        # counts the number of periods within the given datetime index
        # and saves it as variable
        # (number of periods is required for creating generic chp transformers)
        # Importing timesystem parameters from the scenario
        periods = int(self.energysystem["periods"])
        # creates genericCHP transformer object and adds it to the
        # list of components
        self.nodes_transformer.append(
            GenericCHP(
                label=tf["label"],
                fuel_input={
                    self.busd[tf["input"]]: Flow(
                        H_L_FG_share_max=[
                            tf["share of flue gas loss at max heat extraction"]
                            for p in range(0, periods)
                        ],
                        H_L_FG_share_min=[
                            tf["share of flue gas loss at min heat extraction"]
                            for p in range(0, periods)
                        ],
                        variable_costs=tf["variable input costs"],
                        emission_factor=tf["variable input constraint costs"],
                    )
                },
                electrical_output={
                    self.busd[tf["output"]]: Flow(
                        investment=Investment(
                            ep_costs=tf["periodical costs"],
                            periodical_constraint_costs=tf[
                                "periodical constraint costs"
                            ],
                            minimum=tf["min. investment capacity"],
                            maximum=tf["max. investment capacity"],
                            existing=tf["existing capacity"],
                            nonconvex=True
                            if tf["non-convex investment"] == 1
                            else False,
                            offset=tf["fix investment costs"],
                            fix_constraint_costs=tf["fix investment constraint costs"],
                        ),
                        P_max_woDH=[
                            tf["max. electric power without district heating"]
                            for p in range(0, periods)
                        ],
                        P_min_woDH=[
                            tf["min. electric power without district heating"]
                            for p in range(0, periods)
                        ],
                        Eta_el_max_woDH=[
                            tf["el. eff. at max. fuel flow w/o distr. " "heating"]
                            for p in range(0, periods)
                        ],
                        Eta_el_min_woDH=[
                            tf["el. eff. at min. fuel flow w/o distr. " "heating"]
                            for p in range(0, periods)
                        ],
                        variable_costs=tf["variable output costs"],
                        emission_factor=tf["variable output constraint costs"],
                    )
                },
                heat_output={
                    self.busd[tf["output2"]]: Flow(
                        Q_CW_min=[
                            tf["minimal therm. condenser load to cooling water"]
                            for p in range(0, periods)
                        ],
                        variable_costs=tf["variable output costs 2"],
                        emission_factor=tf["variable output constraint costs 2"],
                    )
                },
                Beta=[tf["power loss index"] for p in range(0, periods)],
                back_pressure=True if tf["back pressure"] == 1 else False,
            )
        )

        # returns logging info
        logging.info("\t Transformer created: " + tf["label"])

    def absorption_heat_transformer(self, tf: pd.Series):
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

        Yannick Wittor - yw090223@fh-muenster.de
        """
        # import oemof.thermal in order to calculate COP
        import oemof.thermal.absorption_heatpumps_and_chillers as abs_hp_chiller
        import numpy as np

        # create transformer intern bus and determine operational mode
        temp = self.create_abs_comp_bus(tf)

        # Calculates cooling temperature in absorber/evaporator depending on
        # ambient air temperature of recooling system
        data_np = np.array(self.weather_data["temperature"])
        t_cool = data_np + tf["recooling temperature difference"]
        t_cool = list(map(int, t_cool))

        # Import characteristic equation parameters
        param = pd.read_csv(
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            + "/technical_data/characteristic_parameters.csv"
        )

        # Calculation of characteristic temperature difference
        ddt = abs_hp_chiller.calc_characteristic_temp(
            t_hot=[tf["high temperature"]],
            t_cool=t_cool,
            t_chill=[tf["chilling temperature"]],
            coef_a=param[(param["name"] == tf["name"])]["a"].values[0],
            coef_e=param[(param["name"] == tf["name"])]["e"].values[0],
            method="kuehn_and_ziegler",
        )
        # Calculation of cooling capacity
        q_dots_evap = abs_hp_chiller.calc_heat_flux(
            ddts=ddt,
            coef_s=param[(param["name"] == tf["name"])]["s_E"].values[0],
            coef_r=param[(param["name"] == tf["name"])]["r_E"].values[0],
            method="kuehn_and_ziegler",
        )
        # Calculation of driving heat
        q_dots_gen = abs_hp_chiller.calc_heat_flux(
            ddts=ddt,
            coef_s=param[(param["name"] == tf["name"])]["s_G"].values[0],
            coef_r=param[(param["name"] == tf["name"])]["r_G"].values[0],
            method="kuehn_and_ziegler",
        )
        # Calculation of COPs
        cops_abs = [Qevap / Qgen for Qgen, Qevap in zip(q_dots_gen, q_dots_evap)]

        logging.info(
            "\t "
            + tf["label"]
            + ", Average Coefficient of Performance (COP): {:2.2f}".format(
                numpy.mean(cops_abs)
            )
        )

        # creates a source object as high temperature heat source and sets
        # heat capacity for this source
        maximum = tf["heat capacity of source"]
        source_label = tf["label"] + temp + "_source"
        self.nodes_transformer.append(
            Source(
                label=source_label,
                outputs={
                    self.busd[tf["label"] + temp + "_bus"]: Flow(
                        investment=Investment(
                            maximum=maximum,
                            fix_constraint_costs=0,
                            periodical_constraint_costs=0,
                        ),
                        emission_factor=0,
                    )
                },
            )
        )

        # Returns logging info
        logging.info("\t Heat Source created:" + source_label)

        # Set in- and outputs with conversion factors and creates transformer
        # object and adds it to  the list of components
        inputs = {
            "inputs": {
                self.busd[tf["input"]]: Flow(
                    variable_costs=tf["variable input costs"],
                    emission_factor=tf["variable input constraint costs"],
                ),
                self.busd[tf["label"] + temp + "_bus"]: Flow(emission_factor=0),
            }
        }
        outputs = self.get_primary_output_data(tf)
        conversion_factors = {
            "conversion_factors": {
                self.busd[tf["output"]]: [cop for cop in cops_abs],
                self.busd[tf["input"]]: tf["electrical input conversion factor"],
            }
        }

        self.create_transformer(
            tf, inputs=inputs, outputs=outputs, conversion_factors=conversion_factors
        )

    def __init__(self, nd, nodes, busd):
        """TODO Docstring missing"""
        # renames variables
        self.busd = busd
        self.nodes_transformer = []
        self.weather_data = nd["weather data"].copy()
        self.energysystem = next(nd["energysystem"].iterrows())[1]
        switch_dict = {
            "GenericTransformer": self.generic_transformer,
            "CompressionHeatTransformer": self.compression_heat_transformer,
            "GenericCHP": self.genericchp_transformer,
            "AbsorptionHeatTransformer": self.absorption_heat_transformer,
        }
        # creates a transformer object for every transformer item within nd
        for i, t in (
            nd["transformers"].loc[nd["transformers"]["active"] == 1].iterrows()
        ):
            switch_dict.get(
                t["transformer type"],
                "WARNING: The chosen transformer type is currently"
                " not a part of this model generator or contains "
                "a typo!",
            )(t)

        # appends created transformers to the list of nodes
        for i in range(len(self.nodes_transformer)):
            nodes.append(self.nodes_transformer[i])
