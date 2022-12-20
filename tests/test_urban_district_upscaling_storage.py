import pytest
import pandas
from program_files.urban_district_upscaling.components import Storage
import os

@pytest.fixture
def test_storage_decentralized_battery_entry():
    # import standard parameter
    standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                           + "/standard_parameters.xlsx")
    storages = standard_parameters.parse("5_storages")
    storage = storages.loc[storages["comment"] == "building_battery_storage"]

    return {
        "storages": pandas.DataFrame.from_dict({
                    "label" : ["test_building_battery_storage"],
                    "comment" : ["automatically_created"],
                    "bus": ["test_building" + "_electricity_bus"],
                    "active" : storage["active"].values,
                    "storage type" : storage["storage type"].values,
                    "existing capacity": storage["existing capacity"].values,
                    "min. investment capacity": storage["min. investment capacity"].values,
                    "max. investment capacity": storage["max. investment capacity"].values,
                    "periodical costs": storage["periodical costs"].values,
                    "periodical constraint costs": storage["periodical constraint costs"].values,
                    "non-convex investment": storage["non-convex investment"].values,
                    "fix investment costs": storage["fix investment costs"].values,
                    "fix investment constraint costs": storage["fix investment constraint costs"].values,
                    "input/capacity ratio" : storage["input/capacity ratio"].values,
                    "output/capacity ratio" : storage["output/capacity ratio"].values,
                    "capacity loss": storage["capacity loss"].values,
                    "efficiency inflow" : storage["efficiency inflow"].values,
                    "efficiency outflow" : storage["efficiency outflow"].values,
                    "initial capacity" : storage["initial capacity"].values,
                    "capacity min" : storage["capacity min"].values,
                    "capacity max" : storage["capacity max"].values,
                    "variable input costs" : storage["variable input costs"].values,
                    "variable output costs" : storage["variable output costs"].values,
                    "variable input constraint costs" : storage["variable input constraint costs"].values,
                    "variable output constraint costs" : storage["variable output constraint costs"].values,
                    "diameter" : storage["diameter"].values,
                    "temperature high" : storage["temperature high"].values,
                    "temperature low" : storage["temperature low"].values,
                    "U value" : storage["U value"].values})}


def test_create_storage(test_storage_decentralized_battery_entry):
    sheets = {"storages": pandas.DataFrame()}

    # create a standard_parameter building res electricity bus
    sheets = Storage.create_storage(
        building_id="test_building",
        storage_type="battery",
        de_centralized="building",
        sheets=sheets,
        standard_parameters=pandas.ExcelFile(os.path.dirname(__file__) + "/standard_parameters.xlsx"),
        bus = None)

    pandas.testing.assert_frame_equal(sheets["storages"], test_storage_decentralized_battery_entry["storages"])


def test_building_storages():
    pass

def test_storage_clustering():
    pass

def test_cluster_storage_information():
    pass

def test_create_cluster_storage():
    pass