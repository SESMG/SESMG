# -*- coding: utf-8 -*-
"""
Spreadsheat-Energy-System-Model-Generator (development version)

creates an energy system from a given spreadsheet data file, solves it for the
purpose of least cost optimization, and plots results.

The scenario.xlsx-file must contain the following elements:
    
sheet        | columns
-------------------------------------------------------------------------------
timesystem   | start_date, end_date, holidays, temporal resolution, timezone

buses        | label, active, excess, shortage, shortage costs [CU/kWh], 
               excess costs [CU/kWh]
               
sinks        | label, active, input, input2, load profile, nominal value [kW],
               annual demand [kWh/a], occupants [RICHARDSON], 
               building class [HEAT SLP ONLY], wind class [HEAT SLP ONLY], 
               fixed
               
sources      | label, active, output, technology, variable costs [CU/kWh],
               existing capacity [kW], min. investment capacity [kW], 
               max. investment capacity [kW], periodical costs [CU/(kW a)], 
               technology database (PV ONLY), inverter database (PV ONLY),
               Modul Model (PV ONLY), Inverter Model (PV ONLY), 
               reference value [kW], Azimuth (PV ONL>), Surface Tilt (PV ONLY),
               Albedo (PV ONLY), Altitude (PV ONLY), Latitude (PV ONLY), 
               Longitude (PV ONLY)
               
transformers | label, active, transformer type, input, output, output2, 
               efficiency, efficency2, variable input costs [CU/kWh],
               variable output costs [CU/kWh], existing capacity [kW],
               max. investment capacity [kW], min. investment capacity [kW],
               periodical costs [CU/(kW a)]
               
storages     | label, active, bus, existing capacity [kW], 
               min. investment capacity [kW], max. investment capacity [kW],
               periodical costs [CU/(kW a)], capacity inflow, capacity outflow,
               capacity loss, efficiency inflow, efficiency outflow, 
               initial capacity, capacity min, capacity max, 
               variable input costs, variable output costs
               
powerlines   | label, active, bus_1, bus_2, (un)directed, efficiency, 
               existing capacity [kW], min. investment capacity [kW],
               max. investment capacity [kW], variable costs [CU/kWh],
               periodical costs [CU/(kW a)]
               
time_series  | timestamp, timeseries for components with fixed input or output

weather_data | dates(untitled), dhi, dirhi, pressure, temp_air, windspeed, z0
-------------------------------------------------------------------------------
Docs:
https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/
GIT:
https://git.fh-muenster.de/ck546038/spreadsheet-energy-system-model-generator
-------------------------------------------------------------------------------

@ Christian Klemm - christian.klemm@fh-muenster.de, 13.02.2020
"""

import logging
from oemof.tools import logger
import os

#import program_files.oemof.tools.logger as logger

#from program_files.oemof.tools import logger


# IMPORT CUSTOM MODULES
from program_files import (create_objects, create_results, 
                           create_energy_system, optimize_model)



# DEFINES PATH OF INPUT DATA
scenario_file = os.path.join(os.path.dirname(__file__),'scenario.xlsx')

# DEFINES PATH OF OUTPUR DATA
result_path = os.path.join(os.path.dirname(__file__)+'/results')

# DEFINES A LOGGING FILE
log_path = os.path.join(os.path.dirname(__file__)+'/results')
logger.define_logging(logpath=log_path)

# IMPORTS DATA FROM THE EXCEL FILE AND RETURNS IT AS DICTIONARY
nodes_data = create_energy_system.import_scenario(filepath = scenario_file)

# CREATES AN ENERGYSYSTEM AS DEFINED IN THE SCENARIO FILE
esys = create_energy_system.define_energy_system(filepath = scenario_file,
                                                 nodes_data = nodes_data)

# CREATES THE LIST OF COMPONENTS
nodes = []

# CREATES BUS OBJECTS, EXCESS SINKS, AND SHORTAGE SOURCES AS DEFINED IN THE 
# SCENARIO FILE AND ADDS THEM TO THE lIST OF COMPONENTS
busd = create_objects.buses(nodes_data = nodes_data,
                            nodes = nodes)

# CREATES SOURCE OBJECTS AS DEFINED IN THE SCENARIO FILE AND ADDS THEM TO
# THE lIST OF COMPONENTS
create_objects.sources(nodes_data = nodes_data,
                       nodes = nodes,
                       bus = busd, 
                       filepath = scenario_file)

# CREATES SINK OBJECTS AS DEFINED IN THE SCENARIO FILE AND ADDS THEM TO
# THE lIST OF COMPONENTS
create_objects.sinks(nodes_data = nodes_data,
                     bus = busd, 
                     nodes = nodes,
                     filepath = scenario_file)

# CREATES TRANSFORMER OBJECTS AS DEFINED IN THE SCENARIO FILE AND ADDS THEM TO
# THE lIST OF COMPONENTS
create_objects.transformers(nodes_data = nodes_data,
                            bus = busd,
                            nodes = nodes)

# CREATES STORAGE OBJECTS AS DEFINED IN THE SCENARIO FILE AND ADDS THEM TO
# THE lIST OF COMPONENTS
create_objects.storages(nodes_data = nodes_data,
                        bus = busd,
                        nodes = nodes)

# CREATES LINK OBJECTS AS DEFINED IN THE SCENARIO FILE AND ADDS THEM TO
# THE lIST OF COMPONENTS
create_objects.links(nodes_data = nodes_data,
                     bus = busd,
                     nodes = nodes)

# ADDS THE COMPONENTS TO THE ENERGYSYSTEM
my_nodes = nodes
esys.add(*my_nodes)

# OPTIMIZES THE ENERGYSYSTEM AND RETURNS THE OPTIMIZED ENERGY SYSTEM
om = optimize_model.least_cost_model(nodes_data = nodes_data,
                                     energy_system = esys)

# SHOWS AND SAVES RESULTS OF THE OPTIMIZED MODEL / POST-PROCESSING
create_results.xlsx(nodes_data = nodes_data, 
                    optimization_model = om, 
                    energy_system = esys,
                    filepath=result_path)

create_results.statistics(nodes_data = nodes_data, 
                     optimization_model = om, 
                     energy_system = esys)

logging.info('   '+'Modelling and optimization successfully completed!')


