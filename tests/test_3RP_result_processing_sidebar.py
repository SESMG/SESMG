from unittest.mock import patch
import tests.dynamic_loader_3RP as loader
rp = loader.result_processing_loaded


def test_result_processing_sidebar_with_results():
    with patch("result_processing_loaded.st") as mock_st, \
         patch("result_processing_loaded.import_GUI_input_values_json") as mock_import_json, \
         patch("result_processing_loaded.load_result_folder_list") as mock_load_results, \
         patch("result_processing_loaded.set_result_path") as mock_set_path, \
         patch("result_processing_loaded.os.walk") as mock_walk:

        mock_import_json.return_value = {
            "res_dd_result_folder": "help",
            "res_b_load_results": "help",
            "res_dd_pareto_point": "help"
        }
        mock_load_results.return_value = ["result1", "result2"]
        mock_st.selectbox.side_effect = ["result1", "2023"]
        mock_st.button.return_value = True
        mock_st.session_state = {"state_result_path": "/mocked/path"}
        mock_walk.return_value = iter([("/mocked/path", ["folder_2023_01"], [])])

        rp.result_processing_sidebar()


def test_result_processing_sidebar_no_results():
    with patch("result_processing_loaded.st") as mock_st, \
         patch("result_processing_loaded.import_GUI_input_values_json") as mock_import_json, \
         patch("result_processing_loaded.load_result_folder_list") as mock_load_results, \
         patch("result_processing_loaded.set_result_path") as mock_set_path, \
         patch("result_processing_loaded.os.walk") as mock_walk:

        mock_import_json.return_value = {
            "res_dd_result_folder": "help",
            "res_b_load_results": "help",
            "res_dd_pareto_point": "help"
        }
        mock_load_results.return_value = []
        mock_st.button.return_value = True
        mock_st.selectbox.side_effect = ["result1", "2023"]
        mock_st.session_state = {"state_result_path": "/mocked/path"}
        mock_walk.return_value = iter([("/mocked/path", ["folder_2023_01"], [])])

        rp.result_processing_sidebar()