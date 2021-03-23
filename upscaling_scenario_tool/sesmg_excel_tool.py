import xlsxwriter
import pandas as pd
import os

def copy_standard_parameter_sheet(standard_parameters, sheet):

    sheets[sheet] = standard_parameters.parse(sheet)

def create_standard_parameter_bus(label, bustype, standard_parameters):
    """ Creates a bus with standard_parameters, based on the standard
    parameters given in the "standard_parameters" dataset and adds it to the
    "sheets"-output dataset.

    :param label: label, the created bus will be given
    :param bustype: defines, which set of standard param. will be given to
                    the dict
    :return:
    """

    # Definies Individual Values
    bus_dict = {'label': label}
    # Extracts the bus specific standard values from the given dataset
    bus_standard_parameters = \
        standard_parameters.parse('Buses', index_col='bus_type').loc[bustype]
    bus_standard_keys = bus_standard_parameters.keys().tolist()
    # Addapts standard Values
    for i in range(len(bus_standard_keys)):
        bus_dict[bus_standard_keys[i]] = bus_standard_parameters[bus_standard_keys[i]]
    # Creates Bus-List-Element
    sheets["buses"] = sheets["buses"].append(pd.Series(bus_dict), ignore_index=True)

def create_standard_parameter_link(label, bus_1, bus_2, link_type, standard_parameters):
    """Creates a link with standard_parameters, based on the standard
    parameters given in the "standard_parameters" dataset and adds it to the
    "sheets"-output dataset.

    :param label:
    :param bus_1:
    :param bus_2:
    :param standard_parameters:
    :return:
    """
    link_standard_parameters = standard_parameters.parse('Links')
    link_standard_keys = link_standard_parameters.keys().tolist()
    link_housespecific_dict = {'label': label,
                               'bus_1': bus_1,
                               'bus_2': bus_2}

    # read the heat network standards from standard_parameters.xlsx and append
    # them to the link_housespecific_dict
    # link_standard_keys = link_standard_parameters.keys().tolist()
    link_standard_parameters = standard_parameters.parse('Links', index_col='link_type').loc[link_type]
    link_standard_keys = link_standard_parameters.keys().tolist()
    for i in range(len(link_standard_keys)):
        link_housespecific_dict[link_standard_keys[i]] = \
            link_standard_parameters[link_standard_keys[i]]




    # produce a pandas series out of the dict above due to easier appending
    link_series = pd.Series(link_housespecific_dict)
    sheets["links"] = sheets["links"].append(link_series,
                                             ignore_index=True)

def create_standard_parameter_sink(sink_type, label, input, annual_demand, standard_parameters):
    sink_standard_parameters = standard_parameters.parse('Sinks', index_col="sink_type").loc[sink_type]
    sink_standard_keys = sink_standard_parameters.keys().tolist()
    sink_dict = {'label': label,
                 'input': input,
                 'annual demand /(kWh/a)': annual_demand}

    # read the heat network standards from standard_parameters.xlsx and append
    # them to the sink_housespecific_dict
    sink_standard_keys = sink_standard_parameters.keys().tolist()
    for i in range(len(sink_standard_keys)):
        sink_dict[sink_standard_keys[i]] = \
            sink_standard_parameters[sink_standard_keys[i]]#[0]

    # produce a pandas series out of the dict above due to easier appending
    sink_series = pd.Series(sink_dict)
    sheets["sinks"] = sheets["sinks"].append(sink_series,
                                             ignore_index=True)

def central_comp(central, standard_parameters):
    """

    :param central: excel sheet from pre_scenario
    :return:
    """
    for i, j in central.iterrows():
        if j['district_electricity_bus']:
            create_standard_parameter_bus(label='district_electricity_bus',
                                          bustype="district_electricity_bus",
                                          standard_parameters=standard_parameters)


        # CREATE REQUIRED CENTRAL COMPONENTS FOR A DISTRICT HEATING NETWORK
        if j['district heat']:
            # INPUT BUS
            create_standard_parameter_bus(label='district_heat_input_bus',
                                          bustype="district_heat_input_bus",
                                          standard_parameters=standard_parameters)

            # OUTPUT BUS
            create_standard_parameter_bus(label='district_heat_output_bus',
                                          bustype="district_heat_output_bus",
                                          standard_parameters=standard_parameters)

            # LINK CONSIDERING LOSSES
            create_standard_parameter_link(label="district_heat_link",
                                           bus_1="district_heat_input_bus",
                                           bus_2="district_heat_output_bus",
                                           link_type="district_heat_link",
                                           standard_parameters=standard_parameters)


        # CENTRAL NATURAL GAS CHP
        if j['CHP'] == 'yes':
            create_central_chp(gastype='naturalgas', standard_parameters=standard_param)

        # CENTRAL BIO GAS CHP
        if j['CHP'] == 'yes':
            create_central_chp(gastype='biogas', standard_parameters=standard_param)

        # CENTRAL SWHP
        if j['SWHP'] == 'yes':
            create_central_swhp(standard_parameters=standard_param)

def create_central_swhp(standard_parameters):

    #### SWHP ELEC BUS
    create_standard_parameter_bus(label="central_swhp_elec_bus",
                                  bustype="central_swhp_electricity_bus",
                                  standard_parameters=standard_parameters)

    ### SWHP TRANSFORMER

    swhp_standard_parameters = standard_parameters.parse('SWHP')

    swhp_central_dict = {'label': 'central_swhp_transformer',
                               'comment': 'automatically_created',
                               'input': "central_swhp_elec_bus",
                               'output': 'district_heat_input_bus',
                               'output2': 'None',
                             }

    # read the swhp standards from standard_parameters.xlsx and append
    # them to the swhp_central_dict
    swhp_standard_keys = swhp_standard_parameters.keys().tolist()
    for i in range(len(swhp_standard_keys)):
        swhp_central_dict[swhp_standard_keys[i]] = \
            swhp_standard_parameters[swhp_standard_keys[i]][0]

    # produce a pandas series out of the dict above due to easier appending
    swhp_series = pd.Series(swhp_central_dict)
    sheets["HeatPump&Chiller"] = sheets["HeatPump&Chiller"].append(swhp_series, ignore_index=True)

def create_central_chp(gastype, standard_parameters):

    #### CHP GAS BUS
    create_standard_parameter_bus(label="chp_"+gastype+"_bus",
                                  bustype="central_chp_"+gastype+"_bus",
                                  standard_parameters=standard_parameters)

    #### CENTRAL ELECTRICITY BUS
    create_standard_parameter_bus(label="chp_"+gastype+"_elec_bus",
                                  bustype="central_chp_"+gastype+"_electricity_bus",
                                  standard_parameters=standard_parameters)

    #### Connection to district electricity bus
    create_standard_parameter_link(label="central_chp_"+gastype+"_elec_district_link",
                                   bus_1="chp_"+gastype+"_elec_bus",
                                   bus_2="district_electricity_bus",
                                   link_type="central_chp_elec_district_link",
                                   standard_parameters=standard_parameters)


    ### CHP TRANSFORMER

    chp_standard_parameters = standard_parameters.parse('CHP')

    chp_central_dict = {'label': gastype+'_chp_transformer',
                          'input': "chp_" + gastype + "_bus",
                          'output': "chp_"+gastype+"_elec_bus",
                          'output2': "district_heat_input_bus"
                                      }

    # read the gchp standards from standard_parameters.xlsx and append
    # them to the gchp_central_dict
    chp_standard_keys = chp_standard_parameters.keys().tolist()
    for i in range(len(chp_standard_keys)):
        chp_central_dict[chp_standard_keys[i]] = \
            chp_standard_parameters[chp_standard_keys[i]][0]

    # produce a pandas series out of the dict above due to easier appending
    chp_series = pd.Series(chp_central_dict)
    sheets["GenericTransformer"] = sheets["GenericTransformer"].append(
        chp_series, ignore_index=True)

def create_busses(ID: str, gas_bus: bool, pv_bus: bool, hp_elec_bus, district_heat_bus, standard_parameters):

    ### HOUSE ELECTRICITY BUS
    create_standard_parameter_bus(label=str(ID) + "_electricity_bus",
                                  bustype='building_electricity_bus',
                                  standard_parameters=standard_parameters)

    ### HOUSE HEAT BUS
    create_standard_parameter_bus(label=str(ID) + "_heat_bus",
                                  bustype='building_heat_bus',
                                  standard_parameters=standard_parameters)

    if hp_elec_bus:
        #### BUILDING HP ELECTRICITY BUS
        create_standard_parameter_bus(label=str(ID) + "_hp_elec_bus",
                                      bustype='building_hp_electricity_bus',
                                      standard_parameters=standard_parameters)

        ### ELECTRICITY LINK FROM BUILDING ELECTRICITY BUS TO HP ELEC BUS
        create_standard_parameter_link(label=str(ID) + "_gchp_building_link",
                                       bus_1=str(ID) + "_electricity_bus",
                                       bus_2=str(ID) + "_hp_elec_bus",
                                       link_type="building_hp_elec_link",
                                       standard_parameters=standard_parameters)

    if district_heat_bus:
        ### Heat LINK FROM District Heat Network to Building heat Bus
        create_standard_parameter_link(label= str(ID) + "_district_heat_link",
                                       bus_1="district_heat_output_bus",
                                       bus_2=str(ID) + "_heat_bus",
                                       link_type="building_district_heat_link",
                                       standard_parameters=standard_parameters)

    # TODO excess constraint costs
    if pv_bus:

        #### BUILDING PV BUS
        create_standard_parameter_bus(label=str(ID) + "_pv_bus",
                                      bustype='building_pv_bus',
                                      standard_parameters=standard_parameters)

        # LINK FROM PV BUS TO BUILDING ELECTRICITY BUS
        create_standard_parameter_link(label=str(ID) + "pv_" + str(ID) + "_electricity_link",
                                       bus_1=str(ID) + "_pv_bus",
                                       bus_2=str(ID) + "_electricity_bus",
                                       link_type="building_pv_district_link",
                                       standard_parameters=standard_parameters)

        # LINK FROM PV BUS TO DISTRICT ELECTRICITY BUS
        create_standard_parameter_link(label=str(ID) + "pv_district_electricity_link",
                                       bus_1=str(ID) + "_pv_bus",
                                       bus_2="district_electricity_bus",
                                       link_type="building_pv_district_link",
                                       standard_parameters=standard_parameters)

        # LINK FROM DISTRICT ELEC BUS TO BUILDING ELECTRICITY BUS
        create_standard_parameter_link(label=str(ID) + "district_electricity_link",
                                       bus_1="district_electricity_bus",
                                       bus_2=str(ID) + "_electricity_bus",
                                       link_type="building_district_building_link",
                                       standard_parameters=standard_parameters)

def create_sinks(ID: str, building_type: str, units: int, occupants: int, yoc: str, area: int, standard_parameters):

    # ELECTRICITY DEMAND
    if building_type != 'None':
        # residential parameters
        if "RES" in building_type:
            electricity_demand_residential = {}
            electricity_demand_standard_param = standard_parameters.parse('ResElecDemand')
            for i in range(len(electricity_demand_standard_param)):
                electricity_demand_residential[electricity_demand_standard_param['household size'][i]] =\
                    [electricity_demand_standard_param[building_type + ' (kWh/a)'][i]]

            if occupants <= 5:
                demand_el = electricity_demand_residential[occupants][0]
                demand_el = demand_el*units
            elif occupants > 5:
                demand_el = (electricity_demand_residential[5][0])/5*occupants
                demand_el = demand_el * units

        # commercial parameters
        elif "COM" in building_type:
            electricity_demand_standard_param = standard_parameters.parse('ComElecDemand')
            electricity_demand_standard_param.set_index("commercial type",inplace=True)
            demand_el = electricity_demand_standard_param.loc[building_type]['specific demand (kWh/m2/a)']
            net_floor_area = area * 0.9  # TODO: give this value with standard parameter dataset
            demand_el = demand_el * net_floor_area

        create_standard_parameter_sink(sink_type=building_type + "_electricity_sink",
                                       label=str(ID) + "_electricity_demand",
                                       input=str(ID) + "_electricity_bus",
                                       annual_demand=demand_el,
                                       standard_parameters=standard_parameters)

    # HEAT DEMAND

    # residential building
    if building_type != "None":
        if "RES" in building_type:
            # read standard values from standard_parameter-dataset
            heat_demand_standard_param = standard_parameters.parse('ResHeatDemand')
            heat_demand_standard_param.set_index("Year of Construction", inplace=True)
            specific_heat_demand = heat_demand_standard_param.loc[yoc][str(int(units)) + ' unit(s)']

            net_floor_area = area * 0.9 # TODO: give this value with standard parameter dataset

            if units <= 12:
                demand_heat = specific_heat_demand * net_floor_area
            if units > 12:
                demand_heat = specific_heat_demand * net_floor_area

        # commercial building
        elif "COM" in building_type:
            heat_demand_standard_param = standard_parameters.parse('ComHeatDemand')
            heat_demand_standard_param.set_index("Year of Construction",inplace=True)
            demand_heat = heat_demand_standard_param.loc[yoc][building_type]
            net_floor_area = area * 0.9  # TODO: give this value with standard parameter dataset
            demand_heat = demand_heat * net_floor_area

        create_standard_parameter_sink(sink_type=building_type + "_heat_sink",
                                       label=str(ID) + "_heat_demand",
                                       input=str(ID) + "_heat_bus",
                                       annual_demand=demand_heat,
                                       standard_parameters=standard_parameters)

def create_pv_source(building_ID, plant_ID, azimuth, tilt, area, pv_standard_parameters, latitude, longitude):
    """

    :param longitude:
    :param latitude:
    :param ID:
    :param azimuth:
    :param tilt:
    :param area:
    :param pv_standard_parameters: excel sheet
    :return:
    """
    ###### Technical Parameters

    pv_housespecific_dict = {'label': str(building_ID) + '_' + str(plant_ID) + '_pv_source',
                             'existing capacity /(kW)': 0,
                             'min. investment capacity /(kW)': 0,
                             'output': str(building_ID) + '_pv_bus',
                             'Azimuth': azimuth,
                             'Surface Tilt': tilt,
                             'Latitude':latitude,
                             'Longitude':longitude}


    # read the pv standards from standard_parameters.xlsx and append
    # them to the pv_housespecific_dict
    pv_standard_keys = pv_standard_parameters.keys().tolist()
    for i in range(len(pv_standard_keys)):
        pv_housespecific_dict[pv_standard_keys[i]] = \
            pv_standard_parameters[pv_standard_keys[i]][0]

    pv_housespecific_dict['max. investment capacity /(kW)'] = pv_standard_parameters['Capacity per Area (kW/m2)'][0]*area

    # produce a pandas series out of the dict above due to easier appending
    pv_series = pd.Series(pv_housespecific_dict)
    sheets["PV"] = sheets["PV"].append(pv_series, ignore_index=True)

def create_gchp(ID, area, standard_parameters):

    ### GCHP TRANSFORMER

    gchp_standard_parameters = standard_parameters.parse('GCHP')

    gchp_housespecific_dict = {'label': str(ID) + '_gchp_transformer',
                               'comment': 'automatically_created',
                               'input': str(ID) + '_hp_elec_bus',
                               'output': str(ID) + '_heat_bus',
                               'output2': 'None',
                               'area /(sq m)': area,
                               'existing capacity /(kW)': 0,
                               'min. investment capacity /(kW)': 0,
                             }

    # read the gchp standards from standard_parameters.xlsx and append
    # them to the gchp_housespecific_dict
    gchp_standard_keys = gchp_standard_parameters.keys().tolist()
    for i in range(len(gchp_standard_keys)):
        gchp_housespecific_dict[gchp_standard_keys[i]] = \
            gchp_standard_parameters[gchp_standard_keys[i]][0]

    # produce a pandas series out of the dict above due to easier appending
    gchp_series = pd.Series(gchp_housespecific_dict)
    sheets["HeatPump&Chiller"] = sheets["HeatPump&Chiller"].append(gchp_series, ignore_index=True)

def create_ashp(ID, standard_parameters):

    ### ashp TRANSFORMER

    ashp_standard_parameters = standard_parameters.parse('ASHP')

    ashp_housespecific_dict = {'label': str(ID) + '_ashp_transformer',
                               'comment': 'automatically_created',
                               'input': str(ID) + '_hp_elec_bus',
                               'output': str(ID) + '_heat_bus',
                               'output2': 'None',
                               'existing capacity /(kW)': 0,
                               'min. investment capacity /(kW)': 0,
                             }

    # read the ashp standards from standard_parameters.xlsx and append
    # them to the ashp_housespecific_dict
    ashp_standard_keys = ashp_standard_parameters.keys().tolist()
    for i in range(len(ashp_standard_keys)):
        ashp_housespecific_dict[ashp_standard_keys[i]] = \
            ashp_standard_parameters[ashp_standard_keys[i]][0]

    # produce a pandas series out of the dict above due to easier appending
    ashp_series = pd.Series(ashp_housespecific_dict)
    sheets["HeatPump&Chiller"] = sheets["HeatPump&Chiller"].append(ashp_series, ignore_index=True)

def create_gas_heating(ID, standard_parameters):

    #### BUILDING GAS BUS
    create_standard_parameter_bus(label=str(ID) + "_gas_bus",
                                  bustype='building_gas_bus',
                                  standard_parameters=standard_parameters)

    ### GAS HEATING TRANSFORMER

    gas_heating_standard_parameters = standard_parameters.parse('Gasheating')

    # Define individual gas_heating_parameters
    gas_heating_housespecific_dict = {'label': str(ID) + '_gasheating_transformer',
                               'comment': 'automatically_created',
                               'input': str(ID) + '_gas_bus',
                               'output': str(ID) + '_heat_bus',
                               'output2': 'None',
                             }

    # read the gasheating standards from standard_parameters.xlsx and append
    # them to the  gas_heating_housespecific_dict
    gas_heating_standard_keys = gas_heating_standard_parameters.keys().tolist()
    for i in range(len(gas_heating_standard_keys)):
        gas_heating_housespecific_dict[gas_heating_standard_keys[i]] = \
            gas_heating_standard_parameters[gas_heating_standard_keys[i]][0]

    # produce a pandas series out of the dict above due to easier appending
    gas_heating_series = pd.Series(gas_heating_housespecific_dict)
    sheets["GenericTransformer"] = sheets["GenericTransformer"].append(gas_heating_series, ignore_index=True)

def create_battery(ID, battery_standard_parameters):

    battery_housespecific_dict = {'label': str(ID) + '_battery_storage',
                                  'comment': 'automatically_created',
                                  'bus': str(ID) + '_electricity_bus',
                                  }

    # read the gchp standards from standard_parameters.xlsx and append
    # them to the gchp_housespecific_dict
    battery_standard_keys = battery_standard_parameters.keys().tolist()
    for i in range(len(battery_standard_keys)):
        battery_housespecific_dict[battery_standard_keys[i]] = \
            battery_standard_parameters[battery_standard_keys[i]][0]

    # produce a pandas series out of the dict above due to easier appending
    battery_series = pd.Series(battery_housespecific_dict)
    sheets["GenericStorage"] = sheets["GenericStorage"].append(battery_series, ignore_index=True)


if __name__ == '__main__':

    plain_scenario_path = 'plain_scenario.xlsx'
    xls = pd.ExcelFile("plain_scenario.xlsx")
    standard_param = pd.ExcelFile("standard_parameters.xlsx")

    energysystem_columns = xls.parse("energysystem").keys()
    buses_columns = xls.parse("buses").keys()
    sinks_columns = xls.parse("sinks").keys()
    pv_columns = xls.parse("PV").keys()
    concentradedsolar_columns = xls.parse("ConcentratedSolar").keys()
    flatplate_columns = xls.parse("FlatPlate").keys()
    timeseries_columns = xls.parse("Timeseries").keys()
    wind_columns = xls.parse("Wind").keys()
    commodity_columns = xls.parse("Commodity").keys()
    generictransformer_columns = xls.parse("GenericTransformer").keys()
    genericchp_columns = xls.parse("GenericCHP").keys()
    heatpumps_columns = xls.parse("HeatPump&Chiller").keys()
    absorptionchiller_columns = xls.parse("AbsorptionChiller").keys()
    genericstorage_columns = xls.parse("GenericStorage").keys()
    stratifiedstorage_columns = xls.parse("StratifiedStorage").keys()
    links_columns = xls.parse("links").keys()
    weatherdata_columns = xls.parse("weather data").keys()

    columns = {"energysystem": energysystem_columns,
               "buses": buses_columns,
               "sinks": sinks_columns,
               "PV": pv_columns,
               "ConcentratedSolar": concentradedsolar_columns,
               "FlatPlate": flatplate_columns,
               "Timeseries": timeseries_columns,
               "Wind": wind_columns,
               "Commodity": commodity_columns,
               "GenericTransformer": generictransformer_columns,
               "GenericCHP": genericchp_columns,
               "HeatPump&Chiller": heatpumps_columns,
               "AbsorptionChiller": absorptionchiller_columns,
               "GenericStorage": genericstorage_columns,
               "StratifiedStorage": stratifiedstorage_columns,
               "links": links_columns,
               "weather data":weatherdata_columns,
               "time_series": [0,1] # TODO: placeholder, to be deleted
               }

    worksheets = [i for i in columns.keys()]

    sheets = {}
    for sheet in worksheets:
        sheets.update({sheet: pd.DataFrame(columns=(columns[sheet]))})
    # import the sheet which is filled by the user
    xls = pd.ExcelFile(os.path.dirname(__file__) + "/pre_scenario.xlsx")
    tool = xls.parse("tool")
    central = xls.parse("central")
    central_comp(central, standard_parameters=standard_param)
    for i, j in tool.iterrows():
        # foreach building the three necessary buses will be created
        create_busses(j['label'],
                      True if j['gas heating'] == 'yes' else False,
                      True if j['azimuth 1 (°)'] or j['azimuth 2 (°)'] else False,
                      True if j['gchp area (m2)'] or j['ashp'] else False,
                      True if j['district heat'] else False,
                      standard_param)
        create_sinks(ID=j['label'],
                     building_type=j['building type'],
                     units=j['units'],
                     occupants=j['occupants per unit'],
                     yoc=j['year of construction'],
                     area=j['living space'] * j['floors'],
                     standard_parameters=standard_param)

        # Create PV-Sources
        if j['azimuth 1 (°)']:
            create_pv_source(building_ID=j['label'],
                             plant_ID='1',
                             azimuth=j['azimuth 1 (°)'],
                             tilt=j['surface tilt 1 (°)'],
                             area=j['roof area 1 (m²)'],
                             latitude=j['latitude'],
                             longitude=j['longitude'],
                             pv_standard_parameters=standard_param.parse('PV'))

        if j['azimuth 2 (°)']:
            create_pv_source(building_ID=j['label'],
                             plant_ID='2',
                             azimuth=j['azimuth 2 (°)'],
                             tilt=j['surface tilt 2 (°)'],
                             area=j['roof area 2 (m²)'],
                             latitude=j['latitude'],
                             longitude=j['longitude'],
                             pv_standard_parameters=standard_param.parse('PV'))

        if j['azimuth 3 (°)']:
            create_pv_source(building_ID=j['label'],
                             plant_ID='3',
                             azimuth=j['azimuth 3 (°)'],
                             tilt=j['surface tilt 3 (°)'],
                             area=j['roof area 3 (m²)'],
                             latitude=j['latitude'],
                             longitude=j['longitude'],
                             pv_standard_parameters=standard_param.parse('PV'))

        if j['azimuth 4 (°)']:
            create_pv_source(building_ID=j['label'],
                             plant_ID='4',
                             azimuth=j['azimuth 4 (°)'],
                             tilt=j['surface tilt 4 (°)'],
                             area=j['roof area 4 (m²)'],
                             latitude=j['latitude'],
                             longitude=j['longitude'],
                             pv_standard_parameters=standard_param.parse('PV'))

        if j['azimuth 5 (°)']:
            create_pv_source(building_ID=j['label'],
                             plant_ID='5',
                             azimuth=j['azimuth 5 (°)'],
                             tilt=j['surface tilt 5 (°)'],
                             area=j['roof area 5 (m²)'],
                             latitude=j['latitude'],
                             longitude=j['longitude'],
                             pv_standard_parameters=standard_param.parse('PV'))

        # Creates Heat-Pumps
        if j['gchp area (m2)']:
            create_gchp(ID=j['label'],
                        area=j['gchp area (m2)'],
                        standard_parameters=standard_param)

        # Creates Heat-Pumps
        if j['ashp'] == 'yes':
            create_ashp(ID=j['label'],
                        standard_parameters=standard_param)

        # Creates Gasheating-system
        if j['gas heating'] == 'yes':
            create_gas_heating(ID=j['label'],
                               standard_parameters=standard_param)

        # Battery Storage
        if j['battery storage'] == 'yes':
            create_battery(ID=j['label'],
                           battery_standard_parameters=standard_param.parse('Battery'))


        print(str(j['label']) + ' subsystem added to scenario sheet')



    # Add General Energy System Information to "energysystem"-sheet
    copy_standard_parameter_sheet(standard_parameters=standard_param,
                                  sheet='energysystem')

    # Adds weather data to "weather data"-sheet
    copy_standard_parameter_sheet(standard_parameters=standard_param,
                                  sheet='weather data')

    # Adds weather data to "weather data"-sheet
    copy_standard_parameter_sheet(standard_parameters=standard_param,
                                  sheet='time_series')



    # Open the new Excel file and add all the created components
    j = 0
    writer = pd.ExcelWriter(os.path.dirname(__file__) + "/test_scenario.xlsx",
                            engine='xlsxwriter')
    for i in sheets:
        sheets[i].to_excel(writer, worksheets[j], index=False)
        j = j + 1
    writer.save()


