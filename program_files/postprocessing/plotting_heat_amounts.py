"""
    Gregor Becker - gregor.becker@fh-muenster.de
"""
import pandas


def st_heat_amount(components_df: pandas.DataFrame, pv_st: str,
                   dataframe: pandas.DataFrame, amounts_dict: dict) -> dict:
    """
        Collecting the Solar thermal flat plates output flows within
        the amounts_dict["ST"] entry. Additionally a cardinal
        orientation distinction is made in the
        amounts_dict["ST_north"], amounts_dict["ST_west"], etc. is made.
        
        :param components_df: DataFrame containing all components of \
            the studied energy system
        :type components_df: pandas.DataFrame
        :param pv_st: string holding the technology of the components \
            to be collected
        :type pv_st: str
        :param dataframe: dataframe holding the energy systems' result \
            flows
        :type dataframe: pandas.DataFrame
        :param amounts_dict: dictionary holding the already collected \
            flow values of the studied energy system
        :type amounts_dict: dict
        
        :return: - **amounts_dict** (dict) - dictionary holding the \
            energy systems' flow amounts which was expanded within \
            this method by new ST values
    """
    from program_files.postprocessing.plotting import get_pv_st_dir, \
        get_value, add_value_to_amounts_dict
    if pv_st == "concentrated_solar_power":
        label = "CSP"
    else:
        label = "ST"
    # reduce the components dataframe to the entries containing the
    # "solar_thermal_flat_plate" string
    df_pv_or_st = components_df[(components_df.isin([str(pv_st)])).any(axis=1)]
    # iterate threw the resulting dataframe
    for num, comp in df_pv_or_st.iterrows():
        # append the found component output to the total ST production
        value_am = get_value(label=comp["label"],
                             column="output 1/kWh",
                             dataframe=dataframe)
        # add the value to amounts dict
        amounts_dict = add_value_to_amounts_dict(label=label,
                                                 value_am=value_am,
                                                 amounts_dict=amounts_dict)
        # within the get_pv_st_dir method the cardinal orientation
        # distinction is made
        amounts_dict = get_pv_st_dir(c_dict=amounts_dict,
                                     value=value_am,
                                     comp_type=label,
                                     comp=comp)
    return amounts_dict


def sink_heat_amounts(components_df: pandas.DataFrame, sink_known: dict,
                      dataframe: pandas.DataFrame, amounts_dict: dict) -> dict:
    """
        Collecting the energy systems' heat sinks flow data.
        
        :param components_df: DataFrame containing all components of \
            the studied energy system
        :type components_df: pandas.DataFrame
        :param dataframe: dataframe holding the energy systems' result \
            flows
        :type dataframe: pandas.DataFrame
        :param sink_known: dictionary which defines the type of the \
            energy systems' sinks structure {sink_label: [bool(elec), \
            bool(heat), bool(cooling)]}
        :type sink_known: dict
        :param amounts_dict: dictionary holding the already collected \
            flow values of the studied energy system
        :type amounts_dict: dict
        
        :return: - **amounts_dict** (dict) - dictionary holding the \
            energy systems' flow amounts which was expanded within \
            this method by new heat sink values
    """
    from program_files.postprocessing.plotting import get_value, \
        add_value_to_amounts_dict
    # get the energy system's sinks from nodes data
    df_sinks = components_df[(components_df["annual demand"].notna())]
    df_sinks = pandas.concat(
            [df_sinks,
             components_df[(components_df["nominal value"].notna())]]
    ).drop_duplicates()
    
    # collect the amount of heat demand by iterating threw the energy
    # systems' heat sinks
    for num, sink in df_sinks.iterrows():
        if sink_known[sink["label"]][1]:
            # get the sinks input flow value
            value = get_value(sink["label"], "input 1/kWh", dataframe)
            # append the heat demand on the amounts dict
            amounts_dict = add_value_to_amounts_dict(label="Heat Demand",
                                                     value_am=value,
                                                     amounts_dict=amounts_dict)
    return amounts_dict


def heat_pump_heat_amounts(components_df: pandas.DataFrame,
                           dataframe: pandas.DataFrame,
                           amounts_dict: dict) -> dict:
    """
        Collecting the energy systems' heat pumps flow data.
        
        :param components_df: DataFrame containing all components of \
            the studied energy system
        :type components_df: pandas.DataFrame
        :param dataframe: dataframe holding the energy systems' result \
            flows
        :type dataframe: pandas.DataFrame
        :param amounts_dict: dictionary holding the already collected \
            flow values of the studied energy system
        :type amounts_dict: dict
        
        :return: - **amounts_dict** (dict) - dictionary holding the \
            energy systems' flow amounts which was expanded within \
            this method by new heat pump values
    
    """
    from program_files.postprocessing.plotting import get_value, \
        add_value_to_amounts_dict
    # get the energy system's heat pumps from nodes data
    df_hp = components_df[components_df["transformer type"]
                          == "CompressionHeatTransformer"]
    df_hp = pandas.concat(
            [df_hp,
             components_df[components_df["transformer type"]
                           == "AbsorptionHeatTransformer"]]
    )
    # append the heat production of the heat pumps on the heat
    # amounts dict
    for num, comp in df_hp.iterrows():
        value = get_value(comp["label"], "output 1/kWh", dataframe)
        central = "" if "central" not in comp["sector"] else "central_"
        if comp["mode"] == "heat_pump":
            amounts_dict = add_value_to_amounts_dict(
                label=central + comp["technology"],
                value_am=value,
                amounts_dict=amounts_dict)
    return amounts_dict


def thermal_storage_heat_amounts(components_df: pandas.DataFrame,
                                 dataframe: pandas.DataFrame,
                                 amounts_dict: dict) -> dict:
    """
        Collecting the energy systems' thermal storage losses
        
        :param components_df: DataFrame containing all components of \
            the studied energy system
        :type components_df: pandas.DataFrame
        :param dataframe: dataframe holding the energy systems' result \
            flows
        :type dataframe: pandas.DataFrame
        :param amounts_dict: dictionary holding the already collected \
            flow values of the studied energy system
        :type amounts_dict: dict
        
        :return: - **amounts_dict** (dict) - dictionary holding the \
            energy systems' flow amounts which was expanded within \
            this method by new thermal loss values
    """
    from program_files.postprocessing.plotting import get_value, \
        add_value_to_amounts_dict
    # get the energy system's generic storages from nodes data
    df_storage = components_df[(components_df.isin(["Generic"])).any(axis=1)]
    for num, storage in df_storage.iterrows():
        value = get_value(storage["label"], "output 1/kWh", dataframe)
        input_val = get_value(storage["label"], "input 1/kWh", dataframe)
        # append the heat losses  of generic thermal
        # storages on the heat amounts dict
        central = "" if "central" not in storage["sector"] else "central_"
        if "heat" in storage["sector"]:
            amounts_dict = add_value_to_amounts_dict(
                    label=central + "thermal_storage_losses",
                    value_am=input_val - value,
                    amounts_dict=amounts_dict)
    return amounts_dict


def generic_transformer_heat_amounts(components_df: pandas.DataFrame,
                                     dataframe: pandas.DataFrame,
                                     amounts_dict: dict) -> dict:
    """
        Collecting the energy systems' heat flow of generic
        transformer components (e.g. CHP outputs or electric heating
        components).
        
        NOTE:
        
              It is always assumed that the components are driven
              electrically, so that the first output is an electricity
              output and the second is a heat output.
        
        :param components_df: DataFrame containing all components of \
            the studied energy system
        :type components_df: pandas.DataFrame
        :param dataframe: dataframe holding the energy systems' result \
            flows
        :type dataframe: pandas.DataFrame
        :param amounts_dict: dictionary holding the already collected \
            flow values of the studied energy system
        :type amounts_dict: dict

        :return: - **amounts_dict** (dict) - dictionary holding the \
            energy systems' flow amounts which was expanded within \
            this method by new heat flows of generic transformer \
            components.
    """
    from program_files.postprocessing.plotting import get_value, \
        add_value_to_amounts_dict
    # get the energy system's generic transformers from nodes data
    df_gen_transformer = components_df[
        (components_df.isin(["GenericTransformer"])).any(axis=1)
    ]
    for num, transformer in df_gen_transformer.iterrows():
        central = "" if "central" not in transformer["sector"] else "central_"
        value = get_value(transformer["label"], "output 1/kWh", dataframe)
        
        if transformer["output2"] == "None" \
                and "heat" in transformer["sector"]:
            amounts_dict = add_value_to_amounts_dict(
                    label=central + transformer["technology"],
                    value_am=value,
                    amounts_dict=amounts_dict)
        elif "heat" in transformer["sector"]:
            value2 = get_value(transformer["label"], "output 2/kWh", dataframe)
            amounts_dict = add_value_to_amounts_dict(
                    label=central + transformer["technology"],
                    value_am=value2,
                    amounts_dict=amounts_dict)
        else:
            pass
    
    return amounts_dict


def insulation_heat_amounts(components_df: pandas.DataFrame,
                            dataframe: pandas.DataFrame,
                            amounts_dict: dict) -> dict:
    """
        Collecting the energy systems' insulation heat compensation
        amounts
        
        :param components_df: DataFrame containing all components of \
            the studied energy system
        :type components_df: pandas.DataFrame
        :param dataframe: dataframe holding the energy systems' result \
            flows
        :type dataframe: pandas.DataFrame
        :param amounts_dict: dictionary holding the already collected \
            flow values of the studied energy system
        :type amounts_dict: dict
        
        :return: - **amounts_dict** (dict) - dictionary holding the \
            energy systems' flow amounts which was expanded within \
            this method by new insulation compensation amounts
    """
    from program_files.postprocessing.plotting import get_value, \
        add_value_to_amounts_dict
    # get the energy system's insulations from nodes data
    df_insulation = components_df[components_df["U-value new"].notna()]
    for num, insulation in df_insulation.iterrows():
        cap_sink = get_value(insulation["sink"], "capacity/kW", dataframe)
        cap_insulation = get_value(insulation["label"] + "-insulation",
                                   "capacity/kW", dataframe)
        value_sink = get_value(insulation["sink"], "input 1/kWh", dataframe)
        # append the heat savings of the insulations on the heat
        # amounts dict
        if cap_insulation != 0 and cap_sink != 0:
            amounts_dict = add_value_to_amounts_dict(
                    label="Insulation",
                    value_am=((cap_insulation * value_sink) / cap_sink),
                    amounts_dict=amounts_dict)
    
    return amounts_dict


def dh_heat_amounts(dataframe: pandas.DataFrame,
                    amounts_dict: dict) -> dict:
    """
        Collecting the energy systems' district heating consumer demands
        
        :param dataframe: dataframe holding the energy systems' result \
            flows
        :type dataframe: pandas.DataFrame
        :param amounts_dict: dictionary holding the already collected \
            flow values of the studied energy system
        :type amounts_dict: dict
        
        :return: - **amounts_dict** (dict) - dictionary holding the \
            energy systems' flow amounts which was expanded within \
            this method by new district heating consumer demands
    """
    from program_files.postprocessing.plotting import add_value_to_amounts_dict
    # append the transported heat amounts of the district heating
    # network to the heat amounts dict
    if "DH" not in amounts_dict.keys():
        amounts_dict.update({"DH": []})
    
    amounts_dict["DH"] += list(
            dataframe.loc[
                dataframe["ID"].str.startswith("dh_heat_house_station")][
                "output 1/kWh"
            ].values
    )
    
    return amounts_dict


def collect_heat_amounts(dataframes: dict, nodes_data: dict,
                         result_path: str, sink_known: dict) -> None:
    """
        main function of the algorithm to collect the heat
        amounts of the investigated energy system for later plotting
        within the GUI
        
        :param dataframes: dictionary which holds the results of the \
            pareto optimization - structure {str(share of emission \
            reduction between 0 and 1): \
            pandas.DataFrame(components.csv)}
        :type dataframes: dict
        :param nodes_data: DataFrame containing all components defined \
            within the input scenario file
        :type nodes_data: pandas.DataFrame
        :param result_path: str which defines the folder where the \
            elec_amount plot will be saved
        :type result_path: str
        :param sink_known: dictionary which defines the type of the \
            energy system's sinks structure {sink_label: [bool(elec), \
            bool(heat), bool(cooling)]}
        :type sink_known: dict
    """
    from program_files.postprocessing.plotting import (
        get_dataframe_from_nodes_data,
        dict_to_dataframe
    )
    # data frame which will represent the heat amounts csv file
    heat_amounts = pandas.DataFrame()
    # iterate threw the pareto points
    for key in dataframes:
        # dictionary holding the result file row for pareto point key
        heat_amounts_dict = {"reductionco2": 100 * float(key)}
        
        dataframe = dataframes[key].copy()
        dataframe.reset_index(inplace=True, drop=False)
        components_df = get_dataframe_from_nodes_data(nodes_data)
        # get the ST-Systems' amounts using st_heat_amount method above
        heat_amounts_dict = st_heat_amount(
                components_df=components_df,
                pv_st="solar_thermal_flat_plate",
                dataframe=dataframe,
                amounts_dict=heat_amounts_dict
        )
        
        # get the CSP-Systems' amounts using st_heat_amount method above
        heat_amounts_dict = st_heat_amount(
                components_df=components_df,
                pv_st="concentrated_solar_power",
                dataframe=dataframe,
                amounts_dict=heat_amounts_dict
        )
        # get the Heat sinks' amounts using sink_heat_amounts method
        # above
        heat_amounts_dict = sink_heat_amounts(components_df=components_df,
                                              sink_known=sink_known,
                                              dataframe=dataframe,
                                              amounts_dict=heat_amounts_dict)
        
        # get the Heat pumps' amounts using heat_pump_heat_amounts
        # method above
        heat_amounts_dict = heat_pump_heat_amounts(
                components_df=components_df,
                dataframe=dataframe,
                amounts_dict=heat_amounts_dict
        )
        
        heat_amounts_dict = generic_transformer_heat_amounts(
                components_df=components_df,
                dataframe=dataframe,
                amounts_dict=heat_amounts_dict
        )
        
        heat_amounts_dict = insulation_heat_amounts(
                components_df=components_df,
                dataframe=dataframe,
                amounts_dict=heat_amounts_dict)
        
        heat_amounts_dict = thermal_storage_heat_amounts(
                components_df=components_df,
                dataframe=dataframe,
                amounts_dict=heat_amounts_dict
        )
        
        heat_amounts_dict = dh_heat_amounts(dataframe=dataframe,
                                            amounts_dict=heat_amounts_dict)
        
        heat_amounts = dict_to_dataframe(heat_amounts_dict, heat_amounts)
    heat_amounts.to_csv(result_path + "/heat_amounts.csv")
