import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pytest
import importlib.util
from unittest.mock import patch
import streamlit as st

# Load 4_Demo_Tool.py dynamically
tool_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'program_files', 'GUI_st', 'pages', '4_Demo_Tool.py')
)
spec = importlib.util.spec_from_file_location("demo_tool", tool_path)
demo_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo_tool)

@patch.dict(st.session_state, {"show_pareto_table": True}, clear=True)
def test_toggle_pareto_table_flips_true_to_false():
    demo_tool.toggle_pareto_table()
    assert st.session_state["show_pareto_table"] is False

@patch.dict(st.session_state, {"show_pareto_table": False}, clear=True)
def test_toggle_pareto_table_flips_false_to_true():
    demo_tool.toggle_pareto_table()
    assert st.session_state["show_pareto_table"] is True
