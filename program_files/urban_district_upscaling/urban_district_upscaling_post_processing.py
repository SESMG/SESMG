# todo components.csv is hidden in the current results folder
# TODO problem by central links that are connecting two central comps (labels are inconsistent (ng unequal naturalgas))
# TODO--> urban_district_upscaling --> collector_collector bug
# TODO include a unit row in decentral components sheet
# TODO decide whether include MAX PV and MAX ST or the percentage of area usage

# imports
import pandas as pd
import os


def create_decentral_overview(csv_data):
    # defining columns of the sheet including decentralized components
    decentral_columns = ["Building", "PV 1", "Max. PV 1", "PV 2", "Max. PV 2", "PV 3", "Max. PV 3", "PV 4", "Max. PV 4",
                         "PV 5", "Max. PV 5", "Installed PV", "Max. PV", "STC 1", "Max. STC 1", "STC 2", "Max. STC 2",
                         "STC 3", "Max. STC 3", "STC 4", "Max. STC 4", "STC 5", "Max. STC 5", "Installed STC",
                         "Max. STC", "Gasheating-System", "ASHP", "GCHP", "Battery-Storage", "Heat Transformer",
                         "Electric Heating"]
    decentral_components = pd.DataFrame(columns=decentral_columns)

    # creating a list to reduce the number of rows
    decentral_components_list = ['_1_pv', '_2_pv', '_3_pv', '_4_pv', '_5_pv', '_gasheating_transformer',
                                 '_ashp_transformer', '_gchp_transformer', '_battery_storage', '_district_heat_link',
                                 '_electricheating_transformer', '_1_solarthermal_source_collector',
                                 '_2_solarthermal_source_collector', '_3_solarthermal_source_collector',
                                 '_4_solarthermal_source_collector', '_5_solarthermal_source_collector']
    decentral_components_from_csv = []
    for comp in csv_data['ID']:
        i = comp.split('_')
        if 'pv' not in i[0]:
            if 'central' not in i[0]:
                decentral_components_from_csv.append(i[0])
    decentral_components_from_csv = set(decentral_components_from_csv)
    # import investment values from components.csv
    for i in decentral_components_from_csv:
        installed_power = []

        for comp in decentral_components_list:
            # investment values of pv
            variable_central = (csv_data.loc[csv_data['ID'].str.contains(str(i) + comp)]['investment/kW']).values
            variable_central = float(variable_central[0]) if variable_central.size > 0 else 0
            installed_power.append(variable_central)
        maximums_pv = []
        maximums_st = []
        installed_pv = 0.0
        installed_st = 0.0

        for roofnum in range(5):
            # max values for each pv system
            # todo Solarthermal collector
            maximum_pv = (csv_data.loc[csv_data['ID'].str.contains(str(i) + '_' + str(roofnum+1) + '_pv_source')]['max. invest./kW']).values
            maximum_st = (csv_data.loc[csv_data['ID'].str.contains(str(i) + '_' + str(roofnum+1) + '_solarthermal_source_collector')]['max. invest./kW']).values
            if maximum_pv.size > 0:
                maximums_pv.append(float(maximum_pv[0]))
            else:
                maximums_pv.append(0)
            if maximum_st.size > 0:
                maximums_st.append(float(maximum_st[0]))
            else:
                maximums_st.append(0)

            installed_pv_roof = (csv_data.loc[csv_data['ID'].str.contains(str(i)
                                 + decentral_components_list[roofnum])]['investment/kW']).values
            installed_pv_roof = float(installed_pv_roof[0]) if installed_pv_roof.size > 0 else 0
            installed_pv = installed_pv + installed_pv_roof
            installed_st_roof = (csv_data.loc[csv_data['ID'].str.contains(str(i)
                                                                  + decentral_components_list[-(5-roofnum)])][
                'investment/kW']).values
            installed_st_roof = float(installed_st_roof[0]) if installed_st_roof.size > 0 else 0
            installed_st = installed_st + installed_st_roof

        max_total_pv = sum(maximums_pv)
        max_total_st = sum(maximums_st)

        # dict to append the values
        # comps indices 0:pv1, 1:pv2, ... todo
        decentral_components_dict = {"Building": str(i),
                                     "PV 1": installed_power[0], "Max. PV 1": maximums_pv[0],
                                     "PV 2": installed_power[1], "Max. PV 2": maximums_pv[1],
                                     "PV 3": installed_power[2], "Max. PV 3": maximums_pv[2],
                                     "PV 4": installed_power[3], "Max. PV 4": maximums_pv[3],
                                     "PV 5": installed_power[4], "Max. PV 5": maximums_pv[4],
                                     "Installed PV": installed_pv, "Max. PV": max_total_pv,
                                     "STC 1": installed_power[11], "Max. STC 1": maximums_st[0],
                                     "STC 2": installed_power[12], "Max. STC 2": maximums_st[1],
                                     "STC 3": installed_power[13], "Max. STC 3": maximums_st[2],
                                     "STC 4": installed_power[14], "Max. STC 4": maximums_st[3],
                                     "STC 5": installed_power[15], "Max. STC 5": maximums_st[4],
                                     "Installed STC": installed_st, "Max. STC": max_total_st,
                                     "Gasheating-System": installed_power[5], "ASHP": installed_power[6],
                                     "GCHP": installed_power[7], "Battery-Storage": installed_power[8],
                                     "Heat Transformer": installed_power[9],
                                     "Electric Heating": installed_power[10]}

        decentral_components = decentral_components.append(pd.Series(decentral_components_dict), ignore_index=True)

    return decentral_components


def create_central_overview(csv_data):
    # defining columns of the sheet including centralized components
    central_columns = ["label", "investment"]
    central_values = pd.DataFrame(columns=central_columns)
    central_components = []
    for comp in csv_data['ID']:
        k = comp.split('_')
        if k[0] == 'central':
            if k[-1] in ['transformer', 'storage', 'link']:
                central_components.append(comp)
    # print(pre_scenario_central.keys())
    for comp in central_components:
        # investment values of central components
        variable_central = (csv_data.loc[csv_data['ID'].str.contains(comp)]['investment/kW']).values
        variable_central = float(variable_central[0]) if variable_central.size > 0 else 0
        central_components_dict = {"label": comp, "investment": variable_central}
        central_values = central_values.append(pd.Series(central_components_dict), ignore_index=True)

    return central_values


def urban_district_upscaling_post_processing(components: str, pre_scenario_path: str):
    """
        todo docstring
    """
    csv_data = pd.read_csv(components)
    csv_data = csv_data.replace(to_replace='---', value=0)
    # pre_scenario in order to import the labels
    decentral_components = create_decentral_overview(csv_data)
    central_values = create_central_overview(csv_data)
    # output
    writer = pd.ExcelWriter(os.path.dirname(__file__) + "/overview.xlsx",
                            engine='xlsxwriter')
    decentral_components.to_excel(writer, "decentral_components", index=False)
    central_values.to_excel(writer, "central_components", index=False)
    print("Overview created.")
    writer.save()


if __name__ == "__main__":
    # csv which contains the exportable data
    csv_data = pd.read_csv("components.csv")

    # replace defect values with 0
    csv_data = csv_data.replace(to_replace='---', value=0)

    # pre_scenario in order to import the labels
    decentral_components = create_decentral_overview(csv_data)
    central_values = create_central_overview(csv_data)
    # output
    writer = pd.ExcelWriter(os.path.dirname(__file__) + "/overview.xlsx", engine='xlsxwriter')
    decentral_components.to_excel(writer, "decentral_components", index=False)
    central_values.to_excel(writer, "central_components", index=False)
    writer.save()
