"""
    Christian Klemm - christian.klemm@fh-muenster.de
    GregorBecker - gregor.becker@fh-muenster.de
"""

import logging
import pandas
from oemof.solph.components import Sink, Source
from oemof.solph.buses import Bus
from oemof.solph.flows import Flow


def buses(nd_buses: pandas.DataFrame, nodes: list) -> (dict, list):
    """
        Creates bus objects with the parameters given in 'nodes_data'
        and adds them to the list of components 'nodes'.

        :param nd_buses: pandas DataFrame, which represents the \
            worksheet "buses" of the previously implemented model \
            definition.
        :type nd_buses: pandas.DataFrame
        :param nodes: list of components created before (can be empty)
        :type nodes: list

        :return: - **busd** (dict) - dictionary containing all buses \
                    created
                 - **nodes** (list) - list of all the energy system's \
                    nodes

    """
    # Creates a dict of all buses of the energy system created from
    # the model definition's "buses" worksheet information
    busd = {}

    # Creates components, which are defined within the "buses"-sheet of
    # the original excel-file
    for _, bus in nd_buses[nd_buses["active"] == 1].iterrows():
        # creates an oemof-bus object
        bus_node = Bus(label=bus["label"])
        # adds the bus object to the list of components "nodes"
        nodes.append(bus_node)
        busd[bus["label"]] = bus_node
        # returns logging info
        logging.info("\t Bus created: " + bus["label"])

        # Create an sink for every bus, which is marked with
        # "excess"
        if bus["excess"]:
            # creates the oemof-sink object and
            # directly adds it to the list of components "nodes"
            inputs = {
                busd[bus["label"]]: Flow(
                    variable_costs=bus["excess costs"],
                    custom_attributes={"emission_factor":
                                       bus["excess constraint costs"]},
                )
            }
            nodes.append(Sink(label=bus["label"] + "_excess", inputs=inputs))

        # Create a source for every bus, which is marked with
        # "shortage"
        if bus["shortage"]:
            # creates the oemof-source object and
            # directly adds it to the list of components "nodes"
            outputs = {
                busd[bus["label"]]: Flow(
                    variable_costs=bus["shortage costs"],
                    custom_attributes={"emission_factor":
                                       bus["shortage constraint costs"]},
                )
            }
            nodes.append(Source(label=bus["label"] + "_shortage",
                                outputs=outputs))
    # Returns the list of buses as result of the function
    return busd, nodes
