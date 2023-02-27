import xlsxwriter
import pandas

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
from io import BytesIO

true_bools = ["yes", "Yes", 1]


def append_component(sheets: dict, sheet: str, comp_parameter: dict) -> dict:
    """
        Within this method a component with the parameters stored in \
        comp_parameter will be appended on the in sheets[sheet] stored\
        pandas.DataFrame
        
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param sheet: str which specifies which dict entry will be \
            changed
        :type sheet: str
        :param comp_parameter: component parameters which will be \
            appended as column on sheet
        :type comp_parameter: dict
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    series = pandas.Series(comp_parameter)
    sheets[sheet] = pandas.concat([sheets[sheet], pandas.DataFrame([series])])
    return sheets


def read_standard_parameters(
    name: str, param_type: str, index: str, standard_parameters: pandas.ExcelFile
):
    """
        searches the right entry within the standard parameter sheet

        :param name: component's name
        :type name: str
        :param param_type: determines the technology type
        :type param_type: str
        :param index: defines on which column the index of the parsed \
            Dataframe will be set in order to locate the component's \
            name specific row
        :type index: str
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        
        :return: - **standard_param** (pandas.Dataframe) - technology \
                    specific parameters of name
                 - **standard_keys** (list) - technology specific keys \
                    of name
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
        raise ValueError("The component type " + name + " does not exist.")


def create_standard_parameter_comp(
    specific_param: dict,
    standard_parameter_info: list,
    sheets,
    standard_parameters: pandas.ExcelFile,
) -> dict:
    """
        creates a component with standard_parameters, based on the
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
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets
    """
    # extracts the storage specific standard values from the
    # standard_parameters dataset
    standard_param, standard_keys = read_standard_parameters(
        standard_parameter_info[0],
        standard_parameter_info[1],
        standard_parameter_info[2],
        standard_parameters,
    )
    # insert standard parameters in the components dataset (dict)
    for i in range(len(standard_keys)):
        specific_param[standard_keys[i]] = standard_param[standard_keys[i]]
    # appends the new created component to storages sheet
    return append_component(sheets, standard_parameter_info[1][2:], specific_param)


def create_heat_pump_buses_links(
    building: dict, gchps: dict, sheets: dict, standard_parameters: pandas.ExcelFile
) -> dict:
    """
        In this method, all buses and links required for the heat pumps\
        are created and attached to the "buses" and "links" dataframes \
        in the sheet dictionary.
        
        :param building: dictionary holding the specific data of the \
            considered building
        :type building: dict
        :param gchps: dictionary containing the energy systems gchps
        :type gchps: dict
        :param sheets: dictionary containing the pandas.Dataframes that\
                will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets
    """
    gchp_bool = False
    gchp_heat_bus = None
    gchp_electricity_bus = None

    gchp = True if building["parcel ID"] not in [0, "0"] else False

    if gchp and building["parcel ID"][-9:] in gchps:
        gchp_bool = True
        gchp_heat_bus = building["parcel ID"][-9:] + "_heat_bus"
        gchp_electricity_bus = building["parcel ID"][-9:] + "_hp_elec_bus"

    # if a heatpump is investable for the considered building
    if gchp_bool or building["ashp"] in true_bools:
        # building hp electricity bus
        sheets = Bus.create_standard_parameter_bus(
            label=str(building["label"]) + "_hp_elec_bus",
            bus_type="building_hp_electricity_bus",
            sheets=sheets,
            standard_parameters=standard_parameters,
        )
        # electricity link from building electricity bus to hp
        # electricity bus
        sheets = Link.create_link(
            label=str(building["label"]) + "_building_hp_elec_link",
            bus_1=str(building["label"]) + "_electricity_bus",
            bus_2=str(building["label"]) + "_hp_elec_bus",
            link_type="building_hp_elec_link",
            sheets=sheets,
            standard_parameters=standard_parameters,
        )

        if gchp and gchp_electricity_bus is not None:
            # electricity link from building hp electricity bus to
            # parcel hp electricity bus
            sheets = Link.create_link(
                label=str(building["label"]) + "_parcel_gchp_elec_link",
                bus_1=str(building["label"]) + "_hp_elec_bus",
                bus_2=gchp_electricity_bus,
                link_type="building_hp_elec_link",
                sheets=sheets,
                standard_parameters=standard_parameters,
            )
            # heat link from parcel hp heat bus to building heat bus
            sheets = Link.create_link(
                label=str(building["label"]) + "_parcel_gchp_heat_link",
                bus_1=gchp_heat_bus,
                bus_2=str(building["label"]) + "_heat_bus",
                link_type="building_hp_heat_link",
                sheets=sheets,
                standard_parameters=standard_parameters,
            )
    return sheets


def column_exists(building: pandas.Series, column: str) -> bool:
    """
    Method which is used to check rather the column exists (True)
    within the building Series or not (False).

    :param building: Series which contains the building data
    :type building: pandas.Series
    :param column: label of the investigated column
    :type column: str

    :return: - **None** (bool) -
    """
    # test rather the column exists
    try:
        test = building[column]
    # if an error is thrown return false
    except KeyError:
        return False
    # else return true
    else:
        return True


def represents_int(entry: str) -> bool:
    """
    Method which is used to check rather the entry can be converted
    into an integer.

    :param entry: entry under investigation
    :type entry: str

    :return: - **None** (bool) -
    """
    # test rather the entry is convertible
    try:
        int(entry)
    # if an error is thrown return false
    except ValueError:
        return False
    # else return true
    else:
        return True


def create_building_buses_links(
    building: dict,
    central_elec_bus: bool,
    sheets: dict,
    standard_parameters: pandas.ExcelFile,
) -> dict:
    """
        In this method, all buses and links required for one building\
        are created and attached to the "buses" and "links" dataframes \
        in the sheet dictionary.
        
        :param building: dictionary containing the building specific \
                parameters
        :type building: dict
        :param central_elec_bus: defines rather buildings can be
                                 connected to central elec net or not
        :type central_elec_bus: bool
        :param sheets: dictionary containing the pandas.Dataframes that\
                will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets
    """

    # foreach building the three necessary buses will be created
    pv_bus = False
    roof_num = 1
    while column_exists(building, str("roof area %1d" % roof_num)):
        if building["pv %1d" % roof_num] not in ["No", "no", "0"]:
            pv_bus = True
        roof_num += 1

    # define the building electricity bus type based on the building
    # type
    if building["building type"] in ["SFB", "MFB", "0", 0]:
        bus = "building_res_electricity_bus"
    elif building["building type"] == "IND":
        bus = "building_ind_electricity_bus"
    else:
        bus = "building_com_electricity_bus"

    if pv_bus or building["building type"] not in ["0", 0]:
        # create the building electricity bus
        sheets = Bus.create_standard_parameter_bus(
            label=(str(building["label"]) + "_electricity_bus"),
            bus_type=bus,
            sheets=sheets,
            standard_parameters=standard_parameters,
        )
        # create link from central electricity bus to building
        # electricity bus if the central electricity exchange is enabled
        if central_elec_bus:
            sheets = Link.create_link(
                label=str(building["label"]) + "_central_electricity_link",
                bus_1="central_electricity_bus",
                bus_2=str(building["label"]) + "_electricity_bus",
                link_type="building_central_building_link",
                sheets=sheets,
                standard_parameters=standard_parameters,
            )

    if building["building type"] not in ["0", 0]:
        # house heat bus
        sheets = Bus.create_standard_parameter_bus(
            label=str(building["label"]) + "_heat_bus",
            bus_type="building_heat_bus",
            sheets=sheets,
            coords=[
                building["latitude"],
                building["longitude"],
                1 if building["central heat"] in true_bools else 0,
            ],
            standard_parameters=standard_parameters,
        )

    if pv_bus:
        # create building pv bus
        sheets = Bus.create_standard_parameter_bus(
            label=str(building["label"]) + "_pv_bus",
            bus_type="building_pv_bus",
            sheets=sheets,
            standard_parameters=standard_parameters,
        )

        # create link from pv bus to building electricity bus
        sheets = Link.create_link(
            label=str(building["label"]) + "_pv_self_consumption_electricity_link",
            bus_1=str(building["label"]) + "_pv_bus",
            bus_2=str(building["label"]) + "_electricity_bus",
            link_type="building_pv_building_link",
            sheets=sheets,
            standard_parameters=standard_parameters,
        )
        # create link from pv bus to central electricity bus if the
        # central electricity exchange is enabled
        if central_elec_bus:
            sheets = Link.create_link(
                label=str(building["label"]) + "_pv_central_electricity_link",
                bus_1=str(building["label"]) + "_pv_bus",
                bus_2="central_electricity_bus",
                link_type="building_pv_central_link",
                sheets=sheets,
                standard_parameters=standard_parameters,
            )

    return sheets


def load_input_data(plain_sheet: str, standard_parameter_path: str, pre_scenario: str):
    """
        This method is used to convert the three ExcelFiles necessary \
        for the upscaling tool into pandas structures and then return \
        them to the main method.
        
        :param plain_sheet: string containing the path to the plain \
            sheet ExcelFile, the plain sheet is used to create an \
            empty model definition file in which only the column names \
            are entered.
        :type plain_sheet: str
        :param standard_parameter_path: string containing the path to \
            the standard parameter ExcelFile
        :type plain_sheet: str
        :param pre_scenario: string containing the path to the \
            upscaling tool input file
        :type pre_scenario: str
    """
    sheets = {}
    columns = {}
    # get keys from plain scenario
    plain_sheet = pandas.ExcelFile(plain_sheet)
    # get columns from plain sheet
    for sheet in plain_sheet.sheet_names:
        if sheet not in ["weather data", "time series"]:
            columns[sheet] = plain_sheet.parse(sheet).keys()

    # append worksheets' names to the list of worksheets
    worksheets = [column for column in columns.keys()]
    # get spreadsheet units from plain sheet
    for sheet in worksheets:
        sheets.update({sheet: pandas.DataFrame(columns=(columns[sheet]))})
        units_series = pandas.Series(data={a: "x" for a in sheets[sheet].keys()})
        sheets[sheet] = pandas.concat([sheets[sheet], pandas.DataFrame([units_series])])
    worksheets += ["weather data", "time series", "pipe types"]

    # load standard parameters from standard parameter file
    standard_parameters = pandas.ExcelFile(standard_parameter_path)
    # import the sheet which is filled by the user
    pre_scenario_pd = pandas.ExcelFile(pre_scenario)

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

    return sheets, central, parcel, tool, worksheets, standard_parameters


def get_central_comp_active_status(central: pandas.DataFrame, technology: str) -> bool:
    """
        Method used to check if the central component technology is \
        enabled.
        
        :param central: pandas.DataFrame containing the central \
            components' data from the upscaling tool input file
        :type central: pandas.DataFrame
        :param technology: central component to be checked
        :type technology: str

        :return: - **None** (bool) - return rather the technology is \
            active (True) or not (False)
    """
    entry = central.loc[central["technology"] == technology]
    if entry["active"].values[0] in true_bools:
        return True
    else:
        return False


def create_gchp(
    tool: pandas.DataFrame,
    parcels: pandas.DataFrame,
    sheets: dict,
    standard_parameters: pandas.ExcelFile,
):
    """
        Method that creates a GCHP and its buses for the parcel and \
        appends them to the sheets return structure.
        
        :param tool: DataFrame containing the building data from the \
            upscaling tool's input file
        :type tool: pandas.DataFrame
        :param parcels: DataFrame containing the energy system's \
            parcels as well as their size
        :type parcels: pandas.DataFrame
        :param sheets: dictionary containing the pandas.Dataframes that\
                will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
    """
    # TODO parcel ID and ID parcel have to be unified
    # create GCHPs parcel wise
    gchps = {}
    for num, parcel in parcels.iterrows():
        build_parcel = tool[
            (tool["active"].isin(true_bools))
            & (tool["gchp"].isin(true_bools))
            & (tool["parcel ID"] == parcel["ID parcel"])
        ]
        if not build_parcel.empty:
            gchps.update({parcel["ID parcel"][-9:]: parcel["gchp area (m²)"]})
    # create gchp relevant components
    for gchp in gchps:
        # TODO What supply temperature do we use here, do we have to
        #  average that of the buildings?
        sheets = Transformer.create_transformer(
            building_id=gchp,
            area=gchps[gchp],
            transformer_type="building_gchp_transformer",
            sheets=sheets,
            standard_parameters=standard_parameters,
            flow_temp="60",
        )
        sheets = Bus.create_standard_parameter_bus(
            label=gchp + "_hp_elec_bus",
            bus_type="building_hp_electricity_bus",
            sheets=sheets,
            standard_parameters=standard_parameters,
        )
        sheets = Bus.create_standard_parameter_bus(
            label=gchp + "_heat_bus",
            bus_type="building_heat_bus",
            sheets=sheets,
            standard_parameters=standard_parameters,
        )
    return gchps, sheets


def urban_district_upscaling_pre_processing(
    paths: list, clustering: bool, clustering_dh: bool, streamlit=False
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
        :type clustering: bool
        :param clustering_dh: boolean for decision rather the district
            heating connection will be clustered cluster_id wise
        :type clustering_dh: bool
    """

    print("Creating scenario sheet...")
    # loading typical scenario structure from plain sheet
    sheets, central, parcel, tool, worksheets, standard_parameters = load_input_data(
        paths[3], paths[1], paths[0]
    )

    for sheet_tbc in [
        "energysystem",
        "weather data",
        "time series",
        "district heating",
        "8_pipe_types",
    ]:
        if sheet_tbc not in pandas.ExcelFile(paths[0]).sheet_names:
            if sheet_tbc in standard_parameters.sheet_names:
                if sheet_tbc == "8_pipe_types":
                    sheet_name = "pipe types"
                else:
                    sheet_name = sheet_tbc
                sheets[sheet_name] = standard_parameters.parse(
                    sheet_tbc,
                    parse_dates=["timestamp"]
                    if sheet_tbc in ["weather data", "time series"]
                    else [],
                )
            if "4 - time series data" in pandas.ExcelFile(paths[0]).sheet_names:
                sheets["weather data"] = pandas.ExcelFile(paths[0]).parse(
                    "4 - time series data", parse_dates=["timestamp"]
                )
                sheets["time series"] = pandas.ExcelFile(paths[0]).parse(
                    "4 - time series data", parse_dates=["timestamp"]
                )
            if "3.1 - streets" in pandas.ExcelFile(paths[0]).sheet_names:
                sheets["district heating"] = pandas.ExcelFile(paths[0]).parse(
                    "3.1 - streets"
                )
        else:
            sheets[sheet_tbc] = pandas.ExcelFile(paths[0]).parse(
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
        central, true_bools, sheets, standard_parameters
    )

    gchps, sheets = create_gchp(tool, parcel, sheets, standard_parameters)
    for num, building in tool[tool["active"] == 1].iterrows():
        sheets = create_building_buses_links(
            building=building,
            sheets=sheets,
            central_elec_bus=central_electricity_network,
            standard_parameters=standard_parameters,
        )
        sheets = create_heat_pump_buses_links(
            building=building,
            gchps=gchps,
            sheets=sheets,
            standard_parameters=standard_parameters,
        )

        sheets = Sink.create_sinks(
            building=building, standard_parameters=standard_parameters, sheets=sheets
        )

        sheets = Insulation.create_building_insulation(
            building=building, sheets=sheets, standard_parameters=standard_parameters
        )

        # create sources
        sheets = Source.create_sources(
            building=building,
            clustering=clustering,
            sheets=sheets,
            standard_parameters=standard_parameters,
        )
        # create transformer
        sheets = Transformer.building_transformer(
            building=building,
            p2g_link=p2g_link,
            sheets=sheets,
            standard_parameters=standard_parameters,
        )
        # create storages
        sheets = Storage.building_storages(
            building=building, sheets=sheets, standard_parameters=standard_parameters
        )

        print(str(building["label"]) + " subsystem added to scenario sheet.")

    if clustering:
        sheets = clustering_py.clustering_method(
            tool=tool,
            standard_parameters=standard_parameters,
            sheets=sheets,
            central_electricity_network=central_electricity_network,
            clustering_dh=clustering_dh,
        )
    if streamlit:
        output = BytesIO()
        # open the new excel file and add all the created components
        j = 0
        writer = pandas.ExcelWriter(output, engine="xlsxwriter")
        for i in sheets:
            sheets[i].to_excel(writer, worksheets[j], index=False)
            j = j + 1
        writer.close()
        processed_data = output.getvalue()
        return processed_data
    # TODO to be removed when establishing the new GUI
    else:
        # open the new excel file and add all the created components
        j = 0
        writer = pandas.ExcelWriter(paths[2], engine="xlsxwriter")
        for i in sheets:
            sheets[i].to_excel(writer, worksheets[j], index=False)
            j = j + 1
        print("Scenario created. It can now be executed.")
        writer.close()
