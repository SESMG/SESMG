import xlsxwriter
import pandas as pd
import os
import program_files.urban_district_upscaling.clustering as clustering_py


def append_component(sheet: str, comp_parameter: dict):
    """
        :param sheet:
        :type sheet: str
        :param comp_parameter:
        :type comp_parameter: dict
    """
    series = pd.Series(comp_parameter)
    sheets[sheet] = sheets[sheet].append(series, ignore_index=True)


def read_standard_parameters(standard_parameters, name, param_type, index):
    """
        searches the right entry within the standard parameter sheet

        :param standard_parameters: pandas Dataframe containing the \
            technology specific parameters
        :type standard_parameters: pandas.DataFrame
        :param name: component's name
        :type name: str
        :param param_type: determines the technology type
        :type param_type: str
        :param index: defines on which column the index of the parsed \
            Dataframe will be set in order to locate the component's \
            name specific row
        :returns standard_param: technology specific parameters of name
        :rtype standard_param: pandas.Dataframe
        :returns standard_keys: technology specific keys of name
        :rtype standard_keys: list
    """
    # get the param_type sheet from standard parameters
    standard_param_df = standard_parameters.parse(param_type)
    # reset the dataframes index to the index variable set in args
    standard_param_df.set_index(index, inplace=True)
    # locate the row labeled name
    standard_param = standard_param_df.loc[name]
    # get the keys of the located row
    standard_keys = standard_param.keys().tolist()
    # return parameters and keys
    return standard_param, standard_keys


def create_standard_parameter_bus(label: str, bus_type: str,
                                  standard_parameters, dh=None, lat=None,
                                  lon=None):
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
    standard_param, standard_keys = \
        read_standard_parameters(standard_parameters, bus_type, "buses",
                                 'bus_type')
    # insert standard parameters in the components dataset (dict)
    for i in range(len(standard_keys)):
        bus_dict[standard_keys[i]] = standard_param[standard_keys[i]]
    # defines rather a district heating connection is possible
    if lat is not None:
        bus_dict.update({"district heating conn.": dh, "lat": lat, "lon": lon})
    # appends the new created component to buses sheet
    append_component("buses", bus_dict)


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
    # define individual values
    parameter_dict = {'label': label, 'bus1': bus_1, 'bus2': bus_2}
    # extracts the link specific standard values from the
    # standard_parameters dataset
    standard_param, standard_keys = \
        read_standard_parameters(standard_parameters, link_type, "links",
                                 'link_type')
    # insert standard parameters in the components dataset (dict)
    for i in range(len(standard_keys)):
        parameter_dict[standard_keys[i]] = standard_param[standard_keys[i]]
    # appends the new created component to links sheet
    append_component("links", parameter_dict)


def create_standard_parameter_sink(sink_type: str, label: str,
                                   sink_input: str, annual_demand: int,
                                   standard_parameters):
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
    # define individual values
    sink_dict = {'label': label, 'input': sink_input,
                 'annual demand': annual_demand}
    # extracts the sink specific standard values from the
    # standard_parameters dataset
    standard_param, standard_keys = \
        read_standard_parameters(standard_parameters, sink_type, "sinks",
                                 'sink_type')
    # insert standard parameters in the components dataset (dict)
    for i in range(len(standard_keys)):
        sink_dict[standard_keys[i]] = standard_param[standard_keys[i]]
    # appends the new created component to sinks sheet
    append_component("sinks", sink_dict)


def create_standard_parameter_transformer(specific_param: dict,
                                          standard_parameters,
                                          standard_param_name):
    """
        creates a transformer with standard_parameters, based on the
        standard parameters given in the "standard_parameters" dataset
        and adds it to the "sheets"-output dataset.

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
    # extracts the transformer specific standard values from the
    # standard_parameters dataset
    standard_param, standard_keys = read_standard_parameters(
        standard_parameters, standard_param_name, "transformers", "comment")
    # insert standard parameters in the components dataset (dict)
    for i in range(len(standard_keys)):
        specific_param[standard_keys[i]] = standard_param[standard_keys[i]]
    # appends the new created component to transformers sheet
    append_component("transformers", specific_param)


def create_standard_parameter_storage(specific_param: dict,
                                      standard_parameters,
                                      standard_param_name):
    """
        creates a storage with standard_parameters, based on the
        standard parameters given in the "standard_parameters" dataset
        and adds it to the "sheets"-output dataset.

        :param specific_param: dictionary holding the storage specific
                               parameters (e.g. ng_storage specific, ...)
        :type specific_param: dict
        :param standard_parameters: pandas Dataframe holding the
                   information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
        :param standard_param_name: string defining the storage type
                                    (e.g. central_naturalgas_storage,...)
                                    to locate the right standard parameters
        :type standard_param_name: str
    """
    # extracts the storage specific standard values from the
    # standard_parameters dataset
    standard_param, standard_keys = read_standard_parameters(
        standard_parameters, standard_param_name, "storages", "comment")
    # insert standard parameters in the components dataset (dict)
    for i in range(len(standard_keys)):
        specific_param[standard_keys[i]] = standard_param[standard_keys[i]]
    # appends the new created component to storages sheet
    append_component("storages", specific_param)


def create_central_heat_component(type, bus, standard_parameters,
                                  central_elec_bus, central_chp):
    """
        In this method, all heat supply systems are calculated for a
        heat input into the district heat network.
        
        :param type: defines the component type
        :type type: str
        :param bus: defines the output bus which is one of the heat
            input buses of the district heating network
        :type bus: str
        :param standard_parameters:
        :param central_elec_bus:
        :param central_chp:
        :return:
    """
    if type == 'naturalgas_chp':
        create_central_chp(gastype='naturalgas',
                           standard_parameters=standard_parameters,
                           output=bus,
                           central_elec_bus=central_elec_bus)
    if type == 'biogas_chp':
        create_central_chp(gastype='biogas',
                           standard_parameters=standard_parameters,
                           output=bus,
                           central_elec_bus=central_elec_bus)
    # central natural gas heating plant
    if type == 'naturalgas_heating_plant':
        create_central_gas_heating_transformer(
            gastype='naturalgas',
            standard_parameters=standard_parameters,
            output=bus,
            central_chp=central_chp)
    # central swhp
    central_heatpump_indicator = 0
    if type == 'swhp_transformer':
        create_central_heatpump(
            standard_parameters=standard_parameters,
            specification='swhp',
            create_bus=True if central_heatpump_indicator == 0 else False,
            output=bus, central_elec_bus=central_elec_bus)
        central_heatpump_indicator += 1
    # central ashp
    if type == 'ashp_transformer':
        create_central_heatpump(
            standard_parameters=standard_parameters,
            specification='ashp',
            create_bus=True if central_heatpump_indicator == 0 else False,
            central_elec_bus=central_elec_bus,
            output=bus)
        central_heatpump_indicator += 1
    # central biomass plant
    if type == 'biomass_plant':
        create_central_biomass_plant(
            standard_parameters=standard_parameters,
            output=bus)
    if type == 'thermal_storage':
        create_thermal_storage(building_id="central",
                               standard_parameters=standard_parameters,
                               storage_type="central",
                               bus=bus)


def central_comp(central, standard_parameters):
    """
        In this method, the central components of the energy system are
        added to the scenario, first checking if a heating network is
        foreseen and if so, creating the feeding components, and then
        creating Power to Gas and battery storage if defined in the pre
        scenario.

        :param central: pandas Dataframe holding the information from the \
                prescenario file "central" sheet
        :type central: pd.Dataframe
        :param standard_parameters: pandas Dataframe holding the \
               information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
    """
    for i, j in central.iterrows():

        # creation of the bus for the local power exchange
        if j['electricity_bus'] in ['Yes', 'yes', 1]:
            create_standard_parameter_bus(
                label='central_electricity_bus',
                bus_type="central_electricity_bus",
                standard_parameters=standard_parameters)

        # central heat supply
        if j["central_heat_supply"] in ['yes', 'Yes', 1]:
            for num in range(1, 3):
                print(num)
                if j["heat_input_{}".format(str(num))] in ['yes', 'Yes', 1]:
                    print(num)
                    # create bus which would be used as producer bus in
                    # district heating network
                    create_standard_parameter_bus(
                        label='central_heat_input{}_bus'.format(num),
                        bus_type="central_heat_input_bus",
                        standard_parameters=standard_parameters,
                        dh="dh-system",
                        lat=j["lat.heat_input-{}".format(num)],
                        lon=j["lon.heat_input-{}".format(num)])
                    # create components connected to the producer bus
                    for comp in \
                            str(j["connected_components_heat_input{}".format(num)
                                ]).split(","):
                        if j[comp] in ['yes', 'Yes', 1]:
                            create_central_heat_component(
                                comp, 'central_heat_input{}_bus'.format(num),
                                standard_parameters,
                                True if j['electricity_bus'] in
                                    ['Yes', 'yes', 1] else False,
                                True if j['naturalgas_chp'] in
                                    ['Yes', 'yes', 1] else False)

        # power to gas system
        if j['power_to_gas'] in ['yes', 'Yes', 1]:
            create_power_to_gas_system(standard_parameters=standard_parameters)

        # central battery storage
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


def create_central_biomass_plant(standard_parameters, output):
    """
        This method creates a central biomass plant with the data given
        in the standard parameter sheet.

        :param standard_parameters: pandas Dataframe holding the
                   information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
        :param output: string containing the output bus label
        :type output: str
    """
    # biomass bus
    create_standard_parameter_bus(label="central_biomass_bus",
                                  bus_type="central_biomass_bus",
                                  standard_parameters=standard_parameters)
    # define individual values
    parameter_dict = {'label': 'central_biomass_transformer',
                      'comment': 'automatically_created',
                      'input': "central_biomass_bus",
                      'output': output,
                      'output2': 'None'}

    # extracts the transformer specific standard values from the
    # standard_parameters dataset
    standard_param, standard_keys = \
        read_standard_parameters(standard_parameters,
                                 'central_biomass_transformer', "transformers",
                                 "comment")
    # insert standard parameters in the components dataset (dict)
    for i in range(len(standard_keys)):
        parameter_dict[standard_keys[i]] = standard_param[standard_keys[i]]
    # appends the new created component to transformers sheet
    append_component("transformers", parameter_dict)


def create_central_heatpump(standard_parameters, specification, create_bus,
                            central_elec_bus, output):
    """
        In this method, a central heatpump unit with specified gas type
        is created, for this purpose the necessary data set is obtained
        from the standard parameter sheet, and the component is attached
        to the transformers sheet.
        
        :param standard_parameters: pandas Dataframe holding the
                                    information imported from the
                                    standard parameter file
        :type standard_parameters: pandas Dataframe
        :param specification: string giving the information which type
                              of heatpump shall be added.
        :type specification: str
        :param create_bus: indicates whether a central heatpump
                           electricity bus and further parameters shall
                           be created or not.
        :param central_elec_bus: indicates whether a central elec exists
        :type central_elec_bus: bool
        :return: bool
    """

    if create_bus:
        create_standard_parameter_bus(
            label="central_heatpump_elec_bus",
            bus_type="central_heatpump_electricity_bus",
            standard_parameters=standard_parameters)
        if central_elec_bus:
            # connection to central electricity bus
            create_standard_parameter_link(
                label="central_heatpump_electricity_link",
                bus_1="central_electricity_bus",
                bus_2="central_heatpump_elec_bus",
                link_type="building_central_building_link",
                standard_parameters=standard_parameters)
            
    # define individual values
    parameter_dict = {
        'label': 'central_' + specification + '_transformer',
        'comment': 'automatically_created',
        'input': "central_heatpump_elec_bus",
        'output': output,
        'output2': 'None'}
    # extracts the transformer specific standard values from the
    # standard_parameters dataset
    standard_param, standard_keys = read_standard_parameters(
            standard_parameters, 'central_' + specification + '_transformer',
            "transformers", "comment")
    # insert standard parameters in the components dataset (dict)
    for i in range(len(standard_keys)):
        parameter_dict[standard_keys[i]] = standard_param[standard_keys[i]]
    # appends the new created component to transformers sheet
    append_component("transformers", parameter_dict)


def create_central_gas_heating_transformer(gastype, standard_parameters,
                                           output, central_chp):
    """
        In this method, a central heating plant unit with specified gas
        type is created, for this purpose the necessary data set is
        obtained from the standard parameter sheet, and the component is
        attached to the transformers sheet.

        :param gastype: string which defines rather naturalgas or biogas
                        is used
        :type gastype: str
        :param standard_parameters: pandas Dataframe holding the
                   information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
        :param output: str containing the transformers output
        :type output: str
        :param central_chp: defines rather a central chp is investable
        :type central_chp: bool
    """

    # plant gas bus
    create_standard_parameter_bus(label="central_" + gastype + "_plant_bus",
                                  bus_type="central_chp_naturalgas_bus",
                                  standard_parameters=standard_parameters)
    
    if central_chp:
        # connection to central electricity bus
        create_standard_parameter_link(
            label="heating_plant_" + gastype + "_link",
            bus_1="central_chp_naturalgas_bus",
            bus_2="central_" + gastype + "_plant_bus",
            link_type="central_naturalgas_building_link",
            standard_parameters=standard_parameters)
    # define individual values
    heating_plant_dict = \
        {'label': "central_" + gastype + '_heating_plant_transformer',
         'input': "central_" + gastype + "_plant_bus",
         'output': output,
         'output2': 'None'}
    # extracts the transformer specific standard values from the
    # standard_parameters dataset
    heating_plant_parameter, heating_plant_standard_keys = \
        read_standard_parameters(
                standard_parameters,
                'central_naturalgas_heating_plant_transformer', "transformers",
                "comment")
    # insert standard parameters in the components dataset (dict)
    for i in range(len(heating_plant_standard_keys)):
        heating_plant_dict[heating_plant_standard_keys[i]] = \
            heating_plant_parameter[heating_plant_standard_keys[i]]
    # appends the new created component to transformers sheet
    append_component("transformers", heating_plant_dict)


def create_central_chp(gastype, standard_parameters, output, central_elec_bus):
    """
        In this method, a central CHP unit with specified gas type is
        created, for this purpose the necessary data set is obtained
        from the standard parameter sheet, and the component is attached
         to the transformers sheet.

        :param gastype: string which defines rather naturalgas or \
            biogas is used
        :type gastype: str
        :param standard_parameters: pandas Dataframe holding the
            information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
        :param output: string containing the heat output bus name
        :type output: str
        :param central_elec_bus: determines if the central power \
            exchange exists
    """
    # chp gas bus
    create_standard_parameter_bus(label="central_chp_" + gastype + "_bus",
                                  bus_type="central_chp_" + gastype + "_bus",
                                  standard_parameters=standard_parameters)

    # chp electricity bus
    create_standard_parameter_bus(
        label="central_chp_" + gastype + "_elec_bus",
        bus_type="central_chp_" + gastype + "_electricity_bus",
        standard_parameters=standard_parameters)
    
    if central_elec_bus:
        # connection to central electricity bus
        create_standard_parameter_link(
            label="central_chp_" + gastype + "_elec_central_link",
            bus_1="central_chp_" + gastype + "_elec_bus",
            bus_2="central_electricity_bus",
            link_type="central_chp_elec_central_link",
            standard_parameters=standard_parameters)
    # define individual values
    chp_central_dict = {'label': 'central_' + gastype + '_chp_transformer',
                        'input': "central_chp_" + gastype + "_bus",
                        'output': "central_chp_" + gastype + "_elec_bus",
                        'output2': output
                        }
    # extracts the transformer specific standard values from the
    # standard_parameters dataset
    chp_standard_parameters, chp_parameters_keys = \
        read_standard_parameters(standard_parameters,
                                 "central_" + gastype + "_chp", "transformers",
                                 "comment")
    # insert standard parameters in the components dataset (dict)
    for i in range(len(chp_parameters_keys)):
        chp_central_dict[chp_parameters_keys[i]] = \
            chp_standard_parameters[chp_parameters_keys[i]]
    # appends the new created component to transformers sheet
    append_component("transformers", chp_central_dict)


def create_buses(building_id: str, pv_bus: bool, building_type: str,
                 hp_elec_bus: bool, central_elec_bus: bool, gchp: bool,
                 standard_parameters, gchp_heat_bus=None, gchp_elec_bus=None,
                 lat=None, lon=None):
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

    if building_type != "0" and building_type != 0:
        # house heat bus
        create_standard_parameter_bus(label=str(building_id) + "_heat_bus",
                                      bus_type='building_heat_bus',
                                      standard_parameters=standard_parameters,
                                      dh=1 if lat is not None else 0, lat=lat,
                                      lon=lon)

    if hp_elec_bus:
        # building hp electricity bus
        create_standard_parameter_bus(label=str(building_id) + "_hp_elec_bus",
                                      bus_type='building_hp_electricity_bus',
                                      standard_parameters=standard_parameters,
                                      dh=None)
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
                 occupants: int, yoc: str, area: int, standard_parameters):
    """
        TODO DOCSTRING
    """
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
            standard_parameters=standard_parameters)

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
                                       standard_parameters=standard_parameters)


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
    append_component("sources", pv_house_specific_dict)


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
    constraint_dict = {'component 1': component1, 'factor 1': factor1,
                       'component 2': component2, 'factor 2': factor2,
                       'limit': limit, 'active': 1}
    append_component("competition constraints", constraint_dict)


def create_gchp(parcel_id, area, standard_parameters):
    """
        Sets the specific parameters for a ground coupled heat pump
        system, and creates them afterwards.

        :param parcel_id: parcel label
        :type parcel_id: str
        :param area: parcel area which can be used for gchp anergy
        :type area: float
        :param standard_parameters: Dataframe holding gchp specific
                                    standard parameters
        :type standard_parameters: pd.Dataframe
    """
    standard_param, standard_keys = read_standard_parameters(
        standard_parameters, "building_gchp_transformer", "transformers", "comment")
    # TODO
    #probe_length = \
    #    transformers_standard_parameters.loc['building_gchp_transformer'][
    #        'length of the geoth. probe']
    #heat_extraction = \
    #    transformers_standard_parameters.loc['building_gchp_transformer'][
    #        'heat extraction']
    #min_bore_hole_area = \
    #    transformers_standard_parameters.loc['building_gchp_transformer'][
    #        'min. borehole area']

    parameter_dict = {'label': str(parcel_id) + '_gchp_transformer',
                      'comment': 'automatically_created',
                      'input': str(parcel_id) + '_hp_elec_bus',
                      'output': str(parcel_id) + '_heat_bus',
                      'output2': 'None',
                      'area': area,
                      'existing capacity': 0,
                      'min. investment capacity': 0}

    # read the gchp standards from standard_parameters.xlsx and append
    # them to the gchp_house_specific_dict
    for i in range(len(standard_keys)):
        parameter_dict[standard_keys[i]] = standard_param[standard_keys[i]]
    # produce a pandas series out of the dict above due to easier appending
    append_component("transformers", parameter_dict)


def create_ashp(building_id, standard_parameters):
    """
        Sets the specific parameters for an air source heatpump system,
        and creates them afterwards.

        :param building_id: building label
        :type building_id: str
        :param standard_parameters: Dataframe holding ashp specific
                                    standard parameters
        :type standard_parameters: pd.Dataframe
    """
    standard_param, standard_keys = read_standard_parameters(
        standard_parameters, "building_ashp_transformer", "transformers", "comment")

    parameter_dict = {'label': (str(building_id) + '_ashp_transformer'),
                      'comment': 'automatically_created',
                      'input': str(building_id) + '_hp_elec_bus',
                      'output': str(building_id) + '_heat_bus',
                      'output2': 'None',
                      'existing capacity': 0,
                      'min. investment capacity': 0}

    # read the ashp standards from standard_parameters.xlsx and append
    # them to the ashp_house_specific_dict
    for i in range(len(standard_keys)):
        parameter_dict[standard_keys[i]] = standard_param[standard_keys[i]]

    # produce a pandas series out of the dict above due to easier appending
    append_component("transformers", parameter_dict)


def create_gas_heating(building_id, building_type, standard_parameters):
    """
        Sets the specific parameters for a gas heating system,
        and creates them afterwards.

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

    create_standard_parameter_transformer(
        specific_param={'label': str(building_id) + '_gasheating_transformer',
                        'comment': 'automatically_created',
                        'input': str(building_id) + '_gas_bus',
                        'output': str(building_id) + '_heat_bus',
                        'output2': 'None'},
        standard_parameters=standard_parameters,
        standard_param_name='building_gasheating_transformer')


def create_electric_heating(building_id, standard_parameters):
    """
        Sets the specific parameters for an electric heating system,
        and creates them afterwards.

        :param building_id: building label
        :type building_id: str
        :param standard_parameters: Dataframe holding electric heating
                                    specific standard parameters
        :type standard_parameters: pd.Dataframe
    """
    standard_param, standard_keys = read_standard_parameters(
        standard_parameters, "building_electricheating_transformer",
        "transformers", "comment")

    # define individual electric_heating_parameters
    parameter_dict = \
        {'label': str(building_id) + '_electricheating_transformer',
         'comment': 'automatically_created',
         'input': str(building_id) + '_electricity_bus',
         'output': str(building_id) + '_heat_bus',
         'output2': 'None'}

    # read the electric heating standards from standard_parameters.xlsx
    # and append them to the  electric_heating_house_specific_dict
    for i in range(len(standard_keys)):
        parameter_dict[standard_keys[i]] = standard_param[standard_keys[i]]
    # produce a pandas series out of the dict above due to easier appending
    append_component("transformers", parameter_dict)


def create_battery(building_id: str, standard_parameters, storage_type: str):
    """
        Sets the specific parameters for a battery, and creates them
        afterwards.

        :param building_id: building label
        :type building_id: str
        :param standard_parameters: Dataframe holding battery
                                    specific standard parameters
        :type standard_parameters: pd.Dataframe
        :param storage_type:
        :type storage_type: str
    """
    create_standard_parameter_storage(
        specific_param={
            'label': str(building_id) + '_battery_storage',
            'comment': 'automatically_created',
            'bus': str(building_id) + '_electricity_bus'},
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
        :param bus:
        :type bus: str
    """
    create_standard_parameter_storage(
        specific_param={
            'label': str(building_id) + '_thermal_storage',
            'comment': 'automatically_created',
            'bus': str(building_id) + '_heat_bus' if bus is None else bus},
        standard_parameters=standard_parameters,
        standard_param_name=storage_type + '_thermal_storage')


def create_building_insulation(building_id: str, yoc: int, area_window: float,
                               area_wall: float, area_roof: float,
                               roof_type: str, standard_parameters):
    """
        In this method, the U-value potentials as well as the building
        year-dependent U-value of the insulation types are obtained from
        the standard parameters to create the insulation components in
        the scenario.

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
    insul_standard_param = standard_parameters.parse('insulation')
    insul_standard_param.set_index("year of construction", inplace=True)
    if int(yoc) <= 1918:  # TODO
        yoc = "<1918"
    u_values = {}
    for comp in ["roof", "outer wall", "window"]:
        u_values.update(
            {comp: [insul_standard_param.loc[yoc][comp],
                    insul_standard_param.loc["potential"][comp],
                    insul_standard_param.loc["periodical costs"][comp],
                    insul_standard_param.loc[
                        "periodical constraint costs"][comp]]})
        if comp == "roof":
            u_values[comp] \
             += [insul_standard_param.loc["potential flat"]["roof"],
                 insul_standard_param.loc["periodical costs flat"]["roof"],
                 insul_standard_param.loc["periodical constraint costs flat"]["roof"]]
    param_dict = {'comment': 'automatically_created',
                  'active': 1,
                  'sink': str(building_id) + "_heat_demand",
                  'temperature indoor': 20,
                  'heat limit temperature': 15}
    if area_window:
        window_dict = param_dict.copy()
        window_dict.update(
            {'label': str(building_id) + "_window",
             'U-value old': u_values["window"][0],
             'U-value new': u_values["window"][1],
             'area': area_window,
             'periodical costs': u_values["window"][2],
             'periodical constraint costs': u_values["window"][3]})
        append_component("insulation", window_dict)

    if area_wall:
        wall_dict = param_dict.copy()
        wall_dict.update(
            {'label': str(building_id) + "_wall",
             'U-value old': u_values["outer wall"][0],
             'U-value new': u_values["outer wall"][1],
             'area': area_wall,
             'periodical costs': u_values["outer wall"][2],
             'periodical constraint costs': u_values["outer wall"][3]})
        append_component("insulation", wall_dict)

    if area_roof:
        u_value_new = u_values["roof"][4 if roof_type == "flat roof" else 1]
        periodical_costs = \
            u_values["roof"][5 if roof_type == "flat roof" else 2]
        roof_dict = param_dict.copy()
        roof_dict.update(
            {'label': str(building_id) + "_roof",
             'U-value old': u_values["roof"][0],
             'U-value new': u_value_new,
             'area': area_roof,
             'periodical costs': periodical_costs,
             'periodical constraint costs': u_values["roof"][3 if roof_type != "flat roof" else 6]})
        append_component("insulation", roof_dict)


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
            not in sheets["links"].index \
            and (cluster + "pv_central") in sheets["links"].index:
        create_standard_parameter_link(
            cluster + "pv_" + cluster + "_electricity_link",
            bus_1=cluster + "_pv_bus",
            bus_2=cluster + "_electricity_bus",
            link_type="building_pv_central_link",
            standard_parameters=standard_parameters)
        sheets["links"].set_index("label", inplace=True,
                                  drop=False)


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
    # get keys from plain scenario
    plain_sheet_pd = pd.ExcelFile(plain_sheet)
    sheet_names = plain_sheet_pd.sheet_names
    for i in range(1, len(sheet_names)):
        columns[sheet_names[i]] = plain_sheet_pd.parse(sheet_names[i]).keys()
    # append worksheets' names to the list of worksheets
    worksheets = [column for column in columns.keys()]
    # get spreadsheet units from plain sheet
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
    # get the input sheets
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
        if j['central_heat_supply'] in ['Yes', 'yes', 1]:
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
                standard_parameters=standard_parameters,
                lat=building["latitude"], lon=building["longitude"])

            create_sinks(sink_id=building['label'],
                         building_type=building['building type'],
                         units=building['units'],
                         occupants=building['occupants per unit'],
                         yoc=building['year of construction'],
                         area=building['living space'] * building['floors'],
                         standard_parameters=standard_parameters)

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
                            and building["building type"] != "0" \
                            and building["building type"] != 0:
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
    for sheet_tbc in ["energysystem", "weather data", "time series",
                      "district heating"]:
        sheets[sheet_tbc] = standard_parameters.parse(sheet_tbc)

    if clustering:
        clustering_py.clustering_method(tool, standard_parameters, worksheets,
                                        sheets, central_electricity_network)
    # open the new excel file and add all the created components
    j = 0
    writer = pd.ExcelWriter(output_scenario, engine='xlsxwriter')

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
