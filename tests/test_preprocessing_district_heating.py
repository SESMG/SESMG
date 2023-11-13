import dhnx
import os
import pytest
import tempfile
import pandas
from program_files.preprocessing.components import district_heating


@pytest.fixture
def thermal_net():
    """
        Fixture to create a new ThermalNetwork instance for each test.
    """
    return dhnx.network.ThermalNetwork()


@pytest.fixture
def temp_dir():
    """
        Fixture to create a temporary directory for test CSV files.
    """
    # Create a temporary directory to store test CSV files
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Remove the temporary directory and its contents
    for file_name in ["consumers.csv", "pipes.csv",
                      "producers.csv", "forks.csv"]:
        file_path = os.path.join(temp_dir, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
    os.rmdir(temp_dir)


def create_test_csv_files(temp_dir):
    """
        Helper function to create test CSV files in the specified
        directory (temp_dir).

        :param temp_dir: Temporary directory path.
        :type temp_dir: str resulting from pytest.fixture
    """
    # Create test CSV files for each component
    for dataframe in ["consumers", "pipes", "producers", "forks"]:
        data = {'Column1': [1, 2, 3], 'Column2': [4, 5, 6]}
        df = pandas.DataFrame(data)
        df.to_csv(os.path.join(temp_dir, f"{dataframe}.csv"), index=False)


def test_load_thermal_network_data(temp_dir, thermal_net):
    """
        Test the load_thermal_network_data function of the district
        heating algorithm.

        :param temp_dir: Temporary directory fixture.
        :type temp_dir: str resulting from pytest.fixture
        :param thermal_net: ThermalNetwork instance fixture.
        :type temp_dir: ThermalNetwork resulting from pytest.fixture
    """
    # Create test CSV files
    create_test_csv_files(temp_dir)

    # Call the function to load data
    loaded_thermal_net = district_heating.load_thermal_network_data(
        thermal_net=thermal_net, path=temp_dir)

    # Check if the components in the ThermalNetwork have been loaded
    # Check if the loaded dataframes are not empty
    for dataframe in ["consumers", "pipes", "producers", "forks"]:
        assert dataframe in loaded_thermal_net.components
        assert not loaded_thermal_net.components[dataframe].empty
        

def create_test_dataframes():
    """
        Helper function to create test DataFrames for each component.
    """
    dataframes = {}
    for dataframe in ["consumers", "pipes", "producers", "forks"]:
        data = {'Column1': [1, 2, 3], 'Column2': [4, 5, 6]}
        df = pandas.DataFrame(data)
        dataframes[dataframe] = df
    return dataframes
        
        
def test_save_thermal_network_data(temp_dir, thermal_net):
    """
        Test the save_thermal_network_data function.
    
        :param temp_dir: Temporary directory fixture.
        :type temp_dir: str resulting from pytest.fixture
        :param thermal_net: ThermalNetwork instance fixture.
        :type temp_dir: ThermalNetwork resulting from pytest.fixture
    """
    # Create test DataFrames for each component
    test_dataframes = create_test_dataframes()
    thermal_net.components = test_dataframes

    # Call the function to save data
    district_heating.save_thermal_network_data(thermal_net, temp_dir)

    # Check if the CSV files have been created in the specified directory
    for dataframe in ["consumers", "pipes", "producers", "forks"]:
        file_path = os.path.join(temp_dir, f"{dataframe}.csv")
        assert os.path.exists(file_path)

        # Check if the content of the saved CSV matches the original DataFrame
        loaded_df = pandas.read_csv(file_path)
        loaded_df = loaded_df.drop(columns=loaded_df.columns[
            loaded_df.columns.str.contains('unnamed', case=False)])
        pandas.testing.assert_frame_equal(left=loaded_df,
                                          right=test_dataframes[dataframe])


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


def test_concat_on_thermal_net_components(test_forks_dataframe, thermal_net):
    """
        This test checks if the concatenation of a new row to the
        Thermal Network dataframe (comp_type) works correctly.
    """
    # Calling the concat_on_thermal_net_components function with a
    # new_dict for 'forks' component type
    thermal_net = district_heating.concat_on_thermal_net_components(
        comp_type="forks",
        new_dict={"id": 1,
                  "lat": 10,
                  "lon": 10,
                  "component_type": "Fork",
                  "street": "test",
                  "t": 0.5,
                  "bus": "testbus"},
        thermal_net=thermal_net)
    
    # Comparing the resulting 'forks' component DataFrame with the
    # expected test dataframe
    pandas.testing.assert_frame_equal(
        left=thermal_net.components["forks"],
        right=test_forks_dataframe
    )
    
    
# Mocking the required objects for testing
class MockThermalNetwork:
    def __init__(self):
        self.components = {
            "forks": pandas.DataFrame({"id": [1, 2],
                                       "name": ["Fork1", "Fork2"]}),
            "consumers": pandas.DataFrame({"id": [1, 2],
                                           "name": ["Consumer1", "Consumer2"]}),
            "pipes": pandas.DataFrame({"id": [1, 2],
                                       "length": [100, 200]}),
            "producers": pandas.DataFrame({"id": [1, 2],
                                           "name": ["Producer1", "Producer2"]}),
        }


@pytest.mark.parametrize("dataframe_name", ["forks", "consumers", "pipes",
                                            "producers"])
def test_clear_thermal_net(dataframe_name):
    """
        Test for the clear_thermal_net function.
    
        This test checks if the method clears the specified dataframe
        in the Thermal Network correctly.
    
        :param dataframe_name: Name of the dataframe to test the \
            clearing.
        :type dataframe_name: str
    """
    # Arrange
    # Creating an instance of the MockThermalNetwork
    thermal_net = MockThermalNetwork()

    # Act
    # Calling the clear_thermal_net function to clear a specific dataframe
    result = district_heating.clear_thermal_net(thermal_net)

    # Assert
    # Verifying that the specified dataframe is now an empty dataframe
    assert result.components[dataframe_name].empty
    

def test_create_fork(test_forks_dataframe, thermal_net):
    """
        This test checks whether the row created by the create fork
        method has been correctly parameterized in the DataFrame of the
        thermal network forks.
    """
    thermal_net = district_heating.create_fork(
        point=["x", 10, 10, "x", 0.5, "test"],
        label=1,
        thermal_net=thermal_net,
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


def test_append_pipe(test_pipes_dataframe, thermal_net):
    """
        This test checks whether the row created by the append pipe
        method has been correctly parameterized in the DataFrame of the
        thermal network pipes.
    """
    thermal_net = district_heating.append_pipe(
        nodes=["forks-1", "forks-2"],
        length=30.0,
        street="test-street",
        thermal_net=thermal_net)
    
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
    

def test_create_intersection_forks(test_intersection_forks_dataframe,
                                   thermal_net):
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
        thermal_net=thermal_net)
    
    pandas.testing.assert_frame_equal(
        left=thermal_network.components["forks"].set_index(keys="id",
                                                           drop=True),
        right=test_intersection_forks_dataframe
    )
