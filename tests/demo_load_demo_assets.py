def load_demo_assets(read_md_func, image_loader_func, get_path_func) -> dict:
    """
    Loads text and images needed for the demo page, in a testable way.

    :param read_md_func: function for reading markdown files
    :param image_loader_func: function to open images
    :param get_path_func: function to get the base directory (like get_bundle_dir)
    :return: dictionary with loaded text and images

    """
    assets = {}

    # Opening texts
    assets["intro_text"] = ''.join(read_md_func(
        document_path="docs/GUI_texts/demo_tool_text.md",
        folder_path="docs/images/manual/DemoTool/*",
        fixed_image_width=500
    ))

    # System image
    image_path_system = get_path_func() + "/docs/images/manual/DemoTool/demo_system_graph.png"
    assets["system_image"] = image_loader_func(image_path_system)

    # Table texts
    assets["table_text"] = ''.join(read_md_func(
        document_path="docs/GUI_texts/demo_tool_tables.md",
        folder_path="docs/images/manual/DemoTool/*"
    ))

    # Heating network image
    image_path_dh = get_path_func() + "/docs/images/manual/DemoTool/district_heating_network.png"
    assets["dh_image"] = image_loader_func(image_path_dh)

    return assets
