import pytest
import os
import pandas
from program_files.urban_district_upscaling.components import Transformer

# import standard parameter
standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                       + "/standard_parameters.xlsx")
transformers = standard_parameters.parse("4_transformers")

@pytest.fixture
def test_decentral_gasheating_entry():
    # combine specific data and the standard parameter data
    return {
        "transformers":
            pandas.merge(
                left=pandas.DataFrame.from_dict({
                    "transformer_type": ["building_gasheating_transformer"],
                    "label": ["test_gasheating_transformer"],
                    "input": ["test_gas_bus"],
                    "output": ["test_heat_bus"],
                    "output2": ["None"],
                    "area": [float(0)],
                    "length of the geoth. probe": [0.0],
                    "temperature high": ["60"]}),
                right=transformers,
                on="transformer_type").drop(columns=["transformer_type"])}


@pytest.fixture
def test_decentral_ashp_entry():
    # combine specific data and the standard parameter data
    return {
        "transformers":
            pandas.merge(
                left=pandas.DataFrame.from_dict({
                    "transformer_type": ["building_ashp_transformer"],
                    "label": ["test_ashp_transformer"],
                    "input": ["test_hp_elec_bus"],
                    "output": ["test_heat_bus"],
                    "output2": ["None"],
                    "area": [float(0)],
                    "length of the geoth. probe": [0.0],
                    "temperature high": ["60"]}),
                right=transformers,
                on="transformer_type").drop(columns=["transformer_type"])}
    
    
def test_create_transformer(test_decentral_gasheating_entry):
    """
    
    """
    sheets = {"transformers": pandas.DataFrame(), "buses": pandas.DataFrame()}
    # start the method to be tested
    sheets = Transformer.create_transformer(
        building_id="test",
        transformer_type="building_gasheating_transformer",
        sheets=sheets,
        standard_parameters=standard_parameters,
        flow_temp="60",
        building_type="SFB")
    # assert rather the two dataframes are equal
    pandas.testing.assert_frame_equal(
        sheets["transformers"].sort_index(axis=1),
        test_decentral_gasheating_entry["transformers"].sort_index(axis=1)
    )


def test_building_transformer(test_decentral_gasheating_entry,
                              test_decentral_ashp_entry):
    """
    
    """
    sheets = {"transformers": pandas.DataFrame(), "buses": pandas.DataFrame()}
    # building specific parameter
    building = {
        "label": "test",
        "building type": "SFB",
        "ashp": "yes",
        "gas heating": "yes",
        "electric heating": "no",
        "oil heating": "no",
        "wood stove": "no",
        "flow temperature": "60"
    }
    # start the method to be tested
    sheets = Transformer.building_transformer(
        building=building,
        p2g_link=False,
        sheets=sheets,
        standard_parameters=standard_parameters
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
                         "length of the geoth. probe": [100.0],
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
    tool = pandas.DataFrame.from_dict({"label": ["test_building"],
                                       "active": [1],
                                       "gchp": ["yes"],
                                       "parcel ID": ["test_parcel"]})
    parcels = pandas.DataFrame.from_dict({
        "ID parcel": ["test_parcel"],
        "gchp area (m²)": ["100"],
        "length of the geoth. probe (m)": ["100"]})
    gchps_test = {"st_parcel": ["100", "100"]}
    
    gchps, sheets = Transformer.create_gchp(
        tool=tool,
        parcels=parcels,
        sheets={"buses": pandas.DataFrame(),
                "transformers": pandas.DataFrame()},
        standard_parameters=standard_parameters)
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
