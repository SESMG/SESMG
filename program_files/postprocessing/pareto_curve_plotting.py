import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os


def create_pareto_plot(result_dfs: dict, result_path: str) -> None:
    """
    
        :param result_dfs: dictionary containing the energy systems' \
            components.csv
        :type result_dfs: dict
        :param result_path: path where the pareto plot will be stored
        :type result_path: str
    """
    # dict containing pareto points data
    costs = {"monetary": [], "emissions": []}

    for dataframe in result_dfs:
        print(dataframe)
        if dataframe != "0":
            costs["monetary"].append(
                sum(result_dfs[dataframe]["variable costs/CU"]) + sum(result_dfs[dataframe]["periodical costs/CU"])
            )
            costs["emissions"].append(sum(result_dfs[dataframe]["constraints/CU"]))
        else:
            costs["emissions"].append(
                    sum(result_dfs[dataframe]["variable costs/CU"]) + sum(
                            result_dfs[dataframe]["periodical costs/CU"])
            )
            costs["monetary"].append(
                sum(result_dfs[dataframe]["constraints/CU"]))

    # create pandas Dataframe from results' components.csv points
    df1 = pd.DataFrame(
        {"costs": costs["monetary"], "emissions": costs["emissions"]},
        columns=["costs", "emissions"],
    )
    df1.to_csv(result_path + "/pareto.csv")
    # clear the old plot
    plt.clf()
    # create the new plot
    sns.lineplot(data=df1, x="costs", y="emissions", marker="o")
    # add a grid to plot
    plt.grid()
    # save the plot to result folder
    plt.savefig(result_path + "/pareto.jpeg")


if __name__ == "__main__":
    from program_files.preprocessing.create_energy_system import import_scenario
    create_pareto_plot(
            {"1": pd.read_csv("<path_to_csv_file>"),
             "0.75": pd.read_csv(),
             "0.5": pd.read_csv(),
             "0.35": pd.read_csv(),
             "0.25": pd.read_csv(),
             "0.15": pd.read_csv(),
             "0": pd.read_csv()},
            # result path 
            str()
    )
