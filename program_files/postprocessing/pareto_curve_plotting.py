"""
    @author: GregorBecker - gregor.becker@fh-muenster.de
"""

import pandas as pd


def collect_pareto_data(result_dfs: dict, result_path: str) -> None:
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
        if dataframe != "1":
            costs["monetary"].append(
                sum(result_dfs[dataframe]["variable costs/CU"])
                + sum(result_dfs[dataframe]["periodical costs/CU"])
            )
            costs["emissions"].append(sum(result_dfs[dataframe]["constraints/CU"]))
        else:
            costs["emissions"].append(
                sum(result_dfs[dataframe]["variable costs/CU"])
                + sum(result_dfs[dataframe]["periodical costs/CU"])
            )
            costs["monetary"].append(sum(result_dfs[dataframe]["constraints/CU"]))

    # create pandas Dataframe from results' components.csv points
    df1 = pd.DataFrame(
        {"costs": costs["monetary"], "emissions": costs["emissions"]},
        columns=["costs", "emissions"],
    )
    df1.to_csv(result_path + "/pareto.csv")
