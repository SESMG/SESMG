import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pytest
import pandas as pd
from demo_save_points_to_csv import save_points_to_csv

def test_save_points_to_csv_creates_new_file(tmp_path):
    df = pd.DataFrame({
        "Name": ["A"],
        "Costs": [10.5],
        "Emissions": [1000]
    })
    csv_path = tmp_path / "results.csv"

    save_points_to_csv(df, str(csv_path), append=False)

    assert csv_path.exists()
    loaded = pd.read_csv(csv_path)
    assert loaded.shape == (1, 3)
    assert loaded["Name"][0] == "A"

def test_save_points_to_csv_appends_to_file(tmp_path):
    df1 = pd.DataFrame({"Name": ["A"], "Costs": [1], "Emissions": [100]})
    df2 = pd.DataFrame({"Name": ["B"], "Costs": [2], "Emissions": [200]})
    csv_path = tmp_path / "results.csv"

    save_points_to_csv(df1, str(csv_path), append=False)
    save_points_to_csv(df2, str(csv_path), append=True)

    loaded = pd.read_csv(csv_path)
    assert loaded.shape == (2, 3)
    assert list(loaded["Name"]) == ["A", "B"]

def test_save_points_to_csv_does_nothing_if_empty(tmp_path):
    df_empty = pd.DataFrame()
    csv_path = tmp_path / "empty.csv"

    save_points_to_csv(df_empty, str(csv_path), append=False)

    # The file must not be created
    assert not csv_path.exists()
