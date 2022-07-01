import xlsxwriter
import pandas as pd
import program_files.urban_district_upscaling.clustering as clustering_py
from program_files.urban_district_upscaling.components \
    import Sink, Source, Storage, Transformer, Link, Bus, Insulation, \
        Central_components


true_bools = ["yes", "Yes", 1]


def append_component(sheet: str, comp_parameter: dict):
    """
        :param sheet:
        :type sheet: str
        :param comp_parameter:
        :type comp_parameter: dict
    """
    series = pd.Series(comp_parameter)
    sheets[sheet] = pd.concat([sheets[sheet], pd.DataFrame([series])])


def read_standard_parameters(name, param_type, index):
    """
        searches the right entry within the standard parameter sheet

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


def create_standard_parameter_comp(specific_param: dict,
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
        :param standard_param_name: string defining the storage type
                                    (e.g. central_naturalgas_storage,...)
                                    to locate the right standard parameters
        :type standard_param_name: str
    """
    # extracts the storage specific standard values from the
    # standard_parameters dataset
    standard_param, standard_keys = read_standard_parameters(
        standard_param_name, type, index)
    # insert standard parameters in the components dataset (dict)
    for i in range(len(standard_keys)):
        specific_param[standard_keys[i]] = standard_param[standard_keys[i]]
    # appends the new created component to storages sheet
    append_component(type, specific_param)


def create_buses(building, pv_bus: bool, central_elec_bus: bool, gchps):
    """
        todo docstring
        :param pv_bus: boolean which defines rather a pv bus is created or not
        :type pv_bus: bool
        :param central_elec_bus: defines rather buildings can be
                                 connected to central elec net or not
        :type central_elec_bus: bool


    """
    hp_elec_bus = \
        True if (building['parcel'] != 0
                 and building["gchp"] not in ["No", "no", 0]) \
        or building['ashp'] not in ["No", "no", 0] else False
    gchp = True if building['parcel'] != 0 else False,
    gchp_heat_bus = (building['parcel'][-9:] + "_heat_bus") \
        if (building['parcel'] != 0 and building['parcel'][-9:] in gchps) \
        else None
    gchp_elec_bus = (building['parcel'][-9:] + "_hp_elec_bus") \
        if (building['parcel'] != 0 and building['parcel'][-9:] in gchps) \
        else None

    if building["building type"] == "RES":
        bus = 'building_res_electricity_bus'
    elif building["building type"] == "IND":
        bus = 'building_ind_electricity_bus'
    else:
        bus = 'building_com_electricity_bus'
    if pv_bus or building["building type"] != "0":
        # house electricity bus
        Bus.create_standard_parameter_bus(
            label=(str(building['label']) + "_electricity_bus"),
            bus_type=bus)
        if central_elec_bus:
            # link from central elec bus to building electricity bus
            Link.create_link(
                label=str(building['label']) + "central_electricity_link",
                bus_1="central_electricity_bus",
                bus_2=str(building['label']) + "_electricity_bus",
                link_type="building_central_building_link")

    if building["building type"] not in ["0", 0]:
        # house heat bus
        Bus.create_standard_parameter_bus(
            label=str(building['label']) + "_heat_bus",
            bus_type='building_heat_bus',
            dh="1" if building["latitude"] is not None else "0",
            cords=[building["latitude"], building["longitude"]])

    if hp_elec_bus:
        # building hp electricity bus
        Bus.create_standard_parameter_bus(
            label=str(building['label']) + "_hp_elec_bus",
            bus_type='building_hp_electricity_bus',
            dh="0")
        # electricity link from building electricity bus to hp elec bus
        Link.create_link(label=str(building['label']) + "_gchp_building_link",
                         bus_1=str(building['label']) + "_electricity_bus",
                         bus_2=str(building['label']) + "_hp_elec_bus",
                         link_type="building_hp_elec_link")

        if gchp and gchp_elec_bus is not None:
            Link.create_link(
                label=str(building['label']) + "_parcel_gchp_elec",
                bus_1=str(building['label']) + "_hp_elec_bus",
                bus_2=gchp_elec_bus,
                link_type="building_hp_elec_link")
            Link.create_link(label=str(building['label']) + "_parcel_gchp",
                             bus_1=gchp_heat_bus,
                             bus_2=str(building['label']) + "_heat_bus",
                             link_type="building_hp_elec_link")

    # todo excess constraint costs
    if pv_bus:
        # building pv bus
        Bus.create_standard_parameter_bus(
            label=str(building['label']) + "_pv_bus",
            bus_type='building_pv_bus')

        # link from pv bus to building electricity bus
        Link.create_link(
            label=str(building['label']) + "pv_" + str(building['label'])
                  + "_electricity_link",
            bus_1=str(building['label']) + "_pv_bus",
            bus_2=str(building['label']) + "_electricity_bus",
            link_type="building_pv_central_link")
        if central_elec_bus:
            # link from pv bus to central electricity bus
            Link.create_link(
                label=str(building['label']) + "pv_central_electricity_link",
                bus_1=str(building['label']) + "_pv_bus",
                bus_2="central_electricity_bus",
                link_type="building_pv_central_link")
        

def load_input_data(plain_sheet, standard_parameter_path, pre_scenario):
    global sheets
    global standard_parameters
    sheets = {}
    columns = {}
    # get keys from plain scenario
    plain_sheet = pd.ExcelFile(plain_sheet)
    # load standard parameters from standard parameter file
    standard_parameters = pd.ExcelFile(standard_parameter_path)
    # import the sheet which is filled by the user
    pre_scenario_pd = pd.ExcelFile(pre_scenario)
    
    for i in range(1, len(plain_sheet.sheet_names)):
        if plain_sheet.sheet_names[i] not in ["weather data", "time series"]:
            columns[plain_sheet.sheet_names[i]] = \
                plain_sheet.parse(plain_sheet.sheet_names[i]).keys()
    # append worksheets' names to the list of worksheets
    worksheets = [column for column in columns.keys()]
    # get spreadsheet units from plain sheet
    for sheet in worksheets:
        sheets.update({sheet: pd.DataFrame(columns=(columns[sheet]))})
        units_series = pd.Series(data={a: "x" for a in sheets[sheet].keys()})
        sheets[sheet] = pd.concat([sheets[sheet],
                                   pd.DataFrame([units_series])])
    worksheets += ["weather data", "time series"]
    
    # get the input sheets
    tool = pre_scenario_pd.parse("tool")
    parcel = pre_scenario_pd.parse("parcel")
    central = pre_scenario_pd.parse("central")
    
    return central, parcel, tool, worksheets


def create_gchp(tool, parcel):
    # create GCHPs parcel wise
    gchps = {}
    for num, parcel in parcel.iterrows():
        build_parcel = tool[(tool["active"] == 1)
                            & (tool["gchp"].isin(["Yes", "yes", 1]))
                            & (tool["parcel"] == parcel['ID parcel'])]
        if not build_parcel.empty:
            gchps.update({parcel['ID parcel'][-9:]: parcel['gchp area (m²)']})
    # create gchp relevant components
    for gchp in gchps:
        Transformer.create_transformer(
                building_id=gchp,
                area=gchps[gchp],
                transformer_type="building_gchp_transformer")
        Bus.create_standard_parameter_bus(
                label=gchp + "_hp_elec_bus",
                bus_type="building_hp_electricity_bus")
        Bus.create_standard_parameter_bus(label=gchp + "_heat_bus",
                                          bus_type="building_heat_bus")
    return gchps
    

def urban_district_upscaling_pre_processing(paths: list,
                                            clustering: bool,
                                            clustering_dh: bool):
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

    print('Creating scenario sheet...')
    # loading typical scenario structure from plain sheet
    central, parcel, tool, worksheets = \
        load_input_data(paths[3], paths[1], paths[0])
    
    # create central components
    Central_components.central_comp(central, true_bools)
    
    # set variable for central heating / electricity if activated to
    # decide rather a house can be connected to the central heat
    # network / central electricity network or not
    central_electricity_network = True if central['electricity_bus'] \
        in true_bools else False
    p2g_link = True if central['power_to_gas'] in true_bools else False

    gchps = create_gchp(tool, parcel)
    
    for num, building in tool[tool["active"] == 1].iterrows():
        label = building["label"]
        # foreach building the three necessary buses will be created
        pv_bool = False
        for roof_num in range(1, 29):
            if building['st or pv %1d' % roof_num] == "pv&st":
                pv_bool = True
        
        create_buses(building=building, pv_bus=pv_bool, gchps=gchps,
                     central_elec_bus=central_electricity_network)
        
        Sink.create_sinks(sink_id=label,
                          building_type=building['building type'],
                          units=building['units'],
                          occupants=building['occupants per unit'],
                          yoc=building['year of construction'],
                          area=building['living space'] * building['floors'],
                          standard_parameters=standard_parameters)

        Insulation.create_building_insulation(
            building_id=label,
            yoc=building['year of construction'],
            areas=[building["windows"], building["walls_wo_windows"],
                   building["roof area"]],
            roof_type=building["rooftype"],
            standard_parameters=standard_parameters)
        
        # create sources
        Source.create_sources(building=building, clustering=clustering)
        # create transformer
        Transformer.building_transformer(building, p2g_link, true_bools)
        # create storages
        Storage.building_storages(building, true_bools)

        print(str(label) + ' subsystem added to scenario sheet.')
    for sheet_tbc in ["energysystem", "weather data", "time series",
                      "district heating"]:
        sheets[sheet_tbc] = standard_parameters.parse(sheet_tbc)

    if clustering:
        clustering_py.clustering_method(tool, standard_parameters, worksheets,
                                        sheets, central_electricity_network,
                                        clustering_dh)
    # open the new excel file and add all the created components
    j = 0
    writer = pd.ExcelWriter(paths[2], engine='xlsxwriter')
    for i in sheets:
        sheets[i].to_excel(writer, worksheets[j], index=False)
        j = j + 1
    print("Scenario created. It can now be executed.")
    writer.save()
