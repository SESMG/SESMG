"""
    Gregor Becker - gregor.becker@fh-muenster.de
    Oscar Quiroga - oscar.quiroga@fh-muenster.de
"""
from shapely.geometry import Point
from timezonefinder import TimezoneFinder
from pytz import timezone
from feedinlib.open_FRED import Weather, defaultdb
from datetime import timedelta
import geocoder
import logging


def set_esys_data(nodes_data: dict, location: Point, variables: str) -> dict:
    """
        Create the dictionary which is used to download the weather data
        form the OpenEnergyPlatform Database.
        
        :param nodes_data: dictionary containing the model definition \
            data
        :type nodes_data: dict
        :param location: shapely Point which represents the considered \
            location
        :type location: Point
        :param variables: str which differentiates between \
            windpowerlib and pvlib download
        :type variables: str
        
        :return: - **-** (dict) - dictionary containing the data \
            necessary for the OpenEnergyPlatform Database download
    """
    # since the last day is not included within the Download, the
    # energy systems end date is increased by one day
    end_date = nodes_data["energysystem"].loc[1, "end date"]
    end_date += timedelta(days=1)
    end_date = str(end_date)[:10]
    # return the dictionary containing the Data for the
    # OpenEnergyPlatform Database
    return {
        "start": str(nodes_data["energysystem"].loc[1, "start date"])[:10],
        "stop": end_date,
        "locations": [location],
        "heights": [10],
        "variables": variables,
    }


def import_open_fred_weather_data(nodes_data: dict, lat: float, lon: float
                                  ) -> dict:
    """
        This method downloads the windpowerlib and the pvlib relevant
        weather data from the OpenEnergyPlatform and assembles them to
        the weather data structure of the model definition.
        The modified model definition (nodes data) is then returned to
        the main algorithm.
        
        :param nodes_data: dictionary containing the model definition's\
             data
        :type nodes_data: dict
        :param lat: latitude of the investigated location in WGS84 \
            coordinates
        :type lat: float
        :param lon: longitude of the investigated location in WGS84 \
            coordinates
        :type lon: float
        
        :return: - **nodes_data** (dict) - modified model definition \
            data
    """
    # Validate Latitude and Longitude
    try:
        lonf = float(lon)
        latf = float(lat)
    except (TypeError, ValueError):
        logging.warning(
            f"Skipping weather import: invalid coordinates lat={lat!r}, lon={lon!r}"
        )
        return nodes_data
    location = Point(lonf, latf)
    # Detect timezone based on coordinates
    tf = TimezoneFinder()
    tz = timezone(tf.timezone_at(lng=lonf, lat=latf) or "UTC")
    
    # log the city and country of the given coords
    geo_info = geocoder.google([latf, lonf], method='reverse')
    logging.info("\t The inserted Open Fred coordinates point on "
                 + str(geo_info.city) + " in "
                 + str(geo_info.country) + "."
                 )
    # get windpowerlib relevant weather data from OPEN Fred
    wind_df = Weather(**set_esys_data(nodes_data, location, "windpowerlib"),
                      **defaultdb()).df(location=location, lib="windpowerlib")
    # Be sure the index is timezone-aware
    if wind_df.index.tz is None:
        wind_df.index = wind_df.index.tz_localize("UTC")
    
    # Convert to the specified timezone
    wind_df = wind_df.tz_convert(tz)
    
    # resample wind data
    wind_df = wind_df.resample("1h").mean()
    wind_df.reset_index(drop=True, inplace=True)
    nodes_data["weather_wind"] = wind_df

    # PV data
    # Use the same Location and Timezone as for wind data
    pv_df = Weather(**set_esys_data(nodes_data, location, "pvlib"),
                    **defaultdb()).df(location=location, lib="pvlib")
    if pv_df.index.tz is None:
        pv_df.index = pv_df.index.tz_localize("UTC")
    pv_df = pv_df.tz_convert(tz)
    pv_df = pv_df.resample("1h").mean()
    pv_df.reset_index(drop=True, inplace=True)
    nodes_data["weather_pv"] = pv_df
    
    # create weather data sheet
    data = {
        "pressure": wind_df["pressure"],
        "z0": wind_df["roughness_length"],
        "windspeed": wind_df["wind_speed"],
        "dhi": pv_df["dhi"],
        "dni": pv_df["dni"],
        "ghi": pv_df["ghi"],
        "temperature": pv_df["temp_air"],
    }

    for label in data:
        nodes_data["weather data"][label] = data[label].copy()
    # return nodes data with the new weather data sheet

    return nodes_data
