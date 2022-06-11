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
                    offset=tf['fix investment costs'],
                    fix_constraint_costs=tf["fix investment constraint costs"])
            )}
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
                        else float("+inf")))})
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
                existing=tf['existing capacity'],
                nonconvex=True if
                tf['non-convex investment'] == 1 else False,
                offset=tf['fix investment costs'],
                fix_constraint_costs=tf[
                    "fix investment constraint costs"]
            ))}}
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
                        offset=tf['fix investment costs'],
                        fix_constraint_costs=tf[
                            "fix investment constraint costs"]
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
            os.path.dirname(os.path.dirname(__file__)))
            + '/technical_data/characteristic_parameters.csv')

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
            
            :param t: dictionary containing all information for
                      the creation of an oemof storage.
            :type t: dict

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
                    offset=s['fix investment costs'],
                    fix_constraint_costs=s["fix investment constraint costs"]))
        )

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
        data.index = pd.to_datetime(data.index.values, utc=True)
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
                    offset=s['fix investment costs'],
                    fix_constraint_costs=s["fix investment constraint costs"])
            ))
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
                    ep_constr_costs = link['periodical constraint costs']
                elif link['(un)directed'] == 'undirected':
                    ep_costs = link['periodical costs'] / 2
                    ep_constr_costs = link['periodical constraint costs'] / 2
                else:
                    raise SystemError('Problem with periodical costs')
                link_node = solph.custom.Link(
                    label=link['label'],
                    inputs={self.busd[link['bus1']]: solph.Flow(),
                            self.busd[link['bus2']]: solph.Flow()},
                    outputs={self.busd[link['bus2']]: solph.Flow(
                        variable_costs=
                        link['variable output costs'],
                        emission_factor=
                        link['variable output constraint costs'],
                        investment=solph.Investment(
                            ep_costs=ep_costs,
                            periodical_constraint_costs=ep_constr_costs,
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
                                'fix investment costs'],
                            fix_constraint_costs=link[
                                "fix investment constraint costs"])),
                        self.busd[link['bus1']]: solph.Flow(
                            variable_costs=
                            link['variable output costs'],
                            emission_factor=
                            link['variable output constraint costs'],
                            investment=solph.Investment(
                                ep_costs=ep_costs,
                                periodical_constraint_costs=ep_constr_costs,
                                minimum=link[
                                    'min. investment capacity'],
                                maximum=link['max. investment capacity']
                                if link['max. investment capacity'] != "inf"
                                else float("+inf"),
                                existing=link[
                                    'existing capacity'],))},
                    conversion_factors={
                        (self.busd[link['bus1']],
                         self.busd[link['bus2']]): link['efficiency'],
                        (self.busd[link['bus2']],
                         self.busd[link['bus1']]): link['efficiency']})
                if link["(un)directed"] == "directed":
                    link_node.inputs.pop(self.busd[link['bus2']])
                    link_node.outputs.pop(self.busd[link['bus1']])
                    link_node.conversion_factors.pop((self.busd[link['bus2']],
                                                      self.busd[link['bus1']]))
                nodes.append(link_node)
                # returns logging info
                logging.info('   ' + 'Link created: ' + link['label'])
