import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pytest
import importlib.util
from unittest.mock import patch
import streamlit as st

# Load dynamically 4_Demo_Tool.py
tool_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'program_files', 'GUI_st', 'pages', '4_Demo_Tool.py')
)
spec = importlib.util.spec_from_file_location("demo_tool", tool_path)
demo_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo_tool)

@patch.dict(st.session_state, {}, clear=True)
def test_change_state_submitted_demo_run_sets_done():
    demo_tool.change_state_submitted_demo_run()
    assert "state_submitted_demo_run" in st.session_state
    assert st.session_state["state_submitted_demo_run"] == "done"
