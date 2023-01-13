import pytest
import pandas
import os


@pytest.fixture
def test_storage_decentralized_battery_entry():
    # import standard parameter
    standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                           + "/standard_parameters.xlsx")
    storages = standard_parameters.parse("5_storages")
    storage = storages.loc[storages["storage_type"]
                           == "building_battery_storage"]
    # combine specific data and the standard parameter data
    sheets = {
        "storages":
            pandas.merge(
                    left=pandas.DataFrame.from_dict({
                        "label": ["test_building_battery_storage"],
                        "storage_type": ["building_battery_storage"],
                        "bus": ["test_building_electricity_bus"]}),
                    right=storage,
                    left_on="storage_type",
                    right_on="storage_type"
            )}

    # remove column which was used to merge the two dataframe parts
    sheets["storages"] = sheets["storages"].drop(columns=["storage_type"])

    return sheets
