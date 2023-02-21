# -*- coding: utf-8 -*-
"""
Spreadsheet-Energy-System-Model-Generator.

creates an energy system from a given spreadsheet data file, solves it
for the purpose of least cost optimization, and returns the optimal
scenario results.

The model_definition.xlsx-file must contain the following elements:

+-------------+--------------------------------------------------------+
|sheet        | columns                                                |
+=============+========================================================+
|energysystem | start date (DD.MM.YYYY HH.MM.SS),                      |
|             | end_date (DD.MM.YYYY HH.MM.SS),                        |
|             | temporal resolution,                                   |
|             | periods, constraint costs (CU),                        |
|             | minimal final energy (kWh),                            |
|             | weather data lon. (WGS84),                             |
|             | weather data lat. (WGS84)                              |
+-------------+--------------------------------------------------------+
|buses        | label,                                                 |
|             | active (0 or 1), excess (0 or 1), shortage (0 or 1),   |
|             | excess costs (CU/kWh), shortage costs (CU/kWh),        |
|             | excess constraint costs (CU/kWh),                      |
|             | shortage constraint costs (CU/kWh),                    |
|             | district heating conn. (0 or 1 or dh-system),          |
|             | lat (WGS84), lon(WGS84)                                |
+-------------+--------------------------------------------------------+
|sinks        | label, active (0 or 1), fixed (0 or 1),                |
|             | input (bus label), load profile, nominal value (kW),   |
|             | annual demand (kWh/a), occupants (int [RICHARDSON]),   |
|             | building class [HEAT SLP], wind class [HEAT SLP]       |
+-------------+--------------------------------------------------------+
|sources      | label, active (0 or 1), fixed (0 or 1), technology,    |
|             | output (bus label), input (bus label [ST ONLY]),       |
|             | existing capacity (kW), min. investment capacity (kW), |
|             | max. investment capacity (kW),                         |
|             | non-convex investment (0 or 1),                        |
|             | fix investment costs (CU/a),                           |
|             | fix investment constraint costs (CU/a)                 |
|             | variable costs (CU/kWh), periodical costs (CU/(kW a)), |
|             | variable constraint costs (CU/kWh),                    |
|             | periodical constraint costs (CU/(kW a)),               |
|             | Tubine Model [WINDPOWER], Hub Height [WINDPOWER],      |
|             | technology database [PV], inverter database [PV],      |
|             | Modul Model [PV], Inverter Model [PV], Albedo [PV],    |
|             | Azimuth [PV or ST], Altitude [PV or ST],               |
|             | Surface Tilt [PV or ST],                               |
|             | Latitude [PV or ST], Longitude [PV or ST], ETA0 [ST],  |
|             | A1 [ST], A2 [ST], C1 [ST], C2 [ST],                    |
|             | Temperature Inlet [ST], Temperature Difference [ST],   |
|             | Conversion Factor [ST], Peripheral Losses [ST],        |
|             | Electric Consumption [ST], Cleanliness [ST]            |
+-------------+--------------------------------------------------------+
|competition  | active (0 or 1),                                       |
|constraints  | component 1 (component label), factor 1,               |
|             | component 2 (component label), factor 2                |
+-------------+--------------------------------------------------------+
|transformers | label, active (0 or 1), transformer type, mode,        |
|             | input (bus label), input 2 (bus label),                |
|             | output (bus label), output2 (bus label), input2/input, |
|             | efficiency, efficiency2, existing capacity (kW),       |
|             | min. investment capacity (kW),                         |
|             | max. investment capacity (kW),                         |
|             | non-convex investment (0 or 1),                        |
|             | fix investment costs (CU/a),                           |
|             | fix investment constraint costs (CU/a),                |
|             | variable input costs (CU/kWh),                         |
|             | variable input costs 2 (CU/kWh),                       |
|             | variable output costs (CU/kWh),                        |
|             | variable output costs 2 (CU/kWh),                      |
|             | periodical costs (CU/(kW a)),                          |
|             | variable input constraint costs (CU/kWh),              |
|             | variable input constraint costs 2 (CU/kWh),            |
|             | variable output constraint costs (CU/kWh),             |
|             | variable output constraint costs 2 (CU/kWh),           |
|             | periodical constraint costs (CU/(kW a)),               |
|             | heat source, temperature high [HEAT PUMP],             |
|             | temperature low [CHILLER], quality grade, area (sqm),  |
|             | length of geoth. probe, heat extraction,               |
|             | min. borehole area, temp. threshold icing,             |
|             | factor icing, name, TODO high temperature (duplication)|
|             | TODO chilling temperature (duplication),               |
|             | electric input conversion factor [Absorption],         |
|             | recooling temperature difference [Absorption],         |
|             | min. share of flue gas loss [GenericCHP],              |
|             | max. share of flue gas loss [GenericCHP],              |
|             | min. electric power [GenericCHP],                      |
|             | max. electric power [GenericCHP],                      |
|             | min. electric efficiency [GenericCHP],                 |
|             | max. electric efficiency [GenericCHP],                 |
|             | minimal thermal output [GenericCHP],                   |
|             | elec. power loss index [GenericCHP],                   |
|             | back pressure [GenericCHP]                             |
+-------------+--------------------------------------------------------+
|storages     | label, active (0 or 1), storage type, bus (bus label), |
|             | input/capacity ration, output/capacity ratio,          |
|             | efficiency inflow, efficiency outflow,                 |
|             | initial capacity, capacity min, capacity max,          |
|             | existing capacity (kW), min. investment capacity (kW), |
|             | max. investment capacity (kW),                         |
|             | non-convex investment (0 or 1),                        |
|             | fix investment costs (CU/a),                           |
|             | fix investment constraint costs (CU/a),                |
|             | variable input costs (CU/kWh),                         |
|             | variable output costs (CU/kWh),                        |
|             | periodical costs (CU/(kW a)),                          |
|             | variable input constraint costs (CU/kWh),              |
|             | variable output constraint costs (CU/kWh),             |
|             | periodical constraint costs (CU/(kW a)),               |
|             | capacity loss [GENERIC], diameter [STRATIFIED],        |
|             | temperature high [STRATIFIED],                         |
|             | temperature low [STRATIFIED], U-value [STRATIFIED]     |
+-------------+--------------------------------------------------------+
|links        | label, active (0 or 1), (un)directed, bus1 (bus label),|
|             | bus2 (bus label), efficiency, existing capacity (kW),  |
|             | min. investment capacity (kW),                         |
|             | max. investment capacity (kW),                         |
|             | non-convex investment (0 or 1),                        |
|             | fix investment costs (CU/a),                           |
|             | fix investment constraint costs (CU/a),                |
|             | variable output costs (CU/kWh),                        |
|             | periodical costs (CU/(kW a)),                          |
|             | variable output constraint costs (CU/kWh),             |
|             | periodical constraint costs (CU/(kW a))                |
+-------------+--------------------------------------------------------+
|insulation   | label, active (0 or 1), sink (sink label),             |
|             | temperature indoor (°C), heat limit temperature (°C),  |
|             | U-value old (W/(sqm K)), U-value new (W/(sqm K)),      |
|             | area (sqm), periodical costs (CU/(sqm a)),             |
|             | periodical constraint costs (CU/(sqm a))               |
+-------------+--------------------------------------------------------+
|district     | label, active (0 or 1), lat. 1st intersection (WGS84), |
|heating      | lat. 2nd intersection (WGS84),                         |
|             | lon. 1st intersection (WGS84),                         |
|             | lon. 2nd intersection (WGS84)                          |
+-------------+--------------------------------------------------------+
|time series  | timestamp,                                             |
|             | timeseries for components with fixed input or output   |
+-------------+--------------------------------------------------------+
|weather data | timestamp, dhi, dni, ghi, pressure, temperature,       |
|             | windspeed, z0, temperature, ground temp, water temp,   |
|             | groundwater temp                                       |
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
import pandas as pd
from threading import *
import sys
from program_files.preprocessing import (create_energy_system,
                                         data_preparation)
from program_files.preprocessing.components import (
    district_heating, Bus, Source, Sink, Transformer, Storage, Link)
from program_files.preprocessing.create_graph import ESGraphRenderer
from program_files.postprocessing import create_results
from program_files.processing import optimize_model
from program_files.preprocessing.pre_model_analysis import update_model_according_pre_model_results


def sesmg_main(scenario_file: str, result_path: str, num_threads: int,
               criterion_switch: bool, xlsx_results: bool,
               console_results: bool, timeseries_prep: list, solver: str,
               cluster_dh, graph=False, district_heating_path=None):
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
    os.environ['NUMEXPR_NUM_THREADS'] = str(num_threads)
    # DEFINES A LOGGING FILE
    logger.define_logging(logpath=result_path)
    # IMPORTS DATA FROM THE EXCEL FILE AND RETURNS IT AS DICTIONARY
    nodes_data = create_energy_system.import_model_definition(
        filepath=scenario_file)

    # CRITERION SWITCH
    if criterion_switch:
        data_preparation.change_optimization_criterion(nodes_data)

    if sys.platform.startswith("win"):
        scheme_path = \
            os.path.join(os.path.dirname(__file__)
                         + r'\technical_data\hierarchical_selection'
                           r'_schemes.xlsx')
    else:
        scheme_path = \
            os.path.join(os.path.dirname(os.path.dirname(__file__))
                         + r'/technical_data/hierarchical_selection'
                           r'_schemes.xlsx')
    # Timeseries Preprocessing
    data_preparation.timeseries_preparation(timeseries_prep_param=timeseries_prep,
                                            nodes_data=nodes_data,
                                            scheme_path=scheme_path,
                                            result_path=result_path)

    if timeseries_prep[0] != 'none':
        scenario_file = result_path + "/modified_scenario.xlsx"

    # CREATES AN ENERGYSYSTEM AS DEFINED IN THE SCENARIO FILE
    esys = create_energy_system.define_energy_system(nodes_data=nodes_data)

    weather_data = nodes_data['weather data']
    time_series = nodes_data['timeseries']

    # CREATES AN LIST OF COMPONENTS
    nodes = []

    # CREATES BUS OBJECTS, EXCESS SINKS, AND SHORTAGE SOURCES AS DEFINED IN THE
    # SCENARIO FILE AND ADDS THEM TO THE lIST OF COMPONENTS
    busd = Bus.buses(nodes_data=nodes_data, nodes=nodes)
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
    t3 = Thread(target=Transformer.Transformers,
                args=(nodes_data, nodes, busd))
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
    
    nodes = district_heating.district_heating(nodes_data, nodes, busd,
                                              district_heating_path,
                                              result_path, cluster_dh, False)
    # ADDS THE COMPONENTS TO THE ENERGYSYSTEM
    esys.add(*nodes)
    ESGraphRenderer(energy_system=esys, filepath=result_path, view=graph,
                    legend=True)
    # OPTIMIZES THE ENERGYSYSTEM AND RETURNS THE OPTIMIZED ENERGY SYSTEM
    om = optimize_model.least_cost_model(esys, num_threads, nodes_data, busd,
                                         solver)

    # SHOWS AND SAVES RESULTS OF THE OPTIMIZED MODEL / POST-PROCESSING
    if xlsx_results:
        create_results.xlsx(nodes_data=nodes_data, optimization_model=om,
                            filepath=result_path)
    # CREATES PLOTLY RESULTS AND LOGS RESULTS OF CBC SOLVER
    create_results.Results(nodes_data, om, esys, result_path,
                           console_log=console_results, cluster_dh=cluster_dh)

    logging.info('\t ' + 56 * '-')
    logging.info('\t Modelling and optimization successfully completed!')


def sesmg_main_including_premodel(scenario_file: str, result_path: str, num_threads: int,
               graph: bool, criterion_switch: bool, xlsx_results: bool,
               console_results: bool, timeseries_prep: list, solver: str,
               cluster_dh, pre_model_timeseries_prep: list, investment_boundaries: bool,
               investment_boundary_factor: int, pre_model_path: str, district_heating_path=None):
    # Create Sub-Folders in the results-repository
    os.mkdir(result_path + str('/pre_model'))
    # Start Pre-Modeling Run
    print('STARTING PRE-MODEL')

    print(scenario_file)
    print(result_path + str('/pre_model'))
    print(num_threads)
    print(pre_model_timeseries_prep)
    print(graph)
    print(criterion_switch)
    print(xlsx_results)
    print(console_results)
    print(solver)
    print(district_heating_path)
    print(cluster_dh)

    sesmg_main(
        scenario_file=scenario_file,
        result_path=result_path + str('/pre_model'),
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
        results_components_path=result_path + '/pre_model/components.csv',
        updated_scenario_path=result_path + '/updated_scenario.xlsx',
        investment_boundary_factor=investment_boundary_factor,
        investment_boundaries=investment_boundaries)

    # start main-modeling run
    print('STARTING MAIN-MODEL')

    print(result_path + '/updated_scenario.xlsx')
    print(result_path)
    print(num_threads)
    print(timeseries_prep)
    print(graph)
    print(criterion_switch)
    print(xlsx_results)
    print(console_results)
    print(solver)
    print(district_heating_path)
    print(cluster_dh)

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
