import pytest
import pandas
from tests.conftest import (get_standard_parameter_data,
                            import_standard_parameter_data)
from program_files.urban_district_upscaling.components import Storage


test_sheets_clustering = pandas.DataFrame(columns=["label"])
test_sheets_clustering.set_index("label", inplace=True, drop=False)


@pytest.fixture
def test_storage_decentralized_thermal_storage_entry():
    """
        Create a dataset of a thermal storage entry.
    """
    # combine specific data and the standard parameter data
    return {"storages":
            pandas.merge(
                left=pandas.DataFrame.from_dict({
                    "label": ["test_building_thermal_storage"],
                    "storage type": ["thermal storage decentral"],
                    "bus": ["test_building" + "_heat_bus"],
                    "min. investment capacity": [float(0)]}),
                right=import_standard_parameter_data(label="5_storages"),
                on="storage type").drop(columns=["storage type"])}


def test_create_storage(test_storage_decentralized_battery_entry):
    """
        Create a standard parameter thermal storage and compare it to
        the manual created one to validate creation process.
    """
    # create a standard_parameter building res electricity bus
    sheets = Storage.create_storage(
        building_id="test_building",
        storage_type="battery storage",
        de_centralized="decentral",
        sheets={"storages": pandas.DataFrame()},
        standard_parameters=get_standard_parameter_data())
    
    pandas.testing.assert_frame_equal(
        sheets["storages"].sort_index(axis=1),
        test_storage_decentralized_battery_entry["storages"].sort_index(axis=1)
    )


def test_building_storages(test_storage_decentralized_battery_entry,
                           test_storage_decentralized_thermal_storage_entry):
    """
        Create both decentral storage systems and compare them to the
        manual created ones to validate the creation process.
    """
    
    sheets = {"storages": pandas.DataFrame()}
    # building specific parameters
    building = {
        "label": "test_building",
        "battery storage": "yes",
        "thermal storage": "yes"
    }
    # start the method to be tested
    sheets = Storage.building_storages(
        building=building,
        sheets=sheets,
        standard_parameters=get_standard_parameter_data())
    
    # assert rather the two dataframes are equal
    pandas.testing.assert_frame_equal(
        sheets["storages"].sort_index(axis=1),
        pandas.concat([
            test_storage_decentralized_battery_entry["storages"],
            test_storage_decentralized_thermal_storage_entry["storages"]]
        ).sort_index(axis=1))


def test_storage_clustering():
    """
        Test the collection of the storages parameter to be clustered
        afterward.
    """
    storage_parameter = {"battery storage decentral": [0, 0, 0, 0, 0]}

    building = ["testbuilding", "testparcel", "commercial"]

    sheets = {"storages": pandas.DataFrame.from_dict({
        "label": ["testbuilding_battery_1"]})}

    sheets["storages"].set_index("label", inplace=True, drop=False)

    sheets_clustering = {"storages": pandas.DataFrame.from_dict({
        "label": ["testbuilding_battery_1"],
        "storage_type": ["Generic"],
        "max. investment capacity": [500],
        "periodical costs": [10],
        "periodical constraint costs": [10],
        "variable output costs": [50],
    })}

    storage_parameter, sheets = Storage.storage_clustering(
        storage_parameter=storage_parameter,
        building=building,
        sheets=sheets,
        sheets_clustering=sheets_clustering
    )

    pandas.testing.assert_frame_equal(sheets["storages"],
                                      test_sheets_clustering)

    test_storage_parameter = {"battery storage decentral":
                              [1, 500, 10, 10, 50]}

    assert storage_parameter == test_storage_parameter


def test_cluster_storage_information():
    """
        Test the clustering of storages by inserting two storages that
        need to be collected (parameter) and removed from the old sheets
        dataframe.
    """
    
    sheets = {"storages": pandas.DataFrame.from_dict({
        "label": ["test_1_battery_storage", "test_2_battery_storage"]})}
    sheets["storages"].set_index("label", inplace=True, drop=False)
    
    storage = pandas.DataFrame.from_dict({
        "label": ["test_1_battery_storage", "test_2_battery_storage"],
        "storage type": ["Generic", "Generic"],
        "max. investment capacity": [500, 500],
        "periodical costs": [10, 10],
        "periodical constraint costs": [10, 10],
        "variable output costs": [0, 50],
    })

    storage_parameter = {"battery storage decentral": [0, 0, 0, 0, 0]}
    
    for num, test in storage.iterrows():
        storage_parameter, sheets = Storage.cluster_storage_information(
            storage=test,
            storage_parameter=storage_parameter,
            storage_type="battery",
            sheets=sheets
        )
    
    pandas.testing.assert_frame_equal(sheets["storages"],
                                      test_sheets_clustering)
    
    test_storage_parameter = {"battery storage decentral":
                              [2, 1000, 20, 20, 50]}
    
    assert storage_parameter == test_storage_parameter


@pytest.fixture
def test_clustered_battery_storage():
    """
        Create a dataset of a clustered battery storage clustered
        result of two building battery storages.
    """
    sheets = {"storages": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_cluster_battery_storage"],
                "storage type": ["battery storage decentral"],
                "bus": ["test_cluster_electricity_bus"],
                "max. investment capacity": [1000],
                "periodical costs": [10.0],
                "periodical constraint costs": [10.0],
                "variable output costs": [25.0],
                "min. investment capacity": [0]}),
            right=import_standard_parameter_data(label="5_storages"),
            on="storage type").drop(columns=["storage type",
                                             "max. investment capacity_y",
                                             "periodical costs_y",
                                             "periodical constraint costs_y",
                                             "variable output costs_y"])}
    
    sheets["storages"] = sheets["storages"].rename(columns={
        "max. investment capacity_x": "max. investment capacity",
        "periodical costs_x": "periodical costs",
        "periodical constraint costs_x": "periodical constraint costs",
        "variable output costs_x": "variable output costs",
        "storage type.1": "storage type"
    })
    
    return sheets


def test_create_cluster_storage(test_clustered_battery_storage):
    """
        Test the creation of a battery storage clustered from two
        building battery storages.
    """
    storage_parameter = {"battery storage decentral": [2, 1000, 20, 20, 50]}
    
    sheets = Storage.create_cluster_storage(
        storage_parameter=storage_parameter,
        cluster="test_cluster",
        sheets={"storages": pandas.DataFrame()},
        standard_parameters=get_standard_parameter_data(),
        storage_type="battery storage decentral"
    )

    pandas.testing.assert_frame_equal(
        sheets["storages"].sort_index(axis=1),
        test_clustered_battery_storage["storages"].sort_index(axis=1))
