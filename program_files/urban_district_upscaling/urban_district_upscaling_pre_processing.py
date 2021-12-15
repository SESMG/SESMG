import xlsxwriter
import pandas as pd
import os


def copy_standard_parameter_sheet(standard_parameters, sheet_tbc: str):
    """
        use to create an intern copy of the standard_parameters excel
        sheet

        :param standard_parameters: pandas Dataframe holding the
               information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
        :param sheet_tbc: excel sheet name which has to be copied(_tbc)
        :type sheet_tbc: str
    """

    sheets[sheet_tbc] = standard_parameters.parse(sheet_tbc)


def create_standard_parameter_bus(label: str, bus_type: str,
                                  standard_parameters, lat=None, lon=None,
                                  dh=None):
    """
        creates a bus with standard_parameters, based on the standard
        parameters given in the "standard_parameters" dataset and adds
        it to the "sheets"-output dataset.

        :param label: label, the created bus will be given
        :type label: str
        :param bus_type: defines, which set of standard param. will be
                         given to the dict
        :type bus_type: str
        :param standard_parameters: pandas Dataframe holding the
               information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
        :param lat: latitude of the given bus used to connect a producer
                    bus to district heating network
        :type lat: float
        :param lon: longitude of the given bus used to connect a producer
                    bus to district heating network
        :type lon: float
        :param dh: string which can be "dh-system" (for searching the
                   nearest point on heat network or "street-1/2" if the
                   bus has to be connected to a specific intersection
        :type dh: str
    """

    # define individual values
    bus_dict = {'label': label}
    # extracts the bus specific standard values from the
    # standard_parameters dataset
    bus_standard_parameters = \
        standard_parameters.parse('buses', index_col='bus_type').loc[bus_type]
    bus_standard_keys = bus_standard_parameters.keys().tolist()
    # adapt standard values
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
        :param standard_parameters: pandas Dataframe holding the
               information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
    """
    link_house_specific_dict = {'label': label,
                                'bus1': bus_1,
                                'bus2': bus_2}

    link_standard_parameters = \
        standard_parameters.parse('links',
                                  index_col='link_type').loc[link_type]
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
                                   standard_parameters, dh: int, lat=None,
                                   lon=None):
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
        :param annual_demand: #todo formula
        :type annual_demand: int
        :param dh: boolean rather the dh-connection is active or not
        :param dh: int
        :param standard_parameters: pandas Dataframe holding the
               information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
        :param lat: latitude of the given heat sink used to connect a
                    consumer bus to district heating network
        :type lat: float
        :param lon: longitude of the given heat sink used to connect a
                    consumer bus to district heating network
        :type lon: float
    """
    sink_standard_parameters = \
        standard_parameters.parse('sinks',
                                  index_col="sink_type").loc[sink_type]
    sink_dict = {'label': label,
                 'input': sink_input,
                 'annual demand': annual_demand,
                 'district heating': dh,
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


def create_standard_parameter_transformer(specific_param: dict,
                                          standard_parameters,
                                          standard_param_name):
    """
        TODO DOCSTRING TEXT

        :param specific_param: dictionary holding the transformer specific
                               parameters (e.g. electrolysis specific...)
        :type specific_param: dict
        :param standard_parameters: pandas Dataframe holding the
                   information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
        :param standard_param_name: string defining the transformer type
                                    (e.g. central_electrolysis_transformer,...)
                                    to locate the right standard parameters
        :type standard_param_name: string
    """

    # read the standards from standard_param and append
    # them to the dict
    transformers_standard_parameters = \
        standard_parameters.parse('transformers')
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


def create_standard_parameter_storage(specific_param: dict,
                                      standard_parameters,
                                      standard_param_name):
    """

        :param specific_param: dictionary holding the storage specific
                               parameters (e.g. ng_storage specific, ...)
        :type specific_param: dict
        :param standard_parameters: pandas Dataframe holding the
                   information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
        :param standard_param_name: string defining the storage type
                                    (e.g. central_naturalgas_storage,...)
                                    to locate the right standard parameters
        :type standard_param_name: string
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
        TODO DOCSTRING TEXT

        :param central: pandas Dataframe holding the information from the
                        prescenario file "central" sheet
        :type central: pd.Dataframe
        :param standard_parameters: pandas Dataframe holding the
                   information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
    """
    for i, j in central.iterrows():

        # create central electricity bus
        if j['electricity_bus'] in ['Yes', 'yes', 1]:
            create_standard_parameter_bus(
                label='central_electricity_bus',
                bus_type="central_electricity_bus",
                standard_parameters=standard_parameters)

        # central natural gas
        if j['naturalgas_chp'] in ['yes', 'Yes', 1] \
                or j["biogas_chp"] in ['yes', 'Yes', 1] \
                or j['swhp_transformer'] in ['yes', 'Yes', 1] \
                or j['biomass_plant'] in ['yes', 'Yes', 1] \
                or j['naturalgas_heating_plant'] in ['yes', 'Yes', 1] \
                or j['thermal_storage'] in ['yes', 'Yes', 1]:
            # TODO only one central input implemented yet
            create_standard_parameter_bus(
                label='central_heat_input_bus',
                bus_type="central_heat_input_bus",
                standard_parameters=standard_parameters,
                dh="dh-system",
                lat=j["lat.-chp"],
                lon=j["lon.-chp"])
            if j['naturalgas_chp'] in ['yes', 'Yes', 1]:
                create_central_chp(gastype='naturalgas',
                                   standard_parameters=standard_parameters)
            if j['biogas_chp'] in ['yes', 'Yes', 1]:
                create_central_chp(gastype='biogas',
                                   standard_parameters=standard_parameters)
            # central natural gas heating plant
            if j['naturalgas_heating_plant'] in ['yes', 'Yes', 1]:
                create_central_gas_heating_transformer(
                    gastype='naturalgas',
                    standard_parameters=standard_parameters)
            # central swhp
            central_heatpump_indicator = 0
            if j['swhp_transformer'] in ['yes', 'Yes', 1]:
                create_central_heatpump(
                    standard_parameters=standard_parameters,
                    specification='swhp',
                    create_bus=True if central_heatpump_indicator == 0 else
                    False)
                central_heatpump_indicator += 1
            # central ashp
            if j['ashp_transformer'] in ['yes', 'Yes', 1]:
                create_central_heatpump(
                    standard_parameters=standard_parameters,
                    specification='ashp',
                    create_bus=True if central_heatpump_indicator == 0 else
                    False)
                central_heatpump_indicator += 1
            # central biomass plant
            if j['biomass_plant'] in ['yes', 'Yes', 1]:
                create_central_biomass_plant(
                    standard_parameters=standard_parameters)
            if j['thermal_storage'] in ['yes', 'Yes', 1]:
                create_thermal_storage(building_id="central",
                                       standard_parameters=standard_parameters,
                                       storage_type="central",
                                       bus="central_heat_input_bus")
        # power to gas system
        if j['power_to_gas'] in ['yes', 'Yes', 1]:
            create_power_to_gas_system(standard_parameters=standard_parameters)

        if j['battery_storage'] in ['yes', 'Yes', 1]:
            create_battery(building_id="central",
                           standard_parameters=standard_parameters,
                           storage_type="central")


def create_power_to_gas_system(standard_parameters):
    """
        TODO DOCSTRING TEXT

        :param standard_parameters: pandas Dataframe holding the
                   information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
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

    create_standard_parameter_transformer(
        specific_param=electrolysis_transformer_param,
        standard_parameters=standard_parameters,
        standard_param_name='central_electrolysis_transformer')

    # methanization transformer
    methanization_transformer_param = \
        {'label': 'central_methanization_transformer',
         'comment': 'automatically_created',
         'input': 'central_h2_bus',
         'output': 'central_naturalgas_bus',
         'output2': 'None'}

    create_standard_parameter_transformer(
        specific_param=methanization_transformer_param,
        standard_parameters=standard_parameters,
        standard_param_name='central_methanization_transformer')

    # fuel cell transformer
    fuelcell_transformer_param = \
        {'label': 'central_fuelcell_transformer',
         'comment': 'automatically_created',
         'input': 'central_h2_bus',
         'output': 'central_electricity_bus',
         'output2': 'central_heat_input_bus'}

    create_standard_parameter_transformer(
        specific_param=fuelcell_transformer_param,
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

    create_standard_parameter_storage(
        specific_param=ng_storage_param,
        standard_parameters=standard_parameters,
        standard_param_name='central_naturalgas_storage')

    # link to chp_naturalgas_bus
    create_standard_parameter_link(
        label='central_naturalgas_chp_naturalgas_link',
        bus_1='central_naturalgas_bus',
        bus_2='central_chp_naturalgas_bus',
        link_type='central_naturalgas_chp_link',
        standard_parameters=standard_parameters)


def create_central_biomass_plant(standard_parameters):
    """
        TODO DOCSTRING TEXT

        :param standard_parameters: pandas Dataframe holding the
                   information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
    """
    # biomass bus
    create_standard_parameter_bus(label="central_biomass_bus",
                                  bus_type="central_biomass_bus",
                                  standard_parameters=standard_parameters)

    # biomass transformer
    transformers_standard_parameters = \
        standard_parameters.parse('transformers')
    transformers_standard_parameters.set_index('comment', inplace=True)
    biomass_standard_parameters = \
        transformers_standard_parameters.loc['central_biomass_transformer']
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


def create_central_heatpump(standard_parameters, specification, create_bus):
    """
        TODO DOCSTRING
        :param standard_parameters: pandas Dataframe holding the
                                    information imported from the
                                    standard parameter file
        :param specification: string giving the information which type
                              of heatpump shall be added.
        :param create_bus: indicates whether a central heatpump
                           electricity bus and further parameters shall
                           be created or not.
        :return:
    """

    if create_bus:
        create_standard_parameter_bus(
            label="central_heatpump_elec_bus",
            bus_type="central_heatpump_electricity_bus",
            standard_parameters=standard_parameters)
        # connection to central electricity bus
        create_standard_parameter_link(
            label="central_heatpump_electricity_link",
            bus_1="central_electricity_bus",
            bus_2="central_heatpump_elec_bus",
            link_type="building_central_building_link",
            standard_parameters=standard_parameters)

    # transformer standard parameters
    transformers_standard_parameters = \
        standard_parameters.parse('transformers')
    transformers_standard_parameters.set_index('comment', inplace=True)

    heatpump_standard_parameters = \
        transformers_standard_parameters.loc[
            'central_' + specification + '_transformer']
    heatpump_central_dict = {
        'label': 'central_' + specification + '_transformer',
        'comment': 'automatically_created',
        'input': "central_heatpump_elec_bus",
        'output': 'central_heat_input_bus',
        'output2': 'None'}

    # read the heatpump standards from standard_parameters.xlsx and append
    # them to the heatpump_central_dict
    heatpump_standard_keys = heatpump_standard_parameters.keys().tolist()
    for i in range(len(heatpump_standard_keys)):
        heatpump_central_dict[heatpump_standard_keys[i]] = \
            heatpump_standard_parameters[heatpump_standard_keys[i]]

    # produce a pandas series out of the dict above due to easier appending
    heatpump_series = pd.Series(heatpump_central_dict)
    sheets["transformers"] = \
        sheets["transformers"].append(heatpump_series, ignore_index=True)


def create_central_gas_heating_transformer(gastype, standard_parameters):
    """
        TODO DOCSTRING TEXT

        :param gastype: string which defines rather naturalgas or biogas
                        is used
        :type gastype: str
        :param standard_parameters: pandas Dataframe holding the
                   information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
    """

    # plant gas bus
    create_standard_parameter_bus(label="central_" + gastype + "_plant_bus",
                                  bus_type="central_chp_naturalgas_bus",
                                  standard_parameters=standard_parameters)

    # connection to central electricity bus
    create_standard_parameter_link(
        label="heating_plant_" + gastype + "_link",
        bus_1="central_" + gastype + "_bus",
        bus_2="central_" + gastype + "_plant_bus",
        link_type="central_naturalgas_building_link",
        standard_parameters=standard_parameters)

    # transformer parameters
    heating_plant_standard_parameters = \
        standard_parameters.parse('transformers')

    heating_plant_dict = \
        {'label': "central_" + gastype + '_heating_plant_transformer',
         'input': "central_" + gastype + "_plant_bus",
         'output': "central_heat_input_bus",
         'output2': 'None'}

    # read the chp standards from standard_parameters.xlsx and append
    # them to the gchp_central_dict
    heating_plant_standard_keys = \
        heating_plant_standard_parameters.keys().tolist()
    for i in range(len(heating_plant_standard_keys)):
        heating_plant_dict[heating_plant_standard_keys[i]] = \
            heating_plant_standard_parameters[
                heating_plant_standard_keys[i]][0]

    # produce a pandas series out of the dict above due to easier appending
    heating_plant_series = pd.Series(heating_plant_dict)
    sheets["transformers"] = sheets["transformers"].append(
        heating_plant_series, ignore_index=True)


def create_central_chp(gastype, standard_parameters):
    """
        TODO DOCSTRING TEXT

        :param gastype: string which defines rather naturalgas or biogas
                        is used
        :type gastype: str
        :param standard_parameters: pandas Dataframe holding the
                   information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
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


def create_buses(building_id: str, pv_bus: bool, building_type: str,
                 hp_elec_bus: bool, central_elec_bus: bool, gchp: bool,
                 standard_parameters, gchp_heat_bus=None, gchp_elec_bus=None):
    """
        todo docstring
        :param building_id: building identification
        :type building_id: str
        :param pv_bus: boolean which defines rather a pv bus is created or not
        :type pv_bus: bool
        :param building_type: defines rather it is a residential or a
                              commercial building
        :type building_type: str
        :param hp_elec_bus: defines rather a heat pump bus and its link
                            is created or not
        :type hp_elec_bus: bool
        :param central_elec_bus: defines rather buildings can be
                                 connected to central elec net or not
        :type central_elec_bus: bool
        :param gchp: defines rather the building can connected to a
                     parcel gchp or not
        :type gchp: bool
        :param standard_parameters: pandas Dataframe holding the
                   information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
        :param gchp_heat_bus:
        :type gchp_heat_bus: str
        :param gchp_elec_bus:
        :type gchp_elec_bus: str

    """
    if building_type == "RES":
        bus = 'building_res_electricity_bus'
    elif building_type == "IND":
        bus = 'building_ind_electricity_bus'
    else:
        bus = 'building_com_electricity_bus'
    if pv_bus or building_type != "0":
        # house electricity bus
        create_standard_parameter_bus(label=(str(building_id)
                                             + "_electricity_bus"),
                                      bus_type=bus,
                                      standard_parameters=standard_parameters)
        if central_elec_bus:
            # link from central elec bus to building electricity bus
            create_standard_parameter_link(
                label=str(building_id) + "central_electricity_link",
                bus_1="central_electricity_bus",
                bus_2=str(building_id) + "_electricity_bus",
                link_type="building_central_building_link",
                standard_parameters=standard_parameters)

    if building_type != "0":
        # house heat bus
        create_standard_parameter_bus(label=str(building_id) + "_heat_bus",
                                      bus_type='building_heat_bus',
                                      standard_parameters=standard_parameters)

    if hp_elec_bus:
        # building hp electricity bus
        create_standard_parameter_bus(label=str(building_id) + "_hp_elec_bus",
                                      bus_type='building_hp_electricity_bus',
                                      standard_parameters=standard_parameters)
        # electricity link from building electricity bus to hp elec bus
        create_standard_parameter_link(
            label=str(building_id) + "_gchp_building_link",
            bus_1=str(building_id) + "_electricity_bus",
            bus_2=str(building_id) + "_hp_elec_bus",
            link_type="building_hp_elec_link",
            standard_parameters=standard_parameters)

        if gchp:
            if gchp_elec_bus is not None:
                create_standard_parameter_link(
                    label=str(building_id) + "_parcel_gchp_elec",
                    bus_1=str(building_id) + "_hp_elec_bus",
                    bus_2=gchp_elec_bus,
                    link_type="building_hp_elec_link",
                    standard_parameters=standard_parameters)
                create_standard_parameter_link(
                    label=str(building_id) + "_parcel_gchp",
                    bus_1=gchp_heat_bus,
                    bus_2=str(building_id) + "_heat_bus",
                    link_type="building_hp_elec_link",
                    standard_parameters=standard_parameters)

    # todo excess constraint costs
    if pv_bus:
        # building pv bus
        create_standard_parameter_bus(label=str(building_id) + "_pv_bus",
                                      bus_type='building_pv_bus',
                                      standard_parameters=standard_parameters)

        # link from pv bus to building electricity bus
        create_standard_parameter_link(
            label=str(building_id) + "pv_" + str(building_id)
                  + "_electricity_link",
            bus_1=str(building_id) + "_pv_bus",
            bus_2=str(building_id) + "_electricity_bus",
            link_type="building_pv_central_link",
            standard_parameters=standard_parameters)
        if central_elec_bus:
            # link from pv bus to central electricity bus
            create_standard_parameter_link(
                label=str(building_id) + "pv_central_electricity_link",
                bus_1=str(building_id) + "_pv_bus",
                bus_2="central_electricity_bus",
                link_type="building_pv_central_link",
                standard_parameters=standard_parameters)


def create_sinks(sink_id: str, building_type: str, units: int,
                 occupants: int, yoc: str, area: int, standard_parameters,
                 latitude, longitude, dh):
    """
        TODO DOCSTRING
    """
    if dh:
        dh_value = 1
    else:
        dh_value = 0
    # electricity demand
    if building_type not in ['None', '0', 0]:
        # residential parameters
        demand_el = 0
        sinks_standard_param = standard_parameters.parse('sinks')
        sinks_standard_param.set_index(
            "sink_type", inplace=True)
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
                demand_el = \
                    (electricity_demand_residential[5][0]) / 5 * occupants
                demand_el = demand_el * units
        else:
            # commercial parameters
            if "COM" in building_type:
                electricity_demand_standard_param = \
                    standard_parameters.parse('ComElecDemand')
            # industrial parameters
            elif "IND" in building_type:
                electricity_demand_standard_param = \
                    standard_parameters.parse('IndElecDemand')
            else:
                raise ValueError(
                    "building type: " + building_type + "not allowed")
            electricity_demand_standard_param.set_index(
                "commercial type", inplace=True)
            demand_el = electricity_demand_standard_param \
                .loc[building_type]['specific demand (kWh/(sqm a))']
            net_floor_area = area * sinks_standard_param \
                .loc[building_type + "_electricity_sink"][
                'net_floor_area / area']
            demand_el = demand_el * net_floor_area

        create_standard_parameter_sink(
            sink_type=building_type + "_electricity_sink",
            label=str(sink_id) + "_electricity_demand",
            sink_input=str(sink_id) + "_electricity_bus",
            annual_demand=demand_el,
            standard_parameters=standard_parameters,
            dh=0)

        # heat demand
        if "RES" in building_type:
            # read standard values from standard_parameter-dataset
            heat_demand_standard_param = \
                standard_parameters.parse('ResHeatDemand')
        elif "COM" in building_type:
            heat_demand_standard_param = \
                standard_parameters.parse('ComHeatDemand')
        elif "IND" in building_type:
            heat_demand_standard_param = \
                standard_parameters.parse('IndHeatDemand')
        else:
            raise ValueError("building_type does not exist")
        heat_demand_standard_param.set_index(
            "year of construction", inplace=True)
        if int(yoc) <= 1918:  # TODO
            yoc = "<1918"
        if units > 12:
            units = "> 12"
        if "RES" in building_type:
            specific_heat_demand = \
                heat_demand_standard_param.loc[yoc][str(units) + ' unit(s)']
        else:
            specific_heat_demand = \
                heat_demand_standard_param.loc[yoc][building_type]
        net_floor_area = area * sinks_standard_param \
            .loc[building_type + "_heat_sink"]['net_floor_area / area']
        demand_heat = specific_heat_demand * net_floor_area

        create_standard_parameter_sink(sink_type=building_type + "_heat_sink",
                                       label=str(sink_id) + "_heat_demand",
                                       sink_input=str(sink_id) + "_heat_bus",
                                       annual_demand=demand_heat,
                                       standard_parameters=standard_parameters,
                                       lat=latitude,
                                       lon=longitude,
                                       dh=dh_value)


def create_pv_source(building_id, plant_id, azimuth, tilt, area,
                     pv_standard_parameters, latitude, longitude):
    """
        TODO DOCSTRINGTEXT
        :param building_id: building label
        :type building_id: str
        :param plant_id: roof part number
        :type plant_id: str
        :param azimuth: azimuth of given roof part
        :type azimuth: float
        :param tilt: tilt of given roof part
        :type tilt: float
        :param area: area of the given roof part
        :type area: float
        :param pv_standard_parameters: pandas Dataframe holding the PV
                                       specific standard parameters
        :type pv_standard_parameters: pd.Dataframe
        :param latitude: geographic latitude of the building
        :type latitude: float
        :param longitude: geographic longitude of the building
        :type longitude: float
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
            pv_standard_parameters[pv_standard_keys[i]]

    pv_house_specific_dict['max. investment capacity'] = \
        pv_standard_parameters['Capacity per Area (kW/m2)'] * area

    # produce a pandas series out of the dict above due to easier appending
    pv_series = pd.Series(pv_house_specific_dict)
    sheets["sources"] = sheets["sources"].append(pv_series, ignore_index=True)


def create_solarthermal_source(building_id, plant_id, azimuth, tilt, area,
                               solarthermal_standard_parameters, latitude,
                               longitude):
    """
        TODO DOCSTRINGTEXT
        :param building_id: building label
        :type building_id: str
        :param plant_id: roof part number
        :type plant_id: str
        :param azimuth: azimuth of given roof part
        :type azimuth: float
        :param tilt: tilt of given roof part
        :type tilt: float
        :param area: area of the given roof part
        :type area: float
        :param solarthermal_standard_parameters: pandas Dataframe
                                                 holding the ST specific
                                                 standard parameters
        :type solarthermal_standard_parameters: pd.Dataframe
        :param latitude: geographic latitude of the building
        :type latitude: float
        :param longitude: geographic longitude of the building
        :type longitude: float
    """

    # technical parameters
    solarthermal_house_specific_dict = \
        {'label': (str(building_id) + '_' + str(plant_id)
                   + '_solarthermal_source'),
         'existing capacity': 0,
         'min. investment capacity': 0,
         'output': str(building_id) + '_heat_bus',
         'Azimuth': azimuth,
         'Surface Tilt': tilt,
         'Latitude': latitude,
         'Longitude': longitude,
         'input': str(building_id) + '_electricity_bus'}

    # read the pv standards from standard_parameters.xlsx and append
    # them to the pv_house_specific_dict
    solarthermal_standard_keys = \
        solarthermal_standard_parameters.keys().tolist()
    for i in range(len(solarthermal_standard_keys)):
        solarthermal_house_specific_dict[solarthermal_standard_keys[i]] = \
            solarthermal_standard_parameters[solarthermal_standard_keys[i]]

    solarthermal_house_specific_dict['max. investment capacity'] = \
        solarthermal_standard_parameters['Capacity per Area (kW/m2)'] * area

    # produce a pandas series out of the dict above due to easier appending
    solarthermal_series = pd.Series(solarthermal_house_specific_dict)
    sheets["sources"] = \
        sheets["sources"].append(solarthermal_series, ignore_index=True)


def create_competition_constraint(component1, factor1, component2, factor2,
                                  limit):
    """
        TODO DOCSTRINGTEXT
        :param component1: label of the first component in competition
        :type component1: str
        :param factor1: power per unit of the first component
                        in competition
        :type factor1: float
        :param component2: label of the second component in competition
        :type component2: str
        :param factor2: power per unit of the second component
                        in competition
        :type factor2: float
        :param limit:
        :type limit: float
    """
    # define individual values
    constraint_dict = {'component 1': component1,
                       'factor 1': factor1,
                       'component 2': component2,
                       'factor 2': factor2,
                       'limit': limit,
                       'active': 1}

    sheets["competition constraints"] = \
        sheets["competition constraints"].append(pd.Series(constraint_dict),
                                                 ignore_index=True)


def create_gchp(parcel_id, area, standard_parameters):
    """
        TODO DOCSTRING TEXT

        :param parcel_id: parcel label
        :type parcel_id: str
        :param area: parcel area which can be used for gchp anergy
        :type area: float
        :param standard_parameters: Dataframe holding gchp specific
                                    standard parameters
        :type standard_parameters: pd.Dataframe
    """
    # gchp transformer
    transformers_standard_parameters = \
        standard_parameters.parse('transformers')
    transformers_standard_parameters.set_index('comment', inplace=True)
    gchp_standard_parameters = \
        transformers_standard_parameters.loc['building_gchp_transformer']

    probe_length = \
        transformers_standard_parameters.loc['building_gchp_transformer'][
            'length of the geoth. probe']
    heat_extraction = \
        transformers_standard_parameters.loc['building_gchp_transformer'][
            'heat extraction']
    min_bore_hole_area = \
        transformers_standard_parameters.loc['building_gchp_transformer'][
            'min. borehole area']

    gchp_house_specific_dict = {'label': str(parcel_id) + '_gchp_transformer',
                                'comment': 'automatically_created',
                                'input': str(parcel_id) + '_hp_elec_bus',
                                'output': str(parcel_id) + '_heat_bus',
                                'output2': 'None',
                                'area': area,
                                'existing capacity': 0,
                                'min. investment capacity': 0}

    # read the gchp standards from standard_parameters.xlsx and append
    # them to the gchp_house_specific_dict
    gchp_standard_keys = gchp_standard_parameters.keys().tolist()
    for i in range(len(gchp_standard_keys)):
        gchp_house_specific_dict[gchp_standard_keys[i]] = \
            gchp_standard_parameters[gchp_standard_keys[i]]

    # produce a pandas series out of the dict above due to easier appending
    gchp_series = pd.Series(gchp_house_specific_dict)
    sheets["transformers"] = \
        sheets["transformers"].append(gchp_series, ignore_index=True)


def create_ashp(building_id, standard_parameters):
    """
        TODO DOCSTRING TEXT
        :param building_id: building label
        :type building_id: str
        :param standard_parameters: Dataframe holding ashp specific
                                    standard parameters
        :type standard_parameters: pd.Dataframe
    """
    # ashp transformer
    transformers_standard_parameters = \
        standard_parameters.parse('transformers')
    transformers_standard_parameters.set_index('comment', inplace=True)
    ashp_standard_parameters = \
        transformers_standard_parameters.loc['building_ashp_transformer']

    ashp_house_specific_dict = {'label': (str(building_id)
                                          + '_ashp_transformer'),
                                'comment': 'automatically_created',
                                'input': str(building_id) + '_hp_elec_bus',
                                'output': str(building_id) + '_heat_bus',
                                'output2': 'None',
                                'existing capacity': 0,
                                'min. investment capacity': 0}

    # read the ashp standards from standard_parameters.xlsx and append
    # them to the ashp_house_specific_dict
    ashp_standard_keys = ashp_standard_parameters.keys().tolist()
    for i in range(len(ashp_standard_keys)):
        ashp_house_specific_dict[ashp_standard_keys[i]] = \
            ashp_standard_parameters[ashp_standard_keys[i]]

    # produce a pandas series out of the dict above due to easier appending
    ashp_series = pd.Series(ashp_house_specific_dict)
    sheets["transformers"] = \
        sheets["transformers"].append(ashp_series, ignore_index=True)


def create_gas_heating(building_id, building_type, standard_parameters):
    """
        TODO DOCSTRING TEXT
        :param building_id: building label
        :type building_id: str
        :param building_type: defines rather the usage is residential
                              or commercial
        :type building_type: str
        :param standard_parameters: Dataframe holding ashp specific
                                    standard parameters
        :type standard_parameters: pd.Dataframe
    """

    if building_type == "RES":
        bus = 'building_res_gas_bus'
    elif building_type == "IND":
        bus = 'building_ind_gas_bus'
    else:
        bus = 'building_com_gas_bus'
    # building gas bus
    create_standard_parameter_bus(label=str(building_id) + "_gas_bus",
                                  bus_type=bus,
                                  standard_parameters=standard_parameters)

    # define individual gas_heating_parameters
    gas_heating_house_specific_dict = \
        {'label': str(building_id) + '_gasheating_transformer',
         'comment': 'automatically_created',
         'input': str(building_id) + '_gas_bus',
         'output': str(building_id) + '_heat_bus',
         'output2': 'None'}

    create_standard_parameter_transformer(
        specific_param=gas_heating_house_specific_dict,
        standard_parameters=standard_parameters,
        standard_param_name='building_gasheating_transformer')


def create_electric_heating(building_id, standard_parameters):
    """
        TODO DOCSTRING TEXT
        :param building_id: building label
        :type building_id: str
        :param standard_parameters: Dataframe holding electric heating
                                    specific standard parameters
        :type standard_parameters: pd.Dataframe
    """
    transformers_standard_parameters = \
        standard_parameters.parse('transformers')
    transformers_standard_parameters.set_index('comment', inplace=True)
    electric_heating_standard_parameters = \
        transformers_standard_parameters.loc[
            'building_electricheating_transformer']

    # define individual electric_heating_parameters
    electric_heating_house_specific_dict = \
        {'label': str(building_id) + '_electricheating_transformer',
         'comment': 'automatically_created',
         'input': str(building_id) + '_electricity_bus',
         'output': str(building_id) + '_heat_bus',
         'output2': 'None'}

    # read the electricheating standards from standard_parameters.xlsx
    # and append them to the  electric_heating_house_specific_dict
    electric_heating_standard_keys = \
        electric_heating_standard_parameters.keys().tolist()
    for i in range(len(electric_heating_standard_keys)):
        electric_heating_house_specific_dict[
            electric_heating_standard_keys[i]] = \
            electric_heating_standard_parameters[
                electric_heating_standard_keys[i]]

    # produce a pandas series out of the dict above due to easier appending
    electric_heating_series = pd.Series(electric_heating_house_specific_dict)
    sheets["transformers"] = \
        sheets["transformers"].append(electric_heating_series,
                                      ignore_index=True)


def create_battery(building_id, standard_parameters, storage_type: str):
    """
        TODO DOCSTRING TEXT
        :param building_id: building label
        :type building_id: str
        :param standard_parameters: Dataframe holding battery
                                    specific standard parameters
        :type standard_parameters: pd.Dataframe
        :param storage_type:
        :type storage_type: str
    """
    battery_house_specific_dict = \
        {'label': str(building_id) + '_battery_storage',
         'comment': 'automatically_created',
         'bus': str(building_id) + '_electricity_bus'}

    create_standard_parameter_storage(
        specific_param=battery_house_specific_dict,
        standard_parameters=standard_parameters,
        standard_param_name=storage_type + '_battery_storage')


def create_thermal_storage(building_id, standard_parameters,
                           storage_type: str, bus=None):
    """
        TODO DOCSTRING TEXT
        :param building_id: building label
        :type building_id: str
        :param standard_parameters: Dataframe holding thermal storage
                                    specific standard parameters
        :type standard_parameters: pd.Dataframe
        :param storage_type:
        :type storage_type: str
    """
    thermal_storage_house_specific_dict = \
        {'label': str(building_id) + '_thermal_storage',
         'comment': 'automatically_created',
         'bus': str(building_id) + '_heat_bus'}
    if bus:
        thermal_storage_house_specific_dict["bus"] = bus

    create_standard_parameter_storage(
        specific_param=thermal_storage_house_specific_dict,
        standard_parameters=standard_parameters,
        standard_param_name=storage_type + '_thermal_storage')


def create_building_insulation(building_id, standard_parameters, yoc,
                               area_window, area_wall, area_roof, roof_type):
    """
        TODO DOCSTRING TEXT
        :param building_id: building label
        :type building_id: str
        :param standard_parameters: Dataframe holding the information
                                    loaded from excel standard
                                    parameters file
        :type standard_parameters: pd.Dataframe
        :param yoc: year of construction of the given building
        :type yoc: int
        :param area_window: summed area of windows of the given building
        :type area_window: float
        :param area_wall: summed area of walls (without windows) of the
                          given building
        :type area_wall: float
        :param area_roof: summed area of roof parts of the given
                          building
        :type area_roof: float
        :param roof_type: defines rather the roof is a flat one or not
        :type roof_type: str
    """
    insul_standard_parameters = \
        standard_parameters.parse('insulation')
    insul_standard_parameters.set_index("year of construction", inplace=True)
    if int(yoc) <= 1918:  # TODO
        yoc = "<1918"
    u_value_roof = insul_standard_parameters.loc[yoc]["roof"]
    u_value_outer_wall = insul_standard_parameters.loc[yoc]["outer wall"]
    u_value_window = insul_standard_parameters.loc[yoc]["window"]
    u_value_flat_roof_potential = \
        insul_standard_parameters.loc["potential flat"]["roof"]
    u_value_roof_potential = insul_standard_parameters.loc["potential"]["roof"]
    u_value_outer_wall_potential = \
        insul_standard_parameters.loc["potential"]["outer wall"]
    u_value_window_potential = \
        insul_standard_parameters.loc["potential"]["window"]
    periodical_costs_roof = \
        insul_standard_parameters.loc["periodical_costs"]["roof"]
    periodical_costs_flat_roof = \
        insul_standard_parameters.loc["periodical_costs_flat"]["roof"]
    periodical_costs_wall = \
        insul_standard_parameters.loc["periodical_costs"]["outer wall"]
    periodical_costs_window = \
        insul_standard_parameters.loc["periodical_costs"]["window"]
    periodical__constraint_costs_roof = \
        insul_standard_parameters.loc["periodical_constraint_costs"]["roof"]
    periodical__constraint_costs_wall = \
        insul_standard_parameters.loc["periodical_constraint_costs"]["outer wall"]
    periodical__constraint_costs_window = \
        insul_standard_parameters.loc["periodical_constraint_costs"]["window"]

    if area_window:
        window_dict = {'label': str(building_id) + "_window",
                       'comment': 'automatically_created',
                       'active': 1,
                       'sink': str(building_id) + "_heat_demand",
                       'temperature indoor': 20,
                       'heat limit temperature': 15,
                       'U-value old': u_value_window,
                       'U-value new': u_value_window_potential,
                       'area': area_window,
                       'periodical costs': periodical_costs_window,
                       'periodical_constraint_costs':
                           periodical__constraint_costs_window}
        window_series = pd.Series(window_dict)
        sheets["energetic renovation measures"] = \
            sheets["energetic renovation measures"].append(window_series,
                                                           ignore_index=True)
    if area_wall:
        wall_dict = {'label': str(building_id) + "_wall",
                     'comment': 'automatically_created',
                     'active': 1,
                     'sink': str(building_id) + "_heat_demand",
                     'temperature indoor': 20,
                     'heat limit temperature': 15,
                     'U-value old': u_value_outer_wall,
                     'U-value new': u_value_outer_wall_potential,
                     'area': area_wall,
                     'periodical costs': periodical_costs_wall,
                     'periodical_constraint_costs':
                         periodical__constraint_costs_wall}
        wall_series = pd.Series(wall_dict)
        sheets["energetic renovation measures"] = \
            sheets["energetic renovation measures"].append(wall_series,
                                                           ignore_index=True)
    if area_roof:
        if roof_type == "flachdach":
            u_value_new = u_value_flat_roof_potential
            periodical_costs = periodical_costs_flat_roof
        else:
            u_value_new = u_value_roof_potential
            periodical_costs = periodical_costs_roof
        roof_dict = {'label': str(building_id) + "_roof",
                     'comment': 'automatically_created',
                     'active': 1,
                     'sink': str(building_id) + "_heat_demand",
                     'temperature indoor': 20,
                     'heat limit temperature': 15,
                     'U-value old': u_value_roof,
                     'U-value new': u_value_new,
                     'area': area_roof,
                     'periodical costs': periodical_costs,
                     'periodical_constraint_costs':
                         periodical__constraint_costs_roof}
        roof_series = pd.Series(roof_dict)
        sheets["energetic renovation measures"] = \
            sheets["energetic renovation measures"].append(roof_series,
                                                           ignore_index=True)


def sink_clustering(building, sink, sink_parameters):
    """
        TODO DOCSTRING
    """

    if str(building[0]) in sink["label"] \
            and "electricity" in sink["label"]:
        if sink["load profile"] == "h0" and "RES" in building[2]:
            sink_parameters[0] += sink["annual demand"]
            sheets["sinks"] = sheets["sinks"].drop(index=sink["label"])
        elif "COM" in building[2]:
            sink_parameters[1] += sink["annual demand"]
            sheets["sinks"] = sheets["sinks"].drop(index=sink["label"])
        elif "IND" in building[2]:
            sink_parameters[2] += sink["annual demand"]
            sheets["sinks"] = sheets["sinks"].drop(index=sink["label"])
    elif str(building[0]) in sink["label"] \
            and "heat" in sink["label"]:
        sink_parameters[3].append((building[2], sink["input"]))
        if "RES" in building[2]:
            sink_parameters[4] += sink["annual demand"]
        elif "COM" in building[2]:
            sink_parameters[5] += sink["annual demand"]
        elif "IND" in building[2]:
            sink_parameters[6] += sink["annual demand"]
    return sink_parameters


def sources_clustering(building, sources, source_parameters, azimuth_type):
    if str(building[0]) in sources["label"] \
            and sources["technology"] == "photovoltaic" \
            and sources["label"] in sheets["sources"].index:
        # [counter, maxinvest, periodical costs,
        # periodical constraint costs, variable costs, Albedo,
        # Altitude, Azimuth, Surface Tilt, Latitude, Longitude]

        # counter
        source_parameters["photovoltaic_{}".format(azimuth_type)][0] \
            += 1
        # maxinvest
        source_parameters["photovoltaic_{}".format(azimuth_type)][1] \
            += sources["max. investment capacity"]
        # periodical_costs
        source_parameters["photovoltaic_{}".format(azimuth_type)][2] \
            += sources["periodical costs"]
        # periodical constraint costs
        source_parameters["photovoltaic_{}".format(azimuth_type)][3] \
            += sources["periodical constraint costs"]
        # variable costs
        source_parameters["photovoltaic_{}".format(azimuth_type)][4] \
            += sources["variable costs"]
        # albedo
        source_parameters["photovoltaic_{}".format(azimuth_type)][5] \
            += sources["Albedo"]
        # altitude
        source_parameters["photovoltaic_{}".format(azimuth_type)][6] \
            += sources["Altitude"]
        # azimuth
        source_parameters["photovoltaic_{}".format(azimuth_type)][7] \
            += sources["Azimuth"]
        # surface tilt
        source_parameters["photovoltaic_{}".format(azimuth_type)][8] \
            += sources["Surface Tilt"]
        # latitude
        source_parameters["photovoltaic_{}".format(azimuth_type)][9] \
            += sources["Latitude"]
        # longitude
        source_parameters["photovoltaic_{}".format(azimuth_type)][10] \
            += sources["Longitude"]
        sheets["sources"] = sheets["sources"].drop(index=sources["label"])

    if str(building[0]) in sources["label"] \
            and sources["technology"] == "solar_thermal_flat_plate" \
            and sources["label"] in sheets["sources"].index:
        # counter
        source_parameters["solar_thermal_{}".format(azimuth_type)][0] \
            += 1
        # maxinvest
        source_parameters["solar_thermal_{}".format(azimuth_type)][1] \
            += sources["max. investment capacity"]
        # periodical_costs
        source_parameters["solar_thermal_{}".format(azimuth_type)][2] \
            += sources["periodical costs"]
        # periodical constraint costs
        source_parameters["solar_thermal_{}".format(azimuth_type)][3] \
            += sources["periodical constraint costs"]
        # variable costs
        source_parameters["solar_thermal_{}".format(azimuth_type)][4] \
            += sources["variable costs"]
        # albedo
        source_parameters["solar_thermal_{}".format(azimuth_type)][5] \
            += sources["Albedo"]
        # altitude
        source_parameters["solar_thermal_{}".format(azimuth_type)][6] \
            += sources["Altitude"]
        # azimuth
        source_parameters["solar_thermal_{}".format(azimuth_type)][7] \
            += sources["Azimuth"]
        # surface tilt
        source_parameters["solar_thermal_{}".format(azimuth_type)][8] \
            += sources["Surface Tilt"]
        # latitude
        source_parameters["solar_thermal_{}".format(azimuth_type)][9] \
            += sources["Latitude"]
        # longitude
        source_parameters["solar_thermal_{}".format(azimuth_type)][10] \
            += sources["Longitude"]
        sheets["sources"] = sheets["sources"].drop(index=sources["label"])

    return source_parameters


def transformer_clustering(building, transformer,
                           transformer_parameters, heat_buses_gchps):
    if str(building[0]) in transformer["label"] \
            and "gasheating" in transformer["label"] \
            and transformer["label"] in sheets["transformers"].index:
        transformer_parameters["gasheating"][0] += 1
        transformer_parameters["gasheating"][1] \
            += transformer["efficiency"]
        transformer_parameters["gasheating"][3] \
            += transformer["periodical costs"]
        transformer_parameters["gasheating"][4] += \
            transformer["variable output constraint costs"]
        sheets["transformers"] = \
            sheets["transformers"].drop(index=transformer["label"])
    if str(building[0]) in transformer["label"] \
            and "electric" in transformer["label"] \
            and transformer["label"] in sheets["transformers"].index:
        transformer_parameters["electric_heating"][0] += 1
        transformer_parameters["electric_heating"][1] \
            += transformer["efficiency"]
        transformer_parameters["electric_heating"][3] += transformer[
            "periodical costs"]
        transformer_parameters["electric_heating"][4] += \
            transformer["variable output constraint costs"]
        sheets["transformers"] = \
            sheets["transformers"].drop(index=transformer["label"])
    if str(building[0]) in transformer["label"] \
            and "ashp" in transformer["label"] \
            and transformer["label"] in sheets["transformers"].index:
        transformer_parameters["ashp"][0] += 1
        transformer_parameters["ashp"][1] \
            += transformer["efficiency"]
        transformer_parameters["ashp"][2] \
            += transformer["efficiency2"]
        transformer_parameters["ashp"][3] += transformer[
            "periodical costs"]
        transformer_parameters["ashp"][4] += \
            transformer["variable output constraint costs"]
        sheets["transformers"] = \
            sheets["transformers"].drop(index=transformer["label"])
    if str(building[1]) != "0":
        if str(building[1])[-9:] in transformer["label"] \
                and "gchp" in transformer["label"] \
                and transformer["label"] in sheets["transformers"].index:
            transformer_parameters["gchp"][0] += 1
            transformer_parameters["gchp"][1] \
                += transformer["efficiency"]
            transformer_parameters["gchp"][2] \
                += transformer["efficiency2"]
            transformer_parameters["gchp"][3] += transformer[
                "periodical costs"]
            transformer_parameters["gchp"][4] += \
                transformer["variable output constraint costs"]
            transformer_parameters["gchp"][5] += \
                transformer["area"]
            sheets["buses"].set_index("label", inplace=True, drop=False)
            if transformer["output"] in sheets["buses"].index:
                sheets["buses"] = \
                    sheets["buses"].drop(index=transformer["output"])
            sheets["transformers"] = \
                sheets["transformers"].drop(index=transformer["label"])
    return heat_buses_gchps, transformer_parameters


def storage_clustering(building, storage, storage_parameter):
    if str(building[0]) in storage["label"] \
            and "battery" in storage["label"] \
            and storage["label"] in sheets["storages"].index:
        storage_parameter["battery"][0] += 1
        storage_parameter["battery"][1] += storage["max. investment capacity"]
        storage_parameter["battery"][2] += storage["periodical costs"]
        storage_parameter["battery"][3] += storage[
            "periodical constraint costs"]
        sheets["storages"] = sheets["storages"].drop(index=storage["label"])
    if str(building[0]) in storage["label"] \
            and "thermal" in storage["label"] \
            and storage["label"] in sheets["storages"].index:
        storage_parameter["thermal"][0] += 1
        storage_parameter["thermal"][1] += storage["max. investment capacity"]
        storage_parameter["thermal"][2] += storage["periodical costs"]
        storage_parameter["thermal"][3] += storage[
            "periodical constraint costs"]
        storage_parameter["thermal"][4] += storage["variable output costs"]
        sheets["storages"] = sheets["storages"].drop(index=storage["label"])
    return storage_parameter


def restructuring_links(sheets_clustering, building, cluster,
                        standard_parameters):
    # TODO comments
    for i, j in sheets_clustering["links"].iterrows():

        if j["label"] in sheets["links"].index:
            # remove heatpump links
            if str(building[0]) in j["bus2"] and "hp_elec" in j["bus2"]:
                sheets["links"] = sheets["links"].drop(index=j["label"])
            if str(building[1])[-9:] in j["bus2"] and "hp_elec" in j["bus2"] \
                    and j["label"] in sheets["links"].index:
                sheets["links"] = sheets["links"].drop(index=j["label"])
            # delete pvbus -> central elec
            if str(building[0]) in j["bus1"] and \
                    "central_electricity" in j["bus2"] and \
                    "pv_bus" in j["bus1"]:
                sheets["links"] = sheets["links"].drop(index=j["label"])
                if not (str(cluster) + "_pv_bus" in j["bus1"]
                        and "central_electricity" in j["bus2"]) \
                        and cluster + "pv_central_electricity_link" \
                        not in sheets["links"].index:
                    create_standard_parameter_link(
                        cluster + "pv_central_electricity_link",
                        bus_1=cluster + "_pv_bus",
                        bus_2="central_electricity_bus",
                        link_type="building_pv_central_link",
                        standard_parameters=standard_parameters)
                    sheets["links"].set_index("label", inplace=True,
                                              drop=False)
            # delete pvbus ->  elec bus of building
            if str(building[0]) in j["bus1"] and \
                    str(building[0]) in j["bus2"] and \
                    "pv_bus" in j["bus1"]:
                sheets["links"] = sheets["links"].drop(
                    index=j["label"])

            if str(building[1][-9:]) in j["bus1"] and "heat" in j["bus1"]:
                sheets["links"] = sheets["links"].drop(index=j["label"])

            # connecting the clusters to the central gas bus
            if str(building[0]) in j["label"]:
                if "central_naturalgas" in j["bus1"] and \
                        "_gas_bus" in j["bus2"]:
                    sheets["links"] = sheets["links"].drop(index=j["label"])

                    if "central_naturalgas" + cluster \
                            not in sheets["links"].index:
                        create_standard_parameter_link(
                            "central_naturalgas" + cluster,
                            bus_1="central_naturalgas_bus",
                            bus_2=cluster + "_gas_bus",
                            link_type="central_naturalgas_building_link",
                            standard_parameters=standard_parameters)
                        sheets["links"].set_index("label", inplace=True,
                                                  drop=False)
        if str(building[0]) in j["bus2"] and "electricity" in j["bus2"]:
            sheets["links"]['bus2'] = \
                sheets["links"]['bus2'].replace(
                    [str(building[0]) + "_electricity_bus"],
                    str(cluster) + "_electricity_bus")
        # delete and replace central elec -> building elec
        if str(building[0]) in j["bus2"] and \
                "central_electricity" in j["bus1"] and \
                "electricity_bus" in j["bus2"]:
            sheets["links"] = sheets["links"].drop(index=j["label"])

        if str(building[0]) in j["bus2"] and \
                "gas" in j["bus2"]:
            sheets["links"]['bus2'] = \
                sheets["links"]['bus2'].replace(
                    [str(building[0]) + "_gas_bus"],
                    str(cluster) + "_gas_bus")


def create_central_elec_bus_connection(cluster, standard_parameters):
    if (cluster + "central_electricity_link") \
            not in sheets["links"].index:
        create_standard_parameter_link(
            cluster + "central_electricity_link",
            bus_1="central_electricity_bus",
            bus_2=cluster + "_electricity_bus",
            link_type="building_central_building_link",
            standard_parameters=standard_parameters)
        sheets["links"].set_index("label", inplace=True,
                                  drop=False)
    if (cluster + "pv_" + cluster + "_electricity_link") \
            not in sheets["links"].index:
        create_standard_parameter_link(
            cluster + "pv_" + cluster + "_electricity_link",
            bus_1=cluster + "_pv_bus",
            bus_2=cluster + "_electricity_bus",
            link_type="building_pv_central_link",
            standard_parameters=standard_parameters)
        sheets["links"].set_index("label", inplace=True,
                                  drop=False)


def clustering_method(tool, standard_parameters, sheet_names, central_electricity_network):
    """
        TODO DOCSTRING TEXT
        :param tool:
        :type tool: pd.Dataframe
        :param standard_parameters:
        :type standard_parameters:
        :param sheet_names:
        :type sheet_names:
    """

    # create a dictionary holding the combination of cluster ID the included
    # building labels and its parcels
    cluster_ids = {}
    for num, building in tool.iterrows():
        if building["active"]:
            if str(building["cluster_ID"]) in cluster_ids:
                cluster_ids[str(building["cluster_ID"])].append(
                    [building['label'],
                     building['parcel'],
                     str(building["building type"][0:3])])
            else:
                cluster_ids.update({str(building["cluster_ID"]):
                                        [[building['label'],
                                          building['parcel'],
                                          str(building["building type"][
                                              0:3])]]})
    # lokal copy of status of scenario components
    sheets_clustering = {}
    for sheet in sheet_names:
        sheet_edited = sheets[sheet].copy()
        sheet_edited = sheet_edited.drop(index=0)
        sheets_clustering.update({sheet: sheet_edited})
    # start clustering
    # remove not longer used buses
    for i, j in sheets_clustering["buses"].iterrows():
        if "gas" in j["label"] and "central" not in j["label"]:
            sheets["buses"] = sheets["buses"].drop(index=i)
        if "electricity" in j["label"] and "central" not in j["label"]:
            sheets["buses"] = sheets["buses"].drop(index=i)
        if "hp_elec" in j["label"] and "swhp_elec" not in j["label"]:
            sheets["buses"] = sheets["buses"].drop(index=i)
        if "pv_bus" in j["label"]:
            sheets["buses"] = sheets["buses"].drop(index=i)
    heat_buses_gchps = []
    for cluster in cluster_ids:
        sheets["transformers"].set_index("label", inplace=True, drop=False)
        sheets["storages"].set_index("label", inplace=True, drop=False)
        sheets["links"].set_index("label", inplace=True, drop=False)
        sheets["sinks"].set_index("label", inplace=True, drop=False)
        sheets["sources"].set_index("label", inplace=True, drop=False)
        sheets["buses"].set_index("label", inplace=True, drop=False)
        if cluster_ids[cluster]:
            # cluster sinks parameter [res_elec_demand, com_elec_demand,
            #                          ind_elec_demand, heat_buses,
            #                          res_heat_demand, com_heat_demand,
            #                          ind_heat_demand]
            sink_parameters = [0, 0, 0, [], 0, 0, 0]
            # transformer_param technology: [counter, efficiency, efficiency2,
            # periodical_costs, variable_constraint_costs]
            transformer_parameters = \
                {"gasheating": [0, 0, "x", 0, 0],
                 "electric_heating": [0, 0, "x", 0, 0],
                 "ashp": [0, 0, 0, 0, 0],
                 "gchp": [0, 0, 0, 0, 0, 0]}
            # storage param technology: [counter, maxinvest, periodical costs,
            # periodical constraint costs, variable output costs]
            storage_parameters = {"battery": [0, 0, 0, 0, "x"],
                                  "thermal": [0, 0, 0, 0, 0]}

            # storage param technology: [counter, maxinvest, periodical costs,
            # periodical constraint costs, variable costs, Albedo,
            # Altitude, Azimuth, Surface Tilt, Latitude, Longitude]
            source_parameters = {
                "photovoltaic_north": [0 for i in range(11)],
                "photovoltaic_north_east": [0 for i in range(11)],
                "photovoltaic_east": [0 for i in range(11)],
                "photovoltaic_south_east": [0 for i in range(11)],
                "photovoltaic_south": [0 for i in range(11)],
                "photovoltaic_south_west": [0 for i in range(11)],
                "photovoltaic_west": [0 for i in range(11)],
                "photovoltaic_north_west": [0 for i in range(11)],
                "solar_thermal_north": [0 for i in range(11)],
                "solar_thermal_north_east": [0 for i in range(11)],
                "solar_thermal_east": [0 for i in range(11)],
                "solar_thermal_south_east": [0 for i in range(11)],
                "solar_thermal_south": [0 for i in range(11)],
                "solar_thermal_south_west": [0 for i in range(11)],
                "solar_thermal_west": [0 for i in range(11)],
                "solar_thermal_north_west": [0 for i in range(11)],
            }

            for building in cluster_ids[cluster]:
                for index, sink in sheets_clustering["sinks"].iterrows():
                    # collecting information for bundled elec sinks
                    sink_parameters = \
                        sink_clustering(building, sink,
                                        sink_parameters)
                if "RES" in building[2] \
                        and str(cluster) + "_res_electricity_bus" \
                        not in sheets["buses"].index:

                    # cluster electricity bus if cluster type is res / com
                    create_standard_parameter_bus(
                        label=str(cluster) + "_res_electricity_bus",
                        bus_type='building_res_electricity_bus',
                        standard_parameters=standard_parameters)
                    sheets["buses"].set_index("label", inplace=True,
                                              drop=False)

                    # Creates a Bus connecting the cluster electricity bus with
                    # the res electricity bus
                    create_standard_parameter_link(
                        label=str(cluster) + "_res_electricity_link",
                        bus_1=str(cluster) + "_electricity_bus",
                        bus_2=str(cluster) + "_res_electricity_bus",
                        link_type='building_pv_building_link',
                        standard_parameters=standard_parameters)
                    sheets["links"].set_index("label", inplace=True,
                                              drop=False)

                elif "COM" in building[2] \
                        and str(cluster) + "_com_electricity_bus" \
                        not in sheets["buses"].index:
                    # cluster electricity bus if cluster type is res / com
                    create_standard_parameter_bus(
                        label=str(cluster) + "_com_electricity_bus",
                        bus_type='building_com_electricity_bus',
                        standard_parameters=standard_parameters)
                    sheets["buses"].set_index("label", inplace=True,
                                              drop=False)

                    # Creates a Bus connecting the cluster electricity bus with
                    # the com electricity bus
                    create_standard_parameter_link(
                        label=str(cluster) + "_com_electricity_link",
                        bus_1=str(cluster) + "_electricity_bus",
                        bus_2=str(cluster) + "_com_electricity_bus",
                        link_type='building_pv_building_link',
                        standard_parameters=standard_parameters)
                    sheets["links"].set_index("label", inplace=True,
                                              drop=False)
                elif "IND" in building[2] \
                        and str(cluster) + "_ind_electricity_bus" \
                        not in sheets["buses"].index:
                    # cluster electricity bus if cluster type is res / com
                    create_standard_parameter_bus(
                        label=str(cluster) + "_ind_electricity_bus",
                        bus_type='building_ind_electricity_bus',
                        standard_parameters=standard_parameters)
                    sheets["buses"].set_index("label", inplace=True,
                                              drop=False)

                    # Creates a Bus connecting the cluster electricity bus with
                    # the com electricity bus
                    create_standard_parameter_link(
                        label=str(cluster) + "_ind_electricity_link",
                        bus_1=str(cluster) + "_electricity_bus",
                        bus_2=str(cluster) + "_ind_electricity_bus",
                        link_type='building_pv_building_link',
                        standard_parameters=standard_parameters)
                    sheets["links"].set_index("label", inplace=True,
                                              drop=False)
                for index, sources in sheets_clustering["sources"].iterrows():
                    # collecting information for bundled photovoltaic systems
                    if sources["technology"] in ["photovoltaic",
                                                 "solar_thermal_flat_plate"]:
                        if -22.5 <= sources["Azimuth"] < 22.5:
                            azimuth_type = "north"
                        elif 22.5 <= sources["Azimuth"] < 67.5:
                            azimuth_type = "north_east"
                        elif 67.5 <= sources["Azimuth"] < 112.5:
                            azimuth_type = "east"
                        elif 112.5 <= sources["Azimuth"] < 157.5:
                            azimuth_type = "south_east"
                        elif sources["Azimuth"] >= 157.5 \
                                or sources["Azimuth"] < -157.5:
                            azimuth_type = "south"
                        elif -157.5 <= sources["Azimuth"] < -112.5:
                            azimuth_type = "south_west"
                        elif -112.5 <= sources["Azimuth"] < -67.5:
                            azimuth_type = "west"
                        elif -67.5 <= sources["Azimuth"] < -22.5:
                            azimuth_type = "north_west"

                        source_parameters = \
                            sources_clustering(building,
                                               sources,
                                               source_parameters,
                                               azimuth_type)

                for index, transformer in sheets_clustering[
                    "transformers"].iterrows():
                    # collecting information for bundled transformer
                    heat_buses_gchps, transformer_parameters = \
                        transformer_clustering(building, transformer,
                                               transformer_parameters,
                                               heat_buses_gchps)
                for index, storage in sheets_clustering["storages"].iterrows():
                    # collecting information for bundled storages
                    storage_parameters = \
                        storage_clustering(building, storage,
                                           storage_parameters)
                restructuring_links(sheets_clustering, building, cluster,
                                    standard_parameters)
                # change sources output bus
                for i, j in sheets_clustering["sources"].iterrows():
                    if str(building[0]) in str(j["input"]) and \
                            "electricity" in str(j["input"]):
                        sheets["sources"]['input'] = \
                            sheets["sources"]['input'].replace(
                                [str(building[0]) + "_electricity_bus"],
                                str(cluster) + "_electricity_bus")
                    if str(building[0]) in str(j["output"]) and \
                            "heat" in str(j["output"]):
                        sheets["sources"]["output"] = \
                            sheets["sources"]["output"].replace(
                                [str(building[0]) + "_heat_bus"],
                                str(cluster) + "_heat_bus")

            bus_parameters = \
                standard_parameters.parse('buses', index_col='bus_type')
            total_annual_elec_demand = (sink_parameters[0]
                                        + sink_parameters[1]
                                        + sink_parameters[2])
            total_annual_heat_demand = (sink_parameters[4]
                                        + sink_parameters[5]
                                        + sink_parameters[6])
            if total_annual_elec_demand > 0:
                if cluster + "_electricity_bus" \
                        not in sheets["buses"].index:
                    create_standard_parameter_bus(
                        label=str(cluster) + "_electricity_bus",
                        bus_type='building_res_electricity_bus',
                        standard_parameters=standard_parameters)
                    sheets["buses"].set_index("label", inplace=True,
                                              drop=False)
                    sheets["buses"].loc[(str(cluster) + "_electricity_bus"),
                                        "shortage costs"] = \
                        ((sink_parameters[0]
                          / total_annual_elec_demand)
                         * bus_parameters.loc["building_res_electricity_bus"][
                             "shortage costs"]
                         + (sink_parameters[1] / total_annual_elec_demand)
                         * bus_parameters.loc["building_com_electricity_bus"][
                             "shortage costs"]
                         + (sink_parameters[2] / total_annual_elec_demand)
                         * bus_parameters.loc["building_ind_electricity_bus"][
                             "shortage costs"])
                if central_electricity_network:
                    create_central_elec_bus_connection(cluster,
                                                       standard_parameters)
            if sink_parameters[0] > 0:
                create_standard_parameter_sink(
                    "RES_electricity_sink",
                    str(cluster) + "_res_electricity_demand",
                    str(cluster) + "_res_electricity_bus",
                    sink_parameters[0], standard_parameters, 0)
            if sink_parameters[1] > 0:
                create_standard_parameter_sink(
                    "COM_electricity_sink",
                    str(cluster) + "_com_electricity_demand",
                    str(cluster) + "_com_electricity_bus",
                    sink_parameters[1], standard_parameters, 0)
            if sink_parameters[2] > 0:
                create_standard_parameter_sink(
                    "IND_electricity_sink",
                    str(cluster) + "_ind_electricity_demand",
                    str(cluster) + "_ind_electricity_bus",
                    sink_parameters[2], standard_parameters, 0)
            # create res or com gasheating
            if transformer_parameters["gasheating"][0] > 0:
                create_standard_parameter_bus(
                    label=str(cluster) + "_gas_bus",
                    bus_type='building_res_gas_bus',
                    standard_parameters=standard_parameters)
                sheets["buses"].set_index("label", inplace=True,
                                          drop=False)
                sheets["buses"].loc[(str(cluster) + "_gas_bus"),
                                    "shortage costs"] = \
                    ((sink_parameters[4]
                      / total_annual_heat_demand)
                     * bus_parameters.loc["building_res_gas_bus"][
                         "shortage costs"]
                     + (sink_parameters[5] / total_annual_heat_demand)
                     * bus_parameters.loc["building_com_gas_bus"][
                         "shortage costs"]
                     + (sink_parameters[6] / total_annual_heat_demand)
                     * bus_parameters.loc["building_ind_gas_bus"][
                         "shortage costs"])

                # define individual gas_heating_parameters
                gas_heating_house_specific_dict = \
                    {'label': str(cluster) + '_gasheating_transformer',
                     'comment': 'automatically_created',
                     'input': str(cluster) + '_gas_bus',
                     'output': str(cluster) + '_heat_bus',
                     'output2': 'None'}
                transformers_standard_parameters = \
                    standard_parameters.parse('transformers')
                transformers_standard_parameters.set_index(
                    'comment', inplace=True)
                standard_param = transformers_standard_parameters.loc[
                    'building_gasheating_transformer']

                standard_keys = standard_param.keys().tolist()
                for i in range(len(standard_keys)):
                    gas_heating_house_specific_dict[standard_keys[i]] = \
                        standard_param[standard_keys[i]]
                gas_heating_house_specific_dict["efficiency"] = \
                    transformer_parameters["gasheating"][1] \
                    / transformer_parameters["gasheating"][0]
                gas_heating_house_specific_dict["periodical costs"] = \
                    transformer_parameters["gasheating"][3] \
                    / transformer_parameters["gasheating"][0]
                gas_heating_house_specific_dict[
                    "variable output constraint costs"] = \
                    transformer_parameters["gasheating"][4] \
                    / transformer_parameters["gasheating"][0]
                gas_heating_house_specific_dict[
                    "max. investment capacity"] = \
                    standard_param["max. investment capacity"] \
                    * transformer_parameters["gasheating"][0]
                # produce a pandas series out of the dict above due to
                # easier appending
                transformer_series = \
                    pd.Series(gas_heating_house_specific_dict)
                sheets["transformers"] = \
                    sheets["transformers"].append(transformer_series,
                                                  ignore_index=True)
            # Define PV Standard-Parameters
            sources_standard_parameters = standard_parameters.parse(
                'sources')
            sources_standard_parameters.set_index('comment',
                                                  inplace=True)
            pv_standard_parameters = \
                sources_standard_parameters.loc[
                    'fixed photovoltaic source']

            st_stan_param = \
                sources_standard_parameters.loc[
                    'solar_thermal_collector']

            for azimuth in ["north_000", "north_east_045", "east_090",
                            "south_east_135", "south_180",
                            "south_west_225", "west_270", "north_west_315"]:
                if source_parameters["photovoltaic_{}".format(azimuth[:-4])][
                    0] > 0:
                    if (str(cluster) + "_pv_bus") not in sheets["buses"].index:
                        create_standard_parameter_bus(
                            label=str(cluster) + "_pv_bus",
                            bus_type='building_pv_bus',
                            standard_parameters=standard_parameters)
                        sheets["buses"].set_index("label", inplace=True,
                                                  drop=False)
                    create_pv_source(
                        cluster, azimuth[:-4],
                        area=source_parameters[
                                 "photovoltaic_{}".format(azimuth[:-4])][1]
                             / pv_standard_parameters[
                                 "Capacity per Area (kW/m2)"],
                        tilt=source_parameters[
                                 "photovoltaic_{}".format(azimuth[:-4])][8]
                             / source_parameters[
                                 "photovoltaic_{}".format(azimuth[:-4])][
                                 0],
                        azimuth=int(azimuth[-3:]),
                        latitude=source_parameters[
                                     "photovoltaic_{}".format(
                                         azimuth[:-4])][9]
                                 / source_parameters[
                                     "photovoltaic_{}".format(
                                         azimuth[:-4])][0],
                        longitude=source_parameters[
                                      "photovoltaic_{}".format(
                                          azimuth[:-4])][10]
                                  / source_parameters[
                                      "photovoltaic_{}".format(
                                          azimuth[:-4])][0],
                        pv_standard_parameters=pv_standard_parameters)

                # SOLAR THERMAL
                if source_parameters["solar_thermal_{}".format(azimuth[:-4])][
                    0] > 0:
                    create_solarthermal_source(
                        building_id=cluster,
                        plant_id=azimuth[:-4],
                        azimuth=int(azimuth[-3:]),
                        tilt=source_parameters[
                                 "solar_thermal_{}".format(azimuth[:-4])][
                                 8]
                             / source_parameters[
                                 "solar_thermal_{}".format(azimuth[:-4])][
                                 0],
                        area=source_parameters[
                                 "solar_thermal_{}".format(azimuth[:-4])][
                                 1]
                             / st_stan_param["Capacity per Area (kW/m2)"],
                        solarthermal_standard_parameters=st_stan_param,
                        latitude=source_parameters[
                                     "solar_thermal_{}".format(
                                         azimuth[:-4])][9]
                                 / source_parameters[
                                     "solar_thermal_{}".format(
                                         azimuth[:-4])][0],
                        longitude=source_parameters[
                                      "solar_thermal_{}".format(
                                          azimuth[:-4])][10]
                                  / source_parameters[
                                      "solar_thermal_{}".format(
                                          azimuth[:-4])][0], )

                    if \
                            source_parameters["photovoltaic_{}".format(azimuth[:-4])][
                                0] > 0:
                        area_st = source_parameters[
                                      "solar_thermal_{}".format(azimuth[:-4])][
                                      1] / st_stan_param[
                                      'Capacity per Area (kW/m2)']
                        area_pv = source_parameters[
                                      "solar_thermal_{}".format(azimuth[:-4])][
                                      1] / st_stan_param[
                                      'Capacity per Area (kW/m2)']

                        create_competition_constraint(
                            component1=str(cluster) + "_" + azimuth[
                                                            :-4] + "_solarthermal_source",
                            factor1=1 / st_stan_param[
                                'Capacity per Area (kW/m2)'],
                            component2=str(cluster) + "_" + azimuth[
                                                            :-4] + "_pv_source",
                            factor2=1 / pv_standard_parameters[
                                "Capacity per Area (kW/m2)"],
                            limit=area_st if area_st >= area_pv else area_pv)

                    # [counter, maxinvest, periodical costs,
                    # periodical constraint costs, variable costs, Albedo,
                    # Altitude, Azimuth, Surface Tilt, Latitude, Longitude]

            # TODO do we have to diiferntiate res and com
            if transformer_parameters["electric_heating"][0] > 0:
                # define individual gas_heating_parameters
                electricheating_heating_house_specific_dict = \
                    {'label': str(cluster) + '_electricheating_transformer',
                     'comment': 'automatically_created',
                     'input': str(cluster) + '_electricity_bus',
                     'output': str(cluster) + '_heat_bus',
                     'output2': 'None'}
                transformers_standard_parameters = standard_parameters.parse(
                    'transformers')
                transformers_standard_parameters.set_index(
                    'comment', inplace=True)
                standard_param = transformers_standard_parameters.loc[
                    'building_electricheating_transformer']

                standard_keys = standard_param.keys().tolist()
                for i in range(len(standard_keys)):
                    electricheating_heating_house_specific_dict[
                        standard_keys[i]] = standard_param[standard_keys[i]]
                electricheating_heating_house_specific_dict["efficiency"] = \
                    transformer_parameters["electric_heating"][1] \
                    / transformer_parameters["electric_heating"][0]
                electricheating_heating_house_specific_dict[
                    "periodical costs"] = \
                    transformer_parameters["electric_heating"][3] \
                    / transformer_parameters["electric_heating"][0]
                electricheating_heating_house_specific_dict[
                    "variable output constraint costs"] = \
                    transformer_parameters["electric_heating"][4] \
                    / transformer_parameters["electric_heating"][0]
                electricheating_heating_house_specific_dict[
                    "max. investment capacity"] = \
                    standard_param["max. investment capacity"] \
                    * transformer_parameters["electric_heating"][0]
                # produce a pandas series out of the dict above due to easier
                # appending
                transformer_series = pd.Series(
                    electricheating_heating_house_specific_dict)
                sheets["transformers"] = \
                    sheets["transformers"].append(transformer_series,
                                                  ignore_index=True)
            if transformer_parameters["ashp"][0] > 0:
                # building hp electricity bus
                create_standard_parameter_bus(
                    label=str(cluster) + "_hp_elec_bus",
                    bus_type='building_hp_electricity_bus',
                    standard_parameters=standard_parameters)
                sheets["buses"].set_index("label", inplace=True,
                                          drop=False)
                sheets["buses"].loc[(str(cluster) + "_hp_elec_bus"),
                                    "shortage costs"] = \
                    ((sink_parameters[4]
                      / total_annual_heat_demand)
                     * bus_parameters.loc["building_hp_electricity_bus"][
                         "shortage costs"]
                     + (sink_parameters[5] / total_annual_heat_demand)
                     * bus_parameters.loc["building_hp_electricity_bus"][
                         "shortage costs"]
                     + (sink_parameters[2] / total_annual_heat_demand)
                     * bus_parameters.loc["building_ind_electricity_bus"][
                         "shortage costs"])
                # electricity link from building electricity bus to hp elec bus
                create_standard_parameter_link(
                    label=str(cluster) + "_gchp_building_link",
                    bus_1=str(cluster) + "_electricity_bus",
                    bus_2=str(cluster) + "_hp_elec_bus",
                    link_type="building_hp_elec_link",
                    standard_parameters=standard_parameters)
                # define individual gas_heating_parameters
                ashp_house_specific_dict = {
                    'label': str(cluster) + '_ashp_transformer',
                    'comment': 'automatically_created',
                    'input': str(cluster) + '_hp_elec_bus',
                    'output': str(cluster) + '_heat_bus',
                    'output2': 'None',
                    'existing capacity': 0,
                    'min. investment capacity': 0}

                transformers_standard_parameters = standard_parameters.parse(
                    'transformers')
                transformers_standard_parameters.set_index(
                    'comment', inplace=True)
                standard_param = transformers_standard_parameters.loc[
                    'building_ashp_transformer']

                standard_keys = standard_param.keys().tolist()
                for i in range(len(standard_keys)):
                    ashp_house_specific_dict[standard_keys[
                        i]] = \
                        standard_param[standard_keys[i]]
                ashp_house_specific_dict["efficiency"] = \
                    transformer_parameters["ashp"][1] \
                    / transformer_parameters["ashp"][0]
                ashp_house_specific_dict["efficiency2"] = \
                    transformer_parameters["ashp"][2] \
                    / transformer_parameters["ashp"][0]
                ashp_house_specific_dict["periodical costs"] = \
                    transformer_parameters["ashp"][3] \
                    / transformer_parameters["ashp"][0]
                ashp_house_specific_dict["max. investment capacity"] = \
                    transformer_parameters["ashp"][0] \
                    * ashp_house_specific_dict["max. investment capacity"]
                # produce a pandas series out of the dict above due to easier
                # appending
                transformer_series = pd.Series(ashp_house_specific_dict)
                sheets["transformers"] = \
                    sheets["transformers"].append(transformer_series,
                                                  ignore_index=True)
            if transformer_parameters["gchp"][0] > 0:
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
                transformers_standard_parameters.set_index(
                    'comment', inplace=True)
                standard_param = transformers_standard_parameters.loc[
                    'building_gchp_transformer']

                standard_keys = standard_param.keys().tolist()
                for i in range(len(standard_keys)):
                    gchp_house_specific_dict[standard_keys[
                        i]] = \
                        standard_param[standard_keys[i]]
                gchp_house_specific_dict["efficiency"] = \
                    transformer_parameters["gchp"][1] \
                    / transformer_parameters["gchp"][0]
                gchp_house_specific_dict["efficiency2"] = \
                    transformer_parameters["gchp"][2] \
                    / transformer_parameters["gchp"][0]
                gchp_house_specific_dict["periodical costs"] = \
                    transformer_parameters["gchp"][3] \
                    / transformer_parameters["gchp"][0]
                gchp_house_specific_dict["max. investment capacity"] = \
                    transformer_parameters["gchp"][0] \
                    * gchp_house_specific_dict["max. investment capacity"]
                gchp_house_specific_dict["area"] = \
                    transformer_parameters["gchp"][5]
                # produce a pandas series out of the dict above due to easier
                # appending

                transformer_series = pd.Series(gchp_house_specific_dict)
                sheets["transformers"] = \
                    sheets["transformers"].append(transformer_series,
                                                  ignore_index=True)
            if storage_parameters["battery"][0] > 0:
                # read the standards from standard_param and append
                # them to the dict
                storage_standard_parameters = \
                    standard_parameters.parse('storages')
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

                specific_param["max. investment capacity"] = \
                    storage_parameters["battery"][1]
                specific_param["periodical costs"] = \
                    storage_parameters["battery"][2] / \
                    storage_parameters["battery"][0]
                specific_param["periodical constraint costs"] = \
                    storage_parameters["battery"][3] / \
                    storage_parameters["battery"][0]
                # produce a pandas series out of the dict above due to easier
                # appending
                storage_series = pd.Series(specific_param)
                sheets["storages"] = \
                    sheets["storages"].append(storage_series,
                                              ignore_index=True)
            if storage_parameters["thermal"][0] > 0:
                # read the standards from standard_param and append
                # them to the dict
                storage_standard_parameters = \
                    standard_parameters.parse('storages')
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

                specific_param["max. investment capacity"] = \
                    storage_parameters["thermal"][1]
                specific_param["periodical costs"] = \
                    storage_parameters["thermal"][2] / \
                    storage_parameters["thermal"][0]
                specific_param["periodical constraint costs"] = \
                    storage_parameters["thermal"][3] / \
                    storage_parameters["thermal"][0]
                specific_param["variable output costs"] = \
                    storage_parameters["thermal"][4] / \
                    storage_parameters["thermal"][0]
                # produce a pandas series out of the dict above due to easier
                # appending
                storage_series = pd.Series(specific_param)
                sheets["storages"] = \
                    sheets["storages"].append(storage_series,
                                              ignore_index=True)
            if transformer_parameters["gasheating"][0] > 0:
                if str(cluster) + "_heat_bus" not in sheets["buses"].index:
                    create_standard_parameter_bus(
                        label=str(cluster) + "_heat_bus",
                        bus_type='building_heat_bus',
                        standard_parameters=standard_parameters)
                    sheets["buses"].set_index("label", inplace=True,
                                              drop=False)
            if transformer_parameters["electric_heating"][0] > 0 \
                    or transformer_parameters["ashp"][0] > 0 \
                    or transformer_parameters["gchp"][0] > 0:
                if str(cluster) + "_heat_bus" not in sheets["buses"].index:
                    # building heat bus
                    create_standard_parameter_bus(
                        label=str(cluster) + "_heat_bus",
                        bus_type='building_heat_bus',
                        standard_parameters=standard_parameters)
                    sheets["buses"].set_index("label", inplace=True,
                                              drop=False)

            for i in sink_parameters[3]:
                create_standard_parameter_link(
                    label=str(i[0]) + "_" + str(i[1])
                          + "_heat_building_link",
                    bus_1=str(cluster) + "_heat_bus",
                    bus_2=str(i[1]),
                    link_type="building_hp_elec_link",
                    standard_parameters=standard_parameters)

    buses = sheets["buses"].copy()
    # buses = buses.drop(index="")
    # buses.set_index("label", inplace=True, drop=False)
    for i, j in buses.iterrows():
        if heat_buses_gchps:
            if str(j["label"][:9]) in heat_buses_gchps:
                sheets["buses"] = sheets["buses"].drop(index=j["label"])


def urban_district_upscaling_pre_processing(pre_scenario: str,
                                            standard_parameter_path: str,
                                            output_scenario: str,
                                            plain_sheet: str,
                                            clustering: bool):
    """
        TODO DOCSTRING TEXT

        :param pre_scenario: path of the pre_scenario file
        :type pre_scenario: str
        :param standard_parameter_path: path of the standard_parameter
                                        file
        :type standard_parameter_path: str
        :param output_scenario: path to which the scenario should be
                                created
        :type output_scenario: str
        :param plain_sheet: path to plain sheet file (holding structure)
        :type plain_sheet: str
        :param clustering: boolean for decision rather the buildings are
                           clustered spatially
        :tpye clustering: bool
    """

    print('Creating scenario sheet...')
    # loading typical scenario structure from plain sheet
    global sheets
    sheets = {}
    columns = {}
    plain_sheet_pd = pd.ExcelFile(plain_sheet)
    sheet_names = plain_sheet_pd.sheet_names
    for i in range(1, len(sheet_names)):
        columns[sheet_names[i]] = plain_sheet_pd.parse(sheet_names[i]).keys()
    worksheets = [column for column in columns.keys()]
    for sheet in worksheets:
        sheets_units = {}
        sheets.update({sheet: pd.DataFrame(columns=(columns[sheet]))})
        units = next(plain_sheet_pd.parse(sheet).iterrows())[1]
        for unit in units.keys():
            sheets_units.update({unit: units[unit]})
        sheets[sheet] = sheets[sheet].append(pd.Series(data=sheets_units),
                                             ignore_index=True)
    # load standard parameters from standard parameter file
    standard_parameters = pd.ExcelFile(standard_parameter_path)
    # import the sheet which is filled by the user
    pre_scenario_pd = pd.ExcelFile(pre_scenario)
    tool = pre_scenario_pd.parse("tool")
    parcel = pre_scenario_pd.parse("parcel")
    central = pre_scenario_pd.parse("central")
    # create central components
    central_comp(central, standard_parameters)
    # set variable for central heating / electricity if activated to
    # decide rather a house can be connected to the central heat
    # network / central electricity network or not
    central_heating_network = False
    central_electricity_network = False
    p2g_link = False
    # update the values regarding the values given in central sheet
    for i, j in central.iterrows():
        if j['heat_link'] in ['Yes', 'yes', 1]:
            central_heating_network = True
        if j['electricity_bus'] in ['Yes', 'yes', 1]:
            central_electricity_network = True
        if j['power_to_gas'] in ['Yes', 'yes', 1]:
            p2g_link = True

    # create GCHPs parcel wise
    gchps = {}
    ping = 0
    for num, parcel in parcel.iterrows():
        ping += 1
        for num_inner, building in tool.iterrows():
            if building["active"]:
                if building["gchp"] not in ["No", "no", 0]:
                    if parcel['ID parcel'] == building["parcel"]:
                        gchps.update({
                            parcel['ID parcel'][-9:]:
                                parcel['gchp area (m²)']})
    # create gchp relevant components
    for gchp in gchps:
        create_gchp(parcel_id=gchp, area=gchps[gchp],
                    standard_parameters=standard_parameters)
        create_standard_parameter_bus(label=gchp + "_hp_elec_bus",
                                      bus_type="building_hp_electricity_bus",
                                      standard_parameters=standard_parameters)
        create_standard_parameter_bus(label=gchp + "_heat_bus",
                                      bus_type="building_heat_bus",
                                      standard_parameters=standard_parameters)

    for num, building in tool.iterrows():
        if building["active"]:
            # foreach building the three necessary buses will be created
            pv_bool = False
            for roof_num in range(1, 29):
                if building['st or pv %1d' % roof_num] == "pv&st":
                    pv_bool = True
            create_buses(
                building_id=building['label'],
                pv_bus=pv_bool,
                building_type=building["building type"],
                hp_elec_bus=True if
                (building['parcel'] != 0
                 and building["gchp"] not in ["No", "no", 0])
                or building['ashp'] not in ["No", "no", 0] else False,
                central_elec_bus=central_electricity_network,
                gchp=True if building['parcel'] != 0 else False,
                gchp_heat_bus=(building['parcel'][-9:] + "_heat_bus")
                if (building['parcel'] != 0
                    and building['parcel'][-9:] in gchps) else None,
                gchp_elec_bus=(building['parcel'][-9:] + "_hp_elec_bus")
                if (building['parcel'] != 0
                    and building['parcel'][-9:] in gchps) else None,
                standard_parameters=standard_parameters)

            create_sinks(sink_id=building['label'],
                         building_type=building['building type'],
                         units=building['units'],
                         occupants=building['occupants per unit'],
                         yoc=building['year of construction'],
                         area=building['living space'] * building['floors'],
                         standard_parameters=standard_parameters,
                         latitude=building["latitude"],
                         longitude=building["longitude"],
                         dh=central_heating_network)

            create_building_insulation(
                building_id=building['label'],
                standard_parameters=standard_parameters,
                yoc=building['year of construction'],
                area_window=building["windows"],
                area_wall=building["walls_wo_windows"],
                area_roof=building["roof area"],
                roof_type=building["rooftype"])

            # Define PV Standard-Parameters
            sources_standard_parameters = standard_parameters.parse('sources')
            sources_standard_parameters.set_index('comment', inplace=True)
            pv_standard_parameters = \
                sources_standard_parameters.loc['fixed photovoltaic source']

            # Define solar thermal Standard-Parameters
            st_stan_param = \
                sources_standard_parameters.loc['solar_thermal_collector']

            # create pv-sources and solar thermal-sources including area
            # competition
            for roof_num in range(1, 29):
                if building['roof area (m²) %1d' % roof_num]:
                    plant_id = str(roof_num)
                    if building['st or pv %1d' % roof_num] == "pv&st":
                        create_pv_source(
                            building_id=building['label'],
                            plant_id=plant_id,
                            azimuth=building['azimuth (°) %1d' % roof_num],
                            tilt=building['surface tilt (°) %1d'
                                          % roof_num],
                            area=building['roof area (m²) %1d' % roof_num],
                            latitude=building['latitude'],
                            longitude=building['longitude'],
                            pv_standard_parameters=pv_standard_parameters)
                    if (building['st or pv %1d' % roof_num] == "st"
                        or building['st or pv %1d' % roof_num] == "pv&st") \
                            and building["building type"] != "0":
                        create_solarthermal_source(
                            building_id=building['label'],
                            plant_id=plant_id,
                            azimuth=building['azimuth (°) %1d' % roof_num],
                            tilt=building['surface tilt (°) %1d'
                                          % roof_num],
                            area=building['roof area (m²) %1d' % roof_num],
                            latitude=building['latitude'],
                            longitude=building['longitude'],
                            solarthermal_standard_parameters=st_stan_param)
                    if building['st or pv %1d' % roof_num] == "pv&st" \
                            and building["building type"] != "0" \
                            and clustering == False:
                        create_competition_constraint(
                            component1=(building['label'] + '_'
                                        + plant_id + '_pv_source'),
                            factor1=1 / pv_standard_parameters[
                                'Capacity per Area (kW/m2)'],
                            component2=(building['label'] + '_' + plant_id
                                        + '_solarthermal_source'),
                            factor2=1 / st_stan_param[
                                'Capacity per Area (kW/m2)'],
                            limit=building['roof area (m²) %1d'
                                           % roof_num])

            # creates air source heat-pumps
            if building['ashp'] in ['Yes', 'yes', 1]:
                create_ashp(building_id=building['label'],
                            standard_parameters=standard_parameters)

            # creates gasheating-system
            if building['gas heating'] in ['Yes', 'yes', 1]:
                create_gas_heating(building_id=building['label'],
                                   building_type=building['building type'],
                                   standard_parameters=standard_parameters)

                # natural gas connection link to p2g-ng-bus
                if p2g_link:
                    create_standard_parameter_link(
                        label='central_naturalgas_' + building['label']
                              + 'link',
                        bus_1='central_naturalgas_bus',
                        bus_2=building['label'] + '_gas_bus',
                        link_type='central_naturalgas_building_link',
                        standard_parameters=standard_parameters)

            # creates electric heating-system
            if building['electric heating'] in ['yes', 'Yes', 1]:
                create_electric_heating(
                    building_id=building['label'],
                    standard_parameters=standard_parameters)

            # battery storage
            if building['battery storage'] in ['Yes', 'yes', 1]:
                create_battery(building_id=building['label'],
                               standard_parameters=standard_parameters,
                               storage_type="building")
            if building['thermal storage'] in ['Yes', 'yes', 1]:
                create_thermal_storage(building_id=building['label'],
                                       standard_parameters=standard_parameters,
                                       storage_type="building")

            print(str(building['label'])
                  + ' subsystem added to scenario sheet.')

    # add general energy system information to "energysystem"-sheet
    copy_standard_parameter_sheet(sheet_tbc='energysystem',
                                  standard_parameters=standard_parameters)

    # adds weather data to "weather data"-sheet
    copy_standard_parameter_sheet(sheet_tbc='weather data',
                                  standard_parameters=standard_parameters)

    # adds weather data to "weather data"-sheet
    copy_standard_parameter_sheet(sheet_tbc='time series',
                                  standard_parameters=standard_parameters)

    # adds road sections to "road sections"-sheet
    copy_standard_parameter_sheet(sheet_tbc='road sections',
                                  standard_parameters=standard_parameters)

    if clustering:
        clustering_method(tool, standard_parameters, worksheets, central_electricity_network)
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
    urban_district_upscaling_pre_processing(
        pre_scenario=(os.path.dirname(__file__)
                      + r"/pre_scenario_struenkede_districtsP_20211105.xlsx"),
        standard_parameter_path=(os.path.dirname(__file__)
                                 + r"/standard_parameters.xlsx"),
        output_scenario=os.path.dirname(__file__) + r"/test_scenario.xlsx",
        plain_sheet=os.path.dirname(__file__) + r'/plain_scenario.xlsx',
        clustering=True)