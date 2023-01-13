import pytest
import pandas
from program_files.urban_district_upscaling.components import Storage
import os


@pytest.fixture
def test_storage_decentralized_thermal_storage_entry():
    # import standard parameter
    standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                           + "/standard_parameters.xlsx")
    storages = standard_parameters.parse("5_storages")
    storage = storages.loc[storages["storage_type"]
                           == "building_thermal_storage"]
    # combine specific data and the standard parameter data
    sheets = {
        "storages":
            pandas.merge(
                    left=pandas.DataFrame.from_dict({
                        "label": ["test_building_thermal_storage"],
                        "storage_type": ["building_thermal_storage"],
                        "bus": ["test_building" + "_heat_bus"]}),
                    right=storage,
                    left_on="storage_type",
                    right_on="storage_type"
            )}

    # remove column which was used to merge the two dataframe parts
    sheets["storages"] = sheets["storages"].drop(columns=["storage_type"])

    return sheets


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
        sheets["storages"],
        test_storage_decentralized_battery_entry["storages"])


def test_building_storages(test_storage_decentralized_battery_entry,
                           test_storage_decentralized_thermal_storage_entry):
    """
    
    """
    from program_files.urban_district_upscaling.components import Storage
    
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
    pass

def test_cluster_storage_information():
    pass

def test_create_cluster_storage():
    pass