import pytest
import pandas
import os


@pytest.fixture
def test_decentral_pv_source_entry():
    """
    
    """
    # import standard parameter
    standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                           + "/standard_parameters.xlsx")
    sources = standard_parameters.parse("3_sources")
    source = sources.loc[sources["source_type"] == "fixed photovoltaic source"]

    # combine specific data and the standard parameter data
    sheets = {
        "sources":
            pandas.merge(
                    left=pandas.DataFrame.from_dict({
                        "label": ["test_1_pv_source"],
                        "source_type": ["fixed photovoltaic source"],
                        "output": ["test_pv_bus"],
                        "Azimuth": [10],
                        "Surface Tilt": [10],
                        "Latitude": [10],
                        "Longitude": [10],
                        "input": [0],
                        "Temperature Inlet": [0],
                        "max. investment capacity": source[
                            "Capacity per Area (kW/m2)"] * 100}),
                    right=source,
                    left_on="source_type",
                    right_on="source_type"
            )}
    
    # remove column which was used to merge the two dataframe parts
    sheets["sources"] = sheets["sources"].drop(columns=[
        "source_type", "max. investment capacity_y"])
    # rename the max invest column since it is renamed by the merge
    # above
    sheets["sources"] = sheets["sources"].rename(columns={
        "max. investment capacity_x": "max. investment capacity"})
    
    return sheets


@pytest.fixture
def test_decentral_st_source_entry():
    """

    """
    # import standard parameter
    standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                           + "/standard_parameters.xlsx")
    sources = standard_parameters.parse("3_sources")
    source = sources.loc[sources["source_type"] == "solar_thermal_collector"]
    
    # combine specific data and the standard parameter data
    sheets = {
        "sources":
            pandas.merge(
                    left=pandas.DataFrame.from_dict({
                        "label": ["test_1_solarthermal_source"],
                        "source_type": ["solar_thermal_collector"],
                        "output": ["test_heat_bus"],
                        "Azimuth": [10],
                        "Surface Tilt": [10],
                        "Latitude": [10],
                        "Longitude": [10],
                        "input": ["test_electricity_bus"],
                        "Temperature Inlet": [float(40)],
                        "max. investment capacity": source[
                                                        "Capacity per Area ("
                                                        "kW/m2)"] * 100}),
                    right=source,
                    left_on="source_type",
                    right_on="source_type"
            )}
    
    # remove column which was used to merge the two dataframe parts
    sheets["sources"] = sheets["sources"].drop(columns=[
        "source_type", "max. investment capacity_y"])
    # rename the max invest column since it is renamed by the merge
    # above
    sheets["sources"] = sheets["sources"].rename(columns={
        "max. investment capacity_x": "max. investment capacity"})
    
    return sheets


@pytest.fixture
def test_competition_constraint_entry():
    """

    """
    # import standard parameter
    standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                           + "/standard_parameters.xlsx")
    sources = standard_parameters.parse("3_sources")
    pv_source = sources.loc[sources["source_type"]
                            == "fixed photovoltaic source"]
    st_source = sources.loc[sources["source_type"]
                            == "solar_thermal_collector"]
    
    return {"competition constraints":
        pandas.DataFrame.from_dict({
            "component 1": ["test_1_pv_source"],
            "factor 1": [float(1 / pv_source["Capacity per Area (kW/m2)"])],
            "component 2": ["test_1_solarthermal_source"],
            "factor 2": [float(1 / st_source["Capacity per Area (kW/m2)"])],
            "limit": [100],
            "active": [1]})
    }

   
def test_create_source(test_decentral_pv_source_entry):
    """
    
    """
    
    from program_files.urban_district_upscaling.components.Source \
        import create_source
    
    sheets = {"sources": pandas.DataFrame()}
    
    # building specific parameter
    building = {
        "label": "test",
        "azimuth 1": 10,
        "surface tilt 1": 10,
        "latitude": 10,
        "longitude": 10,
        "roof area 1": 100
    }
    # start the method to be tested
    sheets = create_source(
        source_type="fixed photovoltaic source",
        roof_num=1,
        building=building,
        sheets=sheets,
        standard_parameters=pandas.ExcelFile(os.path.dirname(__file__)
                                             + r"/standard_parameters.xlsx")
    )
    # assert rather the two dataframes are equal
    pandas.testing.assert_frame_equal(
        sheets["sources"], test_decentral_pv_source_entry["sources"])


def test_create_timeseries_source():
    pass


def test_create_competition_constraint(test_competition_constraint_entry):
    """
    
    """
    from program_files.urban_district_upscaling.components import Source
    sheets = {"competition constraints": pandas.DataFrame()}
    
    Source.create_competition_constraint(
        limit=100,
        label="test",
        roof_num=1,
        sheets=sheets,
        standard_parameters=pandas.ExcelFile(os.path.dirname(__file__)
                                             + r"/standard_parameters.xlsx")
    )

    pandas.testing.assert_frame_equal(
        sheets["competition constraints"],
        test_competition_constraint_entry["competition constraints"])


def test_create_sources(test_competition_constraint_entry,
                        test_decentral_st_source_entry,
                        test_decentral_pv_source_entry):
    """
    
    """
    from program_files.urban_district_upscaling.components.Source \
        import create_sources
    
    sheets = {"sources": pandas.DataFrame(),
              "competition constraints": pandas.DataFrame()}
    
    # building specific parameter
    building = {
        "label": "test",
        "azimuth 1": 10,
        "surface tilt 1": 10,
        "latitude": 10,
        "longitude": 10,
        "roof area 1": 100,
        "flow temperature": 60,
        "st or pv 1": "pv&st",
        "building type": "SFB"
    }
    # start the method to be tested
    sheets = create_sources(
        building=building,
        clustering=False,
        sheets=sheets,
        standard_parameters=pandas.ExcelFile(os.path.dirname(__file__)
                                             + r"/standard_parameters.xlsx"),
    )
    test_sheets = pandas.concat([test_decentral_pv_source_entry["sources"],
                                 test_decentral_st_source_entry["sources"]],
                                axis=0)
    # assert rather the two dataframes are equal
    pandas.testing.assert_frame_equal(sheets["sources"], test_sheets)

    pandas.testing.assert_frame_equal(
            sheets["competition constraints"],
            test_competition_constraint_entry["competition constraints"])

def test_cluster_sources_information():
    pass


def test_sources_clustering():
    pass


def test_create_cluster_sources():
    pass


def test_update_sources_in_output():
    pass
