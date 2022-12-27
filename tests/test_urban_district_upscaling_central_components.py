import pytest
import pandas
import os


def test_create_central_heat_component():
    from program_files.urban_district_upscaling.components.Central_components \
        import create_central_heat_component
    pass


def test_central_comp():
    from program_files.urban_district_upscaling.components.Central_components \
        import central_comp
    pass


@pytest.fixture
def test_central_heating_plant_entry():
    # import standard parameter
    standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                           + "/standard_parameters.xlsx")
    buses = standard_parameters.parse("1_buses")
    bus = buses.loc[buses["bus_type"]
                    == "central_heating_plant_naturalgas_bus"]
    
    transformers = standard_parameters.parse("4_transformers")
    transformer = transformers.loc[
        transformers["transformer_type"]
        == "central_naturalgas_heating_plant_transformer"]
    
    links = standard_parameters.parse("6_links")
    link = links.loc[links["link_type"] == "central_naturalgas_building_link"]

    sheets = {
        "buses": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {"label": ["central_test_bus"],
                 "bus_type": ["central_heating_plant_naturalgas_bus"]}),
            right=bus,
            left_on="bus_type",
            right_on="bus_type"),
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
            right=transformer,
            left_on="transformer_type",
            right_on="transformer_type"),
        "links": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {"label": ["heating_plant_test_link"],
                 "link_type": ["central_naturalgas_building_link"],
                 "bus1": ["central_naturalgas_bus"],
                 "bus2": ["central_test_bus"]}),
            right=link,
            left_on="link_type",
            right_on="link_type")}
    
    types = {"buses": ["bus_type"], "transformers": ["transformer_type"],
             "links": ["link_type"]}
    for key in sheets.keys():
        sheets[key] = sheets[key].drop(columns=types.get(key))
     
    return sheets
    

def test_create_central_heating_transformer(test_central_heating_plant_entry):
    from program_files.urban_district_upscaling.components.Central_components \
        import create_central_heating_transformer
    
    sheets = {"buses": pandas.DataFrame(),
              "transformers": pandas.DataFrame(),
              "links": pandas.DataFrame()}
    # start method to be tested
    create_central_heating_transformer(
        label="test",
        fuel_type="naturalgas",
        output="test_output_bus",
        central_fuel_bus=True,
        sheets=sheets,
        standard_parameters=pandas.ExcelFile(os.path.dirname(__file__)
                                             + "/standard_parameters.xlsx"))
    # assert rather the two dataframes are equal
    for key in sheets.keys():
        pandas.testing.assert_frame_equal(
            sheets[key], test_central_heating_plant_entry[key])


@pytest.fixture
def test_central_CHP_entry():
    # import standard parameter
    standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                           + "/standard_parameters.xlsx")
    buses = standard_parameters.parse("1_buses")
    fuel_bus = buses.loc[buses["bus_type"]
                         == "central_chp_naturalgas_bus"]
    elec_bus = buses.loc[buses["bus_type"]
                         == "central_chp_naturalgas_electricity_bus"]
    
    transformers = standard_parameters.parse("4_transformers")
    transformer = transformers.loc[
        transformers["transformer_type"]
        == "central_naturalgas_chp"]
    
    links = standard_parameters.parse("6_links")
    elec_link = links.loc[links["link_type"]
                          == "central_chp_elec_central_link"]
    fuel_link = links.loc[links["link_type"]
                          == "central_naturalgas_chp_link"]
    
    sheets = {
        "buses": pandas.merge(
                left=pandas.DataFrame.from_dict(
                    {"label": ["central_test_bus"],
                     "bus_type": ["central_chp_naturalgas_bus"]}),
                right=fuel_bus,
                left_on="bus_type",
                right_on="bus_type"),
        "transformers": pandas.merge(
                left=pandas.DataFrame.from_dict(
                    {"label": ["central_test_chp_transformer"],
                     "transformer_type": [
                         "central_naturalgas_chp"],
                     "input": ["central_test_bus"],
                     "output": ["central_test_elec_bus"],
                     "output2": ["test_output_bus"],
                     "area": [float(0)],
                     "temperature high": "0"}),
                right=transformer,
                left_on="transformer_type",
                right_on="transformer_type"),
        # TODO Only the purchase of centralized electricity is subject
        #  to charges, not the feed-in, is that correct?
        "links": pandas.merge(
                left=pandas.DataFrame.from_dict(
                    {"label": ["central_test_elec_central_link"],
                     "link_type": ["central_chp_elec_central_link"],
                     "bus1": ["central_test_elec_bus"],
                     "bus2": ["central_electricity_bus"]}),
                right=elec_link,
                left_on="link_type",
                right_on="link_type")}
    
    sheets["buses"] = pandas.concat(
            [sheets["buses"],
             pandas.merge(
                 left=pandas.DataFrame.from_dict(
                     {"label": ["central_test_elec_bus"],
                      "bus_type": ["central_chp_naturalgas_electricity_bus"]}),
                 right=elec_bus,
                 left_on="bus_type",
                 right_on="bus_type")])
    
    sheets["links"] = pandas.concat(
        [sheets["links"],
         pandas.merge(
             left=pandas.DataFrame.from_dict(
                 {"label": ["central_test_naturalgas_link"],
                  "link_type": ["central_naturalgas_chp_link"],
                  "bus1": ["central_naturalgas_bus"],
                  "bus2": ["central_test_bus"]}),
             right=fuel_link,
             left_on="link_type",
             right_on="link_type")])
    
    types = {"buses": ["bus_type"], "transformers": ["transformer_type"],
             "links": ["link_type"]}
    for key in sheets.keys():
        sheets[key] = sheets[key].drop(columns=types.get(key))
    
    return sheets


def test_create_central_chp(test_central_CHP_entry):
    from program_files.urban_district_upscaling.components.Central_components \
        import create_central_chp
    
    sheets = {"buses": pandas.DataFrame(),
              "transformers": pandas.DataFrame(),
              "links": pandas.DataFrame()}
    # start method to be tested
    sheets = create_central_chp(
            label="test",
            fuel_type="naturalgas",
            output="test_output_bus",
            central_elec_bus=True,
            central_fuel_bus=True,
            sheets=sheets,
            standard_parameters=pandas.ExcelFile(os.path.dirname(__file__)
                                                 +
                                                 "/standard_parameters.xlsx"))
    # assert rather the two dataframes are equal
    for key in sheets.keys():
        pandas.testing.assert_frame_equal(
                sheets[key], test_central_CHP_entry[key])
