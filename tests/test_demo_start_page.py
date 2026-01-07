import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pytest
from demo_load_demo_assets import load_demo_assets

def test_load_demo_assets_returns_expected_keys():
    # Mocked functions
    def mock_read_markdown(document_path, folder_path, fixed_image_width=None):
        return [f"<p>Content from {document_path}</p>"]

    def mock_image_loader(path):
        return f"Loaded image from {path}"

    def mock_get_path():
        return "/fake/path"

    # Run the test
    assets = load_demo_assets(
        read_md_func=mock_read_markdown,
        image_loader_func=mock_image_loader,
        get_path_func=mock_get_path
    )

    # Assertions
    assert "intro_text" in assets
    assert "system_image" in assets
    assert "table_text" in assets
    assert "dh_image" in assets

    assert "<p>Content from docs/GUI_texts/demo_tool_text.md</p>" in assets["intro_text"]
    assert assets["system_image"] == "Loaded image from /fake/path/docs/images/manual/DemoTool/demo_system_graph.png"
    assert assets["dh_image"] == "Loaded image from /fake/path/docs/images/manual/DemoTool/district_heating_network.png"