import pandas as pd

def process_demo_results(df_summary: pd.DataFrame, mode: str, input_name: str, mode_dict: dict) -> pd.DataFrame:
    """
    Processes results of a demo simulation and returns a DataFrame with the additional points.

    :param df_summary: DataFrame loaded from summary.csv
    :param mode: optimisation criterion (‘monetary’ or ‘emissions’)
    :param input_name: user-defined case name
    :param mode_dict: dictionary associating the mode with columns of the summary
    :return: DataFrame with a new data point (costs and emissions)

    """
    annual_costs = float(df_summary[mode_dict.get(mode)[0]] / 1_000_000)
    annual_emissions = float(df_summary[mode_dict.get(mode)[1]] / 1_000_000)

    # Calculate relative change from the current state
    stat_quo_costs = 13.68616781
    stat_quo_emissions = 17221.43690357
    rel_result_costs = round((annual_costs - stat_quo_costs) / stat_quo_costs * 100, 2)
    rel_result_emissions = round((annual_emissions - stat_quo_emissions) / stat_quo_emissions * 100, 2)

    # Create DataFrame with results
    new_row = pd.DataFrame({
        'Costs in million Euro/a': [annual_costs],
        'CO2-emissions in t/a': [annual_emissions],
        'Name': [input_name],
        'Relative Cost Change (%)': [rel_result_costs],
        'Relative Emission Change (%)': [rel_result_emissions]
    })

    return new_row
