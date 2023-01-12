Urban District Upscaling Tool
=============================

Documentation to be completed soon.

Using the Upscaling Tool
------------------------

The upscaling tool can be used with the following steps:

1. Fill the "pre-scenario"-xlsx-sheet as described below.
2. Fill the "standard-parameters"-xlsx-sheet as described below.
3. Execute the upscaling tool to generate a model with the structure described below.
4. Execute the automatically generated scenario-xlsx-sheet using the main SESMG application.


Upscaling Model
---------------

.. figure:: ../images/manual/UpscalingTool/Upscaling_Model.png
   :width: 100 %
   :alt: Upscaling_Model
   :align: center


.. list-table:: Components
   :widths: 25 25 50
   :header-rows: 1
   :align: center

   * - component
     - system level
     - description
   * - sub-system electricity bus
     - sub-system
     - The electric distribution within sub-systems is considered to be loss free. Therefore, the sub-system electricity bus represents the entire distribution system of a sub-system [1].
   * - sub-system electricity demand
     - sub-system
     - The **sub-system electricity demand**-sink is directly connected to the **sub-system electricity bus** [1].
   * - sub-system electricity import
     - sub-system
     - Due to different prices for electricity import, a shortage/import source is connected to every sub-systemssub-system electricity bus [1].
   * - photovoltaic system
     - 
     - 
   * - decentral battery storage
     - sub-system
     - 
   * - renovation measures
     - sub-system
     - 
   * - gas heating system
     - sub-system
     - 
   * - solar heat system
     - sub-system
     - 
   * - surface competition constraint
     - sub-system
     - 
   * - heat pumps
     - sub-system
     - 
   * - electric heating system
     - sub-system
     - 
   * - decentral thermal storage
     - sub-system
     - 
   * - electricity exchange
     - main-system
     - 
   * - district heating system
     - main-system
     - 
   * - biomass heating plant
     - main-system
     - 
   * - central heat storage
     - main-system
     - 
   * - natural gas CHP
     - main-system
     - 
   * - biogas CHP
     - main-system
     - 
   * - central thermal storage
     - main-system
     -
   * - central hydrogen system
     - main-system
     -  
    


     


Pre-Scenario
------------

.. list-table:: pre-scenario input columns
   :widths: 100 100
   :header-rows: 1
   :align: center

   * - column
     - description
   * - label
     - n.n
   * - comment
     - n.n
   * - ashp
     - n.n
   * - ...
     - ...

     
Standard Parameters
-------------------

Clustering
----------

References
==========
[1] Klemm, C., Budde J., Vennemann P., *Model Structure for urban energy system optimization models*, unpublished at the time of publication of this documentation, 2021.
