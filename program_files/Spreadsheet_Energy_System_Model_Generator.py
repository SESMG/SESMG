# -*- coding: utf-8 -*-
"""Spreadsheet-Energy-System-Model-Generator.

creates an energy system from a given spreadsheet data file, solves it
for the purpose of least cost optimization, and returns the optimal
scenario results.

The scenario.xlsx-file must contain the following elements:
    
sheet        | columns
------------------------------------------------------------------------
timesystem   |  start_date, end_date, holidays, temporal resolution,
                timezone

buses        |  label, active, excess, shortage,
                shortage costs /(CU/kWh), excess costs /(CU/kWh)
               
sinks        |  label, active, input, input2, load profile,
                nominal value /(kW), annual demand /(kWh/a),
                occupants [RICHARDSON], building class [HEAT SLP ONLY],
                wind class [HEAT SLP ONLY], fixed
               
sources      |  label, active, output, technology,
                variable costs /(CU/kWh), existing capacity /(kW),
                min. investment capacity /(kW),
                max. investment capacity /(kW),
                periodical costs /(CU/(kW a)),
                technology database (PV ONLY),
                inverter database (PV ONLY), Modul Model (PV ONLY),
                Inverter Model (PV ONLY), reference value /(kW),
                Azimuth (PV ONLY), Surface Tilt (PV ONLY),
                Albedo (PV ONLY), Altitude (PV ONLY),
                Latitude (PV ONLY), Longitude (PV ONLY)
               
transformers |  label, active, transformer type, input, output, output2,
                efficiency, efficiency2, variable input costs /(CU/kWh),
                variable output costs /(CU/kWh),
                existing capacity /(kW), max. investment capacity /(kW),
                min. investment capacity /(kW),
                periodical costs /(CU/(kW a))
               
storages     |  label, active, bus, existing capacity /(kW),
                min. investment capacity /(kW),
                max. investment capacity /(kW),
                periodical costs /(CU/(kW a)), capacity inflow,
                capacity outflow, capacity loss, efficiency inflow,
                efficiency outflow, initial capacity, capacity min,
                capacity max, variable input costs,
                variable output costs
               
powerlines   |  label, active, bus_1, bus_2, (un)directed, efficiency,
                existing capacity /(kW), min. investment capacity /(kW),
                max. investment capacity /(kW),
                variable costs /(CU/kWh), periodical costs /(CU/(kW a))
               
time_series  |  timestamp,
                timeseries for components with fixed input or output

weather_data |  dates(untitled), dhi, dirhi, pressure, temp_air,
                windspeed, z0

-------------------------------------------------------------------------------
Docs:
https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/
GIT:
https://git.fh-muenster.de/ck546038/spreadsheet-energy-system-model-generator
-------------------------------------------------------------------------------

@ Christian Klemm - christian.klemm@fh-muenster.de, 13.03.2020
"""
import logging
from oemof.tools import logger
import os
from threading import *
from program_files import (create_objects,
                           create_results,
                           create_energy_system,
                           optimize_model,
                           create_graph)


def sesmg_main(scenario_file, result_path, num_threads, graph, results,
               plotly):
    """
    Main function of the Spreadsheet System Model Generator
    ----
    Keyword arguments:
        scenario_file: obj:'xlsx'
        -- The scenario_file must contain the components specified
        above.
        
        result_path: obj:'str'
        -- path of the folder where the results will be saved
        
        num_threads: obj:'int'
        -- number of threads that the method may use

        graph: obj:'bool'
        -- defines if the graph should be created

        results: obj: 'bool'
        -- defines if the results should be created

        plotly: obj: 'bool'
        -- defines if the plotly dash should be started
    """
    # SETS NUMBER OF THREADS FOR NUMPY
    os.environ['NUMEXPR_NUM_THREADS'] = str(num_threads)
    # DEFINES A LOGGING FILE
    logger.define_logging(logpath=result_path)
    # IMPORTS DATA FROM THE EXCEL FILE AND RETURNS IT AS DICTIONARY
    nodes_data = create_energy_system.import_scenario(filepath=scenario_file)

    # formatting of the weather data record according to the
    # requirements of the classes used
    create_energy_system.format_weather_dataset(filepath=scenario_file)

    # CREATES AN ENERGYSYSTEM AS DEFINED IN THE SCENARIO FILE
    esys = create_energy_system.define_energy_system(nodes_data=nodes_data)
    # CREATES AN LIST OF COMPONENTS
    nodes = []

    # CREATES BUS OBJECTS, EXCESS SINKS, AND SHORTAGE SOURCES AS DEFINED IN THE
    # SCENARIO FILE AND ADDS THEM TO THE lIST OF COMPONENTS
    busd = create_objects.buses(nodes_data=nodes_data,
                                nodes=nodes)

    # PARALLEL CREATION OF ALL OBJECTS OF THE SCENARIO FILE
    
    # CREATES SOURCE OBJECTS AS DEFINED IN THE SCENARIO FILE AND ADDS THEM TO
    # THE lIST OF COMPONENTS
    t1 = Thread(target=create_objects.Sources,
                args=(nodes_data, nodes, busd, scenario_file,))
    t1.start()
    # CREATES SINK OBJECTS AS DEFINED IN THE SCENARIO FILE AND ADDS THEM TO
    # THE lIST OF COMPONENTS
    t2 = Thread(target=create_objects.Sinks, args=(nodes_data, busd,
                                                   nodes, scenario_file,))
    t2.start()
    # CREATES TRANSFORMER OBJECTS AS DEFINED IN THE SCENARIO FILE AND ADDS THEM
    # TO THE lIST OF COMPONENTS
    t3 = Thread(target=create_objects.Transformers, args=(nodes_data, nodes,
                                                          busd,))
    t3.start()
    # CREATES STORAGE OBJECTS AS DEFINED IN THE SCENARIO FILE AND ADDS THEM TO
    # THE lIST OF COMPONENTS
    t4 = Thread(target=create_objects.Storages, args=(nodes_data, nodes,
                                                      busd,))
    t4.start()
    # CREATES LINK OBJECTS AS DEFINED IN THE SCENARIO FILE AND ADDS THEM TO
    # THE lIST OF COMPONENTS
    t5 = Thread(target=create_objects.Links, args=(nodes_data, nodes, busd,))
    t5.start()

    # WAIT UNTIL THE THREADS HAVE DONE THEIR JOBS
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    # ADDS THE COMPONENTS TO THE ENERGYSYSTEM
    esys.add(*nodes)

    # PRINTS A GRAPH OF THE ENERGY SYSTEM
    if graph:
        create_graph.create_graph(filepath=result_path, nodes_data=nodes_data)

    # OPTIMIZES THE ENERGYSYSTEM AND RETURNS THE OPTIMIZED ENERGY SYSTEM
    om = optimize_model.least_cost_model(esys, num_threads,)

    # SHOWS AND SAVES RESULTS OF THE OPTIMIZED MODEL / POST-PROCESSING
    if results:
        create_results.xlsx(nodes_data=nodes_data,
                            optimization_model=om,
                            filepath=result_path)
    # CREATES PLOTLY RESULTS AND LOGS RESULTS OF CBC SOLVER
    if plotly:
        create_results.Results(nodes_data, om, esys, result_path)

    logging.info('   ' + '----------------------------------------------'
                         '----------')
    logging.info('   ' + 'Modelling and optimization successfully completed!')
