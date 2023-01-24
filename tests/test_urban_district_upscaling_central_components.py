import pytest
import pandas
import os
from program_files.urban_district_upscaling.components \
    import Central_components

# import standard parameter
standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                       + "/standard_parameters.xlsx")
buses = standard_parameters.parse("1_buses")
transformers = standard_parameters.parse("4_transformers")
links = standard_parameters.parse("6_links")


def test_create_central_heat_component():
    from program_files.urban_district_upscaling.components.Central_components \
        import create_central_heat_component
    pass


def test_central_comp():
    from program_files.urban_district_upscaling.components.Central_components \
        import central_comp
    pass


@pytest.fixture
def test_central_heatpump_entry():
    """
    
    """
    return {
        "buses": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["central_heatpump_electricity_bus"],
                "bus_type": ["central_heatpump_electricity_bus"],
                "district heating conn.": [float(0)]}),
            right=buses,
            on="bus_type").drop(columns=["bus_type"]),
        "links": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["central_heatpump_electricity_link"],
                "link_type": ["building_central_building_link"],
                "bus1": ["central_electricity_bus"],
                "bus2": ["central_heatpump_electricity_bus"]}),
            right=links,
            on="link_type").drop(columns=["link_type"]),
        "transformers": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["central_test_heatpump_transformer"],
                "transformer_type": ["central_gchp_transformer"],
                "input": ["central_heatpump_electricity_bus"],
                "output": ["test_output_bus"],
                "output2": ["None"],
                "area": [100.0],
                "temperature high": ["60"]}),
            right=transformers,
            on="transformer_type").drop(columns=["transformer_type"]),
    }


def test_create_central_heatpump(test_central_heatpump_entry):
    """
    
    """
    sheets = Central_components.create_central_heatpump(
        label="test",
        specification="gchp",
        create_bus=True,
        central_electricity_bus=True,
        output="test_output_bus",
        sheets={"buses": pandas.DataFrame(columns=["label"]),
                "links": pandas.DataFrame(),
                "transformers": pandas.DataFrame()},
        area="100",
        standard_parameters=standard_parameters,
        flow_temp="60"
    )
    
    for key in sheets.keys():
        pandas.testing.assert_frame_equal(
            sheets[key].sort_index(axis=1),
            test_central_heatpump_entry[key].sort_index(axis=1))


@pytest.fixture
def test_central_heating_plant_entry():
    """
    
    """
    return {
        "buses": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {"label": ["central_test_bus"],
                 "bus_type": ["central_heating_plant_naturalgas_bus"],
                 "district heating conn.": [float(0)]}),
            right=buses,
            on="bus_type").drop(columns=["bus_type"]),
        "transformers": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {"label": ["central_test_heating_plant_transformer"],
                 "transformer_type": [
                     "central_naturalgas_heating_plant_transformer"],
                 "input": ["central_test_bus"],
                 "output": ["test_output_bus"],
                 "output2": ["None"],
                 "area": [float(0)],
                 "temperature high": "0"}),
            right=transformers,
            on="transformer_type").drop(columns=["transformer_type"]),
        "links": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {"label": ["heating_plant_test_link"],
                 "link_type": ["central_naturalgas_building_link"],
                 "bus1": ["central_naturalgas_bus"],
                 "bus2": ["central_test_bus"]}),
            right=links,
            on="link_type").drop(columns=["link_type"])}
    

def test_create_central_heating_transformer(test_central_heating_plant_entry):
    """
    
    """
    # start method to be tested
    sheets = Central_components.create_central_heating_transformer(
        label="test",
        fuel_type="naturalgas",
        output="test_output_bus",
        central_fuel_bus=True,
        sheets={"buses": pandas.DataFrame(),
                "transformers": pandas.DataFrame(),
                "links": pandas.DataFrame()},
        standard_parameters=standard_parameters)
    # assert rather the two dataframes are equal
    for key in sheets.keys():
        pandas.testing.assert_frame_equal(
            sheets[key].sort_index(axis=1),
            test_central_heating_plant_entry[key].sort_index(axis=1))


@pytest.fixture
def test_central_CHP_entry():
    """
   
    """
    return {
        "buses": pandas.merge(
                left=pandas.DataFrame.from_dict(
                    {None: [0, 0],
                     "label": ["central_test_bus",
                               "central_test_elec_bus"],
                     "bus_type": ["central_chp_naturalgas_bus",
                                  "central_chp_naturalgas_electricity_bus"],
                     "district heating conn.": [float(0)] * 2}),
                right=buses,
                on="bus_type").drop(columns=["bus_type"]),
        "transformers": pandas.merge(
                left=pandas.DataFrame.from_dict(
                    {"label": ["central_test_chp_transformer"],
                     "transformer_type": ["central_naturalgas_chp"],
                     "input": ["central_test_bus"],
                     "output": ["central_test_elec_bus"],
                     "output2": ["test_output_bus"],
                     "area": [float(0)],
                     "temperature high": "0"}),
                right=transformers,
                on="transformer_type").drop(columns=["transformer_type"]),
        # TODO Only the purchase of centralized electricity is subject
        #  to charges, not the feed-in, is that correct?
        "links": pandas.merge(
                left=pandas.DataFrame.from_dict(
                    {None: [0, 0],
                     "label": ["central_test_elec_central_link",
                               "central_test_naturalgas_link"],
                     "link_type": ["central_chp_elec_central_link",
                                   "central_naturalgas_chp_link"],
                     "bus1": ["central_test_elec_bus",
                              "central_naturalgas_bus"],
                     "bus2": ["central_electricity_bus",
                              "central_test_bus"]}),
                right=links,
                on="link_type").drop(columns=["link_type"])}


def test_create_central_chp(test_central_CHP_entry):
    """
    
    """
    # start method to be tested
    sheets = Central_components.create_central_chp(
            label="test",
            fuel_type="naturalgas",
            output="test_output_bus",
            central_elec_bus=True,
            central_fuel_bus=True,
            sheets={"buses": pandas.DataFrame(),
                    "transformers": pandas.DataFrame(),
                    "links": pandas.DataFrame()},
            standard_parameters=standard_parameters)
    # assert rather the two dataframes are equal
    for key in sheets.keys():
        if len(sheets[key]) > 1:
            test_central_CHP_entry[key].set_index(None, inplace=True,
                                                  drop=True)
        pandas.testing.assert_frame_equal(
            sheets[key].sort_index(axis=1),
            test_central_CHP_entry[key].sort_index(axis=1))
