import pytest
import os
import pandas
from program_files.urban_district_upscaling.components import Link

# import standard parameter
standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                       + "/standard_parameters.xlsx")
links = standard_parameters.parse("6_links")

@pytest.fixture
def test_create_link_entry():
    # combine specific data and the standard parameter data
    return {
        "links":
            pandas.merge(
                left=pandas.DataFrame.from_dict({
                    "label": ["test_link"],
                    "bus1": ["building_pv_bus"],
                    "link_type": ["building_pv_building_link"],
                    "bus2": ["building_res_electricity_bus"]}),
                right=links,
                on="link_type").drop(columns=["link_type"])}


def test_create_link(test_create_link_entry):
    """
    testing create link function

    """
    # start the method to be tested
    sheets = Link.create_link(
        label="test_link",
        bus_1="building_pv_bus",
        bus_2="building_res_electricity_bus",
        link_type="building_pv_building_link",
        sheets={"links": pandas.DataFrame()},
        standard_parameters=standard_parameters
      )
    # assert rather the two dataframes are equal
    pandas.testing.assert_frame_equal(
        sheets["links"].sort_index(axis=1),
        test_create_link_entry["links"].sort_index(axis=1))
    
    
@pytest.fixture
def test_clustered_electricity_links():
    sheets = {
        "links":
            pandas.merge(
                left=pandas.DataFrame.from_dict({
                    "label": ["test_cluster_pv_central",
                              "test_cluster_central_electricity_link",
                              "test_cluster_pv_test_cluster_electricity_link"],
                    "link_type": ["building_pv_central_link",
                                  "building_central_building_link",
                                  "building_pv_central_link"],
                    "bus1": ["",
                             "central_electricity_bus",
                             "test_cluster_pv_bus"],
                    "bus2": ["",
                             "test_cluster_electricity_bus",
                             "test_cluster_electricity_bus"]}),
                right=links,
                on="link_type").drop(columns=["link_type"])}
    
    sheets["links"].set_index("label", inplace=True, drop=False)
    
    return sheets
    
    
def test_create_central_electricity_bus_connection(
        test_clustered_electricity_links):
    """
    
    """
    sheets = {
        "links": pandas.DataFrame.from_dict(
            {"label": ["test_cluster_pv_central"],
             "(un)directed": ["directed"],
             "active": [1.0],
             "bus1": [""],
             "bus2": [""],
             "efficiency": [1.0],
             "existing capacity": [9999.0],
             "fix investment constraint costs": [0.0],
             "fix investment costs": [0.0],
             "max. investment capacity": [0.0],
             "min. investment capacity": [0.0],
             "non-convex investment": [0.0],
             "periodical constraint costs": [0.00001],
             "periodical costs": [0.00001],
             "variable output constraint costs": [0.0],
             "variable output costs": [0.0]})}
    sheets["links"].set_index("label")
    
    sheets = Link.create_central_electricity_bus_connection(
        cluster="test_cluster",
        sheets=sheets,
        standard_parameters=standard_parameters
    )
    
    sheets["links"] = sheets["links"].sort_index(axis=0)
    test_clustered_electricity_links["links"] = \
        test_clustered_electricity_links["links"].sort_index(axis=0)
    
    pandas.testing.assert_frame_equal(
        sheets["links"].sort_index(axis=1),
        test_clustered_electricity_links["links"].sort_index(axis=1)
    )
    
    
def test_restructuring_links():

    pass