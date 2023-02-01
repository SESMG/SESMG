#!/usr/bin/env python3# -*- coding: utf-8 -*-"""Created on Fri Jan 27 13:23:07 2023@author: jtock - jan.tockloth@fh-muenster.de"""import json########################################### Global GUI functions ###########################################def import_GUI_input_values_json(json_file_path):     """        :param json_file_path: file name to the underlying json with input values for all GUI pages        :type json_file_path: str        :param GUI_settings_cache_dict_reload: exported dict from json file including a (sub)dict for every GUI page        :type json_file_name: dict    """    #Import json file including several (sub)dicts for every GUI page     #Each (sub)dict includes input values as a cache from the last session    with open(json_file_path, "r") as infile:        GUI_settings_cache_dict_reload = json.load(infile)            return GUI_settings_cache_dict_reloaddef safe_GUI_input_values(input_values_dict, json_file_path):    """    Function so safe a dict as json        :param input_values_sub_dict: name of the dict of input values for specific GUI page        :type input_values_dict: dict        :param json_file_path: file name to the underlying json with input values        :type json_file_path: str    """    with open(json_file_path, 'w') as outfile:        json.dump(input_values_dict, outfile, indent=4)                def clear_GUI_input_values(input_values_dict, name_sub_dict, json_file_path):    """        :param input_values_sub_dict: name of the dict of input values for specific GUI page        :type input_values_dict: dict        :param name_sub_dict: name of the subdict in the json-file can be "main_page", "udu_page", "result_page", or "test_page"        :type name_sub_dict: str        :param json_file_path: file name to the underlying json with input values        :type json_file_path: str    """    #Clearing the GUI input values of the subdict / GUI page    input_values_dict_cleared = dict.fromkeys(input_values_dict, "")        #Saving the updates GUI dicts    updated_GUI_dict = safe_GUI_input_values(input_values_dict_cleared, 'GUI_test_setting_cache.json')                                  return updated_GUI_dictdef create_safe_GUI_main_settings_dict(result_path,                             premodeling_result_path,                             num_threads,                             input_timeseries_algorithm_index,                             input_timeseries_cluster_index_index,                             input_timeseries_criterion_index,                             input_timeseries_period_index,                             input_timeseries_season_index,                             graph,                             criterion_switch,                             xlsx_results,                             console_results,                             input_solver_index,                             cluster_dh,                             input_premodeling_invest_boundaries,                             input_premodeling_tightening_factor,                             input_premodeling_timeseries_algorithm_index,                             input_premodeling_timeseries_cluster_index_index,                             input_premodeling_timeseries_criterion_index,                             input_premodeling_timeseries_period_index,                             input_premodeling_timeseries_season_index,                             input_pareto_points,                             json_file_path):        """    Function to create an dict with all GUI settings as an preparation to safe dem             :param result_path: internal path where the latest results were safed        :type result_path: str          :param premodeling_result_path: internal path where the latest premodelling results were safed        :type premodeling_result_path: str          :param num_threads: chosen number of theads to use        :type num_threads: int              :param input_timeseries_algorithm_index: chosen timeseries algorithm as an index created with timeseries_algorithm_dict        :type input_timeseries_algorithm_index: int          :param input_timeseries_cluster_index_index: chosen timeseries cluster index as an index created with timeseries_index_range_values        :type input_timeseries_cluster_index_index: int          :param input_timeseries_criterion_index: chosen timeseries criterion as an index created with timeseries_cluster_criteria_dict        :type input_timeseries_criterion_index: int          :param input_timeseries_period_index: chosen timeseries period as an index created with input_timeseries_period_dict        :type input_timeseries_period_index: int          :param input_timeseries_season_index: chosen timeseries season as an index created with input_timeseries_season_dict        :type input_timeseries_season_index: int          :param graph: chosen if graph png should be created        :type graph: bool          :param criterion_switch: chosen if criterion switch should be active for pareto optimization        :type criterion_switch: bool          :param xlsx_results: chosen if results slsx should be created        :type xlsx_results: bool              :param console_results: ?????????????????????????????????????????????????????        :type console_results: bool          :param input_solver_index: chosen timeseries season as an index created with input_solver_dict        :type input_solver_index: int          :param cluster_dh: ?????????????????????????????????????????????????????        :type cluster_dh: bool          :param input_activate_premodeling: chosen if premodelling should be used        :type input_activate_premodeling: bool         :param input_premodeling_invest_boundaries: chosen if investment boundaries in premodelling should be used        :type input_premodeling_invest_boundaries: bool              :param input_premodeling_tightening_factor: chosen which investment tightening factor in premodelling should be used        :type input_premodeling_tightening_factor: int          :param input_premodeling_timeseries_algorithm_index: chosen timeseries algorithm as an index created with timeseries_algorithm_dict        :type input_premodeling_timeseries_algorithm_index: int          :param input_premodeling_timeseries_cluster_index_index: chosen timeseries cluster index as an index created with timeseries_index_range_values        :type input_premodeling_timeseries_cluster_index_index: int          :param input_premodeling_timeseries_criterion_index: chosen timeseries criterion as an index created with timeseries_cluster_criteria_dict        :type input_premodeling_timeseries_criterion_index: int          :param input_premodeling_timeseries_period_index: chosen timeseries period as an index created with input_timeseries_period_dict        :type input_premodeling_timeseries_period_index: int              :param input_premodeling_timeseries_season_index: chosen timeseries season as an index created with input_timeseries_season_dict        :type input_premodeling_timeseries_season_index: int          :param input_pareto_points: chosen pareto points which will be generated         :type input_pareto_points: list          :param json_file_path: internal path where json should be safed         :type json_file_path: str      """        # creating the dict of GUI input values to be safed as json    input_values_dict = {"result_path": result_path,                         "premodeling_result_path": premodeling_result_path,                         "num_threads": num_threads,                         "input_timeseries_algorithm_index": input_timeseries_algorithm_index,                         "input_timeseries_cluster_index_index": input_timeseries_cluster_index_index,                         "input_timeseries_criterion_index": input_timeseries_criterion_index,                         "input_timeseries_period_index": input_timeseries_period_index,                         "input_timeseries_season_index": input_timeseries_season_index,                         "graph": graph,                         "criterion_switch": criterion_switch,                         "xlsx_results": xlsx_results,                         "console_results": console_results,                         "input_solver_index": input_solver_index,                         "cluster_dh": cluster_dh,                         "input_premodeling_invest_boundaries": input_premodeling_invest_boundaries,                         "input_premodeling_tightening_factor": input_premodeling_tightening_factor,                         "input_premodeling_timeseries_algorithm_index": input_premodeling_timeseries_algorithm_index,                         "input_premodeling_timeseries_cluster_index_index": input_premodeling_timeseries_cluster_index_index,                         "input_premodeling_timeseries_criterion_index": input_premodeling_timeseries_criterion_index,                         "input_premodeling_timeseries_period_index": input_premodeling_timeseries_period_index,                         "input_premodeling_timeseries_season_index": input_premodeling_timeseries_season_index,                         "input_pareto_points": input_pareto_points                         }    # safe dict in GUI_cache.json using predefined function    safe_GUI_input_values(input_values_dict=input_values_dict, json_file_path=json_file_path)    def clear_GUI_main_settings(result_path, premodeling_result_path, json_file_path):         """    Function to clear the  GUI settings dict and safe in json path as variables        :param result_path: internal path where the latest results were safed        :type result_path: str          :param premodeling_result_path: internal path where the latest premodelling results were safed        :type premodeling_result_path: str          :param json_file_path: internal path where json should be safed         :type json_file_path: str      """        # creating the dict of GUI input values to be safed as json    create_safe_GUI_main_settings_dict(result_path=result_path,                                       premodeling_result_path=premodeling_result_path,                                       num_threads=1,                                       input_timeseries_algorithm_index=0,                                       input_timeseries_cluster_index_index=0,                                       input_timeseries_criterion_index=0,                                       input_timeseries_period_index=0 ,                                        input_timeseries_season_index=0 ,                                       graph=False,                                       criterion_switch=False,                                       xlsx_results=False,                                       console_results=False,                                       input_solver_index=0,                                       cluster_dh=False,                                       input_premodeling_invest_boundaries=False,                                       input_premodeling_tightening_factor=1,                                       input_premodeling_timeseries_algorithm_index=0,                                       input_premodeling_timeseries_cluster_index_index=0,                                       input_premodeling_timeseries_criterion_index=0,                                       input_premodeling_timeseries_period_index=0,                                       input_premodeling_timeseries_season_index=0,                                       input_pareto_points=[],                                       json_file_path=json_file_path)                