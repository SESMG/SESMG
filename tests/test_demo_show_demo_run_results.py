import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pytest
import pandas as pd
from demo_process_demo_results import process_demo_results

def test_process_demo_results_returns_expected_dataframe():
    # Create dummy DataFrame (as if coming from summary.csv)
    df_summary = pd.DataFrame({
        "total_costs": [20000000],       # 20 millones
        "total_emissions": [15000000]    # 15 millones
    })

    # Dictionary mapping modes to DataFrame columns
    mode_dict = {
        "monetary": ["total_costs", "total_emissions"]
    }

    # Calling the function
    result = process_demo_results(
        df_summary=df_summary,
        mode="monetary",
        input_name="TestCase1",
        mode_dict=mode_dict
    )

    # Check DataFrame content
    assert result.shape == (1, 5)
    assert result.iloc[0]["Name"] == "TestCase1"
    assert round(result.iloc[0]["Costs in million Euro/a"], 2) == 20.0
    assert round(result.iloc[0]["CO2-emissions in t/a"], 2) == 15.0
