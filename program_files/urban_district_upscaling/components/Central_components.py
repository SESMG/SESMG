"""
    Christian Klemm - christian.klemm@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
    Janik Budde - janik.budde@fh-muenster.de
"""
import pandas


def create_central_heat_component(
        label: str, comp_type: str, bus: str, exchange_buses: dict,
        sheets: dict, standard_parameters: pandas.ExcelFile,
        flow_temp: str, gchp_list: list) -> dict:
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
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        :param flow_temp: flow temperature of the central heating \
            system (district heating)
        :type flow_temp: str
        :param gchp_list: list containing \
            [0] the gchp potential area, [1] the length of the \
            vertical heat exchanger relevant for GCHPs  and [2] the \
            heat extraction for the heat exchanger referring to the \
            location
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    from program_files import Storage

    # CHPs
    if comp_type in ["natural gas_chp", "biogas_chp",
                     "pellet_chp", "woodchips_chp"]:
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
            central_electricity_bus=exchange_buses["electricity_exchange"],
            central_fuel_bus=central_bus,
            sheets=sheets,
            standard_parameters=standard_parameters
        )

    # Heating plants
    if comp_type in ["naturalgas_heating_plant", "biogas_heating_plant",
                     "pellet_heating_plant", "woodchips_heating_plant"]:
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
            standard_parameters=standard_parameters
        )

    # Heatpumps
    central_heatpump_indicator = 0
    if comp_type in ["swhp_transformer", "ashp_transformer",
                     "gchp_transformer"]:
        # create heatpump
        sheets = create_central_heatpump(
            label=label,
            specification=comp_type.split("_")[0],
            create_bus=True if central_heatpump_indicator == 0 else False,
            output=bus,
            central_electricity_bus=exchange_buses["electricity_exchange"],
            sheets=sheets,
            standard_parameters=standard_parameters,
            args={"area": gchp_list[0],
                  "flow_temp": flow_temp,
                  "length_geoth_probe": gchp_list[1],
                  "heat_extraction": gchp_list[2]}
        )
        # increase indicator to prevent duplex bus creation
        central_heatpump_indicator += 1

    # create central thermal storage
    if comp_type == "thermal storage":
        sheets = Storage.create_storage(
            building_id="central_" + label,
            storage_type="thermal storage",
            de_centralized="central",
            sheets=sheets,
            standard_parameters=standard_parameters
        )
        
    # power to gas system
    if comp_type == "power_to_gas":
        sheets = create_power_to_gas_system(
            label=label, output=bus, sheets=sheets,
            standard_parameters=standard_parameters)

    return sheets


def create_central_pv_st_sources(central: pandas.DataFrame, sheets: dict,
                                 standard_parameters: pandas.ExcelFile,
                                 electricity_exchange: bool) -> dict:
    """
        In this method, the bus link construct for connecting central
        sources (PV and ST) to the energy system is created. The
        sources are then created and finally the sheets dict is
        returned.
        
        :param central: pandas Dataframe holding the information from \
            the US-Input file "central" sheet
        :type central: pandas.Dataframe
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        :param electricity_exchange: boolean indicating if the user \
            has enabled the electricity exchange between buildings
        :type electricity_exchange: bool
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    
    """
    from program_files.urban_district_upscaling.components import (Bus, Link,
                                                                   Source)
    # query central pv and st systems
    pv_st = central.query("(technology in ['st', 'pv&st']) and active == 1")
    # create central pv systems
    for _, row in pv_st.iterrows():
        
        # search for the central st heat input bus in the central
        # investment data of the upscaling sheet
        st_dh_connection = central.query(
                "label == '{}' and active == 1".format(row["dh_connection"]))
        
        if len(st_dh_connection) >= 1:
            
            # create pv bus and its connection to the exchange bus if
            # activated
            if row["technology"] != "st":
                sheets = Bus.create_standard_parameter_bus(
                        label=row["label"] + "_pv_bus",
                        bus_type="electricity bus photovoltaic central",
                        sheets=sheets,
                        standard_parameters=standard_parameters
                )
                
                if electricity_exchange:
                    # link from pv bus to central electricity bus
                    sheets = Link.create_link(
                        label=row["label"] + "_pv_to_central_electricity_link",
                        bus_1=row["label"] + "_pv_bus",
                        bus_2="central_electricity_bus",
                        link_type="electricity photovoltaic central "
                                  "link central",
                        sheets=sheets,
                        standard_parameters=standard_parameters
                    )
            
            # create electricity bus with shortage and its connection
            # to the central electricity bus to enable the use of
            # the central solar thermal option
            sheets = Bus.create_standard_parameter_bus(
                    label=row["label"] + "_electricity_bus",
                    bus_type="electricity bus solarthermal central",
                    sheets=sheets,
                    standard_parameters=standard_parameters
            )
            
            if electricity_exchange:
                # link from central electricity bus to electricity bus
                # considering shortage option for the solar thermal
                # source
                sheets = Link.create_link(
                    label=row["label"] + "_central_to_st_electricity_link",
                    bus_1="central_electricity_bus",
                    bus_2=row["label"] + "_electricity_bus",
                    link_type="electricity central link solarthermal central",
                    sheets=sheets,
                    standard_parameters=standard_parameters
                )
            
            # get the "boolean" state for pv and st corresponding to
            # the chosen technology
            switch_dict = {"pv&st": ["yes", "yes"], "st": ["yes", "no"]}
            st_column = switch_dict.get(str(row["technology"]), ["no"] * 2)[0]
            pv_column = switch_dict.get(str(row["technology"]), ["no"] * 2)[1]
            
            # get the inserted flow temperature from the upscaling
            # input sheet
            flow_temp = st_dh_connection["flow temperature"].iloc[0]
            
            # after collecting all necessary data for the central
            # sources create the Series needed and run the
            # create_sources method
            component = pandas.Series(data={
                "label": row["label"],
                "building type": "central",
                "st %1d" % 1: st_column,
                "pv %1d" % 1: pv_column,
                "azimuth {}".format(1): row["azimuth"],
                "surface tilt {}".format(1): row["surface tilt"],
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "roof area {}".format(1): row["area"],
                "flow temperature": float(flow_temp),
                "solar thermal share": "standard"
            })
            
            sheets = Source.create_sources(
                    building=component,
                    clustering=False,
                    sheets=sheets,
                    st_output="central_" + row["dh_connection"] + "_bus",
                    standard_parameters=standard_parameters,
                    central=True
            )
    
    return sheets


def create_central_heat_bus_components(central: pandas.DataFrame,
                                       sheets: dict,
                                       standard_parameters: pandas.ExcelFile,
                                       exchange_buses: dict) -> dict:
    """
        In this method, the components connected to a central heat bus
        are created and appended to the return dictionary sheets.
        
        :param central: pandas Dataframe holding the information from \
            the US-Input file "central" sheet
        :type central: pandas.Dataframe
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        :param exchange_buses: dictionary holding booleans indicating \
            if the user has enabled electricity and/or naturalgas \
            exchange
        :type exchange_buses: dict
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    
    """
    from program_files.urban_district_upscaling.components import Bus
    # query active central heat input buses
    heat_input_buses = central.query(
            "(technology == 'heat_input_bus') and (active == 1)"
    )
    # central heat supply
    if len(heat_input_buses) >= 1:
        for _, bus in heat_input_buses.iterrows():
            # create bus which would be used as producer bus in
            # district heating network
            sheets = Bus.create_standard_parameter_bus(
                label="central_{}_bus".format(bus["label"]),
                bus_type="heat bus input central",
                coords=[bus["latitude"], bus["longitude"], "dh-system"],
                sheets=sheets,
                standard_parameters=standard_parameters
            )
            buses_components = central.query(
                    "dh_connection == '{}' and active == 1".format(
                            bus["label"]))
            # create components connected to the producer bus
            for _, comp in buses_components.iterrows():
                # create a list of gchp specific parameters if the
                # considered component is a gchp
                if comp["technology"] == "gchp_transformer":
                    gchp_list = [comp["area"],
                                 comp["length of the geoth. probe"],
                                 comp["heat extraction"]]
                else:
                    gchp_list = ["0"] * 3
                
                # create the central heat component
                sheets = create_central_heat_component(
                        label=comp["label"],
                        comp_type=comp["technology"],
                        bus="central_{}_bus".format(bus["label"]),
                        exchange_buses=exchange_buses,
                        sheets=sheets,
                        gchp_list=gchp_list,
                        standard_parameters=standard_parameters,
                        flow_temp=bus["flow temperature"]
                )
    
    return sheets


def create_central_timeseries_sources(central: pandas.DataFrame, sheets: dict,
                                      standard_parameters: pandas.ExcelFile,
                                      electricity_exchange: bool) -> dict:
    """
        In this method, the user activated central timeseries sources
        their buses and links are created.
        
        :param central: pandas Dataframe holding the information from \
            the US-Input file "central" sheet
        :type central: pandas.Dataframe
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        :param electricity_exchange: boolean indicating if the user \
            has activated the exchange of electricity between buildings
        :type electricity_exchange: dict
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    
    """
    from program_files.urban_district_upscaling.components import (Bus, Link,
                                                                   Source)
    # query active central timeseries sources
    timeseries_sources = central.query(
        "(technology == 'timeseries_source') and (active == 1)"
    )
    
    if len(timeseries_sources) >= 1:
        for _, source in timeseries_sources.iterrows():
            # create output bus for the current considered timeseries
            # source
            sheets = Bus.create_standard_parameter_bus(
                    label="central_" + source["label"] + "_electricity_bus",
                    bus_type="electricity bus timeseries central",
                    sheets=sheets,
                    standard_parameters=standard_parameters
            )
            
            # if the user has activated the exchange of electricity
            # between building add the link between the sources output
            # and the central electricity bus
            if electricity_exchange:
                sheets = Link.create_link(
                    label="central_" + source["label"]
                          + "_central_electricity_link",
                    bus_1="central_" + source["label"]
                          + "_electricity_bus",
                    bus_2="central_electricity_bus",
                    link_type="electricity timeseries central link central",
                    sheets=sheets,
                    standard_parameters=standard_parameters
                )
                
            # create the considered timeseries source
            sheets = Source.create_timeseries_source(
                sheets=sheets,
                label="central_" + source["label"],
                output="central_" + source["label"] + "_electricity_bus",
                standard_parameters=standard_parameters
            )
    
    return sheets


def central_components(central: pandas.DataFrame, sheets: dict,
                       standard_parameters: pandas.ExcelFile
                       ) -> (dict, bool, bool):
    """
        In this method, the central components of the energy system are
        added to the model definition, first checking if a heating
        network is foreseen and if so, creating the feeding components,
        and then creating Power to Gas and battery storage if defined
        in the US-Input sheet.

        :param central: pandas Dataframe holding the information from \
            the US-Input file "central" sheet
        :type central: pandas.Dataframe
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
    from program_files import Bus, Storage, get_central_comp_active_status
    
    # check if the user has activated central electricity exchange
    # between the given buildings by enabling electricity_exchange in
    # the central us sheet
    electricity_exchange = get_central_comp_active_status(
        central=central, technology="electricity_exchange"
    )
    # check if the user has activated power to gas systems by enabling
    # power_to_gas in the central us sheet
    p2g = get_central_comp_active_status(
        central=central, technology="power_to_gas"
    )

    # create the central electricity bus for the exchange of
    # electricity between buildings
    if electricity_exchange:
        sheets = Bus.create_standard_parameter_bus(
            label="central_electricity_bus",
            bus_type="electricity bus central",
            sheets=sheets,
            standard_parameters=standard_parameters
        )
    
    # append all central source to the sheets dictionary
    sheets = create_central_pv_st_sources(
        central=central,
        sheets=sheets,
        standard_parameters=standard_parameters,
        electricity_exchange=electricity_exchange
    )
    
    # create the components connected to the central heat bus
    sheets = create_central_heat_bus_components(
        central=central,
        sheets=sheets,
        standard_parameters=standard_parameters,
        exchange_buses={"electricity_exchange": electricity_exchange,
                        "naturalgas_exchange": p2g})
    
    sheets = create_central_timeseries_sources(
        central=central,
        sheets=sheets,
        standard_parameters=standard_parameters,
        electricity_exchange=electricity_exchange
    )

    # central battery storage
    if get_central_comp_active_status(central=central, technology="battery"):
        sheets = Storage.create_storage(
            building_id="central",
            storage_type="battery storage",
            de_centralized="central",
            sheets=sheets,
            standard_parameters=standard_parameters
        )

    return sheets, electricity_exchange, p2g


def create_power_to_gas_system(label: str, output: str, sheets: dict,
                               standard_parameters: pandas.ExcelFile) -> dict:
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
    for bus_type in ["natural gas bus central", "hydrogen bus central"]:
        type_list = bus_type.split(" ")
        type_list_short = list(type_list[:len(type_list) - 1])
        label = str(type_list[-1])
        for i in type_list_short:
            label += ("_" + i)
        
        if (len(sheets["buses"]) == 0
                or bus_type not in sheets["buses"]["label"].to_list()):
            # h2 bus
            sheets = Bus.create_standard_parameter_bus(
                label=label,
                bus_type=bus_type,
                sheets=sheets,
                standard_parameters=standard_parameters
            )
    
    transformer_dict = \
        {"electrolysis ": output,
         "methanization ": output,
         "fuel cell ": label[:-4] + "_heat_bus"}
    # create the electrolysis and the methanization transformer
    for transformer in transformer_dict:
        if transformer == "fuel cell ":
            # links
            sheets = Link.create_link(
                    label=label[:-4] + '_heat_link',
                    bus_1=label[:-4] + '_heat_bus',
                    bus_2=output,
                    link_type="heat fuel cell central link central",
                    sheets=sheets,
                    standard_parameters=standard_parameters)
            # separate heat bus for the fuelcell
            sheets = Bus.create_standard_parameter_bus(
                    label=label[:-4] + '_heat_bus',
                    bus_type="heat bus fuel cell central",
                    sheets=sheets,
                    standard_parameters=standard_parameters)
        
        sheets = Transformer.create_transformer(
            label=label[:-4],
            transformer_type=transformer,
            output=transformer_dict.get(transformer),
            sheets=sheets,
            standard_parameters=standard_parameters,
            de_centralized="central",
            # since flow temp does not influence the Generic
            # Transformer's efficiency it is set to 0
            flow_temp="0"
        )

    # storages
    for storage_type in ["hydrogen storage steel cylinder",
                         "natural gas storage steel cylinder"]:
        if (len(sheets["storages"]) == 0
                or storage_type not in sheets["storages"]["label"].to_list()):
            # storages
            sheets = Storage.create_storage(
                building_id="central",
                storage_type=storage_type,
                de_centralized="central",
                sheets=sheets,
                standard_parameters=standard_parameters
            )

    return sheets


def create_central_heatpump(label: str, specification: str, create_bus: bool,
                            central_electricity_bus: bool, output: str,
                            sheets: dict,
                            standard_parameters: pandas.ExcelFile,
                            args: dict) -> dict:
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
        :param args: dictionary containing additional arguments
            (area, flow_temp, length_geoth_probe, heat_extraction)
        :type args: dict
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    from program_files import Bus, Transformer, Link
    
    if (create_bus and (len(sheets["buses"]) == 0
                        or "central_heatpump_electricity_bus"
                        not in sheets["buses"]["label"].to_list())):
        
        # create central heatpump electricity bus
        sheets = Bus.create_standard_parameter_bus(
            label="central_heatpump_electricity_bus",
            bus_type="electricity bus heat pump central",
            sheets=sheets,
            standard_parameters=standard_parameters
        )
        
        # connect the heatpump electricity bus to central
        # electricity bus
        if central_electricity_bus:
            sheets = Link.create_link(
                label="central_heatpump_electricity_link",
                bus_1="central_electricity_bus",
                bus_2="central_heatpump_electricity_bus",
                link_type="electricity central link heat pump central ",
                sheets=sheets,
                standard_parameters=standard_parameters
            )
            
    # create the heatpump
    return Transformer.create_transformer(
        label=label,
        de_centralized="central",
        output=output,
        fuel_type=specification,
        transformer_type="heat pump " + specification,
        sheets=sheets,
        standard_parameters=standard_parameters,
        **args
    )


def create_central_heating_transformer(
        label: str, fuel_type: str, output: str, central_fuel_bus: bool,
        sheets: dict, standard_parameters: pandas.ExcelFile) -> dict:
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
    
    fuel_type_wo_gaps = fuel_type.replace(" ", "_")
    
    if (len(sheets["buses"]) == 0 or
            ("central_" + label + "_" + fuel_type_wo_gaps + "_bus"
             not in list(sheets["buses"]["label"]))):
        # plant gas bus
        sheets = Bus.create_standard_parameter_bus(
            label="central_" + label + "_" + fuel_type_wo_gaps + "_bus",
            bus_type=fuel_type + " bus central",
            sheets=sheets,
            standard_parameters=standard_parameters
        )

    # create a link to the central fuel exchange bus if the fuel
    # exchange is possible
    if central_fuel_bus:
        sheets = Link.create_link(
            label="central_heating_plant_" + label + "_link",
            bus_1="central_" + fuel_type_wo_gaps + "_bus",
            bus_2="central_" + label + "_" + fuel_type_wo_gaps + "_bus",
            link_type=fuel_type + " central link heating plant central",
            sheets=sheets,
            standard_parameters=standard_parameters
        )
        
    if "gas" in fuel_type:
        category = "gas"
    elif fuel_type in ["pellet", "woodchip"]:
        category = "biomass"
    else:
        category = "oil"
    
    fuel_type += " "
    # create the heating plant and return the sheets dict
    return Transformer.create_transformer(
        label="central_" + label,
        fuel_type=fuel_type,
        output=output,
        sheets=sheets,
        de_centralized="central",
        transformer_type=category + " heating " + fuel_type,
        standard_parameters=standard_parameters,
        category=category,
        # since flow temp does not influence the Generic
        # Transformer's efficiency it is set to 0
        flow_temp="0"
    )


def create_central_chp(
        label: str, fuel_type: str, output: str, central_electricity_bus: bool,
        central_fuel_bus: bool, sheets: dict,
        standard_parameters: pandas.ExcelFile) -> dict:
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
        :param output: string containing the transformers output
        :type output: str
        :param central_electricity_bus: determines if the central power \
            exchange exists
        :type central_electricity_bus: bool
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

    fuel_type_wo_gaps = fuel_type.replace(" ", "_")
    
    if (len(sheets["buses"]) == 0 or
            ("central_" + label + "_" + fuel_type_wo_gaps + "_bus"
             not in list(sheets["buses"]["label"]))):
        # create the CHP fuel bus
        sheets = Bus.create_standard_parameter_bus(
            label="central_" + label + "_" + fuel_type_wo_gaps + "_bus",
            bus_type=fuel_type + " bus combined heat and power central",
            sheets=sheets,
            standard_parameters=standard_parameters
        )

    # create the CHP electricity output bus
    sheets = Bus.create_standard_parameter_bus(
        label="central_" + label + "_electricity_bus",
        bus_type="electricity bus combined heat and power "
                 + fuel_type + " central",
        sheets=sheets,
        standard_parameters=standard_parameters
    )

    # create the link between CHP electricity output and central bus
    if central_electricity_bus:
        sheets = Link.create_link(
            label="central_" + label + "_electricity_central_link",
            bus_1="central_" + label + "_electricity_bus",
            bus_2="central_electricity_bus",
            link_type="electricity combined heat and power "
                      + fuel_type + " central link central",
            sheets=sheets,
            standard_parameters=standard_parameters
        )
        
    # create a link to the central fuel exchange bus if the fuel
    # exchange is possible
    if central_fuel_bus:
        sheets = Link.create_link(
            label="central_" + label + "_" + fuel_type_wo_gaps + "_link",
            bus_1="central_" + fuel_type_wo_gaps + "_bus",
            bus_2="central_" + label + "_" + fuel_type_wo_gaps + "_bus",
            link_type=fuel_type
            + " central link combined heat and power central",
            sheets=sheets,
            standard_parameters=standard_parameters
        )
    
    fuel_type += " "
    # create the CHP and return the sheets dict
    return Transformer.create_transformer(
        transformer_type="combined heat and power " + fuel_type,
        label="central_" + label,
        fuel_type=fuel_type,
        output=output,
        sheets=sheets,
        de_centralized="central",
        standard_parameters=standard_parameters,
        # since flow temp does not influence the Generic
        # Transformer's efficiency it is set to 0
        flow_temp="0"
    )
