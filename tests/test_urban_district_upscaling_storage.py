import pytest
import pandas
from program_files.urban_district_upscaling.components import Storage
import os

# import standard parameter
standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                       + "/standard_parameters.xlsx")
storages = standard_parameters.parse("5_storages")

test_sheets_clustering = pandas.DataFrame(columns=["label"])
test_sheets_clustering.set_index("label", inplace=True, drop=False)


@pytest.fixture
def test_storage_decentralized_thermal_storage_entry():
    # combine specific data and the standard parameter data
    return {"storages":
            pandas.merge(
                left=pandas.DataFrame.from_dict({
                    "label": ["test_building_thermal_storage"],
                    "storage_type": ["building_thermal_storage"],
                    "bus": ["test_building" + "_heat_bus"]}),
                right=storages,
                on="storage_type").drop(columns=["storage_type"])}


def test_create_storage(test_storage_decentralized_battery_entry):
    """
    
    """
    sheets = {"storages": pandas.DataFrame()}

    # create a standard_parameter building res electricity bus
    sheets = Storage.create_storage(
        building_id="test_building",
        storage_type="battery",
        de_centralized="building",
        sheets=sheets,
        standard_parameters=pandas.ExcelFile(os.path.dirname(__file__)
                                             + "/standard_parameters.xlsx"))

    pandas.testing.assert_frame_equal(
        sheets["storages"].sort_index(axis=1),
        test_storage_decentralized_battery_entry["storages"].sort_index(axis=1)
    )


def test_building_storages(test_storage_decentralized_battery_entry,
                           test_storage_decentralized_thermal_storage_entry):
    """
    
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
        true_bools=["yes"],
        sheets=sheets,
        standard_parameters=pandas.ExcelFile(os.path.dirname(__file__)
                                             + "/standard_parameters.xlsx"))
    # assert rather the two dataframes are equal
    pandas.testing.assert_frame_equal(
            sheets["storages"],
            pandas.concat([
                test_storage_decentralized_battery_entry["storages"],
                test_storage_decentralized_thermal_storage_entry["storages"]]))


def test_storage_clustering():
    """
    
    """
    storage_parameter = {"battery": [0, 0, 0, 0, 0]}

    building = ["testbuilding", "testparcel", "COM"]

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

    test_storage_parameter = {"battery": [1, 500, 10, 10, 50]}

    assert storage_parameter == test_storage_parameter


def test_cluster_storage_information():
    """
    
    """
    
    sheets = {"storages": pandas.DataFrame.from_dict({
        "label": ["test_1", "test_2"]})}
    sheets["storages"].set_index("label", inplace=True, drop=False)
    
    storage = pandas.DataFrame.from_dict({
        "label": ["test_1", "test_2"],
        "storage type": ["Generic", "Generic"],
        "max. investment capacity": [500, 500],
        "periodical costs": [10, 10],
        "periodical constraint costs": [10, 10],
        "variable output costs": [0, 50],
    })

    storage_parameter = {"battery": [0, 0, 0, 0, 0]}
    
    for num, test in storage.iterrows():
        storage_parameter, sheets = Storage.cluster_storage_information(
            storage=test,
            storage_parameter=storage_parameter,
            storage_type="battery",
            sheets=sheets
        )
    
    pandas.testing.assert_frame_equal(sheets["storages"],
                                      test_sheets_clustering)
    
    test_storage_parameter = {"battery": [2, 1000, 20, 20, 50]}
    
    assert storage_parameter == test_storage_parameter


@pytest.fixture
def test_clustered_battery_storage():
    sheets = {"storages": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test_cluster_battery_storage"],
                "storage_type": ["building_battery_storage"],
                "bus": ["test_cluster_electricity_bus"],
                "max. investment capacity": [1000],
                "periodical costs": [10.0],
                "periodical constraint costs": [10.0],
                "variable output costs": [25.0]}),
            right=storages,
            on="storage_type").drop(columns=["storage_type",
                                             "max. investment capacity_y",
                                             "periodical costs_y",
                                             "periodical constraint costs_y",
                                             "variable output costs_y"])}
    
    sheets["storages"] = sheets["storages"].rename(columns={
        "max. investment capacity_x": "max. investment capacity",
        "periodical costs_x": "periodical costs",
        "periodical constraint costs_x": "periodical constraint costs",
        "variable output costs_x": "variable output costs"
    })
    
    return sheets


def test_create_cluster_storage(test_clustered_battery_storage):
    """
    
    """
    storage_parameter = {"battery": [2, 1000, 20, 20, 50]}
    
    sheets = Storage.create_cluster_storage(
        storage_parameter=storage_parameter,
        cluster="test_cluster",
        sheets={"storages": pandas.DataFrame()},
        standard_parameters=standard_parameters,
        storage_type="battery"
    )

    pandas.testing.assert_frame_equal(
        sheets["storages"].sort_index(axis=1),
        test_clustered_battery_storage["storages"].sort_index(axis=1))
