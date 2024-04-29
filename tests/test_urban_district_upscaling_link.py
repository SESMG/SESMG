import pytest
import pandas
from tests.conftest import (get_standard_parameter_data,
                            import_standard_parameter_data)
from program_files.urban_district_upscaling.components import Link


@pytest.fixture
def test_create_link_entry():
    """
        Create a standard parameter link to connect the pv output bus
        with the building intern electricity bus for self consumption.
    """
    # combine specific data and the standard parameter data
    return {"links": pandas.merge(
        left=pandas.DataFrame.from_dict({
            "label": ["test_link"],
            "bus1": ["building_pv_bus"],
            "link type": ["electricity photovoltaic decentral link decentral"],
            "bus2": ["building_res_electricity_bus"]}),
        right=import_standard_parameter_data(label="6_links"),
        on="link type").drop(columns=["link type"])
    }


def test_create_link(test_create_link_entry):
    """
        Create a standard parameter self consumption link between the
        pv output and the building intern electricity bus and compare
        it to a manual created one to ensure the functionality of the
        creation process for standard parameter self consumption links.
    """
    # start the method to be tested
    sheets = Link.create_link(
        label="test_link",
        bus_1="building_pv_bus",
        bus_2="building_res_electricity_bus",
        link_type="electricity photovoltaic decentral link decentral",
        sheets={"links": pandas.DataFrame()},
        standard_parameters=get_standard_parameter_data()
      )
    
    # assert rather the two dataframes are equal
    pandas.testing.assert_frame_equal(
        sheets["links"].sort_index(axis=1),
        test_create_link_entry["links"].sort_index(axis=1))
    
    
@pytest.fixture
def test_clustered_electricity_links():
    """
        Create a dataset of the link construction to connect the
        cluster buses to the central electricity exchange.
    """
    sheets = {"links": pandas.merge(
        left=pandas.DataFrame.from_dict({
            "label": ["test_cluster_pv_central",
                      "test_cluster_central_electricity_link",
                      "test_cluster_pv_test_cluster_electricity_link"],
            "link type": ["electricity photovoltaic decentral link central",
                          "electricity central link decentral",
                          "electricity photovoltaic decentral link decentral"],
            "bus1": ["None",
                     "central_electricity_bus",
                     "test_cluster_pv_bus"],
            "bus2": ["None",
                     "test_cluster_electricity_bus",
                     "test_cluster_electricity_bus"]}),
        right=import_standard_parameter_data(label="6_links"),
        on="link type").drop(columns=["link type"])}

    sheets["links"].set_index("label", inplace=True, drop=False)
    
    return sheets
    
    
def test_create_central_electricity_bus_connection(
        test_clustered_electricity_links):
    """
        Start the creation process of the cluster link construction
        for electricity exchange with the central electricity bus.
        Compare them to the manual created one to validate the process
        functionality.
    """
    sheets = {
        "links": pandas.DataFrame.from_dict(
            {"label": ["test_cluster_pv_central"],
             "(un)directed": ["directed"],
             "active": [1],
             "bus1": ["None"],
             "bus2": ["None"],
             "efficiency": [1],
             "existing capacity": [9999],
             "fix investment constraint costs": [0],
             "fix investment costs": [0],
             "max. investment capacity": [0],
             "min. investment capacity": [0],
             "non-convex investment": [0],
             "periodical constraint costs": [0.00001],
             "periodical costs": [0.00001],
             "variable output constraint costs": [0],
             "variable output costs": [0],
             "timeseries": [0]})}
    sheets["links"].set_index("label")
    
    sheets = Link.create_central_electricity_bus_connection(
        cluster="test_cluster",
        sheets=sheets,
        standard_parameters=get_standard_parameter_data()
    )
    
    sheets["links"] = sheets["links"].sort_index(axis=0)
    test_clustered_electricity_links["links"] = \
        test_clustered_electricity_links["links"].sort_index(axis=0)
    
    pandas.testing.assert_frame_equal(
        sheets["links"].sort_index(axis=1),
        test_clustered_electricity_links["links"].sort_index(axis=1)
    )
    
    
@pytest.fixture
def test_cluster_pv_links_entries():
    """
        Create a dataset of links between the clusters photovoltaic
        buses and the rest of the electricity system.
    """
    return {"links": pandas.merge(
        left=pandas.DataFrame.from_dict({
            "label": ["test_cluster_pv_central_electricity_link",
                      "test_cluster_pv_electricity_link"],
            "bus1": ["test_cluster_pv_bus"] * 2,
            "bus2": ["central_electricity_bus",
                     "test_cluster_electricity_bus"],
            "link type": ["electricity photovoltaic decentral link central",
                          "electricity photovoltaic decentral link decentral"]
        }),
        right=import_standard_parameter_data(label="6_links"),
        on="link type").drop(columns=["link type"])
    }


def test_create_cluster_pv_links(test_cluster_pv_links_entries):
    """
        Start the creation process for the clusters photovoltaic
        systems exchange with the cluster electricity system as well
        as the central electricity exchange. Compare it to the manual
        created one to validate the creation process functionality.
    """
    sheets = Link.create_cluster_pv_links(
        cluster="test_cluster",
        sheets={"links": pandas.DataFrame()},
        sink_parameters=[1, 2, 3, [], 0, 0, 0, [], [], [], []],
        standard_parameters=get_standard_parameter_data())
    
    test_cluster_pv_links_entries["links"].set_index(
            "label", inplace=True, drop=False)
    
    pandas.testing.assert_frame_equal(
        sheets["links"].sort_index(axis=1),
        test_cluster_pv_links_entries["links"].sort_index(axis=1))


@pytest.fixture
def test_cluster_natural_gas_bus_links_entry():
    """
        Create a dataset of a link connection for the exchange of
        natural gas.
    """
    return {
        "links": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_cluster_central_natural_gas_link"],
                "bus1": ["central_natural_gas_bus"],
                "bus2": ["test_cluster_natural_gas_bus"],
                "link type": ["natural gas central link decentral"]}),
            right=import_standard_parameter_data(label="6_links"),
            on="link type").drop(columns=["link type"])
    }


def test_add_cluster_naturalgas_bus_links(
        test_cluster_natural_gas_bus_links_entry):
    """
        Start the creation of the exchange link for natural gas and
        compare the results to the manual created one to validate the
        methods funcionality.
    """
    sheets = Link.add_cluster_naturalgas_bus_links(
        sheets={"links": pandas.DataFrame()},
        cluster="test_cluster",
        standard_parameters=get_standard_parameter_data()
    )
    
    test_cluster_natural_gas_bus_links_entry["links"].set_index(
            "label", inplace=True, drop=False)

    pandas.testing.assert_frame_equal(
        sheets["links"].sort_index(axis=1),
        test_cluster_natural_gas_bus_links_entry["links"].sort_index(axis=1))
    
    
def test_delete_non_used_links():
    pass
