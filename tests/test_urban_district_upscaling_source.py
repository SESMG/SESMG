import pytest
import pandas
import os


# import standard parameter
standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                       + "/standard_parameters.xlsx")
sources = standard_parameters.parse("3_sources")


@pytest.fixture
def test_decentral_pv_source_entry():
    """
    
    """
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
                    right=sources,
                    on="source_type"
            ).drop(columns=["source_type", "max. investment capacity_y"])}
    
    # rename the max invest column since it is renamed by the merge
    # above
    sheets["sources"] = sheets["sources"].rename(columns={
        "max. investment capacity_x": "max. investment capacity"})
    
    return sheets


@pytest.fixture
def test_decentral_st_source_entry():
    """

    """
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
                    right=sources,
                    on="source_type"
            ).drop(columns=["source_type", "max. investment capacity_y"])}
    
    # rename the max invest column since it is renamed by the merge
    # above
    sheets["sources"] = sheets["sources"].rename(columns={
        "max. investment capacity_x": "max. investment capacity"})
    
    return sheets


@pytest.fixture
def test_competition_constraint_entry():
    """

    """
    pv_source = sources.loc[sources["source_type"]
                            == "fixed photovoltaic source"]
    st_source = sources.loc[sources["source_type"]
                            == "solar_thermal_collector"]
    
    return {
        "competition constraints":
            pandas.DataFrame.from_dict({
                "component 1": ["test_1_pv_source"],
                "factor 1": [
                    float(1 / pv_source["Capacity per Area (kW/m2)"])],
                "component 2": ["test_1_solarthermal_source"],
                "factor 2": [
                    float(1 / st_source["Capacity per Area (kW/m2)"])],
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
        roof_num=str(1),
        building=building,
        sheets=sheets,
        standard_parameters=standard_parameters
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
        roof_num=str(1),
        sheets=sheets,
        standard_parameters=standard_parameters
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
        standard_parameters=standard_parameters
    )
    test_sheets = pandas.concat([test_decentral_pv_source_entry["sources"],
                                 test_decentral_st_source_entry["sources"]],
                                axis=0)
    # assert rather the two dataframes are equal
    pandas.testing.assert_frame_equal(
        sheets["sources"].sort_index(axis=1),
        test_sheets.sort_index(axis=1))

    pandas.testing.assert_frame_equal(
        sheets["competition constraints"].sort_index(axis=1),
        test_competition_constraint_entry[
            "competition constraints"].sort_index(axis=1))


def test_cluster_sources_information():
    """
    
    """
    from program_files.urban_district_upscaling.components.Source \
        import cluster_sources_information
    sheets = {"sources": pandas.DataFrame.from_dict({
        "label": ["test_1", "test_2"]})}
    sheets["sources"].set_index("label", inplace=True, drop=False)
    
    source = pandas.DataFrame.from_dict({
        "label": ["test_1", "test_2"],
        "technology": ["photovoltaic", "solar_thermal_flat_plate"],
        "max. investment capacity": [500, 500],
        "periodical costs": [10, 10],
        "periodical constraint costs": [10, 10],
        "variable costs": [50, 50],
        "Albedo": [10, 10],
        "Altitude": [10, 10],
        "Azimuth": [0, 0],
        "Surface Tilt": [30, 30],
        "Latitude": [10, 10],
        "Longitude": [50, 50],
        "Temperature Inlet": [0, 40]
    })
    
    source_param = {}
    test_source_param = {}
    for i in ["pv", "st"]:
        for j in ["south_west", "west", "north_west", "north", "north_east",
                  "east", "south_east", "south"]:
            source_param.update({i + "_" + j: [0] * 12})
            test_source_param.update({i + "_" + j: [0] * 12})
    
    for num, test in source.iterrows():
        source_param, sheets = cluster_sources_information(
            source=test,
            source_param=source_param,
            azimuth_type="north",
            sheets=sheets
        )
    
    test_sheets = pandas.DataFrame(columns=["label"])
    test_sheets.set_index("label", inplace=True, drop=False)
    
    pandas.testing.assert_frame_equal(sheets["sources"], test_sheets)
    
    test_source_param.update({
        "pv_north": [1, 500, 10, 10, 50, 10, 10, 0, 30, 10, 50, 0],
        "st_north": [1, 500, 10, 10, 50, 10, 10, 0, 30, 10, 50, 40],
    })
    
    assert source_param == test_source_param


def test_sources_clustering():
    pass


def test_create_cluster_sources():
    pass


def test_update_sources_in_output():
    pass
