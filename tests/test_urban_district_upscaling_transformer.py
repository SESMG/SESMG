import pytest
import pandas
from tests.conftest import (get_standard_parameter_data,
                            import_standard_parameter_data)
from program_files.urban_district_upscaling.components import Transformer


@pytest.fixture
def test_decentral_gasheating_entry():
    """
        Create a data set of a decentral gas heating entry.
    """
    # combine specific data and the standard parameter data
    return {"transformers": pandas.merge(
        left=pandas.DataFrame.from_dict({
            "transformer type": ["gas heating natural gas decentral"],
            "label": ["test_natural_gas_heating_plant_transformer"],
            "input": ["test_natural_gas_bus"],
            "output": ["test_heat_bus"],
            "output2": ["None"],
            "area": [float(0)],
            "length of the geoth. probe": [0.0],
            "heat extraction": [0.0],
            "temperature high": ["60"],
            "min. investment capacity": [float(0)]}),
        right=import_standard_parameter_data(label="4_transformers"),
        on="transformer type").drop(columns=["transformer type"])}


@pytest.fixture
def test_decentral_ashp_entry():
    """
        Create a data set of a decentral ashp entry.
    """
    # combine specific data and the standard parameter data
    return {"transformers": pandas.merge(
        left=pandas.DataFrame.from_dict({
            "transformer type": ["heat pump air source decentral"],
            "label": ["test_air_source_heatpump_transformer"],
            "input": ["test_heatpump_electricity_bus"],
            "output": ["test_heat_bus"],
            "output2": ["None"],
            "area": [float(0)],
            "length of the geoth. probe": [0.0],
            "heat extraction": [0.0],
            "temperature high": ["60"],
            "min. investment capacity": [float(0)]}),
        right=import_standard_parameter_data(label="4_transformers"),
        on="transformer type").drop(columns=["transformer type"])}
    
    
def test_create_transformer(test_decentral_gasheating_entry):
    """
        Create a standard parameter building gas heating system and
        compare it to the manual created entries to validate the
        functionality of the creation process.
    """
    sheets = {"transformers": pandas.DataFrame(), "buses": pandas.DataFrame()}
    # start the method to be tested
    sheets = Transformer.create_transformer(
        label="test",
        transformer_type="gas heating natural gas ",
        sheets=sheets,
        standard_parameters=get_standard_parameter_data(),
        flow_temp="60",
        category="gas",
        fuel_type="natural gas ",
        de_centralized="decentral",
        building_type="single family building",
        output="test_heat_bus")
    
    # since there are not only numeric values within these two
    # standard parameter columns dtypes have to be changed from object
    # to int
    for i in ["heat source", "mode"]:
        test_decentral_gasheating_entry["transformers"][i] \
            = test_decentral_gasheating_entry["transformers"][i].astype(int)
        
    # assert rather the two dataframes are equal
    pandas.testing.assert_frame_equal(
        sheets["transformers"].sort_index(axis=1),
        test_decentral_gasheating_entry["transformers"].sort_index(axis=1)
    )


def test_building_transformer(test_decentral_gasheating_entry,
                              test_decentral_ashp_entry):
    """
        Create a standard parameter building gas heating system and a
        standard parameter building ashp and
        compare it to the manual created entries to validate the
        functionality of the creation process.
    """
    # building specific parameter
    building = {
        "label": "test",
        "building type": "SFB",
        "ashp": "yes",
        "gas heating": "yes",
        "electric heating": "no",
        "oil heating": "no",
        "wood stove": "no",
        "aahp": "no",
        "pellet heating": "no",
        "flow temperature": "60",
        "wood stove share": "standard"
    }
    
    # start the method to be tested
    sheets = Transformer.building_transformer(
        building=building,
        p2g_link=False,
        sheets={"transformers": pandas.DataFrame(),
                "buses": pandas.DataFrame()},
        standard_parameters=get_standard_parameter_data()
    )
    
    # assert rather the two dataframes are equal
    pandas.testing.assert_frame_equal(
        sheets["transformers"].sort_index(axis=1),
        pandas.concat(
            [test_decentral_ashp_entry["transformers"],
             test_decentral_gasheating_entry["transformers"]]).sort_index(
                axis=1))


@pytest.fixture
def test_create_gchp_entry():
    """
        Create a data set of a decentral gchp entry.
    """
    # create control data structure
    sheets = {
        "buses": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {None: [0, 0],
                 "label": ["st_parcel_heatpump_electricity_bus",
                           "st_parcel_heat_bus"],
                 "bus type": ["electricity bus heat pump decentral",
                              "heat bus decentral"],
                 "district heating conn. (exergy)": [float(0)] * 2}),
            right=import_standard_parameter_data(label="1_buses"),
            on="bus type"),
        "transformers": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {None: [0],
                 "label": ["st_parcel_ground-coupled_heatpump_transformer"],
                 "input": ["st_parcel_heatpump_electricity_bus"],
                 "output": ["st_parcel_heat_bus"],
                 "output2": ["None"],
                 "area": [float(100)],
                 "length of the geoth. probe": [100.0],
                 "heat extraction": [0.0328],
                 "temperature high": ["60"],
                 "transformer type": ["heat pump ground-coupled decentral"],
                 "min. investment capacity": [float(0)]}),
            right=import_standard_parameter_data(label="4_transformers"),
            on="transformer type")}
    
    types = {"buses": ["bus type"], "transformers": ["transformer type"]}
    for key in sheets.keys():
        sheets[key] = sheets[key].set_index(None, drop=True)
        sheets[key] = sheets[key].drop(columns=types.get(key))
    
    return sheets


def test_create_gchp(test_create_gchp_entry):
    """
        Create a standard parameter parcel gchp transformer and its
        buses and compare them to the manual created one to validate
        ther creation process.
    """
    tool = pandas.DataFrame.from_dict({"label": ["test_building"],
                                       "active": [1],
                                       "gchp": ["yes"],
                                       "parcel ID": ["test_parcel"]})
    
    parcels = pandas.DataFrame.from_dict({
        "ID parcel": ["test_parcel"],
        "gchp area (m²)": ["100"],
        "length of the geoth. probe (m)": ["100"],
        "heat extraction": ["0.0328"]})
    
    gchps_test = {"st_parcel": ["100", "100", "0.0328"]}
    
    gchps, sheets = Transformer.create_gchp(
        tool=tool,
        parcels=parcels,
        sheets={"buses": pandas.DataFrame(),
                "transformers": pandas.DataFrame()},
        standard_parameters=get_standard_parameter_data())
    
    assert gchps == gchps_test
    for key in sheets.keys():
        pandas.testing.assert_frame_equal(
                sheets[key].sort_index(axis=1),
                test_create_gchp_entry[key].sort_index(axis=1))


def test_cluster_transf_information():
    pass


def test_transformer_clustering():
    pass


def test_create_cluster_transformer():
    pass
