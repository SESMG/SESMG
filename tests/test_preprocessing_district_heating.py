import dhnx
import pytest
import pandas
from program_files.preprocessing.components import district_heating


@pytest.fixture
def test_forks_dataframe():
    """
        The pandas dataframe created here provides the benchmark for
        test_concat_on_thermal_net_components and test_create_fork.
    """
    return pandas.DataFrame.from_dict(
        {"id": [1],
         "lat": [10],
         "lon": [10],
         "component_type": ["Fork"],
         "street": ["test"],
         "t": [0.5],
         "bus": ["testbus"]}
    )


def test_concat_on_thermal_net_components(test_forks_dataframe):
    """
        This test checks if the concatenation of a new row to the
        Thermal Network dataframe (comp_type) works correctly.
    """
    thermal_net = district_heating.concat_on_thermal_net_components(
        comp_type="forks",
        new_dict={"id": 1,
                  "lat": 10,
                  "lon": 10,
                  "component_type": "Fork",
                  "street": "test",
                  "t": 0.5,
                  "bus": "testbus"},
        thermal_net=dhnx.network.ThermalNetwork())
    
    pandas.testing.assert_frame_equal(
        left=thermal_net.components["forks"],
        right=test_forks_dataframe
    )
    

def test_create_fork(test_forks_dataframe):
    """
        This test checks whether the row created by the create fork
        method has been correctly parameterized in the DataFrame of the
        thermal network forks.
    """
    thermal_net = district_heating.create_fork(
        point=["x", 10, 10, "x", 0.5, "test"],
        label=1,
        thermal_net=dhnx.network.ThermalNetwork(),
        bus="testbus")
    
    pandas.testing.assert_frame_equal(
        left=thermal_net.components["forks"],
        right=test_forks_dataframe
    )


@pytest.fixture
def test_pipes_dataframe():
    """
        The pandas dataframe created here provides the benchmark for
        test_append_pipe.
    """
    return pandas.DataFrame.from_dict(
        {"id": ["pipe-1"],
         "from_node": ["forks-1"],
         "to_node": ["forks-2"],
         "length": [30.0],
         "component_type": ["Pipe"],
         "street": ["test-street"]}
    )


def test_append_pipe(test_pipes_dataframe):
    """
        This test checks whether the row created by the append pipe
        method has been correctly parameterized in the DataFrame of the
        thermal network pipes.
    """
    thermal_net = district_heating.append_pipe(
        nodes=["forks-1", "forks-2"],
        length=30.0,
        street="test-street",
        thermal_net=dhnx.network.ThermalNetwork())
    
    pandas.testing.assert_frame_equal(
        left=thermal_net.components["pipes"],
        right=test_pipes_dataframe
    )
    

@pytest.fixture
def test_intersection_forks_dataframe():
    """
        The pandas dataframe created here provides the benchmark for
        test_create_intersection_forks.
    """
    return pandas.DataFrame.from_dict(
        {"id": ["0", "1"],
         "lat": [5, 6],
         "lon": [5, 6],
         "component_type": ["Fork", "Fork"]}
    ).set_index(keys="id")
    

def test_create_intersection_forks(test_intersection_forks_dataframe):
    """
        This test checks whether the rows created by the create
        intersection forks method have been correctly parameterized in
        the DataFrame of the thermal network forks.
    """
    thermal_network = district_heating.create_intersection_forks(
        street_sec=pandas.DataFrame.from_dict(
            {"label": ["test"],
             "active": [1],
             "lat. 1st intersection": [5],
             "lon. 1st intersection": [5],
             "lat. 2nd intersection": [6],
             "lon. 2nd intersection": [6]
             }
        ),
        thermal_net=dhnx.network.ThermalNetwork())
    
    pandas.testing.assert_frame_equal(
        left=thermal_network.components["forks"].set_index(keys="id",
                                                           drop=True),
        right=test_intersection_forks_dataframe
    )
