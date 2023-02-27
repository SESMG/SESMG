# TODO decide whether include MAX PV and MAX ST or the percentage of area usage ??
# todo 2021-11-02: Bei max PV/ST starten

import pandas as pd
import os


# TODO find another way to get the combination of cluster and building id
label_Cluster = {"building_ID": "test_cluster"}

# creating a list to reduce the number of rows
decentral_components_list = [
    "_north_pv",
    "_north_east_pv",
    "_east_pv",
    "_south_east_pv",
    "_south_pv",
    "_south_west_pv",
    "_west_pv",
    "_north_west_pv",
    "_north_solarthermal_source_collector",
    "_north_east_solarthermal_source_collector",
    "_east_solarthermal_source_collector",
    "_south_east_solarthermal_source_collector",
    "_south_solarthermal_source_collector",
    "_south_west_solarthermal_source_collector",
    "_west_solarthermal_source_collector",
    "_north_west_solarthermal_source_collector",
    "_gasheating_transformer",
    "_ashp_transformer",
    "_gchp_transformer",
    "_battery_storage",
    "_thermal_storage",
    "_electricheating_transformer",
    "_com_electricity_demand",
    "_res_electricity_demand",
    "_electricity_bus_shortage",
    "_pv_bus_excess",
    "_heat_bus",
    "pv_central",
    "",
]


def __remove_redundant_comps(components, decentral_components_from_csv, wo_pv=False):
    for comp in components["ID"]:
        i = comp.split("_")
        if "pv" not in i[0]:
            if "central" not in i[0]:
                if "RES" not in i[0] and "COM" not in i[0]:
                    if len(str(i[0])) <= 4:
                        decentral_components_from_csv.append(i[0])
    decentral_components_from_csv = set(decentral_components_from_csv)
    return decentral_components_from_csv


def __create_decentral_overview(components):
    # defining columns of the sheet including decentralized components
    decentral_columns = [
        "Cluster",
        "PV north",
        "Max. PV north",
        "PV north east",
        "Max. PV north east",
        "PV east",
        "Max. PV east",
        "PV south east",
        "Max. PV south east",
        "PV south",
        "Max. PV south",
        "PV south west",
        "Max. PV south west",
        "PV west",
        "Max. PV west",
        "PV north west",
        "Max. PV north west",
        "Installed PV",
        "Max. PV",
        "ST north",
        "Max. ST north",
        "ST north east",
        "Max. ST north east",
        "ST east",
        "Max. ST east",
        "ST south east",
        "Max. ST south east",
        "ST south",
        "Max. ST south",
        "ST south west",
        "Max. ST south west",
        "ST west",
        "Max. ST west",
        "ST north west",
        "Max. ST north west",
        "Installed ST",
        "Max. ST",
        "Gasheating-System",
        "ASHP",
        "GCHP",
        "Battery-Storage",
        "Thermal-Storage",
        "Electric Heating",
        "COM Electricity Demand",
        "RES Electricity Demand",
        "Electricity Import",
        "Electricity Export",
        "District Heating",
    ]
    # defining units for decentral components
    decentral_columns_units = {
        "Cluster": "",
        "PV north": "(kW)",
        "Max. PV north": "(kW)",
        "PV north east": "(kW)",
        "Max. PV north east": "(kW)",
        "PV east": "(kW)",
        "Max. PV east": "(kW)",
        "PV south east": "(kW)",
        "Max. PV south east": "(kW)",
        "PV south": "(kW)",
        "Max. PV south": "(kW)",
        "PV south west": "(kW)",
        "Max. PV south west": "(kW)",
        "PV west": "(kW)",
        "Max. PV west": "(kW)",
        "PV north west": "(kW)",
        "Max. PV north west": "(kW)",
        "Installed PV": "(kW)",
        "Max. PV": "(kW)",
        "ST north": "(kW)",
        "Max. ST north": "(kW)",
        "ST north east": "(kW)",
        "Max. ST north east": "(kW)",
        "ST east": "(kW)",
        "Max. ST east": "(kW)",
        "ST south east": "(kW)",
        "Max. ST south east": "(kW)",
        "ST south": "(kW)",
        "Max. ST south": "(kW)",
        "ST south west": "(kW)",
        "Max. ST south west": "(kW)",
        "ST west": "(kW)",
        "Max. ST west": "(kW)",
        "ST north west": "(kW)",
        "Max. ST north west": "(kW)",
        "Installed ST": "(kW)",
        "Max. ST": "(kW)",
        "Gasheating-System": "(kW)",
        "ASHP": "(kW)",
        "GCHP": "(kW)",
        "Battery-Storage": "(kWh)",
        "Thermal-Storage": "(kWh)",
        "Electric Heating": "(kW)",
        "COM Electricity Demand": "(kWh)",
        "RES Electricity Demand": "(kWh)",
        "Electricity Import": "(kWh)",
        "Electricity Export": "(kWh)",
        "District Heating": "(kW)",
    }

    decentral_components = pd.DataFrame(columns=decentral_columns)
    decentral_components = decentral_components.append(
        pd.Series(decentral_columns_units), ignore_index=True
    )

    decentral_components_from_csv = []

    decentral_components_from_csv = __remove_redundant_comps(
        components, decentral_components_from_csv
    )

    # import investment values from components.csv
    for i in decentral_components_from_csv:
        installed_power = []

        for comp in decentral_components_list:
            if comp not in [
                "_com_electricity_demand",
                "_res_electricity_demand",
                "_electricity_bus_shortage",
                "_pv_bus_excess",
                "_heat_bus",
            ]:
                # investment values of pv
                variable_central = (
                    components.loc[components["ID"].str.contains(str(i) + comp)][
                        "investment/kW"
                    ]
                ).values
                variable_central = (
                    float(variable_central[0]) if variable_central.size > 0 else 0
                )
            elif "_heat_bus" in comp:
                dh = 0
                for building in label_Cluster:
                    if label_Cluster[building] == i:
                        variable_building = (
                            components.loc[
                                components["ID"].str.contains(
                                    "-" + str(building) + comp
                                )
                            ]["investment/kW"]
                        ).values
                        variable_building = (
                            float(variable_building[0])
                            if variable_building.size > 0
                            else 0
                        )
                        dh += variable_building
            else:
                if comp != "_electricity_bus_shortage":
                    variable_central = (
                        components.loc[components["ID"].str.contains(str(i) + comp)][
                            "input 1/kWh"
                        ]
                    ).values
                    variable_central = (
                        float(variable_central[0]) if variable_central.size > 0 else 0
                    )
                else:
                    variable_central = (
                        components.loc[components["ID"].str.contains(str(i) + comp)][
                            "output 1/kWh"
                        ]
                    ).values
                    variable_central = (
                        float(variable_central[0]) if variable_central.size > 0 else 0
                    )
            installed_power.append(variable_central)
        maximums_pv = []
        maximums_st = []
        installed_pv = 0.0
        installed_st = 0.0
        celestial = [
            "north",
            "north_east",
            "east",
            "south_east",
            "south",
            "south_west",
            "west",
            "north_west",
        ]

        for test in celestial:
            # max values for each pv system,
            # need celestial to select the pv source
            maximum_pv = (
                components.loc[
                    components["ID"].str.contains(str(i) + "_" + test + "_pv_source")
                ]["max. invest./kW"]
            ).values
            maximum_st = (
                components.loc[
                    components["ID"].str.contains(
                        str(i) + "_" + test + "_solarthermal_source_collector"
                    )
                ]["max. invest./kW"]
            ).values

            if maximum_pv.size > 0:
                maximums_pv.append(float(maximum_pv[0]))
            else:
                maximums_pv.append(0)
            if maximum_st.size > 0:
                maximums_st.append(float(maximum_st[0]))
            else:
                maximums_st.append(0)

        # iterate through decentral components list
        for test2 in range(8):
            installed_pv_roof = (
                components.loc[
                    components["ID"].str.contains(
                        str(i) + decentral_components_list[test2]
                    )
                ]["investment/kW"]
            ).values
            installed_pv_roof = (
                float(installed_pv_roof[0]) if installed_pv_roof.size > 0 else 0
            )
            installed_pv = installed_pv + installed_pv_roof
            installed_st_roof = (
                components.loc[
                    components["ID"].str.contains(
                        str(i) + decentral_components_list[8 + test2]
                    )
                ]["investment/kW"]
            ).values
            installed_st_roof = (
                float(installed_st_roof[0]) if installed_st_roof.size > 0 else 0
            )
            installed_st = installed_st + installed_st_roof

        max_total_pv = sum(maximums_pv)
        max_total_st = sum(maximums_st)

        # dict to append the values
        decentral_components_dict = {
            "Cluster": str(i),
            "PV north": installed_power[0],
            "Max. PV north": maximums_pv[0],
            "PV north east": installed_power[1],
            "Max. PV north east": maximums_pv[1],
            "PV east": installed_power[2],
            "Max. PV east": maximums_pv[2],
            "PV south east": installed_power[3],
            "Max. PV south east": maximums_pv[3],
            "PV south": installed_power[4],
            "Max. PV south": maximums_pv[4],
            "PV south west": installed_power[5],
            "Max. PV south west": maximums_pv[5],
            "PV west": installed_power[6],
            "Max. PV west": maximums_pv[6],
            "PV north west": installed_power[7],
            "Max. PV north west": maximums_pv[7],
            "Installed PV": installed_pv,
            "Max. PV": max_total_pv,
            "ST north": installed_power[8],
            "Max. ST north": maximums_st[0],
            "ST north east": installed_power[9],
            "Max. ST north east": maximums_st[1],
            "ST east": installed_power[10],
            "Max. ST east": maximums_st[2],
            "ST south east": installed_power[11],
            "Max. ST south east": maximums_st[3],
            "ST south": installed_power[12],
            "Max. ST south": maximums_st[4],
            "ST south west": installed_power[13],
            "Max. ST south west": maximums_st[5],
            "ST west": installed_power[14],
            "Max. ST west": maximums_st[6],
            "ST north west": installed_power[15],
            "Max. ST north west": maximums_st[7],
            "Installed ST": installed_st,
            "Max. ST": max_total_st,
            "Gasheating-System": installed_power[16],
            "ASHP": installed_power[17],
            "GCHP": installed_power[18],
            "Battery-Storage": installed_power[19],
            "Thermal-Storage": installed_power[20],
            "Electric Heating": installed_power[21],
            "COM Electricity Demand": installed_power[22],
            "RES Electricity Demand": installed_power[23],
            "Electricity Import": installed_power[24],
            "Electricity Export": installed_power[25],
            "District Heating": dh,
        }

        decentral_components = decentral_components.append(
            pd.Series(decentral_components_dict), ignore_index=True
        )

    return decentral_components


def __create_decentral_overview_energy_amount(components):
    decentral_columns = [
        "Cluster",
        "PV north",
        "PV north east",
        "PV east",
        "PV south east",
        "PV south",
        "PV south west",
        "PV west",
        "PV north west",
        "Produced Amount PV",
        "PV excess",
        "PV->Central",
        "clusterintern consumption",
        "Total_Production - PV excess",
    ]
    # "ST north", "Max. ST north", "ST north east", "Max. ST north east",
    # "ST east", "Max. ST east", "ST south east", "Max. ST south east",
    # "ST south", "Max. ST south", "ST south west", "Max. ST south west",
    # "ST west", "Max. ST west", "ST north west", "Max. ST north west",
    # "Installed ST", "Max. ST",
    # "Gasheating-System", "ASHP", "GCHP", "Battery-Storage",
    # "Thermal-Storage", "Electric Heating", "COM Electricity Demand",
    # "RES Electricity Demand", "Electricity Import", "Electricity Export",
    # "District Heating"]
    # defining units for decentral components
    decentral_columns_units = {
        "Cluster": "",
        "PV north": "(kWh)",
        "PV north east": "(kWh)",
        "PV east": "(kWh)",
        "PV south east": "(kWh)",
        "PV south": "(kWh)",
        "PV south west": "(kWh)",
        "PV west": "(kWh)",
        "PV north west": "(kWh)",
        "Produced Amount PV": "(kWh)",
        "PV excess": "(kWh)",
        "PV->Central": "(kWh)",
        "clusterintern consumption": "(kWh)",
        "Total_Production - PV excess": "(kWh)",
    }

    decentral_components = pd.DataFrame(columns=decentral_columns)
    decentral_components = decentral_components.append(
        pd.Series(decentral_columns_units), ignore_index=True
    )

    decentral_components_from_csv = __remove_redundant_comps(components, [], wo_pv=True)

    for i in decentral_components_from_csv:
        installed_power = []
        installed_pv = 0.0
        for comp in decentral_components_list:
            if "pv" in comp:
                print(comp)
                if "excess" in comp or "central" in comp:
                    variable_central = (
                        components.loc[components["ID"].str.contains(str(i) + comp)][
                            "input 1/kWh"
                        ]
                    ).values
                else:
                    # investment values of pv
                    variable_central = (
                        components.loc[components["ID"].str.contains(str(i) + comp)][
                            "output 1/kWh"
                        ]
                    ).values
                variable_central = (
                    float(variable_central[0]) if variable_central.size > 0 else 0
                )
                installed_power.append(variable_central)
        for test2 in range(8):
            installed_pv_roof = (
                components.loc[
                    components["ID"].str.contains(
                        str(i) + decentral_components_list[test2]
                    )
                ]["output 1/kWh"]
            ).values
            installed_pv_roof = (
                float(installed_pv_roof[0]) if installed_pv_roof.size > 0 else 0
            )
            installed_pv = installed_pv + installed_pv_roof
        decentral_components_dict = {
            "Cluster": str(i),
            "PV north": installed_power[0],
            "PV north east": installed_power[1],
            "PV east": installed_power[2],
            "PV south east": installed_power[3],
            "PV south": installed_power[4],
            "PV south west": installed_power[5],
            "PV west": installed_power[6],
            "PV north west": installed_power[7],
            "Produced Amount PV": installed_pv,
            "PV excess": installed_power[8],
            "PV->Central": installed_power[9],
            "clusterintern consumption": (
                installed_pv - (installed_power[8] + installed_power[9])
            ),
            "Total_Production - PV excess": (installed_pv - installed_power[8]),
        }
        decentral_components = decentral_components.append(
            pd.Series(decentral_components_dict), ignore_index=True
        )

    return decentral_components


def __create_central_overview(components):
    """
    Fetches the central component investment from components.csv and
    creates the data frame which later becomes the Excel sheet
    "central".

    :param components: pandas Dataframe consisting of the
                       components.csv data
    :type components: pd.Dataframe
    :return: -**central values** (pd.Dataframe)
    """
    # defining columns of the sheet including centralized components
    central_columns = ["label", "investment"]
    central_values = pd.DataFrame(columns=central_columns)
    central_components = []
    for comp in components["ID"]:
        k = comp.split("_")
        if k[0] == "central":
            if k[-1] in ["transformer", "storage", "link"]:
                if len(k) == len(set(k)):
                    central_components.append(comp)
    for comp in central_components:
        # investment values of central components
        variable_central = (
            components.loc[components_csv_data["ID"].str.contains(comp)][
                "investment/kW"
            ]
        ).values
        variable_central = (
            float(variable_central[0]) if variable_central.size > 0 else 0
        )
        central_components_dict = {"label": comp, "investment": variable_central}
        central_values = central_values.append(
            pd.Series(central_components_dict), ignore_index=True
        )

    return central_values


def __create_building_overview(components):
    # defining columns
    building_columns = [
        "Building",
        "heat demand",
        "insulation window",
        "insulation wall",
        "insulation roof",
        "district heating",
    ]
    building_columns_units = {
        "Building": "",
        "heat demand": "kWh",
        "insulation window": "kW",
        "insulation wall": "kW",
        "insulation roof": "kW",
        "district heating": "kW",
    }

    # creating data frame
    building_components = pd.DataFrame(columns=building_columns)
    building_components = building_components.append(
        pd.Series(building_columns_units), ignore_index=True
    )

    # components which we will select
    building_components_list = [
        "_heat_demand",
        "_window",
        "_wall",
        "_roof",
        "_heat_bus",
    ]
    building_components_from_csv = []
    for comp in components["ID"]:
        i = comp.split("_")
        if len(str(i[0])) == 9:
            if "central" not in i[0] and "clustered" not in i[0]:
                building_components_from_csv.append(i[0])
    building_components_from_csv = set(building_components_from_csv)

    for i in building_components_from_csv:
        installed_power = []
        for comp in building_components_list:
            if comp == "_heat_demand":
                variable_building = (
                    components.loc[components["ID"].str.contains(str(i) + comp)][
                        "input 1/kWh"
                    ]
                ).values
            elif comp == "_heat_bus":
                variable_building = (
                    components.loc[components["ID"].str.contains("-" + str(i) + comp)][
                        "investment/kW"
                    ]
                ).values
            else:
                variable_building = (
                    components.loc[components["ID"].str.contains(str(i) + comp)][
                        "investment/kW"
                    ]
                ).values
            variable_building = (
                float(variable_building[0]) if variable_building.size > 0 else 0
            )

            installed_power.append(variable_building)
        building_components_dict = {
            "Building": str(i),
            "heat demand": installed_power[0],
            "insulation window": installed_power[1],
            "insulation wall": installed_power[2],
            "insulation roof": installed_power[3],
            "district heating": installed_power[4],
        }
        building_components = building_components.append(
            pd.Series(building_components_dict), ignore_index=True
        )

    return building_components


def __create_summary(components):
    summary_columns = [
        "Component",
        "Component_Costs",
        "Component_Emissions",
        "Total Energy Demand",
        "Total Energy Usage",
    ]
    summary_columns_units = {
        "Component": "",
        "Component_Costs": "€/a",
        "Component_Emissions": "g/a",
        "Total Energy Demand": "",
        "Total Energy Usage": "",
    }
    # creating data frame
    summary_components = pd.DataFrame(columns=summary_columns)
    summary_components = summary_components.append(
        pd.Series(summary_columns_units), ignore_index=True
    )
    total_costs = 0
    total_constr_costs = 0
    for num, comp in components.iterrows():
        costs = "---"
        constr_costs = "---"
        if comp["periodical costs/CU"] not in [0, "0.0", "0"] or comp[
            "variable costs/CU"
        ] not in [0, "0.0", "0"]:
            costs = 0
            if comp["periodical costs/CU"] not in [0, "0.0", "0"]:
                costs += float(comp["periodical costs/CU"])
            if comp["variable costs/CU"] not in [0, "0.0", "0"]:
                costs += float(comp["variable costs/CU"])
            total_costs += costs
        if comp["constraints/CU"] not in [0, "0.0", "0"]:
            constr_costs = float(comp["constraints/CU"])
            total_constr_costs += constr_costs
        if costs != "---" or constr_costs != "---":
            building_components_dict = {
                "Component": comp["ID"],
                "Component_Costs": str(costs),
                "Component_Emissions": str(constr_costs),
                "Total Energy Demand": "---",
                "Total Energy Usage": "---",
            }
            summary_components = summary_components.append(
                pd.Series(building_components_dict), ignore_index=True
            )
    summary_csv_data = pd.read_csv("summary.csv")
    row = next(summary_csv_data.iterrows())[1]
    building_components_dict = {
        "Component": "TOTAL",
        "Component_Costs": (str(round((total_costs / 1000000), 3)) + " Mio. €/a"),
        "Component_Emissions": (
            str(round((total_constr_costs / 1000000), 3)) + " t CO2/a"
        ),
        "Total Energy Demand": (
            str(round((row["Total Energy Demand"] / 1000000), 3)) + " GWh/a"
        ),
        "Total Energy Usage": (
            str(round((row["Total Energy Usage"] / 1000000), 3)) + " GWh/a"
        ),
    }
    summary_components = summary_components.append(
        pd.Series(building_components_dict), ignore_index=True
    )
    return summary_components


def urban_district_upscaling_post_processing_clustered(components: str):
    """
    todo docstring
    """
    components_csv = pd.read_csv(components)
    components_csv = components_csv.replace(to_replace="---", value=0)
    # pre_scenario in order to import the labels
    decentral_comps = __create_decentral_overview(components_csv)
    central_comps = __create_central_overview(components_csv)
    building_comps = __create_building_overview(components_csv)
    # output
    writer = pd.ExcelWriter(
        os.path.dirname(__file__) + "/overview.xlsx", engine="xlsxwriter"
    )
    decentral_comps.to_excel(writer, "decentral_components", index=False)
    central_comps.to_excel(writer, "central_components", index=False)
    building_comps.to_excel(writer, "building_components", index=False)
    print("Overview created.")
    writer.save()


if __name__ == "__main__":
    # csv which contains the exportable data
    components_csv_data = pd.read_csv("components.csv")

    # replace defect values with 0
    components_csv_data = components_csv_data.replace(to_replace="---", value=0)

    # pre_scenario in order to import the labels
    decentral_components = __create_decentral_overview(components_csv_data)
    central_values = __create_central_overview(components_csv_data)
    building_components = __create_building_overview(components_csv_data)
    decentral_components2 = __create_decentral_overview_energy_amount(
        components_csv_data
    )
    # summary = __create_summary(components_csv_data)
    # output
    writer = pd.ExcelWriter(
        os.path.dirname(__file__) + "/overview.xlsx", engine="xlsxwriter"
    )
    decentral_components.to_excel(writer, "decentral_components", index=False)
    decentral_components2.to_excel(writer, "decentral_components_amounts", index=False)
    central_values.to_excel(writer, "central_components", index=False)
    building_components.to_excel(writer, "building_components", index=False)
    # summary.to_excel(writer, "summary", index=False)
    writer.save()
