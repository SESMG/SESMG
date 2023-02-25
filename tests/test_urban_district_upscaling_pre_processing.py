import pandas
import os
import pytest


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
    
    """
    from program_files.urban_district_upscaling.pre_processing \
        import read_standard_parameters
    
    standard_parameters, standard_keys = read_standard_parameters(
        name="building_heat_bus",
        parameter_type="1_buses",
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
        buses["bus_type"] == "building_heat_bus"].set_index(
            "bus_type").squeeze()
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
    links = standard_parameters.parse("6_links")
    
    # create control data structure
    sheets = {
        "buses": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {None: [0],
                 "label": ["test_hp_elec_bus"],
                 "bus_type": ["building_hp_electricity_bus"],
                 "district heating conn.": [float(0)]}),
            right=buses,
            on="bus_type").drop(columns=["bus_type"]),
        "links": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {None: [0, 0, 0],
                 "label": ["test_building_hp_elec_link",
                           "test_parcel_gchp_elec_link",
                           "test_parcel_gchp_heat_link"],
                 "bus1": ["test_electricity_bus",
                          "test_hp_elec_bus",
                          "st_parcel_heat_bus"],
                 "bus2": ["test_hp_elec_bus",
                          "st_parcel_hp_elec_bus",
                          "test_heat_bus"],
                 "link_type": ["building_hp_elec_link",
                               "building_hp_elec_link",
                               "building_hp_heat_link"]}),
            right=links,
            on="link_type").drop(columns=["link_type"])}

    for key in ["buses", "links"]:
        sheets[key] = sheets[key].set_index(None, drop=True)
    
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
        pandas.testing.assert_frame_equal(
            sheets[key].sort_index(axis=1),
            test_hp_buses_entry[key].sort_index(axis=1))


@pytest.fixture
def test_building_buses_entry():
    """
    
    """
    # import standard parameter
    standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                           + "/standard_parameters.xlsx")
    buses = standard_parameters.parse("1_buses")
    links = standard_parameters.parse("6_links")

    # create control data structure
    sheets = {
        "buses": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {None: [0, 0, 0],
                 "label": ["test_electricity_bus",
                           "test_heat_bus",
                           "test_pv_bus"],
                 "bus_type": ["building_res_electricity_bus",
                              "building_heat_bus",
                              "building_pv_bus"],
                 "district heating conn.": [float(0)] * 3,
                 "lat": [None, "0", None],
                 "lon": [None, "0", None]}),
            right=buses,
            on="bus_type"),
        "links": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {None: [0, 0, 0],
                 "label": ["test_central_electricity_link",
                           "test_pv_self_consumption_electricity_link",
                           "test_pv_central_electricity_link"],
                 "bus1": ["central_electricity_bus",
                          "test_pv_bus",
                          "test_pv_bus"],
                 "bus2": ["test_electricity_bus",
                          "test_electricity_bus",
                          "central_electricity_bus"],
                 "link_type": ["building_central_building_link",
                               "building_pv_building_link",
                               "building_pv_central_link"]}),
            right=links,
            on="link_type")}
    
    types = {"buses": ["bus_type"], "links": ["link_type"]}
    for key in sheets.keys():
        sheets[key] = sheets[key].set_index(None, drop=True)
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
        "longitude": "0",
        "st 1": "yes",
        "pv 1": "yes",
        "roof area 1": 10
    }
    building.update({})
    
    sheets = create_building_buses_links(
        building=building,
        central_electricity_bus=True,
        sheets=sheets,
        standard_parameters=pandas.ExcelFile(os.path.dirname(__file__)
                                             + "/standard_parameters.xlsx"))
    
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


@pytest.fixture
def test_create_gchp_entry():
    """
    
    """
    # import standard parameter
    standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                           + "/standard_parameters.xlsx")
    buses = standard_parameters.parse("1_buses")
    transformers = standard_parameters.parse("4_transformers")
    
    # create control data structure
    sheets = {
        "buses": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {None: [0, 0],
                 "label": ["st_parcel_hp_elec_bus",
                           "st_parcel_heat_bus"],
                 "bus_type": ["building_hp_electricity_bus",
                              "building_heat_bus"],
                 "district heating conn.": [float(0)] * 2}),
            right=buses,
            on="bus_type"),
        "transformers": pandas.merge(
            left=pandas.DataFrame.from_dict(
                    {None: [0],
                     "label": ["st_parcel_gchp_transformer"],
                     "input": ["st_parcel_hp_elec_bus"],
                     "output": ["st_parcel_heat_bus"],
                     "output2": ["None"],
                     "area": [float(100)],
                     "temperature high": ["60"],
                     "transformer_type": ["building_gchp_transformer"]}),
            right=transformers,
            on="transformer_type")}
    
    types = {"buses": ["bus_type"], "transformers": ["transformer_type"]}
    for key in sheets.keys():
        sheets[key] = sheets[key].set_index(None, drop=True)
        sheets[key] = sheets[key].drop(columns=types.get(key))
    
    return sheets


def test_create_gchp(test_create_gchp_entry):
    """
    
    """
    from program_files.urban_district_upscaling.pre_processing \
        import create_gchp
    tool = pandas.DataFrame.from_dict({"label": ["test_building"],
                                       "active": [1],
                                       "gchp": ["yes"],
                                       "parcel ID": ["test_parcel"]})
    parcels = pandas.DataFrame.from_dict({"ID parcel": ["test_parcel"],
                                          "gchp area (m²)": "100"})
    gchps_test = {"st_parcel": "100"}
    
    gchps, sheets = create_gchp(
        tool=tool,
        parcels=parcels,
        sheets={"buses": pandas.DataFrame(),
                "transformers": pandas.DataFrame()},
        standard_parameters=pandas.ExcelFile(os.path.dirname(__file__)
                                             + "/standard_parameters.xlsx"))
    assert gchps == gchps_test
    for key in sheets.keys():
        pandas.testing.assert_frame_equal(
            sheets[key].sort_index(axis=1),
            test_create_gchp_entry[key].sort_index(axis=1))


def test_urban_district_upscaling_pre_processing():
    pass
