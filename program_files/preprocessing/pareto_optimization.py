"""
    Gregor Becker - gregor.becker@fh-muenster.de
    Christian Klemm - christian.klemm@fh-muenster.de
"""

import os
from datetime import datetime
import logging
import pandas

from program_files.postprocessing.plotting \
    import create_sink_differentiation_dict, collect_pareto_data
from program_files.postprocessing.plotting_elec_amounts \
    import collect_electricity_amounts
from program_files.postprocessing.plotting_heat_amounts \
    import collect_heat_amounts
from program_files.preprocessing.create_energy_system \
    import import_model_definition


def create_model_definition_save_folder(model_definition, directory: str,
                                        limit="") -> str:
    """
        In this method, the folder necessary for a Pareto run
        (name pattern
        <model_definition_name>_<constraint_limit>_<timestamp>) is
        created in the directory. Here, due to the streamlit interface,
        it must be distinguished whether the model_definitions variable
        is a str or the object resulting from the GUI. After creation,
        the path of the newly created folder is returned.

        :param model_definition: file path of the model definition to \
            be optimized
        :type model_definition: str / streamlit.UploadedFile
        :param directory: file path of the main save path
        :type directory: str
        :param limit: str which is appended on the model name to \
            identify the pareto runs
        :type limit: str

        :return: - **save_path** (str) - path where the optimization \
            results of the pareto point will be stored
    """
    # extract the model_name from model_definition file path
    if type(model_definition) == str:
        model_name = model_definition.split("/")[-1][:-5]
    else:
        model_name = model_definition.name.split("/")[-1][:-5]
    # append the limit on the model name if it's not an empty string
    if limit:
        model_name = model_name + "_" + limit
    # create timestamp
    timestamp = str(datetime.now().strftime("_%Y-%m-%d--%H-%M-%S"))
    # create save path
    save_path = str(directory + "/" + model_name + timestamp)
    # make directory for created save path and return it
    os.mkdir(save_path)
    return save_path


def calc_constraint_limits(result_folders: dict, limits: list) -> dict:
    """
        This method reads out the emissions of the monetary-driven
        minimum as well as those of the emissions-driven minimum, which
        narrows down the solvable range (interval width) of the model
        definition. Based on these interval limits, the emission limits
        for the transformation points (as given in the GUI) are
        calculated. Here, 0.2 represented a reduction of 20% of the
        interval width. The optimization will result a result model
        definition which is limited to 80% (equal or lower) of the
        emissions calculated for the monetary minimum model definition.
        Consequently, it is calculated as follows:

        .. math::
            emissions_{mon} =
                \mathrm{emissions~of~monetary~driven~minimum}

            emissions_{emi} =
                \mathrm{emissions~of~emission~driven~minimum}

            \mathrm{interval~width} = emission_{mon} - emission_{min}

            constraints[x] = emissions_{mon} - limits[x] *  \mathrm{interval~width}

        The list of limits is then returned as constraints.

        :param result_folders: dictionary holding the result paths of \
            monetary and emission minimum
        :type result_folders: dict
        :param limits: list holding the pareto points to be optimized
        :type limits: list

        :return: - **constraints** (dict) - dict of constraint limits \
            for the transformation points of the pareto optimization
    """
    constraints = {}
    # get constraints of the first optimization
    result = pandas.read_csv(str(result_folders["0"][0]) + "/components.csv")
    constr_min_1 = float(sum(result["constraints/CU"]))

    # get constraints of the second optimization since it is an emission
    # driven one the costs attribute is summed
    result2 = pandas.read_csv(str(result_folders["1"][0]) + "/components.csv")
    constr_min_2 = float(sum(result2["variable costs/CU"])
                         + sum(result2["periodical costs/CU"]))

    # divide solvable range in "limits" intervals
    for limit in limits:
        interval_width = float(constr_min_1 - constr_min_2)
        constraints.update({limit: constr_min_1 - interval_width * limit})
    return constraints


def create_transformation_model_definitions(
        constraints: dict, model_definition, directory: str, limits: list
) -> dict:
    """
        After the emission limits have been calculated in the
        calc_constraint_limits method, the transformation model
        definitions are now created. For this purpose, the model
        definition entered by the user is imported again and extended
        by the constraint cost limit. Afterwards it is saved in the
        Pareto directory (directory) and the path is attached to the
        dictionary "files". This dictionary also represents the return
        value of the method.

        :param constraints: list containing the maximum emissions \
            caused by the model definitions which will be created \
            within this method
        :type constraints: list
        :param model_definition: file path of the model definition to \
            be optimized
        :type model_definition: str / streamlit.UploadedFile
        :param directory: str containing the path of the directory \
            where the created model definitions will be saved
        :type directory: str
        :param limits: list containing the percentages of reduction \
            defined within the GUI
        :type limits: list

        :return: - **files** (dict) - dictionary holding the \
            combination of limit and path to the new created model \
            definition
    """
    files = {}
    for limit in limits:
        # append a dict entry for the limit
        files.update({str(limit): []})
        # get the constraint for the given limit from the list of
        # constraints
        constraint = constraints[limit]
        # import the user given model definition without removing the
        # units columns
        nodes_data = import_model_definition(model_definition, False)
        # append the file path for the transformation model definition
        # to the files dict
        file_name = directory + "/" + model_definition.name[:-5]
        files[str(limit)].append(file_name + "_" + str(limit) + ".xlsx")
        # create new model definition and save it to the created path
        writer = pandas.ExcelWriter(files[str(limit)][-1], engine="xlsxwriter")
        nodes_data["energysystem"].loc[1, "constraint cost limit"] = \
            float(constraint)
        nodes_data["time series"] = nodes_data["timeseries"]
        nodes_data.pop("timeseries")
        for sheet in nodes_data.keys():
            nodes_data[sheet].to_excel(writer, sheet_name=sheet, index=False)
        writer.close()
    return files


def run_pareto(limits: list, model_definition, GUI_main_dict: dict,
               result_path: str) -> str:
    """
        This method represents the main function of Pareto
        optimization. For this purpose, the model is first run
        according to the first optimization criterion, then according
        to the second optimization criterion, after which the
        semi-optimal intermediate points are determined.  Finally, the
        CSV files are created for further result processing.

        :param limits: list containing the percentages of reduction \
            defined within the GUI
        :type limits: list
        :param model_definition: file path of the model definition to \
            be optimized
        :type model_definition: str
        :param GUI_main_dict: Dictionary which is passed to the method \
            by the GUI and contains the user's input. The dictionary \
            must contain the following attributes for this method:

                - pre_modeling
                - num_threads
                - time series params
                - graph state
                - xlsx select state
                - console select state
                - solver select
                - dh path
                - cluster dh
                - pre modeling time series params
                - investment boundaries
                - investment boundaries factor
                - pre model path

        :type GUI_main_dict: dict
        :param result_path: str which contains the result path which \
            is user specific
        :type result_path: str
        
        :return: - **directory** (str) - path where the pareto runs \
            were stored
    """
    from program_files.GUI_st.GUI_st_global_functions \
        import run_SESMG, set_result_path

    # create one directory to collect all runs
    directory = (result_path + "/"
                 + datetime.now().strftime("%Y-%m-%d--%H-%M-%S"))
    os.mkdir(directory)

    logging.info("Optimization of the following runs "
                 + str(limits)
                 + " started!")

    # FIRST CRITERION
    result_folders = {"0": []}
    # TODO enable more than one model definition (districts)
    save_path = create_model_definition_save_folder(model_definition,
                                                    directory, "0")
    # append optimum of first criterion driven run to the list of
    # result folders
    result_folders["0"].append(save_path)
    # run the optimization of the first criterion minimum
    run_SESMG(GUI_main_dict, model_definition, save_path)
    
    # SECOND CRITERION
    # TODO enable more than one model definition (districts)
    # set the save path
    save_path2 = create_model_definition_save_folder(model_definition,
                                                     directory, "1")
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
            save_path = create_model_definition_save_folder(model_definition,
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
            import_model_definition(model_definition)["sinks"])
    
    # create amount csv files
    collect_electricity_amounts(
        dataframes=result_dfs,
        nodes_data=import_model_definition(model_definition),
        result_path=os.path.dirname(save_path),
        sink_known=sink_types)

    collect_heat_amounts(dataframes=result_dfs,
                         nodes_data=import_model_definition(model_definition),
                         result_path=os.path.dirname(save_path),
                         sink_known=sink_types)
    
    return directory


def change_optimization_criterion(nodes_data: dict) -> None:
    """
        Swaps the primary optimization criterion ("costs") with the
        secondary criterion ("constraint costs") in the entire model \
        definition. The constraint limit is adjusted.
    
        :param nodes_data: dictionary containing the parameters of the \
            model definition
        :type nodes_data: dict
    """
    
    for sheet in [*nodes_data]:
        switch_dict = {
            'constraint cost limit': 'cost limit',
            'cost limit': 'constraint cost limit',
            'variable costs': 'variable constraint costs',
            'variable constraint costs': 'variable costs',
            'periodical constraint costs': 'periodical costs',
            'periodical costs': 'periodical constraint costs',
            'variable output constraint costs': 'variable output costs',
            'variable output costs': 'variable output constraint costs',
            'variable output constraint costs 2': 'variable output costs 2',
            'variable output costs 2': 'variable output constraint costs 2',
            'variable input constraint costs': 'variable input costs',
            'variable input costs': 'variable input constraint costs',
            'excess constraint costs': 'excess costs',
            'excess costs': 'excess constraint costs',
            'shortage constraint costs': 'shortage costs',
            'shortage costs': 'shortage constraint costs',
            'fix investment constraint costs': 'fix investment costs',
            'fix investment costs': 'fix investment constraint costs'}
        
        column_names = nodes_data[sheet].columns.values
        column_names_list = column_names.tolist()
        
        column_names_list = [
            (switch_dict.get(x) if x in switch_dict.keys() else x)
            for x in column_names_list]
        
        nodes_data[sheet].columns = column_names_list
