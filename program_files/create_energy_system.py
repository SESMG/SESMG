# -*- coding: utf-8 -*-
"""
Functions for the creation of an oemof energy system.

---

@ Christian Klemm - christian.klemm@fh-muenster.de, 14.01.2020
"""

def import_scenario(filepath):
    """Imports data from a spreadsheet scenario file. The excel sheet has to contain
    the following sheets:
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
    
    @ Christian Klemm - christian.klemm@fh-muenster.de, 14.01.2020

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
                      'powerlines': xls.parse('powerlines'),
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
 
    
    
    
    
    
    
    
    
    
def define_energy_system(filepath,sheet, nodes_data):
    """Creates 

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
    
    @ Christian Klemm - christian.klemm@fh-muenster.de, 14.01.2020

    """
    
    
    
    import os
    import logging
    from oemof import solph
    import pandas as pd
    
    def read_excel_cell(file, sheet, column):
        """
        Reads the first value of a specific column from a given excel sheet
        @Christian Klemm
        """
        df = pd.read_excel(file, sheet_name = sheet, usecols = column)
        value=df.at[df.index[0],df.columns[0]]
        return value
    
    #read start and end date from excel sheet //code should be optimated
    start_date = read_excel_cell(filepath, sheet = sheet, column = [0])
    end_date = read_excel_cell(filepath, sheet = sheet, column = [1])
    temp_resolution = read_excel_cell(filepath, sheet = sheet, column = [3])
    
    datetime_index = pd.date_range(start_date, end_date, freq=temp_resolution)
    
    # initialisation of the energy system
    esys = solph.EnergySystem(timeindex=datetime_index)
    
    # set datetime index
    nodes_data['timeseries'].set_index('timestamp', inplace=True)
    nodes_data['timeseries'].index = pd.to_datetime(nodes_data['timeseries'].index)
 #   print('Data from Excel file {} imported.'.format(filename))

    logging.info('Date time index successfully defined:\n start:        '+str(start_date)+
                                                     ',\n end:          '+str(end_date)+
                                                     ',\n resolution:   '+str(temp_resolution))
    
    return esys