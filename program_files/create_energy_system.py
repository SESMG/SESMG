# -*- coding: utf-8 -*-
"""Functions for creating an oemof energy system.
---
@ Christian Klemm - christian.klemm@fh-muenster.de, 27.01.2020
"""
import os
import pandas as pd
import logging


def import_scenario(filepath):
    """Imports data from a spreadsheet scenario file. 
    
    The excel sheet has to contain the following sheets:
        - energysystem
        - buses
        - transformers
        - sinks
        - sources
        - storages
        - powerlines
        - time_series

    ----    
        
    Keyword arguments:
        filepath : obj:'str'
            -- path to excel scenario file

    ----
    
    Returns:
       nodes_data : obj:'dict'
           -- dictionary containing data from excel scenario file

    ----   
    @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
    """

    from oemof.tools import logger
    # reads node data from Excel sheet
    if not filepath or not os.path.isfile(filepath):
        raise FileNotFoundError(
            'Excel data file {} not found.'.format(filepath))

    # creates nodes from excel sheet
    xls = pd.ExcelFile(filepath)
    sources = \
        pd.concat(pd.read_excel(filepath,
                                sheet_name=['PV', 'ConcentratedSolar',
                                            'FlatPlate', 'Timeseries',
                                            'Wind', 'Commodity']),
                  ignore_index=True, sort=True)
    transformer = \
        pd.concat(pd.read_excel(filepath,
                                sheet_name=['GenericTransformer',
                                            'GenericCHP',
                                            'HeatPump&Chiller',
                                            'AbsorptionChiller']),
                  ignore_index=True, sort=True)

    storages = \
        pd.concat(pd.read_excel(filepath,
                                sheet_name=['GenericStorage',
                                            'StratifiedStorage']),
                  ignore_index=True, sort=True)

    nd = {'buses': xls.parse('buses'),
          'energysystem': xls.parse('energysystem'),
          'demand': xls.parse('sinks'),
          'links': xls.parse('links'),
          'sources': sources,
          'timeseries': xls.parse('time_series'),
          'transformers': transformer,
          'storages': storages
          # 'constraints': xls.parse('constraints')
          }

    # error message, if no nodes are provided
    if not nd:
        raise ValueError('No nodes data provided.')

    # returns logging info
    logging.info('Spreadsheet scenario successfully imported.')
    # returns nodes
    return nd


def define_energy_system(nodes_data):
    """Creates an energy system.
    
    Creates an energy system with the parameters defined in the given
    .xlsx-file. The file has to contain a sheet called "energysystem",
    which has to be structured as follows:
        
    |start_date         |end_date           |temporal resolution|
    |-------------------|-------------------|-------------------|
    |YYYY-MM-DD hh:mm:ss|YYYY-MM-DD hh:mm:ss|h                  |

    ----    
        
    Keyword arguments:
        nodes_data : obj:'dict'
            -- dictionary containing data from excel scenario file

    ----
    
    Returns:
       esys : obj:'dict'
           -- oemof energy system

    ----
    @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
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
        nodes_data['timeseries'].index)

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


def format_weather_dataset(filepath):
    """
    The feedinlib can only read .csv data sets, so the weather data from
    the .xlsx scenario file have to be converted into a .csv data set
    and saved
    ----
    Keyword arguments:
        filepath: obj:'str'
        -- -- path to excel scenario file
    """

    # The feedinlib can only read .csv data sets, so the weather data
    # from the .xlsx scenario file have to be converted into a
    # .csv data set and saved
    read_file = pd.read_excel(filepath, sheet_name='weather data')
    read_file.to_csv(os.path.join(os.path.dirname(__file__))
                     + '/interim_data/weather_data.csv', index=None,
                     header=True)
