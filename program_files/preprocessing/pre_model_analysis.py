import pandas as pd
import shutil

def filter_result_component_types(components, type):
    ' returns dataframe containing only one specific component type'

    filtered_components = components[(components.type == type)]
    return(filtered_components)

def update_component_investment_decisions(pre_model_results, scenario_path, results_components_path, updated_scenario_path, scenario_type_name, result_type_name, boundary_factor, investment_boundaries=True):
    '''adapts investment decision depending on the results of a pre-model and returns new dataset plus list of
    deactivated components'''
    components = pre_model_results
    # return components type results
    result_components = filter_result_component_types(components=components, type=result_type_name)

    # return component type scenario sheet
    components_xlsx = pd.read_excel(scenario_path, sheet_name=scenario_type_name)
    # drop first (nan) column
    components_xlsx = components_xlsx.iloc[1: , :]
    # reset of index required, so that it is uniform to the result-dataframe
    components_xlsx = components_xlsx.reset_index()

    if scenario_type_name == 'district heating':
        dh_technical_pre_selection(components_xlsx, result_components)
        list_of_deactivated_components = []

        return components_xlsx, list_of_deactivated_components

    elif scenario_type_name == 'buses':
        bus_technical_pre_selection(components_xlsx, result_components)
        list_of_deactivated_components = []

        return components_xlsx, list_of_deactivated_components

    elif result_type_name == 'insulation':
        insulation_technical_pre_selection(components_xlsx, result_components)
        list_of_deactivated_components = []

        return components_xlsx, list_of_deactivated_components

    else:
        list_of_deactivated_components = technical_pre_selection(components_xlsx, result_components)
        if investment_boundaries == True:
            tightening_investment_boundaries(components_xlsx, result_components, boundary_factor)

        return components_xlsx, list_of_deactivated_components

def technical_pre_selection(components_xlsx, result_components):
    '''deactivates investment-components for which no investments has been carried out and additionally returns a list
    of deactivated components'''
    list_of_deactivated_components = []
    result_components.set_index('ID', inplace=True)
    for i,scenario_component in components_xlsx.iterrows():
        if scenario_component['label'] in result_components.index.values:
            if float(result_components.loc[scenario_component['label']]['max. invest./kW']) > 0:
                if str(result_components.loc[scenario_component['label']]['investment/kW']) == '0.0':
                    components_xlsx.at[i, 'active'] = 0
                    list_of_deactivated_components.append(str(scenario_component['label']))



        # if float(result_components.iloc[i]['max. invest./kW']) > 0:
        #     if str(result_components.iloc[i]['investment/kW']) == '0.0':
        #         components_xlsx.at[i, 'active'] = 0
        #         list_of_deactivated_components.append(str(scenario_component['label']))

    return list_of_deactivated_components

    deactive_respective_competition_constraints(scenario_path, list_of_deactivated_components)

def tightening_investment_boundaries(components_xlsx, result_components, boundary_factor):
    'tightens investment boundaries'
    list_of_adapted_components = []
    for i,scenario_component in components_xlsx.iterrows():
        if scenario_component['label'] in result_components.index.values:
            if float(result_components.loc[scenario_component['label']]['max. invest./kW']) > 0:
                if (float(result_components.loc[scenario_component['label']]['investment/kW']) * boundary_factor) <= float(result_components.loc[scenario_component['label']][
                    'max. invest./kW']):
                    components_xlsx.at[i, 'max. investment capacity'] = float(result_components.loc[scenario_component['label']]['investment/kW']) * boundary_factor
                    list_of_adapted_components.append(str(scenario_component['label']))
        # if float(result_components.iloc[i]['max. invest./kW']) > 0:
        #     if result_components.iloc[i]['investment/kW']*boundary_factor < result_components.iloc[i]['max. invest./kW']:
        #         components_xlsx.at[i, 'max. investment capacity'] = float(result_components.iloc[i]['investment/kW'])*boundary_factor
        #         list_of_adapted_components.append(str(scenario_component['label']))

def update_component_scenario_sheet(updated_data, scenario_sheet_name, updated_scenario_path):
    'updates the original data within the updated scenario sheet'

    if scenario_sheet_name in ['buses', 'district heating', 'sources', 'transformers', 'storages', 'links']:
        # adding an empty row at the top of the dataframe (replacing the unit row in the original scenario file)
        updated_data = pd.DataFrame([[0 for x in range(len(updated_data.columns))]], columns=updated_data.columns).append(updated_data)

    with pd.ExcelWriter(updated_scenario_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        updated_data.to_excel(writer, scenario_sheet_name, index=False)

def deactive_respective_competition_constraints(scenario_path, list_of_deactivated_components):
    ''' identifies which competition constraints contains deactivated components. The respective competition constraints
    are deactivated in an updated dataframe'''
    competition_constraints_xlsx = pd.read_excel(scenario_path, sheet_name='competition constraints')

    for i, constraint in competition_constraints_xlsx.iterrows():
        if constraint['component 1'] in list_of_deactivated_components:
            competition_constraints_xlsx.at[i, 'active'] = 0
        if constraint['component 2'] in list_of_deactivated_components:
            competition_constraints_xlsx.at[i, 'active'] = 0

    return competition_constraints_xlsx

def dh_technical_pre_selection(components_xlsx, result_components):
    '''deactivates district heating investment decisions for which no investments has been carried out '''

    # create list of street-sections for which an investment has been carried out
    dh_investment_list = []
    for i, dh_section in result_components.iterrows():
        if dh_section['investment/kW']:
            #dh_investment_string = dh_investment_string + str(dh_section['ID'])
            if 'dh_heat_house_station' not in dh_section['ID']:
                #print(dh_section['ID'])
                #print(dh_section['investment/kW'])
                if str(dh_section['investment/kW']) not in ['0.0','0','0.00','---']:
                    section_name = dh_section['ID'].split('_Diameter')
                    dh_investment_list.append(section_name[0])
    print("WARNING: IF THE ORIGINAL SECTION NAME CONTAINED THE STRING '_Diameter_' THIS ANALYSIS IS NOT VALID!")

    # deactivate those street section for which no investment has been carried out
    for i, dh_section in components_xlsx.iterrows():
        if str(dh_section['label']) not in dh_investment_list:
            components_xlsx.at[i, 'active'] = 0
            #print(str(dh_section['label'].split('_')[0]))
            #print(str(dh_section['label'])+' deactivated')
            print('test1')
            print(dh_investment_list)

def bus_technical_pre_selection(components_xlsx, result_components):
    bus_xlsx = components_xlsx

    # creates list of heating buses for which an investment has been carried out
    dh_investment_list = []
    print('test2')
    print(result_components)
    for i, dh_section in result_components.iterrows():
        print('HIER')
        print(dh_section['ID'])
        if str(dh_section['investment/kW']) not in ['0.0','0','0.00','---']:
            if 'dh_heat_house_station' in dh_section['ID']:
                print('ping1')
                #if str(dh_section['investment/kW']) != '0.0':
                    # print(dh_section['ID'])
                    # print(dh_section['investment/kW'])
                section_name = dh_section['ID'].split('dh_heat_house_station_')
                dh_investment_list.append(section_name[1])

        elif str(dh_section['capacity/kW']) not in ['0.0','0','0.00','---']:
            if 'dh_source_link' in dh_section['ID']:
                # if str(dh_section['investment/kW']) not in ['0.0','0','0.00','---']:
                section_name = dh_section['ID'].split('_dh_source_link_')[0]
                print(section_name)
                #section_name = section_name[1].split('_Diameter_')
                dh_investment_list.append(section_name)
    print("WARNING: IF THE ORIGINAL BUS NAME CONTAINED THE STRING 'dh_heat_house_station' THIS ANALYSIS IS NOT VALID!")
    print("WARNING: IF THE ORIGINAL BUS NAME CONTAINED THE STRING 'dh_source_link' THIS ANALYSIS IS NOT VALID!")
    print("WARNING: IF THE ORIGINAL BUS NAME ARE DUPLICATES BEFORE USING '_' ANALYSIS IS NOT VALID!")
    print("WARNING: IF THE ORIGINAL BUS NAME CONTAINED THE STRING '_Diameter_' THIS ANALYSIS IS NOT VALID!")
    print(dh_investment_list)
    print('test3')
    print(len(dh_investment_list))

    # deactivate those bus connections for which no investment has been carried out
    for i, dh_bus in bus_xlsx.iterrows():

        # print('TEST HIER')
        # print(str(dh_bus['label']))
        # print(str(dh_bus['label'])[0:9])
        # print(str(dh_bus['label'].split('_')[0]))
        if str(dh_bus['district heating conn.']) not in ['0.0','0','0.00','---']:
            print(dh_bus['label'])
            if str(dh_bus['label']) not in dh_investment_list and str(dh_bus['label'])[0:9] not in dh_investment_list and dh_bus['label'].split('_')[0] not in dh_investment_list:# and dh_bus['district heating conn.']:
                bus_xlsx.at[i, 'district heating conn.'] = '0'
                print(str(dh_bus['label'])+' deactivated')
            # if str(dh_bus['label'])[0:9] not in dh_investment_list and dh_bus['district heating conn.']:
            #     print(str(dh_bus['label'])[0:9])
            #     bus_xlsx.at[i, 'district heating conn.'] = 0
            elif len(dh_investment_list) < 2:
                bus_xlsx.at[i, 'district heating conn.'] = 0

def insulation_technical_pre_selection(components_xlsx, result_components):
    '''deactivates district heating investment decisions for which no investments has been carried out '''

    # create list of insulation measures for which an investment has been carried out
    insulation_investment_list = []
    for i, insulation in result_components.iterrows():
        if insulation['investment/kW']:
            if str(insulation['investment/kW']) != '0.0':
                insulation_investment_list.append(insulation['ID'])

    # deactivate those street section for which no investment has been carried out
    for i, insulation in components_xlsx.iterrows():
        if str('insulation-'+insulation['label']) not in insulation_investment_list:
            components_xlsx.at[i, 'active'] = 0
            #print(str(insulation['label'])+' deactivated')

def update_model_according_pre_model_results(scenario_path, results_components_path, updated_scenario_path,
                                             investment_boundary_factor, investment_boundaries):
    '''
        Carries out technical pre-selection and tightens investment boundaries for a scenario, based on a previously
        performed pre-model.

        :param scenario_path: file path of the pre-model-scenario-file which shall be adapted
        :type scenario_path: str
        :param results_components_path: folder path of the pre-model-results on which base the scenario shall be adapted
        :type results_components_path: str
        :param updated_scenario_path: file path, where the adapted scenario shall be saved
        :type updated_scenario_path: str
        :param investment_boundary_factor: the investment boundaries will be tightenend to the respective investemnt de-
                                            cision of the pre-run multiplicated by this factor.
        :type investment_boundary_factor: int
        :param investment_boundaries: decision whether tightening of the investment boundaries should be carried out
        :type investment_boundaries: bool
    '''

    # IMPORT ORIGINAL SCENARIO
    scenario_xlsx = pd.read_excel(scenario_path, sheet_name=None)

    # IMPORT RESULT DATA
    components = pd.read_csv(results_components_path)

    # Copy original scenario sheet to new file
    shutil.copy(scenario_path, updated_scenario_path)

    # Create List required for adaption of competition constraints
    complete_list_of_deactivated_components =[]

     # list of lists of component types. the first value of the sub-lists represent the name of the component type in the
     # scenario sheet, the second values the component name in the result sheets
    component_types = [['district heating', 'dh'],
                       ['buses', 'transformer'],
                       ['transformers', 'transformer'],
                       ['sources', 'source'],
                       ['storages', 'storage'],
                       ['links', 'link'],
                       ['insulation', 'insulation']]

    for i in component_types:
        scenario_type_name = i[0]
        result_type_name = i[1]

        # technical pre-selection and tightening of investment boundaries
        updated_components, list_of_deactivated_components = update_component_investment_decisions(
            pre_model_results=components,
            scenario_path=scenario_path,
            results_components_path=results_components_path,
            updated_scenario_path=updated_scenario_path,
            scenario_type_name=scenario_type_name,
            result_type_name=result_type_name,
            boundary_factor=investment_boundary_factor,
            investment_boundaries = investment_boundaries)
        complete_list_of_deactivated_components = complete_list_of_deactivated_components + list_of_deactivated_components
        # save updated data
        update_component_scenario_sheet(updated_data=updated_components,
                                        scenario_sheet_name=scenario_type_name,
                                        updated_scenario_path=updated_scenario_path)

    updated_constraints = deactive_respective_competition_constraints(scenario_path,
                                                                      complete_list_of_deactivated_components)
    update_component_scenario_sheet(updated_scenario_path=updated_scenario_path,
                                    updated_data = updated_constraints,
                                    scenario_sheet_name = 'competition constraints')
    print('Scenario updated according to the results of the pre-model.')


# update_model_according_pre_model_results(scenario_path= '20220928_model_V2_reduced.xlsx',
#                                          results_components_path = '20220928_model_V2_reduced_2022-09-29--15-25-03/components.csv',
#                                          updated_scenario_path = 'updated_20220928_model_V2_reduced.xlsx',
#                                          investment_boundary_factor = 1000,
#                                          investment_boundaries = False)
