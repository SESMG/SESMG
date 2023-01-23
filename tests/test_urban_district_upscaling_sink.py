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
    

@pytest.fixture
def test_electric_vehicle_entry():
    """
    
    """
    sheets = {
        "sinks": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_electric_vehicle"],
                "input": ["test_electricity_bus"],
                "nominal value": [float(1)],
                "sink_type": ["EV_electricity_sink"]}),
            right=sinks,
            on="sink_type").drop(columns=["sink_type", "nominal value_y"])}
    
    sheets["sinks"] = sheets["sinks"].rename(columns={
        "nominal value_x": "nominal value"})
    
    return sheets

    
def test_create_sink_ev(test_electric_vehicle_entry):
    """
    
    """
    time_series = \
        pandas.ExcelFile(os.path.dirname(__file__)
                         + "/ev_timeseries.xlsx").parse("ev_timeseries")
    
    sheets = Sink.create_sink_ev(
        building=pandas.Series(data={
            "label": "test",
            "distance of electric vehicles": 10000}),
        sheets={"sinks": pandas.DataFrame(), "time series": time_series},
        standard_parameters=standard_parameters)

    pandas.testing.assert_frame_equal(
        sheets["sinks"].sort_index(axis=1),
        test_electric_vehicle_entry["sinks"].sort_index(axis=1))
    
    assert list(time_series.loc[:, "electric_vehicle.fix"] * 10000) \
           == list(sheets["time series"].loc[:, "test_electric_vehicle.fix"])
    

def test_create_sinks(test_SFB_electricity_sink_entry,
                      test_SFB_heat_sink_entry,
                      test_electric_vehicle_entry):
    """
    
    """
    time_series = \
        pandas.ExcelFile(os.path.dirname(__file__)
                         + "/ev_timeseries.xlsx").parse("ev_timeseries")
    
    sheets = Sink.create_sinks(
        building=pandas.Series({
            "label": "test",
            "building type": "SFB",
            "gross building area": 300,
            "electricity demand": 0,
            "heat demand": 0,
            "occupants per unit": 3,
            "units": 1,
            "year of construction": 2000,
            "distance of electric vehicles": 10000}),
        sheets={"sinks": pandas.DataFrame(),
                "time series": time_series},
        standard_parameters=standard_parameters)
    
    test_sheets = pandas.concat([test_SFB_electricity_sink_entry["sinks"],
                                 test_SFB_heat_sink_entry["sinks"],
                                 test_electric_vehicle_entry["sinks"]])

    pandas.testing.assert_frame_equal(
        sheets["sinks"].sort_index(axis=1),
        test_sheets.sort_index(axis=1))
    

def test_sink_clustering():
    pass


def test_create_cluster_elec_sinks():
    pass
