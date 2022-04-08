Using the program_files/technical_data
*************************************************
For the modelling of technologies like solar thermal or district heating
some technical parameters (e.g. the peak power of a specific solar thermal
panel or of a specific fluid pipe) have to be provided. For fulfilling this
requirement the program_files/technical_data folder holding some csv
files which will be described in more detail in the upcoming sections.

District heating
=================================================
The program_files/technical_data folder is holding a subdirectory holding
the technical data of the created district heating network. Which consists of a file named
'component_parameters.csv' and another one named 'pipes.csv'

pipes.csv
-------------------------
The pipes sheet defines a 'database' which is pipe specific parameters like:

+---------------------+------------+---------------------------------------------+
| required parameter  | DHNx label | description                                 |
+=====================+============+=============================================+
| id                  | label_3    | unique id of the considered heatpipe        |
+---------------------+------------+---------------------------------------------+ 
| nonconvex (boolean) | nonconvex  | indicating whether nothing (no pipe laying) |
|                     |            | or fixed-investment-costs (pipe laying) is  |
|                     |            | invested                                    |
+---------------------+------------+---------------------------------------------+
min. capacity (kW) cap min minimum invested heat capacity
max. capacity (kW) cap max maximum investable heat capacity
heat loss factor
( kWloss
m·kWinstalled )
l factor relative loss factor related to the installed capacity
heat loss factor fix ( kWloss
m ) l factor fix fixed loss, which is incurred directly after the non-
convex investment decision
periodical costs ( e
m·a ) capex pipes investment costs per kW transportable installed heat
capacity
fix investment costs ( e
m ) fix costs investment costs per meter of pipe and its laying
periodical constraint costs
( g CO2
kW·m )
n.n. CO2 emission per kW transportable installed heat
capacity
fix constraint costs ( g CO2
m ) n.n. CO2 emission per meter of pipe and its laying
Reference: ***
These parameters are necessary for the creation of a dhnx fluid driven
energy network.
