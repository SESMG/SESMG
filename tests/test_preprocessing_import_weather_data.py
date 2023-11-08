import pandas
import os
from shapely.geometry import Point
from program_files.preprocessing import import_weather_data


def test_set_esys_data():
    """
        Tests whether the parameterization of the framework data of the
        energy system in the dictionary necessary for openfred have
        been correctly parameterized.
    """
    return_dict = import_weather_data.set_esys_data(
        nodes_data={
            "energysystem": pandas.DataFrame.from_dict({
                "start date": ["", pandas.to_datetime("01.01.2012 00:00:00")],
                "end date": ["", pandas.to_datetime("31.12.2012 23:00:00")]
            })
        },
        location=Point("3", "3"),
        variables="windpowerlib")
    
    test_dict = {
        "start": "2012-01-01",
        "stop": "2013-01-01",
        "locations": [Point("3", "3")],
        "heights": [10],
        "variables": "windpowerlib"
    }
    
    assert return_dict == test_dict


def test_import_open_fred_weather_data():
    """
        Tests if the weather data requested from OpenFred matches the
        data stored in the model definition. The reference location
        here is Düsseldorf Airport.
    """
    test_nodes_data = pandas.read_excel(
        os.path.dirname(os.path.dirname(__file__))
        + "/model_definition_example.xlsx",
        "weather data",
        parse_dates=["timestamp"])
    test_nodes_data = test_nodes_data.drop(columns=["timestamp",
                                                    "ground_temp",
                                                    "water_temp",
                                                    "groundwater_temp",
                                                    "heat_network_temp"])
    
    return_nodes_data = import_weather_data.import_open_fred_weather_data(
        nodes_data={
            "energysystem": pandas.DataFrame.from_dict({
                "start date": ["", pandas.to_datetime("01.01.2012 00:00:00")],
                "end date": ["", pandas.to_datetime("30.12.2012 23:00:00")]
            }),
            "weather data": pandas.DataFrame.from_dict({
                "pressure": [],
                "z0": [],
                "windspeed": [],
                "dhi": [],
                "dni": [],
                "ghi": [],
                "temperature": []}
            )},
        lat=51.3,
        lon=6.77
    )
        
    pandas.testing.assert_frame_equal(
        left=return_nodes_data["weather data"].sort_index(axis=1),
        right=test_nodes_data.sort_index(axis=1)
    )
