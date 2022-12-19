import pytest
import pandas
from program_files.urban_district_upscaling.components import Sink


@pytest.fixture
def test_elec_sink_entry():
    # import standard parameter
    standard_parameters = pandas.ExcelFile(r"standard_parameters.xlsx")
    sinks = standard_parameters.parse("2_sinks")
    sink = sinks.loc[sinks["sink_type"] == "SFB_electricity_sink"]

    return {
        "sinks": pandas.DataFrame.from_dict({
            "label": ["test_sink"],
            "input": ["test_bus"],
            "annual demand": [3000],
            "active": sink["active"].values,
            "fixed": sink["fixed"].values,
            "load profile": sink["load profile"].values,
            "nominal value": sink["nominal value"].values,
            "occupants": sink["occupants"].values,
            "building class": sink["building class"].values,
            "wind class": sink["wind class"].values,
            "net_floor_area / area": sink["net_floor_area / area"].values})
    }


def test_create_standard_parameter_sink(test_elec_sink_entry):
    sheets = {"sinks": pandas.DataFrame()}
    
    # create a standard_parameter building res electricity bus
    sheets = Sink.create_standard_parameter_sink(
        label="test_sink",
        sink_type="SFB_electricity_sink",
        sink_input="test_bus",
        sheets=sheets,
        annual_demand=3000,
        standard_parameters=pandas.ExcelFile(r"standard_parameters.xlsx"))

    pandas.testing.assert_frame_equal(sheets["sinks"],
                                      test_elec_sink_entry["sinks"])


def test_create_sinks():
    # import standard parameter
    standard_parameters = pandas.ExcelFile(r"standard_parameters.xlsx")
    # import elec demand table
    elec = standard_parameters.parse("2_2_electricity")
    # import heat demand table
    heat = standard_parameters.parse("2_1_heat")
    # import sinks table
    sinks = standard_parameters.parse("2_sinks")
    sheets = {"sinks": pandas.DataFrame()}
    
    # prepare FIRST TEST BUILDING:
    # details: Single family building, 100 sqm building area, yoc 2000,
    # 5 person
    building = {
        "label": "test",
        "building type": "SFB",
        "gross building area": 100,
        "occupants per unit": 5,
        "units": 1,
        "electricity demand": 0,
        "year of construction": 2000,
        "heat demand": 0,
        "distance of electric vehicles": 0
    }
    sheets = Sink.create_sinks(
            building=building,
            sheets=sheets,
            standard_parameters=standard_parameters)
    
    # check annual ELEC DEMAND column
    sink = sheets["sinks"].loc[
                sheets["sinks"]["label"] == "test_electricity_demand"]
    # the demand of a single family house with 5 persons
    assert float(sink["annual demand"][0]) == elec.loc[
        elec["household size"] == "specific demand"]["SFB 5 person"][1]
    
    # check annual HEAT DEMAND column
    sink = sheets["sinks"].loc[
        sheets["sinks"]["label"] == "test_heat_demand"]
    # the demand of a single family house build in 2000
    assert float(sink["annual demand"][0]) == float(heat.loc[
        heat["year of construction"] == 2000]["1 unit(s)"]) \
        * float(sinks.loc[sinks["sink_type"] == "SFB_heat_sink"][
                "net_floor_area / area"]) * 100
    
    # prepare SECOND TEST BUILDING:
    # details: Single family building, energy certificate information
    building = {
        "label": "test1",
        "building type": "SFB",
        "gross building area": 100,
        "occupants per unit": 0,
        "units": 1,
        "electricity demand": 100,
        "year of construction": 0,
        "heat demand": 100,
        "distance of electric vehicles": 0
    }
    sheets = Sink.create_sinks(
            building=building,
            sheets=sheets,
            standard_parameters=standard_parameters)
    
    # check annual ELEC DEMAND column
    sink = sheets["sinks"].loc[
        sheets["sinks"]["label"] == "test1_electricity_demand"]
    # the given electricity demand is 100 kWh / (sqm * a)
    assert float(sink["annual demand"]) == 100 * 100
    
    # check annual HEAT DEMAND column
    sink = sheets["sinks"].loc[
        sheets["sinks"]["label"] == "test1_heat_demand"]
    # the given electricity demand is 100 kWh / (sqm * a)
    assert float(sink["annual demand"]) == 100 * 100
    
    # prepare THIRD TEST BUILDING:
    # details: Single family building, >5 person, yoc 1980
    building = {
        "label": "test2",
        "building type": "SFB",
        "gross building area": 100,
        "occupants per unit": 6,
        "units": 1,
        "electricity demand": 0,
        "year of construction": 1980,
        "heat demand": 0,
        "distance of electric vehicles": 0
    }
    sheets = Sink.create_sinks(
            building=building,
            sheets=sheets,
            standard_parameters=standard_parameters)
    
    # check annual ELEC DEMAND column
    sink = sheets["sinks"].loc[
        sheets["sinks"]["label"] == "test2_electricity_demand"]
    # the given electricity demand is 1000 kWh / (occupant * a) (based
    # on the current value within the standard_parameters 5000 kWh / a
    # / 5 person) * 6 occupants per unit * 1 unit
    assert float(sink["annual demand"]) == elec.loc[
        elec["household size"] == "specific demand"]["SFB 5 person"][1] / 5 \
        * 6 * 1

    # check annual HEAT DEMAND column
    sink = sheets["sinks"].loc[
        sheets["sinks"]["label"] == "test2_heat_demand"]
    # the given heat demand for the specific year of construction
    assert float(sink["annual demand"]) == float(heat.loc[
        heat["year of construction"] == 1980]["1 unit(s)"]) * 100 \
        * float(sinks.loc[sinks["sink_type"] == "SFB_heat_sink"][
                "net_floor_area / area"])
    
    # prepare Forth TEST BUILDING:
    # details: Commercial building, yoc 1980
    building = {
        "label": "test3",
        "building type": "COM_Office",
        "gross building area": 100,
        "occupants per unit": 0,
        "units": 1,
        "electricity demand": 0,
        "year of construction": 1980,
        "heat demand": 0,
        "distance of electric vehicles": 0
    }
    sheets = Sink.create_sinks(
            building=building,
            sheets=sheets,
            standard_parameters=standard_parameters)
    
    # check annual ELEC DEMAND column
    sink = sheets["sinks"].loc[
        sheets["sinks"]["label"] == "test3_electricity_demand"]
    # the given electricity demand
    assert float(sink["annual demand"]) == elec.loc[
        elec["household size"] == "specific demand"][
        "COM_Office"][1] * 100 \
        * float(sinks.loc[sinks["sink_type"] == "COM_Office_electricity_sink"][
                "net_floor_area / area"])
    
    # check annual HEAT DEMAND column
    sink = sheets["sinks"].loc[
        sheets["sinks"]["label"] == "test3_heat_demand"]
    # the given electricity demand is 100 kWh / (sqm * a)
    assert float(sink["annual demand"]) == float(heat.loc[
        heat["year of construction"] == 1980]["COM_Office"]) * 100 \
        * float(sinks.loc[sinks["sink_type"] == "COM_Office_heat_sink"][
                "net_floor_area / area"])

    # prepare Fifth TEST BUILDING:
    # details: Commercial building, energy certificate information
    building = {
        "label": "test4",
        "building type": "COM_Office",
        "gross building area": 100,
        "occupants per unit": 0,
        "units": 1,
        "electricity demand": 1000,
        "year of construction": 0,
        "heat demand": 1000,
        "distance of electric vehicles": 0
    }
    sheets = Sink.create_sinks(
            building=building,
            sheets=sheets,
            standard_parameters=standard_parameters)
    
    # check annual ELEC DEMAND column
    sink = sheets["sinks"].loc[
        sheets["sinks"]["label"] == "test4_electricity_demand"]
    # the given electricity demand is 1000 kWh / (occupant * a)
    assert float(sink["annual demand"]) == 1000 * 100
    
    # check annual HEAT DEMAND column
    sink = sheets["sinks"].loc[
        sheets["sinks"]["label"] == "test4_heat_demand"]
    # the given electricity demand is 100 kWh / (sqm * a)
    assert float(sink["annual demand"]) == 1000 * 100
    

def test_sink_clustering():
    pass


def test_create_cluster_elec_sinks():
    pass
