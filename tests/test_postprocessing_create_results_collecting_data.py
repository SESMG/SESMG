import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock
from program_files.postprocessing.create_results_collecting_data import calc_variable_costs

def test_calc_variable_costs_scalar():
    node = Mock()

    # Define two mock flows with scalar variable_costs
    flow_input1 = Mock()
    flow_input1.variable_costs = 0.1
    flow_input2 = Mock()
    flow_input2.variable_costs = 0.0

    flow_output1 = Mock()
    flow_output1.variable_costs = 0.0
    flow_output2 = Mock()
    flow_output2.variable_costs = 0.2

    node.inputs = {"bus1": flow_input1, "bus2": flow_input2}
    node.outputs = {"bus3": flow_output1, "bus4": flow_output2}

    comp_dict = [
        np.array([10.0, 0.0]),      # only input1 active
        np.array([0.0, 0.0]),
        np.array([0.0, 0.0]),
        np.array([20.0, 0.0])        # only output2 active
    ]

    result = calc_variable_costs(node, comp_dict, "variable_costs")
    expected = 10.0 * 0.1 + 20.0 * 0.2 # = 1.0 + 4.0 = 5.0

    assert isinstance(result, float)
    assert result == pytest.approx(expected, rel=1e-6)

def test_calc_variable_costs_timeseries():
    node = Mock()

    cost_series_input1 = pd.Series([0.1] * 24)
    cost_series_input2 = pd.Series([0.0] * 24)
    cost_series_output1 = pd.Series([0.0] * 24)
    cost_series_output2 = pd.Series([0.2] * 24)

    flow_input1 = Mock()
    flow_input1.variable_costs = cost_series_input1
    flow_input2 = Mock()
    flow_input2.variable_costs = cost_series_input2

    flow_output1 = Mock()
    flow_output1.variable_costs = cost_series_output1
    flow_output2 = Mock()
    flow_output2.variable_costs = cost_series_output2

    node.inputs = {"bus1": flow_input1, "bus2": flow_input2}
    node.outputs = {"bus3": flow_output1, "bus4": flow_output2}

    comp_dict = [
        np.array([1.0] * 23),  # only input1 active
        np.array([0.0] * 23),
        np.array([0.0] * 23),
        np.array([2.0] * 23),   # only output2 active
         ]

    result = calc_variable_costs(node, comp_dict, "variable_costs")
    expected = (
                       np.sum(cost_series_input1.iloc[:-1] * 1.0) +
                       np.sum(cost_series_output2.iloc[:-1] * 2.0)
               )
    assert isinstance(result, float)
    assert result == pytest.approx(expected, rel=1e-6)

def test_calc_variable_costs_timeseries_is_one_year_with_factor():
    node = Mock()

    date_range = pd.date_range(start="2022-01-01", periods=8760, freq="H")
    attr_value = 0.1

    cost_series = pd.Series([attr_value] * len(date_range), index=date_range)

    flow_input = Mock()
    flow_input.variable_costs = cost_series
    flow_dummy = Mock()
    flow_dummy.variable_costs = pd.Series([0.0] * len(date_range), index=date_range)

    node.inputs = {"bus1": flow_input, "bus2": flow_dummy}
    node.outputs = {"bus3": flow_dummy, "bus4": flow_dummy}

    # comp_dict has a length of 8759
    comp_dict = [
        np.array([1.0] * (len(date_range) - 1)),  # only input1 activ
        np.array([0.0] * (len(date_range) - 1)),
        np.array([0.0] * (len(date_range) - 1)),
        np.array([0.0] * (len(date_range) - 1)),
    ]

    result = calc_variable_costs(node, comp_dict, "variable_costs")

    # expected hours = result divided by costs
    single_step_cost = attr_value
    hours_equivalent = result / single_step_cost

    # tolerance 12 hours
    assert abs(hours_equivalent - 8759) <= 12