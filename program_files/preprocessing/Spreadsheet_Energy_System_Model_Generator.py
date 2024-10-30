# -*- coding: utf-8 -*-
"""
    Spreadsheet-Energy-System-Model-Generator.
    
    creates an energy system from a given spreadsheet data file, solves
    it for the purpose of least cost optimization, and returns the
    optimal model definition results.
    
    --------------------------------------------------------------------
    
    Christian Klemm - christian.klemm@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
"""
import logging
import pandas as pd
from oemof.tools import logger
import os
from threading import *
from program_files.preprocessing import (create_energy_system,
                                         data_preparation,
                                         pareto_optimization)
from program_files.preprocessing.components import (
    district_heating, Bus, Source, Sink, Transformer, Storage, Link)
from program_files.preprocessing.create_graph import ESGraphRenderer
from program_files.postprocessing import create_results
from program_files.postprocessing.calculate_lca_results import calculate_lca_results_function, add_uuid_to_components, \
    consider_var_cost_factor
from program_files.processing import optimize_model
from program_files.preprocessing.pre_model_analysis import \
    update_model_according_pre_model_results


def call_district_heating_creation(nodes_data: dict, nodes: list, busd: dict,
                                   district_heating_path: str,
                                   result_path: str, cluster_dh: bool
                                   ) -> (dict, list):
    """
    
        :param nodes_data:
        :type nodes_data: dict
        :param nodes:
        :type nodes: list
        :param busd:
        :type busd: dict
        :param district_heating_path:
        :type district_heating_path: str
        :param result_path:
        :type result_path: str
        :param cluster_dh:
        :type cluster_dh: bool
        
        :return: - **nodes** (list) -
                 - **busd** (dict) -
    """
    # get the model definition's buses sheet content
    buses = nodes_data["buses"]
    # get only the active pipe types
    pipe_types = nodes_data["pipe types"].query("active == 1")
    
    # check if at least one bus can possibly be connected to the
    # exergy heating net
    if len(buses[~buses["district heating conn. (exergy)"].isin(["0", 0])]):
        # check if at least one pipe is meant to be used within an
        # exergy network
        if len(pipe_types.query("`anergy or exergy` == 'exergy'")):
            # creates the thermal network components as defined in
            # the model definition file and adds them to the list
            # of components (nodes)
            nodes, busd = district_heating.district_heating(
                nodes_data=nodes_data,
                nodes=nodes, busd=busd,
                district_heating_path=district_heating_path,
                result_path=result_path,
                cluster_dh=cluster_dh,
                is_exergy=True
            )
            
    # check if at least one bus can possibly be connected to the
    # anergy heating net
    if len(buses[~buses["district heating conn. (anergy)"].isin(["0", 0])]):
        # check if at least one pipe is meant to be used within an
        # anergy network
        if len(pipe_types.query("`anergy or exergy` == 'anergy'")):
            # creates the thermal network components as defined in the
            # model definition file and adds them to the list of
            # components (nodes)
            nodes, busd = district_heating.district_heating(
                nodes_data=nodes_data,
                nodes=nodes,
                busd=busd,
                district_heating_path=district_heating_path,
                result_path=result_path,
                cluster_dh=cluster_dh,
                is_exergy=False
            )
            
    return busd, nodes


def sesmg_main(model_definition_file: str, result_path: str, num_threads: int,
               criterion_switch: bool, xlsx_results: bool,
               console_results: bool, lca_results: bool, timeseries_prep: list, solver: str,
               cluster_dh, graph=False, district_heating_path=None) -> None:
    """
        Main function of the Spreadsheet System Model Generator

        :param model_definition_file: The model definition file must \
            contain the components specified above.
        :type model_definition_file: str ['xlsx']
        :param result_path: path of the folder where the results will \
            be saved
        :type result_path: str ['folder']
        :param num_threads: number of threads that the method may use
        :type num_threads: int
        :param criterion_switch: boolean which decides rather the \
            first and second optimization criterion will be switched \
            (True) or not (False)
        :type criterion_switch: bool
        :param xlsx_results: boolean which decides rather a flow \
            Spreadsheet will be created for each bus of the energy \
            system after the optimization (True) or not (False)
        :type xlsx_results: bool
        :param console_results: boolean which decides rather the \
            energy system's results will be printed in the console \
            (True) or not (False)
        :type console_results: bool
        :param timeseries_prep: list containing the attributes \
            necessary for timeseries simplifications
        :type timeseries_prep: list
        :param solver: str holding the user chosen solver
        :type solver: str
        :param cluster_dh: boolean which decides rather the district \
            heating components are clustered street wise (True) or not \
            (False)
        :type cluster_dh: bool
        :param graph: defines if the graph should be created
        :type graph: bool
        :param district_heating_path: path to the folder where already \
            calculated district heating data is stored
        :type district_heating_path: str['folder']
        :param lca_results boolean which decides weather additional lca \
            should be calculated or not
        :type lca_results: bool
    """
    # sets number of threads for numpy
    os.environ['NUMEXPR_NUM_THREADS'] = str(num_threads)
    # defines a logging file
    logger.define_logging(logpath=result_path)
    # imports data from the excel file and returns it as a dictionary
    nodes_data = create_energy_system.import_model_definition(
            filepath=model_definition_file)
    
    # if the user has chosen two switch the optimization criteria the
    # nodes data dict is adapted
    if criterion_switch:
        pareto_optimization.change_optimization_criterion(
                nodes_data=nodes_data)
    
    # Timeseries Preprocessing
    variable_cost_factor = data_preparation.timeseries_preparation(
            timeseries_prep_param=timeseries_prep,
            nodes_data=nodes_data,
            result_path=result_path)
    
    if timeseries_prep[0] != 'none':
        model_definition_file = result_path + "/modified_model_definition.xlsx"
    
    # created an energysystem as defined in the model definition file
    esys, nodes_data = create_energy_system.define_energy_system(
            nodes_data=nodes_data)
    
    # creates bus objects, excess sinks, and shortage sources as defined
    # in the model definition file buses sheet
    busd, nodes = Bus.buses(nd_buses=nodes_data["buses"], nodes=[])
    
    busd, nodes = call_district_heating_creation(
        nodes_data=nodes_data,
        nodes=nodes,
        busd=busd,
        district_heating_path=district_heating_path,
        result_path=result_path,
        cluster_dh=cluster_dh
    )
    
    # PARALLEL CREATION OF ALL OBJECTS OF THE MODEL DEFINITION FILE
    
    # creates source objects as defined in the model definition file and
    # adds them to the list of components (nodes)
    thread1 = Thread(target=Source.Sources, args=(nodes_data, nodes, busd))
    thread1.start()
    # created sink objects as defined in the model definition file and
    # adds them to the list of components (nodes)
    thread2 = Thread(target=Sink.Sinks, args=(nodes_data, busd, nodes))
    thread2.start()
    # creates transformer objects as defined in the model definition
    # file and adds them to the list of components (nodes)
    thread3 = Thread(target=Transformer.Transformers,
                     args=(nodes_data, nodes, busd))
    thread3.start()
    # creates storage objects as defined in the model definition file
    # and adds them to the list of components (nodes)
    thread4 = Thread(target=Storage.Storages, args=(nodes_data, nodes, busd))
    thread4.start()
    # creates link objects as defined in the model definition file and
    # adds them to the list of components (nodes)
    thread5 = Thread(target=Link.Links, args=(nodes_data, nodes, busd))
    thread5.start()
    
    # wait until the threads have done their tasks
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread5.join()
    
    # adds the created components to the energy system created in the
    # beginning of this method
    esys.add(*nodes)
    
    # creates the energy system graph
    ESGraphRenderer(energy_system=esys, filepath=result_path, view=graph,
                    legend=True)
    
    # optimizes the energysystem and returns the optimized energy system
    om = optimize_model.least_cost_model(
            energy_system=esys, num_threads=num_threads, nodes_data=nodes_data,
            busd=busd, solver=solver
    )
    
    # shows and saves results iof the optimized model / postprocessing
    if xlsx_results:
        create_results.xlsx(nodes_data=nodes_data, optimization_model=om,
                            filepath=result_path)
    
    # creates the data used for the results presentation in the GUI
    results_instance = create_results.Results(
            nodes_data=nodes_data, optimization_model=om, energy_system=esys,
            result_path=result_path, console_log=console_results,
            cluster_dh=cluster_dh)
    
    logging.info('\t ' + 56 * '-')
    logging.info('\t Modelling and optimization successfully completed!')

    # calculates additional lca results
    components_list = results_instance.components_list

    # check whether a lca analysis should be added
    if lca_results:

        # add the uuids to the components_list at the right place
        components_list = add_uuid_to_components(nodes_data, components_list)

        # scale results with the var_cost_factor
        components_list = consider_var_cost_factor(components_list, variable_cost_factor)

        # calculate results
        calculate_lca_results_function(path=result_path, components=components_list)


def sesmg_main_including_premodel(
        model_definition_file: str, result_path: str, num_threads: int,
        graph: bool, criterion_switch: bool, xlsx_results: bool,
        console_results: bool, timeseries_prep: list, solver: str,
        cluster_dh, pre_model_timeseries_prep: list,
        investment_boundaries: bool, investment_boundary_factor: int,
        district_heating_path=None) -> None:
    """
         This method solves the specified model definition file is
         solved twice. First with the pre-model time series preparatory
         attributes selected by the user. And then (after the
         pre-modeling algorithm has been performed and the model
         definition has been reduced to the invested components) the
         model definition is solved with the main time series
         preparation algorithms.
         
        :param model_definition_file: The model_definition_file must \
            contain the components specified above.
        :type model_definition_file: str ['xlsx']
        :param result_path: path of the folder where the results
                            will be saved
        :type result_path: str ['folder']
        :param num_threads: number of threads that the method may use
        :type num_threads: int
        :param criterion_switch: boolean which decides rather the \
            first and second optimization criterion will be switched \
            (True) or not (False)
        :type criterion_switch: bool
        :param xlsx_results: boolean which decides rather a flow \
            Spreadsheet will be created for each bus of the energy \
            system after the optimization (True) or not (False)
        :type xlsx_results: bool
        :param console_results: boolean which decides rather the \
            energy system's results will be printed in the console \
            (True) or not (False)
        :type console_results: bool
        :param timeseries_prep: list containing the attributes \
            necessary for timeseries simplifications
        :type timeseries_prep: list
        :param pre_model_timeseries_prep: list containing the \
            attributes necessary for timeseries simplifications of the \
            first optimization run which is used to reduced the model \
            definition's amount of components.
        :type pre_model_timeseries_prep: list
        :param investment_boundaries: Indicates whether "tightening of \
            technical boundaries", i.e. limiting of investment limits \
            based on the pre-model, is executed.
        :type investment_boundaries: bool
        :param investment_boundary_factor: Factor by which investment \
            decisions of the pre-model are multiplied to limit the \
            investment limits in the main model.
        :type investment_boundary_factor: int
        :param solver: str holding the user chosen solver
        :type solver: str
        :param cluster_dh: boolean which decides rather the district \
            heating components are clustered street wise (True) or not \
            (False)
        :type cluster_dh: bool
        :param graph: defines if the graph should be created
        :type graph: bool
        :param district_heating_path: path to the folder where already \
            calculated district heating data is stored
        :type district_heating_path: str['folder']
    """
    # Create Sub-Folders in the results-repository
    os.mkdir(result_path + str('/pre_model'))
    # Start Pre-Modeling Run
    logging.info('STARTING PRE-MODEL')
    logging.info('Pre-modeling results will be stored in: '
                 + result_path + str('/pre_model'))
    
    # starting the optimization of the model definition with timeseries
    # preparation parameters used for model simplification
    sesmg_main(
            model_definition_file=model_definition_file,
            result_path=result_path + str('/pre_model'),
            num_threads=num_threads,
            timeseries_prep=pre_model_timeseries_prep,
            graph=graph,
            criterion_switch=criterion_switch,
            xlsx_results=xlsx_results,
            console_results=console_results,
            solver=solver,
            district_heating_path=district_heating_path,
            cluster_dh=cluster_dh,
            lca_results=False)
    
    # create updated model definition for main-modeling run
    logging.info('UPDATING DATA BASED ON PRE-MODEL RESULTS')
    update_model_according_pre_model_results(
            model_definition_path=model_definition_file,
            results_components_path=result_path + '/pre_model/components.csv',
            updated_model_definition_path=result_path +
                                          '/updated_scenario.xlsx',
            investment_boundary_factor=investment_boundary_factor,
            investment_boundaries=investment_boundaries)
    
    # start main-modeling run
    logging.info('STARTING MAIN-MODEL')
    
    sesmg_main(
            model_definition_file=result_path + '/updated_scenario.xlsx',
            result_path=result_path,
            num_threads=num_threads,
            timeseries_prep=timeseries_prep,
            graph=graph,
            criterion_switch=criterion_switch,
            xlsx_results=xlsx_results,
            console_results=console_results,
            solver=solver,
            district_heating_path=district_heating_path,
            cluster_dh=cluster_dh,
            lca_results=False)
