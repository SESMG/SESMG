"""
    @author: GregorBecker - gregor.becker@fh-muenster.de
"""

import os
from datetime import datetime
import logging
from program_files.GUI_st.GUI_st_global_functions import run_SESMG
from program_files.postprocessing.pareto_curve_plotting \
    import collect_pareto_data
from program_files.postprocessing.plotting \
    import create_sink_differentiation_dict
from program_files.postprocessing.plotting_elec_amounts \
    import collect_electricity_amounts
from program_files.postprocessing.plotting_heat_amounts \
    import collect_heat_amounts
from program_files.preprocessing.create_energy_system \
    import import_scenario
import pandas


def create_scenario_save_folder(model_definition, directory: str,
                                limit=""):
    """
    
        :param model_definition: file path of the model definition to \
            be optimized
        :type model_definition: str
        :param directory: file path of the main save path
        :type directory: str
        :param limit: str which is appended on the model name to \
            identify the pareto runs
        :type limit: str
    """
    # set the save path
    if type(model_definition) == str:    
        model_name = model_definition.split("/")[-1][:-5]
    else: 
        model_name = model_definition.name.split("/")[-1][:-5]
    if limit:
        model_name = model_name + "_" + limit
    save_path = str(directory + "/" + model_name
                    + str(datetime.now().strftime("_%Y-%m-%d--%H-%M-%S")))
    os.mkdir(save_path)
    return save_path

        
def calc_constraint_limits(result_folders: dict, limits: list):
    """
    
        :param result_folders: dictionary holding the result paths of \
            monetary and emission minimum
        :type result_folders: dict
        :param limits: list holding the pareto points to be optimized
        :type limits: list
    """
    constraints = {}
    # get constraints of the first optimization
    result = pandas.read_csv(str(result_folders["0"][0]) + "/components.csv")
    constr_min_1 = float(sum(result["constraints/CU"]))
    # get constraints of the second optimization
    result2 = pandas.read_csv(str(result_folders["1"][0]) + "/components.csv")
    constr_min_2 = float(sum(result2["variable costs/CU"])
                         + sum(result2["periodical costs/CU"]))
    # devide solvable range in "limits" intervals
    for i in limits:
        constraints.update({i: constr_min_1 - float(
            constr_min_1 - constr_min_2) * float(i)})
    return constraints


def create_transformation_model_definitions(constraints: dict,
                                            model_name, directory: str,
                                            limits: list):
    """
    
        :param constraints: list containing the maximum emissions \
            caused by the model definitions which will be created \
            within this method
        :type constraints: list
        :param model_name:
        :type model_name:
        :param directory: str containing the path of the directory \
            where the created model definitions will be saved
        :type directory: str
        :param limits: list containing the percentages of reduction \
            defined within the GUI
        :type limits: list
    """
    files = {}
    for limit in limits:
        files.update({str(limit): []})
    
    for limit in limits:
        constraint = constraints[limit]
        xls = pandas.ExcelFile(model_name)
        nd = {
            "buses": xls.parse("buses"),
            "energysystem": xls.parse("energysystem"),
            "sinks": xls.parse("sinks"),
            "links": xls.parse("links"),
            "sources": xls.parse("sources"),
            "time series": xls.parse("time series"),
            "transformers": xls.parse("transformers"),
            "storages": xls.parse("storages"),
            "weather data": xls.parse("weather data"),
            "competition constraints": xls.parse("competition constraints"),
            "insulation": xls.parse("insulation"),
            "district heating": xls.parse("district heating"),
            "pipe types": xls.parse("pipe types")
        }
        file_name = directory \
            + "/" \
            + model_name.name[:-5] \
            + "_" \
            + str(limit) + ".xlsx"
        files[str(limit)].append(file_name)
        writer = pandas.ExcelWriter(file_name, engine="xlsxwriter")
        nd["energysystem"].loc[1, "constraint cost limit"] = float(constraint)
        for i in nd.keys():
            nd[i].to_excel(writer, sheet_name=str(i), index=False)
        writer.save()
        print(files)
    return files


def run_pareto(limits: list, 
               model_definition,
               GUI_main_dict: dict):
    """
    
        :param limits: list containing the percentages of reduction \
            defined within the GUI
        :type limits: list
        :param model_definition: file path of the model definition to \
            be optimized
        :type model_definition: str
        :param GUI_main_dict: dictionary containing
            
            pre_modeling
            num_threads
            time series params
            graph state
            xlsx select state
            console select state
            solver select
            dh path
            cluster dh
            pre modeling time series params
            investment boundaries
            investment boundaries factor
            pre model path
            
        :type GUI_main_dict
    """
    # create one directory to collect all runs
    directory = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "results/" + datetime.now().strftime("%Y-%m-%d--%H-%M-%S"),
    )
    os.mkdir(directory)
    
    logging.info("Optimiztation of the following runs"
                 + str(limits)
                 + "started!")
    
    # FIRST CRITERION
    result_folders = {"0": []}
    # TODO enable more than one scenario (districts)
    save_path = create_scenario_save_folder(model_definition, directory, "0")
    # append optimum of first criterion driven run to the list of
    # result folders
    result_folders["0"].append(save_path)
    # run the optimization of the first criterion minimum
    run_SESMG(GUI_main_dict, model_definition, save_path)
    
    # SECOND CRITERION
    # TODO enable more than one scenario (districts)
    # set the save path
    save_path2 = create_scenario_save_folder(model_definition, directory, "1")
    # append optimum of first criterion driven run to the list of
    # result folders
    result_folders.update({"1": [save_path2]})
    
    # switch the criterion switch parameter in the gui input parameter
    GUI_main_dict["input_criterion_switch"] = \
        not GUI_main_dict["input_criterion_switch"]
    # run the optimization of the second criterion minimum
    run_SESMG(GUI_main_dict, model_definition, save_path2)
    
    # SEMI OPTIMAL OPTIMIZATION
    # calculate the emission limits for the semi optimal model definitions
    constraints = calc_constraint_limits(result_folders, limits)
    # create the new model definitions with specific constraint limits
    files = create_transformation_model_definitions(
        constraints, model_definition, directory, limits)

    # switch the criterion switch parameter in the gui input parameter
    GUI_main_dict["input_criterion_switch"] = \
        not GUI_main_dict["input_criterion_switch"]
    
    # run the semi optimal optimizations
    for limit in limits:
        result_folders.update({str(limit): []})
        for model_definition in files[str(limit)]:
            save_path = create_scenario_save_folder(model_definition,
                                                    directory)
            result_folders[str(limit)].append(save_path)
            run_SESMG(GUI_main_dict, model_definition, save_path)
            
    result_dfs = {}
    for folder in result_folders:
        result_dfs.update(
            {folder: pandas.read_csv(result_folders[folder][0]
                                     + "/components.csv")})
    
    # create csv file for pareto plotting
    collect_pareto_data(
        result_dfs=dict(sorted(result_dfs.items(), reverse=True)),
        result_path=os.path.dirname(save_path))
    
    sink_types = create_sink_differentiation_dict(
            import_scenario(model_definition)["sinks"])
    
    # create amount csv files
    collect_electricity_amounts(dataframes=result_dfs,
                                nodes_data=import_scenario(model_definition),
                                result_path=os.path.dirname(save_path),
                                sink_known=sink_types)

    collect_heat_amounts(dataframes=result_dfs,
                         nodes_data=import_scenario(model_definition),
                         result_path=os.path.dirname(save_path),
                         sink_known=sink_types)
    
    return directory
