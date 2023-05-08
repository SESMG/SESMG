"""
    Christian Klemm - christian.klemm@fh-muenster.de
"""
from oemof.solph import Investment, Flow
from oemof.solph.custom import Link
import logging
import pandas


class Links:
    """
        Creates link objects as defined in 'nodes_data' and adds them
        to the list of components 'nodes'.
    
        :param nodes_data: dictionary containing data from excel model \
            definition file. The following data have to be provided:
    
                - active
                - label
                - (un)directed
                - efficiency
                - bus1
                - bus2
                - periodical costs
                - periodical constraint costs
                - variable output costs
                - variable output constraint costs
                - non-convex investment
                - fix investment costs
                - fix investment constraint costs
                - min. investment capacity
                - max. investment capacity
                - existing capacity

        :type nodes_data: dict
        :param nodes: list of components created before (can be empty)
        :type nodes: list
        :param busd: dictionary containing the buses of the energy \
            system
        :type busd: dict
    """

    @staticmethod
    def get_flow(link: pandas.Series) -> Flow:
        """
            The parameterization of the output flow of the link
            component has been outsourced to this static method.
            
            :param link: nodes data row of the link in creation
            :type link: pandas.Series
            
            :returns: **-** (oemof.solph.custom.Flow) - oemof Flow \
                object with the output's parameter given in the link \
                parameter
        """
        # if the link is directed the total costs result from one flow
        # which is the reason for the assignment of the total costs to
        # this output flow
        if link["(un)directed"] == "directed":
            ep_costs = link["periodical costs"]
            ep_constr_costs = link["periodical constraint costs"]
            fix_investment_costs = link["fix investment costs"]
            fix_constr_costs = link["fix investment constraint costs"]
        # if the link is undirected the total costs result from both
        # output flows which is the reason for the assignment of the
        # half costs to each of them
        elif link["(un)directed"] == "undirected":
            ep_costs = link["periodical costs"] / 2
            ep_constr_costs = link["periodical constraint costs"] / 2
            fix_investment_costs = link["fix investment costs"] / 2
            fix_constr_costs = link["fix investment constraint costs"] / 2
        else:
            raise SystemError("Parameter (un)directed not filled correctly "
                              "for the component " + link["label"])

        return Flow(
            variable_costs=link["variable output costs"],
            emission_factor=link["variable output constraint costs"],
            investment=Investment(
                ep_costs=ep_costs,
                periodical_constraint_costs=ep_constr_costs,
                minimum=link["min. investment capacity"],
                maximum=link["max. investment capacity"],
                existing=link["existing capacity"],
                nonconvex=True if link["non-convex investment"] == 1
                else False,
                offset=fix_investment_costs,
                fix_constraint_costs=fix_constr_costs,
            ),
        )

    def __init__(self, nodes_data: dict, nodes: list, busd: dict) -> None:
        """
            Inits the Links class.
        """
        # renames variables
        self.busd = busd
        links = nodes_data["links"]
        # creates link objects for every link object in nd
        for num, link in links[links["active"] == 1].iterrows():
            link_node = Link(
                label=link["label"],
                inputs={
                    self.busd[link["bus1"]]: Flow(emission_factor=0),
                    self.busd[link["bus2"]]: Flow(emission_factor=0),
                },
                outputs={
                    self.busd[link["bus2"]]: self.get_flow(link),
                    self.busd[link["bus1"]]: self.get_flow(link),
                },
                conversion_factors={
                    (self.busd[link["bus1"]], self.busd[link["bus2"]]): link[
                        "efficiency"
                    ],
                    (self.busd[link["bus2"]], self.busd[link["bus1"]]): link[
                        "efficiency"
                    ],
                },
            )
            # remove second direction if directed link is chosen
            if link["(un)directed"] == "directed":
                link_node.inputs.pop(self.busd[link["bus2"]])
                link_node.outputs.pop(self.busd[link["bus1"]])
                link_node.conversion_factors.pop(
                    (self.busd[link["bus2"]], self.busd[link["bus1"]])
                )
            nodes.append(link_node)
            # returns logging info
            logging.info("\t Link created: " + link["label"])
