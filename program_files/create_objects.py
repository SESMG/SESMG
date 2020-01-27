# -*- coding: utf-8 -*-
"""
Functions for the creation of oemof energy system objects from a given set 
of object parameters.

@ Christian Klemm - christian.klemm@fh-muenster.de, 27.01.2020
"""

from oemof import solph
import logging
import os
import pandas as pd
import datetime

def buses(nodes_data, nodes):
    """
    Creates bus objects with the parameters given in 'nodes_data' and adds 
    them to the list of components 'nodes'.

    ----    
        
    Keyword arguments:
        
        nodes_data : obj:'dict'
           -- dictionary containing parameters of the buses to be created. The 
           following parameters have to be provided: label, active, excess, 
           shortage, shortage costs [CU/kWh], excess costs [CU/kWh]
        
        nodes : obj:'list'
            -- list of components created before (can be empty)
            
    ----
    
    Returns:
       busd : obj:'dict'
           -- dictionary containing all buses created   
           
    ----
    
    @ Christian Klemm - christian.klemm@fh-muenster.de, 15.01.2020

    """
    
    busd = {}
    nd=nodes_data
    for i, b in nd['buses'].iterrows():
        
        # Create a bus object for every bus, which is marked as "active"
        if b['active']:
            bus = solph.Bus(label=b['label'])
            nodes.append(bus)
            busd[b['label']] = bus
            logging.info('   '+'Bus created: ' + b['label'])
            
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










def sources(nodes_data, nodes, bus, filepath):
    
    """
    Creates source objects with the parameters given in 'nodes_data' and adds 
    them to the list of components 'nodes'. If the parameter 'technology' in 
    nodes_data is labeled as 'commodity source', a source with defined 
    timeseries will be created. If technology is labeled as 'photovoltaic' a 
    photovoltaic system component will be created.
    

    ----    
        
    Keyword arguments:
        
        nodes_data : obj:'dict'
           -- dictionary containing parameters of sources to be created. The 
           following data have to be provided: label, active, output, 
           technology, variable costs [CU/kWh], existing capacity [kW], 
           min. investment capacity [kW], max. investment capacity [kW], 
           periodical costs [CU/(kW a)], technology database (PV ONLY), 
           inverter database (PV ONLY), Modul Model (PV ONLY), 
           Inverter Model (PV ONLY), Azimuth (PV ONLY), 
           Surface Tilt (PV ONLY), Albedo (PV ONLY), Altitude (PV ONLY), 
           Latitude (PV ONLY), Longitude (PV ONLY)
           
        bus : obj:'dict'
           -- dictionary containing the buses of the energy system

        filename : obj:'str'
            -- path to .xlsx scenario file
            
        nodes : obj:'list'
            -- list of components created before (can be empty)
            
        filepath : obj:'str'
            -- path to .xlsx scenario-file containing a "weather data" sheet 
            with timeseries for
               - "dhi" (diffuse horizontal irradiation) W/m^2
               - "dirhi" (direct horizontal irradiance) W/m^2
               - "pressure" in Pa
               - "temperature" in °C
               - "windspeed" in m/s
               - "z0" (roughness length) in m
               

    ----
    
    @ Christian Klemm - christian.klemm@fh-muenster.de, 22.01.2020

    """
    
    
    #PV
#    import pvlib
#    from pvlib.pvsystem import PVSystem
#    from pvlib.location import Location
#    from pvlib.modelchain import ModelChain
#    from pvlib.tools import cosd
#    import feedinlib.weather as weather
    
    import feedinlib
    import pandas as pd
    import os
    import feedinlib.powerplants

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
       logging.info('   '+'Commodity Source created: ' + so['label'])        

    
    def create_pv_source_object():
        
        # reades pv system parameters from parameter dictionary nodes_data
        parameter_set = {
                'azimuth' : so['Azimuth (PV ONLY)'],
                'tilt' : so['Surface Tilt (PV ONLY)'],
                'module_name' : so['Modul Model (PV ONLY)'],
                'inverter_name' : so['Inverter Model (PV ONLY)'],
                'albedo' : so['Albedo (PV ONLY)']}
        
        # sets pv system parameters for pv_module
        pv_module = feedinlib.powerplants.Photovoltaic(**parameter_set)
        
        # reades weather data from interim-.csv data set
        my_weather_pandas_DataFrame = pd.read_csv(os.path.join(os.path.dirname(__file__))+'/interim_data/weather_data.csv', index_col=0,
            date_parser=lambda idx: pd.to_datetime(idx, utc=True))
        
        # calculetes global horizontal irradiance from diffuse (dhi) and direct
        # irradiance and adds it to the wether data frame
        my_weather_pandas_DataFrame['ghi'] = my_weather_pandas_DataFrame.dirhi + my_weather_pandas_DataFrame.dhi
        
        # changes names of data columns, so it fits the needs of the feedinlib
        name_dc = {
            'temperature': 'temp_air',
            'windspeed': 'v_wind'}
        my_weather_pandas_DataFrame.rename(columns=name_dc)
        
        # time series normed on 1 kW pv peak performance
        feedin = pv_module.feedin(
            weather=my_weather_pandas_DataFrame,
            location=(so['Latitude (PV ONLY)'], 
                      so['Longitude (PV ONLY)']), 
            scaling='peak_power')
        
        # Set negative values to zero (requirement for solving the oemof model)
        for i in range(len(feedin)):
            if feedin[i]<0:
                feedin[i] = 0      
        
        nodes.append(
               solph.Source(label=so['label'],
                     outputs={busd[so['output']]: solph.Flow(
                        investment=solph.Investment(
                                ep_costs=so['periodical costs [CU/(kW a)]'],
                                minimum=so['min. investment capacity [kW]'],
                                maximum=so['max. investment capacity [kW]'],
                                existing=so['existing capacity [kW]']),
                        actual_value = feedin,
                        fixed=True,
                        variable_costs=so['variable costs [CU/kWh]'])}))            
                      
        
        logging.info('   '+'Source created: ' + so['label'])
        
    

    
    # The feedinlib can only read .csv data sets, so the weather data from
    # the .xlsx scenario file have to be converted into a .csv data set and
    # saved
    read_file = pd.read_excel(filepath, sheet_name='weather data')
    read_file.to_csv(
            os.path.join(os.path.dirname(__file__))+'/interim_data/weather_data.csv', 
            index = None, 
            header=True)

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
               logging.info('   '+'WARNING: windpower plants can currently not be modelled. This feature will be added later.')








              
def sinks(nodes_data, bus, nodes, filepath):
    
    """
    Creates sinks objects with the parameters given in 'nodes_data' and adds 
    them to the list of components 'nodes'.

    ----    
        
    Keyword arguments:
        
        nodes_data : obj:'dict'
           -- dictionary containing parameters of sinks to be created. The 
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
            -- list of components created before (can be empty)

    ----
    
    @ Christian Klemm - christian.klemm@fh-muenster.de, 21.01.2020

    """
    import demandlib.bdew as bdew    
    
    #Richardson
    import copy
    import richardsonpy.classes.occupancy as occ
    import richardsonpy.functions.change_resolution as cr
    import richardsonpy.functions.load_radiation as loadrad
    import richardsonpy.classes.electric_load as eload
    import numpy as np
    
    def create_unfixed_sink_objects():
        """
        Creates a sink object with an unfixed energy input.
        """            
        # set static inflow values    
        inflow_args = {'nominal_value': de['nominal value [kW]'],
                       'fixed': de['fixed']}   
   
        # create    
        nodes.append(    
            solph.Sink(label=de['label'],   
                       inputs={    
                           busd[de['input']]: solph.Flow(**inflow_args)}))
        logging.info('   '+'Sink created: ' + de['label'])        


    def create_timeseries_sink_objects():
        """
        Creates a sink object with a fixed input. The input must be given
        as a time series in 'nodes_data'.
        
        ----
    
        @ Christian Klemm - christian.klemm@fh-muenster.de, 15.01.2020

        """
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
        logging.info('   '+'Sink created: ' + de['label'])


    def create_residentialheatslp_sink_objects():
        """
        Creates a sink with inputs according to VDEW standard load profiles, 
        using oemofs demandlib and adds it to the list of components 'nodes'. 
        Used for the modelling of residential ectricity demands.
        
        ----
    
        @ Christian Klemm - christian.klemm@fh-muenster.de, 21.01.2020

        """
        # Import weather Data
        data = pd.read_csv(os.path.join(
                os.path.dirname(__file__))+'/interim_data/weather_data.csv')
        
        # Importing timesystem parameters from the scenario file
        for j, ts in nd['timesystem'].iterrows():
            temp_resolution = ts['temporal resolution']
            periods = ts['periods']
            start_date = str(ts['start date'])
        
        # Converting start date into datetime format
        start_date =datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')

        # Create DataFrame
        demand = pd.DataFrame(
                index=pd.date_range(pd.datetime(start_date.year, 
                                                start_date.month, 
                                                start_date.day, 
                                                start_date.hour),
                                    periods=periods, freq=temp_resolution))
            
        demand[de['load profile']] = bdew.HeatBuilding(
                demand.index, 
                temperature=data['temperature'],
                shlp_type=de['load profile'],
                building_class=de['building class [HEAT SLP ONLY]'],                   
                wind_class=de['wind class [HEAT SLP ONLY]'],                       
                annual_heat_demand=1,
                name=de['load profile']).get_bdew_profile()
            
        #create Sink 
        nodes.append(
                solph.Sink(label=de['label'],
                   inputs={
                       busd[de['input']]: solph.Flow(nominal_value = de['annual demand [kWh/a]'],
                                                           actual_value = demand[de['load profile']],
                                                           fixed = True)}))                
        logging.info('   '+'Sink created: ' + de['label'])

    def create_commercialheatslp_sink_objects():
        """
        Creates a sink with inputs according to VDEW standard load profiles, 
        using oemofs demandlib and adds it to the list of components 'nodes'.
        Used for the modelling of commercial electricity demands.
        
        ----
    
        @ Christian Klemm - christian.klemm@fh-muenster.de, 21.01.2020

        """
        # Import weather Data
        data = pd.read_csv(os.path.join(
                os.path.dirname(__file__))+'/interim_data/weather_data.csv')
        
        # Importing timesystem parameters from the scenario file
        for j, ts in nd['timesystem'].iterrows():
            temp_resolution = ts['temporal resolution']
            periods = ts['periods']
            start_date = str(ts['start date'])
        
        # Converting start date into datetime format
        start_date =datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')

        # Create DataFrame
        demand = pd.DataFrame(
                index=pd.date_range(pd.datetime(start_date.year, 
                                                start_date.month, 
                                                start_date.day, 
                                                start_date.hour),
                                    periods=periods, freq=temp_resolution)) 
            
        demand[de['load profile']] = bdew.HeatBuilding(
                demand.index, 
                temperature=data['temperature'],
                shlp_type=de['load profile'],
                wind_class=de['wind class [HEAT SLP ONLY]'],                      
                annual_heat_demand=1,
                name=de['load profile']).get_bdew_profile()
            
        #create Sink 
        nodes.append(
                solph.Sink(label=de['label'],
                   inputs={
                       busd[de['input']]: solph.Flow(nominal_value = de['annual demand [kWh/a]'],
                                                           actual_value = demand[de['load profile']],
                                                           fixed = True)}))                
        logging.info('   '+'Sink created: ' + de['label']) 

    def create_richardson_sink_objects():
        """
        Creates a sink with stochastical input, using richardson.py and adds it 
        to the list of components 'nodes'. Used for the modelling of 
        residential electricity demands.
        
        ----
    
        @ Christian Klemm - christian.klemm@fh-muenster.de, 21.01.2020

        """       
        # Import Weather Data
        dirhi_csv = pd.read_csv(
                os.path.join(os.path.dirname(__file__))+'/interim_data/weather_data.csv', 
                usecols=['dirhi'],
                dtype=float)
        dirhi=dirhi_csv.values.flatten() 
        dhi_csv = pd.read_csv(
        os.path.join(os.path.dirname(__file__))+'/interim_data/weather_data.csv', 
        usecols=['dhi'], 
        dtype=float) 
        dhi=dhi_csv.values.flatten()
        #Conversion of irradiation from W/m^2 to kW/m^2
        dhi = dhi/1000
        dirhi = dirhi/1000
        
        # Reades the temporal resolution from the sceanrio file
        for i, ts in nd['timesystem'].iterrows():
            temp_resolution = ts['temporal resolution']
        
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
            logging.info('   '+'Invalid Temporal Resolution!')
            
        #  Generate occupancy object (necessary as input for electric load gen.)
        occ_obj = occ.Occupancy(number_occupants=nb_occ)
        
        #  Get radiation (necessary for lighting usage calculation)
        (q_direct, q_diffuse) = loadrad.get_rad_from_try_path()
        
        q_direct=dirhi
        q_diffuse=dhi
        
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
        logging.info('   '+'Sink created: ' + de['label'])        


    def create_electricslp_sink_objects(): 
        # read timesystem data from scenario file
        for j, ts in nd['timesystem'].iterrows():
            temp_resolution = ts['temporal resolution']
            year = datetime.datetime.strptime(str(ts['start date']), '%Y-%m-%d %H:%M:%S').year
        
        # Import SLP's
        e_slp = bdew.ElecSlp(year)
        elec_demand = e_slp.get_profile({de['load profile']:1})
    
        elec_demand = elec_demand.resample(temp_resolution).mean()
        
        #create
        nodes.append(
                  solph.Sink(label=de['label'],
                             inputs={busd[de['input']]: solph.Flow(nominal_value = de['annual demand [kWh/a]'], # diesen Wert anpassen
                                                                 actual_value = elec_demand[de['load profile']],
                                                                 fixed = True)}))
        logging.info('   '+'Sink created: ' + de['label'])









    
    nd = nodes_data
    busd = bus
    
    # richardson.py and demandlib can only read .csv data sets, so the weather 
    # data from the .xlsx scenario file have to be converted into a .csv data 
    # set and saved
    read_file = pd.read_excel(filepath, sheet_name='weather data')
    read_file.to_csv(
            os.path.join(os.path.dirname(__file__))+'/interim_data/weather_data.csv', 
            index = None, 
            header=True)
    
    # Create sink objects
    for i, de in nd['demand'].iterrows():
        heat_slps = ['efh', 'mfh'] 
        heat_slps_commercial = ['gmf','gpd','ghd','gwa','ggb','gko','gbd',
                                'gba','gmk','gbh','gga','gha']
        electricity_slps = ['h0', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6',
                            'l0', 'l1', 'l2']
        richardson = ['richardson']
#        
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
    
    @ Christian Klemm - christian.klemm@fh-muenster.de, 27.01.2020

    """

    
    def create_generic_transformer_object():
                """
                Creates a generic transformer with the paramters given in 'nodes_data'
                and adds it to the list of components 'nodes'.
                        
                ----
            
                @ Christian Klemm - christian.klemm@fh-muenster.de, 15.01.2020
        
                """    
        # get time series for inflow of transformer    
#                for col in nd['timeseries'].columns.values:   
#                    if col.split('.')[0] == t['label']:    
#                        inflow_args[col.split('.')[1]] = nd['timeseries'][col]
   
                # create 
                one_output = ['None', 'none', 'x']
                
                if t['output2'] in one_output:
                    
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
                    logging.info('   '+'Transformer created: ' + t['label'])
                    
                else: 
                    existing_capacity2 = (t['existing capacity [kW]']/t['efficiency'])*t['efficiency']
                    minimum_capacity2 = (t['min. investment capacity [kW]']/t['efficiency'])*t['efficiency']
                    maximum_capacity2 = (t['max. investment capacity [kW]']/t['efficiency'])*t['efficiency']
                    
                    nodes.append(    
                        solph.Transformer(    
                            label=t['label'],    
                            inputs={busd[t['input']]: solph.Flow(variable_costs=[t['variable input costs [CU/kWh]']])},    
                            outputs={busd[t['output']]: solph.Flow(
                                        variable_costs=t['variable output costs [CU/kWh]'],
                                        investment=solph.Investment(ep_costs=t['periodical costs [CU/(kW a)]'],
                                                                    minimum=t['min. investment capacity [kW]'],
                                                                    maximum=t['max. investment capacity [kW]'],
                                                                    existing=t['existing capacity [kW]']
                                                                                             )),
                                     busd[t['output2']]: solph.Flow(existing=existing_capacity2,
                                                                     minimum=minimum_capacity2,
                                                                     maximum=maximum_capacity2)},   
                            conversion_factors={busd[t['output']]: t['efficiency'], busd[t['output2']]: t['efficiency']}))
                    logging.info('   '+'Transformer created: ' + t['label'])        










    def create_genericchp_transformer_object():
        """
        Creates a generic chp transformer with the paramters given in 'nodes_data'
        and adds it to the list of components 'nodes'.
                
        ----
    
        @ Christian Klemm - christian.klemm@fh-muenster.de, 15.01.2020

        """ 
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
        logging.info('   '+'Transformer created: ' + t['label'])


    
    busd=bus
    nd=nodes_data

    for i, t in nd['transformers'].iterrows():
        if t['active']:
            
            ### Create Generic Transformers ###               
            if t['transformer type'] == 'GenericTransformer':
                create_generic_transformer_object()
                
            ### Create Extraction Turbine CHPs ###           
            elif t['transformer type'] == 'ExtractionTurbineCHP':
                logging.info('   '+'WARNING: ExtractionTurbineCHP are currently not a part of this model generator, but will be added later.')
            
            ### Create Generic CHPs ###           
            elif t['transformer type'] == 'GenericCHP':         ###Investment hinzufügen!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                create_genericchp_transformer_object()          #### Variable kosten hinzufügen!!!
                
            ### Create Offset Transformers ###            
            elif t['transformer type'] == 'OffsetTransformer':
                logging.info('   '+'WARNING: OffsetTransformer are currently not a part of this model generator, but will be added later.')                
            
            ### Error Message for invalid Transformers ###          
            else:
                logging.info('   '+'WARNING: \'' 
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
            logging.info('   '+'Storage created: ' + s['label'])
            
            
            
            
            
            
            
            
            
            
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
        """
        Creates an undirected link between two buses and adds it to the list of 
        components 'nodes'.
                
        ----
    
        @ Christian Klemm - christian.klemm@fh-muenster.de, 15.01.2020

        """ 
        bus1 = busd[p['bus_1']]
        bus2 = busd[p['bus_2']]
        nodes.append(
            solph.custom.Link(
                label='undirected_link'
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
        logging.info('   '+'Link created: ' + p['label'])
        
    def create_directed_link():
        """
        Creates a directed link between two buses and adds it to the list of 
        components 'nodes'.
                
        ----
    
        @ Christian Klemm - christian.klemm@fh-muenster.de, 24.01.2020

        """ 
        bus1 = busd[p['bus_1']]
        bus2 = busd[p['bus_2']]
        nodes.append(
            solph.custom.Link(
                label='directed_link'
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
        logging.info('   '+'Link created: ' + p['label'])


    for i, p in nd['links'].iterrows():
        if p['active']:
            
            if p['(un)directed'] == 'undirected':
                create_undirected_link()
                
            elif p['(un)directed'] == 'directed':
                create_directed_link()
                
