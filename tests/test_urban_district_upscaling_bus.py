import pytest
import pandas
from program_files.urban_district_upscaling.components import Bus


@pytest.fixture
def test_elec_bus_entry():
    # import standard parameter
    standard_parameters = pandas.ExcelFile(r"standard_parameters.xlsx")
    buses = standard_parameters.parse("1_buses")
    bus = buses.loc[buses["bus_type"] == "building_res_electricity_bus"]

    return {
        "buses": pandas.DataFrame.from_dict({
            "label": ["test_bus"],
            "active": bus["active"].values,
            "excess": bus["excess"].values,
            "shortage": bus["shortage"].values,
            "excess costs": bus["excess costs"].values,
            "shortage costs": bus["shortage costs"].values,
            "excess constraint costs": bus["excess constraint costs"].values,
            "shortage constraint costs": bus["shortage constraint costs"].values,
            "district heating conn.": [0]})
    }


@pytest.fixture
def test_heat_bus_entry():
    # import standard parameter
    standard_parameters = pandas.ExcelFile(r"standard_parameters.xlsx")
    buses = standard_parameters.parse("1_buses")
    bus = buses.loc[buses["bus_type"] == "building_heat_bus"]

    return {
        "buses": pandas.DataFrame.from_dict({
            "label": ["test_bus1"],
            "active": bus["active"].values,
            "excess": bus["excess"].values,
            "shortage": bus["shortage"].values,
            "excess costs": bus["excess costs"].values,
            "shortage costs": bus["shortage costs"].values,
            "excess constraint costs": bus["excess constraint costs"].values,
            "shortage constraint costs": bus["shortage constraint costs"].values,
            "district heating conn.": [1],
            "lat": [10],
            "lon": [10]})
    }


def test_create_standard_parameter_bus(test_elec_bus_entry,
                                       test_heat_bus_entry):
    """
        Short description of the given TEST Suite
    """
    sheets = {"buses": pandas.DataFrame()}
    # create a standard_parameter building res electricity bus
    sheets = Bus.create_standard_parameter_bus(
        label="test_bus",
        bus_type="building_res_electricity_bus",
        sheets=sheets,
        standard_parameters=pandas.ExcelFile(r"standard_parameters.xlsx")
    )
    pandas.testing.assert_frame_equal(sheets["buses"],
                                      test_elec_bus_entry["buses"])
    
    sheets = {"buses": pandas.DataFrame()}
    # add a building heat bus with dh connection
    sheets = Bus.create_standard_parameter_bus(
        label="test_bus1",
        bus_type="building_heat_bus",
        sheets=sheets,
        standard_parameters=pandas.ExcelFile(r"standard_parameters.xlsx"),
        coords=[10, 10, 1])
    pandas.testing.assert_frame_equal(sheets["buses"],
                                      test_heat_bus_entry["buses"])
    
    
def test_create_cluster_elec_buses():
    pass


def test_create_cluster_averaged_bus():
    pass

