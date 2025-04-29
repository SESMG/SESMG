import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pytest
from demo_run_demo_simulation import run_demo_simulation

def test_run_demo_simulation_sets_session_and_calls_main():
    # Simulating inputs
    demo_file = "test_model.xlsx"
    demo_results = "results/"
    mode = "emissions"
    solver = "cbc"
    session_state = {}

    # Create mock of sesmg_main function
    called = {}
    def mock_sesmg_main(**kwargs):
        called.update(kwargs)

    # Execute the function
    run_demo_simulation(
        demo_file=demo_file,
        demo_results=demo_results,
        mode=mode,
        solver=solver,
        session_state=session_state,
        sesmg_main_func=mock_sesmg_main
    )

    # Checks
    assert called["model_definition_file"] == demo_file
    assert called["result_path"] == demo_results
    assert called["criterion_switch"] is True
    assert called["solver"] == solver
    assert session_state["state_submitted_demo_run"] == "not done"