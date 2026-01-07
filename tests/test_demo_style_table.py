import pytest
import pandas as pd
import os
import importlib.util

# Dynamically load 4_Demo_Tool.py
tool_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'program_files', 'GUI_st', 'pages', '4_Demo_Tool.py')
)

spec = importlib.util.spec_from_file_location("demo_tool", tool_path)
demo_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo_tool)

def test_style_table_returns_html_with_styles():
    # Create an example DataFrame
    df = pd.DataFrame({
        "Name": ["A", "B"],
        "Value": [100, 200]
    })

    # Apply style
    html = demo_tool.style_table(df)

    # Checks
    assert isinstance(html, str)
    assert "<table" in html
    assert "font-weight: bold" in html
    assert "text-align: center" in html
    assert html.lower().count("<tr") == 3  # 1 header + 2 rows
    assert html.count("<td") == 4   # 2 rows × 2 columns