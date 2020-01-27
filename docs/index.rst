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
the model with the help of time series. Oemof's sub-library "demandlib" can be used for the estimation of heat and electricity demands of different consumer groups, as based 
on German standard load profiles (SLP). In order to ensure a balance in the energy system at all times, it may be appropriate to add an “excess” sink to the energy system, 
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

.. image:: images/BSP_timesystem.PNG
  :width: 700

Buses
^^^^^

- **label**: Unique designation of the bus. The following format is recommended: "ID_energy sector_bus". Example: "bus001_electricity_bus"; "bus002_electricity_bus"
- **active**: Specifies whether the bus shall be included to the model. 0 = inactive, 1 = active. Example: "1"; "1"
- **excess**: Specifies whether an sink is to be generated, which can decrease excess energy. 0 = no excess sink will be generated; 1 = excess sink will be generated. Example: "0"; "1"
- **shortage**: Specifies whether to generate a shortage source that can compensate energy deficits. 0 = no shortage source will be generated; 1 = shortage source will be generated. Example: "1"; "0"
- **shortage costs [CU/kWh]**: Assigns a price per kWh to the purchase of energy from the shortage source. If the shortage source was deactivated, the fill character "x" is used. Example: "0.30"; "x"
- **excess costs [CU/kWh]**: Assigns a price per kWh to the release of energy to the excess sink. If the excess sink was deactivated, the fill character "x" is used. Example: "x"; "0.10"

.. image:: images/BSP_buses.PNG
  :width: 700

Sinks
^^^^^

- **label**: Unique designation of the sink. The following format is recommended: "ID_energy sector_sinks". Example: "building001_electricity_sink"
- **active**: Specifies whether the source shall be included to the model. 0 = inactive, 1 = active. Example: "1"
- **input**: Specifies which bus the sink is connected with. Example: "bus001_electricity_bus" 
- **standard load profile**: Specifies the basis on which the load profile of the sink is to be created. If the Richardson tool is to be used, "richardson" has to be inserted. For standard load profiles its short designation is used (electricity SLP's: h0, g0, ...; heat SLP's: efh, mfh, its, ...). If a time series is used, "timeseries" must be entered. If the source is not fixed, the fill character "x" has to be used. Example: "richardson" 
- **annual demand [kWh/a]**: Annual energy demand of the sink. Required when using the Richardson Tool or standard load profiles. When using time series, the fill character "x" is used. Example: ""
- **occupants [RICHARDSON]**: Number of occupants living in the considered house. Only required when using the Richardson tool, use fill character "x" for other load profiles.
- **building class [HEAT SLP ONLY]**:
- **wind class [HEAT SLP ONLY]**:
- **fixed**: Indicates whether it is a fixed sink. 0 = not fixed; 1 = fixed.

.. image:: images/BSP_sinks.png
  :width: 700


Sources
^^^^^^^

- **label**: Unique designation of the source. The following format is recommended: "ID_energy sector_source". Example: "pv001_electricity_source"
- **active**: Specifies whether the source shall be included to the model. 0 = inactive, 1 = active. Example: "1"
- **output**: Specifies which bus the source is connected to. Example: "bus001_electricity_bus"
- **variable costs [CU/kWh]**: Defines the variable costs incurred for a kWh of energy drawn from the source. Example: "0.00"
- **existing capacity [kW]**: Existing capacity of the source before possible investments. Example: "10.00"
- **min. investment capacity [kW]**: Minimum capacity to be installed in the case of an investment. Example: "0.00"
- **max. investment capacity [kW]**: Maximum capacity that can be added in the case of an investment. If no investment is possible, enter the value "0" here. Example: "10.00"
- **periodical costs [CU/(kW a)]**: Periodic costs incurred for investments per kWh added. Example: "10.00"
- **technology**: Technology type of source. Input options: "photovoltaic", "wind", "other". Time series are automatically generated for photovoltaic systems and wind turbines. If "other" is selected, a time series must be stored in the "time_series" sheet. Example: "photovoltaic"
- **technology database**: Example: ""
- **inverter database**: Example: ""
- **Modul Model (PV ONLY)**: Example: "Yingli\_YL210\_\_2008\_\_E\_\_" 
- **Inverter Model (PV ONLY)**: Example: "ABB\_\_MICRO\_0\_25\_I\_OUTD\_US\_208\_208V\_\_CEC\_2014\_"
- **reference value [kW] (PV ONLY)**: Example: "434.88"
- **Azimuth (PV ONLY)**: Specifies the orientation of the PV module in degrees. Values between 0 and 360 are permissible (0 = north, 90 = east, 180 = south, 270 = west). Only required for photovoltaic sources, use fill character "x" for other technologies. Example: "153.00"
- **Surface Tilt (PV ONLY)**: Specifies the inclination of the module in degrees (0 = flat). Only required for photovoltaic sources, use fill character "x" for other technologies. Example: "32.00"
- **Albedo (PV ONLY)**: Specifies the albedo value of the reflecting floor surface. Only required for photovoltaic sources, use fill character "x" for other technologies. Example: "0.2"
- **Altitude (PV ONLY)**: Height (above normal zero) in meters of the photovoltaic module. Only required for photovoltaic sources, use fill character "x" for other technologies. Example: "60"
- **Latitude (PV ONLY)**: Geographic latitude (decimal number) of the photovoltaic module. Only required for photovoltaic sources, use fill character "x" for other technologies. Example: "50.00"
- **Longitude (PV ONLY)**: Geographic longitude (decimal number) of the photovoltaic module. Only required for photovoltaic sources, use fill character "x" for other technologies. Example: "10.00"
- **fixed**: 

.. image:: images/BSP_source.png
  :width: 700
  

Transformers
^^^^^^^^^^^^

- **label**: Unique designation of the transformer. The following format is recommended: "ID_energy sector_transformer". Example: "tr001_electricity_transformer"
- **active**: Specifies whether the transformer shall be included to the model. 0 = inactive, 1 = active. Example: "1" 
- **transformer type**:
- **input**:
- **output**:
- **output2**:
- **efficiency**:
- **efficiency2**:
- **variable input costs**:
- **existing capacity [kW]**:
- **max investment capacity [kW]**:
- **min investment capacity [kW]**:
- **el. eff. at max fuel flow w/o distr. heating [GenericCHP]**:
- **el. eff. at min. fuel flow w/o distr. heating [GenericCHP]**:
- **minimal therm. condenser load to cooling water [GenericCHP]**:
- **power loss index [GenericCHP]**:

.. image:: images/BSP_transformers.png
  :width: 700

Storages
^^^^^^^^

- **label**: Unique designation of the storage. The following format is recommended: "ID_energy sector_storage". Example: "battery001_electricity_storage" 
- **active**: Specifies whether the storage shall be included to the model. 0 = inactive, 1 = active. Example: "1" 
- **bus**:
- **capacity inflow**:
- **capacity outflow**:
- **capacity loss**: 
- **efficiency inflow**: 
- **efficiency outflow**:
- **initial capacity**: 
- **capacity min**: 
- **capacity max**: 
- **variable input costs**:
- **variable output costs**:
- **existing capacity [kW]**:
- **periodical costs [CU/a]**: 
- **max. investment capacity [kW]**: 
- **min. investment capacity [kW]**: 

.. image:: images/BSP_storage.png
  :width: 700

Links
^^^^^
- **label**: Unique designation of the link. The following format is recommended: "ID_energy sector_transformer". Example: "pl001_electricity_link" 
- **active**: Specifies whether the link shall be included to the model. 0 = inactive, 1 = active. Example: "1" 
- **bus_1**:
- **bus_2**: 
- **(un)directed**: 
- **efficiency**: 
- **capacity [kW]**:

.. image:: images/BSP_link.png
  :width: 700

Time Series
^^^^^^^^^^^
- **timestamp**:
- **timeseries**:

.. image:: images/timeseries.png
  :width: 700

Weather Data
^^^^^^^^^^^^^^^^ 
- **timestamp**:
- **dhi**:
- **dirhi**:
- **pressure**:
- **windspeed**:
- **z0**:

Using the results
-----------------

.. image:: images/weatherdata.png
  :width: 700

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

.. image:: images/oemof_structure
 :width: 100


Acknowledgements
----------------

The authors thank the German Federal Ministry of Education (BMBF) for funding the R2Q project within grant 033W102A-K.

- Projektlogos einfügen

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`