import pytest
import os
import pandas
from program_files.urban_district_upscaling.components import Transformer

# import standard parameter
standard_parameters = pandas.ExcelFile(
    os.path.dirname(__file__) + "/standard_parameters.xlsx"
)
transformers = standard_parameters.parse("4_transformers")


@pytest.fixture
def test_decentral_gasheating_entry():
    # combine specific data and the standard parameter data
    return {
        "transformers": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {
                    "transformer_type": ["building_gasheating_transformer"],
                    "label": ["test_gasheating_transformer"],
                    "input": ["test_gas_bus"],
                    "output": ["test_heat_bus"],
                    "output2": ["None"],
                    "area": [float(0)],
                    "temperature high": ["60"],
                }
            ),
            right=transformers,
            on="transformer_type",
        ).drop(columns=["transformer_type"])
    }


@pytest.fixture
def test_decentral_ashp_entry():
    # combine specific data and the standard parameter data
    return {
        "transformers": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {
                    "transformer_type": ["building_ashp_transformer"],
                    "label": ["test_ashp_transformer"],
                    "input": ["test_hp_elec_bus"],
                    "output": ["test_heat_bus"],
                    "output2": ["None"],
                    "area": [float(0)],
                    "temperature high": ["60"],
                }
            ),
            right=transformers,
            on="transformer_type",
        ).drop(columns=["transformer_type"])
    }


def test_create_transformer(test_decentral_gasheating_entry):
    """ """
    sheets = {"transformers": pandas.DataFrame(), "buses": pandas.DataFrame()}
    # start the method to be tested
    sheets = Transformer.create_transformer(
        building_id="test",
        transformer_type="building_gasheating_transformer",
        sheets=sheets,
        standard_parameters=standard_parameters,
        flow_temp="60",
        building_type="SFB",
    )
    # assert rather the two dataframes are equal
    pandas.testing.assert_frame_equal(
        sheets["transformers"].sort_index(axis=1),
        test_decentral_gasheating_entry["transformers"].sort_index(axis=1),
    )


def test_building_transformer(
    test_decentral_gasheating_entry, test_decentral_ashp_entry
):
    """ """
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
        "flow temperature": "60",
    }
    # start the method to be tested
    sheets = Transformer.building_transformer(
        building=building,
        p2g_link=False,
        sheets=sheets,
        standard_parameters=standard_parameters,
    )
    # assert rather the two dataframes are equal
    pandas.testing.assert_frame_equal(
        sheets["transformers"].sort_index(axis=1),
        pandas.concat(
            [
                test_decentral_ashp_entry["transformers"],
                test_decentral_gasheating_entry["transformers"],
            ]
        ).sort_index(axis=1),
    )


def test_cluster_transf_information():
    pass


def test_transformer_clustering():
    pass


def test_create_cluster_transformer():
    pass
