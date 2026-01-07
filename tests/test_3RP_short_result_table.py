import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import tests.dynamic_loader_3RP as loader

# Load the dynamically imported module
rp = loader.result_processing_loaded

@patch("result_processing_loaded.AgGrid")
@patch("result_processing_loaded.st")
@patch("result_processing_loaded.pd.read_csv")
def test_short_result_table(mock_read_csv, mock_st, mock_aggrid):
    # Simulate a DataFrame returned by pd.read_csv
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    mock_read_csv.return_value = df

    # Call the function
    rp.short_result_table("mocked_path/components.csv")

    # Assert that the CSV was read correctly
    mock_read_csv.assert_called_once_with("mocked_path/components.csv")
    
    # Check Streamlit components are called as expected
    mock_st.subheader.assert_called_once_with("Result Table")
    mock_st.markdown.assert_called_once()
    
    # Check AgGrid was called
    mock_aggrid.assert_called_once()

    # Validate the 'height' argument was set within bounds
    called_kwargs = mock_aggrid.call_args.kwargs
    assert "height" in called_kwargs
    assert called_kwargs["height"] <= 500