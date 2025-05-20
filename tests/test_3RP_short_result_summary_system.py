import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import tests.dynamic_loader_3RP as loader

rp = loader.result_processing_loaded

@patch("result_processing_loaded.st")
@patch("result_processing_loaded.pd.read_csv")
def test_short_result_summary_system(mock_read_csv, mock_st):
    # Create a DataFrame with 9+ columns (to match summary_headers[3] to [8])
    data = {
        "col0": ["x"],
        "col1": ["y"],
        "col2": ["z"],
        "Total Cost": [1000.0],
        "O&M Cost": [200.0],
        "Fuel Cost": [300.0],
        "Other Cost": [400.0],
        "Generated Energy": [500.0],
        "Imported Energy": [600.0],
    }
    df = pd.DataFrame(data)
    mock_read_csv.return_value = df

    # 2x 4 Streamlit column mocks
    cost_cols = [MagicMock() for _ in range(4)]
    energy_cols = [MagicMock() for _ in range(4)]
    mock_st.columns.side_effect = [
        (cost_cols[0], cost_cols[1], cost_cols[2], cost_cols[3]),
        (energy_cols[0], energy_cols[1], energy_cols[2], energy_cols[3]),
    ]

    # Run function
    rp.short_result_summary_system("mocked_path/summary.csv")

    # Check each metric call (only 6 expected: cost1..4, ener1..2)
    for i in range(4):
        cost_cols[i].metric.assert_called_once()
    for i in range(2):
        energy_cols[i].metric.assert_called_once()

    # Check that ener3 and ener4 are unused
    assert energy_cols[2].metric.call_count == 0
    assert energy_cols[3].metric.call_count == 0