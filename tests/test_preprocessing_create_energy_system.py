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

    start_local = pandas.to_datetime(test_nodes_data_entry["energysystem"].loc[0, "start date"])
    end_local = pandas.to_datetime(test_nodes_data_entry["energysystem"].loc[0, "end date"])
    timezone = test_nodes_data_entry["energysystem"].loc[0, "timezone"]

    # convert to utc
    start_utc = start_local.tz_localize(timezone).tz_convert("UTC")
    end_utc = end_local.tz_localize(timezone).tz_convert("UTC")

    # expected utc timestamp
    expected_time_index = pandas.date_range(
        start=start_utc,
        end=end_utc,
        freq=test_nodes_data_entry["energysystem"].loc[0, "temporal resolution"]
    )

    # expected time stamp
    expected_timestamp = pandas.to_datetime("2012-01-01 00:00:00").tz_localize("Europe/Berlin").tz_convert("UTC")

    assert (esys.timeindex == expected_time_index).all()
    assert nodes_data["timeseries"].index[0] == expected_timestamp
    assert nodes_data["weather data"].index[0] == expected_timestamp
