import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


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
        costs["monetary"].append(
            sum(result_dfs[dataframe]["variable costs/CU"]) + sum(result_dfs[dataframe]["periodical costs/CU"])
        )
        costs["emissions"].append(sum(result_dfs[dataframe]["constraints/CU"]))

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


#if __name__ == "__main__":
#    create_pareto_plot(
#        result_dfs={"1": pd.read_csv(""), "0.5": pd.read_csv(""), "0": pd.read_csv("")},
#        result_path="",
#    )
if __name__ == "__main__":
    from program_files.preprocessing.create_energy_system import import_scenario
    create_pareto_plot(
            {"1": pd.read_csv(
                "/Users/gregor/Downloads/2022-10-24--07-47-24/20221020_SchlossST_variant_1_2022-10-24--07-47-24/components.csv"),
             "0.75": pd.read_csv(
                 "/Users/gregor/Downloads/2022-10-24--07-47-24/20221020_SchlossST_variant_1_0.25_2022-10-24--07-52-26/components.csv"),
             "0.5": pd.read_csv(
                 "/Users/gregor/Downloads/2022-10-24--07-47-24/20221020_SchlossST_variant_1_0.5_2022-10-24--07-51-24/components.csv"),
             "0.25": pd.read_csv(
                 "/Users/gregor/Downloads/2022-10-24--07-47-24/20221020_SchlossST_variant_1_0.75_2022-10-24--07-49-33/components.csv"),
             "0": pd.read_csv(
                 "/Users/gregor/Downloads/2022-10-24--07-47-24/20221020_SchlossST_variant_1_0_2022-10-24--07-48-20/components.csv")},
            #import_scenario(
            #    "/Users/gregor/Downloads/2022-10-24--07-47-24/20221020_SchlossST_variant_1_0.75.xlsx"),
            
            # import_scenario(
            # "/Users/gregor/Desktop/Arbeit/Git/SESMG/results/2022-10-20--17
            # -52-20/20221018_schlossST_Optimierung2_0.5.xlsx"),
            # "/Users/gregor/Desktop/Arbeit/Git/SESMG/results/2022-10-20--17
            # -52-20/"
            "/Users/gregor/Downloads/2022-10-24--07-47-24/"
    )
