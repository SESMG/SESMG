import pandas
import os
import pytest
from tests.conftest import (import_standard_parameter_data,
                            get_standard_parameter_data)


def test_append_component():
    """

    """
    from program_files.urban_district_upscaling.pre_processing \
        import append_component
    
    sheets = append_component(
        sheets={"test": pandas.DataFrame()},
        sheet="test",
        comp_parameter={"test": 3})
    
    pandas.testing.assert_frame_equal(
        sheets["test"], pandas.DataFrame.from_dict({"test": [3]}))


def test_read_standard_parameters():
    """
        Check if the reading method for standard parameter file works
        correctly and imports the index relevant data.
    """
    from program_files.urban_district_upscaling.pre_processing \
        import read_standard_parameters
    
    standard_parameters, standard_keys = read_standard_parameters(
        name="heat bus decentral",
        parameter_type="1_buses",
        index="bus type",
        standard_parameters=get_standard_parameter_data()
    )
    
    # import standard parameter
    buses = import_standard_parameter_data(label="1_buses")
    
    # create test dataframes
    test_standard_parameters = buses.loc[
        buses["bus type"] == "heat bus decentral"].set_index("bus type")
    test_standard_keys = test_standard_parameters.keys()
    
    pandas.testing.assert_frame_equal(standard_parameters,
                                      test_standard_parameters)
    
    assert list(standard_keys) == list(test_standard_keys)


def test_create_standard_parameter_comp(
        test_storage_decentralized_battery_entry):
    """
        Create a standard parameter building battery storage and
        compare it to the manual created one to validate that the
        method for standard parameter component creation works
        correctly.
    """
    from program_files.urban_district_upscaling.pre_processing \
        import create_standard_parameter_comp
    # create a standard parameter building battery storage
    sheets = create_standard_parameter_comp(
        specific_param={"label": "test_building_battery_storage",
                        "bus": "test_building_electricity_bus"},
        standard_parameter_info=[
            "battery storage decentral", "5_storages", "storage type"
        ],
        sheets={"storages": pandas.DataFrame()},
        standard_parameters=get_standard_parameter_data()
    )
    
    sheets["storages"]["min. investment capacity"] = 0.0
    # check if the building battery storage equals the manual created
    # one
    pandas.testing.assert_frame_equal(
        sheets["storages"].sort_index(axis=1),
        test_storage_decentralized_battery_entry["storages"].sort_index(axis=1))


@pytest.fixture
def test_heatpump_buses_entry():
    """
        Create the dataset of buses and links necessary for the
        connection of a parcel gchp transformer.
    """
    # create control data structure
    sheets = {
        "buses": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {None: [0],
                 "label": ["test_heatpump_electricity_bus"],
                 "bus type": ["electricity bus heat pump decentral"],
                 "district heating conn. (exergy)": [float(0)]}),
            right=import_standard_parameter_data(label="1_buses"),
            on="bus type").drop(columns=["bus type"]),
        "links": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {None: [0, 0, 0],
                 "label": ["test_heatpump_electricity_link",
                           "test_parcel_gchp_electricity_link",
                           "test_parcel_gchp_heat_link"],
                 "bus1": ["test_electricity_bus",
                          "test_heatpump_electricity_bus",
                          "st_parcel_heat_bus"],
                 "bus2": ["test_heatpump_electricity_bus",
                          "st_parcel_heatpump_electricity_bus",
                          "test_heat_bus"],
                 "link type": ["electricity decentral link heat pump decentral",
                               "electricity heat pump decentral link heat pump decentral",
                               "heat heat pump decentral link decentral "]}),
            right=import_standard_parameter_data(label="6_links"),
            on="link type").drop(columns=["link type"])}

    for key in ["buses", "links"]:
        sheets[key] = sheets[key].set_index(None, drop=True)
    
    return sheets


def test_create_heat_pump_buses_links(test_heatpump_buses_entry):
    """
        Create a standard parameter bus construction and compare it to
        the manual created one to validate the functionalty of the
        tested method.
    """
    from program_files.urban_district_upscaling.pre_processing \
        import create_heat_pump_buses_links
    
    building = {"label": "test",
                "parcel ID": "test_parcel",
                "ashp": "no",
                "gchp": "yes",
                "heatpump electricity cost": "standard",
                "heatpump electricity emission": "standard"}
    
    sheets = create_heat_pump_buses_links(
        building=pandas.Series(data=building),
        gchps={"st_parcel": "0"},
        sheets={"buses": pandas.DataFrame(),
                "links": pandas.DataFrame()},
        standard_parameters=get_standard_parameter_data())
        
    for key in sheets.keys():
        pandas.testing.assert_frame_equal(
            sheets[key].sort_index(axis=1),
            test_heatpump_buses_entry[key].sort_index(axis=1))


@pytest.fixture
def test_building_buses_entry():
    """
        Create a dataset of building buses and links connected to them.
    """
    # create control data structure
    sheets = {
        "buses": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {None: [0, 0, 0],
                 "label": ["test_pv_bus",
                           "test_electricity_bus",
                           "test_heat_bus"],
                 "bus type": ["electricity bus photovoltaic decentral",
                              "electricity bus residential decentral",
                              "heat bus decentral"],
                 "district heating conn. (exergy)": [float(0)] * 3,
                 "lat": [None, None, "0"],
                 "lon": [None, None, "0"]}),
            right=import_standard_parameter_data(label="1_buses"),
            on="bus type"),
        "links": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {None: [0, 0, 0],
                 "label": ["test_pv_self_consumption_electricity_link",
                           "test_pv_central_electricity_link",
                           "test_central_electricity_link"],
                 "bus1": ["test_pv_bus",
                          "test_pv_bus",
                          "central_electricity_bus"],
                 "bus2": ["test_electricity_bus",
                          "central_electricity_bus",
                          "test_electricity_bus"],
                 "link type": ["electricity photovoltaic decentral link decentral",
                               "electricity photovoltaic decentral link central",
                               "electricity central link decentral"]}),
            right=import_standard_parameter_data(label="6_links"),
            on="link type")}
    
    types = {"buses": ["bus type"], "links": ["link type"]}
    for key in sheets.keys():
        sheets[key] = sheets[key].set_index(None, drop=True)
        sheets[key] = sheets[key].drop(columns=types.get(key))

    return sheets


def test_create_building_buses(test_building_buses_entry):
    """
        Create a standard parameter set of building buses and its
        connected links and compare them to the manual created one to
        validate the methods functionality.
    """
    from program_files.urban_district_upscaling.pre_processing \
        import create_building_buses_and_links
    
    sheets = {"buses": pandas.DataFrame(), "links": pandas.DataFrame()}
    
    building = {
        "label": "test",
        "building type": "single family building",
        "central heat": "no",
        "latitude": "0",
        "longitude": "0",
        "st 1": "yes",
        "pv 1": "yes",
        "roof area 1": 10,
        "electricity cost": "standard",
        "electricity emission": "standard"
    }
    building.update({})
    
    sheets = create_building_buses_and_links(
        building=pandas.Series(data=building),
        central_electricity_bus=True,
        sheets=sheets,
        standard_parameters=get_standard_parameter_data())
    
    for key in sheets.keys():
        pandas.testing.assert_frame_equal(
            sheets[key].sort_index(axis=1),
            test_building_buses_entry[key].sort_index(axis=1))
    

def test_load_input_data():
    pass


def test_get_central_comp_active_status():
    """
    
    """
    from program_files.urban_district_upscaling.pre_processing \
        import get_central_comp_active_status
    
    central = pandas.DataFrame.from_dict({"technology": ["test", "test2"],
                                          "active": ["yes", "no"]})
    
    assert get_central_comp_active_status(central=central, technology="test")
    assert not get_central_comp_active_status(
            central=central, technology="test2")


def test_urban_district_upscaling_pre_processing():
    pass
