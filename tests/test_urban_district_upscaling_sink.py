import pytest
import pandas
from tests.conftest import (get_standard_parameter_data,
                            import_standard_parameter_data)
from program_files.urban_district_upscaling.components import Sink
import os


@pytest.fixture
def test_SFB_electricity_sink_entry():
    """
        Manually create a dataset of a single family builing
        electricity sink entry.
    """
    return {
        "sinks": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_electricity_demand"],
                "input": ["test_electricity_bus"],
                "annual demand": [3600],
                "sink type": ["single family building electricity sink"]}),
            right=import_standard_parameter_data(label="2_sinks"),
            on="sink type").drop(columns=["sink type"])}


@pytest.fixture
def test_MFB_electricity_sink_entry():
    """
        Manually create a dataset of a multi family building
        electricity sink entry.
    """
    return {
        "sinks": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_electricity_demand"],
                "input": ["test_electricity_bus"],
                "annual demand": [4320.0],
                "sink type": ["multi family building electricity sink"]}),
            right=import_standard_parameter_data(label="2_sinks"),
            on="sink type").drop(columns=["sink type"])}


@pytest.fixture
def test_COM_electricity_sink_entry():
    """
        Manually create a dataset of a commercial food building
        electricity sink entry.
    """
    return {
        "sinks": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_electricity_demand"],
                "input": ["test_electricity_bus"],
                "annual demand": [102060.0],
                "sink type": ["commercial food electricity sink"]}),
            right=import_standard_parameter_data(label="2_sinks"),
            on="sink type").drop(columns=["sink type"])}


@pytest.fixture
def test_certificate_electricity_sink_entry():
    """
        Manually create a dataset of a commercial food building
        electricity sink entry with the use of an energy certificate.
    """
    return {
        "sinks": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_electricity_demand"],
                "input": ["test_electricity_bus"],
                "annual demand": [3000],
                "sink type": ["commercial food electricity sink"]}),
            right=import_standard_parameter_data(label="2_sinks"),
            on="sink type").drop(columns=["sink type"])}


def test_create_standard_parameter_sink(test_SFB_electricity_sink_entry):
    """
        Create a standard parameter single family building electricity
        sink and compare it to the manual created one to validate the
        functionality of the creation process.
    """
    # create a standard_parameter building res electricity bus
    sheets = Sink.create_standard_parameter_sink(
        label="test_electricity_demand",
        sink_type="single family building electricity sink",
        sink_input="test_electricity_bus",
        sheets={"sinks": pandas.DataFrame()},
        annual_demand=3600,
        standard_parameters=get_standard_parameter_data())

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
    sinks = import_standard_parameter_data(label="2_sinks")
    if isinstance(sinks.index, pandas.RangeIndex):
        sinks.set_index("sink type", inplace=True)
    sheets = Sink.create_electricity_sink(
        building=pandas.Series(data={
            "label": "test",
            "building type": "single family building",
            "electricity demand": 0,
            "occupants per unit": 3,
            "units": 1}),
        area=0,
        sheets={"sinks": pandas.DataFrame()},
        sinks_standard_param=sinks,
        standard_parameters=get_standard_parameter_data())

    pandas.testing.assert_frame_equal(
        sheets["sinks"].sort_index(axis=1),
        test_SFB_electricity_sink_entry["sinks"].sort_index(axis=1))

    sheets = Sink.create_electricity_sink(
        building=pandas.Series(data={
            "label": "test",
            "building type": "multi family building",
            "electricity demand": 0,
            "occupants per unit": 6,
            "units": 1}),
        area=0,
        sheets={"sinks": pandas.DataFrame()},
        sinks_standard_param=sinks,
        standard_parameters=get_standard_parameter_data())

    pandas.testing.assert_frame_equal(
        sheets["sinks"].sort_index(axis=1),
        test_MFB_electricity_sink_entry["sinks"].sort_index(axis=1))

    sheets = Sink.create_electricity_sink(
        building=pandas.Series(data={
            "label": "test",
            "building type": "commercial food",
            "electricity demand": 0,
            "occupants per unit": 0,
            "units": 1}),
        area=300,
        sheets={"sinks": pandas.DataFrame()},
        sinks_standard_param=sinks,
        standard_parameters=get_standard_parameter_data())

    pandas.testing.assert_frame_equal(
        sheets["sinks"].sort_index(axis=1),
        test_COM_electricity_sink_entry["sinks"].sort_index(axis=1))

    sheets = Sink.create_electricity_sink(
        building=pandas.Series(data={
            "label": "test",
            "building type": "commercial food",
            "electricity demand": 10,
            "occupants per unit": 0,
            "units": 0}),
        area=300,
        sheets={"sinks": pandas.DataFrame()},
        sinks_standard_param=sinks,
        standard_parameters=get_standard_parameter_data())

    pandas.testing.assert_frame_equal(
        sheets["sinks"].sort_index(axis=1),
        test_certificate_electricity_sink_entry["sinks"].sort_index(axis=1))


@pytest.fixture
def test_SFB_heat_sink_entry():
    """
        Manually create a dataset of a single family building heat sink
        entry.
    """
    return {
        "sinks": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_heat_demand"],
                "input": ["test_heat_bus"],
                "annual demand": [131.0 * 300 * 0.9],
                "sink type": ["single family building heat sink"]}),
            right=import_standard_parameter_data(label="2_sinks"),
            on="sink type").drop(columns=["sink type"])}


@pytest.fixture
def test_COM_heat_sink_entry():
    """
        Manually create a dataset of a commercial food building heat
        sink entry.
    """
    return {
        "sinks": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_heat_demand"],
                "input": ["test_heat_bus"],
                "annual demand": [275.0 * 300 * 0.9],
                "sink type": ["commercial food heat sink"]}),
            right=import_standard_parameter_data(label="2_sinks"),
            on="sink type").drop(columns=["sink type"])}


@pytest.fixture
def test_certificate_heat_sink_entry():
    """
        Manually create a dataset of a commercial food building
        heat sink entry with the use of an energy certificate.
    """
    return {
        "sinks": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_heat_demand"],
                "input": ["test_heat_bus"],
                "annual demand": [3000],
                "sink type": ["commercial food heat sink"]}),
            right=import_standard_parameter_data(label="2_sinks"),
            on="sink type").drop(columns=["sink type"])}


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
    sinks = import_standard_parameter_data(label="2_sinks")
    if isinstance(sinks.index, pandas.RangeIndex):
        sinks.set_index("sink type", inplace=True)
    sheets = Sink.create_heat_sink(
        building=pandas.Series(data={
            "label": "test",
            "building type": "single family building",
            "year of construction": 2000,
            "heat demand": 0,
            "units": 1,
            "wood stove share": "standard",
            "solar thermal share": "standard"}),
        area=300,
        sheets={"sinks": pandas.DataFrame()},
        sinks_standard_param=sinks,
        standard_parameters=get_standard_parameter_data())

    pandas.testing.assert_frame_equal(
        sheets["sinks"].sort_index(axis=1),
        test_SFB_heat_sink_entry["sinks"].sort_index(axis=1))

    sheets = Sink.create_heat_sink(
        building=pandas.Series(data={
            "label": "test",
            "building type": "commercial food",
            "year of construction": 1980,
            "heat demand": 0,
            "units": 1,
            "wood stove share": "standard",
            "solar thermal share": "standard"}),
        area=300,
        sheets={"sinks": pandas.DataFrame()},
        sinks_standard_param=sinks,
        standard_parameters=get_standard_parameter_data())

    pandas.testing.assert_frame_equal(
        sheets["sinks"].sort_index(axis=1),
        test_COM_heat_sink_entry["sinks"].sort_index(axis=1))

    sheets = Sink.create_heat_sink(
        building=pandas.Series(data={
            "label": "test",
            "building type": "commercial food",
            "year of construction": 0,
            "heat demand": 10,
            "units": 0,
            "wood stove share": "standard",
            "solar thermal share": "standard"}),
        area=300,
        sheets={"sinks": pandas.DataFrame()},
        sinks_standard_param=sinks,
        standard_parameters=get_standard_parameter_data())

    pandas.testing.assert_frame_equal(
        sheets["sinks"].sort_index(axis=1),
        test_certificate_heat_sink_entry["sinks"].sort_index(axis=1))
    

@pytest.fixture
def test_electric_vehicle_entry():
    """
        Manually create a dataset of an ev sink for an electric vehicle
        with an annual usage of 10000 km.
    """
    sheets = {
        "sinks": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_electric_vehicle"],
                "input": ["test_electricity_bus"],
                "nominal value": [1],
                "annual demand": [0],
                "sink type": ["electric vehicle electricity sink"]}),
            right=import_standard_parameter_data(label="2_sinks"),
            on="sink type").drop(columns=["sink type", "nominal value_y"])}
    
    sheets["sinks"] = sheets["sinks"].rename(columns={
        "nominal value_x": "nominal value"})
    
    return sheets

    
def test_create_sink_ev(test_electric_vehicle_entry):
    """
        Create a standard parameter ev sink and compare it to the
        manual created one to validate the functionality of the
        creation process.
    """
    time_series = \
        pandas.ExcelFile(os.path.dirname(__file__)
                         + "/ev_timeseries.xlsx").parse(
                "ev_timeseries", na_filter=False)
    
    sheets = Sink.create_sink_ev(
        building=pandas.Series(data={
            "label": "test",
            "distance of electric vehicles": 10000}),
        sheets={"sinks": pandas.DataFrame(), "time series": time_series},
        standard_parameters=get_standard_parameter_data())

    print(sheets["sinks"].columns)
    print(test_electric_vehicle_entry["sinks"].columns)
    pandas.testing.assert_frame_equal(
        sheets["sinks"].sort_index(axis=1),
        test_electric_vehicle_entry["sinks"].sort_index(axis=1))
    
    assert list(time_series.loc[:, "electric_vehicle.fix"] * 10000) \
           == list(sheets["time series"].loc[:, "test_electric_vehicle.fix"])
    

def test_create_sinks(test_SFB_electricity_sink_entry,
                      test_SFB_heat_sink_entry,
                      test_electric_vehicle_entry):
    """
        Create all standard parameter sinks of a single family building
        driving an electric vehicle.
    """
    time_series = \
        pandas.ExcelFile(os.path.dirname(__file__)
                         + "/ev_timeseries.xlsx").parse("ev_timeseries",
                                                        na_filter=False)
    
    sheets = Sink.create_sinks(
        building=pandas.Series({
            "label": "test",
            "building type": "single family building",
            "gross building area": 300,
            "electricity demand": 0,
            "heat demand": 0,
            "occupants per unit": 3,
            "units": 1,
            "year of construction": 2000,
            "distance of electric vehicles": 10000,
            "wood stove share": "standard",
            "solar thermal share": "standard"}),
        sheets={"sinks": pandas.DataFrame(),
                "time series": time_series},
        standard_parameters=get_standard_parameter_data())
    
    test_sheets = pandas.concat([test_SFB_electricity_sink_entry["sinks"],
                                 test_SFB_heat_sink_entry["sinks"],
                                 test_electric_vehicle_entry["sinks"]])

    pandas.testing.assert_frame_equal(
        sheets["sinks"].sort_index(axis=1),
        test_sheets.sort_index(axis=1))
    

def test_sink_clustering():
    """
        Test the collection of the sinks parameter to be clustered
        afterward. Within this method all three types of buildings
        are tested (residential, commercial and industrial).
    """
    results = {
        "single family building_electricity":
            [3000, 0, 0, [], 0, 0, 0, [], ["test_electricity_sink"], [], []],
        "single family building_heat":
            [0, 0, 0, [("single family building", "test_heat_bus")], 3000, 0, 0,
             [("single family building", "test_heat_sink")], [], [], []],
        "commercial_electricity":
            [0, 3000, 0, [], 0, 0, 0, [], [], ["test_electricity_sink"], []],
        "commercial_heat":
            [0, 0, 0, [("commercial", "test_heat_bus")], 0, 3000, 0,
             [("commercial", "test_heat_sink")], [], [], []],
        "industrial_electricity":
            [0, 0, 3000, [], 0, 0, 0, [], [], [], ["test_electricity_sink"]],
        "industrial_heat":
            [0, 0, 0, [("industrial", "test_heat_bus")], 0, 0, 3000,
             [("industrial", "test_heat_sink")], [], [], []]}
    
    for i in ["single family building", "commercial", "industrial"]:
        for j in ["electricity", "heat"]:
            # electricity sink clustering
            sink_parameters = Sink.sink_clustering(
                building=["test", "test_parcel", i],
                sink=pandas.Series({
                    "label": "test_" + j + "_sink",
                    "input": "test_" + j + "_bus",
                    "annual demand": 3000}),
                sink_parameters=[0, 0, 0, [], 0, 0, 0, [], [], [], []])
            
            assert sink_parameters == results.get(i + "_" + j)
            

@pytest.fixture
def test_cluster_electricity_sinks_entries():
    """
        Create a dataset of cluster intern electricity sinks.
    """
    sheets = {
        "sinks": pandas.DataFrame.from_dict({
                "label": ["test_electricity_sink",
                          "test1_electricity_sink",
                          "test2_electricity_sink"],
                "input": ["test_cluster_residential_electricity_bus",
                          "test_cluster_commercial_electricity_bus",
                          "test_cluster_industrial_electricity_bus"]}),
        "buses": pandas.merge(
                  left=pandas.DataFrame.from_dict({
                    "label": ["test_cluster_electricity_bus"],
                    "bus type": ["electricity bus residential decentral"],
                    "district heating conn. (exergy)": [float(0)]}),
                  right=import_standard_parameter_data(label="1_buses"),
                  on="bus type").drop(columns=["bus type"]),
        "links": pandas.merge(
                  left=pandas.DataFrame.from_dict({
                      "label": ["test_cluster_central_electricity_link"],
                      "bus1": ["central_electricity_bus"],
                      "bus2": ["test_cluster_electricity_bus"],
                      "link type": ["electricity central link decentral"]}),
                  right=import_standard_parameter_data(label="6_links"),
                  on="link type").drop(columns=["link type"])}
    
    sheets["links"].set_index("label", inplace=True, drop=False)
    sheets["buses"].set_index("label", inplace=True, drop=False)
    
    return sheets


def test_create_cluster_electricity_sinks(
        test_cluster_electricity_sinks_entries):
    """
        Create the sink, link and bus structure of a cluster with
        three sinks (residential, commercial and industrial) with the
        same annual electricity demand.
    """
    sink_parameters = [3000, 3000, 3000, [], 0, 0, 0, [],
                       ["test_electricity_sink"], ["test1_electricity_sink"],
                       ["test2_electricity_sink"]]
    
    sheets = {"sinks": pandas.DataFrame.from_dict({
                "label": ["test_electricity_sink",
                          "test1_electricity_sink",
                          "test2_electricity_sink"],
                "input": ["test_electricity_bus",
                          "test1_electricity_bus",
                          "test2_electricity_bus"]}),
              "buses": pandas.DataFrame(),
              "links": pandas.DataFrame()}
    
    sheets = Sink.create_cluster_electricity_sinks(
        standard_parameters=get_standard_parameter_data(),
        sink_parameters=sink_parameters,
        cluster="test_cluster",
        central_electricity_network=True,
        sheets=sheets
    )
    buses = import_standard_parameter_data(label="1_buses")
    buses.set_index("bus type", inplace=True)
    # since all three demand types are equal each shortage price has to
    # be multiplied by (1/3)
    test_cluster_electricity_sinks_entries["buses"].loc[
        "test_cluster_electricity_bus", "shortage costs"] = \
        (1/3) * buses.loc["electricity bus residential decentral",
                          "shortage costs"] \
        + (1/3) * buses.loc["electricity bus commercial decentral",
                            "shortage costs"] \
        + (1/3) * buses.loc["electricity bus industrial decentral",
                            "shortage costs"]
    
    for i in ["sinks", "links", "buses"]:
        pandas.testing.assert_frame_equal(
            sheets[i].sort_index(axis=1),
            test_cluster_electricity_sinks_entries[i].sort_index(axis=1))
