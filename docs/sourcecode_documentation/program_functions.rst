Sourcecode documentation
*************************************************

define_energy_system()
-------------------------------------------------

.. container:: memitem

   .. container:: memproto

      ======================================================================================
      def program_files.create_energy_system.define_energy_system (*filepath*, *nodes_data*) 
      ======================================================================================

   .. container:: memdoc

      Creates an energy system.

      Creates an energy system with the parameters defined in the given
      .xlsx- file. The file has to contain a sheet called "timesystem",
      which must have the following structure:

      =================== =================== ======== ===================
      start_date          end_date            holidays temporal resolution
      =================== =================== ======== ===================
      YYYY-MM-DD hh:mm:ss YYYY-MM-DD hh:mm:ss          h
      =================== =================== ======== ===================

      --------------

      Parameters
         
         String filename : path to excel scenario file
         String sheet : sheet in excel file, where the timesystem is defined
         dict   nodes_data : dictionary containing data from excel scenario file
         

      --------------

      Return values
         
         dict esys : oemof energy system
        

import_scenario()
-------------------------------------------------

.. container:: memitem

   .. container:: memproto

      ===================================================================
      def program_files.create_energy_system.import_scenario (*filepath*) 
      ===================================================================

   .. container:: memdoc

      Imports data from a spreadsheet scenario file.

      The excel sheet has to contain the following sheets:

      -  timesystem
      -  buses
      -  transformers
      -  sinks
      -  sources
      -  storages
      -  powerlines
      -  time_series

      --------------

      Parameters
         
         String filename : path to excel scenario file
         

      --------------

      Return values
         
         dict nodes_data : dictionary containing data from excel scenario file
         