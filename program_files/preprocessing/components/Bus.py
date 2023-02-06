from oemof.solph import Bus, Flow, Sink, Source
import logging


def buses(nodes_data: dict, nodes: list) -> dict:
    """
        Creates bus objects with the parameters given in 'nodes_data'
        and adds them to the list of components 'nodes'.
    
        :param nodes_data: dictionary containing parameters of the buses
                           to be created.
                           The following parameters have to be provided:
    
                                - label,
                                - active,
                                - excess,
                                - shortage,
                                - shortage costs,
                                - excess costs,
                                - district heating conn.,
                                - lat,
                                - lon
        :type nodes_data: dict
        :param nodes: list of components created before (can be empty)
        :type nodes: list
    
        :return: - **busd** (dict) - dictionary containing all buses \
            created
    
        Christian Klemm - christian.klemm@fh-muenster.de
    """
    # creates a list of buses
    busd = {}

    # Creates components, which are defined within the "buses"-sheet of
    # the original excel-file
    for num, bus in nodes_data["buses"][
            nodes_data["buses"]["active"] == 1].iterrows():
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
                    emission_factor=bus["excess constraint costs"],
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
                    emission_factor=bus["shortage constraint costs"],
                )
            }
            nodes.append(Source(label=bus["label"] + "_shortage",
                                outputs=outputs))
    # Returns the list of buses as result of the function
    return busd
