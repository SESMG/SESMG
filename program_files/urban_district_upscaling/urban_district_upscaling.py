import xlsxwriter
import pandas as pd
import os


def copy_standard_parameter_sheet(sheet_tbc: str, standard_parameters):
    """
        use to create an intern copy of the standard_parameters excel
        sheet

        :param sheet_tbc: excel sheet name which has to be copied(_tbc)
        :type sheet_tbc: str
    """

    sheets[sheet_tbc] = standard_parameters.parse(sheet_tbc)


def create_standard_parameter_bus(label: str, bus_type: str, standard_parameters):
    """
        creates a bus with standard_parameters, based on the standard
        parameters given in the "standard_parameters" dataset and adds
        it to the "sheets"-output dataset.

        :param label: label, the created bus will be given
        :type label: str
        :param bus_type: defines, which set of standard param. will be given to
                        the dict
        :type bus_type: str
    """

    # define individual values
    bus_dict = {'label': label}
    # extracts the bus specific standard values from the standard_parameters
    # dataset
    bus_standard_parameters = \
        standard_parameters.parse('buses', index_col='bus_type').loc[bus_type]
    bus_standard_keys = bus_standard_parameters.keys().tolist()
    # addapt standard values
    for i in range(len(bus_standard_keys)):
        bus_dict[bus_standard_keys[i]] = \
            bus_standard_parameters[bus_standard_keys[i]]
    # creates "bus-list-element"
    sheets["buses"] = \
        sheets["buses"].append(pd.Series(bus_dict), ignore_index=True)


def create_standard_parameter_link(label: str, bus_1: str, bus_2: str,
                                   link_type: str, standard_parameters):
    """
        creates a link with standard_parameters, based on the standard
        parameters given in the "standard_parameters" dataset and adds
        it to the "sheets"-output dataset.

        :param label: label, the created link will be given
        :type label: str
        :param bus_1: label, of the first bus
        :type bus_1: str
        :param bus_2: label, of the second bus
        :type bus_2: str
        :param link_type: needed to get the standard parameters of the
                          link to be created
        :type link_type: str
    """
    link_house_specific_dict = {'label': label,
                                'bus1': bus_1,
                                'bus2': bus_2}

    # read the heat network standards from standard_parameters.xlsx and
    # append them to the link_house_specific_dict
    link_standard_parameters = \
        standard_parameters.parse('links', index_col='link_type') \
            .loc[link_type]
    link_standard_keys = link_standard_parameters.keys().tolist()
    for i in range(len(link_standard_keys)):
        link_house_specific_dict[link_standard_keys[i]] = \
            link_standard_parameters[link_standard_keys[i]]

    # produce a pandas series out of the dict above due to easier appending
    link_series = pd.Series(link_house_specific_dict)
    sheets["links"] = sheets["links"].append(link_series,
                                             ignore_index=True)


def create_standard_parameter_sink(sink_type: str, label: str,
                                   sink_input: str, annual_demand: int, standard_parameters):
    """
        creates a sink with standard_parameters, based on the standard
        parameters given in the "standard_parameters" dataset and adds
        it to the "sheets"-output dataset.

        :param sink_type: needed to get the standard parameters of the
                          link to be created
        :type sink_type: str
        :param label: label, the created sink will be given
        :type label: str
        :param sink_input: label of the bus which will be the input of the
                      sink to be created
        :type sink_input: str
        :param annual_demand: #todo formel
        :type annual_demand: int
    """
    sink_standard_parameters = \
        standard_parameters.parse('sinks', index_col="sink_type") \
            .loc[sink_type]
    sink_dict = {'label': label,
                 'input': sink_input,
                 'annual demand': annual_demand}

    # read the heat network standards from standard_parameters.xlsx and append
    # them to the sink_house_specific_dict
    sink_standard_keys = sink_standard_parameters.keys().tolist()
    for i in range(len(sink_standard_keys)):
        sink_dict[sink_standard_keys[i]] = \
            sink_standard_parameters[sink_standard_keys[i]]

    # produce a pandas series out of the dict above due to easier appending
    sink_series = pd.Series(sink_dict)
    sheets["sinks"] = sheets["sinks"].append(sink_series,
                                             ignore_index=True)


def central_comp(central, standard_parameters):
    """
        todo docstring
    """
    for i, j in central.iterrows():
        if j['district_electricity_bus'] == 'yes' \
                or j['district_electricity_bus'] == 'Yes' \
                or j['district_electricity_bus'] == 1:
            create_standard_parameter_bus(
                label='district_electricity_bus',
                bus_type="district_electricity_bus",
                standard_parameters=standard_parameters)

        # create required central components fpr a district heating
        # network
        if j['district_heat_link'] == 'yes' \
                or j['district_heat_link'] == 'Yes' \
                or j['district_heat_link'] == 1:
            # input bus
            create_standard_parameter_bus(label='district_heat_input_bus',
                                          bus_type="district_heat_input_bus",
                                          standard_parameters=standard_parameters)

            # output bus
            create_standard_parameter_bus(label='district_heat_output_bus',
                                          bus_type="district_heat_output_bus",
                                          standard_parameters=standard_parameters)

            # link considering losses
            create_standard_parameter_link(label="district_heat_link",
                                           bus_1="district_heat_input_bus",
                                           bus_2="district_heat_output_bus",
                                           link_type="district_heat_link",
                                           standard_parameters=standard_parameters)
            # central natural gas
            if j['naturalgas_chp'] == 'yes' or j['naturalgas_chp'] == 'Yes' or \
                    j['naturalgas_chp'] == 1:
                create_central_chp(gastype='naturalgas',
                                   standard_parameters=standard_parameters)

            # central bio gas
            if j['biogas_chp'] == 'yes' or j['biogas_chp'] == 'Yes' or \
                    j['biogas_chp'] == 1:
                create_central_chp(gastype='biogas',
                                   standard_parameters=standard_parameters)

            # central swhp todo simplify
            if j['central_swhp_transformer'] == 'yes' \
                    or j['central_swhp_transformer'] == 'Yes' \
                    or j['central_swhp_transformer'] == 1:
                create_central_swhp(standard_parameters=standard_parameters)


def create_central_swhp(standard_parameters):
    """
            todo docstring
    """
    # swhp elec bus
    create_standard_parameter_bus(label="central_swhp_elec_bus",
                                  bus_type="central_swhp_electricity_bus",
                                  standard_parameters=standard_parameters)

    # swhp transformer
    transformers_standard_parameters = standard_parameters.parse('transformers')
    transformers_standard_parameters.set_index('comment', inplace=True)
    swhp_standard_parameters = transformers_standard_parameters.loc['swhp_transformer']
    swhp_central_dict = {'label': 'central_swhp_transformer',
                         'comment': 'automatically_created',
                         'input': "central_swhp_elec_bus",
                         'output': 'district_heat_input_bus',
                         'output2': 'None'}

    # read the swhp standards from standard_parameters.xlsx and append
    # them to the swhp_central_dict
    swhp_standard_keys = swhp_standard_parameters.keys().tolist()
    for i in range(len(swhp_standard_keys)):
        swhp_central_dict[swhp_standard_keys[i]] = \
            swhp_standard_parameters[swhp_standard_keys[i]]#[0]

    # produce a pandas series out of the dict above due to easier appending
    swhp_series = pd.Series(swhp_central_dict)
    sheets["transformers"] = \
        sheets["transformers"].append(swhp_series, ignore_index=True)


def create_central_chp(gastype, standard_parameters):
    """
        todo docstring
    """
    # chp gas bus
    create_standard_parameter_bus(label="chp_" + gastype + "_bus",
                                  bus_type="central_chp_" + gastype + "_bus",
                                  standard_parameters=standard_parameters)

    # central electricity bus
    create_standard_parameter_bus(
        label="chp_" + gastype + "_elec_bus",
        bus_type="central_chp_" + gastype + "_electricity_bus",
        standard_parameters=standard_parameters)

    # connection to district electricity bus
    create_standard_parameter_link(
        label="central_chp_" + gastype + "_elec_district_link",
        bus_1="chp_" + gastype + "_elec_bus",
        bus_2="district_electricity_bus",
        link_type="central_chp_elec_district_link",
        standard_parameters=standard_parameters)

    # chp transformer
    chp_standard_parameters = standard_parameters.parse(
        'transformers')
    # transformers_standard_parameters = standard_parameters.parse('transformers')
    # transformers_standard_parameters.set_index('comment', inplace=True)
    # ng_chp_standard_parameters = transformers_standard_parameters.loc['natural_gas_chp']
    # bg_chp_standard_parameters = transformers_standard_parameters.loc['bio_gas_chp']

    chp_central_dict = {'label': gastype + '_chp_transformer',
                        'input': "chp_" + gastype + "_bus",
                        'output': "chp_" + gastype + "_elec_bus",
                        'output2': "district_heat_input_bus"
                        }
    # read the chp standards from standard_parameters.xlsx and append
    # them to the gchp_central_dict
    chp_standard_keys = chp_standard_parameters.keys().tolist()
    for i in range(len(chp_standard_keys)):
        chp_central_dict[chp_standard_keys[i]] = \
            chp_standard_parameters[chp_standard_keys[i]][0]

    # produce a pandas series out of the dict above due to easier appending
    chp_series = pd.Series(chp_central_dict)
    sheets["transformers"] = sheets["transformers"].append(
        chp_series, ignore_index=True)


def create_buses(id: str, pv_bus: bool, hp_elec_bus,
                  district_heat_bus, district_elec_bus, gchp, standard_parameters):
    """
        todo docstring
    """

    # house electricity bus
    create_standard_parameter_bus(label=str(id) + "_electricity_bus",
                                  bus_type='building_electricity_bus',
                                  standard_parameters=standard_parameters)

    # house heat bus
    create_standard_parameter_bus(label=str(id) + "_heat_bus",
                                  bus_type='building_heat_bus',
                                  standard_parameters=standard_parameters)

    if hp_elec_bus:
        # building hp electricity bus
        create_standard_parameter_bus(label=str(id) + "_hp_elec_bus",
                                      bus_type='building_hp_electricity_bus',
                                      standard_parameters=standard_parameters)
        if gchp:
            # electricity link from building electricity bus to hp elec bus
            create_standard_parameter_link(label=str(id) + "_gchp_building_link",
                                           bus_1=str(id) + "_electricity_bus",
                                           bus_2=str(id) + "_hp_elec_bus",
                                           link_type="building_hp_elec_link",
                                           standard_parameters=standard_parameters)

    if district_heat_bus:
        # heat link from district heat network to building heat bus
        create_standard_parameter_link(label=str(id) + "_district_heat_link",
                                       bus_1="district_heat_output_bus",
                                       bus_2=str(id) + "_heat_bus",
                                       link_type="building_district_heat_link",
                                       standard_parameters=standard_parameters)

    # todo excess constraint costs
    if pv_bus:
        # building pv bus
        create_standard_parameter_bus(label=str(id) + "_pv_bus",
                                      bus_type='building_pv_bus',
                                      standard_parameters=standard_parameters)

        # link from pv bus to building electricity bus
        create_standard_parameter_link(
            label=str(id) + "pv_" + str(id) + "_electricity_link",
            bus_1=str(id) + "_pv_bus", bus_2=str(id) + "_electricity_bus",
            link_type="building_pv_district_link",
            standard_parameters=standard_parameters)
        if district_elec_bus:
            # link from pv bus to district electricity bus
            create_standard_parameter_link(
                label=str(id) + "pv_district_electricity_link",
                bus_1=str(id) + "_pv_bus", bus_2="district_electricity_bus",
                link_type="building_pv_district_link",
                standard_parameters=standard_parameters)

            # link from district elec bus to building electricity bus
            create_standard_parameter_link(
                label=str(id) + "district_electricity_link",
                bus_1="district_electricity_bus",
                bus_2=str(id) + "_electricity_bus",
                link_type="building_district_building_link",
                standard_parameters=standard_parameters)


def create_sinks(id: str, building_type: str, units: int,
                 occupants: int, yoc: str, area: int, standard_parameters):
    """
        TODO DOCSTRING
    """
    # electricity demand
    if building_type != 'None':
        # residential parameters
        if "RES" in building_type:
            electricity_demand_residential = {}
            electricity_demand_standard_param = \
                standard_parameters.parse('ResElecDemand')
            for i in range(len(electricity_demand_standard_param)):
                electricity_demand_residential[
                    electricity_demand_standard_param['household size'][i]] = \
                    [electricity_demand_standard_param[
                         building_type + ' (kWh/a)'][i]]

            if occupants <= 5:
                demand_el = electricity_demand_residential[occupants][0]
                demand_el = demand_el * units
            elif occupants > 5:
                demand_el = (electricity_demand_residential[5][0]) / 5 * occupants
                demand_el = demand_el * units

        # commercial parameters
        elif "COM" in building_type:
            electricity_demand_standard_param = \
                standard_parameters.parse('ComElecDemand')
            electricity_demand_standard_param.set_index(
                "commercial type", inplace=True)
            demand_el = electricity_demand_standard_param \
                .loc[building_type]['specific demand (kWh/m2/a)']
            net_floor_area = area * 0.9  # todo: give this value with standard parameter dataset
            demand_el = demand_el * net_floor_area

        create_standard_parameter_sink(sink_type=building_type + "_electricity_sink",
                                       label=str(id) + "_electricity_demand",
                                       sink_input=str(id) + "_electricity_bus",
                                       annual_demand=demand_el,
                                       standard_parameters=standard_parameters)

    # heat demand

    # residential building
    if building_type != "None":
        if "RES" in building_type:
            # read standard values from standard_parameter-dataset
            heat_demand_standard_param = \
                standard_parameters.parse('ResHeatDemand')
            heat_demand_standard_param.set_index(
                "year of construction", inplace=True)
            specific_heat_demand = \
                heat_demand_standard_param \
                    .loc[yoc][str(int(units)) + ' unit(s)']

            net_floor_area = area * 0.9  # todo: give this value with standard parameter dataset

            if units <= 12:
                demand_heat = specific_heat_demand * net_floor_area
            if units > 12:
                demand_heat = specific_heat_demand * net_floor_area

        # commercial building
        elif "COM" in building_type:
            heat_demand_standard_parameters = \
                standard_parameters.parse('ComHeatDemand')
            heat_demand_standard_parameters.set_index(
                "year of construction", inplace=True)
            demand_heat = heat_demand_standard_parameters \
                .loc[yoc][building_type]
            net_floor_area = area * 0.9  # todo: give this value with standard parameter dataset
            demand_heat = demand_heat * net_floor_area

        create_standard_parameter_sink(sink_type=building_type + "_heat_sink",
                                       label=str(id) + "_heat_demand",
                                       sink_input=str(id) + "_heat_bus",
                                       annual_demand=demand_heat,
                                       standard_parameters=standard_parameters)


def create_pv_source(building_id, plant_id, azimuth, tilt, area,
                     pv_standard_parameters, latitude, longitude):
    """
        todo docstring
    :param longitude:
    :param latitude:
    :param id:
    :param azimuth:
    :param tilt:
    :param area:
    :param pv_standard_parameters: excel sheet
    :return:
    """
    # technical parameters
    pv_house_specific_dict = \
        {'label': str(building_id) + '_' + str(plant_id) + '_pv_source',
         'existing capacity': 0,
         'min. investment capacity': 0,
         'output': str(building_id) + '_pv_bus',
         'Azimuth': azimuth,
         'Surface Tilt': tilt,
         'Latitude': latitude,
         'Longitude': longitude}

    # read the pv standards from standard_parameters.xlsx and append
    # them to the pv_house_specific_dict
    pv_standard_keys = pv_standard_parameters.keys().tolist()
    for i in range(len(pv_standard_keys)):
        pv_house_specific_dict[pv_standard_keys[i]] = \
            pv_standard_parameters[pv_standard_keys[i]]#[0]

    pv_house_specific_dict['max. investment capacity'] = \
        pv_standard_parameters['Capacity per Area (kW/m2)']* area #[0] * area

    # produce a pandas series out of the dict above due to easier appending
    pv_series = pd.Series(pv_house_specific_dict)
    sheets["sources"] = sheets["sources"].append(pv_series, ignore_index=True)


def create_gchp(id, area, standard_parameters):
    # gchp transformer
    # gchp_standard_parameters = standard_parameters.parse('GCHP')
    transformers_standard_parameters = standard_parameters.parse('transformers')
    transformers_standard_parameters.set_index('comment', inplace=True)
    gchp_standard_parameters = transformers_standard_parameters.loc['gchp_transformer']

    gchp_house_specific_dict = {'label': str(id) + '_gchp_transformer',
                                'comment': 'automatically_created',
                                'input': str(id) + '_hp_elec_bus',
                                'output': str(id) + '_heat_bus',
                                'output2': 'None',
                                'area': area,
                                'existing capacity': 0,
                                'min. investment capacity': 0}

    # read the gchp standards from standard_parameters.xlsx and append
    # them to the gchp_house_specific_dict
    gchp_standard_keys = gchp_standard_parameters.keys().tolist()
    for i in range(len(gchp_standard_keys)):
        gchp_house_specific_dict[gchp_standard_keys[i]] = \
            gchp_standard_parameters[gchp_standard_keys[i]]#[0]

    # produce a pandas series out of the dict above due to easier appending
    gchp_series = pd.Series(gchp_house_specific_dict)
    sheets["transformers"] = \
        sheets["transformers"].append(gchp_series, ignore_index=True)


def create_ashp(id, standard_parameters):
    # ashp transformer
    # ashp_standard_parameters = standard_parameters.parse('ASHP')
    transformers_standard_parameters = standard_parameters.parse('transformers')
    transformers_standard_parameters.set_index('comment', inplace=True)
    ashp_standard_parameters = transformers_standard_parameters.loc['ashp_transformer']

    ashp_house_specific_dict = {'label': str(id) + '_ashp_transformer',
                                'comment': 'automatically_created',
                                'input': str(id) + '_hp_elec_bus',
                                'output': str(id) + '_heat_bus',
                                'output2': 'None',
                                'existing capacity': 0,
                                'min. investment capacity': 0}

    # read the ashp standards from standard_parameters.xlsx and append
    # them to the ashp_house_specific_dict
    ashp_standard_keys = ashp_standard_parameters.keys().tolist()
    for i in range(len(ashp_standard_keys)):
        ashp_house_specific_dict[ashp_standard_keys[i]] = \
            ashp_standard_parameters[ashp_standard_keys[i]]#[0]

    # produce a pandas series out of the dict above due to easier appending
    ashp_series = pd.Series(ashp_house_specific_dict)
    sheets["transformers"] = \
        sheets["transformers"].append(ashp_series, ignore_index=True)


def create_gas_heating(id, standard_parameters):
    # building gas bus
    create_standard_parameter_bus(label=str(id) + "_gas_bus",
                                  bus_type='building_gas_bus',
                                  standard_parameters=standard_parameters)

    # gas heating transformer
    #gas_heating_standard_parameters = standard_parameters.parse('transformers')

    transformers_standard_parameters = standard_parameters.parse('transformers')
    transformers_standard_parameters.set_index('comment', inplace=True)
    gas_heating_standard_parameters = transformers_standard_parameters.loc[
        'gasheating_transformer']


    # define individual gas_heating_parameters
    gas_heating_house_specific_dict = \
        {'label': str(id) + '_gasheating_transformer',
         'comment': 'automatically_created',
         'input': str(id) + '_gas_bus',
         'output': str(id) + '_heat_bus',
         'output2': 'None'}

    # read the gasheating standards from standard_parameters.xlsx and append
    # them to the  gas_heating_house_specific_dict
    gas_heating_standard_keys = gas_heating_standard_parameters.keys().tolist()
    for i in range(len(gas_heating_standard_keys)):
        gas_heating_house_specific_dict[gas_heating_standard_keys[i]] = \
            gas_heating_standard_parameters[gas_heating_standard_keys[i]]#[0]

    # produce a pandas series out of the dict above due to easier appending
    gas_heating_series = pd.Series(gas_heating_house_specific_dict)
    sheets["transformers"] = \
        sheets["transformers"] \
            .append(gas_heating_series, ignore_index=True)


def create_battery(id, battery_standard_parameters):
    """
        todo docstring
    """
    battery_house_specific_dict = {'label': str(id) + '_battery_storage',
                                   'comment': 'automatically_created',
                                   'bus': str(id) + '_electricity_bus'}

    # read the battery standards from standard_parameters.xlsx and append
    # them to the battery_house_specific_dict
    battery_standard_keys = battery_standard_parameters.keys().tolist()
    for i in range(len(battery_standard_keys)):
        battery_house_specific_dict[battery_standard_keys[i]] = \
            battery_standard_parameters[battery_standard_keys[i]]#[0]

    # produce a pandas series out of the dict above due to easier appending
    battery_series = pd.Series(battery_house_specific_dict)
    sheets["storages"] = \
        sheets["storages"].append(battery_series, ignore_index=True)


def urban_district_upscaling_tool(pre_scenario: str, standard_parameter_path: str, output_scenario: str,
                                  plain_sheet: str):
    # todo: docstrings

    print('Creating scenario sheet...')
    xls = pd.ExcelFile(plain_sheet)
    standard_parameters = pd.ExcelFile(standard_parameter_path)


    sheet_names = xls.sheet_names
    columns = {}
    for i in range(1, len(sheet_names)):
        columns[sheet_names[i]] = xls.parse(sheet_names[i]).keys()

    worksheets = [i for i in columns.keys()]
    global sheets
    sheets = {}

    for sheet in worksheets:
        units1 = {}
        sheets_units = {}
        sheets.update({sheet: pd.DataFrame(columns=(columns[sheet]))})
        units = next(xls.parse(sheet).iterrows())[1]
        for unit in units.keys():
            units1.update({unit: units[unit]})

        sheets[sheet] = sheets[sheet].append(pd.Series(data=units1), ignore_index=True)

    # import the sheet which is filled by the user
    xls = pd.ExcelFile(pre_scenario)
    tool = xls.parse("tool")
    central = xls.parse("central")
    central_comp(central, standard_parameters)
    # set variable for central heating if activated to decide rather a house
    # can be connected to the district heat network or not
    central_heating_network = False
    central_electricity_network = False

    for i, j in central.iterrows():
        if j['district_heat_link'] == 'yes' \
                or j['district_heat_link'] == 'Yes' \
                or j['district_heat_link'] == 1:
            central_heating_network = True
        if j['district_electricity_bus'] == 'yes' \
                or j['district_electricity_bus'] == 'Yes' \
                or j['district_electricity_bus'] == 1:
            central_electricity_network = True
    for i, j in tool.iterrows():
        # foreach building the three necessary buses will be created
        create_buses(j['label'],
                      True if j['azimuth 1 (°)'] or j['azimuth 2 (°)'] else False,
                      True if j['gchp area (m2)'] or j['ashp'] else False,
                      True if ((j['district heat'] == 'yes'
                                or j['district heat'] == 'Yes'
                                or j['district heat'] == 1)
                               and
                               central_heating_network) else False,
                      central_electricity_network,
                      True if j['gchp area (m2)'] != 0 else False,
                      standard_parameters=standard_parameters)
        create_sinks(id=j['label'],
                     building_type=j['building type'],
                     units=j['units'],
                     occupants=j['occupants per unit'],
                     yoc=j['year of construction'],
                     area=j['living space'] * j['floors'],
                     standard_parameters=standard_parameters)

        # Define PV Standard-Parameters
        sources_standard_parameters = standard_parameters.parse('sources')
        sources_standard_parameters.set_index('comment', inplace = True)
        pv_standard_parameters = sources_standard_parameters.loc['fixed photovoltaic source']

        # create pv-sources
        if j['azimuth 1 (°)']:
            create_pv_source(building_id=j['label'],
                             plant_id='1',
                             azimuth=j['azimuth 1 (°)'],
                             tilt=j['surface tilt 1 (°)'],
                             area=j['roof area 1 (m²)'],
                             latitude=j['latitude'],
                             longitude=j['longitude'],
                             pv_standard_parameters=pv_standard_parameters)



        if j['azimuth 2 (°)']:
            create_pv_source(building_id=j['label'],
                             plant_id='2',
                             azimuth=j['azimuth 2 (°)'],
                             tilt=j['surface tilt 2 (°)'],
                             area=j['roof area 2 (m²)'],
                             latitude=j['latitude'],
                             longitude=j['longitude'],
                             pv_standard_parameters=pv_standard_parameters)

        if j['azimuth 3 (°)']:
            create_pv_source(building_id=j['label'],
                             plant_id='3',
                             azimuth=j['azimuth 3 (°)'],
                             tilt=j['surface tilt 3 (°)'],
                             area=j['roof area 3 (m²)'],
                             latitude=j['latitude'],
                             longitude=j['longitude'],
                             pv_standard_parameters=pv_standard_parameters)

        if j['azimuth 4 (°)']:
            create_pv_source(building_id=j['label'],
                             plant_id='4',
                             azimuth=j['azimuth 4 (°)'],
                             tilt=j['surface tilt 4 (°)'],
                             area=j['roof area 4 (m²)'],
                             latitude=j['latitude'],
                             longitude=j['longitude'],
                             pv_standard_parameters=pv_standard_parameters)

        # creates heat-pumps
        if j['gchp area (m2)']:
            create_gchp(id=j['label'], area=j['gchp area (m2)'],
                        standard_parameters=standard_parameters)

        # creates heat-pumps
        if j['ashp'] == 'yes' or j['ashp'] == 'Yes' or j['ashp'] == 1:
            create_ashp(id=j['label'],
                        standard_parameters=standard_parameters)

        # creates gasheating-system
        if j['gas heating'] == 'yes' or j['gas heating'] == 'Yes' \
                or j['gas heating'] == 1:
            create_gas_heating(id=j['label'],
                               standard_parameters=standard_parameters)

        # battery storage

        # Define battery Standard-Parameters
        storages_standard_parameters = standard_parameters.parse('storages')
        storages_standard_parameters.set_index('comment', inplace = True)
        battery_standard_parameters = storages_standard_parameters.loc['battery storage']


        if j['battery storage'] == 'yes' or j['battery storage'] == 'Yes' \
                or j['battery storage'] == 1:
            create_battery(
                id=j['label'],
                battery_standard_parameters=battery_standard_parameters)

        print(str(j['label']) + ' subsystem added to scenario sheet.')

    # add general energy system information to "energysystem"-sheet
    copy_standard_parameter_sheet(sheet_tbc='energysystem',
                                  standard_parameters=standard_parameters)

    # adds weather data to "weather data"-sheet
    copy_standard_parameter_sheet(sheet_tbc='weather data',
                                  standard_parameters=standard_parameters)

    # adds weather data to "weather data"-sheet
    copy_standard_parameter_sheet(sheet_tbc='time series',
                                  standard_parameters=standard_parameters)
    # open the new excel file and add all the created components
    j = 0
    writer = pd.ExcelWriter(output_scenario,
                            engine='xlsxwriter')

    for i in sheets:
        sheets[i].to_excel(writer, worksheets[j], index=False)
        j = j + 1
    print("Scenario created. It can now be executed.")
    writer.save()


if __name__ == '__main__':
    urban_district_upscaling_tool(pre_scenario=os.path.dirname(__file__) + r"\pre_scenario.xlsx",
                                  standard_parameter_path=os.path.dirname(__file__) + r"\standard_parameters.xlsx",
                                  output_scenario=os.path.dirname(__file__) + r"\test_scenario.xlsx",
                                  plain_sheet=os.path.dirname(__file__) + r'\plain_scenario.xlsx')
