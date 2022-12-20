# -*- coding: utf-8 -*-


import pytest
import os
import pandas as pd
from program_files.urban_district_upscaling.components import Link



@pytest.fixture
def test_create_link_entry():
    # import standard parameter
    standard_parameters = pd.ExcelFile(os.path.dirname(__file__)
                                           + "/standard_parameters.xlsx")
    links = standard_parameters.parse("6_links")
    link = links.loc[links["link_type"] == "building_pv_building_link"]

    return {
        "links": pd.DataFrame.from_dict({
            "label": ["test_link"],
            "bus1": ["building_pv_bus"],
            "bus2": ["building_res_electricity_bus"],
            "comment": link["comment"].values,
            "active": link["active"].values,
            "(un)directed": link["(un)directed"].values,
            "efficiency": link["efficiency"].values,
            "variable output costs": link["variable output costs"].values,
            "variable output constraint costs": link["variable output constraint costs"].values,
            "existing capacity": link["existing capacity"].values,
            "min. investment capacity": link["min. investment capacity"].values,
            "max. investment capacity": link["max. investment capacity"].values,
            "periodical costs": link["periodical costs"].values, 
            "periodical constraint costs": link["periodical constraint costs"].values, 
            "non-convex investment": link["non-convex investment"].values, 
            "fix investment costs": link["fix investment costs"].values, 
            "fix investment constraint costs": link["fix investment constraint costs"].values 
            })
       } 


def test_create_link(test_create_link_entry):
    """
    testing create link function

    """

    sheets = {"links": pd.DataFrame()}
    # create a standard_parameter building_pv_building_link
    sheets = Link.create_link(label = "test_link",
                              bus_1 = "building_pv_bus", 
                              bus_2 = "building_res_electricity_bus", 
                              link_type = "building_pv_building_link", 
                              sheets = sheets,
                              standard_parameters = pd.ExcelFile(os.path.dirname(__file__)+ "/standard_parameters.xlsx")
                              )
        
    pd.testing.assert_frame_equal(sheets["links"],test_create_link_entry["links"])
    
    
    
def test_create_central_elec_bus_connection():
    
    pass
    
    
def test_restructuring_links():

    pass
    
    