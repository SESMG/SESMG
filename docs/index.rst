.. Spreadsheet Energy System Model Generator documentation master file, created by
   sphinx-quickstart on Fri Jan 24 10:13:26 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Spreadsheet Energy System Model Generator's documentation!
=====================================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

About the Model Generator
=========================
The Spreadsheet Energy System Model Generator allows the modeling and optimization of energy systems without the need for programming skills. 
The components defined in this spreadsheet are defined with the included Python program and the open source Python library "oemof", assembled 
to an energy system and optimized with the open source solver "cbc".

Open Energy Model Framework (oemof)
-----------------------------------
By using `oemof <https://oemof.readthedocs.io/en/stable/index.html>`_, energy systems can be represented by utilizing the mathematical graph theory. Thus, energy systems are exemplified as "graphs" 
consisting of sets of "vertices" and "edges". In more specific terms, vertices stand for components and buses while directed edges connect them. The status variable 
of the energy flow indicates which amount of energy is transported between the individual nodes at what time. Possible components of an oemof energy system are 

- sources,
- sinks,
- transformers, and
- storages. 

Buses furthermore form connection points of an energy system. The graph of a simple energy system consisting of each one source, one transformer, one sink, as well as 
two buses, could look like the example displayed in the following figure.

.. image:: images/simple_energy_system.png
  :width: 600
  
.. figure:: images/simple_energy_system.png
   :width: 100 %
   :alt: Bus-Example
   :align: center

   Graph of a simple energy system, consisting of one source, two buses, one transformer, and one a sink.
  
An oemof energy system must be in equilibrium at all times. Therefore sources must always provide exactly as much energy as the sinks and transformer losses consume. 
In turn, the sink must be able to consume the entire amount of energy supplied. If there is no balance, oemof is not able to solve the energy system.

Buses
^^^^^
The modelling framework oemof does not allow direct connections between components. Instead, they must always be connected with a bus. The bus in turn can be connected 
to other components, so that energy can be transported via the bus. Buses can have any number of incoming and outgoing flows. Buses can not directly be connected with 
each other. They do not consider any conversion processes or losses.

Sources
^^^^^^^
Sources represent the provision of energy. This can either be the exploitation of of an energy source (e.g. gas storage reservoir or solar energy, no energy source in 
physical sense), or the simplified energy import from adjacent energy systems. While some sources may have variable performances, depending on the temporary needs of 
the energy system, others have fixed performances, which depend on external circumstances. In the latter case, the exact performances must be entered to the model in 
form of time series. With the help of oemofs “feedinlib” and “windpowerlib”, electrical outputs of photovoltaik (pv)-systems and wind power plants can be generated 
automatically. In order to ensure a balance in the energy system at all times, it may be useful to add a “shortage” source to the energy system, which supplies energy 
in the event of an energy deficit. In reality, such a source could represent the purchase of energy at a fixed price.

Sinks
^^^^^
Sinks represent either energy demands within the energy system or energy exports to adjacent systems. Like sources, sinks can either have variable or fixed energy demands. 
Sinks with variable demands adjust their consumption to the amount of energy available. This could for example stand for the sale of surplus electricity. However, actual 
consumers usually have fixed energy demands, which do not respond to amount of energy available in the system. As with sources, the exact demands of sinks can be passed to 
the model with the help of time series. Oemof's sub-library `demandlib <https://demandlib.readthedocs.io/en/latest/>`_ can be used for the estimation of heat and electricity demands of different consumer groups, as based 
on German standard load profiles (SLP). The following electric SLPs are available:

.. table:: electrical standardload profiles

| Profil | Consumer Group                                    |
| :----: | ------------------------------------------------- |
|   H0   | households                                        |
|   G0   | commercial general                                |
|   G1   | commercial on weeks 8-18 h                        |
|   G2   | commercial with strong consumption in the evening |
|   G3   | commercial continuous                             |
|   G4   | shop/hairdresser                                  |
|   G5   | bakery                                            |
|   G6   | weekend operation                                 |
|   L0   | agriculture general                               |
|   L1   | agriculture with dairy industry/animal breeding   |
|   L2   | other agriculture                                 |

The following heat SLPs are available:

.. table:: heat standard load profiles

| Profile | House Type                                                   |
| :-----: | ------------------------------------------------------------ |
| EFH     | single family house                                          |
| MFH     | multi family house                                           |
| GMK     | metal and automotive                                         |
| GHA     | retail and wholesale                                         |
| GKO     | Local authorities, credit institutions and insurance companies |
| GBD     | other operational services                                   |
| GGA     | restaurants                                                  |
| GBH     | accommodation                                                |
| GWA     | laundries, dry cleaning                                      |
| GGB     | horticulture                                                 |
| GBA     | bakery                                                       |
| GPD     | paper and printing                                           |
| GMF     | household-like business enterprises                          |
| GHD     | Total load profile Business/Commerce/Services                |



In order to ensure a balance in the energy system at all times, it may be appropriate to add an “excess” sink to the energy system, 
which consumes energy in the event of energy surplus. In reality, this could be the sale of electricity or the give-away of heat to the atmosphere.



Transformers
^^^^^^^^^^^^
Transformers are components with one ore more input flows, which are transformed to one or more output flows. Transformers may be power plants, energy transforming processes 
(e.g., electrolysis, heat pumps), as well as transport lines with losses. The transformers’ efficiencies can be defined for every time step (e.g., the efficiency of a thermal 
powerplants in dependence of  the ambient temperature).

**Generic Transformers** are simply transforming an energy flow linearly into another one. A generic transformer’s efficiency remains the same regardless of the load point. 
transformers may have one or more different outputs, e.g., heat and electricity. For the modeling the nominal performance of a generic transformer with several outputs, the 
respective output ratios and an efficiency for each output need to be known.

The **GenericCHP**-transformer can be used to model different types of CHP plants, such as combined cycle extraction turbines, back pressure turbines, or motoric CHPs. For 
the individual outputs (electricity and heat), different nominal values and efficiencies can be defined. 

Links
^^^^^

Storages
^^^^^^^^
Storages are connected to a bus and can store energy from this bus and return it to a later point in time.

Investment
^^^^^^^^^^
The investment costs help to compare the costs of building new components to the costs of further using existing components instead. The annual savings from building new capacities 
should compensate the investment costs. The investment method can be applied to any new component to be built. In addition to the usual component parameters, the 
maximum installable capacity needs to be known. Further, the periodic costs need to be assigned to the investment costs. The periodic costs refer to the defined 
time horizon. If the time horizon is one year, the periodical costs correspond to the annualized capital costs of an investment.

Richardson Tool
---------------
.

Getting Started
===============

Installation
------------

1. For the application of the Spreadsheet Energy System Model Generator Python (version >= 3.5) 
is required. This can be downloaded `here <https://www.python.org/downloads/>`_ free of charge 
and installed on your PC (Windows, Linux, Mac).

2. Download the program files from `GIT <https://git.fh-muenster.de/ck546038/spreadsheet-energy-system-model-generator>`_ 
as .zip folder.

3. Extract the .zip folder in any directory on your computer

Using the Spreadsheets
----------------------

Timesystem
^^^^^^^^^^^^^^^^


- **start date**: start of the modelling time horizont. Format: "YYYY-MM-DD hh:mm:ss"
- **end date**: end date of the modelling time horizont. Format: "YYYY-MM-DD hh:mm:ss"
- **temporal resolution**: for the modelling considered temporal resolution. Possible inputs: "a" (years), "d" (days), "h (hours) "min" (minutes), "s" (seconds), "ms" (mili seconds).
- **time zone**:
- **periods**:


  
.. figure:: images/BSP_timesystem.PNG
   :width: 100 %
   :alt: Bus-Example
   :align: center

   Exemplary input for the time system

Buses
^^^^^

- **label**: Unique designation of the bus. The following format is recommended: "ID_energy sector_bus".
- **comment**: Space for an individual comment, e.g. to which measure this component belongs.
- **active**: Specifies whether the bus shall be included to the model. 0 = inactive, 1 = active. 
- **excess**: Specifies whether an sink is to be generated, which can decrease excess energy. 0 = no excess sink will be generated; 1 = excess sink will be generated. 
- **shortage**: Specifies whether to generate a shortage source that can compensate energy deficits. 0 = no shortage source will be generated; 1 = shortage source will be generated.
- **shortage costs [CU/kWh]**: Assigns a price per kWh to the purchase of energy from the shortage source. If the shortage source was deactivated, the fill character "x" is used. 
- **excess costs [CU/kWh]**: Assigns a price per kWh to the release of energy to the excess sink. If the excess sink was deactivated, the fill character "x" is used. 

  
	
.. figure:: images/BSP_buses.PNG
   :width: 100 %
   :alt: Bus-Example
   :align: center

   Exemplary input for the creation of buses
  

	
.. figure:: images/BSP_Graph_Bus.png
   :width: 60 %
   :alt: Bus_Graph
   :align: center

   Graph of the energy system, which is created by entering the example components



Sinks
^^^^^

- **label**: Unique designation of the sink. The following format is recommended: "ID_energy sector_sinks".
- **comment**: Space for an individual comment, e.g. to which measure this component belongs.
- **active**: Specifies whether the source shall be included to the model. 0 = inactive, 1 = active.
- **input**: Specifies which bus the sink is connected with.
- **load profile**: Specifies the basis on which the load profile of the sink is to be created. If the Richardson 
tool is to be used, "richardson" has to be inserted. For standard load profiles its short designation is used 
(electricity SLP's: h0, g0, ...; heat SLP's: efh, mfh, its, ...). If a time series is used, "timeseries" must be entered. 
If the source is not fixed, the fill character "x" has to be used.
- **annual demand [kWh/a]**: Annual energy demand of the sink. Required when using the Richardson Tool or standard load profiles. 
When using time series, the fill character "x" is used. 
- **occupants [RICHARDSON]**: Number of occupants living in the considered house. Only required when using the Richardson tool, 
use fill character "x" for other load profiles.
- **building class [HEAT SLP ONLY]**:
- **wind class [HEAT SLP ONLY]**:
- **fixed**: Indicates whether it is a fixed sink or not. 0 = not fixed; 1 = fixed.
 
.. figure:: images/BSP_sinks.png
   :width: 100 %
   :alt: Sink-Example
   :align: center

   Exemplary input for the creation of sinks
  

	
.. figure:: images/BSP_Graph_sink.png
   :width: 60 %
   :alt: Sink_Graph
   :align: center

   Graph of the energy system, which is created by entering the example components

Sources
^^^^^^^

- **label**: Unique designation of the source. The following format is recommended: "ID_energy sector_source".
- **comment**: Space for an individual comment, e.g. to which measure this component belongs.
- **active**: Specifies whether the source shall be included to the model. 0 = inactive, 1 = active.
- **output**: Specifies which bus the source is connected to.
- **technology**: Technology type of source. Input options: "photovoltaic", "wind", "other". Time series are 
automatically generated for photovoltaic systems and wind turbines. If "other" is selected, a time series must be stored in the "time_series" sheet.
- **variable costs [CU/kWh]**: Defines the variable costs incurred for a kWh of energy drawn from the source.
- **existing capacity [kW]**: Existing capacity of the source before possible investments.
- **min. investment capacity [kW]**: Minimum capacity to be installed in the case of an investment.
- **max. investment capacity [kW]**: Maximum capacity that can be added in the case of an investment. If no investment is possible, enter the value "0" here.
- **periodical costs [CU/(kW a)]**: Periodic costs incurred for investments per kW and timeperiod added.
- **technology database (PV ONLY)**: Database, from where module parameters are to be obtained. Recommended Database: "SandiaMod".
- **inverter database (PV ONLY)**: Database, from where inverter parameters are to be obtained. Recommended Database: "sandiainverter".
- **Modul Model (PV ONLY)**: Module name, according to the database used.
- **Inverter Model (PV ONLY)**: Inverter name, according to the database used.
- **Azimuth (PV ONLY)**: Specifies the orientation of the PV module in degrees. Values between 0 and 360 are permissible 
(0 = north, 90 = east, 180 = south, 270 = west). Only required for photovoltaic sources, use fill character "x" for other technologies.
- **Surface Tilt (PV ONLY)**: Specifies the inclination of the module in degrees (0 = flat). Only required for photovoltaic sources, use fill character "x" for other technologies.
- **Albedo (PV ONLY)**: Specifies the albedo value of the reflecting floor surface. Only required for photovoltaic sources, use fill character "x" for other technologies.
- **Altitude (PV ONLY)**: Height (above normal zero) in meters of the photovoltaic module. Only required for photovoltaic sources, use fill character "x" for other technologies.
- **Latitude (PV ONLY)**: Geographic latitude (decimal number) of the photovoltaic module. Only required for photovoltaic sources, use fill character "x" for other technologies.
- **Longitude (PV ONLY)**: Geographic longitude (decimal number) of the photovoltaic module. Only required for photovoltaic sources, use fill character "x" for other technologies.
- **fixed**: Indicates whether it is a fixed source or not. 0 = not fixed; 1 = fixed.

.. figure:: images/BSP_source.png
   :width: 100 %
   :alt: Source-Example
   :align: center

   Exemplary input for the creation of sources
  

	
.. figure:: images/BSP_Graph_source.png
   :width: 60 %
   :alt: Source_Graph
   :align: center

   Graph of the energy system, which is created by entering the example components  

Transformers
^^^^^^^^^^^^

- **label**: Unique designation of the transformer. The following format is recommended: "ID_energy sector_transformer".
- **comment**: Space for an individual comment, e.g. to which measure this component belongs.
- **active**: Specifies whether the transformer shall be included to the model. 0 = inactive, 1 = active.
- **transformer type**: Indicates what kind of transformer it is. Possible entries: "GenericTransformer" 
for linear transformers with constant efficiencies; "GenericCHP" for transformers with varying efficiencies.
- **input**: Specifies from which bus the input to the transformer comes.
- **output**: Specifies to which bus the output of the transformer is forwarded.
- **output2**: Specifies to which bus the output of the transformer is forwarded, if there are several outputs. 
If there is no second output, the fill character "x" must be entered here.
- **efficiency**: Specifies the efficiency of the first output. Values must be between 0 and 1.
- **efficiency2**: Specifies the efficiency of the second output, if there is one. Values must be between 0 and 1. 
If there is no second output, the fill character "x" must be entered here.
- **variable input costs**: Variable costs incurred per kWh of input energy supplied.
- **existing capacity [kW]**: Already installed capacity of the transformer.
- **max investment capacity [kW]**: Maximum in addition to existing capacity, installable transformer capacity.
- **min investment capacity [kW]**: Minimum transformer capacity to be installed.
- **periodical costs [CU/a]**: Periodical costs incurred for investments per kW and timeperiod added.
- **el. eff. at max fuel flow w/o distr. heating [GenericCHP]**:
- **el. eff. at min. fuel flow w/o distr. heating [GenericCHP]**:
- **minimal therm. condenser load to cooling water [GenericCHP]**:
- **power loss index [GenericCHP]**:


.. figure:: images/BSP_transformers.png
   :width: 100 %
   :alt: Transformer-Example
   :align: center

   Exemplary input for the creation of transformers
  

	
.. figure:: images/BSP_Graph_transformer.png
   :width: 60 %
   :alt: Transformer_Graph
   :align: center

   Graph of the energy system, which is created by entering the example components  

Storages
^^^^^^^^

- **label**: Unique designation of the storage. The following format is recommended: "ID_energy sector_storage".
- **comment**: Space for an individual comment, e.g. to which measure this component belongs.
- **active**: Specifies whether the storage shall be included to the model. 0 = inactive, 1 = active.
- **bus**: Specifies which bus the storage is connected to.
- **capacity inflow**: Indicates the performance with which the memory can be charged.
- **capacity outflow**: Indicates the performance with which the memory can be discharged.
- **capacity loss**: Indicates the storage losses per time unit.
- **efficiency inflow**: Specifies the charging efficiency.
- **efficiency outflow**: Specifies the discharging efficiency.
- **initial capacity**: Specifies how far the memory is loaded at time 0 of the simulation. Value must be between 0 and 1.
- **capacity min**: Specifies the minimum amount of memory that must be loaded at any given time. Value must be between 0 and 1.
- **capacity max**: Specifies the maximum amount of memory that can be loaded at any given time. Value must be between 0 and 1.
- **variable input costs**: Indicates how many costs arise for the charging of one kWh.
- **variable output costs**: Indicates how many costs arise for the discharging of a kWh.
- **existing capacity [kW]**: Already installed capacity of the storage.
- **periodical costs [CU/a]**: Periodical costs incurred for investments per kW capacity and timeperiod added.
- **max. investment capacity [kW]**: Maximum in addition to existing capacity, installable storage capacity.
- **min. investment capacity [kW]**: Minimum storage capacity to be installed.

.. figure:: images/BSP_storage.png
   :width: 100 %
   :alt: Storage-Example
   :align: center

   Exemplary input for the creation of storages
  

	
.. figure:: images/BSP_Graph_Storage.png
   :width: 60 %
   :alt: Transformer_Graph
   :align: center

   Graph of the energy system, which is created by entering the example components

Links
^^^^^
- **label**: Unique designation of the link. The following format is recommended: "ID_energy sector_transformer"
- **comment**: Space for an individual comment, e.g. to which measure this component belongs.
- **active**: Specifies whether the link shall be included to the model. 0 = inactive, 1 = active. 
- **bus_1**: First bus to which the link is connected. If it is a directed link, this is the input bus.
- **bus_2**: Second bus to which the link is connected. If it is a directed link, this is the output bus.
- **(un)directed**: Specifies whether it is a directed or an undirected link. Input options: "directed", "undirected".
- **efficiency**: Specifies the efficiency of the link.
- **existing capacity [kW]**: Already installed capacity of the link.
- **min. investment capacity [kW]**: Maximum in addition to existing capacity, installable capacity.
- **max. investment capacity [kW]**: inimum capacity to be installed.
- **variable costs [CU/kWh]**: Indicates how many costs arise for the transport of one kWh.
- **periodical costs [CU/(kW a)]**: Periodical costs incurred for investments per kW capacity and timeperiod added.



.. figure:: images/BSP_link.png
   :width: 100 %
   :alt: Storage-Example
   :align: center

   Exemplary input for the creation of storages
  

	
.. figure:: images/BSP_Graph_link.png
   :width: 60 %
   :alt: Transformer_Graph
   :align: center

   Graph of the energy system, which is created by entering the example components

Time Series
^^^^^^^^^^^
- **timestamp**: Points in time to which the stored time series are related. 
Should be within the time horizon defined in the sheet "timeseries".
- **timeseries**: Time series of a sink which has been assigned the property 
"timeseries" under the attribute "load profile" or source which has been assigned 
the property "other" under the attribute "technology". Time series contain a value 
between 0 and 1 for each point in time, which indicates the proportion of installed 
capacity accounted for by the capacity produced at that point in time. In the header 
line, the name must be entered in the format "componentID.actual_value".

 
 
.. figure:: images/timeseries.PNG
   :width: 100 %
   :alt: Timeseries-Example
   :align: center

   Exemplary input for time series




Weather Data
^^^^^^^^^^^^^^^^ 
- **timestamp**: Points in time to which the stored weather data are related. Should be within the time horizon defined in the sheet "timeseries".
- **dhi**: diffuse horizontal irradiance in W/m^2
- **dirhi**: direct horizontal irradiance in W/m^2
- **pressure**: air pressure in Pa
- **windspeed**: Wind speed, measured at 10 m height, in the unit m/s
- **z0**: roughness length of the environment

.. figure:: images/weatherdata.PNG
   :width: 100 %
   :alt: WeatherData-Example
   :align: center

   Exemplary input for weather data

Using the results
-----------------


Example
-------


General Information
===================

License
-------

Contact
-------
Christian Klemm

Münster University of Applied Sciences

christian.klemm@fh-muenster.de

.. image:: images/FH_logo.jpg
   :width: 20 %


Acknowledgements
----------------

The authors thank the German Federal Ministry of Education (BMBF) for funding the R2Q project within grant 033W102A-K.

- Projektlogos einfügen

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`