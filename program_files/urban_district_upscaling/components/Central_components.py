"""
    Christian Klemm - christian.klemm@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
    Janik Budde - janik.budde@fh-muenster.de
"""
import pandas


def create_central_heat_component(
    label: str,
    comp_type: str,
    bus: str,
    exchange_buses: dict,
    sheets: dict,
    area: str,
    standard_parameters: pandas.ExcelFile,
    flow_temp: str,
) -> dict:
    """
        In this method, all heat supply systems are calculated for a
        heat input into the district heat network.
    
        :param label: defines the central component's label
        :type label: str
        :param comp_type: defines the component type
        :type comp_type: str
        :param bus: defines the output bus which is one of the heat
            input buses of the district heating network
        :type bus: str
        :param exchange_buses: defines rather the central exchange of the \
            specified energy is possible or not
        :type exchange_buses: dict
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param area: filled if a central gchp has to be created
        :type area: str
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        :param flow_temp: flow temperature of the central heating \
            system (district heating)
        :type flow_temp: str
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    from program_files import Storage

    # CHPs
    if comp_type in ["naturalgas_chp", "biogas_chp", "pellet_chp", "woodchips_chp"]:
        # check rather a central exchange of fuel type is possible
        if comp_type.split("_")[0] in exchange_buses:
            central_bus = exchange_buses[comp_type.split("_")[0] + "_exchange"]
        else:
            central_bus = False
        # create the central chp plant
        sheets = create_central_chp(
            label=label,
            fuel_type=comp_type.split("_")[0],
            output=bus,
            central_elec_bus=exchange_buses["electricity_exchange"],
            central_fuel_bus=central_bus,
            sheets=sheets,
            standard_parameters=standard_parameters,
        )

    # Heating plants
    if comp_type in [
        "naturalgas_heating_plant",
        "biogas_heating_plant",
        "pellet_heating_plant",
        "woodchips_heating_plant",
    ]:
        # check rather a central exchange of fuel type is possible
        if comp_type.split("_")[0] in exchange_buses:
            central_bus = exchange_buses[comp_type.split("_")[0] + "_exchange"]
        else:
            central_bus = False
        # create the central heating plant
        sheets = create_central_heating_transformer(
            label=label,
            fuel_type=comp_type.split("_")[0],
            output=bus,
            central_fuel_bus=central_bus,
            sheets=sheets,
            standard_parameters=standard_parameters,
        )

    # Heatpumps
    central_heatpump_indicator = 0
    if comp_type in ["swhp_transformer", "ashp_transformer", "gchp_transformer"]:
        # create heatpump
        sheets = create_central_heatpump(
            label=label,
            specification=comp_type.split("_")[0],
            create_bus=True if central_heatpump_indicator == 0 else False,
            output=bus,
            central_electricity_bus=exchange_buses["electricity_exchange"],
            sheets=sheets,
            area=area,
            standard_parameters=standard_parameters,
            flow_temp=flow_temp,
        )
        # increase indicator to prevent duplex bus creation
        central_heatpump_indicator += 1

    # create central thermal storage
    if comp_type == "thermal_storage":
        sheets = Storage.create_storage(
            building_id="central_" + label,
            storage_type="thermal",
            de_centralized="central",
            bus=bus,
            sheets=sheets,
            standard_parameters=standard_parameters,
        )

    # power to gas system
    if comp_type == "power_to_gas":
        sheets = create_power_to_gas_system(
            label=label,
            output=bus,
            sheets=sheets,
            standard_parameters=standard_parameters,
        )

    return sheets


def central_comp(
    central: pandas.DataFrame,
    true_bools: list,
    sheets: dict,
    standard_parameters: pandas.ExcelFile,
) -> dict:
    """
        In this method, the central components of the energy system are
        added to the model definition, first checking if a heating
        network is foreseen and if so, creating the feeding components,
        and then creating Power to Gas and battery storage if defined
        in the US-Input sheet.

        :param central: pandas Dataframe holding the information from \
            the US-Input file "central" sheet
        :type central: pd.Dataframe
        :param true_bools: list containing the entries that are \
            evaluated as true
        :type true_bools: list
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    from program_files import Bus, Storage, Source, Link, get_central_comp_active_status

    exchange_buses = {"electricity_exchange": False}
    for bus in exchange_buses:
        # creation of the bus for the local power exchange
        if get_central_comp_active_status(central, bus):
            sheets = Bus.create_standard_parameter_bus(
                label="central_" + bus.split("_")[0] + "_bus",
                bus_type="central_" + bus.split("_")[0] + "_bus",
                sheets=sheets,
                standard_parameters=standard_parameters,
            )
            exchange_buses[bus] = True

    # if power to gas in energy system create central natural gas bus
    if get_central_comp_active_status(central, "power_to_gas"):
        exchange_buses.update({"naturalgas_exchange": True})

    # create central pv systems
    for num, pv in central.loc[
        ((central["technology"] == "st") | (central["technology"] == "pv&st"))
        & (central["active"] == 1)
    ].iterrows():
        st_dh_connection = central.loc[
            (central["label"] == pv["dh_connection"]) & (central["active"] == 1)
        ]
        if len(st_dh_connection) >= 1:
            # create pv bus
            sheets = Bus.create_standard_parameter_bus(
                label=pv["label"] + "_pv_bus",
                bus_type="central_pv_bus",
                sheets=sheets,
                standard_parameters=standard_parameters,
            )
            # house electricity bus
            sheets = Bus.create_standard_parameter_bus(
                label=pv["label"] + "_electricity_bus",
                bus_type="building_com_electricity_bus",
                sheets=sheets,
                standard_parameters=standard_parameters,
            )

            if exchange_buses["electricity_exchange"]:
                # link from pv bus to central electricity bus
                sheets = Link.create_link(
                    label=pv["label"] + "pv_central_electricity_link",
                    bus_1=pv["label"] + "_pv_bus",
                    bus_2="central_electricity_bus",
                    link_type="building_pv_central_link",
                    sheets=sheets,
                    standard_parameters=standard_parameters,
                )
                # link from central elec bus to building electricity bus
                sheets = Link.create_link(
                    label=pv["label"] + "central_electricity_link",
                    bus_1="central_electricity_bus",
                    bus_2=pv["label"] + "_electricity_bus",
                    link_type="building_central_building_link",
                    sheets=sheets,
                    standard_parameters=standard_parameters,
                )

            if pv["technology"] == "pv&st":
                st_column = "yes"
                pv_column = "yes"
            elif pv["technology"] == "st":
                st_column = "yes"
                pv_column = "no"
            else:
                st_column = "no"
                pv_column = "no"

            sheets = Source.create_sources(
                building={
                    "label": pv["label"],
                    "building type": "central",
                    "st %1d" % 1: st_column,
                    "pv %1d" % 1: pv_column,
                    "azimuth {}".format(1): pv["azimuth"],
                    "surface tilt {}".format(1): pv["surface tilt"],
                    "latitude": pv["latitude"],
                    "longitude": pv["longitude"],
                    "roof area {}".format(1): pv["area"],
                    "flow temperature": float(
                        central.loc[
                            (central["label"] == pv["dh_connection"])
                            & (central["active"] == 1)
                        ]["flow temperature"]
                    ),
                },
                clustering=False,
                sheets=sheets,
                st_output="central_" + pv["dh_connection"] + "_bus",
                standard_parameters=standard_parameters,
                central=True,
            )

    heat_input_buses = central.loc[central["technology"] == "heat_input_bus"]
    # central heat supply
    if True in (heat_input_buses["active"] == 1).values:
        active_buses = central.loc[
            (central["technology"] == "heat_input_bus") & (central["active"] == 1)
        ]
        for num, bus in active_buses.iterrows():
            # create bus which would be used as producer bus in
            # district heating network
            sheets = Bus.create_standard_parameter_bus(
                label="central_{}_bus".format(bus["label"]),
                bus_type="central_heat_input_bus",
                coords=[bus["latitude"], bus["longitude"], "dh-system"],
                sheets=sheets,
                standard_parameters=standard_parameters,
            )
            # create components connected to the producer bus
            for num1, comp in central.loc[
                central["dh_connection"] == bus["label"]
            ].iterrows():
                if comp["active"] in true_bools:
                    sheets = create_central_heat_component(
                        label=comp["label"],
                        comp_type=comp["technology"],
                        bus="central_{}_bus".format(bus["label"]),
                        exchange_buses=exchange_buses,
                        sheets=sheets,
                        area=comp["area"]
                        if comp["technology"] == "gchp_transformer"
                        else "0",
                        standard_parameters=standard_parameters,
                        flow_temp=bus["flow temperature"],
                    )

    # central battery storage
    if get_central_comp_active_status(central=central, technology="battery"):
        sheets = Storage.create_storage(
            building_id="central",
            storage_type="battery",
            de_centralized="central",
            sheets=sheets,
            standard_parameters=standard_parameters,
        )

    if get_central_comp_active_status(central=central, technology="timeseries_source"):
        # house electricity bus
        sheets = Bus.create_standard_parameter_bus(
            label=("screw_turbine_" + "_electricity_bus"),
            bus_type="screw_turbine_bus",
            sheets=sheets,
            standard_parameters=standard_parameters,
        )

        if exchange_buses["electricity_exchange"]:
            # link from pv bus to central electricity bus
            sheets = Link.create_link(
                label="screw_turbine_" + "pv_central_electricity_link",
                bus_1="screw_turbine_" + "_electricity_bus",
                bus_2="central_electricity_bus",
                link_type="building_pv_central_link",
                sheets=sheets,
                standard_parameters=standard_parameters,
            )
        sheets = Source.create_timeseries_source(
            sheets,
            "screw_turbine",
            "screw_turbine_" + "_electricity_bus",
            standard_parameters,
        )
    return sheets


def create_power_to_gas_system(
    label: str, output: str, sheets: dict, standard_parameters: pandas.ExcelFile
) -> dict:
    """
         In this method, a central power to gas system is created,
         for this purpose the necessary data set is obtained
         from the standard parameter sheet, and the components are
         attached to the transformers, the storages and the buses sheet.
    
        :param label: str containing the label of the heatpump to be \
            created
        :type label: str
        :param output: define the heat output bus for the power to gas \
            components
        :type output: str
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    from program_files import Bus, Transformer, Storage, Link

    # create the h2 and the central natural gas bus if they do not exist
    for bus_type in ["central_h2_bus", "central_naturalgas_bus"]:
        if bus_type not in sheets["buses"]["label"].to_list():
            # h2 bus
            sheets = Bus.create_standard_parameter_bus(
                label=bus_type,
                bus_type=bus_type,
                sheets=sheets,
                standard_parameters=standard_parameters,
            )

    transformer_dict = {
        "central_electrolysis_transformer": output,
        "central_methanization_transformer": output,
        "central_fuelcell_transformer": "central_" + label + "_heat_bus",
    }
    # create the elctrolysis and the methanization transformer
    for transformer in transformer_dict:
        if transformer == "central_fuelcell_transformer":
            # links
            sheets = Link.create_link(
                label="central_" + label + "_heat_link",
                bus_1="central_" + label + "_heat_bus",
                bus_2=output,
                link_type="central_h2_heat_link",
                sheets=sheets,
                standard_parameters=standard_parameters,
            )
            # separate heat bus for the fuelcell
            sheets = Bus.create_standard_parameter_bus(
                label="central_" + label + "_heat_bus",
                bus_type="central_h2_heat_bus",
                sheets=sheets,
                standard_parameters=standard_parameters,
            )

        sheets = Transformer.create_transformer(
            label=label,
            building_id="central",
            transformer_type=transformer,
            output=transformer_dict.get(transformer),
            sheets=sheets,
            standard_parameters=standard_parameters,
            # since flow temp does not influence the Generic
            # Transformer's efficiency it is set to 0
            flow_temp="0",
        )

    # storages
    for storage_type in ["central_h2_storage", "central_naturalgas_storage"]:
        if storage_type not in sheets["storages"]["label"].to_list():
            # storages
            sheets = Storage.create_storage(
                building_id="central",
                storage_type=storage_type[8:],
                de_centralized="central",
                sheets=sheets,
                bus="central_" + storage_type.split("_")[1] + "_bus",
                standard_parameters=standard_parameters,
            )

    return sheets


def create_central_heatpump(
    label: str,
    specification: str,
    create_bus: bool,
    central_electricity_bus: bool,
    output: str,
    sheets: dict,
    area: str,
    standard_parameters: pandas.ExcelFile,
    flow_temp: str,
) -> dict:
    """
         In this method, a central heatpump unit is created, for this
         purpose the necessary data set is obtained
         from the standard parameter sheet, and the component is
         attached to the transformers sheet.
    
        :param label: str containing the label of the heatpump to be \
            created
        :type label: str
        :param specification: string giving the information which type
                               of heatpump shall be added.
        :type specification: str
        :param create_bus: indicates whether a central heatpump
                            electricity bus and further parameters shall
                            be created or not.
        :type create_bus: bool
        :param central_electricity_bus: indicates whether a central
            electricity exists
        :type central_electricity_bus: bool
        :param output: str containing the heatpump's output bus label
        :type output: str
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        :param area: maximum collector area for gchp's
        :type area: str
        :param flow_temp: flow temperature of the heatpump
        :type flow_temp: str
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    from program_files import Bus, Transformer, Link

    # create central heatpump electricity bus
    bus_labels = sheets["buses"]["label"].to_list()
    if create_bus and "central_heatpump_electricity_bus" not in bus_labels:
        sheets = Bus.create_standard_parameter_bus(
            label="central_heatpump_electricity_bus",
            bus_type="central_heatpump_electricity_bus",
            sheets=sheets,
            standard_parameters=standard_parameters,
        )
        if central_electricity_bus:
            # connect the heatpump electricity bus to central
            # electricity bus
            sheets = Link.create_link(
                label="central_heatpump_electricity_link",
                bus_1="central_electricity_bus",
                bus_2="central_heatpump_electricity_bus",
                link_type="building_central_building_link",
                sheets=sheets,
                standard_parameters=standard_parameters,
            )
    # create the heatpump
    return Transformer.create_transformer(
        label=label,
        building_id="central",
        output=output,
        specific=specification,
        transformer_type="central_" + specification + "_transformer",
        sheets=sheets,
        area=area,
        standard_parameters=standard_parameters,
        flow_temp=flow_temp,
    )


def create_central_heating_transformer(
    label: str,
    fuel_type: str,
    output: str,
    central_fuel_bus: bool,
    sheets: dict,
    standard_parameters: pandas.ExcelFile,
) -> dict:
    """
        In this method, a central heating plant unit with specified gas
        type is created, for this purpose the necessary data set is
        obtained from the standard parameter sheet, and the component is
        attached to the transformers sheet.
    
        :param label: defines the central heating plant's label
        :type label: str
        :param fuel_type: string which defines the heating plants fuel \
            type
        :type fuel_type: str
        :param output: str containing the transformers output
        :type output: str
        :param central_fuel_bus: defines rather a central fuel exchange\
            is possible or not
        :type central_fuel_bus: bool
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    from program_files import Bus, Transformer, Link

    # plant gas bus
    sheets = Bus.create_standard_parameter_bus(
        label="central_" + label + "_bus",
        bus_type="central_heating_plant_" + fuel_type + "_bus",
        sheets=sheets,
        standard_parameters=standard_parameters,
    )

    # create a link to the central fuel exchange bus if the fuel
    # exchange is possible
    if central_fuel_bus:
        sheets = Link.create_link(
            label="heating_plant_" + label + "_link",
            bus_1="central_" + fuel_type + "_bus",
            bus_2="central_" + label + "_bus",
            link_type="central_" + fuel_type + "_building_link",
            sheets=sheets,
            standard_parameters=standard_parameters,
        )

    # create the heating plant and return the sheets dict
    return Transformer.create_transformer(
        label=label,
        building_id="central",
        specific=fuel_type,
        output=output,
        sheets=sheets,
        transformer_type="central_" + fuel_type + "_heating_plant_transformer",
        standard_parameters=standard_parameters,
        # since flow temp does not influence the Generic
        # Transformer's efficiency it is set to 0
        flow_temp="0",
    )


def create_central_chp(
    label: str,
    fuel_type: str,
    output: str,
    central_elec_bus: bool,
    central_fuel_bus: bool,
    sheets: dict,
    standard_parameters: pandas.ExcelFile,
) -> dict:
    """
        In this method, a central CHP unit with specified gas type is
        created, for this purpose the necessary data set is obtained
        from the standard parameter sheet, and the component is attached
        to the transformers sheet.
    
        :param label: defines the central heating plant's label
        :type label: str
        :param fuel_type: string which defines the heating plants fuel \
            type
        :type fuel_type: str
        :param output: str containing the transformers output
        :type output: str
        :param central_elec_bus: determines if the central power \
            exchange exists
        :type central_elec_bus: bool
        :param central_fuel_bus: defines rather a central fuel exchange\
            is possible or not
        :type central_fuel_bus: bool
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    from program_files import Bus, Transformer, Link

    # chp gas bus
    sheets = Bus.create_standard_parameter_bus(
        label="central_" + label + "_bus",
        bus_type="central_chp_" + fuel_type + "_bus",
        sheets=sheets,
        standard_parameters=standard_parameters,
    )

    # chp electricity bus
    sheets = Bus.create_standard_parameter_bus(
        label="central_" + label + "_elec_bus",
        bus_type="central_chp_" + fuel_type + "_electricity_bus",
        sheets=sheets,
        standard_parameters=standard_parameters,
    )

    # connection to central electricity bus
    if central_elec_bus:
        sheets = Link.create_link(
            label="central_" + label + "_elec_central_link",
            bus_1="central_" + label + "_elec_bus",
            bus_2="central_electricity_bus",
            link_type="central_chp_elec_central_link",
            sheets=sheets,
            standard_parameters=standard_parameters,
        )
    # create a link to the central fuel exchange bus if the fuel
    # exchange is possible
    if central_fuel_bus:
        sheets = Link.create_link(
            label="central_" + label + "_" + fuel_type + "_link",
            bus_1="central_" + fuel_type + "_bus",
            bus_2="central_" + label + "_bus",
            link_type="central_" + fuel_type + "_chp_link",
            sheets=sheets,
            standard_parameters=standard_parameters,
        )
    # create the CHP and return the sheets dict
    return Transformer.create_transformer(
        building_id="central",
        transformer_type="central_" + fuel_type + "_chp",
        label=label,
        specific=fuel_type,
        output=output,
        sheets=sheets,
        standard_parameters=standard_parameters,
        # since flow temp does not influence the Generic
        # Transformer's efficiency it is set to 0
        flow_temp="0",
    )
