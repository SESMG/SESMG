import pandas as pd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def pv_elec_amount(components_df, pv_st, dataframe, amounts_dict):
    from program_files.postprocessing.plotting import get_pv_st_dir, get_value
    pv_buses = []
    df_pv_or_st = components_df[(components_df.isin([str(pv_st)])).any(axis=1)]
    for num, comp in df_pv_or_st.iterrows():
        value_am = get_value(comp["label"], "output 1/kWh", dataframe)
        amounts_dict["PV"].append(value_am)
        # TODO wie stellen wir fest ob -180 - 180 oder 0 - 360
        #  genutzt wurde
        amounts_dict = get_pv_st_dir(amounts_dict, value_am,  "PV", comp)
        pv_buses.append(comp["output"])
    return amounts_dict, pv_buses


def create_elec_amount_plots(dataframes: dict, nodes_data, result_path,
                             sink_known):
    from program_files.postprocessing.plotting import \
        get_dataframe_from_nodes_data, get_value
    elec_amounts = pd.DataFrame()
    elec_amounts_dict = {}
    emissions_100_percent = sum(dataframes["1"]["constraints/CU"])
    for key in dataframes:
        elec_amounts_dict.update(
            {"run": str(key),
             "PV_north": [],
             "PV_north_east": [],
             "PV_east": [],
             "PV_south_east": [],
             "PV_south": [],
             "PV_south_west": [],
             "PV_west": [],
             "PV_north_west": [],
             "PV": [],
             "PV_excess": [],
             "PV_to_Central": [],
             "Electricity_Demand": [],
             "ASHP": [], "GCHP": [],
             "Import_system_internal": [],
             "grid_import": [],
             "Electric_heating": [],
             "Battery_losses": [],
             "ST_elec": [],
             "Battery_output": [],
             "central_elec_production": [],
             "reductionco2":
                 (sum(dataframes[key]["constraints/CU"])
                  / emissions_100_percent) if key != "0" else
                 ((sum(dataframes[key]["periodical costs/CU"])
                  + sum(dataframes[key]["variable costs/CU"]))
                  / emissions_100_percent)})
        dataframe = dataframes[key].copy()
        dataframe.reset_index(inplace=True, drop=False)
        components_df = get_dataframe_from_nodes_data(nodes_data)
        # PV-System
        elec_amounts_dict, pv_buses = pv_elec_amount(
                components_df.copy(), "photovoltaic",
                dataframe, elec_amounts_dict)
        
        for bus in pv_buses:
            elec_amounts_dict["PV_excess"].append(get_value(
                    str(bus) + "_excess", "input 1/kWh", dataframe))

        df_st = components_df[(components_df.isin(
                [str("solar_thermal_flat_plate")])).any(axis=1)]
        for num, comp in df_st.iterrows():
            elec_amounts_dict["ST_elec"].append(
                    get_value(comp["label"], "input 1/kWh", dataframe))

        df_hp = components_df[(components_df.isin([
            "CompressionHeatTransformer"])).any(
                axis=1)]
        df_hp = pd.concat([df_hp, (components_df.isin([
            "AbsorptionHeatTransformer"])).any(axis=1)])
        for num, comp in df_hp.iterrows():
            if comp["heat source"] == "Ground":
                elec_amounts_dict["GCHP"].append(
                        get_value(comp["label"], "input 1/kWh", dataframe))
            elif comp["heat source"] == "Air":
                elec_amounts_dict["ASHP"].append(
                        get_value(comp["label"], "input 1/kWh", dataframe))

        # sink dataframe
        df_sinks = components_df[
            (components_df['annual demand'].notna())]
        df_sinks = pd.concat(
                [df_sinks, components_df[
                    (components_df[
                         'nominal value'].notna())]]).drop_duplicates()
        # collect the amount of electricity demand
        for num, sink in df_sinks.iterrows():
            if sink_known[sink["label"]][0]:
                elec_amounts_dict["Electricity_Demand"].append(
                        get_value(sink["label"], "input 1/kWh", dataframe))
                
        # generic transformer dataframe
        df_gen_transformer = components_df[(components_df.isin([
            'GenericTransformer'])).any(axis=1)]
        for num, comp in df_gen_transformer.iterrows():
            if "elec" in comp["input"] and "central" not in comp["label"]:
                elec_amounts_dict["Electric_heating"].append(
                        get_value(comp["label"], "input 1/kWh", dataframe))
        
        df_storage = components_df[(components_df.isin([
            'Generic'])).any(axis=1)]
        for num, comp in df_storage.iterrows():
            if "elec" in comp["bus"] and "central" not in comp["label"]:
                value = get_value(comp["label"], "output 1/kWh", dataframe)
                elec_amounts_dict["Battery_output"].append(value)
                input_val = get_value(comp["label"], "input 1/kWh", dataframe)
                elec_amounts_dict["Battery_losses"].append(input_val - value)
                
        df_buses = components_df[(components_df["shortage"] == 1)]
        for num, comp in df_buses.iterrows():
            if "elec" in comp["label"]:
                elec_amounts_dict["grid_import"].append(
                        get_value(comp["label"] + "_shortage", "output 1/kWh",
                                  dataframe))
        df_links = components_df[(components_df['bus1'].notna())]
        for num, link in df_links.iterrows():
            # pvbus -> local electricity market
            if link["bus1"] in pv_buses and "central" in link["bus2"]:
                elec_amounts_dict["PV_to_Central"].append(
                        get_value(link["label"], "output 1/kWh", dataframe))
        
        for i in elec_amounts_dict:
            if i != "run" and i != "reductionco2":
                elec_amounts_dict[i] = sum(elec_amounts_dict[i])
        series = pd.Series(data=elec_amounts_dict)
        elec_amounts = pd.concat([elec_amounts, pd.DataFrame([series])])
        elec_amounts.set_index("reductionco2", inplace=True, drop=False)
        elec_amounts = elec_amounts.sort_values("run")

    plt.clf()
    fig, axs = plt.subplots(5, sharex="all")
    fig.set_size_inches(18.5, 15.5)
    elec_amounts.set_index("run", inplace=True, drop=False)
    plot_dict = {
        axs[0]: {
            "SLP_DEMAND": elec_amounts.Electricity_Demand,
            "PV EXCESS": elec_amounts.PV_excess,
            "PV_to_Central": elec_amounts.PV_to_Central,
            "Battery losses": elec_amounts.Battery_losses},
        axs[1]: {
            'PV': elec_amounts.PV - elec_amounts.PV_to_Central,
            'PV to local market': elec_amounts.PV_to_Central,
            'GRID': elec_amounts.grid_import},
        axs[2]: {
            # TODO
            "Electric_heating": elec_amounts.Electric_heating,
            "Heatpump_elec": elec_amounts.GCHP + elec_amounts.ASHP,
            "ST_elec": elec_amounts.ST_elec},
        axs[3]: {
            "PV_north": elec_amounts.PV_north,
            "PV_north_east": elec_amounts.PV_north_east,
            "PV_east": elec_amounts.PV_east,
            "PV_south_east": elec_amounts.PV_south_east,
            "PV_south": elec_amounts.PV_south,
            "PV_south_west": elec_amounts.PV_south_west,
            "PV_west": elec_amounts.PV_west,
            "PV_north_west": elec_amounts.PV_north_west},
        axs[4]: {
            "central_elec_production":
            elec_amounts.central_elec_production}}
    for plot in plot_dict:
        plot.stackplot(elec_amounts.reductionco2,
                       plot_dict.get(plot).values(),
                       labels=list(plot_dict.get(plot).keys()))

    axs[0].legend()
    axs[0].set_ylabel("Electricity Amount in kWh")
    axs[1].legend()
    axs[1].set_ylabel("Electricity Amount in kWh")
    axs[2].legend(loc="upper left")
    axs[2].set_ylabel("Electricity Amount in kWh")
    axs[3].legend(loc="upper left")
    axs[3].set_ylabel("Electricity Amount in kWh")
    axs[4].invert_xaxis()
    axs[4].legend(loc="upper left")
    axs[4].set_ylabel("Electricity Amount in kWh")
    plt.savefig(result_path + "/elec_amounts.svg")
