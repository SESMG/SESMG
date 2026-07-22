"""
    Christian Klemm - christian.klemm@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
    Oscar Quiroga - oscar.quiroga@fh-muenster.de
"""

import logging
import pandas as pd
from oemof import solph
from matplotlib import pyplot as plt
import os
from program_files.postprocessing.create_results_collecting_data \
    import collect_data
from program_files.postprocessing.create_results_prepare_data \
    import prepare_data


def xlsx(nodes_data: dict, optimization_model: solph.Model, filepath: str) -> None:
    """
    Returns model results as xlsx-files.
    Saves the in- and outgoing flows of every bus of a given,
    optimized energy system as .xlsx file

    :param nodes_data: dictionary containing data from excel
        model definition file
    :type nodes_data: dict
    :param optimization_model: optimized energy system
    :type optimization_model: oemof.solph.model
    :param filepath: path, where the results will be stored
    :type filepath: str
    """
    results = solph.processing.results(optimization_model)

    for i, b in nodes_data["buses"].iterrows():
        if b["active"]:
            file_path = os.path.join(filepath, "results_" + b["label"] + ".xlsx")
            
            node_results = solph.views.node(results, b["label"])
            
            if "sequences" not in node_results:
                logging.warning(f"No sequence results found for bus '{b['label']}', skipping.")
                continue
            
            df = node_results["sequences"]
            

            with pd.ExcelWriter(file_path) as writer:
                df = df.copy()

                # Remove time zone from the index if it exists
                if df.index.tz is not None:
                    df.index = df.index.tz_localize(None)

                # Remove column time zone (just in case)
                for col in df.columns:
                    if pd.api.types.is_datetime64_any_dtype(df[col]):
                        try:
                            df[col] = df[col].dt.tz_localize(None)
                        except Exception:
                            pass

                df.to_excel(writer, sheet_name="Sheet1")


def charts(nodes_data: dict, optimization_model: solph.Model,
           energy_system: solph.EnergySystem) -> None:
    """
        Plots model results in- and outgoing flows of every bus of a
        given, optimized energy system (based on matplotlib)

        :param nodes_data: dictionary containing data from excel \
            model definition file
        :type nodes_data: dict
        :param optimization_model: optimized energy system
        :type optimization_model: oemof.solph.Model
        :param energy_system: original (unoptimized) energy system
        :type energy_system: oemof.solph.Energysystem
    """
    # rename variables
    esys = energy_system
    results = solph.processing.results(optimization_model)

    for num, bus in nodes_data["buses"].iterrows():
        if bus["active"]:
            logging.info('\t ' + 56 * '*')
            logging.info("   " + "RESULTS: " + bus["label"])

            bus = solph.views.node(results, bus["label"])
            logging.info("\t" + bus["sequences"].sum())
            fig, ax = plt.subplots(figsize=(10, 5))
            bus["sequences"].plot(ax=ax)
            ax.legend(
                loc="upper center",
                prop={"size": 8},
                bbox_to_anchor=(0.5, 1.4),
                ncol=2
            )
            fig.subplots_adjust(top=0.7)
            plt.show()

    esys.results["main"] = solph.processing.results(optimization_model)
    esys.results["meta"] = solph.processing.meta_results(optimization_model)
    esys.dump(dpath=None, filename=None)


def get_time_increment_from_index(energy_system: solph.EnergySystem) -> float:
    """
        Returns the temporal resolution of the given EnergySystem in hours.

        The time increment is derived from the EnergySystem.timeindex,
        assuming an equidistant index. It is used to convert power values
        defined per time step (e.g. kW) into energy values (e.g. kWh)
        by multiplication with the time increment.

        :param energy_system: original (unoptimized) energy system
        :type energy_system: oemof.solph.EnergySystem

        :return: - **time_increment** (float) - length of one time step
                  in hours as derived from the EnergySystem.timeindex
    """
    timeindex = energy_system.timeindex

    # default
    time_increment = 1

    if len(timeindex) < 2:
        raise ValueError(
            "EnergySystem.timeindex must contain at least two entries "
            "to derive a time increment."
        )

    # Handle datetime indices
    if isinstance(timeindex, pd.DatetimeIndex):
        # calculates difference between two timeindexes
        diffs = timeindex.to_series().diff().iloc[1:]
        # Ensure that the timeindex is equidistant
        if not (diffs == diffs.iloc[0]).all():
            raise ValueError(
                "Non-equidistant timeindex detected. "
                "get_time_increment_from_index requires an "
                "equidistant timeindex."
            )
        delta = diffs.iloc[0]
        time_increment = delta.total_seconds() / 3600.0

    return time_increment


class Results:
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

        :param nodes_data: dictionary containing data from excel \
            model definition file
        :type nodes_data: dict
        :param optimization_model: optimized energy system
        :type optimization_model: oemof.solph.Model
        :param energy_system: original (unoptimized) energy system
        :type energy_system: oemof.solph.Energysystem
        :param result_path: Path where the results are saved.
        :type result_path: str
        :param variable_cost_factor: factor that considers the data_preparation_algorithms,
            can be used to scale the results up for a year
        :type variable_cost_factor: float
        :param console_log: boolean which decides rather the results \
            will be logged in the console or not
        :type console_log: bool
        :param cluster_dh: boolean which decides rather the thermal \
            network was spatially clustered or not
        :type cluster_dh: bool
    """

    results = None
    esys = None
    comp_capacity = None
    df_list_of_components = None
    df_result_table = None

    def __init__(
        self,
        nodes_data: dict,
        optimization_model: solph.Model,
        energy_system: solph.EnergySystem,
        result_path: str,
        variable_cost_factor: float,
        console_log: bool,
        cluster_dh: bool,
    ):
        """
            Inits the Results class.
        """

        # remove all old entries from method intern variables
        investments_to_be_made = {}
        # define class variables
        self.esys = energy_system
        self.results = solph.processing.results(optimization_model)

        # Derive the length of one time step in hours from the EnergySystem
        # timeindex. This value is used to convert power-based flow values
        # into energy when summing over time.
        time_increment = get_time_increment_from_index(self.esys)

        # collect the energy system results which have to be extracted
        # from the component specific result object
        comp_dict, total_demand, total_usage = collect_data(
            nodes_data=nodes_data,
            results=self.results,
            esys=self.esys,
            result_path=result_path,
            variable_cost_factor=variable_cost_factor,
            time_increment=time_increment
        )

        (
            loc,
            total_periodical_costs,
            total_variable_costs,
            total_constraint_costs,
            df_result_table,
            total_demand,
            flow_info_df,
        ) = prepare_data(comp_dict=comp_dict,
                         total_demand=total_demand,
                         nodes_data=nodes_data,
                         variable_cost_factor=variable_cost_factor,
                         time_increment =  time_increment)
        
        # SUMMARY
        meta_results = solph.processing.meta_results(optimization_model)
        meta_results_objective = meta_results["objective"]

        # Importing time system parameters from the model definition
        ts = next(nodes_data["energysystem"].iterrows())[1]
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
                    variable_cost_factor,
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
                "Variable Cost Factor"
            ],
        )

        # Dataframes are exported as csv for further processing
        loc.to_csv(result_path + "/components.csv", index=False)

        df_result_table = df_result_table.rename_axis("date")
        df_result_table.to_csv(result_path + "/results.csv")

        df_summary.to_csv(result_path + "/summary.csv", index=False)

        flow_info_df.to_csv(result_path + "/flow_information.csv", index=False)

        logging.info("   " + "Successfully prepared results...")
