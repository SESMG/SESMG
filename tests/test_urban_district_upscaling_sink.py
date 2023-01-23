import pytest
import pandas
from program_files.urban_district_upscaling.components import Sink
import os

# import standard parameter
standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                       + "/standard_parameters.xlsx")
sinks = standard_parameters.parse("2_sinks")


@pytest.fixture
def test_SFB_electricity_sink_entry():
    """
    
    """
    return {
        "sinks": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_electricity_demand"],
                "input": ["test_electricity_bus"],
                "annual demand": [3600],
                "sink_type": ["SFB_electricity_sink"]}),
            right=sinks,
            on="sink_type").drop(columns=["sink_type"])}


@pytest.fixture
def test_MFB_electricity_sink_entry():
    """

    """
    return {
        "sinks": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_electricity_demand"],
                "input": ["test_electricity_bus"],
                "annual demand": [4320.0],
                "sink_type": ["MFB_electricity_sink"]}),
            right=sinks,
            on="sink_type").drop(columns=["sink_type"])}


@pytest.fixture
def test_COM_electricity_sink_entry():
    """

    """
    return {
        "sinks": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_electricity_demand"],
                "input": ["test_electricity_bus"],
                "annual demand": [102060.0],
                "sink_type": ["COM_Food_electricity_sink"]}),
            right=sinks,
            on="sink_type").drop(columns=["sink_type"])}


@pytest.fixture
def test_COM_electricity_sink_entry():
    """

    """
    return {
        "sinks": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_electricity_demand"],
                "input": ["test_electricity_bus"],
                "annual demand": [102060.0],
                "sink_type": ["COM_Food_electricity_sink"]}),
            right=sinks,
            on="sink_type").drop(columns=["sink_type"])}


@pytest.fixture
def test_certificate_electricity_sink_entry():
    """

    """
    return {
        "sinks": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_electricity_demand"],
                "input": ["test_electricity_bus"],
                "annual demand": [3000],
                "sink_type": ["COM_Food_electricity_sink"]}),
            right=sinks,
            on="sink_type").drop(columns=["sink_type"])}


def test_create_standard_parameter_sink(test_SFB_electricity_sink_entry):
    """
    
    """
    # create a standard_parameter building res electricity bus
    sheets = Sink.create_standard_parameter_sink(
        label="test_electricity_demand",
        sink_type="SFB_electricity_sink",
        sink_input="test_electricity_bus",
        sheets={"sinks": pandas.DataFrame()},
        annual_demand=3600,
        standard_parameters=standard_parameters)

    pandas.testing.assert_frame_equal(
        sheets["sinks"].sort_index(axis=1),
        test_SFB_electricity_sink_entry["sinks"].sort_index(axis=1))


def test_create_electricity_sink(test_SFB_electricity_sink_entry,
                                 test_MFB_electricity_sink_entry,
                                 test_COM_electricity_sink_entry,
                                 test_certificate_electricity_sink_entry):
    """
        To test the creation process of electricity sinks four different
        sinks are created:
        
        1. A SFB Sink with 3 occupants per unit and 1 unit
        2. A MFB Sink with 6 occupants per unit and 1 unit
        3. A COM Food Sink with 300 square meter
        4. A COM Food Sink with an area specific demand (certificate)
    """
    if type(sinks.index) == pandas.RangeIndex:
        sinks.set_index("sink_type", inplace=True)
    sheets = Sink.create_electricity_sink(
        building=pandas.Series(data={
            "label": "test",
            "building type": "SFB",
            "electricity demand": 0,
            "occupants per unit": 3,
            "units": 1}),
        area=0,
        sheets={"sinks": pandas.DataFrame()},
        sinks_standard_param=sinks,
        standard_parameters=standard_parameters)

    pandas.testing.assert_frame_equal(
        sheets["sinks"].sort_index(axis=1),
        test_SFB_electricity_sink_entry["sinks"].sort_index(axis=1))

    sheets = Sink.create_electricity_sink(
        building=pandas.Series(data={
            "label": "test",
            "building type": "MFB",
            "electricity demand": 0,
            "occupants per unit": 6,
            "units": 1}),
        area=0,
        sheets={"sinks": pandas.DataFrame()},
        sinks_standard_param=sinks,
        standard_parameters=standard_parameters)

    pandas.testing.assert_frame_equal(
        sheets["sinks"].sort_index(axis=1),
        test_MFB_electricity_sink_entry["sinks"].sort_index(axis=1))

    sheets = Sink.create_electricity_sink(
        building=pandas.Series(data={
            "label": "test",
            "building type": "COM_Food",
            "electricity demand": 0,
            "occupants per unit": 0,
            "units": 1}),
        area=300,
        sheets={"sinks": pandas.DataFrame()},
        sinks_standard_param=sinks,
        standard_parameters=standard_parameters)

    pandas.testing.assert_frame_equal(
        sheets["sinks"].sort_index(axis=1),
        test_COM_electricity_sink_entry["sinks"].sort_index(axis=1))

    sheets = Sink.create_electricity_sink(
        building=pandas.Series(data={
            "label": "test",
            "building type": "COM_Food",
            "electricity demand": 10,
            "occupants per unit": 0,
            "units": 0}),
        area=300,
        sheets={"sinks": pandas.DataFrame()},
        sinks_standard_param=sinks,
        standard_parameters=standard_parameters)

    pandas.testing.assert_frame_equal(
        sheets["sinks"].sort_index(axis=1),
        test_certificate_electricity_sink_entry["sinks"].sort_index(axis=1))


@pytest.fixture
def test_SFB_heat_sink_entry():
    """
    
    """
    return {
        "sinks": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_heat_demand"],
                "input": ["test_heat_bus"],
                "annual demand": [131.0 * 300 * 0.9],
                "sink_type": ["SFB_heat_sink"]}),
            right=sinks,
            on="sink_type").drop(columns=["sink_type"])}


@pytest.fixture
def test_COM_heat_sink_entry():
    """

    """
    return {
        "sinks": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_heat_demand"],
                "input": ["test_heat_bus"],
                "annual demand": [275.0 * 300 * 0.9],
                "sink_type": ["COM_Food_heat_sink"]}),
            right=sinks,
            on="sink_type").drop(columns=["sink_type"])}


@pytest.fixture
def test_certificate_heat_sink_entry():
    """

    """
    return {
        "sinks": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_heat_demand"],
                "input": ["test_heat_bus"],
                "annual demand": [3000],
                "sink_type": ["COM_Food_heat_sink"]}),
            right=sinks,
            on="sink_type").drop(columns=["sink_type"])}


def test_create_heat_sink(test_SFB_heat_sink_entry,
                          test_COM_heat_sink_entry,
                          test_certificate_heat_sink_entry):
    """
        To test the creation process of electricity sinks four different
        sinks are created:
    
        1. A SFB Sink with 3 occupants per unit and 1 unit
        2. A MFB Sink with 6 occupants per unit and 1 unit
        3. A COM Food Sink with 300 square meter
        4. A COM Food Sink with an area specific demand (certificate)
    """
    if type(sinks.index) == pandas.RangeIndex:
        sinks.set_index("sink_type", inplace=True)
    sheets = Sink.create_heat_sink(
        building=pandas.Series(data={
            "label": "test",
            "building type": "SFB",
            "year of construction": 2000,
            "heat demand": 0,
            "units": 1}),
        area=300,
        sheets={"sinks": pandas.DataFrame()},
        sinks_standard_param=sinks,
        standard_parameters=standard_parameters)

    pandas.testing.assert_frame_equal(
        sheets["sinks"].sort_index(axis=1),
        test_SFB_heat_sink_entry["sinks"].sort_index(axis=1))

    sheets = Sink.create_heat_sink(
        building=pandas.Series(data={
            "label": "test",
            "building type": "COM_Food",
            "year of construction": 1980,
            "heat demand": 0,
            "units": 1}),
        area=300,
        sheets={"sinks": pandas.DataFrame()},
        sinks_standard_param=sinks,
        standard_parameters=standard_parameters)

    pandas.testing.assert_frame_equal(
        sheets["sinks"].sort_index(axis=1),
        test_COM_heat_sink_entry["sinks"].sort_index(axis=1))

    sheets = Sink.create_heat_sink(
        building=pandas.Series(data={
            "label": "test",
            "building type": "COM_Food",
            "year of construction": 0,
            "heat demand": 10,
            "units": 0}),
        area=300,
        sheets={"sinks": pandas.DataFrame()},
        sinks_standard_param=sinks,
        standard_parameters=standard_parameters)

    pandas.testing.assert_frame_equal(
        sheets["sinks"].sort_index(axis=1),
        test_certificate_heat_sink_entry["sinks"].sort_index(axis=1))
  

@pytest.mark.skip
def test_create_sinks():
    """
        Within this test method 5 different types of buildings and their
        sinks are created. Furthermore the building specific attributes
        as e.g. the annual demand are calculated manually and compared
        with the value resulting from the create sinks method.
        
        FIRST TEST BUILDING:
        details:
            - Single family building,
            - 100 sqm building area,
            - yoc 2000,
            - 5 person
            
        SECOND TEST BUILDING:
        details:
            - Single family building,
            - energy certificate information
    """
    # import elec demand table
    elec = standard_parameters.parse("2_2_electricity")
    elec = elec.loc[elec["household size"] == "specific demand"]
    # import heat demand table
    heat = standard_parameters.parse("2_1_heat")
    
    # FIRST TEST BUILDING:
    # details:
    #   - Single family building,
    #   - 100 sqm building area,
    #   - yoc 2000,
    #   - 5 person
    sink_sheet = Sink.create_sinks(
        building={
            "label": "test",
            "building type": "SFB",
            "gross building area": 100,
            "occupants per unit": 5,
            "units": 1,
            "electricity demand": 0,
            "year of construction": 2000,
            "heat demand": 0,
            "distance of electric vehicles": 0},
        sheets={"sinks": pandas.DataFrame()},
        standard_parameters=standard_parameters)["sinks"]
    
    # check annual ELEC DEMAND column
    sink = sink_sheet.loc[sink_sheet["label"] == "test_electricity_demand"]
    # the demand of a single family house with 5 persons
    assert float(sink["annual demand"][0]) == elec["SFB 5 person"][1]
    
    # check annual HEAT DEMAND column
    sink = sink_sheet.loc[sink_sheet["label"] == "test_heat_demand"]
    yoc_heat = heat.loc[heat["year of construction"] == 2000]
    NFA_GFA = sinks.loc[sinks["sink_type"] == "SFB_heat_sink"][
                "net_floor_area / area"]
    # demand = specific demand for 1 unit (details) * Net Floor Area /
    # Gross Floor Area * gross building area (details)
    ref_demand = float(yoc_heat["1 unit(s)"]) * float(NFA_GFA) * 100
    # the demand of a single family house build in 2000
    assert float(sink["annual demand"][0]) == ref_demand
    
    # SECOND TEST BUILDING:
    # details:
    #   - Single family building,
    #   - energy certificate information
    sink_sheet = Sink.create_sinks(
        building={
            "label": "test1",
            "building type": "SFB",
            "gross building area": 100,
            "occupants per unit": 0,
            "units": 1,
            "electricity demand": 100,
            "year of construction": 0,
            "heat demand": 100,
            "distance of electric vehicles": 0},
        sheets={"sinks": pandas.DataFrame()},
        standard_parameters=standard_parameters)["sinks"]
    
    # check annual ELEC DEMAND column
    sink = sink_sheet.loc[sink_sheet["label"] == "test1_electricity_demand"]
    # the given electricity demand is 100 kWh / (sqm * a)
    assert float(sink["annual demand"]) == 100 * 100
    
    # check annual HEAT DEMAND column
    sink = sink_sheet.loc[sink_sheet["label"] == "test1_heat_demand"]
    # the given electricity demand is 100 kWh / (sqm * a)
    assert float(sink["annual demand"]) == 100 * 100
    
    # THIRD TEST BUILDING:
    # details:
    #   - Single family building,
    #   - >5 person,
    #   - yoc 1980
    sheets = Sink.create_sinks(
        building={
            "label": "test2",
            "building type": "SFB",
            "gross building area": 100,
            "occupants per unit": 6,
            "units": 1,
            "electricity demand": 0,
            "year of construction": 1980,
            "heat demand": 0,
            "distance of electric vehicles": 0},
        sheets={"sinks": pandas.DataFrame()},
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
            sheets={"sinks": pandas.DataFrame()},
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
            sheets={"sinks": pandas.DataFrame()},
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
