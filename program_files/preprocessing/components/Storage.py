from oemof.solph.components import GenericStorage
from oemof.solph import Flow, Investment
import pandas as pd
import logging


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
    
    def create_sink(self, s, loss_rate, storage_levels, fixed_losses):
        # creates storage object and adds it to the
        # list of components
        self.nodes.append(
            GenericStorage(
                label=s['label'],
                inputs={self.busd[s['bus']]: Flow(
                        variable_costs=s['variable input costs'],
                        emission_factor=s['variable input constraint costs'])},
                outputs={self.busd[s['bus']]: Flow(
                        variable_costs=s['variable output costs'],
                        emission_factor=s['variable output constraint costs'])
                },
                min_storage_level=storage_levels[0],
                max_storage_level=storage_levels[1],
                loss_rate=loss_rate,
                fixed_losses_relative=fixed_losses[0],
                fixed_losses_absolute=fixed_losses[1],
                inflow_conversion_factor=s['efficiency inflow'],
                outflow_conversion_factor=s['efficiency outflow'],
                invest_relation_input_capacity=s['input/capacity ratio'],
                invest_relation_output_capacity=s['output/capacity ratio'],
                investment=Investment(
                    ep_costs=s['periodical costs'],
                    periodical_constraint_costs=s[
                        'periodical constraint costs'],
                    existing=s['existing capacity'],
                    minimum=s['min. investment capacity'],
                    maximum=s['max. investment capacity'],
                    nonconvex=True if s['non-convex investment'] == 1
                    else False,
                    offset=s['fix investment costs'],
                    fix_constraint_costs=s["fix investment constraint costs"]))
        )
    
        # returns logging info
        logging.info('\t Storage created: ' + s['label'])
        
    def generic_storage(self, s):
        """
            Creates a generic storage object with the parameters
            given in 'nodes_data' and adds it to the list of components 'nodes'

            :param s: dictionary containing all information for
                      the creation of an oemof storage.
            :type s: dict

        """
        self.create_sink(
                s,
                s['capacity loss'],
                storage_levels=[None, None],
                fixed_losses=[None, None])

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
        data = self.weather_data
        # Import weather Data
        data.index = pd.to_datetime(data.index.values, utc=True)
        data.index = pd.to_datetime(data.index).tz_convert(
                "Europe/Berlin")
        # calculations for stratified thermal storage
        loss_rate, fixed_losses_relative, fixed_losses_absolute = \
            calculate_losses(
                    s['U value'],
                    s['diameter'],
                    s['temperature high'],
                    s['temperature low'],
                    data['temperature'])
        self.create_sink(
                s,
                loss_rate,
                storage_levels =[s['capacity min'], s['capacity max']],
                fixed_losses=[fixed_losses_relative, fixed_losses_absolute])
    
    def __init__(self, nd: dict, nodes: list, busd: dict):
        """
            Inits the storage class.

            Christian Klemm - christian.klemm@fh-muenster.de
        """
        # renames variables
        self.busd = busd
        self.nodes = []
        self.weather_data = nd["weather data"].copy()
        
        switch_dict = {"Generic": self.generic_storage,
                       "Stratified": self.stratified_thermal_storage}
        
        # creates storage object for every storage element in nodes_data
        for i, s in nd['storages'][nd["storages"]["active"] == 1].iterrows():
            switch_dict.get(s["storage type"],
                            "Storage type chosen either consits typo or "
                            "is invalid!")(s)
        
        # appends created storages to the list of nodes
        for i in range(len(self.nodes)):
            nodes.append(self.nodes[i])
