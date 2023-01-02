import pandas
import os
import pytest


def test_append_component():
    """

    """
    from program_files.urban_district_upscaling.pre_processing \
        import append_component
    sheets = {"test": pandas.DataFrame()}
    
    test_sheets = {"test": pandas.DataFrame.from_dict({"test": [3]})}
    
    sheets = append_component(
        sheets=sheets,
        sheet="test",
        comp_parameter={"test": 3})
    
    pandas.testing.assert_frame_equal(sheets["test"], test_sheets["test"])


def test_read_standard_parameters():
    """
    
    """
    from program_files.urban_district_upscaling.pre_processing \
        import read_standard_parameters
    
    standard_parameters, standard_keys = read_standard_parameters(
        name="building_heat_bus",
        param_type="1_buses",
        index="bus_type",
        standard_parameters=pandas.ExcelFile(os.path.dirname(__file__)
                                             + "/standard_parameters.xlsx")
    )
    
    # import standard parameter
    standard_parameters_file = pandas.ExcelFile(os.path.dirname(__file__)
                                                + "/standard_parameters.xlsx")
    buses = standard_parameters_file.parse("1_buses")
    
    # create test dataframes
    test_standard_parameters = buses.loc[
        buses["bus_type"] == "building_heat_bus"].set_index("bus_type").squeeze()
    test_standard_keys = test_standard_parameters.keys()
    
    pandas.testing.assert_series_equal(standard_parameters,
                                       test_standard_parameters)
    
    assert list(standard_keys) == list(test_standard_keys)


def test_create_standard_parameter_comp(
        test_storage_decentralized_battery_entry):
    """
    
    """
    from program_files.urban_district_upscaling.pre_processing \
        import create_standard_parameter_comp
    sheets = {"storages": pandas.DataFrame()}
    
    sheets = create_standard_parameter_comp(
        specific_param={"label": "test_building_battery_storage",
                        "bus": "test_building_electricity_bus"},
        standard_parameter_info=["building_battery_storage", "5_storages",
                                 "storage_type"],
        sheets=sheets,
        standard_parameters=pandas.ExcelFile(os.path.dirname(__file__)
                                             + "/standard_parameters.xlsx")
    )
    
    pandas.testing.assert_frame_equal(
        sheets["storages"],
        test_storage_decentralized_battery_entry["storages"])


@pytest.fixture
def test_hp_buses_entry():
    """
    
    """
    # import standard parameter
    standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                           + "/standard_parameters.xlsx")
    buses = standard_parameters.parse("1_buses")
    bus = buses.loc[buses["bus_type"] == "building_hp_electricity_bus"]
    
    links = standard_parameters.parse("6_links")
    hp_elec_link = links.loc[links["link_type"] == "building_hp_elec_link"]
    hp_heat_link = links.loc[links["link_type"] == "building_hp_heat_link"]
    
    # create control data structure
    sheets = {
        "buses": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {"label": ["test_hp_elec_bus"],
                 "bus_type": ["building_hp_electricity_bus"]}),
            right=bus,
            left_on="bus_type",
            right_on="bus_type"),
        "links": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {"label": ["test_building_hp_elec_link"],
                 "bus1": ["test_electricity_bus"],
                 "bus2": ["test_hp_elec_bus"],
                 "link_type": ["building_hp_elec_link"]}),
            right=hp_elec_link,
            left_on="link_type",
            right_on="link_type")}
    
    sheets["links"] = pandas.concat(
        [sheets["links"],
         pandas.merge(
             left=pandas.DataFrame({"label": ["test_parcel_gchp_elec_link"],
                                    "bus1": ["test_hp_elec_bus"],
                                    "bus2": ["st_parcel_hp_elec_bus"],
                                    "link_type": ["building_hp_elec_link"]}),
             right=hp_elec_link,
             left_on="link_type",
             right_on="link_type"),
         pandas.merge(
             left=pandas.DataFrame({"label": ["test_parcel_gchp_heat_link"],
                                    "bus1": ["st_parcel_heat_bus"],
                                    "bus2": ["test_heat_bus"],
                                    "link_type": ["building_hp_heat_link"]}),
             right=hp_heat_link,
             left_on="link_type",
             right_on="link_type"),
         ])

    types = {"buses": ["bus_type"], "links": ["link_type"]}
    for key in sheets.keys():
        sheets[key] = sheets[key].drop(columns=types.get(key))
    
    return sheets


def test_create_heat_pump_buses_links(test_hp_buses_entry):
    """
    
    """
    from program_files.urban_district_upscaling.pre_processing \
        import create_heat_pump_buses_links
    building = {"label": "test",
                "parcel ID": "test_parcel",
                "ashp": "no",
                "gchp": "yes"}
    
    sheets = {"buses": pandas.DataFrame(),
              "links": pandas.DataFrame()}
    sheets = create_heat_pump_buses_links(
        building=building,
        gchps={"st_parcel": "0"},
        sheets=sheets,
        standard_parameters=pandas.ExcelFile(os.path.dirname(__file__)
                                             + "/standard_parameters.xlsx"))
        
    for key in sheets.keys():
        pandas.testing.assert_frame_equal(sheets[key],
                                          test_hp_buses_entry[key])


@pytest.fixture
def test_building_buses_entry():
    """
    
    """
    # import standard parameter
    standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                           + "/standard_parameters.xlsx")
    buses = standard_parameters.parse("1_buses")
    elec_bus = buses.loc[buses["bus_type"] == "building_res_electricity_bus"]
    heat_bus = buses.loc[buses["bus_type"] == "building_heat_bus"]
    pv_bus = buses.loc[buses["bus_type"] == "building_pv_bus"]

    links = standard_parameters.parse("6_links")
    central_building_link = links.loc[links["link_type"]
                                      == "building_central_building_link"]
    pv_central_link = links.loc[links["link_type"]
                                == "building_pv_central_link"]
    pv_building_link = links.loc[links["link_type"]
                                 == "building_pv_building_link"]

    # create control data structure
    sheets = {
        "buses": pandas.merge(
                left=pandas.DataFrame.from_dict(
                        {"label": ["test_electricity_bus"],
                         "bus_type": ["building_res_electricity_bus"]}),
                right=elec_bus,
                left_on="bus_type",
                right_on="bus_type"),
        "links": pandas.merge(
                left=pandas.DataFrame.from_dict(
                        {"label": ["test_central_electricity_link"],
                         "bus1": ["central_electricity_bus"],
                         "bus2": ["test_electricity_bus"],
                         "link_type": ["building_central_building_link"]}),
                right=central_building_link,
                left_on="link_type",
                right_on="link_type")}

    sheets["buses"] = pandas.concat(
        [sheets["buses"],
         pandas.merge(
             left=pandas.DataFrame(
                 {"label": ["test_heat_bus"],
                  "bus_type": ["building_heat_bus"],
                  "lat": "0",
                  "lon": "0"}),
             right=heat_bus,
             left_on="bus_type",
             right_on="bus_type"),
         pandas.merge(
             left=pandas.DataFrame(
                     {"label": ["test_pv_bus"],
                      "bus_type": ["building_pv_bus"]}),
             right=pv_bus,
             left_on="bus_type",
             right_on="bus_type")])

    sheets["links"] = pandas.concat(
        [sheets["links"],
         pandas.merge(
             left=pandas.DataFrame(
                 {"label": ["test_pv_test_electricity_link"],
                  "bus1": ["test_pv_bus"],
                  "bus2": ["test_electricity_bus"],
                  "link_type": ["building_pv_building_link"]}),
             right=pv_building_link,
             left_on="link_type",
             right_on="link_type"),
         pandas.merge(
             left=pandas.DataFrame(
                 {"label": ["test_pv_central_electricity_link"],
                  "bus1": ["test_pv_bus"],
                  "bus2": ["central_electricity_bus"],
                  "link_type": ["building_pv_central_link"]}),
             right=pv_central_link,
             left_on="link_type",
             right_on="link_type"),
         ])

    types = {"buses": ["bus_type"], "links": ["link_type"]}
    for key in sheets.keys():
        sheets[key] = sheets[key].drop(columns=types.get(key))

    return sheets


def test_create_building_buses(test_building_buses_entry):
    """
    
    """
    from program_files.urban_district_upscaling.pre_processing \
        import create_building_buses_links
    
    sheets = {"buses": pandas.DataFrame(), "links": pandas.DataFrame()}
    
    building = {
        "label": "test",
        "building type": "SFB",
        "central heat": "no",
        "latitude": "0",
        "longitude": "0"
    }
    for i in range(1, 29):
        building.update({"st or pv %1d" % i: "pv&st"})
    
    sheets = create_building_buses_links(
        building=building,
        central_elec_bus=True,
        sheets=sheets,
        standard_parameters=pandas.ExcelFile(os.path.dirname(__file__)
                                             + "/standard_parameters.xlsx"))
    
    for key in sheets.keys():
        pandas.testing.assert_frame_equal(sheets[key],
                                          test_building_buses_entry[key])
    

def test_load_input_data():
    pass


def test_get_central_comp_active_status():
    pass


def test_create_gchp():
    pass


def test_urban_district_upscaling_pre_processing():
    pass