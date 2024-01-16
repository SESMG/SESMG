import pytest
import pandas
from program_files.urban_district_upscaling.components import Bus
import os

# import standard parameter
standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                       + "/standard_parameters.xlsx")
buses = standard_parameters.parse("1_buses")
links = standard_parameters.parse("6_links")


@pytest.fixture
def test_elec_bus_entry():
    """
   
    """
    return {"buses": pandas.merge(
        left=pandas.DataFrame.from_dict({
            "label": ["test_bus"],
            "bus_type": ["building_res_electricity_bus"],
            "district heating conn.": [float(0)]}),
        right=buses,
        on="bus_type").drop(columns=["bus_type"])}


@pytest.fixture
def test_heat_bus_entry():
    """
    
    """
    return {"buses": pandas.merge(
        left=pandas.DataFrame.from_dict({
            "label": ["test_bus1"],
            "bus_type": ["building_heat_bus"],
            "district heating conn.": [1],
            "lat": [10],
            "lon": [10]}),
        right=buses,
        on="bus_type").drop(columns=["bus_type"])}


def test_create_standard_parameter_bus(test_elec_bus_entry,
                                       test_heat_bus_entry):
    """
        Short description of the given TEST Suite
    """
    # create a standard_parameter building res electricity bus
    sheets = Bus.create_standard_parameter_bus(
        label="test_bus",
        bus_type="building_res_electricity_bus",
        sheets={"buses": pandas.DataFrame()},
        standard_parameters=standard_parameters)
    
    print(sheets["buses"]["active"])
    pandas.testing.assert_frame_equal(
        sheets["buses"].sort_index(axis=1),
        test_elec_bus_entry["buses"].sort_index(axis=1))
    
    # add a building heat bus with dh connection
    sheets = Bus.create_standard_parameter_bus(
        label="test_bus1",
        bus_type="building_heat_bus",
        sheets={"buses": pandas.DataFrame()},
        standard_parameters=standard_parameters,
        coords=[10, 10, 1])
    pandas.testing.assert_frame_equal(
        sheets["buses"].sort_index(axis=1),
        test_heat_bus_entry["buses"].sort_index(axis=1))
    
    
@pytest.fixture
def cluster_electricity_bus_entry():
    """
    
    """
    return {"buses": pandas.merge(
                left=pandas.DataFrame.from_dict({
                    "label": ["test1_res_electricity_bus",
                              "test1_com_electricity_bus",
                              "test1_ind_electricity_bus"],
                    "bus_type": ["building_res_electricity_bus",
                                 "building_com_electricity_bus",
                                 "building_ind_electricity_bus"],
                    "district heating conn.": [float(0)] * 3}),
                right=buses,
                on="bus_type").drop(columns=["bus_type"]),
            "links": pandas.merge(
                left=pandas.DataFrame.from_dict({
                    "label": ["test1_res_electricity_link",
                              "test1_com_electricity_link",
                              "test1_ind_electricity_link"],
                    "bus1": ["test1_electricity_bus"] * 3,
                    "bus2": ["test1_res_electricity_bus",
                             "test1_com_electricity_bus",
                             "test1_ind_electricity_bus"],
                    "link_type": ["cluster_electricity_link"] * 3}),
                right=links,
                on="link_type").drop(columns=["link_type"])}
    
    
def test_create_cluster_electricity_buses(cluster_electricity_bus_entry):
    """
    
    """
    from program_files.urban_district_upscaling.components.Bus \
        import create_cluster_electricity_buses
        
    sheets = create_cluster_electricity_buses(
        building=["test1", "test1", "SFB"],
        cluster="test1",
        sheets={"buses": pandas.DataFrame(data={"label": ["dummy"], "active": [1], "shortage": [1], "excess": [1], "shortage costs": [0], "excess costs": [0], "shortage constraint costs": [0], "excess constraint costs": [0], "district heating conn.": [0]}),
                "links": pandas.DataFrame(data={"label": ["dummy"], "active": [1], "bus1": ["dummy"], "bus2": ["dummy"], "(un)directed": ["dummy"], "variable output costs": [0], "variable output constraint costs": [0], "periodical constraint costs": [0], "periodical costs": [0], "non-convex investment": [0],
                                                "fix investment costs": [0], "fix investment constraint costs": [0], "efficiency": [0], "max. investment capacity": [0], "min. investment capacity": [0], "existing capacity": [0]})},
        standard_parameters=standard_parameters)
    
    sheets = create_cluster_electricity_buses(
            building=["test1", "test1", "COM"],
            cluster="test1",
            sheets=sheets,
            standard_parameters=standard_parameters)

    sheets = create_cluster_electricity_buses(
            building=["test1", "test1", "IND"],
            cluster="test1",
            sheets=sheets,
            standard_parameters=standard_parameters)
    
    no_changes_sheets = create_cluster_electricity_buses(
        building=["test1", "test1", "_"],
        cluster="test1",
        sheets=sheets,
        standard_parameters=standard_parameters)
    
    sheets["buses"] = sheets["buses"].query("label != 'dummy'")
    sheets["links"] = sheets["links"].query("label != 'dummy'")

    for key in sheets.keys():
        cluster_electricity_bus_entry[key].set_index(
                "label", inplace=True, drop=False)
        pandas.testing.assert_frame_equal(
            sheets[key].sort_index(axis=1),
            cluster_electricity_bus_entry[key].sort_index(axis=1))
        pandas.testing.assert_frame_equal(
            sheets[key].sort_index(axis=1),
            no_changes_sheets[key].sort_index(axis=1))
        
        
@pytest.fixture
def test_cluster_averaged_bus_entry():
    
    sheets = {"buses": pandas.merge(
            left=pandas.DataFrame.from_dict({
                "label": ["test1_gas_bus"],
                "bus_type": ["building_res_gas_bus"],
                "district heating conn.": [float(0)]}),
            right=buses,
            on="bus_type").drop(columns=["bus_type"])}
    
    res_gas_bus = buses.loc[buses["bus_type"] == "building_res_gas_bus"]
    com_gas_bus = buses.loc[buses["bus_type"] == "building_com_gas_bus"]
    ind_gas_bus = buses.loc[buses["bus_type"] == "building_ind_gas_bus"]
    
    sheets["buses"].loc[0, "shortage costs"] = \
        (1/6) * float(res_gas_bus["shortage costs"]) \
        + (2/6) * float(com_gas_bus["shortage costs"]) \
        + (3/6) * float(ind_gas_bus["shortage costs"])
    
    return sheets


def test_create_cluster_averaged_bus(test_cluster_averaged_bus_entry):
    """
    
    """
    from program_files.urban_district_upscaling.components.Bus \
        import create_cluster_averaged_bus
    sink_parameters = ["x", "x", "x", "x", 1, 2, 3]
    
    sheets = create_cluster_averaged_bus(
        sink_parameters=sink_parameters,
        cluster="test1",
        fuel_type="gas",
        sheets={"buses": pandas.DataFrame()},
        standard_parameters=standard_parameters)
    
    test_cluster_averaged_bus_entry["buses"].set_index(
        "label", inplace=True, drop=False)
    
    pandas.testing.assert_frame_equal(
        sheets["buses"].sort_index(axis=1),
        test_cluster_averaged_bus_entry["buses"].sort_index(axis=1)
    )


