from shapely.geometry import Point, Polygon
from feedinlib.open_FRED import Weather, defaultdb
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import timedelta
import pandas as pd


def create_weather_data_plot(lat, lon):
    fig = plt.figure(figsize=(8, 8))
    m = Basemap(
        projection="lcc",
        resolution=None,
        width=4e6,
        height=4e6,
        lat_0=lat,
        lon_0=lon,
    )
    m.etopo(scale=0.5, alpha=0.5)

    # Map (long, lat) to (x, y) for plotting
    x, y = m(lon, lat)
    plt.plot(x, y, "ok", markersize=5)
    plt.text(x, y, "", fontsize=12)
    plt.show()


def set_esys_data(nodes_data, location, variables):
    # download data for July 2017 (end date will not be included in the
    # time period for which data is downloaded)
    end_date = nodes_data["energysystem"].loc[1, "end date"]
    end_date += timedelta(days=1)
    end_date = str(end_date)[:10]
    # set variables set to download
    heights = [10]
    return {"start": str(nodes_data["energysystem"].loc[1, "start date"])[:10],
            "stop": end_date, "locations": [location],
            "heights": heights, "variables": variables}


def import_open_fred_weather_data(nodes_data, lat, lon):
    # location of area under investigation
    location = Point(lon, lat)
    # get windpower weather data from OPEN Fred
    wind_df = Weather(**set_esys_data(nodes_data, location, "windpowerlib"),
                      **defaultdb()).df(location=location, lib="windpowerlib")
    # meaning the half hour values
    wind_df = wind_df.resample("1h").mean()
    wind_df.reset_index(drop=True, inplace=True)

    # get pv system weather data from OPEN Fred
    pv_df = Weather(**set_esys_data(nodes_data, location, "pvlib"),
                    **defaultdb()).df(location=location, lib="pvlib")
    # resample pv system data from quarter-hourly to hourly resolution
    pv_df = pv_df.resample("1h").mean()
    pv_df.reset_index(drop=True, inplace=True)
    # create weather data sheet
    wind_data = {"pressure": "pressure", "z0": "roughness_length",
                 "windspeed": "wind_speed"}
    for label in wind_data:
        nodes_data["weather data"][label] = wind_df[wind_data[label]].copy()
    pv_data = {"dhi": "dhi", "dni": "dni", "ghi": "ghi",
               "temperature": "temp_air"}
    for label in pv_data:
        nodes_data["weather data"][label] = pv_df[pv_data[label]].copy()
    nodes_data["weather data"].to_csv("weather.csv")
    return nodes_data
