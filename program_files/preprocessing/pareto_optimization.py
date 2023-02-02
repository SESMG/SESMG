import os
from datetime import datetime
import logging
from program_files.preprocessing.Spreadsheet_Energy_System_Model_Generator \
    import sesmg_main, sesmg_main_including_premodel
import pandas


def create_scenario_save_folder(model_definition: str, directory: str,
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
    model_name = os.path.basename(model_definition)[:-5]
    if limit:
        model_name = model_name + "_" + limit
    save_path = str(directory + "/" + model_name
                    + str(datetime.now().strftime("_%Y-%m-%d--%H-%M-%S")))
    os.mkdir(save_path)
    return save_path


def run_SESMG(gui_input_run_parameter: dict,
              model_definition: str, save_path: str):
    """
    
        :param gui_input_run_parameter: TODO ...
        :type gui_input_run_parameter: dict
        :param model_definition: file path of the model definition to \
            be optimized
        :type model_definition: str
        :param save_path: file path where the results will be saved
        :type save_path: str
    """
    
    if gui_input_run_parameter["criterion_switch"]:
        criterion_switch = True
    else:
        criterion_switch = False
    if not gui_input_run_parameter["pre_modeling"]:
        sesmg_main(
            scenario_file=model_definition,
            result_path=save_path,
            num_threads=gui_input_run_parameter["num_threads"],
            timeseries_prep=gui_input_run_parameter["timeseries_prep_param"],
            graph=gui_input_run_parameter["graph_state"],
            criterion_switch=criterion_switch,
            xlsx_results=gui_input_run_parameter["xlsx_select_state"],
            console_results=gui_input_run_parameter["console_select_state"],
            solver=gui_input_run_parameter["solver_select"],
            district_heating_path=gui_input_run_parameter["dh_path"],
            cluster_dh=gui_input_run_parameter["cluster_dh"])
    
    # If pre-modeling is activated a second run will be carried out
    else:
        sesmg_main_including_premodel(
            scenario_file=model_definition,
            result_path=save_path,
            num_threads=gui_input_run_parameter["num_threads"],
            timeseries_prep=gui_input_run_parameter[
                "timeseries_prep_param"],
            graph=gui_input_run_parameter["graph_state"],
            criterion_switch=criterion_switch,
            xlsx_results=gui_input_run_parameter["xlsx_select_state"],
            console_results=gui_input_run_parameter[
                "console_select_state"],
            solver=gui_input_run_parameter["solver_select"],
            district_heating_path=gui_input_run_parameter["dh_path"],
            cluster_dh=gui_input_run_parameter["cluster_dh"],
            pre_model_timeseries_prep=gui_input_run_parameter["pre_modeling_timeseries_prep_param"],
            investment_boundaries=gui_input_run_parameter["investment_boundaries"],
            investment_boundary_factor=gui_input_run_parameter["investment_boundary_factor"],
            pre_model_path=gui_input_run_parameter["pre_model_path"]
        )
        
        
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
    result = pandas.read_csv(str(result_folders["1"][0]) + "/components.csv")
    constr_min_1 = float(sum(result["constraints/CU"]))
    # get constraints of the second optimization
    result2 = pandas.read_csv(str(result_folders["0"][0]) + "/components.csv")
    constr_min_2 = float(sum(result2["variable costs/CU"])
                         + sum(result2["periodical costs/CU"]))
    # devide solvable range in "limits" intervals
    for i in limits:
        constraints.update({i: constr_min_1 - float(
            constr_min_1 - constr_min_2) * float(i)})
    return constraints


def create_transformation_model_definitions(constraints: dict,
                                            model_name: str, directory: str,
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
            + model_name.split("/")[-1][:-5] \
            + "_" \
            + str(limit) + ".xlsx"
        files[str(limit)].append(file_name)
        writer = pandas.ExcelWriter(file_name, engine="xlsxwriter")
        nd["energysystem"].loc[1, "constraint cost limit"] = float(constraint)
        for i in nd.keys():
            nd[i].to_excel(writer, sheet_name=str(i), index=False)
        writer.save()
    return files


def run_pareto(limits: list, model_definition: str,
               gui_input_run_parameter: dict):
    """
    
        :param limits: list containing the percentages of reduction \
            defined within the GUI
        :type limits: list
        :param model_definition: file path of the model definition to \
            be optimized
        :type model_definition: str
        
        :param gui_input_run_parameter: dictionary containing
            
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
    result_folders = {"1": []}
    # TODO enable more than one scenario (districts)
    save_path = create_scenario_save_folder(model_definition, directory)
    # append optimum of first criterion driven run to the list of
    # result folders
    result_folders["1"].append(save_path)
    # run the optimization of the first criterion minimum
    run_SESMG(gui_input_run_parameter, model_definition, save_path)
    
    # SECOND CRITERION
    # TODO enable more than one scenario (districts)
    # set the save path
    save_path2 = create_scenario_save_folder(model_definition, directory, "0")
    # append optimum of first criterion driven run to the list of
    # result folders
    result_folders.update({"0": [save_path2]})
    
    # switch the criterion switch parameter in the gui input parameter
    gui_input_run_parameter["criterion_switch"] = \
        not gui_input_run_parameter["criterion_switch"]
    # run the optimization of the second criterion minimum
    run_SESMG(gui_input_run_parameter, model_definition, save_path2)
    
    # SEMI OPTIMAL OPTIMIZATION
    # calculate the emission limits for the semi optimal model definitions
    constraints = calc_constraint_limits(result_folders, limits)
    # create the new model definitions with specific constraint limits
    files = create_transformation_model_definitions(
        constraints, model_definition, directory, limits)

    # switch the criterion switch parameter in the gui input parameter
    gui_input_run_parameter["criterion_switch"] = \
        not gui_input_run_parameter["criterion_switch"]
    
    # run the semi optimal optimizations
    for limit in limits:
        result_folders.update({str(limit): []})
        for model_definition in files[limit]:
            save_path = create_scenario_save_folder(model_definition,
                                                    directory)
            result_folders[str(limit)].append(save_path)
            run_SESMG(gui_input_run_parameter, model_definition, save_path)
            
    return result_folders
