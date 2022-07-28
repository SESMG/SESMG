from oemof.solph import Investment, Flow
from oemof.solph.custom import Link
import logging


class Links:
    """
        Creates links objects as defined in 'nodes_data' and adds them
        to the list of components 'nodes'.

        # TODO Excel columns missing

        :param nd: dictionary containing data from excel
                           scenario file. The following data have to be
                           provided:

                                - 'active'
                                - 'label'
                                - '(un)directed'
        :type nd: dict
        :param busd: dictionary containing the buses of the energy system
        :type busd: dict
        :param nodes: list of components created before(can be empty)
        :type nodes: list

        Christian Klemm - christian.klemm@fh-muenster.de
    """
    # intern variables
    busd = None
    
    @staticmethod
    def get_flow(link):
        """
        
        """
        if link['(un)directed'] == 'directed':
            ep_costs = link['periodical costs']
            ep_constr_costs = link['periodical constraint costs']
            fix_investment_costs = link['fix investment costs']
            fix_constr_costs = link["fix investment constraint costs"]
        elif link['(un)directed'] == 'undirected':
            ep_costs = link['periodical costs'] / 2
            ep_constr_costs = link['periodical constraint costs'] / 2
            fix_investment_costs = link['fix investment costs'] / 2
            fix_constr_costs = link["fix investment constraint costs"] / 2
        else:
            raise SystemError('Problem with periodical costs')
        
        return Flow(variable_costs=link['variable output costs'],
                    emission_factor=link['variable output constraint costs'],
                    investment=Investment(
                        ep_costs=ep_costs,
                        periodical_constraint_costs=ep_constr_costs,
                        minimum=link['min. investment capacity'],
                        maximum=link['max. investment capacity'],
                        existing=link['existing capacity'],
                        nonconvex=True
                        if link['non-convex investment'] == 1
                        else False,
                        offset=fix_investment_costs,
                        fix_constraint_costs=fix_constr_costs))
    
    def __init__(self, nd, nodes, busd):
        """
            Inits the Links class.

            Christian Klemm - christian.klemm@fh-muenster.de
        """
        # renames variables
        self.busd = busd
        # creates link objects for every link object in nd
        for i, link in nd['links'][nd["links"]["active"] == 1].iterrows():
            link_node = Link(
                label=link['label'],
                inputs={self.busd[link['bus1']]: Flow(emission_factor=0),
                        self.busd[link['bus2']]: Flow(emission_factor=0)},
                outputs={
                    self.busd[link['bus2']]: self.get_flow(link),
                    self.busd[link['bus1']]: self.get_flow(link)},
                conversion_factors={
                    (self.busd[link['bus1']],
                     self.busd[link['bus2']]): link['efficiency'],
                    (self.busd[link['bus2']],
                     self.busd[link['bus1']]): link['efficiency']})
            # remove second direction if directed link is chosen
            if link["(un)directed"] == "directed":
                link_node.inputs.pop(self.busd[link['bus2']])
                link_node.outputs.pop(self.busd[link['bus1']])
                link_node.conversion_factors.pop((self.busd[link['bus2']],
                                                  self.busd[link['bus1']]))
            nodes.append(link_node)
            # returns logging info
            logging.info('\t Link created: ' + link['label'])
