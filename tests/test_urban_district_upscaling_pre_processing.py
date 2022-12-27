import pandas
import os


def test_append_component():
    """

    """
    from program_files.urban_district_upscaling.pre_processing \
        import append_component
    sheets = {"test": pandas.DataFrame()}
    
    test_sheets = {"test": pandas.DataFrame.from_dict({"test": [3]})}
    
    sheets = append_component(
        sheets=sheets,
        sheet="test",
        comp_parameter={"test": 3})
    
    pandas.testing.assert_frame_equal(sheets["test"], test_sheets["test"])


def test_read_standard_parameters():
    """
    
    """
    from program_files.urban_district_upscaling.pre_processing \
        import read_standard_parameters
    
    standard_parameters, standard_keys = read_standard_parameters(
        name="building_heat_bus",
        param_type="1_buses",
        index="bus_type",
        standard_parameters=pandas.ExcelFile(os.path.dirname(__file__)
                                             + "/standard_parameters.xlsx")
    )
    
    # import standard parameter
    standard_parameters_file = pandas.ExcelFile(os.path.dirname(__file__)
                                                + "/standard_parameters.xlsx")
    buses = standard_parameters_file.parse("1_buses")
    
    # create test dataframes
    test_standard_parameters = buses.loc[
        buses["bus_type"] == "building_heat_bus"].set_index("bus_type").squeeze()
    test_standard_keys = test_standard_parameters.keys()
    
    pandas.testing.assert_series_equal(standard_parameters,
                                       test_standard_parameters)
    
    assert list(standard_keys) == list(test_standard_keys)


def test_create_standard_parameter_comp(
        test_storage_decentralized_battery_entry):
    """
    
    """
    from program_files.urban_district_upscaling.pre_processing \
        import create_standard_parameter_comp
    sheets = {"storages": pandas.DataFrame()}
    
    sheets = create_standard_parameter_comp(
        specific_param={"label": "test_building_battery_storage",
                        "bus": "test_building_electricity_bus"},
        standard_parameter_info=["building_battery_storage", "5_storages",
                                 "storage_type"],
        sheets=sheets,
        standard_parameters=pandas.ExcelFile(os.path.dirname(__file__)
                                             + "/standard_parameters.xlsx")
    )
    
    pandas.testing.assert_frame_equal(
        sheets["storages"],
        test_storage_decentralized_battery_entry["storages"])


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