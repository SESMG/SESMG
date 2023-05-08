"""
    Christian Klemm - christian.klemm@fh-muenster.de
    Yannick Wittor - yw090223@fh-muenster.de
"""
from oemof.solph.components import GenericStorage
from oemof.solph import Flow, Investment
import pandas
import logging


class Storages:
    """
        Creates oemof storage objects as defined in 'nodes_data' and
        adds them to the list of components 'nodes'.
    
        :param nodes_data: dictionary containing parameters of the \
            storages to be created. The following data have to be \
            provided:
    
                - label
                - active
                - bus
                - storage type
                - existing capacity
                - min. investment capacity
                - max.investment capacity
                - non-convex investments
                - fix investment costs
                - fix investment constraint costs
                - input/capacity ratio
                - output/capacity ratio
                - efficiency inflow
                - efficiency outflow
                - initial capacity
                - capacity min
                - capacity max
                - periodical costs
                - periodical constraint costs
                - variable input costs
                - variable input constraint costs
                - variable output costs
                - variable output constraint costs
                - capacity loss (Generic)
                - diameter (Stratified)
                - temperature high (Stratified)
                - temperature low (Stratified)
                - U value (Stratified)
    
        :type nodes_data: dict
        :param busd: dictionary containing the buses of the energy system
        :type busd: dict
        :param nodes: list of components created before (can be empty)
        :type nodes: list
    """

    def create_storage(self, storage: pandas.Series, loss_rate: pandas.Series,
                       storage_levels: list, fixed_losses: list) -> None:
        """
            Within this method the previously prepared storage
            parameters are used to create an oemof storage object with
            the given parameters and add it to the class intern list
            nodes which is returned to the main algorithm at the end.
            
            :param storage: Series containing all information for \
                the creation of an oemof storage. At least the \
                following key-value-pairs have to be included:
    
                    - label
                    - active
                    - bus
                    - storage type
                    - existing capacity
                    - min. investment capacity
                    - max.investment capacity
                    - non-convex investments
                    - fix investment costs
                    - fix investment constraint costs
                    - input/capacity ratio
                    - output/capacity ratio
                    - efficiency inflow
                    - efficiency outflow
                    - initial capacity
                    - capacity min
                    - capacity max
                    - periodical costs
                    - periodical constraint costs
                    - variable input costs
                    - variable input constraint costs
                    - variable output costs
                    - variable output constraint costs
            
            :type storage: pandas.Series
            :param loss_rate: time series holding the loss coefficient \
                foreach time step
            :type loss_rate: pandas.Series
            :param storage_levels: list containing the minimum and \
                maximum storage level
            :type storage_levels: list
            :param fixed_losses: list containing the minimum and \
                maximum fixed losses (independent of the mode of \
                operation)
            :type fixed_losses: list
        """
        # creates storage object and adds it to the
        # list of components
        self.nodes.append(
            GenericStorage(
                label=storage["label"],
                inputs={
                    self.busd[storage["bus"]]: Flow(
                        variable_costs=storage["variable input costs"],
                        emission_factor=storage[
                            "variable input constraint costs"],
                    )
                },
                outputs={
                    self.busd[storage["bus"]]: Flow(
                        variable_costs=storage["variable output costs"],
                        emission_factor=storage[
                            "variable output constraint costs"],
                    )
                },
                min_storage_level=storage_levels[0],
                max_storage_level=storage_levels[1],
                loss_rate=loss_rate,
                initial_storage_level=storage["initial capacity"],
                fixed_losses_relative=fixed_losses[0],
                fixed_losses_absolute=fixed_losses[1],
                inflow_conversion_factor=storage["efficiency inflow"],
                outflow_conversion_factor=storage["efficiency outflow"],
                invest_relation_input_capacity=storage["input/capacity ratio"],
                invest_relation_output_capacity=storage[
                    "output/capacity ratio"],
                investment=Investment(
                    ep_costs=storage["periodical costs"],
                    periodical_constraint_costs=storage[
                        "periodical constraint costs"],
                    existing=storage["existing capacity"],
                    minimum=storage["min. investment capacity"],
                    maximum=storage["max. investment capacity"],
                    nonconvex=True if storage["non-convex investment"] == 1
                    else False,
                    offset=storage["fix investment costs"],
                    fix_constraint_costs=storage[
                        "fix investment constraint costs"],
                ),
            )
        )

        # returns logging info
        logging.info("\t Storage created: " + storage["label"])

    def generic_storage(self, storage: pandas.Series) -> None:
        """
            Creates a generic storage object with the parameters
            given in 'nodes_data' and adds it to the list of components
            'nodes'.
    
            :param storage: Series containing all information for the \
                creation of an oemof storage.
            :type storage: dict
        """
        self.create_storage(
            storage,
            storage["capacity loss"],
            storage_levels=[storage["capacity min"], storage["capacity max"]],
            fixed_losses=[0, 0],
        )

    def stratified_thermal_storage(self, storage: pandas.Series) -> None:
        """
            Creates a stratified thermal storage object with the
            parameters given in 'nodes_data' and adds it to the list of
            components 'nodes'.
    
            :param storage: Series which has to contain the following \
                keyword arguments:
                
                    - Standard information on Storages
                    - storage type: Stratified
                    - diameter
                    - temperature high
                    - temperature low
                    - U value /(W/(sqm*K))
                    
            :type storage: pandas.Series
        """
        # import functions for stratified thermal storages from oemof thermal
        from oemof.thermal.stratified_thermal_storage import calculate_losses

        data = self.weather_data
        # Import weather Data
        data.index = pandas.to_datetime(data.index.values)
        # calculations for stratified thermal storage
        loss_rate, fixed_losses_relative, fixed_losses_absolute = \
            calculate_losses(
                storage["U value"],
                storage["diameter"],
                storage["temperature high"],
                storage["temperature low"],
                data["temperature"])
        
        self.create_storage(
            storage=storage,
            loss_rate=loss_rate,
            storage_levels=[storage["capacity min"], storage["capacity max"]],
            fixed_losses=[fixed_losses_relative, fixed_losses_absolute]
        )

    def __init__(self, nodes_data: dict, nodes: list, busd: dict):
        """
            Inits the storage class.
        """
        # renames variables
        self.busd = busd
        self.nodes = []
        self.weather_data = nodes_data["weather data"].copy()

        switch_dict = {
            "Generic": self.generic_storage,
            "Stratified": self.stratified_thermal_storage,
        }
        
        # active storages
        storages = nodes_data["storages"][
            nodes_data["storages"]["active"] == 1]
        # creates storage object for every storage element in nodes_data
        for num, storage in storages.iterrows():
            switch_dict.get(
                storage["storage type"],
                "Storage type chosen either consists typo or " "is invalid!",
            )(storage)

        # appends created storages to the list of nodes
        for i in range(len(self.nodes)):
            nodes.append(self.nodes[i])
