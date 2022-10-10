# TODO PLOT MATRIX MIT BUBBLES(LEISTUNG)
# TODO ENERGIEMENGEN
# TODO ENERGIEMENGEN DER SENKEN OPTIONAL NACH SEKTOR SELEKTIEREN SODASS
#  UNTERSCHEIDUNG IM PLOT MÖGLICH IST
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
        ]:
            nodes_data[key].set_index("label", inplace=True, drop=False)
            if counter == 0:
                df_1 = nodes_data[key].copy()
                counter += 1
            elif counter != 0 and df_1 is not None:
                df_1 = pandas.concat([df_1, nodes_data[key]], ignore_index=True)
    return df_1[df_1["active"] == 1]


def get_value(label, column, dataframe):
    value = dataframe.loc[dataframe["ID"].str.startswith(label)][column].values
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
    return_df = pandas.concat([return_df, pd.DataFrame([series])])
    return_df.set_index("reductionco2", inplace=True, drop=False)
    return_df = return_df.sort_values("run")
    return return_df