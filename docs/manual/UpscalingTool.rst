Urban District Upscaling Tool
=============================

Documentation to be completed soon.


Upscaling Model
---------------

.. figure:: ../images/Upscaling_Model.png
   :width: 100 %
   :alt: Upscaling_Model
   :align: center


.. list-table:: Components
   :widths: 25 25 50
   :header-rows: 1
   :align: center

   * - component
     - system
     - description
   * - sub-system electricity bus
     - every sub-system
     - The electric distribution within sub-systems is considered to be loss free. Therefore, the sub-system electricity bus represents the entire distribution system of a sub-system [1].
   * - sub-system electricity demand
     - every sub-system
     - The **sub-system electricity demand**-sink is directly connected to the **sub-system electricity bus** [1].
   * - sub-system electricity import
     - every sub-system
     - Due to different prices for electricity import, a shortage/import source is connected to every sub-systemssub-system electricity bus [1].


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
[1] Klemm, C., Budde J., Vennemann P., *Model Structure forurban energy system optimization models*, unpublished at the time of publication of this documentation, 2021.
