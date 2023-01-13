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

+-----------------------+--------------+---------------------------------------------+
| required parameter    | DHNx label   | description                                 |
+=======================+==============+=============================================+
| id                    | label_3      | unique id of the considered heatpipe        |
+-----------------------+--------------+---------------------------------------------+ 
| nonconvex (boolean)   | nonconvex    | indicating whether nothing (no pipe laying) |
|                       |              | or fixed-investment-costs (pipe laying) is  |
|                       |              | invested                                    |
+-----------------------+--------------+---------------------------------------------+
| min. capacity (kW)    | cap min      | minimum investable heat capacity            |
+-----------------------+--------------+---------------------------------------------+
| max. capacity (kW)    | cap max      | maximum investable heat capacity            |
+-----------------------+--------------+---------------------------------------------+
| heat loss factor      | l_factor     | relative loss factor related to the         |
| (`kW`:sub:`loss`      |              | installed capacity                          |
| / m *                 |              |                                             |
| `kW`:sub:`installed`) |              |                                             |
+-----------------------+--------------+---------------------------------------------+  
| heat loss factor fix  | l_factor_fix | fixed loss, which is incurred directly      |
| (`kW`:sub:`loss` / m) |              | after the non-convex investment decision    |
+-----------------------+--------------+---------------------------------------------+
| periodical costs      | capex_pipes  | investment costs per kW transportable       |
| (CU / kW * m * a)     |              | installed heat                              |
+-----------------------+--------------+---------------------------------------------+
| fix investment costs  | fix_costs    | investment costs per meter of pipe and its  |
| (CU / m)              |              | laying                                      |
+-----------------------+--------------+---------------------------------------------+
| periodical constraint | n.n.         | CU for second optimization criterion per kW |
| costs (CU / kW * m)   |              | transportable installed heat capacity       |
+-----------------------+--------------+---------------------------------------------+
| fix constraint costs  | n.n.         | CU for second optimization criterion per    |
| (CU / m)              |              | meter of pipe and its laying                |
+-----------------------+--------------+---------------------------------------------+

Reference: Becker G. "A comparative study of open-source district heating modeling tools.", unpublished at the time of publication of this documentation, 2022.

