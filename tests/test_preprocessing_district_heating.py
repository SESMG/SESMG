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
    for file_name in ["consumers_exergy.csv", "pipes_exergy.csv",
                      "producers_exergy.csv", "forks_exergy.csv",
                      "consumers_anergy.csv", "pipes_anergy.csv",
                      "producers_anergy.csv", "forks_anergy.csv"]:
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
        for is_exergy in ["exergy", "anergy"]:
            data = {'Column1': [1, 2, 3], 'Column2': [4, 5, 6]}
            df = pandas.DataFrame(data)
            df.to_csv(os.path.join(temp_dir, f"{dataframe}_{is_exergy}.csv"),
                      index=False)


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
        thermal_net=thermal_net, path=temp_dir, is_exergy=True)

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
    district_heating.save_thermal_network_data(
        thermal_net=thermal_net, path=temp_dir, is_exergy=True)

    # Check if the CSV files have been created in the specified directory
    for dataframe in ["consumers", "pipes", "producers", "forks"]:
        file_path = os.path.join(temp_dir, f"{dataframe}_exergy.csv")
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
            "forks": pandas.DataFrame({
                "id": [1, 2],
                "name": ["Fork1", "Fork2"]}),
            "consumers": pandas.DataFrame({
                "id": [1, 2],
                "name": ["Consumer1", "Consumer2"]}),
            "pipes": pandas.DataFrame({
                "id": [1, 2],
                "length": [100, 200]}),
            "producers": pandas.DataFrame({
                "id": [1, 2],
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
    # Creating an instance of the MockThermalNetwork
    thermal_net = MockThermalNetwork()

    # Calling the clear_thermal_net function to clear a specific dataframe
    result = district_heating.clear_thermal_net(thermal_net)

    # Verifying that the specified dataframe is now an empty dataframe
    assert result.components[dataframe_name].empty
    
    
class MockOemofInvestOptimizationModel:
    def __init__(self, nodes):
        self.nodes = nodes
        

@pytest.fixture
def mock_oemof_model():
    """
        Initialize a dummy thermal network consisting of two buses,
        two sinks and a source
    """
    from oemof import solph
    return MockOemofInvestOptimizationModel([
        solph.buses.Bus(label="bus1"),
        solph.buses.Bus(label="bus2"),
        solph.components.Sink(label="demand1"),
        solph.components.Sink(label="demand2"),
        solph.components.Source(label="other_node")])


def test_remove_sinks_collect_buses(mock_oemof_model):
    """
        Test for the remove_sinks_collect_buses function.
    
        This test checks if the method correctly removes empty sinks
        from the OemofInvestOptimizationModel.
    
        :param mock_oemof_model: A mock OemofInvestOptimizationModel \
            for testing.
        :type mock_oemof_model: MockOemofInvestOptimizationModel
    """
    # Initialize the required inputs for the remove redundant sinks
    # method of the district heating module which will be tested
    # afterwards. Therefore a dict of buses which will be the result
    # of the remove_sinks_collect_buses function is created.
    initial_node_count = len(mock_oemof_model.nodes)
    initial_buses = {}

    # Calling the remove_sinks_collect_buses method and catch it's
    # result for the upcoming assertions
    updated_model, updated_buses = district_heating.remove_sinks_collect_buses(
        oemof_opti_model=mock_oemof_model, busd=initial_buses)
    
    # Check if sinks are removed
    assert len(updated_model.nodes) < initial_node_count
    assert "demand1" not in [node.label for node in updated_model.nodes]
    assert "demand2" not in [node.label for node in updated_model.nodes]
    # since buses should not be removed the length has to be equal
    assert len(updated_buses) == 2
    # Other nodes should not be affected
    assert "other_node" in [node.label for node in updated_model.nodes]
    
    
class MockThermalNetwork2:
    """
        A mock class representing a simplified version of the
        ThermalNetwork.
    
        This class is used for testing purposes to simulate a
        ThermalNetwork instance. It includes placeholders for
        components such as forks, pipes, consumers, and producers.
    
        :param forks: DataFrame representing fork components.
        :type forks: pandas.DataFrame
        :param pipes: DataFrame representing pipe components.
        :type pipes: pandas.DataFrame
        :param consumers: DataFrame representing consumer components.
        :type consumers: pandas.DataFrame
        :param producers: DataFrame representing producer components.
        :type producers: pandas.DataFrame
    """

    def __init__(self, forks, pipes, consumers, producers):
        """
            Initialize the MockThermalNetwork2 instance with provided
            dataframes.
    
            :param forks: DataFrame representing fork components.
            :type forks: pandas.DataFrame
            :param pipes: DataFrame representing pipe components.
            :type pipes: pandas.DataFrame
            :param consumers: DataFrame representing consumer \
                components.
            :type consumers: pandas.DataFrame
            :param producers: DataFrame representing producer \
                components.
            :type producers: pandas.DataFrame
        """
        self.components = {"forks": forks,
                           "pipes": pipes,
                           "consumers": consumers,
                           "producers": producers}
        self.sequences = {"consumers": {"heat_flow": pandas.DataFrame()},
                          "producers": {}}

    def to_nx_graph(self):
        """
            Convert the MockThermalNetwork2 instance to a NetworkX graph.
    
            This method utilizes the
            dhnx.network.thermal_network_to_nx_graph
            function to convert the ThermalNetwork components into a NetworkX graph.
    
            :return: NetworkX graph representation of the ThermalNetwork.
            :rtype: networkx.Graph
        """
        nx_graph = dhnx.network.thermal_network_to_nx_graph(self)
        return nx_graph
    
    
def test_create_components():
    """
        Test the creation of thermal network Oemof components.

        This test function creates mock data for the model definition
        sheet and a ThermalNetwork instance. It then calls the
        create_components method, which runs the dhnx methods for
        creating thermal network Oemof  components.
        The test asserts the expected changes in the result, such as
        the type of the result and the number of nodes added to the
        OemofInvestOptimizationModel.
    """
    # Mock data for nodes_data
    nodes_data = {
        "energysystem": pandas.DataFrame({
            "temporal resolution": ["h"],
            "start date": ["2023-01-01"],
            "periods": [8760]
        }),
        "pipe types": pandas.DataFrame({
            "label": ["DNTest"],
            "min. investment capacity": [0],
            "max. investment capacity": [100],
            "periodical costs": [50],
            "fix investment costs": [500],
            "periodical constraint costs": [10],
            "fix investment constraint costs": [100],
            "anergy or exergy": ["exergy"],
            "distribution pipe": [1],
            "building pipe": [1],
            "active": [1],
            "nonconvex": [1],
            "loss factor": [0],
            "loss factor fix": [0.1],
        })
    }

    # Mock ThermalNetwork instance
    thermal_net = MockThermalNetwork2(
        forks=pandas.DataFrame(
            {"id": [0, 1],
             "name": ["Fork1", "Fork2"],
             "component_type": ["Forks", "Forks"]}),
        consumers=pandas.DataFrame(
            {"id": [0],
             "name": ["Consumer1"],
             "component_type": ["Consumers"]}),
        producers=pandas.DataFrame(
            {"id": [0],
             "name": ["Producer1"],
             "component_type": ["Producers"]}),
        pipes=pandas.DataFrame(
            {"id": [0, 1, 2],
             "from_node": ["producers-0", "forks-0", "forks-1"],
             "to_node": ["forks-0", "forks-1", "consumers-0"],
             "length": [10, 10, 10]}
        )
        )

    # Call the method
    result = district_heating.create_components(
        nodes_data=nodes_data,
        label_5="exergy",
        thermal_net=thermal_net
    )

    # Assert the changes in the result - Assuming it adds 8 nodes to
    # the thermal network instance
    assert isinstance(
        result,
        dhnx.optimization.optimization_models.OemofInvestOptimizationModel)
    assert len(result.nodes) == 8
