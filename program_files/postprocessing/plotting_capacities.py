import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


def pv_st_capacity(components_df, pv_st, dataframe, capacities_dict):
    from program_files.postprocessing.plotting import get_pv_st_dir

    if pv_st == "photovoltaic":
        comp_type = "PV"
    else:
        comp_type = "ST"
    df_pv_or_st = components_df[(components_df.isin([str(pv_st)])).any(axis=1)]
    for num, comp in df_pv_or_st.iterrows():
        value_cap = dataframe.loc[dataframe["ID"].str.contains(comp["label"])][
            "capacity/kW"
        ].values
        value_cap = float(value_cap[0]) if value_cap.size > 0 else 0
        capacities_dict[comp_type].append(value_cap)

        capacities_dict = get_pv_st_dir(capacities_dict, value_cap, comp_type, comp)
    return capacities_dict


def create_capacity_plots(dataframes: dict, nodes_data, result_path):
    from program_files.postprocessing.plotting import get_dataframe_from_nodes_data, get_value

    capacities = pd.DataFrame()
    capacities_dict = {}
    emissions_100_percent = sum(dataframes["1"]["constraints/CU"])
    for key in dataframes:
        capacities_dict.update(
            {
                "run": str(key),
                "PV_north": [],
                "PV_north_east": [],
                "PV_east": [],
                "PV_south_east": [],
                "PV_south": [],
                "PV_south_west": [],
                "PV_west": [],
                "PV_north_west": [],
                "PV": [],
                "ASHP": [],
                "GCHP": [],
                "SWHP": [],
                "Electric_heating": [],
                "Battery": [],
                "ST": [],
                "ng_heat": [],
                "bg_heat": [],
                "wc_heat": [],
                "pe_heat": [],
                "DH": [],
                "Thermalstorage": [],
                "ST_north": [],
                "ST_north_east": [],
                "ST_east": [],
                "ST_south_east": [],
                "ST_south": [],
                "ST_south_west": [],
                "ST_west": [],
                "ST_north_west": [],
                "central_GCHP": [],
                "central_ASHP": [],
                "central_SWHP": [],
                "central_ng_chp": [],
                "central_wc_chp": [],
                "central_bg_chp": [],
                "central_pe_chp": [],
                "central_chp": [],
                "central_ng_heat": [],
                "central_bg_heat": [],
                "central_wc_heat": [],
                "central_pe_heat": [],
                "h2_Storage": [],
                "electrolysis": [],
                "reductionco2": (sum(dataframes[key]["constraints/CU"])
                / emissions_100_percent) if key != "0" else
                ((sum(dataframes[key]["variable costs/CU"]) + sum(dataframes[key]["periodical costs/CU"]))
                / emissions_100_percent),
            }
        )
        dataframe = dataframes[key].copy()
        dataframe.reset_index(inplace=True, drop=False)
        components_df = get_dataframe_from_nodes_data(nodes_data)
        # get central heat buses
        df_central_heat = components_df[components_df["district heating conn."]
                                        == "dh-system"]["label"].values
        # PV-System
        capacities_dict = pv_st_capacity(
            components_df.copy(), "photovoltaic", dataframe, capacities_dict
        )
        # ST-System
        capacities_dict = pv_st_capacity(
            components_df, "solar_thermal_flat_plate", dataframe, capacities_dict
        )

        df_hp = components_df[
            (components_df.isin(["CompressionHeatTransformer"])).any(axis=1)
        ]
        df_hp = pd.concat(
            [df_hp, (components_df.isin(["AbsorptionHeatTransformer"])).any(axis=1)]
        )
        for num, comp in df_hp.iterrows():
            value = get_value(comp["label"], "capacity/kW", dataframe)
            if comp["output"] not in df_central_heat:
                if comp["heat source"] == "Ground":
                    capacities_dict["GCHP"].append(value)
                elif comp["heat source"] == "Air":
                    capacities_dict["ASHP"].append(value)
                elif comp["heat source"] == "Water":
                    capacities_dict["SWHP"].append(value)
            else:
                if comp["heat source"] == "Ground":
                    capacities_dict["central_GCHP"].append(value)
                elif comp["heat source"] == "Air":
                    capacities_dict["central_ASHP"].append(value)
                elif comp["heat source"] == "Water":
                    capacities_dict["central_SWHP"].append(value)

        # generic transformer dataframe
        df_gen_transformer = components_df[
            (components_df.isin(["GenericTransformer"])).any(axis=1)
        ]
        # collecting all decentral generic transformers
        for num, comp in df_gen_transformer.iterrows():
            # TODO used label for differentiation of heating system
            # TODO fuels
            if not (comp["output"] in df_central_heat
                    or comp["output2"] in df_central_heat):
                if "electric" in comp["input"]:
                    value = get_value(comp["label"], "capacity/kW", dataframe)
                    capacities_dict["Electric_heating"].append(value)
                elif "gas" in comp["input"]:
                    value = get_value(comp["label"], "capacity/kW", dataframe)
                    capacities_dict["ng_heat"].append(value)
                elif "bg" in comp["input"]:
                    value = get_value(comp["label"], "capacity/kW", dataframe)
                    capacities_dict["bg_heat"].append(value)
                elif "wc" in comp["input"]:
                    value = get_value(comp["label"], "capacity/kW", dataframe)
                    capacities_dict["wc_heat"].append(value)
                elif "pe" in comp["input"]:
                    value = get_value(comp["label"], "capacity/kW", dataframe)
                    capacities_dict["pe_heat"].append(value)

        df_storage = components_df[(components_df.isin(["Generic"])).any(axis=1)]
        for num, comp in df_storage.iterrows():
            if "elec" in comp["bus"] and "central" not in comp["label"]:
                value = get_value(comp["label"], "capacity/kW", dataframe)
                capacities_dict["Battery"].append(value)
            elif "heat" in comp["bus"] and comp["bus"] not in df_central_heat:
                value = get_value(comp["label"], "capacity/kW", dataframe)
                capacities_dict["Thermalstorage"].append(value)

        capacities_dict["DH"] += list(
            dataframe.loc[dataframe["ID"].str.startswith("dh_heat_house_station")][
                "capacity/kW"
            ].values
        )
        
        df_central_heat = components_df[components_df["district heating conn."]
                                        == "dh-system"]
        for num, bus in df_central_heat.iterrows():
            for i in ["output", "output2"]:
                for num2, comp in components_df[components_df[i]
                                                == bus["label"]].iterrows():
                    if comp["transformer type"] == "GenericTransformer":
                        if comp["output2"] == "None":
                            capacity = get_value(comp["label"], "capacity/kW", dataframe)
                            if "wc" in comp["label"]:
                                capacities_dict["central_wc_heat"].append(capacity)
                            # TODO necessary since natural gas' abbreviation
                            # TODO is ng and heating does contain ng also
                            elif comp["label"].count("ng") >= 2:
                                capacities_dict["central_ng_heat"].append(capacity)
                            elif "bg" in comp["label"]:
                                capacities_dict["central_bg_heat"].append(capacity)
                            elif "pe" in comp["label"]:
                                capacities_dict["central_pe_heat"].append(capacity)
                            else:
                                capacities_dict["central_heat"].append(capacity)
                        else:
                            capacity = get_value(comp["label"], "capacity/kW",
                                                 dataframe)
                            if "wc" in comp["label"]:
                                capacities_dict["central_wc_chp"].append(
                                    capacity)
                            elif "ng" in comp["label"]:
                                capacities_dict["central_ng_chp"].append(
                                    capacity)
                            elif "bg" in comp["label"]:
                                capacities_dict["central_bg_chp"].append(
                                    capacity)
                            elif "pe" in comp["label"]:
                                capacities_dict["central_pe_chp"].append(
                                    capacity)
                            else:
                                capacities_dict["central_chp"].append(
                                    capacity)
                                
        df_h2 = components_df[components_df["label"].str.contains("h2")]
            
        for num, comp in df_h2.iterrows():
            if comp["storage type"] == "Generic":
                value = get_value(comp["label"], "capacity/kW", dataframe)
                capacities_dict["h2_Storage"].append(value)
            else:
                df_comps = components_df[components_df["output"]
                                         == comp["label"]]
                for num2, comp2 in df_comps.iterrows():
                    if comp2["transformer type"] == "GenericTransformer":
                        value = get_value(comp2["label"], "capacity/kW",
                                          dataframe)
                        capacities_dict["electrolysis"].append(value)
                    
        for i in capacities_dict:
            if i != "run" and i != "reductionco2":
                capacities_dict[i] = sum(capacities_dict[i])
        print(capacities_dict)
        series = pd.Series(data=capacities_dict)
        capacities = pd.concat([capacities, pd.DataFrame([series])])
        capacities.set_index("reductionco2", inplace=True, drop=False)
        capacities = capacities.sort_values("run")
        capacities.to_csv(result_path + "/capacities.csv")
        plt.clf()
        fig, axs = plt.subplots(3, sharex="all")
        fig.set_size_inches(18.5, 15.5)
        capacities.set_index("run", inplace=True, drop=False)
        plot_dict = {
            "PV_north": [capacities.PV_north, axs[0]],
            "PV_north_east": [capacities.PV_north_east, axs[0]],
            "PV_east": [capacities.PV_east, axs[0]],
            "PV_south_east": [capacities.PV_south_east, axs[0]],
            "PV_south": [capacities.PV_south, axs[0]],
            "PV_south_west": [capacities.PV_south_west, axs[0]],
            "PV_west": [capacities.PV_west, axs[0]],
            "PV_north_west": [capacities.PV_north_west, axs[0]],
            "ST_north": [capacities.ST_north, axs[1]],
            "ST_north_east": [capacities.ST_north_east, axs[1]],
            "ST_east": [capacities.ST_east, axs[1]],
            "ST_south_east": [capacities.ST_south_east, axs[1]],
            "ST_south": [capacities.ST_south, axs[1]],
            "ST_south_west": [capacities.ST_south_west, axs[1]],
            "ST_west": [capacities.ST_west, axs[1]],
            "ST_north_west": [capacities.ST_north_west, axs[1]],
            "PV": [capacities.PV, axs[2]],
            "ASHP": [capacities.ASHP, axs[2]],
            "GCHP": [capacities.GCHP, axs[2]],
            "Electric_heating": [capacities.Electric_heating, axs[2]],
            "Battery": [capacities.Battery, axs[2]],
            "ST": [capacities.ST, axs[2]],
            "Gasheating": [capacities.ng_heat, axs[2]],
            "DH": [capacities.DH, axs[2]],
            "Thermalstorage": [capacities.Thermalstorage, axs[2]],
        }
        for plot in plot_dict:
            sns.lineplot(
                x=capacities.reductionco2,
                y=plot_dict[plot][0],
                marker="o",
                palette="Spectral",
                label=plot,
                ax=plot_dict[plot][1],
            )

        axs[0].invert_xaxis()
        axs[0].set_xlabel("Emission-reduced Scenario")
        axs[0].set_ylabel("installed capacity in kW")
        axs[1].set_ylabel("installed capacity in kW")
        axs[2].set_ylabel("installed capacity in kW")
        axs[2].legend(loc="upper right")
        axs[2].set_ylim([0, 300])
        plt.savefig(result_path + "/capacities.jpeg")


if __name__ == "__main__":
    from program_files.preprocessing.create_energy_system import import_scenario
    create_capacity_plots(
            {"1": pd.read_csv("<path_to_csv_file>"),
             "0.75": pd.read_csv(),
             "0.5": pd.read_csv(),
             "0.35": pd.read_csv(),
             "0.25": pd.read_csv(),
             "0.15": pd.read_csv(),
             "0": pd.read_csv()},
            # scenario file path
            import_scenario(),
            # result_path
            str(),
    )
