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
The "Open Energy Modeling Framework" (oemof) is an energy system modelling framework for the analysis of energy supply systems. It is carried out 
as open source python library and contains several sub-libraries, which are structured into four layers.

.. image:: images/oemof_structure.png
  :width: 600

By using the sub-library "solph", energy systems can be represented by utilizing the mathematical graph theory. Thus, energy systems are exemplified as "graphs" 
consisting of sets of "vertices" and "edges". In more specific terms, vertices stand for components and buses while directed edges connect them. The status variable 
of the energy flow indicates which amount of energy is transported between the individual nodes at what time. Possible components of an oemof energy system are 

- sources,
- sinks,
- transformers, and
- storages. 

Busses furthermore form connection points of an energy system. The graph of a simple energy system consisting of each one source, one transformer, one sink, as well as 
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
automatically.

Sinks
^^^^^
Sinks represent either energy demands within the energy system or energy exports to adjacent systems. Like sources, sinks can either have variable or fixed energy demands. 
Sinks with variable demands adjust their consumption to the amount of energy available. This could for example stand for the sale of surplus electricity. However, actual 
consumers usually have fixed energy demands, which do not respond to amount of energy available in the system. As with sources, the exact demands of sinks can be passed to 
the model with the help of time series. Oemof's sub-library "demandlib" can be used for the estimation of heat and electricity demands of different consumer groups, as based 
on German standard load profiles (SLP).

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
^^^^^^^^^^^^^^^
.

Getting Started
===============

Installation
------------
For the application of the Spreadsheet Energy System Model Generator Python (version >= 3.5) 
is required. This can be downloaded `here <https://www.python.org/downloads/>`_ free of charge and installed on your PC (Windows, Linux, Mac).


General Information
===================

License
-------

Contact
-------
Christian Klemm

Münster University of Applied Sciences

christian.klemm@fh-muenster.de


Acknowledgements
----------------

The authors thank the German Federal Ministry of Education (BMBF) for funding the R2Q project within grant 033W102A-K.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`