import pandas as pd
import numpy as np
import xlsxwriter
import os
from datetime import datetime
from program_files.preprocessing.Spreadsheet_Energy_System_Model_Generator import sesmg_main


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
            components_csvs[limit].append(pd.read_csv(directory + scenario[7:] + "/components.csv"))
    for limit in limits:
        for dataframe in components_csvs[limit]:
            dataframe = \
                dataframe.replace(to_replace="---", value=0)
            result_df = result_df.append(dataframe)
        for col in result_df.keys():
            if not (str(col) == "ID" or str(col) == "type"):
                result_df[str(col)] = result_df[str(col)].astype(float)
        result_df = result_df.groupby(["ID", "type"]).sum(axis=0)
        returns.update({limit: result_df})
    for result in returns:
        returns[result].to_csv(directory + "/components_{}.csv".format(result))
    return returns

def run_pareto(limits, files, gui_variables, timeseries_prep_param, directory,
               result_folders):
    for limit in limits:
        result_folders.update({str(limit): []})
        for scenario in files[limit]:
            scenario_name = os.path.basename(scenario)[:-5]
            gui_variables["save_path"].set(
                str(os.path.join(gui_variables[
                                     "save_path_directory"].get()) + '/'
                    + scenario_name
                    + str(datetime.now().strftime('_%Y-%m-%d--%H-%M-%S'))))
            # create new folder in which the results will be stored
            os.mkdir(gui_variables["save_path"].get())
            result_folders[str(limit)].append(gui_variables["save_path"].get())
            # execute SESMG algorithm
            sesmg_main(
                scenario_file=scenario,
                result_path=gui_variables["save_path"].get(),
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
                cluster_dh=gui_variables["cluster_dh"].get())
            os.system("mv " + gui_variables["save_path"].get() + " " + directory)
    return result_folders


def get_constraints(result_paths):
    constraints = []
    for folder in result_paths["1"]:
        result = pd.read_csv(folder + "/components.csv")
        result = result.replace(to_replace="---", value=0)
        result["constraints/CU"] = \
            result["constraints/CU"].astype(float)
        constraints.append(sum(result["constraints/CU"]))
    return constraints


def create_transformation_scenarios(constraints, scenario_names, result_path,
                                    limits):
    counter = 0
    files = {}
    path = os.path.join(os.path.dirname(os.path.dirname(
        os.path.dirname(__file__))),
        "results/" + datetime.now().strftime('%Y-%m-%d--%H-%M-%S'))
    os.mkdir(path)
    for limit in limits:
        files.update({str(limit): []})
    for scenario in scenario_names:
        scenario_names = result_path["1"][counter].split("-")[0][8:-5]
        constraint = constraints[counter]
        xls = pd.ExcelFile(scenario)
        nd = {'buses': xls.parse('buses'),
              'energysystem': xls.parse('energysystem'),
              'sinks': xls.parse('sinks'),
              'links': xls.parse('links'),
              'sources': xls.parse('sources'),
              'time series': xls.parse('time series'),
              'transformers': xls.parse('transformers'),
              'storages': xls.parse('storages'),
              'weather data': xls.parse('weather data'),
              'competition constraints': xls.parse('competition constraints'),
              'insulation': xls.parse('insulation'),
              'district heating': xls.parse('district heating')
              }
        for limit in limits:
            files[str(limit)].append(path + "/" + scenario_names + str(limit) + ".xlsx")
            writer = pd.ExcelWriter(path + "/" + scenario_names + str(limit) + ".xlsx",
                                    engine='xlsxwriter')
            nd["energysystem"].loc[1, "constraint cost limit"] = \
                float(constraint) * float(limit)
            for i in nd.keys():
                nd[i].to_excel(writer, sheet_name=str(i))
            writer.save()
        os.system("mv " + result_path["1"][counter] + " " + path)
        counter += 1
    return files, path


if __name__ == "__main__":
    merge_components_csv(
        ['../../results/auto_generated_scenario_2022-03-01--15-00-57',
         '../../results/auto_generated_scenario_no1_2022-03-01--15-01-24']
)
