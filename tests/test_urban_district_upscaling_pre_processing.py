import pandas


def test_append_component():
    from program_files.urban_district_upscaling import pre_processing
    sheets = {"test": pandas.DataFrame()}
    
    test_sheets = {"test": pandas.DataFrame.from_dict({"test": [3]})}
    
    sheets = pre_processing.append_component(sheets, "test", {"test": 3})
    
    pandas.testing.assert_frame_equal(sheets["test"], test_sheets["test"])


def test_read_standard_parameters():
    pass


def test_create_standard_parameter_comp():
    pass


def test_create_buses():
    pass


def test_load_input_data():
    pass


def test_get_central_comp_active_status():
    pass


def test_create_gchp():
    pass


def test_urban_district_upscaling_pre_processing():
    pass