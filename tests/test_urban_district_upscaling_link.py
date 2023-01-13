import pytest
import os
import pandas
from program_files.urban_district_upscaling.components import Link


@pytest.fixture
def test_create_link_entry():
    # import standard parameter
    standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                           + "/standard_parameters.xlsx")
    links = standard_parameters.parse("6_links")
    link = links.loc[links["link_type"] == "building_pv_building_link"]

    # combine specific data and the standard parameter data
    sheets = {
        "links":
            pandas.merge(
                left=pandas.DataFrame.from_dict({
                    "label": ["test_link"],
                    "bus1": ["building_pv_bus"],
                    "link_type": ["building_pv_building_link"],
                    "bus2": ["building_res_electricity_bus"]}),
                right=link,
                left_on="link_type",
                right_on="link_type")}

    # remove column which was used to merge the two dataframe parts
    sheets["links"] = sheets["links"].drop(columns=["link_type"])

    return sheets


def test_create_link(test_create_link_entry):
    """
    testing create link function

    """

    sheets = {"links": pandas.DataFrame()}
    # start the method to be tested
    sheets = Link.create_link(
        label="test_link",
        bus_1="building_pv_bus",
        bus_2="building_res_electricity_bus",
        link_type="building_pv_building_link",
        sheets=sheets,
        standard_parameters=pandas.ExcelFile(os.path.dirname(__file__)
                                             + r"/standard_parameters.xlsx")
      )
    # assert rather the two dataframes are equal
    pandas.testing.assert_frame_equal(sheets["links"],
                                      test_create_link_entry["links"])
    
    
def test_create_central_elec_bus_connection():
    pass
    
    
def test_restructuring_links():

    pass