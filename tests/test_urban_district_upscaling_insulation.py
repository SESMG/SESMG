import pandas
import pytest
import os


@pytest.fixture
def test_insulation_entries():
    # import standard parameter
    standard_parameters = pandas.ExcelFile(os.path.dirname(__file__)
                                           + "/standard_parameters.xlsx")
    insulations = standard_parameters.parse("7_insulation")
    insulation = insulations.loc[insulations["year of construction"]
                                 == "<1918"]
    
    sheets = {
        "insulation": pandas.DataFrame.from_dict({
            None: 3 * [0],
            "active": 3 * [1],
            "sink": 3 * ["test_heat_demand"],
            "temperature indoor": 3 * [20],
            "heat limit temperature": 3 * [15],
            "label": ["test_window", "test_wall", "test_roof"],
            "U-value old": [float(insulation["window"]),
                            float(insulation["outer wall"]),
                            float(insulation["roof"])],
            "U-value new": [float(insulations.loc[
                                    insulations["year of construction"]
                                    == "potential"]["window"]),
                            float(insulations.loc[
                                    insulations["year of construction"]
                                    == "potential"]["outer wall"]),
                            float(insulations.loc[
                                    insulations["year of construction"]
                                    == "potential flat"]["roof"])],
            "area": 3 * ["10"],
            "periodical costs": [
                float(insulations.loc[insulations["year of construction"]
                                      == "periodical costs"]["window"]),
                float(insulations.loc[insulations["year of construction"]
                                      == "periodical costs"]["outer wall"]),
                float(insulations.loc[insulations["year of construction"]
                                      == "periodical costs flat"]["roof"])],
            "periodical constraint costs":  [
                float(insulations.loc[
                        insulations["year of construction"]
                        == "periodical constraint costs"]["window"]),
                float(insulations.loc[
                        insulations["year of construction"]
                        == "periodical constraint costs"]["outer wall"]),
                float(insulations.loc[
                        insulations["year of construction"]
                        == "periodical constraint costs flat"]["roof"])],
        })
    }
    
    sheets["insulation"] = sheets["insulation"].set_index(None)
    return sheets


def test_create_building_insulation(test_insulation_entries):
    """
    
    """
    from program_files.urban_district_upscaling.components import Insulation
    
    sheets = {"insulation": pandas.DataFrame()}
    # building specific data
    building = {
        "year of construction": 1917,
        "rooftype": "flat roof",
        "label": "test",
        "area windows": "10",
        "area outer wall": "10",
        "area roof": "10"
    }
    # start method to be tested
    sheets = Insulation.create_building_insulation(
        building=building,
        sheets=sheets,
        standard_parameters=pandas.ExcelFile(os.path.dirname(__file__)
                                             + r"/standard_parameters.xlsx")
    )
    # assert rather the two dataframes are equal
    pandas.testing.assert_frame_equal(sheets["insulation"],
                                      test_insulation_entries["insulation"])
