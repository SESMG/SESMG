# -*- coding: utf-8 -*-
"""
Functions for the creation of oemof energy system objects from a given 
spreadsheet scenario

@ Christian Klemm - christian.klemm@fh-muenster.de, 14.01.2020
"""


def buses(nodes_data, nodes):
    """
    Creates busses as defined in 'nodes_data' and adds them to the list of 
    components 'nodes'.

    ----    
        
    Keyword arguments:
        
        nodes_data : obj:'dict'
           -- dictionary containing data from excel scenario file. The 
           following data have to be provided: label, active, excess, shortage, 
           shortage costs [CU/kWh], excess costs [CU/kWh]
        
        nodes : obj:'list'
            -- list of components
            
    ----
    
    Returns:
       nodes_data : obj:'dict'
           -- dictionary containing data from excel scenario file    
           
    ----
    
    @ Christian Klemm - christian.klemm@fh-muenster.de, 14.01.2020

    """
    
    from oemof import solph
    import logging
    
    busd = {}
    nd=nodes_data
    for i, b in nd['buses'].iterrows():
        
        # Create a bus object for every bus, which is marked as "active"
        if b['active']:
            bus = solph.Bus(label=b['label'])
            nodes.append(bus)
            busd[b['label']] = bus
            logging.info('Bus created: ' + b['label'])
            
            # Create an excess sink for every bus, which is marked with "excess"
            if b['excess']:
                nodes.append(
                    solph.Sink(label=b['label'] + '_excess',
                               inputs={busd[b['label']]: solph.Flow(
                                   variable_costs=b['excess costs [CU/kWh]'],
                                   #nominal_value=1
                                   )}))
            
            # Create an shortage source for every bus, which is marked with "shortage"
            if b['shortage']:
                nodes.append(
                    solph.Source(label=b['label'] + '_shortage',
                                 outputs={busd[b['label']]: solph.Flow(
                                     variable_costs=b['shortage costs [CU/kWh]'])}))
    return busd










def sources(nodes_data, nodes, bus, weather_data):
    
    """
    Creates source objects as defined in 'nodes_data' and adds them to the 
    list of components 'nodes'.

    ----    
        
    Keyword arguments:
        
        nodes_data : obj:'dict'
           -- dictionary containing data from excel scenario file. The 
           following data have to be provided: label, active, output, 
           technology, variable costs [CU/kWh],existing capacity [kW], 
           min. investment capacity [kW], max. investment capacity [kW], 
           periodical costs [CU/(kW a)], technology database (PV ONLY), 
           inverter database (PV ONLY), Modul Model (PV ONLY), 
           Inverter Model (PV ONLY), reference value [kW], Azimuth (PV ONLY), 
           Surface Tilt (PV ONLY), Albedo (PV ONLY), Altitude (PV ONLY), 
           Latitude (PV ONLY), Longitude (PV ONLY)
           
        bus : obj:'dict'
           -- dictionary containing the busses of the energy system

        filename : obj:'str'
            -- path to xlsx scenario file
            
        nodes : obj:'list'
            -- list of components
            
        weather_data : obj:'str'
            -- path to csv weather data file

    ----
    
    @ Christian Klemm - christian.klemm@fh-muenster.de, 14.01.2020

    """
    
    from oemof import solph
    import logging
    
    #PV
    import pvlib
    from pvlib.pvsystem import PVSystem
    from pvlib.location import Location
    from pvlib.modelchain import ModelChain
    from pvlib.tools import cosd
    import feedinlib.weather as weather

    nd = nodes_data   
    busd = bus

    
    def create_commodity_source_object():
       nodes.append(
               solph.Source(label=so['label'],
                     outputs={busd[so['output']]: solph.Flow(
                        investment=solph.Investment(
                                ep_costs=so['periodical costs [CU/(kW a)]'],
                                minimum=so['min. investment capacity [kW]'],
                                maximum=so['max. investment capacity [kW]'],
                                existing=so['existing capacity [kW]']),
                         variable_costs=so['variable costs [CU/kWh]'])}))
       logging.info('Commodity Source created: ' + so['label'])        

    
    def create_pv_source_object():
                # loading feedinlib's weather data
                my_weather = weather.FeedinWeather()
                my_weather.read_feedinlib_csv(weather_data)
                
                # preparing the weather data to suit pvlib's needs
                # different name for the wind speed
        #        my_weather.data.rename(columns={'v_wind': 'wind_speed'}, inplace=True)
                
                # temperature in degree Celsius instead of Kelvin
                my_weather.data['temp_air'] = my_weather.data.temp_air - 273.15
                
                # calculate ghi
                my_weather.data['ghi'] = my_weather.data.dirhi + my_weather.data.dhi
                w = my_weather.data
                
                # time index from weather data set
                times = my_weather.data.index
                
                # get module and inverter parameter from sandia database
                pv_module = pvlib.pvsystem.retrieve_sam(so['technology database (PV ONLY)'])
                pv_inverter = pvlib.pvsystem.retrieve_sam(so['inverter database (PV ONLY)'])
                         
                # own module parameters
                pv_module = {
                    'module_parameters': pv_module[so['Modul Model (PV ONLY)']],
                    #'a': 0.2,
                    #'b': 0.00001,
                    #'c':0.001,
                    #'d': -0.0005,
                    'inverter_parameters': pv_inverter[so['Inverter Model (PV ONLY)']],
                    'surface_azimuth': so['Azimuth (PV ONLY)'],
                    'surface_tilt': so['Surface Tilt (PV ONLY)'],
                    'albedo': so['Albedo (PV ONLY)'],
                    }
                
                # own location parameter
                location = {
                    'altitude': so['Altitude (PV ONLY)'],
                    'name': 'Herne',
                    'latitude': so['Latitude (PV ONLY)'],
                    'longitude': so['Longitude (PV ONLY)'],
                    }
                
                # the following has been implemented in the pvlib ModelChain in the
                # complete_irradiance method (pvlib version > v0.4.5)
                if w.get('dni') is None:
                    w['dni'] = (w.ghi - w.dhi) / cosd(
                        Location(**location).get_solarposition(times).zenith)
                
                # pvlib's ModelChain
                mc = ModelChain(PVSystem(**pv_module),
                                Location(**location),
                                )
    
                mc.run_model(times, weather=w)
                df = mc.dc.p_mp.fillna(0)
                pv_time_series = df
    
                module_reference_value = so['reference value [kW] (PV ONLY)']
                
                nodes.append(
                       solph.Source(label=so['label'],
                             outputs={busd[so['output']]: solph.Flow(
                                investment=solph.Investment(
                                        ep_costs=so['periodical costs [CU/(kW a)]'],
                                        minimum=so['min. investment capacity [kW]'],
                                        maximum=so['max. investment capacity [kW]'],
                                        existing=so['existing capacity [kW]']),
                                actual_value = pv_time_series/module_reference_value,
                                fixed=True,
                                variable_costs=so['variable costs [CU/kWh]'])}))            
                              
                
                logging.info('Source created: ' + so['label'])


        
    
    # Create Source from "Sources" Table
    for i, so in nd['sources'].iterrows():
        
        # Create a source object for every source, which is marked as "active"
        if so['active']:
           
           ### Create Commodity Sources ###
           if so['technology'] == 'other':
               create_commodity_source_object()
                      
           ### Create Photovoltaic Sources ###  
           elif so['technology'] == 'photovoltaic':
               create_pv_source_object()
          
            ### Create Windpower Sources ###
           elif so['technology'] == 'windpower': 
               logging.info('WARNING: windpower plants can currently not be modelled. This feature will be added later.')








              
def sinks(nodes_data, bus, nodes, temperature_data, filename, weather_richardson):
    
    """
    Creates sinks objects as defined in 'nodes_data' and adds them to the 
    list of components 'nodes'.

    ----    
        
    Keyword arguments:
        
        nodes_data : obj:'dict'
           -- dictionary containing data from excel scenario file. The 
           following data have to be provided: label, active, input, input2, 
           load profile, nominal value [kW], annual demand [kWh/a], 
           occupants [RICHARDSON], building class [HEAT SLP ONLY], 
           wind class [HEAT SLP ONLY], fixed
           
        bus : obj:'dict'
           -- dictionary containing the busses of the energy system
           
        temperature_data : obj:'str' 
            -- path to csv file (stored in the program folder) containing 
                a temperature time series
                
        filename : obj:'str'
            -- path to xlsx scenario file
            
        nodes : obj:'list'
            -- list of components

    ----
    
    @ Christian Klemm - christian.klemm@fh-muenster.de, 14.01.2020

    """

    from oemof import solph
    import logging
    import os
    import pandas as pd
    import demandlib.bdew as bdew    
    
    #Richardson
    import copy
    import richardsonpy.classes.occupancy as occ
    import richardsonpy.functions.change_resolution as cr
    import richardsonpy.functions.load_radiation as loadrad
    import richardsonpy.classes.electric_load as eload
    import numpy as np

    def read_excel_cell(file, sheet, column):
        """
        Reads the first value of a specific column from a given excel sheet
        @Christian Klemm
        """
        df = pd.read_excel(file, sheet_name = sheet, usecols = column)
        value=df.at[df.index[0],df.columns[0]]
        return value
    
    def create_unfixed_sink_objects():            
        # set static inflow values    
        inflow_args = {'nominal_value': de['nominal value [kW]'],
                       'fixed': de['fixed']}   
   
        # create    
        nodes.append(    
            solph.Sink(label=de['label'],   
                       inputs={    
                           busd[de['input']]: solph.Flow(**inflow_args)}))
        logging.info('Sink created: ' + de['label'])        


    def create_timeseries_sink_objects():
        # set static inflow values    
        inflow_args = {'nominal_value': de['nominal value [kW]'],
                       'fixed': de['fixed']}   
                                                   
        # get time series for node and parameter    
        for col in nd['timeseries'].columns.values:    
            if col.split('.')[0] == de['label']:   
                inflow_args[col.split('.')[1]] = nd['timeseries'][col]
   
        # create    
        nodes.append(    
            solph.Sink(label=de['label'],   
                       inputs={    
                           busd[de['input']]: solph.Flow(**inflow_args)}))
        logging.info('Sink created: ' + de['label'])


    def create_residentialheatslp_sink_objects():
        # Import Data
        filename = temperature_data
        data = pd.read_csv(filename, sep=";")
        # Create DataFrame
        demand = pd.DataFrame(
                index=pd.date_range(pd.datetime(2012, 1, 1, 0),#Datum automatisch einlesen!
                                    periods=8760, freq='H')) # Perioden individuell anpassen!  ######### DATUM UND PERIODEN ANPASSEN!
            
        demand[de['load profile']] = bdew.HeatBuilding(
                demand.index, 
                temperature=data['temperature'],
                shlp_type=de['load profile'],
                building_class=de['building class [HEAT SLP ONLY]'],                   # wert individuell anpassen!
                wind_class=de['wind class [HEAT SLP ONLY]'],                       # Wert individuell anpassen!
                annual_heat_demand=1,
                name=de['load profile']).get_bdew_profile()
            
        #create Sink 
        nodes.append(
                solph.Sink(label=de['label'],
                   inputs={
                       busd[de['input']]: solph.Flow(nominal_value = de['annual demand [kWh/a]'],
                                                           actual_value = demand[de['load profile']],
                                                           fixed = True)}))                
        logging.info('Sink created: ' + de['label'])

    def create_commercialheatslp_sink_objects():
        # Import Data
        filename = os.path.join(os.path.dirname(__file__), temperature_data)
        data = pd.read_csv(filename, sep=";")
        # Create DataFrame
        demand = pd.DataFrame(
                index=pd.date_range(pd.datetime(2012, 1, 1, 0),#Datum automatisch einlesen!
                                    periods=8760, freq='H')) # Perioden individuell anpassen!  ######### DATUM UND PERIODEN ANPASSEN!
            
        demand[de['load profile']] = bdew.HeatBuilding(
                demand.index, 
                temperature=data['temperature'],
                shlp_type=de['load profile'],
                wind_class=de['wind class [HEAT SLP ONLY]'],                       # Wert individuell anpassen!
                annual_heat_demand=1,
                name=de['load profile']).get_bdew_profile()
            
        #create Sink 
        nodes.append(
                solph.Sink(label=de['label'],
                   inputs={
                       busd[de['input']]: solph.Flow(nominal_value = de['annual demand [kWh/a]'],
                                                           actual_value = demand[de['load profile']],
                                                           fixed = True)}))                
        logging.info('Sink created: ' + de['label']) 

    def create_richardson_sink_objects():
                
#        xlsx_dhi = pd.read_excel(filename,
#                            header=0,
#                            sheet_name='weather data',
#                            usecols=['dhi'])
#        dhi = xlsx_dhi.to_numpy()
#        
#        xlsx_dirhi = pd.read_excel(filename,
#                            header=0,
#                            sheet_name='weather data',
#                            usecols=['dhi'])
#        dirhi = xlsx_dirhi.to_numpy()
        
#        dirhi = pd.read_excel(filename,
#                            header=0,
#                            sheet_name='weather data',
#                            usecols=['dirhi'])         
        
        
        # Import Weather Data
        dirhi_csv = pd.read_csv(weather_richardson, usecols=[2], dtype=float) # Wert nicht auf spezielle SPalte beziehen, sondern auf Spaltennamen!!
        dirhi=dirhi_csv.values.flatten()        
        dhi_csv = pd.read_csv(weather_richardson, usecols=[1], dtype=float) # Wert nicht auf spezielle SPalte beziehen, sondern auf Spaltennamen!!
        dhi=dhi_csv.values.flatten() 
        #print(dhi)
        #print(type(dhi))
        
        temp_resolution = read_excel_cell((os.path.join(os.path.dirname(__file__), filename)), sheet = 'timesystem', column = [3])
        nb_occ = de['occupants [RICHARDSON]']
        # Workaround, because richardsonpy only allows a maximum of 5 occupants
        if nb_occ > 5:
            occ_ratio = nb_occ/5
            nb_occ = 5
        else:
            occ_ratio = 1
        
        if temp_resolution == 'H':
            timestep = 3600  # in seconds
        elif temp_resolution == 'h':
            timestep = 3600  # in seconds
        elif temp_resolution == 'min':
            timestep = 60  # in seconds
        elif temp_resolution == 's':
            timestep = 1  # in seconds
        else:
            logging.info('Invalid Temporal Resolution!')
            
        #  Generate occupancy object (necessary as input for electric load gen.)
        occ_obj = occ.Occupancy(number_occupants=nb_occ)
        
        #  Get radiation (necessary for lighting usage calculation)
        (q_direct, q_diffuse) = loadrad.get_rad_from_try_path()
        
        q_direct=dirhi
        g_diffuse=dhi
        
        #  Generate stochastic electric power object
        el_load_obj = eload.ElectricLoad(occ_profile=occ_obj.occupancy,
                                         total_nb_occ=nb_occ,
                                         q_direct=q_direct,
                                         q_diffuse=q_diffuse,
                                         timestep=timestep)
        
        #  Copy occupancy object, before changing its resolution
        #  (occ_obj.occupancy is the pointer to the occupancy profile array)
        occ_profile_copy = copy.copy(occ_obj.occupancy)
        
        load_profile = el_load_obj.loadcurve#[0:len(datetime_index)]
        richardson_demand = sum(el_load_obj.loadcurve) * timestep / (3600 * 1000)
        annual_demand = de['annual demand [kWh/a]']
        demand_ratio = annual_demand/richardson_demand
        
        #create
        nodes.append(
                  solph.Sink(label=de['label'],
                             inputs={busd[de['input']]: solph.Flow(nominal_value = 0.001*demand_ratio, # diesen Wert anpassen
                                                                 actual_value = load_profile,
                                                                 fixed = True)}))
        logging.info('Sink created: ' + de['label'])        


    def create_electricslp_sink_objects():       
        # Import SLP's
        year=2012 # in die excel tabelle 'timesystem' Eine Spalte mit Jahr einfügen, dann kann die hier ausgelesen werden.
        e_slp = bdew.ElecSlp(year)
        elec_demand = e_slp.get_profile({de['load profile']:1})
        temp_resolution = read_excel_cell(
              filename,
              sheet = 'timesystem', column = [3]) # am besten nicht über genaue zelle sondern über spaltennamen einlesen
        elec_demand = elec_demand.resample(temp_resolution).mean()
        
        #create
        nodes.append(
                  solph.Sink(label=de['label'],
                             inputs={busd[de['input']]: solph.Flow(nominal_value = de['annual demand [kWh/a]'], # diesen Wert anpassen
                                                                 actual_value = elec_demand[de['load profile']],
                                                                 fixed = True)}))
        logging.info('Sink created: ' + de['label'])


    
    nd = nodes_data
    busd = bus

    for i, de in nd['demand'].iterrows():
        heat_slps = ['efh', 'mfh'] 
        heat_slps_commercial = ['gmf','gpd','ghd','gwa','ggb','gko','gbd',
                                'gba','gmk','gbh','gga','gha']
        electricity_slps = ['h0', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6',
                            'l0', 'l1', 'l2']
        richardson = ['richardson']
        
        if de['active']:    

            ### Create Sinks un-fixed time-series ###        
            if de['load profile'] == 'x':
                create_unfixed_sink_objects()           
            
            ### Create Sinks with Timeseries ###        
            elif de['load profile'] == 'timeseries':
                create_timeseries_sink_objects()                
            
            ### Create Sinks with Heat SLP's ###                    
            elif de['load profile'] in heat_slps:
                create_residentialheatslp_sink_objects()

            elif de['load profile'] in heat_slps_commercial:
                create_commercialheatslp_sink_objects()
                
            ## Richardson                
            elif de['load profile'] in richardson:
                create_richardson_sink_objects()
                
            ### Create Sinks with Electricity SLP's ###            
            elif de['load profile'] in electricity_slps:
                create_electricslp_sink_objects()










def transformers(nodes_data, nodes, bus):

    """
    Creates transformers objects as defined in 'nodes_data' and adds them to 
    the list of components 'nodes'.

    ----    
        
    Keyword arguments:
        
        nodes_data : obj:'dict'
           -- dictionary containing data from excel scenario file. The 
           following data have to be provided: label, active, transformer type, 
           input, output, output2, efficiency, efficency2, 
           variable input costs [CU/kWh], variable output costs [CU/kWh], 
           existing capacity [kW], max. investment capacity [kW], 
           min. investment capacity [kW], periodical costs [CU/(kW a)]
           
        bus : obj:'dict'
           -- dictionary containing the busses of the energy system

        nodes : obj:'list'
            -- list of components

    ----
    
    @ Christian Klemm - christian.klemm@fh-muenster.de, 14.01.2020

    """
    
    from oemof import solph
    import logging
    
    def create_generic_transformer_object():
        # get time series for inflow of transformer    
#                for col in nd['timeseries'].columns.values:   
#                    if col.split('.')[0] == t['label']:    
#                        inflow_args[col.split('.')[1]] = nd['timeseries'][col]
   
                # create 
                if t['output2'] == 'None':                   
                    nodes.append(    
                        solph.Transformer(    
                            label=t['label'],    
                            #inputs={busd[t['input']]: solph.Flow(**inflow_args)},
                            inputs={busd[t['input']]: solph.Flow(variable_costs=t['variable input costs [CU/kWh]'])},  
                            outputs={busd[t['output']]: solph.Flow(variable_costs=t['variable output costs [CU/kWh]'],
                                                                   #fixed_costs=10,
                                                                   investment=solph.Investment(ep_costs=t['periodical costs [CU/(kW a)]'],
                                                                                             minimum=t['min. investment capacity [kW]'],
                                                                                             maximum=t['max. investment capacity [kW]'],
                                                                                             existing=t['existing capacity [kW]']
                                                                                             ))},   
                            conversion_factors={busd[t['output']]: t['efficiency']}))
                    logging.info('Transformer created: ' + t['label'])
                    
                else:    
                    nodes.append(    
                        solph.Transformer(    
                            label=t['label'],    
                            inputs={busd[t['input']]: solph.Flow(variable_costs=[t['variable input costs [CU/kWh]']])},    
                            outputs={busd[t['output']]: solph.Flow(variable_costs=t['variable output costs [CU/kWh]'],
                                                                investment=solph.Investment(ep_costs=t['periodical costs [CU/(kW a)]'],
                                                                                             minimum=t['min. investment capacity [kW]'],
                                                                                             maximum=t['max. investment capacity [kW]'],
                                                                                             existing=t['existing capacity [kW]']
                                                                                             )),
                                     busd[t['output2']]: solph.Flow()},   
                            conversion_factors={busd[t['output']]: t['efficiency'], busd[t['output2']]: t['efficiency2']}))
                    logging.info('Transformer created: ' + t['label'])        










    def create_genericchp_transformer_object():
        periods=len(datetime_index)                                     
        
        nodes.append( 
            solph.components.GenericCHP(
                label=t['label'],
                fuel_input={busd[t['input']]: solph.Flow(
                    H_L_FG_share_max=[t['share of flue gas loss at max heat extraction [GenericCHP]'] for p in range(0, periods)])},
                electrical_output={busd[t['output']]: solph.Flow(
                    P_max_woDH=[t['max. electric power without district heating [GenericCHP]'] for p in range(0, periods)],
                    P_min_woDH=[t['min. electric power without district heating [GenericCHP]'] for p in range(0, periods)],
                    Eta_el_max_woDH=[t['el. eff. at max. fuel flow w/o distr. heating [GenericCHP]'] for p in range(0, periods)],
                    Eta_el_min_woDH=[t['el. eff. at min. fuel flow w/o distr. heating [GenericCHP]'] for p in range(0, periods)])},
                heat_output={busd[t['output2']]: solph.Flow(
                    Q_CW_min=[t['minimal therm. condenser load to cooling water [GenericCHP]'] for p in range(0, periods)])},
                Beta=[t['power loss index [GenericCHP]'] for p in range(0, periods)],
                back_pressure=False))
        logging.info('Transformer created: ' + t['label'])


    
    busd=bus
    nd=nodes_data

    for i, t in nd['transformers'].iterrows():
        if t['active']:
            
            ### Create Generic Transformers ###               
            if t['transformer type'] == 'GenericTransformer':
                create_generic_transformer_object()
                
            ### Create Extraction Turbine CHPs ###           
            elif t['transformer type'] == 'ExtractionTurbineCHP':
                print('WARNING: ExtractionTurbineCHP are currently not a part of this model generator, but will be added later.')
            
            ### Create Generic CHPs ###           
            elif t['transformer type'] == 'GenericCHP':         ###Investment hinzufügen!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                create_genericchp_transformer_object()          #### Variable kosten hinzufügen!!!
                
            ### Create Offset Transformers ###            
            elif t['transformer type'] == 'OffsetTransformer':
                print('WARNING: OffsetTransformer are currently not a part of this model generator, but will be added later.')                
            
            ### Error Message for invalid Transformers ###          
            else:
                print('WARNING: \'' 
                      + t['label'] 
                      + '\' was not created, because \''
                      + t['transformer type'] 
                      + '\' is no valid transformer type.')
            
            
            
            
            
            
            
            
            
            
def storages(nodes_data, nodes, bus):
    
    """
    Creates storage objects as defined in 'nodes_data' and adds them to the 
    list of components 'nodes'.

    ----    
        
    Keyword arguments:
        
        nodes_data : obj:'dict'
           -- dictionary containing data from excel scenario file. The 
           following data have to be provided: label, active, bus, 
           existing capacity [kW], min. investment capacity [kW], 
           max. investment capacity [kW], periodical costs [CU/(kW a)], 
           capacity inflow, capacity outflow, capacity loss, efficiency inflow, 
           efficiency outflow, initial capacity, capacity min, capacity max,
           variable input costs, variable output costs
           
        bus : obj:'dict'
           -- dictionary containing the busses of the energy system

        nodes : obj:'list'
            -- list of components

    ----
    
    @ Christian Klemm - christian.klemm@fh-muenster.de, 14.01.2020

    """
 
    from oemof import solph
    import logging
    
    busd = bus
    nd = nodes_data
    
    for i, s in nd['storages'].iterrows():                                   ##### investment hinzufügen
        if s['active']:
            nodes.append(
                solph.components.GenericStorage(
                    label=s['label'],
                    inputs={busd[s['bus']]: solph.Flow(
                        nominal_value=s['capacity inflow'],
                        variable_costs=s['variable input costs'])},
                    outputs={busd[s['bus']]: solph.Flow(
                        nominal_value=s['capacity outflow'],
                        variable_costs=s['variable output costs'])},
    #                    nominal_storage_capacity=s['nominal capacity'],
                    loss_rate=s['capacity loss'],
                    #initial_storage_level=s['initial capacity'],
                    #max_storage_level=s['capacity max'],
                    #min_storage_level=s['capacity min'],
                    inflow_conversion_factor=s['efficiency inflow'],
                    outflow_conversion_factor=s['efficiency outflow'],
                    #nominal_storage_capacity=s['existing capacity [kW]'],
                    investment = solph.Investment(ep_costs=s['periodical costs [CU/(kW a)]'],
                                                  existing=s['existing capacity [kW]'],
                                                  minimum=s['min. investment capacity [kW]'],
                                                  maximum=s['max. investment capacity [kW]']
                                                  )
                #    investment = solph.Investment(s['ep_costs'])
                    ))
            logging.info('Storage created: ' + s['label'])
            
            
            
            
            
            
            
            
            
            
def links(nodes_data, nodes, bus):
    """
    Creates links objects as defined in 'nodes_data' and adds them to the 
    list of components 'nodes'.

    ----    
        
    Keyword arguments:
        
        nodes_data : obj:'dict'
           -- dictionary containing data from excel scenario file. The 
           following data have to be provided: label, active, bus_1, bus_2, 
           (un)directed, efficiency, existing capacity [kW], 
           min. investment capacity [kW], max. investment capacity [kW], 
           variable costs [CU/kWh], periodical costs [CU/(kW a)]
        
        bus : obj:'dict'
           -- dictionary containing the busses of the energy system
        
        nodes : obj:'list'
            -- list of components

    ----
    
    @ Christian Klemm - christian.klemm@fh-muenster.de, 14.01.2020

    """
    
 
    from oemof import solph
    import logging
    
    busd = bus
    nd = nodes_data
    
    def create_undirected_link():
        bus1 = busd[p['bus_1']]
        bus2 = busd[p['bus_2']]
        nodes.append(
            solph.custom.Link(
                label='undirected_powerline'
                      + '_' + p['bus_1']
                      + '_' + p['bus_2'],
                inputs={bus1: solph.Flow(),
                        bus2: solph.Flow()},
                outputs={bus1: solph.Flow(#nominal_value=p['existing capacity [kW]'],
                                          variable_costs=p['variable costs [CU/kWh]'],
                                          investment=solph.Investment(ep_costs=p['periodical costs [CU/(kW a)]'],
                                                                      minimum=p['min. investment capacity [kW]'],
                                                                      maximum=p['max. investment capacity [kW]'],
                                                                      existing=p['existing capacity [kW]']
                                                                      )),
                         bus2: solph.Flow(#nominal_value=p['existing capacity [kW]'],
                                          variable_costs=p['variable costs [CU/kWh]'],
                                          investment=solph.Investment(ep_costs=p['periodical costs [CU/(kW a)]'],
                                                                      minimum=p['min. investment capacity [kW]'],
                                                                      maximum=p['max. investment capacity [kW]'],
                                                                      existing=p['existing capacity [kW]']))},
                conversion_factors={(bus1, bus2): p['efficiency'],
                                    (bus2, bus1): p['efficiency']}))
        logging.info('Powerline created: ' + p['label'])
        
    def create_directed_link():
        bus1 = busd[p['bus_1']]
        bus2 = busd[p['bus_2']]
        nodes.append(
            solph.custom.Link(
                label='directed_powerline'
                      + '_' + p['bus_1']
                      + '_' + p['bus_2'],
                inputs={bus1: solph.Flow()},
                outputs={bus2: solph.Flow(#nominal_value=p['existing capacity [kW]'],
                                          variable_costs=p['variable costs [CU/kWh]'],
                                          investment=solph.Investment(ep_costs=p['periodical costs [CU/(kW a)]'],
                                                                      #minimum=p['min. investment capacity [kW]'],
                                                                      #maximum=p['max. investment capacity [kW]'],
                                                                      #existing=p['existing capacity [kW]']
                                                                      ))},
                conversion_factors={(bus1, bus2): p['efficiency']}))
        logging.info('Powerline created: ' + p['label'])


    for i, p in nd['powerlines'].iterrows():
        if p['active']:
            
            if p['(un)directed'] == 'undirected':
                create_undirected_link()
                
            elif p['(un)directed'] == 'directed':
                create_directed_link()
                
