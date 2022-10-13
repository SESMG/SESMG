# -*- coding: utf-8 -*-
"""
Spreadsheet-Energy-System-Model-Generator.

creates an energy system from a given spreadsheet data file, solves it
for the purpose of least cost optimization, and returns the optimal
scenario results.

The scenario.xlsx-file must contain the following elements:

+-------------+--------------------------------------------------------+
|sheet        | columns                                                |
+=============+========================================================+
|energysystem | start_date, end_date, holidays, temporal resolution,   |
|             | timezone                                               |
+-------------+--------------------------------------------------------+
|buses        | label, active, excess, shortage,                       |
|             | shortage costs /(CU/kWh), excess costs /(CU/kWh)       |
+-------------+--------------------------------------------------------+
|sinks        | label, active, input, input2, load profile,            |
|             | nominal value /(kW), annual demand /(kWh/a),           |
|             | occupants [RICHARDSON], building class [HEAT SLP ONLY],|
|             | wind class [HEAT SLP ONLY], fixed                      |
+-------------+--------------------------------------------------------+
|sources      | label, active, output, technology,                     |
|             | variable costs /(CU/kWh), existing capacity /(kW),     |
|             | min. investment capacity /(kW),                        |
|             | max. investment capacity /(kW),                        |
|             | periodical costs /(CU/(kW a)),                         |
|             | technology database (PV ONLY),                         |
|             | inverter database (PV ONLY), Modul Model (PV ONLY),    |
|             | Inverter Model (PV ONLY), reference value /(kW),       |
|             | Azimuth (PV ONLY), Surface Tilt (PV ONLY),             |
|             | Albedo (PV ONLY), Altitude (PV ONLY),                  |
|             | Latitude (PV ONLY), Longitude (PV ONLY)                |
+-------------+--------------------------------------------------------+
|transformers | label, active, transformer type, input, output,        |
|             | output2, efficiency, efficiency2,                      |
|             | variable input costs /(CU/kWh),                        |
|             | variable output costs /(CU/kWh),                       |
|             | existing capacity /(kW),                               |
|             | max. investment capacity /(kW),                        |
|             | min. investment capacity /(kW),                        |
|             | periodical costs /(CU/(kW a))                          |
+-------------+--------------------------------------------------------+
|storages     | label, active, bus, existing capacity /(kW),           |
|             | min. investment capacity /(kW),                        |
|             | max. investment capacity /(kW),                        |
|             | periodical costs /(CU/(kW a)), capacity inflow,        |
|             | capacity outflow, capacity loss, efficiency inflow,    |
|             | efficiency outflow, initial capacity, capacity min,    |
|             | capacity max, variable input costs,                    |
|             | variable output costs                                  |
+-------------+--------------------------------------------------------+
|powerlines   | label, active, bus_1, bus_2, (un)directed, efficiency, |
|             | existing capacity /(kW),                               |
|             | min. investment capacity /(kW),                        |
|             | max. investment capacity /(kW),                        |
|             | variable costs /(CU/kWh), periodical costs /(CU/(kW a))|
+-------------+--------------------------------------------------------+
|time_series  | timestamp,                                             |
|             | timeseries for components with fixed input or output   |
+-------------+--------------------------------------------------------+
|weather_data | dates(untitled), dhi, dirhi, pressure, temp_air,       |
|             | windspeed, z0                                          |
+-------------+--------------------------------------------------------+


Docs:
 - https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/
 
GIT:
 - https://github.com/chrklemm/SESMG
 
-------------------------------------------------------------------------------


Christian Klemm - christian.klemm@fh-muenster.de
"""
import logging
from oemof.tools import logger
import os
from threading import *
import sys
from program_files.preprocessing import (
    create_energy_system,
    data_preparation,
)
from program_files.preprocessing.create_graph import ESGraphRenderer
from program_files.preprocessing.components import (
    Sink,
    Transformer,
    Source,
    Storage,
    Link,
    Bus,
    district_heating,
)
from program_files.postprocessing import create_results
from program_files.processing import optimize_model


def sesmg_main(
    scenario_file: str,
    result_path: str,
    num_threads: int,
    graph: bool,
    criterion_switch: bool,
    xlsx_results: bool,
    console_results: bool,
    timeseries_prep: list,
    solver: str,
    cluster_dh,
    district_heating_path=None,
):
    """
    Main function of the Spreadsheet System Model Generator

    :param scenario_file: The scenario_file must contain the
                          components specified above.
    :type scenario_file: str ['xlsx']
    :param result_path: path of the folder where the results
                        will be saved
    :type result_path: str ['folder']
    :param num_threads: number of threads that the method may use
    :type num_threads: int
    :param graph: defines if the graph should be created
    :type graph: bool
    :param results: defines if the results should be created
    :type results: bool
    :param plotly: defines if the plotly dash should be started
    :type plotly: bool

    Christian Klemm - christian.klemm@fh-muenster.de
    """
    # SETS NUMBER OF THREADS FOR NUMPY
    os.environ["NUMEXPR_NUM_THREADS"] = str(num_threads)
    # DEFINES A LOGGING FILE
    logger.define_logging(logpath=result_path)
    # IMPORTS DATA FROM THE EXCEL FILE AND RETURNS IT AS DICTIONARY
    nodes_data = create_energy_system.import_scenario(filepath=scenario_file)

    # CRITERION SWITCH
    if criterion_switch:
        data_preparation.change_optimization_criterion(nodes_data)

    if sys.platform.startswith("win"):
        scheme_path = os.path.join(
            os.path.dirname(__file__) + r"\technical_data\hierarchical_selection"
            r"_schemes.xlsx"
        )
    else:
        scheme_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__))
            + r"/technical_data/hierarchical_selection"
            r"_schemes.xlsx"
        )
    # Timeseries Preprocessing
    data_preparation.timeseries_preparation(
        timeseries_prep_param=timeseries_prep,
        nodes_data=nodes_data,
        scheme_path=scheme_path,
        result_path=result_path,
    )

    if timeseries_prep[0] != "none":
        scenario_file = result_path + "/modified_scenario.xlsx"

    # CREATES AN ENERGYSYSTEM AS DEFINED IN THE SCENARIO FILE
    esys = create_energy_system.define_energy_system(nodes_data=nodes_data)

    weather_data = nodes_data["weather data"]
    time_series = nodes_data["timeseries"]

    # CREATES AN LIST OF COMPONENTS
    nodes = []

    # CREATES BUS OBJECTS, EXCESS SINKS, AND SHORTAGE SOURCES AS DEFINED IN THE
    # SCENARIO FILE AND ADDS THEM TO THE lIST OF COMPONENTS
    busd = Bus.buses(nd=nodes_data, nodes=nodes)
    # PARALLEL CREATION OF ALL OBJECTS OF THE SCENARIO FILE

    # CREATES SOURCE OBJECTS AS DEFINED IN THE SCENARIO FILE AND ADDS THEM TO
    # THE lIST OF COMPONENTS
    t1 = Thread(target=Source.Sources, args=(nodes_data, nodes, busd))
    t1.start()
    # CREATES SINK OBJECTS AS DEFINED IN THE SCENARIO FILE AND ADDS THEM TO
    # THE lIST OF COMPONENTS
    t2 = Thread(target=Sink.Sinks, args=(nodes_data, busd, nodes))
    t2.start()
    # CREATES TRANSFORMER OBJECTS AS DEFINED IN THE SCENARIO FILE AND ADDS THEM
    # TO THE lIST OF COMPONENTS
    t3 = Thread(target=Transformer.Transformers, args=(nodes_data, nodes, busd))
    t3.start()
    # CREATES STORAGE OBJECTS AS DEFINED IN THE SCENARIO FILE AND ADDS THEM TO
    # THE lIST OF COMPONENTS
    t4 = Thread(target=Storage.Storages, args=(nodes_data, nodes, busd))
    t4.start()
    # CREATES LINK OBJECTS AS DEFINED IN THE SCENARIO FILE AND ADDS THEM TO
    # THE lIST OF COMPONENTS
    t5 = Thread(target=Link.Links, args=(nodes_data, nodes, busd))
    t5.start()

    # WAIT UNTIL THE THREADS HAVE DONE THEIR JOBS
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    
    # exergy district heating network
    nodes = district_heating.district_heating(
        nodes_data, nodes, busd, district_heating_path, result_path, cluster_dh, False
    )
    
    # anergy district heating network
    # nodes = district_heating.district_heating(
    #    nodes_data, nodes, busd, district_heating_path, result_path,
    #    cluster_dh, True
    #)
    

    # ADDS THE COMPONENTS TO THE ENERGYSYSTEM
    esys.add(*nodes)
    ESGraphRenderer(energy_system=esys, filepath=result_path, view=graph, legend=True)
    # PRINTS A GRAPH OF THE ENERGY SYSTEM

    # OPTIMIZES THE ENERGYSYSTEM AND RETURNS THE OPTIMIZED ENERGY SYSTEM
    om = optimize_model.least_cost_model(esys, num_threads, nodes_data, busd, solver)

    # SHOWS AND SAVES RESULTS OF THE OPTIMIZED MODEL / POST-PROCESSING
    if xlsx_results:
        create_results.xlsx(
            nodes_data=nodes_data, optimization_model=om, filepath=result_path
        )
    # CREATES PLOTLY RESULTS AND LOGS RESULTS OF CBC SOLVER
    create_results.Results(
        nodes_data,
        om,
        esys,
        result_path,
        console_log=console_results,
        cluster_dh=cluster_dh,
    )

    logging.info("\t " + 56 * "-")
    logging.info("\t Modelling and optimization successfully completed!")
    
    
def sesmg_main_including_premodel(scenario_file: str, result_path: str, num_threads: int,
               graph: bool, criterion_switch: bool, xlsx_results: bool,
               console_results: bool, timeseries_prep: list, solver: str,
               cluster_dh, pre_model_timeseries_prep: list, investment_boundaries: bool,
               investment_boundary_factor: int, pre_model_path: str, district_heating_path=None):
    # Create Sub-Folders in the results-repository
    os.mkdir(pre_model_path)
    # Start Pre-Modeling Run
    print('STARTING PRE-MODEL')
    sesmg_main(
        scenario_file=scenario_file,
        result_path=pre_model_path,
        num_threads=num_threads,
        timeseries_prep=pre_model_timeseries_prep,
        graph=graph,
        criterion_switch=criterion_switch,
        xlsx_results=xlsx_results,
        console_results=console_results,
        solver=solver,
        district_heating_path=district_heating_path,
        cluster_dh=cluster_dh)

    # create updated scenario for main-modeling run
    print('UPDATING DATA BASED ON PRE-MODEL RESULTS')
    update_model_according_pre_model_results(
        scenario_path=scenario_file,
        results_components_path=pre_model_path + '/components.csv',
        updated_scenario_path=result_path + '/updated_scenario.xlsx',
        investment_boundary_factor=investment_boundary_factor,
        investment_boundaries=investment_boundaries)

    # start main-modeling run
    print('STARTING MAIN-MODEL')
    sesmg_main(
        scenario_file=result_path + '/updated_scenario.xlsx',
        result_path=result_path,
        num_threads=num_threads,
        timeseries_prep=timeseries_prep,
        graph=graph,
        criterion_switch=criterion_switch,
        xlsx_results=xlsx_results,
        console_results=console_results,
        solver=solver,
        district_heating_path=district_heating_path,
        cluster_dh=cluster_dh)
    
