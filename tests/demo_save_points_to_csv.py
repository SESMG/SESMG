import pandas as pd

def save_points_to_csv(df: pd.DataFrame, filepath: str, append: bool = False):
    """
    Save a DataFrame in CSV, with option to create new file or append to existing file.

    param df: DataFrame to save
    :param filepath: path to CSV file
    :param append: if True, append to existing file; if False, create new file

    """
    if df.empty:
        return  #Saves nothing if it is empty

    df.to_csv(
        filepath,
        mode="a" if append else "w",
        header=not append,
        index=False
    )
