import pytest
import pandas
from program_files.urban_district_upscaling.components import Bus


def test_create_standard_parameter_bus():
    # import standard parameter
    standard_parameters = pandas.ExcelFile("../program_files/urban_district_upscaling/standard_parameters.xlsx")
    sheets = {"buses": pandas.DataFrame()}
    # create a standard_parameter building res electricity bus
    sheets = Bus.create_standard_parameter_bus(
        "test_bus", "building_res_electricity_bus", sheets, standard_parameters)
    # check the necessary attributes
    assert str(sheets["buses"]["label"][0]) == "test_bus"
    assert int(sheets["buses"]["active"][0]) == 1
    assert int(sheets["buses"]["shortage"][0]) == 1
    assert int(sheets["buses"]["excess"][0]) == 0
    assert int(sheets["buses"]["district heating conn."][0]) == 0
    # add a building heat bus with dh connection
    sheets = Bus.create_standard_parameter_bus(
        "test_bus1", "building_heat_bus", sheets,
        standard_parameters, [10, 10, 1])
    bus = sheets["buses"].loc[sheets["buses"]["label"] == "test_bus1"]
    assert int(bus["district heating conn."]) == 1
    assert int(bus["lat"]) == 10
    assert int(bus["lon"]) == 10
    # check rather an exception is raised by choosing a wrong bus type
    # pytest.raises(
    #    ValueError,
    #    Bus.create_standard_parameter_bus(
    #          "test_bus2", "non-existing-type", sheets, standard_parameters))
    
    
def test_create_cluster_elec_buses():
    pass


def test_create_cluster_averaged_bus():
    pass

