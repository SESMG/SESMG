import xlsxwriter
import pandas as pd

import program_files.urban_district_upscaling.clustering as clustering_py
from program_files.urban_district_upscaling.components import (
    Sink,
    Source,
    Storage,
    Transformer,
    Link,
    Bus,
    Insulation,
    Central_components,
)

true_bools = ["yes", "Yes", 1]


def append_component(sheets, sheet: str, comp_parameter: dict):
    """
    :param sheets:
    :type sheets:
    :param sheet:
    :type sheet: str
    :param comp_parameter:
    :type comp_parameter: dict
    """
    series = pd.Series(comp_parameter)
    sheets[sheet] = pd.concat([sheets[sheet], pd.DataFrame([series])])
    return sheets


def read_standard_parameters(name, param_type, index, standard_parameters):
    """
        searches the right entry within the standard parameter sheet

        :param name: component's name
        :type name: str
        :param param_type: determines the technology type
        :type param_type: str
        :param index: defines on which column the index of the parsed \
            Dataframe will be set in order to locate the component's \
            name specific row
        :param standard_parameters:
        :returns standard_param: technology specific parameters of name
        :rtype standard_param: pandas.Dataframe
        :returns standard_keys: technology specific keys of name
        :rtype standard_keys: list
    """
    # get the param_type sheet from standard parameters
    standard_param_df = standard_parameters.parse(param_type)
    # reset the dataframes index to the index variable set in args
    standard_param_df.set_index(index, inplace=True)
    if name in list(standard_param_df.index):
        # locate the row labeled name
        standard_param = standard_param_df.loc[name]
        # get the keys of the located row
        standard_keys = standard_param.keys().tolist()
        # return parameters and keys
        return standard_param, standard_keys
    else:
        raise ValueError


def create_standard_parameter_comp(
    specific_param: dict, standard_parameter_info: list, sheets,
    standard_parameters):
    """
        creates a storage with standard_parameters, based on the
        standard parameters given in the "standard_parameters" dataset
        and adds it to the "sheets"-output dataset.

        :param specific_param: dictionary holding the storage specific
                               parameters (e.g. ng_storage specific, ...)
        :type specific_param: dict
        :param standard_parameter_info: \
            list defining the component standard parameter label [0], \
            the components type [1] and the index of the components \
            standard parameter worksheets
        :type standard_parameter_info: list
        :param sheets:
        :type sheets:
        :return: - **sheets** () -
    """
    # extracts the storage specific standard values from the
    # standard_parameters dataset
    standard_param, standard_keys = read_standard_parameters(
        standard_parameter_info[0],
        standard_parameter_info[1],
        standard_parameter_info[2],
        standard_parameters
    )
    # insert standard parameters in the components dataset (dict)
    for i in range(len(standard_keys)):
        specific_param[standard_keys[i]] = standard_param[standard_keys[i]]
    # appends the new created component to storages sheet
    return append_component(sheets, standard_parameter_info[1][2:], specific_param)


def create_buses(building, central_elec_bus: bool, gchps, sheets,
                 standard_parameters):
    """
    todo docstring
    :param building:
    :type building:
    :param central_elec_bus: defines rather buildings can be
                             connected to central elec net or not
    :type central_elec_bus: bool
    :param gchps:
    :type gchps:
    :param sheets:
    :type sheets:
    """
    hp_elec_bus = (
        True
        if (building["parcel ID"] != 0 and building["gchp"] not in ["No", "no", 0])
        or building["ashp"] not in ["No", "no", 0]
        else False
    )

    gchp = True if building["parcel ID"] != 0 else False

    gchp_heat_bus = (
        (building["parcel ID"][-9:] + "_heat_bus")
        if (building["parcel ID"] != 0 and building["parcel ID"][-9:] in gchps)
        else None
    )

    gchp_elec_bus = (
        (building["parcel ID"][-9:] + "_hp_elec_bus")
        if (building["parcel ID"] != 0 and building["parcel ID"][-9:] in gchps)
        else None
    )

    # foreach building the three necessary buses will be created
    pv_bus = False
    for roof_num in range(1, 29):
        if building["st or pv %1d" % roof_num] == "pv&st":
            pv_bus = True

    if building["building type"] in ["SFB", "MFB", "0", 0]:
        bus = "building_res_electricity_bus"
    elif building["building type"] == "IND":
        bus = "building_ind_electricity_bus"
    else:
        bus = "building_com_electricity_bus"
    if pv_bus or building["building type"] != "0":
        # house electricity bus
        sheets = Bus.create_standard_parameter_bus(
            label=(str(building["label"]) + "_electricity_bus"),
            bus_type=bus,
            sheets=sheets,
            standard_parameters=standard_parameters
        )
        if central_elec_bus:
            # link from central elec bus to building electricity bus
            sheets = Link.create_link(
                label=str(building["label"]) + "central_electricity_link",
                bus_1="central_electricity_bus",
                bus_2=str(building["label"]) + "_electricity_bus",
                link_type="building_central_building_link",
                sheets=sheets,
                standard_parameters=standard_parameters
            )

    if building["building type"] not in ["0", 0]:
        # house heat bus
        sheets = Bus.create_standard_parameter_bus(
            label=str(building["label"]) + "_heat_bus",
            bus_type="building_heat_bus",
            sheets=sheets,
            cords=[building["latitude"],
                   building["longitude"],
                   1 if building["central heat"] not in ["No", "no", 0, "0"] else 0],
            standard_parameters=standard_parameters
        )

    if hp_elec_bus:
        # building hp electricity bus
        sheets = Bus.create_standard_parameter_bus(
            label=str(building["label"]) + "_hp_elec_bus",
            bus_type="building_hp_electricity_bus",
            sheets=sheets,
            standard_parameters=standard_parameters
        )
        # electricity link from building electricity bus to hp elec bus
        sheets = Link.create_link(
            label=str(building["label"]) + "_gchp_building_link",
            bus_1=str(building["label"]) + "_electricity_bus",
            bus_2=str(building["label"]) + "_hp_elec_bus",
            link_type="building_hp_elec_link",
            sheets=sheets,
            standard_parameters=standard_parameters
        )

        if gchp and gchp_elec_bus is not None:
            sheets = Link.create_link(
                label=str(building["label"]) + "_parcel_gchp_elec",
                bus_1=str(building["label"]) + "_hp_elec_bus",
                bus_2=gchp_elec_bus,
                link_type="building_hp_elec_link",
                sheets=sheets,
                standard_parameters=standard_parameters
            )
            sheets = Link.create_link(
                label=str(building["label"]) + "_parcel_gchp",
                bus_1=gchp_heat_bus,
                bus_2=str(building["label"]) + "_heat_bus",
                link_type="building_hp_elec_link",
                sheets=sheets,
                standard_parameters=standard_parameters
            )

    # todo excess constraint costs
    if pv_bus:
        # building pv bus
        sheets = Bus.create_standard_parameter_bus(
            label=str(building["label"]) + "_pv_bus",
            bus_type="building_pv_bus",
            sheets=sheets,
            standard_parameters=standard_parameters
        )

        # link from pv bus to building electricity bus
        sheets = Link.create_link(
            label=str(building["label"])
            + "pv_"
            + str(building["label"])
            + "_electricity_link",
            bus_1=str(building["label"]) + "_pv_bus",
            bus_2=str(building["label"]) + "_electricity_bus",
            link_type="building_pv_central_link",
            sheets=sheets,
            standard_parameters=standard_parameters
        )
        if central_elec_bus:
            # link from pv bus to central electricity bus
            sheets = Link.create_link(
                label=str(building["label"]) + "pv_central_electricity_link",
                bus_1=str(building["label"]) + "_pv_bus",
                bus_2="central_electricity_bus",
                link_type="building_pv_central_link",
                sheets=sheets,
                standard_parameters=standard_parameters
            )

    return sheets


def load_input_data(plain_sheet, standard_parameter_path, pre_scenario):
    global standard_parameters
    sheets = {}
    columns = {}
    # get keys from plain scenario
    plain_sheet = pd.ExcelFile(plain_sheet)
    # get columns from plain sheet
    for sheet in plain_sheet.sheet_names:
        if sheet not in ["weather data", "time series"]:
            columns[sheet] = plain_sheet.parse(sheet).keys()

    # append worksheets' names to the list of worksheets
    worksheets = [column for column in columns.keys()]
    # get spreadsheet units from plain sheet
    for sheet in worksheets:
        sheets.update({sheet: pd.DataFrame(columns=(columns[sheet]))})
        units_series = pd.Series(data={a: "x" for a in sheets[sheet].keys()})
        sheets[sheet] = pd.concat([sheets[sheet], pd.DataFrame([units_series])])
    worksheets += ["weather data", "time series"]

    # load standard parameters from standard parameter file
    standard_parameters = pd.ExcelFile(standard_parameter_path)
    # import the sheet which is filled by the user
    pre_scenario_pd = pd.ExcelFile(pre_scenario)

    # get the input sheets
    building_data = pre_scenario_pd.parse("1 - building data")
    building_inv_data = pre_scenario_pd.parse("2 - building investment data")
    building_data.set_index("label", inplace=True, drop=True)
    building_inv_data.set_index("label", inplace=True, drop=True)
    tool = building_data.join(building_inv_data, how="inner")
    tool.reset_index(inplace=True, drop=False)
    tool = tool.drop(0)
    parcel = pre_scenario_pd.parse("2.1 - gchp areas")
    central = pre_scenario_pd.parse("3 - central investment data")
    central = central.drop(0)

    return sheets, central, parcel, tool, worksheets


def get_central_comp_active_status(central, technology):
    """

    :param central:
    :type central: pandas.DataFrame
    :param technology:
    :type technology: str

    :return:
    """
    if (
        central.loc[central["technology"] == technology]["active"].values[0]
        in true_bools
    ):
        return True
    else:
        return False


def create_gchp(tool, parcel, sheets):
    # create GCHPs parcel wise
    gchps = {}
    for num, parcel in parcel.iterrows():
        build_parcel = tool[
            (tool["active"] == 1)
            & (tool["gchp"].isin(["Yes", "yes", 1]))
            & (tool["parcel ID"] == parcel["ID parcel"])
        ]
        if not build_parcel.empty:
            gchps.update({parcel["ID parcel"][-9:]: parcel["gchp area (m²)"]})
    # create gchp relevant components
    for gchp in gchps:
        sheets = Transformer.create_transformer(
            building_id=gchp,
            area=gchps[gchp],
            transf_type="building_gchp_transformer",
            sheets=sheets,
            flow_temp=60,
            standard_parameters=standard_parameters
        )
        sheets = Bus.create_standard_parameter_bus(
            label=gchp + "_hp_elec_bus",
            bus_type="building_hp_electricity_bus",
            sheets=sheets,
            standard_parameters=standard_parameters
        )
        sheets = Bus.create_standard_parameter_bus(
            label=gchp + "_heat_bus", bus_type="building_heat_bus", sheets=sheets,
            standard_parameters=standard_parameters
        )
    return gchps, sheets


def urban_district_upscaling_pre_processing(
    paths: list, clustering: bool, clustering_dh: bool
):
    """
        TODO DOCSTRING TEXT
        :param paths: path of the pre_scenario file [0] \
                      path of the standard_parameter file [1] \
                      path to which the scenario should be created [2]\
                      path to plain sheet file (holding structure) [3]
        :type paths: list
        :param clustering: boolean for decision rather the buildings are
                           clustered spatially
        :tpye clustering: bool
        :param clustering_dh: boolean for decision rather the district
            heating connection will be clustered cluster_id wise
        :type clustering_dh: bool
    """

    print("Creating scenario sheet...")
    # loading typical scenario structure from plain sheet
    sheets, central, parcel, tool, worksheets = load_input_data(
        paths[3], paths[1], paths[0]
    )
    
    for sheet_tbc in [
        "energysystem",
        "weather data",
        "time series",
        "district heating",
    ]:
        if sheet_tbc not in pd.ExcelFile(paths[0]).sheet_names:
            if sheet_tbc in standard_parameters.sheet_names:
                sheets[sheet_tbc] = standard_parameters.parse(
                    sheet_tbc,
                    parse_dates=["timestamp"]
                    if sheet_tbc in ["weather data", "time series"]
                    else [],
                )
            if "4 - time series data" in pd.ExcelFile(paths[0]).sheet_names:
                sheets["weather data"] = pd.ExcelFile(paths[0]).parse(
                    "4 - time series data", parse_dates=["timestamp"]
                )
                sheets["time series"] = pd.ExcelFile(paths[0]).parse(
                    "4 - time series data", parse_dates=["timestamp"]
                )
            if "3.1 - streets" in pd.ExcelFile(paths[0]).sheet_names:
                sheets["district heating"] = pd.ExcelFile(paths[0]).parse(
                    "3.1 - streets"
                )
        else:
            sheets[sheet_tbc] = pd.ExcelFile(paths[0]).parse(
                sheet_tbc,
                parse_dates=["timestamp"]
                if sheet_tbc in ["weather data", "time series"]
                else [],
            )
    
    # set variable for central heating / electricity if activated to
    # decide rather a house can be connected to the central heat
    # network / central electricity network or not
    central_electricity_network = get_central_comp_active_status(
        central, "electricity_exchange"
    )

    p2g_link = get_central_comp_active_status(central, "power_to_gas")

    # create central components
    sheets = Central_components.central_comp(
        central, true_bools, sheets, standard_parameters)

    gchps, sheets = create_gchp(tool, parcel, sheets)
    for num, building in tool[tool["active"] == 1].iterrows():
        sheets = create_buses(
            building=building,
            gchps=gchps,
            sheets=sheets,
            central_elec_bus=central_electricity_network,
            standard_parameters=standard_parameters
        )

        sheets = Sink.create_sinks(
            building=building, standard_parameters=standard_parameters, sheets=sheets
        )

        sheets = Insulation.create_building_insulation(
            building=building, sheets=sheets, standard_parameters=standard_parameters
        )

        # create sources
        sheets = Source.create_sources(
            building=building, clustering=clustering, sheets=sheets,
            standard_parameters=standard_parameters
        )
        # create transformer
        sheets = Transformer.building_transformer(
            building=building, p2g_link=p2g_link, true_bools=true_bools,
            sheets=sheets, standard_parameters=standard_parameters
        )
        # create storages
        sheets = Storage.building_storages(
            building=building, true_bools=true_bools, sheets=sheets,
            standard_parameters=standard_parameters
        )

        print(str(building["label"]) + " subsystem added to scenario sheet.")

    if clustering:
        sheets = clustering_py.clustering_method(
            tool,
            standard_parameters,
            sheets,
            central_electricity_network,
            clustering_dh,
        )
    
    # open the new excel file and add all the created components
    j = 0
    writer = pd.ExcelWriter(paths[2], engine="xlsxwriter")
    for i in sheets:
        sheets[i].to_excel(writer, worksheets[j], index=False)
        j = j + 1
    print("Scenario created. It can now be executed.")
    writer.save()
