import pytest
import pandas
from program_files.urban_district_upscaling.components import Bus
import os

# import standard parameter
standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                       + "/standard_parameters.xlsx")
buses = standard_parameters.parse("1_buses")
links = standard_parameters.parse("6_links")


@pytest.fixture
def test_elec_bus_entry():
    """
   
    """
    return {"buses": pandas.merge(
        left=pandas.DataFrame.from_dict({
            "label": ["test_bus"],
            "bus_type": ["building_res_electricity_bus"],
            "district heating conn.": [float(0)]}),
        right=buses,
        on="bus_type").drop(columns=["bus_type"])}


@pytest.fixture
def test_heat_bus_entry():
    """
    
    """
    return {"buses": pandas.merge(
        left=pandas.DataFrame.from_dict({
            "label": ["test_bus1"],
            "bus_type": ["building_heat_bus"],
            "district heating conn.": [1],
            "lat": [10],
            "lon": [10]}),
        right=buses,
        on="bus_type").drop(columns=["bus_type"])}


def test_create_standard_parameter_bus(test_elec_bus_entry,
                                       test_heat_bus_entry):
    """
        Short description of the given TEST Suite
    """
    # create a standard_parameter building res electricity bus
    sheets = Bus.create_standard_parameter_bus(
        label="test_bus",
        bus_type="building_res_electricity_bus",
        sheets={"buses": pandas.DataFrame()},
        standard_parameters=standard_parameters)
    
    pandas.testing.assert_frame_equal(
        sheets["buses"].sort_index(axis=1),
        test_elec_bus_entry["buses"].sort_index(axis=1))
    
    # add a building heat bus with dh connection
    sheets = Bus.create_standard_parameter_bus(
        label="test_bus1",
        bus_type="building_heat_bus",
        sheets={"buses": pandas.DataFrame()},
        standard_parameters=standard_parameters,
        coords=[10, 10, 1])
    pandas.testing.assert_frame_equal(
        sheets["buses"].sort_index(axis=1),
        test_heat_bus_entry["buses"].sort_index(axis=1))
    
    
@pytest.fixture
def cluster_electricity_bus_entry():
    """
    
    """
    return {"buses": pandas.merge(
                left=pandas.DataFrame.from_dict({
                    "label": ["test1_res_electricity_bus",
                              "test1_com_electricity_bus",
                              "test1_ind_electricity_bus"],
                    "bus_type": ["building_res_electricity_bus",
                                 "building_com_electricity_bus",
                                 "building_ind_electricity_bus"],
                    "district heating conn.": [float(0)] * 3}),
                right=buses,
                on="bus_type").drop(columns=["bus_type"]),
            "links": pandas.merge(
                left=pandas.DataFrame.from_dict({
                    "label": ["test1_res_electricity_link",
                              "test1_com_electricity_link",
                              "test1_ind_electricity_link"],
                    "bus1": ["test1_electricity_bus"] * 3,
                    "bus2": ["test1_res_electricity_bus",
                             "test1_com_electricity_bus",
                             "test1_ind_electricity_bus"],
                    "link_type": ["cluster_electricity_link"] * 3}),
                right=links,
                on="link_type").drop(columns=["link_type"])}
    
    
def test_create_cluster_electricity_buses(cluster_electricity_bus_entry):
    """
    
    """
    from program_files.urban_district_upscaling.components.Bus \
        import create_cluster_electricity_buses
    
    sheets = create_cluster_electricity_buses(
        building=["test1", "test1", "SFB"],
        cluster="test1",
        sheets={"buses": pandas.DataFrame(columns=["label"]),
                "links": pandas.DataFrame(columns=["label"])},
        standard_parameters=standard_parameters)
    
    sheets = create_cluster_electricity_buses(
            building=["test1", "test1", "COM"],
            cluster="test1",
            sheets=sheets,
            standard_parameters=standard_parameters)

    sheets = create_cluster_electricity_buses(
            building=["test1", "test1", "IND"],
            cluster="test1",
            sheets=sheets,
            standard_parameters=standard_parameters)

    for key in sheets.keys():
        cluster_electricity_bus_entry[key].set_index(
                "label", inplace=True, drop=False)
        pandas.testing.assert_frame_equal(
            sheets[key].sort_index(axis=1),
            cluster_electricity_bus_entry[key].sort_index(axis=1))


def test_create_cluster_averaged_bus():
    pass

