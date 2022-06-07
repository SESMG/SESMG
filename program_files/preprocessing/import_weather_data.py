from shapely.geometry import Point, Polygon
from feedinlib.open_FRED import Weather, defaultdb
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import timedelta

def create_weather_data_plot(lat, lon):
    fig = plt.figure(figsize=(8, 8))
    m = Basemap(projection='lcc', resolution=None,
                width=4E6, height=4E6,
                lat_0=lat, lon_0=lon, )
    m.etopo(scale=0.5, alpha=0.5)

    # Map (long, lat) to (x, y) for plotting
    x, y = m(lon, lat)
    plt.plot(x, y, 'ok', markersize=5)
    plt.text(x, y, '', fontsize=12)
    plt.show()
    
    
def import_open_fred_windpowerlib(nodes_data, lat, lon):
    location = Point(lon, lat)
    # download data for July 2017 (end date will not be included in the
    # time period for which data is downloaded)
    start_date = str(nodes_data["energysystem"].loc[1, "start date"])[:10]
    end_date = nodes_data["energysystem"].loc[1, "end date"]
    end_date = end_date + timedelta(days=1)
    end_date = str(end_date)[:10]
    # set variables set to download
    variables = "windpowerlib"
    heights= [10]
    open_FRED_weather_windpowerlib_single_location = Weather(
        start=start_date, stop=end_date, locations=[location],
        heights=heights,
        variables=variables,
        **defaultdb())
    windpowerlib_df = open_FRED_weather_windpowerlib_single_location.df(
        location=location,
        lib="windpowerlib")
    windpowerlib_df.reset_index(drop=False, inplace=True)
    for num, row in windpowerlib_df.iterrows():
        if num % 2 == 1:
            windpowerlib_df = windpowerlib_df.drop(num)
        else:
            windpowerlib_df.loc[num, "temperature"] = float(windpowerlib_df.loc[num, "temperature"]) - 273.15
    windpowerlib_df.reset_index(drop=True, inplace=True)
    nodes_data["weather data"]["pressure"] = windpowerlib_df["pressure"].copy()
    nodes_data["weather data"]["z0"] = windpowerlib_df["roughness_length"].copy()
    nodes_data["weather data"]["windspeed"] = windpowerlib_df["wind_speed"].copy()
    nodes_data["weather data"]["temperature"] = windpowerlib_df["temperature"].copy()
    return nodes_data


def import_open_fred_pvlib(nodes_data, lat, lon):
    location = Point(lon, lat)
    # download data for July 2017 (end date will not be included in the
    # time period for which data is downloaded)
    start_date = str(nodes_data["energysystem"].loc[1, "start date"])[:10]
    end_date = nodes_data["energysystem"].loc[1, "end date"]
    end_date = end_date + timedelta(days=1)
    end_date = str(end_date)[:10]
    # set variables set to download
    variables = "pvlib"
    heights = [10]
    open_FRED_weather_pvlib_single_location = Weather(
            start=start_date, stop=end_date, locations=[location],
            heights=heights,
            variables=variables,
            **defaultdb())
    pvlib_df = open_FRED_weather_pvlib_single_location.df(
            location=location,
            lib="pvlib")
    pvlib_df.reset_index(drop=False, inplace=True)
    counter = 0
    for num, row in pvlib_df.iterrows():
        if num != 0:
            if counter != 2:
                if counter == -1:
                    counter += 1
                else:
                    pvlib_df = pvlib_df.drop(num)
                    counter += 1
            else:
                counter = -1
        else:
            pvlib_df.loc[num, "index"] = pvlib_df.loc[num, "index"] - \
                                     timedelta(minutes=7, seconds=30)
    counter = 0
    save_df = {0:[]}
    pvlib_df.reset_index(drop=False, inplace=True)
    pvlib_df_copy = pvlib_df.copy()
    for num, row in pvlib_df_copy.iterrows():
        if num !=  0:
            save_df[counter].append(pvlib_df_copy.iloc[num])
            pvlib_df = pvlib_df.drop(num)
            if num % 2 == 0:
                counter += 1
                save_df.update({counter: []})
    for num in range(0, len(save_df) -1):
        df = save_df[num][0].copy()
        df["dni"] = (df["dni"] + save_df[num][1]["dni"]) / 2
        df["dhi"] = (df["dhi"] + save_df[num][1]["dhi"]) / 2
        df["ghi"] = (df["ghi"] + save_df[num][1]["ghi"]) / 2
        df["index"] = df["index"] + timedelta(minutes=7, seconds=30)
        pvlib_df = pvlib_df.append(df)
    pvlib_df.reset_index(drop=True, inplace=True)
    nodes_data["weather data"]["dhi"] = pvlib_df["dhi"].copy()
    nodes_data["weather data"]["dni"] = pvlib_df["dni"].copy()
    nodes_data["weather data"]["dirhi"] = (pvlib_df["ghi"].copy() - pvlib_df["dhi"].copy())
    nodes_data["weather data"].to_csv("wetter.csv")
    return nodes_data


if __name__ == "__main__":
    import_open_fred_windpowerlib()