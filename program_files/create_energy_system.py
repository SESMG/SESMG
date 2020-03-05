# -*- coding: utf-8 -*-
"""Functions for creating an oemof energy system.

---
@ Christian Klemm - christian.klemm@fh-muenster.de, 27.01.2020
"""

def import_scenario(filepath):
    """Imports data from a spreadsheet scenario file. 
    
    The excel sheet has to contain the following sheets:
        - timesystem
        - buses
        - transformers
        - sinks
        - sources
        - storages
        - powerlines
        - time_series

    ----    
        
    Keyword arguments:
        filename : obj:'str'
            -- path to excel scenario file

    ----
    
    Returns:
       nodes_data : obj:'dict'
           -- dictionary containing data from excel scenario file

    ----   
    @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
    """

    import os
    import logging
    from oemof.tools import logger
    import pandas as pd
    
    # read node data from Excel sheet
    filepath = filepath
    if not filepath or not os.path.isfile(filepath):
      raise FileNotFoundError('Excel data file {} not found.'.format(filepath))
    
    # create nodes from excel sheet
    xls = pd.ExcelFile(filepath)
    nodes_data = {'buses': xls.parse('buses'),
                      'transformers': xls.parse('transformers'),
                      'demand': xls.parse('sinks'),
                      'storages': xls.parse('storages'),
                      'links': xls.parse('links'),
                      'timeseries': xls.parse('time_series'),               
                      'timesystem': xls.parse('timesystem'),
                      'sources': xls.parse('sources')}
    
    # create nodes from Excel sheet data
    nd = nodes_data
    
    if not nd:
        raise ValueError('No nodes data provided.')

    return nd

    logger.define_logging()
    logging.info('Spreadsheet scenario succesfully imported.')
 
   
def define_energy_system(filepath, nodes_data):
    """Creates an energy system.
    
    Creates an energy system with the parameters defined in the given .xlsx-
    file. The file has to contain a sheet called "timesystem", which must have 
    the following structure:
        
    |start_date         |end_date           |holidays|temporal resolution|
    |-------------------|-------------------|--------|-------------------|
    |YYYY-MM-DD hh:mm:ss|YYYY-MM-DD hh:mm:ss|        |h                  |

    ----    
        
    Keyword arguments:
        filename : obj:'str'
            -- path to excel scenario file
        sheet : obj:'str'
            -- sheet in excel file, where the timesystem is defined
        nodes_data : obj:'dict'
            -- dictionary containing data from excel scenario file

    ----
    
    Returns:
       esys : obj:'dict'
           -- oemof energy system

    ----
    @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
    """
       
    import logging
    from oemof import solph
    import pandas as pd
    
    nd=nodes_data
    
    #read start and end date from excel sheet 
    for j, ts in nd['timesystem'].iterrows():
        start_date = ts['start date']
        end_date = ts['end date']
        temp_resolution = ts['temporal resolution']
    
    # create time index
    datetime_index = pd.date_range(start_date, end_date, freq=temp_resolution)
    
    # initialisation of the energy system
    esys = solph.EnergySystem(timeindex=datetime_index)
    
    # set datetime index
    nodes_data['timeseries'].set_index('timestamp', inplace=True)
    nodes_data['timeseries'].index = pd.to_datetime(
                                                nodes_data['timeseries'].index)
 #   logging.info('Data from Excel file {} imported.'.format(filename))

    logging.info('Date time index successfully defined:\n start date:          '
                 +str(start_date)
                 +',\n end date:            '
                 +str(end_date)
                 +',\n temporal resolution: '
                 +str(temp_resolution))
    
    return esys