Urban District Upscaling Tool
=============================

Documentation to be completed soon.

.. figure:: ../images/sesmg_process.png
   :width: 100 %
   :alt: Process of the SESMG.
   :align: center

Using the Upscaling Tool
------------------------

The upscaling tool can be used with the following steps:

1. Fill the `upscaling sheet`_.
2. If necessary, adjust the "standard_parameters"-xlsx-sheet, for example if electricity prices have increased. 
3. Execute the upscaling tool to generate a energy system model with the structure described below.
4. Execute the automatically generated model_definition-xlsx-sheet.


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
    


     

.. _`upscaling sheet`:
Upscaling sheet
=========================

Category 1
-----------------------

.. csv-table:: Input for the upscaling sheet. Category 1: Building-specific data.
   :header:  label,comment,active,year of construction,distance of electric vehicles,electricity demand,heat demand,building type,units,occupants per unit,gross building area,latitude,longitude,year of construction wall,area outer wall,year of construction windows,area windows,year of construction roof,rooftype,area roof,cluster ID,flow temperature

   x,,,,km/a,kWh / (sqm * a),kWh / (sqm * a),,,,sqm,° WGS 84,° WGS 84,,sqm,,sqm,,,sqm,,°C
   001_building,,1,1800,0,400,400,COM_Food,1,1,100,52.000000,7.000000,1800,50,0,0,1967,flat roof,25,0,60
   002_building,,1,1800,0,0,0,MFB,1,1,50,52.000000,7.000000,1979,100,1999,20,1993,flat roof,50,0,60
   003_building,,1,1800,10000,30,20,SFB,1,1,120,52.000000,7.000000,1994,250,2001,125,1992,step roof,125,0,40
   
- **label**: description coming soon
- **comment**: description coming soon
- **active**: description coming soon
- **year of construction**: description coming soon
- **distance of electric vehicles (km/a)**: description coming soon
- **electricity demand (kWh / (m²  a))**: description coming soon
- **heat demand (kWh / (m² a))**: description coming soon
- **building type**: description coming soon
- **units**: description coming soon
- **occupants per unit**: description coming soon
- **gross building area	(m²)**: description coming soon
- **latitude	(° WGS 84)**: description coming soon
- **longitude	(° WGS 84)**: description coming soon
- **year of construction wall**: description coming soon
- **area outer wall	(m²)**: description coming soon
- **year of construction windows**: description coming soon
- **area windows	(m²)**: description coming soon
- **year of construction roof**: description coming soon
- **rooftype**: description coming soon
- **area roof	(m²)**: description coming soon
- **cluster ID**: description coming soon
- **flow temperature	(°C)**: description coming soon
 

Category 2
-----------------------


.. csv-table:: Input for the upscaling sheet. Category 2: Building investment data.
   :header:  label,HS,ashp,gchp,parcel ID,oil heating,gas heating,battery storage,thermal storage,central heat,electric heating,st or pv 1,roof area 1,surface tilt 1,azimuth 1,st or pv 2,roof area 2,surface tilt 2,azimuth 2

   x,,,,,,,,,,,,(m²),(°),(°),,(m²),(°),(°)
   001_building,1,no,no,no,no,no,no,no,yes,no,0,0,0,0,0,0,0,0
   002_building,1,no,no,no,no,yes,no,no,no,no,pv&st,150,75,100,0,0,0,0
   003_building,1,yes,yes,GCHP25,no,no,yes,yes,yes,no,pv&st,200,50,180,0,0,0,0


- **label**: description coming soon
- **HS**: description coming soon
- **ashp**: description coming soon
- **gchp**: description coming soon
- **parcel ID**: description coming soon
- **oil heating**: description coming soon
- **gas heating**: description coming soon
- **battery storage**: description coming soon
- **thermal storage**: description coming soon
- **central heat**: description coming soon
- **electric heating**: description coming soon
- **st or pv 1**: description coming soon
- **roof area 1	(m²)**: description coming soon
- **surface tilt 1	(°)**: description coming soon
- **azimuth 1	(°)**: description coming soon


Category 3
-----------------------


.. csv-table:: Input for the upscaling sheet. Category 3: Central investment data.
   :header:  label,comment,active,technology,latitude,longitude,area,dh_connection,azimuth,surface tilt,flow temperature

   ,,,,° WGS 84,° WGS 84,sqm,,°,°,°C
   electricity_exchange,,1,electricity_exchange,,,,,,, 
   battery_storage,,1,battery,,,,,,, 
   ng_chp,,0,naturalgas_chp,,,,heat_input,,, 
   bg_chp,,0,biogas_chp,,,,heat_input,,, 
   pe_chp,,0,pellet_chp,,,,heat_input,,, 
   wc_chp,,1,woodchips_chp,,,,heat_input,,, 
   swhp,,0,swhp_transformer,,,,heat_input,,, 
   ashp,,0,ashp_transformer,,,,heat_input,,, 
   gchp,free area needed,1,gchp_transformer,,,2500,heat_input,,, 
   ng_heating,,0,naturalgas_heating_plant,,,,heat_input,,, 
   bg_heating,,0,biogas_heating_plant,,,,heat_input,,, 
   pe_heating,,0,pellet_heating_plant,,,,heat_input,,, 
   wc_heating,,1,woodchips_heating_plant,,,,heat_input,,, 
   thermal_storage,,1,thermal_storage,,,,heat_input,,, 
   p2g,,0,power_to_gas,,,,heat_input,,, 
   heat_input,heat center,1,heat_input_bus,52,7,,,,,40
   central_pv_st,free area needed,1,pv&st,52,7,15000,heat_input,180,22.5, 
   screw_turbine,,1,timeseries_source,,,,,,, 


 - **label**: description coming soon
 - **comment**: description coming soon
 - **active**: description coming soon
 - **technology		**: description coming soon
 - **latitude (° WGS 84)**: description coming soon
 - **longitude	(° WGS 84)**: description coming soon
 - **area (m²)**: description coming soon
 - **dh_connection**: description coming soon
 - **azimuth	(°)**: description coming soon
 - **surface tilt	(°)**: description coming soon
 - **flow temperature	(°C)**: description coming soon


Category 4
-----------------------


.. csv-table:: Input for the upscaling sheet. Category 4: Time series.
   :header:  timestamp,dhi,pressure,temperature,windspeed,z0,dni,ghi,ground_temp,water_temp,groundwater_temp,screw_turbine.fix,electric_vehicle.fix

   01.01.2012 00:00,0,100119.3125,8.656125,5.9235,0.159,0,0,12.6,14.62006667,13.06,0.420911041,0
   01.01.2012 01:00,0,100113.836,8.9435,6.455,0.159,0,0,12.6,14.62006667,13.06,0.420911041,0
   01.01.2012 02:00,0,100102.5625,9.210125,6.8535,0.159,0,0,12.6,14.71342667,13.06,0.420911041,0
   01.01.2012 03:00,0,100075.5,9.6415,7.318,0.159,0,0,12.6,14.75492,13.06,0.420911041,0
   01.01.2012 04:00,0,100026.8555,9.9285,7.916,0.159,0,0,12.6,14.99350667,13.06,0.420911041,0
   …,…,…,…,…,…,…,…,…,…,…,…,…


- **timestamp**: description coming soon
- **dhi**: description coming soon
- **pressure**: description coming soon
- **temperature**: description coming soon
- **windspeed**: description coming soon
- **z0**: description coming soon
- **dni**: description coming soon
- **ghi**: description coming soon
- **ground_temp**: description coming soon
- **water_temp**: description coming soon
- **groundwater_temp**: description coming soon
- **screw_turbine.fix**: description coming soon
- **electric_vehicle.fix**: description coming soon


Standard Parameters
-------------------

Clustering
----------

References
==========
[1] Klemm, C., Budde J., Vennemann P., *Model Structure for urban energy system optimization models*, unpublished at the time of publication of this documentation, 2021.
