import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pytest
from demo_build_demo_excel import build_demo_excel
from unittest.mock import Mock

def test_build_demo_excel_calls_set_and_execute(tmp_path):
    # Simulate input values
    input_dict = {
        "input_pv": 1000,
        "input_st": 2000,
        "input_battery": 3000,
        "input_dcts": 4000,
        "input_gchp": 5000,
        "input_ashp": 6000,
        "input_chp": 7000,
        "input_dh_urban": 1,
        "input_dh_sub_urban": 0,
        "input_dh_rural": 0,
        "input_chp_urban": 0,
        "input_chp_sub_urban": 0,
        "input_chp_rural": 0,
        "input_chp_a": 1,
        "input_criterion": "monetary"
    }

    # Create temporary Excel file (empty template)
    import openpyxl
    wb = openpyxl.Workbook()
    demo_path = tmp_path / "demo_model.xlsx"
    wb.save(demo_path)

    # Create mocks
    set_cell_mock = Mock()
    execute_mock = Mock()

    # Execute function
    build_demo_excel(
        input_dict=input_dict,
        template_path=str(demo_path),
        save_path=str(tmp_path / "output_model.xlsx"),
        set_cell_func=set_cell_mock,
        execute_func=execute_mock
    )

    # Check calls
    assert set_cell_mock.call_count > 0
    execute_mock.assert_called_once()
    args, kwargs = execute_mock.call_args
    assert kwargs["demo_file"].endswith("output_model.xlsx")
    assert kwargs["mode"] == "monetary"
