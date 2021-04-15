# todo adapt labels from pre_scenario to post_processing (central components)
# todo components.csv is hidden in the current results folder

# imports
import pandas as pd
import os


def create_decentral_overview(pre_scenario, data):
    # defining columns of the sheet including decentralized components
    decentral_columns = ["Building",
                         "PV-System 1 in kW", "Max. PV 1 in kW",
                         "PV-System 2 in kW", "Max. PV 2 in kW",
                         "PV-System 3 in kW", "Max. PV 3 in kW",
                         "PV-System 4 in kW", "Max. PV 4 in kW",
                         "PV-System 5 in kW", "Max. PV 5 in kW",
                         "Installed PV in kW",
                         "Max. PV in kW",
                         "Gasheating-System in kW",
                         "ASHP in kW", "GCHP in kW", "Battery-Storage in kWh",
                         "Heat Transformer in kW"]
    decentral_components = pd.DataFrame(columns=decentral_columns)

    # creating a list to reduce the number of rows
    decentral_components_list = ['_1_pv', '_2_pv', '_3_pv', '_4_pv', '_5_pv', '_gasheating_transformer',
                                 '_ashp_transformer', '_gchp_transformer', '_battery_storage', '_district_heat_link']

    # import investment values from components.csv
    for i, j in pre_scenario.iterrows():
        installed_power = []

        for comp in decentral_components_list:
            # investment values of pv
            variable_central = (data.loc[data['ID'].str.contains(j['label'] + comp)]['investment/kW']).values
            variable_central = float(variable_central[0]) if variable_central.size > 0 else 0
            installed_power.append(variable_central)
        maximums = []
        installed_pv = 0.0

        for roofnum in range(5):
            # max values for each pv system
            maximums.append(round(j['roof area ' + str(roofnum + 1) + ' (m²)'] * 0.19, 2))
            installed_pv_roof = (data.loc[data['ID'].str.contains(j['label']
                                 + decentral_components_list[roofnum])]['investment/kW']).values
            installed_pv_roof = float(installed_pv_roof[0]) if installed_pv_roof.size > 0 else 0
            installed_pv = installed_pv + installed_pv_roof

        max_total_pv = sum(maximums)

        # dict to append the values
        # comps indices 0:pv1, 1:pv2, ... todo
        decentral_components_dict = {"Building": j['label'],
                                     "PV-System 1 in kW": installed_power[0], "Max. PV 1 in kW": maximums[0],
                                     "PV-System 2 in kW": installed_power[1], "Max. PV 2 in kW": maximums[1],
                                     "PV-System 3 in kW": installed_power[2], "Max. PV 3 in kW": maximums[2],
                                     "PV-System 4 in kW": installed_power[3], "Max. PV 4 in kW": maximums[3],
                                     "PV-System 5 in kW": installed_power[4], "Max. PV 5 in kW": maximums[4],
                                     "Installed PV in kW": installed_pv, "Max. PV in kW": max_total_pv,
                                     "Gasheating-System in kW": installed_power[5], "ASHP in kW": installed_power[6],
                                     "GCHP in kW": installed_power[7], "Battery-Storage in kWh": installed_power[8],
                                     "Heat Transformer in kW": installed_power[9]}

        decentral_components = decentral_components.append(pd.Series(decentral_components_dict), ignore_index=True)

    return decentral_components


def create_central_overview(pre_scenario_central, data):
    # defining columns of the sheet including centralized components
    central_columns = ["label", "investment"]
    central_values = pd.DataFrame(columns=central_columns)
    # todo verknüpfung zu pre_scenario nicht möglich da überschriften nicht die id sind???
    # central_components = ["naturalgas_chp_transformer", "biogas_chp_transformer", "central_swhp_transformer"]
    central_components = pre_scenario_central.keys()
    # print(pre_scenario_central.keys())
    for comp in central_components:
        # investment values of central components
        variable_central = (data.loc[data['ID'].str.contains(comp)]['investment/kW']).values
        variable_central = float(variable_central[0]) if variable_central.size > 0 else 0
        central_components_dict = {"label": comp, "investment": variable_central}
        central_values = central_values.append(pd.Series(central_components_dict), ignore_index=True)

    return central_values


def urban_district_upscaling_post_processing(components: str, pre_scenario_path: str):
    """
        todo docstring 
    """
    data = pd.read_csv(components)
    data = data.replace(to_replace='---', value=0)
    # pre_scenario in order to import the labels
    pre_scenario = pd.read_excel(pre_scenario_path)
    pre_scenario_central = pd.read_excel(pre_scenario_path, 1)
    decentral_components = create_decentral_overview(pre_scenario, data)
    central_values = create_central_overview(pre_scenario_central, data)
    # output
    writer = pd.ExcelWriter(os.path.dirname(__file__) + "/overview.xlsx",
                            engine='xlsxwriter')
    decentral_components.to_excel(writer, "decentral_components", index=False)
    central_values.to_excel(writer, "central_components", index=False)
    print("Overview created.")
    writer.save()


if __name__ == "__main__":
    # csv which contains the exportable data
    data = pd.read_csv("components.csv")

    # replace defect values with 0
    data = data.replace(to_replace='---', value=0)

    # pre_scenario in order to import the labels
    pre_scenario = pd.read_excel('pre_scenario.xlsx')
    pre_scenario_central = pd.read_excel('pre_scenario.xlsx', 1)
    decentral_components = create_decentral_overview(pre_scenario)
    central_values = create_central_overview(pre_scenario_central)
    # output
    writer = pd.ExcelWriter(os.path.dirname(__file__) + "/overview.xlsx", engine='xlsxwriter')
    # dict_clearing = pd.DataFrame()
    # dict_clearing.to_excel(writer, "decentral_components", index=False)
    # dict_clearing.to_excel(writer, "central_components", index=False)
    decentral_components.to_excel(writer, "decentral_components", index=False)
    central_values.to_excel(writer, "central_components", index=False)
    writer.save()
