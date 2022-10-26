import pandas as pd
import numpy as np
import xlsxwriter
import os
from datetime import datetime
from program_files.preprocessing.Spreadsheet_Energy_System_Model_Generator import (
    sesmg_main, sesmg_main_including_premodel
)


def __get_cb_state(checkbox) -> bool:
    """
    removes tkinter variable handling

    :param checkbox: checkbox whose boolean is to be returned
    :type checkbox: tkinter.Variable
    :rtype: bool

    """
    if checkbox.get() == 1:
        return True
    else:
        return False


def merge_component_csvs(limits, files, directory, result_folders):
    components_csvs = {}
    returns = {}
    result_df = pd.DataFrame()
    limits.append("1")
    for limit in limits:
        components_csvs.update({limit: []})
        for scenario in result_folders[limit]:
            components_csvs[limit].append(
                pd.read_csv(directory + scenario[7:] + "/components.csv")
            )
    for limit in limits:
        for dataframe in components_csvs[limit]:
            dataframe = dataframe.replace(to_replace="---", value=0)
            result_df = result_df.append(dataframe, sort=True)
        for col in result_df.keys():
            if not (str(col) == "ID" or str(col) == "type"):
                result_df[str(col)] = result_df[str(col)].astype(float)
        result_df = result_df.groupby(["ID", "type"]).sum(axis=0)
        returns.update({limit: result_df})
    for result in returns:
        returns[result].to_csv(directory + "/components_{}.csv".format(result))
    return returns


def calc_constraint_limits(result_folders, limits):
    constraints = {}
    # get constraints of the first optimization
    result = pd.read_csv(str(result_folders["1"][0]) + "/components.csv")
    constr_min_1 = float(sum(result["constraints/CU"]))
    # get constraints of the second optimization
    result2 = pd.read_csv(str(result_folders["0"][0]) + "/components.csv")
    constr_min_2 = float(sum(result2["variable costs/CU"])
                         + sum(result2["periodical costs/CU"]))
    # devide solvable range in "limits" intervals
    for i in limits:
        constraints.update({i: constr_min_1 - float(constr_min_1-constr_min_2) * float(i)})
    return constraints


def criterion_switch_dh(directory):
    columns = {}
    path = os.path.dirname(os.path.dirname(directory)) \
           + "/program_files/urban_district_upscaling/standard_parameters.xlsx"
    # get keys from plain scenario
    standard_parameter = pd.ExcelFile(path)
    # get columns from plain sheet
    for sheet in standard_parameter.sheet_names:
        if sheet not in ["8_pipe_types", "8_1_other"]:
            columns[sheet] = standard_parameter.parse(sheet)
    
    component_param = standard_parameter.parse("8_pipe_types",
                                               index_col="label_3")
    other_param = standard_parameter.parse("8_1_other", index_col="label")
    writer = pd.ExcelWriter(path, engine="xlsxwriter")
    
    fix_costs = component_param.loc[:, "fix_costs"]
    component_param.loc[:, "fix_costs"] = \
        component_param.loc[:, "fix_constraint_costs"]
    component_param.loc[:, "fix_constraint_costs"] = fix_costs

    periodical_costs = component_param.loc[:, "capex_pipes"].copy()
    component_param.loc[:, "capex_pipes"] = \
        component_param.loc[:, "periodical_constraint_costs"]
    component_param.loc[:, "periodical_constraint_costs"] = periodical_costs
    
    costs = other_param.loc[:, "costs"].copy()
    other_param.loc[:, "costs"] = \
        other_param.loc[:, "constraint costs"]
    other_param.loc[:, "constraint costs"] = costs
    component_param.reset_index(inplace=True, drop=False)
    other_param.reset_index(inplace=True, drop=False)
    component_param.to_excel(writer, "8_pipe_types", index=False)
    other_param.to_excel(writer, "8_1_other", index=False)
    for sheet in columns:
        columns[sheet].to_excel(writer, sheet, index=False)
    writer.save()


def run_pareto(
    limits, scenario, gui_variables, timeseries_prep_param, pre_modeling,
    pre_model_timeseries_prep, investment_boundaries, investment_boundary_factor,
    pre_model_path
):
    # create one directory to collect all runs
    directory = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "results/" + datetime.now().strftime("%Y-%m-%d--%H-%M-%S"),
    )
    os.mkdir(directory)
    print(limits)
    result_folders = {"1": []}
    # TODO enable more than one scenario (districts)
    # set the save path
    scenario_name = os.path.basename(scenario)[:-5]
    save_path = str(
        directory + "/"
        + scenario_name
        + str(datetime.now().strftime("_%Y-%m-%d--%H-%M-%S")))
    # append optimum of first criterion driven run to the list of
    # result folders
    result_folders["1"].append(save_path)
    # create new folder in which the results will be stored
    os.mkdir(save_path)
    if not pre_modeling:
        sesmg_main(
            scenario_file=scenario,
            result_path=save_path,
            num_threads=gui_variables["num_threads"].get(),
            timeseries_prep=timeseries_prep_param,
            graph=__get_cb_state(gui_variables["graph_state"]),
            criterion_switch=False,
            xlsx_results=__get_cb_state(
                    gui_variables["xlsx_select_state"]),
            console_results=__get_cb_state(
                    gui_variables["console_select_state"]),
            solver=gui_variables["solver_select"].get(),
            district_heating_path=gui_variables["dh_path"].get(),
            cluster_dh=gui_variables["cluster_dh"].get())

    # If pre-modeling is activated a second run will be carried out
    elif pre_modeling:
        sesmg_main_including_premodel(
                scenario_file=scenario,
                result_path=save_path,
                num_threads=gui_variables["num_threads"].get(),
                timeseries_prep=timeseries_prep_param,
                graph=__get_cb_state(gui_variables["graph_state"]),
                criterion_switch=__get_cb_state(
                        gui_variables["criterion_state"]),
                xlsx_results=__get_cb_state(
                        gui_variables["xlsx_select_state"]),
                console_results=__get_cb_state(
                        gui_variables["console_select_state"]),
                solver=gui_variables["solver_select"].get(),
                district_heating_path=gui_variables["dh_path"].get(),
                cluster_dh=gui_variables["cluster_dh"].get(),
                pre_model_timeseries_prep=pre_model_timeseries_prep,
                investment_boundaries=investment_boundaries,
                investment_boundary_factor=investment_boundary_factor,
                pre_model_path=pre_model_path
        )
    
    criterion_switch_dh(directory)
    print(save_path)
    # TODO enable more than one scenario (districts)
    # set the save path
    scenario_name = os.path.basename(scenario)[:-5]
    save_path2 = str(
            directory + "/"
            + scenario_name + "_0"
            + str(datetime.now().strftime("_%Y-%m-%d--%H-%M-%S")))
    print(save_path2)
    # append optimum of first criterion driven run to the list of
    # result folders
    result_folders.update({"0": [save_path2]})
    # create new folder in which the results will be stored
    os.mkdir(save_path2)

    if not pre_modeling:
        sesmg_main(
                scenario_file=scenario,
                result_path=save_path2,
                num_threads=gui_variables["num_threads"].get(),
                timeseries_prep=timeseries_prep_param,
                graph=__get_cb_state(gui_variables["graph_state"]),
                criterion_switch=True,
                xlsx_results=__get_cb_state(
                        gui_variables["xlsx_select_state"]),
                console_results=__get_cb_state(
                        gui_variables["console_select_state"]),
                solver=gui_variables["solver_select"].get(),
                district_heating_path=gui_variables["dh_path"].get(),
                cluster_dh=gui_variables["cluster_dh"].get())

    # If pre-modeling is activated a second run will be carried out
    elif pre_modeling:
        sesmg_main_including_premodel(
                scenario_file=scenario,
                result_path=save_path2,
                num_threads=gui_variables["num_threads"].get(),
                timeseries_prep=timeseries_prep_param,
                graph=__get_cb_state(gui_variables["graph_state"]),
                criterion_switch=True,
                xlsx_results=__get_cb_state(
                        gui_variables["xlsx_select_state"]),
                console_results=__get_cb_state(
                        gui_variables["console_select_state"]),
                solver=gui_variables["solver_select"].get(),
                district_heating_path=gui_variables["dh_path"].get(),
                cluster_dh=gui_variables["cluster_dh"].get(),
                pre_model_timeseries_prep=pre_model_timeseries_prep,
                investment_boundaries=investment_boundaries,
                investment_boundary_factor=investment_boundary_factor,
                pre_model_path=pre_model_path
        )
    
    constraints = calc_constraint_limits(result_folders, limits)
    print(constraints)
    files = create_transformation_scenarios(constraints, scenario, directory, limits)

    criterion_switch_dh(directory)
    
    for limit in limits:
        result_folders.update({str(limit): []})
        for scenario in files[limit]:
            scenario_name = os.path.basename(scenario)[:-5]
            print(scenario_name)
            gui_variables["save_path"].set(
                str(
                    directory + "/"
                    + scenario_name
                    + str(datetime.now().strftime("_%Y-%m-%d--%H-%M-%S"))
                )
            )
            # create new folder in which the results will be stored
            os.mkdir(gui_variables["save_path"].get())
            result_folders[str(limit)].append(gui_variables["save_path"].get())
            if not pre_modeling:
                sesmg_main(
                        scenario_file=scenario,
                        result_path=gui_variables["save_path"].get(),
                        num_threads=gui_variables["num_threads"].get(),
                        timeseries_prep=timeseries_prep_param,
                        graph=__get_cb_state(gui_variables["graph_state"]),
                        criterion_switch=False,
                        xlsx_results=__get_cb_state(
                                gui_variables["xlsx_select_state"]),
                        console_results=__get_cb_state(
                                gui_variables["console_select_state"]),
                        solver=gui_variables["solver_select"].get(),
                        district_heating_path=gui_variables["dh_path"].get(),
                        cluster_dh=gui_variables["cluster_dh"].get())

            # If pre-modeling is activated a second run will be carried out
            elif pre_modeling:
                sesmg_main_including_premodel(
                        scenario_file=scenario,
                        result_path=gui_variables["save_path"].get(),
                        num_threads=gui_variables["num_threads"].get(),
                        timeseries_prep=timeseries_prep_param,
                        graph=__get_cb_state(gui_variables["graph_state"]),
                        criterion_switch=False,
                        xlsx_results=__get_cb_state(
                                gui_variables["xlsx_select_state"]),
                        console_results=__get_cb_state(
                                gui_variables["console_select_state"]),
                        solver=gui_variables["solver_select"].get(),
                        district_heating_path=gui_variables["dh_path"].get(),
                        cluster_dh=gui_variables["cluster_dh"].get(),
                        pre_model_timeseries_prep=pre_model_timeseries_prep,
                        investment_boundaries=investment_boundaries,
                        investment_boundary_factor=investment_boundary_factor,
                        pre_model_path=pre_model_path
                )
    return result_folders


def create_transformation_scenarios(constraints, scenario_names, directory, limits):
    files = {}
    for limit in limits:
        files.update({str(limit): []})
    
    for counter in limits:
        constraint = constraints[counter]
        xls = pd.ExcelFile(scenario_names)
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
        }
        files[str(counter)].append(directory + "/" + scenario_names.split("/")[-1][:-5] + "_" + str(counter) + ".xlsx")
        writer = pd.ExcelWriter(
            directory + "/" + scenario_names.split("/")[-1][:-5] + "_" + str(counter) + ".xlsx", engine="xlsxwriter")
        nd["energysystem"].loc[1, "constraint cost limit"] = float(constraint)
        for i in nd.keys():
            nd[i].to_excel(writer, sheet_name=str(i), index=False)
        writer.save()
        #os.system("mv " + result_path + " " + path)
        print(files)
    return files

# todo: clarify the link below!
if __name__ == "__main__":
    merge_component_csvs(
        [],
        "",
        "/Users/gregorbecker/Desktop/SESMG-dev_open_district_upscaling-3/results",
        {"1": ["results/a_test", "results/b_test", "results/c_test"]},
    )
