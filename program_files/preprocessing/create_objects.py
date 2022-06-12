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
