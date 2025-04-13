"""
    Gregor Becker - gregor.becker@fh-muenster.de
"""
import pandas


def pv_electricity_amount(components_df: pandas.DataFrame, pv_st: str,
                          dataframe: pandas.DataFrame, amounts_dict: dict
                          ) -> dict:
    """
        method which is used to get the pv system earnings in total and
        azimuth specific as well as the output buses excess
    
        :param components_df: dataframe containing the nodes data's \
            entries
        :type components_df: pandas.DataFrame
        :param pv_st: str defining rather the algorithm searches for \
            photovoltaic or solar thermal entries
        :type pv_st: str
        :param dataframe: dataframe containing the considered pareto \
            point's result (components.csv)
        :type dataframe: pandas.DataFrame
        :param amounts_dict: dictionary holding the collected \
            electricity amounts for all pareto points
        :type amounts_dict: dict
    
        :return: - **amounts_dict** (dict) - dictionary holding the \
            collected electricity amounts for all pareto points within \
            this method the new PV entries were collected
    
    """
    from program_files.postprocessing.plotting import get_pv_st_dir, \
        get_value, add_value_to_amounts_dict

    pv_buses = []
    # get all photovoltaic entries from nodes data sources
    df_pv_or_st = components_df[(components_df.isin([str(pv_st)])).any(axis=1)]
    # get the components outputs and append them on the total pv
    # earnings as well as the azimuth specific dict entry (using
    # get_pv_st_dir) which is located in the plotting main file
    for num, comp in df_pv_or_st.iterrows():
        value_am = get_value(comp["label"], "output 1/kWh", dataframe)
        amounts_dict = add_value_to_amounts_dict(label="PV",
                                                 value_am=value_am,
                                                 amounts_dict=amounts_dict)
        
        amounts_dict = get_pv_st_dir(c_dict=amounts_dict,
                                     value=value_am,
                                     comp_type="PV",
                                     comp=comp)

    return amounts_dict


def get_electric_timeseries_sources(components_df: pandas.DataFrame,
                                    dataframe: pandas.DataFrame,
                                    amounts_dict: dict) -> dict:
    """
        method which is used to get the electric timeseries sources
        output as well as the output buses excess
    
        :param components_df: dataframe containing the nodes data's \
            entries
        :type components_df: pandas.DataFrame
        :param dataframe: dataframe containing the considered pareto \
            point's result (components.csv)
        :type dataframe: pandas.DataFrame
        :param amounts_dict: dictionary holding the collected \
            electricity amounts for all pareto points
        :type amounts_dict: dict
    
        :return: - **amounts_dict** (dict) - dictionary holding the \
            collected electricity amounts for all pareto points within \
            this method the new timeseries source entries were collected
    
    """
    from program_files.postprocessing.plotting import get_value, \
        add_value_to_amounts_dict

    # get the energy system's heat pumps from nodes data
    df_source = components_df[components_df["technology"] == "timeseries"]
    # get the components outputs and append them on the total pv
    # earnings as well as the azimuth specific dict entry (using
    # get_pv_st_dir) which is located in the plotting main file
    for num, comp in df_source.iterrows():
        if comp["sector"] == "electricity":
            value_am = get_value(comp["label"], "output 1/kWh", dataframe)
            amounts_dict = add_value_to_amounts_dict(label="Timeseries",
                                                     value_am=value_am,
                                                     amounts_dict=amounts_dict)

        # collect all output buses of the energy system's pv system to
        # calculate the pv excess
            value_am = get_value(comp["output"] + "_excess", "input 1/kWh",
                                 dataframe)
            amounts_dict = add_value_to_amounts_dict(label="Timeseries_excess",
                                                     value_am=value_am,
                                                     amounts_dict=amounts_dict)
    return amounts_dict


def get_electric_windpower_sources(components_df: pandas.DataFrame,
                                   dataframe: pandas.DataFrame,
                                   amounts_dict: dict) -> dict:
    """
        method which is used to get the windpower sources
        output as well as the output buses excess
    
        :param components_df: dataframe containing the nodes data's \
            entries
        :type components_df: pandas.DataFrame
        :param dataframe: dataframe containing the considered pareto \
            point's result (components.csv)
        :type dataframe: pandas.DataFrame
        :param amounts_dict: dictionary holding the collected \
            electricity amounts for all pareto points
        :type amounts_dict: dict
    
        :return: - **amounts_dict** (dict) - dictionary holding the \
            collected electricity amounts for all pareto points within \
            this method the new timeseries source entries were collected
    """
    from program_files.postprocessing.plotting import get_value, \
        add_value_to_amounts_dict
    
    # get the energy system's heat pumps from nodes data
    df_source = components_df[components_df["technology"] == "windpower"]
    # get the components outputs and append them on the total pv
    # earnings as well as the azimuth specific dict entry (using
    # get_pv_st_dir) which is located in the plotting main file
    for num, comp in df_source.iterrows():
        value_am = get_value(comp["label"], "output 1/kWh", dataframe)
        amounts_dict = add_value_to_amounts_dict(label="Windpower",
                                                 value_am=value_am,
                                                 amounts_dict=amounts_dict)
        
        # collect all output buses of the energy system's pv system to
        # calculate the pv excess
        value_am = get_value(comp["output"] + "_excess", "input 1/kWh",
                             dataframe)
        amounts_dict = add_value_to_amounts_dict(label="Windpower_excess",
                                                 value_am=value_am,
                                                 amounts_dict=amounts_dict)
    return amounts_dict


def get_st_electricity_amounts(components_df: pandas.DataFrame,
                               amounts_dict: dict,
                               dataframe: pandas.DataFrame) -> dict:
    """
        method which is used to get the electric demand of solar
        thermal flat plates
    
        :param components_df: dataframe containing the nodes data's \
            entries
        :type components_df: pandas.DataFrame
        :param dataframe: dataframe containing the considered pareto \
            point's result (components.csv)
        :type dataframe: pandas.DataFrame
        :param amounts_dict: dictionary holding the collected \
            electricity amounts for all pareto points
        :type amounts_dict: dict
    
        :return: - **amounts_dict** (dict) - dictionary holding the \
            collected electricity amounts for all pareto points within \
            this method the new timeseries source entries were collected
    """
    from program_files.postprocessing.plotting import get_value, \
        add_value_to_amounts_dict
    # get the energy system's solar thermal flat plates from nodes
    # data
    df_st = components_df[
        (components_df.isin([str("solar_thermal_flat_plate")])).any(axis=1)
    ]

    # append the electric consumption of the solar thermal flat
    # plates on the electricity amount dict
    for num, comp in df_st.iterrows():
        central = "" if "central" not in comp["sector"] else "central_"

        input1 = get_value(comp["label"], "input 1/kWh", dataframe)
        input2 = get_value(comp["label"], "input 2/kWh", dataframe)
        # TODO fix the input selection
        value = input1 if input1 < input2 else input2
        amounts_dict = add_value_to_amounts_dict(label= central + "ST_electricity",
                                                 value_am=value,
                                                 amounts_dict=amounts_dict)
    
    return amounts_dict


def sink_electricity_amounts(components_df: pandas.DataFrame, sink_known: dict,
                             dataframe: pandas.DataFrame,
                             amounts_dict: dict) -> dict:
    """
        Collecting the energy systems' electricity sinks flow data.

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
            this method by new electricity sink values

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
        if sink_known[sink["label"]][0]:
            # get the sinks input flow value
            value = get_value(sink["label"], "input 1/kWh", dataframe)
            # append the heat demand on the amounts dict
            amounts_dict = add_value_to_amounts_dict(
                label="electricity_demand",
                value_am=value,
                amounts_dict=amounts_dict)
    return amounts_dict


def generic_transformer_electricity_amounts(components_df: pandas.DataFrame,
                                            dataframe: pandas.DataFrame,
                                            amounts_dict: dict) -> dict:
    """
        Collecting the energy systems' electricity flow of generic
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
            this method by new electricity flows of generic \
            transformer components.
    """
    from program_files.postprocessing.plotting import get_value, \
        add_value_to_amounts_dict
    # get the energy system's generic transformers from nodes data
    df_gen_transformer = components_df[
        (components_df.isin(["GenericTransformer"])).any(axis=1)
    ]

    for num, transformer in df_gen_transformer.iterrows():
        central = "" if "central" not in transformer["sector"] else "central_"

        # values if the first output is an electricity output (one output "electricity", "central_electricity" OR
        # two outputs and "heat" in sector)
        if (transformer["sector"] == "electricity" and transformer["output2"] == "None") or \
            ("heat" in transformer["sector"] and transformer["output2"] != "None"):

            value = get_value(transformer["label"], "output 1/kWh", dataframe)

            # update dictionary
            amounts_dict = add_value_to_amounts_dict(
                    label=central + transformer["technology"],
                    value_am=value,
                    amounts_dict=amounts_dict)


        # values for two outputs and "central_electricity" (second output is electricity)
        elif "electricity" in transformer["sector"] and transformer["output2"] != "None":
            value = get_value(transformer["label"], "output 2/kWh", dataframe)

            # update dictionary
            amounts_dict = add_value_to_amounts_dict(
                label=central + transformer["technology"],
                value_am=value,
                amounts_dict=amounts_dict)


        # values for electric_heating
        elif transformer["sector"] == "electric_heat":
            value = get_value(transformer["label"], "input 1/kWh", dataframe)

            # update dictionaries
            amounts_dict = add_value_to_amounts_dict(
                    label=central + transformer["technology"],
                    value_am=value,
                    amounts_dict=amounts_dict)
    
    return amounts_dict


def get_heat_pump_electricity_amounts(components_df: pandas.DataFrame,
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
        input1 = get_value(comp["label"], "input 1/kWh", dataframe)
        input2 = get_value(comp["label"], "input 2/kWh", dataframe)
        value = input1 if input1 < input2 else input2
        central = "" if "central" not in comp["sector"] else "central_"
        # collecting the Ground source heat pumps' flows
        amounts_dict = add_value_to_amounts_dict(
            label=central + comp["technology"],
            value_am=value,
            amounts_dict=amounts_dict)
    return amounts_dict


def battery_storage_electricity_amounts(components_df: pandas.DataFrame,
                                        dataframe: pandas.DataFrame,
                                        amounts_dict: dict) -> dict:
    """
        Collecting the energy systems' battery storage losses
        
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
            this method by new battery loss values
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
        if "electricity" in storage["sector"]:
            amounts_dict = add_value_to_amounts_dict(
                    label=central + "battery_losses",
                    value_am=input_val - value,
                    amounts_dict=amounts_dict)
    return amounts_dict


def get_grid_import(components_df: pandas.DataFrame,
                    dataframe: pandas.DataFrame,
                    amounts_dict: dict):
    """
        Collecting the energy systems' electricity grid import.
        
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
            this method by new grid import values
    """
    from program_files.postprocessing.plotting import get_value, \
        add_value_to_amounts_dict
    # get the energy system's shortage buses
    df_buses = components_df[(components_df["shortage"] == 1)]
    # append the imported electricity amount on elec amounts dict
    for num, comp in df_buses.iterrows():
        if "electricity" in comp["sector"]:
            value = get_value(comp["label"] + "_shortage", "output 1/kWh",
                              dataframe)
            amounts_dict = add_value_to_amounts_dict(label="grid_import",
                                                     value_am=value,
                                                     amounts_dict=amounts_dict)
    return amounts_dict


def get_electricity_excess(components_df: pandas.DataFrame,
                    dataframe: pandas.DataFrame,
                    amounts_dict: dict):
    """
        Collecting the energy systems' electricity excess bus.

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
            this method by new electricity excess values
    """
    from program_files.postprocessing.plotting import get_value, \
        add_value_to_amounts_dict
    # get the energy system's shortage buses
    df_buses = components_df[(components_df["excess"] == 1)]
    # append the excess electricity amount on elec amounts dict
    for num, comp in df_buses.iterrows():
        if "electricity" in comp["sector"]:
            value = get_value(comp["label"] + "_excess", "input 1/kWh",
                              dataframe)
            amounts_dict = add_value_to_amounts_dict(label="electricity_bus_excess",
                                                     value_am=value,
                                                     amounts_dict=amounts_dict)

    return amounts_dict




def collect_electricity_amounts(
        dataframes: dict, nodes_data: dict, result_path: str,
        sink_known: dict) -> None:
    """
        main function of the algorithm to collect the electricity
        amounts of the investigated energy system for later plotting
        within the GUI
        
        :param dataframes: dictionary which holds the results of the \
            pareto optimization - structure {str(share of emission \
            reduction between 0 and 1): \
            pandas.DataFrame(components.csv)}
        :type dataframes: dict
        :param nodes_data: DataFrame containing all components defined \
            within the input model definition file
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
    # data frame which will represent the elec_amounts.csv
    elec_amounts = pandas.DataFrame()
    # iterate threw the pareto points
    for key in dataframes:
        # dictionary holding the result file row for pareto point key
        elec_amounts_dict = {"reductionco2": 100 * float(key)}

        dataframe = dataframes[key].copy()
        dataframe.reset_index(inplace=True, drop=False)
        components_df = get_dataframe_from_nodes_data(nodes_data)

        elec_amounts_dict = sink_electricity_amounts(
            components_df=components_df,
            sink_known=sink_known,
            dataframe=dataframe,
            amounts_dict=elec_amounts_dict
        )
        
        elec_amounts_dict = pv_electricity_amount(
            components_df=components_df,
            pv_st="photovoltaic",
            dataframe=dataframe,
            amounts_dict=elec_amounts_dict
        )
        
        elec_amounts_dict = battery_storage_electricity_amounts(
            components_df=components_df,
            dataframe=dataframe,
            amounts_dict=elec_amounts_dict
        )
        
        elec_amounts_dict = get_electric_timeseries_sources(
            components_df=components_df,
            dataframe=dataframe,
            amounts_dict=elec_amounts_dict
        )
        
        elec_amounts_dict = get_electric_windpower_sources(
            components_df=components_df,
            dataframe=dataframe,
            amounts_dict=elec_amounts_dict
        )
        
        elec_amounts_dict = generic_transformer_electricity_amounts(
            components_df=components_df,
            dataframe=dataframe,
            amounts_dict=elec_amounts_dict
        )
        
        elec_amounts_dict = get_st_electricity_amounts(
            components_df=components_df,
            dataframe=dataframe,
            amounts_dict=elec_amounts_dict
        )
        
        elec_amounts_dict = get_heat_pump_electricity_amounts(
            components_df=components_df,
            dataframe=dataframe,
            amounts_dict=elec_amounts_dict
        )
        
        elec_amounts_dict = get_grid_import(components_df=components_df,
                                            dataframe=dataframe,
                                            amounts_dict=elec_amounts_dict)

        elec_amounts_dict = get_electricity_excess(components_df=components_df,
                                            dataframe=dataframe,
                                            amounts_dict=elec_amounts_dict)

        # iterate threw the elec amounts dict and append the summed
        # entries on the elec amounts pandas dataframe
        elec_amounts = dict_to_dataframe(elec_amounts_dict, elec_amounts)
    elec_amounts.to_csv(result_path + "/elec_amounts.csv")


