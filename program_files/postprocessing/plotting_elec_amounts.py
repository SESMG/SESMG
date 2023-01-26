import pandas
import matplotlib.pyplot as plt
import os

def pv_elec_amount(components_df: pandas.DataFrame, pv_st: str,
                   dataframe: pandas.DataFrame, amounts_dict: dict):
    """
    method which is used to get the pv system earnings in total and
    azimuth specific as well as the output buses for later excess
    calculations
    
    :param components_df: dataframe containing the nodes data's entries
    :type components_df: pandas.DataFrame
    :param pv_st: str defining rather the algorithm searches for \
        photovoltaic or solar thermal entries
    :param dataframe: dataframe containing the considered pareto \
        point's result (components.csv)
    :type dataframe: pandas.DataFrame
    :param amounts_dict: dictionary holding the collected electricity \
        amounts for all pareto points
    :type amounts_dict: dict
    
    :return: TODO
    
    """
    from program_files.postprocessing.plotting import get_pv_st_dir, get_value

    pv_buses = []
    # get all photovoltaic entries from nodes data sources
    df_pv_or_st = components_df[(components_df.isin([str(pv_st)])).any(axis=1)]
    # get the components outputs and append them on the total pv
    # earnings as well as the azimuth specific dict entry (using
    # get_pv_st_dir) which is located in the plotting main file
    for num, comp in df_pv_or_st.iterrows():
        value_am = get_value(comp["label"], "output 1/kWh", dataframe)
        amounts_dict["PV"].append(value_am)
        # TODO wie stellen wir fest ob -180 - 180 oder 0 - 360
        #  genutzt wurde
        amounts_dict = get_pv_st_dir(amounts_dict, value_am, "PV", comp)
        # collect all output buses of the energy system's pv system to
        # calculate the pv excess
        if comp["output"] not in pv_buses:
            pv_buses.append(comp["output"])
    return amounts_dict, pv_buses


def create_elec_amount_plots(
        dataframes: dict, nodes_data: pandas.DataFrame, result_path: str,
        sink_known: dict) -> None:
    """
    main function of the algorithm to plot an electricity amount plot
    after running an pareto optimization
    
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
    elec_amounts = pandas.DataFrame()
    elec_amounts_dict = {}
    # get the emissions of the monetary cheapest scenario ("1")
    emissions_100_percent = sum(dataframes["1"]["constraints/CU"])
    # iterate threw the pareto points
    for key in dataframes:
        # define all energy system technologies to be searched within
        # the results file components.csv
        if key != "0":
            reductionco2 = (
                sum(dataframes[key]["constraints/CU"]) / emissions_100_percent
                )
        else:
            reductionco2 = ((
                sum(dataframes[key]["periodical costs/CU"])
                + sum(dataframes[key]["variable costs/CU"])
                )
                / emissions_100_percent
                )
        elec_amounts_dict.update(
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
                "PV_excess": [],
                "PV_to_Central": [],
                "Electricity_Demand": [],
                "ASHP": [],
                "GCHP": [],
                "SWHP": [],
                "Import_system_internal": [],
                "grid_import": [],
                "Electric_heating": [],
                "Battery_losses": [],
                "ST_elec": [],
                "Battery_output": [],
                "fuelcell": [],
                "central_wc_elec": [],
                "central_ng_elec": [],
                "central_bg_elec": [],
                "central_pe_elec": [],
                "central_wc_elec_excess": [],
                "central_ng_elec_excess": [],
                "central_bg_elec_excess": [],
                "central_pe_elec_excess": [],
                "central_elec": [],
                "central_elec_excess": [],
                "central_consumption": [],
                "reductionco2": reductionco2
            }
        )
        dataframe = dataframes[key].copy()
        dataframe.reset_index(inplace=True, drop=False)
        components_df = get_dataframe_from_nodes_data(nodes_data)

        # get the energy systems SLP electricity demand as well as the
        # input buses of the sinks
        df_sinks = components_df[(components_df["annual demand"].notna())]
        df_sinks = pandas.concat(
                [df_sinks,
                 components_df[(components_df["nominal value"].notna())]]
        ).drop_duplicates()
        buses = []
        for sink in sink_known:
            if sink_known[sink][0] and sink in df_sinks["label"].values:
                buses.append(df_sinks.loc[df_sinks["label"] == sink]["input"].values[0])
                elec_amounts_dict["Electricity_Demand"].append(
                        get_value(sink, "input 1/kWh", dataframe)
                )

        # get the energy system's links
        df_links = components_df[(components_df["bus1"].notna())]
        # Based on the buses representing the input of the sinks,
        # further buses are searched via the links
        link_buses = []
        for num, link in df_links.iterrows():
            if link["bus2"] in buses:
                link_buses.append(link["bus1"])
                
        # search for duplicate buses in building link connections
        seen = set()
        central_buses = [x for x in link_buses if x in seen or seen.add(x)]
        central_buses = list(dict.fromkeys(central_buses))
        seen = set()
        decentral_buses = [x for x in link_buses if x not in seen
                           and not seen.add(x)]
        decentral_buses = list(set(list(dict.fromkeys(decentral_buses)))
                               - set(central_buses))
        # get all components that are connected directly to the central
        # elec bus
        series_central_elec = pandas.Series()
        for i in range(0, len(central_buses)):
            series_central_elec = pandas.concat([series_central_elec,
                components_df.loc[components_df["output"] == central_buses[i]]
                ["label"]])
            series_central_elec = pandas.concat([series_central_elec,
                components_df.loc[components_df["output2"] == central_buses[i]]
                ["label"]])
        for i in series_central_elec.values:
            output = get_value(i, "output 1/kWh", dataframe)
            elec_amounts_dict["fuelcell"].append(output)

        # Based on the central buses, further buses are searched via the links
        link_buses = []
        for num, link in df_links.iterrows():
            if link["bus2"] in central_buses \
                    and link["bus1"] not in decentral_buses:
                link_buses.append(link["bus1"])
        for j in ["output", "output2"]:
            series_central_elec = pandas.Series()
            for i in range(0, len(link_buses)):
                series_central_elec = pandas.concat(
                    [series_central_elec, components_df.loc[
                        components_df[j] == link_buses[i]]["label"]])

            for i in series_central_elec.values:
                if str(components_df.loc[components_df["label"] == i]
                       ["transformer type"].values[0]) == "GenericTransformer":
                    # TODO since we do not differentiate the chp's fuel we
                    # TODO have to use the label
                    output = get_value(i,
                                       "output 1/kWh" if j == "output"
                                       else "output 2/kWh",
                                       dataframe)
                    if "wc" in i:
                        elec_amounts_dict["central_wc_elec"].append(output)
                        elec_amounts_dict["central_wc_elec_excess"].append(
                                get_value(components_df.loc[
                                              components_df["label"] == i]
                                          [j].values[0] + "_excess",
                                          "input 1/kWh",
                                          dataframe)
                        )
                    elif "ng" in i:
                        elec_amounts_dict["central_ng_elec"].append(output)
                        elec_amounts_dict["central_ng_elec_excess"].append(
                                get_value(components_df.loc[
                                              components_df["label"] == i]
                                          [j].values[0] + "_excess",
                                          "input 1/kWh",
                                          dataframe)
                        )
                    elif "bg" in i:
                        elec_amounts_dict["central_bg_elec"].append(output)
                        elec_amounts_dict["central_bg_elec_excess"].append(
                                get_value(components_df.loc[
                                              components_df["label"] == i]
                                          [j].values[0] + "_excess",
                                          "input 1/kWh",
                                          dataframe)
                        )
                    elif "pe" in i:
                        elec_amounts_dict["central_pe_elec"].append(output)
                        elec_amounts_dict["central_pe_elec_excess"].append(
                                get_value(components_df.loc[
                                              components_df["label"] == i]
                                          [j].values[0] + "_excess",
                                          "input 1/kWh",
                                          dataframe)
                        )
                    else:
                        elec_amounts_dict["central_elec"].append(output)
                        elec_amounts_dict["central_elec_excess"].append(
                                get_value(components_df.loc[
                                              components_df["label"] == i]
                                          [j].values[0] + "_excess",
                                          "input 1/kWh",
                                          dataframe)
                        )
                # search for central timeseries source
                if str(components_df.loc[components_df["label"] == i]
                       ["technology"].values[0]) == "timeseries":
                    output = get_value(i, "output 1/kWh", dataframe)
                    elec_amounts_dict["central_elec"].append(output)
                    elec_amounts_dict["central_elec_excess"].append(
                        get_value(components_df.loc[
                                      components_df["label"] == i]
                                  ["output"].values[0] + "_excess",
                                  "input 1/kWh",
                                  dataframe)
                    )
        for i in range(0, len(central_buses)):
            series_central_elec = pandas.concat([series_central_elec,
                components_df.loc[components_df["input"] == central_buses[i]]
                ["label"]])
        for i in series_central_elec.values:
            if str(components_df.loc[components_df["label"] == i]
                   ["transformer type"].values[0]) == "GenericTransformer":
                elec_amounts_dict["central_consumption"].append(
                    get_value(i, "input 1/kWh", dataframe)
                )
        
        # get the PV-Systems' amounts using pv_elec amount method above
        elec_amounts_dict, pv_buses = pv_elec_amount(
            components_df.copy(), "photovoltaic", dataframe, elec_amounts_dict
        )
        # append the pv_excess on the elec amounts dict
        for bus in pv_buses:
            elec_amounts_dict["PV_excess"].append(
                get_value(str(bus) + "_excess", "input 1/kWh", dataframe)
            )
        
        # get the energy system's solar thermal flat plates from nodes
        # data TODO CSP
        df_st = components_df[
            (components_df.isin([str("solar_thermal_flat_plate")])).any(axis=1)
        ]
        # append the electric consumption of the solar thermal flat
        # plates on the elec amount dict
        for num, comp in df_st.iterrows():
            input1 = get_value(comp["label"], "input 1/kWh", dataframe)
            input2 = get_value(comp["label"], "input 2/kWh", dataframe)
            elec_amounts_dict["ST_elec"].append(
                input1 if input1 < input2 else input2
            )
        
        # get the energy system's heat pumps from nodes data
        df_hp = components_df[
            (components_df.isin(["CompressionHeatTransformer"])).any(axis=1)
        ]
        df_hp = pandas.concat([
            df_hp,
            (components_df.isin(["AbsorptionHeatTransformer"])).any(axis=1)]
        )
        # append the electric consumption of the heat pumps on the elec
        # amounts dict
        for num, comp in df_hp.iterrows():
            input1 = get_value(comp["label"], "input 1/kWh", dataframe)
            input2 = get_value(comp["label"], "input 2/kWh", dataframe)
            if comp["heat source"] == "Ground":
                elec_amounts_dict["GCHP"].append(
                    input1 if input1 < input2 else input2
                )
            elif comp["heat source"] == "Air":
                elec_amounts_dict["ASHP"].append(
                    input1 if input1 < input2 else input2
                )
            elif comp["heat source"] == "Water":
                elec_amounts_dict["SWHP"].append(
                    input1 if input1 < input2 else input2
                )

        # get the energy system's sinks from nodes data
        #df_sinks = components_df[(components_df["annual demand"].notna())]
        #df_sinks = pandas.concat(
        #    [df_sinks, components_df[(components_df["nominal value"].notna())]]
        #).drop_duplicates()
        ## collect the amount of electricity demand
        #for num, sink in df_sinks.iterrows():
        #    if sink_known[sink["label"]][0]:
        #        elec_amounts_dict["Electricity_Demand"].append(
        #            get_value(sink["label"], "input 1/kWh", dataframe)
        #        )

        # get the energy system's generic transformers from nodes data
        df_gen_transformer = components_df[
            (components_df.isin(["GenericTransformer"])).any(axis=1)
        ]
        # append the electric consumption of electric heating systems
        # on the elec amounts dict
        for num, comp in df_gen_transformer.iterrows():
            if "elec" in comp["input"] and "central" not in comp["label"]:
                elec_amounts_dict["Electric_heating"].append(
                    get_value(comp["label"], "input 1/kWh", dataframe)
                )
        
        # get the energy system's generic storages from nodes data
        df_storage = components_df[
            (components_df.isin(["Generic"])).any(axis=1)]
        # append the electric losses and output of generic battery
        # storages on the elec amounts dict
        for num, comp in df_storage.iterrows():
            if "elec" in comp["bus"] and "central" not in comp["label"]:
                value = get_value(comp["label"], "output 1/kWh", dataframe)
                elec_amounts_dict["Battery_output"].append(value)
                input_val = get_value(comp["label"], "input 1/kWh", dataframe)
                elec_amounts_dict["Battery_losses"].append(input_val - value)
        
        # get the energy system's shortage buses
        df_buses = components_df[(components_df["shortage"] == 1)]
        # append the imported elec amount on elec amounts dict
        for num, comp in df_buses.iterrows():
            if "elec" in comp["label"]:
                elec_amounts_dict["grid_import"].append(
                    get_value(comp["label"] + "_shortage",
                              "output 1/kWh", dataframe)
                )
        
        # get the energy system's links
        df_links = components_df[(components_df["bus1"].notna())]
        # append the electricity transport from pv systems to local
        # market on the elec amounts dict
        for num, link in df_links.iterrows():
            # pvbus -> local electricity market
            if link["bus1"] in pv_buses and "central" in link["bus2"]:
                elec_amounts_dict["PV_to_Central"].append(
                    get_value(link["label"], "output 1/kWh", dataframe)
                )
        # iterate threw the elec amounts dict and append the summed
        # entries on the elec amounts pandas dataframe
        elec_amounts = dict_to_dataframe(elec_amounts_dict, elec_amounts)
    # clear the old plot
    plt.clf()
    fig, axs = plt.subplots(4, sharex="all")
    fig.set_size_inches(18.5, 15.5)
    elec_amounts.set_index("run", inplace=True, drop=False)
    elec_amounts.to_csv(result_path + "/elec_amounts.csv")
    # create the elec amounts plot with 4 subplots (consumption,
    # usage of pv elec amount, pv earnings, central elec)
    plot_dict = {
        axs[0]: {
            "SLP_DEMAND": elec_amounts.Electricity_Demand,
            "Battery losses": elec_amounts.Battery_losses,
            "Electric_heating": elec_amounts.Electric_heating,
            "Heatpump_elec": elec_amounts.GCHP + elec_amounts.ASHP,
            "ST_elec": elec_amounts.ST_elec,
        },
        axs[1]: {
            "building consumption (PV)": elec_amounts.PV
            - elec_amounts.PV_to_Central
            - elec_amounts.PV_excess,
            "PV Export": elec_amounts.PV_excess,
            "PV to local market": elec_amounts.PV_to_Central,
            "GRID Import": elec_amounts.grid_import,
        },
        axs[2]: {
            "PV_south": elec_amounts.PV_south,
            "PV_south_east": elec_amounts.PV_south_east,
            "PV_south_west": elec_amounts.PV_south_west,
            "PV_west": elec_amounts.PV_west,
            "PV_east": elec_amounts.PV_east,
            "PV_north_west": elec_amounts.PV_north_west,
            "PV_north_east": elec_amounts.PV_north_east,
            "PV_north": elec_amounts.PV_north,
        },
        axs[3]: {"central_wc_elec": elec_amounts.central_wc_elec,
                 "central_ng_elec": elec_amounts.central_ng_elec,
                 "central_bg_elec": elec_amounts.central_bg_elec,
                 "central_pe_elec": elec_amounts.central_pe_elec,
                 "central_elec": elec_amounts.central_elec},
    }
    for plot in plot_dict:
        plot.stackplot(
            elec_amounts.reductionco2,
            plot_dict.get(plot).values(),
            labels=list(plot_dict.get(plot).keys()),
        )

    axs[0].legend(loc="upper left")
    axs[0].set_ylabel("Electricity Amount in kWh")
    axs[1].legend(loc="upper left")
    axs[1].set_ylabel("Electricity Amount in kWh")
    axs[2].legend(loc="upper left")
    axs[2].set_ylabel("Electricity Amount in kWh")
    axs[3].legend(loc="upper left")
    axs[3].set_ylabel("Electricity Amount in kWh")
    axs[3].invert_xaxis()
    # save the created plot
    plt.savefig(result_path + "/elec_amounts.jpeg")


if __name__ == "__main__":
    from program_files.preprocessing.create_energy_system import \
        import_scenario
    import pandas as pd
    
    create_elec_amount_plots(
            {"1": pd.read_csv("<path_to_csv_file>"),
             "0.75": pd.read_csv(),
             "0.5": pd.read_csv(),
             "0.25": pd.read_csv(),
             "0": pd.read_csv()},
            # scenario file path
            import_scenario(),
            # result_path
            str(os.path.dirname(__file__)),
            # sink types dict {label: [bool(elec), bool(heat), bool(cooling)]}
            {
               "sink_id": ["bool(elec)", "bool(heat)", "bool(cooling)"]
            }
    )
