"""
    Gregor Becker - gregor.becker@fh-muenster.de
    Janik Budde - janik.budde@fh-muenster.de
"""
import pandas


def add_value_to_amounts_dict(label: str, value_am: float,
                              amounts_dict: dict) -> dict:
    """
        Adds the value_am to the given amounts dict by checking if
        the chosen label is already part of the amounts dict (append)
        or not (create new dict entry).
        
        :param label: dict key which will be updated or added
        :type label: str
        :param value_am: value which will be appended to the label's \
            list in the amounts dict
        :type value_am: dict
        :param amounts_dict: dictionary holding the already collected \
            energy amounts
        :type amounts_dict: dict
        
        :return: - **amounts_dict** (dict) -  amounts dict after the \
            new value was added
    """
    if label in amounts_dict.keys():
        amounts_dict[label].append(value_am)
    else:
        amounts_dict.update({label: [value_am]})
    
    return amounts_dict


def get_dataframe_from_nodes_data(nodes_data: dict) -> pandas.DataFrame:
    """
        Within this method the nodes_data DataFrames are combined to
        one big DataFrame holding all the active components of the
        studied energy system.
        
        :param nodes_data: dictionary holding the model definition's \
            spreadsheet data
        :type nodes_data: dict
        
        :return: **-** (pandas.DataFrame) - one big DataFrame holding \
            all active components of the studied energy system
    """
    df_1 = None
    counter = 0
    for key in nodes_data.keys():
        # extract the relevant frames from spreadsheet and set their
        # index
        if key not in [
            "energysystem",
            "timeseries",
            "weather data",
            "district heating",
            "competition constraints",
            "pipe types"
        ]:
            nodes_data[key].set_index("label", inplace=True, drop=False)
            if counter == 0:
                df_1 = nodes_data[key].copy()
                counter += 1
            elif counter != 0 and df_1 is not None:
                df_1 = pandas.concat([df_1, nodes_data[key]],
                                     ignore_index=True)
    return df_1[df_1["active"] == 1]


def get_value(label: str, column: str, dataframe: pandas.DataFrame) -> float:
    """
        Method to locate the values of a given column from the given
        dataframe while the row location is driven by the components ID
        (label).
        
        :param label: string holding the component's ID (label)
        :type label: str
        :param column: string holding the searched column label
        :type column: str
        :param dataframe: DataFrame in which the values will be searched
        :type dataframe: pandas.DataFrame
        
        :return: - **-** (float) - float representing the value of the \
            investigated row's (label) column
    """
    value = dataframe.loc[dataframe["ID"] == label][column].values
    return float(value[0]) if value.size > 0 else 0


def get_pv_st_dir(c_dict: dict, value: float, comp_type: str,
                  comp: pandas.Series) -> dict:
    """
        This method creates an entry in the dictionary c_dict
        associated with the cardinal direction for the PV or ST system
        under consideration and returns it to the plotting.
        
        NOTE: This method only works for azimuth between 0° and 360°.
        Please make sure not to use -180° - 180°.
        
        :param c_dict: component dictionary holding the PV or ST \
            cardinal specific values
        :type c_dict: dict
        :param value: value which will be appended regarding it's \
            cardinal direction to the dictionary c_dict
        :type value: float
        :param comp_type: String that is used to distinguish whether \
            it is a PV or an ST plant.
        :type comp_type: str
        :param comp: Series holding the nodes data row of the \
            investigated component
        :type comp: pandas.Series
        
        :return: - **c_dict** (dict) - dictionary holding the PV or ST \
            cardinal specific values which was updated within this \
            method
    """
    dir_dict = {
        "_north_east": [22.5, 67.5],
        "_east": [67.5, 112.5],
        "_south_east": [112.5, 157.5],
        "_south": [157.5, 202.5],
        "_south_west": [202.5, 247.5],
        "_west": [247.5, 292.5],
        "_north_west": [292.5, 237.5],
    }
    not_north = False
    for dire in dir_dict:
        if not dir_dict[dire][0] <= comp["Azimuth"] < dir_dict[dire][1]:
            pass
        else:
            c_dict = add_value_to_amounts_dict(label=comp_type + dire,
                                               value_am=value,
                                               amounts_dict=c_dict)
            not_north = True
    # handling north since its between 237.5° and 22.5°
    if not not_north:
        c_dict = add_value_to_amounts_dict(label=comp_type + "_north",
                                           value_am=value,
                                           amounts_dict=c_dict)
    return c_dict


def dict_to_dataframe(amounts_dict: dict, return_df: pandas.DataFrame
                      ) -> pandas.DataFrame:
    """
        Method to convert the dictionary with the collected data of a
        Pareto point to a row of return_df.
        
        :param amounts_dict: dictionary holding the previously \
            collected data of the energy systems' components
        :type amounts_dict: dict
        :param return_df: DataFrame to which the new pareto point's \
            row will be added
        :type return_df: pandas.DataFrame
        
        :return: - **return_df** (pandas.DataFrame) - DataFrame \
            holding the amounts of the already considered pareto \
            points (within this method a new row has been added)
    """
    # summing up the previously collected data of the energy system
    # components
    for label in amounts_dict:
        if label != "reductionco2":
            print(label)
            amounts_dict[label] = sum(amounts_dict[label])
    # convert the dictionary into a pandas Series
    series = pandas.Series(data=amounts_dict)
    # append the created series to the pandas Dataframe
    return_df = pandas.concat([return_df, pandas.DataFrame([series])])
    return_df = return_df.sort_values("reductionco2")
    return return_df


def create_sink_differentiation_dict(model_definition: pandas.DataFrame
                                     ) -> dict:
    """
        use the model_definitions sink sheet to create a dictionary
        holding the sink's type as well as it's label
        
        :param model_definition: sinks sheet of the investigated model \
            definition
        :type model_definition: pandas.DataFrame
        
        :return: **sink_types** (dict) - dictionary holding the energy \
            systems' sinks types after a distinction based on the \
            sector column has been done
    """
    sink_types = {}
    
    for num, sink in model_definition.iterrows():
        if sink["sector"] == "electricity":
            sink_types.update({sink["label"]: [True, False, False]})
        elif sink["sector"] == "heat":
            sink_types.update({sink["label"]: [False, True, False]})
        else:
            sink_types.update({sink["label"]: [False, False, True]})
    
    return sink_types


def collect_pareto_data(result_dfs: dict, result_path: str) -> None:
    """
        In this method, the data is prepared for plotting a pareto
        curve.

        :param result_dfs: dictionary containing the energy systems' \
            components.csv
        :type result_dfs: dict
        :param result_path: path where the pareto plot will be stored
        :type result_path: str
    """
    # dict containing pareto points data
    costs = {"monetary": [], "emissions": []}
    
    for dataframe in result_dfs:
        if dataframe != "1":
            costs["monetary"].append(
                    sum(result_dfs[dataframe]["variable costs/CU"])
                    + sum(result_dfs[dataframe]["periodical costs/CU"])
            )
            costs["emissions"].append(
                    sum(result_dfs[dataframe]["constraints/CU"]))
        else:
            costs["emissions"].append(
                    sum(result_dfs[dataframe]["variable costs/CU"]) + sum(
                            result_dfs[dataframe]["periodical costs/CU"])
            )
            costs["monetary"].append(
                    sum(result_dfs[dataframe]["constraints/CU"]))
    
    # create pandas Dataframe from results' components.csv points
    df1 = pandas.DataFrame(
            {"costs": costs["monetary"], "emissions": costs["emissions"]},
            columns=["costs", "emissions"],
    )
    df1.to_csv(result_path + "/pareto.csv")
