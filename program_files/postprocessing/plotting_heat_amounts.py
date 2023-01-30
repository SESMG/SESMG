import pandas
import matplotlib.pyplot as plt
import os

def st_heat_amount(components_df, pv_st, dataframe, amounts_dict):
    from program_files.postprocessing.plotting import get_pv_st_dir, get_value

    df_pv_or_st = components_df[(components_df.isin([str(pv_st)])).any(axis=1)]
    for num, comp in df_pv_or_st.iterrows():
        value_am = get_value(comp["label"], "output 1/kWh", dataframe)
        amounts_dict["ST"].append(value_am)
        # TODO wie stellen wir fest ob -180 - 180 oder 0 - 360
        #  genutzt wurde
        amounts_dict = get_pv_st_dir(amounts_dict, value_am, "ST", comp)
    return amounts_dict


def create_heat_amount_plots(dataframes: dict, nodes_data: pandas.DataFrame,
                             result_path: str, sink_known: dict):
    """
    main function of the algorithm to plot an heat amount plot after
    running an pareto optimization
    
    :param dataframes: dictionary which holds the results of the pareto\
        optimization - structure {str(share of emission reduction \
        between 0 and 1): pandas.DataFrame(components.csv)}
    :type dataframes: dict
    :param nodes_data: DataFrame containing all components defined \
        within the input scenario file
    :type nodes_data: pandas.DataFrame
    :param result_path: str which defines the folder where the \
        elec_amount plot will be saved
    :type result_path: str
    :param sink_known: dictionary which defines the type of the energy \
        system's sinks structure {sink_label: [bool(elec), bool(heat), \
        bool(cooling)]}
    """
    from program_files.postprocessing.plotting import (
        get_dataframe_from_nodes_data,
        get_value,
        dict_to_dataframe
    )
    # data frame to plot the amounts using matplotlib
    heat_amounts = pandas.DataFrame()
    heat_amounts_dict = {}
    # get the emissions of the monetary cheapest scenario ("1")
    emissions_100_percent = sum(dataframes["1"]["constraints/CU"])
    # iterate threw the pareto points
    for key in dataframes:
        # define all energy system technologies to be searched within
        # the results file components.csv
        heat_amounts_dict.update(
            {
                "run": str(key),
                "ST": [],
                "Electric_heating": [],
                "Gasheating": [],
                "HeatPump": [],
                "DH": [],
                "Heat_Demand": [],
                "Thermalstorage_losses": [],
                "Thermalstorage_output": [],
                "ST_north": [],
                "ST_north_east": [],
                "ST_east": [],
                "ST_south_east": [],
                "ST_south": [],
                "ST_south_west": [],
                "ST_west": [],
                "ST_north_west": [],
                "GCHP": [],
                "ASHP": [],
                "Insulation": [],
                "fuelcell": [],
                "central_wc_heat": [],
                "central_ng_heat": [],
                "central_bg_heat": [],
                "central_pe_heat": [],
                "central_heat": [],
                "central_SWHP": [],
                "central_GCHP": [],
                "central_wc_heat_chp": [],
                "central_ng_heat_chp": [],
                "central_bg_heat_chp": [],
                "central_pe_heat_chp": [],
                "central_heat_chp": [],
                "reductionco2": (
                    sum(dataframes[key]["constraints/CU"]) / emissions_100_percent
                )
                if key != "0"
                else (
                    (
                        sum(dataframes[key]["periodical costs/CU"])
                        + sum(dataframes[key]["variable costs/CU"])
                    )
                    / emissions_100_percent
                ),
            }
        )
        dataframe = dataframes[key].copy()
        dataframe.reset_index(inplace=True, drop=False)
        components_df = get_dataframe_from_nodes_data(nodes_data)
        # TODO concentrated solar power
        # get the ST-Systems' amounts using st_heat_amount method above
        heat_amounts_dict = st_heat_amount(
            components_df, "solar_thermal_flat_plate", dataframe,
            heat_amounts_dict
        )
        
        # get the energy system's heat pumps from nodes data
        df_hp = components_df[
            (components_df.isin(["CompressionHeatTransformer"])).any(axis=1)
        ]
        df_hp = pandas.concat(
            [df_hp,
             (components_df.isin(["AbsorptionHeatTransformer"])).any(axis=1)]
        )
        # append the heat production of the heat pumps on the heat
        # amounts dict
        for num, comp in df_hp.iterrows():
            if comp["heat source"] == "Ground":
                heat_amounts_dict["GCHP"].append(
                    get_value(comp["label"], "output 1/kWh", dataframe)
                )
            elif comp["heat source"] == "Air":
                # ashp heat output
                heat_amounts_dict["ASHP"].append(
                    get_value(comp["label"], "output 1/kWh", dataframe)
                )
                
        # get the energy system's sinks from nodes data
        df_sinks = components_df[(components_df["annual demand"].notna())]
        df_sinks = pandas.concat(
            [df_sinks, components_df[(components_df["nominal value"].notna())]]
        ).drop_duplicates()
        # collect the amount of heat demand
        for num, sink in df_sinks.iterrows():
            if sink_known[sink["label"]][1]:
                heat_amounts_dict["Heat_Demand"].append(
                    get_value(sink["label"], "input 1/kWh", dataframe)
                )
        # get the energy system's generic storages from nodes data
        df_storage = components_df[(components_df.isin(["Generic"])).any(axis=1)]
        for num, storage in df_storage.iterrows():
            # append the heat losses and output of generic thermal
            # storages on the heat amounts dict
            if "heat" in storage["bus"] and "central" not in storage["bus"]:
                value = get_value(storage["label"], "output 1/kWh", dataframe)
                heat_amounts_dict["Thermalstorage_output"].append(value)
                input_val = get_value(storage["label"], "input 1/kWh", dataframe)
                heat_amounts_dict["Thermalstorage_losses"].append(input_val - value)
        
        # get the energy system's generic transformers from nodes data
        df_gen_transformer = components_df[
            (components_df.isin(["GenericTransformer"])).any(axis=1)
        ]
        for num, transformer in df_gen_transformer.iterrows():
            # collecting GenericTransformer with electric input
            # (Electric Heating)
            if (
                ("heat" in transformer["output"] or "heat" in transformer["output2"])
                and "central" not in transformer["input"]
                and "elec" in transformer["input"]
            ):
                heat_amounts_dict["Electric_heating"].append(
                    get_value(transformer["label"], "output 1/kWh", dataframe)
                )
            elif (
                ("heat" in transformer["output"] or "heat" in transformer["output2"])
                and "central" not in transformer["input"]
                and "gas" in transformer["input"]
            ):
                heat_amounts_dict["Gasheating"].append(
                    get_value(transformer["label"], "output 1/kWh", dataframe)
                )
        # get the energy system's insulations from nodes data
        df_insulation = components_df[components_df["U-value new"].notna()]
        for num, insulation in df_insulation.iterrows():
            cap_sink = get_value(insulation["sink"], "capacity/kW", dataframe)
            cap_insulation = get_value(insulation["label"] + "-insulation", "capacity/kW", dataframe)
            value_sink = get_value(insulation["sink"], "input 1/kWh", dataframe)
            # append the heat savings of the insulations on the heat
            # amounts dict
            if cap_insulation != 0 and cap_sink != 0:
                heat_amounts_dict["Insulation"].append(
                    ((cap_insulation * value_sink) / cap_sink)
                )
        # append the transported heat amounts of the district heating
        # network to the heat amounts dict
        heat_amounts_dict["DH"] += list(
            dataframe.loc[dataframe["ID"].str.startswith("dh_heat_house_station")][
                "output 1/kWh"
            ].values
        )
        df_central_heat = components_df[components_df["district heating conn."]
                                        == "dh-system"]
        df_comp_heat = pandas.DataFrame()
        for i in ["output", "output2"]:
            for num, bus in df_central_heat.iterrows():
               df_comp_heat = pandas.concat(
                    [df_comp_heat,
                     components_df.loc[components_df[i] == bus["label"]]])
            for num, comp in df_comp_heat.iterrows():
                if str(components_df.loc[components_df["label"] == comp["label"]]
                       ["transformer type"].values[0]) == "GenericTransformer":
                    # TODO since we do not differentiate the chp's fuel we
                    # TODO have to use the label
                    output = get_value(comp["label"],
                                       "output 1/kWh" if i == "output"
                                       else "output 2/kWh",
                                       dataframe)
                    if comp["output2"] != "None":
                        if "wc" in comp["label"]:
                            heat_amounts_dict["central_wc_heat_chp"].append(output)
                        elif "ng" in comp["label"]:
                            heat_amounts_dict["central_ng_heat_chp"].append(output)
                        elif "bg" in comp["label"]:
                            heat_amounts_dict["central_bg_heat_chp"].append(output)
                        elif "pe" in comp["label"]:
                            heat_amounts_dict["central_pe_heat_chp"].append(output)
                        else:
                            heat_amounts_dict["fuelcell"].append(output)
                    else:
                        if "wc" in comp["label"]:
                            heat_amounts_dict["central_wc_heat"].append(output)
                        # TODO necessary since natural gas' abbreviation
                        # TODO is ng and heating does contain ng also
                        elif comp["label"].count("ng") >= 2:
                            heat_amounts_dict["central_ng_heat"].append(output)
                        elif "bg" in comp["label"]:
                            heat_amounts_dict["central_bg_heat"].append(output)
                        elif "pe" in comp["label"]:
                            heat_amounts_dict["central_pe_heat"].append(output)
                        else:
                            heat_amounts_dict["central_heat"].append(output)
                if str(components_df.loc[
                           components_df["label"] == comp["label"]]
                       ["transformer type"].values[0]) == "CompressionHeatTransformer":
                    output = get_value(comp["label"],
                                       "output 1/kWh",
                                       dataframe)
                    if comp["heat source"] == "Water" and i == "output":
                        heat_amounts_dict["central_SWHP"].append(output)
                    elif comp["heat source"] == "Ground" and i == "output":
                        heat_amounts_dict["central_GCHP"].append(output)
                      
        heat_amounts = dict_to_dataframe(heat_amounts_dict, heat_amounts)
    heat_amounts.to_csv(result_path + "/heat_amounts.csv")
    # HEAT PLOT
    fig, axs = plt.subplots(3, sharex="all")
    fig.set_size_inches(18.5, 15.5)
    plot_dict = {
        axs[0]: {
            "SLP_DEMAND": heat_amounts.Heat_Demand,
            "Thermalstorage losses": heat_amounts.Thermalstorage_losses,
            "Insulation": heat_amounts.Insulation,
        },
        axs[1]: {
            "Electric Heating": heat_amounts.Electric_heating,
            "Gasheating": heat_amounts.Gasheating,
            "ASHP": heat_amounts.ASHP,
            "GCHP": heat_amounts.GCHP,
            "DH": heat_amounts.DH,
            "ST": heat_amounts.ST,
        },
        axs[2]: {
            "ST_north": heat_amounts.ST_north,
            "ST_north_east": heat_amounts.ST_north_east,
            "ST_east": heat_amounts.ST_east,
            "ST_south_east": heat_amounts.ST_south_east,
            "ST_south": heat_amounts.ST_south,
            "ST_south_west": heat_amounts.ST_south_west,
            "ST_west": heat_amounts.ST_west,
            "ST_north_west": heat_amounts.ST_north_west,
        },
    }
    for plot in plot_dict:
        plot.stackplot(
            heat_amounts.reductionco2,
            plot_dict.get(plot).values(),
            labels=list(plot_dict.get(plot).keys()),
        )
    axs[0].invert_xaxis()
    axs[0].legend()
    axs[0].set_ylabel("Heat Amount in kWh")
    axs[1].legend()
    axs[1].set_ylabel("Heat Amount in kWh")
    axs[2].legend(loc="upper left")
    axs[2].set_ylabel("Heat Amount in kWh")
    axs[2].set_xlabel("Emission-reduced Scenario")
    plt.savefig(result_path + "/heat_amounts.jpeg")


if __name__ == "__main__":
    from program_files.preprocessing.create_energy_system import \
        import_scenario
    import pandas as pd

    create_heat_amount_plots(
            {"1": pd.read_csv("<path_to_csv_file>"),
             "0.75": pd.read_csv(),
             "0.5": pd.read_csv(),
             "0.35": pd.read_csv(),
             "0.25": pd.read_csv(),
             "0.15": pd.read_csv(),
             "0": pd.read_csv()},
            # import scenario file
            import_scenario(),
            # result_path
            str(),
            # sink types dict {label: [bool(elec), bool(heat), bool(cooling)]}
            {
                "sink_id": ["bool(elec)", "bool(heat)", "bool(cooling)"]
            }
    )
