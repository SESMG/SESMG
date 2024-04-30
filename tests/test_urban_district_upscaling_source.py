import pytest
import pandas
from tests.conftest import (get_standard_parameter_data,
                            import_standard_parameter_data)
from program_files.urban_district_upscaling.components import Source

test_sheets_clustering = pandas.DataFrame(columns=["label"])
test_sheets_clustering.set_index("label", inplace=True, drop=False)


@pytest.fixture
def test_decentral_pv_source_entry():
    """
        Create a decentral roof mounted photovoltaic source for a roof
        of 100 sqm.
    """
    sources = import_standard_parameter_data(label="3_sources")
    source = sources.query("`source type` "
                           "== 'photovoltaic system roof-mounted decentral'")
    # combine specific data and the standard parameter data
    sheets = {"sources": pandas.merge(
        left=pandas.DataFrame.from_dict({
            "label": ["test_1_pv_source"],
            "source type": ["photovoltaic system roof-mounted decentral"],
            "output": ["test_pv_bus"],
            "azimuth": [10],
            "surface tilt": [10],
            "latitude": [10],
            "longitude": [10],
            "input": [0],
            "temperature inlet": [0],
            "min. investment capacity": [float(0)],
            "max. investment capacity": source["capacity per area"] * 100}),
        right=sources,
        on="source type"
    ).drop(columns=["source type", "max. investment capacity_y"])}
    
    # rename the max invest column since it is renamed by the merge
    # above
    sheets["sources"] = sheets["sources"].rename(columns={
        "max. investment capacity_x": "max. investment capacity"})
    
    return sheets


@pytest.fixture
def test_decentral_st_source_entry():
    """
        Create a decentral roof mounted solar thermal source for a roof
        of 100 sqm.
    """
    sources = import_standard_parameter_data(label="3_sources")
    source = sources.query("`source type` "
                           "== 'solar thermal system roof-mounted decentral'")
    # combine specific data and the standard parameter data
    sheets = {"sources": pandas.merge(
        left=pandas.DataFrame.from_dict({
            "label": ["test_1_solarthermal_source"],
            "source type": ["solar thermal system roof-mounted decentral"],
            "output": ["test_heat_bus"],
            "azimuth": [10],
            "surface tilt": [10],
            "latitude": [10],
            "longitude": [10],
            "input": ["test_electricity_bus"],
            "temperature inlet": [float(40)],
            "min. investment capacity": [float(0)],
            "max. investment capacity": source["capacity per area"] * 100}),
        right=sources,
        on="source type"
    ).drop(columns=["source type", "max. investment capacity_y"])}
    
    # rename the max invest column since it is renamed by the merge
    # above
    sheets["sources"] = sheets["sources"].rename(columns={
        "max. investment capacity_x": "max. investment capacity"})
    
    return sheets


@pytest.fixture
def test_competition_constraint_entry():
    """
        Create a competition constraint for two decentral sources
        (photovoltaic / solar thermal) for a total roof area of
        100 sqm.
    """
    sources = import_standard_parameter_data(label="3_sources")
    pv_source = sources.query("`source type` "
                           "== 'photovoltaic system roof-mounted decentral'")
    st_source = sources.query("`source type` "
                           "== 'solar thermal system roof-mounted decentral'")
    
    return {
        "competition constraints":
            pandas.DataFrame.from_dict({
                "component 1": ["test_1_pv_source"],
                "factor 1": [float(1 / pv_source["capacity per area"])],
                "component 2": ["test_1_solarthermal_source"],
                "factor 2": [float(1 / st_source["capacity per area"])],
                "limit": [100],
                "active": [1]})
    }

   
def test_create_source(test_decentral_pv_source_entry):
    """
        Create a standard parameter photovoltaic source and compare it
        to the manual created one.
    """
    
    sheets = {"sources": pandas.DataFrame()}
    
    # building specific parameter
    building = {
        "label": "test",
        "azimuth 1": 10,
        "surface tilt 1": 10,
        "latitude": 10,
        "longitude": 10,
        "roof area 1": 100,
        "solar thermal share": "standard"
    }
    # start the method to be tested
    sheets = Source.create_source(
        source_type="photovoltaic system roof-mounted decentral",
        roof_num=str(1),
        building=pandas.Series(data=building),
        sheets=sheets,
        standard_parameters=get_standard_parameter_data(),
    )
    # assert rather the two dataframes are equal
    pandas.testing.assert_frame_equal(
        sheets["sources"].sort_index(axis=1),
        test_decentral_pv_source_entry["sources"].sort_index(axis=1))


def test_create_timeseries_source():
    pass


def test_create_competition_constraint(test_competition_constraint_entry):
    """
        Create a standard parameter competition constraint and compare
        it to the manual created one to validate functionality of the
        creation algorithm.
    """
    sheets = Source.create_competition_constraint(
        limit=100,
        label="test",
        roof_num=str(1),
        types=["photovoltaic system roof-mounted decentral",
               "solar thermal system roof-mounted decentral"],
        sheets={"competition constraints": pandas.DataFrame()},
        standard_parameters=get_standard_parameter_data()
    )

    pandas.testing.assert_frame_equal(
        sheets["competition constraints"],
        test_competition_constraint_entry["competition constraints"])


def test_create_sources(test_competition_constraint_entry,
                        test_decentral_st_source_entry,
                        test_decentral_pv_source_entry):
    """
        Create two standard parameter sources (photovoltaic and
        solar thermal) using the same roof (competition constraint)
        and compare the resulting entries with the manual created ones
        to validate the functionality of the creation algorithm.
    """
    # building specific parameter
    building = {
        "label": "test",
        "azimuth 1": 10,
        "surface tilt 1": 10,
        "latitude": 10,
        "longitude": 10,
        "roof area 1": 100,
        "flow temperature": 60,
        "st 1": "yes",
        "pv 1": "yes",
        "building type": "single family building",
        "solar thermal share": "standard"
    }
    # start the method to be tested
    sheets = Source.create_sources(
        building=pandas.Series(data=building),
        clustering=False,
        sheets={"sources": pandas.DataFrame(),
                "competition constraints": pandas.DataFrame()},
        standard_parameters=get_standard_parameter_data()
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
        Test the collection of the sources parameter to be clustered
        afterward. Within this method all types of sources are testes
        (photovoltaic / pv, solar thermal flat plates / st).
    """
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
        "albedo": [10, 10],
        "altitude": [10, 10],
        "azimuth": [0, 0],
        "surface tilt": [30, 30],
        "latitude": [10, 10],
        "longitude": [50, 50],
        "temperature inlet": [0, 40]
    })
    
    source_param = {}
    test_source_param = {}
    for i in ["pv", "st"]:
        for j in ["south_west", "west", "north_west", "north", "north_east",
                  "east", "south_east", "south"]:
            source_param.update({i + "_" + j: [0] * 12})
            test_source_param.update({i + "_" + j: [0] * 12})
    
    for num, test in source.iterrows():
        source_param, sheets = Source.cluster_sources_information(
            source=test,
            source_param=source_param,
            azimuth_type="north",
            sheets=sheets
        )
    
    pandas.testing.assert_frame_equal(sheets["sources"],
                                      test_sheets_clustering)
    
    test_source_param.update({
        "pv_north": [1, 500, 10, 10, 50, 10, 10, 0, 30, 10, 50, 0],
        "st_north": [1, 500, 10, 10, 50, 10, 10, 0, 30, 10, 50, 40],
    })
    
    assert source_param == test_source_param


def test_sources_clustering():
    """
        Test the clustering of sources by inserting one pv source which
        has to be collected (parameter) and removed from the old sheets
        dataframe.
    """
    source_param = {}
    test_source_param = {}
    for i in ["pv", "st"]:
        for j in ["south_west", "west", "north_west", "north", "north_east",
                  "east", "south_east", "south"]:
            source_param.update({i + "_" + j: [0] * 12})
            test_source_param.update({i + "_" + j: [0] * 12})
    
    building = ["testbuilding", "testparcel", "COM"]
    
    sheets = {"sources": pandas.DataFrame.from_dict({
        "label": ["testbuilding_pv_1"]})}
    
    sheets["sources"].set_index("label", inplace=True, drop=False)
    
    sheets_clustering = {"sources": pandas.DataFrame.from_dict({
        "label": ["testbuilding_pv_1"],
        "technology": ["photovoltaic"],
        "max. investment capacity": [500],
        "periodical costs": [10],
        "periodical constraint costs": [10],
        "variable costs": [50],
        "albedo": [10],
        "altitude": [10],
        "azimuth": [0],
        "surface tilt": [30],
        "latitude": [10],
        "longitude": [50],
        "temperature inlet": [0]
    })}
    
    source_param, sheets = Source.sources_clustering(
        source_param=source_param,
        building=building,
        sheets=sheets,
        sheets_clustering=sheets_clustering
    )

    pandas.testing.assert_frame_equal(sheets["sources"],
                                      test_sheets_clustering)

    test_source_param.update({
        "pv_north": [1, 500, 10, 10, 50, 10, 10, 0, 30, 10, 50, 0],
    })

    assert source_param == test_source_param


@pytest.fixture
def test_clustered_pv_source_entry():
    """
        Create a data set of a north cluster photovoltaic source.
    """
    # combine specific data and the standard parameter data
    sheets = {"sources": pandas.merge(
        left=pandas.DataFrame.from_dict({
            "label": ["test_cluster_north_pv_source"],
            "source type": ["photovoltaic system roof-mounted decentral"],
            "output": ["test_cluster_pv_bus"],
            "azimuth": [0],
            "surface tilt": [30],
            "latitude": [10],
            "longitude": [50],
            "input": [0],
            "temperature inlet": [0],
            "max. investment capacity": [500],
            "min. investment capacity": [float(0)]}),
        right=import_standard_parameter_data(label="3_sources"),
        on="source type").drop(
            columns=["source type", "max. investment capacity_y"])}
    
    # rename the max invest column since it is renamed by the merge
    # above
    sheets["sources"] = sheets["sources"].rename(columns={
        "max. investment capacity_x": "max. investment capacity"})
    
    return sheets


@pytest.fixture
def test_clustered_st_source_entry():
    """
        Create a data set of a north cluster solar thermal source.
    """
    # combine specific data and the standard parameter data
    sheets = {"sources": pandas.merge(
        left=pandas.DataFrame.from_dict({
            "label": ["test_cluster_north_solarthermal_source"],
            "source type": ["solar thermal system roof-mounted decentral"],
            "output": ["test_cluster_heat_bus"],
            "azimuth": [0],
            "surface tilt": [float(30)],
            "latitude": [float(10)],
            "longitude": [float(50)],
            "input": ["test_cluster_electricity_bus"],
            # Flow temperature (40K) - 2 * temperature difference (10K)
            "temperature inlet": [float(20)],
            "max. investment capacity": [float(500)],
            "min. investment capacity": [float(0)]}),
        right=import_standard_parameter_data(label="3_sources"),
        on="source type").drop(
            columns=["source type", "max. investment capacity_y"])}
    
    # rename the max invest column since it is renamed by the merge
    # above
    sheets["sources"] = sheets["sources"].rename(columns={
        "max. investment capacity_x": "max. investment capacity"})
    
    return sheets


@pytest.fixture
def test_clustered_competition_constraint_entry():
    """
        Create a data set of a competition constraint for the two
        north oriented cluster sources above.
    """
    sources = import_standard_parameter_data(label="3_sources")
    pv_source = sources.loc[sources["source type"]
                            == "photovoltaic system roof-mounted decentral"]
    st_source = sources.loc[sources["source type"]
                            == "solar thermal system roof-mounted decentral"]
    
    sheets = {
        "competition constraints":
            pandas.DataFrame.from_dict({
                None: [0],
                "component 1": ["test_cluster_north_pv_source"],
                "factor 1": [
                    float(1 / pv_source["capacity per area"])],
                "component 2": ["test_cluster_north_solarthermal_source"],
                "factor 2": [
                    float(1 / st_source["capacity per area"])],
                "limit": 500 / pv_source["capacity per area"],
                "active": [1]})
    }
    
    sheets["competition constraints"] = \
        sheets["competition constraints"].set_index(None, drop=True)
    
    return sheets


@pytest.fixture
def test_pv_bus_entry():
    """
        Create a data set of the cluster pv bus.
    """
    # create control data structure
    sheets = {
        "buses": pandas.merge(
            left=pandas.DataFrame.from_dict(
                {"label": ["test_cluster_pv_bus"],
                 "bus type": ["electricity bus photovoltaic decentral"],
                 "district heating conn. (exergy)": [float(0)]}),
            right=import_standard_parameter_data(label="1_buses"),
            on="bus type").drop(columns=["bus type"])}
    
    sheets["buses"].set_index("label", drop=False)

    return sheets


def test_create_cluster_sources(test_clustered_pv_source_entry,
                                test_clustered_st_source_entry,
                                test_clustered_competition_constraint_entry,
                                test_pv_bus_entry):
    """
        Test the creation of two north oriented sources (photovoltaic
        and solar thermal) with an area competition and its buses.
    """
    source_param = {}
    for i in ["pv", "st"]:
        for j in ["south_west", "west", "north_west", "north", "north_east",
                  "east", "south_east", "south"]:
            source_param.update({i + "_" + j: [0] * 12})

    source_param.update({
        "pv_north": [1, 500, 10, 10, 50, 10, 10, 0, 30, 10, 50, 0],
        "st_north": [1, 500, 10, 10, 50, 10, 10, 0, 30, 10, 50, 40],
    })
    
    sheets = Source.create_cluster_sources(
        source_param=source_param,
        cluster="test_cluster",
        sheets={"competition constraints": pandas.DataFrame(),
                "buses": pandas.DataFrame(),
                "sources": pandas.DataFrame()},
        standard_parameters=get_standard_parameter_data()
    )
    test_sheets = {}

    test_sheets.update(test_clustered_competition_constraint_entry)
    test_sheets.update({"sources": pandas.concat(
            [test_clustered_pv_source_entry["sources"],
             test_clustered_st_source_entry["sources"]])})
    test_sheets.update(test_pv_bus_entry)
    
    for key in sheets.keys():
        print(key)
        pandas.testing.assert_frame_equal(
            sheets[key].sort_index(axis=1),
            test_sheets[key].sort_index(axis=1))


def test_update_sources_in_output():
    pass
