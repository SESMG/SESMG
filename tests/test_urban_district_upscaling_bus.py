import pytest
import pandas
from program_files.urban_district_upscaling.components import Bus


def test_create_standard_parameter_bus():
    # import standard parameter
    standard_parameters = pandas.ExcelFile(
        r"program_files/urban_district_upscaling/standard_parameters.xlsx")
    buses = standard_parameters.parse("buses")
    sheets = {"buses": pandas.DataFrame()}
    # create a standard_parameter building res electricity bus
    sheets = Bus.create_standard_parameter_bus(
        label="test_bus",
        bus_type="building_res_electricity_bus",
        sheets=sheets,
        standard_parameters=standard_parameters)
    # check the necessary attributes
    assert str(sheets["buses"]["label"][0]) == "test_bus"
    # check active column
    assert int(sheets["buses"]["active"][0]) == buses.loc[
        buses["bus_type"] == "building_res_electricity_bus"]["active"][0]
    # check shortage column
    assert int(sheets["buses"]["shortage"][0]) == buses.loc[
        buses["bus_type"] == "building_res_electricity_bus"]["shortage"][0]
    # check excess column
    assert int(sheets["buses"]["excess"][0]) == buses.loc[
        buses["bus_type"] == "building_res_electricity_bus"]["excess"][0]
    # check shortage costs
    assert float(sheets["buses"]["shortage costs"][0]) == buses.loc[
        buses["bus_type"] == "building_res_electricity_bus"][
        "shortage costs"][0]
    # check excess costs
    assert float(sheets["buses"]["excess costs"][0]) == buses.loc[
        buses["bus_type"] == "building_res_electricity_bus"]["excess costs"][0]
    # check shortage constraint costs
    assert float(sheets["buses"]["shortage constraint costs"][0]) == buses.loc[
        buses["bus_type"] == "building_res_electricity_bus"][
        "shortage constraint costs"][0]
    # check excess constraint costs
    assert float(sheets["buses"]["excess constraint costs"][0]) == buses.loc[
        buses["bus_type"] == "building_res_electricity_bus"][
        "excess constraint costs"][0]
    # since there is no parameter coords in line 13 - 17 district
    # heating conn. has to be 0
    assert int(sheets["buses"]["district heating conn."][0]) == 0
    
    # add a building heat bus with dh connection
    sheets = Bus.create_standard_parameter_bus(
        "test_bus1", "building_heat_bus", sheets,
        standard_parameters, [10, 10, 1])
    bus = sheets["buses"].loc[sheets["buses"]["label"] == "test_bus1"]
    assert int(bus["district heating conn."]) == 1
    assert int(bus["lat"]) == 10
    assert int(bus["lon"]) == 10
    
    
def test_create_cluster_elec_buses():
    pass


def test_create_cluster_averaged_bus():
    pass

