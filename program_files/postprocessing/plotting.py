# TODO PLOT MATRIX MIT BUBBLES(LEISTUNG)
# TODO ENERGIEMENGEN
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import xlsxwriter
from scipy.interpolate import BSpline, make_interp_spline

# creating a list to reduce the number of rows
decentral_components_list = \
    ["_north_pv", "_north_east_pv", "_east_pv", "_south_east_pv",
     "_south_pv", "_south_west_pv", "_west_pv", "_north_west_pv",
     "_north_solarthermal_source_collector",
     "_north_east_solarthermal_source_collector",
     "_east_solarthermal_source_collector",
     "_south_east_solarthermal_source_collector",
     "_south_solarthermal_source_collector",
     "_south_west_solarthermal_source_collector",
     "_west_solarthermal_source_collector",
     "_north_west_solarthermal_source_collector",
     "_gasheating_transformer", "_ashp_transformer", "_gchp_transformer",
     "_battery_storage",
     "_thermal_storage", "_electricheating_transformer",
     "_com_electricity_demand", "_res_electricity_demand",
     "_electricity_bus_shortage", "_pv_bus_excess", "_heat_bus", "pv_central",
     "central_electricity", "_hp_elec_bus_shortage",
     "_com_electricity_bus_shortage", "_res_electricity_bus_shortage",
     "_heat_bus", ""]

def create_pareto_plot(dfs):
    points = {}
    costs_moni = []
    costs_emi = []
    for dataframe in dfs:
        costs_moni.append(sum(dataframe["variable costs/CU"])\
                          + sum(dataframe["periodical costs/CU"]))
        costs_emi.append(sum(dataframe["constraints/CU"]))
    df1 = pd.DataFrame({"costs": costs_moni, "emissions": costs_emi},
                      columns=["costs", "emissions"])
    #df1 = df1.sort_values("costs")
    #f2 = make_interp_spline(df1["costs"], df1["emissions"])
    #fac = np.polyfit(df1["costs"], df1["emissions"], 1)
    #print(fac)
    #x_new = np.linspace(df1.iloc[0]["costs"], df1.iloc[-1]["costs"], 20)
    #y_new = f2(x_new)
    #df2 = pd.DataFrame({"costs": x_new, "emissions": y_new},
    #                   columns=["costs", "emissions"])

    sns.lineplot(data=df1, x="costs", y="emissions", marker="o")
    #sns.lineplot(data=df2, x="costs", y="emissions")
    plt.grid()
    plt.show()


def __remove_redundant_comps(components, decentral_components_from_csv):
    for comp in components["ID"]:
        i = comp.split("_")
        if "pv" not in i[0]:
            if "central" not in i[0]:
                if "RES" not in i[0] and "COM" not in i[0]:
                    if len(str(i[0])) <= 4:
                        decentral_components_from_csv.append(i[0])
    decentral_components_from_csv = set(decentral_components_from_csv)
    return decentral_components_from_csv


def create_energy_amount_plot_elec(dfs):
    # defining units for decentral components
    elec_amounts = pd.DataFrame()
    elec_amounts_dict = {}
    emissions_100_percent = sum(dfs[1]["constraints/CU"])
    for key in dfs:
        elec_amounts_dict.update(
            {"run": str(key),
             "PV_north": [], "PV_north_east": [], "PV_east": [],
             "PV_south_east": [], "PV_south": [], "PV_south_west": [],
             "PV_west": [], "PV_north_west": [], "Produced_Amount_PV": [],
             "PV_excess": [], "PV_to_Central": [],
             "COM_Electricity_Demand": [], "RES_Electricity_Demand": [],
             "Elec_Demand_SLPs": [], "Heatpump_elec": [],
             "Import_system_internal": [], "grid_import": [],
             "Electric_heating": [], "Battery_losses": [], "ST_elec": [],
             "Elec_Demand_Heat": [], "Total Elec. Demand": [],
             "reductionco2": sum(dfs[key]["constraints/CU"])
                             / emissions_100_percent})
        dataframe = dfs[key]
        decentral_components_from_csv = \
            __remove_redundant_comps(dataframe, [])
        for i in decentral_components_from_csv:
            amounts = []
            amount_pv = 0.0
            amount_st = 0.0
            for comp in decentral_components_list:
                amount = pd.Series()
                if "pv" in comp:
                    if "excess" in comp or "central" in comp:
                        # verkaufter PV Strom
                        amount = (dataframe.loc[dataframe["ID"].str.startswith(
                                    str(i) + comp)]["input 1/kWh"]).values
                    else:
                        # investment values of pv
                        amount = (dataframe.loc[dataframe["ID"].str.startswith(
                                    str(i) + comp)]["output 1/kWh"]).values
                elif comp in ["_com_electricity_demand",
                              "_res_electricity_demand"] \
                        or "central_electricity" in comp \
                        or "solarthermal" in comp \
                        or "ashp" in comp or "gchp" in comp \
                        or "electricheating" in comp:
                    amount = (dataframe.loc[dataframe["ID"].str.startswith(
                                str(i) + comp)]["input 1/kWh"]).values
                elif comp in ["_hp_elec_bus_shortage",
                              "_electricity_bus_shortage",
                              "_com_electricity_bus_shortage",
                              "_res_electricity_bus_shortage"]:
                    amount = (dataframe.loc[dataframe["ID"].str.startswith(
                                str(i) + comp)]["output 1/kWh"]).values
                elif "_battery_storage" in comp:
                    # battery losses
                    batteryinput = \
                        (dataframe.loc[
                            dataframe["ID"].str.startswith(str(i) + comp)]
                        ["input 1/kWh"]).values
                    batteryinput = float(batteryinput[0]) \
                        if batteryinput.size > 0 else 0
                    batteryoutput = \
                        (dataframe.loc[
                            dataframe["ID"].str.startswith(str(i) + comp)]
                        ["output 1/kWh"]).values
                    batteryoutput = float(batteryoutput[0]) \
                        if batteryoutput.size > 0 else 0
                    amount = \
                        pd.Series(data={"battery":
                                        (batteryinput - batteryoutput)})
                amounts.append(float(amount[0]) if amount.size > 0 else 0)

            for num in range(8):
                amount_pv_roof = (
                dataframe.loc[dataframe["ID"].str.startswith(
                    str(i) + decentral_components_list[num])]
                ["output 1/kWh"]).values
                amount_pv += float(amount_pv_roof[0]) \
                    if amount_pv_roof.size > 0 else 0
                amount_st_roof = (
                dataframe.loc[dataframe["ID"].str.startswith(
                    str(i) + decentral_components_list[num + 8])]
                ["input 1/kWh"]).values
                amount_st += float(amount_st_roof[0]) \
                    if amount_st_roof.size > 0 else 0

            elec_amounts_dict["PV_north"].append(amounts[0])
            elec_amounts_dict["PV_north_east"].append(amounts[1])
            elec_amounts_dict["PV_east"].append(amounts[2])
            elec_amounts_dict["PV_south_east"].append(amounts[3])
            elec_amounts_dict["PV_south"].append(amounts[4])
            elec_amounts_dict["PV_south_west"].append(amounts[5])
            elec_amounts_dict["PV_west"].append(amounts[6])
            elec_amounts_dict["PV_north_west"].append(amounts[7])
            elec_amounts_dict["Produced_Amount_PV"].append(amount_pv)
            elec_amounts_dict["PV_excess"].append(amounts[25])
            elec_amounts_dict["PV_to_Central"].append(amounts[27])
            elec_amounts_dict["COM_Electricity_Demand"].append(amounts[22])
            elec_amounts_dict["RES_Electricity_Demand"].append(amounts[23])
            elec_amounts_dict["Elec_Demand_SLPs"].append((amounts[22] + amounts[23]))
            elec_amounts_dict["Heatpump_elec"].append((amounts[17] + amounts[18]))
            elec_amounts_dict["Import_system_internal"].append(amounts[28])
            elec_amounts_dict["grid_import"].append((amounts[24] + amounts[29] + amounts[30] + amounts[31]))
            elec_amounts_dict["Electric_heating"].append(amounts[21])
            elec_amounts_dict["Battery_losses"].append(amounts[19])
            elec_amounts_dict["ST_elec"].append(amount_st)
            elec_amounts_dict["Elec_Demand_Heat"].append((amounts[17] + amounts[18] + amounts[21] + amount_st))
            elec_amounts_dict["Total Elec. Demand"].append((amounts[17] + amounts[18] + amounts[21] + amount_st + amounts[22] + amounts[23]))

        for i in elec_amounts_dict:
            if i != "run" and i != "reductionco2":
                elec_amounts_dict[i] = sum(elec_amounts_dict[i])
        elec_amounts = elec_amounts.append(pd.Series(elec_amounts_dict),
                                           ignore_index=True)
    elec_amounts.to_csv("test.csv")
    elec_amounts.set_index("reductionco2", inplace=True, drop=False)
    elec_amounts = elec_amounts.sort_values("run")
    fig, axs = plt.subplots(4)
    fig.set_size_inches(18.5, 10.5)
    labels1 = ['SLP_DEMAND', 'HEAT_ELEC_DEMAND', "PV EXCESS", "PV_to_Central",
               "Battery losses"]
    axs[0].stackplot(elec_amounts.reductionco2,
                     elec_amounts.Elec_Demand_SLPs,
                     elec_amounts.Elec_Demand_Heat,
                     elec_amounts.PV_excess,
                     elec_amounts.PV_to_Central,
                     elec_amounts.Battery_losses, labels=labels1)
    labels2 = ['PV', 'GRID', 'local_MARKET']
    axs[1].stackplot(elec_amounts.reductionco2,
                     elec_amounts.Produced_Amount_PV,
                     elec_amounts.grid_import,
                     elec_amounts.Import_system_internal, labels=labels2)
    labels3 = ["PV_north", "PV_north_east", "PV_east", "PV_south_east",
               "PV_south", "PV_south_west", "PV_west", "PV_north_west"]
    axs[2].stackplot(elec_amounts.reductionco2,
                     elec_amounts.PV_north,
                     elec_amounts.PV_north_east,
                     elec_amounts.PV_east,
                     elec_amounts.PV_south_east,
                     elec_amounts.PV_south,
                     elec_amounts.PV_south_west,
                     elec_amounts.PV_west,
                     elec_amounts.PV_north_west,
                     labels=labels3)
    labels4 = ["Electric_heating", "Heatpump_elec", "ST_elec"]
    axs[3].stackplot(elec_amounts.reductionco2,
                     elec_amounts.Electric_heating,
                     elec_amounts.Heatpump_elec,
                     elec_amounts.ST_elec,
                     labels=labels4)
    axs[0].invert_xaxis()
    axs[0].legend()
    axs[1].invert_xaxis()
    axs[1].legend()
    axs[2].invert_xaxis()
    axs[2].legend(loc="upper left")
    axs[3].invert_xaxis()
    axs[3].legend(loc="upper left")
    plt.show()


if __name__ == "__main__":

    df1 = pd.read_csv("/Users/gregorbecker/Downloads/SESMG-dev_open_district_upscaling/results/2022-03-03--15-50-12/components_1.csv")
    df2 = pd.read_csv("/Users/gregorbecker/Downloads/SESMG-dev_open_district_upscaling/results/2022-03-03--15-50-12/components_0.1.csv")
    df3 = pd.read_csv("/Users/gregorbecker/Downloads/SESMG-dev_open_district_upscaling/results/2022-03-03--15-50-12/components_0.2.csv")
    df4 = pd.read_csv("/Users/gregorbecker/Downloads/SESMG-dev_open_district_upscaling/results/2022-03-03--15-50-12/components_0.3.csv")
    df5 = pd.read_csv("/Users/gregorbecker/Downloads/SESMG-dev_open_district_upscaling/results/2022-03-03--15-50-12/components_0.4.csv")
    df6 = pd.read_csv("/Users/gregorbecker/Downloads/SESMG-dev_open_district_upscaling/results/2022-03-03--15-50-12/components_0.5.csv")
    df7 = pd.read_csv("/Users/gregorbecker/Downloads/SESMG-dev_open_district_upscaling/results/2022-03-03--15-50-12/components_0.6.csv")
    df8 = pd.read_csv("/Users/gregorbecker/Downloads/SESMG-dev_open_district_upscaling/results/2022-03-03--15-50-12/components_0.7.csv")
    df9 = pd.read_csv("/Users/gregorbecker/Downloads/SESMG-dev_open_district_upscaling/results/2022-03-03--15-50-12/components_0.8.csv")
    df10 = pd.read_csv("/Users/gregorbecker/Downloads/SESMG-dev_open_district_upscaling/results/2022-03-03--15-50-12/components_0.9.csv")


    #create_pareto_plot([df1, df2, df3,df4, df5, df6, df7, df8, df9, df10])
    create_energy_amount_plot_elec(
        {1: df1,
         0.1: df2,
         0.2: df3,
         0.3: df4,
         0.4: df5,
         0.5: df6,
         0.6: df7,
         0.7: df8,
         0.8: df9,
         0.9: df10})




















