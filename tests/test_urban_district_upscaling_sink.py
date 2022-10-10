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
    assert str(sheets["sinks"]["load profile"][0]) == sinks.loc[
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
    # import standard parameter
    standard_parameters = pandas.ExcelFile(
        r"program_files/urban_district_upscaling/standard_parameters.xlsx")
    sheets = {"sinks": pandas.DataFrame()}
    building = {
        "label": "test",
        "building type": "SFB",
        "gross building area": 100,
        "occupants per unit": 5,
        "units": 1,
        "electricity demand": 0,
        "year of construction": 2000,
        "heat demand": 0
    }
    # create a standard_parameter building res electricity bus
    sheets = Sink.create_sinks(
            building=building,
            sheets=sheets,
            standard_parameters=standard_parameters)
    # check annual demand column
    sink = sheets["sinks"].loc[
                sheets["sinks"]["label"] == "test_electricity_demand"]
    # the demand of a single family house with 5 persons is 5000 kWh/a
    assert float(sink["annual demand"]) == 5000
    # check annual demand column
    sink = sheets["sinks"].loc[
        sheets["sinks"]["label"] == "test_heat_demand"]
    # the demand of a single family house build in 2000 is 131 kWh / (sqm * a)
    assert float(sink["annual demand"]) == 131 * 0.9 * 100

    building = {
        "label": "test1",
        "building type": "SFB",
        "gross building area": 100,
        "occupants per unit": 0,
        "units": 1,
        "electricity demand": 100,
        "year of construction": 0,
        "heat demand": 100
    }
    # create a standard_parameter building res electricity bus
    sheets = Sink.create_sinks(
            building=building,
            sheets=sheets,
            standard_parameters=standard_parameters)
    # check annual demand column
    sink = sheets["sinks"].loc[
        sheets["sinks"]["label"] == "test1_electricity_demand"]
    # the given electricity demand is 100 kWh / (sqm * a)
    assert float(sink["annual demand"]) == 100 * 100
    # check annual demand column
    sink = sheets["sinks"].loc[
        sheets["sinks"]["label"] == "test1_heat_demand"]
    # the given electricity demand is 100 kWh / (sqm * a)
    assert float(sink["annual demand"]) == 100 * 100

    building = {
        "label": "test2",
        "building type": "SFB",
        "gross building area": 100,
        "occupants per unit": 6,
        "units": 1,
        "electricity demand": 0,
        "year of construction": 1980,
        "heat demand": 0
    }
    
    # create a standard_parameter building res electricity bus
    sheets = Sink.create_sinks(
            building=building,
            sheets=sheets,
            standard_parameters=standard_parameters)
    # check annual demand column
    sink = sheets["sinks"].loc[
        sheets["sinks"]["label"] == "test2_electricity_demand"]
    # the given electricity demand is 1000 kWh / (occupant * a)
    assert float(sink["annual demand"]) == 1000 * 6 * 1
    # check annual demand column
    sink = sheets["sinks"].loc[
        sheets["sinks"]["label"] == "test2_heat_demand"]
    # the given electricity demand is 100 kWh / (sqm * a)
    assert float(sink["annual demand"]) == 175 * 100 * 0.9

    building = {
        "label": "test3",
        "building type": "COM_Office",
        "gross building area": 100,
        "occupants per unit": 6,
        "units": 1,
        "electricity demand": 0,
        "year of construction": 1980,
        "heat demand": 0
    }
    
    # create a standard_parameter building res electricity bus
    sheets = Sink.create_sinks(
            building=building,
            sheets=sheets,
            standard_parameters=standard_parameters)
    # check annual demand column
    sink = sheets["sinks"].loc[
        sheets["sinks"]["label"] == "test3_electricity_demand"]
    # the given electricity demand is 1000 kWh / (occupant * a)
    assert float(sink["annual demand"]) == 17 * 100 * 0.85
    # check annual demand column
    sink = sheets["sinks"].loc[
        sheets["sinks"]["label"] == "test3_heat_demand"]
    # the given electricity demand is 100 kWh / (sqm * a)
    assert float(sink["annual demand"]) == 136.3 * 100 * 0.85
    

def test_sink_clustering():
    pass


def test_create_cluster_elec_sinks():
    pass
