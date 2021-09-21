# -*- coding: utf-8 -*-
"""
    Functions for creating an oemof energy system.

    Christian Klemm - christian.klemm@fh-muenster.de
"""
import os
import pandas as pd
import logging


def import_scenario(filepath: str) -> dict:
    """
        Imports data from a spreadsheet scenario file.

        The excel sheet has to contain the following sheets:

            - energysystem
            - buses
            - transformers
            - sinks
            - sources
            - storages
            - powerlines
            - time_series

        :param filepath: path to excel scenario file
        :type filepath: str

        :raises FileNotFoundError: excel spreadsheet not found
        :raises ValueError: content of excel spreadsheet not
                            readable or empty

        :return: - **nd** (dict) - dictionary containing excel sheets

        Christian Klemm - christian.klemm@fh-muenster.de
    """
    from oemof.tools import logger
    # reads node data from Excel sheet
    if not filepath or not os.path.isfile(filepath):
        raise FileNotFoundError(
            'Excel data file {} not found.'.format(filepath))

    # creates nodes from excel sheet
    xls = pd.ExcelFile(filepath)

    if 'sources' in xls.sheet_names:
        nd = {'buses': xls.parse('buses'),
              'energysystem': xls.parse('energysystem'),
              'sinks': xls.parse('sinks'),
              'links': xls.parse('links'),
              'sources': xls.parse('sources'),
              'timeseries': xls.parse('time series'),
              'transformers': xls.parse('transformers'),
              'storages': xls.parse('storages'),
              'weather data': xls.parse('weather data'),
              'competition constraints': xls.parse('competition constraints'),
              'energetic_renovation': xls.parse('energetic renovation measures')
              }
        # delete spreadsheet row within technology or units specific parameters
        list = ["energysystem", "buses", "sinks", "sources", "transformers",
                "storages", "links", "competition constraints",
                "energetic_renovation"]
        for i in list:
            nd[i] = nd[i].drop(index=0)

    # error message, if no nodes are provided
    if not nd:
        raise ValueError('No nodes data provided.')

    # returns logging info
    logging.info('Spreadsheet scenario successfully imported.')
    # returns nodes
    return nd


def define_energy_system(nodes_data: dict):
    """
        Creates an energy system.

        Creates an energy system with the parameters defined in the given
        .xlsx-file. The file has to contain a sheet called "energysystem",
        which has to be structured as follows:

        +-------------------+-------------------+-------------------+
        |start_date         |end_date           |temporal resolution|
        +-------------------+-------------------+-------------------+
        |YYYY-MM-DD hh:mm:ss|YYYY-MM-DD hh:mm:ss|h                  |
        +-------------------+-------------------+-------------------+

        :param nodes_data: dictionary containing data from excel scenario
                           file
        :type nodes_data: dict
        :return: - **esys** (oemof.Energysystem) - oemof energy system

        Christian Klemm - christian.klemm@fh-muenster.de
    """

    from oemof import solph
    # Importing energysystem parameters from the scenario
    ts = next(nodes_data['energysystem'].iterrows())[1]
    temp_resolution = ts['temporal resolution']
    start_date = ts['start date']
    end_date = ts['end date']

    # creates time index
    datetime_index = pd.date_range(start_date, end_date, freq=temp_resolution)

    # initialisation of the energy system
    esys = solph.EnergySystem(timeindex=datetime_index)
    # defines a time series
    nodes_data['timeseries'].set_index('timestamp', inplace=True)
    nodes_data['timeseries'].index = pd.to_datetime(
        nodes_data['timeseries'].index.values, utc=True)
    nodes_data['timeseries'].index = \
        pd.to_datetime(
            nodes_data['timeseries'].index).tz_convert("Europe/Berlin")
    nodes_data['weather data'].set_index('timestamp', inplace=True)
    nodes_data['weather data'].index = pd.to_datetime(
        nodes_data['weather data'].index.values, utc=True)
    nodes_data['weather data'].index = \
        pd.to_datetime(
            nodes_data['weather data'].index).tz_convert("Europe/Berlin")

    # returns logging info
    logging.info(
        'Date time index successfully defined:\n start date:          '
        + str(start_date)
        + ',\n end date:            '
        + str(end_date)
        + ',\n temporal resolution: '
        + str(temp_resolution))

    # returns oemof energy system as result of this function
    return esys
