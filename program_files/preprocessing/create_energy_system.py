# -*- coding: utf-8 -*-
"""
    Functions for creating an oemof energy system.

    Christian Klemm - christian.klemm@fh-muenster.de
"""
import pandas
import logging
from program_files.preprocessing.import_weather_data \
    import import_open_fred_weather_data
from oemof.solph import EnergySystem


def import_model_definition(filepath: str, delete_units=True) -> dict:
    """
        Imports data from a spreadsheet model definition file.
    
        The excel sheet has to contain the following sheets:
    
            - energysystem
            - buses
            - transformers
            - sinks
            - sources
            - storages
            - links
            - time series
            - weather data
            - competition constraints
            - insulation
            - district heating
            - pipe types
    
        :param filepath: path to excel model definition file
        :type filepath: str
        :param delete_units: boolean which defines rather the unit \
            row in the imported spreadsheets is removed or not
        :type delete_units: bool
    
        :raises: - **FileNotFoundError** - excel spreadsheet not found
    
        :return: - **nodes_data** (dict) - dictionary containing excel sheets
    """
    # creates nodes from excel sheet
    try:
        xls = pandas.ExcelFile(filepath)
    except FileNotFoundError:
        raise FileNotFoundError("Problem importing model definition file.")
    
    nodes_data = {
        "buses": xls.parse("buses", na_filter=False),
        "energysystem": xls.parse("energysystem", na_filter=False),
        "sinks": xls.parse("sinks", na_filter=False),
        "links": xls.parse("links", na_filter=False),
        "sources": xls.parse("sources", na_filter=False),
        "timeseries": xls.parse("time series", parse_dates=["timestamp"], na_filter=False),
        "transformers": xls.parse("transformers", na_filter=False),
        "storages": xls.parse("storages", na_filter=False),
        "weather data": xls.parse("weather data", parse_dates=["timestamp"], na_filter=False),
        "competition constraints": xls.parse("competition constraints", na_filter=False),
        "insulation": xls.parse("insulation", na_filter=False),
        "district heating": xls.parse("district heating", na_filter=False),
        "pipe types": xls.parse("pipe types", na_filter=False)
    }
    if delete_units:
        # delete spreadsheet row within technology or units specific
        # parameters
        for index in nodes_data.keys():
            if index not in ["timeseries", "weather data"] \
                    and len(nodes_data[index]) > 0:
                nodes_data[index] = nodes_data[index].drop(index=0)
    
    # returns logging info
    logging.info("\t Spreadsheet scenario successfully imported.")
    # if the user imported coordinates for the OpenFred weather data
    # download the import algorithm is triggered
    if nodes_data["energysystem"].loc[1, "weather data lat"] \
            not in ["None", "none"]:
        logging.info("\t Start import weather data")
        lat = nodes_data["energysystem"].loc[1, "weather data lat"]
        lon = nodes_data["energysystem"].loc[1, "weather data lon"]
        nodes_data = import_open_fred_weather_data(nodes_data, lat, lon)
    # returns nodes data
    return nodes_data


def align_timeseries_to_perfect_grid(nodes_data: dict) -> dict:
    """
        Takes raw data from dictionary (with potential Daylight Saving Time gaps
        or duplicate winter time entries), aligns them to a mathematically
        perfect UTC time grid, and fills missing values.

        :param nodes_data: dictionary containing data from nodes_data
        :type nodes_data: dict

        :return: - **nodes_data** (dict) - dictionary containing data \
            from nodes_data with aligned timeseries \
            and weather data
    """
    logging.info("\t Aligning timeseries and weather data to perfect UTC grid...")

    # Read parameters from the energysystem sheet
    row = next(nodes_data["energysystem"].iterrows())[1]
    temp_resolution = row["temporal resolution"]
    timezone = row["timezone"]

    # Calculate the mathematically perfect UTC time grid
    start_date_naive = pandas.to_datetime(row["start date"])
    end_date_naive = pandas.to_datetime(row["end date"])

    start_utc = start_date_naive.tz_localize(timezone).tz_convert("UTC")
    end_utc = end_date_naive.tz_localize(timezone).tz_convert("UTC")

    perfect_utc_index = pandas.date_range(start=start_utc, end=end_utc, freq=temp_resolution)

    # Repair all relevant sheets
    for sheet in ["timeseries", "weather data"]:
        if sheet not in nodes_data or nodes_data[sheet].empty:
            continue

        df = nodes_data[sheet].copy()

        # Set 'timestamp' column as index, if not done already
        if "timestamp" in df.columns:
            df.set_index("timestamp", inplace=True)

        # ensure index is parsed as datetime objects
        df.index = pandas.to_datetime(df.index)

        # Localize naive local timestamps to the specified target timezone:
        # ambiguous: Handles autumn DST overlap (duplicate hours). Tries 'infer' first;
        # falls back to 'NaT' if duplicate sequences are incomplete.
        try:
            df.index = df.index.tz_localize(timezone, ambiguous="infer")
        except Exception:
            df.index = df.index.tz_localize(timezone, ambiguous="NaT", nonexistent="NaT")

        # Drop invalid or unresolvable timestamps (NaT) created during localization
        df = df[df.index.notna()]

        # convert the clean local times to UTC
        df.index = df.index.tz_convert("UTC")

        # Average duplicate timestamps upfront (e.g. DST fallback in autumn or raw data duplicates)
        df = df.groupby(df.index).mean()

        # Align to the perfect UTC grid
        # creates empty (NaN) rows for the hours dropped or that were missing in the raw data
        df = df.reindex(perfect_utc_index)

        # Coerce all data columns to float/int, converting invalid strings to NaN
        for col in df.columns:
            df[col] = pandas.to_numeric(df[col], errors="coerce")

        # Interpolate gaps (e.g. DST spring forward), then backfill/forwardfill edge cases
        df = df.interpolate(method='linear').bfill().ffill()

        # Convert the index back to a 'timestamp' column so the rest of the code
        # (e.g. timeseries_preparation) works as expected
        df.index.name = "timestamp"
        df.reset_index(inplace=True)

        # Remove timezone metadata so Excel exports won't crash
        # Times remain mathematically on UTC level, but are now "tz-naive".
        df["timestamp"] = df["timestamp"].dt.tz_localize(None)

        nodes_data[sheet] = df

    return nodes_data


def define_energy_system(nodes_data: dict) -> (EnergySystem, dict):
    """
        Creates an energy system with the parameters defined in the
        given .xlsx-file. The file has to contain a sheet called
        "energysystem", which has to be structured as follows:
    
        +-------------------+-------------------+-------------------+
        |start_date         |end_date           |temporal resolution|
        +-------------------+-------------------+-------------------+
        |YYYY-MM-DD hh:mm:ss|YYYY-MM-DD hh:mm:ss|h                  |
        +-------------------+-------------------+-------------------+
    
        :param nodes_data: dictionary containing data from excel model \
            definition file
        :type nodes_data: dict
        
        :return: - **esys** (oemof.solph.Energysystem) - oemof energy \
                    system
                 - **nodes_data** (dict) - dictionary containing data \
                    from excel model definition file after the \
                    timestamps of timeseries and weather data sheet \
                    have been changed
    """
    # fix pyomo error while using the streamlit gui
    import pyutilib.subprocess.GlobalData
    pyutilib.subprocess.GlobalData.DEFINE_SIGNAL_HANDLERS_DEFAULT = False
    
    # Importing energysystem parameters from the scenario
    row = next(nodes_data["energysystem"].iterrows())[1]
    temp_resolution = row["temporal resolution"]
    timezone = row["timezone"]

    # parse start/end
    start_date_naive = pandas.to_datetime(row["start date"])
    end_date_naive = pandas.to_datetime(row["end date"])

    # localize start and end date
    start_date_local = start_date_naive.tz_localize(timezone)
    end_date_local = end_date_naive.tz_localize(timezone)

    # convert to time utc
    start_date = start_date_local.tz_convert("UTC")
    end_date = end_date_local.tz_convert("UTC")
    
    # creates time index
    datetime_index = pandas.date_range(start=start_date,
                                       end=end_date,
                                       freq=temp_resolution)

    
    # initialisation of the energy system   
    esys = EnergySystem(timeindex=datetime_index, infer_last_interval=False)
    # setting the index column for time series and weather data
    for sheet in ["timeseries", "weather data"]:
        # defines a time series
        nodes_data[sheet].set_index("timestamp", inplace=True)
        # ensures the index consists of proper datetime objects and re-adds UTC for oemof
        nodes_data[sheet].index = pandas.to_datetime(nodes_data[sheet].index).tz_localize("UTC")
    # returns logging info
    logging.info(
            "Date time index successfully defined:\n start date:          "
            + str(start_date)
            + ",\n end date:            "
            + str(end_date)
            + ",\n temporal resolution: "
            + str(temp_resolution)
    )
    
    # returns oemof energy system as result of this function
    return esys, nodes_data
