"""
    Functions for returning optimization results in several forms.

    Contributor:
        Christian Klemm - christian.klemm@fh-muenster.de
"""

import logging
import pandas as pd
from oemof import solph
from matplotlib import pyplot as plt
import os
from program_files.postprocessing.create_results_collecting_data import collect_data
from program_files.postprocessing.create_results_prepare_data import prepare_data
import csv


def xlsx(nodes_data: dict, optimization_model: solph.Model, filepath: str):
    """
        Returns model results as xlsx-files.
        Saves the in- and outgoing flows of every bus of a given,
        optimized energy system as .xlsx file

        :param nodes_data: dictionary containing data from excel
                           scenario file
        :type nodes_data: dict
        :param optimization_model: optimized energy system
        :type optimization_model: oemof.solph.model
        :param filepath: path, where the results will be stored
        :type filepath: str
        :return: - **results** (.xlsx) - xlsx files containing in and \
                   outgoing flows of the energy systems' buses.

        Christian Klemm - christian.klemm@fh-muenster.de
    """
    results = solph.processing.results(optimization_model)

    # Writes a spreadsheet containing the input and output flows into
    # every bus of the energy system for every timestep of the
    # timesystem
    for i, b in nodes_data["buses"].iterrows():
        if b["active"]:
            file_path = os.path.join(filepath, "results_" + b["label"] + ".xlsx")
            node_results = solph.views.node(results, b["label"])
            df = node_results["sequences"]
            df.head(2)
            with pd.ExcelWriter(file_path) as writer:  # doctest: +SKIP
                df.to_excel(writer, sheet_name=b["label"])
            # returns logging info
            logging.info("   " + "Results saved as xlsx for " + b["label"])
    # Bus xlsx-files for district heating busses
    results_copy = results.copy()
    components = []
    # iterate threw result keys to find district heating buses
    for i in results.keys():
        if "tag1=" not in str(i):
            results_copy.pop(i)
    # determine only the district heating buses from result_copy
    for i in results_copy.keys():
        if i[0] not in components and i[0] is not None:
            if "bus" in str(i[0]) and "dh_source_link" not in str(i[0]):
                components.append(i[0])
        if i[1] not in components and i[1] is not None:
            if "bus" in str(i[1]) and "dh_source_link" not in str(i[1]):
                components.append(i[1])
    for component in components:
        # renaming label for better file names
        label = str(component).replace("infrastructure_heat_bus", "districtheating")
        label = label.replace("consumers_heat_bus", "districtheating")
        label = label.replace("producers_heat_bus", "districtheating")
        file_path = os.path.join(filepath, "results_" + str(label) + ".xlsx")
        node_results = solph.views.node(results, str(component))
        df = node_results["sequences"]
        df.head(2)
        with pd.ExcelWriter(file_path) as writer:  # doctest: +SKIP
            df.to_excel(writer, sheet_name=label)
        # returns logging info
        logging.info("\t Results saved as xlsx for " + str(label))


def charts(
    nodes_data: dict, optimization_model: solph.Model, energy_system: solph.EnergySystem
):
    """
        Plots model results.

        Plots the in- and outgoing flows of every bus of a given,
        optimized energy system

        :param nodes_data: dictionary containing data from excel
                            scenario file
        :type nodes_data: dict
        :param optimization_model: optimized energy system
        :type optimization_model: oemof.solph.Model
        :param energy_system: original (unoptimized) energy system
        :type energy_system: oemof.solph.Energysystem
        :return: - **plots** (matplotlib.plot) plots displaying in \
                   and outgoing flows of the energy systems' buses.

        Christian Klemm - christian.klemm@fh-muenster.de
    """
    # rename variables
    esys = energy_system
    results = solph.processing.results(optimization_model)

    for i, b in nodes_data["buses"].iterrows():
        if b["active"]:
            logging.info(
                "   " + "******************************************" + "***************"
            )
            logging.info("   " + "RESULTS: " + b["label"])

            bus = solph.views.node(results, b["label"])
            logging.info("   " + bus["sequences"].sum())
            fig, ax = plt.subplots(figsize=(10, 5))
            bus["sequences"].plot(ax=ax)
            ax.legend(
                loc="upper center", prop={"size": 8}, bbox_to_anchor=(0.5, 1.4), ncol=2
            )
            fig.subplots_adjust(top=0.7)
            plt.show()

    esys.results["main"] = solph.processing.results(optimization_model)
    esys.results["meta"] = solph.processing.meta_results(optimization_model)
    esys.dump(dpath=None, filename=None)


class Results:
    """
    Class for preparing Plotly results and logging the results of
    Cbc-Solver
    """

    results = None
    esys = None
    comp_capacity = None
    df_list_of_components = None
    df_result_table = pd.DataFrame()

    @staticmethod
    def get_first_node_flow(flow):
        """returns begin of the flow, used to log where the flow comes from"""
        flow_name = str(flow.name)
        flow_name = flow_name[2:-10]
        flow_name = flow_name.split(",")
        return flow_name[0]

    @staticmethod
    def get_last_node_flow(flow):
        """returns end of the flow, used to log where the flow goes to"""
        flow_name = str(flow.name)
        flow_name = flow_name[2:-10]
        flow_name = flow_name.split(",")
        return flow_name[1]

    def console_logging(
        self,
        comp_type,
        capacity=None,
        variable_costs=None,
        periodical_costs=None,
        investment=None,
        transformer_type=None,
    ):
        """
        consists of the different console logging entries and logs
        the one for the given component
        """

        inflow1 = self.comp_input1
        inflow2 = self.comp_input2
        outflow1 = self.comp_output1
        outflow2 = self.comp_output2

        if comp_type == "sink":
            logging.info("   " + "Total Energy Demand: " + str(inflow1.sum()) + " kWh")
        else:
            if comp_type == "source":
                if inflow1 is None or "shortage" in self.get_first_node_flow(outflow1):
                    logging.info(
                        "   " + "Total Energy Input: " + str(outflow1.sum()) + " kWh"
                    )
                    logging.info("   " + "Max. Capacity: " + str(capacity) + " kW")
                else:
                    logging.info(
                        "   "
                        + "Input from "
                        + self.get_first_node_flow(inflow1)
                        + ": "
                        + str(round(inflow1.sum(), 2))
                        + " kWh"
                    )
                    logging.info(
                        "   "
                        + "Ambient Energy Input to "
                        + self.get_first_node_flow(inflow2)
                        + ": "
                        + str(round(inflow2.sum(), 2))
                        + " kWh"
                    )
                    logging.info(
                        "   "
                        + "Energy Output to "
                        + self.get_last_node_flow(outflow1)
                        + ": "
                        + str(round(outflow1.sum(), 2))
                        + " kWh"
                    )

            if comp_type == "transformer":
                if inflow2 is None:
                    logging.info(
                        "   "
                        + "Total Energy Output to"
                        + self.get_last_node_flow(outflow1)
                        + ": "
                        + str(round(outflow1.sum(), 2))
                        + " kWh"
                    )
                    if outflow2 is not None:
                        logging.info(
                            "   "
                            + "Total Energy Output to"
                            + self.get_last_node_flow(outflow2)
                            + ": "
                            + str(round(outflow2.sum(), 2))
                            + " kWh"
                        )
                else:
                    logging.info(
                        "   "
                        + "Electricity Energy Input to "
                        + self.get_first_node_flow(inflow1)
                        + ": "
                        + str(round(inflow1.sum(), 2))
                        + " kWh"
                    )
                    if transformer_type == "absorption_heat_transformer":
                        logging.info(
                            "   "
                            + "Heat Input to"
                            + self.get_last_node_flow(inflow2)
                            + ": "
                            + str(round(inflow2.sum(), 2))
                            + " kWh"
                        )
                    elif transformer_type == "compression_heat_transformer":
                        logging.info(
                            "   "
                            + "Ambient Energy Input to"
                            + self.get_last_node_flow(inflow2)
                            + ": "
                            + str(round(inflow2.sum(), 2))
                            + " kWh"
                        )
                    logging.info(
                        "   "
                        + "Total Energy Output to"
                        + self.get_last_node_flow(outflow1)
                        + ": "
                        + str(round(outflow1.sum(), 2))
                        + " kWh"
                    )
                logging.info("   " + "Max. Capacity: " + str(capacity) + " kW")

                if comp_type == "storage":
                    logging.info(
                        "   "
                        + "Energy Output from "
                        + self.get_first_node_flow(outflow1)
                        + ": "
                        + str(round(outflow1.sum(), 2))
                        + "kWh"
                    )
                    logging.info(
                        "   "
                        + "Energy Input to "
                        + self.get_last_node_flow(outflow1)
                        + ": "
                        + str(round(inflow1.sum(), 2))
                        + " kWh"
                    )

                if comp_type == "link":
                    if capacity is None:
                        logging.info(
                            "   "
                            + "Total Energy Output to "
                            + self.get_last_node_flow(outflow1)
                            + ": "
                            + str(round(outflow1.sum(), 2))
                            + " kWh"
                        )
                        logging.info(
                            "   "
                            + "Total Energy Output to "
                            + self.get_last_node_flow(outflow2)
                            + ": "
                            + str(round(outflow2.sum(), 2))
                            + " kWh"
                        )
                        logging.info(
                            "   "
                            + "Max. Capacity to "
                            + self.get_last_node_flow(outflow1)
                            + ": "
                            + str(round(outflow1.max(), 2))
                            + " kW"
                        )
                        logging.info(
                            "   "
                            + "Max. Capacity to "
                            + self.get_last_node_flow(outflow2)
                            + ": "
                            + str(round(outflow2.max(), 2))
                            + " kW"
                        )
                    else:
                        logging.info(
                            "   "
                            + "Total Energy Output to "
                            + self.get_last_node_flow(outflow1)
                            + ": "
                            + str(round(outflow1.sum(), 2))
                            + " kWh"
                        )
                        logging.info(
                            "   "
                            + "Max. Capacity to "
                            + self.get_last_node_flow(outflow1)
                            + ": "
                            + str(round(capacity, 2))
                            + " kW"
                        )
            if investment is not None:
                logging.info(
                    "   " + "Investment Capacity: " + str(round(investment, 2)) + " kW"
                )
            if periodical_costs is not None:
                logging.info(
                    "   "
                    + "Periodical costs: "
                    + str(round(periodical_costs, 2))
                    + " cost units p.a."
                )
            logging.info(
                "   "
                + "Variable Costs: "
                + str(round(variable_costs, 2))
                + " cost units"
            )

    @staticmethod
    def insert_line_end_of_component():
        logging.info("\t" + 56 * "-")

    def __init__(
        self,
        nd: dict,
        optimization_model: solph.Model,
        energy_system: solph.EnergySystem,
        result_path: str,
        console_log: bool,
        cluster_dh: bool,
    ):
        """
            Returns a list of all defined components with the following
            information:

            +------------+----------------------------------------------+
            |component   |   information                                |
            +------------+----------------------------------------------+
            |sinks       |   Total Energy Demand                        |
            +------------+----------------------------------------------+
            |sources     |   Total Energy Input, Max. Capacity,         |
            |            |   Variable Costs, Periodical Costs           |
            +------------+----------------------------------------------+
            |transformers|   Total Energy Output, Max. Capacity,        |
            |            |   Variable Costs, Investment Capacity,       |
            |            |   Periodical Costs                           |
            +------------+----------------------------------------------+
            |storages    |   Energy Output, Energy Input, Max. Capacity,|
            |            |   Total variable costs, Investment Capacity, |
            |            |   Periodical Costs                           |
            +------------+----------------------------------------------+
            |links       |   Total Energy Output                        |
            +------------+----------------------------------------------+

            Furthermore, a list of recommended investments is printed.

            The algorithm uses the following steps:

                1. logging the component type for example "sinks"
                2. creating pandas dataframe out of the results of the
                   optimization consisting of every single flow in/out
                   a component
                3. calculating the investment and the costs regarding
                   the flows
                4. adding the component to the list of components (loc)
                   which is part of the plotly dash and is the content
                   of components.csv
                5. logging the component specific text with its parameters
                   in the console

            :param nodes_data: dictionary containing data from excel \
                               scenario file
            :type nodes_data: dict
            :param optimization_model: optimized energy system
            :type optimization_model: oemof.solph.Model
            :param energy_system: original (unoptimized) energy system
            :type energy_system: oemof.solph.Energysystem
            :param result_path: Path where the results are saved.
            :type result_path: str

            Christian Klemm - christian.klemm@fh-muenster.de
            Gregor Becker - gregor.becker@fh-muenster.de
        """

        # remove all old entries from method intern variables
        investments_to_be_made = {}
        total_usage = 0
        # define class variables
        self.esys = energy_system
        self.results = solph.processing.results(optimization_model)
        self.df_result_table = pd.DataFrame()

        comp_dict, total_demand = collect_data(nd, self.results, self.esys, result_path)

        (
            loc,
            total_periodical_costs,
            total_variable_costs,
            total_constraint_costs,
            df_result_table,
            total_demand,
        ) = prepare_data(comp_dict, total_demand, nd, result_path, self.df_result_table)
        # SUMMARY
        meta_results = solph.processing.meta_results(optimization_model)
        meta_results_objective = meta_results["objective"]
        if console_log:
            self.log_category("SUMMARY")
            logging.info(
                "   "
                + "Total System Costs:             "
                + str(round(meta_results_objective, 1))
                + " cost units"
            )
            logging.info(
                "   "
                + "Total Constraint Costs:         "
                + str(round(total_constraint_costs))
                + " cost units"
            )
            logging.info(
                "   "
                + "Total Variable Costs:           "
                + str(round(total_variable_costs))
                + " cost units"
            )
            logging.info(
                "   "
                + "Total Periodical Costs (p.a.):  "
                + str(round(total_periodical_costs))
                + " cost units p.a."
            )
            logging.info(
                "   "
                + "Total Energy Demand:            "
                + str(round(total_demand))
                + " kWh"
            )
            logging.info(
                "   "
                + "Total Energy Usage:             "
                + str(round(total_usage))
                + " kWh"
            )
            # creating the list of investments to be made
            self.insert_line_end_of_component()
            logging.info("   " + "Investments to be made:")
            investment_objects = list(investments_to_be_made.keys())
            for i in range(len(investment_objects)):
                logging.info(
                    "   - "
                    + investment_objects[i]
                    + ": "
                    + investments_to_be_made[investment_objects[i]]
                )
            logging.info("   " + 56 * "*" + "\n")

        # Importing time system parameters from the scenario
        ts = next(nd["energysystem"].iterrows())[1]
        temp_resolution = ts["temporal resolution"]
        start_date = ts["start date"]
        end_date = ts["end date"]

        df_summary = pd.DataFrame(
            [
                [
                    start_date,
                    end_date,
                    temp_resolution,
                    round(meta_results_objective, 2),
                    round(total_constraint_costs, 2),
                    round(total_variable_costs, 2),
                    round(total_periodical_costs, 2),
                    round(total_demand, 2),
                    round(total_usage, 2),
                ]
            ],
            columns=[
                "Start Date",
                "End Date",
                "Resolution",
                "Total System Costs",
                "Total Constraint Costs",
                "Total Variable Costs",
                "Total Periodical Costs",
                "Total Energy Demand",
                "Total Energy Usage",
            ],
        )

        # Dataframes are exported as csv for further processing
        loc.to_csv(result_path + "/components.csv", index=False)

        df_result_table = df_result_table.rename_axis("date")
        df_result_table.to_csv(result_path + "/results.csv")

        df_summary.to_csv(result_path + "/summary.csv", index=False)

        logging.info("   " + "Successfully prepared results...")
