"""
    Christian Klemm - christian.klemm@fh-muenster.de
    Janik Budde - Janik.Budde@fh-muenster.de
    Yannick Wittor - yw090223@fh-muenster.de
"""
from oemof.solph import Flow, Investment, Transformer, Source, Bus
from oemof.solph.components import GenericCHP
import logging
import numpy
import pandas
import os


class Transformers:
    """
        Creates transformer objects as defined in 'nodes_data' and adds
        them to the list of components 'nodes'.
    
        :param nodes_data: dictionary containing data from excel model \
            definition file. The following data have to be provided:
    
                - label,
                - active,
                - transformer type,
                - mode,
                - input,
                - input2,
                - output,
                - output2,
                - input2 / input,
                - efficiency,
                - efficiency2,
                - variable input costs,
                - variable input constraint costs,
                - variable input costs 2,
                - variable input constraint costs 2,
                - variable output costs,
                - variable output constraint costs,
                - variable output costs 2,
                - variable output constraint costs 2,
                - existing capacity,
                - max. investment capacity,
                - min. investment capacity,
                - periodical costs,
                - periodical constraint costs,
                - non-convex investment,
                - fix investment costs,
                - fix investment constraint costs,
                - heat source,
                - temperature high,
                - temperature low,
                - quality grade,
                - area,
                - length of geoth. probe,
                - heat extraction,
                - min. borehole area,
                - temp. threshold icing,
                - factor icing,
                - name,
                - high temperature,
                - chilling temperature,
                - electrical input conversion factor,
                - recooling temperature difference,
                - heat capacity of source,
                - min. share of flue gas loss,
                - max. share of flue gas loss,
                - min. electric power,
                - max. electric power,
                - min. electric efficiency,
                - max. electric efficiency,
                - minimal thermal output power,
                - elec. power loss index,
                - back pressure
                
        :type nodes_data: dict
        :param busd: dictionary containing the buses of the energy \
            system
        :type busd: dict
        :param nodes: list of components created before (can be empty)
        :type nodes: list
    """
    
    # intern variables
    nodes_transformer = []
    busd = None
    
    def get_primary_output_data(self, transformer: pandas.Series,
                                max_invest=None) -> dict:
        """
            Within this method the output flow data of the currently
            considered transformer is parameterized and returned to the
            transformer creation method. This method results from the
            equality of output parametrization of nearly each
            transformer.
            
            :param transformer: Series containing the transformer's \
                parameter. Series has to contain at least the \
                following key-value pairs:
                
                    - min. investment capacity
                    - max. investment capacity
                    - periodical costs
                    - periodical constraint costs
                    - existing capacity
                    - non-convex investment
                    - fix investment costs
                    - fix investment constraint costs
                    - variable output costs
                    - variable output constraint costs
                    
            :type transformer: pandas.Series
            :param max_invest: float value, which allows to reduce the \
                maximum capacity value for ground source heat pump to \
                the heat pump extraction capacity from the ground, \
                since this is usually the factor limiting the capacity.
            :type max_invest: float
            
            :returns: - **-** (dict) - dictionary holding the primary \
                output of the considered transformer
        """
        # check rather the max invest value is set and smaller than the
        # one entered within the spreadsheet, if yes replace the
        # spreadsheet value
        if max_invest and max_invest < transformer["max. investment capacity"]:
            transformer["max. investment capacity"] = max_invest
        # create the transformers investment object which is set as
        # investment flow afterwards
        invest = Investment(
                ep_costs=transformer["periodical costs"],
                minimum=transformer["min. investment capacity"],
                maximum=transformer["max. investment capacity"],
                periodical_constraint_costs=transformer[
                    "periodical constraint costs"],
                existing=transformer["existing capacity"],
                nonconvex=True if transformer["non-convex investment"] == 1
                else False,
                offset=transformer["fix investment costs"],
                fix_constraint_costs=transformer[
                    "fix investment constraint costs"])
        # return the parameterized flow to the main creation process
        return {
            "outputs": {
                self.busd[transformer["output"]]: Flow(
                        variable_costs=transformer["variable output costs"],
                        emission_factor=transformer[
                            "variable output constraint costs"],
                        investment=invest,
                )
            }
        }
    
    def create_transformer(self, transformer: pandas.Series, inputs: dict,
                           conversion_factors: dict, outputs: dict) -> None:
        """
            Within this method the parameterized transformer (inputs,
            outputs and conversion factors already created) is added to
            the class intern list of nodes and returned to the main
            algorithm at the end.
            
            :param transformer: Series containing the transformer's \
                parameter. Series has to contain at least the \
                following key-value pairs:
                    
                    - label
            
            :type transformer: pandas.Series
            :param inputs: dictionary holding the transformer's input \
                flows
            :type inputs: dict
            :param outputs: dictionary holding the transformer's \
                output flows
            :type outputs: dict
            :param conversion_factors: dictionary holding the \
                transformer's input and output conversion factors
            :type conversion_factors: dict
        """
        self.nodes_transformer.append(
                Transformer(label=transformer["label"],
                            **inputs,
                            **outputs,
                            **conversion_factors)
        )
        logging.info("\t Transformer created: " + transformer["label"])
    
    def generic_transformer(self, transformer: pandas.Series,
                            two_input=False) -> None:
        """
            Creates a generic transformer with the parameters given in
            'nodes_data' and adds it to the list of components 'nodes'.
    
            :param transformer: Series containing all information \
                for the creation of an oemof transformer. At least the
                following key-value-pairs have to be included:
    
                    - label,
                    - input,
                    - input2,
                    - output,
                    - output2,
                    - efficiency,
                    - efficiency2,
                    - input2 / input,
                    - variable input costs,
                    - variable input constraint costs,
                    - variable input costs 2,
                    - variable input constraint costs 2,
                    - variable output costs,
                    - variable output constraint costs,
                    - variable output costs 2,
                    - variable output constraint costs 2,
                    - periodical costs,
                    - periodical constraint costs,
                    - min. investment capacity,
                    - max. investment capacity,
                    - existing capacity,
                    - non-convex investment,
                    - fix investment costs,
                    - fix investment constraint costs
                    
            :type transformer: pandas.Series
            :param two_input: boolean which is used to differentiate \
                between the creation process of an one or a two input \
                transformer
            :type two_input: bool
        """
        # parametrization of the first transformer output
        outputs = self.get_primary_output_data(transformer)
        conversion_factors = {
            self.busd[transformer["output"]]: transformer["efficiency"]
        }
        # Defines Capacity values for the second transformer output
        if transformer["output2"] not in ["None", "none", 0]:
            efficiency_ratio = float(transformer["efficiency2"]) \
                               / float(transformer["efficiency"])
            # calculate the existing capacity for the second output
            # based on the efficiency ratio
            existing_capacity2 = efficiency_ratio \
                * float(transformer["existing capacity"])
            # calculate the minimum capacity for the second output
            # based on the efficiency ratio
            minimum_capacity2 = efficiency_ratio \
                * float(transformer["min. investment capacity"])
            maximum_capacity2 = efficiency_ratio \
                * float(transformer["max. investment capacity"])
            # Creates transformer object and adds it to the list of
            # components
            outputs["outputs"].update(
                {self.busd[transformer["output2"]]: Flow(
                    variable_costs=transformer["variable output costs 2"],
                    emission_factor=transformer[
                        "variable output constraint costs 2"],
                    investment=Investment(
                            existing=existing_capacity2,
                            minimum=minimum_capacity2,
                            maximum=maximum_capacity2,
                            periodical_constraint_costs=0,
                            fix_constraint_costs=0),
                    )}
            )
            conversion_factors.update({
                self.busd[transformer["output2"]]: transformer["efficiency2"]})
        
        conversion_factors = {"conversion_factors": conversion_factors}
        inputs = {"inputs": {
            self.busd[transformer["input"]]: Flow(
                    variable_costs=transformer["variable input costs"],
                    emission_factor=transformer[
                        "variable input constraint costs"])
        }}
        # within this part of the method a second input for the
        # considered transformer is created. it's conversion factor
        # is calculated based on the input2 / input ratio given within
        # the spreadsheet
        if two_input:
            inputs["inputs"].update(
                    {
                        self.busd[transformer["input2"]]: Flow(
                                variable_costs=transformer[
                                    "variable input costs 2"],
                                emission_factor=transformer[
                                    "variable input constraint costs 2"],
                        )
                    }
            )
            conversion_factors["conversion_factors"].update(
                    {self.busd[transformer["input2"]]: transformer[
                        "input2 / input"]})
        # start the transformer creation after the parametrization has
        # been finished
        self.create_transformer(transformer=transformer,
                                inputs=inputs,
                                outputs=outputs,
                                conversion_factors=conversion_factors)
    
    def create_abs_comp_bus(self, transformer: pandas.Series) -> str:
        """
            create absorption chiller and compression heat transformer's
            intern bus
    
            :param transformer: Series containing all information \
                for the creation of an oemof transformer. At least the \
                following key-value-pairs have to be included:
                
                    - label,
                    - mode
                    
            :type transformer: pandas.Series
            
            :return: - **temp** (str) - mode specific bus label ending
        """
        # creates one oemof-bus object for compression heat transformers
        # depending on mode of operation
        if transformer["mode"] == "heat_pump":
            temp = "_low_temp"
        elif transformer["mode"] == "chiller":
            temp = "_high_temp"
        else:
            raise ValueError("Mode of "
                             + transformer["label"] + "contains a typo")
        bus = Bus(label=transformer["label"] + temp + "_bus")
        
        # adds the bus object to the list of components "nodes"
        self.nodes_transformer.append(bus)
        self.busd[transformer["label"] + temp + "_bus"] = bus
        
        # returns logging info
        logging.info("\t Bus created: " + transformer["label"] + temp + "_bus")
        
        return temp
    
    def compression_heat_transformer(self, transformer: pandas.Series) -> None:
        """
            Creates a Compression Heat Pump or Compression Chiller by
            using oemof.thermal and adds it to the list of components
            'nodes'.
    
            :param tf: Series containing all information \
                for the creation of an oemof transformer. At least the \
                following key-value-pairs have to be included:
    
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
    
            
        """
        
        # import oemof.thermal in order to calculate the cop
        import \
            oemof.thermal.compression_heatpumps_and_chillers as cmpr_hp_chiller
        
        # create transformer intern bus and determine operational mode
        temp = self.create_abs_comp_bus(transformer=transformer)
        
        # dictionary containing the
        # 1. heat source specific labels,
        # 2. capacity calculation,
        # 3. heat_source_temperature definition
        switch_dict = {
            "Ground": [
                transformer["label"] + temp + "_ground_source",
                # A * (l_{probe} * q / A_{min})
                transformer["area"]
                * (transformer["length of the geoth. probe"]
                   * transformer["heat extraction"]
                   / (transformer["min. borehole area"]
                      if transformer["min. borehole area"] != 0 else 1)),
                self.weather_data["ground_temp"],
            ],
            "GroundWater": [
                transformer["label"] + temp + "_groundwater_source",
                float("+inf"),
                self.weather_data["groundwater_temp"],
            ],
            "Air": [
                transformer["label"] + temp + "_air_source",
                float("+inf"),
                self.weather_data["temperature"],
            ],
            "Water": [
                transformer["label"] + temp + "_water_source",
                float("+inf"),
                self.weather_data["water_temp"],
            ],
        }
        # differentiation between heat sources under consideration of mode
        # of operation
        transformer_label, heatsource_cap, temp_low = list(
            switch_dict.get(
                transformer["heat source"],
                transformer["label"] + " Error in heat source attribute"
            )
        )
        
        # Creates heat source for transformer. The heat source costs are
        # considered by the transformer.
        self.nodes_transformer.append(
            Source(
                label=transformer_label,
                outputs={
                    self.busd[transformer["label"] + temp + "_bus"]: Flow(
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
        logging.info("\t Heat Source created: " + transformer["label"]
                     + temp + "_source")
        
        temp_high = temp_low.copy()
        if transformer["heat source"] == "Air":
            temp_low_value = transformer["temperature low"]
            # low temperature as formula to avoid division by zero error
            for index, value in enumerate(temp_high):
                if value == temp_low_value:
                    temp_high[index] = temp_low_value + 0.1
        
        if transformer["mode"] == "heat_pump":
            temp_threshold_icing = transformer["temp. threshold icing"]
            factor_icing = transformer["factor icing"]
            temp_high = [float(transformer["temperature high"])]
        elif transformer["mode"] == "chiller":
            # variable "icing" is not important in cooling mode
            temp_threshold_icing = None
            factor_icing = None
            temp_low = [transformer["temperature low"]]
        else:
            raise ValueError("Mode of " + transformer["label"]
                             + "contains a typo")
        
        # calculation of COPs with set parameters
        cops_hp = cmpr_hp_chiller.calc_cops(
            temp_high=temp_high,
            temp_low=temp_low,
            quality_grade=transformer["quality grade"],
            temp_threshold_icing=temp_threshold_icing,
            factor_icing=factor_icing,
            mode=transformer["mode"],
        )
        # logging the transformer's COP
        logging.info("\t " + transformer["label"]
                     + ", Average Coefficient of Performance (COP): "
                       "{:2.2f}".format(numpy.mean(cops_hp)))
        
        # transformer inputs parameter
        inputs = {
            "inputs": {
                self.busd[transformer["input"]]: Flow(
                    variable_costs=transformer["variable input costs"],
                    emission_factor=transformer[
                        "variable input constraint costs"],
                ),
                self.busd[transformer["label"] + temp + "_bus"]: Flow(
                    emission_factor=0),
            }
        }
        if transformer["heat source"] == "Ground" \
                and transformer["mode"] == "heat_pump":
            cop_new = [(i / (i - 1)) for i in cops_hp]
            max_invest = heatsource_cap * max(cop_new)
        else:
            max_invest = None
        # parametrize the transformer's first output flow
        outputs = self.get_primary_output_data(transformer=transformer,
                                               max_invest=max_invest)
        # transformer conversion factor parameter
        conversion_factors = {
            "conversion_factors": {
                self.busd[transformer["label"] + temp + "_bus"]: [
                    ((cop - 1) / cop) / transformer["efficiency"]
                    for cop in cops_hp
                ],
                self.busd[transformer["input"]]: [1 / cop for cop in cops_hp],
            }
        }
        
        # start the transformer creation after the parametrization has
        # been finished
        self.create_transformer(
            transformer=transformer,
            inputs=inputs,
            outputs=outputs,
            conversion_factors=conversion_factors
        )
    
    def genericchp_transformer(self, tf: pandas.Series):
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
                                        tf[
                                            "share of flue gas loss at max "
                                            "heat extraction"]
                                        for p in range(0, periods)
                                    ],
                                    H_L_FG_share_min=[
                                        tf[
                                            "share of flue gas loss at min "
                                            "heat extraction"]
                                        for p in range(0, periods)
                                    ],
                                    variable_costs=tf["variable input costs"],
                                    emission_factor=tf[
                                        "variable input constraint costs"],
                            )
                        },
                        electrical_output={
                            self.busd[tf["output"]]: Flow(
                                    investment=Investment(
                                            ep_costs=tf["periodical costs"],
                                            periodical_constraint_costs=tf[
                                                "periodical constraint costs"
                                            ],
                                            minimum=tf[
                                                "min. investment capacity"],
                                            maximum=tf[
                                                "max. investment capacity"],
                                            existing=tf["existing capacity"],
                                            nonconvex=True
                                            if tf["non-convex investment"] == 1
                                            else False,
                                            offset=tf["fix investment costs"],
                                            fix_constraint_costs=tf[
                                                "fix investment constraint "
                                                "costs"],
                                    ),
                                    P_max_woDH=[
                                        tf[
                                            "max. electric power without "
                                            "district heating"]
                                        for p in range(0, periods)
                                    ],
                                    P_min_woDH=[
                                        tf[
                                            "min. electric power without "
                                            "district heating"]
                                        for p in range(0, periods)
                                    ],
                                    Eta_el_max_woDH=[
                                        tf[
                                            "el. eff. at max. fuel flow w/o "
                                            "distr. " "heating"]
                                        for p in range(0, periods)
                                    ],
                                    Eta_el_min_woDH=[
                                        tf[
                                            "el. eff. at min. fuel flow w/o "
                                            "distr. " "heating"]
                                        for p in range(0, periods)
                                    ],
                                    variable_costs=tf["variable output costs"],
                                    emission_factor=tf[
                                        "variable output constraint costs"],
                            )
                        },
                        heat_output={
                            self.busd[tf["output2"]]: Flow(
                                    Q_CW_min=[
                                        tf[
                                            "minimal therm. condenser load "
                                            "to cooling water"]
                                        for p in range(0, periods)
                                    ],
                                    variable_costs=tf[
                                        "variable output costs 2"],
                                    emission_factor=tf[
                                        "variable output constraint costs 2"],
                            )
                        },
                        Beta=[tf["power loss index"] for p in
                              range(0, periods)],
                        back_pressure=True if tf[
                                                  "back pressure"] == 1 else
                        False,
                )
        )
        
        # returns logging info
        logging.info("\t Transformer created: " + tf["label"])
    
    def absorption_heat_transformer(self, tf: pandas.Series):
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
        import \
            oemof.thermal.absorption_heatpumps_and_chillers as abs_hp_chiller
        import numpy as np
        
        # create transformer intern bus and determine operational mode
        temp = self.create_abs_comp_bus(tf)
        
        # Calculates cooling temperature in absorber/evaporator depending on
        # ambient air temperature of recooling system
        data_np = np.array(self.weather_data["temperature"])
        t_cool = data_np + tf["recooling temperature difference"]
        t_cool = list(map(int, t_cool))
        
        # Import characteristic equation parameters
        param = pandas.read_csv(
                os.path.join(os.path.dirname(
                    os.path.dirname(os.path.dirname(__file__))))
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
        cops_abs = [Qevap / Qgen for Qgen, Qevap in
                    zip(q_dots_gen, q_dots_evap)]
        
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
                self.busd[tf["label"] + temp + "_bus"]: Flow(
                    emission_factor=0),
            }
        }
        outputs = self.get_primary_output_data(tf)
        conversion_factors = {
            "conversion_factors": {
                self.busd[tf["output"]]: [cop for cop in cops_abs],
                self.busd[tf["input"]]: tf[
                    "electrical input conversion factor"],
            }
        }
        
        self.create_transformer(
                tf, inputs=inputs, outputs=outputs,
                conversion_factors=conversion_factors
        )
    
    def __init__(self, nodes_data, nodes, busd):
        """
            Inits the Transformer class.
        """
        # renames variables
        self.busd = busd
        self.nodes_transformer = []
        self.weather_data = nodes_data["weather data"].copy()
        self.energysystem = next(nodes_data["energysystem"].iterrows())[1]
        switch_dict = {
            "GenericTransformer": self.generic_transformer,
            "CompressionHeatTransformer": self.compression_heat_transformer,
            "GenericCHP": self.genericchp_transformer,
            "AbsorptionHeatTransformer": self.absorption_heat_transformer,
        }
        # creates a transformer object for every transformer item within nd
        for i, t in (
                nodes_data["transformers"].loc[
                    nodes_data["transformers"]["active"] == 1].iterrows()
        ):
            if t["transformer type"] != "GenericTwoInputTransformer":
                switch_dict.get(
                        t["transformer type"],
                        "WARNING: The chosen transformer type is currently"
                        " not a part of this model generator or contains "
                        "a typo!",
                )(t)
            else:
                self.generic_transformer(t, True)
        
        # appends created transformers to the list of nodes
        for i in range(len(self.nodes_transformer)):
            nodes.append(self.nodes_transformer[i])
