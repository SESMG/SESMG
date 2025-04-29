import os
import pandas as pd

def clear_pareto_results(file_path: str) -> bool:
    """
    Clears the contents of a Pareto results CSV file, if it exists.

    :param file_path: Path to the CSV file
    :return: True if the file was cleared, False if the file did not exist
    
    """
    if os.path.exists(file_path):
        empty_df = pd.DataFrame(columns=["Costs in million Euro/a", "CO2-emissions in t/a", "Name"])
        empty_df.to_csv(file_path, index=False)
        return True
    return False
