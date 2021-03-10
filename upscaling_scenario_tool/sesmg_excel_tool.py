import xlsxwriter
import pandas as pd
import os

def central_comp(central, standard_parameters):
    """

    :param central: excel sheet from pre_scenario
    :return:
    """
    for i, j in central.iterrows():
        if j['district_electricity_bus']:
            sheets['buses'] = sheets['buses'].append(
                pd.DataFrame([["district_electricity_bus", "upscaling",
                               1, 0, 0, 0, 0, 0, 0]],
                             columns=columns["buses"]))

        # CREATE REQUIRED CENTRAL COMPONENTS FOR A DISTRICT HEATING NETWORK
        if j['district heat']:

            # INPUT BUS
            sheets['buses'] = sheets['buses'].append(
                pd.DataFrame([["district_heat_input_bus", "automatically created",
                               1, 1, 0, 0, 0, 0, 0]],
                             columns=columns["buses"]))

            # OUTPUT BUS
            sheets['buses'] = sheets['buses'].append(
                pd.DataFrame([["district_heat_output_bus", "automatically created",
                               1, 1, 0, 0, 0, 0, 0]],
                             columns=columns["buses"]))

            # LINK CONSIDERING LOSSES
            heat_network_standard_parameters = standard_parameters.parse('HeatNetwork')
            heat_network_standard_keys = heat_network_standard_parameters.keys().tolist()
            heat_network_housespecific_dict = {'label': "district_heat_link",
                                              'Comment': "automatically created",
                                              'active': 1,
                                              'bus_1': "district_heat_input_bus",
                                              'bus_2': "district_heat_output_bus",
                                              '(un)directed': "directed"}

            # read the heat network standards from standard_parameters.xlsx and append
            # them to the heat_network_housespecific_dict
            heat_network_standard_keys = heat_network_standard_parameters.keys().tolist()
            for i in range(len(heat_network_standard_keys)):
                heat_network_housespecific_dict[heat_network_standard_keys[i]] = \
                    heat_network_standard_parameters[heat_network_standard_keys[i]][0]

            # produce a pandas series out of the dict above due to easier appending
            heat_network_series = pd.Series(heat_network_housespecific_dict)
            sheets["links"] = sheets["links"].append(heat_network_series, ignore_index=True)

            # # link between pv-bus and decentral electricity bus
            # sheets["links"] = sheets["links"].append(
            #     pd.Series(decentral_link_dict), ignore_index=True)

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

    # Definies Individual Values
    swhp_elec_bus_central_dict = {'label': "central_swhp_elec_bus"}
    # Extracts the bus specific standard values from the given dataset
    swhp_elec_bus_standard_parameters = \
    standard_parameters.parse('Buses', index_col='bus_type').loc[
        'central_swhp_electricity_bus']
    swhp_elec_bus_standard_keys = swhp_elec_bus_standard_parameters.keys().tolist()
    # Addapts standard Values
    for i in range(len(swhp_elec_bus_standard_keys)):
        swhp_elec_bus_central_dict[swhp_elec_bus_standard_keys[i]] = \
            swhp_elec_bus_standard_parameters[swhp_elec_bus_standard_keys[i]]
    # Creates Bus-List-Element
    sheets["buses"] = sheets["buses"].append(
        pd.Series(swhp_elec_bus_central_dict),
        ignore_index=True)


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

    # Definies Individual Values
    gas_bus_central_dict = {'label': "chp_"+gastype+"_bus",}
    # Extracts the bus specific standard values from the given dataset
    gas_bus_standard_parameters = \
    standard_parameters.parse('Buses', index_col='bus_type').loc[
        "central_chp_"+gastype+"_bus"]
    gas_bus_standard_keys = gas_bus_standard_parameters.keys().tolist()
    # Addapts standard Values
    for i in range(len(gas_bus_standard_keys)):
        gas_bus_central_dict[gas_bus_standard_keys[i]] = \
            gas_bus_standard_parameters[gas_bus_standard_keys[i]]
    # Creates Bus-List-Element
    sheets["buses"] = sheets["buses"].append(
        pd.Series(gas_bus_central_dict),
        ignore_index=True)

    #### CENTRAL ELECTRICITY BUS

    # Definies Individual Values
    electricity_bus_central_dict = {'label': "chp_"+gastype+"_elec_bus",}
    # Extracts the bus specific standard values from the given dataset
    electricity_bus_standard_parameters = \
    standard_parameters.parse('Buses', index_col='bus_type').loc[
        "central_chp_"+gastype+"_electricity_bus"]
    electricity_bus_standard_keys = electricity_bus_standard_parameters.keys().tolist()
    # Addapts standard Values
    for i in range(len(electricity_bus_standard_keys)):
        electricity_bus_central_dict[electricity_bus_standard_keys[i]] = \
            electricity_bus_standard_parameters[electricity_bus_standard_keys[i]]
    # Creates Bus-List-Element
    sheets["buses"] = sheets["buses"].append(
        pd.Series(electricity_bus_central_dict),
        ignore_index=True)

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

    # Definies Individual Values
    elec_bus_housespecific_dict = {'label': ID + "_electricity_bus"}
    # Extracts the bus specific standard values from the given dataset
    elec_bus_standard_parameters = standard_parameters.parse('Buses', index_col='bus_type').loc['building_electricity_bus']
    elec_bus_standard_keys = elec_bus_standard_parameters.keys().tolist()
    # Addapts standard Values
    for i in range(len(elec_bus_standard_keys)):
        elec_bus_housespecific_dict[elec_bus_standard_keys[i]] = \
            elec_bus_standard_parameters[elec_bus_standard_keys[i]]
    # Creates Bus-List-Element
    sheets["buses"] = sheets["buses"].append(pd.Series(elec_bus_housespecific_dict),
                                             ignore_index=True)


    ### HOUSE HEAT BUS

    # Definies Individual Values
    heat_bus_housespecific_dict = {'label': ID + "_heat_bus"}
    # Extracts the bus specific standard values from the given dataset
    heat_bus_standard_parameters = standard_parameters.parse('Buses', index_col='bus_type').loc['building_heat_bus']
    heat_bus_standard_keys = heat_bus_standard_parameters.keys().tolist()
    # Addapts standard Values
    for i in range(len(heat_bus_standard_keys)):
        heat_bus_housespecific_dict[heat_bus_standard_keys[i]] = \
            heat_bus_standard_parameters[heat_bus_standard_keys[i]]
    # Creates Bus-List-Element
    sheets["buses"] = sheets["buses"].append(pd.Series(heat_bus_housespecific_dict),
                                             ignore_index=True)

    # TODO check costs

    if hp_elec_bus:
        #### BUILDING HP ELECTRICITY BUS

        # Definies Individual Values
        hp_elec_bus_housespecific_dict = {'label': ID + "_hp_elec_bus"}
        # Extracts the bus specific standard values from the given dataset
        hp_elec_bus_standard_parameters = \
        standard_parameters.parse('Buses', index_col='bus_type').loc[
            'building_hp_electricity_bus']
        hp_elec_bus_standard_keys = hp_elec_bus_standard_parameters.keys().tolist()
        # Addapts standard Values
        for i in range(len(hp_elec_bus_standard_keys)):
            hp_elec_bus_housespecific_dict[hp_elec_bus_standard_keys[i]] = \
                hp_elec_bus_standard_parameters[hp_elec_bus_standard_keys[i]]
        # Creates Bus-List-Element
        sheets["buses"] = sheets["buses"].append(
            pd.Series(hp_elec_bus_housespecific_dict),
            ignore_index=True)

        ### ELECTRICITY LINK FROM BUILDING ELECTRICITY BUS TO HP ELEC BUS

        hp_elec_link_housespecific_dict = {'label': ID + "_gchp_building_link",
                                   'bus_1': ID + "_electricity_bus",
                                   'bus_2': ID + "_hp_elec_bus"}
        # Extracts the link specific standard values from the given dataset
        hp_elec_link_standard_parameters = \
        standard_parameters.parse('Links', index_col='link_type').loc[
            'building_hp_elec_link']
        hp_elec_link_standard_keys = hp_elec_link_standard_parameters.keys().tolist()
        # Addapts standard Values
        for i in range(len(hp_elec_link_standard_keys)):
            hp_elec_link_housespecific_dict[hp_elec_link_standard_keys[i]] = \
                hp_elec_link_standard_parameters[hp_elec_link_standard_keys[i]]
        # Creates link-List-Element
        sheets["links"] = sheets["links"].append(
            pd.Series(hp_elec_link_housespecific_dict),
            ignore_index=True)

    if district_heat_bus:
        ### Heat LINK FROM District Heat Network to Building heat Bus

        district_heat_link_housespecific_dict = {'label': ID + "_district_heat_link",
                                   'bus_1': "district_heat_output_bus",
                                   'bus_2': ID + "_heat_bus"}
        # Extracts the link specific standard values from the given dataset
        district_heat_link_standard_parameters = \
        standard_parameters.parse('Links', index_col='link_type').loc[
            'building_district_heat_link']
        district_heat_link_standard_keys = district_heat_link_standard_parameters.keys().tolist()
        # Addapts standard Values
        for i in range(len(district_heat_link_standard_keys)):
            district_heat_link_housespecific_dict[district_heat_link_standard_keys[i]] = \
                district_heat_link_standard_parameters[district_heat_link_standard_keys[i]]
        # Creates link-List-Element
        sheets["links"] = sheets["links"].append(
            pd.Series(district_heat_link_housespecific_dict),
            ignore_index=True)

    # TODO excess constraint costs
    if pv_bus:

        #### BUILDING pv BUS

        # Definies Individual Values
        pv_bus_housespecific_dict = {'label': ID + "_pv_bus"}
        # Extracts the bus specific standard values from the given dataset
        pv_bus_standard_parameters = \
        standard_parameters.parse('Buses', index_col='bus_type').loc[
            'building_pv_bus']
        pv_bus_standard_keys = pv_bus_standard_parameters.keys().tolist()
        # Addapts standard Values
        for i in range(len(pv_bus_standard_keys)):
            pv_bus_housespecific_dict[pv_bus_standard_keys[i]] = \
                pv_bus_standard_parameters[pv_bus_standard_keys[i]]
        # Creates Bus-List-Element
        sheets["buses"] = sheets["buses"].append(
            pd.Series(pv_bus_housespecific_dict),
            ignore_index=True)

        # LINK FROM PV BUS TO BUILDING ELECTRICITY BUS

        pv_building_link_housespecific_dict = {
            'label': ID + "pv_" + ID + "_electricity_link",
            'bus_1': ID + "_pv_bus",
            'bus_2': ID + "_electricity_bus",}
        # Extracts the link specific standard values from the given dataset
        pv_building_link_standard_parameters = \
            standard_parameters.parse('Links', index_col='link_type').loc[
                'building_pv_building_link']
        pv_building_link_standard_keys = pv_building_link_standard_parameters.keys().tolist()
        # Addapts standard Values
        for i in range(len(pv_building_link_standard_keys)):
            pv_building_link_housespecific_dict[
                pv_building_link_standard_keys[i]] = \
                pv_building_link_standard_parameters[
                    pv_building_link_standard_keys[i]]
        # Creates link-List-Element
        sheets["links"] = sheets["links"].append(
            pd.Series(pv_building_link_housespecific_dict),
            ignore_index=True)

        # LINK FROM PV BUS TO DISTRICT ELECTRICITY BUS

        pv_district_link_housespecific_dict = {
            'label': ID + "pv_district_electricity_link",
            'active': 1,
            'bus_1': ID + "_pv_bus",
            'bus_2': "district_electricity_bus"}
        # Extracts the link specific standard values from the given dataset
        pv_district_link_standard_parameters = \
            standard_parameters.parse('Links', index_col='link_type').loc[
                'building_pv_district_link']
        pv_district_link_standard_keys = pv_district_link_standard_parameters.keys().tolist()
        # Addapts standard Values
        for i in range(len(pv_district_link_standard_keys)):
            pv_district_link_housespecific_dict[
                pv_district_link_standard_keys[i]] = \
                pv_district_link_standard_parameters[
                    pv_district_link_standard_keys[i]]
        # Creates link-List-Element
        sheets["links"] = sheets["links"].append(
            pd.Series(pv_district_link_housespecific_dict),
            ignore_index=True)

        # LINK FROM DISTRICT ELEC BUS TO BUILDING ELECTRICITY BUS

        district_building_link_housespecific_dict = {
                             'label': ID + "district_electricity_link",
                             'bus_1': "district_electricity_bus",
                             'bus_2': ID + "_electricity_bus"}
        # Extracts the link specific standard values from the given dataset
        district_building_link_standard_parameters = \
            standard_parameters.parse('Links', index_col='link_type').loc[
                'building_district_building_link']
        district_building_link_standard_keys = district_building_link_standard_parameters.keys().tolist()
        # Addapts standard Values
        for i in range(len(district_building_link_standard_keys)):
            district_building_link_housespecific_dict[
                district_building_link_standard_keys[i]] = \
                district_building_link_standard_parameters[
                    district_building_link_standard_keys[i]]
        # Creates link-List-Element
        sheets["links"] = sheets["links"].append(
            pd.Series(district_building_link_housespecific_dict),
            ignore_index=True)


def create_sinks(ID: str, lp_heat: str, lp_el: str, units: int, occupants: int, yoc: str, area: int):
    # ToDo just for max. 5 occupants
    # electricity demand residential building
    # format: household size: SFB, MFB
    # unit kWh/a
    electricity_demand_residential = \
        {
            1: [2300, 1400], 2: [3000, 2000], 3: [3600, 2600], 4: [4000, 3000], 5: [5000, 3600]
        }
    if units == 1:
        demand_el = electricity_demand_residential[occupants][0]
    else:
        demand_el = electricity_demand_residential[occupants][1]
    sheets["sinks"] = sheets["sinks"].append(pd.DataFrame([[ID + "_electricity_demand", "upscaling", 1, 1, ID + "_electricity_bus",
                                                lp_el, "x", demand_el, "x", "x", "x"]],
                                              columns=columns["sinks"]))
    # heat demand residential building
    # format: year of construction: 1 unit, 2 units, 3-6 units, 7-12 units over 13 units
    # unit kWh/(m^2*a)
    heat_demand_residential = \
        {
            "<1918": [247, 238, 212, 182, 169],
        }
    net_floor_area = area * 0.9
    if units == 1:
        index = 0
    elif units == 2:
        index = 1
    elif units > 2 and units < 7:
        index = 2
    elif units > 6 and units < 13:
        index = 3
    else:
        index = 4
    if yoc == "<1918":
        demand_heat = heat_demand_residential[yoc][index] * net_floor_area
    sheets["sinks"] = sheets["sinks"].append(pd.DataFrame([[ID + "_heat_demand", "upscaling", 1, 1, ID + "_heat_bus",
                                                lp_heat, "x", demand_heat, "x", "x", "x"]],
                                              columns=columns["sinks"]))


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

    pv_housespecific_dict = {'label': building_ID + '_' + plant_ID + '_pv_source',
                             'existing capacity /(kW)': 0,
                             'min. investment capacity /(kW)': 0,
                             'output': building_ID + '_pv_bus',
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

    gchp_housespecific_dict = {'label': ID + '_gchp_transformer',
                               'comment': 'automatically_created',
                               'input': ID + '_hp_elec_bus',
                               'output': ID + '_heat_bus',
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

    ashp_housespecific_dict = {'label': ID + '_ashp_transformer',
                               'comment': 'automatically_created',
                               'input': ID + '_hp_elec_bus',
                               'output': ID + '_heat_bus',
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

    # Definies Individual Values
    gas_bus_housespecific_dict = {'label': ID + "_gas_bus"}
    # Extracts the bus specific standard values from the given dataset
    gas_bus_standard_parameters = standard_parameters.parse('Buses', index_col='bus_type').loc['building_gas_bus']
    gas_bus_standard_keys = gas_bus_standard_parameters.keys().tolist()
    # Addapts standard Values
    for i in range(len(gas_bus_standard_keys)):
        gas_bus_housespecific_dict[gas_bus_standard_keys[i]] = \
            gas_bus_standard_parameters[gas_bus_standard_keys[i]]
    # Creates Bus-List-Element
    sheets["buses"] = sheets["buses"].append(pd.Series(gas_bus_housespecific_dict),
                                             ignore_index=True)


    ### GAS HEATING TRANSFORMER

    gas_heating_standard_parameters = standard_parameters.parse('Gasheating')

    gas_heating_housespecific_dict = {'label': ID + '_gasheating_transformer',
                               'comment': 'automatically_created',
                               'input': ID + '_gas_bus',
                               'output': ID + '_heat_bus',
                               'output2': 'None',
                             }

    # read the gchp standards from standard_parameters.xlsx and append
    # them to the gchp_housespecific_dict
    gas_heating_standard_keys = gas_heating_standard_parameters.keys().tolist()
    for i in range(len(gas_heating_standard_keys)):
        gas_heating_housespecific_dict[gas_heating_standard_keys[i]] = \
            gas_heating_standard_parameters[gas_heating_standard_keys[i]][0]

    # produce a pandas series out of the dict above due to easier appending
    gas_heating_series = pd.Series(gas_heating_housespecific_dict)
    sheets["GenericTransformer"] = sheets["GenericTransformer"].append(gas_heating_series, ignore_index=True)


def create_battery(ID, battery_standard_parameters):

    battery_housespecific_dict = {'label': ID + '_battery_storage',
                                  'comment': 'automatically_created',
                                  'bus': ID + '_electricity_bus',
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
                      True if j['gchp area (m2)'] else False,
                      True if j['district heat'] else False,
                      standard_param)
        create_sinks(j['label'], j['load profile heat'],
                     j['load profile electricity'], j['units'], j['occupants'],
                     j['year of construction'],
                     j['living space'] * j['floors'])

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

    # standard_parameters='standard_parameters.xlsx'
    # create_pv_source(ID='Test', azimuth=180, tilt=30, area=10,
    #                  pv_standard_parameters=standard_param.parse('PV'))
    # Open the new Excel file and add all the created components
    j = 0
    writer = pd.ExcelWriter(os.path.dirname(__file__) + "/test_scenario.xlsx",
                            engine='xlsxwriter')
    for i in sheets:
        sheets[i].to_excel(writer, worksheets[j], index=False)
        j = j + 1
    writer.save()

#####
# def create_transformer_element():
#    placeholder = x
#
# def create_link_element():
#    placeholder = x
#
# def create_source_element():
#   placeholder = x
#
#
#

# GASHEIZUNG ERSTELLEN

# HEATPUMPS ERSTELLEN

# ANBINDUNG AN FERNWÄRMENETZ ERSTELLEN

# ELECTRICITY BUS ERSTELLEN

#   create_bus_element

# ELECTRICITY SENKE ERSTELLEN

# create_sink_element

# BATTERY STORAGE ERSTELLEN

# PV ANLAGEN MIT ENTSPTRECHENDEN LINKS ERSTELLEN

