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
    bus_dict = {"label": label}
    # extracts the bus specific standard values from the standard_parameters
    # dataset
    bus_standard_parameters = standard_parameters.parse(
        "buses", index_col="bus_type"
    ).loc[bus_type]
    bus_standard_keys = bus_standard_parameters.keys().tolist()
    # addapt standard values
    for i in range(len(bus_standard_keys)):
        bus_dict[bus_standard_keys[i]] = bus_standard_parameters[bus_standard_keys[i]]
    # creates "bus-list-element"
    sheets["buses"] = sheets["buses"].append(pd.Series(bus_dict), ignore_index=True)


def create_standard_parameter_link(
    label: str, bus_1: str, bus_2: str, link_type: str, standard_parameters
):
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
    link_house_specific_dict = {"label": label, "bus1": bus_1, "bus2": bus_2}

    # read the heat network standards from standard_parameters.xlsx and
    # append them to the link_house_specific_dict
    link_standard_parameters = standard_parameters.parse(
        "links", index_col="link_type"
    ).loc[link_type]
    link_standard_keys = link_standard_parameters.keys().tolist()
    for i in range(len(link_standard_keys)):
        link_house_specific_dict[link_standard_keys[i]] = link_standard_parameters[
            link_standard_keys[i]
        ]

    # produce a pandas series out of the dict above due to easier appending
    link_series = pd.Series(link_house_specific_dict)
    sheets["links"] = sheets["links"].append(link_series, ignore_index=True)


def create_standard_parameter_sink(
    sink_type: str, label: str, sink_input: str, annual_demand: int, standard_parameters
):
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
    sink_standard_parameters = standard_parameters.parse(
        "sinks", index_col="sink_type"
    ).loc[sink_type]
    sink_dict = {"label": label, "input": sink_input, "annual demand": annual_demand}

    # read the heat network standards from standard_parameters.xlsx and append
    # them to the sink_house_specific_dict
    sink_standard_keys = sink_standard_parameters.keys().tolist()
    for i in range(len(sink_standard_keys)):
        sink_dict[sink_standard_keys[i]] = sink_standard_parameters[
            sink_standard_keys[i]
        ]

    # produce a pandas series out of the dict above due to easier appending
    sink_series = pd.Series(sink_dict)
    sheets["sinks"] = sheets["sinks"].append(sink_series, ignore_index=True)


def create_standard_parameter_transformer(
    specific_param, standard_parameters, standard_param_name
):
    """

    :param specific_param:
    :param standard_param:
    :return:
    """

    # read the standards from standard_param and append
    # them to the dict
    transformers_standard_parameters = standard_parameters.parse("transformers")
    transformers_standard_parameters.set_index("comment", inplace=True)
    standard_param = transformers_standard_parameters.loc[standard_param_name]

    standard_keys = standard_param.keys().tolist()
    for i in range(len(standard_keys)):
        specific_param[standard_keys[i]] = standard_param[standard_keys[i]]

    # produce a pandas series out of the dict above due to easier appending
    transformer_series = pd.Series(specific_param)
    sheets["transformers"] = sheets["transformers"].append(
        transformer_series, ignore_index=True
    )


def create_standard_parameter_storage(
    specific_param, standard_parameters, standard_param_name
):
    """

    :param specific_param:
    :param standard_param_name:
    :return:
    """

    # read the standards from standard_param and append
    # them to the dict
    storage_standard_parameters = standard_parameters.parse("storages")
    storage_standard_parameters.set_index("comment", inplace=True)
    standard_param = storage_standard_parameters.loc[standard_param_name]

    standard_keys = standard_param.keys().tolist()
    for i in range(len(standard_keys)):
        specific_param[standard_keys[i]] = standard_param[standard_keys[i]]

    # produce a pandas series out of the dict above due to easier appending
    transformer_series = pd.Series(specific_param)
    sheets["storages"] = sheets["storages"].append(
        transformer_series, ignore_index=True
    )


def central_comp(central, standard_parameters):
    """
    todo docstring
    """
    for i, j in central.iterrows():
        if j["electricity_bus"] in ["Yes", "yes", 1]:
            create_standard_parameter_bus(
                label="central_electricity_bus",
                bus_type="central_electricity_bus",
                standard_parameters=standard_parameters,
            )

        # create required central components for a central heating
        # network
        if j["heat_link"] in ["yes", "Yes", 1]:
            # input bus
            create_standard_parameter_bus(
                label="central_heat_input_bus",
                bus_type="central_heat_input_bus",
                standard_parameters=standard_parameters,
            )

            # output bus
            create_standard_parameter_bus(
                label="central_heat_output_bus",
                bus_type="central_heat_output_bus",
                standard_parameters=standard_parameters,
            )

            # link considering losses
            create_standard_parameter_link(
                label="central_heat_link",
                bus_1="central_heat_input_bus",
                bus_2="central_heat_output_bus",
                link_type="central_heat_link",
                standard_parameters=standard_parameters,
            )
            # central natural gas
            if j["naturalgas_chp"] in ["yes", "Yes", 1]:
                create_central_chp(
                    gastype="naturalgas", standard_parameters=standard_parameters
                )

            # central bio gas
            if j["biogas_chp"] in ["yes", "Yes", 1]:
                create_central_chp(
                    gastype="biogas", standard_parameters=standard_parameters
                )

            # central swhp todo simplify
            if j["swhp_transformer"] in ["yes", "Yes", 1]:
                create_central_swhp(standard_parameters=standard_parameters)

            # central biomass plant
            if j["biomass_plant"] in ["yes", "Yes", 1]:
                create_central_biomass_plant(standard_parameters=standard_parameters)

            # power to gas system
            if j["power_to_gas"] in ["yes", "Yes", 1]:
                create_power_to_gas_system(standard_parameters=standard_parameters)

            if j["battery_storage"] in ["yes", "Yes", 1]:
                create_battery(
                    id="central",
                    standard_parameters=standard_parameters,
                    storage_type="central",
                )


def create_power_to_gas_system(standard_parameters):
    """
        todo: docstrings

    :param standard_parameters:
    :return:
    """

    # h2 bus
    create_standard_parameter_bus(
        label="central_h2_bus",
        bus_type="central_h2_bus",
        standard_parameters=standard_parameters,
    )

    # natural gas bus
    create_standard_parameter_bus(
        label="central_naturalgas_bus",
        bus_type="central_naturalgas_bus",
        standard_parameters=standard_parameters,
    )

    # electrolysis transformer
    electrolysis_transformer_param = {
        "label": "central_electrolysis_transformer",
        "comment": "automatically_created",
        "input": "central_electricity_bus",
        "output": "central_h2_bus",
        "output2": "None",
    }

    create_standard_parameter_transformer(
        specific_param=electrolysis_transformer_param,
        standard_parameters=standard_parameters,
        standard_param_name="central_electrolysis_transformer",
    )

    # methanization transformer
    methanization_transformer_param = {
        "label": "central_methanization_transformer",
        "comment": "automatically_created",
        "input": "central_h2_bus",
        "output": "central_naturalgas_bus",
        "output2": "None",
    }

    create_standard_parameter_transformer(
        specific_param=methanization_transformer_param,
        standard_parameters=standard_parameters,
        standard_param_name="central_methanization_transformer",
    )

    # fuel cell transformer
    fuelcell_transformer_param = {
        "label": "central_fuelcell_transformer",
        "comment": "automatically_created",
        "input": "central_h2_bus",
        "output": "central_electricity_bus",
        "output2": "central_heat_input_bus",
    }

    create_standard_parameter_transformer(
        specific_param=fuelcell_transformer_param,
        standard_parameters=standard_parameters,
        standard_param_name="central_fuelcell_transformer",
    )

    # h2 storage
    h2_storage_param = {
        "label": "central_h2_storage",
        "comment": "automatically_created",
        "bus": "central_h2_bus",
    }

    create_standard_parameter_storage(
        specific_param=h2_storage_param,
        standard_parameters=standard_parameters,
        standard_param_name="central_h2_storage",
    )

    # natural gas storage
    ng_storage_param = {
        "label": "central_naturalgas_storage",
        "comment": "automatically_created",
        "bus": "central_naturalgas_bus",
    }

    create_standard_parameter_storage(
        specific_param=ng_storage_param,
        standard_parameters=standard_parameters,
        standard_param_name="central_naturalgas_storage",
    )

    # link to chp_naturalgas_bus
    create_standard_parameter_link(
        label="central_naturalgas_chp_naturalgas_link",
        bus_1="central_naturalgas_bus",
        bus_2="central_chp_naturalgas_bus",
        link_type="central_naturalgas_chp_link",
        standard_parameters=standard_parameters,
    )


def create_central_biomass_plant(standard_parameters):
    """
    todo docstring
    """
    # biomass bus
    create_standard_parameter_bus(
        label="central_biomass_bus",
        bus_type="central_biomass_bus",
        standard_parameters=standard_parameters,
    )

    # biomass transformer
    transformers_standard_parameters = standard_parameters.parse("transformers")
    transformers_standard_parameters.set_index("comment", inplace=True)
    biomass_standard_parameters = transformers_standard_parameters.loc[
        "central_biomass_transformer"
    ]
    biomass_central_dict = {
        "label": "central_biomass_transformer",
        "comment": "automatically_created",
        "input": "central_biomass_bus",
        "output": "central_heat_input_bus",
        "output2": "None",
    }

    # read the biomass standards from standard_parameters.xlsx and append
    # them to the biomass_central_dict
    biomass_standard_keys = biomass_standard_parameters.keys().tolist()
    for i in range(len(biomass_standard_keys)):
        biomass_central_dict[biomass_standard_keys[i]] = biomass_standard_parameters[
            biomass_standard_keys[i]
        ]  # [0]

    # produce a pandas series out of the dict above due to easier appending
    biomass_series = pd.Series(biomass_central_dict)
    sheets["transformers"] = sheets["transformers"].append(
        biomass_series, ignore_index=True
    )


def create_central_swhp(standard_parameters):
    """
    todo docstring
    """
    # swhp elec bus
    create_standard_parameter_bus(
        label="central_swhp_elec_bus",
        bus_type="central_swhp_electricity_bus",
        standard_parameters=standard_parameters,
    )

    # swhp transformer
    transformers_standard_parameters = standard_parameters.parse("transformers")
    transformers_standard_parameters.set_index("comment", inplace=True)
    swhp_standard_parameters = transformers_standard_parameters.loc[
        "central_swhp_transformer"
    ]
    swhp_central_dict = {
        "label": "central_swhp_transformer",
        "comment": "automatically_created",
        "input": "central_swhp_elec_bus",
        "output": "central_heat_input_bus",
        "output2": "None",
    }

    # read the swhp standards from standard_parameters.xlsx and append
    # them to the swhp_central_dict
    swhp_standard_keys = swhp_standard_parameters.keys().tolist()
    for i in range(len(swhp_standard_keys)):
        swhp_central_dict[swhp_standard_keys[i]] = swhp_standard_parameters[
            swhp_standard_keys[i]
        ]  # [0]

    # produce a pandas series out of the dict above due to easier appending
    swhp_series = pd.Series(swhp_central_dict)
    sheets["transformers"] = sheets["transformers"].append(
        swhp_series, ignore_index=True
    )


def create_central_chp(gastype, standard_parameters):
    """
    todo docstring
    """
    # chp gas bus
    create_standard_parameter_bus(
        label="central_chp_" + gastype + "_bus",
        bus_type="central_chp_" + gastype + "_bus",
        standard_parameters=standard_parameters,
    )

    # central electricity bus
    create_standard_parameter_bus(
        label="central_chp_" + gastype + "_elec_bus",
        bus_type="central_chp_" + gastype + "_electricity_bus",
        standard_parameters=standard_parameters,
    )

    # connection to central electricity bus
    create_standard_parameter_link(
        label="central_chp_" + gastype + "_elec_central_link",
        bus_1="central_chp_" + gastype + "_elec_bus",
        bus_2="central_electricity_bus",
        link_type="central_chp_elec_central_link",
        standard_parameters=standard_parameters,
    )

    # chp transformer
    chp_standard_parameters = standard_parameters.parse("transformers")

    chp_central_dict = {
        "label": "central_" + gastype + "_chp_transformer",
        "input": "central_chp_" + gastype + "_bus",
        "output": "central_chp_" + gastype + "_elec_bus",
        "output2": "central_heat_input_bus",
    }
    # read the chp standards from standard_parameters.xlsx and append
    # them to the gchp_central_dict
    chp_standard_keys = chp_standard_parameters.keys().tolist()
    for i in range(len(chp_standard_keys)):
        chp_central_dict[chp_standard_keys[i]] = chp_standard_parameters[
            chp_standard_keys[i]
        ][0]

    # produce a pandas series out of the dict above due to easier appending
    chp_series = pd.Series(chp_central_dict)
    sheets["transformers"] = sheets["transformers"].append(
        chp_series, ignore_index=True
    )


def create_buses(
    id: str,
    pv_bus: bool,
    hp_elec_bus,
    central_heat_bus,
    central_elec_bus,
    gchp,
    standard_parameters,
):
    """
    todo docstring
    """

    # house electricity bus
    create_standard_parameter_bus(
        label=str(id) + "_electricity_bus",
        bus_type="building_electricity_bus",
        standard_parameters=standard_parameters,
    )

    # house heat bus
    create_standard_parameter_bus(
        label=str(id) + "_heat_bus",
        bus_type="building_heat_bus",
        standard_parameters=standard_parameters,
    )

    if hp_elec_bus:
        # building hp electricity bus
        create_standard_parameter_bus(
            label=str(id) + "_hp_elec_bus",
            bus_type="building_hp_electricity_bus",
            standard_parameters=standard_parameters,
        )
        if gchp:
            # electricity link from building electricity bus to hp elec bus
            create_standard_parameter_link(
                label=str(id) + "_gchp_building_link",
                bus_1=str(id) + "_electricity_bus",
                bus_2=str(id) + "_hp_elec_bus",
                link_type="building_hp_elec_link",
                standard_parameters=standard_parameters,
            )

    if central_heat_bus:
        # heat link from central heat network to building heat bus
        create_standard_parameter_link(
            label=str(id) + "_central_heat_link",
            bus_1="central_heat_output_bus",
            bus_2=str(id) + "_heat_bus",
            link_type="building_central_heat_link",
            standard_parameters=standard_parameters,
        )

    # todo excess constraint costs
    if pv_bus:
        # building pv bus
        create_standard_parameter_bus(
            label=str(id) + "_pv_bus",
            bus_type="building_pv_bus",
            standard_parameters=standard_parameters,
        )

        # link from pv bus to building electricity bus
        create_standard_parameter_link(
            label=str(id) + "pv_" + str(id) + "_electricity_link",
            bus_1=str(id) + "_pv_bus",
            bus_2=str(id) + "_electricity_bus",
            link_type="building_pv_central_link",
            standard_parameters=standard_parameters,
        )
        if central_elec_bus:
            # link from pv bus to central electricity bus
            create_standard_parameter_link(
                label=str(id) + "pv_central_electricity_link",
                bus_1=str(id) + "_pv_bus",
                bus_2="central_electricity_bus",
                link_type="building_pv_central_link",
                standard_parameters=standard_parameters,
            )

            # link from central elec bus to building electricity bus
            create_standard_parameter_link(
                label=str(id) + "central_electricity_link",
                bus_1="central_electricity_bus",
                bus_2=str(id) + "_electricity_bus",
                link_type="building_central_building_link",
                standard_parameters=standard_parameters,
            )


def create_sinks(
    id: str,
    building_type: str,
    units: int,
    occupants: int,
    yoc: str,
    area: int,
    standard_parameters,
):
    """
    TODO DOCSTRING
    """
    # electricity demand
    if building_type not in ["None", "0", 0]:  # TODO
        # residential parameters
        if "RES" in building_type:
            electricity_demand_residential = {}
            electricity_demand_standard_param = standard_parameters.parse(
                "ResElecDemand"
            )
            for i in range(len(electricity_demand_standard_param)):
                electricity_demand_residential[
                    electricity_demand_standard_param["household size"][i]
                ] = [electricity_demand_standard_param[building_type + " (kWh/a)"][i]]

            if occupants <= 5:
                demand_el = electricity_demand_residential[occupants][0]
                demand_el = demand_el * units
            elif occupants > 5:
                demand_el = (electricity_demand_residential[5][0]) / 5 * occupants
                demand_el = demand_el * units

        # commercial parameters
        elif "COM" in building_type:
            electricity_demand_standard_param = standard_parameters.parse(
                "ComElecDemand"
            )
            electricity_demand_standard_param.set_index("commercial type", inplace=True)
            demand_el = electricity_demand_standard_param.loc[building_type][
                "specific demand (kWh/(sqm a))"
            ]
            net_floor_area = (
                area * 0.9
            )  # todo: give this value with standard parameter dataset
            demand_el = demand_el * net_floor_area

        create_standard_parameter_sink(
            sink_type=building_type + "_electricity_sink",
            label=str(id) + "_electricity_demand",
            sink_input=str(id) + "_electricity_bus",
            annual_demand=demand_el,
            standard_parameters=standard_parameters,
        )

    # heat demand

    # residential building
    if building_type not in ["None", "0", 0]:  # TODO
        if "RES" in building_type:
            # read standard values from standard_parameter-dataset
            heat_demand_standard_param = standard_parameters.parse("ResHeatDemand")
            heat_demand_standard_param.set_index("year of construction", inplace=True)
            if int(yoc) <= 1918:  # TODO
                yoc = "<1918"
            if units > 12:
                units = "> 12"
            specific_heat_demand = heat_demand_standard_param.loc[yoc][
                str(units) + " unit(s)"
            ]
            net_floor_area = (
                area * 0.9
            )  # todo: give this value with standard parameter dataset

            demand_heat = specific_heat_demand * net_floor_area

        # commercial building
        elif "COM" in building_type:
            heat_demand_standard_parameters = standard_parameters.parse("ComHeatDemand")
            heat_demand_standard_parameters.set_index(
                "year of construction", inplace=True
            )
            if int(yoc) <= 1918:  # TODO
                yoc = "<1918"
            demand_heat = heat_demand_standard_parameters.loc[yoc][building_type]
            net_floor_area = (
                area * 0.9
            )  # todo: give this value with standard parameter dataset
            demand_heat = demand_heat * net_floor_area

        create_standard_parameter_sink(
            sink_type=building_type + "_heat_sink",
            label=str(id) + "_heat_demand",
            sink_input=str(id) + "_heat_bus",
            annual_demand=demand_heat,
            standard_parameters=standard_parameters,
        )


def create_pv_source(
    building_id,
    plant_id,
    azimuth,
    tilt,
    area,
    pv_standard_parameters,
    latitude,
    longitude,
):
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
    pv_house_specific_dict = {
        "label": str(building_id) + "_" + str(plant_id) + "_pv_source",
        "existing capacity": 0,
        "min. investment capacity": 0,
        "output": str(building_id) + "_pv_bus",
        "Azimuth": azimuth,
        "Surface Tilt": tilt,
        "Latitude": latitude,
        "Longitude": longitude,
        "input": 0,
    }

    # read the pv standards from standard_parameters.xlsx and append
    # them to the pv_house_specific_dict
    pv_standard_keys = pv_standard_parameters.keys().tolist()
    for i in range(len(pv_standard_keys)):
        pv_house_specific_dict[pv_standard_keys[i]] = pv_standard_parameters[
            pv_standard_keys[i]
        ]  # [0]

    pv_house_specific_dict["max. investment capacity"] = (
        pv_standard_parameters["Capacity per Area (kW/m2)"] * area
    )  # [0] * area

    # produce a pandas series out of the dict above due to easier appending
    pv_series = pd.Series(pv_house_specific_dict)
    sheets["sources"] = sheets["sources"].append(pv_series, ignore_index=True)


def create_solarthermal_source(
    building_id,
    plant_id,
    azimuth,
    tilt,
    area,
    solarthermal_standard_parameters,
    latitude,
    longitude,
):
    """

    :return:
    """

    # technical parameters
    solarthermal_house_specific_dict = {
        "label": str(building_id) + "_" + str(plant_id) + "_solarthermal_source",
        "existing capacity": 0,
        "min. investment capacity": 0,
        "output": str(building_id) + "_heat_bus",
        "Azimuth": azimuth,
        "Surface Tilt": tilt,
        "Latitude": latitude,
        "Longitude": longitude,
        "input": str(building_id) + "_electricity_bus",
    }

    # read the pv standards from standard_parameters.xlsx and append
    # them to the pv_house_specific_dict
    solarthermal_standard_keys = solarthermal_standard_parameters.keys().tolist()
    for i in range(len(solarthermal_standard_keys)):
        solarthermal_house_specific_dict[
            solarthermal_standard_keys[i]
        ] = solarthermal_standard_parameters[
            solarthermal_standard_keys[i]
        ]  # [0]

    solarthermal_house_specific_dict["max. investment capacity"] = (
        solarthermal_standard_parameters["Capacity per Area (kW/m2)"] * area
    )

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
    constraint_dict = {
        "component 1": component1,
        "factor 1": factor1,
        "component 2": component2,
        "factor 2": factor2,
        "limit": limit,
    }

    sheets["competition constraints"] = sheets["competition constraints"].append(
        pd.Series(constraint_dict), ignore_index=True
    )


def create_gchp(id, area, standard_parameters):
    # gchp transformer
    # gchp_standard_parameters = standard_parameters.parse('GCHP')
    transformers_standard_parameters = standard_parameters.parse("transformers")
    transformers_standard_parameters.set_index("comment", inplace=True)
    gchp_standard_parameters = transformers_standard_parameters.loc[
        "building_gchp_transformer"
    ]

    gchp_house_specific_dict = {
        "label": str(id) + "_gchp_transformer",
        "comment": "automatically_created",
        "input": str(id) + "_hp_elec_bus",
        "output": str(id) + "_heat_bus",
        "output2": "None",
        "area": area,
        "existing capacity": 0,
        "min. investment capacity": 0,
    }

    # read the gchp standards from standard_parameters.xlsx and append
    # them to the gchp_house_specific_dict
    gchp_standard_keys = gchp_standard_parameters.keys().tolist()
    for i in range(len(gchp_standard_keys)):
        gchp_house_specific_dict[gchp_standard_keys[i]] = gchp_standard_parameters[
            gchp_standard_keys[i]
        ]  # [0]

    # produce a pandas series out of the dict above due to easier appending
    gchp_series = pd.Series(gchp_house_specific_dict)
    sheets["transformers"] = sheets["transformers"].append(
        gchp_series, ignore_index=True
    )


def create_ashp(id, standard_parameters):
    # ashp transformer
    # ashp_standard_parameters = standard_parameters.parse('ASHP')
    transformers_standard_parameters = standard_parameters.parse("transformers")
    transformers_standard_parameters.set_index("comment", inplace=True)
    ashp_standard_parameters = transformers_standard_parameters.loc[
        "building_ashp_transformer"
    ]

    ashp_house_specific_dict = {
        "label": str(id) + "_ashp_transformer",
        "comment": "automatically_created",
        "input": str(id) + "_hp_elec_bus",
        "output": str(id) + "_heat_bus",
        "output2": "None",
        "existing capacity": 0,
        "min. investment capacity": 0,
    }

    # read the ashp standards from standard_parameters.xlsx and append
    # them to the ashp_house_specific_dict
    ashp_standard_keys = ashp_standard_parameters.keys().tolist()
    for i in range(len(ashp_standard_keys)):
        ashp_house_specific_dict[ashp_standard_keys[i]] = ashp_standard_parameters[
            ashp_standard_keys[i]
        ]  # [0]

    # produce a pandas series out of the dict above due to easier appending
    ashp_series = pd.Series(ashp_house_specific_dict)
    sheets["transformers"] = sheets["transformers"].append(
        ashp_series, ignore_index=True
    )


def create_gas_heating(id, standard_parameters):
    # building gas bus
    create_standard_parameter_bus(
        label=str(id) + "_gas_bus",
        bus_type="building_gas_bus",
        standard_parameters=standard_parameters,
    )

    # define individual gas_heating_parameters
    gas_heating_house_specific_dict = {
        "label": str(id) + "_gasheating_transformer",
        "comment": "automatically_created",
        "input": str(id) + "_gas_bus",
        "output": str(id) + "_heat_bus",
        "output2": "None",
    }

    create_standard_parameter_transformer(
        specific_param=gas_heating_house_specific_dict,
        standard_parameters=standard_parameters,
        standard_param_name="building_gasheating_transformer",
    )


def create_electric_heating(id, standard_parameters):
    # # building gas bus
    # create_standard_parameter_bus(label=str(id) + "_gas_bus",
    #                               bus_type='building_gas_bus',
    #                               standard_parameters=standard_parameters)

    # gas heating transformer
    # gas_heating_standard_parameters = standard_parameters.parse('transformers')

    transformers_standard_parameters = standard_parameters.parse("transformers")
    transformers_standard_parameters.set_index("comment", inplace=True)
    electric_heating_standard_parameters = transformers_standard_parameters.loc[
        "building_electricheating_transformer"
    ]

    # define individual electric_heating_parameters
    electric_heating_house_specific_dict = {
        "label": str(id) + "_electricheating_transformer",
        "comment": "automatically_created",
        "input": str(id) + "_electricity_bus",
        "output": str(id) + "_heat_bus",
        "output2": "None",
    }

    # read the electricheating standards from standard_parameters.xlsx and append
    # them to the  electric_heating_house_specific_dict
    electric_heating_standard_keys = (
        electric_heating_standard_parameters.keys().tolist()
    )
    for i in range(len(electric_heating_standard_keys)):
        electric_heating_house_specific_dict[
            electric_heating_standard_keys[i]
        ] = electric_heating_standard_parameters[
            electric_heating_standard_keys[i]
        ]  # [0]

    # produce a pandas series out of the dict above due to easier appending
    electric_heating_series = pd.Series(electric_heating_house_specific_dict)
    sheets["transformers"] = sheets["transformers"].append(
        electric_heating_series, ignore_index=True
    )


def create_battery(id, standard_parameters, storage_type: str):
    """
    todo docstring
    """
    battery_house_specific_dict = {
        "label": str(id) + "_battery_storage",
        "comment": "automatically_created",
        "bus": str(id) + "_electricity_bus",
    }

    create_standard_parameter_storage(
        specific_param=battery_house_specific_dict,
        standard_parameters=standard_parameters,
        standard_param_name=storage_type + "_battery_storage",
    )


def urban_district_upscaling_pre_processing(
    pre_scenario: str,
    standard_parameter_path: str,
    output_scenario: str,
    plain_sheet: str,
):
    # todo: docstrings

    print("Creating scenario sheet...")
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
    # can be connected to the central heat network or not
    central_heating_network = False
    central_electricity_network = False

    for i, j in central.iterrows():
        if j["heat_link"] in ["Yes", "yes", 1]:
            central_heating_network = True
        if j["electricity_bus"] in ["Yes", "yes", 1]:
            central_electricity_network = True
        if j["power_to_gas"] in ["Yes", "yes", 1]:
            p2g_link = True
        else:
            p2g_link = False

    for i, j in tool.iterrows():
        # foreach building the three necessary buses will be created
        create_buses(
            j["label"],
            True if j["azimuth 1 (°)"] or j["azimuth 2 (°)"] else False,
            True if j["gchp area (m2)"] or j["ashp"] else False,
            True
            if (
                (
                    j["central heat"] == "yes"
                    or j["central heat"] == "Yes"
                    or j["central heat"] == 1
                )
                and central_heating_network
            )
            else False,
            central_electricity_network,
            True if j["gchp area (m2)"] != 0 else False,
            standard_parameters=standard_parameters,
        )
        create_sinks(
            id=j["label"],
            building_type=j["building type"],
            units=j["units"],
            occupants=j["occupants per unit"],
            yoc=j["year of construction"],
            area=j["living space"] * j["floors"],
            standard_parameters=standard_parameters,
        )

        # Define PV Standard-Parameters
        sources_standard_parameters = standard_parameters.parse("sources")
        sources_standard_parameters.set_index("comment", inplace=True)
        pv_standard_parameters = sources_standard_parameters.loc[
            "fixed photovoltaic source"
        ]

        # Define solar thermal Standard-Parameters
        solarthermal_standard_parameters = sources_standard_parameters.loc[
            "solar_thermal_collector"
        ]

        # create pv-sources and solar thermal-sources including area competition
        for i in range(1, 5):
            if j["azimuth %1d (°)" % i]:
                plant_id = str(i)
                if j["photovoltaic"] in ["yes", "Yes", 1]:
                    create_pv_source(
                        building_id=j["label"],
                        plant_id=plant_id,
                        azimuth=j["azimuth %1d (°)" % i],
                        tilt=j["surface tilt %1d (°)" % i],
                        area=j["roof area %1d (m²)" % i],
                        latitude=j["latitude"],
                        longitude=j["longitude"],
                        pv_standard_parameters=pv_standard_parameters,
                    )
                if j["solarthermal"] in ["yes", "Yes", 1]:
                    create_solarthermal_source(
                        building_id=j["label"],
                        plant_id=plant_id,
                        azimuth=j["azimuth %1d (°)" % i],
                        tilt=j["surface tilt %1d (°)" % i],
                        area=j["roof area %1d (m²)" % i],
                        latitude=j["latitude"],
                        longitude=j["longitude"],
                        solarthermal_standard_parameters=solarthermal_standard_parameters,
                    )
                if j["photovoltaic"] in ["yes", "Yes", 1] and j["solarthermal"] in [
                    "yes",
                    "Yes",
                    1,
                ]:
                    create_competition_constraint(
                        component1=j["label"] + "_" + plant_id + "_pv_source",
                        factor1=1 / pv_standard_parameters["Capacity per Area (kW/m2)"],
                        component2=j["label"] + "_" + plant_id + "_solarthermal_source",
                        factor2=1
                        / solarthermal_standard_parameters["Capacity per Area (kW/m2)"],
                        limit=j["roof area %1d (m²)" % i],
                    )

        # creates heat-pumps
        if j["gchp"] in ["Yes", "yes", 1] and j["gchp area (m2)"]:
            create_gchp(
                id=j["label"],
                area=j["gchp area (m2)"],
                standard_parameters=standard_parameters,
            )

        # creates heat-pumps
        if j["ashp"] in ["Yes", "yes", 1]:
            create_ashp(id=j["label"], standard_parameters=standard_parameters)

        # creates gasheating-system
        if j["gas heating"] in ["Yes", "yes", 1]:
            create_gas_heating(id=j["label"], standard_parameters=standard_parameters)

            # natural gas connection link to p2g-ng-bus
            if p2g_link == True:
                create_standard_parameter_link(
                    label="central_naturalgas_" + j["label"] + "link",
                    bus_1="central_naturalgas_bus",
                    bus_2=j["label"] + "_gas_bus",
                    link_type="central_naturalgas_building_link",
                    standard_parameters=standard_parameters,
                )

        # creates electric heating-system
        if j["electric heating"] in ["yes", "Yes", 1]:
            create_electric_heating(
                id=j["label"], standard_parameters=standard_parameters
            )

        # battery storage
        if j["battery storage"] in ["Yes", "yes", 1]:
            create_battery(
                id=j["label"],
                standard_parameters=standard_parameters,
                storage_type="building",
            )

        print(str(j["label"]) + " subsystem added to scenario sheet.")

    # add general energy system information to "energysystem"-sheet
    copy_standard_parameter_sheet(
        sheet_tbc="energysystem", standard_parameters=standard_parameters
    )

    # adds weather data to "weather data"-sheet
    copy_standard_parameter_sheet(
        sheet_tbc="weather data", standard_parameters=standard_parameters
    )

    # adds weather data to "weather data"-sheet
    copy_standard_parameter_sheet(
        sheet_tbc="time series", standard_parameters=standard_parameters
    )
    # open the new excel file and add all the created components
    j = 0
    writer = pd.ExcelWriter(output_scenario, engine="xlsxwriter")

    for i in sheets:
        sheets[i].to_excel(writer, worksheets[j], index=False)
        j = j + 1
    print("Scenario created. It can now be executed.")
    writer.save()


if __name__ == "__main__":
    urban_district_upscaling_pre_processing(
        pre_scenario=os.path.dirname(__file__) + r"\pre_scenario.xlsx",
        standard_parameter_path=os.path.dirname(__file__)
        + r"\standard_parameters.xlsx",
        output_scenario=os.path.dirname(__file__) + r"\test_scenario.xlsx",
        plain_sheet=os.path.dirname(__file__) + r"\plain_scenario.xlsx",
    )
