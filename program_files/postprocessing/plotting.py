"""
    Gregor Becker - gregor.becker@fh-muenster.de
    Janik Budde - janik.budde@fh-muenster.de
"""
import pandas


def get_dataframe_from_nodes_data(nodes_data):
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
                df_1 = pandas.concat([df_1, nodes_data[key]], ignore_index=True)
    return df_1[df_1["active"] == 1]


def get_value(label, column, dataframe):
    value = dataframe.loc[dataframe["ID"] == label][column].values
    return float(value[0]) if value.size > 0 else 0


def get_pv_st_dir(c_dict, value, comp_type, comp):
    # TODO wie stellen wir fest ob -180 - 180 oder 0 - 360
    #  genutzt wurde
    dir_dict = {
        "_north_east": [22.5, 67.5],
        "_east": [67.5, 112.5],
        "_south_east": [112.5, 157.5],
        "_south": [157.5, 202.5],
        "_south_west": [202.5, 247.5],
        "_west": [247.5, 292.5],
        "_north_west": [292.5, 237.5],
    }
    test = False
    for dire in dir_dict:
        if not dir_dict[dire][0] <= comp["Azimuth"] < dir_dict[dire][1]:
            pass
        else:
            c_dict[comp_type + dire].append(value)
            test = True
    if not test:
        c_dict[comp_type + "_north"].append(value)
    return c_dict


def dict_to_dataframe(amounts_dict, return_df):
    for i in amounts_dict:
        if i != "run" and i != "reductionco2":
            amounts_dict[i] = sum(amounts_dict[i])
    series = pandas.Series(data=amounts_dict)
    return_df = pandas.concat([return_df, pandas.DataFrame([series])])
    return_df.set_index("reductionco2", inplace=True, drop=False)
    return_df = return_df.sort_values("run")
    return return_df


def create_sink_differentiation_dict(model_definition: pandas.DataFrame):
    """
        use the model_definitions sink sheet to create a dictionary
        holding the sink's type as well as it's label
        
        :param model_definition: sinks sheet of the investigated model \
            definition
        :type model_definition: pandas.DataFrame
        
        :return: - **sink_types** (dict) -
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
    df1 = pd.DataFrame(
            {"costs": costs["monetary"], "emissions": costs["emissions"]},
            columns=["costs", "emissions"],
    )
    df1.to_csv(result_path + "/pareto.csv")