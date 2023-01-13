import pytest
import os
import pandas


@pytest.fixture
def test_decentral_gasheating_entry():
    # import standard parameter
    standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                           + "/standard_parameters.xlsx")
    transformers = standard_parameters.parse("4_transformers")
    transformer = transformers.loc[transformers["transformer_type"]
                                   == "building_gasheating_transformer"]

    # combine specific data and the standard parameter data
    sheets = {
        "transformers":
            pandas.merge(
                left=pandas.DataFrame.from_dict({
                    "transformer_type": ["building_gasheating_transformer"],
                    "label": ["test_gasheating_transformer"],
                    "input": ["test_gas_bus"],
                    "output": ["test_heat_bus"],
                    "output2": ["None"],
                    "area": [float(0)],
                    "temperature high": ["60"]}),
                right=transformer,
                left_on="transformer_type",
                right_on="transformer_type")}

    # remove column which was used to merge the two dataframe parts
    sheets["transformers"] = sheets["transformers"].drop(
            columns=["transformer_type"])

    return sheets


@pytest.fixture
def test_decentral_ashp_entry():
    # import standard parameter
    standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                           + "/standard_parameters.xlsx")
    transformers = standard_parameters.parse("4_transformers")
    transformer = transformers.loc[transformers["transformer_type"]
                                   == "building_ashp_transformer"]

    # combine specific data and the standard parameter data
    sheets = {
        "transformers":
            pandas.merge(
                left=pandas.DataFrame.from_dict({
                    "transformer_type": ["building_ashp_transformer"],
                    "label": ["test_ashp_transformer"],
                    "input": ["test_hp_elec_bus"],
                    "output": ["test_heat_bus"],
                    "output2": ["None"],
                    "area": [float(0)],
                    "temperature high": ["60"]}),
                right=transformer,
                left_on="transformer_type",
                right_on="transformer_type")}

    # remove column which was used to merge the two dataframe parts
    sheets["transformers"] = sheets["transformers"].drop(
            columns=["transformer_type"])

    return sheets
    
    
def test_create_transformer(test_decentral_gasheating_entry):
    """
    
    """
    from program_files.urban_district_upscaling.components import Transformer
    
    sheets = {"transformers": pandas.DataFrame(), "buses": pandas.DataFrame()}
    # start the method to be tested
    sheets = Transformer.create_transformer(
        building_id="test",
        transf_type="building_gasheating_transformer",
        sheets=sheets,
        standard_parameters=pandas.ExcelFile(os.path.dirname(__file__)
                                             + r"/standard_parameters.xlsx"),
        flow_temp="60",
        building_type="SFB")
    # assert rather the two dataframes are equal
    pandas.testing.assert_frame_equal(
        sheets["transformers"], test_decentral_gasheating_entry["transformers"]
    )


def test_building_transformer(test_decentral_gasheating_entry,
                              test_decentral_ashp_entry):
    from program_files.urban_district_upscaling.components import Transformer
    sheets = {"transformers": pandas.DataFrame(), "buses": pandas.DataFrame()}

    # building specific parameter
    building = {
        "label": "test",
        "building type": "SFB",
        "ashp": "yes",
        "gas heating": "yes",
        "electric heating": "no",
        "oil heating": "no",
        "flow temperature": "60"
    }
    # start the method to be tested
    sheets = Transformer.building_transformer(
        building=building,
        p2g_link=False,
        true_bools=["yes"],
        sheets=sheets,
        standard_parameters=pandas.ExcelFile(os.path.dirname(__file__)
                                             + r"/standard_parameters.xlsx")
    )
    # assert rather the two dataframes are equal
    pandas.testing.assert_frame_equal(
        sheets["transformers"],
        pandas.concat([test_decentral_ashp_entry["transformers"],
                       test_decentral_gasheating_entry["transformers"]]))


def test_cluster_transf_information():
    pass


def test_transformer_clustering():
    pass


def test_create_cluster_transformer():
    pass
