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
         
charts()
-------------------------------------------------

.. container:: memitem

   .. container:: memproto

      =============================================================================================
      def program_files.create_results.charts (*nodes_data*, *optimization_model*, *energy_system*)   
      =============================================================================================

   .. container:: memdoc

      Plots model results.

      Plots the in- and outgoing flows of every bus of a given,
      optimized energy system

      --------------

      Parameters
         
          obj:'dict' nodes_data : dictionary containing data from excel scenario file    
          obj:'oemof.solph.models.Model' optimization_model: optimized energy system                     
          obj energy_system: original (unoptimized) energy system        

      --------------

      Return values
         
          plots plots displaying in and outgoing flows of the energy systems' buses.    
        

prepare_plotly_results()
-------------------------------------------------

.. container:: memitem

   .. container:: memproto

     ====================================================================================================
      def program_files.create_results.prepare_plotly_results (*nodes_data*, *optimization_model*, *energy_system*, *result_path*)
	 ====================================================================================================
   .. container:: memdoc

      Function which prepares the results for the creation of a HTML
      page.

      Creates three pandas data frames and saves them, which are
      required for creating an interactive HTML result page:

      -  df_list_of_components: Consists all components with several
         properties
      -  df_result_table: Consists timeseries of al components
      -  df_summary: Consists summarizing results of the modelling

      --------------

      Parameters
         
         obj:'dict' nodes_data: dictionary containing data from excel scenario file      
         obj:'oemof.solph.models.Model' optimization_model: optimized energy system                    
		 objenergy_system: original (unoptimized) energy system
         String result_path: path, where the data frames shall be saved as csv-file  


statistics()
-------------------------------------------------

.. container:: memitem

   .. container:: memproto

      =================================================================================================
      def program_files.create_results.statistics (*nodes_data*, *optimization_model*, *energy_system*)   	  =================================================================================================

   .. container:: memdoc

      Returns a list of all defined components with the following
      information:

      +--------------+------------------------------------------------------+
      | component    | information                                          |
      +==============+======================================================+
      | sinks        | Total Energy Demand                                  |
      +--------------+------------------------------------------------------+
      | sources      | Total Energy Input, Max. Capacity, Variable Costs,   |
      |              | Periodical Costs                                     |
      +--------------+------------------------------------------------------+
      | transformers | Total Energy Output, Max. Capacity, Variable Costs,  |
      |              | Investment Capacity, Periodical Costs                |
      +--------------+------------------------------------------------------+
      | storages     | Energy Output, Energy Input, Max. Capacity, Total    |
      |              | variable costs, Investment Capacity, Periodical      |
      |              | Costs                                                |
      +--------------+------------------------------------------------------+
      | links        | Total Energy Output                                  |
      +--------------+------------------------------------------------------+

      Furthermore, a list of recommended investments is printed.

      --------------

      Parameters
         
         obj:'dict' nodes_data: dictionary containing data from excel scenario file 
         obj:'oemof.solph.models.Model' optimization_model: optimized energy system                      
         obj energy_system: original (unoptimized) energy system 
        

xlsx()
-------------------------------------------------

.. container:: memitem

   .. container:: memproto

      =======================================================================================================
      def program_files.create_results.xlsx (*nodes_data*, *optimization_model*, *energy_system*, *filepath*)       =======================================================================================================

   .. container:: memdoc

      Returns model results as xlsx-files.

      Saves the in- and outgoing flows of every bus of a given,
      optimized energy system as .xlsx file

      --------------

      Parameters
         
         dict nodes_data : dictionary containing data from excel scenario file         
         obj:'oemof.solph.models.Model' optimization_model: optimized energy system        
         obj energy_system: original (unoptimized) energy system    
         String filepath: path, where the results will be stored 
         
      --------------

      Return values
         
         obj'.xlsx' results: xlsx files containing in and outgoing flows of the energy systems' buses.               
