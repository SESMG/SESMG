import pandas
import pytest


def test_import_scenario():
    from program_files.preprocessing.create_energy_system \
        import import_model_definition
    pass


@pytest.fixture
def test_nodes_data_entry():
    """
        Dictionary holding an exemplary entry of the energy system
        sheet of the users model definition to test whether the
        energy system's definition works correctly.
    """
    return {
        "energysystem": pandas.DataFrame.from_dict(data={
            "start date": ["01.01.2012 00:00:00"],
            "end date": ["30.12.2012 23:00:00"],
            "temporal resolution": ["h"],
            "timezone": ["Europe/Berlin"]}),
        "timeseries": pandas.DataFrame.from_dict(data={
            "timestamp": ["01.01.2012 00:00:00"]
        }),
        "weather data": pandas.DataFrame.from_dict(data={
            "timestamp": ["01.01.2012 00:00:00"]
        })
    }


def test_define_energy_system(test_nodes_data_entry):
    """
        With the help of this test it is checked whether the energy
        system framework conditions given by the user (time horizon,
        temporal resolution as well as geographical position) have been
        correctly transferred into the oemof structures. In addition,
        it is checked whether the conversion of the timeseries and
        weather data to the time zone given by the user was performed
        correctly.
    """
    from program_files.preprocessing.create_energy_system \
        import define_energy_system
    
    esys, nodes_data = define_energy_system(test_nodes_data_entry)
    
    test_time_index = pandas.date_range(
        start=test_nodes_data_entry["energysystem"].loc[0, "start date"],
        end=test_nodes_data_entry["energysystem"].loc[0, "end date"],
        freq=test_nodes_data_entry["energysystem"].loc[0, 
                                                       "temporal resolution"],
        tz=test_nodes_data_entry["energysystem"].loc[0, "timezone"])
    
    test_timestamp = pandas.to_datetime("01.01.2012 01:00:00 +0100")

    assert (esys.timeindex == test_time_index).all()
    assert nodes_data["timeseries"].index == test_timestamp
    assert nodes_data["weather data"].index == test_timestamp
