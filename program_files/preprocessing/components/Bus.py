# -*- coding: utf-8 -*-
"""
    Creates oemof energy system components.

    Functions for the creation of oemof energy system objects from a
    given set of object parameters.

    Contributors:

        - Christian Klemm - christian.klemm@fh-muenster.de
        - Gregor Becker - gb611137@fh-muenster.de
"""

from oemof.solph import Bus, Flow, Sink, Source
import logging


def buses(nd: dict, nodes: list) -> dict:
    """
        Creates bus objects.
        Creates bus objects with the parameters given in 'nodes_data' and
        adds them to the list of components 'nodes'.

        :param nd: dictionary containing parameters of the buses
                           to be created.
                           The following parameters have to be provided:

                                - label,
                                - active,
                                - excess,
                                - shortage,
                                - shortage costs,
                                - excess costs
        :type nd: dict
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
    for i, b in nd['buses'][nd["buses"]["active"] == 1].iterrows():
        # creates an oemof-bus object
        bus = Bus(label=b['label'])
        # adds the bus object to the list of components "nodes"
        nodes.append(bus)
        busd[b['label']] = bus
        # returns logging info
        logging.info('\t Bus created: ' + b['label'])

        # Create an sink for every bus, which is marked with
        # "excess"
        if b['excess']:
            # creates the oemof-sink object and
            # directly adds it to the list of components "nodes"
            inputs = {busd[b['label']]:
                      Flow(variable_costs=b['excess costs'],
                           emission_factor=b['excess constraint costs'])}
            nodes.append(Sink(label=b['label'] + '_excess', inputs=inputs))

        # Create a source for every bus, which is marked with
        # "shortage"
        if b['shortage']:
            # creates the oemof-source object and
            # directly adds it to the list of components "nodes"
            outputs = {busd[b['label']]:
                       Flow(variable_costs=b['shortage costs'],
                            emission_factor=b['shortage constraint costs'])}
            nodes.append(Source(label=b['label'] + '_shortage',
                                outputs=outputs))
    # Returns the list of buses as result of the function
    return busd






