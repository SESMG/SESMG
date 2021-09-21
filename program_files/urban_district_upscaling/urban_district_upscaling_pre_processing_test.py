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


def create_standard_parameter_bus(label: str, bus_type: str, standard_parameters,
                                  lat=None,lon=None, dh=None):
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
    if lat is not None:
        bus_dict.update({"district heating conn.": dh})
        bus_dict.update({"lat": lat})
        bus_dict.update({"lon": lon})
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
                                   sink_input: str, annual_demand: int,
                                   standard_parameters, lat=None, lon=None):
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
                 'annual demand': annual_demand,
                 'district heating': 1 if lat is not None else 0,
                 'lat': lat,
                 'lon': lon}

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

def create_standard_parameter_transformer(specific_param, standard_parameters, standard_param_name):
    """

    :param specific_param:
    :param standard_param:
    :return:
    """

    # read the standards from standard_param and append
    # them to the dict
    transformers_standard_parameters = standard_parameters.parse('transformers')
    transformers_standard_parameters.set_index('comment', inplace=True)
    standard_param = transformers_standard_parameters.loc[standard_param_name]

    standard_keys = standard_param.keys().tolist()
    for i in range(len(standard_keys)):
        specific_param[standard_keys[i]] = \
            standard_param[standard_keys[i]]

    # produce a pandas series out of the dict above due to easier appending
    transformer_series = pd.Series(specific_param)
    sheets["transformers"] = \
        sheets["transformers"].append(transformer_series, ignore_index=True)

def create_standard_parameter_storage(specific_param, standard_parameters, standard_param_name):
    """

    :param specific_param:
    :param standard_param_name:
    :return:
    """

    # read the standards from standard_param and append
    # them to the dict
    storage_standard_parameters = standard_parameters.parse('storages')
    storage_standard_parameters.set_index('comment', inplace=True)
    standard_param = storage_standard_parameters.loc[standard_param_name]

    standard_keys = standard_param.keys().tolist()
    for i in range(len(standard_keys)):
        specific_param[standard_keys[i]] = \
            standard_param[standard_keys[i]]

    # produce a pandas series out of the dict above due to easier appending
    transformer_series = pd.Series(specific_param)
    sheets["storages"] = \
        sheets["storages"].append(transformer_series, ignore_index=True)


def central_comp(central, standard_parameters):
    """
        todo docstring
    """
    for i, j in central.iterrows():
        if j['electricity_bus'] in ['Yes', 'yes', 1]:
            create_standard_parameter_bus(
                label='central_electricity_bus',
                bus_type="central_electricity_bus",
                standard_parameters=standard_parameters)

        # create required central components for a central heating
        # network
        #if j['heat_link'] in ['yes', 'Yes', 1]:
        #    # input bus
        #    create_standard_parameter_bus(label='central_heat_input_bus',
        #                                  bus_type="central_heat_input_bus",
        #                                  standard_parameters=standard_parameters)

            # output bus
        #    create_standard_parameter_bus(label='central_heat_output_bus',
        #                                  bus_type="central_heat_output_bus",
        #                                  standard_parameters=standard_parameters)

            # link considering losses
        #    create_standard_parameter_link(label="central_heat_link",
        #                                   bus_1="central_heat_input_bus",
        #                                   bus_2="central_heat_output_bus",
        #                                   link_type="central_heat_link",
        #                                   standard_parameters=standard_parameters)
        # central natural gas
        if j['naturalgas_chp'] in ['yes', 'Yes', 1]:
            create_standard_parameter_bus(label='central_heat_input_bus',
                                          bus_type="central_heat_input_bus",
                                          standard_parameters=standard_parameters,
                                          dh="dh-system",
                                          lat=j["lat.-chp"],
                                          lon=j["lon.-chp"])
                                          
            create_central_chp(gastype='naturalgas',
                               standard_parameters=standard_parameters)

        # central bio gas
        if j['biogas_chp'] in ['yes', 'Yes', 1]:
            create_central_chp(gastype='biogas',
                               standard_parameters=standard_parameters)

        # central swhp todo simplify
        if j['swhp_transformer'] in ['yes', 'Yes', 1]:
            create_central_swhp(standard_parameters=standard_parameters)

        # central biomass plant
        if j['biomass_plant'] in ['yes', 'Yes', 1]:
           create_central_biomass_plant(standard_parameters=standard_parameters)

        # power to gas system
        if j['power_to_gas'] in ['yes', 'Yes', 1]:
            create_power_to_gas_system(standard_parameters=standard_parameters)

        if j['battery_storage'] in ['yes', 'Yes', 1]:
            create_battery(id="central", standard_parameters=standard_parameters, storage_type="central")

def create_power_to_gas_system(standard_parameters):
    """
        todo: docstrings

    :param standard_parameters:
    :return:
    """

    # h2 bus
    create_standard_parameter_bus(label="central_h2_bus",
                                  bus_type="central_h2_bus",
                                  standard_parameters=standard_parameters)

    # natural gas bus
    create_standard_parameter_bus(label="central_naturalgas_bus",
                                  bus_type="central_naturalgas_bus",
                                  standard_parameters=standard_parameters)

    # electrolysis transformer
    electrolysis_transformer_param = \
        {'label': 'central_electrolysis_transformer',
         'comment': 'automatically_created',
         'input': 'central_electricity_bus',
         'output': 'central_h2_bus',
         'output2': 'None'}

    create_standard_parameter_transformer(specific_param=electrolysis_transformer_param,
                                          standard_parameters=standard_parameters,
                                          standard_param_name='central_electrolysis_transformer')

    # methanization transformer
    methanization_transformer_param = \
        {'label': 'central_methanization_transformer',
         'comment': 'automatically_created',
         'input': 'central_h2_bus',
         'output': 'central_naturalgas_bus',
         'output2': 'None'}

    create_standard_parameter_transformer(specific_param=methanization_transformer_param,
                                          standard_parameters=standard_parameters,
                                          standard_param_name='central_methanization_transformer')

    # fuel cell transformer
    fuelcell_transformer_param = \
        {'label': 'central_fuelcell_transformer',
         'comment': 'automatically_created',
         'input': 'central_h2_bus',
         'output': 'central_electricity_bus',
         'output2': 'central_heat_input_bus'}

    create_standard_parameter_transformer(specific_param=fuelcell_transformer_param,
                                          standard_parameters=standard_parameters,
                                          standard_param_name='central_fuelcell_transformer')

    # h2 storage
    h2_storage_param = {'label': 'central_h2_storage',
                        'comment': 'automatically_created',
                        'bus': 'central_h2_bus'}

    create_standard_parameter_storage(specific_param=h2_storage_param,
                                      standard_parameters=standard_parameters,
                                      standard_param_name='central_h2_storage')

    # natural gas storage
    ng_storage_param = {'label': 'central_naturalgas_storage',
                        'comment': 'automatically_created',
                        'bus': 'central_naturalgas_bus'}

    create_standard_parameter_storage(specific_param=ng_storage_param,
                                      standard_parameters=standard_parameters,
                                      standard_param_name='central_naturalgas_storage')

    # link to chp_naturalgas_bus
    create_standard_parameter_link(label='central_naturalgas_chp_naturalgas_link',
                                   bus_1='central_naturalgas_bus',
                                   bus_2='central_chp_naturalgas_bus',
                                   link_type='central_naturalgas_chp_link',
                                   standard_parameters=standard_parameters)


def create_central_biomass_plant(standard_parameters):
    """
            todo docstring
    """
    # biomass bus
    create_standard_parameter_bus(label="central_biomass_bus",
                                  bus_type="central_biomass_bus",
                                  standard_parameters=standard_parameters)

    # biomass transformer
    transformers_standard_parameters = standard_parameters.parse(
        'transformers')
    transformers_standard_parameters.set_index('comment', inplace=True)
    biomass_standard_parameters = transformers_standard_parameters.loc[
        'central_biomass_transformer']
    biomass_central_dict = {'label': 'central_biomass_transformer',
                         'comment': 'automatically_created',
                         'input': "central_biomass_bus",
                         'output': 'central_heat_input_bus',
                         'output2': 'None'}

    # read the biomass standards from standard_parameters.xlsx and append
    # them to the biomass_central_dict
    biomass_standard_keys = biomass_standard_parameters.keys().tolist()
    for i in range(len(biomass_standard_keys)):
        biomass_central_dict[biomass_standard_keys[i]] = \
            biomass_standard_parameters[biomass_standard_keys[i]]  # [0]

    # produce a pandas series out of the dict above due to easier appending
    biomass_series = pd.Series(biomass_central_dict)
    sheets["transformers"] = \
        sheets["transformers"].append(biomass_series, ignore_index=True)


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
    swhp_standard_parameters = transformers_standard_parameters.loc['central_swhp_transformer']
    swhp_central_dict = {'label': 'central_swhp_transformer',
                         'comment': 'automatically_created',
                         'input': "central_swhp_elec_bus",
                         'output': 'central_heat_input_bus',
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
    create_standard_parameter_bus(label="central_chp_" + gastype + "_bus",
                                  bus_type="central_chp_" + gastype + "_bus",
                                  standard_parameters=standard_parameters)

    # central electricity bus
    create_standard_parameter_bus(
        label="central_chp_" + gastype + "_elec_bus",
        bus_type="central_chp_" + gastype + "_electricity_bus",
        standard_parameters=standard_parameters)

    # connection to central electricity bus
    create_standard_parameter_link(
        label="central_chp_" + gastype + "_elec_central_link",
        bus_1="central_chp_" + gastype + "_elec_bus",
        bus_2="central_electricity_bus",
        link_type="central_chp_elec_central_link",
        standard_parameters=standard_parameters)

    # chp transformer
    chp_standard_parameters = standard_parameters.parse(
        'transformers')

    chp_central_dict = {'label': 'central_' + gastype + '_chp_transformer',
                        'input': "central_chp_" + gastype + "_bus",
                        'output': "central_chp_" + gastype + "_elec_bus",
                        'output2': "central_heat_input_bus"
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


def create_buses(id: str, pv_bus: bool, building_type, hp_elec_bus,
                 central_heat_bus, central_elec_bus, gchp, standard_parameters,
                 gchp_heat_bus=None, gchp_elec_bus=None):
    """
        todo docstring
    """
    if building_type == "RES":
        bus = 'building_res_electricity_bus'
    else:
        bus = 'building_com_electricity_bus'
    if pv_bus or building_type != "0":
        # house electricity bus
        create_standard_parameter_bus(label=str(id) + "_electricity_bus",
                                      bus_type=bus,
                                      standard_parameters=standard_parameters)
        if central_elec_bus:
            # link from central elec bus to building electricity bus
            create_standard_parameter_link(
                label=str(id) + "central_electricity_link",
                bus_1="central_electricity_bus",
                bus_2=str(id) + "_electricity_bus",
                link_type="building_central_building_link",
                standard_parameters=standard_parameters)

    if building_type != "0":
        # house heat bus
        create_standard_parameter_bus(label=str(id) + "_heat_bus",
                                      bus_type='building_heat_bus',
                                      standard_parameters=standard_parameters)

    if hp_elec_bus:
        # building hp electricity bus
        create_standard_parameter_bus(label=str(id) + "_hp_elec_bus",
                                      bus_type='building_hp_electricity_bus',
                                      standard_parameters=standard_parameters)
        # electricity link from building electricity bus to hp elec bus
        create_standard_parameter_link(
                label=str(id) + "_gchp_building_link",
                bus_1=str(id) + "_electricity_bus",
                bus_2=str(id) + "_hp_elec_bus",
                link_type="building_hp_elec_link",
                standard_parameters=standard_parameters)
        if gchp:
            if gchp_elec_bus is not None:
                create_standard_parameter_link(label=str(id) + "_parcel_gchp_elec",
                                               bus_1=str(id) + "_hp_elec_bus" ,
                                               bus_2=gchp_elec_bus,
                                               link_type="building_hp_elec_link",
                                               standard_parameters=standard_parameters)
                create_standard_parameter_link(label=str(id) + "_parcel_gchp",
                                               bus_1=gchp_heat_bus,
                                               bus_2=str(id) + "_heat_bus",
                                               link_type="building_hp_elec_link",
                                               standard_parameters=standard_parameters)
                
    if central_heat_bus and building_type != "0":
        # heat link from central heat network to building heat bus
        create_standard_parameter_link(label=str(id) + "_central_heat_link",
                                       bus_1="central_heat_output_bus",
                                       bus_2=str(id) + "_heat_bus",
                                       link_type="building_central_heat_link",
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
            link_type="building_pv_central_link",
            standard_parameters=standard_parameters)
        if central_elec_bus:
            # link from pv bus to central electricity bus
            create_standard_parameter_link(
                label=str(id) + "pv_central_electricity_link",
                bus_1=str(id) + "_pv_bus", bus_2="central_electricity_bus",
                link_type="building_pv_central_link",
                standard_parameters=standard_parameters)



def create_sinks(id: str, building_type: str, units: int,
                 occupants: int, yoc: str, area: int, standard_parameters,
                 latitude, longitude):
    """
        TODO DOCSTRING
    """
    # electricity demand
    if building_type not in ['None', '0', 0]: # TODO
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
                .loc[building_type]['specific demand (kWh/(sqm a))']
            net_floor_area = area * 0.9  # todo: give this value with standard parameter dataset
            demand_el = demand_el * net_floor_area

        create_standard_parameter_sink(sink_type=building_type + "_electricity_sink",
                                       label=str(id) + "_electricity_demand",
                                       sink_input=str(id) + "_electricity_bus",
                                       annual_demand=demand_el,
                                       standard_parameters=standard_parameters)

    # heat demand

    # residential building
    if building_type not in ['None', '0', 0]: # TODO
        if "RES" in building_type:
            # read standard values from standard_parameter-dataset
            heat_demand_standard_param = \
                standard_parameters.parse('ResHeatDemand')
            heat_demand_standard_param.set_index(
                "year of construction", inplace=True)
            if int(yoc) <= 1918: #TODO
                yoc = "<1918"
            if units > 12:
                units = "> 12"
            specific_heat_demand = \
                heat_demand_standard_param \
                    .loc[yoc][str(units) + ' unit(s)']
            net_floor_area = area * 0.9  # todo: give this value with standard parameter dataset

            demand_heat = specific_heat_demand * net_floor_area

        # commercial building
        elif "COM" in building_type:
            heat_demand_standard_parameters = \
                standard_parameters.parse('ComHeatDemand')
            heat_demand_standard_parameters.set_index(
                "year of construction", inplace=True)
            if int(yoc) <= 1918: #TODO
                yoc = "<1918"
            demand_heat = heat_demand_standard_parameters \
                .loc[yoc][building_type]
            net_floor_area = area * 0.9  # todo: give this value with standard parameter dataset
            demand_heat = demand_heat * net_floor_area

        create_standard_parameter_sink(sink_type=building_type + "_heat_sink",
                                       label=str(id) + "_heat_demand",
                                       sink_input=str(id) + "_heat_bus",
                                       annual_demand=demand_heat,
                                       standard_parameters=standard_parameters,
                                       lat=latitude,
                                       lon=longitude)


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
         'Longitude': longitude,
         'input': 0}

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


def create_solarthermal_source(building_id, plant_id, azimuth, tilt, area,
                     solarthermal_standard_parameters, latitude, longitude):
    """

    :return:
    """

    # technical parameters
    solarthermal_house_specific_dict = \
        {'label': str(building_id) + '_' + str(plant_id) + '_solarthermal_source',
         'existing capacity': 0,
         'min. investment capacity': 0,
         'output': str(building_id) + '_heat_bus',
         'Azimuth': azimuth,
         'Surface Tilt': tilt,
         'Latitude': latitude,
         'Longitude': longitude,
         'input': str(building_id)+'_electricity_bus'}

    # read the pv standards from standard_parameters.xlsx and append
    # them to the pv_house_specific_dict
    solarthermal_standard_keys = solarthermal_standard_parameters.keys().tolist()
    for i in range(len(solarthermal_standard_keys)):
        solarthermal_house_specific_dict[solarthermal_standard_keys[i]] = \
            solarthermal_standard_parameters[solarthermal_standard_keys[i]]  # [0]

    solarthermal_house_specific_dict['max. investment capacity'] = \
        solarthermal_standard_parameters[
            'Capacity per Area (kW/m2)'] * area

    # produce a pandas series out of the dict above due to easier appending
    solarthermal_series = pd.Series(solarthermal_house_specific_dict)
    sheets["sources"] = sheets["sources"].append(solarthermal_series, ignore_index=True)


def create_competition_constraint(component1, factor1, component2, factor2, limit):
    """

    :param component1:
    :param factor1:
    :param component2:
    :param factor2:
    :return:
    """
    # define individual values
    constraint_dict = {'component 1': component1,
                       'factor 1': factor1,
                       'component 2': component2,
                       'factor 2': factor2,
                       'limit': limit,
                       'active': 1}

    sheets["competition constraints"] = \
        sheets["competition constraints"].append(pd.Series(constraint_dict), ignore_index=True)


def create_gchp(id, area, standard_parameters):
    # gchp transformer
    # gchp_standard_parameters = standard_parameters.parse('GCHP')
    transformers_standard_parameters = standard_parameters.parse('transformers')
    transformers_standard_parameters.set_index('comment', inplace=True)
    gchp_standard_parameters = transformers_standard_parameters.loc['building_gchp_transformer']

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
    ashp_standard_parameters = transformers_standard_parameters.loc['building_ashp_transformer']

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


def create_gas_heating(id, building_type, standard_parameters):

    if building_type == "RES":
        bus = 'building_res_gas_bus'
    else:
        bus = 'building_com_gas_bus'
    # building gas bus
    create_standard_parameter_bus(label=str(id) + "_gas_bus",
                                  bus_type=bus,
                                  standard_parameters=standard_parameters)

    # define individual gas_heating_parameters
    gas_heating_house_specific_dict = \
        {'label': str(id) + '_gasheating_transformer',
         'comment': 'automatically_created',
         'input': str(id) + '_gas_bus',
         'output': str(id) + '_heat_bus',
         'output2': 'None'}

    create_standard_parameter_transformer(specific_param=gas_heating_house_specific_dict,
                                          standard_parameters=standard_parameters,
                                          standard_param_name='building_gasheating_transformer')


def create_electric_heating(id, standard_parameters):
    # # building gas bus
    # create_standard_parameter_bus(label=str(id) + "_gas_bus",
    #                               bus_type='building_gas_bus',
    #                               standard_parameters=standard_parameters)

    # gas heating transformer
    #gas_heating_standard_parameters = standard_parameters.parse('transformers')

    transformers_standard_parameters = standard_parameters.parse('transformers')
    transformers_standard_parameters.set_index('comment', inplace=True)
    electric_heating_standard_parameters = transformers_standard_parameters.loc[
        'building_electricheating_transformer']


    # define individual electric_heating_parameters
    electric_heating_house_specific_dict = \
        {'label': str(id) + '_electricheating_transformer',
         'comment': 'automatically_created',
         'input': str(id) + '_electricity_bus',
         'output': str(id) + '_heat_bus',
         'output2': 'None'}

    # read the electricheating standards from standard_parameters.xlsx and append
    # them to the  electric_heating_house_specific_dict
    electric_heating_standard_keys = electric_heating_standard_parameters.keys().tolist()
    for i in range(len(electric_heating_standard_keys)):
        electric_heating_house_specific_dict[electric_heating_standard_keys[i]] = \
            electric_heating_standard_parameters[electric_heating_standard_keys[i]]#[0]

    # produce a pandas series out of the dict above due to easier appending
    electric_heating_series = pd.Series(electric_heating_house_specific_dict)
    sheets["transformers"] = \
        sheets["transformers"] \
            .append(electric_heating_series, ignore_index=True)

def create_battery(id, standard_parameters, storage_type: str):
    """
        todo docstring
    """
    battery_house_specific_dict = {'label': str(id) + '_battery_storage',
                                   'comment': 'automatically_created',
                                   'bus': str(id) + '_electricity_bus'}

    create_standard_parameter_storage(specific_param=battery_house_specific_dict,
                                      standard_parameters=standard_parameters,
                                      standard_param_name=storage_type + '_battery_storage')

def create_thermal_storage(id, standard_parameters, storage_type: str):
    """
        todo docstring
    """
    thermal_storage_house_specific_dict = \
        {'label': str(id) + '_thermal_storage',
         'comment': 'automatically_created',
         'bus': str(id) + '_heat_bus'}

    create_standard_parameter_storage(specific_param=thermal_storage_house_specific_dict,
                                      standard_parameters=standard_parameters,
                                      standard_param_name=storage_type + '_thermal_storage')
    
def create_building_insulation(id, standard_parameters, yoc, area_window,
                               area_wall, area_roof, roof_type):
    standard_parameters = \
        standard_parameters.parse('insulation')
    standard_parameters.set_index(
            "year of construction", inplace=True)
    if int(yoc) <= 1918:  # TODO
        yoc = "<1918"
    u_value_roof = standard_parameters.loc[yoc]["roof"]
    u_value_outer_wall = standard_parameters.loc[yoc]["outer wall"]
    u_value_window = standard_parameters.loc[yoc]["window"]
    if area_window:
        window_dict = {'label': str(id) + "_window",
                       'comment': 'automatically_created',
                       'active': 1,
                       'sink': str(id) + "_heat_demand",
                       'temperature indoor': 20,
                       'heat limit temperature': 15,
                       'U-value old': u_value_window,
                       'U-value new': 0.8, # todo discuss
                       'area': area_window,
                       'periodical costs': 21.9}
        window_series = pd.Series(window_dict)
        sheets["energetic renovation measures"] = \
            sheets["energetic renovation measures"].append(window_series,
                                                           ignore_index=True)
    if area_wall:
        wall_dict = {'label': str(id) + "_wall",
                     'comment': 'automatically_created',
                     'active': 1,
                     'sink': str(id) + "_heat_demand",
                     'temperature indoor': 20,
                     'heat limit temperature': 15,
                     'U-value old': u_value_outer_wall,
                     'U-value new': 0.22,  # todo discuss
                     'area': area_wall,
                     'periodical costs': 6.08}
        wall_series = pd.Series(wall_dict)
        sheets["energetic renovation measures"] = \
            sheets["energetic renovation measures"].append(wall_series,
                                                           ignore_index=True)
    if area_roof:
        if roof_type == "flachdach":
            u_value_new = 0.21
            periodical_costs = 7.14
        else:
            u_value_new = 0.35
            periodical_costs = 9.35
        roof_dict = {'label': str(id) + "_roof",
                     'comment': 'automatically_created',
                     'active': 1,
                     'sink': str(id) + "_heat_demand",
                     'temperature indoor': 20,
                     'heat limit temperature': 15,
                     'U-value old': u_value_roof,
                     'U-value new': u_value_new,  # todo discuss
                     'area': area_roof,
                     'periodical costs': periodical_costs}
        roof_series = pd.Series(roof_dict)
        sheets["energetic renovation measures"] = \
            sheets["energetic renovation measures"].append(roof_series,
                                                           ignore_index=True)
    
    
def clustering_method(tool, standard_parameters):
    # TODO differntiating com and res elec bus and gas bus with its components
    print(sheets["buses"])
    cluster_ids = {}
    for i, j in tool.iterrows():
        if j["active"]:
            if j["cluster ID"] in cluster_ids:
                cluster_ids[j["cluster ID"]].append((j['label'], j['parcel']))
            else:
                cluster_ids.update({j["cluster ID"]: [(j['label'], j['parcel'])]})
    
    buses = sheets["buses"].copy()
    buses = buses.drop(index=0)
    for i, j in buses.iterrows():
        if "gas" in j["label"] and not "central" in j["label"]:
            sheets["buses"] = sheets["buses"].drop(index=i)
        if "electricity" in j["label"] and not "central" in j["label"]:
            sheets["buses"] = sheets["buses"].drop(index=i)
        if "hp_elec" in j["label"] and not "swhp_elec" in j["label"]:
            sheets["buses"] = sheets["buses"].drop(index=i)
    heat_buses_gchps = []

    for cluster in cluster_ids:
        if cluster_ids[cluster]:
            # house electricity bus
            create_standard_parameter_bus(
                label=str(cluster) + "_electricity_bus",
                bus_type='building_res_electricity_bus',
                standard_parameters=standard_parameters)
            com_demand = 0
            res_demand = 0
            sinks = sheets["sinks"].copy()
            sinks = sinks.drop(index=0)
            transformer = sheets["transformers"].copy()
            transformer = transformer.drop(index=0)
            storages = sheets["storages"].copy()
            storages = storages.drop(index=0)
            links = sheets["links"].copy()
            links = links.drop(index=0)
            sources = sheets["sources"].copy()
            sources = sources.drop(index=0)
            efficiency = 0
            gasheating_counter = 0
            periodical_costs = 0
            variable_constraint_costs = 0
            efficiency_el = 0
            electricheating_counter = 0
            periodical_costs_el = 0
            variable_constraint_costs_el = 0
            efficiency_ashp = 0
            efficiency_ashp2 = 0
            ashp_counter = 0
            periodical_costs_ashp = 0
            variable_constraint_costs_ashp = 0
            efficiency_gchp = 0
            efficiency_gchp2 = 0
            gchp_counter = 0
            periodical_costs_gchp = 0
            variable_constraint_costs_gchp = 0
            maxinvest_battery = 0
            maxinvest_thermal = 0
            periodical_costs_battery = 0
            periodical_costs_thermal = 0
            periodical_constr_costs_battery = 0
            periodical_constr_costs_thermal = 0
            battery_counter = 0
            thermal_counter = 0
            variable_output_costs_thermal = 0
            heat_buses = []
            
            for building in cluster_ids[cluster]:
                for i, j in sinks.iterrows():
                    if str(building[0]) in j["label"] \
                            and "electricity" in j["label"]:
                        if j["load profile"] == "h0":
                            res_demand += j["annual demand"]
                            sheets["sinks"] = sheets["sinks"].drop(index=i)
                        else:
                            com_demand += j["annual demand"]
                            sheets["sinks"] = sheets["sinks"].drop(index=i)
                    elif str(building[0]) in j["label"] \
                            and "heat" in j["label"]:
                        heat_buses.append((cluster, j["input"]))
                
                for i, j in transformer.iterrows():
                    if str(building[0]) in j["label"] \
                            and "gasheating" in j["label"]:
                        efficiency += j["efficiency"]
                        gasheating_counter += 1
                        periodical_costs += j["periodical costs"]
                        variable_constraint_costs += \
                            j["variable output constraint costs"]
                        sheets["transformers"] = \
                            sheets["transformers"].drop(index=i)
                    if str(building[0]) in j["label"] \
                            and "electric" in j["label"]:
                        efficiency_el += j["efficiency"]
                        electricheating_counter += 1
                        periodical_costs_el += j["periodical costs"]
                        variable_constraint_costs_el += \
                            j["variable output constraint costs"]
                        sheets["transformers"] = \
                            sheets["transformers"].drop(index=i)
                    if str(building[0]) in j["label"] \
                            and "ashp" in j["label"]:
                        efficiency_ashp += j["efficiency"]
                        efficiency_ashp2 += j["efficiency2"]
                        ashp_counter += 1
                        periodical_costs_ashp += j["periodical costs"]
                        variable_constraint_costs_ashp += \
                            j["variable output constraint costs"]
                        sheets["transformers"] = \
                            sheets["transformers"].drop(index=i)
                    if str(building[1]) != "0":
                        if str(building[1])[-9:] in j["label"] \
                                and "gchp" in j["label"] \
                                and i in sheets["transformers"].index:
                            heat_buses_gchps.append(str(building[1])[-9:])
                            efficiency_gchp += j["efficiency"]
                            efficiency_gchp2 += j["efficiency2"]
                            gchp_counter += 1
                            periodical_costs_gchp += j["periodical costs"]
                            variable_constraint_costs_gchp += \
                                j["variable output constraint costs"]
                            sheets["transformers"] = \
                                sheets["transformers"].drop(index=i)
                        
                for i, j in storages.iterrows():
                    if str(building[0]) in j["label"] \
                            and "battery" in j["label"]:
                        maxinvest_battery += j["max. investment capacity"]
                        periodical_costs_battery += j["periodical costs"]
                        periodical_constr_costs_battery \
                            += j["periodical constraint costs"]
                        battery_counter += 1
                        sheets["storages"] = sheets["storages"].drop(
                            index=i)
                    if str(building[0]) in j["label"] \
                            and "thermal" in j["label"]:
                        maxinvest_thermal += j["max. investment capacity"]
                        periodical_costs_thermal += j["periodical costs"]
                        periodical_constr_costs_thermal \
                            += j["periodical constraint costs"]
                        variable_output_costs_thermal += j["variable output costs"]
                        thermal_counter += 1
                        sheets["storages"] = sheets["storages"].drop(
                            index=i)
            
                for i, j in links.iterrows():
                    if str(building[0]) in j["bus2"] and \
                            "electricity" in j["bus2"]:
                        sheets["links"]['bus2'] = \
                            sheets["links"]['bus2'].replace(
                                    [str(building[0]) + "_electricity_bus"],
                                    str(cluster) + "_electricity_bus")
                    if str(building[0]) in j["bus2"] and \
                            "hp_elec" in j["bus2"]:
                        sheets["links"] = sheets["links"].drop(index=i)
                    if str(building[1])[-9:] in j["bus2"] and \
                            "hp_elec" in j["bus2"] \
                            and i in sheets["links"].index:
                        sheets["links"] = sheets["links"].drop(index=i)
                    if str(building[1][-9:]) in j["bus1"] and \
                            "heat" in j["bus1"] and i in sheets["links"].index:
                        sheets["links"] = sheets["links"].drop(index=i)
                    if str(building[0]) in j["bus2"] and \
                            "gas" in j["bus2"]:
                        sheets["links"]['bus2'] = \
                            sheets["links"]['bus2'].replace(
                                [str(building[0]) + "_gas_bus"],
                                str(cluster) + "_gas_bus")
                for i, j in sources.iterrows():
                    if str(building[0]) in str(j["input"]) and \
                            "electricity" in str(j["input"]):
                        sheets["sources"]['input'] = \
                            sheets["sources"]['input'].replace(
                                    [str(building[0]) + "_electricity_bus"],
                                    str(cluster) + "_electricity_bus")
                        
            if res_demand:
                create_standard_parameter_sink("RES_electricity_sink",
                                               str(cluster)
                                               + "_res_electricity_demand",
                                               str(cluster) + "_electricity_bus",
                                               res_demand,
                                               standard_parameters)
            if com_demand:
                create_standard_parameter_sink("COM_electricity_sink",
                                               str(cluster) +
                                               "_com_electricity_demand",
                                               str(cluster) + "_electricity_bus",
                                               com_demand,
                                               standard_parameters)
            # TODO
            if gasheating_counter:
                create_standard_parameter_bus(label=str(cluster) + "_gas_bus",
                                              bus_type='building_res_gas_bus',
                                              standard_parameters=standard_parameters)
        
                # define individual gas_heating_parameters
                gas_heating_house_specific_dict = \
                    {'label': str(cluster) + '_gasheating_transformer',
                     'comment': 'automatically_created',
                     'input': str(cluster) + '_gas_bus',
                     'output': str(cluster) + '_heat_bus',
                     'output2': 'None'}
                transformers_standard_parameters = standard_parameters.parse(
                    'transformers')
                transformers_standard_parameters.set_index('comment', inplace=True)
                standard_param = transformers_standard_parameters.loc[
                    'building_gasheating_transformer']
        
                standard_keys = standard_param.keys().tolist()
                for i in range(len(standard_keys)):
                    gas_heating_house_specific_dict[standard_keys[i]] = \
                        standard_param[standard_keys[i]]
                gas_heating_house_specific_dict["efficiency"] = \
                    efficiency/gasheating_counter
                gas_heating_house_specific_dict["periodical costs"] = \
                    periodical_costs / gasheating_counter
                gas_heating_house_specific_dict["variable output constraint costs"] = \
                    variable_constraint_costs / gasheating_counter
                # produce a pandas series out of the dict above due to easier appending
                transformer_series = pd.Series(gas_heating_house_specific_dict)
                sheets["transformers"] = \
                    sheets["transformers"].append(transformer_series,
                                                  ignore_index=True)
            if electricheating_counter:
                # define individual gas_heating_parameters
                electricheating_heating_house_specific_dict = \
                    {'label': str(cluster) + '_electricheating_transformer',
                     'comment': 'automatically_created',
                     'input': str(cluster) + '_electricity_bus',
                     'output': str(cluster) + '_heat_bus',
                     'output2': 'None'}
                transformers_standard_parameters = standard_parameters.parse(
                        'transformers')
                transformers_standard_parameters.set_index('comment', inplace=True)
                standard_param = transformers_standard_parameters.loc[
                    'building_electricheating_transformer']
        
                standard_keys = standard_param.keys().tolist()
                for i in range(len(standard_keys)):
                    electricheating_heating_house_specific_dict[standard_keys[i]] = \
                        standard_param[standard_keys[i]]
                electricheating_heating_house_specific_dict["efficiency"] = \
                    efficiency_el / electricheating_counter
                electricheating_heating_house_specific_dict["periodical costs"] = \
                    periodical_costs_el / electricheating_counter
                electricheating_heating_house_specific_dict[
                    "variable output constraint costs"] = \
                    variable_constraint_costs_el / electricheating_counter
                # produce a pandas series out of the dict above due to easier
                # appending
                transformer_series = pd.Series(electricheating_heating_house_specific_dict)
                sheets["transformers"] = \
                    sheets["transformers"].append(transformer_series,
                                                  ignore_index=True)
            if ashp_counter:
                # building hp electricity bus
                create_standard_parameter_bus(label=str(cluster) + "_hp_elec_bus",
                                              bus_type='building_hp_electricity_bus',
                                              standard_parameters=standard_parameters)
                # electricity link from building electricity bus to hp elec bus
                create_standard_parameter_link(
                        label=str(cluster) + "_gchp_building_link",
                        bus_1=str(cluster) + "_electricity_bus",
                        bus_2=str(cluster) + "_hp_elec_bus",
                        link_type="building_hp_elec_link",
                        standard_parameters=standard_parameters)
                # define individual gas_heating_parameters
                ashp_house_specific_dict = {'label': str(cluster) + '_ashp_transformer',
                                            'comment': 'automatically_created',
                                            'input': str(cluster) + '_hp_elec_bus',
                                            'output': str(cluster) + '_heat_bus',
                                            'output2': 'None',
                                            'existing capacity': 0,
                                            'min. investment capacity': 0}
    
                transformers_standard_parameters = standard_parameters.parse(
                        'transformers')
                transformers_standard_parameters.set_index('comment', inplace=True)
                standard_param = transformers_standard_parameters.loc[
                    'building_ashp_transformer']
        
                standard_keys = standard_param.keys().tolist()
                for i in range(len(standard_keys)):
                    ashp_house_specific_dict[standard_keys[
                        i]] = \
                        standard_param[standard_keys[i]]
                ashp_house_specific_dict["efficiency"] = \
                    efficiency_ashp / ashp_counter
                ashp_house_specific_dict["efficiency2"] = \
                    efficiency_ashp2 / ashp_counter
                ashp_house_specific_dict["periodical costs"] = \
                    periodical_costs_ashp / ashp_counter
                ashp_house_specific_dict["max. investment capacity"] = \
                    ashp_counter * ashp_house_specific_dict["max. investment capacity"]
                # produce a pandas series out of the dict above due to easier
                # appending
                transformer_series = pd.Series(
                    ashp_house_specific_dict)
                sheets["transformers"] = \
                    sheets["transformers"].append(transformer_series,
                                                  ignore_index=True)
            
            if gchp_counter:
                # define individual gas_heating_parameters
                gchp_house_specific_dict = {
                    'label': str(cluster) + '_gchp_transformer',
                    'comment': 'automatically_created',
                    'input': str(cluster) + '_hp_elec_bus',
                    'output': str(cluster) + '_heat_bus',
                    'output2': 'None',
                    'existing capacity': 0,
                    'min. investment capacity': 0}
        
                transformers_standard_parameters = standard_parameters.parse(
                        'transformers')
                transformers_standard_parameters.set_index('comment', inplace=True)
                standard_param = transformers_standard_parameters.loc[
                    'building_gchp_transformer']
        
                standard_keys = standard_param.keys().tolist()
                for i in range(len(standard_keys)):
                    gchp_house_specific_dict[standard_keys[
                        i]] = \
                        standard_param[standard_keys[i]]
                gchp_house_specific_dict["efficiency"] = \
                    efficiency_gchp / gchp_counter
                gchp_house_specific_dict["efficiency2"] = \
                    efficiency_gchp2 / gchp_counter
                gchp_house_specific_dict["periodical costs"] = \
                    periodical_costs_gchp / gchp_counter
                gchp_house_specific_dict["max. investment capacity"] = \
                    gchp_counter * gchp_house_specific_dict[
                        "max. investment capacity"]
                # produce a pandas series out of the dict above due to easier
                # appending
                transformer_series = pd.Series(
                        gchp_house_specific_dict)
                sheets["transformers"] = \
                    sheets["transformers"].append(transformer_series,
                                                  ignore_index=True)
                
            if battery_counter:
                # read the standards from standard_param and append
                # them to the dict
                storage_standard_parameters = standard_parameters.parse('storages')
                storage_standard_parameters.set_index('comment', inplace=True)
                standard_param = storage_standard_parameters.loc[
                    'building_battery_storage']
                
                specific_param = {'label': str(cluster) + '_battery_storage',
                                  'comment': 'automatically_created',
                                  'bus': str(cluster) + '_electricity_bus'}
                
                standard_keys = standard_param.keys().tolist()
                for i in range(len(standard_keys)):
                    specific_param[standard_keys[i]] = \
                        standard_param[standard_keys[i]]
                
                specific_param["max. investment capacity"] = maxinvest_battery
                specific_param["periodical costs"] = \
                    periodical_costs_battery / battery_counter
                specific_param["periodical constraint costs"] = \
                    periodical_constr_costs_battery / battery_counter
        
                # produce a pandas series out of the dict above due to easier
                # appending
                storage_series = pd.Series(specific_param)
                sheets["storages"] = \
                    sheets["storages"].append(storage_series,
                                              ignore_index=True)
                
            if thermal_counter:
                # read the standards from standard_param and append
                # them to the dict
                storage_standard_parameters = standard_parameters.parse('storages')
                storage_standard_parameters.set_index('comment', inplace=True)
                standard_param = storage_standard_parameters.loc[
                    'building_thermal_storage']
        
                specific_param = {'label': str(cluster) + '_thermal_storage',
                                  'comment': 'automatically_created',
                                  'bus': str(cluster) + '_heat_bus'}
        
                standard_keys = standard_param.keys().tolist()
                for i in range(len(standard_keys)):
                    specific_param[standard_keys[i]] = \
                        standard_param[standard_keys[i]]
        
                specific_param["max. investment capacity"] = maxinvest_thermal
                specific_param["periodical costs"] = \
                    periodical_costs_thermal / thermal_counter
                specific_param["periodical constraint costs"] = \
                    periodical_constr_costs_thermal / thermal_counter
                specific_param["variable output costs"] = \
                    variable_output_costs_thermal / thermal_counter
        
                # produce a pandas series out of the dict above due to easier
                # appending
                storage_series = pd.Series(specific_param)
                sheets["storages"] = \
                    sheets["storages"].append(storage_series,
                                              ignore_index=True)
            
            if gasheating_counter or electricheating_counter or ashp_counter \
                    or gchp_counter:
                # building hp electricity bus
                create_standard_parameter_bus(
                    label=str(cluster) + "_heat_bus",
                    bus_type='building_heat_bus',
                    standard_parameters=standard_parameters)
                
            for i in heat_buses:
                create_standard_parameter_link(
                        label=str(i[0]) +"_"+ str(i[1])  + "_heat_building_link",
                        bus_1=str(i[0]) + "_heat_bus",
                        bus_2=str(i[1]),
                        link_type="building_hp_elec_link",
                        standard_parameters=standard_parameters)
    buses = sheets["buses"].copy()
    buses = buses.drop(index=0)
    print(buses)
    for i, j in buses.iterrows():
        if str(j["label"][:9]) in heat_buses_gchps:
            sheets["buses"] = sheets["buses"].drop(index=i)
            
            
def urban_district_upscaling_pre_processing(pre_scenario: str,
                                            standard_parameter_path: str,
                                            output_scenario: str,
                                            plain_sheet: str):
    # todo: docstrings

    print('Creating scenario sheet...')
    clustering = True
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

        sheets[sheet] = sheets[sheet].append(pd.Series(data=units1),
                                             ignore_index=True)

    # import the sheet which is filled by the user
    xls = pd.ExcelFile(pre_scenario)
    tool = xls.parse("tool")
    parcel = xls.parse("parcel")
    central = xls.parse("central")
    central_comp(central, standard_parameters)
    # set variable for central heating if activated to decide rather a house
    # can be connected to the central heat network or not
    central_heating_network = False
    central_electricity_network = False

    for i, j in central.iterrows():
        if j['heat_link'] in ['Yes', 'yes', 1]:
            central_heating_network = True
        if j['electricity_bus'] in ['Yes', 'yes', 1]:
            central_electricity_network = True
        if j['power_to_gas'] in ['Yes', 'yes', 1]:
            p2g_link = True
        else:
            p2g_link = False
    
    # create GCHPs parcel wise
    gchps = {}
    for i, j in parcel.iterrows():
        for h, k in tool.iterrows():
            if k["active"]:
                if k["gchp"] not in ["No", "no", 0]:
                    if j['ID parcel'] == k["parcel"]:
                        gchps.update({j['ID parcel'][-9:]:
                                          j['gchp area (m²)']})
                
    for gchp in gchps:
        create_gchp(id=gchp, area=gchps[gchp],
                    standard_parameters=standard_parameters)
        create_standard_parameter_bus(label=gchp + "_hp_elec_bus",
                                      bus_type="building_hp_electricity_bus",
                                      standard_parameters=standard_parameters)
        create_standard_parameter_bus(label=gchp + "_heat_bus",
                                      bus_type="building_heat_bus",
                                      standard_parameters=standard_parameters)

    for i, j in tool.iterrows():
        if j["active"]:
            # foreach building the three necessary buses will be created
            pv_bool = False
            for i in range(1, 29):
                if j['st or pv %1d' % i] == "pv&st":
                    pv_bool = True
            create_buses(j['label'],
                         pv_bool,
                         j["building type"],
                         True if (j['parcel'] != 0
                                  and j["gchp"] not in ["No", "no", 0])
                                 or j['ashp'] not in ["No", "no", 0]
                         else False,
                         True if ((j['central heat'] == 'yes'
                                  or j['central heat'] == 'Yes'
                                  or j['central heat'] == 1)
                                  and
                                  central_heating_network) else False,
                         central_electricity_network,
                         True if j['parcel'] != 0 else False,
                         gchp_heat_bus=(j['parcel'][-9:] + "_heat_bus")
                         if (j['parcel'] != 0 and j['parcel'][-9:] in gchps)
                         else None,
                         gchp_elec_bus=(j['parcel'][-9:] + "_hp_elec_bus")
                         if (j['parcel'] != 0 and j['parcel'][-9:] in gchps)
                         else None,
                         standard_parameters=standard_parameters)
            
            create_sinks(id=j['label'],
                         building_type=j['building type'],
                         units=j['units'],
                         occupants=j['occupants per unit'],
                         yoc=j['year of construction'],
                         area=j['living space'] * j['floors'],
                         standard_parameters=standard_parameters,
                         latitude=j["latitude"],
                         longitude=j["longitude"])
            
            create_building_insulation(id=j['label'],
                                       standard_parameters=standard_parameters,
                                       yoc=j['year of construction'],
                                       area_window=j["windows"],
                                       area_wall=j["walls_wo_windows"],
                                       area_roof=j["roof area"],
                                       roof_type=j["rooftype"])
    
            # Define PV Standard-Parameters
            sources_standard_parameters = standard_parameters.parse('sources')
            sources_standard_parameters.set_index('comment', inplace=True)
            pv_standard_parameters = \
                sources_standard_parameters.loc['fixed photovoltaic source']
    
            # Define solar thermal Standard-Parameters
            solarthermal_standard_parameters = \
                sources_standard_parameters.loc['solar_thermal_collector']
    
            # create pv-sources and solar thermal-sources including area
            # competition
            for i in range(1, 29):
                if j['roof area (m²) %1d' % i]:
                    plant_id = str(i)
                    if j['st or pv %1d' % i] == "pv&st":
                        create_pv_source(building_id=j['label'],
                                         plant_id=plant_id,
                                         azimuth=j['azimuth (°) %1d' % i],
                                         tilt=j['surface tilt (°) %1d' % i],
                                         area=j['roof area (m²) %1d' % i],
                                         latitude=j['latitude'],
                                         longitude=j['longitude'],
                                         pv_standard_parameters=pv_standard_parameters)
                    if (j['st or pv %1d' % i] == "st"
                            or j['st or pv %1d' % i] == "pv&st")\
                            and j["building type"] != "0":
                        create_solarthermal_source(building_id=j['label'],
                                         plant_id=plant_id,
                                         azimuth=j['azimuth (°) %1d' % i],
                                         tilt=j['surface tilt (°) %1d' % i],
                                         area=j['roof area (m²) %1d' % i],
                                         latitude=j['latitude'],
                                         longitude=j['longitude'],
                                         solarthermal_standard_parameters=solarthermal_standard_parameters)
                    if j['st or pv %1d' % i] == "pv&st"\
                            and j["building type"] != "0":
                        create_competition_constraint(component1=
                                                      j['label'] + '_'
                                                      + plant_id + '_pv_source',
                                                      factor1=1/pv_standard_parameters['Capacity per Area (kW/m2)'],
                                                      component2=
                                                      j['label'] + '_'
                                                      + plant_id + '_solarthermal_source',
                                                      factor2=1/solarthermal_standard_parameters['Capacity per Area (kW/m2)'],
                                                      limit=j['roof area (m²) %1d' % i])
    
            # creates heat-pumps
            if j['ashp'] in ['Yes', 'yes', 1]:
                create_ashp(id=j['label'],
                            standard_parameters=standard_parameters)
    
            # creates gasheating-system
            if j['gas heating'] in ['Yes', 'yes', 1]:
                create_gas_heating(id=j['label'],
                                   building_type=j['building type'],
                                   standard_parameters=standard_parameters)
    
                # natural gas connection link to p2g-ng-bus
                if p2g_link == True:
                    create_standard_parameter_link(label='central_naturalgas_' + j['label'] + 'link',
                                                   bus_1='central_naturalgas_bus',
                                                   bus_2=j['label']+'_gas_bus',
                                                   link_type='central_naturalgas_building_link',
                                                   standard_parameters=standard_parameters)
    
            # creates electric heating-system
            if j['electric heating'] in ['yes', 'Yes', 1]:
                create_electric_heating(id=j['label'],
                                        standard_parameters=standard_parameters)
    
            # battery storage
            if j['battery storage'] in ['Yes', 'yes', 1]:
                create_battery(id=j['label'],
                               standard_parameters=standard_parameters, storage_type="building")
            if j['thermal storage'] in ['Yes', 'yes', 1]:
                create_thermal_storage(id=j['label'],
                                       standard_parameters=standard_parameters,
                                       storage_type="building")
    
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
    
    if clustering:
        clustering_method(tool, standard_parameters)
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
    urban_district_upscaling_pre_processing(pre_scenario=os.path.dirname(__file__) + r"/pre_scenario_struenkede_v2.xlsx",
                                            standard_parameter_path=os.path.dirname(__file__)
                                                                    + r"/standard_parameters.xlsx",
                                            output_scenario=os.path.dirname(__file__) + r"/test_scenario.xlsx",
                                            plain_sheet=os.path.dirname(__file__) + r'/plain_scenario.xlsx')
