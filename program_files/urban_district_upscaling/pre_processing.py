import xlsxwriter
import pandas as pd
import os
import program_files.urban_district_upscaling.clustering as clustering_py
from program_files.urban_district_upscaling.components \
    import Sink, Source, Storage, Transformer


def append_component(sheet: str, comp_parameter: dict):
    """
        :param sheet:
        :type sheet: str
        :param comp_parameter:
        :type comp_parameter: dict
    """
    series = pd.Series(comp_parameter)
    sheets[sheet] = pd.concat([sheets[sheet], pd.DataFrame([series])])


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


def create_standard_parameter_comp(specific_param: dict,
                                   standard_parameters,
                                   type,
                                   index,
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
        standard_parameters, standard_param_name, type, index)
    # insert standard parameters in the components dataset (dict)
    for i in range(len(standard_keys)):
        specific_param[standard_keys[i]] = standard_param[standard_keys[i]]
    # appends the new created component to storages sheet
    append_component(type, specific_param)


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
        Storage.create_thermal_storage(
            building_id="central", standard_parameters=standard_parameters,
            storage_type="central", bus=bus)
    # power to gas system
    if type == 'power_to_gas':
        create_power_to_gas_system(standard_parameters=standard_parameters,
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
            # TODO only two central heat buses implemented yet
            for num in range(1, 3):
                if j["heat_input_{}".format(str(num))] in ['yes', 'Yes', 1]:
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

        # central battery storage
        if j['battery_storage'] in ['yes', 'Yes', 1]:
            Storage. create_battery(
                building_id="central", standard_parameters=standard_parameters,
                storage_type="central")


def create_power_to_gas_system(standard_parameters, bus):
    """
        TODO DOCSTRING TEXT

        :param standard_parameters: pandas Dataframe holding the
                   information imported from the standard parameter file
        :type standard_parameters: pd.Dataframe
        :param bus:
        :type bus:
    """
    if "central_h2_bus" not in sheets["buses"]["label"].to_list():
        # h2 bus
        create_standard_parameter_bus(label="central_h2_bus",
                                      bus_type="central_h2_bus",
                                      standard_parameters=standard_parameters)
    if "central_naturalgas_bus" not in sheets["buses"]["label"].to_list():
        # natural gas bus
        create_standard_parameter_bus(label="central_naturalgas_bus",
                                      bus_type="central_naturalgas_bus",
                                      standard_parameters=standard_parameters)
    # transformer
    transformer_dict = {
        "central_electrolysis_transformer":
            ['central_electrolysis_transformer', "central_electricity_bus",
             "central_h2_bus", "None"],
        "central_methanization_transformer":
            ['central_methanization_transformer', "central_h2_bus",
             "central_naturalgas_bus", "None"],
        "central_fuelcell_transformer":
            ['central_fuelcell_transformer', "central_h2_bus",
             "central_electricity_bus", bus]}
    
    for transformer in transformer_dict:
        create_standard_parameter_comp(
                specific_param={"label": transformer_dict[transformer][0],
                                "comment": 'automatically_created',
                                "input": transformer_dict[transformer][1],
                                "output": transformer_dict[transformer][2],
                                "output2": transformer_dict[transformer][3]},
                standard_parameters=standard_parameters,
                type="transformers",
                index="comment",
                standard_param_name=transformer)
        
    # storages
    storage_dict = {
        "central_h2_storage": ["central_h2_storage", "central_h2_bus"],
        "central_naturalgas_storage": ["central_naturalgas_storage",
                                       "central_naturalgas_bus"]}
    for storage in storage_dict:
        create_standard_parameter_comp(
                specific_param={"label": storage_dict[storage][0],
                                "comment": 'automatically_created',
                                "bus": storage_dict[storage][1]},
                standard_parameters=standard_parameters,
                type="transformers",
                index="comment",
                standard_param_name=storage)

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
    
    create_standard_parameter_comp(
        specific_param={'label': 'central_biomass_transformer',
                        'comment': 'automatically_created',
                        'input': "central_biomass_bus",
                        'output': output,
                        'output2': 'None'},
        standard_parameters=standard_parameters,
        type="transformers",
        index="comment",
        standard_param_name="central_biomass_transformer")


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
        if "central_heatpump_elec_bus" not in sheets["buses"]["label"].to_list():
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
    
    create_standard_parameter_comp(
        specific_param={'label': 'central_' + specification + '_transformer',
                        'comment': 'automatically_created',
                        'input': "central_heatpump_elec_bus",
                        'output': output,
                        'output2': 'None'},
        standard_parameters=standard_parameters,
        type="transformers",
        index="comment",
        standard_param_name='central_' + specification + '_transformer')


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

    create_standard_parameter_comp(
        specific_param={
            'label': "central_" + gastype + '_heating_plant_transformer',
            'input': "central_" + gastype + "_plant_bus",
            'output': output,
            'output2': 'None'},
        standard_parameters=standard_parameters,
        type="transformers",
        index="comment",
        standard_param_name="central_naturalgas_heating_plant_transformer")


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

    create_standard_parameter_comp(
        specific_param={'label': 'central_' + gastype + '_chp_transformer',
                        'input': "central_chp_" + gastype + "_bus",
                        'output': "central_chp_" + gastype + "_elec_bus",
                        'output2': output},
        standard_parameters=standard_parameters,
        type="transformers",
        index="comment",
        standard_param_name="central_" + gastype + "_chp")


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
                                            clustering: bool,
                                            clustering_dh: bool):
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
        :param clustering_dh: boolean for decision rather the district
            heating connection will be clustered cluster_id wise
        :type clustering_dh: bool
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
        for num_inner, building in tool[tool["active"] == 1].iterrows():
            if building["gchp"] not in ["No", "no", 0]:
                if parcel['ID parcel'] == building["parcel"]:
                    gchps.update({parcel['ID parcel'][-9:]:
                                    parcel['gchp area (m²)']})
    # create gchp relevant components
    for gchp in gchps:
        Transformer.create_gchp(parcel_id=gchp, area=gchps[gchp],
                                standard_parameters=standard_parameters)
        create_standard_parameter_bus(label=gchp + "_hp_elec_bus",
                                      bus_type="building_hp_electricity_bus",
                                      standard_parameters=standard_parameters)
        create_standard_parameter_bus(label=gchp + "_heat_bus",
                                      bus_type="building_heat_bus",
                                      standard_parameters=standard_parameters)

    for num, building in tool[tool["active"] == 1].iterrows():
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

        Sink.create_sinks(sink_id=building['label'],
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
        
        # create sources
        Source.create_sources(building=building,
                              standard_parameters=standard_parameters,
                              clustering=clustering)

        

        # creates air source heat-pumps
        if building['ashp'] in ['Yes', 'yes', 1]:
            Transformer.create_ashp(building_id=building['label'],
                                    standard_parameters=standard_parameters)

        # creates gasheating-system
        if building['gas heating'] in ['Yes', 'yes', 1]:
            Transformer.create_gas_heating(
                building_id=building['label'],
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
            Transformer.create_electric_heating(
                building_id=building['label'],
                standard_parameters=standard_parameters)

        # battery storage
        if building['battery storage'] in ['Yes', 'yes', 1]:
            Storage.create_battery(
                building_id=building['label'],
                standard_parameters=standard_parameters,
                storage_type="building")
        # thermal storage
        if building['thermal storage'] in ['Yes', 'yes', 1]:
            Storage.create_thermal_storage(
                building_id=building['label'],
                standard_parameters=standard_parameters,
                storage_type="building")

        print(str(building['label'])
              + ' subsystem added to scenario sheet.')
    for sheet_tbc in ["energysystem", "weather data", "time series",
                      "district heating"]:
        sheets[sheet_tbc] = standard_parameters.parse(sheet_tbc)

    if clustering:
        clustering_py.clustering_method(tool, standard_parameters, worksheets,
                                        sheets, central_electricity_network,
                                        clustering_dh)
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
