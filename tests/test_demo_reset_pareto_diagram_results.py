import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pytest
import pandas as pd
from demo_clear_pareto_results import clear_pareto_results

def test_clear_pareto_results_creates_empty_csv(tmp_path):
    # Create a file with data
    file_path = tmp_path / "pareto_results.csv"
    df = pd.DataFrame({
        "Costs in million Euro/a": [10.5],
        "CO2-emissions in t/a": [10000],
        "Name": ["Initial"]
    })
    df.to_csv(file_path, index=False)

    # Run the function
    result = clear_pareto_results(str(file_path))

    # Assertions
    assert result is True
    cleared_df = pd.read_csv(file_path)
    assert cleared_df.empty
    assert list(cleared_df.columns) == ["Costs in million Euro/a", "CO2-emissions in t/a", "Name"]

def test_clear_pareto_results_returns_false_if_file_missing(tmp_path):
    missing_file = tmp_path / "missing.csv"
    result = clear_pareto_results(str(missing_file))
    assert result is False
