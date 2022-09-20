def create_central_heat_component(label, comp_type, bus, exchange_buses, sheets, area):
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
    :param sheets:
    :param area: filled if a central gchp has to be created
    :type area: str
    :return:
    """
    from program_files import Storage

    # create central chp plants
    chp_types = ["naturalgas_chp", "biogas_chp", "pellet_chp", "woodchips_chp"]
    if comp_type in chp_types:
        if comp_type.split("_")[0] in exchange_buses:
            central_bus = exchange_buses[comp_type.split("_")[0] + "_exchange"]
        else:
            central_bus = False
        sheets = create_central_chp(
            label=label,
            gas_type=comp_type.split("_")[0],
            output=bus,
            central_elec_bus=exchange_buses["electricity_exchange"],
            central_gas_bus=central_bus,
            sheets=sheets,
        )

    # central gas heating plants
    heating_plant_types = [
        "naturalgas_heating_plant",
        "biogas_heating_plant",
        "pellet_heating_plant",
        "woodchips_heating_plant",
    ]
    if comp_type in heating_plant_types:
        if comp_type.split("_")[0] in exchange_buses:
            central_bus = exchange_buses[comp_type.split("_")[0] + "_exchange"]
        else:
            central_bus = False
        sheets = create_central_gas_heating_transformer(
            label=label,
            gas_type=comp_type.split("_")[0],
            output=bus,
            central_gas_bus=central_bus,
            sheets=sheets,
        )

    # create central chp plants
    heatpump_types = ["swhp_transformer", "ashp_transformer", "gchp_transformer"]
    central_heatpump_indicator = 0
    if comp_type in heatpump_types:
        sheets = create_central_heatpump(
            label=label,
            specification=comp_type.split("_")[0],
            create_bus=True if central_heatpump_indicator == 0 else False,
            output=bus,
            central_elec_bus=exchange_buses["electricity_exchange"],
            sheets=sheets,
            area=area,
        )
        central_heatpump_indicator += 1

    # create central thermal storage
    if comp_type == "thermal_storage":
        sheets = Storage.create_storage(
            building_id="central_" + label,
            storage_type="thermal",
            de_centralized="central",
            bus=bus,
            sheets=sheets,
        )
    # power to gas system
    if comp_type == "power_to_gas":
        sheets = create_power_to_gas_system(label=label, bus=bus, sheets=sheets)

    return sheets


def central_comp(central, true_bools, sheets):
    """
        In this method, the central components of the energy system are
        added to the scenario, first checking if a heating network is
        foreseen and if so, creating the feeding components, and then
        creating Power to Gas and battery storage if defined in the pre
        scenario.

        :param central: pandas Dataframe holding the information from the \
                prescenario file "central" sheet
        :type central: pd.Dataframe
        :param true_bools:
        :type true_bools:
        :param sheets:
        :type sheets:
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
        if (
            len(
                central.loc[
                    (central["component"] == pv["dh_connection"])
                    & (central["active"] == 1)
                ]
            )
            >= 1
        ):
            # create pv bus
            sheets = Bus.create_standard_parameter_bus(
                label=pv["component"] + "_pv_bus",
                bus_type="central_pv_bus",
                sheets=sheets,
            )
            # house electricity bus
            sheets = Bus.create_standard_parameter_bus(
                label=(pv["component"] + "_electricity_bus"),
                bus_type="building_com_electricity_bus",
                sheets=sheets,
            )

            if exchange_buses["electricity_exchange"]:
                # link from pv bus to central electricity bus
                sheets = Link.create_link(
                    label=pv["component"] + "pv_central_electricity_link",
                    bus_1=pv["component"] + "_pv_bus",
                    bus_2="central_electricity_bus",
                    link_type="building_pv_central_link",
                    sheets=sheets,
                )
                # link from central elec bus to building electricity bus
                sheets = Link.create_link(
                    label=pv["component"] + "central_electricity_link",
                    bus_1="central_electricity_bus",
                    bus_2=pv["component"] + "_electricity_bus",
                    link_type="building_central_building_link",
                    sheets=sheets,
                )

            sheets = Source.create_sources(
                {
                    "label": pv["component"],
                    "building type": "central",
                    "st or pv %1d" % 1: str(pv["technology"]),
                    "azimuth (°) {}".format(1): pv["azimuth"],
                    "surface tilt (°) {}".format(1): pv["surface tilt"],
                    "latitude": pv["lat."],
                    "longitude": pv["lon."],
                    "roof area (m²) {}".format(1): pv["area (m2)"],
                    "roof area (m²) {}".format(2): 0,
                },
                False,
                sheets,
                "central_" + pv["dh_connection"] + "_bus",
            )

    # central heat supply
    if (
        True
        in (
            central.loc[central["technology"] == "heat_input_bus"]["active"] == 1
        ).values
    ):
        for num, bus in central.loc[
            (central["technology"] == "heat_input_bus") & (central["active"] == 1)
        ].iterrows():
            # create bus which would be used as producer bus in
            # district heating network
            sheets = Bus.create_standard_parameter_bus(
                label="central_{}_bus".format(bus["component"]),
                bus_type="central_heat_input_bus",
                cords=[bus["lat."], bus["lon."], "dh-system"],
                sheets=sheets,
            )
            # create components connected to the producer bus
            for num, comp in central.loc[
                central["dh_connection"] == bus["component"]
            ].iterrows():
                if comp["active"] in true_bools:
                    sheets = create_central_heat_component(
                        label=comp["component"],
                        comp_type=comp["technology"],
                        bus="central_{}_bus".format(bus["component"]),
                        exchange_buses=exchange_buses,
                        sheets=sheets,
                        area=comp["area (m2)"]
                        if comp["technology"] == "gchp_transformer"
                        else "0",
                    )

    # central battery storage
    if central.loc[(central["technology"] == "battery")]["active"].values[0] == 1:
        sheets = Storage.create_storage(
            building_id="central",
            storage_type="battery",
            de_centralized="central",
            sheets=sheets,
        )

    if (
        central.loc[(central["technology"] == "timeseries_source")]["active"].values[0]
        == 1
    ):
        # house electricity bus
        sheets = Bus.create_standard_parameter_bus(
            label=("screw_turbine_" + "_electricity_bus"),
            bus_type="central_pv_bus",
            sheets=sheets,
        )

        if exchange_buses["electricity_exchange"]:
            # link from pv bus to central electricity bus
            sheets = Link.create_link(
                label="screw_turbine_" + "pv_central_electricity_link",
                bus_1="screw_turbine_" + "_electricity_bus",
                bus_2="central_electricity_bus",
                link_type="building_pv_central_link",
                sheets=sheets,
            )
        sheets = Source.create_timeseries_source(
            sheets, "screw_turbine", "screw_turbine_" + "_electricity_bus"
        )
    return sheets


def create_power_to_gas_system(label, bus, sheets):
    """
    TODO DOCSTRING TEXT

    :param bus:
    :type bus:
    :param sheets:
    :type sheets:
    """
    from program_files import Bus, Transformer, Storage, Link

    for bus_type in ["central_h2_bus", "central_naturalgas_bus"]:
        if bus_type not in sheets["buses"]["label"].to_list():
            # h2 bus
            sheets = Bus.create_standard_parameter_bus(
                label=bus_type, bus_type=bus_type, sheets=sheets
            )

    for transformer in [
        "central_electrolysis_transformer",
        "central_methanization_transformer",
        "central_fuelcell_transformer",
    ]:
        sheets = Transformer.create_transformer(
            label=label,
            building_id="central",
            transf_type=transformer,
            output=bus,
            sheets=sheets,
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
            )

    return sheets


def create_central_heatpump(
    label, specification, create_bus, central_elec_bus, output, sheets, area
):
    """
     In this method, a central heatpump unit with specified gas type
     is created, for this purpose the necessary data set is obtained
     from the standard parameter sheet, and the component is attached
     to the transformers sheet.

    :param specification: string giving the information which type
                           of heatpump shall be added.
     :type specification: str
     :param create_bus: indicates whether a central heatpump
                        electricity bus and further parameters shall
                        be created or not.
     :param central_elec_bus: indicates whether a central elec exists
     :type central_elec_bus: bool
     :param output:
     :type output:
     :param sheets:
     :type sheets:
     :param area:
     :type area: str
     :return: bool
    """
    from program_files import Bus, Transformer, Link

    if (
        create_bus
        and "central_heatpump_elec_bus" not in sheets["buses"]["label"].to_list()
    ):
        sheets = Bus.create_standard_parameter_bus(
            label="central_heatpump_elec_bus",
            bus_type="central_heatpump_electricity_bus",
            sheets=sheets,
        )
        if central_elec_bus:
            # connection to central electricity bus
            sheets = Link.create_link(
                label="central_heatpump_electricity_link",
                bus_1="central_electricity_bus",
                bus_2="central_heatpump_elec_bus",
                link_type="building_central_building_link",
                sheets=sheets,
            )

    return Transformer.create_transformer(
        label=label,
        building_id="central",
        output=output,
        specific=specification,
        transf_type="central_" + specification + "_transformer",
        sheets=sheets,
        area=area,
    )


def create_central_gas_heating_transformer(
    label, gas_type, output, central_gas_bus, sheets
):
    """
    In this method, a central heating plant unit with specified gas
    type is created, for this purpose the necessary data set is
    obtained from the standard parameter sheet, and the component is
    attached to the transformers sheet.

    :param label: defines the central heating plant's label
    :type label: str
    :param gas_type: string which defines rather naturalgas or biogas
                    is used
    :type gas_type: str
    :param output: str containing the transformers output
    :type output: str
    :param central_gas_bus: defines rather a central gas exchange is \
        investable
    :type central_gas_bus: bool
    :param sheets:
    :type sheets:
    """
    from program_files import Bus, Transformer, Link

    # plant gas bus
    sheets = Bus.create_standard_parameter_bus(
        label="central_" + label + "_bus",
        bus_type="central_heating_plant_" + gas_type + "_bus",
        sheets=sheets,
    )

    if central_gas_bus:
        sheets = Link.create_link(
            label="heating_plant_" + label + "_link",
            bus_1="central_" + gas_type + "_bus",
            bus_2="central_" + label + "_bus",
            link_type="central_naturalgas_building_link",
            sheets=sheets,
        )

    return Transformer.create_transformer(
        label=label,
        building_id="central",
        specific=gas_type,
        output=output,
        sheets=sheets,
        transf_type="central_" + gas_type + "_heating_plant_transformer",
    )


def create_central_chp(
    label, gas_type, output, central_elec_bus, central_gas_bus, sheets
):
    """
        In this method, a central CHP unit with specified gas type is
        created, for this purpose the necessary data set is obtained
        from the standard parameter sheet, and the component is attached
         to the transformers sheet.

        :param label:
        :type label:
        :param gas_type: string which defines rather naturalgas or \
            biogas is used
        :type gas_type: str
        :param output: string containing the heat output bus name
        :type output: str
        :param central_elec_bus: determines if the central power \
            exchange exists
        :param sheets
    """
    from program_files import Bus, Transformer, Link

    # chp gas bus
    sheets = Bus.create_standard_parameter_bus(
        label="central_" + label + "_bus",
        bus_type="central_chp_" + gas_type + "_bus",
        sheets=sheets,
    )

    # chp electricity bus
    sheets = Bus.create_standard_parameter_bus(
        label="central_" + label + "_elec_bus",
        bus_type="central_chp_" + gas_type + "_electricity_bus",
        sheets=sheets,
    )

    if central_elec_bus:
        # connection to central electricity bus
        sheets = Link.create_link(
            label="central_" + label + "_elec_central_link",
            bus_1="central_" + label + "_elec_bus",
            bus_2="central_electricity_bus",
            link_type="central_chp_elec_central_link",
            sheets=sheets,
        )

    if central_gas_bus:
        sheets = Link.create_link(
            label="central_" + label + "_naturalgas_link",
            bus_1="central_naturalgas_bus",
            bus_2="central_" + label + "_bus",
            link_type="central_naturalgas_chp_link",
            sheets=sheets,
        )

    return Transformer.create_transformer(
        building_id="central",
        transf_type="central_" + gas_type + "_chp",
        label=label,
        specific=gas_type,
        output=output,
        sheets=sheets,
    )
