import matplotlib.pyplot as plt
import pandas as pd


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
        costs["monetary"].append(
            sum(dataframe["variable costs/CU"]) + sum(dataframe["periodical costs/CU"])
        )
        costs["emissions"].append(sum(dataframe["constraints/CU"]))

    # create pandas Dataframe from results' components.csv points
    df1 = pd.DataFrame(
        {"costs": costs["monetary"], "emissions": costs["emissions"]},
        columns=["costs", "emissions"],
    )
    # clear the old plot
    plt.clf()
    # create the new plot
    sns.lineplot(data=df1, x="costs", y="emissions", marker="o")
    # add a grid to plot
    plt.grid()
    # save the plot to result folder
    plt.savefig(result_path + "/pareto.jpeg")


if __name__ == "__main__":
    create_pareto_plot(
        result_dfs={"1": pd.read_csv(""), "0.5": pd.read_csv(""), "0": pd.read_csv("")},
        result_path="",
    )
