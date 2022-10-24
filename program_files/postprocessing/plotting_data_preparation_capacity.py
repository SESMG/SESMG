import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


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
    from program_files.postprocessing.plotting import get_dataframe_from_nodes_data

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
                "Electric_heating": [],
                "Battery": [],
                "ST": [],
                "Gasheating": [],
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
                "reductionco2": sum(dataframes[key]["constraints/CU"])
                / emissions_100_percent,
            }
        )
        dataframe = dataframes[key].copy()
        dataframe.reset_index(inplace=True, drop=False)
        components_df = get_dataframe_from_nodes_data(nodes_data)
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
            if comp["heat source"] == "Ground":
                value = dataframe.loc[dataframe["ID"].str.startswith(comp["label"])][
                    "capacity/kW"
                ].values
                value = float(value[0]) if value.size > 0 else 0
                capacities_dict["GCHP"].append(value)
            elif comp["heat source"] == "Air":
                value = dataframe.loc[dataframe["ID"].str.startswith(comp["label"])][
                    "capacity/kW"
                ].values
                value = float(value[0]) if value.size > 0 else 0
                capacities_dict["ASHP"].append(value)

        # generic transformer dataframe
        df_gen_transformer = components_df[
            (components_df.isin(["GenericTransformer"])).any(axis=1)
        ]
        for num, comp in df_gen_transformer.iterrows():
            if "elec" in comp["input"] and "central" not in comp["label"]:
                value = dataframe.loc[dataframe["ID"].str.startswith(comp["label"])][
                    "capacity/kW"
                ].values
                value = float(value[0]) if value.size > 0 else 0
                capacities_dict["Electric_heating"].append(value)
            elif "gas" in comp["input"] and "central" not in comp["label"]:
                value = dataframe.loc[dataframe["ID"].str.startswith(comp["label"])][
                    "capacity/kW"
                ].values
                value = float(value[0]) if value.size > 0 else 0
                capacities_dict["Gasheating"].append(value)

        df_storage = components_df[(components_df.isin(["Generic"])).any(axis=1)]
        for num, comp in df_storage.iterrows():
            if "elec" in comp["bus"] and "central" not in comp["label"]:
                value = dataframe.loc[dataframe["ID"].str.startswith(comp["label"])][
                    "capacity/kW"
                ].values
                value = float(value[0]) if value.size > 0 else 0
                capacities_dict["Battery"].append(value)
            elif "heat" in comp["bus"] and "central" not in comp["label"]:
                value = dataframe.loc[dataframe["ID"].str.startswith(comp["label"])][
                    "capacity/kW"
                ].values
                value = float(value[0]) if value.size > 0 else 0
                capacities_dict["Thermalstorage"].append(value)

        capacities_dict["DH"] += list(
            dataframe.loc[dataframe["ID"].str.startswith("dh_heat_house_station")][
                "capacity/kW"
            ].values
        )

        for i in capacities_dict:
            if i != "run" and i != "reductionco2":
                capacities_dict[i] = sum(capacities_dict[i])
        print(capacities_dict)
        series = pd.Series(data=capacities_dict)
        capacities = pd.concat([capacities, pd.DataFrame([series])])
        capacities.set_index("reductionco2", inplace=True, drop=False)
        capacities = capacities.sort_values("run")
        capacities.csv(result_path + "capacities.csv")
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
            "Gasheating": [capacities.Gasheating, axs[2]],
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
        {"1": pd.read_csv(""),
         "0.75": pd.read_csv(""),
         "0.5": pd.read_csv(""),
         "0.25": pd.read_csv(""),
         "0": pd.read_csv("")},
        # scenario file path
        import_scenario(""),
        # result_path
        ""
    )