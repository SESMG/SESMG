import pytest
import pandas
from program_files.urban_district_upscaling.components import Sink


def test_create_standard_parameter_sink():
    # import standard parameter
    standard_parameters = pandas.ExcelFile(
        r"program_files/urban_district_upscaling/standard_parameters.xlsx")
    sinks = standard_parameters.parse("sinks")
    sheets = {"sinks": pandas.DataFrame()}
    
    # create a standard_parameter building res electricity bus
    sheets = Sink.create_standard_parameter_sink(
        label="test_sink",
        sink_type="RES_electricity_sink",
        sink_input="test_bus",
        sheets=sheets,
        annual_demand=3000,
        standard_parameters=standard_parameters)
    # check the necessary attributes
    assert str(sheets["sinks"]["label"][0]) == "test_sink"
    # check active column
    assert int(sheets["sinks"]["active"][0]) == sinks.loc[
        sinks["sink_type"] == "RES_electricity_sink"]["active"][0]
    # check input column
    assert str(sheets["sinks"]["input"][0]) == "test_bus"
    # check annual demand column
    assert float(sheets["sinks"]["annual demand"][0]) == 3000
    # check fixed column
    assert float(sheets["sinks"]["fixed"][0]) == sinks.loc[
        sinks["sink_type"] == "RES_electricity_sink"][
        "fixed"][0]
    # check load profile
    assert float(sheets["sinks"]["load profile"][0]) == sinks.loc[
        sinks["sink_type"] == "RES_electricity_sink"]["load profile"][0]
    # check nominal value
    assert float(sheets["sinks"]["nominal value"][0]) == sinks.loc[
        sinks["sink_type"] == "RES_electricity_sink"][
        "nominal value"][0]
    # check occupants
    assert float(sheets["sinks"]["occupants"][0]) == sinks.loc[
        sinks["sink_type"] == "RES_electricity_sink"][
        "occupants"][0]
    # check building class
    assert float(sheets["sinks"]["building class"][0]) == sinks.loc[
        sinks["sink_type"] == "RES_electricity_sink"][
        "building class"][0]
    # check wind class
    assert float(sheets["sinks"]["wind class"][0]) == sinks.loc[
        sinks["sink_type"] == "RES_electricity_sink"][
        "wind class"][0]


def test_create_sinks():
    pass


def test_sink_clustering():
    pass


def test_create_cluster_elec_sinks():
    pass
