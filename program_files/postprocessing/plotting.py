# TODO PLOT MATRIX MIT BUBBLES(LEISTUNG)
# TODO ENERGIEMENGEN
# TODO ENERGIEMENGEN DER SENKEN OPTIONAL NACH SEKTOR SELEKTIEREN SODASS
#  UNTERSCHEIDUNG IM PLOT MÖGLICH IST
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import xlsxwriter
from scipy.interpolate import BSpline, make_interp_spline
from program_files.preprocessing.create_energy_system import import_scenario
import tkinter as tk
from tkinter import ttk
from program_files.GUI_files import GUI

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


def create_pareto_plot(dfs, result_path):
    points = {}
    costs_moni = []
    costs_emi = []
    for dataframe in dfs:
        costs_moni.append(sum(dataframe["variable costs/CU"]) \
                          + sum(dataframe["periodical costs/CU"]))
        costs_emi.append(sum(dataframe["constraints/CU"]))
    df1 = pd.DataFrame({"costs": costs_moni, "emissions": costs_emi},
                       columns=["costs", "emissions"])
    # df1 = df1.sort_values("costs")
    # f2 = make_interp_spline(df1["costs"], df1["emissions"])
    # fac = np.polyfit(df1["costs"], df1["emissions"], 1)
    # print(fac)
    # x_new = np.linspace(df1.iloc[0]["costs"], df1.iloc[-1]["costs"], 20)
    # y_new = f2(x_new)
    # df2 = pd.DataFrame({"costs": x_new, "emissions": y_new},
    #                   columns=["costs", "emissions"])
    
    plot = sns.lineplot(data=df1, x="costs", y="emissions", marker="o")
    # sns.lineplot(data=df2, x="costs", y="emissions")
    plt.grid()
    plt.savefig(result_path + "/pareto.jpeg")


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


def get_family(a, df1):
    family = get_ancestors(a, [], df1) + get_children(a, [], df1)
    return family


def get_ancestors(a, ancestors, df1):
    for anc in df1[df1["bus2"] == a]["bus1"]:
        ancestors = ancestors + [anc] + get_ancestors(anc, ancestors, df1)
    return ancestors


def get_children(a, children, df1):
    for child in df1[df1["bus1"] == a]["bus2"]:
        children = children + [child] + get_ancestors(child, children, df1)
    return children


def save_sinks(sink_types, tabcontrol, gui, dfs, nodes_data, sink_known,
               result_path, elec_amounts_bool=True, heat_amounts_bool=True):
    if elec_amounts_bool:
        elec_amounts = pd.DataFrame()
        elec_amounts_dict = {}
    if heat_amounts_bool:
        heat_amounts = pd.DataFrame()
        heat_amounts_dict = {}
    emissions_100_percent = sum(dfs["1"]["constraints/CU"])
    for sink in sink_types:
        sink_known.update({sink: [sink_types[sink][0].get(),
                                       sink_types[sink][1].get(),
                                       sink_types[sink][2].get()]})
    tabcontrol.forget(gui.frames[-1])
    for key in dfs:
        if elec_amounts_bool:
            elec_amounts_dict.update(
                {"run": str(key),
                 "PV_north": [], "PV_north_east": [], "PV_east": [],
                 "PV_south_east": [], "PV_south": [], "PV_south_west": [],
                 "PV_west": [], "PV_north_west": [], "Produced_Amount_PV": [],
                 "PV_excess": [], "PV_to_Central": [],
                 "Electricity_Demand": [],
                 "ASHP": [], "GCHP":[],
                 "Import_system_internal": [], "grid_import": [],
                 "Electric_heating": [], "Battery_losses": [], "ST_elec": [],
                 "Battery_output": [], "central_elec_production": [],
                 "reductionco2": sum(dfs[key]["constraints/CU"])
                                 / emissions_100_percent})
        if heat_amounts_bool:
            heat_amounts_dict.update(
                {"run": str(key),
                 "Produced_Amount_ST": [], "Electric_heating": [],
                 "Gasheating": [], "HeatPump": [], "DH": [], "Heat_Demand": [],
                 "Thermalstorage_losses": [], "Thermalstorage_output": [],
                 "ST_north": [], "ST_north_east": [],
                 "ST_east": [], "ST_south_east": [], "ST_south": [],
                 "ST_south_west": [], "ST_west": [], "ST_north_west": [],
                 "GCHP": [], "ASHP": [], "Insulation": [],
                 "central_heat_production": [],
                 "reductionco2": sum(dfs[key]["constraints/CU"])
                                 / emissions_100_percent})
        dataframe = dfs[key].copy()
        dataframe.reset_index(inplace=True, drop=False)
        counter = 0
        for key in nodes_data.keys():
            if key not in ["energysystem", "timeseries",
                           "weather data", "district heating",
                           "competition constraints"]:
                nodes_data[key].set_index("label", inplace=True, drop=False)
                if counter == 0:
                    df_1 = nodes_data[key].copy()
                    counter += 1
                else:
                    df_1 = df_1.append(nodes_data[key], sort=True)
        # TODO concentrated solar power
        df_pv_st = df_1[(df_1.isin(['photovoltaic'])).any(axis=1)]
        df_pv_st = df_pv_st.append(df_1[(df_1.isin(['solar_thermal_flat_plate']))
                                   .any(axis=1)])
        pv_buses = []
        st_buses = []
        elec_buses = []
        # heat pump dataframe
        df_hp_absch = df_1[(df_1.isin(['CompressionHeatTransformer'])).any(axis=1)]
        df_hp_absch = \
            df_hp_absch.append(df_1[(df_1.isin(['AbsorptionHeatTransformer']))
                               .any(axis=1)])
        hp_buses_input = []
        hp_buses_output = []
        # sink dataframe
        df_sinks = df_1[(df_1['annual demand'].notna())]
        df_sinks = df_sinks.append(df_1[df_1["nominal value"].notna()])
        sink_inputs_el = []
        sink_inputs_heat = []
        # link dataframe
        link_inputs = []
        df_links = df_1[(df_1['bus1'].notna())]
        # storage dataframe
        df_storage = df_1[df_1['bus'].notna()]
        # generic transformer dataframe
        df_gen_transformer = df_1[(df_1.isin(['GenericTransformer'])).any(axis=1)]
        # insulation dataframe
        df_insulation = df_1[df_1['U-value new'].notna()]
        for num, comp in df_pv_st.iterrows():
            if comp["active"]:
                # collect output of active photovoltaic panels
                if comp["technology"] == "photovoltaic":
                    value = dataframe.loc[dataframe["ID"].str.startswith(
                            comp["label"])]["output 1/kWh"].values
                    value = float(value[0]) if value.size > 0 else 0
                    elec_amounts_dict["Produced_Amount_PV"].append(value)
                    # TODO wie stellen wir fest ob -180 - 180 oder 0 - 360 genutzt wurde
                    if -22.5 <= comp["Azimuth"] < 22.5:
                        elec_amounts_dict["PV_north"].append(value)
                    elif 22.5 <= comp["Azimuth"] < 67.5:
                        elec_amounts_dict["PV_north_east"].append(value)
                    elif 67.5 <= comp["Azimuth"] < 112.5:
                        elec_amounts_dict["PV_east"].append(value)
                    elif 112.5 <= comp["Azimuth"] < 157.5:
                        elec_amounts_dict["PV_south_east"].append(value)
                    elif comp["Azimuth"] >= 157.5 \
                            or comp["Azimuth"] < -157.5:
                        elec_amounts_dict["PV_south"].append(value)
                    elif -157.5 <= comp["Azimuth"] < -112.5:
                        elec_amounts_dict["PV_south_west"].append(value)
                    elif -112.5 <= comp["Azimuth"] < -67.5:
                        elec_amounts_dict["PV_west"].append(value)
                    elif -67.5 <= comp["Azimuth"] < -22.5:
                        elec_amounts_dict["PV_north_west"].append(value)
                    pv_buses.append(comp["output"])

                elif comp["technology"] == "solar_thermal_flat_plate":
                    # collect electric input flow of solar thermal flat plate
                    value = dataframe.loc[dataframe["ID"].str.startswith(
                            comp["label"])]["input 1/kWh"].values
                    value = float(value[0]) if value.size > 0 else 0
                    elec_amounts_dict["ST_elec"].append(value)
                    # heat output solar thermal flat plates
                    value = dataframe.loc[dataframe["ID"].str.startswith(
                        comp["label"])]["output 1/kWh"].values
                    value = float(value[0]) if value.size > 0 else 0
                    heat_amounts_dict["Produced_Amount_ST"].append(value)
                    # TODO wie stellen wir fest ob -180 - 180 oder 0 - 360 genutzt wurde
                    if -22.5 <= comp["Azimuth"] < 22.5:
                        heat_amounts_dict["ST_north"].append(value)
                    elif 22.5 <= comp["Azimuth"] < 67.5:
                        heat_amounts_dict["ST_north_east"].append(value)
                    elif 67.5 <= comp["Azimuth"] < 112.5:
                        heat_amounts_dict["ST_east"].append(value)
                    elif 112.5 <= comp["Azimuth"] < 157.5:
                        heat_amounts_dict["ST_south_east"].append(value)
                    elif comp["Azimuth"] >= 157.5 \
                            or comp["Azimuth"] < -157.5:
                        heat_amounts_dict["ST_south"].append(value)
                    elif -157.5 <= comp["Azimuth"] < -112.5:
                        heat_amounts_dict["ST_south_west"].append(value)
                    elif -112.5 <= comp["Azimuth"] < -67.5:
                        heat_amounts_dict["ST_west"].append(value)
                    elif -67.5 <= comp["Azimuth"] < -22.5:
                        heat_amounts_dict["ST_north_west"].append(value)
                    st_buses.append(comp["output"])
        # check rather pv produced amount is sold
        for bus in pv_buses:
            value = dataframe.loc[dataframe["ID"].str.startswith(
                    str(bus) + "_excess")]["input 1/kWh"].values
            value = float(value[0]) if value.size > 0 else 0
            elec_amounts_dict["PV_excess"].append(value)

        # collect electric input flow of Heat Pumps
        for num, comp in df_hp_absch.iterrows():
            if comp["active"]:
                if comp["transformer type"] == "CompressionHeatTransformer"\
                        and comp["heat source"] == "Ground":
                    value = dataframe.loc[dataframe["ID"].str.startswith(
                            comp["label"])]["input 1/kWh"].values
                    value = float(value[0]) if value.size > 0 else 0
                    elec_amounts_dict["GCHP"].append(value)
                    # gchp heat output
                    value = dataframe.loc[dataframe["ID"].str.startswith(
                            comp["label"])]["output 1/kWh"].values
                    value = float(value[0]) if value.size > 0 else 0
                    heat_amounts_dict["GCHP"].append(value)
                    if comp["input"] not in hp_buses_input:
                        hp_buses_input.append(comp["input"])
                    if comp["output"] not in hp_buses_output:
                        hp_buses_output.append(comp["output"])
                elif comp["transformer type"] == "CompressionHeatTransformer"\
                        and comp["heat source"] == "Air":
                    value = dataframe.loc[dataframe["ID"].str.startswith(
                            comp["label"])]["input 1/kWh"].values
                    value = float(value[0]) if value.size > 0 else 0
                    elec_amounts_dict["ASHP"].append(value)
                    # ashp heat output
                    value = dataframe.loc[dataframe["ID"].str.startswith(
                            comp["label"])]["output 1/kWh"].values
                    value = float(value[0]) if value.size > 0 else 0
                    heat_amounts_dict["ASHP"].append(value)
                    if comp["input"] not in hp_buses_input:
                        hp_buses_input.append(comp["input"])
                    if comp["output"] not in hp_buses_output:
                        hp_buses_output.append(comp["output"])

        # collect the amount of electricity demand
        for num, sink in df_sinks.iterrows():
            if sink["active"]:
                if sink_known[sink["label"]][0]:
                    value = dataframe.loc[dataframe["ID"].str.startswith(
                        sink["label"])]["input 1/kWh"].values
                    value = float(value[0]) if value.size > 0 else 0
                    elec_amounts_dict["Electricity_Demand"].append(value)
                    sink_inputs_el.append(sink["input"])
                if sink_known[sink["label"]][1]:
                    value = dataframe.loc[dataframe["ID"].str.startswith(
                        sink["label"])]["input 1/kWh"].values
                    value = float(value[0]) if value.size > 0 else 0
                    heat_amounts_dict["Heat_Demand"].append(value)
                    sink_inputs_heat.append(sink["input"])
        buses_el = []
        for bus in sink_inputs_el + hp_buses_input:
            buses_el.append(bus)
            buses_el += get_family(bus, df_1)
        buses_el = list(set(buses_el))
        buses_heat = []
        for bus in sink_inputs_heat + hp_buses_output:
            buses_heat.append(bus)
            buses_heat += get_family(bus, df_1)
        buses_heat = list(set(buses_heat))
        for num, link in df_links.iterrows():
            if link["active"]:
                # pvbus -> local electricity market
                if link["bus1"] in pv_buses:
                    if link["bus2"] not in sink_inputs_el \
                            and "central" in link["bus2"]:
                        value = \
                            dataframe.loc[dataframe["ID"].str.startswith(
                                link["label"])]["output 1/kWh"].values
                        value = float(value[0]) if value.size > 0 else 0
                        elec_amounts_dict["PV_to_Central"].append(value)
                else:
                    # link outflow in a bus having a sink
                    if link["bus2"] in sink_inputs_el:
                        link_inputs.append(link["bus1"])
        for num, link in df_links.iterrows():
            if link["active"]:
                # link connecting central bus to a bus having a sink, or
                # a bus linked to a bus having a sink
                if "central" in link["bus1"] and link["bus2"] in buses_el \
                        and "central" not in link["bus2"]:
                    value = dataframe.loc[dataframe["ID"].str.startswith(
                        link["label"])]["output 1/kWh"].values
                    value = float(value[0]) if value.size > 0 else 0
                    elec_amounts_dict[
                        "Import_system_internal"].append(value)
                # link connecting central production plant to central
                # elec bus
                if "central" in link["bus2"] \
                        and link["bus1"] not in pv_buses:
                    value = dataframe.loc[dataframe["ID"].str.startswith(
                        link["label"])]["output 1/kWh"].values
                    value = float(value[0]) if value.size > 0 else 0
                    elec_amounts_dict[
                        "central_elec_production"].append(value)

        for num, storage in df_storage.iterrows():
            if storage["active"]:
                # collect battery output and losses of an active storage
                if storage["bus"] in buses_el \
                        and "central" not in storage["bus"]:
                    value = dataframe.loc[dataframe["ID"].str.startswith(
                        storage["label"])]["output 1/kWh"].values
                    value = float(value[0]) if value.size > 0 else 0
                    elec_amounts_dict["Battery_output"].append(value)
                    input = dataframe.loc[dataframe["ID"].str.startswith(
                        storage["label"])]["input 1/kWh"].values
                    input = float(input[0]) if input.size > 0 else 0
                    elec_amounts_dict[
                        "Battery_losses"].append(input - value)
                # collect thermalstorage output and losses of an active
                # storage
                if storage["bus"] in buses_heat \
                        and "central" not in storage["bus"]:
                    value = \
                    dataframe.loc[dataframe["ID"].str.startswith(
                        storage["label"])]["output 1/kWh"].values
                    value = float(
                        value[0]) if value.size > 0 else 0
                    heat_amounts_dict["Thermalstorage_output"].append(
                        value)
                    input = \
                    dataframe.loc[dataframe["ID"].str.startswith(
                        storage["label"])]["input 1/kWh"].values
                    input = float(
                        input[0]) if input.size > 0 else 0
                    heat_amounts_dict[
                        "Thermalstorage_losses"].append(input - value)

        for num, transformer in df_gen_transformer.iterrows():
            if transformer["active"]:
                # collecting GenericTransformer with electric input
                # (Electric Heating)
                if transformer["input"] in buses_el \
                        and "central" not in transformer["input"]:
                    value = dataframe.loc[dataframe["ID"].str.startswith(
                        transformer["label"])]["input 1/kWh"].values
                    value = float(value[0]) if value.size > 0 else 0
                    elec_amounts_dict["Electric_heating"].append(value)
                    value = dataframe.loc[dataframe["ID"].str.startswith(
                        transformer["label"])]["output 1/kWh"].values
                    value = float(value[0]) if value.size > 0 else 0
                    heat_amounts_dict["Electric_heating"].append(value)
                # collecting outflow of central component producing
                # electricity (e.g. fuel cell)
                elif "central" in transformer["output"] \
                        and transformer["output"] in buses_el:
                    value = dataframe.loc[dataframe["ID"].str.startswith(
                        transformer["label"])]["output 1/kWh"].values
                    value = float(value[0]) if value.size > 0 else 0
                    elec_amounts_dict[
                        "central_elec_production"].append(value)
                elif "central" in transformer["output"] \
                    and transformer["output"] in buses_heat:
                    value = dataframe.loc[dataframe["ID"].str.startswith(
                            transformer["label"])]["output 1/kWh"].values
                    value = float(value[0]) if value.size > 0 else 0
                    heat_amounts_dict[
                        "central_heat_production"].append(value)
                # collecting outflow of gasheating plants
                elif "central" not in transformer["label"]:
                    if "gas" not in transformer["label"]:
                        print("Is transformer " + transformer["label"]
                              + "a gasheating plant?")
                    value = dataframe.loc[dataframe["ID"].str.startswith(
                            transformer["label"])]["output 1/kWh"].values
                    value = float(value[0]) if value.size > 0 else 0
                    heat_amounts_dict["Gasheating"].append(value)
        # collect the inflow of all bus out of shortages (grid import)
        for bus in buses_el:
            value = dataframe.loc[dataframe["ID"].str.startswith(
                bus + "_shortage")]["output 1/kWh"].values
            value = float(value[0]) if value.size > 0 else 0
            elec_amounts_dict["grid_import"].append(value)
        # sum the amounts of each component found above for later plotting
        for i in elec_amounts_dict:
            if i != "run" and i != "reductionco2":
                elec_amounts_dict[i] = sum(elec_amounts_dict[i])
        elec_amounts = elec_amounts.append(pd.Series(elec_amounts_dict),
                                           ignore_index=True)
        elec_amounts.set_index("reductionco2", inplace=True, drop=False)
        elec_amounts = elec_amounts.sort_values("run")

        # collects insulation output flows
        for num, insulation in df_insulation.iterrows():
            if insulation["active"]:
                cap_sink = dataframe.loc[dataframe["ID"].str.startswith(
                        insulation["sink"])]["capacity/kW"].values
                cap_sink = float(cap_sink[0]) if cap_sink.size > 0 else 0
                cap_insulation = \
                    dataframe.loc[dataframe["ID"].str.startswith(
                        insulation["label"])]["capacity/kW"].values
                cap_insulation = float(cap_insulation[0]) \
                    if cap_insulation.size > 0 else 0
                value_sink = dataframe.loc[dataframe["ID"].str.startswith(
                        insulation["sink"])]["input 1/kWh"].values
                value_sink = float(value_sink[0]) if value_sink.size > 0 \
                    else 0
                if cap_insulation != 0:
                    heat_amounts_dict["Insulation"].append(
                        ((cap_insulation * value_sink) / cap_sink))

        heat_amounts_dict["DH"] += list(dataframe.loc[dataframe[
            "ID"].str.startswith("dh_heat_house_station")][
                                           "output 1/kWh"].values)
        for i in heat_amounts_dict:
            if i != "run" and i != "reductionco2":
                heat_amounts_dict[i] = sum(heat_amounts_dict[i])
        heat_amounts = heat_amounts.append(pd.Series(heat_amounts_dict),
                                           ignore_index=True)
        heat_amounts.set_index("reductionco2", inplace=True, drop=False)
        heat_amounts = heat_amounts.sort_values("run")
        # ELEC PLOT
        if elec_amounts_bool:
            color = sns.color_palette("Spectral", 16)
            fig, axs = plt.subplots(
                5 if sum(elec_amounts.Produced_Amount_PV) != 0
                else 4, sharex=True)
            fig.tight_layout()
            fig.set_size_inches(18.5, 15.5)
            labels1 = ['SLP_DEMAND',  # 'HEAT_ELEC_DEMAND',
                       "PV EXCESS" if sum(elec_amounts.PV_excess) != 0 else None,
                       "PV_to_Central" if sum(elec_amounts.PV_to_Central) != 0 else None,
                       "Battery losses"]
            axs[0].stackplot(elec_amounts.reductionco2,
                             elec_amounts.Electricity_Demand,
                             elec_amounts.PV_excess,
                             elec_amounts.PV_to_Central,
                             elec_amounts.Battery_losses, labels=labels1, edgecolor="black", colors=[color[0], color[8], color[15]])
            labels2 = ['PV' if sum(elec_amounts.Produced_Amount_PV) != 0 else None,
                       'PV to local market' if sum(elec_amounts.PV_to_Central) != 0 else None,
                       'GRID' if sum(elec_amounts.grid_import) != 0 else None,
                       'local_MARKET'
                       if sum(elec_amounts.Import_system_internal
                              - elec_amounts.PV_to_Central) != 0 else None]
            stacks = axs[1].stackplot(elec_amounts.reductionco2,
                             elec_amounts.Produced_Amount_PV - elec_amounts.PV_to_Central,
                             elec_amounts.PV_to_Central,
                             elec_amounts.grid_import,
                             elec_amounts.Import_system_internal
                             - elec_amounts.PV_to_Central, labels=labels2, edgecolor="black", colors=[color[0], color[0], color[8], color[15]])
            hatches = ["", "/", "", ""]
            for stack, hatch in zip(stacks, hatches):
                stack.set_hatch(hatch)
            #axs[1].fill_between(elec_amounts.reductionco2,
            #                    elec_amounts.Produced_Amount_PV - elec_amounts.PV_to_Central, alpha=0.5)
            labels4 = ["Electric_heating" if sum(elec_amounts.Electric_heating) != 0 else None,
                       "Heatpump_elec" if sum(elec_amounts.GCHP + elec_amounts.ASHP) != 0 else None,
                       "ST_elec" if sum(elec_amounts.ST_elec) != 0 else None]
            axs[2].stackplot(elec_amounts.reductionco2,
                             elec_amounts.Electric_heating,
                             elec_amounts.GCHP + elec_amounts.ASHP,
                             elec_amounts.ST_elec,
                             labels=labels4, edgecolor="black", colors=[color[0], color[8], color[15]])
            labels5 = ["central_elec_production"]
            axs[3].stackplot(elec_amounts.reductionco2,
                             elec_amounts.central_elec_production,
                             labels=labels5, colors=color)
            if sum(elec_amounts.Produced_Amount_PV) != 0:
                labels3 = ["PV_north" if sum(elec_amounts.PV_north) != 0 else None,
                           "PV_north_east" if sum(
                               elec_amounts.PV_north_east) != 0 else None,
                           "PV_east" if sum(elec_amounts.PV_east) != 0 else None,
                           "PV_south_east" if sum(
                               elec_amounts.PV_south_east) != 0 else None,
                           "PV_south" if sum(elec_amounts.PV_south) != 0 else None,
                           "PV_south_west" if sum(
                               elec_amounts.PV_south_west) != 0 else None,
                           "PV_west" if sum(elec_amounts.PV_west) != 0 else None,
                           "PV_north_west" if sum(
                               elec_amounts.PV_north_west) != 0 else None]
                # "Battery_output"]
                axs[4].stackplot(elec_amounts.reductionco2,
                                 elec_amounts.PV_north,
                                 elec_amounts.PV_north_east,
                                 elec_amounts.PV_east,
                                 elec_amounts.PV_south_east,
                                 elec_amounts.PV_south,
                                 elec_amounts.PV_south_west,
                                 elec_amounts.PV_west,
                                 elec_amounts.PV_north_west,
                                 labels=labels3, edgecolor="black", colors=[color[0], color[2], color[4], color[6], color[8], color[10], color[12], color[14]])
            axs[0].legend()
            axs[0].set_ylabel("Electricity Amount in kWh")
            axs[1].legend()
            axs[1].set_ylabel("Electricity Amount in kWh")
            axs[2].legend(loc="upper left")
            axs[2].set_ylabel("Electricity Amount in kWh")
            axs[3].legend(loc="upper left")
            axs[3].set_ylabel("Electricity Amount in kWh")
            if sum(elec_amounts.Produced_Amount_PV) != 0:
                axs[4].invert_xaxis()
                axs[4].legend(loc="upper left")
                axs[4].set_ylabel("Electricity Amount in kWh")
                axs[4].set_xlabel("Emission-reduced Scenario")
            else:
                axs[3].invert_xaxis()
                axs[3].set_xlabel("Emission-reduced Scenario")
            plt.savefig(result_path + "/elec_amounts.jpeg")
        # HEAT PLOT
        if heat_amounts_bool:
            color = sns.color_palette("Spectral")
            fig, axs = plt.subplots(3 if sum(heat_amounts.Produced_Amount_ST) != 0
                                    else 2, sharex=True)
            fig.set_size_inches(18.5, 15.5)
            labels1 = ['SLP_DEMAND',
                       "Thermalstorage losses",
                       "Insulation"]
            stacks = axs[0].stackplot(heat_amounts.reductionco2,
                             heat_amounts.Heat_Demand - heat_amounts.Insulation,
                             heat_amounts.Thermalstorage_losses,
                             heat_amounts.Insulation,
                             labels=labels1, edgecolor="black", colors=color)
            hatches = ["", "", "/"]
            for stack, hatch in zip(stacks, hatches):
                stack.set_hatch(hatch)
            
            labels2 = ['ST' if sum(heat_amounts.Produced_Amount_ST) != 0 else None,
                       'Electric heating' if sum(heat_amounts.Electric_heating) != 0 else None,
                       'Gasheating' if sum(heat_amounts.Gasheating) != 0 else None,
                       "ASHP" if sum(heat_amounts.ASHP) != 0 else None,
                       "GCHP" if sum(heat_amounts.GCHP) != 0 else None,
                       "DH" if sum(heat_amounts.DH) != 0 else None]
            axs[1].stackplot(heat_amounts.reductionco2,
                             heat_amounts.Produced_Amount_ST,
                             heat_amounts.Electric_heating,
                             heat_amounts.Gasheating,
                             heat_amounts.ASHP,
                             heat_amounts.GCHP,
                             heat_amounts.DH,
                             labels=labels2, edgecolor="black", colors=color)
            #axs[1].plot(heat_amounts.reductionco2,
            #            heat_amounts.Heat_Demand - heat_amounts.Insulation
            #            + heat_amounts.Thermalstorage_losses)
            if sum(heat_amounts.Produced_Amount_ST) != 0:
                labels3 = ["ST_north" if sum(heat_amounts.ST_north) != 0 else None,
                           "ST_north_east" if sum(heat_amounts.ST_north_east) != 0 else None,
                           "ST_east" if sum(heat_amounts.ST_east) != 0 else None,
                           "ST_south_east" if sum(heat_amounts.ST_south_east) != 0 else None,
                           "ST_south" if sum(heat_amounts.ST_south) != 0 else None,
                           "ST_south_west" if sum(heat_amounts.ST_south_west) != 0 else None,
                           "ST_west" if sum(heat_amounts.ST_west) != 0 else None,
                           "ST_north_west" if sum(heat_amounts.ST_north_west) != 0 else None]
                axs[2].stackplot(heat_amounts.reductionco2,
                                 heat_amounts.ST_north,
                                 heat_amounts.ST_north_east,
                                 heat_amounts.ST_east,
                                 heat_amounts.ST_south_east,
                                 heat_amounts.ST_south,
                                 heat_amounts.ST_south_west,
                                 heat_amounts.ST_west,
                                 heat_amounts.ST_north_west,
                                 labels=labels3, edgecolor="black", colors=color)

            axs[0].invert_xaxis()
            axs[0].legend()
            axs[0].set_ylabel("Heat Amount in kWh")
            axs[1].legend()
            axs[1].set_ylabel("Heat Amount in kWh")
            if sum(heat_amounts.Produced_Amount_ST) != 0:
                axs[2].legend(loc="upper left")
                axs[2].set_ylabel("Heat Amount in kWh")
                axs[2].set_xlabel("Emission-reduced Scenario")
            else:
                axs[1].set_xlabel("Emission-reduced Scenario")
            plt.savefig(result_path + "/heat_amounts.jpeg")


def create_energy_amount_plot_elec(dfs, result_path, nodes_data, gui,
                                   tab_control):
    gui.frames.append(ttk.Frame(gui))
    tab_control.add(gui.frames[-1], text="SINK SETTINGS")
    row = 0
    df_sinks = nodes_data["sinks"][(nodes_data["sinks"]["active"] == 1)]
    sink_types = {}
    sink_known = {}
    for num, sink in df_sinks.iterrows():
        if "heat" not in sink["label"] and "elec" not in sink["label"] \
                and "cool" not in sink["label"]:
            sink_types.update(
                {sink["label"]: [tk.BooleanVar(gui.frames[-1]),
                                 tk.BooleanVar(gui.frames[-1]),
                                 tk.BooleanVar(gui.frames[-1])]})
        else:
            sink_known.update(
                {sink["label"]: [True if "elec" in sink["label"] else False,
                                 True if "heat" in sink["label"] else False,
                                 True if "cool" in sink["label"] else False]}
            )

    if len(sink_types) != 0:
        label = tk.Label(gui.frames[-1], text="SINK_LABEL",
                         font='Helvetica 10 bold')
        label.grid(row=row, column=0, sticky="w")
        label = tk.Label(gui.frames[-1], text="elec_sink",
                         font='Helvetica 10 bold')
        label.grid(row=row, column=2, sticky="w")
        label = tk.Label(gui.frames[-1], text="heat_sink",
                         font='Helvetica 10 bold')
        label.grid(row=row, column=3, sticky="w")
        label = tk.Label(gui.frames[-1], text="cool_sink",
                         font='Helvetica 10 bold')
        label.grid(row=row, column=4, sticky="w")
        row += 1
        for sink in sink_types:
            label = tk.Label(gui.frames[-1], text=sink, font='Helvetica 10')
            label.grid(row=row, column=0, sticky="w")
            cb_elec = tk.Checkbutton(gui.frames[-1], variable=sink_types[sink][0])
            cb_heat = tk.Checkbutton(gui.frames[-1], variable=sink_types[sink][1])
            cb_cool = tk.Checkbutton(gui.frames[-1], variable=sink_types[sink][2])
            cb_elec.grid(row=row, column=2, sticky="w")
            cb_heat.grid(row=row, column=3, sticky="w")
            cb_cool.grid(row=row, column=4, sticky="w")
            row += 1
        button = tk.Button(gui.frames[-1], text="Save",
                           command=lambda: save_sinks(sink_types, tab_control,
                                                      gui, dfs, nodes_data,
                                                      sink_known, result_path))
        button.grid(column=5, row=row)
    else:
        save_sinks(sink_types, tab_control, gui, dfs, nodes_data, sink_known,
                   result_path)
