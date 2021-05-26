Using the Scenario File
*************************************************

For the modeling and optimization of an energy system, parameters for all system components must be given in the model 
generator using the enclosed .xlsx file (editable with Excel, LibreOffice, …). The .xlsx file is divided into nine 
input sheets. In the "energysystem" sheet, general parameters are defined for the time horizon to be examined, in the 
sheets "buses", "sinks", "sources", "transformers", "storages" and "links" corresponding components are defined. In 
the sheet "time series", the performance of individual components can be stored. In the "weather data" sheet, the 
required weather data is stored. When completing the input file, it is recommended to enter the energy system step by 
step and to perform test runs in between, so that potential input errors are detected early and can be localized more 
easily. In addition to the explanation of the individual input sheets, an example energy system is built step by step 
in the following subchapters. The input file for this example is stored in the program folder "examples" and viewed on 
`GitHub <https://github.com/chrklemm/SESMG/tree/master/examples>`_. The following units are used throughout:

- capacity/performance in kW,
- energy in kWh,
- angles in degrees, and
- costs in cost units (CU).

Cost units are any scalable quantity used to optimize the energy system, such as euros or grams of carbon dioxide emissions.

Energysystem
=================================================

Within this sheet, the time horizon and the temporal resolution of the model is defined. The following parameters have to be entered:

- **start date**: Start of the modelling time horizon. Format: "YYYY-MM-DD hh:mm:ss";
- **end date**: End date of the modelling time horizon. Format: "YYYY-MM-DD hh:mm:ss"; and
- **temporal resolution**: For the modelling considered temporal resolution. Possible inputs: "a" (years), "d" (days), "h" (hours) "min" (minutes), "s" (seconds), "ms" (milliseconds).
- **periods**: Number of periods within the time horizon (one year with hourly resolution equals 8760 periods).
- **constraint costs** in (CU): Value in order to set a limit for the whole energysystem, e.g. carbon dioxide emissions. Set this field to "None" in order to ignore the limit. If you want to set a limit, you have to set specific values for each components seen below.

   
.. csv-table:: Exemplary input for the energy system
   :header: start date,end date,temporal resolution,periods,constraint costs 

   ,,,,(CU)
   2012-01-01 00:00:00,2012-12-30 23:00:00,h,8760,None
   
 

Buses
=================================================

Within this sheet, the buses of the energy system are defined. The following parameters need to be entered:

- **label**: Unique designation of the bus. The following format is recommended: "ID_energy sector_bus".
- **comment**: Space for an individual comment, e.g. an indication of which measure this component belongs to.
- **active**: Specifies whether the bus shall be included to the model. 0 = inactive, 1 = active. 
- **excess**: Specifies whether a sink is to be generated, which consumes excess energy. 0 = no excess sink will be generated; 1 = excess sink will be generated.
- **shortage**: Specifies whether to generate a shortage source that can compensate energy deficits or not. 0 = no shortage source will be generated; 1 = shortage source will be generated.
- **shortage costs** in (CU/kWh): Assigns a price per kWh to the purchase of energy from the shortage source. If the shortage source was deactivated, the fill character "0" is used. 
- **excess costs** in (CU/kWh): Assigns a price per kWh to the release of energy to the excess sink. If the excess sink was deactivated, the fill character "0" is used.
- **variable shortage constraint costs** in (CU/kWh): Assigns a price per kWh to the purchase of energy from the shortage source referring to the constraint limit set in the "energysystem" sheet. If the shortage source was deactivated, the fill character "0" is used. If not considering constraints fill character "0" is used.
- **variable excess constraint costs** in (CU/kWh): Assigns a price per kWh to the release of energy to the excess sink referring to the constraint limit set in the "energysystem" sheet. If the excess sink was deactivated, the fill character "0" is used. If not considering constraints fill character "0" is used.

.. csv-table:: Exemplary input for the buses sheet
   :header: label,comments,active,excess,shortage,excess costs,shortage costs,variable excess constraint costs,variable shortage constraint costs

   ,,,,,(CU/kWh),(CU/kWh),(CU/kWh),(CU/kWh)
   ID_electricity_bus,,1,0,1,0.000,0.300,0.00,474.00
   ID_heat_bus,,1,1,0,0.000,0.000,0.00,0.00
   ID_gas_bus,,1,0,1,0.000,0.070,0.00,0.00
   ID_cooling_bus,chiller,1,1,0,0.000,0.000,0.00,0.00
   ID_pv_bus,,1,1,0,-0.068,0.000,-56.00,0.00
   ID_hp_electricity_bus,heat pumps,1,1,1,0.000,0.220,0.00,474.00
   district_electricity_bus,delivering electr. to neighb. subsystems,0,0,0,0.000,0.000,0.00,0.00
   district_heat_bus,delivering heat to neighb. subsystems,0,0,0,0.000,0.000,0.00,0.00
   district_chp_electricity_bus,,0,0,1,0.000,0.000,-375.00,0.00
   district_gas_bus,,0,0,1,0.000,0.070,0.00,0.00
   
.. figure:: ../images/BSP_Graph_Bus.png
   :width: 100 %
   :alt: Bus_Graph
   :align: center

   Graph of the energy system, which is created by entering the example components. Two buses, a shortage source, and an excess sink were created by the input. The non-active components are not included in the graph above.


Sinks
=================================================

Within this sheet, the sinks of the energy system are defined. The following parameters need to be entered:

- **label**: Unique designation of the sink. The following format is recommended: "ID_energy sector_sink".
- **comment**: Space for an individual comment, e.g. an indication of which measure this component belongs to.
- **active**: Specifies whether the sink shall be included to the model. 0 = inactive, 1 = active.
- **fixed**: Indicates whether it is a fixed sink or not. 0 = not fixed; 1 = fixed.
- **input**: Space for an individual comment, e.g. an indication of which measure this component belongs to.
- **load profile**: Specifies the basis onto which the load profile of the sink is to be created. If the Richardson tool is to be used, "richardson" has to be inserted. For standard load profiles, its acronym is used. If a time series is used, "timeseries" must be entered and must be provided in the `Time series sheet`_. If the sink is not fixed, the fill character "x" has to be used.
- **nominal value** in (kW): Nominal performance of the sink. Required when "time series" has been entered into the "load profile". When SLP or Richardson is used, use the fill character "0" here.
- **annual demand** in (kWh/a): Annual energy demand of the sink. Required when using the Richardson Tool or standard load profiles. When using time series, the fill character "0" is used. 
- **occupants** [RICHARDSON]: Number of occupants living in the respective building. Only required when using the Richardson tool, use fill character "0" for other load profiles.
- **building class** [HEAT SLP ONLY]: BDEW building classes that coincide with the building locations are explained `here <https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/structure_of_energy_system/structure.html#sinks>`_.
- **wind class** [HEAT SLP ONLY]: wind classification for building location (0=not windy, 1=windy)
 
.. csv-table:: Exemplary input for the sinks sheet
   :header: label,comment,active,fixed,input,load profile,nominal value,annual demand,occupants,building class,wind class

   ,,,,,,(kW),(kWh/a),(richardson),(heat slp),(heat slp)
   ID_electricity_sink,H0 standard load profile sink,1,1,ID_electricity_bus,h0,0,5000.0,0,0,0
   ID_heat_sink,EFH standard load profile sink,1,1,ID_heat_bus,efh,0,30000.0,0,3,0
   ID_cooling_sink,fixed timeseries cooling demand,1,1,ID_cooling_bus,timeseries,1,0,0,0,0
   
.. figure:: ../images/BSP_Graph_sink.png
   :width: 100 %
   :alt: Sink_Graph
   :align: center

   Graph of the energy system, which is created by entering the example components. The non-active components are not included in the graph above.

Sources
=================================================
Within this sheet, the sources of the energy system are defined. Technology specific data (see 2nd line), must be filled in only if the respective technology is selected otherwise use 0. The following parameters have to be entered:

- **label**: Unique designation of the source. The following format is recommended: "ID_energy sector_source".
- **comment**: Space for an individual comment, e.g. an indication of which measure this component belongs to.
- **active**: Specifies whether the source shall be included to the model. 0 = inactive, 1 = active.
- **fixed**: Indicates whether it is a fixed source or not. 0 = not fixed; 1 = fixed.
- **output**: Specifies which bus the source is connected to.
- **technology**: Technology type of source. Input options: "photovoltaic", "windpower", "timeseries", "other", "solar_thermal_flat_plate", "concentrated_solar_power". Time series are automatically generated for photovoltaic systems and wind turbines. If "timeseries" is selected, a time series must be provided in the `Time series sheet`_.
Costs
-------------------------
- **variable costs** in (CU/kWh): Defines the variable costs incurred for a kWh of energy drawn from the source.
- **variable constraint costs** in (CU/kWh): Defines the variable costs incurred for a kWh of energy drawn from the source referring to the constraint limit set in the "energysystem" sheet. If not considering constraints fill character "0" is used.
- **existing capacity** in (kW): Existing capacity of the source before possible investments.
- **min. investment capacity** in (kW): Minimum capacity to be installed in case of an investment.
- **max. investment capacity** in (kW): Maximum capacity that can be added in the case of an investment. If no investment is possible, enter the value "0" here.
- **periodical costs** in (CU/(kW a)): Costs incurred per kW for investments within the time horizon.
- **periodical constraint costs** in (CU/(kW a)): Costs incurred per kW for investments within the time horizon referring to the constraint limit set in the "energysystem" sheet. If not considering constraints fill character "0" is used.
- **Non-Convex Investment**: Specifies whether the investment capacity should be defined as a mixed-integer variable, i.e. whether the model can decide whether NOTHING OR THE INVESTMENT should be implemented. Explained `here <https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/structure_of_energy_system/structure.html#investment>`_.
- **Fix Investment Costs** in (CU/a): Fixed costs of non-convex investments (in addition to the periodic costs).
Wind
-------------------------
- **Turbine Model**: Reference wind turbine model. Possible turbine types are listed `here <https://github.com/wind-python/windpowerlib/blob/dev/windpowerlib/oedb/turbine_data.csv>`_. 
- **Hub Height**: Hub height of the wind turbine. Which hub heights are possible for the selected reference turbine can be viewed `here <https://github.com/wind-python/windpowerlib/blob/dev/windpowerlib/oedb/turbine_data.csv>`_.
PV
-------------------------
- **technology database**: Database, from where module parameters are to be obtained. Recommended Database: "SandiaMod".
- **inverter database**: Database, from where inverter parameters are to be obtained. Recommended Database: "sandiainverter". For other databases `click here <https://sam.nrel.gov/photovoltaic/pv-cost-component.html>`_.
- **Modul Model**: Module name, according to the database used.
- **Inverter Model**: Inverter name, according to the database used.
- **Azimuth**: Specifies the orientation of the PV module in degrees. Values between 0 and 360 are permissible (0 = north, 90 = east, 180 = south, 270 = west). Only required for photovoltaic sources, use fill character "0" for other technologies.
- **Surface Tilt**: Specifies the inclination of the module in degrees (0 = flat). Only required for photovoltaic sources, use fill character "0" for other technologies.
- **Albedo**: Specifies the albedo value of the reflecting floor surface. Only required for photovoltaic sources, use fill character "0" for other technologies.
- **Altitude**: Height (above mean sea level) in meters of the photovoltaic module. Only required for photovoltaic sources, use fill character "0" for other technologies.
- **Latitude**: Geographic latitude (decimal number) of the photovoltaic module. Only required for photovoltaic sources, use fill character "0" for other technologies.
- **Longitude**: Geographic longitude (decimal number) of the photovoltaic module. Only required for photovoltaic sources, use fill character "0" for other technologies.
Concentrated Solar Power
------------------------------
.. note::
	upcoming feature
Solar Thermal Flatplate
------------------------------
.. note:: 
	upcoming feature 
Timeseries
-------------------------
If you have choosen the technology "timeseries", you have to include a timeseries in the  `Time series sheet`_ or use default one. 

Commodity
-------------------------
If you have choosen the technology "other", the solver has the opportunity to continuously adjust the power.

.. csv-table:: Exemplary input for the sources sheet
   :header: label,comment,active,fixed,technology,output,input,existing capacity,min. investment capacity,max. investment capapcity,non-convex investment,fix investment costs,variable costs,periodical costs,variable constraint costs,periodical constraint costs,Turbine Model,Hub Height,technology database,inverter database,Modul Model,Inverter Model,Albedo,Altitude,Azimuth,Surface Tilt,Latitude,Longitude,ETA 0,A1,A2,C1,C2,Temperature Inlet,Temperature Difference,Conversion Factor,Peripheral Losses,Electric Consumption,Cleanliness
   
   ,,,,,,solar heat,(kW),(kW),(kW),,(CU/a),(CU/kWh),(CU/(kW a)),(CU/kWh),(CU/(kW a)),windpower,windpower,PV,PV,PV,PV,PV,(m)| PV,(°),(°),(°),(°),solar heat,solar heat,solar heat,solar heat,solar heat,(°C) | solar heat,(°C)|solar heat,(sqm/kW) | solar heat,solar heat,solar heat,solar heat
   ID_photovoltaic_electricity_source,,1,1,photovoltaic,ID_pv_bus,None,0,0,20,0,0,0,90,56,0,0,0,SandiaMod,sandiainverter,Panasonic_VBHN235SA06B__2013_,ABB__MICRO_0_25_I_OUTD_US_240__240V_,0.18,60,180,35,52.13,7.36,0,0,0,0,0,0,0,0,0,0,0
   ID_solar_thermal_source,,0,1,solar_thermal_flat_plate,ID_heat_bus,ID_electricity_bus,0,0,20,0,0,0,40,25,0,0,0,0,0,0,0,0,0,20,10,52.13,7.36,0.719,1.063,0.005,0,0,40,15,1.89941306,0.05,0.06,0
   wind_turbine,,0,1,windpower,electricity_bus,None,0,0,30,0,0,0,100,9,0,E-126/4200,135,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
   

.. figure:: ../images/BSP_Graph_source.png
   :width: 100 %
   :alt: Source_Graph
   :align: center

   Graph of the energy system, which is created by entering the example components of sources sheet. The non-active components are not included in the graph above.
   
Transformers
=================================================

Within this sheet, the transformers of the energy system are defined. 

The following parameters have to be entered:


- **label**: Unique designation of the transformer. The following format is recommended: "ID_energy sector_transformer".
- **comment**: Space for an individual comment, e.g. an indication of which measure this component belongs to.
- **active**: Specifies whether the transformer shall be included to the model. 0 = inactive, 1 = active.
- **transformer type**: Indicates what kind of transformer it is. Possible entries: "GenericTransformer" for linear transformers with constant efficiencies; "GenericCHP" for transformers with varying efficiencies; "compression_heat_transformer"; "absorption_heat_transformer".
- **mode**: Specifies, if a compression or absorption heat transformer is working as "chiller" or "heat_pump". Only required if "transformer type" is set to "compression_heat_transformer" or "absorption_heat_transformer". Otherwise has to be set to "None", "none", "0".
- **input**: Specifies the bus from which the input to the transformer comes from.
- **output**: Specifies bus to which the output of the transformer is forwarded to. For CHP Transformers it should be the electric output.
- **output2**: Specifies the bus to which the output of the transformer is forwarded to, if there are several outputs. If there is no second output, the fill character "0" must be entered here.

Costs
---------------------
- **variable input costs** in (CU/kWh): Variable costs incurred per kWh of input energy supplied.
- **variable output costs** in (CU/kWh): Variable costs incurred per kWh of output energy supplied.
- **variable output costs 2** in (CU/kWh): Variable costs incurred per kWh of output 2 energy supplied.
- **variable input constraint costs** in (CU/kWh): Variable constraint costs incurred per kWh of input energy supplied referring to the constraint limit set in the "energysystem" sheet. If not considering constraints fill character "0" is used.
- **variable output constraint costs** in (CU/kWh): Variable constraint costs incurred per kWh of output energy supplied referring to the constraint limit set in the "energysystem" sheet. If not considering constraints fill character "0" is used.
- **variable output constraint costs 2** in (CU/kWh): Variable constraint costs incurred per kWh of output 2 energy supplied referring to the constraint limit set in the "energysystem" sheet. If not considering constraints fill character "0" is used.
- **existing capacity** in (kW): Already installed capacity of the transformer.
- **min investment capacity** in (kW): Minimum transformer capacity to be installed.
- **max investment capacity** in (kW): Maximum  installable transformer capacity in addition to the previously existing one.
- **periodical costs** in (CU/a): Costs incurred per kW for investments within the time horizon.
- **periodical constraint costs** in (CU/(kW a)): Constraint costs incurred per kW for investments within the time horizon. If not considering constraints fill character "0" is used.
- **Non-Convex Investment**: Specifies whether the investment capacity should be defined as a mixed-integer variable, i.e. whether the model can decide whether NOTHING OR THE INVESTMENT should be implemented. Explained `here <https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/structure_of_energy_system/structure.html#investment>`_.
- **Fix Investment Costs** in (CU/a): Fixed costs of non-convex investments (in addition to the periodic costs)
Generic Transformer
------------------------
- **efficiency**: Specifies the efficiency of the first output. Values between 0 and 1 are allowed entries.
- **efficiency2**: Specifies the efficiency of the second output, if there is one. Values between 0 and 1 are entered. If there is no second output, the fill character "0" must be entered here.
GenericCHP
------------------------
- **min. share of flue gas loss**: Percentage flue gas losses of the operating point with maximum heat extraction.
- **max. share of flue gas loss**:  Percentage flue gas losses of the operating point with minimum heat extraction.
- **min. electric power** in (kW): Minimum electrical power supply without heat extraction (district heating).
- **max. electric power** in (kW): Maximum electrical power supply without heat extraction (district heating).
- **min. electric efficiency**: Specifies the minimum electric efficiency without heat extraction (district heating). Values between 0 and 1 are allowed entries.
- **max. electric efficiency**: Specifies the minimum electric efficiency without heat extraction (district heating). Values between 0 and 1 are allowed entries.
- **minimal thermal output power** in (kW): Heat output taken from the exhaust gas via a condenser even in purely electric operation.
- **electric power loss index**: Reduction of the electrical power by "electric power loss index * extracted thermal power".
- **back pressure**: Defines rather the end pressure of "Turbine CHP" is higher than ambient pressure (input value has to be "1") or not (input value has to be "0"). For "Motoric CHP" it has to be "0".
Compression Heat Transformer
---------------------------------
The following parameters are only required, if "transformer type" is set to "compression_heat_transformer":

- **heat source**: Specifies the heat source. Possible heat sources are "GroundWater", "Ground", "Air" and "Water" possible.
- **temperature high** in (°C): Temperature of the high temperature heat reservoir. Only required if "mode" is set to "heat_pump".
- **temperature low** in (°C): Cooling temperature needed for cooling demand. Only required if "mode" is set to "chiller".
- **quality grade**: To determine the COP of a real machine a scale-down factor (the quality grade) is applied on the Carnot efficiency (see `oemof.thermal <https://github.com/wind-python/windpowerlib/blob/dev/windpowerlib/oedb/turbine_data.csv>`_).
- **area** in (sqm): Open spaces for ground-coupled compression heat transformers (GC-CHT).
- **length of the geoth. probe** in (m): Length of the vertical heat exchanger, only for GC-CHT.
- **heat extraction** in (kW/(m*a)): Heat extraction for the heat exchanger referring to the location, only for GC-CHT.
- **min. borehole area** in (sqm): Limited space due to the regeneation of the ground source, only for GC-CHT.
- **temp threshold icing**: Temperature below which icing occurs (see `oemof.thermal <https://github.com/wind-python/windpowerlib/blob/dev/windpowerlib/oedb/turbine_data.csv>`_). Only required if "mode" is set to "heat_pump".
- **factor icing**: COP reduction caused by icing (see `oemof.thermal <https://github.com/wind-python/windpowerlib/blob/dev/windpowerlib/oedb/turbine_data.csv>`_). Only required if "mode" is set to "heat_pump".
Absorption Heat Transformer
--------------------------------
The following parameters are only required, if "transformer type" is set to "absorption_heat_transformer":

- **name**: Defines the way of calculating the efficiency of the absorption heat transformer. Possible inputs are: "Rotartica", "Safarik", "Broad_01", "Broad_02", and "Kuehn". "Broad_02" refers to a double-effect absorption chiller model, whereas the other keys refer to single-effect absorption chiller models.
- **high temperature** in (°C): Temperature of the heat source, that drives the absorption heat transformer.
- **chilling temperature** in (°C): Output temperature which is needed for the cooling demand.
- **electrical input conversion factor**: Specifies the relation of electricity consumption to energy input. Example: A value of 0,05 means, that the system comsumes 5 % of the input energy as electric energy.
- **recooling temperature difference** in (°C): Defines the temperature difference between temperature source for recooling and recooling cycle.

  
.. csv-table:: Exemplary input for the transformers sheet
   :header: label,comment,active,transformer type,mode,input,output,output2,efficiency,efficiency2,existing capacity,min. investment capacity,max. investment capacity,non-convex investment,fix investment costs,variable input costs,variable output costs,variable output costs 2,periodical costs,variable input constraint costs,variable output constraint costs,variable output constraint costs 2,periodical constraint costs,heat source,temperature high,temperature low,quality grade,area,length of the geoth. probe,heat extraction,min. borehole area,temp. threshold icing,factor icing,name,high temperature,chilling temperature,electrical input conversion factor,recooling temperature difference,min. share of flue gas loss,max. share of flue gas loss,min. electric power,max. electric power,min. electric efficiency, max. electric efficiency,minimal thermal output power,elec. power loss index,back pressure
   
	,,,,,,,,,,(kW),(kW),(kW),,(CU/a),(CU/kWh),(CU/kWh),(CU/kWh),(CU/(kW a)),(CU/kWh),(CU/kWh),(CU/kWh),(CU/(kW a)),,(°C),(°C),,(m²),(`m`),(kW/(m*a)),(m²),(°C),,,(°C),(°C),,(°C),,,(kW),(kW),,,(kW)		   
 	ID_gasheating_transformer,,1,GenericTransformer,0,ID_gas_bus,ID_heat_bus,None,0.85,0,10,0,20,0,0,0,0,0,70,0,200,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0  
	ID_GCHP_transformer,ground-coupled heat pump,1,compression_heat_transformer,heat_pump,ID_hp_electricity_bus,ID_heat_bus,None,1,0,0,0,20,0,0,0,0,0,115.57,0,0,0,0,Ground,60,0,0.6,1000,100,0.05,100,3,0.8,0,0,0,0,0,0,0,0,0,0,0,0,0,0
	ID_ASCH_transformer,air source chiller,0,compression_heat_transformer,chiller,ID_hp_electricity_bus,ID_cooling_bus,None,1,0,0,0,20,0,0,0,0,0,100,0,0,0,0,Air,0,-10,0.4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
	ID_AbsCH_transformer,absorption chiller,0,absorption_heat_transformer,chiller,ID_hp_electricity_bus,ID_cooling_bus,None,1,0,0,0,20,0,0,0,0,0,100,0,0,0,0,0,0,0,0,0,0,0,0,0,0,Kuehn,85,10,0.05,6,0,0,0,0,0,0,0,0,0
	ID_ASHP_transformer,air source heat pump,1,compression_heat_transformer,heat_pump,ID_hp_electricity_bus,ID_heat_bus,None,1,0,0,0,20,0,0,0,0,0,112.78,0,0,0,0,Air,60,0,0.4,0,0,0,0,3,0.8,0,0,0,0,0,0,0,0,0,0,0,0,0,0
	ID_chp_transformer,,0,GenericTransformer,0,district_gas_bus,district_chp_electricity_bus,district_heat_bus,0.35,0.55,0,0,20,0,0,0,0,0,50,130,375,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0   
	
.. figure:: ../images/BSP_Graph_transformer.png
   :width: 100 %
   :alt: Transformer_Graph
   :align: center

   Graph of the energy system, which is created by entering the example components. The non-active components are not included in the graph above.

Storages
=================================================

Within this sheet, the sinks of the energy system are defined. The following parameters have to be entered:

- **label**: Unique designation of the storage. The following format is recommended: "ID_energy sector_storage".
- **comment**: Space for an individual comment, e.g. an indication of which measure this component belongs to.
- **active**: Specifies whether the storage shall be included to the model. 0 = inactive, 1 = active.
- **storage type**: Defines whether the storage is a "Generic" or a "Stratified" sorage. These two inputs are possible.
- **bus**: Specifies which bus the storage is connected to.
- **input/capacity ratio** (invest): Indicates the performance with which the memory can be charged.
- **output/capacity ratio** (invest): Indicates the performance with which the memory can be discharged.
- **efficiency inflow**: Specifies the charging efficiency.
- **efficiency outflow**: Specifies the discharging efficiency.
- **initial capacity**: Specifies how far the memory is loaded at time 0 of the simulation. Value must be between 0 and 1.
- **capacity min**: Specifies the minimum amount of memory that must be loaded at any given time. Value must be between 0 and 1.
- **capacity max**: Specifies the maximum amount of memory that can be loaded at any given time. Value must be between 0 and 1.

Costs
--------------------
- **existing capacity** in (kW): Previously installed capacity of the storage.
- **min. investment capacity** in (kW): Minimum storage capacity to be installed.
- **max. investment capacity** in (kW): Maximum in addition to existing capacity, installable storage capacity.
- **Non-Convex Investment**: Specifies whether the investment capacity should be defined as a mixed-integer variable, i.e. whether the model can decide whether NOTHING OR THE INVESTMENT should be implemented.  Explained `here <https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/structure_of_energy_system/structure.html#investment>`_.
- **Fix Investment Costs** in (CU/a): Fixed costs of non-convex investments (in addition to the periodic costs)
- **variable input costs**: Indicates how many costs arise for charging with one kWh.
- **variable output costs**: Indicates how many costs arise for charging with one kWh.
- **periodical costs** in (CU/a): Costs incurred per kW for investments within the time horizon.
- **variable input constraint costs**: Indicates how many costs arise for charging with one kWh referring to the constraint limit set in the "energysystem" sheet. If not considering constraints fill character "0" is used.
- **variable output constraint costs**: Indicates how many costs arise for charging with one kWh referring to the constraint limit set in the "energysystem" sheet. If not considering constraints fill character "0" is used.
- **periodical constraint costs** in (CU/a): Costs incurred per kW for investments within the time horizon referring to the constraint limit set in the "energysystem" sheet. If not considering constraints fill character "0" is used.
Generic Storage
---------------------
- **capacity loss** (Generic only): Indicates the storage loss per time unit. Only required, if the "storage type" is set to "Generic". 
Stratified Storage
---------------------
- **diameter** in (m) | (Stratified Storage): Defines the diameter of a stratified thermal storage, which is necessary for the calculation of thermal losses.
- **temperature high** in (°C) | (Stratified Storage): Outlet temperature of the stratified thermal storage.
- **temperature low** in (°C) | (Stratified Storage): Inlet temperature of the stratified thermal storage.
- **U value** in (W/(sqm*K)) | (Stratified Storage): Thermal transmittance coefficient

.. csv-table:: Exemplary input for the storages sheet
   :header: label,comment,active,storage type,bus,input/capacity ratio,output/capacity ratio,efficiency inflow,efficiency outflow,initial capacity,capacity min,capacity max,existing capacity,min. investment capacity,max. investment capacity,non-convex investment,fix investment costs,variable input costs,variable output costs,periodical costs,variable input constraint costs,variable output constraint costs,periodical constraint costs,capacity loss,diameter,temperature high,temperature low,U value

	,,,,,(invest),(invest),,,,,,(kWh),(kWh),(kWh),,(CU/a),(CU/kWh),(CU/kWh),(CU/(kWh a)),(CU/kWh),(CU/kWh),(CU/(kWh a)),Generic Storage,(`m`) | Stratified Storage,(°C) | Stratified Storage,Stratified Storage,(W/(m²*K)) | Stratified Storage
	ID_battery_storage,,1,Generic,ID_electricity_bus,0.17,0.17,1,0.98,0,0.1,1,0,0,100,0,0,0,0,70,0,0,400,0,0,0,0,0
	ID_thermal_storage,,1,Generic,ID_heat_bus,0.17,0.17,1,0.98,0,0.1,0.9,0,0,100,0,0,0,20,35,0,0,100,0,0,0,0,0
	ID_stratified_thermal_storage,,0,Stratified,ID_heat_bus,0.2,0.2,1,0.98,0,0.05,0.95,0,0,100,0,0,0,20,35,0,0,100,0,0.8,60,40,0.04
	district_battery_storage,,0,Generic,district_electricity_bus,0.17,0.17,1,0.98,0,0.1,1,0,0,1000,0,0,0,0,10,0,0,10,0,0,0,0,0
	
.. figure:: ../images/BSP_Graph_Storage.png
   :width: 100 %
   :alt: Transformer_Graph
   :align: center

   Graph of the energy system, which is created after entering the example components. One storage has been created by the storage sheet.The non-active components are not included in the graph above.
   
Links
=================================================

Within this sheet, the links of the energy system are defined. The following parameters have 
to be entered:

- **label**: Unique designation of the link. The following format is recommended: "ID_energy sector_transformer"
- **comment**: Space for an individual comment, e.g. an indication of  which measure this component belongs to.
- **active**: Specifies whether the link shall be included to the model. 0 = inactive, 1 = active. 
- **bus_1**: First bus to which the link is connected. If it is a directed link, this is the input bus.
- **bus_2**: Second bus to which the link is connected. If it is a directed link, this is the output bus.
- **(un)directed**: Specifies whether it is a directed or an undirected link. Input options: "directed", "undirected".
- **efficiency**: Specifies the efficiency of the link. Values between 0 and 1 are allowed entries.
Costs
-------------------
- **variable output costs** in (CU/kWh): Specifies the efficiency of the first output. Values between 0 and 1 are allowed entries.
- **variable constraint costs** in (CU/kWh): Costs incurred per kWh referring to the constraint limit set in the "energysystem" sheet. If not considering constraints fill character "0" is used.
- **existing capacity** in (kW): Already installed capacity of the link.
- **min. investment capacity** in (kW): Minimum, in addition to existing capacity, installable capacity.
- **max. investment capacity** in (kW): Maximum capacity to be installed.
- **periodical costs** in (CU/(kW a)): Costs incurred per kW for investments within the time horizon.
- **Non-Convex Investment**: Specifies whether the investment capacity should be defined as a mixed-integer variable, i.e. whether the model can decide whether NOTHING OR THE INVESTMENT should be implemented. Explained `here <https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/structure_of_energy_system/structure.html#investment>`_.
- **Fix Investment Costs** in (CU/a): Fixed costs of non-convex investments (in addition to the periodic costs)

.. csv-table:: Exemplary input for the link sheet
   :header: label,comment,active,(un)directed,bus1,bus2,efficiency,existing capacity,min. investment capacity,max. investment capacity,non-convex investment,fix investment costs,variable output costs,periodical costs,variable constraint costs,periodical constraint costs

	,,,,,,,(kW),(kW),(kW),,(CU/a),(CU/kWh),(CU/(kW a)),(CU/kWh),(CU/(kW a))
	ID_pv_to_ID_electricity_link,,1,directed,ID_pv_bus,ID_electricity_bus,1,0,0,0,0,0,0,0,0,0
	ID_electricity_to_ID_hp_electricity_bus,,1,directed,ID_electricity_bus,ID_hp_electricity_bus,1,0,0,0,0,0,0,0,0,0
	districtheat_directed_link,,0,directed,district_heat_bus,ID_heat_bus,0.85,0,0,0,0,0,0,0,0,0
	districtheat_undirected_link,,0,undirected,district_heat_bus,ID_heat_bus,0.85,0,0,0,0,0,0,0,0,0
	district_electricity_link,,0,directed,district_electricity_bus,ID_electricity_bus,1,0,0,0,0,0,0.1438,0,0,0
	district_chp_to_district_electricity_bus,,0,directed,district_chp_electricity_bus,district_electricity_bus,1,0,0,0,0,0,0.1438,0,0,0
	ID_pv_to_district_electricity_link,,0,directed,ID_pv_bus,ID_electricity_bus,1,0,0,0,0,0,0.1438,0,0,0
	
.. figure:: ../images/BSP_Graph_link.png
   :width: 100 %
   :alt: bsp-graph-link
   :align: center

   Graph of the energy system, which is created by entering the example components. One link has been created by the addition of the links sheet

.. _`Time series sheet`:

Time Series
=================================================

Within this sheet, time series of components of which no automatically created time series exist, are stored. More 
specifically, these are sinks to which the property "load profile" have been assigned as "timeseries" and sources 
with the "technology" property "timeseries". The following parameters have to be entered:

- **timestamp**: Points in time to which the stored time series are related. Should be within the time horizon defined in the sheet "timesystem".
- **timeseries**: Time series of a sink or a source  which has been assigned the property "timeseries" under the attribute "load profile" or "technology. Time series contain a value between 0 and 1 for each point in time, which indicates the proportion of installed capacity accounted for by the capacity produced at that point in time. In the header line, the name must rather be entered in the format "componentID.fix" if the component enters the power system as a fixed component or it requires two columns in the format "componentID.min" and "componentID.max" if it is an unfixed component. The columns "componentID.min/.max" define the range that the solver can use for its optimisation.

 
 
.. csv-table:: Exemplary input for time series sheet
   :header: timestamp,residential_electricity_demand.actual_value,fixed_timeseries_electricty_source.fix, unfixed_timeseries_electricty_source.min,unfixed_timeseries_electricty_source.max,fixed_timeseries_electricity_sink.fix,unfixed_timeseries_electricity_sink.min,unfixed_timeseries_electricity_sink.max,fixed_timeseries_cooling_demand_sink.fix

   2012-01-01 00:00:00,0.559061982,0.000000,0.000000,1.000000,0.000000,0.000000,1.000000,100
   2012-01-01 01:00:00,0.533606486,0.041667,0.000000,0.500000,0.041667,0.000000,0.500000,100
   2012-01-01 02:00:00,0.506058757,0.083333,0.000000,0.333333,0.083333,0.000000,0.333333,100
   2012-01-01 03:00:00,0.504140877,0.125000,0.000000,0.250000,0.125000,0.000000,0.250000,100
   2012-01-01 04:00:00,0.507104873,0.166667,0.000000,0.200000,0.166667,0.000000,0.200000,100
   2012-01-01 05:00:00,0.511376515,0.208333,0.000000,0.166667,0.208333,0.000000,0.166667,100
   2012-01-01 06:00:00,0.541801064,0.250000,0.000000,0.142857,0.250000,0.000000,0.142857,100
   2012-01-01 07:00:00,0.569261616,0.291667,0.000000,0.125000,0.291667,0.000000,0.125000,100
   2012-01-01 08:00:00,0.602998867,0.333333,0.000000,0.111111,0.333333,0.000000,0.111111,100
   2012-01-01 09:00:00,0.629064598,0.375000,0.000000,0.100000,0.375000,0.000000,0.100000,100






Weather Data
=================================================

If electrical load profiles are simulated with the Richardson tool, heating load profiles with the demandlib or 
photovoltaic systems with the feedinlib, weather data must be stored here. The weather 
data time system should be in conformity with the model’s time system, defined in the sheet "timesystem".

- **timestamp**: Points in time to which the stored weather data are related. 
- **dhi**: diffuse horizontal irradiance in W/m\ :sup:`2`
- **dirhi**: direct horizontal irradiance in W/m\ :sup:`2`
- **pressure**: air pressure in Pa
- **windspeed**: wind speed, measured at 10 m height, in unit m/s
- **z0**: roughness length of the environment in units m
- **ground_temp**: constant ground temperature at 100 m depth
- **water_temp**: varying water temperature of a river depending on the air temperature
- **groundwater_temp**: constant temperatur of the ground water at 6 - 10 m depth in North Rhine-Westphalia

.. csv-table:: Exemplary input for weather data
   :header: timestamp,dhi,dirhi,pressure,temperature,windspeed,z0,ground_temp,water_temp,groundwater_temp

   2012-01-01 00:00:00,0.00,0.00,98405.70,10.33,7.2,0.15,13.7,14.62,13.06
   2012-01-01 01:00:00,0.00,0.00,98405.70,10.33,7.8,0.15,13.7,14.62,13.06
   2012-01-01 02:00:00,0.00,0.00,98405.70,10.48,7.7,0.15,13.7,14.71,13.06
   2012-01-01 03:00:00,0.00,0.00,98405.70,10.55,7.7,0.15,13.7,14.75,13.06
   2012-01-01 04:00:00,0.00,0.00,98405.70,10.93,7.8,0.15,13.7,14.99,13.06
   2012-01-01 05:00:00,0.00,0.00,98405.70,10.90,8.5,0.15,13.7,14.97,13.06
   2012-01-01 06:00:00,0.00,0.00,98405.70,10.88,8.5,0.15,13.7,14.96,13.06
   2012-01-01 07:00:00,0.00,0.00,98405.70,11.22,7.9,0.15,13.7,15.17,13.06
   2012-01-01 08:00:00,0.00,0.00,98405.70,11.68,8.7,0.15,13.7,15.46,13.06
   2012-01-01 09:00:00,0.56,0.56,98405.70,11.87,8.6,0.15,13.7,15.57,13.06
   2012-01-01 10:00:00,13.06,13.06,98405.70,11.65,8.0,0.15,13.7,15.44,13.06


