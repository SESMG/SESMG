import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import tests.dynamic_loader_3RP as loader

rp = loader.result_processing_loaded

@patch("result_processing_loaded.st")
@patch("result_processing_loaded.px.area")
@patch("result_processing_loaded.pd.read_csv")
def test_create_energy_amounts_diagram(mock_read_csv, mock_px_area, mock_st):
    # Mocked DataFrame with expected structure
    df = pd.DataFrame({
        "reductionco2": [0, 10, 20],
        "tech1": [100, 150, 200],
        "tech2": [50, 75, 100],
        "zero_column": [0, 0, 0]  # should be filtered out
    })
    mock_read_csv.return_value = df

    # Mock Plotly figure
    mock_fig = MagicMock()
    mock_px_area.return_value.update_layout.return_value = mock_fig

    # Call the function
    rp.create_energy_amounts_diagram("mocked_path/amounts.csv")

    # Check pd.read_csv was called
    mock_read_csv.assert_called_once_with("mocked_path/amounts.csv")

    # Check px.area was called with expected y-columns
    args, kwargs = mock_px_area.call_args
    assert kwargs["x"] == "reductionco2"
    assert kwargs["y"] == ["tech1", "tech2"]

    # Check Streamlit plotted the figure
    mock_st.plotly_chart.assert_called_once_with(mock_fig, theme="streamlit", use_container_width=True)