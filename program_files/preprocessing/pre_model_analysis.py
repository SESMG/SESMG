import pandas as pd
import pandas
import logging


def filter_result_component_types(components: pandas.DataFrame,
                                  component_type: str) -> pandas.DataFrame:
    """
        returns dataframe containing only one specific component type
        
        :param components: pandas DataFrame containing the \
            components.csv content
        :type components: pandas.DataFrame
        :param component_type: str defining which component type will \
            be searched for
        :type component_type: str
        
        :return: - **None** (pandas.DataFrame) - return the filtered \
            pandas.DataFrame
    """
    # search for entries of the components.csv with a given type
    return components[(components.type == component_type)]


def update_component_investment_decisions(
        components: pandas.DataFrame, model_definition_path: str,
        model_definition_type_name: str, result_type_name: str,
        investment_boundary_factor: int, investment_boundaries=True
) -> (pandas.DataFrame, list):
    """
        Adapts investment decision depending on the results of a \
        pre-model and returns new dataset plus list of deactivated \
        components.
        
        :param components: DataFrame holding the pre-model result \
            data's components.csv content
        :type components: pandas.DataFrame
        :param model_definition_path: file path of the \
            pre-model-definition-file which shall be adapted
        :type model_definition_path: str
        :param model_definition_type_name: string which defines the \
            model definition's component type (used to import the \
            correct spreadsheet)
        :type model_definition_type_name: str
        :param result_type_name: string which defines the \
            result's component type (used to filter the \
            components.csv file)
        :type result_type_name: str
        :param investment_boundary_factor: the investment boundaries \
            will be tightened to the respective investment decision of\
            the pre-run multiplied by this factor.
        :type investment_boundary_factor: int
        :param investment_boundaries: decision whether tightening of \
            the investment boundaries should be carried out
        :type investment_boundaries: bool
        
        :return: - **components_xlsx** (pandas.DataFrame) - updated \
            DataFrame after the deactivation and investment tightening \
            process
                 - **list_of_deactivated_components** (list) - list \
            holding the deactivated components
    """
    # return components type results
    result_components = filter_result_component_types(
        components=components,
        component_type=result_type_name)

    # read the component type model definition sheet
    components_xlsx = pandas.read_excel(
        io=model_definition_path,
        sheet_name=model_definition_type_name)
    # drop first (nan) column
    components_xlsx = components_xlsx.iloc[1:, :]
    # reset of index required, so that it is uniform to the result-dataframe
    components_xlsx = components_xlsx.reset_index()
    
    component_type_switch_dict = {
        "district heating": dh_technical_pre_selection,
        "buses": bus_technical_pre_selection,
        "insulation": insulation_technical_pre_selection
    }
    
    try:
        # run the component specific method if applicable in the
        # component_type_switch_dict
        component_type_switch_dict.get(model_definition_type_name)(
            components_xlsx=components_xlsx,
            result_components=result_components)

        # return the updated components_xlsx file as well as an empty
        # list since no components were deactivated
        return components_xlsx, []
    
    except TypeError:
        # run the general technical pre selection if the component_type
        # is not applicable within the component_type_switch_dict
        list_of_deactivated_components = technical_pre_selection(
            components_xlsx=components_xlsx,
            result_components=result_components)
        if investment_boundaries:
            tightening_investment_boundaries(
                components_xlsx=components_xlsx,
                result_components=result_components,
                investment_boundary_factor=investment_boundary_factor)
    
        return components_xlsx, list_of_deactivated_components


def technical_pre_selection(components_xlsx: pandas.DataFrame,
                            result_components: pandas.DataFrame) -> list:
    """
        deactivates investment-components for which no investments has \
        been carried out and additionally returns a list of deactivated\
        components
        
        :param components_xlsx: DataFrame holding the currently \
            considered sheet of the model definition file
        :type components_xlsx: pandas.DataFrame
        :param result_components: DataFrame holding the currently \
            considered components of the result data components.csv file
        :type result_components: pandas.DataFrame
        
        :return: - **list_of_deactivated_components** (list) -  list \
            containing the components which were deactivated within \
            this method
    """
    # create an empty list to collect the deactivated components
    list_of_deactivated_components = []
    # reset the index of the component.csv to the ID column
    result_components.set_index('ID', inplace=True)
    
    # iterate threw all components stored with in the model definition
    for num, component in components_xlsx.iterrows():
        # extract the current component label
        label = str(component["label"])
        # check rather the current considered component is in the
        # results components.csv file
        if label in result_components.index.values:
            # check rather an investment was made "investment/kW" and
            # if an investment was possible max. invest if not
            # deactivate the current considered component and append
            # it's label on the list of deactivated components
            if str(result_components.loc[label]['investment/kW']) == '0.0' and\
                    float(result_components.loc[label]['max. invest./kW']) > 0:
                components_xlsx.at[num, 'active'] = 0
                list_of_deactivated_components.append(label)
    # return the list of deactivated components
    return list_of_deactivated_components


def tightening_investment_boundaries(components_xlsx: pandas.DataFrame,
                                     result_components: pandas.DataFrame,
                                     investment_boundary_factor: int):
    """
        tightens investment boundaries
        
        :param components_xlsx: DataFrame holding the currently \
            considered sheet of the model definition file
        :type components_xlsx: pandas.DataFrame
        :param result_components: DataFrame holding the currently \
            considered components of the result data components.csv file
        :type result_components: pandas.DataFrame
        :param investment_boundary_factor: the investment boundaries \
            will be tightened to the respective investment decision of\
            the pre-run multiplied by this factor.
        :type investment_boundary_factor: int
    """
    # iterate threw all components stored with in the model definition
    for num, component in components_xlsx.iterrows():
        # extract the current component label
        label = str(component["label"])
        # check whether an investment on the currently considered
        # component was possible and if the component is part of the
        # result data's components.csv
        if label in result_components.index.values and \
                float(result_components.loc[label]['max. invest./kW']) > 0:
            # calculate the investment boundary which is defined as
            # solvers investment decision multiplied by the investment
            # boundary factor
            invest_boundary = (
                float(result_components.loc[label]['investment/kW'])
                * investment_boundary_factor)
            # if the invest boundary is lower than the max invest value
            # of the pre model it has to be adapted
            if invest_boundary \
                    <= float(result_components.loc[label]['max. invest./kW']):
                # adapt the max investment capacity of the currently
                # considered component
                components_xlsx.at[num, 'max. investment capacity'] = \
                    invest_boundary


def update_component_scenario_sheet(updated_data: pandas.DataFrame,
                                    model_definition_sheet_name: str,
                                    updated_scenario_path: str):
    """
        updates the original data within the updated model definition
        sheet
        
        :param updated_data: DataFrame holding the updated DataFrame \
            resulting from the pre-model algorithm
        :type updated_data: pandas.DataFrame
        :param model_definition_sheet_name: String holding the sheet \
            name to be stored using the pandas ExcelWriter
        :type model_definition_sheet_name: str
        :param updated_scenario_path: path where the update Excel file \
            will be stored
        :type updated_scenario_path: str
    """
    sheets = ['buses', 'district heating', 'sources',
              'transformers', 'storages', 'links']

    if model_definition_sheet_name in sheets:
        # adding an empty row at the top of the dataframe (replacing the
        # unit row in the original scenario file)
        updated_data = pandas.DataFrame(
            [[0 for x in range(len(updated_data.columns))]],
            columns=updated_data.columns).append(updated_data)

    writer = pandas.ExcelWriter(updated_scenario_path,
                                engine="openpyxl",
                                mode="a",
                                if_sheet_exists="replace")
    with writer:
        updated_data.to_excel(writer, model_definition_sheet_name, index=False)


def deactivate_respective_competition_constraints(
        scenario_path, list_of_deactivated_components):
    """
        identifies which competition constraints contains deactivated \
        components. The respective competition constraints are \
        deactivated in an updated dataframe
    """
    competition_constraints_xlsx = pd.read_excel(
            scenario_path, sheet_name='competition constraints')

    for i, constraint in competition_constraints_xlsx.iterrows():
        if constraint['component 1'] in list_of_deactivated_components:
            competition_constraints_xlsx.at[i, 'active'] = 0
        if constraint['component 2'] in list_of_deactivated_components:
            competition_constraints_xlsx.at[i, 'active'] = 0

    return competition_constraints_xlsx


def dh_technical_pre_selection(components_xlsx: pandas.DataFrame,
                               result_components: pandas.DataFrame):
    """
        deactivates district heating investment decisions for which no
        investments has been carried out
        
        :param components_xlsx: DataFrame holding the currently \
            considered sheet of the model definition file
        :type components_xlsx: pandas.DataFrame
        :param result_components: DataFrame holding the currently \
            considered components of the result data components.csv file
        :type result_components: pandas.DataFrame
    """
    # create list of street-sections for which an investment has been
    # carried out
    dh_investment_list = []
    # reduce the result_components Data Frame on entries with an investment
    result_components = result_components[result_components["investment/kW"]]
    # iterate threw the reduced result_components data frame
    for num, dh_section in result_components.iterrows():
        # if the ID does not contain 'dh_heat_house_station' it must be
        # a pipe of the considered thermal network
        if 'dh_heat_house_station' not in dh_section['ID']:
            no_invest_list = ['0.0', '0', '0.00', '---', '-0', '-0.0', '-0.00']
            # if the investment is in the no invest list the heat
            # network section will be appended on the section list
            if str(dh_section['investment/kW']) not in no_invest_list:
                section_name = dh_section['ID'].split('_Diameter')
                dh_investment_list.append(section_name[0])
                
    # since the Diameter str was part of the heat network consideration
    # the user needs to be informed that if one of his components
    # contains this str the algorithm does not work
    logging.info("\t WARNING: IF THE ORIGINAL SECTION NAME CONTAINED THE "
                 "STRING '_Diameter_' THIS ANALYSIS IS NOT VALID!")

    # deactivate those street section for which no investment has been
    # carried out
    for num, dh_section in components_xlsx.iterrows():
        # check whether the heat network section is within the
        # dh_investment_list  if not deactivate the section
        if str(dh_section['label']) not in dh_investment_list:
            components_xlsx.at[num, 'active'] = 0


def bus_technical_pre_selection(components_xlsx, result_components):
    """
    
    """
    bus_xlsx = components_xlsx
    no_invest_list = ['0.0', '0', '0.00', '---', '-0', '-0.0', '-0.00']
    # creates list of heating buses for which an investment has been
    # carried out
    dh_investment_list = []
    for i, dh_section in result_components.iterrows():
        if str(dh_section['investment/kW']) not in no_invest_list:
            if 'dh_heat_house_station' in dh_section['ID']:
                section_name = dh_section['ID'].split('dh_heat_house_station_')
                dh_investment_list.append(section_name[1])

        elif str(dh_section['capacity/kW']) not in no_invest_list:
            if 'dh_source_link' in dh_section['ID']:
                section_name = dh_section['ID'].split('_dh_source_link_')[0]
                dh_investment_list.append(section_name)
                
    print("WARNING: IF THE ORIGINAL BUS NAME CONTAINED THE STRING "
          "'dh_heat_house_station' THIS ANALYSIS IS NOT VALID!")
    print("WARNING: IF THE ORIGINAL BUS NAME CONTAINED THE STRING "
          "'dh_source_link' THIS ANALYSIS IS NOT VALID!")
    print("WARNING: IF THE ORIGINAL BUS NAME ARE DUPLICATES BEFORE USING"
          " '_' ANALYSIS IS NOT VALID!")
    print("WARNING: IF THE ORIGINAL BUS NAME CONTAINED THE STRING "
          "'_Diameter_' THIS ANALYSIS IS NOT VALID!")

    # deactivate those bus connections for which no investment has been
    # carried out
    print('dh_investment_list')
    print(dh_investment_list)
    for num, dh_bus in bus_xlsx.iterrows():
        label = str(dh_bus['label'])
        if str(dh_bus['district heating conn.']) not in no_invest_list:
            if label not in dh_investment_list \
                    and label[0:9] not in dh_investment_list \
                    and label.split('_')[0] not in dh_investment_list:
                if dh_bus['district heating conn.'] == "dh-system":
                    bus_xlsx.at[num, 'active'] = 0
                bus_xlsx.at[num, 'district heating conn.'] = 0
                
            elif len(dh_investment_list) < 2:
                bus_xlsx.at[num, 'district heating conn.'] = 0


def insulation_technical_pre_selection(components_xlsx, result_components):
    """
        deactivates district heating investment decisions for which no
        investments has been carried out
    """
    # create list of insulation measures for which an investment has
    # been carried out
    insulation_investment_list = []
    for i, insulation in result_components.iterrows():
        if insulation['investment/kW']:
            if str(insulation['investment/kW']) != '0.0':
                insulation_investment_list.append(insulation['ID'])

    # deactivate those street section for which no investment has been
    # carried out
    for i, insulation in components_xlsx.iterrows():
        if str(insulation['label'] + "-insulation") \
                not in insulation_investment_list:
            components_xlsx.at[i, 'active'] = 0


def update_model_according_pre_model_results(
        model_definition_path: str, results_components_path: str,
        updated_scenario_path: str, investment_boundary_factor: int,
        investment_boundaries: bool):
    """
        Carries out technical pre-selection and tightens investment \
        boundaries for a scenario, based on a previously performed \
        pre-model.

        :param model_definition_path: file path of the \
            pre-model-definition-file which shall be adapted
        :type model_definition_path: str
        :param results_components_path: folder path of the \
            pre-model-results on which base the scenario shall be \
            adapted
        :type results_components_path: str
        :param updated_scenario_path: file path, where the adapted \
            scenario shall be saved
        :type updated_scenario_path: str
        :param investment_boundary_factor: the investment boundaries \
            will be tightened to the respective investment decision of\
            the pre-run multiplied by this factor.
        :type investment_boundary_factor: int
        :param investment_boundaries: decision whether tightening of \
            the investment boundaries should be carried out
        :type investment_boundaries: bool
    """

    # import de model definition file
    model_definition_xlsx = pandas.read_excel(
        io=model_definition_path, sheet_name=None)

    # import the components.csv of the pre-model's result data
    components = pandas.read_csv(filepath_or_buffer=results_components_path)

    # Copy original scenario sheet to new file
    with pandas.ExcelWriter(updated_scenario_path) as writer:
        for sheet in model_definition_xlsx:
            model_definition_xlsx[sheet].to_excel(writer, sheet_name=sheet)

    # Create List required for adaption of competition constraints
    complete_list_of_deactivated_components = []

    # list of lists of component types. the first value of the sub-lists
    # represent the name of the component type in the scenario sheet,
    # the second values the component name in the result sheets
    component_types = [['buses', 'transformer'],
                       ['transformers', 'transformer'],
                       ['sources', 'source'],
                       ['storages', 'storage'],
                       ['links', 'link'],
                       ['insulation', 'insulation']]
    # iterate threw the list of list
    for sub_list in component_types:
        # represents the model component type
        model_definition_type_name = sub_list[0]
        # represents the components.csv component type
        result_type_name = sub_list[1]

        # technical pre-selection and tightening of investment boundaries
        updated_components, list_of_deactivated_components = \
            update_component_investment_decisions(
                components=components,
                model_definition_path=model_definition_path,
                model_definition_type_name=model_definition_type_name,
                result_type_name=result_type_name,
                investment_boundary_factor=investment_boundary_factor,
                investment_boundaries=investment_boundaries)
        
        # add the newly deactivated components to the list of \
        # deactivated components
        complete_list_of_deactivated_components \
            += list_of_deactivated_components
        
        # save updated data
        update_component_scenario_sheet(
            updated_data=updated_components,
            model_definition_sheet_name=model_definition_type_name,
            updated_scenario_path=updated_scenario_path)
        
    # deactivate the competition constraint of components that are not
    # longer part of the energy system
    updated_constraints = deactivate_respective_competition_constraints(
        scenario_path=model_definition_path,
        list_of_deactivated_components=complete_list_of_deactivated_components)
    
    # save the changes done in the competition constraints sheet
    update_component_scenario_sheet(
        updated_scenario_path=updated_scenario_path,
        updated_data=updated_constraints,
        model_definition_sheet_name='competition constraints')
    
    logging.info('\t Scenario updated according to the results of the '
                 'pre-model.')
