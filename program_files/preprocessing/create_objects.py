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






