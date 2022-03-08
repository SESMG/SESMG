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

component_parameter.csv
-------------------------
The component_parameter sheet defines the losses (only fo district heat
house stations), costs and constraint costs
of the district heat house station and clustered consumers link which is
used in the context of spatial clustering of a given energysystem due to
infeasible sizes.

pipes.csv
-------------------------
The pipes sheet defines a 'database' which is pipe specific parameters like:

- **active**: this parameter is used to decide rather the given pipe type
    is active(1) or inactive(0)
- **nonconvex**:
- l_factor:
_ l_factor_fix:
- **cap_max** in (kW):
- **cap_min** in (kW): min. investment capacity
- **capex_pipes** in (CU / (kW*m)): periodical costs
- fix_costs:
- periodical_constraint_costs:

These parameters are necessary for the creation of a dhnx fluid driven
energy network.
