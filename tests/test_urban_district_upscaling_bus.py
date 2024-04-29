import pytest
import pandas
from tests.conftest import (import_standard_parameter_data,
                            get_standard_parameter_data)
from program_files.urban_district_upscaling.components import Bus


@pytest.fixture
def test_electricity_bus_entry():
    """
        Create a Tests dict containing a DataFrame of a single standard
        parameter electricity bus. Named: test_bus,
        Profile: residential electricity bus
    """
    return {"buses": pandas.merge(
        left=pandas.DataFrame.from_dict({
            "label": ["test_bus"],
            "bus type": ["electricity bus residential decentral"],
            "district heating conn. (exergy)": [float(0)]}),
        right=import_standard_parameter_data(label="1_buses"),
        on="bus type").drop(columns=["bus type"])}


@pytest.fixture
def test_heat_bus_entry():
    """
        Create a Tests dict containing a DataFrame of a single standard
        parameter heat bus. Named: test_bus1,
        Profile: heat bus decentral
    """
    return {"buses": pandas.merge(
        left=pandas.DataFrame.from_dict({
            "label": ["test_bus1"],
            "bus type": ["heat bus decentral"],
            "district heating conn. (exergy)": [1],
            "lat": [10],
            "lon": [10]}),
        right=import_standard_parameter_data(label="1_buses"),
        on="bus type").drop(columns=["bus type"])}


def test_create_standard_parameter_bus(test_electricity_bus_entry,
                                       test_heat_bus_entry):
    """
        Create a standard parameter electricity and heat bus and
        compare them with two manual created ones to ensure the
        functionality of the creation process for standard parameter
        buses.
    """
    # create a standard_parameter building res electricity bus
    sheets = Bus.create_standard_parameter_bus(
        label="test_bus",
        bus_type="electricity bus residential decentral",
        sheets={"buses": pandas.DataFrame()},
        standard_parameters=get_standard_parameter_data())
    
    # compare the algorithm created dataframe and the manual created
    # dataframe to ensure functionality
    pandas.testing.assert_frame_equal(
        sheets["buses"].sort_index(axis=1),
        test_electricity_bus_entry["buses"].sort_index(axis=1))
    
    # add a building heat bus with dh connection
    sheets = Bus.create_standard_parameter_bus(
        label="test_bus1",
        bus_type="heat bus decentral",
        sheets={"buses": pandas.DataFrame()},
        standard_parameters=get_standard_parameter_data(),
        coords=[10, 10, 1])
    
    # compare the algorithm created dataframe and the manual created
    # dataframe to ensure functionality
    pandas.testing.assert_frame_equal(
        sheets["buses"].sort_index(axis=1),
        test_heat_bus_entry["buses"].sort_index(axis=1))
    
    
@pytest.fixture
def cluster_electricity_bus_entry():
    """
        Dataset of clustered electricity busses of a cluster containing
        all three types of buildings (residential, commercial and
        industrial).
    """
    return {"buses": pandas.merge(
                left=pandas.DataFrame.from_dict({
                    "label": ["test1_residential_electricity_bus",
                              "test1_commercial_electricity_bus",
                              "test1_industrial_electricity_bus"],
                    "bus type": ["electricity bus residential decentral",
                                 "electricity bus commercial decentral",
                                 "electricity bus industrial decentral"],
                    "district heating conn. (exergy)": [float(0)] * 3}),
                right=import_standard_parameter_data(label="1_buses"),
                on="bus type").drop(columns=["bus type"]),
            "links": pandas.merge(
                left=pandas.DataFrame.from_dict({
                    "label": ["test1_residential_electricity_link",
                              "test1_commercial_electricity_link",
                              "test1_industrial_electricity_link"],
                    "bus1": ["test1_electricity_bus"] * 3,
                    "bus2": ["test1_residential_electricity_bus",
                             "test1_commercial_electricity_bus",
                             "test1_industrial_electricity_bus"],
                    "link type": ["electricity cluster link decentral"] * 3}),
                right=import_standard_parameter_data(label="6_links"),
                on="link type").drop(columns=["link type"])}
    
    
def test_create_cluster_electricity_buses(cluster_electricity_bus_entry):
    """
        Call the creation process for the clusters electricity busses
        and compare its result with the manual created data set to
        validate the creation process functionality.
    """
    from program_files.urban_district_upscaling.components.Bus \
        import create_cluster_electricity_buses
        
    sheets = create_cluster_electricity_buses(
        building=["test1", "test1", "single family building"],
        cluster="test1",
        sheets={"buses": pandas.DataFrame(),
                "links": pandas.DataFrame()},
        standard_parameters=get_standard_parameter_data())
    
    sheets = create_cluster_electricity_buses(
            building=["test1", "test1", "commercial food"],
            cluster="test1",
            sheets=sheets,
            standard_parameters=get_standard_parameter_data())

    sheets = create_cluster_electricity_buses(
            building=["test1", "test1", "industrial"],
            cluster="test1",
            sheets=sheets,
            standard_parameters=get_standard_parameter_data())
    
    no_changes_sheets = create_cluster_electricity_buses(
        building=["test1", "test1", "_"],
        cluster="test1",
        sheets=sheets,
        standard_parameters=get_standard_parameter_data())
    
    for key in sheets.keys():
        cluster_electricity_bus_entry[key].set_index(
                "label", inplace=True, drop=False)
        pandas.testing.assert_frame_equal(
            sheets[key].sort_index(axis=1),
            cluster_electricity_bus_entry[key].sort_index(axis=1))
        pandas.testing.assert_frame_equal(
            sheets[key].sort_index(axis=1),
            no_changes_sheets[key].sort_index(axis=1))
        
        
@pytest.fixture
def test_cluster_averaged_bus_entry():
    """
        Create a data set of an averaged gas bus.
    """
    buses = import_standard_parameter_data(label="1_buses")
    sheets = {"buses": pandas.merge(
        left=pandas.DataFrame.from_dict({
            "label": ["test1_natural_gas_bus"],
            "bus type": ["gas bus residential decentral"],
            "district heating conn. (exergy)": [float(0)]}),
        right=buses,
        on="bus type").drop(columns=["bus type"])}
    
    res_gas_bus = buses.query("`bus type` == 'gas bus residential decentral'")
    com_gas_bus = buses.query("`bus type` == 'gas bus commercial decentral'")
    ind_gas_bus = buses.query("`bus type` == 'gas bus industrial decentral'")
    
    sheets["buses"].loc[0, "shortage costs"] = \
        (1/6) * float(res_gas_bus["shortage costs"]) \
        + (2/6) * float(com_gas_bus["shortage costs"]) \
        + (3/6) * float(ind_gas_bus["shortage costs"])
    
    return sheets


def test_create_cluster_averaged_bus(test_cluster_averaged_bus_entry):
    """
    
    """
    from program_files.urban_district_upscaling.components.Bus \
        import create_cluster_averaged_bus
    sink_parameters = [0, 0, 0, "x", 1, 2, 3]
    
    sheets = create_cluster_averaged_bus(
        sink_parameters=sink_parameters,
        cluster="test1",
        fuel_type="gas",
        sheets={"buses": pandas.DataFrame()},
        standard_parameters=get_standard_parameter_data())
    
    test_cluster_averaged_bus_entry["buses"].set_index(
        "label", inplace=True, drop=False)
    
    pandas.testing.assert_frame_equal(
        sheets["buses"].sort_index(axis=1),
        test_cluster_averaged_bus_entry["buses"].sort_index(axis=1)
    )


