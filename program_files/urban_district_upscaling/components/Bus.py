"""
    Christian Klemm - christian.klemm@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
    Janik Budde - janik.budde@fh-muenster.de
"""
import pandas


def create_standard_parameter_bus(label: str, bus_type: str, sheets: dict,
                                  standard_parameters: pandas.ExcelFile,
                                  coords=None, shortage_cost=None,
                                  shortage_emission=None) -> dict:
    """
        Creates a bus with standard_parameters, based on the standard
        parameters given in the "standard_parameters" dataset and adds
        it to the "sheets"-output dataset.
    
        :param label: label, the created bus will be given
        :type label: str
        :param bus_type: defines, which set of standard param. will be
                         given to the dict
        :type bus_type: str
        :param sheets: dictionary containing the pandas.Dataframes that\
                will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        :param coords: latitude / longitude / dh column of the given \
            bus used to connect a producer bus to district heating \
            network
        :type coords: list
        :param shortage_cost: If the user wants to map a shortage \
            price that differs from the standard parameter, this value \
            != None. This will overwrite the value from the standard \
            parameters.
        :type shortage_cost: float
        :param shortage_emission: If the user wants to map a shortage \
            emission that differs from the standard parameter, this \
            value != None. This will overwrite the value from the \
            standard parameters.
        :type shortage_emission: float
        
        :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    from program_files import read_standard_parameters, append_component
    
    # define individual values
    bus_dict = {"label": label}
    # extracts the bus specific standard values from the
    # standard_parameters dataset
    standard_param, standard_keys = read_standard_parameters(
            name=bus_type,
            parameter_type="1_buses",
            index="bus type",
            standard_parameters=standard_parameters
    )
    # insert standard parameters in the components dataset (dict)
    for i in range(len(standard_keys)):
        bus_dict[standard_keys[i]] = standard_param.loc[bus_type,
                                                        standard_keys[i]]
    # defines rather a district heating connection is possible
    if coords is not None:
        bus_dict.update(
                {"district heating conn. (exergy)": coords[2],
                 "lat": coords[0], "lon": coords[1]})
    else:
        bus_dict.update({"district heating conn. (exergy)": float(0)})
    # If the user wants to map a shortage price that differs from the
    # standard parameter
    if shortage_cost is not None:
        bus_dict.update({"shortage costs": shortage_cost})
    if shortage_emission is not None:
        bus_dict.update({"shortage constraint costs": shortage_emission})
    # appends the new created component to buses sheet
    return append_component(sheets, "buses", bus_dict)


def check_rather_building_needs_pv_bus(building: pandas.Series) -> bool:
    """
        If the currently considered building has a PV potential area,
        the return value is true. If this is not the
        case, the return value is False.
    
        :param building: pandas.Series containing the currently \
            investigated building's row from the US Input sheet.
        :type building: pandas.Series
        
        :returns: **pv_bus** (bool) - boolean deciding rather a pv bus \
            will be added to the model definition file or not.
    """
    from program_files import column_exists
    # current pv potential number
    roof_num = 1
    # iterate threw all roof areas to check rather there is a pv
    # potential
    while column_exists(building, str("roof area %1d" % roof_num)):
        # if there is one pv column containing "true" entries
        if building["pv %1d" % roof_num] not in ["No", "no", "0"]:
            return True
        roof_num += 1
    # if there is no "true" pv potential found
    return False


def calculate_average_shortage_costs(standard_parameters: pandas.ExcelFile,
                                     sink_parameters: list,
                                     total_annual_demand: float,
                                     fuel_type: str,
                                     electricity: bool):
    """

    """
    bus = standard_parameters.parse(sheet_name="1_buses",
                                    index_col="bus type",
                                    na_filter=False)
    residential_share = ((sink_parameters[0 if electricity else 4]
                          / total_annual_demand)
                         * bus.loc[fuel_type + " bus residential decentral"][
                             "shortage costs"])
    commercial_share = ((sink_parameters[1 if electricity else 5]
                         / total_annual_demand)
                        * bus.loc[fuel_type + " bus commercial decentral"][
                            "shortage costs"])
    industrial_share = ((sink_parameters[2 if electricity else 6]
                         / total_annual_demand)
                        * bus.loc[fuel_type + " bus industrial decentral"][
                            "shortage costs"])
    
    return residential_share + commercial_share + industrial_share


def create_building_electricity_bus_and_central_link(
        bus: str, sheets: dict, building: pandas.Series,
        standard_parameters: pandas.ExcelFile,
        central_electricity_bus: bool) -> dict:
    """
        In this method, the in-house electricity bus is created if the
        building has a pv potential surface and/or an electrical load
        profile is available for that building. If the user has enabled
        a local electricity exchange, the in-house electricity bus is
        connected to the local exchange via a link. These two
        components are added to the return "sheets" dictionary.
        
        :param bus: string defining the bus type of the house intern \
            electricity bus
        :type bus: str
        :param sheets: dictionary containing the pandas.Dataframes that\
                will represent the model definition's Spreadsheets
        :type sheets: dict
        :param building: pandas.Series containing the currently \
            investigated building's row from the US Input sheet.
        :type building: pandas.Series
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        :param central_electricity_bus: boolean which represents the \
            users decision rather a local exchange of electricity is \
            possible or not
        :type central_electricity_bus: bool
        
        :returns: - **sheets** (dict): dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was updated within this \
            method
    """
    from program_files.urban_district_upscaling.components import Link
    pv_bus = check_rather_building_needs_pv_bus(building=building)
    # get the users shortage costs input
    shortage_cost = building["electricity cost"] \
        if building["electricity cost"] != "standard" else None
    shortage_emission = building["electricity emission"] \
        if building["electricity emission"] != "standard" else None
    # create the building electricity bus if the building has a pv
    # system or gets an electricity demand later on
    if pv_bus or building["building type"] not in ["0", 0]:
        # create the building electricity bus
        sheets = create_standard_parameter_bus(
                label=(str(building["label"]) + "_electricity_bus"),
                bus_type=bus,
                sheets=sheets,
                standard_parameters=standard_parameters,
                shortage_cost=shortage_cost,
                shortage_emission=shortage_emission
        )
        # create link from central electricity bus to building
        # electricity bus if the central electricity exchange is enabled
        if central_electricity_bus:
            sheets = Link.create_link(
                    label=str(building["label"]) + "_central_electricity_link",
                    bus_1="central_electricity_bus",
                    bus_2=str(building["label"]) + "_electricity_bus",
                    link_type="electricity central link decentral",
                    sheets=sheets,
                    standard_parameters=standard_parameters
            )
    
    return sheets


def create_pv_bus_and_links(building: pandas.Series, sheets: dict,
                            standard_parameters: pandas.ExcelFile,
                            central_electricity_bus: bool) -> dict:
    """
        In this method, the PV bus of the considered building is
        created and connected to the in-house electricity bus and, if
        available, to the central electricity bus. The created
        components are appended to the return data structure "sheets",
        which represents the model definition at the end.

        :param building: Series containing the building specific \
            parameters
        :type building: pandas.Series
        :param sheets: dictionary containing the pandas.Dataframes that\
            will represent the model definition's Spreadsheets
        :type sheets: dict
        :param standard_parameters: pandas imported ExcelFile \
            containing the non-building specific technology data
        :type standard_parameters: pandas.ExcelFile
        :param central_electricity_bus: boolean representing the \
            user's decision rather a local electricity exchange is \
            possible or not
        :type central_electricity_bus: bool

         :return: - **sheets** (dict) - dictionary containing the \
            pandas.Dataframes that will represent the model \
            definition's Spreadsheets which was modified in this method
    """
    from program_files.urban_district_upscaling.components import Link
    # create building pv bus
    sheets = create_standard_parameter_bus(
            label=str(building["label"]) + "_pv_bus",
            bus_type="electricity bus photovoltaic decentral",
            sheets=sheets,
            standard_parameters=standard_parameters
    )
    
    # create link from pv bus to building electricity bus
    sheets = Link.create_link(
            label=str(building["label"])
            + "_pv_self_consumption_electricity_link",
            bus_1=str(building["label"]) + "_pv_bus",
            bus_2=str(building["label"]) + "_electricity_bus",
            link_type="electricity photovoltaic decentral link decentral",
            sheets=sheets,
            standard_parameters=standard_parameters
    )
    
    # create link from pv bus to central electricity bus if the
    # central electricity exchange is enabled
    if central_electricity_bus:
        sheets = Link.create_link(
                label=str(building["label"]) + "_pv_central_electricity_link",
                bus_1=str(building["label"]) + "_pv_bus",
                bus_2="central_electricity_bus",
                link_type="electricity photovoltaic decentral link central",
                sheets=sheets,
                standard_parameters=standard_parameters
        )
    
    return sheets


def get_building_type_specific_electricity_bus_label(building: pandas.Series
                                                     ) -> str:
    """
        In this method, based on the building_type column, the
        distinction between RES, COM and IND is made.
    
        :param building: pandas.Series containing the currently \
            investigated building's row from the US Input sheet.
        :type building: pandas.Series
        
        :returns: **bus** (str) - string holding the buildings \
            electricity bus type
    """
    # define the building electricity bus type based on the building
    # type
    if building["building type"] in ["single family building",
                                     "multi family building", "0", 0]:
        return "electricity bus residential decentral"
    elif building["building type"] == "IND":
        return "electricity bus industrial decentral"
    else:
        return "electricity bus commercial decentral"


def create_cluster_electricity_buses(
        building: list, cluster: str, sheets: dict,
        standard_parameters: pandas.ExcelFile) -> dict:
    """
        Method creating the building type specific electricity buses and
        connecting them to the main cluster electricity bus

        :param building: List holding the building label, parcel ID \
            and building type
        :type building: list
        :param cluster: Cluster id
        :type cluster: str
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
    from . import Link
    if len(sheets["buses"]) > 0:
        index_list = list(sheets["buses"]["label"])
    else:
        index_list = []
    # ELECTRICITY BUSES
    # get building type to specify bus type to be created
    if (str(cluster) + "_residential_electricity_bus" not in index_list
            and building[2] in ["single family building",
                                "multi family building"]):
        bus_type = "residential"
    elif (str(cluster) + "_commercial_electricity_bus" not in index_list
          and "commercial" in building[2]):
        bus_type = "commercial"
    elif (str(cluster) + "_industrial_electricity_bus" not in index_list
          and "industrial" in building[2]):
        bus_type = "industrial"
    else:
        bus_type = None
    # if the considered building type is in (RES, COM, IND)
    if bus_type:
        # create building type specific bus
        sheets = create_standard_parameter_bus(
                label=str(cluster) + "_" + bus_type + "_electricity_bus",
                bus_type="electricity bus " + bus_type + " decentral",
                sheets=sheets,
                standard_parameters=standard_parameters
        )
        # reset index to label to ensure further attachments
        sheets["buses"].set_index("label", inplace=True, drop=False)
        
        # Creates a Bus connecting the cluster electricity bus with
        # the res electricity bus
        sheets = Link.create_link(
                label=str(cluster) + "_" + bus_type + "_electricity_link",
                bus_1=str(cluster) + "_electricity_bus",
                bus_2=str(cluster) + "_" + bus_type + "_electricity_bus",
                link_type="electricity cluster link decentral",
                sheets=sheets,
                standard_parameters=standard_parameters)
        
        # reset index to label to ensure further attachments
        sheets["links"].set_index("label", inplace=True, drop=False)
    
    return sheets


def create_cluster_averaged_bus(sink_parameters: list, cluster: str,
                                fuel_type: str, sheets: dict,
                                standard_parameters: pandas.ExcelFile) -> dict:
    """
        In this method, an average grid purchase price for natural gas \
        and heat pump electricity is calculated. This is measured \
        based on the share of the heat demand of a building type \
        (RES, COM, IND) in the total heat demand of the cluster.
        
        :param sink_parameters: list containing the cluster's sinks \
            parameter (4) res_heat_demand, (5) com_heat_demand, \
            (6) ind_heat_demand
        :type sink_parameters: list
        :param fuel_type: str defining which type of buses will be \
            clustered
        :type fuel_type: str
        :param cluster: Cluster id
        :type cluster: str
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
    type_dict = {
        "electricity": ["heatpump_electricity", "heat pump "],
        "gas": ["natural_gas", "residential "],
        "oil": ["oil", "residential "],
        "pellet": ["pellet", ""]}
    type1, type2 = type_dict.get(fuel_type)
    
    # calculate cluster's total heat demand
    total_annual_demand = sum(sink_parameters[4:7])
    if str(cluster) + "_" + type1 + "_bus" not in sheets["buses"].index:
        # create standard_parameter gas bus
        sheets = create_standard_parameter_bus(
                label=str(cluster) + "_" + type1 + "_bus",
                bus_type=fuel_type + " bus " + type2 + "decentral",
                sheets=sheets,
                standard_parameters=standard_parameters)
    
    # reindex for further attachments
    sheets["buses"].set_index("label", inplace=True, drop=False)
    
    if not fuel_type == "pellet":
        # recalculate gas bus shortage costs building type weighted
        costs_type = "shortage costs"
        sheets["buses"].loc[(str(cluster) + "_" + type1 + "_bus"),
                            costs_type] = (
            calculate_average_shortage_costs(
                    standard_parameters=standard_parameters,
                    sink_parameters=sink_parameters,
                    total_annual_demand=total_annual_demand,
                    fuel_type=fuel_type,
                    electricity=False
            ))
    return sheets
