import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pytest
from demo_build_input_dict import build_input_dict

def test_advanced_mode_urban_dh():
    input_data = {
        "name": "Test Run",
        "pv": 1000,
        "st": 2000,
        "ashp": 3000,
        "gchp": 4000,
        "battery": 5000,
        "dcts": 6000,
        "chp": 7000,
        "dh": "urban",
        "solver": "cbc",
        "criterion": "emissions"
    }
    result = build_input_dict("advanced", input_data)

    assert result["input_pv"] == 1000
    assert result["input_dh_urban"] == 1
    assert result["input_chp_a"] == 1
    assert result["solver_select"] == "cbc"
    assert result["input_criterion"] == "emissions"

def test_simplified_mode_percentages():
    input_data = {
        "name": "Simple Test",
        "pv": 1.0,  # 100%
        "st": 0.5,  # 50%
        "ashp": 0.25,
        "gchp": 0.0,
        "battery": 0.75,
        "dcts": 0.5,
        "dh": "rural",
        "solver": "gurobi",
        "criterion": "monetary"
    }
    result = build_input_dict("simplified", input_data)

    assert result["input_pv"] == 10000
    assert result["input_st"] == 13850
    assert result["input_ashp"] == 1250
    assert result["input_gchp"] == 0
    assert result["input_battery"] == 7500
    assert result["input_dcts"] == 5000
    assert result["input_dh_rural"] == 1
    assert result["input_chp_a"] == 0
    assert result["solver_select"] == "gurobi"
    assert result["input_criterion"] == "monetary"
