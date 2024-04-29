import pytest
import pandas
from tests.conftest import (import_standard_parameter_data,
                            get_standard_parameter_data)
from program_files.urban_district_upscaling.components \
    import Central_components


def test_create_central_heat_component():
    from program_files.urban_district_upscaling.components.Central_components \
        import create_central_heat_component
    pass


def test_central_comp():
    from program_files.urban_district_upscaling.components.Central_components \
        import central_components
    pass


@pytest.fixture
def test_create_power_to_gas_entry():
    """
        Create a dataset of power to gas components to validate the
        functionality of its creation process.
    """
    return {
        "buses": pandas.merge(
            left=pandas.DataFrame.from_dict({
                None: [0, 0, 0],
                "label": ["central_natural_gas_bus",
                          "central_hydrogen_bus",
                          "central_hydrogen_heat_bus"],
                "bus type": ["natural gas bus central",
                             "hydrogen bus central",
                             "heat bus fuel cell central"],
                "district heating conn. (exergy)": [float(0)] * 3}),
            right=import_standard_parameter_data(label="1_buses"),
            on="bus type").drop(columns=["bus type"]),
        "links": pandas.merge(
            left=pandas.DataFrame.from_dict({
                None: [0],
                "label": ["central_hydrogen_heat_link"],
                "link type": ["heat fuel cell central link central"],
                "bus1": ["central_hydrogen_heat_bus"],
                "bus2": ["central_heat_input_bus"]}),
            right=import_standard_parameter_data(label="6_links"),
            on="link type").drop(columns=["link type"]),
        "transformers": pandas.merge(
            left=pandas.DataFrame.from_dict({
                None: [0, 0, 0],
                "label": ["central_hydrogen_electrolysis_transformer",
                          "central_hydrogen_methanization_transformer",
                          "central_hydrogen_fuelcell_transformer"],
                "transformer type": ["electrolysis central",
                                     "methanization central",
                                     "fuel cell central"],
                "input": ["central_electricity_bus",
                          "central_hydrogen_bus",
                          "central_hydrogen_bus"],
                "output": ["central_hydrogen_bus",
                           "central_natural_gas_bus",
                           "central_electricity_bus"],
                "output2": ["None",
                            "None",
                            "central_hydrogen_heat_bus"],
                "area": [float(0)] * 3,
                "length of the geoth. probe": [float(0)] * 3,
                "heat extraction": [float(0)] * 3,
                "temperature high": ["0"] * 3,
                "min. investment capacity": [float(0)] * 3}),
            right=import_standard_parameter_data(label="4_transformers"),
            on="transformer type").drop(columns=["transformer type"]),
        "storages": pandas.merge(
            left=pandas.DataFrame.from_dict({
                None: [0, 0],
                "label": ["central_hydrogen_storage",
                          "central_naturalgas_storage"],
                "storage type": ["hydrogen storage steel cylinder central",
                                 "natural gas storage steel cylinder central"],
                "bus": ["central_hydrogen_bus",
                        "central_natural_gas_bus"],
                "min. investment capacity": [float(0)] * 2}),
            right=import_standard_parameter_data(label="5_storages"),
            on="storage type").drop(columns=["storage type"])
    }


def test_create_power_to_gas_system(test_create_power_to_gas_entry):
    """
        Create a standard parameter central power to gas system and
        compare it to a manual created one to ensure the
        functionality of the creation process for standard parameter
        power to gas systems.
    """
    sheets = Central_components.create_power_to_gas_system(
        label="test",
        output="central_heat_input_bus",
        sheets={"buses": pandas.DataFrame(),
                "links": pandas.DataFrame(),
                "transformers": pandas.DataFrame(),
                "storages": pandas.DataFrame()},
        standard_parameters=get_standard_parameter_data())
    
    # since there are not only numeric values within these two
    # standard parameter columns dtypes have to be changed from object
    # to int
    for i in ["heat source", "mode"]:
        test_create_power_to_gas_entry["transformers"][i] \
            = test_create_power_to_gas_entry["transformers"][i].astype(int)

    for key in sheets.keys():
        test_create_power_to_gas_entry[key].set_index(None, inplace=True)
        pandas.testing.assert_frame_equal(
            sheets[key].sort_index(axis=1),
            test_create_power_to_gas_entry[key].sort_index(axis=1))


@pytest.fixture
def test_central_heatpump_entry():
    """
        Create a dataset of central heat pump components to validate
        the functionality of its creation process.
    """
    return {
        "buses": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["central_heatpump_electricity_bus"],
                "bus type": ["electricity bus heat pump central"],
                "district heating conn. (exergy)": [float(0)]}),
            right=import_standard_parameter_data(label="1_buses"),
            on="bus type").drop(columns=["bus type"]),
        "links": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["central_heatpump_electricity_link"],
                "link type": ["electricity central link heat pump central "],
                "bus1": ["central_electricity_bus"],
                "bus2": ["central_heatpump_electricity_bus"]}),
            right=import_standard_parameter_data(label="6_links"),
            on="link type").drop(columns=["link type"]),
        "transformers": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["central_ground-coupled_heatpump_transformer"],
                "transformer type": ["heat pump ground-coupled central"],
                "input": ["central_heatpump_electricity_bus"],
                "output": ["test_output_bus"],
                "output2": ["None"],
                "area": [100.0],
                "length of the geoth. probe": [100.0],
                "heat extraction": [0.0328],
                "temperature high": ["60"],
                "min. investment capacity": [float(0)]}),
            right=import_standard_parameter_data(label="4_transformers"),
            on="transformer type").drop(columns=["transformer type"]),
    }


def test_create_central_heatpump(test_central_heatpump_entry):
    """
        Create a standard parameter central heat pump system and
        compare it to a manual created one to ensure the
        functionality of the creation process for standard parameter
        power to gas systems.
    """
    sheets = Central_components.create_central_heatpump(
        label="central",
        specification="ground-coupled ",
        create_bus=True,
        central_electricity_bus=True,
        output="test_output_bus",
        sheets={"buses": pandas.DataFrame(),
                "links": pandas.DataFrame(),
                "transformers": pandas.DataFrame()},
        standard_parameters=get_standard_parameter_data(),
        args={"area": "100",
              "length_geoth_probe": "100",
              "flow_temp": "60",
              "heat_extraction": "0.0328"}
    )
    
    for key in sheets.keys():
        pandas.testing.assert_frame_equal(
            sheets[key].sort_index(axis=1),
            test_central_heatpump_entry[key].sort_index(axis=1))


@pytest.fixture
def test_central_heating_plant_entry():
    """
        Create a dataset of central natural gas heating components to
        validate the functionality of its creation process.
    """
    return {
        "buses": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {"label": ["central_test_natural_gas_bus"],
                 "bus type": ["natural gas bus central"],
                 "district heating conn. (exergy)": [float(0)]}),
            right=import_standard_parameter_data(label="1_buses"),
            on="bus type").drop(columns=["bus type"]),
        "transformers": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["central_test_natural_gas_heating_plant_transformer"],
                "transformer type": ["gas heating natural gas central"],
                "input": ["central_test_natural_gas_bus"],
                "output": ["central_heat_input_bus"],
                "output2": ["None"],
                "area": [float(0)],
                "length of the geoth. probe": [float(0)],
                "heat extraction": [float(0)],
                "temperature high": ["0"],
                "min. investment capacity": [float(0)]}),
            right=import_standard_parameter_data(label="4_transformers"),
            on="transformer type").drop(columns=["transformer type"]),
        "links": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {"label": ["central_heating_plant_test_link"],
                 "link type": ["natural gas central link decentral"],
                 "bus1": ["central_natural_gas_bus"],
                 "bus2": ["central_test_natural_gas_bus"]}),
            right=import_standard_parameter_data(label="6_links"),
            on="link type").drop(columns=["link type"])}
    

def test_create_central_heating_transformer(test_central_heating_plant_entry):
    """
        Create a standard parameter central natural gas heating system
        and compare it to a manual created one to ensure the
        functionality of the creation process for standard parameter
        power to gas systems.
    """
    # start method to be tested
    sheets = Central_components.create_central_heating_transformer(
        label="test",
        fuel_type="natural gas",
        output="central_heat_input_bus",
        central_fuel_bus=True,
        sheets={"buses": pandas.DataFrame(),
                "transformers": pandas.DataFrame(),
                "links": pandas.DataFrame()},
        standard_parameters=get_standard_parameter_data())
    
    # since there are not only numeric values within these two
    # standard parameter columns dtypes have to be changed from object
    # to int
    for i in ["heat source", "mode"]:
        test_central_heating_plant_entry["transformers"][i] \
            = test_central_heating_plant_entry["transformers"][i].astype(int)
        
    # assert rather the two dataframes are equal
    for key in sheets.keys():
        pandas.testing.assert_frame_equal(
            sheets[key].sort_index(axis=1),
            test_central_heating_plant_entry[key].sort_index(axis=1))


@pytest.fixture
def test_central_CHP_entry():
    """
        Create a dataset of central natural gas combined heat and
        power system components to validate the functionality of its
        creation process.
    """
    return {
        "buses": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {None: [0, 0],
                 "label": ["central_test_natural_gas_bus",
                           "central_test_electricity_bus"],
                 "bus type": ["natural gas bus combined heat and power central",
                              "electricity bus combined heat and power natural gas central"],
                 "district heating conn. (exergy)": [float(0)] * 2}),
            right=import_standard_parameter_data(label="1_buses"),
            on="bus type").drop(columns=["bus type"]),
        "transformers": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {"label": ["central_test_chp_transformer"],
                 "transformer type": ["combined heat and power natural gas central"],
                 "input": ["central_test_natural_gas_bus"],
                 "output": ["central_test_electricity_bus"],
                 "output2": ["central_heat_input_bus"],
                 "area": [float(0)],
                 "length of the geoth. probe": [float(0)],
                 "heat extraction": [float(0)],
                 "temperature high": ["0"],
                 "min. investment capacity": [float(0)]}),
            right=import_standard_parameter_data(label="4_transformers"),
            on="transformer type").drop(columns=["transformer type"]),
        "links": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {None: [0, 0],
                 "label": ["central_test_electricity_central_link",
                           "central_test_natural_gas_link"],
                 "link type": ["electricity combined heat and power natural gas central link central",
                               "natural gas central link combined heat and power central"],
                 "bus1": ["central_test_electricity_bus",
                          "central_natural_gas_bus"],
                 "bus2": ["central_electricity_bus",
                          "central_test_natural_gas_bus"]}),
            right=import_standard_parameter_data(label="6_links"),
            on="link type").drop(columns=["link type"])}


def test_create_central_chp(test_central_CHP_entry):
    """
        Create a standard parameter central natural gas combined heat
        and power system and compare it to a manual created one to
        ensure the functionality of the creation process for standard
        parameter power to gas systems.
    """
    # start method to be tested
    sheets = Central_components.create_central_chp(
        label="test",
        fuel_type="natural gas",
        output="central_heat_input_bus",
        central_electricity_bus=True,
        central_fuel_bus=True,
        sheets={"buses": pandas.DataFrame(),
                "transformers": pandas.DataFrame(),
                "links": pandas.DataFrame()},
        standard_parameters=get_standard_parameter_data())
    
    # since there are not only numeric values within these two
    # standard parameter columns dtypes have to be changed from object
    # to int
    for i in ["heat source", "mode"]:
        test_central_CHP_entry["transformers"][i] \
            = test_central_CHP_entry["transformers"][i].astype(int)
        
    # assert rather the two dataframes are equal
    for key in sheets.keys():
        if len(sheets[key]) > 1:
            test_central_CHP_entry[key].set_index(None, inplace=True,
                                                  drop=True)
        pandas.testing.assert_frame_equal(
            sheets[key].sort_index(axis=1),
            test_central_CHP_entry[key].sort_index(axis=1))
