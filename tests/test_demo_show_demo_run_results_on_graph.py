import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pytest
import pandas as pd
from demo_build_pareto_chart import build_pareto_chart
import altair as alt

def test_build_pareto_chart_returns_chart_object():
    df = pd.DataFrame({
        "Costs in million Euro/a": [12.5],
        "CO2-emissions in t/a": [10000],
        "Name": ["Test Run"]
    })

    chart = build_pareto_chart(df, mode="simplified")

    # Verify that it is an Altair chart
    assert isinstance(chart, alt.Chart) or isinstance(chart, alt.LayerChart)

def test_build_pareto_chart_empty_input():
    df_empty = pd.DataFrame(columns=["Costs in million Euro/a", "CO2-emissions in t/a", "Name"])

    chart = build_pareto_chart(df_empty, mode="advanced")

    assert isinstance(chart, alt.Chart) or isinstance(chart, alt.LayerChart)
